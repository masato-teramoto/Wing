"""AIDD review/completion policy; isolated from the execution mechanism."""
from pathlib import Path

import artifacts
import phase_rules
import record_format


def read(context):
    record = record_format.parse(Path(context.gate_record).read_text(encoding="utf-8"))
    if record.phase != context.process:
        raise ValueError("gate record phase differs")
    return record


def scopes(context):
    if context.action == "tasks-gate-run":
        names = [context.selection] if context.selection else [f["name"] for f in context.features()]
        return [record_format.scope_of("feature", name) for name in names] + [context.scope]
    return [context.scope]


def targets_for(context, scope):
    if context.kind and context.kind != 'cross':
        if context.kind != 'final' or scope != context.scope:
            raise ValueError('implementation approval is only available for the whole feature')
        return context.review_targets()
    if record_format.is_feature_scope(scope):
        item = record_format.scope_feature(scope)
        if scope == context.scope:
            return context.review_targets()
        rule = phase_rules.RULES[context.process]
        return phase_rules.ExecutionContext(context.root, context.state_path, rule["generate"], item).review_targets()
    return context.review_targets()


def inspection(context, record, scope):
    run = record.latest(scope)
    targets = targets_for(context, scope)
    if run is None or run.targets != targets:
        raise ValueError("required inspection missing or targets changed: %s" % scope)
    for target in targets:
        if run.hashes[target] != phase_rules.inspection_digest(context, target):
            raise ValueError("artifact changed since inspection: %s" % target)
    return run


def required_layers(context, scope):
    """L3 coverage policy; tasks' aggregate does not replace feature checks."""
    if record_format.is_cross_scope(scope) or (context.action == "tasks-gate-run" and record_format.is_phase_scope(scope)):
        return "②"
    return "①②"


def complete_inspection(context, record, scope):
    # Only this scope's latest, hash-matching run can satisfy coverage. Earlier
    # runs and human acceptance of findings cannot fill missing inspection work.
    run = inspection(context, record, scope)
    if context.is_implementation:
        import implementation_checks
        implementation_checks.complete_inspection(context)
    required = required_layers(context, scope)
    missing = "".join(layer for layer in required if layer not in run.layers)
    if missing:
        raise ValueError("必要な検査が未完了: %s / 回数 %s / 必須 %s / 実行 %s / 未実施 %s"
                         % (scope, run.number, required, run.layers, missing))
    import finding_rules
    unchecked = finding_rules.unchecked_targets(run)
    if unchecked:
        # 形式不備の節は意味検査から外れている。指摘を受容しても未検査は埋まらない（旧版の ① だけの回と同じ扱い）。
        raise ValueError("必要な検査が未完了: %s / 回数 %s / 形式不備で意味検査から外した対象 %s（形式を直して再検査する）"
                         % (scope, run.number, ", ".join(sorted(unchecked))))
    return run


def _lists(request, finding, context):
    key = {"scope": finding.scope, "run": finding.run, "number": finding.number}
    return any(all(row.get(k) == v for k, v in key.items()) and row.get("phase") == context.process
               for row in request.get("findings", []))


def repair_executed(context, finding):
    """この指摘を含む修正の依頼が、修正の回で実行済み（その回の検査を封印した）か。承認済みの依頼も含む。"""
    import repair_requests
    return any((request.get("executed_run") or request.get("consumed")) and _lists(request, finding, context)
               for request in repair_requests.requests_with_history(context))


def repair_covers(context, finding):
    """A pending human-selected repair (same phase, not yet run) or rollback covers this open finding."""
    import project_progress
    key = {"scope": finding.scope, "run": finding.run, "number": finding.number}
    for request in project_progress.workflow(context).get("repairs", {}).values():
        if isinstance(request, dict) and not request.get("consumed") and not request.get("executed_run") and any(
                all(row.get(k) == v for k, v in key.items()) and row.get("phase") == context.process
                for row in request.get("findings", [])):
            return True
    return any(b.get("status") != "resolved" and all((b.get("finding") or {}).get(k) == v for k, v in key.items())
               and (b.get("finding") or {}).get("phase") == context.process for b in context.blockers())


def ready(context, record=None, allow_repair=False):
    """allow_repair: at a -generate end, open 修正/差戻し handed to -revise do not block."""
    record = record or read(context)
    problems = []
    for scope in scopes(context):
        handoff = allow_repair and any(f.is_open and repair_covers(context, f)
                                      for f in record.relevant(scope))
        if handoff:
            inspection(context, record, scope)
        else:
            complete_inspection(context, record, scope)
        for finding in record.relevant(scope):
            if not finding.has_decision:
                problems.append("判断が未記入: " + finding.label())
            elif finding.is_open and allow_repair and repair_covers(context, finding):
                continue
            elif finding.is_open:
                problems.append("未解消: " + finding.label())
            elif finding.needs_reason and not record_format.filled_text(finding.reason):
                problems.append("理由が未記入: " + finding.label())
    if problems:
        raise ValueError(" / ".join(problems))
    return record


def approval_for(record, run, target):
    return next((row for row in reversed(record.approvals)
                 if row["スコープ"] == run.scope and int(row["回数"]) == run.number
                 and row["対象成果物"] == target and row["原本SHA256"] == run.hashes[target]), None)


def phase_approved(context, target):
    """tasks.md など工程承認の対象が、いずれかの工程承認（全件 phase または phase:<その feature>）で
    現在の内容のまま承認されているか。status 欄は証跡にしない。記録は対象の工程（tasks.md なら tasks）のものを読む。"""
    process = Path(target).stem
    owner = phase_rules.ExecutionContext(context.root, context.state_path, phase_rules.RULES[process]["generate"],
                                         target.split("/")[1] if target.startswith("specs/") else "")
    record = read(owner)
    digest = phase_rules.inspection_digest(owner, target)
    name = target.split("/")[1] if target.startswith("specs/") else ""
    for row in reversed(record.approvals):
        if (row["対象成果物"] == target and row["原本SHA256"] == digest and record_format.is_phase_scope(row["スコープ"])
                and record_format.scope_feature(row["スコープ"]) in ("", name)):
            return row
    raise ValueError("required upstream artifact is missing or not approved: " + target)


def check_approved(context, require_all=True, allow_repair=False):
    if context.is_cross:
        record = ready(context, allow_repair=allow_repair)
        if require_all:
            import review_decisions
            # ゲート自身の完了判定は、現在の回の人の確認を求める（§6.4）。「古い」を止めない緩い判定（check_cross）は
            # 下流の前提確認（prerequisites・implementation_requests）だけに使う（F29）。
            review_decisions._check_cross(context, context.process, context.selection)
        return record
    record = ready(context, allow_repair=allow_repair)
    run = inspection(context, record, context.scope)
    if context.kind:
        if require_all and any(approval_for(record, run, target) is None for target in context.review_targets()):
            raise ValueError('feature implementation needs current human approval evidence')
        return record
    for target in context.approval_targets():
        status = (artifacts.fields(context.path(target)) or {}).get("status")
        if require_all and status != "approved":
            raise ValueError("artifact is not approved: %s" % target)
        if status == "approved" and approval_for(record, run, target) is None:
            raise ValueError("approval evidence missing for current target/run: %s" % target)
    return record
