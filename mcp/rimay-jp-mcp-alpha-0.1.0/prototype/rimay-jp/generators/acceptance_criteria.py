"""acceptance-test-generator: 承認済みCanonical → Given/When/Then受入基準（Phase 3E）。

- 承認済み（approved）以外は生成を拒否し、理由を要求スロット（/status）へ関連付ける。
- extensionsに保持した時間制約はAnd句として生成物へ反映する（欠落禁止）。
- トレース: 使用スロット（CanonicalPointer）・適用Rule・Provenance参照を記録する。
"""
from . import _ROOT  # noqa: F401
from rimay_jp_core.jp_serializer import (  # noqa: E402
    jp_name, role_phrase, response_stem, trigger_dict_form)
from rimay_jp_core.model import finding, canonical_hash  # noqa: E402
from .comparison_predicate import (  # noqa: E402
    ComparisonConsumerError,
    render_given,
    validate_scalar_predicate,
)


def _collect_trace(canonical: dict, used_slots: list[str], rules: list[str]) -> dict:
    slots = canonical["resolution"]["slots"]
    prv = []
    for p in used_slots:
        prv += (slots.get(p) or {}).get("provenance_refs") or []
    return {"slots": sorted(set(used_slots)), "rules": rules,
            "provenance": sorted(set(prv))}


def _when_line(cond: dict, idx: int, used: list[str]) -> str:
    ev = cond["event"]
    fam = ev["action"]["family"]
    used += [f"/rimay_core/conditions/{idx}/event/actor",
             f"/rimay_core/conditions/{idx}/event/object",
             f"/rimay_core/conditions/{idx}/event/action/family"]
    s = f"{jp_name(ev['actor'])}が{jp_name(ev['object'])}を"
    if ev.get("value"):
        used.append(f"/rimay_core/conditions/{idx}/event/value")
        s += f"「{jp_name(ev['value'])}」に"
    return s + trigger_dict_form(fam)


def _given_line(cond: dict, idx: int, used: list[str]) -> str:
    p = cond["predicate"]
    path = f"/rimay_core/conditions/{idx}/predicate"
    rendered, slots = render_given(p, path)
    used.extend(slots)
    return rendered


def generate(canonical: dict, rule_id: str = "RULE-ACCEPTANCE-001") -> dict:
    if canonical.get("status") != "approved":
        return {"ok": False, "criteria": None,
                "findings": [finding("GENERATOR",
                                     f"承認済み要求のみ生成対象です（現在: "
                                     f"{canonical.get('status')}）。", "/status")]}

    core = canonical["rimay_core"]
    if core.get("condition_expression") is not None:
        return {
            "ok": False, "criteria": None,
            "findings": [finding(
                "GENERATOR",
                "Condition式木をGiven/When列へ変換する規則が未採用です。",
                "/rimay_core/condition_expression")],
        }
    if core.get("response_expression") is not None:
        return {
            "ok": False, "criteria": None,
            "findings": [finding(
                "GENERATOR",
                "Response式木を単一Thenへ変換する規則が未採用です。",
                "/rimay_core/response_expression")],
        }
    if core.get("response_block") is not None:
        return {
            "ok": False, "criteria": None,
            "findings": [finding(
                "GENERATOR",
                "Response BlockをGiven/Thenへ展開する規則が未採用です。",
                "/rimay_core/response_block")],
        }
    for index, condition in enumerate(core.get("conditions") or []):
        predicate = condition.get("predicate") or {}
        if "operand" in predicate:
            return {
                "ok": False, "criteria": None,
                "findings": [finding(
                    "GENERATOR",
                    "Typed Operator operandをGivenへ展開する規則は未採用です。",
                    f"/rimay_core/conditions/{index}/predicate/operand",
                    operator_value_code="OPERATOR_VALUE_CONSUMER_RULE_REQUIRED")],
            }
        if "value_expression" in predicate:
            return {
                "ok": False, "criteria": None,
                "findings": [finding(
                    "GENERATOR",
                    "Multi-value treeをGivenへ展開する規則は未採用です。",
                    f"/rimay_core/conditions/{index}/predicate/value_expression",
                    multi_value_code="MULTI_VALUE_CONSUMER_RULE_REQUIRED")],
            }
        if predicate:
            path = f"/rimay_core/conditions/{index}/predicate"
            try:
                validate_scalar_predicate(predicate, path)
            except ComparisonConsumerError as exc:
                return {
                    "ok": False, "criteria": None,
                    "findings": [exc.as_finding()],
                }
    resp = core["response"]
    if resp.get("frequency") is not None:
        return {
            "ok": False, "criteria": None,
            "findings": [finding(
                "GENERATOR",
                "Atomic Response頻度を受入基準へ展開する規則が未採用です。",
                "/rimay_core/response/frequency")],
        }
    fam = resp["action"]["family"]
    used: list[str] = ["/rimay_core/response/actor", "/rimay_core/response/modality",
                       "/rimay_core/response/action/family"]
    for field in ("theme", "property", "result_value", "destination", "source",
                  "location", "display_location", "channel", "rule", "input",
                  "result", "content"):
        if resp.get(field):
            used.append(f"/rimay_core/response/{field}")

    given, when = [], []
    for i, cond in enumerate(core.get("conditions") or []):
        if cond["type"] in ("WHEN", "AFTER", "BEFORE") and cond.get("event"):
            when.append(_when_line(cond, i, used))
        elif cond.get("predicate"):
            given.append(_given_line(cond, i, used))

    stem = response_stem(fam)
    body = f"{jp_name(resp['actor'])}は{role_phrase(canonical)}"
    then = [f"{body}{stem}する" if resp["modality"] == "MUST"
            else f"{body}{stem}しないこと"]

    and_lines = []
    for i, tc in enumerate((canonical.get("extensions") or {}).get("time_constraints") or []):
        if tc.get("value") is None:
            continue
        used.append(f"/extensions/time_constraints/{i}/value")
        if tc.get("kind") == "DEADLINE":
            and_lines.append(f"応答は{tc['value']}秒以内に完了する")
        elif tc.get("kind") == "RETENTION":
            and_lines.append(f"保存期間は{tc['value']}年間である")

    gherkin = ([f"Given {g}" for g in given] + [f"When {w}" for w in when]
               + [f"Then {t}" for t in then] + [f"And {a}" for a in and_lines])
    criteria = {
        "requirement_id": canonical["requirement_id"],
        "canonical_revision": canonical["revision"],
        "canonical_hash": canonical_hash(canonical),
        "gherkin": gherkin,
        "trace": _collect_trace(canonical, used, [rule_id]),
    }
    return {"ok": True, "criteria": criteria, "findings": []}
