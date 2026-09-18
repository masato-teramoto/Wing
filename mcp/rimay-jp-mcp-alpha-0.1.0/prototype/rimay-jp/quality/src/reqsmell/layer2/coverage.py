"""Coverage builder (T040, FR-044).

Assembles the per-result ``coverage`` disclosure: which of a type's source-defined smells were
*checked* (shippable deterministic rules — type catalog + general catalog) vs *unchecked*
(deferred judgment, or pending source). Derived purely from loaded asset metadata — no runtime
judgment — so it is byte-identical for a given knowledge version (FR-015).
"""

from __future__ import annotations

from collections.abc import Iterable

from ..models import Coverage, UncheckedReason, UncheckedSmell

_REASONS = {r.value: r for r in UncheckedReason}


def build_coverage(
    checked: Iterable[str],
    unchecked: Iterable[tuple[str, str]],
) -> Coverage:
    """Build a deterministic Coverage from explicit smell-id lists.

    ``checked``   — smell ids actually evaluated.
    ``unchecked`` — (smell_id, reason) pairs; reason ∈ {deferred_judgment, pending_source}.

    Both lists are de-duplicated and sorted for determinism.
    """
    checked_sorted = tuple(sorted(set(checked)))
    seen: dict[str, UncheckedReason] = {}
    for smell, reason in unchecked:
        if reason not in _REASONS:
            raise ValueError(f"invalid unchecked reason '{reason}' for smell '{smell}'")
        # First reason wins for a given smell; deterministic via sort below regardless.
        seen.setdefault(smell, _REASONS[reason])
    unchecked_sorted = tuple(
        UncheckedSmell(smell, seen[smell]) for smell in sorted(seen)
    )
    return Coverage(checked=checked_sorted, unchecked=unchecked_sorted)


def coverage_from_catalog(entries: Iterable[dict]) -> Coverage:
    """Build Coverage from catalog rule metadata.

    Each entry: {"id": str, "ships": bool, "reason": str|None}. A shipping rule → checked;
    a non-shipping rule → unchecked with its reason (default 'deferred_judgment').
    """
    checked: list[str] = []
    unchecked: list[tuple[str, str]] = []
    for e in entries:
        if e.get("ships"):
            checked.append(e["id"])
        else:
            unchecked.append((e["id"], e.get("reason") or UncheckedReason.DEFERRED_JUDGMENT.value))
    return build_coverage(checked, unchecked)
