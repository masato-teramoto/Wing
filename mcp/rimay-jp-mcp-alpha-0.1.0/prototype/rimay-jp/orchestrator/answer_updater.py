"""answer-to-canonical-patch updater: 利用者回答を根拠付きCanonical Patchへ変換する（Phase 3C）。

apply_answer はPatchを「作る」だけであり、検査・適用は
rimay_jp_core.patch.apply_canonical_patch が行う（責務分離、llm-backend-design §6）。
"""
import re

from . import _ROOT  # noqa: F401
from rimay_jp_core.lexicon import lookup_jp, case_frames  # noqa: E402

_MODALITY = {"必須": "MUST", "禁止": "MUST_NOT",
             "しなければならない": "MUST", "してはならない": "MUST_NOT"}

# 標準動詞（〜する形）→ family
_VERB_TO_FAMILY = {f"{frame['japanese_canonical_verb']}": fam
                   for fam, frame in case_frames().items()}

_DEADLINE = re.compile(r"^([\d,，]+)秒以内$|^([\d,，]+)秒以内に$")


def apply_answer(canonical: dict, question: dict, answer_text: str) -> list[dict]:
    """回答 → Canonical Patchのリスト（適用はしない）。解決不能なら空リスト。"""
    path = question["target_path"]
    if "/operand" in path or "/value_expression" in path:
        # Dedicated typed/tree edit Rules are intentionally not adopted.
        return []
    slots = canonical["resolution"]["slots"]
    current = (slots.get(path) or {}).get("status", "unknown")
    base = {
        "requirement_id": canonical["requirement_id"],
        "base_revision": canonical["revision"],
        "expected_status": current,
        "evidence": {"type": "user_answer",
                     "reference": f"answer:{question['question_id']}"},
    }
    ans = answer_text.strip().strip("。")

    # モダリティ
    if path.endswith("/modality"):
        if ans in _MODALITY:
            return [{**base, "operation": "replace_slot", "path": path,
                     "new_value": _MODALITY[ans], "new_status": "confirmed"}]
        return []

    # Action family（標準動詞または候補ID）
    if path.endswith("/action/family"):
        fam = _VERB_TO_FAMILY.get(ans) or (ans if ans in case_frames() else None)
        if fam:
            return [{**base, "operation": "replace_slot", "path": path,
                     "new_value": fam, "new_status": "confirmed"}]
        return []

    # 時間制約（60秒以内 → value + unit の2 Patch）
    m = _DEADLINE.match(ans)
    if m and "/time_constraints/" in path:
        n = int((m.group(1) or m.group(2)).replace(",", "").replace("，", ""))
        unit_path = path.rsplit("/", 1)[0] + "/unit"
        return [
            {**base, "operation": "replace_slot", "path": path,
             "new_value": n, "new_status": "confirmed"},
            {"requirement_id": canonical["requirement_id"],
             "base_revision": canonical["revision"] + 1,  # 直前Patchの適用後
             "operation": "replace_slot", "path": unit_path,
             "new_value": "second", "new_status": "confirmed",
             "evidence": base["evidence"]},
        ]

    # 用語（辞書解決できた場合のみPatch化。根拠なき値は作らない）
    hit = lookup_jp(ans)
    if hit:
        return [{**base, "operation": "replace_slot", "path": path,
                 "new_value": hit[0], "new_status": "confirmed"}]
    return []
