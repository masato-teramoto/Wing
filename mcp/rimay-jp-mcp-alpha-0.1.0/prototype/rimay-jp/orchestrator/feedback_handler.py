"""feedback-handler: 下流で発見された問題の原因分類と還流（Phase 3F）。

処理（構想書 §21 Phase 3F / §14.12）:
  問題 → 原因分類 → 要求スロット／知識アセット／Rule／Validator／Generatorへ関連付け
       → regression Corpus追加候補 ＋ 改善Backlogエントリ

原因分類（GATE-3F: 要求変更・規則変更・辞書変更・Generator変更の区別＋Validator）:
  requirement_change / knowledge_change / rule_change / validator_change / generator_change

分類は構造化されたcontextフィールドに対する決定論的規則で行う。
LLMを接続する場合は候補生成のみを担い、本規則が最終分類を確定する。
"""
from . import _ROOT  # noqa: F401


def handle(feedback: dict) -> dict:
    """戻り値: {feedback_id, cause, targets, regression_candidate, backlog_entry}。"""
    ctx = feedback.get("context") or {}
    fid = feedback["case_id"]

    # --- 辞書変更（knowledge_change） ---
    if ctx.get("unknown_term"):
        surface = ctx["unknown_term"]
        return _result(fid, "knowledge_change",
                       [{"kind": "term_dictionary", "reference": f"surface:{surface}"}],
                       regression={
                           "kind": "lexicon_positive_case",
                           "proposal": f"用語「{surface}」を辞書へ追加後、同語を含む要求文が"
                                       f"受理されることを検証するケース",
                           "input_surface": surface},
                       backlog={"kind": "term_addition",
                                "target_asset": "lexicon/terms.yaml",
                                "proposal": f"用語「{surface}」の追加（型・内部IDは用語管理者が確定）"})
    if ctx.get("missing_synonym"):
        ms = ctx["missing_synonym"]
        return _result(fid, "knowledge_change",
                       [{"kind": "term_dictionary", "reference": f"term:{ms['term_id']}"}],
                       regression={
                           "kind": "lexicon_synonym_case",
                           "proposal": f"同義語「{ms['surface']}」が {ms['term_id']} へ"
                                       f"正規化されることを検証するケース",
                           "input_surface": ms["surface"], "term_id": ms["term_id"]},
                       backlog={"kind": "synonym_addition",
                                "target_asset": "lexicon/terms.yaml",
                                "proposal": f"{ms['term_id']} へ同義語「{ms['surface']}」を追加"})
    if ctx.get("unknown_state"):
        us = ctx["unknown_state"]
        return _result(fid, "knowledge_change",
                       [{"kind": "state_model", "reference": f"property:{us['property']}"}],
                       regression={
                           "kind": "state_model_case",
                           "proposal": f"{us['property']} の状態「{us['value']}」追加後、"
                                       f"DOMAIN findingが出ないことを検証するケース",
                           "property": us["property"], "value": us["value"]},
                       backlog={"kind": "state_addition",
                                "target_asset": "lexicon/business-rules.yaml",
                                "proposal": f"{us['property']} へ状態 {us['value']} と遷移を追加"})
    if ctx.get("missing_business_rule"):
        br = ctx["missing_business_rule"]
        return _result(fid, "knowledge_change",
                       [{"kind": "business_rule", "reference": "knowledge_bank"}],
                       regression={
                           "kind": "routing_case",
                           "proposal": f"業務ルール追加後、条件「{br}」がルーティングで"
                                       f"根拠付けされることを検証するケース",
                           "predicate": br},
                       backlog={"kind": "business_rule_addition",
                                "target_asset": "lexicon/business-rules.yaml",
                                "proposal": f"業務ルールの追加: {br}"})

    # --- Validator変更 ---
    if ctx.get("undetected_smell"):
        w = ctx["undetected_smell"]
        return _result(fid, "validator_change",
                       [{"kind": "validator", "reference": "validate_core#vague_words"}],
                       regression={
                           "kind": "negative_case",
                           "proposal": f"「{w}」を含む要求文がQUALITY-AMBIGUOUSで"
                                       f"拒否されることを検証する負例",
                           "input_word": w,
                           "expected_codes": ["QUALITY-AMBIGUOUS"]},
                       backlog={"kind": "validator_rule_addition",
                                "target_asset": "core/rimay_jp_core/normalizer.py#_VAGUE_WORDS",
                                "proposal": f"曖昧語リストへ「{w}」を追加"})
    if ctx.get("misclassification"):
        mc = ctx["misclassification"]
        return _result(fid, "validator_change",
                       [{"kind": "validator",
                         "reference": "information-classifier#signals"}],
                       regression={
                           "kind": "classification_case",
                           "proposal": f"シグナル追加後、当該文が {mc['expected']} へ"
                                       f"分類されることを検証する分類ケース",
                           "input_text": mc["text"],
                           "expected_classification": mc["expected"],
                           "observed_classification": mc.get("observed")},
                       backlog={"kind": "classifier_signal_addition",
                                "target_asset":
                                    "orchestrator/information_classifier.py#_RULES",
                                "proposal": f"{mc['expected']} のシグナル規則を追加"
                                            f"（観測: {mc.get('observed')}へ誤分類）"})
    if ctx.get("severity_issue"):
        si = ctx["severity_issue"]
        return _result(fid, "validator_change",
                       [{"kind": "validator", "reference": f"finding:{si['code']}"}],
                       regression=None,  # 重大度調整は方針判断であり再現テスト対象外
                       backlog={"kind": "severity_review",
                                "target_asset": "canonical/finding-code-catalog.yaml",
                                "proposal": f"{si['code']} の severity/blocking の再評価"})

    # --- 規則変更（rule_change） ---
    if ctx.get("missing_question"):
        mq = ctx["missing_question"]
        return _result(fid, "rule_change",
                       [{"kind": "orchestration_rule",
                         "reference": f"slot:{mq['slot']}"}],
                       regression={
                           "kind": "dialogue_case",
                           "proposal": f"スロット {mq['slot']} が未確定のとき質問が"
                                       f"発火することを検証する対話ケース",
                           "target_slot": mq["slot"]},
                       backlog={"kind": "rule_addition",
                                "target_asset": "orchestrator/rules/mvp-rules.yaml",
                                "proposal": f"{mq['slot']} の確認質問Ruleを追加"})
    if ctx.get("question_field_issue"):
        qf = ctx["question_field_issue"]
        return _result(fid, "rule_change",
                       [{"kind": "orchestration_rule",
                         "reference": f"question-planner#{qf['field']}"}],
                       regression={
                           "kind": "dialogue_field_case",
                           "proposal": f"全質問インスタンスが {qf['field']} を"
                                       f"保持することを検証するケース"
                                       f"（経路差による欠落の再発防止）",
                           "required_field": qf["field"],
                           "origin_rule_id": qf.get("rule_id")},
                       backlog={"kind": "planner_field_alignment",
                                "target_asset": "orchestrator/question_planner.py",
                                "proposal": f"Rule由来質問の {qf['field']} を"
                                            f"Rule Assetのquestion_templateから写し、"
                                            f"finding由来質問とキー名を統一する"})
    if ctx.get("question_order_issue"):
        qo = ctx["question_order_issue"]
        return _result(fid, "rule_change",
                       [{"kind": "orchestration_rule",
                         "reference": f"rules:{qo['first']},{qo['second']}"}],
                       regression={
                           "kind": "dialogue_order_case",
                           "proposal": f"{qo['second']} が {qo['first']} より先に質問される"
                                       f"ことを検証する順序ケース",
                           "expected_order": [qo["second"], qo["first"]]},
                       backlog={"kind": "rule_priority_review",
                                "target_asset": "orchestrator/rules/mvp-rules.yaml",
                                "proposal": "stage/priorityの再調整"})

    # --- Generator変更 ---
    if ctx.get("artifact_issue"):
        ai = ctx["artifact_issue"]
        return _result(fid, "generator_change",
                       [{"kind": "generator", "reference": f"generator:{ai['artifact']}"}],
                       regression={
                           "kind": "generation_case",
                           "proposal": f"{ai['artifact']} に「{ai['missing']}」が含まれる"
                                       f"ことを検証する生成ケース",
                           "expected_contains": ai["missing"]},
                       backlog={"kind": "generator_fix",
                                "target_asset": f"generators/{ai['artifact']}.py",
                                "proposal": f"{ai['missing']} の生成対応"})

    # --- 要求変更（requirement_change） ---
    if ctx.get("requirement_id") and ctx.get("slot"):
        return _result(fid, "requirement_change",
                       [{"kind": "requirement_slot",
                         "reference": f"{ctx['requirement_id']}#{ctx['slot']}"}],
                       regression={
                           "kind": "requirement_update_case",
                           "proposal": "修正後の期待値でcorpusケースを更新し回帰させる。"
                                       "承認済み要求の変更は新revisionをcandidateとして"
                                       "作成し再承認する（§5）",
                           "requirement_id": ctx["requirement_id"],
                           "slot": ctx["slot"],
                           "observed": ctx.get("observed"),
                           "expected_value": ctx.get("expected_value")},
                       backlog=None)

    return _result(fid, "unmapped", [], None, None)


def _result(fid, cause, targets, regression, backlog):
    out = {"feedback_id": fid, "cause": cause, "targets": targets,
           "regression_candidate": None, "backlog_entry": None}
    if regression is not None:
        out["regression_candidate"] = {"case_id": f"REG-{fid}",
                                       "origin_feedback": fid, "status": "candidate",
                                       **regression}
    if backlog is not None:
        out["backlog_entry"] = {"id": f"KB-{fid}", "source_feedback": fid,
                                "status": "proposed", **backlog}
    return out
