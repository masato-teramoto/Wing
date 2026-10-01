"""ActionExecutor — 1 つのアクションを、前後の HookPoint のゲートごと実行する。

**この層は順序を知らない。** 受け取った 1 つのアクション（ActionStep）について

    HookPoint start のゲート（記述順） → アクションの run → HookPoint end のゲート（記述順）

を 1 回ぶんとして直列にたどるだけで、flow にアクションがいくつあるかは扱わない。

- **この層は繰り返しを知らない。** Skill のアクションも script・command のアクションも、呼ばれた
  1 回ぶんを実行して「通過済み」の印を付けるだけである。修正の次の回は、L3 が redo で印を無効にし、
  入口 Skill の手順がもう一度呼ぶ。
- **ゲートの読込み・解決はこの層が持ち、実行は GateExecutor に渡す。**
  HookPoint ごとに GateResolver で適用するゲートを解決し、1 本ずつ GateExecutor へ渡す。
- **ゲートが失敗したら、そこで返す。** 後続のゲートにもアクション本体にも進まない。
- **アクション本体とそこに差さったゲートは同じ `item` を共有する。**
- アクション本体の Run（Skill の起動・script の実行）と入出力の受け渡しは RunDispatcher が行う。

結果は 3 値（ok / fail / wait）と emit である。`type: skill` はこの層では実行できないため
`emit` を返し、上位層が「次にやること」を出力して終了する。
"""

from gate_executor import GateExecutor, GateResolver
from run_dispatcher import OK, Outcome, RunDispatcher, Unit


def fields(step):
    # 状態ストアのキーは保存形式のため `event` のまま（中身はアクション名）。
    return {"flow": step.flow.name, "event": step.action.name, "item": step.item}


class ActionExecutor:
    def __init__(self, definitions, state, workdir, state_path, logger=None, trace=None):
        self.definitions = definitions
        self.state = state
        self.dispatcher = RunDispatcher(definitions, state, workdir, state_path, logger, trace)
        self.gates = GateResolver(definitions)
        self.gate_executor = GateExecutor(self.dispatcher)

    # --- アクション ------------------------------------------------------

    def execute(self, step, execute):
        """アクションの 1 回ぶんを進める。終われば OK、止まれば止まった Outcome（step 付き）を返す。"""
        if self.state.result_of(step.done_key) == OK:
            return Outcome(OK, step=step)
        outcome = self.walk(step, execute)
        if outcome.status == OK:
            # 全 unit が済んでいれば印を付ける（実行せずに再開点を求めるときも、欠けた印を補う）。
            self.state.mark(step.done_key, OK, fields(step))
        outcome.step = step
        return outcome

    # --- 1 回ぶん ----------------------------------------------------------

    def walk(self, step, execute):
        """1 回ぶんを、差さったゲートごとたどる。

        `execute` が False なら、何も実行せずに**次に実行する unit** を返す。
        """
        last = None
        for hook_point in ("start", None, "end"):
            if hook_point is None:
                unit = self.body(step)
                outcome = self.dispatcher.execute(unit, execute)
                if outcome.status != OK:
                    return outcome
                last = unit
                continue
            for invocation in self.gates.resolve(step, hook_point):
                result = self.gate_executor.execute(invocation, execute)
                if result.status != OK:
                    return result
                last = invocation.unit
        return Outcome(OK, last)

    @staticmethod
    def body(step):
        """アクション本体の Unit。"""
        action = step.action
        return Unit(step.scope, "run", action.run, action.name, step.flow.name, action.name, step.item)

    # --- ログ（report で書き戻す分）-----------------------------------------

    def log_finished(self, unit, result, detail=None, extra=None):
        self.dispatcher.log_finished(unit, result, detail, extra)
