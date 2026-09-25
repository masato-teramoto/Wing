# L3 進行制御と L0 ランナーの境界

進捗・差戻し・承認の規則は **L3** が所有する。L1 の Spec テンプレートと main_flow に従う規則だからである。L3 の生成／修正 Skill と、ここで定義する進行制御は別の部品とする。

## 依存方向

L3 のホスト入口 → L0 の公開 CLI → 設定に明記した script / Skill。
L0 から L3 の Python モジュールを import しない。L3 は L0 の内部クラスを import せず、JSON 出力、終了コード、実行環境変数を通じて接続する。
同一 state の直列化だけは汎用の公開 `lib/aidd_lock.py` を共用する。業務規則や実行仲介をこのライブラリへ入れない。script の成否と外部実行の報告を受けて再開点を保存する仕組みは L0 が持つ。

| 所有元 | 管理するもの | 管理しないもの |
|---|---|---|
| L0 | 汎用実行属性、unit の順次実行、emit/wait/report/redo、agent の実行仲介、実行履歴・ログの保存 | feature 定義、Spec の status、承認の充足、差戻しの影響範囲 |
| L3 進行制御 | events/flows/gates、入口、入力の同期と鮮度、案件進捗、質問待ち、人間判断の記録、差戻し・再開・無効化対象の決定 | 品質観点による指摘の生成、検査 agent の直接起動 |
| L3 生成／修正 | 指定された自分の成果物、完了・待機・失敗の結果 | phase-progress、ゲート記録、承認、別 Skill の呼出し |
| L4 | 指定された対象・入力の検査、当該実行の指摘・差戻し候補 | 人間判断・承認、進行制御、差戻し確定 |
| L1 | 成果物・記録・状態のテンプレート | 実行と進行判断 |

## 呼出し契約

- L3 が L0 に渡すのは `--config` / `--root` / `--state` と call/report/redo の引数。工程固有データを追加の L0 引数にしない。
- L0 の JSON は設定一覧、保留中の unit、`type` / `target` / `isAgent` / `requiresHuman` / `calls` を返す。終了コードは 0=完了、10=待機、20=Skill の外部実行、1=失敗。
- `requiresHuman` は待機の機構だけを表す。実行計画か承認かは L3 が決め、script の target は必ず設定に明記する。L0 は既定の承認処理を注入しない。
- `isAgent` は別コンテキストでの実行要求。現行 L0 の実行仲介が `.claude/agents/check-runner.md` へ結び付ける。ホストは L0 の emit に従って起動し、結果を report する。L3 には agent 名の解決や起動処理を追加しない。L3 のフロー設定から検査 Skill 名・calls を参照することは許す（管理資料 `l3_generate/docs/main-flow-control-dependencies-2026-09-23.md` の採用案 A）。
- L0 が script に渡す `AIDD_ROOT` / `AIDD_STATE` / `AIDD_EVENT` / `AIDD_ITEM` / `AIDD_EVENT_UNIT` 等は実行コンテキスト。L3 がそれを工程・対象パス・スコープへ解釈する。
- 生成／修正 Skill には解決済みの対象・承認済み入力・質問回答・人間が選んだ指摘キーを渡す。L4 には検査対象、公開された上流、当該実行のスナップショット・指摘ステージだけを渡す。

emit/wait には発行済みの dispatch ID を付け、report はその ID と同じ call/item のみ受け付ける。
同じ結果の再送は保存結果を返し、次の unit に結果を付け替えない。L0 は一般的な相関管理だけを担当する。
review wait と scope-check 証明の照合、operation_id と expected による人間操作の再送は L3 が担当する。
ホストの進行入口は advance/submit/respond。検査 agent の起動は引き続き L0 emit を受け取ったホストが行う。

## 保存と再開

L0 所有欄は `events` / `trace` / `engine_schema` / `engine_reports` / `current.call` / `current.return_to_call` / `current.pending`。L3 はこれらを直接書き換えない。L0 は保存前に案件欄を再読込して保持し、自分の所有欄が外部で変わった場合は停止する。L3 の保存補助もランナー欄と未知の既存欄を保持する。

`features` / `feature_manifest` / `workflow` / `blockers` / 派生進捗は L3 所有。再開時は成果物・入力の鮮度を再確認し、無効化する unit の範囲を L3 が決めて公開 `redo` を呼ぶ。L0 は無効化を追記し、以前の実行履歴を残す。単一ホストで直列に実行する。原子的なファイル置換だけを並列トランザクション保証とは扱わない。

## 原本と配布

原本は `l3_generate/main_flow/workflow/`。入口 Skill は同じ L3 の `skills/aidd-*/`。配布では L0 の `bin/` と L3 の設定・scripts・references・contracts を `.claude/skills/aidd-common/` に合成する。同一ディレクトリに置くことは所有元の統合を意味しない。所有元は配布の `.main-flow-assets.json` で追跡する。

## 後段の境界検証

動作確認可能な配布物を揃えた後、L0 が設定された Skill・人間待ち script で動くこと、実行前に check-runner 欠落と calls 不一致を止めること、子 script の案件更新を L0 が保持すること、redo が履歴を消さないことを確認する。L3 が検査実行成功と承認完了を混同しないことも確認する。
