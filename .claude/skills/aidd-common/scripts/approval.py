"""Present inspection evidence and wait for a real human response.

The host shows this text as is. 人が見る範囲をはっきりさせるため、次の順に示す。

1. この工程で見る観点（設計書の③の節。references/review-viewpoints.json）
2. 見なくてよいもの（L4 が検査済みの項目・AI 内部のファイル・system が自動で処理した指摘）
3. 前回の検査からの変更（変わった節。修正の指示に無い節の変更も示す）
4. 判断が要る指摘（重大を 1 件ずつ → 要判断を束で → 前回までの持ち越し）。要約と AI の推奨を示し、根拠は `詳細` で開く
5. 答え方

決めるのは人。推奨は理由と一緒に示し、採否は記録に残る。Skill / agent の名前は出さない。
"""
import json
from pathlib import Path

import finding_rules
import phase_rules
import review_contract
import review_view
import inspection_seal
import snapshot_artifacts

NAMES = {"intake": "要求受入", "steering": "Steering 作成", "feature": "Feature 分割", "requirements": "requirements 作成",
         "design": "design 作成", "docs": "docs 作成", "tasks": "tasks 作成", "implement": "実装"}
VIEWPOINTS = phase_rules.COMMON / "references" / "review-viewpoints.json"
LIST_LIMIT = 10  # 自動で処理した指摘を 1 件ずつ並べる上限


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


def viewpoints(process):
    try:
        data = json.loads(Path(VIEWPOINTS).read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return {}, ""
    return data.get("phases", {}).get(process, {}), data.get("internal", "")


def recommended(finding):
    try:
        head, why = finding_rules.recommendation(finding.recommendation)
    except ValueError:
        return "-"
    return "%s（%s）" % (head, why) if head and why else head or "-"


def state(finding):
    if not finding.has_decision:
        return "未回答"
    return "%s%s" % (finding.decision, "（%s）" % finding.reason if finding.reason else "")


def brief(findings, latest, multi, limit=LIST_LIMIT):
    shown = ["#%s %s" % (label(f, latest, multi), cell(f.short)) for f in findings[:limit]]
    rest = findings[limit:]
    if rest:
        shown.append("ほか %d 件（%s）" % (len(rest), ", ".join("#" + label(f, latest, multi) for f in rest)))
    return shown


def innermost(context, target, names, own_changed):
    """変わった節のうち、下位の節の変更で変わっただけの上位の節を除く。

    上位の節そのものの本文が変わったとき（own_changed に入っている）は残す。節そのものの本文の変化が
    分からない（前回の snapshot に記録が無い）ときは、何も除かない。
    """
    if own_changed is None:
        return names
    try:
        bodies = finding_rules.sections(Path(context.path(target)).read_text(encoding="utf-8"))
    except OSError:
        return names
    def contains(parent, child):
        return parent != child and child and child in bodies and bodies[child].splitlines()[0] in bodies.get(parent, "").splitlines()[1:]
    return [n for n in names if n in own_changed or not any(contains(n, other) for other in names)]


def under(context, target, name, asked):
    """節 name が、修正を指示した節（asked）か、その下位の節か。"""
    if name in asked:
        return True
    try:
        bodies = finding_rules.sections(Path(context.path(target)).read_text(encoding="utf-8"))
    except OSError:
        return False
    first = (bodies.get(name) or "").splitlines()[:1]
    return bool(name and first) and any(parent and first[0] in bodies.get(parent, "").splitlines()[1:] for parent in asked)


def changes(context):
    """前回の検査から変わった節と、修正の指示に無い節の変更（修正の回だけ）。"""
    try:
        snapshot = snapshot_artifacts.load(context)
    except (OSError, ValueError):
        return []
    changed = snapshot.get("changed_sections") or {}
    if snapshot.get("full_inspection"):
        return ["### 前回の検査（%s 回目）からの変更" % snapshot.get("previous_run"), "",
                "- %s。対象の全体を見てください。" % snapshot["full_inspection"], ""]
    if not changed:
        return []
    import repair_requests
    request = repair_requests.pending(context) if repair_requests.is_revise(context) else None
    expected = set()
    if request:
        record = review_contract.read(context)
        for row in request.get("findings", []):
            found = next((f for r in record.runs for f in r.findings if f.key == (row["scope"], row["run"], row["number"])), None)
            if found is not None:
                path, heading, _ = finding_rules.parse_location(found.location)
                expected.add((path, heading))
    lines = ["### 前回の検査（%s 回目）からの変更" % snapshot.get("previous_run"), ""]
    for target, names in changed.items():
        if names == ["*"]:
            lines.append("- `%s`：新しいファイル" % target)
            continue
        names = innermost(context, target, names, (snapshot.get("changed_own") or {}).get(target, []) if "changed_own" in snapshot else None)
        lines.append("- `%s`：%s" % (target, "、".join(n or "（冒頭）" for n in names)))
        if request:
            headings = [heading for path, heading in expected if path == target]
            if any(not heading for heading in headings):
                continue  # ファイル全体の修正を指示した（節を指していない）
            hashes = snapshot.get("sections", {}).get(target, {})
            asked = {finding_rules.find_section(hashes, heading) for heading in headings}
            outside = [n or "（冒頭）" for n in names if not under(context, target, n, asked)]
            if outside:
                lines.append("  - 修正の指示に無い節の変更：%s（意図した変更か確かめてください）" % "、".join(outside))
    return lines + [""]


def finding_table(lines, findings, latest, multi):
    lines += ["| # | 種類 | 対象箇所 | 要約 | AI の推奨 | 判断 |", "|---|---|---|---|---|---|"]
    for f in findings:
        lines.append("| %s | %s | %s | %s | %s | %s |" % (label(f, latest, multi), cell(f.kind or "-"), cell(f.location),
                                                     cell(f.short), cell(recommended(f)), cell(state(f))))


def render_scope(lines, context, view, multi):
    """1 スコープ分の指摘。返り値は未回答の件数。"""
    run = view.run
    targets = review_contract.targets_for(context, view.scope) if view.scope != "cross" else run.targets
    latest = run.number
    if multi:
        lines += ["#### %s" % view.scope, ""]
    lines.append("**対象**: %s（スコープ: %s / %d 回目）" % (" / ".join("`%s`" % t for t in targets), scope_label(view.scope), run.number))
    layers = "① / ②" if run.layers == "①②" else run.layers
    if run.layers == "①":
        layers += "（① だけ実行。② が未実施のため、このままでは承認できません）"
    elif run.layers == "②":
        layers += "（形式検査を持たない横断スコープのため ② のみ）"
    lines += ["**実行した層**: %s" % layers, ""]
    if not run.findings:
        lines += ["**指摘**: なし（0 件。検査は実行済み）", ""]
    if view.critical:
        lines += ["**重大**（%d 件。1 件ずつ判断してください）" % len(view.critical), ""]
        finding_table(lines, view.critical, latest, multi)
        lines.append("")
    members = [f for b in view.bundles for f in b.findings]
    if view.singles or members:
        lines += ["**要判断**（%d 件）" % (len(view.singles) + len(members)), ""]
    if view.bundles:
        lines += ["| 束 | 観点 | 種類 | 件数 | 番号 | AI の推奨（先頭の指摘） |", "|---|---|---|---|---|---|"]
        for b in view.bundles:
            lines.append("| %s | %s | %s | %d | %s | %s |" % (b.name, cell(b.gate), cell(b.kind), len(b.findings),
                                                          " ".join("#" + label(f, latest, multi) for f in b.findings),
                                                          cell(recommended(b.findings[0]))))
        lines.append("")
    individual = view.singles[:review_view.INDIVIDUAL_LIMIT]
    if individual:
        finding_table(lines, individual, latest, multi)
        rest = view.singles[review_view.INDIVIDUAL_LIMIT:]
        if rest:
            lines.append("| … | | | ほか %d 件（%s） | | |" % (len(rest), " ".join("#" + label(f, latest, multi) for f in rest)))
        lines.append("")
    room = review_view.INDIVIDUAL_LIMIT - len(individual)
    if room > 0 and members:
        lines += ["束の内訳（束でまとめて答えるか、番号で 1 件ずつ答えてください）", ""]
        lines += ["- [%s] #%s %s" % (b.name, label(f, latest, multi), cell(f.short)) for b in view.bundles for f in b.findings][:room]
        lines.append("")
    undecided = sum(1 for f in run.findings if not f.has_decision)
    open_fix = [f for f in view.auto_fix if f.is_open]
    if open_fix:
        lines += ["**AI が修正案で直す軽微**（%d 件。判断は不要。修正の回で直し、再検査で確かめます）" % len(open_fix)]
        lines += ["- " + line for line in brief(open_fix, latest, multi)] + [""]
    if view.carried:
        lines.append("**前回までの指摘**（今回件数に含めない）")
        for f in view.carried:
            if not f.has_decision:
                text = "判断が未回答"
                undecided += 1
            elif f.is_open:
                text = "%s（未解消。再検査で出なくなれば自動で解消を記録します）" % f.decision
            else:
                text = "%s（残件として持ち越し。判断を変える場合は `%s:<記号>`）" % (f.decision, label(f, latest, multi))
            lines.append("- #%s %s [%s] — %s" % (label(f, latest, multi), cell(f.short), cell(f.location), text))
        lines.append("")
    lines.append("**差戻し先の候補**（ゲートの提示。戻すかどうかは判断に含めてください）")
    lines += ["- #%s: %s（%s）" % (c["指摘番号"], c["宛先"], c["理由"]) for c in run.returns] or ["- なし"]
    lines.append("")
    return undecided


def automatic(views, multi):
    """system が自動で処理した指摘（見なくてよいもの）の一覧。"""
    lines = []
    for view in views:
        latest = view.run.number
        prefix = "%s：" % view.scope if multi else ""
        if view.auto_kept:
            lines.append("- %s前回と同じ判断を引き継いだ指摘（箇所に変更なし）%d 件" % (prefix, len(view.auto_kept)))
            lines += ["  - " + line for line in brief(view.auto_kept, latest, multi)]
        if view.auto_resolved:
            lines.append("- %s再検査で出なくなり、解消を記録した指摘 %d 件" % (prefix, len(view.auto_resolved)))
            lines += ["  - " + line for line in brief(view.auto_resolved, latest, multi)]
        if view.excluded:
            lines.append("- %s前提（工程の境界・確定した回答・却下から学んだ扱い）などで出さなかった指摘 %d 件" % (prefix, len(view.excluded)))
            lines += ["  - %s（%s）" % (cell(row["要約"]), cell(row["除外の出典"])) for row in view.excluded[:LIST_LIMIT]]
    return lines


def reevaluated(context, views):
    """再評価の回なら、切り替え前の指摘を何件見直し、何件が残ったかを示す。"""
    try:
        snapshot = snapshot_artifacts.load(context)
    except (OSError, ValueError):
        return []
    entry = snapshot.get("reevaluation")
    view = next((v for v in views if v.scope == context.scope), None)
    if not entry or view is None or snapshot.get("run") != view.run.number:
        return []
    return ["- 切り替え前の指摘 %d 件を再評価した（%d 回目の検査を新しい決まりで見直した）：人に出す指摘として残った %d 件、"
            "出さなかった %d 件（上の一覧と除外の記録のとおり）。元の指摘は再評価の回へ移した"
            % (len(entry["findings"]), entry["run"], len([f for f in view.run.findings if not f.by_system]), len(view.run.excluded))]


ANSWERS = [
    "**答え方**（後に書いたものが優先。束・範囲でまとめて答えられます）",
    "- **A: 修正** — このフェーズ内で直す",
    "- **B: 差戻し** — 上流フェーズ / フロー外の不備として戻す",
    "- **C: 対応せず進める** — 直さずに進める（**理由が必須**）。区分を `C[指摘の誤り]` `C[対象外]` `C[後で決める]` `C[解釈で対応]` で付ける。"
    "対象外・後で決めるに `+` を付けると（例 `C[後で決める+]`）、次の検査から同じ扱いにします",
    "- **D: 未対応** — 今回は判断を保留し、残件として持ち越す（**理由が必須**）",
    "- **推奨** — AI の推奨を採用する（修正なら修正案がそのまま修正の指示になります）",
    "",
]


def main():
    context = phase_rules.gate_context()
    try:
        record = review_contract.read(context)
        seal = inspection_seal.verify(context, record)
        print('AIDD-REVIEW-CONTEXT: '+json.dumps({'unit':context.unit,'snapshot':seal['snapshot'],
              'run':seal['run'],'inspection_hash':seal['record_hash']},ensure_ascii=False))
        scopes = review_contract.scopes(context)
        multi = len(scopes) > 1
        for scope in scopes:
            review_contract.inspection(context, record, scope)
        views = review_view.views(context, record)
        gate_path = phase_rules.PHASES[context.process][1]
        points, internal = viewpoints(context.process)
        lines = ["**Phase %s（%s）の品質ゲートを実行しました。**" % (context.phase, NAMES.get(context.process, context.process)), ""]
        if points.get("see"):
            lines += ["### この工程で見る観点", ""] + ["- " + v for v in points["see"]] + [""]
        lines += ["### 見なくてよいもの", ""]
        if points.get("checked"):
            lines.append("- L4 が検査済みの項目：" + "、".join(points["checked"]))
        lines.append("- %s（記録は `%s`）" % (internal or "AI 内部のファイル", gate_path))
        lines += automatic(views, multi) + reevaluated(context, views) + [""]
        lines += changes(context)
        lines += ["### 判断が必要な指摘", ""]
        undecided_total = sum(render_scope(lines, context, view, multi) for view in views)
        if undecided_total:
            example = ("回答例: `%s 1:推奨 / %s 2:C[後で決める+] design で決める`（複数の範囲をまとめて確認するため、# の欄のとおり範囲を付けて答える）"
                       % (scopes[0], scopes[0]) if multi else
                       "回答例: `1:推奨 / 束1:C[後で決める+] 桁数は design で決める / 3〜5:A / 7:D 次回まで保留`")
            lines += ANSWERS + [example, "全件を同じ判断にする場合は `全件:A` と書いてください。根拠と修正案は `詳細 <番号>` で表示します。", ""]
        fixes = [f for view in views for f in view.run.findings + view.carried if f.decision == "修正" and f.is_open]
        if fixes and not undecided_total:
            lines.append("修正（A）と AI が直す軽微は、修正の指示を書かずに修正の回へ回せます（repair の findings に \"all-fixes\"）。"
                         "AI の推奨を採用していない修正には、修正の指示を書いてください。")
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
        phase_rules.fail(str(error))
    raise SystemExit(phase_rules.EXIT_WAIT)


if __name__ == "__main__":
    main()
