"""Shared detector types (T028–T031).

A detector is a pure function ``(DetectionContext) -> list[DetectionHit]``. It knows nothing
about severity/citation/explanation — the engine attaches those from the rule's metadata.
This is what lets a new rule reuse an existing detector with zero engine change (FR-022).
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field

from ...models import SegmentKind
from ...nlp.base import Analyzer
from ..segmentation import Segment


def phrase_pattern(phrase: str) -> str:
    """Regex for a phrase: word-bounded for ASCII (English), bare substring for CJK/Japanese.

    Japanese has no whitespace word boundaries, so ``\\b`` cannot delimit a Japanese phrase;
    for non-ASCII phrases we match the literal substring. Deterministic either way.
    """
    esc = re.escape(phrase)
    return rf"\b{esc}\b" if phrase.isascii() else esc


def phrase_present(text: str, phrases) -> bool:
    return any(re.search(phrase_pattern(p), text, re.IGNORECASE) for p in phrases)


@dataclass(frozen=True)
class DetectionHit:
    # SegmentKind for functional; a plain string for the other types' schema slots
    # (e.g. "response_measure", "deontic_modality", "role").
    segment: SegmentKind | str
    start: int
    end: int
    text: str
    match: str = ""  # term/word that triggered it (for explanation templating)


@dataclass
class DetectionContext:
    text: str
    segments: list[Segment]
    analyzer: Analyzer | None = None  # optional: regex/lexicon detectors need no analyzer
    params: dict = field(default_factory=dict)
    glossary: set[str] = field(default_factory=set)
