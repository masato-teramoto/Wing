"""term_definition detector — glossary term (ISO 704).

Deterministic circular-definition check: given a "term: definition" entry, flag when the
definition restates the term (the term appears, whole-word, inside its own definition).
Term-set consistency across documents is a separate (Arora 2017) check; not implemented here.

params:
  separator: str  (optional) term/definition separator (default ":")
"""

from __future__ import annotations

import re

from .base import DetectionContext, DetectionHit, phrase_pattern


def detect(ctx: DetectionContext) -> list[DetectionHit]:
    # Accept any of the configured separators (ASCII ':' and full-width '：' by default).
    seps = ctx.params.get("separators") or [ctx.params.get("separator", ":"), "："]
    sep = next((s for s in seps if s in ctx.text), None)
    if sep is None:
        return []
    idx = ctx.text.index(sep)
    term = ctx.text[:idx].strip()
    def_start = idx + len(sep)
    definition = ctx.text[def_start:]
    if not term:
        return []
    m = re.search(phrase_pattern(term), definition, re.IGNORECASE)
    if not m:
        return []
    return [DetectionHit("definition", def_start + m.start(), def_start + m.end(), m.group(0), term)]
