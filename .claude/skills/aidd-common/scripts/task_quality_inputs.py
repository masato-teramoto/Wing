"""L4 specification applicability and input fingerprints; no task progression."""
import copy
from pathlib import Path

import artifacts
import implementation_evidence as evidence
import implementation_reports as reports
import implementation_store as store
import task_verification


def validate_policy(policy):
    value = policy.get('task_quality')
    if value is None:
        if any('specification_scope' in task or 'specification_exemption' in task for task in policy['tasks'].values()):
            raise ValueError('specification settings require task_quality policy')
        return
    if (not isinstance(value, dict) or set(value) != {'schema', 'suites'}
            or type(value['schema']) is not int or value['schema'] != 2
            or not isinstance(value['suites'], dict)):
        raise ValueError('task_quality requires schema 2 and suites; MCP is configured in task_review')
    for scope, suite in value['suites'].items():
        store.identifier(scope)
        if not isinstance(suite, dict) or set(suite) != {'test_paths', 'shared_paths'}:
            raise ValueError('suite requires test_paths and shared_paths')
        for key in ('test_paths', 'shared_paths'):
            paths = suite[key]
            if not isinstance(paths, list) or (key == 'test_paths' and not paths):
                raise ValueError('suite paths must be arrays; test_paths must be nonempty')
            for path in paths:
                if not isinstance(path, str):
                    raise ValueError('suite path must be text')
                artifacts.relative_path(path[:-1] if path.endswith('/') else path)
                if path.split('/')[0] in evidence.CONTROL | evidence.GENERATED or path.rstrip('/') in evidence.CONTROL_FILES:
                    raise ValueError('suite paths must identify source inputs')
                if any(path.rstrip('/') == exclusion.rstrip('/') or evidence.matches(path.rstrip('/'), exclusion)
                       or evidence.matches(exclusion.rstrip('/'), path)
                       for exclusion in policy.get('generated_paths', [])):
                    raise ValueError('suite inputs overlap generated exclusions')
            if len(paths) != len(set(paths)):
                raise ValueError('duplicate suite input path')
    used = set()
    for task in policy['tasks'].values():
        scope, reason = task.get('specification_scope'), task.get('specification_exemption')
        if scope is not None:
            if not isinstance(scope, str) or scope not in value['suites'] or reason is not None:
                raise ValueError('task requires a known specification scope or an exemption, not both')
            used.add(scope)
        elif task.get('tdd') or not isinstance(reason, str) or not reason.strip():
            raise ValueError('non-code specification exemption needs an explicit reason')
    if used != set(value['suites']):
        raise ValueError('task quality suites must be assigned to tasks')


def scope_of(execution):
    validate_policy(execution['policy'])
    if execution['policy'].get('task_quality') is None:
        return None
    return execution['policy']['tasks'][execution['task_id']].get('specification_scope')


def source(context, execution):
    task_verification.validate_task(context, execution)
    code = evidence.check_scope(context, execution)
    directory = store.BASE + '/runs/' + execution['execution_id']
    checks = {}
    for name in ('red.json', 'green.json', 'verify.json', 'result.json'):
        path = reports.plain_file(context.root, directory + '/' + name)
        if path.exists():
            checks[name] = store.digest(path.read_bytes())
    scope = scope_of(execution)
    suite = execution['policy']['task_quality']['suites'][scope]
    tests = {path: digest for path, digest in code.items()
             if any(evidence.matches(path, pattern) for pattern in suite['test_paths'])}
    shared = {path: digest for path, digest in code.items()
              if any(evidence.matches(path, pattern) for pattern in suite['shared_paths'])}
    for pattern in suite['shared_paths']:
        if not any(evidence.matches(path, pattern) for path in shared):
            raise ValueError('shared specification input missing: ' + pattern)
    return {'code': code, 'protected': evidence.inventory(context, execution['policy'], protected=True),
            'upstream': copy.deepcopy(execution['inputs']), 'checks': checks,
            'test_files': tests, 'shared_files': shared}


def target(execution, round_number, inputs):
    return {**{key: execution[key] for key in ('feature', 'plan_ref', 'task_id', 'task_item', 'execution_id', 'request_id')},
            'review_round': round_number, 'input_sha256': store.fingerprint(inputs),
            'config_sha256': store.fingerprint(execution['policy'])}


def case_inventory(request, cases, non_case_files):
    """The generation Skill identifies cases; the controller hashes actual inputs.

    A file hash is deliberately conservative: changing one test re-evaluates all
    cases in that file. Case completeness remains the collector's responsibility.
    """
    if not isinstance(cases, dict) or not isinstance(non_case_files, dict):
        raise ValueError('cases and non_case_files must be objects')
    tests = request['inputs']['test_files']
    covered = set()
    inventory = {}
    for case_id, path in cases.items():
        if not isinstance(case_id, str) or not case_id.strip() or '\n' in case_id:
            raise ValueError('stable runner case ID required')
        if not isinstance(path, str) or path not in tests:
            raise ValueError('case must reference a collected test file')
        covered.add(path)
        inventory[case_id] = store.fingerprint({'test': {path: tests[path]},
            'shared': request['inputs']['shared_files'], 'upstream': request['inputs']['upstream'],
            'test_support': {name: tests[name] for name in non_case_files if name in tests}})
    for path, reason in non_case_files.items():
        if path not in tests or path in covered or not isinstance(reason, str) or not reason.strip():
            raise ValueError('non-case file needs an unambiguous actual reason')
    if covered | set(non_case_files) != set(tests):
        raise ValueError('generation must account for every collected test file')
    return inventory
