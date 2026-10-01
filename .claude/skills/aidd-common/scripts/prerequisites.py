"""Workflow-specific prerequisites, invoked as L0 script actions."""
from pathlib import Path

import phase_rules
import artifacts
import review_decisions
import review_contract


def approved(context, paths):
    import os
    import project_progress
    for path in dict.fromkeys(paths):
        owner = project_progress.owner_of(context, path)
        if owner is not None and unreviewed(owner, path):
            # Left out of its inspection gate's target_review: neither inspected nor approved (D6).
            # Its status field is not evidence either way, so an edited `approved` proves nothing.
            if not Path(context.path(path)).is_file():
                raise ValueError("required upstream artifact is missing: " + path)
            continue
        if (artifacts.fields(context.path(path)) or {}).get("status") != "approved":
            raise ValueError("required upstream artifact is missing or not approved: " + path)
        # status: approved alone is not evidence: the approval record must match the content.
        if owner is not None and not project_progress.evidence_ok(owner):
            if os.environ.get("AIDD_UNIT"):
                raise ValueError("承認の証跡が内容と一致しません: %s（再検査・再承認が必要）" % path)
            raise ValueError(project_progress.reopen_edited(context, owner, path))


def unreviewed(owner, path):
    """True when the owner's inspection gate leaves this output out of its target_review."""
    try:
        return path not in owner.review_targets()
    except ValueError:
        return False  # e.g. a feature outside the approved manifest: keep the not-approved refusal


def unreviewed_inputs(context, paths=None):
    """Upstream files this action may read although they are not approved (D6), for the host
    to hand to authoring and inspection Skills. Empty unless some target_review is narrowed.

    Phase 8 included: its own inspection covers every output, but its upstream (steering,
    specs) may still hold files left out of their inspection. `paths` defaults to the upstream.
    """
    import project_progress
    if paths is None:
        if context.process not in phase_rules.RULES:
            return []
        paths = context.upstream()
    found = []
    for path in paths:
        owner = project_progress.owner_of(context, path)
        if owner is not None and unreviewed(owner, path):
            found.append(path)
    return found


def check(context):
    if context.process not in phase_rules.RULES:
        raise ValueError("unknown workflow action")
    rule = phase_rules.RULES[context.process]
    per_item_action = context.action in (rule["generate"], rule["repair"]) and rule["per_feature"]
    if per_item_action and not context.item:
        raise ValueError("this action requires --item")
    if not per_item_action and context.item:
        raise ValueError("this action does not take --item")
    inputs = context.upstream()
    if context.process == "intake":
        root = Path(context.path(".aidd/rfp"))
        if not root.is_dir() or not any(p.is_file() and not any(part.startswith('.') for part in p.relative_to(root).parts) for p in root.rglob('*')):
            raise ValueError("RFP input files are missing")
    approved(context, inputs)
    if context.process in ("design", "docs", "tasks"):
        review_decisions.check_cross(context, "requirements")
    if context.process in ("docs", "tasks"):
        review_decisions.check_cross(context, "design")
    if context.process in ("requirements", "design") and context.item:
        names = [f["name"] for f in context.features()]
        approved(context, ["specs/%s/%s.md" % (name, context.process) for name in names[:names.index(context.item)]])
    if context.action == "tasks-gate-run":
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
        if entry["status"] == "open" and entry.get("resume_event") == context.action and (entry.get("resume_item") or "") == context.item:
            raise ValueError("open rollback blocks this action until the upstream is reapproved: " + str(entry.get("id", "unknown")))
        phase = entry.get("return_to_phase")
        if not isinstance(phase, int) or not 1 <= phase <= 7:
            raise ValueError("invalid blocker return phase")
        if context.phase <= phase:
            continue
        if entry["status"] == "upstream-approved":
            origin = phase_rules.RULES.get((entry.get("finding") or {}).get("phase"), {}).get("number")
            if origin and context.phase <= origin:
                continue  # Rebuild invalidated prerequisites before reinspecting the origin.
        raise ValueError("open rollback blocks this downstream action: " + str(entry.get("id", "unknown")))
