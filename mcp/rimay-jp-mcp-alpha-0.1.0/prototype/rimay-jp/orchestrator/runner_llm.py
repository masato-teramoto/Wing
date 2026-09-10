"""LLM実接続評価ランナー（Phase 5、PoC継続条件①）。

source-analysis契約の下でLLM分類・抽出を接続し、§22.4を測定する:
- 供給量: 常時注入コア（Profile定数のみ・辞書件数と独立）と1要求あたりの
  プロンプト文字数を実測。ライブAPI実行時はusage（トークン実測）も記録。
- Canonical Patch拒否率: LLM提案Patchの適用結果を理由別に計数。
  統制検査として confirmed昇格の試み・revision競合が拒否されることも機械検査。
- モデル変更回帰差分: fixtureセット（実モデル出力の記録）ごとに全指標を算出し、
  モデル間差分を全回記録する。
- Validator補正効果: LLM単体では検出されない問題（状態モデル外の値・原子性違反等）
  をValidator適用後に検出できた件数。

統制Gate（本試行の合格条件。分類精度そのものはGateでなく測定値）:
- 契約違反出力の拒否漏れ0件（llm-proposal契約・許可Pointer・未知family/modality）
- 誤自動確定0件（LLM経路からconfirmedが生成されない — 契約とアダプタの構造的保証）
- 期待unknownの保持（契約適合出力に対して）
- source-analysis契約適合（extraction_mode=llm）
"""
from __future__ import annotations

import copy
import json
from pathlib import Path

import yaml
from jsonschema import Draft202012Validator

from . import _ROOT  # noqa: F401
from .llm_adapter import (ReplayBackend, build_core_prompt, build_case_prompt,
                          build_patch_prompt, parse_response,
                          assemble_source_analysis, make_patches,
                          term_candidates_for, CORE_PROMPT_VERSION, TEMPERATURE)
from .validation_router import validate_all  # noqa: E402
from .information_classifier import classify as rule_classify  # noqa: E402
from rimay_jp_core import PROFILE_VERSION  # noqa: E402
from rimay_jp_core.lexicon import ROOT as RIMAY_ROOT, versions  # noqa: E402
from rimay_jp_core.patch import apply_canonical_patch  # noqa: E402


def _sa_validator() -> Draft202012Validator:
    doc = json.loads((RIMAY_ROOT / "canonical" / "source-analysis.schema.json")
                     .read_text(encoding="utf-8"))
    # canonicalの中身は canonical-requirement 側で検査するため、ここでは契約形のみ
    return Draft202012Validator(doc)


def _confirmed_llm_slots(canonical: dict) -> list[str]:
    """LLM経路由来のconfirmedスロット（Gate: 0件）。"""
    prv = {p["id"]: p for p in canonical.get("provenance") or []}
    out = []
    for path, s in (canonical.get("resolution") or {}).get("slots", {}).items():
        if s.get("status") != "confirmed":
            continue
        methods = {prv[r]["resolution_method"] for r in s.get("provenance_refs") or []
                   if r in prv}
        if "llm_candidate" in methods or not methods:
            out.append(path)
    return out


def _run_patch_stage(backend, case: dict, text: str, m: dict) -> list[str]:
    """LLM Patch提案の測定と統制検査。戻り値は問題一覧。"""
    from .candidate_extractor import extract as rb_extract
    ps = case["patch_stage"]
    cid = case["case_id"]
    problems: list[str] = []

    canonical = rb_extract({"document_id": cid, "text": text}, f"REQ-{cid}-RB")["canonical"]
    if canonical is None:
        return [f"Patch段の対象Canonicalが抽出できない"]
    # 診断（DialogueState._diagnoseと同じ実体化）: 必須Role欠落をunknownスロット化
    from rimay_jp_core.validator import validate as core_validate
    from rimay_jp_core.model import set_slot
    for f in core_validate(canonical, phase2_slice=False):
        p = f.get("path")
        if f["code"] == "JP-OMISSION" and p \
                and p not in canonical["resolution"]["slots"]:
            set_slot(canonical, p, "unknown", confirmation_required=True)
    slot = (canonical["resolution"]["slots"].get(ps["target_path"]) or {})
    if slot.get("status") != "unknown":
        return [f"Patch対象がunknownでない: {slot.get('status')}"]

    cands = term_candidates_for(ps["target_field"])
    m["knowledge_supplied"] = m.get("knowledge_supplied", 0) + len(cands)
    pprompt = build_patch_prompt(text, ps["target_path"], cands)
    m["prompt_chars_total"] += len(pprompt)
    pres = backend.complete(pprompt, cid, "patch")
    if pres.get("error"):
        return [pres["error"]]
    try:
        pobj = json.loads(pres["text"].strip().strip("`"))
    except (json.JSONDecodeError, ValueError) as e:
        m["contract_violations"] += 1
        return []  # 契約違反出力の拒否（統制どおり・計数のみ）

    patches = make_patches(canonical, pobj, f"{cid}-PATCH")
    if not patches:
        # 提案なし。根拠なしケースでは望ましい統制挙動。根拠ありケースでの
        # 見送りはモデルの保守性の実測値（Gateにしない。回帰差分で記録）
        m["patch_refusals"] += 1
        if case.get("expect_patch_proposal"):
            m["grounded_refusals"] = m.get("grounded_refusals", 0) + 1
    for patch in patches:
        m["patches_proposed"] += 1
        m["knowledge_used"] = m.get("knowledge_used", 0) + 1
        r = apply_canonical_patch(canonical, patch)
        if r["ok"]:
            canonical = r["canonical"]
            m["patches_accepted"] += 1
            if patch["new_value"] not in ps["acceptable_values"]:
                problems.append(f"根拠なき候補が受理: {patch['new_value']}")
            new_slot = canonical["resolution"]["slots"][patch["path"]]
            if new_slot.get("status") != "proposed":
                problems.append(f"LLM Patchがproposed以外: {new_slot.get('status')}")
        else:
            reason = (r["findings"][0].get("evidence") or {}).get("reason") \
                or r["findings"][0]["code"]
            m["patch_rejections"][reason] = m["patch_rejections"].get(reason, 0) + 1

    # 統制検査（提案の有無に依存せず常時実行）:
    # confirmed昇格の試み・revision競合はいずれも拒否される
    synth = {"operation": "replace_slot",
             "requirement_id": canonical["requirement_id"],
             "base_revision": canonical["revision"],
             "path": ps["target_path"],
             "expected_status": (canonical["resolution"]["slots"]
                                 .get(ps["target_path"]) or {}).get("status", "unknown"),
             "new_value": ps["acceptable_values"][0],
             "evidence": {"type": "tool_result", "reference": "governance-check"}}
    if apply_canonical_patch(canonical, {**synth, "new_status": "confirmed"})["ok"]:
        problems.append("tool_result根拠のconfirmedが拒否されない")
    if apply_canonical_patch(canonical, {**synth, "new_status": "proposed",
                                         "base_revision": 999})["ok"]:
        problems.append("revision競合Patchが拒否されない")
    m["governance_checks"] = m.get("governance_checks", 0) + 2
    return problems


def run_model(fixture_path: Path, corpus_dir: Path) -> dict:
    backend = ReplayBackend(fixture_path)
    sa_check = _sa_validator()
    results = []
    m = {"model": backend.model, "cases": 0,
         "classification_hits": 0, "rule_classification_hits": 0,
         "contract_violations": 0, "rejected_slots": 0,
         "unknown_expected": 0, "unknown_kept": 0,
         "validator_corrections": 0,
         "prompt_chars_total": 0, "core_prompt_chars": len(build_core_prompt()),
         "patches_proposed": 0, "patches_accepted": 0, "patch_refusals": 0,
         "grounded_refusals": 0,
         "knowledge_supplied": 0, "knowledge_used": 0, "governance_checks": 0,
         "patch_rejections": {}, "usage_recorded": False}

    for p in sorted(corpus_dir.glob("LLM-*.yaml")):
        case = yaml.safe_load(p.read_text(encoding="utf-8"))
        cid = case["case_id"]
        text = case["japanese"].strip()
        segment = {"document_id": cid, "text": text}
        problems: list[str] = []
        m["cases"] += 1

        prompt = build_case_prompt(segment)
        m["prompt_chars_total"] += len(prompt)
        res = backend.complete(prompt, cid, "analysis")
        if res.get("usage"):
            m["usage_recorded"] = True
        if res.get("error"):
            results.append({"case_id": cid, "verdict": "FAIL",
                            "detail": res["error"]})
            continue

        proposal, errors = parse_response(res["text"])
        if proposal is None:
            # 契約違反 → 拒否（統制どおり）。分類・抽出は不成立として計数
            m["contract_violations"] += 1
            results.append({"case_id": cid, "verdict": "PASS",
                            "detail": f"契約違反出力を拒否: {errors[0]}"})
            continue

        # 規則ベースとのA/B比較（参考記録）
        rb = rule_classify(text)["classification"]
        if rb == case["expected_classification"]:
            m["rule_classification_hits"] += 1

        got_cls = proposal["classification"]
        cls_ok = got_cls == case["expected_classification"]
        if cls_ok:
            m["classification_hits"] += 1

        sa = assemble_source_analysis(segment, proposal, f"REQ-{cid}")
        m["rejected_slots"] += len(sa["rejected_slots"])
        sa_for_check = {k: v for k, v in sa.items() if k != "rejected_slots"}
        errs = [e.message for e in sa_check.iter_errors(sa_for_check)]
        if errs:
            problems.append(f"source-analysis契約違反: {errs[0]}")

        canonical = sa["canonical"]
        if canonical is not None:
            # Gate: LLM経路からconfirmedが生成されない
            bad = _confirmed_llm_slots(canonical)
            if bad:
                problems.append(f"誤自動確定: {bad}")
            # 期待unknownの保持
            slots = canonical["resolution"]["slots"]
            for ptr in case.get("expected_unknowns") or []:
                m["unknown_expected"] += 1
                if (slots.get(ptr) or {}).get("status") == "unknown":
                    m["unknown_kept"] += 1
                else:
                    problems.append(f"unknown不保持: {ptr}")
            anys = case.get("expected_unknowns_any") or []
            if anys:
                m["unknown_expected"] += 1
                if any((slots.get(a) or {}).get("status") == "unknown"
                       for a in anys):
                    m["unknown_kept"] += 1
                else:
                    problems.append(f"unknown不保持（いずれか）: {anys}")
            fam = (canonical["rimay_core"]["response"].get("action") or {}).get("family")
            if case.get("expected_family") and fam != case["expected_family"]:
                problems.append(f"family不一致: {fam}")
            n_prop = sum(1 for s in slots.values() if s.get("status") == "proposed")
            if case.get("expected_proposed_min") and n_prop < case["expected_proposed_min"]:
                problems.append(f"提案スロット不足: {n_prop}")

            # Validator補正効果: LLM単体で通った内容からValidator/診断が問題を検出。
            # ADR-0013境界: raw_text段のissueはPre-Canonical診断（gate）で確認し、
            # Canonical段のReportとは分けて数える（Canonical段は日本語を再解析しない）
            vres = validate_all(copy.deepcopy(canonical))
            issue = case.get("expected_validator_issue")
            if issue:
                codes = {f["normalized_issue_code"]
                         for f in vres["report"]["findings"]}
                from .runner_step4 import _issue_catalog
                if _issue_catalog()[issue]["stage"] == "raw_text":
                    from .raw_text_gate import inspect as _gate
                    codes |= {f["normalized_issue_code"]
                              for f in _gate(text, "ja", cid)["findings"]}
                if issue in codes:
                    m["validator_corrections"] += 1
                else:
                    problems.append(f"Validator補正が働かない: {issue} not in {sorted(codes)}")

        # Patch提案段（対象Canonicalは規則ベース抽出で固定＝LLM分析結果と独立に
        # Patch系を測定する。オンデマンド用語供給→proposed Patch→統制検査）
        ps = case.get("patch_stage")
        if ps:
            problems += _run_patch_stage(backend, case, text, m)

        if not cls_ok:
            detail_cls = f"分類={got_cls}（期待{case['expected_classification']}・規則={rb}）"
        else:
            detail_cls = f"分類OK（規則={rb}）"
        results.append({"case_id": cid,
                        "verdict": "FAIL" if problems else "PASS",
                        "detail": "; ".join(problems) if problems else detail_cls,
                        "classification_ok": cls_ok})

    m["classification_accuracy"] = round(m["classification_hits"] / m["cases"], 4)
    m["rule_classification_accuracy"] = round(
        m["rule_classification_hits"] / m["cases"], 4)
    m["avg_prompt_chars"] = round(m["prompt_chars_total"] / m["cases"])
    m["patch_rejection_rate"] = round(
        sum(m["patch_rejections"].values()) / m["patches_proposed"], 4) \
        if m["patches_proposed"] else 0.0
    m["dynamic_knowledge_use_rate"] = round(
        m["knowledge_used"] / m["knowledge_supplied"], 4) \
        if m["knowledge_supplied"] else 0.0
    return {"results": results, "metrics": m}


def run_llm_trial(root: Path) -> dict:
    corpus_dir = root / "corpus" / "llm"
    fixtures = sorted((corpus_dir / "fixtures").glob("*.jsonl"))
    all_results = []
    per_model = {}
    gate_fail = False

    for fx in fixtures:
        out = run_model(fx, corpus_dir)
        model = out["metrics"]["model"]
        per_model[model] = out["metrics"]
        for r in out["results"]:
            all_results.append({**r, "case_id": f"{model}:{r['case_id']}"})
            if r["verdict"] == "FAIL":
                gate_fail = True

    # モデル変更回帰差分（§22.4: 全回記録）
    diff = {}
    if len(per_model) >= 2:
        keys = ["classification_accuracy", "validator_corrections",
                "patches_accepted", "patch_refusals", "grounded_refusals",
                "patch_rejection_rate", "dynamic_knowledge_use_rate",
                "contract_violations", "rejected_slots", "avg_prompt_chars"]
        models = sorted(per_model)
        diff = {"models": models,
                "deltas": {k: {mm: per_model[mm].get(k) for mm in models}
                           for k in keys}}

    record = {
        "protocol": {  # §22.6: 評価条件の固定・記録
            "profile_version": PROFILE_VERSION,
            "core_prompt_version": CORE_PROMPT_VERSION,
            "temperature": TEMPERATURE,
            "knowledge_versions": versions(),
            "fixture_note": "実モデル出力の記録をReplayBackendで再生（決定論）。"
                            "ライブ実測はANTHROPIC_API_KEY設定時に同一runnerで再実行可能",
        },
        "per_model": per_model,
        "model_regression_diff": diff,
    }
    rep_dir = root / "reports" / "llm-integration"
    rep_dir.mkdir(parents=True, exist_ok=True)
    (rep_dir / "metrics.json").write_text(
        json.dumps(record, ensure_ascii=False, indent=1, sort_keys=True) + "\n",
        encoding="utf-8")

    all_results.append({
        "case_id": "LLM-TRIAL-METRICS",
        "verdict": "FAIL" if (gate_fail or not per_model) else "PASS",
        "detail": " / ".join(
            f"{mm}: 分類{per_model[mm]['classification_accuracy']:.0%}"
            f"（規則{per_model[mm]['rule_classification_accuracy']:.0%}） "
            f"Patch受理{per_model[mm]['patches_accepted']}"
            f"・根拠なし拒否{per_model[mm]['patch_refusals']}"
            f"・拒否率{per_model[mm]['patch_rejection_rate']:.0%} "
            f"契約違反{per_model[mm]['contract_violations']}件拒否 "
            f"補正{per_model[mm]['validator_corrections']}件"
            for mm in sorted(per_model)),
    })
    summary = {"pass": sum(1 for r in all_results if r["verdict"] == "PASS"),
               "fail": sum(1 for r in all_results if r["verdict"] == "FAIL"),
               "models": sorted(per_model)}
    return {"results": all_results, "summary": summary, "record": record}
