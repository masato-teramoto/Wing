"""Bind task-scoped L4 reviews to L0 dispatch and the existing task execution.

The review's gates publish the emit's context (gate_exchange) and verify the result the
generic host stored at submit; nothing outside the gates interprets it.
"""
import copy
import difflib
import prerequisites

import gate_exchange
import implementation_requests as requests
import implementation_store as store
import task_code_review as quality
import task_quality_storage as storage
import task_code_review_mcp as mcp

PREPARE = 'task-code-review-prepare'
REVIEW = 'task-code-review'


def enabled(execution):
    return quality.enabled(execution)


def applicable(context):
    execution = requests.preflight(context)
    return enabled(execution) and not store.empty_revision(context, execution)


def pointer(execution):
    value = execution.get('code_review')
    if not value or value.get('attempt') != len(execution.get('retries', [])):
        raise ValueError('current task code review is missing; run preparation first')
    return value


def previous(context, execution):
    old = execution.get('code_review')
    if old:
        # A failed review stops its action before the next gate; seal it now so its findings are retained.
        ingest(context, execution, old)
        path = storage.path(context.root, execution['execution_id'], old['round'], 'code-review.json')
        if path.exists():
            request, receipt = quality.load(context, execution, old, current=False)
            findings = receipt['review']['findings']
            if receipt['review']['status'] == 'failed':
                # An incomplete inspection cannot erase or downgrade earlier open issues.
                retained = {row['id']: row for row in findings}
                retained.update({row['id']: row for row in (request.get('previous') or {}).get('findings', [])})
                findings = list(retained.values())
            return {'reference': copy.deepcopy(old), 'findings': findings,
                    'inputs': request['inputs'], 'receipt': receipt}
        name = 'code-request.json' if old.get('request_sha256') else 'code-preparation.json'
        return storage.read(context.root, execution['execution_id'], old['round'], name)['previous']
    return None


def prepare(context):
    execution = requests.preflight(context)
    if not applicable(context):
        raise ValueError('task code review is not applicable')
    result = store.read(context.root, store.BASE + '/runs/' + execution['execution_id'] + '/result.json')
    requests.validate_result(context, result)
    if result['status'] != 'completed':
        raise ValueError('completed work is required before code review')
    old = execution.get('code_review')
    attempt = len(execution.get('retries', []))
    if old and old['attempt'] == attempt and old.get('request_sha256'):
        request = quality.verify_request(context, execution, old)
        if request['mcp']['status'] == 'failed':
            raise ValueError('MCP inspection incomplete; evidence retained; use implement-retry to inspect again')
        return request
    if old and old['attempt'] == attempt:
        number = old['round']
        request = storage.read(context.root, execution['execution_id'], number, 'code-preparation.json')
        prior = request['previous']
        if quality.snapshot(context, execution) != request['inputs']:
            raise ValueError('task review inputs changed during MCP preparation; retry the task')
    else:
        prior = previous(context, execution)
        number = old['round'] + 1 if old else 1
        request = quality.make_request(context, execution, number, requests.task_context(context)['task'], prior)
        storage.write_once(context.root, execution['execution_id'], number, 'code-preparation.json', request)
        execution['code_review'] = {'round': number, 'attempt': attempt, 'request_sha256': None}
        store.write(context.root, store.execution_path(execution['execution_id']), execution)
    request['mcp'] = mcp.prepare(context, execution, request, prior)
    if quality.snapshot(context, execution) != request['inputs']:
        raise ValueError('task review inputs changed while MCP was running; retry the task')
    storage.write_once(context.root, execution['execution_id'], number, 'code-request.json', request)
    current = {'round': number, 'attempt': attempt, 'request_sha256': store.fingerprint(request)}
    description_only = bool(execution.get('quality_instructions', {}).get('corrections'))
    if (description_only and prior and prior['inputs'] == request['inputs']
            and prior.get('receipt') and prior['receipt']['review']['status'] == 'completed'
            and not any(row['severity'] in ('critical', 'major') for row in prior['findings'])):
        receipt = {'schema': 1, 'request_sha256': current['request_sha256'],
                   'host_review': prior['receipt']['host_review'], 'review': prior['receipt']['review'], 'reused_from': prior['reference']}
        save_receipt(context, execution, current, request, receipt)
    execution['code_review'] = current
    store.write(context.root, store.execution_path(execution['execution_id']), execution)
    if request['mcp']['status'] == 'failed':
        raise ValueError('MCP inspection incomplete; evidence retained; use implement-retry to inspect again')
    return request


def current_request(context, execution):
    request = quality.verify_request(context, execution, pointer(execution))
    if request['mcp']['status'] not in ('completed', 'not_applicable'):
        raise ValueError('MCP inspection incomplete; retry before dispatching the host review')
    return request


def needs_model(context):
    execution = requests.preflight(context)
    current = pointer(execution)
    current_request(context, execution)
    if storage.path(context.root, execution['execution_id'], current['round'], 'code-review.json').exists():
        _, receipt = quality.load(context, execution, current)
        return not bool(receipt.get('reused_from'))
    return True


def review_context(context):
    execution = requests.preflight(context)
    request = current_request(context, execution)
    # Earlier full requests stay on disk, not in every model context.
    compact = copy.deepcopy(request)
    compact['inputs'].pop('source_text')
    previous = compact.get('previous')
    if previous:
        before = previous['inputs']['source_text']
        after = request['inputs']['source_text']
        compact['previous'] = {'findings': previous['findings'], 'reference': previous['reference'],
            'changed_since_review': {p: ''.join(difflib.unified_diff((before.get(p) or '').splitlines(True),
                (after.get(p) or '').splitlines(True), fromfile='previous/' + p, tofile='current/' + p))
                for p in sorted(set(before) | set(after)) if before.get(p) != after.get(p)}}
    return {'profile': quality.PROFILE, 'request': compact, 'request_sha256': store.fingerprint(request),
            'required_aspects': quality.ASPECTS,
            'unreviewed_inputs': prerequisites.unreviewed_inputs(context, request['inputs']['upstream']),
            'required_paths': sorted(set(request['inputs']['code']) | set(request['inputs']['deleted'])
                                     | set(request['inputs']['upstream']) | set(request['inputs']['checks']))}


def publish(context):
    """What the review Skill's emit shows, or why it is skipped (the host relays it; it never interprets it)."""
    import implementation_task_review as task_review

    if not applicable(context):
        return gate_exchange.publish(context, REVIEW, skip='省略=該当なし（タスクのコードレビュー対象外）',
                                     evidence=task_review.publication_evidence(context, 'skip'))
    if not needs_model(context):
        return gate_exchange.publish(context, REVIEW, skip='省略=既存結果を再利用（説明のみの訂正）',
                                     evidence=task_review.publication_evidence(context, 'code'))
    evidence = task_review.publication_evidence(context, 'code')
    return gate_exchange.publish(context, REVIEW, output={
        'context': review_context(context),
        'next_action': '作業中（AI が今回のタスクの実コード・テストを検査します）。人の操作は不要です。'}, evidence=evidence)


def verify_submitted(context, execution, current, receipt):
    """Bind a sealed review, including reused rounds, to its actual submit."""
    source = receipt.get('reused_from')
    if source:
        _, original = quality.load(context, execution, source, current=False)
        return verify_submitted(context, execution, source, original)
    submitted = gate_exchange.result(context, REVIEW, attempt=current['attempt'])
    if gate_exchange.rejected(context, REVIEW, 'result', submitted):
        raise ValueError('sealed task code review comes from a rejected submission')
    if submitted['result'] != receipt['host_review']:
        raise ValueError('submitted task code review differs from its sealed receipt')
    return submitted


def ingest(context, execution, current=None):
    """Verify and save the review the host stored for `current` (the live round unless given)."""
    live = current is None
    current = pointer(execution) if live else current
    if not current.get('request_sha256'):
        return
    if storage.path(context.root, execution['execution_id'], current['round'], 'code-manifest.json').exists():
        _, receipt = quality.load(context, execution, current, current=live)
        verify_submitted(context, execution, current, receipt)
        return
    request = (current_request(context, execution) if live
               else quality.verify_request(context, execution, current, current=False))
    partial = storage.path(context.root, execution['execution_id'], current['round'], 'code-review.json').exists()
    stored = gate_exchange.result(context, REVIEW, attempt=current['attempt'], required=live or partial)
    if stored is None:
        return
    if gate_exchange.rejected(context, REVIEW, 'result', stored):
        if partial:
            raise ValueError('rejected review result has a saved review artifact')
        if live:
            raise ValueError('this code review result was rejected; retry and submit to the new dispatch')
        return  # The preceding request's validated findings remain in previous().
    try:
        integrated = quality.integrate(request, stored['result'])
    except (ValueError, KeyError, TypeError) as error:
        if partial:
            raise ValueError('saved review artifact cannot be reconstructed from its raw result') from error
        gate_exchange.reject(context, REVIEW, 'result', stored, str(error))
        if live:
            raise ValueError('code review result rejected; retry and submit to the new dispatch: ' + str(error)) from error
        return
    save_receipt(context, execution, current, request,
                 {'schema': 1, 'request_sha256': current['request_sha256'], 'host_review': copy.deepcopy(stored['result']),
                  'review': integrated, 'reused_from': None})
    _, receipt = quality.load(context, execution, current, current=live)
    verify_submitted(context, execution, current, receipt)


def save_receipt(context, execution, current, request, receipt):
    number = current['round']
    hashes = {'code-request.json': store.digest(storage.path(context.root, execution['execution_id'], number, 'code-request.json').read_bytes())}
    hashes['code-review.json'] = storage.write_once(context.root, execution['execution_id'], number, 'code-review.json', receipt)
    hashes['code-summary.md'] = storage.write_once(context.root, execution['execution_id'], number, 'code-summary.md',
                                                  quality.summary(request, receipt).encode('utf-8'))
    storage.write_once(context.root, execution['execution_id'], number, 'code-manifest.json', {'schema': 1, 'files': hashes})


def validate(context, data, save=False):
    execution = requests.preflight(context)
    current = pointer(execution)
    request = current_request(context, execution)
    result = quality.integrate(request, data)
    if save:
        save_receipt(context, execution, current, request,
                     {'schema': 1, 'request_sha256': current['request_sha256'], 'host_review': copy.deepcopy(data), 'review': result, 'reused_from': None})
    return result


def receipt(context, execution, current=True):
    return quality.load(context, execution, pointer(execution), current)


def marker(context, execution, current=True):
    request, value = receipt(context, execution, current)
    return {'target': request['target'], 'receipt_sha256': store.fingerprint(value)}


def presentation(context, execution):
    request, value = receipt(context, execution)
    return {'mcp': request['mcp'], 'code_review': value['review'], 'code_review_reused': bool(value.get('reused_from')),
            'code_review_summary': storage.directory(execution['execution_id'], pointer(execution)['round']) + '/code-summary.md'}


def validate_approval(context, execution, data, current=True):
    _, value = receipt(context, execution, current)
    quality.approve(value, data)


def acceptance(context, execution, response, save=False, current=True):
    value = marker(context, execution, current)
    if response['action'] != 'approve' or response['expected'].get('code_review') != value:
        raise ValueError('task code review lacks a matching actual continue response')
    validate_approval(context, execution, response['data'], current)
    proof = {'schema': 1, **value, 'response_sha256': store.fingerprint(response)}
    number = pointer(execution)['round']
    if save:
        storage.write_once(context.root, execution['execution_id'], number, 'code-acceptance.json', proof)
    elif storage.read(context.root, execution['execution_id'], number, 'code-acceptance.json') != proof:
        raise ValueError('task code review acceptance changed')
    return proof
