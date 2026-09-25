"""L4 tool gate; L3 supplies the frozen feature verification contract."""
import aidd_paths
import implementation_checks

if __name__ == '__main__':
    try:
        implementation_checks.final(aidd_paths.Context())
    except (ValueError, OSError, KeyError) as error:
        aidd_paths.fail(str(error))
    aidd_paths.ok('all required implementation commands completed and passed')
