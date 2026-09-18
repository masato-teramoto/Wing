"""B5-P Response Combinationの隔離candidate bundle。

active Canonical 0.5.0や通常parser/serializerへ接続せず、0.6.0候補のSchema、Repository式木投影、
diagnostic、migration/rollback/Store replay、日本語影響を採用前に検証する。
"""
from __future__ import annotations

import copy
import hashlib
import json
from dataclasses import dataclass
from typing import Callable, Iterable


RESPONSE_EXPRESSION_CANDIDATE_VERSION = "0.6.0"
_TRACE_KEYS = frozenset({"repository_rule_id", "source_span", "source",
                         "atomic_response_index"})
_RULE_IDS = {
    "response": "AtomicSystemResponse",
    "group": "PrimaryExpression_Response",
    "and": "AND_Response",
    "or": "OR_Response",
}
_QUARANTINE_KIND = "RIMAY_JP_RESPONSE_EXPRESSION_QUARANTINE"


def _value_sha256(value: object) -> str:
    payload = json.dumps(
        value, ensure_ascii=False, sort_keys=True, separators=(",", ":")
    ).encode("utf-8")
    return "sha256:" + hashlib.sha256(payload).hexdigest()


@dataclass(frozen=True)
class ResponseExpressionError(ValueError):
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
        raise ResponseExpressionError(
            "RESPONSE_EXPRESSION_INVALID_SPAN", path, "span must be ordered integers")
    return {"start": value["start"], "end": value["end"]}


def _trace(repository_node: dict, kind: str, *, atomic_index: int | None = None) -> dict:
    trace = {
        "repository_rule_id": _RULE_IDS[kind],
        "source_span": _span(repository_node.get("span"), "/repository/span"),
        "source": repository_node.get("source"),
    }
    if not isinstance(trace["source"], str):
        raise ResponseExpressionError(
            "RESPONSE_EXPRESSION_INVALID_SOURCE", "/repository/source",
            "source must be a string")
    if atomic_index is not None:
        trace["atomic_response_index"] = atomic_index
    return trace


def project_repository_response_expression(
    repository_expression: dict,
    project_atomic_response: Callable[[int], dict],
) -> dict:
    """B2のResponse式木だけをCanonical候補へ投影する。

    Atomic Responseの意味は本batchで決めずcallbackへ委譲する。全leaf indexは一度だけ消費する。
    """
    consumed: set[int] = set()

    def visit(node: object, path: str) -> dict:
        if not isinstance(node, dict):
            raise ResponseExpressionError(
                "RESPONSE_EXPRESSION_INVALID_NODE", path, "node must be an object")
        kind = node.get("kind")
        if kind == "atomic":
            expected = {"kind", "span", "source", "atomic_response_index"}
            if set(node) != expected:
                raise ResponseExpressionError(
                    "RESPONSE_EXPRESSION_INVALID_NODE", path, "atomic shape is closed")
            index = node.get("atomic_response_index")
            if type(index) is not int or index < 0:
                raise ResponseExpressionError(
                    "RESPONSE_EXPRESSION_INVALID_LEAF", path,
                    "atomic_response_index must be a non-negative integer")
            if index in consumed:
                raise ResponseExpressionError(
                    "RESPONSE_EXPRESSION_DUPLICATE_LEAF", path,
                    f"atomic response index {index} is consumed more than once")
            response = project_atomic_response(index)
            if not isinstance(response, dict):
                raise ResponseExpressionError(
                    "RESPONSE_EXPRESSION_INVALID_LEAF", path,
                    "atomic projector must return a Canonical response object")
            consumed.add(index)
            return {
                "kind": "response",
                "response": copy.deepcopy(response),
                "repository_trace": _trace(node, "response", atomic_index=index),
            }
        if kind == "group":
            if set(node) != {"kind", "span", "source", "expression"}:
                raise ResponseExpressionError(
                    "RESPONSE_EXPRESSION_INVALID_NODE", path, "group shape is closed")
            return {
                "kind": "group",
                "expression": visit(node.get("expression"), path + "/expression"),
                "repository_trace": _trace(node, "group"),
            }
        if kind in {"and", "or"}:
            if set(node) != {"kind", "span", "source", "operator", "left", "right"}:
                raise ResponseExpressionError(
                    "RESPONSE_EXPRESSION_INVALID_NODE", path, "binary shape is closed")
            operator = node.get("operator")
            if not isinstance(operator, dict) or operator.get("kind") != kind:
                raise ResponseExpressionError(
                    "RESPONSE_EXPRESSION_OPERATOR_MISMATCH", path + "/operator",
                    f"operator must be {kind}")
            return {
                "kind": kind,
                "left": visit(node.get("left"), path + "/left"),
                "right": visit(node.get("right"), path + "/right"),
                "repository_trace": _trace(node, kind),
            }
        raise ResponseExpressionError(
            "RESPONSE_EXPRESSION_INVALID_NODE", path, f"unsupported kind {kind!r}")

    return visit(repository_expression, "/repository/response_expression")


def _finding(code: str, path: str, message: str) -> dict:
    return {"code": code, "severity": "blocking", "path": path, "message": message}


def response_expression_findings(
    expression: object,
    *,
    path: str = "/rimay_core/response_expression",
) -> tuple[dict, ...]:
    """Canonical候補の閉じたshape・trace・leaf一意性を構造化diagnosticで検査する。"""
    findings: list[dict] = []
    leaf_indexes: set[int] = set()

    def visit(node: object, node_path: str, parent_span: dict | None = None) -> None:
        if not isinstance(node, dict):
            findings.append(_finding(
                "RESPONSE_EXPRESSION_INVALID_NODE", node_path, "node must be an object"))
            return
        kind = node.get("kind")
        keys = {
            "response": {"kind", "response", "repository_trace"},
            "group": {"kind", "expression", "repository_trace"},
            "and": {"kind", "left", "right", "repository_trace"},
            "or": {"kind", "left", "right", "repository_trace"},
        }
        required = keys.get(kind)
        actual_keys = set(node)
        if required is None or actual_keys not in (
                required, required - {"repository_trace"}):
            findings.append(_finding(
                "RESPONSE_EXPRESSION_INVALID_NODE", node_path,
                f"closed shape mismatch for kind {kind!r}"))
            return

        trace = node.get("repository_trace")
        current_span: dict | None = None
        if trace is not None:
            allowed = _TRACE_KEYS if kind == "response" else _TRACE_KEYS - {
                "atomic_response_index"}
            required_trace = allowed if kind == "response" else allowed
            if not isinstance(trace, dict) or set(trace) != required_trace:
                findings.append(_finding(
                    "RESPONSE_EXPRESSION_INVALID_TRACE", node_path + "/repository_trace",
                    "trace shape does not match node kind"))
            else:
                expected_rule = _RULE_IDS[kind]
                if trace.get("repository_rule_id") != expected_rule:
                    findings.append(_finding(
                        "RESPONSE_EXPRESSION_TRACE_RULE_MISMATCH",
                        node_path + "/repository_trace/repository_rule_id",
                        f"expected {expected_rule}"))
                try:
                    current_span = _span(
                        trace.get("source_span"), node_path + "/repository_trace/source_span")
                except ResponseExpressionError as exc:
                    findings.append(exc.finding())
                if not isinstance(trace.get("source"), str):
                    findings.append(_finding(
                        "RESPONSE_EXPRESSION_INVALID_SOURCE",
                        node_path + "/repository_trace/source", "source must be a string"))
                if kind == "response":
                    index = trace.get("atomic_response_index")
                    if type(index) is not int or index < 0:
                        findings.append(_finding(
                            "RESPONSE_EXPRESSION_INVALID_LEAF",
                            node_path + "/repository_trace/atomic_response_index",
                            "index must be a non-negative integer"))
                    elif index in leaf_indexes:
                        findings.append(_finding(
                            "RESPONSE_EXPRESSION_DUPLICATE_LEAF",
                            node_path + "/repository_trace/atomic_response_index",
                            f"atomic response index {index} is duplicated"))
                    else:
                        leaf_indexes.add(index)
                if parent_span is not None and current_span is not None and not (
                        parent_span["start"] <= current_span["start"] <=
                        current_span["end"] <= parent_span["end"]):
                    findings.append(_finding(
                        "RESPONSE_EXPRESSION_TRACE_OUTSIDE_PARENT",
                        node_path + "/repository_trace/source_span",
                        "child span is outside parent span"))

        if kind == "response":
            if not isinstance(node.get("response"), dict):
                findings.append(_finding(
                    "RESPONSE_EXPRESSION_INVALID_LEAF", node_path + "/response",
                    "response must be an object"))
            return
        if kind == "group":
            visit(node.get("expression"), node_path + "/expression", current_span)
            return
        visit(node.get("left"), node_path + "/left", current_span)
        visit(node.get("right"), node_path + "/right", current_span)

    visit(expression, path)
    return tuple(findings)


def response_core_findings(core: object) -> tuple[dict, ...]:
    if not isinstance(core, dict):
        return (_finding(
            "RESPONSE_EXPRESSION_INVALID_CORE", "/rimay_core", "rimay_core must be an object"),)
    if core.get("response") is not None and core.get("response_expression") is not None:
        return (_finding(
            "RESPONSE_EXPRESSION_DUAL_SOURCE", "/rimay_core",
            "response and response_expression are mutually exclusive"),)
    if core.get("response_expression") is None:
        return ()
    return response_expression_findings(core["response_expression"])


def _semantic_shape(expression: dict, *, repository: bool) -> tuple:
    kind = expression["kind"]
    if repository and kind == "atomic":
        return ("response", expression["atomic_response_index"])
    if not repository and kind == "response":
        trace = expression.get("repository_trace") or {}
        return ("response", trace.get("atomic_response_index"))
    if kind == "group":
        key = "expression"
        return ("group", _semantic_shape(expression[key], repository=repository))
    if kind in {"and", "or"}:
        return (
            kind,
            _semantic_shape(expression["left"], repository=repository),
            _semantic_shape(expression["right"], repository=repository),
        )
    raise ResponseExpressionError(
        "RESPONSE_EXPRESSION_INVALID_NODE", "/response_expression",
        f"cannot derive semantic shape for {kind!r}")


def repository_response_expression_shape(expression: dict) -> tuple:
    return _semantic_shape(expression, repository=True)


def canonical_response_expression_shape(expression: dict) -> tuple:
    return _semantic_shape(expression, repository=False)


def canonical_response_expression_meaning(expression: dict) -> tuple:
    """traceを除き、式木とCanonical response値だけで意味同値を比較する。"""
    kind = expression["kind"]
    if kind == "response":
        payload = json.dumps(
            expression["response"], ensure_ascii=False, sort_keys=True,
            separators=(",", ":"))
        return ("response", payload)
    if kind == "group":
        return ("group", canonical_response_expression_meaning(expression["expression"]))
    if kind in {"and", "or"}:
        return (
            kind,
            canonical_response_expression_meaning(expression["left"]),
            canonical_response_expression_meaning(expression["right"]),
        )
    raise ResponseExpressionError(
        "RESPONSE_EXPRESSION_INVALID_NODE", "/response_expression",
        f"cannot derive meaning for {kind!r}")


def render_response_expression(
    expression: dict,
    render_response: Callable[[dict], str],
    *,
    language: str,
) -> str:
    connectors = {"en": {"and": "and", "or": "or"},
                  "ja": {"and": "かつ", "or": "または"}}
    if language not in connectors:
        raise ResponseExpressionError(
            "RESPONSE_EXPRESSION_LANGUAGE_UNSUPPORTED", "/language",
            f"unsupported language {language!r}")

    def visit(node: dict) -> str:
        kind = node["kind"]
        if kind == "response":
            rendered = render_response(node["response"])
            if not isinstance(rendered, str) or not rendered.strip():
                raise ResponseExpressionError(
                    "RESPONSE_EXPRESSION_RENDER_EMPTY", "/response_expression",
                    "response renderer returned no text")
            return rendered.strip()
        if kind == "group":
            return "(" + visit(node["expression"]) + ")"
        if kind in {"and", "or"}:
            connector = connectors[language][kind]
            return "(" + visit(node["left"]) + f" {connector} " + \
                visit(node["right"]) + ")"
        raise ResponseExpressionError(
            "RESPONSE_EXPRESSION_INVALID_NODE", "/response_expression",
            f"cannot render {kind!r}")

    return visit(expression)


def parse_rendered_response_expression(
    text: str,
    parse_response: Callable[[str, int], tuple[dict, int]],
    *,
    language: str,
) -> dict:
    """完全括弧化したcandidate表層を、Atomic Response callbackと分離して式木へ戻す。"""
    connectors = {"en": (("and", "and"), ("or", "or")),
                  "ja": (("かつ", "and"), ("または", "or"))}
    if language not in connectors:
        raise ResponseExpressionError(
            "RESPONSE_EXPRESSION_LANGUAGE_UNSUPPORTED", "/language",
            f"unsupported language {language!r}")

    def skip_space(position: int) -> int:
        while position < len(text) and text[position].isspace():
            position += 1
        return position

    def visit(position: int, path: str) -> tuple[dict, int]:
        position = skip_space(position)
        if position >= len(text):
            raise ResponseExpressionError(
                "RESPONSE_EXPRESSION_PARSE_INCOMPLETE", path, "unexpected end of input")
        if text[position] != "(":
            response, end = parse_response(text, position)
            if not isinstance(response, dict) or type(end) is not int or end <= position:
                raise ResponseExpressionError(
                    "RESPONSE_EXPRESSION_PARSE_LEAF", path,
                    "Atomic Response parser did not consume a response object")
            return {"kind": "response", "response": copy.deepcopy(response)}, end

        inner, position = visit(position + 1, path + "/inner")
        position = skip_space(position)
        if position < len(text) and text[position] == ")":
            return {"kind": "group", "expression": inner}, position + 1

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
            raise ResponseExpressionError(
                "RESPONSE_EXPRESSION_PARSE_CONNECTOR", path,
                "expected an unambiguous response connector")
        right, position = visit(position, path + "/right")
        position = skip_space(position)
        if position >= len(text) or text[position] != ")":
            raise ResponseExpressionError(
                "RESPONSE_EXPRESSION_PARSE_GROUP", path,
                "binary response expression is missing a closing parenthesis")
        return {
            "kind": matched[1], "left": inner, "right": right,
        }, position + 1

    expression, end = visit(0, "/response_expression")
    if skip_space(end) != len(text):
        raise ResponseExpressionError(
            "RESPONSE_EXPRESSION_PARSE_TRAILING", "/response_expression",
            "unconsumed surface text remains")
    return expression


def migrate_requirement_to_response_expression(document: dict) -> dict:
    migrated = copy.deepcopy(document)
    if migrated.get("schema_version") != "0.5.0":
        raise ResponseExpressionError(
            "RESPONSE_EXPRESSION_MIGRATION_VERSION", "/schema_version",
            "migration input must use Canonical Schema 0.5.0")
    core = migrated.get("rimay_core")
    if not isinstance(core, dict):
        raise ResponseExpressionError(
            "RESPONSE_EXPRESSION_INVALID_CORE", "/rimay_core",
            "rimay_core must be an object")
    if "response_expression" in core:
        raise ResponseExpressionError(
            "RESPONSE_EXPRESSION_DUAL_SOURCE", "/rimay_core/response_expression",
            "0.5.0 input cannot already contain response_expression")
    response = core.pop("response", None)
    if response is not None:
        core["response_expression"] = {"kind": "response", "response": response}
    migrated["schema_version"] = RESPONSE_EXPRESSION_CANDIDATE_VERSION
    return migrated


def rollback_requirement_from_response_expression(document: dict) -> dict:
    rolled_back = copy.deepcopy(document)
    if rolled_back.get("schema_version") != RESPONSE_EXPRESSION_CANDIDATE_VERSION:
        raise ResponseExpressionError(
            "RESPONSE_EXPRESSION_ROLLBACK_VERSION", "/schema_version",
            f"rollback input must use {RESPONSE_EXPRESSION_CANDIDATE_VERSION}")
    core = rolled_back.get("rimay_core")
    if not isinstance(core, dict):
        raise ResponseExpressionError(
            "RESPONSE_EXPRESSION_INVALID_CORE", "/rimay_core",
            "rimay_core must be an object")
    if core.get("response") is not None and core.get("response_expression") is not None:
        raise ResponseExpressionError(
            "RESPONSE_EXPRESSION_DUAL_SOURCE", "/rimay_core",
            "response and response_expression are mutually exclusive")
    expression = core.pop("response_expression", None)
    if expression is not None:
        findings = response_expression_findings(expression)
        if findings:
            first = findings[0]
            raise ResponseExpressionError(
                first["code"], first["path"], first["message"])
        if not isinstance(expression, dict) or expression.get("kind") != "response":
            raise ResponseExpressionError(
                "RESPONSE_EXPRESSION_ROLLBACK_LOSSY",
                "/rimay_core/response_expression",
                "a composite response expression cannot be represented by Schema 0.5.0")
        core["response"] = expression["response"]
    rolled_back["schema_version"] = "0.5.0"
    return rolled_back


def quarantine_composite_response_expression_for_rollback(document: dict) -> dict:
    """0.5.0で表現不能な複合式をextensionsへ無損失隔離してreader rollbackを可能にする。"""
    quarantined = copy.deepcopy(document)
    if quarantined.get("schema_version") != RESPONSE_EXPRESSION_CANDIDATE_VERSION:
        raise ResponseExpressionError(
            "RESPONSE_EXPRESSION_ROLLBACK_VERSION", "/schema_version",
            f"quarantine input must use {RESPONSE_EXPRESSION_CANDIDATE_VERSION}")
    core = quarantined.get("rimay_core")
    if not isinstance(core, dict):
        raise ResponseExpressionError(
            "RESPONSE_EXPRESSION_INVALID_CORE", "/rimay_core",
            "rimay_core must be an object")
    if core.get("response") is not None and core.get("response_expression") is not None:
        raise ResponseExpressionError(
            "RESPONSE_EXPRESSION_DUAL_SOURCE", "/rimay_core",
            "response and response_expression are mutually exclusive")
    expression = core.pop("response_expression", None)
    if not isinstance(expression, dict) or expression.get("kind") == "response":
        raise ResponseExpressionError(
            "RESPONSE_EXPRESSION_QUARANTINE_SCOPE",
            "/rimay_core/response_expression",
            "only composite response expressions require quarantine rollback")
    findings = response_expression_findings(expression)
    if findings:
        first = findings[0]
        raise ResponseExpressionError(first["code"], first["path"], first["message"])
    extensions = quarantined.setdefault("extensions", {})
    if not isinstance(extensions, dict):
        raise ResponseExpressionError(
            "RESPONSE_EXPRESSION_QUARANTINE_CONFLICT", "/extensions",
            "extensions must be an object")
    semantics = extensions.setdefault("additional_semantics", [])
    if not isinstance(semantics, list) or any(
            isinstance(item, dict) and item.get("kind") == _QUARANTINE_KIND
            for item in semantics):
        raise ResponseExpressionError(
            "RESPONSE_EXPRESSION_QUARANTINE_CONFLICT",
            "/extensions/additional_semantics",
            "a quarantine record already exists or the extension is not a list")
    semantics.append({
        "kind": _QUARANTINE_KIND,
        "source_schema_version": RESPONSE_EXPRESSION_CANDIDATE_VERSION,
        "response_expression": expression,
        "response_expression_sha256": _value_sha256(expression),
    })
    quarantined["schema_version"] = "0.5.0"
    return quarantined


def restore_quarantined_response_expression(document: dict) -> dict:
    restored = copy.deepcopy(document)
    if restored.get("schema_version") != "0.5.0":
        raise ResponseExpressionError(
            "RESPONSE_EXPRESSION_MIGRATION_VERSION", "/schema_version",
            "restore input must use Canonical Schema 0.5.0")
    core = restored.get("rimay_core")
    extensions = restored.get("extensions")
    semantics = extensions.get("additional_semantics") if isinstance(extensions, dict) \
        else None
    if not isinstance(core, dict) or not isinstance(semantics, list):
        raise ResponseExpressionError(
            "RESPONSE_EXPRESSION_QUARANTINE_MISSING",
            "/extensions/additional_semantics", "quarantine record is absent")
    records = [item for item in semantics
               if isinstance(item, dict) and item.get("kind") == _QUARANTINE_KIND]
    if len(records) != 1:
        raise ResponseExpressionError(
            "RESPONSE_EXPRESSION_QUARANTINE_MISSING",
            "/extensions/additional_semantics",
            "exactly one quarantine record is required")
    if core.get("response") is not None or core.get("response_expression") is not None:
        raise ResponseExpressionError(
            "RESPONSE_EXPRESSION_DUAL_SOURCE", "/rimay_core",
            "quarantine restore cannot overwrite a response source")
    record = records[0]
    expected_keys = {
        "kind", "source_schema_version", "response_expression",
        "response_expression_sha256",
    }
    expression = record.get("response_expression")
    if set(record) != expected_keys or \
            record.get("source_schema_version") != RESPONSE_EXPRESSION_CANDIDATE_VERSION or \
            not isinstance(expression, dict) or \
            record.get("response_expression_sha256") != _value_sha256(expression) or \
            response_expression_findings(expression):
        raise ResponseExpressionError(
            "RESPONSE_EXPRESSION_QUARANTINE_INVALID",
            "/extensions/additional_semantics",
            "quarantine payload shape, hash, or expression is invalid")
    core["response_expression"] = expression
    semantics.remove(record)
    if not semantics:
        extensions.pop("additional_semantics")
    restored["schema_version"] = RESPONSE_EXPRESSION_CANDIDATE_VERSION
    return restored


def replay_response_expression_migration(documents: Iterable[dict]) -> dict:
    migrated = [migrate_requirement_to_response_expression(item) for item in documents]
    payload = json.dumps(
        migrated, ensure_ascii=False, sort_keys=True, separators=(",", ":")
    ).encode("utf-8")
    return {
        "documents": migrated,
        "document_count": len(migrated),
        "replay_sha256": "sha256:" + hashlib.sha256(payload).hexdigest(),
    }


def build_response_expression_candidate_schema(base_schema: dict) -> dict:
    schema = copy.deepcopy(base_schema)
    schema["properties"]["schema_version"]["const"] = \
        RESPONSE_EXPRESSION_CANDIDATE_VERSION
    schema["description"] = (
        base_schema.get("description", "") +
        " B5-P CAP-RESPONSE-COMBINATION candidate: response_expressionは採用前隔離検証。"
    )
    trace = {
        "type": "object",
        "required": ["repository_rule_id", "source_span", "source"],
        "additionalProperties": False,
        "properties": {
            "repository_rule_id": {
                "enum": sorted(_RULE_IDS.values()),
            },
            "source_span": {"$ref": "#/$defs/span"},
            "source": {"type": "string"},
            "atomic_response_index": {"type": "integer", "minimum": 0},
        },
    }
    schema["$defs"]["repositoryResponseTrace"] = trace
    schema["$defs"]["responseExpression"] = {
        "oneOf": [
            {"$ref": "#/$defs/responseExpressionLeaf"},
            {"$ref": "#/$defs/responseExpressionGroup"},
            {"$ref": "#/$defs/responseExpressionAnd"},
            {"$ref": "#/$defs/responseExpressionOr"},
        ]
    }
    common_trace = {"$ref": "#/$defs/repositoryResponseTrace"}
    schema["$defs"]["responseExpressionLeaf"] = {
        "type": "object",
        "required": ["kind", "response"],
        "additionalProperties": False,
        "properties": {
            "kind": {"const": "response"},
            "response": {"$ref": "#/$defs/response"},
            "repository_trace": common_trace,
        },
    }
    schema["$defs"]["responseExpressionGroup"] = {
        "type": "object",
        "required": ["kind", "expression"],
        "additionalProperties": False,
        "properties": {
            "kind": {"const": "group"},
            "expression": {"$ref": "#/$defs/responseExpression"},
            "repository_trace": common_trace,
        },
    }
    for kind, suffix in (("and", "And"), ("or", "Or")):
        schema["$defs"]["responseExpression" + suffix] = {
            "type": "object",
            "required": ["kind", "left", "right"],
            "additionalProperties": False,
            "properties": {
                "kind": {"const": kind},
                "left": {"$ref": "#/$defs/responseExpression"},
                "right": {"$ref": "#/$defs/responseExpression"},
                "repository_trace": common_trace,
            },
        }
    core = schema["$defs"]["rimayCore"]
    core["properties"]["response_expression"] = {
        "$ref": "#/$defs/responseExpression"
    }
    core["allOf"] = [{"not": {"required": ["response", "response_expression"]}}]
    return schema
