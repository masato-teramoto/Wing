"""Phase 8 start/end guards. Never dispatch another L0 invocation here."""
import phase_rules
import implementation_requests as requests
import implementation_flows

if __name__ == '__main__':
    try:
        context = phase_rules.gate_context()
        implementation_flows.guard(context)
        if context.action == requests.FINAL:
            requests.prepare_review(context)
        elif context.hook_point == 'start':
            requests.preflight(context)
        else:
            requests.finish_task(context)
    except (ValueError, OSError, KeyError) as error:
        phase_rules.fail(str(error))
    phase_rules.ok('implementation boundary checked')
