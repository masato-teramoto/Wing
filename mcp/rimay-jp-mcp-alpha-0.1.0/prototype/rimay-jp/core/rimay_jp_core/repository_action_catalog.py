"""Compact Repository Grammar capability and rule-detail projections.

All syntax facts are derived from ``GrammarIR``.  Product action families come
only from the active case-frame binding, while mapping treatments come only
from the versioned Repository projection plan.
"""
from __future__ import annotations

import hashlib
import json

from .lexicon import case_frames
from .repository_document import REPOSITORY_DOCUMENT_SCHEMA_VERSION
from .repository_grammar import GrammarIR, direct_syntax_rule_children


CATALOG_VERSION = "0.1.0"
FULL_DOCUMENT_START_RULE = "CNLFunctionalRequirements"


def _walk(node: dict):
    yield node
    for child in node.get("children", []):
        yield from _walk(child)
    child = node.get("child")
    if isinstance(child, dict):
        yield from _walk(child)


def _canonical_signature(value: object) -> str:
    raw = json.dumps(
        value, ensure_ascii=False, sort_keys=True, separators=(",", ":")
    ).encode("utf-8")
    return "sha256:" + hashlib.sha256(raw).hexdigest()


def repository_action_rule_ids(grammar: GrammarIR) -> list[str]:
    """Return the exact direct ``ActionPhrase`` branch population in order."""
    action = grammar.by_name.get("ActionPhrase")
    if action is None:
        return []
    return list(dict.fromkeys(
        node["name"]
        for node in _walk(action.expression)
        if node.get("kind") == "rule_ref"
    ))


def _mapping_summary(mapping_plan: dict) -> dict:
    treatments: dict[str, int] = {}
    for mapping in mapping_plan.get("mappings", []):
        treatment = mapping.get("treatment")
        if isinstance(treatment, str):
            treatments[treatment] = treatments.get(treatment, 0) + 1
    return {
        "total_surfaces": len(mapping_plan.get("mappings", [])),
        "by_treatment": dict(sorted(treatments.items())),
        "surfaces": [
            {
                "mapping_id": mapping.get("mapping_id"),
                "treatment": mapping.get("treatment"),
                "semantic_relation": mapping.get("semantic_relation"),
                "canonical_target_count": len(
                    mapping.get("canonical_targets") or []
                ),
            }
            for mapping in mapping_plan.get("mappings", [])
        ],
        "plan_id": mapping_plan.get("plan_id"),
        "contract_version": mapping_plan.get("contract_version"),
        "plan_signature": _canonical_signature(mapping_plan),
    }


def _action_identity_smoke(grammar: GrammarIR, action_rules: list[str]) -> dict:
    recognizer = grammar.recognizer()
    failures = []
    for rule_id in action_rules:
        surface = recognizer.synthesize_minimal(rule_id)
        parsed = recognizer.parse_syntax(surface, start_rule="ActionPhrase")
        selected = (
            [node["name"] for node in direct_syntax_rule_children(parsed.tree)]
            if parsed.accepted and isinstance(parsed.tree, dict) else []
        )
        if not parsed.accepted or parsed.ambiguity_detected or selected != [rule_id]:
            failures.append({
                "rule_id": rule_id,
                "accepted": parsed.accepted,
                "ambiguity_detected": parsed.ambiguity_detected,
                "selected_rule_ids": selected,
            })
    return {
        "checked_branch_count": len(action_rules),
        "identity_matched_count": len(action_rules) - len(failures),
        "all_identity_matched": not failures,
        "failures": failures,
    }


def repository_parser_capabilities(grammar: GrammarIR, mapping_plan: dict) -> dict:
    """Project compact executable capabilities without exposing Grammar source."""
    statistics = grammar.statistics()
    action_rules = repository_action_rule_ids(grammar)
    mapping = _mapping_summary(mapping_plan)
    return {
        "catalog_version": CATALOG_VERSION,
        "status": "available",
        "grammar": {
            "source_sha256": grammar.source_sha256,
            "ir_signature": grammar.signature(),
            "parser_rule_count": statistics["parser_rule_count"],
            "enum_rule_count": statistics["enum_count"],
            "executable_rule_count": statistics["rule_count"],
            "full_document_start_rule": FULL_DOCUMENT_START_RULE,
            "action_dispatch_branch_count": len(action_rules),
            "action_rule_ids": action_rules,
            "action_identity_smoke": _action_identity_smoke(
                grammar, action_rules
            ),
        },
        "runtime": {
            "syntax_tree": True,
            "full_consumption": True,
            "ambiguity_check": True,
            "same_document_linking": True,
            "cross_resource_linking": False,
            "xtext_validator": False,
        },
        "repository_document": {"version": REPOSITORY_DOCUMENT_SCHEMA_VERSION},
        "projection_mapping": {
            "total_surfaces": mapping["total_surfaces"],
            **mapping["by_treatment"],
            "surfaces": mapping["surfaces"],
            "plan_id": mapping["plan_id"],
            "contract_version": mapping["contract_version"],
            "plan_signature": mapping["plan_signature"],
        },
        "claims": {
            "parser_authority": "fixed_repository_grammar_recognizer",
            "official_generated_parser_equivalence": False,
            "emse_vor_conformance": "withheld",
        },
    }


def _assignment_records(expression: dict) -> list[dict]:
    records = []
    seen = set()
    for node in _walk(expression):
        if node.get("kind") != "assignment":
            continue
        key = (node.get("feature"), node.get("operator"))
        if key in seen:
            continue
        seen.add(key)
        records.append({"feature": key[0], "operator": key[1]})
    return records


def _enum_or_literal_value(node: dict) -> str | None:
    if node.get("kind") == "literal":
        return node.get("value")
    if node.get("kind") == "enum_literal":
        return node.get("name")
    return None


def _all_literals(expression: dict) -> list[str]:
    values = []
    for node in _walk(expression):
        value = _enum_or_literal_value(node)
        if isinstance(value, str) and value not in values:
            values.append(value)
    return values


def _verb_literals(expression: dict) -> list[str]:
    values = []
    for node in _walk(expression):
        if node.get("kind") != "assignment" or node.get("feature") != "verb":
            continue
        for descendant in _walk(node.get("child") or {}):
            value = _enum_or_literal_value(descendant)
            if isinstance(value, str) and value not in values:
                values.append(value)
    return values


def _reachable_rule_ids(grammar: GrammarIR, rule_id: str) -> list[str]:
    reachable = []
    pending = [rule_id]
    seen = set()
    while pending:
        current = pending.pop(0)
        if current in seen or current not in grammar.by_name:
            continue
        seen.add(current)
        reachable.append(current)
        pending.extend(
            node["name"]
            for node in _walk(grammar.by_name[current].expression)
            if node.get("kind") == "rule_ref" and node.get("name") not in seen
        )
    return reachable


def _reference_records(grammar: GrammarIR, rule_id: str) -> list[dict]:
    records = []
    seen = set()
    for owner_rule in _reachable_rule_ids(grammar, rule_id):
        for node in _walk(grammar.by_name[owner_rule].expression):
            if node.get("kind") != "cross_reference":
                continue
            key = (owner_rule, node.get("target"), node.get("terminal"))
            if key in seen:
                continue
            seen.add(key)
            records.append({
                "via_rule": owner_rule,
                "target": key[1],
                "terminal": key[2],
            })
    return records


def _product_family(rule_id: str) -> str | None:
    for family, frame in case_frames().items():
        if frame.get("rimay_action_id") == rule_id:
            return family
    return None


def _mapping_records(rule_id: str, mapping_plan: dict) -> list[dict]:
    records = []
    for mapping in mapping_plan.get("mappings", []):
        selectors = mapping.get("repository_selectors") or []
        if any(rule_id in (selector.get("rule_ids") or []) for selector in selectors):
            records.append({
                "mapping_id": mapping.get("mapping_id"),
                "treatment": mapping.get("treatment"),
                "semantic_relation": mapping.get("semantic_relation"),
            })
    return records


def _rule_record(grammar: GrammarIR, rule_id: str, mapping_plan: dict) -> dict:
    rule = grammar.by_name[rule_id]
    mappings = _mapping_records(rule_id, mapping_plan)
    treatments = list(dict.fromkeys(
        mapping["treatment"] for mapping in mappings
        if isinstance(mapping.get("treatment"), str)
    ))
    return {
        "rule_id": rule.name,
        "rule_kind": rule.kind,
        "returns": rule.returns,
        "derived_from_grammar_ir": True,
        "verb_literals": _verb_literals(rule.expression),
        "literals": _all_literals(rule.expression),
        "assignments": _assignment_records(rule.expression),
        "referenced_rules": _reachable_rule_ids(grammar, rule_id)[1:],
        "references": _reference_records(grammar, rule_id),
        "minimal_example": (
            grammar.recognizer().synthesize_minimal(rule_id)
            if rule.kind == "parser_rule" else None
        ),
        "is_action_dispatch": rule_id in repository_action_rule_ids(grammar),
        "product_action_family": _product_family(rule_id),
        "mapping_treatment": treatments[0] if len(treatments) == 1 else (
            "mixed" if treatments else None
        ),
        "mapping_records": mappings,
    }


def repository_rule_details(
    grammar: GrammarIR,
    mapping_plan: dict,
    *,
    literals: list[str] | None = None,
    rule_ids: list[str] | None = None,
    max_results: int = 5,
) -> dict:
    """Query selected IR facts without returning raw Grammar or IR bodies."""
    if type(max_results) is not int or not 1 <= max_results <= 20:
        raise ValueError("max_results must be an integer from 1 through 20")
    requested_rules = list(dict.fromkeys(rule_ids or []))
    unknown = [rule_id for rule_id in requested_rules if rule_id not in grammar.by_name]
    literal_queries = [item.casefold() for item in (literals or []) if item]

    selected = [rule_id for rule_id in requested_rules if rule_id in grammar.by_name]
    for rule in grammar.rules:
        if rule.name in selected:
            continue
        values = _all_literals(rule.expression)
        if literal_queries and any(
            query in value.casefold()
            for query in literal_queries
            for value in values
        ):
            selected.append(rule.name)
    total_matches = len(selected)
    selected = selected[:max_results]
    return {
        "catalog_version": CATALOG_VERSION,
        "grammar_source_sha256": grammar.source_sha256,
        "grammar_ir_signature": grammar.signature(),
        "query": {
            "literals": literals or [],
            "rule_ids": rule_ids or [],
            "max_results": max_results,
        },
        "unknown_rule_ids": unknown,
        "truncated": total_matches > max_results,
        "results": [_rule_record(grammar, rule_id, mapping_plan) for rule_id in selected],
    }
