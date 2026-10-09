"""人に出す前に L3 が機械で行う指摘の処理。scope-check が検査を封印した直後に 1 回だけ呼ぶ。

同一性キー（種類・位置・対象の語）で前回の指摘と照合し、人が一度した判断を引き継ぐ。

| 前回 | 今回 | 節 | 処理 |
|---|---|---|---|
| 対応せず進める・未対応 | あり | 同じ | 同じ判断を system として記録する（人に出さない） |
| 修正 | あり | — | 前回の指摘を今回へ引き継いで閉じる（今回の指摘を人に出す） |
| 修正・差戻し | なし | 変わった | 再検査による解消を system として記録する（形式不備で意味検査から外した対象は除く） |

今回の「軽微」（AIDD 内部の決まりごと）は、修正案があれば system が「修正」と判断し、AI が修正案で直す。
横断・tasks 全体の検査、実装の検査では直す成果物が 1 つに決まらないため、人に出す。
記録は判断・解消のブロックを末尾に足すだけで、検査の本文は変えない。何度呼んでも同じ記録になる。
"""
from pathlib import Path

import finding_rules
import project_state
import record_format
import review_contract

ACTOR = finding_rules.SYSTEM_ACTOR


def _open_blocker(context, finding):
    key = {"phase": context.process, "scope": finding.scope, "run": finding.run, "number": finding.number}
    return any(b.get("status") != "resolved" and all((b.get("finding") or {}).get(k) == v for k, v in key.items())
               for b in context.blockers())


def auto_repairable(context, scope):
    """system が軽微を直せる検査か（直す成果物がその検査の対象 1 つに決まる）。"""
    return not context.kind and not record_format.is_cross_scope(scope) and context.action != "tasks-gate-run"


def self_fixable(finding, run):
    """この工程の修正 Skill が修正案で直せる軽微か。差戻しの推奨・差戻しの候補・検査対象の外（上流）を指すものは除く。"""
    if finding.suggestion in ("", "-"):
        return False
    try:
        recommended, _ = finding_rules.recommendation(finding.recommendation)
    except ValueError:
        recommended = ""
    if recommended == "差戻し" or any(str(c.get("指摘番号")) == str(finding.number) for c in run.returns):
        return False
    path, _, _ = finding_rules.parse_location(finding.location)
    return path in run.targets


def complete(context, run):
    return all(layer in run.layers for layer in review_contract.required_layers(context, run.scope))


def plan(context, record, run, at):
    """追記する判断・解消の行。"""
    decisions, resolutions = [], []
    earlier = [f for r in record.runs if r.scope == run.scope and r.number < run.number for f in r.findings]
    previous = {}
    for finding in earlier:
        if finding.identity and finding.has_decision:
            previous[finding.identity] = finding  # 新しい回ほど後に来る
    current = {f.identity: f for f in run.findings if f.identity}
    for finding in run.findings:
        if finding.has_decision or not finding.identity:
            continue
        before = previous.get(finding.identity)
        row = {"スコープ": run.scope, "回数": str(run.number), "指摘番号": str(finding.number), "判断者": ACTOR, "日時": at,
               "却下区分": "", "今後も同じ扱い": "", "推奨の採用": ""}
        if (before and before.decision in ("対応せず進める", "未対応") and finding.section != "-"
                and before.section == finding.section):
            reason = "前回（%d 回目 #%d）と同じ指摘で、箇所に変更がない: %s" % (before.run, before.number, before.reason)
            decisions.append(dict(row, 判断=before.decision, 理由=reason, 却下区分=before.category))
        elif finding.level == "軽微" and auto_repairable(context, run.scope) and self_fixable(finding, run):
            decisions.append(dict(row, 判断="修正", 理由="軽微（AIDD 内部の決まりごと）のため、AI が修正案で直す"))
    import reevaluation
    decisions += reevaluation.closing_rows(context, record, run, at)
    for finding in earlier:
        if finding.resolved or finding.decision not in ("修正", "差戻し") or not finding.identity:
            continue
        if context.kind:
            continue  # 実装の解消は、L3 の resolve が確かめる実装固有の条件（resolution_ready）を通す
        again = current.get(finding.identity)
        row = {"スコープ": run.scope, "回数": str(finding.run), "指摘番号": str(finding.number),
               "再検査スコープ": run.scope, "再検査回数": str(run.number), "日時": at}
        if again is not None:
            # 同じ指摘がまだ出ている。判断は今回の指摘で人に問い、前回の修正は今回へ引き継いで閉じる。
            # 差戻しは上流の再承認と結び付くため閉じない（人が今回の指摘とあわせて確かめる）。
            if finding.decision == "修正" and not _open_blocker(context, finding):
                resolutions.append(dict(row, 確認者="%s：同じ指摘を %d 回目 #%d へ引き継ぎ" % (ACTOR, run.number, again.number)))
            continue
        if not complete(context, run) or _open_blocker(context, finding) or finding.section == "-":
            continue
        path, _, _ = finding_rules.parse_location(finding.location)
        if any(target in finding.location or target == path for target in finding_rules.unchecked_targets(run)):
            continue  # 形式不備で意味検査から外した対象。再検出されなくても、検査していないだけかもしれない
        if finding_rules.section_hash(context.root, finding.location) != finding.section:
            resolutions.append(dict(row, 確認者="%s：再検査で再検出なし" % ACTOR))
    return decisions, resolutions


def apply(context):
    record = review_contract.read(context)
    run = record.latest(context.scope)
    if run is None:
        return {"decisions": 0, "resolutions": 0}
    decisions, resolutions = plan(context, record, run, project_state.now())
    path = Path(context.gate_record)
    data = path.read_bytes()
    suffix = b""
    if decisions:
        suffix += ("\n" + record_format.render_table("判断", decisions)).encode("utf-8")
    if resolutions:
        suffix += ("\n" + record_format.render_table("解消", resolutions)).encode("utf-8")
    if suffix:
        record_format.parse((data + suffix).decode("utf-8"))
        temporary = path.with_name(path.name + ".triage.tmp")
        temporary.write_bytes(data + suffix)
        temporary.replace(path)
    import reevaluation
    if reevaluation.pending(context):
        reevaluation.finish(context, run)
    import repair_requests
    if repair_requests.is_revise(context):
        repair_requests.mark_executed(context, run.number)
    return {"decisions": len(decisions), "resolutions": len(resolutions)}
