"""dialogue-state: 対話的要求補完の状態管理（Phase 3C）。

1ラウンド = 質問計画 → 回答1件 → Patch適用 → 関連Validator再実行 → 状態遷移判定。
- 回答によるPatchのみで要求モデルを更新する（表層文・Canonical全体の再生成なし）。
- 各ラウンドの適用Rule・質問・Patch・findingsを履歴として記録する。
- 要求statusの遷移: candidate → under_clarification → structurally_valid
  （review_ready以降はPhase 3D/承認の責務）。
"""
from . import _ROOT  # noqa: F401
from .question_planner import plan
from .answer_updater import apply_answer
from rimay_jp_core.patch import apply_canonical_patch  # noqa: E402
from rimay_jp_core.validator import validate, _ROLE_FIELD  # noqa: E402
from rimay_jp_core.lexicon import case_frames  # noqa: E402
from rimay_jp_core.model import is_blocked, set_slot  # noqa: E402
from rimay_jp_core.response_expression import (  # noqa: E402
    iter_core_responses, ResponseBlockError, ResponseExpressionError)
from rimay_jp_core.atomic_response import AtomicResponseError  # noqa: E402


class DialogueState:
    def __init__(self, canonical: dict):
        self.canonical = canonical
        self.history: list[dict] = []
        self.fired_once: set[str] = set()
        self._diagnose()
        self._auto_apply()
        self._transition()

    # ---- 内部処理 ----
    def _has_unadopted_expression_patch_boundary(self) -> bool:
        core = self.canonical["rimay_core"]
        if core.get("response_expression") is not None or \
            core.get("condition_expression") is not None or \
                core.get("response_block") is not None:
            return True
        try:
            from rimay_jp_core.condition_expression import iter_core_conditions
            if any(
                    "operand" in (condition.get("predicate") or {}) or
                    "value_expression" in (condition.get("predicate") or {})
                   for _path, condition in iter_core_conditions(core)):
                return True
        except ConditionExpressionError:
            return True
        try:
            return any(
                response.get("frequency") is not None or
                response.get("repository_trace") is not None
                for _path, response in iter_core_responses(
                    core,
                    source_text=(self.canonical.get("source") or {}).get("text"),
                )
            )
        except (ResponseBlockError, ResponseExpressionError, AtomicResponseError):
            return True

    def _diagnose(self):
        """Validator findingsを実体化する（必須Role欠落 → unknownスロット化）。"""
        findings = validate(self.canonical, phase2_slice=False)
        slots = self.canonical["resolution"]["slots"]
        for f in findings:
            p = f.get("path")
            if f["code"] == "JP-OMISSION" and p and p not in slots:
                set_slot(self.canonical, p, "unknown", confirmation_required=True)
        self.findings = findings

    def _auto_apply(self):
        """自動補完アクション（APPLY_PROFILE_MAPPING）を確定規則の根拠付きで適用する。"""
        if self._has_unadopted_expression_patch_boundary():
            # 現行Rule Assetはlegacy pointerだけを対象とする。leafを推測して
            # legacy pathへPatchしない（consumer migrationのfail-closed境界）。
            return
        for _ in range(5):  # 連鎖適用の上限
            auto = plan(self.canonical, self.fired_once)["auto_actions"]
            if not auto:
                return
            applied = False
            for act in auto:
                if act["action_type"] != "APPLY_PROFILE_MAPPING":
                    continue
                fam = (self.canonical["rimay_core"]["response"].get("action") or {}).get("family")
                frame = case_frames().get(fam)
                if not frame:
                    continue
                patch = {
                    "operation": "replace_slot",
                    "requirement_id": self.canonical["requirement_id"],
                    "base_revision": self.canonical["revision"],
                    "path": act["target_path"],
                    "expected_status": "unknown",
                    "new_value": frame["rimay_action_id"],
                    "new_status": "confirmed",
                    "evidence": {"type": "knowledge_asset",
                                 "reference": f"profile:rimay-jp-mvp-0.1.0"
                                              f"#action_classes/{fam}"},
                }
                res = apply_canonical_patch(self.canonical, patch)
                if res["ok"]:
                    self.canonical = res["canonical"]
                    self.history.append({"event": "auto_patch", "rule_id": act["rule_id"],
                                         "path": act["target_path"],
                                         "value": frame["rimay_action_id"]})
                    applied = True
            if not applied:
                return

    def _transition(self):
        blocked = is_blocked(self.findings)
        if self.open_questions():
            self.canonical["status"] = "under_clarification"
        elif not blocked:
            self.canonical["status"] = "structurally_valid"

    # ---- 公開API ----
    def open_questions(self) -> list[dict]:
        if self._has_unadopted_expression_patch_boundary():
            return []
        return plan(self.canonical, self.fired_once)["questions"]

    def answer(self, question: dict, answer_text: str) -> dict:
        """回答を適用し、再検査・自動補完・状態遷移まで行う。"""
        if self._has_unadopted_expression_patch_boundary():
            return {"ok": False,
                    "reason": "複合・Atomic ResponseまたはMulti-value treeの対話Patchはleaf対応Ruleの採用まで実行しません"}
        patches = apply_answer(self.canonical, question, answer_text)
        if not patches:
            self.history.append({"event": "answer_unresolved",
                                 "question_id": question["question_id"],
                                 "answer": answer_text})
            return {"ok": False, "reason": "回答を辞書・規則で解決できません"}
        for patch in patches:
            res = apply_canonical_patch(self.canonical, patch)
            if not res["ok"]:
                self.history.append({"event": "patch_rejected",
                                     "findings": res["findings"]})
                return {"ok": False, "reason": res["findings"][0]["message"]}
            self.canonical = res["canonical"]
        self.history.append({
            "event": "answered",
            "question_id": question["question_id"],
            "rule_id": question["rule_id"],
            "target_path": question["target_path"],
            "answer": answer_text,
            "patches": len(patches),
            "revision": self.canonical["revision"],
        })
        # 関連Validatorの再実行と診断・自動補完・遷移（GATE-3C条件2）
        self._diagnose()
        self._auto_apply()
        self._transition()
        return {"ok": True, "revision": self.canonical["revision"]}
