"""experience-store: RQK-E/experience（Experience Store）の追記型一次記録（Step 7、ADR-0012 D4）。

- 一次記録（レビュー§9）: canonical_revision（スナップショット）・patch_applied
  （質問・回答・Patch）・validation_report・approval・feedback。
- governance記録も同一ストアに追記する: reference（類似検索等での参照履歴）・
  promotion（評価Corpusへの昇格）。ストア（JSONL）が唯一の正本であり、
  参照状態・昇格状態はレコードから導出する（Projectionと同じ再構築原則）。
- RQK-E/evaluation（corpus/）とは物理・運用分離（適応計画§2.2）。昇格は
  排他分岐（development/regression と holdout は相互排他）＋評価リーク防止
  （参照履歴のあるレコードはholdoutへ昇格不可＝未参照確認）を機械検査する。
- 決定論性: record_idは連番。時刻は記録しない（再構築同一性の比較を安定させる。
  必要になれば監査ログ側の責務とする）。
"""
from __future__ import annotations

import json
from pathlib import Path

from . import _ROOT  # noqa: F401

KINDS = ("canonical_revision", "patch_applied", "validation_report",
         "approval", "feedback", "reference", "promotion")
LANES = ("development_regression", "holdout")


class ExperienceStore:
    def __init__(self, path: Path, fresh: bool = False):
        self.path = Path(path)
        if fresh and self.path.exists():
            self.path.unlink()
        self._records: list[dict] = []
        if self.path.exists():
            for line in self.path.read_text(encoding="utf-8").splitlines():
                if line.strip():
                    self._records.append(json.loads(line))

    # ---- 一次記録 ----
    def append(self, kind: str, payload: dict,
               requirement_id: str | None = None,
               revision: int | None = None) -> dict:
        assert kind in KINDS, f"未知のrecord kind: {kind}"
        rec = {"record_id": f"EXP-{len(self._records) + 1:06d}", "kind": kind}
        if requirement_id is not None:
            rec["requirement_id"] = requirement_id
        if revision is not None:
            rec["revision"] = revision
        rec["payload"] = payload
        self._records.append(rec)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with self.path.open("a", encoding="utf-8") as f:
            f.write(json.dumps(rec, ensure_ascii=False, sort_keys=True) + "\n")
        return rec

    def records(self, kind: str | None = None) -> list[dict]:
        if kind is None:
            return list(self._records)
        return [r for r in self._records if r["kind"] == kind]

    def append_canonical_revision(self, canonical: dict) -> dict:
        """Active Schema適合済みのCanonical snapshotだけを書き込む。"""
        from rimay_jp_core.schema_check import validate_schema
        errors = validate_schema(canonical)
        if errors:
            raise ValueError(f"Canonical snapshot is not active-schema valid: {errors}")
        return self.append(
            "canonical_revision", {"canonical": canonical},
            requirement_id=canonical["requirement_id"],
            revision=canonical["revision"],
        )

    def canonical_revisions(self, *, migrate_legacy: bool = True) -> list[dict]:
        """Read Canonical records through the active compatibility reader."""
        records = self.records("canonical_revision")
        if not migrate_legacy:
            return records
        from rimay_jp_core.condition_expression import migrate_experience_store_records
        return migrate_experience_store_records(records)["records"]

    def get(self, record_id: str) -> dict | None:
        return next((r for r in self._records if r["record_id"] == record_id), None)

    # ---- 参照履歴（評価リーク防止の根拠。類似検索・Rule調整が参照を残す） ----
    def mark_referenced(self, record_ids: list[str], context: str) -> dict:
        return self.append("reference",
                           {"referenced_record_ids": sorted(record_ids),
                            "context": context})

    def referenced_ids(self) -> set[str]:
        out: set[str] = set()
        for r in self.records("reference"):
            out.update(r["payload"]["referenced_record_ids"])
        return out

    # ---- 昇格（§2.2の分岐プロセス。排他・リーク防止を機械検査） ----
    def promoted_lane(self, record_id: str) -> str | None:
        for r in self.records("promotion"):
            if r["payload"]["target_record_id"] == record_id:
                return r["payload"]["lane"]
        return None

    def promote(self, record_id: str, lane: str,
                anonymized: bool = False, reviewed: bool = False) -> dict:
        """経験レコードの評価Corpus昇格。戻り値: {ok, reason?, record?}。

        前提（§2.2プロセスの宣言）: anonymized=匿名化・品質確認済み、
        reviewed=正解付与・レビュー済み。いずれか欠けると拒否する。
        """
        if lane not in LANES:
            return {"ok": False, "reason": f"未知lane: {lane}"}
        if self.get(record_id) is None:
            return {"ok": False, "reason": f"レコード不在: {record_id}"}
        if not (anonymized and reviewed):
            return {"ok": False,
                    "reason": "匿名化・品質確認／正解付与・レビュー未了（直接自動登録の禁止）"}
        prior = self.promoted_lane(record_id)
        if prior is not None:
            return {"ok": False,
                    "reason": f"昇格済み（{prior}）。分岐は排他であり移動不可"}
        if lane == "holdout" and record_id in self.referenced_ids():
            return {"ok": False,
                    "reason": "参照履歴あり（類似検索等）。未参照確認に失敗＝評価リーク防止"}
        status = "frozen" if lane == "holdout" else "assigned"  # holdoutは凍結・隔離
        rec = self.append("promotion",
                          {"target_record_id": record_id, "lane": lane,
                           "status": status, "anonymized": anonymized,
                           "reviewed": reviewed})
        return {"ok": True, "record": rec}
