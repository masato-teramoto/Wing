"""Phase 4統合評価ランナー: holdout Corpusで§26.6のMVP成功条件を測定する。

- holdoutはルール調整に使用しない（本ランナーは測定と報告のみ）。
- 決定論的実装のためLLM実行条件の固定は不要。知識・規則の版数を記録する。
- 各指標は件数と95%信頼区間（Wilson）を併記する（§22.6）。
- 層別配分（各Action・各Condition最低3件・入力状態の下限・総数100件、§22.6／
  継続条件③）は期待値（ケース仕様）から算出しGateで機械検査する。
"""
import json
import math
from pathlib import Path

import yaml

from . import _ROOT  # noqa: F401
from rimay_jp_core.normalizer import normalize  # noqa: E402
from rimay_jp_core.validator import validate  # noqa: E402
from rimay_jp_core.serializer import render_requirement_views  # noqa: E402
from rimay_jp_core.jp_serializer import render_rimay_jp  # noqa: E402
from rimay_jp_core.parser import parse, ParseError  # noqa: E402
from rimay_jp_core.equivalence import compare, check_sidecar, project  # noqa: E402
from rimay_jp_core.model import is_blocked  # noqa: E402
from rimay_jp_core import PROFILE_VERSION
from rimay_jp_core.lexicon import versions  # noqa: E402
from .candidate_extractor import extract  # noqa: E402
from .dialogue_state import DialogueState  # noqa: E402
from .knowledge_router import route  # noqa: E402
from .information_classifier import classify  # noqa: E402
from .approval import promote_to_review_ready, approve  # noqa: E402
from generators.acceptance_criteria import generate as gen_ac  # noqa: E402


def wilson(k: int, n: int) -> tuple[float, float, float]:
    """比率と95%Wilson信頼区間。"""
    if n == 0:
        return 0.0, 0.0, 0.0
    p = k / n
    z = 1.96
    denom = 1 + z * z / n
    center = (p + z * z / (2 * n)) / denom
    half = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / denom
    return p, max(0.0, center - half), min(1.0, center + half)


class M:
    """分子/分母カウンタ。"""

    def __init__(self):
        self.k = 0
        self.n = 0

    def add(self, ok: bool):
        self.n += 1
        self.k += 1 if ok else 0

    def rate(self):
        return wilson(self.k, self.n)


def _match(expected, actual, diffs, path=""):
    if isinstance(expected, dict):
        actual = actual if isinstance(actual, dict) else {}
        for k, v in expected.items():
            _match(v, actual.get(k), diffs, f"{path}/{k}")
    elif isinstance(expected, list):
        actual = actual if isinstance(actual, list) else []
        if len(expected) != len(actual):
            diffs.append(f"{path}: len {len(expected)} != {len(actual)}")
            return
        for i, v in enumerate(expected):
            _match(v, actual[i], diffs, f"{path}/{i}")
    else:
        if expected is not None and expected != actual:
            diffs.append(f"{path}: {expected!r} != {actual!r}")


# §22.6層別の下限（Action・Condition各3件、入力状態はラチェット=現水準を下回らない）
_FAMILIES = ("SEND", "UPDATE", "CREATE", "STORE", "RECEIVE",
             "DISPLAY", "DELETE", "VERIFY", "CALCULATE", "NOTIFY")
_CONDITION_TYPES = ("WHEN", "IF", "WHILE", "BEFORE", "AFTER", "NONE")
_STATE_MIN = {"normal": 30, "gap": 10, "ambiguous": 8,
              "unsupported": 12, "classification": 15}


def strata(cases) -> dict:
    """層別配分を期待値（ケース仕様）から算出する。実装は実行しない。"""
    fam: dict = {}
    cond: dict = {}
    states: dict = {}
    scope_n = 0
    for c in cases:
        states[c["category"]] = states.get(c["category"], 0) + 1
        if c["category"] != "normal":
            continue
        core = c["expected_canonical"]["rimay_core"]
        f = core["response"]["action"]["family"]
        fam[f] = fam.get(f, 0) + 1
        t = core["conditions"][0]["type"] if core.get("conditions") else "NONE"
        cond[t] = cond.get(t, 0) + 1
        if core.get("scope"):
            scope_n += 1
    return {"families": fam, "conditions": cond, "states": states,
            "scope_cases": scope_n}


def _no_false_confirm(canonical) -> bool:
    prv = {p["id"]: p for p in canonical["provenance"]}
    for s in canonical["resolution"]["slots"].values():
        if s["status"] == "confirmed":
            for r in s.get("provenance_refs") or []:
                if prv[r]["resolution_method"] in ("heuristic_candidate", "synonym_match"):
                    return False
    return True


def run_holdout(holdout_dir: Path) -> dict:
    cases = [yaml.safe_load(p.read_text(encoding="utf-8"))
             for p in sorted(holdout_dir.glob("*.yaml"))]
    m = {name: M() for name in (
        "parser_pass", "equivalence", "sidecar", "slot_match", "jp_roundtrip",
        "gap_detection", "unknown_retention", "no_false_confirm",
        "question_precision", "question_recall", "unsupported_detection",
        "unregistered_detection", "classification_accuracy", "generation_ok")}
    route_tp = route_actual = route_expected = 0
    failures: list[str] = []

    for case in cases:
        cat = case["category"]
        cid = case["case_id"]

        if cat == "classification":
            got = classify(case["source_segment"]["text"])["classification"]
            ok = got == case["expected_classification"]
            m["classification_accuracy"].add(ok)
            if not ok:
                failures.append(f"{cid}: 分類 {case['expected_classification']} != {got}")
            continue

        if cat == "normal":
            canonical, findings = normalize(case["japanese"], f"REQ-{cid}")
            findings += validate(canonical, phase2_slice=False)
            if is_blocked(findings):
                for name in ("parser_pass", "equivalence", "sidecar", "slot_match",
                             "jp_roundtrip"):
                    m[name].add(False)
                failures.append(f"{cid}: 正例がblocked "
                                f"{[(f['code'], f['message']) for f in findings][:2]}")
                continue
            diffs: list[str] = []
            # スロット一致検査ではrimay_action_idも比較する（projectは等価比較用に
            # 表記事項を落とすため、None除去のみの射影を用いる）
            def _strip(v):
                if isinstance(v, dict):
                    return {k: _strip(x) for k, x in v.items() if x is not None}
                if isinstance(v, list):
                    return [_strip(x) for x in v]
                return v
            _match(case["expected_canonical"]["rimay_core"],
                   _strip(canonical["rimay_core"]), diffs)
            exp_ext = case["expected_canonical"].get("extensions") or {}
            if (canonical.get("extensions") or {}) != exp_ext:
                diffs.append("/extensions mismatch")
            m["slot_match"].add(not diffs)
            if diffs:
                failures.append(f"{cid}: スロット不一致 {diffs[:3]}")
            views = render_requirement_views(canonical)
            try:
                ast = parse(views["english_rimay"])
                m["parser_pass"].add(True)
                eq = compare(canonical, ast)
                m["equivalence"].add(not eq)
                if eq:
                    failures.append(f"{cid}: 等価不成立 {eq[:2]}")
            except ParseError as e:
                m["parser_pass"].add(False)
                m["equivalence"].add(False)
                failures.append(f"{cid}: Parser不受理 {e}")
            m["sidecar"].add(not check_sidecar(canonical, views))
            c2, _ = normalize(render_rimay_jp(canonical))
            m["jp_roundtrip"].add(
                project(c2) == project(canonical)
                and (c2.get("extensions") or {}) == (canonical.get("extensions") or {}))
            # 知識ルーティング（expected_routes付きケース）
            if case.get("expected_routes"):
                res = route(canonical)
                actual = set()
                for r in res["routes"]:
                    if r["source"] in ("action_frame", "state_model", "business_rule", "nfr"):
                        if r["hits"]:
                            actual |= {(r["source"], h.split(":", 1)[1]) for h in r["hits"]}
                        else:
                            actual.add((r["source"], "UNRESOLVED"))
                expected = {tuple(e) for e in case["expected_routes"]}
                route_tp += len(expected & actual)
                route_actual += len(actual)
                route_expected += len(expected)
                if expected != actual:
                    failures.append(f"{cid}: route {sorted(expected)} != {sorted(actual)}")
            # 下流生成可能率（承認まで通して受入基準生成）
            out = extract({"document_id": cid, "text": case["japanese"]}, f"REQ-{cid}")
            pr = promote_to_review_ready(out["canonical"])
            gen_ok = False
            if pr["ok"]:
                approve(out["canonical"], "usa", "2026-08-03")
                gen_ok = gen_ac(out["canonical"])["ok"]
            m["generation_ok"].add(gen_ok)
            if not gen_ok:
                failures.append(f"{cid}: 生成不可 {pr.get('reasons')}")
            continue

        if cat in ("gap", "ambiguous"):
            out = extract({"document_id": cid, "text": case["japanese"]}, f"REQ-{cid}")
            ds = DialogueState(out["canonical"])
            findings = ds.findings + validate(ds.canonical, phase2_slice=False)
            codes = {f["code"] for f in findings}
            exp_codes = set(case.get("expected_codes") or [])
            slots = ds.canonical["resolution"]["slots"]
            planned = {q["target_path"] for q in ds.open_questions()}
            expected_q = set(case.get("expected_question_targets") or [])
            if cat == "gap":
                # 不足の検出 = 期待コードのfinding、または期待質問の計画
                # （ヒューリスティック経路では欠落はunknownスロット＋質問として
                #   表面化する。§14.3の意味論）
                detected = bool(exp_codes & codes) or \
                    (bool(expected_q) and expected_q <= planned)
                m["gap_detection"].add(detected)
                if not detected:
                    failures.append(f"{cid}: 不足未検出 codes={sorted(codes)}")
            else:
                detected = (not exp_codes or bool(exp_codes & codes))
                if case.get("expected_candidates_min"):
                    slot = slots.get("/rimay_core/response/action/family") or {}
                    detected = detected and \
                        len(slot.get("candidates") or []) >= case["expected_candidates_min"]
                m["gap_detection"].add(detected)
                if not detected:
                    failures.append(f"{cid}: 曖昧性未検出 codes={sorted(codes)}")
            # unknown保持: 期待質問対象スロットが値なしunknown/proposedで保持される
            retained = all(
                (slots.get(t) or {}).get("status") in ("unknown", "proposed")
                for t in expected_q)
            m["unknown_retention"].add(retained)
            if not retained:
                failures.append(f"{cid}: unknown未保持 {expected_q}")
            m["no_false_confirm"].add(_no_false_confirm(ds.canonical))
            # 質問適合率（precision）と網羅（recall）
            for t in planned:
                m["question_precision"].add(t in expected_q)
            for t in expected_q:
                m["question_recall"].add(t in planned)
            if planned != expected_q:
                failures.append(f"{cid}: 質問 {sorted(expected_q)} != {sorted(planned)}")
            continue

        if cat == "unsupported":
            canonical, findings = normalize(case["japanese"], f"REQ-{cid}")
            findings += validate(canonical, phase2_slice=False)
            codes = {f["code"] for f in findings}
            exp_codes = set(case.get("expected_codes") or [])
            detected = bool(exp_codes & codes) and is_blocked(findings)
            m["unsupported_detection"].add(detected)
            if case.get("unregistered_term_case"):
                m["unregistered_detection"].add("JP-LEXICAL" in codes)
            if not detected:
                failures.append(f"{cid}: 未対応が通過 codes={sorted(codes)}")
            continue

    if route_actual or route_expected:
        route_p = route_tp / route_actual if route_actual else 0.0
        route_r = route_tp / route_expected if route_expected else 0.0
    else:
        route_p = route_r = 0.0

    metrics = {name: {"k": c.k, "n": c.n,
                      "rate": round(c.rate()[0], 4),
                      "ci95": [round(c.rate()[1], 4), round(c.rate()[2], 4)]}
               for name, c in m.items()}
    metrics["knowledge_route"] = {"tp": route_tp, "actual": route_actual,
                                  "expected": route_expected,
                                  "precision": round(route_p, 4),
                                  "recall": round(route_r, 4)}
    st = strata(cases)
    metrics["strata"] = st
    gate = {
        "cases_100": len(cases) >= 100,
        "strata_family_min3": all(st["families"].get(f, 0) >= 3
                                  for f in _FAMILIES),
        "strata_condition_min3": all(st["conditions"].get(t, 0) >= 3
                                     for t in _CONDITION_TYPES),
        "strata_scope_min3": st["scope_cases"] >= 3,
        "strata_state_min": all(st["states"].get(s, 0) >= n
                                for s, n in _STATE_MIN.items()),
        "parser_pass_100": m["parser_pass"].k == m["parser_pass"].n > 0,
        "equivalence_95": m["equivalence"].rate()[0] >= 0.95,
        "sidecar_100": m["sidecar"].k == m["sidecar"].n > 0,
        "slot_match_90": m["slot_match"].rate()[0] >= 0.90,
        "gap_detection_95": m["gap_detection"].rate()[0] >= 0.95,
        "unregistered_100": m["unregistered_detection"].k
                            == m["unregistered_detection"].n > 0,
        "unsupported_95": m["unsupported_detection"].rate()[0] >= 0.95,
        "unknown_retention_100": m["unknown_retention"].k
                                 == m["unknown_retention"].n > 0,
        "no_false_confirm_100": m["no_false_confirm"].k
                                == m["no_false_confirm"].n > 0,
        "route_precision_85": route_p >= 0.85,
        "route_recall_90": route_r >= 0.90,
        "question_precision_85": m["question_precision"].rate()[0] >= 0.85,
        "classification_90": m["classification_accuracy"].rate()[0] >= 0.90,
        "generation_70": m["generation_ok"].rate()[0] >= 0.70,
    }
    return {"cases": len(cases), "metrics": metrics, "gate": gate,
            "gate_pass": all(gate.values()), "failures": failures,
            "versions": {**versions(), "profile": PROFILE_VERSION,
                         "implementation": "deterministic (LLM未使用)"}}


def print_report(out: dict):
    print(f"holdout cases={out['cases']} versions={out['versions']}")
    for name, v in out["metrics"].items():
        if name == "strata":
            print(f"  {name:24} states={v['states']} scope={v['scope_cases']}")
            print(f"  {'':24} families={v['families']}")
            print(f"  {'':24} conditions={v['conditions']}")
        elif name == "knowledge_route":
            print(f"  {name:24} P={v['precision']:.2%} R={v['recall']:.2%} "
                  f"(tp={v['tp']}/act={v['actual']}/exp={v['expected']})")
        else:
            print(f"  {name:24} {v['k']}/{v['n']} = {v['rate']:.2%} "
                  f"CI95=[{v['ci95'][0]:.2%}, {v['ci95'][1]:.2%}]")
    print("  gate:", "PASS" if out["gate_pass"] else "FAIL",
          {k: v for k, v in out["gate"].items() if not v} or "(all criteria met)")
    for f in out["failures"]:
        print(f"  [NG] {f}")
