---
status: draft
updated_at: {{ISO_8601_TIMESTAMP}}
---

# API 設計標準

> **目的**: 命名・URL 構造・リクエスト/レスポンス形式・ステータスコード・認証ヘッダ・バージョニング・エラー表現を統一する。
> API を扱うフィーチャーでは、`design.md` の API Contract セクションは本ファイルとの差分のみを書けばよい状態を目指す。
> エラーボディの詳細フィールド定義・分類は本ファイルの `## エラーハンドリング（API 契約）`、認証ヘッダ・認可（権限チェック）の詳細は `security.md`、
> ページネーションの DB 層方針は `database.md` を正とする。
> 個別フィーチャー固有のエンドポイント定義は `specs/design.md` の API Contract に書き、
> ここには **全 API 共通の「形」** だけを書く。
>
> **テンプレート**: 山括弧で囲んだ大文字の項目は、プロジェクト確定時に実値へ置換する。

## 設計思想

> このプロジェクトの API 設計で何を優先するかの原則を列挙する。後続セクションの判断軸となる。

- <API_DESIGN_PRINCIPLE_N>

## エンドポイントのパターン

> URL の共通形式を固定する。エンドポイントカタログ（実体）はここに書かず、各 `design.md` の API Contract に書く。

```
<ENDPOINT_URL_PATTERN>
```

例:

- <ENDPOINT_EXAMPLE_N>

| ルール | 内容 |
|---|---|
| 名詞・複数形 | <ENDPOINT_NAMING_RULE> |
| 階層 | <ENDPOINT_NESTING_RULE> |
| ID | <ENDPOINT_ID_RULE>（形式は `database.md` と整合） |
| アクション系 | <ENDPOINT_ACTION_RULE> |

## HTTP メソッド

> 採用するメソッドごとに用途・冪等性・安全性を固定する。リトライ設計・キャッシュ設計の根拠になる。

| メソッド | 用途 | 冪等性 | 安全性 |
|---|---|---|---|
| <HTTP_METHOD_N> | <HTTP_METHOD_USAGE_N> | <HTTP_METHOD_IDEMPOTENT_N> | <HTTP_METHOD_SAFE_N> |

## リクエスト/レスポンス形式

> JSON の外側のラッパー構造を統一する。成功とエラーでトップキーを分け、成功レスポンスに `error` を含めない。

> リクエスト形式: <REQUEST_BODY_FORMAT>
> レスポンス形式（成功）: <RESPONSE_SUCCESS_FORMAT>
> レスポンス形式（エラー）: <RESPONSE_ERROR_FORMAT>

エラーボディのフィールド定義・分類は本ファイルの `## エラーハンドリング（API 契約）` に従う（上記の `error` はそのサブセット）。

### パラメータ配置

| ルール | 内容 |
|---|---|
| Content-Type | <REQUEST_CONTENT_TYPE> |
| パラメータ配置 | <REQUEST_PARAM_PLACEMENT> |
| 大量データ | <REQUEST_LARGE_DATA_POLICY> |

## ステータスコード方針

> 「**結果を最も適切に表すコードを選ぶ**」を原則とし、200 で `error` を返す実装は禁止。

| 区分 | コード | 用途 |
|---|---|---|
| <STATUS_CATEGORY_N> | <STATUS_CODE_N> | <STATUS_USAGE_N> |

## 認証情報

> 認証情報の渡し方と実行順を固定する。認証 → 認可 → ビジネスロジックの順を守る。

- 認証情報の標準位置: <AUTH_HEADER_STANDARD>（詳細は `security.md` の `## 認証・認可`）
- 未認証時の扱い: <AUTH_REJECT_POLICY>
- 認可（権限チェック）の方針: <AUTHZ_DEFENSE_POLICY>（詳細は `security.md`）

## 一覧取得（ページネーション / フィルタ / ソート）

> DB 層の方針（カーソル優先等）は `database.md`。ここでは **HTTP クエリと `meta` の契約** のみを固定する。

```
<LIST_QUERY_EXAMPLE>
```

| 機能 | クエリ（既定） | `meta` に含める |
|---|---|---|
| オフセットページ | <PAGINATION_OFFSET_QUERY> | <PAGINATION_OFFSET_META> |
| カーソルページ | <PAGINATION_CURSOR_QUERY> | <PAGINATION_CURSOR_META> |
| ソート | <SORT_QUERY_FORMAT> | — |
| フィルタ | <FILTER_QUERY_FORMAT> | — |
| 全文検索 | <FULLTEXT_QUERY_FORMAT> | — |

- プロジェクトの既定ページネーション方式: <PAGINATION_DEFAULT_CHOICE>（両方許容する場合は `design.md` に明記）
- フィーチャー固有の検索条件は `design.md` の API Contract に差分のみ

## バージョン管理

> API の変更がクライアントに与える影響をコントロールするルールを固定する。

- バージョニング方式: <API_VERSIONING_SCHEME>
- 破壊的変更 → <BREAKING_CHANGE_POLICY>
- 非破壊的変更 → <NON_BREAKING_CHANGE_POLICY>
- 旧バージョンの deprecation: 最低 <DEPRECATION_PERIOD> の猶予期間を設け、レスポンスヘッダ <DEPRECATION_HEADERS> を付与

## エラーハンドリング（API 契約）

> **目的**: エラーの分類・共通レスポンス形式・フィールド規約を統一する。
> 個別フィーチャー固有のエラーコード一覧は `specs/design.md` の Error Handling に書き、ここには **全 API 共通のエラー契約** だけを書く。
> 例外処理フロー・例外クラス命名・グローバルハンドラ（実装部）は `tech.md` の `## 例外処理`、
> ログ・アラート・リトライ・監視（観測部）は `non-functional.md` の `## 信頼性・観測性` を参照する。
> アラート発火時の **対応手順・当番・エスカレーション** は `non-functional.md` の `## 運用・障害対応` を参照する。

### 基本方針（API エラー部分）

> プロジェクトのエラーハンドリング原則を列挙する。採用しない行は削除する。

- <ERR_PRINCIPLE_N>

### 分類

> ハンドリング方針は **エラー区分（Client / Business / Server / External 等）** で決める。
> _分担_: フィーチャー固有のエラーコードと HTTP マッピングの詳細は `specs/design.md` の Error Handling に書く。

| 区分 | 例 | レスポンス |
| --- | --- | --- |
| <ERROR_CATEGORY_N> | <ERROR_CATEGORY_EXAMPLE_N> | <ERROR_CATEGORY_RESPONSE_N> |

### 共通エラー形式

> _分担_: エラーコードの一覧は `specs/design.md` の Error Handling に書く。ここは **レスポンス形式とフィールド規約** のみを定義する。

> レスポンス形式: <ERROR_RESPONSE_FORMAT>

| 項目 | 必須 | ルール |
| --- | --- | --- |
| <ERROR_FIELD_NAME_N> | <ERROR_FIELD_REQUIRED_N> | <ERROR_FIELD_RULE_N> |

### 複数フィールドのバリデーション

| # | ルール |
| --- | --- |
| N | <ERROR_DETAILS_RULE_N> |

---

_API の「形」を統一するためのファイルです。エンドポイントカタログ（実体）はここに書かず、各 `design.md` の API Contract に書いてください。_
