"""B5-P: 原典claimと独立したRepository Capabilityの製品品質・採否契約。"""
from __future__ import annotations

import copy
import hashlib
import json
import re
from dataclasses import dataclass
from datetime import date
from functools import lru_cache
from pathlib import Path

import yaml
from jsonschema import Draft202012Validator
from jsonschema.exceptions import SchemaError

from .lexicon import ROOT


REPOSITORY_PRODUCT_ADOPTION_CONTRACT_VERSION = "0.3.0"
SUPPORTED_REPOSITORY_PRODUCT_ADOPTION_CONTRACT_VERSIONS = frozenset({
    "0.2.0", "0.3.0",
})
PRODUCT_ADOPTION_SCHEMA_PATH = ROOT / "canonical" / "repository-product-adoption.schema.json"
PRODUCTION_CONSUMER_REGISTRY_PATH = "profile/production-consumers.yaml"
MATRIX_PATH = "reports/compatibility/rimay-capability-matrix.yaml"
DECISION_LOG_PATH = Path("corpus/rimay-conformance/decision-log.md")
PRODUCT_DISPOSITIONS = frozenset({"implement_product", "rimay_jp_extension"})
EXCLUSION_DISPOSITIONS = frozenset({"protocol_absorbed", "product_excluded"})
_QUALITY_AXES = (
    "user_value",
    "information_preservation",
    "ambiguity_control",
    "structured_diagnostic",
    "semantic_roundtrip",
    "migration_safety",
    "japanese_parity_impact",
)
_EXPECTED_CLAIM_BOUNDARY = {
    "decides_paper_conformance": False,
    "requires_paper_evidence_resolution": False,
    "withholds_paper_claim_when_evidence_unresolved": True,
}


@dataclass(frozen=True)
class ProductDecision:
    decision_id: str
    capability_id: str
    decision_status: str
    implementation_disposition: str
    decision_ruling_ref: str

    @property
    def product_state(self) -> str:
        if self.decision_status != "accepted":
            return "incubating" if self.decision_status == "proposed" else "rejected"
        return (
            "adopted" if self.implementation_disposition in PRODUCT_DISPOSITIONS
            else "excluded"
        )


@dataclass(frozen=True)
class ProductAdoptionAssessment:
    accepted: bool
    problems: tuple[str, ...]
    decisions: tuple[ProductDecision, ...]

    def accepted_decisions(self) -> dict[str, ProductDecision]:
        return {
            decision.capability_id: decision
            for decision in self.decisions
            if decision.decision_status == "accepted"
        }


@lru_cache(maxsize=1)
def _validator() -> Draft202012Validator:
    with PRODUCT_ADOPTION_SCHEMA_PATH.open(encoding="utf-8") as stream:
        schema = json.load(stream)
    Draft202012Validator.check_schema(schema)
    return Draft202012Validator(schema)


def validate_repository_product_adoption_schema(plan: dict) -> list[str]:
    """B5-P planの閉じたSchema違反を安定したpath付きで返す。"""
    errors = sorted(
        _validator().iter_errors(plan),
        key=lambda error: (tuple(str(part) for part in error.absolute_path), error.message),
    )
    return [
        f"{'/'.join(str(part) for part in error.absolute_path) or '<root>'}: "
        f"{error.message}"
        for error in errors
    ]


def product_signature(plan: dict) -> str:
    """製品判断と品質参照を固定する署名。証拠分類は入力にも署名対象にも含めない。"""
    unsigned = copy.deepcopy(plan)
    unsigned.pop("product_signature", None)
    payload = json.dumps(
        unsigned, sort_keys=True, separators=(",", ":"), ensure_ascii=False
    ).encode("utf-8")
    return "sha256:" + hashlib.sha256(payload).hexdigest()


def product_adoption_binding(plan: dict) -> dict:
    """Repository projection planが参照する最小binding。"""
    return {
        "contract_version": plan.get("contract_version"),
        "plan_id": plan.get("plan_id"),
        "capability_signature": (
            plan.get("capability_matrix_binding") or {}
        ).get("capability_signature"),
        "product_signature": plan.get("product_signature"),
    }


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


def _artifact_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(65536), b""):
            digest.update(chunk)
    return "sha256:" + digest.hexdigest()


def _document_signature(document: dict, signature_key: str) -> str:
    unsigned = copy.deepcopy(document)
    unsigned.pop(signature_key, None)
    payload = json.dumps(
        unsigned, sort_keys=True, separators=(",", ":"), ensure_ascii=False
    ).encode("utf-8")
    return "sha256:" + hashlib.sha256(payload).hexdigest()


def _superseded_active_schema_matches(project_root: Path, ref: dict) -> bool:
    """Resolve a hash-bound active-Schema ref after a governed major activation.

    Accepted product decisions are immutable. When their evidence named the
    then-active Canonical Schema, a later major activation keeps that exact
    artifact under ``canonical/candidates/canonical-requirement-pre-*`` rather
    than rewriting the accepted plan or its signature.
    """
    if ref.get("path") != "canonical/canonical-requirement.schema.json":
        return False
    match = re.search(r"active\s+(\d+\.\d+)", str(ref.get("selector") or ""))
    if match is None:
        return False
    version = match.group(1) + ".0"
    candidates = sorted((project_root / "canonical" / "candidates").glob(
        f"canonical-requirement-pre-*-{version}.schema.json"))
    return len(candidates) == 1 and _artifact_sha256(candidates[0]) == ref["sha256"]


def _adopted_evidence_snapshot_matches(project_root: Path, ref: dict) -> bool:
    """Resolve an immutable accepted-decision artifact by its original digest."""
    expected = str(ref.get("sha256") or "")
    if not expected.startswith("sha256:"):
        return False
    digest = expected.removeprefix("sha256:")
    snapshots = sorted((
        project_root / "canonical" / "candidates" / "adopted-evidence"
    ).glob(digest + ".*"))
    return len(snapshots) == 1 and _artifact_sha256(snapshots[0]) == expected


def _ruling_section_sha256(section: str) -> str:
    normalized = section.rstrip().encode("utf-8")
    return "sha256:" + hashlib.sha256(normalized).hexdigest()


def _decision_log_sections(project_root: Path) -> dict[str, str] | None:
    path = project_root / DECISION_LOG_PATH
    if not path.is_file():
        return None
    text = path.read_text(encoding="utf-8")
    matches = list(re.finditer(r"(?m)^##\s+(RC-[0-9]{3})\b", text))
    return {
        match.group(1): text[match.start():matches[index + 1].start()]
        if index + 1 < len(matches) else text[match.start():]
        for index, match in enumerate(matches)
    }


def _valid_date(value: object) -> bool:
    if not isinstance(value, str):
        return False
    try:
        return date.fromisoformat(value).isoformat() == value
    except ValueError:
        return False


def _consumer_impact_problems(
    item: dict,
    *,
    project_root: Path,
) -> list[str]:
    """B5-P 0.3 consumer影響目録を現行production consumer台帳へ束縛する。"""
    decision_id = item["decision_id"]
    impact = item["consumer_impact"]
    problems: list[str] = []
    if impact["capability_id"] != item["capability_id"]:
        problems.append(
            f"product decision {decision_id} consumer impact capability mismatch"
        )

    shape_ids = [shape["shape_id"] for shape in impact["canonical_shapes"]]
    if len(shape_ids) != len(set(shape_ids)):
        problems.append(f"product decision {decision_id} has duplicate consumer shape_id")
    composition_ids = [
        composition["composition_id"] for composition in impact["compositions"]
    ]
    if len(composition_ids) != len(set(composition_ids)):
        problems.append(
            f"product decision {decision_id} has duplicate consumer composition_id"
        )
    for composition in impact["compositions"]:
        unknown = sorted(set(composition["shape_ids"]) - set(shape_ids))
        if unknown:
            problems.append(
                f"product decision {decision_id} composition "
                f"{composition['composition_id']} has unknown shapes: {unknown}"
            )

    binding = impact["registry_binding"]
    if binding["path"] != PRODUCTION_CONSUMER_REGISTRY_PATH:
        problems.append(
            f"product decision {decision_id} consumer registry path mismatch"
        )
        registry = None
    else:
        registry_path = _resolve_artifact(project_root, binding)
        if registry_path is None or not registry_path.is_file():
            problems.append(
                f"product decision {decision_id} consumer registry is unavailable"
            )
            registry = None
        elif _artifact_sha256(registry_path) != binding["sha256"]:
            problems.append(
                f"product decision {decision_id} consumer registry hash mismatch"
            )
            registry = None
        else:
            try:
                registry = yaml.safe_load(registry_path.read_text(encoding="utf-8"))
            except (OSError, yaml.YAMLError):
                registry = None
                problems.append(
                    f"product decision {decision_id} consumer registry cannot be loaded"
                )

    registered: dict[str, dict] = {}
    if isinstance(registry, dict):
        if registry.get("registry_version") != "0.1.0" or \
                registry.get("registry_signature") != _document_signature(
                    registry, "registry_signature"):
            problems.append(
                f"product decision {decision_id} consumer registry signature mismatch"
            )
        for consumer in registry.get("consumers", []):
            consumer_id = consumer.get("consumer_id") if isinstance(consumer, dict) else None
            if not isinstance(consumer_id, str) or consumer_id in registered:
                problems.append(
                    f"product decision {decision_id} consumer registry has duplicate or "
                    "invalid consumer_id"
                )
                continue
            registered[consumer_id] = consumer

    classified: dict[str, dict] = {}
    for consumer in impact["consumers"]:
        consumer_id = consumer["consumer_id"]
        if consumer_id in classified:
            problems.append(
                f"product decision {decision_id} has duplicate consumer {consumer_id}"
            )
        classified[consumer_id] = consumer
        registry_item = registered.get(consumer_id)
        if registry_item is None:
            problems.append(
                f"product decision {decision_id} has unregistered consumer {consumer_id}"
            )
        elif (consumer["path"], consumer["criticality"]) != (
            registry_item.get("path"), registry_item.get("criticality")
        ):
            problems.append(
                f"product decision {decision_id} consumer classification mismatch: "
                f"{consumer_id}"
            )
        for ref in consumer["refs"]:
            path = _resolve_artifact(project_root, ref)
            if path is None:
                problems.append(
                    f"product decision {decision_id} consumer artifact escapes project "
                    f"root: {ref['path']!r}"
                )
            elif not path.is_file():
                problems.append(
                    f"product decision {decision_id} consumer artifact does not exist: "
                    f"{ref['path']}"
                )
            elif _artifact_sha256(path) != ref["sha256"] and not \
                    _adopted_evidence_snapshot_matches(project_root, ref):
                problems.append(
                    f"product decision {decision_id} consumer artifact hash mismatch: "
                    f"{ref['path']}"
                )

    missing = sorted(set(registered) - set(classified))
    if missing:
        problems.append(
            f"product decision {decision_id} production consumers are unclassified: "
            f"{missing}"
        )
    if item["decision_status"] == "accepted" and impact["satisfied"] is not True:
        problems.append(
            f"product decision {decision_id} accepted with unsatisfied consumer impact"
        )
    return problems


def assess_repository_product_adoption(
    plan: dict,
    capability_matrix: dict,
    *,
    project_root: Path | str = ROOT,
) -> ProductAdoptionAssessment:
    """製品判断をMatrix grouping・RC・品質artifactへ束縛する。

    Matrixの ``classification_signature`` と ``evidence_origin`` は意図的に参照しない。
    原典証拠が未解決でも製品判断を記録できるが、claim boundaryにより論文準拠主張は発生しない。
    """
    schema_problems = validate_repository_product_adoption_schema(plan)
    if schema_problems:
        return ProductAdoptionAssessment(False, tuple(schema_problems), ())
    if not isinstance(capability_matrix, dict):
        return ProductAdoptionAssessment(False, ("capability matrix must be an object",), ())

    project_path = Path(project_root)
    problems: list[str] = []
    if plan["contract_version"] not in \
            SUPPORTED_REPOSITORY_PRODUCT_ADOPTION_CONTRACT_VERSIONS:
        problems.append("repository product adoption contract version mismatch")
    if not _valid_date(plan["recorded_at"]):
        problems.append(f"recorded_at is not a real ISO date: {plan['recorded_at']!r}")
    binding = plan["capability_matrix_binding"]
    if binding["path"] != MATRIX_PATH:
        problems.append("capability matrix path mismatch")
    if binding["capability_signature"] != capability_matrix.get("capability_signature"):
        problems.append("capability grouping signature mismatch")
    if plan["claim_boundary"] != _EXPECTED_CLAIM_BOUNDARY:
        problems.append("paper-conformance claim boundary mismatch")
    if plan["product_signature"] != product_signature(plan):
        problems.append("product signature mismatch")

    capabilities = {
        item.get("capability_id")
        for item in capability_matrix.get("capabilities", [])
        if isinstance(item, dict) and isinstance(item.get("capability_id"), str)
    }
    ruling_sections = _decision_log_sections(project_path)
    decision_ids: set[str] = set()
    capability_ids: set[str] = set()
    decisions: list[ProductDecision] = []
    for index, item in enumerate(plan["decisions"]):
        decision_id = item["decision_id"]
        capability_id = item["capability_id"]
        if decision_id in decision_ids:
            problems.append(f"duplicate product decision_id {decision_id}")
        decision_ids.add(decision_id)
        if capability_id in capability_ids:
            problems.append(f"duplicate product decision for capability {capability_id}")
        capability_ids.add(capability_id)
        if capability_id not in capabilities:
            problems.append(f"unknown capability in product decision: {capability_id}")

        ruling_ref = item["decision_ruling_ref"]
        if ruling_sections is None:
            problems.append("product decision log is unavailable")
        elif ruling_ref not in ruling_sections:
            problems.append(
                f"product decision {decision_id} refers to absent ruling {ruling_ref}"
            )
        else:
            section = ruling_sections[ruling_ref]
            expected_binding = (
                f"B5-P binding: decision_id={decision_id}; "
                f"capability_id={capability_id}; "
                f"decision_status={item['decision_status']}; "
                f"implementation_disposition={item['implementation_disposition']}"
            )
            binding_lines = []
            for line in section.splitlines():
                normalized = line.strip()
                if normalized.startswith("- "):
                    normalized = normalized[2:].strip()
                if normalized.startswith("B5-P binding:"):
                    binding_lines.append(normalized)
            if binding_lines != [expected_binding]:
                problems.append(
                    f"product decision {decision_id} ruling {ruling_ref} is not bound to "
                    "the exact decision content and status"
                )
            if _ruling_section_sha256(section) != item["decision_ruling_sha256"]:
                problems.append(
                    f"product decision {decision_id} ruling section hash mismatch: "
                    f"{ruling_ref}"
                )

        quality = item["quality_contract"]
        for axis in _QUALITY_AXES:
            axis_contract = quality[axis]
            if item["decision_status"] == "accepted" and \
                    axis_contract["status"] != "satisfied":
                problems.append(
                    f"product decision {decision_id} accepted with unsatisfied "
                    f"quality axis {axis}: {axis_contract['status']}"
                )
            for ref in axis_contract["refs"]:
                path = _resolve_artifact(project_path, ref)
                if path is None:
                    problems.append(
                        f"product decision {decision_id} artifact escapes project root: "
                        f"{ref['path']!r}"
                    )
                elif not path.is_file():
                    problems.append(
                        f"product decision {decision_id} artifact does not exist: "
                        f"{ref['path']}"
                    )
                elif _artifact_sha256(path) != ref["sha256"] and not \
                        _superseded_active_schema_matches(project_path, ref) and not \
                        _adopted_evidence_snapshot_matches(project_path, ref):
                    problems.append(
                        f"product decision {decision_id} artifact hash mismatch: "
                        f"{ref['path']}"
                    )

        if plan["contract_version"] == REPOSITORY_PRODUCT_ADOPTION_CONTRACT_VERSION:
            problems.extend(_consumer_impact_problems(
                item, project_root=project_path))

        decisions.append(ProductDecision(
            decision_id=decision_id,
            capability_id=capability_id,
            decision_status=item["decision_status"],
            implementation_disposition=item["implementation_disposition"],
            decision_ruling_ref=ruling_ref,
        ))

    if problems:
        return ProductAdoptionAssessment(False, tuple(problems), ())
    return ProductAdoptionAssessment(True, (), tuple(decisions))
