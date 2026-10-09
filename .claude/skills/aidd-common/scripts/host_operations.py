"""Host-invoked L3 policy operations; L0 remains the only execution dispatcher.

The host agent reaches this through the entry (`aidd_entry.py`, which resolves the command with
L0's CommandResolver). advance / submit / respond run L0's host (`bin/host.py`) in-process with
L3's rules passed as its stage_runner (host_session.run_stage); there are no hooks.
Human actions record received answers; this program never produces them.
"""
import l0  # noqa: F401  L0 の枠組みを import できるようにする
import argparse
import json
from pathlib import Path

import phase_rules
import artifacts
import feature_manifest
import findings_stage
import project_state
import repair_requests
import review_decisions
import snapshot_artifacts
import project_progress
import review_gate


def read_payload(value):
    data = json.loads(Path(value).read_text(encoding="utf-8")) if value else {}
    if not isinstance(data, dict):
        raise ValueError("action payload must be an object")
    return data


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", default=".")
    parser.add_argument("--state")
    parser.add_argument("--action", help="action name; optional for advance when --call names a flow")
    parser.add_argument("--item", default="")
    parser.add_argument("--payload", help="UTF-8 JSON with the actual response or selected repair")
    parser.add_argument("--actor", default="")
    parser.add_argument("--call", help="Actual flow/action call, if different from --action")
    parser.add_argument("operation", choices=("implement-select", "implement-next", "implement-note", "implement-check", "implement-repair", "implement-rebase", "implement-retry", "implement-reverify", "implement-repin", "advance", "submit", "respond", "review-context", "migration-review", "audit", "preflight", "context", "progress", "metrics", "result", "complete", "completion", "decision", "resolve", "approve", "accept-plan", "select-scope", "switch-mode", "wait", "answer", "repair", "reopen", "upstream-approved", "resolve-rollback"))
    args = parser.parse_args(argv)
    try:
        action = args.action
        payload = read_payload(args.payload)
        if not action and args.operation != "advance":
            if args.call in phase_rules.PROCESS_OF:
                action = args.call  # a single action (plan, cross gate) called directly
            else:
                raise ValueError("--action is required (or --call <flow|action> with advance)")
        context = phase_rules.ExecutionContext(args.root, args.state, action, args.item)
        if args.call:
            payload = {**payload,'call':args.call}
        output = execute(context, args.operation, payload, args.actor)
        print(json.dumps(output, ensure_ascii=False, indent=2))
        return 0 if output["status"] == "ok" else 1
    except (ValueError, OSError, KeyError, TypeError) as error:
        output = {"status": "fail", "error": str(error)}
        if isinstance(error,review_gate.OperationRejected):
            output.update(error_code='action_not_allowed',pending=error.pending,next_action=error.next_action,operation_applied=False)
        print(json.dumps(output, ensure_ascii=False))
        return 1


def execute(context, operation, data, actor):
    if operation in ('advance', 'submit', 'respond'):
        # L0's host holds the lock, the operation journal and the idle checks.
        return _execute(context, operation, data, actor)
    with context.locked():
        import host_session
        import review_operations
        host_session.ensure_idle(context)
        review_operations.ensure_idle(context,data.get('operation_id'))
        return _execute(context,operation,data,actor)


def _execute(context, operation, data, actor):
    result = dispatch(context, operation, data, actor)
    output = {"status": "ok", "action": operation, "result": result}
    if operation in ('advance','submit','respond','implement-next'):
        if result.get('status') == 'fail':
            output['status'] = 'fail'
        if result.get('operation_applied'):
            output['operation_applied'] = True
    if operation in ("approve", "complete"):
        # The primary action has committed. Display failure must not request
        # replay of an approval, completion certificate or L0 report.
        output["operation_applied"] = True
        output["progress"] = project_progress.progress(context)
    elif operation == "progress":
        if result["status"] not in ("ready", "partial") or not result["cache_saved"]:
            output["status"] = "fail"
    return output


def dispatch(context, operation, data, actor):
    if operation.startswith('implement-'):
        if not context.kind:
            raise ValueError('implementation operation requires a Phase 8 action')
        import implementation_requests as implementation
        import implementation_repair
        import implementation_checks
        actions = {
            'implement-select': lambda: implementation.select(context, data),
            'implement-next': lambda: implementation.next_task(context, data['request_id']),
            'implement-note': lambda: implementation.note(context, data),
            'implement-check': lambda: implementation_checks.task(context, data),
            'implement-repair': lambda: implementation_repair.request(context, data, actor),
            'implement-rebase': lambda: implementation_repair.rebase(context, data, actor),
            'implement-retry': lambda: implementation_repair.retry(context, data),
            'implement-reverify': lambda: __import__('implementation_reverify').reverify(context, data, actor),
            'implement-repin': lambda: __import__('implementation_reverify').repin(context, data, actor),
        }
        return actions[operation]()
    if operation == 'review-context':
        with context.locked():
            return review_gate.current(context,data.get('call'))
    if operation in ('advance','submit','respond'):
        import host_session
        return host_session.advance(context,data.get('call')) if operation=='advance' else host_session.operate(context,operation,data,actor)
    if operation == "migration-review":
        import migrate_state
        return migrate_state.reconcile(context, data, actor)
    if operation == "audit":
        return project_progress.audit(context)
    if operation in ("complete", "completion"):
        import completion
        return completion.record(context, data.get("call")) if operation == "complete" else completion.check(context)
    if operation == "preflight":
        return project_progress.preflight(context)
    if operation == "progress":
        return project_progress.progress(context)
    if operation == "metrics":
        import review_metrics
        return {"metrics": review_metrics.collect(context.root)}
    if operation == "result":
        import authoring_results
        return authoring_results.save(context, data)
    if operation == "context":
        if context.kind == 'task':
            import implementation_requests
            # The task-level review emits get their context from the record their preparing gate published (gate_exchange).
            return implementation_requests.task_context(context)
        import prerequisites
        # targets: what authoring writes (every output). review_targets: what the inspection
        # gate reviews and a human approves (its target_review). unreviewed_inputs: upstream
        # files left out of their own inspection; they are drafts that may still be read.
        result = {"event": context.action, "item": context.item, "scope": context.scope,
                  "targets": context.artifacts(), "review_targets": context.review_targets(),
                  "upstream": context.upstream(), "unreviewed_inputs": prerequisites.unreviewed_inputs(context),
                  "gate_record_path": context.gate_record}
        result["authoring_inputs"] = context.authoring_inputs()
        if context.kind == 'cross':
            import implementation_project
            result.update(implementation_project.cross_context(context))
        if context.kind == 'final':
            import implementation_evidence
            import implementation_checks
            result.update(profile='implementation-code-v1', implementation=implementation_evidence.verify_review(context),
                          tool_results_path=implementation_checks.final_path(context), required_aspects=implementation_evidence.ASPECTS)
            tools = implementation_checks.validate_final(context)
            result.update(tool_results_sha256=implementation_checks.tools_digest(context), report_summary=tools['summary']['path'])
        path = Path(snapshot_artifacts.snapshot_path(context))
        if path.exists():
            result.update(snapshot_path=str(path), snapshot=snapshot_artifacts.load(context),
                          findings_path=findings_stage.stage_path(context), findings=findings_stage.read(context))
        result["questions"] = project_progress.workflow(context).get("waiting", {}).get(project_progress.key(context))
        if not context.kind:
            # 検査の前提（指摘の共通ルール・人が確定した回答・却下から学んだ扱い・前回までの指摘）。
            import review_premises
            import reevaluation
            result.update(review_premises.collect(context))
            if context.selection:
                # 横断確認の部分集合モード（L4-1、§6.3 2c）：比較集合と、U のうち未収録の feature を渡す。
                scope_features = context.comparison_features()
                result.update(selection=context.selection, scope_features=scope_features,
                              excluded_features=[e["name"] for e in context.features() if e["name"] not in scope_features])
            legacy = reevaluation.inspector_input(context)
            if legacy:
                # この修正の回は再評価：検査役は旧形式の指摘だけを finding-reevaluation の手順で見直す
                result["reevaluation"] = legacy
        if context.action == phase_rules.RULES[context.process]["repair"]:
            # The entry Skill calls the revise action for a pending repair: null means nothing was selected.
            result["repair"] = repair_requests.pending(context)
        if path.exists():
            result["inspection_path"] = str(path).replace(".snapshot.json", ".inspection.md")
        return result
    if operation != "wait":
        review_decisions.person(actor)
    if operation == "decision":
        return review_decisions.decision(context, data["scope"], data["run"], data["number"], data["decision"], data.get("reason", ""), actor,
                                       expected=data.get('expected'),operation_id=data.get('operation_id'),
                                       category=data.get('category', ''), learn=data.get('learn', False), adopted=data.get('adopted', ''))
    elif operation == "resolve":
        # A rollback cannot be resolved until its upstream was reapproved.
        for blocker in context.blockers():
            selected = blocker.get("finding") or {}
            if (selected.get("phase") == context.process
                    and all(selected.get(k) == data.get(k) for k in ("scope", "run", "number"))
                    and blocker.get("status") == "open"):
                raise ValueError("rollback needs upstream reapproval before resolution")
        return review_decisions.resolve(context, data["scope"], data["run"], data["number"], actor,
                                      expected=data.get('expected'),operation_id=data.get('operation_id'))
    elif operation == "approve":
        return review_decisions.approve(context, actor,expected=data.get('expected'),operation_id=data.get('operation_id'))
    elif operation == "accept-plan":
        import feature_scope
        feature_scope.accept_plan(context, data, actor)
    elif operation == "select-scope":
        import feature_scope
        return feature_scope.select(context, data.get("feature"), actor, data.get("note", ""))
    elif operation == "switch-mode":
        import mode_switch
        if not data.get("confirm"):
            return mode_switch.preview(context)
        return mode_switch.switch(context, data, actor)
    elif operation in ("wait", "answer"):
        if context.kind == 'task':
            import implementation_store
            implementation_store.require_execution(context, data)
        waiting = dict(project_progress.workflow(context).get("waiting", {}))
        if operation == "wait":
            if not data.get("questions") and not data.get("reason") and not data.get("return_candidates"):
                raise ValueError("waiting requires questions, return candidates or a reason")
            waiting[project_progress.key(context)] = {**data, "actor": actor, "at": project_state.now(), "status": "waiting"}
        else:
            entry = waiting.get(project_progress.key(context))
            if (context.is_implementation and entry
                    and entry.get('execution_id') != data.get('execution_id')):
                raise ValueError('questions belong to an earlier execution')
            if not entry or not data.get("answers"):
                raise ValueError("recorded questions and actual answers are required")
            if any((c or {}).get("owner") == "rfp" for c in entry.get("return_candidates") or []):
                raise ValueError("RFP の不備はフロー外で RFP を改訂して解消します（回答だけでは進めません）。.aidd/rfp/ を改訂してから再実行してください")
            entry.update(answers=data["answers"], answered_by=actor, answered_at=project_state.now(), status="answered")
        project_progress.save(context, {"waiting": waiting})
    elif operation == "repair":
        return repair_requests.request(context, data, actor)
    elif operation == "reopen":
        return repair_requests.reopen(context, data.get("targets") or [], data.get("instruction", ""), "reopen", actor,
                                     resume_action=data.get("resume_event", ""), resume_item=data.get("resume_item", ""))
    elif operation == "upstream-approved":
        return repair_requests.upstream_approved(context, data["blocker"], actor)
    elif operation == "resolve-rollback":
        repair_requests.complete_rollback(context, data["blocker"], actor)
    return {"event": context.action, "item": context.item}


if __name__ == "__main__":
    raise SystemExit(main())
