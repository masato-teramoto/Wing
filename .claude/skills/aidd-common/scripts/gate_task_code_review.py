"""Prepare a task code review with existing L3 identity and L0 sequencing.

The gate decides for itself whether it applies (no `when` in gate.yaml), and publishes the
review Skill's context or its reasoned skip for the host to relay (gate_exchange).
"""
import l0  # noqa: F401
import phase_rules
import implementation_flows
import implementation_code_review
import implementation_task_review

if __name__ == '__main__':
    try:
        context = phase_rules.ExecutionContext()
        implementation_flows.guard(context)
        implementation_task_review.check_corrections(context)
        # The preceding generation must be accepted before preparing another
        # inspection, including when code review itself does not apply.
        implementation_task_review.ingest_generation(context)
        if not implementation_code_review.applicable(context):
            implementation_code_review.publish(context)  # the review Skill is skipped with this reason
            phase_rules.ok('task code review does not apply to this task', 省略='該当なし')
        implementation_code_review.prepare(context)
        implementation_code_review.publish(context)
    except (ValueError, OSError, KeyError, TypeError) as error:
        phase_rules.fail(str(error))
    phase_rules.ok('task code review prepared')
