"""Rimay conformance runner（改善計画C2・§22）。

paper-only Gateの実行体。corpus/rimay-conformance/ のfixture（C2凍結・76件以上）を
fixture契約検査 → clean-room Parser実行 → 期待値照合の順で処理する。

契約（§22.2・§22.3）:
  - fixture契約違反（欠落field・重複ID・hash不整合・件数不足）は ``fixture_invalid``
    として exit 2 相当で報告し、Parser実行結果と混同しない。
  - 空実行（fixture 0件）は成功ではなく契約違反。
  - 負例は ``rejected`` をassertし、"not accepted" で済ませない（診断codeまで照合）。
  - reference oracleはLicense Gate前は ``oracle_not_run``。paper Gateの成否と分離する。

決定性（§22.4）: signatureは case_id / input hash / outcome / diagnostic
(code/offset/expected/found) / rule ID / normalized roles / profile hash の
canonical JSONに対するsha256。環境metadata・実行時刻はsignature対象外
（本runnerは実行時刻を一切記録しない）。
"""
from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

import yaml

_RIMAY = Path(__file__).resolve().parents[1]
if str(_RIMAY / "core") not in sys.path:
    sys.path.insert(0, str(_RIMAY / "core"))

from rimay_jp_core.english_lexer import PARSE_ERROR_CODES, ParseError  # noqa: E402
from rimay_jp_core.parser import parse  # noqa: E402
from rimay_jp_core.equivalence import canonicalize_ast, _entity  # noqa: E402

CORPUS_DIR = _RIMAY / "corpus" / "rimay-conformance"
FIXTURE_FILES = ("source-cases.yaml", "boundary-cases.yaml", "extension-cases.yaml")

# source manifestと同値（一次資料の同一性・fixture側hash整合の検査に使用）
VOR_HASH = "sha256:75795b18174f477a281b9b08df93c2bef2e0a347e9b4d0ad60a618bcb2f169f7"
GRAMMAR_HASH = "sha256:0f7c4af22ab60329e85b972951be46bedecae2da2a5913b10d2f01d05bb1aa7e"

REQUIRED_MIN = {
    "baseline": 7, "action_positive": 10, "role_missing": 10,
    "preposition_substitution": 10, "condition_positive": 5, "condition_negative": 5,
    "structure": 8, "lexer_boundary": 8, "operator_role_contract": 12, "extension": 1,
    "structure_negative": 4,
}
TOTAL_MIN = 76

_ORIGIN_HASH = {"emse_vor": VOR_HASH, "official_repository": GRAMMAR_HASH,
                "rimay_jp_extension": None}
_EXPECTED_CLEAN_ROOM = {"accept", "reject", "profile_out"}
_ORIGINS = set(_ORIGIN_HASH)
_NON_ROLE_KEYS = {"actor", "modality", "action"}


class FixtureContractError(Exception):
    """fixture/profile契約違反（§22.3 exit 2）。"""


def load_fixtures(corpus_dir: Path = CORPUS_DIR) -> list[dict]:
    """3ファイルを読み、fixture契約を検査する。違反はFixtureContractError。"""
    violations: list[str] = []
    cases: list[dict] = []
    for fname in FIXTURE_FILES:
        p = corpus_dir / fname
        if not p.exists():
            violations.append(f"missing fixture file: {fname}")
            continue
        doc = yaml.safe_load(p.read_text(encoding="utf-8"))
        for c in doc.get("cases", []) or []:
            c["_file"] = fname
            cases.append(c)

    ids: set[str] = set()
    for c in cases:
        cid = c.get("case_id", "?")
        if cid in ids:
            violations.append(f"{cid}: duplicate case_id")
        ids.add(cid)
        if not str(cid).startswith("RCONF-"):
            violations.append(f"{cid}: case_id must start with RCONF-")
        for field in ("category", "source", "text", "expected"):
            if field not in c:
                violations.append(f"{cid}: missing field {field}")
        src = c.get("source") or {}
        origin = src.get("origin")
        if origin not in _ORIGINS:
            violations.append(f"{cid}: origin {origin!r} not in {sorted(_ORIGINS)}")
        elif src.get("source_hash") != _ORIGIN_HASH[origin]:
            violations.append(f"{cid}: source_hash does not match manifest hash for {origin}")
        if origin == "official_repository" and not src.get("repository_evidence_kind"):
            violations.append(f"{cid}: official_repository requires repository_evidence_kind")
        if src.get("provenance") not in ("verbatim", "verbatim-fragment", "assembled"):
            violations.append(f"{cid}: provenance invalid")
        if src.get("provenance") == "assembled":
            mods = src.get("modifications")
            if not mods:
                # 注釈指針の適用範囲と整合（assembled全件に組立記録を必須。RC-014追補）
                violations.append(f"{cid}: assembled case requires modifications record")
            elif "source_note/note参照" in str(mods):
                # 参照形は正式な構造化契約（指針0.1.1）: 参照先の存在と非自明性を検査
                ref = (src.get("source_note") or "") + (c.get("note") or "")
                if len(ref.strip()) < 10:
                    violations.append(
                        f"{cid}: modificationsが参照形だが参照先source_note/noteが空か不十分")
        exp = c.get("expected") or {}
        if exp.get("clean_room") not in _EXPECTED_CLEAN_ROOM:
            violations.append(f"{cid}: expected.clean_room invalid")
        if exp.get("clean_room") in ("reject", "profile_out"):
            if exp.get("error_code") not in PARSE_ERROR_CODES:
                violations.append(f"{cid}: negative case requires expected.error_code from §19.6 enum")
        if exp.get("reference") != "unknown_until_oracle":
            violations.append(f"{cid}: expected.reference must be unknown_until_oracle before Gate L")
        if not (c.get("text") or "").strip():
            violations.append(f"{cid}: empty text")

    counts: dict[str, int] = {}
    for c in cases:
        counts[c.get("category", "?")] = counts.get(c.get("category", "?"), 0) + 1
    for cat, mn in REQUIRED_MIN.items():
        if counts.get(cat, 0) < mn:
            violations.append(f"category {cat}: {counts.get(cat, 0)} < required {mn}")
    if len(cases) < TOTAL_MIN:
        violations.append(f"total fixtures {len(cases)} < {TOTAL_MIN}")
    if not cases:
        violations.append("empty fixture set (0 cases) — 空実行は成功ではない")

    if violations:
        raise FixtureContractError("; ".join(violations))
    return cases


def _roles_of(core_resp: dict) -> dict:
    return {k: v for k, v in core_resp.items() if k not in _NON_ROLE_KEYS}


def run_case(c: dict) -> dict:
    """1 fixtureを実行し、結果と期待の照合を返す。"""
    cid = c["case_id"]
    text = c["text"].rstrip("\n")
    exp = c["expected"]
    want = exp["clean_room"]
    r: dict = {
        "case_id": cid,
        "category": c["category"],
        "input_hash": "sha256:" + hashlib.sha256(text.encode("utf-8")).hexdigest(),
        "outcome": None,
        "diagnostic": None,
        "rimay_action_id": None,
        "emse_rule_id": None,
        "roles": None,
        "reference": "oracle_not_run",
        "mismatches": [],
    }
    try:
        ast = parse(text)
        r["outcome"] = "accepted"
        act = ast["response"]["action"]
        r["rimay_action_id"] = act.get("rimay_action_id")
        r["emse_rule_id"] = act.get("emse_rule_id")
        core = canonicalize_ast(ast)
        roles = _roles_of(core["response"])
        r["roles"] = dict(sorted(roles.items()))
        if want != "accept":
            r["mismatches"].append(
                {"kind": "outcome", "expected": want, "actual": "accepted"})
        else:
            if exp.get("family") and core["response"]["action"]["family"] != exp["family"]:
                r["mismatches"].append({"kind": "family", "expected": exp["family"],
                                        "actual": core["response"]["action"]["family"]})
            if exp.get("modality") and core["response"]["modality"] != exp["modality"]:
                r["mismatches"].append({"kind": "modality", "expected": exp["modality"],
                                        "actual": core["response"]["modality"]})
            if exp.get("rimay_action_id") and r["rimay_action_id"] != exp["rimay_action_id"]:
                r["mismatches"].append({"kind": "rimay_action_id",
                                        "expected": exp["rimay_action_id"],
                                        "actual": r["rimay_action_id"]})
            if exp.get("emse_rule_id") and r["emse_rule_id"] != exp["emse_rule_id"]:
                r["mismatches"].append({"kind": "emse_rule_id",
                                        "expected": exp["emse_rule_id"],
                                        "actual": r["emse_rule_id"]})
            want_roles = {k: _entity(v) for k, v in (exp.get("roles") or {}).items()}
            if want_roles != roles:
                r["mismatches"].append({"kind": "roles",
                                        "expected": dict(sorted(want_roles.items())),
                                        "actual": dict(sorted(roles.items()))})
            if exp.get("condition_type"):
                got = core["conditions"][0]["type"] if core["conditions"] else None
                if got != exp["condition_type"]:
                    r["mismatches"].append({"kind": "condition_type",
                                            "expected": exp["condition_type"], "actual": got})
            if exp.get("operator"):
                got = (core["conditions"][0].get("predicate") or {}).get("operator") \
                    if core["conditions"] else None
                if got != exp["operator"]:
                    r["mismatches"].append({"kind": "operator",
                                            "expected": exp["operator"], "actual": got})
    except ParseError as e:
        d = e.diagnostic()
        r["outcome"] = "profile_out" if e.code == "PROFILE_OUT" else "rejected"
        r["diagnostic"] = {"code": d["code"], "offset": d["offset"],
                           "expected": d["expected"], "found": d["found"]}
        if want == "accept":
            r["mismatches"].append({"kind": "outcome", "expected": "accept",
                                    "actual": r["outcome"],
                                    "diagnostic_code": e.code})
        else:
            want_outcome = "profile_out" if want == "profile_out" else "rejected"
            if r["outcome"] != want_outcome:
                r["mismatches"].append({"kind": "outcome", "expected": want_outcome,
                                        "actual": r["outcome"]})
            if exp.get("error_code") and e.code != exp["error_code"]:
                r["mismatches"].append({"kind": "diagnostic_code",
                                        "expected": exp["error_code"], "actual": e.code})
    return r


def run_conformance(corpus_dir: Path = CORPUS_DIR) -> dict:
    """全fixtureを実行し、決定論的reportを返す（実行時刻は記録しない）。"""
    cases = load_fixtures(corpus_dir)
    results = [run_case(c) for c in cases]
    mismatched = [r for r in results if r["mismatches"]]
    from rimay_jp_core.parser import PARSER_VERSION
    from rimay_jp_core.english_profile import grammar_profile_hash as _grammar_profile_hash
    report = {
        "gate": "paper_only",
        "fixture_total": len(results),
        "conforming": len(results) - len(mismatched),
        "mismatched": len(mismatched),
        "reference_gate": "not_run",   # License Gate前（§16）
        "parser_version": PARSER_VERSION,
        "grammar_profile_hash": _grammar_profile_hash(),
        "results": results,
    }
    report["signature"] = signature_of(report)
    return report


def signature_of(report: dict) -> str:
    """§22.4のsignature: 環境metadata・時刻を含まないcanonical JSONのsha256。"""
    payload = [{
        "case_id": r["case_id"],
        "input_hash": r["input_hash"],
        "outcome": r["outcome"],
        "diagnostic": r["diagnostic"],
        "rimay_action_id": r["rimay_action_id"],
        "emse_rule_id": r["emse_rule_id"],
        "roles": r["roles"],
        "mismatches": r["mismatches"],
    } for r in report["results"]]
    blob = json.dumps({"parser_version": report["parser_version"],
                       "grammar_profile_hash": report["grammar_profile_hash"],
                       "cases": payload},
                      ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    return "sha256:" + hashlib.sha256(blob.encode("utf-8")).hexdigest()


def run_conformance_checks() -> dict:
    """CLI corpus用の要約runner。

    C3以降は--enforce-paper相当（paper mismatch 0件）をPASS条件とする（§24 C2→C3切替）。
    C2で凍結したbaseline reportは履歴として保持する（比較Gateには使用しない）。
    """
    results = []
    try:
        report = run_conformance()
    except FixtureContractError as e:
        results.append({"verdict": "FAIL", "case_id": "RCONF-CONTRACT",
                        "detail": f"fixture契約違反: {e}"})
        return {"results": results, "summary": {"pass": 0, "fail": 1}}
    results.append({"verdict": "PASS", "case_id": "RCONF-CONTRACT",
                    "detail": f"fixture {report['fixture_total']}件（76件以上・全カテゴリ充足・hash整合）"})
    if report["mismatched"]:
        bad = [r["case_id"] for r in report["results"] if r["mismatches"]]
        results.append({"verdict": "FAIL", "case_id": "RCONF-ENFORCE-PAPER",
                        "detail": f"paper mismatch {report['mismatched']}件: {bad[:5]}"})
    else:
        results.append({"verdict": "PASS", "case_id": "RCONF-ENFORCE-PAPER",
                        "detail": f"paper positive/rule/Role差分0件（{report['fixture_total']}件、"
                                  f"signature {report['signature'][:19]}...）"})
    s = {"pass": sum(1 for r in results if r["verdict"] == "PASS"),
         "fail": sum(1 for r in results if r["verdict"] == "FAIL")}
    return {"results": results, "summary": s}


def compare_to_baseline(report: dict, frozen: dict) -> list[str]:
    """現行runと凍結baselineの差分（件数・case ID・診断・mismatch内容）を返す。"""
    drift: list[str] = []
    cur = {r["case_id"]: r for r in report["results"]}
    old = {r["case_id"]: r for r in frozen["results"]}
    for cid in sorted(set(cur) | set(old)):
        a, b = cur.get(cid), old.get(cid)
        if a is None or b is None:
            drift.append(f"{cid}: {'missing now' if a is None else 'new case'}")
            continue
        for key in ("outcome", "diagnostic", "mismatches", "rimay_action_id",
                    "emse_rule_id", "roles", "input_hash"):
            if a[key] != b[key]:
                drift.append(f"{cid}: {key} drift")
                break
    if report["signature"] != frozen.get("signature"):
        if not drift:
            drift.append("signature drift without case drift (contract bug)")
    return drift
