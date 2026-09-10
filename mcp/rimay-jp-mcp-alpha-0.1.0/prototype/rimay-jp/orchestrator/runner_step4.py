"""Step 4評価ランナー: Canonical Validation統合のGate検査。

Gate（adaptation §3 Step 4）:
- Canonical Pointer対応率 95%以上（report findingのtarget_paths保有率）
- normalized issue code正解率 95%以上（期待コードの検出率）
- Rule版・出典追跡率 100%（source_rule_id・validator_id・registry版の保有）
加えて: Reportのfinding契約適合・重複排除の不変条件・validation_stateの整合
（移行契約Phase B: findings[]新規書き込み停止＋read-fallback・STALE検出）、
rolloutポリシー（§6合意）のblocking適用を機械検査する。
"""
from __future__ import annotations

import copy
import json
from functools import lru_cache
from pathlib import Path

import yaml
from jsonschema import Draft202012Validator

from . import _ROOT  # noqa: F401
from .candidate_extractor import extract  # noqa: E402
from .validation_router import validate_all  # noqa: E402
from .validation_report import (dedup, validation_is_stale, read_findings,  # noqa: E402
                                is_blocking_by_policy)
from .raw_text_gate import inspect as gate_inspect  # noqa: E402
from .approval import promote_to_review_ready  # noqa: E402
from rimay_jp_core.lexicon import ROOT as RIMAY_ROOT  # noqa: E402


@lru_cache(maxsize=1)
def _issue_catalog() -> dict:
    doc = yaml.safe_load((RIMAY_ROOT / "canonical" / "issue-code-catalog.yaml")
                         .read_text(encoding="utf-8"))
    return {e["code"]: e for e in doc["issue_codes"]}


@lru_cache(maxsize=1)
def _registry_ids() -> set:
    doc = yaml.safe_load((RIMAY_ROOT / "canonical" / "validator-registry.yaml")
                         .read_text(encoding="utf-8"))
    ids = {v["id"] for v in doc.get("validators") or []}
    return ids | {"validation-router"}  # UNCLASSIFIED既定owner


def _finding_contract_violations(findings: list[dict]) -> list[str]:
    """Validator Registry整合のContract Test（ADR-0013 Phase 4）。

    - normalized_issue_codeがカタログに存在する
    - validator_idがカタログのowner_validatorと一致する（dedup後の主finding）
    - validator_idがRegistryへ登録済み
    """
    v = []
    cat = _issue_catalog()
    for f in findings:
        code = f["normalized_issue_code"]
        if code not in cat:
            v.append(f"カタログ外code: {code}")
            continue
        if f["validator_id"] != cat[code]["owner_validator"]:
            v.append(f"{code}: owner不一致 {f['validator_id']}")
        if f["validator_id"] not in _registry_ids():
            v.append(f"{code}: Registry未登録validator {f['validator_id']}")
    return v


@lru_cache(maxsize=1)
def _report_validator() -> Draft202012Validator:
    doc = json.loads((RIMAY_ROOT / "canonical" / "finding.schema.json")
                     .read_text(encoding="utf-8"))
    return Draft202012Validator({"$defs": doc["$defs"],
                                 "$ref": "#/$defs/validationReport"})


def _dedup_machinery_check() -> list[str]:
    """重複排除の不変条件（owner優先・severity最大・corroboration併合）の合成テスト。"""
    a = {"finding_id": "FND-T-1", "validator_id": "raw-text-quality-gate",
         "source_rule_id": "x#1", "normalized_issue_code": "MISSING_REQUIRED_ROLE",
         "quality_labels": ["completeness"], "severity": "medium", "blocking": False,
         "target_paths": ["/rimay_core/response/destination"], "message": "a",
         "repair_disposition": "ASK_USER", "status": "open"}
    b = {**a, "finding_id": "FND-T-2", "validator_id": "action-frame-validator",
         "source_rule_id": "SEND_11_1_1.required_destination", "severity": "high",
         "blocking": True}
    out = dedup([a, b])
    problems = []
    if len(out) != 1:
        problems.append(f"dedup統合されない: {len(out)}件")
        return problems
    f = out[0]
    if f["validator_id"] != "action-frame-validator":
        problems.append("owner_validator優先になっていない")
    if f["severity"] != "high" or not f["blocking"]:
        problems.append("severity最大・blocking合成が不正")
    corr = (f.get("evidence") or {}).get("corroborated_by") or []
    if not any(c["validator_id"] == "raw-text-quality-gate" for c in corr):
        problems.append("corroborated_by併合が不正")
    return problems


def run_step4_corpus(val_dir: Path) -> dict:
    results = []
    total_findings = with_pointer = 0
    expected_total = expected_hit = 0
    trace_total = trace_ok = 0

    for p in sorted(val_dir.glob("*.yaml")):
        case = yaml.safe_load(p.read_text(encoding="utf-8"))
        cid = case["case_id"]
        out = extract({"document_id": cid, "text": case["japanese"]}, f"REQ-{cid}")
        canonical = out["canonical"]
        res = validate_all(canonical)
        report = res["report"]
        problems: list[str] = []

        # Report契約適合
        errs = [e.message for e in _report_validator().iter_errors(report)]
        if errs:
            problems.append(f"Report契約違反: {errs[0]}")
        # Registry整合（ADR-0013 Phase 4: owner一致・Registry登録済み）
        problems += _finding_contract_violations(report["findings"])

        codes = {f["normalized_issue_code"] for f in report["findings"]}
        exp = set(case.get("expected_issue_codes") or [])
        expected_total += len(exp)
        expected_hit += len(exp & codes)
        if exp - codes:
            problems.append(f"期待issue code未検出: {sorted(exp - codes)} got={sorted(codes)}")

        # Pointer対応率（canonical段findingのみ。raw_text段のDEICTIC等は
        # 対応Pointerを持たないため分母外）・Rule追跡率（全finding）
        catalog = _issue_catalog()
        for f in report["findings"]:
            stage = catalog[f["normalized_issue_code"]]["stage"]
            if stage != "raw_text":
                total_findings += 1
                if f.get("target_paths"):
                    with_pointer += 1
            trace_total += 1
            if f.get("source_rule_id") and f.get("validator_id"):
                trace_ok += 1

        # 重複排除の不変条件: (code×path)の重複なし
        keys = [(f["normalized_issue_code"],
                 f["target_paths"][0] if f.get("target_paths") else "")
                for f in report["findings"]]
        if len(keys) != len(set(keys)):
            problems.append("重複findingが未統合")

        # 移行契約Phase B: legacy findings[]へ新規書き込みしない（Report=唯一の書き込み先）
        if canonical.get("findings"):
            problems.append("Phase B違反: legacy findings[]へ書き込みがある")
        if read_findings(canonical, report) is not report["findings"]:
            problems.append("Report優先の読み取りが不成立")
        state = canonical.get("validation_state") or {}
        if state.get("report_id") != report["report_id"]:
            problems.append("validation_stateのreport参照が不整合")
        n_block = sum(1 for f in report["findings"] if f["blocking"])
        if state.get("blocking_findings") != n_block:
            problems.append("validation_stateの件数が不整合")
        if validation_is_stale(canonical):
            problems.append("検査直後にSTALE判定")
        mutated = copy.deepcopy(canonical)
        mutated["rimay_core"]["response"]["actor"] = "BillingSystem"
        if not validation_is_stale(mutated):
            problems.append("Canonical変更後にSTALEを検出できない")

        results.append({"case_id": cid,
                        "verdict": "FAIL" if problems else "PASS",
                        "detail": "; ".join(problems) if problems
                        else f"issues={sorted(codes)}"})

    results.append({"case_id": "DEDUP-MACHINERY",
                    "verdict": "FAIL" if _dedup_machinery_check() else "PASS",
                    "detail": "; ".join(_dedup_machinery_check()) or
                              "owner優先・severity最大・corroboration併合"})

    # ADR-0013 D3: NormalizerのProfileコンパイルと版数規律
    problems = []
    from rimay_jp_core.lexicon import (normalizer_profile, versions,
                                       profile_content_hash, case_frames)
    from rimay_jp_core import PROFILE_VERSION, MVP_CONDITIONS
    prof = normalizer_profile()
    if set(prof["role_by_particle"]) != set(case_frames()):
        problems.append("role_by_particleが全familyを導出していない")
    if prof["role_by_particle"]["SEND"].get("で") != "channel":
        problems.append("channel導出欠落（二重管理ドリフトの再発）")
    if prof["role_by_particle"]["UPDATE"].get("に") != "result_value":
        problems.append("UPDATE result_value:に がframesから導出されていない")
    allowed_types = MVP_CONDITIONS | {"EVERY", "WHERE"}
    if not {t for _, t in prof["condition_terminals"]} <= allowed_types:
        problems.append("condition_terminalsに未知の条件型")
    if len(prof["modality_endings"]) != 2:
        problems.append("modality_endingsが2件でない")
    ver = versions()
    if ver.get("profile_content_hash") != profile_content_hash() or \
            not str(ver.get("profile_content_hash", "")).startswith("sha256:"):
        problems.append("profile_content_hashがversions()に無い・不安定")
    declared_profile_version = yaml.safe_load(
        (RIMAY_ROOT / "profile" / "supported-profile.yaml").read_text(
            encoding="utf-8"))["profile_version"]
    if PROFILE_VERSION != declared_profile_version:
        problems.append(
            "profile版数規律違反（runtimeとSSOTが不一致）: "
            f"runtime={PROFILE_VERSION} ssot={declared_profile_version}")
    results.append({"case_id": "PROFILE-SSOT",
                    "verdict": "FAIL" if problems else "PASS",
                    "detail": "; ".join(problems) or
                              "Profileコンパイル（channel/result_value導出含む）・"
                              "content hash・SSOT版数一致"})

    # ADR-0013 D5後段: Registry実行契約（input_contract・実行計画生成・機械的制限）
    problems = []
    from .validation_router import execution_plan, verify_plan, _INPUT_VOCAB
    from rimay_jp_core.normalizer import normalize as _norm
    plan = execution_plan()  # Registry契約違反ならここでRuntimeError
    reg = yaml.safe_load((RIMAY_ROOT / "canonical" / "validator-registry.yaml")
                         .read_text(encoding="utf-8"))
    no_ic = [v["id"] for v in reg["validators"]
             if v.get("input_contract") not in _INPUT_VOCAB]
    if no_ic:
        problems.append(f"input_contract未宣言・語彙外: {no_ic}")
    raw_ids = {v["id"] for v in reg["validators"]
               if v.get("input_contract") == "raw_text"}
    if raw_ids != {"information-classifier", "raw-text-quality-gate",
                   "candidate-extractor"}:
        problems.append(f"raw_text契約の宣言が想定と不一致: {sorted(raw_ids)}")
    # 実行結果が計画どおりのlayer構成になる（unblocked=6層／blocked=表層なし）
    ok_c, _ = _norm("利用者が注文確定ボタンを押したとき、通知システムは請求書PDFを"
                    "顧客メールアドレスに送信しなければならない。", "REQ-PLAN-OK")
    res_ok = validate_all(ok_c)
    if set(res_ok["layers"]) != {"schema", "core", "quality", "domain",
                                 "render_precheck", "surface"}:
        problems.append(f"計画実行のlayer構成不一致: {sorted(res_ok['layers'])}")
    ng_c = extract({"document_id": "PLAN", "text":
                    "通知システムは請求書PDFを送信しなければならない。"},
                   "REQ-PLAN-NG")["canonical"]
    res_ng = validate_all(ng_c)
    if "surface" in res_ng["layers"]:
        problems.append("blocking時にpost段（表層往復）が実行された")
    # 契約違反計画の拒否（未知binding・raw_text混入・Registry未登録）
    bad_plans = [
        ("未知binding", {"validate_all": [{"binding": "nonexistent",
          "input_contract": "canonical_requirement", "phase": "pre",
          "validators": ["canonical-schema-validator"]}]}),
        ("raw_text契約の混入", {"validate_all": [{"binding": "schema",
          "input_contract": "raw_text", "phase": "pre",
          "validators": ["canonical-schema-validator"]}]}),
        ("Registry未登録validator", {"validate_all": [{"binding": "schema",
          "input_contract": "canonical_requirement", "phase": "pre",
          "validators": ["rogue-validator"]}]}),
        ("raw_text契約validatorの配置", {"validate_all": [{"binding": "schema",
          "input_contract": "canonical_requirement", "phase": "pre",
          "validators": ["raw-text-quality-gate"]}]}),
    ]
    for name_, doc in bad_plans:
        if not verify_plan(doc):
            problems.append(f"違反計画が拒否されない: {name_}")
    results.append({"case_id": "REGISTRY-PLAN",
                    "verdict": "FAIL" if problems else "PASS",
                    "detail": "; ".join(problems) or
                              f"実行計画をRegistryから生成（{len(plan)}binding）・"
                              "全Validator input_contract宣言・raw_text 3種限定・"
                              "違反計画4種の拒否"})

    # ADR-0013 D4: 保証経路（mode）とSourceカバレッジの永続化・mode別承認条件
    problems = []
    from rimay_jp_core.normalizer import normalize as _norm
    from rimay_jp_core.model import new_canonical as _new
    sc, _f = _norm("利用者が注文確定ボタンを押したとき、通知システムは請求書PDFを"
                   "顧客メールアドレスに送信しなければならない。", "REQ-COV-S")
    n = sc.get("normalization") or {}
    if n.get("mode") != "strict" or (n.get("coverage") or {}).get("unconsumed_spans") \
            or not (n.get("conformance") or {}).get("controlled_language") \
            or not str(n.get("profile_content_hash", "")).startswith("sha256:"):
        problems.append(f"strict記録が不正: {n.get('mode')}")
    hc = extract({"document_id": "COV", "text":
                  "注文管理システムは注文データを保存および更新しなければならない。"},
                 "REQ-COV-H")["canonical"]
    nh = hc.get("normalization") or {}
    unc = (nh.get("coverage") or {}).get("unconsumed_spans") or []
    src_h = hc["source"]["text"]
    fragments = [src_h[s["start"]:s["end"]] for s in unc]
    if nh.get("mode") != "heuristic" or "保存および" not in "".join(fragments):
        problems.append(f"heuristicカバレッジが読み飛ばしを記録しない: {fragments}")
    ready = promote_to_review_ready(copy.deepcopy(hc))
    if ready["ok"] or not any("未解釈span" in r for r in ready["reasons"]):
        problems.append("未解釈span残存の承認遮断が働かない")
    if (_new("REQ-API").get("normalization") or {}).get("mode") != "canonical_api":
        problems.append("直接投入の既定modeがcanonical_apiでない")
    results.append({"case_id": "NORMALIZATION-COVERAGE",
                    "verdict": "FAIL" if problems else "PASS",
                    "detail": "; ".join(problems) or
                              "strict=全消費・heuristic=「保存および」を未解釈記録・"
                              "未解釈残存で承認遮断・既定canonical_api"})

    # 移行契約Phase B: Report不在の旧Canonicalはlegacy findings[]から読める
    problems = []
    legacy_canonical = {"findings": [{"code": "JP-OMISSION", "blocking": True}]}
    if read_findings(legacy_canonical) != legacy_canonical["findings"]:
        problems.append("旧Canonicalのread-fallbackが不成立")
    if read_findings({"findings": None}) != []:
        problems.append("findings欠落時に空リストにならない")
    results.append({"case_id": "PHASEB-READ-FALLBACK",
                    "verdict": "FAIL" if problems else "PASS",
                    "detail": "; ".join(problems) or
                              "Report優先・旧Canonicalはlegacyへフォールバック"})

    # ADR-0013境界: 非原子性はPre-Canonical診断（gate所有・恒久Advisory）へ移管。
    # Canonical段はreqsmellを呼ばない（rollout選定は空）。
    problems = []
    non_atomic = "注文管理システムは注文データを保存および更新しなければならない。"
    gate = gate_inspect(non_atomic, "ja", "POLICY")
    multi = [f for f in gate["findings"]
             if f["normalized_issue_code"] == "MULTIPLE_PRIMARY_ACTIONS"]
    if not multi:
        problems.append("gateがnon_atomicをMULTIPLE_PRIMARY_ACTIONSとして所有していない")
    elif multi[0]["blocking"] or multi[0]["validator_id"] != "raw-text-quality-gate":
        problems.append("Pre-Canonical診断のAdvisory・所有が不正")
    if is_blocking_by_policy("MULTIPLE_PRIMARY_ACTIONS"):
        problems.append("rollout選定が空になっていない（ADR-0013改訂未反映）")
    coord = "注文金額が100,000円以上である場合または検証結果が「失敗」である場合、" \
            "通知システムはエラー内容を管理者メールアドレスに送信しなければならない。"
    gate2 = gate_inspect(coord, "ja", "POLICY2")
    if any(f["blocking"] for f in gate2["findings"]):
        problems.append("raw_text段findingがblockingになっている（恒久Advisory違反）")
    results.append({"case_id": "BOUNDARY-POLICY",
                    "verdict": "FAIL" if problems else "PASS",
                    "detail": "; ".join(problems) or
                              "非原子性=Pre-Canonical診断（gate所有・Advisory）・"
                              "rollout選定空・raw_text恒久Advisory"})

    # ADR-0013境界: Canonical段のValidatorはsource textを再解析しない
    # （surface_analysis参照。source文字列を差し替えてもReportが変わらない）
    problems = []
    out = extract({"document_id": "REPARSE", "text":
                   "通知システムは当該請求書PDFを顧客メールアドレスに"
                   "送信しなければならない。"}, "REQ-NO-REPARSE")
    base_c = out["canonical"]
    res_a = validate_all(copy.deepcopy(base_c))
    codes_a = sorted(f["normalized_issue_code"] for f in res_a["report"]["findings"])
    if "DEICTIC_REFERENCE" not in codes_a:
        problems.append("surface_analysis由来のDEICTICが検出されない")
    mutated = copy.deepcopy(base_c)
    mutated["source"]["text"] = "SENTINEL-NOT-JAPANESE"
    res_b = validate_all(mutated)
    codes_b = sorted(f["normalized_issue_code"] for f in res_b["report"]["findings"])
    if codes_a != codes_b:
        problems.append(f"source文字列の差し替えでReportが変化（再解析の疑い）: "
                        f"{codes_a} vs {codes_b}")
    results.append({"case_id": "NO-REPARSE",
                    "verdict": "FAIL" if problems else "PASS",
                    "detail": "; ".join(problems) or
                              "Canonical段検査はsurface_analysis参照のみ"
                              "（source差し替えでも同一Report）"})

    # 承認ゲート: コアValidator由来のblockingでreview_ready遷移が遮断される
    problems = []
    out = extract({"document_id": "POLICY", "text": non_atomic}, "REQ-POLICY-APPROVAL")
    ready = promote_to_review_ready(out["canonical"])
    if ready["ok"]:
        problems.append("blocking finding付き要求がreview_readyへ遷移できてしまう")
    results.append({"case_id": "BLOCKING-APPROVAL",
                    "verdict": "FAIL" if problems else "PASS",
                    "detail": "; ".join(problems) or
                              "review_ready遷移がコアValidatorのblockingで遮断される"})

    pointer_rate = with_pointer / total_findings if total_findings else 1.0
    issue_acc = expected_hit / expected_total if expected_total else 1.0
    trace_rate = trace_ok / trace_total if trace_total else 1.0
    gate_pass = (pointer_rate >= 0.95 and issue_acc >= 0.95 and trace_rate == 1.0
                 and all(r["verdict"] == "PASS" for r in results))
    results.append({
        "case_id": "STEP4-METRICS",
        "verdict": "PASS" if gate_pass else "FAIL",
        "detail": f"Pointer対応率={pointer_rate:.0%}（{with_pointer}/{total_findings}） "
                  f"issue code正解率={issue_acc:.0%}（{expected_hit}/{expected_total}） "
                  f"Rule追跡率={trace_rate:.0%}",
    })
    summary = {"pass": sum(1 for r in results if r["verdict"] == "PASS"),
               "fail": sum(1 for r in results if r["verdict"] == "FAIL"),
               "pointer_rate": round(pointer_rate, 4),
               "issue_code_accuracy": round(issue_acc, 4),
               "rule_trace_rate": round(trace_rate, 4)}
    return {"results": results, "summary": summary}
