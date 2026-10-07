"""判断負荷を測る（読むだけ）。ゲート記録と進行状態から数える。

- 観点ごと（既定）：観点＋種類ごとの却下の割合・AI 推奨の採用率など。却下のうち「指摘の誤り」「対象外」
  「後で決める」の割合が 10% を超えた観点＋種類は、その観点の SKILL.md・指摘の共通ルール・前提を見直すか、検査を止める。
- まとめ（`--summary`）：工程ごと・全体の合計。対応プランの「効果の確かめ方」の指標と同じ項目。
  人の操作は操作 ID ごとに 1 回と数え、成果物・指摘の数（承認・確認した成果物数、人が判断した指摘）とは分ける。
- 比べる（`--compare <別の案件>`）：同じ案件を改修の前後で流した 2 つを、まとめの項目で並べる。

旧形式の記録（種類を持たない指摘）も数える。種類が無い指摘は「要判断」として数え、同一性キーが要る項目（修正済みの再検出）は数えない。

    python3 .claude/skills/aidd-common/scripts/review_metrics.py --root <案件> [--summary] [--compare <別の案件>]
"""
import argparse
import json
from pathlib import Path
import re

import finding_rules
import record_format

THRESHOLD = 0.10
NOISE = ("指摘の誤り", "対象外", "後で決める")
ORDER = ("intake", "steering", "feature", "requirements", "design", "docs", "tasks", "implement")


def records(root):
    result = []
    for path in sorted((Path(root) / ".aidd/gates").glob("phase-*.md")):
        try:
            result.append(record_format.parse(path.read_text(encoding="utf-8")))
        except (ValueError, OSError):
            continue
    return sorted(result, key=lambda r: ORDER.index(r.phase) if r.phase in ORDER else len(ORDER))


def collect(root):
    """観点＋種類ごとの内訳。"""
    groups = {}
    for record in records(root):
        for run in record.runs:
            for f in run.findings:
                for gate in f.gate.split(" / "):
                    key = (record.phase, gate, f.kind or "未分類")
                    g = groups.setdefault(key, {"指摘": 0, "人の判断": 0, "system の判断": 0, "却下": 0, "却下（誤り・対象外・後で）": 0,
                                                "推奨あり": 0, "推奨を採用": 0, "種類を変更": 0, "除外": 0})
                    g["指摘"] += 1
                    if f.verification.startswith("種類を変更"):
                        g["種類を変更"] += 1
                    if not f.has_decision:
                        continue
                    g["system の判断" if f.by_system else "人の判断"] += 1
                    if f.decision == "対応せず進める" and not f.by_system:
                        g["却下"] += 1
                        if f.category in NOISE:
                            g["却下（誤り・対象外・後で）"] += 1
                    if f.adopted:
                        g["推奨あり"] += 1
                        g["推奨を採用"] += f.adopted == "採用"
            for row in run.excluded:
                key = (record.phase, row["観点"], "除外")
                groups.setdefault(key, {"除外": 0})
                groups[key]["除外"] = groups[key].get("除外", 0) + 1
    rows = []
    for (phase, gate, kind), g in sorted(groups.items()):
        judged = g.get("人の判断", 0)
        noise = g.get("却下（誤り・対象外・後で）", 0) / judged if judged else 0.0
        adopted = g.get("推奨を採用", 0) / g["推奨あり"] if g.get("推奨あり") else None
        rows.append({"工程": phase, "観点": gate, "種類": kind, **g, "誤検知の割合": round(noise, 3),
                     "推奨の採用率": None if adopted is None else round(adopted, 3), "見直し": noise > THRESHOLD})
    return rows


SUMMARY_KEYS = ("検査の回数", "指摘", "人に出た指摘", "重大", "要判断", "軽微", "前提により出さなかった指摘", "形式不備で意味検査から外した節",
                "system が判断した指摘", "人が判断した指摘", "対応せず進める（人）", "対応せず進めるの割合",
                "system の解消", "修正済みの再検出", "人が書いた修正指示", "AI・理由で埋めた修正指示", "承認・確認した成果物数",
                "人の判断の回答", "人の解消確認", "修正の依頼", "承認・確認",
                "人の操作（判断・解消確認・修正の依頼・承認）")
# 人の操作は、操作 ID ごとに 1 回と数える（1 回の回答で複数の指摘を判断しても、1 回の承認で複数の成果物を承認しても 1 回）。
OPERATIONS = {"decisions": "人の判断の回答", "decision": "人の判断の回答", "resolve": "人の解消確認",
              "repair": "修正の依頼", "approve": "承認・確認"}
OPERATION_KEYS = ("人の判断の回答", "人の解消確認", "修正の依頼", "承認・確認")
PHASE_OF_ACTION = (("requirement-intake", "intake"), ("steering-", "steering"), ("feature-decomposition", "feature"),
                   ("requirements-", "requirements"), ("design-", "design"), ("docs-", "docs"), ("tasks-", "tasks"),
                   ("implement", "implement"))


def _empty():
    return {key: 0 for key in SUMMARY_KEYS}


def phase_of(action):
    return next((phase for prefix, phase in PHASE_OF_ACTION if (action or "").startswith(prefix)), "")


def _state(root):
    """進行状態（`.aidd/phase-progress.json`）。読めなければ None。"""
    try:
        return json.loads((Path(root) / ".aidd/phase-progress.json").read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return None


def operations(state):
    """人の操作の回数（工程ごと）。操作 ID ごとに 1 回。

    ホストの回答の記録（host_operations の respond）を数え、ホストを通らずに記録された判断・解消・承認は
    レビュー操作の記録（workflow.review_operations）から数える。後者は、一括の判断の子（`<操作 ID>.<n>`）を親の 1 回にまとめる。
    """
    result, seen = {}, set()
    for key, entry in (state.get("host_operations") or {}).items():
        request = (entry or {}).get("request") or {}
        name = OPERATIONS.get(((request.get("payload") or {}).get("action")) or "")
        if request.get("kind") == "respond" and name:
            seen.add(key)
            counts = result.setdefault(phase_of(request.get("event")), {k: 0 for k in OPERATION_KEYS})
            counts[name] += 1
    grouped = {}
    for key, entry in ((state.get("workflow") or {}).get("review_operations") or {}).items():
        base = re.sub(r"\.\d+$", "", key)
        request = (entry or {}).get("request") or {}
        if base not in seen and OPERATIONS.get(request.get("action")):
            grouped[base] = request
    for request in grouped.values():
        counts = result.setdefault(phase_of(request.get("event")), {k: 0 for k in OPERATION_KEYS})
        counts[OPERATIONS[request["action"]]] += 1
    if not any(entry.get("request", {}).get("kind") == "respond" for entry in (state.get("host_operations") or {}).values()):
        # ホストを通らずに使った案件（試験など）では、修正の依頼は依頼の記録の数で数える。
        workflow = state.get("workflow") or {}
        ids = {}
        for request in list((workflow.get("repairs") or {}).values()) + list(workflow.get("repair_history") or []):
            if (request or {}).get("origin") == "finding" and request.get("actor") != finding_rules.SYSTEM_ACTOR:
                ids[request.get("id")] = phase_of(request.get("event"))
        for phase in ids.values():
            result.setdefault(phase, {k: 0 for k in OPERATION_KEYS})["修正の依頼"] += 1
    return result


def _repair_rows(state):
    """修正の依頼に入った指摘（工程ごと）。人が書いた指示と、L3 が修正案・判断の理由で埋めた指示を分ける。"""
    workflow = state.get("workflow") or {}
    seen, result = set(), {}
    requests = list((workflow.get("repairs") or {}).values()) + list(workflow.get("repair_history") or [])
    for request in requests:
        for row in (request or {}).get("findings") or []:
            key = tuple(row.get(k) for k in ("phase", "scope", "run", "number"))
            if key in seen or not row.get("instruction"):
                continue
            seen.add(key)
            counts = result.setdefault(row.get("phase", ""), [0, 0])
            counts[1 if row.get("instruction_source") else 0] += 1
    return result


def summary(root):
    """工程ごと・全体の合計。成果物・指摘の数と、人の操作の回数（操作 ID ごと）を分けて数える。"""
    phases, judged, blocks = {}, {}, {}
    for record in records(root):
        s = phases.setdefault(record.phase, _empty())
        latest = {}
        for run in record.runs:
            s["検査の回数"] += 1
            unchecked = sum(row["除外の出典"].startswith(finding_rules.UNCHECKED) for row in run.excluded)
            s["形式不備で意味検査から外した節"] += unchecked
            s["前提により出さなかった指摘"] += len(run.excluded) - unchecked
            for f in run.findings:
                s["指摘"] += 1
                s[f.level] += 1
                if f.by_system:
                    s["system が判断した指摘"] += 1
                else:
                    s["人に出た指摘"] += 1
                latest[f.key] = f
        # 進行状態が無いときの代わり：記録のブロック（1 回の書込み）を 1 回と数える。
        fallback = blocks.setdefault(record.phase, {k: 0 for k in OPERATION_KEYS})
        for section, rows in record.blocks:
            human = [row for row in rows if not (row.get("判断者") or row.get("確認者") or "").startswith(finding_rules.SYSTEM_ACTOR)]
            if section == "判断":
                s["人が判断した指摘"] += len(human)
                fallback["人の判断の回答"] += bool(human)
            elif section == "解消":
                s["system の解消"] += len(rows) - len(human)
                s["修正済みの再検出"] += sum("引き継ぎ" in row["確認者"] for row in rows)
                fallback["人の解消確認"] += bool(human)
            elif section in ("承認", "確認"):
                s["承認・確認した成果物数"] += len(rows) if section == "承認" else 1
                fallback["承認・確認"] += 1
        decided = [f for f in latest.values() if f.has_decision and not f.by_system]
        judged[record.phase] = len(decided)
        s["対応せず進める（人）"] = sum(f.decision == "対応せず進める" for f in decided)
        s["対応せず進めるの割合"] = round(s["対応せず進める（人）"] / len(decided), 3) if decided else 0.0
    state = _state(root)
    counted = operations(state) if state is not None else blocks
    for phase, counts in counted.items():
        s = phases.setdefault(phase, _empty())
        for key in OPERATION_KEYS:
            s[key] += counts.get(key, 0)
    for phase, (written, filled) in (_repair_rows(state) if state is not None else {}).items():
        s = phases.setdefault(phase, _empty())
        s["人が書いた修正指示"] += written
        s["AI・理由で埋めた修正指示"] += filled
    total = _empty()
    for s in phases.values():
        s["人の操作（判断・解消確認・修正の依頼・承認）"] = sum(s[key] for key in OPERATION_KEYS)
        for key in SUMMARY_KEYS:
            if key != "対応せず進めるの割合":
                total[key] += s[key]
    decided = sum(judged.values())
    total["対応せず進めるの割合"] = round(total["対応せず進める（人）"] / decided, 3) if decided else 0.0
    ordered = {phase: phases[phase] for phase in sorted(phases, key=lambda p: ORDER.index(p) if p in ORDER else len(ORDER))}
    return {"工程": ordered, "全体": total}


def table(columns):
    """{見出し: まとめ} を、項目を行にした Markdown の表にする。"""
    names = list(columns)
    lines = ["| 項目 | " + " | ".join(names) + " |", "|---|" + "---|" * len(names)]
    for key in SUMMARY_KEYS:
        lines.append("| %s | %s |" % (key, " | ".join(str(columns[name].get(key, "")) for name in names)))
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", default=".")
    parser.add_argument("--summary", action="store_true", help="工程ごと・全体の合計を表で出す")
    parser.add_argument("--compare", help="比べる別の案件（例：改修前の配布物で流した同じ案件）")
    parser.add_argument("--json", action="store_true", help="表ではなく JSON で出す")
    args = parser.parse_args()
    if args.compare:
        before, after = summary(args.compare), summary(args.root)
        if args.json:
            print(json.dumps({"比べる案件": before, "この案件": after}, ensure_ascii=False, indent=2))
            return
        phases = [p for p in ORDER if p in before["工程"] or p in after["工程"]]
        print("## 全体\n\n" + table({"比べる案件": before["全体"], "この案件": after["全体"]}))
        for phase in phases:
            print("\n## %s\n\n" % phase + table({"比べる案件": before["工程"].get(phase, _empty()),
                                                 "この案件": after["工程"].get(phase, _empty())}))
    elif args.summary:
        data = summary(args.root)
        if args.json:
            print(json.dumps(data, ensure_ascii=False, indent=2))
            return
        print(table({**data["工程"], "全体": data["全体"]}))
    else:
        print(json.dumps(collect(args.root), ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
