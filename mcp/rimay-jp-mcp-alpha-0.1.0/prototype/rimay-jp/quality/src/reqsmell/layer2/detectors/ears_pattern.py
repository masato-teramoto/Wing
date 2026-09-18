"""ears_pattern detector — acceptance criteria (EARS).

Deterministic EARS conformance: a well-formed criterion states a system response with
"shall" (or "must"). Optionally a pattern keyword (When/While/Where/If) introduces a
trigger/precondition. Emits a hit when no response operator is present (not EARS-conformant).

params:
  response_markers: list[str]  (optional) default ["shall", "must"]
"""

from __future__ import annotations

from .base import DetectionContext, DetectionHit, phrase_present

_DEFAULT_RESPONSE = ["shall", "must"]


def detect(ctx: DetectionContext) -> list[DetectionHit]:
    markers = ctx.params.get("response_markers", _DEFAULT_RESPONSE)
    if phrase_present(ctx.text, markers):
        return []
    return [DetectionHit("response", 0, len(ctx.text), ctx.text, "no EARS response operator")]
