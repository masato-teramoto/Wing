"""Strict L1 input shapes for deterministic quality checks (L4)."""
import re


def section(text, heading, required=True):
    matches = re.findall(r"^## " + re.escape(heading) + r"\s*\n(.*?)(?=^## |\Z)", text, re.M | re.S)
    if len(matches) != 1:
        if not required and not matches:
            return ""
        raise ValueError("required section missing or duplicated: %s" % heading)
    return re.split(r"(?m)^### 項目の定義", matches[0])[0]


def requirements(text, retired=False):
    heading = "廃止済み要求" if retired else "要求一覧"
    body = section(text, heading, required=not retired)
    expected = ["要求ID", "要求文", "廃止日", "廃止理由"] if retired else ["要求ID", "要求文", "出典種別", "出典アンカー", "分類"]
    lines = [line.strip() for line in body.splitlines() if line.strip().startswith("|")]
    if not lines and retired:
        return []
    if len(lines) < 2:
        raise ValueError("requirement table missing: %s" % heading)
    rows = [[c.strip() for c in line.strip("|").split("|")] for line in lines]
    if rows[0] != expected or len(rows[1]) != len(expected) or not all(re.fullmatch(r":?-{3,}:?", c) for c in rows[1]):
        raise ValueError("requirement table header differs: %s" % heading)
    result = []
    for row in rows[2:]:
        if len(row) != len(expected):
            raise ValueError("requirement table row width differs")
        # The optional retired template may remain unused; active placeholders cannot.
        if retired and row[0] == "<RETIRED_REQUIREMENT_ID_N>":
            continue
        if not re.fullmatch(r"REQ-[0-9]{3,}", row[0]):
            raise ValueError("invalid requirement ID: %s" % row[0])
        result.append(row[0])
    if not result and not retired:
        raise ValueError("active requirement table is empty")
    if len(result) != len(set(result)):
        raise ValueError("duplicate requirement definitions")
    return result


def tasks(text):
    body = section(text, "タスク一覧")
    matches = list(re.finditer(r"(?m)^- \[[ xX]\] ([1-9][0-9]*)[.、]?\s+(.+)$", body))
    if not matches:
        raise ValueError("task checklist is missing or unfilled")
    result = []
    for index, match in enumerate(matches):
        end = matches[index + 1].start() if index + 1 < len(matches) else len(body)
        content = body[match.end():end]
        deps = re.findall(r"_Depends:\s*(.*?)_", content)
        if len(deps) != 1:
            raise ValueError("one Depends annotation is required for task %s" % match[1])
        names = [] if deps[0] == "なし" else [d.strip() for d in deps[0].split(",")]
        if any(not re.fullmatch(r"[1-9][0-9]*", d) for d in names) or len(names) != len(set(names)):
            raise ValueError("invalid task dependency annotation")
        result.append({"name": match[1], "depends_on": names})
    if len(result) != len({r["name"] for r in result}):
        raise ValueError("duplicate task number")
    return result


def graph_problems(entries):
    positions = {entry["name"]: index for index, entry in enumerate(entries)}
    for entry in entries:
        for dependency in entry["depends_on"]:
            if dependency not in positions:
                yield "%s: unknown dependency %s" % (entry["name"], dependency)
            elif positions[dependency] >= positions[entry["name"]]:
                yield "%s: dependency %s is self, cyclic or not earlier" % (entry["name"], dependency)
