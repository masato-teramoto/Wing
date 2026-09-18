"""Step 7評価ランナー: RQK-E Experience Store／ProjectionのGate検査。

Gate（adaptation §3 Step 7）: **Experience StoreからProjectionを100%再構築可能**
（PROJECTION_REBUILD_RATE=100%。ディスクから再読込したストアで再構築した
Projectionが完全一致し、追記が即座に反映される＝キャッシュでない）。
加えて:
- 一次記録の契約適合（experience-record.schema.json）
- 類似事例の助言専用性（advisory=true・evidence無し・similar_case根拠のPatchは
  apply_canonical_patchが拒否）
- 昇格の排他分岐と評価リーク防止（参照済み→holdout拒否、dev/regression⇔holdout移動不可、
  匿名化・レビュー未了の直接自動登録拒否）
を機械検査する。実行はcorpusケースの決定論的リプレイ（時刻・乱数なし）。
"""
from __future__ import annotations

import copy
import json
from pathlib import Path

import yaml
from jsonschema import Draft202012Validator

from . import _ROOT  # noqa: F401
from .candidate_extractor import extract  # noqa: E402
from .dialogue_state import DialogueState  # noqa: E402
from .validation_router import validate_all  # noqa: E402
from .repair_planner import plan_repairs  # noqa: E402
from .experience_store import ExperienceStore  # noqa: E402
from .experience_projections import build_projections, find_similar  # noqa: E402
from .feedback_handler import handle  # noqa: E402
from .approval import promote_to_review_ready  # noqa: E402
from rimay_jp_core.patch import apply_canonical_patch  # noqa: E402
from rimay_jp_core.lexicon import ROOT as RIMAY_ROOT  # noqa: E402


def _dumps(obj) -> str:
    return json.dumps(obj, ensure_ascii=False, sort_keys=True)


def _load_case(root: Path, rel: str) -> dict:
    return yaml.safe_load((root / rel).read_text(encoding="utf-8"))


def _record_report(store: ExperienceStore, canonical: dict, report: dict):
    store.append("validation_report",
                 {"report_id": report["report_id"],
                  "canonical_hash": report["canonical_hash"],
                  "issue_codes": sorted({f["normalized_issue_code"]
                                         for f in report["findings"]})},
                 requirement_id=canonical["requirement_id"],
                 revision=canonical["revision"])


def _replay(store: ExperienceStore, root: Path) -> dict:
    """corpusケースの決定論的リプレイで一次記録を構築する。"""
    ctx: dict = {}

    # 1) クリーン要求（development SEND-001）: revision＋report＋承認試行
    dev = _load_case(root, "corpus/development/SEND-001.yaml")
    out = extract({"document_id": "SEND-001", "text": dev["japanese"].strip()},
                  "REQ-EXP-SEND-001")
    c1 = out["canonical"]
    res1 = validate_all(c1)
    store.append_canonical_revision(copy.deepcopy(c1))
    _record_report(store, c1, res1["report"])
    ready = promote_to_review_ready(copy.deepcopy(c1))
    store.append("approval",
                 {"target_status": "review_ready", "ok": ready["ok"],
                  "reasons": ready.get("reasons") or []},
                 requirement_id=c1["requirement_id"], revision=c1["revision"])

    # 2) 修復フロー（VAL-002: 宛先欠落→質問→回答→Patch→再検証）: 修正前後ペアの一次記録
    val = _load_case(root, "corpus/validation/VAL-002.yaml")
    out = extract({"document_id": "VAL-002", "text": val["japanese"].strip()},
                  "REQ-EXP-VAL-002")
    c2 = out["canonical"]
    res2 = validate_all(c2)
    store.append_canonical_revision(copy.deepcopy(c2))
    _record_report(store, c2, res2["report"])

    ds = DialogueState(c2)
    plan_out = plan_repairs(ds.canonical, res2["report"])
    target = "/rimay_core/response/destination"
    q = next(qq for qq in plan_out["questions"] if qq.get("target_path") == target)
    before_status = (ds.canonical["resolution"]["slots"].get(target)
                     or {}).get("status", "unknown")
    r = ds.answer(q, "顧客メールアドレス")
    res3 = validate_all(copy.deepcopy(ds.canonical))
    resolved = "MISSING_REQUIRED_ROLE" not in {
        f["normalized_issue_code"] for f in res3["report"]["findings"]}
    from .rule_engine import value_at
    store.append("patch_applied",
                 {"target_path": target,
                  "issue_code": q.get("normalized_issue_code"),
                  "rule_id": q.get("rule_id"),
                  "before_status": before_status,
                  "after_value": value_at(ds.canonical, target),
                  "answer": "顧客メールアドレス",
                  "evidence_type": "user_answer",
                  "resolved": bool(r["ok"] and resolved)},
                 requirement_id=ds.canonical["requirement_id"],
                 revision=ds.canonical["revision"])
    store.append_canonical_revision(copy.deepcopy(ds.canonical))
    _record_report(store, ds.canonical, res3["report"])
    ctx["repaired"] = ds.canonical

    # 3) Feedback（FB-001/FB-003のリプレイ）
    for rel in ("corpus/feedback/FB-001.yaml", "corpus/feedback/FB-003.yaml"):
        case = _load_case(root, rel)
        fb = handle(case)
        store.append("feedback", fb, requirement_id=(case.get("context") or {})
                     .get("requirement_id") or "-")
    return ctx


def run_step7(root: Path, *, store_path: Path | None = None) -> dict:
    results = []
    path = store_path or root / "experience" / "store.jsonl"
    exp_dir = path.parent
    store = ExperienceStore(path, fresh=True)
    ctx = _replay(store, root)

    # --- 一次記録の契約適合 ---
    schema = json.loads((RIMAY_ROOT / "canonical" / "experience-record.schema.json")
                        .read_text(encoding="utf-8"))
    validator = Draft202012Validator(schema)
    errs = [f"{r['record_id']}: {e.message}"
            for r in store.records() for e in validator.iter_errors(r)]
    results.append({"case_id": "EXP-CONTRACT",
                    "verdict": "FAIL" if errs else "PASS",
                    "detail": errs[0] if errs else
                    f"{len(store.records())}レコードがschema適合"})

    # --- Gate: Projection 100%再構築（再読込→再構築→完全一致、追記の即時反映） ---
    problems: list[str] = []
    p1 = build_projections(store)
    reloaded = ExperienceStore(store.path)  # ディスクから再読込
    p2 = build_projections(reloaded)
    sections = ["meta", "similar_case_index", "repair_pairs", "question_success"]
    equal = [s for s in sections if _dumps(p1[s]) == _dumps(p2[s])]
    rebuild_rate = len(equal) / len(sections)
    if rebuild_rate < 1.0:
        problems.append(f"再構築不一致: {sorted(set(sections) - set(equal))}")
    n_pairs = len(p1["repair_pairs"])
    store.append("patch_applied",
                 {"target_path": "/rimay_core/response/modality",
                  "issue_code": "MISSING_MODALITY", "rule_id": "RULE-MODALITY-001",
                  "before_status": "unknown", "after_value": "MUST",
                  "answer": "必須", "evidence_type": "user_answer",
                  "resolved": True},
                 requirement_id="REQ-EXP-FRESH", revision=2)
    p3 = build_projections(store)
    if len(p3["repair_pairs"]) != n_pairs + 1:
        problems.append("追記がProjectionへ反映されない（キャッシュの疑い）")
    results.append({"case_id": "EXP-REBUILD",
                    "verdict": "FAIL" if problems else "PASS",
                    "detail": "; ".join(problems) if problems else
                    f"再構築率={rebuild_rate:.0%}（{len(equal)}/{len(sections)}）・追記即時反映"})

    # --- 修正前後ペアの内容（修復フローの一次記録が遡れる） ---
    problems = []
    pair = next((p for p in p1["repair_pairs"]
                 if p["target_path"] == "/rimay_core/response/destination"), None)
    if pair is None:
        problems.append("宛先修復の修正前後ペアがない")
    else:
        if pair["before_status"] != "unknown" or not pair["after_value"]:
            problems.append(f"前後状態が不正: {pair}")
        if pair["evidence_type"] != "user_answer" or not pair["resolved"]:
            problems.append(f"根拠・収束が不正: {pair}")
        if pair["issue_code"] != "MISSING_REQUIRED_ROLE":
            problems.append(f"issue code欠落: {pair['issue_code']}")
    results.append({"case_id": "EXP-REPAIR-PAIR",
                    "verdict": "FAIL" if problems else "PASS",
                    "detail": "; ".join(problems) if problems else
                    "unknown→confirmed（user_answer・収束・issue code追跡）"})

    # --- 類似事例の助言専用性 ---
    problems = []
    hits = find_similar(p1, store, ctx["repaired"])
    if not hits:
        problems.append("類似事例が返らない（SEND同士で類似するはず）")
    else:
        if not all(h.get("advisory") for h in hits):
            problems.append("advisoryフラグ欠落")
        if any("evidence" in h for h in hits):
            problems.append("類似事例がevidence形式を含む（根拠化の危険）")
        patch = {"operation": "replace_slot",
                 "requirement_id": ctx["repaired"]["requirement_id"],
                 "base_revision": ctx["repaired"]["revision"],
                 "path": "/rimay_core/response/theme",
                 "expected_status": (ctx["repaired"]["resolution"]["slots"]
                                     .get("/rimay_core/response/theme")
                                     or {}).get("status", "unknown"),
                 "new_value": "InvoicePDF", "new_status": "confirmed",
                 "evidence": {"type": "similar_case",
                              "reference": hits[0]["record_id"]}}
        res = apply_canonical_patch(copy.deepcopy(ctx["repaired"]), patch)
        if res["ok"]:
            problems.append("similar_case根拠のconfirmed Patchが拒否されない")
    results.append({"case_id": "EXP-SIMILAR-ADVISORY",
                    "verdict": "FAIL" if problems else "PASS",
                    "detail": "; ".join(problems) if problems else
                    f"類似{len(hits)}件（助言専用）・similar_case根拠Patchは拒否"})

    # --- 昇格の排他分岐・評価リーク防止 ---
    problems = []
    referenced = sorted(store.referenced_ids())[0]
    if store.promote(referenced, "holdout", anonymized=True, reviewed=True)["ok"]:
        problems.append("参照済みレコードのholdout昇格が拒否されない（評価リーク）")
    if not store.promote(referenced, "development_regression",
                         anonymized=True, reviewed=True)["ok"]:
        problems.append("development/regression昇格が通らない")
    if store.promote(referenced, "holdout", anonymized=True, reviewed=True)["ok"]:
        problems.append("昇格済みレコードの再昇格が拒否されない（排他分岐違反）")
    unreferenced = next(r["record_id"] for r in store.records("feedback")
                        if r["record_id"] not in store.referenced_ids()
                        and store.promoted_lane(r["record_id"]) is None)
    if store.promote(unreferenced, "holdout")["ok"]:
        problems.append("匿名化・レビュー未了の昇格が拒否されない（直接自動登録）")
    res = store.promote(unreferenced, "holdout", anonymized=True, reviewed=True)
    if not res["ok"]:
        problems.append(f"未参照レコードのholdout昇格が通らない: {res['reason']}")
    elif res["record"]["payload"]["status"] != "frozen":
        problems.append("holdout昇格が凍結・隔離されない")
    if str(store.path).replace("\\", "/").find("/corpus/") >= 0:
        problems.append("Experience Storeがcorpus/配下にある（物理分離違反）")
    results.append({"case_id": "EXP-PROMOTION",
                    "verdict": "FAIL" if problems else "PASS",
                    "detail": "; ".join(problems) if problems else
                    "リーク拒否・排他分岐・未参照holdout凍結・物理分離"})

    # 最終Projectionをデモンストレーションとして書き出す（決定論的）
    final = build_projections(store)
    (exp_dir / "projections.json").write_text(
        json.dumps(final, ensure_ascii=False, sort_keys=True, indent=1) + "\n",
        encoding="utf-8")

    gate_pass = (rebuild_rate == 1.0
                 and all(r["verdict"] == "PASS" for r in results))
    results.append({"case_id": "STEP7-METRICS",
                    "verdict": "PASS" if gate_pass else "FAIL",
                    "detail": f"Projection再構築率={rebuild_rate:.0%} "
                              f"一次記録={len(store.records())}件 "
                              f"修正前後ペア={len(final['repair_pairs'])}件 "
                              f"類似事例={len(hits)}件（助言専用）"})
    summary = {"pass": sum(1 for r in results if r["verdict"] == "PASS"),
               "fail": sum(1 for r in results if r["verdict"] == "FAIL"),
               "projection_rebuild_rate": round(rebuild_rate, 4)}
    return {"results": results, "summary": summary}
