"""Source registry resolution (T012).

Loads knowledge/sources.yaml and resolves a source_id to a retained reference document,
enforcing the Constitution I / FR-024 / FR-040 / FR-042 / FR-046 grounding gates.
"""

from .resolver import (
    Source,
    SourceResolver,
    SourceResolutionError,
    load_source_resolver,
)

__all__ = [
    "Source",
    "SourceResolver",
    "SourceResolutionError",
    "load_source_resolver",
]
