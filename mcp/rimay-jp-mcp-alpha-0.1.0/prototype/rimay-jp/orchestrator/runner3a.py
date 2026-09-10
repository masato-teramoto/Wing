"""Phase 3A評価ランナー: 情報分類精度と抽出の機能成立条件を検査する。"""
from pathlib import Path

import yaml

from . import _ROOT  # noqa: F401
from rimay_jp_core.schema_check import validate_schema  # noqa: E402
from .candidate_extractor import extract  # noqa: E402


def _check_extraction(case: dict, out: dict) -> list[str]:
    problems: list[str] = []
    canonical = out["canonical"]
    if canonical is None:
        return [f"canonicalが生成されていない（mode={out['extraction_mode']}）"]

    errs = validate_schema(canonical)
    if errs:
        problems.append(f"Schema違反: {errs}")
    slots = canonical["resolution"]["slots"]
    prv = {p["id"]: p for p in canonical["provenance"]}

    # 期待unknown（値なし＋unknown保持）
    for ptr in case.get("expected_unknowns") or []:
        s = slots.get(ptr)
        if not s or s["status"] != "unknown":
            problems.append(f"unknown期待が不成立: {ptr} -> {s}")
    # 期待proposed
    for ptr in case.get("expected_proposed") or []:
        s = slots.get(ptr)
        if not s or s["status"] != "proposed":
            problems.append(f"proposed期待が不成立: {ptr} -> {s}")
    # 複数候補
    for ptr, min_count in (case.get("expected_candidates") or {}).items():
        s = slots.get(ptr) or {}
        if len(s.get("candidates") or []) < min_count:
            problems.append(f"候補数不足: {ptr} -> {s.get('candidates')}")
    # source spanトレース: proposed/confirmedスロットはProvenanceのsource_spanへ遡れる
    for ptr, s in slots.items():
        if s["status"] in ("proposed", "confirmed") and s.get("provenance_refs"):
            for ref in s["provenance_refs"]:
                if ref not in prv or not prv[ref].get("source_span"):
                    problems.append(f"source spanトレース不可: {ptr} ({ref})")
    # segment参照の保持
    if not canonical["source"].get("source_segments"):
        problems.append("source_segmentsが記録されていない")
    # 誤自動確定の禁止: heuristic/synonym由来のconfirmedは存在してはならない
    for ptr, s in slots.items():
        if s["status"] == "confirmed":
            for ref in s.get("provenance_refs") or []:
                if prv[ref]["resolution_method"] in ("heuristic_candidate", "synonym_match"):
                    problems.append(f"誤自動確定: {ptr}（{prv[ref]['resolution_method']}）")
    return problems


def run_case(path: Path) -> dict:
    case = yaml.safe_load(path.read_text(encoding="utf-8"))
    cid = case["case_id"]
    out = extract(case["source_segment"], f"REQ-{cid}")

    if out["classification"] != case["expected_classification"]:
        return {"case_id": cid, "verdict": "FAIL",
                "detail": f"分類不一致: expected={case['expected_classification']} "
                          f"got={out['classification']}（{out['rationale']}）"}
    if case["expected_classification"] != "requirement_candidate":
        return {"case_id": cid, "verdict": "PASS",
                "detail": f"{out['classification']}（{out['rationale']}）"}

    if case.get("expected_extraction_mode") and \
            out["extraction_mode"] != case["expected_extraction_mode"]:
        return {"case_id": cid, "verdict": "FAIL",
                "detail": f"抽出モード不一致: expected={case['expected_extraction_mode']} "
                          f"got={out['extraction_mode']}"}
    problems = _check_extraction(case, out)
    if problems:
        return {"case_id": cid, "verdict": "FAIL", "detail": "; ".join(problems)}
    return {"case_id": cid, "verdict": "PASS",
            "detail": f"requirement_candidate（mode={out['extraction_mode']}）"}


def run_classification_corpus(cls_dir: Path) -> dict:
    results = [run_case(p) for p in sorted(cls_dir.glob("*.yaml"))]
    summary = {
        "pass": sum(1 for r in results if r["verdict"] == "PASS"),
        "fail": sum(1 for r in results if r["verdict"] == "FAIL"),
    }
    return {"results": results, "summary": summary}
