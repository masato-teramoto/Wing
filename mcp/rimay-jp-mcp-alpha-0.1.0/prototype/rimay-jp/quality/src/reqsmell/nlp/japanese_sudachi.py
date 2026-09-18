"""POS-based Japanese analyzer (P2Q, improvement plan v0.3).

Deterministic, offline, dictionary-based analysis via SudachiPy + SudachiDict-core,
permitted under the FR-039 interpretation (spec Clarifications Session 2026-08-10;
ADR-0013 追記): pinned provider/dictionary/config with content hashes, byte-identical
across environments, fail-closed, footprint disclosed. No trained-model runtime
inference; GiNZA/spaCy remain forbidden in the execution system.

Fixes the known false judgments of the regex ``JapaneseAnalyzer`` (P2Q items):
- ``has_actor``: noun + は/が by POS, excluding adverbial nouns (「受信したときは」).
- ``action_count``: counts predicate units (sahen noun + する-cluster, coordination
  boundaries て/で・連用形＋読点・clause-final, および-chained sahen predicates),
  so noun coordination 「AおよびBを送信」 is ONE action while
  「Aを保存し、Bを送信」/「保存および更新」 are two.
- ``passive_spans``: 助動詞レル/ラレル tokens only — potential 「できる」 (動詞)
  is never a passive candidate.

Known limitation (disclosed, not resolved — P2Q-5): the auxiliary れる/られる is
ambiguous between passive / potential / spontaneous / honorific; POS alone cannot
disambiguate. See ``analysis_limitations()``. Resolution would require dependency
analysis, which stays in the isolated GiNZA experiment track (never blocking).

Duplication note: the predicate-unit reconstruction intentionally mirrors
``prototype/rimay-jp/orchestrator/predicate_analysis.py`` (decision-log D-006
boundary rules) without importing it — Quality Core must not depend on the
orchestrator (improvement plan §11).
"""

from __future__ import annotations

import hashlib
import json
from functools import lru_cache
from pathlib import Path

from .base import Token
from .japanese import MODAL_PATTERNS

_NEG_SUFFIX_MODALS = ("してはならない",)  # MODAL_PATTERNSに含まれない禁止形


class QualityAnalyzerUnavailable(RuntimeError):
    """sudachipy未導入等で本Analyzerを構成できない（fail-closed。FR-039解釈の条件）。"""


@lru_cache(maxsize=1)
def _tokenizer():
    try:
        from sudachipy import Dictionary
    except ImportError as e:  # silent fallback禁止
        raise QualityAnalyzerUnavailable(
            "SudachiJapaneseAnalyzerにはpin済み依存（SudachiPy==0.6.11 / "
            f"SudachiDict-core==20260723）が必要です: {e}") from e
    return Dictionary(dict="core").create()


@lru_cache(maxsize=4)
def _file_hash(path: str) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return "sha256:" + h.hexdigest()


def analyzer_provenance() -> dict:
    """版・実体hashの記録（FR-039解釈の必須条件）。"""
    import importlib
    from importlib.metadata import version
    import sudachipy
    dic = Path(importlib.import_module("sudachidict_core").__file__).parent \
        / "resources" / "system.dic"
    res = Path(sudachipy.__file__).parent / "resources"
    manifest = [(n, _file_hash(str(res / n)))
                for n in ("sudachi.json", "char.def", "unk.def", "rewrite.def")
                if (res / n).exists()]
    return {
        "provider": "sudachipy",
        "provider_version": sudachipy.__version__,
        "dictionary_package": "sudachidict_core",
        "dictionary_version": version("sudachidict_core"),
        "dictionary_content_hash": _file_hash(str(dic)),
        "config_content_hash": "sha256:" + hashlib.sha256(
            json.dumps(manifest, sort_keys=True).encode("utf-8")).hexdigest(),
        "split_mode": "C",
    }


def analysis_limitations() -> tuple:
    """POSのみでは確定できない事項の開示（P2Q-5。§9.3「coverageで明示」）。"""
    return (
        "助動詞レル（れる/られる）の受身・可能・自発・尊敬はPOSのみでは判別"
        "できない。passive_spansは助動詞レルを受身候補として返し、意味は確定"
        "しない（可能動詞「できる」型のみ確実に除外する）。判別には依存解析が"
        "必要であり、隔離実験トラック（experiments/ginza-quality/）の対象。",
    )


# --- token walk helpers ------------------------------------------------------

def _toks(text: str):
    out, off = [], 0
    for t in _tokenizer().tokenize(text):
        s = t.surface()
        start = text.find(s, off) if text[off:off + len(s)] != s else off
        out.append((s, start, start + len(s), tuple(t.part_of_speech()),
                    t.dictionary_form()))
        off = start + len(s)
    return out


def _is_sahen_noun(pos) -> bool:
    return pos[0] == "名詞" and len(pos) > 2 and pos[2] == "サ変可能"


def _is_adverbial_noun(pos) -> bool:
    return pos[0] == "名詞" and len(pos) > 2 and pos[2] == "副詞可能"


def _strip_modal(text: str) -> str:
    """文末モダリティ表層の除去（非目的: モダリティ判定は表層規則のまま）。"""
    body = text.rstrip()
    if body.endswith("。"):
        body = body[:-1]
    for surface in sorted(MODAL_PATTERNS + _NEG_SUFFIX_MODALS, key=len,
                          reverse=True):
        if body.endswith(surface):
            return body[: -len(surface)]
    return body


def _predicate_units(toks) -> list:
    """並列境界限定の述語unit数え上げ（D-006と同一の境界規則）。"""
    units = []
    n = len(toks)

    def _accept(j, ended_with_te):
        if ended_with_te or j >= n:
            return True
        pos = toks[j][3]
        return pos[0] == "補助記号" and len(pos) > 1 and pos[1] == "読点"

    i = 0
    while i < n:
        s, start, end, pos, dic = toks[i]
        if _is_sahen_noun(pos) and i + 1 < n and toks[i + 1][3][0] == "動詞" \
                and toks[i + 1][4] == "する":
            j, te = i + 2, False
            while j < n:
                p = toks[j][3]
                if p[0] == "助動詞":
                    j += 1
                    continue
                if p[0] == "助詞" and len(p) > 1 and p[1] == "接続助詞" \
                        and toks[j][0] in ("て", "で"):
                    j += 1
                    te = True
                    break
                break
            if _accept(j, te):
                units.append(i)
            i = j
            continue
        if _is_sahen_noun(pos) and i == n - 1:  # モダリティ除去後の裸サ変名詞
            units.append(i)
            i += 1
            continue
        if pos[0] == "動詞" and len(pos) > 1 and pos[1] == "一般":
            j, te = i + 1, False
            while j < n and toks[j][3][0] == "助動詞":
                j += 1
            if j < n and toks[j][3][0] == "助詞" and len(toks[j][3]) > 1 \
                    and toks[j][3][1] == "接続助詞" and toks[j][0] in ("て", "で"):
                j += 1
                te = True
            if _accept(j, te):
                units.append(i)
            i = j
            continue
        i += 1

    # および/かつでサ変名詞が直結された述語並列（保存および更新[する]）。
    # 名詞並列（AおよびBを送信）はunit名詞の左が格助詞なので連鎖しない。
    extra = 0
    for ui in units:
        k = ui
        while k >= 2 and toks[k - 1][3][0] == "接続詞" \
                and toks[k - 1][0] in ("および", "かつ") \
                and _is_sahen_noun(toks[k - 2][3]):
            extra += 1
            k -= 2
    return [None] * (len(units) + extra)  # 呼び出し側は件数のみ使用


class SudachiJapaneseAnalyzer:
    """Analyzer Protocol実装（品詞限定改善。依存解析は使わない）。"""

    lang = "ja"
    CONDITION_MARKERS = ("とき", "場合", "際", "たら")
    SCOPE_MARKERS = ("ごとに", "すべての", "各")
    RESPONSE_SEPARATORS = ("、then", "；", "\n")

    def __init__(self):
        _tokenizer()  # fail-closed: 構築時に能力を確定する

    def tokenize(self, text: str) -> list:
        return [Token(s, a, b) for s, a, b, pos, _ in _toks(text)
                if pos[0] not in ("補助記号", "空白")]

    def has_modal(self, text: str) -> bool:
        return any(p in text for p in MODAL_PATTERNS)

    def has_actor(self, text: str) -> bool:
        """名詞（副詞可能を除く）＋係助詞は／格助詞が（P2Q-1）。"""
        toks = _toks(text)
        for i in range(len(toks) - 1):
            s, _a, _b, pos, _d = toks[i]
            ps, _pa, _pb, ppos, _pd = toks[i + 1]
            if ps in ("は", "が") and ppos[0] == "助詞" \
                    and pos[0] == "名詞" and not _is_adverbial_noun(pos):
                return True
        return False

    def has_finite_verb(self, text: str) -> bool:
        return any(pos[0] == "動詞" for _s, _a, _b, pos, _d in _toks(text)) \
            or self.has_modal(text)

    def action_count(self, text: str) -> int:
        """並列境界限定の述語unit数（P2Q-2/3。名詞並列は数えない）。"""
        body = _strip_modal(text)
        if not body.strip():
            return 1 if self.has_modal(text) else 0
        units = _predicate_units(_toks(body))
        if units:
            return len(units)
        return 1 if self.has_finite_verb(text) else 0

    def passive_spans(self, text: str) -> list:
        """助動詞レル/ラレルのspan（P2Q-4: できる[動詞]は候補にしない）。

        意味（受身/可能/自発/尊敬）は確定しない（analysis_limitations参照）。
        """
        return [(a, b, s) for s, a, b, pos, dic in _toks(text)
                if pos[0] == "助動詞" and dic in ("れる", "られる")]

    def verb_lemmas(self, text: str) -> list:
        return [(dic, a, b) for s, a, b, pos, dic in _toks(text)
                if pos[0] == "動詞"]

    def find_glossary_hits(self, text: str, glossary: set) -> list:
        """regex Analyzerと同一の表層一致（recall非回帰をGateで保証）。"""
        hits = []
        for term in sorted(glossary):
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
