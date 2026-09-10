"""Repository Operator value mapping separation candidate.

The active Canonical 1.1 runtime can represent all three typed Repository
operand wrappers.  This module proves that a complete IF/WHILE condition
record can be projected without guessing declaration identity or dropping a
residual leaf.  It deliberately does not register an active Repository
adapter or change the mapping plan: ``InstanceOrPropertyOperatorValue`` also
belongs to the existing scalar Comparison and Multi-value execution surfaces,
and mapping contract 0.4 has no precedence/composition contract for that
overlap.
"""
from __future__ import annotations

import copy
from dataclasses import dataclass

from .condition_expression_candidate import (
    ConditionExpressionError,
    project_repository_condition_expression,
)
from .operator_value_expression_candidate import (
    OperatorValueExpressionCandidateError,
    project_repository_operator_value_condition,
)


REPOSITORY_OPERATOR_VALUE_MAPPING_CANDIDATE_VERSION = "0.1.0"
OWNED_REPOSITORY_WRAPPERS = frozenset({
    "ActorOrTypeOrPropertyOperatorElement",
    "InstanceOrPropertyOperatorValue",
    "UIComponentInstanceOperatorElement",
})


@dataclass(frozen=True)
class RepositoryOperatorValueProjection:
    """Canonical-ready expression plus validation-only operand traces.

    Canonical condition-expression traces retain the selected Repository rule,
    source, and span.  The more detailed linker/hash trace is consumed while
    proving the typed operand and is returned separately because it is not a
    Canonical condition field.
    """

    condition_expression: dict
    operand_traces: tuple[dict, ...]


@dataclass(frozen=True)
class RepositoryOperatorValueMappingError(ValueError):
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
    raise RepositoryOperatorValueMappingError(code, path, message)


def _source_record(node: object, source_text: str, path: str) -> dict:
    if not isinstance(node, dict):
        _fail("REPOSITORY_OPERATOR_VALUE_INVALID_RECORD", path,
              "record must be an object")
    span = node.get("span")
    source = node.get("source")
    if not isinstance(span, dict) or set(span) != {"start", "end"} or \
            type(span.get("start")) is not int or \
            type(span.get("end")) is not int or \
            span["start"] < 0 or span["end"] < span["start"]:
        _fail("REPOSITORY_OPERATOR_VALUE_INVALID_SPAN", path + "/span",
              "source span must contain ordered non-negative integers")
    if not isinstance(source, str) or span["end"] > len(source_text) or \
            source_text[span["start"]:span["end"]] != source:
        _fail("REPOSITORY_OPERATOR_VALUE_SOURCE_TAMPERED", path + "/source",
              "source must exactly match the selected span")
    return {"start": span["start"], "end": span["end"]}


def project_repository_operator_value_record(
    repository_condition: dict,
    source_text: str,
    linking: object,
    *,
    grammar_source_sha256: str,
) -> RepositoryOperatorValueProjection:
    """Project every leaf of one linked IF/WHILE Repository record.

    All leaves must be one of the three adopted operator-operand wrappers.  A
    single residual, unresolved reference, source mismatch, or unsupported
    operator/value shape rejects the complete record.
    """
    path = "/repository/condition"
    if not isinstance(repository_condition, dict) or \
            set(repository_condition) != {
                "kind", "rule_path", "span", "source", "keyword", "payload"}:
        _fail("REPOSITORY_OPERATOR_VALUE_INVALID_RECORD", path,
              "condition record shape is closed")
    kind = repository_condition.get("kind")
    expected_rule = {"if": "IfStructure", "while": "WhileStructure"}.get(kind)
    if expected_rule is None:
        _fail("REPOSITORY_OPERATOR_VALUE_CONDITION_KIND_UNSUPPORTED", path + "/kind",
              "only IF and WHILE records are selected")
    rule_path = repository_condition.get("rule_path")
    if not isinstance(rule_path, list) or not rule_path or \
            rule_path[-1] != expected_rule:
        _fail("REPOSITORY_OPERATOR_VALUE_INVALID_RECORD", path + "/rule_path",
              "condition kind and final Repository rule must agree")
    parent_span = _source_record(repository_condition, source_text, path)
    payload = repository_condition.get("payload")
    if not isinstance(payload, dict) or set(payload) != {
            "kind", "span", "source", "expression"} or \
            payload.get("kind") != "expression":
        _fail("REPOSITORY_OPERATOR_VALUE_INVALID_RECORD", path + "/payload",
              "operator value mapping requires one expression payload")
    payload_span = _source_record(payload, source_text, path + "/payload")
    if not (parent_span["start"] <= payload_span["start"] <=
            payload_span["end"] <= parent_span["end"]):
        _fail("REPOSITORY_OPERATOR_VALUE_TRACE_OUTSIDE_PARENT",
              path + "/payload/span",
              "expression payload must be contained by the condition record")

    condition_type = expected_rule.removesuffix("Structure").upper()
    operand_traces: list[dict] = []

    def project_leaf(_index: int, leaf: dict) -> dict:
        rule = leaf.get("rule") if isinstance(leaf, dict) else None
        rule_id = rule.get("rule_id") if isinstance(rule, dict) else None
        if rule_id not in OWNED_REPOSITORY_WRAPPERS:
            _fail("REPOSITORY_OPERATOR_VALUE_WRAPPER_UNSUPPORTED",
                  path + "/payload/expression",
                  "every condition leaf must use an adopted operand wrapper")
        condition = project_repository_operator_value_condition(
            rule,
            source_text,
            linking,
            condition_type=condition_type,
            grammar_source_sha256=grammar_source_sha256,
        )
        trace = condition.pop("repository_trace")
        operand_traces.append(copy.deepcopy(trace))
        return condition

    expression = project_repository_condition_expression(
        payload["expression"], source_text, project_leaf)
    return RepositoryOperatorValueProjection(
        condition_expression=expression,
        operand_traces=tuple(operand_traces),
    )


def repository_operator_value_mapping_selector_problems(
    repository_condition: dict,
    source_text: str,
    linking: object,
    *,
    grammar_source_sha256: str,
) -> tuple[str, ...]:
    """Return one stable reason code; any problem preserves the whole record."""
    try:
        project_repository_operator_value_record(
            copy.deepcopy(repository_condition),
            source_text,
            linking,
            grammar_source_sha256=grammar_source_sha256,
        )
    except (
        RepositoryOperatorValueMappingError,
        OperatorValueExpressionCandidateError,
        ConditionExpressionError,
    ) as exc:
        return (exc.code,)
    return ()


__all__ = [
    "OWNED_REPOSITORY_WRAPPERS",
    "REPOSITORY_OPERATOR_VALUE_MAPPING_CANDIDATE_VERSION",
    "RepositoryOperatorValueMappingError",
    "RepositoryOperatorValueProjection",
    "project_repository_operator_value_record",
    "repository_operator_value_mapping_selector_problems",
]
