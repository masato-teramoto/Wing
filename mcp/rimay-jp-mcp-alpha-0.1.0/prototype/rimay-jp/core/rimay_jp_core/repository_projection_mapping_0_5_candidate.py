"""Isolated design audit for Repository projection mapping contract 0.5.

The active mapping contract and adapter remain on 0.4.  This module validates
the proposed owner/provider/supersession contract and proves deterministic
record-level dispatch without registering that dispatch in the product
runtime.
"""
from __future__ import annotations

import hashlib
import json
from collections import Counter
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path

from jsonschema import Draft202012Validator

from .lexicon import ROOT


REPOSITORY_PROJECTION_MAPPING_CANDIDATE_VERSION = "0.5.0"
CANDIDATE_SCHEMA_PATH = (
    ROOT / "canonical/candidates/"
    "repository-projection-mapping-contract-0.5.0-candidate.schema.json"
)
_REQUIRED_FACETS = frozenset({"identity", "operator", "value"})
_REQUIRED_VALUE_SHAPES = frozenset({"scalar", "tree"})


@dataclass(frozen=True)
class MappingContractCandidateAssessment:
    accepted: bool
    problems: tuple[str, ...]


@dataclass(frozen=True)
class LeafSemanticDispatch:
    rule_id: str
    value_shape: str
    facet_providers: tuple[tuple[str, tuple[str, ...]], ...]


@dataclass(frozen=True)
class RepositoryProjectionDispatchDecision:
    selected_mapping_id: str
    state: str
    reason_code: str | None
    leaves: tuple[LeafSemanticDispatch, ...]
    suppressed_mapping_ids: tuple[str, ...]


@dataclass(frozen=True)
class RepositoryProjectionDispatchCandidateError(ValueError):
    code: str
    message: str

    def __str__(self) -> str:
        return f"{self.code}: {self.message}"


@lru_cache(maxsize=1)
def _candidate_validator() -> Draft202012Validator:
    with CANDIDATE_SCHEMA_PATH.open(encoding="utf-8") as stream:
        schema = json.load(stream)
    Draft202012Validator.check_schema(schema)
    return Draft202012Validator(schema)


def validate_repository_projection_mapping_candidate_schema(
    candidate: dict,
) -> list[str]:
    """Return stable path-prefixed structural violations."""
    errors = sorted(
        _candidate_validator().iter_errors(candidate),
        key=lambda error: (
            tuple(str(part) for part in error.absolute_path), error.message),
    )
    return [
        f"{'/'.join(str(part) for part in error.absolute_path) or '<root>'}: "
        f"{error.message}"
        for error in errors
    ]


def _file_sha256(path: Path) -> str | None:
    try:
        return "sha256:" + hashlib.sha256(path.read_bytes()).hexdigest()
    except OSError:
        return None


def _resolve_artifact(project_root: Path, ref: dict) -> Path | None:
    relative = Path(ref["path"])
    if relative.is_absolute() or ".." in relative.parts:
        return None
    root = project_root.resolve()
    resolved = (root / relative).resolve()
    try:
        resolved.relative_to(root)
    except ValueError:
        return None
    return resolved


def _mapping_record_kind(mapping: dict, record_kind: str) -> bool:
    return any(
        isinstance(selector, dict)
        and selector.get("record_kind") == record_kind
        for selector in mapping.get("repository_selectors", [])
    )


def assess_repository_projection_mapping_candidate(
    candidate: dict,
    active_plan: dict,
    *,
    project_root: Path | str = ROOT,
) -> MappingContractCandidateAssessment:
    """Audit the 0.5 candidate against the byte-bound active 0.4 plan."""
    schema_problems = validate_repository_projection_mapping_candidate_schema(
        candidate)
    if schema_problems:
        return MappingContractCandidateAssessment(False, tuple(schema_problems))
    if not isinstance(active_plan, dict):
        return MappingContractCandidateAssessment(
            False, ("active mapping plan must be an object",))

    problems: list[str] = []
    project_path = Path(project_root)
    based_on = candidate["based_on"]
    if active_plan.get("contract_version") != based_on["active_contract_version"]:
        problems.append("active mapping contract version does not match based_on")
    if active_plan.get("plan_id") != based_on["active_plan_id"]:
        problems.append("active mapping plan id does not match based_on")
    for ref_key, hash_key in (
        ("active_plan_ref", "active_plan_sha256"),
        ("active_schema_ref", "active_schema_sha256"),
    ):
        path = _resolve_artifact(project_path, {
            "path": based_on[ref_key], "selector": "byte binding"})
        actual = _file_sha256(path) if path is not None else None
        if actual != based_on[hash_key]:
            problems.append(
                f"based_on.{hash_key} mismatch: recorded={based_on[hash_key]!r}, "
                f"actual={actual!r}")

    active_mappings = {
        mapping.get("mapping_id"): mapping
        for mapping in active_plan.get("mappings", [])
        if isinstance(mapping, dict) and isinstance(mapping.get("mapping_id"), str)
    }
    binding_ids = {
        binding.get("plan_id")
        for binding in active_plan.get("product_adoption_bindings", [])
        if isinstance(binding, dict)
    }
    candidate_mappings: dict[str, dict] = {}
    for mapping in candidate["mapping_candidates"]:
        mapping_id = mapping["mapping_id"]
        if mapping_id in candidate_mappings:
            problems.append(f"duplicate mapping candidate {mapping_id}")
        candidate_mappings[mapping_id] = mapping
        if mapping_id in active_mappings:
            problems.append(
                f"mapping candidate {mapping_id} is already present in the active plan")
        if mapping["product_binding_plan_id"] not in binding_ids:
            problems.append(
                f"mapping candidate {mapping_id} has no active product binding "
                f"{mapping['product_binding_plan_id']}")

    known_mapping_ids = set(active_mappings) | set(candidate_mappings)
    seen_dispatch_ids: set[str] = set()
    for dispatch in candidate["dispatch_contracts"]:
        dispatch_id = dispatch["dispatch_id"]
        prefix = dispatch_id + ":"
        if dispatch_id in seen_dispatch_ids:
            problems.append(f"duplicate dispatch contract {dispatch_id}")
        seen_dispatch_ids.add(dispatch_id)
        owner_id = dispatch["owner_mapping_id"]
        owner = candidate_mappings.get(owner_id)
        if owner is None:
            problems.append(f"{prefix} owner must be an unapplied mapping candidate")
            continue
        if owner["record_kind"] != dispatch["record_kind"]:
            problems.append(f"{prefix} owner and dispatch record kinds differ")
        alternatives = dispatch["leaf_alternative_cardinality"]
        if set(alternatives["rule_ids"]) != set(owner["leaf_rule_ids"]):
            problems.append(
                f"{prefix} leaf alternatives must equal the owner leaf rules")

        branch_by_shape: dict[str, dict] = {}
        provider_mapping_ids: set[str] = set()
        for branch in dispatch["semantic_branches"]:
            shape = branch["value_shape"]
            if shape in branch_by_shape:
                problems.append(f"{prefix} duplicate semantic branch for {shape}")
            branch_by_shape[shape] = branch
            required = set(branch["required_facets"])
            if required != _REQUIRED_FACETS:
                problems.append(
                    f"{prefix} {shape} branch must require identity/operator/value")
            counts: Counter[str] = Counter()
            provided_by_mapping: dict[str, set[str]] = {}
            for provider in branch["facet_providers"]:
                mapping_id = provider["mapping_id"]
                provider_mapping_ids.add(mapping_id)
                if mapping_id not in known_mapping_ids:
                    problems.append(
                        f"{prefix} {shape} branch references unknown provider "
                        f"{mapping_id}")
                facets = set(provider["facets"])
                if mapping_id in provided_by_mapping:
                    problems.append(
                        f"{prefix} {shape} branch repeats provider {mapping_id}")
                provided_by_mapping[mapping_id] = facets
                counts.update(facets)
            for facet in sorted(_REQUIRED_FACETS):
                if counts[facet] != 1:
                    problems.append(
                        f"{prefix} {shape} branch has {counts[facet]} providers "
                        f"for {facet}; exactly one is required")
            owner_facets = provided_by_mapping.get(owner_id, set())
            if "identity" not in owner_facets:
                problems.append(
                    f"{prefix} {shape} branch identity must be owned by {owner_id}")
        if set(branch_by_shape) != _REQUIRED_VALUE_SHAPES:
            problems.append(
                f"{prefix} semantic branches must cover scalar and tree exactly once")

        supersessions: dict[str, dict] = {}
        for supersession in dispatch["supersessions"]:
            mapping_id = supersession["mapping_id"]
            if mapping_id in supersessions:
                problems.append(f"{prefix} duplicate supersession {mapping_id}")
            supersessions[mapping_id] = supersession
            if mapping_id not in active_mappings:
                problems.append(
                    f"{prefix} supersession must reference an active mapping: "
                    f"{mapping_id}")
            suppressed = set(supersession["suppressed_authorities"])
            if not {"selection", "identity"} <= suppressed:
                problems.append(
                    f"{prefix} supersession {mapping_id} must suppress selection "
                    "and identity")
        semantic_active_providers = (
            provider_mapping_ids & set(active_mappings)) - {owner_id}
        if semantic_active_providers != set(supersessions):
            problems.append(
                f"{prefix} active semantic providers and supersessions differ: "
                f"providers={sorted(semantic_active_providers)}, "
                f"supersessions={sorted(supersessions)}")
        for shape, branch in branch_by_shape.items():
            for provider in branch["facet_providers"]:
                supersession = supersessions.get(provider["mapping_id"])
                if supersession is None:
                    continue
                conflict = set(provider["facets"]) & set(
                    supersession["suppressed_authorities"])
                if conflict:
                    problems.append(
                        f"{prefix} {shape} provider {provider['mapping_id']} supplies "
                        f"suppressed facets {sorted(conflict)}")

        residual = dispatch["residual_on_mismatch"]
        residual_id = residual["mapping_id"]
        residual_mapping = active_mappings.get(residual_id)
        if residual_mapping is None:
            problems.append(f"{prefix} residual mapping is not active: {residual_id}")
        elif residual_mapping.get("treatment") != "repository_preserved_only":
            problems.append(
                f"{prefix} residual mapping must be repository_preserved_only")
        elif not _mapping_record_kind(residual_mapping, dispatch["record_kind"]):
            problems.append(
                f"{prefix} residual mapping does not preserve the dispatch record kind")

        adapter = dispatch["adapter_dispatch"]
        if adapter["selection_order"] != [owner_id, residual_id]:
            problems.append(
                f"{prefix} selection order must contain only owner then residual")
        if provider_mapping_ids & set(adapter["selection_order"][1:-1]):
            problems.append(
                f"{prefix} semantic providers must not run as independent projections")
        for ref_name, ref in (
            ("owner selector", dispatch["executable_owner_selector_ref"]),
            ("adapter dispatch", adapter["executable_dispatch_ref"]),
        ):
            path = _resolve_artifact(project_path, ref)
            if path is None or not path.is_file():
                problems.append(
                    f"{prefix} {ref_name} artifact does not exist: {ref['path']}")

    return MappingContractCandidateAssessment(not problems, tuple(problems))


def _residual_decision(dispatch: dict, reason_code: str) \
        -> RepositoryProjectionDispatchDecision:
    return RepositoryProjectionDispatchDecision(
        selected_mapping_id=dispatch["residual_on_mismatch"]["mapping_id"],
        state="preserved_entire_record",
        reason_code=reason_code,
        leaves=(),
        suppressed_mapping_ids=(),
    )


def resolve_repository_projection_dispatch_candidate(
    candidate: dict,
    *,
    leaf_rule_ids: list[list[str]] | tuple[tuple[str, ...], ...],
    value_shapes: list[str] | tuple[str, ...],
    independently_matched_mapping_ids: list[str] | tuple[str, ...] = (),
) -> RepositoryProjectionDispatchDecision:
    """Resolve the proposed dispatch without invoking the active adapter.

    Any leaf mismatch preserves the complete record.  A mapping outside the
    declared supersession set is a dual-projection defect and is rejected
    instead of being resolved by incidental call order.
    """
    if len(candidate.get("dispatch_contracts", [])) != 1:
        raise RepositoryProjectionDispatchCandidateError(
            "REPOSITORY_MAPPING_DISPATCH_CONTRACT_CARDINALITY",
            "the isolated candidate must contain exactly one dispatch contract")
    dispatch = candidate["dispatch_contracts"][0]
    if not leaf_rule_ids or len(leaf_rule_ids) != len(value_shapes):
        return _residual_decision(
            dispatch, "REPOSITORY_MAPPING_COMPLETE_RECORD_SHAPE_MISMATCH")

    alternatives = set(
        dispatch["leaf_alternative_cardinality"]["rule_ids"])
    branch_by_shape = {
        branch["value_shape"]: branch
        for branch in dispatch["semantic_branches"]
    }
    leaves: list[LeafSemanticDispatch] = []
    for rules, value_shape in zip(leaf_rule_ids, value_shapes):
        selected = alternatives & set(rules)
        if len(selected) != 1:
            return _residual_decision(
                dispatch, "REPOSITORY_MAPPING_LEAF_ALTERNATIVE_CARDINALITY")
        branch = branch_by_shape.get(value_shape)
        if branch is None:
            return _residual_decision(
                dispatch, "REPOSITORY_MAPPING_VALUE_SHAPE_UNSUPPORTED")
        providers = tuple(
            (provider["mapping_id"], tuple(provider["facets"]))
            for provider in branch["facet_providers"]
        )
        leaves.append(LeafSemanticDispatch(
            rule_id=next(iter(selected)),
            value_shape=value_shape,
            facet_providers=providers,
        ))

    superseded = {
        item["mapping_id"] for item in dispatch["supersessions"]
    }
    independent = set(independently_matched_mapping_ids)
    unexpected = independent - superseded
    if unexpected:
        raise RepositoryProjectionDispatchCandidateError(
            "REPOSITORY_MAPPING_DUAL_PROJECTION_AUTHORITY",
            f"independent projections are not governed: {sorted(unexpected)}")
    return RepositoryProjectionDispatchDecision(
        selected_mapping_id=dispatch["owner_mapping_id"],
        state="selected_once_and_composed",
        reason_code=None,
        leaves=tuple(leaves),
        suppressed_mapping_ids=tuple(sorted(independent)),
    )


__all__ = [
    "CANDIDATE_SCHEMA_PATH",
    "LeafSemanticDispatch",
    "MappingContractCandidateAssessment",
    "REPOSITORY_PROJECTION_MAPPING_CANDIDATE_VERSION",
    "RepositoryProjectionDispatchCandidateError",
    "RepositoryProjectionDispatchDecision",
    "assess_repository_projection_mapping_candidate",
    "resolve_repository_projection_dispatch_candidate",
    "validate_repository_projection_mapping_candidate_schema",
]
