"""Lossless bridge from a narrow native Canonical slice to Repository Rimay.

The bridge is deliberately smaller than either language.  It does not parse or
rewrite the product English serializer output.  It accepts only a plain SEND
response whose references can be declared from existing dictionary facts, and
fails closed for conditions, inferred property ownership, and other structures.
"""
from __future__ import annotations

import re

from .lexicon import term_ids
from .model import canonical_hash


BRIDGE_VERSION = "0.1.0"
BRIDGE_ORIGIN = "rimay_jp_repository_bridge"

_IDENTIFIER = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*$")
_RESPONSE_KEYS = frozenset({"action", "actor", "destination", "modality", "theme"})


def _unique(values: list[str]) -> list[str]:
    return list(dict.fromkeys(values))


def _fallback(reason_codes: list[str], diagnostics: list[dict]) -> dict:
    return {
        "bridge_version": BRIDGE_VERSION,
        "status": "fallback_required",
        "lossless": False,
        "reason_codes": _unique(reason_codes),
        "resolved_codes": [],
        "candidate_origin": None,
        "repository_candidate": None,
        "synthesized_declarations": [],
        "trace": [],
        "diagnostics": diagnostics,
        "preserve_native_candidate": True,
    }


def _term(term_id: object) -> dict | None:
    if not isinstance(term_id, str):
        return None
    return term_ids().get(term_id)


def build_repository_candidate(canonical: dict) -> dict:
    """Build one fixed-Grammar candidate or return an explicit fallback.

    Demo-ready scope:

    * one condition-free, scope-free ``SEND_11_1_1`` response;
    * ``MUST`` or ``MUST_NOT`` modality;
    * actor and class declarations derived from dictionary types;
    * no owner-class inference for a ``property`` term;
    * no conversion of a reference into a quoted literal.
    """
    reasons: list[str] = []
    diagnostics: list[dict] = []

    if not isinstance(canonical, dict):
        return _fallback(
            ["INVALID_CANONICAL_INPUT"],
            [{"code": "INVALID_CANONICAL_INPUT", "path": "", "value": canonical}],
        )
    core = canonical.get("rimay_core")
    if not isinstance(core, dict):
        return _fallback(
            ["INVALID_CANONICAL_INPUT"],
            [{"code": "INVALID_CANONICAL_INPUT", "path": "/rimay_core"}],
        )

    if core.get("scope") is not None:
        reasons.append("SCOPE_STRUCTURE_UNSUPPORTED")
        diagnostics.append({"code": reasons[-1], "path": "/rimay_core/scope"})

    conditions = core.get("conditions") or []
    if conditions:
        trigger = any(
            isinstance(condition, dict)
            and (condition.get("type") == "WHEN" or condition.get("event") is not None)
            for condition in conditions
        )
        code = "TRIGGER_SHAPE_INCOMPATIBLE" if trigger else "CONDITION_STRUCTURE_UNSUPPORTED"
        reasons.append(code)
        diagnostics.append({"code": code, "path": "/rimay_core/conditions"})

    for field in ("response_expression", "response_block"):
        if core.get(field) is not None:
            reasons.append("MULTI_RESPONSE_STRUCTURE_UNSUPPORTED")
            diagnostics.append({"code": reasons[-1], "path": f"/rimay_core/{field}"})

    extensions = canonical.get("extensions")
    if isinstance(extensions, dict) and extensions:
        reasons.append("EXTENSIONS_UNSUPPORTED")
        diagnostics.append({"code": reasons[-1], "path": "/extensions"})

    response = core.get("response")
    if not isinstance(response, dict):
        reasons.append("SIMPLE_RESPONSE_REQUIRED")
        diagnostics.append({"code": reasons[-1], "path": "/rimay_core/response"})
        return _fallback(reasons, diagnostics)

    unexpected = sorted(
        key for key, value in response.items()
        if key not in _RESPONSE_KEYS and value is not None
    )
    if unexpected:
        reasons.append("OPTIONAL_SEND_ROLE_UNSUPPORTED")
        diagnostics.append({
            "code": reasons[-1],
            "path": "/rimay_core/response",
            "fields": unexpected,
        })

    action = response.get("action")
    if not isinstance(action, dict) or action.get("family") != "SEND" or \
            action.get("rimay_action_id") != "SEND_11_1_1":
        reasons.append("ACTION_NOT_BRIDGEABLE")
        diagnostics.append({
            "code": reasons[-1],
            "path": "/rimay_core/response/action",
            "expected_family": "SEND",
            "expected_rule_id": "SEND_11_1_1",
        })

    modality = response.get("modality")
    if modality not in {"MUST", "MUST_NOT"}:
        reasons.append("MODALITY_NOT_BRIDGEABLE")
        diagnostics.append({
            "code": reasons[-1],
            "path": "/rimay_core/response/modality",
            "value": modality,
        })

    references = (
        ("actor", "/rimay_core/response/actor", "actor"),
        ("theme", "/rimay_core/response/theme", "class"),
        ("destination", "/rimay_core/response/destination", "actor_or_class"),
    )
    resolved: dict[str, tuple[str, str]] = {}
    for field, path, expected in references:
        value = response.get(field)
        entry = _term(value)
        if entry is None:
            code = "REFERENCE_TERM_UNAVAILABLE"
            reasons.append(code)
            diagnostics.append({"code": code, "path": path, "term_id": value})
            continue
        term_type = entry.get("type")
        resolved[field] = (value, term_type)
        if not _IDENTIFIER.fullmatch(value):
            code = "REFERENCE_IDENTIFIER_UNSAFE"
            reasons.append(code)
            diagnostics.append({"code": code, "path": path, "term_id": value})
        if term_type == "property":
            code = "PROPERTY_OWNER_UNRESOLVED"
            reasons.append(code)
            diagnostics.append({
                "code": code,
                "path": path,
                "term_id": value,
                "term_type": term_type,
                "owner_class": None,
            })
        elif expected == "actor" and term_type != "actor":
            code = "REFERENCE_TYPE_INCOMPATIBLE"
            reasons.append(code)
            diagnostics.append({
                "code": code, "path": path, "term_id": value,
                "term_type": term_type, "expected_types": ["actor"],
            })
        elif expected == "class" and term_type != "class":
            code = "REFERENCE_TYPE_INCOMPATIBLE"
            reasons.append(code)
            diagnostics.append({
                "code": code, "path": path, "term_id": value,
                "term_type": term_type, "expected_types": ["class"],
            })
        elif expected == "actor_or_class" and term_type not in {"actor", "class"}:
            code = "REFERENCE_TYPE_INCOMPATIBLE"
            reasons.append(code)
            diagnostics.append({
                "code": code, "path": path, "term_id": value,
                "term_type": term_type, "expected_types": ["actor", "class"],
            })

    if reasons:
        return _fallback(reasons, diagnostics)

    actor = resolved["actor"][0]
    theme = resolved["theme"][0]
    destination, destination_type = resolved["destination"]

    actor_ids = _unique([actor] + ([destination] if destination_type == "actor" else []))
    class_ids = _unique([theme] + ([destination] if destination_type == "class" else []))
    declaration_parts = []
    if actor_ids:
        declaration_parts.append(
            "Actors: " + ", ".join(f"actor {term_id}" for term_id in actor_ids)
        )
    if class_ids:
        declaration_parts.append(
            "Classes: " + ", ".join(f"class {term_id}" for term_id in class_ids)
        )
    prefix = " ".join(declaration_parts)
    modal = "must not" if modality == "MUST_NOT" else "must"
    response_surface = f"{actor} {modal} send {theme} to {destination}."
    candidate = f"{prefix} {response_surface}"
    response_start = len(prefix) + 1

    trace = []
    search_start = response_start
    for field, path in (("actor", "/rimay_core/response/actor"),
                        ("theme", "/rimay_core/response/theme"),
                        ("destination", "/rimay_core/response/destination")):
        value = resolved[field][0]
        start = candidate.index(value, search_start)
        end = start + len(value)
        trace.append({
            "canonical_path": path,
            "source_value": value,
            "candidate_surface": value,
            "candidate_span": {"start": start, "end": end},
            "transformation": "typed_identifier_reference",
        })
        search_start = end

    declaration_paths: dict[str, list[str]] = {}
    for field, path, _ in references:
        declaration_paths.setdefault(resolved[field][0], []).append(path)
    synthesized = [
        {
            "declaration_rule": "Actor" if term_id in actor_ids else "Class",
            "name": term_id,
            "source_paths": declaration_paths[term_id],
        }
        for term_id in actor_ids + class_ids
    ]

    return {
        "bridge_version": BRIDGE_VERSION,
        "status": "bridge_ready",
        "lossless": True,
        "reason_codes": [],
        "resolved_codes": [
            "DECLARATION_SYNTHESIZED",
            "REFERENCE_SURFACE_NORMALIZED",
            "PRODUCT_SERIALIZER_BYPASSED",
        ],
        "candidate_origin": BRIDGE_ORIGIN,
        "repository_candidate": candidate,
        "synthesized_declarations": synthesized,
        "trace": trace,
        "diagnostics": [],
        "preserve_native_candidate": True,
        "canonical_source_signature": canonical_hash(canonical),
    }
