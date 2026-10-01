# 検証計画の条件付き補足

[記入ルール](verification-plan.md)の非コードタスクまたはmetricを使う時に、該当節だけ読む。
以下は部分例。既存の検証計画へ適用する際は、実際のタスクID・検査ID・パスとの対応を保つ。

## 非コードタスク

既存の環境準備タスクが、固定した開発用依存の導入・確認だけを扱う場合のタスク設定例。
tasksの該当IDへ記す。例のために準備タスクを新設したり、業務コードを含むタスクを対象外にしたりしない。

```json
{
  "allowed_paths": ["requirements-test.txt"],
  "check_ids": ["environment"],
  "tdd": false,
  "non_code_reason": "既定の開発用依存を準備するだけで、製品コードを実装しない。",
  "specification_exemption": "環境準備だけで、単体テストの作成・変更を行わない。"
}
```

environmentは案件にある、版・機能の利用可能性を確認するコマンドとしてchecksへ登録する。
feature_checksにも含め、両者の宣言順を保持する。導入コマンドは登録せず、タスク作業として扱う。
non_code_reasonはTDDを行わない理由、specification_exemptionは仕様書生成の対象外理由である。
task_qualityを設定した計画で対象外にする場合は、tdd=falseと両方の理由を記し、specification_scopeは省略する。
VERIFYは必要。全タスクが対象外ならsuitesは`{}`とし、未使用スイートを残さない。

## 任意の数値基準

checksの1件へmetricを追加すると、そのコマンドが出力したJSONの数値を下限と比較する。
採用しない場合はmetricを省略する。値の単位・閾値は案件の検証方針から定め、新しい品質基準を例から補わない。

| metric内の項目 | 型・条件 | 記入内容 |
|---|---|---|
| `path` | 文字列・必須 | JSON出力ファイルの案件ルート相対パス。cwdからの相対ではない |
| `keys` | 空でない文字列配列・必須 | JSONのプロパティを順に辿るキー。末端は有限の数値 |
| `minimum` | 有限の数値・必須 | 下限値。取得値がこの値以上なら条件を満たす |

例えば案件が80以上という下限を採用済みで、実コマンドが次のJSONをcoverage/summary.jsonへ出す場合：

```json
{"total": {"percent_covered": 85}}
```

該当checkへ追加するmetricの値：

```json
{
  "path": "coverage/summary.json",
  "keys": ["total", "percent_covered"],
  "minimum": 80
}
```

コマンド自身が今回のファイルを出力・更新する必要がある。古い値・欠落・非数値・下限未達は成功にならない。
コマンドの失敗も数値で免除しない。metricが出力先の作成や集計を行うわけではない。
例のcoverage/が生成物だけを含む場合はgenerated_pathsへ追加する。実ソース・検証入力と重なる場所は除外しない。
この設定は数値判定であり、最終検査の可読coverageレポートを代替しない。
