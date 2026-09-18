"""文書Term Extractor（ADR-0014 P1。決定論・純粋検出）。

- 入力: AI可読の上流文書（brief・requirements source等）。LLM不使用。
- 出力はObservationのみ（D2: 書き込まない）。永続化は
  TerminologyStore.observe（channel="document"）の明示操作。
- 既登録語はresolved、同表記多義はambiguous、廃止語はdeprecatedへ分類し、
  **未知語だけ**がobservations（候補化対象）になる。

改善計画 v0.3（P1）による拡張:
- Provider注入点（§7.3）。既定は`regex`（従来と同一結果＋analysis_provenance
  のみadditive追加）。`sudachipy`は明示指定時のみ使用し、ロード不能なら
  fail-closed（silent fallback禁止）。
- sudachipy経路はLexicon Overlay（D2: 表層候補→B/C境界検証→位置ごと最長一致
  ＋否定接辞stop）→Resolver→残差候補句生成（D4）の順で処理する。
- 否定接辞でstopした既知語候補は自動resolvedにせず`negation_stopped`へ
  否定文脈付きで保持する（§15裁定までの既定）。
- `normalized_surface`は候補集約用の参考キーであり、Resolver解決には
  使用しない（D3／ADR-0014）。
"""
from __future__ import annotations

import re

from . import _ROOT  # noqa: F401
from rimay_jp_core.lexicon import terms  # noqa: E402
from .terminology import resolve_surface  # noqa: E402

_TOKEN = re.compile(r"[一-龥ァ-ヶーA-Za-z0-9]{2,}")
_HEADING = re.compile(r"^#{1,6}\s*(.+?)\s*$", re.MULTILINE)
_NUMERIC = re.compile(r"^[0-9,，.]+$")
_MAX_SPANS_PER_SURFACE = 3

PHRASE_POLICIES = ("token_only", "maximal_phrase", "lexicon_overlay_residual")

# 候補句を構成し得る品詞（注釈指針 corpus/lexical/annotation-guideline.md で凍結。
# 数詞は除外。中黒（・）は両隣がカタカナ語のときのみ連結を許す）
_CONTENT_POS0 = ("名詞", "接頭辞", "接尾辞")
_NAKAGURO = "・"


def _sections_of(text: str):
    sections = [(0, "(先頭)")]
    for m in _HEADING.finditer(text):
        sections.append((m.start(), m.group(1)))

    def _section(pos: int) -> str:
        name = sections[0][1]
        for start, title in sections:
            if start <= pos:
                name = title
            else:
                break
        return name

    return _section


def extract_document_terms(text: str, document_id: str, vocab=None, *,
                           provider: str = "regex",
                           phrase_policy: str = "lexicon_overlay_residual",
                           phrase_split_mode: str = "C",
                           boundary_split_mode: str = "C",
                           dictionary_edition: str = "core") -> dict:
    """文書から用語候補Observationを抽出する（決定論・無副作用）。

    provider="regex"（既定）は従来実装と同一の結果を返す
    （追加はanalysis_provenanceのみ。§7.1 additive契約）。
    """
    vocab = list(vocab) if vocab is not None else list(terms())
    if provider == "regex":
        return _extract_regex(text, document_id, vocab)
    if provider == "sudachipy":
        return _extract_sudachi(text, document_id, vocab,
                                phrase_policy=phrase_policy,
                                phrase_split_mode=phrase_split_mode,
                                boundary_split_mode=boundary_split_mode,
                                dictionary_edition=dictionary_edition)
    raise ValueError(f"unknown provider: {provider}")


# --- 従来経路（baseline。挙動は変更しない） ---------------------------------

def _extract_regex(text: str, document_id: str, vocab) -> dict:
    from .japanese_lexical_analysis import RegexProvider
    _section = _sections_of(text)

    counts: dict = {}
    spans: dict = {}
    for m in _TOKEN.finditer(text):
        s = m.group(0)
        if _NUMERIC.match(s):
            continue
        counts[s] = counts.get(s, 0) + 1
        if len(spans.setdefault(s, [])) < _MAX_SPANS_PER_SURFACE:
            spans[s].append((m.start(), m.end()))

    observations: list = []
    resolved: dict = {}
    ambiguous: list = []
    deprecated: list = []
    for surface in sorted(counts):
        r = resolve_surface(surface, vocab=vocab)
        first = spans[surface][0]
        entry = {"surface_form": surface, "count": counts[surface],
                 "section_id": _section(first[0]),
                 "matches": [x["term_id"] for x in r["matches"]]}
        if r["kind"] in ("exact", "synonym"):
            resolved[surface] = r["matches"][0]["term_id"]
        elif r["kind"] == "ambiguous":
            ambiguous.append(entry)
        elif r["kind"] == "deprecated":
            deprecated.append(entry)
        else:  # not_found → 候補化対象
            for start, end in spans[surface]:
                observations.append(
                    {"surface_form": surface,
                     "expected_types": [],
                     "source_span": {"start": start, "end": end},
                     "section_id": _section(start),
                     "document_id": document_id})
    return {"document_id": document_id, "observations": observations,
            "resolved": resolved, "ambiguous": ambiguous,
            "deprecated": deprecated, "counts": counts,
            "truncation": {"max_spans_per_surface": _MAX_SPANS_PER_SURFACE},
            "analysis_provenance": RegexProvider().metadata()}


# --- sudachipy経路（P1） -----------------------------------------------------

def _content_token(t) -> bool:
    pos = t.part_of_speech
    if pos[0] in _CONTENT_POS0:
        if len(pos) > 1 and pos[1] == "数詞":
            return False
        return not _NUMERIC.match(t.surface)
    # 連用形の名詞的用法（払い戻し・見積り等の動作名詞。注釈指針で凍結）:
    # 動詞-一般の連用形tokenは候補構成要素に含める。サ変述語の「し」は
    # 非自立可能なので含まれない（保存し、→ 保存＋し）。
    if pos[0] == "動詞" and len(pos) > 5 and pos[1] == "一般" \
            and pos[5].startswith("連用形"):
        return True
    return False


def _adverbial_noun(t) -> bool:
    """単独では候補化しない副詞可能名詞（とき・場合等。注釈指針で凍結）。"""
    pos = t.part_of_speech
    return len(pos) > 2 and pos[0] == "名詞" and pos[2] == "副詞可能"


def _is_katakana(s: str) -> bool:
    return bool(s) and all("ァ" <= ch <= "ヶ" or ch == "ー" for ch in s)


def _phrase_runs(tokens, blocked_spans) -> list:
    """連続content tokenの最大句（(start, end, [token]) のリスト）。

    blocked_spans（既知語採用span）に重なるtokenは句へ含めない
    （lexicon_overlay_residual用。maximal_phraseでは空集合を渡す）。
    中黒は両隣がカタカナcontent tokenのときのみ連結する。
    """
    def _blocked(t) -> bool:
        return any(s < t.end and t.start < e for s, e in blocked_spans)

    runs, cur = [], []
    for i, t in enumerate(tokens):
        if _content_token(t) and not _blocked(t):
            if cur and cur[-1].end != t.start:
                runs.append(cur)
                cur = []
            cur.append(t)
            continue
        if (t.surface == _NAKAGURO and cur and not _blocked(t)
                and i + 1 < len(tokens)
                and cur[-1].end == t.start
                and tokens[i + 1].start == t.end
                and _is_katakana(cur[-1].surface)
                and _is_katakana(tokens[i + 1].surface)
                and _content_token(tokens[i + 1])
                and not _blocked(tokens[i + 1])):
            cur.append(t)
            continue
        if cur:
            runs.append(cur)
            cur = []
    if cur:
        runs.append(cur)
    out = []
    for run in runs:
        while run and run[-1].surface == _NAKAGURO:
            run = run[:-1]
        if run:
            out.append((run[0].start, run[-1].end, run))
    return out


def _candidate_phrases(tokens, policy: str, known_spans) -> list:
    """D4のphrase policy。(start, end, [token]) のリストを返す。"""
    if policy == "token_only":
        return [(t.start, t.end, [t]) for t in tokens
                if _content_token(t) and not _adverbial_noun(t)
                and len(t.surface) >= 2]
    if policy == "maximal_phrase":
        return _phrase_runs(tokens, [])
    if policy == "lexicon_overlay_residual":
        return _phrase_runs(tokens, known_spans)
    raise ValueError(f"unknown phrase policy: {policy}")


def _extract_sudachi(text: str, document_id: str, vocab, *,
                     phrase_policy: str, phrase_split_mode: str,
                     boundary_split_mode: str, dictionary_edition: str) -> dict:
    from .japanese_lexical_analysis import get_provider
    from .lexicon_overlay import overlay

    if phrase_policy not in PHRASE_POLICIES:
        raise ValueError(f"unknown phrase policy: {phrase_policy}")
    sp = get_provider("sudachipy", dictionary=dictionary_edition,
                      split_mode=phrase_split_mode)
    _section = _sections_of(text)

    # D2: 表層候補生成 → B/C境界検証 → 最長一致＋否定接辞stop
    boundary_tokens = sp.analyze(text, mode=boundary_split_mode)
    ov = overlay(text, vocab, boundary_tokens,
                 boundary_split_mode=boundary_split_mode)

    # Resolver（既知語分類。stop候補は自動解決へ流さない）
    counts: dict = {}
    resolved: dict = {}
    ambiguous: list = []
    deprecated: list = []
    known_spans: list = []
    for c in ov["resolvable"]:
        counts[c.surface] = counts.get(c.surface, 0) + 1
        known_spans.append((c.start, c.end))
    for surface in sorted({c.surface for c in ov["resolvable"]}):
        r = resolve_surface(surface, vocab=vocab)
        first = min(c.start for c in ov["resolvable"] if c.surface == surface)
        entry = {"surface_form": surface, "count": counts[surface],
                 "section_id": _section(first),
                 "matches": [x["term_id"] for x in r["matches"]]}
        if r["kind"] in ("exact", "synonym"):
            resolved[surface] = r["matches"][0]["term_id"]
        elif r["kind"] == "ambiguous":
            ambiguous.append(entry)
        elif r["kind"] == "deprecated":
            deprecated.append(entry)
        # not_found（登録表層なのに未解決）は起こらない想定だが、
        # 起きた場合は下の残差候補生成に委ねる（黙って落とさない）

    negation_stopped = [
        {"surface_form": c.surface,
         "source_span": {"start": c.start, "end": c.end},
         "section_id": _section(c.start),
         "matches": [x["term_id"] for x in
                     resolve_surface(c.surface, vocab=vocab)["matches"]],
         "negation": c.negation}
        for c in ov["stopped"]]

    # D4: 残差候補句の生成
    phrase_tokens = sp.analyze(text, mode=phrase_split_mode)
    phrases = _candidate_phrases(phrase_tokens, phrase_policy, known_spans)

    phrase_spans: dict = {}
    normalized: dict = {}
    for start, end, toks in phrases:
        surface = text[start:end]
        if len(surface) < 2 or _NUMERIC.match(surface):
            continue
        if len(toks) == 1 and _adverbial_noun(toks[0]):
            continue  # 単独の副詞可能名詞（とき・場合等）は候補にしない
        if surface in resolved or any(
                surface == e["surface_form"] for e in ambiguous + deprecated):
            continue
        counts[surface] = counts.get(surface, 0) + 1
        if len(phrase_spans.setdefault(surface, [])) < _MAX_SPANS_PER_SURFACE:
            phrase_spans[surface].append((start, end))
        normalized.setdefault(
            surface, "".join(t.normalized_form for t in toks
                             if t.surface != _NAKAGURO))

    observations: list = []
    for surface in sorted(phrase_spans):
        r = resolve_surface(surface, vocab=vocab)
        if r["kind"] != "not_found":
            continue  # 既知はoverlay段で処理済み（重複させない）
        for start, end in phrase_spans[surface]:
            obs = {"surface_form": surface,
                   "expected_types": [],
                   "source_span": {"start": start, "end": end},
                   "section_id": _section(start),
                   "document_id": document_id,
                   "normalized_surface": normalized[surface]}
            # 既知語spanに隣接する残差は複合span文脈を保持（D2比較評価用）
            for ks, ke in known_spans:
                if ke == start:
                    obs["context_span"] = {"start": ks, "end": end}
                    break
                if end == ks:
                    obs["context_span"] = {"start": start, "end": ke}
                    break
            observations.append(obs)

    meta = sp.metadata()
    meta.update({"phrase_split_mode": phrase_split_mode,
                 "boundary_validation_split_mode": boundary_split_mode,
                 "phrase_policy": phrase_policy})
    return {"document_id": document_id, "observations": observations,
            "resolved": resolved, "ambiguous": ambiguous,
            "deprecated": deprecated, "counts": counts,
            "negation_stopped": negation_stopped,
            "truncation": {"max_spans_per_surface": _MAX_SPANS_PER_SURFACE},
            "analysis_provenance": meta}
