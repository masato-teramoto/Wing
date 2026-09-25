"""Versioned Phase 8 files. No execution or approval policy."""
import hashlib
import json
from pathlib import Path
import re
import time

import artifacts

BASE = '.aidd/implementation'


def identifier(value):
    if not isinstance(value, str) or not re.fullmatch(r'[a-zA-Z0-9][a-zA-Z0-9_-]{0,95}', value):
        raise ValueError('invalid implementation identifier')
    return value


def digest(data):
    return hashlib.sha256(data).hexdigest()


def fingerprint(value):
    return digest(json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(',', ':')).encode())


def read(root, path):
    value = json.loads(artifacts.resolve(root, path).read_text(encoding='utf-8'))
    if not isinstance(value, dict) or value.get('schema') != 1:
        raise ValueError('unsupported implementation evidence: ' + path)
    return value


def write(root, path, value):
    target = artifacts.resolve(root, path)
    target.parent.mkdir(parents=True, exist_ok=True)
    temporary = target.with_name(target.name + '.tmp')
    temporary.write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    replace(temporary, target)


def replace(temporary, target):
    # Windows scanners can briefly hold a newly replaced JSON file. A bounded
    # retry preserves the same atomic operation; permanent denial still fails.
    for attempt in range(6):
        try:
            temporary.replace(target)
            return
        except PermissionError as error:
            if getattr(error, 'winerror', None) not in (5, 32, 33) or attempt == 5:
                raise
            time.sleep(0.02 * (2 ** attempt))


def execution_path(execution_id):
    return BASE + '/runs/' + identifier(execution_id) + '/execution.json'


def request_path(request_id):
    return BASE + '/requests/' + identifier(request_id) + '.json'


def item_path(item):
    return BASE + '/task-items/' + identifier(item) + '.json'


def current_execution(context):
    binding = read(context.root, item_path(context.item))
    value = read(context.root, execution_path(binding['execution_id']))
    if (binding.get('task_item') != context.item or value.get('task_item') != context.item
            or any(binding.get(key) != value.get(key) for key in
                   ('execution_id', 'feature', 'task_id', 'plan_ref'))):
        raise ValueError('execution belongs to another task item')
    return value


def empty_revision(context, execution):
    return context.event == 'implement-authoring-revise' and execution['event'] == 'implement-authoring-generate'


def read_execution(context):
    value = current_execution(context)
    if value['event'] != context.event and not empty_revision(context, value):
        raise ValueError('execution belongs to another event/item')
    return value


def require_execution(context, payload, allow_finished=False):
    value = read_execution(context)
    if payload.get('execution_id') != value['execution_id'] or context.event != value['event']:
        raise ValueError('action needs the current execution_id and work event')
    if not value.get('activated'):
        raise ValueError('resume implementation request activation first')
    if value.get('end_checked') and not allow_finished:
        raise ValueError('work event already checked; use explicit retry for further edits')
    return value
