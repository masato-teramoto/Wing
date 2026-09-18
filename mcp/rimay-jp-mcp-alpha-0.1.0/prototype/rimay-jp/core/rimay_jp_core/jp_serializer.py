"""Rimay-JP Serializer: Canonical → 標準Rimay-JP日本語文（Phase 3D）。

表層文はSerializerが再生成する（§14.13）。生成文は制約付き日本語の
標準形（§5表層順序・§9条件表現・§10モダリティ）に従い、
Normalizerで再解析して往復同値になることを検証層が確認する。
"""
from .lexicon import normalizer_profile, term_ids
from .condition_expression import (
    ConditionExpressionError,
    MultiValueRuntimeError,
    condition_core_findings,
    parse_rendered_condition_expression,
    render_condition_expression,
    validate_value_expression,
)
from .response_expression import (
    ResponseExpressionError,
    parse_rendered_response_expression,
    render_response_expression,
    response_core_findings,
)
from .response_block import (
    ResponseBlockError,
    parse_rendered_response_block,
    render_response_block,
)
from .atomic_response import AtomicResponseError

# family → トリガー動詞語幹（normalizer._TRIGGER_VERBSと整合）
_TRIGGER_STEM = {
    "PRESS": "押", "SEND": "送信", "UPDATE": "更新", "CREATE": "生成",
    "STORE": "保存", "RECEIVE": "受信", "VERIFY": "検証", "NOTIFY": "通知",
    "DELETE": "削除", "DISPLAY": "表示", "CALCULATE": "算出",
}

# family → 応答動詞語幹（normalizer._RESPONSE_VERBSと整合）
_RESPONSE_STEM = {
    "SEND": "送信", "UPDATE": "更新", "CREATE": "生成", "STORE": "保存",
    "RECEIVE": "受信", "DISPLAY": "表示", "DELETE": "削除", "VERIFY": "検証",
    "CALCULATE": "算出", "NOTIFY": "通知",
}

_FREQUENCY_UNIT_JP = {
    "second": "秒", "minute": "分", "hour": "時間", "day": "日",
}


def _jp(term_id: str) -> str:
    t = term_ids().get(term_id)
    return t["preferred_japanese"] if t else term_id


def _render_value_expression_jp(expression: dict) -> str:
    validate_value_expression(
        expression, path="/rimay_core/conditions/0/predicate/value_expression")

    def visit(node: dict) -> str:
        kind = node["kind"]
        if kind == "value":
            if node.get("unit") == "JPY":
                number = float(node["value"].replace(",", ""))
                surface = (f"{int(number):,}" if number.is_integer()
                           else format(number, ",g")) + "円"
            else:
                surface = _jp(node["value"])
            return f"「{surface}」"
        if kind == "group":
            return "(" + visit(node["expression"]) + ")"
        surfaces = normalizer_profile()["multi_value_connectors"]
        connector = " " + surfaces[kind] + " "
        return "(" + visit(node["left"]) + connector + visit(node["right"]) + ")"

    return visit(expression)


def render_condition_jp(cond: dict) -> str:
    ctype = cond["type"]
    if ctype in ("WHEN", "AFTER", "BEFORE"):
        ev = cond.get("event") or {}
        stem = _TRIGGER_STEM[ev["action"]["family"]]
        s = f"{_jp(ev['actor'])}が{_jp(ev['object'])}を"
        if ev.get("value"):
            s += f"「{_jp(ev['value'])}」に"
        tail = {"WHEN": "したとき", "AFTER": "した後に", "BEFORE": "する前に"}[ctype]
        # BEFOREは終止形接続（〜する前に）、WHEN/AFTERは連用形（〜した）
        return f"{s}{stem}{tail}、"
    if ctype in ("IF", "WHILE"):
        p = cond.get("predicate") or {}
        if "operand" in p:
            from .operator_value_expression_candidate import (
                OperatorValueExpressionCandidateError,
                render_operator_value_condition,
            )
            try:
                return render_operator_value_condition(
                    {"type": ctype, "predicate": p}, language="ja") + "、"
            except OperatorValueExpressionCandidateError as exc:
                raise ConditionExpressionError(
                    exc.code,
                    exc.path.replace("/condition", "/rimay_core/conditions/0"),
                    exc.message,
                ) from exc
        from .lexicon import normalizer_profile
        surfaces = normalizer_profile()["comparison_operator_surfaces"]
        operator = p.get("operator")
        if operator not in surfaces:
            raise ResponseExpressionError(
                "COMPARISON_OPERATOR_UNSUPPORTED",
                "/rimay_core/conditions/0/predicate/operator",
                f"unsupported comparison operator {operator!r}")
        if "value_expression" in p:
            if "value" in p or "unit" in p:
                raise ConditionExpressionError(
                    "MULTI_VALUE_DUAL_AUTHORITY",
                    "/rimay_core/conditions/0/predicate",
                    "scalar and value_expression authorities are mutually exclusive")
            try:
                value = _render_value_expression_jp(p["value_expression"])
            except MultiValueRuntimeError as exc:
                raise ConditionExpressionError(
                    exc.code, exc.path, exc.message) from exc
        else:
            unit = p.get("unit")
            if unit is not None and unit != "JPY":
                raise ResponseExpressionError(
                    "COMPARISON_OPERATOR_INVALID_OPERAND",
                    "/rimay_core/conditions/0/predicate/unit",
                    f"unsupported comparison unit {unit!r}")
            value = f"{int(p['value']):,}円" if unit == "JPY" else _jp(p["value"])
        suffix = "場合" if ctype == "IF" else "間"
        return (
            f"{_jp(p['subject'])}が{value if 'value_expression' in p else f'「{value}」'}"
            f"{surfaces[operator]}{suffix}、"
        )
    raise ValueError(f"unsupported condition type: {ctype}")


def role_phrase(canonical: dict, response: dict | None = None) -> str:
    """応答の役割句（§5標準表層順序: 対象→送信元→宛先→規則→手段。主体・時間・動詞は含まない）。"""
    resp = response if response is not None else canonical["rimay_core"]["response"]
    fam = resp["action"]["family"]
    s = ""
    if fam == "UPDATE":
        s += f"{_jp(resp['property'])}を"
        if resp.get("result_value"):
            s += f"「{_jp(resp['result_value'])}」に"
    else:
        theme_field = {"CALCULATE": "result", "NOTIFY": "content"}.get(fam, "theme")
        if resp.get(theme_field):
            s += f"{_jp(resp[theme_field])}を"
        source_field = {"CALCULATE": "input"}.get(fam, "source")
        if resp.get(source_field):
            s += f"{_jp(resp[source_field])}から"
        dest = resp.get("destination") or resp.get("location") or resp.get("display_location")
        if dest:
            s += f"{_jp(dest)}に"
        if resp.get("rule"):
            s += f"{_jp(resp['rule'])}に基づいて"
        if resp.get("channel"):
            s += f"{_jp(resp['channel'])}で"
    return s


def time_phrase(canonical: dict) -> str:
    """時間制約句（RETENTION → N年間、DEADLINE → N秒以内に）。"""
    s = ""
    for tc in (canonical.get("extensions") or {}).get("time_constraints") or []:
        if tc.get("value") is None:
            continue
        if tc.get("kind") == "RETENTION" and tc.get("unit") == "year":
            s += f"{tc['value']}年間"
        elif tc.get("kind") == "DEADLINE" and tc.get("unit") == "second":
            s += f"{tc['value']}秒以内に"
    return s


def response_stem(family: str) -> str:
    return _RESPONSE_STEM[family]


def jp_name(term_id: str) -> str:
    return _jp(term_id)


def trigger_dict_form(family: str) -> str:
    """トリガー動詞の終止形（押す・更新する等。Gherkin When行用）。"""
    stem = _TRIGGER_STEM[family]
    return f"{stem}す" if family == "PRESS" else f"{stem}する"


def _render_response_jp(canonical: dict, resp: dict, *, include_time: bool) -> str:
    fam = resp["action"]["family"]
    s = f"{_jp(resp['actor'])}は{role_phrase(canonical, resp)}"
    if include_time:
        s += time_phrase(canonical)
    frequency = resp.get("frequency")
    if frequency is not None:
        value = frequency["value"]
        number = str(value) if type(value) is int else format(value, "g")
        s += f"{number}{_FREQUENCY_UNIT_JP[frequency['unit']]}ごとに"
    modality = "しなければならない" if resp["modality"] == "MUST" else "してはならない"
    return f"{s}{_RESPONSE_STEM[fam]}{modality}"


def render_rimay_jp(canonical: dict) -> str:
    core = canonical["rimay_core"]
    source_text = (canonical.get("source") or {}).get("text")
    parts: list[str] = []

    condition_problems = condition_core_findings(core)
    if condition_problems:
        first = condition_problems[0]
        raise ConditionExpressionError(
            first["code"], first["path"], first["message"])
    response_problems = response_core_findings(core, source_text=source_text)
    if response_problems:
        first = response_problems[0]
        error_type = (
            ResponseBlockError if first["code"].startswith("RESPONSE_BLOCK_")
            else AtomicResponseError if first["code"].startswith("ATOMIC_RESPONSE_")
            else ResponseExpressionError
        )
        raise error_type(first["code"], first["path"], first["message"])

    if core.get("scope") and core["scope"].get("function"):
        parts.append(f"{_jp(core['scope']['function'])}において、")
    condition_expression = core.get("condition_expression")
    if condition_expression is not None:
        rendered_condition = render_condition_expression(
            condition_expression,
            lambda condition: render_condition_jp(condition).removesuffix("、"),
            language="ja",
        )
        parts.append(rendered_condition + "、")
    else:
        for cond in core.get("conditions") or []:
            parts.append(render_condition_jp(cond))

    block = core.get("response_block")
    expression = core.get("response_expression")
    if block is not None:
        if ((canonical.get("extensions") or {}).get("time_constraints") or []):
            raise ResponseBlockError(
                "RESPONSE_BLOCK_EXTENSION_SCOPE",
                "/extensions/time_constraints",
                "time constraint scope across Response Block items is not adopted")
        rendered = render_response_block(
            block,
            lambda response: _render_response_jp(canonical, response, include_time=False),
            language="ja",
            source_text=source_text,
        )
        parts.append(rendered + "。")
    elif expression is not None:
        if ((canonical.get("extensions") or {}).get("time_constraints") or []):
            raise ResponseExpressionError(
                "RESPONSE_EXPRESSION_EXTENSION_SCOPE",
                "/extensions/time_constraints",
                "time constraint scope across multiple responses is not adopted")
        rendered = render_response_expression(
            expression,
            lambda response: _render_response_jp(canonical, response, include_time=False),
            language="ja",
        )
        parts.append(rendered + "。")
    else:
        parts.append(_render_response_jp(
            canonical, core["response"], include_time=True) + "。")
    return "".join(parts)


def parse_rimay_jp(text: str) -> dict:
    """Parse the controlled Japanese surface emitted by ``render_rimay_jp``.

    The return value is a semantic ``rimay_core`` AST.  Provenance and resolution
    remain Canonical ingestion concerns and are intentionally not synthesized here.
    """
    from .model import is_blocked
    from .normalizer import normalize

    surface = text.strip()
    if not surface.endswith("。"):
        raise ResponseExpressionError(
            "RESPONSE_EXPRESSION_PARSE_INCOMPLETE", "/rimay_jp",
            "controlled Japanese requirement must end with 。")
    def top_level_commas(value: str) -> list[int]:
        depth = 0
        quoted = False
        out = []
        for index, char in enumerate(value):
            if char == "「":
                quoted = True
            elif char == "」":
                quoted = False
            elif not quoted and char == "(":
                depth += 1
            elif not quoted and char == ")":
                depth -= 1
            elif not quoted and depth == 0 and char == "、":
                out.append(index)
        return out

    body_without_period = surface[:-1]
    comma_positions = top_level_commas(body_without_period)
    condition_segment = ""
    if comma_positions:
        start = comma_positions[-2] + 1 if len(comma_positions) >= 2 else 0
        condition_segment = body_without_period[start:comma_positions[-1]]
    flat_multi_value_condition = (
        bool(condition_segment) and not condition_segment.startswith("(") and
        "が(" in condition_segment
    )

    expression_start = surface.find("(")
    block_start = surface.find("次の動作を実行する")
    if expression_start < 0 and block_start < 0:
        canonical, findings = normalize(surface, "REQ-JP-PARSE")
        if is_blocked(findings):
            raise ResponseExpressionError(
                "RESPONSE_EXPRESSION_PARSE_LEAF", "/rimay_jp",
                f"Japanese response is not controlled: {[f['code'] for f in findings]}")
        return canonical["rimay_core"]

    body = surface[:-1]

    def matching_parenthesis(value: str, start: int) -> int:
        depth = 0
        for index in range(start, len(value)):
            if value[index] == "(":
                depth += 1
            elif value[index] == ")":
                depth -= 1
                if depth == 0:
                    return index
        raise ResponseExpressionError(
            "RESPONSE_EXPRESSION_PARSE_GROUP", "/rimay_jp",
            "expression is missing a closing parenthesis")

    root_end = matching_parenthesis(body, expression_start) \
        if expression_start >= 0 else -1
    has_condition_expression = (
        expression_start >= 0 and body[root_end + 1:].startswith("、")
    )

    def leaf_end(value: str, position: int) -> int:
        depth = 0
        quoted = False
        index = position
        while index < len(value):
            char = value[index]
            if char == "「":
                quoted = True
            elif char == "」":
                quoted = False
            elif not quoted and char == "(":
                depth += 1
            elif not quoted and char == ")":
                if depth == 0:
                    return index
                depth -= 1
            elif not quoted and depth == 0:
                if value.startswith(" かつ ", index) or \
                        value.startswith(" または ", index):
                    return index
            index += 1
        return len(value)

    response_leaf_surfaces: list[str] = []

    def parse_response_leaf(value: str, position: int) -> tuple[dict, int]:
        end = leaf_end(value, position)
        leaf = value[position:end].strip()
        if not leaf:
            raise ResponseExpressionError(
                "RESPONSE_EXPRESSION_PARSE_LEAF", "/rimay_jp/response_expression",
                "Japanese Atomic Response is empty")
        canonical, findings = normalize(leaf + "。", "REQ-JP-LEAF")
        if is_blocked(findings):
            raise ResponseExpressionError(
                "RESPONSE_EXPRESSION_PARSE_LEAF", "/rimay_jp/response_expression",
                f"Japanese Atomic Response is not controlled: {[f['code'] for f in findings]}")
        response_leaf_surfaces.append(leaf)
        return canonical["rimay_core"]["response"], end

    def parse_response_surface(value: str) -> tuple[dict, str]:
        if value.startswith("次の動作を実行する"):
            block_leaf_surfaces: list[str] = []

            def parse_block_leaf(text: str, position: int) -> tuple[dict, int]:
                delimiter = text.find(" ; ", position)
                end = len(text) if delimiter < 0 else delimiter
                leaf = text[position:end].strip()
                canonical, findings = normalize(leaf + "。", "REQ-JP-BLOCK-LEAF")
                if is_blocked(findings):
                    raise ResponseBlockError(
                        "RESPONSE_BLOCK_PARSE_RESPONSE",
                        "/rimay_jp/response_block",
                        f"Japanese Atomic Response is not controlled: "
                        f"{[f['code'] for f in findings]}")
                block_leaf_surfaces.append(leaf)
                return canonical["rimay_core"]["response"], end

            block = parse_rendered_response_block(
                value, parse_block_leaf, language="ja")
            if not block_leaf_surfaces:
                raise ResponseBlockError(
                    "RESPONSE_BLOCK_EMPTY", "/rimay_jp/response_block",
                    "Response Block has no Atomic Response")
            return {"response_block": block}, block_leaf_surfaces[0]
        if value.startswith("("):
            expression = parse_rendered_response_expression(
                value, parse_response_leaf, language="ja")
            if not response_leaf_surfaces:
                raise ResponseExpressionError(
                    "RESPONSE_EXPRESSION_PARSE_LEAF", "/rimay_jp/response_expression",
                    "Response expression has no Atomic Response")
            return {"response_expression": expression}, response_leaf_surfaces[0]
        canonical, findings = normalize(value + "。", "REQ-JP-RESPONSE")
        if is_blocked(findings):
            raise ResponseExpressionError(
                "RESPONSE_EXPRESSION_PARSE_LEAF", "/rimay_jp/response",
                f"Japanese Atomic Response is not controlled: {[f['code'] for f in findings]}")
        return {"response": canonical["rimay_core"]["response"]}, value

    if flat_multi_value_condition:
        response_start = comma_positions[-1] + 1
        prefix = body[:response_start]
        response_surface = body[response_start:]
        response_value, first_response_leaf = parse_response_surface(response_surface)
        base, findings = normalize(prefix + first_response_leaf + "。", "REQ-JP-PARSE")
        if is_blocked(findings):
            raise ConditionExpressionError(
                "MULTI_VALUE_PARSE_LEAF", "/rimay_jp/conditions/0",
                f"Japanese Multi-value condition is not controlled: "
                f"{[f['code'] for f in findings]}")
        core = base["rimay_core"]
        core.pop("response", None)
        core.update(response_value)
        return core

    if has_condition_expression:
        prefix = body[:expression_start]
        condition_surface = body[expression_start:root_end + 1]
        response_surface = body[root_end + 2:]
        response_value, first_response_leaf = parse_response_surface(response_surface)
        condition_leaf_cores: list[dict] = []

        def parse_condition_leaf(value: str, position: int) -> tuple[dict, int]:
            end = leaf_end(value, position)
            leaf = value[position:end].strip()
            canonical, findings = normalize(
                prefix + leaf + "、" + first_response_leaf + "。",
                "REQ-JP-CONDITION-LEAF",
            )
            if is_blocked(findings) or not canonical["rimay_core"].get("conditions"):
                raise ConditionExpressionError(
                    "CONDITION_EXPRESSION_PARSE_LEAF",
                    "/rimay_jp/condition_expression",
                    f"Japanese condition is not controlled: {[f['code'] for f in findings]}")
            condition_leaf_cores.append(canonical["rimay_core"])
            return canonical["rimay_core"]["conditions"][0], end

        condition_expression = parse_rendered_condition_expression(
            condition_surface, parse_condition_leaf, language="ja")
        if not condition_leaf_cores:
            raise ConditionExpressionError(
                "CONDITION_EXPRESSION_PARSE_LEAF",
                "/rimay_jp/condition_expression", "Condition expression has no leaf")
        core = condition_leaf_cores[0]
        core.pop("conditions", None)
        core.pop("response", None)
        core["condition_expression"] = condition_expression
        core.update(response_value)
        return core

    # The first parenthesized root is a Response expression. Preserve the legacy
    # scope/condition prefix by normalizing it with the first Atomic Response.
    response_start = block_start if block_start >= 0 else expression_start
    prefix = body[:response_start]
    response_surface = body[response_start:]
    response_value, first_response_leaf = parse_response_surface(response_surface)
    base, findings = normalize(prefix + first_response_leaf + "。", "REQ-JP-PARSE")
    if is_blocked(findings):
        raise ResponseExpressionError(
            "RESPONSE_EXPRESSION_PARSE_LEAF", "/rimay_jp",
            f"Japanese scope or condition is not controlled: {[f['code'] for f in findings]}")
    core = base["rimay_core"]
    core.pop("response", None)
    core.update(response_value)
    return core
