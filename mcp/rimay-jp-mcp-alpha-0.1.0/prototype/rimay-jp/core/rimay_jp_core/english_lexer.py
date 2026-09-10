"""English Rimay full-consumption lexer（改善計画C1・§21.1）。

全入力文字を検査し、token間および末尾の非空白ギャップを ``LEXICAL_GAP`` で
即時拒否する（fail-open防止）。本文法にコメント構文はないため許可コメントは
存在しない。Parser成功の不変条件は ``parse_meta.consumed.end == len(input)``
（空白は区切りとして消費済みとみなす）。

ParseErrorの構造化契約（§19.6）もここで定義する。診断は
``code / offset / line / column / expected / found`` を持ち、``str(e)`` は
後方互換の可読メッセージを維持する（既存の ``error: str`` 経路を壊さない）。
"""
from __future__ import annotations

import re
from dataclasses import dataclass

# §19.6 ParseError code enum（DUPLICATE_ROLE等はC3のRole保存契約で使用する）
PARSE_ERROR_CODES = frozenset({
    "LEXICAL_GAP", "UNEXPECTED_TOKEN", "MISSING_TOKEN",
    "UNKNOWN_ACTION", "AMBIGUOUS_ACTION", "PROFILE_OUT", "TRAILING_TOKEN",
    "UNSUPPORTED_OPERATOR", "DUPLICATE_ROLE", "UNMAPPED_ROLE",
})


class ParseError(Exception):
    """構造化Parse診断（§19.6）。

    後方互換: ``str(e)`` は従来どおり人間可読メッセージを返す。構造化情報は
    属性および ``diagnostic()``（MCPのadditive ``diagnostic`` フィールド用）で
    提供する。
    """

    def __init__(self, message: str, *, code: str = "UNEXPECTED_TOKEN",
                 offset: int = 0, text: str = "",
                 expected: tuple[str, ...] | list[str] = (),
                 found: str = "") -> None:
        super().__init__(message)
        assert code in PARSE_ERROR_CODES, f"unknown ParseError code: {code}"
        self.code = code
        self.offset = offset                       # zero-based character offset
        self.expected = tuple(sorted(expected))    # sorted string list（§19.6）
        self.found = found                         # original surface
        # line: one-based / column: one-based（§19.6）
        self.line = text.count("\n", 0, offset) + 1
        self.column = offset - (text.rfind("\n", 0, offset) + 1) + 1

    def diagnostic(self) -> dict:
        """MCP additive diagnostic（§19.6。domainでSerializer診断と区別）。"""
        return {
            "domain": "parse",
            "code": self.code,
            "offset": self.offset,
            "line": self.line,
            "column": self.column,
            "expected": list(self.expected),
            "found": self.found,
        }


@dataclass(frozen=True)
class Token:
    """字句トークン。offsetは原文の文字位置（startは先頭、endは排他的末尾）。

    kind: "Q"（引用符付き。valueは内側テキスト、spanは引用符を含む）
          / "W"（語） / "N"（整数bullet） / "P"（区切り）
    """
    kind: str
    value: str
    start: int
    end: int


# 既存tokenにCanonical 0.8 Response Blockの整数・区切りを加えた集合。
_TOKEN = re.compile(
    r'"([^"]*)"|([A-Za-z][A-Za-z0-9_]*)|([0-9]+)|(,|\.|\(|\)|:|;|\[|\]|=|-)')


def _reject_gap(text: str, start: int, end: int) -> None:
    """token間・末尾ギャップにUnicode空白以外があれば即時拒否（§21.1手順2--4）。"""
    for i in range(start, end):
        ch = text[i]
        if not ch.isspace():
            raise ParseError(
                f"lexical gap at offset {i}: {ch!r} is not part of any token",
                code="LEXICAL_GAP", offset=i, text=text,
                expected=("token boundary or whitespace",), found=ch)


def tokenize(text: str) -> list[Token]:
    """全消費tokenize。非空白の未消費文字が1文字でもあればLEXICAL_GAP。

    未閉じ引用符・Unicode smart quote・バックスラッシュ・``#`` ``@`` 等は
    tokenにならずギャップに残るため、ここで必ず拒否される。block専用tokenの
    文脈外使用はParserが``LEXICAL_GAP``として拒否する。
    """
    toks: list[Token] = []
    pos = 0
    for m in _TOKEN.finditer(text):
        _reject_gap(text, pos, m.start())
        if m.group(1) is not None:
            toks.append(Token("Q", m.group(1), m.start(), m.end()))
        elif m.group(2) is not None:
            toks.append(Token("W", m.group(2), m.start(), m.end()))
        elif m.group(3) is not None:
            toks.append(Token("N", m.group(3), m.start(), m.end()))
        else:
            toks.append(Token("P", m.group(4), m.start(), m.end()))
        pos = m.end()
    _reject_gap(text, pos, len(text))
    return toks
