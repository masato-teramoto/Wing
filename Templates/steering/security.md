---
status: draft
updated_at: {{ISO_8601_TIMESTAMP}}
---

# セキュリティ標準

> **責務宣言: このファイルは「横断防御」と「認証・認可」を扱う。**
> 横断防御では **どの機能にも適用される共通の防御パターン**（入力検証、出力エスケープ、シークレット管理、
> トークン/セッションの保管・転送、ヘッダ、攻撃対策、ログ、脆弱性対応）を、
> 認証・認可では **認証フロー本体（誰か → 検証 → 発行 → 失効）と認可方針（モデル → チェック層 → 所有権）** を扱う（本ファイル末尾の `## 認証・認可`）。
> 個別フィーチャー固有のセキュリティ判断は `specs/design.md` の Security Considerations に書く。
> セキュリティインシデント対応の**骨格**は `non-functional.md` の **障害対応フロー**、**具体手順**は同ファイルの **運用手順書の正本** から運用手順書を参照する（セキュリティインシデント時は本ファイルの **修正 SLA** も併用）。
> エラー応答の機密排除は `api-standards.md` の `## エラーハンドリング（API 契約）` を参照する。
>
> **テンプレート**: 山括弧で囲んだ大文字の項目は、プロジェクト確定時に実値へ置換する。

## 基本方針

> プロジェクトのセキュリティ原則を列挙する。採用しない行は削除する。

- <SEC_PRINCIPLE_N>

## 入力検証 / 出力エスケープ

> **入り口**（検証）と **出口**（エスケープ）は別作業。
> 信頼できない入力を止める最終防衛線は **API 境界**。DB 制約は **データ整合性** の最後（`database.md`）。
> _分担_: フィーチャー固有のファイル受付ルールは `specs/design.md` に書く。

### 入り口 — 入力検証

| 層 | この層の役割 | 実装の要点 | 詳細は |
| --- | --- | --- | --- |
| <INPUT_VALIDATION_LAYER_N> | <INPUT_VALIDATION_ROLE_N> | <INPUT_VALIDATION_IMPLEMENTATION_N> | <INPUT_VALIDATION_REFERENCE_N> |

### 出口 — 出力エスケープ

| 出力先 | 防ぐこと | やること | やってはいけない例 |
| --- | --- | --- | --- |
| <OUTPUT_SINK_N> | <OUTPUT_THREAT_N> | <OUTPUT_MITIGATION_N> | <OUTPUT_ANTIPATTERN_N> |

### 共通ルール

| # | ルール |
| --- | --- |
| N | <INPUT_OUTPUT_COMMON_RULE_N> |

## 攻撃対策（主要パターン）

> 設計・実装・レビュー時の確認リストとして使う。

| 攻撃 | 対策 | 参照 |
| --- | --- | --- |
| <ATTACK_PATTERN_N> | <ATTACK_MITIGATION_N> | <ATTACK_REFERENCE_N> |

## シークレット管理

| 項目 | 内容 |
| --- | --- |
| <SECRET_MGMT_ITEM_N> | <SECRET_MGMT_POLICY_N> |

## セッション / トークンの保管・転送

> 発行・失効のタイミングは本ファイルの `## 認証・認可`。ここでは **どう守るか** を書く。

| # | ルール |
| --- | --- |
| N | <TOKEN_STORAGE_RULE_N> |

## 機密データ

| 種別 | 扱い |
| --- | --- |
| <SENSITIVE_DATA_TYPE_N> | <SENSITIVE_DATA_POLICY_N> |

## ヘッダ / トランスポート

> _分担_: CDN / LB の設定手順は `tech.md` または運用手順書。ここは **推奨値** のみを定義する。

| ヘッダ / 設定 | 推奨 |
| --- | --- |
| <SECURITY_HEADER_N> | <SECURITY_HEADER_VALUE_N> |

## セキュリティログ

> ログ形式・共通フィールドは `non-functional.md` の `### ログ方針` を正とする。本節は **記録対象と保護方針** のみ。

| # | ルール |
| --- | --- |
| N | <SEC_LOG_RULE_N> |

## 脆弱性対応

> インシデント対応の**骨格**は `non-functional.md` の **障害対応フロー（プロセス骨格）** を正とする。
> **具体手順**は `non-functional.md` の **運用手順書の正本** から運用手順書を参照する。
> セキュリティインシデント時は本節の **修正 SLA** も併用する。
> _分担_: 本節は **スキャン・SLA・報告窓口** のみを定義する。

| 項目 | 内容 |
| --- | --- |
| <VULN_MGMT_ITEM_N> | <VULN_MGMT_POLICY_N> |

## 認証・認可

> **このセクションは「認証 = 誰か」と「認可 = 何をしてよいか」の方針を扱う。**
> トークン・セッションの **保管・転送の安全** や、横断的な防御（CSRF / CSP 等）は本ファイル上部の横断防御セクション（`## セッション / トークンの保管・転送`・`## ヘッダ / トランスポート` 等）に書く。重複を避け、認証フロー本体（識別 → 検証 → 発行 → 失効）と認可方針（モデル → チェック層 → 所有権）をここに集約する。
> 個別リソースの権限マトリクスやフィーチャー固有のルールは `design.md` の Security Considerations に書く。

### 認証・認可の設計思想

> このプロジェクトの認証・認可で優先する価値観を列挙する。後続（認証方式・認可モデル・セキュリティパターン）の判断基準になる。

- <AUTH_DESIGN_PRINCIPLE_N>

### 認証

#### 認証方式

> このプロジェクトで採用する方式と理由を 1 セットだけ書く。

- **方式**: <AUTH_METHOD>
- **採用理由**: <AUTH_METHOD_RATIONALE>
- **代替案と不採用理由**: <AUTH_METHOD_ALTERNATIVE>

#### 認証フロー（高レベル）

> 識別 → 検証 → 発行 → 添付 → 毎リクエスト検証 という不変の骨格に、プロジェクト固有のステップ（OAuth コールバック等）を当てはめて記述する。署名アルゴリズム等の実装詳細は `specs/design.md`。

| 順 | ステップ |
| --- | --- |
| N | <AUTH_FLOW_STEP_N> |

#### トークン / セッションのライフサイクル

| 項目 | 既定 |
| --- | --- |
| アクセストークン寿命 | <ACCESS_TOKEN_TTL> |
| リフレッシュトークン寿命 | <REFRESH_TOKEN_TTL> |
| 失効トリガ | <TOKEN_REVOCATION_TRIGGER> |
| ローテーション | <TOKEN_ROTATION_POLICY> |
| 保管場所（クライアント） | <TOKEN_CLIENT_STORAGE> — 詳細は本ファイルの `## セッション / トークンの保管・転送` |

#### セキュリティパターン（認証レイヤ）

> 認証フロー設計時に **必ず検討する** 方針。Cookie 属性・CSP・ヘッダ値など **実装の詳細** は本ファイル上部の横断防御セクションを参照。

| パターン | 方針 | 備考 |
| --- | --- | --- |
| <AUTH_SECURITY_PATTERN_N> | <AUTH_SECURITY_POLICY_N> | <AUTH_SECURITY_NOTE_N> |

> **責務境界**: **横断防御の実装**（httpOnly、CSRF、CSP 等）は本ファイル上部の横断防御セクション。本セクションは **いつ発行・失効するか**（ライフサイクル）と、それとセットで決める **認証上のセキュリティ方針**（紐付け・クレーム・ステップアップの要否）のみ記述する。

### 認証 → 認可の契約（AuthContext）

認証成功後、以降のレイヤは **AuthContext のみ** を参照する（生の JWT / セッション payload をドメインに渡さない）。

| 項目 | ルール |
| --- | --- |
| 生成タイミング | <AUTHCONTEXT_CREATION_TIMING> |
| 必須フィールド | <AUTHCONTEXT_REQUIRED_FIELD_N> |
| 任意フィールド | <AUTHCONTEXT_OPTIONAL_FIELD_N> |
| 型の置き場 | <AUTHCONTEXT_TYPE_LOCATION> |
| 消費側 | <AUTHCONTEXT_CONSUMER> |

- クレームに載せる情報は最小限（上記「クレーム」方針と整合）
- フィーチャー固有の権限マトリクスは `design.md` の Security Considerations

### 認可

#### 権限モデル

> このプロジェクトで採用するモデルと理由を 1 セットだけ書く。

- **モデル**: <AUTHZ_MODEL>
- **定義の置き場**: <AUTHZ_DEFINITION_LOCATION>
- **採用理由**: <AUTHZ_MODEL_RATIONALE>
- **代替案と不採用理由**: <AUTHZ_MODEL_ALTERNATIVE>
- **禁止**: コードベース全体での権限名・ロールのハードコーディング

#### チェックの適用箇所

| 層 | 役割 | 例 |
| --- | --- | --- |
| <AUTHZ_CHECK_LAYER_N> | <AUTHZ_CHECK_ROLE_N> | <AUTHZ_CHECK_EXAMPLE_N> |

> **責務境界**: 上記の「例」は **パターン例**。権限名の一覧・リソースごとのマトリクスは `design.md` に書く。二重防御の方針は本ファイル上部の横断防御セクションを参照。

#### 所有権・エンティティ境界

| 項目 | 既定 |
| --- | --- |
| パターン | <OWNERSHIP_PATTERN> |
| 検証タイミング | <OWNERSHIP_CHECK_TIMING> |
| 権限名の形式 | <PERMISSION_NAME_FORMAT> |

### パスワード / MFA

| 項目 | 内容 |
| --- | --- |
| パスワード強度 | <PASSWORD_STRENGTH_POLICY> |
| ハッシュ | <PASSWORD_HASH_POLICY> |
| パスワードリセット | <PASSWORD_RESET_POLICY> |
| MFA | <MFA_POLICY> |
| アカウントロック | <ACCOUNT_LOCK_POLICY> |

### API 間認証（service-to-service）

| 項目 | 内容 |
| --- | --- |
| 方式 | <SERVICE_AUTH_METHOD> |
| スコープ | <SERVICE_AUTH_SCOPE> |
| ローテーション | <SERVICE_AUTH_ROTATION> |
| 監査 | <SERVICE_AUTH_AUDIT> |

---

*横断的な防御パターンと認証・認可の方針を固定するファイルです。フィーチャー固有のセキュリティ判断・権限マトリクスは `specs/design.md` の Security Considerations に書いてください。*
