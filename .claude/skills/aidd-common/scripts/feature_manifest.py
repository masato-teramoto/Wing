"""One strict reader for feature definitions; consumers use the checked snapshot."""

import hashlib
import json
from pathlib import Path
import re

import artifacts
import project_state

SOURCE = ".aidd/feature-list.md"
SCHEMA = 1
COLUMNS = ["feature 名", "種別", "目的", "依存", "優先度", "想定規模", "対応要求ID"]
DEFINITION_KEYS = ("name", "kind", "priority", "depends_on")
RESERVED = {"con", "prn", "aux", "nul", *("com%d" % n for n in range(1, 10)), *("lpt%d" % n for n in range(1, 10))}


def source_path(root):
    return artifacts.resolve(root, SOURCE)


def source_hash(root, approved=True):
    path = source_path(root)
    if not path.is_file():
        raise ValueError("feature-list.md is missing")
    if approved and (artifacts.fields(path) or {}).get("status") != "approved":
        raise ValueError("feature-list.md must be approved")
    return artifacts.protected_digest(path)


def parse(text):
    sections = re.findall(r"^## フィーチャー一覧\s*\n(.*?)(?=^## |\Z)", text, re.M | re.S)
    if len(sections) != 1:
        raise ValueError("one フィーチャー一覧 section is required")
    # Ignore definitions after ###; only the fixed manifest table is data.
    body = re.split(r"(?m)^### ", sections[0], maxsplit=1)[0]
    lines = [line.strip() for line in body.splitlines() if line.strip().startswith("|")]
    if len(lines) < 3:
        raise ValueError("feature table is empty or missing")
    rows = []
    for line in lines:
        if not line.endswith("|"):
            raise ValueError("feature table row is not closed")
        cells = [cell.strip() for cell in line[1:-1].split("|")]
        if len(cells) != len(COLUMNS):
            raise ValueError("feature table column count differs")
        rows.append(cells)
    if rows[0] != COLUMNS or not all(re.fullmatch(r":?-{3,}:?", cell) for cell in rows[1]):
        raise ValueError("feature table header differs from the L1 contract")
    features, seen = [], set()
    previous_priority = 0
    for cells in rows[2:]:
        if any(not cell or re.search(r"<[A-Z][A-Z0-9_]*>|\{\{", cell) for cell in cells):
            raise ValueError("feature table contains empty or placeholder cells")
        name, kind, _, dependency, priority, scale, _ = cells
        if not re.fullmatch(r"[a-z0-9][a-z0-9_-]*", name) or name in RESERVED or name in seen:
            raise ValueError("invalid or duplicate feature name: %s" % name)
        if kind not in ("User", "Platform") or scale not in ("大", "中", "小"):
            raise ValueError("invalid feature kind or scale: %s" % name)
        if not re.fullmatch(r"[1-9][0-9]*", priority):
            raise ValueError("priority must be a positive integer: %s" % name)
        value = int(priority)
        if value < previous_priority:
            raise ValueError("feature rows are not in priority order")
        dependencies = [] if dependency == "なし" else [d.strip() for d in dependency.split(",")]
        if len(set(dependencies)) != len(dependencies) or any(not re.fullmatch(r"[a-z0-9][a-z0-9_-]*", d) for d in dependencies):
            raise ValueError("invalid dependency list: %s" % name)
        # Dependencies must precede their consumers; this rejects cycles too.
        if any(d not in seen for d in dependencies):
            raise ValueError("dependency missing, cyclic, self-referencing or after consumer: %s" % name)
        features.append({"name": name, "kind": kind, "priority": value, "depends_on": dependencies})
        seen.add(name)
        previous_priority = value
    return features


def synchronize(root, state_path):
    digest = source_hash(root)
    definitions = parse(source_path(root).read_text(encoding="utf-8"))
    if source_hash(root) != digest:
        raise ValueError("feature source changed during synchronization")
    state = project_state.read(state_path)
    previous = state.get("feature_manifest") or {}
    old = state.get("features") or []
    old_by_name = {f["name"]: f for f in old if isinstance(f, dict) and isinstance(f.get("name"), str)}
    merged = []
    for definition in definitions:
        entry = dict(old_by_name.get(definition["name"], {}))
        entry.update(definition)
        merged.append(entry)
    history = list(state.get("feature_history") or [])
    workflow = dict(state.get("workflow") or {})
    if previous and previous.get("sha256") != digest:
        history.append({"at": project_state.now(), "manifest": previous, "features": old})
        old_defs = [{k: f.get(k) for k in DEFINITION_KEYS} for f in old]
        # Plans are re-presented only when the order or the set of features changed;
        # other column edits were already reviewed in the approved Phase 3 revision.
        structural = [d["name"] for d in old_defs] != [d["name"] for d in definitions] or \
            [d["depends_on"] for d in old_defs] != [d["depends_on"] for d in definitions]
        changed = sorted({d["name"] for d in definitions if d not in old_defs} | ({d["name"] for d in old_defs} - {d["name"] for d in definitions}))
        workflow["manifest_change"] = {"before": previous.get("sha256"), "after": digest, "needs_replan": True,
                                       "structural": structural, "changed": changed}
    metadata = {"source": SOURCE, "schema": SCHEMA, "sha256": digest, "synced_at": project_state.now(),
                "definition_sha256": hashlib.sha256(json.dumps(definitions, ensure_ascii=False, sort_keys=True).encode()).hexdigest()}
    project_state.update(state_path, {"features": merged, "feature_manifest": metadata,
                                      "feature_history": history, "workflow": workflow})
    return merged


def load(root, state_path):
    state = project_state.read(state_path)
    metadata = state.get("feature_manifest") or {}
    if metadata.get("schema") != SCHEMA or metadata.get("source") != SOURCE:
        raise ValueError("feature snapshot missing or incompatible; synchronize first")
    if metadata.get("sha256") != source_hash(root):
        raise ValueError("feature snapshot stale; synchronize and review the changed plan")
    features = state.get("features")
    if not isinstance(features, list) or not features:
        raise ValueError("feature snapshot is empty")
    try:
        definitions = [{key: entry[key] for key in DEFINITION_KEYS} for entry in features]
    except (TypeError, KeyError):
        raise ValueError("invalid feature snapshot schema")
    digest = hashlib.sha256(json.dumps(definitions, ensure_ascii=False, sort_keys=True).encode()).hexdigest()
    if digest != metadata.get("definition_sha256"):
        raise ValueError("feature snapshot was independently edited; synchronize again")
    return features
