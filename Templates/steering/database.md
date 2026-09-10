---
status: draft
updated_at: {{ISO_8601_TIMESTAMP}}
---

# データベース標準

> **目的**: スキーマ設計・命名・型・マイグレーション・クエリ・トランザクション・整合性・バックアップ/リカバリ の方針を統一する。
> 個別フィーチャーのテーブル定義は `specs/design.md` の Data Models に書き、
> ここには **全フィーチャーに適用される共通ルール** だけを書く。
> ページネーションの **HTTP 契約** は `api-standards.md`、
> バックアップ暗号化等の **横断防御** は `security.md`、
> サービス全体の **DR 運用手順** は `non-functional.md` を参照する。
> システム全体の ER 図・スキーマは `docs/architecture/data-model.md`、業務コード・区分値・採番ルールは `docs/code-design.md` を参照する。
>
> **テンプレート**: 山括弧で囲んだ大文字の項目は、プロジェクト確定時に実値へ置換する。

## 設計思想

> プロジェクトの DB 設計原則を列挙する。採用しない行は削除する。

- <DB_PRINCIPLE_N>

## 命名規則

> _分担_: フィーチャー固有のテーブル名・カラム定義は `specs/design.md` の Data Models に書く。ここは **命名形式** のみを定義する。
> 主キーの型（UUID / ULID / bigint）は `## 型の指針` で確定する。

| 対象 | 規約 | 例 |
| --- | --- | --- |
| <DB_NAMING_OBJECT_N> | <DB_NAMING_RULE_N> | <DB_NAMING_EXAMPLE_N> |

## 型の指針

> DB エンジン名は `tech.md` で確定する。ID 型は **1 種類に統一** する。

| 用途 | 推奨型 | 備考 |
| --- | --- | --- |
| <DB_TYPE_USE_N> | <DB_TYPE_RECOMMENDED_N> | <DB_TYPE_NOTE_N> |

## マイグレーション

> _分担_: マイグレーションツール選定は `tech.md`。本節は **変更管理ルールとロールアウト手順** のみを定義する。

| ルール | 内容 |
| --- | --- |
| <DB_MIGRATION_RULE_N> | <DB_MIGRATION_POLICY_N> |

### 後方互換のあるロールアウト

| # | 操作 | 手順 |
| --- | --- | --- |
| N | <DB_ROLLOUT_OPERATION_N> | <DB_ROLLOUT_STEPS_N> |

## クエリパターン

> _分担_: ページネーションの HTTP 契約（カーソル / オフセットの API 形式）は `api-standards.md`。
> ここは **DB 層の実装方針** のみを定義する。
> 検索対象カラム・スコアリング・同期方式は `specs/design.md` に書く。

| パターン | 方針 |
| --- | --- |
| <DB_QUERY_PATTERN_N> | <DB_QUERY_POLICY_N> |

> <DB_INDEX_POLICY>

## 接続 / トランザクション

> コネクションプール・アイソレーション・長時間トランザクション禁止を固定し、DB の過負荷やデッドロックを予防する。

| 項目 | 既定 |
| --- | --- |
| <DB_CONNECTION_ITEM_N> | <DB_CONNECTION_DEFAULT_N> |

## 整合性

> _分担_: 所有権チェック・マルチテナントの認可ロジックは `security.md` の `## 認証・認可`。
> ここは **制約の置き場所とマルチサービス整合** の方針のみを定義する。

- <DB_INTEGRITY_RULE_N>

## バックアップ / リカバリ

> _分担_: 暗号化方式・転送時 TLS 等の横断防御は `security.md`。
> サービス全体の DR **運用手順** は `non-functional.md`。
> ここは **取得頻度・RPO / RTO・復元テスト** の数値が正本。

| 項目 | 内容 |
| --- | --- |
| <DB_BACKUP_ITEM_N> | <DB_BACKUP_VALUE_N> |

## 関連ドキュメント

> システム全体の ER 図・スキーマは `docs/architecture/data-model.md` を参照。フィーチャーの Physical Data Model を変更した場合は `docs/architecture/data-model.md` との整合を確認すること。
> 業務コード・区分値・採番ルールは `docs/code-design.md` を参照。

---

*DB の共通ルールを固定するファイルです。フィーチャー固有のテーブル定義・インデックス設計は `specs/design.md` の Data Models に書いてください。*
