"""NLP analyzer protocol + shared token type (T020).

The engine and detectors depend ONLY on this protocol, never on a concrete NLP library.
v1 ships deterministic, dependency-light analyzers (english.py, japanese.py). A spaCy/GiNZA
analyzer could implement the same protocol later without touching the engine or rules.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Protocol, runtime_checkable


@dataclass(frozen=True)
class Token:
    text: str
    start: int
    end: int

    @property
    def lower(self) -> str:
        return self.text.lower()


_WORD_RE = re.compile(r"\w[\w'-]*", re.UNICODE)


def simple_tokenize(text: str) -> list[Token]:
    """Whitespace/punctuation tokenizer with character offsets (deterministic)."""
    return [Token(m.group(0), m.start(), m.end()) for m in _WORD_RE.finditer(text)]


@runtime_checkable
class Analyzer(Protocol):
    """Linguistic predicates the detectors need, per language."""

    lang: str

    # Lexical markers (lowercase) used by segmentation.
    CONDITION_MARKERS: tuple[str, ...]
    SCOPE_MARKERS: tuple[str, ...]
    RESPONSE_SEPARATORS: tuple[str, ...]

    def tokenize(self, text: str) -> list[Token]:
        ...

    def has_modal(self, text: str) -> bool:
        ...

    def has_actor(self, text: str) -> bool:
        ...

    def has_finite_verb(self, text: str) -> bool:
        ...

    def action_count(self, text: str) -> int:
        """Number of coordinated actions in a system response (>1 => non-atomic)."""
        ...

    def passive_spans(self, text: str) -> list[tuple[int, int, str]]:
        """(start, end, matched_text) char spans of passive-voice constructions."""
        ...

    def verb_lemmas(self, text: str) -> list[tuple[str, int, int]]:
        """(lemma, start, end) for verb-like tokens, for glossary matching."""
        ...

    def find_glossary_hits(
        self, text: str, glossary: set[str]
    ) -> list[tuple[str, int, int]]:
        """(matched_term, start, end) for glossary terms occurring in ``text``."""
        ...

    def is_condition_clause(self, clause: str) -> bool:
        ...

    def is_scope_clause(self, clause: str) -> bool:
        ...
