"""L3 task/code scope and verification policy; commands belong to L4."""
from pathlib import Path
import os
import math

import artifacts
import implementation_store as store

GENERATED = {'.git', '__pycache__', '.pytest_cache', '.venv', 'node_modules'}
CONTROL = {'.aidd', '.claude', 'Templates', 'specs', 'steering', 'docs'}
CONTROL_FILES = {'.main-flow-assets.json', 'CLAUDE.md', 'aidd-run.py'}
ASPECTS = ['implementation-traceability', 'implementation-boundary', 'implementation-tests']


def config_path(feature):
    return store.BASE + '/config/' + store.identifier(feature) + '.json'


def policy(context, feature, tasks):
    value = store.read(context.root, config_path(feature))
    if value.get('feature') != feature or set(value.get('tasks', {})) != set(tasks):
        raise ValueError('verification policy must identify the feature and every task')
    checks = value.get('checks')
    if not isinstance(checks, list) or not checks:
        raise ValueError('nonempty mandatory verification checks required')
    ids = []
    for check in checks:
        store.identifier(check.get('id'))
        ids.append(check['id'])
        argv = check.get('argv')
        if not isinstance(argv, list) or not argv or any(not isinstance(arg, str) or not arg for arg in argv):
            raise ValueError('verification argv must be a nonempty string array')
        cwd = check.get('cwd', '.')
        if cwd != '.':
            artifacts.resolve(context.root, cwd)
        timeout = check.get('timeout_seconds')
        if type(timeout) is not int or not 1 <= timeout <= 480:
            raise ValueError('each check requires a timeout in 1..480 seconds')
        metric = check.get('metric')
        if metric:
            artifacts.resolve(context.root, metric['path'])
            if (not isinstance(metric.get('keys'), list) or not metric['keys']
                    or any(not isinstance(key, str) for key in metric['keys'])
                    or type(metric.get('minimum')) not in (int, float) or not math.isfinite(metric['minimum'])):
                raise ValueError('metric needs JSON keys and numeric minimum')
    if len(ids) != len(set(ids)):
        raise ValueError('duplicate check ID')
    if sum(c['timeout_seconds'] for c in checks) > 480:
        raise ValueError('aggregate tool budget exceeds 480 seconds; split the checks or decide on an L0 timeout extension')
    if value.get('feature_checks') != ids:
        raise ValueError('feature_checks must include every mandatory check in declared order')
    for key, task in value['tasks'].items():
        selected = task.get('check_ids')
        if not isinstance(selected, list) or not selected or len(selected) != len(set(selected)) or set(selected) - set(ids):
            raise ValueError('each task needs known, unique check IDs')
        if selected != [check_id for check_id in ids if check_id in selected]:
            raise ValueError('task check IDs must preserve declared command order')
        paths = task.get('allowed_paths')
        if not isinstance(paths, list) or not paths:
            raise ValueError('each task requires explicit allowed paths derived from Boundary')
        for path in paths:
            artifacts.relative_path(path.rstrip('/'))
            if path.split('/')[0] in CONTROL | GENERATED or path.rstrip('/') in CONTROL_FILES:
                raise ValueError('implementation cannot modify workflow/specification assets')
        if type(task.get('tdd')) is not bool or (not task['tdd'] and not task.get('non_code_reason')):
            raise ValueError('task must use TDD or identify why it is a non-code task')
    verification_paths = value.get('verification_paths', [])
    if not isinstance(verification_paths, list):
        raise ValueError('verification_paths must be an array')
    for path in verification_paths:
        artifacts.relative_path(path.rstrip('/'))
    generated = value.get('generated_paths', [])
    if not isinstance(generated, list):
        raise ValueError('generated_paths must be an array')
    for path in generated:
        artifacts.relative_path(path.rstrip('/'))
        if path.split('/')[0] in CONTROL or path.rstrip('/') in CONTROL_FILES or any(matches(path.rstrip('/'), scope) or matches(scope.rstrip('/'), path)
                                              for task in value['tasks'].values() for scope in task['allowed_paths']):
            raise ValueError('generated exclusions overlap protected or editable source paths')
    return value


def matches(path, scope):
    return path.startswith(scope) if scope.endswith('/') else path == scope


def inventory(context, policy_value, protected=False):
    base = Path(context.root)
    result = {}
    paths = []
    for directory, subdirectories, files in os.walk(base, followlinks=False):
        parent = Path(directory)
        kept = []
        for name in sorted(subdirectories):
            relative = (parent / name).relative_to(base).as_posix()
            if name in GENERATED or any(matches(relative + '/', scope) for scope in policy_value.get('generated_paths', [])):
                continue
            if parent == base and (name == '.aidd' or (name in CONTROL and not protected)):
                continue
            if (parent / name).is_symlink() or getattr(parent / name, 'is_junction', lambda: False)():
                raise ValueError('linked implementation directory is unsupported: ' + relative)
            kept.append(name)
        subdirectories[:] = kept
        paths.extend(parent / name for name in files)
    for path in sorted(paths):
        relative = path.relative_to(base).as_posix()
        parts = relative.split('/')
        if any(part in GENERATED for part in parts):
            continue
        if any(matches(relative, scope) for scope in policy_value.get('generated_paths', [])):
            continue
        is_control = parts[0] in CONTROL or relative in CONTROL_FILES
        if is_control:
            # Specification bytes are protected separately, including unrelated specs.
            if not protected or parts[0] == '.aidd':
                continue
        elif protected:
            continue
        if path.is_symlink() or getattr(path, 'is_junction', lambda: False)():
            raise ValueError('linked implementation path is unsupported: ' + relative)
        if path.is_file():
            data = path.read_bytes()
            if protected and parts[0] == 'specs' and path.name == 'tasks.md':
                import task_runtime
                data = task_runtime.project(path, data)
            result[relative] = store.digest(data)
    return result


def changed(before, after):
    return sorted(p for p in set(before) | set(after) if before.get(p) != after.get(p))


def feature_inventory(context, policy_value):
    scopes = [p for task in policy_value['tasks'].values() for p in task['allowed_paths']]
    scopes += policy_value.get('verification_paths', [])
    for scope in scopes:
        artifacts.relative_path(scope.rstrip('/'))
    return {p: h for p, h in inventory(context, policy_value).items() if any(matches(p, scope) for scope in scopes)}


def check_scope(context, execution):
    current = inventory(context, execution['policy'])
    outside = [p for p in changed(execution['baseline'], current)
               if not any(matches(p, scope) for scope in execution['allowed_paths'])]
    if outside:
        raise ValueError('task changed files outside Boundary: ' + ', '.join(outside))
    if inventory(context, execution['policy'], protected=True) != execution['protected']:
        raise ValueError('implementation modified protected specifications or workflow assets')
    return current


def receipts(context, execution, stage='verify', current=True):
    path = store.BASE + '/runs/' + execution['execution_id'] + '/' + stage + '.json'
    result = store.read(context.root, path)
    expected = execution['policy']['tasks'][execution['task_id']]['check_ids']
    if (result.get('source_changed') or result.get('stage') != stage
            or result.get('execution_id') != execution['execution_id'] or result.get('task_id') != execution['task_id']
            or result.get('policy_hash') != store.fingerprint(execution['policy'])
            or (current and result.get('code') != inventory(context, execution['policy']))
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


def review_path(feature):
    return store.BASE + '/features/' + store.identifier(feature) + '/review.json'


def review_digest(context, target):
    if target != review_path(context.item):
        raise ValueError('wrong implementation review target')
    verify_review(context)
    return store.digest(Path(context.path(target)).read_bytes())


def verify_review(context):
    import implementation_requests as requests
    state = requests.feature_state(context, context.item)
    value = store.read(context.root, review_path(context.item))
    import implementation_report_plan
    if value.get('report_plan') != implementation_report_plan.freeze(context, state['policy']):
        raise ValueError('reporting configuration or inputs changed; reinspection required')
    import implementation_flows
    implementation_flows.require_saved(context, value)
    requests.check_feature_ready(context, context.item)
    if (value['code'] != feature_inventory(context, state['policy'])
            or value['protected'] != inventory(context, state['policy'], protected=True)
            or value['tasks_current_sha256'] != store.digest(Path(context.path('specs/' + context.item + '/tasks.md')).read_bytes())
            or value['inputs'] != requests.input_signature(context, context.item)
            or value['tasks'] != state['completed']):
        raise ValueError('implementation changed since feature inspection; reinspection required')
    return value
