---
status: draft
updated_at: {{ISO_8601_TIMESTAMP}}
---

# システムアーキテクチャ

> このファイルは **論理構成・責務・境界、およびディレクトリ構成・import / path alias** を固定する steering ドキュメントです。
> 命名規則・コード規約・技術選定・検証手順は [`tech.md`](./tech.md) を参照してください。
> 機能ごとの責務分担とつなぎ方（画面・サービス・モジュールの担当範囲）は `design.md` の Components and Interfaces に書いてください。
>
> **テンプレート**: 山括弧で囲んだ大文字の項目は、プロジェクト確定時に実値へ置換する。

## アーキテクチャ概要

> 全体構成を 1 行で要約し、構成・配置モデル・通信パターンの 3 点を箇条書きで固定する。

<ARCHITECTURE_SUMMARY>

- **構成**: <ARCHITECTURE_COMPOSITION>
- **配置モデル**: <DEPLOYMENT_MODEL>
- **通信パターン**: <COMMUNICATION_PATTERN>

## 配置原則

> _分担_: プロジェクト全体の配置パターンのみ本節に書く。**フィーチャー固有の追加ディレクトリ**は `design.md` の File Structure Plan に書く。

- **原則**: <PLACEMENT_PRINCIPLE>
- **採用理由**: <PLACEMENT_RATIONALE>
- **レイヤーとディレクトリ構成の対応**: <LAYER_DIRECTORY_MAPPING>（詳細は本ファイルの `## ディレクトリ構成`）
- **フィーチャー固有の追加ディレクトリ**: 本ファイルに増やさず、`design.md` の File Structure Plan に書く

## レイヤーと依存ルール

> 許可・禁止・外部システムの 3 点を明文化する。具体的な依存方向は矢印（`→`）で示す。

- **許可する依存方向**: <ALLOWED_DEPENDENCY_DIRECTION>
- **禁止**: <PROHIBITED_DEPENDENCY>
- **外部システム**: <EXTERNAL_SYSTEM_RULE>

## 各システムコンポーネントの役割

> ここでの **コンポーネント = System component**（FE / BE / 外部連携 / 共通基盤など、**アーキテクチャ上の大きな塊**）を指します。
> **UI 部品**（個々のボタン・フォーム・画面要素など）や **ドメイン内のクラス単位** は対象外です。
> フィーチャー固有の境界（画面・サービス・モジュールなど）は `design.md` の Components and Interfaces に書いてください。
> 命名規則の「ファイル（コンポーネント）」は UI ファイル用の別概念です（`tech.md` の `## 命名規則` 参照）。
>
> 各コンポーネントは **責務 / しないこと / 配置 / 境界** の 4 点で書く。プロジェクトに無いコンポーネントは削除し、追加が必要なものは同じ 4 点で追記する。

### フロントエンド（FE）

- **責務**: <COMPONENT_FE_RESPONSIBILITY>
- **しないこと**: <COMPONENT_FE_NON_RESPONSIBILITY>
- **配置**: <COMPONENT_FE_LOCATION>
- **境界**: <COMPONENT_FE_BOUNDARY>

### バックエンド（BE）

- **責務**: <COMPONENT_BE_RESPONSIBILITY>
- **しないこと**: <COMPONENT_BE_NON_RESPONSIBILITY>
- **配置**: <COMPONENT_BE_LOCATION>
- **境界**: <COMPONENT_BE_BOUNDARY>

### 外部 API / 外部システム

- **責務**: <COMPONENT_EXTERNAL_RESPONSIBILITY>
- **しないこと**: <COMPONENT_EXTERNAL_NON_RESPONSIBILITY>
- **配置**: <COMPONENT_EXTERNAL_LOCATION>
- **境界**: <COMPONENT_EXTERNAL_BOUNDARY>

### 共通基盤（shared）

- **責務**: <COMPONENT_SHARED_RESPONSIBILITY>
- **しないこと**: <COMPONENT_SHARED_NON_RESPONSIBILITY>
- **配置**: <COMPONENT_SHARED_LOCATION>

### <COMPONENT_NAME_N>

- **責務**: <COMPONENT_RESPONSIBILITY_N>
- **しないこと**: <COMPONENT_NON_RESPONSIBILITY_N>
- **配置**: <COMPONENT_LOCATION_N>
- **境界**: <COMPONENT_BOUNDARY_N>

## フィーチャー設計との分担

| 粒度 | 書く場所 |
|---|---|
| プロジェクト全体の論理構成・責務 | 本ファイル（`architecture.md`） |
| フィーチャー固有の画面・API・モジュール境界 | `design.md` の Components and Interfaces |
| フィーチャー固有の追加ディレクトリ | `design.md` の File Structure Plan |

## ディレクトリ構成

> **Spec / Steering の配置はフローが固定する。** プロジェクトルート直下に `steering/` / `specs/` / `docs/` を置き、フローの管理ファイルは `.aidd/` に置く。**この 4 つは書き換えない。** steering 内の相互参照は、ルート直下からの相対パス（`steering/`、`specs/<feature>/`）で統一してください。

```
<PROJECT_ROOT>/
├── .aidd/                       # フロー管理（RFP / 要求一覧 / feature-list / 進捗 / ゲート記録）
├── steering/                    # 横断方針 7ファイル（本ファイルを含む）
├── specs/                       # フィーチャーごとの requirements / design / tasks
├── docs/                        # 全体設計ドキュメント + README 以外のドキュメント
│   ├── code-design.md           # 業務コード・区分値・採番ルール
│   ├── architecture/            # data-model.md / system-overview.md
│   └── runbooks/                # 運用手順（任意。正本が Excel の場合は non-functional.md に URL のみ）
├── src/
│   ├── <DOMAIN_A>/              # ドメイン A の責務（配置原則は本ファイルの配置原則）
│   │   ├── controller.<SRC_EXT>      # 入口（HTTP / CLI）
│   │   ├── service.<SRC_EXT>         # ビジネスロジック
│   │   ├── repository.<SRC_EXT>      # 永続化アクセス
│   │   └── types.<SRC_EXT>           # ドメイン型
│   ├── <DOMAIN_B>/              # ドメイン B（A と同じパターン）
│   └── shared/
│       ├── lib/                 # 汎用ユーティリティ
│       └── middleware/          # 横断関心事
├── tests/                       # E2E / Integration（コロケーションでない場合）
├── public/ または static/        # 静的アセット
└── scripts/                     # 開発・運用スクリプト
```

> `src/` 以下はパターン例。実プロジェクトに合わせて書き換えてください（`.aidd/` / `steering/` / `specs/` / `docs/` の 4 つは書き換えない）。**繰り返し構造はパターンだけ書く** ことで、新規ディレクトリ追加時のメンテを減らします。
> レイヤーと配置の対応（controller / service / repository など）は本ファイルの `## 配置原則` に従ってください。

## import / path alias

| alias | 解決先 |
|---|---|
| <PATH_ALIAS_N> | <PATH_ALIAS_TARGET_N> |

- **原則**: <IMPORT_PRINCIPLE>
- **禁止**: <IMPORT_PROHIBITED>

## 全体図のルール

> プロジェクト全体の地図（システム全体像・主要ビジネスフロー・外部連携・ドメイン境界）の **図の種別・ツール・Mermaid 利用方針** を定義する。
> **図の実体（Mermaid 図・記述・プレースホルダー）は `docs/architecture/system-overview.md` を参照する。** 本節には図の方針のみを書き、図そのものは置かない。
> 図は **Mermaid のみ**（画像を貼らない）。フィーチャー個別のフローは `specs/<feature>/design.md` の System Flows に書く。
> _分担_: コンポーネント横断の代表フローのみ全体図に載せる。サービス内部の詳細シーケンス / ステート図は `specs/<feature>/design.md` に書く。

### 記入時の連携（必須）

> 全体図（`docs/architecture/system-overview.md`）は単独では書けない。他 Steering を **正本として参照** し、値を二重定義しない。

| 全体図で参照する内容 | 正本 |
| --- | --- |
| コンポーネント・レイヤー・ドメイン境界 | 本ファイル（`architecture.md`） |
| 採用技術名（バージョン除く） | `tech.md` |
| 主要ユースケースの選定 | `product.md` |
| 認証・外部 ID 連携 | `security.md` |
| 失敗時方針の詳細（リトライ・遮断等） | `non-functional.md`（全体図は方針名のみ） |
| 障害切り分けで全体図を参照 | `non-functional.md` の障害対応フローから参照される |

### 図の種別と粒度

| 図 | 用途 | ノード粒度 | 実体の場所 |
| --- | --- | --- | --- |
| システム全体像（flowchart） | 主要コンポーネントの接続を 1 枚で示す | コンポーネント単位（クラス・メソッド単位は `design.md`） | `docs/architecture/system-overview.md` |
| 主要ビジネスフロー（sequenceDiagram） | 代表ユースケース 3〜5 個・各 7〜10 ステップ以内 | コンポーネント間のやりとり | `docs/architecture/system-overview.md` |
| 外部連携の俯瞰（任意） | 外部連携が 3 個以上、または失敗時方針が連携先ごとに異なる場合 | 連携先単位 | `docs/architecture/system-overview.md` |
| ドメイン境界の地図（任意） | 複数ドメイン（Bounded Context）がある場合 | ドメイン単位 | `docs/architecture/system-overview.md` |

---

*論理構成・責務境界・ディレクトリ構成を固定するためのファイルです。製品名・版・コマンド・命名規則・コード規約は [`tech.md`](./tech.md) に書いてください。*
