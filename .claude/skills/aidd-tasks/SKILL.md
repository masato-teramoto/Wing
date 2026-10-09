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
   計画に smoke wrapper の owner の候補が出たら、人に選ばせて accept-plan の data に `owner`（「候補なし」なら `owner_reason` も）を入れる。
   owner の tasks には、全体結合確認の 1 経路を実行する wrapper を作る「結合確認タスク」を入れる（`references/implementation/integration.md`）。
2. 了承した計画の順に、feature ごとに `--call tasks-authoring-generate --item <feature> advance` を進める。
   個別検査までで、ここでは承認を求めない。
3. 全件の個別検査後、`--call tasks-gate-run advance` で全体の依存・トレースを確認し、feature 別の指摘と全体指摘を
   まとめて提示して、最後に全件の人間承認を得る。
   準備タスクにツール導入がある場合は、その本文の導入対象・版の条件・導入先・変更範囲・ネットワーク取得も
   承認対象として案内する。既存の提示形式と選択肢を保ち、導入だけの別承認を追加しない。
   最初の実行計画の了承を、完成したタスク一覧や導入範囲の承認として扱わない。
4. 修正は人が対象を指定して repair する（host-protocol §4）。返却の `repair`（修正のアクションと item）で
   `--call tasks-authoring-revise --item <feature> advance` を呼ぶ。修正Skillのemitを受けたら、下記の履歴収集を行ってからSkillへ渡す。修正後は全体確認と承認をやり直す。

## Feature 方式（`workflow.mode` が `feature`）

手順 1〜3 の全件ループは使わず、選択中の feature（S）だけを進める。`--item` は付けない。入口（`aidd_entry.py`）が選択中の S を補う（計画停止点・作成・修正は S。横断確認・全体確認は、その工程の成果物が全 feature で承認済みのときだけ item 無しの全件、それ以外は S。差し戻した S の再承認も S）。
明示した item が選択中の S と違えば L3 が拒否する。S が未選択なら入口が止めて select-scope を求める。
承認後も、依存する側の feature には自動で進まない。次の feature は人が選ぶ（select-scope）。

1. 対象を変えるときは `select-scope`（payload `{"feature": "<名前>"}`）を呼ぶ。
2. `--call tasks-plan advance` で S の計画停止点を提示し、了承を記録する。smoke wrapper の owner の候補が出たら（S が候補のとき）、
   上の手順 1 と同じく owner を選ばせる。
3. `--call tasks-authoring-generate advance` で S の tasks を作り、個別検査まで進める（修正の回は返却の `repair` のとおり）。
4. `--call tasks-gate-run advance` で S と依存先（Platform なら承認済みの利用側も）の tasks の依存・トレースを確認し、S の tasks を承認する。
5. 全 feature の tasks が承認されたら、`--call tasks-gate-run advance` で全件の確認と承認を行う（入口は item を補わない）。
6. 続けて S の実装に入るなら `/aidd-implement <S>`、別の feature を進めるなら `select-scope` から。

## 修正Skillへ渡す着手履歴

修正対象がある`tasks-authoring-revise`のemitでは、入口のホストが毎回（別セッションでの再開・質問回答後も）案件rootから次を読み取る。
CLIのcontextに履歴が自動で含まれるとは扱わない。repairが空・targetsが0件なら収集せず、既存の無編集終了へ進む。

1. contextのitem・targets・repairを確認し、対象tasksのチェック状態・実装メモと、修正指示・保存済みの質問回答を読む。
2. `.aidd/implementation/features/<feature>/state.json`のcompleted・history・active_request・plan_ref・invalidated、
   `plans/<feature>/*.json`の元計画・操作履歴（`*-history.json`を含む）、`requests/*.json`と`runs/*/execution.json`の同featureの記録を読む。
   ここでのplans / requests / runsはすべて`.aidd/implementation/`の下。active.jsonの不在だけで未着手と判断しない。再開・差戻しで退役した計画も残る。
3. 該当するexecutionの同じディレクトリにあるRED・GREEN・VERIFYのreceipt（`red.json` / `green.json` / `verify.json`）と、
   判断に必要な参照ログを確認する。feature・plan_ref・task_id・execution_idの対応を保ち、過去の完了と現在の計画での有効性を区別する。
   完了表から外れた実行や未完了の実行も着手履歴であり、古い計画の同番号を現在のタスクへ付け替えない。
4. 元のdispatchとcontextは変更せず、追加の読み取り専用資料`task_history`として、確認時点・対象feature・計画別のタスク状態・
   execution_idと証跡の要点・根拠ファイルのパス・欠落/読取不能/矛盾・人の実回答を修正Skillへ一緒に渡す。
   修正Skillが根拠を再確認できるよう参照先を示す。submitは元のdispatchと共通契約の結果を使い、task_historyを状態ストアへ書き戻さない。
5. 記録がないこと、チェックが空であることだけでは未着手を証明しない。確認できた情報は渡し、不明な対象だけ質問・調査が必要と示す。
   未着手という人の実回答は出典とともに渡せるが、既存証跡と矛盾する場合は確認する。保存済み証跡で分かる着手状況を改めて人に質問しない。

これらは変更影響を判断する資料であり、生成要件・承認の代わりには使わない。入口も修正Skillも履歴・証跡・状態を直接編集しない。
着手済みタスクの再編や証跡移行が必要な場合は影響を提示し、既存の差戻し・再承認・rebase手順で扱える範囲を確認する。
