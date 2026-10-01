# 実テストからの単体テスト仕様書とタスク末尾確認

生成済みテストを入力に、L4が人の確認用仕様書を生成・差分更新する。仕様書内容の独立レビューは追加しない。
既存のfeature最終の実テストレビューは維持する。MCPは既存のタスクレビュー準備へ接続し、その実結果を同じ3観点レビューへ渡す。

## 設定

項目定義・適用条件・設定例は[検証計画の記入ルール](verification-plan.md)を正とする。
本書は生成emit・人間待機・再開の操作時に読む。設定済みなら、以下の該当手順から参照する。

## 生成と提示

タスクの作業結果をcompletedで提出すると、endのゲートで入力と実検証証跡を固定する。
`task-specification-generate`のemitは、返却contextをcheck-runnerへ渡す。
profile=task-specification-v1を使い、仕様書生成SkillのJSONを通常のsubmitで返す。
生成Skillは読取りとJSON応答だけを行う。保存やMarkdown化はL4 scriptが担当する。

生成物は`.aidd/implementation/runs/<execution_id>/reviews/<round>/`へ保存される。
`specification.md`がケース別仕様書、`summary.md`が仕様書差分の確認資料（MCP状態は統合レビューのreceiptを参照）。
前回版の無変更項目・順序を保持し、追加・変更・削除・再評価を記録する。
書式や説明の言い換えだけで無関係なケースを書き換えない。

task_review設定時は、生成後に`task-code-review`がemitされる。返却contextを同じcheck-runnerへ
渡し、profile=implementation-task-review-v1で3観点を1回検査する。実際のホスト・モデル版をengineへ記す。
返却JSONを同じdispatchのsubmitへ渡す。仕様書対象外でもコードレビューと人間待機は実施する。
レビューのために検証コマンドを重複実行しない。入力不足・読取り失敗はfailedで返す。
失敗時は既存implement-retryで同じ未完タスクを再開する。新しい依存を追加する必要があれば
検証計画を途中で書き換えず、実装契約の修正・再開に従って計画を再確定する。

code-request.json、code-review.json、code-summary.md、code-manifest.jsonを同じreviews配下へ
仕様書とは独立に不変保存する。既存result.jsonを後から上書きしない。
`task-specification-review`のwaitで、対象タスク、存在する仕様書と差分、統合コードレビュー結果、実MCP状態・未完了理由を人に提示する。
続行・修正・保留を受け取り、未回答や保留ではタスク完了・次タスクへ進まない。

ホストは保存済みの実dispatchとreview_contextを使い、実ユーザーの回答をrespondへ渡す。
下の値は形の例であり、人の回答・actorを生成してはならない。

```json
{
  "operation_id": "保存して再送でも使う操作ID",
  "action": "approve",
  "expected": "返却されたreview_contextをオブジェクトのまま渡す",
  "data": {"answer": "実際に受け取った続行回答"}
}
```

critical/major指摘が残る場合は続行できない。修正後のレビューで同じIDの指摘を残すか、
resolved_findingsに実際の解消根拠が必要。minor/info指摘を受容して続行する場合は、dataに
`"dispositions": {"指摘ID": {"decision": "accept", "reason": "実際の受容理由"}}`を追加する。
全ての残存指摘を実回答と対応づける。指摘なしでも未実施観点や版不一致を人間回答で補完できない。

`--actor`には実回答者を渡す。保留はaction=hold、data.answerに実回答を保持する。
修正はaction=repair、dataを次の形式にする。

```json
{
  "instruction": "実際の修正指示",
  "corrections": {
    "tests/test_booking.py::test_duplicate": "説明だけを直す場合のケースIDと訂正理由"
  }
}
```

コード修正ならcorrectionsを省略できる。説明訂正なら実在するケースIDを指定する。
同じ未完タスクをredoし、新しい確認回で差分更新・再提示する。仕様書ファイルを直接編集しない。
元コード・検証入力が不変なら既存RED/GREEN/VERIFYを再利用して作業結果を再提出できる。
説明だけの訂正のために正常な実装を壊したり、不要な検証を作り直したりしない。
コード・依存・上流・設定・検証証跡・レビュー規則が同じならコードレビュー結果を再利用する。
再利用元の確認回を保存し、新しい資料への実回答は取り直す。変更時は前回指摘と差分で再レビューする。
自動再利用は明示された説明訂正で阻害指摘がない場合に限る。コードレビュー自体の再確認指示や
阻害指摘がある場合は、同じ入力でも再検査する。誤指摘の再確認のために無意味なコード変更を要求しない。

応答が途切れた場合は、同じoperation_id、payload、actorで再送する。保存・L0 report・redoの続きから復旧する。
古い確認回・別タスク・資料や入力が変わった後の回答は拒否する。低水準reportだけでは完了できない。

## 空修正と最終検査

生成直後のnoop修正では追加生成・二重待機をしない。生成側の実回答と同じ版の確認を照合してから完了する。
feature最終レビューからの実修正は新しいexecutionで生成・確認し、前回のスイート資料を差分更新する。

最終reporting設定のspecificationsには従来の手書き資料を残してよい。現在の全スイートのL4生成仕様書がある場合は
空配列も指定でき、manifestで照合した生成資料を最終summaryへ自動で添える。任意の`.aidd`パスを入力に追加しない。
後続作業で関連テスト・共有入力が変わっていれば、対象スイートの更新・再確認を求めて最終検査を止める。

feature最終のimplementation-testsは、従来どおり実テストの入力・assertion・依存代替・証跡をレビューする。
生成した説明文に対する新しい品質観点は設けない。MCP接続や指摘処置の詳細は、実ツール仕様が判明してから追加する。
