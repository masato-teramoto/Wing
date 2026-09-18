#!/usr/bin/env python3
"""Rimay-JP MCP Adapter（Phase 5、PoC継続条件⑤。llm-backend-design v0.5 §6のツール群）。

- 本Adapterは**状態・独自正本を持たない**（ADR-0012 D2: MCPはCoreを公開するAdapter）。
  全ツールはrimay-jp-core／orchestrator／generatorsの既存関数への薄い委譲であり、
  CLI・CI・Library・MCPの全経路が同一のSSOT（Supported Profile・辞書・Rule）を使う。
- ハンドラは`mcp`ライブラリへ依存しない素の関数として定義し（quality adapterと同型）、
  MCPトランスポートが必要な場合のみ serve() が遅延importでFastMCPへ登録する。
- 統制はツールの内側で担保される: 確定はapply_canonical_patchの根拠検査のみ、
  LLM候補はproposed、表層はSerializerが再生成、合否判定はツール側（§8統制点）。

§6ツール対応（コア・検証／知識・対話／下流・還流）＋統合拡張2件
（validate_all_layers=Step 4 Validation Report、plan_repairs=Step 5修復計画）。
"""
from __future__ import annotations

import copy
import sys
from pathlib import Path

_RIMAY = Path(__file__).resolve().parents[2]  # prototype/rimay-jp
for p in (str(_RIMAY / "core"), str(_RIMAY)):
    if p not in sys.path:
        sys.path.insert(0, p)

from rimay_jp_core import SCHEMA_VERSION, PROFILE_VERSION, MVP_CONDITIONS  # noqa: E402
from rimay_jp_core.normalizer import normalize as _normalize  # noqa: E402
from rimay_jp_core.validator import validate as _validate  # noqa: E402
from rimay_jp_core.schema_check import validate_schema  # noqa: E402
from rimay_jp_core.serializer import render_requirement_views as _render  # noqa: E402
from rimay_jp_core.parser import parse as _parse, ParseError  # noqa: E402
from rimay_jp_core.equivalence import compare, check_sidecar  # noqa: E402
from rimay_jp_core.patch import apply_canonical_patch as _apply_patch  # noqa: E402
from rimay_jp_core.response_expression import iter_core_responses  # noqa: E402
from rimay_jp_core.english_profile import operators_in, value_connectors  # noqa: E402
from rimay_jp_core.lexicon import (lookup_jp, case_frames, knowledge_bank,  # noqa: E402
                                   versions)
from rimay_jp_core.vocabulary import (  # noqa: E402
    VocabularyRegistry, effective_terms, project_terms, vocabulary_operation)
from orchestrator.information_classifier import classify as _classify  # noqa: E402
from orchestrator.candidate_extractor import extract as _extract  # noqa: E402
from orchestrator.knowledge_router import route as _route  # noqa: E402
from orchestrator.question_planner import plan as _plan_questions  # noqa: E402
from orchestrator.answer_updater import apply_answer as _apply_answer  # noqa: E402
from orchestrator.validation_router import validate_all as _validate_all  # noqa: E402
from orchestrator.repair_planner import plan_repairs as _plan_repairs  # noqa: E402
from orchestrator.feedback_handler import handle as _handle_feedback  # noqa: E402
from orchestrator.llm_adapter import _ALLOWED_POINTERS  # noqa: E402
from orchestrator.repository_demo import (  # noqa: E402
    analyze_japanese_requirement as _analyze_japanese_requirement,
    evaluate_rimay_candidate as _evaluate_rimay_candidate,
    get_repository_parser_capabilities as _get_repository_parser_capabilities,
    get_repository_rule_details as _get_repository_rule_details,
    inspect_japanese_requirement_alpha as _inspect_japanese_requirement_alpha,
)
from orchestrator.repository_demo_observation import (  # noqa: E402
    build_repository_demo_observation as _build_repository_demo_observation,
)
from generators.acceptance_criteria import generate as _gen_ac  # noqa: E402
from generators.test_candidates import generate as _gen_tc  # noqa: E402


# ---- コア・検証ツール（§6.1） ----

def get_supported_profile() -> dict:
    """対応する条件・モダリティ・Action・Schema版（Supported Profile要約）を返す。"""
    return {
        "profile_version": PROFILE_VERSION,
        "schema_version": SCHEMA_VERSION,
        "condition_types": sorted(MVP_CONDITIONS),
        "comparison_operators": sorted(operators_in()),
        "comparison_operator_classification": {
            "classification": "rimay_jp_extension",
            "extension_feature": "COMPARISON_OPERATOR",
            "paper_claim": "withheld",
        },
        "multi_value": {
            "canonical_field": "value_expression",
            "expression_kinds": ["value", "group", "and", "or"],
            "connectors": value_connectors(),
            "binary_form": "fully_parenthesized",
            "automatic_scalar_lifting": "forbidden",
            "classification": "rimay_jp_extension",
            "extension_feature": "MULTI_VALUE",
            "paper_claim": "withheld",
        },
        "operator_value_expression": {
            "canonical_field": "operand",
            "identity_authority": ["legacy_subject", "typed_operand"],
            "typed_operand_wrappers": [
                "declared_reference", "instance_or_property", "ui_component_instance"],
            "declared_reference_kinds": ["actor", "class", "property"],
            "typed_operand_requires": "value_expression",
            "automatic_subject_typing": "forbidden",
            "class_gap_synthesis": "forbidden",
            "repository_mapping": "preserved_only",
            "classification": "rimay_jp_extension",
            "extension_feature": "OPERATOR_VALUE_EXPRESSION",
            "paper_claim": "withheld",
        },
        "modalities": ["MUST", "MUST_NOT"],
        "action_families": {fam: {"rimay_action_id": f["rimay_action_id"],
                                  "required_roles": f["required_roles"],
                                  "japanese_canonical_verb": f["japanese_canonical_verb"]}
                            for fam, f in sorted(case_frames().items())},
        "allowed_slot_pointers": list(_ALLOWED_POINTERS),
        "knowledge_versions": versions(),
    }


def normalize(text: str, project_id: str,
              requirement_id: str = "REQ-MCP") -> dict:
    """Rimay-JP文からCanonical候補を生成する。"""
    context = _vocabulary_context(project_id)
    with vocabulary_operation(context):
        canonical, findings = _normalize(text, requirement_id)
    return {"canonical": canonical, "findings": findings,
            "vocabulary_context": context.public()}


def validate_core(canonical: dict, project_id: str) -> dict:
    """Schema・格フレーム・品質規則を検査する。"""
    context = _vocabulary_context(project_id)
    with vocabulary_operation(context):
        return {"schema_errors": validate_schema(canonical),
                "findings": _validate(canonical, phase2_slice=False),
                "vocabulary_context": context.public()}


def validate_terminology(canonical: dict, project_id: str) -> dict:
    """用語辞書適合と語彙依存を検査する（terminology-validator所有の4コード）。

    ADR-0014: 未登録語（JP-LEXICAL/UNREGISTERED_TERM）に加え、候補承認待ち
    （TERM_APPROVAL_PENDING=blocking）・多義（AMBIGUOUS_TERM）・廃止語
    （DEPRECATED_TERM=warning）を返す。
    """
    owned = {"JP-LEXICAL", "TERM_APPROVAL_PENDING", "AMBIGUOUS_TERM",
             "DEPRECATED_TERM"}
    context = _vocabulary_context(project_id)
    with vocabulary_operation(context):
        findings = [f for f in _validate(canonical, phase2_slice=False)
                    if f["code"] in owned]
    return {"findings": findings, "vocabulary_context": context.public()}


def validate_domain(canonical: dict, project_id: str) -> dict:
    """業務ルール・状態モデルとの整合を検査する（外部知識の版に依存）。"""
    context = _vocabulary_context(project_id)
    with vocabulary_operation(context):
        out = _route(copy.deepcopy(canonical))
        return {"findings": out["findings"], "routes": out["routes"],
                "knowledge_versions": versions(),
                "vocabulary_context": context.public()}


def validate_sidecar(canonical: dict, views: dict) -> dict:
    """sidecar完全性とartifact-manifest整合（SIDECAR-STALE）を検査する。"""
    return {"messages": check_sidecar(canonical, views)}


def render_requirement_views(canonical: dict) -> dict:
    """CanonicalからRimay-JP文・English Rimay・sidecarをmanifest付きで生成する。"""
    from rimay_jp_core.jp_serializer import render_rimay_jp
    views = _render(canonical)
    return {**views, "rimay_jp": render_rimay_jp(canonical)}


def parse_english_rimay(text: str) -> dict:
    """クリーンルームParser（論文ベース再実装）を実行する。"""
    try:
        return {"ok": True, "ast": _parse(text)}
    except ParseError as e:
        # §19.6: error文字列は後方互換で維持し、diagnosticをadditive追加する
        return {"ok": False, "error": str(e), "diagnostic": e.diagnostic()}


def check_equivalence(canonical: dict, english_rimay: str) -> dict:
    """Canonical rimay_coreとASTの射影意味等価を検査する。"""
    try:
        ast = _parse(english_rimay)
    except ParseError as e:
        return {"equivalent": False, "differences": [f"parse error: {e}"]}
    diffs = compare(canonical, ast)
    return {"equivalent": not diffs, "differences": diffs}


def check_conformance(canonical: dict, english_rimay: str) -> dict:
    """grammar conformance検査（C4・§20.2。semantic等価とは別軸＝主計画D4）。

    rule ID束縛（rimay_action_id/emse_rule_id）・operator集合・full consumptionを
    English conformance profileに対して検査する。分類（emse_vor/official_repository/
    rimay_jp_extension）はSerializer manifestのconformance欄が正本。
    """
    from rimay_jp_core.equivalence import compare_conformance
    try:
        ast = _parse(english_rimay)
    except ParseError as e:
        return {"conformant": False, "differences": [f"parse error: {e}"],
                "diagnostic": e.diagnostic()}
    diffs = compare_conformance(canonical, ast)
    result = {"conformant": not diffs, "differences": diffs}
    if ast.get("response_expression") is None and ast.get("response_block") is None:
        result.update({
            "rimay_action_id": ast["response"]["action"]["rimay_action_id"],
            "emse_rule_id": ast["response"]["action"]["emse_rule_id"],
        })
        if isinstance(ast["response"].get("frequency"), dict):
            result["frequency"] = {
                key: ast["response"]["frequency"][key]
                for key in ("value", "unit")
            }
        return result
    result["response_expression"] = ast.get("response_expression") is not None
    result["response_block"] = ast.get("response_block") is not None
    result["leaf_bindings"] = [
        {
            "path": path.removeprefix("/rimay_core"),
            "rimay_action_id": response["action"]["rimay_action_id"],
            "emse_rule_id": response["action"]["emse_rule_id"],
            **({"frequency": {
                key: response["frequency"][key] for key in ("value", "unit")
            }} if isinstance(response.get("frequency"), dict) else {}),
        }
        for path, response in iter_core_responses(ast)
    ]
    return result


def apply_canonical_patch(canonical: dict, patch: dict) -> dict:
    """Patchを検査し、許可された差分だけを適用する（唯一の更新手段。§8統制）。"""
    return _apply_patch(canonical, patch)


# ---- Repository Grammar壁打ちデモ（stateless facade） ----

def analyze_japanese_requirement(
    source_text_ja: str,
    requirement_id: str = "REQ-DEMO",
    request_id: str = "REQ-DEMO-JA",
    detail: str = "compact",
) -> dict:
    """日本語Normalizerを第一入口にし、lossless bridge可否を返す。"""
    return _analyze_japanese_requirement(
        source_text_ja, requirement_id=requirement_id,
        request_id=request_id, detail=detail,
    )


def inspect_japanese_requirement_alpha(
    source_text_ja: str,
    rimay_candidate: str | None = None,
    requirement_id: str = "REQ-ALPHA",
    request_id: str = "REQ-ALPHA-JA",
    detail: str = "compact",
) -> dict:
    """任意の日本語要求についてスメルと固定Grammar候補を一括検査する（alpha）。

    rimay_candidate省略時は決定的bridgeを試し、作れなければcandidate_requiredを返す。
    hostまたは利用者の完全な候補を渡せば、特定Actionに限定せず同じ入口で再検査する。
    日本語と候補の意味同値は検証済みとしない。
    """
    return _inspect_japanese_requirement_alpha(
        source_text_ja,
        rimay_candidate=rimay_candidate,
        requirement_id=requirement_id,
        request_id=request_id,
        detail=detail,
    )


def get_repository_parser_capabilities() -> dict:
    """固定Repository Grammarの実行可能Ruleとauthority境界を返す。"""
    return _get_repository_parser_capabilities()


def get_repository_rule_details(
    literals: list[str] | None = None,
    rule_ids: list[str] | None = None,
    max_results: int = 5,
) -> dict:
    """候補生成に必要なRuleのIR由来要約だけを返す。"""
    return _get_repository_rule_details(
        literals=literals, rule_ids=rule_ids, max_results=max_results,
    )


def evaluate_rimay_candidate(
    rimay_candidate: str,
    candidate_origin: str,
    source_text_ja: str | None = None,
    request_id: str = "REQ-DEMO-CANDIDATE",
    start_rule: str = "CNLFunctionalRequirements",
    detail: str = "compact",
) -> dict:
    """完全なRepository Rimay候補をparse・link・projectする。"""
    return _evaluate_rimay_candidate(
        rimay_candidate, candidate_origin=candidate_origin,
        source_text_ja=source_text_ja, request_id=request_id,
        start_rule=start_rule, detail=detail,
    )


def build_repository_demo_observation(
    session_id: str,
    turn_id: str,
    analysis_response: dict,
    evaluation_response: dict,
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
    """Parser応答と分離したdefault-redacted observationを組み立てる。"""
    return _build_repository_demo_observation(
        session_id, turn_id, analysis_response, evaluation_response,
        privacy_mode=privacy_mode, source_text_ja=source_text_ja,
        rimay_candidate=rimay_candidate, model_id=model_id,
        prompt_version=prompt_version, next_question_ja=next_question_ja,
        user_accepted_candidate=user_accepted_candidate,
        retry_count=retry_count,
        restricted_raw_controls=restricted_raw_controls,
    )


# ---- 知識・対話ツール（§6.2） ----

def classify_information(text: str) -> dict:
    """Context・Rule・Issue・Requirement Candidate等へ分類する。"""
    return _classify(text)


def extract_requirement_candidates(segment: dict, project_id: str,
                                   requirement_id: str = "REQ-MCP") -> dict:
    """分類済みセグメントから要求候補を抽出する（source-analysis契約）。"""
    context = _vocabulary_context(project_id)
    with vocabulary_operation(context):
        out = _extract(segment, requirement_id)
    return {**out, "vocabulary_context": context.public()}


def lookup_term(surface: str, project_id: str) -> dict:
    """用語を標準IDへ解決する。"""
    from orchestrator.terminology import resolve_surface_in_context
    context = _vocabulary_context(project_id)
    resolved = resolve_surface_in_context(surface, context)
    if resolved["kind"] in ("exact", "synonym"):
        hit = resolved["matches"][0]
        return {"found": True, "term_id": hit["term_id"],
                "local_term_id": hit["local_term_id"],
                "type": next(t["type"] for t in effective_terms(context)
                             if t["qualified_id"] == hit["term_id"]),
                "vocabulary_context": context.public()}
    return {"found": False, "resolution": resolved,
            "vocabulary_context": context.public()}


def get_case_frame(family: str) -> dict:
    """Action Classと必須Roleを返す。"""
    frame = case_frames().get(family)
    if frame is None:
        return {"found": False, "known_families": sorted(case_frames().keys())}
    return {"found": True, **frame}


def lookup_state_model(property_id: str) -> dict:
    """状態・イベント・遷移を照会する。"""
    for sm in knowledge_bank().get("state_models") or []:
        if sm.get("property") == property_id:
            return {"found": True, **sm}
    return {"found": False}


def lookup_business_rule(keyword: str = "") -> dict:
    """業務ルール・規制・既存仕様を照会する（keywordで絞り込み）。"""
    rules = knowledge_bank().get("business_rules") or []
    if keyword:
        rules = [r for r in rules if keyword in str(r)]
    return {"rules": rules, "knowledge_versions": versions()}


def route_knowledge(canonical: dict) -> dict:
    """スロットとfindingから必要な知識源を選択する（RQK-D）。"""
    return _route(copy.deepcopy(canonical))


def plan_questions(canonical: dict) -> dict:
    """不足・曖昧性に対する質問と優先順位を返す（Rule Engine発火）。"""
    return _plan_questions(canonical)


def apply_answer(canonical: dict, question: dict, answer_text: str) -> dict:
    """利用者回答を根拠付きCanonical Patchへ変換する（適用はapply_canonical_patch）。"""
    return {"patches": _apply_answer(canonical, question, answer_text)}


# ---- 下流・還流ツール（§6.3） ----

def generate_acceptance_criteria(canonical: dict) -> dict:
    """承認済みCanonicalから受入基準を生成する（approved以外は拒否）。"""
    return _gen_ac(canonical)


def generate_test_candidates(canonical: dict, criteria: dict | None = None) -> dict:
    """承認済みCanonical＋受入基準からテスト候補を生成する（approved以外は拒否）。"""
    return _gen_tc(canonical,
                   criteria or {"trace": {"slots": [], "provenance": []}})


def record_feedback(feedback: dict) -> dict:
    """下流問題を要求スロット・知識・Validator・Generatorへ関連付ける（Phase 3F）。"""
    return _handle_feedback(feedback)


# ---- 統合拡張（Step 4/5。§6策定後に確定した契約） ----

def validate_all_layers(canonical: dict, project_id: str) -> dict:
    """9層検証を統合実行し、Validation Report（正本）とvalidation_stateを返す。"""
    context = _vocabulary_context(project_id)
    with vocabulary_operation(context):
        res = _validate_all(canonical, vocabulary_context=context)
    return {"blocked": res["blocked"], "report": res["report"],
            "validation_state": res["validation_state"],
            "classification": res["classification"],
            "artifacts": res["artifacts"], "canonical": canonical}


def plan_repairs(canonical: dict, report: dict | None = None,
                 extra_findings: list | None = None) -> dict:
    """Validation Reportのfindingをrepair_dispositionで修復アクションへ振り分ける。

    Patchは含まれない（質問・分割提案・知識ルート・自動表層修復のみ。Step 5統制）。
    """
    return _plan_repairs(canonical, report, extra_findings)


def diagnose_raw_text(text: str, language: str = "ja",
                      case_id: str = "RAW") -> dict:
    """Free-text Import診断（Pre-Canonical。ADR-0013の境界で唯一、
    reqsmell日本語Analyzerを使う入口）。非排除: findingは分類見直し・並べ替え・
    質問・分割提案を起動するのみで、要求を遮断しない（恒久Advisory）。
    """
    from orchestrator.raw_text_gate import inspect
    return inspect(text, language, case_id)


def accept_split_proposal(canonical: dict, proposal: dict) -> dict:
    """**人間が分割提案を承諾した後にのみ呼ぶ**。各partを通常抽出経路へ入れ、
    親子traceabilityを張る（意味部分は不変。親のsuperseded化は承認ワークフローの責務）。
    """
    from orchestrator.split_proposal import accept_split
    out = accept_split(canonical, proposal)
    return {**out, "canonical": canonical, "proposal": proposal}


# ---- 語彙形成ループ（ADR-0014 P0-8） ----
# vocabulary-rootと案件レジストリはサーバー設定。MCP入力には公開しない。
# リポジトリ既定値はproject:sample fixtureだけを指し、実案件は外部rootへ差し替える。
VOCABULARY_ROOT = _RIMAY
VOCABULARY_REGISTRY = _RIMAY / "terminology" / "project-registry.yaml"
# 0.1.x runner/import互換名（新しい案件別処理では参照しない）。
TERMINOLOGY_ROOT = _RIMAY / "terminology"
LEXICON_BASE = _RIMAY / "lexicon"


def _registry():
    return VocabularyRegistry(VOCABULARY_ROOT, VOCABULARY_REGISTRY)


def _vocabulary_context(project_id: str):
    return _registry().resolve(project_id)


def _term_store(project_id: str):
    from orchestrator.terminology import TerminologyStore
    registry = _registry()
    return TerminologyStore(registry.terminology_root(project_id), project_id)


def _current_vocab(project_id: str):
    context = _vocabulary_context(project_id)
    return context, effective_terms(context)


def observe_term_occurrence(project_id: str, observation: dict, document_id: str,
                            requirement_id: str, channel: str = "dialogue",
                            observed_at: str = "") -> dict:
    """未知語Observationを不変Occurrenceとして永続化し、候補を起票する。

    ADR-0014 D2の明示記録操作（Normalizerは書き込まない）。自然キーでidempotent。
    observationはnormalize結果findingsのevidence由来
    （orchestrator.terminology.observations_from）を渡す。
    """
    context = _vocabulary_context(project_id)
    store = _term_store(project_id)
    occ = store.observe(observation, document_id=document_id,
                        requirement_id=requirement_id, channel=channel,
                        observed_at=observed_at)
    return {"occurrence": occ, "candidate": store.ensure_candidate(occ),
            "vocabulary_context": context.public()}


def resolve_term_surface(surface: str, project_id: str) -> dict:
    """表層の多値Resolution（exact|synonym|ambiguous|not_found|deprecated）。"""
    from orchestrator.terminology import resolve_surface_in_context
    context = _vocabulary_context(project_id)
    return resolve_surface_in_context(surface, context)


def get_term_candidate(candidate_id: str, project_id: str) -> dict:
    """語彙候補の現在状態（revision含む。書き込み系はbase_revision必須）。"""
    return {"candidate": _term_store(project_id).candidate(candidate_id)}


def propose_term_candidate(candidate_id: str, base_revision: int,
                           proposed_term: dict, project_id: str,
                           evidence: list | None = None) -> dict:
    """候補へ定義案（id・表記・type・定義・根拠）を記録する（楽観ロック）。"""
    proposed = dict(proposed_term)
    proposed.setdefault("scope", f"project:{project_id}")
    patch: dict = {"proposed_term": proposed}
    if evidence:
        patch["evidence"] = evidence
    return {"candidate": _term_store(project_id).update_candidate(
        candidate_id, base_revision, patch)}


def submit_term_candidate_for_review(candidate_id: str,
                                     base_revision: int, project_id: str) -> dict:
    """候補を審査中（under_review）へ進める。"""
    return {"candidate": _term_store(project_id).update_candidate(
        candidate_id, base_revision, {"status": "under_review"})}


def approve_term_candidate(candidate_id: str, base_revision: int,
                           reviewer: str, approved_at: str,
                           project_id: str,
                           decision_reason: str = "") -> dict:
    """人間の承認操作。Approval Receiptを発行する（ReceiptなしにSnapshot公開不可）。"""
    store = _term_store(project_id)
    receipt = store.approve(candidate_id, base_revision, reviewer=reviewer,
                            approved_at=approved_at,
                            decision_reason=decision_reason)
    return {"receipt": receipt, "candidate": store.candidate(candidate_id)}


def reject_term_candidate(candidate_id: str, base_revision: int,
                          reviewer: str, decided_at: str,
                          project_id: str,
                          reason: str = "") -> dict:
    """候補を却下する（人間操作。記録は残る）。"""
    return {"candidate": _term_store(project_id).update_candidate(
        candidate_id, base_revision,
        {"status": "rejected", "review": {"reviewer": reviewer,
                                          "decided_at": decided_at,
                                          "decision_reason": reason}})}


def publish_vocabulary_snapshot(snapshot_id: str, candidate_ids: list,
                                operation_id: str, published_at: str,
                                project_id: str,
                                requirement_term_index: dict | None = None
                                ) -> dict:
    """承認済み候補をImmutable Snapshotとして公開し、伝播Sagaを起票する。

    Receipt必須（Gate 5）・同表層重複はLoader gateで公開拒否・同一IDの再公開拒否。
    供給の正本はSnapshot ID指定のload_vocabulary（cache_clearに依存しない）。
    """
    context, _ = _current_vocab(project_id)
    if context.project.source_ref.startswith("vocabulary-fixture://"):
        raise ValueError("sample fixture is read-only; configure an external vocabulary-root")
    op = _term_store(project_id).publish_snapshot(
        snapshot_id, lexicon_base=context.project.base,
        base_vocab=list(project_terms(context)),
        candidate_ids=candidate_ids, operation_id=operation_id,
        published_at=published_at,
        requirement_term_index=requirement_term_index,
        scope=f"project:{project_id}")
    # 同一プロセスへの即時反映（最適化。正しさはSnapshot ID指定読込が正本）
    from rimay_jp_core import lexicon as _lex
    for fn in (_lex.terms, _lex.jp_index, _lex.term_ids):
        fn.cache_clear()
    refreshed = _vocabulary_context(project_id)
    return {"operation": op, "vocabulary_context": refreshed.public()}


def extract_document_terms(text: str, document_id: str, project_id: str) -> dict:
    """文書から用語候補Observationを抽出する（決定論・無副作用。ADR-0014 P1）。

    未知語のみがobservations（候補化対象）。永続化は別途
    observe_term_occurrence（channel="document"）で明示的に行う。
    既登録=resolved／同表記多義=ambiguous／廃止語=deprecatedへ分類して返す。
    """
    from orchestrator.document_term_extractor import (
        extract_document_terms as _extract_doc)
    context, vocab = _current_vocab(project_id)
    return {**_extract_doc(text, document_id, vocab=vocab),
            "vocabulary_context": context.public()}


def analyze_vocabulary_impact(operation_id: str, project_id: str) -> dict:
    """公開operationの影響計画と伝播未完了Requirement集合を返す（read-only）。"""
    store = _term_store(project_id)
    return {"operation": store.operation(operation_id),
            "pending_requirements": sorted(store.pending_requirements())}


def propagate_vocabulary_operation(operation_id: str, canonicals: list,
                                   applied_at: str, project_id: str) -> dict:
    """影響RequirementへSaga伝播する（idempotent・部分完了はretry_requiredで可視）。

    Patchはknowledge_asset根拠（term:<id>@<snapshot>）で通常の統制ゲートを通る。
    """
    from orchestrator.terminology import propagate
    store = _term_store(project_id)
    cmap = {c["requirement_id"]: c for c in canonicals}
    op = propagate(store, operation_id, cmap, applied_at=applied_at)
    return {"operation": op, "canonicals": list(cmap.values())}


TOOLS = [
    # §6.1 コア・検証
    get_supported_profile, normalize, validate_core, validate_terminology,
    validate_domain, validate_sidecar, render_requirement_views,
    parse_english_rimay, check_equivalence, check_conformance, apply_canonical_patch,
    analyze_japanese_requirement, inspect_japanese_requirement_alpha,
    get_repository_parser_capabilities,
    get_repository_rule_details, evaluate_rimay_candidate,
    build_repository_demo_observation,
    # §6.2 知識・対話
    classify_information, extract_requirement_candidates, lookup_term,
    get_case_frame, lookup_state_model, lookup_business_rule, route_knowledge,
    plan_questions, apply_answer,
    # §6.3 下流・還流
    generate_acceptance_criteria, generate_test_candidates, record_feedback,
    # 統合拡張（Step 4/5・ADR-0013）
    validate_all_layers, plan_repairs, accept_split_proposal, diagnose_raw_text,
    # 語彙形成ループ（ADR-0014 P0-8＋P1）
    extract_document_terms,
    observe_term_occurrence, resolve_term_surface, get_term_candidate,
    propose_term_candidate, submit_term_candidate_for_review,
    approve_term_candidate, reject_term_candidate,
    publish_vocabulary_snapshot, analyze_vocabulary_impact,
    propagate_vocabulary_operation,
]


def serve() -> None:
    """MCPトランスポートで公開する（`mcp`パッケージがある環境のみ）。"""
    from mcp.server.fastmcp import FastMCP  # 遅延import

    server = FastMCP("rimay-jp")
    for tool in TOOLS:
        server.tool()(tool)
    server.run()


if __name__ == "__main__":
    serve()
