#!/usr/bin/env python3
"""process 開始の実行計画を提示して止まる（`script / requiresHuman: true`）。

**旧 `aidd-flow` の Step 0 にあたる。** コマンドの境界だけでは、
`/aidd-requirements-init` のように 1 コマンドが 3 フェーズを持つ場合に
Phase 2 / 3 の開始が無言で通り過ぎ、`forEach` を回すコマンドでも
**対象 feature と順序が一度も提示されない**。成果物が量産される前に
人間が範囲と順序を直せるようにするための停止であり、許可を取るための停止ではない。

このスクリプトは**回答を生成しない。** 計画を組み立てて出力し、
終了コード 10（人間待ち）で返すだけである。

Phase 1（`intake`）には付けない。人間がコマンドを打った直後であり、
計画が起動指示と重複する（旧 `aidd-flow` §5 Step 0 と同じ扱い）。
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import phase_rules

# process id → (フェーズ名, 生成単位, ゲートの通し方)
PLANS = {
    "steering": ("Steering 作成", "一括（依存順）", "7 ファイルを 1 スコープで一括 1 回"),
    "feature": ("Feature 分割", "一括", "一括 1 回"),
    "requirements": (
        "requirements 作成",
        "1 feature ずつ（優先度順）",
        "feature ごとに 1 回 ＋ 全 feature が approved になった後に横断 1 回",
    ),
    "design": (
        "design 作成",
        "1 feature ずつ（優先度順）",
        "feature ごとに 1 回 ＋ 全 feature が approved になった後に横断 1 回（契約整合）",
    ),
    "docs": ("docs 作成", "抽出は feature 単位・確定は一括", "一括 1 回"),
    "tasks": ("tasks 作成", "1 feature ずつ（優先度順）", "feature 別に検査し、最後に全体の依存確認と人間承認を一括 1 回"),
}

# 対象 feature と順序を列挙するフェーズ。それ以外は「該当なし」と書く（省略しない）。
PER_FEATURE = ("requirements", "design", "tasks")


def main():
    context = phase_rules.gate_context()
    name, unit, gate = PLANS.get(context.process, (context.process, "一括", "一括 1 回"))

    lines = [
        "**Phase %s（%s）に入ります。** 開始前に実行計画を確認してください。"
        % (context.phase or "?", name),
        "",
        "**生成単位**: %s。ゲートは %s 通します。" % (unit, gate),
        "",
        "**対象 feature と順序**（`.aidd/feature-list.md` の優先度順）",
    ]

    if context.kind == "plan":
        print("\n".join(_implement_plan(context, context.item)))
        sys.exit(phase_rules.EXIT_WAIT)
    features = context.features() if context.phase >= 4 else []
    import feature_scope
    current_mode = feature_scope.mode(context) if context.phase >= 4 else "all"
    if context.plan_item:
        print("\n".join(_selection_plan(context, context.plan_item)))
        sys.exit(phase_rules.EXIT_WAIT)
    if context.process not in PER_FEATURE:
        lines.append("- 該当なし（feature 単位ではない）")
    elif not features:
        lines.append("- **未確定。** `.aidd/feature-list.md` と状態ストアの `features[]` を先に確定させること。")
    else:
        for index, feature in enumerate(features, start=1):
            depends = feature.get("depends_on") or []
            lines.append(
                "%d. `%s`（%s / 依存: %s）"
                % (index, feature["name"], feature.get("kind") or "—",
                   "、".join("`%s`" % d for d in depends) if depends else "なし")
            )

    lines += [
        "",
        "**入力として読むもの**（すべて `approved`）",
    ]
    inputs = context.authoring_inputs() if context.process != "intake" else []
    lines += ["- `%s`" % path for path in dict.fromkeys(inputs)] or ["- 該当なし（RFP は自由形式）"]
    preconditions = [p for p in context.upstream() if p not in inputs]
    if preconditions:
        lines += ["", "**開始の前提**（`approved` であること。生成の入力にはしない）"]
        lines += ["- `%s`" % path for path in preconditions]

    outputs = context.artifacts()
    lines += [
        "",
        "**出力先**: %s（%d ファイル）"
        % (" / ".join("`%s`" % o for o in outputs) if outputs
           else "`specs/<feature 名>/%s.md`" % context.process,
           len(outputs) if outputs else len(features)),
        "",
        "**想定される停止回数**: %s。作成中に根拠が足りない箇所があれば、その都度質問して停止します。"
        % _stops(context.process, features),
    ]

    if context.process in PER_FEATURE:
        lines.append("")
        lines.append(
            "**対象 feature や順序を変える場合は `.aidd/feature-list.md` の変更になるため、"
            "Phase 3 への差戻しとして扱います。**"
        )
        lines.append("（変更する場合は、その内容を指示してください。今回は一部だけ作る等の進め方の指示は計画に記録し、"
                     "フェーズの完了条件は全 feature の完了のままです。）")
    if context.process == "design":
        lines.append("feature ごとに要件トレーサビリティの自己診断結果を報告します。")

    if context.process == "requirements" and current_mode is None:
        lines += ["", "**進め方（方式）を選んでください**（了承時に記録し、以後の変更は `/aidd-mode-switch` で全件方式→Feature 方式の 1 回だけ）",
                  "- 全件方式：上の順で全 feature の requirements を作ってから design へ進む（従来どおり）",
                  "- Feature 方式：1 feature ずつ選んで requirements→design→docs→tasks→実装まで進める。候補は次のとおり："]
        lines += _candidates(context, "requirements")
    lines += _owner_lines(context)
    lines += ["", "この計画で進めてよいか指示してください。"]

    print("\n".join(lines))
    sys.exit(phase_rules.EXIT_WAIT)


def _owner_lines(context):
    """smoke wrapper の owner の候補と選択（§6.11。候補がいれば選ばないと了承できない）。"""
    import feature_scope
    candidates = feature_scope.owner_required(context)
    if not candidates:
        return []
    return ["", "**smoke wrapper の owner を選んでください**（選ばないと了承できません）",
            "- 候補：" + "、".join("`%s`" % c for c in candidates),
            "- owner の tasks に、全体結合確認の 1 経路を実行する wrapper を作る「結合確認タスク」を入れます。",
            "- 業務 API を持つ feature が無いときは「候補なし」と理由を答えます（smoke は起動→readiness 待ち→停止に縮めます）",
            "- 回答：accept-plan の data に `owner`（と「候補なし」なら `owner_reason`）"]


def _candidates(context, process):
    import feature_scope
    rows = []
    for row in feature_scope.candidates(context, process):
        rows.append("  - `%s`（%s / 依存先: %s / 被依存: %s / 状態: %s）%s"
                    % (row["name"], row["kind"], "、".join(row["depends_on"]) or "なし",
                       "、".join(row["dependents"]) or "なし", row["status"],
                       "" if row["selectable"] else " — 選べない理由: " + row["reason"]))
    return rows


def _selection_plan(context, name):
    """Feature 方式の計画停止点 `<process>-plan[S]`（D-9）。承認前提は S と D だけにかかる。"""
    import feature_scope
    chosen = (context.state().get("workflow") or {}).get("selection") or {}
    members = feature_scope.plan_features(context, context.process, name)
    lines = ["**Phase %s（%s）を feature `%s` について始めます（Feature 方式）。** 開始前に実行計画を確認してください。"
             % (context.phase, PLANS[context.process][0], name), "",
             "**選択**: `%s`（選択者: %s / %s）" % (name, chosen.get("actor", "—"), chosen.get("at", "—")), "",
             "**依存先（推移的）**: %s" % ("、".join("`%s`" % d for d in feature_scope.closure(context, name)) or "なし"),
             "**この計画の前提にする feature**: %s" % "、".join("`%s`" % m for m in members), ""]
    lines += ["**入力として読むもの**（すべて `approved`）"] + ["- `%s`" % p for p in dict.fromkeys(context.upstream())]
    lines += ["", "**出力先**: %s" % " / ".join("`%s`" % o for o in context.artifacts()), "",
              "**他の feature の状態**（表示のみ。承認前提には使わない）"] + _candidates(context, context.process)
    lines += _owner_lines(context)
    lines += ["", "工程の承認後も、依存する側の feature には自動で進みません。次の feature は改めて選びます（select-scope）。",
              "", "この計画で進めてよいか指示してください。"]
    return lines


def _implement_plan(context, name):
    """Feature 方式の Phase 8 の計画停止点 `implement-plan[S]`（D-11）。"""
    import feature_scope
    import implementation_requests
    import implementation_evidence
    import task_runtime
    chosen = (context.state().get("workflow") or {}).get("selection") or {}
    lines = ["**Phase 8（実装）を feature `%s` について始めます（Feature 方式）。** 開始前に実行計画を確認してください。" % name, ""]
    if chosen.get("previous") and chosen.get("previous") != name:
        lines.append("**対象の切替**: `%s` から `%s` に切り替えました（選択者: %s / %s）"
                     % (chosen["previous"], name, chosen.get("actor", "—"), chosen.get("at", "—")))
    else:
        lines.append("**選択**: `%s`（選択者: %s / %s）" % (name, chosen.get("actor", "—"), chosen.get("at", "—")))
    lines += ["", "**依存先（推移的）**: %s" % ("、".join("`%s`" % d for d in feature_scope.closure(context, name)) or "なし"), ""]
    plan = task_runtime.freeze(context, name)
    lines.append("**対象タスクと依存順**")
    for key in plan["order"]:
        task = plan["tasks"][key]
        lines.append("%s. %s%s（依存: %s）" % (key, task["summary"], "（完了済み）" if task.get("checked") else "",
                                           "、".join(task["depends_on"]) or "なし"))
    config = implementation_evidence.config_path(name)
    lines += ["", "**検証計画**（`%s`。AI が用意したもの）" % config]
    try:
        import implementation_store
        value = implementation_store.read(context.root, config)
        for check in value.get("checks") or []:
            lines.append("- `%s`：`%s`（上限 %s 秒）" % (check.get("id"), " ".join(check.get("argv") or []), check.get("timeout_seconds")))
        for key, task in sorted((value.get("tasks") or {}).items()):
            lines.append("- タスク %s の変更範囲（allowed_paths）：%s" % (key, "、".join("`%s`" % p for p in task.get("allowed_paths") or [])))
    except (ValueError, OSError, KeyError):
        lines.append("- **未作成。** 了承の前に検証計画を用意してください")
    remaining = [k for k in plan["order"] if not plan["tasks"][k].get("checked")]
    lines += ["", "**想定される停止回数**: タスクの人間確認 %d 回 ＋ feature の最終承認 1 回。作業中に根拠が足りなければ、その都度質問して停止します。"
              % len(remaining)]
    entry = next(e for e in context.features() if e["name"] == name)
    if entry["kind"] == "Platform":
        waiting = [n for n in feature_scope.dependents(context, name)
                   if phase_rules.status_of(context.path("specs/%s/requirements.md" % n)) != "approved"]
        if waiting:
            lines += ["", "**利用側 %d 件（%s）の requirements が未承認です。** 契約が変わると、承認済みの実装の再検証が起きます。"
                      "進めるかどうかの判断は了承の note に残してください" % (len(waiting), "、".join(waiting))]
    found = implementation_requests.overlaps(context, name)
    if found:
        lines += ["", "**依存先の変更範囲との重なり**（依存先の再検証を伴う変更。了承した場合だけ許します）"]
        lines += ["- `%s` と依存先 `%s` の `%s`" % (mine, other, theirs) for other, mine, theirs in found]
    lines += ["", "対象を変えるときは select-scope で選び直します。この計画で進めてよいか指示してください。"]
    return lines


def _stops(process, features):
    if process in ("requirements", "design"):
        return "feature 数 + 1 回（%d 回）" % (len(features) + 1) if features else "feature 数 + 1 回"
    if process == "tasks":
        return "1 回（feature 別検査後の全体確認で人間承認をまとめるため）"
    return "1 回"


if __name__ == "__main__":
    main()
