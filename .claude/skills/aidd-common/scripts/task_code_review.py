"""Task-scoped L4 review inputs and receipts. No progression or model transport."""
import copy
import difflib
import json
from pathlib import Path

import artifacts
import implementation_evidence as evidence
import implementation_store as store
import task_quality_storage as storage
import task_verification
import task_code_review_mcp as mcp

PROFILE = 'implementation-task-review-v1'
# 3 段の (2) の reverify 用レビュー（L4 修正計画 M-05・M-06）。変更の集合（共有ファイル・依存先・docs・steering 等の前後）を読む。
REVERIFY_PROFILE = 'implementation-task-reverify-v1'
ASPECTS = list(evidence.ASPECTS)
RULE_FILES = ['.claude/agents/check-runner.md'] + [
    '.claude/skills/' + name + '/SKILL.md' for name in ['task-implement-check', 'implement-check'] + ASPECTS]


def validate_policy(policy):
    config = policy.get('task_review')
    if config is None:
        if any('review_paths' in task or 'review_exemption' in task for task in policy['tasks'].values()):
            raise ValueError('task review fields require task_review policy')
        return
    if not isinstance(config, dict) or config != {'schema': 2, 'engine': 'host', 'mcp': 'ace'} or type(config.get('schema')) is not int:
        raise ValueError('task_review requires schema 2, engine=host and mcp=ace')
    for task in policy['tasks'].values():
        if not task['tdd'] and (not isinstance(task.get('non_code_reason'), str) or not task['non_code_reason'].strip()):
            raise ValueError('non-code task review policy requires an actual non-code reason')
        reason = task.get('review_exemption')
        if reason is not None:
            if task['tdd'] or not task.get('non_code_reason') or not isinstance(reason, str) or not reason.strip():
                raise ValueError('only explicitly non-code work can have a reasoned review exemption')
            if 'review_paths' in task:
                raise ValueError('an exempt task cannot declare review paths')
            continue
        paths = task.get('review_paths')
        if (not isinstance(paths, list) or any(not isinstance(p, str) for p in paths)
                or len(paths) != len(set(paths))):
            raise ValueError('review_paths must explicitly list additional dependencies (or [])')
        for path in paths:
            artifacts.relative_path(path.rstrip('/'))
            if path.split('/')[0] in evidence.CONTROL | evidence.GENERATED or path.rstrip('/') in evidence.CONTROL_FILES:
                raise ValueError('review_paths must identify source inputs')
            if any(evidence.matches(path.rstrip('/'), p) or evidence.matches(p.rstrip('/'), path)
                   for p in policy.get('generated_paths', [])):
                raise ValueError('review dependency overlaps generated exclusions')


def enabled(execution):
    validate_policy(execution['policy'])
    return bool(execution['policy'].get('task_review')) and not execution['policy']['tasks'][execution['task_id']].get('review_exemption')


def source_text(path):
    try:
        return Path(path).read_bytes().decode('utf-8')
    except UnicodeDecodeError:
        return None


def baseline(context, execution):
    if not enabled(execution):
        return None
    return {p: source_text(context.path(p)) for p in execution['baseline']
            if any(evidence.matches(p, pattern) for pattern in execution['allowed_paths'])}


def snapshot(context, execution):
    task_verification.validate_task(context, execution)
    code = evidence.check_scope(context, execution)
    policy = execution['policy']['tasks'][execution['task_id']]
    selected = {p: digest for p, digest in code.items()
                if any(evidence.matches(p, pattern) for pattern in execution['allowed_paths'] + policy['review_paths'])}
    for pattern in policy['review_paths']:
        if not any(evidence.matches(p, pattern) for p in selected):
            raise ValueError('review dependency missing: ' + pattern)
    changed = evidence.changed(execution['baseline'], code)
    if execution.get('reverify'):
        # reverify（3 段の (2)）：コード編集は 0 件。変わった共有ファイルのうち、このタスクのレビュー対象に入るものを見る。
        changed = sorted(p for p in execution['reverify'].get('code', {}) if p in selected)
    before = execution.get('review_baseline')
    if before is None:
        raise ValueError('task review baseline missing; create a new execution')
    texts = {p: source_text(context.path(p)) for p in selected}
    diffs = {}
    for path in changed:
        diffs[path] = ''.join(difflib.unified_diff((before.get(path) or '').splitlines(True),
            (texts.get(path) or '').splitlines(True), fromfile='before/' + path, tofile='after/' + path))
    directory = store.BASE + '/runs/' + execution['execution_id']
    checks = {directory + '/' + name: store.digest(Path(context.path(directory + '/' + name)).read_bytes())
              for name in ('red.json', 'green.json', 'verify.json') if Path(context.path(directory + '/' + name)).is_file()}
    for path in list(checks):
        for receipt in store.read(context.root, path)['receipts']:
            for key in ('stdout', 'stderr'):
                log = receipt[key]
                checks[log['path']] = log['sha256']
    return {'code': selected, 'deleted': sorted(set(changed) - set(code)), 'changed_paths': changed,
            'diffs': diffs, 'source_text': texts, 'unreadable': [p for p, text in texts.items() if text is None], 'upstream': copy.deepcopy(execution['inputs']), 'checks': checks,
            'rules': {p: store.digest(Path(context.path(p)).read_bytes()) for p in RULE_FILES}, 'mcp_version': mcp.version()}


def make_request(context, execution, round_number, task, previous):
    inputs = snapshot(context, execution)
    target = {key: execution[key] for key in ('feature', 'task_id', 'task_item', 'execution_id', 'request_id', 'plan_ref')}
    target.update(review_round=round_number, input_sha256=store.fingerprint(inputs),
                  config_sha256=store.fingerprint(execution['policy']))
    return {'schema': 1, 'profile': profile_for(execution),
            'target': target, 'inputs': inputs, 'task': task, 'reverify': execution.get('reverify'),
            'required_aspects': ASPECTS, 'previous': previous,
            'instruction': execution.get('quality_instructions', {}).get('instruction', '')}


def profile_for(execution):
    """このタスクの実行のレビューの profile。reverify（3 段の (2)）の子 execution は再検証用。"""
    return REVERIFY_PROFILE if execution.get('reverify') else PROFILE


def verify_request(context, execution, pointer, current=True):
    request = storage.read(context.root, execution['execution_id'], pointer['round'], 'code-request.json')
    target = request['target']
    if (store.fingerprint(request) != pointer['request_sha256'] or request.get('profile') != profile_for(execution)
            or target.get('review_round') != pointer['round'] or request.get('required_aspects') != ASPECTS
            or any(target.get(k) != execution[k] for k in ('feature', 'task_id', 'task_item', 'execution_id', 'request_id', 'plan_ref'))
            or target.get('config_sha256') != store.fingerprint(execution['policy'])
            or target.get('input_sha256') != store.fingerprint(request['inputs'])):
        raise ValueError('task code review request identity or version differs')
    mcp.verify(context.root, request)
    if current and snapshot(context, execution) != request['inputs']:
        raise ValueError('task code review inputs changed; retry and review the current version')
    return request


def validate_result(request, data):
    fields = {'status', 'target', 'request_sha256', 'engine', 'aspects', 'reviewed_paths',
              'unreviewed', 'findings', 'resolved_findings', 'reason', 'mcp'}
    if (not isinstance(data, dict) or set(data) != fields or data.get('target') != request['target']
            or data.get('request_sha256') != store.fingerprint(request)):
        raise ValueError('code review must identify the exact task request')
    engine = data['engine']
    if (not isinstance(engine, dict) or set(engine) != {'provider', 'tool', 'version'}
            or any(not isinstance(v, str) or not v.strip() for v in engine.values())
            or engine['provider'] != 'host'):
        raise ValueError('task review needs its actual host engine identity')
    for key in ('aspects', 'reviewed_paths', 'unreviewed', 'findings', 'resolved_findings'):
        if not isinstance(data[key], list):
            raise ValueError('review ' + key + ' must be an array')
    failed = data['status'] == 'failed'
    if failed:
        if not isinstance(data['reason'], str) or not data['reason'].strip():
            raise ValueError('failed task review needs its actual reason')
    elif data['status'] != 'completed' or data['reason'] != '' or data['aspects'] != ASPECTS:
        raise ValueError('completed task review requires every declared aspect')
    required = set(request['inputs']['code']) | set(request['inputs']['deleted']) | set(request['inputs']['upstream']) | set(request['inputs']['checks'])
    if (any(not isinstance(p, str) for p in data['reviewed_paths'])
            or len(data['reviewed_paths']) != len(set(data['reviewed_paths']))
            or not set(data['reviewed_paths']) <= required
            or any(not isinstance(p, str) or not p.strip() for p in data['unreviewed'])
            or any(a not in ASPECTS for a in data['aspects'])
            or (not failed and (set(data['reviewed_paths']) != required or data['unreviewed']))):
        raise ValueError('required task review inputs must all be reviewed; missing scope cannot pass')
    ids = set()
    for row in data['findings']:
        if not isinstance(row, dict) or set(row) != {'id', 'aspect', 'severity', 'location', 'summary', 'evidence', 'suggestion'}:
            raise ValueError('invalid task finding')
        if any(not isinstance(v, str) or not v.strip() for v in row.values()):
            raise ValueError('finding values must be nonblank text')
        store.identifier(row['id'])
        if row['id'].startswith('ACE-') or row['id'] in ids or row['aspect'] not in ASPECTS or row['severity'] not in ('critical', 'major', 'minor', 'info'):
            raise ValueError('unknown or duplicate task finding')
        ids.add(row['id'])
    acknowledged = data['mcp']
    expected_mcp = request['mcp']
    if (not isinstance(acknowledged, dict) or set(acknowledged) != {'reference', 'assessments'}
            or acknowledged['reference'] != expected_mcp['reference']
            or not isinstance(acknowledged['assessments'], list)):
        raise ValueError('host must acknowledge the exact MCP evidence reference')
    ace_ids = {row['id'] for row in expected_mcp['findings']}
    seen = set()
    for row in acknowledged['assessments']:
        if (not isinstance(row, dict) or set(row) != {'id', 'evidence', 'duplicate_of'}
                or not isinstance(row['id'], str) or row['id'] not in ace_ids or row['id'] in seen
                or not isinstance(row['evidence'], str) or not row['evidence'].strip()
                or (row['duplicate_of'] is not None and (not isinstance(row['duplicate_of'], str) or row['duplicate_of'] not in ids))):
            raise ValueError('each MCP finding requires evidence and a valid optional host duplicate')
        seen.add(row['id'])
    if seen != ace_ids or expected_mcp['status'] not in ('completed', 'not_applicable'):
        raise ValueError('MCP inspection/acknowledgement is incomplete; retry before host review')
    previous = (request.get('previous') or {}).get('findings', [])
    old = {row['id'] for row in previous}
    resolved = set()
    for row in data['resolved_findings']:
        if (not isinstance(row, dict) or set(row) != {'id', 'evidence'} or row.get('id') not in old
                or row['id'] in resolved or not isinstance(row.get('evidence'), str) or not row['evidence'].strip()):
            raise ValueError('resolution requires an actual previous finding and evidence')
        old_row = next(f for f in previous if f['id'] == row['id'])
        if row['id'].startswith('ACE-'):
            path = old_row['source']['path']
            if row['id'] in ace_ids or (path not in expected_mcp['reviewed'] and path not in request['inputs']['deleted']):
                raise ValueError('ACE resolution requires a new completed inspection of that file or its deletion')
        resolved.add(row['id'])
    if resolved & (ids | ace_ids) or (not failed and old - ids - ace_ids - resolved):
        raise ValueError('every previous finding must remain open or have review evidence of resolution')
    return copy.deepcopy(data)


def integrate(request, host):
    result = validate_result(request, host)
    result['findings'] = [{**row, 'source': {'provider': 'host', 'id': row['id']}} for row in result['findings']]
    assessments = {row['id']: row for row in host['mcp']['assessments']}
    for finding in request['mcp']['findings']:
        row = copy.deepcopy(finding)
        severities = ['info', 'minor', 'major', 'critical']
        previous = next((f for f in (request.get('previous') or {}).get('findings', []) if f['id'] == row['id']), None)
        if previous and severities.index(previous['severity']) > severities.index(row['severity']):
            row['severity'] = previous['severity']
        row['duplicate_of'] = assessments[row['id']]['duplicate_of']
        row['host_evidence'] = assessments[row['id']]['evidence']
        result['findings'].append(row)
    return result


def load(context, execution, pointer, current=True):
    request = verify_request(context, execution, pointer, current)
    manifest = storage.read(context.root, execution['execution_id'], pointer['round'], 'code-manifest.json')
    if manifest.get('schema') != 1 or set(manifest.get('files', {})) != {'code-request.json', 'code-review.json', 'code-summary.md'}:
        raise ValueError('invalid task code review manifest')
    for name, digest in manifest['files'].items():
        if store.digest(storage.path(context.root, execution['execution_id'], pointer['round'], name).read_bytes()) != digest:
            raise ValueError('task code review artifact changed: ' + name)
    receipt = storage.read(context.root, execution['execution_id'], pointer['round'], 'code-review.json')
    if (set(receipt) != {'schema', 'request_sha256', 'host_review', 'review', 'reused_from'} or receipt.get('schema') != 1
            or receipt.get('request_sha256') != pointer['request_sha256']):
        raise ValueError('code review receipt belongs to another request')
    source = receipt.get('reused_from')
    if source:
        if type(source.get('round')) is not int or not 0 < source['round'] < pointer['round']:
            raise ValueError('reuse must reference an earlier round of the same execution')
        old_request, old_receipt = load(context, execution, source, current=False)
        if (receipt['review'] != old_receipt['review'] or receipt['host_review'] != old_receipt['host_review']
                or old_request['mcp'] != request['mcp'] or old_request['inputs'] != request['inputs']
                or old_receipt['review']['status'] != 'completed'):
            raise ValueError('reused task review inputs or receipt differ')
    else:
        if integrate(request, receipt['host_review']) != receipt['review']:
            raise ValueError('integrated review differs from host and ACE evidence')
    if storage.path(context.root, execution['execution_id'], pointer['round'], 'code-summary.md').read_bytes().decode('utf-8') != summary(request, receipt):
        raise ValueError('task code review summary differs')
    return request, receipt


def approve(receipt, data):
    review = receipt['review']
    if review['status'] != 'completed':
        raise ValueError('unfinished task review cannot be approved')
    if any(row['severity'] in ('critical', 'major') for row in review['findings']):
        raise ValueError('blocking task findings require repair and a new review')
    dispositions = data.get('dispositions', {})
    if not isinstance(dispositions, dict) or set(dispositions) != {row['id'] for row in review['findings']}:
        raise ValueError('every nonblocking finding requires an actual human disposition')
    for row in dispositions.values():
        if (not isinstance(row, dict) or set(row) != {'decision', 'reason'} or row['decision'] != 'accept'
                or not isinstance(row['reason'], str) or not row['reason'].strip()):
            raise ValueError('finding acceptance requires its actual reason')


def summary(request, receipt):
    review = receipt['review']
    lines = ['# タスクのコードとテストのレビュー', '', '対象タスク: ' + request['target']['task_id'],
             '', '実施状態: ' + review['status'], 'MCPによる外部レビュー: ' + request['mcp']['status'], request['mcp']['reason'], '']
    if receipt.get('reused_from'):
        lines += ['同じ入力版の保存済みレビューを再利用しています。', '']
    import unit_test_specification as specification
    lines += ['host: ' + specification._literal(json.dumps(receipt['host_review']['engine'], ensure_ascii=False, sort_keys=True)),
              'MCP証跡: review round ' + str(request['mcp']['reference']['round']),
              'MCP確認ファイル: ' + str(len(request['mcp']['reviewed'])), '']
    for engine in request['mcp']['engine']:
        lines += ['ACE: ' + specification._literal(json.dumps(engine, ensure_ascii=False, sort_keys=True)), '']
    if review['status'] == 'failed':
        lines += ['検査未完了: ' + specification._literal(review['reason']), '']
        lines += ['未確認: ' + specification._literal(row) for row in review['unreviewed']]
    for row in review['findings']:
        lines.append('- 出典: ' + row['source']['provider'] + (' / 対応するhost指摘: ' + row['duplicate_of'] if row.get('duplicate_of') else ''))
        lines.append('- ' + specification._literal(' / '.join(row[k] for k in ('id', 'severity', 'location', 'summary', 'evidence', 'suggestion'))))
        if row.get('host_evidence'):
            lines.append('  host確認根拠: ' + specification._literal(row['host_evidence']))
    if not review['findings'] and review['status'] == 'completed':
        lines.append('指摘なし。必要観点の実施と対象版を照合してから続行します。')
    return '\n'.join(lines) + '\n'
