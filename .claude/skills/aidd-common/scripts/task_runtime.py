"""Approved task plans and replayable, narrowly authorized runtime edits.

The original approved bytes never change. Reading a projected plan digest first
replays the entire journal against the actual document; this is not a blanket
exclusion of checkboxes or notes from approval protection.
"""
import base64
from pathlib import Path
import re

import artifacts
import implementation_store as store

NOTES = ('決定ログ', '既知の制約 / 残課題', '後続への申し送り')
TASK = re.compile(r'^- \[([ xX])\] ([1-9][0-9]*) (.+)$', re.M)
RUNTIME_SLOTS = {'TSK_DECISION_LOG_N', 'TSK_KNOWN_ISSUE_N', 'TSK_HANDOVER_N'}


def open_plan_slots(data):
    allowed = dict(zip(NOTES, ('TSK_DECISION_LOG_N', 'TSK_KNOWN_ISSUE_N', 'TSK_HANDOVER_N')))
    in_notes, section, count = False, None, 0
    for line in data.decode('utf-8').splitlines():
        if line.startswith('## '):
            in_notes = line == '## 実装メモ（Implementation Notes）'
            section = None
        elif line.startswith('### '):
            section = line[4:] if in_notes else None
        count += sum(slot != allowed.get(section) for slot in re.findall(r'<([A-Z][A-Z0-9_]*)>', line))
    return count


def locations(path):
    path = Path(path).resolve()
    if path.name != 'tasks.md' or path.parent.parent.name != 'specs':
        return None
    root, feature = path.parents[2], path.parent.name
    return root, store.BASE + '/plans/' + store.identifier(feature) + '/active.json'


def protected_bytes(data):
    match = artifacts.FRONT.match(data)
    if not match:
        raise ValueError('tasks frontmatter missing')
    header = b'\n'.join(line for line in match.group(1).splitlines() if not artifacts.MUTABLE.match(line))
    return header + b'\n---\n' + data[match.end():]


def parse(data):
    text = data.decode('utf-8').replace('\r\n', '\n')
    if text.count('## タスク一覧\n') != 1 or text.count('## 実装メモ（Implementation Notes）\n') != 1:
        raise ValueError('tasks require the task list and Implementation Notes sections')
    body = text.split('## タスク一覧\n', 1)[1].split('## 実装メモ（Implementation Notes）\n', 1)[0]
    matches = list(TASK.finditer(body))
    if not matches or len(re.findall(r'^- \[', body, re.M)) != len(matches):
        raise ValueError('tasks need unique positive integer IDs (hierarchical IDs are unsupported)')
    result = {}
    for index, match in enumerate(matches):
        task_id = match.group(2)
        if task_id in result:
            raise ValueError('duplicate task ID: ' + task_id)
        block = body[match.end():matches[index + 1].start() if index + 1 < len(matches) else len(body)]
        fields = {}
        for key in ('Requirements', 'Design', 'Boundary', 'Depends'):
            found = re.findall(r'^  - _' + key + r': (.+)_\s*$', block, re.M)
            if len(found) != 1 or re.search(r'<[^>]+>|\{\{', found[0]):
                raise ValueError('task ' + task_id + ' requires ' + key)
            fields[key] = found[0].strip()
        done = re.findall(r'^  - 観測可能な完了条件: (.+)$', block, re.M)
        if not done or any(re.search(r'<[^>]+>|\{\{', line) for line in done):
            raise ValueError('task needs observable completion criteria: ' + task_id)
        deps = [] if fields['Depends'] in ('なし', '-', 'none') else [part.strip() for part in fields['Depends'].split(',')]
        if any(not re.fullmatch(r'[1-9][0-9]*', dep) for dep in deps) or len(deps) != len(set(deps)):
            raise ValueError('Depends must contain unique integer task IDs')
        result[task_id] = {'task_id': task_id, 'summary': match.group(3), 'checked': match.group(1) != ' ',
                           'criteria': done, 'references': fields, 'depends_on': deps}
    for note in NOTES:
        if text.count('### ' + note + '\n') != 1:
            raise ValueError('missing or duplicate note section: ' + note)
    ordered, visiting = [], set()
    def visit(key):
        if key not in result:
            raise ValueError('unknown dependency: ' + key)
        if key in visiting:
            raise ValueError('task dependency cycle')
        if key in ordered:
            return
        visiting.add(key)
        for dep in result[key]['depends_on']:
            visit(dep)
        visiting.remove(key)
        ordered.append(key)
    for key in result:
        visit(key)
    return result, ordered


def apply_bytes(data, operation):
    text = data.decode('utf-8')
    newline = '\r\n' if '\r\n' in text else '\n'
    text = text.replace('\r\n', '\n')
    task_id = operation['task_id']
    if task_id not in parse(data)[0]:
        raise ValueError('task not in approved plan')
    if operation['kind'] == 'check':
        if type(operation['checked']) is not bool:
            raise ValueError('checked must be boolean')
        text, count = re.subn(r'^(- \[)[ xX](\] ' + task_id + r' .+)$',
                             lambda m: m[1] + ('x' if operation['checked'] else ' ') + m[2], text, flags=re.M)
        if count != 1:
            raise ValueError('task checkbox is ambiguous')
    elif operation['kind'] == 'note':
        section, message = operation['section'], operation['text']
        if section not in NOTES or not isinstance(message, str) or not message.strip() or '\n' in message or '\r' in message:
            raise ValueError('a single-line note and a known section are required')
        heading = '### ' + section + '\n'
        start = text.index(heading) + len(heading)
        stop = re.search(r'^#{1,3} |^---\s*$', text[start:], re.M)
        end = start + stop.start() if stop else len(text)
        text = text[:end] + '- [task ' + task_id + '] ' + message + '\n\n' + text[end:]
    else:
        raise ValueError('unknown task runtime operation')
    return text.replace('\n', newline).encode('utf-8')


def replay(value, include_prepared=False):
    data = base64.b64decode(value['original'], validate=True)
    if store.digest(data) != value['original_sha256']:
        raise ValueError('approved task original changed')
    for op in value['operations']:
        if op['status'] == 'applied' or include_prepared:
            if store.digest(protected_bytes(data)) != op['before_sha256']:
                raise ValueError('task journal predecessor changed')
            data = apply_bytes(data, op['operation'])
            if store.digest(protected_bytes(data)) != op['after_sha256']:
                raise ValueError('task journal result changed')
    return data


def project(path, data):
    location = locations(path)
    if location is None or not (location[0] / location[1]).exists():
        return data
    value = store.read(*location)
    approval = value['approval']
    record = artifacts.resolve(location[0], approval['path']).read_bytes()
    if len(record) < approval['bytes'] or store.digest(record[:approval['bytes']]) != approval['sha256']:
        raise ValueError('original task approval evidence changed or disappeared')
    expected = replay(value)
    if protected_bytes(data) != protected_bytes(expected):
        raise ValueError('tasks differ from approved plan plus authorized journal; resume pending edit or revise the plan')
    if any(op['status'] != 'applied' for op in value['operations']):
        raise ValueError('task update interrupted; retry its original operation')
    return base64.b64decode(value['original'], validate=True)


def freeze(context, feature):
    path = Path(context.path('specs/' + store.identifier(feature) + '/tasks.md'))
    root, location = locations(path)
    if (root / location).exists():
        project(path, path.read_bytes())
        return store.read(root, location)
    import aidd_paths
    import review_contract
    approved = aidd_paths.Context(context.root, context.state_path, 'tasks-gate-run')
    record = review_contract.check_approved(approved)
    approval_bytes = Path(approved.gate_record).read_bytes()
    data = path.read_bytes()
    tasks, order = parse(data)
    plan_ref = store.digest(protected_bytes(data))
    value = {'schema': 1, 'feature': feature, 'plan_ref': plan_ref,
             'original': base64.b64encode(data).decode(), 'original_sha256': store.digest(data),
             'tasks': tasks, 'order': order, 'operations': [],
             'approval': {'path': Path(approved.gate_record).relative_to(context.root).as_posix(),
                          'bytes': len(approval_bytes), 'sha256': store.digest(approval_bytes),
                          'scope': 'phase', 'run': record.latest('phase').number,
                          'feature_run': record.latest('feature:' + feature).number}}
    store.write(root, location.replace('active.json', plan_ref + '.json'), value)
    store.write(root, location, value)
    return value


def update(context, feature, operation_id, operation):
    path = Path(context.path('specs/' + store.identifier(feature) + '/tasks.md'))
    root, location = locations(path)
    value = store.read(root, location)
    previous = next((op for op in value['operations'] if op['id'] == operation_id), None)
    if previous and previous['operation'] != operation:
        raise ValueError('task operation ID reused with different content')
    if any(op['id'] != operation_id and op['status'] != 'applied' for op in value['operations']):
        raise ValueError('retry the unfinished task update first')
    before = replay(value)
    current = path.read_bytes()
    if previous and previous['status'] == 'applied':
        project(path, current)
        return value
    if previous is None:
        project(path, current)
        previous = {'id': operation_id, 'operation': operation, 'status': 'prepared',
                    'before_sha256': store.digest(protected_bytes(before)),
                    'after_sha256': store.digest(protected_bytes(apply_bytes(before, operation)))}
        # Validate before making the journal durable.
        apply_bytes(before, operation)
        value['operations'].append(previous)
        store.write(root, location, value)
    after = replay(value, include_prepared=True)
    if protected_bytes(current) not in (protected_bytes(before), protected_bytes(after)):
        raise ValueError('conflicting task edit; preserve evidence and diagnose')
    if protected_bytes(current) != protected_bytes(after):
        # Keep current, authorized status/updated_at changes from Phase 7.
        header = artifacts.FRONT.match(current).group(0)
        result = header + after[artifacts.FRONT.match(after).end():]
        temporary = path.with_name(path.name + '.runtime.tmp')
        temporary.write_bytes(result)
        store.replace(temporary, path)
    previous['status'] = 'applied'
    store.write(root, location, value)
    return value


def retire(context, feature):
    path = Path(context.path('specs/' + store.identifier(feature) + '/tasks.md'))
    root, location = locations(path)
    if (root / location).exists():
        value = store.read(root, location)
        archive = location.replace('active.json', value['plan_ref'] + '-history.json')
        store.write(root, archive, value)
        (root / location).unlink()
