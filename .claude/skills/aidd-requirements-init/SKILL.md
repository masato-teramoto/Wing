---
name: aidd-requirements-init
description: RFP から要求一覧・steering・feature 一覧を作成または再開する（Phase 1〜3）。
---

# /aidd-requirements-init

`.claude/skills/aidd-common/references/host-protocol.md` を読み、その手順で進める。
進行は `aidd-run.py workflow` の `advance / submit / respond` で行い、返却の `next_action` を人へ伝える。
計画・人間レビューの提示文（detail）は見出し・選択肢を変えずにそのまま示し、推奨・既定値を示さない。
承認・判断・理由は実際の回答者のものだけを記録する（テスト題材でも自動承認しない）。

1. `.aidd/rfp/` に実際の RFP を配置する。外部にある資料は出典パスを残してここへ入力用に複製する。
2. `--call requirements-init advance` で進める。flow は要求受入 → steering → feature 分割の各工程を
   生成 → 修正の順に通す。Phase 2 / 3 の開始時に実行計画、各工程の検査後に人間レビューで止まる。
3. 修正・差戻しは host-protocol §4。再開も同じ `--call requirements-init advance` で行う。
4. Phase 3 の承認後、`/aidd-requirements` へ進むよう人へ伝える。
