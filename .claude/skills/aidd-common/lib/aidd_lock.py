"""Public, policy-free state lock shared by the CLI and its host adapters.

The OS releases the lock on process death. A nonce permits only nested child
commands to reuse a live parent's lease; no project file is created for locking.
"""
from contextlib import contextmanager
import hashlib
import json
import os
from pathlib import Path
import tempfile
import threading
import uuid

_SERIAL = threading.RLock()
_ENV = 'AIDD_STATE_LOCKS'


def _acquire(handle):
    handle.seek(0)
    if os.name == 'nt':
        import msvcrt
        msvcrt.locking(handle.fileno(), msvcrt.LK_NBLCK, 1)
    else:
        import fcntl
        fcntl.flock(handle.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)


def _release(handle):
    handle.seek(0)
    if os.name == 'nt':
        import msvcrt
        msvcrt.locking(handle.fileno(), msvcrt.LK_UNLCK, 1)
    else:
        import fcntl
        fcntl.flock(handle.fileno(), fcntl.LOCK_UN)


@contextmanager
def hold(state_path):
    key = hashlib.sha256(str(Path(state_path).resolve()).encode()).hexdigest()
    folder = Path(tempfile.gettempdir()) / 'aidd-state-locks'
    with _SERIAL:
        folder.mkdir(exist_ok=True)
        path = folder / (key + '.lock')
        old = os.environ.get(_ENV)
        leases = json.loads(old or '{}')
        with path.open('a+b') as handle:
            if path.stat().st_size == 0:
                handle.write(b' ')
                handle.flush()
            try:
                _acquire(handle)
            except OSError as error:
                handle.seek(1)
                recorded = handle.read().decode('utf-8').strip()
                if recorded and leases.get(key) == recorded:
                    yield
                    return
                raise ValueError('another operation is using this project; retry the same operation ID') from error
            token = uuid.uuid4().hex
            handle.seek(1)
            handle.truncate()
            handle.write(token.encode())
            handle.flush()
            leases[key] = token
            os.environ[_ENV] = json.dumps(leases)
            try:
                yield
            finally:
                handle.seek(1)
                handle.truncate()
                handle.flush()
                if old is None:
                    os.environ.pop(_ENV, None)
                else:
                    os.environ[_ENV] = old
                _release(handle)
