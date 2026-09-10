"""Lexical Analysis Provider／Lexicon Overlayの契約検査（改善計画 v0.3 §10.1/10.2）。

- Provider fail-closed、token原文契約、D2三段階（raw候補→B/C境界検証→
  最長一致＋否定接辞stop）、3値契約、regex baseline非回帰、Strict非影響、
  offline実行、Provenance記録を機械検査する。
- sudachipyがロード不能な環境では該当caseを**明示的にFAIL**させる
  （§7.3 fail-closed。silent skipしない。CIはpin済み依存を導入する）。
"""
from __future__ import annotations

import json
import socket
from pathlib import Path

import yaml

from . import _ROOT
from rimay_jp_core.lexicon import terms  # noqa: E402
from .japanese_lexical_analysis import (  # noqa: E402
    LexicalCapabilityUnavailable, RegexProvider, get_provider)
from .lexicon_overlay import (  # noqa: E402
    fixture_outcome, overlay, raw_surface_candidates)
from .document_term_extractor import extract_document_terms  # noqa: E402

_LEXDIR = Path(_ROOT) / "corpus" / "lexical"


def _case(results, cid, problems, ok_detail):
    results.append({"case_id": cid, "verdict": "FAIL" if problems else "PASS",
                    "detail": "; ".join(problems) or ok_detail})


def _sudachi_or_none(problems):
    try:
        return get_provider("sudachipy", dictionary="core")
    except LexicalCapabilityUnavailable as e:
        problems.append(f"capability unavailable（fail-closed）: {e}")
        return None


def run_lexical_checks() -> dict:
    results: list = []
    vocab = list(terms())

    # --- Provider契約: fail-closed・境界mode制限 ---
    problems = []
    try:
        get_provider("nope")
        problems.append("未知Providerが例外にならない")
    except ValueError:
        pass
    try:
        overlay("x", vocab, [], boundary_split_mode="A")
        problems.append("境界検証mode Aが拒否されない（D2: B/C限定）")
    except ValueError:
        pass
    rp = RegexProvider()
    if [t.surface for t in rp.analyze("注文一覧を表示")] != ["注文一覧", "表示"]:
        problems.append("RegexProviderが現行token走査と一致しない")
    _case(results, "LEX-PROVIDER-CONTRACT", problems,
          "未知Provider拒否・境界mode B/C限定・regex baseline token一致")

    # --- Sudachi token原文契約（offset・辞書形・正規化形・中黒・踊り字） ---
    problems = []
    sp = _sudachi_or_none(problems)
    if sp is not None:
        text = "オンライン・ショップで見積りと個々のOAuth認証を扱う。"
        toks = sp.analyze(text, mode="C")
        for t in toks:
            if text[t.start:t.end] != t.surface:
                problems.append(f"offsetが原文sliceと不一致: {t}")
        by_surface = {t.surface: t for t in toks}
        if by_surface.get("見積り") is None or \
                by_surface["見積り"].normalized_form != "見積もり":
            problems.append("見積りのnormalized_formが取れない")
        if "個々" not in by_surface:
            problems.append("踊り字（個々）が1tokenにならない")
        if by_surface.get("扱う") is None or \
                by_surface["扱う"].dictionary_form != "扱う":
            problems.append("dictionary_formが取れない")
        if not all(isinstance(t.is_oov, bool) for t in toks):
            problems.append("is_oovがboolでない")
    _case(results, "LEX-TOKEN-CONTRACT", problems,
          "surface=原文slice・辞書形・正規化形・踊り字・OOVフラグ")

    # --- D2三段階＋3値契約（negative fixtureをB/C両modeで） ---
    problems = []
    sp = sp if sp is not None else _sudachi_or_none(problems)
    if sp is not None:
        neg = yaml.safe_load(
            (_LEXDIR / "negative-fixtures.yaml").read_text(encoding="utf-8"))
        for case in neg["cases"]:
            if case["kind"] == "residual":
                continue
            text, term = case["text"].strip(), case["term"]
            expect = case["expect"]
            for bmode in ("B", "C"):
                cands = overlay(text, vocab, sp.analyze(text, mode=bmode),
                                boundary_split_mode=bmode)["candidates"]
                got = fixture_outcome(text, term, cands)
                if got == "not_generated":
                    problems.append(
                        f"{case['fixture_id']}: not_generated"
                        "（fixture設計不備。P0 fail）")
                elif got != expect["boundary"]:
                    problems.append(
                        f"{case['fixture_id']}({bmode}): {got} != "
                        f"{expect['boundary']}")
        # 3値のnot_generated判定自体の検査（存在しない表層）
        if fixture_outcome("請求書類を保管する。", "存在しない語",
                           raw_surface_candidates("請求書類を保管する。",
                                                  vocab)) != "not_generated":
            problems.append("not_generated判定が機能しない")
    _case(results, "LEX-OVERLAY-3VALUE", problems,
          "raw候補生成→B/C境界検証の3値がnegative fixture期待と一致")

    # --- 否定接辞stop policy（span外側隣接のみ・内部は抑制しない） ---
    problems = []
    if sp is not None:
        def _final(text):
            return extract_document_terms(text, "DOC-NEG",
                                          provider="sudachipy")
        out = _final("処理が不成功のとき、再試行する。")
        st = {n["surface_form"]: n["negation"]
              for n in out["negation_stopped"]}
        if st.get("成功") != {"side": "prefix", "morpheme": "不"}:
            problems.append(f"不成功→成功がstopされない: {st}")
        if "成功" in out["resolved"]:
            problems.append("stop対象がresolvedに混入")
        out = _final("受付不可の場合、拒否する。")
        if not any(n["surface_form"] == "受付" and
                   n["negation"]["morpheme"] == "不可"
                   for n in out["negation_stopped"]):
            problems.append("受付不可→受付がstopされない")
        out = _final("注文が未確定の場合、通知する。")
        if out["resolved"].get("未確定") != "Unconfirmed":
            problems.append("登録表層（未確定）がspan内部の接頭辞で抑制された")
        if out["negation_stopped"]:
            problems.append(f"未確定が誤ってstopされた: {out['negation_stopped']}")
        out = _final("設定が無効のとき、記録する。")
        if out["resolved"].get("無効") != "Inactive":
            problems.append("登録表層（無効）が抑制された")
    _case(results, "LEX-NEGATION-STOP", problems,
          "否定接辞はspan外側隣接のみ参照・無効／未確定自身は抑制しない")

    # --- Extractor sudachipy経路（送り仮名・残差・正規化キー非解決） ---
    problems = []
    if sp is not None:
        doc = ("# 要望\n問い合わせと払い戻し、取り消し、見積り、割り当てを扱う。\n"
               "注文管理システム画面表示処理を刷新する。\n")
        out1 = extract_document_terms(doc, "DOC-L", provider="sudachipy")
        out2 = extract_document_terms(doc, "DOC-L", provider="sudachipy")
        if json.dumps(out1, ensure_ascii=False, sort_keys=True) != \
                json.dumps(out2, ensure_ascii=False, sort_keys=True):
            problems.append("sudachipy経路が非決定的")
        surfaces = {o["surface_form"] for o in out1["observations"]}
        missing = {"問い合わせ", "払い戻し", "取り消し", "見積り",
                   "割り当て"} - surfaces
        if missing:
            problems.append(f"送り仮名語が抽出されない: {sorted(missing)}")
        if out1["resolved"].get("注文管理システム") != "OrderManagementSystem":
            problems.append("既知複合の既知部分がresolvedされない")
        residual = [o for o in out1["observations"]
                    if o["surface_form"] == "画面表示処理"]
        if not residual:
            problems.append("既知＋未知複合の残差が候補化されない")
        elif residual[0].get("context_span") is None or \
                doc[residual[0]["context_span"]["start"]:
                    residual[0]["context_span"]["end"]] != "注文管理システム画面表示処理":
            problems.append(f"複合span文脈が不正: {residual[0]}")
        for o in out1["observations"]:
            s = o["source_span"]
            if doc[s["start"]:s["end"]] != o["surface_form"]:
                problems.append(f"surface_formが原文sliceと不一致: {o}")
        mi = [o for o in out1["observations"] if o["surface_form"] == "見積り"]
        if mi and mi[0].get("normalized_surface") != "見積もり":
            problems.append("normalized_surfaceが記録されない")
        if "見積り" in out1["resolved"] or "見積もり" in out1["resolved"]:
            problems.append("normalized_surfaceで自動resolvedされた（D3違反）")
    _case(results, "LEX-EXTRACTOR-SUDACHI", problems,
          "送り仮名抽出・既知複合の残差分離・span根拠・正規化キー非解決・決定論")

    # --- regex baseline非回帰（従来出力と同一。追加はprovenanceのみ） ---
    problems = []
    doc = ("# 概要\n注文管理システムを刷新する。\n"
           "## 要望\nラジオ局一覧をメールで配信したい。契約登録も行う。\n")
    out = extract_document_terms(doc, "DOC-X", vocab=vocab)  # 既定=regex
    legacy = _legacy_regex_extract(doc, "DOC-X", vocab)
    stripped = {k: v for k, v in out.items() if k != "analysis_provenance"}
    if stripped != legacy:
        problems.append("regex経路の出力が従来実装と一致しない")
    if out.get("analysis_provenance", {}).get("provider") != "regex":
        problems.append("regex provenanceが記録されない")
    if out["resolved"].get("注文管理システム") != "OrderManagementSystem":
        problems.append("既登録語resolved非回帰の期待値不一致")
    _case(results, "LEX-REGEX-BASELINE-UNCHANGED", problems,
          "provider=regex既定は従来出力＋analysis_provenanceのみ")

    # --- Strict Normalizer非影響（Provider選択と独立） ---
    problems = []
    from rimay_jp_core.normalizer import normalize
    text = "注文管理システムは注文確定通知を顧客メールアドレスに送信しなければならない。"
    before = json.dumps(normalize(text, "REQ-LX-1")[0],
                        ensure_ascii=False, sort_keys=True)
    if sp is not None:
        extract_document_terms(text, "DOC-STRICT", provider="sudachipy")
    after = json.dumps(normalize(text, "REQ-LX-1")[0],
                       ensure_ascii=False, sort_keys=True)
    if before != after:
        problems.append("Provider使用前後でStrict出力が変化した")
    _case(results, "LEX-STRICT-UNAFFECTED", problems,
          "Strict Normalizerの出力はProvider選択・使用に影響されない")

    # --- offline実行（FR相当: socket無効下でsudachipy経路が成功） ---
    problems = []
    if sp is not None:
        orig_socket, orig_conn = socket.socket, socket.create_connection

        def _boom(*a, **k):
            raise AssertionError("network access during lexical analysis")
        socket.socket = _boom  # type: ignore[assignment]
        socket.create_connection = _boom  # type: ignore[assignment]
        try:
            extract_document_terms("問い合わせを扱う。", "DOC-OFF",
                                   provider="sudachipy")
        except AssertionError as e:
            problems.append(str(e))
        finally:
            socket.socket, socket.create_connection = orig_socket, orig_conn
    _case(results, "LEX-OFFLINE", problems, "socket無効下でsudachipy経路が成功")

    # --- Provenance記録（D6: 版数＋実体hash＋両split mode） ---
    problems = []
    if sp is not None:
        meta = extract_document_terms("問い合わせを扱う。", "DOC-PV",
                                      provider="sudachipy")["analysis_provenance"]
        for key in ("provider", "provider_version", "dictionary_package",
                    "dictionary_version", "dictionary_content_hash",
                    "config_content_hash", "phrase_split_mode",
                    "boundary_validation_split_mode", "phrase_policy"):
            if not meta.get(key):
                problems.append(f"provenance欠落: {key}")
        for key in ("dictionary_content_hash", "config_content_hash"):
            if not str(meta.get(key, "")).startswith("sha256:"):
                problems.append(f"実体hashでない: {key}")
        if meta.get("boundary_validation_split_mode") not in ("B", "C"):
            problems.append("境界検証modeがB/C外")
    _case(results, "LEX-PROVENANCE", problems,
          "Provider版・辞書実体hash・設定hash・両split mode・policyを記録")

    # --- fixture資産の整合（P0成果物が壊れていないこと） ---
    problems = []
    try:
        gold = yaml.safe_load((_LEXDIR / "document-terms-gold.yaml")
                              .read_text(encoding="utf-8"))
        for d in gold["documents"]:
            for k in ("document_id", "text", "gold_candidates", "gold_known"):
                if k not in d:
                    problems.append(f"gold fixture欠落: {d.get('document_id')}/{k}")
        pairs = yaml.safe_load((_LEXDIR / "conjugation-minimal-pairs.yaml")
                               .read_text(encoding="utf-8"))
        if not pairs.get("conjugation_cases") or \
                not pairs.get("multi_predicate_cases"):
            problems.append("minimal pair fixtureが空")
        if not (_LEXDIR / "annotation-guideline.md").exists():
            problems.append("注釈指針が存在しない")
    except Exception as e:  # fixture破損はP0成果物の破損
        problems.append(f"fixture読込失敗: {e}")
    _case(results, "LEX-FIXTURES", problems,
          "注釈指針・gold・negative・minimal pairのP0資産が読める")


    # --- P2: 述語再構成（活用形・否定・複数述語。D5／§9.2） ---
    problems = []
    if sp is not None:
        import yaml as _yaml
        from .candidate_extractor import extract, heuristic_extract

        def _hx(text):
            return heuristic_extract(text, {"text": text,
                                            "document_id": "RUN-P2"},
                                     provider="sudachipy")

        def _fam(c):
            slot = c["resolution"]["slots"].get(
                "/rimay_core/response/action/family", {})
            fam = (c["rimay_core"]["response"].get("action") or {}).get("family")
            return (slot.get("status"), fam,
                    [x["value"] for x in slot.get("candidates", [])],
                    {a["kind"] for a in
                     c["extensions"].get("additional_semantics", [])})

        for tail in ("送信する", "送信した", "送信します"):
            st, fam, cands, _ = _fam(_hx(f"通知システムは注文確定通知を{tail}。"))
            if fam != "SEND" and "SEND" not in cands:
                problems.append(f"{tail}: SEND候補に対応しない")
            if st == "confirmed":
                problems.append(f"{tail}: 誤confirmed")
        st, fam, cands, sems = _fam(_hx("通知システムは注文確定通知を送信しない。"))
        if "SEND" not in ([fam] + cands):
            problems.append("送信しない: SEND候補に対応しない")
        if "negated_predicate" not in sems:
            problems.append("送信しない: 否定が記録されない")
        _, _, _, sems = _fam(_hx("通知システムは注文確定通知を送信して記録する。"))
        if "multiple_predicates" not in sems:
            problems.append("〜して〜する: 複数述語が検出されない")
        c = _hx("請求管理システムは請求書PDFを保存し、"
                "注文確定通知を送信しなければならない。")
        st, fam, cands, sems = _fam(c)
        if st == "confirmed" or fam is not None:
            problems.append("複数述語が単一Actionへ集約された")
        if not {"SEND", "STORE"} <= set(cands):
            problems.append(f"複数述語の候補集合不足: {cands}")
        st, fam, cands, sems = _fam(_hx(
            "通知システムは注文確定通知および承認警告を送信しなければならない。"))
        if "multiple_predicates" in sems:
            problems.append("名詞並列（および）を複数述語と誤判定")
        if fam != "SEND":
            problems.append(f"名詞並列: SEND単一候補にならない: {fam}")
        st, fam, cands, sems = _fam(_hx(
            "通知システムは保存した注文データを送信しなければならない。"))
        if "multiple_predicates" in sems:
            problems.append("連体修飾（保存した）を並列述語と誤検出")
        if fam != "SEND":
            problems.append(f"連体修飾: SEND単一候補にならない: {fam}")
    _case(results, "LEX-P2-PREDICATES", problems,
          "活用形→同一Action候補・否定記録・複数述語の非集約・名詞並列の区別")

    # --- P2: Canonical契約（Schema適合・解析Provenance・Strict非依存） ---
    problems = []
    if sp is not None:
        from rimay_jp_core.schema_check import validate_schema
        c = _hx("通知システムは注文確定通知を送信します。")
        errs = validate_schema(c)
        if errs:
            problems.append(f"Schema違反: {errs[:2]}")
        la = c["normalization"].get("lexical_analysis") or {}
        if la.get("provider") != "sudachipy" or                 not str(la.get("dictionary_content_hash", "")).startswith("sha256:"):
            problems.append(f"lexical_analysis provenance不備: {la.keys()}")
        text = "注文管理システムは注文確定通知を顧客メールアドレスに送信しなければならない。"
        seg = {"text": text, "document_id": "RUN-P2"}
        a = extract(seg, "REQ-SP", provider="regex")
        b = extract(seg, "REQ-SP", provider="sudachipy")
        if a["extraction_mode"] != "strict" or a != b:
            problems.append("strict経路がproviderに依存している")
        strict_la = (a["canonical"] or {}).get("normalization", {})
        if "lexical_analysis" in strict_la:
            problems.append("strict経路にlexical_analysisが記録された")
    _case(results, "LEX-P2-CANONICAL-CONTRACT", problems,
          "Schema適合・heuristic限定のlexical_analysis記録・Strict Provider非依存")

    summary = {"pass": sum(r["verdict"] == "PASS" for r in results),
               "fail": sum(r["verdict"] == "FAIL" for r in results)}
    return {"results": results, "summary": summary}


def _legacy_regex_extract(text: str, document_id: str, vocab) -> dict:
    """v0.3導入前のdocument_term_extractor実装の凍結コピー（非回帰基準）。"""
    import re
    from .terminology import resolve_surface
    _TOKEN = re.compile(r"[一-龥ァ-ヶーA-Za-z0-9]{2,}")
    _HEADING = re.compile(r"^#{1,6}\s*(.+?)\s*$", re.MULTILINE)
    _NUMERIC = re.compile(r"^[0-9,，.]+$")
    _MAX = 3
    sections = [(0, "(先頭)")]
    for m in _HEADING.finditer(text):
        sections.append((m.start(), m.group(1)))

    def _section(pos):
        name = sections[0][1]
        for start, title in sections:
            if start <= pos:
                name = title
            else:
                break
        return name

    counts, spans = {}, {}
    for m in _TOKEN.finditer(text):
        s = m.group(0)
        if _NUMERIC.match(s):
            continue
        counts[s] = counts.get(s, 0) + 1
        if len(spans.setdefault(s, [])) < _MAX:
            spans[s].append((m.start(), m.end()))
    observations, resolved, ambiguous, deprecated = [], {}, [], []
    for surface in sorted(counts):
        r = resolve_surface(surface, vocab=vocab)
        first = spans[surface][0]
        entry = {"surface_form": surface, "count": counts[surface],
                 "section_id": _section(first[0]),
                 "matches": [x["term_id"] for x in r["matches"]]}
        if r["kind"] in ("exact", "synonym"):
            resolved[surface] = r["matches"][0]["term_id"]
        elif r["kind"] == "ambiguous":
            ambiguous.append(entry)
        elif r["kind"] == "deprecated":
            deprecated.append(entry)
        else:
            for start, end in spans[surface]:
                observations.append(
                    {"surface_form": surface, "expected_types": [],
                     "source_span": {"start": start, "end": end},
                     "section_id": _section(start),
                     "document_id": document_id})
    return {"document_id": document_id, "observations": observations,
            "resolved": resolved, "ambiguous": ambiguous,
            "deprecated": deprecated, "counts": counts,
            "truncation": {"max_spans_per_surface": _MAX}}
