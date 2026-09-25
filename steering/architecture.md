---
status: draft
updated_at: 2026-09-25T12:54:34+09:00
---

# システムアーキテクチャ

> このファイルは **論理構成・責務・境界、およびディレクトリ構成・import / path alias** を固定する steering ドキュメントです。
> 命名規則・コード規約・技術選定・検証手順は [`tech.md`](./tech.md) を参照してください。
> 機能ごとの責務分担とつなぎ方（画面・サービス・モジュールの担当範囲）は `design.md` の Components and Interfaces に書いてください。
>
> **テンプレート**: 山括弧で囲んだ大文字の項目は、プロジェクト確定時に実値へ置換する。

> **本ファイルの記入根拠**: 本改修は既存 WiNG への機能追加であり、既存のアーキテクチャ・フレームワーク・コーディング規約に従う（REQ-053）。既存の WTG 機能にデグレードを発生させない（REQ-052）。したがってレイヤー構成・依存ルール・ディレクトリ構成・パッケージ配置は、既存実装（`wing` の `jp.co.kccs.wt.function.<サブシステム>.<画面ID>` 配下の `controller` / `form` / `service` / `mapper`、`jp.co.kccs.wt.common` の共通部品、`servlet-context.xml` の interceptor マッピング）の実体を根拠として記入している。

## アーキテクチャ概要

> 全体構成を 1 行で要約し、構成・配置モデル・通信パターンの 3 点を箇条書きで固定する。

既存 WiNG（Java / Spring MVC のオンライン Web アプリケーションと JavaKit バッチエンジンのバッチ）に、契約・管財管理（WTG）の新規機能を追加する（REQ-011 / REQ-053）。

- **構成**: サーバサイドレンダリングの Web アプリケーション（Controller → Service → Mapper の 3 層）+ バッチ（JavaKit バッチエンジン）+ Oracle Database の単一スキーマ。画面・帳票・バッチを何本のプログラムに分割するかは基本設計で決定する（REQ-010）
- **配置モデル**: Tomcat にデプロイする WAR（`wing-web.war`）と、バッチ実行環境で起動する JavaKit バッチタスク。いずれも同一の Oracle Database を参照する。UQ 様社内システム群（工事援／Compass、ドキュメント管理、AI・進捗状況、社間のやり取り、プロジェクト情報等）とは WiNG を介して連携する（REQ-006）
- **通信パターン**: ブラウザ ↔ サーバは HTTP（POST による画面遷移と、画面内の非同期通信）。バッチ実行はオンライン画面からタスクを登録し、バッチエンジンが実行する非同期方式（REQ-041）。DB アクセスは JNDI データソース（`java:comp/env/jdbc/wingDB`）経由の JDBC

## 配置原則

> _分担_: プロジェクト全体の配置パターンのみ本節に書く。**フィーチャー固有の追加ディレクトリ**は `design.md` の File Structure Plan に書く。

- **原則**: 画面（PGID）単位でパッケージを切り、その配下に `controller` / `form` / `service`（必要に応じて `mapper` / `bean`）を置く。パッケージ名は `jp.co.kccs.wt.function.<サブシステムコード小文字>.<画面ID小文字>` とし、複数画面で共有する処理のみ `jp.co.kccs.wt.common` または `jp.co.kccs.wt.function.<サブシステム>.common` に置く
- **採用理由**: 既存 WTG（`wtg002`〜`wtg050`）を含む既存機能がこの配置で実装されており、既存のアーキテクチャに従う必要があるため（REQ-053）。画面単位に閉じることで、新規機能の追加が既存機能に影響しない（REQ-052）
- **レイヤーとディレクトリ構成の対応**: `controller`（HTTP の入口・画面遷移）→ `service`（業務ロジック・トランザクション境界）→ `mapper`（SQL / 永続化）。画面の入力値は `form`、DB の行は `domain` の POJO で受け渡す（詳細は本ファイルの `## ディレクトリ構成`）
- **フィーチャー固有の追加ディレクトリ**: 本ファイルに増やさず、`design.md` の File Structure Plan に書く

## レイヤーと依存ルール

> 許可・禁止・外部システムの 3 点を明文化する。具体的な依存方向は矢印（`→`）で示す。

- **許可する依存方向**: `controller` → `service` → `mapper` → DB。`controller` / `service` → `form` / `domain` / `bean`（データ構造）。各層 → `jp.co.kccs.wt.common`（共通ユーティリティ・共通サービス）。横断関心事（ログ・セッション確認・パスワード有効期限確認・権限制御・CSRF）は `interceptor` が `controller` の手前で処理する
- **禁止**（いずれも既存実装がこの形を取っておらず、既存の構成に従うことを根拠とする — REQ-053。機能パッケージ間の直接依存の禁止は、新規機能が既存機能に影響しないための境界でもある — REQ-052）: 逆方向の依存（`service` → `controller`、`mapper` → `service`）。`controller` から `mapper` を直接呼ぶこと。`controller` / `mapper` に業務ロジックを置くこと。機能パッケージ間の直接依存（`function.wtg.wtgXXX` → `function.wtg.wtgYYY`。共有が必要な処理は `common` に置く）。`jp.co.kccs.wt.common` から機能パッケージへの依存
- **外部システム**: UQ 様社内システムは本プロジェクトの改修対象外であり（REQ-008）、連携が必要な場合も相手側の仕様に合わせる。連携は DB 上の受け渡し（インポート／エクスポート）とファイル（CSV）の受け渡しを基本とし（REQ-014 / REQ-021 / REQ-042 / REQ-047）、既存の連携方式を変更しない

## 各システムコンポーネントの役割

> ここでの **コンポーネント = System component**（FE / BE / 外部連携 / 共通基盤など、**アーキテクチャ上の大きな塊**）を指します。
> **UI 部品**（個々のボタン・フォーム・画面要素など）や **ドメイン内のクラス単位** は対象外です。
> フィーチャー固有の境界（画面・サービス・モジュールなど）は `design.md` の Components and Interfaces に書いてください。
> 命名規則の「ファイル（コンポーネント）」は UI ファイル用の別概念です（`tech.md` の `## 命名規則` 参照）。
>
> 各コンポーネントは **責務 / しないこと / 配置 / 境界** の 4 点で書く。プロジェクトに無いコンポーネントは削除し、追加が必要なものは同じ 4 点で追記する。

### フロントエンド（FE）

- **責務**: Thymeleaf テンプレートによる画面描画、入力欄の表示制御（権限による活性・非活性、複数局モード時の項目制御など）、クライアント側の入力補助（チュートリアル・サンプル入力・金額の自動計算の画面反映・行追加）、ZOOM 画面（別ウインドウ）の呼び出し
- **しないこと**: 業務ルールの最終判定（サーバ側の検証を正とする）。DB アクセス。権限判定の最終決定（`AccessControlInterceptor` が正）
- **配置**: `wing/src/main/webapp/WEB-INF/pages/<サブシステム小文字>/<画面ID小文字>/`（画面本体と `Script.html`）、共通の静的資源は `wing/src/main/webapp/static/`
- **境界**: サーバとは Form クラスにバインドされる HTTP リクエスト／`ModelAndView` のモデル属性でのみやりとりする

### バックエンド（BE）

- **責務**: リクエストの受付と画面遷移（`controller`）、入力チェックと業務ロジックとトランザクション制御（`service`）、SQL の実行（`mapper`）、帳票・CSV の生成
- **しないこと**: 画面のレイアウト定義。既存 WTG 機能の仕様変更（REQ-052）。他サブシステムのテーブルの更新（参照は既存の方式に従う）
- **配置**: `wing/src/main/java/jp/co/kccs/wt/function/wtg/<画面ID小文字>/`、SQL は `wing/src/main/resources/` 配下の同一パッケージパス
- **境界**: FE とは Form、DB とは `domain` の POJO、バッチとはタスク登録テーブル（`BatchCommonService` 経由）で接する

### 外部 API / 外部システム

- **責務**: UQ 様社内システム群との連携（REQ-006）。契約情報の取込（REQ-040〜REQ-043）と、取込で使える形式の CSV の提供（REQ-047）、進捗管理 DB インポート用の CSV 出力（REQ-021）
- **しないこと**: 相手側システムの改修（REQ-008）。相手側の仕様に合わせない独自形式の定義
- **配置**: 受け渡しファイルの入出力は既存のファイルアップロード／ダウンロードの仕組み（`FileUploadService` / `DownLoadFileInfo`）に載せる
- **境界**: ファイル（CSV）と DB 上のテーブルを境界とし、相手システムのプロセスを直接呼び出さない

### 共通基盤（shared）

- **責務**: 認証・セッション管理（`SessionService` / `LoginService`）、権限制御（`AccessControlInterceptor` + `@FuncID`）、CSRF トークンの生成・検証、ログ出力（`LoggingInterceptor` / `LogUtils`）、採番（`NumberingService`）、コードマスタ取得（`CodeMstService`）、ファイルアップロード（`FileUploadService`）、例外の一括処理（`ExceptionResolver`）、共通ユーティリティ（`utils`）
- **しないこと**: 特定機能に固有の業務ロジックを持つこと。機能パッケージへの依存を持つこと
- **配置**: `wing/src/main/java/jp/co/kccs/wt/common/`（`annotation` / `bean` / `controller` / `domain` / `exception` / `form` / `handler` / `interceptor` / `mapper` / `service` / `utils`）
- **境界**: 機能パッケージ（`jp.co.kccs.wt.function.**`）から呼ばれる側であり、呼ぶ向きは機能 → 共通基盤の一方向とする。共通基盤から機能パッケージのクラスを参照しない。Interceptor・`ExceptionResolver`・`ControllerBase` は `servlet-context.xml` と Spring の登録によって全リクエストに効き、機能側からは呼び出さない。サブシステム内の複数の画面で共有する業務処理は共通基盤に置かず、`jp.co.kccs.wt.function.<サブシステム小文字>.common` に置く（既存の `jp.co.kccs.wt.function.wte.common`。人間が確定 / 2026-09-25）

### バッチ

- **責務**: オンラインから登録されたタスクの実行（契約情報インポート、洗替更新など — REQ-041〜REQ-043）、帳票の一括生成
- **しないこと**: 画面の描画。オンライン専用の共通処理への依存
- **配置**: `WTX_Batch/src/jp/co/kccs/wt/<サブシステム小文字>/<機能ID小文字>/`、設定は `WTX_Batch/config/`（Windows）/ `WTX_Batch/config_linux/`（Linux）
- **境界**: オンラインとはタスク登録テーブルと処理対象データ（DB / ファイル）を境界とし、オンラインのクラスを直接呼び出さない

### <COMPONENT_NAME_N>

> **不要（記入者: 人間 / 2026-09-11）**: 追加のシステムコンポーネントは無し。FE / BE / 外部 API・外部システム / 共通基盤 / バッチ の 5 つで現構成を表せているため、以下の予備枠は未記入のまま残す。

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

> **Spec / Steering の配置はフローが固定する。** プロジェクトルート直下に `steering/` / `specs/` / `docs/` を置き、フローの管理ファイルは `.aidd/` に置く。**この 4 つは書き換えない。** steering 内の相互参照は、ルート直下からの相対パス（`steering/`、`specs/<feature>/`）で統一してください。

```
<リポジトリルート>/
├── .aidd/                       # フロー管理（RFP / 要求一覧 / feature-list / 進捗 / ゲート記録）
├── steering/                    # 横断方針 7ファイル（本ファイルを含む）
├── specs/                       # フィーチャーごとの requirements / design / tasks
├── docs/                        # 全体設計ドキュメント + README 以外のドキュメント
│   ├── code-design.md           # 業務コード・区分値・採番ルール
│   ├── architecture/            # data-model.md / system-overview.md
│   └── runbooks/                # 運用手順（任意。正本が Excel の場合は non-functional.md に URL のみ）
├── wing/                        # オンライン（Spring MVC / Maven）。新規 WTG 画面はここに追加する
│   ├── pom.xml
│   ├── lib/                     # ローカル install する同梱 jar（geframe / javakit / kccs-commons）
│   └── src/main/
│       ├── java/jp/co/kccs/wt/
│       │   ├── common/          # 共通基盤（annotation / bean / controller / domain /
│       │   │                    #   exception / form / handler / interceptor / mapper /
│       │   │                    #   service / utils）
│       │   └── function/<サブシステム小文字>/<画面ID小文字>/
│       │       ├── controller/  # 入口（HTTP）
│       │       ├── form/        # 画面の入力値
│       │       ├── service/     # 業務ロジック・トランザクション境界
│       │       └── mapper/      # 永続化アクセス（必要な場合）
│       ├── resources/           # log4j2.xml / messages.properties / mybatis-config.xml /
│       │   └── jp/co/kccs/wt/…  #   servlet-context.xml / wing-web.properties / Mapper XML
│       └── webapp/
│           ├── WEB-INF/pages/<サブシステム小文字>/<画面ID小文字>/   # Thymeleaf テンプレート
│           └── static/          # 静的資源（plugins / vender）
├── WTX/                         # 既存オンライン（JavaKit / geframe。Ant）
├── WTX_Batch/                   # バッチ（JavaKit バッチエンジン。Ant）
│   ├── config/ | config_linux/  # 実行環境別の設定
│   └── src/jp/co/kccs/wt/…
└── WTX_Common/                  # 既存の共通資産（Ant）
```

> `src/` 以下はパターン例。実プロジェクトに合わせて書き換えてください（`.aidd/` / `steering/` / `specs/` / `docs/` の 4 つは書き換えない）。**繰り返し構造はパターンだけ書く** ことで、新規ディレクトリ追加時のメンテを減らします。
> レイヤーと配置の対応（controller / service / repository など）は本ファイルの `## 配置原則` に従ってください。

## インポート / パスエイリアス（import / path alias）

> **不要（記入者: 人間 / 2026-09-11）**: 既存構成に従い、Java のパッケージ解決をそのまま用いる（エイリアス機構を導入しない）。下表の枠は未記入のまま残す。

| パスエイリアス | 解決先 |
|---|---|
| <PATH_ALIAS_N> | <PATH_ALIAS_TARGET_N> |

- **原則**: 完全修飾のパッケージ名で import する。`src/main/java` のパッケージ階層と `src/main/resources` の Mapper XML の配置を一致させる
- **禁止**: ワイルドカード import（Checkstyle `AvoidStarImport`）、未使用 import（`UnusedImports`）、重複 import（`RedundantImport`）

## 全体図のルール

> プロジェクト全体の地図（システム全体像・主要ビジネスフロー・外部連携・ドメイン境界）の **図の種別・ツール・Mermaid 利用方針** を定義する。
> **図の実体（Mermaid 図・記述・プレースホルダー）は `docs/architecture/system-overview.md` を参照する。** 本節には図の方針のみを書き、図そのものは置かない。
> 図は **Mermaid のみ**（画像を貼らない）。フィーチャー個別のフローは `specs/<feature>/design.md` の System Flows に書く。
> _分担_: コンポーネント横断の代表フローのみ全体図に載せる。サービス内部の詳細シーケンス / ステート図は `specs/<feature>/design.md` に書く。

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

*論理構成・責務境界・ディレクトリ構成を固定するためのファイルです。製品名・版・コマンド・命名規則・コード規約は [`tech.md`](./tech.md) に書いてください。*
