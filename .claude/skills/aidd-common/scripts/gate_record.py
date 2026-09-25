"""Read-only inventory of legacy evidence; never used to decide completion.

Legacy tables had ambiguous scopes/columns. Preserve every line rather than
padding malformed rows or interpreting an unreadable record as zero findings.
The executable v2 reader is record_format.parse.
"""
import argparse
import hashlib
import json
from pathlib import Path


def inspect(path):
    data = Path(path).read_bytes()
    text = data.decode('utf-8')
    return {'path': str(path), 'sha256': hashlib.sha256(data).hexdigest(),
            'format': 'v2' if any('format_version: 2' in part for part in text.split('---', 2)[1:2]) else 'unclassified',
            'lines': [{'line': n, 'text': line} for n, line in enumerate(text.splitlines(), 1)],
            'completion': 'not inferred; reconcile legacy findings explicitly'}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('path')
    args = parser.parse_args()
    print(json.dumps(inspect(args.path), ensure_ascii=False, indent=2))
