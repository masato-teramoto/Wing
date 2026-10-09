"""Archive stale verification markers only after the operator confirms process stop."""
import argparse
import json
from pathlib import Path
import uuid

import l0  # noqa: F401
import aidd_lock
import implementation_reports as reports
import implementation_store as store


def recover(root, state, processes_stopped=False):
    root = Path(root).resolve()
    with aidd_lock.hold(state):
        pending = []
        patterns = ['runs/*/' + stage + '/running.json' for stage in ('red', 'green', 'verify')]
        patterns += ['features/*/inspections/*/running.json', 'features/*/inspections/*/reporting/running.json']
        paths = {path for pattern in patterns for path in root.glob(store.BASE + '/' + pattern)}
        for path in sorted(paths):
            relative = path.relative_to(root).as_posix()
            path = reports.plain_file(str(root), relative)
            value = store.read(str(root), relative)
            if value.get('status') == 'running':
                if not isinstance(value.get('operation_id'), str) or not value['operation_id']:
                    raise ValueError('invalid verification marker: ' + relative)
                pending.append((path, relative, value))
        archived = []
        if processes_stopped and pending:
            directory = '.aidd/recovery/checks-' + uuid.uuid4().hex
            for index, (path, relative, value) in enumerate(pending):
                target = directory + '/' + str(index) + '.json'
                # Archive first. A crash before unlink leaves a safely blocked marker.
                store.write(str(root), target, {'schema': 1, 'source': relative,
                                              'processes_stopped': True, 'marker': value})
                path.unlink()
                archived.append(target)
        return {'status': 'recovered' if processes_stopped else 'inspection',
                'pending': [{'path': relative, 'pid': value.get('pid'), 'check_id': value.get('check_id')}
                            for _, relative, value in pending], 'archives': archived}


def main(root, state, argv):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--processes-stopped', action='store_true',
                        help='Confirm that all listed verification commands and their children have stopped.')
    args = parser.parse_args(argv)
    try:
        print(json.dumps(recover(root, state, args.processes_stopped), ensure_ascii=False))
        return 0
    except (ValueError, OSError) as error:
        print(json.dumps({'status': 'fail', 'error': str(error)}, ensure_ascii=False))
        return 1
