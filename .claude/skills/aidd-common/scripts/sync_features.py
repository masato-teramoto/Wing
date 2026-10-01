"""Refresh the derived feature snapshot only from the approved source."""
import phase_rules
import feature_manifest


def main():
    context = phase_rules.ExecutionContext()
    try:
        features = feature_manifest.synchronize(context.root, context.state_path)
        # After synchronizing: expanding per-feature outputs needs the current snapshot.
        phase_rules.check_gate_targets(context)
    except (ValueError, OSError, KeyError) as error:
        phase_rules.fail(str(error))
    phase_rules.ok("feature snapshot synchronized: %d" % len(features))


if __name__ == "__main__":
    main()
