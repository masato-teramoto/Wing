"""repair-planner: Validation Reportのfindingをrepair_dispositionで修復アクションへ振り分ける
（Step 5: finding→壁打ち・Patch接続、Advisory mode。ADR-0012 D7、適応計画§3 Step 5）。

- D1（Rimay-JP基盤優先）: Rule Engine由来の質問（question-planner）を主とし、
  同一target_pathのASK_USER findingは既存質問の発火根拠
  （finding_ids・normalized_issue_code・出典Rule）として併合する。二重質問を作らない。
- Rule側に対応質問が無いASK_USER findingのみ、finding由来の補助質問を合成する。
  選択肢は辞書・状態モデル根拠付きのfix_candidatesに限る（値の推測はしない）。
- 本plannerはPatchを作らない・スロットを確定しない。確定は回答経由
  （answer_updater → apply_canonical_patch の根拠検査）のみ。
  「意味補完の無承認確定0件」Gateを構造的に保証する。
- Advisory mode（切替計画）: 非blocking findingからの項目は advisory=true として
  非遮断で提示する。Step 3でShadow（記録のみ）だったraw_text findingは、
  extra_findings経由で本plannerに入り、実行可能な修復提案として提示される。
"""
from __future__ import annotations

import re

from . import _ROOT  # noqa: F401
from .question_planner import plan
from .split_proposal import propose_split

# 表記専用path（Serializer入力。射影意味等価の対象外＝意味変更に数えない）
_NOTATION_PATHS = ("/rimay_core/response/action/rimay_action_id",)

# raw-text段の語順修復: 「応答、条件。」→「条件、応答。」（節の並べ替えのみ・意味不変）。
# 語順違反文はモダリティが文末に来ないため分類器が要求候補と認識できず、
# 抽出前のraw-text段でしか修復できない（REP-004で実証）。
_TRAILING_CONDITION = re.compile(
    r"^(?P<resp>.+?(?:しなければならない|してはならない))、"
    r"(?P<cond>.+?(?:とき|場合))。?$")


def surface_reorder(text: str) -> str | None:
    """条件節後置の決定論的並べ替え。適用不能ならNone。"""
    m = _TRAILING_CONDITION.match(text.strip())
    if not m:
        return None
    return f"{m['cond']}、{m['resp']}。"


def plan_repairs(canonical: dict | None, report: dict | None = None,
                 extra_findings: list[dict] | None = None,
                 rule_plan: dict | None = None,
                 raw_text: str | None = None) -> dict:
    """Validation Report＋追加finding（raw_text gate等）→ 修復計画。

    canonical=None はraw-text段（抽出前）の計画。Rule質問・分割提案は
    canonicalが前提のため合成しない。
    戻り値: {questions, split_proposals, knowledge_routes, auto_resolved,
             reclassify, human_review}。Patchは含まない（構造的保証）。
    """
    findings = list((report or {}).get("findings") or []) + list(extra_findings or [])
    if rule_plan is None:
        rule_plan = (plan(canonical) if canonical is not None
                     else {"questions": [], "auto_actions": []})
    questions = [dict(q) for q in rule_plan["questions"]]
    by_target = {q["target_path"]: q for q in questions if q.get("target_path")}
    out: dict = {"questions": questions, "split_proposals": [],
                 "knowledge_routes": [], "auto_resolved": [],
                 "reclassify": [], "human_review": []}

    for f in findings:
        disp = f["repair_disposition"]
        advisory = not f.get("blocking", False)

        if disp == "ASK_USER":
            target = (f.get("target_paths") or [None])[0]
            q = by_target.get(target)
            if q is not None:
                # Rule Engine質問を主とし、findingを発火根拠として併合（D1）
                q.setdefault("finding_ids", []).append(f["finding_id"])
                q["normalized_issue_code"] = f["normalized_issue_code"]
                q["finding_source_rule_id"] = f.get("source_rule_id")
                q.setdefault("advisory", False)
            else:
                q = _question_from_finding(f, len(questions), advisory)
                questions.append(q)
                if q.get("target_path"):
                    by_target[q["target_path"]] = q
        elif disp == "PROPOSE_SPLIT":
            prop = propose_split(canonical, f) if canonical is not None else None
            if prop:
                prop["advisory"] = advisory
                out["split_proposals"].append(prop)
            else:
                out["human_review"].append(
                    _item(f, advisory, note="決定論的分割案なし（人間判断へ）"))
        elif disp == "ROUTE_KNOWLEDGE":
            out["knowledge_routes"].append(
                _item(f, advisory, candidates=f.get("fix_candidates") or []))
        elif disp == "AUTO_SURFACE_REWRITE":
            src = raw_text or ((canonical or {}).get("source") or {}).get("text") or ""
            rewritten = surface_reorder(src)
            if rewritten:
                # raw-text段: 節の並べ替えのみ（意味不変）。再抽出は通常経路が担う。
                out["auto_resolved"].append(
                    _item(f, advisory, method="surface_reorder",
                          rewritten_text=rewritten,
                          note="条件節後置の並べ替え（表層のみ・意味不変）。再抽出へ"))
            else:
                out["auto_resolved"].append(
                    _item(f, advisory, method="serializer_regeneration",
                          note="Canonical確定後のSerializer再生成で解消（表層のみ・意味不変）"))
        elif disp == "RECLASSIFY":
            out["reclassify"].append(_item(f, advisory))
        else:  # HUMAN_REVIEW および未知disposition
            out["human_review"].append(_item(f, advisory))
    return out


def _item(f: dict, advisory: bool, **extra) -> dict:
    return {"finding_id": f["finding_id"],
            "normalized_issue_code": f["normalized_issue_code"],
            "source_rule_id": f.get("source_rule_id"),
            "target_paths": list(f.get("target_paths") or []),
            "advisory": advisory, **extra}


def _question_from_finding(f: dict, n: int, advisory: bool) -> dict:
    q = {
        "question_id": f"RQ{n + 1}",
        "origin": "finding",
        "finding_ids": [f["finding_id"]],
        "rule_id": f.get("source_rule_id"),
        "normalized_issue_code": f["normalized_issue_code"],
        "action_type": "ASK_USER",
        "target_path": (f.get("target_paths") or [""])[0],
        "question_text": f.get("clarification") or f["message"],
        "advisory": advisory,
    }
    if f.get("fix_candidates"):
        q["choices"] = [c["value"] for c in f["fix_candidates"]]
    return q


# ---- 意味差分検査（Gate: 意図しない意味変更率0%） ----

def meaning_diff(before: dict, after: dict) -> list[str]:
    """rimay_coreの変更点（追加・削除・値変更）をJSON Pointerで列挙する。"""
    out: list[str] = []
    _walk(before.get("rimay_core"), after.get("rimay_core"), "/rimay_core", out)
    return out


def _walk(a, b, ptr: str, out: list[str]):
    if isinstance(a, dict) and isinstance(b, dict):
        for k in sorted(set(a) | set(b)):
            _walk(a.get(k), b.get(k), f"{ptr}/{k}", out)
    elif isinstance(a, list) and isinstance(b, list):
        for i in range(max(len(a), len(b))):
            _walk(a[i] if i < len(a) else None,
                  b[i] if i < len(b) else None, f"{ptr}/{i}", out)
    elif a != b:
        out.append(ptr)


def unintended_meaning_changes(before: dict, after: dict,
                               allowed_paths: list[str]) -> list[str]:
    """許可path（回答対象とその配下）と表記専用path以外の意味変更を返す。"""
    allowed = tuple(p for p in allowed_paths if p)
    return [p for p in meaning_diff(before, after)
            if not any(p == a or p.startswith(a + "/") for a in allowed)
            and p not in _NOTATION_PATHS]
