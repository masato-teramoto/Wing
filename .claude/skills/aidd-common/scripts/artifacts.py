"""Artifact status and protected content. No phase or approval policy lives here."""

import hashlib
import os
from pathlib import Path, PurePosixPath
import re

FRONT = re.compile(rb"\A---\r?\n(.*?)\r?\n---(?:\r?\n|$)", re.S)
MUTABLE = re.compile(rb"^(status|updated_at)\s*:")


def relative_path(value):
    if not isinstance(value, str) or not value or "\\" in value or ":" in value:
        raise ValueError("project-relative path required: %r" % value)
    path = PurePosixPath(value)
    if path.is_absolute() or ".." in path.parts or path.as_posix() != value or value == ".":
        raise ValueError("non-canonical artifact path: %r" % value)
    return value


def resolve(root, value):
    relative_path(value)
    base = Path(root).resolve()
    target = base / value
    if not target.resolve().is_relative_to(base):
        raise ValueError("artifact escapes project: %s" % value)
    return target


def fields(path):
    path = Path(path)
    if not path.exists():
        return None
    match = FRONT.match(path.read_bytes())
    if not match:
        raise ValueError("frontmatter missing: %s" % path)
    result = {}
    for line in match.group(1).decode("utf-8").splitlines():
        if not line or line.startswith((" ", "\t", "#")) or ":" not in line:
            continue
        key, value = line.split(":", 1)
        key = key.strip()
        if key in result:
            raise ValueError("duplicate frontmatter key %s: %s" % (key, path))
        result[key] = value.strip().strip("\"'")
    return result


def protected_digest(path):
    data = Path(path).read_bytes()
    if Path(path).name == 'tasks.md':
        import task_runtime
        data = task_runtime.project(path, data)
    return protected_bytes_digest(data)


def protected_bytes_digest(data):
    match = FRONT.match(data)
    if not match:
        raise ValueError("frontmatter missing in protected artifact bytes")
    # Preserve body and every metadata field except the two authorized keys.
    header = b"\n".join(line for line in match.group(1).splitlines() if not MUTABLE.match(line))
    return hashlib.sha256(header + b"\n---\n" + data[match.end():]).hexdigest()


def set_status(path, status, timestamp):
    path = Path(path)
    updated = status_bytes(path, status, timestamp)
    temporary = path.with_name(path.name + ".tmp")
    temporary.write_bytes(updated)
    os.replace(temporary, path)


def status_bytes(path, status, timestamp):
    if status not in ("draft", "review", "approved"):
        raise ValueError("unknown artifact status")
    path = Path(path)
    data = path.read_bytes()
    fields(path)
    match = FRONT.match(data)
    if not match:
        raise ValueError("frontmatter missing: %s" % path)
    newline = b"\r\n" if b"\r\n" in match.group(0) else b"\n"
    lines = [line for line in match.group(1).splitlines() if not MUTABLE.match(line)]
    lines += [("status: " + status).encode(), ("updated_at: " + timestamp).encode()]
    updated = b"---" + newline + newline.join(lines) + newline + b"---" + newline + data[match.end():]
    return updated
