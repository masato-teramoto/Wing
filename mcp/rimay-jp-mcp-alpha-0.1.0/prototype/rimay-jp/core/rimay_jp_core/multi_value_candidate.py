"""Isolated B5-P candidate for ``CAP-MULTI-VALUE``.

The candidate owns only value-expression cardinality, AND/OR precedence, and
explicit groups.  Comparison operators and atomic value meanings are reused as
closed callbacks/contracts; active Canonical 0.9 and product entry points are
not widened by importing this module.
"""
from __future__ import annotations

import copy
import hashlib
import json
from dataclasses import dataclass

from .comparison_operator_candidate import COMPARISON_OPERATORS
from .semantic_values import split_money


MULTI_VALUE_CANDIDATE_VERSION = "0.1.0"
MULTI_VALUE_TARGET_CANONICAL_VERSION = "1.0.0-candidate"
ACTIVE_CANONICAL_VERSION = "0.9.0"

_EN_OPERATOR_SURFACE = {
    "IS": "is",
    "EQUALS": "is equal to",
    "NOT_EQUALS": "is not",
    "GREATER_THAN": "is greater than",
    "LESS_THAN": "is less than",
    "GREATER_OR_EQUAL": "is greater or equal to",
    "LESS_OR_EQUAL": "is less than or equal to",
    "CONTAINS": "contains",
}
_JA_OPERATOR_SURFACE = {
    "IS": "である",
    "EQUALS": "と等しい",
    "NOT_EQUALS": "ではない",
    "GREATER_THAN": "より大きい",
    "LESS_THAN": "より小さい",
    "GREATER_OR_EQUAL": "以上である",
    "LESS_OR_EQUAL": "以下である",
    "CONTAINS": "を含む",
}
_CONNECTORS = {
    "en": {"and": " AND ", "or": " OR "},
    "ja": {"and": " かつ ", "or": " または "},
}


@dataclass
class MultiValueCandidateError(ValueError):
    code: str
    path: str
    message: str

    def __str__(self) -> str:
        return f"{self.code} at {self.path}: {self.message}"

    def diagnostic(self) -> dict:
        return {
            "domain": "multi_value_candidate",
            "code": self.code,
            "path": self.path,
            "message": self.message,
        }


def _fail(code: str, path: str, message: str) -> None:
    raise MultiValueCandidateError(code, path, message)


def _leaf_problem(node: object, path: str) -> None:
    if not isinstance(node, dict) or set(node) - {"kind", "value", "unit"} or \
            set(node) < {"kind", "value"} or node.get("kind") != "value":
        _fail("MULTI_VALUE_CANDIDATE_INVALID_LEAF", path,
              "leaf must contain kind, value, and optional unit")
    value = node.get("value")
    if not isinstance(value, str) or not value or value != value.strip() or \
            any(mark in value for mark in ('"', "'", "「", "」", "\n", "\r")):
        _fail("MULTI_VALUE_CANDIDATE_INVALID_VALUE", path + "/value",
              "value must be non-empty, trim-stable, and delimiter-free")
    unit = node.get("unit")
    if unit is not None and unit != "JPY":
        _fail("MULTI_VALUE_CANDIDATE_UNSUPPORTED_UNIT", path + "/unit",
              "atomic unit semantics remain closed to the adopted JPY contract")
    if unit == "JPY" and split_money(f"{value} JPY") is None:
        _fail("MULTI_VALUE_CANDIDATE_INVALID_UNIT_VALUE", path + "/value",
              "JPY leaf must contain a numeric scalar")
    recognized = split_money(value)
    if recognized is not None:
        _fail("MULTI_VALUE_CANDIDATE_EMBEDDED_UNIT", path + "/value",
              "recognized money must use the separate unit field")


def validate_multi_value_expression(expression: object, *, path: str = "/value_expression") \
        -> None:
    """Validate the closed leaf/group/AND/OR candidate tree."""
    if not isinstance(expression, dict):
        _fail("MULTI_VALUE_CANDIDATE_INVALID_NODE", path, "node must be an object")
    kind = expression.get("kind")
    if kind == "value":
        _leaf_problem(expression, path)
        return
    if kind == "group":
        if set(expression) != {"kind", "expression"}:
            _fail("MULTI_VALUE_CANDIDATE_INVALID_GROUP", path,
                  "group shape is closed")
        validate_multi_value_expression(expression["expression"], path=path + "/expression")
        return
    if kind in {"and", "or"}:
        if set(expression) != {"kind", "left", "right"}:
            _fail("MULTI_VALUE_CANDIDATE_INVALID_BINARY", path,
                  "binary shape is closed")
        validate_multi_value_expression(expression["left"], path=path + "/left")
        validate_multi_value_expression(expression["right"], path=path + "/right")
        return
    _fail("MULTI_VALUE_CANDIDATE_INVALID_NODE", path,
          f"unsupported node kind {kind!r}")


def _condition(condition: object) -> tuple[str, dict]:
    if not isinstance(condition, dict) or set(condition) != {"type", "predicate"}:
        _fail("MULTI_VALUE_CANDIDATE_INVALID_CONDITION", "/condition",
              "condition must contain only type and predicate")
    condition_type = condition.get("type")
    if condition_type not in {"IF", "WHILE"}:
        _fail("MULTI_VALUE_CANDIDATE_CONDITION_TYPE", "/condition/type",
              "candidate is limited to IF and WHILE predicates")
    predicate = condition.get("predicate")
    if not isinstance(predicate, dict) or set(predicate) != {
            "subject", "operator", "value_expression"}:
        _fail("MULTI_VALUE_CANDIDATE_INVALID_PREDICATE", "/condition/predicate",
              "predicate must contain subject, operator, and value_expression")
    subject = predicate.get("subject")
    if not isinstance(subject, str) or not subject or subject != subject.strip() or \
            any(mark in subject for mark in ('"', "「", "」", "\n", "\r")):
        _fail("MULTI_VALUE_CANDIDATE_INVALID_SUBJECT", "/condition/predicate/subject",
              "subject must be a non-empty delimiter-free string")
    if predicate.get("operator") not in COMPARISON_OPERATORS:
        _fail("MULTI_VALUE_CANDIDATE_UNSUPPORTED_OPERATOR",
              "/condition/predicate/operator",
              "operator must reuse the adopted closed comparison contract")
    validate_multi_value_expression(
        predicate["value_expression"], path="/condition/predicate/value_expression")
    return condition_type, predicate


def _render_leaf(node: dict, language: str) -> str:
    value = node["value"]
    if node.get("unit") == "JPY":
        if language == "en":
            value += " JPY"
        else:
            number = float(value)
            value = (f"{int(number):,}" if number.is_integer()
                     else format(number, ",g")) + "円"
    return f'"{value}"' if language == "en" else f"「{value}」"


def render_multi_value_expression(expression: dict, *, language: str) -> str:
    if language not in _CONNECTORS:
        _fail("MULTI_VALUE_CANDIDATE_LANGUAGE", "/language",
              f"unsupported language {language!r}")
    validate_multi_value_expression(expression)

    def visit(node: dict) -> str:
        kind = node["kind"]
        if kind == "value":
            return _render_leaf(node, language)
        if kind == "group":
            return "(" + visit(node["expression"]) + ")"
        return (
            "(" + visit(node["left"]) + _CONNECTORS[language][kind]
            + visit(node["right"]) + ")"
        )

    return visit(expression)


class _ExpressionParser:
    def __init__(self, text: str, language: str, *, source_offset: int = 0):
        self.text = text
        self.language = language
        self.position = 0
        self.source_offset = source_offset
        self.leaves: list[tuple[str, int, int]] = []

    def _quoted(self) -> dict:
        opening, closing = ('"', '"') if self.language == "en" else ("「", "」")
        if not self.text.startswith(opening, self.position):
            _fail("MULTI_VALUE_CANDIDATE_EXPECTED_VALUE", "/value_expression",
                  f"expected quoted value at offset {self.position}")
        start = self.position
        end = self.text.find(closing, start + len(opening))
        if end < 0:
            _fail("MULTI_VALUE_CANDIDATE_UNCLOSED_VALUE", "/value_expression",
                  f"unclosed value at offset {start}")
        surface = self.text[start + len(opening):end]
        self.position = end + len(closing)
        leaf = {"kind": "value", "value": surface}
        if self.language == "en":
            money = split_money(surface)
            if money is not None:
                leaf["value"], leaf["unit"] = money
        else:
            candidate = surface.replace(",", "")
            if candidate.endswith("円") and candidate[:-1].replace(".", "", 1).isdigit():
                leaf["value"] = candidate[:-1]
                leaf["unit"] = "JPY"
        _leaf_problem(leaf, "/value_expression")
        self.leaves.append((leaf["value"], self.source_offset + start,
                            self.source_offset + self.position))
        return leaf

    def parse_node(self) -> dict:
        if self.position >= len(self.text):
            _fail("MULTI_VALUE_CANDIDATE_PARSE_INCOMPLETE", "/value_expression",
                  "value expression ended before an operand")
        opening = '"' if self.language == "en" else "「"
        if self.text.startswith(opening, self.position):
            return self._quoted()
        if self.text[self.position] != "(":
            _fail("MULTI_VALUE_CANDIDATE_UNPARENTHESIZED", "/value_expression",
                  "binary and group expressions must be explicitly parenthesized")
        self.position += 1
        left = self.parse_node()
        for kind, connector in _CONNECTORS[self.language].items():
            if self.text.startswith(connector, self.position):
                self.position += len(connector)
                right = self.parse_node()
                if self.position >= len(self.text) or self.text[self.position] != ")":
                    _fail("MULTI_VALUE_CANDIDATE_UNCLOSED_GROUP", "/value_expression",
                          "binary expression must close immediately after its right operand")
                self.position += 1
                return {"kind": kind, "left": left, "right": right}
        if self.position >= len(self.text) or self.text[self.position] != ")":
            _fail("MULTI_VALUE_CANDIDATE_UNKNOWN_CONNECTOR", "/value_expression",
                  "group contains trailing or unknown connector text")
        self.position += 1
        return {"kind": "group", "expression": left}


class _RepositoryExpressionParser(_ExpressionParser):
    """Parse the fixed Grammar's precedence form while preserving explicit groups."""

    def parse_primary(self) -> dict:
        if self.position < len(self.text) and self.text[self.position] == "(":
            self.position += 1
            expression = self.parse_or()
            if self.position >= len(self.text) or self.text[self.position] != ")":
                _fail("MULTI_VALUE_CANDIDATE_REPOSITORY_UNCLOSED_GROUP",
                      "/repository/rule/valuesExpression",
                      "Repository value group is not closed")
            self.position += 1
            return {"kind": "group", "expression": expression}
        return self._quoted()

    def _consume(self, operator: str) -> bool:
        for surface in (f" {operator} ", f", {operator} "):
            if self.text.startswith(surface, self.position):
                self.position += len(surface)
                return True
        return False

    def parse_and(self) -> dict:
        expression = self.parse_primary()
        while self._consume("AND"):
            expression = {
                "kind": "and", "left": expression, "right": self.parse_primary()}
        return expression

    def parse_or(self) -> dict:
        expression = self.parse_and()
        while self._consume("OR"):
            expression = {
                "kind": "or", "left": expression, "right": self.parse_and()}
        return expression


def parse_multi_value_expression(text: str, *, language: str) -> dict:
    if language not in _CONNECTORS or not isinstance(text, str) or not text or \
            text != text.strip():
        _fail("MULTI_VALUE_CANDIDATE_AMBIGUOUS_SURFACE", "/value_expression",
              "candidate expression must be non-empty, trim-stable, and use a known language")
    parser = _ExpressionParser(text, language)
    expression = parser.parse_node()
    if parser.position != len(text):
        _fail("MULTI_VALUE_CANDIDATE_PARSE_TRAILING", "/value_expression",
              "unconsumed value-expression text remains")
    validate_multi_value_expression(expression)
    return expression


def render_multi_value_condition(condition: dict, *, language: str) -> str:
    condition_type, predicate = _condition(condition)
    expression = render_multi_value_expression(
        predicate["value_expression"], language=language)
    if language == "en":
        keyword = "If" if condition_type == "IF" else "While"
        return (f'{keyword} the "{predicate["subject"]}" '
                f'{_EN_OPERATOR_SURFACE[predicate["operator"]]} {expression}')
    if language == "ja":
        suffix = "場合" if condition_type == "IF" else "間"
        return (f'{predicate["subject"]}が{expression}'
                f'{_JA_OPERATOR_SURFACE[predicate["operator"]]}{suffix}')
    _fail("MULTI_VALUE_CANDIDATE_LANGUAGE", "/language",
          f"unsupported language {language!r}")


def parse_multi_value_condition(text: str, *, language: str) -> dict:
    if not isinstance(text, str) or not text or text != text.strip():
        _fail("MULTI_VALUE_CANDIDATE_AMBIGUOUS_SURFACE", "/condition",
              "condition must be non-empty and trim-stable")
    if language == "en":
        prefixes = (("If the \"", "IF"), ("While the \"", "WHILE"))
        match = next(((prefix, kind) for prefix, kind in prefixes
                      if text.startswith(prefix)), None)
        if match is None:
            _fail("MULTI_VALUE_CANDIDATE_CONDITION_TYPE", "/condition/type",
                  "English candidate must start with canonical If or While")
        prefix, condition_type = match
        subject_end = text.find('"', len(prefix))
        if subject_end < 0:
            _fail("MULTI_VALUE_CANDIDATE_INVALID_SUBJECT", "/condition/predicate/subject",
                  "subject quote is not closed")
        subject = text[len(prefix):subject_end]
        tail = text[subject_end + 1:]
        operator = next((item for item in sorted(
            _EN_OPERATOR_SURFACE, key=lambda key: len(_EN_OPERATOR_SURFACE[key]), reverse=True)
            if tail.startswith(" " + _EN_OPERATOR_SURFACE[item] + " ")), None)
        if operator is None:
            _fail("MULTI_VALUE_CANDIDATE_UNSUPPORTED_OPERATOR",
                  "/condition/predicate/operator", "operator surface is not canonical")
        expression_surface = tail[len(_EN_OPERATOR_SURFACE[operator]) + 2:]
    elif language == "ja":
        suffix_match = next(((operator, suffix, kind)
                             for kind, suffix in (("IF", "場合"), ("WHILE", "間"))
                             for operator in sorted(
                                 _JA_OPERATOR_SURFACE,
                                 key=lambda key: len(_JA_OPERATOR_SURFACE[key]), reverse=True)
                             if text.endswith(_JA_OPERATOR_SURFACE[operator] + suffix)), None)
        if suffix_match is None or "が" not in text:
            _fail("MULTI_VALUE_CANDIDATE_AMBIGUOUS_SURFACE", "/condition",
                  "Japanese candidate must use one canonical predicate ending")
        operator, suffix, condition_type = suffix_match
        subject, tail = text.split("が", 1)
        expression_surface = tail[:-len(_JA_OPERATOR_SURFACE[operator] + suffix)]
    else:
        _fail("MULTI_VALUE_CANDIDATE_LANGUAGE", "/language",
              f"unsupported language {language!r}")
    condition = {
        "type": condition_type,
        "predicate": {
            "subject": subject,
            "operator": operator,
            "value_expression": parse_multi_value_expression(
                expression_surface, language=language),
        },
    }
    _condition(condition)
    return condition


def migrate_scalar_condition(condition: dict) -> dict:
    """Losslessly lift one active scalar predicate into a candidate value leaf."""
    if not isinstance(condition, dict) or set(condition) != {"type", "predicate"} or \
            not isinstance(condition.get("predicate"), dict):
        _fail("MULTI_VALUE_CANDIDATE_MIGRATION_SOURCE", "/condition",
              "migration source must be one active scalar predicate")
    predicate = condition["predicate"]
    if not {"subject", "operator", "value"} <= set(predicate) or \
            set(predicate) - {"subject", "operator", "value", "unit"}:
        _fail("MULTI_VALUE_CANDIDATE_MIGRATION_SOURCE", "/condition/predicate",
              "active predicate shape is not scalar")
    leaf = {"kind": "value", "value": predicate["value"]}
    if predicate.get("unit") is not None:
        leaf["unit"] = predicate["unit"]
    candidate = {
        "type": condition["type"],
        "predicate": {
            "subject": predicate["subject"],
            "operator": predicate["operator"],
            "value_expression": leaf,
        },
    }
    _condition(candidate)
    return candidate


def rollback_scalar_condition(condition: dict) -> dict:
    """Rollback only a semantic singleton; never select a value from a tree."""
    _condition(condition)
    expression = condition["predicate"]["value_expression"]
    while expression["kind"] == "group":
        expression = expression["expression"]
    if expression["kind"] != "value":
        _fail("MULTI_VALUE_CANDIDATE_ROLLBACK_REQUIRES_QUARANTINE",
              "/condition/predicate/value_expression",
              "multi-value trees cannot roll back to one scalar without information loss")
    predicate = condition["predicate"]
    scalar = {
        "subject": predicate["subject"],
        "operator": predicate["operator"],
        "value": expression["value"],
    }
    if expression.get("unit") is not None:
        scalar["unit"] = expression["unit"]
    return {"type": condition["type"], "predicate": scalar}


def quarantine_multi_value_condition(condition: dict) -> dict:
    _condition(condition)
    payload = copy.deepcopy(condition)
    digest = hashlib.sha256(json.dumps(
        payload, ensure_ascii=False, sort_keys=True,
        separators=(",", ":")).encode("utf-8")).hexdigest()
    return {
        "kind": "RIMAY_JP_MULTI_VALUE_QUARANTINE",
        "candidate_version": MULTI_VALUE_CANDIDATE_VERSION,
        "payload_sha256": "sha256:" + digest,
        "payload": payload,
    }


def restore_multi_value_quarantine(record: dict) -> dict:
    if not isinstance(record, dict) or set(record) != {
            "kind", "candidate_version", "payload_sha256", "payload"} or \
            record.get("kind") != "RIMAY_JP_MULTI_VALUE_QUARANTINE" or \
            record.get("candidate_version") != MULTI_VALUE_CANDIDATE_VERSION:
        _fail("MULTI_VALUE_CANDIDATE_INVALID_QUARANTINE", "/quarantine",
              "quarantine envelope is invalid")
    expected = quarantine_multi_value_condition(record["payload"])["payload_sha256"]
    if record.get("payload_sha256") != expected:
        _fail("MULTI_VALUE_CANDIDATE_QUARANTINE_TAMPERED", "/quarantine/payload_sha256",
              "quarantine payload hash does not match")
    return copy.deepcopy(record["payload"])


def project_repository_multi_value_expression(rule: dict, source_text: str) -> dict:
    """Project a validated Repository rule's value source without adopting AtomicValue."""
    if not isinstance(rule, dict) or rule.get("rule_id") != \
            "InstanceOrPropertyOperatorValue" or not isinstance(rule.get("assignments"), list):
        _fail("MULTI_VALUE_CANDIDATE_REPOSITORY_RULE", "/repository/rule",
              "expected one Repository InstanceOrPropertyOperatorValue record")
    assignments = rule["assignments"]
    value_sources = [item for item in assignments
                     if isinstance(item, dict)
                     and item.get("owner_rule") == "OperatorValuesExpr"
                     and item.get("feature") == "valuesExpression"]
    if len(value_sources) != 1:
        _fail("MULTI_VALUE_CANDIDATE_REPOSITORY_CARDINALITY", "/repository/rule",
              "valuesExpression assignment must occur exactly once")
    selected = value_sources[0]
    span = selected.get("span")
    if not isinstance(span, dict) or type(span.get("start")) is not int or \
            type(span.get("end")) is not int or not 0 <= span["start"] <= span["end"] \
            <= len(source_text) or source_text[span["start"]:span["end"]] != \
            selected.get("source"):
        _fail("MULTI_VALUE_CANDIDATE_REPOSITORY_SOURCE_TAMPERED",
              "/repository/rule/valuesExpression",
              "valuesExpression source/span is not bound to the Repository source")
    parser = _RepositoryExpressionParser(
        selected["source"], "en", source_offset=span["start"])
    expression = parser.parse_or()
    if parser.position != len(selected["source"]):
        _fail("MULTI_VALUE_CANDIDATE_REPOSITORY_TRAILING",
              "/repository/rule/valuesExpression",
              "unconsumed Repository multi-value source remains")
    atomic = [item for item in assignments if isinstance(item, dict)
              and item.get("owner_rule") == "AtomicValue"
              and item.get("feature") == "value"]
    if len(atomic) != len(parser.leaves):
        _fail("MULTI_VALUE_CANDIDATE_REPOSITORY_CARDINALITY", "/repository/rule",
              "parsed leaves and AtomicValue assignments must have equal cardinality")
    for index, (assignment, (value, start, end)) in enumerate(zip(atomic, parser.leaves)):
        values = assignment.get("values")
        actual_span = assignment.get("span")
        if not isinstance(values, list) or len(values) != 1 or \
                not isinstance(values[0], dict) or values[0].get("value") != value or \
                actual_span != {"start": start, "end": end}:
            _fail("MULTI_VALUE_CANDIDATE_REPOSITORY_FACT_MISMATCH",
                  f"/repository/rule/atomic/{index}",
                  "AtomicValue fact does not match the parsed source leaf")
        if any(name in {"OfClassOrReferenceToLabel", "Label"}
               for item in assignments if isinstance(item, dict)
               for name in item.get("rule_path", [])):
            _fail("MULTI_VALUE_CANDIDATE_ATOMIC_METADATA_OUT_OF_SCOPE",
                  f"/repository/rule/atomic/{index}",
                  "AtomicValue metadata remains in the CAP-VALUE residual")
    validate_multi_value_expression(expression)
    return expression


__all__ = [
    "ACTIVE_CANONICAL_VERSION",
    "MULTI_VALUE_CANDIDATE_VERSION",
    "MULTI_VALUE_TARGET_CANONICAL_VERSION",
    "MultiValueCandidateError",
    "migrate_scalar_condition",
    "parse_multi_value_condition",
    "parse_multi_value_expression",
    "project_repository_multi_value_expression",
    "quarantine_multi_value_condition",
    "render_multi_value_condition",
    "render_multi_value_expression",
    "restore_multi_value_quarantine",
    "rollback_scalar_condition",
    "validate_multi_value_expression",
]
