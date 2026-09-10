"""採用済みscalar comparisonを下流成果物へ意味保存して展開する共通Rule。"""
from __future__ import annotations

from dataclasses import dataclass

from rimay_jp_core.english_profile import operators_in
from rimay_jp_core.jp_serializer import jp_name
from rimay_jp_core.lexicon import normalizer_profile
from rimay_jp_core.model import finding
from rimay_jp_core.semantic_values import split_money


@dataclass(frozen=True)
class ComparisonConsumerError(ValueError):
    code: str
    path: str
    message: str

    def as_finding(self) -> dict:
        return finding(
            "GENERATOR",
            self.message,
            self.path,
            consumer_closure_code=self.code,
        )


def _error(code: str, path: str, message: str) -> ComparisonConsumerError:
    return ComparisonConsumerError(code, path, message)


def validate_scalar_predicate(predicate: object, path: str) -> dict:
    if not isinstance(predicate, dict):
        raise _error(
            "COMPARISON_CONSUMER_INVALID_PREDICATE",
            path,
            "比較条件がobjectではないため成果物へ展開できません。",
        )
    required = {"subject", "operator", "value"}
    allowed = required | {"unit"}
    if not required <= set(predicate) or set(predicate) - allowed:
        raise _error(
            "COMPARISON_CONSUMER_UNSUPPORTED_SHAPE",
            path,
            "scalar comparisonはsubject／operator／valueと任意unitだけを受理します。",
        )
    for field in ("subject", "value"):
        value = predicate.get(field)
        if not isinstance(value, str) or not value:
            raise _error(
                "COMPARISON_CONSUMER_INVALID_SCALAR",
                f"{path}/{field}",
                f"比較条件の{field}は空でない文字列でなければなりません。",
            )
    operator = predicate.get("operator")
    if operator not in operators_in():
        raise _error(
            "COMPARISON_CONSUMER_UNSUPPORTED_OPERATOR",
            f"{path}/operator",
            f"比較演算子 {operator!r} は採用済みの閉じた8値に含まれません。",
        )
    unit = predicate.get("unit")
    if unit is not None and unit != "JPY":
        raise _error(
            "COMPARISON_CONSUMER_UNSUPPORTED_UNIT",
            f"{path}/unit",
            f"比較条件の単位 {unit!r} は採用済みscalar単位ではありません。",
        )
    if unit == "JPY" and split_money(f"{predicate['value']} JPY") is None:
        raise _error(
            "COMPARISON_CONSUMER_INVALID_NUMERIC_VALUE",
            f"{path}/value",
            "JPY比較値は数値scalarでなければなりません。",
        )
    return predicate


def _value_surface(predicate: dict) -> str:
    if predicate.get("unit") == "JPY":
        amount, _unit = split_money(f"{predicate['value']} JPY") or ("", "")
        return f"{int(amount):,}円"
    return f"「{jp_name(predicate['value'])}」"


def render_given(predicate: object, path: str) -> tuple[str, list[str]]:
    scalar = validate_scalar_predicate(predicate, path)
    surfaces = normalizer_profile()["comparison_operator_surfaces"]
    operator = scalar["operator"]
    if set(surfaces) != operators_in() or operator not in surfaces:
        raise _error(
            "COMPARISON_CONSUMER_PROFILE_STALE",
            f"{path}/operator",
            "日本語比較演算子Profileが採用済み8値と一致しません。",
        )
    used = [f"{path}/{field}" for field in ("subject", "operator", "value")]
    if scalar.get("unit") is not None:
        used.append(f"{path}/unit")
    return (
        f"{jp_name(scalar['subject'])}が{_value_surface(scalar)}"
        f"{surfaces[operator]}",
        used,
    )


def ordering_boundary_oracle(predicate: object, path: str) -> dict | None:
    """契約上数値であるJPY orderingだけに境界値oracleを作る。"""
    scalar = validate_scalar_predicate(predicate, path)
    operator = scalar["operator"]
    if scalar.get("unit") != "JPY" or operator not in {
        "GREATER_THAN", "LESS_THAN", "GREATER_OR_EQUAL", "LESS_OR_EQUAL",
    }:
        return None
    threshold = int(scalar["value"].replace(",", ""))
    values = {
        "GREATER_THAN": (threshold + 1, threshold),
        "LESS_THAN": (threshold - 1, threshold),
        "GREATER_OR_EQUAL": (threshold, threshold - 1),
        "LESS_OR_EQUAL": (threshold, threshold + 1),
    }
    passing, failing = values[operator]
    surface = normalizer_profile()["comparison_operator_surfaces"][operator]
    return {
        "description": (
            f"{jp_name(scalar['subject'])}が{passing:,}円のとき"
            f"「{threshold:,}円{surface}」が成立し、{failing:,}円のとき"
            "不成立となることを確認する。"
        ),
        "slots": [
            f"{path}/subject", f"{path}/operator", f"{path}/value", f"{path}/unit",
        ],
    }
