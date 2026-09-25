# main_flow ホスト手順（L3）

進捗・差戻し・承認規則は L3、検査は L4、実行の仲介は L0 が所有する。
この文書は L3 の工程選択手順である。Skill の実行は必ず L0 `call → emit → report`
に従う。L3 policy script は検査 agent を起動せず、ランナーの Python クラスも import しない。
`.claude/skills/aidd-common/engine.md` の公開 CLI と併読する。

配布環境のコマンドは `python3 -X utf8 -B aidd-run.py workflow ...`（Windows は `py -3`）。
以下では `W` と略す。root / state はプロジェクトに固定される。

## 1. 流れの単位：flow と単独イベント

`flows.yaml` は Phase 1–7 を **生成（`<base>-generate`）→ 修正（`<base>-revise`）** の順に並べる。
修正イベントは**毎回走る**。人が修正を選んでいなければ修正 Skill は何も編集せず、
修正イベントの検査・人間レビュー・承認のゲートは省略される（停止は増えない）。

| コマンド | 進める単位（`--call`） |
|---|---|
| `/aidd-requirements-init` | `requirements-init`（Phase 1–3 の 6 イベント） |
| `/aidd-requirements` | `requirements-plan` → feature ごとに `requirements --item <名>` → `requirements-cross-gate` |
| `/aidd-design` | `design-plan` → feature ごとに `design --item <名>` → `design-cross-gate` → `docs` |
| `/aidd-tasks` | `tasks-plan` → feature ごとに `tasks --item <名>` → `tasks-gate-run` |
| `/aidd-implement` | `implement-task`（生成・修正）をタスクの固定 task_item ごとに実行 → `implement-review --item <feature>`。実際のcallはL3がflows.yamlから解決する。詳細は [実装契約](implementation/contract.md) |

feature の順序は `advance` の結果（計画の `対象 feature と順序`）に従う。完了した単位を
もう一度 `advance` しても、L0 が済んだ unit を飛ばして `done` を返す（再開は同じ入口で行う）。

```text
W --call <flow|event> [--item <feature>] advance
W --event <返された event> [--item <返された item>] --payload <保存したJSON> submit
W --event <返された event> [--item <返された item>] --payload <保存したJSON> --actor <実回答者> respond
```

返却の `result.status` と `allowed_actions`、`next_action`（次に人がすべきことの 1 行）に従う。
`next_action` は人へそのまま伝える（alpha2 の Step 6）。

| result.status | ホストの処理 |
|---|---|
| emit、通常 Skill | 指定 SKILL.md を Read し、context の authoring_inputs・対象・回答・修正依頼（repair）を渡して実行し、結果を submit |
| emit、isAgent: true | check-runner を別コンテキストで起動し、target/calls、snapshot_path / findings_path / inspection_path を渡す。完了を待って submit |
| wait、計画 | detail の計画を**そのまま**人へ提示し、了承（accept-plan）か変更指示（change-plan）を待つ |
| wait、review | detail の提示文を**そのまま**人へ提示し、判断・解消確認・承認を待つ（§3） |
| waiting | 生成途中の質問・差戻し候補を提示し、回答（answer）または差戻し（repair）を待つ |
| blocked | 差戻しが未解消。`blockers` の target_event / target_item の flow を先に進める（§4） |
| done | 次の単位へ進む |
| fail | 理由を人へ示して停止する。機械ゲートへ外部から成功を記録しない |

workflow CLI 自体の終了コードは成功0／失敗1。`fail` でも `operation_applied: true` なら受領は保存済み。

### 進捗の提示

進捗を人に提示する直前に `W --event <event> progress` を実行し、返された一覧を示す。
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
completed は今回の検査処理と記録が完了したことを意味する。形式不備で意味検査を省略した
場合も含み、必要な全検査の実施・指摘0件・承認を意味しない。

## 3. 計画と人間レビュー

**計画**：detail を提示し、人の回答に応じて次のどちらかを respond する。

- 了承：`{"operation_id":..., "action":"accept-plan", "dispatch":<wait の dispatch>, "data":{"note":"今回は上位2件だけ等、進め方の指示があれば"}}`
- 対象・順序の変更（Phase 4 / 5 / 7）：`{"action":"change-plan", "dispatch":..., "data":{"instruction":"実際の変更指示"}}`。
  Phase 3 への差戻しとして feature 一覧を修正・再検査・再承認し、その後に計画を出し直す。
- 「開始してよいですか」だけを問わない。計画を示さずに可否を尋ねない。

**人間レビュー**：detail は alpha2 の ③ 提示文の形式で出る。見出し・選択肢の記号・並びを変えずに提示し、
推奨・既定値を示さない。Skill 名・agent 名を出さない。回答は人の言葉のまま転記する（要約・言い換えをしない）。

回答の種類（いずれも直前の返却の `review_context` を `expected` にコピーし、回答ごとに新しい operation_id を付ける）:

| action | data | 用途 |
|---|---|---|
| decisions | `{"answer":"1:A / 2:C 理由 / 3:D 理由"}` または `{"answer":"全件:A"}` | 指摘ごとの判断（A 修正 / B 差戻し / C 対応せず進める / D 未対応）。C と D は理由必須。前回までの指摘は `2-1:C 理由` のように「回数-番号」で指す。複数スコープの一括確認では先頭に `feature:x` を付ける |
| decision | `{"scope","run","number","decision","reason"}` | 1 件ずつの判断（decisions と同じ意味） |
| repair | `{"event","item","targets","findings":[{phase,scope,run,number,instruction}]}` | 判断 A/B の実行。修正の内容・対象ファイルは人が決める（§4） |
| resolve | `{"scope","run","number"}` | 再検査後、前回の修正・差戻しの解消を人が確認する |
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

## 4. 修正・差戻し

判断 A（修正）/ B（差戻し）を記録したら、人が決めた修正指示と対象で `repair` を respond する。

- **同じ工程の修正**（A）：`event` は当該工程の `<base>-generate`、`item` は当該 feature。生成レビューでの
  repair は、そのレビューへの回答として記録され、flow はそのまま修正イベントへ進む（修正 Skill → 再検査 → 再レビュー）。
  再レビューで旧指摘を `resolve` し、新しい指摘に判断してから承認する。何度でも繰り返せる。
- **上流への差戻し**（B）：`event` / `item` は戻し先（所有工程）の `<base>-generate` と feature。
  戻し先の成果物と、指摘を出した成果物が開き直される（Phase 7 からの design 差戻しでは docs も対象）。
  修正後に入力内容が変わった場合は、その入力を実際に使う下流成果物も再検査へ戻す。
  上流の再承認だけで下流の完了証跡を書き換えない。関係しない承認済み成果物はそのまま。
  返却は `blocked` / `rollback`。戻し先の flow を進めて修正・再検査・承認すると、その承認で差戻しは
  「上流の再承認済み」になる（alpha2 と同じく、上流の再承認で差戻しが解ける）。続けて元の flow を進めると
  指摘元の成果物が見直され、再検査後に旧指摘を `resolve` して承認した時点で差戻しは解消済みになる。
  blocker の履歴は削除しない。自動で解けなかった場合だけ、同じ blocker ID を
  `upstream-approved` / `resolve-rollback` に渡して記録する（`--payload '{"blocker":"ID"}' --actor <人>`）。
- **横断検査・tasks 全体確認での修正**：`event` / `item` に対象 feature の `<base>-generate` を指定する。
  その feature の flow を進めて修正・再検査・承認した後、横断検査（または `tasks-gate-run`）を再実行する。
- **作成中に判明した差戻し**（waiting の return_candidates）：人が差戻しを選んだら、戻し先の event / item で
  `W --event <戻し先の generate> [--item <feature>] --payload <JSON> --actor <人> repair` を実行する。
  payload は `{"origin":"authoring-candidate","candidate":{"event":"<作成中の event>","item":"<feature>","index":0},"targets":[...],"instruction":"実際の指示"}`。
  戻し先を修正・承認すると、作成中の工程が続きから再開する（Phase 7 から design へ戻した場合は docs も見直す）。
- **新しい上流要求**（下流の壁打ちで判明）：要求一覧は Phase 1 だけが更新する。Phase 1 への差戻しとして扱う。
- **承認済み成果物をもう一度確認したい**：`W --event <generate> [--item] --payload '{"instruction":"実際の指示"}' --actor <人> reopen`。
- フロー外で承認済み成果物や RFP を変えた場合は、次の advance がそれを検知し、その成果物（RFP なら要求一覧）だけを
  修正イベントで見直す手順に戻す。承認を手で付け直さない。

同一 state へのホスト処理は直列にする。検査 agent に本文や進捗を修正させない。
