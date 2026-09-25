"""Orchestrator — 呼ばれた名前（`event_handler.call(<名前>)`）を解決し、状態を持つ。

**状態を持つのはこの層だけである。** 下の 2 層は結果を返すだけで、止まる判断をしない。
この層がやることは 3 つしかない。

1. どの flow（または flows）を実行するかを決める
2. Flow Executor が並べたイベントを、順に Event Executor へ渡す
3. 返ってきた 3 値を解釈し、状態を保存する

3 値の解釈は次のとおりで、これ以外の分岐を持たない。

- `ok` … 次のイベントへ進む
- `fail` … **その flow はそこで終わる**（束ねた `flows` の残りにも進まない）
- `wait` … **状態を保存して止まる**（engine は人間の回答を生成しない）

`type: skill` はこの層でも実行できないため、`emit` を受けたら
「次にやること」を呼び出し元へ返して終了する。ホストのエージェントが実行し、
`report` で結果を戻すと、同じ unit は済んだものとして飛ばされる。

**`item` は呼び出し側（コマンドの SKILL.md）が決めて渡すだけである。** この層は
`item` の集合や順序を知らない。同じ `call` を `item` を変えて何度も呼べば、
その回数ぶん最初から（`start` のゲートから）たどり直す。**イベント本体に差さった
ゲートは、そのイベントと同じ `item` で走る**（`flow.py` の `EventUnit.scope` が
`item` を含むため、gate の unit key も自動的に `item` ごとに分かれる）。

ログは **`orchestrator_id` と `phase_id`** を埋める。`orchestrator_id` は `call` 1 回につき
1 つ発行し、**全ログが必ず持つ**。`phase_id` は flow を渡す直前に発行する。
**`error` にするのは `失敗` 行だけ**である（error の件数＝止まった回数という関係を保つ）。
"""

import os
import hashlib
from pathlib import Path

import event as event_module
import flow as flow_module
import log as log_module


class ReportRejected(Exception):
    """engine 自身が実行する unit の結果を外から書き込もうとした。"""


class Result:
    __slots__ = ("status", "event_unit", "outcome", "message")

    def __init__(self, status, event_unit=None, outcome=None, message=None):
        self.status = status  # done / emit / wait / fail
        self.event_unit = event_unit
        self.outcome = outcome
        self.message = message


class Orchestrator:
    def __init__(self, config, state, workdir, logger=None):
        self.config = config
        self.state = state
        self.workdir = workdir
        self.logger = logger
        self.trace = log_module.Trace(state)
        self.flows = flow_module.FlowExecutor(config, state, logger, self.trace)
        self.events = event_module.EventExecutor(
            config, state, workdir, state.path, logger, self.trace
        )
        self.config_hash = hashlib.sha256(b''.join(
            (Path(config.path) / name).read_bytes()
            for name in ('events.yaml', 'flows.yaml', 'gates.yaml'))).hexdigest()
        if logger is not None:
            # 続きの呼び出し（`report` など）は、状態ストアの ID をそのまま使う。
            logger.bind(self.trace.orchestrator_id, self.trace.command)

    # --- 呼ばれた名前を解決する ------------------------------------------

    def select(self, call=None):
        """実行する名前を決める。指定が無ければ状態ストアの `current.call` を使う。"""
        if call:
            self.config.call(call)  # 未定義ならここで落とす
            return call
        for candidate in (self.state.return_to_call, self.state.call):
            if candidate:
                try:
                    self.config.call(candidate)
                except Exception:
                    continue
                return candidate
        return next(iter(self.config.flows)) if self.config.flows else next(iter(self.config.events))

    # --- 再開点 ----------------------------------------------------------

    def pending(self, call, item=None):
        """次に実行する unit を、実行せずに求める。"""
        for event_unit in flow_module.pending(self.config, call, self.state, item):
            outcome = self.events.walk(event_unit, execute=False)
            if outcome.status != event_module.OK:
                return event_unit, outcome
            # 記録上は全 unit が済んでいるのにイベントの印が無い場合は、印を補う。
            self.state.mark(event_unit.done_key, "ok", _fields(event_unit))
        return None, None

    # --- 実行 ------------------------------------------------------------

    def run(self, call, item=None):
        self.state.set_call(call)
        if self.state.return_to_call == call:
            self.state.set_return_to_call(None)
        self.begin_call(call)

        if self.logger is not None:
            # debug — 調査用。既定では出さない。
            remaining = self.flows.pending(call, item)
            self.logger.write(
                log_module.DEBUG,
                log_module.compose(
                    log_module.START,
                    "plan",
                    (("残り", len(remaining)),),
                    " ".join(u.scope for u in remaining),
                ),
                orchestrator_id=self.trace.orchestrator_id,
            )

        for event_unit in self.flows.pending(call, item):
            self._enter_flow(call, event_unit)
            self.flows.enter(event_unit)
            outcome = self.events.walk(event_unit, execute=True)

            if outcome.status == event_module.OK:
                self.state.mark(event_unit.done_key, "ok", _fields(event_unit))
                continue

            if outcome.status == event_module.EMIT:
                self.state.issue(call, outcome.unit, "emit", self.config_hash)
                # コマンド実行は続いている。トレースを開いたまま返す。
                self.state.save()
                return Result("emit", event_unit, outcome)

            if outcome.status == event_module.WAIT:
                self.state.issue(call, outcome.unit, "wait", self.config_hash, outcome.detail)
                return self._close(call, Result("wait", event_unit, outcome), "人間待ち")

            # fail — その flow はそこで終わる。
            self.state.mark(event_unit.done_key, "fail", _fields(event_unit))
            self.state.forget_dispatch()
            return self._close(call, Result("fail", event_unit, outcome), "中断", outcome.detail)

        self.state.forget_dispatch()
        return self._close(call, Result("done"), "完了")

    def dispatch_for(self, call, item=None):
        _, outcome = self.pending(call, item)
        receipt = self.state.data.get("current", {}).get("pending")
        if not receipt or outcome is None:
            return None
        if (receipt.get("call") != call or receipt.get("item") != item
                or receipt.get("unit") != outcome.unit.key
                or receipt.get("config_sha256") != self.config_hash):
            return None
        if receipt.get("status") == "wait" and self.state.result_of(outcome.unit.key) != "wait":
            return None
        return receipt

    # --- ログ（orchestrator_id / phase_id）--------------------------------

    def begin_call(self, call):
        """呼び出しを受理した直後。**1 回の `call` に 1 つ**発行する。
        `type: skill` を出して止まった続きであれば、同じトレースを持ち回る。"""
        if self.logger is None:
            return
        if self.trace.open and self.trace.command == call:
            self.logger.bind(self.trace.orchestrator_id, call)
            return
        self.logger.bind(self.trace.start_command(call), call)
        self.logger.write(
            log_module.INFO,
            log_module.compose(
                log_module.START,
                "call(%s)" % call,
                (
                    ("model", os.environ.get("AIDD_MODEL")),
                    ("version", self.state.release or os.environ.get("AIDD_VERSION")),
                ),
            ),
            orchestrator_id=self.trace.orchestrator_id,
        )

    def _enter_flow(self, call, event_unit):
        """flow を渡す直前。`flows` なら flow ごとに 1 つ発行する。"""
        if self.logger is None:
            return
        key = event_unit.flow.name
        if self.trace.key_of("phase") == key:
            return
        self.flows.leave("成功")
        self._leave_flow("成功")
        self.trace.open_slot("phase", key)
        self.logger.write(
            log_module.INFO,
            log_module.compose(
                log_module.START,
                key,
                (("イベント", len(event_unit.flow.event_order)),),
            ),
            orchestrator_id=self.trace.orchestrator_id,
            phase_id=self.trace.id_of("phase"),
        )

    def _leave_flow(self, result):
        """結果を受け取った時点。**`終了` の level は `結果=失敗` のとき warn、他は info。**"""
        if self.logger is None or self.trace.key_of("phase") is None:
            return
        key = self.trace.key_of("phase")
        self.logger.write(
            log_module.end_level(result=result),
            log_module.compose(
                log_module.END, key, (("結果", result), ("残り", self._remaining(key))),
            ),
            orchestrator_id=self.trace.orchestrator_id,
            phase_id=self.trace.id_of("phase"),
        )
        self.trace.close_slot("phase")

    def _remaining(self, flow_name):
        call = self.state.call
        if not call:
            return None
        try:
            pending = self.flows.pending(call)
        except Exception:
            return None
        return len([u for u in pending if u.flow.name == flow_name])

    # call の結末（呼び出し行の語彙）→ flow / イベントの 結果 の語彙。
    INNER_RESULT = {"完了": "成功", "中断": "失敗", "人間待ち": "人間待ち"}

    def _close(self, call, result, outcome_word, reason=None):
        """呼び出しを離れる。**その `終了` 行は必ず出す**（終了の無い開始＝中断 の判定を保つ）。"""
        inner = self.INNER_RESULT.get(outcome_word, outcome_word)
        self.trace.stash()
        self.flows.leave(inner)
        self._leave_flow(inner)
        if self.logger is not None:
            if outcome_word == "中断":
                self.logger.write(
                    log_module.ERROR,
                    log_module.compose(
                        log_module.FAIL,
                        "call(%s)" % call,
                        (("理由", log_module.short(reason or "-")),),
                    ),
                    orchestrator_id=self.trace.orchestrator_id,
                )
            else:
                self.logger.write(
                    log_module.INFO,
                    log_module.compose(
                        log_module.END,
                        "call(%s)" % call,
                        (
                            ("結果", outcome_word),
                            ("所要", log_module.elapsed(self.trace.started_at)),
                        ),
                    ),
                    orchestrator_id=self.trace.orchestrator_id,
                )
            self.trace.close_command()
        self.state.save()
        return result

    def fail_flow(self, flow_name, reason, return_to):
        """差戻しが確定した時点。**error にする `失敗` 行**である。"""
        if self.logger is None:
            return
        self.logger.write(
            log_module.ERROR,
            log_module.compose(
                log_module.FAIL,
                flow_name,
                (("理由", log_module.short(reason)), ("差戻し先", return_to)),
            ),
            orchestrator_id=self.trace.orchestrator_id,
            phase_id=self.trace.id_of("phase"),
        )

    # --- 結果の書き戻し ---------------------------------------------------

    RESULT_WORDS = {"ok": "成功", "fail": "失敗", "wait": "人間待ち"}

    @staticmethod
    def _reportable(run):
        """ホストのエージェントが実行する（`report` で結果を書き戻せる）run か。

        `type: skill` は isAgent の値に関わらず常にホスト（Read／Task 起動）が実行する。
        `type: script` は `requiresHuman: true` のときだけ、人間の回答を待つために
        `report` を要る（回答を得るまで engine 自身では先に進めない）。
        """
        return run.type == "skill" or (run.type == "script" and run.requires_human)

    def report(self, call, result, note=None, detail=None, item=None, dispatch_id=None):
        """ホストのエージェントが実行した unit の結果を記録する。

        **`script`（`requiresHuman` でないもの）/ `command` の結果は受け付けない。**
        それらは engine 自身が実行し、終了コードで成否を決める。
        外から `ok` と言わせれば機械検査を素通りできてしまう。
        """
        if not dispatch_id:
            raise ReportRejected('report requires --dispatch-id from the actual emit/wait')
        request = {"call":call, "item":item, "result":result, "note":note, "detail":detail}
        previous = self.state.data.get("engine_reports", {}).get(dispatch_id)
        if previous:
            if previous["request"] != request:
                raise ReportRejected('dispatch already reported with different content')
            return previous["unit"]
        receipt = self.dispatch_for(call, item)
        if not receipt or receipt["id"] != dispatch_id:
            raise ReportRejected('stale or unissued dispatch; obtain the current emit/wait')
        event_unit, outcome = self.pending(call, item)
        if event_unit is None:
            return None
        unit = outcome.unit
        if not self._reportable(unit.run):
            raise ReportRejected(
                "`%s` は engine が実行する type（%s）であり、結果を外から書き込めない。"
                "`call` を実行し直すこと。" % (unit.key, unit.run.type)
            )
        self._log_report(unit, result, detail)
        self.state.record(unit, result, note)
        if result == "ok":
            # このイベントの残りが無ければ、イベントの印も付ける。
            remaining = self.events.walk(event_unit, execute=False)
            if remaining.status == event_module.OK:
                self.state.mark(event_unit.done_key, "ok", _fields(event_unit))
        self.state.set_call(call)
        self.state.forget_dispatch()
        description = unit.describe()
        self.state.data.setdefault("engine_reports", {})[dispatch_id] = {"request":request, "unit":description}
        self.state.save()
        return description

    def _log_report(self, unit, result, detail):
        """ホストのエージェントが実行した分の `終了` 行。

        `type: skill` は `call` が `開始` で採番した `event_id` をそのまま使う。
        **`requiresHuman: true` の `script` だけは 2 行目として別の `event_id` を採番する**
        （同じ ID で 2 回 `終了` が出ると所要時間の算出が壊れる）。
        """
        if self.logger is None:
            return
        if unit.run.type == "script" and unit.run.requires_human:
            self.trace.open_slot("event", unit.key + "#answer")
        elif self.trace.key_of("event") != unit.key:
            self.trace.open_slot("event", unit.key)
        self.events.log_finished(
            unit, self.RESULT_WORDS.get(result, result), None, log_module.parse_pairs(detail)
        )

    def redo(self, call, flow_name=None, event_name=None, item=None):
        """成功印を無効化し、その範囲を最初からやり直せるようにする。履歴は保持する。

        `item` を渡せば、その `item` の成功印だけを無効化する。渡さなければ、
        （`flow_name` / `event_name` に一致する）**そのイベントの全 `item` の成功印**を無効化する
        （feature ごとに呼ばれるイベントは、状態ストアに `item` ごと別の記録として積まれて
        いるため、`plan()` を 1 回たどるだけでは拾いきれない。状態ストア側から名前で拾う）。
        """
        targets = {
            event_unit.event.name
            for event_unit in flow_module.plan(self.config, call)
            if (not flow_name or event_unit.flow.name == flow_name)
            and (not event_name or event_unit.event.name == event_name)
        }
        keys = []
        for entry in self.state.events:
            unit_key = entry.get("unit")
            if not isinstance(unit_key, str) or entry.get("event") not in targets:
                continue
            if item is not None and entry.get("item") != item:
                continue
            keys.append(unit_key)
        removed = self.state.clear(keys)
        self.state.forget_dispatch()
        self.state.set_return_to_call(call)
        self.state.save()
        return removed


def _fields(event_unit):
    return {"flow": event_unit.flow.name, "event": event_unit.event.name, "item": event_unit.item}
