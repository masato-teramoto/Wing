"""split-proposal: PROPOSE_SPLIT dispositionの決定論的分割提案（Step 5、ADR-0012 D7）。

- 提案は「作る」だけで、元Canonicalの意味部分（canonical_hash対象）を変更しない。
  承認までは提案オブジェクトのみが存在する（意図しない意味変更率0%の構造的保証）。
- 分割は表層文字列の決定論的操作に限定する:
  - conjunction_split: 「XおよびYしなければならない」→ 各動作1件の2要求（両立・意味保存）
  - or_condition_split: 「A場合またはB場合、Z」→ 各条件1件で同一応答の2要求（両立・意味保存）
  値の推測・意味の補完はしない。分割後の不足補完は各partの通常経路
  （candidate-extractor → 質問 → 根拠付きPatch）が担う。
- accept_split は人間承認後にのみ呼ぶ。各partを通常抽出経路へ入れ、
  traceability（kind=requirement、canonical_hash対象外）で親子を双方向に結ぶ。
  親のstatus変更（superseded化）は承認ワークフローの責務であり、ここでは推奨のみ返す。
"""
from __future__ import annotations

import re

from . import _ROOT  # noqa: F401

# 「〜を X および Y しなければ/してはならない」（応答動作の連結）
_CONJUNCTION = re.compile(
    r"^(?P<head>.*を)(?P<v1>[^、。]+?)および(?P<v2>[^、。]+?)"
    r"(?P<tail>(?:しなければならない|してはならない)。?)$")

# 「A場合 または/もしくは B場合、Z」（トリガー条件の並列）
_OR_CONDITION = re.compile(
    r"^(?P<c1>.+?場合)(?:または|もしくは)(?P<c2>.+場合)、(?P<resp>.+)$")


def _conjunction_split(text: str) -> list[str] | None:
    m = _CONJUNCTION.match(text.strip())
    if not m:
        return None
    return [m["head"] + m["v1"] + m["tail"], m["head"] + m["v2"] + m["tail"]]


def _or_condition_split(text: str) -> list[str] | None:
    m = _OR_CONDITION.match(text.strip())
    if not m:
        return None
    return [f"{m['c1']}、{m['resp']}", f"{m['c2']}、{m['resp']}"]


_STRATEGIES = {
    "MULTIPLE_PRIMARY_ACTIONS": ("conjunction_split", _conjunction_split),
    "COORDINATION_AMBIGUITY": ("or_condition_split", _or_condition_split),
}


def propose_split(canonical: dict, finding: dict) -> dict | None:
    """finding → 分割提案。決定論的に分割できない場合はNone（HUMAN_REVIEWへ）。"""
    code = finding["normalized_issue_code"]
    if code not in _STRATEGIES:
        return None
    strategy, fn = _STRATEGIES[code]
    text = (canonical.get("source") or {}).get("text") or ""
    parts = fn(text)
    if not parts:
        return None
    rid = canonical["requirement_id"]
    return {
        "proposal_id": f"SPL-{finding['finding_id']}",
        "origin_requirement_id": rid,
        "origin_finding_id": finding["finding_id"],
        "normalized_issue_code": code,
        "source_rule_id": finding.get("source_rule_id"),
        "strategy": strategy,
        "status": "proposed",  # proposed → accepted / rejected（人間判断）
        "parts": [{"part_id": f"{rid}-S{i}", "text": t}
                  for i, t in enumerate(parts, 1)],
    }


def accept_split(canonical: dict, proposal: dict) -> dict:
    """人間承認後の分割実行。partごとに通常抽出し、親子traceabilityを張る。"""
    from .candidate_extractor import extract

    segs = (canonical.get("source") or {}).get("source_segments") or [{}]
    doc_id = segs[0].get("document_id") or canonical["requirement_id"]
    ref = proposal["proposal_id"]

    children = []
    for part in proposal["parts"]:
        out = extract({"document_id": doc_id, "text": part["text"]}, part["part_id"])
        child = out["canonical"]
        if child is not None:
            child["traceability"].append({
                "kind": "requirement",
                "reference": f"split-parent:{proposal['origin_requirement_id']}#{ref}",
            })
        children.append({"part_id": part["part_id"],
                         "extraction_mode": out["extraction_mode"],
                         "canonical": child})

    for part in proposal["parts"]:
        canonical["traceability"].append({
            "kind": "requirement",
            "reference": f"split-child:{part['part_id']}#{ref}",
        })
    proposal["status"] = "accepted"
    return {"children": children, "origin_status_recommendation": "superseded"}
