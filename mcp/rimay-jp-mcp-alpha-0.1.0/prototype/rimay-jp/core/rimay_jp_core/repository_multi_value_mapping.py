"""Active Repository-document projection for adopted Multi-value predicates.

RC-079 activates the source-bound, disjoint selector frozen by RC-078.  The
historical candidate remains immutable evidence; this module is the active
mapping surface referenced by the Repository projection plan.
"""
from __future__ import annotations

from .repository_multi_value_mapping_candidate import (
    RepositoryMultiValueMappingError,
    project_repository_multi_value_condition,
    repository_multi_value_mapping_selector_problems,
)


REPOSITORY_MULTI_VALUE_MAPPING_VERSION = "0.1.0"


__all__ = [
    "REPOSITORY_MULTI_VALUE_MAPPING_VERSION",
    "RepositoryMultiValueMappingError",
    "project_repository_multi_value_condition",
    "repository_multi_value_mapping_selector_problems",
]
