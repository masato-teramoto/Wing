# main_flow ホスト手順（L3）

進捗・差戻し・承認規則は L3、検査は L4、実行の仲介は L0 が所有する。
この文書は L3 の工程選択手順である。Skill の実行は必ず L0 `call → emit → report`
に従う。L3 policy script は検査 agent を起動せず、ランナーの Python クラスも import しない。
`.claude/skills/aidd-common/engine.md` の公開 CLI と併読する。

入口は `aidd_entry.py` だけである（CommandResolver でコマンドと呼出し先を解決し、L0 の host に L3 の規則を渡して実行する）。配布環境のコマンドは
`python3 -X utf8 -B .claude/skills/aidd-common/scripts/aidd_entry.py <実行中のコマンド> ...`（例：`/aidd-requirements`。Windows は `py -3`）。
以下では `W` と略す（`W` はコマンドまでを含む）。root / state はプロジェクトに固定される。
`--call` / `--action` は実行中のコマンドの呼出し先に限る。別のコマンドの呼出し先（差戻し先など）は、
そのコマンドで呼ぶ（拒否の返却に、呼べるコマンドが示される）。

Phase 8のtask-specification-v1は資料生成用profile。task-specification-reviewのwaitは
タスク単位の確認であり、既存のfeature最終reviewとは対象が異なる。
task_review設定時はimplementation-task-review-v1で実コードの3観点を一度に検査し、
そのJSONをsubmitする。生成・タスクレビューprofileはinspection_pathへ書かず、返却contextの契約を使う。
同じsubmit/respondを使う（host は結果・回答を解釈せずに保存し、L4 の後のゲートが検査する。文脈は準備のゲートが公開する）。
タスク単位のゲートは適用の条件（when）を持たず、該当しないタスクでは自分で省く（Skill の emit は、準備のゲートが公開した理由で host が省く）。
設定の新規作成・変更時は
[検証計画の記入ルール](implementation/verification-plan.md)、生成・確認時の実回答payloadは
[単体テスト仕様書とタスク末尾確認](implementation/task-specification.md)を参照する。

## 1. 流れの単位：flow と単独アクション

`flow.yaml` は Phase 1–7 を **生成（`<base>-generate`）→ 修正（`<base>-revise`）** の順に並べる（工程の定義）。
コマンドと、たどる呼出し先の正は `command.yaml`（CommandResolver が解決する）。

### 1.1 繰り返しは入口 Skill の手順が持つ

**L0 は繰り返しを知らない。** 呼ばれた呼出し先（flow・アクション）を、`--item` の item で 1 回ぶんだけ実行する。
feature ごと・修正の回の繰り返しは入口 Skill（`aidd-*`）の手順が持ち、繰り返しの 1 回ごとに L0 を呼ぶ。
L0 はその 1 回ぶんの前後のゲート（検査・人間レビュー・承認）を実行するため、検査と承認は feature ごと・修正の回ごとに行われる。

| 繰り返し | 入口 Skill がすること |
|---|---|
| feature ごと | 了承した計画の順に、feature ごとに生成のアクションを `--item <feature>` で呼ぶ。承認されてから次の feature へ進む |
| 修正の回 | 人間レビューで修正が選ばれ、返却が `status: repair`（`repair.event` / `repair.item`）なら、その修正のアクションを呼ぶ。修正の回の人間レビューでまた修正が選ばれれば、同じ呼出しで次の回が続く |
| 修正要求が無いとき | 修正のアクションは呼ばない（その検査・人間レビュー・承認のゲートも走らない） |
| Phase 8 のタスク | L3 の `implement-next` が依存順に 1 件を選び、そのタスクの flow を呼ぶ（[実装契約](implementation/contract.md)） |

アクション Skill（生成・修正）は呼ばれた 1 件・1 回だけを扱い、L0 を呼ばない。
Skill の手順の冒頭の宣言（`役割:` / `繰り返し:`）は、Skill の役割と feature ごとかを表す（L0 は読まない。L3 の工程の規則が使う）。

| コマンド | 進める単位（`--call`。`command.yaml` の steps の順） |
|---|---|
| `/aidd-requirements-init` | 工程ごとに `requirement-intake-generate` / `steering-authoring-generate` / `feature-decomposition-generate`（修正要求があるあいだ各 `-revise`） |
| `/aidd-requirements` | `requirements-plan` → feature ごとに `requirements-authoring-generate --item <名>`（修正要求があるあいだ `-revise`）→ `requirements-cross-gate` |
| `/aidd-design` | `design-plan` → feature ごとに `design-authoring-generate --item <名>`（同上）→ `design-cross-gate` → `docs-integration-generate`（同上） |
| `/aidd-tasks` | `tasks-plan` → feature ごとに `tasks-authoring-generate --item <名>` → `tasks-gate-run`（修正は `tasks-authoring-revise --item <名>`） |
| `/aidd-implement` | `implement`（生成・修正）をタスクの固定 task_item ごとに実行 → `implement-review --item <feature>`。実際のcallはL3がflow.yamlから解決する。詳細は [実装契約](implementation/contract.md) |

feature の順序は `advance` の結果（計画の `対象 feature と順序`）に従う。完了した単位を
もう一度 `advance` しても、L0 が済んだ unit を飛ばして `done` を返す（再開は同じ入口で行う）。

```text
W --call <flow|action> [--item <feature>] advance
W --action <返された event（アクション名）> [--item <返された item>] --payload <保存したJSON> submit
W --action <返された event（アクション名）> [--item <返された item>] --payload <保存したJSON> --actor <実回答者> respond
```

返却の `result.status` と `allowed_actions`、`next_action`（次に人がすべきことの 1 行）に従う。
`next_action` は人へそのまま伝える（alpha2 の Step 6）。

| result.status | ホストの処理 |
|---|---|
| emit、通常 Skill | 指定 SKILL.md を Read し、context の authoring_inputs・対象（`targets`）・`unreviewed_inputs`・回答・修正依頼（repair）を渡して実行し、結果を submit |
| emit、isAgent: true | check-runner を別コンテキストで起動し、target/calls、検査対象（`review_targets`）・上流（`upstream`）・`unreviewed_inputs`、snapshot_path / findings_path / inspection_path を渡す。完了を待って submit |
| wait、計画 | detail の計画を**そのまま**人へ提示し、了承（accept-plan）か変更指示（change-plan）を待つ |
| wait、review | detail の提示文を**そのまま**人へ提示し、判断・解消確認・承認を待つ（§3） |
| waiting | 生成途中の質問・差戻し候補を提示し、回答（answer）または差戻し（repair）を待つ |
| blocked | 差戻しが未解消。`blockers` の target_action / target_item の flow を先に進める（§4） |
| done | 次の単位へ進む |
| fail | 理由を人へ示して停止する。機械ゲートへ外部から成功を記録しない |

workflow CLI 自体の終了コードは成功0／失敗1。`fail` でも `operation_applied: true` なら受領は保存済み。

### 進捗の提示

進捗を人に提示する直前に `W --action <event> progress` を実行し、返された一覧を示す。
保存済みの `phase-progress.json` をそのまま最新値として提示しない。

## 2. emit の実行と結果受領

submit 用 JSON は次の形。dispatch オブジェクトを返却値から丸ごとコピーする。

```json
{
  "operation_id": "一度だけ発行し保存するUUID",
  "dispatch": {"返されたdispatchの全フィールド": "値を保持"},
  "result": {"status": "completed", "targets": [], "questions": [],
    "open_placeholders": 0, "changed_findings": [], "return_candidates": [], "summary": "実際の結果"}
}
```

- 生成 Skill の result は実際の返却 JSON 全体。targets を空のまま使わない。
- 修正 Skill は context の `repair` を見る。`null` なら何も編集せず
  `{"status":"completed","targets":[],"questions":[],"open_placeholders":0,"changed_findings":[],"return_candidates":[],"summary":"修正対象 0 件"}` を返す。
- 検査 agent の result は `{"status":"completed"}` または `{"status":"failed"}`。検査役は 1 実行ブロックを
  `inspection_path` に書くだけで、ゲート記録・成果物は編集しない（追記と review 遷移は L3 の scope-check が 1 回だけ行う）。
  中断後にもう一度検査を実行しても記録は二重にならない。
- 生成途中の質問は `waiting` で返す。実回答は `{"answers":["実回答"]}` を `--actor <人> answer` に渡してから advance する。
  差戻し候補（return_candidates）の対応は §4。RFP の不備（owner: rfp）は RFP の改訂でしか解消しない。

Phase 8のコードprofileは例外で、scope/run/layers/findings_count/aspects/gate_record_pathを含む
完全な結果が必要。詳細は [実装契約](implementation/contract.md)。通常タスクのitemはexecution_idである。
completed は今回の検査処理と記録が完了したことを意味する。形式不備があっても意味検査は止めない
（不備のある節だけを外す）。旧版の検査役が①だけで止めた回も含み、必要な全検査の実施・指摘0件・承認を意味しない。

## 3. 計画と人間レビュー

**選択肢で聞く**：人に聞く停止（計画・作成中の質問・指摘への判断・修正に回すか・承認）の返却には `choices` がある。
人が文字を入力しなくて済むように、提示文（detail）をそのまま示したあと、`choices.questions` を Claude Code の
選択式の質問（AskUserQuestion）で出す。

- 1 回に 4 問まで出す（多ければ順に分けて出す）。各問の `header`・`question`、選択肢の `label`・`description` をそのまま使い、
  ホストが選択肢や推奨を足したり、並べ替えたりしない。選択式の質問は「その他」で自由に入力できる。
- 選ばれた選択肢の `answer` を、`choices.kind` ごとに次のように使う。「その他」の入力は、下の回答の書き方に直して足す（後に書いたものが優先）。

  | kind | 使い方 |
  |---|---|
  | decisions | 全問の `answer` を ` / ` でつなぎ、`decisions` の `answer` にする（例 `1:推奨 / 束1:C[後で決める] 後の工程で決める`）。`reevaluate` が選ばれたら、先に `reevaluate` を respond し（下記）、ほかの答えは再評価の回のレビューで聞き直す |
  | repair | `repair:all-fixes` → `repair` を `{"findings":"all-fixes"}` で respond。`repair:manual` → 修正の指示を人に聞く。横断・tasks 全体・実装の検査では出ない（修正先を人が選ぶため、`repair` を event・targets 付きで respond する） |
  | resolve | 修正の回と再検査を終えたが自動では解消されなかった指摘。`resolve:<scope> <run> <number>` → `resolve` を `{"scope","run","number"}` で respond。`repair:manual` → 修正の指示を人に聞き、もう一度 `repair` |
  | none | 人に聞く選択肢が無い（判断は揃ったが、検査の完了待ちなど承認できない）。選択式の質問は出さず、detail をそのまま示して返却の指示に従う |
  | approve | `approve` → 承認（横断は確認）を respond。`hold` → 何を変えるかを人に聞く |
  | plan | `accept-plan` → 了承。`accept-plan-with-note` → 「その他」の条件を note にして了承。`change-plan` → 「その他」の指示で change-plan |
  | answers | 各問で選ばれた `answer`（または「その他」の文）を、質問の順に `answer` の answers に入れる |

- 回答者（actor）は実際に答えた人。名前がまだ分からなければ、最初の質問と一緒に聞き、以後は同じ名前を使う。
- 選択式の質問が使えない環境（`claude -p` などの非対話の実行）では、同じ選択肢を番号付きの文で示し、文字の回答を受ける。

**計画**：detail を提示し、人の回答に応じて次のどちらかを respond する。

- 了承：`{"operation_id":..., "action":"accept-plan", "dispatch":<wait の dispatch>, "data":{"note":"今回は上位2件だけ等、進め方の指示があれば"}}`
- 対象・順序の変更（Phase 4 / 5 / 7）：`{"action":"change-plan", "dispatch":..., "data":{"instruction":"実際の変更指示"}}`。
  Phase 3 への差戻しとして feature 一覧を修正・再検査・再承認し、その後に計画を出し直す。
- 「開始してよいですか」だけを問わない。計画を示さずに可否を尋ねない。

**人間レビュー**：detail は ③ の提示文で、見る観点 → 見なくてよいもの（L4 検査済み・内部ファイル・自動で処理した指摘）→
前回の検査からの変更 → 判断が必要な指摘（重大 → 要判断の束 → 持ち越し）→ 答え方 の順に出る。見出し・選択肢の記号・並びを
変えずにそのまま提示する。AI の推奨は提示文が示すものだけを示し、ホストが推奨や既定値を足さない。Skill 名・agent 名を出さない。
回答は人の言葉のまま転記する（要約・言い換えをしない）。人が `詳細 <番号>` と書いたら、`review` の該当行の
`description`（根拠）・`suggestion`（修正案）・`recommendation`（推奨）を示す。

回答の種類（いずれも直前の返却の `review_context` を `expected` にコピーし、回答ごとに新しい operation_id を付ける）:

| action | data | 用途 |
|---|---|---|
| decisions | `{"answer":"1:推奨 / 束1:C[後で決める+] 理由 / 3〜5:A / 7:D 理由"}` または `{"answer":"全件:A"}` | 指摘ごとの判断（A 修正 / B 差戻し / C 対応せず進める / D 未対応 / 推奨＝AI の推奨を採用）。C と D は理由必須。C の却下区分は `C[指摘の誤り\|対象外\|後で決める\|解釈で対応]`、対象外・後で決めるに `+` で今後も同じ扱い。`束N` は提示文の束、`N〜M` は範囲。後に書いたものが優先。前回までの指摘は `2-1:C 理由` のように「回数-番号」で指す。複数スコープの一括確認では先頭に `feature:x` を付ける |
| decision | `{"scope","run","number","decision","reason"[,"category","learn","adopted"]}` | 1 件ずつの判断（decisions と同じ意味。category＝却下区分、learn＝今後も同じ扱い、adopted＝推奨の 採用／不採用） |
| repair | `{"event","item","targets","findings":[{phase,scope,run,number,instruction}]}` または `{"findings":"all-fixes"}` | 判断 A/B の実行（§4）。`all-fixes` は、この工程・項目の修正（A）の指摘と system が「修正」とした軽微をまとめて修正に回す。instruction を省くと、推奨を採用した修正・軽微は修正案、差戻しは判断の理由が指示になる。修正の依頼は、修正の回の検査を封印した時点で「実行済み」（`executed_run`）になる。実行済みの依頼には追記せず、次の `repair` は新しい依頼になる（実行済みの指示を次の修正の回に渡さない。再評価の回の後の修正も同じ）。修正の回で実行済みの指摘は `all-fixes` に入らず、解消の確認（選択肢 `resolve`）で聞く。同じ operation_id の再送は、予約の後に中断した場合も、保存済みの依頼で続きから処理する。指示が決まらない指摘があると拒否され、その指摘が返る。ホストはその指摘ごとに選択式の質問（「AI の修正案で直す：<修正案>」／「指示を自分で書く」＝「その他」）で聞き、`findings` に instruction を付けて respond し直す |
| reevaluate | `{}` | 切り替え前の版で出た未判断の指摘（旧形式）を再評価に回す。人の判断として「未対応（再評価に回した）」を記録し、本文を変えない修正の回を予約する。返却は `status: repair`（`repair.event` が修正のアクション）。修正の回の検査で、検査役が旧形式の指摘を新しい決まりで見直し、人は残った指摘だけを判断する。修正の依頼が残っている間はできない |
| resolve | `{"scope","run","number"}` | 再検査で同じ指摘が出なくなったものは system が解消を記録する。それで閉じない指摘（節が変わっていない・差戻しの戻し先が未承認など）だけを人が確認する |
| approve | `{}` | 判断が揃い、修正・差戻しが残っていないときの承認（横断は確認）。actor は承認者本人 |

- 4 値に収まらない回答（部分対応など）は、どの値に当たるかを人に確認してから転記する。
- 判断が揃う前、修正・差戻しが残っている間は承認を問わない（承認は拒否される）。
- 指摘 0 件でも停止し、承認の可否だけを問う。「指摘が無いので承認します」と書かない。
- `未対応` は残件として同じスコープの以後のレビューに持ち越され、承認時の残件はゲート記録に残る。
- actor は実回答者。架空の回答・承認・理由を作成しない。テスト題材でも自動承認しない。

decision/resolve の応答には更新済み review_context がある。次の回答はそれを使う。
approve の応答は report と次の L0 call の結果。改めて report を手動実行しない。
allowed_actions は現在の候補であり、実行時にも個別の対象・指摘・再検査条件を検証する。
repair が必要なら §4 に進み、承認で代用しない。修正対象は人間が選ぶ。

必要な検査層は status-protocol.md §6 に従う。未実施があれば approve は候補に出ず、
直接実行しても停止する。指摘の受容や理由の記入で未実施検査を免除しない。
形式不備で①のみの場合、実際の人間回答に基づき当該指摘を修正対象として §4 へ進め、
再検査で①②を実施する。受容済みの判断をホストが無断で修正へ変更しない。
指摘0件なのに層が不足する場合は検査処理・記録を診断して再検査し、架空の指摘や実行層を追加しない。
actor は実回答者。架空の回答・承認・理由を作成しない。

### 途中停止・再送

操作前に operation_id を一度発行し、完全な JSON payload を `.aidd/.engine/` のファイルへ保存する
（`.aidd/.engine/` は git で共有してよい。レビュー待ちの続きは別の場所でも実行できる）。
応答が不明な場合は**同じ ID・payload・actor**で再実行する。ID を変えたり expected を取り直して再送しない。
同じ ID の内容変更は拒否される。

タスク末尾の生成・レビュー結果や回答が後続gateで不正として拒否された場合は、消費済みdispatchへ訂正を再送しない。
拒否理由を確認し、既存の`implement-retry`で新しいdispatchを取得して訂正する。旧提出・回答とTDD/VERIFY証跡は保持する。
保存途中の中断は`advance`で同じgateを再開する。同じ操作IDの再送が返す保存済みfailと、現在のgateの再開結果を区別する。

## 4. 修正・差戻し

判断 A（修正）/ B（差戻し）を記録したら、人が決めた修正指示と対象で `repair` を respond する。

- **同じ工程の修正**（A）：`event` は当該工程の `<base>-generate`、`item` は当該 feature。生成レビューでの
  repair は、そのレビューへの回答として記録され、返却は `status: repair`（`repair.event` が修正のアクション）。
  入口 Skill は `W --call <repair.event> [--item <repair.item>] advance` で修正の回を進める（修正 Skill → 再検査 → 再レビュー）。
  修正の回のレビューでまた repair を選ぶと、同じ修正のアクションが次の回として続けて実行される。
  再検査で出なくなった旧指摘は system が解消を記録する。新しい指摘に判断してから承認する。何度でも繰り返せる（§1.1）。
  横断・tasks 全体の指摘は `all-fixes` の対象にならない。修正する feature を `event` / `item` に指定して 1 件ずつ選ぶ。
- **上流への差戻し**（B）：`event` / `item` は戻し先（所有工程）の `<base>-generate` と feature。
  戻し先の成果物と、指摘を出した成果物が開き直される（Phase 7 からの design 差戻しでは docs も対象）。
  修正後に入力内容が変わった場合は、その入力を実際に使う下流成果物も再検査へ戻す。
  上流の再承認だけで下流の完了証跡を書き換えない。関係しない承認済み成果物はそのまま。
  返却は `blocked` / `rollback`。戻し先の flow を進めて修正・再検査・承認すると、その承認で差戻しは
  「上流の再承認済み」になる（alpha2 と同じく、上流の再承認で差戻しが解ける）。続けて元の flow を進めると
  指摘元の成果物が見直され、再検査で出なくなった旧指摘は system が解消を記録する（自動で閉じない指摘だけ人が `resolve`）。承認した時点で差戻しは解消済みになる。
  blocker の履歴は削除しない。自動で解けなかった場合だけ、同じ blocker ID を
  `upstream-approved` / `resolve-rollback` に渡して記録する（`--payload '{"blocker":"ID"}' --actor <人>`）。
- **横断検査・tasks 全体確認での修正**：`event` / `item` に対象 feature の `<base>-generate` を指定する。
  その feature の flow を進めて修正・再検査・承認した後、横断検査（または `tasks-gate-run`）を再実行する。
- **作成中に判明した差戻し**（waiting の return_candidates）：人が差戻しを選んだら、戻し先の event / item で
  `W --action <戻し先の generate> [--item <feature>] --payload <JSON> --actor <人> repair` を実行する。
  payload は `{"origin":"authoring-candidate","candidate":{"event":"<作成中の event>","item":"<feature>","index":0},"targets":[...],"instruction":"実際の指示"}`。
  戻し先を修正・承認すると、作成中の工程が続きから再開する（Phase 7 から design へ戻した場合は docs も見直す）。
- **新しい上流要求**（下流の壁打ちで判明）：要求一覧は Phase 1 だけが更新する。Phase 1 への差戻しとして扱う。
- **承認済み成果物をもう一度確認したい**：`W --action <generate> [--item] --payload '{"instruction":"実際の指示"}' --actor <人> reopen`。
- フロー外で承認済み成果物や RFP を変えた場合は、次の advance がそれを検知し、その成果物（RFP なら要求一覧）だけを
  修正アクションで見直す手順に戻す。承認を手で付け直さない。

同一 state へのホスト処理は直列にする。検査 agent に本文や進捗を修正させない。
