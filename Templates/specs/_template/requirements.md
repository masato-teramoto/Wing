---
feature: {{FEATURE_NAME}}
status: draft
updated_at: {{ISO_8601_TIMESTAMP_JST}}
---

# 要件定義書

> このファイルは **「何を作るか」「完了をどう判定するか」** を確定させる文書である。\
> _分担_: `status: approved` になるまで `design.md` に進まない。`approved` は人間が付ける（エージェントは付けない）。

> _書き方_: 確定した要件だけを書き、作成の手順やレビューの記録は残さない。

## 概要（Introduction）

> このフィーチャーが何のために、誰のためにあるかを示す節。\
> _分担_: プロダクト全体の目的は `steering/product.md` の `## 開発物の概要・背景`、価値は同ファイルの `## 提供価値`。

> _書き方_: このフィーチャー固有の事情だけを書き、経緯や検討過程は書かない。

- **背景**: <REQ_INTRO_BACKGROUND>
- **対象ユーザー**: <REQ_INTRO_TARGET_USER>
- **期待する変化**: <REQ_INTRO_EXPECTED_CHANGE>

## 業務フロー

> 人とシステムの担当を整理する節。人の判断が入る手順を明示したいときに書く。\
> _分担_: システム全体の主要ビジネスフローは `docs/architecture/system-overview.md` の `## 主要ビジネスフロー`。

> _書き方_: 承認フローや、紙・口頭で行っていた作業をシステムが担う場合が該当する。対象業務には業務名だけを書く。手順と介在ステップは 1 ステップ 1 行で列挙する。ステップが多い場合や担当が複数にまたがる場合は Mermaid の sequenceDiagram（担当ごとにレーンを分けるスイムレーン形式）を併用する。

- **対象業務**: <REQ_BIZFLOW_TARGET>
- **現状の業務手順（Before）**:
  - <REQ_BIZFLOW_BEFORE_N>
- **システム導入後（After）**:
  - <REQ_BIZFLOW_AFTER_N>
- **人が介在するステップ**:
  - <REQ_BIZFLOW_HUMAN_STEP_N>

## スコープの境界（Boundary Context）

> このフィーチャーで**何を作り、何を作らないか**を確定させる節。スコープの誤読が起きやすい場合や、隣接するシステム・スペックに影響する場合は必ず書く。\
> _分担_: 扱わない理由と引き継ぎ先は `## 対象外`。無いと成立しない依存は `## 前提と依存（Dependencies / Assumptions）`。実装として何を所有するかは `design.md` の `## 責務境界（Boundary Commitments）`。ここには利用者から見た機能の範囲だけを書き、理由や実装の話は書かない。

> _書き方_: **確定した境界だけ**を書き、検討中のものは書かない。1 項目 1 行で列挙する。

- **扱う範囲（In Scope）**:
  - <REQ_SCOPE_IN_N>
- **扱わない範囲（Out of Scope）**:
  - <REQ_SCOPE_OUT_N>
- **隣接する仕組みへの期待（Adjacent）**:
  - <REQ_SCOPE_ADJACENT_N>

## 対象外

> このフィーチャーで扱わないことを、理由と引き継ぎ先つきで示す節。\
> _分担_: 境界そのものの宣言は `## スコープの境界（Boundary Context）`。一言で境界が伝わるものはあちらに置き、理由や引き継ぎ先の説明が要るものだけをここに書く。**同じ内容を両方に書かない。**

> _書き方_: 1 項目に「扱わないこと / 理由 / どこで扱う予定か」をまとめて書く。

- <REQ_OUTSCOPE_ITEM_N>

## 前提と依存（Dependencies / Assumptions）

> このフィーチャーが成立するために、外部で満たされている必要があることを書く節。\
> _分担_: 「相手の担当だと宣言したいもの」は `## スコープの境界（Boundary Context）` の 隣接する仕組みへの期待（Adjacent）。ここには「**無いとこのフィーチャーが動かないもの**」を書く。実装が使ってよい範囲と守る制約は `design.md` の `### 依存してよい対象（Allowed Dependencies）`。

> _書き方_: 前提は、崩れると設計が成り立たなくなるものだけを書く（「たぶんそうだろう」は書かない）。依存は、フィーチャー名・システム名・API 名など後から特定できる固有名で書く。未確定事項は、誰が確認するかを添えて書き、`design.md` に進む前に解消する。

- **前提**:
  - <REQ_ASSUMPTION_N>
- **依存**:
  - <REQ_DEPENDENCY_N>
- **未確定事項**:
  - <REQ_OPEN_ISSUE_N>

## 要件（Requirements）

> このフィーチャーの要件を列挙する節。要件ごとに利用者ストーリーと受け入れ基準を対で書く。

> _書き方_: 要件ごとに整数の番号を振り、受け入れ基準にはその番号に連番をつないだ ID（要件 1 なら `1.1`, `1.2`, `…`、要件 2 なら `2.1`, `2.2`）を付ける。この **受け入れ基準ID** は `design.md`・`tasks.md` と外部の対応表から参照されるので、一度付けたら変えない。要件は必要な数だけ `### 要件 2`, `### 要件 3` と同じ形で追加する。\
> 利用者ストーリーは「〜として、〜をしたい。なぜなら〜だから。」の 1 文にまとめる（例: 「ログインユーザーとして、自分のプロフィールを編集したい。なぜなら表示名と通知設定を常に最新に保ちたいから。」）。監査やログなどの裏方の要件でも省略しない。\
> 受け入れ基準は 1 行 1 基準で、必要な数だけ行を足す。行を続ける場合は行末に `\` を置く。義務は **「しなければならない」**、禁止は **「してはならない」** と書く。単に「する／しない」と書くと事実の説明に読めてしまい、義務として伝わらないため使わない。\
> 番号付きの受け入れ基準には、外から見て YES / NO を判定できる応答・拒否・状態変化だけを書く。境界やスコープの説明文に番号を付けない。上位の決定（要件・steering）が「〜のみ可／〜以外は不可」と定めている場合は、拒否される場合だけでなく、許可される場合も対にして書く。
>
> **EARS 意味パターン早見表** — 中列の日本語の表記を使う。右列は原文との対照。
>
> | 意味 | 日本語の表記（ja） | 英語の表記（en） |
> |---|---|---|
> | イベント駆動（Event-driven） | `[イベント] のとき、システムは [応答] しなければならない` | `When [event], the system shall [response]` |
> | 条件駆動（Conditional） | `[条件] の場合、システムは [応答] しなければならない` | `If [precondition], then the system shall [response]` |
> | 望ましくない条件への応答（Unwanted behavior） | `[望ましくない条件] の場合、システムは [応答] しなければならない` | `If [unwanted condition], then the system shall [response]` |
> | 持続状態（State-driven） | `[状態] のあいだ、システムは [応答] しなければならない` | `While [state], the system shall [response]` |
> | 機能スコープ（Optional feature） | `[領域] において、システムは [応答] しなければならない` | `Where [feature included], the system shall [response]` |
> | 普遍要件（Ubiquitous） | `システムは [応答] しなければならない` | `The system shall [response]` |
> | 禁止（shall not） | `[条件] の場合、システムは [行為] してはならない` | `If [precondition], the system shall not [action]` |

### 要件 1: <REQ_AREA_NAME>

**利用者ストーリー（User Story）**: <REQ_USERSTORY_ROLE> として、<REQ_USERSTORY_WANT> をしたい。なぜなら <REQ_USERSTORY_WHY> だから。

#### 受け入れ基準（Acceptance Criteria）

1.1. <REQ_AC_TRIGGER_N> のとき、システムは <REQ_AC_RESPONSE_N> しなければならない\
1.2. <REQ_AC_CONDITION_N> の場合、システムは <REQ_AC_FORBIDDEN_ACTION_N> してはならない

## 非機能要件（Non-Functional Requirements）

> このフィーチャーで満たすべき非機能要件を確定させる節。**目標値**（例: このフィーチャーで追加する p95）はこの表を正式版とする。\
> _分担_: 共通の SLO（サービスレベル目標）は `steering/non-functional.md` の `## 可用性・性能`、障害対応フローと運用当番は同ファイルの `## 運用・障害対応`、ログ・監視の実装標準は同ファイルの `## 信頼性・観測性`。実現手段は `design.md` の `### 性能とスケーラビリティ（Performance & Scalability）` に書く。

> _書き方_: steering で既に決まっているものは参照だけにして、ここで書き直さない。各行は「steering 準拠 + このフィーチャー固有の値」の形で書く（例: パフォーマンス「`steering/non-functional.md` 準拠 + p95（応答時間の 95 パーセンタイル）200ms」、アクセシビリティ「WCAG 2.1 AA」、プライバシー「扱う個人情報（PII）と保持期間」）。検証方法の列には、その要件を確かめる手段を書く（例: 負荷試験、本番メトリクス、SLO ダッシュボード、プライバシー影響評価（DPIA）、監査ログ）。

| 区分 | 要件 | 計測 / 検証方法 |
|---|---|---|
| パフォーマンス | <REQ_NFR_PERFORMANCE> | <REQ_NFR_PERFORMANCE_VERIFY> |
| 可用性 | <REQ_NFR_AVAILABILITY> | <REQ_NFR_AVAILABILITY_VERIFY> |
| 運用・監視 | <REQ_NFR_OPERATION> | <REQ_NFR_OPERATION_VERIFY> |
| セキュリティ | <REQ_NFR_SECURITY> | <REQ_NFR_SECURITY_VERIFY> |
| アクセシビリティ | <REQ_NFR_ACCESSIBILITY> | <REQ_NFR_ACCESSIBILITY_VERIFY> |
| 多言語・地域対応（i18n / l10n） | <REQ_NFR_I18N> | <REQ_NFR_I18N_VERIFY> |
| プライバシー | <REQ_NFR_PRIVACY> | <REQ_NFR_PRIVACY_VERIFY> |
| 監査 | <REQ_NFR_AUDIT> | <REQ_NFR_AUDIT_VERIFY> |

---

_「何を作るか」を確定させる文書。_
