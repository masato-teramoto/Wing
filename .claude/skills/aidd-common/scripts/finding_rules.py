"""指摘の共通ルールのうち、L3 が機械で適用する部分（種類・重大度・同一性キー・節ハッシュ）。

L4 の `finding-rules` Skill（検査役が読む共通ルール）と同じ表を持つ。表が食い違わないことは試験で確かめる。
重大度は AI が出さず、検査役が選んだ種類から、人が事前に決めたこの対応で L3 が決める。
"""
import hashlib
import json
from pathlib import Path
import re

import artifacts

# 種類（6 つ）と重大度。迷ったら上の行を選ぶ（業務に寄せる）。
KINDS = ("業務の欠落・矛盾", "業務のあいまい・不足", "工程・文書の分担", "文書間の参照", "出典・根拠", "書式")
SEVERITY = {
    "業務の欠落・矛盾": "重大",
    "業務のあいまい・不足": "要判断",
    "工程・文書の分担": "軽微",
    "文書間の参照": "軽微",
    "出典・根拠": "軽微",
    "書式": "軽微",
}
SEVERITIES = ("重大", "要判断", "軽微")
# 旧形式の記録（種類を持たない指摘）は、区別がつかないため人に出す。
UNCLASSIFIED = "未分類"
# 機械の検査（L4 の script）の指摘は、検査の種類から種類が決まる。
# 機械の検査（L4 の script）が findings_path に書く観点の名前と、選べる種類（先頭が既定）。
# 名前は main_flow_gate_scripts の findings_stage.append の第 2 引数と一致させる（試験で確かめる）。
MACHINE_KINDS = {
    "format-conformance": ("書式", "文書間の参照"),   # 参照のリンク切れは文書間の参照
    "revision-diff-validity": ("文書間の参照",),
    "sequence-consistency": ("文書間の参照",),
    "dependency-cycle-detection": ("業務の欠落・矛盾",),
}
# AI の推奨として選べる判断。業務の新しい事実が要るものは「質問」として出す。
RECOMMENDATIONS = ("修正", "差戻し", "対応せず進める", "質問")
SUMMARY_LIMIT = 60
# 却下（対応せず進める）の理由の 4 区分。「対象外」「後で決める」だけが「今後も同じ扱い」にできる。
REJECTIONS = ("指摘の誤り", "対象外", "後で決める", "解釈で対応")
REJECTION_ALIASES = {"誤り": "指摘の誤り", "後で": "後で決める", "解釈": "解釈で対応"}
LEARNABLE = ("対象外", "後で決める")
SYSTEM_ACTOR = "system（自動）"
# 工程の境界の表（L4 finding-rules §4）の id。`rule:` の除外の出典はこのどれか。
BOUNDARY_IDS = ("B-01", "B-02", "B-03", "B-04", "TBD")
EXCLUSION_SOURCES = ("rule:", "answer:", "learned:", "verify:", "unchecked:")
# 形式不備のため意味検査から外した節。検査役は除外に `unchecked:<理由>` で記録する。
UNCHECKED = "unchecked:"
FORMAT_GATES = ("format-conformance",)

_ELSEWHERE = re.compile(r"\s*[（(]?\s*ほか\s*\d+\s*か所\s*[）)]?\s*$")
_SPACE = re.compile(r"\s+")


def severity(kind):
    """種類から重大度を決める。種類が無い・不明なら人に出す（要判断）。"""
    return SEVERITY.get(kind, "要判断")


def kind_for(gate, kind):
    """機械の検査の指摘は、その検査で選べる種類に限る（選べない種類なら既定の種類）。それ以外は検査役が選んだ種類。"""
    for name in str(gate).split(" / "):
        if name in MACHINE_KINDS:
            allowed = MACHINE_KINDS[name]
            return kind if kind in allowed else allowed[0]
    return kind


def kind_allowed(gate, kind):
    """まとめた指摘（観点を「 / 」で並べたもの）でも、機械の検査ごとに選べる種類か。"""
    return all(kind in MACHINE_KINDS[name] for name in str(gate).split(" / ") if name in MACHINE_KINDS)


def normalize(text):
    return _SPACE.sub(" ", str(text or "")).strip().casefold()


def parse_location(location):
    """`<案件相対パス> § <節見出し> / <ID>` を (path, heading, ident) に分ける。省略可。"""
    text = _ELSEWHERE.sub("", str(location or "")).strip()
    path, heading, ident = text, "", ""
    if "§" in text:
        path, _, rest = text.partition("§")
        heading, _, ident = rest.partition(" / ")
    elif " / " in text:
        path, _, ident = text.partition(" / ")
    return path.strip(), heading.strip(), ident.strip()


def identity_key(kind, location, subject):
    """同じ指摘を見分けるキー。観点・本文の言い回しは入れない（観点をまたいだ重複もまとめる）。"""
    path, heading, ident = parse_location(location)
    material = [kind or UNCLASSIFIED, normalize(path), normalize(heading), normalize(ident), normalize(subject)]
    return hashlib.sha256(json.dumps(material, ensure_ascii=False).encode("utf-8")).hexdigest()[:16]


def _body(text):
    match = re.match(r"\A---\r?\n.*?\r?\n---\r?\n", text, re.S)
    return text[match.end():] if match else text


def _headings(lines):
    """見出しの (位置, 深さ, 名前)。同じ見出しが複数あれば、出現順に番号を付けて区別する。"""
    heads, seen = [], {""}
    for index, line in enumerate(lines):
        match = re.match(r"^(#{1,6})\s+(.*?)\s*#*\s*$", line)
        if match:
            title = name = match.group(2).strip()
            suffix = 2
            while name in seen:
                name = "%s (%d)" % (title, suffix)
                suffix += 1
            seen.add(name)
            heads.append((index, len(match.group(1)), name))
    return heads


def sections(text, own=False):
    """見出し（`#` で始まる行）ごとの節。値は節の本文（下位の節を含む）。見出しの前は空の見出しに入れる。

    own=True は、節そのものの本文（次の見出しまで。下位の節を含まない）。親の節そのものの文が変わったのか、
    下位の節の変更で親が変わっただけなのかを区別するのに使う。
    """
    lines = _body(text).splitlines()
    heads = _headings(lines)
    result = {"": "\n".join(lines[:heads[0][0]] if heads else lines)}
    for position, (index, level, name) in enumerate(heads):
        later = heads[position + 1:]
        end = (later[0][0] if later else len(lines)) if own else next(
            (other for other, other_level, _ in later if other_level <= level), len(lines))
        result[name] = "\n".join(lines[index:end])
    return result


def digest(text):
    return hashlib.sha256(_SPACE.sub(" ", text).strip().encode("utf-8")).hexdigest()[:16]


def section_hashes(path, own=False):
    """ファイルの節ごとのハッシュ。ファイル全体は `*` に入れる。own=True は節そのものの本文（下位の節を除く）。"""
    file = Path(path)
    if not file.is_file():
        return {}
    text = file.read_text(encoding="utf-8")
    result = {name: digest(body) for name, body in sections(text, own).items()}
    result["*"] = digest(_body(text))
    return result


def find_section(hashes, heading):
    """位置の見出しに当たる節。完全一致がなければ、見出しを含む節を 1 つだけ選ぶ。"""
    if not heading:
        return None
    if heading in hashes:
        return heading
    wanted = normalize(heading)
    matches = [name for name in hashes if name not in ("", "*") and (normalize(name) == wanted or wanted in normalize(name))]
    return matches[0] if len(matches) == 1 else None


def section_hash(root, location):
    """指摘の位置が指す節のハッシュ。節が分からない・ファイルが無ければ `-`。

    ファイル全体のハッシュで代えない。代えると、別の節を変えただけで「再検査で再検出なし」として自動で解消されるため。
    節ハッシュが `-` の指摘は、自動の解消・前回の判断の引き継ぎの対象にしない。
    """
    path, heading, _ = parse_location(location)
    try:
        relative = artifacts.relative_path(path)
    except (ValueError, TypeError):
        return "-"
    hashes = section_hashes(Path(root) / relative)
    if not hashes:
        return "-"
    name = find_section(hashes, heading)
    return hashes[name] if name is not None else "-"


def unchecked_targets(run):
    """この回で意味検査を終えていない対象（形式不備で外した節を持つ対象）。

    検査役が除外に `unchecked:` で記録した節と、機械の形式検査の指摘がある対象を数える。検査していないことを、
    指摘が無くなったことと取り違えないため（自動の解消をしない・承認を止める）。旧形式の回は層（①／①②）で扱うので数えない。
    """
    if not any(f.kind for f in run.findings) and not run.excluded:
        return set()
    def targets_of(location):
        found = {t for t in run.targets if t in location}
        return found or set(run.targets)
    result = set()
    for row in run.excluded:
        if row["除外の出典"].startswith(UNCHECKED):
            result |= targets_of(row["対象箇所"])
    for f in run.findings:
        # 機械の形式検査の指摘がある対象も、検査役が外した節を書き漏らしていても未検査として扱う。
        # ただし、人が「指摘の誤り」と判断したもの・解消したものは外す（形式の不備が無かった）。
        refuted = f.decision == "対応せず進める" and f.category == "指摘の誤り"
        if f.kind and not f.resolved and not refuted and any(gate in FORMAT_GATES for gate in f.gate.split(" / ")):
            result |= targets_of(f.location)
    return result


def rejection(category):
    """却下区分の正規化。空は未記入（旧回答）として許す。"""
    value = REJECTION_ALIASES.get(category, category or "")
    if value and value not in REJECTIONS:
        raise ValueError("却下区分は %s のどれか: %s" % (" / ".join(REJECTIONS), category))
    return value


def recommendation(cell):
    """推奨の欄 `<判断>：<理由>` を (判断, 理由) に分ける。推奨が無ければ ("", "")。"""
    text = str(cell or "").strip()
    if text in ("", "-", "—"):
        return "", ""
    head, reason = (re.split(r"[：:]", text, maxsplit=1) + [""])[:2]
    head = head.strip()
    if head not in RECOMMENDATIONS:
        raise ValueError("推奨は %s のどれか: %s" % (" / ".join(RECOMMENDATIONS), text))
    return head, reason.strip()
