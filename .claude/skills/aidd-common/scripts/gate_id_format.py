"""Inspect exact requirement/feature definitions, not prose references."""
from pathlib import Path
import aidd_paths
import feature_manifest
import findings_stage
import quality_inputs


def main():
    context = aidd_paths.Context()
    relative = ".aidd/requirement-list.md" if context.process == "intake" else ".aidd/feature-list.md"
    text = Path(context.path(relative)).read_text(encoding="utf-8")
    try:
        if context.process == "intake":
            active = quality_inputs.requirements(text)
            retired = quality_inputs.requirements(text, retired=True)
            if set(active) & set(retired):
                raise ValueError("active and retired IDs overlap")
        elif context.process == "feature":
            feature_manifest.parse(text)
        else:
            raise ValueError("unsupported ID-check process")
    except ValueError as error:
        findings_stage.append(context, "format-conformance", relative, str(error))
    aidd_paths.ok("ID and manifest structure check completed")


if __name__ == "__main__":
    main()
