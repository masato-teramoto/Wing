import aidd_paths
import prerequisites

if __name__ == "__main__":
    try:
        prerequisites.check(aidd_paths.Context())
    except (ValueError, OSError) as error:
        aidd_paths.fail(str(error))
    aidd_paths.ok("upstream and workflow prerequisites are satisfied")
