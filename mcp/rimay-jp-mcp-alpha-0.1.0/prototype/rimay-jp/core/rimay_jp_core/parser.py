"""English Rimay MVPサブセットの再実装Parser（再帰下降）。

一次ソースはCC BY 4.0論文（Veizaga et al., EMSE 2021, Version of Record）に
記載の文法構造。SNTSVV/Rimayリポジトリのコードは複製していない
（Phase 0ライセンス裁定・D7クリーンルーム規律）。

C1（§19.5/§19.6/§21.1/§21.2）: full-consumption lexer、構造化ParseError、
応答Actor冠詞、AST契約（conditions配列・action object・parse_meta）。
D-01是正（RC-014）: keyword・助動詞・冠詞・動詞・前置詞は公式Grammarに明示された
表層のみを受理する（大小文字区別）。条件keywordはGrammarが明示する
'When'|'when' 等の2表層、Scopeは 'For' のみ。無条件文の先頭articleに限り
文頭大文字 'The'|'A'|'An' を追加受理する（論文S-1 Listing 1の ARTICLE? に基づく
Gate B凍結正例（RCONF-STRUCT-006等）を維持。公式GrammarのWithoutConditionは
('The')? のみのため、A/Anはrepository-spec差分D-16として記録=D1論文正本優先）。
大小文字の正規化は**受理判定後の内部処理に限定**する。
C3（§21.3/§21.6--§21.8・CG-01〜09）:
  - English conformance profile（profile/english-rimay-conformance.yaml）駆動の
    Action選択とrimay_action_id/emse_rule_id束縛
  - Role保存契約: rolesはRole名キーの {value, preposition, span}。
    写像外前置詞=UNMAPPED_ROLE、単値Role重複=DUPLICATE_ROLE、必須Role欠落=MISSING_TOKEN
  - 否定比較のNOT_EQUALS正規化（CG-01。IS_NOTを生成しない）
  - 既知Profile外のoperator（less than/contains等）・動詞（detect/ignore）=PROFILE_OUT
  - KEEP_15_2リテラル（value/values/property/properties）と
    retention句（for a period of "P" starting from "D"。期間+開始点一体のみ、§21.6）

対象（Phase 2スライス + C3拡張）:
  requirement := [scope] [(condition | condition_expression) ','] ['then']
                 (response | response_expression | response_block) '.'
  condition_expression := condition
                        | '(' condition_expression ('and'|'or') condition_expression ')'
  response_expression := response
                       | '(' response_expression ')'
                       | '(' response_expression ('and'|'or') response_expression ')'
  scope       := 'For' QUOTED ','                     # 'For'のみ（'for'は拒否。D-01）
  condition   := ('When'|'when'|'After'|'after'|'Before'|'before') trigger
               | ('If'|'if'|'While'|'while') predicate
  trigger     := IDENT verb3 np role_phrase*
  predicate   := np ('is'|'are') ['not'] (cmp | QUOTED | IDENT)
  cmp         := 'greater' 'or' 'equal' 'to' QUOTED
  response    := [article] IDENT ('must'|'shall') ['not'] verb object roles* [retention]
                 # article: 'the'|'a'|'an'。無条件文の先頭に限り 'The'|'A'|'An' も受理
                 # （D-01・D-16。条件節後は小文字のみ=ArticleInLowercase）
  object      := ['the'|'a'|'an'] [literal] (QUOTED | IDENT)      # literalはSTOREのみ
  np          := ['the'|'a'|'an'] (QUOTED | IDENT)

emse_rule_id はASTの検査用派生値であり、Canonicalへはコピーしない（§19.5）。
"""
import re

from .english_lexer import ParseError, Token, tokenize
from .english_profile import (
    binding, grammar_profile_hash, operator_surfaces,
    profile_out_verb_index, trigger_verb_index, value_connectors, verb_index,
)

__all__ = ["parse", "verb_family", "ParseError", "PARSER_VERSION"]

# 0.3.0: profile駆動Action選択・Role名キーroles・NOT_EQUALS正規化（AST契約変更、§11）
# 0.4.0: D-01是正（RC-014）— 受理表層をGrammar明示表層に限定（大小文字区別。受理契約変更）
# 0.5.0: Canonical 0.6.0 Response expressionの完全括弧化and/or境界（RC-029）
# 0.6.0: Canonical 0.7.0 Condition expressionの完全括弧化and/or境界
PARSER_VERSION = "0.11.0"  # 0.11.0: typed Operator value expression runtime activation

_ARTICLES = ("the", "a", "an")
# 無条件文頭に限り受理する文頭大文字冠詞（paper S-1 Listing 1・repo差分D-16）
_SENTENCE_INITIAL_ARTICLES = ("The", "A", "An")
_CONDITION_WORDS = (
    "When", "when", "If", "if", "While", "while",
    "After", "after", "Before", "before", "Where", "where",
    "Every", "every",
)

_RESERVED_CACHE: frozenset | None = None


def _reserved() -> frozenset:
    """Grammar keyword＋profile表層の予約語集合（RC-014追補・D-17。二層構成）。

    公式Xtextではkeyword tokenはID terminalになれない（^escapeなしでは識別子に
    使えない）ため、これらの表層を識別子slot（応答actor・トリガーactor・名詞句の
    非引用値・object位置）で受理しない。引用符付き値（Q）は制限しない。

    構造層は固定資産 `profile/official-grammar-keywords.yaml`（検証済みGrammar
    hashに紐づく。契約テスト=test_keyword_inventory.py）から読み、動詞・前置詞・
    演算子語はprofileから実行時導出して合成する。**A/Anはkeywordではない**ため
    含めない（D-16の文頭限定表層は `_SENTENCE_INITIAL_ARTICLES` が別扱いする）。
    """
    global _RESERVED_CACHE
    if _RESERVED_CACHE is None:
        import yaml as _yaml
        from pathlib import Path as _Path
        inv_path = _Path(__file__).resolve().parents[2] / "profile" / "official-grammar-keywords.yaml"
        inv = _yaml.safe_load(inv_path.read_text(encoding="utf-8"))
        # F-4完全化（RC-015）: 固定Grammar抽出の完全keyword inventory
        # （引用268 ∪ enum14 = 277語）そのものを予約集合とする。第二読者提供の
        # 固定Grammar直接読解で確定し、契約テストがGrammar hash・268 oracle・
        # 277集合一致を機械検査する。A/Anは非keyword（大文字）のため含まれない。
        base = set(inv["complete_keyword_inventory"])
        assert "A" not in base and "An" not in base   # D-16文頭限定表層は予約しない
        _RESERVED_CACHE = frozenset(base)
    return _RESERVED_CACHE
# 前置詞候補（写像可否はfamily bindingで判定。写像外はUNMAPPED_ROLE）
_PREPOSITIONS = ("to", "from", "through", "on", "of", "using", "in")


class _P:
    def __init__(self, text: str):
        self.text = text
        self.toks: list[Token] = tokenize(text)   # LEXICAL_GAPはここで即時送出
        block_prefix = ("do", "the", "following", "actions")
        has_block_prefix = any(
            tuple(token.value for token in self.toks[index:index + 4]) == block_prefix
            for index in range(max(0, len(self.toks) - 3))
        )
        if not has_block_prefix:
            for token in self.toks:
                if token.kind == "N" or (
                        token.kind == "P" and token.value in ":;[]="):
                    raise ParseError(
                        f"lexical gap at offset {token.start}: "
                        f"{token.value!r} is not part of the selected surface",
                        code="LEXICAL_GAP", offset=token.start, text=text,
                        expected=("token boundary or whitespace",),
                        found=token.value[0])
        self.i = 0

    def peek(self, ahead: int = 0) -> Token:
        j = self.i + ahead
        if j < len(self.toks):
            return self.toks[j]
        return Token("EOF", "", len(self.text), len(self.text))

    def next(self) -> Token:
        t = self.peek()
        self.i += 1
        return t

    def _fail(self, code: str, expected: tuple, tok: Token) -> None:
        if tok.kind == "EOF" and code == "UNEXPECTED_TOKEN":
            code = "MISSING_TOKEN"
        shown = tok.value if tok.kind != "EOF" else "<end of input>"
        raise ParseError(
            f"expected {', '.join(expected)}, got {shown!r}",
            code=code, offset=tok.start, text=self.text,
            expected=tuple(str(e) for e in expected), found=tok.value)

    def expect_word(self, *words: str, label: str | None = None) -> str:
        tok = self.next()
        if tok.kind != "W" or (words and tok.value not in words):
            self._fail("UNEXPECTED_TOKEN", tuple(words) or (label or "identifier",), tok)
        return tok.value

    def expect_punct(self, p: str) -> None:
        tok = self.next()
        if tok.kind != "P" or tok.value != p:
            self._fail("UNEXPECTED_TOKEN", (p,), tok)

    def expect_number(self) -> str:
        tok = self.next()
        if tok.kind != "N":
            self._fail("UNEXPECTED_TOKEN", ("integer bullet",), tok)
        return tok.value

    def accept_word(self, *words: str) -> str | None:
        tok = self.peek()
        if tok.kind == "W" and tok.value in words:
            self.i += 1
            return tok.value
        return None

    def accept_punct(self, *punctuation: str) -> str | None:
        tok = self.peek()
        if tok.kind == "P" and tok.value in punctuation:
            self.i += 1
            return tok.value
        return None

    def np(self) -> str:
        self.accept_word(*_ARTICLES)
        tok = self.next()
        if tok.kind == "Q":
            return tok.value
        if tok.kind == "W":
            if tok.value in _reserved():   # keyword-as-ID拒否（RC-014追補・D-17）
                self._fail("UNEXPECTED_TOKEN", ("entity",), tok)
            return tok.value
        self._fail("UNEXPECTED_TOKEN", ("entity",), tok)

    def np_with_span(self) -> tuple:
        self.accept_word(*_ARTICLES)
        tok = self.next()
        if tok.kind == "Q":
            return tok.value, {"start": tok.start, "end": tok.end}
        if tok.kind == "W":
            if tok.value in _reserved():   # keyword-as-ID拒否（RC-014追補・D-17）
                self._fail("UNEXPECTED_TOKEN", ("entity",), tok)
            return tok.value, {"start": tok.start, "end": tok.end}
        self._fail("UNEXPECTED_TOKEN", ("entity",), tok)


def _parse_typed_operand(p: _P) -> dict | None:
    """Parse one exact 0.5 profile operand surface without name inference."""
    first = p.peek()
    if first.kind != "W":
        return None
    if first.value in {"actor", "class", "property"} and p.peek(1).kind == "Q":
        kind = p.next().value
        name = p.next().value
        return {"wrapper": "declared_reference", "kind": kind, "name": name}
    if (first.value, p.peek(1).value, p.peek(2).value,
            p.peek(3).value) == ("instance", "-", "or", "-") and \
            p.peek(4).value == "property":
        p.next()
        p.expect_punct("-")
        p.expect_word("or")
        p.expect_punct("-")
        p.expect_word("property")
        name = p.next()
        if name.kind != "Q":
            p._fail("UNEXPECTED_TOKEN", ("quoted operand name",), name)
        operand = {"wrapper": "instance_or_property",
                   "kind": "instance_or_property", "name": name.value}
        if p.accept_word("of"):
            kind = p.expect_word("class", "label")
            value = p.next()
            if value.kind != "Q":
                p._fail("UNEXPECTED_TOKEN", ("quoted type name",), value)
            operand["defined_in_type"] = {"kind": kind, "name": value.value}
        if p.accept_word("labelled"):
            value = p.next()
            if value.kind != "Q":
                p._fail("UNEXPECTED_TOKEN", ("quoted label",), value)
            operand["label"] = value.value
        return operand
    if (first.value, p.peek(1).value, p.peek(2).value) == ("UI", "-", "component"):
        p.next()
        p.expect_punct("-")
        p.expect_word("component")
        name = p.next()
        if name.kind != "Q":
            p._fail("UNEXPECTED_TOKEN", ("quoted UI component name",), name)
        p.expect_word("of")
        p.expect_word("type")
        component_type = p.next()
        if component_type.kind != "Q":
            p._fail("UNEXPECTED_TOKEN", ("quoted UI component type",), component_type)
        return {"wrapper": "ui_component_instance", "kind": "ui_component_instance",
                "name": name.value, "component_type": component_type.value}
    return None


def _parse_predicate(p: _P, kw: str, kw_tok: Token) -> dict:
    """If/While述語。scalarと完全括弧value treeを相互排他で解析する。"""
    operand = _parse_typed_operand(p)
    subj = None if operand is not None else p.np()
    start = p.peek()
    candidates = sorted(
        ((tuple(surface.split()), operator)
         for operator, surface in operator_surfaces().items()),
        key=lambda item: (-len(item[0]), item[0]),
    )
    op = None
    for words, operator in candidates:
        actual = tuple(
            p.peek(index).value if p.peek(index).kind == "W" else None
            for index in range(len(words))
        )
        if actual == words:
            for word in words:
                p.expect_word(word)
            op = operator
            break
    if op is None:
        raise ParseError(
            "comparison operator is not one of the adopted canonical surfaces",
            code="UNSUPPORTED_OPERATOR", offset=start.start, text=p.text,
            expected=tuple(sorted(operator_surfaces().values())), found=start.value)
    if operand is not None:
        try:
            value_expression = _parse_value_expression(p)
        except ParseError as exc:
            raise ParseError(
                "typed operand requires a canonical value expression",
                code="UNSUPPORTED_OPERATOR", offset=p.peek().start, text=p.text,
                expected=("quoted value", "fully parenthesized value expression"),
                found=p.peek().value,
            ) from exc
        val = None
    elif p.peek().kind == "P" and p.peek().value == "(":
        value_expression = _parse_value_expression(p)
        val = None
    else:
        try:
            val = p.np()
        except ParseError as exc:
            raise ParseError(
                "comparison operator alias or predicate value is not canonical",
                code="UNSUPPORTED_OPERATOR", offset=p.peek().start, text=p.text,
                expected=("single predicate value", "fully parenthesized value expression"),
                found=p.peek().value,
            ) from exc
    following = p.peek()
    if following.kind == "W" and following.value in {
        "equal", "greater", "less", "not", "or", "than", "to",
    }:
        raise ParseError(
            "comparison predicate has trailing text or a non-canonical alias",
            code="UNSUPPORTED_OPERATOR", offset=following.start, text=p.text,
            expected=("condition delimiter",), found=following.value)
    result = {"kind": kw, "op": op}
    if operand is not None:
        result["operand"] = operand
    else:
        result["subject"] = subj
    if val is None:
        result["value_expression"] = value_expression
    else:
        result["value"] = val
    return result


def _parse_value_expression(p: _P) -> dict:
    """Parse an inner value tree without consuming outer Condition connectors.

    Product value connectors are deliberately uppercase. Outer Condition
    connectors remain lowercase, so the two authorities cannot silently bleed
    into one another even when both trees are nested.
    """
    opening = p.peek()
    if opening.kind == "Q":
        p.next()
        return {"kind": "value", "value": opening.value}
    if not p.accept_punct("("):
        p._fail("UNEXPECTED_TOKEN", ("quoted value", "("), opening)
    left = _parse_value_expression(p)
    if p.accept_punct(")"):
        return {"kind": "group", "expression": left}
    connector_token = p.peek()
    connectors = value_connectors()
    connector = p.accept_word(*connectors.values())
    if connector is None:
        p._fail("UNEXPECTED_TOKEN", ("AND", "OR", ")"), connector_token)
    right = _parse_value_expression(p)
    p.expect_punct(")")
    kind = next(key for key, surface in connectors.items() if surface == connector)
    return {"kind": kind, "left": left, "right": right}


def _parse_trigger(p: _P, kw: str) -> dict:
    """When/After/Beforeトリガー。eventはactor/action/object/valueのみ保持
    （ast-canonical-mapping準拠。'to'はUPDATE系更新後値のみcanonicalizeが採用）。"""
    tv_index = trigger_verb_index()
    at = p.next()
    if at.kind != "W" or at.value in _reserved():   # keyword-as-ID拒否（D-17）
        p._fail("UNEXPECTED_TOKEN", ("trigger actor",), at)
    actor = at.value
    vt = p.next()
    if vt.kind != "W" or vt.value not in tv_index:
        p._fail("UNKNOWN_ACTION", ("trigger verb",), vt)
    obj = p.np()
    ev = {"kind": kw, "actor": actor, "verb": vt.value, "object": obj}
    while True:
        if p.accept_word("to"):
            ev["to_value"] = p.np()
        elif p.accept_word("from", "through", "on", "of", "using", "in"):
            p.np()
        else:
            break
    return ev


def _parse_condition(p: _P) -> dict:
    """Parse one condition leaf without consuming the outer comma."""
    kw_tok = p.peek()
    kw = p.accept_word(*_CONDITION_WORDS)
    if kw is None:
        p._fail("UNEXPECTED_TOKEN", _CONDITION_WORDS, kw_tok)
    kw = kw.lower()
    if kw in ("when", "after", "before"):
        return _parse_trigger(p, kw)
    if kw in ("if", "while"):
        return _parse_predicate(p, kw, kw_tok)
    raise ParseError(
        f"condition keyword {kw!r} is outside the supported profile",
        code="PROFILE_OUT", offset=kw_tok.start, text=p.text,
        expected=("if", "when", "while", "after", "before"), found=kw)


def _parse_condition_expression(p: _P) -> dict:
    """Parse a fully-parenthesized binary condition tree."""
    if not p.accept_punct("("):
        return {"kind": "condition", "condition": _parse_condition(p)}
    left = _parse_condition_expression(p)
    connector_tok = p.peek()
    connector = p.accept_word("and", "or")
    if connector is None:
        p._fail("UNEXPECTED_TOKEN", ("and", "or"), connector_tok)
    right = _parse_condition_expression(p)
    p.expect_punct(")")
    return {"kind": connector, "left": left, "right": right}


def _starts_condition_expression(p: _P) -> bool:
    """Distinguish a parenthesized condition prefix from a response expression."""
    offset = 0
    while p.peek(offset).kind == "P" and p.peek(offset).value == "(":
        offset += 1
    token = p.peek(offset)
    return offset > 0 and token.kind == "W" and token.value in _CONDITION_WORDS


def _parse_response(p: _P, sentence_initial: bool = False) -> dict:
    """応答節（§21.2冠詞・§21.3 Action選択・§21.8 Role保存契約）。

    sentence_initial: 無条件文の先頭に限り文頭大文字冠詞 'The'|'A'|'An' を
    追加受理する（D-01・D-16。条件節後はArticleInLowercase=小文字のみ）。
    """
    v_index = verb_index()
    out_verbs = profile_out_verb_index()

    # Actor（冠詞は1回だけ受理し、AST値に含めない。位置別表層=D-01/D-16）
    articles = _ARTICLES + _SENTENCE_INITIAL_ARTICLES if sentence_initial else _ARTICLES
    art = p.accept_word(*articles)
    at = p.next()
    if (art in ("A", "An") and (at.kind != "W" or at.value in _reserved())):
        # 'A must …' 等: A/Anはkeywordではないため、後続がactorになれない場合は
        # 冠詞ではなくactor識別子として扱う（official構文と一致。RC-014追補2）
        p.i -= 1
        at = Token("W", art, at.start - len(art) - 1, at.start - 1)
    if at.kind != "W":
        p._fail("UNEXPECTED_TOKEN", ("actor identifier",), at)
    if at.value in _reserved():   # 冠詞・modal・keyword全般をactor IDとして拒否（D-17）
        p._fail("UNEXPECTED_TOKEN", ("actor identifier",), at)
    actor = at.value

    p.expect_word("must", "shall")
    neg = bool(p.accept_word("not"))

    # Action選択（§21.3）: profile索引で候補化。既知Profile外はPROFILE_OUT
    vt = p.next()
    verb = vt.value if vt.kind == "W" else ""
    if vt.kind != "W":
        p._fail("UNKNOWN_ACTION", ("response verb",), vt)
    if verb in out_verbs:
        raise ParseError(
            f"verb {verb!r} ({out_verbs[verb]}) is outside the supported profile",
            code="PROFILE_OUT", offset=vt.start, text=p.text,
            expected=tuple(sorted({v for v in v_index if not v.endswith('s')})[:5]),
            found=vt.value)
    if verb not in v_index:
        p._fail("UNKNOWN_ACTION", ("response verb",), vt)
    fam = v_index[verb]
    b = binding(fam)

    resp: dict = {
        "actor": actor,
        "modality": "MUST_NOT" if neg else "MUST",
        "verb": verb,
        "action": {
            "family": fam,
            "verb": verb,
            "rimay_action_id": b["rimay_action_id"],
            "emse_rule_id": b.get("emse_rule_id"),
            "span": {"start": vt.start, "end": vt.end},
        },
        "roles": {},
    }

    # object（無前置詞名詞句 → object_role）。STOREのみKEEP_15_2リテラルを受理
    p.accept_word(*_ARTICLES)
    literal = None
    lt = p.peek()
    if (b.get("object_literals") and lt.kind == "W"
            and lt.value in b["object_literals"] and p.peek(1).kind == "Q"):
        literal = p.next().value
    ot = p.next()
    obj_role = b["object_role"]
    if ot.kind not in ("Q", "W") or (ot.kind == "W" and ot.value in _reserved()):
        # object名詞句の欠落（keyword-as-ID含む）は必須Role欠落（MISSING_TOKEN、CG-08系統一・D-17）
        p._fail("MISSING_TOKEN", (obj_role,), ot)
    resp["roles"][obj_role] = {"value": ot.value, "preposition": None,
                              "span": {"start": ot.start, "end": ot.end}}
    if literal:
        resp["object_literal"] = literal

    # 前置詞Role句（§21.8: 写像外=UNMAPPED_ROLE、重複=DUPLICATE_ROLE）
    role_map = {prep: spec["role"] for prep, spec in (b.get("roles") or {}).items()}
    while True:
        tok = p.peek()
        if tok.kind != "W":
            break
        w = tok.value
        if b.get("retention_clause") and w == "for":
            break
        if (w == "by" and p.peek(1).kind == "W" and p.peek(1).value == "checking"
                and p.peek(2).kind == "W" and p.peek(2).value == "that"):
            p.next(); p.next(); p.next()
            prep = "by checking that"   # VoR VALIDATE構文（Gate B二名確定。RC-006）
        elif w in _PREPOSITIONS:
            p.next()
            prep = w
        else:
            break
        val, span = p.np_with_span()
        role = role_map.get(prep)
        if role is None:
            raise ParseError(
                f"preposition {prep!r} has no role mapping for {fam}",
                code="UNMAPPED_ROLE", offset=tok.start, text=p.text,
                expected=tuple(sorted(role_map)), found=prep)
        if role in resp["roles"]:
            raise ParseError(
                f"duplicate role {role!r} (cardinality 1)",
                code="DUPLICATE_ROLE", offset=tok.start, text=p.text,
                expected=(f"single {role}",), found=prep)
        resp["roles"][role] = {"value": val, "preposition": prep, "span": span}

    # KEEP_15_2 retention句（期間+開始点一体のみ。§21.6）
    if b.get("retention_clause") and p.peek().kind == "W" and p.peek().value == "for":
        p.next()
        p.expect_word("a")
        p.expect_word("period")
        p.expect_word("of")
        pt = p.next()
        if pt.kind != "Q":
            p._fail("UNEXPECTED_TOKEN", ("quoted period",), pt)
        p.expect_word("starting")
        p.expect_word("from")
        st = p.next()
        if st.kind != "Q":
            p._fail("UNEXPECTED_TOKEN", ("quoted start date",), st)
        resp["retention"] = {"period": pt.value, "start": st.value,
                             "span": {"start": pt.start, "end": st.end}}

    # Canonical 0.9 Atomic Response leaf-local frequency.  The quoted payload
    # is preserved for provenance while value/unit are the semantic authority.
    if p.accept_word("every"):
        ft = p.next()
        if ft.kind != "Q":
            p._fail("UNEXPECTED_TOKEN", ("quoted frequency",), ft)
        match = re.fullmatch(
            r"\s*([0-9]+(?:\.[0-9]+)?)\s+"
            r"(second|seconds|minute|minutes|hour|hours|day|days)\s*",
            ft.value,
        )
        if match is None or float(match.group(1)) <= 0:
            p._fail(
                "UNEXPECTED_TOKEN",
                ("positive number plus second/minute/hour/day",),
                ft,
            )
        number = float(match.group(1))
        resp["frequency"] = {
            "value": int(number) if number.is_integer() else number,
            "unit": match.group(2).removesuffix("s"),
            "source_expression": ft.value,
        }

    # 必須Role検査（modality/動詞別免除を適用。欠落=MISSING_TOKEN）
    required = list(b.get("required_roles") or [])
    if resp["modality"] == "MUST_NOT":
        required = [r for r in required if r not in (b.get("mustnot_waived_roles") or [])]
    waived = (b.get("verb_role_waivers") or {}).get(verb) or []
    required = [r for r in required if r not in waived]
    missing = sorted(r for r in required if r not in resp["roles"])
    if missing:
        tok = p.peek()
        raise ParseError(
            f"required role(s) missing for {fam}: {', '.join(missing)}",
            code="MISSING_TOKEN", offset=tok.start, text=p.text,
            expected=tuple(missing), found=tok.value)
    return resp


def _parse_response_expression(p: _P, sentence_initial: bool = False) -> dict:
    """完全括弧化されたResponse式木を左から右へ構築する。

    単一Responseは従来の ``response`` AST契約へ残し、本関数は括弧を検出した場合
    だけ呼ばれる。これにより既存consumerの単一文互換を維持する。
    """
    if not p.accept_punct("("):
        return {"kind": "response",
                "response": _parse_response(p, sentence_initial=sentence_initial)}

    left = _parse_response_expression(p, sentence_initial=sentence_initial)
    if p.accept_punct(")"):
        return {"kind": "group", "expression": left}

    connector_tok = p.peek()
    connector = p.accept_word("and", "or")
    if connector is None:
        p._fail("UNEXPECTED_TOKEN", ("and", "or", ")"), connector_tok)
    right = _parse_response_expression(p, sentence_initial=False)
    p.expect_punct(")")
    return {"kind": connector, "left": left, "right": right}


def _starts_response_block(p: _P) -> bool:
    return (
        p.peek().kind == "W" and p.peek().value == "do" and
        p.peek(1).kind == "W" and p.peek(1).value == "the" and
        p.peek(2).kind == "W" and p.peek(2).value == "following" and
        p.peek(3).kind == "W" and p.peek(3).value == "actions"
    )


def _parse_response_block(p: _P) -> dict:
    """Parse the adopted fully-explicit English itemized block surface."""
    for word in ("do", "the", "following", "actions"):
        p.expect_word(word)
    in_sequence = False
    if p.accept_word("in"):
        p.expect_word("sequence")
        in_sequence = True
    p.expect_punct(":")

    reverse_connector = {
        "none": None,
        "comma": "comma",
        "and": "and",
        "or": "or",
        "comma_and": "comma_and",
        "comma_or": "comma_or",
    }
    items: list[dict] = []
    while True:
        p.expect_punct("[")
        p.expect_word("item")
        p.expect_punct("=")
        bullet = p.accept_punct("-")
        if bullet is None:
            bullet = p.expect_number()
        p.expect_punct(";")
        p.expect_word("connector")
        p.expect_punct("=")
        connector_position = p.peek()
        connector_token = p.expect_word(*reverse_connector)
        connector = reverse_connector[connector_token]
        if (not items and connector is not None) or (items and connector is None):
            p._fail(
                "UNEXPECTED_TOKEN",
                ("none" if not items else "non-none connector",),
                connector_position,
            )
        p.expect_punct("]")
        items.append({
            "position": len(items),
            "bullet": {
                "kind": "hyphen" if bullet == "-" else "integer",
                "value": bullet,
            },
            "connector_before": connector,
            "response": _parse_response(p, sentence_initial=False),
        })
        if p.peek().kind != "P" or p.peek().value != ";":
            break
        p.next()
    return {"kind": "itemized", "in_sequence": in_sequence, "items": items}


def parse(text: str) -> dict:
    """English Rimay文 → AST（受理失敗は構造化ParseError）。

    成功時の不変条件: 全非空白文字が消費済み
    （``parse_meta.consumed == {"start": 0, "end": len(text)}``）。
    """
    p = _P(text)
    ast: dict = {"scope": None, "conditions": []}

    # Scope keywordは 'For' のみ（D-01。'for'は明示拒否して診断を固定する）
    t0 = p.peek()
    if t0.kind == "W" and t0.value == "for" and p.peek(1).kind == "Q":
        raise ParseError(
            "scope keyword must be 'For'",
            code="UNEXPECTED_TOKEN", offset=t0.start, text=text,
            expected=("For",), found="for")
    if p.accept_word("For"):
        ast["scope"] = p.np()
        p.expect_punct(",")

    has_condition = False
    if _starts_condition_expression(p):
        ast["condition_expression"] = _parse_condition_expression(p)
        has_condition = True
        p.expect_punct(",")
        p.accept_word("then")
    elif p.peek().kind == "W" and p.peek().value in _CONDITION_WORDS:
        ast["conditions"].append(_parse_condition(p))
        has_condition = True
        p.expect_punct(",")
        p.accept_word("then")

    if _starts_response_block(p):
        ast["response_block"] = _parse_response_block(p)
    elif p.peek().kind == "P" and p.peek().value == "(":
        ast["response_expression"] = _parse_response_expression(
            p, sentence_initial=not has_condition)
    else:
        ast["response"] = _parse_response(p, sentence_initial=not has_condition)

    p.expect_punct(".")
    tail = p.peek()
    if tail.kind != "EOF":
        raise ParseError(
            f"trailing tokens: {tail.value!r}",
            code="TRAILING_TOKEN", offset=tail.start, text=text,
            expected=("end of input",), found=tail.value)

    ast["parse_meta"] = {
        "consumed": {"start": 0, "end": len(text)},
        "parser_version": PARSER_VERSION,
        "grammar_profile_hash": grammar_profile_hash(),
    }
    return ast


def verb_family(verb: str) -> str:
    """動詞→family（トリガー動詞を含む。equivalenceのevent正規化が使用）。"""
    return trigger_verb_index()[verb.lower()]
