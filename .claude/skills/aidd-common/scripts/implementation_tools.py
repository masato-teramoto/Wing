"""L4 technical command execution. No workflow completion or human decisions."""
import json
import math
import os
import re
from pathlib import Path
import subprocess
import sys
import time
import uuid

import artifacts
import implementation_store as store
import implementation_reports as reports
from implementation_process import ProcessTree


def _run_commands(root, checks, directory, report_directory=None, final=False):
    """Save full logs and one receipt per declared check, including failures.

    A running marker deliberately blocks replay after an unobserved crash. The
    host must diagnose/terminate that process before archiving the marker.
    """
    marker = directory + '/running.json'
    marker_path = artifacts.resolve(root, marker)
    if marker_path.exists():
        previous = store.read(root, marker)
        if previous.get('status') == 'running':
            raise ValueError('verification may still be running; inspect its saved PID before retrying')
    receipts = []
    for check in checks:
        operation = uuid.uuid4().hex
        prefix = directory + '/logs/' + check['id'] + '-' + operation
        out_path = artifacts.resolve(root, prefix + '.stdout.txt')
        err_path = artifacts.resolve(root, prefix + '.stderr.txt')
        out_path.parent.mkdir(parents=True, exist_ok=True)
        argv = [sys.executable if arg == '{python}' else arg.replace('{report_dir}', report_directory or '') for arg in check['argv']]
        cwd = root if check.get('cwd', '.') == '.' else str(artifacts.resolve(root, check['cwd']))
        receipt = {'check_id': check['id'], 'argv': argv, 'cwd': check.get('cwd', '.'),
                   'timeout_seconds': check['timeout_seconds'], 'status': 'launch_failed', 'exit_code': None}
        start = time.monotonic()
        metric = check.get('metric')
        metric_before = None
        if metric:
            metric_path = artifacts.resolve(root, metric['path'])
            if metric_path.exists():
                metric_before = (metric_path.stat().st_mtime_ns, store.digest(metric_path.read_bytes()))
        running = {'schema': 1, 'status': 'running', 'operation_id': operation, 'check_id': check['id'], 'pid': None}
        store.write(root, marker, running)
        command_stopped = True  # No command exists until Popen succeeds.
        process = None
        try:
            with out_path.open('wb') as stdout, err_path.open('wb') as stderr:
                options = {'creationflags': subprocess.CREATE_NEW_PROCESS_GROUP} if os.name == 'nt' else {'start_new_session': True}
                tree = None
                try:
                    tree = ProcessTree()
                    # The Windows wrapper waits for one byte before spawning any
                    # command children, removing the job-assignment race.
                    launched = [sys.executable, '-B', str(Path(__file__).with_name('implementation_child.py')), *argv] if os.name == 'nt' else argv
                    environment = dict(os.environ)
                    if report_directory:
                        environment.update(AIDD_REPORT_DIR=report_directory, AIDD_REPORTING='1' if final else '0')
                    command_stopped = False
                    process = subprocess.Popen(launched, cwd=cwd, stdout=stdout, stderr=stderr, env=environment,
                                               stdin=subprocess.PIPE if os.name == 'nt' else subprocess.DEVNULL,
                                               shell=False, **options)
                    tree.attach(process)
                    if os.name == 'nt':
                        process.stdin.write(b'G')
                        process.stdin.close()
                    running['pid'] = process.pid
                    store.write(root, marker, running)
                    try:
                        receipt['exit_code'] = process.wait(timeout=check['timeout_seconds'])
                        receipt['status'] = 'passed' if receipt['exit_code'] == 0 else 'test_failed'
                    except subprocess.TimeoutExpired:
                        tree.stop()
                        receipt['status'] = 'timeout'
                except OSError as error:
                    stderr.write(str(error).encode('utf-8'))
                    receipt['error'] = str(error)
                finally:
                    if tree is not None:
                        tree.close()
                    command_stopped = process is None or process.poll() is not None
            if receipt['status'] == 'passed' and metric:
                try:
                    raw = metric_path.read_bytes()
                    if metric_before == (metric_path.stat().st_mtime_ns, store.digest(raw)):
                        raise ValueError('metric was not refreshed by this check')
                    value = json.loads(raw)
                    for key in metric['keys']:
                        value = value[key]
                    if type(value) not in (int, float) or not math.isfinite(value):
                        raise ValueError('metric is not numeric')
                    receipt['metric'] = {'value': value, 'minimum': metric['minimum'], 'sha256': store.digest(raw)}
                    if value < metric['minimum']:
                        receipt['status'] = 'threshold_failed'
                except (ValueError, KeyError, TypeError, OSError) as error:
                    receipt.update(status='metric_failed', error=str(error))
            receipt['elapsed_seconds'] = round(time.monotonic() - start, 3)
            if receipt['status'] == 'test_failed':
                diagnostics = out_path.read_text(encoding='utf-8', errors='replace') + '\n' + err_path.read_text(encoding='utf-8', errors='replace')
                if receipt['exit_code'] in (126, 127, 9009):
                    receipt['status'] = 'launch_failed'
                elif (re.search(r'(?m)^(?:ModuleNotFoundError|ImportError|SyntaxError|IndentationError|FileNotFoundError|PermissionError):', diagnostics)
                        or re.search(r'no tests ran|collected 0 items', diagnostics)):
                    receipt['status'] = 'environment_failed'
            for key, path in (('stdout', out_path), ('stderr', err_path)):
                receipt[key] = {'path': path.relative_to(root).as_posix(), 'sha256': store.digest(path.read_bytes())}
            receipts.append(receipt)
            store.write(root, prefix + '.receipt.json', {'schema': 1, **receipt})
            store.write(root, marker, {**running, 'status': 'finished'})
        except OSError as error:
            # A log/receipt write failure after a confirmed stop is retryable.
            # Unknown crashes and processes still alive retain the running marker.
            if command_stopped:
                try:
                    store.write(root, marker, {**running, 'status': 'interrupted', 'error': str(error)})
                except OSError:
                    pass  # Preserve the original failure if even the marker cannot be saved.
            raise
    return receipts


def run_checks(root, checks, directory, final=False):
    """Run native exporters before returning failure to the L0 gate.

    Postprocessing and mandatory report validation apply only to feature final
    checks. Each attempt starts empty; task receipts keep their existing rules.
    """
    if not final:
        return _run_commands(root, checks, directory)
    receipts = []
    for check in checks:
        attempt = directory + '/reports/' + check['id'] + '-' + uuid.uuid4().hex
        output = reports.plain_file(root, attempt)
        output.mkdir(parents=True, exist_ok=False)
        receipt = _run_commands(root, [check], directory, str(output), final)[0]
        receipt['command_status'] = receipt['status']
        receipt['postprocess'] = []
        if final:
            for index, command in enumerate(check.get('postprocess', []), 1):
                command = {'cwd': check.get('cwd', '.'), **command, 'id': check['id'] + '-post-' + str(index)}
                result = _run_commands(root, [command], directory, str(output), final)[0]
                receipt['postprocess'].append(result)
            if receipt['status'] == 'passed' and any(r['status'] != 'passed' for r in receipt['postprocess']):
                receipt['status'] = 'postprocess_failed'
            try:
                receipt['report'] = reports.collect(root, check, attempt)
            except (ValueError, OSError, KeyError, TypeError) as error:
                receipt['report_error'] = str(error)
                receipt['report'] = {'directory': attempt, 'entries': check.get('reports', [])}
                # Retain partial native outputs even when tests fail. Unsafe
                # paths are never followed while collecting diagnostics.
                try:
                    receipt['report']['files'] = reports.files(root, attempt)
                except (ValueError, OSError):
                    pass
                if receipt['status'] == 'passed':
                    receipt['status'] = 'report_failed'
            if receipt['status'] != 'passed':
                diagnostic = receipt['stdout']['path'].replace('.stdout.txt', '.diagnostic.md')
                text = ('# 検証が完了しませんでした\n\n'
                        + 'これは診断記録であり、正常なテストレポートの代わりにはなりません。\n\n'
                        + '```json\n' + json.dumps(receipt, ensure_ascii=False, indent=2) + '\n```\n')
                reports.plain_file(root, diagnostic).write_text(text, encoding='utf-8')
                receipt['diagnostic'] = {'path': diagnostic, 'sha256': store.digest(text.encode('utf-8'))}
        # Replace the command-only receipt with its complete export outcome.
        target = receipt['stdout']['path'].replace('.stdout.txt', '.receipt.json')
        store.write(root, target, {'schema': 1, **receipt})
        receipts.append(receipt)
    return receipts
