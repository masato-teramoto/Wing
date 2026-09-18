"""Canonical Requirement のヘルパ（hash・finding・pointer）。"""
import hashlib
import json

from . import SCHEMA_VERSION, PROFILE_VERSION
from .lexicon import finding_catalog


def new_canonical(requirement_id: str = "REQ-ADHOC") -> dict:
    return {
        "schema_version": SCHEMA_VERSION,
        "profile_version": PROFILE_VERSION,
        "requirement_id": requirement_id,
        "revision": 1,
        "status": "candidate",
        "source": {"text": ""},
        "rimay_core": {"scope": None, "conditions": [], "response": {}},
        "extensions": {},
        "resolution": {"slots": {}},
        "provenance": [],
        "findings": [],
        "traceability": [],
        # 保証経路の既定はcanonical_api（直接投入）。Normalizer/Extractor/LLM
        # Adapterが各経路で上書きする（ADR-0013 D4）
        "normalization": {"mode": "canonical_api"},
    }


def canonical_hash(canonical: dict) -> str:
    """意味部分の決定論的hash（§14.13の契約: rimay_core+extensions+resolution+版）。"""
    subject = {
        "rimay_core": canonical.get("rimay_core"),
        "extensions": canonical.get("extensions"),
        "resolution": canonical.get("resolution"),
        "schema_version": canonical.get("schema_version"),
        "profile_version": canonical.get("profile_version"),
    }
    blob = json.dumps(subject, sort_keys=True, ensure_ascii=False, separators=(",", ":"))
    return "sha256:" + hashlib.sha256(blob.encode("utf-8")).hexdigest()


def finding(code: str, message: str, path: str | None = None, **evidence) -> dict:
    """finding-code-catalog.yaml をSSOTとしてseverity/blockingを引く。"""
    meta = finding_catalog()[code]
    f = {
        "code": code,
        "severity": meta["severity"],
        "blocking": bool(meta["blocking"]),
        "message": message,
    }
    if path:
        f["path"] = path
    if evidence:
        f["evidence"] = evidence
    return f


def is_blocked(findings: list[dict]) -> bool:
    return any(f["blocking"] for f in findings)


def set_slot(canonical: dict, pointer: str, status: str, source_span: str | None = None,
             method: str = "exact_term_match", confirmation_required: bool = False,
             candidates: list | None = None, reference: str | None = None):
    """リーフスロットの状態とProvenanceを記録する（CanonicalPointer、'*'不可）。

    candidates: 複数候補（§5表現規則6）。[{value, provenance_refs?}] 形式。
    """
    assert "*" not in pointer, "resolution.slots のキーはCanonicalPointer（'*'不可）"
    slot: dict = {"status": status}
    if confirmation_required:
        slot["confirmation_required"] = True
    if reference is not None:
        assert isinstance(reference, str) and reference.strip(), \
            "provenance reference は非空文字列"
    if source_span is not None:
        prv_id = f"PRV-{len(canonical['provenance']) + 1}"
        provenance = {
            "id": prv_id,
            "path": pointer,
            "source_type": "requirement_text",
            "source_span": source_span,
            "resolution_method": method,
        }
        if reference is not None:
            provenance["reference"] = reference
        canonical["provenance"].append(provenance)
        slot["provenance_refs"] = [prv_id]
    if candidates:
        slot["candidates"] = candidates
    canonical["resolution"]["slots"][pointer] = slot
