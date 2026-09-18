"""knowledge-router: スロット・候補Action・findingsから必要な知識源を決定論的に選択する（Phase 3B）。

構想書 §14.5/§14.6/§21 Phase 3B:
- Grammar全体や全用語を毎回LLMへ投入しない（必要スロット分だけ照会する）。
- 取得した規則・用語・根拠にID・版数・取得方法のProvenanceを付ける。
- 辞書登録済みであっても根拠不足の候補を自動的にconfirmedへしない
  （routerはスロットstatusを一切変更しない。追加するのはProvenanceだけ）。
"""
import copy

from . import _ROOT  # noqa: F401
from rimay_jp_core.lexicon import case_frames, term_ids, knowledge_bank, versions  # noqa: E402
from rimay_jp_core.model import finding  # noqa: E402
from rimay_jp_core.response_expression import (  # noqa: E402
    ResponseBlockError,
    ResponseExpressionError,
    iter_core_responses,
)
from rimay_jp_core.condition_expression import (  # noqa: E402
    ConditionExpressionError,
    MultiValueRuntimeError,
    iter_core_conditions,
    iter_predicate_value_leaves,
    operator_operand_identity,
)

# 知識源種別（§14.6 スロットと知識ルーティング）
SOURCES = ("term_dictionary", "action_frame", "state_model", "business_rule", "nfr")


def _state_model_for(property_id: str):
    for sm in knowledge_bank().get("state_models") or []:
        if sm.get("property") == property_id:
            return sm
    return None


def _match_business_rule(predicate: dict):
    hits = []
    for br in knowledge_bank().get("business_rules") or []:
        p = br.get("predicate") or {}
        if p and all(p.get(k) == predicate.get(k)
                     for k in ("subject", "operator", "value", "unit")):
            hits.append(br)
    return hits


def route(canonical: dict) -> dict:
    """戻り値: {routes, findings, provenance_added}。canonicalにはProvenanceのみ追記する。"""
    ver = versions()
    routes: list[dict] = []
    findings: list[dict] = []
    added: list[str] = []
    core = canonical["rimay_core"]
    slots = canonical["resolution"]["slots"]

    try:
        responses = list(iter_core_responses(
            core, source_text=(canonical.get("source") or {}).get("text")))
        conditions = list(iter_core_conditions(core))
    except (ResponseExpressionError, ResponseBlockError,
            ConditionExpressionError) as exc:
        return {
            "routes": [],
            "findings": [finding(
                "KNOWLEDGE-ROUTE", str(exc), exc.path,
                expression_code=exc.code)],
            "provenance_added": [],
        }

    def add_route(slot, source, query, method, hits):
        routes.append({"slot": slot, "source": source, "query": query,
                       "method": method, "hits": hits,
                       "source_version": ver.get(source, ver["domain_knowledge"])
                       if source in ver else ver["domain_knowledge"]})

    def ground(pointer: str, source: str, ref: str, version: str):
        """知識アセットによる根拠付け。statusは変更しない（Provenance追記のみ）。"""
        prv_id = f"PRV-{len(canonical['provenance']) + 1}"
        canonical["provenance"].append({
            "id": prv_id,
            "path": pointer,
            "source_type": "knowledge_asset",
            "reference": f"{source}:{ref}@{version}",
            "resolution_method": "rule_application",
        })
        slot = slots.setdefault(pointer, {"status": "unknown"})
        slot.setdefault("provenance_refs", []).append(prv_id)
        added.append(prv_id)

    # 1) Action → Action Frame（候補が複数なら全候補を照会する）
    for response_path, resp in responses:
        family_path = f"{response_path}/action/family"
        fam_slot = slots.get(family_path) or {}
        fams = [c["value"] for c in fam_slot.get("candidates") or []]
        if not fams:
            fam = (resp.get("action") or {}).get("family")
            fams = [fam] if fam else []
        for fam in fams:
            hit = fam in case_frames()
            add_route(family_path, "action_frame", fam,
                      "id_lookup", [f"case-frame:{fam}"] if hit else [])
            if not hit:
                findings.append(finding(
                    "KNOWLEDGE-ROUTE", f"Action Frameが見つかりません: {fam}",
                    family_path))

    # 2) 状態値 → 状態モデル（property×valueの組で照会し、根拠付けする）
    checks = []
    for response_path, resp in responses:
        if resp.get("property") and resp.get("result_value"):
            checks.append((resp["property"], resp["result_value"],
                           f"{response_path}/result_value"))
    for condition_path, cond in conditions:
        ev = cond.get("event") or {}
        if ev.get("object") and ev.get("value"):
            checks.append((ev["object"], ev["value"],
                           f"{condition_path}/event/value"))
        pred = cond.get("predicate") or {}
        state_property = pred.get("subject")
        operand = pred.get("operand")
        if isinstance(operand, dict):
            state_property = (
                operand.get("name")
                if operand.get("wrapper") == "declared_reference" and
                operand.get("kind") == "property"
                else None
            )
        if state_property and pred.get("operator") == "IS":
            predicate_path = f"{condition_path}/predicate"
            try:
                for leaf_path, leaf in iter_predicate_value_leaves(
                        pred, path=predicate_path):
                    value = leaf.get("value")
                    if value and leaf.get("unit") is None:
                        pointer = (predicate_path + "/value"
                                   if leaf_path == predicate_path
                                   else leaf_path + "/value")
                        checks.append((state_property, value, pointer))
            except MultiValueRuntimeError as exc:
                findings.append(finding(
                    "KNOWLEDGE-ROUTE", str(exc), exc.path,
                    multi_value_code=exc.code))
    for prop, value, pointer in checks:
        sm = _state_model_for(prop)
        if not sm:
            add_route(pointer, "state_model", f"{prop}={value}", "id_lookup", [])
            continue
        add_route(pointer, "state_model", f"{prop}={value}", "id_lookup",
                  [f"state-model:{sm['id']}"])
        if value in (sm.get("states") or []):
            ground(pointer, "state-model", sm["id"], ver["domain_knowledge"])
        else:
            findings.append(finding("DOMAIN",
                                    f"状態値 {value} は状態モデル {sm['id']} に定義がありません。",
                                    pointer, state_model=sm["id"],
                                    known_states=sm.get("states")))

    # 3) 数値条件 → 業務ルール（構造化述語の一致で照合する）
    for condition_path, cond in conditions:
        pred = cond.get("predicate") or {}
        if "value_expression" in pred:
            pointer = f"{condition_path}/predicate/value_expression"
            try:
                leaves = list(iter_predicate_value_leaves(
                    pred, path=f"{condition_path}/predicate"))
            except MultiValueRuntimeError as exc:
                findings.append(finding(
                    "KNOWLEDGE-ROUTE", str(exc), exc.path,
                    multi_value_code=exc.code))
                continue
            query = " | ".join(
                f"{leaf.get('value')} {leaf.get('unit') or ''}".rstrip()
                for _leaf_path, leaf in leaves
            )
            identity = pred.get("subject")
            if "operand" in pred:
                try:
                    identity = "operand:" + operator_operand_identity(pred["operand"])
                except ValueError as exc:
                    findings.append(finding(
                        "KNOWLEDGE-ROUTE", str(exc),
                        f"{condition_path}/predicate/operand",
                        operator_value_code=getattr(
                            exc, "code", "OPERATOR_VALUE_INVALID_OPERAND")))
                    continue
            add_route(pointer, "business_rule",
                      f"{identity} {pred.get('operator')} TREE[{query}]",
                      "multi_value_residual", [])
            findings.append(finding(
                "KNOWLEDGE-ROUTE",
                "Multi-value treeの業務ルール照合は専用Rule採用まで残差として保持します。",
                pointer, multi_value_code="MULTI_VALUE_CONSUMER_RULE_REQUIRED",
                leaf_pointers=[leaf_path for leaf_path, _leaf in leaves]))
            continue
        if pred.get("operator") and pred["operator"] != "IS":
            hits = _match_business_rule(pred)
            pointer = f"{condition_path}/predicate"
            add_route(pointer, "business_rule",
                      f"{pred.get('subject')} {pred.get('operator')} {pred.get('value')}",
                      "predicate_match", [f"rule:{br['id']}" for br in hits])
            for br in hits:
                ground(pointer, "rule", br["id"], ver["domain_knowledge"])

    # 4) 未解決の時間制約 → NFR知識（MVPでは知識源なし＝未解決として記録する）
    for i, tc in enumerate((canonical.get("extensions") or {}).get("time_constraints") or []):
        if tc.get("value") is None:
            pointer = f"/extensions/time_constraints/{i}/value"
            add_route(pointer, "nfr", tc.get("source_expression") or "deadline",
                      "scan", [])
            findings.append(finding("KNOWLEDGE-ROUTE",
                                    "時間制約を確定できる知識源がありません（確認質問へ）。",
                                    pointer))

    # 5) 同義語由来スロット → 用語辞書の再照会（正規化の根拠を版数付きで記録）
    prv = {p["id"]: p for p in canonical["provenance"]}
    for pointer, slot in list(slots.items()):
        for ref in slot.get("provenance_refs") or []:
            if prv.get(ref, {}).get("resolution_method") == "synonym_match":
                tid = _value_at(canonical, pointer)
                add_route(pointer, "term_dictionary", prv[ref].get("source_span", ""),
                          "synonym_lookup",
                          [f"term:{tid}"] if tid in term_ids() else [])
                if tid in term_ids():
                    ground(pointer, "term", tid, ver["term_dictionary"])

    return {"routes": routes, "findings": findings, "provenance_added": added}


def _value_at(canonical: dict, pointer: str):
    node = canonical
    for token in pointer.strip("/").split("/"):
        if isinstance(node, list):
            try:
                node = node[int(token)]
            except (ValueError, IndexError):
                return None
        elif isinstance(node, dict):
            node = node.get(token)
        else:
            return None
    return node


def routing_log(canonical: dict, result: dict) -> dict:
    """再現可能なrouting log（knowledge-routing-log契約）。"""
    return {
        "requirement_id": canonical["requirement_id"],
        "profile_version": canonical["profile_version"],
        "source_versions": versions(),
        "routes": result["routes"],
        "findings": [{"code": f["code"], "path": f.get("path")} for f in result["findings"]],
        "provenance_added": result["provenance_added"],
    }


def route_reproducible(canonical: dict) -> bool:
    """同一入力に対するルーティングの再現性検査（GATE-3B機能条件）。"""
    a = route(copy.deepcopy(canonical))
    b = route(copy.deepcopy(canonical))
    return a["routes"] == b["routes"]
