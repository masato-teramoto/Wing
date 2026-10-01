import phase_rules
import prerequisites

if __name__ == "__main__":
    try:
        prerequisites.blockers(phase_rules.gate_context())
    except (ValueError, OSError) as error:
        phase_rules.fail(str(error))
    phase_rules.ok("no unresolved rollback blocks this action")
