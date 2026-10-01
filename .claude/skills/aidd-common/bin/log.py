"""統一エンベロープのログ。

**全ログが同じ 7 フィールドである。** 種別は「どの ID まで埋まっているか」で決まり、
ログの型は 1 つしかない。実体は JSONL で、空のフィールドはキーごと省略する。

| フィールド | 内容 |
|---|---|
| `timestamp` | 発生時刻（ISO 8601）。システムが打つ |
| `level` | `info` / `warn` / `error` / `debug`。**重大度であり階層ではない** |
| `orchestrator_id` | トレース ID。コマンド実行単位で 1 つ発行し、**全ログが必ず持つ** |
| `phase_id` | 工程単位（flow 1 本） |
| `sub_phase_id` | イベント 1 件（その event と、そこに差さったゲート） |
| `event_id` | 単発の実行単位（event 1 回） |
| `detail` | 実行内容。先頭語は **開始 / 終了 / 失敗** の 3 語に固定 |

ID は 4 つとも ULID である。**発行するのはその ID を書く層**であり、
上位の ID は渡されたものをそのまま持ち回る。**下の層が上の ID を書き足すことはない。**
親子を辿らせず祖先をすべて並べて持つため、1 行だけで所属が確定し、集計に結合が要らない。
短縮するなら**末尾** 8 桁（先頭 10 桁は時刻部のため同じミリ秒で衝突する）。

出力先と閾値は **`.aidd/logging.yaml`** が持つ（`Settings`）。

`修正主体`（AI 再生成か人手か）だけは、`detail` が自由文で機械集計できないため
**専用のキー `fix_by` としても持つ**。
"""

import datetime
import json
import os
import sys

import repositories as repositories_module
import ulid

INFO = "info"
WARN = "warn"
ERROR = "error"
DEBUG = "debug"

ORDER = {DEBUG: 0, INFO: 1, WARN: 2, ERROR: 3}

# detail の先頭語。この 3 語以外を使わない。
START = "開始"
END = "終了"
FAIL = "失敗"

# 終了 行を warn にする判断の値（§3・§5）。
WARN_DECISIONS = ("差戻し", "対応せず進める", "未対応")


def now():
    return datetime.datetime.now().astimezone().replace(microsecond=0).isoformat()


class LogError(ValueError):
    """設定が壊れている、または出力先を作れない。**実行を止める。**"""


class Settings:
    """`.aidd/logging.yaml` の `output` ブロック。

        output:
          dir: .aidd/logs
          filename: "{trace_id}.log"
          level: info

    | キー | 内容 |
    |---|---|
    | `dir` | 案件ルートからの**相対パス**。絶対パスは使わない（案件を移すと壊れる）。無ければ作り、**作れなければ実行を止める** |
    | `filename` | 使える変数は `{trace_id}` / `{date}` / `{command}` の 3 つ |
    | `level` | **閾値であり配列ではない**（配列にすると warn だけ出して error を落とす設定が書けてしまう） |

    **拡張子は `.log` だが中身は JSONL（1 行 1 JSON）である。**
    """

    PATH = ".aidd/logging.yaml"
    VARIABLES = ("trace_id", "date", "command")

    DEFAULTS = {"dir": ".aidd/logs", "filename": "{trace_id}.log", "level": INFO}

    def __init__(self, directory, filename, level):
        self.dir = directory
        self.filename = filename
        self.level = level

    @classmethod
    def load(cls, root, path=None):
        source = path or os.path.join(root, cls.PATH)
        values = dict(cls.DEFAULTS)
        if os.path.exists(source):
            with open(source, encoding="utf-8") as handle:
                data = repositories_module.parse_yaml(handle.read())
            if not isinstance(data, dict):
                raise LogError("%s のルートはマッピングでなければならない" % source)
            output = data.get("output") or {}
            if not isinstance(output, dict):
                raise LogError("%s: `output` はマッピングでなければならない" % source)
            unknown = set(output) - set(cls.DEFAULTS)
            if unknown:
                raise LogError(
                    "%s: `output` に不明なキーがある: %s" % (source, ", ".join(sorted(unknown)))
                )
            values.update({k: v for k, v in output.items() if v is not None})
        return cls(
            cls._dir(values["dir"], source),
            cls._filename(values["filename"], source),
            cls._level(values["level"], source),
        )

    @staticmethod
    def _dir(value, source):
        if not isinstance(value, str) or not value.strip():
            raise LogError("%s: `output.dir` は文字列で書く" % source)
        value = value.strip()
        if os.path.isabs(value) or (len(value) > 1 and value[1] == ":"):
            # 絶対パスは案件を移すと壊れる。
            raise LogError("%s: `output.dir` は案件ルートからの相対パスで書く（%s）" % (source, value))
        return value

    @classmethod
    def _filename(cls, value, source):
        if not isinstance(value, str) or not value.strip():
            raise LogError("%s: `output.filename` は文字列で書く" % source)
        value = value.strip()
        if os.sep in value or "/" in value:
            raise LogError("%s: `output.filename` にディレクトリを含めない（`dir` で指定する）" % source)
        import re

        for name in re.findall(r"\{([^}]*)\}", value):
            if name not in cls.VARIABLES:
                raise LogError(
                    "%s: `output.filename` に使える変数は %s だけ（`{%s}` は使えない）"
                    % (source, " / ".join("{%s}" % v for v in cls.VARIABLES), name)
                )
        return value

    @staticmethod
    def _level(value, source):
        if isinstance(value, (list, tuple, set)):
            # 配列にすると warn だけ出して error を落とす設定が書けてしまう。
            raise LogError("%s: `output.level` は閾値であり配列ではない" % source)
        if value not in ORDER:
            raise LogError(
                "%s: `output.level` は %s のいずれか（実際: %r）"
                % (source, " / ".join(sorted(ORDER, key=ORDER.get)), value)
            )
        return value

    def resolve(self, root, trace_id=None, command=None):
        """出力先の絶対パス。ディレクトリが無ければ作り、**作れなければ実行を止める**。"""
        directory = os.path.join(root, self.dir)
        try:
            os.makedirs(directory, exist_ok=True)
        except OSError as error:
            raise LogError("ログの出力先 `%s` を作れない: %s" % (self.dir, error))
        name = self.filename.format(
            trace_id=trace_id or "unbound",
            date=datetime.date.today().isoformat(),
            command=command or "unbound",
        )
        return os.path.join(directory, name)


class Logger:
    """JSONL を追記する。**ログ書き込み自体の失敗は握りつぶさず** stderr に出す。

    出力先は `{trace_id}` を含みうるため、**最初の書き込みまで確定しない**。
    トレース ID が決まった時点で `bind()` を呼ぶ。
    """

    def __init__(self, settings, root, min_level=None, echo=False):
        self.settings = settings
        self.root = root
        self.min_level = min_level if min_level in ORDER else settings.level
        self.echo = echo
        self.broken = False
        self.trace_id = None
        self.command = None
        self._path = None

    def bind(self, trace_id=None, command=None):
        """ファイル名に使う値を渡す。値が変わったら出力先も引き直す。"""
        if trace_id and trace_id != self.trace_id:
            self.trace_id, self._path = trace_id, None
        if command and command != self.command:
            self.command, self._path = command, None

    @property
    def path(self):
        if self._path is None:
            self._path = self.settings.resolve(self.root, self.trace_id, self.command)
        return self._path

    def enabled(self, level):
        return ORDER.get(level, 1) >= ORDER[self.min_level]

    def write(self, level, detail, orchestrator_id=None, phase_id=None,
              sub_phase_id=None, event_id=None, fix_by=None):
        if not self.enabled(level):
            return None
        record = {"timestamp": now(), "level": level}
        for key, value in (
            ("orchestrator_id", orchestrator_id),
            ("phase_id", phase_id),
            ("sub_phase_id", sub_phase_id),
            ("event_id", event_id),
        ):
            if value:
                record[key] = value
        record["detail"] = detail
        if fix_by:
            record["fix_by"] = fix_by
        self._append(record)
        return record

    def _append(self, record):
        line = json.dumps(record, ensure_ascii=False)
        if self.echo:
            print(line, file=sys.stderr)
        if self.broken:
            return
        try:
            with open(self.path, "a", encoding="utf-8") as handle:
                handle.write(line + "\n")
        except OSError as error:
            # 「ログ書き込み自体の失敗」は error 相当の事象である。
            # 以降の書き込みは諦めるが、**黙って続けない**。
            self.broken = True
            print("ログを書けない（%s）: %s" % (self.path, error), file=sys.stderr)


# --- detail の組み立て ----------------------------------------------------


def compose(head, subject, pairs=(), free=None):
    """`<先頭語> <主語> キー=値 キー=値 … 自由文` を組み立てる。

    値が空のキーは落とす。自由文は必ず最後に置く。
    """
    parts = ["%s %s" % (head, subject) if subject else head]
    for key, value in pairs:
        if value is None or value == "":
            continue
        parts.append("%s=%s" % (key, _flat(value)))
    if free:
        parts.append(_flat(free))
    return " ".join(parts)


def _flat(value):
    """detail は 1 行である。改行と連続空白を潰す。"""
    return " ".join(str(value).split())


def short(text, limit=80):
    """`理由=<短文>` 用。detail は 1 行であり、長文をそのまま載せない。"""
    flat = _flat(text or "")
    return flat if len(flat) <= limit else flat[: limit - 1] + "…"


def parse_pairs(text):
    """`キー=値` の並びを辞書にする。`AIDD-LOG:` 行と `--detail` の解釈に使う。"""
    pairs = {}
    for token in _flat(text or "").split(" "):
        if "=" in token:
            key, _, value = token.partition("=")
            if key:
                pairs[key] = value
    return pairs


# --- level の決め方（§3・§5）----------------------------------------------


def end_level(result=None, findings=None, runs=None, decision=None):
    """`終了` 行の level。**`error` にするのは `失敗` 行だけ**である
    （error の件数＝止まった回数という関係を崩さない）。"""
    if result == "失敗":
        return WARN
    if _at_least(findings, 1) or _at_least(runs, 2):
        return WARN
    if decision:
        for value in str(decision).replace("/", " ").split():
            if value in WARN_DECISIONS:
                return WARN
    return INFO


def _at_least(value, threshold):
    try:
        return int(value) >= threshold
    except (TypeError, ValueError):
        return False


def elapsed(started_at, ended_at=None):
    """`所要=<m:s>` の値。読めない場合は空を返す。"""
    import datetime

    if not started_at:
        return ""
    try:
        start = datetime.datetime.fromisoformat(started_at)
        end = datetime.datetime.fromisoformat(ended_at) if ended_at else datetime.datetime.now(
            start.tzinfo
        )
    except ValueError:
        return ""
    total = int(max(0, (end - start).total_seconds()))
    return "%dm%02ds" % divmod(total, 60)


# --- トレース（4 つの ID の持ち回り）--------------------------------------


class Trace:
    """状態ストアの `trace` ブロックを読み書きする。

    `aidd.py` は 1 回の呼び出しで終わるが、**コマンド実行は複数回の呼び出しにまたがる**
    （`next` が `skill` を出して止まり、実行後に `report` で戻る）。
    ID をまたいで持ち回れるよう、発行済みの ID は状態ストアに置く。
    """

    def __init__(self, state):
        self.state = state

    @property
    def data(self):
        return self.state.data.setdefault("trace", {})

    def clear(self):
        self.state.data.pop("trace", None)

    # --- コマンド（orchestrator_id）-------------------------------------

    @property
    def orchestrator_id(self):
        return self.data.get("orchestrator_id")

    @property
    def command(self):
        return self.data.get("command")

    @property
    def open(self):
        return bool(self.data.get("open"))

    def start_command(self, command):
        self.state.data["trace"] = {
            "orchestrator_id": ulid.new(),
            "command": command,
            "started_at": now(),
            "open": True,
        }
        return self.data["orchestrator_id"]

    def stash(self):
        """呼び出しを離れる直前に、phase / sub_phase の ID を控える。"""
        # 開いている slot の値だけを控える（`id_of` の控えへのフォールバックを使わない）。
        self.data["last"] = {
            "phase": self._slot("phase").get("id"),
            "sub_phase": self._slot("sub_phase").get("id"),
        }

    def close_command(self):
        self.data["open"] = False

    @property
    def started_at(self):
        return self.data.get("started_at")

    # --- flow（phase_id）／ event（sub_phase_id）／ 1 回の実行（event_id）-----

    def _slot(self, name):
        return self.data.get(name) or {}

    def id_of(self, name):
        """開いている slot の ID。閉じた後は `stash` で控えた値を返す
        （人間待ちで止まった後の `report` が、同じ所属の行を書けるようにするため）。"""
        current = self._slot(name).get("id")
        if current:
            return current
        return (self.data.get("last") or {}).get(name)

    def key_of(self, name):
        return self._slot(name).get("key")

    def open_slot(self, name, key, label=None):
        self.data[name] = {"id": ulid.new(), "key": key, "started_at": now()}
        if label:
            self.data[name]["label"] = label
        return self.data[name]["id"]

    def label_of(self, name):
        return self._slot(name).get("label")

    def close_slot(self, name):
        self.data.pop(name, None)

    def started_at_of(self, name):
        return self._slot(name).get("started_at")

    # --- 終了 行に持ち越す値（指摘・回数・status）------------------------

    @property
    def carry(self):
        return self.data.setdefault("carry", {})

    def carry_from(self, pairs):
        for key in ("指摘", "回数", "status", "結果"):
            if key in pairs:
                self.carry[key] = pairs[key]

    def clear_carry(self):
        self.data.pop("carry", None)
