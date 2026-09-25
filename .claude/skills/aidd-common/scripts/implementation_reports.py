"""Native OSS report artifacts and small JUnit/TRX completion checks.

No test-case normalization, metric calculation, or HTML result scraping.
"""
from pathlib import Path
import xml.etree.ElementTree as ET

import artifacts
import implementation_store as store


def relative(value):
    artifacts.relative_path(value)
    if any(part.startswith('.') for part in Path(value).parts):
        raise ValueError('report paths must be visible paths below the attempt directory')
    return value


def plain_file(root, relative_path):
    path = artifacts.resolve(root, relative_path)
    base = Path(root).resolve()
    for item in (path, *path.parents):
        if item == base:
            break
        if item.is_symlink() or getattr(item, 'is_junction', lambda: False)():
            raise ValueError('linked report or specification path: ' + relative_path)
    return path


def validate_check(check):
    if not isinstance(check, dict):
        raise ValueError('reporting check must be an object')
    entries = check.get('reports', [])
    if not isinstance(entries, list):
        raise ValueError('reports must be an array')
    for entry in entries:
        if not isinstance(entry, dict) or entry.get('role') not in ('tests', 'coverage', 'quality'):
            raise ValueError('report role must be tests, coverage or quality')
        relative(entry.get('path'))
        if Path(entry['path']).suffix.lower() not in ('.html', '.htm', '.md'):
            raise ValueError('readable reports must be HTML or Markdown')
        if any(not isinstance(entry.get(k), str) or not entry[k].strip() for k in ('scope', 'tool')):
            raise ValueError('each report needs its actual scope and tool/version')
        if 'viewing' in entry and not isinstance(entry['viewing'], str):
            raise ValueError('report viewing instructions must be text')
        if entry['role'] == 'quality':
            metrics = entry.get('metrics')
            if not isinstance(metrics, list) or not metrics or any(not isinstance(m, str) or not m.strip() for m in metrics):
                raise ValueError('quality reports must name the verified metrics')
    if len({e['path'] for e in entries}) != len(entries):
        raise ValueError('duplicate report entry path')
    required = check.get('report_files', [])
    if not isinstance(required, list):
        raise ValueError('report_files must be an array of required asset paths/globs')
    for pattern in required:
        relative(pattern)
    results = check.get('test_results')
    if results is not None:
        if not isinstance(results, dict) or results.get('format') not in ('junit', 'trx'):
            raise ValueError('test_results format must be junit or trx')
        paths = results.get('paths')
        if not isinstance(paths, list) or not paths:
            raise ValueError('test_results needs native result paths/globs')
        for pattern in paths:
            relative(pattern)
        if not {'tests', 'coverage'} <= {e['role'] for e in entries}:
            raise ValueError('unit tests require both readable results and coverage')
    elif any(e['role'] in ('tests', 'coverage') for e in entries):
        raise ValueError('unit-test reports need native JUnit or TRX results')


def files(root, directory):
    base = plain_file(root, directory)
    if not base.is_dir():
        raise ValueError('report attempt directory missing')
    result = {}
    for path in sorted(base.rglob('*')):
        relative_path = path.relative_to(Path(root)).as_posix()
        plain_file(root, relative_path)
        if path.is_file():
            result[path.relative_to(base).as_posix()] = store.digest(path.read_bytes())
        elif not path.is_dir():
            raise ValueError('unsupported report artifact: ' + relative_path)
    return result


def select(root, directory, patterns):
    base = plain_file(root, directory)
    selected = set()
    for pattern in patterns:
        relative(pattern)
        matches = [p for p in base.glob(pattern) if p.is_file()]
        if not matches:
            raise ValueError('required report output missing: ' + pattern)
        for path in matches:
            plain_file(root, path.relative_to(Path(root)).as_posix())
            if not path.stat().st_size:
                raise ValueError('empty report output: ' + str(path))
            selected.add(path)
    return sorted(selected)


def test_summary(paths, format_name):
    total = 0
    for path in paths:
        raw = path.read_bytes()
        if len(raw) > 20 * 1024 * 1024 or b'<!DOCTYPE' in raw.upper() or b'<!ENTITY' in raw.upper():
            raise ValueError('unsupported native test XML')
        try:
            tree = ET.fromstring(raw)
        except ET.ParseError as error:
            raise ValueError('invalid native test XML: ' + str(error)) from error
        tag = lambda e: e.tag.rsplit('}', 1)[-1]
        if format_name == 'junit':
            if tag(tree) not in ('testsuite', 'testsuites'):
                raise ValueError('expected JUnit testsuite(s)')
            cases = [e for e in tree.iter() if tag(e) == 'testcase']
            if any(not e.get('name') for e in cases):
                raise ValueError('JUnit test cases must have names')
            if any(tag(e) in ('failure', 'error', 'skipped') for e in tree.iter()):
                raise ValueError('unit tests failed, errored or skipped')
            for suite in (e for e in tree.iter() if tag(e) in ('testsuite', 'testsuites')):
                for key in ('failures', 'errors', 'skipped', 'disabled'):
                    if int(suite.get(key, '0')) != 0:
                        raise ValueError('unit tests are incomplete: ' + key)
                if suite.get('tests') is not None and int(suite.get('tests')) != sum(tag(e) == 'testcase' for e in suite.iter()):
                    raise ValueError('JUnit case count differs from declared total')
            if any(e.get('status', 'run') in ('notrun', 'disabled') for e in cases):
                raise ValueError('unit tests were not executed')
        else:
            if tag(tree) != 'TestRun':
                raise ValueError('expected TRX TestRun')
            cases = [e for e in tree.iter() if tag(e) == 'UnitTestResult']
            counters = [e for e in tree.iter() if tag(e) == 'Counters']
            if (any(e.get('outcome') != 'Passed' for e in cases) or len(counters) != 1
                    or any(int(counters[0].get(k, '-1')) != len(cases) for k in ('total', 'executed', 'passed'))):
                raise ValueError('TRX unit tests are incomplete or unsuccessful')
        total += len(cases)
    if total == 0:
        raise ValueError('no executed unit test cases')
    return {'format': format_name, 'executed': total, 'passed': total}


def collect(root, check, directory):
    inventory = files(root, directory)
    for entry in check.get('reports', []):
        path = select(root, directory, [entry['path']])[0]
        if not path.read_text(encoding='utf-8').strip():
            raise ValueError('blank readable report: ' + entry['path'])
    select(root, directory, check.get('report_files', []))
    value = {'directory': directory, 'entries': check.get('reports', []), 'files': inventory}
    if check.get('test_results'):
        results = check['test_results']
        value['tests'] = test_summary(select(root, directory, results['paths']), results['format'])
    return value


def verify(root, check, receipt):
    report = receipt.get('report')
    if not isinstance(report, dict) or collect(root, check, report['directory']) != report:
        raise ValueError('report artifacts changed, missing or from a different contract')


def copy_specifications(root, paths, directory):
    copies = []
    for source in paths:
        path = plain_file(root, source)
        raw = path.read_bytes()
        if path.suffix.lower() not in ('.md', '.html', '.htm') or not raw.strip():
            raise ValueError('test specification must be nonempty Markdown or HTML')
        target = directory + '/' + source
        destination = plain_file(root, target)
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_bytes(raw)
        copies.append({'source': source, 'path': target, 'sha256': store.digest(raw)})
    return copies


def verify_specifications(root, expected, copies):
    if [c['source'] for c in copies] != expected:
        raise ValueError('test specification coverage differs from policy')
    for copy in copies:
        if any(store.digest(plain_file(root, copy[key]).read_bytes()) != copy['sha256'] for key in ('source', 'path')):
            raise ValueError('test specification changed or missing')
