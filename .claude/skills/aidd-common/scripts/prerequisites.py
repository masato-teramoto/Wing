"""Workflow-specific prerequisites, invoked as L0 script events."""
from pathlib import Path

import aidd_paths
import artifacts
import review_actions
import review_contract


def approved(context, paths):
    import os
    import workflow_state
    for path in dict.fromkeys(paths):
        if (artifacts.fields(context.path(path)) or {}).get("status") != "approved":
            raise ValueError("required upstream artifact is missing or not approved: " + path)
        # status: approved alone is not evidence: the approval record must match the content.
        owner = workflow_state.owner_of(context, path)
        if owner is not None and not workflow_state.evidence_ok(owner):
            if os.environ.get("AIDD_UNIT"):
                raise ValueError("承認の証跡が内容と一致しません: %s（再検査・再承認が必要）" % path)
            raise ValueError(workflow_state.reopen_edited(context, owner, path))


def check(context):
    if context.process not in aidd_paths.RULES:
        raise ValueError("unknown workflow event")
    rule = aidd_paths.RULES[context.process]
    per_item_event = context.event in (rule["generate"], rule["repair"]) and rule["per_feature"]
    if per_item_event and not context.item:
        raise ValueError("this event requires --item")
    if not per_item_event and context.item:
        raise ValueError("this event does not take --item")
    inputs = context.upstream()
    if context.process == "intake":
        root = Path(context.path(".aidd/rfp"))
        if not root.is_dir() or not any(p.is_file() and not any(part.startswith('.') for part in p.relative_to(root).parts) for p in root.rglob('*')):
            raise ValueError("RFP input files are missing")
    approved(context, inputs)
    if context.process in ("design", "docs", "tasks"):
        review_actions.check_cross(context, "requirements")
    if context.process in ("docs", "tasks"):
        review_actions.check_cross(context, "design")
    if context.process in ("requirements", "design") and context.item:
        names = [f["name"] for f in context.features()]
        approved(context, ["specs/%s/%s.md" % (name, context.process) for name in names[:names.index(context.item)]])
    if context.event == "tasks-gate-run":
        record = review_contract.read(context)
        for feature in context.features():
            review_contract.inspection(context, record, "feature:" + feature["name"])
        for target in context.artifacts():
            if (artifacts.fields(context.path(target)) or {}).get("status") not in ("review", "approved"):
                raise ValueError("tasks must have completed their feature inspection: " + target)


def blockers(context):
    for entry in context.blockers():
        if not isinstance(entry, dict) or entry.get("status") not in ("open", "upstream-approved", "resolved"):
            raise ValueError("invalid blocker; explicit migration is required")
        if entry["status"] == "resolved":
            continue
        # The discovering artifact waits for its own upstream fix (also within one phase).
        if entry["status"] == "open" and entry.get("resume_event") == context.event and (entry.get("resume_item") or "") == context.item:
            raise ValueError("open rollback blocks this event until the upstream is reapproved: " + str(entry.get("id", "unknown")))
        phase = entry.get("return_to_phase")
        if not isinstance(phase, int) or not 1 <= phase <= 7:
            raise ValueError("invalid blocker return phase")
        if context.phase <= phase:
            continue
        if entry["status"] == "upstream-approved":
            origin = aidd_paths.RULES.get((entry.get("finding") or {}).get("phase"), {}).get("number")
            if origin and context.phase <= origin:
                continue  # Rebuild invalidated prerequisites before reinspecting the origin.
        raise ValueError("open rollback blocks this downstream event: " + str(entry.get("id", "unknown")))
