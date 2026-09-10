"""Phase 3D評価ランナー: 多層検証・失敗分類・修正候補のGATE-3D条件を検査する。"""
from pathlib import Path

import yaml

from . import _ROOT  # noqa: F401
from .candidate_extractor import extract  # noqa: E402
from .validation_router import validate_all  # noqa: E402


def sweep_development(dev_dir: Path) -> dict:
    """development正例24件で GATE-3D の維持条件（Parser/等価/sidecar/JP往復）を検査。"""
    total = ok = 0
    failures = []
    for p in sorted(dev_dir.glob("*.yaml")):
        case = yaml.safe_load(p.read_text(encoding="utf-8"))
        if case.get("expected_result") != "accept":
            continue
        total += 1
        out = extract({"document_id": case["case_id"], "text": case["japanese"]},
                      f"REQ-{case['case_id']}")
        res = validate_all(out["canonical"])
        if res["blocked"] or not res["artifacts"] or not res["jp_roundtrip_ok"]:
            failures.append((case["case_id"],
                             [f["code"] for f in res["findings"]],
                             res["jp_roundtrip_ok"]))
        else:
            ok += 1
    return {"total": total, "ok": ok, "failures": failures}


def run_case(path: Path) -> dict:
    case = yaml.safe_load(path.read_text(encoding="utf-8"))
    cid = case["case_id"]
    out = extract({"document_id": cid, "text": case["japanese"]}, f"REQ-{cid}")
    if out["canonical"] is None:
        return {"case_id": cid, "verdict": "FAIL", "detail": "抽出失敗"}
    res = validate_all(out["canonical"])
    codes = {f["code"] for f in res["findings"]}
    problems = []

    exp_codes = set(case.get("expected_codes") or [])
    if exp_codes - codes:
        problems.append(f"期待コード未検出: {sorted(exp_codes - codes)} got={sorted(codes)}")

    if case.get("expected_blocked") is not None and res["blocked"] != case["expected_blocked"]:
        problems.append(f"blocked: expected={case['expected_blocked']} got={res['blocked']}")

    # 失敗分類（日本語側・知識側・Rimay側・拡張情報側）
    for group, code_list in (case.get("expected_classification") or {}).items():
        for c in code_list:
            if c not in res["classification"].get(group, []):
                problems.append(f"分類不一致: {c} が {group} にない "
                                f"（{res['classification']}）")

    # 根拠付き修正候補
    fx = case.get("expected_fix")
    if fx:
        target = next((f for f in res["findings"] if f["code"] == fx["code"]), None)
        if not target:
            problems.append(f"修正候補対象のfindingがない: {fx['code']}")
        else:
            cands = target.get("fix_candidates") or []
            if fx.get("min_candidates", 0) > len(cands):
                problems.append(f"修正候補不足: {len(cands)}件")
            for c in cands:
                if c.get("status") != "proposed" or not c.get("source"):
                    problems.append(f"候補が根拠付きproposedでない: {c}")
            if fx.get("source_prefix") and cands and \
                    not all(c["source"].startswith(fx["source_prefix"]) for c in cands):
                problems.append(f"候補sourceが{fx['source_prefix']}でない")

    # 確認事項（clarification）
    if case.get("expected_clarification_code"):
        target = next((f for f in res["findings"]
                       if f["code"] == case["expected_clarification_code"]), None)
        if not target or not target.get("clarification"):
            problems.append(f"確認事項がない: {case['expected_clarification_code']}")

    if problems:
        return {"case_id": cid, "verdict": "FAIL", "detail": "; ".join(problems)}
    return {"case_id": cid, "verdict": "PASS",
            "detail": f"codes={sorted(codes)} blocked={res['blocked']}"}


def run_validation_corpus(val_dir: Path, dev_dir: Path) -> dict:
    results = [run_case(p) for p in sorted(val_dir.glob("*.yaml"))]
    sweep = sweep_development(dev_dir)
    ok = sweep["ok"] == sweep["total"] and sweep["total"] > 0
    results.append({
        "case_id": "DEV-SWEEP",
        "verdict": "PASS" if ok else "FAIL",
        "detail": f"{sweep['ok']}/{sweep['total']} 正例がrender+parse+等価+sidecar+JP往復を通過"
                  + (f"; failures={sweep['failures']}" if sweep["failures"] else ""),
    })
    summary = {
        "pass": sum(1 for r in results if r["verdict"] == "PASS"),
        "fail": sum(1 for r in results if r["verdict"] == "FAIL"),
    }
    return {"results": results, "summary": summary}
