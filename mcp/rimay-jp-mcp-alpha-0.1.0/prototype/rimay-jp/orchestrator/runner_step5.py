"""Step 5評価ランナー: finding→壁打ち・Patch接続（Advisory mode）のGate検査。

Gate（adaptation §3 Step 5）:
- 意味補完の無承認確定0件（FALSE_AUTO_CONFIRMATION_RATE=0%。修復で新たにconfirmedに
  なったスロットは user_answer / knowledge_asset / rule の根拠Provenanceを持つ）
- 意図しない意味変更率0%（UNINTENDED_MEANING_CHANGE_RATE=0%。Patch適用による
  rimay_core変更は回答対象path配下＋表記専用pathに限る。分割提案・知識ルート・
  自動表層修復では意味部分（canonical_hash）が不変）
加えて: 質問へのfinding発火根拠の付与（Rule質問との併合・二重質問なし）、
修復収束（再検証で当該issue解消）、Advisory項目の非遮断性を機械検査する。
"""
from __future__ import annotations

import copy
from pathlib import Path

import yaml

from . import _ROOT  # noqa: F401
from .candidate_extractor import extract  # noqa: E402
from .dialogue_state import DialogueState  # noqa: E402
from .validation_router import validate_all  # noqa: E402
from .repair_planner import plan_repairs, unintended_meaning_changes  # noqa: E402
from .split_proposal import accept_split  # noqa: E402
from .raw_text_gate import inspect  # noqa: E402
from rimay_jp_core.model import canonical_hash  # noqa: E402

_EVIDENCE_OK = ("user_answer", "knowledge_asset", "rule")


def _confirmed_paths(canonical: dict) -> set[str]:
    return {p for p, s in canonical["resolution"]["slots"].items()
            if s["status"] == "confirmed"}


def _unauthorized_confirms(canonical: dict, before: set[str]) -> list[str]:
    """修復で新たにconfirmedになったスロットのうち、根拠なきもの（Gate: 0件）。"""
    prv = {p["id"]: p for p in canonical["provenance"]}
    bad = []
    for path in sorted(_confirmed_paths(canonical) - before):
        slot = canonical["resolution"]["slots"][path]
        entries = [prv[r] for r in slot.get("provenance_refs") or [] if r in prv]
        if not any(e.get("source_type") in _EVIDENCE_OK for e in entries):
            bad.append(path)
    return bad


def _heuristic_confirms(canonical: dict) -> list[str]:
    """抽出由来canonicalの誤自動確定（heuristic/synonym由来のconfirmed）検査。"""
    prv = {p["id"]: p for p in canonical["provenance"]}
    return [p for p, s in canonical["resolution"]["slots"].items()
            if s["status"] == "confirmed"
            and any(prv[r]["resolution_method"] in ("heuristic_candidate",
                                                    "synonym_match")
                    for r in s.get("provenance_refs") or [] if r in prv)]


def _check_proposal(case: dict, plan_out: dict, canonical: dict,
                    h0: str, problems: list[str]) -> dict | None:
    props = [p for p in plan_out["split_proposals"]
             if p["normalized_issue_code"] == case["expected_issue_code"]]
    if len(props) != 1:
        problems.append(f"分割提案が1件でない: {len(props)}件")
        return None
    prop = props[0]
    if prop["strategy"] != case["expected_strategy"]:
        problems.append(f"strategy不一致: {prop['strategy']}")
    if prop.get("advisory") != case.get("expected_advisory", True):
        problems.append("advisoryフラグ不一致（非遮断で提示されていない）")
    got = [p["text"] for p in prop["parts"]]
    if got != case["expected_parts"]:
        problems.append(f"分割文不一致: {got}")
    if canonical_hash(canonical) != h0:
        problems.append("提案生成で元Canonicalの意味部分が変化（意図しない意味変更）")
    return prop


def _check_children(case: dict, origin: dict, prop: dict,
                    problems: list[str]):
    acc = accept_split(origin, prop)
    ref = prop["proposal_id"]
    for i, ch in enumerate(acc["children"]):
        c, mode = ch["canonical"], ch["extraction_mode"]
        if c is None:
            problems.append(f"part{i + 1}が抽出されない")
            continue
        if mode != case["expected_part_modes"][i]:
            problems.append(f"part{i + 1}抽出モード不一致: {mode}")
        fam = ((c["rimay_core"]["response"].get("action") or {}).get("family"))
        if fam != case["expected_part_families"][i]:
            problems.append(f"part{i + 1} family不一致: {fam}")
        n_exp = (case.get("expected_part_condition_counts") or [None, None])[i]
        if n_exp is not None:
            n = len(c["rimay_core"].get("conditions") or [])
            if n != n_exp:
                problems.append(f"part{i + 1}条件数不一致: {n}")
        if not any(t["reference"].startswith("split-parent:") and ref in t["reference"]
                   for t in c["traceability"]):
            problems.append(f"part{i + 1}に親traceabilityがない")
        bad = _heuristic_confirms(c)
        if bad:
            problems.append(f"part{i + 1}に誤自動確定: {bad}")
    n_child_refs = sum(1 for t in origin["traceability"]
                       if t["reference"].startswith("split-child:"))
    if n_child_refs != len(prop["parts"]):
        problems.append("親側のsplit-child traceabilityが不足")
    if prop["status"] != "accepted":
        problems.append("提案statusがacceptedに遷移していない")


def run_step5_corpus(rep_dir: Path) -> dict:
    results = []
    unauthorized_total = 0
    unintended_total = 0
    attempted = resolved = 0
    rationale_total = rationale_ok = 0

    for path in sorted(rep_dir.glob("*.yaml")):
        case = yaml.safe_load(path.read_text(encoding="utf-8"))
        cid, flow = case["case_id"], case["flow"]
        text = case["japanese"].strip()
        problems: list[str] = []

        out = extract({"document_id": cid, "text": text}, f"REQ-{cid}")
        canonical = out["canonical"]
        if canonical is None and flow != "auto_resolved":
            results.append({"case_id": cid, "verdict": "FAIL",
                            "detail": "canonical未生成"})
            continue

        if flow == "ask_user_patch":
            res = validate_all(canonical)
            before = copy.deepcopy(canonical)
            before_confirmed = _confirmed_paths(canonical)
            ds = DialogueState(canonical)
            plan_out = plan_repairs(ds.canonical, res["report"])

            target = case["expected_question_target"]
            qs = [q for q in plan_out["questions"]
                  if q.get("target_path") == target]
            if len(qs) != 1:
                problems.append(f"対象質問が1件でない（二重質問防止違反）: {len(qs)}件")
            q = qs[0] if qs else None
            if q:
                if not q.get("finding_ids"):
                    problems.append("質問にfinding発火根拠（finding_ids）がない")
                if q.get("rule_id") != case["expected_rule_id"]:
                    problems.append(f"Rule質問との併合不成立: rule_id={q.get('rule_id')}")
                if q.get("normalized_issue_code") != case["expected_issue_code"]:
                    problems.append(f"issue code不一致: {q.get('normalized_issue_code')}")
                if q.get("finding_source_rule_id") != case["expected_finding_rule_trace"]:
                    problems.append(f"出典Rule追跡不一致: {q.get('finding_source_rule_id')}")
            # 発火根拠の接続率: ASK_USER findingが何らかの質問に併合されている
            for f in res["report"]["findings"]:
                if f["repair_disposition"] == "ASK_USER":
                    rationale_total += 1
                    if any(f["finding_id"] in (qq.get("finding_ids") or [])
                           for qq in plan_out["questions"]):
                        rationale_ok += 1

            if q:
                attempted += 1
                r = ds.answer(q, case["answer"])
                if not r["ok"]:
                    problems.append(f"回答が適用できない: {r.get('reason')}")
                else:
                    unauth = _unauthorized_confirms(ds.canonical, before_confirmed)
                    unauthorized_total += len(unauth)
                    if unauth:
                        problems.append(f"無承認確定: {unauth}")
                    changes = unintended_meaning_changes(before, ds.canonical,
                                                         [target])
                    unintended_total += len(changes)
                    if changes:
                        problems.append(f"意図しない意味変更: {changes}")
                    res2 = validate_all(copy.deepcopy(ds.canonical))
                    codes2 = {f["normalized_issue_code"]
                              for f in res2["report"]["findings"]}
                    missing = [c for c in case["expected_resolved"] if c in codes2]
                    if missing:
                        problems.append(f"再検証で未解消: {missing}")
                    else:
                        resolved += 1

        elif flow == "propose_split":
            res = validate_all(canonical)
            h0 = canonical_hash(canonical)
            plan_out = plan_repairs(canonical, res["report"])
            prop = _check_proposal(case, plan_out, canonical, h0, problems)
            if prop:
                _check_children(case, canonical, prop, problems)
                if canonical_hash(canonical) != h0:
                    problems.append("accept_splitで親の意味部分が変化")

        elif flow == "propose_split_rawtext":
            gate = inspect(text, "ja", cid)
            h0 = canonical_hash(canonical)
            plan_out = plan_repairs(canonical, extra_findings=gate["findings"])
            prop = _check_proposal(case, plan_out, canonical, h0, problems)
            if prop:
                _check_children(case, canonical, prop, problems)
                if canonical_hash(canonical) != h0:
                    problems.append("accept_splitで親の意味部分が変化")

        elif flow == "auto_resolved":
            # raw-text段の修復: 語順違反文はモダリティが文末に来ないため
            # 分類器が要求候補と認識せず、canonical=Noneが期待動作。
            gate = inspect(text, "ja", cid)
            plan_out = plan_repairs(canonical, extra_findings=gate["findings"],
                                    raw_text=text)
            code = case["expected_issue_code"]
            ar = [a for a in plan_out["auto_resolved"]
                  if a["normalized_issue_code"] == code]
            if not ar:
                problems.append(f"{code}がauto_resolvedへ振り分けられない")
            else:
                if ar[0]["method"] != case["expected_method"]:
                    problems.append(f"修復方法不一致: {ar[0]['method']}")
                if ar[0]["advisory"] != case.get("expected_advisory", True):
                    problems.append("advisoryフラグ不一致")
                rewritten = ar[0].get("rewritten_text")
                if case.get("expected_rewritten"):
                    if rewritten != case["expected_rewritten"]:
                        problems.append(f"並べ替え結果不一致: {rewritten}")
                    else:
                        # 並べ替え後は通常経路で抽出でき、当該スメルが解消する（収束）
                        out2 = extract({"document_id": cid, "text": rewritten},
                                       f"REQ-{cid}-R")
                        if out2["extraction_mode"] != case["expected_reextract_mode"]:
                            problems.append(
                                f"再抽出モード不一致: {out2['extraction_mode']}")
                        gate2 = inspect(rewritten, "ja", f"{cid}-R")
                        if any(f["normalized_issue_code"] == code
                               for f in gate2["findings"]):
                            problems.append("並べ替え後も語順スメルが残存")
            if any(qq.get("normalized_issue_code") == code
                   for qq in plan_out["questions"]):
                problems.append(f"{code}が質問化されている（自動修復対象のはず）")
            if any(p["normalized_issue_code"] == code
                   for p in plan_out["split_proposals"]):
                problems.append(f"{code}が分割提案化されている")

        elif flow == "route_knowledge":
            res = validate_all(canonical)
            h0 = canonical_hash(canonical)
            plan_out = plan_repairs(canonical, res["report"])
            code = case["expected_issue_code"]
            krs = [k for k in plan_out["knowledge_routes"]
                   if k["normalized_issue_code"] == code]
            if not krs:
                problems.append(f"{code}がknowledge_routesへ振り分けられない")
            else:
                cands = krs[0]["candidates"]
                if len(cands) < case["expected_min_candidates"]:
                    problems.append(f"候補数不足: {len(cands)}")
                prefix = case["expected_candidate_source_prefix"]
                if not all(c.get("source", "").startswith(prefix) for c in cands):
                    problems.append("根拠なし候補が含まれる")
                if any(c.get("status") == "confirmed" for c in cands):
                    problems.append("候補がconfirmedで提示されている（人間判断前）")
            if canonical_hash(canonical) != h0:
                problems.append("修復計画の生成で意味部分が変化（無承認確定の疑い）")

        else:
            problems.append(f"未知flow: {flow}")

        results.append({"case_id": cid,
                        "verdict": "FAIL" if problems else "PASS",
                        "detail": "; ".join(problems) if problems else flow})

    conv = resolved / attempted if attempted else 1.0
    rationale = rationale_ok / rationale_total if rationale_total else 1.0
    gate_pass = (unauthorized_total == 0 and unintended_total == 0
                 and conv == 1.0 and rationale == 1.0
                 and all(r["verdict"] == "PASS" for r in results))
    results.append({
        "case_id": "STEP5-METRICS",
        "verdict": "PASS" if gate_pass else "FAIL",
        "detail": f"無承認確定={unauthorized_total}件 "
                  f"意図しない意味変更={unintended_total}件 "
                  f"修復収束率={conv:.0%}（{resolved}/{attempted}） "
                  f"発火根拠接続率={rationale:.0%}（{rationale_ok}/{rationale_total}）",
    })
    summary = {"pass": sum(1 for r in results if r["verdict"] == "PASS"),
               "fail": sum(1 for r in results if r["verdict"] == "FAIL"),
               "unauthorized_confirms": unauthorized_total,
               "unintended_changes": unintended_total,
               "repair_convergence": round(conv, 4),
               "rationale_connection": round(rationale, 4)}
    return {"results": results, "summary": summary}
