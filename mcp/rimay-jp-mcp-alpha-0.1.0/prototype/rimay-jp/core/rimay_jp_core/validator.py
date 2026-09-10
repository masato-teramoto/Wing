"""validate_core / validate_terminology のPhase 2サブセット。

裁定（Phase 2、GATE-1留保2の解消）:
必須Roleの格フレーム充足検査は modality == MUST の要求にのみ適用する。
禁止要求（MUST_NOT）は動作の不実行を求めるため、結果値・宛先等の
必須Roleを要求しない（UPDATE-003参照）。
"""
from . import PHASE2_CONDITIONS, PHASE2_FAMILIES, MVP_CONDITIONS
from .lexicon import case_frames
from .model import finding
from .condition_expression import (
    condition_core_findings,
    iter_core_conditions,
    iter_predicate_value_leaves,
    MultiValueRuntimeError,
    validate_predicate_authority,
)
from .response_expression import (
    iter_core_responses,
    response_core_findings,
)
from .atomic_response import atomic_response_findings
from .english_profile import operators_in
from .semantic_values import split_money

# 格フレームrole → Canonical response フィールド
# Role→フィールド対応の正本はlexicon.ROLE_FIELD（ADR-0013 D3。ここは互換別名）
from .lexicon import ROLE_FIELD as _ROLE_FIELD  # noqa: E402


def _validate_response(resp: dict, path: str, phase2_slice: bool) -> list[dict]:
    findings: list[dict] = []

    # 主体・モダリティ・動作の存在
    if not resp.get("actor"):
        findings.append(finding("JP-OMISSION", "応答主体が確定していません。",
                                path + "/actor"))
    if resp.get("modality") not in ("MUST", "MUST_NOT"):
        findings.append(finding("JP-MODAL", "モダリティが確定していません。",
                                path + "/modality"))
    fam = (resp.get("action") or {}).get("family")
    if not fam:
        findings.append(finding("RIMAY-ACTION", "Action familyが確定していません。",
                                path + "/action/family"))
        return findings

    frame = case_frames().get(fam)
    if not frame:
        findings.append(finding("RIMAY-ACTION",
                                f"family {fam} に対応するAction Frameがありません。",
                                path + "/action/family"))
        return findings
    if phase2_slice and fam not in PHASE2_FAMILIES:
        findings.append(finding("PROFILE-OUT",
                                f"Action {fam} はPhase 2スライス（SEND/UPDATE）の対象外です。",
                                path + "/action/family", slice="phase2"))

    # 格フレーム充足（MUSTのみ。裁定は本モジュールdocstring）
    if resp.get("modality") == "MUST":
        for role in frame["required_roles"]:
            field = _ROLE_FIELD.get(role)
            if field == "actor":
                continue  # 上で検査済み
            if field and not resp.get(field):
                findings.append(finding("JP-OMISSION",
                                        f"{fam} の必須Role '{role}' が欠落しています。",
                                        f"{path}/{field}",
                                        case_frame=frame["rimay_action_id"],
                                        required_role=role))
    return findings


def _validate_predicate(cond: dict, path: str) -> list[dict]:
    """Direct-call guard for mutually exclusive scalar and value-tree authority."""
    findings: list[dict] = []
    if cond.get("type") not in {"IF", "WHILE"}:
        return findings
    predicate = cond.get("predicate")
    predicate_path = path + "/predicate"
    if not isinstance(predicate, dict):
        return [finding(
            "JP-COORD", "IF／WHILE条件の単値predicateがありません。", predicate_path,
            comparison_operator_code="COMPARISON_OPERATOR_INVALID_OPERAND")]
    allowed_keys = {"subject", "operand", "operator", "value", "unit", "value_expression"}
    if set(predicate) - allowed_keys:
        findings.append(finding(
            "JP-COORD", "predicateに未採用fieldがあります。", predicate_path,
            comparison_operator_code="COMPARISON_OPERATOR_INVALID_OPERAND",
            fields=sorted(set(predicate) - allowed_keys)))
    try:
        validate_predicate_authority(predicate, path=predicate_path)
    except MultiValueRuntimeError as exc:
        findings.append(finding(
            "JP-COORD", exc.message, exc.path,
            operator_value_code=exc.code))
        return findings
    operator = predicate.get("operator")
    if operator not in operators_in():
        findings.append(finding(
            "PROFILE-OUT", f"比較演算子 {operator!r} はProfile 0.5の対象外です。",
            predicate_path + "/operator",
            comparison_operator_code="COMPARISON_OPERATOR_UNSUPPORTED"))
    try:
        leaves = list(iter_predicate_value_leaves(predicate, path=predicate_path))
    except MultiValueRuntimeError as exc:
        findings.append(finding(
            "JP-COORD", exc.message, exc.path,
            multi_value_code=exc.code))
        return findings
    for leaf_path, leaf in leaves:
        value = leaf.get("value")
        value_path = (leaf_path + "/value" if leaf_path != predicate_path
                      else predicate_path + "/value")
        if not isinstance(value, str) or not value:
            findings.append(finding(
                "JP-COORD", "predicate value leafは非空文字列でなければなりません。",
                value_path, multi_value_code="MULTI_VALUE_INVALID_VALUE"))
            continue
        unit = leaf.get("unit")
        unit_path = (leaf_path + "/unit" if leaf_path != predicate_path
                     else predicate_path + "/unit")
        if unit is not None and unit != "JPY":
            findings.append(finding(
            "PROFILE-OUT", f"比較単位 {unit!r} はProfile 0.5の対象外です。",
                unit_path,
                comparison_operator_code="COMPARISON_OPERATOR_INVALID_OPERAND",
                multi_value_code="MULTI_VALUE_UNSUPPORTED_UNIT"))
        if unit == "JPY" and split_money(f"{value} JPY") is None:
            findings.append(finding(
                "JP-COORD", "JPY比較値は数値スカラーでなければなりません。",
                value_path,
                comparison_operator_code="COMPARISON_OPERATOR_INVALID_OPERAND",
                multi_value_code="MULTI_VALUE_INVALID_UNIT_VALUE"))
    return findings


def validate(canonical: dict, phase2_slice: bool = True) -> list[dict]:
    findings: list[dict] = []
    core = canonical["rimay_core"]
    source_text = (canonical.get("source") or {}).get("text")

    condition_problems = condition_core_findings(core)
    if condition_problems:
        for problem in condition_problems:
            findings.append(finding(
                "JP-COORD", problem["message"], problem["path"],
                condition_expression_code=problem["code"]))
        findings += terminology_findings(canonical)
        return findings

    # 条件種別の対応範囲（legacy配列と式木leafを同じ契約で検査）
    for path, cond in iter_core_conditions(core):
        ctype = cond.get("type")
        if ctype not in MVP_CONDITIONS:
            findings.append(finding("PROFILE-OUT",
                                    f"条件種別 {ctype} はSupported Profile v0.1の対象外です。",
                                    f"{path}/type"))
        elif phase2_slice and ctype not in PHASE2_CONDITIONS:
            findings.append(finding("PROFILE-OUT",
                                    f"条件種別 {ctype} はPhase 2スライス（When/If）の対象外です。",
                                    f"{path}/type", slice="phase2"))
        findings += _validate_predicate(cond, path)

    expression_problems = response_core_findings(core, source_text=source_text)
    if expression_problems:
        for problem in expression_problems:
            evidence_key = (
                "response_block_code"
                if problem["code"].startswith("RESPONSE_BLOCK_")
                else "atomic_response_code"
                if problem["code"].startswith("ATOMIC_RESPONSE_")
                else "response_expression_code"
            )
            findings.append(finding(
                "JP-COORD", problem["message"], problem["path"],
                **{evidence_key: problem["code"]}))
        findings += terminology_findings(canonical)
        return findings

    response_structure = (
        "response_block" if core.get("response_block") is not None
        else "response_expression" if core.get("response_expression") is not None
        else None
    )
    if response_structure is not None and \
            ((canonical.get("extensions") or {}).get("time_constraints") or []):
        code = (
            "RESPONSE_BLOCK_EXTENSION_SCOPE"
            if response_structure == "response_block"
            else "RESPONSE_EXPRESSION_EXTENSION_SCOPE"
        )
        evidence_key = (
            "response_block_code" if response_structure == "response_block"
            else "response_expression_code"
        )
        findings.append(finding(
            "JP-COORD",
            "複数Responseに対する時間制約の適用範囲が確定していません。",
            "/extensions/time_constraints",
            **{evidence_key: code}))

    responses = list(iter_core_responses(core, source_text=source_text))
    if not responses:
        responses = [("/rimay_core/response", {})]
    for path, response in responses:
        for problem in atomic_response_findings(
                response,
                source_text=source_text,
                path=path):
            findings.append(finding(
                "JP-COORD", problem["message"], problem["path"],
                atomic_response_code=problem["code"]))
        findings += _validate_response(response, path, phase2_slice)

    global_frequency = any(
        tc.get("kind") == "FREQUENCY"
        for tc in ((canonical.get("extensions") or {}).get("time_constraints") or [])
        if isinstance(tc, dict)
    )
    if global_frequency and any(response.get("frequency") is not None
                                for _path, response in responses):
        findings.append(finding(
            "JP-COORD",
            "応答頻度がAtomic Responseとlegacy time_constraintsの双方に存在します。",
            "/extensions/time_constraints",
            atomic_response_code="ATOMIC_RESPONSE_FREQUENCY_AUTHORITY_CONFLICT"))

    # 曖昧語（測定不能な時間制約）
    for i, tc in enumerate((canonical.get("extensions") or {}).get("time_constraints") or []):
        if tc.get("source_expression") and tc.get("value") is None:
            findings.append(finding("QUALITY-AMBIGUOUS",
                                    f"曖昧語「{tc['source_expression']}」は測定可能な条件へ"
                                    f"変換されていません。",
                                    f"/extensions/time_constraints/{i}/value",
                                    source_expression=tc["source_expression"]))

    findings += terminology_findings(canonical)
    return findings


def terminology_findings(canonical: dict, term_meta: dict | None = None) -> list[dict]:
    """語彙依存の検査（ADR-0014 D4/D5。owner: terminology-validator）。

    - 未解消のterminology_candidate依存スロット → TERM_APPROVAL_PENDING（blocking。
      承認・Snapshot公開・伝播Patchで依存が除去されるまでreview_readyへ進めない）
    - 廃止・統合済みterm IDの参照 → DEPRECATED_TERM（warning・後継提示）
    """
    from .lexicon import term_ids
    findings: list[dict] = []
    slots = (canonical.get("resolution") or {}).get("slots") or {}
    for path, slot in slots.items():
        for dep in slot.get("dependency_refs") or []:
            if dep.get("type") == "terminology_candidate" and \
                    slot.get("status") != "confirmed":
                findings.append(finding(
                    "TERM_APPROVAL_PENDING",
                    f"未公開のTerm Candidate承認待ちです: {dep['reference']}",
                    path, candidate_ref=dep["reference"]))
    meta = term_meta if term_meta is not None else term_ids()

    def _walk(v, path):
        if isinstance(v, dict):
            for k, x in v.items():
                _walk(x, f"{path}/{k}")
        elif isinstance(v, list):
            for i, x in enumerate(v):
                _walk(x, f"{path}/{i}")
        elif isinstance(v, str):
            t = meta.get(v)
            if isinstance(t, dict) and t.get("status") in ("deprecated", "superseded"):
                findings.append(finding(
                    "DEPRECATED_TERM", f"廃止・統合済みの用語を参照しています: {v}",
                    path, term_id=v, superseded_by=t.get("superseded_by")))

    _walk(canonical.get("rimay_core") or {}, "/rimay_core")
    return findings
