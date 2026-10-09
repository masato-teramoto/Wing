"""`implement-integration-run`・`implement-cross-ace-run` の本体（L0 の action は run が必須）。

ゲートが保存した受領証を確かめるだけで、何も実行しない（計画 v3 §6.11）。
"""
import phase_rules
import implementation_project as project

if __name__ == '__main__':
    context = phase_rules.ExecutionContext()
    try:
        project.run_proof(context)
        message = '%s[%s] passed on the current code' % (context.action, context.item)
    except (ValueError, OSError, KeyError) as error:
        phase_rules.fail(str(error))
    phase_rules.ok(message)
