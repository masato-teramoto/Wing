"""Project-owned fields, kept separate from the runner's events/current/trace."""

from datetime import datetime
import json
import os
from pathlib import Path

RUNNER_FIELDS = {"events", "trace", "current", "engine_schema", "engine_reports"}


def now():
    return datetime.now().astimezone().replace(microsecond=0).isoformat()


def read(path):
    path = Path(path)
    if not path.exists():
        return {}
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError("state root must be an object")
    return data


def update(path, changes):
    if RUNNER_FIELDS.intersection(changes):
        raise ValueError("project updates may not replace runner-owned fields")
    data = read(path)
    data.update(changes)
    data["updated_at"] = now()
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(path.name + ".project.tmp")
    temporary.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    os.replace(temporary, path)
    return data
