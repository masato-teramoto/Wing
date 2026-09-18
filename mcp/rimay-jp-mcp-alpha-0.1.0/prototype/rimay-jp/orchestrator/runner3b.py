"""Phase 3B評価ランナー: 知識ルーティングのprecision/recallと機能成立条件を検査する。"""
import copy
import json
from pathlib import Path

import yaml

from . import _ROOT  # noqa: F401
from .candidate_extractor import extract  # noqa: E402
from .knowledge_router import route, routing_log, route_reproducible  # noqa: E402

# 評価対象の知識源種別（term_dictionaryは常時発生するため精度評価から除外し、ログのみ）
_SCORED = {"action_frame", "state_model", "business_rule", "nfr"}


def _actual_pairs(routes: list[dict]) -> set[tuple[str, str]]:
    pairs = set()
    for r in routes:
        if r["source"] not in _SCORED:
            continue
        if r["hits"]:
            for h in r["hits"]:
                pairs.add((r["source"], h.split(":", 1)[1]))
        else:
            pairs.add((r["source"], "UNRESOLVED"))
    return pairs


def run_case(path: Path) -> dict:
    case = yaml.safe_load(path.read_text(encoding="utf-8"))
    cid = case["case_id"]
    out = extract({"document_id": cid, "text": case["japanese"]}, f"REQ-{cid}")
    canonical = out["canonical"]
    if canonical is None:
        return {"case_id": cid, "verdict": "FAIL", "detail": "抽出でcanonicalが得られない"}

    before_status = {p: s["status"] for p, s in canonical["resolution"]["slots"].items()}

    if not route_reproducible(canonical):
        return {"case_id": cid, "verdict": "FAIL", "detail": "ルーティングが再現不能"}
    result = route(canonical)

    # 機能条件: routerはstatusを変更しない（confirmedへの昇格禁止）
    after_status = {p: canonical["resolution"]["slots"][p]["status"] for p in before_status}
    if before_status != after_status:
        return {"case_id": cid, "verdict": "FAIL",
                "detail": f"routerがstatusを変更: {before_status} -> {after_status}"}

    # 機能条件: 知識Provenanceは reference=<source>:<id>@<version> 形式
    prv = {p["id"]: p for p in canonical["provenance"]}
    for pid in result["provenance_added"]:
        ref = prv[pid].get("reference", "")
        if "@" not in ref or ":" not in ref:
            return {"case_id": cid, "verdict": "FAIL",
                    "detail": f"知識Provenanceに版数がない: {ref}"}

    expected = {(k, r) for k, r in (tuple(e) for e in case.get("expected_routes") or [])}
    actual = _actual_pairs(result["routes"])
    tp = expected & actual
    precision = len(tp) / len(actual) if actual else 1.0
    recall = len(tp) / len(expected) if expected else 1.0
    if precision < 1.0 or recall < 1.0:
        return {"case_id": cid, "verdict": "FAIL",
                "detail": f"P={precision:.2f} R={recall:.2f} "
                          f"expected={sorted(expected)} actual={sorted(actual)}"}

    exp_codes = set(case.get("expected_finding_codes") or [])
    got_codes = {f["code"] for f in result["findings"]}
    if exp_codes - got_codes:
        return {"case_id": cid, "verdict": "FAIL",
                "detail": f"期待finding未検出: {sorted(exp_codes - got_codes)}"}

    return {"case_id": cid, "verdict": "PASS",
            "detail": f"routes={sorted(actual)} P=1.00 R=1.00",
            "log": routing_log(canonical, result)}


def run_routing_corpus(routing_dir: Path) -> dict:
    results = [run_case(p) for p in sorted(routing_dir.glob("*.yaml"))]
    summary = {
        "pass": sum(1 for r in results if r["verdict"] == "PASS"),
        "fail": sum(1 for r in results if r["verdict"] == "FAIL"),
    }
    return {"results": results, "summary": summary}


def write_sample_log(routing_dir: Path, out_path: Path):
    """代表ケースのrouting logを成果物として出力する（knowledge-routing-log）。"""
    logs = [r["log"] for r in run_routing_corpus(routing_dir)["results"] if "log" in r]
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(logs, ensure_ascii=False, indent=2), encoding="utf-8")
