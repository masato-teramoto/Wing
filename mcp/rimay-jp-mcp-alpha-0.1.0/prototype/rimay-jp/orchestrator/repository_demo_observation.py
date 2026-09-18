"""Privacy-bounded, non-persistent observations for the dialogue demo."""
from __future__ import annotations

import hashlib
import json


OBSERVATION_VERSION = "0.1.0"
_PRIVACY_MODES = frozenset({"synthetic", "redacted", "restricted_raw"})


def _signature(value: object) -> str:
    encoded = json.dumps(
        value, ensure_ascii=False, sort_keys=True, separators=(",", ":")
    ).encode("utf-8")
    return "sha256:" + hashlib.sha256(encoded).hexdigest()


def _text_signature(value: str) -> str:
    return "sha256:" + hashlib.sha256(value.encode("utf-8")).hexdigest()


def _require_tool(value: dict, tool: str) -> None:
    if not isinstance(value, dict) or value.get("tool") != tool:
        raise ValueError(f"expected {tool} response")


def _restricted_controls(controls: dict | None) -> dict:
    if not isinstance(controls, dict) or controls.get("explicit_consent") is not True:
        raise ValueError("restricted_raw requires explicit_consent=true")
    required_text = ("purpose", "deletion_condition")
    if any(not isinstance(controls.get(key), str) or not controls[key].strip()
           for key in required_text):
        raise ValueError(
            "restricted_raw requires purpose and deletion_condition"
        )
    principals = controls.get("authorized_principals")
    if not isinstance(principals, list) or not principals or not all(
            isinstance(item, str) and item.strip() for item in principals):
        raise ValueError(
            "restricted_raw requires non-empty authorized_principals"
        )
    return {
        "explicit_consent": True,
        "purpose": controls["purpose"],
        "authorized_principals": principals,
        "deletion_condition": controls["deletion_condition"],
    }


def build_repository_demo_observation(
    session_id: str,
    turn_id: str,
    analysis_response: dict,
    evaluation_response: dict,
    *,
    privacy_mode: str = "redacted",
    source_text_ja: str | None = None,
    rimay_candidate: str | None = None,
    model_id: str | None = None,
    prompt_version: str | None = None,
    next_question_ja: str | None = None,
    user_accepted_candidate: bool | None = None,
    retry_count: int = 0,
    restricted_raw_controls: dict | None = None,
) -> dict:
    """Build an export envelope without writing or changing product state."""
    if not isinstance(session_id, str) or not session_id:
        raise ValueError("session_id must be a non-empty string")
    if not isinstance(turn_id, str) or not turn_id:
        raise ValueError("turn_id must be a non-empty string")
    if privacy_mode not in _PRIVACY_MODES:
        raise ValueError(f"unknown privacy_mode: {privacy_mode!r}")
    if type(retry_count) is not int or retry_count < 0:
        raise ValueError("retry_count must be a non-negative integer")
    if user_accepted_candidate is not None and \
            type(user_accepted_candidate) is not bool:
        raise ValueError("user_accepted_candidate must be boolean or null")
    _require_tool(analysis_response, "analyze_japanese_requirement")
    _require_tool(evaluation_response, "evaluate_rimay_candidate")

    candidate = evaluation_response["candidate"]
    if rimay_candidate is not None and \
            _text_signature(rimay_candidate) != candidate["rimay_candidate_sha256"]:
        raise ValueError("rimay_candidate does not match evaluation response")
    supplied_source_signature = (
        _text_signature(source_text_ja) if source_text_ja is not None else None
    )
    if supplied_source_signature is not None \
            and candidate["source_text_ja_sha256"] is not None \
            and supplied_source_signature != candidate["source_text_ja_sha256"]:
        raise ValueError("source_text_ja does not match evaluation response")

    if privacy_mode == "restricted_raw":
        controls = _restricted_controls(restricted_raw_controls)
    else:
        if restricted_raw_controls is not None:
            raise ValueError(
                "restricted_raw_controls are only valid for restricted_raw"
            )
        controls = None

    retain_raw = privacy_mode in {"synthetic", "restricted_raw"}
    if retain_raw and (source_text_ja is None or rimay_candidate is None):
        raise ValueError(
            f"{privacy_mode} requires source_text_ja and rimay_candidate"
        )

    native = analysis_response["native_analysis"]
    repository = evaluation_response["repository_projection"]
    assignment_names = list(dict.fromkeys(
        assignment.get("feature")
        for action in repository.get("action_facts", [])
        for assignment in action.get("assignments", [])
        if isinstance(assignment.get("feature"), str)
    ))
    observation = {
        "observation_version": OBSERVATION_VERSION,
        "session_id": session_id,
        "turn_id": turn_id,
        "privacy": {
            "mode": privacy_mode,
            "raw_text_retained": retain_raw,
            "export_review": (
                "required_before_repository_commit"
                if privacy_mode == "synthetic"
                else "not_applicable_no_raw"
                if privacy_mode == "redacted"
                else "required_controlled_storage"
            ),
            "repository_commit": (
                "reviewed_sanitized_fixture_only"
                if privacy_mode != "restricted_raw" else "forbidden"
            ),
        },
        "normalizer": {
            "request_signature": analysis_response["input_signature"],
            "source_text_ja_sha256": (
                candidate["source_text_ja_sha256"] or supplied_source_signature
            ),
            "profile_version": native["profile_version"],
            "status": native["status"],
            "finding_codes": list(dict.fromkeys(
                finding.get("code") for finding in native.get("findings", [])
                if isinstance(finding.get("code"), str)
            )),
        },
        "llm": {
            "model_id": model_id,
            "prompt_version": prompt_version,
            "candidate_origin": candidate["origin"],
            "rimay_candidate_sha256": candidate["rimay_candidate_sha256"],
        },
        "rimay_jp": {
            "version": evaluation_response["provenance"]["rimay_jp_version"],
            "request_signature": evaluation_response["input_signature"],
            "response_signature": _signature(evaluation_response),
            "parser_status": evaluation_response["parser"]["status"],
            "action_rule_ids": evaluation_response["parser"][
                "selected_action_rule_ids"
            ],
            "assignment_names": assignment_names,
            "linking_status": evaluation_response["linking"]["status"],
            "residual_mapping_ids": evaluation_response["canonical_projection"][
                "residual_mapping_ids"
            ],
        },
        "dialogue": {
            "retry_count": retry_count,
            "next_question_present": next_question_ja is not None,
            "user_accepted_candidate": user_accepted_candidate,
        },
        "non_intervention": {
            "persistent_write_performed": False,
            "parser_response_dependency": False,
            "automatic_product_update": False,
        },
    }
    if controls is not None:
        observation["privacy"]["restricted_raw_controls"] = controls
    if retain_raw:
        observation["source_text_ja"] = source_text_ja
        observation["llm"]["rimay_candidate"] = rimay_candidate
        observation["dialogue"]["next_question_ja"] = next_question_ja
    return observation
