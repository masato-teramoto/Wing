"""Version 2 append-only gate records. Strict tables; stable scope/run identity.

Readers do not mutate evidence. Human decisions, resolutions and approvals are
separate appended blocks, so the original inspection remains unchanged.
"""

from dataclasses import dataclass, field
from datetime import datetime
import html
import json
import re

import artifacts

HEADERS = {
    "実行": ["スコープ", "回数", "実行日時", "実行した層", "対象成果物", "原本SHA256", "指摘件数"],
    "指摘": ["#", "観点", "対象箇所", "指摘内容", "判断", "理由"],
    "差戻し先候補": ["指摘番号", "宛先", "理由"],
    "判断": ["スコープ", "回数", "指摘番号", "判断", "理由", "判断者", "日時"],
    "解消": ["スコープ", "回数", "指摘番号", "再検査スコープ", "再検査回数", "確認者", "日時"],
    "承認": ["スコープ", "回数", "対象成果物", "承認者", "承認日時", "原本SHA256"],
    "確認": ["スコープ", "回数", "確認者", "日時", "原本SHA256"],
    # 承認・確認の時点で残っていた指摘（未対応・対応せず進める）。alpha2 の「承認時の残件」。
    "残件": ["スコープ", "回数", "指摘番号", "判断", "理由", "承認スコープ", "承認回数"],
}
DECISIONS = ("修正", "差戻し", "対応せず進める", "未対応")


def timestamp(value):
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except (ValueError, AttributeError):
        raise ValueError("ISO 8601 timestamp required: %r" % value)
    if parsed.tzinfo is None:
        raise ValueError("timestamp requires timezone")
    return value


def scope_key(value):
    if value in ("phase", "cross"):
        return value
    if isinstance(value, str) and value.startswith("feature:"):
        name = value[len("feature:"):]
        if re.fullmatch(r"[a-z0-9][a-z0-9_-]*", name):
            return value
    raise ValueError("invalid scope: %r" % value)


def positive(value):
    if not re.fullmatch(r"[1-9][0-9]*", str(value)):
        raise ValueError("positive integer required: %r" % value)
    return int(value)


def identity(row):
    return scope_key(row["スコープ"]), positive(row["回数"])


def filled(value):
    """Names and identifiers: no template placeholder anywhere."""
    return bool(value and value.strip() not in ("-", "—") and not re.search(r"<[A-Z][A-Z0-9_]*>", value))


def filled_text(value):
    """Free text (findings, reasons): may mention a placeholder name, e.g. a finding
    about a leftover `<PRODUCT_NAME>`; only a cell that is just a placeholder is unfilled."""
    return bool(value and value.strip() not in ("-", "—") and not re.fullmatch(r"\s*<[A-Z][A-Z0-9_]*>\s*", value))


def cells(line):
    if not line.startswith("|") or not line.endswith("|"):
        raise ValueError("table rows must start/end with |")
    return [html.unescape(x.strip()) for x in line[1:-1].split("|")]


@dataclass
class Finding:
    scope: str
    run: int
    number: int
    gate: str
    location: str
    description: str
    decision: str = ""
    reason: str = ""
    resolved: bool = False

    @property
    def key(self):
        return self.scope, self.run, self.number

    def label(self):
        return "%s / run %s / #%s" % self.key

    @property
    def has_decision(self):
        return self.decision in DECISIONS

    @property
    def needs_reason(self):
        return self.decision in ("対応せず進める", "未対応")

    @property
    def is_carried(self):
        return not self.resolved and self.decision == "未対応"

    @property
    def is_open(self):
        return not self.resolved and (not self.has_decision or self.decision in ("修正", "差戻し"))


@dataclass
class Run:
    scope: str
    number: int
    at: str
    layers: str
    targets: list
    hashes: dict
    count: int
    findings: list = field(default_factory=list)
    returns: list = field(default_factory=list)


@dataclass
class Record:
    phase: str
    runs: list = field(default_factory=list)
    approvals: list = field(default_factory=list)
    blocks: list = field(default_factory=list)
    confirmations: list = field(default_factory=list)
    remaining: list = field(default_factory=list)

    def latest(self, scope):
        return next((run for run in reversed(self.runs) if run.scope == scope), None)

    def relevant(self, scope):
        latest = self.latest(scope)
        if latest is None:
            raise ValueError("scope has no inspection: %s" % scope)
        # 未対応は残件として次回以降のレビューにも持ち越して示す（承認は妨げない）。
        return [finding for run in self.runs if run.scope == scope for finding in run.findings
                if run is latest or finding.is_open or finding.is_carried
                or (finding.needs_reason and not filled_text(finding.reason))]


def table_blocks(text):
    section, rows, header, separator = None, [], None, False
    result = []
    for line in text.splitlines():
        line = line.strip()
        if line.startswith(("## ", "### ")):
            if section in HEADERS:
                if header is None or not separator:
                    raise ValueError("missing table: %s" % section)
                result.append((section, rows))
            section = line.split(" ", 1)[1]
            if section not in HEADERS:
                raise ValueError("unknown record section: %s" % section)
            header, rows, separator = None, [], False
        elif section in HEADERS and line:
            if not line.startswith("|"):
                raise ValueError("unexpected content in %s" % section)
            values = cells(line)
            if header is None:
                if values != HEADERS[section]:
                    raise ValueError("invalid columns in %s" % section)
                header = values
            elif not separator:
                if len(values) != len(header) or not all(re.fullmatch(r":?-{3,}:?", v) for v in values):
                    raise ValueError("invalid separator in %s" % section)
                separator = True
            else:
                if len(values) != len(header):
                    raise ValueError("invalid row width in %s" % section)
                rows.append(dict(zip(header, values)))
    if section in HEADERS:
        if header is None or not separator:
            raise ValueError("missing table: %s" % section)
        result.append((section, rows))
    return result


def parse(text):
    match = re.match(r"\A---\r?\n(.*?)\r?\n---\r?\n", text, re.S)
    if not match:
        raise ValueError("record header missing")
    meta = {}
    for line in match.group(1).splitlines():
        key, sep, value = line.partition(":")
        if not sep or key in meta:
            raise ValueError("invalid record header")
        meta[key] = value.strip().strip('"')
    if meta.get("format_version") != "2":
        raise ValueError("legacy gate record requires explicit scope-aware migration")
    if set(meta) != {"format_version", "phase", "created_at"}:
        raise ValueError("unexpected record header keys")
    timestamp(meta["created_at"])
    if not filled(meta["phase"]):
        raise ValueError("phase missing")
    record = Record(meta["phase"])
    record.blocks = table_blocks(text[match.end():])
    runs, findings = {}, {}
    active, stage = None, None
    for section, rows in record.blocks:
        if section == "実行":
            if len(rows) != 1:
                raise ValueError("one metadata row per inspection required")
            row = rows[0]
            key = identity(row)
            expected = 1 + max((r.number for r in record.runs if r.scope == key[0]), default=0)
            if key in runs or key[1] != expected:
                raise ValueError("non-sequential inspection identity")
            targets, hashes = json.loads(row["対象成果物"]), json.loads(row["原本SHA256"])
            if not isinstance(targets, list) or not targets or len(targets) != len(set(targets)):
                raise ValueError("inspection requires distinct targets")
            for target in targets:
                artifacts.relative_path(target)
            if not isinstance(hashes, dict) or set(hashes) != set(targets) or not all(re.fullmatch(r"[a-f0-9]{64}", h) for h in hashes.values()):
                raise ValueError("inspection hashes do not match targets")
            if row["実行した層"] not in ("①", "②", "①②") or not row["指摘件数"].isdigit():
                raise ValueError("invalid layers or findings count")
            active = Run(*key, timestamp(row["実行日時"]), row["実行した層"], targets, hashes, int(row["指摘件数"]))
            record.runs.append(active)
            runs[key] = active
            stage = "実行"
        elif section == "指摘":
            if active is None or stage != "実行":
                raise ValueError("findings must follow inspection metadata")
            for row in rows:
                number = positive(row["#"])
                if number != len(active.findings) + 1 or row["判断"] or row["理由"]:
                    raise ValueError("findings must be sequential and undecided")
                if not all(filled_text(row[k]) for k in ("観点", "対象箇所", "指摘内容")):
                    raise ValueError("incomplete finding")
                finding = Finding(active.scope, active.number, number, row["観点"], row["対象箇所"], row["指摘内容"])
                findings[finding.key] = finding
                active.findings.append(finding)
            stage = "指摘"
        elif section == "差戻し先候補":
            if active is None or stage != "指摘":
                raise ValueError("return candidates must follow findings")
            for row in rows:
                if (active.scope, active.number, positive(row["指摘番号"])) not in findings or not filled_text(row["宛先"]) or not filled_text(row["理由"]):
                    raise ValueError("invalid return candidate")
            active.returns = rows
            stage = "差戻し先候補"
        elif section in ("判断", "解消"):
            active, stage = None, None
            for row in rows:
                key = (*identity(row), positive(row["指摘番号"]))
                if key not in findings:
                    raise ValueError("unknown finding: %s" % (key,))
                finding = findings[key]
                timestamp(row["日時"])
                if section == "判断":
                    if row["判断"] not in DECISIONS or not filled(row["判断者"]):
                        raise ValueError("invalid human decision")
                    if row["判断"] in ("対応せず進める", "未対応") and not filled_text(row["理由"]):
                        raise ValueError("decision requires a reason")
                    finding.decision, finding.reason, finding.resolved = row["判断"], row["理由"], False
                else:
                    new_key = scope_key(row["再検査スコープ"]), positive(row["再検査回数"])
                    if new_key not in runs or new_key[0] != key[0] or new_key[1] <= key[1] or not filled(row["確認者"]) or finding.decision not in ("修正", "差戻し"):
                        raise ValueError("resolution requires a later inspection and human confirmation")
                    if record.runs.index(runs[new_key]) <= record.runs.index(runs[key[:2]]):
                        raise ValueError("resolution inspection predates the finding")
                    finding.resolved = True
        elif section == "確認":
            active, stage = None, None
            for row in rows:
                key = identity(row)
                if key not in runs or key[0] != "cross" or not filled(row["確認者"]) or json.loads(row["原本SHA256"]) != runs[key].hashes:
                    raise ValueError("cross confirmation requires matching inspection and person")
                timestamp(row["日時"])
                record.confirmations.append(row)
        elif section == "残件":
            active, stage = None, None
            for row in rows:
                key = (*identity(row), positive(row["指摘番号"]))
                if key not in findings or row["判断"] not in ("対応せず進める", "未対応"):
                    raise ValueError("remaining item must reference a decided finding")
                if (scope_key(row["承認スコープ"]), positive(row["承認回数"])) not in runs:
                    raise ValueError("remaining item must reference its approval inspection")
                record.remaining.append(row)
        elif section == "承認":
            active, stage = None, None
            for row in rows:
                key = identity(row)
                target = artifacts.relative_path(row["対象成果物"])
                if key not in runs or target not in runs[key].targets:
                    raise ValueError("approval target not inspected")
                if not filled(row["承認者"]) or row["原本SHA256"] != runs[key].hashes[target]:
                    raise ValueError("approval requires person and matching content hash")
                timestamp(row["承認日時"])
                record.approvals.append(row)
    for run in record.runs:
        if len(run.findings) != run.count:
            raise ValueError("finding count does not match inspection metadata")
    # Empty findings still need their explicit table; missing tables are not zero.
    for index, (section, _) in enumerate(record.blocks):
        if section == "実行" and (index + 1 == len(record.blocks) or record.blocks[index + 1][0] != "指摘"):
            raise ValueError("inspection is missing its findings table")
    return record


def render_table(section, rows, heading=2):
    header = HEADERS[section]
    def cell(value):
        return html.escape(str(value), quote=False).replace("|", "&#124;").replace("\n", "&#10;").replace("\r", "&#13;")
    lines = ["#" * heading + " " + section, "", "| " + " | ".join(header) + " |", "|" + "|".join("---" for _ in header) + "|"]
    lines.extend("| " + " | ".join(cell(row.get(key, "")) for key in header) + " |" for row in rows)
    return "\n".join(lines) + "\n"


def new_header(phase, at):
    timestamp(at)
    return '---\nformat_version: 2\nphase: %s\ncreated_at: %s\n---\n\n# ゲート記録\n' % (phase, at)
