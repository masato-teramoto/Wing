"""Readiness planner for immutable accepted-evidence adapter snapshots.

The planner is read-only.  It identifies accepted product references that
would become stale when the legacy Repository adapter is changed and derives
the digest-named snapshot paths understood by repository_product_adoption.
"""
from __future__ import annotations

import hashlib
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

from .lexicon import ROOT


REPOSITORY_ADAPTER_EVIDENCE_SNAPSHOT_CANDIDATE_VERSION = "0.1.0"
LEGACY_ADAPTER_EVIDENCE_TARGETS = (
    "core/rimay_jp_core/repository_canonical.py",
    "tests/conformance/test_repository_canonical.py",
)
_SNAPSHOT_ROOT = "canonical/candidates/adopted-evidence"


@dataclass(frozen=True)
class AdapterEvidenceSnapshotSpec:
    source_path: str
    expected_sha256: str
    snapshot_path: str
    product_plan_ids: tuple[str, ...]
    decision_ids: tuple[str, ...]
    selectors: tuple[str, ...]
    reference_count: int
    status: str


def _sha256(path: Path) -> str:
    return "sha256:" + hashlib.sha256(path.read_bytes()).hexdigest()


def _quality_refs(plan: dict) -> Iterable[tuple[str, str, str, dict]]:
    plan_id = plan.get("plan_id")
    for decision in plan.get("decisions", []):
        decision_id = decision.get("decision_id")
        quality = decision.get("quality_contract")
        if not isinstance(quality, dict):
            continue
        for axis in quality.values():
            if not isinstance(axis, dict):
                continue
            for ref in axis.get("refs", []):
                if isinstance(ref, dict):
                    yield plan_id, decision_id, str(ref.get("selector") or ""), ref


def adapter_evidence_snapshot_readiness(
    product_plans: Iterable[dict],
    *,
    project_root: Path | str = ROOT,
) -> tuple[tuple[AdapterEvidenceSnapshotSpec, ...], tuple[str, ...]]:
    """Derive exact snapshot specs without writing or changing active evidence."""
    root = Path(project_root)
    references: dict[str, list[tuple[str, str, str, str]]] = {
        target: [] for target in LEGACY_ADAPTER_EVIDENCE_TARGETS}
    for plan in product_plans:
        for plan_id, decision_id, selector, ref in _quality_refs(plan):
            path = ref.get("path")
            if path in references:
                references[path].append(
                    (plan_id, decision_id, selector, str(ref.get("sha256") or "")))

    specs: list[AdapterEvidenceSnapshotSpec] = []
    problems: list[str] = []
    snapshot_root = root / _SNAPSHOT_ROOT
    for target in LEGACY_ADAPTER_EVIDENCE_TARGETS:
        refs = references[target]
        if not refs:
            problems.append(f"{target}: no accepted product evidence reference")
            continue
        expected = {item[3] for item in refs}
        if len(expected) != 1 or not next(iter(expected)).startswith("sha256:"):
            problems.append(f"{target}: accepted references do not share one sha256")
            continue
        expected_sha256 = next(iter(expected))
        source = root / target
        if not source.is_file():
            problems.append(f"{target}: active evidence file is absent")
            continue
        current_sha256 = _sha256(source)
        if current_sha256 != expected_sha256:
            problems.append(
                f"{target}: active evidence hash {current_sha256} != {expected_sha256}")
            continue
        digest = expected_sha256.removeprefix("sha256:")
        snapshot_path = f"{_SNAPSHOT_ROOT}/{digest}.py.txt"
        matches = sorted(snapshot_root.glob(digest + ".*")) \
            if snapshot_root.is_dir() else []
        status = "ready_to_create"
        if matches:
            if len(matches) != 1 or _sha256(matches[0]) != expected_sha256:
                problems.append(f"{target}: digest snapshot collision")
                continue
            status = "already_present"
            snapshot_path = matches[0].relative_to(root).as_posix()
        specs.append(AdapterEvidenceSnapshotSpec(
            source_path=target,
            expected_sha256=expected_sha256,
            snapshot_path=snapshot_path,
            product_plan_ids=tuple(sorted({item[0] for item in refs})),
            decision_ids=tuple(sorted({item[1] for item in refs})),
            selectors=tuple(sorted({item[2] for item in refs})),
            reference_count=len(refs),
            status=status,
        ))
    return tuple(specs), tuple(problems)


def snapshot_payload(
    spec: AdapterEvidenceSnapshotSpec,
    *,
    project_root: Path | str = ROOT,
) -> bytes:
    """Return verified bytes for an explicitly materialized future snapshot."""
    source = Path(project_root) / spec.source_path
    payload = source.read_bytes()
    actual = "sha256:" + hashlib.sha256(payload).hexdigest()
    if actual != spec.expected_sha256:
        raise ValueError(
            f"snapshot source changed: {spec.source_path}: {actual} != "
            f"{spec.expected_sha256}")
    return payload


__all__ = [
    "REPOSITORY_ADAPTER_EVIDENCE_SNAPSHOT_CANDIDATE_VERSION",
    "LEGACY_ADAPTER_EVIDENCE_TARGETS",
    "AdapterEvidenceSnapshotSpec",
    "adapter_evidence_snapshot_readiness",
    "snapshot_payload",
]
