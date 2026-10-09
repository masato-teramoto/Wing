---
name: tasks-revision
description: main_flow Phase 7 のtasks成果物を修正する。修正対象0件なら何も編集しない。指定された自分の成果物だけを編集し、完了・待機・失敗をホストへ返す。
disable-model-invocation: true
---

# tasks-revision

対象: `specs/{feature}/tasks.md`。feature単位の対象はホストから受け取る。
テンプレート: `Templates/specs/_template/tasks.md`。
起動アクション: `tasks-authoring-revise`（`tasks-authoring-generate` の後、修正要求があるあいだ、入口 Skill が修正の 1 回ごとに呼ぶ）。


修正の依頼の origin が `reevaluation`（切り替え前の指摘の再評価）のときは、本文を変えない。`{"status":"completed","targets":<依頼の targets>,"questions":[],"open_placeholders":0,"changed_findings":[],"return_candidates":[],"summary":"再評価のため本文は変えない"}` を返す。

## 手順

役割: 修正（repair）
繰り返し: feature ごと（per-feature）

1. `.claude/skills/aidd-common/references/authoring/contract.md` の「修正 Skill」節を読み、ホストが渡した修正要求（repair）を確認する。
2. repair が null・空、または targets が0件なら、どのファイルも編集せず `{"status":"completed","targets":[],"questions":[],"open_placeholders":0,"changed_findings":[],"return_candidates":[],"summary":"修正対象 0 件"}` を返して終了する。
3. 修正要求の種別を確認する。ゲート指摘由来なら findings の各要素に phase / scope / run / number / instruction がある。指摘なしの人間指示なら origin（plan-change / reopen / rfp-change / edited-outside-flow / rollback-from-downstream 等）と instruction があり、findings は空。指定対象がすべて存在し、L3進行制御によってdraftに戻されていることを確認する。対象欠落・draft以外の対象・修正指示の欠落があれば何も変更せずfailedを返す。repair の instruction は L3 が修正案・差戻しの理由から埋めることがある（人が指示文を書かず、推奨の採用・軽微・差戻しで決まった指摘）。そのときも instruction を修正指示として扱い、修正案はそのまま当てはめ、差戻しの理由は直す方針として読む。
4. `.claude/skills/aidd-common/references/authoring/tasks.md` と上記の実行時テンプレートを読む。steering は一式（全文）を読む。
5. 修正前に下記の「既存tasksの変更範囲」を確認し、影響を提示する。その上で、指定されたdraftの対象だけを、修正指示に関係する箇所だけ修正する。下流ファイルや指定外の対象を編集しない。既存の履歴を消さず、プレースホルダーを削除せず、根拠のない値を推測で書かない。statusは変更しない。根拠不足や上流の不足は質問・差戻し候補として返し、回答後は同じdraftへ再入する。選ばれた指摘・指示に関係しない節は変えない（L3 が承認時に変わった節を示し、指示に無い変更を知らせる）。
6. changed_findings は、ゲート指摘由来なら選択された指摘の phase / scope / run / number を過不足なく、指摘なしの人間指示なら `[]` とする。
7. 自己検査：返す前に、作成・修正した対象を上記の実行時テンプレートと照らし、ID 形式・参照（ID・パス・節の参照先が実在するか）・書式（見出し・表・記法）を確かめ、不備はその場で直す。往復は 2 回までとし、残ったものはそのまま返す（L4 のゲートは別に行う。自己検査はそれを代替しない）。根拠の無い値を自己検査で補わない。
8. 共通契約のJSON結果を返して終了する。進行状態・ゲート記録・上流・承認を変更せず、他Skillやagentを起動しない。

## 既存tasksの変更範囲

- 資材のバージョン更新だけを理由に再生成しない。共通作成規則と整合する既存タスクを新しい例の表現へ統一しない。
- 修正前に、変更するタスク番号と理由、責務変更が波及するDepends・AC対応・検証計画の参照、着手・完了状態と証跡への影響、再検査・再承認の範囲を示す。着手状況は入口が添えた`task_history`と根拠の参照先で確かめる。過去の完了と現在の計画での有効性を区別し、記録の欠落・矛盾などで不明な対象だけ質問する。未着手と推測せず、履歴が未添付なら入口に収集を求める。手順は`.claude/skills/aidd-tasks/SKILL.md`の「修正Skillへ渡す着手履歴」を参照する。
- 未着手の不整合は、テスト・実装・検証が同一タスクで完結する最小の差分にする。対象と必要な依存・参照だけを直し、無関係な本文・番号・並び・チェック状態・実装メモ・履歴を維持する。番号を詰め直したり、AC・完了条件を弱めて指摘を消したりしない。
- 着手済み・完了済みタスクの番号変更・削除・統合や既存証跡の扱いに変更が必要なら、編集前に影響と別対応の必要性を返す。完了印を外す、履歴を消す、過去の証跡を別タスクへ付け替える操作はしない。
- 本文の修正範囲と検査・承認の範囲を区別する。局所修正でも、既存の`aidd-tasks`は修正後のfeature検査・全体確認と人間承認を要求する。再検査・再承認を変更タスクだけに限定すると約束しない。検証計画など下流の変更は影響として返し、このSkillで書き換えない。
- 明示的な再計画・再生成の要求と局所修正を区別し、結果のsummaryにも要求の区分と変更・影響を残す。再承認だけで「再作成」と扱わない。ACEの適用判断はPhase 8の検証計画記入ルールが担い、このSkillから設定を書かない。
