#!/usr/bin/env python3
"""aidd_entry — host agent の入口（L3）。L3 が L0 を import する（逆はしない）。

    python3 .claude/skills/aidd-common/scripts/aidd_entry.py <コマンド> [オプション] <操作> [オプション]
    python3 .claude/skills/aidd-common/scripts/aidd_entry.py validate | doctor [--runtime-only]

コマンドは L0 の CommandResolver が `command.yaml` の CommandDefinition（id または `/aidd-...`）から解決し、
`--call` / `--action` はそのコマンドの呼出し先に限る（仕様書の不変条件 1）。

| 操作 | 行き先 |
|---|---|
| `advance` / `submit` / `respond` | L0 の host（`bin/host.py` の `Host`）を同じプロセスで、L3 の規則（`host_session.run_stage`）を渡して実行する |
| `status` / `report` / `redo` / `migrate-flow` / `validate` | L0 の CLI（`bin/command_resolver.py`） |
| それ以外（L3・L4 の操作：`implement-next` / `decision` / `approve` / `repair` / `progress` など） | `host_operations` |

定義ファイルに hook は無い。L0 は L3・L4 を import せず、L4 は L0 の GateExecutor が gate.yaml から実行するゲートの中だけで動く。
案件ルート・状態ストア・定義ファイルの置き場は、このファイルの場所から決まる（`--root` / `--state` / `--config` では変えられない）。
"""
import l0  # noqa: F401  L0 の枠組みを import できるようにする
import json
import os
import sys

import command_resolver  # L0


def doctor(root, state, config, runtime_only):
    """L0 の確認に、配布物・入力の確認（L3）を加える。"""
    import host_session
    extra = host_session.stage_doctor({'root': root})['checks']
    return command_resolver.doctor(root, state, config, runtime_only, extra)


def run(argv):
    if not argv or argv[0] in ('-h', '--help'):
        print(__doc__)
        return 0 if argv else 1
    if argv[0] == 'doctor':
        known = command_resolver._options(argv[1:])
        return doctor(*command_resolver._paths(known), '--runtime-only' in known.rest)
    if argv[0] in command_resolver.GLOBAL_OPERATIONS:
        return command_resolver.run(argv)
    command = argv[0]
    known = command_resolver._options(argv[1:])
    if not known.operation:
        raise command_resolver.DefinitionError('操作が要る（例: /aidd-requirements advance --call requirements-plan）')
    if known.operation in command_resolver.ENGINE_OPERATIONS:
        return command_resolver.run(argv)
    root, state, config = command_resolver._paths(known)
    import repositories
    resolver = command_resolver.CommandResolver(repositories.load(config))
    resolver.check(command, known.call)
    resolver.check(command, known.action)
    import host_operations
    # The public entry validates this project's definitions. In-process contexts
    # must use the same definitions even when the caller inherited another gate's
    # AIDD_CONFIG; restore that environment for callers embedding this entry.
    previous = os.environ.get('AIDD_CONFIG')
    os.environ['AIDD_CONFIG'] = config
    try:
        return host_operations.main(['--root', root, '--state', state] + command_resolver._passthrough(known)
                                    + known.rest + [known.operation])
    finally:
        if previous is None:
            os.environ.pop('AIDD_CONFIG', None)
        else:
            os.environ['AIDD_CONFIG'] = previous


def main(argv=None):
    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, 'reconfigure'):
            stream.reconfigure(encoding='utf-8', errors='replace')
    try:
        return run(list(sys.argv[1:] if argv is None else argv))
    except command_resolver.DefinitionError as error:
        print(json.dumps({'status': 'fail', 'error': str(error)}, ensure_ascii=False))
        return 1


if __name__ == '__main__':
    raise SystemExit(main())
