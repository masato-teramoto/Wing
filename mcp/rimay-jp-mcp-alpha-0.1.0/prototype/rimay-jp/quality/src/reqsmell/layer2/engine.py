"""Validation engine (T033, T038).

Applies every language-matching rule to a requirement, assembles findings from rule
metadata + detector hits, and returns deterministic results. No persistence, no logging
of requirement text (FR-029/FR-030).
"""

from __future__ import annotations

from ..knowledge_io import knowledge_dir, load_yaml
from ..models import (
    BatchSummary,
    BatchValidationResult,
    Citation,
    Finding,
    Language,
    Location,
    SegmentKind,
    Severity,
    ValidationResult,
    Verdict,
)
from .detectors import REGISTRY, DetectionContext
from .language import analyzer_for, detect_language
from .rule_loader import Rule, load_rules
from .segmentation import segment

MAX_REQUIREMENT_CHARS = 10_000
MAX_BATCH = 1_000


class Engine:
    def __init__(self) -> None:
        self._rules: list[Rule] = load_rules()
        catalog = load_yaml(knowledge_dir() / "layer2" / "catalog.yaml")
        self._catalog_index = {s["id"]: i for i, s in enumerate(catalog["smells"])}
        self._smell_name = {s["id"]: s["name"] for s in catalog["smells"]}

    # ---- single ----------------------------------------------------------------
    def validate(self, requirement: str, language: str | None = None) -> ValidationResult:
        if requirement is None or not requirement.strip():
            return ValidationResult(Language.UNDETERMINED, Verdict.PASS, analyzable=False,
                                    notes="empty or whitespace-only input")
        if len(requirement) > MAX_REQUIREMENT_CHARS:
            return ValidationResult(Language.UNDETERMINED, Verdict.PASS, analyzable=False,
                                    notes=f"input exceeds {MAX_REQUIREMENT_CHARS} characters")

        lang = detect_language(requirement, language)
        analyzer = analyzer_for(lang)
        if analyzer is None:
            return ValidationResult(Language.UNDETERMINED, Verdict.PASS, analyzable=False,
                                    notes="language could not be determined")

        segments = segment(requirement, analyzer)
        findings: list[Finding] = []
        for rule in self._rules:
            if rule.language != lang.value:
                continue
            ctx = DetectionContext(
                text=requirement, segments=segments, analyzer=analyzer,
                params=rule.detector_params, glossary=rule.glossary,
            )
            for hit in REGISTRY[rule.detector_type](ctx):
                findings.append(self._make_finding(rule, hit))

        findings = self._order(findings)
        verdict = Verdict.FAIL if findings else Verdict.PASS
        return ValidationResult(lang, verdict, analyzable=True, findings=findings)

    # ---- batch -----------------------------------------------------------------
    def validate_batch(self, requirements: list[str], language: str | None = None) -> BatchValidationResult:
        if len(requirements) > MAX_BATCH:
            raise ValueError(f"batch exceeds {MAX_BATCH} requirements")
        results = [self.validate(r, language) for r in requirements]
        passed = sum(1 for r in results if r.analyzable and r.verdict == Verdict.PASS)
        failed = sum(1 for r in results if r.analyzable and r.verdict == Verdict.FAIL)
        by_smell: dict[str, int] = {}
        for r in results:
            for f in r.findings:
                by_smell[f.smell] = by_smell.get(f.smell, 0) + 1
        summary = BatchSummary(total=len(results), passed=passed, failed=failed,
                               by_smell=dict(sorted(by_smell.items())))
        return BatchValidationResult(results=results, summary=summary)

    # ---- helpers ---------------------------------------------------------------
    def _make_finding(self, rule: Rule, hit) -> Finding:
        explanation = rule.explanation_template.format(match=hit.match or hit.text)
        return Finding(
            smell=rule.id,
            smell_name=rule.name,
            quality_attribute=rule.quality_attribute,
            location=Location(SegmentKind(hit.segment), hit.start, hit.end, hit.text),
            severity=Severity(rule.default_severity),
            explanation=explanation,
            citation=Citation(rule.citation["document"], rule.citation["locator"]),
            rule_id=rule.rule_id,
        )

    def _order(self, findings: list[Finding]) -> list[Finding]:
        """Stable, total order: by start offset, then catalog order, then rule id (FR-015)."""
        return sorted(
            findings,
            key=lambda f: (f.location.start, self._catalog_index.get(f.smell, 999), f.rule_id),
        )
