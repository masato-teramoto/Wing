"""rimay-jp-core: Rimay-JP 決定論的コアライブラリ（Phase 2 最小縦断スライス）。

LLM・MCP・特定知識基盤へ依存しない。構想書v0.5の契約
（CanonicalPointer/RuleSelector分離、リーフ粒度resolution、unknown非格納）に従う。
"""

SCHEMA_VERSION = "1.2.0"  # 1.2.0: versions_usedへProfile内容hashをadditive公開
PROFILE_VERSION = "rimay-jp-mvp-0.5.0"  # 0.5.0: Operator value expression英日runtime
__version__ = "0.14.0"  # 0.14.0: Canonical 1.2 Schema closure／1.1互換reader

# Phase 2 縦断スライス（構想書 §21 Phase 2 初期対象）
PHASE2_CONDITIONS = {"WHEN", "IF"}
PHASE2_FAMILIES = {"SEND", "UPDATE"}

# Supported Profile v0.1（MVP全体。スライス外だがMVP内は PROFILE-OUT ではなく slice-out）
MVP_CONDITIONS = {"WHEN", "IF", "WHILE", "BEFORE", "AFTER"}
