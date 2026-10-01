# 検証計画の記入ルール

Phase 8のホストが新規作成・変更時に読む。記入先は`.aidd/implementation/config/<feature>.json`。
requirements/design/tasks、steering・docs、既存コード・テスト・実行設定から、タスク選択前に確定する。
以下は現行設定の意味と制約であり、案件のテスト構成や品質基準を新設するものではない。

## 値の選び方

実コマンド・パス・検査の粒度は、承認済み仕様と実環境に合わせて選ぶ。複数の妥当な選択肢があっても、
その範囲で判断して進め、必要な理由を既存のimplement-noteへ残す。例の値・言語・ディレクトリを必須にしない。
既存の検証設定・実行手順を先に照合し、そこで定めたコマンドと実行条件を基点にする。変更が必要なら根拠を確認し、例の値や推測で置き換えない。
仕様の矛盾、判断に必要な根拠の不足、承認範囲を超える変更は質問／差戻しで扱う。
差戻し候補は不足のある文書と箇所を示し、工程番号を推測して指定しない。
必須検査の省略や無条件成功化はしない。実行環境の導入は[実装契約](contract.md#検証レポート用ツールの準備)の準備タスクに従う。

## 記入順と最終確認

1. 既存設定があればそれを基点にし、新規なら下の基本例を使う。featureを置き換え、tasks.mdの全IDをtasksへ写す。
2. 完了条件を確かめる実コマンドをchecksへ定義し、各タスクのcheck_idsから参照する。編集先はallowed_paths、範囲外の読取依存はverification_paths、生成物の除外はgenerated_pathsへ記す。
3. 新規案件では`task_review: {"schema": 2, "engine": "host", "mcp": "ace"}`と各タスクの`review_paths`も記す。編集範囲外の呼出し元・呼出し先・共有fixture等を列挙し、追加依存がなければ`[]`にする。
4. 実テストのまとまりごとにsuitesを定義し、対象タスクのspecification_scopeへそのIDを写す。非コードで対象外にする時だけ補足を読み、両方の理由を記す。
5. feature_checksへchecksの全IDを宣言順に写す。全タスクの必須項目、検査ID・スイートIDの参照先、未使用スイートがないことを確認してから選択する。

## 一般項目

`tasks.<ID>`はtasks.mdの全タスクを同じIDで記す。今回選択したタスクだけへ減らさない。
`checks`は必須検査の共通一覧、`check_ids`は各タスクで実行する部分集合、`feature_checks`は最終検査で再実行する全件である。
複数タスクで同じ検査を共有してよく、1タスク1コマンドや単体テストだけに限定しない。

| 項目 | 型・適用条件 | 意味・記入値 |
|---|---|---|
| `schema` | 整数・必須 | 設定形式の版。現在は`1` |
| `feature` | 文字列・必須 | 対象feature名。ファイル名・実行対象と一致させる |
| `tasks` | オブジェクト・必須 | タスクID→以下のタスク設定 |
| `tasks.<ID>.allowed_paths` | 空でない文字列配列・必須 | Boundaryに沿った編集許可範囲。作成予定のファイル・ディレクトリも指定できる |
| `tasks.<ID>.check_ids` | 空でない文字列配列・必須 | 完了条件と回帰に必要な`checks[].id`。重複なし、checksの宣言順を保持 |
| `tasks.<ID>.tdd` | 真偽値・必須 | コードタスクは`true`。非コードだけの場合の`false`は[補足](verification-plan-options.md#非コードタスク)を参照 |
| `tasks.<ID>.non_code_reason` | 文字列・`tdd=false`時に必須 | 非コード作業と判断する実理由。VERIFYを免除する設定ではない |
| `checks` | 空でない配列・必須 | 実行コマンドと成功条件。インストールや最終レポート処理を混ぜない |
| `checks[].id` | 文字列・必須 | 計画内で一意な検査ID。先頭は英数字、以降は英数字・`_`・`-`、全体1〜96文字 |
| `checks[].argv` | 空でない文字列の配列・必須 | 実行ファイルと引数を別要素にする。shell展開はしない。`{python}`という要素はAIDD実行中のPythonへ置換され、案件のvenvを自動選択しない |
| `checks[].cwd` | 文字列・省略時は`.` | コマンドの作業ディレクトリ。`.`は案件ルート、それ以外は案件ルート相対 |
| `checks[].timeout_seconds` | 整数・必須 | 1コマンドの上限秒数。1〜480。実処理に合わせ、下記の合計上限も守る |
| `checks[].metric` | オブジェクト・任意 | コマンド出力の数値を下限と比較する場合だけ使う。[定義・例](verification-plan-options.md#任意の数値基準)を参照 |
| `feature_checks` | 文字列配列・必須 | `checks[].id`の全件を同じ順序で記す |
| `verification_paths` | 文字列配列・省略時は`[]` | 編集許可範囲の外にある補助コード・設定・提供側コード等をfeature検査の対象版に含める。編集許可は増えない |
| `generated_paths` | 文字列配列・省略時は`[]` | ソース変更検出から除外する生成物。出力先を作成・指定する設定ではない。実ソース・検証入力を隠さない |

パス配列は案件ルート相対、区切りは`/`、ファイルまたは末尾`/`のディレクトリを指定する。glob展開はしない。
絶対パス・`..`を使わない。argv内の相対引数はコマンドがcwdを基準に解釈するため、設定のパス配列と区別する。
argv自体のshell非展開と、`npm run`等が呼ぶ既存スクリプト内の展開は別である。この制約だけを理由に既存の起動コマンドを別コマンドへ書き換えない。
`.aidd/.claude/Templates/specs/steering/docs`等の制御・仕様領域は編集対象にできない。
`.git/.venv/node_modules/__pycache__/.pytest_cache`は自動除外される。追加の除外を編集許可範囲へ重ねない。
必要な読取依存は用途に応じてverification_pathsと下記shared_pathsの両方に指定してよい。

checksのtimeout合計は480秒以内。最終検査では、別設定のレポート実行・後処理も含めて480秒以内に収める。
L0既定600秒・L3外側720秒には終了処理の余裕を残す。超過する場合は構成・上限拡張を明示して判断する。
ソース変更・検証入力・stdout/stderr・結果の版を照合する。検査が実ソースを書き換えた場合は成功にしない。

## 仕様書生成の項目

新規コードタスクではtask_qualityを設定する。実テストから仕様書を生成・差分更新し、タスク末尾で人が確認する。
仕様書内容の独立レビューは追加せず、feature最終の実テストレビューを維持する。

| 項目 | 型・適用条件 | 意味・記入値 |
|---|---|---|
| `task_quality` | オブジェクト | featureの仕様書生成設定。次のschema・suitesを持つ |
| `task_quality.schema` | 整数・設定時必須 | この設定の版。現在は`2` |
| `task_quality.suites` | オブジェクト・設定時必須 | 継続して管理するテスト群のID→スイート設定。IDの文字・長さ条件はchecks[].idと同じ。feature名・タスクIDと同じでなくてよい |
| `suites.<ID>.test_paths` | 空でない文字列配列・必須 | スイート全体のテスト入力。複数ファイルを含められる。変更したテストだけへ絞らない |
| `suites.<ID>.shared_paths` | 文字列配列・必須、`[]`可 | 影響する共通fixture・モック・設定等。依存がなければ`[]`。指定した入力は生成時に実在する必要がある |
| `tasks.<ID>.specification_scope` | 文字列・対象タスクで必須 | `task_quality.suites`に定義したスイートIDを1つ記す。例：`"booking"` |
| `tasks.<ID>.specification_exemption` | 文字列・非コードの対象外指定時に必須 | 仕様書を生成しない実理由。scopeと併記しない。[非コード例](verification-plan-options.md#非コードタスク)を参照 |

1タスク1スイートで、複数タスクが同じスイートを共有してよい。全スイートを少なくとも1タスクに割り当てる。
test_paths/shared_pathsの各配列内で同じパスを重複させない。制御領域・実行証跡・生成物の除外範囲は入力に指定できない。
テストは生成時の実ファイルから収集する。計画時点で作成予定のテストを指定することは妨げない。
task_qualityの適用は仕様書生成の有無を表す。ホストは新規コード案件に上記設定を含める。途中で設定を加減して確認を回避しない。変更時は[修正・再開](contract.md#修正再開)に従う。

## タスクのコードレビュー

新規案件は`task_review: {"schema": 2, "engine": "host", "mcp": "ace"}`を設定する。3観点のL4レビューを
仕様書生成後・人間確認前に1回実施する。準備処理でACEを実行し、その証跡と指摘を同じ3観点レビューへ渡す。
各タスクの`review_paths`は読取り依存の文字列配列で、追加がなければ`[]`を明記する。
allowed_pathsに含まれる実装・テストは自動で対象になる。レビュー時には依存が実在する必要がある。
仕様書用shared_pathsや最終検証用verification_pathsが同じ依存を持つ場合はreview_pathsにも指定する。
宣言だけで影響分析を保証するものではない。必要な依存の不足はレビュー失敗とし、
計画の修正・再開で範囲と理由を確定する。設定はタスク選択後に変更できない。

仕様書設定の有無やtdd=falseはコードレビューの省略条件ではない。
明示的な非コード作業だけを対象外とする場合はnon_code_reasonとreview_exemptionに実理由を記し、
review_pathsを併記しない。VERIFYとfeature最終検査は維持する。
task_review未設定はレビュー非適用を表す。未公開のschema 1は受理せず、schema 2へ統一する。
進行中案件へ設定・ゲートを上書きして移行しない。

MCPに送るのは、その生成・repair executionの開始版との差分にある追加・変更ファイルの現行全文。
同executionのretryは開始版を維持し、別repair executionは新しいbaselineを使う。
MCPへ未変更依存・仕様・ログを送信しない。削除と非コードはhostで確認する。
対象拡張子・サイズ・UTF-8条件を満たさない必須対象は未完了で停止し、対象を黙って除外しない。
設定・入力・アダプター版の変更は再検査が必要。接続設定は配布の`aidd-common/scripts/code_review.json`を参照。
MCP設定はtask_reviewが所有し、task_qualityにmcp設定を重ねない。

## 基本設定例

Pythonの既存unittest構成を使う、コードタスク1件の完全な検証計画例。実テスト・実装はこの後作成できる。
この例ではpyproject.tomlが既存の共通検証設定である。実際の依存が違う場合は置き換え、依存がなければ両配列を`[]`にする。
checksは環境にあるランナーへ合わせる。以下のコマンド・120秒という値を他案件の必須条件にしない。
`feature`とタスクID、編集・読取パス、実コマンドを案件に合わせる。スイートIDを変えたらsuitesのキーとspecification_scopeを一緒に変える。

```json
{
  "schema": 1,
  "feature": "booking",
  "tasks": {
    "1": {
      "allowed_paths": ["src/booking/", "tests/booking/"],
      "check_ids": ["tests"],
      "tdd": true,
      "specification_scope": "booking",
      "review_paths": ["pyproject.toml"]
    }
  },
  "checks": [
    {
      "id": "tests",
      "argv": ["{python}", "-B", "-m", "unittest", "discover", "-s", "tests/booking"],
      "cwd": ".",
      "timeout_seconds": 120
    }
  ],
  "feature_checks": ["tests"],
  "verification_paths": ["pyproject.toml"],
  "generated_paths": [],
  "task_review": {"schema": 2, "engine": "host", "mcp": "ace"},
  "task_quality": {
    "schema": 2,
    "suites": {
      "booking": {
        "test_paths": ["tests/booking/"],
        "shared_paths": ["pyproject.toml"]
      }
    }
  }
}
```

非コードタスク／metricを使う場合だけ[補足の該当節](verification-plan-options.md)を読む。
生成・回答の操作はその時点で[タスク確認手順](task-specification.md)、最終検査用の出力設定はその時点で
[レポート契約](reporting.md)を参照する。レポート設定は別ファイルで最終検査時に固定し、タスクの検査へ混ぜない。
