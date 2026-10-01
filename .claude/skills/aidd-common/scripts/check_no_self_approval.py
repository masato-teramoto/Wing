"""An approved artifact must have exact target/run/content evidence."""
import phase_rules
import repair_requests
import review_contract


def main():
    try:
        context = phase_rules.gate_context()
        review_contract.check_approved(context, require_all=False, allow_repair=repair_requests.is_generate(context))
    except (ValueError, OSError) as error:
        phase_rules.fail(str(error))
    phase_rules.ok("approval evidence matches the current inspection")


if __name__ == "__main__":
    main()
