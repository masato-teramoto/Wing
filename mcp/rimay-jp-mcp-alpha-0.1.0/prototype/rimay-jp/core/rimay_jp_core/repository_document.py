"""固定Repository構文木からRepository固有の文書投影を作る。

この投影はCanonicalではなく、製品Action Familyや論文corpusを参照しない。受理済みの
Repository構文が選択したRequirement・Condition・Trigger・Atomic Response・Action規則と、
そのassignmentを入力span付きで保持する。論理接続・括弧・itemized構造を縮退させず、
後段の製品投影とは独立に扱う。
"""
from __future__ import annotations

import ast
import copy
import hashlib
import re
from dataclasses import dataclass

from .repository_grammar import (
    GrammarIR, SyntaxParseResult, direct_syntax_rule_children,
    syntax_tree_children, syntax_tree_problems, syntax_tree_signature,
    walk_syntax_tree,
)
from .repository_linker import (
    SemanticLinkResult, grammar_linking_inventory, link_repository_syntax,
)


REPOSITORY_DOCUMENT_SCHEMA_VERSION = "0.5.0"
REPOSITORY_DOCUMENT_ROOT = "CNLFunctionalRequirements"
REPOSITORY_DOCUMENT_STATUSES = frozenset({
    "projected_document", "syntax_not_accepted", "unsupported_root_rule",
    "ambiguity_check_required", "ambiguous_syntax",
    "semantic_linking_required", "semantic_linking_failed", "projection_contract_error",
})


@dataclass(frozen=True)
class RepositoryDocumentProjectionResult:
    status: str
    root_rule: str
    document: dict | None
    reason: str

    def __post_init__(self) -> None:
        if self.status not in REPOSITORY_DOCUMENT_STATUSES:
            raise ValueError(f"unknown repository document status: {self.status}")


def _source_sha256(text: str) -> str:
    return "sha256:" + hashlib.sha256(text.encode("utf-8")).hexdigest()


def _decode_surface(surface: str) -> str:
    if len(surface) >= 2 and surface[0] == surface[-1] and surface[0] in "\"'":
        try:
            value = ast.literal_eval(surface)
            if isinstance(value, str):
                return value
        except (SyntaxError, ValueError):
            pass
        return surface[1:-1]
    return surface[1:] if surface.startswith("^") else surface


def _fragment(source_text: str, span: dict) -> str:
    start, end = span.get("start"), span.get("end")
    if type(start) is int and type(end) is int and 0 <= start <= end <= len(source_text):
        return source_text[start:end]
    raise ValueError(f"invalid source span: {span!r}")


def _contains(outer: dict, inner: dict) -> bool:
    return type(outer.get("start")) is int and type(outer.get("end")) is int and \
        type(inner.get("start")) is int and type(inner.get("end")) is int and \
        outer["start"] <= inner["start"] <= inner["end"] <= outer["end"]


def _leaf_fact(node: dict, source_text: str) -> dict | None:
    kind = node.get("kind")
    span = copy.deepcopy(node.get("span") or {})
    surface = _fragment(source_text, span)
    if kind == "cross_reference":
        return {
            "kind": kind, "target": node.get("target"), "terminal": node.get("terminal"),
            "value": _decode_surface(surface), "surface": surface, "span": span,
            # The projection boundary requires a successfully recomputed
            # SemanticLinkResult; the syntax node itself intentionally keeps
            # its parse-time flag unchanged.
            "linking_checked": True,
        }
    if kind == "terminal":
        return {
            "kind": kind, "terminal": node.get("name"),
            "value": _decode_surface(surface), "surface": surface, "span": span,
        }
    if kind == "enum_literal":
        return {
            "kind": kind, "name": node.get("name"),
            "value": surface, "surface": surface, "span": span,
        }
    if kind == "literal":
        return {
            "kind": kind, "value": node.get("value"),
            "surface": surface, "span": span,
        }
    return None


def _assignment_records(action: dict, source_text: str) -> list[dict]:
    records: list[dict] = []

    def visit(node: dict, rule_path: tuple[str, ...]) -> None:
        path = rule_path
        if node.get("kind") == "rule":
            path = rule_path + (node["name"],)
        if node.get("kind") == "assignment":
            child = node.get("child")
            values = [] if not isinstance(child, dict) else [
                fact for item in walk_syntax_tree(child)
                if (fact := _leaf_fact(item, source_text)) is not None
            ]
            span = copy.deepcopy(node.get("span") or {})
            records.append({
                "owner_rule": path[-1], "rule_path": list(path),
                "feature": node.get("feature"), "operator": node.get("operator"),
                "span": span, "source": _fragment(source_text, span), "values": values,
            })
        for child in syntax_tree_children(node):
            visit(child, path)

    visit(action, ())
    return records


def _direct_assignment_record(rule: dict, source_text: str,
                              features: set[str], description: str) -> dict:
    """Return one assignment owned directly by ``rule``.

    Wrapper rules such as SystemResponse contain an entire response subtree.  The
    direct rule path keeps wrapper facts separate from the Atomic Response facts
    already projected elsewhere.
    """
    rule_id = rule.get("name")
    records = [
        record for record in _assignment_records(rule, source_text)
        if record.get("rule_path") == [rule_id]
        and record.get("feature") in features
    ]
    return _only(records, description)


def _rule_nodes(node: dict, name: str) -> list[dict]:
    return [item for item in walk_syntax_tree(node)
            if item.get("kind") == "rule" and item.get("name") == name]


def _owned_nodes(rule: dict, *, kind: str | None = None,
                 feature: str | None = None) -> list[dict]:
    """Return nodes owned by ``rule`` without descending into called rules."""
    found: list[dict] = []

    def visit(node: dict) -> None:
        for child in syntax_tree_children(node):
            if child.get("kind") == "rule":
                continue
            if (kind is None or child.get("kind") == kind) and \
                    (feature is None or child.get("feature") == feature):
                found.append(child)
            visit(child)

    visit(rule)
    return found


def _only(items: list[dict], description: str) -> dict:
    if len(items) != 1:
        raise ValueError(f"{description} must occur exactly once, got {len(items)}")
    return items[0]


def _span_source(node: dict, source_text: str) -> dict:
    span = copy.deepcopy(node.get("span") or {})
    return {"span": span, "source": _fragment(source_text, span)}


def _operator_record(node: dict, expected: str, source_text: str) -> dict:
    literals = [item for item in _owned_nodes(node, kind="literal")
                if item.get("value") in {",", expected}]
    operator_tokens = [item for item in literals if item.get("value") == expected]
    _only(operator_tokens, f"{expected} operator token")
    start = min(item["span"]["start"] for item in literals)
    end = max(item["span"]["end"] for item in literals)
    span = {"start": start, "end": end}
    return {"kind": expected, "span": span, "source": _fragment(source_text, span)}


def _expression_record(node: dict, source_text: str,
                       atomic_index_by_node: dict[int, int]) -> dict:
    name = node.get("name")
    if name == "ResponseBlockNotItemized":
        child = _only(
            [item for item in direct_syntax_rule_children(node)
             if item.get("name") == "OR_Response"],
            "ResponseBlockNotItemized expression")
        return _expression_record(child, source_text, atomic_index_by_node)
    if name in {"OR_Response", "AND_Response"}:
        child_name = "AND_Response" if name == "OR_Response" \
            else "PrimaryExpression_Response"
        operator_kind = "or" if name == "OR_Response" else "and"
        children = [item for item in direct_syntax_rule_children(node)
                    if item.get("name") == child_name]
        if not children:
            raise ValueError(f"{name} has no {child_name} operand")
        expression = _expression_record(children[0], source_text, atomic_index_by_node)
        repeats = [item for item in _owned_nodes(node, kind="repeat")
                   if item.get("max") is None]
        repeated = [] if not repeats else repeats[-1].get("children", [])
        if len(repeated) != len(children) - 1:
            raise ValueError(f"{name} operand/operator count mismatch")
        for group, right_node in zip(repeated, children[1:]):
            right = _expression_record(right_node, source_text, atomic_index_by_node)
            span = {"start": expression["span"]["start"], "end": right["span"]["end"]}
            expression = {
                "kind": operator_kind, "span": span,
                "source": _fragment(source_text, span),
                "operator": _operator_record(group, operator_kind, source_text),
                "left": expression, "right": right,
            }
        return expression
    if name == "PrimaryExpression_Response":
        atomics = [item for item in direct_syntax_rule_children(node)
                   if item.get("name") == "AtomicSystemResponse"]
        nested = [item for item in direct_syntax_rule_children(node)
                  if item.get("name") == "ResponseBlockNotItemized"]
        if atomics and not nested:
            atomic = _only(atomics, "primary atomic response")
            try:
                index = atomic_index_by_node[id(atomic)]
            except KeyError as exc:
                raise ValueError("expression atomic response is outside its requirement") from exc
            return {"kind": "atomic", "atomic_response_index": index,
                    **_span_source(atomic, source_text)}
        if nested and not atomics:
            inner = _only(nested, "parenthesized response expression")
            return {"kind": "group", **_span_source(node, source_text),
                    "expression": _expression_record(
                        inner, source_text, atomic_index_by_node)}
        raise ValueError("PrimaryExpression_Response has an unsupported selected branch")
    raise ValueError(f"unsupported response expression rule: {name}")


def _connector_record(source_text: str, start: int, end: int) -> dict | None:
    raw = source_text[start:end]
    compact = re.sub(r"\s+", "", raw)
    if not compact:
        return None
    kinds = {",": "comma", "and": "and", "or": "or",
             ",and": "comma_and", ",or": "comma_or"}
    try:
        kind = kinds[compact]
    except KeyError as exc:
        raise ValueError(f"unsupported itemized response connector: {raw!r}") from exc
    leading = len(raw) - len(raw.lstrip())
    trailing = len(raw) - len(raw.rstrip())
    span = {"start": start + leading, "end": end - trailing}
    return {"kind": kind, "span": span, "source": _fragment(source_text, span)}


def _itemized_record(node: dict, source_text: str,
                     atomic_index_by_node: dict[int, int]) -> dict:
    item_assignments = _owned_nodes(node, kind="assignment", feature="item")
    response_assignments = _owned_nodes(node, kind="assignment", feature="response")
    if len(item_assignments) != len(response_assignments) or not item_assignments:
        raise ValueError("itemized response bullet/response count mismatch")
    sequence_assignments = _owned_nodes(
        node, kind="assignment", feature="in_sequence")
    if len(sequence_assignments) > 1:
        raise ValueError("itemized response has multiple in_sequence assignments")
    in_sequence = None
    if sequence_assignments:
        assignment = sequence_assignments[0]
        sequence_tokens = [item for item in _owned_nodes(node, kind="literal")
                           if item.get("value") == "sequence"]
        token = _only(sequence_tokens, "in sequence literal")
        span = {"start": assignment["span"]["start"], "end": token["span"]["end"]}
        in_sequence = {"span": span, "source": _fragment(source_text, span)}
    items = []
    previous_end: int | None = None
    for index, (item_assignment, response_assignment) in enumerate(
            zip(item_assignments, response_assignments)):
        atomic = _only(
            [item for item in direct_syntax_rule_children(response_assignment)
             if item.get("name") == "AtomicSystemResponse"],
            f"itemized response[{index}]")
        try:
            atomic_index = atomic_index_by_node[id(atomic)]
        except KeyError as exc:
            raise ValueError("itemized atomic response is outside its requirement") from exc
        bullet_source = _fragment(source_text, item_assignment["span"])
        if bullet_source == "-":
            bullet_kind = "hyphen"
        elif bullet_source.isdigit():
            bullet_kind = "integer"
        else:
            raise ValueError(f"unsupported itemized response bullet: {bullet_source!r}")
        connector = None if previous_end is None else _connector_record(
            source_text, previous_end, item_assignment["span"]["start"])
        span = {"start": item_assignment["span"]["start"],
                "end": atomic["span"]["end"]}
        items.append({
            "index": index, "span": span, "source": _fragment(source_text, span),
            "connector_before": connector,
            "bullet": {"kind": bullet_kind, "value": bullet_source,
                       **_span_source(item_assignment, source_text)},
            "atomic_response_index": atomic_index,
        })
        previous_end = atomic["span"]["end"]
    return {"kind": "itemized", **_span_source(node, source_text),
            "in_sequence": in_sequence, "items": items}


def _response_structure(requirement: dict, source_text: str,
                        atomic_index_by_node: dict[int, int]) -> dict:
    blocks = _rule_nodes(requirement, "ResponseBlock")
    block = _only(blocks, "Requirement ResponseBlock")
    selected = [item for item in direct_syntax_rule_children(block)
                if item.get("name") in {
                    "ResponseBlockNotItemized", "ResponseBlockItemized"}]
    selected_block = _only(selected, "ResponseBlock selected form")
    if selected_block["name"] == "ResponseBlockItemized":
        return _itemized_record(selected_block, source_text, atomic_index_by_node)
    return {"kind": "expression", **_span_source(selected_block, source_text),
            "expression": _expression_record(
                selected_block, source_text, atomic_index_by_node)}


def _rule_record(rule: dict, source_text: str) -> dict:
    return {"rule_id": rule.get("name"), **_span_source(rule, source_text),
            "assignments": _assignment_records(rule, source_text)}


def _condition_leaf_record(condition: dict, source_text: str) -> dict:
    selected = _only(direct_syntax_rule_children(condition), "Condition selected rule")
    return {"kind": "condition", **_span_source(condition, source_text),
            "rule": _rule_record(selected, source_text)}


def _precondition_expression_record(node: dict, source_text: str) -> dict:
    name = node.get("name")
    if name == "NonItemizedConditions":
        child = _only(
            [item for item in direct_syntax_rule_children(node)
             if item.get("name") == "ConditionsOrExpression"],
            "NonItemizedConditions expression")
        return _precondition_expression_record(child, source_text)
    if name in {"ConditionsOrExpression", "ConditionsAndExpression"}:
        child_name = "ConditionsAndExpression" if name == "ConditionsOrExpression" \
            else "ConditionsPrimaryExpression"
        operator_kind = "or" if name == "ConditionsOrExpression" else "and"
        children = [item for item in direct_syntax_rule_children(node)
                    if item.get("name") == child_name]
        if not children:
            raise ValueError(f"{name} has no {child_name} operand")
        expression = _precondition_expression_record(children[0], source_text)
        repeats = [item for item in _owned_nodes(node, kind="repeat")
                   if item.get("max") is None]
        repeated = [] if not repeats else repeats[-1].get("children", [])
        if len(repeated) != len(children) - 1:
            raise ValueError(f"{name} operand/operator count mismatch")
        for group, right_node in zip(repeated, children[1:]):
            right = _precondition_expression_record(right_node, source_text)
            span = {"start": expression["span"]["start"], "end": right["span"]["end"]}
            expression = {
                "kind": operator_kind, "span": span,
                "source": _fragment(source_text, span),
                "operator": _operator_record(group, operator_kind, source_text),
                "left": expression, "right": right,
            }
        return expression
    if name == "ConditionsPrimaryExpression":
        conditions = [item for item in direct_syntax_rule_children(node)
                      if item.get("name") == "Condition"]
        itemized = [item for item in direct_syntax_rule_children(node)
                    if item.get("name") == "ItemizedConditions"]
        if conditions and not itemized:
            return _condition_leaf_record(
                _only(conditions, "primary condition"), source_text)
        if itemized and not conditions:
            nested = _only(itemized, "parenthesized itemized conditions")
            return {"kind": "group", **_span_source(node, source_text),
                    "preconditions": _precondition_structure_record(
                        nested, source_text)}
        raise ValueError("ConditionsPrimaryExpression has an unsupported selected branch")
    raise ValueError(f"unsupported precondition expression rule: {name}")


def _precondition_itemized_record(node: dict, source_text: str) -> dict:
    item_assignments = _owned_nodes(node, kind="assignment", feature="item")
    condition_assignments = _owned_nodes(
        node, kind="assignment", feature="precondition")
    if len(item_assignments) != len(condition_assignments) or not item_assignments:
        raise ValueError("itemized condition bullet/condition count mismatch")
    items = []
    previous_end: int | None = None
    for index, (item_assignment, condition_assignment) in enumerate(
            zip(item_assignments, condition_assignments)):
        condition = _only(
            [item for item in direct_syntax_rule_children(condition_assignment)
             if item.get("name") == "Condition"],
            f"itemized condition[{index}]")
        bullet_source = _fragment(source_text, item_assignment["span"])
        if bullet_source == "-":
            bullet_kind = "hyphen"
        elif bullet_source.isdigit():
            bullet_kind = "integer"
        else:
            raise ValueError(f"unsupported itemized condition bullet: {bullet_source!r}")
        connector = None if previous_end is None else _connector_record(
            source_text, previous_end, item_assignment["span"]["start"])
        if index and connector is None:
            raise ValueError("itemized condition connector is missing")
        span = {"start": item_assignment["span"]["start"],
                "end": condition["span"]["end"]}
        items.append({
            "index": index, "span": span, "source": _fragment(source_text, span),
            "connector_before": connector,
            "bullet": {"kind": bullet_kind, "value": bullet_source,
                       **_span_source(item_assignment, source_text)},
            "condition": _condition_leaf_record(condition, source_text),
        })
        previous_end = condition["span"]["end"]
    return {"kind": "itemized", **_span_source(node, source_text), "items": items}


def _precondition_structure_record(node: dict, source_text: str) -> dict:
    if node.get("name") == "PreconditionStructure":
        selected = _only(
            [item for item in direct_syntax_rule_children(node)
             if item.get("name") in {"ItemizedConditions", "NonItemizedConditions"}],
            "PreconditionStructure selected form")
    else:
        selected = node
    if selected.get("name") == "ItemizedConditions":
        return _precondition_itemized_record(selected, source_text)
    if selected.get("name") == "NonItemizedConditions":
        return {"kind": "expression", **_span_source(selected, source_text),
                "expression": _precondition_expression_record(selected, source_text)}
    raise ValueError(f"unsupported precondition structure: {selected.get('name')}")


def _trigger_action_record(atomic: dict, source_text: str) -> dict:
    action_assignment = _only(
        _owned_nodes(atomic, kind="assignment", feature="action"),
        "AtomicActionInTrigger action")
    selected = _only(
        [item for item in direct_syntax_rule_children(action_assignment)
         if item.get("name") in {"ActionPhrase", "UIAction"}],
        "AtomicActionInTrigger selected action")
    if selected.get("name") == "ActionPhrase":
        selected = _only(
            direct_syntax_rule_children(selected), "trigger ActionPhrase selected rule")
    negations = _owned_nodes(atomic, kind="assignment", feature="negation")
    if len(negations) > 1:
        raise ValueError("AtomicActionInTrigger has multiple negation assignments")
    negation = None if not negations else _span_source(negations[0], source_text)
    return {"span": copy.deepcopy(atomic["span"]),
            "source": _fragment(source_text, atomic["span"]),
            "negation": negation, "action": _rule_record(selected, source_text)}


def _trigger_action_expression_record(node: dict, source_text: str,
                                      atomic_index_by_node: dict[int, int]) -> dict:
    name = node.get("name")
    if name == "ActionsExpression":
        child = _only(
            [item for item in direct_syntax_rule_children(node)
             if item.get("name") == "ActionsOrExpression"],
            "ActionsExpression expression")
        return _trigger_action_expression_record(
            child, source_text, atomic_index_by_node)
    if name in {"ActionsOrExpression", "ActionsAndExpression"}:
        child_name = "ActionsAndExpression" if name == "ActionsOrExpression" \
            else "ActionsPrimaryExpression"
        operator_kind = "or" if name == "ActionsOrExpression" else "and"
        children = [item for item in direct_syntax_rule_children(node)
                    if item.get("name") == child_name]
        if not children:
            raise ValueError(f"{name} has no {child_name} operand")
        expression = _trigger_action_expression_record(
            children[0], source_text, atomic_index_by_node)
        repeats = [item for item in _owned_nodes(node, kind="repeat")
                   if item.get("max") is None]
        repeated = [] if not repeats else repeats[-1].get("children", [])
        if len(repeated) != len(children) - 1:
            raise ValueError(f"{name} operand/operator count mismatch")
        for group, right_node in zip(repeated, children[1:]):
            right = _trigger_action_expression_record(
                right_node, source_text, atomic_index_by_node)
            span = {"start": expression["span"]["start"], "end": right["span"]["end"]}
            expression = {
                "kind": operator_kind, "span": span,
                "source": _fragment(source_text, span),
                "operator": _operator_record(group, operator_kind, source_text),
                "left": expression, "right": right,
            }
        return expression
    if name == "ActionsPrimaryExpression":
        atomics = [item for item in direct_syntax_rule_children(node)
                   if item.get("name") == "AtomicActionInTrigger"]
        nested = [item for item in direct_syntax_rule_children(node)
                  if item.get("name") == "ActionsExpression"]
        if atomics and not nested:
            atomic = _only(atomics, "primary trigger action")
            try:
                index = atomic_index_by_node[id(atomic)]
            except KeyError as exc:
                raise ValueError("trigger action is outside its Trigger") from exc
            return {"kind": "atomic", "atomic_action_index": index,
                    **_span_source(atomic, source_text)}
        if nested and not atomics:
            inner = _only(nested, "parenthesized trigger actions")
            return {"kind": "group", **_span_source(node, source_text),
                    "expression": _trigger_action_expression_record(
                        inner, source_text, atomic_index_by_node)}
        raise ValueError("ActionsPrimaryExpression has an unsupported selected branch")
    raise ValueError(f"unsupported trigger action expression rule: {name}")


def _trigger_record(trigger: dict, source_text: str) -> dict:
    atomics = _rule_nodes(trigger, "AtomicActionInTrigger")
    atomic_index_by_node = {id(node): index for index, node in enumerate(atomics)}
    actions = []
    for index, atomic in enumerate(atomics):
        actions.append({"index": index, **_trigger_action_record(atomic, source_text)})
    expression = _only(
        [item for item in direct_syntax_rule_children(trigger)
         if item.get("name") == "ActionsExpression"],
        "Trigger actions expression")
    trigger_assignments = [
        item for item in _assignment_records(trigger, source_text)
        if item.get("owner_rule") == "Trigger" and item.get("feature") != "actions"]
    return {"kind": "trigger", **_span_source(trigger, source_text),
            "assignments": trigger_assignments, "atomic_actions": actions,
            "action_structure": _trigger_action_expression_record(
                expression, source_text, atomic_index_by_node)}


def _condition_payload(rule: dict, source_text: str) -> dict:
    name = rule.get("name")
    direct = direct_syntax_rule_children(rule)
    if name == "WhileStructure":
        preconditions = _only(
            [item for item in direct if item.get("name") == "PreconditionStructure"],
            "WhileStructure preconditions")
        return _precondition_structure_record(preconditions, source_text)
    if name in {"WhenStructure", "IfStructure"}:
        selected = _only(
            [item for item in direct if item.get("name") in {
                "Trigger", "FreeExpression", "PreconditionStructure"}],
            f"{name} payload")
        if selected.get("name") == "Trigger":
            return _trigger_record(selected, source_text)
        if selected.get("name") == "PreconditionStructure":
            return _precondition_structure_record(selected, source_text)
        return {"kind": "free_expression", **_span_source(selected, source_text),
                "rule": _rule_record(selected, source_text)}
    if name == "WhereStructure":
        selected = _only(
            [item for item in direct if item.get("name") == "FreeExpression"],
            "WhereStructure FreeExpression")
        return {"kind": "free_expression", **_span_source(selected, source_text),
                "rule": _rule_record(selected, source_text)}
    if name == "RepeatOnce":
        selected = _only(
            [item for item in direct if item.get("name") in {
                "Trigger", "Time", "Condition"}], "RepeatOnce payload")
        if selected.get("name") == "Trigger":
            return _trigger_record(selected, source_text)
        if selected.get("name") == "Condition":
            return _condition_leaf_record(selected, source_text)
        return {"kind": "time", **_span_source(selected, source_text),
                "rule": _rule_record(selected, source_text)}
    if name == "Frequently":
        times = [item for item in direct if item.get("name") == "Time"]
        if times:
            selected = _only(times, "Frequently Time")
            return {"kind": "time", **_span_source(selected, source_text),
                    "rule": _rule_record(selected, source_text)}
        frequency = _atomic_option(rule, "frequency", source_text)
        if frequency is None:
            raise ValueError("Frequently has no Time or frequency")
        return {"kind": "frequency", **frequency}
    raise ValueError(f"unsupported condition payload rule: {name}")


def _condition_structure_record(condition: dict, source_text: str) -> dict:
    selected = _only(
        [item for item in direct_syntax_rule_children(condition)
         if item.get("name") in {
             "WhileStructure", "WhenStructure", "WhereStructure", "IfStructure",
             "TemporalStructure"}], "ConditionStructure selected rule")
    rule_path = ["ConditionStructure", selected["name"]]
    actual = selected
    if selected.get("name") == "TemporalStructure":
        actual = _only(
            [item for item in direct_syntax_rule_children(selected)
             if item.get("name") in {"RepeatOnce", "Frequently"}],
            "TemporalStructure selected rule")
        rule_path.append(actual["name"])
    keyword_feature = "advice_keyword" if actual.get("name") == "RepeatOnce" else "keyword"
    keyword = _atomic_option(actual, keyword_feature, source_text)
    if keyword is None:
        raise ValueError(f"{actual.get('name')} keyword is missing")
    kind = keyword["value"]["value"].lower()
    return {"kind": kind, "rule_path": rule_path,
            **_span_source(condition, source_text), "keyword": keyword,
            "payload": _condition_payload(actual, source_text)}


def _response_connector_record(source_text: str, start: int, end: int) -> dict:
    raw = source_text[start:end]
    compact = re.sub(r"\s+", "", raw).lower()
    kinds = {",": "comma", ",then": "comma_then"}
    if compact not in kinds:
        raise ValueError(f"unsupported condition/response connector: {raw!r}")
    leading = len(raw) - len(raw.lstrip())
    trailing = len(raw) - len(raw.rstrip())
    span = {"start": start + leading, "end": end - trailing}
    return {"kind": kinds[compact], "span": span,
            "source": _fragment(source_text, span)}


def _requirement_condition_structure(requirement: dict, source_text: str) -> dict:
    patterns = [item for item in direct_syntax_rule_children(requirement)
                if item.get("name") in {"WithoutCondition", "WithCondition"}]
    pattern = _only(patterns, "Requirement selected pattern")
    system_response = _only(
        _rule_nodes(pattern, "SystemResponse"), "Requirement SystemResponse")
    system_record = {
        **_span_source(system_response, source_text),
        "system_name": _direct_assignment_record(
            system_response, source_text, {"system_name"},
            "SystemResponse system_name"),
        "modality": _direct_assignment_record(
            system_response, source_text, {"modal", "modal_verb"},
            "SystemResponse modality"),
    }
    if pattern.get("name") == "WithoutCondition":
        return {"kind": "without_condition", **_span_source(pattern, source_text),
                "system_response": system_record}
    condition_nodes = _rule_nodes(pattern, "ConditionStructure")
    if not condition_nodes:
        raise ValueError("WithCondition has no ConditionStructure")
    conditions = []
    previous_end: int | None = None
    for index, condition in enumerate(condition_nodes):
        connector = None if previous_end is None else _connector_record(
            source_text, previous_end, condition["span"]["start"])
        conditions.append({
            "index": index, **_span_source(condition, source_text),
            "connector_before": connector,
            "condition": _condition_structure_record(condition, source_text),
        })
        previous_end = condition["span"]["end"]
    response_connector = _response_connector_record(
        source_text, condition_nodes[-1]["span"]["end"],
        system_response["span"]["start"])
    return {"kind": "with_condition", **_span_source(pattern, source_text),
            "conditions": conditions, "response_connector": response_connector,
            "system_response": system_record}


def _atomic_option(atomic: dict, feature: str, source_text: str) -> dict | None:
    owner = atomic.get("name") or atomic.get("kind") or "syntax node"
    assignments = _owned_nodes(atomic, kind="assignment", feature=feature)
    if len(assignments) > 1:
        raise ValueError(f"{owner} has multiple {feature} assignments")
    if not assignments:
        return None
    assignment = assignments[0]
    facts = [fact for item in walk_syntax_tree(assignment.get("child") or {})
             if (fact := _leaf_fact(item, source_text)) is not None]
    if len(facts) != 1:
        raise ValueError(f"{owner} {feature} must contain one value")
    return {"span": copy.deepcopy(assignment["span"]),
            "source": _fragment(source_text, assignment["span"]),
            "value": facts[0]}


def _frequency_record(atomic: dict, source_text: str) -> dict | None:
    frequency = _atomic_option(atomic, "frequency", source_text)
    if frequency is None:
        return None
    every_tokens = [item for item in _owned_nodes(atomic, kind="literal")
                    if item.get("value") == "every"]
    every = _only(every_tokens, "AtomicSystemResponse every token")
    span = {"start": every["span"]["start"], "end": frequency["span"]["end"]}
    return {"span": span, "source": _fragment(source_text, span),
            "keyword": {"value": "every", **_span_source(every, source_text)},
            "value": frequency["value"]}


def _action_record(atomic: dict, source_text: str) -> dict:
    phrases = _rule_nodes(atomic, "ActionPhrase")
    actions = direct_syntax_rule_children(phrases[0]) if len(phrases) == 1 else []
    if len(actions) != 1:
        raise ValueError(
            f"AtomicSystemResponse must select exactly one ActionPhrase rule, got {len(actions)}")
    action = actions[0]
    span = copy.deepcopy(action.get("span") or {})
    return {
        "rule_id": action.get("name"), "span": span,
        "source": _fragment(source_text, span),
        "assignments": _assignment_records(action, source_text),
    }


def _normalized_identifier(surface: str) -> str:
    return ".".join(part[1:] if part.startswith("^") else part
                    for part in surface.split("."))


def _declaration_records(tree: dict, source_text: str,
                         linking: SemanticLinkResult) -> list[dict]:
    candidates: dict[tuple[str, int, int], list[dict]] = {}
    for node in walk_syntax_tree(tree):
        if node.get("kind") != "rule":
            continue
        names = _owned_nodes(node, kind="assignment", feature="name")
        if len(names) != 1:
            continue
        name_span = names[0].get("span") or {}
        key = (node.get("name"), name_span.get("start"), name_span.get("end"))
        candidates.setdefault(key, []).append(node)

    records = []
    for index, symbol in enumerate(linking.symbols):
        name_span = copy.deepcopy(symbol.get("span") or {})
        key = (symbol.get("declaration_rule"), name_span.get("start"),
               name_span.get("end"))
        declaration = _only(
            candidates.get(key, []),
            f"linked declaration {symbol.get('symbol_id')}")
        span = copy.deepcopy(declaration.get("span") or {})
        records.append({
            "index": index,
            "symbol_id": symbol.get("symbol_id"),
            "rule_id": symbol.get("declaration_rule"),
            "name": symbol.get("name"),
            "qualified_name": symbol.get("qualified_name"),
            "span": span,
            "source": _fragment(source_text, span),
            "name_span": name_span,
            "name_source": _fragment(source_text, name_span),
            "tree_path": symbol.get("tree_path"),
            "assignments": _assignment_records(declaration, source_text),
        })
    return records


def _instance_records(tree: dict, source_text: str) -> list[dict]:
    instances = [node for node in walk_syntax_tree(tree)
                 if node.get("kind") == "rule" and node.get("name") in {
                     "NonUIComponentInstance", "UIComponentInstance"}]
    instances.sort(key=lambda node: (
        (node.get("span") or {}).get("start", -1),
        (node.get("span") or {}).get("end", -1),
        node.get("name", ""),
    ))
    kinds = {
        "NonUIComponentInstance": "non_ui_component",
        "UIComponentInstance": "ui_component",
    }
    return [{
        "index": index,
        "kind": kinds[node["name"]],
        **_span_source(node, source_text),
        "rule": _rule_record(node, source_text),
    } for index, node in enumerate(instances)]


def _linking_audit(linking: SemanticLinkResult, grammar: GrammarIR,
                   source_text: str) -> dict:
    references = []
    for index, reference in enumerate(linking.references):
        span = copy.deepcopy(reference.get("span") or {})
        references.append({
            "index": index,
            "target": reference.get("target"),
            "terminal": reference.get("terminal"),
            "surface": reference.get("surface"),
            "span": span,
            "source": _fragment(source_text, span),
            "tree_path": reference.get("tree_path"),
            "status": reference.get("status"),
            "compatible_declaration_rules": copy.deepcopy(
                reference.get("compatible_declaration_rules")),
            "candidate_symbol_ids": copy.deepcopy(
                reference.get("candidate_symbol_ids")),
            "resolved_symbol_id": reference.get("resolved_symbol_id"),
        })
    return {
        "checked": linking.checked,
        "succeeded": linking.succeeded,
        "scope": "same_document",
        "external_scope_used": False,
        "grammar_inventory": copy.deepcopy(grammar_linking_inventory(grammar)),
        "symbol_count": len(linking.symbols),
        "reference_count": len(linking.references),
        "references": references,
    }


def _document(tree: dict, parsed: SyntaxParseResult, source_text: str,
              linking: SemanticLinkResult, grammar: GrammarIR) -> dict:
    requirements = _rule_nodes(tree, "Requirement")
    projected_requirements = []
    for requirement_index, requirement in enumerate(requirements):
        atomic_responses = _rule_nodes(requirement, "AtomicSystemResponse")
        atomic_index_by_node = {id(node): index
                                for index, node in enumerate(atomic_responses)}
        projected_responses = []
        for response_index, atomic in enumerate(atomic_responses):
            span = copy.deepcopy(atomic.get("span") or {})
            projected_responses.append({
                "index": response_index, "span": span,
                "source": _fragment(source_text, span),
                "modality": _atomic_option(atomic, "modal_verb", source_text),
                "negation": _atomic_option(atomic, "not", source_text),
                "frequency": _frequency_record(atomic, source_text),
                "action": _action_record(atomic, source_text),
            })
        span = copy.deepcopy(requirement.get("span") or {})
        scopes = _rule_nodes(requirement, "Scope")
        if len(scopes) > 1:
            raise ValueError(f"Requirement Scope must occur at most once, got {len(scopes)}")
        scope = None
        if scopes:
            scope_rule = scopes[0]
            scope = {
                **_span_source(scope_rule, source_text),
                "assignments": _assignment_records(scope_rule, source_text),
            }
        projected_requirements.append({
            "index": requirement_index, "span": span,
            "source": _fragment(source_text, span),
            "scope": scope,
            "atomic_responses": projected_responses,
            "condition_structure": _requirement_condition_structure(
                requirement, source_text),
            "response_structure": _response_structure(
                requirement, source_text, atomic_index_by_node),
        })
    return {
        "repository_document_schema_version": REPOSITORY_DOCUMENT_SCHEMA_VERSION,
        "root_rule": parsed.start_rule,
        "grammar_source_sha256": parsed.grammar_source_sha256,
        "source_sha256": parsed.source_sha256,
        "declarations": _declaration_records(tree, source_text, linking),
        "instances": _instance_records(tree, source_text),
        "linking_audit": _linking_audit(linking, grammar, source_text),
        "requirements": projected_requirements,
    }


def historical_repository_document_0_4(document: dict) -> dict:
    """Derive the frozen 0.4.0 projection from an active 0.5.0 document."""
    if not isinstance(document, dict) or \
            document.get("repository_document_schema_version") != \
            REPOSITORY_DOCUMENT_SCHEMA_VERSION:
        raise ValueError("historical projection input must use Repository document 0.5.0")
    historical = copy.deepcopy(document)
    historical["repository_document_schema_version"] = "0.4.0"
    requirements = historical.get("requirements")
    if not isinstance(requirements, list):
        raise ValueError("historical projection input requirements must be a list")
    for index, requirement in enumerate(requirements):
        if not isinstance(requirement, dict):
            raise ValueError(f"historical projection requirement[{index}] must be a mapping")
        if "scope" not in requirement:
            raise ValueError(f"historical projection requirement[{index}] has no scope field")
        requirement.pop("scope")
        structure = requirement.get("condition_structure")
        system_response = structure.get("system_response") \
            if isinstance(structure, dict) else None
        if not isinstance(system_response, dict):
            raise ValueError(
                f"historical projection requirement[{index}] has no system_response")
        if "system_name" not in system_response or "modality" not in system_response:
            raise ValueError(
                f"historical projection requirement[{index}] has incomplete SystemResponse")
        system_response.pop("system_name")
        system_response.pop("modality")
    return historical


_VALUE_KEYS = {
    "cross_reference": {
        "kind", "target", "terminal", "value", "surface", "span",
        "linking_checked"},
    "terminal": {"kind", "terminal", "value", "surface", "span"},
    "enum_literal": {"kind", "name", "value", "surface", "span"},
    "literal": {"kind", "value", "surface", "span"},
}


def _record_source_problems(record: dict, source_text: str, prefix: str) -> list[str]:
    problems: list[str] = []
    try:
        if record.get("source") != _fragment(source_text, record.get("span") or {}):
            problems.append(prefix + " source/span mismatch")
    except ValueError:
        problems.append(prefix + " span is invalid")
    return problems


def _value_problems(value: object, source_text: str, prefix: str,
                    outer_span: dict | None = None) -> list[str]:
    problems: list[str] = []
    kind = value.get("kind") if isinstance(value, dict) else None
    if not isinstance(value, dict) or kind not in _VALUE_KEYS or \
            set(value) != _VALUE_KEYS.get(kind, set()):
        return [prefix + " shape is invalid"]
    if any(not isinstance(value.get(key), str) or not value.get(key)
           for key in _VALUE_KEYS[kind] - {"kind", "span", "linking_checked"}):
        problems.append(prefix + " scalar value is invalid")
    if kind == "cross_reference" and value.get("linking_checked") is not True:
        problems.append(prefix + " is not linked")
    try:
        if value.get("surface") != _fragment(source_text, value.get("span") or {}):
            problems.append(prefix + " surface/span mismatch")
    except ValueError:
        problems.append(prefix + " span is invalid")
    surface = value.get("surface")
    if isinstance(surface, str):
        expected_value = _decode_surface(surface) \
            if kind in {"cross_reference", "terminal"} else surface
        if value.get("value") != expected_value:
            problems.append(prefix + " decoded value mismatch")
    if outer_span is not None and not _contains(outer_span, value.get("span") or {}):
        problems.append(prefix + " span is outside its owner")
    return problems


def _atomic_option_problems(option: object, source_text: str, prefix: str,
                            response_span: dict, expected_kind: str | set[str],
                            expected_value: str | None = None) -> list[str]:
    if option is None:
        return []
    if not isinstance(option, dict) or set(option) != {"span", "source", "value"}:
        return [prefix + " shape is invalid"]
    problems = _record_source_problems(option, source_text, prefix)
    if not _contains(response_span, option.get("span") or {}):
        problems.append(prefix + " span is outside its response")
    problems.extend(_value_problems(
        option.get("value"), source_text, prefix + ".value", option.get("span") or {}))
    value = option.get("value")
    expected_kinds = {expected_kind} if isinstance(expected_kind, str) else set(expected_kind)
    if isinstance(value, dict) and value.get("kind") not in expected_kinds:
        problems.append(prefix + " value kind mismatch")
    if expected_value is not None and isinstance(value, dict) and \
            value.get("value") != expected_value:
        problems.append(prefix + " value mismatch")
    return problems


def _frequency_problems(frequency: object, source_text: str, prefix: str,
                        response_span: dict) -> list[str]:
    if frequency is None:
        return []
    if not isinstance(frequency, dict) or set(frequency) != {
            "span", "source", "keyword", "value"}:
        return [prefix + " shape is invalid"]
    problems = _record_source_problems(frequency, source_text, prefix)
    if not _contains(response_span, frequency.get("span") or {}):
        problems.append(prefix + " span is outside its response")
    keyword = frequency.get("keyword")
    if not isinstance(keyword, dict) or set(keyword) != {"value", "span", "source"}:
        problems.append(prefix + ".keyword shape is invalid")
    else:
        problems.extend(_record_source_problems(keyword, source_text, prefix + ".keyword"))
        if keyword.get("value") != "every" or keyword.get("source") != "every":
            problems.append(prefix + ".keyword mismatch")
        if not _contains(frequency.get("span") or {}, keyword.get("span") or {}):
            problems.append(prefix + ".keyword span is outside frequency")
    problems.extend(_value_problems(
        frequency.get("value"), source_text, prefix + ".value",
        frequency.get("span") or {}))
    value = frequency.get("value")
    if isinstance(value, dict) and value.get("kind") != "terminal":
        problems.append(prefix + " value kind mismatch")
    return problems


def _response_expression_problems(expression: object, source_text: str,
                                  prefix: str, outer_span: dict,
                                  references: list[tuple[int, dict]]) -> list[str]:
    if not isinstance(expression, dict):
        return [prefix + " must be a mapping"]
    kind = expression.get("kind")
    keys = {
        "atomic": {"kind", "span", "source", "atomic_response_index"},
        "group": {"kind", "span", "source", "expression"},
        "and": {"kind", "span", "source", "operator", "left", "right"},
        "or": {"kind", "span", "source", "operator", "left", "right"},
    }
    if kind not in keys or set(expression) != keys.get(kind, set()):
        return [prefix + " shape is invalid"]
    problems = _record_source_problems(expression, source_text, prefix)
    if not _contains(outer_span, expression.get("span") or {}):
        problems.append(prefix + " span is outside response structure")
    if kind == "atomic":
        index = expression.get("atomic_response_index")
        if type(index) is not int or index < 0:
            problems.append(prefix + " atomic response index is invalid")
        else:
            references.append((index, expression.get("span") or {}))
        return problems
    if kind == "group":
        source = expression.get("source")
        if not isinstance(source, str) or not source.strip().startswith("(") or \
                not source.strip().endswith(")"):
            problems.append(prefix + " grouping tokens are invalid")
        problems.extend(_response_expression_problems(
            expression.get("expression"), source_text, prefix + ".expression",
            expression.get("span") or {}, references))
        return problems
    operator = expression.get("operator")
    if not isinstance(operator, dict) or set(operator) != {"kind", "span", "source"}:
        problems.append(prefix + ".operator shape is invalid")
    else:
        problems.extend(_record_source_problems(operator, source_text, prefix + ".operator"))
        normalized = re.sub(r"\s+", "", operator.get("source", ""))
        if operator.get("kind") != kind or normalized not in {kind, "," + kind}:
            problems.append(prefix + ".operator mismatch")
        if not _contains(expression.get("span") or {}, operator.get("span") or {}):
            problems.append(prefix + ".operator span is outside expression")
    for side in ("left", "right"):
        problems.extend(_response_expression_problems(
            expression.get(side), source_text, prefix + "." + side,
            expression.get("span") or {}, references))
    left = expression.get("left")
    right = expression.get("right")
    if isinstance(left, dict) and isinstance(right, dict) and isinstance(operator, dict):
        if left.get("span", {}).get("start") != expression.get("span", {}).get("start") or \
                right.get("span", {}).get("end") != expression.get("span", {}).get("end"):
            problems.append(prefix + " operand boundaries mismatch")
        if type(left.get("span", {}).get("end")) is int and \
                type(operator.get("span", {}).get("start")) is int and \
                type(operator.get("span", {}).get("end")) is int and \
                type(right.get("span", {}).get("start")) is int and not (
                    left["span"]["end"] <= operator["span"]["start"] <=
                    operator["span"]["end"] <= right["span"]["start"]):
            problems.append(prefix + " operator order mismatch")
    return problems


def _response_structure_problems(structure: object, source_text: str, prefix: str,
                                 requirement_span: dict) \
        -> tuple[list[str], list[tuple[int, dict]]]:
    references: list[tuple[int, dict]] = []
    if not isinstance(structure, dict):
        return [prefix + " must be a mapping"], references
    kind = structure.get("kind")
    expected = {
        "expression": {"kind", "span", "source", "expression"},
        "itemized": {"kind", "span", "source", "in_sequence", "items"},
    }
    if kind not in expected or set(structure) != expected.get(kind, set()):
        return [prefix + " shape is invalid"], references
    problems = _record_source_problems(structure, source_text, prefix)
    if not _contains(requirement_span, structure.get("span") or {}):
        problems.append(prefix + " span is outside requirement")
    if kind == "expression":
        problems.extend(_response_expression_problems(
            structure.get("expression"), source_text, prefix + ".expression",
            structure.get("span") or {}, references))
        return problems, references
    in_sequence = structure.get("in_sequence")
    if in_sequence is not None:
        if not isinstance(in_sequence, dict) or set(in_sequence) != {"span", "source"}:
            problems.append(prefix + ".in_sequence shape is invalid")
        else:
            problems.extend(_record_source_problems(
                in_sequence, source_text, prefix + ".in_sequence"))
            if re.sub(r"\s+", "", in_sequence.get("source", "")) != "insequence":
                problems.append(prefix + ".in_sequence tokens mismatch")
            if not _contains(structure.get("span") or {}, in_sequence.get("span") or {}):
                problems.append(prefix + ".in_sequence span is outside structure")
    items = structure.get("items")
    if not isinstance(items, list) or not items:
        problems.append(prefix + ".items must be a non-empty list")
        return problems, references
    connector_kinds = {",": "comma", "and": "and", "or": "or",
                       ",and": "comma_and", ",or": "comma_or"}
    for item_index, item in enumerate(items):
        iprefix = prefix + f".item[{item_index}]"
        if not isinstance(item, dict) or set(item) != {
                "index", "span", "source", "connector_before", "bullet",
                "atomic_response_index"}:
            problems.append(iprefix + " shape is invalid")
            continue
        if item.get("index") != item_index:
            problems.append(iprefix + " index mismatch")
        problems.extend(_record_source_problems(item, source_text, iprefix))
        if not _contains(structure.get("span") or {}, item.get("span") or {}):
            problems.append(iprefix + " span is outside structure")
        connector = item.get("connector_before")
        if item_index == 0 and connector is not None:
            problems.append(iprefix + " first item must not have a connector")
        elif connector is not None:
            if not isinstance(connector, dict) or set(connector) != {
                    "kind", "span", "source"}:
                problems.append(iprefix + ".connector shape is invalid")
            else:
                problems.extend(_record_source_problems(
                    connector, source_text, iprefix + ".connector"))
                compact = re.sub(r"\s+", "", connector.get("source", ""))
                if connector_kinds.get(compact) != connector.get("kind"):
                    problems.append(iprefix + ".connector mismatch")
        bullet = item.get("bullet")
        if not isinstance(bullet, dict) or set(bullet) != {
                "kind", "value", "span", "source"}:
            problems.append(iprefix + ".bullet shape is invalid")
        else:
            problems.extend(_record_source_problems(
                bullet, source_text, iprefix + ".bullet"))
            expected_kind = "hyphen" if bullet.get("source") == "-" else \
                "integer" if str(bullet.get("source", "")).isdigit() else None
            if bullet.get("kind") != expected_kind or \
                    bullet.get("value") != bullet.get("source"):
                problems.append(iprefix + ".bullet mismatch")
            if not _contains(item.get("span") or {}, bullet.get("span") or {}):
                problems.append(iprefix + ".bullet span is outside item")
        atomic_index = item.get("atomic_response_index")
        if type(atomic_index) is not int or atomic_index < 0:
            problems.append(iprefix + " atomic response index is invalid")
        else:
            references.append((atomic_index, item.get("span") or {}))
    return problems, references


def _assignments_problems(assignments: object, source_text: str, prefix: str,
                          owner_span: dict) -> list[str]:
    if not isinstance(assignments, list):
        return [prefix + " must be a list"]
    problems: list[str] = []
    previous_start = -1
    for assignment_index, assignment in enumerate(assignments):
        aprefix = prefix + f"[{assignment_index}]"
        if not isinstance(assignment, dict) or set(assignment) != {
                "owner_rule", "rule_path", "feature", "operator",
                "span", "source", "values"}:
            problems.append(aprefix + " shape is invalid")
            continue
        if not isinstance(assignment.get("rule_path"), list) or \
                not assignment.get("rule_path") or \
                assignment.get("owner_rule") != assignment.get("rule_path", [None])[-1]:
            problems.append(aprefix + " rule path is invalid")
        if not isinstance(assignment.get("feature"), str) or \
                not assignment.get("feature") or \
                assignment.get("operator") not in {"=", "+=", "?="}:
            problems.append(aprefix + " feature/operator is invalid")
        problems.extend(_record_source_problems(assignment, source_text, aprefix))
        if not _contains(owner_span, assignment.get("span") or {}):
            problems.append(aprefix + " span is outside its owner")
        start = (assignment.get("span") or {}).get("start")
        if type(start) is int and start < previous_start:
            problems.append(aprefix + " source order mismatch")
        if type(start) is int:
            previous_start = start
        values = assignment.get("values")
        if not isinstance(values, list):
            problems.append(aprefix + " values must be a list")
            continue
        for value_index, value in enumerate(values):
            problems.extend(_value_problems(
                value, source_text, aprefix + f".value[{value_index}]",
                assignment.get("span") or {}))
    return problems


def _rule_record_problems(rule: object, source_text: str, prefix: str,
                          outer_span: dict) -> list[str]:
    if not isinstance(rule, dict) or set(rule) != {
            "rule_id", "span", "source", "assignments"}:
        return [prefix + " shape is invalid"]
    problems = _record_source_problems(rule, source_text, prefix)
    if not isinstance(rule.get("rule_id"), str) or not rule.get("rule_id"):
        problems.append(prefix + " rule_id is invalid")
    if not _contains(outer_span, rule.get("span") or {}):
        problems.append(prefix + " span is outside its owner")
    problems.extend(_assignments_problems(
        rule.get("assignments"), source_text, prefix + ".assignment",
        rule.get("span") or {}))
    return problems


def _logical_operator_problems(expression: dict, source_text: str,
                               prefix: str) -> list[str]:
    problems: list[str] = []
    kind = expression.get("kind")
    operator = expression.get("operator")
    if not isinstance(operator, dict) or set(operator) != {"kind", "span", "source"}:
        problems.append(prefix + ".operator shape is invalid")
    else:
        problems.extend(_record_source_problems(operator, source_text, prefix + ".operator"))
        normalized = re.sub(r"\s+", "", operator.get("source", ""))
        if operator.get("kind") != kind or normalized not in {kind, "," + str(kind)}:
            problems.append(prefix + ".operator mismatch")
        if not _contains(expression.get("span") or {}, operator.get("span") or {}):
            problems.append(prefix + ".operator span is outside expression")
    left = expression.get("left")
    right = expression.get("right")
    if isinstance(left, dict) and isinstance(right, dict) and isinstance(operator, dict):
        if left.get("span", {}).get("start") != expression.get("span", {}).get("start") or \
                right.get("span", {}).get("end") != expression.get("span", {}).get("end"):
            problems.append(prefix + " operand boundaries mismatch")
        if type(left.get("span", {}).get("end")) is int and \
                type(operator.get("span", {}).get("start")) is int and \
                type(operator.get("span", {}).get("end")) is int and \
                type(right.get("span", {}).get("start")) is int and not (
                    left["span"]["end"] <= operator["span"]["start"] <=
                    operator["span"]["end"] <= right["span"]["start"]):
            problems.append(prefix + " operator order mismatch")
    return problems


def _condition_leaf_problems(condition: object, source_text: str, prefix: str,
                             outer_span: dict) -> list[str]:
    if not isinstance(condition, dict) or set(condition) != {
            "kind", "span", "source", "rule"} or condition.get("kind") != "condition":
        return [prefix + " shape is invalid"]
    problems = _record_source_problems(condition, source_text, prefix)
    if not _contains(outer_span, condition.get("span") or {}):
        problems.append(prefix + " span is outside precondition structure")
    problems.extend(_rule_record_problems(
        condition.get("rule"), source_text, prefix + ".rule",
        condition.get("span") or {}))
    return problems


def _precondition_expression_problems(expression: object, source_text: str,
                                      prefix: str, outer_span: dict) -> list[str]:
    if not isinstance(expression, dict):
        return [prefix + " must be a mapping"]
    kind = expression.get("kind")
    expected = {
        "condition": {"kind", "span", "source", "rule"},
        "group": {"kind", "span", "source", "preconditions"},
        "and": {"kind", "span", "source", "operator", "left", "right"},
        "or": {"kind", "span", "source", "operator", "left", "right"},
    }
    if kind not in expected or set(expression) != expected.get(kind, set()):
        return [prefix + " shape is invalid"]
    if kind == "condition":
        return _condition_leaf_problems(expression, source_text, prefix, outer_span)
    problems = _record_source_problems(expression, source_text, prefix)
    if not _contains(outer_span, expression.get("span") or {}):
        problems.append(prefix + " span is outside precondition structure")
    if kind == "group":
        source = expression.get("source")
        if not isinstance(source, str) or not source.strip().startswith("(") or \
                not source.strip().endswith(")"):
            problems.append(prefix + " grouping tokens are invalid")
        problems.extend(_precondition_structure_problems(
            expression.get("preconditions"), source_text, prefix + ".preconditions",
            expression.get("span") or {}))
        return problems
    problems.extend(_logical_operator_problems(expression, source_text, prefix))
    for side in ("left", "right"):
        problems.extend(_precondition_expression_problems(
            expression.get(side), source_text, prefix + "." + side,
            expression.get("span") or {}))
    return problems


def _connector_problems(connector: object, source_text: str, prefix: str,
                        outer_span: dict) -> list[str]:
    if not isinstance(connector, dict) or set(connector) != {"kind", "span", "source"}:
        return [prefix + " shape is invalid"]
    problems = _record_source_problems(connector, source_text, prefix)
    kinds = {",": "comma", "and": "and", "or": "or",
             ",and": "comma_and", ",or": "comma_or"}
    compact = re.sub(r"\s+", "", connector.get("source", "")).lower()
    if kinds.get(compact) != connector.get("kind"):
        problems.append(prefix + " mismatch")
    if not _contains(outer_span, connector.get("span") or {}):
        problems.append(prefix + " span is outside its owner")
    return problems


def _bullet_problems(bullet: object, source_text: str, prefix: str,
                     outer_span: dict) -> list[str]:
    if not isinstance(bullet, dict) or set(bullet) != {
            "kind", "value", "span", "source"}:
        return [prefix + " shape is invalid"]
    problems = _record_source_problems(bullet, source_text, prefix)
    expected_kind = "hyphen" if bullet.get("source") == "-" else \
        "integer" if str(bullet.get("source", "")).isdigit() else None
    if bullet.get("kind") != expected_kind or bullet.get("value") != bullet.get("source"):
        problems.append(prefix + " mismatch")
    if not _contains(outer_span, bullet.get("span") or {}):
        problems.append(prefix + " span is outside its owner")
    return problems


def _precondition_structure_problems(structure: object, source_text: str,
                                     prefix: str, outer_span: dict) -> list[str]:
    if not isinstance(structure, dict):
        return [prefix + " must be a mapping"]
    kind = structure.get("kind")
    expected = {
        "expression": {"kind", "span", "source", "expression"},
        "itemized": {"kind", "span", "source", "items"},
    }
    if kind not in expected or set(structure) != expected.get(kind, set()):
        return [prefix + " shape is invalid"]
    problems = _record_source_problems(structure, source_text, prefix)
    if not _contains(outer_span, structure.get("span") or {}):
        problems.append(prefix + " span is outside its owner")
    if kind == "expression":
        problems.extend(_precondition_expression_problems(
            structure.get("expression"), source_text, prefix + ".expression",
            structure.get("span") or {}))
        return problems
    items = structure.get("items")
    if not isinstance(items, list) or not items:
        problems.append(prefix + ".items must be a non-empty list")
        return problems
    for item_index, item in enumerate(items):
        iprefix = prefix + f".item[{item_index}]"
        if not isinstance(item, dict) or set(item) != {
                "index", "span", "source", "connector_before", "bullet", "condition"}:
            problems.append(iprefix + " shape is invalid")
            continue
        if item.get("index") != item_index:
            problems.append(iprefix + " index mismatch")
        problems.extend(_record_source_problems(item, source_text, iprefix))
        if not _contains(structure.get("span") or {}, item.get("span") or {}):
            problems.append(iprefix + " span is outside itemized conditions")
        connector = item.get("connector_before")
        if item_index == 0 and connector is not None:
            problems.append(iprefix + " first item must not have a connector")
        elif item_index and connector is None:
            problems.append(iprefix + " connector is missing")
        elif connector is not None:
            problems.extend(_connector_problems(
                connector, source_text, iprefix + ".connector",
                structure.get("span") or {}))
        problems.extend(_bullet_problems(
            item.get("bullet"), source_text, iprefix + ".bullet",
            item.get("span") or {}))
        problems.extend(_condition_leaf_problems(
            item.get("condition"), source_text, iprefix + ".condition",
            item.get("span") or {}))
    return problems


def _trigger_action_expression_problems(expression: object, source_text: str,
                                        prefix: str, outer_span: dict,
                                        references: list[tuple[int, dict]]) -> list[str]:
    if not isinstance(expression, dict):
        return [prefix + " must be a mapping"]
    kind = expression.get("kind")
    expected = {
        "atomic": {"kind", "span", "source", "atomic_action_index"},
        "group": {"kind", "span", "source", "expression"},
        "and": {"kind", "span", "source", "operator", "left", "right"},
        "or": {"kind", "span", "source", "operator", "left", "right"},
    }
    if kind not in expected or set(expression) != expected.get(kind, set()):
        return [prefix + " shape is invalid"]
    problems = _record_source_problems(expression, source_text, prefix)
    if not _contains(outer_span, expression.get("span") or {}):
        problems.append(prefix + " span is outside Trigger")
    if kind == "atomic":
        index = expression.get("atomic_action_index")
        if type(index) is not int or index < 0:
            problems.append(prefix + " atomic action index is invalid")
        else:
            references.append((index, expression.get("span") or {}))
        return problems
    if kind == "group":
        source = expression.get("source")
        if not isinstance(source, str) or not source.strip().startswith("(") or \
                not source.strip().endswith(")"):
            problems.append(prefix + " grouping tokens are invalid")
        problems.extend(_trigger_action_expression_problems(
            expression.get("expression"), source_text, prefix + ".expression",
            expression.get("span") or {}, references))
        return problems
    problems.extend(_logical_operator_problems(expression, source_text, prefix))
    for side in ("left", "right"):
        problems.extend(_trigger_action_expression_problems(
            expression.get(side), source_text, prefix + "." + side,
            expression.get("span") or {}, references))
    return problems


def _trigger_problems(trigger: object, source_text: str, prefix: str,
                      outer_span: dict) -> list[str]:
    if not isinstance(trigger, dict) or set(trigger) != {
            "kind", "span", "source", "assignments", "atomic_actions",
            "action_structure"} or trigger.get("kind") != "trigger":
        return [prefix + " shape is invalid"]
    problems = _record_source_problems(trigger, source_text, prefix)
    if not _contains(outer_span, trigger.get("span") or {}):
        problems.append(prefix + " span is outside condition")
    problems.extend(_assignments_problems(
        trigger.get("assignments"), source_text, prefix + ".assignment",
        trigger.get("span") or {}))
    actions = trigger.get("atomic_actions")
    if not isinstance(actions, list) or not actions:
        problems.append(prefix + ".atomic_actions must be a non-empty list")
        return problems
    for action_index, action in enumerate(actions):
        aprefix = prefix + f".atomic_action[{action_index}]"
        if not isinstance(action, dict) or set(action) != {
                "index", "span", "source", "negation", "action"}:
            problems.append(aprefix + " shape is invalid")
            continue
        if action.get("index") != action_index:
            problems.append(aprefix + " index mismatch")
        problems.extend(_record_source_problems(action, source_text, aprefix))
        if not _contains(trigger.get("span") or {}, action.get("span") or {}):
            problems.append(aprefix + " span is outside Trigger")
        negation = action.get("negation")
        if negation is not None:
            if not isinstance(negation, dict) or set(negation) != {"span", "source"}:
                problems.append(aprefix + ".negation shape is invalid")
            else:
                problems.extend(_record_source_problems(
                    negation, source_text, aprefix + ".negation"))
                if re.sub(r"\s+", "", negation.get("source", "")).lower() not in {
                        "donot", "doesnot"}:
                    problems.append(aprefix + ".negation tokens mismatch")
                if not _contains(action.get("span") or {}, negation.get("span") or {}):
                    problems.append(aprefix + ".negation span is outside action")
        problems.extend(_rule_record_problems(
            action.get("action"), source_text, aprefix + ".action",
            action.get("span") or {}))
    references: list[tuple[int, dict]] = []
    problems.extend(_trigger_action_expression_problems(
        trigger.get("action_structure"), source_text, prefix + ".action_structure",
        trigger.get("span") or {}, references))
    if [item[0] for item in references] != list(range(len(actions))):
        problems.append(prefix + " action structure/index coverage mismatch")
    for reference_index, reference_span in references:
        if 0 <= reference_index < len(actions) and \
                reference_span != actions[reference_index].get("span"):
            problems.append(prefix + " action structure span/index mismatch")
    return problems


def _condition_payload_problems(payload: object, source_text: str, prefix: str,
                                outer_span: dict) -> list[str]:
    if not isinstance(payload, dict):
        return [prefix + " must be a mapping"]
    kind = payload.get("kind")
    if kind in {"expression", "itemized"}:
        return _precondition_structure_problems(
            payload, source_text, prefix, outer_span)
    if kind == "trigger":
        return _trigger_problems(payload, source_text, prefix, outer_span)
    if kind == "condition":
        return _condition_leaf_problems(payload, source_text, prefix, outer_span)
    if kind in {"free_expression", "time"}:
        if set(payload) != {"kind", "span", "source", "rule"}:
            return [prefix + " shape is invalid"]
        problems = _record_source_problems(payload, source_text, prefix)
        if not _contains(outer_span, payload.get("span") or {}):
            problems.append(prefix + " span is outside condition")
        problems.extend(_rule_record_problems(
            payload.get("rule"), source_text, prefix + ".rule",
            payload.get("span") or {}))
        return problems
    if kind == "frequency":
        if set(payload) != {"kind", "span", "source", "value"}:
            return [prefix + " shape is invalid"]
        problems = _record_source_problems(payload, source_text, prefix)
        if not _contains(outer_span, payload.get("span") or {}):
            problems.append(prefix + " span is outside condition")
        problems.extend(_value_problems(
            payload.get("value"), source_text, prefix + ".value",
            payload.get("span") or {}))
        return problems
    return [prefix + " kind is invalid"]


def _condition_structure_record_problems(condition: object, source_text: str,
                                         prefix: str, outer_span: dict) -> list[str]:
    if not isinstance(condition, dict) or set(condition) != {
            "kind", "rule_path", "span", "source", "keyword", "payload"}:
        return [prefix + " shape is invalid"]
    kind = condition.get("kind")
    rule_paths = {
        "while": ["ConditionStructure", "WhileStructure"],
        "when": ["ConditionStructure", "WhenStructure"],
        "where": ["ConditionStructure", "WhereStructure"],
        "if": ["ConditionStructure", "IfStructure"],
        "before": ["ConditionStructure", "TemporalStructure", "RepeatOnce"],
        "after": ["ConditionStructure", "TemporalStructure", "RepeatOnce"],
        "every": ["ConditionStructure", "TemporalStructure", "Frequently"],
    }
    problems = _record_source_problems(condition, source_text, prefix)
    if kind not in rule_paths or condition.get("rule_path") != rule_paths.get(kind):
        problems.append(prefix + " kind/rule path mismatch")
    if not _contains(outer_span, condition.get("span") or {}):
        problems.append(prefix + " span is outside WithCondition")
    keyword = condition.get("keyword")
    problems.extend(_atomic_option_problems(
        keyword, source_text, prefix + ".keyword", condition.get("span") or {},
        {"literal", "enum_literal"}))
    value = keyword.get("value") if isinstance(keyword, dict) else None
    if isinstance(value, dict) and str(value.get("value", "")).lower() != kind:
        problems.append(prefix + ".keyword kind mismatch")
    payload = condition.get("payload")
    problems.extend(_condition_payload_problems(
        payload, source_text, prefix + ".payload", condition.get("span") or {}))
    payload_kind = payload.get("kind") if isinstance(payload, dict) else None
    allowed_payloads = {
        "while": {"expression", "itemized"},
        "when": {"trigger", "free_expression"},
        "where": {"free_expression"},
        "if": {"expression", "itemized", "trigger"},
        "before": {"trigger", "time", "condition"},
        "after": {"trigger", "time", "condition"},
        "every": {"time", "frequency"},
    }
    if kind in allowed_payloads and payload_kind not in allowed_payloads[kind]:
        problems.append(prefix + " kind/payload mismatch")
    return problems


def _scope_problems(scope: object, source_text: str, prefix: str,
                    requirement_span: dict) -> list[str]:
    if scope is None:
        return []
    if not isinstance(scope, dict) or set(scope) != {
            "span", "source", "assignments"}:
        return [prefix + " shape is invalid"]
    problems = _record_source_problems(scope, source_text, prefix)
    if not _contains(requirement_span, scope.get("span") or {}):
        problems.append(prefix + " span is outside requirement")
    assignments = scope.get("assignments")
    problems.extend(_assignments_problems(
        assignments, source_text, prefix + ".assignment", scope.get("span") or {}))
    if not isinstance(assignments, list):
        return problems
    allowed = {
        ("Scope", "scope_text"),
        ("ScopeText", "modifier"),
        ("ScopeText", "scope"),
    }
    for index, assignment in enumerate(assignments):
        if not isinstance(assignment, dict):
            continue
        pair = (assignment.get("owner_rule"), assignment.get("feature"))
        rule_path = assignment.get("rule_path")
        if pair not in allowed or not isinstance(rule_path, list) or \
                not rule_path or rule_path[0] != "Scope":
            problems.append(prefix + f".assignment[{index}] owner/feature is invalid")
    wrapper_values = [
        item for item in assignments
        if isinstance(item, dict) and item.get("rule_path") == ["Scope"]
        and item.get("feature") == "scope_text"
    ]
    scope_values = [
        item for item in assignments
        if isinstance(item, dict) and item.get("rule_path") == ["Scope", "ScopeText"]
        and item.get("feature") == "scope"
    ]
    if len(wrapper_values) not in {1, 2} or len(scope_values) != len(wrapper_values):
        problems.append(prefix + " scope_text/value coverage mismatch")
    for index, assignment in enumerate(scope_values):
        values = assignment.get("values")
        if not isinstance(values, list) or len(values) != 1 or \
                not isinstance(values[0], dict) or values[0].get("kind") != "terminal":
            problems.append(prefix + f".scope_value[{index}] is invalid")
    return problems


def _system_response_assignment_problems(
    assignment: object,
    source_text: str,
    prefix: str,
    system_span: dict,
    *,
    features: set[str],
    value_kinds: set[str],
) -> list[str]:
    problems = _assignments_problems(
        [assignment], source_text, prefix, system_span)
    if not isinstance(assignment, dict):
        return problems
    if assignment.get("rule_path") != ["SystemResponse"] or \
            assignment.get("owner_rule") != "SystemResponse" or \
            assignment.get("feature") not in features or \
            assignment.get("operator") != "=":
        problems.append(prefix + " wrapper assignment is invalid")
    values = assignment.get("values")
    if not isinstance(values, list) or len(values) != 1 or \
            not isinstance(values[0], dict) or values[0].get("kind") not in value_kinds:
        problems.append(prefix + " value is invalid")
    return problems


def _system_response_problems(system_response: object, source_text: str,
                              prefix: str, pattern_span: dict) -> list[str]:
    if not isinstance(system_response, dict) or set(system_response) != {
            "span", "source", "system_name", "modality"}:
        return [prefix + " shape is invalid"]
    problems = _record_source_problems(system_response, source_text, prefix)
    if not _contains(pattern_span, system_response.get("span") or {}):
        problems.append(prefix + " span is outside pattern")
    problems.extend(_system_response_assignment_problems(
        system_response.get("system_name"), source_text,
        prefix + ".system_name", system_response.get("span") or {},
        features={"system_name"}, value_kinds={"cross_reference"}))
    problems.extend(_system_response_assignment_problems(
        system_response.get("modality"), source_text,
        prefix + ".modality", system_response.get("span") or {},
        features={"modal", "modal_verb"},
        value_kinds={"enum_literal", "literal"}))
    modality = system_response.get("modality")
    values = modality.get("values") if isinstance(modality, dict) else None
    if isinstance(values, list) and len(values) == 1 and \
            isinstance(values[0], dict) and \
            str(values[0].get("value", "")).lower() not in {"must", "shall"}:
        problems.append(prefix + ".modality value mismatch")
    return problems


def _requirement_condition_structure_problems(structure: object, source_text: str,
                                              prefix: str,
                                              requirement_span: dict) -> list[str]:
    if not isinstance(structure, dict):
        return [prefix + " must be a mapping"]
    kind = structure.get("kind")
    expected = {
        "without_condition": {"kind", "span", "source", "system_response"},
        "with_condition": {
            "kind", "span", "source", "conditions", "response_connector",
            "system_response"},
    }
    if kind not in expected or set(structure) != expected.get(kind, set()):
        return [prefix + " shape is invalid"]
    problems = _record_source_problems(structure, source_text, prefix)
    if not _contains(requirement_span, structure.get("span") or {}):
        problems.append(prefix + " span is outside requirement")
    system_response = structure.get("system_response")
    problems.extend(_system_response_problems(
        system_response, source_text, prefix + ".system_response",
        structure.get("span") or {}))
    if kind == "without_condition":
        return problems
    conditions = structure.get("conditions")
    if not isinstance(conditions, list) or not conditions:
        problems.append(prefix + ".conditions must be a non-empty list")
        return problems
    for condition_index, item in enumerate(conditions):
        iprefix = prefix + f".condition[{condition_index}]"
        if not isinstance(item, dict) or set(item) != {
                "index", "span", "source", "connector_before", "condition"}:
            problems.append(iprefix + " shape is invalid")
            continue
        if item.get("index") != condition_index:
            problems.append(iprefix + " index mismatch")
        problems.extend(_record_source_problems(item, source_text, iprefix))
        if not _contains(structure.get("span") or {}, item.get("span") or {}):
            problems.append(iprefix + " span is outside WithCondition")
        connector = item.get("connector_before")
        if condition_index == 0 and connector is not None:
            problems.append(iprefix + " first condition must not have a connector")
        elif connector is not None:
            problems.extend(_connector_problems(
                connector, source_text, iprefix + ".connector",
                structure.get("span") or {}))
        problems.extend(_condition_structure_record_problems(
            item.get("condition"), source_text, iprefix + ".condition",
            item.get("span") or {}))
    response_connector = structure.get("response_connector")
    if not isinstance(response_connector, dict) or set(response_connector) != {
            "kind", "span", "source"}:
        problems.append(prefix + ".response_connector shape is invalid")
    else:
        problems.extend(_record_source_problems(
            response_connector, source_text, prefix + ".response_connector"))
        compact = re.sub(r"\s+", "", response_connector.get("source", "")).lower()
        if {",": "comma", ",then": "comma_then"}.get(compact) != \
                response_connector.get("kind"):
            problems.append(prefix + ".response_connector mismatch")
        if not _contains(structure.get("span") or {},
                         response_connector.get("span") or {}):
            problems.append(prefix + ".response_connector span is outside pattern")
    return problems


def _declarations_problems(declarations: object, source_text: str) \
        -> tuple[list[str], dict[str, dict]]:
    if not isinstance(declarations, list):
        return ["repository document declarations must be a list"], {}
    problems: list[str] = []
    symbols: dict[str, dict] = {}
    previous_start = -1
    expected_keys = {
        "index", "symbol_id", "rule_id", "name", "qualified_name",
        "span", "source", "name_span", "name_source", "tree_path",
        "assignments",
    }
    for index, declaration in enumerate(declarations):
        prefix = f"declaration[{index}]"
        if not isinstance(declaration, dict) or set(declaration) != expected_keys:
            problems.append(prefix + " shape is invalid")
            continue
        if declaration.get("index") != index:
            problems.append(prefix + " index mismatch")
        expected_symbol_id = f"SYM-{index + 1:03d}"
        symbol_id = declaration.get("symbol_id")
        if symbol_id != expected_symbol_id:
            problems.append(prefix + " symbol_id/order mismatch")
        elif symbol_id in symbols:
            problems.append(prefix + " symbol_id is duplicated")
        else:
            symbols[symbol_id] = declaration
        problems.extend(_record_source_problems(declaration, source_text, prefix))
        span = declaration.get("span") or {}
        name_span = declaration.get("name_span") or {}
        if not _contains(span, name_span):
            problems.append(prefix + " name span is outside declaration")
        try:
            if declaration.get("name_source") != _fragment(source_text, name_span):
                problems.append(prefix + " name source/span mismatch")
        except ValueError:
            problems.append(prefix + " name span is invalid")
        name = declaration.get("name")
        qualified = declaration.get("qualified_name")
        rule_id = declaration.get("rule_id")
        if not isinstance(rule_id, str) or not rule_id:
            problems.append(prefix + " rule_id is invalid")
        if not isinstance(name, str) or not name or \
                _normalized_identifier(declaration.get("name_source", "")) != name:
            problems.append(prefix + " name is invalid")
        if not isinstance(qualified, str) or not qualified or \
                qualified.split(".")[-1] != name:
            problems.append(prefix + " qualified_name is invalid")
        if not isinstance(declaration.get("tree_path"), str):
            problems.append(prefix + " tree_path is invalid")
        start = span.get("start")
        if type(start) is int and start < previous_start:
            problems.append(prefix + " source order mismatch")
        if type(start) is int:
            previous_start = start
        assignments = declaration.get("assignments")
        problems.extend(_assignments_problems(
            assignments, source_text, prefix + ".assignment", span))
        local_names = [assignment for assignment in assignments
                       if isinstance(assignment, dict) and
                       assignment.get("owner_rule") == rule_id and
                       assignment.get("feature") == "name" and
                       assignment.get("span") == name_span] \
            if isinstance(assignments, list) else []
        if len(local_names) != 1:
            problems.append(prefix + " local name assignment mismatch")
    return problems, symbols


def _instances_problems(instances: object, source_text: str) -> list[str]:
    if not isinstance(instances, list):
        return ["repository document instances must be a list"]
    problems: list[str] = []
    rules = {
        "non_ui_component": "NonUIComponentInstance",
        "ui_component": "UIComponentInstance",
    }
    previous_start = -1
    for index, instance in enumerate(instances):
        prefix = f"instance[{index}]"
        if not isinstance(instance, dict) or set(instance) != {
                "index", "kind", "span", "source", "rule"}:
            problems.append(prefix + " shape is invalid")
            continue
        if instance.get("index") != index:
            problems.append(prefix + " index mismatch")
        problems.extend(_record_source_problems(instance, source_text, prefix))
        span = instance.get("span") or {}
        start = span.get("start")
        if type(start) is int and start < previous_start:
            problems.append(prefix + " source order mismatch")
        if type(start) is int:
            previous_start = start
        kind = instance.get("kind")
        if kind not in rules:
            problems.append(prefix + " kind is invalid")
        problems.extend(_rule_record_problems(
            instance.get("rule"), source_text, prefix + ".rule", span))
        rule = instance.get("rule")
        if isinstance(rule, dict) and rule.get("rule_id") != rules.get(kind):
            problems.append(prefix + " kind/rule mismatch")
        if isinstance(rule, dict) and (rule.get("span") != span or
                                      rule.get("source") != instance.get("source")):
            problems.append(prefix + " rule binding mismatch")
    return problems


def _grammar_inventory_problems(inventory: object, prefix: str) -> list[str]:
    if not isinstance(inventory, dict) or set(inventory) != {
            "cross_reference_count", "targets"}:
        return [prefix + " shape is invalid"]
    problems: list[str] = []
    count = inventory.get("cross_reference_count")
    targets = inventory.get("targets")
    if type(count) is not int or count < 0:
        problems.append(prefix + " cross-reference count is invalid")
    if not isinstance(targets, dict):
        problems.append(prefix + " targets must be a mapping")
        return problems
    occurrence_sum = 0
    for target, details in targets.items():
        tprefix = prefix + f".target[{target!r}]"
        if not isinstance(target, str) or not target:
            problems.append(tprefix + " target is invalid")
        if not isinstance(details, dict) or set(details) != {
                "occurrences", "terminal_occurrences",
                "compatible_declaration_rules", "supported"}:
            problems.append(tprefix + " shape is invalid")
            continue
        occurrences = details.get("occurrences")
        terminal_occurrences = details.get("terminal_occurrences")
        compatible = details.get("compatible_declaration_rules")
        supported = details.get("supported")
        if type(occurrences) is not int or occurrences <= 0:
            problems.append(tprefix + " occurrences is invalid")
        else:
            occurrence_sum += occurrences
        if not isinstance(terminal_occurrences, list) or not terminal_occurrences:
            problems.append(tprefix + " terminal occurrences are invalid")
        else:
            terminal_total = 0
            seen_terminals: set[str | None] = set()
            for terminal_index, terminal_entry in enumerate(terminal_occurrences):
                eprefix = tprefix + f".terminal[{terminal_index}]"
                if not isinstance(terminal_entry, dict) or set(terminal_entry) != {
                        "terminal", "occurrences"}:
                    problems.append(eprefix + " shape is invalid")
                    continue
                terminal = terminal_entry.get("terminal")
                terminal_count = terminal_entry.get("occurrences")
                if terminal is not None and (not isinstance(terminal, str) or
                                             not terminal):
                    problems.append(eprefix + " terminal is invalid")
                if terminal in seen_terminals:
                    problems.append(eprefix + " terminal is duplicated")
                seen_terminals.add(terminal)
                if type(terminal_count) is not int or terminal_count <= 0:
                    problems.append(eprefix + " occurrences is invalid")
                else:
                    terminal_total += terminal_count
            if type(occurrences) is int and terminal_total != occurrences:
                problems.append(tprefix + " terminal occurrence total mismatch")
        if not isinstance(compatible, list) or any(
                not isinstance(rule, str) or not rule for rule in compatible) or \
                compatible != sorted(set(compatible)):
            problems.append(tprefix + " compatible rules are invalid")
        if type(supported) is not bool or \
                (isinstance(compatible, list) and supported != bool(compatible)):
            problems.append(tprefix + " supported flag mismatch")
    if type(count) is int and occurrence_sum != count:
        problems.append(prefix + " occurrence total mismatch")
    return problems


def _linking_audit_problems(audit: object, source_text: str,
                            symbols: dict[str, dict]) -> list[str]:
    expected_keys = {
        "checked", "succeeded", "scope", "external_scope_used",
        "grammar_inventory", "symbol_count", "reference_count", "references",
    }
    if not isinstance(audit, dict) or set(audit) != expected_keys:
        return ["linking_audit shape is invalid"]
    problems: list[str] = []
    if audit.get("checked") is not True or audit.get("succeeded") is not True:
        problems.append("linking_audit is not successfully checked")
    if audit.get("scope") != "same_document" or \
            audit.get("external_scope_used") is not False:
        problems.append("linking_audit scope is not closed to the same document")
    if audit.get("symbol_count") != len(symbols):
        problems.append("linking_audit symbol count mismatch")
    problems.extend(_grammar_inventory_problems(
        audit.get("grammar_inventory"), "linking_audit.grammar_inventory"))
    references = audit.get("references")
    if not isinstance(references, list):
        problems.append("linking_audit references must be a list")
        return problems
    if audit.get("reference_count") != len(references):
        problems.append("linking_audit reference count mismatch")
    expected_reference_keys = {
        "index", "target", "terminal", "surface", "span", "source",
        "tree_path", "status", "compatible_declaration_rules",
        "candidate_symbol_ids", "resolved_symbol_id",
    }
    previous_start = -1
    inventory = audit.get("grammar_inventory")
    targets = inventory.get("targets", {}) if isinstance(inventory, dict) else {}
    for index, reference in enumerate(references):
        prefix = f"linking_audit.reference[{index}]"
        if not isinstance(reference, dict) or set(reference) != expected_reference_keys:
            problems.append(prefix + " shape is invalid")
            continue
        if reference.get("index") != index:
            problems.append(prefix + " index mismatch")
        problems.extend(_record_source_problems(reference, source_text, prefix))
        start = (reference.get("span") or {}).get("start")
        if type(start) is int and start < previous_start:
            problems.append(prefix + " source order mismatch")
        if type(start) is int:
            previous_start = start
        for field in ("target", "terminal", "surface", "tree_path"):
            if not isinstance(reference.get(field), str):
                problems.append(prefix + f" {field} is invalid")
        target = reference.get("target")
        target_details = targets.get(target) if isinstance(targets, dict) else None
        if not isinstance(target_details, dict):
            problems.append(prefix + " target is absent from grammar inventory")
        compatible = reference.get("compatible_declaration_rules")
        if not isinstance(compatible, list) or any(
                not isinstance(rule, str) or not rule for rule in compatible) or \
                compatible != sorted(set(compatible)):
            problems.append(prefix + " compatible rules are invalid")
        if isinstance(target_details, dict) and \
                compatible != target_details.get("compatible_declaration_rules"):
            problems.append(prefix + " target compatibility mismatch")
        if reference.get("status") != "resolved":
            problems.append(prefix + " is not uniquely resolved")
        candidate_ids = reference.get("candidate_symbol_ids")
        resolved_id = reference.get("resolved_symbol_id")
        if not isinstance(candidate_ids, list) or candidate_ids != [resolved_id] or \
                resolved_id not in symbols:
            problems.append(prefix + " resolved symbol binding mismatch")
            continue
        declaration = symbols[resolved_id]
        if isinstance(compatible, list) and declaration.get("rule_id") not in compatible:
            problems.append(prefix + " resolved declaration type mismatch")
        surface = reference.get("surface")
        if isinstance(surface, str) and \
                _normalized_identifier(reference.get("source", "")) != surface:
            problems.append(prefix + " surface/source mismatch")
        if isinstance(surface, str) and surface not in {
                declaration.get("name"), declaration.get("qualified_name")}:
            problems.append(prefix + " resolved declaration name mismatch")
    return problems


def repository_document_problems(document: dict, source_text: str) -> list[str]:
    """Validate the closed B4 document projection without trusting its producer."""
    problems: list[str] = []
    if not isinstance(document, dict):
        return ["repository document must be a mapping"]
    expected = {
        "repository_document_schema_version", "root_rule", "grammar_source_sha256",
        "source_sha256", "declarations", "instances", "linking_audit",
        "requirements",
    }
    if set(document) != expected:
        problems.append(f"repository document keys mismatch: {sorted(map(repr, set(document) ^ expected))}")
    if document.get("repository_document_schema_version") != REPOSITORY_DOCUMENT_SCHEMA_VERSION:
        problems.append("repository document schema version mismatch")
    if document.get("root_rule") != REPOSITORY_DOCUMENT_ROOT:
        problems.append("repository document root rule mismatch")
    if document.get("source_sha256") != _source_sha256(source_text):
        problems.append("repository document source hash mismatch")
    if not isinstance(document.get("grammar_source_sha256"), str) or \
            not document.get("grammar_source_sha256", "").startswith("sha256:"):
        problems.append("repository document grammar hash is invalid")
    declaration_problems, symbols = _declarations_problems(
        document.get("declarations"), source_text)
    problems.extend(declaration_problems)
    problems.extend(_instances_problems(document.get("instances"), source_text))
    problems.extend(_linking_audit_problems(
        document.get("linking_audit"), source_text, symbols))
    requirements = document.get("requirements")
    if not isinstance(requirements, list):
        problems.append("repository document requirements must be a list")
        return problems
    for expected_index, requirement in enumerate(requirements):
        if not isinstance(requirement, dict) or set(requirement) != {
                "index", "span", "source", "scope", "atomic_responses",
                "condition_structure", "response_structure"}:
            problems.append(f"requirement[{expected_index}] shape is invalid")
            continue
        if requirement.get("index") != expected_index:
            problems.append(f"requirement[{expected_index}] index mismatch")
        try:
            if requirement.get("source") != _fragment(source_text, requirement.get("span") or {}):
                problems.append(f"requirement[{expected_index}] source/span mismatch")
        except ValueError:
            problems.append(f"requirement[{expected_index}] span is invalid")
        problems.extend(_scope_problems(
            requirement.get("scope"), source_text,
            f"requirement[{expected_index}].scope", requirement.get("span") or {}))
        responses = requirement.get("atomic_responses")
        if not isinstance(responses, list):
            problems.append(f"requirement[{expected_index}] responses must be a list")
            continue
        for response_index, response in enumerate(responses):
            prefix = f"requirement[{expected_index}].response[{response_index}]"
            if not isinstance(response, dict) or set(response) != {
                    "index", "span", "source", "modality", "negation",
                    "frequency", "action"}:
                problems.append(prefix + " shape is invalid")
                continue
            if response.get("index") != response_index:
                problems.append(prefix + " index mismatch")
            try:
                if response.get("source") != _fragment(source_text, response.get("span") or {}):
                    problems.append(prefix + " source/span mismatch")
            except ValueError:
                problems.append(prefix + " span is invalid")
            problems.extend(_atomic_option_problems(
                response.get("modality"), source_text, prefix + ".modality",
                response.get("span") or {}, {"enum_literal", "literal"}))
            problems.extend(_atomic_option_problems(
                response.get("negation"), source_text, prefix + ".negation",
                response.get("span") or {}, "literal", "not"))
            problems.extend(_frequency_problems(
                response.get("frequency"), source_text, prefix + ".frequency",
                response.get("span") or {}))
            action = response.get("action")
            if not isinstance(action, dict) or set(action) != {
                    "rule_id", "span", "source", "assignments"}:
                problems.append(prefix + ".action shape is invalid")
                continue
            if not isinstance(action.get("rule_id"), str) or not action.get("rule_id"):
                problems.append(prefix + ".action rule_id is invalid")
            try:
                if action.get("source") != _fragment(source_text, action.get("span") or {}):
                    problems.append(prefix + ".action source/span mismatch")
            except ValueError:
                problems.append(prefix + ".action span is invalid")
            if not _contains(response.get("span") or {}, action.get("span") or {}):
                problems.append(prefix + ".action span is outside its response")
            problems.extend(_assignments_problems(
                action.get("assignments"), source_text, prefix + ".action.assignment",
                action.get("span") or {}))
        condition_problems = _requirement_condition_structure_problems(
            requirement.get("condition_structure"), source_text,
            f"requirement[{expected_index}].condition_structure",
            requirement.get("span") or {})
        problems.extend(condition_problems)
        structure_problems, references = _response_structure_problems(
            requirement.get("response_structure"), source_text,
            f"requirement[{expected_index}].response_structure",
            requirement.get("span") or {})
        problems.extend(structure_problems)
        reference_indexes = [item[0] for item in references]
        if reference_indexes != list(range(len(responses))):
            problems.append(
                f"requirement[{expected_index}] response structure/index coverage mismatch")
        for reference_index, container_span in references:
            if 0 <= reference_index < len(responses) and \
                    not _contains(container_span, responses[reference_index].get("span") or {}):
                problems.append(
                    f"requirement[{expected_index}] response structure span/index mismatch")
        condition_structure = requirement.get("condition_structure")
        response_structure = requirement.get("response_structure")
        system_response = condition_structure.get("system_response") \
            if isinstance(condition_structure, dict) else None
        if isinstance(system_response, dict) and isinstance(response_structure, dict) and \
                not _contains(system_response.get("span") or {},
                              response_structure.get("span") or {}):
            problems.append(
                f"requirement[{expected_index}] condition/response structure binding mismatch")
    return problems


def project_repository_document(parsed: SyntaxParseResult, source_text: str,
                                linking: SemanticLinkResult | None,
                                grammar: GrammarIR | None) \
        -> RepositoryDocumentProjectionResult:
    """Project a linked fixed-grammar document without applying product semantics."""
    root = parsed.start_rule
    if not parsed.accepted or parsed.tree is None:
        return RepositoryDocumentProjectionResult(
            "syntax_not_accepted", root, None,
            "Repository Grammarのfull matchが成立していない")
    tree_problems = syntax_tree_problems(parsed.tree, source_text, expected_root=root)
    if tree_problems:
        return RepositoryDocumentProjectionResult(
            "projection_contract_error", root, None,
            "parse resultのsyntax tree契約違反: " + "; ".join(tree_problems))
    if root != REPOSITORY_DOCUMENT_ROOT:
        return RepositoryDocumentProjectionResult(
            "unsupported_root_rule", root, None,
            "Repository文書投影はCNLFunctionalRequirementsだけを受理する")
    if not parsed.ambiguity_checked:
        return RepositoryDocumentProjectionResult(
            "ambiguity_check_required", root, None,
            "Repository文書投影には構文derivation一意性の確認が必要")
    if parsed.ambiguity_detected is not False:
        return RepositoryDocumentProjectionResult(
            "ambiguous_syntax", root, None,
            "Repository Grammar IR上で複数のfull-match derivationが成立する")
    if not isinstance(linking, SemanticLinkResult) or not linking.checked or \
            not isinstance(grammar, GrammarIR):
        return RepositoryDocumentProjectionResult(
            "semantic_linking_required", root, None,
            "Repository文書投影には同一文書内linkingの確認が必要")
    source_sha = _source_sha256(source_text)
    mismatch = linking.start_rule != root or \
        linking.grammar_ir_signature != parsed.grammar_ir_signature or \
        linking.grammar_source_sha256 != parsed.grammar_source_sha256 or \
        linking.syntax_tree_sha256 != syntax_tree_signature(parsed.tree) or \
        linking.source_sha256 != source_sha or parsed.source_sha256 != source_sha
    if mismatch or link_repository_syntax(grammar, parsed, source_text) != linking:
        return RepositoryDocumentProjectionResult(
            "projection_contract_error", root, None,
            "semantic link result is not bound to this parse result/source")
    if not linking.succeeded:
        return RepositoryDocumentProjectionResult(
            "semantic_linking_failed", root, None,
            "cross-reference linkingに未解決・曖昧・型不一致が残っている")
    try:
        document = _document(parsed.tree, parsed, source_text, linking, grammar)
        problems = repository_document_problems(document, source_text)
    except Exception as exc:
        return RepositoryDocumentProjectionResult(
            "projection_contract_error", root, None,
            f"repository document projection raised {type(exc).__name__}: {exc}")
    if problems:
        return RepositoryDocumentProjectionResult(
            "projection_contract_error", root, None, "; ".join(problems))
    return RepositoryDocumentProjectionResult(
        "projected_document", root, copy.deepcopy(document),
        "Repository構文・linkingだけに基づく文書投影（製品採用・原典準拠を意味しない）")


def migrate_repository_document_0_4_to_0_5(
    document: dict,
    parsed: SyntaxParseResult,
    source_text: str,
    linking: SemanticLinkResult | None,
    grammar: GrammarIR | None,
) -> dict:
    """Replay a frozen 0.4.0 projection through the bound source and Grammar.

    Scope and SystemResponse wrapper assignments cannot be inferred safely from
    the old projection alone.  Migration therefore requires the same accepted,
    unambiguous, linked parse boundary as a fresh projection and proves that the
    supplied 0.4.0 document is exactly the historical view of that result.
    """
    if not isinstance(document, dict) or \
            document.get("repository_document_schema_version") != "0.4.0":
        raise ValueError("migration input must use Repository document 0.4.0")
    projected = project_repository_document(parsed, source_text, linking, grammar)
    if projected.status != "projected_document" or projected.document is None:
        raise ValueError(
            "Repository document migration replay failed: "
            f"{projected.status}: {projected.reason}")
    expected_historical = historical_repository_document_0_4(projected.document)
    if document != expected_historical:
        raise ValueError(
            "Repository document 0.4.0 is not bound to the replayed source/Grammar")
    return copy.deepcopy(projected.document)
