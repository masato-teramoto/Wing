"""L3 completion certificates; repair completion can satisfy the original work.

No runner state is fabricated. A certificate is issued only after the public L0
status reports no pending units and current review evidence matches the files.
"""
import l0  # noqa: F401  L0 の枠組みを import できるようにする
import json
from pathlib import Path
import subprocess
import sys

import phase_rules
import artifacts
import project_state
import review_contract
import project_progress


def canonical(context):
    rule = phase_rules.RULES[context.process]
    action = rule["generate"] if context.action == rule["repair"] else context.action
    return action + '[' + context.item + ']'


def proof(context):
    rule = phase_rules.RULES[context.process]
    if context.kind == "integration":
        import implementation_project
        implementation_project.run_proof(context)  # 記録を書かない action は受領証で確かめる（§6.11）
    elif context.process == "tasks" and context.action in (rule["generate"], rule["repair"]):
        record = review_contract.read(context)
        review_contract.complete_inspection(context, record, context.scope)
        for target in context.artifacts():
            if (artifacts.fields(context.path(target)) or {}).get("status") not in ("review", "approved"):
                raise ValueError("feature tasks have not been inspected")
    else:
        review_contract.check_approved(context)


def record(context, call=None, flow_done=False):
    """flow_done: the host saw this process finish inside its flow (status of later units pending)."""
    if context.is_implementation:
        import implementation_flows
        call = implementation_flows.require_call(context, call)
        if context.kind == 'task':
            import implementation_requests
            return implementation_requests.record_completion(context)
    if context.action.endswith('-plan'):
        raise ValueError("plans are recorded by accept-plan")
    rule = phase_rules.RULES[context.process]
    allowed = {context.action}
    if context.is_implementation:
        allowed.add(call)
    if context.action in (rule['generate'], rule['repair']):
        allowed.add(rule['call'])
    if call and call not in allowed:
        raise ValueError('call does not belong to this workflow action')
    common = Path(__file__).resolve().parents[1]
    command = [sys.executable, '-B', str(common / 'bin/aidd.py'), '--config', str(common),
               '--root', context.root, '--state', context.state_path, 'status',
               '--call', call or context.action, '--json']
    if context.item:
        command += ['--item', context.item]
    result = subprocess.run(command, capture_output=True, encoding='utf-8', check=False)
    if result.returncode:
        raise ValueError('L0 status failed: ' + (result.stderr or result.stdout))
    status = json.loads(result.stdout)
    pending = status.get('pending')
    if pending is not None and not (flow_done and pending.get('event') not in (rule['generate'], rule['repair'])):
        raise ValueError('finish all L0 units before recording workflow completion')
    proof(context)
    values = dict(project_progress.workflow(context).get('completions', {}))
    values[canonical(context)] = {'source_event': context.action, 'call': call or context.action,
        'at': project_state.now(), 'inputs': project_progress.signature(context),
        'hashes': {p: phase_rules.inspection_digest(context, p) for p in context.artifacts()}}
    project_progress.save(context, {'completions': values})
    return values[canonical(context)]


def check(context):
    if context.kind == 'task':
        import implementation_store
        import implementation_requests
        import implementation_evidence
        import implementation_flows
        value = implementation_store.read_execution(context)
        state = implementation_requests.feature_state(context, value['feature'])
        certificate = state['completed'].get(value['task_id'], {})
        valid = (value.get('event_complete') and not state.get('invalidated')
                 and implementation_flows.same_contract(context, value.get('flow_contract'))
                 and state.get('flow_contract') == value.get('flow_contract')
                 and certificate.get('execution_id') == value['execution_id']
                 and implementation_requests.same_inputs(context, value['feature'], state['inputs'],
                                                         implementation_requests.input_signature(context, value['feature']))
                 and state['live_code'] == implementation_evidence.feature_inventory(context, state['policy']))
        return {'complete': bool(valid), 'source_event': context.action}
    value = project_progress.workflow(context).get('completions', {}).get(canonical(context))
    if not value:
        return {'complete': False}
    try:
        proof(context)
        valid = value['inputs'] == project_progress.signature(context) and value['hashes'] == {
            p: phase_rules.inspection_digest(context, p) for p in context.artifacts()}
    except (ValueError, OSError):
        valid = False
    return {'complete': valid, 'source_event': value['source_event']}
