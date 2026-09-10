"""requirement-candidate-extractor: 要求候補セグメントからCanonical候補を抽出する（Phase 3A）。

方針（構想書 §21 Phase 3A / §14.3）:
- まず厳密Normalizer（rimay_jp_core.normalizer）を試みる（strictモード）。
- 不適合なら決定論的ヒューリスティックで部分抽出する（heuristicモード）。
  - 値を推測で埋めず、不明スロットは unknown（値なし＋confirmation_required）で保持する。
  - ヒューリスティック抽出値は proposed とし、confirmed にしない（誤自動確定率0%）。
    例外は「は」標識＋辞書完全一致のActorのみ（決定論的に一意なため confirmed）。
  - 複数のAction候補は resolution.slots の candidates に保持する。
  - すべての抽出値に source span のProvenanceを付ける。
"""
import re

from . import _ROOT  # noqa: F401  (sys.path設定の副作用)
from rimay_jp_core.normalizer import normalize, _VAGUE_WORDS  # noqa: E402
from rimay_jp_core.lexicon import lookup_jp, match_jp_prefix, case_frames, term_ids  # noqa: E402
from rimay_jp_core.model import new_canonical, set_slot, is_blocked  # noqa: E402
from .information_classifier import classify  # noqa: E402

# 自由文動詞 → Action family候補（複数可）。
# 正本はProfile SSOT（supported-profile.yaml japanese_surface.action_expressions、
# ADR-0014 D6）。標準動詞（格フレームのjapanese_canonical_verb）も単一候補として
# 含める（3D残課題の解消: 主体欠落等でstrict不成立でも動作候補を保持するため）。
from rimay_jp_core.lexicon import normalizer_profile as _normalizer_profile  # noqa: E402

_VERB_CANDIDATES = {k: list(v) for k, v in
                    _normalizer_profile()["action_expressions"].items()}
for _fam, _frame in case_frames().items():
    _VERB_CANDIDATES.setdefault(_frame["japanese_canonical_verb"], [_fam])

# 宛先として十分に具体的な用語種別（それ以外はconfirmation_required）
_CONCRETE_DEST_TYPES = {"actor", "property"}


def extract(segment: dict, requirement_id: str = "REQ-CANDIDATE", *,
            provider: str = "regex") -> dict:
    """source_segment → {classification, rationale, extraction_mode, canonical}。

    provider（改善計画 v0.3 P2／§7.3）: heuristic経路の語彙・形態解析。
    "regex"（既定）は従来実装と同一。"sudachipy"はD-005採用構成
    （core辞書・split mode C）で活用形・複数述語・形態素境界走査に対応する。
    Strict-first制御フローはproviderに依存しない（P2-1）。
    """
    text = segment["text"]
    cls = classify(text)
    result = {"classification": cls["classification"], "rationale": cls["rationale"],
              "extraction_mode": "none", "canonical": None}
    if cls["classification"] != "requirement_candidate":
        return result

    # strict: 制約付き日本語として受理できるか（Provider非依存）
    canonical, findings = normalize(text, requirement_id)
    if not is_blocked(findings):
        _attach_segment(canonical, segment)
        result.update(extraction_mode="strict", canonical=canonical)
        return result

    # heuristic: 部分抽出（unknown許容・proposed保持）
    if provider == "regex":
        canonical = _heuristic_extract(text, segment, requirement_id)
    elif provider == "sudachipy":
        canonical = _heuristic_extract_sudachi(text, segment, requirement_id)
    else:
        raise ValueError(f"unknown provider: {provider}")
    result.update(extraction_mode="heuristic", canonical=canonical)
    return result


def heuristic_extract(text: str, segment: dict,
                      requirement_id: str = "REQ-CANDIDATE", *,
                      provider: str = "regex") -> dict:
    """heuristic層の直接呼び出し（P2評価・minimal pair検証用の公開点）。

    extract()と異なり情報分類・strict判定を経ない。活用形minimal pair
    （送信した／しない等）は分類器が事実記述として正しくcontextへ分類する
    ため、述語再構成の評価はこの層を対象とする（分類器はP2スコープ外）。
    """
    if provider == "regex":
        return _heuristic_extract(text, segment, requirement_id)
    if provider == "sudachipy":
        return _heuristic_extract_sudachi(text, segment, requirement_id)
    raise ValueError(f"unknown provider: {provider}")


def _attach_segment(canonical: dict, segment: dict):
    seg = {k: v for k, v in segment.items() if k in
           ("document_id", "section_id", "text", "location")}
    canonical["source"]["source_segments"] = [seg]


def _heuristic_extract(text: str, segment: dict, rid: str) -> dict:
    c = new_canonical(rid)
    src = re.sub(r"\s+", "", text)
    c["source"]["text"] = src
    from rimay_jp_core.normalizer import (attach_surface_analysis,
                                          attach_normalization)
    attach_surface_analysis(c, src, "heuristic")  # 表層解析はNormalizerに集約（ADR-0013）
    _attach_segment(c, segment)
    resp: dict = {}
    c["rimay_core"]["response"] = resp

    # Sourceカバレッジ（ADR-0013 D4）: どこを解釈し、どこを未解釈のまま
    # 残したかを記録する（読み飛ばし=unconsumedは承認条件が遮断する）
    flags: list = [None] * len(src)

    def _mark(a: int, b: int, kind: str = "c"):
        for i in range(max(a, 0), min(b, len(src))):
            flags[i] = kind

    if src.endswith("。"):
        _mark(len(src) - 1, len(src), "i")
        body = src[:-1]
    else:
        body = src
    base = 0

    # モダリティ
    if body.endswith("しなければならない"):
        resp["modality"] = "MUST"
        set_slot(c, "/rimay_core/response/modality", "confirmed",
                 method="deterministic_parse")
        _mark(len(body) - len("しなければならない"), len(body))
        body = body[: -len("しなければならない")]
    elif body.endswith("してはならない"):
        resp["modality"] = "MUST_NOT"
        set_slot(c, "/rimay_core/response/modality", "confirmed",
                 method="deterministic_parse")
        _mark(len(body) - len("してはならない"), len(body))
        body = body[: -len("してはならない")]
    else:
        set_slot(c, "/rimay_core/response/modality", "unknown",
                 confirmation_required=True)

    # 条件候補（〜後、／〜したら、／〜のとき、／〜の場合、）
    m = re.match(r"^(.+?(後|したら|したとき|のとき|の場合))、(.*)$", body)
    if m:
        span, tail = m.group(1), m.group(3)
        ctype = {"後": "AFTER", "したら": "WHEN", "したとき": "WHEN",
                 "のとき": "WHEN", "の場合": "IF"}[m.group(2)]
        c["rimay_core"]["conditions"].append(
            {"type": ctype, "event": {"actor": None, "action": {"family": None}}})
        set_slot(c, "/rimay_core/conditions/0/type", "proposed", span,
                 method="heuristic_candidate")
        set_slot(c, "/rimay_core/conditions/0/event/actor", "unknown",
                 confirmation_required=True)
        _mark(base, base + len(span))
        _mark(base + len(span), base + len(span) + 1, "i")  # 読点
        base += len(span) + 1
        body = tail

    # 応答主体（<X>は）
    m = re.match(r"^(.+?)は(.+)$", body)
    if m:
        hit = lookup_jp(m.group(1))
        if hit and hit[1] == "actor":
            resp["actor"] = hit[0]
            set_slot(c, "/rimay_core/response/actor", "confirmed", m.group(1))
            _mark(base, base + len(m.group(1)) + 1)
            base += len(m.group(1)) + 1
            body = m.group(2)
    if "actor" not in resp:
        set_slot(c, "/rimay_core/response/actor", "unknown", confirmation_required=True)

    # 役割句・曖昧語の走査
    pos = 0
    while pos < len(body):
        seg_text = body[pos:]
        vw = next((w for w in _VAGUE_WORDS if seg_text.startswith(w)), None)
        if vw:
            c["extensions"].setdefault("time_constraints", []).append(
                {"kind": "DEADLINE", "value": None, "unit": None,
                 "applies_to": "response", "source_expression": vw})
            i = len(c["extensions"]["time_constraints"]) - 1
            set_slot(c, f"/extensions/time_constraints/{i}/value", "unknown",
                     confirmation_required=True)
            _mark(base + pos, base + pos + len(vw))
            pos += len(vw)
            continue
        hit = match_jp_prefix(seg_text)
        if hit:
            surface, tid, ttype = hit
            after = seg_text[len(surface):]
            pm = re.match(r"^(を|に|へ|から|で)", after)
            if pm:
                particle = pm.group(1)
                method = ("exact_term_match"
                          if surface == term_ids()[tid]["preferred_japanese"]
                          else "synonym_match")
                if particle == "を":
                    resp["theme"] = tid
                    set_slot(c, "/rimay_core/response/theme", "proposed", surface,
                             method=method)
                elif particle in ("に", "へ"):
                    resp["destination"] = tid
                    set_slot(c, "/rimay_core/response/destination", "proposed", surface,
                             method=method,
                             confirmation_required=(ttype not in _CONCRETE_DEST_TYPES))
                elif particle == "から":
                    resp["source"] = tid
                    set_slot(c, "/rimay_core/response/source", "proposed", surface,
                             method=method)
                _mark(base + pos, base + pos + len(surface) + len(particle))
                pos += len(surface) + len(particle)
                continue
        pos += 1  # 未知語は読み飛ばす（値を創作しない）

    # 動詞（末尾）→ family候補
    fams = None
    verb_span = None
    for verb, cands in sorted(_VERB_CANDIDATES.items(), key=lambda kv: -len(kv[0])):
        stem = verb[:-2] if verb.endswith("する") else verb
        if body.endswith(verb) or body.endswith(stem):
            fams, verb_span = cands, verb
            matched = verb if body.endswith(verb) else stem
            _mark(base + len(body) - len(matched), base + len(body))
            break
    if fams and len(fams) == 1:
        fam = fams[0]
        frame = case_frames().get(fam)
        resp["action"] = {"family": fam, "rimay_action_id": None}
        set_slot(c, "/rimay_core/response/action/family", "proposed", verb_span,
                 method="heuristic_candidate")
        set_slot(c, "/rimay_core/response/action/rimay_action_id", "unknown")
        # 必須Roleの欠落をunknownとして明示する
        if frame:
            from rimay_jp_core.validator import _ROLE_FIELD
            for role in frame["required_roles"]:
                field = _ROLE_FIELD.get(role)
                if field and field != "actor" and not resp.get(field):
                    set_slot(c, f"/rimay_core/response/{field}", "unknown",
                             confirmation_required=True)
    elif fams:
        resp["action"] = {"family": None, "rimay_action_id": None}
        set_slot(c, "/rimay_core/response/action/family", "proposed", verb_span,
                 method="heuristic_candidate", confirmation_required=True,
                 candidates=[{"value": f} for f in fams])
        set_slot(c, "/rimay_core/response/action/rimay_action_id", "unknown")
    else:
        resp["action"] = {"family": None, "rimay_action_id": None}
        set_slot(c, "/rimay_core/response/action/family", "unknown",
                 confirmation_required=True)
        set_slot(c, "/rimay_core/response/action/rimay_action_id", "unknown")

    attach_normalization(c, "heuristic", src, flags=flags)
    return c


# --- sudachipy heuristic経路（改善計画 v0.3 P2。D-005採用構成） ---------------

def _heuristic_extract_sudachi(text: str, segment: dict, rid: str) -> dict:
    """形態素境界を用いたheuristic抽出（D5: 述語解決へ限定利用）。

    regex経路との差分:
    - 述語句をサ変名詞＋する系の再構成で同定し、活用形（送信した／します／
      しない／して）を同一Action候補へ対応付ける（P2-3/4）。
    - 複数述語を検出し、単一Actionへ誤集約しない（P2-5。候補集合として保持し
      confirmedにしない。誤自動確定率0%維持）。
    - 未知語走査は1文字送りではなく形態素境界送り（P2-7）。句読点はignoredへ。
    - 解析ProvenanceをNormalization（canonical_hash対象外）へ記録する（§7.2）。
    モダリティ・条件節・応答主体（〜は）の判定はregex経路と同一の表層規則
    （非目的: モダリティ判定を形態素解析へ移さない）。
    """
    from .japanese_lexical_analysis import get_provider
    from .predicate_analysis import reconstruct_predicates

    sp = get_provider("sudachipy", dictionary="core", split_mode="C")
    c = new_canonical(rid)
    src = re.sub(r"\s+", "", text)
    c["source"]["text"] = src
    from rimay_jp_core.normalizer import (attach_surface_analysis,
                                          attach_normalization)
    attach_surface_analysis(c, src, "heuristic")
    _attach_segment(c, segment)
    resp: dict = {}
    c["rimay_core"]["response"] = resp

    flags: list = [None] * len(src)

    def _mark(a: int, b: int, kind: str = "c"):
        for i in range(max(a, 0), min(b, len(src))):
            flags[i] = kind

    if src.endswith("。"):
        _mark(len(src) - 1, len(src), "i")
        body = src[:-1]
    else:
        body = src
    base = 0

    # モダリティ（regex経路と同一の表層規則）
    if body.endswith("しなければならない"):
        resp["modality"] = "MUST"
        set_slot(c, "/rimay_core/response/modality", "confirmed",
                 method="deterministic_parse")
        _mark(len(body) - len("しなければならない"), len(body))
        body = body[: -len("しなければならない")]
    elif body.endswith("してはならない"):
        resp["modality"] = "MUST_NOT"
        set_slot(c, "/rimay_core/response/modality", "confirmed",
                 method="deterministic_parse")
        _mark(len(body) - len("してはならない"), len(body))
        body = body[: -len("してはならない")]
    else:
        set_slot(c, "/rimay_core/response/modality", "unknown",
                 confirmation_required=True)

    # 条件候補（regex経路と同一）
    m = re.match(r"^(.+?(後|したら|したとき|のとき|の場合))、(.*)$", body)
    if m:
        span, tail = m.group(1), m.group(3)
        ctype = {"後": "AFTER", "したら": "WHEN", "したとき": "WHEN",
                 "のとき": "WHEN", "の場合": "IF"}[m.group(2)]
        c["rimay_core"]["conditions"].append(
            {"type": ctype, "event": {"actor": None, "action": {"family": None}}})
        set_slot(c, "/rimay_core/conditions/0/type", "proposed", span,
                 method="heuristic_candidate")
        set_slot(c, "/rimay_core/conditions/0/event/actor", "unknown",
                 confirmation_required=True)
        _mark(base, base + len(span))
        _mark(base + len(span), base + len(span) + 1, "i")
        base += len(span) + 1
        body = tail

    # 応答主体（<X>は。regex経路と同一。辞書完全一致のみconfirmed）
    m = re.match(r"^(.+?)は(.+)$", body)
    if m:
        hit = lookup_jp(m.group(1))
        if hit and hit[1] == "actor":
            resp["actor"] = hit[0]
            set_slot(c, "/rimay_core/response/actor", "confirmed", m.group(1))
            _mark(base, base + len(m.group(1)) + 1)
            base += len(m.group(1)) + 1
            body = m.group(2)
    if "actor" not in resp:
        set_slot(c, "/rimay_core/response/actor", "unknown", confirmation_required=True)

    # 形態素解析（bodyのみ。P2-2: heuristic経路だけでProviderを呼ぶ）
    toks = sp.analyze(body, mode="C")
    units = reconstruct_predicates(toks)
    unit_spans = [(u["start"], u["end"]) for u in units]
    bounds = sorted({t.start for t in toks} | {t.end for t in toks})
    punct = {(t.start, t.end) for t in toks
             if t.part_of_speech[0] == "補助記号"}

    # 役割句・曖昧語の走査（形態素境界送り。述語spanはスキップして消費）
    pos = 0
    while pos < len(body):
        u_end = next((e for s, e in unit_spans if s <= pos < e), None)
        if u_end is not None:
            _mark(base + pos, base + u_end)
            pos = u_end
            continue
        p_end = next((e for s, e in punct if s == pos), None)
        if p_end is not None:
            _mark(base + pos, base + p_end, "i")
            pos = p_end
            continue
        seg_text = body[pos:]
        vw = next((w for w in _VAGUE_WORDS if seg_text.startswith(w)), None)
        if vw:
            c["extensions"].setdefault("time_constraints", []).append(
                {"kind": "DEADLINE", "value": None, "unit": None,
                 "applies_to": "response", "source_expression": vw})
            i = len(c["extensions"]["time_constraints"]) - 1
            set_slot(c, f"/extensions/time_constraints/{i}/value", "unknown",
                     confirmation_required=True)
            _mark(base + pos, base + pos + len(vw))
            pos += len(vw)
            continue
        hit = match_jp_prefix(seg_text)
        if hit:
            surface, tid, ttype = hit
            after = seg_text[len(surface):]
            pm = re.match(r"^(を|に|へ|から|で)", after)
            if pm:
                particle = pm.group(1)
                method = ("exact_term_match"
                          if surface == term_ids()[tid]["preferred_japanese"]
                          else "synonym_match")
                if particle == "を":
                    resp["theme"] = tid
                    set_slot(c, "/rimay_core/response/theme", "proposed", surface,
                             method=method)
                elif particle in ("に", "へ"):
                    resp["destination"] = tid
                    set_slot(c, "/rimay_core/response/destination", "proposed", surface,
                             method=method,
                             confirmation_required=(ttype not in _CONCRETE_DEST_TYPES))
                elif particle == "から":
                    resp["source"] = tid
                    set_slot(c, "/rimay_core/response/source", "proposed", surface,
                             method=method)
                _mark(base + pos, base + pos + len(surface) + len(particle))
                pos += len(surface) + len(particle)
                continue
        # 未知語: 形態素境界まで送る（値を創作しない。unconsumedのまま残す）
        nxt = next((b for b in bounds if b > pos), pos + 1)
        pos = nxt

    # 述語 → Action family（P2-3/4: 辞書形句で照合。活用形を同一候補へ）
    def _families(unit):
        pred = unit["predicate"]
        fams = _VERB_CANDIDATES.get(pred)
        if fams is None and pred.endswith("する"):
            fams = _VERB_CANDIDATES.get(pred[:-2])
        return list(fams) if fams else []

    if len(units) == 0:
        resp["action"] = {"family": None, "rimay_action_id": None}
        set_slot(c, "/rimay_core/response/action/family", "unknown",
                 confirmation_required=True)
        set_slot(c, "/rimay_core/response/action/rimay_action_id", "unknown")
    elif len(units) == 1:
        u = units[0]
        fams = _families(u)
        if u["negated"]:
            c["extensions"].setdefault("additional_semantics", []).append(
                {"kind": "negated_predicate", "predicate": u["predicate"],
                 "surface": u["surface"]})
        if len(fams) == 1 and not u["negated"]:
            fam = fams[0]
            frame = case_frames().get(fam)
            resp["action"] = {"family": fam, "rimay_action_id": None}
            set_slot(c, "/rimay_core/response/action/family", "proposed",
                     u["predicate"], method="heuristic_candidate")
            set_slot(c, "/rimay_core/response/action/rimay_action_id", "unknown")
            if frame:
                from rimay_jp_core.validator import _ROLE_FIELD
                for role in frame["required_roles"]:
                    field = _ROLE_FIELD.get(role)
                    if field and field != "actor" and not resp.get(field):
                        set_slot(c, f"/rimay_core/response/{field}", "unknown",
                                 confirmation_required=True)
        elif fams:
            resp["action"] = {"family": fams[0] if len(fams) == 1 else None,
                              "rimay_action_id": None}
            set_slot(c, "/rimay_core/response/action/family", "proposed",
                     u["predicate"], method="heuristic_candidate",
                     confirmation_required=True,
                     candidates=[{"value": f} for f in fams])
            set_slot(c, "/rimay_core/response/action/rimay_action_id", "unknown")
        else:
            resp["action"] = {"family": None, "rimay_action_id": None}
            set_slot(c, "/rimay_core/response/action/family", "unknown",
                     confirmation_required=True)
            set_slot(c, "/rimay_core/response/action/rimay_action_id", "unknown")
    else:
        # 複数述語（P2-5）: 単一Actionへ誤集約しない・confirmedにしない。
        # 全述語を候補集合として保持し、Split Proposal判断の材料を残す（D5-5）。
        all_fams = sorted({f for u in units for f in _families(u)})
        resp["action"] = {"family": None, "rimay_action_id": None}
        set_slot(c, "/rimay_core/response/action/family", "unknown",
                 confirmation_required=True,
                 candidates=[{"value": f} for f in all_fams] or None)
        set_slot(c, "/rimay_core/response/action/rimay_action_id", "unknown")
        c["extensions"].setdefault("additional_semantics", []).append(
            {"kind": "multiple_predicates",
             "predicates": [{"predicate": u["predicate"],
                             "negated": u["negated"],
                             "families": _families(u)} for u in units]})

    attach_normalization(c, "heuristic", src, flags=flags)
    meta = sp.metadata()
    meta.update({"phrase_split_mode": "C",
                 "boundary_validation_split_mode": "C",
                 "scope": "heuristic_body"})
    c["normalization"]["lexical_analysis"] = meta
    return c
