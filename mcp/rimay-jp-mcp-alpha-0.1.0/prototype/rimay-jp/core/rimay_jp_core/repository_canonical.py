"""固定Repository Grammar構文木からCanonical候補を作る組み込みadapter。

構文とAction規則IDはRepository Grammar IR、製品family・role意味はRimay-JPの
Action Frameを正本とする。未採用規則はIDだけを保持し、familyを未解決にする。
論文corpus、Capability証拠、規則名推測は入力にしない。1文書1Requirementだけを扱い、
複数Requirementや複数Responseを先頭要素へ縮退させない。
"""
from __future__ import annotations

import ast
import hashlib

from .lexicon import ROLE_FIELD, case_frames
from .model import new_canonical, set_slot
from .repository_adapter import (
    AdapterPayload, AdapterScopeUnsupported, AdapterSpec,
    RepositoryCanonicalAdapterRegistry,
)
from .repository_linker import SemanticLinkResult
from .repository_comparison_mapping_candidate import (
    repository_comparison_scalar_value_problem,
    repository_comparison_selector_problems,
)
from .repository_multi_value_legacy_adapter import (
    RepositoryMultiValueLegacyAdapterError,
    project_legacy_repository_multi_value_condition,
)
from .repository_grammar import (
    direct_syntax_rule_children as _direct_rule_children,
    syntax_tree_children as _children,
    walk_syntax_tree as _walk,
)
from .semantic_values import split_money


ADAPTER_ID = "REPOSITORY-CNL-01"
ROOT_RULE = "CNLFunctionalRequirements"
REPOSITORY_GRAMMAR_PROJECTION_REFERENCE = \
    "rimay-repository-grammar-projection/0.1.0"

# Repository assignment path -> Canonical response leaf. Each path starts at
# the Action rule and crosses only explicitly named assignment boundaries.
# This prevents a same-named feature in an unrelated nested rule from leaking
# into a role. Absent/one-to-many fields remain unresolved.
ACTION_ROLE_PATHS = {
    "SEND_11_1_1": {
        "theme": (("theme_to_send_rule", "theme_to_send"),
                  ("theme_to_send_rule", "theme_to_send_ref")),
        "source": (("initial_location_rule", "initial_location"),),
        "destination": (("destination_rule", "destination"),),
        "channel": (("channel_through_rule", "channel_actor"),
                    ("channel_through_rule", "actor")),
    },
    "DS_UPDATE": {
        "property": (("change", "patient"),),
        "result_value": (("change", "toValue"),),
    },
    "ENGENDER_27": {
        "theme": (("instance",), ("instance2",)),
    },
    "KEEP_15_2": {
        "theme": (("properties",), ("values",)),
        "location": (("place_name",), ("place_ref",)),
    },
    "OBTAIN_13_5_2": {
        "theme": (("instance_or_class",),),
        "source": (("source", "source"),),
        "channel": (("channel_through_rule", "channel_actor"),
                    ("channel_through_rule", "actor")),
    },
    "REFLEXIVE_APPEARANCE_48_1_2": {
        "theme": (("theme",), ("ref",)),
        "display_location": (("on_in_actor",),
                             ("on_in_ui_instance", "instance_name")),
    },
    "REMOVE_10_1": {
        "theme": (("property",),),
    },
    "DS_VALIDATE": {
        "theme": (("validate_option", "entity"),
                  ("validate_option", "entity_ref"),
                  ("action",)),
        "rule": (("rule",),),
    },
    "CREATE_26_4": {
        "result": (("property",), ("property_referenced",)),
        "input": (("artifact",),),
    },
    "SAY_37_7": {
        "content": (("topic",),),
        "destination": (("recipient",),),
        "channel": (("channel_account",),),
    },
}

# Canonical event.object is the patient/result that identifies the event.
# This is deliberately explicit: Repository Action rules have different role
# names, and selecting the first STRING in a Trigger would silently confuse a
# destination/source with the event object.
EVENT_OBJECT_FIELD_BY_RULE = {
    "SEND_11_1_1": "theme",
    "DS_UPDATE": "property",
    "ENGENDER_27": "theme",
    "KEEP_15_2": "theme",
    "OBTAIN_13_5_2": "theme",
    "REFLEXIVE_APPEARANCE_48_1_2": "theme",
    "REMOVE_10_1": "theme",
    "DS_VALIDATE": "theme",
    "CREATE_26_4": "result",
    "SAY_37_7": "content",
}


def _rules(node: dict, name: str) -> list[dict]:
    return [item for item in _walk(node)
            if item.get("kind") == "rule" and item.get("name") == name]


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


def _semantic_leaves(node: dict):
    for item in _walk(node):
        if item.get("kind") == "cross_reference":
            yield _decode_surface(item.get("surface", "")), item.get("span") or {}
        elif item.get("kind") == "terminal" and item.get("name") in {"STRING", "ID"}:
            yield _decode_surface(item.get("surface", "")), item.get("span") or {}


def _local_assignments(node: dict, feature: str) -> list[dict]:
    found = []

    def visit(item: dict, root: bool = False) -> None:
        if item.get("kind") == "rule" and not root:
            return
        if item.get("kind") == "assignment" and item.get("feature") == feature:
            found.append(item)
            return
        for child in _children(item):
            visit(child)

    visit(node, root=True)
    return found


def _assignment_path_value(node: dict, paths: tuple[tuple[str, ...], ...]) \
        -> tuple[str, dict] | None:
    found: list[tuple[str, dict]] = []
    for path in paths:
        current = [node]
        for feature in path:
            next_nodes = []
            for parent in current:
                for assignment in _local_assignments(parent, feature):
                    child = assignment.get("child")
                    if isinstance(child, dict):
                        next_nodes.append(child)
            current = next_nodes
            if not current:
                break
        for child in current:
            found.extend(_semantic_leaves(child))
    unique: dict[str, dict] = {}
    for value, span in found:
        if value:
            unique.setdefault(value, span)
    if len(unique) != 1:
        return None
    value = next(iter(unique))
    return value, unique[value]


def _assignment_source(node: dict, feature: str,
                       source_text: str) -> tuple[str, dict] | None:
    found: list[tuple[str, dict]] = []
    for item in _walk(node):
        if item.get("kind") != "assignment" or item.get("feature") != feature:
            continue
        span = item.get("span") or {}
        found.append((_source_fragment(source_text, span), span))
    return found[0] if len(found) == 1 else None


def _local_literal(rule: dict, value: str) -> bool:
    def visit(node: dict, root: bool = False) -> bool:
        if node.get("kind") == "rule" and not root:
            return False
        if node.get("kind") == "literal" and node.get("value") == value:
            return True
        return any(visit(child) for child in _children(node))
    return visit(rule, root=True)


def _local_assignment_present(rule: dict, feature: str) -> bool:
    return bool(_local_assignments(rule, feature))


def _source_fragment(source_text: str, span: dict) -> str:
    start, end = span.get("start"), span.get("end")
    if type(start) is int and type(end) is int and 0 <= start <= end <= len(source_text):
        return source_text[start:end]
    return ""


def _action_frames_by_rule() -> dict[str, dict]:
    by_rule = {}
    for family, frame in case_frames().items():
        rule = frame.get("rimay_action_id")
        if not isinstance(rule, str) or not rule or rule in by_rule:
            raise ValueError("Rimay-JP Action Frame has a missing/duplicate repository rule")
        by_rule[rule] = {**frame, "family": family}
    return by_rule


def _condition_slot(canonical: dict, path: str, source_text: str,
                    span: dict, method: str = "deterministic_parse",
                    reference: str | None = None) -> None:
    set_slot(canonical, path, "confirmed", _source_fragment(source_text, span),
             method=method, reference=reference)


def _predicate_operator(operator: dict) -> str | None:
    compares = _rules(operator, "Compare")
    contains = _rules(operator, "Contains")
    if len(compares) == 1 and not contains:
        compare = compares[0]
        negated = _local_assignment_present(compare, "not")
        ordered = (
            ("GreaterOrEqualTo", "GREATER_OR_EQUAL"),
            ("LessOrEqualTo", "LESS_OR_EQUAL"),
            ("GreaterThan", "GREATER_THAN"),
            ("LessThan", "LESS_THAN"),
            ("EqualsTo", "EQUALS"),
        )
        for rule, value in ordered:
            if _rules(compare, rule):
                # Canonical can express negated equality but has no negated
                # ordering operators. Do not rewrite those into a different
                # positive comparison.
                if negated:
                    return "NOT_EQUALS" if rule == "EqualsTo" else None
                return value
        return "NOT_EQUALS" if negated else "IS"
    if len(contains) == 1 and not compares and not _rules(contains[0], "Negation"):
        return "CONTAINS"
    return None


def _money_value(value: str) -> tuple[str, str] | None:
    return split_money(value)


def _project_predicate(structure: dict, ctype: str, canonical: dict,
                       source_text: str) -> dict | None:
    if repository_comparison_selector_problems(structure):
        return None
    conditions = _rules(structure, "Condition")
    # Canonical has no connector field. A multiple/itemized expression cannot
    # be projected as a list without losing AND/OR and precedence.
    if len(conditions) != 1 or _rules(structure, "ItemizedConditions"):
        return None
    candidates = _rules(conditions[0], "InstanceOrPropertyOperatorValue")
    if len(candidates) != 1:
        return None
    candidate = candidates[0]
    subject = _assignment_path_value(
        candidate, (("non_ui_instance_or_property",),))
    operators = _rules(candidate, "OperatorValuesExpr")
    atomic_values = _rules(candidate, "AtomicValue")
    value = _assignment_path_value(
        candidate, (("rest", "valuesExpression"),))
    if subject is None or value is None or len(operators) != 1 or len(atomic_values) != 1:
        return None
    op = _predicate_operator(operators[0])
    if op is None:
        return None
    subject_value, subject_span = subject
    predicate_value, value_span = value
    if repository_comparison_scalar_value_problem(predicate_value) is not None:
        return None
    predicate = {"subject": subject_value, "operator": op,
                 "value": predicate_value}
    money = _money_value(predicate_value)
    if money and op in {"GREATER_THAN", "LESS_THAN", "GREATER_OR_EQUAL",
                        "LESS_OR_EQUAL"}:
        predicate["value"], predicate["unit"] = money
    condition = {"type": ctype, "predicate": predicate}
    base = "/rimay_core/conditions/0"
    _condition_slot(canonical, base + "/type", source_text,
                    structure.get("span") or {},
                    method="rule_application",
                    reference=REPOSITORY_GRAMMAR_PROJECTION_REFERENCE)
    _condition_slot(canonical, base + "/predicate/subject", source_text, subject_span)
    _condition_slot(canonical, base + "/predicate/operator", source_text,
                    operators[0].get("span") or {})
    _condition_slot(canonical, base + "/predicate/value", source_text, value_span)
    if "unit" in predicate:
        _condition_slot(canonical, base + "/predicate/unit", source_text, value_span)
    return condition


def _record_multi_value_slots(canonical: dict, expression: dict,
                              source_text: str) -> None:
    """Bind active Multi-value expression leaves to Repository source."""
    def record_value(node: dict, path: str, span: dict) -> None:
        _condition_slot(canonical, path + "/kind", source_text, span,
                        method="rule_application",
                        reference=REPOSITORY_GRAMMAR_PROJECTION_REFERENCE)
        kind = node["kind"]
        if kind == "value":
            _condition_slot(canonical, path + "/value", source_text, span)
            if "unit" in node:
                _condition_slot(canonical, path + "/unit", source_text, span)
            return
        if kind == "group":
            record_value(node["expression"], path + "/expression", span)
            return
        record_value(node["left"], path + "/left", span)
        record_value(node["right"], path + "/right", span)

    def visit(node: dict, path: str) -> None:
        trace = node["repository_trace"]
        span = trace["source_span"]
        _condition_slot(canonical, path + "/kind", source_text, span,
                        method="rule_application",
                        reference=REPOSITORY_GRAMMAR_PROJECTION_REFERENCE)
        if node["kind"] == "condition":
            condition = node["condition"]
            base = path + "/condition"
            _condition_slot(canonical, base + "/type", source_text, span,
                            method="rule_application",
                            reference=REPOSITORY_GRAMMAR_PROJECTION_REFERENCE)
            predicate = condition["predicate"]
            _condition_slot(
                canonical, base + "/predicate/subject", source_text, span)
            _condition_slot(
                canonical, base + "/predicate/operator", source_text, span)
            if "value" in predicate:
                _condition_slot(
                    canonical, base + "/predicate/value", source_text, span)
                if "unit" in predicate:
                    _condition_slot(
                        canonical, base + "/predicate/unit", source_text, span)
            else:
                record_value(
                    predicate["value_expression"],
                    base + "/predicate/value_expression",
                    span,
                )
            return
        visit(node["left"], path + "/left")
        visit(node["right"], path + "/right")

    visit(expression, "/rimay_core/condition_expression")


def _project_predicate_condition(structure: dict, ctype: str, canonical: dict,
                                 source_text: str) -> tuple[str, object] | None:
    try:
        expression = project_legacy_repository_multi_value_condition(
            structure, source_text)
    except RepositoryMultiValueLegacyAdapterError:
        condition = _project_predicate(
            structure, ctype, canonical, source_text)
        return ("conditions", [condition]) if condition is not None else None
    _record_multi_value_slots(canonical, expression, source_text)
    return "condition_expression", expression


def _action_role_values(action_node: dict, rule: str) -> dict[str, tuple[str, dict]]:
    result = {}
    for field, paths in ACTION_ROLE_PATHS.get(rule, {}).items():
        projected = _assignment_path_value(action_node, paths)
        if projected is not None:
            result[field] = projected
    return result


def _project_trigger(structure: dict, ctype: str, canonical: dict,
                     source_text: str, unresolved: set[str]) -> dict | None:
    triggers = _rules(structure, "Trigger")
    if len(triggers) != 1 or _rules(structure, "Time"):
        return None
    trigger = triggers[0]
    actor = _assignment_path_value(trigger, (("actor",),))
    action_phrases = _rules(trigger, "ActionPhrase")
    actions = _direct_rule_children(action_phrases[0]) \
        if len(action_phrases) == 1 else []
    if actor is None or len(actions) != 1 or \
            len(_rules(trigger, "AtomicActionInTrigger")) != 1:
        return None
    action_node = actions[0]
    rule = action_node["name"]
    frames = _action_frames_by_rule()
    frame = frames.get(rule)
    roles = _action_role_values(action_node, rule) if frame else {}
    object_field = EVENT_OBJECT_FIELD_BY_RULE.get(rule) if frame else None
    event_object = roles.get(object_field) if object_field else None
    actor_value, actor_span = actor
    event = {"actor": actor_value,
             "action": {"family": frame["family"] if frame else None,
                        "rimay_action_id": rule}}
    if event_object is not None:
        object_value, _object_span = event_object
        event["object"] = object_value
    if rule == "DS_UPDATE" and "result_value" in roles:
        event["value"] = roles["result_value"][0]
    condition = {"type": ctype, "event": event}
    base = "/rimay_core/conditions/0"
    _condition_slot(canonical, base + "/type", source_text,
                    structure.get("span") or {},
                    method="rule_application",
                    reference=REPOSITORY_GRAMMAR_PROJECTION_REFERENCE)
    _condition_slot(canonical, base + "/event/actor", source_text, actor_span)
    _condition_slot(canonical, base + "/event/action/rimay_action_id", source_text,
                    action_node.get("span") or {},
                    method="rule_application",
                    reference=REPOSITORY_GRAMMAR_PROJECTION_REFERENCE)
    if frame is None:
        unresolved.add(base + "/event/action/family")
    else:
        _condition_slot(canonical, base + "/event/action/family", source_text,
                        action_node.get("span") or {},
                        method="rule_application",
                        reference=REPOSITORY_GRAMMAR_PROJECTION_REFERENCE)
    if event_object is None:
        unresolved.add(base + "/event/object")
    else:
        _condition_slot(canonical, base + "/event/object", source_text,
                        event_object[1])
    if "value" in event:
        _condition_slot(canonical, base + "/event/value", source_text,
                        roles["result_value"][1])
    return condition


def _project_condition(requirement: dict, canonical: dict,
                       source_text: str, unresolved: set[str]) \
        -> tuple[str, object] | None:
    structures = _rules(requirement, "ConditionStructure")
    if len(structures) != 1:
        return None
    structure = structures[0]
    if len(_rules(structure, "IfStructure")) == 1:
        return _project_predicate_condition(
            structure, "IF", canonical, source_text)
    if len(_rules(structure, "WhileStructure")) == 1:
        return _project_predicate_condition(
            structure, "WHILE", canonical, source_text)
    if len(_rules(structure, "WhenStructure")) == 1:
        condition = _project_trigger(
            structure, "WHEN", canonical, source_text, unresolved)
        return ("conditions", [condition]) if condition is not None else None
    repeats = _rules(structure, "RepeatOnce")
    if len(repeats) == 1:
        repeat = repeats[0]
        before = _local_literal(repeat, "Before") or _local_literal(repeat, "before")
        after = _local_literal(repeat, "After") or _local_literal(repeat, "after")
        if before != after:
            condition = _project_trigger(
                repeat, "BEFORE" if before else "AFTER",
                canonical, source_text, unresolved)
            return ("conditions", [condition]) if condition is not None else None
    return None


def _project_scope(requirement: dict, canonical: dict,
                   source_text: str) -> bool:
    scopes = _rules(requirement, "Scope")
    if not scopes:
        return True
    if len(scopes) != 1:
        return False
    scope_texts = _rules(scopes[0], "ScopeText")
    # Repository Scope supports two coordinated values, while Canonical has a
    # single function slot. Do not concatenate them or select the first.
    if len(scope_texts) != 1:
        return False
    projected = _assignment_path_value(scope_texts[0], (("scope",),))
    if projected is None:
        return False
    value, span = projected
    canonical["rimay_core"]["scope"] = {"function": value}
    set_slot(canonical, "/rimay_core/scope/function", "confirmed",
             _source_fragment(source_text, span), method="deterministic_parse")
    return True


def _project_cnl(tree: dict, source_text: str,
                 linking: SemanticLinkResult | None) -> AdapterPayload:
    if linking is None or not linking.succeeded:
        raise ValueError("successful semantic linking is required")
    requirements = _rules(tree, "Requirement")
    if len(requirements) != 1:
        raise AdapterScopeUnsupported(
            f"{ADAPTER_ID} requires exactly one Requirement, got {len(requirements)}")
    requirement = requirements[0]
    responses = _rules(requirement, "SystemResponse")
    atomic = _rules(requirement, "AtomicSystemResponse")
    if len(responses) != 1 or len(atomic) != 1:
        raise AdapterScopeUnsupported(
            f"{ADAPTER_ID} requires one SystemResponse/AtomicSystemResponse, "
            f"got {len(responses)}/{len(atomic)}")

    req_hash = hashlib.sha256(source_text.encode("utf-8")).hexdigest()[:12]
    canonical = new_canonical(f"REQ-REPOSITORY-{req_hash}")
    canonical["source"]["text"] = source_text
    canonical.pop("normalization", None)
    unresolved: set[str] = set()

    if _rules(requirement, "WithCondition"):
        projection = _project_condition(requirement, canonical, source_text,
                                        unresolved)
        if projection is None:
            canonical["rimay_core"].pop("conditions", None)
            unresolved.add("/rimay_core/conditions")
        else:
            field, value = projection
            canonical["rimay_core"].pop(
                "condition_expression" if field == "conditions" else "conditions",
                None,
            )
            canonical["rimay_core"][field] = value
    elif not _rules(requirement, "WithoutCondition"):
        canonical["rimay_core"].pop("conditions", None)
        unresolved.add("/rimay_core/conditions")

    if not _project_scope(requirement, canonical, source_text):
        canonical["rimay_core"].pop("scope", None)
        unresolved.add("/rimay_core/scope")

    actor = _assignment_path_value(responses[0], (("system_name",),))
    if actor is None:
        unresolved.add("/rimay_core/response/actor")
    else:
        value, span = actor
        canonical["rimay_core"]["response"]["actor"] = value
        set_slot(canonical, "/rimay_core/response/actor", "confirmed",
                 _source_fragment(source_text, span), method="deterministic_parse")

    modal = _assignment_source(responses[0], "modal_verb", source_text)
    if modal is None or modal[0] not in {"must", "shall"}:
        unresolved.add("/rimay_core/response/modality")
    else:
        surface, span = modal
        modality = "MUST_NOT" if _local_literal(atomic[0], "not") else "MUST"
        canonical["rimay_core"]["response"]["modality"] = modality
        set_slot(canonical, "/rimay_core/response/modality", "confirmed",
                 _source_fragment(source_text, span), method="deterministic_parse")

    action_phrases = _rules(atomic[0], "ActionPhrase")
    action_nodes = _direct_rule_children(action_phrases[0]) \
        if len(action_phrases) == 1 else []
    if len(action_nodes) != 1:
        unresolved.update({"/rimay_core/response/action/family",
                           "/rimay_core/response/action/rimay_action_id"})
        return AdapterPayload(canonical, tuple(sorted(unresolved)))

    action_node = action_nodes[0]
    rule = action_node["name"]
    frames = _action_frames_by_rule()
    frame = frames.get(rule)
    action = {"family": frame["family"] if frame else None,
              "rimay_action_id": rule}
    canonical["rimay_core"]["response"]["action"] = action
    action_source = _source_fragment(source_text, action_node.get("span") or {})
    set_slot(canonical, "/rimay_core/response/action/rimay_action_id", "confirmed",
             action_source, method="rule_application",
             reference=REPOSITORY_GRAMMAR_PROJECTION_REFERENCE)

    # Exact Repository rule identity is syntax evidence, independent of
    # whether Rimay-JP has adopted a product Action Family for it.  Preserve
    # the ID and fail closed only on the unestablished product mapping.
    if frame is None:
        unresolved.add("/rimay_core/response/action/family")
        return AdapterPayload(canonical, tuple(sorted(unresolved)))

    set_slot(canonical, "/rimay_core/response/action/family", "confirmed",
             action_source, method="rule_application",
             reference=REPOSITORY_GRAMMAR_PROJECTION_REFERENCE)

    role_values = _action_role_values(action_node, rule)
    for field, (value, span) in role_values.items():
        canonical["rimay_core"]["response"][field] = value
        set_slot(canonical, f"/rimay_core/response/{field}", "confirmed",
                 _source_fragment(source_text, span), method="deterministic_parse")

    # Product Validator contract: prohibited requirements do not require the
    # positive action's output/destination roles.
    if canonical["rimay_core"]["response"].get("modality") == "MUST":
        for role in frame.get("required_roles", []):
            field = ROLE_FIELD.get(role)
            if field and field != "actor" and \
                    not canonical["rimay_core"]["response"].get(field):
                unresolved.add(f"/rimay_core/response/{field}")
    return AdapterPayload(canonical, tuple(sorted(unresolved)))


def default_repository_adapter_registry() -> RepositoryCanonicalAdapterRegistry:
    registry = RepositoryCanonicalAdapterRegistry()
    registry.register(AdapterSpec(ADAPTER_ID, ROOT_RULE, _project_cnl))
    return registry
