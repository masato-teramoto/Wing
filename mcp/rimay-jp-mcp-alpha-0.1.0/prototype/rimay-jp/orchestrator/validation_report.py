"""finding正規化・重複排除・Validation Report生成（Step 4、ADR-0012 D6）。

- legacy finding（finding-code-catalog 29コード）を normalized_issue_code へ正規化する。
  JP-OMISSION等の多義コードはtarget_pathで曖昧性を解決する。
- **本モジュールは日本語文字列を解析しない**（ADR-0013: 日本語解析はNormalizerに
  集約。表層スメル診断はFree-text Import段=raw_text_gateの責務であり、
  Canonical段の検査入力はCanonicalとsurface_analysisのみ）。
- 重複排除: (normalized_issue_code × target_path) をキーに、issueカタログの
  owner_validatorのfindingを主とし、他検出はevidence.corroborated_byへ併合する。
- Validation Reportはrevision紐付きの正本。Canonical本体にはvalidation_state要約のみ
  （移行契約Phase B: findings[]への新規書き込みは停止）。
"""
from __future__ import annotations

from functools import lru_cache
from pathlib import Path

import yaml

_RIMAY = Path(__file__).resolve().parents[1]

from rimay_jp_core.model import canonical_hash  # noqa: E402

REGISTRY_VERSION = "0.3.0"  # 0.3.0: terminology所有コード拡張（ADR-0014 D4）
_SEV = {"error": "high", "warning": "medium", "info": "low"}
_SEV_ORDER = {"high": 2, "medium": 1, "low": 0}

_STATIC_MAP = {
    "JP-MODAL": "MISSING_MODALITY",
    "JP-LEXICAL": "UNREGISTERED_TERM",
    "JP-CASE": "INCORRECT_SEGMENT_ORDER",
    "JP-COORD": "COORDINATION_AMBIGUITY",
    "QUALITY-AMBIGUOUS": "AMBIGUOUS_TIME_EXPRESSION",
    "QUALITY-DEICTIC": "DEICTIC_REFERENCE",
    "DOMAIN": "STATE_VALUE_OUT_OF_MODEL",
    "PROFILE-OUT": "UNSUPPORTED_CONSTRUCT",
    "RIMAY-ACTION": "UNSUPPORTED_CONSTRUCT",
    "RIMAY-MODAL": "UNSUPPORTED_CONSTRUCT",
    "RIMAY-ROLE": "INCOMPLETE_TRIGGER_EVENT",
    "RIMAY-CONSTRAINT": "EXTENSION_LOSS",
    "AST-EQUIVALENCE": "SEMANTIC_PROJECTION_MISMATCH",
    "SIDECAR-LOSS": "EXTENSION_LOSS",
    "SIDECAR-STALE": "EXTENSION_LOSS",
    "KNOWLEDGE-ROUTE": "KNOWLEDGE_GAP",
    "KNOWLEDGE-CONFLICT": "KNOWLEDGE_GAP",
    # ADR-0014: 語彙形成ループ（コアfinding名と正規化Issue名を一致させる）
    "TERM_APPROVAL_PENDING": "TERM_APPROVAL_PENDING",
    "AMBIGUOUS_TERM": "AMBIGUOUS_TERM",
    "DEPRECATED_TERM": "DEPRECATED_TERM",
}


@lru_cache(maxsize=1)
def _catalog() -> dict:
    doc = yaml.safe_load((_RIMAY / "canonical" / "issue-code-catalog.yaml")
                         .read_text(encoding="utf-8"))
    return {e["code"]: e for e in doc["issue_codes"]}


@lru_cache(maxsize=1)
def _rollout() -> dict:
    """切替計画のSSOT（issue-code-catalog rollout。§6合意 2026-08-04）。"""
    doc = yaml.safe_load((_RIMAY / "canonical" / "issue-code-catalog.yaml")
                         .read_text(encoding="utf-8"))
    return doc.get("rollout") or {"mode": "advisory", "blocking_issue_codes": []}


def is_blocking_by_policy(code: str) -> bool:
    r = _rollout()
    return r["mode"] == "blocking" and code in r["blocking_issue_codes"]


def issue_code_for(legacy_code: str, path: str | None) -> str:
    """legacyコード→issue code（JP-OMISSIONはtarget_pathで曖昧性を解決する）。"""
    if legacy_code == "JP-OMISSION":
        p = path or ""
        expression_leaf = p.startswith("/rimay_core/response_expression/")
        block_leaf = p.startswith("/rimay_core/response_block/items/")
        if p == "/rimay_core/response/actor" or (
                (expression_leaf or block_leaf) and p.endswith("/response/actor")):
            return "MISSING_RESPONSE_ACTOR"
        if "/event/actor" in p:
            return "MISSING_CONDITION_ACTOR"
        if p == "/rimay_core/response/modality" or (
                (expression_leaf or block_leaf) and p.endswith("/response/modality")):
            return "MISSING_MODALITY"
        return "MISSING_REQUIRED_ROLE"
    return _STATIC_MAP.get(legacy_code, "UNCLASSIFIED")


def _rule_id(legacy: dict, code: str) -> str:
    """Rule追跡: 格フレーム由来は <frame>.required_<role> 形式（レビュー§6.3例と同形）。"""
    ev = legacy.get("evidence") or {}
    if ev.get("case_frame") and ev.get("required_role"):
        return f"{ev['case_frame']}.required_{ev['required_role']}"
    owner = _catalog()[code]["owner_validator"]
    return f"{owner}#{legacy['code']}"


def normalize_findings(legacy_findings: list[dict], requirement_id: str) -> list[dict]:
    out = []
    for i, f in enumerate(legacy_findings, start=1):
        code = issue_code_for(f["code"], f.get("path"))
        cat = _catalog()[code]
        common = {
            "finding_id": f"FND-{requirement_id}-{i:03d}",
            "validator_id": cat["owner_validator"],
            "source_rule_id": _rule_id(f, code),
            "normalized_issue_code": code,
            "legacy_code": f["code"],
            "quality_labels": list(cat.get("quality_labels") or []),
            "severity": _SEV[f["severity"]],
            "blocking": bool(f["blocking"]),
            "target_paths": [f["path"]] if f.get("path") else [],
            "message": f["message"],
            "repair_disposition": cat["repair_disposition"],
            "status": "open",
        }
        if f.get("evidence"):
            common["evidence"] = dict(f["evidence"])
        if f.get("fix_candidates"):
            common["fix_candidates"] = f["fix_candidates"]
        if f.get("clarification"):
            common["clarification"] = f["clarification"]
        out.append(common)
    return out


def dedup(findings: list[dict], corroborations: list[dict] | None = None) -> list[dict]:
    """(issue code × target_path) で統合。owner_validatorのfindingを主とする。"""
    merged: dict[tuple, dict] = {}
    for f in findings:
        key = (f["normalized_issue_code"],
               f["target_paths"][0] if f.get("target_paths") else "")
        if key not in merged:
            merged[key] = f
            continue
        primary = merged[key]
        owner = _catalog()[f["normalized_issue_code"]]["owner_validator"]
        if f["validator_id"] == owner and primary["validator_id"] != owner:
            primary, f = f, primary
            merged[key] = primary
        ev = primary.setdefault("evidence", {})
        ev.setdefault("corroborated_by", []).append(
            {"validator_id": f["validator_id"], "source_rule_id": f["source_rule_id"]})
        if _SEV_ORDER[f["severity"]] > _SEV_ORDER[primary["severity"]]:
            primary["severity"] = f["severity"]
        primary["blocking"] = primary["blocking"] or f["blocking"]
        primary["quality_labels"] = sorted(set(primary["quality_labels"])
                                           | set(f["quality_labels"]))
    out = list(merged.values())
    # reqsmell incomplete_*系は同種issueのcorroborationとして併合する
    for c in corroborations or []:
        for f in out:
            if f["normalized_issue_code"] in c["codes"]:
                f.setdefault("evidence", {}).setdefault("corroborated_by", []).append(
                    {"validator_id": "requirement-quality-core",
                     "source_rule_id": c["rule_id"]})
    return out


def build_report(canonical: dict, common_findings: list[dict], *,
                 vocabulary_context=None, vocab=None) -> tuple[dict, dict]:
    """Validation Report（正本）とvalidation_state（Canonical要約）を生成する。"""
    chash = canonical_hash(canonical)
    # engine/knowledge版は固定文字列でなく実体から取得する（ADR-0013 D3）。
    # requirement-quality-coreの実行行は削除（Canonical段で実行しない=D1）。
    from rimay_jp_core import __version__ as engine_version
    from rimay_jp_core.lexicon import versions
    from rimay_jp_core.vocabulary import (active_vocabulary_context,
                                          effective_terms)
    ver = versions()
    context = vocabulary_context or active_vocabulary_context()
    effective_vocab = (list(vocab) if vocab is not None else
                       (list(effective_terms(context)) if context is not None else None))
    report = {
        "report_id": f"VR-{canonical['requirement_id']}-{canonical['revision']}",
        "requirement_id": canonical["requirement_id"],
        "canonical_revision": canonical["revision"],
        "canonical_hash": chash,
        "profile_version": canonical["profile_version"],
        "profile_content_hash": ver["profile_content_hash"],
        "validator_registry_version": REGISTRY_VERSION,
        "executions": [
            {"validator_id": "rimay-jp-core", "engine_version": engine_version,
             "knowledge_version": ver["domain_knowledge"]},
        ],
        "findings": common_findings,
    }
    state = {
        "report_id": report["report_id"],
        "blocking_findings": sum(1 for f in common_findings if f["blocking"]),
        "warning_findings": sum(1 for f in common_findings if not f["blocking"]),
        "validated_canonical_hash": chash,
        "validator_registry_version": REGISTRY_VERSION,
        # ADR-0014 D5: 検査時点の語彙Snapshotを固定（再現性=Gate 9）
        "validated_vocabulary_snapshot": ver["vocabulary_snapshot_id"],
        "validated_vocabulary_hash": ver["vocabulary_content_hash"],
        # Gate 6: STALEは参照用語の実体指紋で判定（無関係な公開で古くならない）
        "validated_term_fingerprint": _term_fp(canonical, effective_vocab),
    }
    if context is not None:
        public_context = context.public()
        report["vocabulary_context"] = public_context
        # 0.x reader用の単一fieldは案件Snapshotへの互換projectionとして維持する。
        state["validated_vocabulary_snapshot"] = context.project.snapshot_id
        state["validated_vocabulary_hash"] = context.project.content_hash
    return report, state


def _term_fp(canonical: dict, vocab=None) -> str:
    from rimay_jp_core.lexicon import terms
    from .terminology import term_fingerprint
    return term_fingerprint(canonical, vocab if vocab is not None else terms())


def validation_is_stale(canonical: dict, current_vocab=None,
                        vocabulary_context=None,
                        validation_report: dict | None = None) -> bool:
    """validation_stateが現Canonical・現語彙と不整合（STALE）か。

    Report不在は未検査=stale扱い。語彙依存はADR-0014 D5/Gate 6:
    **参照している用語の実体指紋**が現行語彙で変わった場合のみSTALE
    （無関係な新語追加・Snapshot切替だけでは古くならない。
    旧stateに指紋記録がない場合はcanonical hashのみ=後方互換）。
    current_vocabは語彙リストの外部注入（試験・影響シミュレーション用）。
    """
    state = canonical.get("validation_state")
    if not state:
        return True
    if state["validated_canonical_hash"] != canonical_hash(canonical):
        return True
    recorded_context = ((validation_report or {}).get("vocabulary_context") or
                        state.get("validated_vocabulary_context"))
    if recorded_context is not None:
        from rimay_jp_core.vocabulary import (active_vocabulary_context,
                                              effective_terms)
        context = vocabulary_context or active_vocabulary_context()
        if context is None and current_vocab is None:
            return True
        if context is not None:
            if context.project_id != recorded_context.get("project_id"):
                return True
            if current_vocab is None:
                current_vocab = list(effective_terms(context))
    elif vocabulary_context is not None and current_vocab is None:
        from rimay_jp_core.vocabulary import effective_terms
        current_vocab = list(effective_terms(vocabulary_context))
    if "validated_term_fingerprint" in state:
        if state["validated_term_fingerprint"] != \
                _term_fp(canonical, current_vocab):
            return True
    return False


def read_findings(canonical: dict, report: dict | None = None) -> list[dict]:
    """検査結果の読み取り（移行契約Phase B、2026-08-04移行）。

    正本はValidation Report。Reportが与えられればそれを読み、無い場合
    （validation_state以前の旧Canonical）のみ legacy findings[] へ
    フォールバックする。新規書き込みはReportのみ（findings[]への書き込みは停止）。
    """
    if report is not None:
        return report["findings"]
    return list(canonical.get("findings") or [])
