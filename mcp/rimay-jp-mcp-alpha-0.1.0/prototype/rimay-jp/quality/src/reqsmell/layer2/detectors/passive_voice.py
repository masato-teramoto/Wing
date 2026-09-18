"""passive_voice detector — the paper's structural patterns #1–8 (and JA 受身).

Scans condition, system_response, and unclassified clauses for passive constructions.
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
        for rel_start, rel_end, matched in ctx.analyzer.passive_spans(s.text):
            kind = s.kind if s.kind != SegmentKind.WHOLE_REQUIREMENT else SegmentKind.SYSTEM_RESPONSE
            hits.append(
                DetectionHit(kind, s.start + rel_start, s.start + rel_end, matched, matched)
            )
    return hits
