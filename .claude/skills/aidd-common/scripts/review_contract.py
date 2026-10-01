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
        return ["feature:" + f["name"] for f in context.features()] + ["phase"]
    return [context.scope]


def targets_for(context, scope):
    if context.process == 'implement':
        if context.action != 'implement-gate-run' or scope != context.scope:
            raise ValueError('implementation approval is only available for the whole feature')
        return context.review_targets()
    if scope.startswith("feature:"):
        item = scope[len("feature:"):]
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
    if scope == "cross" or (context.action == "tasks-gate-run" and scope == "phase"):
        return "②"
    return "①②"


def complete_inspection(context, record, scope):
    # Only this scope's latest, hash-matching run can satisfy coverage. Earlier
    # runs and human acceptance of findings cannot fill missing inspection work.
    run = inspection(context, record, scope)
    if context.process == 'implement':
        import implementation_checks
        implementation_checks.complete_inspection(context)
    required = required_layers(context, scope)
    missing = "".join(layer for layer in required if layer not in run.layers)
    if missing:
        raise ValueError("必要な検査が未完了: %s / 回数 %s / 必須 %s / 実行 %s / 未実施 %s"
                         % (scope, run.number, required, run.layers, missing))
    return run


def repair_covers(context, finding):
    """A pending human-selected repair (same phase) or rollback covers this open finding."""
    import project_progress
    key = {"scope": finding.scope, "run": finding.run, "number": finding.number}
    for request in project_progress.workflow(context).get("repairs", {}).values():
        if isinstance(request, dict) and not request.get("consumed") and any(
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


def check_approved(context, require_all=True, allow_repair=False):
    if context.is_cross:
        record = ready(context, allow_repair=allow_repair)
        if require_all:
            import review_decisions
            review_decisions.check_cross(context, context.process)
        return record
    record = ready(context, allow_repair=allow_repair)
    run = inspection(context, record, context.scope)
    if context.process == 'implement':
        if require_all and any(approval_for(record, run, target) is None for target in context.review_targets()):
            raise ValueError('feature implementation needs current human approval evidence')
        return record
    for target in context.review_targets():
        status = (artifacts.fields(context.path(target)) or {}).get("status")
        if require_all and status != "approved":
            raise ValueError("artifact is not approved: %s" % target)
        if status == "approved" and approval_for(record, run, target) is None:
            raise ValueError("approval evidence missing for current target/run: %s" % target)
    return record
