"""L3 Phase 8 routes. L0 alone expands flows and executes their units."""
from pathlib import Path

import phase_rules
import implementation_store as store
import engine_client

# 3: flows come from flow.yaml and the Skills' aidd-role (contracts/main_flow.json removed).
SCHEMA = 3


def configuration(context, validate=False):
    rule = phase_rules.RULES['implement']
    roles = {'generate': rule['generate'], 'repair': rule['repair'], 'review': phase_rules.IMPLEMENT_REVIEW}
    names = rule['flows']
    if names['generate'] != names['repair'] or names['generate'] == names['review']:
        raise ValueError('Phase 8 needs one task flow for generate/repair and a separate review flow')
    calls = {action: names[role] for role, action in roles.items()}
    # The configuration hash is L0's (validate --json `config_sha256`).
    value = {'schema': SCHEMA, 'calls': calls, 'config_sha256': engine_client.validate(context)['config_sha256']}
    if validate:
        data = engine_client.validate(context)
        flows = {row['name']: row for row in data['flows']}
        orders = {names['generate']: [roles['generate'], roles['repair']], names['review']: [roles['review']]}
        for call, order in orders.items():
            flow = flows.get(call)
            if not flow or flow['kind'] != 'flow' or flow['order'] != order:
                raise ValueError('Phase 8 flow is missing or has incompatible role/item scope: ' + call)
        # Multiple owning flows create different L0 histories for the same task.
        for row in flows.values():
            if row['kind'] == 'flow':
                for action in set(row['order']) & set(calls):
                    if row['name'] != calls[action]:
                        raise ValueError('Phase 8 action has multiple owning flows: ' + action)
    return value


def call(context):
    try:
        return configuration(context)['calls'][context.action]
    except KeyError as error:
        raise ValueError('unknown Phase 8 flow role') from error


def require_call(context, selected=None, validate=False):
    value = configuration(context, validate=validate)
    expected = value['calls'].get(context.action)
    if not expected or (selected is not None and selected != expected):
        raise ValueError('Phase 8 must use its declared flow call: ' + str(expected))
    return expected


def require_saved(context, value):
    saved = value.get('flow_contract')
    if saved is None:
        raise ValueError('legacy Phase 8 execution: finish the active request with its original distribution before switching flows')
    if not same_contract(context, saved):
        raise ValueError('Phase 8 flow configuration changed; restore the saved configuration or explicitly rebase at a quiescent boundary')
    return saved


def same_contract(context, saved):
    """保存した flow 契約が現在と同じか、再固定記録（implement-repin）の連鎖でつながるか（§6.5）。"""
    current = configuration(context)
    if saved == current:
        return True
    import implementation_reverify
    return implementation_reverify.repinned_contract(context, saved, current)


def require_current(context):
    import implementation_requests as requests
    feature = requests.feature_of(context)
    require_saved(context, requests.feature_state(context, feature))
    if requests.kind(context) == 'task':
        require_saved(context, store.current_execution(context))


def guard(context):
    """Called inside existing gates; no nested L0 invocation."""
    if context.flow != require_call(context):
        raise ValueError('Phase 8 gate requires the declared flow; direct action calls are not allowed')


def legacy_boundary(context, feature):
    """Do not move an in-flight dispatch or legacy task into a new history key."""
    pending = context.state().get('current', {}).get('pending') or {}
    if pending and pending.get('config_sha256') != configuration(context)['config_sha256']:
        raise ValueError('an old-configuration dispatch is pending; finish it with the original distribution before switching flows')
    for path in Path(context.path(store.BASE + '/runs')).glob('*/execution.json'):
        execution = store.read(context.root, path.relative_to(context.root).as_posix())
        if (execution.get('feature') == feature and (execution.get('flow_contract') or {}).get('schema') != SCHEMA
                and not execution.get('event_complete')):
            raise ValueError('legacy Phase 8 task is incomplete; finish it with the original distribution before switching flows')


def entry_action(context, selected):
    value = configuration(context, validate=True)
    matches = [action for action, name in value['calls'].items() if name == selected]
    if 'implement-authoring-generate' in matches:
        return store.current_execution(context)['event']
    return matches[0] if matches else None
