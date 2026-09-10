"""Lexicon Overlay（改善計画 v0.3 D2: 表層候補生成→形態素境界検証→
位置ごとの最長一致＋否定接辞stop policy→Resolver）。

- 段階1（raw表層候補）は網羅列挙のみでresolvedにしない。
- 段階2（境界検証）はsplit mode B/C限定。phrase policyがAを使う場合も
  既知語の境界検証にはAを使わない。
- 段階3（選択）は左から位置ごとの最長一致。採用span内部から始まる短い候補は
  保持しない。否定接辞判定は**マッチspan外側の直前・直後に隣接する形態素だけ**
  を参照し、登録表層（無効／未確定等）のspan内部を理由に抑制しない。
- 3値契約（§10.2）: 候補outcomeは accepted / rejected。not_generatedは
  fixture側の概念であり、negative fixtureの対象表層が段階1で一度も生成されない
  場合、評価器はfixture設計不備としてP0をfailさせる。
"""
from __future__ import annotations

from dataclasses import dataclass, field

NEGATION_PREFIXES = ("未", "不", "非", "無")
NEGATION_SUFFIXES = ("不可", "不能", "以外")
BOUNDARY_SPLIT_MODES = ("B", "C")


@dataclass
class SurfaceCandidate:
    surface: str
    start: int
    end: int
    outcome: str = "generated"          # generated -> accepted | rejected
    selected: bool = False
    negation: dict | None = None        # {"side": "prefix"|"suffix", "morpheme": str}
    context: dict = field(default_factory=dict)


def vocabulary_surfaces(vocab) -> list:
    """Published Vocabularyの全表層（preferred＋synonyms）。長さ降順。

    deprecated/homonymも候補生成には含める（分類はResolverの責務であり、
    段階1で黙って落とすとdeprecated検出が失われる）。
    """
    seen = set()
    for t in vocab:
        for s in [t["preferred_japanese"], *(t.get("synonyms") or [])]:
            if s:
                seen.add(s)
    return sorted(seen, key=lambda s: (-len(s), s))


def raw_surface_candidates(text: str, vocab) -> list:
    """段階1: 原文上の全raw表層候補（重複位置も網羅。決定論順）。"""
    out = []
    for surface in vocabulary_surfaces(vocab):
        start = text.find(surface)
        while start != -1:
            out.append(SurfaceCandidate(surface, start, start + len(surface)))
            start = text.find(surface, start + 1)
    out.sort(key=lambda c: (c.start, -(c.end - c.start), c.surface))
    return out


def token_boundaries(tokens) -> set:
    b = set()
    for t in tokens:
        b.add(t.start)
        b.add(t.end)
    return b


def validate_boundaries(candidates: list, boundary_tokens) -> list:
    """段階2: 形態素境界整合検査（B/C mode tokenを渡すこと）。"""
    bounds = token_boundaries(boundary_tokens)
    for c in candidates:
        c.outcome = "accepted" if (c.start in bounds and c.end in bounds) \
            else "rejected"
    return candidates


def select_longest(candidates: list) -> list:
    """段階3a: 左から位置ごとの最長一致（accepted候補のみ対象）。"""
    cursor = -1
    selected = []
    for c in candidates:  # (start asc, length desc) 順
        if c.outcome != "accepted":
            continue
        if c.start > cursor:
            c.selected = True
            selected.append(c)
            cursor = c.end - 1
    return selected


def apply_negation_stop(selected: list, boundary_tokens) -> None:
    """段階3b: 否定接辞stop policy（マッチspan外側の隣接形態素のみ参照）。"""
    by_end = {t.end: t for t in boundary_tokens}
    by_start = {t.start: t for t in boundary_tokens}
    for c in selected:
        prev = by_end.get(c.start)
        nxt = by_start.get(c.end)
        if prev is not None and prev.surface in NEGATION_PREFIXES:
            c.negation = {"side": "prefix", "morpheme": prev.surface}
        elif nxt is not None and nxt.surface in NEGATION_SUFFIXES:
            c.negation = {"side": "suffix", "morpheme": nxt.surface}


def overlay(text: str, vocab, boundary_tokens, *,
            boundary_split_mode: str) -> dict:
    """D2三段階の実行。resolvedへの写像はしない（Resolverは呼び出し側）。

    戻り値:
      candidates: 全raw候補（outcome付き）
      selected:   最長一致採用候補（negation付き。stop対象を含む）
      resolvable: stop対象を除いた自動解決可能候補
      stopped:    否定接辞stop候補（§15: 棄却せず否定文脈付きで保持）
    """
    if boundary_split_mode not in BOUNDARY_SPLIT_MODES:
        raise ValueError(
            f"boundary validation split mode must be B or C: {boundary_split_mode}")
    candidates = raw_surface_candidates(text, vocab)
    validate_boundaries(candidates, boundary_tokens)
    selected = select_longest(candidates)
    apply_negation_stop(selected, boundary_tokens)
    return {
        "candidates": candidates,
        "selected": selected,
        "resolvable": [c for c in selected if c.negation is None],
        "stopped": [c for c in selected if c.negation is not None],
    }


def fixture_outcome(text: str, term: str, candidates: list) -> str:
    """negative fixture用の3値判定（§10.2）。

    not_generated: 段階1で対象表層の候補が1件も生成されていない
                   （fixture設計不備。評価器はP0をfailさせる）
    accepted:      いずれかの候補が境界検証を通過
    rejected:      候補は生成されたが全件棄却
    """
    hits = [c for c in candidates if c.surface == term]
    if not hits:
        return "not_generated"
    return "accepted" if any(c.outcome == "accepted" for c in hits) \
        else "rejected"
