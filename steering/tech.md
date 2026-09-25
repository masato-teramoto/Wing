---
status: draft
updated_at: 2026-09-25T12:54:34+09:00
---

# 技術スタック

> このファイルは **プロジェクト全体で固定する技術的前提** を記述する steering ドキュメントです。
> エージェント・人間どちらもここを参照することで、フィーチャーごとに別スタックを選ばないようにします。
> その機能だけで使う追加ライブラリは `design.md` の Technology Stack に書いてください。

> **論理構成・配置モデル・通信パターン** は [`architecture.md`](./architecture.md) を参照してください。本ファイルには製品名・版・検証手順のみを書きます。
>
> **テンプレート**: 山括弧で囲んだ大文字の項目は、プロジェクト確定時に実値へ置換する。

> **本ファイルの記入根拠**: 本改修は既存 WiNG への機能追加であり、既存のアーキテクチャ・フレームワーク・コーディング規約に従う（REQ-053）。したがって採用技術・版・規約は、既存資産（`wing` = Spring MVC オンライン、`WTX` = JavaKit/geframe オンライン、`WTX_Batch` = JavaKit バッチ、`WTX_Common` = 共通）の実体を根拠として記入している。

## コアテクノロジ

> 区分は例。プロジェクトで使わない区分は行ごと削除し、足りない区分は行を追加する。

| 区分 | 採用 | バージョン | 備考 |
| --- | --- | --- | --- |
| 言語（FE） | JavaScript（jQuery ベース） | jQuery / jQuery UI 1.12.1（`wing/src/main/webapp/static/plugins/`） | SPA フレームワークを新規採用しない（REQ-053） |
| 言語（BE） | Java | コンパイルの source / target とも 1.7（`wing/pom.xml`） | バッチ側（`WTX_Batch`）は JavaKit バッチエンジンの実行系に従う |
| フレームワーク（FE） | Thymeleaf テンプレート（サーバサイドレンダリング） | Thymeleaf 3.0.0.RELEASE / thymeleaf-spring4 | `/WEB-INF/pages/` 配下・拡張子 `.html`・UTF-8（`servlet-context.xml`） |
| フレームワーク（BE） | Spring Framework（Spring MVC） | 4.3.5.RELEASE | `DispatcherServlet` + `servlet-context.xml`。JavaKit / geframe（`geframe-core` / `geframe-commons` / `geframe-jk2extension` 3.5.0、`javakit` 2.14.3）と併用 |
| ランタイム | Apache Tomcat（Servlet 3.0 / WAR デプロイ） | `web.xml` は `web-app_3_0.xsd`。ローカル実行は tomcat7-maven-plugin 2.2 | 成果物名 `wing-web.war`（`pom.xml` の `finalName`） |
| データベース | Oracle Database | JDBC ドライバ ojdbc7 12.1.0.2（`wing/pom.xml`） | 接続は JNDI データソース `java:comp/env/jdbc/wingDB` |
| キャッシュ / キー・バリューストア（KVS） | 採用しない | — | 既存 WiNG に該当構成が無い。HTTP セッション（`HttpSession`）以外のキャッシュ層を新規に導入しない |
| メッセージング | 採用しない | — | 非同期処理は JavaKit バッチエンジンへのタスク登録で行う（`BatchCommonService`） |

## 主要な技術選定と理由

> なぜこのスタックを選んだか、代替案を含めて 1 セット 3〜5 行で。議論になりやすいカテゴリ（言語・FW・DB 等）だけ書く。不要なら節ごと省略可。

### 言語: Java（コンパイルターゲット 1.7）

- **採用理由**: 本改修は既存 WiNG への機能追加であり、既存のアーキテクチャ・フレームワーク・コーディング規約に従うため（REQ-053）。既存資産（`wing` / `WTX` / `WTX_Batch` / `WTX_Common`）がすべて Java で実装されている
- **代替案**: <TECH_CHOICE_LANGUAGE_ALTERNATIVE> — **不要（記入者: 人間 / 2026-09-11）**: 既存構成を変えないため代替案の検討を行わない（REQ-053）
- **再評価条件**: <TECH_CHOICE_LANGUAGE_REEVAL> — **不要（記入者: 人間 / 2026-09-11）**: 同上

### フレームワーク: Spring MVC 4.3.5 + MyBatis 3.4.5 + Thymeleaf 3（オンライン）／ JavaKit バッチエンジン（バッチ）

- **採用理由**: 既存の WTG 画面（例: `wtg004` = PWTGO008）が Controller / Service / Form / Mapper の構成で実装済みであり、新規機能も同一構成で追加することで既存機能との整合性（画面ID・PGID体系、権限制御、マスタ構造）を維持できる（REQ-009 / REQ-053）。バッチは既存の JavaKit バッチエンジンでタスク登録・実行される仕組みに合わせる
- **代替案**: <TECH_CHOICE_FRAMEWORK_ALTERNATIVE> — **不要（記入者: 人間 / 2026-09-11）**: 既存構成を変えないため代替案の検討を行わない（REQ-053）
- **再評価条件**: <TECH_CHOICE_FRAMEWORK_REEVAL> — **不要（記入者: 人間 / 2026-09-11）**: 同上

### データベース: Oracle Database

- **採用理由**: 既存 WiNG が Oracle（ojdbc7 12.1.0.2、JNDI データソース `jdbc/wingDB`）で稼働しており、新規テーブルも同一スキーマに追加するため（REQ-053）。既存マスタ構造との整合性を維持する必要がある（REQ-009）
- **代替案**: <TECH_CHOICE_DATABASE_ALTERNATIVE> — **不要（記入者: 人間 / 2026-09-11）**: 既存構成を変えないため代替案の検討を行わない（REQ-053）
- **再評価条件**: <TECH_CHOICE_DATABASE_REEVAL> — **不要（記入者: 人間 / 2026-09-11）**: 同上

## 主要ライブラリ

> 開発パターンに影響する主要ライブラリのみ。全依存はここに書かない。繰り返しが必要な項目は `*_N` を行追加用スロットとして使う。

- **ORM / クエリ / マイグレーション**: MyBatis 3.4.5 + mybatis-spring 1.3.1 — 既存の DB アクセスが Mapper インタフェース + XML の SQL で実装されており、これに合わせる（REQ-053）
- **バリデーション**: Bean Validation（validation-api 1.1.0.Final / hibernate-validator 5.0.1.Final）+ 業務チェックの `ValidationUtils` — 既存の入力チェックが `LocalValidatorFactoryBean` と `ValidationUtils` の併用で実装されている
- **テスト**: JUnit 4.12 + spring-test 4.3.5.RELEASE — `wing/pom.xml` の test スコープ依存。適用範囲と運用は本ファイルの `## テスト方針` を参照
- **認証**: 自前実装（`LoginService` / `SessionCheckInterceptor` / `PasswordCheckInterceptor` / `AccessControlInterceptor`）— 方針は `security.md` の `## 認証・認可` を正とする
- **HTTP クライアント**: Apache HttpClient 4.5.3 — 外部連携が必要な場合のみ使用する
- **リトライ / 外部依存の遮断**: <LIB_RETRY> — <LIB_RETRY_REASON> — **不要（記入者: 人間 / 2026-09-25）**: wing には既存のリトライ用ライブラリが無く、本リリースでも外部サービスを同期で呼ばないため
- **帳票**: オンラインは Excel テンプレート方式（原本の Excel をコピーして値を書き込み、PDF に変換する。Excel を扱うライブラリは未確定で、選定したら本行に追記する）／ report-engine（`WTX_Batch`）— 帳票出力（REQ-023 / REQ-025）の基盤。`wing/pom.xml` に宣言のある JasperReports 6.5.1 は帳票の基盤に使わない（人間が確定 / 2026-09-25。根拠: WTG070 機能定義書_印刷・閲覧用帳票）
- **QR コード**: zxing core 3.2.1 — 帳票の表紙情報に印字する QR コード画像の生成（REQ-024）
- **ログ**: Log4j 2（log4j-api / log4j-core 2.12.4）— 設定は `wing/src/main/resources/log4j2.xml`。出力方針は `non-functional.md` の `### ログ方針` を正とする
- **JSON / シリアライズ**: Jackson 2.9.4 / Gson 2.8.1 — 画面の非同期通信で使用
- **ファイルアップロード**: commons-fileupload 1.3.3（`CommonsMultipartResolver`。`maxUploadSize` は 1,048,576,000 バイト。**本項を上限値の正本とする**）— 契約稟議に関するファイル登録（REQ-020）で使用
- **ボイラープレート削減**: Lombok 1.16.18 — `domain` パッケージの `@Data` / `@NoArgsConstructor` / `@AllArgsConstructor`

## 開発環境

### 必須ツール

| ツール | バージョン | 用途 |
| --- | --- | --- |
| JDK | source / target 1.7 でコンパイルできる版 | ビルド・実行 |
| Apache Maven | Maven Wrapper 同梱（`wing/.mvn/wrapper`） | `wing`（オンライン）のビルド・依存解決 |
| Apache Ant | 同梱の `build.xml` が動作する版 | `WTX` / `WTX_Batch` / `WTX_Common` のビルド（`init` / `clean` / `build` / `war` ターゲット） |
| Eclipse（Pleiades 同梱版） | `.project` / `.classpath` / `.settings` を読める版 | 既存プロジェクトの IDE |
| Oracle Database 接続環境 | ojdbc7 12.1.0.2 で接続できる版 | ローカル・検証機での DB 接続 |
| Apache Tomcat | Servlet 3.0 対応版 | WAR のデプロイ先 |

### 推奨 OS / IDE

- OS: 開発は Windows（`execute_task.bat` / `dsz015.bat` の起動スクリプト、`wing-web.properties` の `CHARSET=Windows-31J` が Windows 前提）。実行環境は Linux（`WTX_Batch/config_linux/`。`log4j2.xml` のログ出力先は `non-functional.md` の `#### 監視基盤` を正とする）
- IDE: Eclipse（Pleiades）、推奨拡張: Checkstyle プラグイン（`.checkstyle` と `CodeStyle/kccs-checkstyle-2.0.1.xml` を読む）、Tomcat プラグイン（`WTX/.tomcatplugin`）、m2e（`wing/.settings/org.eclipse.m2e.core.prefs`）

### Git 戦略

> **不要（記入者: 人間 / 2026-09-11）**: 既存 WiNG の開発運用に従い、本プロジェクトで新たに定めない。以下のプレースホルダーはこの理由で未記入のまま残す。

- **ブランチ運用モデル**: <GIT_BRANCHING_MODEL>
- **保護ブランチ**: <PROTECTED_BRANCH>
- **保護ブランチの条件**: <PROTECTED_BRANCH_RULE>
- **マージ方法**: <MERGE_STRATEGY>
- **リリースタグ**: <RELEASE_TAG_CONVENTION>

※マージ条件・詳細ルールは `## 開発標準`、CI 詳細は本ファイルの `## テスト方針` > `### CI 統合`、本番リリース・障害対応は `non-functional.md`、シークレット管理は `security.md` を参照。

#### 運用ルール一覧

| 項目 | 運用ルール |
| --- | --- |
| **ブランチ名** | <BRANCH_NAMING_RULE> |
| **仕様管理（spec）** | <SPEC_MANAGEMENT_RULE> |
| **コミット** | <COMMIT_CONVENTION_RULE> |
| **PR（プルリクエスト）** | <PR_RULE> |

**禁止事項:**

- <GIT_PROHIBITED_PRACTICE_N>


## 共通コマンド

> **不要（記入者: 人間 / 2026-09-11）**: 既存 WiNG のビルド手順（`wing` は Maven Wrapper、`WTX` / `WTX_Batch` / `WTX_Common` は Ant の `build.xml`）に従い、本プロジェクトで新たに標準コマンドを定めない。テンプレートは「ローカルで実際に成功するコマンドのみを記載する」ことを求めているため、実行確認を経ていないコマンドをここに書かず、プレースホルダーのまま残す。

```bash
# 依存インストール
<CMD_INSTALL>

# ローカル開発
<CMD_DEV>

# ビルド
<CMD_BUILD>

# テスト（全体）
<CMD_TEST_ALL>

# テスト（単一ファイル）
<CMD_TEST_SINGLE>

# Lint / フォーマット
<CMD_LINT> && <CMD_FORMAT>

# 型チェック
<CMD_TYPECHECK>
```

> ここに書いたコマンドは、このリポジトリで変更を検証するときの **標準手順** です。人間の開発者・CI・実装を支援するエージェントは、いずれもここを起点にしてください。プレースホルダや未検証のコマンドは残さず、**ローカルで実際に成功する** ものだけを記載してください。

## 開発標準

エージェント・人間ともに、フィーチャー実装で次を守る（詳細設定はリポジトリの Lint / CI に委ねる）。

- **型安全**: Java の静的型付けに従う。`domain` は Lombok の `@Data` を付けた POJO とし、MyBatis の `resultType` で受ける。`Map` による型無しのデータ受け渡しを新規に増やさない
- **API 境界**: 画面と Controller の境界は Form クラス（`FormBase` を継承）、Service と Mapper の境界は `domain` パッケージの POJO とする。Controller に SQL・業務ロジックを書かない（レイヤの規約は `architecture.md`、HTTP の形は `api-standards.md` を正とする）
- **品質ゲート**: <DEV_STANDARD_QUALITY_GATE>（不要 / 人間 2026-09-11: 既存 WiNG の開発運用に従う）
- **レビュー**: 対象設計書とレビュー実施時期は RFP §10-1 のレビュー計画に従う。基本設計は五月雨式にレビューを依頼する（REQ-068）。コードレビューの運用は <DEV_STANDARD_REVIEW>（不要 / 人間 2026-09-11: 既存 WiNG の開発運用に従う）

## 命名規則

> _分担_: ディレクトリ構成・import / path alias は `architecture.md` を参照する。ここは **識別子・ファイル名・テーブル名等の命名形式** を定義する。

| 対象 | 規約 | 例 |
|---|---|---|
| 画面ID | `GWTG` + 3 桁の連番。既存の画面ID体系に従って採番する（REQ-051） | `GWTG004` |
| PGID（オンライン） | `PWTGO` + 3 桁の連番。既存の PGID 体系に従って採番する（REQ-051） | `PWTGO008` |
| PGID（バッチ） | `PWTGB` + 3 桁の連番。既存の PGID 体系に従って採番する（REQ-051） | `PWTGB001` |
| 機能パッケージ | `jp.co.kccs.wt.function.<サブシステムコード小文字>.<画面ID小文字>` | `jp.co.kccs.wt.function.wtg.wtg004` |
| Controller クラス | PGID の先頭大文字 + `Controller`。`@Controller` / `@RequestMapping("/<画面ID小文字>")` / `@FuncID("<PGID大文字>")` を付与する。**同じ画面IDに属する別の PGID は、同じ機能パッケージに置いて `@RequestMapping("/<画面ID小文字>/<サブパス>")` で受ける**（既存 `Pwtgo007Controller` の `/wtg003/payInfoRef`。人間が確定 / 2026-09-24） | `Pwtgo008Controller` |
| 帳票ID | `R` + サブシステムコード + 3 桁。既存の帳票ID体系（WT_機能一覧）に従って採番する（REQ-051。人間が確定 / 2026-09-24） | `RWTG070` |
| Service クラス | PGID の先頭大文字 + `Service` | `Pwtgo008Service` |
| Form クラス | PGID の先頭大文字 + `Form`。`FormBase` を継承する | `Pwtgo008Form` |
| Mapper インタフェース | PGID の先頭大文字 + `Mapper`（共通は対象テーブル名の先頭大文字 + `Mapper`）。`@Mapper` を付与する | `Pwtgo008Mapper` / `Twtzm050Mapper` |
| Mapper XML | Mapper インタフェースと同名の `.xml`。`src/main/resources` 配下の **同一パッケージパス** に置き、`namespace` に完全修飾名を書く | `jp/co/kccs/wt/common/mapper/NumberingMapper.xml` |
| domain クラス | `database.md` の `## 命名規則` を正とする | — |
| domain のフィールド | `database.md` の `## 命名規則` を正とする | — |
| ファイル（コンポーネント） | 1 ファイル = 1 クラスとし、ファイル名はクラス名と同じにする（`<クラス名>.java`）。画面のファイルは下の「Thymeleaf テンプレート」の行に従う。`architecture.md` のコンポーネント（責務の単位）とは別の概念である（人間が確定 / 2026-09-25） | `Pwtgo070Controller.java` / `pwtgo070.html` |
| Thymeleaf テンプレート | `/WEB-INF/pages/<サブシステム小文字>/<画面ID小文字>/<PGID小文字>.html`。画面内の JavaScript は同ディレクトリの `<PGID小文字>Script.html` に分ける | `wtg/wtg004/pwtgo008.html` / `pwtgo008Script.html` |
| ZOOM 画面 | `z` で始まるパッケージに置き、表示サイズを `wing-web.properties` の `ZOOM_DEFINE.<PGID小文字>` に定義する | `zwtz002` |
| メッセージID | `<3 文字の区分>-<6 桁の連番>`。`messages.properties` に定義する | `DS-000001` / `GEF-000036` |
| 例外クラス | 事象を表す名詞 + `Exception` | `ExclusiveException` / `InvalidAccessErrorException` |
| テーブル名・カラム名 | `database.md` の `## 命名規則` を正とする | — |

## コード規約

> 自動チェックに任せられないコーディング方針をここに書く。Linter / Formatter で機械チェックできる項目（インデント幅・セミコロンなど）は書かない。

- **Checkstyle 準拠**: `CodeStyle/kccs-checkstyle-2.0.1.xml`（KCCS 標準）に従う。機械チェックできる項目はここに再掲しない。やむを得ず外す場合のみ `//CHECKSTYLE:OFF` 〜 `//CHECKSTYLE:ON` で範囲を限定する（例: Lombok を使う `domain` クラス）
- **Javadoc**: クラス・メソッド・フィールドに Javadoc を書く。クラスとメソッドには `@author`（`KCCS` + 担当者名）と `@since`（`yyyy/MM/dd`）を入れる。既存クラスを変更する場合は既存の記載を消さない
- **著作権ヘッダ**: ファイル先頭に `Copyright <年> Kyocera Communication Systems Co., Ltd All rights reserved.` のコメントを置く
- **日本語コメント**: フィールド・定数の説明は日本語で書く（既存資産が日本語コメントで統一されている）
- **定数**: リテラルの直書きを避け、共通の値は `jp.co.kccs.wt.common.utils.Constants` に定義する。機能固有の定数は当該機能のクラス内に `static final` で置く
- **メッセージの外出し**: 画面・ログに出す文言は `messages.properties` にメッセージID付きで定義し、`MessageSource` 経由で取得する。ソースに文言を直書きしない
- **SQL の置き場・パラメータ**: `database.md` の `## クエリパターン`「SQL の置き場」「パラメータ」を正とする（本ファイルに再掲しない）
- **新規機能の追加方針**: 既存クラス・既存 SQL を書き換えず、新規の Controller / Service / Mapper / Form を追加する形で実装する。既存 WTG 機能にデグレードを発生させない（REQ-052）
- **共通処理の再利用**: 採番は `NumberingService`、コードマスタ取得は `CodeMstService`、ファイルアップロードは `FileUploadService`、ログインユーザー情報は `LoginUserUtils` を使う。同等の処理を機能側で作り直さない

## 例外処理

> このセクションは **実装レベルの例外処理** を扱う。
> エラー区分・共通レスポンス形式・API 契約は `api-standards.md` の `## エラーハンドリング（API 契約）`、
> ログ・アラート・リトライ・監視（観測部）は `non-functional.md` の `## 信頼性・観測性` を参照する。

### 例外処理フロー

> ここでは **例外オブジェクト** を各箇所でどう扱い、上位層に渡していくかを定める（exception propagation）。
> 識別子（`requestId` / `traceId`）の下流伝播は `non-functional.md` の「ログ方針 > トレース ID / リクエスト ID の伝播」を参照。
> _分担_: フィーチャー固有の例外クラス一覧は `specs/<feature-name>/design.md` の Error Handling に書く。

| 箇所 | 方針 |
| --- | --- |
| Mapper（MyBatis） | 例外を握りつぶさない。SQL 実行時の例外はそのまま Service へ伝播させる |
| Service | 業務エラーは `ApplicationException` またはその派生（`ExclusiveException` 等）を投げる。メッセージは文言ではなくメッセージID（`getMessageKey()`）で保持する |
| Controller | 入力チェックの結果は `BindingResult` に積み、画面に戻して表示する。業務エラーの例外は捕捉せずグローバルハンドラに委ねる |
| Interceptor | 認証・認可・CSRF の違反は専用例外（`InvalidAccessErrorException` / `CSRFTokenErrorException`）を投げてリクエストを止める |
| グローバルハンドラ | `ExceptionResolver` が例外をメッセージIDから文言に変換し、`error` ビューへ遷移させたうえでスタックトレースを Log4j 2 に出力する |
| バッチ | JavaKit バッチエンジンのタスクとして異常終了させ、タスクの状態とメッセージIDをログに残す |

### 例外クラス命名規約

| 種別 | 命名 / 用途 |
| --- | --- |
| `ApplicationException` | 業務エラーの基底。メッセージID（`messageKey`）とパラメータ（`messageParam`）を保持する |
| `ExclusiveException` | 排他エラー（他ユーザーによる更新の検出） |
| `InvalidAccessErrorException` | 権限の無い機能へのアクセス。ユーザーID / メニューID / 機能ID を保持する |
| `CSRFTokenErrorException` | CSRF トークンの不一致 |
| `InvalidParamErrorException` | 想定しないリクエストパラメータ |
| `AddRowInvalidException` | 明細の行追加の上限・不正 |

| # | ルール |
| --- | --- |
| 1 | クラス名は事象を表す名詞 + `Exception` とし、`jp.co.kccs.wt.common.exception` に置く（機能固有のものは当該機能のパッケージ） |
| 2 | 業務エラーの例外は文言ではなくメッセージIDを保持し、文言化はグローバルハンドラで行う |
| 3 | 例外を握りつぶさない。`catch` して何もしない実装を作らない（Checkstyle の `IllegalCatch` に従い、`Exception` / `Throwable` の広域 catch を新規に増やさない） |

### グローバルハンドラ

- **方針**: `HandlerExceptionResolver` の実装 `ExceptionResolver` を `@Component` として登録し、Controller で捕捉されなかった例外を一括で処理する。例外種別ごとにメッセージIDを決め、`MessageSource` で文言化して `error` ビューへ渡す。**渡すモデル属性名・既定のエラーコードは `api-standards.md` の `### 共通エラー形式` を正とする**（本節に再掲しない）。

| フレームワーク | 実装場所 |
| --- | --- |
| Spring MVC（例外の一括処理） | `jp.co.kccs.wt.common.handler.ExceptionResolver` |
| Spring MVC（Controller 共通の前処理） | `jp.co.kccs.wt.common.controller.ControllerBase`（`@ControllerAdvice`） |

| # | ルール |
| --- | --- |
| 1 | 新規機能のために `ExceptionResolver` へ分岐を足さない。機能固有の例外は `ApplicationException` を継承してメッセージIDで区別する |
| 2 | 画面に返す文言にスタックトレース・SQL・内部パスを含めない（`security.md` の機密データの扱いと整合） |
| 3 | 例外はスタックトレースを Log4j 2 の `error` レベルで出力する（出力先・形式は `non-functional.md` を正とする） |

## テスト方針

> **目的**: テストの方針・配置・命名・種類・構造・モック方針・カバレッジ目標を統一する。
> 個別フィーチャー固有の **テスト観点** は `specs/<feature>/design.md` に書き、
> **完了条件** は `specs/<feature>/tasks.md` に書き、
> ここには **全フィーチャーに適用される共通のテストルール** だけを書く。
> テストツール・実行コマンドの正本は本ファイルの `## 共通コマンド`、アサート対象のエラーコード形式は `api-standards.md` を参照する。
> CI 品質ゲートと PR マージ条件の連携は本ファイルの `## 開発標準` と整合させる。

### 基本方針

> プロジェクトのテスト原則を列挙する。採用しない行は削除する。

- 既存の WTG 機能（契約情報変更・参照、支払実績データ作成／変更／参照、電力会社直受支払実績変更、契約支払情報インポート、契約基本情報インポート、インボイス情報インポート）にデグレードを発生させないことを確認する（REQ-052 / REQ-073）
- データ移行のテストは発注者にて実施する。本プロジェクトのテスト範囲に含めない（REQ-054）
- テスト用データ（整合性のとれているマスタデータ、取込データ）は発注者から提供される前提で計画する（REQ-069）
- 受入テストの準備・運営は発注者が行う（REQ-070）
- <TEST_PRINCIPLE_N>（不要 / 人間 2026-09-11: 既存 WiNG の開発運用に従う）

> **以降の `### 配置 / 命名` から `### CI 統合` までの未記入項目について（記入者: 人間 / 2026-09-11）**: テストの配置・命名・種類・構造・モック方針・カバレッジ目標・CI は、既存 WiNG の開発運用に従い本プロジェクトで新たに定めない。プレースホルダーはこの理由で未記入のまま残す。

### 配置 / 命名

> _分担_: フィーチャー固有のテストファイル一覧は `specs/<feature>/tasks.md` / `design.md` に書く。
> ここは **リポジトリ全体の配置・命名規約** のみを定義する。

#### 配置パターン

| パターン | 例 | 備考 |
| --- | --- | --- |
| <TEST_LAYOUT_PATTERN_PRIMARY> | <TEST_LAYOUT_EXAMPLE_PRIMARY> | <TEST_LAYOUT_NOTE_PRIMARY> |
| <TEST_LAYOUT_PATTERN_ALT> | <TEST_LAYOUT_EXAMPLE_ALT> | <TEST_LAYOUT_NOTE_ALT> |

| # | 配置に関するルール |
| --- | --- |
| N | <TEST_LAYOUT_RULE_N> |

#### 命名

| 対象 | ルール | 例 |
| --- | --- | --- |
| ファイル | <TEST_FILE_NAMING_RULE> | <TEST_FILE_NAMING_EXAMPLE> |
| describe | <TEST_DESCRIBE_NAMING_RULE> | <TEST_DESCRIBE_NAMING_EXAMPLE> |
| it / test | <TEST_IT_NAMING_RULE> | <TEST_IT_NAMING_EXAMPLE> |
| 通しテスト（E2E）のシナリオ | <TEST_E2E_NAMING_RULE> | <TEST_E2E_NAMING_EXAMPLE> |

| # | 命名に関する補足 |
| --- | --- |
| N | <TEST_NAMING_NOTE_N> |

### テスト種類

> _分担_: フィーチャーごとに「何を Unit / Integration / E2E で検証するか」は `specs/<feature>/design.md` の Testing に書く。

| 種類 | 範囲 | モック方針 | 速度目標 |
| --- | --- | --- | --- |
| <TEST_TYPE_N> | <TEST_TYPE_SCOPE_N> | <TEST_TYPE_MOCK_POLICY_N> | <TEST_TYPE_SPEED_TARGET_N> |

| # | 選定基準 |
| --- | --- |
| N | <TEST_SELECTION_CRITERIA_N> |

### 構造（AAA）

> Arrange → Act → Assert の骨格で 1 テスト = 1 振る舞いを徹底する。

| # | ルール |
| --- | --- |
| N | <TEST_AAA_RULE_N> |

### モック / フィクスチャ / データ

| # | 方針 |
| --- | --- |
| N | <TEST_MOCK_POLICY_N> |

### テストデータ管理

| 種類 | 方針 |
| --- | --- |
| マスタデータ・取込データ | 発注者が提供する整合性のとれたデータを使用する（REQ-069） |
| <TEST_DATA_KIND_N> | <TEST_DATA_POLICY_N>（不要 / 人間 2026-09-11: 既存 WiNG の開発運用に従う） |

### カバレッジ目標

> _分担_: **カバレッジの数値閾値**はプロジェクト共通ルールとして本節のみに書く。
> `specs/<feature>/design.md` の Testing には **検証観点（何を・どの粒度で確認するか）** のみを書き、○％ 以上のような数値は書かない。
> 閾値の **実装**（ツール設定・CI ワークフロー）は本ファイルの `## 共通コマンド` / リポジトリ設定が正本。ここでは **数値目標と例外ルール** のみを定義する。

| 区分 | 目標 |
| --- | --- |
| <COVERAGE_SCOPE_N> | <COVERAGE_TARGET_N> |

| # | カバレッジ運用ルール |
| --- | --- |
| N | <COVERAGE_POLICY_N> |

### CI 統合

> 実行コマンド・ワークフロー定義の正本は本ファイルの `## 共通コマンド` とリポジトリの CI 設定。
> ここは **いつ何を blocking にするか** の方針のみを定義する。

| # | 項目 | 内容 |
| --- | --- | --- |
| N | <CI_TEST_ITEM_N> | <CI_TEST_POLICY_N> |

### 完了条件との接続

> _分担_: 各タスクの観測可能な完了条件は `specs/<feature>/tasks.md` に書く。
> 受け入れ基準（EARS）の原文は `specs/<feature>/requirements.md` が正本。

| # | 接続ルール |
| --- | --- |
| 1 | 各工程の完了は工程完了報告書（基本設計・製造・総合テスト・検証機リリース・本番機リリース）の納品をもって示す（REQ-057） |
| N | <TEST_COMPLETION_RULE_N>（不要 / 人間 2026-09-11: 既存 WiNG の開発運用に従う） |

---

*技術的前提と標準コマンドを固定するためのファイルです。個別フィーチャーが採用する追加ライブラリや実装詳細はここに書かないでください。*