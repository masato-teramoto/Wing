---
name: docs-integration
description: main_flow Phase 6 のdocs成果物を生成する。指定された自分の成果物だけを編集し、完了・待機・失敗をホストへ返す。
disable-model-invocation: true
---

# docs-integration

対象: `docs/code-design.md` / `docs/architecture/data-model.md` / `docs/architecture/system-overview.md`。feature単位の対象はホストから受け取る。
テンプレート: `Templates/docs/code-design.md` / `Templates/docs/architecture/data-model.md` / `Templates/docs/architecture/system-overview.md`。
起動 event: `docs-integration-generate`（直後に `docs-integration-revise` が毎回実行される）。

## 手順

1. `.claude/skills/aidd-common/references/authoring/contract.md` を読み、受け取った対象・承認済み入力・質問回答を確認する。
2. `.claude/skills/aidd-common/references/authoring/docs.md` と上記の実行時テンプレートを読む。steering は一式（全文）を読む。
3. 指定対象の未作成または再入中のdraftを確認する。既存のreview/approvedを変更しない。
4. 承認済み入力と実際の回答から対象を生成する。根拠のない値を推測で書かず、プレースホルダーを削除せず、`TBD` / `未定` を記入欄へ新たに書かない。
5. design 間の競合・欠落は該当 design への差戻し候補として返し、docs 統合を保留する。人間の回答だけで当該要素を採用しない。
6. テンプレートと実成果物の前提矛盾・上流の不足・新規要求は編集で吸収せず、共通契約の「停止して返す場面」に従い質問・差戻し候補として返す。上流を疑う前に当該工程内で解消できないかを確認する。新規要求は要求一覧を編集せず Phase 1 への差戻し候補とする。
7. 共通契約のJSON結果を返して終了する。進行状態・ゲート記録・上流・承認を変更せず、他Skillやagentを起動しない。
