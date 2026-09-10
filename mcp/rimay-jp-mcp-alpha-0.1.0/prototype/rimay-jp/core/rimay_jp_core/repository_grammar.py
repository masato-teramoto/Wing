"""固定 Rimay Xtext Grammar の clean-room 実行用 IR compiler。

Grammar本文や生成IR本文はrepositoryへ保存しない。利用者が権限を持つGrammar実体を
明示的に渡したときだけ、全productionをメモリ上の閉じたIRへ変換する。論文corpus、
Capability承認、Supported Profileは入力にしない。
"""
from __future__ import annotations

import ast
import copy
import hashlib
import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable


FIXED_COMMIT = "7308c20125f6678333282e31cda75a82e68b4970"
FIXED_GRAMMAR_SHA256 = "0f7c4af22ab60329e85b972951be46bedecae2da2a5913b10d2f01d05bb1aa7e"
FIXED_GRAMMAR_PATH = "org.xtext.dsl_rimay/src/org/xtext/Dsl_rimay.xtext"
IR_SCHEMA_VERSION = "0.1.0"
SYNTAX_TREE_SCHEMA_VERSION = "0.1.0"
SYNTAX_TREE_KEYS = {
    "rule": frozenset({"kind", "name", "rule_kind", "returns", "span", "child"}),
    "sequence": frozenset({"kind", "span", "children"}),
    "choice": frozenset({"kind", "selected_index", "alternative_count", "span", "child"}),
    "repeat": frozenset({"kind", "min", "max", "count", "span", "children"}),
    "assignment": frozenset({"kind", "feature", "operator", "span", "child"}),
    "cross_reference": frozenset({
        "kind", "target", "terminal", "surface", "span", "terminal_rule",
        "linking_checked",
    }),
    "terminal": frozenset({"kind", "name", "surface", "span"}),
    "literal": frozenset({"kind", "value", "surface", "span"}),
    "enum_literal": frozenset({"kind", "name", "surface", "span"}),
    "tree_action": frozenset({"kind", "type", "feature", "value", "span"}),
    "epsilon": frozenset({"kind", "span"}),
}
COMMON_TERMINALS = frozenset({"ID", "INT", "STRING", "ML_COMMENT", "SL_COMMENT", "WS",
                              "ANY_OTHER"})
NODE_KINDS = frozenset({
    "choice", "sequence", "repeat", "literal", "rule_ref", "terminal_ref",
    "assignment", "cross_reference", "tree_action", "enum_literal", "epsilon",
})
CARDINALITIES = {"?": (0, 1), "*": (0, None), "+": (1, None)}
RECOGNIZER_EXIT_CODE_BY_STATUS = {
    "accepted": 0,
    "canonical_ready": 0,
    "not_matched": 1,
    "linking_failed": 3,
    "repository_projection_failed": 4,
    "canonical_projection_failed": 4,
    "canonical_projection_incomplete": 4,
}


class GrammarCompileError(ValueError):
    """Grammarを損失なく閉じたIRへ変換できない。"""


def syntax_tree_children(node: dict):
    """Yield the structural children allowed by the closed syntax-tree schema."""
    child = node.get("child")
    if isinstance(child, dict):
        yield child
    terminal_rule = node.get("terminal_rule")
    if isinstance(terminal_rule, dict):
        yield terminal_rule
    for item in node.get("children", []):
        if isinstance(item, dict):
            yield item


def walk_syntax_tree(node: dict):
    """Walk a validated syntax tree in deterministic pre-order."""
    yield node
    for child in syntax_tree_children(node):
        yield from walk_syntax_tree(child)


def direct_syntax_rule_children(rule: dict) -> list[dict]:
    """Return selected rule calls without leaking their nested descendants."""
    found = []

    def visit(node: dict) -> None:
        for child in syntax_tree_children(node):
            if child.get("kind") == "rule":
                found.append(child)
            else:
                visit(child)

    visit(rule)
    return found


def recognizer_status_exit_code(status: str) -> int:
    """Map the closed recognizer result status to the public CLI contract."""
    try:
        return RECOGNIZER_EXIT_CODE_BY_STATUS[status]
    except KeyError as exc:
        raise ValueError(f"unknown recognizer status: {status}") from exc


@dataclass(frozen=True)
class Token:
    kind: str
    value: str
    offset: int


@dataclass(frozen=True)
class RuleIR:
    name: str
    kind: str
    returns: str | None
    expression: dict

    def canonical(self) -> dict:
        return {"name": self.name, "kind": self.kind, "returns": self.returns,
                "expression": self.expression}


@dataclass(frozen=True)
class GrammarIR:
    grammar_name: str
    generated_namespace: str
    source_sha256: str
    rules: tuple[RuleIR, ...]

    @property
    def by_name(self) -> dict[str, RuleIR]:
        return {rule.name: rule for rule in self.rules}

    def canonical(self) -> dict:
        return {
            "ir_schema_version": IR_SCHEMA_VERSION,
            "grammar_name": self.grammar_name,
            "generated_namespace": self.generated_namespace,
            "source_sha256": self.source_sha256,
            "rules": [rule.canonical() for rule in self.rules],
        }

    def signature(self) -> str:
        raw = json.dumps(self.canonical(), ensure_ascii=False, sort_keys=True,
                         separators=(",", ":")).encode("utf-8")
        return "sha256:" + hashlib.sha256(raw).hexdigest()

    def statistics(self) -> dict:
        counts = {kind: 0 for kind in sorted(NODE_KINDS)}
        bounded, unbounded = 0, 0

        def visit(node: dict) -> None:
            nonlocal bounded, unbounded
            counts[node["kind"]] += 1
            if node["kind"] == "repeat":
                if node["max"] is None:
                    unbounded += 1
                else:
                    bounded += 1
            for child in node.get("children", []):
                visit(child)
            if "child" in node:
                visit(node["child"])

        for rule in self.rules:
            visit(rule.expression)
        return {
            "parser_rule_count": sum(rule.kind == "parser_rule" for rule in self.rules),
            "enum_count": sum(rule.kind == "enum" for rule in self.rules),
            "rule_count": len(self.rules),
            "node_counts": counts,
            "bounded_repeat_count": bounded,
            "unbounded_repeat_count": unbounded,
        }

    def recognizer(self) -> "RepositoryGrammarRecognizer":
        """このIRを実行する構文recognizerを返す。"""
        return RepositoryGrammarRecognizer(self)


def _strip_comments(raw: str) -> str:
    out: list[str] = []
    index = 0
    quote: str | None = None
    while index < len(raw):
        char = raw[index]
        if quote:
            out.append(char)
            if char == "\\" and index + 1 < len(raw):
                out.append(raw[index + 1])
                index += 2
                continue
            if char == quote:
                quote = None
            index += 1
            continue
        if char in "'\"":
            quote = char
            out.append(char)
            index += 1
            continue
        if raw.startswith("//", index):
            while index < len(raw) and raw[index] != "\n":
                index += 1
            continue
        if raw.startswith("/*", index):
            end = raw.find("*/", index + 2)
            if end < 0:
                raise GrammarCompileError(f"unterminated block comment at offset {index}")
            # Keep line boundaries so column-zero headers cannot be fabricated by comment removal.
            comment = raw[index:end + 2]
            out.append(" ")
            out.extend("\n" for char in comment if char == "\n")
            out.append(" ")
            index = end + 2
            continue
        out.append(char)
        index += 1
    if quote:
        raise GrammarCompileError("unterminated quoted string")
    return "".join(out)


_HEADER = re.compile(
    r"^(?P<enum>enum\s+)?(?P<name>[A-Za-z_][A-Za-z0-9_]*)\s*"
    r"(?:returns\s+(?P<returns>[A-Za-z_][A-Za-z0-9_.]*)\s*)?:")
_GRAMMAR = re.compile(
    r"(?m)^grammar\s+(?P<name>[A-Za-z_][A-Za-z0-9_.]*)\s+with\s+"
    r"org\.eclipse\.xtext\.common\.Terminals\s*$")
_GENERATE = re.compile(
    r"(?m)^generate\s+[A-Za-z_][A-Za-z0-9_]*\s+['\"](?P<uri>[^'\"]+)['\"]\s*$")


def _blocks(clean: str) -> tuple[str, str, list[tuple[str, str, str | None, str]]]:
    grammar = _GRAMMAR.search(clean)
    generated = _GENERATE.search(clean)
    if not grammar or not generated:
        raise GrammarCompileError("grammar/generate directive is missing or unsupported")
    lines = clean.splitlines()
    headers: list[tuple[int, str, str, str | None]] = []
    for line_no, line in enumerate(lines):
        if not line or line[0].isspace():
            continue
        match = _HEADER.match(line)
        if match:
            headers.append((line_no, match.group("name"),
                            "enum" if match.group("enum") else "parser_rule",
                            match.group("returns")))
    if not headers:
        raise GrammarCompileError("no rule headers found")
    result = []
    for index, (line_no, name, kind, returns) in enumerate(headers):
        end = headers[index + 1][0] if index + 1 < len(headers) else len(lines)
        block = "\n".join(lines[line_no:end])
        colon = block.find(":")
        body = block[colon + 1:].strip()
        if not body.endswith(";"):
            raise GrammarCompileError(f"{name}: production does not end with semicolon")
        body = body[:-1].strip()
        if not body:
            raise GrammarCompileError(f"{name}: empty production")
        result.append((name, kind, returns, body))
    names = [name for name, _, _, _ in result]
    if len(names) != len(set(names)):
        raise GrammarCompileError("duplicate rule header")
    return grammar.group("name"), generated.group("uri"), result


def _decode_string(raw: str, offset: int) -> str:
    try:
        value = ast.literal_eval(raw)
    except (SyntaxError, ValueError) as exc:
        raise GrammarCompileError(f"invalid keyword literal at offset {offset}: {raw!r}") from exc
    if not isinstance(value, str):
        raise GrammarCompileError(f"non-string keyword literal at offset {offset}")
    return value


def _tokens(body: str) -> list[Token]:
    result: list[Token] = []
    index = 0
    multi = ("+=", "?=")
    single = frozenset("()[]{}|?*+=.")
    while index < len(body):
        char = body[index]
        if char.isspace():
            index += 1
            continue
        operator = next((item for item in multi if body.startswith(item, index)), None)
        if operator:
            result.append(Token("symbol", operator, index))
            index += len(operator)
            continue
        if char in single:
            result.append(Token("symbol", char, index))
            index += 1
            continue
        if char in "'\"":
            start = index
            quote = char
            index += 1
            while index < len(body):
                if body[index] == "\\" and index + 1 < len(body):
                    index += 2
                    continue
                if body[index] == quote:
                    index += 1
                    break
                index += 1
            else:
                raise GrammarCompileError(f"unterminated keyword literal at offset {start}")
            result.append(Token("string", _decode_string(body[start:index], start), start))
            continue
        match = re.match(r"[A-Za-z_][A-Za-z0-9_]*", body[index:])
        if match:
            value = match.group(0)
            result.append(Token("identifier", value, index))
            index += len(value)
            continue
        raise GrammarCompileError(f"unsupported Grammar character at offset {index}: {char!r}")
    result.append(Token("eof", "", len(body)))
    return result


def _node(kind: str, **values) -> dict:
    return {"kind": kind, **values}


class _ExpressionParser:
    def __init__(self, tokens: list[Token], *, enum: bool = False):
        self.tokens = tokens
        self.index = 0
        self.enum = enum

    def peek(self, value: str | None = None) -> Token:
        token = self.tokens[self.index]
        if value is None or token.value == value:
            return token
        return Token("mismatch", "", token.offset)

    def take(self, value: str | None = None) -> Token:
        token = self.tokens[self.index]
        if value is not None and token.value != value:
            raise GrammarCompileError(
                f"expected {value!r} at offset {token.offset}, found {token.value!r}")
        self.index += 1
        return token

    def peek_symbol(self, value: str) -> Token:
        token = self.tokens[self.index]
        if token.kind == "symbol" and token.value == value:
            return token
        return Token("mismatch", "", token.offset)

    def take_symbol(self, value: str) -> Token:
        token = self.tokens[self.index]
        if token.kind != "symbol" or token.value != value:
            raise GrammarCompileError(
                f"expected symbol {value!r} at offset {token.offset}, "
                f"found {token.value!r}")
        self.index += 1
        return token

    def parse(self) -> dict:
        expression = self.choice(stop={""})
        if self.peek().kind != "eof":
            token = self.peek()
            raise GrammarCompileError(f"unconsumed token {token.value!r} at offset {token.offset}")
        return expression

    def choice(self, stop: set[str]) -> dict:
        children = [self.sequence(stop | {"|"})]
        while self.peek_symbol("|").kind != "mismatch":
            self.take_symbol("|")
            children.append(self.sequence(stop | {"|"}))
        return children[0] if len(children) == 1 else _node("choice", children=children)

    def sequence(self, stop: set[str]) -> dict:
        children = []
        while self.peek().kind != "eof" and not (
                self.peek().kind == "symbol" and self.peek().value in stop):
            children.append(self.postfix())
        if not children:
            return _node("epsilon")
        return children[0] if len(children) == 1 else _node("sequence", children=children)

    def postfix(self) -> dict:
        if self.peek().kind == "identifier" and \
                self.tokens[self.index + 1].kind == "symbol" and \
                self.tokens[self.index + 1].value in {"=", "+=", "?="}:
            feature = self.take().value
            operator = self.take().value
            child = self.atom()
            value = _node("assignment", feature=feature, operator=operator, child=child)
        else:
            value = self.atom()
        if self.peek().kind == "symbol" and self.peek().value in CARDINALITIES:
            marker = self.take().value
            minimum, maximum = CARDINALITIES[marker]
            value = _node("repeat", min=minimum, max=maximum, child=value)
        return value

    def atom(self) -> dict:
        token = self.peek()
        if token.kind == "symbol" and token.value == "(":
            self.take_symbol("(")
            child = self.choice(stop={")"})
            self.take_symbol(")")
            return child
        if token.kind == "symbol" and token.value == "[":
            self.take_symbol("[")
            target = self.take()
            if target.kind != "identifier":
                raise GrammarCompileError(f"cross-reference target is invalid at {target.offset}")
            terminal = None
            if self.peek_symbol("|").kind != "mismatch":
                self.take_symbol("|")
                terminal_token = self.take()
                if terminal_token.kind != "identifier":
                    raise GrammarCompileError(
                        f"cross-reference terminal is invalid at {terminal_token.offset}")
                terminal = terminal_token.value
            self.take_symbol("]")
            return _node("cross_reference", target=target.value, terminal=terminal)
        if token.kind == "symbol" and token.value == "{":
            self.take_symbol("{")
            type_token = self.take()
            self.take_symbol(".")
            feature = self.take()
            self.take_symbol("=")
            value = self.take()
            self.take_symbol("}")
            if any(item.kind != "identifier" for item in (type_token, feature, value)):
                raise GrammarCompileError(f"tree action is malformed at {token.offset}")
            return _node("tree_action", type=type_token.value, feature=feature.value,
                         value=value.value)
        if token.kind == "string":
            self.take()
            return _node("literal", value=token.value)
        if token.kind == "identifier":
            self.take()
            return _node("enum_literal" if self.enum else "rule_ref", name=token.value)
        raise GrammarCompileError(f"expected Grammar atom at offset {token.offset}, "
                                  f"found {token.value!r}")


def _walk(node: dict) -> Iterable[dict]:
    yield node
    for child in node.get("children", []):
        yield from _walk(child)
    if "child" in node:
        yield from _walk(node["child"])


def _resolve(rules: list[RuleIR]) -> tuple[RuleIR, ...]:
    names = {rule.name for rule in rules}
    resolved = []
    problems = []
    for rule in rules:
        expression = json.loads(json.dumps(rule.expression))
        if any(node["kind"] == "epsilon" for node in _walk(expression)):
            problems.append(f"{rule.name}: implicit empty alternative is not supported")
        for node in _walk(expression):
            if node["kind"] != "rule_ref":
                continue
            name = node["name"]
            if name in names:
                continue
            if name in COMMON_TERMINALS:
                node["kind"] = "terminal_ref"
                continue
            problems.append(f"{rule.name}: unresolved rule/terminal reference {name}")
        for node in _walk(expression):
            if node["kind"] == "cross_reference":
                terminal = node["terminal"] or "ID"
                if terminal not in names and terminal not in COMMON_TERMINALS:
                    problems.append(
                        f"{rule.name}: unresolved cross-reference terminal {terminal}")
        resolved.append(RuleIR(rule.name, rule.kind, rule.returns, expression))
    if problems:
        raise GrammarCompileError("; ".join(problems))
    return tuple(resolved)


def _nullable(node: dict, nullable_rules: frozenset[str]) -> bool:
    """Return whether ``node`` can finish without consuming source text."""
    kind = node["kind"]
    if kind in {"epsilon", "tree_action"}:
        return True
    if kind == "literal":
        return node.get("value") == ""
    if kind == "enum_literal":
        return node.get("name") == ""
    if kind == "rule_ref":
        return node["name"] in nullable_rules
    if kind == "assignment":
        return _nullable(node["child"], nullable_rules)
    if kind == "repeat":
        return node["min"] == 0 or _nullable(node["child"], nullable_rules)
    if kind == "choice":
        return any(_nullable(child, nullable_rules) for child in node["children"])
    if kind == "sequence":
        return all(_nullable(child, nullable_rules) for child in node["children"])
    return False


def _nullable_rule_names(rules: tuple[RuleIR, ...]) -> frozenset[str]:
    nullable: set[str] = set()
    while True:
        expanded = {
            rule.name for rule in rules
            if _nullable(rule.expression, frozenset(nullable))
        }
        if expanded <= nullable:
            return frozenset(nullable)
        nullable.update(expanded)


def _left_corners(node: dict, nullable_rules: frozenset[str],
                  rule_names: frozenset[str]) -> set[str]:
    """Parser rules reachable before any terminal or keyword is consumed."""
    kind = node["kind"]
    if kind == "rule_ref":
        return {node["name"]}
    if kind == "cross_reference":
        terminal = node.get("terminal") or "ID"
        return {terminal} if terminal in rule_names else set()
    if kind == "assignment":
        return _left_corners(node["child"], nullable_rules, rule_names)
    if kind == "repeat":
        return _left_corners(node["child"], nullable_rules, rule_names)
    if kind == "choice":
        return set().union(*(
            _left_corners(child, nullable_rules, rule_names)
            for child in node["children"]
        ))
    if kind == "sequence":
        result: set[str] = set()
        for child in node["children"]:
            result.update(_left_corners(child, nullable_rules, rule_names))
            if not _nullable(child, nullable_rules):
                break
        return result
    return set()


def _left_recursion_cycle(rules: tuple[RuleIR, ...]) -> tuple[str, ...] | None:
    """Find one deterministic direct/indirect left-recursion cycle."""
    names = frozenset(rule.name for rule in rules)
    nullable = _nullable_rule_names(rules)
    graph = {
        rule.name: tuple(sorted(_left_corners(rule.expression, nullable, names)))
        for rule in rules
    }
    state: dict[str, int] = {}
    stack: list[str] = []

    def visit(name: str) -> tuple[str, ...] | None:
        state[name] = 1
        stack.append(name)
        for next_name in graph[name]:
            if state.get(next_name) == 1:
                start = stack.index(next_name)
                return tuple(stack[start:] + [next_name])
            if state.get(next_name, 0) == 0:
                cycle = visit(next_name)
                if cycle:
                    return cycle
        stack.pop()
        state[name] = 2
        return None

    for name in sorted(graph):
        if state.get(name, 0) == 0:
            cycle = visit(name)
            if cycle:
                return cycle
    return None


def _reject_left_recursion(rules: tuple[RuleIR, ...]) -> None:
    cycle = _left_recursion_cycle(rules)
    if cycle:
        raise GrammarCompileError(
            "left recursion is unsupported: " + " -> ".join(cycle))


def compile_xtext_grammar(raw: str, *, expected_sha256: str | None = None) -> GrammarIR:
    raw_bytes = raw.encode("utf-8")
    actual = hashlib.sha256(raw_bytes).hexdigest()
    if expected_sha256 is not None and actual != expected_sha256:
        raise GrammarCompileError(
            f"Grammar sha256 mismatch: expected {expected_sha256}, actual {actual}")
    clean = _strip_comments(raw)
    grammar_name, namespace, blocks = _blocks(clean)
    parsed = []
    for name, kind, returns, body in blocks:
        try:
            expression = _ExpressionParser(_tokens(body), enum=kind == "enum").parse()
        except GrammarCompileError as exc:
            raise GrammarCompileError(f"{name}: {exc}") from exc
        parsed.append(RuleIR(name, kind, returns, expression))
    resolved = _resolve(parsed)
    _reject_left_recursion(resolved)
    return GrammarIR(grammar_name, namespace, "sha256:" + actual, resolved)


def compile_fixed_grammar(path: str | Path) -> GrammarIR:
    source = Path(path)
    if not source.is_file():
        raise GrammarCompileError(f"Grammar source does not exist: {source}")
    return compile_xtext_grammar(source.read_text(encoding="utf-8"),
                                 expected_sha256=FIXED_GRAMMAR_SHA256)


@dataclass(frozen=True)
class RecognitionResult:
    accepted: bool
    start_rule: str
    end_offsets: tuple[int, ...]
    furthest_offset: int


@dataclass(frozen=True)
class SyntaxParseResult:
    accepted: bool
    start_rule: str
    tree: dict | None
    furthest_offset: int
    consumed_end: int | None
    selection_policy: str
    ambiguity_checked: bool
    ambiguity_detected: bool | None
    semantic_linking_checked: bool
    xtext_validator_checked: bool
    grammar_ir_signature: str
    grammar_source_sha256: str
    source_sha256: str

    def diagnostic(self) -> dict:
        return {
            "syntax_tree_schema_version": SYNTAX_TREE_SCHEMA_VERSION,
            "accepted": self.accepted,
            "start_rule": self.start_rule,
            "furthest_offset": self.furthest_offset,
            "consumed_end": self.consumed_end,
            "selection_policy": self.selection_policy,
            "ambiguity_checked": self.ambiguity_checked,
            "ambiguity_detected": self.ambiguity_detected,
            "semantic_linking_checked": self.semantic_linking_checked,
            "xtext_validator_checked": self.xtext_validator_checked,
            "grammar_ir_signature": self.grammar_ir_signature,
            "grammar_source_sha256": self.grammar_source_sha256,
            "source_sha256": self.source_sha256,
        }


def syntax_tree_signature(tree: object) -> str:
    raw = json.dumps(tree, ensure_ascii=False, sort_keys=True,
                     separators=(",", ":")).encode("utf-8")
    return "sha256:" + hashlib.sha256(raw).hexdigest()


def syntax_tree_problems(tree: object, source_text: str,
                         *, expected_root: str | None = None) -> tuple[str, ...]:
    """Repository構文木の閉Schemaとsource spanを検査する。

    semantic linkingやXtext validatorの成功は、この検査を通っても主張しない。
    """
    problems: list[str] = []
    if not isinstance(source_text, str):
        return ("source_text must be a string",)

    def scalar(value: object, label: str, path: str) -> bool:
        if not isinstance(value, str) or not value:
            problems.append(f"{path}.{label} must be a non-empty string")
            return False
        return True

    def visit(node: object, path: str, parent_span: tuple[int, int] | None = None) -> None:
        if not isinstance(node, dict):
            problems.append(f"{path} must be a mapping")
            return
        kind = node.get("kind")
        if not isinstance(kind, str) or kind not in SYNTAX_TREE_KEYS:
            problems.append(f"{path}.kind is unknown: {kind!r}")
            return
        keys = frozenset(node)
        expected = SYNTAX_TREE_KEYS[kind]
        if keys != expected:
            problems.append(
                f"{path} keys mismatch: "
                f"missing={sorted(map(repr, expected - keys))!r}, "
                f"extra={sorted(map(repr, keys - expected))!r}")
        span = node.get("span")
        current_span: tuple[int, int] | None = None
        if not isinstance(span, dict) or frozenset(span) != {"start", "end"} or \
                type(span.get("start")) is not int or type(span.get("end")) is not int:
            problems.append(f"{path}.span must contain integer start/end only")
        else:
            start, end = span["start"], span["end"]
            current_span = (start, end)
            if not 0 <= start <= end <= len(source_text):
                problems.append(f"{path}.span is outside source bounds: {span!r}")
            if parent_span and not (parent_span[0] <= start <= end <= parent_span[1]):
                problems.append(f"{path}.span is outside parent span: {span!r}")
        child_parent = current_span or parent_span

        if kind == "rule":
            scalar(node.get("name"), "name", path)
            if node.get("rule_kind") not in {"parser_rule", "enum"}:
                problems.append(f"{path}.rule_kind is invalid: {node.get('rule_kind')!r}")
            if node.get("returns") is not None:
                scalar(node.get("returns"), "returns", path)
            visit(node.get("child"), f"{path}.child", child_parent)
        elif kind in {"sequence", "repeat"}:
            children = node.get("children")
            if not isinstance(children, list):
                problems.append(f"{path}.children must be a list")
            else:
                previous_end = child_parent[0] if child_parent else 0
                for index, child in enumerate(children):
                    visit(child, f"{path}.children[{index}]", child_parent)
                    child_span = child.get("span") if isinstance(child, dict) else None
                    if isinstance(child_span, dict) and type(child_span.get("start")) is int \
                            and child_span["start"] < previous_end:
                        problems.append(f"{path}.children are not source ordered")
                    if isinstance(child_span, dict) and type(child_span.get("end")) is int:
                        previous_end = max(previous_end, child_span["end"])
            if kind == "repeat":
                minimum, maximum, count = node.get("min"), node.get("max"), node.get("count")
                if type(minimum) is not int or minimum < 0:
                    problems.append(f"{path}.min must be a non-negative integer")
                if maximum is not None and (type(maximum) is not int or maximum < 0):
                    problems.append(f"{path}.max must be null or a non-negative integer")
                if type(count) is not int or count < 0:
                    problems.append(f"{path}.count must be a non-negative integer")
                elif isinstance(children, list) and count != len(children):
                    problems.append(f"{path}.count does not match children length")
                if type(minimum) is int and type(count) is int and count < minimum:
                    problems.append(f"{path}.count is below min")
                if type(maximum) is int and type(count) is int and count > maximum:
                    problems.append(f"{path}.count is above max")
                if type(minimum) is int and type(maximum) is int and minimum > maximum:
                    problems.append(f"{path}.min is above max")
        elif kind == "choice":
            selected = node.get("selected_index")
            count = node.get("alternative_count")
            if type(count) is not int or count <= 0:
                problems.append(f"{path}.alternative_count must be a positive integer")
            if type(selected) is not int or selected < 0 or \
                    (type(count) is int and selected >= count):
                problems.append(f"{path}.selected_index is outside alternatives")
            visit(node.get("child"), f"{path}.child", child_parent)
        elif kind == "assignment":
            scalar(node.get("feature"), "feature", path)
            if node.get("operator") not in {"=", "+=", "?="}:
                problems.append(f"{path}.operator is invalid: {node.get('operator')!r}")
            visit(node.get("child"), f"{path}.child", child_parent)
        elif kind == "cross_reference":
            scalar(node.get("target"), "target", path)
            scalar(node.get("terminal"), "terminal", path)
            if type(node.get("linking_checked")) is not bool:
                problems.append(f"{path}.linking_checked must be bool")
            terminal_rule = node.get("terminal_rule")
            if terminal_rule is not None:
                visit(terminal_rule, f"{path}.terminal_rule", child_parent)
        elif kind == "terminal":
            scalar(node.get("name"), "name", path)
        elif kind == "literal":
            scalar(node.get("value"), "value", path)
        elif kind == "enum_literal":
            scalar(node.get("name"), "name", path)
        elif kind == "tree_action":
            scalar(node.get("type"), "type", path)
            if node.get("feature") is not None:
                scalar(node.get("feature"), "feature", path)
            if node.get("value") is not None:
                scalar(node.get("value"), "value", path)

        if kind in {"literal", "enum_literal", "terminal", "cross_reference"}:
            surface = node.get("surface")
            if not isinstance(surface, str):
                problems.append(f"{path}.surface must be a string")
            elif current_span and source_text[current_span[0]:current_span[1]] != surface:
                problems.append(f"{path}.surface does not match source span")
        if kind in {"epsilon", "tree_action"} and current_span and \
                current_span[0] != current_span[1]:
            problems.append(f"{path} must have a zero-width span")

    visit(tree, "tree")
    if isinstance(tree, dict) and expected_root is not None and \
            (tree.get("kind") != "rule" or tree.get("name") != expected_root):
        problems.append("tree root does not match expected_root")
    return tuple(problems)


class RepositoryGrammarRecognizer:
    """Grammar IRの全EBNF nodeを解釈する構文recognizer。

    Xtextのcross-referenceは構文上のterminalだけを照合する。参照先のscope/linking、
    validator、生成AST型は別層であり、本classはそれらの成功を主張しない。
    """

    _ID = re.compile(r"\^?[A-Za-z_][A-Za-z0-9_]*")
    _INT = re.compile(r"[0-9]+")

    def __init__(self, grammar: GrammarIR):
        # Recheck at the execution boundary as GrammarIR expressions are plain
        # dictionaries and callers could construct or mutate an IR manually.
        # The runtime recursion guards remain defense in depth; correctness does
        # not rely on turning a recursive branch into a partial derivation.
        _reject_left_recursion(grammar.rules)
        self.grammar = grammar
        self.rules = grammar.by_name
        self.keywords = frozenset(
            node.get("value") if node["kind"] == "literal" else node.get("name")
            for rule in grammar.rules for node in _walk(rule.expression)
            if node["kind"] in {"literal", "enum_literal"})
        self.word_keywords = frozenset(
            value for value in self.keywords
            if value and re.fullmatch(r"[A-Za-z_][A-Za-z0-9_]*", value))
        self.text = ""
        self._memo: dict[tuple[str, int], frozenset[int]] = {}
        self._active: set[tuple[str, int]] = set()
        self._trace_memo: dict[tuple[str, int, int], dict | None] = {}
        self._trace_active: set[tuple[str, int, int]] = set()
        self._count_memo: dict[tuple[int, int, int], int] = {}
        self._count_rule_memo: dict[tuple[str, int, int], int] = {}
        self._count_rule_active: set[tuple[str, int, int]] = set()
        self._furthest = 0

    def recognize(self, text: str, *, start_rule: str = "CNLFunctionalRequirements") \
            -> RecognitionResult:
        if start_rule not in self.rules:
            raise GrammarCompileError(f"unknown start rule: {start_rule}")
        self.text = text
        self._memo = {}
        self._active = set()
        self._furthest = 0
        starts = self._match_rule(start_rule, 0)
        endpoints = tuple(sorted({self._skip_hidden(offset) for offset in starts}))
        accepted = len(text) in endpoints
        return RecognitionResult(accepted, start_rule, endpoints, self._furthest)

    def parse_syntax(self, text: str, *, start_rule: str = "CNLFunctionalRequirements") \
            -> SyntaxParseResult:
        """full matchをRepository構文木として復元する。

        複数derivationがある場合はGrammar記載順で最初のfull matchを選ぶ。同じIR上の
        full-match derivation数を2件で打ち切って数え、一意性を結果に明示する。Xtext ASTや
        Canonical ASTを自称しない。
        """
        recognition = self.recognize(text, start_rule=start_rule)
        self._trace_memo = {}
        self._trace_active = set()
        self._count_memo = {}
        self._count_rule_memo = {}
        self._count_rule_active = set()
        raw_end = next((end for end in sorted(self._match_rule(start_rule, 0), reverse=True)
                        if self._skip_hidden(end) == len(text)), None)
        if not recognition.accepted or raw_end is None:
            return SyntaxParseResult(
                accepted=False, start_rule=start_rule, tree=None,
                furthest_offset=recognition.furthest_offset, consumed_end=None,
                selection_policy="grammar_order_first_full_match",
                ambiguity_checked=False, ambiguity_detected=None,
                semantic_linking_checked=False, xtext_validator_checked=False,
                grammar_ir_signature=self.grammar.signature(),
                grammar_source_sha256=self.grammar.source_sha256,
                source_sha256="sha256:" + hashlib.sha256(text.encode("utf-8")).hexdigest())
        derivation_count = self._count_rule(start_rule, 0, raw_end)
        if derivation_count == 0:
            raise GrammarCompileError(
                "recognizer accepted input but no finite syntax derivation was counted")
        tree = self._trace_rule(start_rule, 0, raw_end)
        if tree is None:
            raise GrammarCompileError(
                "recognizer accepted input but syntax trace could not be reconstructed")
        problems = syntax_tree_problems(tree, text, expected_root=start_rule)
        if problems:
            raise GrammarCompileError(
                "recognizer produced an invalid syntax tree: " + "; ".join(problems))
        return SyntaxParseResult(
            accepted=True, start_rule=start_rule, tree=tree,
            furthest_offset=recognition.furthest_offset, consumed_end=len(text),
            selection_policy="grammar_order_first_full_match",
            ambiguity_checked=True, ambiguity_detected=derivation_count > 1,
            semantic_linking_checked=False, xtext_validator_checked=False,
            grammar_ir_signature=self.grammar.signature(),
            grammar_source_sha256=self.grammar.source_sha256,
            source_sha256="sha256:" + hashlib.sha256(text.encode("utf-8")).hexdigest())

    def synthesize_minimal(self, rule: str) -> str:
        """指定規則を通る最短の構文fixtureをIRだけから作る。

        cross-referenceは構文terminalのみを満たすplaceholderであり、linking成功は主張しない。
        主用途は全production branchの実行回帰。
        """
        if rule not in self.rules:
            raise GrammarCompileError(f"unknown rule for synthesis: {rule}")
        cache: dict[str, tuple[str, ...]] = {}

        def for_rule(name: str, active: frozenset[str]) -> tuple[str, ...]:
            if name in cache:
                return cache[name]
            if name in active:
                raise GrammarCompileError(f"no non-recursive minimal expansion for {name}")
            value = for_node(self.rules[name].expression, active | {name})
            cache[name] = value
            return value

        def for_node(node: dict, active: frozenset[str]) -> tuple[str, ...]:
            kind = node["kind"]
            if kind in {"epsilon", "tree_action"}:
                return ()
            if kind == "literal":
                return (node["value"],)
            if kind == "enum_literal":
                return (node["name"],)
            if kind == "terminal_ref":
                return terminal(node["name"])
            if kind == "cross_reference":
                cross_terminal = node["terminal"] or "ID"
                return for_rule(cross_terminal, active) if cross_terminal in self.rules \
                    else terminal(cross_terminal)
            if kind == "assignment":
                return for_node(node["child"], active)
            if kind == "rule_ref":
                return for_rule(node["name"], active)
            if kind == "sequence":
                return tuple(item for child in node["children"]
                             for item in for_node(child, active))
            if kind == "choice":
                candidates = []
                for child in node["children"]:
                    try:
                        candidates.append(for_node(child, active))
                    except GrammarCompileError:
                        continue
                if not candidates:
                    raise GrammarCompileError("choice has no finite minimal expansion")
                return min(candidates, key=lambda value: (len(" ".join(value)), value))
            if kind == "repeat":
                return for_node(node["child"], active) * node["min"]
            raise GrammarCompileError(f"unsupported synthesis node: {kind}")

        def terminal(name: str) -> tuple[str, ...]:
            if name == "ID":
                return ("Identifier",)
            if name == "INT":
                return ("1",)
            if name == "STRING":
                return ('"text"',)
            if name == "ANY_OTHER":
                return ("@",)
            raise GrammarCompileError(f"no fixture placeholder for terminal {name}")

        return " ".join(for_rule(rule, frozenset()))

    def _skip_hidden(self, offset: int) -> int:
        while offset < len(self.text):
            match = re.match(r"\s+", self.text[offset:])
            if match:
                offset += match.end()
                continue
            if self.text.startswith("//", offset):
                newline = self.text.find("\n", offset + 2)
                offset = len(self.text) if newline < 0 else newline + 1
                continue
            if self.text.startswith("/*", offset):
                end = self.text.find("*/", offset + 2)
                if end < 0:
                    self._furthest = max(self._furthest, offset)
                    return offset
                offset = end + 2
                continue
            break
        self._furthest = max(self._furthest, offset)
        return offset

    def _match_literal(self, value: str, offset: int) -> frozenset[int]:
        offset = self._skip_hidden(offset)
        if not self.text.startswith(value, offset):
            return frozenset()
        end = offset + len(value)
        if value and (value[-1].isalnum() or value[-1] == "_") and end < len(self.text) \
                and (self.text[end].isalnum() or self.text[end] == "_"):
            return frozenset()
        self._furthest = max(self._furthest, end)
        return frozenset({end})

    def _match_terminal(self, name: str, offset: int) -> frozenset[int]:
        offset = self._skip_hidden(offset)
        if name == "ID":
            match = self._ID.match(self.text, offset)
            if not match:
                return frozenset()
            surface = match.group(0)
            if not surface.startswith("^") and surface in self.word_keywords:
                return frozenset()
            self._furthest = max(self._furthest, match.end())
            return frozenset({match.end()})
        if name == "INT":
            match = self._INT.match(self.text, offset)
            if match:
                self._furthest = max(self._furthest, match.end())
                return frozenset({match.end()})
            return frozenset()
        if name == "STRING":
            if offset >= len(self.text) or self.text[offset] not in "'\"":
                return frozenset()
            quote = self.text[offset]
            index = offset + 1
            while index < len(self.text):
                if self.text[index] == "\\" and index + 1 < len(self.text):
                    index += 2
                    continue
                if self.text[index] == quote:
                    self._furthest = max(self._furthest, index + 1)
                    return frozenset({index + 1})
                if self.text[index] in "\r\n":
                    return frozenset()
                index += 1
            return frozenset()
        if name == "WS":
            match = re.match(r"\s+", self.text[offset:])
            return frozenset({offset + match.end()}) if match else frozenset()
        if name == "SL_COMMENT" and self.text.startswith("//", offset):
            newline = self.text.find("\n", offset + 2)
            return frozenset({len(self.text) if newline < 0 else newline + 1})
        if name == "ML_COMMENT" and self.text.startswith("/*", offset):
            end = self.text.find("*/", offset + 2)
            return frozenset({end + 2}) if end >= 0 else frozenset()
        if name == "ANY_OTHER" and offset < len(self.text):
            return frozenset({offset + 1})
        return frozenset()

    def _match_rule(self, name: str, offset: int) -> frozenset[int]:
        offset = self._skip_hidden(offset)
        key = (name, offset)
        if key in self._memo:
            return self._memo[key]
        if key in self._active:
            # Compiler rejects direct/indirect left recursion. Keep this guard
            # for manually constructed GrammarIR values as a final fail-closed
            # boundary rather than attempting a partial seed-growing parse.
            return frozenset()
        self._active.add(key)
        result = self._match(self.rules[name].expression, offset)
        self._active.remove(key)
        self._memo[key] = result
        return result

    def _span(self, start: int, end: int) -> dict:
        return {"start": start, "end": end}

    def _cover_span(self, children: list[dict], default_start: int, default_end: int) -> dict:
        spans = [child["span"] for child in children if isinstance(child.get("span"), dict)]
        return self._span(min(span["start"] for span in spans),
                          max(span["end"] for span in spans)) if spans \
            else self._span(default_start, default_end)

    def _trace_rule(self, name: str, offset: int, target: int) -> dict | None:
        start = self._skip_hidden(offset)
        key = (name, start, target)
        if key in self._trace_memo:
            return copy.deepcopy(self._trace_memo[key])
        if key in self._trace_active:
            return None
        if target not in self._match_rule(name, start):
            self._trace_memo[key] = None
            return None
        self._trace_active.add(key)
        try:
            child = self._trace(self.rules[name].expression, start, target)
        finally:
            self._trace_active.remove(key)
        if child is None:
            self._trace_memo[key] = None
            return None
        rule = self.rules[name]
        result = {
            "kind": "rule", "name": name, "rule_kind": rule.kind,
            "returns": rule.returns, "span": dict(child["span"]), "child": child,
        }
        self._trace_memo[key] = result
        return copy.deepcopy(result)

    @staticmethod
    def _cap_count(value: int) -> int:
        return min(value, 2)

    def _count_rule(self, name: str, offset: int, target: int) -> int:
        start = self._skip_hidden(offset)
        key = (name, start, target)
        if key in self._count_rule_memo:
            return self._count_rule_memo[key]
        if key in self._count_rule_active or target not in self._match_rule(name, start):
            return 0
        self._count_rule_active.add(key)
        try:
            result = self._count(self.rules[name].expression, start, target)
        finally:
            self._count_rule_active.remove(key)
        self._count_rule_memo[key] = result
        return result

    def _count(self, node: dict, offset: int, target: int) -> int:
        """同じIR node/spanの有限derivation数を0/1/2以上へ飽和して数える。"""
        key = (id(node), offset, target)
        if key in self._count_memo:
            return self._count_memo[key]
        kind = node["kind"]
        if kind in {"epsilon", "tree_action"}:
            result = int(offset == target)
        elif kind == "literal":
            result = int(target in self._match_literal(node["value"], offset))
        elif kind == "enum_literal":
            result = int(target in self._match_literal(node["name"], offset))
        elif kind == "terminal_ref":
            result = int(target in self._match_terminal(node["name"], offset))
        elif kind == "rule_ref":
            result = self._count_rule(node["name"], offset, target)
        elif kind == "cross_reference":
            terminal = node["terminal"] or "ID"
            result = self._count_rule(terminal, offset, target) if terminal in self.rules \
                else int(target in self._match_terminal(terminal, offset))
        elif kind == "assignment":
            result = self._count(node["child"], offset, target)
        elif kind == "choice":
            result = 0
            for child in node["children"]:
                result = self._cap_count(result + self._count(child, offset, target))
                if result == 2:
                    break
        elif kind == "sequence":
            children = node["children"]
            memo: dict[tuple[int, int], int] = {}

            def sequence(index: int, position: int) -> int:
                seq_key = (index, position)
                if seq_key in memo:
                    return memo[seq_key]
                if index == len(children):
                    return int(position == target)
                total = 0
                child = children[index]
                for end in self._match(child, position):
                    if end > target:
                        continue
                    total = self._cap_count(
                        total + self._count(child, position, end) * sequence(index + 1, end))
                    if total == 2:
                        break
                memo[seq_key] = total
                return total

            result = sequence(0, offset)
        elif kind == "repeat":
            child = node["child"]
            minimum, maximum = node["min"], node["max"]
            limit = maximum if maximum is not None else len(self.text) + 1
            memo: dict[tuple[int, int], int] = {}

            def repeat(position: int, count: int) -> int:
                repeat_key = (position, count)
                if repeat_key in memo:
                    return memo[repeat_key]
                total = int(count >= minimum and position == target)
                if count < limit:
                    for end in self._match(child, position):
                        if end == position or end > target:
                            continue
                        total = self._cap_count(
                            total + self._count(child, position, end) * repeat(end, count + 1))
                        if total == 2:
                            break
                memo[repeat_key] = total
                return total

            result = repeat(offset, 0)
        else:
            raise GrammarCompileError(f"unsupported IR node in derivation count: {kind}")
        result = self._cap_count(result)
        self._count_memo[key] = result
        return result

    def _trace_sequence(self, children: list[dict], index: int, offset: int,
                        target: int) -> list[dict] | None:
        if index == len(children):
            return [] if offset == target else None
        child = children[index]
        for end in sorted(self._match(child, offset), reverse=True):
            if end > target:
                continue
            tail = self._trace_sequence(children, index + 1, end, target)
            if tail is None:
                continue
            traced = self._trace(child, offset, end)
            if traced is not None:
                return [traced, *tail]
        return None

    def _trace_repeat(self, child: dict, offset: int, target: int,
                      minimum: int, maximum: int | None) -> list[dict] | None:
        limit = maximum if maximum is not None else len(self.text) + 1

        def visit(position: int, count: int) -> list[dict] | None:
            if count < limit:
                for end in sorted(self._match(child, position), reverse=True):
                    if end == position or end > target:
                        continue
                    tail = visit(end, count + 1)
                    if tail is None:
                        continue
                    traced = self._trace(child, position, end)
                    if traced is not None:
                        return [traced, *tail]
            if count >= minimum and position == target:
                return []
            return None

        return visit(offset, 0)

    def _trace(self, node: dict, offset: int, target: int) -> dict | None:
        kind = node["kind"]
        start = self._skip_hidden(offset) \
            if kind in {"literal", "enum_literal", "terminal_ref", "cross_reference",
                        "rule_ref"} else offset
        span = self._span(start, target)
        if kind == "epsilon":
            return {"kind": "epsilon", "span": span} if target == offset else None
        if kind == "tree_action":
            if target != offset:
                return None
            return {"kind": "tree_action", "type": node["type"], "feature": node["feature"],
                    "value": node["value"], "span": span}
        if kind == "literal":
            if target not in self._match_literal(node["value"], offset):
                return None
            return {"kind": "literal", "value": node["value"],
                    "surface": self.text[start:target], "span": span}
        if kind == "enum_literal":
            if target not in self._match_literal(node["name"], offset):
                return None
            return {"kind": "enum_literal", "name": node["name"],
                    "surface": self.text[start:target], "span": span}
        if kind == "terminal_ref":
            if target not in self._match_terminal(node["name"], offset):
                return None
            return {"kind": "terminal", "name": node["name"],
                    "surface": self.text[start:target], "span": span}
        if kind == "cross_reference":
            terminal = node["terminal"] or "ID"
            if terminal in self.rules:
                child = self._trace_rule(terminal, offset, target)
            else:
                child = None
                if target not in self._match_terminal(terminal, offset):
                    return None
            return {
                "kind": "cross_reference", "target": node["target"], "terminal": terminal,
                "surface": self.text[start:target], "span": span, "terminal_rule": child,
                "linking_checked": False,
            }
        if kind == "rule_ref":
            return self._trace_rule(node["name"], offset, target)
        if kind == "assignment":
            child = self._trace(node["child"], offset, target)
            if child is None:
                return None
            return {"kind": "assignment", "feature": node["feature"],
                    "operator": node["operator"], "span": dict(child["span"]),
                    "child": child}
        if kind == "choice":
            for index, child_node in enumerate(node["children"]):
                if target not in self._match(child_node, offset):
                    continue
                child = self._trace(child_node, offset, target)
                if child is not None:
                    return {"kind": "choice", "selected_index": index,
                            "alternative_count": len(node["children"]),
                            "span": dict(child["span"]), "child": child}
            return None
        if kind == "sequence":
            children = self._trace_sequence(node["children"], 0, offset, target)
            return None if children is None else {
                "kind": "sequence", "span": self._cover_span(children, offset, target),
                "children": children}
        if kind == "repeat":
            children = self._trace_repeat(node["child"], offset, target,
                                          node["min"], node["max"])
            return None if children is None else {
                "kind": "repeat", "min": node["min"], "max": node["max"],
                "count": len(children), "span": self._cover_span(children, offset, target),
                "children": children,
            }
        raise GrammarCompileError(f"unsupported IR node in syntax trace: {kind}")

    def _match(self, node: dict, offset: int) -> frozenset[int]:
        kind = node["kind"]
        if kind == "epsilon" or kind == "tree_action":
            return frozenset({offset})
        if kind == "literal":
            return self._match_literal(node["value"], offset)
        if kind == "enum_literal":
            return self._match_literal(node["name"], offset)
        if kind == "terminal_ref":
            return self._match_terminal(node["name"], offset)
        if kind == "rule_ref":
            return self._match_rule(node["name"], offset)
        if kind == "cross_reference":
            terminal = node["terminal"] or "ID"
            return self._match_rule(terminal, offset) if terminal in self.rules \
                else self._match_terminal(terminal, offset)
        if kind == "assignment":
            return self._match(node["child"], offset)
        if kind == "choice":
            return frozenset().union(*(self._match(child, offset)
                                       for child in node["children"]))
        if kind == "sequence":
            positions = frozenset({offset})
            for child in node["children"]:
                positions = frozenset().union(*(self._match(child, item)
                                                for item in positions))
                if not positions:
                    break
            return positions
        if kind == "repeat":
            positions = frozenset({offset})
            accepted = frozenset({offset}) if node["min"] == 0 else frozenset()
            count = 0
            while positions and (node["max"] is None or count < node["max"]):
                # 各開始位置ごとにzero-width結果だけを除く。別pathの開始位置と同じoffsetへ
                # 到達する正当な結果まで全体集合比較で落としてはならない。
                advanced = frozenset(
                    end for item in positions for end in self._match(node["child"], item)
                    if end != item)
                count += 1
                positions = advanced
                if count >= node["min"]:
                    accepted = accepted | positions
                if not advanced:
                    break
            return accepted
        raise GrammarCompileError(f"unsupported IR node at runtime: {kind}")
