"""Serial L3 host entry: advance, submit Skill output, respond to a real wait.

Only the public L0 CLI dispatches execution. Persistent operation IDs cover the
gap between a saved L3 action, its L0 report and the following engine call.
The host advances a flow (flows.yaml: <base>-generate -> <base>-revise per phase)
or a single event (plans, cross gates); L0 skips units that already succeeded.
"""
import re

import aidd_paths
import authoring_results
import completion
import repair_actions
import review_actions
import review_contract
import review_gate
import review_operations
import runtime_client
import workflow_state

RESPONSES = ('decision', 'decisions', 'resolve', 'approve', 'accept-plan', 'change-plan', 'repair')
LETTERS = {'A': '修正', 'B': '差戻し', 'C': '対応せず進める', 'D': '未対応'}


def _save(context, entries):
    workflow_state.save(context, {'host_operations':entries})


def ensure_idle(context, operation_id=None):
    entries = workflow_state.workflow(context).get('host_operations', {})
    def own(k):
        return operation_id is not None and (k == operation_id or operation_id.startswith(k + '.'))
    if any(not own(k) and v['status'] != 'finished' for k,v in entries.items()):
        raise ValueError('a host operation is incomplete; retry its original operation ID and payload')


def _matching(context, receipt):
    if not isinstance(receipt,dict) or not receipt.get('id'):
        raise ValueError('the actual L0 dispatch is required')
    if context.process == 'implement':
        import implementation_flows
        implementation_flows.require_call(context, receipt.get('call'), validate=True)
    status = runtime_client.invoke(context,'status',receipt.get('call'))
    if status.get('dispatch') != receipt:
        raise ValueError('stale or unissued dispatch')
    unit = status['pending']
    if unit['event'] != context.event or (unit.get('item') or '') != context.item:
        raise ValueError('dispatch belongs to another event/item')
    return unit


def _next_action(outcome, active):
    """alpha2 Step 6: tell the person the next thing to do in one line."""
    status = outcome.get('status')
    if status == 'emit':
        return '作業中（AI が %s を実行します）。人の操作は不要です。' % ('検査' if outcome.get('isAgent') else '作成・修正')
    if status == 'wait' and outcome.get('gate') == 'review':
        return '検査結果を確認し、指摘ごとに A〜D で判断を回答してください（判断が揃い修正が無ければ承認者名を回答）。'
    if status == 'wait':
        return '実行計画を確認し、了承するか、対象・順序の変更を指示してください。'
    if status == 'done':
        return '完了しました。次のコマンド（または次の feature）へ進んでください。'
    if status == 'fail':
        return '停止しました。理由を確認し、表示された対処（上流の修正・再実行など）を行ってください。'
    return ''


def _present(context, outcome):
    result = dict(outcome)
    event = outcome.get('event',context.event)
    item = outcome.get('item') or ''
    active = aidd_paths.Context(context.root,context.state_path,event,item)
    if outcome['status'] == 'emit':
        import workflow
        result.update(allowed_actions=['submit'], context=workflow.dispatch(active,'context',{},''))
    elif outcome['status'] == 'wait' and outcome.get('gate') == 'review':
        result.update(allowed_actions=review_options(active),
                      review_context=review_gate.current(active,outcome['call']),
                      review=review_summary(active))
        if active.process == 'implement':
            import implementation_checks
            result['report_summary'] = implementation_checks.validate_final(active)['summary']['path']
    elif outcome['status'] == 'wait':
        result['allowed_actions'] = ['accept-plan'] + (['change-plan'] if active.process in ('requirements','design','tasks') else [])
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
                         'description': f.description, 'location': f.location})
    return rows


def review_options(context):
    record = review_contract.read(context)
    findings = [f for scope in review_contract.scopes(context) for f in record.relevant(scope)]
    result = ['decision', 'decisions'] if findings else []
    if any(f.is_open for f in findings):
        result += ['resolve','repair']
    try:
        review_contract.ready(context,record)
    except ValueError:
        pass
    else:
        result.append('approve')
    return result


def flow_processes(call):
    """Processes whose -generate/-revise run inside the flow `call`, in order."""
    names = [name for name, rule in sorted(aidd_paths.RULES.items(), key=lambda kv: kv[1]['number'])
             if name != 'implement' and rule['call'] == call]
    return names


def record_completions(context, call):
    """Issue completion certificates for every process of a flow that has finished."""
    processes = flow_processes(call)
    if not processes:
        if not context.event.endswith('-plan'):
            try:
                completion.record(context, call)
            except ValueError:
                pass
        return
    pending = runtime_client.invoke(context, 'status', call).get('pending')
    later = aidd_paths.PROCESS_OF.get(pending['event']) if pending else None
    for process in processes:
        if later is not None and aidd_paths.RULES[process]['number'] >= aidd_paths.RULES[later]['number']:
            break
        target = aidd_paths.Context(context.root, context.state_path, aidd_paths.RULES[process]['repair'], context.item)
        if completion.check(target).get('complete'):
            continue
        try:
            completion.record(target, call, flow_done=True)
        except ValueError:
            pass


def _advance(context, call):
    if context.process == 'implement':
        import implementation_flows
        implementation_flows.require_call(context, call, validate=True)
        implementation_flows.require_current(context)
    workflow_state.audit(context)
    status = runtime_client.invoke(context,'status',call)
    unit = status.get('pending')
    active = aidd_paths.Context(context.root,context.state_path,unit['event'],unit.get('item') or '') if unit else context
    try:
        workflow_state.preflight(active)
    except ValueError as error:
        # A policy stop (open rollback, unapproved upstream, reopened input ...) is a normal
        # result for the host, not a crash: show the reason and what to do next.
        blockers = [b for b in active.blockers() if b.get('status') != 'resolved']
        data = {'status': 'fail', 'event': active.event, 'item': active.item, 'detail': str(error),
                'allowed_actions': [], 'blockers': blockers}
        if blockers and 'rollback' in str(error):
            data['status'] = 'blocked'
            data['next_action'] = '差戻し先の工程（blockers の target_event / target_item）を実行し、再承認後に upstream-approved を記録してください。'
        else:
            data['next_action'] = _next_action(data, active)
        return data
    try:
        outcome = runtime_client.invoke(active,'call',call)
    except runtime_client.RuntimeFailure as error:
        record_completions(active, call)
        data = {**error.data,'allowed_actions':[]}
        data['next_action'] = _next_action(data, active)
        return data
    record_completions(active, call)
    return _present(active,outcome)


def advance(context, call=None):
    with context.locked():
        review_operations.ensure_idle(context)
        ensure_idle(context)
        if call is None and context.process == 'implement':
            import implementation_flows
            call = implementation_flows.call(context)
        return _advance(context,call or context.event)


def parse_answer(context, text):
    """alpha2 Step 4 answer form: `1:A / 2:C 理由 / 1-3:D 理由`, or `全件:A`."""
    record = review_contract.read(context)
    scopes = review_contract.scopes(context)
    relevant = [f for scope in scopes for f in record.relevant(scope)]
    latest = {scope: record.latest(scope).number for scope in scopes}
    undecided = [f for f in relevant if not f.has_decision]
    parts = [p.strip() for p in re.split(r'[／/\n]', text or '') if p.strip()]
    if not parts:
        raise ValueError('answer is empty')
    decisions = []
    for part in parts:
        m = re.fullmatch(r'(全件|(?:(feature:[a-z0-9][a-z0-9_-]*|phase|cross)\s+)?(?:(\d+)-)?(\d+))\s*[:：]\s*([A-DＡ-Ｄ])\s*(.*)', part)
        if not m:
            raise ValueError('answer must look like `1:A` / `2:C 理由` / `全件:A`: %s' % part)
        letter = m.group(5).translate(str.maketrans('ＡＢＣＤ', 'ABCD'))
        value, reason = LETTERS[letter], m.group(6).strip()
        if m.group(1) == '全件':
            if not undecided:
                raise ValueError('no undecided findings for 全件')
            decisions += [(f.scope, f.run, f.number, value, reason) for f in undecided]
            continue
        scope = m.group(2) or (scopes[-1] if len(scopes) == 1 else None)
        if scope is None:
            raise ValueError('several scopes are reviewed together; prefix the scope (e.g. `feature:x 1:A`)')
        run = int(m.group(3)) if m.group(3) else latest[scope]
        decisions.append((scope, run, int(m.group(4)), value, reason))
    for scope, run, number, value, reason in decisions:
        if value in ('対応せず進める', '未対応') and not reason:
            raise ValueError('理由が必要です: %s run %s #%s' % (scope, run, number))
    return decisions


def operate(context, kind, payload, actor=''):
    with context.locked():
        if context.process == 'implement':
            import implementation_flows
            implementation_flows.require_current(context)
        opid = payload.get('operation_id')
        if not isinstance(opid,str) or not re.fullmatch(r'[A-Za-z0-9][A-Za-z0-9_.:-]{0,127}',opid):
            raise ValueError('a stable operation_id is required')
        request = {'kind':kind,'payload':payload,'actor':actor,'event':context.event,'item':context.item,
                   'root':context.root,'state':context.state_path}
        entries = dict(workflow_state.workflow(context).get('host_operations',{}))
        entry = entries.get(opid)
        if entry:
            if entry['request'] != request:
                raise ValueError('operation ID already used with different content')
            if entry['status'] == 'finished':
                return {**entry['output'],'replayed':True}
        ensure_idle(context,opid)
        review_operations.ensure_idle(context,opid)
        action = payload.get('action') if kind == 'respond' else None
        if not entry:
            if kind == 'submit':
                receipt = payload.get('dispatch')
                unit = _matching(context,receipt)
                if receipt['status'] != 'emit' or unit['type'] != 'skill':
                    raise ValueError('submit requires an emitted Skill')
                data = payload['result']
                if unit.get('isAgent'):
                    if data.get('status') not in ('completed','failed'):
                        raise ValueError('inspector result must be completed or failed')
                    if data.get('status') == 'completed':
                        import check_gate_write_scope
                        try:
                            check_gate_write_scope.validate_staged(context)
                        except ValueError as error:
                            raise ValueError('検査記録の形式に不備があります（%s）。検査役（check-runner）をもう一度実行して '
                                             'inspection_path を書き直し、同じ dispatch で submit し直してください' % error)
                    if context.process == 'implement' and data['status'] == 'completed':
                        import implementation_checks
                        implementation_checks.validate_semantic(context, data)
                else:
                    authoring_results.validate(context,data)
                result = {'completed':'ok','waiting':'wait','failed':'fail'}[data['status']]
                workflow_state.audit(context)
                workflow_state.preflight(context)
                # Audit may schedule a redo after an upstream edit. Do not
                # prepare an operation against a receipt that it invalidated.
                _matching(context, receipt)
            else:
                if action not in RESPONSES:
                    raise ValueError('unsupported human response action')
                review_actions.person(actor)
                if action in ('accept-plan', 'change-plan'):
                    receipt = payload.get('dispatch')
                    unit = _matching(context,receipt)
                    if receipt['status'] != 'wait' or not (unit.get('gate') == 'plan' or context.event.endswith('-plan')):
                        raise ValueError('%s requires its actual plan wait' % action)
                    if action == 'change-plan':
                        if context.process not in ('requirements','design','tasks'):
                            raise ValueError('this plan is not per feature; record conditions as the accept-plan note')
                        if not (payload.get('data') or {}).get('instruction'):
                            raise ValueError('change-plan requires the actual instruction')
                else:
                    expected = payload.get('expected')
                    review_gate.require(context,expected)
                    data = payload.get('data') or {}
                    if action == 'decisions':
                        for scope, run, number, value, reason in parse_answer(context, data.get('answer', '')):
                            review_actions.prepare_response(context,'decision',{'scope':scope,'run':run,'number':number,'decision':value,'reason':reason},actor)
                    elif action == 'repair':
                        owner = _owner(context, data)
                        repair_actions.request(owner, data, actor, apply=False)
                    else:
                        review_actions.prepare_response(context,action,data,actor)
                    receipt = runtime_client.invoke(context,'status',expected['call'])['dispatch']
                result = 'ok'
            entry = {'status':'prepared','request':request,'dispatch':receipt,'result':result}
            if action == 'decisions':
                # Freeze 全件 before any child decision changes the live set.
                entry['decisions'] = parse_answer(context, (payload.get('data') or {}).get('answer', ''))
            entries[opid] = entry
            _save(context,entries)
        receipt = entry['dispatch']
        answers_generate_review = kind == 'respond' and action == 'repair' and repair_actions.is_generate(context)
        if entry['status'] == 'prepared' and answers_generate_review:
            # The human's repair selection answers this -generate review; report it
            # before the repair's runtime invalidations discard the pending dispatch.
            runtime_client.invoke(context,'report',receipt['call'],result='ok',dispatch_id=receipt['id'])
            entry['status'] = 'answered'
            _save(context,entries)
        if entry['status'] in ('prepared', 'answered'):
            if kind == 'submit':
                unit = _matching(context,receipt)
                workflow_state.audit(context)
                workflow_state.preflight(context)
                if not unit.get('isAgent'):
                    authoring_results.save(context,payload['result'])
                    if entry['result'] == 'wait':
                        import workflow
                        workflow.dispatch(context,'wait',payload['result'],'')
                elif context.process == 'implement' and entry['result'] == 'ok':
                    import implementation_checks
                    implementation_checks.save_semantic(context, payload['result'])
            else:
                import workflow
                data = dict(payload.get('data') or {})
                if action == 'accept-plan':
                    _matching(context,receipt)
                    workflow.dispatch(context,action,data,actor)
                elif action == 'change-plan':
                    _matching(context,receipt)
                    feature = aidd_paths.Context(context.root, context.state_path, aidd_paths.RULES['feature']['generate'])
                    repair_actions.reopen(feature, ['.aidd/feature-list.md'], data['instruction'], 'plan-change', actor,
                                          resume_event=context.event, resume_item=context.item)
                elif action == 'repair':
                    repair_actions.request(_owner(context, data), data, actor)
                elif action == 'decisions':
                    for index, (scope, run, number, value, reason) in enumerate(entry['decisions']):
                        child_id = '%s.%d' % (opid, index)
                        previous = workflow_state.workflow(context).get('review_operations', {}).get(child_id)
                        expected = previous['request']['expected'] if previous else review_gate.current(context, receipt['call'])
                        review_actions.decision(context, scope, run, number, value, reason, actor,
                                                expected=expected, operation_id=child_id)
                else:
                    data.update(expected=payload['expected'], operation_id=opid)
                    workflow.dispatch(context,action,data,actor)
                    # Consumer invalidation runs in _advance, after this review's
                    # L0 report. Redo before report would discard its live receipt.
                    if action == 'approve':
                        repair_actions.auto_clear(context, actor)
            entry['status'] = 'saved' if entry['status'] == 'prepared' else 'reported'
            _save(context,entries)
        if kind == 'respond' and action in ('decision','decisions','resolve'):
            output = {'status':'wait','allowed_actions':review_options(context),
                      'review_context':review_gate.current(context,receipt['call']),
                      'review':review_summary(context)}
            output['next_action'] = _next_action({'status':'wait','gate':'review'}, context)
        elif kind == 'respond' and action in ('change-plan', 'repair') and not answers_generate_review:
            if action == 'repair' and repair_actions.is_revise(context):
                output = _advance(context, receipt['call'])
            else:
                output = {'status':'rollback','allowed_actions':[],'blockers':[b for b in context.blockers() if b.get('status') != 'resolved'],
                          'next_action':'差戻し先の工程（blockers の target_event / target_item）を実行し、再承認後に upstream-approved を記録してから元の工程へ戻ってください。'}
                if action == 'repair':
                    owner = repair_actions.revise_context(_owner(context, payload.get('data') or {}))
                    output['repair'] = {'event': owner.event, 'item': owner.item, 'call': aidd_paths.RULES[owner.process]['call']}
                    if not output['blockers']:
                        output['status'] = 'repair'
                        output['next_action'] = '修正の工程（%s%s）を実行し、再検査後に元の検査をやり直してください。' % (
                            owner.event, ' --item ' + owner.item if owner.item else '')
        else:
            if entry['status'] == 'saved':
                # L0 deduplicates this exact dispatch/result even if its reply was lost.
                runtime_client.invoke(context,'report',receipt['call'],result=entry['result'],dispatch_id=receipt['id'])
                entry['status'] = 'reported'
                _save(context,entries)
            if entry['result'] == 'ok':
                output = _advance(context,receipt['call'])
            else:
                output = {'status':'waiting' if entry['result']=='wait' else 'fail',
                          'allowed_actions':['answer','repair'] if entry['result']=='wait' else [],
                          'result':payload.get('result')}
                output['next_action'] = ('作成中の質問に回答してください（差戻し候補がある場合は差戻しも選べます）。'
                                         if entry['result'] == 'wait' else _next_action({'status':'fail'}, context))
        output.update(operation_id=opid,operation_applied=True)
        entry.update(status='finished',output=output)
        _save(context,entries)
        return output


def _owner(context, data):
    """The owner of a repair: explicit event/item in the answer, else this phase's own item."""
    event = data.get('event') or aidd_paths.RULES[context.process]['generate']
    item = data.get('item') if 'item' in data else (context.item if aidd_paths.RULES.get(aidd_paths.PROCESS_OF.get(event, ''), {}).get('per_feature') else '')
    return aidd_paths.Context(context.root, context.state_path, event, item or '')
