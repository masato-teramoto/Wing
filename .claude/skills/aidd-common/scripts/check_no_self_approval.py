"""An approved artifact must have exact target/run/content evidence."""
import aidd_paths
import repair_actions
import review_contract


def main():
    try:
        context = aidd_paths.Context()
        review_contract.check_approved(context, require_all=False, allow_repair=repair_actions.is_generate(context))
    except (ValueError, OSError) as error:
        aidd_paths.fail(str(error))
    aidd_paths.ok("approval evidence matches the current inspection")


if __name__ == "__main__":
    main()
