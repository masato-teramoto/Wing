"""Active Response expression boundary for Canonical 0.6.0 and later.

The accepted B5-P candidate remains as frozen adoption evidence. This module is
the runtime entry point: it exposes the proven projection/migration primitives
and adds traversal helpers used by parser, serializers, validators and Store.
"""
from __future__ import annotations

from typing import Iterable, Iterator

from . import SCHEMA_VERSION
from .response_expression_candidate import (
    RESPONSE_EXPRESSION_CANDIDATE_VERSION,
    ResponseExpressionError,
    canonical_response_expression_meaning,
    canonical_response_expression_shape,
    migrate_requirement_to_response_expression,
    parse_rendered_response_expression,
    project_repository_response_expression,
    quarantine_composite_response_expression_for_rollback,
    render_response_expression,
    repository_response_expression_shape,
    response_core_findings as response_expression_core_findings,
    response_expression_findings,
    restore_quarantined_response_expression,
    rollback_requirement_from_response_expression,
)
from .response_block import (
    ResponseBlockError,
    iter_response_block_items,
    response_block_core_findings,
)
from .atomic_response import AtomicResponseError, atomic_response_findings

RESPONSE_EXPRESSION_VERSION = "0.6.0"
if tuple(map(int, SCHEMA_VERSION.split("."))) < (0, 6, 0) or \
        RESPONSE_EXPRESSION_CANDIDATE_VERSION != RESPONSE_EXPRESSION_VERSION:
    raise RuntimeError("active Response expression and Canonical Schema versions diverged")


def iter_response_expression_leaves(
    expression: dict,
    *,
    path: str = "/rimay_core/response_expression",
) -> Iterator[tuple[str, dict]]:
    """Yield ``(CanonicalPointer, response)`` in stable left-to-right order."""
    kind = expression.get("kind") if isinstance(expression, dict) else None
    if kind == "response":
        response = expression.get("response")
        if not isinstance(response, dict):
            raise ResponseExpressionError(
                "RESPONSE_EXPRESSION_INVALID_LEAF", path + "/response",
                "response must be an object")
        yield path + "/response", response
        return
    if kind == "group":
        yield from iter_response_expression_leaves(
            expression.get("expression"), path=path + "/expression")
        return
    if kind in {"and", "or"}:
        yield from iter_response_expression_leaves(
            expression.get("left"), path=path + "/left")
        yield from iter_response_expression_leaves(
            expression.get("right"), path=path + "/right")
        return
    raise ResponseExpressionError(
        "RESPONSE_EXPRESSION_INVALID_NODE", path, f"unsupported kind {kind!r}")


def iter_core_responses(
    core: dict, *, source_text: str | None = None,
) -> Iterator[tuple[str, dict]]:
    """Traverse single response, expression leaves, or block items."""
    problems = response_core_findings(core, source_text=source_text)
    if problems:
        first = problems[0]
        error_type = (
            ResponseBlockError if first["code"].startswith("RESPONSE_BLOCK_")
            else AtomicResponseError if first["code"].startswith("ATOMIC_RESPONSE_")
            else ResponseExpressionError
        )
        raise error_type(first["code"], first["path"], first["message"])
    expression = core.get("response_expression")
    if expression is not None:
        yield from iter_response_expression_leaves(expression)
        return
    block = core.get("response_block")
    if block is not None:
        yield from iter_response_block_items(block, source_text=source_text)
        return
    response = core.get("response")
    if isinstance(response, dict):
        yield "/rimay_core/response", response


def response_core_findings(
    core: object, *, source_text: str | None = None,
) -> tuple[dict, ...]:
    """Validate the mutually-exclusive active response source and its shape."""
    if isinstance(core, dict) and "response_block" in core:
        block_problems = response_block_core_findings(core, source_text=source_text)
        if block_problems:
            return block_problems
    structural = response_expression_core_findings(core)
    if structural:
        return structural
    if not isinstance(core, dict):
        return structural

    responses: list[tuple[str, dict]] = []
    expression = core.get("response_expression")
    block = core.get("response_block")
    if isinstance(expression, dict):
        responses.extend(iter_response_expression_leaves(expression))
    elif isinstance(block, dict):
        responses.extend(iter_response_block_items(block, source_text=source_text))
    elif isinstance(core.get("response"), dict):
        responses.append(("/rimay_core/response", core["response"]))
    findings = []
    for path, response in responses:
        findings.extend(atomic_response_findings(
            response, source_text=source_text, path=path))
    return tuple(findings)


def strip_repository_trace(value: object) -> object:
    """Return the semantic value of a response tree without repository provenance."""
    if isinstance(value, dict):
        return {
            key: strip_repository_trace(item)
            for key, item in value.items()
            if key != "repository_trace"
        }
    if isinstance(value, list):
        return [strip_repository_trace(item) for item in value]
    return value


def migrate_experience_store_records(records: Iterable[dict]) -> dict:
    """Compatibility import for the active Canonical Store reader."""
    from .condition_expression import migrate_experience_store_records as migrate
    return migrate(records)


__all__ = [
    "RESPONSE_EXPRESSION_VERSION", "ResponseBlockError", "ResponseExpressionError",
    "canonical_response_expression_meaning", "canonical_response_expression_shape",
    "iter_core_responses", "iter_response_expression_leaves",
    "migrate_experience_store_records", "migrate_requirement_to_response_expression",
    "parse_rendered_response_expression", "project_repository_response_expression",
    "quarantine_composite_response_expression_for_rollback",
    "render_response_expression", "repository_response_expression_shape",
    "response_core_findings", "response_expression_findings",
    "restore_quarantined_response_expression", "rollback_requirement_from_response_expression",
    "strip_repository_trace",
]
