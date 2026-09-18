"""experience-projections: Experience Storeから派生する再構築可能Projection（Step 7）。

- Projectionは正本（Experience Store）の**純関数**であり、いつでも100%再構築できる
  （Gate。レビュー§9「ProjectionはCanonicalと履歴から再構築可能でなければならない」）。
  時刻・乱数・外部状態に依存しない。
- 実装するProjection（レビュー§9の派生Projectionから、MVPで根拠を持てるもの）:
  - similar_case_index: 類似要求検索（決定論的特徴集合＋Jaccard係数）
  - repair_pairs: 修正前後ペア（patch_appliedレコードから）
  - question_success: 質問成功事例（rule_idごとの回答・確定件数）
  グラフ関係・ベクトル索引はStep 8（KG/SHACL、条件成立待ち）の責務。
- **類似事例は助言専用**: 自動確定根拠として使用しない（レビューStep 7）。
  Patch根拠に使える型は user_answer／knowledge_asset／rule のみで、
  similar_case は apply_canonical_patch が構造的に拒否する。
  さらに find_similar は参照履歴（reference record）を自動で残し、
  参照済みレコードのholdout昇格を不可能にする（評価リーク防止）。
"""
from __future__ import annotations

from . import _ROOT  # noqa: F401
from .experience_store import ExperienceStore
from rimay_jp_core.response_expression import iter_core_responses
from rimay_jp_core.condition_expression import (  # noqa: E402
    MultiValueRuntimeError,
    iter_core_conditions,
    iter_predicate_value_leaves,
    operator_operand_identity,
)

PROJECTION_VERSION = "0.1.0"


def _features(canonical: dict, issue_codes: list[str] | None = None) -> list[str]:
    """類似判定に使う決定論的特徴集合（値の推測なし・意味部分の構造特徴のみ）。"""
    feats: set[str] = set()
    core = canonical.get("rimay_core") or {}
    for _path, resp in iter_core_responses(
            core, source_text=(canonical.get("source") or {}).get("text")):
        fam = (resp.get("action") or {}).get("family")
        if fam:
            feats.add(f"family:{fam}")
        if resp.get("modality"):
            feats.add(f"modality:{resp['modality']}")
        frequency = resp.get("frequency")
        if isinstance(frequency, dict):
            feats.add(f"frequency:{frequency.get('value')}:{frequency.get('unit')}")
        for field in ("actor", "destination", "location", "theme", "content"):
            if resp.get(field):
                feats.add(f"{field}:{resp[field]}")
    for _path, cond in iter_core_conditions(core):
        if cond.get("type"):
            feats.add(f"cond:{cond['type']}")
        predicate = cond.get("predicate")
        if isinstance(predicate, dict):
            predicate_path = _path + "/predicate"
            identity = predicate.get("subject")
            if "operand" in predicate:
                try:
                    identity = "operand:" + operator_operand_identity(predicate["operand"])
                except ValueError as exc:
                    feats.add(f"predicate-invalid:{getattr(exc, 'code', 'OPERATOR_VALUE_INVALID')}")
                    continue
                operand = predicate["operand"]
                feats.add("operand-wrapper:" + operand["wrapper"])
                feats.add("operand-kind:" + operand["kind"])
                feats.add("operand-name:" + operand["name"])
            try:
                leaves = list(iter_predicate_value_leaves(
                    predicate, path=predicate_path))
            except MultiValueRuntimeError as exc:
                feats.add(f"predicate-invalid:{exc.code}:{exc.path}")
                continue
            if "value_expression" not in predicate:
                leaf = leaves[0][1]
                feats.add(
                    "predicate:"
                    f"{identity}:"
                    f"{predicate.get('operator')}:"
                    f"{leaf.get('value')}:"
                    f"{leaf.get('unit') or ''}"
                )
                continue

            def shape(node: dict) -> str:
                kind = node["kind"]
                if kind == "value":
                    return f"value:{node['value']}:{node.get('unit') or ''}"
                if kind == "group":
                    return "group(" + shape(node["expression"]) + ")"
                return kind + "(" + shape(node["left"]) + "," + shape(node["right"]) + ")"

            feats.add(
                "predicate-tree:"
                f"{identity}:{predicate.get('operator')}:"
                f"{shape(predicate['value_expression'])}"
            )
            for leaf_path, leaf in leaves:
                feats.add(
                    f"predicate-leaf:{leaf_path}:{leaf.get('value')}:"
                    f"{leaf.get('unit') or ''}"
                )
    for code in issue_codes or []:
        feats.add(f"issue:{code}")
    return sorted(feats)


def build_projections(store: ExperienceStore) -> dict:
    """Experience Store → 全Projection。純関数（同じストア→同じ出力）。"""
    reports_by_req: dict[str, list] = {}
    for r in store.records("validation_report"):
        reports_by_req.setdefault(r["requirement_id"], []).append(r)

    similar_index: dict[str, dict] = {}
    for r in store.canonical_revisions():
        canonical = r["payload"]["canonical"]
        codes = sorted({c for rep in reports_by_req.get(r["requirement_id"], [])
                        for c in rep["payload"].get("issue_codes") or []})
        similar_index[r["record_id"]] = {
            "requirement_id": r["requirement_id"],
            "revision": r.get("revision"),
            "source_text": (canonical.get("source") or {}).get("text") or "",
            "features": _features(canonical, codes),
        }

    repair_pairs = []
    for r in store.records("patch_applied"):
        p = r["payload"]
        repair_pairs.append({
            "requirement_id": r["requirement_id"],
            "target_path": p["target_path"],
            "issue_code": p.get("issue_code"),
            "question_rule_id": p.get("rule_id"),
            "before_status": p.get("before_status"),
            "after_value": p.get("after_value"),
            "answer": p.get("answer"),
            "evidence_type": p.get("evidence_type"),
            "resolved": bool(p.get("resolved")),
        })

    question_success: dict[str, dict] = {}
    for pair in repair_pairs:
        rid = pair["question_rule_id"] or "(finding)"
        s = question_success.setdefault(rid, {"asked": 0, "resolved": 0})
        s["asked"] += 1
        if pair["resolved"]:
            s["resolved"] += 1

    return {
        "meta": {"projection_version": PROJECTION_VERSION,
                 "record_count": len(store.records()),
                 "source": "experience-store"},
        "similar_case_index": similar_index,
        "repair_pairs": repair_pairs,
        "question_success": question_success,
    }


def find_similar(projections: dict, store: ExperienceStore, canonical: dict,
                 k: int = 3, min_score: float = 0.2) -> list[dict]:
    """類似事例検索（助言専用）。参照履歴を自動で残す（holdout昇格の未参照確認用）。

    戻り値の各要素は advisory=true を持ち、Patch根拠に使える形（evidence）を含まない。
    """
    query = set(_features(canonical))
    scored = []
    for rec_id, entry in projections["similar_case_index"].items():
        feats = set(entry["features"])
        union = query | feats
        score = len(query & feats) / len(union) if union else 0.0
        if score >= min_score:
            scored.append({"record_id": rec_id, "score": round(score, 4),
                           "requirement_id": entry["requirement_id"],
                           "source_text": entry["source_text"],
                           "advisory": True})
    scored.sort(key=lambda s: (-s["score"], s["record_id"]))
    hits = scored[:k]
    if hits:
        store.mark_referenced([h["record_id"] for h in hits],
                              "similar_case_search")
    return hits
