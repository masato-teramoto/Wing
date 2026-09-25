"""Rebuild a display from L3 facts; never approve, synchronize or dispatch work."""
from pathlib import Path

import aidd_paths
import artifacts
import feature_manifest
import project_state


ERRORS = (ValueError, OSError, KeyError, TypeError, UnicodeError)


def document_status(context, relative):
    path = Path(context.path(relative))
    try:
        path.stat()
    except FileNotFoundError:
        return "not_started"
    fields = artifacts.fields(path)
    if fields is None or fields.get("status") not in ("draft", "review", "approved"):
        raise ValueError("invalid or changed progress source: " + relative)
    return fields["status"]


def calculate(context):
    """Read facts only. A missing feature set is unknown, never zero completed."""
    state = context.state()
    workflow = state.get("workflow", {})
    if not isinstance(workflow, dict):
        raise ValueError("workflow must be an object")
    change = workflow.get("manifest_change", {})
    if not isinstance(change, dict) or not isinstance(state.get("feature_manifest", {}), dict):
        raise ValueError("invalid progress source metadata")
    if workflow.get("invalidation") or change.get("needs_replan"):
        return {"schema": 1, "status": "updating", "documents": None,
                "feature_status": "unavailable", "reason": "workflow invalidation or replanning is pending"}

    source_status = document_status(context, feature_manifest.SOURCE)
    if source_status == "approved":
        features = feature_manifest.load(context.root, context.state_path)
        names = [entry["name"] for entry in features]
    elif state.get("feature_manifest") or state.get("features") or (context.phase or 0) >= 4:
        raise ValueError("previously synchronized feature source is missing or not approved")
    else:
        names = None

    values = {}
    for name, rule in aidd_paths.RULES.items():
        if name == 'implement':
            import implementation_repair
            values[name] = implementation_repair.progress(context, names)
            continue
        if rule["per_feature"] and names is None:
            values[name] = None
            continue
        paths = ([p.format(feature=feature) for feature in names for p in rule["outputs"]]
                 if rule["per_feature"] else rule["outputs"])
        values[name] = {p: document_status(context, p) for p in paths}
    return {"schema": 1, "status": "partial" if names is None else "ready",
            "feature_status": "undetermined" if names is None else "ready", "documents": values}


def refresh(context):
    """Display failures are data, so a committed action need not be replayed."""
    try:
        view = calculate(context)
    except ERRORS as error:
        view = {"schema": 1, "status": "unavailable", "documents": None,
                "feature_status": "unavailable", "reason": str(error)}
    metadata = {key: value for key, value in view.items() if key != "documents"}
    try:
        project_state.update(context.state_path, {
            "release": aidd_paths.CONTRACT["release"],
            "progress": view["documents"],
            "progress_view": {**metadata, "refreshed_at": project_state.now()},
        })
    except ERRORS as error:
        return {**view, "cache_saved": False, "cache_error": str(error)}
    return {**view, "cache_saved": True}
