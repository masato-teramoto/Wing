"""Phase 3E評価ランナー: 下流生成のGATE-3E条件を検査する。"""
from pathlib import Path

import yaml

from . import _ROOT  # noqa: F401
from .candidate_extractor import extract  # noqa: E402
from .approval import promote_to_review_ready, approve  # noqa: E402
from .question_planner import plan  # noqa: E402
from generators.acceptance_criteria import generate as gen_ac  # noqa: E402
from generators.test_candidates import generate as gen_tc  # noqa: E402


def run_case(path: Path) -> dict:
    case = yaml.safe_load(path.read_text(encoding="utf-8"))
    cid = case["case_id"]
    out = extract({"document_id": cid, "text": case["japanese"]}, f"REQ-{cid}")
    canonical = out["canonical"]
    if canonical is None:
        return {"case_id": cid, "verdict": "FAIL", "detail": "抽出失敗"}
    problems: list[str] = []

    if case.get("approve", True):
        pr = promote_to_review_ready(canonical)
        if not pr["ok"]:
            return {"case_id": cid, "verdict": "FAIL",
                    "detail": f"review_ready昇格失敗: {pr['reasons']}"}
        if not canonical.get("versions_used"):
            problems.append("versions_usedが記録されていない")
        ap = approve(canonical, "usa", case.get("approved_at", "2026-08-03"))
        if not ap["ok"]:
            return {"case_id": cid, "verdict": "FAIL", "detail": f"承認失敗: {ap['reasons']}"}
        # 承認によりRULE-ACCEPTANCE/TESTGENが発火することを確認（Rule↔生成の対応）
        autos = {a["action_type"]: a["rule_id"]
                 for a in plan(canonical)["auto_actions"]}
        for t in ("GENERATE_ACCEPTANCE_CRITERIA", "GENERATE_TEST_CANDIDATES"):
            if t not in autos:
                problems.append(f"承認後に{t}が発火しない")

    ac = gen_ac(canonical)
    tc = gen_tc(canonical, ac["criteria"]) if ac["ok"] else \
        gen_tc(canonical, {"trace": {"slots": [], "provenance": []}})

    if case.get("approve", True):
        if not ac["ok"]:
            return {"case_id": cid, "verdict": "FAIL",
                    "detail": f"受入基準生成失敗: {ac['findings']}"}
        crit = ac["criteria"]
        # 要求ID・revision引き継ぎ
        if crit["requirement_id"] != canonical["requirement_id"]:
            problems.append("requirement_id未引き継ぎ")
        # 期待文言（extensionsの反映を含む）
        text = "\n".join(crit["gherkin"])
        for s in case.get("expected_gherkin_contains") or []:
            if s not in text:
                problems.append(f"受入基準に「{s}」がない: {crit['gherkin']}")
        # トレース: スロット実在・Provenance解決可能・Rule記録
        slot_keys = set(canonical["resolution"]["slots"])
        prv_ids = {p["id"] for p in canonical["provenance"]}
        trace = crit["trace"]
        if not trace["slots"] or not set(trace["slots"]) <= slot_keys:
            problems.append(f"トレースslot不正: {trace['slots']}")
        if not trace["provenance"] or not set(trace["provenance"]) <= prv_ids:
            problems.append(f"トレースprovenance不正: {trace['provenance']}")
        if "RULE-ACCEPTANCE-001" not in trace["rules"]:
            problems.append("適用Rule未記録")
        # テスト候補
        kinds = {c["kind"] for c in tc["candidates"]}
        for k in case.get("expected_test_kinds") or []:
            if k not in kinds:
                problems.append(f"テスト候補種別{k}がない（{sorted(kinds)}）")
        for c in tc["candidates"]:
            if not set(c["trace"]["slots"]) <= slot_keys:
                problems.append(f"候補{c['id']}のトレースslot不正")
    else:
        # 未承認: 生成拒否と理由の要求スロット関連付け
        if ac["ok"] or tc["ok"]:
            problems.append("未承認要求で生成が実行された")
        else:
            f = ac["findings"][0]
            if f["code"] != "GENERATOR" or f.get("path") != "/status":
                problems.append(f"拒否理由が/statusへ関連付いていない: {f}")

    if problems:
        return {"case_id": cid, "verdict": "FAIL", "detail": "; ".join(problems)}
    n = len(tc["candidates"]) if case.get("approve", True) else 0
    return {"case_id": cid, "verdict": "PASS",
            "detail": (f"criteria={len(ac['criteria']['gherkin'])}行 tests={n}件"
                       if case.get("approve", True) else "未承認生成を拒否（/statusへ関連付け）")}


def run_generation_corpus(gen_dir: Path) -> dict:
    results = [run_case(p) for p in sorted(gen_dir.glob("*.yaml"))]
    summary = {
        "pass": sum(1 for r in results if r["verdict"] == "PASS"),
        "fail": sum(1 for r in results if r["verdict"] == "FAIL"),
    }
    return {"results": results, "summary": summary}
