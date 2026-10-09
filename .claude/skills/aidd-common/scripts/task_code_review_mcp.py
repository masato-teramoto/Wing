"""Immutable ACE evidence within the L3-owned task review round."""
import copy
from pathlib import Path

import code_review_mcp as adapter
import implementation_project as project  # ACE の版・索引の鍵の定義は L3 に 1 つだけ置く（§6.11、L4-5）
import implementation_store as store
import task_quality_storage as storage

BASE_NAMES = {'mcp-request.json', 'mcp-response.json', 'mcp-review.json', 'mcp-summary.md'}
RULES = project.ACE_RULES


def version():
    config, sha = adapter.settings()
    return {'settings_sha256': sha, 'config': config,
            'rules': {name: store.digest(Path(__file__).with_name(name).read_bytes()) for name in RULES}}


def record_index(root, result, reference):
    """受け付けて応答を得たファイルを (path, sha256, 版) の索引に足す（execution をまたぐ再利用：M-06・M-08）。"""
    version = project.ace_version()
    for path in result['reviewed']:
        target = project.index_path(path)
        try:
            value = store.read(root, target)
        except (OSError, ValueError):
            value = {'schema': 1, 'path': path, 'entries': []}
        entry = {'sha256': result['files'][path], 'version': version, 'status': 'completed', 'reference': reference,
                 'findings': [f for f in result['findings'] if f['source']['path'] == path]}
        if not any(row['sha256'] == entry['sha256'] and row['version'] == version for row in value['entries']):
            value['entries'].append(entry)
            store.write(root, target, value)


def file_name(path):
    return 'mcp-file-' + store.digest(path.encode('utf-8'))[:32] + '.json'


def make_request(request, execution):
    inputs = request['inputs']
    files = {p: sha for p, sha in inputs['code'].items() if p in inputs['changed_paths']}
    non_code = not execution['policy']['tasks'][execution['task_id']]['tdd']
    return {'schema': 1, 'target': request['target'], 'version': inputs['mcp_version'],
            'files': {} if non_code else files,
            'not_applicable_reason': execution['policy']['tasks'][execution['task_id']].get('non_code_reason', '') if non_code
                else ('生成・修正の追加変更ファイルなし（削除・依存の影響はhostで確認）' if not files else '')}


def eligibility(request, texts):
    entries, skipped = [], []
    for path, sha in sorted(request['files'].items()):
        content = texts[path]
        if content is None:
            skipped.append({'path': path, 'reason': 'not UTF-8 text'})
            continue
        raw = content.encode('utf-8')
        if store.digest(raw) != sha:
            raise ValueError('MCP input bytes differ from the frozen file: ' + path)
        reason = ''
        if Path(path).suffix.lower() not in request['version']['config']['extensions']:
            reason = 'unsupported extension'
        elif len(Path(path).name) > 255:
            reason = 'filename exceeds 255 characters'
        elif len(raw) > adapter.MAX_BYTES:
            reason = 'content exceeds 512000 bytes'
        elif not content.strip():
            reason = 'empty/whitespace content is unsupported by ACE'
        if reason:
            skipped.append({'path': path, 'reason': reason})
        else:
            entries.append((path, content, sha))
    return entries, skipped


def normalized(request, responses, skipped):
    findings, incomplete, engines, reviewed = [], list(skipped), [], []
    for path, record in sorted(responses.items()):
        if record['path'] != path or record['sha256'] != request['files'][path]:
            raise ValueError('MCP response identity differs')
        if record['engine'] and record['engine'] not in engines:
            engines.append(record['engine'])
        if record['error']:
            incomplete.append({'path': path, **record['error']})
            continue
        calls = [event['reply'].get('result') for event in record['trace'] if event['method'] == 'tools/call']
        try:
            if len(calls) != 1 or not isinstance(calls[0], dict):
                raise adapter.ReviewError('protocol', 'no unique ACE tool response')
            data = adapter.tool_data(calls[0], Path(path).name)
            found, missing = adapter.normalize(path, data, request['version']['config'])
            findings.extend(found)
            incomplete.extend(missing)
            if not missing:
                reviewed.append(path)
        except adapter.ReviewError as error:
            incomplete.append({'path': path, 'kind': error.kind, 'reason': str(error)})
    missing = set(request['files']) - set(responses) - {row['path'] for row in skipped}
    incomplete += [{'path': p, 'reason': 'MCP response missing'} for p in sorted(missing)]
    if len(engines) > 1:
        incomplete.append({'reason': 'ACE server/tool identity changed within this review'})
    status = 'failed' if incomplete else ('completed' if request['files'] else 'not_applicable')
    return {'status': status, 'engine': engines, 'files': request['files'], 'reviewed': reviewed,
            'skipped': skipped, 'incomplete': incomplete, 'findings': findings,
            'reason': request['not_applicable_reason']}


def summary(result):
    return '# MCP静的検査\n\n' + result['status'] + '\n' + result['reason'] + '\n\n' + '\n'.join(
        '- ' + row['path'] + ': ' + row.get('reason', row.get('message', '未完了')) for row in result['incomplete'] if 'path' in row) + '\n'


def load(root, reference):
    execution_id, number = reference['execution_id'], reference['round']
    manifest = storage.read(root, execution_id, number, 'mcp-manifest.json')
    if manifest.get('schema') != 1 or store.fingerprint(manifest) != reference['manifest_sha256']:
        raise ValueError('MCP evidence manifest changed')
    request = storage.read(root, execution_id, number, 'mcp-request.json')
    result = storage.read(root, execution_id, number, 'mcp-review.json')
    responses = storage.read(root, execution_id, number, 'mcp-response.json')
    expected = BASE_NAMES | {file_name(p) for p in responses}
    if set(manifest.get('files', {})) != expected:
        raise ValueError('MCP manifest has missing or unknown artifacts')
    for name, sha in manifest['files'].items():
        if store.digest(storage.path(root, execution_id, number, name).read_bytes()) != sha:
            raise ValueError('MCP evidence artifact changed: ' + name)
    for path, value in responses.items():
        if storage.read(root, execution_id, number, file_name(path)) != value:
            raise ValueError('MCP file checkpoint differs from the final response')
    if (request['target']['execution_id'] != execution_id or request['target']['review_round'] != number
            or normalized(request, responses, result['skipped']) != result
            or storage.path(root, execution_id, number, 'mcp-summary.md').read_text(encoding='utf-8') != summary(result)):
        raise ValueError('MCP result differs from its source evidence')
    return request, result


def context(reference, result):
    return {'reference': reference, **copy.deepcopy(result)}


def verify(root, request):
    value = request['mcp']
    source, result = load(root, value['reference'])
    if (context(value['reference'], result) != value or source['version'] != request['inputs']['mcp_version']
            or source['target']['review_round'] > request['target']['review_round']
            or any(source['target'][k] != v for k, v in request['target'].items() if k != 'review_round')):
        raise ValueError('MCP evidence belongs to different task review inputs')
    return result


def prepare(context_value, execution, request, prior=None):
    root, execution_id, number = context_value.root, execution['execution_id'], request['target']['review_round']
    if prior and prior['inputs'] == request['inputs'] and execution.get('quality_instructions', {}).get('corrections'):
        previous = storage.read(root, execution_id, prior['reference']['round'], 'code-request.json')
        value = previous['mcp']
        verify(root, previous)
        if value['status'] in ('completed', 'not_applicable'):
            return copy.deepcopy(value)
    wanted = make_request(request, execution)
    storage.write_once(root, execution_id, number, 'mcp-request.json', wanted)
    manifest_path = storage.path(root, execution_id, number, 'mcp-manifest.json')
    if manifest_path.exists():
        reference = {'execution_id': execution_id, 'round': number,
                     'manifest_sha256': store.fingerprint(storage.read(root, execution_id, number, 'mcp-manifest.json'))}
        _, result = load(root, reference)
        return context(reference, result)
    entries, skipped = eligibility(wanted, request['inputs']['source_text'])
    saved = {}
    for path, _, sha in entries:
        filename = file_name(path)
        if storage.path(root, execution_id, number, filename).exists():
            value = storage.read(root, execution_id, number, filename)
            if value['path'] != path or value['sha256'] != sha:
                raise ValueError('MCP checkpoint belongs to another input')
            saved[path] = value
    def save(record):
        storage.write_once(root, execution_id, number, file_name(record['path']), record)
    responses = adapter.review_entries(entries, wanted['version']['config'], saved, save)
    result = normalized(wanted, responses, skipped)
    storage.write_once(root, execution_id, number, 'mcp-response.json', responses)
    storage.write_once(root, execution_id, number, 'mcp-review.json', result)
    storage.write_once(root, execution_id, number, 'mcp-summary.md', summary(result).encode('utf-8'))
    names = BASE_NAMES | {file_name(p) for p in responses}
    manifest = {'schema': 1, 'files': {name: store.digest(storage.path(root, execution_id, number, name).read_bytes()) for name in sorted(names)}}
    storage.write_once(root, execution_id, number, 'mcp-manifest.json', manifest)
    reference = {'execution_id': execution_id, 'round': number, 'manifest_sha256': store.fingerprint(manifest)}
    record_index(root, result, {'kind': 'task', **reference})
    return context(reference, result)
