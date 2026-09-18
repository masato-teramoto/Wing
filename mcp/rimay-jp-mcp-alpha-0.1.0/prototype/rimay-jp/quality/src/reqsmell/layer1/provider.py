"""Layer 1 structure provider (T012).

Loads and schema-validates knowledge/layer1/structure.yaml and serves it. Contains NO
smell-detection logic (FR-004) — it only supplies the structure (FR-001–FR-005).
"""

from __future__ import annotations

from functools import lru_cache

from ..artifact_types.registry import load_artifact_type_registry
from ..knowledge_io import knowledge_dir, load_yaml, repo_root, validate_against_schema


@lru_cache(maxsize=1)
def get_structure() -> dict:
    """Return the validated (legacy, functional) Layer 1 structure as a JSON-ready dict.

    Retained for backward compatibility; new callers use ``get_structure_for(artifact_type)``.
    """
    data = load_yaml(knowledge_dir() / "layer1" / "structure.yaml")
    validate_against_schema(data, "layer1-structure.schema.json", source="layer1/structure.yaml")
    return data


@lru_cache(maxsize=16)
def get_structure_for(artifact_type: str) -> dict:
    """Return the validated Layer 1 segment schema for one of the six in-scope types.

    Reads the path from the artifact-type registry and validates against the multi-artifact
    schema (``layer1-structure.v2.schema.json``). No detection logic (FR-004). Raises
    ArtifactTypeError for an unknown type.
    """
    entry = load_artifact_type_registry().get(artifact_type)
    path = repo_root() / entry.layer1_structure
    data = load_yaml(path)
    validate_against_schema(
        data, "layer1-structure.v2.schema.json", source=entry.layer1_structure
    )
    return data


def list_artifact_types() -> list[dict]:
    """Discovery: the six in-scope types with grounding status (FR-032). No detection."""
    reg = load_artifact_type_registry()
    out: list[dict] = []
    for tid in reg.ids():
        e = reg.get(tid)
        out.append(
            {
                "id": e.id,
                "name": e.name,
                "grounding_status": e.grounding_status,
                "implementable": e.implementable,
                "definition_source_id": e.definition_source_id,
            }
        )
    return out
