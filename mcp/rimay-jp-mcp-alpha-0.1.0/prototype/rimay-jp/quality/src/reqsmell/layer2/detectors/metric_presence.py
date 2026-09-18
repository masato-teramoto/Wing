"""metric_presence detector — non-functional requirement (QAS).

The core NFR smell is a *quality target without a measurable metric* (a missing
``response_measure``). This is an ABSENCE check: it emits a single hit covering the whole
artifact when NO quantified measure is present. Deterministic (regex only).

params:
  units: list[str]  (optional) extra unit tokens that count as a measure
"""

from __future__ import annotations

import re

from .base import DetectionContext, DetectionHit

# A measurable target = a number (optionally with %, time, or a unit word) or a percentage word.
_DEFAULT_UNITS = ["%", "ms", "s", "sec", "second", "seconds", "minute", "minutes", "hour",
                  "hours", "percent", "requests", "users", "mb", "gb", "kb", "fps"]
_NUMBER_RE = re.compile(r"\d")


def _has_measure(text: str, units: list[str]) -> bool:
    if _NUMBER_RE.search(text):
        return True
    low = text.lower()
    return any(re.search(r"\b" + re.escape(u) + r"\b", low) for u in units if u.isalpha())


def detect(ctx: DetectionContext) -> list[DetectionHit]:
    units = _DEFAULT_UNITS + list(ctx.params.get("units", []))
    if _has_measure(ctx.text, units):
        return []
    return [DetectionHit("response_measure", 0, len(ctx.text), ctx.text, "")]
