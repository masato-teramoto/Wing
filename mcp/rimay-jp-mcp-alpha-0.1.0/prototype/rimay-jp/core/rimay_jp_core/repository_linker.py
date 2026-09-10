"""固定Repository Grammar構文木の文書内cross-reference linker。

宣言規則とtarget互換集合はGrammar IRから導出する。論文corpus、Capability台帳、外部辞書、
名称推測は入力にしない。Xtext scope providerそのものではなく、固定Grammarが表現する文書内
宣言だけを解決するfail-closed linkerである。
"""
from __future__ import annotations

import hashlib
from dataclasses import dataclass

from .repository_grammar import (
    GrammarIR, SyntaxParseResult, syntax_tree_problems, syntax_tree_signature,
)


LINK_STATUSES = frozenset({
    "resolved", "unresolved", "ambiguous", "type_mismatch", "unsupported_target_type",
})
LINK_PROBLEM_CODES = frozenset({
    "LINK_INPUT_MISMATCH", "DUPLICATE_DECLARATION", "UNRESOLVED_REFERENCE",
    "AMBIGUOUS_REFERENCE", "REFERENCE_TYPE_MISMATCH", "UNSUPPORTED_TARGET_TYPE",
})


@dataclass(frozen=True)
class SemanticLinkResult:
    checked: bool
    succeeded: bool
    start_rule: str
    grammar_ir_signature: str
    grammar_source_sha256: str
    syntax_tree_sha256: str
    source_sha256: str
    symbols: tuple[dict, ...]
    references: tuple[dict, ...]
    problems: tuple[dict, ...]


def _source_sha256(text: str) -> str:
    return "sha256:" + hashlib.sha256(text.encode("utf-8")).hexdigest()


def _walk_ir(node: dict):
    yield node
    for child in node.get("children", []):
        yield from _walk_ir(child)
    if isinstance(node.get("child"), dict):
        yield from _walk_ir(node["child"])


def _has_local_name_assignment(expression: dict) -> bool:
    return any(node.get("kind") == "assignment" and node.get("feature") == "name"
               for node in _walk_ir(expression))


def _delegated_declaration_rules(grammar: GrammarIR, target: str) -> tuple[str, ...] | None:
    """cross-reference targetが受理する具象宣言規則をGrammarだけから導出する。"""
    if target not in grammar.by_name:
        return None
    active: set[str] = set()

    def resolve(name: str) -> set[str] | None:
        if name in active:
            return None
        rule = grammar.by_name.get(name)
        if rule is None:
            return None
        if _has_local_name_assignment(rule.expression):
            return {name}
        active.add(name)
        try:
            refs: list[str] = []

            def delegated(node: dict) -> bool:
                kind = node["kind"]
                if kind == "rule_ref":
                    refs.append(node["name"])
                    return True
                # A choice delegates the target type to one alternative. A
                # multi-element sequence composes values and must not be
                # reinterpreted as a union of declaration types.
                if kind == "choice":
                    return bool(node["children"]) and all(delegated(child)
                                                          for child in node["children"])
                if kind == "sequence" and len(node["children"]) == 1:
                    return delegated(node["children"][0])
                if kind == "epsilon":
                    return True
                return False

            if not delegated(rule.expression) or not refs:
                return None
            result: set[str] = set()
            for ref in refs:
                resolved = resolve(ref)
                if resolved is None:
                    return None
                result.update(resolved)
            return result
        finally:
            active.remove(name)

    result = resolve(target)
    return tuple(sorted(result)) if result else None


def grammar_linking_inventory(grammar: GrammarIR) -> dict:
    occurrences: dict[str, int] = {}
    terminal_occurrences: dict[str, dict[str | None, int]] = {}
    for rule in grammar.rules:
        for node in _walk_ir(rule.expression):
            if node["kind"] == "cross_reference":
                target = node["target"]
                terminal = node.get("terminal")
                occurrences[target] = occurrences.get(target, 0) + 1
                by_terminal = terminal_occurrences.setdefault(target, {})
                by_terminal[terminal] = by_terminal.get(terminal, 0) + 1
    targets = {}
    for target in sorted(occurrences):
        compatible = _delegated_declaration_rules(grammar, target)
        targets[target] = {
            "occurrences": occurrences[target],
            "terminal_occurrences": [
                {"terminal": terminal, "occurrences": count}
                for terminal, count in sorted(
                    terminal_occurrences[target].items(),
                    key=lambda item: (item[0] is not None, item[0] or ""))
            ],
            "compatible_declaration_rules": list(compatible or ()),
            "supported": compatible is not None,
        }
    return {
        "cross_reference_count": sum(occurrences.values()),
        "targets": targets,
    }


def _children(node: dict):
    child = node.get("child")
    if isinstance(child, dict):
        yield "child", child
    terminal_rule = node.get("terminal_rule")
    if isinstance(terminal_rule, dict):
        yield "terminal_rule", terminal_rule
    for index, item in enumerate(node.get("children", [])):
        yield f"children/{index}", item


def _assignment_surface(rule_node: dict, feature: str, source_text: str) \
        -> tuple[str, dict] | None:
    """当該rule自身のassignmentだけを探し、入れ子ruleのassignmentは横取りしない。"""
    found: list[tuple[str, dict]] = []

    def visit(node: dict, root: bool = False) -> None:
        if node.get("kind") == "rule" and not root:
            return
        if node.get("kind") == "assignment" and node.get("feature") == feature:
            span = node.get("span") or {}
            if type(span.get("start")) is int and type(span.get("end")) is int:
                found.append((source_text[span["start"]:span["end"]], dict(span)))
            return
        for _, child in _children(node):
            visit(child)

    visit(rule_node, root=True)
    return found[0] if len(found) == 1 else None


def _normalize_identifier(surface: str) -> str:
    return ".".join(part[1:] if part.startswith("^") else part
                    for part in surface.split("."))


def _mismatch_result(grammar: GrammarIR, parsed: SyntaxParseResult, source_text: str,
                     messages: list[str]) -> SemanticLinkResult:
    problems = tuple({"code": "LINK_INPUT_MISMATCH", "message": message}
                     for message in messages)
    return SemanticLinkResult(
        checked=False, succeeded=False, start_rule=parsed.start_rule,
        grammar_ir_signature=grammar.signature(),
        grammar_source_sha256=grammar.source_sha256,
        syntax_tree_sha256=syntax_tree_signature(parsed.tree),
        source_sha256=_source_sha256(source_text), symbols=(), references=(),
        problems=problems)


def link_repository_syntax(grammar: GrammarIR, parsed: SyntaxParseResult,
                           source_text: str) -> SemanticLinkResult:
    """文書内宣言へcross-referenceを型付きで解決する。"""
    messages: list[str] = []
    if not parsed.accepted or parsed.tree is None:
        messages.append("syntax parse is not an accepted full match")
    if parsed.grammar_ir_signature != grammar.signature():
        messages.append("parse result grammar IR signature does not match linker grammar")
    grammar_sha = grammar.source_sha256
    if parsed.grammar_source_sha256 != grammar_sha:
        messages.append("parse result grammar source hash does not match linker grammar")
    if parsed.source_sha256 != _source_sha256(source_text):
        messages.append("parse result source hash does not match linker source text")
    tree_problems = syntax_tree_problems(parsed.tree, source_text,
                                         expected_root=parsed.start_rule) \
        if parsed.tree is not None else ()
    messages.extend(f"invalid syntax tree: {problem}" for problem in tree_problems)
    if messages:
        return _mismatch_result(grammar, parsed, source_text, messages)

    cross_targets = sorted(grammar_linking_inventory(grammar)["targets"])
    compatibility = {target: _delegated_declaration_rules(grammar, target)
                     for target in cross_targets}
    declaration_rules = frozenset(
        rule for rules in compatibility.values() if rules for rule in rules)

    raw_symbols: list[dict] = []
    raw_references: list[dict] = []

    def collect(node: dict, path: str, parent_symbol: dict | None = None) -> None:
        next_parent = parent_symbol
        if node.get("kind") == "rule" and node.get("name") in declaration_rules:
            named = _assignment_surface(node, "name", source_text)
            if named is not None:
                surface, span = named
                name = _normalize_identifier(surface)
                qualified = f"{parent_symbol['qualified_name']}.{name}" \
                    if parent_symbol else name
                symbol = {
                    "declaration_rule": node["name"], "name": name,
                    "qualified_name": qualified, "span": span, "tree_path": path,
                }
                raw_symbols.append(symbol)
                next_parent = symbol
        if node.get("kind") == "cross_reference":
            raw_references.append({
                "target": node.get("target"), "terminal": node.get("terminal"),
                "surface": _normalize_identifier(node.get("surface", "")),
                "span": dict(node.get("span") or {}), "tree_path": path,
            })
        for segment, child in _children(node):
            collect(child, f"{path}/{segment}", next_parent)

    collect(parsed.tree, "")
    raw_symbols.sort(key=lambda item: (item["span"]["start"], item["tree_path"]))
    symbols: list[dict] = []
    for index, item in enumerate(raw_symbols, start=1):
        symbols.append({**item, "symbol_id": f"SYM-{index:03d}"})

    problems: list[dict] = []
    duplicate_groups: dict[tuple[str, str], list[dict]] = {}
    for symbol in symbols:
        duplicate_groups.setdefault(
            (symbol["declaration_rule"], symbol["qualified_name"]), []).append(symbol)
    for (rule, name), group in sorted(duplicate_groups.items()):
        if len(group) > 1:
            problems.append({
                "code": "DUPLICATE_DECLARATION",
                "message": f"duplicate {rule} declaration: {name}",
                "symbol_ids": [item["symbol_id"] for item in group],
            })

    references: list[dict] = []
    for raw in sorted(raw_references,
                      key=lambda item: (item["span"].get("start", -1), item["tree_path"])):
        target = raw["target"]
        rules = compatibility.get(target)
        surface = raw["surface"]
        qualified = "." in surface
        same_name = [symbol for symbol in symbols
                     if (symbol["qualified_name"] == surface if qualified
                         else symbol["name"] == surface)]
        compatible = [symbol for symbol in same_name
                      if rules and symbol["declaration_rule"] in rules]
        resolved_ids = [symbol["symbol_id"] for symbol in compatible]
        if rules is None:
            status, code = "unsupported_target_type", "UNSUPPORTED_TARGET_TYPE"
            message = f"cross-reference target type is not derivable from Grammar: {target}"
        elif len(compatible) == 1:
            status, code, message = "resolved", None, "resolved to one compatible declaration"
        elif len(compatible) > 1:
            status, code = "ambiguous", "AMBIGUOUS_REFERENCE"
            message = f"multiple compatible declarations match {surface!r}"
        elif same_name:
            status, code = "type_mismatch", "REFERENCE_TYPE_MISMATCH"
            message = f"declarations named {surface!r} exist but none match target {target}"
        else:
            status, code = "unresolved", "UNRESOLVED_REFERENCE"
            message = f"no declaration matches {surface!r} for target {target}"
        reference = {
            **raw, "status": status,
            "compatible_declaration_rules": list(rules or ()),
            "candidate_symbol_ids": resolved_ids,
            "resolved_symbol_id": resolved_ids[0] if status == "resolved" else None,
        }
        references.append(reference)
        if code:
            problems.append({
                "code": code, "message": message,
                "reference_path": raw["tree_path"],
                "candidate_symbol_ids": resolved_ids,
            })

    return SemanticLinkResult(
        checked=True, succeeded=not problems, start_rule=parsed.start_rule,
        grammar_ir_signature=grammar.signature(), grammar_source_sha256=grammar_sha,
        syntax_tree_sha256=syntax_tree_signature(parsed.tree),
        source_sha256=_source_sha256(source_text), symbols=tuple(symbols),
        references=tuple(references), problems=tuple(problems))
