"""Completion is stricter than checking the evidence of already-approved files.

At a -generate end a pending human-selected repair defers approval to -revise.
At a -revise end the approved result consumes the repair request.
"""
import phase_rules
import repair_requests
import review_contract


def main():
    try:
        context = phase_rules.gate_context()
        if repair_requests.is_generate(context) and repair_requests.handed_to_revise(context):
            phase_rules.ok("repair selected by the human; approval follows in the revise action")
        review_contract.check_approved(context)
        if repair_requests.is_revise(context):
            repair_requests.consume(context)
        elif context.action == 'tasks-gate-run':
            # Individual task documents have no approval gate. Their repair
            # requests finish only when the aggregate approval is complete.
            for feature in context.features():
                repair_requests.consume(repair_requests.revise_context(context, 'tasks', feature['name']))
    except (ValueError, OSError) as error:
        phase_rules.fail(str(error))
    phase_rules.ok("all required artifacts are approved")


if __name__ == "__main__":
    main()
