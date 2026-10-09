"""L3 review permission, based on a live L0 wait and a checked inspection."""
import hashlib
import json
from pathlib import Path
import location_identity

import inspection_seal
import review_contract
import engine_client


class OperationRejected(ValueError):
    def __init__(self, reason, pending=None):
        self.pending = pending
        self.next_action = ('submit the emitted Skill result' if pending and pending.get('type') == 'skill'
                            else 'advance the same call/item until review waits')
        super().__init__(reason)


def current(context, call=None):
    """The live feature-level review wait (a task-level review wait is L4's: implementation_task_review.current)."""
    if context.is_implementation:
        import implementation_flows
        call = implementation_flows.require_call(context, call)
    call = call or context.action
    state = engine_client.invoke(context, 'status', call)
    pending, receipt = state.get('pending'), state.get('dispatch')
    if (not pending or pending.get('gate') != 'review' or pending.get('event') != context.action
            or (pending.get('item') or '') != context.item or not receipt or receipt.get('status') != 'wait'):
        raise OperationRejected('review action is not allowed before the actual matching review wait', pending)
    record = review_contract.read(context)
    seal = inspection_seal.verify(context, record)
    markers = [line[len('AIDD-REVIEW-CONTEXT: '):] for line in (receipt.get('detail') or '').splitlines()
               if line.startswith('AIDD-REVIEW-CONTEXT: ')]
    evidence = {'unit':receipt['unit'],'snapshot':seal['snapshot'],'run':seal['run'],
                'inspection_hash':seal['record_hash']}
    if len(markers) != 1 or json.loads(markers[0]) != evidence:
        raise OperationRejected('review wait belongs to a different inspection', pending)
    # Tasks final review includes every individual inspection as well as phase.
    for scope in review_contract.scopes(context):
        review_contract.inspection(context, record, scope)
    raw = Path(context.gate_record).read_bytes()
    return {'root':str(Path(context.root).resolve()),'state':str(Path(context.state_path).resolve()),
            'call':call,'event':context.action,'item':context.item,'dispatch_id':receipt['id'],
            'unit':receipt['unit'],'scope':context.scope,'run':seal['run'],'snapshot':seal['snapshot'],
            'record_hash':hashlib.sha256(raw).hexdigest()}


def require(context, expected, call=None, resuming=False):
    if not isinstance(expected, dict):
        raise OperationRejected('a current review context is required; obtain review-context first')
    now = current(context, call or expected.get('call'))
    names = set(now) - ({'record_hash'} if resuming else set())
    if not location_identity.same_binding({k: now[k] for k in names}, {k: expected.get(k) for k in names}):
        raise OperationRejected('stale review context; obtain the current review before writing')
    return now
