"""Present inspection evidence and wait for a real human response.

The wording follows the alpha2 ③ human-review template (aidd-flow Step 4): the
host shows this text as is. Headings, choice letters and order do not change,
no recommendation or default is shown, and Skill / agent names are not shown.
"""
import aidd_paths
import review_contract
import inspection_seal
import json

NAMES = {"intake": "要求受入", "steering": "Steering 作成", "feature": "Feature 分割", "requirements": "requirements 作成",
         "design": "design 作成", "docs": "docs 作成", "tasks": "tasks 作成"}
MACHINE = ("format-conformance", "revision-diff-validity", "sequence-consistency", "dependency-cycle")


def cell(value):
    return str(value).replace("|", "&#124;").replace("\n", " ")


def label(finding, latest, multi):
    base = str(finding.number) if finding.run == latest else "%d-%d" % (finding.run, finding.number)
    return ("%s %s" % (finding.scope, base)) if multi else base


def scope_label(scope):
    if scope == "cross":
        return "横断"
    if scope.startswith("feature:"):
        return "成果物単位（%s）" % scope[len("feature:"):]
    return "成果物単位"


def main():
    context = aidd_paths.Context()
    try:
        record = review_contract.read(context)
        seal = inspection_seal.verify(context, record)
        print('AIDD-REVIEW-CONTEXT: '+json.dumps({'unit':context.unit,'snapshot':seal['snapshot'],
              'run':seal['run'],'inspection_hash':seal['record_hash']},ensure_ascii=False))
        scopes = review_contract.scopes(context)
        multi = len(scopes) > 1
        gate_path = aidd_paths.PHASES[context.process][1]
        undecided_total = 0
        lines = ["**Phase %s（%s）の品質ゲートを実行しました。** 指摘ごとに判断を選んでください。" % (context.phase, NAMES.get(context.process, context.process)), ""]
        for scope in scopes:
            run = review_contract.inspection(context, record, scope)
            targets = review_contract.targets_for(context, scope) if scope != "cross" else run.targets
            if multi:
                lines += ["#### %s" % scope, ""]
            lines.append("**対象**: %s（スコープ: %s / %d 回目）" % (" / ".join("`%s`" % t for t in targets), scope_label(scope), run.number))
            layers = "① / ②" if run.layers == "①②" else run.layers
            if run.layers == "①":
                layers += "（① で形式の不備を検出したため ② は実行していません）"
            elif run.layers == "②":
                layers += "（形式検査を持たない横断スコープのため ② のみ）"
            lines += ["**実行した層**: %s" % layers, ""]
            current = [f for f in run.findings]
            pending = [f for f in current if not f.has_decision]
            answered = [f for f in current if f.has_decision]
            undecided_total += len(pending)
            if not current:
                lines += ["**指摘**（ゲート記録 `%s` の当該実行分）: なし（0 件。検査は実行済み）" % gate_path, ""]
            else:
                lines += ["**指摘**（ゲート記録 `%s` の当該実行分）" % gate_path, "",
                          "| # | 層 | 対象箇所 | 指摘内容 |", "|---|---|---|---|"]
                for f in pending:
                    layer = "①" if f.gate in MACHINE else "②"
                    lines.append("| %s | %s | %s | %s |" % (label(f, run.number, multi), layer, cell(f.location), cell(f.description)))
                if not pending:
                    lines.append("| — | — | — | 未回答の指摘はありません |")
                lines.append("")
                if answered:
                    lines.append("**回答済み**: " + " / ".join("#%s %s%s" % (label(f, run.number, multi), f.decision, "（%s）" % f.reason if f.reason else "") for f in answered))
                    lines.append("")
            carried = [f for f in record.relevant(scope) if f.run != run.number]
            if carried:
                lines += ["**前回までの指摘**（今回件数に含めない）"]
                for f in carried:
                    if not f.has_decision:
                        state = "判断が未回答"
                        undecided_total += 1
                    elif f.is_open:
                        state = "%s → 再検査の結果を見て解消を確認してください" % f.decision
                    else:
                        state = "%s（残件として持ち越し。判断を変える場合は `%s:<記号>`）" % (f.decision, label(f, run.number, multi))
                    lines.append("- #%s %s [%s] — %s" % (label(f, run.number, multi), cell(f.description), cell(f.location), state))
                lines.append("")
            lines.append("**差戻し先の候補**（ゲートの提示。戻すかどうかは判断に含めてください）")
            lines += ["- #%s: %s（%s）" % (c["指摘番号"], c["宛先"], c["理由"]) for c in run.returns] or ["- なし"]
            lines.append("")
        if undecided_total:
            lines += ["**判断の選択肢**（指摘ごとに 1 つ選ぶ）",
                      "- **A: 修正** — このフェーズ内で直す",
                      "- **B: 差戻し** — 上流フェーズ / フロー外の不備として戻す",
                      "- **C: 対応せず進める** — 直さずに進める（**理由が必須**）",
                      "- **D: 未対応** — 今回は判断を保留し、残件として持ち越す（**理由が必須**）", "",
                      ("回答例: `%s 1:A / phase 1:C 既存システムの制約で変更できない`（複数の範囲をまとめて確認するため、# の欄のとおり範囲を付けて答える）" % scopes[0]
                       if multi else "回答例: `1:A / 2:C 既存システムの制約で変更できない / 3:D 次回レビューまで保留`"),
                      "全件を同じ判断にする場合は `全件:A` と書いてください。"]
        try:
            review_contract.ready(context, record)
        except ValueError as error:
            if not undecided_total:
                lines.append("承認を問う前に必要なこと: %s" % error)
        else:
            lines.append("横断スコープは承認対象の文書を持たないため、承認ではなく確認を記録します。確認する場合は確認者名を回答してください。"
                         if context.is_cross else "判断が揃いました。承認の可否を回答してください（承認する場合は承認者名）。")
        print("\n".join(lines))
    except (ValueError, OSError) as error:
        aidd_paths.fail(str(error))
    raise SystemExit(aidd_paths.EXIT_WAIT)


if __name__ == "__main__":
    main()
