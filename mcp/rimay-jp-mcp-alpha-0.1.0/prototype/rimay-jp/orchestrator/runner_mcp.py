"""MCP Adapter評価ランナー（Phase 5、PoC継続条件⑤）。

検査（quality adapterのStep 1完了条件と同型＋§6網羅）:
- ツール網羅: core／知識／下流23件、Repository日本語alpha 6件、統合拡張4件、
  語彙形成11件の計44ツールが公開されている
- Adapter同値: MCPハンドラ経由と直接呼び出しの結果が一致する（全経路同一SSOT）
- 直列化可能性: 全ツールの出力がJSON直列化できる（MCPトランスポート前提）
- 統制の透過: Adapter経由でも確定根拠検査・楽観ロック・approved限定生成が働く
- FastMCP登録: `mcp`（<2）で全ツールが登録できる（サーバ起動はしない）
"""
from __future__ import annotations

import copy
import json
import os
from pathlib import Path

from . import _ROOT  # noqa: F401
from rimay_jp_core.normalizer import normalize as direct_normalize  # noqa: E402
from .information_classifier import classify as direct_classify  # noqa: E402
from .candidate_extractor import extract as direct_extract  # noqa: E402
from .validation_router import validate_all as direct_validate_all  # noqa: E402

_EXPECTED_TOOLS = [
    # §6.1
    "get_supported_profile", "normalize", "validate_core",
    "validate_terminology", "validate_domain", "validate_sidecar",
    "render_requirement_views", "parse_english_rimay", "check_equivalence",
    "check_conformance", "apply_canonical_patch",
    # Repository Grammar日本語alpha
    "analyze_japanese_requirement", "inspect_japanese_requirement_alpha",
    "get_repository_parser_capabilities",
    "get_repository_rule_details", "evaluate_rimay_candidate",
    "build_repository_demo_observation",
    # §6.2
    "classify_information", "extract_requirement_candidates", "lookup_term",
    "get_case_frame", "lookup_state_model", "lookup_business_rule",
    "route_knowledge", "plan_questions", "apply_answer",
    # §6.3
    "generate_acceptance_criteria", "generate_test_candidates",
    "record_feedback",
    # 統合拡張
    "validate_all_layers", "plan_repairs", "accept_split_proposal",
    "diagnose_raw_text",
    # 語彙形成ループ（ADR-0014 P0-8＋P1）
    "extract_document_terms",
    "observe_term_occurrence", "resolve_term_surface", "get_term_candidate",
    "propose_term_candidate", "submit_term_candidate_for_review",
    "approve_term_candidate", "reject_term_candidate",
    "publish_vocabulary_snapshot", "analyze_vocabulary_impact",
    "propagate_vocabulary_operation",
]

_TEXT_OK = ("利用者が注文確定ボタンを押したとき、"
            "通知システムは請求書PDFを顧客メールアドレスに送信しなければならない。")
_TEXT_GAP = "通知システムは請求書PDFを送信しなければならない。"
_PROJECT = "sample"


def _split_call(adapter):
    """分割提案→受諾の直列化検査。非原子性はPre-Canonical診断
    （diagnose_raw_text）由来のfindingとして供給する（ADR-0013境界）。"""
    text = "注文管理システムは注文データを保存および更新しなければならない。"
    can = adapter.extract_requirement_candidates(
        {"document_id": "MCP-SPLIT", "text": text}, _PROJECT,
        "REQ-SPLIT")["canonical"]
    gate = adapter.diagnose_raw_text(text, "ja", "MCP-SPLIT")
    props = adapter.plan_repairs(can, None, gate["findings"])["split_proposals"]
    if not props:
        raise RuntimeError("分割提案が得られない")
    return adapter.accept_split_proposal(can, props[0])


def _load_adapter():
    import importlib.util
    path = Path(__file__).resolve().parents[1] / "adapters" / "mcp" / "rimay_jp_mcp.py"
    spec = importlib.util.spec_from_file_location("rimay_jp_mcp", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def run_mcp_check() -> dict:
    results = []
    adapter = _load_adapter()

    # --- ツール網羅（§6対応表） ---
    names = [t.__name__ for t in adapter.TOOLS]
    missing = [n for n in _EXPECTED_TOOLS if n not in names]
    extra = [n for n in names if n not in _EXPECTED_TOOLS]
    results.append({"case_id": "MCP-TOOLSET",
                    "verdict": "FAIL" if (missing or extra) else "PASS",
                    "detail": f"欠落{missing} 想定外{extra}" if (missing or extra)
                    else f"core・知識・下流23件＋Repository日本語alpha 6件＋"
                         f"統合拡張4件＋語彙ループ11件（計{len(names)}）"})

    # --- Adapter同値（全経路同一SSOT） ---
    problems = []
    context = adapter._vocabulary_context(_PROJECT)
    from rimay_jp_core.vocabulary import vocabulary_operation
    with vocabulary_operation(context):
        a_norm = adapter.normalize(_TEXT_OK, _PROJECT, "REQ-EQ")
        d_can, d_fnd = direct_normalize(_TEXT_OK, "REQ-EQ")
    if a_norm["canonical"] != d_can or a_norm["findings"] != d_fnd:
        problems.append("normalizeの結果が直接呼び出しと不一致")
    if adapter.classify_information(_TEXT_GAP) != direct_classify(_TEXT_GAP):
        problems.append("classify_informationの結果が不一致")
    seg = {"document_id": "MCP-EQ", "text": _TEXT_GAP}
    extracted = adapter.extract_requirement_candidates(seg, _PROJECT, "REQ-EQ2")
    if {k: v for k, v in extracted.items() if k != "vocabulary_context"} \
            != direct_extract(seg, "REQ-EQ2"):
        problems.append("extract_requirement_candidatesの結果が不一致")
    a_val = adapter.validate_all_layers(copy.deepcopy(d_can), _PROJECT)
    with vocabulary_operation(context):
        d_val = direct_validate_all(copy.deepcopy(d_can),
                                    vocabulary_context=context)
    if a_val["report"] != d_val["report"]:
        problems.append("validate_all_layersのReportが不一致")
    results.append({"case_id": "MCP-EQUIVALENCE",
                    "verdict": "FAIL" if problems else "PASS",
                    "detail": "; ".join(problems) or
                    "normalize/classify/extract/validate_allが直接呼び出しと一致"})

    # --- 直列化可能性（全ツールを代表入力で実行しJSON化） ---
    problems = []
    canonical = copy.deepcopy(d_can)
    views = adapter.render_requirement_views(canonical)
    question = {"question_id": "Q1", "rule_id": "RULE-SEND-DEST-001",
                "target_path": "/rimay_core/response/destination"}
    gap_can = adapter.extract_requirement_candidates(
        {"document_id": "MCP-GAP", "text": _TEXT_GAP}, _PROJECT,
        "REQ-GAP")["canonical"]
    calls = [
        ("get_supported_profile", lambda: adapter.get_supported_profile()),
        ("normalize", lambda: adapter.normalize(_TEXT_OK, _PROJECT)),
        ("validate_core", lambda: adapter.validate_core(canonical, _PROJECT)),
        ("validate_terminology", lambda: adapter.validate_terminology(canonical, _PROJECT)),
        ("validate_domain", lambda: adapter.validate_domain(canonical, _PROJECT)),
        ("validate_sidecar", lambda: adapter.validate_sidecar(canonical, views)),
        ("render_requirement_views", lambda: views),
        ("parse_english_rimay",
         lambda: adapter.parse_english_rimay(views["english_rimay"])),
        ("check_equivalence",
         lambda: adapter.check_equivalence(canonical, views["english_rimay"])),
        ("check_conformance",
         lambda: adapter.check_conformance(canonical, views["english_rimay"])),
        ("apply_canonical_patch", lambda: adapter.apply_canonical_patch(
            copy.deepcopy(gap_can),
            {"operation": "replace_slot", "requirement_id": "REQ-GAP",
             "base_revision": gap_can["revision"],
             "path": "/rimay_core/response/destination",
             "new_value": "CustomerEmailAddress", "new_status": "proposed",
             "evidence": {"type": "tool_result", "reference": "term:CustomerEmailAddress"}})),
        ("classify_information", lambda: adapter.classify_information(_TEXT_OK)),
        ("extract_requirement_candidates",
         lambda: adapter.extract_requirement_candidates(seg, _PROJECT)),
        ("lookup_term", lambda: adapter.lookup_term("顧客メールアドレス", _PROJECT)),
        ("get_case_frame", lambda: adapter.get_case_frame("SEND")),
        ("lookup_state_model", lambda: adapter.lookup_state_model("OrderStatus")),
        ("lookup_business_rule", lambda: adapter.lookup_business_rule("承認")),
        ("route_knowledge", lambda: adapter.route_knowledge(canonical)),
        ("plan_questions", lambda: adapter.plan_questions(gap_can)),
        ("apply_answer", lambda: adapter.apply_answer(
            gap_can, question, "顧客メールアドレス")),
        ("generate_acceptance_criteria",
         lambda: adapter.generate_acceptance_criteria(canonical)),
        ("generate_test_candidates",
         lambda: adapter.generate_test_candidates(canonical)),
        ("record_feedback", lambda: adapter.record_feedback(
            {"case_id": "MCP-FB", "context": {"unknown_term": "配送先住所"}})),
        ("validate_all_layers",
         lambda: adapter.validate_all_layers(copy.deepcopy(canonical), _PROJECT)),
        ("plan_repairs", lambda: adapter.plan_repairs(
            copy.deepcopy(gap_can),
            adapter.validate_all_layers(copy.deepcopy(gap_can), _PROJECT)["report"])),
        ("accept_split_proposal", lambda: _split_call(adapter)),
        ("diagnose_raw_text", lambda: adapter.diagnose_raw_text(
            "通知システムは請求書PDFを送信しなければならない、"
            "利用者が注文確定ボタンを押したとき。", "ja", "MCP-RAW")),
        ("analyze_japanese_requirement",
         lambda: adapter.analyze_japanese_requirement(
             "通知システムは請求書PDFを請求管理システムに"
             "送信しなければならない。")),
        ("inspect_japanese_requirement_alpha",
         lambda: adapter.inspect_japanese_requirement_alpha(
             "通知システムは請求書PDFを送信しなければならない、"
             "利用者が注文確定ボタンを押したとき。")),
    ]
    if os.environ.get("RIMAY_FIXED_GRAMMAR"):
        demo = adapter.analyze_japanese_requirement(
            "通知システムは請求書PDFを請求管理システムに"
            "送信しなければならない。"
        )
        demo_evaluation = adapter.evaluate_rimay_candidate(
            demo["repository_compatibility"]["repository_candidate"],
            candidate_origin="rimay_jp_repository_bridge",
            source_text_ja=(
                "通知システムは請求書PDFを請求管理システムに"
                "送信しなければならない。"
            ),
        )
        calls.extend([
            ("get_repository_parser_capabilities",
             lambda: adapter.get_repository_parser_capabilities()),
            ("get_repository_rule_details",
             lambda: adapter.get_repository_rule_details(
                 rule_ids=["SEND_11_1_1"])),
            ("evaluate_rimay_candidate",
             lambda: demo_evaluation),
            ("build_repository_demo_observation",
             lambda: adapter.build_repository_demo_observation(
                 "MCP-DEMO", "TURN-1", demo, demo_evaluation)),
        ])
    else:
        for name, fn in (
            ("get_repository_parser_capabilities",
             adapter.get_repository_parser_capabilities),
            ("get_repository_rule_details",
             lambda: adapter.get_repository_rule_details(
                 rule_ids=["SEND_11_1_1"])),
            ("evaluate_rimay_candidate",
             lambda: adapter.evaluate_rimay_candidate(
                 "candidate", candidate_origin="llm")),
        ):
            try:
                fn()
                problems.append(f"{name}: fixed Grammar未設定でも成功した")
            except ValueError as exc:
                if "RIMAY_FIXED_GRAMMAR is not configured" not in str(exc):
                    problems.append(f"{name}: 想定外のfail-closed: {exc}")
    for name, fn in calls:
        try:
            json.dumps(fn(), ensure_ascii=False)
        except Exception as e:  # noqa: BLE001 — 検査目的の網羅catch
            problems.append(f"{name}: {type(e).__name__}: {e}")
    results.append({"case_id": "MCP-SERIALIZABLE",
                    "verdict": "FAIL" if problems else "PASS",
                    "detail": "; ".join(problems[:3]) or
                    f"全{len(calls)}ツールの出力がJSON直列化可能"})

    # --- 語彙形成ループE2E（ADR-0014 P0-8 Gate: 発見→承認→公開→伝播→確定） ---
    problems = []
    import shutil
    import tempfile
    tmp = Path(tempfile.mkdtemp(prefix="rimay-mcp-term-"))
    keep_vroot, keep_registry = adapter.VOCABULARY_ROOT, adapter.VOCABULARY_REGISTRY
    vocabulary_root = tmp / "vocabulary"
    vocabulary_root.mkdir()
    registry_path = vocabulary_root / "project-registry.yaml"
    registry_path.write_text(json.dumps({
        "registry_version": "1.0.0",
        "organization": {},
        "projects": [{"project_id": _PROJECT}],
    }), encoding="utf-8")
    from rimay_jp_core.lexicon import terms as seed_terms
    from rimay_jp_core.vocabulary import write_snapshot_artifact
    write_snapshot_artifact(
        vocabulary_root / "org" / "common", "org:common", "VOC-ORG-001", [],
        published_at="2026-08-19T00:00:00+09:00", operation_id="FIXTURE-ORG")
    write_snapshot_artifact(
        vocabulary_root / "projects" / _PROJECT, f"project:{_PROJECT}",
        "VOC-SAMPLE-001", seed_terms(),
        published_at="2026-08-19T00:00:00+09:00", operation_id="FIXTURE-SAMPLE")
    adapter.VOCABULARY_ROOT = vocabulary_root
    adapter.VOCABULARY_REGISTRY = registry_path
    try:
        from orchestrator.terminology import observations_from
        text = "ラジオシステムは注文一覧を注文画面に表示しなければならない。"
        e2e_calls = []
        out_n = adapter.normalize(text, _PROJECT, "REQ-MCP-TERM")
        c_term = out_n["canonical"]
        obs = observations_from(out_n["findings"], text)
        if len(obs) != 1:
            problems.append(f"Observation抽出不備: {obs}")
        out = adapter.observe_term_occurrence(
            _PROJECT, obs[0], document_id="DOC-MCP", requirement_id="REQ-MCP-TERM",
            channel="normalizer", observed_at="2026-08-06T13:00:00+09:00")
        e2e_calls.append(("observe_term_occurrence", out))
        cand = out["candidate"]
        r = adapter.resolve_term_surface("ラジオシステム", _PROJECT)
        e2e_calls.append(("resolve_term_surface", r))
        if r["kind"] != "not_found":
            problems.append(f"公開前にnot_foundでない: {r['kind']}")
        from orchestrator.terminology import attach_dependency
        attach_dependency(c_term, "/rimay_core/response/actor",
                          cand["candidate_id"])
        if not any(f["code"] == "TERM_APPROVAL_PENDING" and f["blocking"]
                   for f in adapter.validate_terminology(c_term, _PROJECT)["findings"]):
            problems.append("依存中のblocking遮断がAdapter経由で働かない")
        out = adapter.propose_term_candidate(
            cand["candidate_id"], cand["revision"],
            {"id": "RadioSystem", "preferred_japanese": "ラジオシステム",
             "type": "actor", "synonyms": [],
             "definition": "ラジオ聴取機能を提供するシステム"},
            _PROJECT,
            evidence=[{"type": "user_answer", "reference": "dialogue:MCP/Q-1"}])
        e2e_calls.append(("propose_term_candidate", out))
        out = adapter.submit_term_candidate_for_review(
            cand["candidate_id"], out["candidate"]["revision"], _PROJECT)
        e2e_calls.append(("submit_term_candidate_for_review", out))
        e2e_calls.append(("get_term_candidate",
                          adapter.get_term_candidate(cand["candidate_id"], _PROJECT)))
        try:
            adapter.publish_vocabulary_snapshot(
                "VOC-MCP-001", [cand["candidate_id"]], "TOP-MCP-001",
                "2026-08-06T13:01:00+09:00", _PROJECT)
            problems.append("承認前公開が拒否されない")
        except ValueError:
            pass
        out = adapter.approve_term_candidate(
            cand["candidate_id"], out["candidate"]["revision"],
            reviewer="usa", approved_at="2026-08-06T13:02:00+09:00",
            project_id=_PROJECT)
        e2e_calls.append(("approve_term_candidate", out))
        out = adapter.publish_vocabulary_snapshot(
            "VOC-MCP-001", [cand["candidate_id"]], "TOP-MCP-001",
            "2026-08-06T13:03:00+09:00", _PROJECT)
        e2e_calls.append(("publish_vocabulary_snapshot", out))
        imp = adapter.analyze_vocabulary_impact("TOP-MCP-001", _PROJECT)
        e2e_calls.append(("analyze_vocabulary_impact", imp))
        if imp["operation"]["impact_kind"].get("REQ-MCP-TERM") != "re-resolve" \
                or "REQ-MCP-TERM" not in imp["pending_requirements"]:
            problems.append(f"影響分類が不正: {imp['operation']}")
        r2 = adapter.resolve_term_surface("ラジオシステム", _PROJECT)
        if r2["kind"] != "exact" or \
                r2["vocabulary_context"]["project"]["snapshot_id"] != "VOC-MCP-001":
            problems.append(f"公開後のResolutionが不正: {r2}")
        out = adapter.propagate_vocabulary_operation(
            "TOP-MCP-001", [c_term], "2026-08-06T13:04:00+09:00", _PROJECT)
        e2e_calls.append(("propagate_vocabulary_operation", out))
        c_done = out["canonicals"][0]
        slot = c_done["resolution"]["slots"]["/rimay_core/response/actor"]
        if c_done["rimay_core"]["response"].get("actor") != "RadioSystem" or \
                slot.get("status") != "confirmed" or slot.get("dependency_refs"):
            problems.append(f"伝播確定が不成立: {slot}")
        if out["operation"]["status"] != "completed":
            problems.append("operationが完了しない")
        # 却下経路＋全出力のJSON直列化
        out_b = adapter.observe_term_occurrence(
            _PROJECT,
            {"surface_form": "在庫照会システム", "expected_types": ["actor"],
             "target_path": "/rimay_core/response/actor"},
            document_id="DOC-MCP", requirement_id="REQ-MCP-REJ",
            channel="dialogue", observed_at="2026-08-06T13:05:00+09:00")
        out_r = adapter.reject_term_candidate(
            out_b["candidate"]["candidate_id"], out_b["candidate"]["revision"],
            reviewer="usa", decided_at="2026-08-06T13:06:00+09:00",
            project_id=_PROJECT, reason="案件対象外")
        e2e_calls.append(("reject_term_candidate", out_r))
        for name, payload in e2e_calls:
            try:
                json.dumps(payload, ensure_ascii=False)
            except Exception as e:  # noqa: BLE001
                problems.append(f"{name}: JSON直列化不可 {e}")
    finally:
        adapter.VOCABULARY_ROOT = keep_vroot
        adapter.VOCABULARY_REGISTRY = keep_registry
        shutil.rmtree(tmp, ignore_errors=True)
    results.append({"case_id": "MCP-TERMINOLOGY-E2E",
                    "verdict": "FAIL" if problems else "PASS",
                    "detail": "; ".join(problems[:3]) or
                    "発見→依存blocking→承認Receipt→公開→影響分析→伝播確定→却下の"
                    "全10ツールがJSON直列化可能で一周成立"})

    # --- 統制の透過（Adapter経由でも同じ統制が働く） ---
    problems = []
    g = copy.deepcopy(gap_can)
    base = {"operation": "replace_slot", "requirement_id": g["requirement_id"],
            "path": "/rimay_core/response/destination",
            "new_value": "CustomerEmailAddress",
            "evidence": {"type": "tool_result", "reference": "governance"}}
    if adapter.apply_canonical_patch(
            g, {**base, "base_revision": g["revision"],
                "new_status": "confirmed"})["ok"]:
        problems.append("tool_result根拠のconfirmedが拒否されない")
    if adapter.apply_canonical_patch(
            g, {**base, "base_revision": 999, "new_status": "proposed"})["ok"]:
        problems.append("revision競合が拒否されない")
    ac = adapter.generate_acceptance_criteria(g)  # 非approved
    if not ac.get("findings"):
        problems.append("非approvedの受入基準生成が拒否されない")
    results.append({"case_id": "MCP-GOVERNANCE",
                    "verdict": "FAIL" if problems else "PASS",
                    "detail": "; ".join(problems) or
                    "確定根拠検査・楽観ロック・approved限定生成が透過"})

    # --- FastMCP登録（サーバ起動なし） ---
    problems = []
    try:
        from mcp.server.fastmcp import FastMCP
        server = FastMCP("rimay-jp-check")
        for tool in adapter.TOOLS:
            server.tool()(tool)
        detail = f"FastMCPへ{len(adapter.TOOLS)}ツール登録成功（mcp<2）"
    except ImportError:
        detail = "mcp未導入環境のためSKIP（ハンドラ検査は完了）"
    except Exception as e:  # noqa: BLE001
        problems.append(f"登録失敗: {e}")
        detail = ""
    results.append({"case_id": "MCP-REGISTRATION",
                    "verdict": "FAIL" if problems else "PASS",
                    "detail": "; ".join(problems) or detail})

    summary = {"pass": sum(1 for r in results if r["verdict"] == "PASS"),
               "fail": sum(1 for r in results if r["verdict"] == "FAIL")}
    return {"results": results, "summary": summary}
