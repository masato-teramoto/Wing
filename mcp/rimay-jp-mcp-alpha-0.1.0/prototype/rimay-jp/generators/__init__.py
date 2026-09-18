"""rimay-generators: 承認済みCanonicalからの下流成果物生成（Phase 3E）。

承認済み（approved）要求だけを生成対象とし、Generatorが使用した
要求スロット・Rule・Provenanceをトレースとして記録する（GATE-3E）。
"""
import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[1]
for p in (str(_ROOT / "core"), str(_ROOT)):
    if p not in sys.path:
        sys.path.insert(0, p)
