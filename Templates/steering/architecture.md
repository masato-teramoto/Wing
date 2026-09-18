---
status: draft
updated_at: {{ISO_8601_TIMESTAMP_JST}}
---

# システムアーキテクチャ

> このファイルは、**プロジェクト全体の論理構成・責務・境界と、ディレクトリ構成・import の別名** を確定させる文書である。\
> _分担_: 製品名とバージョンは `tech.md` の `## コアテクノロジ`、命名規則とコード規約は同ファイルの `## 命名規則` と `## コード規約`、検証手順は同ファイルの `## 共通コマンド`。機能ごとの責務分担とつなぎ方は `specs/<feature>/design.md` の `## コンポーネントとインターフェース（Components and Interfaces）`。

> _書き方_: プロジェクト全体に共通する構成だけを書く。特定の機能にしか出てこない要素は書かない。

## アーキテクチャ概要

> システム全体がどういう形をしているかを確定させる節。

> _書き方_: 概要には、全体の形を短く言い切る（単一のアプリケーションか、複数に分かれているか、など）。構成には、どんな塊に分かれているかを書く。配置モデルには、それぞれがどこで動くかを書く。通信パターンには、塊どうしがどうやり取りするかを書く。

<ARCHITECTURE_SUMMARY>

- **構成**: <ARCHITECTURE_COMPOSITION>
- **配置モデル**: <ARCHITECTURE_DEPLOYMENT_MODEL>
- **通信パターン**: <ARCHITECTURE_COMMUNICATION_PATTERN>

## 配置原則

> ファイルをどういう単位で置くかの原則を確定させる節。\
> _分担_: 実際のディレクトリの並びは `## ディレクトリ構成`。フィーチャー固有の追加ディレクトリはこのファイルに増やさず、`specs/<feature>/design.md` の `## ファイル配置計画（File Structure Plan）` に書く。

> _書き方_: 原則には、何を単位としてまとめるかを書く（機能ごとにまとめるか、層ごとにまとめるか、など）。採用理由には、他の置き方ではなくこれを選んだ決め手を書く。

- **原則**: <PLACEMENT_PRINCIPLE>
- **採用理由**: <PLACEMENT_RATIONALE>
- **レイヤーとディレクトリ構成の対応**: <LAYER_DIRECTORY_MAPPING>

## レイヤーと依存ルール

> どの層がどの層を呼んでよいかを確定させる節。\
> _分担_: インポートの書き方と別名の設定は `## インポート / パスエイリアス（import / path alias）`。ここには呼んでよい向きだけを書く。

> _書き方_: 依存の向きは矢印（`→`）で示す。禁止には、逆向きの呼び出しや層を飛び越えた呼び出しなど、避けるものを書く。外部システムには、外部との通信をどの層に閉じ込めるかを書く。

- **許可する依存方向**: <ALLOWED_DEPENDENCY_DIRECTION>
- **禁止**: <PROHIBITED_DEPENDENCY>
- **外部システム**: <EXTERNAL_SYSTEM_RULE>

## 各システムコンポーネントの役割

> システムを構成する大きな塊（フロントエンド、バックエンド、外部連携、共通基盤など）ごとに、その担当範囲を確定させる節。ここでいうコンポーネントは**アーキテクチャ上の塊**を指し、個々のボタンやフォームなどの画面部品や、ドメイン内のクラス単位は含まない。\
> _分担_: フィーチャー固有の境界（画面・サービス・モジュール）は `specs/<feature>/design.md` の `## コンポーネントとインターフェース（Components and Interfaces）`。命名規則における「ファイル（コンポーネント）」は画面部品のファイルを指す別の概念であり、`tech.md` の `## 命名規則` で扱う。

> _書き方_: 各コンポーネントを **責務 / しないこと / 配置 / 境界** の 4 点で書く。「しないこと」には、そのコンポーネントに紛れ込みやすい役割を書く。

### フロントエンド（FE）

> 利用者が直接触れる部分の担当範囲を確定させる節。

> _書き方_: 「しないこと」には、業務ルールの判定や権限の最終確認など、後ろ側に任せるものを書く。

- **責務**: <COMPONENT_FE_RESPONSIBILITY>
- **しないこと**: <COMPONENT_FE_NON_RESPONSIBILITY>
- **配置**: <COMPONENT_FE_LOCATION>
- **境界**: <COMPONENT_FE_BOUNDARY>

### バックエンド（BE）

> 要求を受け取り、業務ロジックを実行する部分の担当範囲を確定させる節。

> _書き方_: 「しないこと」には、画面の見た目に関する判断など、前側に任せるものを書く。

- **責務**: <COMPONENT_BE_RESPONSIBILITY>
- **しないこと**: <COMPONENT_BE_NON_RESPONSIBILITY>
- **配置**: <COMPONENT_BE_LOCATION>
- **境界**: <COMPONENT_BE_BOUNDARY>

### 外部 API / 外部システム

> 自分たちで作らない、外部の仕組みとの関わり方を確定させる節。\
> _分担_: 失敗したときの再実行や遮断の方針は `non-functional.md` の `### リトライ`。ここには担当範囲だけを書く。

> _書き方_: 「しないこと」には、外部に期待してはいけないこと（自分たちの業務ルールの判定を任せる、など）を書く。境界には、外部とのやり取りをどこに閉じ込めるかを書く。

- **責務**: <COMPONENT_EXTERNAL_RESPONSIBILITY>
- **しないこと**: <COMPONENT_EXTERNAL_NON_RESPONSIBILITY>
- **配置**: <COMPONENT_EXTERNAL_LOCATION>
- **境界**: <COMPONENT_EXTERNAL_BOUNDARY>

### 共通基盤（shared）

> 複数の場所から使われる共通の部品の担当範囲を確定させる節。

> _書き方_: 「しないこと」には、特定の業務に依存する処理など、ここへ置いてはいけないものを書く。何でも入る置き場にならないように、入れてよい条件を明確にする。

- **責務**: <COMPONENT_SHARED_RESPONSIBILITY>
- **しないこと**: <COMPONENT_SHARED_NON_RESPONSIBILITY>
- **配置**: <COMPONENT_SHARED_LOCATION>
- **境界**: <COMPONENT_SHARED_BOUNDARY>

### <COMPONENT_NAME_N>

> 上の 4 つに当てはまらないコンポーネントを書く節。

> _書き方_: バッチ処理基盤、管理画面、常駐サービスなど、プロジェクト固有の塊をここに書く。上の 4 つと同じ 4 点で書く。

- **責務**: <COMPONENT_RESPONSIBILITY_N>
- **しないこと**: <COMPONENT_NON_RESPONSIBILITY_N>
- **配置**: <COMPONENT_LOCATION_N>
- **境界**: <COMPONENT_BOUNDARY_N>

## フィーチャー設計との分担

> どの粒度の話をどのファイルに書くかを確定させる節。

> _書き方_: この表はプロジェクトによらず同じ内容になるため、原則そのまま使う。プロジェクト固有の書き分けが増えた場合だけ行を足す。

| 粒度 | 書く場所 |
|---|---|
| プロジェクト全体の論理構成・責務 | 本ファイル（`architecture.md`） |
| フィーチャー固有の画面・API・モジュール境界 | `specs/<feature>/design.md` の `## コンポーネントとインターフェース（Components and Interfaces）` |
| フィーチャー固有の追加ディレクトリ | `specs/<feature>/design.md` の `## ファイル配置計画（File Structure Plan）` |

## ディレクトリ構成

> ディレクトリの並びを確定させる節。Spec ルートとは `steering/`・`specs/`・`docs/` の親ディレクトリであり、その配置先（リポジトリ直下、`docs/spec/`、`spec/` など）はプロジェクトで決める。\
> _分担_: 何を単位としてまとめるかの考え方は本ファイルの `## 配置原則`。フィーチャー固有の追加ディレクトリは `specs/<feature>/design.md` の `## ファイル配置計画（File Structure Plan）`。

> _書き方_: Steering 内の相互参照はファイル名だけで書き、Specs / Docs からの参照は `steering/`・`docs/` を付けて書く。`src/` 以下は実プロジェクトのルートに合わせた形を書く。同じ形が並ぶところはパターンを 1 つだけ書き、実際の数だけ並べない。レイヤーと配置の対応（controller / service / repository など）は `## 配置原則` と揃える。

```
<DIR_PROJECT_ROOT>/
├── <DIR_SPEC_ROOT>/                 # steering / specs / docs の親（パスはプロジェクトで決める）
│   ├── steering/
│   │   ├── product.md           # なぜ作るか
│   │   ├── tech.md              # 技術スタック・命名規則・コード規約・テスト方針
│   │   ├── architecture.md      # 論理構成・責務・境界・ディレクトリ構成（本ファイル）
│   │   ├── database.md
│   │   ├── api-standards.md
│   │   ├── security.md
│   │   └── non-functional.md
│   ├── specs/
│   │   └── _template/           # コピー先は specs/<feature>/
│   └── docs/
│       ├── architecture/
│       │   ├── system-overview.md
│       │   └── data-model.md
│       └── code-design.md
├── src/
│   ├── <DIR_DOMAIN_N>/          # ドメインごとの責務（本ファイルの `## 配置原則` に従う）
│   │   ├── controller.<DIR_SRC_EXT>      # 入口（HTTP / CLI）
│   │   ├── service.<DIR_SRC_EXT>         # ビジネスロジック
│   │   ├── repository.<DIR_SRC_EXT>      # 永続化アクセス
│   │   └── types.<DIR_SRC_EXT>           # ドメイン型
│   └── shared/
│       ├── lib/                 # 汎用ユーティリティ
│       └── middleware/          # 複数の機能にまたがる共通処理
├── tests/                       # 通しテスト（E2E）・結合テスト（対象と同じ場所に置かない場合）
├── public/ または static/        # 静的アセット
└── scripts/                     # 開発・運用スクリプト
```

## インポート / パスエイリアス（import / path alias）

> ファイルを読み込むときの書き方と、長いパスに付ける別名を確定させる節。\
> _分担_: 別名を実際に効かせる設定はリポジトリの設定ファイル。ここには対応関係だけを書く。

> _書き方_: 原則には、相対パスと別名のどちらを使うかの判断を書く。禁止には、階層をさかのぼり続ける書き方や、層を越えた直接の読み込みなど、避けるものを書く。

| パスエイリアス | 解決先 |
|---|---|
| <PATH_ALIAS_N> | <PATH_ALIAS_TARGET_N> |

- **原則**: <IMPORT_PRINCIPLE>
- **禁止**: <IMPORT_PROHIBITED>

## 全体図のルール

> プロジェクト全体の地図（全体像・主要な業務の流れ・外部連携・ドメインの境界）について、**どういう図を描くか**を確定させる節。図そのものはここに置かない。\
> _分担_: 図の実体は `docs/architecture/system-overview.md`。フィーチャー個別の流れと、サービス内部の細かい順序や状態の図は `specs/<feature>/design.md` の `## 処理フロー（System Flows）`。

### 記入時の連携

> 全体図を書くときに、要素ごとにどのファイルを正本として見るかを確定させる節。\
> _分担_: 図の実体は `docs/architecture/system-overview.md`。ここには正本の対応だけを置き、値そのものは書かない。

> _書き方_: この表はプロジェクトによらず同じ内容になるため、原則そのまま使う。正本の欄には、ファイル名と見る節を書く。

| 全体図で書く内容 | 正本 |
| --- | --- |
| コンポーネント・レイヤー・ドメイン境界 | 本ファイル（`architecture.md`） |
| 採用技術名（バージョンを除く） | `tech.md` の `## コアテクノロジ` |
| 主要ユースケースの選び方 | `product.md` の `## 主要ユースケース` |
| 認証・外部 ID 連携 | `security.md` の `## 認証・認可` |
| 失敗したときの方針（再実行・遮断など） | `non-functional.md` の `### リトライ`（全体図には方針名だけを書く） |
| 障害の切り分けで全体図を見る流れ | `non-functional.md` の `### 障害対応フロー（プロセス骨格）` |

### 図の種別と粒度

> 描く図の種類ごとに、何のために描くか、どこまで細かく描くかを確定させる節。\
> _分担_: 図の実体は `docs/architecture/system-overview.md`。フィーチャー個別の流れは `specs/<feature>/design.md` の `## 処理フロー（System Flows）`。

> _書き方_: 用途には、その図を見た人が何を判断できるようになるかを書く。ノードの細かさには、1 つの箱が何を表すかを書く。この表はプロジェクトによらず同じ内容になるため、原則そのまま使う。

| 図 | 用途 | ノードの細かさ | 実体の場所 |
| --- | --- | --- | --- |
| システム全体像（flowchart） | 主要コンポーネントのつながりを 1 枚で見せる | コンポーネント単位（クラス・メソッド単位は `specs/<feature>/design.md` の `## コンポーネントとインターフェース（Components and Interfaces）`） | `docs/architecture/system-overview.md` |
| 主要ビジネスフロー（sequenceDiagram） | 代表的な使われ方を、関係するコンポーネントの順に追えるようにする | コンポーネント間のやりとり | `docs/architecture/system-overview.md` |
| 外部連携の俯瞰 | 外部との接点と、失敗したときの方針の違いを一覧で見せる | 連携先単位 | `docs/architecture/system-overview.md` |
| ドメイン境界の地図 | ドメインの境界と、境界をまたぐやりとりを見せる | ドメイン単位 | `docs/architecture/system-overview.md` |

---

_論理構成・責務境界・ディレクトリ構成を固定する文書。_
