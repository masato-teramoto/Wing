"""射影意味等価検査: canonicalize(parse(serialize(project(C)))) == normalize_core(project(C))。

比較は表層文字列ではなく、Condition Type、action family、Entity Reference（用語ID）、
Semantic Role、モダリティで行う（ast-canonical-mapping.yaml の正規化規則）。
"""
from .lexicon import resolve_en
from .parser import verb_family
from .semantic_values import split_money
from .atomic_response import semantic_atomic_response


def _entity(surface: str):
    """英語表層 → 用語ID（引用符内ラベル・裸IDの双方を受理）。"""
    tid = resolve_en(surface)
    return tid if tid else surface.replace(" ", "")


def _money(surface: str):
    return split_money(surface)


def canonicalize_ast(ast: dict) -> dict:
    """AST → 比較用 rimay_core 射影。"""
    core: dict = {"scope": None}
    if ast.get("scope"):
        core["scope"] = {"function": _entity(ast["scope"])}

    def condition_value(cond: dict) -> dict:
        kind = cond["kind"]
        if kind in ("when", "after", "before"):
            fam = verb_family(cond["verb"])
            c = {"type": kind.upper(),
                 "event": {"actor": _entity(cond["actor"]),
                           "action": {"family": fam},
                           "object": _entity(cond["object"])}}
            # eventのvalueはUPDATE系トリガーの更新後値のみ（他の'to'句は役割句として無視）
            if cond.get("to_value") and fam == "UPDATE":
                c["event"]["value"] = _entity(cond["to_value"])
            return c
        else:
            pred = {"operator": cond["op"]}
            if "operand" in cond:
                # Typed identities are canonical IDs supplied by the explicit
                # surface; dictionary lookup would silently erase wrapper semantics.
                pred["operand"] = dict(cond["operand"])
                if "defined_in_type" in cond["operand"]:
                    pred["operand"]["defined_in_type"] = dict(
                        cond["operand"]["defined_in_type"])
            else:
                pred["subject"] = _entity(cond["subject"])
            if "value_expression" in cond:
                def value_expression(node: dict) -> dict:
                    kind = node["kind"]
                    if kind == "value":
                        money = _money(node["value"])
                        if money:
                            return {"kind": "value", "value": money[0], "unit": money[1]}
                        return {"kind": "value", "value": _entity(node["value"])}
                    if kind == "group":
                        return {"kind": "group",
                                "expression": value_expression(node["expression"])}
                    return {"kind": kind,
                            "left": value_expression(node["left"]),
                            "right": value_expression(node["right"])}
                pred["value_expression"] = value_expression(cond["value_expression"])
            else:
                m = _money(cond["value"])
                if m:
                    pred.update({"value": m[0], "unit": m[1]})
                else:
                    pred.update({"value": _entity(cond["value"])})
            return {"type": kind.upper(), "predicate": pred}

    def condition_expression_value(node: dict) -> dict:
        kind = node["kind"]
        if kind == "condition":
            return {"kind": "condition", "condition": condition_value(node["condition"])}
        return {
            "kind": kind,
            "left": condition_expression_value(node["left"]),
            "right": condition_expression_value(node["right"]),
        }

    if ast.get("condition_expression") is not None:
        core["condition_expression"] = condition_expression_value(
            ast["condition_expression"])
    else:
        core["conditions"] = [
            condition_value(cond) for cond in (ast.get("conditions") or [])
        ]

    def response_value(r: dict) -> dict:
        fam = r["action"]["family"]
        # rimay_action_idはSerializer検証・conformance比較でのみ扱う（semantic射影から除外）
        resp = {"actor": _entity(r["actor"]),
                "modality": r["modality"],
                "action": {"family": fam}}
        # C3: ASTのrolesはRole名キー（Parserがprofile束縛で写像済み。§21.8）。
        for role, entry in (r.get("roles") or {}).items():
            resp[role] = _entity(entry["value"])
        if isinstance(r.get("frequency"), dict):
            resp["frequency"] = {
                "value": r["frequency"]["value"],
                "unit": r["frequency"]["unit"],
            }
        return resp

    def expression_value(node: dict) -> dict:
        kind = node["kind"]
        if kind == "response":
            return {"kind": "response", "response": response_value(node["response"])}
        if kind == "group":
            return {"kind": "group", "expression": expression_value(node["expression"])}
        return {"kind": kind,
                "left": expression_value(node["left"]),
                "right": expression_value(node["right"])}

    def block_value(block: dict) -> dict:
        return {
            "kind": block["kind"],
            "in_sequence": block["in_sequence"],
            "items": [{
                "position": item["position"],
                "bullet": dict(item["bullet"]),
                "connector_before": item["connector_before"],
                "response": response_value(item["response"]),
            } for item in block["items"]],
        }

    # retention（KEEP_15_2句）はextensions（sidecar）帰属のためsemantic射影に含めない（§21.6）
    if ast.get("response_block") is not None:
        core["response_block"] = block_value(ast["response_block"])
    elif ast.get("response_expression") is not None:
        core["response_expression"] = expression_value(ast["response_expression"])
    else:
        core["response"] = response_value(ast["response"])
    return core


def project(canonical: dict) -> dict:
    """Canonical → 比較用 rimay_core 射影（None値とrimay_action_idを落とす）。

    rimay_action_idは表記事項でありSerializer検証でのみ比較する
    （ast-canonical-mapping.yaml 正規化規則）。
    """
    def strip(v, drop_action_id=False):
        if isinstance(v, dict):
            return {k: strip(x, drop_action_id=(k == "action"))
                    for k, x in v.items()
                    if x is not None and not (drop_action_id and k == "rimay_action_id")}
        if isinstance(v, list):
            return [strip(x) for x in v]
        return v
    projected = strip(semantic_atomic_response(canonical["rimay_core"]))

    def normalize_value_expression(node: object) -> None:
        if not isinstance(node, dict):
            return
        kind = node.get("kind")
        if kind == "value" and node.get("unit") == "JPY" and \
                isinstance(node.get("value"), str):
            money = split_money(f"{node['value']} JPY")
            if money is not None:
                node["value"] = money[0]
        elif kind == "group":
            normalize_value_expression(node.get("expression"))
        elif kind in {"and", "or"}:
            normalize_value_expression(node.get("left"))
            normalize_value_expression(node.get("right"))

    def normalize_predicate_money(node: object) -> None:
        if isinstance(node, dict):
            predicate = node.get("predicate")
            if isinstance(predicate, dict):
                if predicate.get("unit") == "JPY" and \
                        isinstance(predicate.get("value"), str):
                    money = split_money(f"{predicate['value']} JPY")
                    if money is not None:
                        predicate["value"] = money[0]
                normalize_value_expression(predicate.get("value_expression"))
            for value in node.values():
                normalize_predicate_money(value)
        elif isinstance(node, list):
            for value in node:
                normalize_predicate_money(value)

    normalize_predicate_money(projected)
    return projected


def compare_semantic(canonical: dict, ast: dict) -> list[str]:
    """不一致パスのリストを返す（空なら射影意味等価）。"""
    a, b = project(canonical), canonicalize_ast(ast)
    diffs: list[str] = []

    def walk(x, y, path):
        if isinstance(x, dict) or isinstance(y, dict):
            x = x if isinstance(x, dict) else {}
            y = y if isinstance(y, dict) else {}
            for k in sorted(set(x) | set(y)):
                walk(x.get(k), y.get(k), f"{path}/{k}")
        elif isinstance(x, list) or isinstance(y, list):
            x = x if isinstance(x, list) else []
            y = y if isinstance(y, list) else []
            if len(x) != len(y):
                diffs.append(f"{path}: length {len(x)} != {len(y)}")
            for i, (xi, yi) in enumerate(zip(x, y)):
                walk(xi, yi, f"{path}/{i}")
        else:
            if x is None and y is None:
                return
            if x != y:
                diffs.append(f"{path}: {x!r} != {y!r}")

    walk(a, b, "")
    return diffs


# 旧APIのalias（§21.5: 1 minor期間維持。実行時warningは決定性のため出さない）
compare = compare_semantic


def compare_conformance(canonical: dict, ast: dict, profile: dict | None = None) -> list[str]:
    """grammar conformance差分（semanticとは別軸。§21.5・D4）。

    検査対象:
      - AST束縛（rimay_action_id / emse_rule_id）がEnglish conformance profileの
        family束縛と一致すること
      - full consumption（parse_meta.consumed）が存在すること
      - 条件operatorがprofileのin集合に含まれること
      - Canonical側rimay_action_idとprofile束縛の一致（C4 migration完了済み。
        pipelineのGateに組込済み＝RC-005）
    """
    from .english_profile import binding, load_profile, operators_in
    prof = profile or load_profile()
    diffs: list[str] = []
    def response_entries(value: dict, prefix: str):
        if value.get("response_block") is not None:
            return [
                (f"{prefix}/response_block/items/{index}/response", item["response"])
                for index, item in enumerate(value["response_block"]["items"])
            ]
        if value.get("response_expression") is None:
            return [(prefix + "/response", value["response"])]
        out = []

        def visit(node, path):
            kind = node["kind"]
            if kind == "response":
                out.append((path + "/response", node["response"]))
            elif kind == "group":
                visit(node["expression"], path + "/expression")
            else:
                visit(node["left"], path + "/left")
                visit(node["right"], path + "/right")

        visit(value["response_expression"], prefix + "/response_expression")
        return out

    ast_entries = response_entries(ast, "")
    canonical_entries = response_entries(canonical["rimay_core"], "/rimay_core")
    if len(ast_entries) != len(canonical_entries):
        diffs.append(
            f"/response_expression: AST leaf count {len(ast_entries)} "
            f"!= canonical {len(canonical_entries)}")
    for (ast_path, response), (canonical_path, canonical_response) in zip(
            ast_entries, canonical_entries):
        fam = response["action"]["family"]
        b = prof["bindings"].get(fam) or binding(fam)
        act = response["action"]
        if act.get("rimay_action_id") != b.get("rimay_action_id"):
            diffs.append(
                f"{ast_path}/action/rimay_action_id: AST "
                f"{act.get('rimay_action_id')!r} != profile {b.get('rimay_action_id')!r}")
        if act.get("emse_rule_id") != b.get("emse_rule_id"):
            diffs.append(
                f"{ast_path}/action/emse_rule_id: AST {act.get('emse_rule_id')!r} "
                f"!= profile {b.get('emse_rule_id')!r}")
        can_id = (canonical_response.get("action") or {}).get("rimay_action_id")
        if can_id and can_id != b.get("rimay_action_id"):
            diffs.append(
                f"{canonical_path}/action/rimay_action_id: canonical {can_id!r} "
                f"!= profile {b.get('rimay_action_id')!r}")
    meta = ast.get("parse_meta") or {}
    consumed = meta.get("consumed") or {}
    if consumed.get("start") != 0 or "end" not in consumed:
        diffs.append("/parse_meta/consumed: full-consumption証跡がない")
    ops_in = operators_in()
    def condition_entries(value: dict):
        if value.get("condition_expression") is None:
            return [
                (f"/conditions/{index}", condition)
                for index, condition in enumerate(value.get("conditions") or [])
            ]
        out = []

        def visit(node, path):
            if node["kind"] == "condition":
                out.append((path + "/condition", node["condition"]))
            else:
                visit(node["left"], path + "/left")
                visit(node["right"], path + "/right")

        visit(value["condition_expression"], "/condition_expression")
        return out

    for path, cond in condition_entries(ast):
        op = cond.get("op")
        if op and op not in ops_in:
            diffs.append(f"{path}/op: {op!r} is not in profile operator set")
    return diffs


def check_sidecar(canonical: dict, views: dict) -> list[str]:
    """sidecar完全性 + manifest整合（SIDECAR-LOSS / SIDECAR-STALE）。"""
    from .model import canonical_hash
    problems = []
    if views["sidecar"].get("extensions") != (canonical.get("extensions") or {}):
        problems.append("SIDECAR-LOSS: extensionsがsidecarと一致しません")
    if views["manifest"]["canonical_hash"] != canonical_hash(canonical):
        problems.append("SIDECAR-STALE: manifestのcanonical_hashが現行Canonicalと不一致")
    return problems
