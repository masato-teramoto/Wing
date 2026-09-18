"""test-case-generator: 承認済みCanonical＋受入基準 → テスト候補（Phase 3E）。

生成する候補種別:
- positive:    受入基準の正常系
- negative:    条件不成立時の非実行 ／ 禁止動作の試行拒否
- boundary:    数値条件（以上・以下）の境界値
- performance: 期限（DEADLINE）の計測
各候補は使用スロット・Rule・Provenanceへのトレースを持つ。
"""
from . import _ROOT  # noqa: F401
from rimay_jp_core.jp_serializer import jp_name, role_phrase, response_stem  # noqa: E402
from rimay_jp_core.model import finding  # noqa: E402
from .comparison_predicate import (  # noqa: E402
    ComparisonConsumerError,
    ordering_boundary_oracle,
    validate_scalar_predicate,
)


def generate(canonical: dict, criteria: dict,
             rule_id: str = "RULE-TESTGEN-001") -> dict:
    if canonical.get("status") != "approved":
        return {"ok": False, "candidates": [],
                "findings": [finding("GENERATOR",
                                     f"承認済み要求のみ生成対象です（現在: "
                                     f"{canonical.get('status')}）。", "/status")]}

    core = canonical["rimay_core"]
    for expression_name, label in (
        ("condition_expression", "Condition"),
        ("response_expression", "Response"),
        ("response_block", "Response Block"),
    ):
        if core.get(expression_name) is not None:
            return {
                "ok": False, "candidates": [],
                "findings": [finding(
                    "GENERATOR",
                    f"{label}のテスト候補展開規則が未採用です。",
                f"/rimay_core/{expression_name}")],
            }
    for index, condition in enumerate(core.get("conditions") or []):
        predicate = condition.get("predicate") or {}
        if "operand" in predicate:
            return {
                "ok": False, "candidates": [],
                "findings": [finding(
                    "GENERATOR",
                    "Typed Operator operandのtest oracle生成規則は未採用です。",
                    f"/rimay_core/conditions/{index}/predicate/operand",
                    operator_value_code="OPERATOR_VALUE_CONSUMER_RULE_REQUIRED")],
            }
        if "value_expression" in predicate:
            return {
                "ok": False, "candidates": [],
                "findings": [finding(
                    "GENERATOR",
                    "Multi-value treeのtest oracle生成規則は未採用です。",
                    f"/rimay_core/conditions/{index}/predicate/value_expression",
                    multi_value_code="MULTI_VALUE_CONSUMER_RULE_REQUIRED")],
            }
        if predicate:
            path = f"/rimay_core/conditions/{index}/predicate"
            try:
                validate_scalar_predicate(predicate, path)
            except ComparisonConsumerError as exc:
                return {
                    "ok": False, "candidates": [],
                    "findings": [exc.as_finding()],
                }
    resp = core["response"]
    if resp.get("frequency") is not None:
        return {
            "ok": False, "candidates": [],
            "findings": [finding(
                "GENERATOR",
                "Atomic Response頻度のテスト候補展開規則が未採用です。",
                "/rimay_core/response/frequency")],
        }
    fam = resp["action"]["family"]
    rid = canonical["requirement_id"]
    stem = response_stem(fam)
    body = f"{jp_name(resp['actor'])}は{role_phrase(canonical)}{stem}"
    slots = criteria["trace"]["slots"]
    prv = criteria["trace"]["provenance"]
    cands: list[dict] = []

    def add(kind: str, description: str, extra_slots: list[str] | None = None):
        cands.append({
            "id": f"TC-{rid}-{len(cands) + 1:02d}",
            "kind": kind,
            "description": description,
            "requirement_id": rid,
            "canonical_revision": canonical["revision"],
            "trace": {"slots": sorted(set(slots + (extra_slots or []))),
                      "rules": [rule_id], "provenance": prv},
        })

    # positive / negative（モダリティ別）
    if resp["modality"] == "MUST":
        add("positive", f"受入基準の手順を実行し、{body}することを確認する。")
        if core.get("conditions"):
            add("negative", "トリガー・条件が成立しない状態では応答が実行されないことを確認する。")
    else:
        add("negative", f"{body}る操作を試行し、拒否されることを確認する。")

    # boundary（契約上数値であるJPY orderingだけ）
    for i, cond in enumerate(core.get("conditions") or []):
        p = cond.get("predicate") or {}
        if not p:
            continue
        path = f"/rimay_core/conditions/{i}/predicate"
        oracle = ordering_boundary_oracle(p, path)
        if oracle is not None:
            add("boundary", oracle["description"], oracle["slots"])

    # performance（期限）
    for i, tc in enumerate((canonical.get("extensions") or {}).get("time_constraints") or []):
        if tc.get("kind") == "DEADLINE" and tc.get("value") is not None:
            add("performance",
                f"応答が{tc['value']}秒以内に完了することを計測する。",
                [f"/extensions/time_constraints/{i}/value"])

    return {"ok": True, "candidates": cands, "findings": []}
