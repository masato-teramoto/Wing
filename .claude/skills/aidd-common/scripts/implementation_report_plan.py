"""Feature reporting configuration, independent of task plans and check_ids."""
from pathlib import Path

import artifacts
import implementation_evidence as evidence
import implementation_reports as reports
import implementation_store as store


def path(feature):
    return store.BASE + '/reporting/' + store.identifier(feature) + '.json'


def freeze(context, task_policy):
    location = path(context.item)
    if not Path(context.path(location)).is_file():
        raise ValueError('feature reporting plan required before final inspection: ' + location)
    value = store.read(context.root, location)
    if value.get('schema') != 1 or value.get('feature') != context.item:
        raise ValueError('reporting plan must identify its feature (schema 1)')
    specifications = value.get('specifications')
    if (not isinstance(specifications, list) or not specifications
            or any(not isinstance(p, str) for p in specifications) or len(specifications) != len(set(specifications))):
        raise ValueError('reporting specifications must identify readable test/verification specifications')
    for name in specifications:
        if Path(name).suffix.lower() not in ('.md', '.html', '.htm'):
            raise ValueError('specifications must be Markdown or HTML')
    scopes = value.get('verification_paths')
    if not isinstance(scopes, list) or not scopes:
        raise ValueError('reporting verification_paths must identify runner/configuration inputs')
    inventory = {**evidence.inventory(context, task_policy), **evidence.inventory(context, task_policy, protected=True)}
    inputs = {}
    for scope in specifications + scopes:
        if not isinstance(scope, str):
            raise ValueError('reporting input paths must be strings')
        artifacts.relative_path(scope.rstrip('/'))
        if any(part in evidence.GENERATED | {'.aidd', '.claude'} for part in scope.split('/')):
            raise ValueError('reporting inputs cannot be generated execution evidence')
        selected = {p: h for p, h in inventory.items() if evidence.matches(p, scope)}
        if not selected:
            raise ValueError('reporting input missing or excluded: ' + scope)
        inputs.update(selected)
    checks = value.get('checks')
    if not isinstance(checks, list):
        raise ValueError('reporting checks must be an array')
    ids, budget = [], sum(c['timeout_seconds'] for c in task_policy['checks'])
    for check in checks:
        reports.validate_check(check)
        ids.append(store.identifier(check.get('id')))
        if not check.get('reports'):
            raise ValueError('each reporting check must declare readable outputs')
        postprocess = check.get('postprocess', [])
        if not isinstance(postprocess, list):
            raise ValueError('postprocess must be an array')
        for command in [check] + postprocess:
            if not isinstance(command, dict):
                raise ValueError('reporting command must be an object')
            argv = command.get('argv')
            if not isinstance(argv, list) or not argv or any(not isinstance(arg, str) or not arg for arg in argv):
                raise ValueError('reporting argv must be a nonempty string array')
            cwd = command.get('cwd', check.get('cwd', '.'))
            if cwd != '.':
                artifacts.resolve(context.root, cwd)
            timeout = command.get('timeout_seconds')
            if type(timeout) is not int or not 1 <= timeout <= 480:
                raise ValueError('each reporting command requires a timeout in 1..480 seconds')
            budget += timeout
    if len(ids) != len(set(ids)):
        raise ValueError('duplicate reporting check ID')
    if budget > 480:
        raise ValueError('verification + reporting + postprocessing budget exceeds 480 seconds')
    reason = value.get('not_applicable_reason')
    non_code = all(not t['tdd'] and t.get('non_code_reason') for t in task_policy['tasks'].values())
    if reason and (not non_code or not isinstance(reason, str) or not reason.strip()):
        raise ValueError('test/coverage exemption requires a planned non-code feature')
    if not reason and not any(c.get('test_results') for c in checks):
        raise ValueError('final reporting requires unit-test results and coverage')
    return {'policy': value, 'sha256': store.digest(Path(context.path(location)).read_bytes()), 'inputs': inputs}
