"""ADR-0017: Capability採用・runtime active・consumer workflow完結の分離契約。"""
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

from .lexicon import ROOT
from .repository_product_adoption import (
    PRODUCT_DISPOSITIONS,
    product_signature,
)


CONSUMER_CLOSURE_CONTRACT_VERSION = "0.1.0"
CONSUMER_REGISTRY_VERSION = "0.1.0"
CONSUMER_CLOSURE_SCHEMA_PATH = (
    ROOT / "canonical" / "capability-consumer-closure.schema.json"
)
CONSUMER_REGISTRY_SCHEMA_PATH = (
    ROOT / "canonical" / "production-consumer-registry.schema.json"
)
CONSUMER_REGISTRY_PATH = ROOT / "profile" / "production-consumers.yaml"
DECISION_LOG_PATH = ROOT / "corpus" / "rimay-conformance" / "decision-log.md"


@dataclass(frozen=True)
class ConsumerClosureAssessment:
    accepted: bool
    workflow_complete: bool
    problems: tuple[str, ...]


def _load_schema(path: Path) -> dict:
    with path.open(encoding="utf-8") as stream:
        return json.load(stream)


@lru_cache(maxsize=1)
def _closure_validator() -> Draft202012Validator:
    schema = _load_schema(CONSUMER_CLOSURE_SCHEMA_PATH)
    Draft202012Validator.check_schema(schema)
    return Draft202012Validator(schema)


@lru_cache(maxsize=1)
def _registry_validator() -> Draft202012Validator:
    schema = _load_schema(CONSUMER_REGISTRY_SCHEMA_PATH)
    Draft202012Validator.check_schema(schema)
    return Draft202012Validator(schema)


def _schema_problems(validator: Draft202012Validator, document: object) -> list[str]:
    errors = sorted(
        validator.iter_errors(document),
        key=lambda error: (
            tuple(str(part) for part in error.absolute_path), error.message),
    )
    return [
        f"{'/'.join(str(part) for part in error.absolute_path) or '<root>'}: "
        f"{error.message}"
        for error in errors
    ]


def validate_consumer_closure_schema(supplement: dict) -> list[str]:
    return _schema_problems(_closure_validator(), supplement)


def validate_production_consumer_registry_schema(registry: dict) -> list[str]:
    return _schema_problems(_registry_validator(), registry)


def _content_signature(document: dict, signature_key: str) -> str:
    unsigned = copy.deepcopy(document)
    unsigned.pop(signature_key, None)
    payload = json.dumps(
        unsigned, ensure_ascii=False, sort_keys=True, separators=(",", ":")
    ).encode("utf-8")
    return "sha256:" + hashlib.sha256(payload).hexdigest()


def consumer_closure_signature(supplement: dict) -> str:
    return _content_signature(supplement, "closure_signature")


def production_consumer_registry_signature(registry: dict) -> str:
    return _content_signature(registry, "registry_signature")


def _artifact_sha256(path: Path) -> str:
    return "sha256:" + hashlib.sha256(path.read_bytes()).hexdigest()


def _resolve_artifact(project_root: Path, relative: str) -> Path | None:
    path = Path(relative)
    if path.is_absolute() or ".." in path.parts:
        return None
    root = project_root.resolve()
    candidate = (root / path).resolve()
    try:
        candidate.relative_to(root)
    except ValueError:
        return None
    return candidate


def _load_yaml(path: Path) -> object:
    return yaml.safe_load(path.read_text(encoding="utf-8"))


def _valid_date(value: object) -> bool:
    if not isinstance(value, str):
        return False
    try:
        return date.fromisoformat(value).isoformat() == value
    except ValueError:
        return False


def _json_pointer(document: object, pointer: str) -> object:
    current = document
    for raw in pointer.split("/")[1:]:
        token = raw.replace("~1", "/").replace("~0", "~")
        if isinstance(current, dict) and token in current:
            current = current[token]
        elif isinstance(current, list) and token.isdigit() and int(token) < len(current):
            current = current[int(token)]
        else:
            raise KeyError(pointer)
    return current


def _artifact_ref_problems(
    ref: dict,
    project_root: Path,
    *,
    owner: str,
) -> list[str]:
    path = _resolve_artifact(project_root, ref["path"])
    if path is None:
        return [f"{owner} artifact escapes project root: {ref['path']!r}"]
    if not path.is_file():
        return [f"{owner} artifact does not exist: {ref['path']}"]
    if _artifact_sha256(path) != ref["sha256"]:
        # Accepted consumer-closure supplements are immutable. A governed
        # successor activation may update an active fixture, so resolve the
        # exact accepted bytes by digest instead of rewriting its signature.
        expected = str(ref.get("sha256") or "")
        digest = expected.removeprefix("sha256:")
        snapshots = sorted((
            project_root / "canonical" / "candidates" / "adopted-evidence"
        ).glob(digest + ".*"))
        if len(snapshots) != 1 or _artifact_sha256(snapshots[0]) != expected:
            return [f"{owner} artifact hash mismatch: {ref['path']}"]
    return []


def _binding_document(
    binding: dict,
    project_root: Path,
    *,
    owner: str,
    problems: list[str],
) -> tuple[Path | None, object | None]:
    path = _resolve_artifact(project_root, binding["path"])
    if path is None:
        problems.append(f"{owner} path escapes project root: {binding['path']!r}")
        return None, None
    if not path.is_file():
        problems.append(f"{owner} does not exist: {binding['path']}")
        return path, None
    if _artifact_sha256(path) != binding["sha256"]:
        problems.append(f"{owner} hash mismatch: {binding['path']}")
    try:
        document = _load_yaml(path)
    except (OSError, yaml.YAMLError) as exc:
        problems.append(f"{owner} cannot be loaded: {exc}")
        return path, None
    return path, document


def _ruling_exists(ruling_ref: str, project_root: Path) -> bool:
    path = project_root / DECISION_LOG_PATH.relative_to(ROOT)
    if not path.is_file():
        return False
    return re.search(
        rf"(?m)^##\s+{re.escape(ruling_ref)}\b",
        path.read_text(encoding="utf-8"),
    ) is not None


def assess_capability_consumer_closure(
    supplement: dict,
    *,
    project_root: Path | str = ROOT,
) -> ConsumerClosureAssessment:
    """Closure supplementを署名済み採用・activation・consumer台帳へ束縛する。"""
    schema_problems = validate_consumer_closure_schema(supplement)
    if schema_problems:
        return ConsumerClosureAssessment(False, False, tuple(schema_problems))

    root = Path(project_root)
    problems: list[str] = []
    if not _valid_date(supplement["recorded_at"]):
        problems.append(f"recorded_at is not a real ISO date: {supplement['recorded_at']!r}")
    if supplement["closure_signature"] != consumer_closure_signature(supplement):
        problems.append("consumer closure signature mismatch")
    if not _ruling_exists(supplement["governance_ruling_ref"], root):
        problems.append(
            f"consumer closure governance ruling is absent: "
            f"{supplement['governance_ruling_ref']}"
        )

    capability_id = supplement["capability_id"]
    product_binding = supplement["product_adoption_binding"]
    _product_path, product = _binding_document(
        product_binding, root, owner="product adoption binding", problems=problems)
    if isinstance(product, dict):
        if product.get("plan_id") != product_binding["plan_id"]:
            problems.append("product adoption plan_id mismatch")
        if product.get("product_signature") != product_signature(product):
            problems.append("bound product adoption signature is invalid")
        if product.get("product_signature") != product_binding["product_signature"]:
            problems.append("product adoption product_signature mismatch")
        decisions = [
            item for item in product.get("decisions", [])
            if isinstance(item, dict)
            and item.get("decision_id") == product_binding["decision_id"]
        ]
        if len(decisions) != 1:
            problems.append("product adoption decision binding must resolve exactly once")
        else:
            decision = decisions[0]
            if decision.get("capability_id") != capability_id:
                problems.append("product adoption capability_id mismatch")
            if decision.get("decision_status") != "accepted" or \
                    decision.get("implementation_disposition") not in PRODUCT_DISPOSITIONS:
                problems.append("consumer closure requires an adopted product decision")

    activation_binding = supplement["runtime_activation_binding"]
    _activation_path, activation = _binding_document(
        activation_binding, root, owner="runtime activation binding", problems=problems)
    if isinstance(activation, dict):
        pointer_values: dict[str, object] = {}
        for key in (
            "capability_pointer",
            "product_signature_pointer",
            "ruling_pointer",
            "runtime_status_pointer",
        ):
            try:
                pointer_values[key] = _json_pointer(activation, activation_binding[key])
            except KeyError:
                problems.append(
                    f"runtime activation pointer does not resolve: {activation_binding[key]}"
                )
        target = pointer_values.get("capability_pointer")
        if target is not None and not (
            target == capability_id or
            isinstance(target, list) and capability_id in target
        ):
            problems.append("runtime activation capability binding mismatch")
        if pointer_values.get("product_signature_pointer") != \
                product_binding["product_signature"]:
            problems.append("runtime activation product signature mismatch")
        if pointer_values.get("ruling_pointer") != activation_binding["ruling_ref"]:
            problems.append("runtime activation ruling mismatch")
        if pointer_values.get("runtime_status_pointer") != "runtime_active":
            problems.append("runtime activation is not runtime_active")

    registry_binding = supplement["consumer_registry_binding"]
    _registry_path, registry = _binding_document(
        registry_binding, root, owner="consumer registry binding", problems=problems)
    registry_by_id: dict[str, dict] = {}
    if isinstance(registry, dict):
        problems.extend(
            f"consumer registry: {problem}"
            for problem in validate_production_consumer_registry_schema(registry)
        )
        if registry.get("registry_signature") != \
                production_consumer_registry_signature(registry):
            problems.append("production consumer registry signature mismatch")
        if registry.get("registry_signature") != registry_binding["registry_signature"]:
            problems.append("consumer registry binding signature mismatch")
        if not _valid_date(registry.get("recorded_at")):
            problems.append("production consumer registry recorded_at is not a real ISO date")
        for item in registry.get("consumers", []):
            consumer_id = item.get("consumer_id") if isinstance(item, dict) else None
            if consumer_id in registry_by_id:
                problems.append(f"duplicate production consumer_id {consumer_id}")
            elif isinstance(consumer_id, str):
                registry_by_id[consumer_id] = item
                path = _resolve_artifact(root, item["path"])
                if path is None or not path.is_file():
                    problems.append(
                        f"production consumer path does not exist: {item['path']}"
                    )

    closure = supplement["consumer_closure"]
    entries = closure["consumers"]
    entry_by_id: dict[str, dict] = {}
    for entry in entries:
        consumer_id = entry["consumer_id"]
        if consumer_id in entry_by_id:
            problems.append(f"duplicate closure consumer_id {consumer_id}")
        entry_by_id[consumer_id] = entry
        registered = registry_by_id.get(consumer_id)
        if registered is None:
            problems.append(f"unregistered consumer in closure: {consumer_id}")
        elif (entry["path"], entry["criticality"]) != (
            registered["path"], registered["criticality"]
        ):
            problems.append(f"consumer registry classification mismatch: {consumer_id}")
        if entry["disposition"] == "implemented_verified" and \
                entry["deferred_shape_ids"]:
            problems.append(
                f"implemented consumer has deferred shapes: {consumer_id}"
            )
        if entry["disposition"] == "fail_closed_deferred" and \
                not entry["deferred_shape_ids"]:
            problems.append(
                f"fail-closed consumer has no deferred shape: {consumer_id}"
            )
        if entry["disposition"] == "not_applicable" and \
                (entry["implemented_shape_ids"] or entry["deferred_shape_ids"]):
            problems.append(
                f"not-applicable consumer cannot claim implemented or deferred shapes: "
                f"{consumer_id}"
            )
        for ref in entry["fixture_refs"]:
            problems.extend(_artifact_ref_problems(
                ref, root, owner=f"consumer {consumer_id}"))

    missing = sorted(set(registry_by_id) - set(entry_by_id))
    if missing:
        problems.append(f"production consumers are unclassified: {missing}")

    composition_ids: set[str] = set()
    compositions = closure["composition_cases"]
    for case in compositions:
        composition_id = case["composition_id"]
        if composition_id in composition_ids:
            problems.append(f"duplicate composition_id {composition_id}")
        composition_ids.add(composition_id)
        unknown_consumers = sorted(set(case["consumer_ids"]) - set(entry_by_id))
        if unknown_consumers:
            problems.append(
                f"composition {composition_id} has unknown consumers: {unknown_consumers}"
            )
        if case["status"] == "fail_closed_deferred" and not case.get(
                "diagnostic_code"):
            problems.append(
                f"deferred composition has no diagnostic_code: {composition_id}"
            )
        for ref in case["fixture_refs"]:
            problems.extend(_artifact_ref_problems(
                ref, root, owner=f"composition {composition_id}"))

    required_entries = [
        entry for entry in entries if entry["criticality"] == "required_workflow"
    ]
    required_cases = [case for case in compositions if case["required_for_workflow"]]
    summary = {
        "required_workflow_total": len(required_entries),
        "required_workflow_implemented": sum(
            entry["disposition"] in {"implemented_verified", "not_applicable"}
            for entry in required_entries
        ),
        "required_workflow_deferred": sum(
            entry["disposition"] == "fail_closed_deferred"
            for entry in required_entries
        ),
        "required_compositions_total": len(required_cases),
        "required_compositions_implemented": sum(
            case["status"] in {"implemented_verified", "not_applicable"}
            for case in required_cases
        ),
        "required_compositions_deferred": sum(
            case["status"] == "fail_closed_deferred"
            for case in required_cases
        ),
    }
    if closure["summary"] != summary:
        problems.append("consumer closure summary differs from classified consumers")
    workflow_complete = (
        summary["required_workflow_deferred"] == 0
        and summary["required_compositions_deferred"] == 0
    )
    expected_workflow = "workflow_complete" if workflow_complete \
        else "workflow_incomplete"
    if supplement["state"]["workflow"] != expected_workflow:
        problems.append(
            f"workflow state mismatch: expected {expected_workflow}"
        )

    return ConsumerClosureAssessment(
        accepted=not problems,
        workflow_complete=workflow_complete and not problems,
        problems=tuple(problems),
    )
