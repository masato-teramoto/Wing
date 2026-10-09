"""L3 selection and per-task execution. L0 owns each start/run/end traversal."""
import l0  # noqa: F401  L0 の枠組みを import できるようにする
from pathlib import Path
import copy

import phase_rules
import artifacts
import implementation_evidence as evidence
import implementation_flows as flows
import implementation_store as store
import project_state
import task_runtime

TASK_ACTIONS = phase_rules.IMPLEMENT_TASKS
FINAL = phase_rules.IMPLEMENT_REVIEW
PLAN = phase_rules.IMPLEMENT_PLAN


def kind(context):
    """Phase 8 の action の種類（task / final / plan / cross / integration。implement 工程でなければ空、§6.11）。"""
    return context.kind


def feature_path(feature):
    return store.BASE + '/features/' + store.identifier(feature) + '/state.json'


def feature_state(context, feature):
    return store.read(context.root, feature_path(feature))


def feature_of(context):
    """action が扱う feature。task は実行記録の feature、final・plan は item。feature を持たない種類は空。"""
    value = kind(context)
    if value == 'task':
        return store.current_execution(context)['feature']
    if value in ('final', 'plan'):
        return store.identifier(context.item)
    return ''


def evidence_paths(context):
    """種類ごとの検査・承認の対象（証跡パス）。task は実行の作業領域、final・plan は feature の review.json、
    cross は束ねた入力の cross-review.json、integration（記録を書かない）は無し。"""
    if kind(context) == 'task':
        return store.read_execution(context)['allowed_paths']
    if kind(context) == 'cross':
        import implementation_project
        return [implementation_project.CROSS_REVIEW]
    feature = feature_of(context)
    return [evidence.review_path(feature)] if feature else []


def workspace_policy(context):
    """検査の前後で照合する作業領域の policy（feature の state.json に固定したもの）。"""
    return feature_state(context, feature_of(context))['policy']


def workspace_code(context):
    """検査の前後で照合するコード在庫（検査役がコードを書き換えていないことの照合）。種類ごとに 1 か所。

    task・final は feature の policy で取る。cross は案件全体（`_project.json` の generated_paths を除く。
    全体結合確認・横断 ACE と同じ取り方）。それ以外の種類は照合しない（None）。
    """
    if kind(context) in phase_rules.EVIDENCE_KINDS:
        return evidence.inventory(context, workspace_policy(context))
    if kind(context) == 'cross':
        import implementation_project as project
        return project.project_inventory(context, project.project_policy(context))
    return None


def upstream(context, feature):
    # The task actions and the final review declare the same inputs in action.yaml.
    return context.expand(list(phase_rules.action_row(FINAL)['inputs']), feature)


def _docs_paths():
    return tuple(phase_rules.config()['rules']['docs']['outputs'])


def input_signature(context, feature):
    import feature_scope
    if feature_scope.is_feature(context):
        return _feature_signature(context, feature)
    values = {p: artifacts.protected_digest(context.path(p)) for p in upstream(context, feature)}
    values[evidence.config_path(feature)] = store.digest(Path(context.path(evidence.config_path(feature))).read_bytes())
    owner = phase_rules.ExecutionContext(context.root, context.state_path, phase_rules.RULES['tasks']['generate'], feature)
    for dependency in owner.feature()['depends_on']:
        path = evidence.review_path(dependency)
        values[path] = store.digest(Path(context.path(path)).read_bytes())
    return values


def _feature_signature(context, feature):
    """Feature 方式の Phase 8 入力署名（§6.5）。docs は固定版の id、一覧は S ∪ D の射影、
    依存先は推移閉包 D の実装承認行 (scope, 回数, SHA256)（D-8。review.json の digest ではない）。"""
    import docs_revision
    import feature_manifest
    import feature_scope
    import review_contract
    values = {p: artifacts.protected_digest(context.path(p)) for p in upstream(context, feature)
              if p not in _docs_paths() and p != feature_manifest.SOURCE}
    values[feature_manifest.SOURCE] = feature_manifest.projection(context.root, [feature, *feature_scope.closure(context, feature)])
    values['docs_revision'] = docs_revision.fixed(context, feature) or 'unfixed'
    values[evidence.config_path(feature)] = store.digest(Path(context.path(evidence.config_path(feature))).read_bytes())
    for dependency in feature_scope.closure(context, feature):
        final = phase_rules.ExecutionContext(context.root, context.state_path, FINAL, dependency)
        values['approval:' + evidence.review_path(dependency)] = approval_reference(final)
    return values


def approval_reference(final):
    """feature の実装承認行 (scope, 回数, SHA256)。最新の検査回の承認行が無ければ None（D-8）。"""
    import review_contract
    record = review_contract.read(final)
    run = record.latest(final.scope)
    row = run and next((r for r in reversed(record.approvals) if r['スコープ'] == run.scope and int(r['回数']) == run.number), None)
    return [row['スコープ'], int(row['回数']), row['原本SHA256']] if row else None


def plan_signature(context, feature):
    """計画停止点 implement-plan[S] の記録入力（D-11、§6.1）：S の specs、S と D の検証計画、S ∪ D の一覧の射影。

    D の検証計画が変われば `allowed_paths` の重なりの提示が変わるので、D の config も入れる。
    """
    import feature_manifest
    import feature_scope
    members = [feature, *feature_scope.closure(context, feature)]
    values = {p: artifacts.protected_digest(context.path(p))
              for p in context.expand(list(phase_rules.action_row(PLAN)['inputs']), feature)}
    values[feature_manifest.SOURCE] = feature_manifest.projection(context.root, members)
    for name in members:
        path = Path(context.path(evidence.config_path(name)))
        values[evidence.config_path(name)] = store.digest(path.read_bytes()) if path.is_file() else None
    return values


def plan_digest(context, feature):
    """implement-plan[S] の了承の照合値（accepted_plans['implement']['items'][S]['manifest']）。"""
    return store.fingerprint(plan_signature(context, feature))


def plan_prerequisites(context):
    """implement-plan[S] の前提：Feature 方式で S が選択中、S と D について Phase 8 の開始前提を満たす。"""
    import feature_scope
    feature_scope.require_feature_mode(context, 'Phase 8 の計画停止点（implement-plan）')
    if not context.item:
        raise ValueError('implement-plan は item（選択 feature）付きで呼びます')
    current = feature_scope.selection(context)
    if context.item != current:
        raise ValueError('選択中の feature は %s です（implement-plan[%s] は別の feature）。切り替えるときは select-scope を使います'
                         % (current or '未選択', context.item))
    prerequisites(context, feature_of(context))


def overlaps(context, feature):
    """S の allowed_paths と依存先 D の allowed_paths の重なり（§6.12。計画提示と親要求の作成で使う）。"""
    import feature_scope
    found = []
    mine = _allowed_paths(context, feature)
    for name in feature_scope.closure(context, feature):
        for path in mine:
            for other in _allowed_paths(context, name):
                if _overlap(path, other):
                    found.append((name, path, other))
    return found


def _allowed_paths(context, feature):
    path = Path(context.path(evidence.config_path(feature)))
    if not path.is_file():
        return []
    value = store.read(context.root, evidence.config_path(feature))
    return sorted({p for task in (value.get('tasks') or {}).values() for p in task.get('allowed_paths') or []})


def _overlap(left, right):
    a, b = left.rstrip('/'), right.rstrip('/')
    return a == b or a.startswith(b + '/') or b.startswith(a + '/')


def same_inputs(context, feature, saved, current, switched=True):
    """保存した入力署名と現在が同じか。Feature 方式の docs 固定版は C2 影響なしの同値記録でつながればよい。
    方式切替の前に記録した値は、切替記録の対応（旧方式の値 → 新方式の値）でつながればよい（§6.1 の引継ぎ (5)(6)）。"""
    if saved == current:
        return True
    if switched:
        data = context.state().get('workflow') or {}
        # 方式切替の対応（§6.1 の引継ぎ (5)(6)）と、reverify で全タスクが (3) だったときの対応（§6.5）。
        pairs = ((((data.get('mode_switch') or {}).get('phase8') or {}).get(feature) or [])
                 + ((data.get('input_equivalences') or {}).get(feature) or []))
        if any(pair['from'] == saved and same_inputs(context, feature, pair['to'], current, switched=False) for pair in pairs):
            return True
        import implementation_reverify
        if implementation_reverify.repinned_protected(context, saved, current):
            return True  # 再固定記録（implement-repin）の遡及不要の差分だけでつながる
    import docs_revision
    rest = lambda value: {k: v for k, v in value.items() if k != 'docs_revision'}
    return (isinstance(saved, dict) and rest(saved) == rest(current) and 'docs_revision' in saved
            and docs_revision.equivalent(context, feature, saved['docs_revision'], current.get('docs_revision')))


def prerequisites(context, feature, starting=True):
    import prerequisites as checks
    import review_contract
    import review_decisions
    import feature_scope
    if feature_scope.is_feature(context):
        return _feature_prerequisites(context, feature, starting)
    checks.approved(context, upstream(context, feature))
    checks.blockers(context)
    review_decisions.check_cross(context, 'requirements')
    review_decisions.check_cross(context, 'design')
    review_contract.check_approved(phase_rules.ExecutionContext(context.root, context.state_path, 'tasks-gate-run'))
    feature_context = phase_rules.ExecutionContext(context.root, context.state_path, phase_rules.RULES['tasks']['generate'], feature)
    for dependency in feature_context.feature()['depends_on']:
        review_contract.check_approved(phase_rules.ExecutionContext(context.root, context.state_path, FINAL, dependency))


def _feature_prerequisites(context, feature, starting=True):
    """Feature 方式の Phase 8 開始前提（§6.4・§6.5・D-6・P4）。

    docs は現在のファイルではなく固定版の有効性で判定する（他 feature の docs 改訂中も止まらない）。
    全件 tasks-gate-run の承認の代わりに S の tasks.md の工程承認（`phase:<S>` または全件 `phase`）、
    全件 cross の代わりに S が Platform で利用側があるときの `cross:<S>`、依存先は推移閉包 D の実装承認。
    """
    import prerequisites as checks
    import review_contract
    import review_decisions
    import docs_revision
    import feature_scope
    checks.approved(context, [p for p in upstream(context, feature) if p not in _docs_paths()
                              and not p.endswith('/tasks.md')])
    docs_revision.valid(context, docs_revision.fixed(context, feature))
    checks.blockers(context)
    # Platform の selection 横断確認は開始の前提だけ。承認済みの照合では見ない（利用側の承認で比較相手が
    # 増えるたびに実装承認が落ちないように。鮮度は残件として表示する：D-10、§6.12）。
    for process in ('requirements', 'design') if starting else ():
        if feature_scope.consumers(context, process, feature):
            review_decisions.check_cross(context, process, feature)
        # 弱い形（§6.5）：依存先 Platform P の cross:<P> が一度も実施されていなければ止める。実施済みで古い・無効なら案内だけ。
        for dependency in feature_scope.closure(context, feature):
            if feature_scope.consumers(context, process, dependency):
                state, _ = review_decisions.selection_cross_state(context, process, dependency)
                if state == 'missing':
                    raise ValueError('依存先 %s の %s の横断確認（cross:%s）が一度も実施されていません。'
                                     '%s を選んで横断確認を通してから実装に入ります' % (dependency, process, dependency, dependency))
    review_contract.phase_approved(context, 'specs/%s/tasks.md' % feature)
    for dependency in feature_scope.closure(context, feature):
        review_contract.check_approved(phase_rules.ExecutionContext(context.root, context.state_path, FINAL, dependency))


def select(context, payload):
    feature = store.identifier(context.item)
    import feature_scope
    import implementation_project
    if not feature_scope.is_feature(context) and not any(Path(context.path(store.BASE + '/features')).glob('*/state.json')):
        # 全件方式の旧案件で Phase 8 未着手なら、/aidd-tasks で owner を選んでから始める（着手済みの旧案件は対象外：§6.11）。
        # Feature 方式は owner 候補の feature の tasks-plan[S] の番で選ぶので、それより前の feature の Phase 8 は止めない。
        implementation_project.require_owner(context)
    if feature_scope.is_feature(context) and not feature_scope.plan_accepted(context, 'implement', feature):
        # 計画停止点の了承前にタスクの実行は始まらない（D-11）。了承後に検証計画・tasks が変われば再提示する。
        raise ValueError('implement-plan[%s] の計画を提示して了承を得てから実装を始めます（/aidd-implement %s）' % (feature, feature))
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
        if state.get('invalidated') or not same_inputs(context, feature, state['inputs'], inputs) or state['plan_ref'] != plan['plan_ref']:
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
    import implementation_reverify
    state['phase8_definitions'] = implementation_reverify.definitions_digest(context)  # implement-repin の照合値
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
    if kind(context) == 'task':
        flows.require_saved(context, store.read_execution(context))
        # Recover only the exact completion edit already authorized by this action.
        path = Path(context.path('specs/' + feature + '/tasks.md'))
        location = task_runtime.locations(path)
        if location and (location[0] / location[1]).exists():
            journal = store.read(*location)
            pending = [op for op in journal['operations'] if op['status'] != 'applied']
            if pending and pending[0]['id'] == store.read_execution(context)['execution_id'] + '-complete':
                task_runtime.update(context, feature, pending[0]['id'], pending[0]['operation'])
    prerequisites(context, feature)
    state = feature_state(context, feature)
    if state.get('invalidated') or not same_inputs(context, feature, state['inputs'], input_signature(context, feature)):
        raise ValueError('implementation input version changed; explicit rebase is required')
    if kind(context) == 'task':
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
        elif (context.action == 'implement-authoring-revise' and not execution.get('repair_findings')
              and not execution.get('reverify')):
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
    if state.get('invalidated') or not same_inputs(context, feature, state['inputs'], input_signature(context, feature)):
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
        action = 'implement-authoring-revise' if request['kind'] in ('repair', 'reverify') else 'implement-authoring-generate'
        path = store.execution_path(child)
        if Path(context.path(path)).exists():
            execution = store.read(context.root, path)
        else:
            execution = {'schema': 1, 'execution_id': child, 'request_id': request_id, 'feature': feature,
                         'flow_contract': request['flow_contract'],
                         'task_item': request['previous'][key]['task_item'] if request['kind'] in ('repair', 'reverify') else child,
                         'task_id': key, 'event': action, 'plan_ref': state['plan_ref'], 'inputs': state['inputs'],
                         'policy': request['policy'], 'allowed_paths': request['policy']['tasks'][key]['allowed_paths'],
                         'baseline': evidence.inventory(context, request['policy']),
                         'protected': evidence.inventory(context, request['policy'], protected=True),
                         'repair_findings': [f for f in request.get('findings', []) if key in f['task_ids']],
                         'previous_execution': request.get('previous', {}).get(key), 'event_complete': False}
            if request['kind'] == 'reverify':
                # 3 段の (2)：コードは作り直さない（編集 0 件）。変更の集合を L4 の reverify 用レビューに渡す（§6.5）。
                execution.update(reverify=request['changes'], allowed_paths=[])
            # The task review's code baseline is recorded by the L4 start gate `task-code-review-baseline`.
            store.write(context.root, path, execution)
        request['children'][key] = child
        store.write(context.root, store.request_path(request_id), request)
        return advance_execution(context, execution)
    request['status'] = 'completed'
    store.write(context.root, store.request_path(request_id), request)
    if len(state['completed']) != len(state['policy']['tasks']):
        return {'status': 'partial', 'request_id': request_id, 'completed': sorted(state['completed']),
                'remaining': sorted(set(state['policy']['tasks']) - set(state['completed'])), 'approved': False}
    final_context = phase_rules.ExecutionContext(context.root, context.state_path, FINAL, feature)
    # L0 keeps completed units; a changed feature must explicitly redo final inspection.
    return host_session.advance(final_context)


def advance_execution(context, execution):
    """Journal activation before dispatch; a repair invalidates only revision units."""
    import host_session
    import engine_client
    import project_progress
    child = phase_rules.ExecutionContext(context.root, context.state_path, execution['event'], execution['task_item'])
    if not execution.get('activated'):
        state = feature_state(context, execution['feature'])
        if state.get('active_request') != execution['request_id'] or state.get('invalidated'):
            raise ValueError('activation belongs to an inactive parent')
        if execution['event'] == 'implement-authoring-revise':
            if not execution.get('activation_prepared'):
                previous = store.current_execution(child)
                proof = execution['previous_execution']
                if (previous['execution_id'] != proof['execution_id'] or not previous.get('event_complete')
                        or engine_client.invoke(child, 'status')['pending'] is not None):
                    raise ValueError('repair requires a completed task flow on the same item')
                execution['activation_prepared'] = True
                store.write(context.root, store.execution_path(execution['execution_id']), execution)
            # Until activated is durable no skill or helper can run, so replaying
            # this redo after a crash cannot discard new work.
            project_progress.redo(child, child.action, child.item)
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
    waiting = context.state().get('workflow', {}).get('waiting', {}).get(context.action + '[' + context.item + ']')
    if waiting and waiting.get('execution_id') != execution['execution_id']:
        waiting = None
    if noop:
        identity['allowed_paths'] = []
    import prerequisites
    inputs = upstream(context, execution['feature'])
    # unreviewed_inputs: upstream drafts left out of their inspection's target_review (D6).
    return {**identity, 'event': context.action, 'task_item': context.item, 'noop': noop, 'task': task, 'upstream': inputs,
            'authoring_inputs': inputs, 'unreviewed_inputs': prerequisites.unreviewed_inputs(context, inputs),
            'questions': waiting,
            'execution_path': store.execution_path(execution['execution_id']),
            'verification_plan': execution['policy'],
            'targets': [] if noop else execution['allowed_paths'],
            'review_targets': [] if noop else context.review_targets(), 'profile': 'implementation-task',
            'reverify': execution.get('reverify')}


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
        import task_verification
        task_verification.validate_task(context, execution)
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
    # The end gates can finish before the independent checkbox save resumes.
    # Recheck the gate-issued evidence at this save boundary, without importing L4.
    import implementation_completion
    implementation_completion.require(context, execution, current=True)
    if execution.get('event_complete'):
        return execution
    execution['empty_revision_checked' if store.empty_revision(context, execution) else 'end_checked'] = True
    store.write(context.root, store.execution_path(execution['execution_id']), execution)
    return execution


def record_completion(context):
    import engine_client
    execution = store.read_execution(context)
    flows.require_saved(context, execution)
    if engine_client.invoke(context, 'status')['pending'] is not None or not execution.get('end_checked'):
        raise ValueError('all task action units must finish before completion')
    if execution.get('event_complete'):
        return execution
    work = phase_rules.ExecutionContext(context.root, context.state_path, execution['event'], context.item)
    finish_task(work)
    if execution['event'] == 'implement-authoring-generate':
        finish_task(phase_rules.ExecutionContext(context.root, context.state_path, 'implement-authoring-revise', context.item))
    task_runtime.update(context, execution['feature'], execution['execution_id'] + '-complete',
                        {'kind': 'check', 'task_id': execution['task_id'], 'checked': True,
                         'execution_id': execution['execution_id'], 'verification_ref': store.BASE + '/runs/' + execution['execution_id'] + '/verify.json'})
    state = feature_state(context, execution['feature'])
    state['completed'][execution['task_id']] = {'execution_id': execution['execution_id'], 'event': execution['event'], 'task_item': context.item,
        'plan_ref': execution['plan_ref'], 'policy_hash': store.fingerprint(execution['policy']),
        'verification_sha256': store.digest(Path(context.path(store.BASE + '/runs/' + execution['execution_id'] + '/verify.json')).read_bytes())}
    # Records the task's reviews attached to this execution (L4 writes `feature_records`,
    # e.g. the generated specification per suite); L3 carries them into the feature state as data.
    for key, values in (execution.get('feature_records') or {}).items():
        state.setdefault(key, {}).update(values)
    state['live_code'] = evidence.feature_inventory(context, execution['policy'])
    store.write(context.root, feature_path(execution['feature']), state)
    # タスク前後のコード在庫の差（横断 ACE の「どのタスクも触っていない」の材料。§6.11）。state['completed'] には足さない。
    name = 'empty-revision.json' if store.empty_revision(context, execution) else 'result.json'
    result = store.read(context.root, store.BASE + '/runs/' + execution['execution_id'] + '/' + name)
    execution.update(changed_paths=evidence.changed(execution['baseline'], result['code']))
    execution.update(event_complete=True, completed_at=project_state.now())
    store.write(context.root, store.execution_path(execution['execution_id']), execution)
    return execution


def check_feature_ready(context, feature):
    state = feature_state(context, feature)
    flows.require_saved(context, state)
    prerequisites(context, feature, starting=False)
    plan = task_runtime.freeze(context, feature)
    actual_tasks = task_runtime.parse(Path(context.path('specs/' + feature + '/tasks.md')).read_bytes())[0]
    if (state.get('invalidated') or not same_inputs(context, feature, state['inputs'], input_signature(context, feature))
            or set(state['completed']) != set(plan['tasks']) or not all(t['checked'] for t in actual_tasks.values())
            or state['live_code'] != evidence.feature_inventory(context, state['policy'])):
        raise ValueError('feature needs all task actions, current inputs and verification evidence')
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
        # Historical certificates remain evidence even as later tasks change code.
        import implementation_completion
        implementation_completion.require(context, execution, current=False)


def prepare_review(context):
    state = check_feature_ready(context, context.item)
    import implementation_report_plan
    value = {'schema': 1, 'profile': 'implementation-code-v1', 'feature': context.item,
             'code': evidence.feature_inventory(context, state['policy']),
             'protected': evidence.review_protected(context, context.item),
             'tasks_current_sha256': evidence.tasks_current(context, context.item, evidence.REVIEW_DIGEST_VERSION),
             'inputs': state['inputs'], 'tasks': state['completed'], 'policy': state['policy'], 'aspects': evidence.ASPECTS,
             'flow_contract': state['flow_contract'], 'report_plan': implementation_report_plan.freeze(context, state['policy'])}
    store.write(context.root, evidence.review_path(context.item), value)
    # 照合値の規約版は review.json ではなく L3 の state.json に記録する（§6.6。キー構成を変えない）。
    state = feature_state(context, context.item)
    if state.get('review_digest_version') != evidence.REVIEW_DIGEST_VERSION:
        state['review_digest_version'] = evidence.REVIEW_DIGEST_VERSION
        store.write(context.root, feature_path(context.item), state)
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
