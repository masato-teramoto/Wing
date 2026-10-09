"""Prepared, replayable review writes. All validation precedes the journal.

The journal and record replacements are atomic individual writes. A retry applies
only missing effects, including an interrupted multi-artifact approval.
"""
import l0  # noqa: F401  L0 の枠組みを import できるようにする
import hashlib
from pathlib import Path
import re

import artifacts
import project_state
import location_identity
import record_format
import review_gate
import project_progress


def digest(data):
    return hashlib.sha256(data).hexdigest()


def record_effect(context, section, rows):
    before = Path(context.gate_record).read_bytes()
    suffix = ('\n'+record_format.render_table(section, rows)).encode('utf-8')
    record_format.parse((before+suffix).decode('utf-8'))
    return {'kind':'record','path':Path(context.gate_record).relative_to(context.root).as_posix(),
            'before':digest(before),'after':digest(before+suffix),'suffix':suffix.decode('utf-8')}


def record_effect_after(context, previous, section, rows):
    """A second append to the same record, chained after the previous record effects."""
    before = Path(context.gate_record).read_bytes()
    for effect in previous:
        if effect['kind'] == 'record':
            before += effect['suffix'].encode('utf-8')
    suffix = ('\n'+record_format.render_table(section, rows)).encode('utf-8')
    record_format.parse((before+suffix).decode('utf-8'))
    return {'kind':'record','path':Path(context.gate_record).relative_to(context.root).as_posix(),
            'before':digest(before),'after':digest(before+suffix),'suffix':suffix.decode('utf-8')}


def status_effect(context, target, status, at):
    path = Path(context.path(target))
    return {'kind':'status','path':target,'before':digest(path.read_bytes()),
            'after':digest(artifacts.status_bytes(path,status,at)),'status':status,'at':at}


def apply_effect(context, effect):
    if effect['kind'] == 'cross':
        value = project_progress.workflow(context)
        key = project_progress.cross_key(context.process, context.selection)
        update = {'invalidated_cross': [p for p in value.get('invalidated_cross', []) if p != key]}
        if effect.get('scope') and context.selection:
            import feature_scope
            core = [context.selection, *feature_scope.closure(context, context.selection)]
            features = []
            for target in effect.get('targets', []):
                parts = target.split('/')
                if len(parts) > 2 and parts[0] == 'specs' and parts[1] not in features:
                    features.append(parts[1])
            scopes = dict(value.get('scopes', {}))
            scopes['%s#%d' % (effect['scope'], effect['run'])] = {
                'selection': context.selection, 'closure': [n for n in core[1:]],
                'consumers': [n for n in features if n not in core]}
            update['scopes'] = scopes
        project_progress.save(context, update)
        return
    path = Path(context.path(effect['path']))
    before = path.read_bytes()
    actual = digest(before)
    if actual == effect['after']:
        return
    if actual != effect['before']:
        raise ValueError('operation evidence changed; diagnose instead of replaying: '+effect['path'])
    after = before+effect['suffix'].encode('utf-8') if effect['kind']=='record' else artifacts.status_bytes(path,effect['status'],effect['at'])
    if digest(after) != effect['after']:
        raise ValueError('prepared operation hash differs')
    temporary = path.with_name(path.name+'.operation.tmp')
    temporary.write_bytes(after)
    temporary.replace(path)


def ensure_idle(context, operation_id=None):
    state = project_progress.workflow(context)
    operations = state.get('review_operations', {})
    parent = context.state().get('host_operations', {}).get(operation_id, {})  # L0 host の記録
    request = parent.get('request', {})
    batch = request.get('kind') == 'respond' and request.get('payload', {}).get('action') == 'decisions'
    def owned(key):
        return operation_id is not None and (key == operation_id or (batch and key.startswith(operation_id + '.')))
    if any(not owned(key) and op['status'] != 'applied' for key,op in operations.items()):
        raise ValueError('a review write is incomplete; retry its original operation ID and payload first')


def execute(context, operation, data, actor, expected, operation_id, prepare):
    with context.locked():
        if not isinstance(operation_id,str) or not re.fullmatch(r'[A-Za-z0-9][A-Za-z0-9_.:-]{0,127}',operation_id):
            raise review_gate.OperationRejected('a stable operation_id is required for review writes')
        request = {'action':operation,'data':data,'actor':actor,'expected':expected,
                   'root':str(Path(context.root).resolve()),'state':str(Path(context.state_path).resolve()),
                   'event':context.action,'item':context.item}
        operations = dict(project_progress.workflow(context).get('review_operations', {}))
        previous = operations.get(operation_id)
        if previous:
            if not location_identity.same_request(previous['request'], request):
                raise ValueError('operation ID already used with different content')
            if previous['status'] == 'applied':
                return {**previous['result'],'replayed':True}
        ensure_idle(context, operation_id)
        import host_session
        host_session.ensure_idle(context, operation_id)
        review_gate.require(context, expected, resuming=bool(previous))
        if previous and operation == 'approve':
            # A prepared operation may predate the current approval policy.
            # Revalidate without rebuilding effects already partially applied.
            import review_contract
            review_contract.ready(context)
        if not previous:
            effects = prepare()
            # Recheck after constructing and validating every effect, before writing.
            review_gate.require(context, expected)
            previous = {'status':'prepared','request':request,'effects':effects,
                        'result':{'event':context.action,'item':context.item,'operation_id':operation_id,'operation_applied':True}}
            operations[operation_id] = previous
            project_progress.save(context, {'review_operations':operations})
        # Inspect all files before applying any remaining effect.
        allowed = {}
        for effect in previous['effects']:
            if effect['kind'] != 'cross':
                allowed.setdefault(effect['path'], set()).update((effect['before'], effect['after']))
        for path, hashes in allowed.items():
            if digest(Path(context.path(path)).read_bytes()) not in hashes:
                raise ValueError('prepared operation has conflicting file changes: '+path)
        completed = set()
        for path in allowed:
            chain = [(i, e) for i, e in enumerate(previous['effects'])
                     if e.get('path') == path]
            for (_, earlier), (_, later) in zip(chain, chain[1:]):
                if earlier['after'] != later['before']:
                    raise ValueError('prepared operation has a broken effect chain: ' + path)
            actual = digest(Path(context.path(path)).read_bytes())
            reached = [i for i, e in chain if e['after'] == actual]
            if reached:
                completed.update(i for i, _ in chain if i <= max(reached))
        for index, effect in enumerate(previous['effects']):
            if index not in completed:
                apply_effect(context, effect)
        previous['status'] = 'applied'
        operations[operation_id] = previous
        project_progress.save(context, {'review_operations':operations})
        return previous['result']
