"""FlowExecutor — flow の手順（steps）をたどり、アクションを ActionExecutor に渡す。

**この層は gate を知らない。** 扱うのは「どの flow の、どのアクションか」だけで、
アクションの前後に何が差さっているか（`gate.yaml`）は ActionExecutor が扱う。

flow の手順はアクション（ActionStep）か、入れ子の flow（FlowStep）である。FlowStep は同じ手順で
入れ子の flow をたどる（深さの制限は無く、循環は `repositories.py` が読み込み時に落とす）。

**この層は繰り返しを知らない。** 呼ばれた flow の手順を、呼出しの `item` で 1 周たどるだけである。
入れ子の flow は呼び出し元の item を引き継ぐ。feature ごと・修正の繰り返しは Skill の手順が持ち、
繰り返しの 1 回ごとに呼出しを行う（L3 の入口 Skill）。

ログは **`sub_phase_id` まで**を埋める。単位は「1 回の呼び出しで 1 つのアクション」であり、
そのアクション本体と、差さったゲートは同じ `sub_phase_id` を持つ（ログの項目名は保存形式のため変えない）。
"""

import log as log_module
from run_dispatcher import OK, Outcome


class ActionStep:
    """1 つの flow の 1 つのアクション（`item` でスコープされた 1 回ぶん）。"""

    __slots__ = ("call", "flow", "action", "index", "item")

    def __init__(self, call, flow, action, index, item=None):
        self.call = call
        self.flow = flow
        self.action = action
        self.index = index
        self.item = item

    @property
    def scope(self):
        """状態ストア上でのアクションの同一性。gate の unit key の前半になる。

        **`call` を含めない。** 同じ flow は、どの `call` から呼ばれても同じ記録を指す。
        **`item` を含める。** feature ごとに呼ばれるアクションは、feature ごとに別の記録になる
        （`--item` を付けずに呼べば、これまでどおり 1 本の記録になる）。
        """
        return "%s/%s[%s]" % (self.flow.name, self.action.name, self.item if self.item is not None else "-")

    @property
    def done_key(self):
        """このアクションが最後まで（差さったゲートまで）通ったことを表す印（保存形式のため `::event` のまま）。"""
        return self.scope + "::event"

    def label(self):
        if self.item is None:
            return "%s / %s" % (self.flow.name, self.action.name)
        return "%s / %s [%s]" % (self.flow.name, self.action.name, self.item)


def plan(definitions, call, item=None):
    """`call` がたどるアクションを、手順の順に並べる（`item` でスコープする。入れ子の flow も展開する）。

    状態の件数表示と redo の対象の特定に使う。
    """
    return [ActionStep(call, flow, action, index, item)
            for index, (flow, action) in enumerate(definitions.actions_in(call))]


def pending(definitions, call, state, item=None):
    """まだ通っていないアクションを、順序を保ったまま返す。"""
    return [unit for unit in plan(definitions, call, item) if state.result_of(unit.done_key) != "ok"]


class FlowExecutor:
    """flow の手順をたどり、アクション 1 件の開始と終了を記録する。

    **gate を知らない。** そのアクションの前後で何が実行されるかは ActionExecutor の担当であり、
    この層は「どのアクションに入ったか」「それが確定したか」だけを見る。
    """

    def __init__(self, definitions, state, actions, logger=None, trace=None):
        self.definitions = definitions
        self.state = state
        self.actions = actions        # ActionExecutor
        self.logger = logger
        self.trace = trace
        self.on_enter = None          # アクションに入る直前に呼ぶ（Workflow Engine のログ）

    def plan(self, call, item=None):
        return plan(self.definitions, call, item)

    def pending(self, call, item=None):
        return pending(self.definitions, call, self.state, item)

    # --- flow ------------------------------------------------------------

    def execute(self, call, item, execute):
        """呼出し先を 1 周たどる。終われば OK、止まれば止まった Outcome を返す。"""
        return self.run_steps(call, self.definitions.call(call), item, execute)

    def run_steps(self, call, flow, item, execute):
        for index, step in enumerate(flow.steps):
            if step.kind == "action":
                action_step = ActionStep(call, flow, self.definitions.actions.get(step.name), index, item)
                if execute and self.state.result_of(action_step.done_key) != OK:
                    if self.on_enter is not None:
                        self.on_enter(call, action_step)
                    self.enter(action_step)
                outcome = self.actions.execute(action_step, execute)
            else:
                outcome = self.run_steps(call, self.definitions.flows.find(step.name), item, execute)
            if outcome.status != OK:
                return outcome
        return Outcome(OK)

    # --- アクション 1 件の境界 ---------------------------------------------

    def enter(self, unit):
        """アクションに入る時。"""
        if self.logger is None or self.trace is None:
            return
        if self.trace.key_of("sub_phase") == unit.scope:
            return
        # The next action is entered only after the previous one completed.
        self.leave("成功")
        self.trace.open_slot("sub_phase", unit.scope, unit.action.name)
        self.trace.clear_carry()
        self._emit(
            log_module.INFO,
            log_module.compose(
                log_module.START,
                unit.action.name,
                (
                    ("type", unit.action.run.type),
                    ("item", unit.item),
                    ("ゲート", self._gate_count(unit)),
                ),
            ),
        )

    def leave(self, result):
        """そのアクションが確定した時点。**途中で失敗しても `終了` 行は必ず出す。**"""
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
        start = len(self.definitions.gates.find(unit.action.name, "start"))
        end = len(self.definitions.gates.find(unit.action.name, "end"))
        return "%d+%d" % (start, end)

    def _emit(self, level, detail):
        self.logger.write(
            level,
            detail,
            orchestrator_id=self.trace.orchestrator_id,
            phase_id=self.trace.id_of("phase"),
            sub_phase_id=self.trace.id_of("sub_phase"),
        )
