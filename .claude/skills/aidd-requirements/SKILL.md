---
name: aidd-requirements
description: 承認済み feature 一覧から feature 別 requirements と横断確認を進める（Phase 4）。
---

# /aidd-requirements

`.claude/skills/aidd-common/references/host-protocol.md` を読み、その手順で進める。
進行は `aidd-run.py workflow` の `advance / submit / respond` で行い、返却の `next_action` を人へ伝える。
計画・人間レビューの提示文（detail）は見出し・選択肢を変えずにそのまま示し、推奨・既定値を示さない。
承認・判断・理由は実際の回答者のものだけを記録する（テスト題材でも自動承認しない）。

1. `--call requirements-plan advance` で実行計画を提示し、了承（accept-plan）または対象・順序の変更（change-plan）を記録する。
2. 計画の順に feature ごとに `--call requirements --item <名> advance` を進め、個別検査・人間承認まで完走させる。
   1 件目の粒度・AC・要求ID対応の誤りを後続に繰り返さないため、feature ごとに承認してから次へ進む。
3. 全 feature の承認後、`--call requirements-cross-gate advance` で横断検査を行い人間の確認を得る。
4. 修正・差戻しは host-protocol §4。完了後 `/aidd-design` へ進むよう人へ伝える。
