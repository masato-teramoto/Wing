"""MCP server entrypoint (T007, T013, T036, T039).

Exposes three tools over stdio:
  - get_requirement_structure   (Layer 1)
  - validate_requirement        (Layer 2, single)
  - validate_requirements_batch (Layer 2, batch)

Stateless: requirement text is never persisted; only metadata is logged (FR-029/FR-030).
"""

from __future__ import annotations

from functools import lru_cache

from mcp.server.fastmcp import FastMCP

from .layer1.provider import get_structure, get_structure_for, list_artifact_types
from .layer2.engine import MAX_BATCH, Engine
from .layer2.engine_v2 import validate_batch_typed, validate_typed
from .logging_config import log_validation_metadata

mcp = FastMCP("reqsmell")


@lru_cache(maxsize=1)
def _engine() -> Engine:
    return Engine()


@mcp.tool()
def get_artifact_types() -> dict:
    """List the six supported requirement artifact types and their grounding status (FR-032).
    No smell detection; lets an agent discover which types can be retrieved/validated."""
    return {"types": list_artifact_types()}


@mcp.tool()
def get_requirement_structure(artifact_type: str | None = None) -> dict:
    """Return the Layer 1 well-formed structure (segment schema) for an artifact type.

    Args:
        artifact_type: one of functional / acceptance_criteria / user_story / constraint /
            non_functional / glossary_term. If omitted, returns the legacy functional structure.
    No smell detection (FR-004)."""
    if artifact_type is None:
        return get_structure()
    return get_structure_for(artifact_type)


@mcp.tool()
def validate_requirement(
    requirement: str, language: str | None = None, artifact_type: str | None = None
) -> dict:
    """Validate a single requirement artifact for smells. Returns a coverage-scoped pass/fail
    verdict and, per detected smell, its name, location, severity, explanation, and source id.

    Args:
        requirement: the artifact text to validate.
        language: optional 'en' or 'ja' to override automatic language detection.
        artifact_type: optional one of functional / acceptance_criteria / user_story /
            constraint / non_functional / glossary_term. Omitted ⇒ legacy functional path.
    """
    # New per-type path for the non-functional types; functional keeps the legacy engine.
    if artifact_type is not None and artifact_type != "functional":
        result = validate_typed(requirement, artifact_type, language)
    else:
        result = _engine().validate(requirement, language)
    by_smell: dict[str, int] = {}
    for f in result.findings:
        by_smell[f.smell] = by_smell.get(f.smell, 0) + 1
    log_validation_metadata(language=result.language.value,
                            finding_count=len(result.findings), by_smell=by_smell)
    return result.to_dict()


@mcp.tool()
def validate_requirements_batch(
    requirements: list[str], language: str | None = None, artifact_type: str | None = None
) -> dict:
    """Validate a batch of artifacts (max ~1000). Returns a per-item result plus a cross-batch
    summary (passed, failed, occurrences per smell, and counts per artifact type).

    Args:
        requirements: list of artifact texts.
        language: optional 'en' or 'ja' applied to all items (else per-item detection).
        artifact_type: optional type applied to all items. Omitted ⇒ legacy functional batch;
            pass a type to use the per-type path (mixed-type detection when type is omitted there).
    """
    if len(requirements) > MAX_BATCH:
        raise ValueError(f"batch exceeds {MAX_BATCH} requirements (LIMIT_EXCEEDED)")
    if artifact_type is not None and artifact_type != "functional":
        result = validate_batch_typed(requirements, artifact_type, language)
    else:
        result = _engine().validate_batch(requirements, language)
    log_validation_metadata(language="batch", finding_count=sum(result.summary.by_smell.values()),
                            by_smell=result.summary.by_smell)
    return result.to_dict()


def main() -> None:
    """Start the MCP server.

    Default transport is **stdio** (the client spawns the process). To run as a standalone
    HTTP server, pass ``--http`` (streamable-http) or ``--sse``, or set REQSMELL_TRANSPORT.
    Host/port come from REQSMELL_HOST / REQSMELL_PORT (default 127.0.0.1:8000); the HTTP
    endpoint is served at ``/mcp``.
    """
    import os
    import sys

    argv = sys.argv[1:]
    transport = os.environ.get("REQSMELL_TRANSPORT", "stdio").lower()
    if "--http" in argv or transport in ("http", "streamable-http"):
        transport = "streamable-http"
    elif "--sse" in argv or transport == "sse":
        transport = "sse"
    else:
        transport = "stdio"

    if transport == "stdio":
        mcp.run()
        return

    mcp.settings.host = os.environ.get("REQSMELL_HOST", mcp.settings.host)
    mcp.settings.port = int(os.environ.get("REQSMELL_PORT", mcp.settings.port))
    mcp.run(transport=transport)


if __name__ == "__main__":
    main()
