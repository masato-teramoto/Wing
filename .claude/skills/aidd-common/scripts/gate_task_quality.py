"""L4 start gates of the Phase 8 task-level reviews (L3 does not import L4; these gates do the L4 part).

| gate | action (hookPoint) | what it does |
|---|---|---|
| `task-quality-policy` | task actions / `implement-gate-run` (start) | Validates the policy's `task_quality` / `task_review` sections |
| `task-code-review-baseline` | task actions (start) | Records the code baseline of the task code review in the execution (once) |
| `task-quality-feature` | `implement-gate-run` (start, before `implementation-input`) | Rechecks every completed task's confirmation and records the generated specifications and task review entries for the feature report |
"""
import l0  # noqa: F401
import phase_rules
import implementation_flows
import implementation_requests as requests
import implementation_store as store
import implementation_code_review as code_review
import implementation_task_review as task_review
import task_code_review
import task_quality
import task_quality_inputs
import task_quality_storage


def policy(context):
    if requests.kind(context) == 'final':
        value = requests.feature_state(context, context.item)['policy']
    else:
        value = store.read_execution(context)['policy']
    task_quality_inputs.validate_policy(value)
    task_code_review.validate_policy(value)


def baseline(context):
    execution = store.read_execution(context)
    if 'review_baseline' in execution:
        return
    execution['review_baseline'] = task_code_review.baseline(context, execution)
    store.write(context.root, store.execution_path(execution['execution_id']), execution)


def feature(context):
    state = requests.feature_state(context, context.item)
    entries = []
    for task_id, proof in sorted(state['completed'].items()):
        execution = store.read(context.root, store.execution_path(proof['execution_id']))
        task_review.require_accepted(context, execution, current=False)
        if code_review.enabled(execution):
            request, _ = code_review.receipt(context, execution, current=False)
            path = task_quality_storage.directory(execution['execution_id'], execution['code_review']['round']) + '/code-summary.md'
            entries.append({'label': 'タスク ' + task_id + ' の統合レビュー', 'path': path, 'note': 'MCP: ' + request['mcp']['status']})
        else:
            entries.append({'label': 'タスク ' + task_id + ': MCP非適用（タスクレビュー未設定または理由付き免除）'})
    generated = task_quality.latest_for_feature(context, state) if state['policy'].get('task_quality') else []
    state['report_extensions'] = {'generated_specifications': generated, 'task_reviews': entries}
    store.write(context.root, requests.feature_path(context.item), state)


GATES = {'task-quality-policy': policy, 'task-code-review-baseline': baseline, 'task-quality-feature': feature}


if __name__ == '__main__':
    try:
        context = phase_rules.gate_context()
        implementation_flows.guard(context)
        GATES[context.gate](context)
    except (ValueError, OSError, KeyError, TypeError) as error:
        phase_rules.fail(str(error))
    phase_rules.ok('task quality gate completed')
