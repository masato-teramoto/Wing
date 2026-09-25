"""The public L0 CLI boundary. No runner implementation is imported."""
import json
from pathlib import Path
import subprocess
import sys


def validate(context):
    return invoke(context, 'validate')


def invoke(context, command, call=None, **options):
    common = Path(__file__).resolve().parents[1]
    argv = [sys.executable, '-X', 'utf8', '-B', str(common/'bin/aidd.py'),
            '--root', context.root, '--state', context.state_path, '--config', str(common), command]
    if command != 'validate':
        selected = call
        if selected is None and context.process == 'implement':
            import implementation_flows
            selected = implementation_flows.call(context)
        selected = selected or context.event
        argv += [selected] if command == 'call' else ['--call', selected]
        if context.item:
            argv += ['--item', context.item]
    for name, value in options.items():
        if value is not None:
            argv += ['--'+name.replace('_','-'), str(value)]
    argv.append('--json')
    # Phase 8 fixes a <=480s aggregate tool budget below L0's 600s unit limit.
    # The outer call also includes its guards/snapshot and must outlive the unit.
    timeout = 720 if context.process == 'implement' and command == 'call' else 60
    result = subprocess.run(argv, cwd=context.root, capture_output=True, encoding='utf-8', timeout=timeout)
    try:
        data = json.loads(result.stdout)
    except ValueError as error:
        raise ValueError('L0 returned invalid JSON: '+result.stderr) from error
    if result.returncode not in (0,10,20):
        raise RuntimeFailure(data)
    return data


class RuntimeFailure(ValueError):
    def __init__(self, data):
        self.data = data
        super().__init__(data.get('detail') or data.get('error') or str(data))
