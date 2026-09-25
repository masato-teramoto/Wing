"""Event Executor — 1 つのイベントを、差さったゲートごと実行する。

**この層は順序を知らない。** 受け取った 1 つのイベントについて

    hookPoint: start のゲート（記述順） → イベントの run → hookPoint: end のゲート（記述順）

を直列にたどるだけで、flow にイベントがいくつあるかは扱わない。

- **同じ差し口のゲートは記述順に直列で走る。並列にしない。**
- **ゲートが失敗したら、そこで返す。** 後続のゲートにもイベントにも進まない。
- **ゲートはゲートを持たない。** 入れ子が無いため、この層に再帰も深さ制限も要らない。
- **イベント本体とそこに差さったゲートは同じ `item` を共有する。** `item` があるイベントを
  呼べば、その前後のゲートも同じ `item` で走る（ゲートを足しても、この対応は変わらない）。

結果は 3 値だけである。

| 値 | 意味 | 上位層の扱い |
|---|---|---|
| `ok` | 成功 | 次へ進む |
| `fail` | 失敗 | その flow を終える |
| `wait` | 人間待ち | 状態を保存して止まる |

`type: skill` はこの層では実行できない（`isAgent: false` なら Read して実行し、
`isAgent: true` なら別コンテキストで起動する。どちらもホストのエージェントの仕事である）。
その場合は `emit` を返し、上位層が「次にやること」を出力して終了する。
`type` が増えても Flow Executor と Orchestrator は変わらない。

ログは **`event_id` まで**を埋める（`orchestrator_id` / `phase_id` / `sub_phase_id` は
渡されたものをそのまま持ち回り、この層で書き足さない）。`event_id` は `開始` で採番し、
`終了` / `失敗` で同じ値を使う。**リトライは 1 回ごとに `開始` と `終了` を出し、`event_id` も毎回別**である
（まとめると回数が消え、「リトライして成功した」を warn で拾えなくなる）。
"""

import os
import re
import shlex
import subprocess
import sys

import config as config_module
import log as log_module

OK = "ok"
FAIL = "fail"
WAIT = "wait"
EMIT = "emit"
PENDING = "pending"   # 実行せずに未了の unit を探すときだけ使う内部値

# script / command が「人間待ち」を表すために使う終了コード。
WAIT_EXIT_CODE = 10

# gate の `when` 条件 script が「この差し口では省略する」を表す終了コード。
# 0 は適用、それ以外は失敗。省略した gate は成功として記録し、detail に省略を残す。
SKIP_EXIT_CODE = 11

# script / command が 終了 行へ載せたいキーを渡すための行。
# ランナーは中身を解釈せず、`キー=値` をそのまま detail に並べる。
AIDD_LOG = re.compile(r"^\s*AIDD-LOG:\s*(.+)$", re.MULTILINE)


class Outcome:
    __slots__ = ("status", "unit", "detail")

    def __init__(self, status, unit=None, detail=None):
        self.status = status
        self.unit = unit
        self.detail = detail


class Unit:
    """1 回の実行（イベント本体 1 回、またはゲート 1 本）。

    `key` が状態ストア上の同一性である。`scope` はイベント 1 件（`item` を含む）を表し、
    **そのイベントに差さったゲートは同じ `scope` を共有する**
    （`snapshot` と `check_gate_write_scope` が同じ控えを見るのはこのためである）。
    """

    __slots__ = ("scope", "path", "run", "name", "flow", "event", "item", "gate", "hook_point", "when")

    def __init__(self, scope, path, run, name, flow, event, item=None, gate=None, hook_point=None, when=None):
        self.scope = scope
        self.path = path
        self.run = run
        self.name = name          # gate 名、または event 名
        self.flow = flow
        self.event = event        # 差し先のイベント名（ゲートでも同じ）
        self.item = item          # feature 名など。ループの外なら None
        self.gate = gate          # ゲートなら名前、イベント本体なら None
        self.hook_point = hook_point  # start / end、イベント本体なら None
        self.when = when          # gate の適用条件 script（無ければ常に適用）

    @property
    def key(self):
        return "%s::%s" % (self.scope, self.path)

    def target(self):
        return expand(self.run.target, self.flow, self.event, self.item, self.gate)

    def describe(self):
        return {
            "unit": self.key,
            "flow": self.flow,
            "event": self.event,
            "item": self.item,
            "gate": self.gate,
            "hookPoint": self.hook_point,
            "name": self.name,
            "type": self.run.type,
            "target": self.target(),
            "isAgent": self.run.is_agent,
            "requiresHuman": self.run.requires_human,
            "calls": list(self.run.calls) if self.run.calls else [],
        }


def _trigger(unit):
    """`契機=<event|start|end>`。**必ず書く**
    （無いとイベント本体の実行とゲートが同じ形で並び、後から区別できない）。"""
    return unit.hook_point or "event"


def _captured(detail):
    """script / command が出した `AIDD-LOG:` 行だけを取り出す。"""
    if not detail:
        return ""
    return " ".join(match.strip() for match in AIDD_LOG.findall(detail))


def expand(text, flow, event, item=None, gate=None):
    """`{flow}` / `{event}` / `{item}` / `{gate}` を差し替える。"""
    if not isinstance(text, str):
        return text
    for name, value in (("flow", flow), ("event", event), ("item", item), ("gate", gate)):
        if value is not None:
            text = text.replace("{%s}" % name, str(value))
    return text


class EventExecutor:
    def __init__(self, config, state, workdir, state_path, logger=None, trace=None):
        self.config = config
        self.state = state
        self.workdir = workdir
        self.state_path = state_path
        self.logger = logger
        self.trace = trace

    # --- 入口 ------------------------------------------------------------

    def walk(self, event_unit, execute):
        """1 つのイベントを、差さったゲートごとたどる。

        `execute` が False なら、何も実行せずに**次に実行する unit** を返す。
        """
        last = None
        for unit in self.units(event_unit):
            outcome = self._step(unit, execute)
            if outcome.status != OK:
                return outcome
            last = unit
        return Outcome(OK, last)

    def units(self, event_unit):
        """`start のゲート → イベント本体 → end のゲート` を記述順に並べる。"""
        event = event_unit.event
        scope = event_unit.scope
        item = event_unit.item
        units = []
        for hook_point in ("start", None, "end"):
            if hook_point is None:
                units.append(
                    Unit(scope, "run", event.run, event.name, event_unit.flow.name, event.name, item)
                )
                continue
            for gate in self.config.gates_for(event.name, hook_point):
                units.append(
                    Unit(
                        scope,
                        "%s.%s" % (hook_point, gate.name),
                        gate.run,
                        gate.name,
                        event_unit.flow.name,
                        event.name,
                        item,
                        gate.name,
                        hook_point,
                        gate.when,
                    )
                )
        return units

    # --- 1 つの unit -----------------------------------------------------

    def _step(self, unit, execute):
        if self.state.result_of(unit.key) == OK:
            return Outcome(OK, unit)
        if not execute:
            return Outcome(PENDING, unit)

        if unit.when:
            skipped, reason = self._condition(unit)
            if skipped is None:
                self.state.record(unit, FAIL, reason)
                return Outcome(FAIL, unit, reason)
            if skipped:
                note = "条件により省略: %s" % (reason or unit.when)
                self.begin_event(unit)
                self.log_finished(unit, "成功", note)
                self.state.record(unit, OK, note)
                return Outcome(OK, unit, note)

        inline = unit.run.type in ("script", "command")
        if not inline:
            self.begin_event(unit)
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

    def begin_event(self, unit, trigger=None):
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
        raise config_module.ConfigError("unit `%s`: 未知の type `%s`" % (unit.key, run.type))

    def _condition(self, unit):
        """`when` script を実行する。(True, 理由) で省略、(False, None) で適用、(None, 理由) で失敗。"""
        path = self.config.resolve(unit.when)
        if not os.path.exists(path):
            return None, "when の script `%s` が見つからない" % unit.when
        try:
            completed = subprocess.run([sys.executable, path], cwd=self.workdir, env=self._env(unit),
                                       capture_output=True, text=True, encoding="utf-8",
                                       timeout=config_module.seconds(config_module.DEFAULT_TIMEOUT))
        except subprocess.TimeoutExpired:
            return None, "when の script が timeout (%s)" % config_module.DEFAULT_TIMEOUT
        except OSError as error:
            return None, "when の script を実行できない: %s" % error
        output = ((completed.stdout or "") + (completed.stderr or "")).strip()
        if completed.returncode == 0:
            return False, None
        if completed.returncode == SKIP_EXIT_CODE:
            return True, output or None
        return None, output or "when の script が失敗した（終了コード %d）" % completed.returncode

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
        candidate = self.config.resolve(unit.target())
        return candidate if os.path.exists(candidate) else None

    def _spawn(self, unit, argv, retry=None, timeout=None, log_attempts=False):
        run = unit.run
        attempts = (run.retry if retry is None else retry) + 1
        seconds = config_module.seconds(run.timeout if timeout is None else timeout)
        last = None
        for attempt in range(attempts):
            # リトライは 1 回ごとに 開始 / 終了 を出し、event_id も毎回別にする。
            if log_attempts:
                self.begin_event(unit)
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
                "AIDD_CONFIG": self.config.path,
                "AIDD_FLOW": unit.flow or "",
                # 差し先のイベント名。**ゲートでも、差さったイベントの名前が入る。**
                "AIDD_EVENT": unit.event or "",
                # `--item` で渡された feature 名など。ループの外なら空。
                "AIDD_ITEM": unit.item or "",
                "AIDD_GATE": unit.gate or "",
                "AIDD_HOOK_POINT": unit.hook_point or "",
                "AIDD_UNIT": unit.key,
                # イベント 1 件の同一性。イベント本体と、そこに差さったゲートで同じ値になる。
                "AIDD_EVENT_UNIT": unit.scope,
            }
        )
        return env
