"""Inspection-scoped handoff from deterministic checks to the L4 runner.

Adapted from 82d2db2: no glob consumption, no silent JSON corruption recovery.
"""
import json
from pathlib import Path

import snapshot_artifacts


def stage_path(context):
    return snapshot_artifacts.snapshot_path(context).replace(".snapshot.json", ".findings.json")


def reset(context, snapshot):
    data = {key: snapshot[key] for key in ("phase", "event", "scope", "run")}
    data["findings"] = []
    Path(stage_path(context)).write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def read(context):
    data = json.loads(Path(stage_path(context)).read_text(encoding="utf-8"))
    snapshot = snapshot_artifacts.load(context)
    if not isinstance(data, dict) or any(data.get(k) != snapshot[k] for k in ("phase", "event", "scope", "run")):
        raise ValueError("staged findings belong to another inspection")
    rows = data.get("findings")
    if not isinstance(rows, list):
        raise ValueError("staged findings must be an array")
    for row in rows:
        if not isinstance(row, dict) or set(row) != {"gate", "location", "finding", "is_rollback_candidate"}:
            raise ValueError("invalid staged finding")
        if any(not isinstance(row[k], str) or not row[k] for k in ("gate", "location", "finding")) or not isinstance(row["is_rollback_candidate"], bool):
            raise ValueError("invalid staged finding values")
    return rows


def append(context, gate, location, finding, is_rollback_candidate=False):
    rows = read(context)
    row = {"gate": gate, "location": location, "finding": finding, "is_rollback_candidate": bool(is_rollback_candidate)}
    if row not in rows:
        rows.append(row)
    data = json.loads(Path(stage_path(context)).read_text(encoding="utf-8"))
    data["findings"] = rows
    Path(stage_path(context)).write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
