"""`when` condition for -revise gates: apply only while a human-selected repair is pending.

Exit 0 applies the gate; exit 11 (L0 SKIP_EXIT_CODE) skips it. The revise event
itself always runs; with no selected repair it edits nothing and its inspection,
review and approval gates are skipped (the generate approval stays in force).
"""
import sys

import aidd_paths
import workflow_state

SKIP = 11


def pending(context):
    rule = aidd_paths.RULES.get(context.process)
    if not rule or context.event != rule["repair"]:
        return False
    request = workflow_state.workflow(context).get("repairs", {}).get(workflow_state.key(context))
    return bool(isinstance(request, dict) and request.get("targets") and not request.get("consumed"))


def main():
    try:
        context = aidd_paths.Context()
        if pending(context):
            raise SystemExit(0)
    except (ValueError, OSError) as error:
        print(str(error), file=sys.stderr)
        raise SystemExit(1)
    print("修正対象 0 件")
    raise SystemExit(SKIP)


if __name__ == "__main__":
    main()
