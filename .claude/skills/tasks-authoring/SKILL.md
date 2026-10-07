---
name: tasks-authoring
description: main_flow Phase 7 のtasks成果物を生成する。指定された自分の成果物だけを編集し、完了・待機・失敗をホストへ返す。
disable-model-invocation: true
---

# tasks-authoring

対象: `specs/{feature}/tasks.md`。feature単位の対象はホストから受け取る。
テンプレート: `Templates/specs/_template/tasks.md`。
起動アクション: `tasks-authoring-generate`（修正要求があるときだけ、入口 Skill が続けて `tasks-authoring-revise` を呼ぶ）。

## 手順

役割: 生成（generate）
繰り返し: feature ごと（per-feature）

1. `.claude/skills/aidd-common/references/authoring/contract.md` を読み、受け取った対象・承認済み入力・質問回答を確認する。
2. `.claude/skills/aidd-common/references/authoring/tasks.md` と上記の実行時テンプレートを読む。steering は一式（全文）を読む。
3. 指定対象の未作成または再入中のdraftを確認する。既存のreview/approvedを変更しない。
4. 承認済み入力と実際の回答から対象を生成する。根拠のない値を推測で書かず、プレースホルダーを削除せず、`TBD` / `未定` を記入欄へ新たに書かない。
5. `docs/` は生成入力として読まない。tasks にしか存在しない設計判断が必要なら該当 design への差戻し候補として返す。
6. テンプレートと実成果物の前提矛盾・上流の不足・新規要求は編集で吸収せず、共通契約の「停止して返す場面」に従い質問・差戻し候補として返す。上流を疑う前に当該工程内で解消できないかを確認する。新規要求は要求一覧を編集せず Phase 1 への差戻し候補とする。
7. 自己検査：返す前に、作成・修正した対象を上記の実行時テンプレートと照らし、ID 形式・参照（ID・パス・節の参照先が実在するか）・書式（見出し・表・記法）を確かめ、不備はその場で直す。往復は 2 回までとし、残ったものはそのまま返す（L4 のゲートは別に行う。自己検査はそれを代替しない）。根拠の無い値を自己検査で補わない。
8. 共通契約のJSON結果を返して終了する。進行状態・ゲート記録・上流・承認を変更せず、他Skillやagentを起動しない。
