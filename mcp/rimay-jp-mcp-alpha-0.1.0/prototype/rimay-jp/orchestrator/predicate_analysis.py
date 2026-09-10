"""述語句の再構成（改善計画 v0.3 D5／P2。決定論・純粋）。

- サ変可能名詞＋辞書形`する`のサ変動詞を連結し、`送信する`等の述語句を
  再構成する（送信する／した／します／しない／して → 送信する）。
- モダリティ表層（〜しなければならない等）は呼び出し側が**事前に**
  surface一致で除去していること（非目的: モダリティ判定を形態素解析へ
  移さない）。除去の結果、body末尾に残った裸のサ変名詞も述語とみなす。
- 並列位置の述語は**明示的な並列境界に限定して**採用する（Gate Cレビュー裁定）:
  接続助詞`て／で`で終わるクラスタ、連用形＋読点（保存し、）、および末尾述語。
  境界を持たない非末尾の動詞句（`保存した注文データ`の連体修飾等）は
  述語として採用しない。
- 否定は述語クラスタ内の助動詞`ない`で検出し、意味確定はしない
  （negatedフラグとして返すのみ）。
"""
from __future__ import annotations


def _is_sahen_noun(t) -> bool:
    pos = t.part_of_speech
    return pos[0] == "名詞" and len(pos) > 2 and pos[2] == "サ変可能"


def _is_touten(t) -> bool:
    pos = t.part_of_speech
    return pos[0] == "補助記号" and len(pos) > 1 and pos[1] == "読点"


def _is_te(t) -> bool:
    pos = t.part_of_speech
    return pos[0] == "助詞" and len(pos) > 1 and pos[1] == "接続助詞" \
        and t.surface in ("て", "で")


def reconstruct_predicates(tokens) -> list:
    """token列 → 述語unit列。

    unit: {"surface", "predicate"（辞書形句）, "start", "end", "negated"}
    offsetは解析対象文字列基準。
    採用条件（並列境界。Gate Cレビュー裁定）:
      末尾クラスタ／接続助詞て・でで終端／直後が読点。
      それ以外の非末尾クラスタ（連体修飾等）は採用しない。
    """
    units: list = []
    n = len(tokens)

    def _accept(j: int, ended_with_te: bool) -> bool:
        if ended_with_te:
            return True
        if j >= n:
            return True  # 末尾述語
        return _is_touten(tokens[j])  # 連用形＋読点

    i = 0
    while i < n:
        t = tokens[i]
        pos = t.part_of_speech

        # サ変可能名詞 ＋ 動詞（辞書形する）
        if _is_sahen_noun(t) and i + 1 < n \
                and tokens[i + 1].part_of_speech[0] == "動詞" \
                and tokens[i + 1].dictionary_form == "する":
            j = i + 2
            negated = False
            ended_with_te = False
            while j < n:
                p = tokens[j].part_of_speech
                if p[0] == "助動詞":
                    if tokens[j].dictionary_form == "ない":
                        negated = True
                    j += 1
                    continue
                if _is_te(tokens[j]):
                    j += 1  # て＝並列境界（クラスタに含めて終了）
                    ended_with_te = True
                    break
                break
            if _accept(j, ended_with_te):
                units.append({"surface": t.surface,
                              "predicate": t.surface + "する",
                              "start": t.start, "end": tokens[j - 1].end,
                              "negated": negated})
            i = j
            continue

        # body末尾の裸サ変名詞（モダリティ表層の事前除去で「する」が
        # 消えた形。〜を送信［しなければならない］→ …を送信）
        if _is_sahen_noun(t) and i == n - 1:
            units.append({"surface": t.surface,
                          "predicate": t.surface + "する",
                          "start": t.start, "end": t.end,
                          "negated": False})
            i += 1
            continue

        # 一般動詞（扱う・送る等）
        if pos[0] == "動詞" and len(pos) > 1 and pos[1] == "一般":
            j = i + 1
            negated = False
            ended_with_te = False
            while j < n and tokens[j].part_of_speech[0] == "助動詞":
                if tokens[j].dictionary_form == "ない":
                    negated = True
                j += 1
            if j < n and _is_te(tokens[j]):
                j += 1
                ended_with_te = True
            if _accept(j, ended_with_te):
                units.append({"surface": t.surface,
                              "predicate": t.dictionary_form,
                              "start": t.start, "end": tokens[j - 1].end,
                              "negated": negated})
            i = j
            continue

        i += 1
    return units
