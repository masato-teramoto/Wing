"""Artifact-type registry (T013).

Loads knowledge/artifact-types.yaml — the six in-scope types (FR-032/FR-045) — and exposes
per-type Layer 1 / Layer 2 paths, grounding source, and status.
"""

from .registry import (
    ArtifactTypeEntry,
    ArtifactTypeRegistry,
    load_artifact_type_registry,
)

__all__ = [
    "ArtifactTypeEntry",
    "ArtifactTypeRegistry",
    "load_artifact_type_registry",
]
