"""apply_canonical_patch: Canonical Requirementへの唯一の更新手段（構想書 §14.13）。

検査（違反はPATCH-INVALIDとして拒否し、Canonicalを変更しない）:
- canonical-patch.schema.json への適合
- base_revision の一致（楽観ロック。reason: revision_conflict）
- path が単一ノードのCanonicalPointer（'*'不可）
- expected_status と現在状態の一致
- confirmed への遷移に user_answer / knowledge_asset / rule の根拠
- 既存Provenanceの保持（追記のみ・削除しない）
適用成功時は revision を+1し、派生物（Parser結果・AST等価・sidecar・承認状態）を失効させる。
"""
import copy
import json
from functools import lru_cache

from jsonschema import Draft202012Validator

from .lexicon import ROOT
from .model import finding

_METHOD = {"user_answer": "user_confirmation",
           "knowledge_asset": "profile_mapping",
           "rule": "rule_application",
           "tool_result": "rule_application",
           "requirement_text": "deterministic_parse"}


@lru_cache(maxsize=1)
def _patch_validator() -> Draft202012Validator:
    with open(ROOT / "canonical" / "canonical-patch.schema.json", encoding="utf-8") as f:
        return Draft202012Validator(json.load(f))


def _set_value(canonical: dict, pointer: str, value):
    tokens = pointer.strip("/").split("/")
    node = canonical
    for t in tokens[:-1]:
        if isinstance(node, list):
            node = node[int(t)]
        else:
            if t not in node or node[t] is None:
                node[t] = {}
            node = node[t]
    leaf = tokens[-1]
    if isinstance(node, list):
        node[int(leaf)] = value
    else:
        node[leaf] = value


def apply_canonical_patch(canonical: dict, patch: dict) -> dict:
    """戻り値: {ok, findings, canonical}。失敗時はcanonicalを変更しない。"""
    errs = [e.message for e in _patch_validator().iter_errors(patch)]
    if errs:
        return {"ok": False, "canonical": canonical,
                "findings": [finding("PATCH-INVALID", f"PatchがSchemaに違反: {errs[0]}",
                                     patch.get("path"), reason="schema_violation")]}

    if patch["base_revision"] != canonical["revision"]:
        return {"ok": False, "canonical": canonical,
                "findings": [finding("PATCH-INVALID",
                                     f"revision競合: base={patch['base_revision']} "
                                     f"current={canonical['revision']}",
                                     patch["path"], reason="revision_conflict")]}

    path = patch["path"]
    if "*" in path:
        return {"ok": False, "canonical": canonical,
                "findings": [finding("PATCH-INVALID",
                                     "PatchのpathにRuleSelectorは使用できません。",
                                     path, reason="selector_in_path")]}

    slots = canonical["resolution"]["slots"]
    current = slots.get(path, {"status": "unknown"})
    if patch.get("expected_status") and current["status"] != patch["expected_status"]:
        return {"ok": False, "canonical": canonical,
                "findings": [finding("PATCH-INVALID",
                                     f"expected_status不一致: expected="
                                     f"{patch['expected_status']} current={current['status']}",
                                     path, reason="status_conflict")]}

    new_status = patch.get("new_status")
    if new_status == "confirmed" and patch["evidence"]["type"] not in (
            "user_answer", "knowledge_asset", "rule"):
        return {"ok": False, "canonical": canonical,
                "findings": [finding("PROVENANCE-MISSING",
                                     "confirmedへの遷移には利用者回答または確定規則の"
                                     "根拠が必要です。", path)]}

    # 適用（コピー上で行い、成功時のみ差し替える）
    c = copy.deepcopy(canonical)
    op = patch["operation"]
    if op == "replace_slot":
        _set_value(c, path, patch["new_value"])
    elif op == "revert_slot":
        _set_value(c, path, None)

    prv_id = f"PRV-{len(c['provenance']) + 1}"
    c["provenance"].append({
        "id": prv_id,
        "path": path,
        "source_type": patch["evidence"]["type"],
        "reference": patch["evidence"]["reference"],
        "resolution_method": _METHOD[patch["evidence"]["type"]],
    })
    slot = dict(c["resolution"]["slots"].get(path) or {})
    refs = list(slot.get("provenance_refs") or [])
    new_slot = {"status": new_status or slot.get("status", "proposed"),
                "provenance_refs": refs + [prv_id]}
    # 確定時は候補・確認要求を解消する。それ以外は維持する。
    if new_slot["status"] not in ("confirmed", "not_applicable"):
        if slot.get("confirmation_required"):
            new_slot["confirmation_required"] = True
        if slot.get("candidates"):
            new_slot["candidates"] = slot["candidates"]
    c["resolution"]["slots"][path] = new_slot
    c["revision"] += 1
    # Patch適用で失効する派生物（§5）。legacy findings[]は除去のみ（移行契約Phase B:
    # 新規書き込みはValidation Reportのみ。失効はvalidation_stateのSTALE検出が担う）。
    c.pop("findings", None)
    return {"ok": True, "canonical": c, "findings": []}
