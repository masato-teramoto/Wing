"""L4 gates for generated test specifications, using existing L3/L0 sequencing.

Each gate decides for itself whether it applies (no `when` in gate.yaml): a gate that does not
apply to this task ends with ok and `省略=該当なし`. Malformed review state is never a skip.

These gates are the only L4 code on the task's agent/human units (L0's GateExecutor runs them):
- `task-specification-prepare` publishes the generation Skill's context, or its skip.
- `task-specification-review` verifies and saves the agent results the host stored, then publishes the wait.
- `task-specification-accept` verifies the human answer the host stored, then accepts.
"""
import json

import l0  # noqa: F401
import phase_rules
import implementation_flows
import implementation_task_completion as task_completion
import implementation_task_review as task_review


def main():
    context = phase_rules.ExecutionContext()
    try:
        implementation_flows.guard(context)
        if context.gate == 'task-specification-accept':
            # Acceptance also seals valid exemptions. An empty revision only
            # rechecks its generation's proof; it does not invent an approval.
            task_completion.accept(context)
            phase_rules.ok('task specification acceptance and completion evidence checked')
        if context.gate == 'task-specification-prepare':
            task_review.check_corrections(context)
        applies = (task_review.applicable(context) if context.gate == 'task-specification-prepare'
                   else task_review.confirmation_applicable(context))
        if not applies:
            if context.gate == 'task-specification-prepare':
                task_review.publish_generation(context)  # the generation Skill is skipped with this reason
            elif context.gate == task_review.WAIT:
                task_review.publish_confirmation_skip(context)  # L0 still issues the wait; the host skips it
            phase_rules.ok('task specification gate does not apply to this task', 省略='該当なし')
        if context.gate == 'task-specification-prepare':
            task_review.prepare(context)
            task_review.publish_generation(context)
        elif context.gate == task_review.WAIT:
            task_review.ingest(context)
            task_review.publish_confirmation(context)
            print('AIDD-TASK-REVIEW: ' + json.dumps(task_review.marker(context), ensure_ascii=False))
            presentation = task_review.presentation(context)
            if 'specification' in presentation:
                print('単体テスト仕様書: ' + presentation['specification'])
                print('今回の差分と確認資料: ' + presentation['report_summary'])
            if 'code_review_summary' in presentation:
                print('コードとテストのレビュー: ' + presentation['code_review_summary'])
            print('外部コードレビュー（MCP）: ' + presentation['mcp']['status'])
            print('続行・修正・保留を回答してください。未回答ではタスクを完了しません。')
            raise SystemExit(phase_rules.EXIT_WAIT)
        else:
            raise ValueError('unknown task specification gate')
    except (ValueError, OSError, KeyError, TypeError) as error:
        phase_rules.fail(str(error))
    phase_rules.ok('task specification gate completed')


if __name__ == '__main__':
    main()
