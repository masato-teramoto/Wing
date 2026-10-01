"""L0 の CLI（`aidd.py`）を子プロセスで呼ぶ。host（`host.py`）と L3・L4 の規則 script が使う。

実行（call / report / redo / status）はこの経路で行う。状態ストアの排他と保存を `aidd.py` が持つため、
呼ぶ側は状態ストアのランナー欄を直接書き換えない。定義の読込みは `execution_context.definitions()` を使う。
"""
import json
import os
import subprocess
import sys

COMMON = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


class RuntimeFailure(ValueError):
    """`aidd.py` が 0 / 10 / 20 以外で終わった（失敗・設定の誤り）。`data` に出力の JSON を持つ。"""

    def __init__(self, data):
        self.data = data
        super().__init__(data.get('detail') or data.get('error') or data.get('message') or str(data))


def invoke(root, state_path, command, call=None, item=None, config=None, timeout=60, **options):
    """`aidd.py <command>` を実行し、JSON の出力を返す。"""
    argv = [sys.executable, '-X', 'utf8', '-B', os.path.join(COMMON, 'bin', 'aidd.py'),
            '--root', str(root), '--state', str(state_path), '--config', str(config or COMMON), command]
    if command != 'validate':
        if call:
            argv += [call] if command == 'call' else ['--call', call]
        if item:
            argv += ['--item', item]
    for name, value in options.items():
        if value is not None:
            argv += ['--' + name.replace('_', '-'), str(value)]
    argv.append('--json')
    result = subprocess.run(argv, cwd=str(root), capture_output=True, encoding='utf-8', timeout=timeout)
    try:
        data = json.loads(result.stdout)
    except ValueError as error:
        raise ValueError('L0 returned invalid JSON: ' + result.stderr) from error
    if result.returncode not in (0, 10, 20):
        raise RuntimeFailure(data)
    return data
