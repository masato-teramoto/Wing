"""Phase 3C評価ランナー: 対話的要求補完のGATE-3C機能条件を検査する。"""
from pathlib import Path

import yaml

from . import _ROOT  # noqa: F401
from .candidate_extractor import extract  # noqa: E402
from .dialogue_state import DialogueState  # noqa: E402
from rimay_jp_core.patch import apply_canonical_patch  # noqa: E402


def _negative_patch_checks(ds: DialogueState) -> list[str]:
    """Patch統制の負テスト（適用されないこと）。"""
    problems = []
    stale = {"operation": "replace_slot", "requirement_id": ds.canonical["requirement_id"],
             "base_revision": 1, "path": "/rimay_core/response/theme",
             "new_value": "AuditLog", "new_status": "proposed",
             "evidence": {"type": "tool_result", "reference": "term:AuditLog"}}
    res = apply_canonical_patch(ds.canonical, stale)
    if res["ok"] or res["findings"][0]["evidence"].get("reason") != "revision_conflict":
        problems.append("旧revision Patchが拒否されない")

    bad_confirm = {"operation": "replace_slot",
                   "requirement_id": ds.canonical["requirement_id"],
                   "base_revision": ds.canonical["revision"],
                   "path": "/rimay_core/response/theme",
                   "new_value": "AuditLog", "new_status": "confirmed",
                   "evidence": {"type": "tool_result", "reference": "term:AuditLog"}}
    res = apply_canonical_patch(ds.canonical, bad_confirm)
    if res["ok"] or res["findings"][0]["code"] != "PROVENANCE-MISSING":
        problems.append("根拠のないconfirmed遷移が拒否されない")
    return problems


def run_case(path: Path) -> dict:
    case = yaml.safe_load(path.read_text(encoding="utf-8"))
    cid = case["case_id"]
    out = extract({"document_id": cid, "text": case["japanese"]}, f"REQ-{cid}")
    if out["canonical"] is None:
        return {"case_id": cid, "verdict": "FAIL", "detail": "抽出失敗"}

    ds = DialogueState(out["canonical"])
    script = list(case.get("script") or [])
    asked_order: list[str] = []
    rounds = 0
    while rounds < 30:
        rounds += 1
        qs = ds.open_questions()
        if not qs:
            break
        q = qs[0]
        # GATE-3C条件1: 質問↔スロット↔Ruleの対応
        if not q.get("rule_id") or not q.get("target_path") or not q.get("stage"):
            return {"case_id": cid, "verdict": "FAIL",
                    "detail": f"質問にrule_id/target/stageがない: {q}"}
        # FB-014再発防止: 質問文の正規キー question_text を必ず持つ
        # （統合契約§6 questionRecordがquestion_text必須。経路差による欠落を禁止）
        if not q.get("question_text"):
            return {"case_id": cid, "verdict": "FAIL",
                    "detail": f"質問にquestion_textがない: {q.get('rule_id')}"}
        asked_order.append(q["target_path"])
        entry = next((s for s in script if s["target"] == q["target_path"]), None)
        if entry is None:
            return {"case_id": cid, "verdict": "FAIL",
                    "detail": f"scriptにない質問: {q['target_path']}（{q['rule_id']}）"}
        res = ds.answer(q, entry["answer"])
        if not res["ok"]:
            return {"case_id": cid, "verdict": "FAIL",
                    "detail": f"回答適用失敗 {q['target_path']}: {res['reason']}"}
        script.remove(entry)

    problems: list[str] = []
    if script:
        problems.append(f"未消化のscript: {[s['target'] for s in script]}")
    if ds.open_questions():
        problems.append(f"未解消の質問: {[q['target_path'] for q in ds.open_questions()]}")

    exp = case["expected_final"]
    if ds.canonical["status"] != exp["status"]:
        problems.append(f"status: expected={exp['status']} got={ds.canonical['status']}")
    if ds.canonical["revision"] < exp.get("min_revision", 1):
        problems.append(f"revision不足: {ds.canonical['revision']}")

    # GATE-3C条件3: confirmed遷移の根拠（user_answer / knowledge_asset / rule）
    prv = {p["id"]: p for p in ds.canonical["provenance"]}
    for ptr in exp.get("confirmed") or []:
        slot = ds.canonical["resolution"]["slots"].get(ptr)
        if not slot or slot["status"] != "confirmed":
            problems.append(f"confirmed期待が不成立: {ptr} -> {slot}")
            continue
        sources = {prv[r]["source_type"] for r in slot.get("provenance_refs") or []}
        if not sources & {"user_answer", "knowledge_asset", "rule"}:
            problems.append(f"confirmedに根拠がない: {ptr}（{sources}）")

    # GATE-3C条件2の可観測性: 再検査により新質問が後段で出現する（部分列検査）
    order = case.get("expected_question_order") or []
    it = iter(asked_order)
    if not all(any(o == a for a in it) for o in order):
        problems.append(f"質問順序が期待部分列と不一致: {asked_order}")

    problems += _negative_patch_checks(ds)

    if problems:
        return {"case_id": cid, "verdict": "FAIL", "detail": "; ".join(problems)}
    return {"case_id": cid, "verdict": "PASS",
            "detail": f"rounds={rounds - 1} revision={ds.canonical['revision']} "
                      f"status={ds.canonical['status']}"}


def run_dialogue_corpus(dlg_dir: Path) -> dict:
    results = [run_case(p) for p in sorted(dlg_dir.glob("*.yaml"))]
    summary = {
        "pass": sum(1 for r in results if r["verdict"] == "PASS"),
        "fail": sum(1 for r in results if r["verdict"] == "FAIL"),
    }
    return {"results": results, "summary": summary}
