"""Refresh the derived feature snapshot only from the approved source."""
import aidd_paths
import feature_manifest


def main():
    context = aidd_paths.Context()
    try:
        features = feature_manifest.synchronize(context.root, context.state_path)
    except (ValueError, OSError) as error:
        aidd_paths.fail(str(error))
    aidd_paths.ok("feature snapshot synchronized: %d" % len(features))


if __name__ == "__main__":
    main()
