import phase_rules
import repair_requests

if __name__ == "__main__":
    try:
        repair_requests.check(phase_rules.gate_context())
    except (ValueError, OSError) as error:
        phase_rules.fail(str(error))
    phase_rules.ok("explicit repair request is available")
