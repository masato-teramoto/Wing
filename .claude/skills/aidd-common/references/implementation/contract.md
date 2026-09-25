# Phase 8 実行契約 v3（生成・修正の統合flow）

親request_idは選択集合、子execution_idは単一task_idの今回の生成または修正を識別する。
L0のitemにはtask_itemを使い、同じタスクの生成・修正で固定する。初回生成のexecution_idを
そのtask_itemとして採用し、修正ごとに新しいexecution_idを発行する。最終検査のitemはfeature。

既定の `implement-task` は `[implement-authoring-generate, implement-authoring-revise]`、
`implement-review` は `[implement-gate-run]`。`contracts/main_flow.json` の
`phases.implement.flows` はgenerate/repairを同じflow、reviewを別flowへ対応づける。
L3が対象と正規flowを選び、L0が順序と前後ゲートを実行する。定義欠落・順序違い・別flowへの
重複所属は開始前に拒否し、直接event呼び出しへ切り替えない。Phase 1〜7の直接event入口は維持する。

生成直後の修正は `context.noop=true`。コード・メモ・検証ログを変更せず、同じ識別子と
completed、空のquestions/return_candidates/changed_findingsを返す。追加の検査・人間承認は行わない。
生成結果と実コードの一致を確認し、空修正を含めてflow全体が完了した後にタスクをチェックする。
修正要求がある場合だけ、同じtask_itemの修正eventをredoし、生成の完了履歴を再利用する。
結果・RED/GREEN/verify・ログは `.aidd/implementation/runs/<execution_id>/` に分け、過去の実行を上書きしない。

再送は同じ操作ID・payload・dispatchを保持する。新しい修正を古い実行の再送として扱わない。

## 案件の検証計画

`.aidd/implementation/config/<feature>.json` を作成前に確定する。以下は形の例であり、
コマンド・許可範囲・観点は当該案件の実在する仕様とテストへ置き換える。

```json
{
  "schema": 1, "feature": "booking",
  "tasks": {
    "1": {"allowed_paths": ["src/booking/", "tests/booking/"], "check_ids": ["tests"], "tdd": true}
  },
  "checks": [{"id": "tests", "argv": ["{python}", "-B", "-m", "unittest", "discover", "-s", "tests/booking"], "cwd": ".", "timeout_seconds": 120}],
  "feature_checks": ["tests"],
  "verification_paths": ["pyproject.toml"],
  "generated_paths": ["coverage/"]
}
```

taskキーはtasks.mdの全タスクID。チェックは全て必須、最終feature_checksはchecksの順序付き全ID。
allowed_pathsはファイルまたは末尾 `/` のディレクトリで、Boundaryから解決する。
verification_pathsには対象外に置かれたテストハーネス・設定・提供側コード等の読取依存も明示する。
生成物除外は実ソース範囲に重ねない。`.git/.venv/node_modules/__pycache__/.pytest_cache` は実行証跡の対象外。
ソース・検証設定・新規・削除はハッシュ照合する。L4コマンドが実ソースを変更した場合は成功にしない。

チェックのtimeout合計は480秒以内。L0既定600秒のunitとL3外側720秒の間に終了処理の余裕を置く。
それ以上が必要なら構成・L0設定拡張を明示して判断する。timeoutを無視した成功や検査削除で通さない。
argvはshellを介さない。`{python}` は現在のPython。必要な実行環境は案件の承認済み準備タスク、または既存環境で用意する。
coverage等はcheckの `metric: {path, keys: ["total", "percent_covered"], minimum: 80}` として指定できる。
当該コマンドで更新されていない値・欠落・基準未達を成功にしない。完全なstdout/stderrとreceiptを残す。

可読レポートは別ファイル`.aidd/implementation/reporting/<feature>.json`で設定する。
[レポート契約](reporting.md)を参照。タスク内のcheck_idsにはレポート用処理を追加しない。
レポート設定はfeature最終検査の開始時に固定し、タスクのTDD・VERIFY証跡とは分離する。
上記480秒には最終検査のレポート実行・後処理も含める。

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

配布ルートの `python -X utf8 -B aidd-run.py workflow --event <emit.event> --item <emit.item>
--payload <JSON> <action>` を使う。生成Skillが行える更新は次の補助操作だけである。

- `implement-note`: `{execution_id, operation_id, section, text}`。sectionは「決定ログ」「既知の制約 / 残課題」「後続への申し送り」。判断時に1行を追記する。送り先もtextに記す。
  制約の解消は元の記述を特定し、決定・確認結果を添えて同じ制約欄へ追記する。履歴の削除や新しい状態機構は不要。
- `implement-check`: `{execution_id, stage: "red|green|verify", expected_failure?: "予期する失敗と理由"}`。redでは実際の失敗原因を読み、環境エラーを仕様のREDと扱わない。

tasks.mdを直接書き換えない。末尾ゲートで証跡を確認し、flow全体のL0完了後にL3がチェックを確定する。
計画本文の修正は上流へ返す。コード・テスト・設定の編集はallowed_paths内だけ。

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
同じ指摘の複数task_idsは別イベントへ分割し、全件の完了と全体再検査まで解消しない。
上流への差戻しは既存のrepair/upstream-approved/resolve-rollbackを用いる。

単なる応答喪失は同じsubmit/操作IDで再送する。末尾確認だけ未了ならSkillを再実行しない。
タスクのコード再編集が必要ならホストが `implement-retry` に `{execution_id, reason}` を渡す。
生成のretryは生成と空修正、修正のretryは修正だけをredoする。質問への `answer` にも
`{execution_id, answers}` を渡す。補助操作はcontext内の今回のexecution_idを必須とし、
同じtask_itemでも古い実行IDの操作・古い質問への回答を拒否する。
外部コード・上流・検証計画の変更は、原因を確認し承認済み入力を揃えてから、
`implement-rebase` に実actorと `{operation_id, reason}` を渡す。履歴を残し全タスクの再検証を要求する。
`.aidd/implementation/**/running.json` がrunningなら二重起動しない。保存PIDの停止を確認してログと
markerを退避してから再試行する。プロセス不明のままmarkerを削除してはいけない。

親要求・子実行・feature状態・最終検査manifestには `flow_contract` を保存する。
callの対応、events/flows/gatesのハッシュ、L3契約のハッシュが一致する場合だけ再開する。
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
manifestだけの変更検査ではなく、毎回その中身と実ファイルを再照合する。実コードにstatusを書かない。
全ツール実施・成功と全意味観点の最新実績が必要。承認は実review waitへの実回答のみで保存する。
