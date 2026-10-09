"""L3 state policy. Runtime invalidation goes through the public L0 CLI only."""
import l0  # noqa: F401  L0 の枠組みを import できるようにする
import hashlib
import json
from pathlib import Path
import subprocess
import sys

import phase_rules
import artifacts
import feature_manifest
import prerequisites
import project_state


def workflow(context):
    value = context.state().get("workflow", {})
    if not isinstance(value, dict):
        raise ValueError("workflow must be an object")
    return value


def save(context, changes):
    data = dict(workflow(context))
    data.update(changes)
    project_state.update(context.state_path, {"workflow": data})


def key(context):
    return context.action + "[" + context.item + "]"


def require_current_inputs(context):
    data = workflow(context)
    inputs = data.get('inputs', {})
    if inputs and (data.get('input_signature_version') != 2 or any(
            name.split('[', 1)[0] not in phase_rules.PROCESS_OF for name in inputs)):
        raise ValueError('旧イベント名または旧入力証跡です。案件を停止したコピーで migration.md の移行手順を実施してください')


def signature(context):
    if context.kind in ('cross', 'integration'):
        import implementation_project
        return implementation_project.signature(context)
    if context.kind == 'plan':
        import implementation_requests as implementation
        return implementation.plan_signature(context, implementation.feature_of(context))
    if context.is_implementation:
        import implementation_requests as implementation
        return implementation.input_signature(context, implementation.feature_of(context))
    paths = context.upstream()
    if context.process == "intake":
        rfp = Path(context.path(".aidd/rfp"))
        paths = sorted(p.relative_to(context.root).as_posix() for p in rfp.rglob('*') if p.is_file() and not any(s.startswith('.') for s in p.relative_to(rfp).parts))
    # Approval metadata is mutable; the protected content and authorized task
    # projection are the input version actually used by authoring/inspection.
    import feature_scope
    scoped = context.phase >= 4 and bool(context.item) and feature_scope.is_feature(context)
    docs = phase_rules.config()["rules"]["docs"]["outputs"] if scoped and context.process == "tasks" else ()
    hashes = {p: (hashlib.sha256(Path(context.path(p)).read_bytes()).hexdigest()
                  if context.process == 'intake' else artifacts.protected_digest(context.path(p))) for p in paths if p not in docs}
    if docs:
        # Feature 方式の tasks は docs の固定版を参照する（§6.5）。docs の改訂は C2 の影響評価で受ける。
        import docs_revision
        hashes["docs_revision"] = docs_revision.fixed(context, context.item) or "unfixed"
    if context.phase >= 4:
        hashes[feature_manifest.SOURCE] = (feature_manifest.projection(context.root, _projected(context)) if scoped
                                           else feature_manifest.source_hash(context.root))
    return hashes


def _projected(context):
    """射影に入れる行（§6.5）：自 feature と推移閉包 D。共通機能の横断確認・tasks の selection 確認は比較集合 C(p)。"""
    import feature_scope
    if context.selection:
        return context.comparison_features()
    return [context.item, *feature_scope.closure(context, context.item)]


def cross_key(process, selection=""):
    """workflow.invalidated_cross の鍵。全件の横断確認は工程名、selection 単位は `<工程>:<S>`。

    鍵を分けるので、cross:<S> の確認が全件 cross の失効印を消さない（逆も同じ）。
    """
    return process + (":" + selection if selection else "")


def redo(context, action, item=None):
    """Called by the stopped host's preflight/action command, never a gate child."""
    common = Path(__file__).resolve().parents[1]
    call = action
    if phase_rules.implement_kind(action) in phase_rules.EVIDENCE_KINDS:
        import implementation_flows
        owner = phase_rules.ExecutionContext(context.root, context.state_path, action, item or '')
        call = implementation_flows.require_call(owner, validate=True)
    command = [sys.executable, "-B", str(common / "bin/aidd.py"), "--config", str(common),
               "--root", context.root, "--state", context.state_path,
               "redo", "--call", call, "--action", action, "--json"]
    if item is not None:
        command += ["--item", item]
    result = subprocess.run(command, capture_output=True, encoding="utf-8", check=False)
    if result.returncode:
        raise ValueError("runtime invalidation failed: " + (result.stderr or result.stdout).strip())


def invalidate(context, from_phase, include_current=True, item=None):
    """Conservative downstream closure; retain artifacts, history and questions.

    全件方式の明示的な全件再計画として残す（計画 v3 §6.5、段階 0 で確定）。一覧順で後続 feature を開き直すので、
    Feature 方式では呼ばない（失効は入力変更検知・射影・差戻しの範囲で受ける）。
    """
    import feature_scope
    if feature_scope.is_feature(context):
        raise ValueError("一覧順の全件失効（invalidate）は Feature 方式では使いません。差戻し（reopen）で範囲を指定してください")
    feature_scope.settle_mode(context)  # 計画了承を消す前に、旧案件の全件方式を書く
    start = from_phase if include_current else from_phase + 1
    import implementation_repair
    implementation_repair.invalidate(context, start, item)
    state = context.state()
    features = state.get("features") or []
    names = [f["name"] for f in features]
    # Requirements/design are approved in manifest order. Rebuild the selected
    # item and later items; keep earlier approved providers usable for repair.
    affected_items = names[names.index(item):] if item in names and start in (4, 5) else ([item] if item else names)
    events = set()
    targets = []
    for name, rule in phase_rules.RULES.items():
        if name == 'implement':
            continue  # Code evidence is invalidated without writing Markdown status.
        if rule["number"] < start:
            continue
        events.update((rule["generate"], rule["repair"]))
        if name in ("requirements", "design", "tasks"):
            events.add(name + "-plan")
            events.add(name + "-cross-gate" if name != "tasks" else "tasks-gate-run")
        selected = [f for f in features if not item or rule["number"] != start or f["name"] in affected_items]
        targets += ([p.format(feature=f["name"]) for f in selected for p in rule["outputs"]]
                    if rule["per_feature"] else rule["outputs"])
    # Persist pending work first. A partial failure cannot look like completion.
    save(context, {"invalidation": {"from_phase": start, "item": item, "events": sorted(events), "targets": targets, "at": project_state.now()}})
    for action in sorted(events):
        owner = phase_rules.PROCESS_OF.get(action)
        rule = phase_rules.RULES.get(owner, {})
        if item and rule.get("number") == start and action in (rule.get("generate"), rule.get("repair")):
            for local_item in affected_items:
                redo(context, action, local_item)
        else:
            redo(context, action)
    for target in targets:
        if Path(context.path(target)).exists():
            artifacts.set_status(context.path(target), "draft", project_state.now())
    current = workflow(context)
    current.pop("invalidation", None)
    current["cross_confirmations"] = {name: value for name, value in current.get("cross_confirmations", {}).items()
                                       if phase_rules.RULES[name]["number"] < start}
    current["invalidated_cross"] = sorted(set(current.get("invalidated_cross", [])) | {
        name for name in ("requirements", "design") if phase_rules.RULES[name]["number"] >= start})
    current["accepted_plans"] = {name: value for name, value in current.get("accepted_plans", {}).items()
                                  if phase_rules.RULES[name]["number"] < start}
    def retained(name):
        action, _, scope = name.partition('[')
        rule = phase_rules.RULES.get(phase_rules.PROCESS_OF.get(action, ''), {})
        phase = rule.get("number", 99)
        return phase < start or (phase == start and item and rule.get("per_feature")
                                and action in (rule.get("generate"), rule.get("repair")) and scope[:-1] not in affected_items)
    for collection in ("inputs", "results", "completions"):
        current[collection] = {name: value for name, value in current.get(collection, {}).items() if retained(name)}
    project_state.update(context.state_path, {"workflow": current})


class Replanned(ValueError):
    """The approved feature source changed; the plan is presented again (not an error)."""


SYSTEM_ACTOR = "AIDD（変更の自動検知）"


def owner_of(context, path):
    """Artifact owner; Phase 7 aggregate evidence is checked by implementation prerequisites."""
    if path == ".aidd/requirement-list.md":
        process, item = "intake", ""
    elif path == feature_manifest.SOURCE:
        process, item = "feature", ""
    elif path.startswith("steering/"):
        process, item = "steering", ""
    elif path.startswith("docs/"):
        process, item = "docs", ""
    elif path.startswith("specs/") and path.count("/") == 2:
        _, item, name = path.split("/")
        process = name[:-3]
        if process not in ("requirements", "design"):
            return None
    else:
        return None
    return phase_rules.ExecutionContext(context.root, context.state_path, phase_rules.RULES[process]["generate"], item)


def evidence_ok(owner):
    import review_contract
    try:
        review_contract.check_approved(owner)
    except (ValueError, OSError, KeyError):
        return False
    return True


def rebaseline(context, paths):
    """Reopen actual consumers of changed inputs; never rewrite certificates."""
    for name, previous in list(workflow(context).get('inputs', {}).items()):
        if not set(paths) & set(previous):
            continue
        action, item = name[:-1].split('[', 1)
        consumer = phase_rules.ExecutionContext(context.root, context.state_path, action, item)
        try:
            current = signature(consumer)
        except (ValueError, OSError):
            continue
        if previous != current:
            input_changed(consumer, previous, current)


def reopen_consumer(context, changed):
    """Schedule work for this recorded consumer, retaining old review history."""
    import repair_requests
    if context.kind:
        import implementation_repair
        implementation_repair.reopen(context, changed)
    elif context.is_cross and context.selection and _comparison_only(context, changed):
        # 鮮度（§6.7）：比較相手（利用側 Cons）だけが変わったので失効印は付けず、再実施できるよう通過印だけ消す。
        redo(context, context.action, context.selection)
    elif context.is_cross or context.action == 'tasks-gate-run':
        repair_requests._redo_cross(context, context.process, context.selection)
    elif context.action.endswith('-plan'):
        # Feature 方式の <工程>-plan[S] は S の計画だけを出し直す（item を省くと L0 は全 item の済印を消す）。
        redo(context, context.action, context.item or None)
    else:
        owner = repair_requests.revise_context(context)
        if repair_requests.pending(owner) is not None:
            repair_requests.ensure_scheduled(owner)  # an existing request may have been interrupted
        else:
            targets = [p for p in owner.artifacts() if Path(owner.path(p)).exists()]
            if targets:
                repair_requests.reopen(context, targets,
                    '入力変更の影響を確認し、反映・再検査する: ' + ', '.join(changed),
                    'upstream-change', SYSTEM_ACTOR)
    # Acknowledge scheduling, not successful completion. Historical completion
    # inputs stay unchanged until this consumer really completes another run.
    inputs = dict(workflow(context).get('inputs', {}))
    inputs[key(context)] = signature(context)
    save(context, {'inputs': inputs})


def _comparison_only(context, changed):
    """変わった入力が、selection の横断確認の比較相手（S と依存先 D の外の feature の specs）だけか。

    feature に属さない入力（一覧の射影・steering・要求一覧・docs）が変わったら False（失効の側）。
    """
    import feature_scope
    if not changed:
        return False
    core = {context.selection, *feature_scope.closure(context, context.selection)}
    for path in changed:
        if path == feature_manifest.SOURCE:
            # 射影は比較集合 C(p) の行を持つので、利用側が増えるだけで変わる（§6.5）。S と D の行の変化は
            # S・D の成果物の開き直しと、selection の状態の hash の照合（review_decisions）で無効になる。
            continue
        parts = path.split('/')
        if not (len(parts) > 2 and parts[0] == 'specs') or parts[1] in core:
            return False
    return True


def reopen_edited(context, owner, path):
    """An approved artifact changed outside the flow: reinspect it through its -revise."""
    import repair_requests
    targets = [t for t in repair_requests.revise_context(owner).artifacts() if t == path] or [path]
    repair_requests.reopen(owner, targets, "承認後にフロー外で変更された内容（%s）を確認し、再検査・再承認する" % path,
                          "edited-outside-flow", SYSTEM_ACTOR)
    return "承認後にフロー外で変更されたため再検査が必要です: %s（%s%s を実行）" % (
        path, phase_rules.RULES[owner.process]["repair"], " --item " + owner.item if owner.item else "")


def rfp_changed(context):
    """alpha2: RFP の改版は差分判定に対して要求一覧を再承認する（下流は ③ が判断するまで動かさない）。"""
    import repair_requests
    intake = phase_rules.ExecutionContext(context.root, context.state_path, phase_rules.RULES["intake"]["generate"])
    if evidence_ok(intake):
        repair_requests.reopen(intake, [".aidd/requirement-list.md"],
                              "RFP の改版差分を反映する（既存IDとの維持／変更／新規／廃止を整理し、採番規則を守る）",
                              "rfp-change", SYSTEM_ACTOR)
        return "RFP が変更されました。要求一覧を改版差分で見直して再承認します（requirement-intake-revise）"
    waiting = dict(workflow(intake).get("waiting", {}))
    waiting.pop(key(intake), None)
    save(intake, {"waiting": waiting})
    redo(intake, intake.action)
    return "RFP が変更されました。要求受入を改訂後の RFP でやり直します"


def input_changed(context, previous, current):
    """Changed input content requires reinspection of its actual consumers."""
    import repair_requests
    changed = sorted(p for p in set(previous) | set(current) if previous.get(p) != current.get(p))
    messages = []
    official = False
    if any(p.startswith(".aidd/rfp/") for p in changed) and context.process == "intake":
        intake = phase_rules.ExecutionContext(context.root, context.state_path, phase_rules.RULES["intake"]["generate"])
        if repair_requests.pending(repair_requests.revise_context(intake)) is None:
            messages.append(rfp_changed(context))
        # The new RFP is the input from now on; the reopened intake revises against it.
        inputs = dict(workflow(context).get("inputs", {}))
        inputs[key(context)] = current
        save(context, {"inputs": inputs})
        official = True
    for path in changed:
        owner = owner_of(context, path)
        if owner is None:
            continue
        if (repair_requests.pending(repair_requests.revise_context(owner)) is not None
                and not evidence_ok(owner)):
            # Wait while the upstream repair is unapproved. Its reapproval
            # schedules this consumer instead of silently certifying new inputs.
            official = True
            continue
        if not evidence_ok(owner):
            messages.append(reopen_edited(context, owner, path))
    if not messages and not official:
        reopen_consumer(context, changed)
    return messages


def _manifest(context):
    """Synchronize an approved feature source and reopen only the affected features."""
    import repair_requests
    state = context.state()
    before = state.get("feature_manifest", {}).get("sha256")
    source = feature_manifest.source_hash(context.root, approved=False)
    pending_change = workflow(context).get("manifest_change", {})
    resume = bool(pending_change.get("needs_replan")) and pending_change.get("after") == source
    if before and before != source:
        feature = phase_rules.ExecutionContext(context.root, context.state_path, phase_rules.RULES["feature"]["generate"])
        if not evidence_ok(feature):
            raise ValueError(reopen_edited(context, feature, feature_manifest.SOURCE))
    feature_manifest.synchronize(context.root, context.state_path)
    change = dict(workflow(context).get("manifest_change", {}))
    if not (((before and before != source) or resume) and change.get("needs_replan")):
        return
    names = {f["name"]: f for f in context.features()}
    affected = set(change.get("changed", []))
    grew = True
    while grew:
        grew = False
        for name, entry in names.items():
            if name not in affected and set(entry.get("depends_on", [])) & affected:
                affected.add(name)
                grew = True
    reopened_design = False
    for process in ("requirements", "design", "tasks"):
        for name in sorted(affected & set(names)):
            owner = phase_rules.ExecutionContext(context.root, context.state_path, phase_rules.RULES[process]["generate"], name)
            target = "specs/%s/%s.md" % (name, process)
            if Path(owner.path(target)).exists():
                repair_requests.reopen(owner, [target], "feature 一覧の変更（%s）を反映する" % ", ".join(sorted(affected)),
                                      "rollback-derived", SYSTEM_ACTOR)
                reopened_design = reopened_design or process == "design"
    if reopened_design:
        docs = phase_rules.ExecutionContext(context.root, context.state_path, phase_rules.RULES["docs"]["generate"])
        existing = [t for t in docs.artifacts() if Path(docs.path(t)).exists()]
        if existing:
            repair_requests.reopen(docs, existing, "feature 一覧の変更に伴う design の見直しを docs に反映する", "rollback-derived", SYSTEM_ACTOR)
    import feature_scope
    feature_scope.settle_mode(context)  # 計画了承を消す前に、旧案件の全件方式を書く
    plans = dict(workflow(context).get("accepted_plans", {}))
    if change.get("structural") and feature_scope.is_feature(context):
        plans = _retained_plans(context, plans)
    elif change.get("structural"):
        plans = {k: v for k, v in plans.items() if k not in ("requirements", "design", "tasks")}
    else:
        plans = {k: dict(v, manifest=source) if isinstance(v, dict) and v.get("manifest") else v for k, v in plans.items()}
    change["needs_replan"] = False
    save(context, {"manifest_change": change, "accepted_plans": plans})
    rebaseline(context, [feature_manifest.SOURCE])


def _retained_plans(context, plans):
    """Feature 方式の一覧の構造変更：射影（S ∪ D）が変わらない feature の計画了承は残す（§6.5、F40）。"""
    import feature_scope
    names = {f["name"] for f in context.features()}
    kept = {}
    for process, entry in plans.items():
        if process not in feature_scope.PLAN_PROCESSES or not isinstance(entry, dict):
            kept[process] = entry
            continue
        items = {}
        for name, value in (entry.get("items") or {}).items():
            if name in names and value.get("manifest") == feature_scope.plan_digest(context, process, name):
                items[name] = value
        kept[process] = dict(entry, items=items) if "items" in entry else entry
        if process != "requirements":
            kept[process] = {"items": items}
    return kept


def sync_approved_manifest(context):
    """A re-approved feature list is synchronized (or its interrupted sync resumed) before consumers are audited."""
    before = (context.state().get("feature_manifest") or {}).get("sha256")
    path = feature_manifest.source_path(context.root)
    if not before or not path.is_file() or (artifacts.fields(path) or {}).get("status") != "approved":
        return
    source = feature_manifest.source_hash(context.root)
    change = workflow(context).get("manifest_change", {})
    if before != source or (change.get("needs_replan") and change.get("after") == source):
        _manifest(context)


def preflight(context):
    """Recheck even when L0 will skip already successful start units."""
    if phase_rules.is_management(context.action):
        return None
    require_current_inputs(context)
    if context.process not in phase_rules.RULES:
        raise ValueError("unknown main_flow action")
    if context.is_implementation:
        import implementation_requests
        return implementation_requests.preflight(context)
    pending = workflow(context).get("invalidation")
    if pending:
        invalidate(context, pending["from_phase"], item=pending.get("item"))
        raise ValueError("interrupted invalidation finished; review the plan before resuming")
    if context.phase >= 4:
        _manifest(context)
        feature_manifest.load(context.root, context.state_path)
    import feature_scope
    if feature_scope.is_feature(context) and context.action == phase_rules.RULES["docs"]["repair"]:
        import docs_revision
        docs_revision.accumulate(context)
    if feature_scope.is_feature(context) and context.process == "tasks" and context.item:
        import docs_revision
        rule = phase_rules.RULES["tasks"]
        docs_revision.ensure_fixed(context, context.item, regenerate=context.action == rule["repair"]
                                   and _regenerating(context))
    prerequisites.blockers(context)
    prerequisites.check(context)
    rule = phase_rules.RULES[context.process]
    # implement-plan[S] は計画停止点の経路（記録入力の比較）を通る。了承の照合は implement-select が見る（D-11）。
    if rule["per_feature"] and context.action == rule["generate"]:
        import feature_scope
        if not feature_scope.plan_accepted(context):
            raise ValueError("a current plan must be presented and confirmed before authoring")
    if context.kind == "cross":
        import implementation_project
        implementation_project.prepare_cross_review(context)  # snapshot が束ねる検査対象（§6.11）
    current = signature(context)
    previous = workflow(context).get("inputs", {}).get(key(context))
    if previous is not None and previous != current:
        messages = input_changed(context, previous, current)
        if messages:
            raise ValueError(" / ".join(messages))
    inputs = dict(workflow(context).get("inputs", {}))
    inputs[key(context)] = current
    save(context, {"inputs": inputs, "input_signature_version": 2})
    return {"event": context.action, "item": context.item, "scope": context.scope,
            "targets": context.artifacts(), "upstream": context.upstream(), "inputs": current}


def _regenerating(context):
    """tasks-authoring-revise が docs の影響評価による開き直しを処理する回か。"""
    import repair_requests
    request = repair_requests.pending(context)
    return bool(request) and request.get("origin") == "docs-revision"


def audit(context):
    """Standalone host action before choosing work, including an already-done call."""
    require_current_inputs(context)
    import feature_scope
    feature_scope.require_no_pending_switch(context)
    feature_scope.settle_mode(context)
    feature_scope.apply_owner_reopen(context)  # 直接の accept-plan で保留した owner の修正の要求
    pending = workflow(context).get("invalidation")
    if pending:
        invalidate(context, pending["from_phase"], item=pending.get("item"))
        raise ValueError("interrupted invalidation finished; review the plan")
    sync_approved_manifest(context)
    import feature_scope
    if feature_scope.is_feature(context) and (context.state().get("feature_manifest") or {}).get("sha256"):
        import docs_revision
        docs_revision.evaluate(context)
    import repair_requests
    repair_requests.resume_unscheduled(context)
    entries = list(workflow(context).get("inputs", {}).items())
    entries.sort(key=lambda pair: phase_rules.RULES[phase_rules.PROCESS_OF[pair[0].split('[', 1)[0]]]["number"])
    for name, previous in entries:
        action, item = name[:-1].split('[', 1)
        target = phase_rules.ExecutionContext(context.root, context.state_path, action, item)
        try:
            current = signature(target)
        except (ValueError, OSError):
            continue  # Not yet resolvable (e.g. feature not in the approved manifest); preflight decides.
        if previous != current:
            messages = input_changed(target, previous, current)
            if messages:
                raise ValueError(" / ".join(messages))
    return {"checked": len(entries)}


def progress(context):
    import progress_view
    return progress_view.refresh(context)
