"""English conformance profileの読込・hash・起動時契約検査（改善計画C3・§19.3・§21.7）。

実行契約のSSOTは profile/english-rimay-conformance.yaml。本moduleは読込時に
fail-closedの契約検査を行い、不整合があれば例外で停止する（黙って既定値へ
流さない）。Parser/Serializer/equivalenceは本moduleのみを経由して束縛を参照する。

profile_content_hash（lexicon.py・Canonical正規化系）は3ファイル母集合を維持する。
本moduleの ``grammar_profile_hash()`` は英語実行契約の4ファイル母集合
（＋official-grammar-keywords.yaml。RC-014追補3で分離）を対象とし、
AST parse_metaとconformance評価にのみ使用する（台帳・Experience Storeへは
波及させない）。
"""
from __future__ import annotations

import hashlib
from functools import lru_cache
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[2]   # prototype/rimay-jp
PROFILE_PATH = ROOT / "profile" / "english-rimay-conformance.yaml"

_FAMILIES = ("CREATE", "STORE", "SEND", "RECEIVE", "DISPLAY",
             "UPDATE", "DELETE", "VERIFY", "CALCULATE", "NOTIFY")


class ProfileContractError(Exception):
    """profile契約違反（起動時fail-closed。§20.1 english_profile.py 完了条件）。"""


@lru_cache(maxsize=1)
def load_profile() -> dict:
    """profileを読込み、契約検査のうえ返す。違反はProfileContractError。"""
    if not PROFILE_PATH.exists():
        raise ProfileContractError(f"missing profile: {PROFILE_PATH}")
    prof = yaml.safe_load(PROFILE_PATH.read_text(encoding="utf-8"))
    problems: list[str] = []

    bindings = prof.get("bindings") or {}
    if set(bindings) != set(_FAMILIES):
        problems.append(f"bindings families mismatch: {sorted(set(bindings) ^ set(_FAMILIES))}")

    verb_owner: dict[str, str] = {}
    for fam, b in bindings.items():
        for field in ("rimay_action_id", "conformance_class", "verbs", "object_role",
                      "roles", "required_roles"):
            if field not in b:
                problems.append(f"{fam}: missing {field}")
        if "emse_rule_id" not in b:
            problems.append(f"{fam}: missing emse_rule_id (nullはRepository拡張として明示する)")
        for v in b.get("verbs") or []:
            if v in verb_owner:
                problems.append(f"verb {v!r} bound to both {verb_owner[v]} and {fam}")
            verb_owner[v] = fam
        roles = b.get("roles") or {}
        for prep in roles:
            if not isinstance(prep, str):
                problems.append(f"{fam}: role preposition key {prep!r} is not a string "
                                "(YAML 1.1のon/off/yes/no boolean化に注意。引用符で明示する)")
        mapped = {spec["role"] for spec in roles.values()}
        for req in b.get("required_roles") or []:
            if req != b.get("object_role") and req not in mapped:
                problems.append(f"{fam}: required role {req} has no preposition mapping")
        for w in (b.get("mustnot_waived_roles") or []):
            if w not in (b.get("required_roles") or []):
                problems.append(f"{fam}: mustnot waiver {w} is not a required role")
        for verb, waived in (b.get("verb_role_waivers") or {}).items():
            if verb not in (b.get("verbs") or []):
                problems.append(f"{fam}: waiver verb {verb} not in verbs")
            for w in waived:
                if w not in (b.get("required_roles") or []):
                    problems.append(f"{fam}: verb waiver {w} is not a required role")

    for e in prof.get("profile_out_verbs") or []:
        if e.get("verb") in verb_owner:
            problems.append(f"profile_out verb {e.get('verb')!r} also bound to {verb_owner[e['verb']]}")

    ops = (prof.get("operators") or {})
    in_set = set(ops.get("in") or [])
    expected_operators = {
        "IS", "EQUALS", "NOT_EQUALS", "GREATER_THAN", "LESS_THAN",
        "GREATER_OR_EQUAL", "LESS_OR_EQUAL", "CONTAINS",
    }
    if in_set != expected_operators:
        problems.append(
            f"operators.in must be the closed eight-operator set: "
            f"{sorted(in_set ^ expected_operators)}")
    if "IS_NOT" in in_set:
        problems.append("IS_NOT is not a canonical operator (CG-01: NOT_EQUALSへ正規化)")
    surfaces = ops.get("surfaces") or {}
    if set(surfaces) != in_set or len(set(surfaces.values())) != len(in_set):
        problems.append("operators.surfaces must map every in operator to one unique surface")
    for e in ops.get("known_out_surfaces") or []:
        if e.get("canonical") in in_set:
            problems.append(f"operator {e.get('canonical')} cannot be both in and known_out")
    if ops.get("classification") != "rimay_jp_extension" or \
            ops.get("extension_feature") != "COMPARISON_OPERATOR" or \
            ops.get("paper_claim") != "withheld":
        problems.append("comparison operator product-extension classification is incomplete")

    values = prof.get("value_expressions") or {}
    if values.get("authority") != "value_expression" or \
            values.get("mutually_exclusive_with_scalar") is not True or \
            values.get("automatic_scalar_lifting") != "forbidden" or \
            values.get("expression_kinds") != ["value", "group", "and", "or"] or \
            values.get("connectors") != {"and": "AND", "or": "OR"} or \
            values.get("binary_form") != "fully_parenthesized" or \
            values.get("aliases") != "reject" or \
            values.get("classification") != "rimay_jp_extension" or \
            values.get("extension_feature") != "MULTI_VALUE" or \
            values.get("paper_claim") != "withheld":
        problems.append("Multi-value product-extension contract is incomplete")

    operator_values = prof.get("operator_value_expressions") or {}
    if operator_values.get("authority") != "operand" or \
            operator_values.get("mutually_exclusive_with_subject") is not True or \
            operator_values.get("typed_operand_requires") != "value_expression" or \
            operator_values.get("automatic_subject_typing") != "forbidden" or \
            operator_values.get("wrappers") != [
                "declared_reference", "instance_or_property", "ui_component_instance"] or \
            operator_values.get("declared_reference_surfaces") != {
                "actor": "actor", "class": "class", "property": "property"} or \
            operator_values.get("instance_or_property_surface") != \
            "instance-or-property" or \
            operator_values.get("ui_component_instance_surface") != "UI-component" or \
            operator_values.get("aliases") != "reject" or \
            operator_values.get("classification") != "rimay_jp_extension" or \
            operator_values.get("extension_feature") != \
            "OPERATOR_VALUE_EXPRESSION" or \
            operator_values.get("paper_claim") != "withheld":
        problems.append("Operator value expression product-extension contract is incomplete")

    lim = prof.get("limits") or {}
    if lim.get("max_conditions") != 1 or lim.get("max_primary_responses") != 1:
        problems.append("limits must be max_conditions=1 / max_primary_responses=1 (§19.3)")

    if problems:
        raise ProfileContractError("; ".join(problems))
    return prof


@lru_cache(maxsize=1)
def grammar_profile_hash() -> str:
    """英語grammar実行契約のhash（RC-014追補3で母集合を分離）。

    従来3資産（supported-profile / case-frames / english-rimay-conformance）に
    **keyword inventory（official-grammar-keywords.yaml）を加えた4ファイル**のhash。
    inventoryはD-17予約語を通じて受理結果を変える実行契約入力のため、
    hash外の隠れ入力にしない（第二読者指摘）。日本語側の
    lexicon.profile_content_hash()（Canonical正規化記録の母集合）は
    従来3ファイルのまま分離維持し、日本語資産へのhash波及を避ける。
    """
    global _GRAMMAR_HASH_CACHE
    if _GRAMMAR_HASH_CACHE is None:
        import hashlib
        from .lexicon import ROOT
        h = hashlib.sha256()
        for rel in ("profile/supported-profile.yaml", "lexicon/case-frames.yaml",
                    "profile/english-rimay-conformance.yaml",
                    "profile/official-grammar-keywords.yaml"):
            h.update((ROOT / rel).read_bytes())
        _GRAMMAR_HASH_CACHE = "sha256:" + h.hexdigest()
    return _GRAMMAR_HASH_CACHE


_GRAMMAR_HASH_CACHE: str | None = None


@lru_cache(maxsize=1)
def verb_index() -> dict:
    """response動詞 → family。"""
    prof = load_profile()
    return {v: fam for fam, b in prof["bindings"].items() for v in b["verbs"]}


@lru_cache(maxsize=1)
def profile_out_verb_index() -> dict:
    prof = load_profile()
    return {e["verb"]: e.get("rimay_action_id") for e in prof.get("profile_out_verbs") or []}


@lru_cache(maxsize=1)
def trigger_verb_index() -> dict:
    """トリガー動詞 → family（press系 + 全binding動詞）。"""
    prof = load_profile()
    idx = dict(verb_index())
    for e in prof.get("trigger_extra_verbs") or []:
        idx[e["verb"]] = e["family"]
    return idx


def binding(family: str) -> dict:
    b = load_profile()["bindings"].get(family)
    if b is None:
        raise ProfileContractError(f"no binding for family {family}")
    return b


@lru_cache(maxsize=1)
def known_out_operator_surfaces() -> dict:
    prof = load_profile()
    return {e["surface"]: e["canonical"]
            for e in (prof.get("operators") or {}).get("known_out_surfaces") or []}


def operators_in() -> set:
    return set((load_profile().get("operators") or {}).get("in") or [])


def operator_surfaces() -> dict[str, str]:
    """Canonical operator → the sole adopted English surface."""
    return dict((load_profile().get("operators") or {}).get("surfaces") or {})


def value_connectors() -> dict[str, str]:
    """Canonical value-expression kind → the sole adopted English connector."""
    return dict((load_profile().get("value_expressions") or {}).get("connectors") or {})


def operator_value_profile() -> dict:
    """Return the closed typed-operand English surface contract."""
    return dict(load_profile().get("operator_value_expressions") or {})


def profile_version() -> str:
    return str(load_profile().get("conformance_profile_version"))
