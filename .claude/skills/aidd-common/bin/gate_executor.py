"""Gate — アクションの HookPoint（start / end）で検査を実行する。

    ActionExecutor → HookPoint → GateResolver → GateRepository → GateDefinition[]
                   → GateExecutor.execute(GateInvocation) → GateResult

| 部品 | 責務 |
|---|---|
| GateResolver | 今のアクション・HookPoint に適用するゲートを、記述順に解決する（Repository から引く） |
| GateInvocation | 1 本のゲートの実行に要るもの（GateDefinition、HookPoint、差し先のアクション、実行の Unit） |
| GateExecutor | ゲートの Run を実行して GateResult を返す（適用の条件 `when` は持たない。判断はゲート script 自身が行う） |
| GateResult | 3 値（ok / fail / wait）と、ホストへの emit。detail を持つ |

HookPoint は差し込み位置であり、ゲートそのものではない。**同じ差し口のゲートは記述順に
直列で走る。並列にしない。** ゲートが失敗したら、ActionExecutor はそこで返す。
**ゲートはゲートを持たない。** 入れ子が無いため、再帰も深さ制限も要らない。
"""

from run_dispatcher import OK, PENDING, Outcome, Unit


class GateResult(Outcome):
    """ゲート 1 本の結果。3 値（ok / fail / wait）と emit、PENDING（未実行）を取る。"""

    __slots__ = ()


class GateInvocation:
    __slots__ = ("gate", "hook_point", "action", "unit")

    def __init__(self, gate, hook_point, action, unit):
        self.gate = gate              # GateDefinition
        self.hook_point = hook_point  # start / end
        self.action = action          # 差し先の ActionDefinition（参照してよいメタ情報）
        self.unit = unit              # 状態ストア上の同一性とログを持つ実行の単位


class GateResolver:
    def __init__(self, definitions):
        self.definitions = definitions

    def resolve(self, step, hook_point):
        """アクション 1 件（ActionStep）の HookPoint に適用するゲートを、記述順の GateInvocation にする。"""
        action = step.action
        return [
            GateInvocation(
                gate,
                hook_point,
                action,
                Unit(step.scope, "%s.%s" % (hook_point, gate.name), gate.run, gate.name, step.flow.name,
                     action.name, step.item, gate.name, hook_point, gate.target_review),
            )
            for gate in self.definitions.gates.find(action.name, hook_point)
        ]


class GateExecutor:
    def __init__(self, dispatcher):
        self.dispatcher = dispatcher
        self.state = dispatcher.state

    def execute(self, invocation, execute=True):
        """ゲート 1 本を実行する。`execute` が False なら、済んでいなければ PENDING を返す。"""
        unit = invocation.unit
        if self.state.result_of(unit.key) == OK:
            return GateResult(OK, unit)
        if not execute:
            return GateResult(PENDING, unit)
        outcome = self.dispatcher.run(unit)
        return GateResult(outcome.status, outcome.unit, outcome.detail)
