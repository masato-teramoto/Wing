"""Rebuild a display from L3 facts; never approve, synchronize or dispatch work."""
import l0  # noqa: F401  L0 の枠組みを import できるようにする
from pathlib import Path

import phase_rules
import artifacts
import feature_manifest
import project_state


ERRORS = (ValueError, OSError, KeyError, TypeError, UnicodeError)
RELEASE = "alpha3"


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
    for name, rule in phase_rules.RULES.items():
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
    view = {"schema": 1, "status": "partial" if names is None else "ready",
            "feature_status": "undetermined" if names is None else "ready", "documents": values}
    if names and any(Path(context.root, ".aidd/implementation/features").glob("*/state.json")):
        # Phase 8 に入った案件だけ（全件の照合を毎回走らせない）。表示の失敗は残件の不明として出す。
        try:
            view["whole_project"] = whole_project(context)
        except ERRORS as error:
            view["whole_project"] = {"status": "不明", "remaining": [], "reason": str(error)}
    if workflow.get("mode") == "feature":
        # Feature 方式の進捗（§6.1 のナビゲーション）：方式・S・切替・差戻しで止まっている feature。
        switch = workflow.get("mode_switch") or {}
        stopped = sorted({n for b in context.blockers() if b.get("status") != "resolved"
                          for n in (b.get("affected_features") or [])})
        view["feature_mode"] = {"mode": "feature", "selection": (workflow.get("selection") or {}).get("feature", ""),
                                "switched_at": switch.get("at", ""), "switched_by": switch.get("actor", ""),
                                "stopped_features": stopped}
    return view


def whole_project(context):
    """案件全体の全件横断確認の残件（§6.7）。途中確認の寄せ集めで全件確認を済んだ扱いにしない。

    仕様の 3 層（全件の requirements／design 横断確認、全件 tasks-gate-run）と、実コードの 2 層（全体結合確認・
    implement-cross-gate）。ACE 対象外は implement-cross-gate の承認で人が一覧を見ていれば未実施に数えない。
    """
    import review_contract
    import review_decisions
    remaining = []
    for process in ("requirements", "design"):
        try:
            review_decisions.check_cross(context, process)
        except ERRORS:
            remaining.append("%s の全件横断確認" % process)
    try:
        review_contract.check_approved(phase_rules.ExecutionContext(context.root, context.state_path, "tasks-gate-run"))
    except ERRORS:
        remaining.append("tasks の全件確認（tasks-gate-run）")
    import implementation_project
    code = implementation_project.progress(context)
    if code["unapproved"]:
        remaining.append("実装承認（未承認: %s）" % ", ".join(code["unapproved"]))
    for group in implementation_project.GROUPS:
        if code["integration"].get(group, "未実施") != "passed":
            remaining.append("全体結合確認（%s）" % group)
    cross = phase_rules.ExecutionContext(context.root, context.state_path, implementation_project.CROSS_GATE)
    try:
        review_contract.check_approved(cross)
        approved = True
    except ERRORS:
        approved = False
        remaining.append("実コードの横断確認（implement-cross-gate）")
    excluded = (code["ace"] or {}).get("excluded", 0)
    status = ("全件整合済み" + ("（ACE 対象外 %d 件を承認済み）" % excluded if excluded and approved else "")) if not remaining else "残件あり"
    return {"status": status, "remaining": remaining, "ace": code["ace"]}


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
            "release": RELEASE,
            "progress": view["documents"],
            "progress_view": {**metadata, "refreshed_at": project_state.now()},
        })
    except ERRORS as error:
        return {**view, "cache_saved": False, "cache_error": str(error)}
    return {**view, "cache_saved": True}
