"""Require current decisions and resolution of carried findings.

At a -generate end, open 修正/差戻し findings already handed to a human-selected
repair (the following -revise, or an upstream rollback) do not block.
"""
import phase_rules
import repair_requests
import review_contract


def main():
    try:
        context = phase_rules.gate_context()
        review_contract.ready(context, allow_repair=repair_requests.is_generate(context))
    except (ValueError, OSError) as error:
        phase_rules.fail(str(error))
    phase_rules.ok("current and carried findings have complete human decisions")


if __name__ == "__main__":
    main()
