"""L3 selection and per-task execution. L0 owns each start/run/end traversal."""
from pathlib import Path
import copy

import aidd_paths
import artifacts
import implementation_evidence as evidence
import implementation_flows as flows
import implementation_store as store
import project_state
import task_runtime

TASK_EVENTS = ('implement-authoring-generate', 'implement-authoring-revise')
FINAL = 'implement-gate-run'


def feature_path(feature):
    return store.BASE + '/features/' + store.identifier(feature) + '/state.json'


def feature_state(context, feature):
    return store.read(context.root, feature_path(feature))


def feature_of(context):
    return store.current_execution(context)['feature'] if context.event in TASK_EVENTS else store.identifier(context.item)


def upstream(context, feature):
    return list(dict.fromkeys(aidd_paths.RULES['tasks']['upstream'] + [
        'specs/' + feature + '/' + name + '.md' for name in ('requirements', 'design', 'tasks')]))


def input_signature(context, feature):
    values = {p: artifacts.protected_digest(context.path(p)) for p in upstream(context, feature)}
    values[evidence.config_path(feature)] = store.digest(Path(context.path(evidence.config_path(feature))).read_bytes())
    owner = aidd_paths.Context(context.root, context.state_path, aidd_paths.RULES['tasks']['generate'], feature)
    for dependency in owner.feature()['depends_on']:
        path = evidence.review_path(dependency)
        values[path] = store.digest(Path(context.path(path)).read_bytes())
    return values


def prerequisites(context, feature):
    import prerequisites as checks
    import review_contract
    import review_actions
    checks.approved(context, upstream(context, feature))
    checks.blockers(context)
    review_actions.check_cross(context, 'requirements')
    review_actions.check_cross(context, 'design')
    review_contract.check_approved(aidd_paths.Context(context.root, context.state_path, 'tasks-gate-run'))
    feature_context = aidd_paths.Context(context.root, context.state_path, aidd_paths.RULES['tasks']['generate'], feature)
    for dependency in feature_context.feature()['depends_on']:
        review_contract.check_approved(aidd_paths.Context(context.root, context.state_path, FINAL, dependency))


def select(context, payload):
    feature = store.identifier(context.item)
    route = flows.configuration(context, validate=True)
    flows.legacy_boundary(context, feature)
    request_id = store.identifier(payload.get('request_id'))
    request_file = store.request_path(request_id)
    if Path(context.path(request_file)).exists():
        previous = store.read(context.root, request_file)
        flows.require_saved(context, previous)
        if previous['selection'] != payload or previous['feature'] != feature:
            raise ValueError('request ID was reused with another selection')
        if previous['status'] == 'active':
            path = feature_path(feature)
            state = feature_state(context, feature) if Path(context.path(path)).exists() else previous['feature_seed']
            active = state.get('active_request')
            if active and active != request_id and store.read(context.root, store.request_path(active))['status'] == 'active':
                raise ValueError('another parent is active')
            state['active_request'] = request_id
            store.write(context.root, path, state)
        return previous
    prerequisites(context, feature)
    plan = task_runtime.freeze(context, feature)
    policy = evidence.policy(context, feature, plan['tasks'])
    inputs = input_signature(context, feature)
    path = feature_path(feature)
    if Path(context.path(path)).exists():
        state = feature_state(context, feature)
        flows.require_saved(context, state)
        if state.get('invalidated') or state['inputs'] != inputs or state['plan_ref'] != plan['plan_ref']:
            raise ValueError('implementation inputs changed; rebase after upstream approval before selecting tasks')
        if state['live_code'] != evidence.feature_inventory(context, policy):
            raise ValueError('code changed outside recorded task execution; reverify/rebase explicitly')
        active = state.get('active_request')
        if active and store.read(context.root, store.request_path(active))['status'] == 'active':
            raise ValueError('resume the current parent request: ' + active)
        validate_completed(context, feature, state)
    else:
        state = {'schema': 1, 'feature': feature, 'inputs': inputs, 'plan_ref': plan['plan_ref'], 'policy': policy,
                 'completed': {}, 'live_code': evidence.feature_inventory(context, policy), 'history': []}
    selected = payload.get('task_ids')
    if selected is None:
        selected = [key for key in plan['order'] if key not in state['completed']]
    if (not isinstance(selected, list) or any(not isinstance(key, str) or key not in plan['tasks'] for key in selected)
            or len(selected) != len(set(selected))):
        raise ValueError('select known, unique integer task ID strings')
    for key in selected:
        missing = set(plan['tasks'][key]['depends_on']) - set(selected) - set(state['completed'])
        if missing:
            raise ValueError('select unfinished dependency tasks first: ' + ', '.join(sorted(missing)))
    state['flow_contract'] = route
    request = {'schema': 1, 'request_id': request_id, 'feature': feature, 'selection': payload,
               'flow_contract': route,
               'task_ids': [key for key in plan['order'] if key in selected], 'plan_ref': plan['plan_ref'],
               'inputs': inputs, 'policy': policy, 'children': {}, 'status': 'active', 'kind': 'generate',
               'feature_seed': copy.deepcopy(state)}
    store.write(context.root, request_file, request)
    state['active_request'] = request_id
    store.write(context.root, path, state)
    return request


def preflight(context):
    feature = feature_of(context)
    state = feature_state(context, feature)
    flows.require_saved(context, state)
    if context.event in TASK_EVENTS:
        flows.require_saved(context, store.read_execution(context))
    if context.event in TASK_EVENTS:
        # Recover only the exact completion edit already authorized by this event.
        path = Path(context.path('specs/' + feature + '/tasks.md'))
        location = task_runtime.locations(path)
        if location and (location[0] / location[1]).exists():
            journal = store.read(*location)
            pending = [op for op in journal['operations'] if op['status'] != 'applied']
            if pending and pending[0]['id'] == store.read_execution(context)['execution_id'] + '-complete':
                task_runtime.update(context, feature, pending[0]['id'], pending[0]['operation'])
    prerequisites(context, feature)
    state = feature_state(context, feature)
    if state.get('invalidated') or state['inputs'] != input_signature(context, feature):
        raise ValueError('implementation input version changed; explicit rebase is required')
    if context.event in TASK_EVENTS:
        execution = store.read_execution(context)
        parent = store.read(context.root, store.request_path(execution['request_id']))
        if parent['status'] not in ('active', 'completed') or state.get('active_request') != execution['request_id']:
            raise ValueError('task execution belongs to an inactive parent')
        if (execution['task_id'] not in parent['task_ids'] or execution['plan_ref'] != state['plan_ref']
                or execution['policy'] != state['policy'] or execution['inputs'] != state['inputs']):
            raise ValueError('task execution differs from its frozen selection/plan')
        if parent['children'].get(execution['task_id']) != execution['execution_id']:
            raise ValueError('execution is not the selected child')
        if not execution.get('activated'):
            raise ValueError('resume implementation request activation first')
        if store.empty_revision(context, execution):
            if not execution.get('end_checked'):
                raise ValueError('generation must finish before the empty revision')
        elif context.event == 'implement-authoring-revise' and not execution.get('repair_findings'):
            raise ValueError('repair requires an actual nonempty human correction request')
        evidence.check_scope(context, execution)
        return execution
    return state


def next_task(context, request_id):
    import host_session
    request = store.read(context.root, store.request_path(request_id))
    flows.configuration(context, validate=True)
    flows.require_saved(context, request)
    flows.legacy_boundary(context, request['feature'])
    if request['status'] not in ('active', 'completed'):
        raise ValueError('parent request is not ready; resume its preparation or rebase')
    feature = request['feature']
    if context.item != feature:
        raise ValueError('parent request belongs to another feature')
    state = feature_state(context, feature)
    # Let the current child's preflight recover a prepared end-gate edit before
    # the parent checks Phase 7 approval through that same task journal.
    for key in request['task_ids']:
        child = request['children'].get(key)
        if child:
            execution = store.read(context.root, store.execution_path(child))
            if not execution.get('event_complete'):
                return advance_execution(context, execution)
        elif key not in state['completed'] or request['kind'] != 'generate':
            break
    prerequisites(context, feature)
    if state.get('invalidated') or state['inputs'] != input_signature(context, feature):
        raise ValueError('parent inputs changed; rebase after upstream approval')
    for key in request['task_ids']:
        child = request['children'].get(key)
        if child:
            execution = store.read(context.root, store.execution_path(child))
            if execution.get('event_complete'):
                continue
            return advance_execution(context, execution)
        if key in state['completed'] and request['kind'] == 'generate':
            continue
        if state['live_code'] != evidence.feature_inventory(context, request['policy']):
            raise ValueError('code changed between tasks; do not silently capture a new baseline')
        child = 'exec-' + store.fingerprint({'request_id': request_id, 'task_id': key})[:32]
        event = 'implement-authoring-revise' if request['kind'] == 'repair' else 'implement-authoring-generate'
        path = store.execution_path(child)
        if Path(context.path(path)).exists():
            execution = store.read(context.root, path)
        else:
            execution = {'schema': 1, 'execution_id': child, 'request_id': request_id, 'feature': feature,
                         'flow_contract': request['flow_contract'],
                         'task_item': request['previous'][key]['task_item'] if request['kind'] == 'repair' else child,
                         'task_id': key, 'event': event, 'plan_ref': state['plan_ref'], 'inputs': state['inputs'],
                         'policy': request['policy'], 'allowed_paths': request['policy']['tasks'][key]['allowed_paths'],
                         'baseline': evidence.inventory(context, request['policy']),
                         'protected': evidence.inventory(context, request['policy'], protected=True),
                         'repair_findings': [f for f in request.get('findings', []) if key in f['task_ids']],
                         'previous_execution': request.get('previous', {}).get(key), 'event_complete': False}
            store.write(context.root, path, execution)
        request['children'][key] = child
        store.write(context.root, store.request_path(request_id), request)
        return advance_execution(context, execution)
    request['status'] = 'completed'
    store.write(context.root, store.request_path(request_id), request)
    if len(state['completed']) != len(state['policy']['tasks']):
        return {'status': 'partial', 'request_id': request_id, 'completed': sorted(state['completed']),
                'remaining': sorted(set(state['policy']['tasks']) - set(state['completed'])), 'approved': False}
    final_context = aidd_paths.Context(context.root, context.state_path, FINAL, feature)
    # L0 keeps completed units; a changed feature must explicitly redo final inspection.
    return host_session.advance(final_context)


def advance_execution(context, execution):
    """Journal activation before dispatch; a repair invalidates only revision units."""
    import host_session
    import runtime_client
    import workflow_state
    child = aidd_paths.Context(context.root, context.state_path, execution['event'], execution['task_item'])
    if not execution.get('activated'):
        state = feature_state(context, execution['feature'])
        if state.get('active_request') != execution['request_id'] or state.get('invalidated'):
            raise ValueError('activation belongs to an inactive parent')
        if execution['event'] == 'implement-authoring-revise':
            if not execution.get('activation_prepared'):
                previous = store.current_execution(child)
                proof = execution['previous_execution']
                if (previous['execution_id'] != proof['execution_id'] or not previous.get('event_complete')
                        or runtime_client.invoke(child, 'status')['pending'] is not None):
                    raise ValueError('repair requires a completed task flow on the same item')
                execution['activation_prepared'] = True
                store.write(context.root, store.execution_path(execution['execution_id']), execution)
            # Until activated is durable no skill or helper can run, so replaying
            # this redo after a crash cannot discard new work.
            workflow_state.redo(child, child.event, child.item)
        binding = {'schema': 1, **{key: execution[key] for key in
                   ('task_item', 'execution_id', 'feature', 'task_id', 'plan_ref')}}
        store.write(context.root, store.item_path(child.item), binding)
        execution['activated'] = True
        store.write(context.root, store.execution_path(execution['execution_id']), execution)
    return host_session.advance(child)


def task_context(context):
    execution = preflight(context)
    task = task_runtime.freeze(context, execution['feature'])['tasks'][execution['task_id']]
    identity = {key: execution[key] for key in ('execution_id', 'request_id', 'feature', 'task_id', 'event', 'plan_ref', 'allowed_paths', 'repair_findings', 'previous_execution')}
    noop = store.empty_revision(context, execution)
    waiting = context.state().get('workflow', {}).get('waiting', {}).get(context.event + '[' + context.item + ']')
    if waiting and waiting.get('execution_id') != execution['execution_id']:
        waiting = None
    if noop:
        identity['allowed_paths'] = []
    return {**identity, 'event': context.event, 'task_item': context.item, 'noop': noop, 'task': task, 'upstream': upstream(context, execution['feature']),
            'authoring_inputs': upstream(context, execution['feature']),
            'questions': waiting,
            'execution_path': store.execution_path(execution['execution_id']),
            'verification_plan': execution['policy'],
            'targets': [] if noop else execution['allowed_paths'], 'profile': 'implementation-task'}


def validate_result(context, data):
    execution = preflight(context)
    if 'task_ids' in data or any(data.get(key) != execution[key] for key in ('request_id', 'execution_id', 'task_id', 'feature')):
        raise ValueError('Skill result must identify exactly its single task and execution')
    if data.get('status') not in ('completed', 'waiting', 'failed'):
        raise ValueError('invalid implementation result status')
    for key in ('questions', 'return_candidates', 'changed_findings'):
        if not isinstance(data.get(key), list):
            raise ValueError('implementation result needs array ' + key)
    code = evidence.check_scope(context, execution)
    if store.empty_revision(context, execution):
        original = store.read(context.root, store.BASE + '/runs/' + execution['execution_id'] + '/result.json')
        if (data['status'] != 'completed' or any(data[key] for key in ('questions', 'return_candidates', 'changed_findings'))
                or original['status'] != 'completed' or original['code'] != code):
            raise ValueError('empty revision must complete without edits, questions or findings')
        return {**data, 'code': code}
    if data['status'] == 'completed':
        if data['questions'] or data['return_candidates']:
            raise ValueError('completed task still has questions/returns')
        verified = evidence.receipts(context, execution)
        if execution['policy']['tasks'][execution['task_id']]['tdd']:
            red = store.read(context.root, store.BASE + '/runs/' + execution['execution_id'] + '/red.json')
            green = evidence.receipts(context, execution, stage='green', current=False)
            if (red.get('task_id') != execution['task_id'] or red.get('execution_id') != execution['execution_id']
                    or red.get('policy_hash') != store.fingerprint(execution['policy'])
                    or red.get('source_changed') or red.get('stage') != 'red'
                    or not red.get('completed_at') or not green.get('completed_at') or not verified.get('completed_at')
                    or not (red['completed_at'] <= green['completed_at'] <= verified['completed_at'])
                    or not red.get('expected_failure') or not any(r['status'] == 'test_failed' for r in red['receipts'])
                    or any(r['status'] not in ('passed', 'test_failed') for r in red['receipts'])):
                raise ValueError('TDD requires an observed expected test failure, not an environment failure')
            for row in red['receipts']:
                for channel in ('stdout', 'stderr'):
                    if store.digest(Path(context.path(row[channel]['path'])).read_bytes()) != row[channel]['sha256']:
                        raise ValueError('RED verification log changed or missing')
        if data['changed_findings'] != execution['repair_findings']:
            raise ValueError('repair result must retain the original finding-to-task mapping')
    elif not (data.get('reason') or data['questions'] or data['return_candidates']):
        raise ValueError('stopped task must preserve its reason and resumption information')
    return {**data, 'code': code}


def save_result(context, data):
    execution = store.read_execution(context)
    if execution.get('event_complete'):
        raise ValueError('completed task results are immutable; use a new authorized execution')
    result = validate_result(context, data)
    name = 'empty-revision.json' if store.empty_revision(context, execution) else 'result.json'
    store.write(context.root, store.BASE + '/runs/' + execution['execution_id'] + '/' + name, {'schema': 1, **result})
    return result


def finish_task(context):
    execution = preflight(context)
    name = 'empty-revision.json' if store.empty_revision(context, execution) else 'result.json'
    result = store.read(context.root, store.BASE + '/runs/' + execution['execution_id'] + '/' + name)
    if result['status'] != 'completed' or result['code'] != evidence.check_scope(context, execution):
        raise ValueError('task result is missing, incomplete or stale')
    validate_result(context, result)
    if execution.get('event_complete'):
        return execution
    execution['empty_revision_checked' if store.empty_revision(context, execution) else 'end_checked'] = True
    store.write(context.root, store.execution_path(execution['execution_id']), execution)
    return execution


def record_completion(context):
    import runtime_client
    execution = store.read_execution(context)
    flows.require_saved(context, execution)
    if runtime_client.invoke(context, 'status')['pending'] is not None or not execution.get('end_checked'):
        raise ValueError('all task event units must finish before completion')
    if execution.get('event_complete'):
        return execution
    work = aidd_paths.Context(context.root, context.state_path, execution['event'], context.item)
    finish_task(work)
    if execution['event'] == 'implement-authoring-generate':
        finish_task(aidd_paths.Context(context.root, context.state_path, 'implement-authoring-revise', context.item))
    task_runtime.update(context, execution['feature'], execution['execution_id'] + '-complete',
                        {'kind': 'check', 'task_id': execution['task_id'], 'checked': True,
                         'execution_id': execution['execution_id'], 'verification_ref': store.BASE + '/runs/' + execution['execution_id'] + '/verify.json'})
    state = feature_state(context, execution['feature'])
    state['completed'][execution['task_id']] = {'execution_id': execution['execution_id'], 'event': execution['event'], 'task_item': context.item,
        'plan_ref': execution['plan_ref'], 'policy_hash': store.fingerprint(execution['policy']),
        'verification_sha256': store.digest(Path(context.path(store.BASE + '/runs/' + execution['execution_id'] + '/verify.json')).read_bytes())}
    state['live_code'] = evidence.feature_inventory(context, execution['policy'])
    store.write(context.root, feature_path(execution['feature']), state)
    execution.update(event_complete=True, completed_at=project_state.now())
    store.write(context.root, store.execution_path(execution['execution_id']), execution)
    return execution


def check_feature_ready(context, feature):
    state = feature_state(context, feature)
    flows.require_saved(context, state)
    prerequisites(context, feature)
    plan = task_runtime.freeze(context, feature)
    actual_tasks = task_runtime.parse(Path(context.path('specs/' + feature + '/tasks.md')).read_bytes())[0]
    if (state.get('invalidated') or state['inputs'] != input_signature(context, feature)
            or set(state['completed']) != set(plan['tasks']) or not all(t['checked'] for t in actual_tasks.values())
            or state['live_code'] != evidence.feature_inventory(context, state['policy'])):
        raise ValueError('feature needs all task events, current inputs and verification evidence')
    validate_completed(context, feature, state)
    return state


def validate_completed(context, feature, state):
    """Existing certificates remain evidence; never synthesize new L0 history."""
    for key, proof in state['completed'].items():
        execution = store.read(context.root, store.execution_path(proof['execution_id']))
        receipt_path = store.BASE + '/runs/' + proof['execution_id'] + '/verify.json'
        if (not execution.get('event_complete') or execution['task_id'] != key or execution['feature'] != feature
                or proof['plan_ref'] != state['plan_ref'] or proof['policy_hash'] != store.fingerprint(state['policy'])
                or proof['verification_sha256'] != store.digest(Path(context.path(receipt_path)).read_bytes())):
            raise ValueError('feature task completion evidence is invalid')
        evidence.receipts(context, execution, current=False)


def prepare_review(context):
    state = check_feature_ready(context, context.item)
    import implementation_report_plan
    value = {'schema': 1, 'profile': 'implementation-code-v1', 'feature': context.item,
             'code': evidence.feature_inventory(context, state['policy']),
             'protected': evidence.inventory(context, state['policy'], protected=True),
             'tasks_current_sha256': store.digest(Path(context.path('specs/' + context.item + '/tasks.md')).read_bytes()),
             'inputs': state['inputs'], 'tasks': state['completed'], 'policy': state['policy'], 'aspects': evidence.ASPECTS,
             'flow_contract': state['flow_contract'], 'report_plan': implementation_report_plan.freeze(context, state['policy'])}
    store.write(context.root, evidence.review_path(context.item), value)
    return value


def note(context, data):
    execution = store.require_execution(context, data)
    if execution.get('event_complete'):
        raise ValueError('completed task notes are immutable; use a new authorized execution')
    path = Path(context.path('specs/' + execution['feature'] + '/tasks.md'))
    journal = store.read(*task_runtime.locations(path))
    if any(op['id'] == data.get('operation_id') and op['status'] != 'applied' for op in journal['operations']):
        task_runtime.update(context, execution['feature'], data['operation_id'],
            {'kind': 'note', 'task_id': execution['task_id'], 'section': data['section'], 'text': data['text'], 'execution_id': execution['execution_id']})
    execution = preflight(context)
    task_runtime.update(context, execution['feature'], store.identifier(data['operation_id']),
        {'kind': 'note', 'task_id': execution['task_id'], 'section': data['section'], 'text': data['text'], 'execution_id': execution['execution_id']})
    return {'operation_id': data['operation_id'], 'task_id': execution['task_id'], 'section': data['section'], 'recorded': True}
