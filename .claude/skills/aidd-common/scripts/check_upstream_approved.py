import phase_rules
import prerequisites

if __name__ == "__main__":
    try:
        prerequisites.check(phase_rules.gate_context())
    except (ValueError, OSError) as error:
        phase_rules.fail(str(error))
    phase_rules.ok("upstream and workflow prerequisites are satisfied")
