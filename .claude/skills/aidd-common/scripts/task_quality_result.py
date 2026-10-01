"""Provider-neutral L4 review receipt, not a quality or human approval decision.

The adapter must normalize actual engine output to this local contract. The
specification hash binds the attached human-readable artifact, not an extra
semantic review of that artifact. Missing or
unknown output is rejected instead of being treated as a clean review. Storage,
source verification, MCP transport and L0/L3 integration are separate concerns.
"""
import copy
from pathlib import PurePosixPath
import re

import unit_test_specification as specifications

TARGET_FIELDS = {'feature', 'plan_ref', 'task_id', 'task_item', 'execution_id',
                 'request_id', 'review_round', 'input_sha256', 'config_sha256'}
REVIEW_FIELDS = {'target', 'specification_sha256', 'status', 'engine', 'findings',
                 'reviewed_paths', 'unreviewed', 'error'}
FINDING_FIELDS = {'id', 'kind', 'severity', 'location', 'summary', 'evidence', 'suggestion'}


def _object(value, fields, name):
    if not isinstance(value, dict) or set(value) != fields:
        raise ValueError(name + ' has missing or unknown fields')


def _text(value, name):
    if not isinstance(value, str) or not value.strip() or '\x00' in value:
        raise ValueError(name + ' must be nonblank text')


def _target(value):
    _object(value, TARGET_FIELDS, 'review target')
    for key in TARGET_FIELDS - {'review_round'}:
        _text(value[key], key)
    for key in ('plan_ref', 'input_sha256', 'config_sha256'):
        if not re.fullmatch('[0-9a-f]{64}', value[key]):
            raise ValueError(key + ' must be a SHA-256 digest')
    if type(value['review_round']) is not int or value['review_round'] < 1:
        raise ValueError('review_round must be a positive integer')


def build_result(target, specification, review):
    """Bind an inspection result and readable specification to the same input.

    Both completed reviews (including zero findings) and review failures require
    a valid specification. A generation failure cannot produce this receipt.
    completed means the review returned, not that its findings or scope passed.
    """
    _target(target)
    specifications.validate_snapshot(specification)
    if specification['input_sha256'] != target['input_sha256']:
        raise ValueError('specification belongs to a different input')
    _object(review, REVIEW_FIELDS, 'review')
    _target(review['target'])
    if review['target'] != target:
        raise ValueError('review belongs to a different target')
    if review['specification_sha256'] != specification['snapshot_sha256']:
        raise ValueError('review belongs to a different specification snapshot')
    if review['status'] not in ('completed', 'error'):
        raise ValueError('review status must be completed or error')
    _object(review['engine'], {'provider', 'tool', 'version'}, 'engine')
    for key, value in review['engine'].items():
        _text(value, 'engine ' + key)
    if not isinstance(review['findings'], list):
        raise ValueError('findings must be an array')
    ids = set()
    for finding in review['findings']:
        _object(finding, FINDING_FIELDS, 'finding')
        for key, value in finding.items():
            _text(value, 'finding ' + key)
        if finding['id'] in ids:
            raise ValueError('duplicate finding ID')
        ids.add(finding['id'])
        if finding['kind'] not in ('tests', 'implementation'):
            raise ValueError('unknown finding kind')
        if finding['severity'] not in ('critical', 'major', 'minor', 'info'):
            raise ValueError('unknown finding severity')
    for key in ('reviewed_paths', 'unreviewed'):
        if not isinstance(review[key], list):
            raise ValueError(key + ' must be an array')
        for value in review[key]:
            _text(value, key + ' entry')
    for path in review['reviewed_paths']:
        parsed = PurePosixPath(path)
        if (parsed.is_absolute() or path != parsed.as_posix() or '..' in parsed.parts
                or not parsed.parts or '\\' in path or ':' in path):
            raise ValueError('reviewed paths must be canonical project-relative file paths')
    if len(review['reviewed_paths']) != len(set(review['reviewed_paths'])):
        raise ValueError('duplicate reviewed path')
    if review['status'] == 'completed':
        if not review['reviewed_paths'] or review['error'] is not None:
            raise ValueError('completed review needs an actual scope and no execution error')
    else:
        _object(review['error'], {'kind', 'message'}, 'review error')
        for value in review['error'].values():
            _text(value, 'error detail')
    return copy.deepcopy({'schema': 1, 'target': target,
                          'specification': specification, 'review': review})
