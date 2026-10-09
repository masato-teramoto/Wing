"""Phase 8 の案件レベル（全 feature の実装承認の後。計画 v3 §6.11）。両方式に適用する。

- 全体結合確認 `implement-integration-run[<group>]`（group は build・smoke）：案件の検証計画 `_project.json` の checks を
  unit 内で実行する（L4 の `implementation-integration-tools` ゲートが `final_project` を呼ぶ）。記録は書かない。
- 横断 ACE `implement-cross-ace-run[<chunk>]`：案件全体のコードのうち、現在の hash の ACE 受領証が無いファイルを
  ACE 計画のチャンクごとに L4 の ACE ゲートへ渡す。記録は書かない。
- 実コードの横断確認 `implement-cross-gate`（item 無し）：上の受領証を束ねた `cross-review.json` を検査・承認する。
  記録は `.aidd/gates/phase-8-implement.md` の `cross` scope。

保存先は feature の名前空間（`features/<feature>/`）と分ける（group 名・チャンク ID は feature 名と同じ形でも衝突しない）：
- `config/_project.json`：`{schema: 1, groups: {build: {checks}, smoke: {checks}}, owner, owner_reason, wrapper, generated_paths}`。
  全 feature の実装承認の後に AI が作る。owner は workflow.smoke_owner から写す。
- `integration/<group>/receipt.json`：group の受領証（案件のコード在庫 digest、`_project.json`・wrapper の hash、checks の結果）。
- `cross-ace/plan.json`：ACE 計画（基底 digest、ACE の版、ファイルと hash・「どのタスクも触っていない」の印、チャンク）。
- `cross-ace/<chunk>/result.json`：L4 の ACE ゲートの結果（passed / split / resend / stop）。
- `cross-review.json`：`implement-cross-gate` の検査対象（束ねた入力）。
"""
import l0  # noqa: F401  L0 の枠組みを import できるようにする
import json
import os
from pathlib import Path
import uuid

import artifacts
import phase_rules
import implementation_evidence as evidence
import implementation_store as store
import project_state

BASE = store.BASE
PROJECT_CONFIG = BASE + '/config/_project.json'
GROUPS = ('build', 'smoke')
INTEGRATION = BASE + '/integration'
ACE = BASE + '/cross-ace'
ACE_PLAN = ACE + '/plan.json'
ACE_INDEX = BASE + '/ace-index'
CROSS_REVIEW = BASE + '/cross-review.json'
INTEGRATION_RUN = 'implement-integration-run'
CROSS_ACE_RUN = 'implement-cross-ace-run'
CROSS_GATE = 'implement-cross-gate'
ACTIONS = (INTEGRATION_RUN, CROSS_ACE_RUN)
# ACE の版の材料：ACE まわりの L4 のコード（L4 の task_code_review_mcp.RULES もこの値を使う。定義はここだけ）。
# L3 は L4 の設定とコードをデータとして読み、import はしない。
ACE_RULES = ('code_review_mcp.py', 'task_code_review_mcp.py', 'task_code_review.py', 'task_quality_storage.py')
# 同じチャンクで続けて送り直す上限（仮）。超えたら停止して人が判断する。
RESEND_LIMIT = 3
NO_OWNER = '候補なし'
OUTCOMES = ('passed', 'split', 'resend', 'stop')


def _exists(context, path):
    return Path(context.path(path)).is_file()


def _digest_file(context, path):
    target = Path(context.path(path))
    return store.digest(target.read_bytes()) if target.is_file() else None


# --- 全 feature の実装承認 ---------------------------------------------------

def unapproved(context):
    """実装承認が現在の照合で通らない feature（一覧順）。"""
    import review_contract
    names = []
    for entry in context.features():
        final = phase_rules.ExecutionContext(context.root, context.state_path, phase_rules.IMPLEMENT_REVIEW, entry['name'])
        try:
            review_contract.check_approved(final)
        except (ValueError, OSError, KeyError):
            names.append(entry['name'])
    return names


def require_all_approved(context):
    names = unapproved(context)
    if names:
        raise ValueError('全 feature の実装承認の後に実行します。未承認: ' + ', '.join(names))


# --- smoke wrapper の owner ---------------------------------------------------

def owner_record(context):
    """owner の正本 `workflow.smoke_owner`（tasks の計画停止点か方式切替の確定で書く。計画了承の外に置くので、
    一覧の構造変更・全件再計画で計画了承を消しても残る）。未設定なら owner は空。

    この版の途中の案件が計画了承・切替記録に持つ owner も読む（後方互換）。
    """
    data = context.state().get('workflow') or {}
    record = data.get('smoke_owner') or {}
    if record.get('owner'):
        return {'owner': record['owner'], 'owner_reason': record.get('owner_reason', '')}
    tasks = (data.get('accepted_plans') or {}).get('tasks') or {}
    for entry in [tasks, *(tasks.get('items') or {}).values()]:
        if entry.get('owner'):
            return {'owner': entry['owner'], 'owner_reason': entry.get('owner_reason', '')}
    switch = data.get('mode_switch') or {}
    if switch.get('owner'):
        return {'owner': switch['owner'], 'owner_reason': switch.get('owner_reason', '')}
    if switch.get('owner_reason'):
        return {'owner': NO_OWNER, 'owner_reason': switch['owner_reason']}
    return {'owner': '', 'owner_reason': ''}


def require_owner(context):
    """owner の候補がいるのに未設定なら止める（旧案件。§6.11「旧案件」）。"""
    import mode_switch
    if not owner_record(context)['owner'] and mode_switch.owner_candidates(context):
        raise ValueError('smoke wrapper の owner が未設定です。/aidd-tasks で tasks-plan の計画停止点を出し直し、'
                         'owner を選んでから Phase 8 を進めます')


# --- 案件の検証計画 _project.json ---------------------------------------------

def project_policy(context):
    """`_project.json` の検査。checks の検査は feature の検証計画と共通（evidence.validate_checks）。"""
    if not _exists(context, PROJECT_CONFIG):
        raise ValueError('案件の検証計画 %s がありません。全 feature の実装承認の後に作ります' % PROJECT_CONFIG)
    value = store.read(context.root, PROJECT_CONFIG)
    if value.get('schema') != 1 or set(value.get('groups') or {}) != set(GROUPS):
        raise ValueError('_project.json は schema 1 と group %s を持ちます' % '・'.join(GROUPS))
    for group in GROUPS:
        evidence.validate_checks(context, (value['groups'][group] or {}).get('checks'))
    require_owner(context)
    record = owner_record(context)
    if (value.get('owner') or '') != record['owner']:
        raise ValueError('_project.json の owner は workflow.smoke_owner（%s）から写します' % (record['owner'] or '未設定'))
    wrapper = value.get('wrapper') or ''
    if record['owner'] and record['owner'] != NO_OWNER:
        if not wrapper:
            raise ValueError('smoke wrapper のパスが必要です（owner %s の結合確認タスク）' % record['owner'])
        artifacts.relative_path(wrapper)
    generated = value.get('generated_paths', [])
    if not isinstance(generated, list) or any(not isinstance(p, str) for p in generated):
        raise ValueError('_project.json の generated_paths は文字列の配列です')
    for path in generated:
        artifacts.relative_path(path.rstrip('/'))
    return value


def project_inventory(context, value):
    """案件全体のコード在庫（どの feature の allowed_paths にも入らない既存コードを含む）。"""
    return evidence.inventory(context, {'generated_paths': value.get('generated_paths', [])})


def config_digest(context):
    return _digest_file(context, PROJECT_CONFIG)


def wrapper_digest(context, value):
    return _digest_file(context, value['wrapper']) if value.get('wrapper') else None


def receipt_path(group):
    return INTEGRATION + '/' + group + '/receipt.json'


def _group(context):
    if context.item not in GROUPS:
        raise ValueError('implement-integration-run の item は group（%s）です: %s' % (' / '.join(GROUPS), context.item or '-'))
    return context.item


def final_project(context):
    """全体結合確認の実行（L4 の `implementation-integration-tools` ゲートが unit 内で呼ぶ）。

    timeout・起動失敗・経路失敗・受領証の欠落は失敗として記録し、成功扱いにしない（MFD/08）。
    起動したサーバーは wrapper が停止し、残れば ProcessTree が強制停止する（implementation_tools）。
    """
    import implementation_tools
    group = _group(context)
    require_all_approved(context)
    value = project_policy(context)
    before = project_inventory(context, value)
    directory = INTEGRATION + '/' + group + '/' + uuid.uuid4().hex
    results = implementation_tools.run_checks(context.root, value['groups'][group]['checks'], directory)
    receipt = {'schema': 1, 'group': group, 'code': store.fingerprint(before), 'config_sha256': config_digest(context),
               'wrapper_sha256': wrapper_digest(context, value), 'owner': value.get('owner', ''),
               'directory': directory, 'receipts': results, 'completed_at': project_state.now()}
    if project_inventory(context, value) != before:
        receipt['source_changed'] = True
    store.write(context.root, receipt_path(group), receipt)
    validate_project(context, group)
    if group == 'smoke':
        ace_plan(context, refresh=True)  # 次の implement-cross-ace-run の item（チャンク ID）が要る（§6.11）
    return receipt


def validate_project(context, group):
    """group の受領証が、現在のコード在庫・`_project.json`・wrapper で合格しているか（失効：§6.11）。"""
    value = project_policy(context)
    if not _exists(context, receipt_path(group)):
        raise ValueError('全体結合確認（%s）が未実施です' % group)
    receipt = store.read(context.root, receipt_path(group))
    expected = [check['id'] for check in value['groups'][group]['checks']]
    if (receipt.get('source_changed') or receipt.get('group') != group
            or receipt.get('code') != store.fingerprint(project_inventory(context, value))
            or receipt.get('config_sha256') != config_digest(context)
            or receipt.get('wrapper_sha256') != wrapper_digest(context, value)
            or [row['check_id'] for row in receipt.get('receipts', [])] != expected
            or any(row['status'] != 'passed' for row in receipt['receipts'])):
        raise ValueError('全体結合確認（%s）が現在のコードと検証計画で合格していません（再実行は同じ action の次の unit）' % group)
    for row in receipt['receipts']:
        for key in ('stdout', 'stderr'):
            if _digest_file(context, row[key]['path']) != row[key]['sha256']:
                raise ValueError('全体結合確認（%s）のログが変わったか欠けています' % group)
    return receipt


# --- 横断 ACE の計画 ----------------------------------------------------------

def ace_settings():
    """L4 の `code_review.json`（データとして読む。L4 のコードは import しない。§6.11 の例外）。"""
    path = os.environ.get('AIDD_CODE_REVIEW_SETTINGS') or str(Path(__file__).with_name('code_review.json'))
    raw = Path(path).read_bytes()
    return json.loads(raw), raw


def ace_version():
    """ACE の版（受領証の索引と ACE 計画の鍵）。受領証を再利用できるのは、ファイルの hash とこの版が一致するときだけ。

    L3 の ACE 計画と L4 の ACE ゲート・索引の書込みは、どちらもこの関数を使う（定義を 1 つにする）。
    同じ配布の間（ACE まわりの L4 のコードと code_review.json が同じ間）だけ受領証を再利用する。
    """
    _, raw = ace_settings()
    parts = [store.digest(raw)] + [store.digest(Path(__file__).with_name(name).read_bytes()) for name in ACE_RULES]
    return store.digest('\n'.join(parts).encode('utf-8'))


def index_path(path):
    return ACE_INDEX + '/' + store.digest(path.encode('utf-8'))[:32] + '.json'


def reviewed(context, path, sha256, version):
    """(path, sha256, mcp_version) の ACE 受領証（L4 が書く索引、L4-5）。無ければ None。"""
    if not _exists(context, index_path(path)):
        return None
    value = store.read(context.root, index_path(path))
    if value.get('path') != path:
        return None
    return next((row for row in value.get('entries', [])
                 if row.get('sha256') == sha256 and row.get('version') == version and row.get('status') == 'completed'), None)


def touched_paths(context):
    """どれかの AIDD タスクが変更・追加・削除したファイル（rebase で退避したものを含む全 execution の和集合）。"""
    found = set()
    for path in Path(context.path(BASE + '/runs')).glob('*/execution.json'):
        execution = store.read(context.root, path.relative_to(context.root).as_posix())
        if execution.get('event_complete'):
            found.update(execution.get('changed_paths') or [])
    return found


def _ace_base(context):
    """計画の基底：ACE の対象拡張子の全コード（path と hash）・ACE の版・チャンクの件数。受領証の有無は含めない
    （チャンクが通って索引が増えても基底は変わらない。コードか版が変われば変わる）。"""
    value = project_policy(context)
    settings, _ = ace_settings()
    version = ace_version()
    extensions = {e.lower() for e in settings['extensions']}
    code = {p: h for p, h in sorted(project_inventory(context, value).items()) if Path(p).suffix.lower() in extensions}
    size = max(1, settings['workers'] * settings['budget_seconds'] // settings['timeout_seconds'])
    base = store.fingerprint({'code': code, 'version': version, 'size': size})
    return {'base': base, 'version': version, 'size': size, 'code': code}


def ace_plan(context, refresh=False):
    """ACE 計画。現在のコードと ACE の版で作った基底が同じなら既存の計画（追記された分割を含む）を返す。"""
    current = _ace_base(context)
    if _exists(context, ACE_PLAN):
        plan = store.read(context.root, ACE_PLAN)
        if plan.get('base') == current['base']:
            return plan
        if not refresh:
            raise ValueError('ACE 計画が古くなりました（コードか ACE の版が変わった）。'
                             'implement-integration-run[smoke] から作り直します')
    touched = touched_paths(context)
    files, reused = {}, {}
    for path, sha in current['code'].items():
        receipt = reviewed(context, path, sha, current['version'])
        if receipt:
            reused[path] = {'sha256': sha, 'reference': receipt.get('reference')}  # 送らず、受領証を参照として示す（M-08）
        else:
            files[path] = {'sha256': sha, 'untouched': path not in touched}
    current.update(files=files, reused=reused)
    names = sorted(files)
    chunks = {}
    for index in range(0, len(names), current['size']):
        key = '%s-%02d' % (current['base'][:8], index // current['size'] + 1)
        chunks[key] = {'files': names[index:index + current['size']], 'parent': None, 'split': False, 'attempts': 0}
    plan = {'schema': 1, 'revision': 1, 'base': current['base'], 'version': current['version'], 'size': current['size'],
            'files': current['files'], 'reused': current['reused'], 'chunks': chunks, 'created_at': project_state.now()}
    store.write(context.root, ACE_PLAN, plan)
    return plan


def leaves(plan):
    """それ以上分けていないチャンク（完了の判定に数えるもの）。"""
    return [key for key, chunk in plan['chunks'].items() if not chunk['split']]


def chunk_result_path(chunk):
    return ACE + '/' + store.identifier(chunk) + '/result.json'


def chunk_result(context, chunk):
    path = chunk_result_path(chunk)
    return store.read(context.root, path) if _exists(context, path) else None


def chunk_passed(context, plan, chunk):
    result = chunk_result(context, chunk)
    return bool(result) and result.get('status') == 'passed' and result.get('version') == plan['version'] and (
        result.get('files') == {p: plan['files'][p]['sha256'] for p in plan['chunks'][chunk]['files']})


def pending_chunks(context, plan):
    return [key for key in leaves(plan) if not chunk_passed(context, plan, key)]


def ace_chunk(context):
    """`implement-cross-ace-run[<chunk>]` の対象（L4 の ACE ゲートが読む）。計画が古ければ止める。"""
    plan = ace_plan(context)
    chunk = plan['chunks'].get(context.item)
    if not chunk:
        raise ValueError('ACE 計画に無いチャンクです: %s' % (context.item or '-'))
    if chunk['split']:
        raise ValueError('分割済みのチャンクです（分割後のチャンクを呼びます）: ' + context.item)
    return {'chunk': context.item, 'version': plan['version'], 'directory': ACE + '/' + context.item,
            'files': {path: plan['files'][path] for path in chunk['files']}, 'attempts': chunk['attempts']}


def after_failure(context, chunk):
    """失敗したチャンクの扱い（L4 の結果ファイルの分類をデータとして読む。人の操作は要らない：R7）。"""
    plan = ace_plan(context)
    result = chunk_result(context, chunk) or {}
    outcome = result.get('status')
    entry = plan['chunks'][chunk]
    if outcome == 'split' and len(entry['files']) > 1:
        half = (len(entry['files']) + 1) // 2
        entry['split'] = True
        for suffix, files in (('-1', entry['files'][:half]), ('-2', entry['files'][half:])):
            plan['chunks'][chunk + suffix] = {'files': files, 'parent': chunk, 'split': False, 'attempts': 0}
        plan['revision'] += 1
        store.write(context.root, ACE_PLAN, plan)
        return {'outcome': 'split', 'chunks': [chunk + '-1', chunk + '-2']}
    if outcome == 'resend' and entry['attempts'] < RESEND_LIMIT:
        entry['attempts'] += 1
        plan['revision'] += 1
        store.write(context.root, ACE_PLAN, plan)
        return {'outcome': 'resend', 'chunks': [chunk]}
    reasons = result.get('incomplete') or [{'reason': '分類できない失敗（%s）' % (outcome or '結果なし')}]
    return {'outcome': 'stop', 'chunks': [], 'reasons': reasons}


def ace_complete(context):
    plan = ace_plan(context)
    remaining = pending_chunks(context, plan)
    if remaining:
        raise ValueError('横断 ACE の未完了のチャンクがあります: ' + ', '.join(remaining))
    return plan


def excluded(context, plan):
    """どのタスクも触っていない既存コードのうち、ACE が受け付けず「ACE 対象外」になったもの（提示・記録用）。"""
    rows = []
    for key in leaves(plan):
        rows += (chunk_result(context, key) or {}).get('excluded', [])
    return rows


def run_proof(context):
    """`implement-integration-run`・`implement-cross-ace-run` の完了の証拠（受領証）。本体の run と同じ判定。"""
    if context.action == INTEGRATION_RUN:
        return validate_project(context, _group(context))
    plan = ace_plan(context)
    if not chunk_passed(context, plan, context.item):
        raise ValueError('横断 ACE のチャンク %s に合格の結果がありません' % context.item)
    return chunk_result(context, context.item)


# --- 前提・記録入力・提示 -----------------------------------------------------

def _docs_final(context):
    """全 feature の docs の固定版が最終の docs_revision と一致（Feature 方式。全件方式は実装承認の照合が現在の docs で通る）。"""
    import feature_scope
    if not feature_scope.is_feature(context):
        return
    import docs_revision
    current = (context.state().get('workflow') or {}).get('docs_revision')
    stale = [e['name'] for e in context.features()
             if not docs_revision.equivalent(context, e['name'], docs_revision.fixed(context, e['name']), current)]
    if stale:
        raise ValueError('docs の固定版が最終の docs_revision と一致しない feature があります（固定版を進めるか 3 段の (2)）: '
                         + ', '.join(stale))


def prerequisites(context):
    """featureless な Phase 8 action の前提（§6.11 の「順序と前提」）。blocker は prerequisites.blockers が全件で見る。"""
    require_all_approved(context)
    if context.action == INTEGRATION_RUN:
        _group(context)
        project_policy(context)
        if context.item == 'smoke':
            validate_project(context, 'build')
        return
    for group in GROUPS:
        validate_project(context, group)
    if context.action == CROSS_ACE_RUN:
        ace_chunk(context)
        return
    if context.item:
        raise ValueError('implement-cross-gate は item を取りません（全件。分割しない）')
    ace_complete(context)
    _docs_final(context)


def signature(context):
    """記録入力（§6.11 の inputs）：全 feature の実装承認行、specs・docs・steering、_project.json・wrapper、受領証、ACE。"""
    import feature_manifest
    import implementation_requests as requests
    values = {feature_manifest.SOURCE: feature_manifest.source_hash(context.root), PROJECT_CONFIG: config_digest(context)}
    for entry in context.features():
        final = phase_rules.ExecutionContext(context.root, context.state_path, phase_rules.IMPLEMENT_REVIEW, entry['name'])
        values['approval:' + evidence.review_path(entry['name'])] = requests.approval_reference(final)
    if context.action == INTEGRATION_RUN:
        return values
    for group in GROUPS:
        values[receipt_path(group)] = _digest_file(context, receipt_path(group))
    values[ACE_PLAN] = _digest_file(context, ACE_PLAN)
    if context.action == CROSS_ACE_RUN:
        return values
    paths = [p.replace('{feature}', e['name']) for e in context.features()
             for p in phase_rules.RULES['tasks']['inputs'] if '{feature}' in p]
    paths += [p for p in phase_rules.RULES['tasks']['inputs'] if '{' not in p and not p.endswith('/')]
    for path in dict.fromkeys(paths):
        values[path] = artifacts.protected_digest(context.path(path)) if Path(context.path(path)).is_file() else None
    plan = store.read(context.root, ACE_PLAN) if _exists(context, ACE_PLAN) else {'chunks': {}}
    for key in leaves(plan) if plan.get('chunks') else []:
        values[chunk_result_path(key)] = _digest_file(context, chunk_result_path(key))
    value = store.read(context.root, PROJECT_CONFIG) if _exists(context, PROJECT_CONFIG) else {}
    values['wrapper'] = wrapper_digest(context, value) if value else None
    values['docs_revision'] = (context.state().get('workflow') or {}).get('docs_revision')
    return values


def prepare_cross_review(context):
    """`implement-cross-gate` の検査対象を書く（preflight。snapshot がこの hash を束ねる）。"""
    plan = ace_plan(context)
    value = {'schema': 1, 'profile': 'implementation-cross-v1', 'inputs': signature(context),
             'features': [e['name'] for e in context.features()],
             'integration': {group: receipt_path(group) for group in GROUPS},
             'ace': {'plan': ACE_PLAN, 'chunks': leaves(plan), 'reused': sorted(plan['reused']),
                     'excluded': excluded(context, plan)},
             'owner': owner_record(context)}
    if not _exists(context, CROSS_REVIEW) or store.read(context.root, CROSS_REVIEW) != value:
        store.write(context.root, CROSS_REVIEW, value)
    return value


def cross_digest(context, target):
    if target != CROSS_REVIEW:
        raise ValueError('wrong cross review target')
    value = store.read(context.root, CROSS_REVIEW)
    if value.get('inputs') != signature(context):
        raise ValueError('実コードの横断確認の入力が検査後に変わりました。再検査が要ります')
    return _digest_file(context, CROSS_REVIEW)


def cross_context(context):
    """check-runner（profile implementation-cross-v1）に渡す文脈。"""
    value = prepare_cross_review(context)
    project = store.read(context.root, PROJECT_CONFIG)
    owner = owner_record(context)
    note = ''
    if owner['owner'] == NO_OWNER:
        note = 'smoke の 1 経路は「起動→readiness 待ち→停止」に縮めた（owner「候補なし」: %s）' % owner['owner_reason']
    return {'profile': 'implementation-cross-v1', 'cross_review_path': CROSS_REVIEW, 'cross_review': value,
            'project_config': project, 'smoke_note': note,
            'reviews': {name: evidence.review_path(name) for name in value['features']}}


def after_run(context, failed):
    """featureless な Phase 8 action の返却（次に呼ぶもの）。繰り返しは入口 Skill が持つ。"""
    if context.action == INTEGRATION_RUN:
        if failed:
            return {'next_action': '全体結合確認（%s）が失敗しました。受領証とログを確認し、コードか _project.json を直してから'
                                   '同じ group を呼び直します（timeout・起動失敗・受領証の欠落は成功扱いにしません）' % context.item}
        if context.item == 'build':
            return {'next_action': 'implement-integration-run[smoke] を呼びます'}
        chunks = pending_chunks(context, ace_plan(context))
        return {'chunks': chunks, 'next_action': (('implement-cross-ace-run を次のチャンクごとに呼びます: ' + ', '.join(chunks))
                                                  if chunks else 'implement-cross-gate を呼びます')}
    if failed:
        decision = after_failure(context, context.item)
        if decision['outcome'] == 'stop':
            lines = ['- %s: %s' % (row.get('path', '-'), row.get('reason') or row.get('message') or '未完了') for row in decision['reasons']]
            return {'ace': decision, 'next_action': '横断 ACE を止めました。ファイルと理由を確認し、後で送り直す・ファイルを直す・'
                                                  'generated_paths に入れるのいずれかを決めます\n' + '\n'.join(lines)}
        return {'ace': decision, 'chunks': decision['chunks'],
                'next_action': 'implement-cross-ace-run を呼びます: ' + ', '.join(decision['chunks'])}
    chunks = pending_chunks(context, ace_plan(context))
    return {'chunks': chunks, 'next_action': (('implement-cross-ace-run を次のチャンクごとに呼びます: ' + ', '.join(chunks))
                                              if chunks else 'implement-cross-gate を呼びます')}


def progress(context):
    """進捗表示（全件横断確認の実コード層）。全チャンク数と完了数、受領証の状態。"""
    view = {'unapproved': unapproved(context), 'integration': {}, 'ace': None}
    if view['unapproved']:
        return view
    for group in GROUPS:
        try:
            validate_project(context, group)
            view['integration'][group] = 'passed'
        except (ValueError, OSError, KeyError) as error:
            view['integration'][group] = str(error)
    if _exists(context, ACE_PLAN):
        plan = store.read(context.root, ACE_PLAN)
        names = leaves(plan)
        view['ace'] = {'chunks': len(names), 'done': len([n for n in names if chunk_passed(context, plan, n)]),
                       'excluded': len(excluded(context, plan))}
    return view
