---
name: task-specification
description: 生成済み単体テストから人の確認用仕様書のケース内容を作り、前回版へ差分を返す。
disable-model-invocation: true
---

## 入力と責務

profile=task-specification-v1。contextのrequest、request_sha256、previous_specification、taskを使う。
これはL4での資料生成であり、仕様書内容の追加レビューではない。実テストを正として説明する。
既存のfeature最終のimplementation-testsによる実テストレビューを代替・省略しない。
MCPレビューは後続のタスクレビュー準備処理が実行する。この仕様書生成では呼び出したり、指摘0件という結果を作ったりしない。

すべて読取り専用。JSONを応答で返し、コード、仕様書ファイル、確認記録、承認状態へ書き込まない。
Markdown化と不変保存は返却後にL4のscriptが行う。タスク完了や人間の判断を代行しない。

## 手順

1. request.targetで今回のタスク・実行・確認回を確認する。inputs.test_filesの全ファイルを読む。
   inputs.shared_files、upstreamの要件・設計と、必要なinputs.codeの実装を読み、実際のテストの
   入力・assertion・fixture・モック・parameter IDを理解する。生成済みコードを読むことが目的であり、
   作者のsummaryやケース名だけから期待値を補完しない。
2. 現在のスイートの全ケースをcasesに列挙する。タスクの変更ケースだけに限定しない。
   ケースIDは実ランナーの名前・parameter IDを使う。行番号・実行回数をIDに含めない。
   casesの値は入力のtest_filesにある実テストファイルのパス。ケースを持たない補助ファイルは
   non_case_filesへ実理由を記す。全入力ファイルをどちらかに対応付ける。
3. 各ケースのtitle/purpose/requirement/category/preconditions/steps/expected/referenceを記述する。
   文字列は日本語の平文とし、title/category/referenceは1行、他は改行してよい。
   具体的な入力値、操作順、assertionが検査する戻り値・例外・状態・副作用を説明する。
   要件・設計参照は対応が確認できたものだけ記す。実テストが検査していない期待を説明へ足さない。
   パラメータは各IDの値と期待結果を区別する。性質テストは生成範囲・不変条件を説明する。
4. 前回版がある場合、追加ケースだけをadditionsへ入れ、変更が必要な既存ケースはupdatesへ
   その項目だけを入れる。同じテストファイルが変わったケース、shared_files・upstreamの変更を受ける
   ケース、ケースを持たない補助ファイルの追加・削除・変更を受けるスイート内のケース、
   request.correctionsの対象は、説明無変更ならupdatesに空オブジェクトを入れる。
   ケース別入力ハッシュはL4が実ファイルから計算する。前回と今回の入力は保存済みrequestから確認できる。
   前回requestはprevious.execution_idとroundで`.aidd/implementation/runs/<id>/reviews/<round>/request.json`にある。
   無変更ケースの言い換え・並べ替えをしない。入力不変の説明訂正はrequest.correctionsの対象だけ。
   削除したケースはcasesから除く。移動・改名の対応が未確認なら追加／削除として扱う。
5. 元ファイルが欠落・読取不能、または具体的な説明を作れない場合はfailedと理由を返す。
   ケース漏れを「ケースなし」としない。現行の全ケースが削除された等、実際に0件なら
   no_cases_reasonに理由を書く。内容を生成した後に、別の仕様書レビューを起動しない。

## 返却

```json
{
  "status": "completed",
  "target": "request.targetをオブジェクトのまま返す",
  "request_sha256": "context.request_sha256",
  "cases": {"tests/test_booking.py::test_duplicate": "tests/test_booking.py"},
  "non_case_files": {},
  "additions": {
    "tests/test_booking.py::test_duplicate": {
      "title": "同一枠への重複予約を拒否する",
      "purpose": "重複予約の拒否と予約状態の保持を確認する。",
      "requirement": "実際に対応する要件・設計の参照",
      "category": "異常系",
      "preconditions": "枠S1にU1の予約が1件あり、通知先はモック。",
      "steps": "U2がS1を1回予約する。",
      "expected": "実テストで確認する例外、予約件数、通知呼出回数。",
      "reference": "tests/test_booking.py::test_duplicate"
    }
  },
  "updates": {},
  "no_cases_reason": ""
}
```

例の対象と説明は形の参考であり、そのまま製品のケースとして出力しない。
failedは`{status: failed, reason: 実際の生成失敗理由}`を返す。人間の確認回答や承認は含めない。
