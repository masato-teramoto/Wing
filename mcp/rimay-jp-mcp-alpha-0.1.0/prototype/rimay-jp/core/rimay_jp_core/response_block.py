"""Active Canonical 0.8.0 Itemized Response Block boundary.

The accepted candidate remains frozen adoption evidence. This runtime entry
point re-exports its proven projection, rendering and migration primitives and
adds stable item traversal for active consumers.
"""
from __future__ import annotations

from typing import Iterator

from . import SCHEMA_VERSION
from .response_block_candidate import (
    RESPONSE_BLOCK_CANDIDATE_VERSION,
    ResponseBlockError,
    build_response_block_candidate_schema,
    canonical_response_block_meaning,
    migrate_requirement_to_response_block_candidate,
    parse_rendered_response_block,
    project_repository_response_block,
    quarantine_response_block_for_rollback,
    render_response_block,
    replay_response_block_migration,
    response_block_core_findings,
    response_block_findings,
    restore_quarantined_response_block,
    rollback_requirement_from_response_block_candidate,
)

RESPONSE_BLOCK_VERSION = "0.8.0"
if tuple(map(int, SCHEMA_VERSION.split("."))) < (0, 8, 0) or \
        RESPONSE_BLOCK_CANDIDATE_VERSION != RESPONSE_BLOCK_VERSION:
    raise RuntimeError("active Response Block and Canonical Schema versions diverged")


def iter_response_block_items(
    block: dict,
    *,
    path: str = "/rimay_core/response_block",
    source_text: str | None = None,
) -> Iterator[tuple[str, dict]]:
    """Yield ``(CanonicalPointer, response)`` in stable item position order."""
    findings = response_block_findings(block, source_text=source_text, path=path)
    if findings:
        first = findings[0]
        raise ResponseBlockError(first["code"], first["path"], first["message"])
    for position, item in enumerate(block["items"]):
        yield f"{path}/items/{position}/response", item["response"]


__all__ = [
    "RESPONSE_BLOCK_VERSION", "ResponseBlockError",
    "build_response_block_candidate_schema", "canonical_response_block_meaning",
    "iter_response_block_items", "migrate_requirement_to_response_block_candidate",
    "parse_rendered_response_block", "project_repository_response_block",
    "quarantine_response_block_for_rollback", "render_response_block",
    "replay_response_block_migration", "response_block_core_findings",
    "response_block_findings", "restore_quarantined_response_block",
    "rollback_requirement_from_response_block_candidate",
]
