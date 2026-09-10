"""lexical detector — Femmer-style artifact-agnostic lexical smells (FR-041).

Flags occurrences of words from a configured lexicon. Word-bounded for ASCII (English),
substring for CJK (Japanese). Deterministic, case-insensitive. params:
  lexicon: list[str]      (required) the words/phrases to flag
  segment: str            (optional) segment label for hits (default "whole_artifact")
"""

from __future__ import annotations

import re

from .base import DetectionContext, DetectionHit, phrase_pattern


def detect(ctx: DetectionContext) -> list[DetectionHit]:
    lexicon = ctx.params.get("lexicon", [])
    label = ctx.params.get("segment", "whole_artifact")
    hits: list[DetectionHit] = []
    # Longest-first so multi-word phrases win over their parts; deterministic.
    for term in sorted(set(lexicon), key=len, reverse=True):
        for m in re.finditer(phrase_pattern(term), ctx.text, re.IGNORECASE):
            hits.append(DetectionHit(label, m.start(), m.end(), m.group(0), term.lower()))
    # De-dupe overlapping spans (a longer phrase covering a shorter one), then order.
    seen: set[tuple[int, int]] = set()
    unique = []
    for h in sorted(hits, key=lambda h: (h.start, -(h.end - h.start))):
        if any(h.start < e and s < h.end for s, e in seen):
            continue
        seen.add((h.start, h.end))
        unique.append(h)
    return sorted(unique, key=lambda h: (h.start, h.match))
