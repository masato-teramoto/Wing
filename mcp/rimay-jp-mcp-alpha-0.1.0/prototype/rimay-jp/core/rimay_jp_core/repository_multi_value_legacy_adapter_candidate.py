"""Isolated legacy-adapter bridge for the active Multi-value mapping.

This candidate converts one fixed-Repository ConditionStructure syntax node to
the source-bound Repository document record consumed by the active RC-079
mapping.  It is not imported by repository_canonical until separately approved.
"""
from __future__ import annotations

import copy
from dataclasses import dataclass

from .repository_document import _condition_structure_record
from .repository_multi_value_mapping import (
    project_repository_multi_value_condition,
    repository_multi_value_mapping_selector_problems,
)


REPOSITORY_MULTI_VALUE_LEGACY_ADAPTER_CANDIDATE_VERSION = "0.1.0"


@dataclass(frozen=True)
class RepositoryMultiValueLegacyAdapterCandidateError(ValueError):
    code: str
    message: str

    def __str__(self) -> str:
        return f"{self.code}: {self.message}"


def project_legacy_repository_multi_value_condition(
    condition_structure: dict,
    source_text: str,
) -> dict:
    """Project one selected fixed-Repository syntax node through RC-079."""
    try:
        record = _condition_structure_record(
            copy.deepcopy(condition_structure), source_text)
    except (KeyError, TypeError, ValueError) as exc:
        raise RepositoryMultiValueLegacyAdapterCandidateError(
            "REPOSITORY_MULTI_VALUE_LEGACY_RECORD_UNSUPPORTED", str(exc)) from exc
    problems = repository_multi_value_mapping_selector_problems(record, source_text)
    if problems:
        raise RepositoryMultiValueLegacyAdapterCandidateError(
            problems[0], "the complete condition remains on the legacy residual path")
    return project_repository_multi_value_condition(record, source_text)


def legacy_repository_multi_value_selector_problems(
    condition_structure: dict,
    source_text: str,
) -> tuple[str, ...]:
    try:
        project_legacy_repository_multi_value_condition(
            copy.deepcopy(condition_structure), source_text)
    except RepositoryMultiValueLegacyAdapterCandidateError as exc:
        return (exc.code,)
    return ()


__all__ = [
    "REPOSITORY_MULTI_VALUE_LEGACY_ADAPTER_CANDIDATE_VERSION",
    "RepositoryMultiValueLegacyAdapterCandidateError",
    "project_legacy_repository_multi_value_condition",
    "legacy_repository_multi_value_selector_problems",
]
