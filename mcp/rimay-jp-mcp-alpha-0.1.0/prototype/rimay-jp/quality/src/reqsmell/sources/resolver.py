"""Source registry resolver (T012).

Loads ``knowledge/sources.yaml`` (validated by ``schemas/source-registry.schema.json``) and
resolves a ``source_id`` to its retained reference document. Implements the grounding gates:

* FR-024  — a rule's definition source_id MUST resolve to a retained file (retention=retained
            with an existing ``ref``); otherwise the rule cannot ship.
* FR-040  — a Layer 2 detection rule whose definition source is standard/notation tier MUST
            additionally cite a paper-tier ``method`` source; else it is deferred.
* FR-042  — a ``method``-role source may not be used as a rule's definition source.
* FR-046  — a ``retention: recommended`` (analyst-asserted) source is admissible for Layer 1
            structure grounding ONLY; it is rejected as a Layer 2 rule's source.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from ..knowledge_io import (
    KnowledgeError,
    knowledge_dir,
    load_yaml,
    repo_root,
    validate_against_schema,
)


class SourceResolutionError(KnowledgeError):
    """Raised when a source_id cannot be resolved or violates a grounding gate."""


@dataclass(frozen=True)
class Source:
    id: str
    tier: str           # paper | standard | notation
    role: str           # definition | method
    retention: str      # retained | recommended
    title: str
    ref: str | None = None

    @property
    def is_retained(self) -> bool:
        return self.retention == "retained"

    @property
    def is_paper(self) -> bool:
        return self.tier == "paper"


class SourceResolver:
    """In-memory view of the source registry with the grounding gates."""

    def __init__(self, sources: dict[str, Source]):
        self._sources = sources

    # -- lookup -----------------------------------------------------------
    def get(self, source_id: str) -> Source:
        try:
            return self._sources[source_id]
        except KeyError:
            raise SourceResolutionError(
                f"Unknown source_id '{source_id}' (not in sources.yaml)"
            ) from None

    def __contains__(self, source_id: str) -> bool:
        return source_id in self._sources

    # -- gates ------------------------------------------------------------
    def resolve_definition(self, source_id: str, *, layer: str = "layer2") -> Source:
        """Resolve a *definition* source for ``layer`` ('layer1' | 'layer2').

        Decision B (2026-06-24, amended FR-046): an analyst-asserted source
        (``retention: recommended``) may ground **both** Layer 1 structure and Layer 2 detection.
        A retained source must still have an existing ``ref`` (FR-024); a method-role source may
        never define (FR-042); and FR-040's paper-method requirement for standard/notation tiers
        is enforced separately in ``layer2_rule_ships``. ``layer`` is retained for context only.
        """
        src = self.get(source_id)
        if src.role != "definition":  # FR-042
            raise SourceResolutionError(
                f"source '{source_id}' has role '{src.role}'; a definition source is required "
                f"(method/SOTA sources may not define — FR-042)"
            )
        if src.is_retained:
            self._assert_ref_exists(src)
        # else: analyst-asserted (recommended) — admissible for L1 and L2 (amended FR-046).
        return src

    def requires_method(self, definition: Source) -> bool:
        """FR-040: a standard/notation definition needs paper-tier method evidence to ship."""
        return definition.tier in ("standard", "notation")

    def resolve_method(self, source_id: str) -> Source:
        src = self.get(source_id)
        if src.role != "method":
            raise SourceResolutionError(
                f"source '{source_id}' has role '{src.role}'; a method source is required (FR-040)"
            )
        if not src.is_paper:
            raise SourceResolutionError(
                f"method source '{source_id}' is tier '{src.tier}'; FR-040 requires paper-tier "
                f"method evidence"
            )
        if not src.is_retained:
            raise SourceResolutionError(
                f"method source '{source_id}' must be retained (FR-024)"
            )
        self._assert_ref_exists(src)
        return src

    def layer2_rule_ships(
        self, definition_source_id: str, method_source_id: str | None
    ) -> tuple[bool, str]:
        """Decide whether an L2 deterministic rule may ship; return (ships, reason).

        ships=False means the rule is *deferred* (defined but not executed), not malformed.
        """
        try:
            definition = self.resolve_definition(definition_source_id, layer="layer2")
        except SourceResolutionError as exc:
            return False, str(exc)
        if self.requires_method(definition):
            if method_source_id is None:
                return False, (
                    f"definition '{definition_source_id}' is {definition.tier}-tier; FR-040 "
                    f"requires a paper method_source_id to ship"
                )
            try:
                self.resolve_method(method_source_id)
            except SourceResolutionError as exc:
                return False, str(exc)
        return True, "ok"

    # -- helpers ----------------------------------------------------------
    def _assert_ref_exists(self, src: Source) -> None:
        if not src.ref:
            raise SourceResolutionError(
                f"source '{src.id}' is retained but has no 'ref' path"
            )
        path = repo_root() / src.ref
        if not path.exists():
            raise SourceResolutionError(
                f"source '{src.id}' ref does not exist on disk: {src.ref} (FR-024)"
            )


def load_source_resolver(path: Path | None = None) -> SourceResolver:
    """Load + schema-validate sources.yaml and build a SourceResolver."""
    path = path or (knowledge_dir() / "sources.yaml")
    data = load_yaml(path)
    validate_against_schema(data, "source-registry.schema.json", source=str(path))
    sources: dict[str, Source] = {}
    for row in data["sources"]:
        if row["id"] in sources:
            raise SourceResolutionError(f"duplicate source_id '{row['id']}' in {path}")
        sources[row["id"]] = Source(
            id=row["id"],
            tier=row["tier"],
            role=row["role"],
            retention=row["retention"],
            title=row["title"],
            ref=row.get("ref"),
        )
    return SourceResolver(sources)
