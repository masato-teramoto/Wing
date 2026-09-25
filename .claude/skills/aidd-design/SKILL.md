---
name: aidd-design
description: feature 別 design、横断確認、docs 統合までを進める（Phase 5〜6）。
---

# /aidd-design

`.claude/skills/aidd-common/references/host-protocol.md` を読み、その手順で進める。
進行は `aidd-run.py workflow` の `advance / submit / respond` で行い、返却の `next_action` を人へ伝える。
計画・人間レビューの提示文（detail）は見出し・選択肢を変えずにそのまま示し、推奨・既定値を示さない。
承認・判断・理由は実際の回答者のものだけを記録する（テスト題材でも自動承認しない）。

1. `--call design-plan advance` で実行計画を提示し、了承または変更指示を記録する。
2. 計画の依存順に feature ごとに `--call design --item <名> advance` を進め、個別検査・人間承認まで完走させる。
   依存先 design の公開契約を入力にする。feature ごとの要件トレーサビリティ自己診断を人へ報告する。
3. `--call design-cross-gate advance` で横断検査（契約整合）を行い人間の確認を得る。
4. `--call docs advance` で docs 3 文書の計画提示・生成・検査・人間承認を行う。docs は設計の抽出物。
   design 間の競合が見つかれば design の所有工程へ差し戻す（host-protocol §4）。
5. 完了後 `/aidd-tasks` へ進むよう人へ伝える。
