"""Capture a single inspection's inputs and immutable record prefix."""
import l0  # noqa: F401  L0 の枠組みを import できるようにする
import hashlib
import json
from pathlib import Path

import phase_rules
import artifacts
import project_state
import record_format


def snapshot_path(context):
    # One serial host; an action/item has the same inspection identity whether
    # called directly or through a flow. Do not require callers to decode L0 keys.
    key = context.action + "[" + context.item + "]"
    name = hashlib.sha256(key.encode("utf-8")).hexdigest()
    return context.path(".aidd/.engine/%s.snapshot.json" % name)


def inspection_path(context):
    """Where the inspector writes its single run block; L3 appends it to the record once."""
    return snapshot_path(context).replace(".snapshot.json", ".inspection.md")


def body_digest(path):
    return artifacts.protected_digest(path) if Path(path).exists() else None


def load(context):
    data = json.loads(Path(snapshot_path(context)).read_text(encoding="utf-8"))
    if data.get("event") != context.action or data.get("scope") != context.scope or data.get("phase") != context.process:
        raise ValueError("snapshot belongs to another inspection")
    return data


def _previous(context, run):
    """同じスコープで、記録済みの最新の回（run）の snapshot（作成・修正のどちらのアクションでもよい）。無ければ None。

    検査が記録されずに中断した回の snapshot は使わない（それを基準にすると、変わった節が空になる）。
    """
    actions = {context.action}
    rule = phase_rules.RULES.get(context.process, {})
    if context.action in (rule.get("generate"), rule.get("repair")):
        actions |= {rule["generate"], rule["repair"]}
    found = []
    for action in actions:
        other = phase_rules.ExecutionContext(context.root, context.state_path, action, context.item)
        path = Path(snapshot_path(other))
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, ValueError):
            continue
        if (data.get("scope") == context.scope and data.get("phase") == context.process and data.get("sections")
                and data.get("run") == run):
            found.append(data)
    return max(found, key=lambda data: data.get("run", 0), default=None)


def changed_sections(before, after):
    """対象ごとに、前回から変わった節（追加・削除を含む）。新しい対象は `*`（ファイル全体）。"""
    result = {}
    for target, now in after.items():
        if target not in before:
            result[target] = ["*"]
            continue
        old = before[target]
        names = [n for n in list(now) + [n for n in old if n not in now] if n != "*" and old.get(n) != now.get(n)]
        if names:
            result[target] = names
    return result


def capture(context):
    targets = context.review_targets()
    entry = {"schema": 2, "phase": context.process, "event": context.action,
             "scope": context.scope, "at": project_state.now(), "artifacts": {}, "record": {}}
    # Outputs left out of target_review are not inspected, but the inspector must not edit them
    # either: neither the body nor the status (the body digest ignores status/updated_at).
    unreviewed = [p for p in context.artifacts() if p not in targets]
    if unreviewed:
        entry["unreviewed"] = {p: {"status": (artifacts.fields(context.path(p)) or {}).get("status"),
                                   "sha256": body_digest(context.path(p))} for p in unreviewed}
    if context.process == 'implement':
        import implementation_evidence
        import implementation_requests
        state = implementation_requests.feature_state(context, context.item)
        entry['workspace_code'] = implementation_evidence.inventory(context, state['policy'])
    for relative in targets:
        if context.process == 'implement':
            entry['profile'] = 'implementation-code-v1'
            entry['artifacts'][relative] = {'status': 'readonly', 'sha256': phase_rules.inspection_digest(context, relative)}
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
    if context.process != 'implement':
        # 節ごとのハッシュ。再検査では、前回から変わった節だけを意味検査する（差分の検査）。
        import finding_rules
        import project_progress
        entry["sections"] = {p: finding_rules.section_hashes(context.path(p)) for p in targets}
        entry["own_sections"] = {p: finding_rules.section_hashes(context.path(p), own=True) for p in targets}
        import reevaluation
        pending_reevaluation = reevaluation.pending(context)
        if pending_reevaluation:
            entry["reevaluation"] = pending_reevaluation
        try:
            entry["inputs"] = project_progress.signature(context)
        except (ValueError, OSError):
            entry["inputs"] = None
        before = _previous(context, latest.number) if latest is not None else None
        # 上流の入力（RFP・steering・上流の成果物）が前回の検査から変わっていれば、変わった節に絞らず全体を検査する。
        # 対象の本文が同じでも、上流の変更の反映漏れは対象のどの節にもありうるため。
        if (before is not None and latest is not None and entry["inputs"] is not None
                and before.get("inputs") == entry["inputs"]):
            entry["previous_run"] = before["run"]
            entry["changed_sections"] = changed_sections(before["sections"], entry["sections"])
            if before.get("own_sections"):
                # 節そのものの本文が変わった節（下位の節の変更で変わっただけの親を含まない）
                entry["changed_own"] = changed_sections(before["own_sections"], entry["own_sections"])
            # 前回、形式不備で意味検査から外した節を持つ対象は、本文が変わっていなくても全体を意味検査する。
            for target in sorted(finding_rules.unchecked_targets(latest) & set(targets)):
                entry["changed_sections"][target] = ["*"]
                entry.setdefault("changed_own", {})[target] = ["*"]
        elif before is not None and latest is not None:
            entry["previous_run"] = before["run"]
            entry["full_inspection"] = "上流の入力が前回の検査から変わった（または比べられない）ため、全体を検査する"
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
        entry = capture(phase_rules.gate_context())
    except (ValueError, OSError) as error:
        phase_rules.fail(str(error))
    phase_rules.ok("inspection snapshot captured", 回数=entry["run"])


if __name__ == "__main__":
    main()
