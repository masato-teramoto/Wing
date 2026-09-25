---
name: design-revision
description: main_flow Phase 5 のdesign成果物を修正する。修正対象0件なら何も編集しない。指定された自分の成果物だけを編集し、完了・待機・失敗をホストへ返す。
disable-model-invocation: true
---

# design-revision

対象: `specs/{feature}/design.md`。feature単位の対象はホストから受け取る。
テンプレート: `Templates/specs/_template/design.md`。
起動 event: `design-authoring-revise`（`design-authoring-generate` の直後に毎回実行される）。

## 手順

1. `.claude/skills/aidd-common/references/authoring/contract.md` の「修正 Skill」節を読み、ホストが渡した修正要求（repair）を確認する。
2. repair が null・空、または targets が0件なら、どのファイルも編集せず `{"status":"completed","targets":[],"questions":[],"open_placeholders":0,"changed_findings":[],"return_candidates":[],"summary":"修正対象 0 件"}` を返して終了する。
3. 修正要求の種別を確認する。ゲート指摘由来なら findings の各要素に phase / scope / run / number / instruction がある。指摘なしの人間指示なら origin（plan-change / reopen / rfp-change / edited-outside-flow / rollback-from-downstream 等）と instruction があり、findings は空。指定対象がすべて存在し、L3進行制御によってdraftに戻されていることを確認する。対象欠落・draft以外の対象・修正指示の欠落があれば何も変更せずfailedを返す。
4. `.claude/skills/aidd-common/references/authoring/design.md` と上記の実行時テンプレートを読む。steering は一式（全文）を読む。
5. 指定されたdraftの対象だけを、修正指示に関係する箇所だけ修正する。下流ファイルや指定外の対象を編集しない。既存の履歴を消さず、プレースホルダーを削除せず、根拠のない値を推測で書かない。statusは変更しない。根拠不足や上流の不足は質問・差戻し候補として返し、回答後は同じdraftへ再入する。
6. changed_findings は、ゲート指摘由来なら選択された指摘の phase / scope / run / number を過不足なく、指摘なしの人間指示なら `[]` とする。
7. 共通契約のJSON結果を返して終了する。進行状態・ゲート記録・上流・承認を変更せず、他Skillやagentを起動しない。
