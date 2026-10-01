"""合成 Skill の手順と `calls` の一致を確かめる（L4）。L0 は Skill の中身を読まないため、ここで確かめる。

`gate.yaml` / `action.yaml` の `run.calls` は、合成 Skill（`run.target`）の `## 手順` が Read する
観点 Skill（`.claude/skills/<name>/SKILL.md`）の並びと、順序まで一致しなければならない。

    python3 .claude/skills/aidd-common/scripts/check_calls.py     # 一致しなければ終了コード 1
"""
import os
import re
import sys

import l0  # noqa: F401
import execution_context as framework

_SKILL_REF = re.compile(r"\.claude/skills/([A-Za-z0-9_.-]+)/SKILL\.md")
_STEPS = re.compile(r"^## 手順\s*\n(.*?)(?=^## |\Z)", re.M | re.S)


def referenced_skills(text):
    """合成 Skill の手順内の参照だけを、順序を保って返す。"""
    sections = _STEPS.findall(text)
    if len(sections) != 1:
        raise ValueError("合成 Skill は `## 手順` を一つ持つ必要がある")
    return [match.group(1) for match in _SKILL_REF.finditer(sections[0])]


def problems(config=None):
    data = framework.definitions(config)
    skills_root = os.path.dirname(data["config"])
    rows = [("action `%s`" % row["name"], row["run"]) for row in data["events"]]
    rows += [("gate `%s`" % row["name"], row["run"]) for row in data["gates"]]
    found, checked = [], set()
    for label, run in rows:
        if run["type"] != "skill" or not run.get("calls"):
            continue
        key = (run["target"], tuple(run["calls"]))
        if key in checked:
            continue
        checked.add(key)
        with open(os.path.join(skills_root, run["target"], "SKILL.md"), encoding="utf-8") as handle:
            try:
                body = referenced_skills(handle.read())
            except ValueError as error:
                found.append("%s: %s" % (label, error))
                continue
        if body != list(run["calls"]):
            found.append("%s: `run.calls` %s と、合成 Skill `%s` の手順内 Read 対象 %s が一致しない"
                         % (label, list(run["calls"]), run["target"], body))
    return found


if __name__ == "__main__":
    errors = problems(sys.argv[1] if len(sys.argv) > 1 else None)
    for line in errors:
        print(line, file=sys.stderr)
    sys.exit(1 if errors else 0)
