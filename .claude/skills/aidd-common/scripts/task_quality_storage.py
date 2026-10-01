"""Immutable, narrowly located review artifacts. No workflow or approval policy."""
import json
import os
import re
import uuid

import implementation_reports as reports
import implementation_store as store
import unit_test_specification as specifications

NAMES = {'request.json', 'specification.json', 'specification.md', 'result.json',
         'summary.md', 'manifest.json', 'response.json', 'acceptance.json',
         'code-request.json', 'code-review.json', 'code-summary.md', 'code-manifest.json',
         'code-response.json', 'code-acceptance.json', 'code-preparation.json',
         'mcp-request.json', 'mcp-response.json', 'mcp-review.json', 'mcp-summary.md', 'mcp-manifest.json'}


def directory(execution_id, round_number):
    if type(round_number) is not int or round_number < 1:
        raise ValueError('review round must be a positive integer')
    return store.BASE + '/runs/' + store.identifier(execution_id) + '/reviews/' + str(round_number)


def path(root, execution_id, round_number, name):
    if name not in NAMES and not re.fullmatch(r'mcp-file-[0-9a-f]{32}\.json', name):
        raise ValueError('unsupported task quality artifact')
    return reports.plain_file(root, directory(execution_id, round_number) + '/' + name)


def encoded(value):
    return (json.dumps(value, ensure_ascii=False, sort_keys=True, indent=2, allow_nan=False) + '\n').encode('utf-8')


def write_once(root, execution_id, round_number, name, value):
    data = value if isinstance(value, bytes) else encoded(value)
    target = path(root, execution_id, round_number, name)
    if target.exists():
        if target.read_bytes() != data:
            raise ValueError('immutable task quality artifact differs: ' + name)
        return store.digest(data)
    target.parent.mkdir(parents=True, exist_ok=True)
    temporary = target.with_name('.quality-' + uuid.uuid4().hex + '.tmp')
    try:
        temporary.write_bytes(data)
        try:
            # Publish a complete file without ever replacing an existing round,
            # including when another writer created the name after our check.
            os.link(temporary, target)
        except FileExistsError:
            if target.read_bytes() != data:
                raise ValueError('immutable task quality artifact differs: ' + name)
    finally:
        temporary.unlink(missing_ok=True)
    return store.digest(data)


def read(root, execution_id, round_number, name):
    return json.loads(path(root, execution_id, round_number, name).read_bytes())


def save_bundle(root, execution_id, round_number, result, summary):
    specification = result['specification']
    specifications.validate_snapshot(specification)
    files = {
        'specification.json': specification,
        'specification.md': specification['markdown'].encode('utf-8'),
        'result.json': result,
        'summary.md': summary.encode('utf-8'),
    }
    hashes = {name: write_once(root, execution_id, round_number, name, value) for name, value in files.items()}
    hashes['request.json'] = store.digest(path(root, execution_id, round_number, 'request.json').read_bytes())
    manifest = {'schema': 1, 'files': hashes}
    write_once(root, execution_id, round_number, 'manifest.json', manifest)
    return manifest


def load_bundle(root, execution_id, round_number):
    manifest = read(root, execution_id, round_number, 'manifest.json')
    expected = {'request.json', 'specification.json', 'specification.md', 'result.json', 'summary.md'}
    if manifest.get('schema') != 1 or set(manifest.get('files', {})) != expected:
        raise ValueError('invalid task quality manifest')
    for name, digest in manifest['files'].items():
        if store.digest(path(root, execution_id, round_number, name).read_bytes()) != digest:
            raise ValueError('task quality artifact changed: ' + name)
    result = read(root, execution_id, round_number, 'result.json')
    specification = read(root, execution_id, round_number, 'specification.json')
    specifications.validate_snapshot(specification)
    if (result.get('specification') != specification
            or path(root, execution_id, round_number, 'specification.md').read_bytes() != specification['markdown'].encode('utf-8')):
        raise ValueError('specification and review result differ')
    return result, manifest
