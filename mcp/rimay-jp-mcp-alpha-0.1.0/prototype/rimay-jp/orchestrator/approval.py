"""承認フロー: structurally_valid → review_ready → approved（§5状態機械）。

review_ready遷移条件:
- 必須Roleがすべてconfirmedまたはnot_applicable
- blocking findingが0件（validation-router全層）
- Parser受理・AST射影意味等価・sidecar完全性を通過（validation-routerに含む）
- 使用したSchema/Profile/辞書/Rule版を固定・記録（versions_used）
approvedは直接変更しない。変更は新revisionをcandidateとして作る（§5）。
"""
import copy

from . import _ROOT  # noqa: F401
from .validation_router import validate_all  # noqa: E402
from rimay_jp_core import SCHEMA_VERSION, PROFILE_VERSION  # noqa: E402
from rimay_jp_core.lexicon import case_frames, versions  # noqa: E402
from rimay_jp_core.response_expression import (  # noqa: E402
    ResponseBlockError,
    ResponseExpressionError,
    iter_core_responses,
)
from rimay_jp_core.condition_expression import (  # noqa: E402
    ConditionExpressionError,
    MultiValueRuntimeError,
    iter_core_conditions,
    iter_operator_operand_leaves,
    iter_predicate_value_leaves,
)
from rimay_jp_core.validator import _ROLE_FIELD  # noqa: E402
from .rule_engine import rule_set_version  # noqa: E402


def required_pointers(canonical: dict) -> list[str]:
    """review_ready判定の対象となる応答RoleとComparison predicateリーフ。"""
    ptrs: list[str] = []
    for response_path, resp in iter_core_responses(
            canonical["rimay_core"],
            source_text=(canonical.get("source") or {}).get("text")):
        fam = (resp.get("action") or {}).get("family")
        ptrs.extend([
            f"{response_path}/actor",
            f"{response_path}/modality",
            f"{response_path}/action/family",
            f"{response_path}/action/rimay_action_id",
        ])
        if resp.get("frequency") is not None:
            ptrs.extend([
                f"{response_path}/frequency/value",
                f"{response_path}/frequency/unit",
            ])
        frame = case_frames().get(fam)
        if frame:
            for role in frame["required_roles"]:
                field = _ROLE_FIELD.get(role)
                if field and field != "actor":
                    # 禁止要求はresult_value等を要求しない（Phase 2裁定と整合）
                    if resp.get("modality") == "MUST_NOT" and not resp.get(field):
                        continue
                    ptrs.append(f"{response_path}/{field}")
    for condition_path, condition in iter_core_conditions(canonical["rimay_core"]):
        predicate = condition.get("predicate")
        if isinstance(predicate, dict):
            predicate_path = f"{condition_path}/predicate"
            if "operand" in predicate:
                try:
                    ptrs.extend(iter_operator_operand_leaves(
                        predicate["operand"], path=predicate_path + "/operand"))
                except MultiValueRuntimeError:
                    continue
            else:
                ptrs.append(predicate_path + "/subject")
            ptrs.append(predicate_path + "/operator")
            try:
                leaves = iter_predicate_value_leaves(predicate, path=predicate_path)
                for leaf_path, leaf in leaves:
                    if leaf_path == predicate_path:
                        ptrs.append(predicate_path + "/value")
                        if leaf.get("unit") is not None:
                            ptrs.append(predicate_path + "/unit")
                    else:
                        ptrs.append(leaf_path + "/value")
                        if leaf.get("unit") is not None:
                            ptrs.append(leaf_path + "/unit")
            except MultiValueRuntimeError:
                # Validator owns the diagnostic. Approval remains deterministic
                # and never invents a scalar fallback pointer for an invalid tree.
                continue
    return ptrs


def promote_to_review_ready(canonical: dict) -> dict:
    reasons: list[str] = []
    res = validate_all(canonical)
    if res["blocked"]:
        reasons.append(f"blocking findingあり: "
                       f"{sorted({f['code'] for f in res['findings'] if f['blocking']})}")
    # §6合意によるBlocking化の作用点: Validation Report（正規化finding）の
    # blockingが1件でもあればreview_readyへ進めない（rolloutポリシー準拠）。
    state = res.get("validation_state") or {}
    if state.get("blocking_findings"):
        codes = sorted({f["normalized_issue_code"]
                        for f in res["report"]["findings"] if f["blocking"]})
        reasons.append(f"Validation Reportにblocking findingあり: {codes}")

    # 保証経路（mode）別の承認条件（ADR-0013 D4）:
    # strict: 未解釈span 0（往復意味等価はvalidate_all内で検査済み）
    # heuristic/llm: 未解釈span 0＋全スロット解決済み＋Strict表層再生成の往復成立
    norm = canonical.get("normalization") or {}
    mode = norm.get("mode", "canonical_api")
    if mode in ("strict", "heuristic", "llm"):
        cov = norm.get("coverage")
        if cov is None:
            reasons.append(f"正規化カバレッジ未記録（mode={mode}）")
        elif cov.get("unconsumed_spans"):
            src = canonical.get("source", {}).get("text") or ""
            frag = [src[s["start"]:s["end"]] for s in cov["unconsumed_spans"][:3]]
            reasons.append(f"未解釈spanが残存: {frag}（意味の取りこぼしを解消してから承認）")
    if mode in ("heuristic", "llm"):
        unresolved = [p for p, s in canonical["resolution"]["slots"].items()
                      if s.get("status") not in ("confirmed", "not_applicable")]
        if unresolved:
            reasons.append(f"未解決スロットあり（{mode}経路は全解決が条件）: "
                           f"{unresolved[:3]}")
        if res.get("jp_roundtrip_ok") is not True:
            reasons.append("Strict表層再生成の往復が未成立"
                           f"（{mode}経路はSerializer再生成文のstrict往復が条件）")
    if not res.get("artifacts"):
        reasons.append("表層生成（Parser/AST等価/sidecar検査）が未通過")
    slots = canonical["resolution"]["slots"]
    try:
        pointers = required_pointers(canonical)
    except (ResponseExpressionError, ResponseBlockError, ConditionExpressionError) as exc:
        reasons.append(f"式構造が不正: {exc.code} at {exc.path}")
    else:
        for ptr in pointers:
            st = (slots.get(ptr) or {}).get("status")
            if st not in ("confirmed", "not_applicable"):
                reasons.append(f"必須Role未確定: {ptr}（{st}）")
    if reasons:
        return {"ok": False, "reasons": reasons}

    previous_status = canonical["status"]
    previous_versions = copy.deepcopy(canonical.get("versions_used"))
    previous_validation_state = copy.deepcopy(canonical.get("validation_state"))
    canonical["status"] = "review_ready"
    ver = versions()
    canonical["versions_used"] = {
        "schema_version": SCHEMA_VERSION,
        "profile_version": PROFILE_VERSION,
        "lexicon_version": ver["term_dictionary"],
        "frame_set_version": ver["action_frame"],
        "knowledge_version": ver["domain_knowledge"],
        "rule_set_version": rule_set_version(),
        "profile_content_hash": ver["profile_content_hash"],
    }
    # KD-08: 遷移前に通ったことだけでは、遷移が追加するstatus／versions_usedの
    # Schema closureを保証できない。書き込み後の完全Canonicalを同じpreflightへ通す。
    post = validate_all(canonical)
    if post["blocked"]:
        schema_errors = ((post.get("layers") or {}).get("schema") or {}).get(
            "errors") or []
        blocking_codes = sorted({
            finding["code"] for finding in post.get("findings") or []
            if finding.get("blocking")
        })
        canonical["status"] = previous_status
        if previous_versions is None:
            canonical.pop("versions_used", None)
        else:
            canonical["versions_used"] = previous_versions
        if previous_validation_state is None:
            canonical.pop("validation_state", None)
        else:
            canonical["validation_state"] = previous_validation_state
        return {
            "ok": False,
            "reasons": [
                "review_ready昇格後の再検証に失敗: "
                f"schema={schema_errors[:3]} blocking={blocking_codes}"
            ],
        }
    return {"ok": True, "reasons": [], "artifacts": post["artifacts"]}


def approve(canonical: dict, approved_by: str, approved_at: str) -> dict:
    if canonical["status"] != "review_ready":
        return {"ok": False,
                "reasons": [f"review_readyではありません: {canonical['status']}"]}
    preflight = validate_all(canonical)
    if preflight["blocked"]:
        schema_errors = ((preflight.get("layers") or {}).get("schema") or {}).get(
            "errors") or []
        return {
            "ok": False,
            "reasons": [f"承認preflightに失敗: schema={schema_errors[:3]}"],
        }
    confirmed = [p for p, s in canonical["resolution"]["slots"].items()
                 if s["status"] == "confirmed"]
    previous_validation_state = copy.deepcopy(canonical.get("validation_state"))
    canonical["status"] = "approved"
    canonical["approval"] = {"approved_by": approved_by, "approved_at": approved_at,
                             "approved_slots": sorted(confirmed)}
    post = validate_all(canonical)
    if post["blocked"]:
        schema_errors = ((post.get("layers") or {}).get("schema") or {}).get(
            "errors") or []
        canonical["status"] = "review_ready"
        canonical.pop("approval", None)
        if previous_validation_state is None:
            canonical.pop("validation_state", None)
        else:
            canonical["validation_state"] = previous_validation_state
        return {
            "ok": False,
            "reasons": [f"approved遷移後の再検証に失敗: schema={schema_errors[:3]}"],
        }
    return {"ok": True, "reasons": []}
