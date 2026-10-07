"""検査に渡す前提。専用のファイルは持たず、すでにある記録から集める。

| 前提 | 置き場所 |
|---|---|
| 工程の境界・対象外 | 指摘の共通ルール（L4 `finding-rules`）。全案件で同じ |
| 人が確定した回答 | 進行状態の `workflow.waiting`（作成時の質問への回答） |
| 却下から学んだ扱い | ゲート記録の判断の行（却下区分と「今後も同じ扱い」） |
| 前回までの指摘 | このスコープのゲート記録 |

前提に入るのは、人が宣言・回答・選択したものだけ。AI が推測した前提は入れない。
"""
from pathlib import Path

import project_progress
import record_format

FINDING_RULES = ".claude/skills/finding-rules/SKILL.md"


def confirmed_answers(context):
    rows = []
    for key, entry in sorted(project_progress.workflow(context).get("waiting", {}).items()):
        if isinstance(entry, dict) and entry.get("status") == "answered" and entry.get("answers"):
            rows.append({"key": key, "questions": entry.get("questions") or [], "answers": entry["answers"],
                         "answered_by": entry.get("answered_by", ""), "answered_at": entry.get("answered_at", "")})
    return rows


def records(context):
    """読めるゲート記録（旧形式は前提にしない）。"""
    folder = Path(context.gate_record).parent
    result = []
    for path in sorted(folder.glob("phase-*.md")) if folder.is_dir() else []:
        try:
            result.append(record_format.parse(path.read_text(encoding="utf-8")))
        except (ValueError, OSError):
            continue
    return result


def learned(context):
    """同じ工程の「今後も同じ扱い」の却下だけ（ほかの工程で決める事項を、その工程の検査で外さないため）。"""
    rows = []
    for record in records(context):
        if record.phase != context.process:
            continue
        for run in record.runs:
            for f in run.findings:
                if f.learn and f.decision == "対応せず進める":
                    rows.append({"phase": record.phase, "scope": f.scope, "run": f.run, "number": f.number,
                                 "観点": f.gate, "種類": f.kind, "対象箇所": f.location, "要約": f.short,
                                 "却下区分": f.category, "理由": f.reason, "判断者": f.decided_by})
    return rows


def previous_findings(context):
    path = Path(context.gate_record)
    if not path.exists():
        return []
    try:
        record = record_format.parse(path.read_text(encoding="utf-8"))
    except ValueError:
        return []
    return [{"run": f.run, "number": f.number, "観点": f.gate, "種類": f.kind, "対象箇所": f.location,
             "対象の語": f.subject, "要約": f.short, "判断": f.decision, "理由": f.reason, "解消": f.resolved}
            for run in record.runs if run.scope == context.scope for f in run.findings]


def collect(context):
    return {"finding_rules": FINDING_RULES, "confirmed_answers": confirmed_answers(context),
            "learned": learned(context), "previous_findings": previous_findings(context)}
