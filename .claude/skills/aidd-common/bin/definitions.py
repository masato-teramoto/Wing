"""Definition Models — 定義ファイルを読み込んだ後の、実行時のモデル。

定義ファイル（YAML）と実行ロジックの結合を弱めるため、読込み・検査は
`repositories.py`、実行は Workflow Engine 以下の部品が行い、この層は値だけを持つ。

| 定義ファイル | モデル |
|---|---|
| `command.yaml` | `CommandDefinition`（`CommandStep` の並び） |
| `flow.yaml` | `FlowDefinition`（`StepDefinition` の並び。アクションか、入れ子の flow） |
| `action.yaml` | `ActionDefinition` |
| `gate.yaml` | `GateDefinition` |

アクションとゲートは同じ `RunDefinition`（何をどう実行するか）を持つ。
フェーズ・feature・承認といった AIDD 固有の語彙は持たない。それらは定義の値として
現れるだけで、ランナーは値の意味を解釈しない。繰り返し（feature ごと・修正）はランナーではなく
Skill の手順が持ち、繰り返しの 1 回ごとに呼出しを行う。
"""

RUN_TYPES = ("command", "script", "skill")
HOOK_POINTS = ("start", "end")

# retry / timeout は定義ファイルに持たせない（スキーマは name / run / 並びだけである）。
# engine の既定値としてここに置き、**requiresHuman: true の run には適用しない**。
DEFAULT_TIMEOUT = "10m"
DEFAULT_RETRY = 0


class DefinitionError(ValueError):
    """定義ファイルがスキーマに合っていない。読み込んだ時点で止める。"""


class RunDefinition:
    """アクションとゲートで共通の「実行のされ方」。

    `type` は「何を実行するか」だけを表す。「どう実行されるか」は
    `isAgent` / `requiresHuman` という独立したフラグで表す（type に混ぜない）。

    | type | 実行のされ方 |
    |---|---|
    | `command` | スラッシュコマンドを実行 |
    | `script` | シェル実行。終了コードが成否。`requiresHuman: true` なら人間に提示して停止する（**retry・timeout を適用しない**） |
    | `skill` | Skill を Read して実行させる。`isAgent: true` なら L0 の実行プロトコルに従ってホストが check-runner を別コンテキストで起動する |

    `calls` は `type: skill` のときだけ意味を持つ。`target` の Skill が内部で
    他の Skill を順に呼ぶ場合の、呼び出し先の名前の一覧（パラメータは持たない）。
    """

    __slots__ = ("type", "target", "is_agent", "requires_human", "calls", "retry", "timeout")

    def __init__(self, type_, target, is_agent=False, requires_human=False, calls=None,
                 retry=DEFAULT_RETRY, timeout=DEFAULT_TIMEOUT):
        self.type = type_
        self.target = target
        self.is_agent = is_agent
        self.requires_human = requires_human
        self.calls = calls
        if requires_human:
            # 人間の停止に retry / timeout は適用しない（engine は回答を生成しない）。
            retry, timeout = 0, None
        self.retry = retry
        self.timeout = timeout

    def __repr__(self):
        flags = "".join(
            f" {label}" for label, on in (("isAgent", self.is_agent), ("requiresHuman", self.requires_human)) if on
        )
        return "RunDefinition(%s, %s%s)" % (self.type, self.target, flags)


class CommandStep:
    """コマンドが順に呼ぶ 1 つの呼出し先（flow・action の名前）。"""

    __slots__ = ("flow",)

    def __init__(self, flow):
        self.flow = flow


class CommandDefinition:
    """Harness が管理するコマンド。`id` は入口 Skill の名前、`command` は利用者が入力する文字列。"""

    __slots__ = ("id", "command", "steps")

    def __init__(self, id_, command, steps):
        self.id = id_
        self.command = command
        self.steps = tuple(steps)

    def __repr__(self):
        return "CommandDefinition(%s)" % self.id


class ActionDefinition:
    """Flow 配下の実行単位。`inputs` / `outputs` は読む入力・書く出力のパスの並び（任意）。

    ランナーは中身を解釈せず、形（空でない文字列の配列・重複なし）だけを検査して
    `validate` の出力に載せる。展開・存在・承認の確認は呼び出し側の規則が行う。
    """

    __slots__ = ("name", "run", "inputs", "outputs")

    def __init__(self, name, run, inputs=(), outputs=()):
        self.name = name
        self.run = run
        self.inputs = tuple(inputs)
        self.outputs = tuple(outputs)

    def __repr__(self):
        return "ActionDefinition(%s)" % self.name


class StepDefinition:
    """flow の 1 手順。`kind` は `action`（ActionStep）か `flow`（FlowStep。入れ子の flow を呼ぶ）。"""

    __slots__ = ("kind", "name")

    def __init__(self, kind, name):
        self.kind = kind
        self.name = name

    def __repr__(self):
        return "StepDefinition(%s: %s)" % (self.kind, self.name)


class FlowDefinition:
    """`flow` ― 手順（アクション・入れ子の flow）の並び。

    `synthetic` はアクション名で直接呼んだときに、その場で組み立てたアクション 1 本の flow。
    登録された flow ではないため、flow の next を問わずに 1 回だけたどる。
    """

    __slots__ = ("name", "steps", "synthetic")

    def __init__(self, name, steps, synthetic=False):
        self.name = name
        self.steps = tuple(steps)
        self.synthetic = synthetic

    @property
    def kind(self):
        return "flow"

    @property
    def action_names(self):
        """この flow が直接持つアクションの名前（入れ子の flow は含めない）。"""
        return [step.name for step in self.steps if step.kind == "action"]


class GateDefinition:
    """アクションの HookPoint（start / end）に差す検査。1 つの差し口につき 1 つ。"""

    __slots__ = ("name", "target_action", "hook_point", "run", "target_review")

    def __init__(self, name, target_action, hook_point, run, target_review=None):
        self.name = name
        self.target_action = target_action
        self.hook_point = hook_point
        self.run = run
        # 適用の条件（when）は持たない。実行するかどうかは呼出し（Skill の手順）と、ゲート script 自身が決める。
        # 差し口ごとの検査対象（案件ルートからの相対パスの並び）。None は省略。
        # L0 は形だけを検査して dispatch と環境変数に載せ、省略時の既定は呼出し側の規則が決める。
        self.target_review = target_review

    def __repr__(self):
        return "GateDefinition(%s, %s, %s)" % (self.name, self.target_action, self.hook_point)


def seconds(timeout):
    """\"10m\" / \"90s\" / \"1h\" を秒に直す。None はそのまま返す。"""
    if timeout is None:
        return None
    text = str(timeout).strip().lower()
    unit = {"s": 1, "m": 60, "h": 3600}
    if text and text[-1] in unit:
        try:
            return int(float(text[:-1]) * unit[text[-1]])
        except ValueError:
            raise DefinitionError("timeout `%s` を秒に直せない" % timeout)
    try:
        return int(text)
    except ValueError:
        raise DefinitionError("timeout `%s` を秒に直せない" % timeout)
