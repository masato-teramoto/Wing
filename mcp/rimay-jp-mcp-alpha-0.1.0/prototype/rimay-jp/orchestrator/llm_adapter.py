"""llm-adapter: LLM分類・抽出のsource-analysis契約接続（Phase 5、PoC継続条件①）。

役割分担（llm-backend-design §1・§3・§8）:
- LLMは**候補生成のみ**を行う実行役。出力契約（llm-proposal.schema.json）は
  statusフィールドを持たず、confirmedを構造的に表現できない。
- 組立は本アダプタが決定論的に行う: value非null→proposed（source_span付き
  Provenance）、value null→unknown。family確定後の必須Role欠落は
  case frames（決定論知識）からunknown化する（LLMの申告に依存しない）。
- 知識供給は4層分離（§3）: 常時注入コアはProfile定数のみ（**用語辞書の件数と
  独立**＝§22.4の常時ロード知識量の統制）。用語候補はPatch提案段でのみ
  オンデマンド供給する（動的知識利用率の測定対象）。
- Patch提案はnew_status=proposed・evidence=tool_resultに固定して
  apply_canonical_patchへ渡す（confirmedはPROVENANCE-MISSINGで拒否される）。

バックエンド:
- ReplayBackend: 実モデル出力を記録したfixture（corpus/llm/fixtures/*.jsonl）を
  決定論的に再生する。CI・回帰用。モデル名・記録方法をfixtureに明記する。
- AnthropicApiBackend: ANTHROPIC_API_KEY設定時のライブ接続（stdlib urllib）。
  同一runnerで実測を再実行できる（§22.6: モデル・プロンプト版・温度を記録）。
"""
from __future__ import annotations

import json
import os
import re
import urllib.request
from functools import lru_cache
from pathlib import Path

from jsonschema import Draft202012Validator

from . import _ROOT  # noqa: F401
from rimay_jp_core import PROFILE_VERSION, MVP_CONDITIONS  # noqa: E402
from rimay_jp_core.lexicon import (ROOT as RIMAY_ROOT, case_frames, terms,  # noqa: E402
                                   lookup_jp)
from rimay_jp_core.model import new_canonical, set_slot  # noqa: E402
from rimay_jp_core.validator import _ROLE_FIELD  # noqa: E402

CORE_PROMPT_VERSION = "0.1.0"
TEMPERATURE = 0  # §22.6: 評価時は温度固定

# LLMが使用できるスロットPointerの許可一覧（プロンプト固定知識と同一のSSOT）
_RESPONSE_FIELDS = ("actor", "modality", "theme", "content", "destination",
                    "location", "display_location", "source", "input", "rule",
                    "property", "result_value", "channel")
_ALLOWED_POINTERS = tuple(
    [f"/rimay_core/response/{f}" for f in _RESPONSE_FIELDS]
    + ["/rimay_core/response/action/family",
       "/rimay_core/conditions/0/type",
       "/rimay_core/conditions/0/event/actor",
       "/rimay_core/conditions/0/event/object",
       "/rimay_core/conditions/0/event/action/family"])

_CLASSES = ("context", "problem", "goal", "stakeholder_view", "assumption",
            "issue", "decision", "business_rule", "requirement_candidate")


@lru_cache(maxsize=1)
def _proposal_validator() -> Draft202012Validator:
    doc = json.loads((RIMAY_ROOT / "canonical" / "llm-proposal.schema.json")
                     .read_text(encoding="utf-8"))
    return Draft202012Validator(doc)


# ---- プロンプト（常時注入コア＝Profile定数のみ。用語辞書と独立） ----

@lru_cache(maxsize=1)
def build_core_prompt() -> str:
    families = "、".join(sorted(case_frames().keys()))
    conditions = " / ".join(sorted(MVP_CONDITIONS))
    pointers = "\n".join(f"  {p}" for p in _ALLOWED_POINTERS)
    return f"""あなたは要求文書の分析器である。出力は指定したJSONのみとする（コードフェンス・説明文・前置きなし）。

[固定知識: Supported Profile {PROFILE_VERSION} / core-prompt {CORE_PROMPT_VERSION}]
- 分類カテゴリ: {" / ".join(_CLASSES)}
- Action family: {families}
- モダリティ: MUST（〜しなければならない）/ MUST_NOT（〜してはならない）
- 条件型: {conditions}
- スロットPointer許可一覧（これ以外は使用不可）:
{pointers}

[規則]
1. 入力文を分類カテゴリのいずれか1つへ分類し、根拠をrationaleへ書く。
2. requirement_candidate以外は slots を空オブジェクトにする。
3. requirement_candidateの場合、文に明示された値のみslotsへ入れる。
   各値に source_span（原文中の該当表現）を必ず付ける。
4. 文に無い値を推測して埋めない。必要だが文に無いスロットは value: null で列挙してよい。
5. 値の確定はできない。すべて候補として後段の検証・質問・人間確認を経る。
6. 出力JSON形式:
   {{"classification": "...", "rationale": "...",
    "slots": {{"<pointer>": {{"value": "...", "source_span": "..."}}}}}}"""


def build_case_prompt(segment: dict) -> str:
    return (build_core_prompt()
            + f"\n\n[入力文]\n{segment['text'].strip()}\n\n[出力JSON]")


def build_patch_prompt(case_prompt_text: str, target_path: str,
                       term_candidates: list[dict]) -> str:
    """Patch提案プロンプト。用語候補はオンデマンド供給（動的知識利用率の測定対象）。"""
    cands = "\n".join(f"  - id: {t['id']}（日本語: {t.get('ja', '')}）"
                      for t in term_candidates)
    return f"""あなたは要求スロットの候補提案器である。出力は指定したJSONのみとする。

[対象要求文]
{case_prompt_text.strip()}

[未確定スロット]
{target_path}

[使用可能な用語候補（この一覧のみ。一覧に適切な候補が無ければ空リストを返す）]
{cands}

[規則]
1. 要求文の意味に適合する候補だけを提案する。推測で埋めない。
2. 候補は最大1件。確定はできない（提案は後段で検証される）。
3. 出力JSON形式: {{"patches": [{{"path": "{target_path}", "new_value": "<用語id>", "reference": "term:<用語id>"}}]}}"""


# ---- 応答の解析・契約検査 ----

_FENCE = re.compile(r"^```[a-zA-Z]*\n|\n?```$")


def parse_response(text: str) -> tuple[dict | None, list[str]]:
    """LLM応答テキスト → (契約適合proposal, 違反一覧)。違反時はproposal=None。"""
    body = _FENCE.sub("", text.strip()).strip()
    start = body.find("{")
    if start > 0:
        body = body[start:]
    try:
        obj = json.loads(body)
    except (json.JSONDecodeError, ValueError) as e:
        return None, [f"JSONとして解析できない: {e}"]
    errs = [e.message for e in _proposal_validator().iter_errors(obj)]
    if errs:
        return None, [f"llm-proposal契約違反: {m}" for m in errs[:3]]
    return obj, []


# ---- 決定論的組立（source-analysis契約への写像） ----

def assemble_source_analysis(segment: dict, proposal: dict,
                             requirement_id: str = "REQ-LLM") -> dict:
    """契約適合proposal → source-analysis出力（extraction_mode=llm）。

    統制: value非null→proposed（span付きProvenance）、value null→unknown。
    許可一覧外Pointer・未知family・未知モダリティは拒否して計数する。
    confirmedを作るコードパスは存在しない。
    """
    rejected: list[dict] = []
    out = {"segment": {k: v for k, v in segment.items()
                       if k in ("document_id", "section_id", "text", "location")},
           "classification": proposal["classification"],
           "rationale": proposal["rationale"],
           "extraction_mode": "none", "canonical": None,
           "rejected_slots": rejected}
    if proposal["classification"] != "requirement_candidate":
        return out

    c = new_canonical(requirement_id)
    src = re.sub(r"\s+", "", segment["text"])
    c["source"]["text"] = src
    c["source"]["source_segments"] = [out["segment"]]
    c["rimay_core"]["response"] = {}
    from rimay_jp_core.normalizer import attach_surface_analysis
    attach_surface_analysis(c, src, "llm")  # 表層解析はNormalizerに集約（ADR-0013）

    family = None
    for pointer, slot in sorted(proposal["slots"].items()):
        value, span = slot.get("value"), slot.get("source_span")
        if pointer not in _ALLOWED_POINTERS:
            rejected.append({"pointer": pointer, "reason": "pointer_not_allowed"})
            continue
        if value is None:
            set_slot(c, pointer, "unknown", confirmation_required=True)
            continue
        if pointer.endswith("/action/family"):
            if value not in case_frames():
                rejected.append({"pointer": pointer, "value": value,
                                 "reason": "unknown_family"})
                continue
            if pointer == "/rimay_core/response/action/family":
                family = value
        if pointer.endswith("/modality") and value not in ("MUST", "MUST_NOT"):
            rejected.append({"pointer": pointer, "value": value,
                             "reason": "unknown_modality"})
            continue
        # 用語正規化は決定論コアの責務（§3）: LLMは表層を提案し、
        # 辞書完全一致の場合のみ用語IDへ解決する（それ以外は表層のまま
        # proposedとし、terminology validatorが未登録語として検出する）
        if (isinstance(value, str) and not pointer.endswith("/modality")
                and not pointer.endswith("/family") and not pointer.endswith("/type")):
            hit = lookup_jp(value) or lookup_jp(value.strip("「」『』\"'"))
            if hit:
                value = hit[0]
        _set_by_pointer(c, pointer, value)
        set_slot(c, pointer, "proposed", source_span=span or segment["text"],
                 method="llm_candidate")

    # 型一致による必須Roleの再配置（決定論: 辞書型×フレーム要求が一意な場合のみ）。
    # 例: UPDATEのproperty必須に対し、theme に置かれた property型用語を再配置する。
    frame = case_frames().get(family) if family else None
    _rehome_typed_roles(c, frame)

    # 必須Role欠落のunknown化は決定論知識（case frames）が担保する
    if frame:
        for role in frame["required_roles"]:
            field = _ROLE_FIELD.get(role)
            if not field:
                continue
            p = f"/rimay_core/response/{field}"
            if field != "actor" and not c["rimay_core"]["response"].get(field) \
                    and p not in c["resolution"]["slots"]:
                set_slot(c, p, "unknown", confirmation_required=True)

    # Sourceカバレッジ（ADR-0013 D4）: 提案のsource_spanを原文中で消費として
    # 記録し、根拠づけられなかった残りをunconsumedとして残す
    from rimay_jp_core.normalizer import attach_normalization
    flags: list = [None] * len(src)
    if src.endswith("。"):
        flags[-1] = "i"
    for pointer, slot in proposal["slots"].items():
        span = slot.get("source_span")
        if span:
            idx = src.find(re.sub(r"\s+", "", span))
            if idx >= 0:
                for i in range(idx, idx + len(re.sub(r"\s+", "", span))):
                    flags[i] = "c"
    attach_normalization(c, "llm", src, flags=flags)
    out.update(extraction_mode="llm", canonical=c)
    return out


# 一意な辞書型を持つRole field（型一致再配置の対象。class型等の多義型は対象外）
_TYPED_FIELDS = {"property": "property", "rule": "rule"}


def _rehome_typed_roles(canonical: dict, frame: dict | None):
    """必須Role欠落を、辞書型が一致する提案値の再配置で決定論的に解消する。

    値の推測ではない: 「フレームが要求するRoleの辞書型」と「提案値の辞書型」が
    ともに一意に定まる場合のみ移動する（proposedのまま。確定はしない）。
    """
    if not frame:
        return
    resp = canonical["rimay_core"]["response"]
    slots = canonical["resolution"]["slots"]
    term_type = {t["id"]: t["type"] for t in terms()}
    for role in frame["required_roles"]:
        field = _ROLE_FIELD.get(role)
        ftype = _TYPED_FIELDS.get(field)
        if not ftype or resp.get(field):
            continue
        for src_field in ("theme", "content", "input"):
            v = resp.get(src_field)
            if isinstance(v, str) and term_type.get(v) == ftype:
                resp[field] = v
                resp.pop(src_field)
                sp = f"/rimay_core/response/{src_field}"
                dp = f"/rimay_core/response/{field}"
                if sp in slots:
                    slots[dp] = slots.pop(sp)
                for prv in canonical["provenance"]:
                    if prv.get("path") == sp:
                        prv["path"] = dp
                break


def _set_by_pointer(canonical: dict, pointer: str, value):
    tokens = pointer.strip("/").split("/")
    node = canonical
    for t in tokens[:-1]:
        if isinstance(node, list):
            idx = int(t)
            while len(node) <= idx:
                node.append({})
            node = node[idx]
        else:
            if t not in node or node[t] is None:
                node[t] = [] if t == "conditions" else {}
            node = node[t]
    node[tokens[-1]] = value


def make_patches(canonical: dict, patch_proposal: dict,
                 question_id: str = "LLM-PATCH") -> list[dict]:
    """LLMのPatch提案 → 統制済みPatch（proposed・tool_result固定）。"""
    out = []
    for p in patch_proposal.get("patches") or []:
        slots = canonical["resolution"]["slots"]
        current = (slots.get(p.get("path")) or {}).get("status", "unknown")
        out.append({
            "operation": "replace_slot",
            "requirement_id": canonical["requirement_id"],
            "base_revision": canonical["revision"],
            "path": p.get("path"),
            "expected_status": current,
            "new_value": p.get("new_value"),
            "new_status": "proposed",  # LLM候補はproposed固定（§8統制点3）
            "evidence": {"type": "tool_result",
                         "reference": p.get("reference") or question_id},
        })
    return out


def term_candidates_for(field: str, limit: int = 8) -> list[dict]:
    """Patch提案段のオンデマンド用語供給（型の優先順で列挙。宛先はproperty=
    メールアドレス等を先に出す）。"""
    types = {"destination": ("property", "actor"), "source": ("actor", "class"),
             "location": ("class",), "display_location": ("class",),
             "rule": ("rule",), "theme": ("class",), "content": ("class",),
             "input": ("class",), "actor": ("actor",)}.get(field, ())
    out = []
    for ty in types:
        out += [{"id": t["id"], "ja": t.get("preferred_japanese") or ""}
                for t in terms() if t["type"] == ty]
    return out[:limit]


# ---- バックエンド ----

class ReplayBackend:
    """実モデル出力の決定論的再生（fixture）。CI・回帰用。"""

    def __init__(self, path: Path):
        self.path = Path(path)
        self.model = "replay"
        self._responses: dict[tuple, dict] = {}
        for line in self.path.read_text(encoding="utf-8").splitlines():
            if not line.strip():
                continue
            rec = json.loads(line)
            self._responses[(rec["case_id"], rec["stage"])] = rec
            self.model = rec.get("model", self.model)

    def complete(self, prompt: str, case_id: str, stage: str) -> dict:
        rec = self._responses.get((case_id, stage))
        if rec is None:
            return {"text": "", "model": self.model,
                    "error": f"fixture欠落: {case_id}/{stage}"}
        return {"text": rec["response"], "model": rec.get("model", self.model),
                "usage": rec.get("usage")}


class AnthropicApiBackend:
    """ライブ接続（ANTHROPIC_API_KEY設定時）。§22.6の記録項目を返す。"""

    def __init__(self, model: str = "claude-sonnet-5"):
        self.model = model
        self.api_key = os.environ.get("ANTHROPIC_API_KEY")
        if not self.api_key:
            raise RuntimeError("ANTHROPIC_API_KEYが未設定です")

    def complete(self, prompt: str, case_id: str, stage: str) -> dict:
        req = urllib.request.Request(
            "https://api.anthropic.com/v1/messages",
            data=json.dumps({
                "model": self.model, "max_tokens": 1024,
                "temperature": TEMPERATURE,
                "messages": [{"role": "user", "content": prompt}],
            }).encode("utf-8"),
            headers={"content-type": "application/json",
                     "x-api-key": self.api_key,
                     "anthropic-version": "2023-06-01"})
        with urllib.request.urlopen(req, timeout=120) as res:
            body = json.loads(res.read().decode("utf-8"))
        return {"text": "".join(b.get("text", "") for b in body["content"]),
                "model": body.get("model", self.model),
                "usage": body.get("usage")}
