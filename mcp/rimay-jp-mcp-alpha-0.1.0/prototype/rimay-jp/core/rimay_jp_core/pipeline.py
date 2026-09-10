"""縦断パイプライン実行とCorpus回帰評価（GATE-2判定材料）。"""
from pathlib import Path

import yaml

from . import MVP_CONDITIONS
from .lexicon import case_frames
from .normalizer import normalize
from .validator import validate
from .serializer import render_requirement_views
from .parser import parse, ParseError
from .equivalence import compare, compare_conformance, check_sidecar, canonicalize_ast
from .model import is_blocked
from .response_expression import ResponseExpressionError, iter_core_responses
from .response_block import ResponseBlockError
from .condition_expression import ConditionExpressionError, iter_core_conditions


def _in_mvp(expected_canonical: dict) -> bool:
    core = expected_canonical.get("rimay_core") or {}
    try:
        responses = list(iter_core_responses(
            core,
            source_text=(expected_canonical.get("source") or {}).get("text"),
        ))
        conditions = list(iter_core_conditions(core))
    except (ResponseExpressionError, ResponseBlockError, ConditionExpressionError):
        return False
    if not responses or any(
            ((response.get("action") or {}).get("family") not in case_frames())
            for _path, response in responses):
        return False
    for _path, cond in conditions:
        if cond.get("type") not in MVP_CONDITIONS:
            return False
    return True


def _match_expected(canonical: dict, expected_core: dict) -> list[str]:
    """抽出Canonicalと期待Canonicalの突合（スロット完全一致検査）。

    等価比較用のproject()はrimay_action_id（表記事項）を落とすが、
    期待値突合では抽出結果そのもの（None除去のみ）と比較する。
    """
    def _strip(v):
        if isinstance(v, dict):
            return {k: _strip(x) for k, x in v.items() if x is not None}
        if isinstance(v, list):
            return [_strip(x) for x in v]
        return v
    diffs = []

    def walk(exp, act, path):
        if isinstance(exp, dict):
            act = act if isinstance(act, dict) else {}
            for k, v in exp.items():
                walk(v, act.get(k), f"{path}/{k}")
        elif isinstance(exp, list):
            act = act if isinstance(act, list) else []
            if len(exp) != len(act):
                diffs.append(f"{path}: expected {len(exp)} items, got {len(act)}")
                return
            for i, v in enumerate(exp):
                walk(v, act[i] if i < len(act) else None, f"{path}/{i}")
        else:
            if exp is None:
                return
            if exp != act:
                diffs.append(f"{path}: expected {exp!r}, got {act!r}")

    walk(expected_core, _strip(canonical["rimay_core"]), "")
    return diffs


def run_case(path: Path) -> dict:
    """1ケースの縦断実行。戻り値: {case_id, verdict, detail}。"""
    case = yaml.safe_load(path.read_text(encoding="utf-8"))
    cid = case["case_id"]
    expected = case.get("expected_result", "accept")
    canonical, findings = normalize(case["japanese"], f"REQ-{cid}")
    findings += validate(canonical, phase2_slice=False)

    if expected != "accept":
        # 負例: 期待コードのfindingが出て、かつ成功扱いされないこと
        exp_codes = set(case.get("expected_codes") or [])
        got_codes = {f["code"] for f in findings}
        if not is_blocked(findings):
            return {"case_id": cid, "verdict": "FAIL",
                    "detail": f"不正入力がblockingなしで通過: findings={sorted(got_codes)}"}
        if exp_codes and not (exp_codes & got_codes):
            return {"case_id": cid, "verdict": "FAIL",
                    "detail": f"期待コード{sorted(exp_codes)}が未検出: {sorted(got_codes)}"}
        return {"case_id": cid, "verdict": "PASS", "detail": f"rejected: {sorted(got_codes)}"}

    # 正例
    if not _in_mvp(case["expected_canonical"]):
        # MVP外のケース: PROFILE-OUTとして成功扱いしないことを確認
        codes = {f["code"] for f in findings}
        if "PROFILE-OUT" in codes or is_blocked(findings):
            return {"case_id": cid, "verdict": "SKIP",
                    "detail": "MVP対象外（PROFILE-OUTとして検出済み）"}
        return {"case_id": cid, "verdict": "FAIL",
                "detail": "MVP外入力がPROFILE-OUTなしで通過"}

    if is_blocked(findings):
        return {"case_id": cid, "verdict": "FAIL",
                "detail": f"正例がblocked: {[(f['code'], f['message']) for f in findings]}"}

    # Canonical Requirement Schema適合（canonical-requirement.schema.json）
    from .schema_check import validate_schema
    schema_errors = validate_schema(canonical)
    if schema_errors:
        return {"case_id": cid, "verdict": "FAIL",
                "detail": f"Schema違反: {schema_errors}"}

    # 期待Canonicalとの突合
    diffs = _match_expected(canonical, case["expected_canonical"]["rimay_core"])
    exp_ext = case["expected_canonical"].get("extensions") or {}
    if (canonical.get("extensions") or {}) != exp_ext:
        diffs.append(f"/extensions: expected {exp_ext}, got {canonical.get('extensions')}")
    if diffs:
        return {"case_id": cid, "verdict": "FAIL", "detail": f"抽出不一致: {diffs}"}

    # Serializer → Parser → 射影意味等価
    views = render_requirement_views(canonical)
    try:
        ast = parse(views["english_rimay"])
    except ParseError as e:
        return {"case_id": cid, "verdict": "FAIL",
                "detail": f"Serializer出力がParser不受理: {e}: {views['english_rimay']}"}
    eq = compare(canonical, ast)
    if eq:
        return {"case_id": cid, "verdict": "FAIL", "detail": f"射影意味不一致: {eq}"}

    # grammar conformance検査（§21.5・D4: semanticと別軸）。C4 migration完了により
    # Canonical側rimay_action_id差分の除外を解除（RC-005。全差分をGate対象とする）
    conf = compare_conformance(canonical, ast)
    if conf:
        return {"case_id": cid, "verdict": "FAIL", "detail": f"conformance不一致: {conf}"}

    # sidecar完全性・manifest整合
    sc = check_sidecar(canonical, views)
    if sc:
        return {"case_id": cid, "verdict": "FAIL", "detail": f"sidecar: {sc}"}

    # 基準english_rimay（corpus記載文）もParserが受理し同一Canonicalへ戻ること
    ref = case.get("english_rimay", "").strip()
    if ref:
        try:
            ref_ast = parse(ref)
            ref_eq = compare(canonical, ref_ast)
            if ref_eq:
                return {"case_id": cid, "verdict": "FAIL",
                        "detail": f"基準英文との射影不一致: {ref_eq}"}
        except ParseError as e:
            return {"case_id": cid, "verdict": "FAIL", "detail": f"基準英文がParser不受理: {e}"}

    return {"case_id": cid, "verdict": "PASS",
            "detail": views["english_rimay"]}


def run_corpus(dev_dir: Path, neg_dir: Path) -> dict:
    results = []
    for p in sorted(dev_dir.glob("*.yaml")):
        results.append(run_case(p))
    for p in sorted(neg_dir.glob("*.yaml")):
        results.append(run_case(p))
    # regressionの実行可能ケース（japanese+expected_canonicalを持つもの。
    # 3F由来のcandidateスケルトンは対象外）
    reg_dir = dev_dir.parent / "regression"
    if reg_dir.exists():
        for p in sorted(reg_dir.glob("*.yaml")):
            case = yaml.safe_load(p.read_text(encoding="utf-8"))
            if case.get("japanese") and case.get("expected_canonical"):
                results.append(run_case(p))
    summary = {
        "pass": sum(1 for r in results if r["verdict"] == "PASS"),
        "fail": sum(1 for r in results if r["verdict"] == "FAIL"),
        "skip": sum(1 for r in results if r["verdict"] == "SKIP"),
    }
    return {"results": results, "summary": summary}
