"""segment_count detector — the paper's "Rules" technique (§5.3).

Handles five smells via params["check"]: non_atomic, incomplete_requirement,
incorrect_order, not_a_requirement, coordination_ambiguity.
"""

from __future__ import annotations

import re

from ...models import SegmentKind
from .base import DetectionContext, DetectionHit

_OR_COND_EN = re.compile(r"\bor\b\s+(when|if|while|where)\b", re.IGNORECASE)
_OR_JA = ("または", "もしくは")


def _responses(ctx: DetectionContext):
    return [s for s in ctx.segments if s.kind == SegmentKind.SYSTEM_RESPONSE]


def _conditions(ctx: DetectionContext):
    return [s for s in ctx.segments if s.kind == SegmentKind.CONDITION]


def _scopes(ctx: DetectionContext):
    return [s for s in ctx.segments if s.kind == SegmentKind.SCOPE]


def _action_like(ctx: DetectionContext):
    """Clauses that look like a system response but lack a modal (missing-modal case)."""
    out = []
    for s in ctx.segments:
        if s.kind == SegmentKind.WHOLE_REQUIREMENT:
            if (
                ctx.analyzer.has_actor(s.text)
                and ctx.analyzer.has_finite_verb(s.text)
                and not ctx.analyzer.has_modal(s.text)
            ):
                out.append(s)
    return out


def _whole_span(ctx: DetectionContext) -> DetectionHit:
    return DetectionHit(SegmentKind.WHOLE_REQUIREMENT, 0, len(ctx.text), ctx.text)


def detect(ctx: DetectionContext) -> list[DetectionHit]:
    check = ctx.params.get("check")
    responses = _responses(ctx)
    conditions = _conditions(ctx)
    scopes = _scopes(ctx)

    if check == "non_atomic":
        total = sum(ctx.analyzer.action_count(s.text) for s in responses)
        if responses and total > 1:
            first, last = responses[0], responses[-1]
            return [DetectionHit(SegmentKind.WHOLE_REQUIREMENT, first.start, last.end,
                                 ctx.text[first.start:last.end])]
        return []

    if check == "incomplete_requirement":
        if (conditions or scopes) and not responses and not _action_like(ctx):
            return [_whole_span(ctx)]
        return []

    if check == "incorrect_order":
        hits = []
        if responses:
            first_response_start = responses[0].start
            for c in conditions:
                if c.start > first_response_start:
                    hits.append(DetectionHit(SegmentKind.CONDITION, c.start, c.end, c.text))
        return hits

    if check == "not_a_requirement":
        if not responses and not conditions and not scopes and not _action_like(ctx):
            return [_whole_span(ctx)]
        return []

    if check == "coordination_ambiguity":
        hits = []
        for c in conditions:
            if ctx.analyzer.lang == "ja":
                triggered = any(tok in c.text for tok in _OR_JA)
            else:
                triggered = bool(_OR_COND_EN.search(c.text))
            if triggered:
                hits.append(DetectionHit(SegmentKind.CONDITION, c.start, c.end, c.text))
        return hits

    raise ValueError(f"segment_count: unknown check '{check}'")
