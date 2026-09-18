"""information-classifier: source_segmentを§18の情報分類へ振り分ける（Phase 3A）。

決定論的シグナル規則で分類し、根拠（マッチしたシグナル）を必ず返す。
Requirement Candidate以外はRimay化の対象にしない（構想書 §18）。
"""
import re

CLASSIFICATIONS = [
    "context", "problem", "goal", "stakeholder_view", "assumption",
    "issue", "decision", "business_rule", "requirement_candidate",
]

# 評価順に並べたシグナル規則（先勝ち）。requirement判定より前に他分類を評価する。
_RULES: list[tuple[str, str]] = [
    ("assumption",            r"(前提とする|と想定する)。?$"),
    ("decision",              r"(を採用する|と決定した|方針とする)。?$"),
    # goal: 到達目標・願望の表明（FB-013で「〜たい」系を追補。「実現したい」だけでなく
    # 「作りたい」「見たい」等の動詞連用形＋たいを文末で拾う）。
    # 要求文はMUST形（しなければならない／してはならない）を必須とするため、
    # 「〜たい」を goal に採ってもrequirement_candidateとは衝突しない。
    ("goal",                  r"(を目指す|を目的とする|たい)。?$"),
    ("issue",                 r"(未定である|検討中である|未決である)。?$"),
    ("problem",               r"(課題である|問題がある|問題となっている|時間がかかっている)。?$"),
    ("stakeholder_view",      r"(という要望がある|との意見がある|という声がある|を要望している)。?$"),
    ("business_rule",         r"(を必要とする|を禁止とする|ものとする)。?$"),
    ("requirement_candidate", r"(しなければならない|してはならない|すること)。?$"),
]

# 弱シグナル: 対象（を格）を持つ動作文。確認を要する候補として扱う。
_WEAK_REQ = re.compile(r"を.+(?<!てい)(る|す)。?$")


def classify(text: str) -> dict:
    """戻り値: {classification, rationale, strength}。"""
    t = re.sub(r"\s+", "", text)
    for cls, pattern in _RULES:
        m = re.search(pattern, t)
        if m:
            return {"classification": cls, "rationale": f"シグナル一致: 「{m.group(0)}」",
                    "strength": "strong"}
    if _WEAK_REQ.search(t):
        return {"classification": "requirement_candidate",
                "rationale": "弱シグナル: 対象（を格）を持つ動作文。分類の確認を要する",
                "strength": "weak"}
    return {"classification": "context",
            "rationale": "既知シグナルなし（既定分類）", "strength": "fallback"}
