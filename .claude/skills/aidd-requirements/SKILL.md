---
name: aidd-requirements
description: 承認済み feature 一覧から feature 別 requirements と横断確認を進める（Phase 4）。
---

# /aidd-requirements

`.claude/skills/aidd-common/references/host-protocol.md` を読み、その手順で進める。
呼出し先の順の正は `.claude/skills/aidd-common/command.yaml` のこのコマンドの steps。
繰り返し（feature ごと・修正の回）はこの手順が持ち、1 回ごとに L0 を呼ぶ（L0 は繰り返しを知らない。host-protocol §1.1）。
進行は入口（host-protocol の `W`：`aidd_entry.py`。このコマンドを最初の引数にする）の `advance / submit / respond` で行い、返却の `next_action` を人へ伝える。
計画・人間レビューの提示文（detail）は見出し・選択肢を変えずにそのまま示し、推奨・既定値を示さない。
承認・判断・理由は実際の回答者のものだけを記録する（テスト題材でも自動承認しない）。

## 手順

1. `--call requirements-plan advance` で実行計画を提示し、了承（accept-plan）または対象・順序の変更（change-plan）を記録する。
2. 了承した計画の順（`.aidd/feature-list.md` の優先度順）に、feature ごとに次を行う。
   a. `--call requirements-authoring-generate --item <feature> advance` で生成し、検査・人間レビューまで進める。
   b. 人間レビューで修正が選ばれ、返却が `status: repair`（修正のアクションと item）なら、
      `--call requirements-authoring-revise --item <feature> advance` で修正の回を進める。修正の回の人間レビューでまた修正が選ばれれば、
      同じ呼出しで次の回が続く。修正要求が無ければ修正のアクションは呼ばない。
   c. 承認されたら次へ進む。
   1 件目の粒度・AC・要求ID対応の誤りを後続に繰り返さないため、feature ごとに承認してから次へ進む。
3. 全 feature の承認後、`--call requirements-cross-gate advance` で横断検査を行い人間の確認を得る。
4. 修正・差戻しは host-protocol §4。完了後 `/aidd-design` へ進むよう人へ伝える。
