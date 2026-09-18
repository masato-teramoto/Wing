"""Rule Engine: オーケストレーション規則の決定論的評価（Phase 3C）。

- 実行順序は stage（列挙順）→ priority（小さいほど先）→ Rule ID辞書順。
- when条件・target_selectorはRuleSelector（'*'許可）。評価時に単一の
  CanonicalPointerへ展開し、発行される質問・PatchのtargetはPointerになる。
- LLMは処理順序や合否を決めない（構想書 §14.8）。
"""
import json
from functools import lru_cache
from pathlib import Path

import yaml
from jsonschema import Draft202012Validator

from . import _ROOT
from rimay_jp_core.lexicon import ROOT as CORE_ROOT  # noqa: E402

STAGES = ["structural_completion", "semantic_disambiguation", "knowledge_conflict",
          "exception_boundary", "quality_constraint", "downstream_generation"]

_RULES_PATH = Path(__file__).resolve().parent / "rules" / "mvp-rules.yaml"


@lru_cache(maxsize=1)
def rule_set_version() -> str:
    """Rule資産の宣言版数（記録は実体から取得する＝ADR-0013 D3の版数規律）。"""
    doc = yaml.safe_load(_RULES_PATH.read_text(encoding="utf-8"))
    return str(doc.get("rule_set_version", "0.0.0"))


@lru_cache(maxsize=1)
def load_rules() -> list[dict]:
    """規則をSchema検証してからstage/priority/id順で返す。"""
    doc = yaml.safe_load(_RULES_PATH.read_text(encoding="utf-8"))
    with open(CORE_ROOT / "canonical" / "orchestration-rule.schema.json",
              encoding="utf-8") as f:
        errors = [f"{e.json_path}: {e.message}"
                  for e in Draft202012Validator(json.load(f)).iter_errors(doc)]
    if errors:
        raise ValueError(f"mvp-rules.yamlがSchemaに違反: {errors[:3]}")
    return sorted(doc["rules"],
                  key=lambda r: (STAGES.index(r["stage"]), r["priority"], r["id"]))


def expand_selector(selector: str, canonical: dict) -> list[str]:
    """RuleSelector → 具体的なCanonicalPointerのリスト。'*'は配列全要素。"""
    pointers = [""]
    node_map = {"": canonical}
    for token in selector.strip("/").split("/"):
        nxt: list[str] = []
        nxt_map = {}
        for ptr in pointers:
            node = node_map[ptr]
            if token == "*":
                if isinstance(node, list):
                    for i, item in enumerate(node):
                        p = f"{ptr}/{i}"
                        nxt.append(p)
                        nxt_map[p] = item
                continue
            child = None
            if isinstance(node, list):
                try:
                    child = node[int(token)]
                except (ValueError, IndexError):
                    continue
            elif isinstance(node, dict):
                if token not in node:
                    # 実体が未生成でもスロット参照はあり得る（値なしスロット）
                    p = f"{ptr}/{token}"
                    nxt.append(p)
                    nxt_map[p] = None
                    continue
                child = node[token]
            else:
                continue
            p = f"{ptr}/{token}"
            nxt.append(p)
            nxt_map[p] = child
        pointers, node_map = nxt, nxt_map
    return pointers


def value_at(canonical: dict, pointer: str):
    node = canonical
    for token in pointer.strip("/").split("/"):
        if isinstance(node, list):
            try:
                node = node[int(token)]
            except (ValueError, IndexError):
                return None
        elif isinstance(node, dict):
            node = node.get(token)
        else:
            return None
    return node


def _atomic_lhs(cond: dict, canonical: dict, pointer: str):
    slots = canonical["resolution"]["slots"]
    if "value_at" in cond:
        return value_at(canonical, pointer)
    if "status_at" in cond:
        slot = slots.get(pointer)
        return slot["status"] if slot else None  # 未評価はNone（unknownと区別）
    # meta_at
    slot = slots.get(pointer) or {}
    op = cond["op"]
    if op == "candidate_count_greater_than":
        return len(slot.get("candidates") or [])
    if op == "confirmation_required":
        return bool(slot.get("confirmation_required"))
    return None


def _apply_op(op: str, lhs, rhs) -> bool:
    if op == "equals":
        return lhs == rhs
    if op == "not_equals":
        return lhs != rhs
    if op == "in":
        return lhs in rhs
    if op == "not_in":
        return lhs not in rhs
    if op == "greater_than":
        return lhs is not None and lhs > rhs
    if op == "less_than":
        return lhs is not None and lhs < rhs
    if op == "exists":
        return (lhs is not None) == rhs
    if op == "candidate_count_greater_than":
        return lhs > rhs
    if op == "confirmation_required":
        return lhs == rhs
    return False


def eval_expr(expr: dict, canonical: dict, bind: dict[str, str] | None = None) -> bool:
    """条件式の評価。bind: selector→固定Pointer（done_whenのtarget束縛用）。
    '*'を含むselectorは存在量化（いずれかの展開先で真）。"""
    if "all" in expr:
        return all(eval_expr(e, canonical, bind) for e in expr["all"])
    if "any" in expr:
        return any(eval_expr(e, canonical, bind) for e in expr["any"])
    if "not" in expr:
        return not eval_expr(expr["not"], canonical, bind)
    selector = expr.get("value_at") or expr.get("status_at") or expr.get("meta_at")
    if bind and selector in bind:
        pointers = [bind[selector]]
    else:
        pointers = expand_selector(selector, canonical) if "*" in selector else [selector]
    return any(_apply_op(expr["op"], _atomic_lhs(expr, canonical, p), expr["value"])
               for p in pointers)


def evaluate(canonical: dict, fired_once: set[str] | None = None) -> list[dict]:
    """発火した規則アクションのインスタンスを実行順で返す。

    戻り値要素: {rule_id, stage, priority, action_type, target_path(単一Pointer),
                question_template}
    """
    fired_once = fired_once or set()
    instances: list[dict] = []
    for rule in load_rules():
        if rule["execution_mode"] == "once" and rule["id"] in fired_once:
            continue
        if not eval_expr(rule["when"], canonical):
            continue
        selector = rule["action"].get("target_selector")
        targets = (expand_selector(selector, canonical) if selector and "*" in selector
                   else [selector] if selector else [None])
        for t in targets:
            if t is not None and "*" in (t or ""):
                continue
            # done_when（target束縛で個別判定）
            if rule.get("done_when"):
                bind = {selector: t} if selector and t else None
                if eval_expr(rule["done_when"], canonical, bind):
                    continue
            # whenの状態条件がこのtargetで成立しているか（'*'選択子の個別絞り込み）
            if selector and "*" in selector and not _target_matches(rule, canonical, selector, t):
                continue
            instances.append({
                "rule_id": rule["id"],
                "stage": rule["stage"],
                "priority": rule["priority"],
                "action_type": rule["action"]["type"],
                "target_path": t,
                "question_template": rule["action"].get("question_template"),
            })
    return instances


def _target_matches(rule: dict, canonical: dict, selector: str, pointer: str) -> bool:
    return eval_expr(rule["when"], canonical, {selector: pointer})
