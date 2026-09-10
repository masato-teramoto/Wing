"""Active fixed-Repository bridge for the Multi-value mapping.

RC-081 activates the source-bound bridge frozen by RC-080.  The candidate
module remains immutable readiness evidence; this module is the active import
surface used by the legacy all-in-one Repository adapter.
"""
from __future__ import annotations

from .repository_multi_value_legacy_adapter_candidate import (
    RepositoryMultiValueLegacyAdapterCandidateError,
    legacy_repository_multi_value_selector_problems,
    project_legacy_repository_multi_value_condition,
)


REPOSITORY_MULTI_VALUE_LEGACY_ADAPTER_VERSION = "0.1.0"
RepositoryMultiValueLegacyAdapterError = \
    RepositoryMultiValueLegacyAdapterCandidateError


__all__ = [
    "REPOSITORY_MULTI_VALUE_LEGACY_ADAPTER_VERSION",
    "RepositoryMultiValueLegacyAdapterError",
    "project_legacy_repository_multi_value_condition",
    "legacy_repository_multi_value_selector_problems",
]
