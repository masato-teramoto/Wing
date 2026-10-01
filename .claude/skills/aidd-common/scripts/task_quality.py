"""L4 generation artifacts and verification. Specification content is human-reviewed.

MCP evidence belongs to the unified task review, not this generation artifact. This module does not add a semantic
review of the generated description and never invents a clean MCP response.
"""
import copy
import json

import implementation_store as store
import task_quality_inputs as inputs
import task_quality_storage as storage
import unit_test_specification as specifications

PROFILE = 'task-specification-v1'
MCP = {'status': 'managed_by_task_review', 'reason': 'MCP実施状態は統合タスクレビューの証跡を参照。仕様書生成結果はMCPの合否を表さない。'}


def reference(root, execution_id, round_number):
    result, manifest = storage.load_bundle(root, execution_id, round_number)
    return {'execution_id': execution_id, 'round': round_number,
            'snapshot_sha256': result['specification']['snapshot_sha256'],
            'manifest_sha256': store.fingerprint(manifest)}


def previous_snapshot(root, ref, feature, scope):
    if ref is None:
        return None
    result, manifest = storage.load_bundle(root, ref['execution_id'], ref['round'])
    if (result['target']['feature'] != feature or result['specification']['scope'] != scope
            or result['specification']['snapshot_sha256'] != ref['snapshot_sha256']
            or store.fingerprint(manifest) != ref['manifest_sha256']):
        raise ValueError('previous specification reference differs')
    return result['specification']


def make_request(context, execution, round_number, previous, instructions):
    scope = inputs.scope_of(execution)
    snapshot = inputs.source(context, execution)
    previous_snapshot(context.root, previous, execution['feature'], scope)
    return {'schema': 1, 'profile': PROFILE, 'target': inputs.target(execution, round_number, snapshot),
            'scope': scope, 'inputs': snapshot, 'previous': previous,
            'instruction': instructions.get('instruction', ''),
            'corrections': copy.deepcopy(instructions.get('corrections', {})), 'mcp': MCP}


def verify_request(context, execution, pointer, current=True):
    request = storage.read(context.root, execution['execution_id'], pointer['round'], 'request.json')
    if (store.fingerprint(request) != pointer['request_sha256'] or request.get('schema') != 1
            or request.get('profile') != PROFILE or request.get('mcp') != MCP
            or request['scope'] != inputs.scope_of(execution)
            or request['target'] != inputs.target(execution, pointer['round'], request['inputs'])):
        raise ValueError('task specification request identity or version differs')
    if current and request['inputs'] != inputs.source(context, execution):
        raise ValueError('task specification inputs changed; retry the task before regenerating')
    return request


def generate(context, request, data):
    fields = {'status', 'target', 'request_sha256', 'cases', 'non_case_files',
              'additions', 'updates', 'no_cases_reason'}
    if (not isinstance(data, dict) or set(data) != fields or data['status'] != 'completed'
            or data['target'] != request['target'] or data['request_sha256'] != store.fingerprint(request)):
        raise ValueError('generation result must identify the exact task specification request')
    inventory = inputs.case_inventory(request, data['cases'], data['non_case_files'])
    reason = data['no_cases_reason']
    if not isinstance(reason, str) or (not inventory and not reason.strip()) or (inventory and reason):
        raise ValueError('an empty case inventory requires its actual reason')
    previous = previous_snapshot(context.root, request['previous'], request['target']['feature'], request['scope'])
    specification = specifications.update_specification(previous, scope=request['scope'],
        input_sha256=request['target']['input_sha256'], inventory=inventory,
        additions=data['additions'], updates=data['updates'], corrections=request['corrections'])
    result = {'schema': 1, 'profile': PROFILE, 'target': request['target'],
              'request_sha256': store.fingerprint(request), 'specification': specification,
              'case_sources': data['cases'], 'non_case_files': data['non_case_files'],
              'no_cases_reason': reason, 'mcp': MCP}
    return copy.deepcopy(result)


def save(context, request, data):
    result = generate(context, request, data)
    target = request['target']
    storage.save_bundle(context.root, target['execution_id'], target['review_round'], result, summary(result))
    return result


def summary(result):
    target, spec = result['target'], result['specification']
    literal = specifications._literal
    lines = ['# タスクの単体テスト仕様書確認', '',
             '対象: ' + literal(target['feature']) + ' / タスク ' + literal(target['task_id']), '',
             '[単体テスト仕様書](specification.md)', '',
             '生成済みテストを基にした人の確認資料です。仕様書内容の追加レビュー工程は設けていません。', '',
             '**外部コードレビュー: 統合タスクレビューで確認**', '', MCP['reason'], '',
             '## 今回の仕様書差分', '']
    for key, label in (('added', '追加'), ('updated', '変更'), ('removed', '削除'), ('unchanged', '本文変更なし')):
        lines.append('- ' + label + ': ' + (', '.join(literal(name) for name in spec['changes'][key]) or 'なし'))
    if result['no_cases_reason']:
        lines += ['', '現行ケースなしの理由: ' + literal(result['no_cases_reason'])]
    if result['non_case_files']:
        lines += ['', '## ケースを含まない入力ファイル', '']
        lines += ['- ' + literal(path) + ': ' + literal(reason) for path, reason in result['non_case_files'].items()]
    lines += ['', '続行・修正・保留を回答してください。未回答・保留の間はタスクを完了しません。', '']
    return '\n'.join(lines)


def load(context, execution, pointer, current=True):
    request = verify_request(context, execution, pointer, current)
    result, manifest = storage.load_bundle(context.root, execution['execution_id'], pointer['round'])
    if (result.get('target') != request['target'] or result.get('request_sha256') != pointer['request_sha256']
            or result.get('mcp') != MCP or result.get('profile') != PROFILE
            or result['specification']['input_sha256'] != request['target']['input_sha256']):
        raise ValueError('task specification result differs from its request')
    return result, manifest


def accept(context, execution, pointer, response):
    result, manifest = load(context, execution, pointer)
    if response.get('action') != 'approve':
        raise ValueError('task specification confirmation requires an actual continue response')
    value = {'schema': 1, 'target': result['target'], 'manifest_sha256': store.fingerprint(manifest),
             'response_sha256': store.fingerprint(response), 'verification': 'passed', 'mcp': MCP}
    storage.write_once(context.root, execution['execution_id'], pointer['round'], 'acceptance.json', value)
    return value


def require_acceptance(context, execution, pointer, response, current=True):
    result, manifest = load(context, execution, pointer, current)
    value = storage.read(context.root, execution['execution_id'], pointer['round'], 'acceptance.json')
    expected = {'schema': 1, 'target': result['target'], 'manifest_sha256': store.fingerprint(manifest),
                'response_sha256': store.fingerprint(response), 'verification': 'passed', 'mcp': MCP}
    if response.get('action') != 'approve' or value != expected:
        raise ValueError('task confirmation is missing or belongs to a different version')
    return value


def latest_for_feature(context, state):
    """Only sealed, current suite descriptions may enter the final report."""
    import implementation_evidence as evidence
    policy = state['policy']
    if not policy.get('task_quality'):
        return []
    code = evidence.inventory(context, policy)
    latest = state.get('specifications', {})
    suites = policy['task_quality']['suites']
    if set(latest) != set(suites):
        raise ValueError('current specifications for all configured suites are required')
    results = []
    for scope, suite in suites.items():
        ref = latest[scope]
        spec = previous_snapshot(context.root, ref, policy['feature'], scope)
        request = storage.read(context.root, ref['execution_id'], ref['round'], 'request.json')
        for kind, patterns in (('test_files', suite['test_paths']), ('shared_files', suite['shared_paths'])):
            actual = {p: digest for p, digest in code.items() if any(evidence.matches(p, pattern) for pattern in patterns)}
            if request['inputs'][kind] != actual:
                raise ValueError('suite specification inputs changed; regenerate and confirm scope: ' + scope)
        if request['inputs']['upstream'] != state['inputs']:
            raise ValueError('suite specification uses old requirements or settings: ' + scope)
        if not any(proof['execution_id'] == ref['execution_id'] for proof in state['completed'].values()):
            raise ValueError('latest specification has no current completed task')
        results.append({'scope': scope, 'path': storage.directory(ref['execution_id'], ref['round']) + '/specification.md',
                        'sha256': spec['body_sha256'], 'reference': ref})
    return results
