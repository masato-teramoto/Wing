"""L3 human-review actions. No Skill/agent dispatch or runner imports."""
import l0  # noqa: F401  L0 の枠組みを import できるようにする
import json

import artifacts
import phase_rules
import finding_rules
import project_state
import record_format
import review_contract
import review_operations
import snapshot_artifacts


def person(value):
    if not record_format.filled(value):
        raise ValueError("the actual human respondent is required")
    if str(value).strip().startswith(finding_rules.SYSTEM_ACTOR):
        raise ValueError("the respondent must be a person, not %s" % finding_rules.SYSTEM_ACTOR)
    return value


def finding(record, scope, run, number):
    return next((f for r in record.runs for f in r.findings
                 if f.key == (scope, int(run), int(number))), None)


def decision(context, scope, run, number, value, reason, actor, *, expected=None, operation_id=None,
             category="", learn=False, adopted=""):
    """category: 却下区分（対応せず進める）。learn: 今後も同じ扱い。adopted: AI 推奨の 採用／不採用。"""
    data = {'scope':scope,'run':run,'number':number,'decision':value,'reason':reason}
    if category or learn or adopted:
        data.update(category=category, learn=bool(learn), adopted=adopted)
    return review_operations.execute(context,'decision',data,actor,expected,operation_id,
        lambda: _decision(context,scope,run,number,value,reason,actor,category,learn,adopted))


def _decision(context, scope, run, number, value, reason, actor, category="", learn=False, adopted=""):
    record = review_contract.read(context)
    if scope not in review_contract.scopes(context):
        raise ValueError('finding is outside the current review scope')
    selected = finding(record, scope, run, number)
    if selected is None or selected not in record.relevant(scope):
        raise ValueError("finding does not exist in the current review")
    row = {"スコープ": scope, "回数": run, "指摘番号": number,
           "判断": value, "理由": reason, "判断者": person(actor), "日時": project_state.now()}
    if category or learn or adopted:
        row.update({"却下区分": finding_rules.rejection(category), "今後も同じ扱い": "はい" if learn else "",
                    "推奨の採用": adopted})
    return [review_operations.record_effect(context, "判断", [row])]


def resolve(context, scope, run, number, actor, *, expected=None, operation_id=None):
    data = {'scope':scope,'run':run,'number':number}
    return review_operations.execute(context,'resolve',data,actor,expected,operation_id,
        lambda: _resolve(context,scope,run,number,actor))


def _resolve(context, scope, run, number, actor):
    if context.is_implementation:
        import implementation_repair
        implementation_repair.resolution_ready(context, scope, run, number)
    inclusive = None
    if scope not in review_contract.scopes(context):
        # 部分集合のスコープの指摘は、対象を包含する全件スコープの後続検査回で解消できる（§6.4 の持越し・解消）。
        kind, name = record_format.scope_parts(scope)
        full = record_format.scope_of(kind)
        if not (name and kind in ("cross", "phase") and full in review_contract.scopes(context)):
            raise ValueError('finding is outside the current review scope')
        inclusive = full
    for blocker in context.blockers():
        selected = blocker.get('finding') or {}
        if (selected.get('phase') == context.process
                and (selected.get('scope'),selected.get('run'),selected.get('number')) == (scope,run,number)
                and blocker.get('status') == 'open'):
            raise ValueError('rollback needs upstream reapproval before resolution')
    record = review_contract.read(context)
    original = finding(record, scope, run, number)
    current = review_contract.inspection(context, record, inclusive or scope)
    if original is None or original.decision not in ("修正", "差戻し") or original.resolved:
        raise ValueError("an unresolved human correction decision is required")
    if inclusive:
        source = next((r for r in record.runs if r.scope == scope and r.number == int(run)), None)
        if source is None or record.runs.index(current) < record.runs.index(source):
            raise ValueError("reinspection after the finding is required")
    elif current.number <= int(run):
        raise ValueError("reinspection after the finding is required")
    return [review_operations.record_effect(context, "解消", [{"スコープ": scope, "回数": run, "指摘番号": number,
                           "再検査スコープ": inclusive or scope, "再検査回数": current.number,
                           "確認者": person(actor), "日時": project_state.now()}])]


def approve(context, actor, *, expected=None, operation_id=None):
    return review_operations.execute(context,'approve',{},actor,expected,operation_id,
        lambda: _approve(context,actor))


def remaining_rows(context, record, run):
    """Findings approved while still 未対応 / 対応せず進める (alpha2「承認時の残件」)."""
    rows = []
    for scope in review_contract.scopes(context):
        runs = [r for r in record.runs if r.scope == scope]
        for index, earlier in enumerate(runs):
            later = {f.identity for r in runs[index + 1:] for f in r.findings if f.identity}
            for f in earlier.findings:
                if f.decision not in ("対応せず進める", "未対応") or f.resolved:
                    continue
                if earlier is not runs[-1] and not f.identity and not f.is_carried:
                    continue  # 旧形式の前の回の却下は、同じ問題か比べられないので従来どおり載せない
                # 後の回に同じ指摘（同一性キー）があれば、そちらで数える
                if f.identity and f.identity in later:
                    continue
                rows.append({"スコープ": f.scope, "回数": f.run, "指摘番号": f.number, "判断": f.decision,
                             "理由": f.reason, "承認スコープ": run.scope, "承認回数": run.number})
    return rows


def _approve(context, actor):
    person(actor)
    migration = context.state().get("workflow", {}).get("migration", {})
    if migration.get("status") == "review-required" and context.process not in migration.get("reviewed_phases", []):
        raise ValueError("legacy records require explicit migration reconciliation before approval")
    record = review_contract.ready(context)
    if context.is_cross:
        run = review_contract.inspection(context, record, context.scope)
        if any(row['スコープ']==run.scope and int(row['回数'])==run.number for row in record.confirmations):
            raise ValueError('this inspection is already confirmed; retry the original operation ID')
        effect = review_operations.record_effect(context, "確認", [{"スコープ": run.scope, "回数": run.number, "確認者": actor,
                               "日時": project_state.now(), "原本SHA256": json.dumps(run.hashes, ensure_ascii=False)}])
        effects = [effect]
        rest = remaining_rows(context, record, run)
        if rest:
            effects.append(review_operations.record_effect_after(context, [effect], "残件", rest))
        cross = {'kind': 'cross'}
        if context.selection:
            # 比較相手の内訳（§6.4 の scope 記録）。判定は実行行の対象・hash で行い、これは監査用の記録。
            cross.update(scope=run.scope, run=run.number, targets=list(run.targets))
        return effects + [cross]
    run = review_contract.inspection(context, record, context.scope)
    targets = context.approval_targets()
    snapshot = snapshot_artifacts.load(context)
    for target in targets:
        if context.kind:
            if review_contract.approval_for(record, run, target):
                raise ValueError('this feature inspection is already approved')
            continue
        status = artifacts.fields(context.path(target)).get("status")
        # Final tasks review may combine a revised item and unchanged approved
        # items. Only an approval already present at the snapshot is admissible.
        if status != "review" and not (status == "approved" and snapshot['artifacts'][target]['status'] == 'approved'):
            raise ValueError("only inspected review artifacts can be approved: " + target)
        if review_contract.approval_for(record,run,target):
            raise ValueError('this inspection is already approved; retry the original operation ID')
    at = project_state.now()
    rows = [{"スコープ": run.scope, "回数": run.number, "対象成果物": target,
             "承認者": actor, "承認日時": at, "原本SHA256": run.hashes[target]} for target in targets]
    effects = [review_operations.record_effect(context, "承認", rows)]
    rest = remaining_rows(context, record, run)
    if rest:
        effects.append(review_operations.record_effect_after(context, effects, "残件", rest))
    if context.kind:
        return effects
    return effects + [
        review_operations.status_effect(context,target,'approved',at) for target in targets
        if artifacts.fields(context.path(target)).get('status') != 'approved']


def prepare_response(context, operation, data, actor):
    """Validate every human effect without saving anything."""
    if operation == 'approve':
        return _approve(context,actor)
    if operation == 'decision':
        return _decision(context,data['scope'],data['run'],data['number'],data['decision'],data.get('reason',''),actor,
                         data.get('category',''),data.get('learn',False),data.get('adopted',''))
    if operation == 'resolve':
        return _resolve(context,data['scope'],data['run'],data['number'],actor)
    raise ValueError('unsupported review action')


def check_cross(context, process, selection=""):
    """工程 process の横断確認の有効な確認。selection が空なら全件（cross）、あれば cross:<selection>。

    selection の前提は、現在の内容と一致して確認済みの全件 cross でも満たす（U ⊇ C(p)。計画 v3 §6.1 の引継ぎ (2)）。
    逆（selection の確認で全件の前提を満たすこと）は認めない。
    """
    if selection:
        state, reason = selection_cross_state(context, process, selection)
        if state in ("valid", "stale"):
            return None  # 「古い」は案内だけで前提を止めない（§6.7）
        try:
            return _check_cross(context, process, "")
        except (ValueError, OSError, KeyError):
            raise ValueError("cross inspection %s:%s is %s: %s" % (process, selection, state, reason)) from None
    return _check_cross(context, process, "")


def _feature_of_target(path):
    parts = path.split("/")
    return parts[1] if len(parts) > 2 and parts[0] == "specs" else ""


def selection_cross_state(context, process, selection):
    """`cross:<selection>` の状態（§6.7）。('valid' | 'stale' | 'invalid' | 'missing', 理由)。

    今の C(p) と比べる `inspection()` は使わない（利用側が増えるだけで止まるため）。最新の確認済みの回の
    対象と hash のうち、S と依存先 D の分だけを今と比べ、違えば invalid。利用側 Cons の分の差
    （増減・内容の変化）は stale とする。前提を止めるのは invalid と missing だけ。
    """
    from phase_rules import ExecutionContext
    import feature_scope
    import project_progress
    upstream = ExecutionContext(context.root, context.state_path, process + "-cross-gate", selection)
    if project_progress.cross_key(process, selection) in context.state().get("workflow", {}).get("invalidated_cross", []):
        return "invalid", "invalidated"
    try:
        record = review_contract.read(upstream)
    except (OSError, ValueError):
        return "missing", "no gate record"
    scope = upstream.scope
    run = None
    for row in reversed(record.confirmations):
        if row["スコープ"] != scope:
            continue
        found = next((r for r in record.runs if r.scope == scope and r.number == int(row["回数"])), None)
        if found is not None and json.loads(row["原本SHA256"]) == found.hashes:
            run = found
            break
    if run is not None:
        targets, hashes = list(run.targets), dict(run.hashes)
    else:
        # 切替後で cross:<P> をまだ実施していない P は、切替記録の基準の確認で判定する（§6.1 の引継ぎ (2)）。
        baseline = ((context.state().get("workflow", {}).get("mode_switch") or {}).get("baselines") or {}).get(process, {}).get(selection)
        if not baseline:
            return "missing", "no confirmed selection round"
        targets, hashes = list(baseline["targets"]), dict(baseline["hashes"])
    core = {selection, *feature_scope.closure(upstream, selection)}
    current = review_contract.targets_for(upstream, scope)
    recorded_core = sorted(t for t in targets if _feature_of_target(t) in core)
    current_core = sorted(t for t in current if _feature_of_target(t) in core or not _feature_of_target(t))
    if recorded_core != sorted(t for t in current_core if _feature_of_target(t)):
        return "invalid", "selection or dependency targets changed"
    for target in recorded_core:
        if hashes.get(target) != phase_rules.inspection_digest(upstream, target):
            return "invalid", "changed since confirmation: " + target
    # 比較相手は selection を推移的に依存先に持つ利用側だけ（全件の回を基準にした場合の無関係な feature は比べない）。
    users = set(feature_scope.dependents(upstream, selection)) - core
    recorded_cons = {t: hashes.get(t) for t in targets if _feature_of_target(t) in users}
    current_cons = {t: phase_rules.inspection_digest(upstream, t) for t in current if _feature_of_target(t) in users}
    if recorded_cons != current_cons:
        return "stale", "comparison targets changed"
    return "valid", ""


def _check_cross(context, process, selection):
    from phase_rules import ExecutionContext
    upstream = ExecutionContext(context.root, context.state_path, process + "-cross-gate", selection)
    import project_progress
    if project_progress.cross_key(process, selection) in context.state().get("workflow", {}).get("invalidated_cross", []):
        raise ValueError("cross inspection was invalidated and must be repeated: " + process)
    record = review_contract.ready(upstream)
    run = review_contract.inspection(upstream, record, upstream.scope)
    # 確認行は同じスコープ・同じ回の行だけを認める（別スコープの同じ回数・同じ hash を流用しない）。
    confirmation = next((row for row in reversed(record.confirmations) if row["スコープ"] == run.scope
                         and int(row["回数"]) == run.number and json.loads(row["原本SHA256"]) == run.hashes), None)
    if not confirmation:
        raise ValueError("current cross inspection requires human confirmation: " + process)
