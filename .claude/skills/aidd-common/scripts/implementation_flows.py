"""L3 Phase 8 routes. L0 alone expands flows and executes their units."""
import json
from pathlib import Path

import aidd_paths
import implementation_store as store
import runtime_client


def configuration(context, validate=False):
    common = Path(runtime_client.__file__).resolve().parents[1]
    contract_raw = (common / 'contracts/main_flow.json').read_bytes()
    contract = json.loads(contract_raw)
    rule = contract['phases']['implement']
    roles = {'generate': rule['generate'], 'repair': rule['repair'], 'review': 'implement-gate-run'}
    names = rule.get('flows')
    if (not isinstance(names, dict) or set(names) != set(roles)
            or any(not isinstance(name, str) or not name.strip() for name in names.values())
            or names['generate'] != names['repair'] or names['generate'] == names['review']):
        raise ValueError('Phase 8 needs one task flow for generate/repair and a separate review flow')
    if rule.get('call') != names['generate']:
        raise ValueError('Phase 8 entry call differs from its generate flow')
    calls = {event: names[role] for role, event in roles.items()}
    raw = b''.join((common / name).read_bytes() for name in ('events.yaml', 'flows.yaml', 'gates.yaml'))
    value = {'schema': 2, 'calls': calls, 'config_sha256': store.digest(raw),
             'contract_sha256': store.digest(contract_raw)}
    if validate:
        data = runtime_client.validate(context)
        flows = {row['name']: row for row in data['flows']}
        orders = {names['generate']: [roles['generate'], roles['repair']], names['review']: [roles['review']]}
        for call, order in orders.items():
            flow = flows.get(call)
            if not flow or flow['kind'] != 'flow' or flow['order'] != order:
                raise ValueError('Phase 8 flow is missing or has incompatible role/item scope: ' + call)
        # Multiple owning flows create different L0 histories for the same task.
        for row in flows.values():
            if row['kind'] == 'flow':
                for event in set(row['order']) & set(calls):
                    if row['name'] != calls[event]:
                        raise ValueError('Phase 8 event has multiple owning flows: ' + event)
    return value


def call(context):
    try:
        return configuration(context)['calls'][context.event]
    except KeyError as error:
        raise ValueError('unknown Phase 8 flow role') from error


def require_call(context, selected=None, validate=False):
    value = configuration(context, validate=validate)
    expected = value['calls'].get(context.event)
    if not expected or (selected is not None and selected != expected):
        raise ValueError('Phase 8 must use its declared flow call: ' + str(expected))
    return expected


def require_saved(context, value):
    saved = value.get('flow_contract')
    if saved is None:
        raise ValueError('legacy Phase 8 execution: finish the active request with its original distribution before switching flows')
    if saved != configuration(context):
        raise ValueError('Phase 8 flow configuration changed; restore the saved configuration or explicitly rebase at a quiescent boundary')
    return saved


def require_current(context):
    import implementation_requests as requests
    feature = requests.feature_of(context)
    require_saved(context, requests.feature_state(context, feature))
    if context.event in requests.TASK_EVENTS:
        require_saved(context, store.current_execution(context))


def guard(context):
    """Called inside existing gates; no nested L0 invocation."""
    if context.flow != require_call(context):
        raise ValueError('Phase 8 gate requires the declared flow; direct event calls are not allowed')


def legacy_boundary(context, feature):
    """Do not move an in-flight dispatch or legacy task into a new history key."""
    pending = context.state().get('current', {}).get('pending') or {}
    if pending and pending.get('config_sha256') != configuration(context)['config_sha256']:
        raise ValueError('an old-configuration dispatch is pending; finish it with the original distribution before switching flows')
    for path in Path(context.path(store.BASE + '/runs')).glob('*/execution.json'):
        execution = store.read(context.root, path.relative_to(context.root).as_posix())
        if (execution.get('feature') == feature and (execution.get('flow_contract') or {}).get('schema') != 2
                and not execution.get('event_complete')):
            raise ValueError('legacy Phase 8 task is incomplete; finish it with the original distribution before switching flows')


def entry_event(context, selected):
    value = configuration(context, validate=True)
    matches = [event for event, name in value['calls'].items() if name == selected]
    if 'implement-authoring-generate' in matches:
        return store.current_execution(context)['event']
    return matches[0] if matches else None
