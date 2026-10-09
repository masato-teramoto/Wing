"""L4 task verification criteria, shared by submission and completion gates."""
from pathlib import Path

import implementation_store as store
import implementation_evidence as evidence


def receipts(context, execution, stage='verify', current=True):
    path = store.BASE + '/runs/' + execution['execution_id'] + '/' + stage + '.json'
    result = store.read(context.root, path)
    expected = execution['policy']['tasks'][execution['task_id']]['check_ids']
    if (result.get('source_changed') or result.get('stage') != stage
            or result.get('execution_id') != execution['execution_id'] or result.get('task_id') != execution['task_id']
            or result.get('policy_hash') != store.fingerprint(execution['policy'])
            or (current and result.get('code') != evidence.inventory(context, execution['policy']))
            or [r['check_id'] for r in result.get('receipts', [])] != expected):
        raise ValueError('verification receipt identity, coverage or version mismatch')
    if any(r['status'] != 'passed' for r in result['receipts']):
        raise ValueError('required verification did not pass')
    for receipt in result['receipts']:
        for key in ('stdout', 'stderr'):
            log = receipt[key]
            if store.digest(Path(context.path(log['path'])).read_bytes()) != log['sha256']:
                raise ValueError('verification log changed or missing')
    return result



def validate_task(context, execution):
    verified = receipts(context, execution)
    if execution['policy']['tasks'][execution['task_id']]['tdd'] and not execution.get('reverify'):
        # reverify（コード編集 0 件）は RED を観測できないので、GREEN・VERIFY 相当の checks だけを取り直す（§6.5）。
        red = store.read(context.root, store.BASE + '/runs/' + execution['execution_id'] + '/red.json')
        green = receipts(context, execution, stage='green', current=False)
        if (red.get('task_id') != execution['task_id'] or red.get('execution_id') != execution['execution_id']
                or red.get('policy_hash') != store.fingerprint(execution['policy'])
                or red.get('source_changed') or red.get('stage') != 'red'
                or not red.get('completed_at') or not green.get('completed_at') or not verified.get('completed_at')
                or not (red['completed_at'] <= green['completed_at'] <= verified['completed_at'])
                or not red.get('expected_failure') or not any(r['status'] == 'test_failed' for r in red['receipts'])
                or any(r['status'] not in ('passed', 'test_failed') for r in red['receipts'])):
            raise ValueError('TDD requires an observed expected test failure, not an environment failure')
        for row in red['receipts']:
            for channel in ('stdout', 'stderr'):
                if store.digest(Path(context.path(row[channel]['path'])).read_bytes()) != row[channel]['sha256']:
                    raise ValueError('RED verification log changed or missing')
    return verified
