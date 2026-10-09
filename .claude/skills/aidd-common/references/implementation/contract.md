# Phase 8 実行契約 v3（生成・修正の統合flow）

親request_idは選択集合、子execution_idは単一task_idの今回の生成または修正を識別する。
L0のitemにはtask_itemを使い、同じタスクの生成・修正で固定する。初回生成のexecution_idを
そのtask_itemとして採用し、修正ごとに新しいexecution_idを発行する。最終検査のitemはfeature。

工程の flow `implement` は `[implement-authoring-generate, implement-authoring-revise]`、
`implement-review` は `[implement-gate-run]`。generate/repairは生成・修正の Skill
（手順の宣言 `役割:`）を含む flow `implement`、reviewは `implement-gate-run` を含む flow に対応づける。
`implement` は工程名のため改名できない。レビュー flow の名前は flow.yaml だけで変えられる。
L3が対象と正規flowを選び、L0が順序と前後ゲートを実行する。定義欠落・順序違い・別flowへの
重複所属は開始前に拒否し、直接event呼び出しへ切り替えない。Phase 1〜7の直接event入口は維持する。

生成直後の修正は `context.noop=true`。コード・メモ・検証ログを変更せず、同じ識別子と
completed、空のquestions/return_candidates/changed_findingsを返す。追加の検査・人間承認は行わない。
生成結果と実コードの一致を確認し、空修正を含めてflow全体が完了した後にタスクをチェックする。
修正要求がある場合だけ、同じtask_itemの修正eventをredoし、生成の完了履歴を再利用する。
結果・RED/GREEN/verify・ログは `.aidd/implementation/runs/<execution_id>/` に分け、過去の実行を上書きしない。

再送は同じ操作ID・payload・dispatchを保持する。新しい修正を古い実行の再送として扱わない。

## 案件の検証計画

`.aidd/implementation/config/<feature>.json`をタスク選択前に確定する。
新規作成・変更時に[検証計画の記入ルール](verification-plan.md)を読む。項目定義と基本の完全例の正本である。
既存設定で再開する時は設定と対象版を照合し、変更が必要な項目の定義を参照する。
新規コードタスクでは実テストからの仕様書生成とタスク末尾確認を有効にする。
生成emit・人間待機時の操作は[タスク確認手順](task-specification.md)をその時点で参照する。
可読レポートは最終検査前に別設定を用意し、[レポート契約](reporting.md)を参照する。
必要な検証対象・対象版の確認は省略しない。設定変更後の再開は本書の「修正・再開」に従う。

## タスク内の操作

### 検証・レポート用ツールの準備

導入対象・版の条件・導入先・変更範囲・実行方法・ネットワーク取得は、通常のtasks本文と設計を根拠にする。
Phase 7のタスク一覧の最終レビューでまとめて承認し、その範囲内の導入で別の確認を要求しない。
最初のtasks-planの了承だけでは導入を始めない。現在の上流・全体承認の検証をそのまま使う。

作成Skillは変更を伴わない確認を先に行い、必要な場合だけ承認済みの案件スクリプトやOSS標準コマンドを
通常のタスク作業として実行する。既存環境で足りれば導入を省く。実際の版・実行結果・変更ファイル・ログの場所を
implement-noteへ記録する。新しいツール・範囲外の依存更新・既存環境の削除が必要ならwaiting／差戻しで
計画の修正・再承認へ戻す。CC自身の実行権限確認は利用環境に従い、迂回しない。

導入をcheck_ids・feature_checks・reportingのchecks/postprocessへ入れない。導入終了後に、
必要な版・機能の利用可能性を変更なしでVERIFYする。環境準備だけならtdd=falseとnon_code_reasonを使えるが、
製品コードの実装を含むタスク全体のTDDを免除しない。最新VERIFYとflow末尾確認なしに完了しない。
新規作成を提供するスクリプトは専用の新規配置先でその経路も検証する。既存環境の利用だけが担当範囲なら、
新規作成の検証を一律に要求しない。手動復旧とスクリプトの再現確認は別の実績として記録する。
dev/test依存やmanifest/lockfileの共有は許容する。追跡する依存定義はallowed_pathsで管理し、生成物除外へ隠さない。
案件本来のビルド・配布物が揃った段階で依存衝突と製品への混入を確認する。

導入にも外側の実行上限内のtimeoutを設ける。長い処理は分割・事前取得を検討し、検査の時間枠へ導入を混ぜない。
中断時はプロセスと実環境を確認してから同じ承認範囲で再開する。稼働中の導入へ重ねて起動しない。
通常タスクの再送制御は使うが、外部の導入処理にexactly-once・自動rollbackを保証しない。
専用setup設定・action・承認状態は追加しない。CCとAIDDを起動する最低限の環境は配布の前提とする。

### 既存の補助操作

配布ルートの `python -X utf8 -B .claude/skills/aidd-common/scripts/aidd_entry.py /aidd-implement
--action <emit.event> --item <emit.item> --payload <JSON> <action>` を使う。生成Skillが行える更新は次の補助操作だけである。

- `implement-note`: `{execution_id, operation_id, section, text}`。sectionは「決定ログ」「既知の制約 / 残課題」「後続への申し送り」。判断時に1行を追記する。送り先もtextに記す。
  制約の解消は元の記述を特定し、決定・確認結果を添えて同じ制約欄へ追記する。履歴の削除や新しい状態機構は不要。
- `implement-check`: `{execution_id, stage: "red|green|verify", expected_failure?: "予期する失敗と理由"}`。redでは実際の失敗原因を読み、環境エラーを仕様のREDと扱わない。

tasks.mdを直接書き換えない。末尾ゲートで証跡を確認し、flow全体のL0完了後にL3がチェックを確定する。
計画本文の修正は上流へ返す。コード・テスト・設定の編集はallowed_paths内だけ。
上流（context の `upstream`）は approved を前提とする。ただし context の `unreviewed_inputs` に挙げた入力
（上流工程の `target_review` から外れ、検査・承認されない draft）は、approved でなくても読む。これを理由に
failed・waiting・差戻し候補にしない。タスク実装・修正と最終検査の context の両方に同じ規則で渡る。

```json
{
  "status": "completed",
  "request_id": "親ID", "execution_id": "子ID", "feature": "booking", "task_id": "1",
  "questions": [], "return_candidates": [], "changed_findings": [], "summary": "実際の変更と検証結果"
}
```

waiting/failedも同じ識別子と配列、reason、変更済みファイルと検証状況を返す。
task_ids配列を子の結果へ入れない。修正のchanged_findingsは入力repair_findingsと一致させる。
completedは作業結果だけを表す。L3が実差分・証跡・task更新を照合し、L0の末尾完了後に完了証明を発行する。

## 修正・再開

featureレビューの実回答で修正を記録した後、event=implement-gate-run/item=featureで
`implement-repair` に `{request_id, expected: <review_context>, findings: [{phase: "implement",
scope: "feature:booking", run: 1, number: 1, instruction: "実際の指示", task_ids: ["1"]}]}` と実actorを渡す。
同じ指摘の複数task_idsは別アクションへ分割し、全件の完了と全体再検査まで解消しない。
上流への差戻しは既存のrepair/upstream-approved/resolve-rollbackを用いる。

単なる応答喪失は同じsubmit/操作IDで再送する。末尾確認だけ未了ならSkillを再実行しない。
タスクのコード再編集が必要ならホストが `implement-retry` に `{execution_id, reason}` を渡す。
生成のretryは生成と空修正、修正のretryは修正だけをredoする。質問への `answer` にも
`{execution_id, answers}` を渡す。補助操作はcontext内の今回のexecution_idを必須とし、
同じtask_itemでも古い実行IDの操作・古い質問への回答を拒否する。
外部コード・上流・検証計画の変更は、原因を確認し承認済み入力を揃えてから、
`implement-rebase` に実actorと `{operation_id, reason}` を渡す。履歴を残し全タスクの再検証を要求する。
`.aidd/implementation/**/running.json` がrunningなら二重起動しない。検査と子プロセスの停止を確認し、
`aidd_entry.py recover-checks --processes-stopped` で該当markerを退避してから再試行する。
引数なしの `recover-checks` は対象パス・PIDを表示するだけ。ログ・完了証跡は変更せず、退避記録を
`.aidd/recovery/checks-<id>/` に保存する。PIDがnullでも停止を確認し、プロセス不明のまま実行しない。
ランナー自身が停止を確認した後のログ・証跡書込みエラーはinterruptedとして記録し、次回の再試行を許可する。
OS停止などで停止確認できなかった場合やmarkerの更新も失敗した場合は、runningのまま残す。

### α版の配置場所変更

全プロセスを止め、`.aidd`・`.claude`・成果物を含む案件フォルダ全体を短い場所へ移して、
移動先を作業フォルダとして同じ入口コマンドを使う。元のコピーと移動先を同時に動かさない。
本対応を導入済みで、実行資材も証跡も同じまま配置場所だけを変える場合は、rebaseを要求しない。
対象は同一OS内の移動と案件内のstate。旧版案件に復旧修正を適用すると資材ハッシュが変わるため、
そのまま旧タスクを続行しない。既存の `implement-rebase` で履歴を残してPhase 8を再検証・再承認する。
Phase 1〜7の承認・入力が有効でflow定義も同じ場合は、全工程をやり直す必要はない。
共通資材が変わるため、他featureのPhase 8も再検証の対象になり得る。
適用対象・停止条件・操作順は[既存案件の復旧手順](../workspace-recovery.md)に従う。

α版では、実行・回答・完了証跡のrootの絶対位置は同一性の条件から外し、stateは案件ルートからの
相対位置で照合する。実行ID・dispatch・回答内容・成果物と設定のハッシュは照合を続ける。
既存証跡・回答・操作履歴のバイト列は書き換えず、案件内の絶対参照は読取り時に移動先へ対応付ける。
この緩和により、案件全体の複製も同じ案件の継続として扱う。別案件との分離を配置場所だけでは保証しない。

タスクgateの公開は元の本文とハッシュを実行記録へ一緒に保存してから公開ファイルを書く。
途中で移動しても元の本文で再送し、配置位置以外の差異は拒否する。
旧形式でハッシュだけが残り元の公開本文が無い場合は、移動後に本文を推測して補わず、明示的にrebaseする。

案件外のstate・外部設定ファイルは移動対象に含めない。検証コマンドに直書きした絶対パスや
仮想環境の移動互換性は別途確認する。コード・上流・検証計画の内容を変えた場合は通常の再検証が必要。
長いパスが無効なWindowsでは、例えば `C:\w\project` へ移す。feature名・check ID・レポートの
内部階層も短く保つ。旧版で残ったrunning記録がある場合だけ、上記の復旧コマンドを使う。

親要求・子実行・feature状態・最終検査manifestには `flow_contract` を保存する。
callの対応、command/flow/action/gateのハッシュが一致する場合だけ再開する。
submit/respondは実dispatchまたはreview_contextのcall/event/itemを保持する。
retry/rebase/上流変更によるredoも正規flowを使用する。

### 旧配布環境からの切り替え

更新前に案件をコピーして保管し、未回答dispatch・未完のhost操作・旧タスク実行を旧配布環境で確定する。
`flow_contract.schema=2` より前の進行中タスクは新環境で継続しない。
旧環境で完了まで進められない場合は、コピー上で原因と証跡を調査する。
L0の履歴キーにはflow名が含まれるため、名前だけを置換したり新flowの成功印を作ったりしない。

旧環境の完了済み状態も新flowの完了扱いには移さない。未回答dispatch・進行中実行のない境界で
`implement-rebase` に実actorと `{operation_id, reason}` を渡し、新request_idで全タスクを
再検証する。旧証跡と旧完了表は履歴に残し、新しいtask_itemで生成から開始する。
新flowで全タスクと最終検査を完了し、実際の人間承認を得る。以前の承認は履歴として残す。
設定変更時も、元の設定に戻すか、同じ手順で明示的にrebaseする。

## 検査と承認

コードprofile `implementation-code-v1` のreview.jsonは対象コードの在庫（追加・削除を含む）、
上流、計画、tasks完了証跡、検証計画、flow契約の機械manifest。既存v2表の承認ハッシュはmanifestのSHA256である。
検査対象（review_targets）と `unreviewed_inputs` は、Phase 1〜7 と同じ規則で決まる（Phase 8 の例外は無い）。
最終検査はアクション本体（implement-gate-run）が行い、`tasks-gate-run` と同じく検査ゲートの `target_review` を持たないため、
検査対象は feature の出力すべてになる。上流の `unreviewed_inputs` は入力の例外であり、検査対象ではない。
manifestだけの変更検査ではなく、毎回その中身と実ファイルを再照合する。実コードにstatusを書かない。
全ツール実施・成功と全意味観点の最新実績が必要。承認は実review waitへの実回答のみで保存する。
