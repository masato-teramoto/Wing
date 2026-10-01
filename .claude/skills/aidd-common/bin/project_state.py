"""状態ストアの案件欄の読み書き（L3・L4 が import する枠組みの API）。

状態ストア（`.aidd/phase-progress.json`）の欄は、ランナーの欄（`RUNNER_FIELDS`）と案件の欄に分かれる。
ランナーの欄は `state.py`（Workflow Engine）と `host.py` だけが書く。案件の欄（`phases` / `features` /
`workflow` …）は L3・L4 の規則が、この module で書く。L0 は案件の欄の意味を解釈しない。
"""

from datetime import datetime
import json
import os
from pathlib import Path

# host_operations は host（host.py）の操作の記録。L3・L4 は書き換えない。
RUNNER_FIELDS = {"events", "trace", "current", "engine_schema", "engine_reports", "host_operations"}


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
    """案件の欄を書き換える。ランナーの欄を含めればエラーにする。"""
    if RUNNER_FIELDS.intersection(changes):
        raise ValueError("project updates may not replace runner-owned fields")
    return _write(path, changes)


def _write(path, changes):
    data = read(path)
    data.update(changes)
    data["updated_at"] = now()
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(path.name + ".project.tmp")
    temporary.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    os.replace(temporary, path)
    return data
