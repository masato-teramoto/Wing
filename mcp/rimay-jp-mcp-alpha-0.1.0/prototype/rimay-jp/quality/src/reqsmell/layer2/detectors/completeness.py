"""completeness detector — incomplete condition / incomplete system response.

params["check"] = "condition" | "system_response".
Mirrors the paper's structural patterns (#9–14) and IC1/IC2: a condition missing actor
or verb; a system response missing actor, modal, or verb.
"""

from __future__ import annotations

from ...models import SegmentKind
from .base import DetectionContext, DetectionHit


def detect(ctx: DetectionContext) -> list[DetectionHit]:
    check = ctx.params.get("check")
    a = ctx.analyzer
    hits: list[DetectionHit] = []

    if check == "condition":
        for s in ctx.segments:
            if s.kind != SegmentKind.CONDITION:
                continue
            if not (a.has_actor(s.text) and a.has_finite_verb(s.text)):
                hits.append(DetectionHit(SegmentKind.CONDITION, s.start, s.end, s.text))
        return hits

    if check == "system_response":
        # (a) modal-bearing responses missing actor or verb
        for s in ctx.segments:
            if s.kind != SegmentKind.SYSTEM_RESPONSE:
                continue
            if not (a.has_actor(s.text) and a.has_finite_verb(s.text)):
                hits.append(DetectionHit(SegmentKind.SYSTEM_RESPONSE, s.start, s.end, s.text))
        # (b) action-like clause missing its modal
        for s in ctx.segments:
            if s.kind != SegmentKind.WHOLE_REQUIREMENT:
                continue
            if (
                a.has_actor(s.text)
                and a.has_finite_verb(s.text)
                and not a.has_modal(s.text)
            ):
                hits.append(DetectionHit(SegmentKind.SYSTEM_RESPONSE, s.start, s.end, s.text))
        return hits

    raise ValueError(f"completeness: unknown check '{check}'")
