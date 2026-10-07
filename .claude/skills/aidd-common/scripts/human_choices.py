"""人に聞く場面の選択肢（人が文字を入力せずに選べるようにする）。

ホストは返却の `choices` を、Claude Code の選択式の質問（1 回に 4 問まで・1 問に 4 択まで、「その他」で自由入力）で出す。
各選択肢の `answer` は、そのまま回答に使える文（判断は decisions の書き方）。選ばれた `answer` を `/` でつなぐと回答になる。
選択式の質問が使えない環境（非対話の実行など）では、ホストは同じ選択肢を番号付きの文で示し、文字の回答を受ける。

選択肢は AI の推奨と、よく使う判断から作る。差戻し（B）・未対応（D）・別の理由は「その他」で入力する。
"""
import finding_rules
import review_contract
import review_view

HEADER_LIMIT = 12
OTHER = "差戻し（B）・未対応（D）・別の理由は「その他」で入力"


def _label(finding, latest, multi):
    base = str(finding.number) if finding.run == latest else "%d-%d" % (finding.run, finding.number)
    return ("%s %s" % (finding.scope, base)) if multi else base


def uniform_recommendation(findings):
    """指摘すべての推奨が同じ判断なら (判断, 理由)。違えば ("", "")（束の「推奨」を出さない）。"""
    heads = []
    for finding in findings:
        try:
            heads.append(finding_rules.recommendation(finding.recommendation))
        except ValueError:
            return "", ""
    if heads and all(head == heads[0][0] for head, _ in heads):
        return heads[0]
    return "", ""


def _question(finding):
    """推奨が「質問：…」なら、その質問の文（人の回答が修正の指示になる）。"""
    text = str(finding.recommendation or "").strip()
    for head in ("質問：", "質問:"):
        if text.startswith(head):
            return text[len(head):].strip()
    return ""


def _decision_options(target, finding, members=None):
    """1 件（または束）の判断の選択肢。最大 4 つ。束は、全件の推奨が同じときだけ「推奨」を出す。"""
    recommended, why = uniform_recommendation(members or [finding])
    options = []
    if recommended in ("修正", "差戻し", "対応せず進める"):
        options.append({"label": "推奨：%s" % recommended, "description": why or "AI の推奨",
                        "answer": "%s:推奨" % target})
    if recommended != "修正":
        proposal = finding.suggestion if finding.suggestion not in ("", "-") else ""
        options.append({"label": "A 修正", "description": "この工程で直す" + ("（修正案：%s）" % proposal[:60] if proposal else ""),
                        "answer": "%s:A" % target})
    options.append({"label": "C 後で決める", "description": "後の工程で決める事項なので、今は直さずに進める",
                    "answer": "%s:C[後で決める] 後の工程で決める" % target})
    options.append({"label": "C 対象外", "description": "この工程の対象外なので、直さずに進める",
                    "answer": "%s:C[対象外] この工程の対象外" % target})
    return options[:4]


def _repaired(context, finding):
    """この指摘を含む修正の依頼が、修正の回で実行済みか（承認を待たずに、その回の検査の封印で決まる）。"""
    return review_contract.repair_executed(context, finding)


def review(context, record=None):
    """レビューで人に問う判断の選択肢。重大は 1 件ずつ、要判断は束ごと、束にならないものは 1 件ずつ。"""
    record = record or review_contract.read(context)
    views = review_view.views(context, record)
    multi = len(views) > 1
    questions = []
    for view in views:
        latest = view.run.number
        for f in view.critical + view.singles:
            if f.has_decision:
                continue
            target = _label(f, latest, multi)
            asked = _question(f)
            note = ("AI からの質問：%s　答えて直す場合は「その他」に `%s:A <回答>` と入力（回答が修正の指示になる）。" % (asked, target)
                    if asked else "")
            questions.append({"id": target, "header": ("#%s %s" % (target, f.level))[:HEADER_LIMIT],
                              "question": "%s（%s・%s）にどう対応しますか？ %s%s" % (f.short, f.kind or "種類なし", f.level, note, OTHER),
                              "options": _decision_options(target, f), "multiSelect": False})
        for bundle in view.bundles:
            if all(f.has_decision for f in bundle.findings):
                continue
            if bundle.legacy:
                questions.append(legacy_question(bundle))
                continue
            first = bundle.findings[0]
            summaries = " / ".join(f.short for f in bundle.findings[:3]) + (" ほか" if len(bundle.findings) > 3 else "")
            questions.append({"id": bundle.name, "header": ("%s %d件" % (bundle.name, len(bundle.findings)))[:HEADER_LIMIT],
                              "question": "%s（%s・%s %d 件：%s）をまとめてどう扱いますか？ 1 件だけ変える場合は「その他」で番号を指定。%s"
                                          % (bundle.name, bundle.kind, bundle.gate, len(bundle.findings), summaries, OTHER),
                              "options": _decision_options(bundle.name, first, bundle.findings), "multiSelect": False})
    if questions:
        return {"kind": "decisions", "questions": questions}
    import finding_triage
    to_send, to_confirm = [], []
    for view in views:
        for f in view.run.findings + view.carried:
            if f.decision != "修正" or not f.is_open:
                continue
            if review_contract.repair_covers(context, f):
                continue  # 修正の回を予約済み
            if _repaired(context, f) and f.run < view.run.number:
                to_confirm.append((view, f))  # 修正の回と再検査は済んだが、自動では解消されなかった
            else:
                to_send.append(f)
    if to_confirm:
        return {"kind": "resolve", "questions": [{
            "id": "resolve %s %d %d" % f.key, "header": ("#%s 解消" % _label(f, view.run.number, multi))[:HEADER_LIMIT],
            "question": "%s（前回「修正」を選んだ指摘）は、再検査で自動では解消されませんでした（節が特定できない・変わっていない など）。直っていますか？" % f.short,
            "options": [{"label": "解消を確認した", "description": "再検査の結果と本文を見て、直っていることを確かめた",
                         "answer": "resolve:%s %d %d" % f.key},
                        {"label": "まだ直っていない", "description": "もう一度修正に回す（修正の指示を書く）", "answer": "repair:manual"}],
            "multiSelect": False} for view, f in to_confirm]}
    fixes = to_send if all(finding_triage.auto_repairable(context, view.scope) for view in views) else []
    if fixes:
        return {"kind": "repair", "questions": [{
            "id": "repair", "header": "修正に回す", "question": "修正（A）の指摘と AI が直す軽微（%d 件）を修正の回へ回しますか？" % len(fixes),
            "options": [{"label": "修正案のとおり修正に回す", "description": "推奨を採用した修正と軽微は、修正案がそのまま指示になる",
                         "answer": "repair:all-fixes"},
                        {"label": "修正の指示を自分で書く", "description": "指示を書きたい指摘がある", "answer": "repair:manual"}],
            "multiSelect": False}]}
    try:
        review_contract.ready(context, record)
    except ValueError:
        return {"kind": "none", "questions": []}
    word = "確認" if context.is_cross else "承認"
    return {"kind": "approve", "questions": [{
        "id": "approve", "header": word, "question": "判断が揃いました。%sしますか？" % word,
        "options": [{"label": "%sする" % word, "description": "回答者の名前で%sを記録する" % word, "answer": "approve"},
                    {"label": "%sしない" % word, "description": "判断を変える・修正を指示する", "answer": "hold"}],
        "multiSelect": False}]}


def legacy_question(bundle):
    """切り替え前（旧形式）の未判断の指摘の束。再評価を勧め、まとめて閉じる選択肢も出す。"""
    count = len(bundle.findings)
    return {"id": bundle.name, "header": ("切替前 %d件" % count)[:HEADER_LIMIT],
            "question": "%s：切り替え前の版で出た未判断の指摘 %d 件があります。どう扱いますか？ 1 件ずつ答える場合は「その他」で番号を指定。"
                        % (bundle.name, count),
            "options": [{"label": "再評価する（推奨）",
                         "description": "AI が新しい決まりで見直す（前提に当たるもの・実在しないもの・重複を外し、重大度と推奨を付ける）。残ったものだけを判断する",
                         "answer": "reevaluate"},
                        {"label": "C 後で決める（まとめて）", "description": "全件を、後の工程で決める事項として直さずに進める",
                         "answer": "%s:C[後で決める] 切り替え前の指摘。後の工程で決める" % bundle.name},
                        {"label": "C 対象外（まとめて）", "description": "全件を、この工程の対象外として直さずに進める",
                         "answer": "%s:C[対象外] 切り替え前の指摘。この工程の対象外" % bundle.name}],
            "multiSelect": False}


def plan(context):
    options = [{"label": "了承する", "description": "示された計画のとおり進める", "answer": "accept-plan"}]
    if context.process in ("requirements", "design", "tasks"):
        options.append({"label": "対象・順序を変える", "description": "変更の指示は「その他」で入力", "answer": "change-plan"})
    else:
        options.append({"label": "条件を付けて了承する", "description": "条件は「その他」で入力（了承の記録に残る）", "answer": "accept-plan-with-note"})
    return {"kind": "plan", "questions": [{"id": "plan", "header": "実行計画", "question": "この実行計画で進めますか？",
                                           "options": options, "multiSelect": False}]}


DEFAULT_ANSWERS = [{"label": "RFP に無いので空欄にする", "description": "値を推測せず、不要理由「該当なし（RFP に記載なし）」を書いて進める",
                    "answer": "該当なし（RFP に記載なし）。値を推測せず、不要理由を併記する"},
                   {"label": "後の工程で決める", "description": "今は決めず、後の工程で決める旨を書いて進める",
                    "answer": "後の工程で決める。今は決めない旨を併記する"}]


def questions(items):
    """作成中の質問の選択肢。作成 Skill が `options`（2〜4 個の候補）を付けた質問はそれを使い、無ければ既定の 2 択を付ける。"""
    result = []
    for index, item in enumerate(items or [], 1):
        text = item.get("question") if isinstance(item, dict) else str(item)
        given = item.get("options") if isinstance(item, dict) else None
        options = []
        for option in (given or [])[:4]:
            label = option.get("label") if isinstance(option, dict) else str(option)
            options.append({"label": label[:40], "description": (option.get("description") if isinstance(option, dict) else "") or label,
                            "answer": (option.get("answer") if isinstance(option, dict) else None) or label})
        if len(options) < 2:
            options = DEFAULT_ANSWERS
        result.append({"id": "Q%d" % index, "header": "質問 %d" % index, "question": text, "options": options, "multiSelect": False})
    return {"kind": "answers", "questions": result} if result else {"kind": "none", "questions": []}
