# 案件レベルの確認（全体結合確認・横断 ACE・実コードの横断確認）

全 feature の実装承認の後に、両方式で 1 回通す（計画 v3 §6.11）。正本の判定は L3 の `implementation_project.py`。

## 案件の検証計画 `.aidd/implementation/config/_project.json`

```json
{
  "schema": 1,
  "groups": {
    "build": {"checks": [{"id": "build", "argv": ["..."], "cwd": ".", "timeout_seconds": 300}]},
    "smoke": {"checks": [{"id": "smoke", "argv": ["{python}", "-B", "tools/smoke.py"], "cwd": ".", "timeout_seconds": 300}]}
  },
  "owner": "<owner feature または 候補なし>",
  "owner_reason": "",
  "wrapper": "tools/smoke.py",
  "generated_paths": []
}
```

- checks の形は feature の検証計画と同じ（id・argv・cwd・timeout_seconds 1..480・metric、group ごとの合計 480 秒以内）。
- group は build（全体 build）と smoke（起動→readiness 待ち→共通機能を通る 1 経路→停止を 1 つの wrapper で行う）の 2 つ。
  共通機能が無い案件は「起動→readiness 待ち→業務 API 1 本→停止」、owner が「候補なし」の案件は「起動→readiness 待ち→停止」に縮める。
- owner は `workflow.smoke_owner`（tasks の計画停止点か方式切替の確定で選んだ値）から写す。違えば L3 が拒否する。
- wrapper は owner feature の tasks の「結合確認タスク」で作り、タスクレビューを通したもの。
- 1 経路の内容は Platform feature の design（公開契約）と案件の実際の起動手順から AI が確定する。別の承認の停止は置かず、
  不明点があれば質問で止まる。必須検査を省略したり、便宜的な成功コマンドを作ったりしない。

## 全体結合確認 `implement-integration-run[build]` → `[smoke]`

L4 の `implementation-integration-tools` ゲートが unit 内で checks を実行する（feature の `implementation-tools` と同じ実行器）。
`final_project()` の判定項目（L4 に示す仕様、M-10）：

| 項目 | 合格の条件 |
|---|---|
| 前提 | 全 feature の実装承認が現在の照合で通る。smoke は build の受領証が合格 |
| 実行 | 宣言した checks を宣言順に全部実行し、全部の終了コードが 0（timeout・起動失敗・経路失敗は失敗） |
| プロセス | 起動したサーバーは wrapper が停止し、残れば ProcessTree が強制停止する |
| 受領証 | `integration/<group>/receipt.json` に checks の結果・ログの hash を保存。ログが欠ければ失敗 |
| 鮮度 | 受領証のコード在庫 digest（案件全体。どの feature の allowed_paths にも入らない既存コードを含む）・`_project.json` の hash・wrapper の hash が現在と一致 |

いずれかの feature の実装が再承認された（コードが変わった）、`_project.json` か wrapper が変わったら受領証は古く、再実行は同じ action の次の unit。

## 横断 ACE `implement-cross-ace-run[<chunk>]`

smoke の合格を記録した時点で L3 が ACE 計画（`cross-ace/plan.json`）を作る。対象は案件全体のコードのうち ACE の対象拡張子で、
現在の hash と ACE の版の受領証が無いファイル。チャンクは `workers × budget_seconds ÷ timeout_seconds` 件ずつ。
受領証のあるファイルは送らず、受領証を参照として示す。失敗したチャンクは L3 が分割（全体の予算切れ）・送り直し（一時的な失敗、3 回まで）・
停止（それ以外）に振り分ける。どのタスクも触っていない既存コードのうち ACE が受け付けないものは「ACE 対象外」として理由付きで示す。

## 実コードの横断確認 `implement-cross-gate`

前提：全 feature の実装承認、build・smoke の受領証が合格、ACE 計画の最新の版の全チャンクが完了、Feature 方式では全 feature の
docs の固定版が最終の docs_revision と一致。検査対象は束ねた入力の `cross-review.json`。承認されるまで Phase 8 は完了にならない。
