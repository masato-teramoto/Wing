---
name: implement-revision
description: 実際の人間修正要求に対応づく単一task_idを修正し、回帰検証と結果を返す。
disable-model-invocation: true
---

## 手順

役割: 修正（repair）

1. `.claude/skills/aidd-common/references/implementation/contract.md` を読み、
   repair_findingsの元検査回・指摘番号・実指示・対象task_id・前回実行を確認する。
   contextの`unreviewed_inputs`に挙げた上流（target_reviewから外れたdraft）はapprovedでなくてよい。
   context.noop=trueなら変更・メモ・検証コマンドを実行せず、同じrequest_id/execution_id/feature/task_idと
   status=completed、空のquestions/return_candidates/changed_findingsを返して終了する。
   noopでないのに非空の要求が無い、または複数タスクを実装する必要がある場合はwaitingで返す。
2. `.claude/skills/aidd-common/references/implementation/task-procedure.md` に従い、
   対象1件を再現テストから修正する。共有コードと依存先への影響も検証する。
3. changed_findingsには受け取った対応表をそのまま返す。他タスクや元指摘全体の解消を宣言しない。
   次アクション・検査agent・人間承認を実行しない。
