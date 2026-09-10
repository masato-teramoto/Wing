"""B5-P itemized Response Blockの隔離Canonical 0.8.0 candidate bundle。

Active 0.7.0 runtimeへ接続せず、Repository固有文書が保持するitem、bullet、
connector、``in sequence``、Atomic Response参照を欠落なく検証する。
"""
from __future__ import annotations

import copy
import hashlib
import json
import re
from dataclasses import dataclass
from typing import Callable, Iterable


ACTIVE_CANONICAL_VERSION = "0.7.0"
RESPONSE_BLOCK_CANDIDATE_VERSION = "0.8.0"
_CONNECTORS = frozenset({
    "comma", "and", "or", "comma_and", "comma_or",
})
_CONNECTOR_SOURCE = {
    "comma": ",", "and": "and", "or": "or",
    "comma_and": ",and", "comma_or": ",or",
}
_QUARANTINE_KIND = "RIMAY_JP_RESPONSE_BLOCK_QUARANTINE"
_ASCII_INTEGER_BULLET = re.compile(r"[0-9]+")


@dataclass(frozen=True)
class ResponseBlockError(ValueError):
    code: str
    path: str
    message: str

    def __str__(self) -> str:
        return f"{self.code} at {self.path}: {self.message}"

    def finding(self) -> dict:
        return {
            "code": self.code, "severity": "blocking",
            "path": self.path, "message": self.message,
        }


def _value_sha256(value: object) -> str:
    payload = json.dumps(
        value, ensure_ascii=False, sort_keys=True, separators=(",", ":")
    ).encode("utf-8")
    return "sha256:" + hashlib.sha256(payload).hexdigest()


def _finding(code: str, path: str, message: str) -> dict:
    return {"code": code, "severity": "blocking", "path": path, "message": message}


def _span(value: object, path: str) -> dict:
    if not isinstance(value, dict) or set(value) != {"start", "end"} or \
            type(value.get("start")) is not int or type(value.get("end")) is not int or \
            value["start"] < 0 or value["end"] < value["start"]:
        raise ResponseBlockError(
            "RESPONSE_BLOCK_INVALID_SPAN", path, "span must be ordered integers")
    return {"start": value["start"], "end": value["end"]}


def _source_record(value: object, source_text: str, path: str) -> tuple[dict, str]:
    if not isinstance(value, dict):
        raise ResponseBlockError(
            "RESPONSE_BLOCK_INVALID_REPOSITORY_NODE", path, "node must be an object")
    span = _span(value.get("span"), path + "/span")
    source = value.get("source")
    if not isinstance(source, str):
        raise ResponseBlockError(
            "RESPONSE_BLOCK_INVALID_SOURCE", path + "/source", "source must be a string")
    if span["end"] > len(source_text) or source_text[span["start"]:span["end"]] != source:
        raise ResponseBlockError(
            "RESPONSE_BLOCK_SOURCE_TAMPERED", path + "/source",
            "source does not match the declared source span")
    return span, source


def _nullable_source_record(
    value: object, source_text: str, path: str,
) -> tuple[dict | None, str | None]:
    if value is None:
        return None, None
    return _source_record(value, source_text, path)


def _is_ascii_integer_bullet(value: object) -> bool:
    return isinstance(value, str) and _ASCII_INTEGER_BULLET.fullmatch(value) is not None


def _canonical_source_text(document: object) -> str | None:
    source = document.get("source") if isinstance(document, dict) else None
    text = source.get("text") if isinstance(source, dict) else None
    return text if isinstance(text, str) else None


def _bullet(value: object, path: str) -> dict:
    if not isinstance(value, dict) or set(value) != {"kind", "value", "span", "source"}:
        raise ResponseBlockError(
            "RESPONSE_BLOCK_INVALID_BULLET", path, "bullet shape is closed")
    kind = value.get("kind")
    token = value.get("value")
    if kind == "hyphen" and token != "-":
        raise ResponseBlockError(
            "RESPONSE_BLOCK_BULLET_MISMATCH", path, "hyphen bullet must use '-'")
    if kind == "integer" and not _is_ascii_integer_bullet(token):
        raise ResponseBlockError(
            "RESPONSE_BLOCK_BULLET_MISMATCH", path,
            "integer bullet must use ASCII digits")
    if kind not in {"hyphen", "integer"}:
        raise ResponseBlockError(
            "RESPONSE_BLOCK_INVALID_BULLET", path, f"unsupported bullet kind {kind!r}")
    return {"kind": kind, "value": token}


def project_repository_response_block(
    repository_structure: dict,
    source_text: str,
    project_atomic_response: Callable[[int, dict], dict],
) -> dict:
    """Repository itemized blockだけを0.8 candidateへ投影する。"""
    path = "/repository/response_structure"
    if not isinstance(repository_structure, dict) or \
            repository_structure.get("kind") != "itemized":
        raise ResponseBlockError(
            "RESPONSE_BLOCK_NON_ITEMIZED_OUTSIDE_BATCH", path,
            "only itemized ResponseBlock belongs to this batch")
    if set(repository_structure) != {"kind", "span", "source", "in_sequence", "items"}:
        raise ResponseBlockError(
            "RESPONSE_BLOCK_INVALID_REPOSITORY_NODE", path, "itemized shape is closed")
    block_span, block_source = _source_record(repository_structure, source_text, path)
    sequence_span, sequence_source = _nullable_source_record(
        repository_structure.get("in_sequence"), source_text, path + "/in_sequence")
    if sequence_source is not None and "".join(sequence_source.split()) != "insequence":
        raise ResponseBlockError(
            "RESPONSE_BLOCK_SEQUENCE_TAMPERED", path + "/in_sequence",
            "sequence source must be 'in sequence'")
    items = repository_structure.get("items")
    if not isinstance(items, list) or not items:
        raise ResponseBlockError(
            "RESPONSE_BLOCK_EMPTY", path + "/items", "itemized block must contain items")

    projected: list[dict] = []
    consumed: set[int] = set()
    for position, item in enumerate(items):
        item_path = f"{path}/items/{position}"
        if not isinstance(item, dict) or set(item) != {
                "index", "span", "source", "connector_before", "bullet",
                "atomic_response_index"}:
            raise ResponseBlockError(
                "RESPONSE_BLOCK_INVALID_ITEM", item_path, "item shape is closed")
        if item.get("index") != position:
            raise ResponseBlockError(
                "RESPONSE_BLOCK_POSITION_MISMATCH", item_path + "/index",
                "item indexes must be contiguous and zero-based")
        item_span, item_source = _source_record(item, source_text, item_path)
        bullet_value = _bullet(item.get("bullet"), item_path + "/bullet")
        bullet_span, bullet_source = _source_record(
            item["bullet"], source_text, item_path + "/bullet")
        connector = item.get("connector_before")
        connector_span, connector_source = _nullable_source_record(
            connector, source_text, item_path + "/connector_before")
        connector_kind = connector.get("kind") if isinstance(connector, dict) else None
        if position == 0 and connector is not None:
            raise ResponseBlockError(
                "RESPONSE_BLOCK_FIRST_CONNECTOR", item_path + "/connector_before",
                "the first item cannot have a connector")
        if connector is not None:
            if set(connector) != {"kind", "span", "source"} or \
                    connector_kind not in _CONNECTORS:
                raise ResponseBlockError(
                    "RESPONSE_BLOCK_INVALID_CONNECTOR", item_path + "/connector_before",
                    "connector shape or kind is invalid")
            if "".join((connector_source or "").split()) != \
                    _CONNECTOR_SOURCE[connector_kind]:
                raise ResponseBlockError(
                    "RESPONSE_BLOCK_CONNECTOR_TAMPERED",
                    item_path + "/connector_before/source",
                    "connector source does not match its kind")
        atomic_index = item.get("atomic_response_index")
        if type(atomic_index) is not int or atomic_index < 0:
            raise ResponseBlockError(
                "RESPONSE_BLOCK_INVALID_ATOMIC_INDEX",
                item_path + "/atomic_response_index", "index must be non-negative")
        if atomic_index in consumed:
            raise ResponseBlockError(
                "RESPONSE_BLOCK_DUPLICATE_ATOMIC_INDEX",
                item_path + "/atomic_response_index",
                f"atomic response index {atomic_index} is consumed more than once")
        response = project_atomic_response(atomic_index, item)
        if not isinstance(response, dict):
            raise ResponseBlockError(
                "RESPONSE_BLOCK_INVALID_RESPONSE", item_path,
                "atomic projector must return a Canonical response object")
        consumed.add(atomic_index)
        projected.append({
            "position": position,
            "bullet": bullet_value,
            "connector_before": connector_kind,
            "response": copy.deepcopy(response),
            "repository_trace": {
                "repository_rule_id": "BULLET",
                "source_span": item_span,
                "source": item_source,
                "bullet_span": bullet_span,
                "bullet_source": bullet_source,
                "connector_span": connector_span,
                "connector_source": connector_source,
                "atomic_response_index": atomic_index,
            },
        })
    return {
        "kind": "itemized",
        "in_sequence": sequence_span is not None,
        "items": projected,
        "repository_trace": {
            "repository_rule_id": "ResponseBlockItemized",
            "source_span": block_span,
            "source": block_source,
            "in_sequence_span": sequence_span,
            "in_sequence_source": sequence_source,
        },
    }


def response_block_findings(
    block: object,
    *,
    source_text: str | None = None,
    path: str = "/rimay_core/response_block",
) -> tuple[dict, ...]:
    findings: list[dict] = []
    if not isinstance(block, dict) or block.get("kind") != "itemized" or \
            set(block) not in (
                {"kind", "in_sequence", "items"},
                {"kind", "in_sequence", "items", "repository_trace"},
            ):
        return (_finding(
            "RESPONSE_BLOCK_INVALID_NODE", path, "itemized block shape is closed"),)
    if type(block.get("in_sequence")) is not bool:
        findings.append(_finding(
            "RESPONSE_BLOCK_INVALID_SEQUENCE", path + "/in_sequence",
            "in_sequence must be boolean"))
    items = block.get("items")
    if not isinstance(items, list) or not items:
        findings.append(_finding(
            "RESPONSE_BLOCK_EMPTY", path + "/items", "itemized block must contain items"))
        return tuple(findings)

    trace_present = block.get("repository_trace") is not None or any(
        isinstance(item, dict) and item.get("repository_trace") is not None
        for item in items
    )
    if trace_present and source_text is None:
        findings.append(_finding(
            "RESPONSE_BLOCK_SOURCE_REQUIRED", path + "/repository_trace",
            "source.text is required to validate Repository trace spans"))

    block_trace = block.get("repository_trace")
    block_span: dict | None = None
    if block_trace is not None:
        required = {
            "repository_rule_id", "source_span", "source",
            "in_sequence_span", "in_sequence_source",
        }
        if not isinstance(block_trace, dict) or set(block_trace) != required:
            findings.append(_finding(
                "RESPONSE_BLOCK_INVALID_TRACE", path + "/repository_trace",
                "block trace shape is closed"))
        else:
            if block_trace.get("repository_rule_id") != "ResponseBlockItemized":
                findings.append(_finding(
                    "RESPONSE_BLOCK_TRACE_RULE_MISMATCH",
                    path + "/repository_trace/repository_rule_id",
                    "expected ResponseBlockItemized"))
            try:
                block_span = _span(
                    block_trace.get("source_span"),
                    path + "/repository_trace/source_span")
            except ResponseBlockError as exc:
                findings.append(exc.finding())
            sequence_span = block_trace.get("in_sequence_span")
            sequence_source = block_trace.get("in_sequence_source")
            if (sequence_span is None) != (sequence_source is None) or \
                    bool(block.get("in_sequence")) != (sequence_span is not None):
                findings.append(_finding(
                    "RESPONSE_BLOCK_SEQUENCE_TRACE_MISMATCH",
                    path + "/repository_trace/in_sequence_span",
                    "sequence flag and trace must agree"))
            if sequence_span is not None:
                try:
                    _span(sequence_span, path + "/repository_trace/in_sequence_span")
                except ResponseBlockError as exc:
                    findings.append(exc.finding())
                if "".join((sequence_source or "").split()) != "insequence":
                    findings.append(_finding(
                        "RESPONSE_BLOCK_SEQUENCE_TAMPERED",
                        path + "/repository_trace/in_sequence_source",
                        "sequence source must be 'in sequence'"))
            if source_text is not None and block_span is not None:
                source = block_trace.get("source")
                if block_span["end"] > len(source_text) or \
                        source_text[block_span["start"]:block_span["end"]] != source:
                    findings.append(_finding(
                        "RESPONSE_BLOCK_SOURCE_TAMPERED",
                        path + "/repository_trace/source",
                        "source does not match source_span"))

    atomic_indexes: set[int] = set()
    for position, item in enumerate(items):
        item_path = f"{path}/items/{position}"
        required = {"position", "bullet", "connector_before", "response"}
        if not isinstance(item, dict) or set(item) not in (
                required, required | {"repository_trace"}):
            findings.append(_finding(
                "RESPONSE_BLOCK_INVALID_ITEM", item_path, "item shape is closed"))
            continue
        if item.get("position") != position:
            findings.append(_finding(
                "RESPONSE_BLOCK_POSITION_MISMATCH", item_path + "/position",
                "positions must be contiguous and zero-based"))
        bullet = item.get("bullet")
        try:
            _bullet({**bullet, "span": {}, "source": ""}
                    if isinstance(bullet, dict) else bullet, item_path + "/bullet")
        except ResponseBlockError:
            if not isinstance(bullet, dict) or set(bullet) != {"kind", "value"} or \
                    (bullet.get("kind") == "hyphen" and bullet.get("value") != "-") or \
                    (bullet.get("kind") == "integer" and
                     not _is_ascii_integer_bullet(bullet.get("value"))) or \
                    (isinstance(bullet, dict) and
                     bullet.get("kind") not in {"hyphen", "integer"}):
                findings.append(_finding(
                    "RESPONSE_BLOCK_INVALID_BULLET", item_path + "/bullet",
                    "bullet kind and value must agree"))
        connector = item.get("connector_before")
        if position == 0 and connector is not None:
            findings.append(_finding(
                "RESPONSE_BLOCK_FIRST_CONNECTOR", item_path + "/connector_before",
                "the first item cannot have a connector"))
        elif connector is not None and connector not in _CONNECTORS:
            findings.append(_finding(
                "RESPONSE_BLOCK_INVALID_CONNECTOR", item_path + "/connector_before",
                f"unsupported connector {connector!r}"))
        if not isinstance(item.get("response"), dict):
            findings.append(_finding(
                "RESPONSE_BLOCK_INVALID_RESPONSE", item_path + "/response",
                "response must be an object"))

        trace = item.get("repository_trace")
        if trace is None:
            continue
        trace_keys = {
            "repository_rule_id", "source_span", "source", "bullet_span",
            "bullet_source", "connector_span", "connector_source",
            "atomic_response_index",
        }
        if not isinstance(trace, dict) or set(trace) != trace_keys:
            findings.append(_finding(
                "RESPONSE_BLOCK_INVALID_TRACE", item_path + "/repository_trace",
                "item trace shape is closed"))
            continue
        if trace.get("repository_rule_id") != "BULLET":
            findings.append(_finding(
                "RESPONSE_BLOCK_TRACE_RULE_MISMATCH",
                item_path + "/repository_trace/repository_rule_id", "expected BULLET"))
        try:
            item_span = _span(
                trace.get("source_span"), item_path + "/repository_trace/source_span")
            bullet_span = _span(
                trace.get("bullet_span"), item_path + "/repository_trace/bullet_span")
            if not (item_span["start"] <= bullet_span["start"] <=
                    bullet_span["end"] <= item_span["end"]):
                findings.append(_finding(
                    "RESPONSE_BLOCK_TRACE_OUTSIDE_ITEM",
                    item_path + "/repository_trace/bullet_span",
                    "bullet span is outside item span"))
            if block_span is not None and not (
                    block_span["start"] <= item_span["start"] <=
                    item_span["end"] <= block_span["end"]):
                findings.append(_finding(
                    "RESPONSE_BLOCK_TRACE_OUTSIDE_BLOCK",
                    item_path + "/repository_trace/source_span",
                    "item span is outside block span"))
            if source_text is not None:
                for span_value, source_key in (
                    (item_span, "source"), (bullet_span, "bullet_source")):
                    if span_value["end"] > len(source_text) or \
                            source_text[span_value["start"]:span_value["end"]] != \
                            trace.get(source_key):
                        findings.append(_finding(
                            "RESPONSE_BLOCK_SOURCE_TAMPERED",
                            item_path + "/repository_trace/" + source_key,
                            "source does not match source_span"))
        except ResponseBlockError as exc:
            findings.append(exc.finding())
        connector_span = trace.get("connector_span")
        connector_source = trace.get("connector_source")
        if (connector_span is None) != (connector_source is None) or \
                (connector is None) != (connector_span is None):
            findings.append(_finding(
                "RESPONSE_BLOCK_CONNECTOR_TRACE_MISMATCH",
                item_path + "/repository_trace/connector_span",
                "connector value and trace must agree"))
        elif connector_span is not None:
            try:
                parsed_span = _span(
                    connector_span, item_path + "/repository_trace/connector_span")
                if source_text is not None and (
                        parsed_span["end"] > len(source_text) or
                        source_text[parsed_span["start"]:parsed_span["end"]] !=
                        connector_source):
                    findings.append(_finding(
                        "RESPONSE_BLOCK_SOURCE_TAMPERED",
                        item_path + "/repository_trace/connector_source",
                        "connector source does not match span"))
            except ResponseBlockError as exc:
                findings.append(exc.finding())
            if connector in _CONNECTORS and \
                    "".join((connector_source or "").split()) != \
                    _CONNECTOR_SOURCE[connector]:
                findings.append(_finding(
                    "RESPONSE_BLOCK_CONNECTOR_TAMPERED",
                    item_path + "/repository_trace/connector_source",
                    "connector source does not match kind"))
        atomic_index = trace.get("atomic_response_index")
        if type(atomic_index) is not int or atomic_index < 0:
            findings.append(_finding(
                "RESPONSE_BLOCK_INVALID_ATOMIC_INDEX",
                item_path + "/repository_trace/atomic_response_index",
                "index must be non-negative"))
        elif atomic_index in atomic_indexes:
            findings.append(_finding(
                "RESPONSE_BLOCK_DUPLICATE_ATOMIC_INDEX",
                item_path + "/repository_trace/atomic_response_index",
                f"atomic response index {atomic_index} is duplicated"))
        else:
            atomic_indexes.add(atomic_index)
    return tuple(findings)


def response_block_core_findings(
    core: object, *, source_text: str | None = None,
) -> tuple[dict, ...]:
    if not isinstance(core, dict):
        return (_finding(
            "RESPONSE_BLOCK_INVALID_CORE", "/rimay_core", "rimay_core must be an object"),)
    sources = [name for name in ("response", "response_expression", "response_block")
               if name in core]
    if len(sources) > 1:
        return (_finding(
            "RESPONSE_BLOCK_DUAL_SOURCE", "/rimay_core",
            "response, response_expression and response_block are mutually exclusive"),)
    if "response_block" not in core:
        return ()
    return response_block_findings(core["response_block"], source_text=source_text)


def canonical_response_block_meaning(
    block: dict, *, source_text: str | None = None,
) -> tuple:
    findings = response_block_findings(block, source_text=source_text)
    if findings:
        first = findings[0]
        raise ResponseBlockError(first["code"], first["path"], first["message"])
    return (
        "itemized", block["in_sequence"],
        tuple((
            item["position"], item["bullet"]["kind"], item["bullet"]["value"],
            item["connector_before"], _value_sha256(item["response"]),
        ) for item in block["items"]),
    )


_SURFACE = {
    "en": {
        "prefix": "do the following actions", "sequence": " in sequence",
        "item": "item", "connector": "connector",
        "none": "none", **{kind: kind for kind in _CONNECTORS},
    },
    "ja": {
        "prefix": "次の動作を実行する", "sequence": "（順番に）",
        "item": "項目", "connector": "接続", "none": "なし",
        "comma": "読点", "and": "かつ", "or": "または",
        "comma_and": "読点かつ", "comma_or": "読点または",
    },
}


def render_response_block(
    block: dict, render_response: Callable[[dict], str], *, language: str,
    source_text: str | None = None,
) -> str:
    labels = _SURFACE.get(language)
    if labels is None:
        raise ResponseBlockError(
            "RESPONSE_BLOCK_LANGUAGE", "/language", f"unsupported language {language!r}")
    findings = response_block_findings(block, source_text=source_text)
    if findings:
        first = findings[0]
        raise ResponseBlockError(first["code"], first["path"], first["message"])
    rendered = []
    for item in block["items"]:
        leaf = render_response(item["response"])
        if not isinstance(leaf, str) or not leaf:
            raise ResponseBlockError(
                "RESPONSE_BLOCK_RENDER_EMPTY", "/rimay_core/response_block/items",
                "response renderer must return non-empty text")
        connector = labels[item["connector_before"]] \
            if item["connector_before"] is not None else labels["none"]
        rendered.append(
            f"[{labels['item']}={item['bullet']['value']};"
            f"{labels['connector']}={connector}] {leaf}")
    prefix = labels["prefix"] + (labels["sequence"] if block["in_sequence"] else "")
    return prefix + ": " + " ; ".join(rendered)


def parse_rendered_response_block(
    text: str,
    parse_response: Callable[[str, int], tuple[dict, int]],
    *,
    language: str,
) -> dict:
    labels = _SURFACE.get(language)
    if labels is None:
        raise ResponseBlockError(
            "RESPONSE_BLOCK_LANGUAGE", "/language", f"unsupported language {language!r}")
    plain_prefix = labels["prefix"] + ": "
    sequence_prefix = labels["prefix"] + labels["sequence"] + ": "
    if text.startswith(sequence_prefix):
        in_sequence, position = True, len(sequence_prefix)
    elif text.startswith(plain_prefix):
        in_sequence, position = False, len(plain_prefix)
    else:
        raise ResponseBlockError(
            "RESPONSE_BLOCK_PARSE_PREFIX", "/surface", "response block prefix is invalid")
    reverse = {value: key for key, value in labels.items()
               if key in _CONNECTORS or key == "none"}
    items: list[dict] = []
    while position < len(text):
        closing = text.find("] ", position)
        if closing < 0 or not text.startswith("[", position):
            raise ResponseBlockError(
                "RESPONSE_BLOCK_PARSE_ITEM", "/surface", "item header is incomplete")
        header = text[position + 1:closing]
        expected_item = labels["item"] + "="
        expected_connector = labels["connector"] + "="
        parts = header.split(";")
        if len(parts) != 2 or not parts[0].startswith(expected_item) or \
                not parts[1].startswith(expected_connector):
            raise ResponseBlockError(
                "RESPONSE_BLOCK_PARSE_ITEM", "/surface", "item header is invalid")
        bullet_value = parts[0][len(expected_item):]
        connector_label = parts[1][len(expected_connector):]
        connector = reverse.get(connector_label)
        if connector_label not in reverse:
            raise ResponseBlockError(
                "RESPONSE_BLOCK_PARSE_CONNECTOR", "/surface",
                f"unknown connector label {connector_label!r}")
        connector_value = None if connector == "none" else connector
        if bullet_value != "-" and not _is_ascii_integer_bullet(bullet_value):
            raise ResponseBlockError(
                "RESPONSE_BLOCK_PARSE_BULLET", "/surface", "bullet token is invalid")
        response, end = parse_response(text, closing + 2)
        if not isinstance(response, dict) or type(end) is not int or \
                end <= closing + 2 or end > len(text):
            raise ResponseBlockError(
                "RESPONSE_BLOCK_PARSE_RESPONSE", "/surface",
                "response parser returned an invalid result")
        items.append({
            "position": len(items),
            "bullet": {"kind": "hyphen" if bullet_value == "-" else "integer",
                       "value": bullet_value},
            "connector_before": connector_value,
            "response": response,
        })
        if end == len(text):
            position = end
            break
        if not text.startswith(" ; ", end):
            raise ResponseBlockError(
                "RESPONSE_BLOCK_PARSE_TRAILING", "/surface",
                "expected the item delimiter")
        position = end + 3
    block = {"kind": "itemized", "in_sequence": in_sequence, "items": items}
    findings = response_block_findings(block)
    if findings:
        first = findings[0]
        raise ResponseBlockError(first["code"], first["path"], first["message"])
    return block


def migrate_requirement_to_response_block_candidate(document: dict) -> dict:
    migrated = copy.deepcopy(document)
    if migrated.get("schema_version") != ACTIVE_CANONICAL_VERSION:
        raise ResponseBlockError(
            "RESPONSE_BLOCK_MIGRATION_VERSION", "/schema_version",
            f"migration input must use {ACTIVE_CANONICAL_VERSION}")
    core = migrated.get("rimay_core")
    if not isinstance(core, dict) or "response_block" in core:
        raise ResponseBlockError(
            "RESPONSE_BLOCK_INVALID_CORE", "/rimay_core",
            "0.7 input must have no response_block")
    findings = response_block_core_findings(
        core, source_text=_canonical_source_text(migrated))
    if findings:
        first = findings[0]
        raise ResponseBlockError(first["code"], first["path"], first["message"])
    migrated["schema_version"] = RESPONSE_BLOCK_CANDIDATE_VERSION
    migrated.pop("validation_state", None)
    return migrated


def rollback_requirement_from_response_block_candidate(document: dict) -> dict:
    rolled_back = copy.deepcopy(document)
    if rolled_back.get("schema_version") != RESPONSE_BLOCK_CANDIDATE_VERSION:
        raise ResponseBlockError(
            "RESPONSE_BLOCK_ROLLBACK_VERSION", "/schema_version",
            f"rollback input must use {RESPONSE_BLOCK_CANDIDATE_VERSION}")
    core = rolled_back.get("rimay_core")
    if not isinstance(core, dict):
        raise ResponseBlockError(
            "RESPONSE_BLOCK_INVALID_CORE", "/rimay_core", "rimay_core must be an object")
    findings = response_block_core_findings(
        core, source_text=_canonical_source_text(rolled_back))
    if findings:
        first = findings[0]
        raise ResponseBlockError(first["code"], first["path"], first["message"])
    if "response_block" in core:
        raise ResponseBlockError(
            "RESPONSE_BLOCK_ROLLBACK_LOSSY", "/rimay_core/response_block",
            "itemized Response Block is not representable by Schema 0.7.0")
    rolled_back["schema_version"] = ACTIVE_CANONICAL_VERSION
    return rolled_back


def quarantine_response_block_for_rollback(document: dict) -> dict:
    quarantined = copy.deepcopy(document)
    if quarantined.get("schema_version") != RESPONSE_BLOCK_CANDIDATE_VERSION:
        raise ResponseBlockError(
            "RESPONSE_BLOCK_ROLLBACK_VERSION", "/schema_version",
            f"quarantine input must use {RESPONSE_BLOCK_CANDIDATE_VERSION}")
    core = quarantined.get("rimay_core")
    if not isinstance(core, dict):
        raise ResponseBlockError(
            "RESPONSE_BLOCK_INVALID_CORE", "/rimay_core", "rimay_core must be an object")
    block = core.get("response_block")
    if not isinstance(block, dict):
        raise ResponseBlockError(
            "RESPONSE_BLOCK_QUARANTINE_SCOPE", "/rimay_core/response_block",
            "a valid itemized response_block is required")
    findings = response_block_findings(
        block, source_text=_canonical_source_text(quarantined))
    if findings:
        first = findings[0]
        raise ResponseBlockError(first["code"], first["path"], first["message"])
    core.pop("response_block")
    extensions = quarantined.setdefault("extensions", {})
    semantics = extensions.setdefault("additional_semantics", []) \
        if isinstance(extensions, dict) else None
    if not isinstance(semantics, list) or any(
            isinstance(item, dict) and item.get("kind") == _QUARANTINE_KIND
            for item in semantics):
        raise ResponseBlockError(
            "RESPONSE_BLOCK_QUARANTINE_CONFLICT", "/extensions/additional_semantics",
            "quarantine target is invalid or already occupied")
    semantics.append({
        "kind": _QUARANTINE_KIND,
        "source_schema_version": RESPONSE_BLOCK_CANDIDATE_VERSION,
        "response_block": block,
        "response_block_sha256": _value_sha256(block),
    })
    quarantined["schema_version"] = ACTIVE_CANONICAL_VERSION
    return quarantined


def restore_quarantined_response_block(document: dict) -> dict:
    restored = copy.deepcopy(document)
    if restored.get("schema_version") != ACTIVE_CANONICAL_VERSION:
        raise ResponseBlockError(
            "RESPONSE_BLOCK_MIGRATION_VERSION", "/schema_version",
            f"restore input must use {ACTIVE_CANONICAL_VERSION}")
    core = restored.get("rimay_core")
    extensions = restored.get("extensions")
    semantics = extensions.get("additional_semantics") if isinstance(extensions, dict) \
        else None
    if not isinstance(core, dict) or not isinstance(semantics, list):
        raise ResponseBlockError(
            "RESPONSE_BLOCK_QUARANTINE_MISSING", "/extensions/additional_semantics",
            "quarantine record is absent")
    records = [item for item in semantics
               if isinstance(item, dict) and item.get("kind") == _QUARANTINE_KIND]
    if len(records) != 1 or any(
            name in core for name in ("response", "response_expression", "response_block")):
        raise ResponseBlockError(
            "RESPONSE_BLOCK_QUARANTINE_CONFLICT", "/rimay_core",
            "restore requires one record and an empty response source")
    record = records[0]
    required = {
        "kind", "source_schema_version", "response_block", "response_block_sha256"}
    block = record.get("response_block")
    if set(record) != required or \
            record.get("source_schema_version") != RESPONSE_BLOCK_CANDIDATE_VERSION or \
            not isinstance(block, dict) or \
            record.get("response_block_sha256") != _value_sha256(block):
        raise ResponseBlockError(
            "RESPONSE_BLOCK_QUARANTINE_INVALID", "/extensions/additional_semantics",
            "quarantine payload shape, hash, or block is invalid")
    findings = response_block_findings(
        block, source_text=_canonical_source_text(restored))
    if findings:
        first = findings[0]
        raise ResponseBlockError(first["code"], first["path"], first["message"])
    core["response_block"] = block
    semantics.remove(record)
    if not semantics:
        extensions.pop("additional_semantics")
    restored["schema_version"] = RESPONSE_BLOCK_CANDIDATE_VERSION
    return restored


def replay_response_block_migration(documents: Iterable[dict]) -> dict:
    migrated = [migrate_requirement_to_response_block_candidate(item)
                for item in documents]
    payload = json.dumps(
        migrated, ensure_ascii=False, sort_keys=True, separators=(",", ":")
    ).encode("utf-8")
    return {
        "documents": migrated, "document_count": len(migrated),
        "replay_sha256": "sha256:" + hashlib.sha256(payload).hexdigest(),
    }


def build_response_block_candidate_schema(base_schema: dict) -> dict:
    schema = copy.deepcopy(base_schema)
    schema["properties"]["schema_version"]["const"] = RESPONSE_BLOCK_CANDIDATE_VERSION
    schema["description"] = (
        base_schema.get("description", "") +
        " B5 CAP-RESPONSE-BLOCK/CAP-LEXICAL-STRUCTURE candidate: "
        "response_blockは採用前隔離検証。"
    )
    nullable_span = {"oneOf": [{"$ref": "#/$defs/span"}, {"type": "null"}]}
    nullable_string = {"type": ["string", "null"]}
    schema["$defs"]["repositoryResponseBlockTrace"] = {
        "type": "object",
        "required": [
            "repository_rule_id", "source_span", "source",
            "in_sequence_span", "in_sequence_source",
        ],
        "additionalProperties": False,
        "properties": {
            "repository_rule_id": {"const": "ResponseBlockItemized"},
            "source_span": {"$ref": "#/$defs/span"},
            "source": {"type": "string"},
            "in_sequence_span": nullable_span,
            "in_sequence_source": nullable_string,
        },
    }
    schema["$defs"]["repositoryResponseBlockItemTrace"] = {
        "type": "object",
        "required": [
            "repository_rule_id", "source_span", "source", "bullet_span",
            "bullet_source", "connector_span", "connector_source",
            "atomic_response_index",
        ],
        "additionalProperties": False,
        "properties": {
            "repository_rule_id": {"const": "BULLET"},
            "source_span": {"$ref": "#/$defs/span"},
            "source": {"type": "string"},
            "bullet_span": {"$ref": "#/$defs/span"},
            "bullet_source": {"type": "string"},
            "connector_span": nullable_span,
            "connector_source": nullable_string,
            "atomic_response_index": {"type": "integer", "minimum": 0},
        },
    }
    schema["$defs"]["responseBlockBullet"] = {
        "oneOf": [
            {
                "type": "object", "required": ["kind", "value"],
                "additionalProperties": False,
                "properties": {"kind": {"const": "hyphen"}, "value": {"const": "-"}},
            },
            {
                "type": "object", "required": ["kind", "value"],
                "additionalProperties": False,
                "properties": {
                    "kind": {"const": "integer"},
                    "value": {"type": "string", "pattern": "^[0-9]+$"},
                },
            },
        ]
    }
    schema["$defs"]["responseBlockItem"] = {
        "type": "object",
        "required": ["position", "bullet", "connector_before", "response"],
        "additionalProperties": False,
        "properties": {
            "position": {"type": "integer", "minimum": 0},
            "bullet": {"$ref": "#/$defs/responseBlockBullet"},
            "connector_before": {
                "type": ["string", "null"],
                "enum": [None, "comma", "and", "or", "comma_and", "comma_or"],
            },
            "response": {"$ref": "#/$defs/response"},
            "repository_trace": {"$ref": "#/$defs/repositoryResponseBlockItemTrace"},
        },
    }
    schema["$defs"]["responseBlock"] = {
        "type": "object",
        "required": ["kind", "in_sequence", "items"],
        "additionalProperties": False,
        "properties": {
            "kind": {"const": "itemized"},
            "in_sequence": {"type": "boolean"},
            "items": {
                "type": "array", "minItems": 1,
                "items": {"$ref": "#/$defs/responseBlockItem"},
            },
            "repository_trace": {"$ref": "#/$defs/repositoryResponseBlockTrace"},
        },
    }
    core = schema["$defs"]["rimayCore"]
    core["properties"]["response_block"] = {"$ref": "#/$defs/responseBlock"}
    core.setdefault("allOf", []).extend([
        {"not": {"required": ["response", "response_block"]}},
        {"not": {"required": ["response_expression", "response_block"]}},
    ])
    return schema
