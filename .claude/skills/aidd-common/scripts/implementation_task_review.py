"""Task identity, generation binding and the real human response, verified inside L4 gates.

L0's GateExecutor runs these gates from gate.yaml. The generic host (L3) only relays: it shows
what a gate published, and stores the agent result and the human answer (gate_exchange) for the
next gate here to verify. Generation and verification criteria remain in L4.
"""
import gate_exchange
import implementation_requests as requests
import implementation_store as store
import location_identity
import review_decisions
import review_gate
import task_quality
import task_code_review
import task_quality_inputs as inputs
import task_quality_storage as storage
import project_progress
import prerequisites
import implementation_code_review as code_review

GENERATE = 'task-specification-generate'
WAIT = 'task-specification-review'


def task_context(context):
    return requests.kind(context) == 'task'


def applicable(context):
    execution = requests.preflight(context)
    return bool(inputs.scope_of(execution)) and not store.empty_revision(context, execution)


def confirmation_applicable(context):
    execution = requests.preflight(context)
    return (bool(inputs.scope_of(execution)) or code_review.enabled(execution)) and not store.empty_revision(context, execution)


def response_slot(execution):
    if inputs.scope_of(execution):
        return pointer(execution)['round'], 'response.json'
    return code_review.pointer(execution)['round'], 'code-response.json'


def pointer(execution):
    value = execution.get('task_quality')
    if not value or value.get('attempt') != len(execution.get('retries', [])):
        raise ValueError('current task specification request is missing; run the preparation gate')
    return value


def previous(context, execution):
    old = execution.get('task_quality')
    if old:
        if storage.path(context.root, execution['execution_id'], old['round'], 'manifest.json').exists():
            return task_quality.reference(context.root, execution['execution_id'], old['round'])
        return storage.read(context.root, execution['execution_id'], old['round'], 'request.json')['previous']
    state = requests.feature_state(context, execution['feature'])
    latest = state.get('specifications', {}).get(inputs.scope_of(execution))
    if latest:
        return latest
    candidates = list(state['completed'].values())
    if execution.get('previous_execution'):
        candidates.append(execution['previous_execution'])
    for proof in reversed(candidates):
        prior = store.read(context.root, store.execution_path(proof['execution_id']))
        if inputs.scope_of(prior) == inputs.scope_of(execution) and prior.get('task_quality'):
            return task_quality.reference(context.root, prior['execution_id'], prior['task_quality']['round'])
    return None


def prepare(context):
    execution = requests.preflight(context)
    if not applicable(context):
        raise ValueError('task specification generation is not applicable')
    result = store.read(context.root, store.BASE + '/runs/' + execution['execution_id'] + '/result.json')
    if result['status'] != 'completed':
        raise ValueError('completed task work is required before specification generation')
    requests.validate_result(context, result)
    attempt = len(execution.get('retries', []))
    old = execution.get('task_quality')
    if old and old['attempt'] == attempt:
        return task_quality.verify_request(context, execution, old)
    round_number = old['round'] + 1 if old else 1
    instructions = execution.get('quality_instructions', {})
    if instructions.get('attempt') != attempt:
        instructions = {}
    request = task_quality.make_request(context, execution, round_number, previous(context, execution), instructions)
    storage.write_once(context.root, execution['execution_id'], round_number, 'request.json', request)
    execution['task_quality'] = {'round': round_number, 'attempt': attempt, 'request_sha256': store.fingerprint(request)}
    store.write(context.root, store.execution_path(execution['execution_id']), execution)
    return request


def check_corrections(context):
    """Description corrections from a repair answer must name existing case IDs with an actual reason."""
    execution = requests.preflight(context)
    instructions = execution.get('quality_instructions', {})
    corrections = instructions.get('corrections') if instructions.get('attempt') == len(execution.get('retries', [])) else None
    if corrections is not None and not isinstance(corrections, dict):
        raise ValueError('description corrections must be an object')
    if not corrections:
        return
    old, ids = execution.get('task_quality'), set()
    if inputs.scope_of(execution) and old:
        if old.get('attempt') == len(execution.get('retries', [])):
            # Preparation has already advanced the pointer. Corrections still
            # refer to the reviewed version, not this ungenerated/new version.
            request = task_quality.verify_request(context, execution, old)
            specification = task_quality.previous_snapshot(context.root, request['previous'],
                                                           execution['feature'], request['scope'])
        else:
            result, _ = task_quality.load(context, execution, old, current=False)
            specification = result['specification']
        ids = {row['id'] for row in (specification or {}).get('cases', [])}
    for key, reason in corrections.items():
        if key not in ids or not isinstance(reason, str) or not reason.strip():
            raise ValueError('description corrections require an existing case ID and actual reason')


def publication_evidence(context, kind):
    """Select L4 dependencies for L3's neutral, pre-report freshness check.

    A dispatch snapshot excludes the result it is asking for. Completed review
    bundles are only included once available, before the human confirmation.
    """
    from pathlib import Path

    import code_review_mcp as adapter
    import implementation_completion as completion
    import implementation_task_completion as task_completion
    import task_code_review_mcp as mcp

    execution = requests.preflight(context)
    if kind == 'skip':
        return completion.capture(context, execution, artifacts=[],
                                  execution_bindings=task_completion.EXECUTION_BINDINGS)
    if kind == 'confirmation':
        return completion.capture(context, execution,
                                  **task_completion.dependencies(context, execution, accepted=False))
    evidence = task_completion.Evidence(context, execution)
    execution_id = execution['execution_id']
    directory = store.BASE + '/runs/' + execution_id
    current_artifacts, environment_files = [], []
    if kind == 'generation':
        request = evidence.read(execution_id, pointer(execution)['round'], 'request.json')
        previous = request.get('previous')
        if previous:
            evidence.collect('specification', previous['execution_id'], previous['round'])
        evidence.paths.update(directory + '/' + name for name in request['inputs']['checks'])
        checks = ('red.json', 'green.json', 'verify.json', 'result.json')
        for name in ('red.json', 'green.json', 'verify.json'):
            if name in request['inputs']['checks']:
                for receipt in store.read(context.root, directory + '/' + name)['receipts']:
                    current_artifacts.extend(receipt[key]['path'] for key in ('stdout', 'stderr'))
    elif kind == 'code':
        request = evidence.read(execution_id, code_review.pointer(execution)['round'], 'code-request.json')
        reference = request['mcp']['reference']
        evidence.collect('mcp', reference['execution_id'], reference['round'])
        previous = (request.get('previous') or {}).get('reference')
        if previous:
            evidence.collect('code', execution_id, previous['round'], previous['attempt'])
        evidence.paths.update(request['inputs']['checks'])
        checks = ('red.json', 'green.json', 'verify.json')
        current_artifacts = list(task_code_review.RULE_FILES) + [
            str(Path(mcp.__file__).with_name(name)) for name in mcp.RULES]
        environment_files = [{'variable': 'AIDD_CODE_REVIEW_SETTINGS',
                              'default': str(Path(adapter.__file__).with_name('code_review.json'))}]
    else:
        raise ValueError('unknown task publication evidence kind')
    return completion.capture(context, execution, artifacts=sorted(evidence.paths),
                              current_artifacts=sorted(set(current_artifacts)),
                              current_optional_artifacts=[directory + '/' + name for name in checks],
                              inventories=[False, True], environment_files=environment_files,
                              execution_bindings=task_completion.EXECUTION_BINDINGS,
                              operations=sorted(evidence.operations))


def publish_generation(context):
    """What the generation Skill's emit shows (the host relays it; it never interprets it)."""
    if not applicable(context):
        return gate_exchange.publish(context, GENERATE, skip='省略=該当なし（仕様書の生成対象外）',
                                     evidence=publication_evidence(context, 'skip'))
    evidence = publication_evidence(context, 'generation')
    return gate_exchange.publish(context, GENERATE, output={
        'context': generation_context(context),
        'next_action': '作業中（AI が実テストから単体テスト仕様書を生成します）。人の操作は不要です。'}, evidence=evidence)


def generation_context(context):
    execution = requests.preflight(context)
    request = task_quality.verify_request(context, execution, pointer(execution))
    return {'profile': task_quality.PROFILE, 'request': request, 'request_sha256': store.fingerprint(request),
            'previous_specification': task_quality.previous_snapshot(context.root, request['previous'],
                                                                    execution['feature'], request['scope']),
            'task': requests.task_context(context)['task'],
            'unreviewed_inputs': prerequisites.unreviewed_inputs(context, request['inputs']['upstream']),
            'instruction': request['instruction'], 'mcp': request['mcp']}


def validate_generation(context, data, save=False):
    execution = requests.preflight(context)
    request = task_quality.verify_request(context, execution, pointer(execution))
    return task_quality.save(context, request, data) if save else task_quality.generate(context, request, data)


def _record_specification(context):
    """The generated suite specification this task contributes to the feature (L3 carries it at completion)."""
    execution = store.read_execution(context)
    scope = inputs.scope_of(execution)
    if not scope:
        return
    reference = task_quality.reference(context.root, execution['execution_id'], execution['task_quality']['round'])
    execution.setdefault('feature_records', {}).setdefault('specifications', {})[scope] = reference
    store.write(context.root, store.execution_path(execution['execution_id']), execution)


def ingest_generation(context, execution=None):
    """Validate generation before code-review preparation, with repeatable immutable saves."""
    execution = execution or requests.preflight(context)
    if inputs.scope_of(execution) and not store.empty_revision(context, execution):
        current = pointer(execution)
        # result() also verifies the actual submit operation. Do not bypass
        # that origin check when resuming after the immutable bundle was saved.
        submitted = gate_exchange.result(context, GENERATE)
        request = task_quality.verify_request(context, execution, current)
        if gate_exchange.rejected(context, GENERATE, 'result', submitted):
            raise ValueError('this generation result was rejected; retry and submit to the new dispatch')
        if not storage.path(context.root, execution['execution_id'], current['round'], 'manifest.json').exists():
            # Verify existing inputs/history separately: a corrupt artifact is
            # never classified as a correctable agent submission.
            task_quality.previous_snapshot(context.root, request['previous'], execution['feature'], request['scope'])
            try:
                result = task_quality.generate(context, request, submitted['result'])
            except (ValueError, KeyError, TypeError) as error:
                task_quality.verify_request(context, execution, current)
                task_quality.previous_snapshot(context.root, request['previous'], execution['feature'], request['scope'])
                gate_exchange.reject(context, GENERATE, 'result', submitted, str(error))
                raise ValueError('generation result rejected; retry and submit to the new dispatch: ' + str(error)) from error
            # Interrupted immutable publication resumes from the same validated
            # raw result; mismatched existing files remain hard failures.
            storage.save_bundle(context.root, execution['execution_id'], current['round'], result, task_quality.summary(result))
        saved, _ = task_quality.load(context, execution, current)
        if task_quality.generate(context, request, submitted['result']) != saved:
            raise ValueError('submitted task specification differs from its sealed result')
        _record_specification(context)


def ingest(context):
    """Verify and save the agent results the host stored for this attempt (resumable, write-once)."""
    execution = requests.preflight(context)
    ingest_generation(context, execution)
    if code_review.enabled(execution):
        code_review.ingest(context, execution)


ANSWERS = {'approve': {'required': {'answer': 'text'}},
           'hold': {'required': {'answer': 'text'}},
           'repair': {'required': {'instruction': 'text'}, 'optional': {'corrections': 'object'}}}


def publish_confirmation_skip(context):
    """A requiresHuman gate always becomes a wait in L0; publish why this one does not apply."""
    if confirmation_applicable(context):
        raise ValueError('applicable task confirmation cannot be skipped')
    return gate_exchange.publish(context, WAIT, skip='省略=該当なし（タスク確認の対象外）',
                                 evidence=publication_evidence(context, 'skip'))


def publish_confirmation(context):
    """What the human wait shows, its review target, and the answer fields the host checks."""
    if not confirmation_applicable(context):
        return publish_confirmation_skip(context)
    evidence = publication_evidence(context, 'confirmation')
    execution = requests.preflight(context)
    answers = {key: {'required': dict(value['required']), 'optional': dict(value.get('optional', {}))}
               for key, value in ANSWERS.items()}
    if code_review.enabled(execution):
        answers['approve']['optional']['dispositions'] = 'object'
    actions = allowed_actions(context)
    next_action = ('今回の確認資料とレビュー結果を確認し、続行・修正・保留を回答してください。' if 'approve' in actions
                   else '修正が必要な指摘を確認し、修正・保留を回答してください。')
    return gate_exchange.publish(context, WAIT, output={'allowed_actions': actions, **presentation(context),
                                                        'next_action': next_action},
                                 review_context=marker(context), answers=answers, evidence=evidence)


def marker(context):
    execution = requests.preflight(context)
    value = {'unit': context.unit}
    if inputs.scope_of(execution):
        result, manifest = task_quality.load(context, execution, pointer(execution))
        value.update(target=result['target'], manifest_sha256=store.fingerprint(manifest))
    if code_review.enabled(execution):
        value['code_review'] = code_review.marker(context, execution)
        value.setdefault('target', value['code_review']['target'])
    return value


def presentation(context):
    execution = requests.preflight(context)
    exemption = execution['policy']['tasks'][execution['task_id']].get('review_exemption')
    value = {'mcp': {'status': 'not_applicable', 'reason': exemption or 'task_review設定なし'}}
    if inputs.scope_of(execution):
        result, manifest = task_quality.load(context, execution, pointer(execution))
        directory = storage.directory(execution['execution_id'], pointer(execution)['round'])
        value.update(specification=directory + '/specification.md', report_summary=directory + '/summary.md',
                     changes=result['specification']['changes'], no_cases_reason=result['no_cases_reason'])
    if code_review.enabled(execution):
        value.update(code_review.presentation(context, execution))
    return value


def allowed_actions(context):
    execution = requests.preflight(context)
    if code_review.enabled(execution):
        _, receipt = code_review.receipt(context, execution)
        if receipt['review']['status'] != 'completed' or any(row['severity'] in ('critical', 'major') for row in receipt['review']['findings']):
            return ['repair', 'hold']
    return ['approve', 'repair', 'hold']


def take_response(context, execution):
    """Verify the approval the host stored for this wait, then seal it into this round (write-once)."""
    stored = gate_exchange.answer(context, WAIT)
    review_decisions.person(stored['actor'])
    if stored['action'] != 'approve':
        raise ValueError('task confirmation requires an actual continue response')
    current = marker(context)
    if any(stored['expected'].get(key) != value for key, value in current.items() if key != 'unit'):
        raise review_gate.OperationRejected('task confirmation belongs to different generated artifacts')
    if code_review.enabled(execution):
        _, receipt = code_review.receipt(context, execution)
        if gate_exchange.rejected(context, WAIT, 'answer', stored):
            raise ValueError('this task answer was rejected; retry and answer the new confirmation')
        try:
            task_code_review.approve(receipt, stored['data'])
        except (ValueError, KeyError, TypeError) as error:
            gate_exchange.reject(context, WAIT, 'answer', stored, str(error))
            raise ValueError('task answer rejected; retry and answer the new confirmation: ' + str(error)) from error
    value = {'schema': 1, 'operation_id': stored['operation_id'], 'action': stored['action'], 'actor': stored['actor'],
             'data': stored['data'], 'expected': stored['expected']}
    number, name = response_slot(execution)
    storage.write_once(context.root, execution['execution_id'], number, name, value)


def recorded_response(context, execution):
    number, name = response_slot(execution)
    value = storage.read(context.root, execution['execution_id'], number, name)
    # The host operation journal is L0's (`host_operations` in the state store).
    entry = context.state().get('host_operations', {}).get(value['operation_id'])
    request = entry.get('request', {}) if entry else {}
    payload = request.get('payload', {})
    if (not entry or entry['status'] not in ('reported', 'finished') or request.get('kind') != 'respond'
            or request.get('event') != execution['event'] or request.get('item') != execution['task_item']
            or not location_identity.same_binding({key: request.get(key) for key in ('root', 'state')},
                                                  {'root': context.root, 'state': context.state_path})
            or request.get('actor') != value['actor'] or payload.get('action') != value['action']
            or payload.get('expected') != value['expected'] or payload.get('data') != value['data']
            or value['expected']['target']['execution_id'] != execution['execution_id']
            or value['expected']['target']['review_round'] != number):
        raise ValueError('task confirmation lacks its actual recorded human response')
    review_decisions.person(value['actor'])
    return value


def accept(context):
    execution = requests.preflight(context)
    take_response(context, execution)
    response = recorded_response(context, execution)
    code = code_review.acceptance(context, execution, response, save=True) if code_review.enabled(execution) else None
    return task_quality.accept(context, execution, pointer(execution), response) if inputs.scope_of(execution) else code


def require_accepted(context, execution, current=True):
    if not inputs.scope_of(execution) and not code_review.enabled(execution):
        return None
    response = recorded_response(context, execution)
    code = code_review.acceptance(context, execution, response, current=current) if code_review.enabled(execution) else None
    return task_quality.require_acceptance(context, execution, pointer(execution), response, current) if inputs.scope_of(execution) else code
