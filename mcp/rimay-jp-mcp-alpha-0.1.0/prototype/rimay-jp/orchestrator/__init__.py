"""rimay-orchestrator: 要求形成オーケストレーション層（Phase 3）。

コアライブラリ（rimay_jp_core）を呼び出し、構文判定を重複実装しない。
Phase 3Aは決定論的ルールで実装する。LLMを接続する場合も、出力は
canonical/source-analysis.schema.json の契約に適合させ、確定はしない。
"""
import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[1]
if str(_ROOT / "core") not in sys.path:
    sys.path.insert(0, str(_ROOT / "core"))
