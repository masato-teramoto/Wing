"""Completion is stricter than checking the evidence of already-approved files.

At a -generate end a pending human-selected repair defers approval to -revise.
At a -revise end the approved result consumes the repair request.
"""
import aidd_paths
import repair_actions
import review_contract


def main():
    try:
        context = aidd_paths.Context()
        if repair_actions.is_generate(context) and repair_actions.handed_to_revise(context):
            aidd_paths.ok("repair selected by the human; approval follows in the revise event")
        review_contract.check_approved(context)
        if repair_actions.is_revise(context):
            repair_actions.consume(context)
        elif context.event == 'tasks-gate-run':
            # Individual task documents have no approval gate. Their repair
            # requests finish only when the aggregate approval is complete.
            for feature in context.features():
                repair_actions.consume(repair_actions.revise_context(context, 'tasks', feature['name']))
    except (ValueError, OSError) as error:
        aidd_paths.fail(str(error))
    aidd_paths.ok("all required artifacts are approved")


if __name__ == "__main__":
    main()
