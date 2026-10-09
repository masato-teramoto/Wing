"""Feature 方式の docs の累積と固定版（計画 v3 §6.5「docs の固定」、§6.6、§6.10 C2・C8）。

- 収録集合：design が承認済み（証跡あり）の feature。Feature 方式の `docs-integration-*` の `{features}`。
- 不変版 `docs_revision`：`.aidd/docs/revisions/<id>.json`（追加のみ。id は内容の SHA-256）。docs が承認済み
  （証跡あり）になった後の最初の audit で作る。現在版の参照は `workflow.docs_revision`。
- 固定版：feature ごとに、tasks を作った時点の版（`workflow.docs_fixed[<feature>]`）。Phase 7 の記録入力と
  Phase 8 の入力署名はファイルの digest ではなくこの id を持つので、docs の改訂で開き直されない。
- C2：版が進んだとき、digest だけで影響を判定する。影響なし → 固定版を進める（Phase 8 承認済みは
  `review.json` を書き換えず、同値の記録 `docs_repins` を追記する）。影響あり → Phase 8 前は tasks を開き直す。
  Phase 8 承認済みの「影響あり」は 3 段の (2) の対象として記録だけ残す（再検証の実行は段階 3）。
全件方式ではどの関数も呼ばれない（呼出し側が mode を見る）。
"""
import l0  # noqa: F401  L0 の枠組みを import できるようにする
import hashlib
import json
from pathlib import Path

import artifacts
import phase_rules
import project_state

BASE = ".aidd/docs/revisions"


def _workflow(context):
    value = context.state().get("workflow", {})
    return value if isinstance(value, dict) else {}


def _save(context, changes):
    current = dict(_workflow(context))
    current.update(changes)
    project_state.update(context.state_path, {"workflow": current})


def _docs_context(context):
    return phase_rules.ExecutionContext(context.root, context.state_path, phase_rules.RULES["docs"]["generate"])


def _steering(context):
    return [p for p in phase_rules.config()["rules"]["steering"]["outputs"]]


def members(context):
    """収録集合：design.md が承認済みで、その承認が現在の内容と一致する feature（一覧順）。"""
    import project_progress
    names = []
    for entry in context.features():
        path = "specs/%s/design.md" % entry["name"]
        if phase_rules.status_of(context.path(path)) != "approved":
            continue
        owner = project_progress.owner_of(context, path)
        if owner is not None and project_progress.evidence_ok(owner):
            names.append(entry["name"])
    return names


def _digest(context, path):
    full = Path(context.path(path))
    return artifacts.protected_digest(str(full)) if full.is_file() else None


def build(context):
    """承認済み（証跡あり）の現在の docs から版の内容を組み立てる。docs が未承認なら None。"""
    import project_progress
    import review_contract
    docs = _docs_context(context)
    if not project_progress.evidence_ok(docs):
        return None
    record = review_contract.read(docs)
    consumed = _consumed(context)
    if consumed is None:
        return None
    # 収録集合と元の digest は、docs が実際に読んだ入力（docs の action の記録入力）から取る。現在 design が
    # 承認済みの feature から取ると、docs の改訂前に収録したことになる版ができる。
    included = [e["name"] for e in context.features() if "specs/%s/design.md" % e["name"] in consumed]
    value = {"schema": 1, "features": included,
             "unrecorded": [e["name"] for e in context.features() if e["name"] not in included],
             "specs": {name: {kind: consumed.get("specs/%s/%s.md" % (name, kind)) for kind in ("requirements", "design")}
                       for name in included},
             "docs": {}, "approvals": {}, "steering": {p: _digest(context, p) for p in _steering(context)}}
    for path in phase_rules.config()["rules"]["docs"]["outputs"]:
        digest = phase_rules.inspection_digest(docs, path)
        row = next((r for r in reversed(record.approvals) if r["対象成果物"] == path and r["原本SHA256"] == digest), None)
        if row is None:
            return None
        value["docs"][path] = digest
        value["approvals"][path] = {"scope": row["スコープ"], "run": int(row["回数"])}
    return value


def _consumed(context):
    """docs の最後の実行の記録入力（revise があれば revise、なければ generate）。"""
    rule = phase_rules.RULES["docs"]
    inputs = _workflow(context).get("inputs") or {}
    return inputs.get(rule["repair"] + "[]") or inputs.get(rule["generate"] + "[]")


def identify(value):
    return hashlib.sha256(json.dumps(value, ensure_ascii=False, sort_keys=True).encode()).hexdigest()


def path_of(revision_id):
    return BASE + "/" + revision_id + ".json"


def read(context, revision_id):
    path = Path(context.path(path_of(revision_id)))
    value = json.loads(path.read_text(encoding="utf-8"))
    if identify(value) != revision_id:
        raise ValueError("docs_revision の内容が id と一致しません（改変）: " + revision_id)
    return value


def current(context):
    """現在の承認済み docs の版 id（必要なら作る）。docs が未承認・改訂中なら記録済みの最後の版。"""
    value = build(context)
    if value is None:
        return _workflow(context).get("docs_revision")
    revision_id = identify(value)
    path = Path(context.path(path_of(revision_id)))
    if not path.is_file():
        path.parent.mkdir(parents=True, exist_ok=True)
        temporary = path.with_name(path.name + ".tmp")
        temporary.write_text(json.dumps(value, ensure_ascii=False, sort_keys=True, indent=1), encoding="utf-8")
        temporary.replace(path)
    if _workflow(context).get("docs_revision") != revision_id:
        history = list(_workflow(context).get("docs_revision_history") or []) + [{"id": revision_id, "at": project_state.now()}]
        _save(context, {"docs_revision": revision_id, "docs_revision_history": history})
    return revision_id


def valid(context, revision_id):
    """固定版の有効性：版が改変されておらず、各文書の承認行がその hash で記録ファイルに残っている。"""
    import review_contract
    if not revision_id:
        raise ValueError("docs の固定版がありません（tasks の作成時に固定します）")
    value = read(context, revision_id)
    record = review_contract.read(_docs_context(context))
    for path, digest in value["docs"].items():
        approval = value["approvals"][path]
        if not any(r["対象成果物"] == path and r["原本SHA256"] == digest and r["スコープ"] == approval["scope"]
                   and int(r["回数"]) == approval["run"] for r in record.approvals):
            raise ValueError("docs の固定版の承認行が見つかりません: %s（%s）" % (path, revision_id))
    return value


def fixed(context, feature):
    return (_workflow(context).get("docs_fixed") or {}).get(feature)


def fix(context, feature, revision_id, reason, advance_inputs=False):
    """固定版を記録する。advance_inputs のとき（C2 影響なしで進める）は、その feature の tasks 系 consumer の
    記録入力の版 id も同じ取引で進める（§6.5「記録入力の固定版を更新し」）。進めないと入力変更検知が開き直す。"""
    data = _workflow(context)
    fixed_map = dict(data.get("docs_fixed") or {})
    old = fixed_map.get(feature)
    if old == revision_id:
        return
    fixed_map[feature] = revision_id
    history = list(data.get("docs_fixed_history") or []) + [
        {"feature": feature, "from": old, "id": revision_id, "reason": reason, "at": project_state.now()}]
    changes = {"docs_fixed": fixed_map, "docs_fixed_history": history}
    if advance_inputs:
        inputs = dict(data.get("inputs") or {})
        for key, value in inputs.items():
            action, _, item = key[:-1].partition("[")
            if (item == feature and phase_rules.PROCESS_OF.get(action) == "tasks" and isinstance(value, dict)
                    and value.get("docs_revision") == old):
                inputs[key] = dict(value, docs_revision=revision_id)
        changes["inputs"] = inputs
    _save(context, changes)


def unfix(context, feature, reason):
    """固定版を外す（履歴に残す）。次の tasks の作成で、その時点の承認済み版を固定し直す。"""
    data = _workflow(context)
    fixed_map = dict(data.get("docs_fixed") or {})
    if feature not in fixed_map:
        return
    old = fixed_map.pop(feature)
    history = list(data.get("docs_fixed_history") or []) + [
        {"feature": feature, "from": old, "id": None, "reason": reason, "at": project_state.now()}]
    _save(context, {"docs_fixed": fixed_map, "docs_fixed_history": history})


def ensure_fixed(context, feature, regenerate=False):
    """tasks の作成（・再生成）時点の承認済み版を固定版にする。"""
    if fixed(context, feature) and not regenerate:
        return fixed(context, feature)
    revision_id = current(context)
    if not revision_id:
        raise ValueError("docs が承認されていません（tasks は承認済みの docs から作ります）")
    fix(context, feature, revision_id, "tasks の再生成" if regenerate else "tasks の作成")
    return revision_id


def impact(context, feature, old_id, new_id):
    """C2：(a) 変わった feature が F ∪ D(F) を含まない、(b) 変わった feature がある、(c) steering が同じ、のすべてで影響なし。"""
    import feature_scope
    old, new = read(context, old_id), read(context, new_id)
    names = set(old["specs"]) | set(new["specs"])
    changed = sorted(n for n in names if old["specs"].get(n) != new["specs"].get(n))
    own = {feature, *feature_scope.closure(context, feature)}
    reasons = []
    if set(changed) & own:
        reasons.append("自 feature または依存先の requirements／design が変わった: " + ", ".join(sorted(set(changed) & own)))
    if not changed:
        reasons.append("feature の差分を伴わない docs の改訂（帰属を機械的に決められない）")
    if old["steering"] != new["steering"]:
        reasons.append("steering が変わった")
    return {"feature": feature, "from": old_id, "to": new_id, "changed_features": changed,
            "impact": bool(reasons), "reasons": reasons}


def phase8_approved(context, feature):
    import review_contract
    import implementation_evidence
    if not Path(context.path(implementation_evidence.review_path(feature))).is_file():
        return False
    final = phase_rules.ExecutionContext(context.root, context.state_path, phase_rules.IMPLEMENT_REVIEW, feature)
    record = review_contract.read(final)
    run = record.latest(final.scope)
    return bool(run) and any(r["スコープ"] == run.scope and int(r["回数"]) == run.number for r in record.approvals)


def evaluate(context):
    """版が進んだ feature を C2 で仕分ける（audit から呼ぶ）。判定の記録は `docs_evaluations` に追記する。"""
    import repair_requests
    import project_progress
    import feature_manifest
    path = feature_manifest.source_path(context.root)
    if not path.is_file() or (artifacts.fields(path) or {}).get("status") != "approved":
        return []  # 一覧の差戻し中（上流差戻し）は評価しない。再承認後の audit で評価する
    revision_id = current(context)
    if not revision_id:
        return []
    results = []
    for feature, old_id in sorted((_workflow(context).get("docs_fixed") or {}).items()):
        if old_id == revision_id:
            continue
        done = [e for e in _workflow(context).get("docs_evaluations") or []
                if e["feature"] == feature and e["from"] == old_id and e["to"] == revision_id]
        if done:
            continue
        result = impact(context, feature, old_id, revision_id)
        approved_code = phase8_approved(context, feature)
        result["phase8_approved"] = approved_code
        if not result["impact"]:
            if approved_code:
                # review.json は書き換えない。入力署名の同値を追記専用の記録で示す（implement-repin と同じ考え方）。
                repins = list(_workflow(context).get("docs_repins") or []) + [
                    {"feature": feature, "from": old_id, "to": revision_id, "at": project_state.now(), "evaluation": "C2 影響なし"}]
                _save(context, {"docs_repins": repins})
            fix(context, feature, revision_id, "C2 影響なし", advance_inputs=True)
            result["action"] = "固定版を進めた"
        elif approved_code:
            result["action"] = "3 段の (2)（実装承認済み。再検証は段階 3 の implement-reverify）"
        else:
            tasks = "specs/%s/tasks.md" % feature
            owner = phase_rules.ExecutionContext(context.root, context.state_path, phase_rules.RULES["tasks"]["generate"], feature)
            if not Path(context.path(tasks)).is_file():
                # tasks がまだ無い：古い固定版を残すと、作成時にその版のまま使われる（ensure_fixed）。固定を外し、作成時に今の版で固定する。
                unfix(context, feature, "C2 影響あり・tasks 未作成（%s → %s）" % (old_id[:12], revision_id[:12]))
                result["action"] = "固定を外した（tasks の作成時に今の版で固定する）"
            elif repair_requests.pending(repair_requests.revise_context(owner)) is not None:
                # 別の tasks の修正要求が待っている：その修正は docs の再固定をしない（origin が docs-revision でない）。
                # 評価を記録せず、要求の完了後の audit でもう一度評価する。
                continue
            else:
                repair_requests.reopen(owner, [tasks], "docs の改訂（%s → %s）の影響を反映する: %s"
                                       % (old_id[:12], revision_id[:12], " / ".join(result["reasons"])),
                                       "docs-revision", project_progress.SYSTEM_ACTOR)
                result["action"] = "tasks を開き直した"
        result["at"] = project_state.now()
        evaluations = list(_workflow(context).get("docs_evaluations") or []) + [result]
        _save(context, {"docs_evaluations": evaluations})
        results.append(result)
    return results


def accumulate(context):
    """2 件目以降の収録（§6.3 2f）：収録集合が最後の版から変わっていれば、docs への修正要求を L3 が起こす。

    `docs-integration-revise` には修正要求が要る（repair-request-check）。計画停止は置かず、docs-check と人間承認で止める。
    """
    import repair_requests
    import project_progress
    if repair_requests.pending(context) is not None:
        return None
    revision_id = _workflow(context).get("docs_revision")
    recorded = set(read(context, revision_id)["features"]) if revision_id else set()
    added = [n for n in members(context) if n not in recorded]
    if not added and revision_id:
        return None
    targets = [t for t in context.artifacts() if Path(context.path(t)).is_file()]
    if not targets:
        return None
    return repair_requests.reopen(context, targets, "feature %s の収録（docs の累積）" % ", ".join(added),
                                  "docs-accumulate", project_progress.SYSTEM_ACTOR)


def equivalent(context, feature, saved_id, current_id):
    """Phase 8 の照合：保存した版と現在の固定版が同じか、C2 影響なしの同値記録でつながるか。"""
    if saved_id == current_id:
        return True
    links = {(e["from"], e["to"]) for e in _workflow(context).get("docs_repins") or [] if e["feature"] == feature}
    frontier, seen = {saved_id}, set()
    while frontier:
        node = frontier.pop()
        if node == current_id:
            return True
        seen.add(node)
        frontier |= {b for a, b in links if a == node and b not in seen}
    return False
