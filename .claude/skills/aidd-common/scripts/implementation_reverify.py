"""再検証と再固定（計画 v3 §6.5、§6.10 C3、R4）。

`classify` は `implement-reverify` の 3 段の機械判定（仕分けだけ）。`reverify` が仕分けに従って状態を進め、
(2) の親要求 kind `reverify` を作る。`repin` は定義・`.claude` 資材の改訂の再固定（下の「再固定」）。

実装承認済み feature の完了タスクを、保存済みの証跡（`review.json`・各タスクの execution）と現在の値の比較だけで
次の 3 段に仕分ける。推定はしない。
(1) 自 feature の requirements／design／tasks が変わった → 再生成。
(2) 自 feature の仕様は不変だが、共有資材が変わった → 検証コマンドと L4 の reverify 用レビューを再実行（段階 3）。
    共有資材：依存先 D の仕様・実装承認、docs の固定版（C2 で影響あり）、検証計画、steering／Templates、
    宣言（allowed_paths 以外の verification_paths・review_paths・task_quality の shared_paths）に入る共有ファイル。
    steering／Templates の変更はその feature の全タスクを (2) にする（宣言と結び付かないため。(3) に落とさない）。
(3) どちらも不変 → 証跡の再照合だけで維持。
例外：自 feature の仕様が不変なのにタスクの allowed_paths の中が変わっていたら、reverify ではなく改変（repair 要求）。
"""
import l0  # noqa: F401  L0 の枠組みを import できるようにする
from pathlib import Path

import yamlmini

import phase_rules
import project_state
import implementation_evidence as evidence
import implementation_flows as flows
import implementation_requests as requests
import implementation_store as store
import task_runtime

DECLARATIONS = ('rule-changes-l0.yaml', 'rule-changes-l3.yaml', 'rule-changes.yaml')
RETRO_FREE = '遡及不要'
RECHECK = '再検査要'
CLASSES = (RETRO_FREE, RECHECK)
DEFINITIONS = tuple('.claude/skills/aidd-common/' + name for name in ('command.yaml', 'flow.yaml', 'action.yaml', 'gate.yaml'))


def _changed(before, after):
    return sorted(p for p in set(before) | set(after) if before.get(p) != after.get(p))


def _declared(policy, key):
    task = policy["tasks"][key]
    paths = list(task.get("review_paths") or []) + list(policy.get("verification_paths") or [])
    for suite in ((policy.get("task_quality") or {}).get("suites") or {}).values():
        paths += list(suite.get("shared_paths") or [])
    return paths


def classify(context, feature):
    review = store.read(context.root, evidence.review_path(feature))
    state = requests.feature_state(context, feature)
    saved, current = review["inputs"], requests.input_signature(context, feature)
    own = "specs/%s/" % feature
    own_changed = [p for p in _changed(saved, current) if p.startswith(own)]
    if review["tasks_current_sha256"] != evidence.tasks_current(context, feature, state.get("review_digest_version")):
        own_changed.append(own + "tasks.md")
    shared = []
    for path in _changed(saved, current):
        if path.startswith(own):
            continue
        if path == "docs_revision":
            import docs_revision
            if not docs_revision.equivalent(context, feature, saved.get(path), current.get(path)):
                shared.append("docs の固定版（C2 で影響あり）")
        elif path == evidence.config_path(feature):
            shared.append("検証計画 " + path)
        elif path.startswith("approval:") or path.startswith("specs/"):
            shared.append("依存先 " + path.replace("approval:", ""))
        else:
            shared.append(path)
    protected_now = (evidence.review_protected(context, feature) if state.get("review_digest_version") == evidence.REVIEW_DIGEST_VERSION
                     else evidence.inventory(context, state["policy"], protected=True))
    rule_assets = [p for p in _changed(review["protected"], protected_now) if p.split("/")[0] in ("steering", "Templates")]
    claude_assets = [p for p in _changed(review["protected"], protected_now) if p.startswith(".claude/")]
    code_now = evidence.inventory(context, state["policy"])
    result = {}
    for key, proof in sorted(state["completed"].items()):
        execution = store.read(context.root, store.execution_path(proof["execution_id"]))
        reasons, cls = [], 3
        if own_changed:
            cls, reasons = 1, ["自 feature の仕様が変わった: " + ", ".join(sorted(set(own_changed)))]
        else:
            moved = _changed(execution["baseline"], code_now)
            inside = [p for p in moved if any(evidence.matches(p, s) for s in execution["allowed_paths"])
                      and review["code"].get(p) != code_now.get(p)]
            if inside:
                result[key] = {"class": "repair", "reasons": ["承認後に Boundary 内のファイルが変わった（改変。repair 要求へ）: "
                                                              + ", ".join(inside)]}
                continue
            declared = [p for p in moved if not any(evidence.matches(p, s) for s in execution["allowed_paths"])
                        and any(evidence.matches(p, s) for s in _declared(state["policy"], key))]
            reasons += shared + (["steering／Templates が変わった: " + ", ".join(rule_assets)] if rule_assets else [])
            reasons += (["フロー資材（.claude）が変わった（遡及区分の宣言で判定。宣言なしは再検査）: " + ", ".join(claude_assets)]
                        if claude_assets else [])
            reasons += (["宣言された共有ファイルが変わった: " + ", ".join(declared)] if declared else [])
            cls = 2 if reasons else 3
        result[key] = {"class": cls, "reasons": reasons}
    redo = any(v["class"] in (1, 2, "repair") for v in result.values())
    return {"feature": feature, "tasks": result, "final": "redo" if redo else "keep"}


def _workflow(context):
    value = context.state().get('workflow', {})
    return value if isinstance(value, dict) else {}


def _save_workflow(context, **values):
    current = dict(_workflow(context))
    current.update(values)
    project_state.update(context.state_path, {'workflow': current})


# --- 遡及区分の宣言 ----------------------------------------------------------

def declarations():
    """L0・L3・L4 が配布する遡及区分の宣言（各項目：path・from・to・class）。gate.yaml は対象外（4 定義ファイルの規則で判定）。"""
    rows = []
    for name in DECLARATIONS:
        path = phase_rules.COMMON / name
        if not path.is_file():
            continue
        value = yamlmini.load(path.read_text(encoding='utf-8')) or {}
        for row in value.get('changes') or []:
            if not isinstance(row, dict) or row.get('class') not in CLASSES or not all(row.get(k) for k in ('path', 'from', 'to')):
                raise ValueError('遡及区分の宣言の形式が不正です: %s' % name)
            if row['path'] in DEFINITIONS:
                raise ValueError('4 定義ファイルは遡及区分の宣言の対象にしません: %s' % row['path'])
            rows.append(dict(row, source=name))
    return rows


def classify_change(path, before, after, rows=None):
    """差分 (before → after) の区分。宣言の連鎖が前後の hash でつながるときだけ適用し、つながらなければ宣言なし（再検査要）。"""
    rows = declarations() if rows is None else rows
    current, used = before, []
    for _ in range(len(rows) + 1):
        if current == after:
            break
        step = next((r for r in rows if r['path'] == path and r['from'] == current), None)
        if step is None:
            return RECHECK, []
        used.append(step)
        current = step['to']
    if current != after:
        return RECHECK, []
    return (RECHECK if any(r['class'] == RECHECK for r in used) else RETRO_FREE), used


# --- Phase 8 の定義の digest ---------------------------------------------------

def definitions_digest(context):
    """Phase 8 に関わる定義（implement-* の action、implement flow、implement-* に差さる gate の行）の digest。"""
    import engine_client
    data = engine_client.validate(context)
    actions = sorted((row for row in data['events'] if row['name'].startswith('implement-')), key=lambda r: r['name'])
    names = {row['name'] for row in actions}
    flows_rows = sorted((row for row in data['flows'] if set(row.get('order') or []) & names), key=lambda r: r['name'])
    gates = sorted((row for row in data['gates'] if str(row.get('target_event', '')).startswith('implement-')),
                   key=lambda r: (r['target_event'], r['hookPoint'], r['name']))
    return store.fingerprint({'actions': actions, 'flows': flows_rows, 'gates': gates})


# --- 再固定 implement-repin -----------------------------------------------------

def _quiescent(context):
    if (context.state().get('current') or {}).get('pending'):
        raise ValueError('待ち中の dispatch があります。静止境界（pending 無し・未完了の execution 無し）で行います')
    for path in Path(context.path(store.BASE + '/runs')).glob('*/execution.json'):
        execution = store.read(context.root, path.relative_to(context.root).as_posix())
        if execution.get('activated') and not execution.get('event_complete'):
            raise ValueError('未完了のタスクがあります: %s %s' % (execution.get('feature'), execution.get('task_id')))


def _feature_states(context):
    for path in sorted(Path(context.path(store.BASE + '/features')).glob('*/state.json')):
        yield path.parent.name, requests.feature_state(context, path.parent.name)


def repin(context, payload, actor):
    """定義変更時の契約再固定（人の明示操作 `{operation_id, reason}`）。何も書き換えず、追記の記録で同値とみなす。"""
    import review_decisions
    review_decisions.person(actor)
    operation = store.identifier(payload.get('operation_id'))
    if not str(payload.get('reason') or '').strip():
        raise ValueError('implement-repin には理由が要ります')
    records = list(_workflow(context).get('implementation_repins') or [])
    previous = next((r for r in records if r['operation_id'] == operation), None)
    if previous:
        return previous
    _quiescent(context)
    current = flows.configuration(context)
    digest = definitions_digest(context)
    rows = declarations()
    changed, sources = {}, set()
    for name, state in _feature_states(context):
        saved = state.get('flow_contract') or {}
        if saved.get('calls') != current['calls'] or saved.get('schema') != current['schema']:
            raise ValueError('%s: Phase 8 の flow の対応が変わりました。implement-rebase で扱います' % name)
        if saved.get('config_sha256') != current['config_sha256']:
            if state.get('phase8_definitions') != digest:
                raise ValueError('%s: Phase 8 に関わる定義（implement 系の action・flow・gate）が変わったか、照合値がありません。'
                                 'implement-rebase で扱います' % name)
            sources.add(saved['config_sha256'])
        review = Path(context.path(evidence.review_path(name)))
        if not review.is_file():
            continue
        before = store.read(context.root, evidence.review_path(name))['protected']
        after = evidence.review_protected(context, name)
        for path in sorted(set(before) | set(after)):
            if before.get(path) == after.get(path) or not path.startswith('.claude/'):
                continue
            if path in DEFINITIONS:
                entry = {'from': before.get(path), 'to': after.get(path), 'class': RETRO_FREE,
                         'declaration': 'Phase 8 に関わる定義が新旧で同一'}
            else:
                kind, used = classify_change(path, before.get(path), after.get(path), rows)
                entry = {'from': before.get(path), 'to': after.get(path), 'class': kind,
                         'declaration': [{'source': r['source'], 'from': r['from'], 'to': r['to']} for r in used]}
            changed.setdefault(path, entry)
    record = {'operation_id': operation, 'reason': payload['reason'], 'actor': actor, 'at': project_state.now(),
              'from_config_sha256': sorted(sources), 'to_config_sha256': current['config_sha256'],
              'definitions': digest, 'changed_paths': changed,
              'recheck': sorted(p for p, v in changed.items() if v['class'] == RECHECK)}
    records.append(record)
    _save_workflow(context, implementation_repins=records)
    for name, state in _feature_states(context):
        if state.get('phase8_definitions') != digest:
            state['phase8_definitions'] = digest
            store.write(context.root, requests.feature_path(name), state)
    return record


def repinned_contract(context, saved, current):
    """保存した flow 契約と現在が、再固定記録の連鎖でつながるか（calls・schema は同じであること）。"""
    if not saved or saved.get('calls') != current.get('calls') or saved.get('schema') != current.get('schema'):
        return False
    value = saved.get('config_sha256')
    for record in _workflow(context).get('implementation_repins') or []:
        if value in record['from_config_sha256']:
            value = record['to_config_sha256']
    return value == current.get('config_sha256')


def repinned_protected(context, saved, current):
    """保護対象の差が、遡及不要と記録した changed_paths の連鎖だけでつながるか。"""
    if not isinstance(saved, dict) or not isinstance(current, dict):
        return False
    records = _workflow(context).get('implementation_repins') or []
    for path in set(saved) | set(current):
        value = saved.get(path)
        for record in records:
            entry = record['changed_paths'].get(path)
            if entry and entry['class'] == RETRO_FREE and entry['from'] == value:
                value = entry['to']
        if value != current.get(path):
            return False
    return True


# --- 再検証 implement-reverify ---------------------------------------------------

def change_set(context, feature):
    """(2) の子 execution に記録する変更の集合（L4 の reverify 用レビューが読む）。差分本文は持たず前後の digest だけ。

    変わった共有ファイル・依存先の承認行・docs の固定版・steering／Templates・.claude 資材の前後の digest。
    """
    review = store.read(context.root, evidence.review_path(feature))
    state = requests.feature_state(context, feature)
    current = requests.input_signature(context, feature)
    protected = (evidence.review_protected(context, feature) if state.get('review_digest_version') == evidence.REVIEW_DIGEST_VERSION
                 else evidence.inventory(context, state['policy'], protected=True))
    code = evidence.inventory(context, state['policy'])
    shared = {}
    for proof in state['completed'].values():
        execution = store.read(context.root, store.execution_path(proof['execution_id']))
        for path in _changed(execution['baseline'], code):
            if not any(evidence.matches(path, s) for s in execution['allowed_paths']):
                shared[path] = {'from': execution['baseline'].get(path), 'to': code.get(path)}
    return {'inputs': {k: {'from': review['inputs'].get(k), 'to': current.get(k)} for k in _changed(review['inputs'], current)},
            'protected': {k: {'from': review['protected'].get(k), 'to': protected.get(k)}
                          for k in _changed(review['protected'], protected) if not k.startswith('specs/')},
            'code': shared}


def reverify(context, payload, actor):
    """`implement-reverify`（feature の最終検査の文脈、`{operation_id, reason}`）。仕分けに従って状態を進める。

    (1) は completed から外して未完了に戻し（次の implement-select で再生成）、(2) は親要求 kind `reverify` を作る
    （implement-next が子 execution を `implement-authoring-revise` で進める。コード編集 0 件）、(3) は完了証跡を維持する。
    改変（承認後に Boundary 内が変わった）が 1 件でもあれば何もせず repair を求める。
    """
    import review_decisions
    import project_progress
    review_decisions.person(actor)
    if requests.kind(context) != 'final':
        raise ValueError('implement-reverify は feature の最終検査（implement-gate-run[<feature>]）の文脈で呼びます')
    feature = context.item
    operation = store.identifier(payload.get('operation_id'))
    if not str(payload.get('reason') or '').strip():
        raise ValueError('implement-reverify には理由が要ります')
    state = requests.feature_state(context, feature)
    previous = next((e for e in state['history'] if (e.get('reverify') or {}).get('operation_id') == operation), None)
    if previous:
        return previous['assessment']
    _quiescent(context)
    result = classify(context, feature)
    repair = sorted(k for k, v in result['tasks'].items() if v['class'] == 'repair')
    if repair:
        raise ValueError('承認後に Boundary 内のファイルが変わったタスクがあります（改変。repair 要求で扱います）: ' + ', '.join(repair))
    stage = {n: [k for k, v in result['tasks'].items() if v['class'] == n] for n in (1, 2, 3)}
    changes = change_set(context, feature)
    route = flows.configuration(context, validate=True)
    requests.prerequisites(context, feature, starting=False)
    if stage[1]:
        task_runtime.retire(context, feature)  # tasks が変わったので計画を作り直す
    plan = task_runtime.freeze(context, feature)
    policy = evidence.policy(context, feature, plan['tasks'])
    request = {'operation_id': operation, 'reason': payload['reason'], 'actor': actor, 'at': project_state.now()}
    state['history'].append({'reverify': request, 'assessment': result, 'inputs': state['inputs'],
                             'completed': state['completed'], 'plan_ref': state['plan_ref'],
                             'active_request': state.get('active_request')})
    for key in stage[1]:
        task_runtime.update(context, feature, operation + '-regenerate-' + key, {'kind': 'check', 'task_id': key, 'checked': False})
    kept = {}
    for key in stage[3]:
        proof = state['completed'][key]
        if (proof['plan_ref'], proof['policy_hash']) != (plan['plan_ref'], store.fingerprint(policy)):
            # 証跡の再照合で維持（成功印の合成ではなく、どの照合値から引き継いだかを残す）。
            proof = dict(proof, plan_ref=plan['plan_ref'], policy_hash=store.fingerprint(policy),
                         carried={'operation_id': operation, 'plan_ref': proof['plan_ref'], 'policy_hash': proof['policy_hash']})
        kept[key] = proof
    previous_proofs = {key: state['completed'][key] for key in stage[2]}
    state.update(inputs=requests.input_signature(context, feature), plan_ref=plan['plan_ref'], policy=policy,
                 flow_contract=route, completed=kept, invalidated=False, active_request=None,
                 live_code=evidence.feature_inventory(context, policy))
    request_id = None
    if stage[2]:
        request_id = store.identifier(payload.get('request_id') or ('reverify-' + operation)[:96])
        parent = {'schema': 1, 'request_id': request_id, 'feature': feature, 'kind': 'reverify', 'flow_contract': route,
                  'selection': payload, 'actor': actor, 'status': 'active', 'children': {},
                  'task_ids': [key for key in plan['order'] if key in stage[2]], 'plan_ref': plan['plan_ref'],
                  'inputs': state['inputs'], 'policy': policy, 'previous': previous_proofs, 'changes': changes}
        store.write(context.root, store.request_path(request_id), parent)
        state['active_request'] = request_id
    store.write(context.root, requests.feature_path(feature), state)
    if stage[1] or stage[2]:
        project_progress.redo(context, requests.FINAL, feature)
    else:
        # 全タスクが (3)：承認を維持し、照合値の対応（旧 → 新）を記録する（review.json は書き換えない）。
        review = store.read(context.root, evidence.review_path(feature))
        pairs = dict(_workflow(context).get('input_equivalences') or {})
        pairs.setdefault(feature, []).extend([
            {'from': review['inputs'], 'to': state['inputs'], 'operation_id': operation},
            {'from': review['protected'], 'to': evidence.review_protected(context, feature), 'operation_id': operation}])
        _save_workflow(context, input_equivalences=pairs)
    return dict(result, stages=stage, request_id=request_id,
                next_action=('implement-next で (2) の再検証を進めます（コード編集なし）' if stage[2] else
                             'implement-select で (1) のタスクを再生成します' if stage[1] else
                             '全タスクが (3) です。実装承認を維持しました'))
