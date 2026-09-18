"""Canonical 1.2 Schema closure migration and lossless rollback contracts.

Canonical 1.2 is an additive audit-field release: it admits the
``versions_used.profile_content_hash`` value already written by approval under
ADR-0013 D3.  It does not infer the hash for historical Canonical documents.
"""
from __future__ import annotations

import copy
import hashlib
import json
from dataclasses import dataclass

from . import SCHEMA_VERSION


SCHEMA_CLOSURE_VERSION = "1.2.0"
SCHEMA_CLOSURE_READER_VERSION = "1.1.0"
SCHEMA_CLOSURE_QUARANTINE_KIND = "RIMAY_JP_SCHEMA_CLOSURE_QUARANTINE"

if SCHEMA_VERSION != SCHEMA_CLOSURE_VERSION:
    raise RuntimeError("active Schema closure and Canonical Schema versions diverged")


@dataclass
class SchemaClosureError(ValueError):
    code: str
    path: str
    message: str

    def __str__(self) -> str:
        return f"{self.code} at {self.path}: {self.message}"


def _stable_sha256(value: object) -> str:
    payload = json.dumps(
        value, ensure_ascii=False, sort_keys=True, separators=(",", ":")
    ).encode("utf-8")
    return "sha256:" + hashlib.sha256(payload).hexdigest()


def migrate_requirement_to_schema_closure(document: dict) -> dict:
    """Migrate a 1.1 document without inventing an historical Profile hash."""
    if document.get("schema_version") != SCHEMA_CLOSURE_READER_VERSION:
        raise SchemaClosureError(
            "SCHEMA_CLOSURE_MIGRATION_VERSION", "/schema_version",
            "migration input must use Canonical 1.1.0",
        )
    migrated = copy.deepcopy(document)
    migrated["schema_version"] = SCHEMA_CLOSURE_VERSION
    migrated.pop("validation_state", None)
    return migrated


def rollback_requirement_from_schema_closure(document: dict) -> dict:
    """Roll back only when no 1.2-only audit value would be discarded."""
    if document.get("schema_version") != SCHEMA_CLOSURE_VERSION:
        raise SchemaClosureError(
            "SCHEMA_CLOSURE_ROLLBACK_VERSION", "/schema_version",
            "rollback input must use Canonical 1.2.0",
        )
    versions_used = document.get("versions_used") or {}
    if "profile_content_hash" in versions_used:
        raise SchemaClosureError(
            "SCHEMA_CLOSURE_ROLLBACK_REQUIRES_QUARANTINE",
            "/versions_used/profile_content_hash",
            "Canonical 1.1 cannot represent the ADR-0013 D3 audit hash",
        )
    rolled_back = copy.deepcopy(document)
    rolled_back["schema_version"] = SCHEMA_CLOSURE_READER_VERSION
    rolled_back.pop("validation_state", None)
    return rolled_back


def quarantine_schema_closure_for_rollback(document: dict) -> dict:
    """Create a 1.1-readable document while preserving the audit hash exactly."""
    if document.get("schema_version") != SCHEMA_CLOSURE_VERSION:
        raise SchemaClosureError(
            "SCHEMA_CLOSURE_QUARANTINE_VERSION", "/schema_version",
            "quarantine input must use Canonical 1.2.0",
        )
    versions_used = document.get("versions_used")
    if not isinstance(versions_used, dict) or \
            "profile_content_hash" not in versions_used:
        raise SchemaClosureError(
            "SCHEMA_CLOSURE_QUARANTINE_NOT_REQUIRED",
            "/versions_used/profile_content_hash",
            "document has no 1.2-only Profile audit hash",
        )
    quarantined = copy.deepcopy(document)
    semantics = quarantined.setdefault("extensions", {}).setdefault(
        "additional_semantics", [])
    if not isinstance(semantics, list) or any(
            isinstance(item, dict) and
            item.get("kind") == SCHEMA_CLOSURE_QUARANTINE_KIND
            for item in semantics):
        raise SchemaClosureError(
            "SCHEMA_CLOSURE_QUARANTINE_CONFLICT",
            "/extensions/additional_semantics",
            "Schema closure quarantine target is invalid or occupied",
        )
    payload = {
        "profile_content_hash": quarantined["versions_used"].pop(
            "profile_content_hash")
    }
    semantics.append({
        "kind": SCHEMA_CLOSURE_QUARANTINE_KIND,
        "canonical_pointer": "/versions_used/profile_content_hash",
        "source_schema_version": SCHEMA_CLOSURE_VERSION,
        "target_schema_version": SCHEMA_CLOSURE_READER_VERSION,
        "payload_sha256": _stable_sha256(payload),
        "payload": payload,
    })
    quarantined["schema_version"] = SCHEMA_CLOSURE_READER_VERSION
    quarantined.pop("validation_state", None)
    return quarantined


def restore_quarantined_schema_closure(document: dict) -> dict:
    """Restore a hash-bound Profile audit value into the active 1.2 shape."""
    if document.get("schema_version") != SCHEMA_CLOSURE_READER_VERSION:
        raise SchemaClosureError(
            "SCHEMA_CLOSURE_RESTORE_VERSION", "/schema_version",
            "restore input must use Canonical 1.1.0",
        )
    restored = copy.deepcopy(document)
    semantics = ((restored.get("extensions") or {}).get(
        "additional_semantics") or [])
    records = [
        item for item in semantics
        if isinstance(item, dict) and
        item.get("kind") == SCHEMA_CLOSURE_QUARANTINE_KIND
    ]
    if len(records) != 1:
        raise SchemaClosureError(
            "SCHEMA_CLOSURE_QUARANTINE_MISSING",
            "/extensions/additional_semantics",
            "exactly one Schema closure quarantine record is required",
        )
    record = records[0]
    required = {
        "kind", "canonical_pointer", "source_schema_version",
        "target_schema_version", "payload_sha256", "payload",
    }
    payload = record.get("payload")
    if set(record) != required or \
            record.get("canonical_pointer") != \
            "/versions_used/profile_content_hash" or \
            record.get("source_schema_version") != SCHEMA_CLOSURE_VERSION or \
            record.get("target_schema_version") != \
            SCHEMA_CLOSURE_READER_VERSION or \
            not isinstance(payload, dict) or \
            set(payload) != {"profile_content_hash"} or \
            _stable_sha256(payload) != record.get("payload_sha256"):
        raise SchemaClosureError(
            "SCHEMA_CLOSURE_QUARANTINE_TAMPERED",
            "/extensions/additional_semantics",
            "Schema closure quarantine envelope or payload hash does not match",
        )
    versions_used = restored.setdefault("versions_used", {})
    if "profile_content_hash" in versions_used:
        raise SchemaClosureError(
            "SCHEMA_CLOSURE_QUARANTINE_COLLISION",
            "/versions_used/profile_content_hash",
            "restored audit hash would overwrite an existing value",
        )
    versions_used["profile_content_hash"] = payload["profile_content_hash"]
    extensions = restored["extensions"]
    extensions["additional_semantics"] = [
        item for item in semantics if item is not record
    ]
    if not extensions["additional_semantics"]:
        extensions.pop("additional_semantics")
    restored["schema_version"] = SCHEMA_CLOSURE_VERSION
    restored.pop("validation_state", None)
    return restored


__all__ = [
    "SCHEMA_CLOSURE_QUARANTINE_KIND", "SCHEMA_CLOSURE_READER_VERSION",
    "SCHEMA_CLOSURE_VERSION", "SchemaClosureError",
    "migrate_requirement_to_schema_closure",
    "quarantine_schema_closure_for_rollback",
    "restore_quarantined_schema_closure",
    "rollback_requirement_from_schema_closure",
]
