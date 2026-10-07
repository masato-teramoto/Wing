# L3 進行制御と L0 ランナーの境界

進捗・差戻し・承認の規則は **L3** が所有する。L1 の Spec テンプレートと main_flow に従う規則だからである。L3 の生成／修正 Skill と、ここで定義する進行制御は別の部品とする。

## 依存方向

**L0 は L3・L4 の枠組みである。** L3・L4 は L0 の設計に従って定義ファイルと Skill・script を書き、L0 がそれを実行する。

```text
                L0（枠組み：bin/・lib/）
     読む：L3 の command.yaml / flow.yaml / action.yaml、L4 の gate.yaml（これだけ）
     呼ぶ：定義に書かれた script（コマンドライン）と Skill（host agent への emit）
          ▲ import してよい          ▲ import してよい
   L3（scripts/・skills/）  ◀── import してよい ──  L4（scripts/・skills/・agents/）
```

- **L0 は L3・L4 を import しない。** 定義ファイル 4 つ以外の L3・L4 のファイル（Skill の本文・script の中身）も読まない。
  Skill・script は、定義に書かれた名前のファイルがあることだけを確かめる。
- **L3・L4 は L0 を import してよい**（`import l0` の後に `execution_context` / `project_state` / `engine_cli` / `host` など）。
  ただし実行（call / report / redo / status）は L0 の CLI を通す。状態ストアのランナー欄は L0 だけが書く。
- **L4 は L3 を import してよい。L3 は L4 を import しない。**
- host agent は入口 Skill（L3）の手順に従い、入口（`scripts/aidd_entry.py <コマンド> <操作>`）だけを呼ぶ。
  入口は L0 の CommandResolver でコマンドと呼出し先を解決する。advance / submit / respond は L0 の host を同じプロセスで
  L3 の規則を渡して実行し、status / report / redo は L0 の CLI へ、それ以外の操作は `host_operations` へ渡す。定義ファイルに hook は無い。
- 同一 state の直列化は L0 の `lib/aidd_lock.py` を共用する。
- `test_layer_boundaries.py` が、L0 が L3・L4 を import しないこと、L3 が L4 を import しないこと、
  L0 が L3・L4 のファイルを開かないことを確かめる。

| 所有元 | 管理するもの | 管理しないもの |
|---|---|---|
| L0 | 定義の読込み・検索（Repository）、コマンドの解決（CommandResolver）、呼出しの実行状態と再開点（Workflow Engine）、flow の手順の展開（FlowExecutor）、アクションの前後のゲート解決と実行（ActionExecutor・GateResolver・GateExecutor）、Run の実行とログ（RunDispatcher）、emit/wait/report/redo、host の入口 advance / submit / respond（`host.py`：排他・操作の記録・dispatch の照合・報告）、実行器の間の文脈（`execution_context.py`）、状態ストアの案件欄の読み書き（`project_state.py`） | 繰り返し（item の集合・順序・修正の回）、feature 定義、Spec の status、承認の充足、差戻しの影響範囲 |
| L3 進行制御 | 定義ファイル（command / flow / action）、host の規則の段（`- hook:`）、入口 Skill の手順（繰り返し）、入力の同期と鮮度、案件進捗、質問待ち、人間判断の記録、差戻し・再開・無効化対象の決定 | 品質観点による指摘の生成、検査 agent の直接起動 |
| L3 生成／修正 | 指定された自分の成果物、完了・待機・失敗の結果、手順の宣言（役割・繰り返し） | phase-progress、ゲート記録、承認、別 Skill の呼出し、L0 の呼出し |
| L4 | `gate.yaml`、指定された対象・入力の検査、当該実行の指摘・差戻し候補、合成 Skill と `calls` の一致の確認 | 人間判断・承認、進行制御、差戻し確定 |
| L1 | 成果物・記録・状態のテンプレート | 実行と進行判断 |

### L3 進行制御の主な script

| script | 責務 |
|---|---|
| `phase_rules.py`（`ExecutionContext`） | 工程の規則。L0 の `ExecutionContext` に工程・feature・入出力の展開・上流を足す。定義は L0 の `execution_context.definitions()` から読む |
| `host_session.py` | host の規則の段（`run_stage`）。L0 の `host.py` が呼ぶ。L3 から L0 の host を使う入口（`advance` / `operate`）も持つ |
| `host_operations.py` | host の操作（operation）の CLI（CommandResolver が L3・L4 の操作を渡す）と、L0 の host が呼ぶ `hook <段>` の入口 |
| `project_progress.py` | 案件の進行状態（待機・結果・修正要求・完了）と、L0 の redo の依頼 |
| `engine_client.py` | L0 の CLI の呼出し（Phase 8 の呼出し先の既定と時間の上限だけが L3 の規則） |
| `review_decisions.py` / `review_operations.py` / `review_contract.py` | 人間の判断・解消・承認の記録 / 再送できる書込み / 記録と承認の照合 |
| `repair_requests.py` | 修正要求・差戻し・再開の記録 |
| `check_*.py` ほか規則確認 script | ゲートとして L0 から実行される規則確認（`gate.yaml` は L4 が持ち、L3 の script を名前で指す） |

host の「操作」（advance / submit / respond / approve など）は operation と呼び、実行単位の Action と区別する。
受渡しの JSON のキー（`action` / `allowed_actions` / `event` など）は互換のため変えない。

## 呼出し契約

- L3 が L0 に渡すのは `--config` / `--root` / `--state` と call/report/redo の引数。工程固有データを追加の L0 引数にしない。
- L0 の JSON は設定一覧、保留中の unit、`type` / `target` / `isAgent` / `requiresHuman` / `calls` を返す。終了コードは 0=完了、10=待機、20=Skill の外部実行、1=失敗。
- `requiresHuman` は待機の機構だけを表す。実行計画か承認かは L3 が決め、script の target は必ず設定に明記する。L0 は既定の承認処理を注入しない。
- `isAgent` は別コンテキストでの実行要求。現行 L0 の実行仲介が `.claude/agents/check-runner.md` へ結び付ける。ホストは L0 の emit に従って起動し、結果を report する。L3 には agent 名の解決や起動処理を追加しない。L3 のフロー設定から検査 Skill 名・calls を参照することは許す（管理資料 `l3_generate/docs/main-flow-control-dependencies-2026-09-23.md` の採用案 A）。
- L0 が script に渡す `AIDD_ROOT` / `AIDD_STATE` / `AIDD_ACTION` / `AIDD_ITEM` / `AIDD_ACTION_UNIT` 等は実行コンテキスト。L3 がそれを工程・対象パス・スコープへ解釈する。
- 生成／修正 Skill には解決済みの対象・承認済み入力・質問回答・人間が選んだ指摘キーを渡す。L4 には検査対象、公開された上流、当該実行のスナップショット（節ごとのハッシュ・前回からの変わった節を含む）・指摘ステージと、検査の前提（`review_premises.py`：指摘の共通ルールのパス・人が確定した回答・却下から学んだ扱い・このスコープの前回までの指摘）を渡す。前提は人が宣言・回答・選択したものだけで、AI が推測した前提は入れない。

emit/wait には発行済みの dispatch ID を付け、report はその ID と同じ call/item のみ受け付ける。
同じ結果の再送は保存結果を返し、次の unit に結果を付け替えない。L0 は一般的な相関管理だけを担当する。
review wait と scope-check 証明の照合、operation_id と expected による人間操作の再送は L3 が担当する。
ホストの進行入口は advance/submit/respond。検査 agent の起動は引き続き L0 emit を受け取ったホストが行う。

## 保存と再開

L0 所有欄は `events` / `trace` / `engine_schema` / `engine_reports` / `host_operations` / `current.call` / `current.return_to_call` / `current.pending`。L3 はこれらを直接書き換えない。L0 は保存前に案件欄を再読込して保持し、自分の所有欄が外部で変わった場合は停止する。L3 の保存補助もランナー欄と未知の既存欄を保持する。

`features` / `feature_manifest` / `workflow` / `blockers` / 派生進捗は L3 所有。再開時は成果物・入力の鮮度を再確認し、無効化する unit の範囲を L3 が決めて公開 `redo` を呼ぶ。L0 は無効化を追記し、以前の実行履歴を残す。単一ホストで直列に実行する。原子的なファイル置換だけを並列トランザクション保証とは扱わない。

## 原本と配布

原本は `l3_generate/main_flow/workflow/`（command / flow / action.yaml・scripts・references）と `l4_governance/main_flow/workflow/gate.yaml`。入口 Skill は同じ L3 の `skills/aidd-*/`。配布では L0 の `bin/`・`lib/` と L3・L4 の設定・scripts・references を `.claude/skills/aidd-common/` に合成する。同一ディレクトリに置くことは所有元の統合を意味しない。所有元は配布の `.main-flow-assets.json` で追跡する。

## 後段の境界検証

動作確認可能な配布物を揃えた後、L0 が設定された Skill・人間待ち script で動くこと、実行前に check-runner 欠落を止めること（calls 不一致は L4 の `check_calls.py`）、子 script の案件更新を L0 が保持すること、redo が履歴を消さないことを確認する。L3 が検査実行成功と承認完了を混同しないことも確認する。
