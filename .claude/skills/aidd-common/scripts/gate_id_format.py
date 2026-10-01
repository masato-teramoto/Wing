"""Inspect exact requirement/feature definitions, not prose references."""
from pathlib import Path
import phase_rules
import feature_manifest
import findings_stage
import quality_inputs


def main():
    context = phase_rules.ExecutionContext()
    if context.process not in ("intake", "feature"):
        phase_rules.fail("unsupported ID-check process")
    for relative in context.gate_targets():
        text = Path(context.path(relative)).read_text(encoding="utf-8")
        try:
            if context.process == "intake":
                active = quality_inputs.requirements(text)
                retired = quality_inputs.requirements(text, retired=True)
                if set(active) & set(retired):
                    raise ValueError("active and retired IDs overlap")
            else:
                feature_manifest.parse(text)
        except ValueError as error:
            findings_stage.append(context, "format-conformance", relative, str(error))
    phase_rules.ok("ID and manifest structure check completed")


if __name__ == "__main__":
    main()
