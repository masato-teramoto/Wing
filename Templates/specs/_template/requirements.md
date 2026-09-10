---
feature: {{FEATURE_NAME}}
status: draft
updated_at: {{ISO_8601_TIMESTAMP}}
---

# 要件定義書

> このファイルは **「何を作るか」「完了の判定基準は何か」** の正です。
> 自律エージェントが解釈ぶれを起こさないよう、受け入れ基準は **EARS 形式** で記述してください。
> このフィーチャーが承認 (`status: approved`) されてから `design.md` の作成に進みます。
>
> **テンプレート**: 山括弧で囲んだ大文字の項目は、プロジェクト確定時に実値へ置換する。

## Introduction（概要）

> このフィーチャーが何のために、誰のためにあるかを 2〜3 段落で書く。`背景` はなぜ今このフィーチャーが必要か、`対象ユーザー` は想定する利用者像、`期待する変化` はこのフィーチャーがあると何が変わるか。

<FEATURE_INTRODUCTION>

- **背景**: <FEATURE_BACKGROUND>
- **対象ユーザー**: <FEATURE_TARGET_USER>
- **期待する変化**: <FEATURE_EXPECTED_CHANGE>

> プロダクトレベルの目的・価値は steering の `product.md` を参照。ここではこのフィーチャー固有の文脈を書く。

## 業務フロー（任意）

> 業務システムなど人とシステムの責務境界を整理する必要がある場合のみ記述する。
> 承認フロー・今まで紙で行っていた作業をシステムが担う場合など、人の判断が介在するステップを明示したいときに有効。
> 不要なフィーチャーではこのセクションごと削除してよい。
> `対象業務` はこのフィーチャーが自動化・支援する業務名、`Before` は現在の手順（紙・口頭・別システムでの対応方法を含む）、`After` はシステム稼働後の手順、`人が介在するステップ` は承認・確認・例外処理などシステム外の人的操作。

- **対象業務**: <BUSINESS_FLOW_TARGET>
- **Before（現状の業務手順）**: <BUSINESS_FLOW_BEFORE>
- **After（システム導入後）**: <BUSINESS_FLOW_AFTER>
- **人が介在するステップ**: <BUSINESS_FLOW_HUMAN_STEPS>

> **記法**: Mermaid `sequenceDiagram`（スイムレーン形式）。人とシステムの責務境界が図で追える形にする。図が不要なら本スロットを残して直後に不要理由を書く。

<BUSINESS_FLOW_DIAGRAM>

> システム全体の主要ビジネスフローは `docs/architecture/system-overview.md §主要ビジネスフロー` を参照。

## Boundary Context（境界文脈）

> スコープの誤読が起こりやすい場合や、隣接するシステム / スペックに影響する場合は必ず記述する。
> `_N` の行を項目の数だけ増やす。`Out of Scope` は扱わない振る舞いに加えて理由または委譲先を書く。`Adjacent` は前提として動いている他フィーチャー / API / バッチ、およびこのフィーチャーが依頼している外部側の責務を書く。

- **In Scope（このフィーチャーで扱う）**:
  - <IN_SCOPE_BEHAVIOR_N>
- **Out of Scope（扱わない）**:
  - <OUT_OF_SCOPE_BEHAVIOR_N>
- **Adjacent（隣接システム / 隣接スペックへの期待）**:
  - <ADJACENT_EXPECTATION_N>

## Requirements（要件）

> 要件 ID は **数値**（`1`, `1.1`, `2`, `2.1` ...）のみ。`A`, `B` などのアルファベット ID は使わない。
> 各要件は **User Story** + **Acceptance Criteria（EARS 形式）** で構成する。
> **`### Requirement` のブロックを要件の数だけ複製する。** 要件領域名は、その要件がどの範囲を扱うかが分かる名前にする。

### Requirement <REQUIREMENT_NO>: <REQUIREMENT_AREA_NAME>

**User Story**: <USER_STORY_ROLE> として、<USER_STORY_GOAL> をしたい。なぜなら <USER_STORY_REASON> だから。

例: 「ログインユーザーとして、自分のプロフィールを編集したい。なぜなら表示名と通知設定を常に最新に保ちたいから。」

#### Acceptance Criteria（EARS 形式）

> 1 項目 = 1 基準。`_N` の行を基準の数だけ増やす。下の早見表のいずれかのパターンに当てはめて書く。

1. <ACCEPTANCE_CRITERION_N>

**EARS パターン早見表**:
- `When [event], the system shall [response]`（イベント駆動）
- `If [precondition], then the system shall [response]`（条件分岐）
- `While [state], the system shall [response]`（持続状態）
- `Where [feature included], the system shall [response]`（機能スコープ条件）
- `The system shall [response]`（普遍要件）

## Non-Functional Requirements（非機能要件）

> 当該フィーチャーで成立させるべき非機能要件のみ記述（steering で固定済みのものは引用に留める）。
> 共通 SLO・障害フロー・当番は `non-functional.md`、ログ・監視の実装標準は `non-functional.md`（観測部）を参照。
> `要件` は steering の該当ファイルへの準拠を示したうえで、このフィーチャー固有の値を書く（例: パフォーマンスなら `non-functional.md` 準拠 + p95 200ms、アクセシビリティなら WCAG 2.1 AA、プライバシーなら扱う PII と保持期間）。`計測 / 検証方法` は負荷試験・SLO ダッシュボード・スキャン・監査ログなど、その要件を確認する手段を書く。区分の行は増減してよい。

| 区分 | 要件 | 計測 / 検証方法 |
|---|---|---|
| パフォーマンス | <NFR_PERFORMANCE_REQUIREMENT> | <NFR_PERFORMANCE_VERIFICATION> |
| 可用性 | <NFR_AVAILABILITY_REQUIREMENT> | <NFR_AVAILABILITY_VERIFICATION> |
| 運用・監視 | <NFR_OPERATIONS_REQUIREMENT> | <NFR_OPERATIONS_VERIFICATION> |
| セキュリティ | <NFR_SECURITY_REQUIREMENT> | <NFR_SECURITY_VERIFICATION> |
| アクセシビリティ | <NFR_ACCESSIBILITY_REQUIREMENT> | <NFR_ACCESSIBILITY_VERIFICATION> |
| i18n / l10n | <NFR_I18N_REQUIREMENT> | <NFR_I18N_VERIFICATION> |
| プライバシー | <NFR_PRIVACY_REQUIREMENT> | <NFR_PRIVACY_VERIFICATION> |
| 監査 | <NFR_AUDIT_REQUIREMENT> | <NFR_AUDIT_VERIFICATION> |

## Out of Scope（明示的に対象外）

> Boundary Context だけで誤読を防ぎきれないとき、追加でここに書く。
> 1 項目 = 1 件。`_N` の行を件数だけ増やす。対象外にするものと、なぜ対象外か、どこで扱う予定かを書く。

- <EXPLICIT_OUT_OF_SCOPE_N>

## Dependencies / Assumptions（前提と依存）

> `前提` はこのフィーチャーが成立するために真でなければならない事項、`依存` は他フィーチャー / 既存システム / 外部 API / データ、`未確定事項` は調査・確認待ちのトピック（design に進む前に解消する）。

- **前提**: <FEATURE_ASSUMPTIONS>
- **依存**: <FEATURE_DEPENDENCIES>
- **未確定事項**: <FEATURE_OPEN_QUESTIONS>

---

_「何を作るか」を契約する正のドキュメントです。実装方法 / コンポーネント設計は `design.md`、タスクの分解は `tasks.md` に書いてください。_
