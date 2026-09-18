"""Runtime result models (in-memory only; never persisted — FR-029).

Implemented with stdlib dataclasses/enums for determinism and zero extra deps.
Every model provides ``to_dict()`` producing JSON-ready primitives for the MCP wire.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum


class Severity(str, Enum):
    """The only permitted severity values (FR-013)."""

    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class Language(str, Enum):
    EN = "en"
    JA = "ja"
    UNDETERMINED = "undetermined"


class SegmentKind(str, Enum):
    SCOPE = "scope"
    CONDITION = "condition"
    SYSTEM_RESPONSE = "system_response"
    WHOLE_REQUIREMENT = "whole_requirement"


class Verdict(str, Enum):
    PASS = "pass"
    FAIL = "fail"


class ArtifactType(str, Enum):
    """The six in-scope artifact types (FR-032/FR-045). requirement_set is out of scope."""

    FUNCTIONAL = "functional"
    ACCEPTANCE_CRITERIA = "acceptance_criteria"
    USER_STORY = "user_story"
    CONSTRAINT = "constraint"
    NON_FUNCTIONAL = "non_functional"
    GLOSSARY_TERM = "glossary_term"


class TypeResolution(str, Enum):
    """How an artifact's type was resolved (FR-033/FR-034)."""

    DECLARED = "declared"
    DETECTED = "detected"
    INDETERMINATE = "indeterminate"


class ShipStatus(str, Enum):
    """Whether a rule executes or is defined-but-deferred (FR-039/FR-040)."""

    SHIPPABLE = "shippable"
    DEFERRED = "deferred"


class GroundingStatus(str, Enum):
    GROUNDED = "grounded"
    PENDING_SOURCE = "pending_source"
    PARTIAL = "partial"


class SourceTier(str, Enum):
    PAPER = "paper"
    STANDARD = "standard"
    NOTATION = "notation"


class SourceRole(str, Enum):
    DEFINITION = "definition"
    METHOD = "method"


class UncheckedReason(str, Enum):
    """Why a source-defined smell was not evaluated (FR-044)."""

    DEFERRED_JUDGMENT = "deferred_judgment"
    PENDING_SOURCE = "pending_source"


@dataclass(frozen=True)
class UncheckedSmell:
    smell: str
    reason: UncheckedReason

    def to_dict(self) -> dict:
        return {"smell": self.smell, "reason": self.reason.value}


@dataclass(frozen=True)
class Coverage:
    """Per-result disclosure of checked vs unchecked smells (FR-044).

    Derived from the loaded asset (no runtime judgment) so it is byte-identical per
    knowledge version. ``checked`` lists smell ids actually evaluated (type catalog +
    general catalog); ``unchecked`` lists deferred/pending smells with a reason.
    """

    checked: tuple[str, ...] = ()
    unchecked: tuple[UncheckedSmell, ...] = ()

    def to_dict(self) -> dict:
        return {
            "checked": list(self.checked),
            "unchecked": [u.to_dict() for u in self.unchecked],
        }


@dataclass(frozen=True)
class Citation:
    document: str
    locator: str

    def to_dict(self) -> dict:
        return {"document": self.document, "locator": self.locator}


@dataclass(frozen=True)
class Location:
    """Where a finding occurs (FR-010): segment label + character span.

    ``segment`` is a ``SegmentKind`` (functional) or a plain string for the other types'
    schema slots (e.g. ``role``/``goal``/``benefit``, ``response_measure``) — the segment
    label set is defined by each artifact type's Layer 1 schema.
    """

    segment: SegmentKind | str
    start: int
    end: int
    text: str

    def to_dict(self) -> dict:
        seg = self.segment.value if isinstance(self.segment, Enum) else self.segment
        return {
            "segment": seg,
            "start": self.start,
            "end": self.end,
            "text": self.text,
        }


@dataclass(frozen=True)
class Finding:
    """One detected smell (FR-010, FR-012, FR-017).

    Multi-artifact fields are optional for now so the functional-only engine keeps working
    during migration: ``source_id`` (resolvable definition citation), ``catalog`` ('type' |
    'general'), and ``method_source_id`` (FR-040) are added as the engine adopts the source
    registry. ``citation`` is retained for backward compatibility.
    """

    smell: str
    smell_name: str
    quality_attribute: str
    location: Location
    severity: Severity
    explanation: str
    citation: Citation
    rule_id: str
    source_id: str | None = None
    catalog: str | None = None
    method_source_id: str | None = None

    def to_dict(self) -> dict:
        out: dict = {
            "smell": self.smell,
            "smell_name": self.smell_name,
            "quality_attribute": self.quality_attribute,
            "location": self.location.to_dict(),
            "severity": self.severity.value,
            "explanation": self.explanation,
            "citation": self.citation.to_dict(),
            "rule_id": self.rule_id,
        }
        if self.source_id is not None:
            out["source_id"] = self.source_id
        if self.catalog is not None:
            out["catalog"] = self.catalog
        if self.method_source_id is not None:
            out["method_source_id"] = self.method_source_id
        return out


@dataclass
class ValidationResult:
    language: Language
    verdict: Verdict
    analyzable: bool
    findings: list[Finding] = field(default_factory=list)
    notes: str | None = None
    # Multi-artifact fields (optional during migration):
    artifact_type: ArtifactType | None = None
    type_resolution: TypeResolution | None = None
    coverage: Coverage | None = None
    status_note: str | None = None

    def to_dict(self) -> dict:
        out: dict = {}
        if self.artifact_type is not None:
            out["artifact_type"] = self.artifact_type.value
        if self.type_resolution is not None:
            out["type_resolution"] = self.type_resolution.value
        out["language"] = self.language.value
        out["verdict"] = self.verdict.value
        out["analyzable"] = self.analyzable
        out["findings"] = [f.to_dict() for f in self.findings]
        if self.coverage is not None:
            out["coverage"] = self.coverage.to_dict()
        if self.notes is not None:
            out["notes"] = self.notes
        if self.status_note is not None:
            out["status_note"] = self.status_note
        return out


@dataclass
class BatchSummary:
    total: int
    passed: int
    failed: int
    by_smell: dict[str, int]
    by_type: dict[str, int] | None = None  # FR-014 (added with multi-artifact routing)

    def to_dict(self) -> dict:
        out: dict = {
            "total": self.total,
            "passed": self.passed,
            "failed": self.failed,
            "by_smell": dict(self.by_smell),
        }
        if self.by_type is not None:
            out["by_type"] = dict(self.by_type)
        return out


@dataclass
class BatchValidationResult:
    results: list[ValidationResult]
    summary: BatchSummary

    def to_dict(self) -> dict:
        return {
            "results": [r.to_dict() for r in self.results],
            "summary": self.summary.to_dict(),
        }
