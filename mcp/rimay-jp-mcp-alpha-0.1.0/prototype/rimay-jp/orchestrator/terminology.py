"""語彙発見・承認ループの中核（ADR-0014 P0-2/3/4の実装）。

- 検出は純粋（D2）: Normalizer/ExtractorはfindingのevidenceにObservationを載せる
  だけで書き込まない。永続化は本モジュールの明示操作のみ。
- Occurrenceは不変イベント（D1）。解決状況はResolutionレコードが別管理。
- 候補語はNormalizer/Resolverの正規化解決に使えない（Gate 2）。
- 公開はReceipt必須（Gate 5）・Immutable Snapshot（D5）。伝播Sagaは operations に
  記録する（本ファイルでは骨格まで。impact計画の全面実装はP0-6/7）。
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

import yaml
from jsonschema import Draft202012Validator

from . import _ROOT  # noqa: F401
from rimay_jp_core.lexicon import (  # noqa: E402
    ROOT as CORE_ROOT, build_jp_index, load_vocabulary, lookup_jp)
from rimay_jp_core.vocabulary import (  # noqa: E402
    VocabularyContext,
    VocabularyRegistry,
    assert_project_owner,
    effective_terms,
    organization_terms,
    project_terms,
    qualified_term_id,
    write_snapshot_artifact,
)

_SCHEMA_DIR = CORE_ROOT / "canonical"
_TERM_TYPES = ("actor", "class", "property", "value", "function", "rule")


def _schema(name: str) -> Draft202012Validator:
    with open(_SCHEMA_DIR / name, encoding="utf-8") as f:
        return Draft202012Validator(json.load(f))


def _sha8(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()[:8]


# --- D2: findingsからの構造化Observation抽出（メッセージ解析禁止） ---

def observations_from(findings: list[dict], source_text: str = "") -> list[dict]:
    """JP-LEXICAL findingの構造化evidenceからObservationを組み立てる。

    kind=action_expression（D6: Action表現はTerm Candidateにしない）と
    kind=unparsed（残句）は除外する。spanはsource_textの最初の出現位置。
    """
    obs = []
    for f in findings:
        if f.get("code") != "JP-LEXICAL":
            continue
        ev = f.get("evidence") or {}
        if not ev.get("surface_form") or ev.get("kind") in (
                "action_expression", "unparsed"):
            continue
        o = {"surface_form": ev["surface_form"],
             "expected_types": list(ev.get("expected_types") or []),
             "target_path": f.get("path")}
        pos = source_text.find(ev["surface_form"]) if source_text else -1
        if pos >= 0:
            o["source_span"] = {"start": pos, "end": pos + len(ev["surface_form"])}
        obs.append(o)
    return obs


# --- D3: Resolver多値化 ---

def candidate_summary(store: "TerminologyStore") -> list[dict]:
    """対話・文書横断の候補集約ビュー（ADR-0014 P1。読み取りのみ）。

    候補は表層ごとに1件へ集約済み（ensure_candidateの自然キー）なので、
    ここでは出現の広がり（文書・要求・経路）を可視化する。
    """
    occ = {o["occurrence_id"]: o for o in store.occurrences()}
    out = []
    for c in store.candidates():
        os_ = [occ[i] for i in c["occurrence_refs"] if i in occ]
        out.append({
            "candidate_id": c["candidate_id"],
            "surface_form": c["surface_form"], "status": c["status"],
            "occurrences": len(os_),
            "documents": sorted({o["source"]["document_id"] for o in os_}),
            "requirements": sorted(
                {(o.get("requirement_ref") or {}).get("requirement_id")
                 for o in os_ if o.get("requirement_ref")}),
            "channels": sorted({o["channel"] for o in os_})})
    return out


def promotion_candidates(project_vocabs: dict) -> list[dict]:
    """組織共通語彙への昇格候補（ADR-0014 P1。advisory・昇格判断は人間）。

    条件（terminology-lifecycle.yaml promotion参照）: 2案件以上で使用・
    定義（type＋definition）が競合しない。昇格の実行は既存の変更公開経路
    （候補→承認→Snapshot公開でscopeをorg:commonへ）を使う。
    """
    seen: dict = {}
    for proj, vocab in project_vocabs.items():
        for t in vocab:
            if str(t.get("scope") or "").startswith("org:"):
                continue
            if t.get("scope") != f"project:{proj}":
                raise ValueError(
                    f"promotion source scope mismatch: {proj}/{t.get('id')}")
            seen.setdefault(t["preferred_japanese"], []).append((proj, t))
    out = []
    for surface, uses in sorted(seen.items()):
        projects = sorted({p for p, _ in uses})
        if len(projects) < 2:
            continue
        defs = {json.dumps({"type": t.get("type"),
                            "definition": t.get("definition")},
                           ensure_ascii=False, sort_keys=True)
                for _, t in uses}
        provenance_complete = all(bool(t.get("provenance")) for _, t in uses)
        definition_complete = all(bool(t.get("definition")) for _, t in uses)
        out.append({"surface_form": surface, "projects": projects,
                    "term_ids": sorted({
                        t.get("qualified_id") or qualified_term_id(t["scope"], t["id"])
                        for _, t in uses}),
                    "definition_conflict": len(defs) > 1,
                    "definition_complete": definition_complete,
                    "provenance_complete": provenance_complete,
                    "eligible": (len(defs) == 1 and definition_complete and
                                 provenance_complete)})
    return out


def resolve_surface(surface: str, vocab=None, scope: str | None = None) -> dict:
    """表層→Resolution判定。単一値lookupではなく多値の判定結果を返す。

    kind: exact | synonym | ambiguous | not_found | deprecated
    """
    term_list = vocab if vocab is not None else load_vocabulary(
        __import__("rimay_jp_core.lexicon", fromlist=["current_snapshot_id"])
        .current_snapshot_id())
    matches = []
    for t in term_list:
        qid = (t.get("qualified_id") or
               (qualified_term_id(t["scope"], t["id"]) if t.get("scope") else t["id"]))
        if t["preferred_japanese"] == surface:
            matches.append({"term_id": t["id"], "qualified_term_id": qid,
                            "via": "exact",
                            "scope": t.get("scope"), "status": t.get("status"),
                            "superseded_by": t.get("superseded_by")})
        elif surface in (t.get("synonyms") or []):
            matches.append({"term_id": t["id"], "qualified_term_id": qid,
                            "via": "synonym",
                            "scope": t.get("scope"), "status": t.get("status"),
                            "superseded_by": t.get("superseded_by")})
    if not matches:
        return {"kind": "not_found", "matches": []}
    active = [m for m in matches if m.get("status") not in ("deprecated", "superseded")]
    if not active:
        return {"kind": "deprecated", "matches": matches}
    if len({m["qualified_term_id"] for m in active}) > 1:
        # 名前空間解決（P1）: 呼出し文脈のscopeで一意になるならambiguousにしない
        if scope:
            scoped = [m for m in active if m.get("scope") == scope]
            if len({m["qualified_term_id"] for m in scoped}) == 1:
                return {"kind": scoped[0]["via"], "matches": scoped,
                        "scope_filtered": True}
        return {"kind": "ambiguous", "matches": active}
    m = active[0]
    return {"kind": m["via"], "matches": [m]}


def resolve_surface_in_context(surface: str, context: VocabularyContext) -> dict:
    """案件優先、候補なしの場合だけ組織へfallbackする決定論的Resolver。"""
    project = resolve_surface(surface, vocab=project_terms(context),
                              scope=context.project.scope)
    if project["kind"] != "not_found":
        project["matches"] = [
            {**match, "local_term_id": match["term_id"],
             "term_id": match["qualified_term_id"]}
            for match in project["matches"]]
        return {**project, "resolved_scope": context.project.scope,
                "fallback": False, "vocabulary_context": context.public()}
    organization = resolve_surface(surface, vocab=organization_terms(context),
                                   scope=context.organization.scope)
    organization["matches"] = [
        {**match, "local_term_id": match["term_id"],
         "term_id": match["qualified_term_id"]}
        for match in organization["matches"]]
    return {**organization,
            "resolved_scope": (context.organization.scope
                               if organization["kind"] != "not_found" else None),
            "fallback": organization["kind"] != "not_found",
            "vocabulary_context": context.public()}


# --- P0-2: ストア（候補と公開済みの分離） ---

class TerminologyStore:
    """terminology/ 配下の永続化。書き込みはすべて明示操作・検証付き。"""

    def __init__(self, root: Path, project_id: str | None = None):
        self.root = Path(root)
        self.project_id = project_id
        for d in ("candidates", "receipts", "operations"):
            (self.root / d).mkdir(parents=True, exist_ok=True)
        self._occ_schema = _schema("term-occurrence.schema.json")
        self._cand_schema = _schema("term-candidate.schema.json")

    # -- Occurrence（不変イベント・追記のみ・自然キーでidempotent） --

    def _occ_path(self) -> Path:
        return self.root / "occurrences.jsonl"

    def occurrences(self) -> list[dict]:
        p = self._occ_path()
        if not p.exists():
            return []
        values = [json.loads(ln) for ln in
                  p.read_text(encoding="utf-8").splitlines() if ln.strip()]
        if self.project_id is not None:
            for value in values:
                assert_project_owner(value, self.project_id)
        return values

    def observe(self, observation: dict, *, document_id: str,
                requirement_id: str, channel: str, observed_at: str) -> dict:
        """Observation→Occurrence永続化（明示操作。同一自然キーは再利用）。"""
        key = f"{observation['surface_form']}|{requirement_id}|" \
              f"{observation.get('target_path')}"
        oid = f"TO-{_sha8(key)}"
        for existing in self.occurrences():
            if existing["occurrence_id"] == oid:
                return existing
        occ = {"occurrence_id": oid,
               "surface_form": observation["surface_form"],
               "observed_at": observed_at,
               "channel": channel,
               "source": {"document_id": document_id},
               "expected_types": list(observation.get("expected_types") or [])}
        if self.project_id is not None:
            occ["project_id"] = self.project_id
        if observation.get("source_span"):
            occ["source"]["span"] = observation["source_span"]
        if observation.get("target_path"):
            occ["requirement_ref"] = {"requirement_id": requirement_id,
                                      "target_path": observation["target_path"]}
        errors = sorted(self._occ_schema.iter_errors(occ), key=str)
        if errors:
            raise ValueError(f"Occurrence schema violation: {errors[0].message}")
        with open(self._occ_path(), "a", encoding="utf-8") as f:
            f.write(json.dumps(occ, ensure_ascii=False) + "\n")
        return occ

    # -- Resolution（Occurrenceと分離。D1） --

    def _res_path(self) -> Path:
        return self.root / "resolutions.jsonl"

    def resolutions(self) -> dict:
        p = self._res_path()
        out = {}
        if p.exists():
            for ln in p.read_text(encoding="utf-8").splitlines():
                if ln.strip():
                    r = json.loads(ln)
                    if self.project_id is not None:
                        assert_project_owner(r, self.project_id)
                    out[r["occurrence_id"]] = r  # 後勝ち=最新状態
        return out

    def record_resolution(self, occurrence_id: str, status: str,
                          resolved_term_id: str | None = None,
                          snapshot_id: str | None = None,
                          resolved_at: str | None = None) -> dict:
        rec = {"occurrence_id": occurrence_id, "status": status}
        if self.project_id is not None:
            occurrence = next(
                (o for o in self.occurrences() if o["occurrence_id"] == occurrence_id),
                None)
            if occurrence is None:
                raise ValueError(f"unknown occurrence: {occurrence_id}")
            rec["project_id"] = self.project_id
        if resolved_term_id:
            rec["resolved_term_id"] = resolved_term_id
        if snapshot_id:
            rec["snapshot_id"] = snapshot_id
        if resolved_at:
            rec["resolved_at"] = resolved_at
        with open(self._res_path(), "a", encoding="utf-8") as f:
            f.write(json.dumps(rec, ensure_ascii=False) + "\n")
        return rec

    def unresolved_surfaces(self) -> dict:
        """surface → [occurrence]（未解決のみ。D5影響分類のre-resolve逆引き）。"""
        res = self.resolutions()
        out: dict = {}
        for occ in self.occurrences():
            r = res.get(occ["occurrence_id"])
            if r is None or r["status"] == "unresolved":
                out.setdefault(occ["surface_form"], []).append(occ)
        return out

    # -- Candidate（revision楽観ロック） --

    def _cand_path(self, cid: str) -> Path:
        return self.root / "candidates" / f"{cid}.json"

    def candidate(self, cid: str) -> dict | None:
        p = self._cand_path(cid)
        value = json.loads(p.read_text(encoding="utf-8")) if p.exists() else None
        if value is not None and self.project_id is not None:
            assert_project_owner(value, self.project_id)
        return value

    def candidates(self) -> list[dict]:
        values = [json.loads(p.read_text(encoding="utf-8"))
                  for p in sorted((self.root / "candidates").glob("TC-*.json"))]
        if self.project_id is not None:
            for value in values:
                assert_project_owner(value, self.project_id)
        return values

    def _write_candidate(self, cand: dict):
        errors = sorted(self._cand_schema.iter_errors(cand), key=str)
        if errors:
            raise ValueError(f"Candidate schema violation: {errors[0].message}")
        self._cand_path(cand["candidate_id"]).write_text(
            json.dumps(cand, ensure_ascii=False, indent=1), encoding="utf-8")

    def ensure_candidate(self, occurrence: dict) -> dict:
        """同一表層は1候補（idempotent）。occurrence_refを重複なく追記。"""
        cid = f"TC-{_sha8(occurrence['surface_form'])}"
        cand = self.candidate(cid)
        if cand is None:
            cand = {"candidate_id": cid,
                    "surface_form": occurrence["surface_form"],
                    "status": "open", "revision": 1,
                    "occurrence_refs": [occurrence["occurrence_id"]]}
            if self.project_id is not None:
                assert_project_owner(occurrence, self.project_id)
                cand["project_id"] = self.project_id
        elif occurrence["occurrence_id"] not in cand["occurrence_refs"]:
            cand["occurrence_refs"].append(occurrence["occurrence_id"])
            cand["revision"] += 1
        self._write_candidate(cand)
        return cand

    def update_candidate(self, cid: str, base_revision: int, patch: dict) -> dict:
        cand = self.candidate(cid)
        if cand is None:
            raise ValueError(f"unknown candidate: {cid}")
        if cand["revision"] != base_revision:
            raise ValueError(f"revision conflict: {cid} "
                             f"base={base_revision} current={cand['revision']}")
        allowed = {"proposed_term", "evidence", "status", "review"}
        bad = set(patch) - allowed
        if bad:
            raise ValueError(f"patch not allowed for fields: {sorted(bad)}")
        if self.project_id is not None and patch.get("proposed_term"):
            scope = patch["proposed_term"].get("scope")
            if scope != f"project:{self.project_id}":
                raise ValueError(
                    f"proposed term scope must be project:{self.project_id}")
        cand.update(patch)
        cand["revision"] += 1
        self._write_candidate(cand)
        return cand

    # -- 承認Receipt（D4。承認は人間のみ・Receiptと同時発行） --

    def approve(self, cid: str, base_revision: int, *, reviewer: str,
                approved_at: str, decision_reason: str = "") -> dict:
        cand = self.candidate(cid)
        if cand is None:
            raise ValueError(f"unknown candidate: {cid}")
        if cand["revision"] != base_revision:
            raise ValueError(f"revision conflict: {cid}")
        if cand["status"] != "under_review":
            raise ValueError(f"approve requires under_review: {cand['status']}")
        if not cand.get("proposed_term"):
            raise ValueError("approve requires proposed_term")
        receipt = {"receipt_id": f"APR-TERM-{cid[3:]}",
                   "candidate_id": cid,
                   "approved_by": reviewer,
                   "approved_at": approved_at,
                   "resulting_term_id": cand["proposed_term"]["id"],
                   "bundled_evidence": list(cand.get("evidence") or [])}
        if self.project_id is not None:
            receipt["project_id"] = self.project_id
        (self.root / "receipts" / f"{receipt['receipt_id']}.json").write_text(
            json.dumps(receipt, ensure_ascii=False, indent=1), encoding="utf-8")
        cand.update({"status": "approved", "receipt_id": receipt["receipt_id"],
                     "review": {"reviewer": reviewer, "decided_at": approved_at,
                                "decision_reason": decision_reason}})
        cand["revision"] += 1
        self._write_candidate(cand)
        return receipt

    def receipt(self, receipt_id: str) -> dict | None:
        p = self.root / "receipts" / f"{receipt_id}.json"
        return json.loads(p.read_text(encoding="utf-8")) if p.exists() else None

    # -- Snapshot公開（D5: immutable・Receipt必須=Gate 5・重複はLoader gate） --

    def publish_snapshot(self, snapshot_id: str, *, lexicon_base: Path,
                         base_vocab, candidate_ids: list[str],
                         operation_id: str, published_at: str,
                         requirement_term_index: dict | None = None,
                         scope: str | None = None) -> dict:
        """承認済み候補をimmutable Snapshotとして公開し、影響計画を起票する。

        - 候補のproposed_term.idが既存IDなら**変更公開**（置換）。新規なら追加。
        - 影響分類（ADR-0014 D5/Gate 6）: 新規/同義語=re-resolve、type変更=
          re-validate、定義・scope等=re-review、廃止・統合=stale、
          同表層homonym追加=過去解決要求のre-review候補。
        - requirement_term_index（{requirement_id: [term_id]}）は変更系の
          逆引き補完。未提供時はループ経由のResolution記録のみで逆引きする
          （op.index_providedへ記録＝網羅範囲を隠さない）。
        """
        pub_keys = ("preferred_japanese", "type", "synonyms", "definition",
                    "scope", "status", "superseded_by", "homonym")
        new_terms = []
        receipts = {}
        for cid in candidate_ids:
            cand = self.candidate(cid)
            if cand is None or cand["status"] != "approved":
                raise ValueError(f"publish requires approved candidate: {cid}")
            if not cand.get("receipt_id") or not self.receipt(cand["receipt_id"]):
                raise ValueError(f"publish requires approval receipt: {cid}")
            t = dict(cand["proposed_term"])
            if scope is not None and t.get("scope") != scope:
                raise ValueError(
                    f"publish scope mismatch: expected {scope}, got {t.get('scope')}")
            entry = {"id": t["id"],
                     **{k: t[k] for k in pub_keys if t.get(k) is not None}}
            entry.setdefault("synonyms", [])
            new_terms.append(entry)
            receipts[t["id"]] = cand["receipt_id"]
        merged_map = {t["id"]: dict(t) for t in base_vocab}
        appended = [t for t in new_terms if t["id"] not in merged_map]
        for t in new_terms:
            merged_map[t["id"]] = t
        merged = [merged_map[t["id"]] for t in base_vocab] + appended
        build_jp_index(merged)  # Loader gate: homonym宣言なき重複は公開拒否
        if scope is None:  # 0.1.x read/write互換。案件別公開は下の1.0契約だけを使う。
            snap_dir = Path(lexicon_base) / "snapshots" / snapshot_id
            if snap_dir.exists():
                raise ValueError(f"snapshot already exists (immutable): {snapshot_id}")
            snap_dir.mkdir(parents=True)
            (snap_dir / "terms.yaml").write_text(
                yaml.safe_dump({"terms": merged}, allow_unicode=True,
                               sort_keys=False), encoding="utf-8")
            (Path(lexicon_base) / "snapshots" / "current.json").write_text(
                json.dumps({"snapshot_id": snapshot_id}), encoding="utf-8")
        else:
            write_snapshot_artifact(
                Path(lexicon_base), scope, snapshot_id, merged,
                published_at=published_at, operation_id=operation_id)
        # 影響計画（伝播SagaはP0-6のpropagateが実行）
        changes = classify_term_changes(base_vocab, merged)
        homonym_surfaces = changes.pop("__homonym_surfaces__")
        op = {"operation_id": operation_id, "snapshot_id": snapshot_id,
              "status": "propagating", "published_at": published_at,
              "added_term_ids": [t["id"] for t in appended],
              "term_changes": {k: v for k, v in changes.items()
                               if v != "re-resolve"},
              "homonym_surfaces": homonym_surfaces,
              "index_provided": requirement_term_index is not None,
              "affected_requirements": {}, "impact_kind": {}, "targets": {}}
        if self.project_id is not None:
            op["project_id"] = self.project_id
        if scope is not None:
            op["scope"] = scope
        _RANK = {"re-resolve": 0, "re-review": 1, "re-validate": 2, "stale": 3}

        def _mark(rid, kind, actionable=False):
            cur = op["impact_kind"].get(rid)
            if cur is None or _RANK[kind] > _RANK[cur]:
                op["impact_kind"][rid] = kind
            if actionable:
                op["affected_requirements"][rid] = "pending"
            else:
                op["affected_requirements"].setdefault(rid, "advisory")

        # (1) 新規Term/synonym → 同surfaceの未解決Occurrence保持要求をre-resolve
        for t in new_terms:
            if changes.get(t["id"]) != "re-resolve":
                continue
            surfaces = [t["preferred_japanese"]] + list(t.get("synonyms") or [])
            for surface, occs in self.unresolved_surfaces().items():
                if surface in surfaces:
                    for occ in occs:
                        ref = occ.get("requirement_ref") or {}
                        rid = ref.get("requirement_id")
                        if rid:
                            _mark(rid, "re-resolve", actionable=True)
                            op["targets"].setdefault(rid, []).append(
                                {"target_path": ref.get("target_path"),
                                 "term_id": t["id"],
                                 "occurrence_id": occ["occurrence_id"],
                                 "receipt_id": receipts[t["id"]]})
        # (2) 既存Termの変更 → term_id使用要求（index＋Resolution記録で逆引き）
        rid_terms: dict = {rid: set(tids)
                           for rid, tids in (requirement_term_index or {}).items()}
        res = self.resolutions()
        occ_by_id = {o["occurrence_id"]: o for o in self.occurrences()}
        for oid, r in res.items():
            if r["status"] == "resolved" and r.get("resolved_term_id"):
                ref = (occ_by_id.get(oid) or {}).get("requirement_ref") or {}
                if ref.get("requirement_id"):
                    rid_terms.setdefault(ref["requirement_id"],
                                         set()).add(r["resolved_term_id"])
        for tid, kind in changes.items():
            if kind == "re-resolve":
                continue
            for rid, tids in rid_terms.items():
                if tid in tids:
                    _mark(rid, kind)
        # (3) 同表層homonym追加 → その表層から過去解決した要求のre-review候補
        for oid, r in res.items():
            occ = occ_by_id.get(oid) or {}
            ref = occ.get("requirement_ref") or {}
            if r["status"] == "resolved" and ref.get("requirement_id") and \
                    occ.get("surface_form") in homonym_surfaces:
                _mark(ref["requirement_id"], "re-review")
        if not any(v in ("pending", "retry_required")
                   for v in op["affected_requirements"].values()):
            op["status"] = "completed"
        (self.root / "operations" / f"{operation_id}.json").write_text(
            json.dumps(op, ensure_ascii=False, indent=1), encoding="utf-8")
        return op

    def operation(self, operation_id: str) -> dict | None:
        p = self.root / "operations" / f"{operation_id}.json"
        return json.loads(p.read_text(encoding="utf-8")) if p.exists() else None

    def pending_requirements(self) -> set:
        """伝播未完了のRequirement（review_ready/approved進行の遮断対象）。"""
        out = set()
        for p in (self.root / "operations").glob("*.json"):
            op = json.loads(p.read_text(encoding="utf-8"))
            if op["status"] in ("planning", "propagating", "retry_required"):
                for rid, st in op["affected_requirements"].items():
                    if st in ("pending", "retry_required"):
                        out.add(rid)
        return out


def referenced_term_ids(canonical: dict, entries: dict) -> list[str]:
    """CanonicalのRimay Coreが参照する登録term IDの一覧。"""
    refs: set = set()

    def _walk(v):
        if isinstance(v, dict):
            for x in v.values():
                _walk(x)
        elif isinstance(v, list):
            for x in v:
                _walk(x)
        elif isinstance(v, str) and v in entries:
            refs.add(v)

    _walk(canonical.get("rimay_core") or {})
    return sorted(refs)


def term_fingerprint(canonical: dict, vocab) -> str:
    """要求が参照する用語の**実体指紋**（ADR-0014 Gate 6の「無関係は影響を受けない」）。

    指紋の基底 = 参照term IDごとの (エントリ内容, その全表層を共有するID集合)。
    - 無関係な新語追加では変わらない（Snapshot切替だけでSTALEにしない）
    - 参照termのtype/定義/scope/status変更・同表層homonym追加で変わる
    """
    entries = {}
    for term in vocab:
        # effective vocabはproject→org順。裸ID互換Canonicalはproject-firstで
        # 解釈し、fingerprint basis自体にはqualified IDを記録する。
        entries.setdefault(term["id"], term)
    surface_owners: dict = {}
    for t in vocab:
        qid = (t.get("qualified_id") or
               (qualified_term_id(t["scope"], t["id"]) if t.get("scope") else t["id"]))
        for s in [t["preferred_japanese"], *(t.get("synonyms") or [])]:
            surface_owners.setdefault(s, set()).add(qid)
    basis = []
    for tid in referenced_term_ids(canonical, entries):
        e = entries[tid]
        qid = (e.get("qualified_id") or
               (qualified_term_id(e["scope"], e["id"]) if e.get("scope") else tid))
        surfaces = [e["preferred_japanese"], *(e.get("synonyms") or [])]
        sharing = sorted(set().union(*(surface_owners[s] for s in surfaces)))
        basis.append([qid, json.dumps(e, sort_keys=True, ensure_ascii=False),
                      sharing])
    return "sha256:" + hashlib.sha256(
        json.dumps(basis, ensure_ascii=False).encode("utf-8")).hexdigest()


def classify_term_changes(base_vocab, merged_vocab) -> dict:
    """新旧語彙の差分→影響種別（ADR-0014 D5の4分類）。

    返り値: {term_id: kind}（新規はre-resolve、既存変更はstale/re-validate/
    re-review）＋ {"__homonym_surfaces__": [表層]}（同表層追加の再確認候補）。
    """
    old = {t["id"]: t for t in base_vocab}
    old_surfaces: dict = {}
    for t in base_vocab:
        for s in [t["preferred_japanese"], *(t.get("synonyms") or [])]:
            old_surfaces.setdefault(s, set()).add(t["id"])
    kinds: dict = {}
    homonym_surfaces: list = []
    for t in merged_vocab:
        tid = t["id"]
        prev = old.get(tid)
        if prev is None:
            kinds[tid] = "re-resolve"
            for s in [t["preferred_japanese"], *(t.get("synonyms") or [])]:
                if any(o != tid for o in old_surfaces.get(s, ())):
                    homonym_surfaces.append(s)
            continue
        if t == prev:
            continue
        if t.get("status") in ("deprecated", "superseded") and \
                prev.get("status") not in ("deprecated", "superseded"):
            kinds[tid] = "stale"
        elif t.get("type") != prev.get("type"):
            kinds[tid] = "re-validate"
        else:
            kinds[tid] = "re-review"
    out = dict(kinds)
    out["__homonym_surfaces__"] = sorted(set(homonym_surfaces))
    return out


def promote_to_org_common(
        registry: VocabularyRegistry, *, operation_id: str, org_term: dict,
        project_term_ids: dict[str, str], org_snapshot_id: str,
        project_snapshot_ids: dict[str, str], approved_by: str,
        approved_at: str, affected_requirements: dict[str, list[str]] | None = None
        ) -> dict:
    """組織公開＋案件supersessionを部分完了可視のSagaとして実行する。

    同一operationの再実行は完了stepを飛ばす。案件側の元TermやSnapshot IDが
    一時的に不足した場合は ``retry_required`` を永続化して戻り、元Snapshotを
    書き換えない。
    """
    if not operation_id or not approved_by or not approved_at:
        raise ValueError("promotion requires operation ID and human approval")
    if org_term.get("scope") != "org:common":
        raise ValueError("promoted organization term must have scope org:common")
    if len(project_term_ids) < 2:
        raise ValueError("promotion requires evidence from at least two projects")
    if set(project_term_ids) != set(project_snapshot_ids):
        raise ValueError("each promotion source project requires a target snapshot ID")

    request_basis = {
        "org_term": org_term,
        "project_term_ids": dict(sorted(project_term_ids.items())),
        "org_snapshot_id": org_snapshot_id,
        "project_snapshot_ids": dict(sorted(project_snapshot_ids.items())),
        "approved_by": approved_by,
        "approved_at": approved_at,
        "affected_requirements": affected_requirements or {},
    }
    request_hash = "sha256:" + hashlib.sha256(json.dumps(
        request_basis, ensure_ascii=False, sort_keys=True,
        separators=(",", ":")).encode("utf-8")).hexdigest()

    operation_root = registry.organization_root() / "terminology" / "operations"
    operation_path = operation_root / f"{operation_id}.json"
    if operation_path.exists():
        op = json.loads(operation_path.read_text(encoding="utf-8"))
        if op.get("operation_id") != operation_id or \
                op.get("request_hash") != request_hash:
            raise ValueError("promotion operation ID was reused for different content")
        if op.get("status") == "completed":
            return op
    else:
        requirements = {
            rid: "pending"
            for project_id in sorted(project_term_ids)
            for rid in (affected_requirements or {}).get(project_id, [])
        }
        op = {
            "operation_version": "1.0.0",
            "operation_id": operation_id,
            "request_hash": request_hash,
            "kind": "org_publish_project_supersession",
            "status": "propagating",
            "approved_by": approved_by,
            "approved_at": approved_at,
            "target_qualified_term_id": qualified_term_id(
                "org:common", org_term["id"]),
            "organization": {"snapshot_id": org_snapshot_id, "status": "pending"},
            "projects": {
                project_id: {
                    "source_term_id": term_id,
                    "snapshot_id": project_snapshot_ids[project_id],
                    "status": "pending",
                }
                for project_id, term_id in sorted(project_term_ids.items())
            },
            "affected_requirements": requirements,
        }

    def _persist():
        operation_root.mkdir(parents=True, exist_ok=True)
        payload = json.dumps(op, ensure_ascii=False, indent=2) + "\n"
        operation_path.write_text(payload, encoding="utf-8")
        # 各案件の承認ゲートも同じ部分完了を読めるようoperationを複製する。
        for project_id in project_term_ids:
            root = registry.terminology_root(project_id) / "operations"
            root.mkdir(parents=True, exist_ok=True)
            (root / f"{operation_id}.json").write_text(payload, encoding="utf-8")

    _persist()
    target_qid = op["target_qualified_term_id"]

    # eligibilityは公開前に全案件をpreflightする。機械判定は必要条件だけで、
    # approved_by/approved_atが人間裁定の境界を表す。
    source_bases: dict[str, list[dict]] = {}
    reference_shape = None
    for project_id, source_term_id in sorted(project_term_ids.items()):
        try:
            context = registry.resolve(project_id)
            base = list(project_terms(context))
            source = next((t for t in base if t["id"] == source_term_id), None)
            if source is None:
                raise ValueError(
                    f"promotion source term is missing: {project_id}/{source_term_id}")
            if not source.get("provenance"):
                raise ValueError(
                    f"promotion source provenance is missing: {project_id}/{source_term_id}")
            shape = (source.get("type"), source.get("definition"))
            if reference_shape is None:
                reference_shape = shape
            if shape != reference_shape or shape != (
                    org_term.get("type"), org_term.get("definition")):
                raise ValueError("promotion source definitions conflict")
            source_bases[project_id] = base
        except (OSError, ValueError, KeyError) as exc:
            op["projects"][project_id].update(
                {"status": "retry_required", "error": str(exc)})
            op["status"] = "retry_required"
            _persist()
            return op

    if op["organization"]["status"] != "completed":
        try:
            sample_project = next(iter(project_term_ids))
            org_context = registry.resolve(sample_project)
            org_base = list(organization_terms(org_context))
            org_map = {t["id"]: {k: v for k, v in t.items()
                                  if k != "qualified_id"} for t in org_base}
            clean_org = {k: v for k, v in org_term.items() if k != "qualified_id"}
            org_map[clean_org["id"]] = clean_org
            build_jp_index(list(org_map.values()))
            write_snapshot_artifact(
                registry.organization_root(), "org:common", org_snapshot_id,
                list(org_map.values()), published_at=approved_at,
                operation_id=operation_id)
            op["organization"]["status"] = "completed"
            op["organization"].pop("error", None)
        except (OSError, ValueError, KeyError) as exc:
            op["organization"].update(
                {"status": "retry_required", "error": str(exc)})
            op["status"] = "retry_required"
            _persist()
            return op
        _persist()

    for project_id, source_term_id in sorted(project_term_ids.items()):
        target = op["projects"][project_id]
        if target["status"] == "completed":
            continue
        try:
            base = source_bases[project_id]
            merged = []
            for term in base:
                clean = {k: v for k, v in term.items() if k != "qualified_id"}
                if term["id"] == source_term_id:
                    clean["status"] = "superseded"
                    clean["superseded_by"] = target_qid
                merged.append(clean)
            build_jp_index(merged)
            write_snapshot_artifact(
                registry.project_root(project_id), f"project:{project_id}",
                target["snapshot_id"], merged, published_at=approved_at,
                operation_id=operation_id)
            target["status"] = "completed"
            target.pop("error", None)
        except (OSError, ValueError, KeyError) as exc:
            target.update({"status": "retry_required", "error": str(exc)})
            op["status"] = "retry_required"
            for rid in (affected_requirements or {}).get(project_id, []):
                op["affected_requirements"][rid] = "retry_required"
            _persist()
            return op
        _persist()

    op["status"] = "completed"
    for rid in op["affected_requirements"]:
        op["affected_requirements"][rid] = "completed"
    _persist()
    return op


def attach_dependency(canonical: dict, target_path: str, candidate_id: str) -> dict:
    """スロットへ語彙候補依存を付与する（ADR-0014 D4。状態機械は増やさない）。

    依存が残る限りterminology-validatorがTERM_APPROVAL_PENDING（blocking）を
    発火し、review_ready/approvedへ進めない。解消は伝播Patchが行う。
    """
    slots = canonical["resolution"]["slots"]
    slot = slots.setdefault(target_path, {"status": "unknown"})
    deps = slot.setdefault("dependency_refs", [])
    ref = {"type": "terminology_candidate", "reference": candidate_id}
    if ref not in deps:
        deps.append(ref)
    return slot


def _clear_dependency(canonical: dict, target_path: str):
    slot = canonical["resolution"]["slots"].get(target_path) or {}
    if "dependency_refs" in slot:
        slot["dependency_refs"] = [
            d for d in slot["dependency_refs"]
            if d.get("type") != "terminology_candidate"]
        if not slot["dependency_refs"]:
            del slot["dependency_refs"]


def ambiguity_findings(observations: list[dict], vocab) -> list[dict]:
    """同表記多義（homonym）のObservationへAMBIGUOUS_TERM findingを生成する。"""
    from rimay_jp_core.model import finding
    out = []
    for o in observations:
        r = resolve_surface(o["surface_form"], vocab=vocab)
        if r["kind"] == "ambiguous":
            out.append(finding(
                "AMBIGUOUS_TERM",
                f"同表記が複数の登録概念に一致します: {o['surface_form']}",
                o.get("target_path"), surface_form=o["surface_form"],
                matches=[m["term_id"] for m in r["matches"]]))
    return out


def propagate(store: TerminologyStore, operation_id: str,
              canonicals: dict, *, applied_at: str) -> dict:
    """公開Snapshotの影響Requirementへの伝播（ADR-0014 D4のSaga実行）。

    - idempotent: completed要求はスキップ。確定済みスロットへ重複Patchしない。
    - 失敗・不在はretry_requiredとして永続化（隠さない・放置できない）。
    - Patch evidenceは knowledge_asset（term:<id>@<snapshot>）でReceiptへ追跡可能。
    """
    from rimay_jp_core.patch import apply_canonical_patch
    op = store.operation(operation_id)
    if op is None:
        raise ValueError(f"unknown operation: {operation_id}")
    for rid, status in list(op["affected_requirements"].items()):
        if status in ("completed", "advisory"):
            continue  # advisory（re-validate/re-review/stale）はPatch対象外
        c = canonicals.get(rid)
        if c is None:
            op["affected_requirements"][rid] = "retry_required"
            continue
        ok_all = True
        for tgt in (op.get("targets") or {}).get(rid, []):
            path = tgt["target_path"]
            slot = c["resolution"]["slots"].get(path) or {}
            if slot.get("status") == "confirmed":
                _clear_dependency(c, path)
                continue
            patch = {"operation": "replace_slot", "requirement_id": rid,
                     "base_revision": c["revision"],
                     "expected_status": slot.get("status", "unknown"),
                     "path": path, "new_value": tgt["term_id"],
                     "new_status": "confirmed",
                     "evidence": {"type": "knowledge_asset",
                                  "reference": f"term:{tgt['term_id']}"
                                               f"@{op['snapshot_id']}"}}
            res = apply_canonical_patch(c, patch)
            if not res["ok"]:
                ok_all = False
                break
            c = res["canonical"]
            canonicals[rid] = c
            _clear_dependency(c, path)
            store.record_resolution(
                tgt["occurrence_id"], "resolved",
                resolved_term_id=tgt["term_id"],
                snapshot_id=op["snapshot_id"], resolved_at=applied_at)
        op["affected_requirements"][rid] = "completed" if ok_all \
            else "retry_required"
    if all(v in ("completed", "advisory")
           for v in op["affected_requirements"].values()):
        op["status"] = "completed"
    (store.root / "operations" / f"{operation_id}.json").write_text(
        json.dumps(op, ensure_ascii=False, indent=1), encoding="utf-8")
    return op


def candidate_not_resolvable(store: TerminologyStore) -> list[str]:
    """Gate 2の機械検査: 候補語が正規化で解決されないことの違反一覧。"""
    violations = []
    for cand in store.candidates():
        if cand["status"] in ("open", "under_review") and \
                lookup_jp(cand["surface_form"]):
            violations.append(
                f"候補語が正規化で解決可能: {cand['surface_form']}")
    return violations
