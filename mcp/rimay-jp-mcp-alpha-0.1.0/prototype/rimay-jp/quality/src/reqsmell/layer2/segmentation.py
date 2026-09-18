"""Requirement segmentation (T024).

Splits a requirement into ordered segments (scope / condition / system_response /
unclassified) using the paper's keyword + information-content method (Table 7),
implemented deterministically via the language Analyzer.
"""

from __future__ import annotations

import re
from dataclasses import dataclass

from ..models import SegmentKind
from ..nlp.base import Analyzer

# Clause boundaries: comma (EN/JA), semicolon, the word "then", and newlines.
_SPLIT_RE = re.compile(r"(,|、|;|；|\n|\bthen\b)", re.IGNORECASE)


@dataclass(frozen=True)
class Segment:
    kind: SegmentKind
    text: str
    start: int
    end: int


def _clause_spans(text: str) -> list[tuple[str, int, int]]:
    spans: list[tuple[str, int, int]] = []
    pos = 0
    for m in _SPLIT_RE.finditer(text):
        chunk = text[pos : m.start()]
        if chunk.strip():
            spans.append((chunk, pos, m.start()))
        pos = m.end()
    tail = text[pos:]
    if tail.strip():
        spans.append((tail, pos, len(text)))
    return spans


def segment(text: str, analyzer: Analyzer) -> list[Segment]:
    """Return ordered segments with character offsets into ``text``."""
    segments: list[Segment] = []
    for chunk, start, end in _clause_spans(text):
        clause = chunk.strip()
        # tighten offsets to the stripped clause
        lead = len(chunk) - len(chunk.lstrip())
        c_start = start + lead
        c_end = c_start + len(clause)

        if analyzer.is_scope_clause(clause):
            kind = SegmentKind.SCOPE
        elif analyzer.is_condition_clause(clause):
            kind = SegmentKind.CONDITION
        elif analyzer.has_modal(clause):
            kind = SegmentKind.SYSTEM_RESPONSE
        else:
            kind = None

        if kind is not None:
            segments.append(Segment(kind, clause, c_start, c_end))
        else:
            # Keep unclassified clauses too (needed for not-a-requirement detection),
            # tagged as whole_requirement-level leftovers.
            segments.append(Segment(SegmentKind.WHOLE_REQUIREMENT, clause, c_start, c_end))
    return segments


def by_kind(segments: list[Segment], kind: SegmentKind) -> list[Segment]:
    return [s for s in segments if s.kind == kind]


# ---------------------------------------------------------------------------
# Per-type segmentation (T035) — deterministic splitters for the six in-scope
# artifact types' Layer 1 segment schemas. Labels are plain strings matching each
# type's schema slots. Functional reuses the legacy segment() splitter above.
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class TypedSegment:
    label: str
    text: str
    start: int
    end: int


def _span(label: str, text: str, start: int, end: int) -> TypedSegment:
    return TypedSegment(label, text[start:end].strip(), start, end)


def _whole(label: str, text: str) -> list[TypedSegment]:
    return [TypedSegment(label, text.strip(), 0, len(text))]


_US_ROLE = re.compile(r"\bas\s+an?\b", re.IGNORECASE)
_US_MEANS = re.compile(r"\bi\s+(?:want|need|would\s+like|wish|can)\b", re.IGNORECASE)
_US_BENEFIT = re.compile(r"\bso\s+that\b", re.IGNORECASE)
_AC_LEAD = re.compile(r"^\s*(when|while|where|if|given)\b", re.IGNORECASE)
_MODAL = re.compile(r"\b(must\s+not|shall\s+not|may\s+not|must|shall|may)\b", re.IGNORECASE)


def _segment_user_story(text: str) -> list[TypedSegment]:
    segs: list[TypedSegment] = []
    role_m, means_m, ben_m = _US_ROLE.search(text), _US_MEANS.search(text), _US_BENEFIT.search(text)
    if role_m:
        end = means_m.start() if means_m else (ben_m.start() if ben_m else len(text))
        segs.append(_span("role", text, role_m.start(), end))
    if means_m:
        end = ben_m.start() if ben_m else len(text)
        segs.append(_span("goal", text, means_m.start(), end))
    if ben_m:
        segs.append(_span("benefit", text, ben_m.start(), len(text)))
    return segs or _whole("goal", text)


def _segment_acceptance(text: str) -> list[TypedSegment]:
    lead = _AC_LEAD.match(text)
    comma = text.find(",")
    if lead and comma != -1:
        label = "trigger" if lead.group(1).lower() in ("when", "if", "given") else "precondition"
        return [_span(label, text, 0, comma), _span("response", text, comma + 1, len(text))]
    return _whole("response", text)


def _segment_constraint(text: str) -> list[TypedSegment]:
    m = _MODAL.search(text)
    if not m:
        return _whole("rule_statement", text)
    segs: list[TypedSegment] = []
    if text[: m.start()].strip():
        segs.append(_span("subject", text, 0, m.start()))
    segs.append(_span("deontic_modality", text, m.start(), m.end()))
    if text[m.end():].strip():
        segs.append(_span("rule_statement", text, m.end(), len(text)))
    return segs


def _segment_glossary(text: str) -> list[TypedSegment]:
    if ":" not in text:
        return _whole("term", text)
    idx = text.index(":")
    segs = [_span("term", text, 0, idx)]
    if text[idx + 1:].strip():
        segs.append(_span("definition", text, idx + 1, len(text)))
    return segs


def segment_for(
    artifact_type: str, text: str, analyzer: Analyzer | None = None
) -> list[TypedSegment]:
    """Deterministic per-type segmentation into the type's schema slots.

    ``functional`` delegates to the legacy clause splitter (requires an analyzer); the other
    types use surface-cue splitters. ``non_functional`` is coarse (whole artifact) for now —
    its detector (metric_presence) scans the whole text.
    """
    if artifact_type == "functional":
        if analyzer is None:
            raise ValueError("functional segmentation requires an analyzer")
        return [TypedSegment(s.kind.value, s.text, s.start, s.end) for s in segment(text, analyzer)]
    if artifact_type == "user_story":
        return _segment_user_story(text)
    if artifact_type == "acceptance_criteria":
        return _segment_acceptance(text)
    if artifact_type == "constraint":
        return _segment_constraint(text)
    if artifact_type == "glossary_term":
        return _segment_glossary(text)
    if artifact_type == "non_functional":
        return _whole("whole_artifact", text)
    raise ValueError(f"unknown artifact_type '{artifact_type}'")
