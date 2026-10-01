"""L4 case-level specification contract and deterministic Markdown rendering.

A collector supplies the complete current case inventory and input fingerprints.
A generator supplies only additions and field patches. This module does not infer
assertions, approve quality, call an LLM/MCP, or write workflow state.
"""
import copy
import hashlib
import html
import json
import re

FIELDS = (
    ('title', '名称'), ('purpose', '目的'), ('requirement', '要件・設計'),
    ('category', '分類'), ('preconditions', '前提'), ('steps', '入力・操作'),
    ('expected', '期待結果'), ('reference', '実テスト'),
)
FIELD_NAMES = {name for name, _ in FIELDS}
CHANGE_LISTS = ('added', 'updated', 'removed', 'unchanged', 'revalidated')
SNAPSHOT_FIELDS = {'schema', 'scope', 'input_sha256', 'cases', 'markdown',
                   'body_sha256', 'previous_sha256', 'changes', 'snapshot_sha256'}


def _text(value, name, single_line=False):
    if (not isinstance(value, str) or not value.strip()
            or any(ord(c) < 32 and c not in '\n\t' for c in value)
            or (single_line and ('\n' in value or '\t' in value))):
        raise ValueError(name + ' must be nonblank text' + (' on one line' if single_line else ''))
    return value


def _hash(value, name):
    if not isinstance(value, str) or not re.fullmatch('[0-9a-f]{64}', value):
        raise ValueError(name + ' must be a SHA-256 digest')
    return value


def _object(value, name, keys=None):
    if not isinstance(value, dict) or (keys is not None and set(value) != keys):
        raise ValueError(name + ' has invalid fields')


def _digest(data):
    return hashlib.sha256(data).hexdigest()


def _fingerprint(value):
    return _digest(json.dumps(value, ensure_ascii=False, sort_keys=True,
                              separators=(',', ':'), allow_nan=False).encode('utf-8'))


def _content(value, partial=False):
    _object(value, 'case content')
    if (not set(value) <= FIELD_NAMES) or (not partial and set(value) != FIELD_NAMES):
        raise ValueError('case content has missing or unknown fields')
    for name, text in value.items():
        _text(text, name, single_line=name in ('title', 'category', 'reference'))


def _literal(value):
    # Descriptions are text, not arbitrary HTML, links, or Markdown headings.
    return re.sub(r'([\\`*_{}\[\]()#+.!|>~-])', r'\\\1', html.escape(value, quote=False))


def _rows(value):
    """One table row per line. Line text is kept as written: a leading -1, 1.5 or
    requirement number is content, so nothing but surrounding blanks is removed."""
    return [_literal(line.strip()) for line in value.split('\n') if line.strip()]


def _render(scope, cases):
    """Render the suite as 区分/内容 tables from the existing fields only.

    Module details, expected-result kinds, parameter tables and requirement
    mismatches have no source field and are therefore not shown.
    """
    parts = ['# 単体テスト仕様書\n\n## ' + _literal(scope) + '\n']
    if not cases:
        parts.append('\nこの範囲の現行ケースはありません。\n')
    for case in cases:
        fields = case['content']
        steps = _rows(fields['steps'])
        rows = [('目的', ' '.join(_rows(fields['purpose']))), ('分類', _literal(fields['category'])),
                ('要件・設計', ' '.join(_rows(fields['requirement'])))]
        rows += [('前提', row) for row in _rows(fields['preconditions'])]
        rows += ([('入力・操作', steps[0])] if len(steps) == 1
                 else [('入力・操作（%d）' % n, step) for n, step in enumerate(steps, 1)])
        rows += [('期待結果', row) for row in _rows(fields['expected'])]
        rows += [('実テスト', _literal(fields['reference'])), ('ケースID', _literal(case['id']))]
        parts.append('\n### ' + _literal(fields['title']) + '\n\n| 区分 | 内容 |\n|---|---|\n')
        parts.append(''.join('| %s | %s |\n' % row for row in rows))
    return ''.join(parts)


def _render_legacy(scope, cases):
    """Pre-table layout; still accepted for snapshots saved before the change."""
    parts = ['# 単体テスト仕様書\n\n対象: ' + _literal(scope) + '\n']
    if not cases:
        parts.append('\nこの範囲の現行ケースはありません。\n')
    for case in cases:
        fields = case['content']
        parts.append('\n## ' + _literal(fields['title']) + '\n\n')
        parts.append('- ケースID: ' + _literal(case['id']) + '\n')
        for name, label in FIELDS:
            if name != 'title':
                parts.append('- ' + label + ': ' + _literal(fields[name]).replace('\n', '\n  ') + '\n')
    return ''.join(parts)


def validate_snapshot(value):
    """Check structure, rendering, and hashes; not provenance or semantic quality."""
    _object(value, 'specification snapshot', SNAPSHOT_FIELDS)
    if type(value['schema']) is not int or value['schema'] != 1:
        raise ValueError('unsupported specification schema')
    _text(value['scope'], 'scope', single_line=True)
    for key in ('input_sha256', 'body_sha256', 'snapshot_sha256'):
        _hash(value[key], key)
    if value['previous_sha256'] is not None:
        _hash(value['previous_sha256'], 'previous_sha256')
    if not isinstance(value['cases'], list):
        raise ValueError('cases must be an array')
    ids = set()
    for row in value['cases']:
        _object(row, 'case', {'id', 'input_sha256', 'content'})
        _text(row['id'], 'case ID', single_line=True)
        if row['id'] in ids:
            raise ValueError('duplicate case ID')
        ids.add(row['id'])
        _hash(row['input_sha256'], 'case input_sha256')
        _content(row['content'])
    _object(value['changes'], 'changes', set(CHANGE_LISTS) | {'corrections'})
    for key in CHANGE_LISTS:
        entries = value['changes'][key]
        if not isinstance(entries, list):
            raise ValueError('change IDs must be arrays')
        for entry in entries:
            _text(entry, 'change ID', single_line=True)
        if len(entries) != len(set(entries)):
            raise ValueError('duplicate change ID')
    _object(value['changes']['corrections'], 'corrections')
    for key, reason in value['changes']['corrections'].items():
        _text(key, 'correction ID', single_line=True)
        _text(reason, 'correction reason')
    # A legacy body stays valid as history; the next update re-renders as tables.
    if value['markdown'] not in (_render(value['scope'], value['cases']), _render_legacy(value['scope'], value['cases'])):
        raise ValueError('specification body differs from case content')
    if value['body_sha256'] != _digest(value['markdown'].encode('utf-8')):
        raise ValueError('specification body digest differs')
    unsigned = {k: v for k, v in value.items() if k != 'snapshot_sha256'}
    if value['snapshot_sha256'] != _fingerprint(unsigned):
        raise ValueError('specification snapshot digest differs')


def update_specification(previous, *, scope, input_sha256, inventory,
                         additions=None, updates=None, corrections=None):
    """Return a new snapshot without mutating the prior one or any arguments.

    inventory maps stable runner/parameter IDs to hashes of relevant test,
    fixture, configuration and requirement inputs. Code-only changes may change
    input_sha256 without changing these case hashes. An affected existing case
    requires a patch ({} explicitly means rechecked, no description change).
    corrections contains reasons supplied by the coordinator, not the generator.
    Missing inventory entries remove cases; new cases append in ID order.
    """
    _text(scope, 'scope', single_line=True)
    _hash(input_sha256, 'input_sha256')
    _object(inventory, 'inventory')
    for key, fingerprint in inventory.items():
        _text(key, 'case ID', single_line=True)
        _hash(fingerprint, 'case input_sha256')
    additions = {} if additions is None else additions
    updates = {} if updates is None else updates
    corrections = {} if corrections is None else corrections
    for name, values in (('additions', additions), ('updates', updates), ('corrections', corrections)):
        _object(values, name)
        for key in values:
            _text(key, name + ' case ID', single_line=True)
    old = {}
    if previous is not None:
        validate_snapshot(previous)
        if previous['scope'] != scope:
            raise ValueError('cannot update a different specification scope')
        old = {row['id']: row for row in previous['cases']}
    current, existing = set(inventory), set(old)
    surviving = current & existing
    if set(additions) != current - existing:
        raise ValueError('additions must exactly match new inventory cases')
    if not set(corrections) <= surviving:
        raise ValueError('corrections must name surviving cases')
    for reason in corrections.values():
        _text(reason, 'correction reason')
    affected = {key for key in surviving if inventory[key] != old[key]['input_sha256']}
    affected.update(corrections)
    if set(updates) - affected:
        raise ValueError('generator patch targets an unaffected case')
    if affected - set(updates):
        raise ValueError('affected cases require explicit re-evaluation')
    for content in additions.values():
        _content(content)
    for patch in updates.values():
        _content(patch, partial=True)

    changes = {key: [] for key in CHANGE_LISTS}
    changes['corrections'] = copy.deepcopy(corrections)
    cases = []
    for key, row in old.items():
        if key not in current:
            changes['removed'].append(key)
            continue
        content = {**row['content'], **updates.get(key, {})}
        cases.append({'id': key, 'input_sha256': inventory[key], 'content': content})
        changes['updated' if content != row['content'] else 'unchanged'].append(key)
        if key in affected:
            changes['revalidated'].append(key)
    for key in sorted(additions):
        cases.append({'id': key, 'input_sha256': inventory[key], 'content': copy.deepcopy(additions[key])})
        changes['added'].append(key)
    markdown = _render(scope, cases)
    value = {'schema': 1, 'scope': scope, 'input_sha256': input_sha256, 'cases': cases,
             'markdown': markdown, 'body_sha256': _digest(markdown.encode('utf-8')),
             'previous_sha256': previous['snapshot_sha256'] if previous is not None else None,
             'changes': changes}
    value['snapshot_sha256'] = _fingerprint(value)
    return value
