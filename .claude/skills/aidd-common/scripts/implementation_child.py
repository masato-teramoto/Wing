"""Windows launch barrier: start the command only after job assignment."""
import subprocess
import sys

if __name__ == '__main__':
    if sys.stdin.buffer.read(1) != b'G':
        raise SystemExit(126)
    try:
        raise SystemExit(subprocess.call(sys.argv[1:]))
    except OSError as error:
        print(str(error), file=sys.stderr)
        raise SystemExit(127)
