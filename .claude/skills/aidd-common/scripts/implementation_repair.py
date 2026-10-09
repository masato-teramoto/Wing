"""L3 repair fan-out, upstream invalidation and explicit evidence recovery."""
from pathlib import Path

import phase_rules
import implementation_evidence as evidence
import implementation_flows as flows
import implementation_requests as requests
import implementation_store as store
import review_decisions
import review_contract
import review_gate
import task_runtime
import project_progress


def request(context, payload, actor):
    review_decisions.person(actor)
    flows.configuration(context, validate=True)
    if requests.kind(context) != 'final':
        raise ValueError('select implementation repairs from the feature review')
    request_id = store.identifier(payload.get('request_id'))
    path = store.request_path(request_id)
    if Path(context.path(path)).exists():
        value = store.read(context.root, path)
        flows.require_saved(context, value)
        if value.get('selection') != payload or value.get('actor') != actor:
            raise ValueError('repair request ID reused with another response')
        if value['status'] != 'preparing':
            return value
    else:
        review_gate.require(context, payload.get('expected'))
        selected = payload.get('findings')
        if not isinstance(selected, list) or not selected:
            raise ValueError('repair needs actual human-selected findings')
        state = requests.feature_state(context, context.item)
        flows.require_saved(context, state)
        record = review_contract.read(context)
        keys, task_ids = set(), set()
        for row in selected:
            identity = (row.get('scope'), row.get('run'), row.get('number'))
            if row.get('phase') != 'implement' or row.get('scope') != context.scope or identity in keys:
                raise ValueError('repair has duplicated or wrong-scope findings')
            finding = review_decisions.finding(record, *identity)
            ids = row.get('task_ids')
            if (finding is None or finding.resolved or finding.decision != '修正'
                    or not isinstance(row.get('instruction'), str) or not row['instruction'].strip()
                    or not isinstance(ids, list) or not ids or len(ids) != len(set(ids))
                    or any(key not in state['policy']['tasks'] for key in ids)):
                raise ValueError('repair requires a recorded correction and an unambiguous task mapping')
            keys.add(identity)
            task_ids.update(ids)
        plan = task_runtime.freeze(context, context.item)
        value = {'schema': 1, 'request_id': request_id, 'feature': context.item, 'kind': 'repair',
                 'flow_contract': state['flow_contract'],
                 'selection': payload, 'actor': actor, 'findings': selected, 'status': 'preparing',
                 'task_ids': [key for key in plan['order'] if key in task_ids], 'children': {},
                 'plan_ref': state['plan_ref'], 'inputs': state['inputs'], 'policy': state['policy'],
                 'previous': {key: state['completed'].get(key) for key in task_ids}}
        store.write(context.root, path, value)
    # All affected tasks lose completion before any repair child can run.
    state = requests.feature_state(context, context.item)
    for key in value['task_ids']:
        task_runtime.update(context, context.item, request_id + '-invalidate-' + key,
                            {'kind': 'check', 'task_id': key, 'checked': False})
        state['completed'].pop(key, None)
    state['active_request'] = request_id
    store.write(context.root, requests.feature_path(context.item), state)
    project_progress.redo(context, requests.FINAL, context.item)
    value['status'] = 'active'
    store.write(context.root, path, value)
    return value


def resolution_ready(context, scope, run, number):
    record = review_contract.read(context)
    finding = review_decisions.finding(record, scope, run, number)
    if finding is not None and finding.decision == '差戻し':
        # Upstream repairs use the rollback ledger, then rebase/reverify every
        # task. They do not create an implementation-only correction request.
        matching = [b for b in context.blockers() if (b.get('finding') or {}).get('phase') == 'implement'
                    and tuple((b.get('finding') or {}).get(k) for k in ('scope', 'run', 'number')) == (scope, run, number)]
        if not matching or any(b.get('status') != 'upstream-approved' for b in matching):
            raise ValueError('upstream reapproval is required before implementation rollback resolution')
        requests.check_feature_ready(context, context.item)
        import implementation_checks
        implementation_checks.complete_inspection(context)
        return
    directory = Path(context.path(store.BASE + '/requests'))
    matched = []
    for path in directory.glob('*.json'):
        value = store.read(context.root, path.relative_to(context.root).as_posix())
        if value['feature'] != context.item or value.get('kind') != 'repair':
            continue
        if any((row['scope'], row['run'], row['number']) == (scope, run, number) for row in value['findings']):
            matched.append(value)
    if not matched or any(value['status'] != 'completed' for value in matched):
        raise ValueError('all mapped repair task actions must complete before finding resolution')
    requests.check_feature_ready(context, context.item)
    import implementation_checks
    implementation_checks.complete_inspection(context)


def reopen(context, changed):
    """記録入力が変わった Phase 8 の consumer の開き直し（種類ごとに 1 か所、§6.11）。

    計画停止点 implement-plan[S] は計画を出し直す（了承の照合値も変わるので、了承前にタスクは始まらない）。
    実装の証跡を持つ種類は feature の証跡を失効させる。
    """
    if requests.kind(context) in ('plan', 'integration'):
        project_progress.redo(context, context.action, context.item)
    elif requests.kind(context) == 'cross':
        import repair_requests
        repair_requests._redo_cross(context, context.process, '')
    elif requests.kind(context) in phase_rules.EVIDENCE_KINDS:
        invalidate_feature(context, requests.feature_of(context),
                           retire_plan=any(p.endswith('/tasks.md') for p in changed))


def invalidate_feature(context, feature, retire_plan=False):
    """Invalidate one actual consumer without touching other feature evidence."""
    path = requests.feature_path(feature)
    if not Path(context.path(path)).exists():
        return
    state = requests.feature_state(context, feature)
    if not state.get('invalidated'):
        state['invalidated'] = True
        store.write(context.root, path, state)
        project_progress.redo(context, requests.FINAL, feature)
    if retire_plan:
        task_runtime.retire(context, feature)


def invalidate(context, from_phase, item=None):
    base = Path(context.path(store.BASE + '/features'))
    for path in base.glob('*/state.json'):
        feature = path.parent.name
        if item and from_phase >= 7 and feature != item:
            continue
        state = requests.feature_state(context, feature)
        state['invalidated'] = True
        store.write(context.root, requests.feature_path(feature), state)
        project_progress.redo(context, requests.FINAL, feature)
        if from_phase <= 7:
            task_runtime.retire(context, feature)


def rebase(context, payload, actor):
    """Retain old evidence; reverify after an explicitly diagnosed external edit."""
    review_decisions.person(actor)
    if not payload.get('reason'):
        raise ValueError('rebase requires the actual reason for input/code changes')
    route = flows.configuration(context, validate=True)
    flows.legacy_boundary(context, context.item)
    opid = store.identifier(payload.get('operation_id'))
    location = task_runtime.locations(Path(context.path('specs/' + context.item + '/tasks.md')))
    if location and (location[0] / location[1]).exists():
        journal = store.read(*location)
        for operation in journal['operations']:
            if operation['status'] != 'applied' and operation['id'].startswith(opid + '-'):
                task_runtime.update(context, context.item, operation['id'], operation['operation'])
    requests.prerequisites(context, context.item)
    state = requests.feature_state(context, context.item)
    plan = task_runtime.freeze(context, context.item)
    policy = evidence.policy(context, context.item, plan['tasks'])
    request = {'operation_id': opid, 'reason': payload['reason'], 'actor': actor}
    previous = next((entry for entry in state['history'] if entry.get('rebase', {}).get('operation_id') == opid), None)
    if previous:
        if previous['rebase'] != request:
            raise ValueError('rebase operation ID reused')
        return state
    for key in plan['tasks']:
        task_runtime.update(context, context.item, opid + '-' + key, {'kind': 'check', 'task_id': key, 'checked': False})
    state['history'].append({'rebase': request, 'inputs': state['inputs'], 'completed': state['completed'],
                             'plan_ref': state['plan_ref'], 'active_request': state.get('active_request')})
    if state.get('active_request'):
        old = store.read(context.root, store.request_path(state['active_request']))
        old['status'] = 'invalidated'
        store.write(context.root, store.request_path(old['request_id']), old)
    state.update(inputs=requests.input_signature(context, context.item), plan_ref=plan['plan_ref'], policy=policy,
                 flow_contract=route,
                 completed={}, active_request=None, invalidated=False, live_code=evidence.feature_inventory(context, policy))
    project_progress.redo(context, requests.FINAL, context.item)
    store.write(context.root, requests.feature_path(context.item), state)
    return state


def retry(context, payload, instructions=None):
    """Explicitly redo only this task's event after code needs further editing."""
    execution = store.require_execution(context, payload, allow_finished=True)
    flows.require_saved(context, execution)
    operation_id = payload.get('operation_id')
    retry_request = {'payload': payload, 'instructions': instructions}
    if operation_id and operation_id in execution.get('retry_operations', {}):
        if execution['retry_operations'][operation_id] != retry_request:
            raise ValueError('retry operation ID reused with a different instruction')
        return {'execution_id': execution['execution_id'], 'event': context.action}
    if execution.get('event_complete'):
        raise ValueError('completed task edits require an explicit repair or rebase')
    if not payload.get('reason'):
        raise ValueError('retry requires a diagnosis')
    requests.preflight(context)
    project_progress.redo(context, context.action, context.item)
    if context.action == 'implement-authoring-generate':
        project_progress.redo(context, 'implement-authoring-revise', context.item)
        execution['empty_revision_checked'] = False
    execution['end_checked'] = False
    execution.setdefault('retries', []).append(payload['reason'])
    if instructions is not None:
        execution['quality_instructions'] = {**instructions, 'attempt': len(execution['retries'])}
    if operation_id:
        execution.setdefault('retry_operations', {})[operation_id] = retry_request
    store.write(context.root, store.execution_path(execution['execution_id']), execution)
    return {'execution_id': execution['execution_id'], 'event': context.action}


def progress(context, names):
    if names is None:
        return None
    values = {}
    for name in names:
        path = requests.feature_path(name)
        if not Path(context.path(path)).exists():
            values[name] = {'status': 'not_started', 'completed_tasks': []}
            continue
        state = requests.feature_state(context, name)
        status = 'needs_revalidation' if state.get('invalidated') else 'partial'
        try:
            review_contract.check_approved(phase_rules.ExecutionContext(context.root, context.state_path, requests.FINAL, name))
            status = 'approved'
        except (ValueError, OSError, KeyError):
            pass
        values[name] = {'status': status, 'completed_tasks': sorted(state['completed']),
                        'total_tasks': len(state['policy']['tasks'])}
    return values
