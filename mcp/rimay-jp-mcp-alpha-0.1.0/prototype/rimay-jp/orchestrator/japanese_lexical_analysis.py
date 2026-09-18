"""Lexical Analysis Provider境界（改善計画 v0.3 §5.1 / D2。ADR-0013整合）。

- Pre-Canonicalの補助的な語彙・形態情報の共有部品。Strict Core
  （rimay_jp_core）とQuality Core（quality/src/reqsmell）からはimportしない。
- Providerのロード失敗時に別Providerへsilent fallbackしない（§7.3:
  capability unavailableとして明示的に失敗させる）。
- Analyzer固有オブジェクトをCanonicalやObservationへ保存しない。
  呼び出し側が受け取るのは本モジュールのLexicalTokenとdictメタデータのみ。
"""
from __future__ import annotations

import hashlib
import re
from dataclasses import dataclass

# 現行document_term_extractorと同一の表層走査（baseline Provider。ADR-0014 P1）
_REGEX_TOKEN_PATTERN = r"[一-龥ァ-ヶーA-Za-z0-9]{2,}"


class LexicalCapabilityUnavailable(RuntimeError):
    """指定Providerをロードできない（fail-closed。silent fallback禁止）。"""


@dataclass(frozen=True)
class LexicalToken:
    """原文基準の形態素/表層トークン（v0.3 §5.1の最小フィールド）。"""
    surface: str
    start: int
    end: int
    part_of_speech: tuple
    dictionary_form: str
    normalized_form: str
    reading_form: str
    is_oov: bool


class RegexProvider:
    """現行の文字種連続正規表現をProvider契約へ載せたbaseline（P1-1）。

    形態素情報は持たない（part_of_speech=("REGEX",)、辞書形=正規化形=表層）。
    現行`document_term_extractor`のtoken列と同一のsurface/spanを返す。
    """

    provider_id = "regex"

    def __init__(self):
        self._re = re.compile(_REGEX_TOKEN_PATTERN)

    def analyze(self, text: str) -> list:
        return [LexicalToken(m.group(0), m.start(), m.end(), ("REGEX",),
                             m.group(0), m.group(0), "", False)
                for m in self._re.finditer(text)]

    def metadata(self) -> dict:
        return {
            "provider": "regex",
            "provider_version": "builtin",
            "pattern": _REGEX_TOKEN_PATTERN,
            "pattern_content_hash": "sha256:" + hashlib.sha256(
                _REGEX_TOKEN_PATTERN.encode("utf-8")).hexdigest(),
        }


def get_provider(name: str, *, dictionary: str = "core",
                 split_mode: str = "C"):
    """Provider解決（§7.3: 明示指定・fail-closed・自動切替禁止）。"""
    if name == "regex":
        return RegexProvider()
    if name == "sudachipy":
        try:
            from .sudachi_provider import SudachiProvider
            return SudachiProvider(dictionary=dictionary,
                                   split_mode=split_mode)
        except ImportError as e:  # 構築時のsudachipy/辞書不在もfail-closed
            raise LexicalCapabilityUnavailable(
                "provider 'sudachipy' をロードできません。"
                "pin済み依存（SudachiPy==0.6.11 / SudachiDict==20260723）を"
                f"導入してください: {e}") from e
    raise ValueError(f"unknown lexical provider: {name}")
