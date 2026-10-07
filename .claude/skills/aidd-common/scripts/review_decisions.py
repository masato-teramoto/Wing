"""L3 human-review actions. No Skill/agent dispatch or runner imports."""
import l0  # noqa: F401  L0 の枠組みを import できるようにする
import json

import artifacts
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
    if context.process == 'implement':
        import implementation_repair
        implementation_repair.resolution_ready(context, scope, run, number)
    if scope not in review_contract.scopes(context):
        raise ValueError('finding is outside the current review scope')
    for blocker in context.blockers():
        selected = blocker.get('finding') or {}
        if (selected.get('phase') == context.process
                and (selected.get('scope'),selected.get('run'),selected.get('number')) == (scope,run,number)
                and blocker.get('status') == 'open'):
            raise ValueError('rollback needs upstream reapproval before resolution')
    record = review_contract.read(context)
    original = finding(record, scope, run, number)
    current = review_contract.inspection(context, record, scope)
    if original is None or original.decision not in ("修正", "差戻し") or original.resolved:
        raise ValueError("an unresolved human correction decision is required")
    if current.number <= int(run):
        raise ValueError("reinspection after the finding is required")
    return [review_operations.record_effect(context, "解消", [{"スコープ": scope, "回数": run, "指摘番号": number,
                           "再検査スコープ": scope, "再検査回数": current.number,
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
        run = review_contract.inspection(context, record, "cross")
        if any(row['スコープ']=='cross' and int(row['回数'])==run.number for row in record.confirmations):
            raise ValueError('this inspection is already confirmed; retry the original operation ID')
        effect = review_operations.record_effect(context, "確認", [{"スコープ": "cross", "回数": run.number, "確認者": actor,
                               "日時": project_state.now(), "原本SHA256": json.dumps(run.hashes, ensure_ascii=False)}])
        effects = [effect]
        rest = remaining_rows(context, record, run)
        if rest:
            effects.append(review_operations.record_effect_after(context, [effect], "残件", rest))
        return effects + [{'kind':'cross'}]
    run = review_contract.inspection(context, record, context.scope)
    targets = context.review_targets()
    snapshot = snapshot_artifacts.load(context)
    for target in targets:
        if context.process == 'implement':
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
    if context.process == 'implement':
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


def check_cross(context, process):
    from phase_rules import ExecutionContext
    upstream = ExecutionContext(context.root, context.state_path, process + "-cross-gate")
    if process in context.state().get("workflow", {}).get("invalidated_cross", []):
        raise ValueError("cross inspection was invalidated and must be repeated: " + process)
    record = review_contract.ready(upstream)
    run = review_contract.inspection(upstream, record, "cross")
    confirmation = next((row for row in reversed(record.confirmations) if int(row["回数"]) == run.number and json.loads(row["原本SHA256"]) == run.hashes), None)
    if not confirmation:
        raise ValueError("current cross inspection requires human confirmation: " + process)
