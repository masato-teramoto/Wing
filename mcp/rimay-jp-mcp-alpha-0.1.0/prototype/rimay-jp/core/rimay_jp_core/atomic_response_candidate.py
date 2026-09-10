"""B5-P Atomic Responseの隔離Canonical 0.9.0 candidate bundle。

Active 0.8.0 runtimeへ接続せず、Repository固有文書のAtomicSystemResponseが
保持するeffective modality、否定、leaf-local frequency、rule/source/spanを
欠落なく検証する。Action Family・Roleの意味はcallback境界へ残す。
"""
from __future__ import annotations

import copy
import hashlib
import json
import re
from dataclasses import dataclass
from typing import Callable, Iterable, Iterator


ACTIVE_CANONICAL_VERSION = "0.8.0"
ATOMIC_RESPONSE_CANDIDATE_VERSION = "0.9.0"
_QUARANTINE_KIND = "RIMAY_JP_ATOMIC_RESPONSE_QUARANTINE"
_MODALS = {"must": "MUST", "shall": "MUST"}
_UNITS = {
    "second": "second", "seconds": "second",
    "minute": "minute", "minutes": "minute",
    "hour": "hour", "hours": "hour",
    "day": "day", "days": "day",
}
_JA_UNITS = {"second": "秒", "minute": "分", "hour": "時間", "day": "日"}


@dataclass(frozen=True)
class AtomicResponseError(ValueError):
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


def _finding(code: str, path: str, message: str) -> dict:
    return {"code": code, "severity": "blocking", "path": path, "message": message}


def _value_sha256(value: object) -> str:
    payload = json.dumps(
        value, ensure_ascii=False, sort_keys=True, separators=(",", ":")
    ).encode("utf-8")
    return "sha256:" + hashlib.sha256(payload).hexdigest()


def _span(value: object, path: str) -> dict:
    if not isinstance(value, dict) or set(value) != {"start", "end"} or \
            type(value.get("start")) is not int or type(value.get("end")) is not int or \
            value["start"] < 0 or value["end"] < value["start"]:
        raise AtomicResponseError(
            "ATOMIC_RESPONSE_INVALID_SPAN", path, "span must be ordered integers")
    return {"start": value["start"], "end": value["end"]}


def _source(value: object, source_text: str, path: str) -> tuple[dict, str]:
    if not isinstance(value, dict):
        raise AtomicResponseError(
            "ATOMIC_RESPONSE_INVALID_REPOSITORY_NODE", path, "record must be an object")
    span = _span(value.get("span"), path + "/span")
    source = value.get("source")
    if not isinstance(source, str) or span["end"] > len(source_text) or \
            source_text[span["start"]:span["end"]] != source:
        raise AtomicResponseError(
            "ATOMIC_RESPONSE_SOURCE_TAMPERED", path + "/source",
            "source does not match source_span")
    return span, source


def _decoded_fact(
    value: object, source_text: str, path: str, *, outer_span: dict,
) -> str:
    if not isinstance(value, dict) or not isinstance(value.get("value"), str):
        raise AtomicResponseError(
            "ATOMIC_RESPONSE_INVALID_OPTION", path, "one decoded value is required")
    value_span = _span(value.get("span"), path + "/span")
    if not (outer_span["start"] <= value_span["start"] <=
            value_span["end"] <= outer_span["end"]):
        raise AtomicResponseError(
            "ATOMIC_RESPONSE_OPTION_OUTSIDE_RECORD", path + "/span",
            "value span is outside option span")
    surface = value.get("surface")
    if not isinstance(surface, str) or value_span["end"] > len(source_text) or \
            source_text[value_span["start"]:value_span["end"]] != surface:
        raise AtomicResponseError(
            "ATOMIC_RESPONSE_SOURCE_TAMPERED", path + "/surface",
            "value surface does not match span")
    return value["value"]


def _leaf_value(option: object, source_text: str, path: str) -> tuple[str, dict, str]:
    if not isinstance(option, dict) or set(option) != {"span", "source", "value"}:
        raise AtomicResponseError(
            "ATOMIC_RESPONSE_INVALID_OPTION", path, "option shape is closed")
    option_span, option_source = _source(option, source_text, path)
    decoded = _decoded_fact(
        option.get("value"), source_text, path + "/value", outer_span=option_span)
    return decoded, option_span, option_source


def _system_modal(record: object, source_text: str) -> tuple[str, dict, str]:
    path = "/repository/system_response/modality"
    required = {"owner_rule", "rule_path", "feature", "operator", "span", "source", "values"}
    if not isinstance(record, dict) or set(record) != required or \
            record.get("owner_rule") != "SystemResponse" or \
            record.get("rule_path") != ["SystemResponse"] or \
            record.get("feature") not in {"modal", "modal_verb"} or \
            record.get("operator") != "=":
        raise AtomicResponseError(
            "ATOMIC_RESPONSE_INVALID_SYSTEM_MODAL", path,
            "SystemResponse modality assignment is invalid")
    span, source = _source(record, source_text, path)
    values = record.get("values")
    if not isinstance(values, list) or len(values) != 1 or \
            not isinstance(values[0], dict) or not isinstance(values[0].get("value"), str):
        raise AtomicResponseError(
            "ATOMIC_RESPONSE_INVALID_SYSTEM_MODAL", path + "/values",
            "one modal value is required")
    modal = values[0]["value"].lower()
    if modal not in _MODALS or source.lower() != modal:
        raise AtomicResponseError(
            "ATOMIC_RESPONSE_UNSUPPORTED_MODAL", path,
            f"unsupported SystemResponse modal {values[0]['value']!r}")
    return modal, span, source


def _frequency(record: object, source_text: str, path: str) -> tuple[dict, dict, str]:
    if not isinstance(record, dict) or set(record) != {
            "span", "source", "keyword", "value"}:
        raise AtomicResponseError(
            "ATOMIC_RESPONSE_INVALID_FREQUENCY", path, "frequency shape is closed")
    span, source = _source(record, source_text, path)
    keyword = record.get("keyword")
    if not isinstance(keyword, dict) or keyword.get("value") != "every":
        raise AtomicResponseError(
            "ATOMIC_RESPONSE_INVALID_FREQUENCY", path + "/keyword",
            "Atomic Response frequency must use every")
    _, keyword_source = _source(keyword, source_text, path + "/keyword")
    if keyword_source.lower() != "every":
        raise AtomicResponseError(
            "ATOMIC_RESPONSE_SOURCE_TAMPERED", path + "/keyword/source",
            "frequency keyword source must be every")
    expression = _decoded_fact(
        record.get("value"), source_text, path + "/value", outer_span=span)
    match = re.fullmatch(r"\s*([0-9]+(?:\.[0-9]+)?)\s+([A-Za-z]+)\s*", expression)
    if match is None or match.group(2).lower() not in _UNITS:
        raise AtomicResponseError(
            "ATOMIC_RESPONSE_FREQUENCY_UNMEASURABLE", path + "/value",
            "frequency must be a positive number plus second/minute/hour/day")
    number = float(match.group(1))
    if number <= 0:
        raise AtomicResponseError(
            "ATOMIC_RESPONSE_FREQUENCY_NON_POSITIVE", path + "/value",
            "frequency interval must be positive")
    value: int | float = int(number) if number.is_integer() else number
    return {
        "value": value,
        "unit": _UNITS[match.group(2).lower()],
        "source_expression": expression,
    }, span, source


def project_repository_atomic_response(
    repository_atomic: dict,
    system_modality: dict,
    source_text: str,
    project_action: Callable[[dict], dict],
) -> dict:
    """AtomicSystemResponse一件を0.9 response候補へ正規化する。"""
    path = "/repository/atomic_response"
    required = {"index", "span", "source", "modality", "negation", "frequency", "action"}
    if not isinstance(repository_atomic, dict) or set(repository_atomic) != required:
        raise AtomicResponseError(
            "ATOMIC_RESPONSE_INVALID_REPOSITORY_NODE", path, "atomic shape is closed")
    index = repository_atomic.get("index")
    if type(index) is not int or index < 0:
        raise AtomicResponseError(
            "ATOMIC_RESPONSE_INVALID_INDEX", path + "/index", "index must be non-negative")
    atomic_span, atomic_source = _source(repository_atomic, source_text, path)
    outer_modal, outer_span, outer_source = _system_modal(system_modality, source_text)

    local = repository_atomic.get("modality")
    if local is None:
        modal, modal_span, modal_source, modal_origin = (
            outer_modal, outer_span, outer_source, "system_response")
    else:
        modal, modal_span, modal_source = _leaf_value(
            local, source_text, path + "/modality")
        modal = modal.lower()
        if modal not in _MODALS:
            raise AtomicResponseError(
                "ATOMIC_RESPONSE_UNSUPPORTED_MODAL", path + "/modality",
                f"unsupported Atomic Response modal {modal!r}")
        modal_origin = "atomic_response"

    negation = repository_atomic.get("negation")
    negation_span = negation_source = None
    if negation is not None:
        negation_value, negation_span, negation_source = _leaf_value(
            negation, source_text, path + "/negation")
        if negation_value.lower() != "not":
            raise AtomicResponseError(
                "ATOMIC_RESPONSE_INVALID_NEGATION", path + "/negation",
                "Atomic Response negation must be not")

    frequency = repository_atomic.get("frequency")
    frequency_value = frequency_span = frequency_source = None
    if frequency is not None:
        frequency_value, frequency_span, frequency_source = _frequency(
            frequency, source_text, path + "/frequency")

    response = project_action(copy.deepcopy(repository_atomic["action"]))
    if not isinstance(response, dict):
        raise AtomicResponseError(
            "ATOMIC_RESPONSE_INVALID_ACTION_RESULT", path + "/action",
            "action projector must return a Canonical response object")
    reserved = {"modality", "frequency", "repository_trace"} & set(response)
    if reserved:
        raise AtomicResponseError(
            "ATOMIC_RESPONSE_ACTION_AUTHORITY_CONFLICT", path + "/action",
            f"action projector controls reserved fields: {sorted(reserved)}")
    response["modality"] = "MUST_NOT" if negation is not None else _MODALS[modal]
    if frequency_value is not None:
        response["frequency"] = frequency_value
    response["repository_trace"] = {
        "repository_rule_id": "AtomicSystemResponse",
        "atomic_response_index": index,
        "source_span": atomic_span,
        "source": atomic_source,
        "modality_origin": modal_origin,
        "modality_span": modal_span,
        "modality_source": modal_source,
        "negation_span": negation_span,
        "negation_source": negation_source,
        "frequency_span": frequency_span,
        "frequency_source": frequency_source,
    }
    findings = atomic_response_findings(response, source_text=source_text)
    if findings:
        first = findings[0]
        raise AtomicResponseError(first["code"], first["path"], first["message"])
    return response


def atomic_response_findings(
    response: object,
    *,
    source_text: str | None = None,
    path: str = "/rimay_core/response",
) -> tuple[dict, ...]:
    """0.9 additionsのclosed shape・意味・trace整合を検査する。"""
    if not isinstance(response, dict):
        return (_finding(
            "ATOMIC_RESPONSE_INVALID_RESPONSE", path, "response must be an object"),)
    findings: list[dict] = []
    frequency = response.get("frequency")
    if frequency is not None:
        if not isinstance(frequency, dict) or set(frequency) != {
                "value", "unit", "source_expression"}:
            findings.append(_finding(
                "ATOMIC_RESPONSE_INVALID_FREQUENCY", path + "/frequency",
                "frequency shape is closed"))
        else:
            value = frequency.get("value")
            if type(value) not in {int, float} or value <= 0:
                findings.append(_finding(
                    "ATOMIC_RESPONSE_FREQUENCY_NON_POSITIVE", path + "/frequency/value",
                    "frequency interval must be positive"))
            if frequency.get("unit") not in set(_UNITS.values()):
                findings.append(_finding(
                    "ATOMIC_RESPONSE_INVALID_FREQUENCY", path + "/frequency/unit",
                    "frequency unit is unsupported"))
            if not isinstance(frequency.get("source_expression"), str) or \
                    not frequency["source_expression"].strip():
                findings.append(_finding(
                    "ATOMIC_RESPONSE_INVALID_FREQUENCY",
                    path + "/frequency/source_expression",
                    "source_expression must be non-empty"))
    trace = response.get("repository_trace")
    if trace is None:
        return tuple(findings)
    trace_keys = {
        "repository_rule_id", "atomic_response_index", "source_span", "source",
        "modality_origin", "modality_span", "modality_source",
        "negation_span", "negation_source", "frequency_span", "frequency_source",
    }
    if not isinstance(trace, dict) or set(trace) != trace_keys:
        findings.append(_finding(
            "ATOMIC_RESPONSE_INVALID_TRACE", path + "/repository_trace",
            "atomic trace shape is closed"))
        return tuple(findings)
    if trace.get("repository_rule_id") != "AtomicSystemResponse":
        findings.append(_finding(
            "ATOMIC_RESPONSE_TRACE_RULE_MISMATCH",
            path + "/repository_trace/repository_rule_id",
            "expected AtomicSystemResponse"))
    if type(trace.get("atomic_response_index")) is not int or \
            trace["atomic_response_index"] < 0:
        findings.append(_finding(
            "ATOMIC_RESPONSE_INVALID_INDEX",
            path + "/repository_trace/atomic_response_index",
            "index must be non-negative"))
    try:
        atomic_span = _span(trace.get("source_span"), path + "/repository_trace/source_span")
        modal_span = _span(trace.get("modality_span"), path + "/repository_trace/modality_span")
    except AtomicResponseError as exc:
        findings.append(exc.finding())
        atomic_span = modal_span = None
    origin = trace.get("modality_origin")
    modal_source = trace.get("modality_source")
    if origin not in {"system_response", "atomic_response"} or \
            not isinstance(modal_source, str) or modal_source.lower() not in _MODALS:
        findings.append(_finding(
            "ATOMIC_RESPONSE_INVALID_MODAL_TRACE", path + "/repository_trace/modality_source",
            "modal trace must identify must/shall and its origin"))
    if origin == "atomic_response" and atomic_span is not None and modal_span is not None and \
            not (atomic_span["start"] <= modal_span["start"] <=
                 modal_span["end"] <= atomic_span["end"]):
        findings.append(_finding(
            "ATOMIC_RESPONSE_TRACE_OUTSIDE_RESPONSE",
            path + "/repository_trace/modality_span",
            "local modality span is outside Atomic Response"))
    for name in ("negation", "frequency"):
        span_value = trace.get(name + "_span")
        source_value = trace.get(name + "_source")
        if (span_value is None) != (source_value is None):
            findings.append(_finding(
                "ATOMIC_RESPONSE_TRACE_PAIR_MISMATCH",
                path + "/repository_trace/" + name + "_span",
                f"{name} span and source must both be present or absent"))
            continue
        if span_value is not None:
            try:
                parsed = _span(span_value, path + "/repository_trace/" + name + "_span")
                if atomic_span is not None and not (
                        atomic_span["start"] <= parsed["start"] <=
                        parsed["end"] <= atomic_span["end"]):
                    findings.append(_finding(
                        "ATOMIC_RESPONSE_TRACE_OUTSIDE_RESPONSE",
                        path + "/repository_trace/" + name + "_span",
                        f"{name} span is outside Atomic Response"))
            except AtomicResponseError as exc:
                findings.append(exc.finding())
    negated = trace.get("negation_span") is not None
    if (response.get("modality") == "MUST_NOT") != negated:
        findings.append(_finding(
            "ATOMIC_RESPONSE_NEGATION_MODALITY_MISMATCH", path + "/modality",
            "MUST_NOT must agree with the Atomic Response not trace"))
    if (frequency is not None) != (trace.get("frequency_span") is not None):
        findings.append(_finding(
            "ATOMIC_RESPONSE_FREQUENCY_TRACE_MISMATCH", path + "/frequency",
            "frequency value and trace must agree"))
    if source_text is not None:
        for span_key, source_key in (
                ("source_span", "source"), ("modality_span", "modality_source"),
                ("negation_span", "negation_source"),
                ("frequency_span", "frequency_source")):
            span_value, source_value = trace.get(span_key), trace.get(source_key)
            if span_value is None:
                continue
            try:
                parsed = _span(span_value, path + "/repository_trace/" + span_key)
                if parsed["end"] > len(source_text) or \
                        source_text[parsed["start"]:parsed["end"]] != source_value:
                    findings.append(_finding(
                        "ATOMIC_RESPONSE_SOURCE_TAMPERED",
                        path + "/repository_trace/" + source_key,
                        "trace source does not match span"))
            except AtomicResponseError as exc:
                findings.append(exc.finding())
    return tuple(findings)


def canonical_atomic_response_meaning(response: dict) -> tuple:
    findings = atomic_response_findings(response)
    if findings:
        first = findings[0]
        raise AtomicResponseError(first["code"], first["path"], first["message"])
    semantic = copy.deepcopy(response)
    semantic.pop("repository_trace", None)
    if isinstance(semantic.get("frequency"), dict):
        semantic["frequency"].pop("source_expression", None)
    return ("atomic_response", _value_sha256(semantic))


def _number_text(value: int | float) -> str:
    return str(value) if type(value) is int else format(value, "g")


def render_atomic_response(
    response: dict,
    render_action: Callable[[dict], str],
    *,
    language: str,
) -> str:
    findings = atomic_response_findings(response)
    if findings:
        first = findings[0]
        raise AtomicResponseError(first["code"], first["path"], first["message"])
    if response.get("modality") not in {"MUST", "MUST_NOT"}:
        raise AtomicResponseError(
            "ATOMIC_RESPONSE_UNSUPPORTED_MODALITY", "/rimay_core/response/modality",
            "candidate surface supports MUST and MUST_NOT")
    action = render_action(response)
    if not isinstance(action, str) or not action.strip():
        raise AtomicResponseError(
            "ATOMIC_RESPONSE_RENDER_EMPTY", "/rimay_core/response/action",
            "action renderer returned an empty surface")
    frequency = response.get("frequency")
    if frequency is None:
        freq_en, freq_ja = "none", "なし"
    else:
        number = _number_text(frequency["value"])
        freq_en = number + " " + frequency["unit"]
        freq_ja = number + _JA_UNITS[frequency["unit"]]
    if language == "en":
        return (f"atomic response [modality={response['modality']}; "
                f"frequency={freq_en}]: {action}")
    if language == "ja":
        modal = "必須" if response["modality"] == "MUST" else "禁止"
        return f"原子応答［モダリティ={modal}；頻度={freq_ja}］：{action}"
    raise AtomicResponseError(
        "ATOMIC_RESPONSE_UNSUPPORTED_LANGUAGE", "/language", f"unsupported {language!r}")


def parse_rendered_atomic_response(
    surface: str,
    parse_action: Callable[[str], dict],
    *,
    language: str,
) -> dict:
    if language == "en":
        match = re.fullmatch(
            r"atomic response \[modality=(MUST|MUST_NOT); frequency=(none|[0-9]+(?:\.[0-9]+)? (?:second|minute|hour|day))\]: (.+)",
            surface)
        modal_map = {"MUST": "MUST", "MUST_NOT": "MUST_NOT"}
    elif language == "ja":
        match = re.fullmatch(
            r"原子応答［モダリティ=(必須|禁止)；頻度=(なし|[0-9]+(?:\.[0-9]+)?(?:秒|分|時間|日))］：(.+)",
            surface)
        modal_map = {"必須": "MUST", "禁止": "MUST_NOT"}
    else:
        raise AtomicResponseError(
            "ATOMIC_RESPONSE_UNSUPPORTED_LANGUAGE", "/language", f"unsupported {language!r}")
    if match is None:
        raise AtomicResponseError(
            "ATOMIC_RESPONSE_PARSE_SHAPE", "/surface", "surface is not a controlled Atomic Response")
    response = parse_action(match.group(3))
    if not isinstance(response, dict) or {"modality", "frequency", "repository_trace"} & set(response):
        raise AtomicResponseError(
            "ATOMIC_RESPONSE_ACTION_AUTHORITY_CONFLICT", "/surface/action",
            "action parser must return a response without Atomic-owned fields")
    response["modality"] = modal_map[match.group(1)]
    freq = match.group(2)
    if freq not in {"none", "なし"}:
        if language == "en":
            number_text, unit = freq.split(" ", 1)
        else:
            unit = next(key for key, value in _JA_UNITS.items() if freq.endswith(value))
            number_text = freq[:-len(_JA_UNITS[unit])]
        number = float(number_text)
        response["frequency"] = {
            "value": int(number) if number.is_integer() else number,
            "unit": unit,
            "source_expression": number_text + " " + unit + ("s" if number != 1 else ""),
        }
    findings = atomic_response_findings(response)
    if findings:
        first = findings[0]
        raise AtomicResponseError(first["code"], first["path"], first["message"])
    return response


def _iter_responses(core: dict) -> Iterator[tuple[str, dict]]:
    if isinstance(core.get("response"), dict):
        yield "/rimay_core/response", core["response"]
        return
    expression = core.get("response_expression")
    if isinstance(expression, dict):
        def visit(node: dict, path: str) -> Iterator[tuple[str, dict]]:
            if node.get("kind") == "response" and isinstance(node.get("response"), dict):
                yield path + "/response", node["response"]
            elif node.get("kind") == "group" and isinstance(node.get("expression"), dict):
                yield from visit(node["expression"], path + "/expression")
            elif node.get("kind") in {"and", "or"}:
                for side in ("left", "right"):
                    if isinstance(node.get(side), dict):
                        yield from visit(node[side], path + "/" + side)
        yield from visit(expression, "/rimay_core/response_expression")
        return
    block = core.get("response_block")
    if isinstance(block, dict) and isinstance(block.get("items"), list):
        for index, item in enumerate(block["items"]):
            if isinstance(item, dict) and isinstance(item.get("response"), dict):
                yield f"/rimay_core/response_block/items/{index}/response", item["response"]


def _resolve_response(core: dict, path: str) -> dict | None:
    parts = path.removeprefix("/rimay_core/").split("/")
    value: object = core
    for part in parts:
        if isinstance(value, list) and part.isdigit():
            index = int(part)
            value = value[index] if index < len(value) else None
        elif isinstance(value, dict):
            value = value.get(part)
        else:
            return None
    return value if isinstance(value, dict) else None


def migrate_requirement_to_atomic_response_candidate(document: dict) -> dict:
    migrated = copy.deepcopy(document)
    if migrated.get("schema_version") != ACTIVE_CANONICAL_VERSION:
        raise AtomicResponseError(
            "ATOMIC_RESPONSE_MIGRATION_VERSION", "/schema_version",
            f"migration input must use {ACTIVE_CANONICAL_VERSION}")
    core = migrated.get("rimay_core")
    if not isinstance(core, dict):
        raise AtomicResponseError(
            "ATOMIC_RESPONSE_INVALID_CORE", "/rimay_core", "rimay_core must be an object")
    if any("frequency" in response or "repository_trace" in response
           for _, response in _iter_responses(core)):
        raise AtomicResponseError(
            "ATOMIC_RESPONSE_MIGRATION_CONFLICT", "/rimay_core",
            "0.8 input contains 0.9 Atomic Response fields")
    migrated["schema_version"] = ATOMIC_RESPONSE_CANDIDATE_VERSION
    migrated.pop("validation_state", None)
    return migrated


def rollback_requirement_from_atomic_response_candidate(document: dict) -> dict:
    rolled_back = copy.deepcopy(document)
    if rolled_back.get("schema_version") != ATOMIC_RESPONSE_CANDIDATE_VERSION:
        raise AtomicResponseError(
            "ATOMIC_RESPONSE_ROLLBACK_VERSION", "/schema_version",
            f"rollback input must use {ATOMIC_RESPONSE_CANDIDATE_VERSION}")
    core = rolled_back.get("rimay_core")
    if not isinstance(core, dict):
        raise AtomicResponseError(
            "ATOMIC_RESPONSE_INVALID_CORE", "/rimay_core", "rimay_core must be an object")
    if any("frequency" in response or "repository_trace" in response
           for _, response in _iter_responses(core)):
        raise AtomicResponseError(
            "ATOMIC_RESPONSE_ROLLBACK_LOSSY", "/rimay_core",
            "Atomic Response frequency/trace is not representable by Schema 0.8.0")
    rolled_back["schema_version"] = ACTIVE_CANONICAL_VERSION
    return rolled_back


def quarantine_atomic_responses_for_rollback(document: dict) -> dict:
    quarantined = copy.deepcopy(document)
    if quarantined.get("schema_version") != ATOMIC_RESPONSE_CANDIDATE_VERSION:
        raise AtomicResponseError(
            "ATOMIC_RESPONSE_ROLLBACK_VERSION", "/schema_version",
            f"quarantine input must use {ATOMIC_RESPONSE_CANDIDATE_VERSION}")
    core = quarantined.get("rimay_core")
    if not isinstance(core, dict):
        raise AtomicResponseError(
            "ATOMIC_RESPONSE_INVALID_CORE", "/rimay_core", "rimay_core must be an object")
    records = []
    for path, response in _iter_responses(core):
        additions = {key: response.pop(key) for key in ("frequency", "repository_trace")
                     if key in response}
        if additions:
            records.append({"path": path, "additions": additions,
                            "sha256": _value_sha256(additions)})
    if not records:
        raise AtomicResponseError(
            "ATOMIC_RESPONSE_QUARANTINE_SCOPE", "/rimay_core",
            "at least one Atomic Response addition is required")
    extensions = quarantined.setdefault("extensions", {})
    semantics = extensions.setdefault("additional_semantics", []) \
        if isinstance(extensions, dict) else None
    if not isinstance(semantics, list) or any(
            isinstance(item, dict) and item.get("kind") == _QUARANTINE_KIND
            for item in semantics):
        raise AtomicResponseError(
            "ATOMIC_RESPONSE_QUARANTINE_CONFLICT", "/extensions/additional_semantics",
            "quarantine target is invalid or occupied")
    payload = {"kind": _QUARANTINE_KIND,
               "source_schema_version": ATOMIC_RESPONSE_CANDIDATE_VERSION,
               "records": records}
    payload["records_sha256"] = _value_sha256(records)
    semantics.append(payload)
    quarantined["schema_version"] = ACTIVE_CANONICAL_VERSION
    return quarantined


def restore_quarantined_atomic_responses(document: dict) -> dict:
    restored = copy.deepcopy(document)
    if restored.get("schema_version") != ACTIVE_CANONICAL_VERSION:
        raise AtomicResponseError(
            "ATOMIC_RESPONSE_MIGRATION_VERSION", "/schema_version",
            f"restore input must use {ACTIVE_CANONICAL_VERSION}")
    core, extensions = restored.get("rimay_core"), restored.get("extensions")
    semantics = extensions.get("additional_semantics") if isinstance(extensions, dict) else None
    records = [item for item in semantics or []
               if isinstance(item, dict) and item.get("kind") == _QUARANTINE_KIND]
    if not isinstance(core, dict) or len(records) != 1:
        raise AtomicResponseError(
            "ATOMIC_RESPONSE_QUARANTINE_MISSING", "/extensions/additional_semantics",
            "one Atomic Response quarantine record is required")
    record = records[0]
    required = {"kind", "source_schema_version", "records", "records_sha256"}
    payloads = record.get("records")
    if set(record) != required or \
            record.get("source_schema_version") != ATOMIC_RESPONSE_CANDIDATE_VERSION or \
            not isinstance(payloads, list) or not payloads or \
            record.get("records_sha256") != _value_sha256(payloads):
        raise AtomicResponseError(
            "ATOMIC_RESPONSE_QUARANTINE_INVALID", "/extensions/additional_semantics",
            "quarantine envelope or hash is invalid")
    for index, payload in enumerate(payloads):
        if not isinstance(payload, dict) or set(payload) != {"path", "additions", "sha256"} or \
                payload.get("sha256") != _value_sha256(payload.get("additions")):
            raise AtomicResponseError(
                "ATOMIC_RESPONSE_QUARANTINE_INVALID",
                f"/extensions/additional_semantics/records/{index}",
                "quarantine payload or hash is invalid")
        response = _resolve_response(core, payload["path"])
        additions = payload.get("additions")
        if response is None or not isinstance(additions, dict) or \
                set(additions) - {"frequency", "repository_trace"} or \
                set(additions) & set(response):
            raise AtomicResponseError(
                "ATOMIC_RESPONSE_QUARANTINE_CONFLICT", payload.get("path", "/rimay_core"),
                "restore target is absent or already owns Atomic fields")
        response.update(copy.deepcopy(additions))
        findings = atomic_response_findings(response, path=payload["path"])
        if findings:
            raise AtomicResponseError(
                "ATOMIC_RESPONSE_QUARANTINE_INVALID", payload["path"],
                "restored Atomic Response additions are invalid")
    semantics.remove(record)
    if not semantics:
        extensions.pop("additional_semantics")
    restored["schema_version"] = ATOMIC_RESPONSE_CANDIDATE_VERSION
    return restored


def replay_atomic_response_migration(documents: Iterable[dict]) -> dict:
    migrated = [migrate_requirement_to_atomic_response_candidate(item)
                for item in documents]
    payload = json.dumps(
        migrated, ensure_ascii=False, sort_keys=True, separators=(",", ":")
    ).encode("utf-8")
    return {
        "documents": migrated, "document_count": len(migrated),
        "replay_sha256": "sha256:" + hashlib.sha256(payload).hexdigest(),
    }


def build_atomic_response_candidate_schema(base_schema: dict) -> dict:
    schema = copy.deepcopy(base_schema)
    schema["properties"]["schema_version"]["const"] = ATOMIC_RESPONSE_CANDIDATE_VERSION
    schema["description"] = (
        base_schema.get("description", "") +
        " B5 CAP-ATOMIC-RESPONSE candidate: leaf-local frequencyとAtomic traceは採用前隔離検証。"
    )
    nullable_span = {"oneOf": [{"$ref": "#/$defs/span"}, {"type": "null"}]}
    nullable_string = {"type": ["string", "null"]}
    schema["$defs"]["responseFrequency"] = {
        "type": "object",
        "required": ["value", "unit", "source_expression"],
        "additionalProperties": False,
        "properties": {
            "value": {"type": "number", "exclusiveMinimum": 0},
            "unit": {"enum": ["second", "minute", "hour", "day"]},
            "source_expression": {"type": "string", "minLength": 1},
        },
    }
    schema["$defs"]["repositoryAtomicResponseTrace"] = {
        "type": "object",
        "required": [
            "repository_rule_id", "atomic_response_index", "source_span", "source",
            "modality_origin", "modality_span", "modality_source",
            "negation_span", "negation_source", "frequency_span", "frequency_source",
        ],
        "additionalProperties": False,
        "properties": {
            "repository_rule_id": {"const": "AtomicSystemResponse"},
            "atomic_response_index": {"type": "integer", "minimum": 0},
            "source_span": {"$ref": "#/$defs/span"},
            "source": {"type": "string"},
            "modality_origin": {"enum": ["system_response", "atomic_response"]},
            "modality_span": {"$ref": "#/$defs/span"},
            "modality_source": {"enum": ["must", "shall"]},
            "negation_span": nullable_span,
            "negation_source": nullable_string,
            "frequency_span": nullable_span,
            "frequency_source": nullable_string,
        },
    }
    response = schema["$defs"]["response"]
    response["properties"]["frequency"] = {"$ref": "#/$defs/responseFrequency"}
    response["properties"]["repository_trace"] = {
        "$ref": "#/$defs/repositoryAtomicResponseTrace"}
    return schema
