"""L3 から L0 の CLI を呼ぶ。呼出し先の既定（Phase 8 の flow）と時間の上限だけが L3 の規則である。"""
import l0  # noqa: F401
import engine_cli
import execution_context as framework

RuntimeFailure = engine_cli.RuntimeFailure


def validate(context):
    return framework.definitions(context.config)


def invoke(context, command, call=None, **options):
    if command == 'validate':
        return validate(context)
    selected = call
    if selected is None and context.process == 'implement':
        import implementation_flows
        selected = implementation_flows.call(context)
    selected = selected or context.action
    # Phase 8 fixes a <=480s aggregate tool budget below L0's 600s unit limit.
    # The outer call also includes its guards/snapshot and must outlive the unit.
    timeout = 720 if context.process == 'implement' and command == 'call' else 60
    return engine_cli.invoke(context.root, context.state_path, command, selected, context.item or None,
                             config=context.config, timeout=timeout, **options)
