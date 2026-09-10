"""Deterministic English analyzer (T021).

Implements the paper's detection *criteria* (FR-020) with a dependency-light lexicon +
morphology, no external models. Pure functions of the input → reproducible (FR-015/FR-016).
"""

from __future__ import annotations

import re

from .base import Token, simple_tokenize

MODALS = {"must", "shall", "should", "will", "may", "can", "should"}
BE_FORMS = {"is", "are", "was", "were", "be", "been", "being", "am"}
# Past participles that are not regular -ed forms (enough for the rule examples).
IRREGULAR_PPL = {
    "set", "sent", "received", "taken", "made", "given", "done", "shown", "written",
    "read", "built", "held", "kept", "met", "paid", "put", "seen", "told", "found",
    "drawn", "known", "chosen", "left", "lost", "run", "begun",
}
# Common requirement verbs (base + frequent inflections). Nominalizations (e.g. "reception",
# "creation") and gerunds ("creating") are intentionally absent => treated as "no finite verb".
VERB_LEXICON = {
    "receive", "receives", "send", "sends", "create", "creates", "click", "clicks",
    "validate", "validates", "store", "stores", "update", "updates", "display", "displays",
    "set", "sets", "contain", "contains", "have", "has", "submit", "submits", "request",
    "requests", "open", "opens", "add", "adds", "allow", "allows", "subscribe", "subscribes",
    "raise", "raises", "process", "processes", "handle", "handles", "perform", "performs",
    "support", "supports", "remove", "removes", "delete", "deletes", "populate", "populates",
    "launch", "launches", "cancel", "cancels", "define", "defines", "upload", "uploads",
}
COMMON_ACTOR_WORDS = {"system", "user", "application", "server", "service", "operator", "customer"}


def _lemma(word: str) -> str:
    w = word.lower()
    if w in VERB_LEXICON:
        # crude de-inflection for -s third person
        if w.endswith("es") and (w[:-2] in VERB_LEXICON):
            return w[:-2]
        if w.endswith("s") and (w[:-1] in VERB_LEXICON):
            return w[:-1]
        return w
    return w


class EnglishAnalyzer:
    lang = "en"
    CONDITION_MARKERS = ("when", "if", "while", "where", "until", "upon", "once", "after", "before")
    SCOPE_MARKERS = ("for",)
    RESPONSE_SEPARATORS = ("then", ";", "\n")

    def tokenize(self, text: str) -> list[Token]:
        return simple_tokenize(text)

    def has_modal(self, text: str) -> bool:
        return any(t.lower in MODALS for t in self.tokenize(text))

    def has_actor(self, text: str) -> bool:
        toks = self.tokenize(text)
        for i, t in enumerate(toks):
            if t.lower in COMMON_ACTOR_WORDS:
                return True
            # Capitalized non-initial token, or hyphenated proper noun like "System-A".
            if t.text[:1].isupper() and (i > 0 or "-" in t.text):
                return True
            if "-" in t.text and t.text[:1].isupper():
                return True
        # pronoun subjects
        return any(t.lower in {"it", "they", "he", "she"} for t in toks)

    def has_finite_verb(self, text: str) -> bool:
        for t in self.tokenize(text):
            w = t.lower
            if w in VERB_LEXICON:
                return True
            # regular past tense not ending in gerund
            if w.endswith("ed") and len(w) > 3:
                return True
        return False

    def action_count(self, text: str) -> int:
        """Count coordinated actions: multiple modals, or verbs split by ' and '."""
        modal_count = sum(1 for t in self.tokenize(text) if t.lower in MODALS)
        and_parts = re.split(r"\band\b", text)
        verb_parts = sum(1 for part in and_parts if self.has_finite_verb(part))
        return max(modal_count, verb_parts, 1 if self.has_finite_verb(text) else 0)

    def passive_spans(self, text: str) -> list[tuple[int, int, str]]:
        toks = self.tokenize(text)
        spans: list[tuple[int, int, str]] = []
        for i, t in enumerate(toks):
            if t.lower in BE_FORMS:
                # allow an adverb ("not") and/or "been" between be and participle
                for j in range(i + 1, min(i + 4, len(toks))):
                    cand = toks[j]
                    if cand.lower in ("not", "been", "being"):
                        continue
                    if self._is_past_participle(cand.text):
                        spans.append((t.start, cand.end, text[t.start : cand.end]))
                    break
        return spans

    @staticmethod
    def _is_past_participle(word: str) -> bool:
        w = word.lower()
        if w in IRREGULAR_PPL:
            return True
        return w.endswith("ed") and len(w) > 3

    def verb_lemmas(self, text: str) -> list[tuple[str, int, int]]:
        out: list[tuple[str, int, int]] = []
        for t in self.tokenize(text):
            if t.lower in VERB_LEXICON:
                out.append((_lemma(t.text), t.start, t.end))
        return out

    def find_glossary_hits(self, text: str, glossary: set[str]) -> list[tuple[str, int, int]]:
        hits: list[tuple[str, int, int]] = []
        for t in self.tokenize(text):
            if _lemma(t.text) in glossary:
                hits.append((_lemma(t.text), t.start, t.end))
        return hits

    def is_condition_clause(self, clause: str) -> bool:
        toks = self.tokenize(clause)
        return bool(toks) and toks[0].lower in self.CONDITION_MARKERS

    def is_scope_clause(self, clause: str) -> bool:
        toks = self.tokenize(clause)
        if len(toks) < 2 or toks[0].lower != "for":
            return False
        return toks[1].lower in {"each", "all", "none", "any", "every"}
