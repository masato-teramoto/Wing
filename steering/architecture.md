---
status: approved
updated_at: 2026-10-05T18:25:03+09:00
---

# システムアーキテクチャ

> このファイルは、**プロジェクト全体の論理構成・責務・境界と、ディレクトリ構成・import の別名** を確定させる文書である。\
> _分担_: 製品名とバージョンは `tech.md` の `## コアテクノロジ`、命名規則とコード規約は同ファイルの `## 命名規則` と `## コード規約`、検証手順は同ファイルの `## 共通コマンド`。機能ごとの責務分担とつなぎ方は `specs/<feature>/design.md` の `## コンポーネントとインターフェース（Components and Interfaces）`。

> _書き方_: プロジェクト全体に共通する構成だけを書く。特定の機能にしか出てこない要素は書かない。

> _出典の表記_: 「回答 N」「回答 Q-STR-xxx」とパスの意味は `tech.md` の冒頭と同じ。

## アーキテクチャ概要

> システム全体がどういう形をしているかを確定させる節。

> _書き方_: 概要には、全体の形を短く言い切る（単一のアプリケーションか、複数に分かれているか、など）。構成には、どんな塊に分かれているかを書く。配置モデルには、それぞれがどこで動くかを書く。通信パターンには、塊どうしがどうやり取りするかを書く。

WiNG は、2 つの Web アプリケーション（wing と WTX）と常駐のバッチ（WTX_Batch）が 1 つの Oracle データベースを共有する構成である。本プロジェクトの新しい画面は wing に、取込バッチは WTX_Batch に追加する（回答 1・回答 2）。

- **構成**: wing（Spring MVC。ログインと WTG 画面を持つ）、WTX（GreenEARTH Framework と JAVA-KIT。他サブシステムの画面を持つ）、WTX_Batch（batch-engine の常駐バッチ）、WTX_Common（WTX と WTX_Batch が使う共通部品）、Oracle データベース
- **配置モデル**: wing と WTX は war として Tomcat に配備し、前段に Apache HTTP Server を置く。帳票の PDF 変換に使う OpenOffice は、Tomcat と同じアプリケーションサーバーに常駐させ、localhost の 8100 番ポートで待ち受ける（版は本番サーバーに導入済みのものに従う。Phase 2 ゲート 2 回目 指摘14 の修正指示）。Web と DB のサーバーは Oracle Linux（WTZ 共通「非機能要求」。回答 6）。バッチはキューごとに常駐するエンジン `WTBatchEngineAdmin` として動く（`WTX_Batch/sh/batch_start.sh`）
- **通信パターン**: ブラウザと wing は HTTP のフォーム送信（一部は画面内の JSON 取得。`wing/src/main/java/jp/co/kccs/wt/function/wte/wte020/controller/Pwteo020Dialog2Controller.java`）。wing と WTX は DB のセッション表 `ZSESSION` を共有し、メニューから画面をリダイレクトして行き来する（`wing/src/main/java/jp/co/kccs/wt/common/service/RedirectService.java`）。画面からバッチへの依頼は、画面が DB のタスクリスト（`STASKLIST` 系）にタスクを登録し、常駐エンジンが取り出して実行する（`wing/src/main/java/jp/co/kccs/wt/function/wtg/wtg040/controller/Pwtgo040Controller.java`）

## 配置原則

> ファイルをどういう単位で置くかの原則を確定させる節。\
> _分担_: 実際のディレクトリの並びは `## ディレクトリ構成`。フィーチャー固有の追加ディレクトリはこのファイルに増やさず、`specs/<feature>/design.md` の `## ファイル配置計画（File Structure Plan）` に書く。

> _書き方_: 原則には、何を単位としてまとめるかを書く（機能ごとにまとめるか、層ごとにまとめるか、など）。採用理由には、他の置き方ではなくこれを選んだ決め手を書く。

- **原則**: サブシステム → 機能ID の単位でまとめ、その中を層で分ける。複数機能で使う部品は `common` に置く
- **採用理由**: 既存 wing・WTX_Batch の置き方であり、既存の画面ID・PGID 体系と対応させる（REQ-004・REQ-045）
- **レイヤーとディレクトリ構成の対応**: wing は `function/<サブシステム>/<機能ID>/` の下に `controller`（要求の受付）・`service`（業務ロジック）・`mapper`（DB アクセス。SQL は `src/main/resources` の同じパスの XML）・`form`（画面の入力）・`bean`（画面の表示・検索条件）。バッチは `wt/<サブシステム>/<機能ID>/` に `PWTGBxxxJob`（処理本体）・`PWTGBxxxConst`（定数・VE の ID）・`PWTGBxxxCheckUtils`（チェック）

## レイヤーと依存ルール

> どの層がどの層を呼んでよいかを確定させる節。\
> _分担_: インポートの書き方と別名の設定は `## インポート / パスエイリアス（import / path alias）`。ここには呼んでよい向きだけを書く。

> _書き方_: 依存の向きは矢印（`→`）で示す。禁止には、逆向きの呼び出しや層を飛び越えた呼び出しなど、避けるものを書く。外部システムには、外部との通信をどの層に閉じ込めるかを書く。

- **許可する依存方向**: 画面は Controller → Service → Mapper → DB。各層から `common`（`common/service`・`common/utils` など）を呼んでよい。バッチは Job → 共通部品（`WTX_Common` の `ds`・`kyocera`、`WTX_Batch` の `wt/core`）→ VE → DB
- **禁止**: Controller から Mapper を直接呼ばない（必ず Service を通す）。Service から Controller と Form を参照しない。ほかの機能パッケージの Service と Mapper を直接呼ばない（共通処理は `common` 配下に置く）（回答 Q-STR-108）
- **外部システム**: 本プロジェクトで通信する外部システムは無い（`### 外部 API / 外部システム`）

## 各システムコンポーネントの役割

> システムを構成する大きな塊（フロントエンド、バックエンド、外部連携、共通基盤など）ごとに、その担当範囲を確定させる節。ここでいうコンポーネントは**アーキテクチャ上の塊**を指し、個々のボタンやフォームなどの画面部品や、ドメイン内のクラス単位は含まない。\
> _分担_: フィーチャー固有の境界（画面・サービス・モジュール）は `specs/<feature>/design.md` の `## コンポーネントとインターフェース（Components and Interfaces）`。命名規則における「ファイル（コンポーネント）」は画面部品のファイルを指す別の概念であり、`tech.md` の `## 命名規則` で扱う。

> _書き方_: 各コンポーネントを **責務 / しないこと / 配置 / 境界** の 4 点で書く。「しないこと」には、そのコンポーネントに紛れ込みやすい役割を書く。

### フロントエンド（FE）

> 利用者が直接触れる部分の担当範囲を確定させる節。

> _書き方_: 「しないこと」には、業務ルールの判定や権限の最終確認など、後ろ側に任せるものを書く。

- **責務**: 画面の表示と入力（Thymeleaf のテンプレートと、画面ごとのスクリプト）、子画面・ポップアップの表示、画面内の項目の出し分け
- **しないこと**: 権限の最終判定と業務ルールの判定（サーバ側のインターセプタと Service が行う）
- **配置**: `wing/src/main/webapp/WEB-INF/pages/`（テンプレート）、`wing/src/main/webapp/static/`（jQuery・共通の CSS と JS）
- **境界**: Controller へのフォーム送信（更新系は CSRF トークン `_csrf` を付ける。`pages/common/csrf.html`）

### バックエンド（BE）

> 要求を受け取り、業務ロジックを実行する部分の担当範囲を確定させる節。

> _書き方_: 「しないこと」には、画面の見た目に関する判断など、前側に任せるものを書く。

- **責務**: 要求の受付（Controller）、入力チェックと業務ロジック（Service）、DB アクセス（Mapper）、セッション・権限・CSRF の確認（インターセプタ）、帳票とファイルの出力
- **しないこと**: 画面の見た目の組み立て（テンプレートが行う）、時間のかかる取込処理の実行（タスクを登録してバッチに任せる）
- **配置**: `wing/src/main/java/jp/co/kccs/wt/function/`（機能）、`wing/src/main/resources/`（Mapper XML・設定）
- **境界**: 画面とは Spring MVC の Controller、DB とは MyBatis の Mapper、バッチとはタスクリストへのタスク登録（`BatchCommonService.insertTask`）

### 外部 API / 外部システム

> 自分たちで作らない、外部の仕組みとの関わり方を確定させる節。\
> _分担_: 失敗したときの再実行や遮断の方針は `non-functional.md` の `### リトライ`。ここには担当範囲だけを書く。

> _書き方_: 「しないこと」には、外部に期待してはいけないこと（自分たちの業務ルールの判定を任せる、など）を書く。境界には、外部とのやり取りをどこに閉じ込めるかを書く。

- **責務**: <COMPONENT_EXTERNAL_RESPONSIBILITY>（不要：通信する外部システムが無いため。進捗管理DB へは CSV ファイルを渡すだけで、システム間の通信はしない — 回答 Q-STR-109）
- **しないこと**: <COMPONENT_EXTERNAL_NON_RESPONSIBILITY>（不要：通信する外部システムが無いため。進捗管理DB へは CSV ファイルを渡すだけで、システム間の通信はしない — 回答 Q-STR-109）
- **配置**: <COMPONENT_EXTERNAL_LOCATION>（不要：通信する外部システムが無いため。進捗管理DB へは CSV ファイルを渡すだけで、システム間の通信はしない — 回答 Q-STR-109）
- **境界**: <COMPONENT_EXTERNAL_BOUNDARY>（不要：通信する外部システムが無いため。進捗管理DB へは CSV ファイルを渡すだけで、システム間の通信はしない — 回答 Q-STR-109）

### 共通基盤（shared）

> 複数の場所から使われる共通の部品の担当範囲を確定させる節。

> _書き方_: 「しないこと」には、特定の業務に依存する処理など、ここへ置いてはいけないものを書く。何でも入る置き場にならないように、入れてよい条件を明確にする。

- **責務**: ログイン・セッション・権限確認・CSRF・例外の受け止め・ログ・採番（`TWTZM050`）・コードマスタ（`TWTZM040`）の参照・ファイルのダウンロードなど、複数の機能で使う処理
- **しないこと**: 特定の画面や業務にだけ使う処理（その機能の `function/<サブシステム>/<機能ID>/` か、サブシステム共通の `function/<サブシステム>/common/` に置く）
- **配置**: wing は `wing/src/main/java/jp/co/kccs/wt/common/`、バッチは `WTX_Common/ds/`・`WTX_Common/kyocera/` と `WTX_Batch/src/jp/co/kccs/wt/core/`
- **境界**: 機能側からは `common/service`・`common/utils` のクラスとインターセプタを通して使う

### バッチ（WTX_Batch）

> 上の 4 つに当てはまらないコンポーネントを書く節。

> _書き方_: バッチ処理基盤、管理画面、常駐サービスなど、プロジェクト固有の塊をここに書く。上の 4 つと同じ 4 点で書く。

- **責務**: タスクリストに登録された取込などの処理を、キューごとの常駐エンジンで実行し、進捗と件数をタスクリストに記録する
- **しないこと**: 画面の表示と、利用者との対話（結果は画面のバッチ処理状況一覧 `/zzz010/` で確認する）
- **配置**: `WTX_Batch/src/jp/co/kccs/wt/<サブシステム>/<機能ID>/`（ジョブ）、`WTX_Batch/config/`・`config_linux/`（設定）、`WTX_Batch/sh/`（起動）
- **境界**: 画面とはタスクリスト（`STASKLIST` 系）、取込ファイルとは出力履歴管理（`DSOutputLogic.findHistoryFile`）、DB とは VE

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

Spec ルートはこのリポジトリの直下とする（このリポジトリで `steering/`・`specs/`・`docs/` を作成している）。

```
<案件ルート>/
├── steering/                        # steering 一式（本ファイルを含む 7 ファイル）
├── specs/
│   └── <feature>/                   # requirements.md / design.md / tasks.md
├── docs/
│   ├── architecture/
│   │   ├── system-overview.md
│   │   └── data-model.md
│   └── code-design.md
├── wing/                            # Web アプリ（Spring MVC。新しい画面はここ）
│   ├── pom.xml
│   ├── lib/                         # 社内ライブラリの jar（geframe・javakit・kccs-commons）
│   └── src/
│       ├── main/java/jp/co/kccs/wt/
│       │   ├── common/              # 共通（controller・service・interceptor・handler・exception・domain・mapper・utils ほか）
│       │   └── function/<サブシステム>/<機能ID>/
│       │       ├── controller/      # 入口（HTTP）
│       │       ├── service/         # ビジネスロジック
│       │       ├── mapper/          # 永続化アクセス（MyBatis の @Mapper）
│       │       ├── form/            # 画面の入力
│       │       └── bean/            # 画面の表示・検索条件
│       ├── main/resources/
│       │   ├── jp/co/kccs/wt/function/<サブシステム>/<機能ID>/   # Mapper XML
│       │   └── servlet-context.xml・messages.properties・log4j2.xml ほか
│       ├── main/webapp/
│       │   ├── WEB-INF/pages/<サブシステム>/<機能ID>/            # 画面テンプレート
│       │   └── static/              # 静的アセット
│       └── test/java/               # 自動テスト（書く場合。対象と同じパッケージ）
├── WTX/                             # Web アプリ（GreenEARTH・JAVA-KIT。他サブシステムの画面）
├── WTX_Batch/                       # バッチ
│   ├── src/jp/co/kccs/wt/<サブシステム>/<機能ID>/          # ジョブ
│   ├── config/ ・ config_linux/     # 設定（Windows 用・Linux 用）
│   └── sh/                          # 起動・運用スクリプト
└── WTX_Common/                      # WTX と WTX_Batch の共通部品（ds・kyocera）
```

## インポート / パスエイリアス（import / path alias）

> ファイルを読み込むときの書き方と、長いパスに付ける別名を確定させる節。\
> _分担_: 別名を実際に効かせる設定はリポジトリの設定ファイル。ここには対応関係だけを書く。

> _書き方_: 原則には、相対パスと別名のどちらを使うかの判断を書く。禁止には、階層をさかのぼり続ける書き方や、層を越えた直接の読み込みなど、避けるものを書く。

| パスエイリアス | 解決先 |
|---|---|
| なし | Java の import はパッケージの完全名で書く。別名の仕組みは無い |

- **原則**: クラスは 1 つずつ完全名で import する
- **禁止**: `*` による一括 import と、使っていない import（checkstyle の AvoidStarImport・UnusedImports。`WTX/CodeStyle/kccs-checkstyle-2.0.1.xml`）

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
