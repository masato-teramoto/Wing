"""Explicit repair requests and rollback state. No agent execution.

A repair reopens only what the fixed rollback table names (alpha2 status-protocol
§3): the owner's selected targets through its -revise action, the discovering
artifact through its own -revise (with the rollback finding), derived docs when a
design is sent back from Phase 7, and the owner phase's cross confirmation.
Actual consumers of changed content are reopened separately by project_progress.
Historical completion certificates are never rewritten to match new inputs.
"""
import l0  # noqa: F401  L0 の枠組みを import できるようにする
import hashlib
import json
from pathlib import Path

import phase_rules
import artifacts
import project_state
import review_decisions
import review_contract
import project_progress

ORIGINS = ("finding", "plan-change", "reopen", "authoring-candidate", "rollback", "rollback-derived", "rfp-change", "edited-outside-flow", "upstream-change")


def rule_of(context):
    return phase_rules.RULES.get(context.process, {})


def is_generate(context):
    return context.action == rule_of(context).get("generate")


def is_revise(context):
    return context.action == rule_of(context).get("repair")


def revise_context(context, process=None, item=None):
    process = process or context.process
    rule = phase_rules.RULES[process]
    return phase_rules.ExecutionContext(context.root, context.state_path, rule["repair"], context.item if item is None else item)


def pending(context):
    """The unconsumed repair request of this -revise action/item, or None."""
    data = project_progress.workflow(context).get("repairs", {}).get(project_progress.key(context))
    if isinstance(data, dict) and data.get("targets") and not data.get("consumed"):
        return data
    return None


def handed_to_revise(context):
    return pending(revise_context(context)) is not None


def consume(context):
    repairs = dict(project_progress.workflow(context).get("repairs", {}))
    data = repairs.get(project_progress.key(context))
    if isinstance(data, dict) and not data.get("consumed"):
        data = dict(data, consumed=project_state.now())
        repairs[project_progress.key(context)] = data
        history = list(project_progress.workflow(context).get("repair_history", []))
        history.append(data)
        project_progress.save(context, {"repairs": repairs, "repair_history": history})


def _set_draft(context, targets):
    for target in targets:
        path = Path(context.path(target))
        if path.exists() and (artifacts.fields(path) or {}).get("status") != "draft":
            artifacts.set_status(str(path), "draft", project_state.now())


def _record(owner, data):
    repairs = dict(project_progress.workflow(owner).get("repairs", {}))
    repairs[project_progress.key(owner)] = data
    project_progress.save(owner, {"repairs": repairs})


def _new_request(owner, targets, findings, actor, origin, instruction, extra):
    at = project_state.now()
    data = {"event": owner.action, "item": owner.item, "targets": list(targets), "findings": list(findings),
            "instruction": instruction, "origin": origin, "actor": actor, "at": at, "scheduled": None}
    data["id"] = hashlib.sha256((project_progress.key(owner) + at + json.dumps(findings, sort_keys=True, ensure_ascii=False) + instruction).encode()).hexdigest()
    if extra:
        data.update(extra)
    return data


def _open(owner, targets, findings, actor, origin, instruction="", extra=None):
    """Record the -revise request for owner (a -revise context) and reopen its targets."""
    if set(targets) - set(owner.artifacts()):
        raise ValueError("repair may change only the selected owner's artifacts")
    existing = pending(owner)
    if existing and all(existing.get(k) == v for k, v in (
            ("targets", list(targets)), ("findings", list(findings)), ("actor", actor),
            ("instruction", instruction), ("origin", origin))):
        data = existing  # a resent request keeps its id, time and instruction
    else:
        data = _new_request(owner, targets, findings, actor, origin, instruction, extra)
        _record(owner, data)
    return _schedule(owner, data)


def _schedule(owner, data):
    """Reopen the request's targets and redo its -revise event, then mark it scheduled."""
    if owner.process == 'tasks':
        # A plan revision ends the old task journal before the author edits its
        # protected body. Preserve its evidence and invalidate only this feature.
        import implementation_repair
        import task_runtime
        implementation_repair.invalidate_feature(owner, owner.item)
        task_runtime.retire(owner, owner.item)
    _set_draft(owner, data["targets"])
    project_progress.redo(owner, owner.action, owner.item or None)
    data = dict(data, scheduled=project_state.now())
    _record(owner, data)
    return data


def unscheduled(data):
    """Saved but not yet reopened/redone. Records from before this field are treated as scheduled."""
    return isinstance(data, dict) and "scheduled" in data and not data["scheduled"]


def ensure_scheduled(owner):
    """Finish the reopening of this owner's pending request if an interruption left it unscheduled."""
    data = pending(owner)
    if unscheduled(data):
        return _schedule(owner, data)
    return data


def resume_unscheduled(context):
    """Resume every pending request whose reopening was interrupted (called by audit)."""
    for data in list(project_progress.workflow(context).get("repairs", {}).values()):
        if unscheduled(data) and not data.get("consumed"):
            owner = phase_rules.ExecutionContext(context.root, context.state_path, data["event"], data.get("item") or "")
            ensure_scheduled(owner)


def _redo_cross(context, process):
    """The owner phase's cross confirmation no longer matches; inspect it again."""
    if process in ("requirements", "design"):
        action = process + "-cross-gate"
        current = project_progress.workflow(context)
        project_progress.save(context, {"invalidated_cross": sorted(set(current.get("invalidated_cross", [])) | {process})})
        project_progress.redo(context, action)
    elif process == "tasks":
        project_progress.redo(context, "tasks-gate-run")


def _discovering(context, row, owner_process, actor):
    """Reopen the artifact whose inspection found the rollback, through its own -revise."""
    phase = row["phase"]
    rule = phase_rules.RULES[phase]
    scope = row["scope"]
    note = "差戻し先（%s）の修正を反映して見直す: %s" % (owner_process, row["instruction"])
    if phase == 'implement':
        import implementation_repair
        implementation_repair.invalidate_feature(context, scope.removeprefix('feature:'), retire_plan=False)
        return
    if scope == "cross":
        _redo_cross(context, phase)
        return
    if phase == "tasks" and scope in ("phase",):
        project_progress.redo(context, "tasks-gate-run")
        return
    item = scope[len("feature:"):] if scope.startswith("feature:") else ""
    if rule["per_feature"] and not item:
        return
    owner = revise_context(context, phase, item)
    owner.draft_manifest = True
    targets = [t for t in owner.artifacts() if Path(owner.path(t)).exists()]
    if targets:
        _open(owner, targets, [row], actor, "rollback", note)
    if phase == "tasks":
        project_progress.redo(context, "tasks-gate-run")


def _derived(context, owner_process, row, actor):
    """alpha2 §3: a design sent back from Phase 7 also lowers docs/."""
    if owner_process == "design" and row["phase"] == "tasks":
        docs = revise_context(context, "docs", "")
        targets = [t for t in docs.artifacts() if Path(docs.path(t)).exists()]
        if targets:
            _open(docs, targets, [], actor, "rollback-derived", "design の差戻し修正を docs に反映する: " + row["instruction"])


def discovering_key(row):
    """-revise action/item of the artifact whose inspection found the rollback."""
    rule = phase_rules.RULES[row["phase"]]
    scope = row["scope"]
    if row['phase'] == 'implement':
        return 'implement-gate-run', scope.removeprefix('feature:')
    if scope == "cross":
        return row["phase"] + "-cross-gate", ""
    if row["phase"] == "tasks" and scope == "phase":
        return "tasks-gate-run", ""
    return rule["repair"], scope[len("feature:"):] if scope.startswith("feature:") else ""


def request(context, payload, actor, apply=True):
    """Human-selected repair. context names the owner (its -generate or -revise action and item).

    apply=False validates everything without writing (used before a review wait is answered).
    """
    review_decisions.person(actor)
    origin = payload.get("origin") or "finding"
    if origin not in ORIGINS:
        raise ValueError("unknown repair origin")
    if origin == "authoring-candidate":
        return request_from_candidate(context, payload, actor, apply)
    if origin in ("plan-change", "reopen"):
        if not payload.get("instruction"):
            raise ValueError("reopen requires the human instruction")
        if not apply:
            return None
        return reopen(context, payload.get("targets") or [], payload.get("instruction", ""), origin, actor,
                      resume_action=payload.get("resume_event", ""), resume_item=payload.get("resume_item", ""))
    selected = payload.get("findings")
    targets = payload.get("targets")
    if not isinstance(selected, list) or not selected or not isinstance(targets, list) or not targets:
        raise ValueError("repair requires human-selected findings and targets before changing status")
    if len(targets) != len(set(targets)) or not set(targets).issubset(context.artifacts()):
        raise ValueError("repair may change only the selected owner's artifacts")
    rows = []
    for row in selected:
        if not isinstance(row, dict) or not row.get("instruction"):
            raise ValueError("each selected finding needs the human repair instruction")
        phase = row.get("phase")
        if phase not in phase_rules.RULES:
            raise ValueError("unknown finding phase")
        if phase_rules.RULES[phase]["number"] < context.phase:
            raise ValueError("a repair target cannot be downstream of the finding owner")
        origin_context = phase_rules.ExecutionContext(context.root, context.state_path, phase_rules.RULES[phase]["generate"])
        record = review_contract.read(origin_context)
        found = review_decisions.finding(record, row["scope"], row["run"], row["number"])
        if found is None or found.resolved or found.decision not in ("修正", "差戻し"):
            raise ValueError("repair requires a recorded, unresolved human decision")
        if phase != context.process and found.decision != "差戻し":
            raise ValueError("cross-phase repair requires the human rollback decision")
        if phase == context.process and row["scope"] not in (context.scope, "cross", "phase") and found.decision != "差戻し":
            raise ValueError("repairing another feature's artifact requires the human rollback decision")
        rows.append(row)
    if not apply:
        return None
    owner = revise_context(context)
    data = _open(owner, targets, rows, actor, "finding")
    blockers = list(context.blockers())
    for row in rows:
        other_feature = row["phase"] == context.process and row["scope"] not in (context.scope, "cross", "phase")
        if phase_rules.RULES[row["phase"]]["number"] > context.phase or other_feature:
            if any(b.get("status") == "open" and b.get("target_event") == owner.action and b.get("target_item") == owner.item
                   and all((b.get("finding") or {}).get(k) == row.get(k) for k in ("phase", "scope", "run", "number"))
                   for b in blockers):
                continue  # a resent request after a partial failure
            resume_action, resume_item = discovering_key(row)
            blockers.append({"id": data["id"] + ":" + str(len(blockers)), "status": "open",
                             "return_to_phase": context.phase, "target_event": owner.action,
                             "target_item": owner.item, "targets": targets, "finding": row,
                             "resume_event": resume_action, "resume_item": resume_item,
                             "actor": actor, "at": project_state.now()})
    project_state.update(context.state_path, {"blockers": blockers})
    for row in rows:
        if row["phase"] != context.process or row["scope"] != context.scope:
            _discovering(context, row, context.process, actor)
            _derived(context, context.process, row, actor)
    if context.process in ("requirements", "design", "tasks"):
        _redo_cross(context, context.process)
    return data


def reopen(context, targets, instruction, origin, actor, resume_action="", resume_item=""):
    """Human instruction without a gate finding: plan change, explicit reinspection, etc."""
    review_decisions.person(actor)
    if not instruction:
        raise ValueError("reopen requires the human instruction")
    owner = revise_context(context)
    targets = targets or [t for t in owner.artifacts() if Path(owner.path(t)).exists()]
    data = _open(owner, targets, [], actor, origin, instruction)
    if resume_action:
        blockers = list(context.blockers())
        # The request ID survives interrupted replay. Keep its original blocker,
        # while allowing a separate return route to the same pending repair.
        existing = any(b.get("status") == "open" and b.get("id", "").startswith(data["id"] + ":")
                       and b.get("target_event") == owner.action and b.get("target_item") == owner.item
                       and b.get("resume_event") == resume_action and b.get("resume_item") == resume_item
                       for b in blockers)
        if not existing:
            blockers.append({"id": data["id"] + ":" + str(len(blockers)), "status": "open", "origin": origin,
                             "return_to_phase": context.phase, "target_event": owner.action, "target_item": owner.item,
                             "targets": targets, "finding": None, "instruction": instruction,
                             "resume_event": resume_action, "resume_item": resume_item, "actor": actor, "at": project_state.now()})
            project_state.update(context.state_path, {"blockers": blockers})
    if context.process in ("requirements", "design", "tasks"):
        _redo_cross(context, context.process)
    return data


def request_from_candidate(context, payload, actor, apply=True):
    """A return candidate reported while authoring (waiting result) that the human sends back."""
    source = payload.get("candidate") or {}
    discovering = phase_rules.ExecutionContext(context.root, context.state_path, source.get("event", ""), source.get("item", ""))
    if discovering.process not in phase_rules.RULES:
        raise ValueError("candidate must name the waiting authoring action")
    waiting = dict(project_progress.workflow(discovering).get("waiting", {}))
    entry = waiting.get(project_progress.key(discovering))
    candidates = (entry or {}).get("return_candidates") or []
    index = source.get("index", 0)
    if not entry or entry.get("status") != "waiting" or not isinstance(index, int) or not 0 <= index < len(candidates):
        raise ValueError("no recorded return candidate for this authoring wait")
    instruction = payload.get("instruction") or ""
    if not instruction:
        raise ValueError("rollback requires the human instruction")
    if not apply:
        return None
    data = reopen(context, payload.get("targets") or [], instruction, "authoring-candidate", actor,
                  resume_action=discovering.action, resume_item=discovering.item)
    if context.process == "design" and discovering.process == "tasks":
        # alpha2 §3: a design sent back from Phase 7 also lowers docs/ (same as the gate-finding route).
        _derived(context, "design", {"phase": "tasks", "instruction": instruction}, actor)
    entry.update(status="answered", answers=["差戻し: %s" % instruction], answered_by=actor,
                 answered_at=project_state.now(), rollback=data["id"])
    waiting[project_progress.key(discovering)] = entry
    project_progress.save(discovering, {"waiting": waiting})
    return data


def check(context):
    data = pending(context)
    if data is None:
        raise ValueError("a nonempty explicit repair request is required")
    if data.get("event") != context.action or data.get("item") != context.item or not set(data["targets"]).issubset(context.artifacts()):
        raise ValueError("repair request belongs to another target")
    return data


def upstream_approved(context, blocker_id, actor):
    review_decisions.person(actor)
    entries = context.blockers()
    found = next((entry for entry in entries if entry.get("id") == blocker_id), None)
    if found is None or found.get("status") != "open":
        raise ValueError("open rollback not found")
    target = phase_rules.ExecutionContext(context.root, context.state_path, found["target_event"], found["target_item"])
    # Tasks are inspected individually but approved by the aggregate Phase 7
    # review; there is no feature-scope approval row in the revision's record.
    approved = (phase_rules.ExecutionContext(context.root, context.state_path, 'tasks-gate-run')
                if target.process == 'tasks' else target)
    review_contract.check_approved(approved)
    found.update(status="upstream-approved", confirmed_by=actor, confirmed_at=project_state.now())
    if not found.get("finding"):
        # Plan changes / authoring candidates have no downstream finding to reinspect.
        found.update(status="resolved", resolved_by=actor, resolved_at=project_state.now())
    project_state.update(context.state_path, {"blockers": entries})
    return {"event": found["resume_event"], "item": found["resume_item"]}


def auto_clear(context, actor):
    """alpha2 clears a rollback implicitly when the upstream is re-approved and the finder
    is approved again. Called right after a human approval of `context`."""
    for entry in list(context.blockers()):
        same_owner = (entry.get("target_event") == context.action and (entry.get("target_item") or "") == context.item)
        tasks_owner = (context.action == 'tasks-gate-run'
                       and phase_rules.PROCESS_OF.get(entry.get('target_event')) == 'tasks')
        if entry.get("status") == "open" and (same_owner or tasks_owner):
            try:
                upstream_approved(context, entry["id"], actor)
            except ValueError:
                pass
    for entry in list(context.blockers()):
        if entry.get("status") == "upstream-approved" and entry.get("resume_event") == context.action and (entry.get("resume_item") or "") == context.item:
            try:
                complete_rollback(context, entry["id"], actor)
            except (ValueError, KeyError, TypeError):
                pass


def complete_rollback(context, blocker_id, actor):
    review_decisions.person(actor)
    entries = context.blockers()
    found = next((entry for entry in entries if entry.get("id") == blocker_id), None)
    if found is None or found.get("status") != "upstream-approved":
        raise ValueError("upstream reapproval is required before clearing rollback")
    row = found["finding"]
    finder = phase_rules.ExecutionContext(context.root, context.state_path, phase_rules.RULES[row["phase"]]["generate"],
                                row["scope"][len("feature:"):] if row["scope"].startswith("feature:") else "")
    record = review_contract.read(finder)
    finding = review_decisions.finding(record, row["scope"], row["run"], row["number"])
    if not finding or not finding.resolved:
        raise ValueError("downstream finding needs reinspection and explicit resolution")
    found.update(status="resolved", resolved_by=actor, resolved_at=project_state.now())
    project_state.update(context.state_path, {"blockers": entries})
