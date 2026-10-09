"""Authoring return-envelope checks owned by L3, not the generic runner."""
import phase_rules
import artifacts
import repair_requests
import project_progress


def check_open_placeholders(data):
    if "open_placeholders" not in data:
        raise ValueError("authoring result requires open_placeholders; obtain a fresh result")
    count = data["open_placeholders"]
    if count is None and data.get("status") == "failed":
        return  # An unreadable input must not be reported as zero unfilled slots.
    if type(count) is not int or count < 0:
        raise ValueError("open_placeholders must be a nonnegative integer")
    if data.get("status") == "completed" and count != 0:
        raise ValueError("completed authoring requires zero open_placeholders")
    if data.get("status") == "waiting" and count and not (data.get("questions") or data.get("return_candidates")):
        raise ValueError("open_placeholders need questions or return candidates identifying the slots")


def validate(context, data):
    if context.is_implementation:
        import implementation_requests
        return implementation_requests.validate_result(context, data)
    rule = phase_rules.RULES[context.process]
    if context.action not in (rule["generate"], rule["repair"]):
        raise ValueError("not an authoring action")
    status = data.get("status")
    if status not in ("completed", "waiting", "failed"):
        raise ValueError("invalid authoring return status")
    for name in ("targets", "questions", "changed_findings", "return_candidates"):
        if not isinstance(data.get(name), list):
            raise ValueError("authoring result requires array: " + name)
    check_open_placeholders(data)
    repair = repair_requests.pending(context) if context.action == rule["repair"] else None
    if context.action == rule["repair"] and repair is None:
        # With no selected repair the revise Skill answers next with done; if run anyway it edits nothing.
        if status != "completed" or data["targets"] or data["changed_findings"] or data["questions"] or data["return_candidates"]:
            raise ValueError("no repair is selected: the revise result must be completed with no targets or changes")
        return {**data, "hashes": {}}
    expected = repair["targets"] if repair is not None else context.artifacts()
    if set(data["targets"]) - set(expected):
        raise ValueError("authoring reported artifacts outside its ownership")
    hashes = {}
    if status == "completed":
        if data["targets"] != expected or data["questions"] or data["return_candidates"]:
            raise ValueError("completed authoring needs all targets and no pending questions/returns")
        if context.action == rule["repair"]:
            def finding_key(row):
                return tuple(row[k] for k in ("phase", "scope", "run", "number"))
            selected = {finding_key(row) for row in repair["findings"]}
            changed = {finding_key(row) for row in data["changed_findings"]}
            if changed != selected:
                raise ValueError("repair result must identify every selected finding and no others")
        for target in expected:
            if (artifacts.fields(context.path(target)) or {}).get("status") != "draft":
                raise ValueError("authoring must return existing draft artifacts: " + target)
            hashes[target] = artifacts.protected_digest(context.path(target))
    value = {**data, "hashes": hashes}
    if repair is not None and status == "completed":
        # The repair Skill's next reads this: a request applied by a finished round is not run again.
        value["repair_id"] = repair.get("id")
    return value


def save(context, data):
    if context.is_implementation:
        import implementation_requests
        return implementation_requests.save_result(context, data)
    value = validate(context, data)
    results = dict(project_progress.workflow(context).get("results", {}))
    results[project_progress.key(context)] = value
    project_progress.save(context, {"results": results})
    return {"status": value['status'], "targets": data["targets"], "open_placeholders": data["open_placeholders"]}


def check(context):
    result = project_progress.workflow(context).get("results", {}).get(project_progress.key(context))
    if not result or result.get("status") != "completed":
        raise ValueError("host must record a completed authoring result before reporting ok")
    check_open_placeholders(result)
    for target, digest in result["hashes"].items():
        if digest != artifacts.protected_digest(context.path(target)):
            raise ValueError("artifact changed after the authoring result: " + target)


if __name__ == "__main__":
    try:
        check(phase_rules.gate_context())
    except (ValueError, OSError) as error:
        phase_rules.fail(str(error))
    phase_rules.ok("authoring result is complete")
