"""Per-type validation engine (T039).

Validates a single artifact of any of the six in-scope types against its catalog + the
cross-cutting general catalog, deterministically, and returns a coverage-scoped result
(FR-006/FR-010–FR-013/FR-039/FR-044). Runs ONLY shippable (deterministic) rules; judgment /
pending rules are disclosed via coverage but never executed. No persistence/logging of text.

Functional artifacts are handled by the legacy ``Engine`` (already grounded); this engine
covers the new types (acceptance_criteria, user_story, constraint, non_functional, glossary_term).
"""

from __future__ import annotations

from functools import lru_cache

from ..artifact_types.detection import resolve
from ..models import (
    ArtifactType,
    BatchSummary,
    BatchValidationResult,
    Citation,
    Coverage,
    Finding,
    Language,
    Location,
    Severity,
    TypeResolution,
    ValidationResult,
    Verdict,
)
from .coverage import build_coverage
from .detectors import REGISTRY, DetectionContext
from .language import analyzer_for
from .rule_loader_v2 import RuleV2, load_typed_rules
from .segmentation import segment_for

MAX_REQUIREMENT_CHARS = 10_000
MAX_BATCH = 1_000


@lru_cache(maxsize=8)
def _rules(artifact_type: str) -> tuple[RuleV2, ...]:
    return tuple(load_typed_rules(artifact_type))


def _finding(rule: RuleV2, hit) -> Finding:
    seg = hit.segment.value if hasattr(hit.segment, "value") else hit.segment
    explanation = rule.explanation_template.replace("{match}", hit.match or hit.text)
    return Finding(
        smell=rule.id,
        smell_name=rule.name,
        quality_attribute=rule.quality_attribute,
        location=Location(segment=seg, start=hit.start, end=hit.end, text=hit.text),
        severity=Severity(rule.default_severity),
        explanation=explanation,
        citation=Citation(document=rule.definition_source_id, locator=""),
        rule_id=rule.rule_id,
        source_id=rule.definition_source_id,
        catalog=rule.catalog,
        method_source_id=rule.method_source_id,
    )


def validate_typed(
    text: str,
    declared_type: str | None = None,
    language: str | None = None,
) -> ValidationResult:
    if text is None or not text.strip():
        return ValidationResult(Language.UNDETERMINED, Verdict.PASS, analyzable=False,
                                status_note="empty or whitespace-only input")
    if len(text) > MAX_REQUIREMENT_CHARS:
        return ValidationResult(Language.UNDETERMINED, Verdict.PASS, analyzable=False,
                                status_note=f"input exceeds {MAX_REQUIREMENT_CHARS} characters")

    at, resolution, lang = resolve(text, declared_type, language)
    if at is None:
        return ValidationResult(
            Language.UNDETERMINED if lang is Language.UNDETERMINED else lang,
            Verdict.PASS, analyzable=False, type_resolution=TypeResolution.INDETERMINATE,
            status_note="artifact type indeterminate",
        )

    analyzer = analyzer_for(lang)
    seg_analyzer = analyzer if at is ArtifactType.FUNCTIONAL else None
    # Segmentation is computed for location context / future segment-aware detectors.
    segment_for(at.value, text, seg_analyzer)

    rules = _rules(at.value)
    findings: list[Finding] = []
    checked: list[str] = []
    unchecked: list[tuple[str, str]] = []

    for rule in rules:
        if rule.language != lang.value:
            continue
        if not rule.ships:
            unchecked.append((rule.id, rule.defer_reason))
            continue
        checked.append(rule.id)
        ctx = DetectionContext(
            text=text, segments=[], analyzer=analyzer,
            params=dict(rule.detector_params), glossary=set(),
        )
        for hit in REGISTRY[rule.detector_type](ctx):
            findings.append(_finding(rule, hit))

    # Deterministic total order: (location.start, type-before-general, rule_id).
    findings.sort(key=lambda f: (f.location.start, 0 if f.catalog == "type" else 1, f.rule_id))

    coverage: Coverage = build_coverage(checked, unchecked)
    verdict = Verdict.FAIL if findings else Verdict.PASS
    return ValidationResult(
        language=lang, verdict=verdict, analyzable=True, findings=findings,
        artifact_type=at, type_resolution=resolution, coverage=coverage,
    )


def validate_batch_typed(
    texts: list[str],
    artifact_type: str | None = None,
    language: str | None = None,
) -> BatchValidationResult:
    """Validate a batch on the typed path (FR-007/FR-014/FR-021/FR-036).

    ``artifact_type=None`` ⇒ each item's type is detected independently (mixed-type batch).
    The summary reports passed/failed, occurrences per smell, and counts per artifact type.
    """
    if len(texts) > MAX_BATCH:
        raise ValueError(f"batch exceeds {MAX_BATCH} artifacts (LIMIT_EXCEEDED)")
    results = [validate_typed(t, artifact_type, language) for t in texts]
    by_smell: dict[str, int] = {}
    by_type: dict[str, int] = {}
    passed = failed = 0
    for r in results:
        at = r.artifact_type.value if r.artifact_type else "indeterminate"
        by_type[at] = by_type.get(at, 0) + 1
        if not r.analyzable:
            continue
        if r.verdict is Verdict.PASS:
            passed += 1
        else:
            failed += 1
        for f in r.findings:
            by_smell[f.smell] = by_smell.get(f.smell, 0) + 1
    summary = BatchSummary(total=len(texts), passed=passed, failed=failed,
                           by_smell=by_smell, by_type=by_type)
    return BatchValidationResult(results=results, summary=summary)
