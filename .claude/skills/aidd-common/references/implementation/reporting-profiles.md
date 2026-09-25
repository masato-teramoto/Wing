# OSSレポーターの選定と出力対応

共通制御は言語を解釈せず、コマンド、HTML／MDの入口、ネイティブJUnit XML／TRXを扱う。
以下はランナーごとの接続方法。案件の採用版・OS・フレームワーク設定で動作を確認してから必須化する。
対応する指標を事前に確認し、全ツールへ全指標を要求しない。概要は[レポート契約](reporting.md)。

| 系統 | 結果 / coverage | 機械向け結果 | 今回の確認 |
|---|---|---|---|
| Python | pytest-html / pytest-cov | pytestのJUnit XML | pytest 8.4.2、pytest-html 4.1.1、pytest-cov 7.0.0、coverage 7.16.1で実行 |
| JS/TS | Vitest HTML / coverage-v8 | VitestのJUnit XML | Vitest、@vitest/ui、@vitest/coverage-v8 4.0.18で実行 |
| JS/TS（既存Jest） | jest-html-reporter / Jest coverage HTML | jest-junit | Jest 30.5.2、HTML 4.4.2、JUnit 17.0.0で実行。Vitestへの移行は要求しない |
| Java/JVM | Gradle標準HTML、またはMaven Surefire Report / JaCoCo | JUnit XML群 | JUnit 5.13.4、Gradle 8.14.3、Maven 3.9.9／Surefire Report 3.5.5、JaCoCo 0.8.15で実行 |
| C#/.NET（VSTest） | HTML logger / Coverlet + ReportGenerator | TRX | SDK 8.0.425、xUnit 2.9.3／NUnit 4.6.1／MSTest 4.4.1、Coverlet 6.0.4、ReportGenerator 5.5.11で実行 |
| PHP | PHPUnit TestDox HTML / PHPUnit coverage HTML | PHPUnit JUnit XML | PHP 8.4.26、PHPUnit 12.5.35、Xdebug 3.5.1／PCOV 1.0.12で実行 |

追加確認は2026-09-25の小さな合成題材で行った。JS/PythonはmacOS arm64、Java/.NET/PHPはLinux arm64コンテナ。
正常出力、意図的失敗後の出力保持、既存AIDDでの不合格を確認した範囲であり、全フレームワークの対応保証ではない。

## Python

既存のpytest収集設定を使い、`--junitxml={report_dir}/junit.xml`、
`--html={report_dir}/tests.html --self-contained-html`とcoverageのHTML出力を追加する。
coverageの対象は案件の実コード全体を明示し、未ロードのコードも含める。
中間データ`COVERAGE_FILE`も`AIDD_REPORT_DIR`配下へ向ける。
標準unittestのテストはpytestで実行できる場合があるが、収集・fixture差異を確認し、
既存ランナーを自動的に置き換えない。単なるトップレベルスクリプトをテストケース0件のまま成功としない。

## JS/TS

採用版Vitestの別設定に、既存設定を継承してreporters・outputFile・coverageの出力先だけを追加する。
実行コマンド例は`node node_modules/vitest/vitest.mjs run --config vitest.report.config.mjs`。
4.0.18では次の設定で実出力を確認した。最新メジャー版との互換は仮定しない。

```javascript
const output = process.env.AIDD_REPORT_DIR;
// 既存のinclude / environment / setupFiles / alias等を保持したtest設定へ追加する。
const reportOptions = {
  reporters: ['default', 'junit', 'html'],
  outputFile: { junit: `${output}/junit.xml`, html: `${output}/tests/index.html` },
  coverage: { enabled: true, provider: 'v8', include: ['src/**/*.ts'],
    reporter: ['html'], reportsDirectory: `${output}/coverage`, reportOnFailure: true },
};
```

Vitest HTMLは今回のcheckの出力フォルダ（testsとcoverageの親）をHTTPルートにして、
`/tests/index.html`を開く。親階層をルートにすると、内蔵のcoverageリンクが`/coverage/index.html`を
参照して404になることを確認した。reportsの`viewing`へこの閲覧条件も記載する。
Jest案件では、既存Jest設定へHTMLとJUnitのレポーター、coverageReportersのHTMLを追加する。
プロジェクト固有の収集・変換・ブラウザー環境は維持する。

## Java/JVM

GradleならTestタスクのHTML、JUnit XML、JaCoCo HTMLの各出力先を今回専用ディレクトリへ設定する。
テスト後にJaCoCoを生成する場合は、テスト失敗でも実行されるfinalizedBy、または独立した
postprocessを使う。MavenならSurefireのXMLからSurefire ReportとJaCoCo HTMLを生成する。
`test && report`は使わず、基盤のpostprocessへ後処理を登録する。
JUnit XML群は`test_results.paths: ["raw/TEST-*.xml"]`等で指定する。
マルチモジュールの出力はモジュールごとに保存し、coverageの率を平均しない。
固定出力先しか使えない設定では案件側wrapperが実行前に専用出力を初期化し、今回の結果だけをコピーする。
ビルド成果物の用途やタスク計画を、レポートのために変更しない。

## C#/.NET

VSTest構成なら`dotnet test --logger "trx;LogFileName=tests.trx" --logger "html;LogFileName=tests.html"`
に今回の`--results-directory`を追加し、Coverletを案件の既存構成に合わせる。
ReportGeneratorのHTML変換はpostprocessで実行する。
`test_results: {"format":"trx", "paths":["raw/*.trx"]}`と可読入口を宣言する。
Microsoft.Testing.Platformは別の拡張・オプションを持つため、このVSTest設定をそのまま適用しない。

## PHP

既存PHPUnitへ`--log-junit {report_dir}/junit.xml --testdox-html {report_dir}/tests.html
--coverage-html {report_dir}/coverage`を追加する。coverageには対応したXdebug／PCOV等が必要。
対象コード・除外・分岐等は採用版の設定で明示する。機能の無い環境で形式だけ空のcoverageを置かない。
Xdebugの`--path-coverage`は題材でも既定128MBでは停止し、`php -d memory_limit=512M`で成功した。
必要メモリを実測して実行条件に含める。PCOVで確認したのは行coverageで、同じ分岐・経路出力を要求しない。

## 静的解析

Lizard 1.18.0の`-H -o {report_dir}/quality.html -i -1`はPython・TypeScript・Java・C#・PHPで実行確認した。
対象は関数のCCN・NLOC・引数数。HTMLの列名・値はOSSの定義を保持する。
jscpd 5.3.2はJS・Python・Java・C#・PHPの重複をHTMLへ出力できた。閾値違反でもHTMLが残る。
dependency-cruiser 18.4.0は循環と禁止依存を確認できるが、HTML／JSON reporterは違反があっても終了0となる。
必須の依存規則は`--output-type err`で判定し、JSON保存と`depcruise-fmt`のHTML出力をpostprocessへ分ける。
ESLint 10.11.0、Radon 6.0.1、Import Linter 2.15はテキストをMDに包み、元の終了コードを保持して接続した。
ArchUnit 1.5.0／ArchUnitNET 0.13.4は、正常な依存方向と違反の両方をJUnit／TRXで確認した。

CK 0.7.0のCSVは選択列をMD表にでき、CBO・fan-in/out・LCOM*・TCC等を対照クラスで確認した。
TCCを使う場合、第4引数のvariables/fields解析は`true`が必要。`false`では対照クラスのTCCまで0となった。
PhpMetrics 2.11.0は複雑度・規模・結合度のHTMLを確認したが、LCOMは異なるフィールド群を識別できず採用保留。
getter/setterの除外もあるため、出力された0や1をそのまま良好な凝集度と判定しない。
Microsoft.CodeAnalysis.Metrics 5.6.0の配布物は.NET Framework 4.7.2用exeで、Linux／SDK 8では起動できなかった。
XML／MDの実出力とWindows環境は未確認。これをクロスプラットフォームの必須ツールへ設定しない。
LCOMの方式を混ぜず、未対応や未検証を0で代替しない。各案件では採用版・構文・対象範囲を再確認する。

## 公式資料

- [pytest-html](https://pytest-html.readthedocs.io/en/latest/user_guide.html)、[pytest-cov](https://pytest-cov.readthedocs.io/en/latest/reporting.html)
- [Vitest reporters](https://vitest.dev/guide/reporters)、[coverage](https://vitest.dev/guide/coverage.html)、[Jest HTML reporter](https://github.com/Hargne/jest-html-reporter)
- [Gradle Test](https://docs.gradle.org/current/userguide/java_testing.html)、[Surefire Report](https://maven.apache.org/surefire/maven-surefire-report-plugin/)、[JaCoCo](https://www.jacoco.org/jacoco/trunk/doc/report-mojo.html)
- [VSTest](https://learn.microsoft.com/en-us/dotnet/core/tools/dotnet-test-vstest)、[ReportGenerator](https://github.com/danielpalme/ReportGenerator)
- [PHPUnit](https://docs.phpunit.de/en/12.5/textui.html#logging)、[Lizard](https://github.com/terryyin/lizard)

公式資料の最新版と固定した採用版の差は、導入時に確認する。
