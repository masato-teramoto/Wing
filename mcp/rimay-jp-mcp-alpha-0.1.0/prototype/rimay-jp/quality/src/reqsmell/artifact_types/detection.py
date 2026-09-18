"""Deterministic artifact-type + language resolution (T034; FR-019/FR-033/FR-034).

Resolution order for type: **declared > detected > indeterminate**. Detection uses fixed
surface-cue rules (no ML/LLM — FR-039); when no cue matches and nothing was declared, the
type is reported INDETERMINATE rather than guessed. Language reuses the existing detector.
"""

from __future__ import annotations

import re

from ..layer2.language import detect_language
from ..models import ArtifactType, Language, TypeResolution

# Ordered, most-specific-first surface cues. Each returns True/False deterministically.
_USER_STORY_RE = re.compile(r"\bas\s+an?\b.*\bi\s+(want|need|would\s+like|wish)\b",
                            re.IGNORECASE | re.DOTALL)
_GLOSSARY_RE = re.compile(r"^\s*[\w][\w \-/]{0,48}:\s+\S")
_NON_OBLIGATION_MODAL_RE = re.compile(
    r"\b(must\s+not|shall\s+not|may\s+not|may|is\s+(prohibited|permitted|required)\s+to)\b",
    re.IGNORECASE,
)
_EARS_RE = re.compile(r"^\s*(when|while|where|if|given)\b", re.IGNORECASE)
_RESPONSE_RE = re.compile(r"\b(shall|must)\b", re.IGNORECASE)
_NFR_ATTR_RE = re.compile(
    r"\b(performance|latency|throughput|availability|uptime|response\s+time|scalab|secur|"
    r"reliab|usab|maintainab|portab)\w*\b",
    re.IGNORECASE,
)
_NUMBER_RE = re.compile(r"\d")


def detect_artifact_type(text: str) -> ArtifactType | None:
    """Return the detected type, or None if no cue matches (→ indeterminate)."""
    if _USER_STORY_RE.search(text):
        return ArtifactType.USER_STORY
    if _GLOSSARY_RE.search(text) and _RESPONSE_RE.search(text) is None:
        return ArtifactType.GLOSSARY_TERM
    # Quality attribute + a measurable number, without behavioural shall/actor pattern → NFR.
    if _NFR_ATTR_RE.search(text) and _NUMBER_RE.search(text):
        return ArtifactType.NON_FUNCTIONAL
    # Prohibition/permission modality strongly signals a business rule / constraint.
    if _NON_OBLIGATION_MODAL_RE.search(text):
        return ArtifactType.CONSTRAINT
    if _EARS_RE.search(text) and _RESPONSE_RE.search(text):
        return ArtifactType.ACCEPTANCE_CRITERIA
    if _RESPONSE_RE.search(text):
        return ArtifactType.FUNCTIONAL
    return None


def resolve(
    text: str,
    declared_type: str | None = None,
    declared_language: str | None = None,
) -> tuple[ArtifactType | None, TypeResolution, Language]:
    """Resolve (artifact_type, type_resolution, language) deterministically.

    declared_type wins (FR-033); else detection; else INDETERMINATE (FR-034).
    Raises ValueError for an unknown declared_type.
    """
    if declared_type:
        try:
            at = ArtifactType(declared_type)
        except ValueError as exc:
            raise ValueError(f"Unknown artifact_type '{declared_type}'") from exc
        resolution = TypeResolution.DECLARED
    else:
        at = detect_artifact_type(text)
        resolution = TypeResolution.DETECTED if at is not None else TypeResolution.INDETERMINATE
    language = detect_language(text, declared_language)
    return at, resolution, language
