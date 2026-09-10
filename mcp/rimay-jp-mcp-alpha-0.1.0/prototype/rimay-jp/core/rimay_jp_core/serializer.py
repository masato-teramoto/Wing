"""render_requirement_views: Canonical → English Rimay + sidecar + artifact-manifest。

3成果物は原子的に生成する。English Rimay本文にメタデータは埋め込まない。

C3（改善計画§21.4・§21.7・§19.4・CG-02/03/08）:
  - handler選択はfamily直結の英語動詞表でなく、English conformance profileの束縛を経由し、
    Canonicalのrimay_action_idが現行宣言（case-frames）と一致することを検査する
    （不一致は生成せずSerializationError RIMAY-CONFORMANCE。fail-closed）。
  - 未対応operatorは通常の"is"へ縮退せず、SerializationError UNSUPPORTED_OPERATOR。
  - SEND.sourceを出力する（CG-03: from句のRole消失を解消）。
  - 表層形の是正: CALCULATE `using`、NOTIFY `notify <content> to <destination>
    [using <channel>]`（SAY_37_7語順）、STORE `store the value|property "<theme>"`
    （KEEP_15_2リテラル。term typeがpropertyならproperty）。
  - VERIFYの生成形はGate B二名確定まで現行形を維持する（§21.4）。
  - 必須Role欠落はKeyErrorでなくSerializationError MISSING_ROLE（CG-08）。
  - artifact manifestへconformance情報（§19.4）を追加する。

retention（extensions.time_constraints[kind=RETENTION]）は現行Schemaに開始点fieldが
存在しないため「期間+開始点一体」の生成が構造的に不能であり、§21.6のとおり本文へ
生成せずsidecarに保持する（sidecar_only_features）。X-06/X-07裁定まで据え置き。
"""
import hashlib

from .english_profile import binding, profile_version as _conf_profile_version
from .english_profile import grammar_profile_hash, value_connectors
from .lexicon import en_label, term_ids
from .model import canonical_hash
from .condition_expression import (
    condition_core_findings,
    iter_core_conditions,
    render_condition_expression,
    validate_value_expression,
)
from .response_expression import (
    iter_core_responses,
    render_response_expression,
    response_core_findings,
)
from .response_block import render_response_block

SERIALIZER_VERSION = "0.9.0"   # 0.9.0: typed Operator value expression runtime activation

# 条件比較operatorの明示handler（CG-02: 未登録operatorはfail-closed）
_OPERATOR_HANDLERS = {
    "IS": "is",
    "EQUALS": "is equal to",
    "NOT_EQUALS": "is not",
    "GREATER_THAN": "is greater than",
    "LESS_THAN": "is less than",
    "GREATER_OR_EQUAL": "is greater or equal to",
    "LESS_OR_EQUAL": "is less than or equal to",
    "CONTAINS": "contains",
}


class SerializationError(Exception):
    """構造化Serializer診断（§19.6。Parser診断とはdomainで区別）。"""

    def __init__(self, message: str, *, code: str, path: str = "",
                 expected=(), found=None) -> None:
        super().__init__(message)
        self.code = code                      # MISSING_ROLE | UNSUPPORTED_OPERATOR |
        self.path = path                      #   UNMAPPED_ROLE | ACTION_BINDING_MISMATCH | PROFILE_OUT
        self.expected = tuple(sorted(str(e) for e in expected))
        self.found = found

    def diagnostic(self) -> dict:
        return {"domain": "serialization", "code": self.code, "path": self.path,
                "expected": list(self.expected), "found": self.found}


def _q(term_id: str) -> str:
    """種別に応じた実体レンダリング: Actorは裸ID、それ以外は引用符付きラベル。"""
    t = term_ids().get(term_id)
    if t and t["type"] == "actor":
        return term_id
    return f'the "{en_label(term_id)}"'


def _fmt_money(value: str, unit: str) -> str:
    return f'"{int(value.replace(",", "")):,} {unit}"'


def _render_value_expression(expression: dict) -> str:
    """Render the active English value tree without collapsing its structure."""
    validate_value_expression(
        expression, path="/rimay_core/conditions/0/predicate/value_expression")

    def visit(node: dict) -> str:
        kind = node["kind"]
        if kind == "value":
            if node.get("unit") == "JPY":
                return _fmt_money(node["value"], "JPY")
            return f'"{en_label(node["value"])}"'
        if kind == "group":
            return "(" + visit(node["expression"]) + ")"
        connector = " " + value_connectors()[kind] + " "
        return "(" + visit(node["left"]) + connector + visit(node["right"]) + ")"

    return visit(expression)


def _require(resp: dict, role: str, fam: str):
    """必須Roleの取得（欠落はKeyErrorでなくMISSING_ROLE。CG-08）。"""
    v = resp.get(role)
    if not v:
        raise SerializationError(
            f"required role {role!r} missing for {fam}",
            code="MISSING_ROLE", path=f"/rimay_core/response/{role}",
            expected=(role,), found=None)
    return v


def _declared_action_id(fam: str) -> str:
    """Canonical宣言のrimay_action_id（C4でEnglish profile束縛へ統一。RC-005。

    case-frames.yamlとの同期はcontract test（divergence==∅）が機械保証する。"""
    return binding(fam)["rimay_action_id"]


def render_condition(cond: dict) -> str:
    ctype = cond["type"]
    if ctype in ("WHEN", "AFTER", "BEFORE"):
        kw = {"WHEN": "When", "AFTER": "After", "BEFORE": "Before"}[ctype]
        ev = cond.get("event") or {}
        fam = ev["action"]["family"]
        b = binding(fam) if fam != "PRESS" else None
        verb3 = b["verbs"][1] if b else "presses"   # 三単現（bindingsは[基本形,三単現,...]）
        s = f"{kw} {ev['actor']} {verb3} {_q(ev['object'])}"
        if ev.get("value"):
            s += f' to "{en_label(ev["value"])}"'
        return s
    if ctype in ("IF", "WHILE"):
        kw = "If" if ctype == "IF" else "While"
        p = cond.get("predicate") or {}
        if "operand" in p:
            try:
                from .operator_value_expression_candidate import \
                    render_operator_value_condition
                return render_operator_value_condition(
                    {"type": ctype, "predicate": p}, language="en")
            except ValueError as exc:
                raise SerializationError(
                    exc.message, code=exc.code,
                    path=exc.path.replace("/condition", "/rimay_core/conditions/0"),
                ) from exc
        subj = _q(p["subject"])
        op = p.get("operator")
        surface = _OPERATOR_HANDLERS.get(op)
        if surface is None:
            # CG-02: 未対応operatorを"is"へ縮退しない
            raise SerializationError(
                f"operator {op!r} has no serializer handler",
                code="UNSUPPORTED_OPERATOR", path="/rimay_core/conditions/0/predicate/operator",
                expected=sorted(_OPERATOR_HANDLERS),
                found=op)
        if "value_expression" in p:
            if "value" in p or "unit" in p:
                raise SerializationError(
                    "scalar and value_expression authorities are mutually exclusive",
                    code="MULTI_VALUE_DUAL_AUTHORITY",
                    path="/rimay_core/conditions/0/predicate")
            try:
                value = _render_value_expression(p["value_expression"])
            except ValueError as exc:
                raise SerializationError(
                    str(exc), code=getattr(exc, "code", "MULTI_VALUE_INVALID_NODE"),
                    path=getattr(exc, "path", "/rimay_core/conditions/0/predicate/value_expression")) \
                    from exc
        else:
            unit = p.get("unit")
            if unit is not None and unit != "JPY":
                raise SerializationError(
                    f"unit {unit!r} is outside the comparison predicate contract",
                    code="UNSUPPORTED_OPERATOR", path="/rimay_core/conditions/0/predicate/unit",
                    expected=("JPY",), found=unit)
            value = _fmt_money(p["value"], unit) if unit == "JPY" \
                else f'"{en_label(p["value"])}"'
        return f"{kw} {subj} {surface} {value}"
    raise SerializationError(f"unsupported condition type: {ctype}",
                             code="PROFILE_OUT", path="/rimay_core/conditions/0/type",
                             expected=("WHEN", "AFTER", "BEFORE", "IF", "WHILE"), found=ctype)


def _store_literal(theme_id: str) -> str:
    """KEEP_15_2リテラル: term typeがpropertyならproperty、それ以外はvalue（§21.4）。"""
    t = term_ids().get(theme_id)
    return "property" if (t and t["type"] == "property") else "value"


def render_response(resp: dict) -> str:
    fam = resp["action"]["family"]
    b = binding(fam)

    # §21.4手順2--3: Canonicalのrimay_action_idが現行宣言と一致するか（不一致は生成しない）
    declared = _declared_action_id(fam)
    actual = (resp.get("action") or {}).get("rimay_action_id")
    if actual and actual != declared:
        raise SerializationError(
            f"rimay_action_id {actual!r} does not match declared binding {declared!r} for {fam}",
            code="ACTION_BINDING_MISMATCH", path="/rimay_core/response/action/rimay_action_id",
            expected=(declared,), found=actual)

    verb = b["verbs"][0]
    neg = " not" if resp["modality"] == "MUST_NOT" else ""
    s = f"{resp['actor']} must{neg} {verb}"

    if fam == "SEND":
        s += f" {_q(_require(resp, 'theme', fam))} to {_q(_require(resp, 'destination', fam))}"
        if resp.get("source"):
            s += f" from {_q(resp['source'])}"      # CG-03: SEND.sourceを出力
        if resp.get("channel"):
            s += f" through {_q(resp['channel'])}"
    elif fam == "UPDATE":
        s += f" {_q(_require(resp, 'property', fam))}"
        if resp.get("result_value"):
            s += f' to "{en_label(resp["result_value"])}"'
        elif resp["modality"] != "MUST_NOT":
            raise SerializationError(
                "required role 'result_value' missing for UPDATE (MUST)",
                code="MISSING_ROLE", path="/rimay_core/response/result_value",
                expected=("result_value",), found=None)
    elif fam == "CREATE":
        s += f" {_q(_require(resp, 'theme', fam))}"
        if resp.get("source"):
            s += f" from {_q(resp['source'])}"
    elif fam == "STORE":
        theme = _require(resp, "theme", fam)
        s += f' the {_store_literal(theme)} "{en_label(theme)}"'
        s += f" in {_q(_require(resp, 'location', fam))}"
    elif fam == "RECEIVE":
        s += f" {_q(_require(resp, 'theme', fam))} from {_q(_require(resp, 'source', fam))}"
        if resp.get("channel"):
            s += f" through {_q(resp['channel'])}"
    elif fam == "DISPLAY":
        s += f" {_q(_require(resp, 'theme', fam))} on {_q(_require(resp, 'display_location', fam))}"
    elif fam == "DELETE":
        s += f" {_q(_require(resp, 'theme', fam))}"
    elif fam == "VERIFY":
        # Gate B二名確定（VoR Table 12 p46）: by checking that形で固定（RC-006）
        s += f" {_q(_require(resp, 'theme', fam))}"
        if resp.get("rule"):
            s += f' by checking that "{en_label(resp["rule"])}"'

    elif fam == "CALCULATE":
        s += f" {_q(_require(resp, 'result', fam))} using {_q(_require(resp, 'input', fam))}"
    elif fam == "NOTIFY":
        # SAY_37_7語順: notify <content> to <destination> [using <channel>]（§2.5・D7）
        s += f" {_q(_require(resp, 'content', fam))} to {_q(_require(resp, 'destination', fam))}"
        if resp.get("channel"):
            s += f" using {_q(resp['channel'])}"
    else:
        raise SerializationError(f"serializer does not support family: {fam}",
                                 code="PROFILE_OUT",
                                 path="/rimay_core/response/action/family",
                                 expected=(), found=fam)
    frequency = resp.get("frequency")
    if frequency is not None:
        value = frequency["value"]
        number = str(value) if type(value) is int else format(value, "g")
        unit = frequency["unit"] + ("" if value == 1 else "s")
        s += f' every "{number} {unit}"'
    return s


def _response_classification(resp: dict) -> dict:
    fam = (resp.get("action") or {}).get("family")
    b = binding(fam) if fam else {}
    features = []
    classification = "emse_vor"
    if fam == "CREATE" and resp.get("source"):
        classification = "rimay_jp_extension"
        features.append("CREATE_SOURCE_FROM")
    if resp.get("frequency") is not None:
        classification = "rimay_jp_extension"
        features.append("ATOMIC_RESPONSE_FREQUENCY")
    if b.get("classification"):
        classification = b["classification"]     # NOTIFY: official_repository（格上げ禁止）
    return {
        "profile_version": _conf_profile_version(),
        "profile_content_hash": grammar_profile_hash(),
        "classification": classification,
        "rimay_action_id": b.get("rimay_action_id"),
        "emse_rule_id": b.get("emse_rule_id"),
        "extension_features": features,
    }


def _classification(core: dict, *, source_text: str | None = None) -> dict:
    """文単位のconformance分類（単一互換形＋複合式のleaf別分類）。"""
    if core.get("response_block") is not None:
        leaves = [_response_classification(response)
                  for _path, response in iter_core_responses(
                      core, source_text=source_text)]
        block = core["response_block"]
        features = ["ITEMIZED_RESPONSE_BLOCK", "BULLET_STRUCTURE"]
        if block.get("in_sequence"):
            features.append("SEQUENTIAL_RESPONSE_BLOCK")
        result = {
            "profile_version": _conf_profile_version(),
            "profile_content_hash": grammar_profile_hash(),
            "classification": "rimay_jp_extension",
            "rimay_action_id": None,
            "emse_rule_id": None,
            "extension_features": features,
            "response_block": True,
            "leaf_conformance": leaves,
        }
    elif core.get("response_expression") is None:
        result = _response_classification(core.get("response") or {})
    else:
        leaves = [_response_classification(response)
                  for _path, response in iter_core_responses(
                      core, source_text=source_text)]
        result = {
            "profile_version": _conf_profile_version(),
            "profile_content_hash": grammar_profile_hash(),
            "classification": "rimay_jp_extension",
            "rimay_action_id": None,
            "emse_rule_id": None,
            "extension_features": ["RESPONSE_COMBINATION"],
            "response_expression": True,
            "leaf_conformance": leaves,
        }
    if core.get("condition_expression") is not None:
        result["classification"] = "rimay_jp_extension"
        features = result.setdefault("extension_features", [])
        if "CONDITION_COMBINATION" not in features:
            features.append("CONDITION_COMBINATION")
        result["condition_expression"] = True
        result["condition_leaf_count"] = len(list(iter_core_conditions(core)))
    comparison_operators = sorted({
        (condition.get("predicate") or {}).get("operator")
        for _path, condition in iter_core_conditions(core)
        if (condition.get("predicate") or {}).get("operator") is not None
    })
    if comparison_operators:
        result["classification"] = "rimay_jp_extension"
        features = result.setdefault("extension_features", [])
        if "COMPARISON_OPERATOR" not in features:
            features.append("COMPARISON_OPERATOR")
        result["comparison_operators"] = comparison_operators
        result["paper_claim"] = "withheld"
    multi_value_count = sum(
        1 for _path, condition in iter_core_conditions(core)
        if "value_expression" in (condition.get("predicate") or {})
    )
    if multi_value_count:
        result["classification"] = "rimay_jp_extension"
        features = result.setdefault("extension_features", [])
        if "MULTI_VALUE" not in features:
            features.append("MULTI_VALUE")
        result["multi_value"] = True
        result["multi_value_condition_count"] = multi_value_count
        result["paper_claim"] = "withheld"
    operator_value_count = sum(
        1 for _path, condition in iter_core_conditions(core)
        if "operand" in (condition.get("predicate") or {})
    )
    if operator_value_count:
        result["classification"] = "rimay_jp_extension"
        features = result.setdefault("extension_features", [])
        if "OPERATOR_VALUE_EXPRESSION" not in features:
            features.append("OPERATOR_VALUE_EXPRESSION")
        result["operator_value_expression"] = True
        result["operator_value_condition_count"] = operator_value_count
        result["paper_claim"] = "withheld"
    return result


def render_requirement_views(canonical: dict) -> dict:
    """戻り値: {english_rimay, sidecar, manifest}（原子的生成）。"""
    core = canonical["rimay_core"]
    source_text = (canonical.get("source") or {}).get("text")
    condition_problems = condition_core_findings(core)
    if condition_problems:
        first = condition_problems[0]
        raise SerializationError(
            first["message"], code=first["code"], path=first["path"])
    problems = response_core_findings(core, source_text=source_text)
    if problems:
        first = problems[0]
        raise SerializationError(
            first["message"], code=first["code"], path=first["path"])
    parts = []
    if core.get("scope") and core["scope"].get("function"):
        parts.append(f'For "{core["scope"]["function"]}",')
    if core.get("condition_expression") is not None:
        rendered_condition = render_condition_expression(
            core["condition_expression"], render_condition, language="en")
        parts.append(rendered_condition + ",")
    else:
        for cond in core.get("conditions") or []:
            parts.append(render_condition(cond) + ",")
    if core.get("response_block") is not None:
        if ((canonical.get("extensions") or {}).get("time_constraints") or []):
            raise SerializationError(
                "time constraint scope across Response Block items is not adopted",
                code="RESPONSE_BLOCK_EXTENSION_SCOPE",
                path="/extensions/time_constraints")
        rendered = render_response_block(
            core["response_block"], render_response, language="en",
            source_text=source_text)
        parts.append(rendered + ".")
    elif core.get("response_expression") is not None:
        rendered = render_response_expression(
            core["response_expression"], render_response, language="en")
        parts.append(rendered + ".")
    else:
        parts.append(render_response(core["response"]) + ".")
    english = " ".join(parts)

    sidecar = {"extensions": canonical.get("extensions") or {}}

    def _h(s: str) -> str:
        return "sha256:" + hashlib.sha256(s.encode("utf-8")).hexdigest()

    import json
    manifest = {
        "requirement_id": canonical["requirement_id"],
        "canonical_revision": canonical["revision"],
        "canonical_hash": canonical_hash(canonical),
        "schema_version": canonical["schema_version"],
        "profile_version": canonical["profile_version"],
        "projection_version": "0.1.0",
        "serializer_version": SERIALIZER_VERSION,
        "conformance": _classification(core, source_text=source_text),   # §19.4
        "artifacts": {
            "english_rimay": {"file": "english.rimay", "hash": _h(english)},
            "sidecar": {"file": "sidecar.yaml",
                        "hash": _h(json.dumps(sidecar, sort_keys=True, ensure_ascii=False))},
        },
    }
    return {"english_rimay": english, "sidecar": sidecar, "manifest": manifest}
