---
name: aidd-design
description: feature 別 design、横断確認、docs 統合までを進める（Phase 5〜6）。
---

# /aidd-design

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

## Feature 方式（`workflow.mode` が `feature`）

手順 1〜3 の全件ループは使わず、選択中の feature（S）だけを進める。`--item` は付けない。入口（`aidd_entry.py`）が選択中の S を補う（計画停止点・作成・修正は S。横断確認・全体確認は、その工程の成果物が全 feature で承認済みのときだけ item 無しの全件、それ以外は S。差し戻した S の再承認も S）。
明示した item が選択中の S と違えば L3 が拒否する。S が未選択なら入口が止めて select-scope を求める。
承認後も、依存する側の feature には自動で進まない。次の feature は人が選ぶ（select-scope）。

1. 対象を変えるときは `select-scope`（payload `{"feature": "<名前>"}`）を呼ぶ。依存先の design が未承認の feature は選べない（理由が返る）。
2. `--call design-plan advance` で S の計画停止点（前提は S と依存先）を提示し、了承を記録する。
3. `--call design-authoring-generate advance` で S の design を作り、承認まで進める（修正の回は `--call design-authoring-revise advance`）。
4. S が Platform で、利用側の design が承認済みなら、`--call design-cross-gate advance` で S の横断確認（契約整合、利用側と比較）を行う。
   利用側がまだ無ければ呼ばない。User なら呼ばない。
5. docs を S の design に合わせて累積する。docs が未作成なら `--call docs-integration-generate advance`（docs の計画停止が 1 回出る）、
   作成済みなら `--call docs-integration-revise advance`（L3 が収録の修正要求を起こす）。検査・人間承認まで進める。
6. 全 feature の design が承認されたら、`--call design-cross-gate advance` で全件の横断確認を行い、docs の最終改訂と承認を通す。
7. 続けて S の tasks を作るなら `/aidd-tasks`、別の feature を進めるなら `select-scope` から。
