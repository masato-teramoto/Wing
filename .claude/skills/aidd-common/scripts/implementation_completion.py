"""L3-owned immutable completion evidence, issued by existing L4 gates.

The issuer decides acceptance and supplies its dependency closure. This module
checks identity and bytes, never review findings or upper-layer policy. Missing
proofs require explicit revalidation; completion cannot create its own approval.
"""
import copy
import json
import os
from pathlib import Path
import re
import uuid

import implementation_evidence as evidence
import implementation_reports as reports
import implementation_store as store

FIELDS = {'schema', 'identity', 'artifacts', 'current_artifacts', 'inventories',
          'current_optional_artifacts', 'environment_files', 'execution_bindings', 'operations'}
IDENTITY = ('execution_id', 'request_id', 'feature', 'task_id', 'task_item', 'event', 'plan_ref')


def identity(context, execution):
    return {'root': str(Path(context.root).resolve()),
            'state': str(Path(context.state_path).resolve()),
            **{key: execution[key] for key in IDENTITY},
            'attempt': len(execution.get('retries', [])),
            **{key + '_sha256': store.fingerprint(execution.get(key))
               for key in ('policy', 'inputs', 'flow_contract', 'retries')}}


def proof_path(execution):
    return (store.BASE + '/runs/' + store.identifier(execution['execution_id'])
            + '/completion-' + str(len(execution.get('retries', []))) + '.json')


def _file(context, name, external=False):
    if not isinstance(name, str) or not name:
        raise ValueError('completion evidence requires a file path')
    if external and Path(name).is_absolute():
        return Path(name)
    return reports.plain_file(context.root, name)


def _hashes(context, names, external=False):
    return {name: store.digest(_file(context, name, external).read_bytes()) for name in sorted(names)}


def _optional_hashes(context, names):
    values = {}
    for name in sorted(names):
        path = _file(context, name)
        values[name] = store.digest(path.read_bytes()) if path.exists() else None
    return values


def _environment(context, row):
    if (not isinstance(row, dict) or not isinstance(row.get('variable'), str)
            or not row['variable'].isidentifier() or not isinstance(row.get('default'), str)
            or not Path(row['default']).is_absolute()):
        raise ValueError('completion evidence requires an environment file selector')
    selected = Path(os.environ.get(row['variable']) or row['default'])
    # Gates run in the project root; direct completion calls may run elsewhere.
    # Preserve that same root-relative selector at both boundaries.
    if not selected.is_absolute():
        selected = Path(context.root) / selected
    selected = selected.absolute()
    return {'variable': row['variable'], 'default': row['default'],
            'selected': str(selected), 'sha256': store.digest(selected.read_bytes())}


def _operations(context, ids):
    journal = context.state().get('host_operations', {})
    result = {}
    for operation_id in ids:
        entry = journal.get(operation_id, {})
        if (entry.get('status') not in ('reported', 'finished')
                or not isinstance(entry.get('request'), dict) or not entry['request']):
            raise ValueError('completion evidence lacks its recorded operation')
        # Status can advance from reported to finished and other operations can
        # be appended. The actual request (actor/dispatch/answer) must not change.
        result[operation_id] = store.fingerprint(entry['request'])
    return result


def capture(context, execution, *, artifacts, current_artifacts=(), inventories=(),
            current_optional_artifacts=(), environment_files=(), execution_bindings=(), operations=()):
    """Freeze dependencies BEFORE the issuer's final semantic validation."""
    if any(type(protected) is not bool for protected in inventories):
        raise ValueError('completion inventory selectors must be boolean')
    return {'schema': 1, 'identity': identity(context, execution),
            'artifacts': _hashes(context, artifacts),
            'current_artifacts': _hashes(context, current_artifacts, external=True),
            'current_optional_artifacts': _optional_hashes(context, current_optional_artifacts),
            'inventories': [{'protected': protected,
                             'sha256': store.fingerprint(evidence.inventory(context, execution['policy'], protected))}
                            for protected in inventories],
            'environment_files': [_environment(context, row) for row in environment_files],
            'execution_bindings': {key: copy.deepcopy(execution.get(key)) for key in execution_bindings},
            'operations': _operations(context, operations)}


def _verify(context, execution, proof, current):
    if type(current) is not bool:
        raise ValueError('completion validation requires a boolean current flag')
    if (not isinstance(proof, dict) or set(proof) != FIELDS
            or type(proof.get('schema')) is not int or proof['schema'] != 1
            or proof.get('identity') != identity(context, execution)
            or any(not isinstance(proof.get(key), dict)
                   for key in ('artifacts', 'current_artifacts', 'current_optional_artifacts', 'execution_bindings', 'operations'))
            or any(not isinstance(proof.get(key), list) for key in ('inventories', 'environment_files'))):
        raise ValueError('completion evidence identity or schema differs; revalidation is required')
    if proof['execution_bindings'] != {key: execution.get(key) for key in proof['execution_bindings']}:
        raise ValueError('completion evidence execution references changed')
    if _hashes(context, proof['artifacts']) != proof['artifacts']:
        raise ValueError('completion evidence artifact changed')
    if _operations(context, proof['operations']) != proof['operations']:
        raise ValueError('completion evidence recorded operation changed')
    for row in proof['inventories']:
        if (not isinstance(row, dict) or set(row) != {'protected', 'sha256'}
                or type(row['protected']) is not bool):
            raise ValueError('invalid completion inventory')
    if current:
        if _hashes(context, proof['current_artifacts'], external=True) != proof['current_artifacts']:
            raise ValueError('completion evidence current inputs changed')
        if _optional_hashes(context, proof['current_optional_artifacts']) != proof['current_optional_artifacts']:
            raise ValueError('completion evidence current file presence or contents changed')
        if any(store.fingerprint(evidence.inventory(context, execution['policy'], row['protected'])) != row['sha256']
               for row in proof['inventories']):
            raise ValueError('completion evidence input inventory changed')
        if [_environment(context, row) for row in proof['environment_files']] != proof['environment_files']:
            raise ValueError('completion evidence environment selection changed')
    return proof


def validate_snapshot(context, execution, candidate, current=True):
    """Recheck a captured gate dependency snapshot without publishing approval."""
    return _verify(context, execution, candidate, current)


def _write_once(target, raw):
    target.parent.mkdir(parents=True, exist_ok=True)
    temporary = target.with_name('.completion-' + uuid.uuid4().hex + '.tmp')
    try:
        temporary.write_bytes(raw)
        try:
            os.link(temporary, target)
        except FileExistsError:
            if target.read_bytes() != raw:
                raise ValueError('immutable completion evidence differs; retry requires a new attempt')
    finally:
        temporary.unlink(missing_ok=True)


def publish(context, execution, proof):
    """Publish a gate-validated snapshot, rechecking it before either save.

An interrupted publication can repeat only the identical proof. A previous
attempt's pointer is replaced only after a new attempt obtains its own proof.
"""
    saved = store.read(context.root, store.execution_path(execution['execution_id']))
    _verify(context, saved, proof, current=True)
    _verify(context, execution, proof, current=True)
    raw = (json.dumps(proof, ensure_ascii=False, sort_keys=True, indent=2, allow_nan=False) + '\n').encode('utf-8')
    name = proof_path(execution)
    pointer = {'path': name, 'sha256': store.digest(raw)}
    previous = saved.get('completion_proof')
    if previous and previous.get('path') == name and previous != pointer:
        raise ValueError('completion evidence pointer differs within the same attempt')
    _write_once(_file(context, name), raw)
    # Verify once more after publication, before making this proof reachable.
    _verify(context, saved, proof, current=True)
    saved['completion_proof'] = pointer
    store.write(context.root, store.execution_path(saved['execution_id']), saved)
    execution['completion_proof'] = copy.deepcopy(pointer)
    return proof


def require(context, execution, current=True):
    pointer = execution.get('completion_proof')
    if (not isinstance(pointer, dict) or set(pointer) != {'path', 'sha256'}
            or pointer.get('path') != proof_path(execution)
            or not isinstance(pointer.get('sha256'), str)
            or not re.fullmatch(r'[0-9a-f]{64}', pointer['sha256'])):
        raise ValueError('completion evidence is missing or stale; revalidation by the acceptance gate is required')
    raw = _file(context, pointer['path']).read_bytes()
    if store.digest(raw) != pointer['sha256']:
        raise ValueError('completion evidence file changed')
    return _verify(context, execution, json.loads(raw), current)
