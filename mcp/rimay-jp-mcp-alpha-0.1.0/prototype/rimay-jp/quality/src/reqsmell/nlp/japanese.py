"""Deterministic Japanese analyzer (T022).

Reuses the paper's smell *definitions* but with a Japanese detection basis (FR-020):
受身 (passive) auxiliaries, obligation endings (〜しなければならない), 助詞-marked subjects,
and a Japanese vague-verb glossary. Pattern-based and pure → reproducible (FR-015/FR-016).
Full morphological analysis (e.g. GiNZA) can replace this behind the Analyzer protocol later.
"""

from __future__ import annotations

import re

from .base import Token, simple_tokenize

# Obligation / requirement endings (the Japanese analogue of a modal verb).
MODAL_PATTERNS = ("しなければならない", "なければならない", "ねばならない", "しなければなりません",
                  "するものとする", "すること", "必要がある")
PASSIVE_RE = re.compile(r"(されている|された|される|られた|られる|れた|れる)")
# Subject marked by は / が preceded by a noun-ish run (kanji/kana/katakana/latin).
SUBJECT_RE = re.compile(r"[\wァ-ヶ一-龥ー]+(は|が)")
# Verb tail: する-forms, passive forms, or a dictionary-form verb ending (う-row kana)
# / past た, immediately before a clause boundary or end of string.
VERB_TAIL_RE = re.compile(r"(する|した|します|される|られる|た|[うくぐすつぬぶむる])([。、]|$)")
_COORD_TOKENS = ("し、", "たり", "および", "かつ")


class JapaneseAnalyzer:
    lang = "ja"
    # NOTE: 「なら」「ば」 are intentionally excluded — they occur inside the obligation
    # ending 「〜しなければならない」 and would misclassify responses as conditions.
    CONDITION_MARKERS = ("とき", "場合", "際", "たら")
    SCOPE_MARKERS = ("ごとに", "すべての", "各")
    RESPONSE_SEPARATORS = ("、then", "；", "\n")

    def tokenize(self, text: str) -> list[Token]:
        return simple_tokenize(text)

    def has_modal(self, text: str) -> bool:
        return any(p in text for p in MODAL_PATTERNS)

    def has_actor(self, text: str) -> bool:
        return bool(SUBJECT_RE.search(text))

    def has_finite_verb(self, text: str) -> bool:
        # する/した/される forms may appear mid-clause (e.g. 「受信したとき」), so detect them
        # anywhere; otherwise require a dictionary-form verb tail at a clause boundary.
        if re.search(r"(する|した|します|される|られる|られた)", text):
            return True
        return bool(VERB_TAIL_RE.search(text)) or self.has_modal(text)

    def action_count(self, text: str) -> int:
        # Count the core obligation ending once (しなければならない CONTAINS なければならない).
        modal_count = text.count("なければならない") + text.count("すること")
        # coordinated predicates joined by 〜し、 / 〜たり / および / かつ
        coord = sum(text.count(tok) for tok in _COORD_TOKENS)
        base = 1 if self.has_finite_verb(text) else 0
        return max(modal_count, base + (1 if coord else 0), base)

    def passive_spans(self, text: str) -> list[tuple[int, int, str]]:
        return [(m.start(), m.end(), m.group(0)) for m in PASSIVE_RE.finditer(text)]

    def verb_lemmas(self, text: str) -> list[tuple[str, int, int]]:
        # Not used for JA glossary matching; see find_glossary_hits.
        return []

    def find_glossary_hits(self, text: str, glossary: set[str]) -> list[tuple[str, int, int]]:
        hits: list[tuple[str, int, int]] = []
        for term in sorted(glossary):  # sorted => deterministic ordering
            start = text.find(term)
            while start != -1:
                hits.append((term, start, start + len(term)))
                start = text.find(term, start + 1)
        hits.sort(key=lambda h: h[1])
        return hits

    def is_condition_clause(self, clause: str) -> bool:
        return any(m in clause for m in self.CONDITION_MARKERS)

    def is_scope_clause(self, clause: str) -> bool:
        return any(m in clause for m in self.SCOPE_MARKERS)
