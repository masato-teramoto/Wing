"""辞書・格フレーム・findingカタログのローダ（SSOT: lexicon/ と canonical/）。"""
import re
from functools import lru_cache
from pathlib import Path

import yaml

from .vocabulary import (
    active_vocabulary_context,
    effective_terms,
    organization_terms,
    project_terms,
)

ROOT = Path(__file__).resolve().parents[2]  # prototype/rimay-jp


def _load(rel: str):
    with open(ROOT / rel, encoding="utf-8") as f:
        return yaml.safe_load(f)


# --- Vocabulary Snapshot（ADR-0014 D5: IDをcacheキーに読み込む。
#     cache_clearは最適化であり整合性保証に使わない） ---

BOOTSTRAP_SNAPSHOT = "VOC-BOOTSTRAP"  # 移行期: lexicon/terms.yamlを暗黙Snapshotとする


def current_snapshot_id(base: Path | None = None) -> str:
    """current.jsonが指すSnapshot ID。未公開環境はbootstrap。"""
    import json
    p = (base or ROOT / "lexicon") / "snapshots" / "current.json"
    if p.exists():
        return json.loads(p.read_text(encoding="utf-8"))["snapshot_id"]
    return BOOTSTRAP_SNAPSHOT


@lru_cache(maxsize=16)
def load_vocabulary(snapshot_id: str, base: Path | None = None) -> tuple:
    """Snapshot IDをキーとするimmutableな用語リスト（tupleで凍結）。"""
    root = base or ROOT / "lexicon"
    if snapshot_id == BOOTSTRAP_SNAPSHOT:
        path = ROOT / "lexicon" / "terms.yaml"
    else:
        path = root / "snapshots" / snapshot_id / "terms.yaml"
    with open(path, encoding="utf-8") as f:
        doc = yaml.safe_load(f)
    # 旧Snapshotはtermごとのscopeを持たないためread互換を維持する。
    # 新しい案件別経路はvocabulary._read_terms_fileでscopeなしを拒否する。
    scope = doc.get("scope")
    return tuple({**t, **({"scope": scope} if scope and not t.get("scope") else {})}
                 for t in doc["terms"])


def vocabulary_content_hash(snapshot_id: str | None = None,
                            base: Path | None = None) -> str:
    import hashlib
    root = base or ROOT / "lexicon"
    sid = snapshot_id or current_snapshot_id(base)
    path = (ROOT / "lexicon" / "terms.yaml" if sid == BOOTSTRAP_SNAPSHOT
            else root / "snapshots" / sid / "terms.yaml")
    return "sha256:" + hashlib.sha256(path.read_bytes()).hexdigest()


@lru_cache(maxsize=1)
def _legacy_terms():
    """正規化・検証への語彙供給（ADR-0014 D5: current Snapshotをプロセス開始時に
    解決。未公開環境はbootstrap=lexicon/terms.yaml）。公開後の同一プロセス反映は
    publish操作のcache_clear（最適化）が行い、正しさはSnapshot ID指定の
    load_vocabularyが担う。"""
    return tuple(load_vocabulary(current_snapshot_id()))


def terms(context=None):
    """操作にpinされた案件＋組織語彙、または旧単一Snapshotを返す。"""
    ctx = context or active_vocabulary_context()
    if ctx is not None:
        return list(effective_terms(ctx))
    return list(_legacy_terms())


@lru_cache(maxsize=64)
def _context_jp_index(context):
    # project側に候補（廃止・homonymを含む）が存在する表層はorgへfallbackしない。
    project = project_terms(context)
    organization = organization_terms(context)
    blocked = {
        surface
        for term in project
        for surface in [term["preferred_japanese"], *(term.get("synonyms") or [])]
    }
    idx = build_jp_index(project)
    for surface, hit in build_jp_index(organization).items():
        if surface not in blocked:
            idx[surface] = hit
    return dict(sorted(idx.items(), key=lambda kv: -len(kv[0])))


@lru_cache(maxsize=1)
def _legacy_jp_index():
    return build_jp_index(_legacy_terms())


def jp_index(context=None):
    """日本語表層 → (term_id, type)。最長一致用に長さ降順で返す。

    ADR-0014 D3: 同一表層の重複登録は起動時拒否（fail-closed）。無言の後勝ち
    上書きで同表記異義が黙って解決されることを構造的に排除する。homonymの
    宣言・多値解決はResolver多値化（P0-3）で導入し、それまで重複は登録不可。
    """
    ctx = context or active_vocabulary_context()
    return _context_jp_index(ctx) if ctx is not None else _legacy_jp_index()


def build_jp_index(term_list) -> dict:
    """表層索引の構築（Loader gate込み。Snapshot公開時の検査でも使用）。

    - homonym: true 宣言のエントリは索引から除外（自動confirm不可。
      解決はResolver多値経路でAMBIGUOUS_TERM質問になる）。
    - status: deprecated のエントリも索引から除外（正規化に使わせない）。
    """
    idx = {}
    for t in term_list:
        if t.get("homonym") or t.get("status") in ("deprecated", "superseded"):
            continue
        names = [t["preferred_japanese"]] + list(t.get("synonyms") or [])
        for n in names:
            if n in idx and idx[n][0] != t["id"]:
                raise ValueError(
                    f"用語表層の重複登録: 「{n}」が {idx[n][0]} と {t['id']} の"
                    "両方に属する（ADR-0014 D3: homonym宣言なき重複は起動時拒否）")
            idx[n] = (t["id"], t["type"])
    return dict(sorted(idx.items(), key=lambda kv: -len(kv[0])))


@lru_cache(maxsize=64)
def _context_term_ids(context):
    # Canonicalの裸ID互換期間はproject-firstで1件へ射影する。API/provenanceは
    # qualified_idを使い、同一性を失わない。
    out = {t["id"]: t for t in organization_terms(context)}
    out.update({t["id"]: t for t in project_terms(context)})
    return out


@lru_cache(maxsize=1)
def _legacy_term_ids():
    return {t["id"]: t for t in _legacy_terms()}


def term_ids(context=None):
    ctx = context or active_vocabulary_context()
    return _context_term_ids(ctx) if ctx is not None else _legacy_term_ids()


def _clear_vocabulary_caches():
    _legacy_terms.cache_clear()
    _legacy_jp_index.cache_clear()
    _legacy_term_ids.cache_clear()
    _context_jp_index.cache_clear()
    _context_term_ids.cache_clear()


# 既存publish呼出しのcache_clear契約を維持する。
terms.cache_clear = _clear_vocabulary_caches
jp_index.cache_clear = _clear_vocabulary_caches
term_ids.cache_clear = _clear_vocabulary_caches


@lru_cache(maxsize=1)
def case_frames():
    frames = _load("lexicon/case-frames.yaml")["case_frames"]
    return {f["family"]: f for f in frames}


@lru_cache(maxsize=1)
def finding_catalog():
    cat = _load("canonical/finding-code-catalog.yaml")["codes"]
    return {c["code"]: c for c in cat}


@lru_cache(maxsize=1)
def knowledge_bank():
    """業務ルール・状態モデル（domain-reference-adapter用）。"""
    return _load("lexicon/business-rules.yaml")


# Role名 → Canonical応答フィールド名（正本。validator._ROLE_FIELDは本定義の別名）
ROLE_FIELD = {
    "agent": "actor", "theme": "theme", "destination": "destination",
    "source": "source", "location": "location", "property": "property",
    "result_value": "result_value", "rule": "rule", "input": "input",
    "result": "result", "content": "content",
    "display_location": "display_location", "channel": "channel",
}


@lru_cache(maxsize=1)
def profile_content_hash() -> str:
    """Profile SSOT（supported-profile.yaml＋case-frames.yaml）の内容hash
    （ADR-0013 D3: 宣言ドリフトの機械検出。版数と併記する）。"""
    import hashlib
    h = hashlib.sha256()
    # C4: English conformance profileを母集合へ追加（主計画§20.2。grammar実行契約と統合）
    for rel in ("profile/supported-profile.yaml", "lexicon/case-frames.yaml",
                "profile/english-rimay-conformance.yaml"):
        h.update((ROOT / rel).read_bytes())
    return "sha256:" + h.hexdigest()


@lru_cache(maxsize=1)
def normalizer_profile() -> dict:
    """Normalizer ProfileをSSOTからコンパイルする（ADR-0013 D3）。

    Pythonコード側には汎用アルゴリズム（最長一致・走査・正規表現実行・
    Canonical書き込み）だけを残し、表層知識はここで一元供給する。
    - japanese_surface（supported-profile.yaml）: 条件終端・トリガー動詞・
      モダリティ・曖昧語・指示語・定量パターン
    - role_by_particle: case-frames.yaml の japanese_case_mapping から導出
      （family × 格助詞 → 応答フィールド。'は'=agentは主体解析側で扱うため除外）
    - response_verb_stems: 各frameの japanese_canonical_verb から導出
    """
    js = _load("profile/supported-profile.yaml")["japanese_surface"]
    role_by_particle: dict[str, dict[str, str]] = {}
    response_verb_stems: dict[str, str] = {}
    for fam, frame in case_frames().items():
        mapping = {}
        for role, particle in (frame.get("japanese_case_mapping") or {}).items():
            if particle == "は":
                continue
            mapping[particle] = ROLE_FIELD.get(role, role)
        role_by_particle[fam] = mapping
        verb = frame.get("japanese_canonical_verb") or ""
        stem = verb[:-2] if verb.endswith("する") else verb
        if stem:
            response_verb_stems[stem] = fam
    particles = sorted({p for m in role_by_particle.values() for p in m},
                       key=len, reverse=True)
    return {
        "condition_terminals": [(e["surface"], e["type"])
                                for e in js["condition_terminals"]],
        "comparison_operator_surfaces": dict(js["comparison_operator_surfaces"]),
        "multi_value_connectors": dict(js["multi_value_connectors"]),
        "operator_operand_surfaces": dict(js["operator_operand_surfaces"]),
        "trigger_verb_stems": dict(js["trigger_verb_stems"]),
        "modality_endings": [(e["surface"], e["modality"])
                             for e in js["modality_endings"]],
        "vague_words": list(js["vague_words"]),
        "action_expressions": {k: list(v) for k, v in
                               (js.get("action_expressions") or {}).items()},
        "deictic_words": list(js["deictic_words"]),
        "deadline_pattern": js["quantitative_patterns"]["deadline"],
        "retention_pattern": js["quantitative_patterns"]["retention"],
        "role_by_particle": role_by_particle,
        "response_verb_stems": response_verb_stems,
        "particle_alternation": "|".join(re.escape(p) for p in particles),
    }


@lru_cache(maxsize=1)
def versions():
    """知識源の版数（Provenance記録用）。"""
    out = {
        "term_dictionary": _load("lexicon/terms.yaml").get("lexicon_version", "0.0.0"),
        "action_frame": _load("lexicon/case-frames.yaml").get("frame_set_version", "0.0.0"),
        "domain_knowledge": knowledge_bank().get("knowledge_version", "0.0.0"),
        "profile_content_hash": profile_content_hash(),
        # ADR-0014 D5: 語彙はSnapshot IDと実体hashで固定（STALE判定の依存）
        "vocabulary_snapshot_id": current_snapshot_id(),
        "vocabulary_content_hash": vocabulary_content_hash(),
    }
    context = active_vocabulary_context()
    if context is not None:
        out["vocabulary_snapshot_id"] = context.project.snapshot_id
        out["vocabulary_content_hash"] = context.project.content_hash
        out["vocabulary_context"] = context.public()
    return out


def lookup_jp(surface: str):
    """完全一致の用語解決。(id, type) または None。"""
    return jp_index().get(surface)


def match_jp_prefix(text: str):
    """先頭からの最長一致。(surface, id, type) または None。"""
    for name, (tid, ttype) in jp_index().items():
        if text.startswith(name):
            return name, tid, ttype
    return None


_CAMEL = re.compile(r"(?<=[a-z0-9])(?=[A-Z])|(?<=[A-Z])(?=[A-Z][a-z])")


def en_label(term_id: str) -> str:
    """内部ID → 英語表示ラベル（CamelCase分割）。InvoicePDF -> 'Invoice PDF'"""
    return _CAMEL.sub(" ", term_id)


def resolve_en(name: str):
    """英語表層（引用符内ラベルまたは裸ID）→ term_id。未登録はNone。"""
    ids = term_ids()
    if name in ids:
        return name
    compact = name.replace(" ", "").replace(",", "")
    return compact if compact in ids else None
