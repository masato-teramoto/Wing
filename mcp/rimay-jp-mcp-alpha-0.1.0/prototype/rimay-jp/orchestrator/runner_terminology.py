"""語彙発見・承認ループの契約検査（ADR-0014 P0-2/3/4、Gate 1〜5・7の一部）。

一時ディレクトリ上で発見→候補→承認→公開の一周を機械検査する。
リポジトリの実ストア・実Snapshotには書き込まない。
"""
from __future__ import annotations

import shutil
import tempfile
from pathlib import Path

from . import _ROOT  # noqa: F401
from rimay_jp_core.normalizer import normalize  # noqa: E402
from rimay_jp_core.lexicon import (  # noqa: E402
    terms, lookup_jp, load_vocabulary, current_snapshot_id)
from rimay_jp_core.validator import validate, terminology_findings  # noqa: E402
from rimay_jp_core.model import is_blocked  # noqa: E402
from .terminology import (  # noqa: E402
    TerminologyStore, observations_from, resolve_surface,
    candidate_not_resolvable, attach_dependency, ambiguity_findings, propagate)

_TEXT = "ラジオシステムは注文一覧を注文画面に表示しなければならない。"
_AT = "2026-08-06T12:00:00+09:00"


def _case(results, cid, problems, ok_detail):
    results.append({"case_id": cid, "verdict": "FAIL" if problems else "PASS",
                    "detail": "; ".join(problems) or ok_detail})


def run_terminology_checks() -> dict:
    results: list[dict] = []
    tmp = Path(tempfile.mkdtemp(prefix="rimay-term-"))
    try:
        store = TerminologyStore(tmp / "terminology")

        # --- Gate 1: 未知語→構造化Observation（メッセージ解析なし・span付き） ---
        problems = []
        c, findings = normalize(_TEXT, "REQ-RADIO-001")
        lex = [f for f in findings if f["code"] == "JP-LEXICAL"]
        ev = (lex[0].get("evidence") or {}) if lex else {}
        if ev.get("surface_form") != "ラジオシステム" or \
                ev.get("expected_types") != ["actor"]:
            problems.append(f"evidence不備: {ev}")
        obs = observations_from(findings, _TEXT)
        if len(obs) != 1 or obs[0]["source_span"] != {"start": 0, "end": 7} or \
                obs[0]["target_path"] != "/rimay_core/response/actor":
            problems.append(f"Observation不備: {obs}")
        _case(results, "TERM-OBSERVATION", problems,
              "JP-LEXICAL evidenceからsurface/type/span/path付きObservation生成")

        # --- D2: 検出の純粋性（normalize/observeの副作用境界とidempotency） ---
        problems = []
        normalize(_TEXT, "REQ-RADIO-001")
        if store.occurrences():
            problems.append("normalizeがストアへ書き込んだ（純粋性違反）")
        occ1 = store.observe(obs[0], document_id="DOC-T01",
                             requirement_id="REQ-RADIO-001",
                             channel="normalizer", observed_at=_AT)
        occ2 = store.observe(obs[0], document_id="DOC-T01",
                             requirement_id="REQ-RADIO-001",
                             channel="normalizer", observed_at=_AT)
        if occ1["occurrence_id"] != occ2["occurrence_id"] or \
                len(store.occurrences()) != 1:
            problems.append("observeがidempotentでない")
        if "status" in occ1:
            problems.append("Occurrenceが状態を持つ（不変イベント違反）")
        _case(results, "TERM-PURITY", problems,
              "normalize無副作用・observe明示操作・自然キーidempotent・不変イベント")

        # --- D6: Action表現はTerm Candidateへ流さない ---
        problems = []
        _, f2 = normalize("注文管理システムは注文データをアーカイブしなければならない。",
                          "REQ-ACT-001")
        lex2 = [f for f in f2 if f["code"] == "JP-LEXICAL"]
        if not lex2 or (lex2[0].get("evidence") or {}).get("kind") != \
                "action_expression":
            problems.append(f"動詞evidenceにaction_expression印がない: {lex2}")
        if observations_from(f2, ""):
            problems.append("Action表現がObservation化された（D6違反）")
        _case(results, "TERM-ACTION-ROUTING", problems,
              "未知動詞はaction_expression印・Term Candidate経路から除外")

        # --- D3: Resolver多値化（5種のkind） ---
        problems = []
        vocab = list(terms()) + [
            {"id": "ContractRegistrationSales", "preferred_japanese": "契約登録",
             "type": "class", "synonyms": [], "homonym": True, "scope": "sales"},
            {"id": "ContractRegistrationAudit", "preferred_japanese": "契約登録",
             "type": "class", "synonyms": [], "homonym": True, "scope": "audit"},
            {"id": "OldBillingSystem", "preferred_japanese": "旧請求システム",
             "type": "actor", "synonyms": [], "status": "deprecated",
             "superseded_by": "BillingSystem"},
        ]
        for surface, kind in (("注文管理システム", "exact"), ("メール", "synonym"),
                              ("契約登録", "ambiguous"), ("ラジオシステム", "not_found"),
                              ("旧請求システム", "deprecated")):
            r = resolve_surface(surface, vocab=vocab)
            if r["kind"] != kind:
                problems.append(f"{surface}: {kind}期待が{r['kind']}")
        if len(resolve_surface("契約登録", vocab=vocab)["matches"]) != 2:
            problems.append("ambiguousのmatchesが多値でない")
        _case(results, "TERM-RESOLVER", problems,
              "exact/synonym/ambiguous/not_found/deprecatedの5種判定＋多値matches")

        # --- Gate 2: 候補語は正規化で解決されない ---
        problems = []
        cand = store.ensure_candidate(occ1)
        cand2 = store.ensure_candidate(occ1)
        if cand2["candidate_id"] != cand["candidate_id"] or \
                len(store.candidates()) != 1:
            problems.append("ensure_candidateがidempotentでない")
        if lookup_jp("ラジオシステム") is not None:
            problems.append("候補語がlookup_jpで解決された")
        _, f3 = normalize(_TEXT, "REQ-RADIO-001")
        if not any(f["code"] == "JP-LEXICAL" for f in f3):
            problems.append("候補登録後にNormalizerが解決してしまう")
        if candidate_not_resolvable(store):
            problems.append("candidate_not_resolvable違反")
        _case(results, "TERM-CANDIDATE-ISOLATION", problems,
              "候補ストアの語はNormalizer/lookup_jpから隔離（公開まで解決不可）")

        # --- 楽観ロック ---
        problems = []
        try:
            store.update_candidate(cand["candidate_id"], base_revision=99,
                                   patch={"status": "under_review"})
            problems.append("revision conflictが検出されない")
        except ValueError:
            pass
        _case(results, "TERM-REVISION-LOCK", problems,
              "base_revision不一致の書き込みを拒否")

        # --- Gate 5＋D5: Receipt必須の公開・immutable Snapshot・供給境界 ---
        problems = []
        cand = store.update_candidate(
            cand["candidate_id"], cand["revision"],
            {"proposed_term": {"id": "RadioSystem",
                               "preferred_japanese": "ラジオシステム",
                               "type": "actor", "synonyms": [],
                               "definition": "ラジオ聴取機能を提供するシステム"},
             "evidence": [{"type": "user_answer",
                           "reference": "dialogue:TEST/Q-01"}],
             "status": "under_review"})
        lex_base = tmp / "lexicon"
        try:
            store.publish_snapshot("VOC-TEST-001", lexicon_base=lex_base,
                                   base_vocab=terms(),
                                   candidate_ids=[cand["candidate_id"]],
                                   operation_id="TOP-001", published_at=_AT)
            problems.append("承認前の公開が拒否されない（Gate 5違反）")
        except ValueError:
            pass
        receipt = store.approve(cand["candidate_id"], cand["revision"],
                                reviewer="usa", approved_at=_AT,
                                decision_reason="テスト承認")
        if store.receipt(receipt["receipt_id"]) is None:
            problems.append("Receiptが永続化されていない")
        op = store.publish_snapshot("VOC-TEST-001", lexicon_base=lex_base,
                                    base_vocab=terms(),
                                    candidate_ids=[cand["candidate_id"]],
                                    operation_id="TOP-001", published_at=_AT)
        loaded = load_vocabulary("VOC-TEST-001", base=lex_base)
        if not any(t["id"] == "RadioSystem" for t in loaded):
            problems.append("公開SnapshotへTermが入っていない")
        if resolve_surface("ラジオシステム", vocab=loaded)["kind"] != "exact":
            problems.append("公開後のResolverが解決しない")
        if lookup_jp("ラジオシステム") is not None:
            problems.append("公開前Snapshot（bootstrap）供給が汚染された")
        try:
            store.publish_snapshot("VOC-TEST-001", lexicon_base=lex_base,
                                   base_vocab=terms(),
                                   candidate_ids=[cand["candidate_id"]],
                                   operation_id="TOP-002", published_at=_AT)
            problems.append("同一Snapshot再公開が拒否されない（immutable違反）")
        except ValueError:
            pass
        _case(results, "TERM-RECEIPT-PUBLISH", problems,
              "Receiptなし公開拒否→承認→immutable Snapshot公開→ID指定供給")

        # --- Gate 7骨格＋D5: 伝播Sagaと影響分類（re-resolve） ---
        problems = []
        if op["status"] != "propagating" or \
                op["affected_requirements"].get("REQ-RADIO-001") != "pending" or \
                op["impact_kind"].get("REQ-RADIO-001") != "re-resolve":
            problems.append(f"影響計画が不正: {op}")
        if "REQ-RADIO-001" not in store.pending_requirements():
            problems.append("伝播未完了要求がpending_requirementsに出ない")
        # 無関係Snapshot公開（衝突なし新語のみ）は影響ゼロ
        occ_b = store.observe(
            {"surface_form": "在庫照会システム", "expected_types": ["actor"],
             "target_path": "/rimay_core/response/actor"},
            document_id="DOC-T02", requirement_id="REQ-STOCK-001",
            channel="normalizer", observed_at=_AT)
        cand_b = store.ensure_candidate(occ_b)
        cand_b = store.update_candidate(
            cand_b["candidate_id"], cand_b["revision"],
            {"proposed_term": {"id": "StockInquirySystem",
                               "preferred_japanese": "在庫照会システム",
                               "type": "actor", "synonyms": []},
             "status": "under_review"})
        store.approve(cand_b["candidate_id"], cand_b["revision"],
                      reviewer="usa", approved_at=_AT)
        store.record_resolution(occ_b["occurrence_id"], "resolved",
                                resolved_term_id="StockInquirySystem",
                                snapshot_id="VOC-TEST-002", resolved_at=_AT)
        op2 = store.publish_snapshot("VOC-TEST-002", lexicon_base=lex_base,
                                     base_vocab=loaded,
                                     candidate_ids=[cand_b["candidate_id"]],
                                     operation_id="TOP-003", published_at=_AT)
        if "REQ-RADIO-001" in op2["affected_requirements"]:
            problems.append("解決済み・無関係要求が影響に含まれた")
        _case(results, "TERM-SAGA-IMPACT", problems,
              "operation記録・pending遮断集合・未解決同surfaceのみre-resolve対象")
        # --- D4: dependency_refs→TERM_APPROVAL_PENDING（blocking）＋多義・廃止語 ---
        problems = []
        c_dep, _ = normalize(_TEXT, "REQ-RADIO-001")
        attach_dependency(c_dep, "/rimay_core/response/actor",
                          cand["candidate_id"])
        fdep = validate(c_dep, phase2_slice=False)
        tap = [f for f in fdep if f["code"] == "TERM_APPROVAL_PENDING"]
        if not tap or not tap[0]["blocking"] or not is_blocked(fdep):
            problems.append(f"TERM_APPROVAL_PENDINGがblocking発火しない: {tap}")
        if (tap and tap[0].get("evidence", {}).get("candidate_ref")
                != cand["candidate_id"]):
            problems.append("candidate_refがevidenceにない")
        amb = ambiguity_findings(
            [{"surface_form": "契約登録",
              "target_path": "/rimay_core/response/theme"}], vocab)
        if len(amb) != 1 or amb[0]["code"] != "AMBIGUOUS_TERM" or \
                not amb[0]["blocking"]:
            problems.append(f"AMBIGUOUS_TERM不発火: {amb}")
        dep_f = terminology_findings(
            {"rimay_core": {"response": {"actor": "OldBillingSystem"}},
             "resolution": {"slots": {}}},
            term_meta={"OldBillingSystem": {"status": "deprecated",
                                            "superseded_by": "BillingSystem"}})
        if len(dep_f) != 1 or dep_f[0]["code"] != "DEPRECATED_TERM" or \
                dep_f[0]["blocking"]:
            problems.append(f"DEPRECATED_TERM（warning）不発火: {dep_f}")
        _case(results, "TERM-DEPENDENCY-BLOCKING", problems,
              "候補依存=blocking承認遮断・homonym=AMBIGUOUS_TERM・廃止語=warning")

        # --- Gate 7: Saga伝播（Patch適用・依存解消・idempotent） ---
        problems = []
        canonicals = {"REQ-RADIO-001": c_dep}
        op_done = propagate(store, "TOP-001", canonicals, applied_at=_AT)
        c_after = canonicals["REQ-RADIO-001"]
        slot = c_after["resolution"]["slots"]["/rimay_core/response/actor"]
        if c_after["rimay_core"]["response"].get("actor") != "RadioSystem" or \
                slot.get("status") != "confirmed":
            problems.append(f"伝播Patch不成立: {slot}")
        if slot.get("dependency_refs"):
            problems.append("依存が解消されていない")
        if any(f["code"] == "TERM_APPROVAL_PENDING"
               for f in validate(c_after, phase2_slice=False)):
            problems.append("伝播後もTERM_APPROVAL_PENDINGが残る")
        if op_done["affected_requirements"].get("REQ-RADIO-001") != "completed" \
                or op_done["status"] != "completed":
            problems.append(f"operation未完了: {op_done['status']}")
        if "REQ-RADIO-001" in store.pending_requirements():
            problems.append("完了後もpending扱い")
        rev = c_after["revision"]
        op_re = propagate(store, "TOP-001", canonicals, applied_at=_AT)
        if canonicals["REQ-RADIO-001"]["revision"] != rev or \
                op_re["status"] != "completed":
            problems.append("再実行がidempotentでない（重複Patch）")
        res_map = store.resolutions()
        if res_map.get(occ1["occurrence_id"], {}).get("resolved_term_id") \
                != "RadioSystem":
            problems.append("Resolutionが記録されていない")
        _case(results, "TERM-PROPAGATION", problems,
              "knowledge_asset Patch→confirmed・依存解消・operation完了・再実行安全")

        # --- Gate 6/9: 参照指紋STALE（無関係な公開で古くならない） ---
        problems = []
        import copy as _copy
        from .validation_router import validate_all
        from .validation_report import validation_is_stale
        c_ok, f_ok = normalize(
            "通知システムは請求書PDFを顧客メールアドレスに送信しなければならない。",
            "REQ-STALE-001")
        validate_all(c_ok)
        state = c_ok.get("validation_state") or {}
        # 検査の意図は「検証時の語彙Snapshotと指紋が記録されていること」。
        # 現行Snapshot IDと比較する（"VOC-BOOTSTRAP" 固定はSnapshot機構が
        # 未稼働だった時期の前提。N-01解消により固定値では成立しない）。
        if state.get("validated_vocabulary_snapshot") != current_snapshot_id() or \
                not state.get("validated_term_fingerprint"):
            problems.append(f"語彙Snapshot/指紋未記録: {state}")
        if validation_is_stale(c_ok):
            problems.append("同一語彙でSTALE誤判定")
        base_terms = list(terms())
        unrelated = base_terms + [{"id": "RadioSystem",
                                   "preferred_japanese": "ラジオシステム",
                                   "type": "actor", "synonyms": []}]
        if validation_is_stale(c_ok, current_vocab=unrelated):
            problems.append("無関係な新語追加でSTALEになった（Gate 6違反）")
        mutated = _copy.deepcopy(base_terms)
        for t in mutated:
            if t["id"] == "InvoicePDF":
                t["type"] = "property"  # 参照termのtype変更
        if not validation_is_stale(c_ok, current_vocab=mutated):
            problems.append("参照termの変更がSTALEにならない")
        homo = base_terms + [{"id": "InvoicePDF2",
                              "preferred_japanese": "請求書PDF",
                              "type": "class", "synonyms": [],
                              "homonym": True}]
        if not validation_is_stale(c_ok, current_vocab=homo):
            problems.append("参照表層へのhomonym追加がSTALEにならない")
        _case(results, "TERM-STALE", problems,
              "参照指紋方式: 無関係公開は不変・参照term変更/同表層homonymでSTALE")

        # --- Gate 6: 変更系公開の影響4分類 ---
        problems = []
        vocab_now = list(load_vocabulary("VOC-TEST-002", base=lex_base))

        def _change_candidate(surface, req, proposed):
            occ = store.observe(
                {"surface_form": surface, "expected_types": ["actor"],
                 "target_path": "/rimay_core/response/actor"},
                document_id="DOC-CHG", requirement_id=req,
                channel="dialogue", observed_at=_AT)
            cc = store.ensure_candidate(occ)
            cc = store.update_candidate(cc["candidate_id"], cc["revision"],
                                        {"proposed_term": proposed,
                                         "status": "under_review"})
            store.approve(cc["candidate_id"], cc["revision"],
                          reviewer="usa", approved_at=_AT)
            return store.candidate(cc["candidate_id"])

        cc_type = _change_candidate(
            "ラジオシステム変更", "REQ-CHG-TYPE",
            {"id": "RadioSystem", "preferred_japanese": "ラジオシステム",
             "type": "class", "synonyms": []})
        cc_dep = _change_candidate(
            "在庫照会システム廃止", "REQ-CHG-DEP",
            {"id": "StockInquirySystem", "preferred_japanese": "在庫照会システム",
             "type": "actor", "synonyms": [], "status": "deprecated",
             "superseded_by": "OrderManagementSystem"})
        op3 = store.publish_snapshot(
            "VOC-TEST-003", lexicon_base=lex_base, base_vocab=vocab_now,
            candidate_ids=[cc_type["candidate_id"], cc_dep["candidate_id"]],
            operation_id="TOP-004", published_at=_AT,
            requirement_term_index={"REQ-USES-RADIO": ["RadioSystem"],
                                    "REQ-UNRELATED": ["InvoicePDF"]})
        ik = op3["impact_kind"]
        if ik.get("REQ-USES-RADIO") != "re-validate":
            problems.append(f"type変更がre-validateでない: {ik}")
        if ik.get("REQ-RADIO-001") != "re-validate":
            problems.append(f"Resolution逆引きがre-validateでない: {ik}")
        if ik.get("REQ-STOCK-001") != "stale":
            problems.append(f"廃止がstaleでない: {ik}")
        if "REQ-UNRELATED" in ik:
            problems.append("無関係要求が影響に含まれた")
        if op3["term_changes"].get("RadioSystem") != "re-validate" or \
                op3["term_changes"].get("StockInquirySystem") != "stale":
            problems.append(f"term_changes分類不正: {op3['term_changes']}")
        if op3["status"] != "completed" or \
                any(v not in ("advisory",)
                    for v in op3["affected_requirements"].values()):
            problems.append("advisory影響がpending扱い（Saga誤遮断）")
        pub = {t["id"]: t
               for t in load_vocabulary("VOC-TEST-003", base=lex_base)}
        if pub["RadioSystem"]["type"] != "class" or \
                pub["StockInquirySystem"].get("status") != "deprecated":
            problems.append("変更が公開Snapshotへ反映されていない")
        if resolve_surface("在庫照会システム",
                           vocab=list(pub.values()))["kind"] != "deprecated":
            problems.append("廃止語がResolverでdeprecatedにならない")
        _case(results, "TERM-CHANGE-IMPACT", problems,
              "変更公開: type→re-validate・廃止→stale・index/Resolution逆引き・"
              "無関係不干渉・advisory非遮断")

        # --- D6: Action表現写像のSSOT一致（Python直書きの再発防止） ---
        problems = []
        from rimay_jp_core.lexicon import normalizer_profile
        from .candidate_extractor import _VERB_CANDIDATES
        ssot = normalizer_profile()["action_expressions"]
        if not ssot:
            problems.append("Profileにaction_expressionsが無い")
        for k, v in ssot.items():
            if _VERB_CANDIDATES.get(k) != v:
                problems.append(f"抽出器とSSOTの乖離: {k}")
        multi = [k for k, v in ssot.items() if len(v) > 1]
        if not multi:
            problems.append("多義動詞（複数候補）がSSOTに無い")
        _case(results, "TERM-ACTION-SSOT", problems,
              "自由文動詞→family候補写像がProfile SSOTから供給されている")

        # --- P1: 文書Term Extractor（決定論・純粋・根拠付き） ---
        problems = []
        from .document_term_extractor import extract_document_terms
        doc = ("# 概要\n注文管理システムを刷新する。\n"
               "## 要望\nラジオ局一覧をメールで配信したい。契約登録も行う。\n")
        out1 = extract_document_terms(doc, "DOC-X", vocab=vocab)
        out2 = extract_document_terms(doc, "DOC-X", vocab=vocab)
        if out1 != out2:
            problems.append("抽出が非決定的")
        if store.occurrences() and any(
                o["source"]["document_id"] == "DOC-X"
                for o in store.occurrences()):
            problems.append("抽出が書き込みを行った（純粋性違反）")
        if out1["resolved"].get("注文管理システム") != "OrderManagementSystem" \
                or out1["resolved"].get("メール") != "Email":
            problems.append(f"既登録語がresolvedにない: {out1['resolved']}")
        if not any(a["surface_form"] == "契約登録" for a in out1["ambiguous"]):
            problems.append("homonymがambiguousに分類されない")
        radio = [o for o in out1["observations"]
                 if o["surface_form"] == "ラジオ局一覧"]
        if not radio:
            problems.append("未知語がObservation化されない")
        else:
            sp = radio[0]["source_span"]
            if doc[sp["start"]:sp["end"]] != "ラジオ局一覧" or \
                    radio[0]["section_id"] != "要望":
                problems.append(f"span/節の根拠不正: {radio[0]}")
        if any(o["surface_form"] in out1["resolved"]
               for o in out1["observations"]):
            problems.append("既登録語が候補化された")
        occ_doc = store.observe(radio[0], document_id="DOC-X",
                                requirement_id="REQ-DOC-001",
                                channel="document", observed_at=_AT)
        if occ_doc["channel"] != "document":
            problems.append("document経路のOccurrence化が不正")
        _case(results, "TERM-DOC-EXTRACTOR", problems,
              "決定論・無副作用・resolved/ambiguous分類・span根拠・observe接続")

        # --- P1: 横断集約・scope解決・昇格候補 ---
        problems = []
        from .terminology import candidate_summary, promotion_candidates
        occ_y = store.observe({"surface_form": "ラジオシステム",
                               "expected_types": ["actor"],
                               "target_path": "/rimay_core/response/actor"},
                              document_id="DOC-Y",
                              requirement_id="REQ-RADIO-002",
                              channel="dialogue", observed_at=_AT)
        store.ensure_candidate(occ_y)
        summ = {s["surface_form"]: s for s in candidate_summary(store)}
        radio_s = summ.get("ラジオシステム") or {}
        if radio_s.get("occurrences", 0) < 2 or \
                len(radio_s.get("requirements", [])) < 2 or \
                len(radio_s.get("documents", [])) < 2:
            problems.append(f"横断集約が不正: {radio_s}")
        r_scope = resolve_surface("契約登録", vocab=vocab, scope="sales")
        if r_scope["kind"] != "exact" or not r_scope.get("scope_filtered"):
            problems.append(f"scope解決が働かない: {r_scope}")
        if resolve_surface("契約登録", vocab=vocab)["kind"] != "ambiguous":
            problems.append("scope未指定でambiguousにならない")
        promo = promotion_candidates({
            "billing": [{"id": "p1/Customer", "preferred_japanese": "顧客",
                         "type": "actor", "definition": "契約主体",
                         "scope": "project:billing", "provenance": ["DOC-B"]}],
            "device": [{"id": "p2/Customer", "preferred_japanese": "顧客",
                        "type": "actor", "definition": "契約主体",
                        "scope": "project:device", "provenance": ["DOC-D"]},
                       {"id": "p2/Terminal", "preferred_japanese": "端末X",
                        "type": "class", "scope": "project:device"}],
            "sales": [{"id": "p3/Customer", "preferred_japanese": "顧客",
                       "type": "class", "definition": "請求先",
                       "scope": "project:sales", "provenance": ["DOC-S"]}]})
        cust = next((p for p in promo if p["surface_form"] == "顧客"), {})
        if not cust or cust.get("eligible") or not cust.get("definition_conflict"):
            problems.append(f"定義競合の検出不正: {cust}")
        promo2 = promotion_candidates({
            "a": [{"id": "a/X", "preferred_japanese": "検証結果票",
                   "type": "class", "definition": "d", "scope": "project:a",
                   "provenance": ["DOC-A"]}],
            "b": [{"id": "b/X", "preferred_japanese": "検証結果票",
                   "type": "class", "definition": "d", "scope": "project:b",
                   "provenance": ["DOC-B"]}]})
        if not promo2 or not promo2[0]["eligible"]:
            problems.append(f"適格昇格候補が出ない: {promo2}")
        if any(p["surface_form"] == "端末X" for p in promo):
            problems.append("単一案件語が昇格候補に混入")
        _case(results, "TERM-MULTIPROJECT", problems,
              "横断集約（出現/要求/文書）・scope一意化・昇格候補=2案件+無競合のみ")
    finally:
        shutil.rmtree(tmp, ignore_errors=True)

    summary = {"pass": sum(1 for r in results if r["verdict"] == "PASS"),
               "fail": sum(1 for r in results if r["verdict"] == "FAIL")}
    return {"results": results, "summary": summary}
