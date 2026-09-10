"""Artifact-type registry (T013).

Loads ``knowledge/artifact-types.yaml`` (validated by ``schemas/artifact-types.schema.json``) and
exposes the six in-scope artifact types. ``requirement_set`` is intentionally absent (out of scope,
FR-045). Optionally cross-checks each type's ``definition_source_id`` against a SourceResolver.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from ..knowledge_io import (
    KnowledgeError,
    knowledge_dir,
    load_yaml,
    validate_against_schema,
)
from ..sources.resolver import SourceResolver

IN_SCOPE_TYPES = (
    "functional",
    "acceptance_criteria",
    "user_story",
    "constraint",
    "non_functional",
    "glossary_term",
)


class ArtifactTypeError(KnowledgeError):
    """Raised when the artifact-type registry is missing or invalid."""


@dataclass(frozen=True)
class ArtifactTypeEntry:
    id: str
    name: str
    layer1_structure: str
    layer2_catalog_dir: str
    definition_source_id: str
    implementable: str       # deterministic | judgment | mixed
    grounding_status: str    # grounded | pending_source | partial


class ArtifactTypeRegistry:
    def __init__(self, entries: dict[str, ArtifactTypeEntry]):
        self._entries = entries

    def ids(self) -> list[str]:
        return list(self._entries.keys())

    def get(self, type_id: str) -> ArtifactTypeEntry:
        try:
            return self._entries[type_id]
        except KeyError:
            raise ArtifactTypeError(
                f"Unknown artifact type '{type_id}' (in-scope: {', '.join(self._entries)})"
            ) from None

    def __contains__(self, type_id: str) -> bool:
        return type_id in self._entries

    def __len__(self) -> int:
        return len(self._entries)

    def validate_groundings(self, resolver: SourceResolver) -> None:
        """Confirm every type's definition_source_id resolves (Layer 1 grounding; FR-005/FR-046)."""
        for entry in self._entries.values():
            resolver.resolve_definition(entry.definition_source_id, layer="layer1")


def load_artifact_type_registry(path: Path | None = None) -> ArtifactTypeRegistry:
    path = path or (knowledge_dir() / "artifact-types.yaml")
    data = load_yaml(path)
    validate_against_schema(data, "artifact-types.schema.json", source=str(path))
    entries: dict[str, ArtifactTypeEntry] = {}
    for row in data["types"]:
        if row["id"] in entries:
            raise ArtifactTypeError(f"duplicate artifact type '{row['id']}' in {path}")
        entries[row["id"]] = ArtifactTypeEntry(
            id=row["id"],
            name=row["name"],
            layer1_structure=row["layer1_structure"],
            layer2_catalog_dir=row["layer2_catalog_dir"],
            definition_source_id=row["definition_source_id"],
            implementable=row["implementable"],
            grounding_status=row["grounding_status"],
        )
    if "requirement_set" in entries:  # FR-045 guard
        raise ArtifactTypeError("requirement_set is out of scope (FR-045) and must not be registered")
    return ArtifactTypeRegistry(entries)
