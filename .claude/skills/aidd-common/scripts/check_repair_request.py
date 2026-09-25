import aidd_paths
import repair_actions

if __name__ == "__main__":
    try:
        repair_actions.check(aidd_paths.Context())
    except (ValueError, OSError) as error:
        aidd_paths.fail(str(error))
    aidd_paths.ok("explicit repair request is available")
