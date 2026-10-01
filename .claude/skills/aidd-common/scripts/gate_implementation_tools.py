"""L4 tool gate; L3 supplies the frozen feature verification contract."""
import phase_rules
import implementation_checks

if __name__ == '__main__':
    try:
        implementation_checks.final(phase_rules.gate_context())
    except (ValueError, OSError, KeyError) as error:
        phase_rules.fail(str(error))
    phase_rules.ok('all required implementation commands completed and passed')
