---
name: aidd-requirements-init
description: RFP から要求一覧・steering・feature 一覧を作成または再開する（Phase 1〜3）。
---

# /aidd-requirements-init

`.claude/skills/aidd-common/references/host-protocol.md` を読み、その手順で進める。
呼出し先の順の正は `.claude/skills/aidd-common/command.yaml` のこのコマンドの steps。
繰り返し（feature ごと・修正の回）はこの手順が持ち、1 回ごとに L0 を呼ぶ（L0 は繰り返しを知らない。host-protocol §1.1）。
進行は入口（host-protocol の `W`：`aidd_entry.py`。このコマンドを最初の引数にする）の `advance / submit / respond` で行い、返却の `next_action` を人へ伝える。
計画・人間レビューの提示文（detail）は見出し・選択肢を変えずにそのまま示し、推奨・既定値を示さない。
承認・判断・理由は実際の回答者のものだけを記録する（テスト題材でも自動承認しない）。

## 手順

1. `.aidd/rfp/` に実際の RFP を配置する。外部にある資料は出典パスを残してここへ入力用に複製する。
2. 要求受入（`requirement-intake`）→ steering（`steering-authoring`）→ feature 分割（`feature-decomposition`）の順に、
   工程ごとに次を行う。Phase 2 / 3 は生成の開始時に実行計画で止まる。
   a. `--call <工程>-generate advance` で生成し、検査・人間レビューまで進める。
   b. 人間レビューで修正が選ばれ、返却が `status: repair`（修正のアクションと item）なら、
      `--call <工程>-revise advance` で修正の回を進める。修正の回の人間レビューでまた修正が選ばれれば、
      同じ呼出しで次の回が続く。修正要求が無ければ修正のアクションは呼ばない。
   c. 承認されたら次へ進む。
3. 修正・差戻しは host-protocol §4。再開も同じ呼出しで行う（済んだ呼出しは L0 が飛ばす）。
4. Phase 3 の承認後、`/aidd-requirements` へ進むよう人へ伝える。
