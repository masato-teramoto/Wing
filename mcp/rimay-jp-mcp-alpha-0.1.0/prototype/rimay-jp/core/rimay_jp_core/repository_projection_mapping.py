"""Repository固有文書からCanonicalへの写像処遇を統制するB5共通契約。

原典claimはCapability Matrixを、証拠未解決行の製品採否はB5-P planを正本参照する。本moduleは
それらを再分類せず、現在の写像処遇、意味関係、検証強度、必要artifactをfail-closedに検査する。
Repository文書とCanonical RequirementのSchema自体は変更しない。
"""
from __future__ import annotations

import copy
import json
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path

from jsonschema import Draft202012Validator
from jsonschema.exceptions import SchemaError

from .lexicon import ROOT
from .repository_document import REPOSITORY_DOCUMENT_SCHEMA_VERSION
from .repository_product_adoption import (
    ProductDecision,
    assess_repository_product_adoption,
    product_adoption_binding,
)


REPOSITORY_PROJECTION_MAPPING_CONTRACT_VERSION = "0.4.0"
MAPPING_SCHEMA_PATH = ROOT / "canonical" / "repository-projection-mapping.schema.json"
CANONICAL_SCHEMA_PATH = Path("canonical/canonical-requirement.schema.json")
MATRIX_PATH = "reports/compatibility/rimay-capability-matrix.yaml"

_RESOLUTION_STATUSES = frozenset({"decided", "ruling_required"})
_PRODUCT_DISPOSITIONS = frozenset({"implement_product", "rimay_jp_extension"})
_ALL_DISPOSITIONS = _PRODUCT_DISPOSITIONS | {"protocol_absorbed", "product_excluded"}
_PRODUCT_TREATMENTS = frozenset({
    "existing_canonical", "canonical_extension_candidate",
})


@dataclass(frozen=True)
class MappingReadiness:
    mapping_id: str
    state: str


@dataclass(frozen=True)
class ProjectionMappingAssessment:
    accepted: bool
    problems: tuple[str, ...]
    readiness: tuple[MappingReadiness, ...]


@lru_cache(maxsize=1)
def _mapping_validator() -> Draft202012Validator:
    with MAPPING_SCHEMA_PATH.open(encoding="utf-8") as stream:
        schema = json.load(stream)
    Draft202012Validator.check_schema(schema)
    return Draft202012Validator(schema)


def validate_repository_projection_mapping_schema(plan: dict) -> list[str]:
    """B5 mapping planの構造違反を安定したpath付きで返す。"""
    errors = sorted(
        _mapping_validator().iter_errors(plan),
        key=lambda error: (tuple(str(part) for part in error.absolute_path), error.message),
    )
    return [
        f"{'/'.join(str(part) for part in error.absolute_path) or '<root>'}: "
        f"{error.message}"
        for error in errors
    ]


def _matrix_gate_problems(matrix: dict) -> tuple[list[str], bool]:
    problems: list[str] = []
    capabilities = matrix.get("capabilities")
    if not isinstance(capabilities, list):
        return ["capability matrix capabilities must be an array"], False

    counts = {"decided": 0, "ruling_required": 0, "invalid_status": 0}
    evidence_unresolved_decided = 0
    seen: set[str] = set()
    for index, capability in enumerate(capabilities):
        if not isinstance(capability, dict):
            problems.append(f"capability matrix capabilities/{index} must be an object")
            counts["invalid_status"] += 1
            continue
        capability_id = capability.get("capability_id")
        if not isinstance(capability_id, str) or not capability_id:
            problems.append(f"capability matrix capabilities/{index} has no capability_id")
        elif capability_id in seen:
            problems.append(f"capability matrix has duplicate capability_id {capability_id}")
        else:
            seen.add(capability_id)
        classification = capability.get("classification")
        if not isinstance(classification, dict):
            problems.append(f"capability matrix {capability_id or index} has no classification")
            counts["invalid_status"] += 1
            continue
        status = classification.get("resolution_status")
        if status in _RESOLUTION_STATUSES:
            counts[status] += 1
        else:
            counts["invalid_status"] += 1
        if status == "decided":
            evidence = classification.get("evidence_origin")
            if not isinstance(evidence, dict) or any(
                    evidence.get(key) not in {"supported", "not_supported"}
                    for key in ("emse_vor", "official_repository")):
                evidence_unresolved_decided += 1

    derived_ready = (
        counts["ruling_required"] == 0
        and counts["invalid_status"] == 0
        and evidence_unresolved_decided == 0
    )
    recorded = matrix.get("gate_o0b_status")
    if not isinstance(recorded, dict):
        problems.append("capability matrix gate_o0b_status must be an object")
    else:
        expected = {
            **counts,
            "evidence_unresolved_decided": evidence_unresolved_decided,
            "o0b_ready": derived_ready,
        }
        for key, value in expected.items():
            if recorded.get(key) != value:
                problems.append(
                    f"capability matrix gate_o0b_status.{key} mismatch: "
                    f"recorded={recorded.get(key)!r}, derived={value!r}"
                )
    return problems, derived_ready


def _capability_index(matrix: dict) -> dict[str, dict]:
    return {
        capability["capability_id"]: capability
        for capability in matrix.get("capabilities", [])
        if isinstance(capability, dict)
        and isinstance(capability.get("capability_id"), str)
    }


def _grammar_rule_ids(matrix: dict) -> set[str]:
    return {
        element["element_id"].removeprefix("rule:")
        for element in matrix.get("grammar_elements", [])
        if isinstance(element, dict)
        and isinstance(element.get("element_id"), str)
        and element["element_id"].startswith("rule:")
    }


def _matrix_binding_problems(plan: dict, matrix: dict) -> list[str]:
    binding = plan["capability_matrix_binding"]
    expected = {
        "path": MATRIX_PATH,
        "matrix_version": matrix.get("matrix_version"),
        "capability_signature": matrix.get("capability_signature"),
        "classification_signature": matrix.get("classification_signature"),
    }
    return [
        f"capability_matrix_binding.{key} mismatch: "
        f"plan={binding.get(key)!r}, matrix={value!r}"
        for key, value in expected.items()
        if binding.get(key) != value
    ]


def _effective_product_disposition(
    mapping_id: str,
    capability_id: str,
    classification: dict,
    product_decisions: dict[str, ProductDecision],
    problems: list[str],
) -> str | None:
    matrix_disposition = (
        classification.get("implementation_disposition")
        if classification.get("resolution_status") == "decided"
        else None
    )
    decision = product_decisions.get(capability_id)
    if decision is None:
        return matrix_disposition
    if matrix_disposition is not None and \
            decision.implementation_disposition != matrix_disposition:
        problems.append(
            f"{mapping_id}: B5-P decision conflicts with decided Matrix capability "
            f"{capability_id}: product={decision.implementation_disposition!r}, "
            f"matrix={matrix_disposition!r}"
        )
    return decision.implementation_disposition


def _mapping_matrix_problems(
    mapping: dict,
    capabilities: dict[str, dict],
    product_decisions: dict[str, ProductDecision],
) -> list[str]:
    mapping_id = mapping["mapping_id"]
    refs = mapping["capability_refs"]
    capability_ids = [refs["primary"], *refs["supporting"]]
    problems: list[str] = []
    if refs["primary"] in refs["supporting"]:
        problems.append(f"{mapping_id}: primary capability is repeated as supporting")

    classifications: dict[str, dict] = {}
    effective_dispositions: dict[str, str | None] = {}
    for capability_id in capability_ids:
        capability = capabilities.get(capability_id)
        if capability is None:
            problems.append(f"{mapping_id}: unknown capability {capability_id}")
            continue
        classification = capability.get("classification")
        if not isinstance(classification, dict):
            problems.append(f"{mapping_id}: capability {capability_id} has no classification")
            continue
        status = classification.get("resolution_status")
        if status not in _RESOLUTION_STATUSES:
            problems.append(
                f"{mapping_id}: capability {capability_id} has invalid resolution_status "
                f"{status!r}"
            )
        disposition = classification.get("implementation_disposition")
        if status == "decided" and disposition not in _ALL_DISPOSITIONS:
            problems.append(
                f"{mapping_id}: decided capability {capability_id} has invalid "
                f"implementation_disposition {disposition!r}"
            )
        if status == "ruling_required" and disposition is not None:
            problems.append(
                f"{mapping_id}: unresolved capability {capability_id} must not carry "
                "implementation_disposition"
            )
        classifications[capability_id] = classification
        effective_dispositions[capability_id] = _effective_product_disposition(
            mapping_id, capability_id, classification, product_decisions, problems)

    treatment = mapping["treatment"]
    if treatment in _PRODUCT_TREATMENTS:
        for capability_id in capability_ids:
            classification = classifications.get(capability_id)
            if classification is None:
                continue
            disposition = effective_dispositions.get(capability_id)
            if disposition not in _PRODUCT_DISPOSITIONS:
                problems.append(
                    f"{mapping_id}: {treatment} requires an accepted product decision "
                    f"for {capability_id}; effective disposition={disposition!r}"
                )
    elif treatment == "explicitly_excluded":
        primary = classifications.get(refs["primary"])
        if primary is not None and effective_dispositions.get(refs["primary"]) != \
                "product_excluded":
            problems.append(
                f"{mapping_id}: explicitly_excluded requires an accepted "
                "product_excluded primary decision"
            )

    if "repository_compatible" not in mapping["compatibility_modes"]:
        problems.append(
            f"{mapping_id}: a fixed-Repository selector must remain available in "
            "repository_compatible mode"
        )
    if mapping["semantic_relation"] == "extended" and \
            "rimay_jp_enhanced" not in mapping["compatibility_modes"]:
        problems.append(
            f"{mapping_id}: extended semantics require rimay_jp_enhanced mode"
        )
    return problems


def _artifact_refs(mapping: dict):
    evidence = mapping["evidence"]
    for group in ("implementation_refs", "validator_refs"):
        yield from evidence[group]
    for group in ("positive", "negative", "boundary", "ambiguity"):
        yield from evidence["fixture_refs"][group]
    extension = mapping.get("extension_bundle")
    if extension is not None:
        for key in ("schema_ref", "migration_ref", "store_replay_ref", "rollback_ref"):
            yield extension[key]
    for selector in mapping["repository_selectors"]:
        predicate = selector.get("structural_predicate")
        if predicate is not None:
            yield predicate["executable_selector_ref"]


def _resolve_artifact(project_root: Path, ref: dict) -> Path | None:
    relative = Path(ref["path"])
    if relative.is_absolute() or ".." in relative.parts:
        return None
    root = project_root.resolve()
    candidate = (root / relative).resolve()
    try:
        candidate.relative_to(root)
    except ValueError:
        return None
    return candidate


def _artifact_problems(mapping: dict, project_root: Path) -> list[str]:
    problems: list[str] = []
    for ref in _artifact_refs(mapping):
        path = _resolve_artifact(project_root, ref)
        if path is None:
            problems.append(
                f"{mapping['mapping_id']}: artifact path escapes project root: "
                f"{ref['path']!r}"
            )
        elif not path.is_file():
            problems.append(
                f"{mapping['mapping_id']}: artifact does not exist: {ref['path']}"
            )
    return problems


def _structural_predicate_problems(mapping: dict, mappings_by_id: dict[str, dict]) -> list[str]:
    """Validate selector overlap as an explicit, fail-closed residual contract."""
    problems: list[str] = []
    mapping_id = mapping["mapping_id"]
    for selector_index, selector in enumerate(mapping["repository_selectors"]):
        predicate = selector.get("structural_predicate")
        if predicate is None:
            continue
        prefix = f"{mapping_id}: repository selector {selector_index}"
        if mapping["treatment"] not in _PRODUCT_TREATMENTS:
            problems.append(
                f"{prefix}: structural predicate requires a product mapping treatment")
        unknown_cardinality_rules = sorted(
            set(predicate["exact_rule_cardinality"]) - set(selector["rule_ids"]))
        if unknown_cardinality_rules:
            problems.append(
                f"{prefix}: exact cardinality rules are absent from rule_ids: "
                f"{unknown_cardinality_rules}")
        residual_id = predicate["residual_on_mismatch"]["mapping_id"]
        residual = mappings_by_id.get(residual_id)
        if residual is None:
            problems.append(f"{prefix}: unknown residual mapping {residual_id}")
        elif residual_id == mapping_id:
            problems.append(f"{prefix}: residual mapping must differ from the active mapping")
        elif residual["treatment"] != "repository_preserved_only":
            problems.append(
                f"{prefix}: residual mapping {residual_id} must be repository_preserved_only")
        elif not any(
                candidate["record_kind"] == selector["record_kind"]
                for candidate in residual["repository_selectors"]):
            problems.append(
                f"{prefix}: residual mapping {residual_id} does not preserve record kind "
                f"{selector['record_kind']}")
    return problems


def _pointer_tokens(pointer: str) -> list[str]:
    return [token.replace("~1", "/").replace("~0", "~")
            for token in pointer[1:].split("/")]


def _local_ref(schema: dict, ref: str) -> dict | None:
    if not ref.startswith("#/"):
        return None
    current: object = schema
    for token in _pointer_tokens(ref[1:]):
        if not isinstance(current, dict) or token not in current:
            return None
        current = current[token]
    return current if isinstance(current, dict) else None


def _canonical_pointer_exists(schema: dict, pointer: str) -> bool:
    current: dict | None = schema
    for token in _pointer_tokens(pointer):
        seen_refs: set[str] = set()
        while isinstance(current, dict) and "$ref" in current:
            ref = current["$ref"]
            if not isinstance(ref, str) or ref in seen_refs:
                return False
            seen_refs.add(ref)
            current = _local_ref(schema, ref)
        if not isinstance(current, dict):
            return False
        properties = current.get("properties")
        if isinstance(properties, dict) and token in properties:
            current = properties[token]
            continue
        if current.get("type") == "array" and token.isdigit() and \
                isinstance(current.get("items"), dict):
            current = current["items"]
            continue
        return False
    return True


def _load_json(path: Path) -> tuple[dict | None, str | None]:
    try:
        with path.open(encoding="utf-8") as stream:
            value = json.load(stream)
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        return None, f"{type(exc).__name__}: {exc}"
    if not isinstance(value, dict):
        return None, "root is not an object"
    return value, None


def _schema_version(schema: dict) -> str | None:
    properties = schema.get("properties")
    if not isinstance(properties, dict):
        return None
    version = properties.get("schema_version")
    return version.get("const") if isinstance(version, dict) else None


def _semver_tuple(value: str) -> tuple[int, int, int]:
    return tuple(int(part) for part in value.split("."))


def _schema_structure(schema: dict) -> dict:
    """Ignore editorial top-level text when comparing an adopted candidate."""
    comparable = copy.deepcopy(schema)
    comparable.pop("description", None)
    return comparable


def _canonical_target_problems(mapping: dict, project_root: Path) -> list[str]:
    treatment = mapping["treatment"]
    if treatment not in _PRODUCT_TREATMENTS:
        return []
    current_path = project_root / CANONICAL_SCHEMA_PATH
    current_schema, error = _load_json(current_path)
    if error is not None:
        return [
            f"{mapping['mapping_id']}: cannot load current Canonical Schema "
            f"{CANONICAL_SCHEMA_PATH}: {error}"
        ]
    try:
        Draft202012Validator.check_schema(current_schema)
    except SchemaError as exc:
        return [f"{mapping['mapping_id']}: current Canonical Schema is invalid: {exc.message}"]

    target_schema = current_schema
    problems: list[str] = []
    if treatment == "canonical_extension_candidate":
        extension = mapping["extension_bundle"]
        schema_path = _resolve_artifact(project_root, extension["schema_ref"])
        if schema_path is None or not schema_path.is_file():
            return problems  # artifact検査が同じ欠落を報告する
        target_schema, error = _load_json(schema_path)
        if error is not None:
            return [
                f"{mapping['mapping_id']}: cannot load extension Schema "
                f"{extension['schema_ref']['path']}: {error}"
            ]
        try:
            Draft202012Validator.check_schema(target_schema)
        except SchemaError as exc:
            problems.append(
                f"{mapping['mapping_id']}: extension Schema is invalid: {exc.message}"
            )
        target_version = extension["target_schema_version"]
        actual_version = _schema_version(target_schema)
        current_version = _schema_version(current_schema)
        if actual_version != target_version:
            problems.append(
                f"{mapping['mapping_id']}: extension Schema version mismatch: "
                f"bundle={target_version!r}, schema={actual_version!r}"
            )
        if current_version is None or _semver_tuple(target_version) < \
                _semver_tuple(current_version):
            problems.append(
                f"{mapping['mapping_id']}: extension target version {target_version} "
                f"must not be older than current {current_version!r}"
            )
        elif target_version == current_version and \
                _schema_structure(target_schema) != _schema_structure(current_schema):
            problems.append(
                f"{mapping['mapping_id']}: extension target {target_version} matches "
                "the active version but its Schema structure has drifted"
            )

    for pointer in mapping["canonical_targets"]:
        if not _canonical_pointer_exists(target_schema, pointer):
            problems.append(
                f"{mapping['mapping_id']}: Canonical target is absent from the "
                f"applicable Schema: {pointer}"
            )
    return problems


def assess_repository_projection_mapping(
    plan: dict,
    capability_matrix: dict,
    *,
    project_root: Path | str = ROOT,
    product_adoption_plans: list[dict] | tuple[dict, ...] | None = None,
) -> ProjectionMappingAssessment:
    """Schema・原典claim Matrix・B5-P製品裁定・artifactを一括検査する。

    ``capability_matrix`` は ``check_capability_matrix.py`` 適合済みの文書を入力前提とするが、
    本境界でも参照署名とGate集計を独立に検査する。Global O0-Bは原典claim里程標であり、
    製品写像の着手条件には使わない。証拠未解決行の採否はB5-P planだけから消費する。
    """
    schema_problems = validate_repository_projection_mapping_schema(plan)
    if schema_problems:
        return ProjectionMappingAssessment(False, tuple(schema_problems), ())
    if not isinstance(capability_matrix, dict):
        return ProjectionMappingAssessment(
            False, ("capability matrix must be an object",), ())

    problems: list[str] = []
    product_decisions: dict[str, ProductDecision] = {}
    if plan["contract_version"] != REPOSITORY_PROJECTION_MAPPING_CONTRACT_VERSION:
        problems.append("repository projection mapping contract version mismatch")
    if plan["repository_document_schema_version"] != REPOSITORY_DOCUMENT_SCHEMA_VERSION:
        problems.append(
            "repository document schema version mismatch: "
            f"plan={plan['repository_document_schema_version']!r}, "
            f"runtime={REPOSITORY_DOCUMENT_SCHEMA_VERSION!r}"
        )
    problems.extend(_matrix_binding_problems(plan, capability_matrix))
    gate_problems, _o0b_ready = _matrix_gate_problems(capability_matrix)
    problems.extend(gate_problems)
    bindings = plan.get("product_adoption_bindings", [])
    adoption_plans = list(product_adoption_plans or [])
    if bool(bindings) != bool(adoption_plans):
        problems.append(
            "product_adoption_bindings and product_adoption_plans must be supplied together"
        )
    else:
        binding_by_id: dict[str, dict] = {}
        for binding in bindings:
            plan_id = binding["plan_id"]
            if plan_id in binding_by_id:
                problems.append(f"duplicate product adoption binding plan_id {plan_id}")
            binding_by_id[plan_id] = binding

        adoption_by_id: dict[str, dict] = {}
        for adoption_plan in adoption_plans:
            plan_id = adoption_plan.get("plan_id") if isinstance(adoption_plan, dict) else None
            if not isinstance(plan_id, str):
                problems.append("product adoption plan has no plan_id")
                continue
            if plan_id in adoption_by_id:
                problems.append(f"duplicate product adoption plan_id {plan_id}")
            adoption_by_id[plan_id] = adoption_plan

        missing_documents = sorted(set(binding_by_id) - set(adoption_by_id))
        unbound_documents = sorted(set(adoption_by_id) - set(binding_by_id))
        if missing_documents:
            problems.append(
                f"product adoption bindings have no documents: {missing_documents}"
            )
        if unbound_documents:
            problems.append(
                f"product adoption documents have no bindings: {unbound_documents}"
            )

        decision_owner: dict[str, str] = {}
        for plan_id in sorted(set(binding_by_id) & set(adoption_by_id)):
            adoption_plan = adoption_by_id[plan_id]
            product_assessment = assess_repository_product_adoption(
                adoption_plan, capability_matrix, project_root=project_root)
            if not product_assessment.accepted:
                problems.extend(
                    f"product adoption {plan_id}: {problem}"
                    for problem in product_assessment.problems)
                continue
            expected_binding = product_adoption_binding(adoption_plan)
            binding = binding_by_id[plan_id]
            for key, value in expected_binding.items():
                if binding.get(key) != value:
                    problems.append(
                        f"product_adoption_bindings[{plan_id}].{key} mismatch: "
                        f"plan={binding.get(key)!r}, product={value!r}"
                    )
            for capability_id, decision in \
                    product_assessment.accepted_decisions().items():
                if capability_id in product_decisions:
                    problems.append(
                        f"duplicate accepted product decision for capability "
                        f"{capability_id}: plans={decision_owner[capability_id]!r}, "
                        f"{plan_id!r}"
                    )
                    continue
                product_decisions[capability_id] = decision
                decision_owner[capability_id] = plan_id
    capabilities = _capability_index(capability_matrix)
    grammar_rule_ids = _grammar_rule_ids(capability_matrix)
    if not grammar_rule_ids:
        problems.append("capability matrix has no parser-rule inventory")
    project_path = Path(project_root)

    mapping_ids: set[str] = set()
    mappings_by_id = {
        mapping["mapping_id"]: mapping for mapping in plan["mappings"]
    }
    for mapping in plan["mappings"]:
        mapping_id = mapping["mapping_id"]
        if mapping_id in mapping_ids:
            problems.append(f"duplicate mapping_id {mapping_id}")
        mapping_ids.add(mapping_id)
        selector_keys: set[tuple[str, tuple[str, ...]]] = set()
        for selector in mapping["repository_selectors"]:
            key = (selector["record_kind"], tuple(selector["rule_ids"]))
            if key in selector_keys:
                problems.append(f"{mapping_id}: duplicate repository selector {key!r}")
            selector_keys.add(key)
            for rule_id in selector["rule_ids"]:
                if rule_id not in grammar_rule_ids:
                    problems.append(
                        f"{mapping_id}: Repository rule is absent from the bound "
                        f"Capability Matrix inventory: {rule_id}"
                    )
        problems.extend(_mapping_matrix_problems(mapping, capabilities, product_decisions))
        problems.extend(_artifact_problems(mapping, project_path))
        problems.extend(_canonical_target_problems(mapping, project_path))
        problems.extend(_structural_predicate_problems(mapping, mappings_by_id))

    if problems:
        return ProjectionMappingAssessment(False, tuple(problems), ())

    readiness = []
    states = {
        "existing_canonical": "active",
        "repository_preserved_only": "preserved_only",
        "explicitly_excluded": "not_adopted",
    }
    for mapping in plan["mappings"]:
        treatment = mapping["treatment"]
        state = (
            "eligible_for_schema_evolution"
            if treatment == "canonical_extension_candidate"
            else states[treatment]
        )
        readiness.append(MappingReadiness(mapping["mapping_id"], state))
    return ProjectionMappingAssessment(True, (), tuple(readiness))
