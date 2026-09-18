"""Rule loader (T032).

Auto-discovers every YAML file under knowledge/layer2/rules/, validates each against
schemas/rule.schema.json, and enforces the governance gates (FR-024):
  - citation present (schema)
  - >=1 positive and >=1 negative example (schema)
  - id in the catalog (no unsupported smell — FR-008)
  - detector.type in the registry (else it would need an engine change)
  - language=ja requires detection_basis (schema)
Any violation raises KnowledgeError (loud failure — the rule cannot ship).
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from ..knowledge_io import KnowledgeError, knowledge_dir, load_yaml, validate_against_schema
from .detectors import REGISTRY


@dataclass(frozen=True)
class Rule:
    id: str
    name: str
    language: str
    quality_attribute: str
    definition: str
    citation: dict
    detector_type: str
    detector_params: dict
    default_severity: str
    explanation_template: str
    positive: list[str]
    negative: list[str]
    glossary: set[str]
    source_path: str

    @property
    def rule_id(self) -> str:
        return f"{self.id}.{self.language}"


def _catalog_ids() -> list[str]:
    catalog = load_yaml(knowledge_dir() / "layer2" / "catalog.yaml")
    return [s["id"] for s in catalog["smells"]]


def _resolve_glossary(ref: str | None) -> set[str]:
    if not ref:
        return set()
    path = knowledge_dir() / "layer2" / ref
    data = load_yaml(path)
    return set(data.get("verbs", []))


def load_rules() -> list[Rule]:
    rules_dir = knowledge_dir() / "layer2" / "rules"
    catalog_ids = set(_catalog_ids())
    rules: list[Rule] = []

    for path in sorted(rules_dir.glob("*.yaml")):
        data = load_yaml(path)
        validate_against_schema(data, "rule.schema.json", source=path.name)

        if data["id"] not in catalog_ids:
            raise KnowledgeError(f"{path.name}: smell id '{data['id']}' not in catalog (FR-008)")
        detector = data["detector"]
        if detector["type"] not in REGISTRY:
            raise KnowledgeError(
                f"{path.name}: detector type '{detector['type']}' has no engine primitive"
            )

        glossary_ref = detector.get("params", {}).get("glossary_ref")
        rules.append(
            Rule(
                id=data["id"],
                name=data["name"],
                language=data["language"],
                quality_attribute=data["quality_attribute"],
                definition=data["definition"],
                citation=data["citation"],
                detector_type=detector["type"],
                detector_params=detector.get("params", {}),
                default_severity=data["default_severity"],
                explanation_template=data["explanation_template"],
                positive=list(data["examples"]["positive"]),
                negative=list(data["examples"]["negative"]),
                glossary=_resolve_glossary(glossary_ref),
                source_path=str(Path("knowledge/layer2/rules") / path.name),
            )
        )

    if not rules:
        raise KnowledgeError("No rules found under knowledge/layer2/rules/")
    return rules
