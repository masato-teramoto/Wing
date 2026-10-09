"""全件方式 → Feature 方式の切替（`/aidd-mode-switch`、1 回限り。計画 v3 §6.1「方式の切替」）。

script として呼ばれたとき（action `mode-switch-confirm`）は確認表示を出すだけで、何も変えない。
確定は host 操作 `switch-mode`（`{"confirm": true, ...}`）で行う。入口 Skill が確認表示を人に示し、
人が確定と回答したときだけ呼ぶ。確定しなければ何も変えない。

切替記録（`workflow.mode_switch`、追記のみ）：
`{operation_id, actor, at, reason, from: "all", phase_snapshot, carried, baselines, owner}`
- `baselines[<process>][<P>]`：Platform の P ごとの基準の確認（§6.1 の引継ぎ (2)）。引き継ぐ全件 cross の
  確認済みの回の回数・対象・hash。P が `cross:<P>` を一度実施するまで `cross:<P>` の確認の代わりになり、
  有効性は P と依存先 D の hash で判定する（review_decisions.selection_cross_state）。
- `owner`：smoke wrapper の owner（§6.1 の引継ぎ (7)）。
"""
import l0  # noqa: F401
import json
from pathlib import Path

import phase_rules
import project_state
import record_format

FULL_CROSS = record_format.scope_of("cross")

CROSS_PROCESSES = ("requirements", "design")


def _workflow(context):
    value = context.state().get("workflow", {})
    return value if isinstance(value, dict) else {}


def _confirmed_full_cross(context, process):
    """工程 process の全件 cross の、確認済みの最新の回（無ければ None）。"""
    import review_contract
    gate = phase_rules.ExecutionContext(context.root, context.state_path, process + "-cross-gate", "")
    try:
        record = review_contract.read(gate)
    except (OSError, ValueError):
        return None
    for row in reversed(record.confirmations):
        if row["スコープ"] != FULL_CROSS:
            continue
        run = next((r for r in record.runs if r.scope == FULL_CROSS and r.number == int(row["回数"])), None)
        if run is not None and json.loads(row["原本SHA256"]) == run.hashes:
            return run
    return None


def _feature_of(path):
    parts = path.split("/")
    return parts[1] if len(parts) > 2 and parts[0] == "specs" else ""


def _artifacts(context):
    return sorted(p.relative_to(context.root).as_posix() for p in Path(context.root, "specs").rglob("*.md"))


def owner_candidates(context):
    """smoke wrapper の owner の候補（§6.11 の「適用範囲」(2)）。一覧の種別・依存から機械的に決める。"""
    import feature_scope
    entries = context.features()
    platforms = {e["name"] for e in entries if e["kind"] == "Platform"}
    users = [e["name"] for e in entries if e["kind"] != "Platform"]
    dependent = [n for n in users if platforms & set(feature_scope.closure(context, n))]
    return dependent or users


def owner_of(context):
    import implementation_project
    return implementation_project.owner_record(context)["owner"]


def _reasons(context):
    """切替を止めている残作業（許可条件のうち満たしていないもの）。"""
    import feature_scope
    data = _workflow(context)
    state = context.state()
    reasons = []
    if data.get("mode_switch_pending"):
        return []  # 前回の確定が途中で止まった：確定し直せば続きから終える
    current = feature_scope.mode(context)
    if current is None:
        reasons.append("方式が未決定です（最初の requirements-plan の了承前）。Phase 4 に入ってから切り替えます")
    elif current == "feature":
        reasons.append("すでに Feature 方式です（逆方向と 2 回目の切替はできません）")
    if data.get("mode_switch"):
        reasons.append("切替は 1 回限りで、すでに切り替えています")
    pending = (state.get("current") or {}).get("pending")
    if pending:
        reasons.append("未回答の待機（dispatch）があります: %s[%s]" % (pending.get("event"), pending.get("item") or "-"))
    if any((entry or {}).get("status") != "finished" for entry in (state.get("host_operations") or {}).values()):
        reasons.append("終わっていない host 操作があります")
    review = [p for p in _artifacts(context) if phase_rules.status_of(context.path(p)) == "review"]
    review += [p for p in ("docs/code-design.md", "docs/architecture/data-model.md", "docs/architecture/system-overview.md")
               if Path(context.path(p)).exists() and phase_rules.status_of(context.path(p)) == "review"]
    if review:
        reasons.append("承認待ち（review）の成果物があります: " + ", ".join(review))
    import review_contract
    for process in CROSS_PROCESSES:
        gate = phase_rules.ExecutionContext(context.root, context.state_path, process + "-cross-gate", "")
        try:
            record = review_contract.read(gate)
        except (OSError, ValueError):
            continue
        latest = record.latest(FULL_CROSS)
        if latest is not None and not any(r["スコープ"] == FULL_CROSS and int(r["回数"]) == latest.number for r in record.confirmations):
            reasons.append("%s の全件の横断確認が人間確認待ちです（%d 回目）" % (process, latest.number))
    if (data.get("manifest_change") or {}).get("needs_replan"):
        reasons.append("feature 一覧の差戻し中（上流差戻し）です")
    reasons += _phase8_reasons(context)
    return reasons


def phase8_features(context):
    """Phase 8 に着手済みの feature（state.json があるもの）と、実装承認行の有無。"""
    import implementation_requests as requests
    import review_contract
    import implementation_store as store
    found = {}
    for entry in context.features():
        if not Path(context.path(requests.feature_path(entry["name"]))).is_file():
            continue
        final = phase_rules.ExecutionContext(context.root, context.state_path, phase_rules.IMPLEMENT_REVIEW, entry["name"])
        try:
            record = review_contract.read(final)
            found[entry["name"]] = any(row["スコープ"] == final.scope for row in record.approvals)
        except (OSError, ValueError):
            found[entry["name"]] = False
    return found


def _phase8_reasons(context):
    """Phase 8 の引継ぎの条件（§6.1 の引継ぎ (5)(6)）。承認済みは旧方式の照合が通ること、途中は実行中でないこと。"""
    import implementation_store as store
    import review_contract
    reasons = []
    for name, approved in phase8_features(context).items():
        if approved:
            final = phase_rules.ExecutionContext(context.root, context.state_path, phase_rules.IMPLEMENT_REVIEW, name)
            try:
                review_contract.check_approved(final)
            except (ValueError, OSError, KeyError) as error:
                reasons.append("実装承認済みの %s が旧方式の照合を通りません（切替前に repair／rebase で整えます）: %s" % (name, error))
    for path in Path(context.path(store.BASE + "/runs")).glob("*/execution.json"):
        execution = store.read(context.root, path.relative_to(context.root).as_posix())
        if execution.get("activated") and not execution.get("event_complete"):
            reasons.append("実行中のタスクがあります: %s のタスク %s" % (execution.get("feature"), execution.get("task_id")))
    return reasons


def _phase8_before(context):
    """切替前（旧方式）の照合値。承認済みは review.json の inputs・protected、途中は state.json の inputs。"""
    import implementation_requests as requests
    import implementation_evidence as evidence
    import implementation_store as store
    values = {}
    for name, approved in phase8_features(context).items():
        if approved:
            review = store.read(context.root, evidence.review_path(name))
            values[name] = {"inputs": review["inputs"], "protected": review["protected"]}
        else:
            values[name] = {"inputs": requests.feature_state(context, name)["inputs"]}
    return values


def _phase8_pairs(context, before):
    """切替後（新方式）の照合値との対応（§6.1 の引継ぎ (5)）。verify_review と select はこの対応で同値とみなす。"""
    import implementation_requests as requests
    import implementation_evidence as evidence
    pairs = {}
    for name, old in before.items():
        rows = [{"from": old["inputs"], "to": requests.input_signature(context, name)}]
        if "protected" in old:
            rows.append({"from": old["protected"], "to": evidence.review_protected(context, name)})
        pairs[name] = rows
    return pairs


def preview(context):
    """確認表示（§6.1 の (1)）。何も変えない。"""
    entries = context.features()
    approved = {kind: [e["name"] for e in entries if phase_rules.status_of(context.path("specs/%s/%s.md" % (e["name"], kind))) == "approved"]
                for kind in ("requirements", "design", "tasks")}
    carried = {"approved": approved,
               "full_cross": {p: (run.number if (run := _confirmed_full_cross(context, p)) else None) for p in CROSS_PROCESSES},
               "phase8": phase8_features(context)}
    candidates = owner_candidates(context)
    owner_required = not owner_of(context) and any(Path(context.path("specs/%s/tasks.md" % n)).exists() for n in candidates)
    reasons = _reasons(context)
    if _workflow(context).get("mode_switch_pending"):
        text = ("**前回の切替の確定が途中で止まっています。** 確定し直すと、前回の内容（%s の確定）のまま続きから終えます。"
                "終えるまで他の操作は止まります。" % _workflow(context)["mode_switch_pending"].get("actor", "—"))
        return {"allowed": True, "reasons": [], "carried": _workflow(context)["mode_switch_pending"].get("carried", {}),
                "owner_required": False, "owner_candidates": [], "text": text}
    lines = ["**全件方式から Feature 方式へ切り替えます（1 回限り。戻せません）。**", "",
             "### 引き継ぐもの（再承認なし）"]
    for kind, names in approved.items():
        lines.append("- 承認済みの %s：%s" % (kind, "、".join(names) or "なし"))
    for process, number in carried["full_cross"].items():
        lines.append("- 全件の %s 横断確認：%s" % (process, ("%d 回目（Platform ごとの基準の確認として引き継ぐ）" % number) if number else "なし"))
    for name, done in carried["phase8"].items():
        lines.append("- Phase 8 の %s：%s" % (name, "実装承認済み（review.json を書き換えず、切替記録の対応で照合する）" if done
                                             else "途中（残タスクを持ったまま続ける。次の /aidd-implement で implement-plan[%s] が 1 回出る）" % name))
    lines += ["", "### 引き継がないもの", "- 工程単位の計画了承（最初の select-scope で、選択 feature ごとの了承になります）", ""]
    if owner_required:
        lines += ["### smoke wrapper の owner（選ばないと確定できません）",
                  "- 候補：" + "、".join(candidates),
                  "- owner を選ぶと、その feature の tasks に結合確認タスクを足す修正を起こし、tasks-gate-run[owner] だけを再承認します。"
                  "業務 API を持つ feature が無いときは「候補なし」と理由を答えます", ""]
    if reasons:
        lines += ["### 切替を止めている残作業"] + ["- " + r for r in reasons] + [""]
    else:
        lines += ["確定するときは、確定の回答と理由を返してください。確定しなければ何も変えません。"]
    return {"allowed": not reasons, "reasons": reasons, "carried": carried, "owner_required": owner_required,
            "owner_candidates": candidates, "text": "\n".join(lines)}


def _baselines(context):
    import feature_scope
    result = {}
    for process in CROSS_PROCESSES:
        run = _confirmed_full_cross(context, process)
        if run is None:
            continue
        for entry in context.features():
            if entry["kind"] != "Platform":
                continue
            result.setdefault(process, {})[entry["name"]] = {
                "run": run.number, "targets": list(run.targets), "hashes": dict(run.hashes),
                "comparison_targets": sorted({_feature_of(t) for t in run.targets if _feature_of(t)})}
    return result


def switch(context, data, actor):
    """確定（§6.1 の (2)）：mode を feature に書き、切替記録を残す。許可条件を満たさなければ何も変えない。"""
    import review_decisions
    import feature_scope
    review_decisions.person(actor)
    if data.get("confirm") is not True:
        raise ValueError("確定の回答（confirm: true）が無いので、何も変えません")
    pending = _workflow(context).get("mode_switch_pending")
    if pending:
        return _finish(context, pending)  # 前回の確定が途中で止まった：続きから終える
    view = preview(context)
    if not view["allowed"]:
        raise ValueError("切替できません: " + " / ".join(view["reasons"]))
    owner = data.get("owner") or ""
    if view["owner_required"]:
        if owner == "候補なし":
            if not str(data.get("owner_reason") or "").strip():
                raise ValueError("「候補なし」には理由が必要です")
        elif owner not in view["owner_candidates"]:
            raise ValueError("smoke wrapper の owner を候補から選んでください: " + "、".join(view["owner_candidates"]))
    # 1 段目：切替前に計算できるものを全部計算し、mode と途中の記録を 1 回で保存する（失敗したら何も変わらない）。
    pre = {"operation_id": data.get("operation_id") or "", "actor": actor, "at": project_state.now(),
           "reason": data.get("reason", ""), "from": "all",
           "phase_snapshot": {kind: {e["name"]: phase_rules.status_of(context.path("specs/%s/%s.md" % (e["name"], kind))) or "未着手"
                                     for e in context.features()} for kind in ("requirements", "design", "tasks")},
           "carried": view["carried"], "baselines": _baselines(context), "phase8_before": _phase8_before(context),
           "unchanged": feature_scope.switch_unchanged_inputs(context),
           "owner": owner, "owner_reason": data.get("owner_reason", ""), "owner_required": view["owner_required"]}
    current = dict(_workflow(context))
    current.update(mode="feature", mode_switch_pending=pre)
    project_state.update(context.state_path, {"workflow": current})
    return _finish(context, pre)


def _finish(context, pre):
    """2 段目：mode=feature の下で新しい形式の値を計算し、切替記録・記録入力・owner を 1 回で保存する。
    途中で失敗しても、mode_switch_pending が残るので、switch-mode を呼び直すとここから終える。"""
    import feature_scope
    inputs = feature_scope.rebase_inputs_after_switch(context, pre["unchanged"])  # §6.1 の引継ぎ (8)
    owner = pre["owner"]
    record = {key: pre[key] for key in ("operation_id", "actor", "at", "reason", "from", "phase_snapshot", "carried", "baselines")}
    record.update(rebased=pre["unchanged"], owner=owner if owner != "候補なし" else "", owner_reason=pre["owner_reason"],
                  phase8=_phase8_pairs(context, pre["phase8_before"]))  # 新方式の照合値（§6.1 の引継ぎ (5)(6)）
    current = dict(_workflow(context))
    current["inputs"] = dict(current.get("inputs") or {}, **inputs)
    current["mode_switch"] = record
    current.pop("mode_switch_pending", None)
    if pre["owner_required"]:
        # owner の正本（計画了承の外、§6.11）。「候補なし」は理由とともに残す。
        current["smoke_owner"] = {"owner": owner, "owner_reason": pre["owner_reason"], "actor": pre["actor"],
                                  "at": pre["at"], "source": "switch-mode"}
    if record["owner"] and Path(context.path("specs/%s/tasks.md" % owner)).exists():
        # owner の tasks の修正の要求は保留して、次の audit で起こす（mode を書いた後なので blocker の範囲が付く。§6.1 の引継ぎ (7)）。
        current["owner_reopen"] = {"owner": owner, "actor": pre["actor"]}
    project_state.update(context.state_path, {"workflow": current})
    return {"switched": True, "record": record}


def main():
    context = phase_rules.ExecutionContext()
    try:
        view = preview(context)
    except (ValueError, OSError, KeyError) as error:
        phase_rules.fail(str(error))
    phase_rules.ok(view["text"])


if __name__ == "__main__":
    main()
