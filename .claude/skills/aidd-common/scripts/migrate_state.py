"""Offline migration to a NEW state file. The source is never modified.

Retain legacy evidence, invalidate active success marks, and require explicit
record reconciliation before approval. Run only while the host is stopped.
"""
import argparse
import copy
import hashlib
import json
from pathlib import Path

import project_state


def reconcile(context, data, actor):
    import aidd_paths
    import review_actions
    import review_contract
    import workflow_state
    review_actions.person(actor)
    migration = workflow_state.workflow(context).get('migration', {})
    if migration.get('status') != 'review-required':
        raise ValueError('no pending migration review')
    archives = {p.name: p for p in Path(context.path('.aidd/legacy-gates')).glob('*.md')}
    expected = migration.get('records', {})
    if set(archives) != set(expected) or any(hashlib.sha256(p.read_bytes()).hexdigest() != expected[name] for name,p in archives.items()):
        raise ValueError('all original gate records must be archived with their original hashes')
    receipts = data.get('records', [])
    if not isinstance(receipts, list) or not {row.get('file') for row in receipts}.issubset(archives) or len({row.get('file') for row in receipts}) != len(receipts):
        raise ValueError('review must identify archived gate records without duplicates')
    if not data.get('state_review'):
        raise ValueError('human review of legacy questions, blockers and state is required')
    phases = {Path(path).name: name for name, (_, path) in aidd_paths.PHASES.items()}
    for row in receipts:
        path = archives[row['file']]
        if row['file'] not in phases or row.get('sha256') != hashlib.sha256(path.read_bytes()).hexdigest():
            raise ValueError('archive identity/hash differs')
        origin = aidd_paths.Context(context.root, context.state_path, aidd_paths.RULES[phases[row['file']]]['generate'])
        record = review_contract.read(origin)
        if not record.runs or not row.get('review_summary'):
            raise ValueError('reinspection and actual human reconciliation are required')
        mappings = row.get('carried_findings')
        if not isinstance(mappings, list):
            raise ValueError('carried_findings must list remaining legacy findings, or be explicitly empty')
        for finding in mappings:
            if not finding.get('legacy_location') or review_actions.finding(record, finding['scope'], finding['run'], finding['number']) is None:
                raise ValueError('carried legacy finding must reference a current finding')
    history = list(migration.get('reconciliations', []))
    history.append({'actor': actor, 'at': project_state.now(), 'data': data})
    reviewed = set(migration.get('reviewed_phases', []))
    reviewed.update(phases[row['file']] for row in receipts)
    reviewed.update(name for file, name in phases.items() if file not in archives)
    migration.update(status='reviewed' if reviewed == set(aidd_paths.RULES) else 'review-required',
                     reconciliations=history, reviewed_phases=sorted(reviewed))
    workflow_state.save(context, {'migration': migration})
    return migration


def migrate(source, output):
    source, output = Path(source), Path(output)
    if output.exists():
        raise ValueError('migration output must not exist')
    raw = source.read_bytes()
    old = json.loads(raw.decode('utf-8'))
    if not isinstance(old, dict) or not isinstance(old.get('events', []), list):
        raise ValueError('legacy state must be an object with an events array')
    new = copy.deepcopy(old)
    new['legacy_state'] = {'sha256': hashlib.sha256(raw).hexdigest(), 'data': old}
    events = new.setdefault('events', [])
    latest = {e['unit']: e for e in events if isinstance(e, dict) and isinstance(e.get('unit'), str)}
    for entry in latest.values():
        events.append({**entry, 'result': 'invalidated', 'at': project_state.now(), 'note': 'explicit schema migration'})
    records = {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in (source.parent / 'gates').glob('*.md')}
    new.update(engine_schema=2, current={}, workflow={'migration': {'status': 'review-required', 'records':records}}, blockers=[])
    new.pop('trace', None)
    new.pop('feature_manifest', None)
    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open('x', encoding='utf-8') as handle:
        json.dump(new, handle, ensure_ascii=False, indent=2)
        handle.write('\n')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source', required=True)
    parser.add_argument('--output', required=True)
    args = parser.parse_args()
    try:
        migrate(args.source, args.output)
    except (ValueError, OSError) as error:
        parser.exit(1, str(error) + '\n')
