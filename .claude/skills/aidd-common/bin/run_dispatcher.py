"""RunDispatcher — 1 つの Unit（アクション本体 1 回、またはゲート 1 本）の Run を実行する。

ActionExecutor（アクション本体）と GateExecutor（ゲート）が共用する、最下層の実行部品である。
**この層は順序もゲートも知らない。** 受け取った 1 つの Unit について、

- 済んでいれば（状態ストアの最後の結果が ok）実行しない
- `type` ごとに実行し（script / command は子プロセス、skill はホストへ emit）
- 結果を状態ストアへ記録し、`開始` / `終了` のログを書く

だけを行う。結果は 3 値（ok / fail / wait）と、ホストへ渡す emit である。

| 値 | 意味 | 上位層の扱い |
|---|---|---|
| `ok` | 成功 | 次へ進む |
| `fail` | 失敗 | その flow を終える |
| `wait` | 人間待ち | 状態を保存して止まる |
| `emit` | ホストのエージェントが実行する | 「次にやること」を返して止まる |

ログは **`event_id` まで**を埋める（`orchestrator_id` / `phase_id` / `sub_phase_id` は
渡されたものをそのまま持ち回り、この層で書き足さない。ログの項目名は保存形式のため変えない）。
`event_id` は `開始` で採番し、`終了` / `失敗` で同じ値を使う。**リトライは 1 回ごとに `開始` と
`終了` を出し、`event_id` も毎回別**である（まとめると回数が消え、「リトライして成功した」を
warn で拾えなくなる）。
"""

import json
import os
import re
import shlex
import subprocess
import sys

import definitions as definitions_module
import log as log_module

OK = "ok"
FAIL = "fail"
WAIT = "wait"
EMIT = "emit"
PENDING = "pending"   # 実行せずに未了の unit を探すときだけ使う内部値

# script / command が「人間待ち」を表すために使う終了コード。
WAIT_EXIT_CODE = 10

# script / command が 終了 行へ載せたいキーを渡すための行。
# ランナーは中身を解釈せず、`キー=値` をそのまま detail に並べる。
AIDD_LOG = re.compile(r"^\s*AIDD-LOG:\s*(.+)$", re.MULTILINE)


def expand(text, flow, action, item=None, gate=None):
    """`{flow}` / `{action}` / `{item}` / `{gate}` を差し替える。"""
    if not isinstance(text, str):
        return text
    for name, value in (("flow", flow), ("action", action), ("item", item), ("gate", gate)):
        if value is not None:
            text = text.replace("{%s}" % name, str(value))
    return text


class Outcome:
    __slots__ = ("status", "unit", "detail", "step")

    def __init__(self, status, unit=None, detail=None, step=None):
        self.status = status
        self.unit = unit
        self.detail = detail
        self.step = step          # 止まったアクション（ActionStep）


class Unit:
    """1 回の実行（アクション本体 1 回、またはゲート 1 本）。

    `key` が状態ストア上の同一性である。`scope` はアクション 1 件（`item` を含む）を表し、
    **そのアクションに差さったゲートは同じ `scope` を共有する**
    （`snapshot` と `check_gate_write_scope` が同じ控えを見るのはこのためである）。
    """

    __slots__ = ("scope", "path", "run", "name", "flow", "action", "item", "gate", "hook_point",
                 "target_review")

    def __init__(self, scope, path, run, name, flow, action, item=None, gate=None, hook_point=None,
                 target_review=None):
        self.scope = scope
        self.path = path
        self.run = run
        self.name = name          # gate 名、または action 名
        self.flow = flow
        self.action = action      # 差し先のアクション名（ゲートでも同じ）
        self.item = item          # feature 名など。ループの外なら None
        self.gate = gate          # ゲートなら名前、アクション本体なら None
        self.hook_point = hook_point  # start / end、アクション本体なら None
        self.target_review = target_review  # gate の検査対象（無ければ None。既定は呼出し側が決める）

    @property
    def key(self):
        return "%s::%s" % (self.scope, self.path)

    def target(self):
        return expand(self.run.target, self.flow, self.action, self.item, self.gate)

    def review(self):
        """`target_review` の `{item}` などを差し替えた並び。省略なら None。"""
        if self.target_review is None:
            return None
        return [expand(path, self.flow, self.action, self.item, self.gate) for path in self.target_review]

    def describe(self):
        # 受渡しの形式（JSON のキー）は変えない。`event` はアクション名である。
        return {
            "unit": self.key,
            "flow": self.flow,
            "event": self.action,
            "item": self.item,
            "gate": self.gate,
            "hookPoint": self.hook_point,
            "name": self.name,
            "type": self.run.type,
            "target": self.target(),
            "isAgent": self.run.is_agent,
            "requiresHuman": self.run.requires_human,
            "calls": list(self.run.calls) if self.run.calls else [],
            "targetReview": self.review(),
        }


def _trigger(unit):
    """`契機=<event|start|end>`。**必ず書く**
    （無いとアクション本体の実行とゲートが同じ形で並び、後から区別できない）。"""
    return unit.hook_point or "event"


def _captured(detail):
    """script / command が出した `AIDD-LOG:` 行だけを取り出す。"""
    if not detail:
        return ""
    return " ".join(match.strip() for match in AIDD_LOG.findall(detail))


def target_declarations(definitions):
    """`target_review` を書いたゲートの差し口だけを、定義の値のまま並べる（意味は解釈しない）。

    受渡しの形式（JSON のキー）は変えない。`event` は差し先のアクション名である。
    """
    return [
        {
            "gate": gate.name,
            "event": gate.target_action,
            "hookPoint": gate.hook_point,
            "type": gate.run.type,
            "isAgent": gate.run.is_agent,
            "target_review": list(gate.target_review),
        }
        for gate in definitions.gates.all()
        if gate.target_review is not None
    ]


class RunDispatcher:
    def __init__(self, definitions, state, workdir, state_path, logger=None, trace=None):
        self.definitions = definitions
        self.state = state
        self.workdir = workdir
        self.state_path = state_path
        self.logger = logger
        self.trace = trace

    # --- 1 つの unit -----------------------------------------------------

    def execute(self, unit, execute):
        """Unit を実行して記録する。`execute` が False なら、済んでいなければ PENDING を返す。"""
        if self.state.result_of(unit.key) == OK:
            return Outcome(OK, unit)
        if not execute:
            return Outcome(PENDING, unit)
        return self.run(unit)

    def run(self, unit):
        inline = unit.run.type in ("script", "command")
        if not inline:
            self.begin(unit)
        try:
            status, detail = self._dispatch(unit)
        except Exception as error:  # 例外は握りつぶさない（engine.md §2 エラーログ）
            self.log_failed(unit, "%s: %s" % (type(error).__name__, error))
            self.state.record(unit, FAIL, str(error))
            return Outcome(FAIL, unit, str(error))

        if status == EMIT:
            # 実行はホストのエージェントが行う。`終了` は report で出す。
            return Outcome(EMIT, unit, detail)
        if status == WAIT:
            if not inline:
                self.log_finished(unit, "人間待ち", detail)
            self.state.record(unit, WAIT, detail)
            return Outcome(WAIT, unit, detail)
        if status == FAIL:
            if not inline:
                self.log_finished(unit, "失敗", detail)
            self.state.record(unit, FAIL, detail)
            return Outcome(FAIL, unit, detail)
        if not inline:
            self.log_finished(unit, "成功", detail)
        self.state.record(unit, OK, detail)
        return Outcome(OK, unit, detail)

    # --- ログ（event_id まで）---------------------------------------------

    def _end_keys(self, unit):
        """終了 行に付けるキーは type と isAgent / requiresHuman で決まる（engine.md §7）。"""
        run = unit.run
        if run.type in ("skill", "command"):
            return ("指摘", "回数") if run.is_agent else ("出力",)
        if run.type == "script":
            return ("判断", "判断者", "修正主体", "理由") if run.requires_human else ("終了コード",)
        return ()

    def begin(self, unit, trigger=None):
        """実行の**直前**。ここで `event_id` を採番する。"""
        if self.logger is None or self.trace is None:
            return None
        event_id = self.trace.open_slot("event", unit.key)
        self._write(
            log_module.INFO,
            log_module.compose(
                log_module.START,
                unit.target(),
                (("type", unit.run.type), ("契機", trigger or _trigger(unit))),
            ),
        )
        return event_id

    def log_finished(self, unit, result, detail=None, extra=None):
        """呼び出しが返った時点。`開始` と同じ `event_id` を使う。"""
        if self.logger is None or self.trace is None:
            return
        pairs = dict(log_module.parse_pairs(_captured(detail)))
        pairs.update(extra or {})
        keys = self._end_keys(unit)
        ordered = [("結果", result)] + [(k, pairs.get(k)) for k in keys]
        self.trace.carry_from(pairs)
        self._write(
            log_module.end_level(
                result=result,
                findings=pairs.get("指摘"),
                runs=pairs.get("回数"),
                decision=pairs.get("判断"),
            ),
            log_module.compose(log_module.END, unit.target(), ordered),
            fix_by=pairs.get("修正主体"),
        )
        self.trace.close_slot("event")

    def log_failed(self, unit, reason):
        """例外で落ちた時点。**error にするのはこの行だけ**である。"""
        if self.logger is None or self.trace is None:
            return
        self._write(
            log_module.ERROR,
            log_module.compose(log_module.FAIL, unit.target(), (("理由", reason),)),
        )
        self.trace.close_slot("event")

    def _write(self, level, detail, fix_by=None):
        self.logger.write(
            level,
            detail,
            orchestrator_id=self.trace.orchestrator_id,
            phase_id=self.trace.id_of("phase"),
            sub_phase_id=self.trace.id_of("sub_phase"),
            event_id=self.trace.id_of("event"),
            fix_by=fix_by,
        )

    # --- type による振り分け ----------------------------------------------

    def _dispatch(self, unit):
        run = unit.run
        if run.type == "command":
            return self._run_command(unit)
        if run.type == "skill":
            # isAgent の値に関わらず、Read するか Task で起動するかはホストの仕事。
            return self._hand_over(unit)
        if run.type == "script":
            if run.requires_human:
                return self._run_human_script(unit)
            return self._run_script(unit)
        raise definitions_module.DefinitionError("unit `%s`: 未知の type `%s`" % (unit.key, run.type))

    def _hand_over(self, unit):
        # isAgent: false は Read して実行し、isAgent: true は別コンテキストで 1 件ずつ起動する。
        # どちらもホストのエージェントの仕事であり、ここでは実行しない。
        return EMIT, None

    def _run_command(self, unit):
        return self._spawn(unit, shlex.split(unit.target()), log_attempts=True)

    def _run_script(self, unit):
        path = self._script_path(unit)
        if path is None:
            return FAIL, "script `%s` が見つからない" % unit.target()
        return self._spawn(unit, [sys.executable, path], log_attempts=True)

    def _run_human_script(self, unit):
        # `requiresHuman: true` の script（既定の承認スクリプトを含む）。
        path = self._script_path(unit)
        if path is None:
            return FAIL, "script `%s` が見つからない" % unit.target()
        status, detail = self._spawn(unit, [sys.executable, path], retry=0, timeout=None)
        if status == OK:
            # スクリプトが即座に成功で返っても、engine は回答を生成しない。
            # 人間の停止は必ず「人間待ち」として現れる。
            return WAIT, detail
        return status, detail

    def _script_path(self, unit):
        candidate = self.definitions.resolve(unit.target())
        return candidate if os.path.exists(candidate) else None

    def _spawn(self, unit, argv, retry=None, timeout=None, log_attempts=False):
        run = unit.run
        attempts = (run.retry if retry is None else retry) + 1
        seconds = definitions_module.seconds(run.timeout if timeout is None else timeout)
        last = None
        for attempt in range(attempts):
            # リトライは 1 回ごとに 開始 / 終了 を出し、event_id も毎回別にする。
            if log_attempts:
                self.begin(unit)
            if self.logger is not None:
                # debug — 実行するコマンドと試行回数。既定では出さない。
                self._write(
                    log_module.DEBUG,
                    log_module.compose(
                        log_module.START,
                        unit.target(),
                        (("試行", "%d/%d" % (attempt + 1, attempts)), ("timeout", run.timeout)),
                        " ".join(argv),
                    ),
                )
            try:
                completed = subprocess.run(
                    argv,
                    cwd=self.workdir,
                    env=self._env(unit),
                    timeout=seconds,
                    capture_output=True,
                    text=True,
                    encoding="utf-8",
                )
            except FileNotFoundError:
                reason = "実行できない: %s" % " ".join(argv)
                if log_attempts:
                    self.log_failed(unit, reason)
                return FAIL, reason
            except subprocess.TimeoutExpired:
                last = "timeout (%s)" % run.timeout
                if log_attempts:
                    self.log_finished(unit, "失敗", last, {"終了コード": "timeout"})
                continue
            output = ((completed.stdout or "") + (completed.stderr or "")).strip()
            code = completed.returncode
            if code == 0:
                if log_attempts:
                    self.log_finished(unit, "成功", output, {"終了コード": code})
                return OK, output or None
            if code == WAIT_EXIT_CODE:
                if log_attempts:
                    self.log_finished(unit, "人間待ち", output, {"終了コード": code})
                return WAIT, output or None
            last = output or "終了コード %d" % code
            if log_attempts:
                self.log_finished(unit, "失敗", output, {"終了コード": code})
            if attempt + 1 < attempts:
                continue
        return FAIL, last

    def _env(self, unit):
        env = dict(os.environ)
        env.update(
            {
                # 子プロセス（script/command）の標準出力を UTF-8 に固定する。
                # 既定ロケールが cp932 等の環境（Windows）でも、親側の読み取り
                # （`encoding="utf-8"`）と一致させ、日本語出力の文字化け・
                # UnicodeDecodeError を防ぐ。
                "PYTHONIOENCODING": "utf-8",
                "AIDD_ROOT": self.workdir,
                "AIDD_STATE": self.state_path,
                "AIDD_CONFIG": self.definitions.path,
                "AIDD_FLOW": unit.flow or "",
                # 差し先のアクション名。**ゲートでも、差さったアクションの名前が入る。**
                "AIDD_ACTION": unit.action or "",
                # `--item` で渡された feature 名など。ループの外なら空。
                "AIDD_ITEM": unit.item or "",
                "AIDD_GATE": unit.gate or "",
                "AIDD_HOOK_POINT": unit.hook_point or "",
                "AIDD_UNIT": unit.key,
                # アクション 1 件の同一性。アクション本体と、そこに差さったゲートで同じ値になる。
                "AIDD_ACTION_UNIT": unit.scope,
                # この unit の検査対象（JSON のパス配列）。省略なら空（既定は呼出し側の規則が決める）。
                "AIDD_TARGET_REVIEW": json.dumps(unit.review(), ensure_ascii=False) if unit.target_review else "",
                # 全ゲートの検査対象の宣言（別の差し口の対象を引く規則 script 用。validate と同じ内容）。
                "AIDD_GATE_TARGETS": json.dumps(target_declarations(self.definitions), ensure_ascii=False),
            }
        )
        return env
