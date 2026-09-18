"""Per-type rule loader (T038).

Discovers new-format rule files under ``knowledge/layer2/<type>/rules/`` and the cross-cutting
``knowledge/layer2/general/rules/``, validates each against ``schemas/rule.v2.schema.json``, and
resolves the source-gating verdict via the SourceResolver:

* ``implementable: judgment`` → DEFERRED (loaded, shape-checked, never executed — FR-039).
* a standard/notation definition without a paper method → DEFERRED (FR-040).
* an unresolvable / non-retained / method-role definition source → rejected or deferred (FR-024/FR-042/FR-046).

A *shippable* rule additionally requires a detector type present in the engine REGISTRY.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from ..knowledge_io import KnowledgeError, knowledge_dir, load_yaml, validate_against_schema
from ..models import UncheckedReason
from ..sources.resolver import SourceResolver, load_source_resolver
from .detectors import REGISTRY


@dataclass(frozen=True)
class RuleV2:
    id: str
    name: str
    artifact_type: str
    language: str
    quality_attribute: str
    definition: str
    definition_source_id: str
    method_source_id: str | None
    implementable: str
    detector_type: str | None
    detector_params: dict
    default_severity: str
    explanation_template: str
    positive: list[str]
    negative: list[str]
    ships: bool
    defer_reason: str | None       # UncheckedReason value when not shipping
    source_path: str

    @property
    def rule_id(self) -> str:
        return f"{self.artifact_type}/{self.id}.{self.language}"

    @property
    def catalog(self) -> str:
        return "general" if self.artifact_type == "general" else "type"


def _rules_dir(sub: str) -> Path:
    return knowledge_dir() / "layer2" / sub / "rules"


def _load_dir(sub: str, resolver: SourceResolver) -> list[RuleV2]:
    d = _rules_dir(sub)
    if not d.exists():
        return []
    out: list[RuleV2] = []
    for path in sorted(d.glob("*.yaml")):
        data = load_yaml(path)
        validate_against_schema(data, "rule.v2.schema.json", source=path.name)
        implementable = data["implementable"]
        method_id = data.get("method_source_id")

        if implementable == "judgment":
            ships, reason = False, UncheckedReason.DEFERRED_JUDGMENT.value
        else:
            ok, why = resolver.layer2_rule_ships(data["definition_source_id"], method_id)
            if ok:
                det = data.get("detector", {}).get("type")
                if det not in REGISTRY:
                    raise KnowledgeError(
                        f"{path.name}: detector type '{det}' has no engine primitive (FR-022)"
                    )
                ships, reason = True, None
            else:
                ships, reason = False, UncheckedReason.PENDING_SOURCE.value

        det = data.get("detector") or {}
        out.append(
            RuleV2(
                id=data["id"],
                name=data["name"],
                artifact_type=data["artifact_type"],
                language=data["language"],
                quality_attribute=data["quality_attribute"],
                definition=data["definition"],
                definition_source_id=data["definition_source_id"],
                method_source_id=method_id,
                implementable=implementable,
                detector_type=det.get("type"),
                detector_params=det.get("params", {}),
                default_severity=data["default_severity"],
                explanation_template=data["explanation_template"],
                positive=list(data["examples"]["positive"]),
                negative=list(data["examples"]["negative"]),
                ships=ships,
                defer_reason=reason,
                source_path=str(Path("knowledge/layer2") / sub / "rules" / path.name),
            )
        )
    return out


def load_typed_rules(
    artifact_type: str, resolver: SourceResolver | None = None
) -> list[RuleV2]:
    """All rules applicable to ``artifact_type``: its own catalog + the general catalog."""
    resolver = resolver or load_source_resolver()
    rules = _load_dir(artifact_type, resolver) + _load_dir("general", resolver)
    return rules
