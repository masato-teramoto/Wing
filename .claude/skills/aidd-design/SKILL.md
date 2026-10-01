---
name: aidd-design
description: feature 別 design、横断確認、docs 統合までを進める（Phase 5〜6）。
---

# /aidd-design

`.claude/skills/aidd-common/references/host-protocol.md` を読み、その手順で進める。
呼出し先の順の正は `.claude/skills/aidd-common/command.yaml` のこのコマンドの steps。
繰り返し（feature ごと・修正の回）はこの手順が持ち、1 回ごとに L0 を呼ぶ（L0 は繰り返しを知らない。host-protocol §1.1）。
進行は入口（host-protocol の `W`：`aidd_entry.py`。このコマンドを最初の引数にする）の `advance / submit / respond` で行い、返却の `next_action` を人へ伝える。
計画・人間レビューの提示文（detail）は見出し・選択肢を変えずにそのまま示し、推奨・既定値を示さない。
承認・判断・理由は実際の回答者のものだけを記録する（テスト題材でも自動承認しない）。

## 手順

1. `--call design-plan advance` で実行計画を提示し、了承または変更指示を記録する。
2. 了承した計画の順（依存順）に、feature ごとに次を行う。依存先 design の公開契約を入力にする。
   a. `--call design-authoring-generate --item <feature> advance` で生成し、検査・人間レビューまで進める。
   b. 人間レビューで修正が選ばれ、返却が `status: repair`（修正のアクションと item）なら、
      `--call design-authoring-revise --item <feature> advance` で修正の回を進める。修正の回の人間レビューでまた修正が選ばれれば、
      同じ呼出しで次の回が続く。修正要求が無ければ修正のアクションは呼ばない。
   c. 承認されたら次へ進む。
   feature ごとの要件トレーサビリティ自己診断を人へ報告する。
3. `--call design-cross-gate advance` で横断検査（契約整合）を行い人間の確認を得る。
4. docs 3 文書（`docs-integration`）を同じ形で進める（計画提示・生成・検査・人間承認。修正要求があれば修正の回）。
   a. `--call docs-integration-generate advance` で生成し、検査・人間レビューまで進める。
   b. 人間レビューで修正が選ばれ、返却が `status: repair`（修正のアクションと item）なら、
      `--call docs-integration-revise advance` で修正の回を進める。修正の回の人間レビューでまた修正が選ばれれば、
      同じ呼出しで次の回が続く。修正要求が無ければ修正のアクションは呼ばない。
   c. 承認されたら次へ進む。
   docs は設計の抽出物。design 間の競合が見つかれば design の所有工程へ差し戻す（host-protocol §4）。
5. 完了後 `/aidd-tasks` へ進むよう人へ伝える。
