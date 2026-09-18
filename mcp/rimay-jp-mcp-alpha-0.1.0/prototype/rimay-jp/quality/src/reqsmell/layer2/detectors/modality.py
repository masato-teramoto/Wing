"""modality detector — constraint / business rule (SBVR).

Deterministic well-formedness of deontic modality: a constraint must carry an explicit
obligation/prohibition/permission operator. Emits a hit when no strong modal is present
(missing modality) or only a weak/ambiguous modal is present (ambiguous modality).

params:
  modals: list[str]  (optional) strong deontic operators (default must/shall/may + negations)
  weak:   list[str]  (optional) ambiguous operators (default should/could/might/ought)
"""

from __future__ import annotations

from .base import DetectionContext, DetectionHit, phrase_present

_DEFAULT_MODALS = ["must not", "shall not", "must", "shall", "may not", "may",
                   "is required to", "is prohibited from", "is permitted to"]
_DEFAULT_WEAK = ["should", "could", "might", "ought to", "ideally", "preferably"]


def detect(ctx: DetectionContext) -> list[DetectionHit]:
    modals = ctx.params.get("modals", _DEFAULT_MODALS)
    weak = ctx.params.get("weak", _DEFAULT_WEAK)
    if phrase_present(ctx.text, modals):
        return []
    # No strong modal: a hit on the deontic_modality slot. Note ambiguity if a weak modal exists.
    match = "ambiguous" if phrase_present(ctx.text, weak) else "missing"
    return [DetectionHit("deontic_modality", 0, len(ctx.text), ctx.text, match)]
