"""Active Atomic Response boundary for Canonical 0.9.0 and later.

The accepted candidate remains frozen adoption evidence.  This entry point
exposes the proven projection, validation and migration primitives to active
runtime consumers while keeping Repository provenance out of semantic
comparison.
"""
from __future__ import annotations

import copy

from . import SCHEMA_VERSION
from .atomic_response_candidate import (
    ATOMIC_RESPONSE_CANDIDATE_VERSION,
    AtomicResponseError,
    atomic_response_findings,
    canonical_atomic_response_meaning,
    migrate_requirement_to_atomic_response_candidate,
    project_repository_atomic_response,
    quarantine_atomic_responses_for_rollback,
    replay_atomic_response_migration,
    restore_quarantined_atomic_responses,
    rollback_requirement_from_atomic_response_candidate,
)

ATOMIC_RESPONSE_VERSION = "0.9.0"
if tuple(map(int, SCHEMA_VERSION.split("."))) < (0, 9, 0) or \
        ATOMIC_RESPONSE_CANDIDATE_VERSION != ATOMIC_RESPONSE_VERSION:
    raise RuntimeError("active Atomic Response and Canonical Schema versions diverged")


def semantic_atomic_response(value: object) -> object:
    """Drop provenance-only Atomic fields while retaining value and unit."""
    if isinstance(value, dict):
        out = {
            key: semantic_atomic_response(item)
            for key, item in value.items()
            if key != "repository_trace"
        }
        frequency = out.get("frequency")
        if isinstance(frequency, dict):
            frequency.pop("source_expression", None)
        return out
    if isinstance(value, list):
        return [semantic_atomic_response(item) for item in value]
    return copy.deepcopy(value)


__all__ = [
    "ATOMIC_RESPONSE_VERSION", "AtomicResponseError",
    "atomic_response_findings", "canonical_atomic_response_meaning",
    "migrate_requirement_to_atomic_response_candidate",
    "project_repository_atomic_response", "quarantine_atomic_responses_for_rollback",
    "replay_atomic_response_migration", "restore_quarantined_atomic_responses",
    "rollback_requirement_from_atomic_response_candidate", "semantic_atomic_response",
]
