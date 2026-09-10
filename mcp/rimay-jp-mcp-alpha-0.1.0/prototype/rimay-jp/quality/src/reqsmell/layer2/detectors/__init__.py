"""Detector primitive registry.

Maps a rule's ``detector.type`` to its pure detection function. Adding a rule that uses
one of these types requires NO engine change (Constitution IV / FR-022).
"""

from __future__ import annotations

from collections.abc import Callable

from . import (
    completeness,
    ears_pattern,
    glossary,
    lexical,
    metric_presence,
    modality,
    passive_voice,
    segment_count,
    story_template,
    term_definition,
)
from .base import DetectionContext, DetectionHit

REGISTRY: dict[str, Callable[[DetectionContext], list[DetectionHit]]] = {
    # functional-era primitives
    "segment_count": segment_count.detect,
    "completeness": completeness.detect,
    "passive_voice": passive_voice.detect,
    "glossary": glossary.detect,
    # multi-artifact deterministic primitives
    "lexical": lexical.detect,
    "metric_presence": metric_presence.detect,
    "modality": modality.detect,
    "story_template": story_template.detect,
    "ears_pattern": ears_pattern.detect,
    "term_definition": term_definition.detect,
}

__all__ = ["REGISTRY", "DetectionContext", "DetectionHit"]
