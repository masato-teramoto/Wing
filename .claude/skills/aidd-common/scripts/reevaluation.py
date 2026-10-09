"""切り替え前（旧形式）の未判断の指摘の再評価。改修前の版で検査した案件を、途中から新しい版に切り替えたときに使う。

旧形式の指摘は種類を持たないため、重大度・束・推奨・前提による除外・自動の引き継ぎが効かない。人が「再評価する」を
選ぶと、次のように新しい決まりの指摘として見直す。

1. 人の判断として、旧形式の未判断の指摘に「未対応（再評価に回した）」を記録する（承認は止まらない。持ち越しになる）。
2. 本文を変えない修正の回（origin: reevaluation）を予約する。修正 Skill は本文を変えずに完了を返す。
3. 修正の回の検査で、検査役は合成 check の観点を実行せず、`finding-reevaluation` の手順で旧形式の指摘だけを見直す
   （前提に当たるもの・実在しないもの・重複を除外し、残ったものに種類・要約・推奨を付ける）。
4. scope-check は、本文が再評価の対象の回から変わっていないこと、実行した層がその回と同じであることを確かめる。
   再評価の回は、その回の検査の範囲を引き継ぐ（新しく検査を広げたのではない）。
5. 封印の後、system が旧形式の指摘に「対応せず進める（再評価の n 回目へ移した）」を記録する（finding_triage）。
   人が判断するのは、再評価の回に残った指摘だけ。除外した指摘は記録に残り、承認時に一覧で見られる。

横断・tasks 全体の検査には修正の回が無いので、再評価は使えない（判断するか、検査をやり直す）。
"""
import phase_rules
import project_progress
import project_state
import record_format
import repair_requests
import review_contract
import review_operations
import review_view

REASON = "再評価に回した（再評価の回で、新しい決まりの指摘として見直す）"
CLOSE = "切り替え前の指摘。再評価（%d 回目）へ移した"
INSTRUCTION = "再評価のため本文は変えない。完了（targets は依頼のとおり、changed_findings は空）を返す"


def owner(context):
    if context.is_cross or context.action == "tasks-gate-run" or context.kind:
        raise ValueError("再評価は成果物ごとの検査で使う（横断・tasks 全体・実装の検査では、判断するか検査をやり直す）")
    revise = repair_requests.revise_context(context)
    waiting = repair_requests.waiting(revise)
    if waiting and waiting.get("origin") != "reevaluation":
        raise ValueError("修正の依頼と再評価は同じ修正の回にできません。先に再評価を終えてから修正を選んでください")
    return revise


def legacy(context, record=None):
    record = record or review_contract.read(context)
    return [f for f in record.relevant(context.scope) if review_view.is_legacy(f)]


def _rows(context, findings, actor):
    at = project_state.now()
    return [{"スコープ": f.scope, "回数": f.run, "指摘番号": f.number, "判断": "未対応", "理由": REASON,
             "判断者": actor, "日時": at} for f in findings]


def prepare(context, actor):
    """書き込まずに確かめる（回答の受付時）。"""
    owner(context)
    findings = legacy(context)
    if not findings:
        raise ValueError("再評価する切り替え前の未判断の指摘がありません")
    return review_operations.record_effect(context, "判断", _rows(context, findings, actor))


def request(context, actor, *, expected=None, operation_id=None):
    """旧形式の未判断の指摘を再評価に回し、本文を変えない修正の回を予約する。

    回答の記録（respond の apply）の中で呼ぶ。-generate のレビューでは回答を先に報告するため、ここではレビューの
    待ちを前提にした書き込み（review_operations.execute）を使わず、記録へ直接追記する。何度呼んでも同じ結果になる
    （再評価の対象を先に保存し、まだ判断の無いものだけに「未対応」を書く）。expected・operation_id は受付時に確かめ済み。
    """
    revise = owner(context)
    record = review_contract.read(context)
    run = record.latest(context.scope)
    entries = dict(project_progress.workflow(context).get("reevaluations", {}))
    key = project_progress.key(revise)
    entry = entries.get(key)
    if not entry or entry.get("done_run"):
        findings = legacy(context, record)
        if not findings:
            raise ValueError("再評価する切り替え前の未判断の指摘がありません")
        entry = {"scope": context.scope, "run": run.number, "layers": run.layers, "hashes": run.hashes,
                 "findings": [list(f.key) for f in findings], "actor": actor, "at": project_state.now()}
        entries[key] = entry
        project_progress.save(context, {"reevaluations": entries})
    keys = {tuple(k) for k in entry["findings"]}
    rest = [f for f in legacy(context, record) if f.key in keys]
    if rest:
        review_operations.apply_effect(context, review_operations.record_effect(context, "判断", _rows(context, rest, actor)))
    targets = [t for t in revise.artifacts() if t in run.targets]
    return repair_requests._open(revise, targets, [], actor, "reevaluation", INSTRUCTION)


def pending(context):
    """この修正の回で行う再評価（無ければ None）。"""
    entry = project_progress.workflow(context).get("reevaluations", {}).get(project_progress.key(context))
    if not entry or entry.get("done_run") or entry.get("scope") != context.scope:
        return None
    return entry


def inspector_input(context):
    """検査役に渡す再評価の材料（旧形式の指摘の本文）。"""
    entry = pending(context)
    if entry is None:
        return None
    record = review_contract.read(context)
    findings = []
    for scope, run, number in entry["findings"]:
        f = next((x for r in record.runs for x in r.findings if x.key == (scope, run, number)), None)
        if f is not None:
            findings.append({"scope": scope, "run": run, "number": number, "観点": f.gate, "対象箇所": f.location,
                             "指摘内容": f.description})
    return {"run": entry["run"], "layers": entry["layers"], "findings": findings}


def check_run(context, snapshot, run):
    """scope-check：再評価の回は本文を変えず、再評価の対象の回と同じ層で記録する。"""
    entry = snapshot.get("reevaluation")
    if not entry:
        return
    if run.hashes != entry["hashes"]:
        raise ValueError("再評価の回で本文が変わっています（再評価は本文を変えずに行う）")
    if run.layers != entry["layers"]:
        raise ValueError("再評価の回の実行した層は、再評価の対象の回（%s）と同じにする" % entry["layers"])


def closing_rows(context, record, run, at):
    """再評価の回の記録の後、旧形式の指摘を「再評価の回へ移した」として閉じる判断（system）。"""
    import snapshot_artifacts
    try:
        snapshot = snapshot_artifacts.load(context)
    except (OSError, ValueError):
        return []
    entry = snapshot.get("reevaluation")
    if not entry or snapshot.get("run") != run.number:
        return []
    import finding_rules
    rows = []
    for scope, number_run, number in entry["findings"]:
        f = next((x for r in record.runs for x in r.findings if x.key == (scope, number_run, number)), None)
        if f is None or (f.by_system and f.decision == "対応せず進める"):
            continue
        rows.append({"スコープ": scope, "回数": str(number_run), "指摘番号": str(number), "判断": "対応せず進める",
                     "理由": CLOSE % run.number, "判断者": finding_rules.SYSTEM_ACTOR, "日時": at,
                     "却下区分": "", "今後も同じ扱い": "", "推奨の採用": ""})
    return rows


def finish(context, run):
    """再評価を終えた印（次の回では行わない）。"""
    entries = dict(project_progress.workflow(context).get("reevaluations", {}))
    key = project_progress.key(context)
    if key in entries and not entries[key].get("done_run"):
        entries[key] = dict(entries[key], done_run=run.number)
        project_progress.save(context, {"reevaluations": entries})
