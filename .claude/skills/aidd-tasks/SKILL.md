---
name: aidd-tasks
description: feature 別 tasks を検査し、最後に全体確認と人間承認を行う（Phase 7）。
---

# /aidd-tasks

`.claude/skills/aidd-common/references/host-protocol.md` を読み、その手順で進める。
進行は `aidd-run.py workflow` の `advance / submit / respond` で行い、返却の `next_action` を人へ伝える。
計画・人間レビューの提示文（detail）は見出し・選択肢を変えずにそのまま示し、推奨・既定値を示さない。
承認・判断・理由は実際の回答者のものだけを記録する（テスト題材でも自動承認しない）。

1. `--call tasks-plan advance` で実行計画を提示し、了承または変更指示を記録する（docs 3 文書の承認は開始の前提。生成の入力にはしない）。
2. 計画の順に feature ごとに `--call tasks --item <名> advance` を進める。個別検査までで、ここでは承認を求めない。
3. 全件の個別検査後、`--call tasks-gate-run advance` で全体の依存・トレースを確認し、feature 別の指摘と全体指摘を
   まとめて提示して、最後に全件の人間承認を得る。
   準備タスクにツール導入がある場合は、その本文の導入対象・版の条件・導入先・変更範囲・ネットワーク取得も
   承認対象として案内する。既存の提示形式と選択肢を保ち、導入だけの別承認を追加しない。
   最初の実行計画の了承を、完成したタスク一覧や導入範囲の承認として扱わない。
4. 修正は人が対象を指定して repair する（host-protocol §4）。修正後は全体確認と承認をやり直す。
