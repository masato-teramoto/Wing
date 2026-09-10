"""Repository Comparison predicate mappingの隔離selector候補。

固定Repository GrammarのCondition leafは、単一AtomicValueだけでなくModifier、
追加FreeExpression、型／Label metadata、複数値と括弧groupも保持できる。本selectorは
採用済みComparison operatorへ欠落なく写像できる閉じた部分だけを選び、残余を
``RPMAP-CONDITION-STRUCTURE-PRESERVED``へ送る。mapping bindingやactive処遇は変更しない。
"""
from __future__ import annotations

from .repository_grammar import walk_syntax_tree
from .semantic_values import split_money


REPOSITORY_COMPARISON_MAPPING_CANDIDATE_VERSION = "0.1.0"


def _rules(node: dict, name: str) -> list[dict]:
    return [
        item for item in walk_syntax_tree(node)
        if item.get("kind") == "rule" and item.get("name") == name
    ]


def repository_comparison_leaf_selector_problems(condition: dict) -> tuple[str, ...]:
    """Return stable reason codes when one Repository Condition leaf is not scalar."""
    problems: list[str] = []
    candidates = _rules(condition, "InstanceOrPropertyOperatorValue")
    if len(candidates) != 1:
        problems.append("REPOSITORY_COMPARISON_CONDITION_RULE_UNSUPPORTED")
        return tuple(problems)
    candidate = candidates[0]

    if _rules(candidate, "Modifier"):
        problems.append("REPOSITORY_COMPARISON_MODIFIER_UNSUPPORTED")
    if _rules(candidate, "FreeExpression"):
        problems.append("REPOSITORY_COMPARISON_ADDITIONAL_INFORMATION_UNSUPPORTED")
    if _rules(candidate, "OfClassOrReferenceToLabel") or _rules(candidate, "Label"):
        problems.append("REPOSITORY_COMPARISON_VALUE_METADATA_UNSUPPORTED")

    if len(_rules(candidate, "OperatorValuesExpr")) != 1:
        problems.append("REPOSITORY_COMPARISON_OPERATOR_CARDINALITY")
    # A parenthesized singleton creates a nested MultiValuesExpr.  It is kept in
    # the residual surface with AND/OR values rather than silently discarding the
    # explicit group.
    if len(_rules(candidate, "MultiValuesExpr")) != 1 or \
            len(_rules(candidate, "AtomicValue")) != 1:
        problems.append("REPOSITORY_COMPARISON_VALUE_CARDINALITY")
    return tuple(dict.fromkeys(problems))


def repository_comparison_selector_problems(structure: dict) -> tuple[str, ...]:
    """Return reason codes for the active adapter's one-condition projection.

    A future Condition-expression mapping can apply
    :func:`repository_comparison_leaf_selector_problems` to every leaf and reject
    the entire expression when any leaf is residual.
    """
    conditions = _rules(structure, "Condition")
    if len(conditions) != 1:
        return ("REPOSITORY_COMPARISON_CONDITION_CARDINALITY",)
    if _rules(structure, "ItemizedConditions"):
        return ("REPOSITORY_COMPARISON_ITEMIZED_UNSUPPORTED",)
    return repository_comparison_leaf_selector_problems(conditions[0])


def repository_comparison_scalar_value_problem(value: str) -> str | None:
    """Reject product-recognized non-JPY money without treating it as opaque text."""
    money = split_money(value)
    if money is not None and money[1] != "JPY":
        return "REPOSITORY_COMPARISON_UNIT_UNSUPPORTED"
    return None
