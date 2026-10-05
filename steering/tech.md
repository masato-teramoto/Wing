---
status: approved
updated_at: 2026-10-05T18:25:03+09:00
---

# 技術スタック

> このファイルは、**プロジェクト全体で固定する技術的な前提** を確定させる文書である。人もエージェントもここを見ることで、フィーチャーごとに別々の技術を選ばないようにする。\
> _分担_: 論理構成・配置モデル・通信パターンは `architecture.md` の `## アーキテクチャ概要`、ディレクトリ構成は同ファイルの `## ディレクトリ構成`。その機能だけで使う追加ライブラリは `specs/<feature>/design.md` の `### 技術スタック（Technology Stack）`。

> _書き方_: 製品名・バージョン・コマンド・規約など、全フィーチャーに共通するものだけを書く。

> _出典の表記_: 「回答 N」「回答 Q-STR-xxx」は Phase 2 の作成中の質問に対する人間の回答（回答者 Junichi Noumi、2026-10-01）の項番・質問ID。パスは案件ルート（このリポジトリ）からの相対パスで、既存 WiNG のソース（`wing/`・`WTX/`・`WTX_Batch/`・`WTX_Common/`）から読み取った根拠を示す（ソースから読み取ることは人間の回答による指示）。

## コアテクノロジ

> プロジェクトの土台となる技術と、そのバージョンを確定させる節。\
> _分担_: 選んだ理由と代替案は `## 主要な技術選定と理由`。ここには製品名とバージョンだけを書く。DB エンジン名はこの表を正とし、`database.md` はここを参照する。

> _書き方_: バージョンは、実際に動かしているものを書く。備考には、上げ下げの制約や、特定バージョンに依存している事情を書く。

| 区分 | 採用 | バージョン | 備考 |
| --- | --- | --- | --- |
| 言語（FE） | HTML（Thymeleaf テンプレート）／ JavaScript（jQuery・jQuery UI） | jQuery 3.6.0 ／ jQuery UI 1.12.1 | 新しい画面はすべて wing で作る（回答 1）。`wing/src/main/webapp/static/` |
| 言語（BE） | Java | 1.7（実行環境の JDK は 1.7.0.55） | `wing/pom.xml` の source/target 1.7。JDK は WTZ 共通「非機能要求」に従う（回答 6）。バッチ（`WTX_Batch/`）も Java 7 で動く（`WTX_Batch/sh/batch_start.sh` の JAVA_HOME） |
| フレームワーク（FE） | Thymeleaf（thymeleaf-spring4） | 3.0.0.RELEASE | `wing/pom.xml` |
| フレームワーク（BE） | 画面：Spring MVC（XML 設定。Spring Boot は使っていない）／ バッチ：GreenEARTH Framework（geframe）と JAVA-KIT の batch-engine | Spring 4.3.5.RELEASE ／ geframe 3.5.0・javakit 2.14.3・batch-engine 2.7.0 | 画面は `wing/pom.xml`・`wing/src/main/resources/servlet-context.xml`。バッチは `WTX_Batch/lib/`。新しいバッチは既存の PWTGB030・040・050 と同じ batch-engine で作る（回答 2） |
| ランタイム | Apache Tomcat（前段に Apache HTTP Server）。OS は Oracle Linux。PDF 変換用に OpenOffice（Tomcat と同じアプリケーションサーバーに常駐させ、localhost の 8100 番ポートで待ち受ける。版は本番サーバーに導入済みのものに従う）（Phase 2 ゲート 2 回目 指摘14 の修正指示） | Tomcat 7.0.53 ／ Apache HTTP Server 2.4.34 ／ Oracle Linux 7.9 | WTZ 共通「非機能要求」に従う（回答 6）。wing は war を Tomcat に配備する（`wing/src/main/webapp/META-INF/context.xml`） |
| データベース | Oracle Database Enterprise Edition | 19.15 | WTZ 共通「非機能要求」に従う（回答 6）。JDBC ドライバは ojdbc7 12.1.0.2（`wing/pom.xml`） |
| キャッシュ / キー・バリューストア（KVS） | なし | — | 既存 WiNG の依存（`wing/pom.xml`・`WTX/WEB-INF/lib/`・`WTX_Batch/lib/`）に該当する製品が無い |
| メッセージング | なし | — | 同上。画面からバッチへの依頼は DB のタスクリストへの登録で行う（`architecture.md` の `## アーキテクチャ概要`） |

## 主要な技術選定と理由

> なぜこの技術を選んだかを、代替案とあわせて残す節。後から参加した人が同じ判断に至れるようにする。\
> _分担_: 製品名とバージョンは `## コアテクノロジ`。ここには理由だけを書く。

> _書き方_: 意見が分かれやすいもの（言語、フレームワーク、DB など）だけを書く。再評価条件には、何が起きたらこの選択を見直すかを書く。

### 言語: Java

- **採用理由**: 既存 WiNG への機能追加であり、既存のアーキテクチャ・フレームワーク・コーディング規約に従う（REQ-045）
- **代替案**: <TECH_CHOICE_LANGUAGE_ALTERNATIVE>（不要：既存構成を変えないため。REQ-045 — 回答 Q-STR-101）
- **再評価条件**: <TECH_CHOICE_LANGUAGE_REEVAL>（不要：既存構成を変えないため。REQ-045 — 回答 Q-STR-101）

### フレームワーク: Spring MVC（画面）／ batch-engine（バッチ）

- **採用理由**: 既存の WTG 画面（GWTG003〜GWTG050）とログインが wing（Spring MVC）にあり、新しい画面もすべて wing で作る（回答 1）。取込バッチは既存の PWTGB030・040・050 と同じく WTX_Batch の batch-engine で作る（回答 2）
- **代替案**: <TECH_CHOICE_FRAMEWORK_ALTERNATIVE>（不要：既存構成を変えないため。REQ-045 — 回答 Q-STR-101）
- **再評価条件**: <TECH_CHOICE_FRAMEWORK_REEVAL>（不要：既存構成を変えないため。REQ-045 — 回答 Q-STR-101）

### データベース: Oracle Database

- **採用理由**: 既存 WiNG の DB であり、既存の WTG のテーブルとマスタ構造を使う（REQ-004・REQ-045、回答 6）
- **代替案**: <TECH_CHOICE_DATABASE_ALTERNATIVE>（不要：既存構成を変えないため。REQ-045 — 回答 Q-STR-101）
- **再評価条件**: <TECH_CHOICE_DATABASE_REEVAL>（不要：既存構成を変えないため。REQ-045 — 回答 Q-STR-101）

## 主要ライブラリ

> 開発のしかたに影響する主要なライブラリを確定させる節。\
> _分担_: その機能だけで使うライブラリは `specs/<feature>/design.md` の `### 技術スタック（Technology Stack）`。すべての依存関係はここに書かず、リポジトリの依存定義ファイルを正とする。

> _書き方_: 選ぶと書き方が変わるもの（データの取り出し方、検証のしかた、テストの書き方など）だけを書く。理由には、他の候補ではなくこれを選んだ決め手を書く。挙げた区分に当てはまらないものは、最終行と同じ形で足す。

- **ORM / クエリ / マイグレーション**: 画面は MyBatis 3.4.5 ＋ mybatis-spring 1.3.1（SQL は Mapper XML）、バッチは GreenEARTH の仮想エンティティ（GDBVirtualEntity。VE）。マイグレーションのツールは無い — 画面は既存 wing の方式（`wing/pom.xml`、`wing/src/main/resources/servlet-context.xml`）、バッチは回答 2 の指定
- **バリデーション**: 専用ライブラリの注釈は使わず、Service の `checkXxx` で `BindingResult.rejectValue` にエラーを積む手書き方式（共通部品は `wing/src/main/java/jp/co/kccs/wt/common/utils/ValidationUtils.java`）。依存の hibernate-validator 5.0.1 の注釈は使われていない — 既存 wing の実装に合わせる（REQ-045）。入力検証は Service の `checkXxx` で `BindingResult.rejectValue` にエラーを積む方式とし、Bean Validation の注釈は使わない（Phase 2 ゲート 2 回目 指摘15 の修正指示）
- **テスト**: JUnit 4.12 ＋ spring-test（自動テストを書く場合） — 回答 4
- **認証**: 専用ライブラリは使わない。独自のフォームログインと DB のセッション表（ZSESSION）で行う（Spring Security は使っていない） — 既存 wing の方式（`wing/src/main/java/jp/co/kccs/wt/common/service/LoginService.java`・`SessionService.java`）
- **HTTP クライアント**: 使わない — 外部 API の呼び出しが無い（`architecture.md` の `### 外部 API / 外部システム`）
- **リトライ / 外部依存の遮断**: 専用ライブラリは使わない — 外部依存の呼び出しが無い。DB 接続と行ロックの再試行は既存の設定で行う（`non-functional.md` の `### リトライ`）
- **帳票出力**: Excel テンプレート方式。原本の Excel（.xlsx）をコピーして値を設定し、PDF に変換する。JasperReports は使わない（wing/pom.xml に依存はあるが使われていない） — 計画了承時の人間確定事項、回答 3
- **Excel 編集**: Apache POI 3.17（poi と poi-ooxml。テンプレートは .xlsx。wing/pom.xml に追加する） — 回答 3・回答 Q-STR-102。既存の POI 3.1（`WTX/WEB-INF/lib/`）は .xls 専用で wing には無い
- **QR コード生成**: zxing の core と javase 3.4.1（wing/pom.xml に追加し、画像を生成して帳票に貼る） — 回答 Q-STR-102。計画了承時と回答 3 の「zxing core 3.2.1」は、回答 Q-STR-102 で 3.4.1 に訂正された
- **PDF 変換**: jodconverter 2.2.1。サーバー上の OpenOffice（localhost の 8100 番ポート）に接続して、値を設定した Excel を PDF に変換する（wing/pom.xml に追加する） — 回答 Q-STR-102
- **ログ**: 画面は log4j2 2.12.4、バッチは log4j 1.2.14（commons-logging 経由） — 既存の設定（`wing/src/main/resources/log4j2.xml`、`WTX_Batch/config/ge-framework.properties`）
- **ボイラープレート削減**: Lombok 1.16.18（`@Data` 等。provided） — 既存 wing のクラスの書き方（`wing/pom.xml`）

## 開発環境

> 開発を始めるために各自の手元へ用意するものと、その運用を確定させる節。\
> _分担_: 実行するコマンドは `## 共通コマンド`、Lint や CI の設定値はリポジトリの設定ファイル。

> _書き方_: 誰の手元でも同じように必要になるものだけを書く。個人の好みで変えてよいものは書かない。

### 必須ツール

> 開発を始めるために各自の環境へ入れておくものを確定させる節。\
> _分担_: 実際に叩くコマンドは `## 共通コマンド`。ここには何を入れるかだけを書く。

> _書き方_: 入っていないと作業が始められないものだけを書く。バージョンには、揃えないと動作が変わるものだけ具体的な値を書く。

| ツール | バージョン | 用途 |
| --- | --- | --- |
| JDK | 1.7（1.7.0.55） | コンパイルと実行（回答 6） |
| Maven（Maven Wrapper） | 3.3.9 | wing のビルド（`wing/.mvn/wrapper/maven-wrapper.properties`） |
| Apache Tomcat | 7.0.53 | wing の実行（回答 6） |
| OpenOffice | 本番サーバーに導入済みのものに従う | 帳票の PDF 変換。Tomcat と同じアプリケーションサーバーに常駐させ、localhost の 8100 番ポートで待ち受ける（Phase 2 ゲート 2 回目 指摘14 の修正指示） |
| Eclipse | — | 既存のプロジェクト設定（`.project`・`.classpath`・`.settings/`）による開発。WTX・WTX_Batch・WTX_Common の依存はここで解決する |

### 推奨 OS / IDE

> 開発環境として推奨するものを確定させる節。

> _書き方_: 推奨する理由が動作の再現性にある場合（この OS でしか検証していない、など）は、その旨も書く。

- OS: Windows 11（クライアント環境と同じ。起動スクリプトが .bat で、文字コードが Windows-31J のため — 回答 Q-STR-103）
- IDE: Eclipse、推奨拡張: Checkstyle プラグイン（`.checkstyle`）、Tomcat プラグイン（`WTX/.tomcatplugin`）

### Git 戦略

> ブランチの切り方から取り込み方までの運用を確定させる節。\
> _分担_: マージの条件と品質ゲートは `## 開発標準`、CI で何を必須にするかは `### CI 統合`、本番リリースと障害対応は `non-functional.md` の `## デプロイ / リリース` と `## 運用・障害対応`、シークレットの扱いは `security.md` の `## シークレット管理`。

> _書き方_: 保護ブランチの条件には、直接 push を禁じるか、レビューを必須にするか、CI のどの確認を通す必要があるかを書く。リリースタグには、付ける形式を実例で示す（`v1.2.3` のような形）。

- **ブランチ運用モデル**: 案件ごとに `PJ<番号>_develop` ブランチを作り、案件の完了後に `master` へマージする。実際のソース管理は Backlog の Git（ABA603）で行う（回答 5）
- **保護ブランチ**: `master`（回答 5）
- **保護ブランチの条件**: <PROTECTED_BRANCH_RULE>（不要：Backlog の既存の開発運用に従う — 回答 Q-STR-104）
- **マージ方法**: 案件の完了後に案件ブランチを `master` へマージする（回答 5）
- **リリースタグ**: <RELEASE_TAG_CONVENTION>（不要：リリースタグは使わない — 回答 5）

#### 運用ルール一覧

> ブランチ・コミット・レビュー依頼の名前と単位を確定させる節。

> _書き方_: 例には、そのまま真似できる実例を書く。禁止事項には、あとから取り消しにくい操作を書く。

| 項目 | 運用ルール |
| --- | --- |
| **ブランチ名** | `PJ<番号>_develop`（案件ごとに 1 本。回答 5） |
| **仕様管理（spec）** | `steering/`・`specs/`・`docs/` はこのリポジトリで管理し、承認したらコミットする（回答 Q-STR-104） |
| **コミット** | コミットメッセージは「課題キー＋内容」とする。例 `ABA603-6249 納品物取込`（回答 5） |
| **PR（プルリクエスト）** | <PR_RULE>（不要：Backlog の既存の開発運用に従う — 回答 Q-STR-104） |

**禁止事項:**

- <GIT_PROHIBITED_PRACTICE_N>（不要：Backlog の既存の開発運用に従う — 回答 Q-STR-104）

## 共通コマンド

> このリポジトリで変更を確かめるときの標準手順を確定させる節。人も CI も実装を手伝うエージェントも、ここを起点にする。\
> _分担_: いつ何を必須にするかは `### CI 統合`。ここには実行するコマンドだけを書く。

> _書き方_: **手元で実際に成功したコマンドだけ**を書く。置き換えていない箇所や、動作を確かめていないコマンドを残さない。

> _確認状況_: 以下のコマンドは人間の回答（回答 Q-STR-105）による。この端末には Java と Maven が無いため、いずれも未実行で、成功を確認していない（回答 Q-STR-105 で「未確認と書いてよい」とされた）。

```bash
# 依存インストール（wing/lib の社内 jar をローカルリポジトリへ登録する。未確認）
mvn -f wing/pom.xml clean

# ローカル開発（未確認）
mvn -f wing/pom.xml tomcat7:run

# ビルド（未確認。WTX 系は各フォルダの build.xml）
mvn -f wing/pom.xml package
ant -f <各フォルダ>/build.xml build

# テスト（全体。未確認）
mvn -f wing/pom.xml test

# テスト（単一ファイル。未確認）
mvn -f wing/pom.xml test -Dtest=<クラス名>

# Lint / フォーマット
<CMD_LINT>   # 不要：Lint は Eclipse の Checkstyle プラグインで行い、コマンドは持たない — 回答 Q-STR-105
<CMD_FORMAT>   # 不要：フォーマットは行わない — 回答 Q-STR-105

# 型チェック
<CMD_TYPECHECK>   # 不要：Java のコンパイルで型を検査する — 回答 Q-STR-105
```

## 開発標準

> フィーチャーを実装するときに、人もエージェントも守る決まりを確定させる節。\
> _分担_: 細かい設定はリポジトリの Lint と CI の設定ファイルを正とする。品質ゲートの具体的な閾値は `### カバレッジ目標`、マージの条件は `### Git 戦略`。

> _書き方_: 設定ファイルで機械的に確認できないものだけを書く。品質ゲートには、何を満たせば次へ進めるかを書く。

- **型安全**: Java の静的型に従い、`Map` による型の無い受け渡しを新しく増やさない（回答 Q-STR-106）
- **API 境界**: 画面以外から呼ばれる API を設けない（回答 7）。画面と業務ロジックの境界は Controller と Service（`architecture.md` の `## レイヤーと依存ルール`）
- **品質ゲート**: 自動テストは必須にしない。テストは工程ごとの試験仕様書で行う（回答 4）。追加の条件は無く、Checkstyle（`kccs-checkstyle-2.0.1.xml`）に通すことだけとする（回答 Q-STR-106）
- **レビュー**: 既存の開発運用に従う（回答 Q-STR-106）

## 命名規則

> 識別子・ファイル名などの名前の付け方を確定させる節。\
> _分担_: ディレクトリ構成と別名は `architecture.md` の `## ディレクトリ構成` と `## インポート / パスエイリアス（import / path alias）`。テーブル名とカラム名は `database.md` の `## 命名規則`。

> _書き方_: 対象には、変数、関数、クラス、ファイル、定数など、名前の付け方が変わる単位を書く。例には、そのまま真似できる実例を書く。

| 対象 | 規約 | 例 |
|---|---|---|
| 画面ID | `G` ＋ サブシステム（`WTG`）＋ 3 桁の番号。既存の画面ID体系に従う（REQ-004） | `GWTG060` |
| プログラムID（画面） | `P` ＋ サブシステム ＋ `O` ＋ 3 桁の番号（REQ-004） | `PWTGO090` |
| プログラムID（バッチ） | `P` ＋ サブシステム ＋ `B` ＋ 3 桁の番号（REQ-004） | `PWTGB090` |
| 帳票ID | `R` ＋ サブシステム ＋ 3 桁の番号 | `RWTG070`（回答 3） |
| 画面のクラス（wing） | プログラムID を先頭大文字・以降小文字にし、種別を付ける（`Controller` / `Service` / `Mapper` / `Form`）。`@FuncID` にはプログラムID を大文字で書く | `Pwtgo005Controller`・`Pwtgo005Service`・`@FuncID("PWTGO005")`（`wing/src/main/java/jp/co/kccs/wt/function/wtg/wtg002/`） |
| 画面の補助クラス（wing） | プログラムID ＋ 用途 ＋ `Info` など | `Pwtgo005CondInfo`（同上 `bean/`） |
| バッチのジョブクラス | プログラムID ＋ `Job`。定数クラスは ＋ `Const`、チェック部品は ＋ `CheckUtils` | `PWTGB030Job`・`PWTGB030Const`・`PWTGB040CheckUtils`（`WTX_Batch/src/jp/co/kccs/wt/wtg/`） |
| パッケージ（wing） | `jp.co.kccs.wt.function.<サブシステム小文字>.<機能ID小文字>.<層>`。層は `controller` / `service` / `mapper` / `form` / `bean` | `jp.co.kccs.wt.function.wtg.wtg002.controller` |
| パッケージ（バッチ） | `jp.co.kccs.wt.<サブシステム小文字>.<機能ID小文字>` | `jp.co.kccs.wt.wtg.wtg030` |
| 画面テンプレート | `WEB-INF/pages/<サブシステム>/<機能ID>/<プログラムID小文字>.html` と、スクリプト用の `<プログラムID小文字>Script.html` の組 | `pages/wtg/wtg002/pwtgo004.html` |
| Mapper XML | `src/main/resources/jp/co/kccs/wt/function/<サブシステム>/<機能ID>/<Mapper クラス名>.xml` | `jp/co/kccs/wt/function/wtg/wtg002/Pwtgo005Mapper.xml` |
| URL | `/<機能ID小文字>` ＋ `/<アクション>`。アクション名は `search` / `update` / `regist` / `delete` / `execute` / `download` など | `/wtg002/edit`・`/wtg002/payUpdate` |
| 定数 | 大文字と `_`（checkstyle の ConstantName） | `PARAM_SESSION_KEY` |
| パッケージ名の文字 | 小文字と数字（checkstyle の PackageName `^[a-z]+(\.[a-z][a-z0-9]*)*$`） | `jp.co.kccs.wt.function.wtg` |
| メッセージキー | `<分類>-<6 桁>`（`messages.properties`） | `DS-000001`・`GEF-000000` |

## コード規約

> 自動での確認に任せられないコーディング方針を確定させる節。

> _書き方_: Lint ツールやフォーマッタが機械的に直せるもの（字下げの幅、行末の記号など）は書かない。判断が必要なもの（どこまでを 1 つの関数にするか、いつコメントを書くかなど）を書く。

- **既存規約への準拠**: 既存 WiNG のコーディング規約に従う（REQ-045）。機械的な確認は `WTX/CodeStyle/kccs-checkstyle-2.0.1.xml`（wing は `kccs-checkstyle-2.0.1_bugfix`。`wing/.checkstyle`）で行う
- **Javadoc**: クラス・メソッド・フィールドに Javadoc を書く（checkstyle で必須）
- **ファイル冒頭のヘッダ**: システム名・プログラムID・プログラム名・変更日・計画書No・変更者・変更理由を書く（例 `WTX/WEB-INF/src/jp/co/kccs/wt/wtb/wtb020/PWTBO021Action.java` の冒頭）
- **メソッドとファイルの長さ**: メソッドは 150 行以内、ファイルは 2000 行以内を目安にする（checkstyle は警告）
- **例外の受け方**: 例外は具体的なクラスで受ける（checkstyle の IllegalCatch。最後に受け止める箇所は `## 例外処理`）
- **トランザクション**: Service はクラスに `@Transactional(readOnly = true)` を付け、更新するメソッドだけに `@Transactional` を付ける（`wing/src/main/java/jp/co/kccs/wt/function/wtg/wtg002/service/Pwtgo005Service.java`）
- **排他制御**: 更新対象の `ExclusiveFG` を比較し、一致しなければ `ExclusiveException` を投げる（`wing/src/main/java/jp/co/kccs/wt/function/wte/common/service/WTEValidateService.java`）
- **<CODE_RULE_TOPIC_N>**: <CODE_RULE_DETAIL_N>（不要：追加のコード規約は無い — 回答 Q-STR-106）

## 例外処理

> 実装レベルでの例外の扱いを確定させる節。\
> _分担_: エラーの区分と共通レスポンス形式、API としての約束は `api-standards.md` の `## エラーハンドリング（API 契約）`。ログ・通知・再実行・監視は `non-functional.md` の `## 信頼性・観測性`。

> _書き方_: どの機能にも共通する扱いだけを書く。

### 例外処理フロー

> 発生した例外を、各層でどう扱い、上の層へどう渡すかを確定させる節。\
> _分担_: `requestId` や `traceId` といった識別子を呼び出し先へ引き継ぐ扱いは `non-functional.md` の `#### トレース ID / リクエスト ID の伝播`。フィーチャー固有の例外クラス一覧は `specs/<feature>/design.md` の `## 機能固有のエラー処理（Error Handling）`。

> _書き方_: 箇所には、データ取得、業務ロジック、要求を受け取る場所など、例外が通過する層を書く。方針には、その層で握りつぶすか、包み直すか、そのまま上へ渡すかを書く。

| 箇所 | 方針 |
| --- | --- |
| 画面：入力チェック（Service の `checkXxx`） | 例外にせず `BindingResult` にメッセージキー付きでエラーを積み、Controller が同じ画面へ戻す |
| 画面：業務ロジック（Service） | 業務上の失敗は `ApplicationException` の派生（排他は `ExclusiveException` など）をメッセージキー付きで投げ、そのまま上へ渡す |
| 画面：データ取得（Mapper） | 捕まえずに上へ渡す（Spring のトランザクションでロールバックされる） |
| 画面：要求を受け取る場所（Controller） | 個別に捕まえず、グローバルハンドラに任せる |
| バッチ：DB アクセス・ファイル処理 | `SQLException` などは `DSExceptionUtils.createLoggingException` で `KCLoggingException` に包み直して上へ渡す（`WTX_Common/ds/jp/co/kccs/ds/util/DSExceptionUtils.java`） |
| バッチ：ジョブ（`execute()`） | `KCLoggingException` と `Exception` を受け、ロールバック → `logError` → `CODE_ERROR` を返す。それ以外の例外は `GEF-000000` に包む（`WTX_Batch/src/jp/co/kccs/wt/wtg/wtg030/PWTGB030Job.java`） |

### 例外クラス命名規約

> 例外クラスの名前の付け方と、基底となるクラスの構成を確定させる節。\
> _分担_: 一般的な命名規則は `## 命名規則`。ここには例外クラス特有のものだけを書く。

> _書き方_: 種別には、業務上の失敗、入力の誤り、外部連携の失敗など、扱いが変わる単位を書く。ルールには、接尾辞の付け方や、どこまで細かく分けるかを書く。

| 種別 | 命名 / 用途 |
| --- | --- |
| 画面の基底 | `ApplicationException`（`RuntimeException` を継承。メッセージキーの既定は `GEF-000000`。`wing/src/main/java/jp/co/kccs/wt/common/exception/`） |
| 画面の派生 | `ExclusiveException`（排他）、`InvalidAccessErrorException`（権限なし）、`InvalidParamErrorException`（不正パラメータ）、`CSRFTokenErrorException` など（同上） |
| バッチの基底 | `KCLoggingException`（`Exception` を継承。コード・説明・キー項目を持つ。`WTX_Common/kyocera/jp/co/kccs/kyocera/log/KCLoggingException.java`） |

| # | ルール |
| --- | --- |
| 1 | 例外クラス名は事象を表す名詞 ＋ `Exception` とする |
| 2 | 利用者に示す文言は例外クラスに持たせず、メッセージキー（`messages.properties`）で引く |

### グローバルハンドラ

> どの層でも捕まえられなかった例外を、最後に受け止める仕組みを確定させる節。\
> _分担_: そこから返すレスポンスの形は `api-standards.md` の `### 共通エラー形式`。ここには受け止める仕組みだけを書く。

> _書き方_: 方針には、どこまでをここで受け止め、どこから先を各層に任せるかを書く。ルールには、利用者へ返す情報と、記録だけに残す情報の分け方を書く。

- **方針**: 画面では、Controller から出たすべての例外を `HandlerExceptionResolver` の実装で受け止め、エラー画面へ遷移させる。バッチでは、ジョブの `execute()` で受け止めて終了コードとバッチログに反映する

| フレームワーク | 実装場所 |
| --- | --- |
| Spring MVC（wing） | `wing/src/main/java/jp/co/kccs/wt/common/handler/ExceptionResolver.java`（`@Component`） |
| batch-engine（WTX_Batch） | 各ジョブの `execute()` と `WTX_Batch/src/jp/co/kccs/greenearth/javakit/frame/batch/engine/WTActiveTask.java` |

| # | ルール |
| --- | --- |
| 1 | 利用者にはエラーの種類・エラーコード・メッセージ（`messages.properties` から引いた文言）だけを示す |
| 2 | スタックトレースはログ（`log.error`）にだけ残し、画面に出さない |

## テスト方針

> テストの原則・配置・命名・種類・書き方・カバレッジ目標を確定させる節。\
> _分担_: フィーチャーごとの**何を確かめるか**は `specs/<feature>/design.md` の `## テスト戦略（Testing Strategy）`、**完了の条件**は `specs/<feature>/tasks.md`。実行コマンドは `## 共通コマンド`、確認するエラーコードの形式は `api-standards.md` の `### 共通エラー形式`。

> _書き方_: 全フィーチャーに共通するルールだけを書く。

### 基本方針

> テストで何を優先するかの原則を確定させる節。後続の各節の判断軸になる。

> _書き方_: 1 項目 1 行で列挙する。どこまで書けば十分とするかなど、判断に迷う場面を想定して書く。

- 自動テストは必須にしない。テストは工程ごとの試験仕様書で行う（回答 4）
- 自動テストを書く場合は JUnit 4.12 と spring-test を使う（回答 4）

### 配置 / 命名

> テストファイルをどこに置き、どう名付けるかを確定させる節。\
> _分担_: フィーチャーごとのテストファイル一覧は `specs/<feature>/tasks.md` の `## タスク一覧` と `specs/<feature>/design.md` の `## テスト戦略（Testing Strategy）`。ここにはリポジトリ全体に共通する置き方と名前の付け方だけを書く。

> _書き方_: どのフィーチャーにも当てはまるものだけを書く。

#### 配置パターン

> テストファイルの置き場所を、主に使う形と例外的に使う形の 2 通りで確定させる節。

> _書き方_: 1 行目には基本として使う形を書き、2 行目にはそれで収まらない場合の形を書く。例には、そのまま真似できるパスを書く。備考には、その形を選ぶ条件を書く。配置に関するルールには、対象と同じ場所に置くか専用のディレクトリにまとめるかの判断や、どちらにも当てはまらない場合の扱いを書く。

| パターン | 例 | 備考 |
| --- | --- | --- |
| `src/test/java` の、対象クラスと同じパッケージに置く | `wing/src/test/java/jp/co/kccs/wt/function/wtg/wtg002/service/Pwtgo005ServiceTest.java` | 自動テストを書く場合（回答 4） |
| <TEST_LAYOUT_PATTERN_ALT>（不要：自動テストは必須でないため、基本の置き場所以外は定めない — Phase 2 ゲート 1 回目 指摘1 の修正指示、回答者 Junichi Noumi） | <TEST_LAYOUT_EXAMPLE_ALT>（不要：自動テストは必須でないため、基本の置き場所以外は定めない — Phase 2 ゲート 1 回目 指摘1 の修正指示、回答者 Junichi Noumi） | <TEST_LAYOUT_NOTE_ALT>（不要：自動テストは必須でないため、基本の置き場所以外は定めない — Phase 2 ゲート 1 回目 指摘1 の修正指示、回答者 Junichi Noumi） |

| # | 配置に関するルール |
| --- | --- |
| N | <TEST_LAYOUT_RULE_N>（不要：自動テストは必須でないため — 回答 Q-STR-107） |

#### 命名

> テストの名前の付け方を確定させる節。失敗したときに、何が壊れたかが名前だけで分かるようにする。

> _書き方_: 例には、そのまま真似できる実例を書く。`describe` と `it` は、つなげて読んだときに 1 つの文になる形を示す。

| 対象 | ルール | 例 |
| --- | --- | --- |
| ファイル | `<クラス名>Test.java`（回答 4） | `Pwtgo005ServiceTest.java` |
| describe | <TEST_DESCRIBE_NAMING_RULE> | <TEST_DESCRIBE_NAMING_EXAMPLE>（不要：自動テストは必須でないため — 回答 Q-STR-107） |
| it / test | <TEST_IT_NAMING_RULE> | <TEST_IT_NAMING_EXAMPLE>（不要：自動テストは必須でないため — 回答 Q-STR-107） |
| 通しテスト（E2E）のシナリオ | <TEST_E2E_NAMING_RULE> | <TEST_E2E_NAMING_EXAMPLE>（不要：自動テストは必須でないため — 回答 Q-STR-107） |

| # | 命名に関する補足 |
| --- | --- |
| N | <TEST_NAMING_NOTE_N>（不要：自動テストは必須でないため — 回答 Q-STR-107） |

### テスト種類

> テストの種類ごとに、どこまでを確かめる範囲とするかを確定させる節。\
> _分担_: フィーチャーごとに何をどの種類で確かめるかは `specs/<feature>/design.md` の `## テスト戦略（Testing Strategy）`。

> _書き方_: 範囲には、どこからどこまでを本物で動かすかを書く。選定基準には、迷ったときにどの種類を選ぶかの判断のしかたを書く。

| 種類 | 範囲 | モック方針 | 速度目標 |
| --- | --- | --- | --- |
| <TEST_TYPE_N> | <TEST_TYPE_SCOPE_N> | <TEST_TYPE_MOCK_POLICY_N> | <TEST_TYPE_SPEED_TARGET_N>（不要：自動テストは必須でないため — 回答 Q-STR-107） |

| # | 選定基準 |
| --- | --- |
| N | <TEST_SELECTION_CRITERIA_N>（不要：自動テストは必須でないため — 回答 Q-STR-107） |

### 構造（AAA）

> 1 つのテストの組み立て方を確定させる節。準備（Arrange）、実行（Act）、確認（Assert）の順に書き、1 つのテストで 1 つの振る舞いだけを確かめる。

> _書き方_: 3 つの区切りをどう表すか（空行で分ける、コメントを付けるなど）を書く。1 つのテストに複数の確認を入れてよい条件があれば、それも書く。

| # | ルール |
| --- | --- |
| N | <TEST_AAA_RULE_N>（不要：自動テストは必須でないため — 回答 Q-STR-107） |

### モック / フィクスチャ / データ

> 本物の代わりに使う偽物（モック）と、あらかじめ用意しておくデータ（フィクスチャ）の扱いを確定させる節。

> _書き方_: 何を偽物に置き換えてよく、何は本物のまま動かすかを書く。置き換えすぎると、動いているのに壊れているテストになるため、その線引きを書く。

| # | 方針 |
| --- | --- |
| N | <TEST_MOCK_POLICY_N>（不要：自動テストは必須でないため — 回答 Q-STR-107） |

### テストデータ管理

> テストで使うデータの作り方と後始末を確定させる節。\
> _分担_: 各環境に置くデータの方針は `non-functional.md` の `## 環境`。ここにはテスト実行時のデータだけを書く。

> _書き方_: 種類には、毎回作るもの、あらかじめ用意しておくもの、本番から持ってくるものなどを書く。本番のデータを使う場合は、加工の要否も書く。

| 種類 | 方針 |
| --- | --- |
| 総合テスト・受入テスト用のマスタデータと取込データ | 整合性のとれているデータを発注者が提供する（REQ-061） |

### カバレッジ目標

> テストがどれだけコードを通っているかの目標値を確定させる節。\
> _分担_: 数値の目標はこの節を正とする。`specs/<feature>/design.md` の `## テスト戦略（Testing Strategy）` には**何をどこまで確かめるか**だけを書き、割合の数値を書かない。閾値を実際に効かせる設定は `## 共通コマンド` とリポジトリの CI 設定。

> _書き方_: 区分には、全体、追加した差分、重要な領域など、目標を変える単位を書く。運用ルールには、目標に届かない場合の扱いと、対象から外してよい範囲を書く。

| 区分 | 目標 |
| --- | --- |
| <COVERAGE_SCOPE_N> | <COVERAGE_TARGET_N>（不要：カバレッジ目標は設けない。既存に無いため — 回答 4） |

| # | カバレッジ運用ルール |
| --- | --- |
| N | <COVERAGE_POLICY_N>（不要：カバレッジ目標は設けない。既存に無いため — 回答 4） |

### CI 統合

> 自動実行のなかで、いつ何を必須にするかを確定させる節。\
> _分担_: 実行するコマンドは `## 共通コマンド`、ワークフローの定義はリポジトリの CI 設定。マージの条件は `## 開発標準` および `### Git 戦略` と食い違わないようにする。

> _書き方_: 項目には、実行するタイミング（PR を出したとき、マージした後など）を書く。内容には、失敗したときに先へ進めなくするかどうかを書く。

| # | 項目 | 内容 |
| --- | --- | --- |
| N | <CI_TEST_ITEM_N> | <CI_TEST_POLICY_N>（不要：CI は設けない。既存に無いため — 回答 4） |

### 完了条件との接続

> テストと、タスクが終わったと言える条件を、どう結びつけるかを確定させる節。\
> _分担_: 各タスクの完了条件は `specs/<feature>/tasks.md`、受け入れ基準は `specs/<feature>/requirements.md` の `#### 受け入れ基準（Acceptance Criteria）` が正となる。

> _書き方_: 受け入れ基準の ID とテストをどう対応づけるかを書く。1 つの基準に対してテストがない状態を許すかどうかも書く。

| # | 接続ルール |
| --- | --- |
| 1 | 試験仕様書の各ケースには、対応する受け入れ基準の番号を書く（回答 Q-STR-107） |

---

_技術的な前提と標準コマンドをプロジェクト全体で固定する文書。_
