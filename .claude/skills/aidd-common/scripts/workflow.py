"""Host-invoked L3 policy actions; L0 remains the only execution dispatcher.

Use advance/submit/respond to sequence preflight, public L0 calls and reports.
Human actions record received answers; this program never produces them.
"""
import argparse
import json
from pathlib import Path

import aidd_paths
import artifacts
import feature_manifest
import findings_stage
import project_state
import repair_actions
import review_actions
import snapshot_artifacts
import workflow_state
import review_gate


def read_payload(value):
    data = json.loads(Path(value).read_text(encoding="utf-8")) if value else {}
    if not isinstance(data, dict):
        raise ValueError("action payload must be an object")
    return data


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", default=".")
    parser.add_argument("--state")
    parser.add_argument("--event", help="event name; optional for advance when --call names a flow")
    parser.add_argument("--item", default="")
    parser.add_argument("--payload", help="UTF-8 JSON with the actual response or selected repair")
    parser.add_argument("--actor", default="")
    parser.add_argument("--call", help="Actual flow/event call, if different from --event")
    parser.add_argument("action", choices=("implement-select", "implement-next", "implement-note", "implement-check", "implement-repair", "implement-rebase", "implement-retry", "advance", "submit", "respond", "review-context", "migration-review", "audit", "preflight", "context", "progress", "result", "complete", "completion", "decision", "resolve", "approve", "accept-plan", "wait", "answer", "repair", "reopen", "upstream-approved", "resolve-rollback"))
    args = parser.parse_args()
    try:
        event = args.event
        if not event and args.call in aidd_paths.PROCESS_OF:
            event = args.call  # a single event (plan, cross gate) called directly
        if not event:
            first = [rule for rule in sorted(aidd_paths.RULES.values(), key=lambda r: r["number"]) if rule["call"] == args.call]
            if args.action != "advance":
                raise ValueError("--event is required (or --call <flow|event> with advance)")
            if first and first[0]['number'] != 8:
                event = first[0]["generate"]
            else:
                import implementation_flows
                probe = aidd_paths.Context(args.root, args.state, 'implement-gate-run', args.item)
                event = implementation_flows.entry_event(probe, args.call)
                if not event:
                    raise ValueError('unknown workflow flow: ' + str(args.call))
        context = aidd_paths.Context(args.root, args.state, event, args.item)
        payload = read_payload(args.payload)
        if args.call:
            payload = {**payload,'call':args.call}
        output = execute(context, args.action, payload, args.actor)
        print(json.dumps(output, ensure_ascii=False, indent=2))
        return 0 if output["status"] == "ok" else 1
    except (ValueError, OSError, KeyError, TypeError) as error:
        output = {"status": "fail", "error": str(error)}
        if isinstance(error,review_gate.ActionRejected):
            output.update(error_code='action_not_allowed',pending=error.pending,next_action=error.next_action,operation_applied=False)
        print(json.dumps(output, ensure_ascii=False))
        return 1


def execute(context, action, data, actor):
    with context.locked():
        import host_session
        import review_operations
        host_session.ensure_idle(context,data.get('operation_id') if action in ('submit','respond') else None)
        review_operations.ensure_idle(context,data.get('operation_id'))
        return _execute(context,action,data,actor)


def _execute(context, action, data, actor):
    result = dispatch(context, action, data, actor)
    output = {"status": "ok", "action": action, "result": result}
    if action in ('advance','submit','respond','implement-next'):
        if result.get('status') == 'fail':
            output['status'] = 'fail'
        if result.get('operation_applied'):
            output['operation_applied'] = True
    if action in ("approve", "complete"):
        # The primary action has committed. Display failure must not request
        # replay of an approval, completion certificate or L0 report.
        output["operation_applied"] = True
        output["progress"] = workflow_state.progress(context)
    elif action == "progress":
        if result["status"] not in ("ready", "partial") or not result["cache_saved"]:
            output["status"] = "fail"
    return output


def dispatch(context, action, data, actor):
    if action.startswith('implement-'):
        if context.process != 'implement':
            raise ValueError('implementation action requires a Phase 8 event')
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
        }
        return actions[action]()
    if action == 'review-context':
        with context.locked():
            return review_gate.current(context,data.get('call'))
    if action in ('advance','submit','respond'):
        import host_session
        return host_session.advance(context,data.get('call')) if action=='advance' else host_session.operate(context,action,data,actor)
    if action == "migration-review":
        import migrate_state
        return migrate_state.reconcile(context, data, actor)
    if action == "audit":
        return workflow_state.audit(context)
    if action in ("complete", "completion"):
        import completion
        return completion.record(context, data.get("call")) if action == "complete" else completion.check(context)
    if action == "preflight":
        return workflow_state.preflight(context)
    if action == "progress":
        return workflow_state.progress(context)
    if action == "result":
        import authoring_results
        return authoring_results.save(context, data)
    if action == "context":
        if context.process == 'implement' and context.event != 'implement-gate-run':
            import implementation_requests
            return implementation_requests.task_context(context)
        result = {"event": context.event, "item": context.item, "scope": context.scope,
                  "targets": context.artifacts(), "upstream": context.upstream(), "gate_record_path": context.gate_record}
        result["authoring_inputs"] = context.authoring_inputs()
        if context.process == 'implement':
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
        result["questions"] = workflow_state.workflow(context).get("waiting", {}).get(workflow_state.key(context))
        if context.event == aidd_paths.RULES[context.process]["repair"]:
            # The revise event always runs: null means nothing was selected (edit nothing).
            result["repair"] = repair_actions.pending(context)
        if path.exists():
            result["inspection_path"] = str(path).replace(".snapshot.json", ".inspection.md")
        return result
    if action != "wait":
        review_actions.person(actor)
    if action == "decision":
        return review_actions.decision(context, data["scope"], data["run"], data["number"], data["decision"], data.get("reason", ""), actor,
                                       expected=data.get('expected'),operation_id=data.get('operation_id'))
    elif action == "resolve":
        # A rollback cannot be resolved until its upstream was reapproved.
        for blocker in context.blockers():
            selected = blocker.get("finding") or {}
            if all(selected.get(k) == data.get(k) for k in ("scope", "run", "number")) and blocker.get("status") == "open":
                raise ValueError("rollback needs upstream reapproval before resolution")
        return review_actions.resolve(context, data["scope"], data["run"], data["number"], actor,
                                      expected=data.get('expected'),operation_id=data.get('operation_id'))
    elif action == "approve":
        return review_actions.approve(context, actor,expected=data.get('expected'),operation_id=data.get('operation_id'))
    elif action == "accept-plan":
        plans = dict(workflow_state.workflow(context).get("accepted_plans", {}))
        plans[context.process] = {"actor": actor, "at": project_state.now(), "note": data.get("note", ""),
                                  "manifest": feature_manifest.source_hash(context.root) if context.phase >= 4 else None}
        workflow_state.save(context, {"accepted_plans": plans})
    elif action in ("wait", "answer"):
        if context.process == 'implement' and context.event != 'implement-gate-run':
            import implementation_store
            implementation_store.require_execution(context, data)
        waiting = dict(workflow_state.workflow(context).get("waiting", {}))
        if action == "wait":
            if not data.get("questions") and not data.get("reason") and not data.get("return_candidates"):
                raise ValueError("waiting requires questions, return candidates or a reason")
            waiting[workflow_state.key(context)] = {**data, "actor": actor, "at": project_state.now(), "status": "waiting"}
        else:
            entry = waiting.get(workflow_state.key(context))
            if (context.process == 'implement' and entry
                    and entry.get('execution_id') != data.get('execution_id')):
                raise ValueError('questions belong to an earlier execution')
            if not entry or not data.get("answers"):
                raise ValueError("recorded questions and actual answers are required")
            if any((c or {}).get("owner") == "rfp" for c in entry.get("return_candidates") or []):
                raise ValueError("RFP の不備はフロー外で RFP を改訂して解消します（回答だけでは進めません）。.aidd/rfp/ を改訂してから再実行してください")
            entry.update(answers=data["answers"], answered_by=actor, answered_at=project_state.now(), status="answered")
        workflow_state.save(context, {"waiting": waiting})
    elif action == "repair":
        return repair_actions.request(context, data, actor)
    elif action == "reopen":
        return repair_actions.reopen(context, data.get("targets") or [], data.get("instruction", ""), "reopen", actor,
                                     resume_event=data.get("resume_event", ""), resume_item=data.get("resume_item", ""))
    elif action == "upstream-approved":
        return repair_actions.upstream_approved(context, data["blocker"], actor)
    elif action == "resolve-rollback":
        repair_actions.complete_rollback(context, data["blocker"], actor)
    return {"event": context.event, "item": context.item}


if __name__ == "__main__":
    raise SystemExit(main())
