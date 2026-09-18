"""Step 3評価ランナー: Raw Text Quality GateのShadow mode評価。

Gate（adaptation §3 Step 3）:
- Shadow modeでPrecision／Recall基準達成（P≥0.85・R≥0.90、所有3コードのmicro平均）
- 既存分類性能を悪化させない（3A分類CorpusがFAIL 0のまま）
- 出力findingが共通契約 finding.schema.json に適合する
Shadow mode: 本ランナーは既存パイプラインの判定へ一切影響しない（並行実行・記録のみ）。
"""
from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path

import yaml
from jsonschema import Draft202012Validator

from . import _ROOT  # noqa: F401
from .raw_text_gate import inspect  # noqa: E402
from .information_classifier import classify  # noqa: E402
from .runner3a import run_classification_corpus  # noqa: E402
from rimay_jp_core.lexicon import ROOT as RIMAY_ROOT  # noqa: E402


@lru_cache(maxsize=1)
def _finding_validator() -> Draft202012Validator:
    doc = json.loads((RIMAY_ROOT / "canonical" / "finding.schema.json")
                     .read_text(encoding="utf-8"))
    return Draft202012Validator({"$defs": doc["$defs"], "$ref": "#/$defs/finding"})


def run_rawtext_corpus(rt_dir: Path, cls_dir: Path) -> dict:
    results = []
    tp = fp = fn = 0
    shadow_log = []
    for p in sorted(rt_dir.glob("*.yaml")):
        case = yaml.safe_load(p.read_text(encoding="utf-8"))
        cid = case["case_id"]
        out = inspect(case["japanese"], "ja", cid)
        problems: list[str] = []

        # 共通finding契約への適合（全finding）
        for f in out["findings"]:
            errs = [e.message for e in _finding_validator().iter_errors(f)]
            if errs:
                problems.append(f"finding契約違反 {f['finding_id']}: {errs[0]}")

        predicted = {f["normalized_issue_code"] for f in out["findings"]}
        expected = set(case.get("expected_codes") or [])
        tp += len(predicted & expected)
        fp += len(predicted - expected)
        fn += len(expected - predicted)
        if predicted != expected:
            problems.append(f"検出差分: expected={sorted(expected)} got={sorted(predicted)}")

        # cross signal（他Validator所有スメルの照合ログ）
        cross_codes = {c["issue_code"] for c in out["cross_signals"]}
        for c in case.get("expected_cross_contains") or []:
            if c not in cross_codes:
                problems.append(f"期待cross未記録: {c}")

        shadow_log.append({
            "case_id": cid,
            "gate_findings": out["findings"],
            "cross_signals": out["cross_signals"],
            "reqsmell_raw_smells": out["raw_smells"],
            "classifier": classify(case["japanese"])["classification"],
        })
        results.append({"case_id": cid,
                        "verdict": "FAIL" if problems else "PASS",
                        "detail": "; ".join(problems) if problems
                        else (f"codes={sorted(predicted)}" if predicted else "clean")})

    precision = tp / (tp + fp) if (tp + fp) else 1.0
    recall = tp / (tp + fn) if (tp + fn) else 1.0

    # 非回帰: 既存3A分類Corpusが劣化しないこと（Shadowは本体へ無影響）
    cls = run_classification_corpus(cls_dir)["summary"]
    non_regression = cls["fail"] == 0

    gate_pass = precision >= 0.85 and recall >= 0.90 and non_regression \
        and all(r["verdict"] == "PASS" for r in results)
    results.append({
        "case_id": "RAWTEXT-METRICS",
        "verdict": "PASS" if gate_pass else "FAIL",
        "detail": f"P={precision:.0%} R={recall:.0%}（tp={tp} fp={fp} fn={fn}） "
                  f"3A非回帰={'OK' if non_regression else 'NG'}"
                  f"（classification {cls['pass']}/{cls['pass'] + cls['fail']}）",
    })
    summary = {
        "pass": sum(1 for r in results if r["verdict"] == "PASS"),
        "fail": sum(1 for r in results if r["verdict"] == "FAIL"),
        "precision": round(precision, 4), "recall": round(recall, 4),
        "shadow_log": shadow_log,
    }
    return {"results": results, "summary": summary}


def write_shadow_log(rt_dir: Path, cls_dir: Path, out_path: Path) -> dict:
    out = run_rawtext_corpus(rt_dir, cls_dir)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(
        {"mode": "shadow",
         "precision": out["summary"]["precision"],
         "recall": out["summary"]["recall"],
         "cases": out["summary"]["shadow_log"]},
        ensure_ascii=False, indent=2), encoding="utf-8")
    return out
