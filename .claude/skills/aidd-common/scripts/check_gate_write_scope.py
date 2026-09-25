"""Enforce immutable artifacts and exactly one undecided appended inspection."""
import hashlib
from pathlib import Path

import aidd_paths
import artifacts
import findings_stage
import record_format
import snapshot_artifacts


def _append_staged(context, before):
    """Append the inspector's staged block exactly once (idempotent across a crash/re-run)."""
    staged_path = Path(snapshot_artifacts.inspection_path(context))
    record_path = Path(context.gate_record)
    data = record_path.read_bytes()
    prefix = before["record"]
    if not staged_path.exists():
        return  # legacy inspector appended directly; validated below
    block = staged_path.read_text(encoding="utf-8").replace("\r\n", "\n").strip("\n")
    if not block:
        raise ValueError("the inspector's staged block is empty")
    suffix = ("\n" + block + "\n").encode("utf-8")
    if len(data) > prefix["bytes"]:
        if data[prefix["bytes"]:] != suffix:
            raise ValueError("gate record was appended outside the staged inspection")
    else:
        record_format.parse((data + suffix).decode("utf-8"))
        temporary = record_path.with_name(record_path.name + ".append.tmp")
        temporary.write_bytes(data + suffix)
        temporary.replace(record_path)
    if context.scope != "cross" and context.process != "implement":
        import project_state
        for relative, previous in before["artifacts"].items():
            target = context.path(relative)
            status = (artifacts.fields(target) or {}).get("status")
            if previous["status"] in ("draft", "review") and status == previous["status"] and status != "review":
                artifacts.set_status(target, "review", project_state.now())


def _verify_record(context, before, data):
    """Checks on the would-be record bytes (the actual file, or prefix + staged block)."""
    prefix = before["record"]
    if len(data) <= prefix["bytes"] or hashlib.sha256(data[:prefix["bytes"]]).hexdigest() != prefix["sha256"]:
        raise ValueError("gate record prefix changed or no inspection was appended")
    record = record_format.parse(data.decode("utf-8"))
    appended = record.blocks[prefix["blocks"]:]
    if [name for name, _ in appended] not in (["実行", "指摘"], ["実行", "指摘", "差戻し先候補"]):
        raise ValueError("gate may append only one inspection and its findings/candidates")
    run = record.runs[-1]
    if record.phase != context.process or run.scope != context.scope or run.number != before["run"]:
        raise ValueError("appended inspection identity differs from snapshot")
    if run.at != before["at"]:
        raise ValueError("inspection timestamp differs from snapshot")
    if run.targets != list(before["artifacts"]) or run.hashes != {p: e["sha256"] for p, e in before["artifacts"].items()}:
        raise ValueError("inspection targets differ from snapshot")
    staged = findings_stage.read(context)
    for row in staged:
        if not any(f.gate == row["gate"] and f.location == row["location"] and f.description == row["finding"] for f in run.findings):
            raise ValueError("deterministic finding was omitted or rewritten")
    return run


def validate_staged(context):
    """Dry run at the inspector's submit: a malformed block is refused before it is
    reported, so the host re-runs the inspector (the block is overwritten) instead of
    getting stuck at scope-check."""
    before = snapshot_artifacts.load(context)
    staged_path = Path(snapshot_artifacts.inspection_path(context))
    data = Path(context.gate_record).read_bytes()
    if not staged_path.exists():
        if len(data) > before["record"]["bytes"]:
            return _verify_record(context, before, data)  # legacy direct append
        raise ValueError("the inspector did not write its block to inspection_path")
    block = staged_path.read_text(encoding="utf-8").replace("\r\n", "\n").strip("\n")
    if not block:
        raise ValueError("the inspector's staged block is empty")
    suffix = ("\n" + block + "\n").encode("utf-8")
    if len(data) > before["record"]["bytes"]:
        if data[before["record"]["bytes"]:] != suffix:
            raise ValueError("gate record was appended outside the staged inspection")
        return _verify_record(context, before, data)
    return _verify_record(context, before, data + suffix)


def check(context):
    before = snapshot_artifacts.load(context)
    if context.process == 'implement':
        import implementation_evidence
        import implementation_requests
        state = implementation_requests.feature_state(context, context.item)
        if before['workspace_code'] != implementation_evidence.inventory(context, state['policy']):
            raise ValueError('inspector modified implementation workspace files')
    validate_staged(context)
    for relative, previous in before["artifacts"].items():
        target = context.path(relative)
        if aidd_paths.inspection_digest(context, relative) != previous["sha256"]:
            raise ValueError("protected artifact changed: %s" % relative)
        if context.process == "implement":
            continue
        status = (artifacts.fields(target) or {}).get("status")
        allowed = (previous["status"], "review") if previous["status"] in ("draft", "review") else (previous["status"],)
        if status not in allowed:
            raise ValueError("unauthorized status transition: %s" % relative)
    _append_staged(context, before)
    return _verify_record(context, before, Path(context.gate_record).read_bytes())


def main():
    try:
        context = aidd_paths.Context()
        run = check(context)
        import inspection_seal
        inspection_seal.save(context, run)
    except (ValueError, OSError) as error:
        aidd_paths.fail(str(error))
    aidd_paths.ok("gate write scope is intact", 回数=run.number, 指摘=run.count)


if __name__ == "__main__":
    main()
