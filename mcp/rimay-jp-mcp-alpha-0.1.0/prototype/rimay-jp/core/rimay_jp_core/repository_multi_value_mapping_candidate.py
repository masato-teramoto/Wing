"""Isolated Repository mapping candidate for active Multi-value predicates.

The selector is disjoint from the active scalar Comparison mapping: every
condition leaf must be either an accepted scalar predicate or an accepted
value tree, and at least one leaf must contain an explicit group or multiple
values.  Any residual meaning rejects the complete condition record.
"""
from __future__ import annotations

import copy
from dataclasses import dataclass

from .condition_expression import MultiValueRuntimeError, validate_value_expression
from .condition_expression_candidate import (
    ConditionExpressionError,
    project_repository_condition_expression,
)
from .multi_value_candidate import (
    MultiValueCandidateError,
    project_repository_multi_value_expression,
)
from .repository_comparison_mapping import (
    RepositoryComparisonMappingError,
    _assignment_records,
    _matching,
    _one_terminal_string,
    _operator,
    _source_record,
    project_repository_comparison_leaf,
)


REPOSITORY_MULTI_VALUE_MAPPING_CANDIDATE_VERSION = "0.1.0"


@dataclass
class RepositoryMultiValueMappingError(ValueError):
    code: str
    path: str
    message: str

    def __str__(self) -> str:
        return f"{self.code} at {self.path}: {self.message}"

    def finding(self) -> dict:
        return {
            "code": self.code,
            "severity": "blocking",
            "path": self.path,
            "message": self.message,
        }


def _fail(code: str, path: str, message: str) -> None:
    raise RepositoryMultiValueMappingError(code, path, message)


def _candidate_failure(exc: MultiValueCandidateError, path: str) -> None:
    suffix = exc.code.removeprefix("MULTI_VALUE_CANDIDATE_")
    suffix = suffix.removeprefix("REPOSITORY_")
    _fail("REPOSITORY_MULTI_VALUE_" + suffix, path + exc.path, exc.message)


def _project_multi_value_leaf(
    condition_index: int,
    repository_leaf: dict,
    condition_type: str,
    source_text: str,
) -> dict:
    path = f"/repository/condition_expression/leaf/{condition_index}"
    if not isinstance(repository_leaf, dict) or set(repository_leaf) != {
            "kind", "span", "source", "rule"} or \
            repository_leaf.get("kind") != "condition":
        _fail("REPOSITORY_MULTI_VALUE_INVALID_LEAF", path,
              "multi-value leaf shape is closed")
    _source_record(repository_leaf, source_text, path)
    rule = repository_leaf.get("rule")
    if not isinstance(rule, dict) or set(rule) != {
            "rule_id", "span", "source", "assignments"} or \
            rule.get("rule_id") != "InstanceOrPropertyOperatorValue":
        _fail("REPOSITORY_MULTI_VALUE_CONDITION_RULE_UNSUPPORTED", path + "/rule",
              "selected rule must be InstanceOrPropertyOperatorValue")
    _source_record(rule, source_text, path + "/rule")
    assignments = _assignment_records(rule, source_text, path + "/rule")

    rule_names = {name for item in assignments for name in item["rule_path"]}
    features = {item["feature"] for item in assignments}
    if "Modifier" in rule_names or features & {"modifier", "value_modifier"}:
        _fail("REPOSITORY_MULTI_VALUE_MODIFIER_UNSUPPORTED", path,
              "Modifier has no slot in the adopted predicate")
    if "FreeExpression" in rule_names or "additional_information" in features:
        _fail("REPOSITORY_MULTI_VALUE_ADDITIONAL_INFORMATION_UNSUPPORTED", path,
              "additional FreeExpression has no Canonical predicate slot")
    if rule_names & {"OfClassOrReferenceToLabel", "Label"}:
        _fail("REPOSITORY_MULTI_VALUE_METADATA_UNSUPPORTED", path,
              "value type or label metadata remains in the CAP-VALUE residual")

    subjects = [item for item in _matching(
        assignments, "InstanceOrPropertyOperatorValue",
        "non_ui_instance_or_property")
        if item["rule_path"] == ["InstanceOrPropertyOperatorValue"]]
    if len(subjects) != 1:
        _fail("REPOSITORY_MULTI_VALUE_SUBJECT_CARDINALITY", path + "/subject",
              "subject must occur exactly once on the selected condition rule")
    subject, _subject_span = _one_terminal_string(
        subjects[0], source_text, path + "/subject")
    operator = _operator(assignments, path + "/operator")
    try:
        expression = project_repository_multi_value_expression(rule, source_text)
    except MultiValueCandidateError as exc:
        _candidate_failure(exc, path)
        raise AssertionError("unreachable")
    if expression.get("kind") == "value":
        _fail("REPOSITORY_MULTI_VALUE_SCALAR_DELEGATED", path + "/value_expression",
              "a bare scalar belongs to RPMAP-COMPARISON-PREDICATE")
    validate_value_expression(expression, path=path + "/value_expression")
    return {
        "type": condition_type,
        "predicate": {
            "subject": subject,
            "operator": operator,
            "value_expression": expression,
        },
    }


def project_repository_multi_value_condition(
    repository_condition: dict,
    source_text: str,
) -> dict:
    """Project one IF/WHILE record with at least one non-scalar value tree."""
    path = "/repository/condition"
    if not isinstance(repository_condition, dict) or set(repository_condition) != {
            "kind", "rule_path", "span", "source", "keyword", "payload"}:
        _fail("REPOSITORY_MULTI_VALUE_INVALID_CONDITION_RECORD", path,
              "condition record shape is closed")
    kind = repository_condition.get("kind")
    expected_rule = {"if": "IfStructure", "while": "WhileStructure"}.get(kind)
    if expected_rule is None:
        _fail("REPOSITORY_MULTI_VALUE_CONDITION_KIND_UNSUPPORTED", path + "/kind",
              "only IF and WHILE records are selected")
    rule_path = repository_condition.get("rule_path")
    if not isinstance(rule_path, list) or not rule_path or \
            rule_path[-1] != expected_rule:
        _fail("REPOSITORY_MULTI_VALUE_INVALID_CONDITION_RECORD", path + "/rule_path",
              "condition kind and final Repository rule must agree")
    parent_span = _source_record(repository_condition, source_text, path)
    payload = repository_condition.get("payload")
    if not isinstance(payload, dict) or set(payload) != {
            "kind", "span", "source", "expression"} or \
            payload.get("kind") != "expression":
        _fail("REPOSITORY_MULTI_VALUE_INVALID_CONDITION_RECORD", path + "/payload",
              "multi-value condition requires one expression payload")
    payload_span = _source_record(payload, source_text, path + "/payload")
    if not (parent_span["start"] <= payload_span["start"] <= payload_span["end"]
            <= parent_span["end"]):
        _fail("REPOSITORY_MULTI_VALUE_TRACE_OUTSIDE_PARENT", path + "/payload/span",
              "expression payload must be contained by the condition record")
    condition_type = expected_rule.removesuffix("Structure").upper()
    multi_value_count = 0

    def project_leaf(index: int, leaf: dict) -> dict:
        nonlocal multi_value_count
        try:
            projected = _project_multi_value_leaf(
                index, leaf, condition_type, source_text)
        except RepositoryMultiValueMappingError as exc:
            if exc.code != "REPOSITORY_MULTI_VALUE_SCALAR_DELEGATED":
                raise
            return project_repository_comparison_leaf(
                index, leaf, condition_type, source_text)
        multi_value_count += 1
        return projected

    projected = project_repository_condition_expression(
        payload["expression"], source_text, project_leaf)
    if multi_value_count == 0:
        _fail("REPOSITORY_MULTI_VALUE_SCALAR_DELEGATED", path,
              "the complete record belongs to RPMAP-COMPARISON-PREDICATE")
    return projected


def repository_multi_value_mapping_selector_problems(
    repository_condition: dict,
    source_text: str,
) -> tuple[str, ...]:
    """Executable selector candidate; any problem preserves the complete record."""
    try:
        project_repository_multi_value_condition(
            copy.deepcopy(repository_condition), source_text)
    except (
        RepositoryMultiValueMappingError,
        RepositoryComparisonMappingError,
        ConditionExpressionError,
        MultiValueCandidateError,
        MultiValueRuntimeError,
    ) as exc:
        return (exc.code,)
    return ()


__all__ = [
    "REPOSITORY_MULTI_VALUE_MAPPING_CANDIDATE_VERSION",
    "RepositoryMultiValueMappingError",
    "project_repository_multi_value_condition",
    "repository_multi_value_mapping_selector_problems",
]
