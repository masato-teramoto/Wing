"""story_template detector — user story (QUS/AQUSA, syntactic).

Deterministic well-formedness: a user story must have a role marker and a means marker. English
defaults follow Connextra ("As a <role>", "I want <goal>"); Japanese (or other) cues can be
supplied via params. Semantic QUS criteria are judgment-based and DEFERRED (FR-039).

params:
  role_pattern: str   (optional) regex for the role marker (default English "as a/an")
  means_pattern: str  (optional) regex for the means/goal marker (default English "I want/need…")
"""

from __future__ import annotations

import re

from .base import DetectionContext, DetectionHit

_DEFAULT_ROLE = r"\bas\s+an?\b"
_DEFAULT_MEANS = r"\bi\s+(want|need|would like|wish|can)\b"


def detect(ctx: DetectionContext) -> list[DetectionHit]:
    role_re = re.compile(ctx.params.get("role_pattern", _DEFAULT_ROLE), re.IGNORECASE)
    means_re = re.compile(ctx.params.get("means_pattern", _DEFAULT_MEANS), re.IGNORECASE)
    hits: list[DetectionHit] = []
    if not role_re.search(ctx.text):
        hits.append(DetectionHit("role", 0, len(ctx.text), ctx.text, "missing role"))
    if not means_re.search(ctx.text):
        hits.append(DetectionHit("goal", 0, len(ctx.text), ctx.text, "missing means/goal"))
    return hits
