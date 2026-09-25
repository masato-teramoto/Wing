"""Capture a single inspection's inputs and immutable record prefix."""
import hashlib
import json
from pathlib import Path

import aidd_paths
import artifacts
import project_state
import record_format


def snapshot_path(context):
    # One serial host; an event/item has the same inspection identity whether
    # called directly or through a flow. Do not require callers to decode L0 keys.
    key = context.event + "[" + context.item + "]"
    name = hashlib.sha256(key.encode("utf-8")).hexdigest()
    return context.path(".aidd/.engine/%s.snapshot.json" % name)


def inspection_path(context):
    """Where the inspector writes its single run block; L3 appends it to the record once."""
    return snapshot_path(context).replace(".snapshot.json", ".inspection.md")


def body_digest(path):
    return artifacts.protected_digest(path) if Path(path).exists() else None


def load(context):
    data = json.loads(Path(snapshot_path(context)).read_text(encoding="utf-8"))
    if data.get("event") != context.event or data.get("scope") != context.scope or data.get("phase") != context.process:
        raise ValueError("snapshot belongs to another inspection")
    return data


def capture(context):
    targets = context.artifacts()
    entry = {"schema": 2, "phase": context.process, "event": context.event,
             "scope": context.scope, "at": project_state.now(), "artifacts": {}, "record": {}}
    if context.process == 'implement':
        import implementation_evidence
        import implementation_requests
        state = implementation_requests.feature_state(context, context.item)
        entry['workspace_code'] = implementation_evidence.inventory(context, state['policy'])
    for relative in targets:
        if context.process == 'implement':
            entry['profile'] = 'implementation-code-v1'
            entry['artifacts'][relative] = {'status': 'readonly', 'sha256': aidd_paths.inspection_digest(context, relative)}
            continue
        target = context.path(relative)
        fields = artifacts.fields(target)
        if fields is None or fields.get("status") not in ("draft", "review", "approved"):
            raise ValueError("inspection artifact missing or invalid: %s" % relative)
        entry["artifacts"][relative] = {"status": fields["status"], "sha256": artifacts.protected_digest(target)}
    path = Path(context.gate_record)
    if not path.exists():
        template = Path(context.path("Templates/Flow/gate-record.md")).read_text(encoding="utf-8")
        header = template.replace("{{PHASE_NAME}}", context.process).replace("{{ISO_8601_TIMESTAMP}}", entry["at"])
        record_format.parse(header)
        path.parent.mkdir(parents=True, exist_ok=True)
        # Path.write_text(newline=...) requires Python 3.10; keep explicit LF
        # output on the macOS system Python 3.9 as well.
        with path.open("w", encoding="utf-8", newline="\n") as handle:
            handle.write(header)
    data = path.read_bytes() if path.exists() else b""
    previous = record_format.parse(data.decode("utf-8"))
    if previous.phase != context.process:
        raise ValueError("gate record belongs to another phase")
    latest = previous.latest(context.scope)
    entry["run"] = latest.number + 1 if latest else 1
    entry["record"] = {"bytes": len(data), "sha256": hashlib.sha256(data).hexdigest(), "blocks": len(previous.blocks)}
    output = Path(snapshot_path(context))
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(entry, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    import findings_stage
    findings_stage.reset(context, entry)
    staged = Path(inspection_path(context))
    if staged.exists():
        staged.unlink()
    return entry


def main():
    try:
        entry = capture(aidd_paths.Context())
    except (ValueError, OSError) as error:
        aidd_paths.fail(str(error))
    aidd_paths.ok("inspection snapshot captured", 回数=entry["run"])


if __name__ == "__main__":
    main()
