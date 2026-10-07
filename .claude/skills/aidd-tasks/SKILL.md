---
name: aidd-tasks
description: feature 別 tasks を検査し、最後に全体確認と人間承認を行う（Phase 7）。
---

# /aidd-tasks

`.claude/skills/aidd-common/references/host-protocol.md` を読み、その手順で進める。
呼出し先の順の正は `.claude/skills/aidd-common/command.yaml` のこのコマンドの steps。
繰り返し（feature ごと・修正の回）はこの手順が持ち、1 回ごとに L0 を呼ぶ（L0 は繰り返しを知らない。host-protocol §1.1）。
進行は入口（host-protocol の `W`：`aidd_entry.py`。このコマンドを最初の引数にする）の `advance / submit / respond` で行い、返却の `next_action` を人へ伝える。
計画・人間レビューの提示文（detail）は見出し・選択肢を変えずにそのまま示す。推奨は提示文にあるものだけを示し、ホストが推奨・既定値を作らない。
人が `詳細 <番号>` と書いたら、返却の `review`（指摘の一覧）からその指摘の指摘内容・修正案・推奨を示す。
返却に `choices` があれば、提示文を示したあと、その選択肢を Claude Code の選択式の質問（AskUserQuestion）で出し、人に選んでもらう（`references/host-protocol.md` §3「選択肢で聞く」）。人に回答の文を入力させない。選択式の質問が使えない非対話の実行では、選択肢を番号付きの文で示す。
人間レビューの回答は `1:A`、`2:C[後で決める+] 理由`、`3〜8:C 理由`、`束1:C 理由`、`1:推奨`、`全件:A` の形のまま `decisions` の `answer` に渡す（後に書いたものが優先）。
修正（A）と AI が直す軽微は `repair` に `findings: "all-fixes"` を渡してまとめて修正に回す（横断・全体の検査の指摘は `all-fixes` に入らない。指摘を選び、直す feature の生成アクションと item を宛先にする）。修正指示は、A に添えた回答・採用した修正案・差戻しの理由から L3 が埋めるので、人に書かせない。埋まらない指摘があると `all-fixes` はその指摘を返して拒否するので、その指摘だけを選択式（「AI の修正案で直す」／「その他」で指示を書く）で聞き、instruction を付けて repair し直す。
承認・判断・理由は実際の回答者のものだけを記録する（テスト題材でも自動承認しない）。

## 手順

1. `--call tasks-plan advance` で実行計画を提示し、了承または変更指示を記録する（docs 3 文書の承認は開始の前提。生成の入力にはしない）。
2. 了承した計画の順に、feature ごとに `--call tasks-authoring-generate --item <feature> advance` を進める。
   個別検査までで、ここでは承認を求めない。
3. 全件の個別検査後、`--call tasks-gate-run advance` で全体の依存・トレースを確認し、feature 別の指摘と全体指摘を
   まとめて提示して、最後に全件の人間承認を得る。
   準備タスクにツール導入がある場合は、その本文の導入対象・版の条件・導入先・変更範囲・ネットワーク取得も
   承認対象として案内する。既存の提示形式と選択肢を保ち、導入だけの別承認を追加しない。
   最初の実行計画の了承を、完成したタスク一覧や導入範囲の承認として扱わない。
4. 修正は人が対象を指定して repair する（host-protocol §4）。返却の `repair`（修正のアクションと item）で
   `--call tasks-authoring-revise --item <feature> advance` を呼び、修正後は全体確認と承認をやり直す。
