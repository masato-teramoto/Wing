"""Active Repository-document projection for the closed Comparison predicate subset.

The mapping consumes only IF/WHILE condition records whose every expression leaf is
one scalar ``InstanceOrPropertyOperatorValue``.  Any unsupported leaf raises a
blocking error before a Canonical expression is returned, so callers can preserve
the complete record through ``RPMAP-CONDITION-STRUCTURE-PRESERVED``.
"""
from __future__ import annotations

import copy
from dataclasses import dataclass

from .condition_expression_candidate import (
    ConditionExpressionError,
    project_repository_condition_expression,
)
from .repository_comparison_mapping_candidate import (
    repository_comparison_scalar_value_problem,
)
from .semantic_values import split_money


REPOSITORY_COMPARISON_MAPPING_VERSION = "0.1.0"


@dataclass
class RepositoryComparisonMappingError(ValueError):
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
    raise RepositoryComparisonMappingError(code, path, message)


def _span(value: object, path: str) -> dict:
    if not isinstance(value, dict) or set(value) != {"start", "end"} or \
            type(value.get("start")) is not int or type(value.get("end")) is not int or \
            value["start"] < 0 or value["end"] < value["start"]:
        _fail("REPOSITORY_COMPARISON_INVALID_SPAN", path,
              "span must be ordered non-negative integers")
    return {"start": value["start"], "end": value["end"]}


def _source_record(node: dict, source_text: str, path: str) -> dict:
    span = _span(node.get("span"), path + "/span")
    source = node.get("source")
    if not isinstance(source, str) or span["end"] > len(source_text) or \
            source_text[span["start"]:span["end"]] != source:
        _fail("REPOSITORY_COMPARISON_SOURCE_TAMPERED", path,
              "source must be the exact fragment selected by span")
    return span


def _assignment_records(rule: dict, source_text: str, path: str) -> list[dict]:
    assignments = rule.get("assignments")
    if not isinstance(assignments, list):
        _fail("REPOSITORY_COMPARISON_INVALID_ASSIGNMENT", path + "/assignments",
              "assignments must be an array")
    for index, assignment in enumerate(assignments):
        apath = f"{path}/assignments/{index}"
        if not isinstance(assignment, dict) or set(assignment) != {
                "owner_rule", "rule_path", "feature", "operator", "span",
                "source", "values"}:
            _fail("REPOSITORY_COMPARISON_INVALID_ASSIGNMENT", apath,
                  "assignment shape is closed")
        owner = assignment.get("owner_rule")
        rule_path = assignment.get("rule_path")
        if not isinstance(owner, str) or not isinstance(rule_path, list) or \
                not rule_path or any(not isinstance(item, str) or not item
                                     for item in rule_path) or rule_path[-1] != owner:
            _fail("REPOSITORY_COMPARISON_INVALID_ASSIGNMENT", apath,
                  "owner_rule must close a non-empty rule_path")
        if not isinstance(assignment.get("feature"), str) or \
                assignment.get("operator") not in {"=", "+=", "?="} or \
                not isinstance(assignment.get("values"), list):
            _fail("REPOSITORY_COMPARISON_INVALID_ASSIGNMENT", apath,
                  "feature, operator, and values are invalid")
        _source_record(assignment, source_text, apath)
    return assignments


def _matching(assignments: list[dict], owner: str, feature: str) -> list[dict]:
    return [item for item in assignments
            if item["owner_rule"] == owner and item["feature"] == feature]


def _one_terminal_string(assignment: dict, source_text: str, path: str) -> tuple[str, dict]:
    values = assignment["values"]
    if len(values) != 1 or not isinstance(values[0], dict):
        _fail("REPOSITORY_COMPARISON_VALUE_CARDINALITY", path,
              "selected scalar assignment must contain exactly one fact")
    fact = values[0]
    if set(fact) != {"kind", "terminal", "value", "surface", "span"} or \
            fact.get("kind") != "terminal" or fact.get("terminal") != "STRING" or \
            not isinstance(fact.get("value"), str) or not fact["value"]:
        _fail("REPOSITORY_COMPARISON_INVALID_SCALAR", path,
              "selected scalar must be one non-empty STRING terminal")
    span = _span(fact.get("span"), path + "/span")
    if not isinstance(fact.get("surface"), str) or span["end"] > len(source_text) or \
            source_text[span["start"]:span["end"]] != fact["surface"]:
        _fail("REPOSITORY_COMPARISON_SOURCE_TAMPERED", path,
              "scalar surface must be the exact fragment selected by span")
    return fact["value"], span


def _operator(assignments: list[dict], path: str) -> str:
    operator_assignments = _matching(assignments, "OperatorValuesExpr", "operator")
    if len(operator_assignments) != 1:
        _fail("REPOSITORY_COMPARISON_OPERATOR_CARDINALITY", path,
              "OperatorValuesExpr.operator must occur exactly once")
    paths = [item["rule_path"] for item in assignments]
    owners = {item["owner_rule"] for item in assignments}
    if "OtherOperators" in owners or any("OtherOperators" in item for item in paths):
        _fail("REPOSITORY_COMPARISON_OPERATOR_UNSUPPORTED", path,
              "OtherOperators is outside the adopted Comparison contract")

    compare_count = len(_matching(assignments, "Compare", "is_are"))
    contains_count = sum(
        item["owner_rule"] == "Contains" and item["feature"] in {"has", "contains"}
        for item in assignments)
    if compare_count + contains_count != 1:
        _fail("REPOSITORY_COMPARISON_OPERATOR_CARDINALITY", path,
              "exactly one Compare or Contains rule must be selected")
    if contains_count:
        if "Negation" in owners or any("Negation" in item for item in paths):
            _fail("REPOSITORY_COMPARISON_OPERATOR_UNSUPPORTED", path,
                  "negated Contains has no adopted Canonical operator")
        return "CONTAINS"

    negated = bool(_matching(assignments, "Compare", "not"))
    ordered = (
        ("GreaterOrEqualTo", "GREATER_OR_EQUAL"),
        ("LessOrEqualTo", "LESS_OR_EQUAL"),
        ("GreaterThan", "GREATER_THAN"),
        ("LessThan", "LESS_THAN"),
        ("EqualsTo", "EQUALS"),
    )
    # The fixed Grammar's >= / <= composite rules contain the corresponding
    # Greater/Less and Equals subrules.  Specific-to-general order therefore
    # selects the outer semantic operator without treating its children as a
    # second comparison.
    selected = next((value for rule, value in ordered
                     if rule in owners or any(rule in item for item in paths)), None)
    if selected is not None:
        if negated and selected != "EQUALS":
            _fail("REPOSITORY_COMPARISON_OPERATOR_UNSUPPORTED", path,
                  "negated ordering cannot be normalized without changing meaning")
        return "NOT_EQUALS" if negated else selected
    return "NOT_EQUALS" if negated else "IS"


def project_repository_comparison_leaf(
    condition_index: int,
    repository_leaf: dict,
    condition_type: str,
    source_text: str,
) -> dict:
    """Project one closed scalar leaf into an active Canonical condition."""
    path = f"/repository/condition_expression/leaf/{condition_index}"
    if not isinstance(repository_leaf, dict) or set(repository_leaf) != {
            "kind", "span", "source", "rule"} or \
            repository_leaf.get("kind") != "condition":
        _fail("REPOSITORY_COMPARISON_INVALID_LEAF", path,
              "comparison leaf shape is closed")
    _source_record(repository_leaf, source_text, path)
    rule = repository_leaf.get("rule")
    if not isinstance(rule, dict) or set(rule) != {
            "rule_id", "span", "source", "assignments"} or \
            rule.get("rule_id") != "InstanceOrPropertyOperatorValue":
        _fail("REPOSITORY_COMPARISON_CONDITION_RULE_UNSUPPORTED", path + "/rule",
              "selected rule must be InstanceOrPropertyOperatorValue")
    _source_record(rule, source_text, path + "/rule")
    assignments = _assignment_records(rule, source_text, path + "/rule")

    rule_names = {name for item in assignments for name in item["rule_path"]}
    features = {item["feature"] for item in assignments}
    if "Modifier" in rule_names or features & {"modifier", "value_modifier"}:
        _fail("REPOSITORY_COMPARISON_MODIFIER_UNSUPPORTED", path,
              "Modifier cannot be represented by a scalar Canonical predicate")
    if "FreeExpression" in rule_names or "additional_information" in features:
        _fail("REPOSITORY_COMPARISON_ADDITIONAL_INFORMATION_UNSUPPORTED", path,
              "additional FreeExpression has no Canonical predicate slot")
    if rule_names & {"OfClassOrReferenceToLabel", "Label"}:
        _fail("REPOSITORY_COMPARISON_VALUE_METADATA_UNSUPPORTED", path,
              "value type or label metadata has no Canonical predicate slot")
    if any(item["owner_rule"] in {"ValueOrValue", "ValueAndValue"}
           and item["feature"] == "right" for item in assignments):
        _fail("REPOSITORY_COMPARISON_VALUE_CARDINALITY", path,
              "AND/OR values are outside the scalar mapping")

    subjects = [item for item in _matching(
        assignments, "InstanceOrPropertyOperatorValue", "non_ui_instance_or_property")
        if item["rule_path"] == ["InstanceOrPropertyOperatorValue"]]
    if len(subjects) != 1:
        _fail("REPOSITORY_COMPARISON_SUBJECT_CARDINALITY", path,
              "subject must occur exactly once on the selected condition rule")
    multi_values = _matching(assignments, "MultiValuesExpr", "values")
    atomic_values = _matching(assignments, "AtomicValue", "value")
    value_expressions = _matching(assignments, "OperatorValuesExpr", "valuesExpression")
    if len(multi_values) != 1 or len(atomic_values) != 1 or len(value_expressions) != 1:
        _fail("REPOSITORY_COMPARISON_VALUE_CARDINALITY", path,
              "MultiValuesExpr and AtomicValue must each occur exactly once")

    subject, _subject_span = _one_terminal_string(
        subjects[0], source_text, path + "/subject")
    value, _value_span = _one_terminal_string(
        atomic_values[0], source_text, path + "/value")
    scalar_problem = repository_comparison_scalar_value_problem(value)
    if scalar_problem is not None:
        _fail(scalar_problem, path + "/value",
              "recognized non-JPY money is outside the adopted scalar mapping")
    operator = _operator(assignments, path + "/operator")
    predicate = {"subject": subject, "operator": operator, "value": value}
    money = split_money(value)
    if money is not None and operator in {
            "GREATER_THAN", "LESS_THAN", "GREATER_OR_EQUAL", "LESS_OR_EQUAL"}:
        predicate["value"], predicate["unit"] = money
    return {"type": condition_type, "predicate": predicate}


def project_repository_comparison_condition(
    repository_condition: dict,
    source_text: str,
) -> dict:
    """Project one IF/WHILE record; reject the entire expression on any bad leaf."""
    path = "/repository/condition"
    if not isinstance(repository_condition, dict) or set(repository_condition) != {
            "kind", "rule_path", "span", "source", "keyword", "payload"}:
        _fail("REPOSITORY_COMPARISON_INVALID_CONDITION_RECORD", path,
              "condition record shape is closed")
    kind = repository_condition.get("kind")
    expected_rule = {"if": "IfStructure", "while": "WhileStructure"}.get(kind)
    if expected_rule is None:
        _fail("REPOSITORY_COMPARISON_CONDITION_KIND_UNSUPPORTED", path + "/kind",
              "only IF and WHILE records are selected")
    rule_path = repository_condition.get("rule_path")
    if not isinstance(rule_path, list) or not rule_path or rule_path[-1] != expected_rule:
        _fail("REPOSITORY_COMPARISON_INVALID_CONDITION_RECORD", path + "/rule_path",
              "condition kind and final Repository rule must agree")
    parent_span = _source_record(repository_condition, source_text, path)
    payload = repository_condition.get("payload")
    if not isinstance(payload, dict) or set(payload) != {
            "kind", "span", "source", "expression"} or payload.get("kind") != "expression":
        _fail("REPOSITORY_COMPARISON_INVALID_CONDITION_RECORD", path + "/payload",
              "comparison condition requires one expression payload")
    payload_span = _source_record(payload, source_text, path + "/payload")
    if not (parent_span["start"] <= payload_span["start"] <= payload_span["end"]
            <= parent_span["end"]):
        _fail("REPOSITORY_COMPARISON_TRACE_OUTSIDE_PARENT", path + "/payload/span",
              "expression payload must be contained by the condition record")
    condition_type = expected_rule.removesuffix("Structure").upper()

    def project_leaf(index: int, leaf: dict) -> dict:
        return project_repository_comparison_leaf(
            index, leaf, condition_type, source_text)

    return project_repository_condition_expression(
        payload["expression"], source_text, project_leaf)


def repository_comparison_mapping_selector_problems(
    repository_condition: dict,
    source_text: str,
) -> tuple[str, ...]:
    """Executable 0.4 selector: one problem means preserve the entire record."""
    try:
        project_repository_comparison_condition(
            copy.deepcopy(repository_condition), source_text)
    except (RepositoryComparisonMappingError, ConditionExpressionError) as exc:
        return (exc.code,)
    return ()
