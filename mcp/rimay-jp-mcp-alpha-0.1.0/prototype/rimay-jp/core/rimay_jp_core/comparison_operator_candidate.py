"""B5-P comparison-operator candidate isolated from the active language profile.

The active Canonical schema already has a closed eight-operator enum, and the
Repository adapter can project the corresponding typed rules.  The active
English/Japanese front ends intentionally remain narrower until the product
decision is accepted.  This module supplies the acceptance candidate without
silently widening those active entry points.
"""
from __future__ import annotations

import copy
import re
from dataclasses import dataclass

from .condition_expression import (
    parse_rendered_condition_expression,
    render_condition_expression,
)
from .english_lexer import ParseError, Token, tokenize
from .equivalence import canonicalize_ast
from .jp_serializer import parse_rimay_jp, render_rimay_jp
from .lexicon import en_label, lookup_jp, resolve_en, term_ids
from .parser import parse
from .semantic_values import split_money
from .serializer import render_requirement_views


COMPARISON_OPERATOR_CANDIDATE_VERSION = "0.1.0"
COMPARISON_OPERATORS = (
    "IS",
    "EQUALS",
    "NOT_EQUALS",
    "GREATER_THAN",
    "LESS_THAN",
    "GREATER_OR_EQUAL",
    "LESS_OR_EQUAL",
    "CONTAINS",
)

# Longest first.  Each operator has one controlled English surface; the
# existing GREATER_OR_EQUAL spelling is retained for compatibility.
_EN_OPERATOR_TOKENS = (
    (("is", "greater", "or", "equal", "to"), "GREATER_OR_EQUAL"),
    (("is", "less", "than", "or", "equal", "to"), "LESS_OR_EQUAL"),
    (("is", "greater", "than"), "GREATER_THAN"),
    (("is", "less", "than"), "LESS_THAN"),
    (("is", "equal", "to"), "EQUALS"),
    (("is", "not"), "NOT_EQUALS"),
    (("contains",), "CONTAINS"),
    (("is",), "IS"),
)
_EN_OPERATOR_SURFACE = {
    operator: " ".join(words) for words, operator in _EN_OPERATOR_TOKENS
}

_JP_OPERATOR_SURFACE = {
    "IS": "である",
    "EQUALS": "と等しい",
    "NOT_EQUALS": "ではない",
    "GREATER_THAN": "より大きい",
    "LESS_THAN": "より小さい",
    "GREATER_OR_EQUAL": "以上である",
    "LESS_OR_EQUAL": "以下である",
    "CONTAINS": "を含む",
}
_JP_OPERATOR_PATTERN = "|".join(
    re.escape(surface)
    for surface in sorted(_JP_OPERATOR_SURFACE.values(), key=len, reverse=True)
)
_JP_OPERATOR_BY_SURFACE = {
    surface: operator for operator, surface in _JP_OPERATOR_SURFACE.items()
}


@dataclass(frozen=True)
class ComparisonOperatorCandidateError(ValueError):
    """Structured candidate diagnostic; no active parser code is widened."""

    code: str
    path: str
    message: str

    def __str__(self) -> str:
        return self.message

    def diagnostic(self) -> dict:
        return {
            "domain": "comparison_operator_candidate",
            "code": self.code,
            "path": self.path,
            "message": self.message,
        }


def _error(code: str, path: str, message: str) -> ComparisonOperatorCandidateError:
    return ComparisonOperatorCandidateError(code, path, message)


def _predicate(condition: object) -> tuple[str, dict]:
    if not isinstance(condition, dict) or set(condition) != {"type", "predicate"}:
        raise _error(
            "COMPARISON_CANDIDATE_INVALID_CONDITION",
            "/condition",
            "candidate condition must contain only type and predicate",
        )
    condition_type = condition.get("type")
    if condition_type not in {"IF", "WHILE"}:
        raise _error(
            "COMPARISON_CANDIDATE_CONDITION_TYPE",
            "/condition/type",
            "comparison candidate is limited to IF and WHILE predicates",
        )
    predicate = condition.get("predicate")
    if not isinstance(predicate, dict) or not {"subject", "operator", "value"} <= set(predicate) \
            or set(predicate) - {"subject", "operator", "value", "unit"}:
        raise _error(
            "COMPARISON_CANDIDATE_INVALID_PREDICATE",
            "/condition/predicate",
            "predicate must contain subject, operator, value, and optional unit",
        )
    for key in ("subject", "value"):
        if not isinstance(predicate.get(key), str) or not predicate[key]:
            raise _error(
                "COMPARISON_CANDIDATE_INVALID_OPERAND",
                f"/condition/predicate/{key}",
                f"{key} must be a non-empty string",
            )
        if any(mark in predicate[key] for mark in ('"', "「", "」")):
            raise _error(
                "COMPARISON_CANDIDATE_AMBIGUOUS_OPERAND",
                f"/condition/predicate/{key}",
                f"{key} contains a controlled-surface delimiter",
            )
    operator = predicate.get("operator")
    if operator not in COMPARISON_OPERATORS:
        raise _error(
            "COMPARISON_CANDIDATE_UNSUPPORTED_OPERATOR",
            "/condition/predicate/operator",
            f"operator {operator!r} is outside the closed candidate set",
        )
    unit = predicate.get("unit")
    if unit is not None and unit != "JPY":
        raise _error(
            "COMPARISON_CANDIDATE_UNSUPPORTED_UNIT",
            "/condition/predicate/unit",
            "the candidate preserves units only through the closed JPY value contract",
        )
    if unit == "JPY" and split_money(f'{predicate["value"]} JPY') is None:
        raise _error(
            "COMPARISON_CANDIDATE_INVALID_UNIT_VALUE",
            "/condition/predicate/value",
            "JPY value must be a numeric scalar",
        )
    return condition_type, predicate


def _english_term(value: str) -> str:
    return en_label(value) if value in term_ids() else value


def _japanese_term(value: str) -> str:
    term = term_ids().get(value)
    return term["preferred_japanese"] if term else value


def _resolve_english(value: str) -> str:
    return resolve_en(value) or value


def _resolve_japanese(value: str) -> str:
    hit = lookup_jp(value)
    return hit[0] if hit else value


def _render_value_en(predicate: dict) -> str:
    if predicate.get("unit") == "JPY":
        return f'{predicate["value"]} JPY'
    return _english_term(predicate["value"])


def _render_value_ja(predicate: dict) -> str:
    if predicate.get("unit") == "JPY":
        value = predicate["value"]
        try:
            number = float(value)
            rendered = f"{int(number):,}" if number.is_integer() else format(number, ",g")
        except ValueError as exc:  # guarded by _predicate; keep direct calls fail-closed
            raise _error(
                "COMPARISON_CANDIDATE_INVALID_UNIT_VALUE",
                "/condition/predicate/value",
                "JPY value must be a numeric scalar",
            ) from exc
        return rendered + "円"
    return _japanese_term(predicate["value"])


def render_comparison_condition(condition: dict, *, language: str) -> str:
    """Render one closed IF/WHILE predicate without a clause delimiter."""
    condition_type, predicate = _predicate(condition)
    if language == "en":
        keyword = "If" if condition_type == "IF" else "While"
        subject = _english_term(predicate["subject"])
        operator = _EN_OPERATOR_SURFACE[predicate["operator"]]
        value = _render_value_en(predicate)
        return f'{keyword} the "{subject}" {operator} "{value}"'
    if language == "ja":
        subject = _japanese_term(predicate["subject"])
        operator = _JP_OPERATOR_SURFACE[predicate["operator"]]
        value = _render_value_ja(predicate)
        suffix = "場合" if condition_type == "IF" else "間"
        return f"{subject}が「{value}」{operator}{suffix}"
    raise _error(
        "COMPARISON_CANDIDATE_LANGUAGE",
        "/language",
        f"unsupported candidate language {language!r}",
    )


def _token_value(token: Token, text: str, path: str) -> str:
    if token.kind not in {"Q", "W"}:
        raise _error(
            "COMPARISON_CANDIDATE_INVALID_OPERAND",
            path,
            f"expected an entity/value token at offset {token.start} in {text!r}",
        )
    return token.value


def _parse_comparison_condition_en(text: str) -> dict:
    try:
        tokens = tokenize(text)
    except ParseError as exc:
        raise _error(
            "COMPARISON_CANDIDATE_LEXICAL_GAP",
            "/condition",
            str(exc),
        ) from exc
    if not tokens or tokens[0].kind != "W" or tokens[0].value not in {"If", "While"}:
        raise _error(
            "COMPARISON_CANDIDATE_CONDITION_TYPE",
            "/condition/type",
            "English candidate must start with canonical If or While",
        )
    condition_type = "IF" if tokens[0].value == "If" else "WHILE"
    position = 1
    if position < len(tokens) and tokens[position].kind == "W" \
            and tokens[position].value == "the":
        position += 1
    if position >= len(tokens):
        raise _error(
            "COMPARISON_CANDIDATE_PARSE_INCOMPLETE",
            "/condition/predicate/subject",
            "predicate subject is missing",
        )
    subject = _resolve_english(_token_value(
        tokens[position], text, "/condition/predicate/subject"))
    position += 1

    operator = None
    for words, candidate in _EN_OPERATOR_TOKENS:
        actual = tuple(
            token.value for token in tokens[position:position + len(words)]
            if token.kind == "W"
        )
        if len(actual) == len(words) and actual == words:
            operator = candidate
            position += len(words)
            break
    if operator is None:
        found = " ".join(token.value for token in tokens[position:])
        raise _error(
            "COMPARISON_CANDIDATE_UNSUPPORTED_OPERATOR",
            "/condition/predicate/operator",
            f"no canonical comparison surface starts with {found!r}",
        )
    if position >= len(tokens):
        raise _error(
            "COMPARISON_CANDIDATE_PARSE_INCOMPLETE",
            "/condition/predicate/value",
            "predicate value is missing",
        )
    value_token = tokens[position]
    if value_token.kind != "Q":
        raise _error(
            "COMPARISON_CANDIDATE_UNSUPPORTED_OPERATOR",
            "/condition/predicate/operator",
            "operator surface is not one of the closed canonical spellings",
        )
    position += 1
    if position != len(tokens):
        raise _error(
            "COMPARISON_CANDIDATE_PARSE_TRAILING",
            "/condition",
            "unconsumed English comparison text remains",
        )
    money = split_money(value_token.value)
    predicate = {
        "subject": subject,
        "operator": operator,
        "value": _resolve_english(value_token.value),
    }
    if money:
        predicate["value"], predicate["unit"] = money
    condition = {"type": condition_type, "predicate": predicate}
    _predicate(condition)
    return condition


def _parse_comparison_condition_ja(text: str) -> dict:
    match = re.fullmatch(
        rf"(.+?)が「([^」]+)」({_JP_OPERATOR_PATTERN})(場合|間)", text
    )
    if match is None:
        raise _error(
            "COMPARISON_CANDIDATE_AMBIGUOUS_SURFACE",
            "/condition",
            "Japanese candidate must use one exact quoted comparison surface",
        )
    subject_surface, value_surface, operator_surface, suffix = match.groups()
    predicate = {
        "subject": _resolve_japanese(subject_surface),
        "operator": _JP_OPERATOR_BY_SURFACE[operator_surface],
        "value": _resolve_japanese(value_surface),
    }
    money = re.fullmatch(r"([0-9][0-9,]*(?:\.[0-9]+)?)円", value_surface)
    if money:
        predicate["value"] = money.group(1).replace(",", "")
        predicate["unit"] = "JPY"
    condition = {
        "type": "IF" if suffix == "場合" else "WHILE",
        "predicate": predicate,
    }
    _predicate(condition)
    return condition


def parse_comparison_condition(text: str, *, language: str) -> dict:
    """Parse one full candidate fragment; aliases and trailing text are rejected."""
    if not isinstance(text, str) or not text or text != text.strip():
        raise _error(
            "COMPARISON_CANDIDATE_AMBIGUOUS_SURFACE",
            "/condition",
            "candidate condition must be a non-empty, trim-stable string",
        )
    if language == "en":
        return _parse_comparison_condition_en(text)
    if language == "ja":
        return _parse_comparison_condition_ja(text)
    raise _error(
        "COMPARISON_CANDIDATE_LANGUAGE",
        "/language",
        f"unsupported candidate language {language!r}",
    )


def _leaf_end(text: str, position: int, *, language: str) -> int:
    delimiters = (" and ", " or ", ")") if language == "en" else \
        (" かつ ", " または ", ")")
    indexes = [text.find(delimiter, position) for delimiter in delimiters]
    return min(index for index in indexes if index >= 0) if any(
        index >= 0 for index in indexes) else len(text)


def render_comparison_condition_expression(expression: dict, *, language: str) -> str:
    return render_condition_expression(
        expression,
        lambda condition: render_comparison_condition(condition, language=language),
        language=language,
    )


def parse_comparison_condition_expression(text: str, *, language: str) -> dict:
    def parse_leaf(value: str, position: int) -> tuple[dict, int]:
        end = _leaf_end(value, position, language=language)
        fragment = value[position:end].rstrip()
        return parse_comparison_condition(fragment, language=language), \
            position + len(fragment)

    return parse_rendered_condition_expression(
        text, parse_leaf, language=language)


def _without_conditions(document: dict) -> dict:
    candidate = copy.deepcopy(document)
    core = candidate.get("rimay_core")
    if not isinstance(core, dict) or core.get("scope") is not None:
        raise _error(
            "COMPARISON_CANDIDATE_REQUIREMENT_SCOPE",
            "/rimay_core/scope",
            "requirement candidate keeps Scope outside this operator batch",
        )
    has_flat = isinstance(core.get("conditions"), list) and len(core["conditions"]) == 1
    has_expression = core.get("condition_expression") is not None
    if has_flat == has_expression:
        raise _error(
            "COMPARISON_CANDIDATE_CONDITION_AUTHORITY",
            "/rimay_core",
            "requirement candidate needs exactly one condition authority",
        )
    core["conditions"] = []
    core.pop("condition_expression", None)
    return candidate


def render_comparison_requirement(document: dict, *, language: str) -> str:
    """Render a full candidate requirement while reusing the active response runtime."""
    response_only = _without_conditions(document)
    core = document["rimay_core"]
    if core.get("condition_expression") is not None:
        condition = render_comparison_condition_expression(
            core["condition_expression"], language=language)
    else:
        condition = render_comparison_condition(core["conditions"][0], language=language)
    if language == "en":
        response = render_requirement_views(response_only)["english_rimay"]
        return condition + ", " + response
    if language == "ja":
        response = render_rimay_jp(response_only)
        return condition + "、" + response
    raise _error(
        "COMPARISON_CANDIDATE_LANGUAGE",
        "/language",
        f"unsupported candidate language {language!r}",
    )


def _split_requirement(text: str, *, language: str) -> tuple[str, str]:
    delimiter = ", " if language == "en" else "、"
    quote_open, quote_close = ('"', '"') if language == "en" else ("「", "」")
    in_quote = False
    depth = 0
    index = 0
    while index < len(text):
        char = text[index]
        if char == quote_open:
            in_quote = not in_quote if quote_open == quote_close else True
        elif char == quote_close and quote_open != quote_close:
            in_quote = False
        elif not in_quote and char == "(":
            depth += 1
        elif not in_quote and char == ")":
            depth -= 1
            if depth < 0:
                break
        if not in_quote and depth == 0 and text.startswith(delimiter, index):
            return text[:index], text[index + len(delimiter):]
        index += 1
    raise _error(
        "COMPARISON_CANDIDATE_REQUIREMENT_DELIMITER",
        "/requirement",
        "condition and response are not separated by one unambiguous delimiter",
    )


def parse_comparison_requirement(text: str, *, language: str) -> dict:
    """Parse a full candidate surface into a semantic ``rimay_core`` object."""
    if language not in {"en", "ja"}:
        raise _error(
            "COMPARISON_CANDIDATE_LANGUAGE",
            "/language",
            f"unsupported candidate language {language!r}",
        )
    condition_surface, response_surface = _split_requirement(text, language=language)
    if condition_surface.startswith("("):
        expression = parse_comparison_condition_expression(
            condition_surface, language=language)
        conditions = None
    else:
        conditions = [parse_comparison_condition(
            condition_surface, language=language)]
        expression = None
    if language == "en":
        try:
            core = canonicalize_ast(parse(response_surface))
        except ParseError as exc:
            raise _error(
                "COMPARISON_CANDIDATE_RESPONSE_PARSE",
                "/rimay_core/response",
                str(exc),
            ) from exc
    else:
        core = parse_rimay_jp(response_surface)
    if core.get("scope") is None:
        core.pop("scope", None)
    core.pop("conditions", None)
    core.pop("condition_expression", None)
    if expression is not None:
        core["condition_expression"] = expression
    else:
        core["conditions"] = conditions
    return core


__all__ = [
    "COMPARISON_OPERATOR_CANDIDATE_VERSION",
    "COMPARISON_OPERATORS",
    "ComparisonOperatorCandidateError",
    "parse_comparison_condition",
    "parse_comparison_condition_expression",
    "parse_comparison_requirement",
    "render_comparison_condition",
    "render_comparison_condition_expression",
    "render_comparison_requirement",
]
