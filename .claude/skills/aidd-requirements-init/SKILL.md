---
name: aidd-requirements-init
description: RFP から要求一覧・steering・feature 一覧を作成または再開する（Phase 1〜3）。
---

# /aidd-requirements-init

`.claude/skills/aidd-common/references/host-protocol.md` を読み、その手順で進める。
呼出し先の順の正は `.claude/skills/aidd-common/command.yaml` のこのコマンドの steps。
繰り返し（feature ごと・修正の回）はこの手順が持ち、1 回ごとに L0 を呼ぶ（L0 は繰り返しを知らない。host-protocol §1.1）。
進行は入口（host-protocol の `W`：`aidd_entry.py`。このコマンドを最初の引数にする）の `advance / submit / respond` で行い、返却の `next_action` を人へ伝える。
計画・人間レビューの提示文（detail）は見出し・選択肢を変えずにそのまま示す。推奨は提示文にあるものだけを示し、ホストが推奨・既定値を作らない。
人が `詳細 <番号>` と書いたら、返却の `review`（指摘の一覧）からその指摘の指摘内容・修正案・推奨を示す。
返却に `choices` があれば、提示文を示したあと、その選択肢を Claude Code の選択式の質問（AskUserQuestion）で出し、人に選んでもらう（`references/host-protocol.md` §3「選択肢で聞く」）。人に回答の文を入力させない。選択式の質問が使えない非対話の実行では、選択肢を番号付きの文で示す。
人間レビューの回答は `1:A`、`2:C[後で決める+] 理由`、`3〜8:C 理由`、`束1:C 理由`、`1:推奨`、`全件:A` の形のまま `decisions` の `answer` に渡す（後に書いたものが優先）。
修正（A）と AI が直す軽微は `repair` に `findings: "all-fixes"` を渡してまとめて修正に回す。修正指示は、A に添えた回答・採用した修正案・差戻しの理由から L3 が埋めるので、人に書かせない。埋まらない指摘があると `all-fixes` はその指摘を返して拒否するので、その指摘だけを選択式（「AI の修正案で直す」／「その他」で指示を書く）で聞き、instruction を付けて repair し直す。
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
