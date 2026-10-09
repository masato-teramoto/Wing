"""Workflow-specific prerequisites, invoked as L0 script actions."""
from pathlib import Path

import phase_rules
import artifacts
import review_decisions
import review_contract
import record_format


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
    if context.kind == "plan":
        import implementation_requests
        implementation_requests.plan_prerequisites(context)  # 計画停止点 implement-plan[S]（D-11）
        return
    if context.kind in ("cross", "integration"):
        import implementation_project
        implementation_project.prerequisites(context)  # 全 feature の実装承認の後（§6.11）
        return
    rule = phase_rules.RULES[context.process]
    per_item_action = context.action in (rule["generate"], rule["repair"]) and rule["per_feature"]
    if per_item_action and not context.item:
        raise ValueError("this action requires --item")
    if not per_item_action and context.item and not context.selection and not context.plan_item:
        raise ValueError("this action does not take --item")
    import feature_scope
    feature_mode = feature_scope.is_feature(context)
    if (context.selection or context.plan_item) and not feature_mode:
        raise ValueError("全件方式の案件では feature を指定できません（%s --item %s）。Feature 方式への切替は /aidd-mode-switch で行います"
                         % (context.action, context.item))
    if (feature_mode and context.action.endswith("-plan") and context.process in ("design", "tasks")
            and not context.plan_item):
        raise ValueError("Feature 方式の %s は item（選択 feature）付きで呼びます" % context.action)
    feature_scope.require_selected(context)
    feature_scope.require_owner_for_tasks(context)
    if context.selection and context.is_cross and context.feature()["kind"] != "Platform":
        # User feature と依存先の整合は design-check が見る。途中の横断確認は共通機能の番だけ（§6.3 2b）。
        raise ValueError("selection cross inspection is only for Platform features: " + context.item)
    inputs = context.upstream()
    if context.process == "intake":
        root = Path(context.path(".aidd/rfp"))
        if not root.is_dir() or not any(p.is_file() and not any(part.startswith('.') for part in p.relative_to(root).parts) for p in root.rglob('*')):
            raise ValueError("RFP input files are missing")
    approved(context, inputs)
    if feature_mode:
        _selection_crosses(context)
    else:
        if context.process in ("design", "docs", "tasks"):
            review_decisions.check_cross(context, "requirements")
        if context.process in ("docs", "tasks"):
            review_decisions.check_cross(context, "design")
    if context.process in ("requirements", "design") and per_item_action and not feature_mode:
        names = [f["name"] for f in context.features()]
        approved(context, ["specs/%s/%s.md" % (name, context.process) for name in names[:names.index(context.item)]])
    if context.action == "tasks-gate-run":
        record = review_contract.read(context)
        names = [context.selection] if context.selection else [f["name"] for f in context.features()]
        for name in names:
            review_contract.inspection(context, record, record_format.scope_of("feature", name))
        if context.selection:
            # 比較相手（D、Platform なら利用側）の tasks は各自の回で承認済みであること（§6.3 2a）。
            # tasks.md は owner_of の対象外（status 欄だけになる）なので、承認行と内容の hash で照合する。
            for name in context.comparison_features():
                if name != context.selection:
                    review_contract.phase_approved(context, "specs/%s/tasks.md" % name)
        for target in context.artifacts():
            if (artifacts.fields(context.path(target)) or {}).get("status") not in ("review", "approved"):
                raise ValueError("tasks must have completed their feature inspection: " + target)


def _selection_crosses(context):
    """Feature 方式の横断確認の前提（D-6）。全件 cross は前提にしない。

    S が Platform で利用側 Cons(p) があるときだけ、S の `cross:<S>` の有効な確認を求める。User と Cons(p)=∅ は前提にしない。
    item 無しの action（docs）は selection を持たないので前提にしない（全件横断確認は U 全件が揃った後に通す）。
    """
    import feature_scope
    name = context.item if context.process in ("design", "tasks") else ""
    if not name:
        return
    for process in ("requirements", "design") if context.process == "tasks" else ("requirements",):
        if feature_scope.consumers(context, process, name):
            review_decisions.check_cross(context, process, name)


def _blocks(context, entry):
    """blocker の範囲（§6.8）。affected_features の無い blocker（全件方式・旧案件）は案件全体を止める。"""
    import feature_scope
    if not feature_scope.is_feature(context):
        return True
    docs = phase_rules.RULES["docs"]
    if context.kind in ("task", "final", "plan") and entry.get("target_event") in (docs["generate"], docs["repair"]):
        return False  # Feature 方式の Phase 8 は docs の固定版を参照するので、docs の差戻しでは止めない
    scope = entry.get("affected_features")
    if not scope:
        return True
    current = feature_scope.current_feature(context)
    return not current or current in scope


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
        if not _blocks(context, entry):
            continue
        if entry["status"] == "upstream-approved":
            origin = phase_rules.RULES.get((entry.get("finding") or {}).get("phase"), {}).get("number")
            if origin and context.phase <= origin:
                continue  # Rebuild invalidated prerequisites before reinspecting the origin.
        raise ValueError("open rollback blocks this downstream action: " + str(entry.get("id", "unknown")))
