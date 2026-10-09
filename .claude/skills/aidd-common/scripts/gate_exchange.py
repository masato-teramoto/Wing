"""Records exchanged between Phase 8 task gates and the generic host, per task execution attempt.

L0's GateExecutor runs every gate from gate.yaml; nothing imports the gate's own scripts or Skills.
A task action's agent (emit) and human (wait) gates therefore meet the host only through these records:

| record | written by | read by |
|---|---|---|
| `published` | a script gate of the same action, before the unit is issued | the host (`host_session`): context / presentation of the emit or wait, or a reasoned skip |
| `result` | the host at submit (the agent's result as submitted, not interpreted) | a later gate, which verifies and saves it |
| `answer` | the host at respond (the human's answer as given, not interpreted) | a later gate, which verifies and accepts it |

L3 never interprets their content. Each record is bound to the execution, its attempt and the task
action (`binding.action`). An answer's `action` is the human operation, not that binding. Producers are trusted;
these checks reject missing/mismatched records, while gates verify their meaning and the host checks
the live dispatch before saving. A reissued dispatch can replace a record in the same attempt.
"""
import copy

import implementation_store as store
import location_identity

KINDS = ('published', 'result', 'answer')


def _binding(context, attempt=None):
    execution = store.read_execution(context)
    current = len(execution.get('retries', []))
    attempt = current if attempt is None else attempt
    if type(attempt) is not int or not 0 <= attempt <= current:
        raise ValueError('task gate record needs an existing execution attempt')
    return execution, attempt


def _path(execution, action, gate, attempt, kind):
    if kind not in KINDS or not isinstance(gate, str) or not gate:
        raise ValueError('unknown task gate record')
    return '%s/runs/%s/gates/%s/%s/%d-%s.json' % (store.BASE, execution['execution_id'], store.identifier(action),
                                                  store.identifier(gate), attempt, kind)


def record_path(context, gate, kind, attempt=None):
    """Project-relative evidence path, optionally for an earlier attempt of this execution."""
    execution, attempt = _binding(context, attempt)
    return _path(execution, context.action, gate, attempt, kind)


def _text(value):
    return isinstance(value, str) and bool(value.strip())


def _validate_payload(context, kind, record):
    """Check only the exchange shape and dispatch binding; gates own result/answer policy."""
    if kind == 'published':
        if (not {'skip', 'output', 'review_context', 'answers', 'evidence'} <= record.keys()
                or not isinstance(record['output'], dict)
                or (record['skip'] is not None and not _text(record['skip']))
                or any(record[key] is not None and not isinstance(record[key], dict)
                       for key in ('review_context', 'answers', 'evidence'))):
            raise ValueError('invalid published task gate record')
    elif kind == 'result':
        if not _text(record.get('dispatch_id')) or not isinstance(record.get('result'), dict):
            raise ValueError('invalid submitted task gate record')
    elif kind == 'answer':
        if (any(not _text(record.get(key)) for key in ('dispatch_id', 'operation_id', 'action', 'actor'))
                or not isinstance(record.get('data'), dict) or not isinstance(record.get('expected'), dict)):
            raise ValueError('invalid task gate answer record')
        expected = record['expected']
        binding = {'event': context.action, 'item': context.item, 'root': context.root,
                   'state': context.state_path, 'dispatch_id': record['dispatch_id']}
        if not location_identity.same_binding({key: expected.get(key) for key in binding}, binding):
            raise ValueError('task gate answer belongs to another dispatch')


def _record_binding(context, gate, kind, execution, attempt):
    return {'kind': kind, 'gate': gate, 'action': context.action, 'item': context.item,
            'execution_id': execution['execution_id'], 'attempt': attempt}


def _record(context, gate, kind, value, execution, attempt):
    record = {**copy.deepcopy(value), 'schema': 1,
              'binding': _record_binding(context, gate, kind, execution, attempt)}
    _validate_payload(context, kind, record)
    return record


def _write(context, gate, kind, value):
    execution, attempt = _binding(context)
    record = _record(context, gate, kind, value, execution, attempt)
    store.write(context.root, _path(execution, context.action, gate, attempt, kind), record)
    return record


def _validate_record(context, gate, kind, execution, attempt, record):
    if not isinstance(record, dict):
        raise ValueError('invalid task gate record')
    binding = record.get('binding')
    if (type(record.get('schema')) is not int or record['schema'] != 1
            or not isinstance(binding, dict) or type(binding.get('attempt')) is not int
            or binding != _record_binding(context, gate, kind, execution, attempt)):
        raise ValueError('task gate `%s` %s record belongs to another execution' % (gate, kind))
    _validate_payload(context, kind, record)
    return record


def _read(context, gate, kind, attempt=None, required=True):
    execution, attempt = _binding(context, attempt)
    path = _path(execution, context.action, gate, attempt, kind)
    try:
        record = store.read(context.root, path)
    except FileNotFoundError:
        if required:
            raise ValueError('task gate `%s` has no %s record for this attempt' % (gate, kind))
        return None
    return _validate_record(context, gate, kind, execution, attempt, record)


# --- published by a gate (read by the host) -------------------------------

def _validate_evidence(context, evidence):
    if evidence is not None:
        import implementation_completion
        implementation_completion.validate_snapshot(context, store.read_execution(context), evidence, current=True)


def _publication_key(context, gate, attempt):
    return '%s/%s/%d' % (store.identifier(context.action), store.identifier(gate), attempt)


def _publications(execution):
    values = execution.get('gate_publications', {})
    if not isinstance(values, dict):
        raise ValueError('invalid task gate publication bindings')
    return values


def _publication(execution, key):
    values = _publications(execution)
    value = values.get(key)
    if isinstance(value, dict):
        if (set(value) != {'sha256', 'record'} or not isinstance(value['record'], dict)
                or value['sha256'] != store.fingerprint(value['record'])):
            raise ValueError('task gate publication is changed or lacks its saved binding')
        return value['sha256'], value['record']
    if key in values and not isinstance(value, str):
        raise ValueError('invalid task gate publication binding')
    return value, None  # Existing executions saved only the raw fingerprint.


def _portable_publication(record):
    value = copy.deepcopy(record)
    if value['evidence'] is not None:
        import implementation_completion
        value['evidence'] = implementation_completion.portable_snapshot(value['evidence'])
    return value


def publish(context, gate, output=None, skip=None, review_context=None, answers=None, evidence=None):
    """Seal this attempt's presentation or reasoned skip before the unit is issued.

    Persist the original record and fingerprint together in the execution first.
    A move during an interrupted write can then replay those exact original bytes.
    An old unbound record cannot supply a decision.
    """
    if skip is not None and (not isinstance(skip, str) or not skip.strip()):
        raise ValueError('a skipped task gate needs its reason')
    _validate_evidence(context, evidence)
    execution, attempt = _binding(context)
    record = _record(context, gate, 'published', {'skip': skip, 'output': {} if output is None else output,
                                                'review_context': review_context, 'answers': answers,
                                                'evidence': evidence}, execution, attempt)
    path = _path(execution, context.action, gate, attempt, 'published')
    key = _publication_key(context, gate, attempt)
    fingerprint = store.fingerprint(record)
    publications = _publications(execution)
    pinned_hash, prepared = _publication(execution, key)
    previous = _read(context, gate, 'published', required=False)
    if previous is not None:
        if pinned_hash != store.fingerprint(previous):
            raise ValueError('task gate publication is changed or lacks its saved binding')
        prepared = previous
    if prepared is not None:
        _validate_record(context, gate, 'published', execution, attempt, prepared)
        _validate_evidence(context, prepared['evidence'])
        if _portable_publication(prepared) != _portable_publication(record):
            raise ValueError('immutable task gate publication differs; use a new attempt')
        record = prepared
    elif pinned_hash is not None and pinned_hash != fingerprint:
        # A legacy interrupted binding has no original record to reconstruct safely.
        raise ValueError('immutable task gate publication differs; explicitly rebase for revalidation')
    if previous is not None:
        return previous
    if key not in publications:
        execution['gate_publications'] = {**publications, key: {'sha256': fingerprint, 'record': record}}
        store.write(context.root, store.execution_path(execution['execution_id']), execution)
    store.write(context.root, path, record)
    return record


def published(context, gate):
    record = _read(context, gate, 'published')
    execution, attempt = _binding(context)
    fingerprint, _ = _publication(execution, _publication_key(context, gate, attempt))
    if fingerprint != store.fingerprint(record):
        raise ValueError('task gate publication is changed or lacks its saved binding')
    _validate_evidence(context, record['evidence'])
    return record


# --- written by the host (read by a later gate) ---------------------------

def save_result(context, gate, dispatch_id, result):
    previous = _read(context, gate, 'result', required=False)
    if previous and previous['dispatch_id'] == dispatch_id:
        if store.fingerprint(previous['result']) != store.fingerprint(result):
            raise ValueError('this dispatch already has a different submitted result')
        return previous
    return _write(context, gate, 'result', {'dispatch_id': dispatch_id, 'result': result})


def result(context, gate, attempt=None, required=True, *, allow_saved=False):
    record = _read(context, gate, 'result', attempt, required)
    if record is not None:
        record_operation(context, gate, 'result', record, allow_saved=allow_saved)
    return record


def save_answer(context, gate, dispatch_id, operation_id, action, actor, data, expected):
    value = {'dispatch_id': dispatch_id, 'operation_id': operation_id, 'action': action, 'actor': actor,
             'data': data, 'expected': expected}
    previous = _read(context, gate, 'answer', required=False)
    if previous and previous['dispatch_id'] == dispatch_id:
        if store.fingerprint({key: previous[key] for key in value}) != store.fingerprint(value):
            raise ValueError('this wait already has a different recorded answer')
        return previous
    return _write(context, gate, 'answer', value)


def answer(context, gate, required=True, *, allow_saved=False):
    record = _read(context, gate, 'answer', required=required)
    if record is not None:
        record_operation(context, gate, 'answer', record, allow_saved=allow_saved)
    return record


def record_operation(context, gate, kind, stored_record, *, allow_saved=False):
    """Return the host operation that persisted exactly this raw result or answer.

    Readers after a gate report require a reported/finished operation. Only the host's
    saved-operation recovery guard permits saved, before it reports the dispatch. This
    also works for historical attempts without requiring their dispatch to remain live.
    """
    if (kind not in ('result', 'answer') or not isinstance(stored_record, dict)
            or not isinstance(stored_record.get('binding'), dict)):
        raise ValueError('only a submitted result or answer has a host operation')
    execution, attempt = _binding(context, stored_record['binding'].get('attempt'))
    _validate_record(context, gate, kind, execution, attempt, stored_record)
    entries = context.state().get('host_operations', {})
    if not isinstance(entries, dict):
        raise ValueError('invalid task gate host operations')
    operation_kind = 'submit' if kind == 'result' else 'respond'
    candidates = []
    for operation_id, entry in entries.items():
        if not isinstance(entry, dict):
            continue
        request, receipt = entry.get('request'), entry.get('dispatch')
        if (not isinstance(request, dict) or not isinstance(receipt, dict)
                or request.get('kind') != operation_kind
                or receipt.get('id') != stored_record['dispatch_id']):
            continue
        # A human hold uses the same wait but does not persist an answer.
        if kind == 'answer' and operation_id != stored_record['operation_id']:
            continue
        candidates.append((operation_id, entry, request, receipt))
    if len(candidates) != 1:
        raise ValueError('task gate record lacks a unique source host operation')
    operation_id, entry, request, receipt = candidates[0]
    payload = request.get('payload')
    statuses = ('saved', 'reported', 'finished') if allow_saved else ('reported', 'finished')
    identity = {'root': context.root, 'state': context.state_path,
                'event': context.action, 'item': context.item}
    if (not _text(operation_id) or entry.get('status') not in statuses
            or not location_identity.same_binding({key: request.get(key) for key in identity}, identity)
            or not isinstance(payload, dict) or payload.get('operation_id') != operation_id
            or receipt.get('event') != context.action or (receipt.get('item') or '') != context.item
            or not _text(receipt.get('call')) or not _text(receipt.get('unit'))):
        raise ValueError('task gate record differs from its source host operation')
    if kind == 'result':
        unit = entry.get('unit')
        valid = (receipt.get('status') == 'emit' and isinstance(unit, dict)
                 and unit.get('gate') == gate and unit.get('type') == 'skill'
                 and unit.get('event') == context.action and (unit.get('item') or '') == context.item
                 and store.fingerprint(payload.get('dispatch')) == store.fingerprint(receipt)
                 and store.fingerprint(payload.get('result')) == store.fingerprint(stored_record['result']))
    else:
        expected = stored_record['expected']
        valid = (receipt.get('status') == 'wait' and entry.get('gate') == gate
                 and entry.get('then') in ('report', 'report-then')
                 and request.get('actor') == stored_record['actor']
                 and all(store.fingerprint(payload.get(key)) == store.fingerprint(stored_record[key])
                         for key in ('action', 'data', 'expected'))
                 and expected.get('call') == receipt['call'] and expected.get('unit') == receipt['unit'])
    if not valid:
        raise ValueError('task gate record differs from its source host operation')
    return operation_id


def _rejection(context, gate, kind, record):
    if (kind not in ('result', 'answer') or not isinstance(record, dict)
            or not isinstance(record.get('binding'), dict)):
        raise ValueError('only a submitted result or answer may be rejected')
    execution, attempt = _binding(context, record['binding'].get('attempt'))
    _validate_record(context, gate, kind, execution, attempt, record)
    fingerprint = store.fingerprint(record)
    path = _path(execution, context.action, gate, attempt, kind)[:-5] + '-' + fingerprint + '-rejected.json'
    binding = _record_binding(context, gate, 'rejection', execution, attempt)
    return path, {'schema': 1, 'binding': binding,
                  'record_kind': kind, 'record_sha256': fingerprint}


def _read_rejection(context, path, binding):
    try:
        value = store.read(context.root, path)
    except FileNotFoundError:
        return None
    if (set(value) != set(binding) | {'reason'} or type(value.get('schema')) is not int
            or not isinstance(value.get('binding'), dict) or type(value['binding'].get('attempt')) is not int
            or any(value.get(key) != expected for key, expected in binding.items()) or not _text(value.get('reason'))):
        raise ValueError('invalid task gate rejection receipt')
    return value


def reject(context, gate, kind, stored_record, reason):
    """Persist the gate's rejection of exactly these raw bytes/content; never replace a prior receipt."""
    path, binding = _rejection(context, gate, kind, stored_record)
    if not _text(reason):
        raise ValueError('a rejected task gate record needs its reason')
    if _read(context, gate, kind, stored_record['binding']['attempt']) != stored_record:
        raise ValueError('task gate record changed before rejection')
    receipt = {**binding, 'reason': reason}
    previous = _read_rejection(context, path, binding)
    if previous is not None:
        if previous != receipt:
            raise ValueError('immutable task gate rejection differs')
        return previous
    # The host serializes gate execution and persistence. Retrying after a lost write reply
    # finds this same receipt; a corrected dispatch gets its own fingerprint and receipt.
    store.write(context.root, path, receipt)
    return receipt


def rejected(context, gate, kind, stored_record):
    """Only an intact receipt for this exact record permits a gate to omit rejected raw history."""
    path, binding = _rejection(context, gate, kind, stored_record)
    return _read_rejection(context, path, binding) is not None


def check_answer(spec, action, data):
    """Check the answer's shape against the answer fields the gate published (no meaning is read)."""
    if not isinstance(spec, dict) or action not in spec:
        raise ValueError('unsupported task confirmation action')
    fields = spec[action]
    if not isinstance(fields, dict) or set(fields) - {'required', 'optional'}:
        raise ValueError('invalid task confirmation field declaration')
    if not isinstance(data, dict):
        raise ValueError('task confirmation data must be an object')
    required, optional = fields.get('required', {}), fields.get('optional', {})
    if (not isinstance(required, dict) or not isinstance(optional, dict) or set(required) & set(optional)
            or any(not _text(key) or kind not in ('text', 'object')
                   for key, kind in list(required.items()) + list(optional.items()))):
        raise ValueError('invalid task confirmation field declaration')
    if set(data) - set(required) - set(optional) or set(required) - set(data):
        raise ValueError('task confirmation requires the actual human answer')
    for key, value in data.items():
        kind = required.get(key) or optional.get(key)
        if kind == 'text' and (not isinstance(value, str) or not value.strip()):
            raise ValueError('task confirmation requires the actual human answer')
        if kind == 'object' and not isinstance(value, dict):
            raise ValueError('task confirmation field `%s` must be an object' % key)
