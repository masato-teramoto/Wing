"""Alpha portability: compare execution locations relative to the project root.

Only location fields in execution/review envelopes are normalized. Business
payloads, dispatches and stored evidence bytes stay unchanged. A complete copy
of a workspace is intentionally treated as the same project.
"""
from pathlib import Path
import os


def binding(value):
    if not isinstance(value, dict):
        return value
    root, state = value.get('root'), value.get('state')
    if not all(isinstance(p, str) and Path(p).is_absolute() for p in (root, state)):
        return value
    try:
        relative = Path(os.path.normpath(state)).relative_to(Path(os.path.normpath(root)))
    except ValueError:
        return value  # External state stores retain their absolute binding.
    if relative == Path('.'):
        return value
    # A tuple cannot be confused with a malformed JSON envelope using a relative root.
    return relative.as_posix(), {key: item for key, item in value.items() if key not in ('root', 'state')}


def _resolved_binding(value):
    """Read legacy alias bindings only while their actual locations are available.

    The lexical comparison remains first, so ordinary relocation never depends
    on the old directory still existing. Do not infer a lost alias from a state
    filename or rewrite stored requests/evidence when resolving a live alias.
    """
    if isinstance(value, dict):
        root, state = value.get('root'), value.get('state')
        if all(isinstance(p, str) and Path(p).is_absolute() for p in (root, state)):
            try:
                resolved_root = Path(root).resolve(strict=True)
                resolved_state = Path(state).resolve(strict=True)
                if resolved_root.is_dir():
                    value = dict(value, root=str(resolved_root), state=str(resolved_state))
            except (OSError, RuntimeError, ValueError):
                pass  # Missing, inaccessible or looping aliases do not establish identity.
    return binding(value)


def same_binding(left, right):
    return (binding(left) == binding(right)
            or _resolved_binding(left) == _resolved_binding(right))


def request(value, *, resolve_aliases=False):
    if not isinstance(value, dict):
        return value
    normalize = _resolved_binding if resolve_aliases else binding
    normalized = dict(value)
    if isinstance(normalized.get('expected'), dict):
        normalized['expected'] = normalize(normalized['expected'])
    if isinstance(normalized.get('payload'), dict):
        payload = dict(normalized['payload'])
        if isinstance(payload.get('expected'), dict):
            payload['expected'] = normalize(payload['expected'])
        normalized['payload'] = payload
    return normalize(normalized)


def same_request(left, right):
    return (request(left) == request(right)
            or request(left, resolve_aliases=True) == request(right, resolve_aliases=True))


def relocated_file(name, previous_root, root):
    """Rebase an in-project dependency; leave external paths alone."""
    path = Path(name)
    if previous_root and path.is_absolute():
        try:
            relative = Path(os.path.normpath(name)).relative_to(Path(os.path.normpath(previous_root)))
        except ValueError:
            return path
        return Path(root) / relative
    return path
