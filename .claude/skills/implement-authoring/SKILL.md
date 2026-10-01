---
name: implement-authoring
description: 指定された単一task_idをTDDで実装・検証し、タスク完了要求を返す。
disable-model-invocation: true
---

## 手順

役割: 生成（generate）

1. `.claude/skills/aidd-common/references/implementation/contract.md` を読む。
   渡されたfeature/request_id/execution_id/task_idと承認済み入力を照合する。
   contextの`unreviewed_inputs`に挙げた上流（target_reviewから外れたdraft）はapprovedでなくてよい。
2. `.claude/skills/aidd-common/references/implementation/task-procedure.md` に従い、対象1件を実装する。
3. 結果JSONを返して終了する。次のタスク・検査agentを起動せず、承認・完了状態を変更しない。
