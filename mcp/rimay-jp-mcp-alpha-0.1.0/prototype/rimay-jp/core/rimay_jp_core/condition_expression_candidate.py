"""B5 Condition Combinationの隔離Canonical 0.7.0 candidate bundle。

active Canonical 0.6.0や通常parser/serializerへ接続せず、Repositoryが保証する
condition leaf／AND／OR優先順位木だけを採用前に検証する。固定Repository Grammarの
``group`` はItemizedConditionsのcontainerなので、本candidateの論理式へは投影しない。
"""
from __future__ import annotations

import copy
import hashlib
import json
from dataclasses import dataclass
from typing import Callable, Iterable


CONDITION_EXPRESSION_CANDIDATE_VERSION = "0.7.0"
ACTIVE_CANONICAL_VERSION = "0.6.0"
_RULE_IDS = {
    "condition": "ConditionsPrimaryExpression",
    "and": "ConditionsAndExpression",
    "or": "ConditionsOrExpression",
}
_LEAF_TRACE_KEYS = frozenset({
    "repository_rule_id", "selected_condition_rule_id", "source_span", "source",
    "condition_index",
})
_OPERATOR_TRACE_KEYS = frozenset({
    "repository_rule_id", "source_span", "source",
})
_QUARANTINE_KIND = "RIMAY_JP_CONDITION_EXPRESSION_QUARANTINE"


def _value_sha256(value: object) -> str:
    payload = json.dumps(
        value, ensure_ascii=False, sort_keys=True, separators=(",", ":")
    ).encode("utf-8")
    return "sha256:" + hashlib.sha256(payload).hexdigest()


@dataclass(frozen=True)
class ConditionExpressionError(ValueError):
    code: str
    path: str
    message: str

    def __str__(self) -> str:
        return f"{self.code} at {self.path}: {self.message}"

    def finding(self) -> dict:
        return {
            "code": self.code,
            "severity": "blocking",
            "path": self.path,
            "message": self.message,
        }


def _span(value: object, path: str) -> dict:
    if not isinstance(value, dict) or set(value) != {"start", "end"} or \
            type(value.get("start")) is not int or type(value.get("end")) is not int or \
            value["start"] < 0 or value["end"] < value["start"]:
        raise ConditionExpressionError(
            "CONDITION_EXPRESSION_INVALID_SPAN", path,
            "span must be ordered non-negative integers")
    return {"start": value["start"], "end": value["end"]}


def _source_record(node: dict, source_text: str, path: str) -> tuple[dict, str]:
    span = _span(node.get("span"), path + "/span")
    source = node.get("source")
    if not isinstance(source, str):
        raise ConditionExpressionError(
            "CONDITION_EXPRESSION_INVALID_SOURCE", path + "/source",
            "source must be a string")
    if span["end"] > len(source_text) or source_text[span["start"]:span["end"]] != source:
        raise ConditionExpressionError(
            "CONDITION_EXPRESSION_SOURCE_TAMPERED", path,
            "source is not the exact fragment selected by span")
    return span, source


def _trace(node: dict, kind: str, source_text: str, *, condition_index: int | None = None,
           selected_condition_rule_id: str | None = None, path: str) -> dict:
    span, source = _source_record(node, source_text, path)
    trace = {
        "repository_rule_id": _RULE_IDS[kind],
        "source_span": span,
        "source": source,
    }
    if kind == "condition":
        trace["selected_condition_rule_id"] = selected_condition_rule_id
        trace["condition_index"] = condition_index
    return trace


def project_repository_condition_expression(
    repository_expression: dict,
    source_text: str,
    project_condition: Callable[[int, dict], dict],
) -> dict:
    """Repository documentの非itemized condition式木をCanonical候補へ投影する。

    Condition leafの製品意味はcallbackへ委譲し、本境界はAND/OR木、順序、rule、span、
    sourceだけを所有する。Repository documentは事前に同じ``source_text``で検査済みとするが、
    この投影境界でも使用する全nodeを独立に再検査する。
    """
    next_index = 0

    def visit(node: object, path: str) -> dict:
        nonlocal next_index
        if not isinstance(node, dict):
            raise ConditionExpressionError(
                "CONDITION_EXPRESSION_INVALID_NODE", path, "node must be an object")
        kind = node.get("kind")
        if kind == "group":
            raise ConditionExpressionError(
                "CONDITION_EXPRESSION_ITEMIZED_UNSUPPORTED", path,
                "Repository group contains ItemizedConditions and is outside this candidate")
        if kind == "condition":
            if set(node) != {"kind", "span", "source", "rule"}:
                raise ConditionExpressionError(
                    "CONDITION_EXPRESSION_INVALID_NODE", path,
                    "condition leaf shape is closed")
            rule = node.get("rule")
            if not isinstance(rule, dict) or set(rule) != {
                    "rule_id", "span", "source", "assignments"}:
                raise ConditionExpressionError(
                    "CONDITION_EXPRESSION_INVALID_LEAF_RULE", path + "/rule",
                    "selected condition rule shape is closed")
            rule_id = rule.get("rule_id")
            if not isinstance(rule_id, str) or not rule_id:
                raise ConditionExpressionError(
                    "CONDITION_EXPRESSION_INVALID_LEAF_RULE", path + "/rule/rule_id",
                    "selected condition rule id is required")
            leaf_span, _ = _source_record(node, source_text, path)
            rule_span, _ = _source_record(rule, source_text, path + "/rule")
            if not (leaf_span["start"] <= rule_span["start"] <=
                    rule_span["end"] <= leaf_span["end"]):
                raise ConditionExpressionError(
                    "CONDITION_EXPRESSION_TRACE_OUTSIDE_PARENT", path + "/rule/span",
                    "selected condition rule is outside its leaf")
            condition_index = next_index
            next_index += 1
            condition = project_condition(condition_index, copy.deepcopy(node))
            if not isinstance(condition, dict):
                raise ConditionExpressionError(
                    "CONDITION_EXPRESSION_INVALID_LEAF", path,
                    "condition projector must return a Canonical condition object")
            return {
                "kind": "condition",
                "condition": copy.deepcopy(condition),
                "repository_trace": _trace(
                    node, kind, source_text, condition_index=condition_index,
                    selected_condition_rule_id=rule_id, path=path),
            }
        if kind in {"and", "or"}:
            if set(node) != {"kind", "span", "source", "operator", "left", "right"}:
                raise ConditionExpressionError(
                    "CONDITION_EXPRESSION_INVALID_NODE", path,
                    "binary expression shape is closed")
            operator = node.get("operator")
            if not isinstance(operator, dict) or set(operator) != {
                    "kind", "span", "source"} or operator.get("kind") != kind:
                raise ConditionExpressionError(
                    "CONDITION_EXPRESSION_OPERATOR_MISMATCH", path + "/operator",
                    f"operator must be a closed {kind!r} record")
            parent_span, _ = _source_record(node, source_text, path)
            operator_span, _ = _source_record(operator, source_text, path + "/operator")
            if not (parent_span["start"] <= operator_span["start"] <=
                    operator_span["end"] <= parent_span["end"]):
                raise ConditionExpressionError(
                    "CONDITION_EXPRESSION_TRACE_OUTSIDE_PARENT", path + "/operator/span",
                    "operator is outside its expression")
            left = visit(node.get("left"), path + "/left")
            right = visit(node.get("right"), path + "/right")
            left_span = left["repository_trace"]["source_span"]
            right_span = right["repository_trace"]["source_span"]
            if not (parent_span["start"] <= left_span["start"] <= left_span["end"] <=
                    operator_span["start"] <= operator_span["end"] <=
                    right_span["start"] <= right_span["end"] <= parent_span["end"]):
                raise ConditionExpressionError(
                    "CONDITION_EXPRESSION_OPERATOR_ORDER", path,
                    "left, operator, and right spans are not ordered")
            return {
                "kind": kind,
                "left": left,
                "right": right,
                "repository_trace": _trace(node, kind, source_text, path=path),
            }
        raise ConditionExpressionError(
            "CONDITION_EXPRESSION_INVALID_NODE", path,
            f"unsupported condition expression kind {kind!r}")

    return visit(repository_expression, "/repository/condition_expression")


def _finding(code: str, path: str, message: str) -> dict:
    return {"code": code, "severity": "blocking", "path": path, "message": message}


def condition_expression_findings(
    expression: object,
    *,
    path: str = "/rimay_core/condition_expression",
    source_text: str | None = None,
) -> tuple[dict, ...]:
    """閉じたshape、trace、leaf index、source/span包含を構造化診断する。"""
    findings: list[dict] = []
    leaf_indexes: list[int] = []

    def visit(node: object, node_path: str, parent_trace: dict | None = None) -> None:
        if not isinstance(node, dict):
            findings.append(_finding(
                "CONDITION_EXPRESSION_INVALID_NODE", node_path,
                "node must be an object"))
            return
        kind = node.get("kind")
        required_by_kind = {
            "condition": {"kind", "condition", "repository_trace"},
            "and": {"kind", "left", "right", "repository_trace"},
            "or": {"kind", "left", "right", "repository_trace"},
        }
        required = required_by_kind.get(kind)
        actual = set(node)
        if required is None or actual not in (required, required - {"repository_trace"}):
            findings.append(_finding(
                "CONDITION_EXPRESSION_INVALID_NODE", node_path,
                f"closed shape mismatch for kind {kind!r}"))
            return

        trace = node.get("repository_trace")
        current_trace: dict | None = None
        if trace is not None:
            expected_keys = _LEAF_TRACE_KEYS if kind == "condition" else \
                _OPERATOR_TRACE_KEYS
            if not isinstance(trace, dict) or set(trace) != expected_keys:
                findings.append(_finding(
                    "CONDITION_EXPRESSION_INVALID_TRACE",
                    node_path + "/repository_trace",
                    "trace shape does not match node kind"))
            else:
                current_trace = trace
                if trace.get("repository_rule_id") != _RULE_IDS[kind]:
                    findings.append(_finding(
                        "CONDITION_EXPRESSION_TRACE_RULE_MISMATCH",
                        node_path + "/repository_trace/repository_rule_id",
                        f"expected {_RULE_IDS[kind]}"))
                try:
                    current_span = _span(
                        trace.get("source_span"),
                        node_path + "/repository_trace/source_span")
                except ConditionExpressionError as exc:
                    findings.append(exc.finding())
                    current_span = None
                source = trace.get("source")
                if not isinstance(source, str):
                    findings.append(_finding(
                        "CONDITION_EXPRESSION_INVALID_SOURCE",
                        node_path + "/repository_trace/source",
                        "source must be a string"))
                elif current_span is not None and source_text is not None and (
                        current_span["end"] > len(source_text) or
                        source_text[current_span["start"]:current_span["end"]] != source):
                    findings.append(_finding(
                        "CONDITION_EXPRESSION_SOURCE_TAMPERED",
                        node_path + "/repository_trace",
                        "source is not the exact fragment selected by span"))
                if parent_trace is not None and current_span is not None:
                    parent_span = parent_trace["source_span"]
                    if not (parent_span["start"] <= current_span["start"] <=
                            current_span["end"] <= parent_span["end"]):
                        findings.append(_finding(
                            "CONDITION_EXPRESSION_TRACE_OUTSIDE_PARENT",
                            node_path + "/repository_trace/source_span",
                            "child span is outside parent span"))
                    elif isinstance(source, str) and isinstance(
                            parent_trace.get("source"), str):
                        offset_start = current_span["start"] - parent_span["start"]
                        offset_end = current_span["end"] - parent_span["start"]
                        if parent_trace["source"][offset_start:offset_end] != source:
                            findings.append(_finding(
                                "CONDITION_EXPRESSION_SOURCE_TAMPERED",
                                node_path + "/repository_trace/source",
                                "child source is inconsistent with parent trace"))
                if kind == "condition":
                    selected = trace.get("selected_condition_rule_id")
                    if not isinstance(selected, str) or not selected:
                        findings.append(_finding(
                            "CONDITION_EXPRESSION_INVALID_LEAF_RULE",
                            node_path + "/repository_trace/selected_condition_rule_id",
                            "selected condition rule id is required"))
                    index = trace.get("condition_index")
                    if type(index) is not int or index < 0:
                        findings.append(_finding(
                            "CONDITION_EXPRESSION_INVALID_LEAF",
                            node_path + "/repository_trace/condition_index",
                            "condition index must be a non-negative integer"))
                    elif index in leaf_indexes:
                        findings.append(_finding(
                            "CONDITION_EXPRESSION_DUPLICATE_LEAF",
                            node_path + "/repository_trace/condition_index",
                            f"condition index {index} is duplicated"))
                    else:
                        leaf_indexes.append(index)

        if kind == "condition":
            if not isinstance(node.get("condition"), dict):
                findings.append(_finding(
                    "CONDITION_EXPRESSION_INVALID_LEAF", node_path + "/condition",
                    "condition must be an object"))
            return
        visit(node.get("left"), node_path + "/left", current_trace)
        visit(node.get("right"), node_path + "/right", current_trace)

    visit(expression, path)
    if leaf_indexes and sorted(leaf_indexes) != list(range(len(leaf_indexes))):
        findings.append(_finding(
            "CONDITION_EXPRESSION_LEAF_COVERAGE", path,
            "Repository condition indexes must cover a contiguous zero-based sequence"))
    return tuple(findings)


def condition_core_findings(core: object) -> tuple[dict, ...]:
    if not isinstance(core, dict):
        return (_finding(
            "CONDITION_EXPRESSION_INVALID_CORE", "/rimay_core",
            "rimay_core must be an object"),)
    if "conditions" in core and "condition_expression" in core:
        return (_finding(
            "CONDITION_EXPRESSION_DUAL_SOURCE", "/rimay_core",
            "conditions and condition_expression are mutually exclusive"),)
    if "condition_expression" not in core:
        return ()
    return condition_expression_findings(core["condition_expression"])


def repository_condition_expression_shape(expression: dict) -> tuple:
    next_index = 0

    def visit(node: dict) -> tuple:
        nonlocal next_index
        kind = node["kind"]
        if kind == "condition":
            index = next_index
            next_index += 1
            return ("condition", index)
        if kind in {"and", "or"}:
            return (kind, visit(node["left"]), visit(node["right"]))
        raise ConditionExpressionError(
            "CONDITION_EXPRESSION_INVALID_NODE", "/condition_expression",
            f"cannot derive Repository shape for {kind!r}")

    return visit(expression)


def canonical_condition_expression_shape(expression: dict) -> tuple:
    next_index = 0

    def visit(node: dict) -> tuple:
        nonlocal next_index
        kind = node["kind"]
        if kind == "condition":
            trace = node.get("repository_trace") or {}
            index = trace.get("condition_index")
            if index is None:
                index = next_index
            next_index += 1
            return ("condition", index)
        if kind in {"and", "or"}:
            return (kind, visit(node["left"]), visit(node["right"]))
        raise ConditionExpressionError(
            "CONDITION_EXPRESSION_INVALID_NODE", "/condition_expression",
            f"cannot derive Canonical shape for {kind!r}")

    return visit(expression)


def canonical_condition_expression_meaning(expression: dict) -> tuple:
    kind = expression["kind"]
    if kind == "condition":
        payload = json.dumps(
            expression["condition"], ensure_ascii=False, sort_keys=True,
            separators=(",", ":"))
        return ("condition", payload)
    if kind in {"and", "or"}:
        return (
            kind,
            canonical_condition_expression_meaning(expression["left"]),
            canonical_condition_expression_meaning(expression["right"]),
        )
    raise ConditionExpressionError(
        "CONDITION_EXPRESSION_INVALID_NODE", "/condition_expression",
        f"cannot derive meaning for {kind!r}")


def render_condition_expression(
    expression: dict,
    render_condition: Callable[[dict], str],
    *,
    language: str,
) -> str:
    connectors = {
        "en": {"and": "and", "or": "or"},
        "ja": {"and": "かつ", "or": "または"},
    }
    if language not in connectors:
        raise ConditionExpressionError(
            "CONDITION_EXPRESSION_LANGUAGE_UNSUPPORTED", "/language",
            f"unsupported language {language!r}")

    def visit(node: dict) -> str:
        kind = node["kind"]
        if kind == "condition":
            rendered = render_condition(node["condition"])
            if not isinstance(rendered, str) or not rendered.strip():
                raise ConditionExpressionError(
                    "CONDITION_EXPRESSION_RENDER_EMPTY", "/condition_expression",
                    "condition renderer returned no text")
            return rendered.strip()
        if kind in {"and", "or"}:
            connector = connectors[language][kind]
            return "(" + visit(node["left"]) + f" {connector} " + \
                visit(node["right"]) + ")"
        raise ConditionExpressionError(
            "CONDITION_EXPRESSION_INVALID_NODE", "/condition_expression",
            f"cannot render {kind!r}")

    return visit(expression)


def parse_rendered_condition_expression(
    text: str,
    parse_condition: Callable[[str, int], tuple[dict, int]],
    *,
    language: str,
) -> dict:
    """完全括弧化したcandidate表層だけをcondition callbackと分離して復元する。"""
    connectors = {
        "en": (("and", "and"), ("or", "or")),
        "ja": (("かつ", "and"), ("または", "or")),
    }
    if language not in connectors:
        raise ConditionExpressionError(
            "CONDITION_EXPRESSION_LANGUAGE_UNSUPPORTED", "/language",
            f"unsupported language {language!r}")

    def skip_space(position: int) -> int:
        while position < len(text) and text[position].isspace():
            position += 1
        return position

    def visit(position: int, path: str) -> tuple[dict, int]:
        position = skip_space(position)
        if position >= len(text):
            raise ConditionExpressionError(
                "CONDITION_EXPRESSION_PARSE_INCOMPLETE", path,
                "unexpected end of input")
        if text[position] != "(":
            condition, end = parse_condition(text, position)
            if not isinstance(condition, dict) or type(end) is not int or end <= position:
                raise ConditionExpressionError(
                    "CONDITION_EXPRESSION_PARSE_LEAF", path,
                    "condition parser did not consume a condition object")
            return {"kind": "condition", "condition": copy.deepcopy(condition)}, end

        left, position = visit(position + 1, path + "/left")
        position = skip_space(position)
        matched: tuple[str, str] | None = None
        for surface, kind in connectors[language]:
            if text.startswith(surface, position):
                before_ok = position == 0 or text[position - 1].isspace()
                after = position + len(surface)
                after_ok = after == len(text) or text[after].isspace()
                if before_ok and after_ok:
                    matched = (surface, kind)
                    position = after
                    break
        if matched is None:
            raise ConditionExpressionError(
                "CONDITION_EXPRESSION_PARSE_CONNECTOR", path,
                "expected an unambiguous condition connector")
        right, position = visit(position, path + "/right")
        position = skip_space(position)
        if position >= len(text) or text[position] != ")":
            raise ConditionExpressionError(
                "CONDITION_EXPRESSION_PARSE_GROUP", path,
                "binary condition expression is missing a closing parenthesis")
        return {"kind": matched[1], "left": left, "right": right}, position + 1

    expression, end = visit(0, "/condition_expression")
    if skip_space(end) != len(text):
        raise ConditionExpressionError(
            "CONDITION_EXPRESSION_PARSE_TRAILING", "/condition_expression",
            "unconsumed surface text remains")
    return expression


def _rebase_pointer(pointer: object, old_prefix: str, new_prefix: str) -> object:
    if not isinstance(pointer, str):
        return pointer
    if pointer == old_prefix:
        return new_prefix
    if pointer.startswith(old_prefix + "/"):
        return new_prefix + pointer[len(old_prefix):]
    return pointer


def _rebase_pointer_metadata(document: dict, old_prefix: str, new_prefix: str) -> None:
    """Rebase every declared Canonical-pointer carrier after a shape migration."""
    resolution = document.get("resolution")
    slots = resolution.get("slots") if isinstance(resolution, dict) else None
    if isinstance(slots, dict):
        rebased: dict = {}
        for pointer, state in slots.items():
            target = _rebase_pointer(pointer, old_prefix, new_prefix)
            if target in rebased:
                raise ConditionExpressionError(
                    "CONDITION_EXPRESSION_POINTER_COLLISION", "/resolution/slots",
                    f"pointer rebase collides at {target!r}")
            rebased[target] = state
        resolution["slots"] = rebased

    for collection_name in ("provenance", "findings"):
        collection = document.get(collection_name)
        if isinstance(collection, list):
            for item in collection:
                if isinstance(item, dict) and "path" in item:
                    item["path"] = _rebase_pointer(
                        item.get("path"), old_prefix, new_prefix)

    approval = document.get("approval")
    approved_slots = approval.get("approved_slots") \
        if isinstance(approval, dict) else None
    if isinstance(approved_slots, list):
        approval["approved_slots"] = [
            _rebase_pointer(pointer, old_prefix, new_prefix)
            for pointer in approved_slots
        ]

    # A validation snapshot hashes the pre-migration object and cannot be carried
    # across a semantic path rewrite. Callers must validate the migrated document.
    document.pop("validation_state", None)


def migrate_requirement_to_condition_expression(document: dict) -> dict:
    migrated = copy.deepcopy(document)
    if migrated.get("schema_version") != ACTIVE_CANONICAL_VERSION:
        raise ConditionExpressionError(
            "CONDITION_EXPRESSION_MIGRATION_VERSION", "/schema_version",
            f"migration input must use Canonical Schema {ACTIVE_CANONICAL_VERSION}")
    core = migrated.get("rimay_core")
    if not isinstance(core, dict):
        raise ConditionExpressionError(
            "CONDITION_EXPRESSION_INVALID_CORE", "/rimay_core",
            "rimay_core must be an object")
    if "condition_expression" in core:
        raise ConditionExpressionError(
            "CONDITION_EXPRESSION_DUAL_SOURCE", "/rimay_core/condition_expression",
            "0.6.0 input cannot already contain condition_expression")
    conditions = core.get("conditions")
    if conditions is not None and not isinstance(conditions, list):
        raise ConditionExpressionError(
            "CONDITION_EXPRESSION_INVALID_CONDITIONS", "/rimay_core/conditions",
            "conditions must be an array")
    if isinstance(conditions, list) and len(conditions) > 1:
        raise ConditionExpressionError(
            "CONDITION_EXPRESSION_MIGRATION_AMBIGUOUS", "/rimay_core/conditions",
            "multiple flat conditions have no connector semantics")
    if conditions:
        core.pop("conditions")
        core["condition_expression"] = {
            "kind": "condition", "condition": copy.deepcopy(conditions[0])}
        _rebase_pointer_metadata(
            migrated,
            "/rimay_core/conditions/0",
            "/rimay_core/condition_expression/condition",
        )
    migrated["schema_version"] = CONDITION_EXPRESSION_CANDIDATE_VERSION
    return migrated


def rollback_requirement_from_condition_expression(document: dict) -> dict:
    rolled_back = copy.deepcopy(document)
    if rolled_back.get("schema_version") != CONDITION_EXPRESSION_CANDIDATE_VERSION:
        raise ConditionExpressionError(
            "CONDITION_EXPRESSION_ROLLBACK_VERSION", "/schema_version",
            f"rollback input must use {CONDITION_EXPRESSION_CANDIDATE_VERSION}")
    core = rolled_back.get("rimay_core")
    if not isinstance(core, dict):
        raise ConditionExpressionError(
            "CONDITION_EXPRESSION_INVALID_CORE", "/rimay_core",
            "rimay_core must be an object")
    if "conditions" in core and "condition_expression" in core:
        raise ConditionExpressionError(
            "CONDITION_EXPRESSION_DUAL_SOURCE", "/rimay_core",
            "conditions and condition_expression are mutually exclusive")
    expression = core.pop("condition_expression", None)
    if expression is not None:
        findings = condition_expression_findings(expression)
        if findings:
            first = findings[0]
            raise ConditionExpressionError(first["code"], first["path"], first["message"])
        if not isinstance(expression, dict) or expression.get("kind") != "condition":
            raise ConditionExpressionError(
                "CONDITION_EXPRESSION_ROLLBACK_LOSSY",
                "/rimay_core/condition_expression",
                "a composite condition expression cannot be represented by Schema 0.6.0")
        core["conditions"] = [copy.deepcopy(expression["condition"])]
        _rebase_pointer_metadata(
            rolled_back,
            "/rimay_core/condition_expression/condition",
            "/rimay_core/conditions/0",
        )
    rolled_back["schema_version"] = ACTIVE_CANONICAL_VERSION
    return rolled_back


def quarantine_composite_condition_expression_for_rollback(document: dict) -> dict:
    """0.6.0で表現不能な複合式をextensionsへ無損失隔離する。"""
    quarantined = copy.deepcopy(document)
    if quarantined.get("schema_version") != CONDITION_EXPRESSION_CANDIDATE_VERSION:
        raise ConditionExpressionError(
            "CONDITION_EXPRESSION_ROLLBACK_VERSION", "/schema_version",
            f"quarantine input must use {CONDITION_EXPRESSION_CANDIDATE_VERSION}")
    core = quarantined.get("rimay_core")
    if not isinstance(core, dict):
        raise ConditionExpressionError(
            "CONDITION_EXPRESSION_INVALID_CORE", "/rimay_core",
            "rimay_core must be an object")
    if "conditions" in core and "condition_expression" in core:
        raise ConditionExpressionError(
            "CONDITION_EXPRESSION_DUAL_SOURCE", "/rimay_core",
            "conditions and condition_expression are mutually exclusive")
    expression = core.pop("condition_expression", None)
    if not isinstance(expression, dict) or expression.get("kind") == "condition":
        raise ConditionExpressionError(
            "CONDITION_EXPRESSION_QUARANTINE_SCOPE",
            "/rimay_core/condition_expression",
            "only composite condition expressions require quarantine rollback")
    findings = condition_expression_findings(expression)
    if findings:
        first = findings[0]
        raise ConditionExpressionError(first["code"], first["path"], first["message"])
    extensions = quarantined.setdefault("extensions", {})
    if not isinstance(extensions, dict):
        raise ConditionExpressionError(
            "CONDITION_EXPRESSION_QUARANTINE_CONFLICT", "/extensions",
            "extensions must be an object")
    semantics = extensions.setdefault("additional_semantics", [])
    if not isinstance(semantics, list) or any(
            isinstance(item, dict) and item.get("kind") == _QUARANTINE_KIND
            for item in semantics):
        raise ConditionExpressionError(
            "CONDITION_EXPRESSION_QUARANTINE_CONFLICT",
            "/extensions/additional_semantics",
            "a quarantine record already exists or the extension is not a list")
    semantics.append({
        "kind": _QUARANTINE_KIND,
        "source_schema_version": CONDITION_EXPRESSION_CANDIDATE_VERSION,
        "condition_expression": expression,
        "condition_expression_sha256": _value_sha256(expression),
    })
    quarantined["schema_version"] = ACTIVE_CANONICAL_VERSION
    return quarantined


def restore_quarantined_condition_expression(document: dict) -> dict:
    restored = copy.deepcopy(document)
    if restored.get("schema_version") != ACTIVE_CANONICAL_VERSION:
        raise ConditionExpressionError(
            "CONDITION_EXPRESSION_MIGRATION_VERSION", "/schema_version",
            f"restore input must use Canonical Schema {ACTIVE_CANONICAL_VERSION}")
    core = restored.get("rimay_core")
    extensions = restored.get("extensions")
    semantics = extensions.get("additional_semantics") if isinstance(extensions, dict) \
        else None
    if not isinstance(core, dict) or not isinstance(semantics, list):
        raise ConditionExpressionError(
            "CONDITION_EXPRESSION_QUARANTINE_MISSING",
            "/extensions/additional_semantics", "quarantine record is absent")
    records = [item for item in semantics
               if isinstance(item, dict) and item.get("kind") == _QUARANTINE_KIND]
    if len(records) != 1:
        raise ConditionExpressionError(
            "CONDITION_EXPRESSION_QUARANTINE_MISSING",
            "/extensions/additional_semantics",
            "exactly one quarantine record is required")
    if "conditions" in core or "condition_expression" in core:
        raise ConditionExpressionError(
            "CONDITION_EXPRESSION_DUAL_SOURCE", "/rimay_core",
            "quarantine restore cannot overwrite a condition source")
    record = records[0]
    expected_keys = {
        "kind", "source_schema_version", "condition_expression",
        "condition_expression_sha256",
    }
    expression = record.get("condition_expression")
    if set(record) != expected_keys or \
            record.get("source_schema_version") != \
            CONDITION_EXPRESSION_CANDIDATE_VERSION or \
            not isinstance(expression, dict) or \
            record.get("condition_expression_sha256") != _value_sha256(expression) or \
            condition_expression_findings(expression):
        raise ConditionExpressionError(
            "CONDITION_EXPRESSION_QUARANTINE_INVALID",
            "/extensions/additional_semantics",
            "quarantine payload shape, hash, or expression is invalid")
    core["condition_expression"] = expression
    semantics.remove(record)
    if not semantics:
        extensions.pop("additional_semantics")
    restored["schema_version"] = CONDITION_EXPRESSION_CANDIDATE_VERSION
    return restored


def replay_condition_expression_migration(documents: Iterable[dict]) -> dict:
    migrated = [migrate_requirement_to_condition_expression(item) for item in documents]
    payload = json.dumps(
        migrated, ensure_ascii=False, sort_keys=True, separators=(",", ":")
    ).encode("utf-8")
    return {
        "documents": migrated,
        "document_count": len(migrated),
        "replay_sha256": "sha256:" + hashlib.sha256(payload).hexdigest(),
    }


def build_condition_expression_candidate_schema(base_schema: dict) -> dict:
    schema = copy.deepcopy(base_schema)
    schema["properties"]["schema_version"]["const"] = \
        CONDITION_EXPRESSION_CANDIDATE_VERSION
    schema["description"] = (
        base_schema.get("description", "") +
        " B5 CAP-CONDITION-COMBINATION candidate: condition_expressionは採用前隔離検証。"
    )
    schema["$defs"]["repositoryConditionLeafTrace"] = {
        "type": "object",
        "required": sorted(_LEAF_TRACE_KEYS),
        "additionalProperties": False,
        "properties": {
            "repository_rule_id": {"const": _RULE_IDS["condition"]},
            "selected_condition_rule_id": {"type": "string", "minLength": 1},
            "source_span": {"$ref": "#/$defs/span"},
            "source": {"type": "string"},
            "condition_index": {"type": "integer", "minimum": 0},
        },
    }
    schema["$defs"]["repositoryConditionOperatorTrace"] = {
        "type": "object",
        "required": sorted(_OPERATOR_TRACE_KEYS),
        "additionalProperties": False,
        "properties": {
            "repository_rule_id": {
                "enum": [_RULE_IDS["and"], _RULE_IDS["or"]]},
            "source_span": {"$ref": "#/$defs/span"},
            "source": {"type": "string"},
        },
    }
    schema["$defs"]["conditionExpression"] = {
        "oneOf": [
            {"$ref": "#/$defs/conditionExpressionLeaf"},
            {"$ref": "#/$defs/conditionExpressionAnd"},
            {"$ref": "#/$defs/conditionExpressionOr"},
        ]
    }
    schema["$defs"]["conditionExpressionLeaf"] = {
        "type": "object",
        "required": ["kind", "condition"],
        "additionalProperties": False,
        "properties": {
            "kind": {"const": "condition"},
            "condition": {"$ref": "#/$defs/condition"},
            "repository_trace": {"$ref": "#/$defs/repositoryConditionLeafTrace"},
        },
    }
    for kind, suffix in (("and", "And"), ("or", "Or")):
        schema["$defs"]["conditionExpression" + suffix] = {
            "type": "object",
            "required": ["kind", "left", "right"],
            "additionalProperties": False,
            "properties": {
                "kind": {"const": kind},
                "left": {"$ref": "#/$defs/conditionExpression"},
                "right": {"$ref": "#/$defs/conditionExpression"},
                "repository_trace": {
                    "$ref": "#/$defs/repositoryConditionOperatorTrace"},
            },
        }
    core = schema["$defs"]["rimayCore"]
    core["properties"]["condition_expression"] = {
        "$ref": "#/$defs/conditionExpression"}
    core.setdefault("allOf", []).append({
        "not": {"required": ["conditions", "condition_expression"]}})
    return schema
