---
status: draft
updated_at: {{ISO_8601_TIMESTAMP}}
---

# 非機能要件・運用標準

> このファイルは可用性・性能・信頼性・観測性・運用手順の共通標準を定義する。
> 旧 operations.md と error-handling.md（ログ・アラート・監視部）を統合した steering ドキュメント。
> フィーチャー固有の非機能要件は `specs/<feature>/requirements.md` の Non-Functional Requirements に書く。
> エラー区分・共通レスポンス形式・API 契約は `api-standards.md` の `## エラーハンドリング（API 契約）`、
> 例外処理フロー・例外クラス命名・グローバルハンドラ（実装部）は `tech.md` の `## 例外処理`、
> バックアップの **取得頻度・保持期間・RPO / RTO・復元テスト** の数値は `database.md`、
> セキュリティインシデントの **脆弱性対応 SLA** は `security.md` の **脆弱性対応** を参照する。
> 個別フィーチャー固有の監視項目・運用手順書・性能目標は `specs/design.md` に書く。
>
> **テンプレート**: 山括弧で囲んだ大文字の項目は、プロジェクト確定時に実値へ置換する。

## 基本方針

> プロジェクトの運用・観測性の原則を列挙する。採用しない行は削除する。

- <OPS_PRINCIPLE_N>

## 可用性・性能

### サービスレベル（SLO / SLA）

> 数値はプロジェクトで確定する。アラート閾値は本ファイルの `### アラート方針`、
> 閾値超過時の**対応手順**は本ファイルの `### 障害対応フロー（プロセス骨格）` を参照。
> _分担_: 全サービス共通の SLO のみ本節に書く。**機能固有の SLO 追加・監視メトリクス**は `specs/requirements.md` の NFR + `specs/design.md` に書く。

| 指標ID | 目標（SLO） | 計測方法 | レビュー周期 | 備考 |
| --- | --- | --- | --- | --- |
| <SLO_METRIC_ID_N> | <SLO_TARGET_N> | <SLO_MEASUREMENT_N> | <SLO_REVIEW_CADENCE_N> | <SLO_NOTE_N> |

### 優先度定義

| 優先度 | 定義 | 判定条件 | 初動 SLA | 復旧目標 |
| --- | --- | --- | --- | --- |
| <INCIDENT_PRIORITY_P1> | <P1_DEFINITION> | <P1_CRITERIA> | <P1_INITIAL_RESPONSE_SLA> | <P1_RECOVERY_TARGET> |
| <INCIDENT_PRIORITY_P2> | <P2_DEFINITION> | <P2_CRITERIA> | <P2_INITIAL_RESPONSE_SLA> | <P2_RECOVERY_TARGET> |
| <INCIDENT_PRIORITY_P3> | <P3_DEFINITION> | <P3_CRITERIA> | <P3_INITIAL_RESPONSE_SLA> | <P3_RECOVERY_TARGET> |

### 性能・容量運用（方針）

> 機能固有の性能目標・キャッシュ設計は `specs/design.md` の Performance & Scalability。

| 項目 | 方針 |
| --- | --- |
| <CAPACITY_ITEM_N> | <CAPACITY_POLICY_N> |

## 環境

> 用途・デプロイ元の対応（方針）のみを定義する。具体的な IP・ポート・認証情報は書かない。
> ブランチの**命名・保護・マージ条件は `tech.md` の Git 戦略を正とする**（ここで再定義しない）。
> 本節の「デプロイ元」列は、**どのブランチ / 成果物がどの環境へ出るか** の対応のみを定義する。

| 環境 | 用途 | データ | デプロイ元 | 監視 |
| --- | --- | --- | --- | --- |
| <ENV_DEV_NAME> | <ENV_DEV_PURPOSE> | <ENV_DEV_DATA_POLICY> | <ENV_DEV_DEPLOY_SOURCE> | <ENV_DEV_MONITORING> |
| <ENV_STAGING_NAME> | <ENV_STAGING_PURPOSE> | <ENV_STAGING_DATA_POLICY> | <ENV_STAGING_DEPLOY_SOURCE> | <ENV_STAGING_MONITORING> |
| <ENV_PROD_NAME> | <ENV_PROD_PURPOSE> | <ENV_PROD_DATA_POLICY> | <ENV_PROD_DEPLOY_SOURCE> | <ENV_PROD_MONITORING> |

| # | 環境運用ルール |
| --- | --- |
| N | <ENV_OPERATIONAL_RULE_N> |

## デプロイ / リリース

> _分担_: 全サービス共通のリリース方式・承認・ロールバック条件のみを定義する。
> **機能固有のリリース順序・feature flag・段階移行**は `specs/design.md`（Migration Strategy / Performance）に書く。

### リリースモデル

| 項目 | 内容 |
| --- | --- |
| 方式 | <RELEASE_STRATEGY> |
| 頻度 | <RELEASE_CADENCE> |
| 承認 | <RELEASE_APPROVAL_PROCESS> |
| 禁止事項 | <RELEASE_PROHIBITED_PRACTICES> |

### リリース前チェックリスト

| # | 確認項目 | 合格条件 | 必須 |
| --- | --- | --- | --- |
| N | <PRE_RELEASE_CHECK_ITEM_N> | <PRE_RELEASE_CHECK_CRITERIA_N> | <PRE_RELEASE_CHECK_REQUIRED_N> |

### ロールバック条件

| 条件 | 対応 |
| --- | --- |
| <ROLLBACK_CONDITION_N> | <ROLLBACK_ACTION_N> |

### リリース後

| # | 項目 | 内容 |
| --- | --- | --- |
| N | <POST_RELEASE_ITEM_N> | <POST_RELEASE_DETAIL_N> |

## 信頼性・観測性

> ログ・アラート・リトライ・監視 / ヘルスの **実装標準**（旧 error-handling.md のログ監視部）を定義する。
> _分担_: フィーチャー固有の **ログ詳細キー** は各 `specs/design.md` の Components / Error Handling に書く。

### ログ方針

#### ログレベル

| レベル | 用途 |
| --- | --- |
| <LOG_LEVEL_N> | <LOG_LEVEL_PURPOSE_N> |

#### 出力する

| # | 項目 |
| --- | --- |
| N | <LOG_INCLUDE_N> |

#### 出力しない

| # | 項目 |
| --- | --- |
| N | <LOG_EXCLUDE_N> |

#### ログフィールド標準

> 出力形式は `<LOG_OUTPUT_FORMAT>` でプロジェクト確定する（JSON Lines / プレーン / 基盤連携形式等）。
> 形式にかかわらず **フィールド名・型・意味** を全サービスで統一する。

| フィールド | 必須 | 型 | 値の規約 | 例 |
| --- | --- | --- | --- | --- |
| <LOG_FIELD_NAME_N> | <LOG_FIELD_REQUIRED_N> | <LOG_FIELD_TYPE_N> | <LOG_FIELD_RULE_N> | <LOG_FIELD_EXAMPLE_N> |

| # | 禁止事項 |
| --- | --- |
| N | <LOG_PROHIBITION_N> |

#### トレース ID / requestId の伝播

> ここでは **識別子（メタデータ）** を下流コンポーネントに引き継ぐ方針を扱う（context propagation）。
> 例外オブジェクトを上位層に渡す扱いは `tech.md` の `## 例外処理` > `### 例外処理フロー` を参照。

| # | ルール |
| --- | --- |
| N | <TRACE_PROPAGATION_RULE_N> |

### アラート方針

> 閾値超過時の**対応手順**は本ファイルの `### 障害対応フロー（プロセス骨格）` を参照。
> _分担_: 優先度（P1/P2/P3）の定義は本ファイルの `### 優先度定義`。ここは**トリガと通知先**のみを定義する。

| トリガ | 通知先 |
| --- | --- |
| <ALERT_TRIGGER_N> | <ALERT_DESTINATION_N> |

| # | 方針 |
| --- | --- |
| N | <ALERT_POLICY_N> |

### リトライ

> _分担_: リトライ・外部依存遮断の **実装選定** は `tech.md`。本節は **条件・戦略・遮断方針** のみを定義する。

| 条件 | 内容 |
| --- | --- |
| <RETRY_DO_LABEL> | <RETRY_DO_POLICY> |
| <RETRY_DONT_LABEL> | <RETRY_DONT_POLICY> |
| 戦略 | <RETRY_STRATEGY> |
| 冪等キー | <IDEMPOTENCY_KEY_POLICY> |
| 外部依存の遮断 | <CIRCUIT_BREAKER_POLICY> |

### 監視 / ヘルス

> _分担_: ダッシュボードの束ね方は本ファイルの `### 監視・観測（運用面）`。本節は **ヘルスチェックとメトリクス定義** が正本。
> _分担_: フィーチャー固有の監視項目は `specs/design.md` + `specs/tasks.md` に書く。

#### ヘルスチェック

| # | 種別 | パス | 用途 |
| --- | --- | --- | --- |
| N | <HEALTH_CHECK_TYPE_N> | <HEALTH_CHECK_PATH_N> | <HEALTH_CHECK_PURPOSE_N> |

#### メトリクス

| メトリクス | 説明 |
| --- | --- |
| <METRIC_N> | <METRIC_DESCRIPTION_N> |

| # | 方針 |
| --- | --- |
| N | <HEALTH_POLICY_N> |

## 運用・障害対応

### 監視・観測（運用面）

> ログフィールドは本ファイルの `### ログ方針`、エラーレスポンス形式は `api-standards.md` を正とする。
> 本節は **運用者がどこを見るか** のみを定義する。
> _分担_: **機能固有の監視メトリクス・ダッシュボード追加**は `specs/design.md` + `specs/tasks.md` に書く。

#### 監視基盤

| 区分 | 採用 | 用途 |
| --- | --- | --- |
| <MONITORING_CATEGORY_N> | <MONITORING_PLATFORM_N> | <MONITORING_PURPOSE_N> |

#### 必須ダッシュボード（サービス共通）

> 計測する **メトリクスの定義**は本ファイルの `### 監視 / ヘルス` が正本。本節は **可視化の束ね方** のみを定義する。

| ダッシュボード | 範囲 | 参照 |
| --- | --- | --- |
| <DASHBOARD_NAME_N> | <DASHBOARD_SCOPE_N> | <DASHBOARD_REFERENCE_N> |

#### 日常確認

| タイミング | 確認内容 | 担当 |
| --- | --- | --- |
| <ROUTINE_CHECK_CADENCE_N> | <ROUTINE_CHECK_SCOPE_N> | <ROUTINE_CHECK_OWNER_N> |

### 障害対応フロー（プロセス骨格）

> セキュリティインシデント（漏えい・脆弱性悪用疑い）は `security.md` の **脆弱性対応**（修正 SLA）も併用する。具体手順は本ファイルの **運用手順書の正本** を正とする。
> _分担_: 全フィーチャー共通の障害対応フローのみ本節に書く。**機能固有の復旧フロー**は `specs/design.md` に書く。運用手順書の実体は本ファイルの **運用手順書の正本**（`<RUNBOOK_REPOSITORY_LOCATION>`）に置き、フローの成果物としては生成しない。

#### 1. 検知

| 経路 | 検知方法 |
| --- | --- |
| <INCIDENT_DETECTION_ROUTE_N> | <INCIDENT_DETECTION_METHOD_N> |

#### 2. 初動（<INCIDENT_INITIAL_RESPONSE_SLA> 以内）

| 順 | 手順 |
| --- | --- |
| N | <INCIDENT_INITIAL_STEP_N> |

#### 3. 切り分け

> <INCIDENT_TRIAGE_APPROACH>

| 確認順 | 観点 | 参照 |
| --- | --- | --- |
| N | <TRIAGE_STEP_N_SCOPE> | <TRIAGE_STEP_N_REFERENCE> |

#### 4. 暫定復旧

| 手段 | 使う条件 | 注意 |
| --- | --- | --- |
| <MITIGATION_METHOD_N> | <MITIGATION_CONDITION_N> | <MITIGATION_CAUTION_N> |

#### 5. 恒久対応・再発防止

| # | 項目 | 内容 |
| --- | --- | --- |
| N | <POST_INCIDENT_ITEM_N> | <POST_INCIDENT_DETAIL_N> |

#### エスカレーション

| 段階 | 条件 | 連絡先 |
| --- | --- | --- |
| <ESCALATION_L1_LABEL> | <ESCALATION_L1_CONDITION> | <ESCALATION_L1_CONTACT> |
| <ESCALATION_L2_LABEL> | <ESCALATION_L2_CONDITION> | <ESCALATION_L2_CONTACT> |
| <ESCALATION_L3_LABEL> | <ESCALATION_L3_CONDITION> | <ESCALATION_L3_CONTACT> |
| <ESCALATION_VENDOR_LABEL> | <ESCALATION_VENDOR_CONDITION> | <ESCALATION_VENDOR_CONTACT> |

### 当番（オンコール）

> 移行運用スケジュール・保守タイムチャートは本テンプレートの外（MS Project / Gantt チャートツール / 課題管理ツール等）で管理する。URL が確定した場合は本セクションまたは `docs/` に参照リンクを記載すること。

| 項目 | 運用 |
| --- | --- |
| <ONCALL_ITEM_N> | <ONCALL_POLICY_N> |

### 変更管理

| 変更種別 | プロセス |
| --- | --- |
| <CHANGE_TYPE_PLANNED> | <PLANNED_CHANGE_PROCESS> |
| <CHANGE_TYPE_EMERGENCY> | <EMERGENCY_CHANGE_PROCESS> |
| <CHANGE_TYPE_CONFIG> | <CONFIG_CHANGE_PROCESS> |

### 運用手順書の正本（任意）

> 詳細手順は <RUNBOOK_REPOSITORY_LOCATION> に置き、ここは**索引のみ**。
> **運用手順書が未整備でも、本テンプレートの記入要件としては問題ない。** 配置先と運用ルール（下記 `<RUNBOOK_INDEX_GOVERNANCE>`）と、未決項目の **TBD + 整備期限・担当** が書かれていれば足りる。
> 索引行が未作成の手順は TBD のままよい。具体手順は整備後に追記するか、インシデント後に運用手順書として整備する。
> Confluence URL / TBD / リポジトリ内 `docs/` も可。
> <RUNBOOK_INDEX_GOVERNANCE>

| ドキュメント | 形式 | 正本の場所 | 更新担当 | 更新頻度 |
| --- | --- | --- | --- | --- |
| <RUNBOOK_INDEX_NAME_N> | <RUNBOOK_FORMAT_N> | <RUNBOOK_LOCATION_N> | <RUNBOOK_OWNER_N> | <RUNBOOK_UPDATE_CADENCE_N> |

## バックアップ / DR（サービス全体）

> _分担_: バックアップの **取得頻度・保持期間・暗号化・RPO / RTO・復元テスト・ジョブ失敗監視** は `database.md` の「バックアップ / リカバリ」を正とする（数値をここで二重に持たない）。
> 本節は **サービス全体の DR 運用**（対象資産の広がり・発動判断・演習）のみを定義する。

| 項目 | 方針 |
| --- | --- |
| <DR_ITEM_N> | <DR_POLICY_N> |

## 運用ツール参照（任意）

> 安定した URL・リンク。ここ or `docs/` どちらでも可。監視基盤・課題管理・Gantt チャート等の参照先を集約する。

| ツール | 用途 | 参照先（URL / TBD） |
| --- | --- | --- |
| <OPS_TOOL_NAME_N> | <OPS_TOOL_PURPOSE_N> | <OPS_TOOL_REFERENCE_N> |

---

*非機能要件・運用プロセスの共通標準を固定するファイルです。実装標準や数値は各ファイル（`database.md` / `api-standards.md` / `tech.md` / `security.md`）を正本として参照します。フィーチャー固有の非機能要件は `specs/<feature>/requirements.md` の NFR と `specs/design.md` に書いてください。*
