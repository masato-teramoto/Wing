"""Language detection + explicit-override precedence (T023, FR-019).

Explicit caller-supplied language always wins; otherwise detect from the script used.
"""

from __future__ import annotations

import re

from ..models import Language
from ..nlp.base import Analyzer
from ..nlp.english import EnglishAnalyzer
from ..nlp.japanese import JapaneseAnalyzer

_CJK_RE = re.compile(r"[぀-ヿ぀-ゟ゠-ヿ一-龥]")
_LATIN_RE = re.compile(r"[A-Za-z]")

_ANALYZERS: dict[Language, Analyzer] = {
    Language.EN: EnglishAnalyzer(),
    Language.JA: JapaneseAnalyzer(),
}


def configure_japanese_analyzer(name: str) -> None:
    """JA Analyzerの明示選択（P2Q。既定はregex＝従来挙動）。

    "sudachi"はFR-039解釈（spec Clarifications 2026-08-10）の条件付き許可に
    基づく品詞ベース実装。未導入環境ではfail-closed（silent fallback禁止）で
    QualityAnalyzerUnavailableを送出する。
    """
    if name == "regex":
        _ANALYZERS[Language.JA] = JapaneseAnalyzer()
        return
    if name == "sudachi":
        from ..nlp.japanese_sudachi import SudachiJapaneseAnalyzer
        _ANALYZERS[Language.JA] = SudachiJapaneseAnalyzer()
        return
    raise ValueError(f"unknown japanese analyzer: {name}")


def detect_language(text: str, explicit: str | None = None) -> Language:
    """Resolve language: explicit override beats detection (FR-019)."""
    if explicit:
        try:
            lang = Language(explicit.lower())
        except ValueError as exc:
            raise ValueError(f"Unsupported language '{explicit}'") from exc
        if lang in (Language.EN, Language.JA):
            return lang
    if _CJK_RE.search(text):
        return Language.JA
    if _LATIN_RE.search(text):
        return Language.EN
    return Language.UNDETERMINED


def analyzer_for(language: Language) -> Analyzer | None:
    return _ANALYZERS.get(language)
