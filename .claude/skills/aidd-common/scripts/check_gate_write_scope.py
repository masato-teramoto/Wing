"""Enforce immutable artifacts and exactly one undecided appended inspection."""
import l0  # noqa: F401  L0 の枠組みを import できるようにする
import hashlib
from pathlib import Path

import phase_rules
import artifacts
import finding_rules
import findings_stage
import record_format
import snapshot_artifacts


def _merge(rows):
    """同一性キーが同じ指摘を 1 件にまとめる（観点をまたいだ重複）。返り値は (まとめた行, 旧番号→新番号)。"""
    merged, numbers, by_key = [], {}, {}
    for row in rows:
        key = row["同一性キー"]
        if key in by_key:
            first = by_key[key]
            gates = first["観点"].split(" / ")
            for gate in row["観点"].split(" / "):
                if gate not in gates:
                    gates.append(gate)
            first["観点"] = " / ".join(gates)
            if row["指摘内容"] not in first["指摘内容"]:
                first["指摘内容"] += "\n" + row["指摘内容"]
            for name in ("修正案", "確かめ役"):
                if row[name] not in ("", "-") and row[name] not in first[name]:
                    first[name] = row[name] if first[name] in ("", "-") else first[name] + "\n" + row[name]
            if first["推奨"] in ("", "-"):
                first["推奨"] = row["推奨"]
            numbers[row["#"]] = first["#"]
            continue
        row = dict(row, **{"#": str(len(merged) + 1)})
        numbers[row["_number"]] = row["#"]
        by_key[key] = row
        merged.append(row)
    for row in merged:
        row.pop("_number", None)
    return merged, numbers


def _finding_header(block):
    """指摘表の列の並び（見出しの次の最初の表の行）。指摘が 0 件でも列で形を見分ける。"""
    section = None
    for line in block.splitlines():
        line = line.strip()
        if line.startswith(("## ", "### ")):
            section = line.split(" ", 1)[1]
        elif section == "指摘" and line.startswith("|"):
            return record_format.cells(line)
    return None


def check_exclusions(context, rows):
    """除外の出典が実在すること。作った出典で指摘（業務の欠落・矛盾を含む）を外させない。"""
    if not rows:
        return
    import review_premises
    answers = {row["key"] for row in review_premises.confirmed_answers(context)}
    learned = {"%s %s %s-%s" % (r["phase"], r["scope"], r["run"], r["number"]) for r in review_premises.learned(context)}
    for row in rows:
        source = row["除外の出典"].strip()
        prefix = next((p for p in finding_rules.EXCLUSION_SOURCES if source.startswith(p)), None)
        value = source[len(prefix):].strip() if prefix else ""
        if prefix is None:
            raise ValueError("除外の出典は %s のどれかで始める: %s" % (" / ".join(finding_rules.EXCLUSION_SOURCES), source))
        if prefix == "rule:" and value not in finding_rules.BOUNDARY_IDS:
            raise ValueError("工程の境界の表に無い出典: %s" % source)
        if prefix == "answer:" and value not in answers:
            raise ValueError("人が確定した回答に無い出典: %s" % source)
        if prefix == "learned:" and value not in learned:
            raise ValueError("却下から学んだ扱いに無い出典: %s" % source)
        if prefix in ("verify:", "unchecked:") and not value:
            raise ValueError("除外の出典に理由が必要: %s" % source)


def record_block(context, block):
    """検査役の 1 実行ブロックを、記録に追記する形にする。

    種類から重大度を、種類・位置・対象の語から同一性キーを、位置の節から節ハッシュを L3 が計算して埋め、
    同じ指摘をまとめる。旧形式（6 列の指摘表）はそのまま返す。指摘が 0 件でも新しい形の表は記録の形にする。
    何度呼んでも同じ結果になる。
    """
    blocks = record_format.table_blocks(block, staged=True)
    check_exclusions(context, next((rows for name, rows in blocks if name == "除外"), []))
    findings = next((rows for name, rows in blocks if name == "指摘"), None)
    if findings is None or _finding_header(block) == record_format.HEADERS["指摘"]:
        return block
    rows = []
    for row in findings:
        kind = finding_rules.kind_for(row["観点"], row["種類"])
        if kind not in finding_rules.KINDS:
            raise ValueError("指摘の種類は finding-rules の 6 つから選ぶ: #%s %s" % (row["#"], row["種類"]))
        location = row["対象箇所"]
        rows.append(dict(row, **{"_number": row["#"], "種類": kind, "重大度": finding_rules.severity(kind),
                                 "同一性キー": finding_rules.identity_key(kind, location, row["対象の語"]),
                                 "節ハッシュ": finding_rules.section_hash(context.root, location)}))
    merged, numbers = _merge(rows)
    output = []
    for name, table in blocks:
        heading = 2 if name == "実行" else 3
        if name == "実行":
            table = [dict(row, 指摘件数=str(len(merged))) for row in table]
        elif name == "指摘":
            table = merged
        elif name == "差戻し先候補":
            seen, remapped = set(), []
            for row in table:
                row = dict(row, 指摘番号=numbers.get(row["指摘番号"], row["指摘番号"]))
                if (row["指摘番号"], row["宛先"]) not in seen:
                    seen.add((row["指摘番号"], row["宛先"]))
                    remapped.append(row)
            table = remapped
        header = record_format.EXTENDED["指摘"] if name == "指摘" else None
        output.append(record_format.render_table(name, table, heading, header=header).rstrip("\n"))
    return "\n\n".join(output)


def _inspection_end(context, before, suffix, data):
    """記録の末尾が、検査ブロック（suffix）と、その後に system が足した判断・解消だけであること。

    scope-check は封印の後に system の判断・解消を追記する（finding_triage）。その後、L0 が成功を保存する前に
    中断して scope-check をやり直しても、自分の追記を外からの追記と取り違えないようにする。返り値は検査ブロックの終わり。
    """
    start = before["record"]["bytes"]
    if data[start:start + len(suffix)] != suffix:
        raise ValueError("gate record was appended outside the staged inspection")
    rest = data[start + len(suffix):]
    if rest:
        # 名前ではなく中身で確かめる：追記は、自動処理（finding_triage）がこの検査の記録から作るはずの
        # 判断・解消と、日時を除いて一致しなければならない（system を名乗った判断の書き込みを受け付けない）。
        import finding_triage
        record = record_format.parse(data[:start + len(suffix)].decode("utf-8"))
        decisions, resolutions = finding_triage.plan(context, record, record.latest(context.scope), "")
        expected = [(name, rows) for name, rows in (("判断", decisions), ("解消", resolutions)) if rows]
        def comparable(blocks):
            return [(name, [{k: str(v) for k, v in row.items() if k != "日時" and str(v) != ""} for row in rows])
                    for name, rows in blocks]
        if comparable(record_format.table_blocks(rest.decode("utf-8"))) != comparable(expected):
            raise ValueError("gate record was appended outside the staged inspection")
    return start + len(suffix)


def _staged_suffix(context, staged_path):
    block = staged_path.read_text(encoding="utf-8").replace("\r\n", "\n").strip("\n")
    if not block:
        raise ValueError("the inspector's staged block is empty")
    return ("\n" + record_block(context, block).strip("\n") + "\n").encode("utf-8")


def _append_staged(context, before):
    """Append the inspector's staged block exactly once (idempotent across a crash/re-run)."""
    staged_path = Path(snapshot_artifacts.inspection_path(context))
    record_path = Path(context.gate_record)
    data = record_path.read_bytes()
    prefix = before["record"]
    if not staged_path.exists():
        return  # legacy inspector appended directly; validated below
    suffix = _staged_suffix(context, staged_path)
    if len(data) > prefix["bytes"]:
        _inspection_end(context, before, suffix, data)  # 追記済み（中断後のやり直し）
    else:
        record_format.parse((data + suffix).decode("utf-8"))
        temporary = record_path.with_name(record_path.name + ".append.tmp")
        temporary.write_bytes(data + suffix)
        temporary.replace(record_path)
    if not record_format.is_cross_scope(context.scope) and not context.kind:
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
    names = [name for name, _ in appended]
    if names[:2] != ["実行", "指摘"] or names[2:] not in ([], ["差戻し先候補"], ["除外"], ["差戻し先候補", "除外"]):
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
        # まとめた指摘は観点を「 / 」で並べ、本文を改行でつなぐ。機械指摘の本文は改変しない。
        if not any(row["gate"] in f.gate.split(" / ") and row["finding"] in f.description
                   for f in run.findings):
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
    suffix = _staged_suffix(context, staged_path)
    if len(data) > before["record"]["bytes"]:
        return _verify_record(context, before, data[:_inspection_end(context, before, suffix, data)])
    return _verify_record(context, before, data + suffix)


def check(context):
    before = snapshot_artifacts.load(context)
    import implementation_requests
    code = implementation_requests.workspace_code(context)
    if code is not None and before.get('workspace_code') != code:
        raise ValueError('inspector modified implementation workspace files')
    validate_staged(context)
    for relative, previous in before.get("unreviewed", {}).items():
        if snapshot_artifacts.body_digest(context.path(relative)) != previous["sha256"]:
            raise ValueError("protected artifact changed: %s" % relative)
        # Not inspected, so no status transition is authorized (not even to review/approved).
        if (artifacts.fields(context.path(relative)) or {}).get("status") != previous["status"]:
            raise ValueError("unauthorized status change of an unreviewed artifact: %s" % relative)
    for relative, previous in before["artifacts"].items():
        target = context.path(relative)
        if phase_rules.inspection_digest(context, relative) != previous["sha256"]:
            raise ValueError("protected artifact changed: %s" % relative)
        if context.kind:
            continue
        status = (artifacts.fields(target) or {}).get("status")
        allowed = (previous["status"], "review") if previous["status"] in ("draft", "review") else (previous["status"],)
        if status not in allowed:
            raise ValueError("unauthorized status transition: %s" % relative)
    _append_staged(context, before)
    data = Path(context.gate_record).read_bytes()
    staged_path = Path(snapshot_artifacts.inspection_path(context))
    if staged_path.exists():
        data = data[:_inspection_end(context, before, _staged_suffix(context, staged_path), data)]
    run = _verify_record(context, before, data)
    import reevaluation
    reevaluation.check_run(context, before, run)
    return run


def main():
    try:
        context = phase_rules.gate_context()
        run = check(context)
        import inspection_seal
        inspection_seal.save(context, run)
        # 封印の後に、人に出す前の機械の処理（前回却下済み・軽微・再検査による解消）を記録する。
        import finding_triage
        finding_triage.apply(context)
    except (ValueError, OSError) as error:
        phase_rules.fail(str(error))
    phase_rules.ok("gate write scope is intact", 回数=run.number, 指摘=run.count)


if __name__ == "__main__":
    main()
