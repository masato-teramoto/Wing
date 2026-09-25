---
name: requirement-intake
description: main_flow Phase 1 のintake成果物を生成する。指定された自分の成果物だけを編集し、完了・待機・失敗をホストへ返す。
disable-model-invocation: true
---

# requirement-intake

対象: `.aidd/requirement-list.md`。feature単位の対象はホストから受け取る。
テンプレート: `Templates/Flow/requirement-list.md`。
起動 event: `requirement-intake-generate`（直後に `requirement-intake-revise` が毎回実行される）。

## 手順

1. `.claude/skills/aidd-common/references/authoring/contract.md` を読み、受け取った対象・承認済み入力・質問回答を確認する。
2. `.claude/skills/aidd-common/references/authoring/intake.md` と上記の実行時テンプレートを読む。
3. 指定対象の未作成または再入中のdraftを確認する。既存のreview/approvedを変更しない。
4. 生成の前に RFP の受入判定（intake.md の 3 点）を行う。満たさなければ要求一覧を作らず、RFP のパスを対象とする差戻し候補（フロー外、人間が RFP を改訂）を付けて waiting で返す。回答だけで受入済みとしない。
5. 承認済み入力と実際の回答から対象を生成する。根拠のない値を推測で書かず、プレースホルダーを削除せず、`TBD` / `未定` を記入欄へ新たに書かない。
6. テンプレートと実成果物の前提矛盾は編集で吸収せず、共通契約の「停止して返す場面」に従い質問・差戻し候補として返す。値の未確定・対象の不特定は反映先フェーズで確定させるものとし、本工程で推測して明確化しない。
7. 共通契約のJSON結果を返して終了する。進行状態・ゲート記録・上流・承認を変更せず、他Skillやagentを起動しない。
