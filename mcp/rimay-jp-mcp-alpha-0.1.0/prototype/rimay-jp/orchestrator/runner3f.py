"""Phase 3F評価ランナー: フィードバック還流のGATE-3F条件を検査する。

品質合格条件（レビューP1裁定）: 原因分類の正解を付与した準備済みケース
（10件以上）に対し、関連付け精度90%以上・regression Corpus化率80%以上。
実案件の指摘件数は評価条件にしない（運用実績指標として別掲）。
"""
import json
from pathlib import Path

import yaml

from . import _ROOT  # noqa: F401
from .feedback_handler import handle  # noqa: E402


def run_feedback_corpus(fb_dir: Path) -> dict:
    cases = [yaml.safe_load(p.read_text(encoding="utf-8"))
             for p in sorted(fb_dir.glob("*.yaml"))]
    results = []
    correct = 0
    regression_ok = 0
    causes_seen = set()
    for case in cases:
        out = handle(case)
        problems = []
        causes_seen.add(out["cause"])
        # 関連付け精度: 原因分類と関連付け先種別の双方一致
        target_kinds = {t["kind"] for t in out["targets"]}
        hit = (out["cause"] == case["expected_cause"]
               and case["expected_target_kind"] in target_kinds)
        if hit:
            correct += 1
        else:
            problems.append(f"分類不一致: expected=({case['expected_cause']},"
                            f"{case['expected_target_kind']}) got=({out['cause']},"
                            f"{sorted(target_kinds)})")
        # 関連付け先の参照が具体的であること
        for t in out["targets"]:
            if not t.get("reference"):
                problems.append(f"target参照なし: {t}")
        # regression Corpus化
        has_reg = out["regression_candidate"] is not None
        if has_reg:
            regression_ok += 1
            rc = out["regression_candidate"]
            if not rc.get("proposal") or not rc.get("kind"):
                problems.append(f"regression候補が不完全: {rc}")
        if case["expected_regression"] != has_reg:
            problems.append(f"regression期待不一致: expected="
                            f"{case['expected_regression']} got={has_reg}")
        results.append({"case_id": case["case_id"],
                        "verdict": "FAIL" if problems else "PASS",
                        "detail": "; ".join(problems) if problems
                        else f"{out['cause']} -> {sorted(target_kinds)}"
                             + ("+regression" if has_reg else ""),
                        "mapping": out})

    n = len(cases)
    accuracy = correct / n if n else 0.0
    reg_rate = regression_ok / n if n else 0.0
    gate = {
        "cases": n,
        "mapping_accuracy": round(accuracy, 3),
        "regression_rate": round(reg_rate, 3),
        "distinct_causes": sorted(causes_seen),
        "quality_pass": n >= 10 and accuracy >= 0.90 and reg_rate >= 0.80
                        and len(causes_seen - {"unmapped"}) >= 4,
    }
    results.append({
        "case_id": "GATE-3F-METRICS",
        "verdict": "PASS" if gate["quality_pass"] else "FAIL",
        "detail": f"n={n} 関連付け精度={accuracy:.0%} regression化率={reg_rate:.0%} "
                  f"原因分類={len(causes_seen - {'unmapped'})}種",
    })
    summary = {
        "pass": sum(1 for r in results if r["verdict"] == "PASS"),
        "fail": sum(1 for r in results if r["verdict"] == "FAIL"),
        "gate": gate,
    }
    return {"results": results, "summary": summary}


def write_artifacts(fb_dir: Path, reg_dir: Path, reports_dir: Path):
    """regression追加候補・改善Backlog・マッピングログを成果物として出力する。"""
    out = run_feedback_corpus(fb_dir)
    reg_dir.mkdir(parents=True, exist_ok=True)
    reports_dir.mkdir(parents=True, exist_ok=True)
    backlog = []
    mappings = []
    for r in out["results"]:
        m = r.get("mapping")
        if not m:
            continue
        mappings.append(m)
        rc = m["regression_candidate"]
        if rc:
            (reg_dir / f"{rc['case_id']}.yaml").write_text(
                yaml.safe_dump(rc, allow_unicode=True, sort_keys=False),
                encoding="utf-8")
        if m["backlog_entry"]:
            backlog.append(m["backlog_entry"])
    (reports_dir / "knowledge-improvement-backlog.yaml").write_text(
        yaml.safe_dump({"backlog": backlog}, allow_unicode=True, sort_keys=False),
        encoding="utf-8")
    (reports_dir / "feedback-mapping-log.json").write_text(
        json.dumps(mappings, ensure_ascii=False, indent=2), encoding="utf-8")
    return out
