"""案件語彙と組織共通語彙の固定コンテキスト（ADR-0016）。

クライアントは ``project_id`` だけを渡す。物理パスはサーバー側レジストリが
固定レイアウトから解決し、操作開始時に両SnapshotのID・hashをpinする。
"""
from __future__ import annotations

from contextlib import contextmanager
from contextvars import ContextVar
from dataclasses import dataclass
from functools import lru_cache
import hashlib
import json
from pathlib import Path
import re
from urllib.parse import quote, unquote

import yaml


CONTEXT_VERSION = "1.0.0"
REGISTRY_VERSION = "1.0.0"
MANIFEST_VERSION = "1.0.0"
_PROJECT_ID = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]*$")
_QUALIFIED_PREFIX = "rimay-term:v1:"


def qualified_term_id(scope: str, term_id: str) -> str:
    """``(scope, id)`` を損失なく受け渡す版付き表現。"""
    if not scope or not term_id:
        raise ValueError("qualified term ID requires non-empty scope and id")
    return f"{_QUALIFIED_PREFIX}{quote(scope, safe='')}:{quote(term_id, safe='')}"


def split_qualified_term_id(value: str) -> tuple[str, str]:
    if not value.startswith(_QUALIFIED_PREFIX):
        raise ValueError(f"unsupported qualified term ID: {value}")
    encoded = value[len(_QUALIFIED_PREFIX):]
    try:
        scope, term_id = encoded.split(":", 1)
    except ValueError as exc:
        raise ValueError(f"malformed qualified term ID: {value}") from exc
    if not scope or not term_id:
        raise ValueError(f"malformed qualified term ID: {value}")
    return unquote(scope), unquote(term_id)


@dataclass(frozen=True)
class SnapshotBinding:
    scope: str
    snapshot_id: str
    content_hash: str
    source_ref: str
    base: Path
    terms_file: Path

    def public(self) -> dict:
        return {
            "scope": self.scope,
            "snapshot_id": self.snapshot_id,
            "content_hash": self.content_hash,
            "source_ref": self.source_ref,
        }


@dataclass(frozen=True)
class VocabularyContext:
    project_id: str
    project: SnapshotBinding
    organization: SnapshotBinding
    context_version: str = CONTEXT_VERSION

    def __post_init__(self):
        if self.project.scope != f"project:{self.project_id}":
            raise ValueError("project Snapshot scope does not match project_id")
        if self.organization.scope != "org:common":
            raise ValueError("organization Snapshot scope must be org:common")

    def public(self) -> dict:
        return {
            "context_version": self.context_version,
            "project_id": self.project_id,
            "project": self.project.public(),
            "organization": self.organization.public(),
        }

    @property
    def cache_key(self) -> tuple:
        return (
            self.context_version,
            self.project_id,
            self.project.snapshot_id,
            self.project.content_hash,
            self.project.source_ref,
            self.organization.snapshot_id,
            self.organization.content_hash,
            self.organization.source_ref,
        )


_ACTIVE_CONTEXT: ContextVar[VocabularyContext | None] = ContextVar(
    "rimay_vocabulary_context", default=None)


def active_vocabulary_context() -> VocabularyContext | None:
    return _ACTIVE_CONTEXT.get()


@contextmanager
def vocabulary_operation(context: VocabularyContext):
    """明示解決済みContextを1操作へ束縛する。ContextVarなので並行操作を隔離する。"""
    token = _ACTIVE_CONTEXT.set(context)
    try:
        yield context
    finally:
        _ACTIVE_CONTEXT.reset(token)


def _sha256(path: Path) -> str:
    return "sha256:" + hashlib.sha256(path.read_bytes()).hexdigest()


def _inside(root: Path, candidate: Path) -> Path:
    root = root.resolve()
    candidate = candidate.resolve()
    if candidate != root and root not in candidate.parents:
        raise ValueError("vocabulary registry reference escapes vocabulary root")
    return candidate


def _read_terms_file(path: Path, expected_scope: str) -> tuple[dict, ...]:
    doc = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    declared_scope = doc.get("scope")
    if declared_scope is not None and declared_scope != expected_scope:
        raise ValueError(
            f"Snapshot scope mismatch: expected {expected_scope}, got {declared_scope}")
    rows = doc.get("terms")
    if not isinstance(rows, list):
        raise ValueError(f"Snapshot terms must be a list: {path}")
    out: list[dict] = []
    identities: set[tuple[str, str]] = set()
    qualified: set[str] = set()
    for source in rows:
        if not isinstance(source, dict):
            raise ValueError(f"Snapshot term must be an object: {path}")
        term = dict(source)
        scope = term.get("scope") or declared_scope
        if not scope:
            raise ValueError(f"scope-less term is forbidden: {term.get('id')}")
        if scope != expected_scope:
            raise ValueError(
                f"term scope mismatch: expected {expected_scope}, got {scope}")
        term_id = term.get("id")
        if not isinstance(term_id, str) or not term_id:
            raise ValueError("term id must be a non-empty string")
        identity = (scope, term_id)
        qid = qualified_term_id(scope, term_id)
        if identity in identities or qid in qualified:
            raise ValueError(f"duplicate qualified term identity: {qid}")
        identities.add(identity)
        qualified.add(qid)
        term["scope"] = scope
        term["qualified_id"] = qid
        out.append(term)
    surface_owners: dict[str, str] = {}
    for term in out:
        if term.get("homonym") or term.get("status") in ("deprecated", "superseded"):
            continue
        for surface in [term["preferred_japanese"], *(term.get("synonyms") or [])]:
            owner = surface_owners.get(surface)
            if owner is not None and owner != term["qualified_id"]:
                raise ValueError(
                    f"conflicting term surface in {expected_scope}: {surface}")
            surface_owners[surface] = term["qualified_id"]
    return tuple(out)


@lru_cache(maxsize=64)
def _load_binding(binding: SnapshotBinding) -> tuple[dict, ...]:
    actual = _sha256(binding.terms_file)
    if actual != binding.content_hash:
        raise ValueError(
            f"pinned vocabulary hash mismatch: {binding.source_ref} "
            f"expected={binding.content_hash} actual={actual}")
    return _read_terms_file(binding.terms_file, binding.scope)


def project_terms(context: VocabularyContext) -> tuple[dict, ...]:
    return _load_binding(context.project)


def organization_terms(context: VocabularyContext) -> tuple[dict, ...]:
    return _load_binding(context.organization)


@lru_cache(maxsize=64)
def _effective_terms(context: VocabularyContext) -> tuple[dict, ...]:
    # 優先順位は並び順ではなくResolverがscopeごとに適用する。ここでは複合IDの
    # 一意性だけを検査し、異scopeの同じ裸ID・同じ表層は共存させる。
    merged = project_terms(context) + organization_terms(context)
    seen: set[str] = set()
    for term in merged:
        qid = term["qualified_id"]
        if qid in seen:
            raise ValueError(f"duplicate qualified term ID in context: {qid}")
        seen.add(qid)
    return merged


def effective_terms(context: VocabularyContext) -> tuple[dict, ...]:
    return _effective_terms(context)


class VocabularyRegistry:
    """サーバー管理の案件レジストリ。クライアント入力をパスへ変換しない。"""

    def __init__(self, vocabulary_root: Path, registry_path: Path | None = None):
        self.root = Path(vocabulary_root).resolve()
        self.registry_path = Path(registry_path or self.root / "project-registry.yaml")
        doc = yaml.safe_load(self.registry_path.read_text(encoding="utf-8")) or {}
        if doc.get("registry_version") != REGISTRY_VERSION:
            raise ValueError(
                f"unsupported vocabulary registry version: {doc.get('registry_version')}")
        rows = doc.get("projects") or []
        if not isinstance(rows, list):
            raise ValueError("projects must be a list")
        self._projects: dict[str, dict] = {}
        for row in rows:
            if not isinstance(row, dict) or set(row) - {"project_id", "fixture"}:
                raise ValueError("unsupported project registry field")
            pid = (row or {}).get("project_id")
            if not isinstance(pid, str) or not _PROJECT_ID.fullmatch(pid):
                raise ValueError(f"invalid registered project_id: {pid}")
            if pid in self._projects:
                raise ValueError(f"duplicate registered project_id: {pid}")
            self._projects[pid] = dict(row)
        self._organization = dict(doc.get("organization") or {})
        if set(self._organization) - {"fixture"}:
            raise ValueError("unsupported organization registry field")

    def registered(self, project_id: str) -> bool:
        return project_id in self._projects

    def project_root(self, project_id: str) -> Path:
        self._project_record(project_id)
        return _inside(self.root, self.root / "projects" / project_id)

    def terminology_root(self, project_id: str) -> Path:
        return self.project_root(project_id) / "terminology"

    def organization_root(self) -> Path:
        return _inside(self.root, self.root / "org" / "common")

    def _project_record(self, project_id: str) -> dict:
        if not isinstance(project_id, str) or not _PROJECT_ID.fullmatch(project_id):
            raise ValueError(f"invalid project_id: {project_id}")
        if project_id not in self._projects:
            raise ValueError(f"unregistered project_id: {project_id}")
        return self._projects[project_id]

    def _fixture_binding(self, fixture: dict, scope: str) -> SnapshotBinding:
        allowed = {"snapshot_id", "terms_file", "source_ref"}
        if set(fixture) - allowed:
            raise ValueError("unsupported fixture registry field")
        rel = fixture.get("terms_file")
        if not isinstance(rel, str) or Path(rel).is_absolute() or ".." in Path(rel).parts:
            raise ValueError("fixture terms_file must be a safe root-relative path")
        path = _inside(self.root, self.root / rel)
        sid = fixture.get("snapshot_id")
        if not isinstance(sid, str) or not sid:
            raise ValueError("fixture snapshot_id is required")
        source_ref = fixture.get("source_ref") or f"vocabulary-fixture://{scope}/{sid}"
        return SnapshotBinding(scope, sid, _sha256(path), source_ref,
                               path.parent, path)

    def _snapshot_binding(self, base: Path, scope: str,
                          snapshot_id: str | None, source_prefix: str) -> SnapshotBinding:
        if snapshot_id is None:
            pointer = base / "snapshots" / "current.json"
            if not pointer.exists():
                raise ValueError(f"current vocabulary pointer is missing: {source_prefix}")
            snapshot_id = json.loads(pointer.read_text(encoding="utf-8"))["snapshot_id"]
        if not isinstance(snapshot_id, str) or not snapshot_id or "/" in snapshot_id:
            raise ValueError(f"invalid snapshot_id: {snapshot_id}")
        snap = _inside(base, base / "snapshots" / snapshot_id)
        terms_file = snap / "terms.yaml"
        manifest_file = snap / "manifest.json"
        if not terms_file.is_file() or not manifest_file.is_file():
            raise ValueError(f"published Snapshot artifact is incomplete: {source_prefix}/{snapshot_id}")
        manifest = json.loads(manifest_file.read_text(encoding="utf-8"))
        actual = _sha256(terms_file)
        expected = {
            "manifest_version": MANIFEST_VERSION,
            "snapshot_id": snapshot_id,
            "scope": scope,
            "content_hash": actual,
        }
        for key, value in expected.items():
            if manifest.get(key) != value:
                raise ValueError(f"Snapshot manifest mismatch for {key}: {source_prefix}/{snapshot_id}")
        return SnapshotBinding(
            scope, snapshot_id, actual,
            f"vocabulary://{source_prefix}/snapshots/{snapshot_id}", base, terms_file)

    def resolve(self, project_id: str, *, project_snapshot_id: str | None = None,
                organization_snapshot_id: str | None = None) -> VocabularyContext:
        row = self._project_record(project_id)
        project_scope = f"project:{project_id}"
        if row.get("fixture") is not None:
            if project_snapshot_id is not None and \
                    project_snapshot_id != row["fixture"].get("snapshot_id"):
                raise ValueError("fixture project Snapshot pin does not exist")
            project = self._fixture_binding(row["fixture"], project_scope)
        else:
            project = self._snapshot_binding(
                self.project_root(project_id), project_scope, project_snapshot_id,
                f"projects/{project_id}")

        if self._organization.get("fixture") is not None:
            fixture = self._organization["fixture"]
            if organization_snapshot_id is not None and \
                    organization_snapshot_id != fixture.get("snapshot_id"):
                raise ValueError("fixture organization Snapshot pin does not exist")
            organization = self._fixture_binding(fixture, "org:common")
        else:
            organization = self._snapshot_binding(
                self.organization_root(), "org:common", organization_snapshot_id,
                "org/common")
        context = VocabularyContext(project_id, project, organization)
        # pin時点でscope・複合ID・manifestをfail-closed検査する。
        effective_terms(context)
        return context


def write_snapshot_artifact(base: Path, scope: str, snapshot_id: str, terms,
                            *, published_at: str, operation_id: str) -> dict:
    """Immutable Snapshot・manifest・current指示子を耐久成果物として書く。"""
    base = Path(base)
    if not snapshot_id or "/" in snapshot_id:
        raise ValueError(f"invalid snapshot_id: {snapshot_id}")
    normalized: list[dict] = []
    for source in terms:
        term = {k: v for k, v in dict(source).items() if k != "qualified_id"}
        actual_scope = term.get("scope") or scope
        if actual_scope != scope:
            raise ValueError(
                f"term scope mismatch during publish: expected {scope}, got {actual_scope}")
        term["scope"] = scope
        normalized.append(term)
    # 公開前に同一複合IDとscopeなしを検査する。表層重複は呼出し側のLoader gate。
    identities: set[tuple[str, str]] = set()
    for term in normalized:
        identity = (scope, term.get("id"))
        if not identity[1] or identity in identities:
            raise ValueError(f"duplicate or missing term identity: {identity}")
        identities.add(identity)

    snap_dir = base / "snapshots" / snapshot_id
    terms_text = yaml.safe_dump(
        {"snapshot_contract_version": "1.0.0", "scope": scope,
         "terms": normalized}, allow_unicode=True, sort_keys=False)
    content_hash = "sha256:" + hashlib.sha256(terms_text.encode("utf-8")).hexdigest()
    manifest = {
        "manifest_version": MANIFEST_VERSION,
        "snapshot_id": snapshot_id,
        "scope": scope,
        "content_hash": content_hash,
        "published_at": published_at,
        "operation_id": operation_id,
    }
    if snap_dir.exists():
        existing_terms = snap_dir / "terms.yaml"
        existing_manifest = snap_dir / "manifest.json"
        if existing_terms.is_file() and existing_manifest.is_file() and \
                _sha256(existing_terms) == content_hash and \
                json.loads(existing_manifest.read_text(encoding="utf-8")) == manifest:
            return manifest
        raise ValueError(f"snapshot already exists with different content: {snapshot_id}")
    snap_dir.mkdir(parents=True)
    (snap_dir / "terms.yaml").write_text(terms_text, encoding="utf-8")
    (snap_dir / "manifest.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    pointer = base / "snapshots" / "current.json"
    pointer.write_text(
        json.dumps({"pointer_version": "1.0.0", "snapshot_id": snapshot_id},
                   ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return manifest


def assert_project_owner(record: dict, project_id: str) -> None:
    owner = record.get("project_id")
    if owner != project_id:
        raise ValueError(
            f"project ownership mismatch: requested={project_id} stored={owner}")
