"""validation-router: 多層検証の統合実行（Phase 3D、構想書 §21 Phase 3D検証層）。

層: (1)Rimay-JP表層往復 (2)Canonical Schema (3)Action Frame・格
    (4)English Rimay Grammar (5)AST射影意味等価 (6)sidecar完全性
    (7)品質（曖昧語・指示語） (8)ドメイン整合性 (9)描画前提（event完全性）
失敗は 日本語側 / 知識側 / Rimay側 / 拡張情報側 へ分類し、
各findingへ根拠付き修正候補（fix_candidates）または確認事項（clarification）を付与する。
"""
import copy
import re
from functools import lru_cache

from . import _ROOT  # noqa: F401
from rimay_jp_core.validator import validate  # noqa: E402
from rimay_jp_core.schema_check import validate_schema  # noqa: E402
from rimay_jp_core.serializer import render_requirement_views  # noqa: E402
from rimay_jp_core.jp_serializer import parse_rimay_jp, render_rimay_jp  # noqa: E402
from rimay_jp_core.normalizer import normalize  # noqa: E402
from rimay_jp_core.parser import parse, ParseError  # noqa: E402
from rimay_jp_core.equivalence import compare, compare_conformance, check_sidecar, project  # noqa: E402
from rimay_jp_core.model import finding, is_blocked  # noqa: E402
from rimay_jp_core.lexicon import terms, knowledge_bank  # noqa: E402
from rimay_jp_core.response_expression import (  # noqa: E402
    ResponseBlockError,
    ResponseExpressionError,
)
from rimay_jp_core.condition_expression import (  # noqa: E402
    ConditionExpressionError,
    iter_core_conditions,
)
from .knowledge_router import route  # noqa: E402

# 失敗分類（GATE-3D: 日本語側・知識側・Rimay側・拡張情報側）
_GROUPS = {
    "japanese": ("JP-",),
    "knowledge": ("KNOWLEDGE-", "DOMAIN", "QUALITY-"),
    "rimay": ("RIMAY-ACTION", "RIMAY-ROLE", "RIMAY-MODAL", "AST-EQUIVALENCE", "PROFILE-OUT"),
    "extension": ("RIMAY-CONSTRAINT", "SIDECAR-"),
}

# 必須Role欠落時の修正候補に使う用語種別（辞書に根拠を持つ候補のみ提示する）
_ROLE_TERM_TYPES = {
    "destination": ("actor", "property"),
    "source": ("actor", "class"),
    "location": ("class",),
    "display_location": ("class",),
    "rule": ("rule",),
    "theme": ("class",),
    "content": ("class",),
    "input": ("class",),
    "result": ("property",),
    "actor": ("actor",),
}


def classify_finding(code: str) -> str:
    for group, prefixes in _GROUPS.items():
        if any(code.startswith(p) for p in prefixes):
            return group
    return "governance"  # PATCH-INVALID / PROVENANCE-MISSING 等の統制系


def _enrich(f: dict, canonical: dict) -> dict:
    """findingへ根拠付き修正候補または確認事項を付与する（GATE-3D）。"""
    code, path = f["code"], f.get("path") or ""
    if code == "DOMAIN":
        states = (f.get("evidence") or {}).get("known_states") or []
        sm = (f.get("evidence") or {}).get("state_model")
        f["fix_candidates"] = [{"value": s, "source": f"state-model:{sm}",
                                "status": "proposed"} for s in states]
    elif code == "JP-OMISSION" and (
            path.startswith("/rimay_core/response/") or
            (path.startswith("/rimay_core/response_expression/") and
             "/response/" in path) or
            (path.startswith("/rimay_core/response_block/items/") and
             "/response/" in path)):
        field = path.rsplit("/", 1)[-1]
        types = _ROLE_TERM_TYPES.get(field)
        if types:
            cands = [t["id"] for t in terms() if t["type"] in types][:5]
            f["fix_candidates"] = [{"value": c, "source": f"term:{c}",
                                    "status": "proposed"} for c in cands]
    elif code in ("QUALITY-AMBIGUOUS",):
        f["clarification"] = "時間条件を測定可能な形で指定してください（例：60秒以内）。"
    elif code == "RIMAY-ROLE":
        f["clarification"] = "トリガー事象の動作と対象（誰が何をどうしたとき）を指定してください。"
    return f


def _render_precheck(canonical: dict) -> list[dict]:
    """描画前提: 条件のevent完全性（English Rimay生成に必要な意味Role）。"""
    out = []
    for condition_path, cond in iter_core_conditions(canonical["rimay_core"]):
        if cond.get("type") in ("WHEN", "AFTER", "BEFORE"):
            ev = cond.get("event") or {}
            missing = [k for k in ("actor", "object") if not ev.get(k)]
            if not (ev.get("action") or {}).get("family"):
                missing.append("action.family")
            if missing:
                out.append(finding("RIMAY-ROLE",
                                   f"トリガー事象のRoleが不足しています: {missing}",
                                   f"{condition_path}/event",
                                   missing=missing))
    return out


# ---- 実行計画（ADR-0013 D5: Validator Registryから生成する） ----
# binding → 実装。各実装は input_contract が示す入力**だけ**を受け取る。
# Canonical段のinputsに raw_text は存在しない（機械的制限。
# 挙動面の保証はNO-REPARSE契約テストが担う）。

_INPUT_VOCAB = {"raw_text", "surface_analysis", "canonical_requirement",
                "domain_context", "validation_report"}


def _bind_schema(canonical, ctx):
    errors = validate_schema(canonical)
    ctx["schema_errors"] = errors
    return "schema", {"errors": errors}, []


def _bind_core(canonical, ctx):
    fs = validate(canonical, phase2_slice=False)
    return "core", {"findings": [f["code"] for f in fs]}, fs


def _bind_quality_surface(sa, ctx):
    # 入力はsurface_analysisのみ（Canonical・source textを受け取らない）
    deictic_words = sorted({d["word"] for d in (sa or {}).get("deictic") or []})
    fs = [finding("QUALITY-DEICTIC",
                  f"指示語「{w}」は要求IDまたは正式名称へ置き換えてください。")
          for w in deictic_words]
    return "quality", {"deictic": deictic_words}, fs


def _bind_domain(domain_context, ctx):
    out = route(domain_context["canonical"])
    return "domain", {"findings": [f["code"] for f in out["findings"]]}, out["findings"]


def _bind_render_precheck(canonical, ctx):
    fs = _render_precheck(canonical)
    return "render_precheck", {"findings": [f["code"] for f in fs]}, fs


def _bind_surface_roundtrip(canonical, ctx):
    fs: list[dict] = []
    views = render_requirement_views(canonical)
    rimay_jp = render_rimay_jp(canonical)
    try:
        ast = parse(views["english_rimay"])
        eq = compare(canonical, ast)
    except ParseError as e:
        eq = [f"parse error: {e}"]
    if eq:
        fs.append(finding("AST-EQUIVALENCE", f"射影意味等価が不成立: {eq[:3]}"))
    else:
        # C4: semantic不一致とconformance不一致を別finding化（主計画§20.2・D4）
        conf = compare_conformance(canonical, ast)
        if conf:
            fs.append(finding("RIMAY-CONFORMANCE", f"grammar conformance差分: {conf[:3]}"))
    for msg in check_sidecar(canonical, views):
        code = "SIDECAR-STALE" if "STALE" in msg else "SIDECAR-LOSS"
        fs.append(finding(code, msg))
    if canonical["rimay_core"].get("response_expression") is not None or \
            canonical["rimay_core"].get("condition_expression") is not None or \
            canonical["rimay_core"].get("response_block") is not None:
        try:
            parsed_core = parse_rimay_jp(rimay_jp)
            jp_ok = project({"rimay_core": parsed_core}) == project(canonical)
        except (ResponseExpressionError, ResponseBlockError,
                ConditionExpressionError):
            jp_ok = False
    else:
        c2, _f2 = normalize(rimay_jp)
        jp_ok = (project(c2) == project(canonical)
                 and (c2.get("extensions") or {}) == (canonical.get("extensions") or {}))
    if not jp_ok:
        fs.append(finding("JP-CASE",
                          "Rimay-JP再生成文の再解析が元Canonicalと一致しません。",
                          evidence_jp=rimay_jp))
    ctx["jp_roundtrip_ok"] = jp_ok
    ctx["artifacts"] = {"rimay_jp": rimay_jp, **views}
    return "surface", {"rimay_jp": rimay_jp,
                       "english_rimay": views["english_rimay"],
                       "jp_roundtrip_ok": jp_ok}, fs


_BINDINGS = {
    "schema": _bind_schema,
    "core": _bind_core,
    "quality_surface": _bind_quality_surface,
    "domain": _bind_domain,
    "render_precheck": _bind_render_precheck,
    "surface_roundtrip": _bind_surface_roundtrip,
}


def verify_plan(plan_doc: dict) -> list[str]:
    """実行計画の契約検査（Registry未登録Validator・語彙外契約・raw_text混入の拒否）。"""
    import yaml
    from rimay_jp_core.lexicon import ROOT as _R
    reg = yaml.safe_load((_R / "canonical" / "validator-registry.yaml")
                         .read_text(encoding="utf-8"))
    registered = {v["id"]: v for v in reg["validators"]}
    v: list[str] = []
    for e in plan_doc.get("validate_all") or []:
        if e["binding"] not in _BINDINGS:
            v.append(f"未知binding: {e['binding']}")
        if e["input_contract"] not in _INPUT_VOCAB:
            v.append(f"語彙外input_contract: {e['input_contract']}")
        if e["input_contract"] == "raw_text":
            v.append(f"Canonical段計画にraw_text契約: {e['binding']}")
        for vid in e["validators"]:
            if vid not in registered:
                v.append(f"Registry未登録Validator: {vid}")
            elif registered[vid].get("input_contract") == "raw_text":
                v.append(f"raw_text契約ValidatorをCanonical段へ配置: {vid}")
    return v


@lru_cache(maxsize=1)
def execution_plan() -> list[dict]:
    """RegistryのexecutionプランをロードしContract検査のうえ返す（ADR-0013 D5）。"""
    import yaml
    from rimay_jp_core.lexicon import ROOT as _R
    reg = yaml.safe_load((_R / "canonical" / "validator-registry.yaml")
                         .read_text(encoding="utf-8"))
    plan_doc = reg.get("execution_plan") or {}
    violations = verify_plan(plan_doc)
    if violations:
        raise RuntimeError(f"実行計画がRegistry契約に違反: {violations}")
    return plan_doc["validate_all"]


def validate_all(canonical: dict, vocabulary_context=None) -> dict:
    layers: dict[str, dict] = {}
    findings: list[dict] = []
    ctx: dict = {"schema_errors": []}

    # Canonical段のinputs（raw_textは存在しない=ADR-0013 D5の機械的制限）。
    # surface_analysis未記録の旧Canonicalのみ、唯一のAnalyzer=Normalizerへ委譲。
    sa = canonical.get("surface_analysis")
    if sa is None:
        from rimay_jp_core.normalizer import surface_signals
        sa = surface_signals(canonical.get("source", {}).get("text") or "")
    inputs = {
        "canonical_requirement": canonical,
        "surface_analysis": sa,
        "domain_context": {"canonical": copy.deepcopy(canonical)},
    }

    blocked = False
    for entry in execution_plan():
        if entry["phase"] == "post":
            findings = [_enrich(f, canonical) for f in findings]
            blocked = bool(ctx["schema_errors"]) or is_blocked(findings)
            if blocked:
                continue
        key, layer, fs = _BINDINGS[entry["binding"]](
            inputs[entry["input_contract"]], ctx)
        layers[key] = layer
        findings += fs

    findings = [_enrich(f, canonical) for f in findings]
    blocked = bool(ctx["schema_errors"]) or is_blocked(findings)
    artifacts = ctx.get("artifacts")
    jp_roundtrip_ok = ctx.get("jp_roundtrip_ok")

    classification: dict[str, list] = {"japanese": [], "knowledge": [], "rimay": [],
                                       "extension": [], "governance": []}
    for f in findings:
        classification[classify_finding(f["code"])].append(f["code"])

    # Step 4: finding正規化・重複排除・Validation Report生成。
    # Canonical段でのreqsmellによる日本語再解析は行わない（ADR-0013:
    # 表層スメルはFree-text Import診断=raw_text_gateの責務。二重解析の禁止）。
    from .validation_report import normalize_findings, dedup, build_report
    common = dedup(normalize_findings(findings, canonical["requirement_id"]))
    report, state = build_report(
        canonical, common, vocabulary_context=vocabulary_context)
    # 移行契約Phase B（2026-08-04移行）: legacy findings[]への新規書き込みを停止。
    # Reportが唯一の書き込み先。旧Canonicalの読み取りはread_findings()の
    # read-fallbackが担い、validation_state要約は維持する。
    canonical["validation_state"] = state

    return {"blocked": blocked, "findings": findings, "layers": layers,
            "classification": classification, "artifacts": artifacts,
            "jp_roundtrip_ok": jp_roundtrip_ok,
            "report": report, "validation_state": state}
