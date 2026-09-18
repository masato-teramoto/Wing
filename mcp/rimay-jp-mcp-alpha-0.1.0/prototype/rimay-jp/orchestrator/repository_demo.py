"""Stateless facade for the Repository-Grammar-backed dialogue demo."""
from __future__ import annotations

import hashlib
import json
import os
from functools import lru_cache
from pathlib import Path

import yaml

from rimay_jp_core import PROFILE_VERSION, SCHEMA_VERSION, __version__
from rimay_jp_core.jp_serializer import render_rimay_jp
from rimay_jp_core.lexicon import ROOT, versions
from rimay_jp_core.model import is_blocked
from rimay_jp_core.normalizer import normalize
from rimay_jp_core.repository_action_catalog import (
    FULL_DOCUMENT_START_RULE,
    repository_parser_capabilities,
    repository_rule_details,
)
from rimay_jp_core.repository_canonical import default_repository_adapter_registry
from rimay_jp_core.repository_candidate_bridge import (
    BRIDGE_VERSION,
    build_repository_candidate,
)
from rimay_jp_core.repository_document import (
    REPOSITORY_DOCUMENT_SCHEMA_VERSION,
    project_repository_document,
)
from rimay_jp_core.repository_grammar import (
    FIXED_GRAMMAR_SHA256,
    GrammarCompileError,
    compile_xtext_grammar,
    direct_syntax_rule_children,
    syntax_tree_signature,
    walk_syntax_tree,
)
from rimay_jp_core.repository_linker import link_repository_syntax
from rimay_jp_core.repository_projection_mapping import (
    validate_repository_projection_mapping_schema,
)
from rimay_jp_core.serializer import render_requirement_views
from rimay_jp_core.schema_check import validate_schema
from rimay_jp_core.validator import validate


DEMO_CONTRACT_VERSION = "0.1.0"
JAPANESE_ALPHA_CONTRACT_VERSION = "0.1.0"
MAPPING_PLAN_PATH = ROOT / "canonical" / "repository-projection-mapping-plan.yaml"
CANONICAL_SCHEMA_PATH = ROOT / "canonical" / "canonical-requirement.schema.json"
BUNDLED_FIXED_GRAMMAR_PATH = (
    ROOT / "adapters" / "mcp" / "assets" / "Dsl_rimay.xtext"
)
ALPHA_DISTRIBUTION_PATH = ROOT / "adapters" / "mcp" / "alpha-distribution.yaml"
REPOSITORY_ROOT = ROOT.parents[1]
_CANDIDATE_ORIGINS = frozenset({
    "rimay_jp_repository_bridge", "llm", "rimay_jp_native",
})
_SAFE_ACTIVE_MAPPING_IDS = frozenset({
    "RPMAP-RESPONSE-BLOCK-PRESERVED",
    "RPMAP-RESPONSE-COMBINATION-PRESERVED",
    "RPMAP-ATOMIC-RESPONSE-PRESERVED",
})


class RepositoryDemoContractError(ValueError):
    """Fixed authority or demo input contract is unavailable or invalid."""


def _signature(value: object) -> str:
    encoded = json.dumps(
        value, ensure_ascii=False, sort_keys=True, separators=(",", ":")
    ).encode("utf-8")
    return "sha256:" + hashlib.sha256(encoded).hexdigest()


def _text_signature(value: str) -> str:
    return "sha256:" + hashlib.sha256(value.encode("utf-8")).hexdigest()


def _file_signature(path: Path) -> str:
    return "sha256:" + hashlib.sha256(path.read_bytes()).hexdigest()


@lru_cache(maxsize=2)
def _compile_fixed_source(source: str):
    return compile_xtext_grammar(source, expected_sha256=FIXED_GRAMMAR_SHA256)


def _fixed_grammar_binding():
    configured = os.environ.get("RIMAY_FIXED_GRAMMAR")
    if configured:
        path = Path(configured)
        if not path.is_absolute():
            path = REPOSITORY_ROOT / path
        source_kind = "environment_override"
    else:
        path = BUNDLED_FIXED_GRAMMAR_PATH
        source_kind = "bundled_alpha"
    try:
        source = path.read_text(encoding="utf-8")
    except OSError as exc:
        raise RepositoryDemoContractError(
            f"cannot read fixed Repository Grammar: {exc}"
        ) from exc
    try:
        return _compile_fixed_source(source), path.resolve(), source_kind
    except GrammarCompileError as exc:
        raise RepositoryDemoContractError(str(exc)) from exc


def _fixed_grammar():
    return _fixed_grammar_binding()[0]


def _alpha_distribution() -> dict:
    try:
        value = yaml.safe_load(ALPHA_DISTRIBUTION_PATH.read_text(encoding="utf-8"))
    except (OSError, yaml.YAMLError) as exc:
        raise RepositoryDemoContractError(
            f"cannot load alpha distribution contract: {exc}"
        ) from exc
    if not isinstance(value, dict):
        raise RepositoryDemoContractError(
            "alpha distribution contract must be a mapping"
        )
    return value


def _mapping_plan() -> dict:
    try:
        plan = yaml.safe_load(MAPPING_PLAN_PATH.read_text(encoding="utf-8"))
    except (OSError, yaml.YAMLError) as exc:
        raise RepositoryDemoContractError(f"cannot load mapping plan: {exc}") from exc
    problems = validate_repository_projection_mapping_schema(plan)
    if problems:
        raise RepositoryDemoContractError(
            "mapping plan schema invalid: " + "; ".join(problems)
        )
    return plan


def _grammar_queries(canonical: dict, reason_codes: list[str]) -> list[str]:
    queries = []
    if "TRIGGER_SHAPE_INCOMPATIBLE" in reason_codes:
        queries.append("Trigger")
    if "PROPERTY_OWNER_UNRESOLVED" in reason_codes:
        queries.extend(["Class", "PropertyId"])
    action = ((canonical.get("rimay_core") or {}).get("response") or {}).get("action") or {}
    rule_id = action.get("rimay_action_id")
    if isinstance(rule_id, str):
        queries.append(rule_id)
    return list(dict.fromkeys(queries))


def _merge_findings(*groups: list[dict]) -> list[dict]:
    merged = []
    seen = set()
    for group in groups:
        for finding in group:
            key = (
                finding.get("code"),
                finding.get("path"),
                finding.get("message"),
            )
            if key not in seen:
                seen.add(key)
                merged.append(finding)
    return merged


def analyze_japanese_requirement(
    source_text_ja: str,
    requirement_id: str = "REQ-DEMO",
    request_id: str = "REQ-DEMO-JA",
    detail: str = "compact",
) -> dict:
    """Run the product Normalizer first and assess the lossless bridge boundary.

    Parser verification is intentionally a separate full-candidate operation.  A
    bridge-ready response therefore says ``not_run`` and provides the candidate
    for the common evaluator; it never aliases Normalizer success to Parser P1.
    """
    if detail not in {"compact", "full"}:
        raise ValueError("detail must be 'compact' or 'full'")
    canonical, normalizer_findings = normalize(source_text_ja, requirement_id)
    schema_errors = validate_schema(canonical)
    profile_findings = validate(canonical, phase2_slice=False)
    findings = _merge_findings(normalizer_findings, profile_findings)
    blocked = bool(schema_errors) or is_blocked(findings)

    views = None
    if not blocked:
        rendered = render_requirement_views(canonical)
        views = {
            "rimay_jp": render_rimay_jp(canonical),
            "english_rimay": rendered["english_rimay"],
            "manifest": rendered["manifest"],
        }

    if blocked:
        bridge = {
            "bridge_version": BRIDGE_VERSION,
            "status": "not_attempted",
            "lossless": False,
            "reason_codes": ["NORMALIZER_BLOCKING_FINDINGS"],
            "resolved_codes": [],
            "candidate_origin": None,
            "repository_candidate": None,
            "synthesized_declarations": [],
            "trace": [],
            "diagnostics": [],
            "preserve_native_candidate": True,
        }
        native_status = "fallback_required"
    else:
        bridge = build_repository_candidate(canonical)
        native_status = (
            "native_candidate"
            if bridge["status"] == "bridge_ready"
            else "native_candidate_repository_incompatible"
        )

    reason_codes = bridge["reason_codes"]
    fallback_required = blocked or bridge["status"] != "bridge_ready"
    signature_input = {
        "demo_contract_version": DEMO_CONTRACT_VERSION,
        "tool": "analyze_japanese_requirement",
        "request_id": request_id,
        "requirement_id": requirement_id,
        "source_text_ja": source_text_ja,
        "detail": detail,
        "rimay_jp_version": __version__,
        "profile_version": PROFILE_VERSION,
        "schema_version": SCHEMA_VERSION,
    }
    response = {
        "demo_contract_version": DEMO_CONTRACT_VERSION,
        "tool": "analyze_japanese_requirement",
        "request_id": request_id,
        "input_signature": _signature(signature_input),
        "native_analysis": {
            "status": native_status,
            "profile_version": PROFILE_VERSION,
            "schema_version": SCHEMA_VERSION,
            "candidate_origin": "rimay_jp_normalizer" if not blocked else None,
            "canonical_candidate": canonical,
            "product_rimay_jp": views["rimay_jp"] if views else None,
            "product_english_rimay": views["english_rimay"] if views else None,
            "schema_errors": schema_errors,
            "normalizer_findings": normalizer_findings,
            "profile_findings": profile_findings,
            "findings": findings,
        },
        "repository_compatibility": bridge,
        "fallback": {
            "required": fallback_required,
            "preserve_native_candidate": True,
            "grammar_queries": _grammar_queries(canonical, reason_codes),
        },
        "parser_verification": {
            "status": "not_run",
            "next_tool": "evaluate_rimay_candidate" if not fallback_required else None,
        },
        "authority": {
            "normalizer": "rimay_jp_product_normalizer",
            "repository_bridge": "deterministic_lossless_subset",
            "parser": "not_run",
            "semantic_alignment_with_japanese": "not_checked_by_rimay_jp",
        },
    }
    if detail == "full" and views:
        response["native_analysis"]["product_manifest"] = views["manifest"]
    return response


def inspect_japanese_requirement_alpha(
    source_text_ja: str,
    rimay_candidate: str | None = None,
    requirement_id: str = "REQ-ALPHA",
    request_id: str = "REQ-ALPHA-JA",
    detail: str = "compact",
) -> dict:
    """Inspect arbitrary Japanese input through one stateless alpha entry point.

    Japanese smells remain advisory.  Syntax is checked only against a complete
    Repository Rimay candidate: the deterministic bridge is used when available,
    otherwise the MCP host or user may supply a candidate for any fixed-Grammar
    action branch.  The parser result never claims Japanese semantic equivalence.
    """
    if not isinstance(source_text_ja, str) or not source_text_ja.strip():
        raise ValueError("source_text_ja must be a non-empty string")
    if rimay_candidate is not None and (
        not isinstance(rimay_candidate, str) or not rimay_candidate.strip()
    ):
        raise ValueError("rimay_candidate must be a non-empty string when provided")

    # This is the same Free-text Import diagnostic path exposed by
    # diagnose_raw_text; it remains advisory and is not a second blocking parser.
    from orchestrator.raw_text_gate import inspect as inspect_raw_text

    japanese_quality = inspect_raw_text(
        source_text_ja, language="ja", case_id=requirement_id
    )
    native_analysis = analyze_japanese_requirement(
        source_text_ja,
        requirement_id=requirement_id,
        request_id=request_id,
        detail=detail,
    )

    candidate = rimay_candidate
    candidate_origin = "llm" if candidate is not None else None
    candidate_source = "provided" if candidate is not None else "none"
    bridge = native_analysis["repository_compatibility"]
    if candidate is None and bridge["status"] == "bridge_ready":
        candidate = bridge["repository_candidate"]
        candidate_origin = bridge["candidate_origin"]
        candidate_source = "deterministic_bridge"

    evaluation = None
    if candidate is not None and candidate_origin is not None:
        evaluation = evaluate_rimay_candidate(
            candidate,
            candidate_origin=candidate_origin,
            source_text_ja=source_text_ja,
            request_id=request_id,
            detail=detail,
        )

    parser_status = (
        evaluation["parser"]["status"] if evaluation is not None else "not_run"
    )
    linking_status = (
        evaluation["linking"]["status"] if evaluation is not None else "not_run"
    )
    repository_status = (
        evaluation["repository_projection"]["status"]
        if evaluation is not None else "not_run"
    )
    canonical_status = (
        evaluation["canonical_projection"]["status"]
        if evaluation is not None else "not_run"
    )
    action_rule_ids = (
        evaluation["parser"]["selected_action_rule_ids"]
        if evaluation is not None else []
    )

    if evaluation is None:
        status = "candidate_required"
        next_action = "supply_complete_rimay_candidate"
    elif parser_status in {"rejected", "ambiguous"}:
        status = f"syntax_{parser_status}"
        next_action = "revise_rimay_candidate"
    elif linking_status == "failed":
        status = "syntax_accepted_linking_failed"
        next_action = "declare_or_correct_references"
    elif repository_status == "failed":
        status = "repository_projection_failed"
        next_action = "inspect_repository_projection_diagnostics"
    else:
        status = "checked"
        next_action = "review_japanese_semantic_alignment"

    issue_codes = list(dict.fromkeys([
        finding["normalized_issue_code"]
        for finding in japanese_quality["findings"]
    ] + [
        signal["issue_code"] for signal in japanese_quality["cross_signals"]
    ]))
    return {
        "alpha_contract_version": JAPANESE_ALPHA_CONTRACT_VERSION,
        "tool": "inspect_japanese_requirement_alpha",
        "request_id": request_id,
        "summary": {
            "status": status,
            "candidate_source": candidate_source,
            "parser_status": parser_status,
            "linking_status": linking_status,
            "repository_projection_status": repository_status,
            "canonical_projection_status": canonical_status,
            "selected_action_rule_ids": action_rule_ids,
            "detected_smell_count": len(japanese_quality["raw_smells"]),
            "smell_issue_codes": issue_codes,
            "next_action": next_action,
        },
        "japanese_quality": {
            "mode": "advisory",
            **japanese_quality,
        },
        "japanese_analysis": native_analysis,
        "candidate": {
            "source": candidate_source,
            "origin": candidate_origin,
            "rimay_candidate": candidate,
        },
        "fixed_grammar_evaluation": evaluation,
        "candidate_guidance": {
            "required": evaluation is None,
            "grammar_queries": native_analysis["fallback"]["grammar_queries"],
            "rule_lookup_tool": "get_repository_rule_details",
            "evaluation_scope": "complete_fixed_grammar_document",
        },
        "authority": {
            "japanese_smells": "raw_text_quality_gate_advisory",
            "syntax": (
                "fixed_repository_grammar_recognizer"
                if evaluation is not None else "not_run"
            ),
            "candidate_generation": (
                "deterministic_lossless_subset"
                if candidate_source == "deterministic_bridge"
                else "host_or_user" if candidate_source == "provided"
                else "not_run"
            ),
            "semantic_alignment_with_japanese": "not_checked_by_rimay_jp",
            "official_generated_parser_equivalence": False,
        },
    }


def get_repository_parser_capabilities() -> dict:
    """Return executable fixed-Grammar facts and the current mapping summary."""
    grammar, grammar_path, source_kind = _fixed_grammar_binding()
    distribution = _alpha_distribution()
    try:
        reported_path = grammar_path.relative_to(REPOSITORY_ROOT).as_posix()
    except ValueError:
        reported_path = str(grammar_path)
    return {
        "demo_contract_version": DEMO_CONTRACT_VERSION,
        "tool": "get_repository_parser_capabilities",
        "rimay_jp_version": __version__,
        "distribution": {
            "distribution_version": distribution.get("distribution_version"),
            "mode": distribution.get("mode"),
            "audience": distribution.get("audience"),
            "grammar_source": source_kind,
            "grammar_path": reported_path,
            "beta_replacement": (distribution.get("sunset") or {}).get(
                "replacement"
            ),
        },
        **repository_parser_capabilities(grammar, _mapping_plan()),
    }


def get_repository_rule_details(
    literals: list[str] | None = None,
    rule_ids: list[str] | None = None,
    max_results: int = 5,
) -> dict:
    """Return only requested Grammar IR facts for LLM candidate construction."""
    return {
        "demo_contract_version": DEMO_CONTRACT_VERSION,
        "tool": "get_repository_rule_details",
        **repository_rule_details(
            _fixed_grammar(), _mapping_plan(), literals=literals,
            rule_ids=rule_ids, max_results=max_results,
        ),
    }


def _selected_action_rule_ids(tree: dict | None) -> list[str]:
    selected = []
    if not isinstance(tree, dict):
        return selected
    for node in walk_syntax_tree(tree):
        if node.get("kind") != "rule" or node.get("name") != "ActionPhrase":
            continue
        children = direct_syntax_rule_children(node)
        if len(children) == 1:
            selected.append(children[0]["name"])
    return list(dict.fromkeys(selected))


def _compact_action_facts(document: dict | None) -> list[dict]:
    facts = []
    if not isinstance(document, dict):
        return facts
    for requirement_index, requirement in enumerate(document.get("requirements", [])):
        for response_index, response in enumerate(requirement.get("atomic_responses", [])):
            action = response.get("action") or {}
            facts.append({
                "requirement_index": requirement_index,
                "response_index": response_index,
                "rule_id": action.get("rule_id"),
                "source": action.get("source"),
                "span": action.get("span"),
                "assignments": [
                    {
                        "owner_rule": assignment.get("owner_rule"),
                        "rule_path": assignment.get("rule_path"),
                        "feature": assignment.get("feature"),
                        "operator": assignment.get("operator"),
                        "source": assignment.get("source"),
                        "span": assignment.get("span"),
                        "values": assignment.get("values", []),
                    }
                    for assignment in action.get("assignments", [])
                ],
            })
    return facts


def _expression_summary(node: dict | None) -> dict | None:
    if not isinstance(node, dict):
        return None
    summary = {"kind": node.get("kind")}
    if "atomic_response_index" in node:
        summary["atomic_response_index"] = node["atomic_response_index"]
    if "atomic_action_index" in node:
        summary["atomic_action_index"] = node["atomic_action_index"]
    if isinstance(node.get("expression"), dict):
        summary["expression"] = _expression_summary(node["expression"])
    if isinstance(node.get("left"), dict):
        summary["left"] = _expression_summary(node["left"])
    if isinstance(node.get("right"), dict):
        summary["right"] = _expression_summary(node["right"])
    return summary


def _condition_summary(structure: dict | None) -> dict | None:
    if not isinstance(structure, dict):
        return None
    conditions = []
    for item in structure.get("conditions", []):
        condition = item.get("condition") or {}
        payload = condition.get("payload") or {}
        conditions.append({
            "index": item.get("index"),
            "kind": condition.get("kind"),
            "connector_before": (
                (item.get("connector_before") or {}).get("kind")
            ),
            "payload_kind": payload.get("kind"),
            "expression": _expression_summary(payload.get("expression")),
            "trigger_action_structure": _expression_summary(
                payload.get("action_structure")
            ),
            "trigger_action_rule_ids": [
                (atomic.get("action") or {}).get("rule_id")
                for atomic in payload.get("atomic_actions", [])
            ],
        })
    return {
        "kind": structure.get("kind"),
        "conditions": conditions,
        "response_connector": (
            (structure.get("response_connector") or {}).get("kind")
        ),
    }


def _response_summary(structure: dict | None) -> dict | None:
    if not isinstance(structure, dict):
        return None
    return {
        "kind": structure.get("kind"),
        "expression": _expression_summary(structure.get("expression")),
        "in_sequence": structure.get("in_sequence") is not None,
        "items": [
            {
                "index": item.get("index"),
                "atomic_response_index": item.get("atomic_response_index"),
                "bullet": (item.get("bullet") or {}).get("kind"),
                "connector_before": (
                    (item.get("connector_before") or {}).get("kind")
                ),
            }
            for item in structure.get("items", [])
        ],
    }


def _compact_structure_facts(document: dict | None) -> list[dict]:
    if not isinstance(document, dict):
        return []
    return [
        {
            "requirement_index": index,
            "scope_present": requirement.get("scope") is not None,
            "response": _response_summary(requirement.get("response_structure")),
            "conditions": _condition_summary(
                requirement.get("condition_structure")
            ),
        }
        for index, requirement in enumerate(document.get("requirements", []))
    ]


def _population_counts(document: dict | None, key: str, field: str) -> dict:
    counts: dict[str, int] = {}
    if not isinstance(document, dict):
        return counts
    for item in document.get(key, []):
        value = item.get(field)
        if isinstance(value, str):
            counts[value] = counts.get(value, 0) + 1
    return dict(sorted(counts.items()))


def _pointer_exists(document: dict, pointer: str) -> bool:
    current: object = document
    for segment in pointer.removeprefix("/").split("/"):
        if isinstance(current, dict) and segment in current:
            current = current[segment]
        elif isinstance(current, list) and segment.isdigit() and \
                int(segment) < len(current):
            current = current[int(segment)]
        else:
            return False
    return True


def _mapping_ids(
    tree: dict | None,
    mapping_plan: dict,
    canonical_candidate: dict | None,
    unresolved_paths: tuple[str, ...],
) -> tuple[list[str], list[str]]:
    rule_names = {
        node["name"]
        for node in walk_syntax_tree(tree)
        if isinstance(tree, dict) and node.get("kind") == "rule"
    } if isinstance(tree, dict) else set()
    active = []
    residual = []
    for mapping in mapping_plan.get("mappings", []):
        selector_ids = {
            rule_id
            for selector in mapping.get("repository_selectors", [])
            for rule_id in selector.get("rule_ids", [])
        }
        if not selector_ids.intersection(rule_names):
            continue
        mapping_id = mapping["mapping_id"]
        targets = mapping.get("canonical_targets", [])
        represented_targets = [
            target for target in targets
            if isinstance(canonical_candidate, dict)
            and _pointer_exists(canonical_candidate, target)
        ]
        target_unresolved = any(
            unresolved == target
            or unresolved.startswith(target + "/")
            or target.startswith(unresolved + "/")
            for unresolved in unresolved_paths
            for target in represented_targets
        )
        safe_active = (
            mapping.get("treatment") == "existing_canonical"
            and mapping_id in _SAFE_ACTIVE_MAPPING_IDS
            and bool(represented_targets)
            and not target_unresolved
        )
        (active if safe_active else residual).append(mapping_id)
    return active, residual


def _linking_section(linked) -> dict:
    if linked is None:
        return {
            "checked": False, "status": "not_run", "unresolved": [],
            "ambiguous": [], "type_mismatch": [], "symbol_count": 0,
            "reference_count": 0, "resolved_reference_count": 0,
        }
    problems = list(linked.problems)
    return {
        "checked": linked.checked,
        "status": "succeeded" if linked.succeeded else "failed",
        "unresolved": [
            problem for problem in problems
            if problem.get("code") == "UNRESOLVED_REFERENCE"
        ],
        "ambiguous": [
            problem for problem in problems
            if problem.get("code") in {"AMBIGUOUS_REFERENCE", "DUPLICATE_DECLARATION"}
        ],
        "type_mismatch": [
            problem for problem in problems
            if problem.get("code") in {
                "REFERENCE_TYPE_MISMATCH", "UNSUPPORTED_TARGET_TYPE",
            }
        ],
        "symbol_count": len(linked.symbols),
        "reference_count": len(linked.references),
        "resolved_reference_count": sum(
            reference.get("status") == "resolved"
            for reference in linked.references
        ),
    }


def evaluate_rimay_candidate(
    rimay_candidate: str,
    candidate_origin: str,
    source_text_ja: str | None = None,
    request_id: str = "REQ-DEMO-CANDIDATE",
    start_rule: str = FULL_DOCUMENT_START_RULE,
    detail: str = "compact",
) -> dict:
    """Parse, link, preserve, and optionally project one complete candidate."""
    if candidate_origin not in _CANDIDATE_ORIGINS:
        raise ValueError(f"unknown candidate_origin: {candidate_origin!r}")
    if start_rule != FULL_DOCUMENT_START_RULE:
        raise ValueError(
            f"evaluate_rimay_candidate requires {FULL_DOCUMENT_START_RULE}"
        )
    if detail not in {"compact", "full"}:
        raise ValueError("detail must be 'compact' or 'full'")
    if not isinstance(rimay_candidate, str) or not rimay_candidate:
        raise ValueError("rimay_candidate must be a non-empty string")

    grammar = _fixed_grammar()
    mapping_plan = _mapping_plan()
    parsed = grammar.recognizer().parse_syntax(rimay_candidate, start_rule=start_rule)
    parser_status = "rejected"
    if parsed.accepted:
        parser_status = "ambiguous" if parsed.ambiguity_detected else "accepted"

    linked = None
    repository_projection = None
    canonical_projection = None
    canonical_schema_errors: list[str] = []
    canonical_findings: list[dict] = []
    if parsed.accepted and not parsed.ambiguity_detected:
        linked = link_repository_syntax(grammar, parsed, rimay_candidate)
    if linked is not None and linked.succeeded:
        repository_projection = project_repository_document(
            parsed, rimay_candidate, linked, grammar
        )
        canonical_projection = default_repository_adapter_registry().project(
            parsed, rimay_candidate, linked, grammar
        )
        if canonical_projection.canonical_candidate is not None:
            canonical_schema_errors = validate_schema(
                canonical_projection.canonical_candidate
            )
            canonical_findings = validate(
                canonical_projection.canonical_candidate, phase2_slice=False
            )

    repository_document = (
        repository_projection.document
        if repository_projection is not None
        and repository_projection.status == "projected_document"
        else None
    )
    candidate_canonical = (
        canonical_projection.canonical_candidate
        if canonical_projection is not None else None
    )
    unresolved_paths = (
        canonical_projection.unresolved_paths
        if canonical_projection is not None else ()
    )
    active_mapping_ids, residual_mapping_ids = _mapping_ids(
        parsed.tree, mapping_plan, candidate_canonical, unresolved_paths
    ) if linked is not None and linked.succeeded else ([], [])

    canonical_blocking = [
        finding for finding in canonical_findings if finding.get("blocking")
    ]
    if canonical_projection is None:
        canonical_status = "not_run"
        validation_status = "not_run"
    elif canonical_projection.status != "adapted_candidate" or \
            candidate_canonical is None:
        canonical_status = "unavailable"
        validation_status = "not_run"
    elif unresolved_paths or canonical_schema_errors or canonical_blocking:
        canonical_status = "partial"
        validation_status = "failed"
    else:
        canonical_status = "valid"
        validation_status = "passed"

    blocking = []
    advisory = []
    if not parsed.accepted:
        start = max(0, parsed.furthest_offset - 20)
        end = min(len(rimay_candidate), parsed.furthest_offset + 20)
        blocking.append({
            "code": "PARSER_REJECTED",
            "message": "candidate is not a fixed-Grammar full match",
            "furthest_offset": parsed.furthest_offset,
            "near_surface": rimay_candidate[start:end],
        })
    elif parsed.ambiguity_detected:
        blocking.append({
            "code": "PARSER_AMBIGUOUS",
            "message": "multiple full-match derivations were detected",
        })
    elif linked is not None and not linked.succeeded:
        blocking.extend(linked.problems)
    elif repository_projection is not None and \
            repository_projection.status != "projected_document":
        blocking.append({
            "code": "REPOSITORY_PROJECTION_FAILED",
            "message": repository_projection.message,
            "status": repository_projection.status,
        })
    if canonical_projection is not None and canonical_status != "valid":
        advisory.append({
            "code": "CANONICAL_PROJECTION_INCOMPLETE",
            "message": canonical_projection.reason,
            "status": canonical_projection.status,
            "unresolved_paths": list(unresolved_paths),
            "schema_errors": canonical_schema_errors,
            "blocking_findings": canonical_blocking,
        })

    normalizer_signature = versions()["profile_content_hash"] \
        if candidate_origin != "llm" else None
    canonical_schema_signature = _file_signature(CANONICAL_SCHEMA_PATH) \
        if canonical_projection is not None else None
    mapping_signature = _signature(mapping_plan)
    signature_inputs = {
        "rimay_candidate_sha256": _text_signature(rimay_candidate),
        "candidate_origin": candidate_origin,
        "start_rule": start_rule,
        "response_schema_version": DEMO_CONTRACT_VERSION,
        "rimay_jp_version": __version__,
        "normalizer_profile_signature": normalizer_signature,
        "grammar_source_sha256": grammar.source_sha256,
        "grammar_ir_signature": grammar.signature(),
        "repository_document_schema_version": REPOSITORY_DOCUMENT_SCHEMA_VERSION,
        "mapping_plan_signature": mapping_signature,
        "canonical_schema_signature": canonical_schema_signature,
    }
    response = {
        "demo_contract_version": DEMO_CONTRACT_VERSION,
        "tool": "evaluate_rimay_candidate",
        "request_id": request_id,
        "input_signature": _signature(signature_inputs),
        "candidate": {
            "origin": candidate_origin,
            "source_text_ja_sha256": (
                _text_signature(source_text_ja) if source_text_ja is not None else None
            ),
            "rimay_candidate_sha256": _text_signature(rimay_candidate),
            "semantic_alignment_with_japanese": "not_checked_by_rimay_jp",
        },
        "parser": {
            "status": parser_status,
            "authority": "fixed_repository_grammar_recognizer",
            "start_rule": start_rule,
            "full_consumption": bool(
                parsed.accepted and parsed.consumed_end == len(rimay_candidate)
            ),
            "consumed_end": parsed.consumed_end,
            "furthest_offset": parsed.furthest_offset,
            "ambiguity_checked": parsed.ambiguity_checked,
            "ambiguity_detected": parsed.ambiguity_detected,
            "semantic_linking_checked": False,
            "xtext_validator_checked": False,
            "selected_action_rule_ids": _selected_action_rule_ids(parsed.tree),
            "syntax_tree_signature": (
                syntax_tree_signature(parsed.tree) if parsed.tree is not None else None
            ),
        },
        "linking": _linking_section(linked),
        "repository_projection": {
            "status": (
                "succeeded" if repository_document is not None
                else "failed" if repository_projection is not None else "not_run"
            ),
            "document_version": (
                REPOSITORY_DOCUMENT_SCHEMA_VERSION
                if repository_document is not None else None
            ),
            "requirement_count": (
                len(repository_document.get("requirements", []))
                if repository_document is not None else None
            ),
            "action_facts": _compact_action_facts(repository_document),
            "structure_facts": _compact_structure_facts(repository_document),
            "declaration_counts": _population_counts(
                repository_document, "declarations", "rule_id"
            ),
            "instance_counts": _population_counts(
                repository_document, "instances", "kind"
            ),
        },
        "canonical_projection": {
            "status": canonical_status,
            "active_mapping_ids": active_mapping_ids,
            "residual_mapping_ids": residual_mapping_ids,
            "canonical_candidate": candidate_canonical if detail == "full" else None,
            "validation": validation_status,
        },
        "diagnostics": {"blocking": blocking, "advisory": advisory},
        "provenance": {
            "rimay_jp_version": __version__,
            "response_schema_version": DEMO_CONTRACT_VERSION,
            "normalizer_profile_signature": normalizer_signature,
            "grammar_source_sha256": grammar.source_sha256,
            "grammar_ir_signature": grammar.signature(),
            "repository_document_schema_version": REPOSITORY_DOCUMENT_SCHEMA_VERSION,
            "mapping_plan_signature": mapping_signature,
            "canonical_schema_signature": canonical_schema_signature,
            "signature_inputs_complete": True,
        },
    }
    if detail == "full":
        response["parser"]["syntax_tree"] = parsed.tree
        response["linking"]["symbols"] = list(linked.symbols) if linked else []
        response["linking"]["references"] = list(linked.references) if linked else []
        response["linking"]["problems"] = list(linked.problems) if linked else []
        response["repository_projection"]["document"] = repository_document
    return response
