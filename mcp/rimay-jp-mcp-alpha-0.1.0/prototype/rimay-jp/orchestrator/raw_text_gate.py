"""raw-text-quality-gate: 表層スメルのRaw Text検査（Step 3、Shadow mode）。

- validator-registryどおり、本ゲートが所有するのは表層3スメル
  （INCORRECT_SEGMENT_ORDER／PASSIVE_VOICE／COORDINATION_AMBIGUITY）のみ。
  Canonical段のスメル（incomplete_*・non_atomic）はStep 4の責務であり除外する。
  not_a_requirement／not_precise_verb はそれぞれclassifier／extractorの所有で、
  照合用のcross signalとしてログにのみ記録する。
- **非排除ゲート**（ADR-0012 D5）: rejectせず、findingごとに
  normalize（Serializer再生成）／clarify（質問）／split（分割提案）を推奨する。
- 出力findingは共通契約 finding.schema.json に適合する
  （normalized_issue_code・quality_labels・source_span・候補target_paths・citation）。
"""
from __future__ import annotations

import sys
from functools import lru_cache
from pathlib import Path

import yaml

_RIMAY = Path(__file__).resolve().parents[1]
for p in (str(_RIMAY / "quality" / "src"),):
    if p not in sys.path:
        sys.path.insert(0, p)

from reqsmell.layer2.engine import Engine  # noqa: E402

# 所有スメル → (normalized_issue_code, 推奨アクション)
# non_atomicはADR-0013でCanonical段からPre-Canonical診断へ移管
# （自由文の複数動作＝分割候補。Canonical段は日本語を再解析しない）
_OWNED = {
    "incorrect_order_requirement": ("INCORRECT_SEGMENT_ORDER", "normalize"),
    "passive_voice": ("PASSIVE_VOICE", "clarify"),
    "coordination_ambiguity": ("COORDINATION_AMBIGUITY", "split"),
    "non_atomic_requirement": ("MULTIPLE_PRIMARY_ACTIONS", "split"),
}
# cross signal（他Validator所有。照合ログ専用）
_CROSS = {
    "not_a_requirement": "NOT_A_REQUIREMENT",
    "not_precise_verb": "IMPRECISE_ACTION_VERB",
}


@lru_cache(maxsize=1)
def _engine() -> Engine:
    return Engine()


@lru_cache(maxsize=1)
def _issue_catalog() -> dict:
    doc = yaml.safe_load((_RIMAY / "canonical" / "issue-code-catalog.yaml")
                         .read_text(encoding="utf-8"))
    return {e["code"]: e for e in doc["issue_codes"]}


def _target_paths(smell: str, segment: str) -> list[str]:
    """根因の候補CanonicalPointer（span直結ではなく候補として返す）。"""
    if smell == "passive_voice":
        if segment == "condition":
            return ["/rimay_core/conditions/0/event/actor"]
        return ["/rimay_core/response/actor"]
    if smell == "coordination_ambiguity":
        return ["/rimay_core/conditions/0"]
    return []  # incorrect_order: 文全体（Serializer再生成で決定論的に修復）


def inspect(text: str, language: str = "ja", case_id: str = "RT") -> dict:
    """戻り値: {findings（所有3コード・共通契約）, cross_signals, raw_smells}。"""
    result = _engine().validate(text, language)
    findings: list[dict] = []
    cross: list[dict] = []
    raw: list[str] = []
    for i, f in enumerate(result.findings, start=1):
        raw.append(f.smell)
        if f.smell in _CROSS:
            cross.append({"smell": f.smell, "issue_code": _CROSS[f.smell],
                          "owner_hint": "information-classifier"
                          if f.smell == "not_a_requirement" else "candidate-extractor"})
            continue
        if f.smell not in _OWNED:
            continue  # incomplete_*等はCanonical段のコアValidatorの責務（二重判定防止）
        code, _action = _OWNED[f.smell]
        cat = _issue_catalog()[code]
        findings.append({
            "finding_id": f"FND-{case_id}-{i:02d}",
            "validator_id": "raw-text-quality-gate",
            "source_rule_id": f.rule_id,
            "normalized_issue_code": code,
            "quality_labels": [f.smell, f.quality_attribute],
            "severity": f.severity.value,
            # §6合意（2026-08-04）: raw_text段は恒久Advisory（非排除ゲート）。
            # findingは分類見直し・並べ替え・質問・分割を起動するのみで遮断しない。
            "blocking": False,
            "target_paths": _target_paths(f.smell, str(f.location.to_dict()["segment"])),
            "source_span": {"start": f.location.start, "end": f.location.end,
                            "text": f.location.text},
            "message": f.explanation,
            "citation": {"source": f.citation.document, "locator": f.citation.locator},
            "repair_disposition": cat["repair_disposition"],
            "status": "open",
            # 非排除ゲート: 起動アクションはrepair_dispositionが示す
            # （AUTO_SURFACE_REWRITE=normalize / ASK_USER=clarify / PROPOSE_SPLIT=split）
        })
    return {"findings": findings, "cross_signals": cross, "raw_smells": raw}
