"""L3 verification envelopes around L4 technical results."""
import l0  # noqa: F401  L0 の枠組みを import できるようにする
from pathlib import Path
import json
import os
import uuid

import implementation_evidence as evidence
import implementation_requests as requests
import implementation_store as store
import implementation_tools
import implementation_reports
import project_state
import snapshot_artifacts


def task(context, payload):
    store.require_execution(context, payload)
    execution = requests.preflight(context)
    if execution.get('event_complete'):
        raise ValueError('completed task receipts are immutable; use a new authorized execution')
    stage = payload.get('stage', 'verify')
    if stage not in ('red', 'green', 'verify'):
        raise ValueError('verification stage must be red, green or verify')
    if stage == 'red' and not payload.get('expected_failure'):
        raise ValueError('RED requires the expected assertion failure and its reason')
    ids = execution['policy']['tasks'][execution['task_id']]['check_ids']
    checks = [c for c in execution['policy']['checks'] if c['id'] in ids]
    before = evidence.check_scope(context, execution)
    directory = store.BASE + '/runs/' + execution['execution_id']
    results = implementation_tools.run_checks(context.root, checks, directory + '/' + stage)
    after = evidence.check_scope(context, execution)
    value = {'schema': 1, 'execution_id': execution['execution_id'], 'task_id': execution['task_id'], 'stage': stage,
             'expected_failure': payload.get('expected_failure'), 'policy_hash': store.fingerprint(execution['policy']),
             'code': before, 'receipts': results, 'completed_at': project_state.now()}
    if after != before:
        value['source_changed'] = True
    store.write(context.root, directory + '/' + stage + '.json', value)
    if after != before:
        raise ValueError('verification modified source files; restore and verify a stable version')
    return value


def final_path(context):
    snapshot = snapshot_artifacts.load(context)
    return store.BASE + '/features/' + context.item + '/inspections/' + str(snapshot['run']) + '/tools.json'


def final(context):
    review = evidence.verify_review(context)
    reporting = review['report_plan']['policy']
    before = evidence.inventory(context, review['policy'])
    target = final_path(context)
    directory = target.rsplit('/', 1)[0]
    bundle = directory + '/reports/summary-' + uuid.uuid4().hex
    specifications = implementation_reports.copy_specifications(context.root, reporting['specifications'], bundle + '/spec')
    results = implementation_tools.run_checks(context.root, review['policy']['checks'], directory)
    report_results = implementation_tools.run_checks(context.root, reporting['checks'], directory + '/reporting', final=True)
    value = {'schema': 1, 'feature': context.item, 'run': snapshot_artifacts.load(context)['run'],
             'snapshot_hash': store.fingerprint(snapshot_artifacts.load(context)),
             'code': review['code'], 'policy_hash': store.fingerprint(review['policy']), 'receipts': results,
             'report_plan_hash': store.fingerprint(review['report_plan']), 'report_receipts': report_results,
             'completed_at': project_state.now(), 'specifications': specifications}
    value['generated_specifications'] = review['report_plan']['generated_specifications']
    if before != evidence.inventory(context, review['policy']):
        value['source_changed'] = True
    summary_path = bundle + '/README.md'
    def link(path):
        return os.path.relpath(path, bundle).replace(os.sep, '/')
    lines = ['# 検証レポート', '', '対象 feature: ' + context.item, '',
             '実行日時: ' + value['completed_at'], '',
             '対象コード・設定・実行条件は末尾の実行証跡を参照。結果の率や件数は合算しない。', '']
    if reporting.get('not_applicable_reason'):
        lines += ['単体テスト・coverageの不適用理由: ' + reporting['not_applicable_reason'], '']
    for spec in specifications:
        lines += ['- [仕様: ' + spec['source'] + '](<' + link(spec['path']) + '>)']
    for spec in value['generated_specifications']:
        lines += ['- [生成済み単体テスト仕様書: ' + spec['scope'] + '](<' + link(spec['path']) + '>)']
    # Task-level review entries are recorded in the feature state by the L4 start gate
    # `task-quality-feature` ({label, path?, note?} per task); L3 renders them as data.
    import implementation_requests
    entries = implementation_requests.feature_state(context, context.item).get('report_extensions', {}).get('task_reviews', [])
    for entry in entries:
        text = ('[' + entry['label'] + '](<' + link(entry['path']) + '>)') if entry.get('path') else entry['label']
        lines += ['', '- ' + text + ('; ' + entry['note'] if entry.get('note') else '')]
    lines += ['', 'feature最終の実テスト・横断検査は本レポートで確認する。']
    for result in results + report_results:
        lines += ['', '## ' + result['check_id'] + ': ' + result['status'], '']
        for entry in result.get('report', {}).get('entries', []):
            path = result['report']['directory'] + '/' + entry['path']
            lines += ['- [' + entry['role'] + '](<' + link(path) + '>); 対象: ' + entry['scope'] + '; ツール: ' + entry['tool']]
            if entry.get('viewing'):
                lines += ['  閲覧方法: ' + entry['viewing']]
        if result.get('diagnostic'):
            lines += ['- [失敗の診断](<' + link(result['diagnostic']['path']) + '>)']
    lines += ['', '## 実行証跡', '', '```json', json.dumps(value, ensure_ascii=False, indent=2), '```', '']
    raw = '\n'.join(lines).encode('utf-8')
    summary_file = implementation_reports.plain_file(context.root, summary_path)
    summary_file.parent.mkdir(parents=True, exist_ok=True)
    summary_file.write_bytes(raw)
    value['summary'] = {'path': summary_path, 'sha256': store.digest(raw)}
    store.write(context.root, target, value)
    try:
        validate_final(context)
    except (ValueError, OSError) as error:
        raise ValueError(str(error) + '; report_summary: ' + summary_path) from error
    return value


def validate_final(context):
    review = evidence.verify_review(context)
    reporting = review['report_plan']['policy']
    value = store.read(context.root, final_path(context))
    if (value.get('source_changed') or value['feature'] != context.item
            or value['snapshot_hash'] != store.fingerprint(snapshot_artifacts.load(context))
            or value['code'] != review['code'] or value['policy_hash'] != store.fingerprint(review['policy'])
            or value.get('report_plan_hash') != store.fingerprint(review['report_plan'])
            or [r['check_id'] for r in value['receipts']] != review['policy']['feature_checks']
            or any(r['status'] != 'passed' for r in value['receipts'])):
        raise ValueError('all mandatory feature checks must finish and pass on the current version')
    if ([r['check_id'] for r in value.get('report_receipts', [])] != [c['id'] for c in reporting['checks']]
            or any(r['status'] != 'passed' for r in value.get('report_receipts', []))):
        raise ValueError('all selected reporting commands and readable outputs must finish and pass')
    implementation_reports.verify_specifications(context.root, reporting['specifications'], value.get('specifications', []))
    if value.get('generated_specifications') != review['report_plan']['generated_specifications']:
        raise ValueError('generated specification references changed; repeat final reporting')
    summary = value.get('summary')
    if not summary or store.digest(implementation_reports.plain_file(context.root, summary['path']).read_bytes()) != summary['sha256']:
        raise ValueError('readable verification summary changed or missing')
    for row in value['receipts']:
        for key in ('stdout', 'stderr'):
            if store.digest(Path(context.path(row[key]['path'])).read_bytes()) != row[key]['sha256']:
                raise ValueError('feature verification log changed or missing')
    for check, row in zip(reporting['checks'], value['report_receipts']):
        implementation_reports.verify(context.root, check, row)
        commands = [row] + row.get('postprocess', [])
        if len(row.get('postprocess', [])) != len(check.get('postprocess', [])) or any(r['status'] != 'passed' for r in commands):
            raise ValueError('required report postprocessing did not finish')
        for command in commands:
            for key in ('stdout', 'stderr'):
                if store.digest(implementation_reports.plain_file(context.root, command[key]['path']).read_bytes()) != command[key]['sha256']:
                    raise ValueError('feature verification log changed or missing')
    return value


def tools_digest(context):
    return store.digest(Path(context.path(final_path(context))).read_bytes())


def semantic_path(context):
    return final_path(context).replace('tools.json', 'semantic.json')


def validate_semantic(context, result):
    snapshot = snapshot_artifacts.load(context)
    if (result.get('scope') != context.scope or type(result.get('run')) is not int or result.get('run') != snapshot['run']
            or type(result.get('findings_count')) is not int or result['findings_count'] < 0
            or result.get('gate_record_path') != context.gate_record
            or result.get('aspects') != evidence.ASPECTS or result.get('layers') != '①②'
            or result.get('tool_results_sha256') != tools_digest(context)):
        raise ValueError('code inspector must return every required aspect for this exact inspection')
    validate_final(context)
    return snapshot


def save_semantic(context, result):
    snapshot = validate_semantic(context, result)
    value = {'schema': 1, 'snapshot_hash': store.fingerprint(snapshot), 'result': result}
    store.write(context.root, semantic_path(context), value)


def complete_inspection(context):
    validate_final(context)
    value = store.read(context.root, semantic_path(context))
    result = value['result']
    import review_contract
    run = review_contract.inspection(context, review_contract.read(context), context.scope)
    if (value['snapshot_hash'] != store.fingerprint(snapshot_artifacts.load(context))
            or result.get('tool_results_sha256') != tools_digest(context)
            or result.get('status') != 'completed' or result.get('aspects') != evidence.ASPECTS
            or result.get('findings_count') != run.count or result.get('layers') != run.layers):
        raise ValueError('independent code inspection is incomplete')
