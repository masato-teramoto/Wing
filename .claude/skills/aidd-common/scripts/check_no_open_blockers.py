import aidd_paths
import prerequisites

if __name__ == "__main__":
    try:
        prerequisites.blockers(aidd_paths.Context())
    except (ValueError, OSError) as error:
        aidd_paths.fail(str(error))
    aidd_paths.ok("no unresolved rollback blocks this event")
