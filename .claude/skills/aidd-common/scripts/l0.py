"""L0 の枠組み（`bin/`・`lib/`）を import できるようにする。L3・L4 の script は L0 を import してよい（逆はしない）。

配布物では `aidd-common/scripts/`（L3・L4）の隣に `aidd-common/bin/`・`lib/`（L0）がある。
L0 の module（`project_state` / `execution_context` / `engine_cli` など）を import する前に `import l0` を置く。
"""
import os
import sys

COMMON = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
for _path in (os.path.join(COMMON, "lib"), os.path.join(COMMON, "bin")):
    if _path not in sys.path:
        sys.path.insert(1, _path)
