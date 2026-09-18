"""Isolated B5-P candidate for ``CAP-OPERATOR-VALUE-EXPR``.

The active Canonical 1.0 predicate stores its subject as an untyped string.
This candidate keeps the three Repository operator-operand wrappers distinct,
reuses the adopted comparison and multi-value contracts, and leaves active
entry points unchanged.  Modifier, FreeExpression, and the missing
``INSTANCE_OR_CLASS_HAS_PROPERTIES::CLASS`` branch remain explicit residuals.
"""
from __future__ import annotations

import copy
import hashlib
import json
import re
from dataclasses import dataclass
from typing import Iterable

from .comparison_operator_candidate import COMPARISON_OPERATORS
from .multi_value_candidate import (
    MultiValueCandidateError,
    parse_multi_value_expression,
    project_repository_multi_value_expression,
    render_multi_value_expression,
    validate_multi_value_expression,
)


OPERATOR_VALUE_EXPRESSION_CANDIDATE_VERSION = "0.1.0"
OPERATOR_VALUE_EXPRESSION_TARGET_CANONICAL_VERSION = "1.1.0-candidate"
ACTIVE_CANONICAL_VERSION = "1.0.0"

_WRAPPERS = {
    "ActorOrTypeOrPropertyOperatorElement": "declared_reference",
    "InstanceOrPropertyOperatorValue": "instance_or_property",
    "UIComponentInstanceOperatorElement": "ui_component_instance",
}
_DECLARATION_KIND = {
    "Actor": "actor",
    "Class": "class",
    "PropertyId": "property",
    "Label": "label",
    "UIComponent": "ui_component",
}
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
_EN_OPERAND_PREFIX = {
    "actor": "actor",
    "class": "class",
    "property": "property",
}
_JA_OPERAND_PREFIX = {
    "actor": "アクター",
    "class": "クラス",
    "property": "プロパティ",
}
_QUARANTINE_KIND = "RIMAY_JP_OPERATOR_VALUE_EXPRESSION_QUARANTINE"
_SHA256_RE = re.compile(r"^sha256:[0-9a-f]{64}$")


@dataclass
class OperatorValueExpressionCandidateError(ValueError):
    code: str
    path: str
    message: str

    def __str__(self) -> str:
        return f"{self.code} at {self.path}: {self.message}"

    def diagnostic(self) -> dict:
        return {
            "domain": "operator_value_expression_candidate",
            "code": self.code,
            "path": self.path,
            "message": self.message,
        }


def _fail(code: str, path: str, message: str) -> None:
    raise OperatorValueExpressionCandidateError(code, path, message)


def _closed_text(value: object, path: str) -> str:
    if not isinstance(value, str) or not value or value != value.strip() or \
            any(mark in value for mark in ('"', "「", "」", "\n", "\r")):
        _fail("OPERATOR_VALUE_CANDIDATE_INVALID_TEXT", path,
              "value must be non-empty, trim-stable, and delimiter-free")
    return value


def validate_operator_operand(operand: object, *, path: str = "/condition/predicate/operand") \
        -> None:
    """Validate one closed typed operand without resolving omitted semantics."""
    if not isinstance(operand, dict):
        _fail("OPERATOR_VALUE_CANDIDATE_INVALID_OPERAND", path,
              "operand must be an object")
    wrapper = operand.get("wrapper")
    kind = operand.get("kind")
    if wrapper == "declared_reference":
        if set(operand) != {"wrapper", "kind", "name"} or \
                kind not in {"actor", "class", "property"}:
            _fail("OPERATOR_VALUE_CANDIDATE_INVALID_DECLARED_REFERENCE", path,
                  "declared reference must identify actor, class, or property")
        _closed_text(operand.get("name"), path + "/name")
        return
    if wrapper == "instance_or_property":
        if kind != "instance_or_property" or \
                set(operand) - {"wrapper", "kind", "name", "defined_in_type", "label"} or \
                not {"wrapper", "kind", "name"} <= set(operand):
            _fail("OPERATOR_VALUE_CANDIDATE_INVALID_INSTANCE_OR_PROPERTY", path,
                  "instance/property disjunction has a closed shape")
        _closed_text(operand.get("name"), path + "/name")
        defined = operand.get("defined_in_type")
        if defined is not None:
            if not isinstance(defined, dict) or set(defined) != {"kind", "name"} or \
                    defined.get("kind") not in {"class", "label"}:
                _fail("OPERATOR_VALUE_CANDIDATE_INVALID_TYPE_REFERENCE",
                      path + "/defined_in_type",
                      "type reference must resolve to one class or label")
            _closed_text(defined.get("name"), path + "/defined_in_type/name")
        if "label" in operand:
            _closed_text(operand.get("label"), path + "/label")
        return
    if wrapper == "ui_component_instance":
        if set(operand) != {"wrapper", "kind", "name", "component_type"} or \
                kind != "ui_component_instance":
            _fail("OPERATOR_VALUE_CANDIDATE_INVALID_UI_COMPONENT", path,
                  "UI component operand must preserve instance and component type")
        _closed_text(operand.get("name"), path + "/name")
        _closed_text(operand.get("component_type"), path + "/component_type")
        return
    _fail("OPERATOR_VALUE_CANDIDATE_UNSUPPORTED_WRAPPER", path + "/wrapper",
          f"unsupported operand wrapper {wrapper!r}")


def validate_operator_value_condition(condition: object) -> None:
    allowed = {"type", "predicate", "repository_trace"}
    if not isinstance(condition, dict) or set(condition) - allowed or \
            not {"type", "predicate"} <= set(condition):
        _fail("OPERATOR_VALUE_CANDIDATE_INVALID_CONDITION", "/condition",
              "condition must contain type, predicate, and optional Repository trace")
    if condition.get("type") not in {"IF", "WHILE"}:
        _fail("OPERATOR_VALUE_CANDIDATE_CONDITION_TYPE", "/condition/type",
              "candidate is limited to IF and WHILE")
    predicate = condition.get("predicate")
    if not isinstance(predicate, dict) or set(predicate) != {
            "operand", "operator", "value_expression"}:
        _fail("OPERATOR_VALUE_CANDIDATE_INVALID_PREDICATE", "/condition/predicate",
              "predicate must contain operand, operator, and value_expression")
    validate_operator_operand(predicate["operand"])
    if predicate.get("operator") not in COMPARISON_OPERATORS:
        _fail("OPERATOR_VALUE_CANDIDATE_UNSUPPORTED_OPERATOR",
              "/condition/predicate/operator",
              "operator must reuse the adopted comparison contract")
    try:
        validate_multi_value_expression(
            predicate["value_expression"],
            path="/condition/predicate/value_expression")
    except MultiValueCandidateError as exc:
        _fail("OPERATOR_VALUE_CANDIDATE_VALUE_EXPRESSION",
              exc.path, str(exc))
    if "repository_trace" in condition:
        trace = condition["repository_trace"]
        required = {"repository_rule_id", "source_span", "source",
                    "grammar_source_sha256", "operand_resolution"}
        if not isinstance(trace, dict) or set(trace) != required or \
                trace.get("repository_rule_id") not in _WRAPPERS:
            _fail("OPERATOR_VALUE_CANDIDATE_INVALID_REPOSITORY_TRACE",
                  "/condition/repository_trace", "Repository trace shape is closed")
        _span_source(trace.get("source_span"), trace.get("source"), None,
                     "/condition/repository_trace")
        grammar_source_sha256 = trace.get("grammar_source_sha256")
        if not isinstance(grammar_source_sha256, str) or \
                _SHA256_RE.fullmatch(grammar_source_sha256) is None:
            _fail("OPERATOR_VALUE_CANDIDATE_INVALID_REPOSITORY_TRACE",
                  "/condition/repository_trace/grammar_source_sha256",
                  "Grammar source signature must be sha256 followed by 64 lowercase hex digits")
        resolution = trace.get("operand_resolution")
        if not isinstance(resolution, dict) or set(resolution) != {
                "status", "symbol_id", "declaration_rule"}:
            _fail("OPERATOR_VALUE_CANDIDATE_INVALID_REPOSITORY_TRACE",
                  "/condition/repository_trace/operand_resolution",
                  "operand resolution shape is closed")
        wrapper = trace["repository_rule_id"]
        operand = predicate["operand"]
        status = resolution.get("status")
        symbol_id = resolution.get("symbol_id")
        declaration_rule = resolution.get("declaration_rule")
        if wrapper == "ActorOrTypeOrPropertyOperatorElement":
            expected_rule = {
                "actor": "Actor", "class": "Class", "property": "PropertyId",
            }.get(operand.get("kind"))
            if operand.get("wrapper") != "declared_reference" or \
                    status != "resolved" or expected_rule is None or \
                    declaration_rule != expected_rule or \
                    not isinstance(symbol_id, str) or not symbol_id.strip():
                _fail("OPERATOR_VALUE_CANDIDATE_INVALID_REPOSITORY_TRACE",
                      "/condition/repository_trace/operand_resolution",
                      "declared-reference trace must match its resolved declaration identity")
        elif wrapper == "InstanceOrPropertyOperatorValue":
            if operand.get("wrapper") != "instance_or_property" or \
                    status != "explicit_disjunction" or symbol_id is not None or \
                    declaration_rule is not None:
                _fail("OPERATOR_VALUE_CANDIDATE_INVALID_REPOSITORY_TRACE",
                      "/condition/repository_trace/operand_resolution",
                      "instance/property trace must preserve an unresolved explicit disjunction")
        elif operand.get("wrapper") != "ui_component_instance" or \
                status != "resolved" or declaration_rule != "UIComponent" or \
                not isinstance(symbol_id, str) or not symbol_id.strip():
            _fail("OPERATOR_VALUE_CANDIDATE_INVALID_REPOSITORY_TRACE",
                  "/condition/repository_trace/operand_resolution",
                  "UI-component trace must match its resolved UIComponent identity")


def _render_operand(operand: dict, language: str) -> str:
    validate_operator_operand(operand)
    wrapper = operand["wrapper"]
    if wrapper == "declared_reference":
        if language == "en":
            return (_EN_OPERAND_PREFIX[operand["kind"]] + ' "'
                    + operand["name"] + '"')
        return _JA_OPERAND_PREFIX[operand["kind"]] + "「" + operand["name"] + "」"
    if wrapper == "instance_or_property":
        if language == "en":
            rendered = f'instance-or-property "{operand["name"]}"'
            if "defined_in_type" in operand:
                defined = operand["defined_in_type"]
                rendered += f' of {defined["kind"]} "{defined["name"]}"'
            if "label" in operand:
                rendered += f' labelled "{operand["label"]}"'
            return rendered
        rendered = f'インスタンス／プロパティ「{operand["name"]}」'
        details = []
        if "defined_in_type" in operand:
            defined = operand["defined_in_type"]
            details.append(
                ("クラス" if defined["kind"] == "class" else "ラベル")
                + f'=「{defined["name"]}」')
        if "label" in operand:
            details.append(f'参照名=「{operand["label"]}」')
        return rendered + (("（" + "；".join(details) + "）") if details else "")
    if language == "en":
        return (f'UI-component "{operand["name"]}" '
                f'of type "{operand["component_type"]}"')
    return (f'UIコンポーネント「{operand["name"]}」'
            f'（型=「{operand["component_type"]}」）')


def _parse_quoted(text: str, position: int, opening: str, closing: str,
                  path: str) -> tuple[str, int]:
    if not text.startswith(opening, position):
        _fail("OPERATOR_VALUE_CANDIDATE_AMBIGUOUS_OPERAND", path,
              f"expected {opening!r} at offset {position}")
    end = text.find(closing, position + len(opening))
    if end < 0:
        _fail("OPERATOR_VALUE_CANDIDATE_AMBIGUOUS_OPERAND", path,
              "operand delimiter is not closed")
    value = text[position + len(opening):end]
    _closed_text(value, path)
    return value, end + len(closing)


def _parse_operand_en(text: str) -> dict:
    for kind, prefix in _EN_OPERAND_PREFIX.items():
        marker = prefix + ' "'
        if text.startswith(marker):
            name, end = _parse_quoted(text, len(prefix) + 1, '"', '"',
                                      "/condition/predicate/operand/name")
            if end != len(text):
                _fail("OPERATOR_VALUE_CANDIDATE_AMBIGUOUS_OPERAND",
                      "/condition/predicate/operand", "trailing operand text remains")
            return {"wrapper": "declared_reference", "kind": kind, "name": name}
    prefix = 'instance-or-property "'
    if text.startswith(prefix):
        name, position = _parse_quoted(text, len("instance-or-property "), '"', '"',
                                       "/condition/predicate/operand/name")
        operand = {"wrapper": "instance_or_property",
                   "kind": "instance_or_property", "name": name}
        if text.startswith(" of ", position):
            position += 4
            kind = next((item for item in ("class", "label")
                         if text.startswith(item + ' "', position)), None)
            if kind is None:
                _fail("OPERATOR_VALUE_CANDIDATE_INVALID_TYPE_REFERENCE",
                      "/condition/predicate/operand/defined_in_type",
                      "type reference must name class or label")
            position += len(kind) + 1
            value, position = _parse_quoted(
                text, position, '"', '"',
                "/condition/predicate/operand/defined_in_type/name")
            operand["defined_in_type"] = {"kind": kind, "name": value}
        if text.startswith(" labelled ", position):
            position += len(" labelled ")
            operand["label"], position = _parse_quoted(
                text, position, '"', '"', "/condition/predicate/operand/label")
        if position != len(text):
            _fail("OPERATOR_VALUE_CANDIDATE_AMBIGUOUS_OPERAND",
                  "/condition/predicate/operand", "trailing operand text remains")
        return operand
    prefix = 'UI-component "'
    if text.startswith(prefix):
        name, position = _parse_quoted(text, len("UI-component "), '"', '"',
                                       "/condition/predicate/operand/name")
        marker = ' of type "'
        if not text.startswith(marker, position):
            _fail("OPERATOR_VALUE_CANDIDATE_INVALID_UI_COMPONENT",
                  "/condition/predicate/operand/component_type",
                  "UI component type is required")
        component_type, position = _parse_quoted(
            text, position + len(" of type "), '"', '"',
            "/condition/predicate/operand/component_type")
        if position != len(text):
            _fail("OPERATOR_VALUE_CANDIDATE_AMBIGUOUS_OPERAND",
                  "/condition/predicate/operand", "trailing operand text remains")
        return {"wrapper": "ui_component_instance", "kind": "ui_component_instance",
                "name": name, "component_type": component_type}
    _fail("OPERATOR_VALUE_CANDIDATE_AMBIGUOUS_OPERAND",
          "/condition/predicate/operand", "unknown English operand surface")


def _parse_operand_ja(text: str) -> dict:
    for kind, prefix in _JA_OPERAND_PREFIX.items():
        marker = prefix + "「"
        if text.startswith(marker):
            name, end = _parse_quoted(text, len(prefix), "「", "」",
                                      "/condition/predicate/operand/name")
            if end != len(text):
                _fail("OPERATOR_VALUE_CANDIDATE_AMBIGUOUS_OPERAND",
                      "/condition/predicate/operand", "trailing operand text remains")
            return {"wrapper": "declared_reference", "kind": kind, "name": name}
    prefix = "インスタンス／プロパティ"
    if text.startswith(prefix + "「"):
        name, position = _parse_quoted(text, len(prefix), "「", "」",
                                       "/condition/predicate/operand/name")
        operand = {"wrapper": "instance_or_property",
                   "kind": "instance_or_property", "name": name}
        if position < len(text):
            if not text.startswith("（", position) or not text.endswith("）"):
                _fail("OPERATOR_VALUE_CANDIDATE_AMBIGUOUS_OPERAND",
                      "/condition/predicate/operand", "Japanese details are malformed")
            details = text[position + 1:-1].split("；")
            for detail in details:
                if detail.startswith(("クラス=", "ラベル=")):
                    kind = "class" if detail.startswith("クラス=") else "label"
                    offset = len("クラス=") if kind == "class" else len("ラベル=")
                    value, end = _parse_quoted(
                        detail, offset, "「", "」",
                        "/condition/predicate/operand/defined_in_type/name")
                    if end != len(detail) or "defined_in_type" in operand:
                        _fail("OPERATOR_VALUE_CANDIDATE_AMBIGUOUS_OPERAND",
                              "/condition/predicate/operand", "duplicate type detail")
                    operand["defined_in_type"] = {"kind": kind, "name": value}
                elif detail.startswith("参照名="):
                    value, end = _parse_quoted(
                        detail, len("参照名="), "「", "」",
                        "/condition/predicate/operand/label")
                    if end != len(detail) or "label" in operand:
                        _fail("OPERATOR_VALUE_CANDIDATE_AMBIGUOUS_OPERAND",
                              "/condition/predicate/operand", "duplicate label detail")
                    operand["label"] = value
                else:
                    _fail("OPERATOR_VALUE_CANDIDATE_AMBIGUOUS_OPERAND",
                          "/condition/predicate/operand", "unknown Japanese detail")
        return operand
    prefix = "UIコンポーネント"
    if text.startswith(prefix + "「"):
        name, position = _parse_quoted(text, len(prefix), "「", "」",
                                       "/condition/predicate/operand/name")
        marker = "（型=「"
        if not text.startswith(marker, position) or not text.endswith("）"):
            _fail("OPERATOR_VALUE_CANDIDATE_INVALID_UI_COMPONENT",
                  "/condition/predicate/operand/component_type", "UI type is required")
        component_type, end = _parse_quoted(
            text, position + len("（型="), "「", "」",
            "/condition/predicate/operand/component_type")
        if end != len(text) - 1:
            _fail("OPERATOR_VALUE_CANDIDATE_AMBIGUOUS_OPERAND",
                  "/condition/predicate/operand", "trailing UI operand text remains")
        return {"wrapper": "ui_component_instance", "kind": "ui_component_instance",
                "name": name, "component_type": component_type}
    _fail("OPERATOR_VALUE_CANDIDATE_AMBIGUOUS_OPERAND",
          "/condition/predicate/operand", "unknown Japanese operand surface")


def render_operator_value_condition(condition: dict, *, language: str) -> str:
    validate_operator_value_condition(condition)
    predicate = condition["predicate"]
    operand = _render_operand(predicate["operand"], language)
    expression = render_multi_value_expression(
        predicate["value_expression"], language=language)
    if language == "en":
        keyword = "If" if condition["type"] == "IF" else "While"
        return f'{keyword} {operand} {_EN_OPERATOR_SURFACE[predicate["operator"]]} {expression}'
    if language == "ja":
        suffix = "場合" if condition["type"] == "IF" else "間"
        return f'{operand}が{expression}{_JA_OPERATOR_SURFACE[predicate["operator"]]}{suffix}'
    _fail("OPERATOR_VALUE_CANDIDATE_LANGUAGE", "/language",
          f"unsupported language {language!r}")


def parse_operator_value_condition(text: str, *, language: str) -> dict:
    if not isinstance(text, str) or not text or text != text.strip():
        _fail("OPERATOR_VALUE_CANDIDATE_AMBIGUOUS_SURFACE", "/condition",
              "condition must be non-empty and trim-stable")
    if language == "en":
        prefix = next((item for item in (("If ", "IF"), ("While ", "WHILE"))
                       if text.startswith(item[0])), None)
        if prefix is None:
            _fail("OPERATOR_VALUE_CANDIDATE_CONDITION_TYPE", "/condition/type",
                  "English condition must start with If or While")
        marker, condition_type = prefix
        tail = text[len(marker):]
        matches = []
        value_errors: list[MultiValueCandidateError] = []
        for candidate_operator, surface in sorted(
                _EN_OPERATOR_SURFACE.items(),
                key=lambda item: len(item[1]), reverse=True):
            separator = " " + surface + " "
            position = tail.find(separator)
            while position >= 0:
                try:
                    candidate_operand = _parse_operand_en(tail[:position])
                except OperatorValueExpressionCandidateError:
                    position = tail.find(separator, position + 1)
                    continue
                try:
                    candidate_expression = parse_multi_value_expression(
                        tail[position + len(separator):], language="en")
                except MultiValueCandidateError as exc:
                    value_errors.append(exc)
                else:
                    matches.append((candidate_operator, candidate_operand,
                                    candidate_expression))
                position = tail.find(separator, position + 1)
        if not matches:
            if value_errors:
                error = value_errors[0]
                _fail("OPERATOR_VALUE_CANDIDATE_VALUE_EXPRESSION",
                      error.path, str(error))
            _fail("OPERATOR_VALUE_CANDIDATE_UNSUPPORTED_OPERATOR",
                  "/condition/predicate/operator", "canonical operator surface is absent")
        if len(matches) != 1:
            _fail("OPERATOR_VALUE_CANDIDATE_AMBIGUOUS_SURFACE", "/condition",
                  "English condition has multiple complete interpretations")
        operator, operand, expression = matches[0]
    elif language == "ja":
        suffix_match = next(((operator, suffix, kind)
                             for kind, suffix in (("IF", "場合"), ("WHILE", "間"))
                             for operator, surface in sorted(
                                 _JA_OPERATOR_SURFACE.items(),
                                 key=lambda item: len(item[1]), reverse=True)
                             if text.endswith(surface + suffix)), None)
        if suffix_match is None:
            _fail("OPERATOR_VALUE_CANDIDATE_UNSUPPORTED_OPERATOR",
                  "/condition/predicate/operator", "canonical Japanese ending is absent")
        operator, suffix, condition_type = suffix_match
        ending = _JA_OPERATOR_SURFACE[operator] + suffix
        body = text[:-len(ending)]
        matches = []
        value_errors = []
        position = body.find("が")
        while position >= 0:
            try:
                candidate_operand = _parse_operand_ja(body[:position])
            except OperatorValueExpressionCandidateError:
                position = body.find("が", position + 1)
                continue
            try:
                candidate_expression = parse_multi_value_expression(
                    body[position + 1:], language="ja")
            except MultiValueCandidateError as exc:
                value_errors.append(exc)
            else:
                matches.append((candidate_operand, candidate_expression))
            position = body.find("が", position + 1)
        if not matches:
            if value_errors:
                error = value_errors[0]
                _fail("OPERATOR_VALUE_CANDIDATE_VALUE_EXPRESSION",
                      error.path, str(error))
            _fail("OPERATOR_VALUE_CANDIDATE_AMBIGUOUS_SURFACE", "/condition",
                  "Japanese operand/value delimiter is absent")
        if len(matches) != 1:
            _fail("OPERATOR_VALUE_CANDIDATE_AMBIGUOUS_SURFACE", "/condition",
                  "Japanese condition has multiple complete interpretations")
        operand, expression = matches[0]
    else:
        _fail("OPERATOR_VALUE_CANDIDATE_LANGUAGE", "/language",
              f"unsupported language {language!r}")
    condition = {"type": condition_type, "predicate": {
        "operand": operand, "operator": operator, "value_expression": expression}}
    validate_operator_value_condition(condition)
    return condition


def operator_value_semantics(condition: dict) -> dict:
    """Return the trace-free meaning used for English/Japanese comparison."""
    validate_operator_value_condition(condition)
    return {key: copy.deepcopy(value) for key, value in condition.items()
            if key != "repository_trace"}


def _assignments(rule: dict, owner: str, feature: str) -> list[dict]:
    return [item for item in rule.get("assignments", [])
            if isinstance(item, dict) and item.get("owner_rule") == owner
            and item.get("feature") == feature]


def _one_assignment(rule: dict, owner: str, feature: str, path: str) -> dict:
    candidates = _assignments(rule, owner, feature)
    if len(candidates) != 1:
        _fail("OPERATOR_VALUE_CANDIDATE_REPOSITORY_CARDINALITY", path,
              f"{owner}.{feature} must occur exactly once")
    return candidates[0]


def _assignment_value(assignment: dict, path: str, *, kind: str | None = None) -> str:
    values = assignment.get("values")
    candidates = [item.get("value") for item in values or []
                  if isinstance(item, dict) and (kind is None or item.get("kind") == kind)
                  and isinstance(item.get("value"), str)]
    if not candidates:
        _fail("OPERATOR_VALUE_CANDIDATE_REPOSITORY_FACT", path,
              "assignment has no required decoded value")
    return candidates[0]


def _span_source(span: object, source: object, source_text: str | None,
                 path: str) -> dict:
    if not isinstance(span, dict) or set(span) != {"start", "end"} or \
            type(span.get("start")) is not int or type(span.get("end")) is not int or \
            span["start"] < 0 or span["end"] < span["start"]:
        _fail("OPERATOR_VALUE_CANDIDATE_REPOSITORY_SPAN", path + "/source_span",
              "source span must be ordered integers")
    if not isinstance(source, str):
        _fail("OPERATOR_VALUE_CANDIDATE_REPOSITORY_SOURCE_TAMPERED", path + "/source",
              "source must be a string")
    if source_text is not None and (span["end"] > len(source_text) or
                                    source_text[span["start"]:span["end"]] != source):
        _fail("OPERATOR_VALUE_CANDIDATE_REPOSITORY_SOURCE_TAMPERED", path + "/source",
              "source does not match its Repository span")
    return {"start": span["start"], "end": span["end"]}


def _resolved_symbol(assignment: dict, linking: object, expected: Iterable[str],
                     path: str) -> dict:
    references = getattr(linking, "references", ())
    symbols = {item.get("symbol_id"): item for item in getattr(linking, "symbols", ())}
    span = assignment.get("span")
    surface = assignment.get("source")
    matches = [item for item in references if item.get("span") == span
               and item.get("surface") == surface and item.get("status") == "resolved"]
    if len(matches) != 1:
        _fail("OPERATOR_VALUE_CANDIDATE_REFERENCE_UNRESOLVED", path,
              "operand reference must resolve exactly once")
    symbol = symbols.get(matches[0].get("resolved_symbol_id"))
    if not isinstance(symbol, dict) or symbol.get("declaration_rule") not in set(expected):
        _fail("OPERATOR_VALUE_CANDIDATE_REFERENCE_KIND", path,
              "resolved declaration kind is outside the wrapper contract")
    return symbol


def _operator_from_rule(rule: dict) -> str:
    paths = [item.get("rule_path", []) for item in rule.get("assignments", [])
             if isinstance(item, dict)]
    present = lambda name: any(name in path for path in paths)
    if present("OtherOperators"):
        _fail("OPERATOR_VALUE_CANDIDATE_OTHER_OPERATOR_DEFERRED",
              "/repository/rule/operator",
              "OtherOperators semantics are outside the adopted comparison contract")
    if present("Contains"):
        if present("Negation"):
            _fail("OPERATOR_VALUE_CANDIDATE_NEGATION_DEFERRED",
                  "/repository/rule/operator",
                  "negated Contains remains a separate capability")
        return "CONTAINS"
    if not present("Compare"):
        _fail("OPERATOR_VALUE_CANDIDATE_REPOSITORY_OPERATOR",
              "/repository/rule/operator", "typed comparison rule is absent")
    negated = bool(_assignments(rule, "Compare", "not"))
    for name, operator in (
        ("GreaterOrEqualTo", "GREATER_OR_EQUAL"),
        ("LessOrEqualTo", "LESS_OR_EQUAL"),
        ("GreaterThan", "GREATER_THAN"),
        ("LessThan", "LESS_THAN"),
        ("EqualsTo", "EQUALS"),
    ):
        if present(name):
            if negated and name != "EqualsTo":
                _fail("OPERATOR_VALUE_CANDIDATE_NEGATION_DEFERRED",
                      "/repository/rule/operator",
                      "negated ordering has no adopted operator")
            return "NOT_EQUALS" if negated else operator
    return "NOT_EQUALS" if negated else "IS"


def _repository_operand(rule: dict, linking: object) -> tuple[dict, dict]:
    rule_id = rule["rule_id"]
    if rule_id == "ActorOrTypeOrPropertyOperatorElement":
        assignment = _one_assignment(
            rule, rule_id, "actor_or_type_or_property",
            "/repository/rule/actor_or_type_or_property")
        symbol = _resolved_symbol(
            assignment, linking, ("Actor", "Class", "PropertyId"),
            "/repository/rule/actor_or_type_or_property")
        kind = _DECLARATION_KIND[symbol["declaration_rule"]]
        return ({"wrapper": "declared_reference", "kind": kind,
                 "name": symbol["qualified_name"]},
                {"status": "resolved", "symbol_id": symbol["symbol_id"],
                 "declaration_rule": symbol["declaration_rule"]})
    if rule_id == "InstanceOrPropertyOperatorValue":
        assignment = _one_assignment(
            rule, rule_id, "non_ui_instance_or_property",
            "/repository/rule/non_ui_instance_or_property")
        operand = {"wrapper": "instance_or_property",
                   "kind": "instance_or_property",
                   "name": _assignment_value(
                       assignment, "/repository/rule/non_ui_instance_or_property",
                       kind="terminal")}
        resolution = {"status": "explicit_disjunction",
                      "declaration_rule": None, "symbol_id": None}
        defined = _assignments(rule, rule_id, "defined_in_type")
        if len(defined) > 1:
            _fail("OPERATOR_VALUE_CANDIDATE_REPOSITORY_CARDINALITY",
                  "/repository/rule/defined_in_type", "at most one type is allowed")
        if defined:
            type_assignment = _one_assignment(
                rule, "OfClassOrReferenceToLabel", "of_type",
                "/repository/rule/defined_in_type")
            symbol = _resolved_symbol(
                type_assignment, linking, ("Class", "Label"),
                "/repository/rule/defined_in_type")
            operand["defined_in_type"] = {
                "kind": _DECLARATION_KIND[symbol["declaration_rule"]],
                "name": symbol["qualified_name"],
            }
        labels = _assignments(rule, "Label", "name")
        if len(labels) > 1:
            _fail("OPERATOR_VALUE_CANDIDATE_REPOSITORY_CARDINALITY",
                  "/repository/rule/label", "at most one label is allowed")
        if labels:
            operand["label"] = _assignment_value(
                labels[0], "/repository/rule/label", kind="terminal")
        return operand, resolution
    assignment = _one_assignment(
        rule, rule_id, "ui_component_name", "/repository/rule/ui_component_name")
    type_assignment = _one_assignment(
        rule, rule_id, "ui_component_type", "/repository/rule/ui_component_type")
    symbol = _resolved_symbol(
        type_assignment, linking, ("UIComponent",),
        "/repository/rule/ui_component_type")
    return ({"wrapper": "ui_component_instance", "kind": "ui_component_instance",
             "name": _assignment_value(
                 assignment, "/repository/rule/ui_component_name", kind="terminal"),
             "component_type": symbol["qualified_name"]},
            {"status": "resolved", "symbol_id": symbol["symbol_id"],
             "declaration_rule": symbol["declaration_rule"]})


def project_repository_operator_value_condition(
    rule: dict,
    source_text: str,
    linking: object,
    *,
    condition_type: str,
    grammar_source_sha256: str,
) -> dict:
    """Project one linked Repository wrapper into the isolated typed candidate."""
    if not isinstance(rule, dict) or rule.get("rule_id") not in _WRAPPERS or \
            not isinstance(rule.get("assignments"), list):
        _fail("OPERATOR_VALUE_CANDIDATE_REPOSITORY_RULE", "/repository/rule",
              "expected one of the three owned Repository operator wrappers")
    _span_source(rule.get("span"), rule.get("source"), source_text, "/repository/rule")
    if condition_type not in {"IF", "WHILE"}:
        _fail("OPERATOR_VALUE_CANDIDATE_CONDITION_TYPE", "/condition/type",
              "Repository candidate is limited to IF and WHILE")
    if not getattr(linking, "succeeded", False):
        _fail("OPERATOR_VALUE_CANDIDATE_LINKING_REQUIRED", "/repository/linking",
              "successful semantic linking is required")
    if getattr(linking, "grammar_source_sha256", None) != grammar_source_sha256:
        _fail("OPERATOR_VALUE_CANDIDATE_GRAMMAR_BINDING", "/repository/linking",
              "linking and caller Grammar signatures differ")
    if any(item.get("owner_rule") in _WRAPPERS and item.get("feature") == "modifier"
           for item in rule["assignments"] if isinstance(item, dict)):
        _fail("OPERATOR_VALUE_CANDIDATE_MODIFIER_DEFERRED",
              "/repository/rule/modifier", "operand Modifier remains CAP-MODIFIER")
    if _assignments(rule, "OperatorValuesExpr", "value_modifier"):
        _fail("OPERATOR_VALUE_CANDIDATE_MODIFIER_DEFERRED",
              "/repository/rule/value_modifier", "value Modifier remains CAP-MODIFIER")
    if _assignments(rule, "OperatorValuesExpr", "additional_information"):
        _fail("OPERATOR_VALUE_CANDIDATE_FREE_EXPRESSION_DEFERRED",
              "/repository/rule/additional_information",
              "additional FreeExpression remains a separate capability")

    operand, resolution = _repository_operand(rule, linking)
    normalized = copy.deepcopy(rule)
    # The adopted multi-value projector validates the common assignment shape;
    # wrapper identity is validated above and is not allowed to leak into it.
    # Operand-level OfClass/Label metadata must not be mistaken for AtomicValue
    # metadata by that deliberately narrower projector.
    normalized["rule_id"] = "InstanceOrPropertyOperatorValue"
    normalized["assignments"] = [
        item for item in normalized["assignments"]
        if "OperatorValuesExpr" in item.get("rule_path", [])
    ]
    try:
        expression = project_repository_multi_value_expression(normalized, source_text)
    except MultiValueCandidateError as exc:
        _fail("OPERATOR_VALUE_CANDIDATE_VALUE_EXPRESSION", exc.path, str(exc))
    condition = {
        "type": condition_type,
        "predicate": {
            "operand": operand,
            "operator": _operator_from_rule(rule),
            "value_expression": expression,
        },
        "repository_trace": {
            "repository_rule_id": rule["rule_id"],
            "source_span": copy.deepcopy(rule["span"]),
            "source": rule["source"],
            "grammar_source_sha256": grammar_source_sha256,
            "operand_resolution": resolution,
        },
    }
    validate_operator_value_condition(condition)
    return condition


def migrate_active_condition(condition: dict, operand: dict) -> dict:
    """Lift active 1.0 data only after a caller supplies explicit operand type."""
    validate_operator_operand(operand)
    if not isinstance(condition, dict) or set(condition) != {"type", "predicate"} or \
            not isinstance(condition.get("predicate"), dict):
        _fail("OPERATOR_VALUE_CANDIDATE_MIGRATION_SOURCE", "/condition",
              "source must be one active IF/WHILE condition")
    predicate = condition["predicate"]
    if condition.get("type") not in {"IF", "WHILE"} or \
            predicate.get("operator") not in COMPARISON_OPERATORS or \
            not isinstance(predicate.get("subject"), str):
        _fail("OPERATOR_VALUE_CANDIDATE_MIGRATION_SOURCE", "/condition",
              "active condition is outside the adopted predicate boundary")
    if operand.get("name") != predicate["subject"]:
        _fail("OPERATOR_VALUE_CANDIDATE_MIGRATION_SUBJECT_MISMATCH",
              "/condition/predicate/operand/name",
              "explicit operand must preserve the active subject")
    if "value_expression" in predicate:
        if set(predicate) != {"subject", "operator", "value_expression"}:
            _fail("OPERATOR_VALUE_CANDIDATE_MIGRATION_SOURCE", "/condition/predicate",
                  "active multi-value predicate shape is closed")
        expression = copy.deepcopy(predicate["value_expression"])
    else:
        if not {"subject", "operator", "value"} <= set(predicate) or \
                set(predicate) - {"subject", "operator", "value", "unit"}:
            _fail("OPERATOR_VALUE_CANDIDATE_MIGRATION_SOURCE", "/condition/predicate",
                  "active scalar predicate shape is closed")
        expression = {"kind": "value", "value": predicate["value"]}
        if "unit" in predicate:
            expression["unit"] = predicate["unit"]
    candidate = {"type": condition["type"], "predicate": {
        "operand": copy.deepcopy(operand), "operator": predicate["operator"],
        "value_expression": expression}}
    validate_operator_value_condition(candidate)
    return candidate


def rollback_active_condition(condition: dict) -> dict:
    validate_operator_value_condition(condition)
    _fail("OPERATOR_VALUE_CANDIDATE_ROLLBACK_REQUIRES_QUARANTINE", "/condition",
          "active Canonical cannot preserve operand wrapper and declaration kind")


def quarantine_operator_value_condition(condition: dict) -> dict:
    validate_operator_value_condition(condition)
    payload = copy.deepcopy(condition)
    digest = hashlib.sha256(json.dumps(
        payload, ensure_ascii=False, sort_keys=True,
        separators=(",", ":")).encode("utf-8")).hexdigest()
    return {
        "kind": _QUARANTINE_KIND,
        "candidate_version": OPERATOR_VALUE_EXPRESSION_CANDIDATE_VERSION,
        "payload_sha256": "sha256:" + digest,
        "payload": payload,
    }


def restore_operator_value_quarantine(record: dict) -> dict:
    if not isinstance(record, dict) or set(record) != {
            "kind", "candidate_version", "payload_sha256", "payload"} or \
            record.get("kind") != _QUARANTINE_KIND or \
            record.get("candidate_version") != OPERATOR_VALUE_EXPRESSION_CANDIDATE_VERSION:
        _fail("OPERATOR_VALUE_CANDIDATE_INVALID_QUARANTINE", "/quarantine",
              "quarantine envelope is invalid")
    expected = quarantine_operator_value_condition(record["payload"])["payload_sha256"]
    if record.get("payload_sha256") != expected:
        _fail("OPERATOR_VALUE_CANDIDATE_QUARANTINE_TAMPERED",
              "/quarantine/payload_sha256", "quarantine payload hash does not match")
    return copy.deepcopy(record["payload"])


__all__ = [
    "ACTIVE_CANONICAL_VERSION",
    "OPERATOR_VALUE_EXPRESSION_CANDIDATE_VERSION",
    "OPERATOR_VALUE_EXPRESSION_TARGET_CANONICAL_VERSION",
    "OperatorValueExpressionCandidateError",
    "migrate_active_condition",
    "operator_value_semantics",
    "parse_operator_value_condition",
    "project_repository_operator_value_condition",
    "quarantine_operator_value_condition",
    "render_operator_value_condition",
    "restore_operator_value_quarantine",
    "rollback_active_condition",
    "validate_operator_operand",
    "validate_operator_value_condition",
]
