"""Phase 8 start/end guards. Never dispatch another L0 invocation here."""
import aidd_paths
import implementation_requests as requests
import implementation_flows

if __name__ == '__main__':
    try:
        context = aidd_paths.Context()
        implementation_flows.guard(context)
        if context.event == requests.FINAL:
            requests.prepare_review(context)
        elif context.hook_point == 'start':
            requests.preflight(context)
        else:
            requests.finish_task(context)
    except (ValueError, OSError, KeyError) as error:
        aidd_paths.fail(str(error))
    aidd_paths.ok('implementation boundary checked')
