"""main_flow の host の規則。L0 の `host.py`（advance / submit / respond）が各段で呼ぶ。

L0 の host は、状態ストアの排他・操作の記録（再送の識別子）・dispatch の照合・L0 への報告を持ち、
規則が要る段でこの module の `run_stage` を呼ぶ。L3 の入口（`aidd_entry.py` → `host_operations`）が
L0 の host を import し、`run_stage` を渡して呼ぶ（`advance` / `operate`）。定義ファイルに hook は無く、
L0 は L3 を import しない。繰り返しは入口 Skill の手順が持ち、この module は 1 回の呼出しの
前後（実行前の確認・完了の記録・提示）と、submit / respond の検査・保存だけを行う。
"""
import re

import l0  # noqa: F401
import location_identity
import host as l0_host  # L0 の host（L3 は L0 を import してよい）

import phase_rules
import authoring_results
import completion
import repair_requests
import review_decisions
import review_contract
import review_gate
import review_operations
import engine_client
import project_progress

RESPONSES = ('decision', 'decisions', 'resolve', 'approve', 'accept-plan', 'change-plan', 'repair', 'reevaluate')
LETTERS = {'A': '修正', 'B': '差戻し', 'C': '対応せず進める', 'D': '未対応'}


# --- 同じプロセスからの入口（L3 が L0 の host を呼ぶ）-------------------------

def _host(context):
    return l0_host.Host(context.root, context.state_path, config=context.config, stage_runner=run_stage)


def advance(context, call=None):
    return _host(context).advance(call, context.action, context.item)


def operate(context, kind, payload, actor=''):
    host = _host(context)
    if kind == 'submit':
        return host.submit(context.action, context.item, payload, actor)
    return host.respond(context.action, context.item, payload, actor)


def ensure_idle(context, operation_id=None):
    """host の操作の記録（L0 所有）に、終わっていない他の操作が無いこと。"""
    l0_host.ensure_idle(context.state(), operation_id)


def _matching(context, receipt):
    return _host(context).matching(context.action, context.item, receipt)


# --- 段（L0 の host が呼ぶ）----------------------------------------------------

def run_stage(stage, data):
    """段の名前と材料（JSON）を受け取り、結果（JSON）を返す。規則の拒否は ValueError。"""
    handler = STAGES.get(stage)
    if handler is None:
        return {}
    return handler(data) or {}


def _context(data, action=None, item=None):
    return phase_rules.ExecutionContext(data['root'], data['state'], data.get('action', '') if action is None else action,
                                        (data.get('item') or '') if item is None else item)


def stage_resolve(data):
    """呼出し先と、文脈のアクションを決める（入口 Skill が --call だけを渡したとき、Phase 8 の flow）。"""
    action, call, item = data.get('action') or '', data.get('call'), data.get('item') or ''
    if not action and call in phase_rules.PROCESS_OF:
        action = call  # a single action (plan, cross gate) called directly
    if not action and call in phase_rules.MANAGEMENT_CALLS:
        action = phase_rules.MANAGEMENT_CALLS[call]  # 工程に属さない管理用の action
    if not action:
        first = [rule for rule in sorted(phase_rules.RULES.values(), key=lambda r: r['number']) if rule['call'] == call]
        if data.get('operation') != 'advance':
            raise ValueError('--action is required (or --call <flow|action> with advance)')
        if first and first[0]['generate'] != phase_rules.RULES['implement']['generate']:
            action = first[0]['generate']
        else:
            import implementation_flows
            probe = phase_rules.ExecutionContext(data['root'], data['state'], phase_rules.IMPLEMENT_REVIEW, item)
            action = implementation_flows.entry_action(probe, call)
            if not action:
                raise ValueError('unknown workflow flow: ' + str(call))
    context = _context(data, action, item)
    if call is None and context.is_implementation:
        import implementation_flows
        call = implementation_flows.call(context)
    return {'action': action, 'item': item, 'call': call or action}


def stage_guard(data):
    """操作の前：review の書込みが途中でないこと、Phase 8 の実行が今のものであること。"""
    context = _context(data)
    review_operations.ensure_idle(context, data.get('operation_id'))
    if data.get('operation') in ('submit', 'respond') and context.is_implementation:
        import implementation_flows
        implementation_flows.require_current(context)
        _guard_task_replay(context, data.get('operation_id'))
    # 旧配布の config hash で発行された未回答の dispatch は、L0 の黙った再発行に乗せず止めて案内する（§7.1、U03）。
    pending = (context.state().get('current') or {}).get('pending') or {}
    if (data.get('operation') == 'advance' and pending.get('config_sha256')
            and pending['config_sha256'] != engine_client.validate(context)['config_sha256']):
        raise ValueError('更新前の配布で発行された未回答の待ち（%s[%s]）があります。更新前の配布で回答して確定するか、'
                         '該当の操作を取り消してから、新しい配布で進めます' % (pending.get('event', '-'), pending.get('item') or '-'))
    # 旧配布物の host の記録（workflow.host_operations）が途中なら、その配布物で終える。
    legacy = project_progress.workflow(context).get('host_operations', {})
    if any(entry.get('status') != 'finished' for entry in legacy.values()):
        raise ValueError('a host operation of the previous release is incomplete; finish it with that release')
    return {}


def _guard_task_replay(context, operation_id):
    """A prepared/saved retry must not consume a dispatch using changed publication inputs."""
    entry = context.state().get('host_operations', {}).get(operation_id)
    if not entry or entry.get('status') not in ('prepared', 'saved'):
        return
    request = entry.get('request', {})
    if request.get('kind') == 'submit' and _task_gate(entry.get('unit')):
        gate = entry['unit']['gate']
    elif request.get('kind') == 'respond' and _task_wait(context, entry.get('gate')):
        gate = entry['gate']
    else:
        return
    import gate_exchange
    record = gate_exchange.published(context, gate)
    receipt = entry['dispatch']
    # A saved report may already have reached L0 even when its response was lost.
    # L0 deduplicates that report; only the prepared state requires a still-live unit.
    if entry['status'] == 'prepared':
        unit = _matching(context, receipt)
        if unit.get('gate') != gate:
            raise ValueError('task operation belongs to another gate')
    if request['kind'] == 'respond':
        if not location_identity.same_binding(request['payload'].get('expected'), _task_review_context(context, record, receipt)):
            raise review_gate.OperationRejected('stale task confirmation; obtain the current review context')
    if entry['status'] == 'saved':
        # Apply is skipped on replay, so its saved raw file must still be the
        # exact result/answer in this operation before L0 consumes the dispatch.
        if request['kind'] == 'submit':
            kind, raw = 'result', gate_exchange.result(context, gate, allow_saved=True)
        elif request['payload'].get('action') != 'hold':
            kind, raw = 'answer', gate_exchange.answer(context, gate, allow_saved=True)
        else:
            return
        if gate_exchange.record_operation(context, gate, kind, raw, allow_saved=True) != operation_id:
            raise ValueError('task gate record belongs to another host operation')


def stage_advance_before(data):
    """呼出しの前：Phase 8 の呼出し先、入力の変更（audit）と実行前の確認（preflight）。"""
    context = _context(data)
    call = data['call']
    if phase_rules.is_management(context.action):
        # 管理用の action は状態を変えない確認表示なので、毎回出し直す（通過印を残さない）。
        try:
            project_progress.redo(context, context.action)
        except (ValueError, OSError, KeyError):
            pass
        return {}
    if _task_gate(data.get('pending')):
        # A live task dispatch already has a publication. Check its identity
        # and inputs before another engine call can consume or refresh it.
        import gate_exchange
        pending = data['pending']
        active = _context(data, pending.get('event') or '', pending.get('item') or '')
        if engine_client.invoke(active, 'status', call).get('dispatch'):
            gate_exchange.published(active, pending['gate'])
        return {}
    if context.is_implementation:
        import implementation_flows
        implementation_flows.require_call(context, call, validate=True)
        implementation_flows.require_current(context)
    project_progress.audit(context)
    unit = data.get('pending')
    active = _context(data, unit.get('event') or '', unit.get('item') or '') if unit else context
    try:
        project_progress.preflight(active)
    except ValueError as error:
        # A policy stop (open rollback, unapproved upstream, reopened input ...) is a normal
        # result for the host, not a crash: show the reason and what to do next.
        blockers = [b for b in active.blockers() if b.get('status') != 'resolved']
        stop = {'status': 'fail', 'event': active.action, 'item': active.item, 'detail': str(error),
                'allowed_actions': [], 'blockers': blockers}
        if blockers and 'rollback' in str(error):
            stop['status'] = 'blocked'
            stop['next_action'] = '差戻し先の工程（blockers の target_event / target_item）を実行し、再承認後に upstream-approved を記録してください。'
        else:
            stop['next_action'] = _next_action(stop, active)
        return {'stop': stop}
    return {}


def stage_advance_after(data):
    """呼出しの後：完了の記録と、返却の提示（host agent が次にすること）。"""
    outcome, unit = data['outcome'], data.get('pending')
    active = _context(data, unit.get('event') or '', unit.get('item') or '') if unit else _context(data)
    if phase_rules.is_management(active.action):
        import mode_switch
        output = dict(outcome)
        preview = mode_switch.preview(active)  # L0 は script の出力を返さないので、確認表示は L3 が載せる
        output.update(preview=preview['text'], switch_allowed=preview['allowed'], reasons=preview['reasons'],
                      owner_required=preview['owner_required'], owner_candidates=preview['owner_candidates'])
        output['allowed_actions'] = ['switch-mode'] if preview['allowed'] else []
        output['next_action'] = ('確認表示を人に示し、確定と回答されたときだけ switch-mode（confirm: true、理由、'
                                 '必要なら owner）を呼ぶ。確定しなければ何もしない。')
        return {'output': output}
    if not data.get('failed') and outcome.get('status') in ('emit', 'wait') and _task_gate(outcome):
        return _task_gate_output(data, outcome)
    if active.kind == 'integration':
        # 全体結合確認・横断 ACE（記録を書かない）。失敗は分割・送り直し・停止に振り分け、次に呼ぶものを返す（§6.11）。
        import implementation_project
        failed = bool(data.get('failed')) or outcome.get('status') == 'fail'
        if not failed:
            completion.record(active, data['call'])
        output = {**outcome, 'allowed_actions': []}
        output.update(implementation_project.after_run(active, failed))
        return {'output': output}
    record_completions(active, data['call'])
    if data.get('failed'):
        output = {**outcome, 'allowed_actions': []}
        output['next_action'] = _next_action(output, active)
        return {'output': output}
    return {'output': _present(active, outcome)}


def stage_submit_prepare(data):
    """Skill の結果の検査。L0 に報告する結果（ok / wait / fail）を返す。"""
    context = _context(data)
    unit, result = data['unit'], data['result']
    if _task_gate(unit):
        return _task_submit_prepare(context, unit, result)
    if unit.get('isAgent'):
        if result.get('status') not in ('completed', 'failed'):
            raise ValueError('inspector result must be completed or failed')
        if result.get('status') == 'completed':
            import check_gate_write_scope
            try:
                check_gate_write_scope.validate_staged(context)
            except ValueError as error:
                raise ValueError('検査記録の形式に不備があります（%s）。検査役（check-runner）をもう一度実行して '
                                 'inspection_path を書き直し、同じ dispatch で submit し直してください' % error)
        if context.is_implementation and result['status'] == 'completed':
            import implementation_checks
            implementation_checks.validate_semantic(context, result)
    else:
        authoring_results.validate(context, result)
    project_progress.audit(context)
    project_progress.preflight(context)
    return {'result': {'completed': 'ok', 'waiting': 'wait', 'failed': 'fail'}[result['status']]}


def stage_submit_apply(data):
    """Skill の結果の保存（L0 への報告の前）。報告が ok でないときの提示も返す。"""
    context = _context(data)
    unit, result = data['unit'], data['result']
    if _task_gate(unit):
        return _task_submit_apply(context, unit, data)
    project_progress.audit(context)
    project_progress.preflight(context)
    if not unit.get('isAgent'):
        authoring_results.save(context, result)
        if data['report'] == 'wait':
            import host_operations
            host_operations.dispatch(context, 'wait', result, '')
    elif context.is_implementation and data['report'] == 'ok':
        import implementation_checks
        implementation_checks.save_semantic(context, result)
    if data['report'] == 'ok':
        return {}
    output = {'status': 'waiting' if data['report'] == 'wait' else 'fail',
              'allowed_actions': ['answer', 'repair'] if data['report'] == 'wait' else [], 'result': result}
    if data['report'] == 'wait':
        import human_choices
        output['choices'] = human_choices.questions(result.get('questions'))
    output['next_action'] = ('作成中の質問に回答してください（差戻し候補がある場合は差戻しも選べます）。'
                             if data['report'] == 'wait' else _next_action({'status': 'fail'}, context))
    return {'output': output}


def stage_respond_prepare(data):
    """人間の回答の検査と準備。回答が答える dispatch（receipt）を返す。"""
    context = _context(data)
    payload, actor = data['payload'], data.get('actor', '')
    operation = payload.get('action')
    if _task_wait(context, data.get('gate')):
        return _task_respond_prepare(context, data)
    if operation not in RESPONSES:
        raise ValueError('unsupported human response action')
    review_decisions.person(actor)
    value = {'result': 'ok'}
    if operation in ('accept-plan', 'change-plan'):
        receipt = payload.get('dispatch')
        unit = _host(context).matching(context.action, context.item, receipt)
        if receipt['status'] != 'wait' or not (unit.get('gate') == 'plan' or context.action.endswith('-plan')):
            raise ValueError('%s requires its actual plan wait' % operation)
        if operation == 'change-plan':
            if context.process not in ('requirements', 'design', 'tasks'):
                raise ValueError('this plan is not per feature; record conditions as the accept-plan note')
            if not (payload.get('data') or {}).get('instruction'):
                raise ValueError('change-plan requires the actual instruction')
    else:
        expected = payload.get('expected')
        review_gate.require(context, expected)
        answer = payload.get('data') or {}
        if operation == 'decisions':
            for scope, run, number, decided, reason, category, learn, adopted in parse_answer(context, answer.get('answer', '')):
                review_decisions.prepare_response(context, 'decision', {'scope': scope, 'run': run, 'number': number,
                                                                        'decision': decided, 'reason': reason, 'category': category,
                                                                        'learn': learn, 'adopted': adopted}, actor)
            # Freeze 全件 before any child decision changes the live set.
            value['decisions'] = parse_answer(context, answer.get('answer', ''))
        elif operation == 'repair':
            repair_requests.request(_owner(context, answer), answer, actor, apply=False, operation_id=data.get('operation_id'))
        elif operation == 'reevaluate':
            import reevaluation
            reevaluation.prepare(context, actor)
        else:
            review_decisions.prepare_response(context, operation, answer, actor)
        receipt = engine_client.invoke(context, 'status', expected['call'])['dispatch']
    value['receipt'] = receipt
    # The human's repair selection answers this -generate review; report it
    # before the repair's runtime invalidations discard the pending dispatch.
    value['report_first'] = operation in ('repair', 'reevaluate') and repair_requests.is_generate(context)
    return value


def stage_respond_apply(data):
    """人間の回答の記録。L0 が報告するか、続けて advance するか、提示するものを返す。"""
    context = _context(data)
    payload, actor, receipt = data['payload'], data.get('actor', ''), data['receipt']
    operation, opid = payload.get('action'), data['operation_id']
    if _task_wait(context, data.get('gate')):
        return _task_respond_apply(context, data)
    answer = dict(payload.get('data') or {})
    import host_operations
    if operation == 'accept-plan':
        # change-plan is not matched again: the prepared journal already validated this exact
        # request, and reopening the feature list invalidates the plan dispatch (replay must resume).
        _host(context).matching(context.action, context.item, receipt)
        host_operations.dispatch(context, operation, answer, actor)
    elif operation == 'change-plan':
        feature = phase_rules.ExecutionContext(context.root, context.state_path, phase_rules.RULES['feature']['generate'])
        repair_requests.reopen(feature, ['.aidd/feature-list.md'], answer['instruction'], 'plan-change', actor,
                               resume_action=context.action, resume_item=context.item)
    elif operation == 'repair':
        repair_requests.request(_owner(context, answer), answer, actor, operation_id=opid)
    elif operation == 'reevaluate':
        import reevaluation
        reevaluation.request(context, actor, expected=payload['expected'], operation_id=opid)
    elif operation == 'decisions':
        for index, entry in enumerate(data.get('decisions') or []):
            # 旧配布物で準備した回答は 5 項目（却下区分などを持たない）。
            scope, run, number, decided, reason, category, learn, adopted = (list(entry) + ['', False, ''])[:8]
            child_id = '%s.%d' % (opid, index)
            previous = project_progress.workflow(context).get('review_operations', {}).get(child_id)
            expected = previous['request']['expected'] if previous else review_gate.current(context, receipt['call'])
            review_decisions.decision(context, scope, run, number, decided, reason, actor,
                                      expected=expected, operation_id=child_id,
                                      category=category, learn=learn, adopted=adopted)
    else:
        answer.update(expected=payload['expected'], operation_id=opid)
        host_operations.dispatch(context, operation, answer, actor)
        # Consumer invalidation runs in advance, after this review's
        # L0 report. Redo before report would discard its live receipt.
        if operation == 'approve':
            repair_requests.auto_clear(context, actor)
    return {'then': respond_then(context, operation, data.get('report_first'), answer)}


def respond_then(context, operation, report_first, answer=None):
    """回答の後に L0 がすること：`report`（報告して advance）/ `advance` / `output`（提示だけ）。"""
    if operation in ('decision', 'decisions', 'resolve', 'change-plan'):
        return 'output'
    if operation == 'reevaluate':
        return 'advance' if not report_first and repair_requests.is_revise(context) else 'output'
    if operation == 'repair':
        # At a revise review the repair reruns the same revise action (the next round);
        # elsewhere the entry Skill calls the returned revise action (status: repair) or the rollback.
        # A repair owned by another phase or feature is a rollback: do not continue this action.
        if not report_first and repair_requests.is_revise(context) and not _crosses(context, answer or {}):
            return 'advance'
        return 'output'
    return 'report'


def stage_respond_output(data):
    """報告も advance もしない回答の提示（レビューの続き・差戻し・修正）。"""
    context = _context(data)
    payload, receipt = data['payload'], data['receipt']
    operation = payload.get('action')
    if operation in ('decision', 'decisions', 'resolve'):
        import human_choices
        output = {'status': 'wait', 'allowed_actions': review_options(context),
                  'review_context': review_gate.current(context, receipt['call']),
                  'review': review_summary(context), 'choices': human_choices.review(context)}
        output['next_action'] = _next_action({'status': 'wait', 'gate': 'review'}, context)
        return {'output': output}
    output = {'status': 'rollback', 'allowed_actions': [],
              'blockers': [b for b in context.blockers() if b.get('status') != 'resolved'],
              'next_action': '差戻し先の工程（blockers の target_event / target_item）を実行し、再承認後に upstream-approved を記録してから元の工程へ戻ってください。'}
    if operation in ('repair', 'reevaluate'):
        owner = repair_requests.revise_context(_owner(context, payload.get('data') or {}) if operation == 'repair' else context)
        output['repair'] = {'event': owner.action, 'item': owner.item, 'call': owner.action}
        if not output['blockers']:
            output['status'] = 'repair'
            output['next_action'] = '修正の工程（%s%s）を実行し、再検査後に元の検査をやり直してください。' % (
                owner.action, ' --item ' + owner.item if owner.item else '')
    return {'output': output}


def stage_doctor(data):
    """配布物の確認（入口 `aidd_entry.py doctor` が L0 の確認に加える）。資材の一覧と、入力の RFP があること。"""
    import json as _json
    from pathlib import Path
    root, checks = Path(data['root']), []
    try:
        manifest = _json.loads((root / '.main-flow-assets.json').read_text(encoding='utf-8'))
        if manifest.get('schema') != 1 or not isinstance(manifest.get('assets'), dict):
            raise ValueError('invalid asset manifest')
        required = list(manifest['assets']) + ['CLAUDE.md', '.claude/agents/check-runner.md']
        missing = [name for name in required if not (root / name).is_file()]
        checks.append({'name': 'assets', 'ok': not missing, 'detail': missing or '%d deployed assets' % len(manifest['assets'])})
    except (ValueError, OSError) as error:
        checks.append({'name': 'assets', 'ok': False, 'detail': str(error)})
    rfp = root / '.aidd/rfp'
    inputs = sorted(p.relative_to(root).as_posix() for p in rfp.rglob('*')
                    if p.is_file() and not any(part.startswith('.') for part in p.relative_to(rfp).parts)) if rfp.is_dir() else []
    checks.append({'name': 'rfp', 'ok': bool(inputs), 'detail': inputs or 'Place an RFP in .aidd/rfp/ before starting.'})
    return {'checks': checks}


# --- Phase 8 のタスク単位のゲート（agent / human）---------------------------------
# タスクのアクションの emit / wait のゲートは L4 のゲートであり、L0 の GateExecutor が gate.yaml から実行する。
# この host はその中身を解釈しない。前のゲートが公開した提示（または理由付きの省略）を返し、
# エージェントの結果と人間の回答をそのまま保存して、後のゲートに検査させる（gate_exchange）。

TASK_RESPONSES = ('approve', 'repair', 'hold')


def _task_gate(unit):
    """タスクのアクションの agent（skill）/ human（requiresHuman）のゲートの unit か。"""
    return bool(unit and unit.get('gate') and phase_rules.implement_kind(unit.get('event') or '') == 'task'
                and (unit.get('type') == 'skill' or unit.get('requiresHuman')))


def _task_wait(context, gate):
    return bool(gate) and context.kind == 'task'


def _task_review_context(context, record, receipt):
    """ゲートが公開した確認の対象に、今の wait（dispatch）への結び付きを加える。"""
    return dict(record['review_context'] or {}, unit=receipt['unit'], root=context.root, state=context.state_path,
                call=receipt['call'], event=context.action, item=context.item, dispatch_id=receipt['id'])


def _task_gate_output(data, outcome):
    import gate_exchange
    active = _context(data, outcome.get('event') or '', outcome.get('item') or '')
    record = gate_exchange.published(active, outcome['gate'])
    if record['skip']:
        # The gate itself decided this unit does not apply; L0 records it with the reason.
        return {'complete': 'ok', 'note': record['skip']}
    result = dict(outcome, **record['output'])
    if outcome['status'] == 'emit':
        result['allowed_actions'] = ['submit']
    else:
        result['review_context'] = _task_review_context(active, record, outcome['dispatch'])
    return {'output': result}


def _task_submit_prepare(context, unit, result):
    import gate_exchange
    if not isinstance(result, dict) or result.get('status') not in ('completed', 'failed'):
        raise ValueError('task review result must be completed or failed')
    record = gate_exchange.published(context, unit['gate'])
    if record['skip']:
        raise ValueError('this task gate was skipped; there is nothing to submit')
    project_progress.audit(context)
    project_progress.preflight(context)
    return {'result': {'completed': 'ok', 'failed': 'fail'}[result['status']]}


def _task_submit_apply(context, unit, data):
    """結果は解釈せずに保存し、後のゲートが検査・保存する。"""
    import gate_exchange
    project_progress.audit(context)
    project_progress.preflight(context)
    gate_exchange.save_result(context, unit['gate'], data['receipt']['id'], data['result'])
    if data['report'] == 'ok':
        return {}
    output = {'status': 'fail', 'allowed_actions': [], 'result': data['result']}
    output['next_action'] = _next_action({'status': 'fail'}, context)
    return {'output': output}


def _task_live_wait(context, gate, expected):
    """回答が答える、今のタスクの wait（dispatch）と、ゲートが公開した記録。"""
    import gate_exchange
    if not isinstance(expected, dict) or not expected.get('call'):
        raise review_gate.OperationRejected('stale task confirmation; obtain the current review context')
    state = engine_client.invoke(context, 'status', expected['call'])
    pending, receipt = state.get('pending'), state.get('dispatch')
    if (not pending or pending.get('gate') != gate or pending.get('event') != context.action
            or (pending.get('item') or '') != context.item or not receipt or receipt.get('status') != 'wait'):
        raise review_gate.OperationRejected('task confirmation requires the actual task specification wait', pending)
    record = gate_exchange.published(context, gate)
    if not location_identity.same_binding(expected, _task_review_context(context, record, receipt)):
        raise review_gate.OperationRejected('stale task confirmation; obtain the current review context', pending)
    return receipt, record


def _task_respond_prepare(context, data):
    import gate_exchange
    payload, actor = data['payload'], data.get('actor', '')
    operation = payload.get('action')
    if operation not in TASK_RESPONSES:
        raise ValueError('unsupported task confirmation action')
    review_decisions.person(actor)
    receipt, record = _task_live_wait(context, data['gate'], payload.get('expected'))
    if operation not in record['output'].get('allowed_actions', []):
        raise review_gate.OperationRejected('this task confirmation does not allow `%s`' % operation)
    gate_exchange.check_answer(record['answers'], operation, payload.get('data'))
    return {'receipt': receipt, 'result': 'ok', 'report_first': False}


def _task_respond_apply(context, data):
    """回答は解釈せずに保存する。hold は wait を残し、approve / repair は報告する（repair はタスクをやり直す）。"""
    import gate_exchange
    payload, receipt = data['payload'], data['receipt']
    operation = payload['action']
    if operation == 'hold':
        return {'then': 'advance'}  # The host journal retains this answer; the dispatch stays live.
    gate_exchange.save_answer(context, data['gate'], receipt['id'], data['operation_id'], operation,
                              data.get('actor', ''), payload['data'], payload['expected'])
    return {'then': 'report-then' if operation == 'repair' else 'report'}


def stage_respond_reported(data):
    """報告の後：タスクの確認の修正は、同じタスクをやり直す（L3 の implementation_repair）。
    tasks の計画停止点で選んだ owner の tasks の修正の要求も、ここで起こす（feature_scope.apply_owner_reopen）。"""
    context = _context(data)
    payload = data['payload']
    if payload.get('action') == 'accept-plan':
        import feature_scope
        feature_scope.apply_owner_reopen(context)
    if _task_wait(context, data.get('gate')) and payload.get('action') == 'repair':
        import implementation_repair
        import implementation_store as store
        answer = payload['data']
        execution = store.read_execution(context)
        implementation_repair.retry(context, {'execution_id': execution['execution_id'],
                                              'operation_id': data['operation_id'], 'reason': answer['instruction']},
                                    instructions={'instruction': answer['instruction'],
                                                  'corrections': answer.get('corrections', {})})
    return {}


STAGES = {
    'resolve': stage_resolve,
    'guard': stage_guard,
    'advance-before': stage_advance_before,
    'advance-after': stage_advance_after,
    'submit-prepare': stage_submit_prepare,
    'submit-apply': stage_submit_apply,
    'respond-prepare': stage_respond_prepare,
    'respond-apply': stage_respond_apply,
    'respond-output': stage_respond_output,
    'respond-reported': stage_respond_reported,
}


# --- 提示 ----------------------------------------------------------------

def _next_action(outcome, active):
    """alpha2 Step 6: tell the person the next thing to do in one line."""
    status = outcome.get('status')
    if status == 'emit':
        return '作業中（AI が %s を実行します）。人の操作は不要です。' % ('検査' if outcome.get('isAgent') else '作成・修正')
    if status == 'wait' and outcome.get('gate') == 'review':
        return ('提示文をそのまま示し、choices の選択肢を選択式の質問で出して、人に選んでもらってください。'
                '検査結果を確認し、重大と要判断の指摘に A〜D か「推奨」で答えてください（束・範囲でまとめて答えられます）。'
                '修正（A）と AI が直す軽微があれば repair（findings: "all-fixes"）で修正に回し、判断が揃い修正が無ければ承認者名を回答してください。')
    if status == 'wait':
        return '実行計画を確認し、了承するか、対象・順序の変更を指示してください。'
    if status == 'done':
        return '完了しました。入口 Skill の手順の次（次の feature・修正の回・次の呼出し）へ進んでください。'
    if status == 'fail':
        return '停止しました。理由を確認し、表示された対処（上流の修正・再実行など）を行ってください。'
    return ''


def _present(context, outcome):
    result = dict(outcome)
    action = outcome.get('event', context.action)
    item = outcome.get('item') or ''
    active = phase_rules.ExecutionContext(context.root, context.state_path, action or '', item)
    if outcome['status'] == 'emit':
        import host_operations
        result.update(allowed_actions=['submit'], context=host_operations.dispatch(active, 'context', {}, ''))
    elif outcome['status'] == 'wait' and outcome.get('gate') == 'review':
        import human_choices
        result.update(allowed_actions=review_options(active),
                      review_context=review_gate.current(active, outcome['call']),
                      review=review_summary(active), choices=human_choices.review(active))
        if active.is_implementation:
            import implementation_checks
            result['report_summary'] = implementation_checks.validate_final(active)['summary']['path']
    elif outcome['status'] == 'wait':
        import human_choices
        result['allowed_actions'] = (['accept-plan'] + (['change-plan'] if active.process in ('requirements', 'design', 'tasks') else [])
                                     + (['select-scope'] if active.kind == 'plan' else []))
        result['choices'] = human_choices.plan(active)
    else:
        result['allowed_actions'] = []
    result['next_action'] = _next_action(outcome, active)
    return result


def review_summary(context):
    """Structured findings of the live review (for the host to map answers; not shown as is)."""
    record = review_contract.read(context)
    rows = []
    for scope in review_contract.scopes(context):
        latest = record.latest(scope).number
        for f in record.relevant(scope):
            rows.append({'scope': f.scope, 'run': f.run, 'number': f.number, 'current': f.run == latest,
                         'decision': f.decision, 'reason': f.reason, 'open': f.is_open, 'resolved': f.resolved,
                         'description': f.description, 'location': f.location,
                         'kind': f.kind, 'severity': f.level, 'summary': f.short, 'suggestion': f.suggestion,
                         'recommendation': f.recommendation, 'decided_by': f.decided_by})
    return rows


def review_options(context):
    record = review_contract.read(context)
    findings = [f for scope in review_contract.scopes(context) for f in record.relevant(scope)]
    result = ['decision', 'decisions'] if findings else []
    if any(f.is_open for f in findings):
        result += ['resolve', 'repair']
    try:
        review_contract.ready(context, record)
    except ValueError:
        pass
    else:
        result.append('approve')
    return result


# --- 完了の記録 ----------------------------------------------------------

def flow_processes(call):
    """Processes whose -generate/-revise run inside the flow `call`, in order."""
    return [name for name, rule in sorted(phase_rules.RULES.items(), key=lambda kv: kv[1]['number'])
            if name != 'implement' and rule['call'] == call]


def record_completions(context, call):
    """Issue completion certificates for what this call finished.

    The entry Skill calls one action per round (D24): the certificate of the action's
    phase/item is issued once its review evidence is complete; an unfinished one is skipped.
    """
    processes = flow_processes(call)
    if not processes:
        if not context.action.endswith('-plan'):
            try:
                completion.record(context, call)
            except ValueError:
                if context.kind == 'cross' and engine_client.invoke(context, 'status', call).get('pending') is None:
                    raise  # feature を持たない action の完了の記録は黙って欠かさない（§6.11）
        return
    pending = engine_client.invoke(context, 'status', call).get('pending')
    later = phase_rules.PROCESS_OF.get(pending.get('event') or '') if pending else None
    for process in processes:
        rule = phase_rules.RULES[process]
        if later is not None and rule['number'] >= phase_rules.RULES[later]['number']:
            break
        items = [context.item]
        if rule['per_feature'] and not context.item:
            try:
                items = [entry['name'] for entry in context.features()]
            except ValueError:
                items = []
        for item in items:
            target = phase_rules.ExecutionContext(context.root, context.state_path, rule['repair'], item)
            if completion.check(target).get('complete'):
                continue
            try:
                completion.record(target, call, flow_done=True)
            except (ValueError, OSError):
                pass


# --- 回答の読み取り ------------------------------------------------------

_TARGET = r'(全件|束\d+|(?:((?:feature|phase|cross):[a-z0-9][a-z0-9_-]*|phase|cross)\s+)?(?:(\d+)\s*[〜~]\s*(\d+)|(?:(\d+)-)?(\d+)))'
_CHOICE = r'([A-DＡ-Ｄ]|推奨)(?:\s*[\[［]\s*([^\]］+＋]*?)\s*([+＋])?\s*[\]］])?'
_ANSWER = re.compile(_TARGET + r'\s*[:：]\s*' + _CHOICE + r'\s*(.*)')


def parse_answer(context, text):
    """回答の読み取り。返り値は (scope, run, number, 判断, 理由, 却下区分, 今後も同じ扱い, 推奨の採用) の並び。

    書き方（`/` か改行で区切る。後に書いたものが前のものより優先する）:
    `1:A`、`2:C 理由`、`2-1:D 理由`（2 回目の #1）、`3〜8:C 理由`（範囲）、`束1:C 理由`（束）、`全件:A`、
    `1:推奨`（AI の推奨を採用）、`2:C[後で決める+] 理由`（却下区分。`+` は今後も同じ扱い）。
    """
    import finding_rules
    import review_view
    record = review_contract.read(context)
    scopes = review_contract.scopes(context)
    relevant = [f for scope in scopes for f in record.relevant(scope)]
    latest = {scope: record.latest(scope).number for scope in scopes}
    undecided = [f for f in relevant if not f.has_decision]
    named = review_view.bundles(context, record)
    parts = [p.strip() for p in re.split(r'[／/\n]', text or '') if p.strip()]
    if not parts:
        raise ValueError('answer is empty')
    chosen = {}
    for part in parts:
        m = _ANSWER.fullmatch(part)
        if not m:
            raise ValueError('answer must look like `1:A` / `2:C 理由` / `束1:C 理由` / `3〜5:A` / `1:推奨` / `全件:A`: %s' % part)
        target, scope_name, low, high, run_text, number_text, choice, category, learn, reason = m.groups()
        reason = reason.strip()
        if target == '全件':
            if not undecided:
                raise ValueError('no undecided findings for 全件')
            findings = undecided
        elif target.startswith('束'):
            if target not in named:
                raise ValueError('unknown bundle: %s' % target)
            findings = named[target].findings
        else:
            scope = scope_name or (scopes[-1] if len(scopes) == 1 else None)
            if scope is None:
                raise ValueError('several scopes are reviewed together; prefix the scope (e.g. `feature:x 1:A`)')
            run = int(run_text) if run_text else latest[scope]
            numbers = range(int(low), int(high) + 1) if low else [int(number_text)]
            findings = []
            for number in numbers:
                found = next((f for f in relevant if f.key == (scope, run, number)), None)
                if found is None:
                    raise ValueError('finding does not exist in the current review: %s %s #%s' % (scope, run, number))
                findings.append(found)
        if choice == '推奨' and target.startswith('束'):
            import human_choices
            if not human_choices.uniform_recommendation(findings)[0]:
                raise ValueError('束の中で AI の推奨がそろっていません。束の判断を A〜D で選ぶか、番号ごとに答えてください: %s' % target)
        for finding in findings:
            recommended, why = finding_rules.recommendation(finding.recommendation)
            if choice == '推奨':
                if recommended in ('', '質問'):
                    raise ValueError('AI の推奨が無い指摘です（A〜D で答えてください）: %s' % finding.label())
                value, adopted = recommended, '採用'
                text_reason = reason or 'AI 推奨を採用: ' + why
            else:
                value = LETTERS[choice.translate(str.maketrans('ＡＢＣＤ', 'ABCD'))]
                adopted = ('採用' if value == recommended else '不採用') if recommended not in ('', '質問') else ''
                text_reason = reason
            kind = finding_rules.rejection((category or '').strip())
            if kind and value != '対応せず進める':
                raise ValueError('却下区分は C（対応せず進める）にだけ付ける: %s' % part)
            if learn and kind not in finding_rules.LEARNABLE:
                raise ValueError('「今後も同じ扱い（+）」は 対象外 か 後で決める にだけ付ける: %s' % part)
            chosen[finding.key] = (finding.scope, finding.run, finding.number, value, text_reason, kind, bool(learn), adopted)
    decisions = list(chosen.values())
    for scope, run, number, value, reason, *_ in decisions:
        if value in ('対応せず進める', '未対応') and not reason:
            raise ValueError('理由が必要です: %s run %s #%s' % (scope, run, number))
    return decisions


def _crosses(context, data):
    """A repair owned by another phase or feature is a rollback: do not continue this action."""
    owner = _owner(context, data)
    return owner.process != context.process or owner.item != context.item


def _owner(context, data):
    """The owner of a repair: explicit action/item in the answer, else this phase's own item."""
    action = data.get('event') or phase_rules.RULES[context.process]['generate']
    item = data.get('item') if 'item' in data else (context.item if phase_rules.RULES.get(phase_rules.PROCESS_OF.get(action, ''), {}).get('per_feature') else '')
    return phase_rules.ExecutionContext(context.root, context.state_path, action, item or '')
