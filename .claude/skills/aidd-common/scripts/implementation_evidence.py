"""L3 task/code scope and verification policy; commands belong to L4."""
from pathlib import Path
import os
import math

import artifacts
import implementation_store as store

GENERATED = {'.git', '__pycache__', '.pytest_cache', '.venv', 'node_modules'}
CONTROL = {'.aidd', '.claude', 'Templates', 'specs', 'steering', 'docs'}
CONTROL_FILES = {'.main-flow-assets.json', 'CLAUDE.md'}
# User-local settings are outside AIDD: never counted in any inventory (plan v3 §6.6).
LOCAL_FILES = {'.claude/settings.local.json', 'CLAUDE.local.md'}
ASPECTS = ['implementation-traceability', 'implementation-boundary', 'implementation-tests']


def config_path(feature):
    return store.BASE + '/config/' + store.identifier(feature) + '.json'


def validate_checks(context, checks):
    """検証コマンドの宣言（id・argv・cwd・timeout 1..480・metric・合計 480 秒）。feature と案件レベル（_project.json）で共通。"""
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
    return ids


def policy(context, feature, tasks):
    value = store.read(context.root, config_path(feature))
    if value.get('feature') != feature or set(value.get('tasks', {})) != set(tasks):
        raise ValueError('verification policy must identify the feature and every task')
    ids = validate_checks(context, value.get('checks'))
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
            if path.rstrip('/') in LOCAL_FILES:
                raise ValueError('user-local settings are outside AIDD and cannot be planned: ' + path)
        for path in task.get('review_paths', []) or []:
            if isinstance(path, str) and path.rstrip('/') in LOCAL_FILES:
                raise ValueError('user-local settings are outside AIDD and cannot be planned: ' + path)
        if type(task.get('tdd')) is not bool or (not task['tdd'] and not task.get('non_code_reason')):
            raise ValueError('task must use TDD or identify why it is a non-code task')
    verification_paths = value.get('verification_paths', [])
    if not isinstance(verification_paths, list):
        raise ValueError('verification_paths must be an array')
    for path in verification_paths:
        artifacts.relative_path(path.rstrip('/'))
        if path.rstrip('/') in LOCAL_FILES:
            raise ValueError('user-local settings are outside AIDD and cannot be planned: ' + path)
    generated = value.get('generated_paths', [])
    if not isinstance(generated, list):
        raise ValueError('generated_paths must be an array')
    for path in generated:
        artifacts.relative_path(path.rstrip('/'))
        if path.split('/')[0] in CONTROL or path.rstrip('/') in CONTROL_FILES or any(matches(path.rstrip('/'), scope) or matches(scope.rstrip('/'), path)
                                              for task in value['tasks'].values() for scope in task['allowed_paths']):
            raise ValueError('generated exclusions overlap protected or editable source paths')
    # The task-quality sections (`task_quality` / `task_review`) are L4's: the L4 start gate
    # `task-quality-policy` validates them (L3 does not import L4).
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
        if relative in LOCAL_FILES:
            continue
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
    import task_verification
    return task_verification.receipts(context, execution, stage, current)


REVIEW_DIGEST_VERSION = 2
LOCAL_SETTINGS = '.claude/settings.local.json'


def review_protected(context, feature):
    """feature 承認の照合で凍結する保護対象（D-7、§6.6）。L4 から呼べる公開関数。

    集合：自 feature と推移閉包 D の specs、docs（Feature 方式は固定版の参照、全件方式は 3 文書）、
    steering、Templates、`.claude`（`settings.local.json` を除く）。無関係 feature の specs、作業用 docs の
    実体（Feature 方式）、CONTROL_FILES は含めない。specs と docs は承認操作で変わる status・updated_at を除いた
    digest、それ以外は生バイト。`inventory()`（タスク実行中の保護対象・L4 のタスク品質入力）は変えない。
    """
    import feature_scope
    import docs_revision
    names = [feature, *feature_scope.closure(context, feature)]
    base = Path(context.root)
    result = {}
    for name in names:
        folder = base / 'specs' / name
        for path in sorted(folder.rglob('*')) if folder.is_dir() else []:
            if path.is_file() and not any(part in GENERATED for part in path.parts):
                relative = path.relative_to(base).as_posix()
                result[relative] = (artifacts.protected_digest(str(path)) if path.suffix == '.md'
                                    else store.digest(path.read_bytes()))
    if feature_scope.is_feature(context):
        result['docs_revision'] = docs_revision.fixed(context, feature) or 'unfixed'
    else:
        import phase_rules
        for relative in phase_rules.config()['rules']['docs']['outputs']:
            if (base / relative).is_file():
                result[relative] = artifacts.protected_digest(str(base / relative))
    for top in ('steering', 'Templates', '.claude'):
        folder = base / top
        for path in sorted(folder.rglob('*')) if folder.is_dir() else []:
            relative = path.relative_to(base).as_posix()
            if path.is_file() and relative != LOCAL_SETTINGS and not any(part in GENERATED for part in path.parts):
                result[relative] = store.digest(path.read_bytes())
    return result


def tasks_current(context, feature, version):
    path = Path(context.path('specs/' + feature + '/tasks.md'))
    if version == REVIEW_DIGEST_VERSION:
        return artifacts.protected_digest(str(path))
    return store.digest(path.read_bytes())


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
    version = state.get('review_digest_version')
    protected = (review_protected(context, context.item) if version == REVIEW_DIGEST_VERSION
                 else inventory(context, state['policy'], protected=True))
    import implementation_report_plan
    if value.get('report_plan') != implementation_report_plan.freeze(context, state['policy']):
        raise ValueError('reporting configuration or inputs changed; reinspection required')
    import implementation_flows
    implementation_flows.require_saved(context, value)
    requests.check_feature_ready(context, context.item)
    if (value['code'] != feature_inventory(context, state['policy'])
            or not requests.same_inputs(context, context.item, value['protected'], protected)
            or value['tasks_current_sha256'] != tasks_current(context, context.item, version)
            or not requests.same_inputs(context, context.item, value['inputs'], requests.input_signature(context, context.item))
            or value['tasks'] != state['completed']):
        raise ValueError('implementation changed since feature inspection; reinspection required')
    return value
