# feature最終検査の可読レポート

レポートの単位はテストスイート／モジュールであり、作業タスクではない。
タスク分割・check_ids・既存テスト生成物の目的は変更しない。タスクのRED/GREEN/VERIFYでは
以下のレポート処理を実行しない。独立した設定をfeature最終の`implementation-tools`だけが読む。

Phase 8の意味検査では、今回追加した生成レポートの表示・書式だけを評価対象から外す。
範囲はimplement-checkの共通指示に従う。案件のテスト・実行設定・導入補助は除外せず、
レポートの結果・coverageも検査証跡として使う。必須の実行・出力・証跡の機械検査は維持する。

## 設定場所と実行順

ツールの選定は既存のsteering/tech.mdとdesignの技術スタック・テスト戦略・設計判断に記録する。
必要な導入作業は通常の準備タスクに含め、Phase 7のタスク一覧の最終承認で確認する。
既存環境・既存準備タスク・先行featureで足りる場合は専用タスクを増やさない。
reporting設定の追加だけのために業務タスクを変更しない。導入が必要なら最終検査前の承認済み作業で完了させる。
checks/postprocessは導入済みのOSSを使う。パッケージの自動取得・依存同期を伴う実行方式を避け、
不足時は診断して停止する。最終検査の中でインストールを始めない。

`.aidd/implementation/reporting/<feature>.json`を最終検査までに用意する。
タスク用の`config/<feature>.json`とは別で、タスク終了後に追加してもタスク再実行を要求しない。
ただし、実コードや既存タスクが使用するテスト・検証設定を変えれば、従来の変更検出の対象になる。
最終検査用の設定だけを用意するために、承認済みtasksやテストの粒度を変えてはならない。
報告専用のwrapper・補足資料を後から追加する場合は、既存タスクの編集範囲／検証入力を
変更せず、専用の`reporting/`等へ置いてreporting設定のverification_pathsで管理する。
既存の検証対象内に新しいテストやファイルを追加すれば従来の変更検出が働く。
進行中のタスクの外部へファイルを追加せず、完了したタスク間または最終検査前の境界で準備する。

1. 最終検査の開始時に、レポート設定・仕様説明・検証入力の版をreview.jsonへ固定する。
2. 既存feature_checksを実行する。その後、reportingのchecksを宣言順に実行する。
3. レポート用checkごとに空の試行フォルダを割り当て、OSSを実行する。
4. 主コマンドが失敗してもpostprocessを実行し、取得できる出力と診断を保存する。
5. 可読結果・coverage・仕様コピー・付属ファイルを保存し、完全なファイル一覧とハッシュをtools.jsonへ記録する。
6. 独立検査、人間レビュー、承認、完了で同じ出力を再検証する。

アクションやフローは追加しない。レポート生成のためにタスクを新設・再分割しない。
正式レポートのためのスイート再実行は許容する。タスク途中の異なる版の結果を足し合わせない。
既存ランナーの専用report設定・CLIオプションで出力だけ追加する方式を優先する。
別のランナーへの乗換え、テスト種別の変更、coverageの対象変更を自動的に行わない。

実行タイミングの分離は、テストケースやassertionの複製を意味しない。既存テストをそのまま収集するか、
必要なら既存ケース・検証関数を呼ぶ薄いadapterを使い、参照元もverification_pathsへ含める。
追加の観測用スイートが異なる用途を持つ場合は、その範囲と既存検査との関係を仕様に記す。
報告用コピーだけが古くなる構成を避ける。既存テストを修正した場合の再検証は従来どおり必要である。

## 作成・閲覧時の目安

OSSのケース名／パラメータIDと仕様から、入力・型・期待する結果や拒否理由を識別できるようにする。
文字列と数値、boolと整数が同じ表示になる場合は、OSS標準の明示IDや表示名を使う。
全入力をIDへ詰め込む必要はなく、大きな入力・秘密値は安全なケース名と仕様参照で表す。
reportsのscopeは実スイート・要求境界・coverageの対象と照合し、未実施のCLI・結合検査等を含めない。
これらの表示・表記は作成・閲覧時の目安とし、表記だけを意味検査の指摘の根拠にしない。
以下は案件テストの評価として維持し、レポート追加を理由に評価基準を変えない。
要件の境界は実際の値で照合し、別の入力でも同じ境界を満たす既存ケースを見落とさない。
coverageは通過経路を表すもので、正しい期待値・拒否理由をassertした証明にはならない。
例外理由・エラーコード等が契約にある場合はその内容も検証する。文言の完全一致が契約でなければ要求しない。
複数条件を同時に破る入力では、未規定の検査順序を前提に唯一の拒否理由を要求しない。
言語横断のケース台帳・独自coverage計算・新規ゲートは追加しない。

## 設定例（Python / pytest）

以下は例。ツールの版と対象範囲を確認して案件へ合わせる。単体テスト仕様は既存資料を優先し、
不足する前提・入力・期待結果・要求対応だけを補う。専用の全ケースJSONは作らない。

```json
{
  "schema": 1,
  "feature": "booking",
  "specifications": ["tests/booking/specification.md"],
  "verification_paths": ["tests/booking/", "pyproject.toml", "requirements-test.txt"],
  "checks": [
    {
      "id": "booking-unit-report",
      "argv": [".venv/bin/python", "-m", "pytest", "tests/booking", "--junitxml={report_dir}/junit.xml", "--html={report_dir}/tests.html", "--self-contained-html", "--cov=src.booking", "--cov-report=html:{report_dir}/coverage"],
      "cwd": ".",
      "timeout_seconds": 180,
      "reports": [
        {"role": "tests", "path": "tests.html", "scope": "bookingの単体テスト", "tool": "pytest 8.4.2 / pytest-html 4.1.1"},
        {"role": "coverage", "path": "coverage/index.html", "scope": "src.booking（未ロードのソースも含む）", "tool": "pytest-cov 7.0.0 / coverage.py（案件の固定版を記入）"}
      ],
      "report_files": ["coverage/*.css", "coverage/*.js"],
      "test_results": {"format": "junit", "paths": ["junit.xml"]}
    }
  ]
}
```

Windowsではvenvの実行パス等をそのOSに合わせる。`.coverage`などOSSの中間ファイルは、
専用設定や小さな案件側wrapperで`AIDD_REPORT_DIR`内へ向ける。上記コマンドだけでは
coverageの中間ファイル位置までは変わらない。全生成物を今回の出力先へ向けることを確認する。
案件の既存実行が中間生成物を外へ出す場合は、従来のgenerated_paths規則に従う。
ソースや検証入力を除外して検査を通さない。

- `specifications`: MarkdownまたはHTMLの仕様説明。最終検査時のコピーを報告に含める。
- `verification_paths`: レポート用のテスト・設定・wrapper・依存固定ファイル等。ファイル、または末尾`/`のディレクトリ。入力の欠落・変更を検出する。
- `checks`: レポート生成の単位。タスクIDとの対応付けは不要。複数モジュールは複数checkでよい。
- `argv`: shellを介さない文字列配列。`{python}`はAIDDを実行中のPython。
  `{report_dir}`は引数の一部でも今回専用の絶対パスに置換する。環境変数`AIDD_REPORT_DIR`も同じ値。
- `reports`: 入口ファイルと役割（tests / coverage / quality）、実際の測定範囲、ツール名・版。
  HTMLかMDの一方でよく、同じ内容を両方へ出さない。
- `report_files`: 出力先内に必要な付属ファイル／glob。宣言したglobは1件以上必要。
  全ての生成済みファイルは宣言に関係なく保存・ハッシュ照合する。表示確認は作成側または閲覧者が行う。
- `test_results`: OSSのネイティブなJUnit XMLまたはTRX。相対パス／globを列挙する。
  結果とcoverageの可読入口を併せて要求する。実ケース0件、失敗、エラー、skip、件数不整合は通さない。
  必須ケースの不足や仕様の十分性は、配置やレポート利用の有無を問わず、ランナーの収集設定と独立検査で確認する。
- `postprocess`: 必要な場合だけ、`argv`・`timeout_seconds`・任意の`cwd`を持つコマンドの配列。
  HTML変換やOSSの閾値検査等を置く。実行失敗を後処理の成功で上書きしない。

単体テストcheckはtestsとcoverageを揃える。非コードfeatureでは、全タスクが事前に非コードと
定義されている場合だけ`not_applicable_reason`に理由を記載できる。その場合もspecificationsに
代替検証の内容を記し、既存の必須検証を実行する。テスト失敗後の免除には使わない。
coverageの率はOSSが計算する。対象・除外・分岐計測・閾値を案件で決め、未計測を0/100%にしない。

## 内部品質指標を追加する場合

確認済みのOSS出力を別checkとして追加する。例えばLizardのHTMLへ複雑度・NLOC・引数数を出すなら、
`reports`に`role: "quality"`と`metrics: ["CCN", "NLOC", "parameter_count"]`を記載する。
計測できる指標と可読化できる指標を採用版で確認し、指標定義・対象範囲・既知の限界を仕様説明に記す。
CKのCSVや.NET MetricsのXMLだけでは可読入口を満たさない。既存OSS formatterを優先し、
必要なら限定した表の整形で補う。未対応の凝集度等を独自に計算して埋めない。

解析の採用自体は任意だが、選択してchecksへ定めた実行・出力は必須である。
指標の値を参考扱いにする場合は、計測成功と高い複雑度等の警告を区別できるOSS設定を使う。
基準違反で止める場合はOSSの終了コード／postprocessで判定する。
実行エラーを無条件のexit 0で隠すwrapperは使わない。非ブロッキングの失敗を表す設定は初期版にはない。

## 保存・共有と制約

検査回の`tools.json`にある`summary.path`（ホスト出力の`report_summary`）が入口。
一覧は小さなMDであり、OSSの結果を描き直したダッシュボードではない。
仕様コピー・結果・coverage・quality・付属ファイルは別々でよい。
共有時は`features/<feature>/inspections/<run>/`フォルダ全体を保持する。
動的HTMLの閲覧にHTTPサーバーが必要なら、採用版のOSSの閲覧方法を案件へ記載する。

最終検査の既存checksとレポート本体・後処理のtimeout合計は480秒以内。
重い解析を全て詰め込まず、必要な範囲を選ぶ。必須出力欠落・空ファイル・改変・付属ファイル削除、
構造化結果の不備は停止する。診断MDは成功レポートの代替ではない。
HTMLの意味・画面表示・仕様の十分性やすべての外部資材参照をファイル存在だけで保証しない。
リンク／symlinkを使った別試行への流用は許可しない。未完了のrunning markerの扱いは既存契約に従う。

## 既存案件への適用

タスク用設定が変わらなければ、完了済みタスク証跡はそのまま保持する。
最終検査の開始前にreporting設定を追加する。実行中のdispatchへ資材を上書きしない。
既に最終検査を開始・承認済みの案件は、元の履歴を保存し、未回答dispatchのない境界で
新しい最終検査回へ進む。正規のengine redoは`implement-review`の対象featureだけへ行い、
タスク生成・修正flowをレポート追加のために再実行しない。保存済みflow契約が異なる場合は
実装契約の移行手順を先に適用する。過去の承認を新しい出力の承認として流用しない。
