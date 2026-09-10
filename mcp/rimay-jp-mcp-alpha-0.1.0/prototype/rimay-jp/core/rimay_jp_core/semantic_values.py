"""Product-level scalar value semantics shared by all projection paths."""
from __future__ import annotations


MONEY_UNITS = frozenset({"JPY", "USD", "EUR"})


def split_money(surface: str) -> tuple[str, str] | None:
    """Return normalized amount/unit only for the closed product currency set."""
    parts = surface.replace(",", "").split()
    if len(parts) == 2 and parts[0].isdigit() and parts[1] in MONEY_UNITS:
        return parts[0], parts[1]
    return None
