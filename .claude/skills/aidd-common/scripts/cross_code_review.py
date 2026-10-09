"""execution に依存しない ACE（横断 ACE。計画 v3 §6.11、L4 修正計画 L4-5）。

L3 の ACE 計画のチャンク（`implementation_project.ace_chunk`）のファイルを ACE に送る。送受信・正規化は
タスクの ACE と同じ（code_review_mcp・task_code_review_mcp）。保存先と回の採番だけがチャンク用になる：
- 保存先：`cross-ace/<chunk>/<round>/`（タスクの `runs/<execution_id>/reviews/<round>/` と分ける）
- 回：前の回の mcp-manifest が passed 以外なら次の回、mcp-manifest が無い（中断）なら同じ回で再開する
結果 `cross-ace/<chunk>/result.json` の status（L3 が読んで分割・送り直しを決める）：
- passed：全ファイルの応答を得た（指摘はそのまま。合否は出さない）
- split：全体の予算切れ ／ resend：無応答・接続不可 ／ stop：認証・形式・HTTP 4xx・印の無い skipped・未知
  混在したときは stop → resend → split の順に強いものを採る。
どのタスクも触っていない既存コードのうち ACE が受け付けないものは excluded（理由付き）にし、失敗にしない。
"""
from pathlib import Path

import code_review_mcp as adapter
import implementation_store as store
import implementation_project as project
import task_code_review_mcp as task_mcp

NAMES = ('mcp-request.json', 'mcp-response.json', 'mcp-review.json')


def _round(context, base):
    number = 1
    while Path(context.path('%s/%d/mcp-manifest.json' % (base, number))).is_file():
        if store.read(context.root, '%s/%d/mcp-manifest.json' % (base, number)).get('status') == 'passed':
            return number
        number += 1
    return number


def classify(incomplete):
    found = set()
    for row in incomplete:
        kind, message = row.get('kind'), row.get('message') or row.get('reason') or ''
        if kind == 'timeout' and 'budget' in message:
            found.add('split')
        elif kind in ('timeout', 'connection'):
            found.add('resend')
        else:
            found.add('stop')
    for status in ('stop', 'resend', 'split'):
        if status in found:
            return status
    return 'passed'


def review(context):
    chunk = project.ace_chunk(context)
    version = project.ace_version()
    if version != chunk['version']:
        raise ValueError('ACE の版が ACE 計画と違います。implement-integration-run[smoke] から計画を作り直します')
    base = chunk['directory']
    number = _round(context, base)
    directory = '%s/%d' % (base, number)
    manifest = directory + '/mcp-manifest.json'
    if Path(context.path(manifest)).is_file():
        return store.read(context.root, project.chunk_result_path(chunk['chunk']))
    texts = {}
    for path in chunk['files']:
        raw = Path(context.path(path)).read_bytes()
        try:
            texts[path] = raw.decode('utf-8')
        except UnicodeDecodeError:
            texts[path] = None
    request = {'files': {p: v['sha256'] for p, v in chunk['files'].items()}, 'version': task_mcp.version(),
               'not_applicable_reason': ''}
    entries, skipped = task_mcp.eligibility(request, texts)
    excluded = [row for row in skipped if chunk['files'][row['path']]['untouched']]
    sent = dict(request, files={p: s for p, s in request['files'].items() if p not in {r['path'] for r in excluded}})
    store.write(context.root, directory + '/mcp-request.json', sent)
    saved = {}
    for path, _, sha in entries:
        name = directory + '/' + task_mcp.file_name(path)
        if Path(context.path(name)).is_file():
            value = store.read(context.root, name)
            if value['path'] != path or value['sha256'] != sha:
                raise ValueError('ACE checkpoint belongs to another input: ' + path)
            saved[path] = value

    def save(record):
        store.write(context.root, directory + '/' + task_mcp.file_name(record['path']), record)

    responses = adapter.review_entries(entries, request['version']['config'], saved, save)
    result = task_mcp.normalized(sent, responses, [row for row in skipped if row not in excluded])
    status = classify(result['incomplete']) if result['incomplete'] else 'passed'
    store.write(context.root, directory + '/mcp-response.json', responses)
    store.write(context.root, directory + '/mcp-review.json', result)
    reference = {'kind': 'cross', 'chunk': chunk['chunk'], 'round': number}
    if status == 'passed':
        task_mcp.record_index(context.root, result, reference)
    value = {'schema': 1, 'chunk': chunk['chunk'], 'round': number, 'status': status, 'version': chunk['version'],
             'files': request['files'], 'excluded': excluded, 'incomplete': result['incomplete'],
             'reviewed': result['reviewed'], 'findings': result['findings'], 'engine': result['engine']}
    store.write(context.root, project.chunk_result_path(chunk['chunk']), value)
    names = list(NAMES) + [task_mcp.file_name(p) for p in responses]
    store.write(context.root, manifest, {'schema': 1, 'status': status, 'files': {
        name: store.digest(Path(context.path(directory + '/' + name)).read_bytes()) for name in sorted(names)}})
    return value
