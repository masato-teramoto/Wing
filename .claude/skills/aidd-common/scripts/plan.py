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

import aidd_paths

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
    context = aidd_paths.Context()
    name, unit, gate = PLANS.get(context.process, (context.process, "一括", "一括 1 回"))

    lines = [
        "**Phase %s（%s）に入ります。** 開始前に実行計画を確認してください。"
        % (context.phase or "?", name),
        "",
        "**生成単位**: %s。ゲートは %s 通します。" % (unit, gate),
        "",
        "**対象 feature と順序**（`.aidd/feature-list.md` の優先度順）",
    ]

    features = context.features() if context.phase >= 4 else []
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

    lines += ["", "この計画で進めてよいか指示してください。"]

    print("\n".join(lines))
    sys.exit(aidd_paths.EXIT_WAIT)


def _stops(process, features):
    if process in ("requirements", "design"):
        return "feature 数 + 1 回（%d 回）" % (len(features) + 1) if features else "feature 数 + 1 回"
    if process == "tasks":
        return "1 回（feature 別検査後の全体確認で人間承認をまとめるため）"
    return "1 回"


if __name__ == "__main__":
    main()
