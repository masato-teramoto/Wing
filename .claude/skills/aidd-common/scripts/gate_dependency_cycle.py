"""Check dependency order in the actual L1 feature/table or task/checklist shape."""
from pathlib import Path
import aidd_paths
import feature_manifest
import findings_stage
import quality_inputs


def main():
    context = aidd_paths.Context()
    relative = ".aidd/feature-list.md" if context.process == "feature" else "specs/%s/tasks.md" % context.item
    if context.process not in ("feature", "tasks") or (context.process == "tasks" and not context.item):
        aidd_paths.fail("unsupported dependency-check scope")
    text = Path(context.path(relative)).read_text(encoding="utf-8")
    try:
        entries = feature_manifest.parse(text) if context.process == "feature" else quality_inputs.tasks(text)
        for problem in quality_inputs.graph_problems(entries):
            findings_stage.append(context, "dependency-cycle-detection", relative, problem)
    except ValueError as error:
        findings_stage.append(context, "format-conformance", relative, str(error))
    aidd_paths.ok("dependency check completed")


if __name__ == "__main__":
    main()
