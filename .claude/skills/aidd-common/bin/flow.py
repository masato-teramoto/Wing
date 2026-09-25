"""Flow Executor — flow を展開し、イベントを並べる。

**この層は gate を知らない。** 扱うのは「どの flow の、どのイベントか」だけで、
イベントの前後に何が差さっているか（`gates.yaml`）は触らない。ゲートを足しても
この層は変わらない。

`flows`（flow の並び）は**記述順に flow へ展開する。入れ子は 1 段まで**であり、
`flow_order` に `flows` の名前は書けない（`config.py` が読み込み時に落とす）。

**この層は繰り返しを知らない。** feature ごとに何度呼ぶか・どの順で呼ぶかは
呼び出し側（コマンドの SKILL.md）が決める。この層はその 1 回ぶん、
**`item`（feature 名など）でスコープされたイベントの並び**を返すだけである。
`item` が無い呼び出しはこれまでどおり 1 回だけ走る。

ログは **`sub_phase_id` まで**を埋める。単位は「1 回の呼び出しで 1 つのイベント」であり、
そのイベント本体と、差さったゲートは同じ `sub_phase_id` を持つ。
"""

import log as log_module


class EventUnit:
    """1 つの flow の 1 つのイベント（`item` でスコープされた 1 回ぶん）。"""

    __slots__ = ("call", "flow", "event", "index", "item")

    def __init__(self, call, flow, event, index, item=None):
        self.call = call
        self.flow = flow
        self.event = event
        self.index = index
        self.item = item

    @property
    def scope(self):
        """状態ストア上でのイベントの同一性。gate の unit key の前半になる。

        **`call` を含めない。** 同じ flow は、どの `call` から呼ばれても同じ記録を指す。
        **`item` を含める。** feature ごとに呼ばれるイベントは、feature ごとに別の記録になる
        （`--item` を付けずに呼べば、これまでどおり 1 本の記録になる）。
        """
        return "%s/%s[%s]" % (self.flow.name, self.event.name, self.item if self.item is not None else "-")

    @property
    def done_key(self):
        """このイベントが最後まで（差さったゲートまで）通ったことを表す印。"""
        return self.scope + "::event"

    def label(self):
        if self.item is None:
            return "%s / %s" % (self.flow.name, self.event.name)
        return "%s / %s [%s]" % (self.flow.name, self.event.name, self.item)


def plan(config, call, item=None):
    """`call` の名前を、実行順のイベントの列にする（`item` でスコープする）。"""
    units = []
    index = 0
    for flow in config.flow_order(call):
        for event_name in flow.event_order:
            units.append(EventUnit(call, flow, config.event(event_name), index, item))
            index += 1
    return units


def pending(config, call, state, item=None):
    """まだ通っていないイベントを、順序を保ったまま返す。"""
    return [unit for unit in plan(config, call, item) if state.result_of(unit.done_key) != "ok"]


class FlowExecutor:
    """イベントを並べ、1 件の開始と終了を記録する。

    **gate を知らない。** そのイベントの前後で何が実行されるかは Event Executor の担当であり、
    この層は「どのイベントに入ったか」「それが確定したか」だけを見る。
    """

    def __init__(self, config, state, logger=None, trace=None):
        self.config = config
        self.state = state
        self.logger = logger
        self.trace = trace

    def plan(self, call, item=None):
        return plan(self.config, call, item)

    def pending(self, call, item=None):
        return pending(self.config, call, self.state, item)

    # --- イベント 1 件の境界 ---------------------------------------------

    def enter(self, unit):
        """イベントに入る時。"""
        if self.logger is None or self.trace is None:
            return
        if self.trace.key_of("sub_phase") == unit.scope:
            return
        # The next event is entered only after the previous one completed.
        self.leave("成功")
        self.trace.open_slot("sub_phase", unit.scope, unit.event.name)
        self.trace.clear_carry()
        self._emit(
            log_module.INFO,
            log_module.compose(
                log_module.START,
                unit.event.name,
                (
                    ("type", unit.event.run.type),
                    ("item", unit.item),
                    ("ゲート", self._gate_count(unit)),
                ),
            ),
        )

    def leave(self, result):
        """そのイベントが確定した時点。**途中で失敗しても `終了` 行は必ず出す。**"""
        if self.logger is None or self.trace is None:
            return
        if self.trace.key_of("sub_phase") is None:
            return
        carry = dict(self.trace.carry)
        label = self.trace.label_of("sub_phase") or self.trace.key_of("sub_phase")
        self._emit(
            log_module.end_level(
                result=result, findings=carry.get("指摘"), runs=carry.get("回数")
            ),
            log_module.compose(
                log_module.END,
                label,
                (
                    ("結果", result),
                    ("status", carry.get("status")),
                    ("指摘", carry.get("指摘")),
                    ("回数", carry.get("回数")),
                ),
            ),
        )
        self.trace.close_slot("sub_phase")
        self.trace.clear_carry()

    def _gate_count(self, unit):
        """`ゲート=<start 本数>+<end 本数>`。差し込みの本数を 1 行で読めるようにする。"""
        start = len(self.config.gates_for(unit.event.name, "start"))
        end = len(self.config.gates_for(unit.event.name, "end"))
        return "%d+%d" % (start, end)

    def _emit(self, level, detail):
        self.logger.write(
            level,
            detail,
            orchestrator_id=self.trace.orchestrator_id,
            phase_id=self.trace.id_of("phase"),
            sub_phase_id=self.trace.id_of("sub_phase"),
        )
