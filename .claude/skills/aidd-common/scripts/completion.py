"""L3 completion certificates; repair completion can satisfy the original work.

No runner state is fabricated. A certificate is issued only after the public L0
status reports no pending units and current review evidence matches the files.
"""
import json
from pathlib import Path
import subprocess
import sys

import aidd_paths
import artifacts
import project_state
import review_contract
import workflow_state


def canonical(context):
    rule = aidd_paths.RULES[context.process]
    event = rule["generate"] if context.event == rule["repair"] else context.event
    return event + '[' + context.item + ']'


def proof(context):
    if context.process == "tasks" and context.item:
        record = review_contract.read(context)
        review_contract.complete_inspection(context, record, context.scope)
        for target in context.artifacts():
            if (artifacts.fields(context.path(target)) or {}).get("status") not in ("review", "approved"):
                raise ValueError("feature tasks have not been inspected")
    else:
        review_contract.check_approved(context)


def record(context, call=None, flow_done=False):
    """flow_done: the host saw this process finish inside its flow (status of later units pending)."""
    if context.process == 'implement':
        import implementation_flows
        call = implementation_flows.require_call(context, call)
        if context.event != 'implement-gate-run':
            import implementation_requests
            return implementation_requests.record_completion(context)
    if context.event.endswith('-plan'):
        raise ValueError("plans are recorded by accept-plan")
    rule = aidd_paths.RULES[context.process]
    allowed = {context.event}
    if context.process == 'implement':
        allowed.add(call)
    if context.event in (rule['generate'], rule['repair']):
        allowed.add(rule['call'])
    if call and call not in allowed:
        raise ValueError('call does not belong to this workflow event')
    common = Path(__file__).resolve().parents[1]
    command = [sys.executable, '-B', str(common / 'bin/aidd.py'), '--config', str(common),
               '--root', context.root, '--state', context.state_path, 'status',
               '--call', call or context.event, '--json']
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
    values = dict(workflow_state.workflow(context).get('completions', {}))
    values[canonical(context)] = {'source_event': context.event, 'call': call or context.event,
        'at': project_state.now(), 'inputs': workflow_state.signature(context),
        'hashes': {p: aidd_paths.inspection_digest(context, p) for p in context.artifacts()}}
    workflow_state.save(context, {'completions': values})
    return values[canonical(context)]


def check(context):
    if context.process == 'implement' and context.event != 'implement-gate-run':
        import implementation_store
        import implementation_requests
        import implementation_evidence
        import implementation_flows
        value = implementation_store.read_execution(context)
        state = implementation_requests.feature_state(context, value['feature'])
        certificate = state['completed'].get(value['task_id'], {})
        valid = (value.get('event_complete') and not state.get('invalidated')
                 and value.get('flow_contract') == implementation_flows.configuration(context)
                 and state.get('flow_contract') == value.get('flow_contract')
                 and certificate.get('execution_id') == value['execution_id']
                 and state['inputs'] == implementation_requests.input_signature(context, value['feature'])
                 and state['live_code'] == implementation_evidence.feature_inventory(context, state['policy']))
        return {'complete': bool(valid), 'source_event': context.event}
    value = workflow_state.workflow(context).get('completions', {}).get(canonical(context))
    if not value:
        return {'complete': False}
    try:
        proof(context)
        valid = value['inputs'] == workflow_state.signature(context) and value['hashes'] == {
            p: aidd_paths.inspection_digest(context, p) for p in context.artifacts()}
    except (ValueError, OSError):
        valid = False
    return {'complete': valid, 'source_event': value['source_event']}
