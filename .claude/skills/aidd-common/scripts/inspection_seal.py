"""Record the successful machine check's immutable inspection boundary."""
import hashlib
import json
from pathlib import Path

import artifacts
import phase_rules
import snapshot_artifacts
import project_progress


def digest(data):
    return hashlib.sha256(data).hexdigest()


def path(context):
    return Path(snapshot_artifacts.snapshot_path(context)).with_suffix('.checked.json')


def save(context, run):
    record = Path(context.gate_record).read_bytes()
    snapshot = Path(snapshot_artifacts.snapshot_path(context)).read_bytes()
    data = {'event':context.action,'scope':context.scope,'run':run.number,
            'snapshot':digest(snapshot),'record_bytes':len(record),'record_hash':digest(record),
            'targets':run.targets,'hashes':run.hashes,'inputs':project_progress.signature(context)}
    if context.process == 'implement':
        import implementation_checks
        data['implementation_tools'] = implementation_checks.tools_digest(context)
    target = path(context)
    temporary = target.with_suffix('.tmp')
    temporary.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    temporary.replace(target)
    return data


def verify(context, record):
    value = json.loads(path(context).read_text(encoding='utf-8'))
    snapshot = Path(snapshot_artifacts.snapshot_path(context)).read_bytes()
    raw = Path(context.gate_record).read_bytes()
    run = record.latest(context.scope)
    if (not run or value['event'] != context.action or value['scope'] != context.scope
            or value['run'] != run.number or value['snapshot'] != digest(snapshot)
            or value['record_hash'] != digest(raw[:value['record_bytes']])):
        raise ValueError('inspection changed after scope-check; obtain a new checked review')
    if value['inputs'] != project_progress.signature(context):
        raise ValueError('inputs changed since inspection; run audit before resuming')
    if context.process == 'implement':
        import implementation_checks
        if value.get('implementation_tools') != implementation_checks.tools_digest(context):
            raise ValueError('tool reports changed since scope-check; obtain a new inspection')
        import implementation_evidence
        import implementation_requests
        state = implementation_requests.feature_state(context, context.item)
        before = snapshot_artifacts.load(context)
        if before['workspace_code'] != implementation_evidence.inventory(context, state['policy']):
            raise ValueError('implementation workspace changed since scope-check')
    if value['targets'] != context.review_targets() or value['hashes'] != run.hashes:
        raise ValueError('checked inspection targets differ')
    if any(phase_rules.inspection_digest(context, p) != v for p,v in value['hashes'].items()):
        raise ValueError('artifact changed since scope-check')
    import record_format
    prefix = record_format.parse(raw[:value['record_bytes']].decode('utf-8'))
    if any(name not in ('判断','解消','承認','確認','残件') for name,_ in record.blocks[len(prefix.blocks):]):
        raise ValueError('inspection boundary changed after scope-check')
    return value
