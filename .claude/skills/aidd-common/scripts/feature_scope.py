"""Feature 方式の方式（mode）・選択（S）・集合の判定（計画 v3 §6.1・§6.2・§6.8・§6.10 C4）。

判定はここに集め、各所は呼ぶだけにする。全件方式（mode `all`、および mode の無い旧案件）では
どの関数も現行の動作を変えない値を返す。状態は L3 所有の `workflow` 欄だけに書く（L0 所有欄は触らない）。

`workflow` 欄に書くもの（記録形式はコンバーター向けに段階 0 の検証記録で文書化する）：
- `mode`：`all` / `feature`。最初の `requirements-plan`（item 無し）を了承したときに必ず書く。
- `selection`：`{feature, actor, at, note}`。人の選択事実。`selection_history` に追記する。
- `accepted_plans[<process>]['items'][<S>]`：Feature 方式の計画停止点の了承（D-9）。
"""
import l0  # noqa: F401  L0 の枠組みを import できるようにする
from pathlib import Path

import artifacts
import feature_manifest
import phase_rules
import project_state

MODES = ("all", "feature")
PLAN_PROCESSES = ("requirements", "design", "tasks")
OWNER_REOPEN = "smoke wrapper の結合確認タスクを足す（owner に選ばれた）"


def _workflow(context):
    value = context.state().get("workflow", {})
    return value if isinstance(value, dict) else {}


def mode(context):
    """`all` / `feature`、未決定なら None。了承済みで mode の無い旧案件は全件方式（R3）。不正な値は止める。"""
    data = _workflow(context)
    value = data.get("mode")
    if value is None:
        return "all" if (data.get("accepted_plans") or {}).get("requirements") or _legacy_progress(context, data) else None
    if value not in MODES:
        raise ValueError("workflow.mode が不正です（%r）。自動で全件方式へ戻さないので、復旧してください" % (value,))
    return value


def _legacy_progress(context, data):
    """mode の無い案件が Phase 4 以降を進めた痕跡（計画了承を失った旧案件も全件方式とみなす。R3）。

    痕跡にするのは、計画の了承の後にしかできないものだけ：計画停止点以外の Phase 4〜8 の action の記録入力・
    結果・完了の記録、全件再計画の印（invalidation）、作成済みの requirements／design／tasks。
    最初の requirements-plan の記録入力（了承の前の preflight で書く）と一覧の変更の記録（Phase 3 でもできる）は
    使わない（新規案件の方式の選択を全件方式に決めつけない）。
    """
    if data.get("invalidation"):
        return True
    for key in [*(data.get("inputs") or {}), *(data.get("results") or {}), *(data.get("completions") or {})]:
        action = key.split("[", 1)[0]
        process = phase_rules.PROCESS_OF.get(action)
        if process and phase_rules.RULES[process]["number"] >= 4 and not action.endswith("-plan"):
            return True
    return any(next(Path(context.root, "specs").glob("*/%s.md" % kind), None) is not None for kind in PLAN_PROCESSES)


def settle_mode(context):
    """mode の無い了承済みの旧案件（R3）の全件方式を状態に書く。推定の根拠（requirements の計画了承）は
    一覧の構造変更・全件再計画で消えるので、消す前に書いておく（消えた後に方式の選択が出て、
    /aidd-mode-switch を通らずに Feature 方式へ入れてしまうのを防ぐ）。"""
    data = _workflow(context)
    if data.get("mode") is None and mode(context) == "all":
        current = dict(data)
        current["mode"] = "all"
        project_state.update(context.state_path, {"workflow": current})


def require_no_pending_switch(context):
    """方式切替の確定が途中で止まっている間は進めない（記録入力が旧形式のまま開き直しが走るのを防ぐ）。"""
    if _workflow(context).get("mode_switch_pending"):
        raise ValueError("方式切替の確定が途中で止まっています。/aidd-mode-switch で確定し直すと続きから終えます")


def is_feature(context):
    return mode(context) == "feature"


def selection(context):
    value = _workflow(context).get("selection")
    if value is None:
        return ""
    if not isinstance(value, dict) or not isinstance(value.get("feature"), str):
        raise ValueError("Feature 方式の選択記録が壊れています。自動で推測しないので、復旧してください")
    return value["feature"]


# --- 集合（§6.2）-------------------------------------------------------------

def _entries(context):
    return {entry["name"]: entry for entry in context.features()}


def closure(context, name):
    """name の推移的依存先 D（一覧順）。"""
    entries = _entries(context)
    if name not in entries:
        raise ValueError("feature not in approved manifest: " + name)
    found, pending = set(), list(entries[name]["depends_on"])
    while pending:
        current = pending.pop()
        if current not in found:
            found.add(current)
            pending.extend(entries[current]["depends_on"])
    return [n for n in entries if n in found]


def dependents(context, name):
    """name を推移的依存先に持つ feature（利用側、一覧順）。"""
    return [n for n in _entries(context) if name in closure(context, n)]


def plan_features(context, process, name):
    """計画停止点 `<process>-plan[S]` の `{features}`：S ∪ D。requirements は D を前提にしないので S だけ（D-1）。"""
    if process == "requirements":
        return [name]
    members = {name, *closure(context, name)}
    return [n for n in _entries(context) if n in members]


def consumers(context, process, name):
    """Cons(p)：S が Platform のとき、工程 p の成果物が approved の利用側（status は候補の絞り込みだけ）。"""
    entries = _entries(context)
    if entries[name]["kind"] != "Platform":
        return []
    outputs = [p for p in phase_rules.config()["rules"][process]["outputs"] if "{feature}" in p]
    return [n for n in dependents(context, name)
            if outputs and all(phase_rules.status_of(context.path(p.replace("{feature}", n))) == "approved" for p in outputs)]


def current_feature(context):
    """この action が扱う feature（blocker の範囲判定用）。feature を持たない action は空。"""
    if context.kind:
        import implementation_requests
        try:
            return implementation_requests.feature_of(context)
        except (ValueError, OSError, KeyError):
            return ""
    if not context.item:
        return ""
    return context.item if context.item in _entries(context) else ""


def affected_features(context, target_item):
    """blocker が止める feature（§6.8）。target_item と、それを推移的依存先に持つ利用側。空は案件全体。"""
    if not target_item or not is_feature(context):
        return []
    if target_item not in _entries(context):
        return []
    return [target_item] + dependents(context, target_item)


# --- 選択（§6.1、§6.10 C4）---------------------------------------------------

def require_feature_mode(context, what):
    current = mode(context)
    if current != "feature":
        raise ValueError("%sは Feature 方式の案件だけで使えます（現在の方式: %s）。方式の切替は /aidd-mode-switch で行います"
                         % (what, current or "未決定"))


def blocking(context, name):
    """name を止める未解消の blocker（範囲が案件全体のもの、または affected_features に name を含むもの）。"""
    found = []
    for entry in context.blockers():
        if not isinstance(entry, dict) or entry.get("status") == "resolved":
            continue
        scope = entry.get("affected_features")
        if not scope or name in scope:
            found.append(entry.get("id", "unknown"))
    return found


def select(context, feature, actor, note=""):
    """`select-scope`：Feature 方式の対象 S を選ぶ（C4 の許可条件を満たすときだけ）。"""
    require_feature_mode(context, "対象の選択（select-scope）")
    if not actor:
        raise ValueError("選択者（実際の人）が必要です")
    entries = _entries(context)
    if feature not in entries:
        raise ValueError("feature not in approved manifest: " + str(feature))
    state = context.state()
    data = _workflow(context)
    pending = (state.get("current") or {}).get("pending") or {}
    previous_selection = selection(context)
    plan_wait = (pending.get("event", "").endswith("-plan") and pending.get("item")
                 and pending.get("item") == previous_selection)
    if pending and not plan_wait:
        raise ValueError("未回答の待機（dispatch）が残っています。回答してから対象を選び直してください")
    if (data.get("manifest_change") or {}).get("needs_replan"):
        raise ValueError("feature 一覧の差戻し中（上流差戻し）です。一覧の再承認後に対象を選んでください")
    previous = selection(context)
    if previous and previous != feature:
        for process in PLAN_PROCESSES:
            path = "specs/%s/%s.md" % (previous, process)
            if phase_rules.status_of(context.path(path)) == "review":
                raise ValueError("選択中の %s に承認待ち（review）の成果物があります: %s" % (previous, path))
        _require_phase8_idle(context, previous)
    blocked = blocking(context, feature)
    if blocked:
        raise ValueError("%s を止める未解消の差戻しがあります: %s" % (feature, ", ".join(map(str, blocked))))
    value = {"feature": feature, "actor": actor, "at": project_state.now(), "note": note, "previous": previous}
    history = list(data.get("selection_history") or []) + [value]
    current = dict(data)
    current.update(selection=value, selection_history=history)
    project_state.update(context.state_path, {"workflow": current})
    if plan_wait and feature != previous_selection:
        # 計画停止点の待機中の対象の変更（§6.1）：選択中の S の計画停止点を出し直せるよう待機を外す。
        import project_progress
        waiting = phase_rules.ExecutionContext(context.root, context.state_path, pending["event"], pending["item"])
        project_progress.redo(waiting, pending["event"], pending["item"])
    return value


def _require_phase8_idle(context, name):
    """直列規則（§6.6）：実行中のタスク execution、または最終検査待ちがある間は対象を変えない。"""
    import implementation_store as store
    path = Path(context.root) / (store.BASE + "/features/" + name + "/state.json")
    if not path.is_file():
        return
    state = store.read(context.root, store.BASE + "/features/" + name + "/state.json")
    request_id = state.get("active_request")
    if request_id:
        request = store.read(context.root, store.request_path(request_id))
        for execution_id in (request.get("children") or {}).values():
            execution = store.read(context.root, store.execution_path(execution_id))
            if not execution.get("event_complete"):
                raise ValueError("選択中の %s にタスクの実行中の execution があります" % name)
    review = Path(context.root) / (store.BASE + "/features/" + name + "/review.json")
    if review.is_file() and len(state.get("completed") or {}) == len((state.get("policy") or {}).get("tasks") or {}):
        final = phase_rules.ExecutionContext(context.root, context.state_path, phase_rules.IMPLEMENT_REVIEW, name)
        import review_contract
        try:
            review_contract.check_approved(final)
        except (ValueError, OSError, KeyError):
            raise ValueError("選択中の %s が最終検査（implement-gate-run）の承認待ちです" % name)


def default_item(context):
    """Feature 方式で `--item` を省いた advance の item（計画 v3 §6.1「ガード」：入口で mode・S を解決する）。

    全件方式・明示の `--item`・Phase 4〜7 の外の action はそのまま。Feature 方式では次のとおり補う。
    - 計画停止点・作成・修正：選択中の S（未選択なら select-scope を求めて止める）
    - 横断確認・tasks-gate-run：その工程の成果物が U 全件で approved のときだけ item 無し（全件、§6.7）。
      それ以外は S（再承認待ちで S が review に戻っている場合を含む）。過去の確認行・承認行の有無では決めない
      （同じ内容の過去の承認行があっても、今の再承認待ちを全件確認へ回さない）。User の S の横断確認は L3 が拒否する。
    方式を選ぶ最初の requirements-plan（方式が未決定）には補わない。
    """
    if context.item or context.process not in PLAN_PROCESSES or not is_feature(context):
        return context.item
    rule = phase_rules.RULES[context.process]
    name = selection(context)
    if context.action.endswith("-plan") or context.action in (rule["generate"], rule["repair"]):
        if not name:
            raise ValueError("Feature 方式で対象 feature が未選択です。select-scope で選んでから実行してください")
        return name
    if not name:
        return ""
    if context.is_cross or context.action == "tasks-gate-run":
        return "" if all_approved(context, context.process) else name
    return ""


def all_approved(context, process):
    """工程 process の成果物が、承認済みの一覧の U 全件で approved か（全件の確認を通す時点、§6.7）。"""
    outputs = [p for p in phase_rules.RULES[process]["outputs"] if "{feature}" in p]
    return bool(outputs) and all(phase_rules.status_of(context.path(p.replace("{feature}", e["name"]))) == "approved"
                                 for e in context.features() for p in outputs)


def require_selected(context):
    """Feature 方式で item を取る Phase 4〜7 の action は、選択中の S だけを扱う。"""
    if not is_feature(context) or context.process in ("intake", "steering", "feature", "docs", "implement"):
        return
    if not context.item:
        return
    current = selection(context)
    if not current:
        raise ValueError("Feature 方式で対象 feature が未選択です。select-scope で選んでから実行してください")
    if context.item != current:
        raise ValueError("選択中の feature は %s です（--item %s は別の feature）。切り替えるときは select-scope を使います"
                         % (current, context.item))


# --- 計画停止点の了承（D-9）---------------------------------------------------

def plan_digest(context, process, name):
    if phase_rules.implement_kind(process + "-plan") == "plan":
        import implementation_requests
        return implementation_requests.plan_digest(context, name)  # Phase 8：tasks・検証計画・射影（D-11）
    return feature_manifest.projection(context.root, plan_features(context, process, name))


def owner_required(context):
    """この計画停止点で smoke wrapper の owner を答える番か（§6.11 の「適用範囲」(2)）。

    候補は feature 一覧の種別・依存から機械的に決める（mode_switch.owner_candidates）。owner がまだ無く候補がいる
    tasks の計画停止点で答える。Feature 方式では候補の feature の `tasks-plan[S]` の番（最初に来た候補の番）。
    """
    if context.process != "tasks" or not context.action.endswith("-plan"):
        return []
    import implementation_project
    import mode_switch
    if implementation_project.owner_record(context)["owner"]:
        return []
    candidates = mode_switch.owner_candidates(context)
    if is_feature(context) and context.item not in candidates:
        return []
    return candidates


def _owner_answer(context, data):
    """owner の回答（候補がいれば選ばないと了承できない）。選び済みなら聞かない（owner_required が空）。"""
    import implementation_project
    candidates = owner_required(context)
    if not candidates:
        return {}
    owner = data.get("owner") or ""
    if owner == implementation_project.NO_OWNER:
        if not str(data.get("owner_reason") or "").strip():
            raise ValueError("「候補なし」には理由（業務 API を持つ feature が無いこと）が必要です")
    elif owner not in candidates:
        raise ValueError("smoke wrapper の owner を候補から選ぶか「候補なし」と理由を答えます。候補: " + "、".join(candidates))
    return {"owner": owner, "owner_reason": data.get("owner_reason", "")}


def _reopen_owner_tasks(context, owner, actor):
    """owner の tasks が作成済みなら結合確認タスクを足す修正を起こす（§6.11 の「旧案件」、§6.1 の引継ぎ (7)）。"""
    import implementation_project
    if not owner or owner == implementation_project.NO_OWNER or not Path(context.path("specs/%s/tasks.md" % owner)).exists():
        return
    import repair_requests
    owner_context = phase_rules.ExecutionContext(context.root, context.state_path, phase_rules.RULES["tasks"]["generate"], owner)
    waiting = repair_requests.pending(repair_requests.revise_context(owner_context))
    if waiting and waiting.get("instruction") == OWNER_REOPEN:
        return  # 前回の reopen は成功していた（保留を消す前に止まった）。二重に起こさない
    repair_requests.reopen(owner_context, ["specs/%s/tasks.md" % owner], OWNER_REOPEN, "reopen", actor)


def accept_plan(context, data, actor):
    """計画停止点の了承の記録。item 無しの最初の requirements-plan で mode を確定する。"""
    plans = dict(_workflow(context).get("accepted_plans", {}))
    updates = {}
    owner = {}
    if context.item:
        require_feature_mode(context, "item 付きの計画停止点")
        if context.item != selection(context):
            raise ValueError("計画停止点の item（%s）が選択中の feature（%s）と違います" % (context.item, selection(context)))
        entry = dict(plans.get(context.process) or {})
        items = dict(entry.get("items") or {})
        owner = _owner_answer(context, data)
        items[context.item] = {"actor": actor, "at": project_state.now(), "note": data.get("note", ""),
                               "manifest": plan_digest(context, context.process, context.item)}
        entry["items"] = items
        plans[context.process] = entry
    else:
        current = _workflow(context).get("mode")
        chosen = data.get("mode")
        if context.action == "requirements-plan" and current is None:
            if mode(context) == "all" and chosen not in (None, "all"):
                raise ValueError("旧案件（mode 未記載・了承済み）は全件方式です。切り替えは /aidd-mode-switch で行います")
            chosen = chosen or "all"
            if chosen not in MODES:
                raise ValueError("mode は all か feature を選びます: %r" % (chosen,))
            updates["mode"] = chosen
        elif chosen is not None and chosen != mode(context):
            raise ValueError("方式は最初の requirements-plan の了承で決まります。切り替えは /aidd-mode-switch で行います")
        if mode(context) == "feature" and context.process in PLAN_PROCESSES and context.action != "requirements-plan":
            raise ValueError("Feature 方式の %s-plan は item（選択 feature）付きで呼びます" % context.process)
        owner = _owner_answer(context, data)
        plans[context.process] = {"actor": actor, "at": project_state.now(), "note": data.get("note", ""),
                                  "manifest": feature_manifest.source_hash(context.root) if context.phase >= 4 else None}
    updates["accepted_plans"] = plans
    current = dict(_workflow(context))
    current.update(updates)
    if owner:
        # owner の正本は計画了承の外に置く（一覧の構造変更・全件再計画で計画了承を消しても残る。§6.11）。
        current["smoke_owner"] = dict(owner, actor=actor, at=project_state.now(),
                                      source=context.action + "[" + (context.item or "-") + "]")
        if owner["owner"] != context.item and not previous_owner(context):
            # 回答の処理の中で reopen すると L0 の redo が待ち中の dispatch を消し、続く report が拒否される。
            # 報告の後（host_session.stage_respond_reported、または次の audit）に起こす（§6.1 の引継ぎ (7)）。
            current["owner_reopen"] = {"owner": owner["owner"], "actor": actor}
    project_state.update(context.state_path, {"workflow": current})


def previous_owner(context):
    return (_workflow(context).get("owner_reopen") or {}).get("owner")


def apply_owner_reopen(context):
    """保留した owner の tasks の修正の要求を起こす（待ち中の dispatch が無いときだけ）。"""
    pending = _workflow(context).get("owner_reopen")
    if not pending or (context.state().get("current") or {}).get("pending"):
        return
    try:
        _reopen_owner_tasks(context, pending["owner"], pending["actor"])
    except (ValueError, OSError, KeyError) as error:
        # 失敗しても保留を消さない（次の audit でもう一度起こす）。理由を残して表示に使う。
        current = dict(_workflow(context))
        current["owner_reopen"] = dict(pending, error=str(error), at=project_state.now())
        project_state.update(context.state_path, {"workflow": current})
        return
    current = dict(_workflow(context))
    current.pop("owner_reopen", None)
    project_state.update(context.state_path, {"workflow": current})


def require_owner_for_tasks(context):
    """owner を答える前に tasks を先へ進めない（§6.11 の「旧案件」）。

    全件方式で owner の無い古い tasks の計画了承は外して `tasks-plan` を出し直す（残すと古い了承で tasks-authoring を通る）。
    Feature 方式は候補の feature の番だけを止める。
    """
    import implementation_project
    import mode_switch
    if context.process != "tasks" or context.action.endswith("-plan") or implementation_project.owner_record(context)["owner"]:
        return
    candidates = mode_switch.owner_candidates(context)
    if not candidates or (is_feature(context) and context.item and context.item not in candidates):
        return
    if is_feature(context) and not context.item:
        return  # 全件の tasks-gate-run は候補の feature の番で答えた owner を前提にする（下の implement-select も止める）
    settle_mode(context)  # 計画了承を消す前に、旧案件の全件方式を書く
    plans = dict(_workflow(context).get("accepted_plans", {}))
    if not is_feature(context) and plans.get("tasks"):
        plans.pop("tasks")
        current = dict(_workflow(context))
        current["accepted_plans"] = plans
        project_state.update(context.state_path, {"workflow": current})
        import project_progress
        project_progress.redo(context, "tasks-plan")
        raise ValueError("smoke wrapper の owner が未設定です。tasks-plan の計画停止点を出し直しました。owner を選んでから進めます")
    raise ValueError("smoke wrapper の owner が未設定です。%s の計画停止点で owner を選びます"
                     % ("tasks-plan[%s]" % context.item if is_feature(context) else "tasks-plan"))

def plan_accepted(context, process=None, name=None):
    """作成 action の前提：当該工程の計画が、現在の一覧（Feature 方式は射影）に対して了承済み。"""
    plans = _workflow(context).get("accepted_plans", {})
    process, name = process or context.process, name or context.item
    if is_feature(context):
        entry = ((plans.get(process) or {}).get("items") or {}).get(name)
        return bool(entry) and entry.get("manifest") == plan_digest(context, process, name)
    plan = plans.get(context.process)
    return bool(plan) and plan.get("manifest") == feature_manifest.source_hash(context.root)


def candidates(context, process):
    """計画提示の候補一覧（§6.1）：依存先・被依存・依存先の工程状態・選べない理由。表示専用。"""
    rows = []
    for entry in context.features():
        name = entry["name"]
        deps = closure(context, name)
        waiting = [] if process == "requirements" else [
            d for d in deps if phase_rules.status_of(context.path("specs/%s/%s.md" % (d, process))) != "approved"]
        rows.append({"name": name, "kind": entry["kind"], "depends_on": deps, "dependents": dependents(context, name),
                     "status": phase_rules.status_of(context.path("specs/%s/%s.md" % (name, process))) or "未着手",
                     "selectable": not waiting,
                     "reason": ("依存先の %s が未承認: %s" % (process, ", ".join(waiting))) if waiting else ""})
    rows.sort(key=lambda r: (r["kind"] != "Platform",))
    return rows


def rebase_inputs_for_switch(context):
    """方式切替（全件→Feature）の記録入力の引継ぎの試作（`switch-mode` は段階 2）。

    全件方式の記録入力（一覧全体の digest・docs 3 文書の digest）は Feature 方式の形式（射影・docs の固定版）と
    違うので、そのままだと切替直後の audit が全 feature を開き直す。入力が変わっていない consumer
    （全件方式の形式で再計算して記録と一致するもの）だけを、新しい形式で記録し直す。変わっていたものは
    触らず、切替後の audit が従来どおり開き直す。tasks のある feature は docs の固定版を作る（C8）。
    """
    unchanged = switch_unchanged_inputs(context)
    data = dict(_workflow(context))
    data["mode"] = "feature"
    project_state.update(context.state_path, {"workflow": data})
    current = dict(_workflow(context))
    current["inputs"] = dict(current.get("inputs") or {}, **rebase_inputs_after_switch(context, unchanged))
    project_state.update(context.state_path, {"workflow": current})
    return {"rebased": unchanged}


def switch_unchanged_inputs(context):
    """切替前（全件方式の形式）に、入力が変わっていない consumer の記録入力の鍵。状態は書かない。"""
    import project_progress
    data = dict(_workflow(context))
    if data.get("mode") != "all" and mode(context) != "all":
        raise ValueError("切替は全件方式の案件だけで行います")
    unchanged = []
    for key, previous in (data.get("inputs") or {}).items():
        action, _, item = key[:-1].partition("[")
        consumer = phase_rules.ExecutionContext(context.root, context.state_path, action, item)
        try:
            if project_progress.signature(consumer) == previous:
                unchanged.append(key)
        except (ValueError, OSError, KeyError):
            continue
    return unchanged


def rebase_inputs_after_switch(context, unchanged):
    """mode=feature を書いた後：tasks のある feature の docs の固定版を作り（C8。何度呼んでも同じ）、
    unchanged の記録入力を新しい形式で計算して返す。記録入力そのものは書かない（呼び元が 1 回で保存する）。"""
    import project_progress
    import docs_revision
    for entry in context.features():
        if phase_rules.status_of(context.path("specs/%s/tasks.md" % entry["name"])) and docs_revision.current(context):
            docs_revision.ensure_fixed(context, entry["name"])
    inputs = {}
    for key in unchanged:
        action, _, item = key[:-1].partition("[")
        inputs[key] = project_progress.signature(phase_rules.ExecutionContext(context.root, context.state_path, action, item))
    return inputs


def present(path):
    return Path(path).is_file()


def approved_with_evidence(context, path):
    import project_progress
    owner = project_progress.owner_of(context, path)
    return (artifacts.fields(context.path(path)) or {}).get("status") == "approved" and (
        owner is None or project_progress.evidence_ok(owner))
