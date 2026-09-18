"""glossary detector — the paper's "Glossary search" technique (§5.3).

Flags vague verbs (params glossary) appearing in condition / system_response / clause text.
"""

from __future__ import annotations

from ...models import SegmentKind
from .base import DetectionContext, DetectionHit

_SCANNED = {SegmentKind.CONDITION, SegmentKind.SYSTEM_RESPONSE, SegmentKind.WHOLE_REQUIREMENT}


def detect(ctx: DetectionContext) -> list[DetectionHit]:
    hits: list[DetectionHit] = []
    for s in ctx.segments:
        if s.kind not in _SCANNED:
            continue
        for term, rel_start, rel_end in ctx.analyzer.find_glossary_hits(s.text, ctx.glossary):
            kind = s.kind if s.kind != SegmentKind.WHOLE_REQUIREMENT else SegmentKind.SYSTEM_RESPONSE
            hits.append(
                DetectionHit(kind, s.start + rel_start, s.start + rel_end, term, term)
            )
    return hits
