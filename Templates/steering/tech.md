---
status: draft
updated_at: {{ISO_8601_TIMESTAMP}}
---

# 技術スタック

> このファイルは **プロジェクト全体で固定する技術的前提** を記述する steering ドキュメントです。
> エージェント・人間どちらもここを参照することで、フィーチャーごとに別スタックを選ばないようにします。
> その機能だけで使う追加ライブラリは `design.md` の Technology Stack に書いてください。

> **論理構成・配置モデル・通信パターン** は [`architecture.md`](./architecture.md) を参照してください。本ファイルには製品名・版・検証手順のみを書きます。
>
> **テンプレート**: 山括弧で囲んだ大文字の項目は、プロジェクト確定時に実値へ置換する。

## コアテクノロジ

> 区分は例。プロジェクトで使わない区分は行ごと削除し、足りない区分は行を追加する。

| 区分 | 採用 | バージョン | 備考 |
| --- | --- | --- | --- |
| 言語（FE） | <CORE_FE_LANGUAGE> | <CORE_FE_LANGUAGE_VERSION> | <CORE_FE_LANGUAGE_NOTE> |
| 言語（BE） | <CORE_BE_LANGUAGE> | <CORE_BE_LANGUAGE_VERSION> | <CORE_BE_LANGUAGE_NOTE> |
| フレームワーク（FE） | <CORE_FE_FRAMEWORK> | <CORE_FE_FRAMEWORK_VERSION> | <CORE_FE_FRAMEWORK_NOTE> |
| フレームワーク（BE） | <CORE_BE_FRAMEWORK> | <CORE_BE_FRAMEWORK_VERSION> | <CORE_BE_FRAMEWORK_NOTE> |
| ランタイム | <CORE_RUNTIME> | <CORE_RUNTIME_VERSION> | <CORE_RUNTIME_NOTE> |
| データベース | <CORE_DATABASE> | <CORE_DATABASE_VERSION> | <CORE_DATABASE_NOTE> |
| キャッシュ / KVS | <CORE_CACHE> | <CORE_CACHE_VERSION> | <CORE_CACHE_NOTE> |
| メッセージング | <CORE_MESSAGING> | <CORE_MESSAGING_VERSION> | <CORE_MESSAGING_NOTE> |

## 主要ライブラリ

> 開発パターンに影響する主要ライブラリのみ。全依存はここに書かない。繰り返しが必要な項目は `*_N` を行追加用スロットとして使う。

- **ORM / クエリ**: <LIB_ORM> — <LIB_ORM_REASON>
- **バリデーション**: <LIB_VALIDATION> — <LIB_VALIDATION_REASON>
- **テスト**: <LIB_TEST> — <LIB_TEST_REASON>
- **認証**: <LIB_AUTH> — <LIB_AUTH_REASON>
- **HTTP クライアント**: <LIB_HTTP_CLIENT> — <LIB_HTTP_CLIENT_REASON>
- **<LIB_CATEGORY_N>**: <LIB_NAME_N> — <LIB_REASON_N>

## 開発環境

### 必須ツール

| ツール | バージョン | 用途 |
| --- | --- | --- |
| <TOOL_NAME_N> | <TOOL_VERSION_N> | <TOOL_PURPOSE_N> |

### 推奨 OS / IDE

- OS: <RECOMMENDED_OS>
- IDE: <RECOMMENDED_IDE>、推奨拡張: <RECOMMENDED_IDE_EXTENSIONS>

### Git戦略

<GIT_BRANCHING_MODEL> を採用する。
保護ブランチ `<PROTECTED_BRANCH>`（直接 push 禁止・PR 必須・CIによる <CI_REQUIRED_CHECKS> の通過必須）から短命ブランチを切り、<MERGE_STRATEGY> で取り込む。
※マージ条件・詳細ルールは `## 開発標準`、CI 詳細は本ファイルの `## テスト方針` > `### CI 統合`、本番リリース・障害対応は `non-functional.md`、シークレット管理は `security.md` を参照。

#### 運用ルール一覧

| 項目 | 運用ルール |
| --- | --- |
| **ブランチ名** | <BRANCH_NAMING_RULE> |
| **仕様管理 (spec)** | <SPEC_MANAGEMENT_RULE> |
| **コミット** | <COMMIT_CONVENTION_RULE> |
| **PR (プルリク)** | <PR_RULE> |

**禁止事項:**

- <GIT_PROHIBITED_PRACTICE_N>

※リリース時のみ、`<PROTECTED_BRANCH>` ブランチに <RELEASE_TAG_CONVENTION>（例: `v1.2.3`）を付与する。

## 共通コマンド

```bash
# 依存インストール
<CMD_INSTALL>

# ローカル開発
<CMD_DEV>

# ビルド
<CMD_BUILD>

# テスト（全体）
<CMD_TEST_ALL>

# テスト（単一ファイル）
<CMD_TEST_SINGLE>

# Lint / フォーマット
<CMD_LINT> && <CMD_FORMAT>

# 型チェック
<CMD_TYPECHECK>
```

> ここに書いたコマンドは、このリポジトリで変更を検証するときの **標準手順** です。人間の開発者・CI・実装を支援するエージェントは、いずれもここを起点にしてください。プレースホルダや未検証のコマンドは残さず、**ローカルで実際に成功する** ものだけを記載してください。

## 開発標準

エージェント・人間ともに、フィーチャー実装で次を守る（詳細設定はリポジトリの Lint / CI に委ねる）。

- **型安全**: <DEV_STANDARD_TYPE_SAFETY>
- **API 境界**: <DEV_STANDARD_API_BOUNDARY>
- **品質ゲート**: <DEV_STANDARD_QUALITY_GATE>
- **レビュー**: <DEV_STANDARD_REVIEW>

## 主要な技術選定と理由

> なぜこのスタックを選んだか、代替案を含めて 1 セット 3〜5 行で。議論になりやすいカテゴリ（言語・FW・DB 等）だけ書く。不要なら節ごと省略可。

### 言語: <TECH_CHOICE_LANGUAGE>

- **採用理由**: <TECH_CHOICE_LANGUAGE_REASON>
- **代替案**: <TECH_CHOICE_LANGUAGE_ALTERNATIVE>
- **再評価条件**: <TECH_CHOICE_LANGUAGE_REEVAL>

### フレームワーク: <TECH_CHOICE_FRAMEWORK>

- **採用理由**: <TECH_CHOICE_FRAMEWORK_REASON>
- **代替案**: <TECH_CHOICE_FRAMEWORK_ALTERNATIVE>
- **再評価条件**: <TECH_CHOICE_FRAMEWORK_REEVAL>

### データベース: <TECH_CHOICE_DATABASE>

- **採用理由**: <TECH_CHOICE_DATABASE_REASON>
- **代替案**: <TECH_CHOICE_DATABASE_ALTERNATIVE>
- **再評価条件**: <TECH_CHOICE_DATABASE_REEVAL>

## 命名規則

> _分担_: ディレクトリ構成・import / path alias は `architecture.md` を参照する。ここは **識別子・ファイル名・テーブル名等の命名形式** を定義する。

| 対象 | 規約 | 例 |
|---|---|---|
| <NAMING_TARGET_N> | <NAMING_CONVENTION_N> | <NAMING_EXAMPLE_N> |

## コード規約

> 自動チェックに任せられないコーディング方針をここに書く。Linter / Formatter で機械チェックできる項目（インデント幅・セミコロンなど）は書かない。

- **<CODE_RULE_TOPIC_N>**: <CODE_RULE_DETAIL_N>

## 例外処理

> このセクションは **実装レベルの例外処理** を扱う。
> エラー区分・共通レスポンス形式・API 契約は `api-standards.md` の `## エラーハンドリング（API 契約）`、
> ログ・アラート・リトライ・監視（観測部）は `non-functional.md` の `## 信頼性・観測性` を参照する。

### 例外処理フロー

> ここでは **例外オブジェクト** を各箇所でどう扱い、上位層に渡していくかを定める（exception propagation）。
> 識別子（`requestId` / `traceId`）の下流伝播は `non-functional.md` の「ログ方針 > トレース ID / requestId の伝播」を参照。
> _分担_: フィーチャー固有の例外クラス一覧は `specs/design.md` の Error Handling に書く。

| 箇所 | 方針 |
| --- | --- |
| <EXCEPTION_LAYER_N> | <EXCEPTION_LAYER_POLICY_N> |

### 例外クラス命名規約

| 種別 | 命名 / 用途 |
| --- | --- |
| <EXCEPTION_BASE_CLASS_N> | <EXCEPTION_BASE_CLASS_RULE_N> |

| # | ルール |
| --- | --- |
| N | <EXCEPTION_NAMING_RULE_N> |

### グローバルハンドラ

> <GLOBAL_HANDLER_APPROACH>

| フレームワーク | 実装場所 |
| --- | --- |
| <GLOBAL_HANDLER_FRAMEWORK_N> | <GLOBAL_HANDLER_LOCATION_N> |

| # | ルール |
| --- | --- |
| N | <GLOBAL_HANDLER_RULE_N> |

## テスト方針

> **目的**: テストの方針・配置・命名・種類・構造・モック方針・カバレッジ目標を統一する。
> 個別フィーチャー固有の **テスト観点** は `specs/<feature>/design.md` に書き、
> **完了条件** は `specs/<feature>/tasks.md` に書き、
> ここには **全フィーチャーに適用される共通のテストルール** だけを書く。
> テストツール・実行コマンドの正本は本ファイルの `## 共通コマンド`、アサート対象のエラーコード形式は `api-standards.md` を参照する。
> CI 品質ゲートと PR マージ条件の連携は本ファイルの `## 開発標準` と整合させる。

### 基本方針

> プロジェクトのテスト原則を列挙する。採用しない行は削除する。

- <TEST_PRINCIPLE_N>

### 配置 / 命名

> _分担_: フィーチャー固有のテストファイル一覧は `specs/<feature>/tasks.md` / `design.md` に書く。
> ここは **リポジトリ全体の配置・命名規約** のみを定義する。

#### 配置パターン

| パターン | 例 | 備考 |
| --- | --- | --- |
| <TEST_LAYOUT_PATTERN_PRIMARY> | <TEST_LAYOUT_EXAMPLE_PRIMARY> | <TEST_LAYOUT_NOTE_PRIMARY> |
| <TEST_LAYOUT_PATTERN_ALT> | <TEST_LAYOUT_EXAMPLE_ALT> | <TEST_LAYOUT_NOTE_ALT> |

| # | 配置に関するルール |
| --- | --- |
| N | <TEST_LAYOUT_RULE_N> |

#### 命名

| 対象 | ルール | 例 |
| --- | --- | --- |
| ファイル | <TEST_FILE_NAMING_RULE> | <TEST_FILE_NAMING_EXAMPLE> |
| describe | <TEST_DESCRIBE_NAMING_RULE> | <TEST_DESCRIBE_NAMING_EXAMPLE> |
| it / test | <TEST_IT_NAMING_RULE> | <TEST_IT_NAMING_EXAMPLE> |
| E2E シナリオ | <TEST_E2E_NAMING_RULE> | <TEST_E2E_NAMING_EXAMPLE> |

| # | 命名に関する補足 |
| --- | --- |
| N | <TEST_NAMING_NOTE_N> |

### テスト種類

> _分担_: フィーチャーごとに「何を Unit / Integration / E2E で検証するか」は `specs/<feature>/design.md` の Testing に書く。

| 種類 | 範囲 | モック方針 | 速度目標 |
| --- | --- | --- | --- |
| <TEST_TYPE_N> | <TEST_TYPE_SCOPE_N> | <TEST_TYPE_MOCK_POLICY_N> | <TEST_TYPE_SPEED_TARGET_N> |

| # | 選定基準 |
| --- | --- |
| N | <TEST_SELECTION_CRITERIA_N> |

### 構造（AAA）

> Arrange → Act → Assert の骨格で 1 テスト = 1 振る舞いを徹底する。

| # | ルール |
| --- | --- |
| N | <TEST_AAA_RULE_N> |

### モック / フィクスチャ / データ

| # | 方針 |
| --- | --- |
| N | <TEST_MOCK_POLICY_N> |

### テストデータ管理

| 種類 | 方針 |
| --- | --- |
| <TEST_DATA_KIND_N> | <TEST_DATA_POLICY_N> |

### カバレッジ目標

> _分担_: **カバレッジの数値閾値**はプロジェクト共通ルールとして本節のみに書く。
> `specs/<feature>/design.md` の Testing には **検証観点（何を・どの粒度で確認するか）** のみを書き、○％ 以上のような数値は書かない。
> 閾値の **実装**（ツール設定・CI ワークフロー）は本ファイルの `## 共通コマンド` / リポジトリ設定が正本。ここでは **数値目標と例外ルール** のみを定義する。

| 区分 | 目標 |
| --- | --- |
| <COVERAGE_SCOPE_N> | <COVERAGE_TARGET_N> |

| # | カバレッジ運用ルール |
| --- | --- |
| N | <COVERAGE_POLICY_N> |

### CI 統合

> 実行コマンド・ワークフロー定義の正本は本ファイルの `## 共通コマンド` とリポジトリの CI 設定。
> ここは **いつ何を blocking にするか** の方針のみを定義する。

| # | 項目 | 内容 |
| --- | --- | --- |
| N | <CI_TEST_ITEM_N> | <CI_TEST_POLICY_N> |

### 完了条件との接続

> _分担_: 各タスクの観測可能な完了条件は `specs/<feature>/tasks.md` に書く。
> 受け入れ基準（EARS）の原文は `specs/<feature>/requirements.md` が正本。

| # | 接続ルール |
| --- | --- |
| N | <TEST_COMPLETION_RULE_N> |

---

*技術的前提と標準コマンドを固定するためのファイルです。個別フィーチャーが採用する追加ライブラリや実装詳細はここに書かないでください。*
