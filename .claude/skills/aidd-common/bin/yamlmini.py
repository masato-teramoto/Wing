"""設定ファイル（events.yaml / flows.yaml / gates.yaml）を読むための YAML サブセットパーサ。

PyYAML が入っていない環境でもランナーが動くようにするための代替であり、
**設定ファイルが使う範囲だけ**を解釈する。次に挙げる以外の YAML 機能は扱わない。

- ブロックマッピング（インデントによる入れ子）
- ブロックシーケンス（`- ` 始まり。`- id: x` のように同じ行でマッピングを開始する形を含む）
- フローマッピング `{ a: b }` とフローシーケンス `[a, b]`
- スカラー（素の文字列 / 引用符付き文字列 / 整数 / 真偽値 / null）
- `#` 以降のコメントと空行

アンカー・別名・複数行スカラー・複数ドキュメント・タグは**解釈せずエラーにする**。
これらを設定ファイルで使わないこと自体が制約である。
"""

import re

_TRUE = {"true", "yes", "on"}
_FALSE = {"false", "no", "off"}
_NULL = {"", "null", "~"}


class YamlError(ValueError):
    pass


def load(text):
    lines = _strip(text)
    if not lines:
        return None
    if len(lines) == 1 and lines[0][1] == '[]':
        return []
    value, index = _parse_block(lines, 0, lines[0][0])
    if index != len(lines):
        raise YamlError("行 %d: インデントが揃っていない" % (lines[index][2],))
    return value


# --- 前処理 -------------------------------------------------------------


def _strip(text):
    """(インデント幅, 本文, 元の行番号) の列にする。空行とコメント行は落とす。"""
    out = []
    for number, raw in enumerate(text.splitlines(), start=1):
        if raw.lstrip().startswith("#"):
            continue
        body = _cut_comment(raw).rstrip()
        if not body.strip():
            continue
        if "\t" in body[: len(body) - len(body.lstrip())]:
            raise YamlError("行 %d: インデントにタブを使えない" % number)
        if body.lstrip().startswith(("&", "*", "---", "...")):
            raise YamlError("行 %d: 扱えない YAML 機能（アンカー・別名・複数ドキュメント）" % number)
        out.append((len(body) - len(body.lstrip()), body.strip(), number))
    return out


def _cut_comment(raw):
    """引用符とフロー記法の外にある `#` 以降を落とす。"""
    quote = None
    for i, ch in enumerate(raw):
        if quote:
            if ch == quote:
                quote = None
        elif ch in "\"'":
            quote = ch
        elif ch == "#" and (i == 0 or raw[i - 1] in " \t"):
            return raw[:i]
    return raw


# --- ブロック構造 -------------------------------------------------------


def _parse_block(lines, index, indent):
    if lines[index][1].startswith("- "):
        return _parse_sequence(lines, index, indent)
    return _parse_mapping(lines, index, indent)


def _parse_sequence(lines, index, indent):
    items = []
    while index < len(lines):
        column, body, number = lines[index]
        if column < indent:
            break
        if column > indent:
            raise YamlError("行 %d: シーケンスのインデントが揃っていない" % number)
        if not body.startswith("- "):
            break
        rest = body[2:].strip()
        inline_indent = column + 2
        if _is_key(rest):
            # `- id: x` — 同じ行からマッピングが始まる
            synthetic = [(inline_indent, rest, number)] + lines[index + 1 :]
            value, used = _parse_mapping(synthetic, 0, inline_indent)
            items.append(value)
            index += used
        else:
            items.append(_scalar(rest, number))
            index += 1
    return items, index


def _parse_mapping(lines, index, indent):
    mapping = {}
    while index < len(lines):
        column, body, number = lines[index]
        if column < indent:
            break
        if column > indent:
            raise YamlError("行 %d: マッピングのインデントが揃っていない" % number)
        if body.startswith("- "):
            break
        key, raw = _split_key(body, number)
        if key in mapping:
            raise YamlError("行 %d: キー `%s` が重複している" % (number, key))
        if raw:
            mapping[key] = _scalar(raw, number)
            index += 1
            continue
        # 値は次行以降のブロック
        if index + 1 >= len(lines):
            mapping[key] = None
            index += 1
            continue
        child_column = lines[index + 1][0]
        if child_column > column or (child_column == column and lines[index + 1][1].startswith("- ")):
            value, index = _parse_block(lines, index + 1, child_column)
            mapping[key] = value
        else:
            mapping[key] = None
            index += 1
    return mapping, index


_KEY = re.compile(r"^(?:\"[^\"]*\"|'[^']*'|[^\s:{}\[\],]+)\s*:(?:\s|$)")


def _is_key(text):
    return bool(_KEY.match(text))


def _split_key(body, number):
    match = _KEY.match(body)
    if not match:
        raise YamlError("行 %d: `キー: 値` の形になっていない (%s)" % (number, body))
    head = match.group(0)
    key = head.rstrip().rstrip(":").strip()
    return _unquote(key), body[len(head) :].strip()


# --- スカラーとフロー記法 -----------------------------------------------


def _scalar(text, number):
    text = text.strip()
    if text.startswith("{"):
        value, rest = _flow(text, number)
        if rest.strip():
            raise YamlError("行 %d: フローマッピングの後に余りがある" % number)
        return value
    if text.startswith("["):
        value, rest = _flow(text, number)
        if rest.strip():
            raise YamlError("行 %d: フローシーケンスの後に余りがある" % number)
        return value
    return _plain(text)


def _plain(text):
    if len(text) >= 2 and text[0] == text[-1] and text[0] in "\"'":
        return text[1:-1]
    lowered = text.lower()
    if lowered in _NULL:
        return None
    if lowered in _TRUE:
        return True
    if lowered in _FALSE:
        return False
    if re.fullmatch(r"[+-]?\d+", text):
        return int(text)
    if re.fullmatch(r"[+-]?\d+\.\d+", text):
        return float(text)
    return text


def _unquote(text):
    if len(text) >= 2 and text[0] == text[-1] and text[0] in "\"'":
        return text[1:-1]
    return text


def _flow(text, number):
    """先頭の `{` / `[` から対応する閉じ括弧までを読み、(値, 残り) を返す。"""
    opener = text[0]
    closer = "}" if opener == "{" else "]"
    body, rest = _balanced(text, opener, closer, number)
    parts = _split_top(body, number)
    if opener == "[":
        return [_scalar(p, number) for p in parts if p.strip()], rest
    mapping = {}
    for part in parts:
        if not part.strip():
            continue
        key, raw = _split_key(part.strip(), number)
        if not raw:
            raise YamlError("行 %d: フローマッピングの `%s` に値が無い" % (number, key))
        mapping[key] = _scalar(raw, number)
    return mapping, rest


def _balanced(text, opener, closer, number):
    depth = 0
    quote = None
    for i, ch in enumerate(text):
        if quote:
            if ch == quote:
                quote = None
            continue
        if ch in "\"'":
            quote = ch
        elif ch == opener:
            depth += 1
        elif ch == closer:
            depth -= 1
            if depth == 0:
                return text[1:i], text[i + 1 :]
    raise YamlError("行 %d: `%s` が閉じていない" % (number, opener))


def _split_top(body, number):
    parts = []
    depth = 0
    quote = None
    start = 0
    for i, ch in enumerate(body):
        if quote:
            if ch == quote:
                quote = None
            continue
        if ch in "\"'":
            quote = ch
        elif ch in "{[":
            depth += 1
        elif ch in "}]":
            depth -= 1
        elif ch == "," and depth == 0:
            parts.append(body[start:i])
            start = i + 1
    parts.append(body[start:])
    return parts
