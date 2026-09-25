"""Require current decisions and resolution of carried findings.

At a -generate end, open 修正/差戻し findings already handed to a human-selected
repair (the following -revise, or an upstream rollback) do not block.
"""
import aidd_paths
import repair_actions
import review_contract


def main():
    try:
        context = aidd_paths.Context()
        review_contract.ready(context, allow_repair=repair_actions.is_generate(context))
    except (ValueError, OSError) as error:
        aidd_paths.fail(str(error))
    aidd_paths.ok("current and carried findings have complete human decisions")


if __name__ == "__main__":
    main()
