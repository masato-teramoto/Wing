---
name: design-revision
description: main_flow Phase 5 のdesign成果物を修正する。修正対象0件なら何も編集しない。指定された自分の成果物だけを編集し、完了・待機・失敗をホストへ返す。
disable-model-invocation: true
---

# design-revision

対象: `specs/{feature}/design.md`。feature単位の対象はホストから受け取る。
テンプレート: `Templates/specs/_template/design.md`。
起動アクション: `design-authoring-revise`（`design-authoring-generate` の後、修正要求があるあいだ、入口 Skill が修正の 1 回ごとに呼ぶ）。


修正の依頼の origin が `reevaluation`（切り替え前の指摘の再評価）のときは、本文を変えない。`{"status":"completed","targets":<依頼の targets>,"questions":[],"open_placeholders":0,"changed_findings":[],"return_candidates":[],"summary":"再評価のため本文は変えない"}` を返す。

## 手順

役割: 修正（repair）
繰り返し: feature ごと（per-feature）

1. `.claude/skills/aidd-common/references/authoring/contract.md` の「修正 Skill」節を読み、ホストが渡した修正要求（repair）を確認する。
2. repair が null・空、または targets が0件なら、どのファイルも編集せず `{"status":"completed","targets":[],"questions":[],"open_placeholders":0,"changed_findings":[],"return_candidates":[],"summary":"修正対象 0 件"}` を返して終了する。
3. 修正要求の種別を確認する。ゲート指摘由来なら findings の各要素に phase / scope / run / number / instruction がある。指摘なしの人間指示なら origin（plan-change / reopen / rfp-change / edited-outside-flow / rollback-from-downstream 等）と instruction があり、findings は空。指定対象がすべて存在し、L3進行制御によってdraftに戻されていることを確認する。対象欠落・draft以外の対象・修正指示の欠落があれば何も変更せずfailedを返す。repair の instruction は L3 が修正案・差戻しの理由から埋めることがある（人が指示文を書かず、推奨の採用・軽微・差戻しで決まった指摘）。そのときも instruction を修正指示として扱い、修正案はそのまま当てはめ、差戻しの理由は直す方針として読む。
4. `.claude/skills/aidd-common/references/authoring/design.md` と上記の実行時テンプレートを読む。steering は一式（全文）を読む。
5. 指定されたdraftの対象だけを、修正指示に関係する箇所だけ修正する。下流ファイルや指定外の対象を編集しない。既存の履歴を消さず、プレースホルダーを削除せず、根拠のない値を推測で書かない。statusは変更しない。根拠不足や上流の不足は質問・差戻し候補として返し、回答後は同じdraftへ再入する。選ばれた指摘・指示に関係しない節は変えない（L3 が承認時に変わった節を示し、指示に無い変更を知らせる）。
6. changed_findings は、ゲート指摘由来なら選択された指摘の phase / scope / run / number を過不足なく、指摘なしの人間指示なら `[]` とする。
7. 自己検査：返す前に、作成・修正した対象を上記の実行時テンプレートと照らし、ID 形式・参照（ID・パス・節の参照先が実在するか）・書式（見出し・表・記法）を確かめ、不備はその場で直す。往復は 2 回までとし、残ったものはそのまま返す（L4 のゲートは別に行う。自己検査はそれを代替しない）。根拠の無い値を自己検査で補わない。
8. 共通契約のJSON結果を返して終了する。進行状態・ゲート記録・上流・承認を変更せず、他Skillやagentを起動しない。
