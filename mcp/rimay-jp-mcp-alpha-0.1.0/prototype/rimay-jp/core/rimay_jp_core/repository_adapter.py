"""Repository構文木 → Canonical候補の明示登録adapter境界。

汎用fallbackや規則名による推測は置かない。構文木のroot規則ごとにadapterを登録し、
曖昧性・semantic linkingの前提をadapter自身が宣言する。出力はValidator前のcandidateであり、
Canonical確定値を自称しない。
"""
from __future__ import annotations

import copy
import hashlib
from dataclasses import dataclass
from typing import Callable

from .repository_grammar import (
    GrammarIR, SyntaxParseResult, syntax_tree_problems, syntax_tree_signature,
)
from .repository_linker import SemanticLinkResult, link_repository_syntax


PROJECTION_STATUSES = frozenset({
    "adapted_candidate", "syntax_not_accepted", "unsupported_root_rule",
    "ambiguity_check_required", "ambiguous_syntax", "semantic_linking_required",
    "semantic_linking_failed", "adapter_scope_unsupported", "adapter_contract_error",
})


class AdapterScopeUnsupported(ValueError):
    """Valid Repository document whose cardinality/scope cannot map to one Canonical."""


@dataclass(frozen=True)
class AdapterPayload:
    canonical_candidate: dict
    unresolved_paths: tuple[str, ...]


@dataclass(frozen=True)
class AdapterSpec:
    adapter_id: str
    root_rule: str
    project: Callable[[dict, str, SemanticLinkResult | None], AdapterPayload]
    requires_ambiguity_check: bool = True
    requires_semantic_linking: bool = True


@dataclass(frozen=True)
class ProjectionResult:
    status: str
    root_rule: str
    adapter_id: str | None
    canonical_candidate: dict | None
    unresolved_paths: tuple[str, ...]
    validation_required: bool
    reason: str

    def __post_init__(self) -> None:
        if self.status not in PROJECTION_STATUSES:
            raise ValueError(f"unknown projection status: {self.status}")


class RepositoryCanonicalAdapterRegistry:
    """root rule単位の閉じたadapter registry。"""

    def __init__(self) -> None:
        self._specs: dict[str, AdapterSpec] = {}

    @property
    def registered_roots(self) -> tuple[str, ...]:
        return tuple(sorted(self._specs))

    def register(self, spec: AdapterSpec) -> None:
        if not isinstance(spec.adapter_id, str) or not spec.adapter_id:
            raise ValueError("adapter_id must be a non-empty string")
        if not isinstance(spec.root_rule, str) or not spec.root_rule:
            raise ValueError("root_rule must be a non-empty string")
        if not callable(spec.project):
            raise ValueError("project must be callable")
        if type(spec.requires_ambiguity_check) is not bool or \
                type(spec.requires_semantic_linking) is not bool:
            raise ValueError("adapter preconditions must be bool")
        if spec.root_rule in self._specs:
            raise ValueError(f"adapter already registered for root rule {spec.root_rule}")
        if any(existing.adapter_id == spec.adapter_id for existing in self._specs.values()):
            raise ValueError(f"adapter_id already registered: {spec.adapter_id}")
        self._specs[spec.root_rule] = spec

    def project(self, parsed: SyntaxParseResult, source_text: str,
                linking: SemanticLinkResult | None = None,
                grammar: GrammarIR | None = None) -> ProjectionResult:
        root = parsed.start_rule
        if not parsed.accepted or parsed.tree is None:
            return ProjectionResult(
                "syntax_not_accepted", root, None, None, (), True,
                "Repository Grammarのfull matchが成立していない")
        tree_problems = syntax_tree_problems(parsed.tree, source_text, expected_root=root)
        if tree_problems:
            return ProjectionResult(
                "adapter_contract_error", root, None, None, (), True,
                "parse resultのsyntax tree契約違反: " + "; ".join(tree_problems))
        if linking is not None:
            source_sha = "sha256:" + hashlib.sha256(source_text.encode("utf-8")).hexdigest()
            link_mismatch = not isinstance(linking, SemanticLinkResult) or \
                linking.start_rule != root or \
                linking.grammar_ir_signature != parsed.grammar_ir_signature or \
                linking.grammar_source_sha256 != parsed.grammar_source_sha256 or \
                linking.syntax_tree_sha256 != syntax_tree_signature(parsed.tree) or \
                linking.source_sha256 != source_sha or parsed.source_sha256 != source_sha
            if link_mismatch:
                return ProjectionResult(
                    "adapter_contract_error", root, None, None, (), True,
                    "semantic link result is not bound to this parse result/source")
            if not isinstance(grammar, GrammarIR):
                return ProjectionResult(
                    "semantic_linking_required", root, None, None, (), True,
                    "semantic link resultの独立再導出にGrammar IRが必要")
            recomputed = link_repository_syntax(grammar, parsed, source_text)
            if recomputed != linking:
                return ProjectionResult(
                    "adapter_contract_error", root, None, None, (), True,
                    "semantic link result does not match independent recomputation")
        spec = self._specs.get(root)
        if spec is None:
            return ProjectionResult(
                "unsupported_root_rule", root, None, None, (), True,
                "root ruleに明示adapterが登録されていない")
        if spec.requires_ambiguity_check and not parsed.ambiguity_checked:
            return ProjectionResult(
                "ambiguity_check_required", root, spec.adapter_id, None, (), True,
                "adapterが要求する構文derivation一意性を確認していない")
        if spec.requires_ambiguity_check and parsed.ambiguity_detected is not False:
            return ProjectionResult(
                "ambiguous_syntax", root, spec.adapter_id, None, (), True,
                "Repository Grammar IR上で複数のfull-match derivationが成立する")
        if spec.requires_semantic_linking and (linking is None or not linking.checked or
                                               not isinstance(grammar, GrammarIR)):
            return ProjectionResult(
                "semantic_linking_required", root, spec.adapter_id, None, (), True,
                "adapterが要求するcross-reference linkingを確認していない")
        if spec.requires_semantic_linking and not linking.succeeded:
            return ProjectionResult(
                "semantic_linking_failed", root, spec.adapter_id, None, (), True,
                "cross-reference linkingに未解決・曖昧・型不一致が残っている")
        try:
            payload = spec.project(copy.deepcopy(parsed.tree), source_text,
                                   copy.deepcopy(linking))
        except AdapterScopeUnsupported as exc:
            return ProjectionResult(
                "adapter_scope_unsupported", root, spec.adapter_id, None, (), True,
                str(exc))
        except Exception as exc:  # adapter境界で構造化し、candidateを漏らさない
            return ProjectionResult(
                "adapter_contract_error", root, spec.adapter_id, None, (), True,
                f"adapter raised {type(exc).__name__}: {exc}")
        if not isinstance(payload, AdapterPayload) or \
                not isinstance(payload.canonical_candidate, dict) or \
                any(not isinstance(path, str) or not path.startswith("/")
                    for path in payload.unresolved_paths) or \
                len(set(payload.unresolved_paths)) != len(payload.unresolved_paths):
            return ProjectionResult(
                "adapter_contract_error", root, spec.adapter_id, None, (), True,
                "adapter output does not satisfy AdapterPayload contract")
        return ProjectionResult(
            "adapted_candidate", root, spec.adapter_id,
            copy.deepcopy(payload.canonical_candidate), tuple(payload.unresolved_paths), True,
            "Canonical Schema/Validatorと人間確認をまだ通していないcandidate")
