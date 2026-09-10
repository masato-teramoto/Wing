"""question-planner: Rule Engineの発火結果を質問インスタンスと自動補完へ振り分ける（Phase 3C）。

- 質問には rule_id・target_path・stage を必ず付け、
  「質問と不足スロット、適用Ruleの対応」を説明可能にする（GATE-3C）。
- APPLY_PROFILE_MAPPING は人間確認を要しない表記事項の自動補完として分離する。
"""
from . import _ROOT  # noqa: F401
from .rule_engine import evaluate
from rimay_jp_core.lexicon import case_frames  # noqa: E402

_ASK_TYPES = {"ASK_USER", "ASK_ACTION_MEANING", "ASK_MEASURABLE_CRITERIA"}


def plan(canonical: dict, fired_once: set[str] | None = None) -> dict:
    """戻り値: {questions: [...], auto_actions: [...]}（実行順ソート済み）。"""
    questions = []
    auto_actions = []
    for i, inst in enumerate(evaluate(canonical, fired_once)):
        if inst["action_type"] in _ASK_TYPES:
            q = dict(inst)
            q["question_id"] = f"Q{len(questions) + 1}"
            # 質問文の正規キーは question_text（FB-014）。Rule由来は Rule Asset の
            # question_template から写し、finding由来（repair_planner）と統一する
            # ——統合契約§6のquestionRecordがquestion_text必須のため。
            if not q.get("question_text"):
                q["question_text"] = inst.get("question_template") or ""
            if inst["action_type"] == "ASK_ACTION_MEANING":
                q["choices"] = _action_choices(canonical, inst["target_path"])
            questions.append(q)
        else:
            auto_actions.append(inst)
    return {"questions": questions, "auto_actions": auto_actions}


def _action_choices(canonical: dict, pointer: str) -> list[str]:
    slot = canonical["resolution"]["slots"].get(pointer) or {}
    cands = [c["value"] for c in slot.get("candidates") or []]
    if cands:
        return cands
    from .rule_engine import value_at
    v = value_at(canonical, pointer)
    return [v] if v else sorted(case_frames().keys())
