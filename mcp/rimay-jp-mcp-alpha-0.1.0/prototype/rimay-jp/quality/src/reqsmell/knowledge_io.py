"""YAML + JSON-Schema loading utilities (T006).

Resolves the repository's knowledge/ and schemas/ trees, loads YAML, and validates
documents against a JSON Schema. Fails loudly (raises) on invalid data so a malformed
knowledge asset can never ship silently (FR-024, Constitution V).
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import jsonschema
import yaml


class KnowledgeError(RuntimeError):
    """Raised when a knowledge-asset file is missing or invalid."""


def repo_root() -> Path:
    """Project root = three levels up from this file (src/reqsmell/knowledge_io.py)."""
    return Path(__file__).resolve().parents[2]


def knowledge_dir() -> Path:
    return repo_root() / "knowledge"


def schemas_dir() -> Path:
    return repo_root() / "schemas"


def load_yaml(path: Path) -> Any:
    if not path.exists():
        raise KnowledgeError(f"Knowledge file not found: {path}")
    with path.open("r", encoding="utf-8") as fh:
        return yaml.safe_load(fh)


def load_schema(name: str) -> dict:
    path = schemas_dir() / name
    if not path.exists():
        raise KnowledgeError(f"Schema not found: {path}")
    with path.open("r", encoding="utf-8") as fh:
        return json.load(fh)


def validate_against_schema(data: Any, schema_name: str, *, source: str) -> None:
    """Validate ``data`` against ``schema_name``; raise KnowledgeError on failure."""
    schema = load_schema(schema_name)
    try:
        jsonschema.validate(instance=data, schema=schema)
    except jsonschema.ValidationError as exc:  # pragma: no cover - message formatting
        loc = "/".join(str(p) for p in exc.absolute_path) or "<root>"
        raise KnowledgeError(
            f"{source} failed schema '{schema_name}' at {loc}: {exc.message}"
        ) from exc
