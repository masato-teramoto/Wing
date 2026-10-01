"""Repositories — 定義ファイルを読み込み、検査し、名前で検索する。

    command.yaml ― どこから入るか : コマンドと、順に呼ぶ呼出し先
    flow.yaml    ― どの順で呼ぶか : 手順（steps）の並び。手順はアクションか、入れ子の flow
    action.yaml  ― 何をするか     : name と Run、任意で inputs / outputs（パスの並び）
    gate.yaml    ― どこに差すか   : target_action と hookPoint で、アクションの前後に差し込む
    （`- hook:` は無い。host の規則は L3 の入口が L0 の host に渡す）

**つながりはすべて名前による参照である。** 名前は 4 ファイルを横断して一意であり、
未定義の名前は**読み込んだ時点でエラーにする**（実行時に見つからないと、検査が黙って
スキップされる）。**gate だけが逆向きに指すため、ゲートを足しても action と flow は変わらない。**

**呼出し先（`call(名前)`）は action を直接指してもよい。** flow.yaml に 1 アクションだけの
flow を量産しないための救済であり、その場でアクション 1 本の flow を組み立てて返すだけで、
名前の登録（4 ファイル横断の一意性）は増やさない。

この層は検索だけを行う。どのコマンドの step かの解決は CommandResolver、
どのゲートを適用するかの判断は GateResolver が行う。繰り返しは Skill の手順が持つ。

**L0 が L3・L4 から読むのは、この 4 ファイルだけである。** Skill・script・agent は、定義に書かれた
名前のファイルがあることだけを確かめ、中身は読まない（合成 Skill の手順と `calls` の一致は
L4 の `check_calls.py` が確かめる）。
"""

import os
import re

from definitions import (
    HOOK_POINTS,
    RUN_TYPES,
    ActionDefinition,
    CommandDefinition,
    CommandStep,
    DefinitionError,
    FlowDefinition,
    GateDefinition,
    RunDefinition,
    StepDefinition,
)

try:  # PyYAML があれば使う。無ければ同梱のサブセットパーサで読む。
    import yaml as _yaml

    def parse_yaml(text):
        """定義ファイルと .aidd/logging.yaml の両方がこれで読む。"""
        return _yaml.safe_load(text)

except ImportError:  # pragma: no cover - 環境依存

    import yamlmini as _yamlmini

    def parse_yaml(text):
        """定義ファイルと .aidd/logging.yaml の両方がこれで読む。"""
        return _yamlmini.load(text)


COMMAND_FILE = "command.yaml"
FLOW_FILE = "flow.yaml"
ACTION_FILE = "action.yaml"
GATE_FILE = "gate.yaml"
FILES = (COMMAND_FILE, FLOW_FILE, ACTION_FILE, GATE_FILE)


class CommandRepository:
    """CommandDefinition を記述順に保持し、id で引く。"""

    def __init__(self, commands):
        self._commands = commands  # {id: CommandDefinition}

    def get(self, command_id):
        try:
            return self._commands[command_id]
        except KeyError:
            raise DefinitionError("command `%s` は %s に無い" % (command_id, COMMAND_FILE))

    def all(self):
        return list(self._commands.values())

    def __contains__(self, command_id):
        return command_id in self._commands


class FlowRepository:
    """FlowDefinition を記述順に保持し、名前で引く。"""

    def __init__(self, flows):
        self._flows = flows  # {name: FlowDefinition}

    def find(self, name):
        return self._flows.get(name)

    def all(self):
        return list(self._flows.values())

    def names(self):
        return list(self._flows)

    def __contains__(self, name):
        return name in self._flows


class ActionRepository:
    """ActionDefinition を記述順に保持し、名前で引く。"""

    def __init__(self, actions):
        self._actions = actions  # {name: ActionDefinition}

    def get(self, name):
        try:
            return self._actions[name]
        except KeyError:
            raise DefinitionError("action `%s` は %s に無い" % (name, ACTION_FILE))

    def all(self):
        return list(self._actions.values())

    def names(self):
        return list(self._actions)

    def __contains__(self, name):
        return name in self._actions


class GateRepository:
    """GateDefinition を記述順に保持し、アクション・HookPoint で候補を引く。"""

    def __init__(self, gates):
        self._gates = gates  # [GateDefinition]（記述順。同じ差し口はこの順で直列に走る）

    def find(self, action_name, hook_point):
        return [gate for gate in self._gates
                if gate.target_action == action_name and gate.hook_point == hook_point]

    def all(self):
        return list(self._gates)


class Definitions:
    """4 つの Repository を束ねる。定義ファイルの置き場（`path`）を相対パスの基準にする。"""

    def __init__(self, root, commands, flows, actions, gates):
        self.root = os.path.abspath(root)
        self.commands = commands
        self.flows = flows
        self.actions = actions
        self.gates = gates

    @property
    def path(self):
        """定義ファイルの置き場（ログと環境変数に載せる）。"""
        return self.root

    def paths(self):
        return [os.path.join(self.root, name) for name in FILES]

    def call(self, name):
        """呼出し先の名前が指すもの。flow または action のいずれでもよい。

        flow.yaml に登録が無くても、action の名前と一致すれば **その場でアクション 1 本の
        flow を組み立てて返す**（登録はしない。計画 1 回・横断検査 1 回のような呼出しがこの経路を使う）。
        """
        found = self.flows.find(name)
        if found is not None:
            return found
        if name in self.actions:
            return FlowDefinition(name, [StepDefinition("action", name)], synthetic=True)
        raise DefinitionError(
            "`%s` は action にも %s にも無い（登録済み flow: %s）"
            % (name, FLOW_FILE, ", ".join(self.flows.names()) or "なし")
        )

    def actions_in(self, name):
        """呼出し先がたどるアクションを、(アクションを直接持つ flow, ActionDefinition) の並びで返す。"""
        result = []

        def walk(flow):
            for step in flow.steps:
                if step.kind == "action":
                    result.append((flow, self.actions.get(step.name)))
                else:
                    walk(self.flows.find(step.name))

        walk(self.call(name))
        return result

    def resolve(self, path):
        """定義ファイルの置き場からの相対パスを絶対パスにする。"""
        if os.path.isabs(path):
            return path
        return os.path.normpath(os.path.join(self.root, path))


# --- 読み込み -------------------------------------------------------------


def config_hash(root):
    """4 ファイルの内容の SHA-256。未回答の emit / wait は、設定が変わっていないときだけ報告できる。"""
    import hashlib
    digest = hashlib.sha256()
    for name in FILES:
        with open(os.path.join(os.path.abspath(root), name), "rb") as handle:
            digest.update(handle.read())
    return digest.hexdigest()


def load(root):
    """`root` に置かれた 4 ファイルを読む。1 つでも欠けていたらエラーにする。"""
    root = os.path.abspath(root)
    raw = {}
    for name in FILES:
        path = os.path.join(root, name)
        if not os.path.exists(path):
            raise DefinitionError("定義ファイル `%s` が無い（置き場: %s）" % (name, root))
        with open(path, encoding="utf-8") as handle:
            raw[name] = _entries(parse_yaml(handle.read()), name)

    names = {}  # 4 ファイル横断の一意性はここで見る
    actions = _load_actions(raw[ACTION_FILE], names)
    flows = _load_flows(raw[FLOW_FILE], names)
    gates = _load_gates(raw[GATE_FILE], names)
    commands = _load_commands(raw[COMMAND_FILE], names)

    definitions = Definitions(root, CommandRepository(commands), FlowRepository(flows),
                              ActionRepository(actions), GateRepository(gates))
    _check_references(definitions)
    _check_targets(definitions)
    return definitions


def _entries(data, where):
    if data is None:
        return []
    if not isinstance(data, list):
        raise DefinitionError("%s のルートは `- <種別>:` の並び（シーケンス）でなければならない" % where)
    return data


def _claim(names, name, where, key="name"):
    """名前を 4 ファイル横断で一意に保つ。"""
    if not isinstance(name, str) or not name.strip():
        raise DefinitionError("%s: `%s` は空でない文字列でなければならない" % (where, key))
    name = name.strip()
    if name in names:
        raise DefinitionError(
            "%s: 名前 `%s` が重複している（%s と衝突）。名前は 4 ファイル横断で一意である"
            % (where, name, names[name])
        )
    names[name] = where
    return name


def _body(entry, kinds, where):
    """`- command:` / `- flow:` / `- action:` / `- gate:` の 1 ブロックを開く。"""
    if not isinstance(entry, dict):
        raise DefinitionError("%s: `- <種別>:` のマッピングでなければならない" % where)
    if len(entry) != 1:
        raise DefinitionError(
            "%s: 1 エントリに書けるのは `%s` のいずれか 1 つだけ（実際: %s）"
            % (where, " / ".join(kinds), ", ".join(sorted(entry)))
        )
    kind, body = next(iter(entry.items()))
    if kind not in kinds:
        raise DefinitionError(
            "%s: 先頭のキーは `%s` のいずれか（実際: `%s`）" % (where, " / ".join(kinds), kind)
        )
    if not isinstance(body, dict):
        raise DefinitionError("%s: `%s` の中身はマッピングでなければならない" % (where, kind))
    return kind, body


def _keys(body, required, optional, where):
    unknown = set(body) - set(required) - set(optional)
    if unknown:
        raise DefinitionError("%s: 不明なキーがある: %s" % (where, ", ".join(sorted(unknown))))
    for key in required:
        if body.get(key) is None:
            raise DefinitionError("%s: `%s` が無い" % (where, key))


def _run(raw, where):
    if not isinstance(raw, dict):
        raise DefinitionError("%s: `run` は `{ type: ..., target: ... }` の形で書く" % where)
    _keys(raw, ("type",), ("target", "isAgent", "requiresHuman", "calls"), where + ".run")

    type_ = raw.get("type")
    if type_ in ("agent", "approval"):
        raise DefinitionError(
            "%s.run: 旧 type `%s` は移行が必要。agent は skill + isAgent、"
            "approval は script + requiresHuman へ変更し、呼出先と再開点を確認する。"
            "references/migration.md を参照（状態・証跡を削除しない）。" % (where, type_)
        )
    if type_ not in RUN_TYPES:
        raise DefinitionError(
            "%s.run: `type` は %s のいずれか（実際: %r）"
            % (where, " / ".join(RUN_TYPES), type_)
        )

    is_agent = raw.get("isAgent", False)
    if not isinstance(is_agent, bool):
        raise DefinitionError("%s.run: `isAgent` は真偽値で書く" % where)
    if is_agent and type_ != "skill":
        raise DefinitionError("%s.run: `isAgent` は `type: skill` のときのみ意味を持つ" % where)

    requires_human = raw.get("requiresHuman", False)
    if not isinstance(requires_human, bool):
        raise DefinitionError("%s.run: `requiresHuman` は真偽値で書く" % where)
    if requires_human and type_ != "script":
        raise DefinitionError("%s.run: `requiresHuman` は `type: script` のときのみ意味を持つ" % where)

    calls = raw.get("calls")
    if calls is not None:
        if type_ != "skill":
            raise DefinitionError("%s.run: `calls` は `type: skill` のときのみ意味を持つ" % where)
        if not isinstance(calls, list) or not calls:
            raise DefinitionError("%s.run: `calls` は空でない名前の配列で書く" % where)
        resolved_calls = []
        for item in calls:
            if not isinstance(item, str) or not item.strip():
                raise DefinitionError("%s.run.calls: 要素は名前の文字列で書く（実際: %r）" % (where, item))
            resolved_calls.append(item.strip())
        calls = resolved_calls

    target = raw.get("target")
    if not target:
        raise DefinitionError("%s.run: `type: %s` には `target` が要る" % (where, type_))
    if not isinstance(target, str) or not target.strip():
        raise DefinitionError("%s.run: target は空でない文字列で書く" % where)
    if type_ == "skill" and not re.fullmatch(r"[a-z0-9][a-z0-9_.-]*", target):
        raise DefinitionError("%s.run: Skill target はディレクトリ名で指定する" % where)
    if calls and any(not re.fullmatch(r"[a-z0-9][a-z0-9_.-]*", name) for name in calls):
        raise DefinitionError("%s.run: calls は Skill ディレクトリ名の列で指定する" % where)
    return RunDefinition(type_, target, is_agent, requires_human, calls)


NO_HOOK = ("%s: `- hook:` は書かない。定義ファイルは command / flow / action / gate だけを持つ"
           "（host の規則は L3 の入口が L0 の host に渡す。L4 の規則は GateExecutor が実行するゲートの中で動く）")


def _load_commands(entries, names):
    commands, texts = {}, {}
    for index, entry in enumerate(entries):
        where = "%s[%d]" % (COMMAND_FILE, index)
        if isinstance(entry, dict) and "hook" in entry:
            raise DefinitionError(NO_HOOK % where)
        _, body = _body(entry, ("command",), where)
        _keys(body, ("id", "command", "steps"), (), where)
        command_id = _claim(names, body["id"], where, "id")
        text = body["command"]
        if not isinstance(text, str) or not text.strip():
            raise DefinitionError("%s: `command` は利用者が入力する文字列で書く" % where)
        if text.strip() in texts:
            raise DefinitionError("%s: command `%s` が重複している（%s と衝突）" % (where, text.strip(), texts[text.strip()]))
        texts[text.strip()] = where
        raw = body["steps"]
        if not isinstance(raw, list) or not raw:
            raise DefinitionError("%s: `steps` は空でない呼出し先の配列で書く" % where)
        steps = []
        for step_index, step in enumerate(raw):
            step_where = "%s.steps[%d]" % (where, step_index)
            if not isinstance(step, dict):
                raise DefinitionError("%s: `{ flow: <名前> }` の形で書く" % step_where)
            # per_feature は持たない。feature ごとの繰り返しは Skill の手順が持つ。
            _keys(step, ("flow",), (), step_where)
            flow = step["flow"]
            if not isinstance(flow, str) or not flow.strip():
                raise DefinitionError("%s: `flow` は flow・action の名前で書く" % step_where)
            steps.append(CommandStep(flow.strip()))
        commands[command_id] = CommandDefinition(command_id, text.strip(), steps)
    return commands


def _load_actions(entries, names):
    actions = {}
    for index, entry in enumerate(entries):
        where = "%s[%d]" % (ACTION_FILE, index)
        _, body = _body(entry, ("action",), where)
        _keys(body, ("name", "run"), ("inputs", "outputs"), where)
        name = _claim(names, body["name"], where)
        actions[name] = ActionDefinition(
            name,
            _run(body["run"], "action `%s`" % name),
            _paths(body, "inputs", "action `%s`" % name),
            _paths(body, "outputs", "action `%s`" % name),
        )
    if not actions:
        raise DefinitionError("%s に action が 1 つも無い" % ACTION_FILE)
    return actions


def _paths(body, key, where):
    """`inputs` / `outputs` を読む。形だけを検査し、中身は解釈しない。"""
    if key not in body:
        return ()
    value = body[key]
    if not isinstance(value, list) or not value:
        raise DefinitionError("%s.%s: 空でないパスの配列で書く（不要ならキーごと省く）" % (where, key))
    paths = []
    for item in value:
        if not isinstance(item, str) or not item.strip() or item != item.strip():
            raise DefinitionError("%s.%s: 要素は前後に空白の無い空でない文字列で書く（実際: %r）" % (where, key, item))
        if item in paths:
            raise DefinitionError("%s.%s: `%s` が重複している" % (where, key, item))
        paths.append(item)
    return tuple(paths)


def _load_flows(entries, names):
    flows = {}
    for index, entry in enumerate(entries):
        where = "%s[%d]" % (FLOW_FILE, index)
        if isinstance(entry, dict) and "flows" in entry:
            raise DefinitionError(
                "%s: `flows`（flow の並び）は廃止した。flow の `steps` に `- flow: <名前>` を書いて入れ子にする" % where)
        _, body = _body(entry, ("flow",), where)
        _keys(body, ("name", "steps"), (), where)
        name = _claim(names, body["name"], where)
        flows[name] = FlowDefinition(name, _steps(body["steps"], "flow `%s`.steps" % name))
    return flows


def _steps(value, where):
    """`steps` を読む。各要素は `{action: <名前>}` か `{flow: <名前>}` のどちらか 1 つ。"""
    if not isinstance(value, list) or not value:
        raise DefinitionError("%s: 手順の配列（空でない）で書く" % where)
    steps = []
    for index, item in enumerate(value):
        item_where = "%s[%d]" % (where, index)
        if not isinstance(item, dict) or len(item) != 1 or next(iter(item)) not in ("action", "flow"):
            raise DefinitionError("%s: `- action: <名前>` か `- flow: <名前>` のどちらか 1 つで書く（実際: %r）" % (item_where, item))
        kind, name = next(iter(item.items()))
        if not isinstance(name, str) or not name.strip():
            raise DefinitionError("%s: `%s` は名前の文字列で書く" % (item_where, kind))
        steps.append(StepDefinition(kind, name.strip()))
    return steps


def _order(value, where):
    if not isinstance(value, list) or not value:
        raise DefinitionError("%s: 名前の配列（空でない）で書く" % where)
    order = []
    for item in value:
        if not isinstance(item, str) or not item.strip():
            raise DefinitionError("%s: 要素は名前の文字列で書く（実際: %r）" % (where, item))
        order.append(item.strip())
    return order


def _load_gates(entries, names):
    gates = []
    for index, entry in enumerate(entries):
        where = "%s[%d]" % (GATE_FILE, index)
        if isinstance(entry, dict) and "hook" in entry:
            raise DefinitionError(NO_HOOK % where)
        _, body = _body(entry, ("gate",), where)
        # `hookPoint` は `target_action` が文字列のときだけ必須（配列のときは各要素が持つ）。
        _keys(body, ("name", "target_action", "run"), ("hookPoint",), where)
        name = _claim(names, body["name"], where)
        run = _run(body["run"], "gate `%s`" % name)
        for target_action, hook_point, target_review in _target_actions(body, name, where):
            gates.append(GateDefinition(name, target_action, hook_point, run, target_review))
    return gates


def _target_actions(body, name, where):
    """`target_action` を `(action, hookPoint, target_review)` の列にする。

    文字列（トップレベルの `hookPoint` が必須）か、`{action, hookPoint}` の配列
    （同一ロジックの汎用ゲートを複数アクションへまとめて差す形）のどちらかを受け付ける。
    配列のときはトップレベルの `hookPoint` を持てない（各要素の `hookPoint` を使うため、
    両方あると衝突する）。
    """
    raw = body["target_action"]
    if isinstance(raw, str):
        if not raw.strip():
            raise DefinitionError("gate `%s`: `target_action` は action の名前で書く" % name)
        hook_point = body.get("hookPoint")
        if hook_point not in HOOK_POINTS:
            raise DefinitionError(
                "gate `%s`: `hookPoint` は %s のいずれか（実際: %r）"
                % (name, " / ".join(HOOK_POINTS), hook_point)
            )
        return [(raw.strip(), hook_point, None)]

    if isinstance(raw, list) and raw:
        if body.get("hookPoint") is not None:
            raise DefinitionError(
                "gate `%s`: `target_action` が配列のときは、トップレベルの `hookPoint` を持てない"
                "（各要素の `hookPoint` を使う）" % name
            )
        pairs = []
        for item_index, item in enumerate(raw):
            item_where = "%s.target_action[%d]" % (where, item_index)
            if not isinstance(item, dict):
                raise DefinitionError("%s: `{ action, hookPoint }` の形で書く" % item_where)
            if "when" in item:
                raise DefinitionError(
                    "%s: `when` は廃止した。実行するかどうかはアクションの next（Skill）とゲート script 自身が決める" % item_where)
            unknown = set(item) - {"action", "hookPoint", "target_review"}
            if unknown:
                raise DefinitionError("%s: 不明なキーがある: %s" % (item_where, ", ".join(sorted(unknown))))
            action_name = item.get("action")
            hook_point = item.get("hookPoint")
            if not isinstance(action_name, str) or not action_name.strip():
                raise DefinitionError("%s: `action` は action の名前で書く" % item_where)
            if hook_point not in HOOK_POINTS:
                raise DefinitionError(
                    "%s: `hookPoint` は %s のいずれか（実際: %r）"
                    % (item_where, " / ".join(HOOK_POINTS), hook_point)
                )
            target_review = _target_review(item, item_where) if "target_review" in item else None
            pairs.append((action_name.strip(), hook_point, target_review))
        return pairs

    raise DefinitionError(
        "gate `%s`: `target_action` は action 名の文字列、または `{action,hookPoint}` の配列で書く" % name
    )


def _target_review(item, where):
    """`target_review` を検査する。ファイル、`<dir>/`（直下）、`<dir>/**`（配下すべて）、`**`（すべて）の配列。

    空の配列は書き誤りとして止める（全出力を対象にするならキーごと省略する）。
    パスの意味（どのファイルが出力か）は解釈しない。
    """
    raw = item["target_review"]
    if not isinstance(raw, list) or not raw:
        raise DefinitionError("%s: `target_review` は空でないパスの配列で書く（全出力ならキーごと省略する）" % where)
    paths = []
    for entry in raw:
        if not isinstance(entry, str) or not entry.strip():
            raise DefinitionError("%s: `target_review` の要素はパスの文字列で書く（実際: %r）" % (where, entry))
        path = entry.strip()
        if path == "**":
            if len(raw) != 1:
                raise DefinitionError("%s: `target_review` の `**` は単独で書く" % where)
            paths.append(path)
            continue
        body = path[:-3] if path.endswith("/**") else path.rstrip("/") if path.endswith("/") else path
        parts = body.split("/")
        if (path.startswith("/") or "\\" in path or re.match(r"^[A-Za-z]:", path) or not body
                or any(part in ("", ".", "..") for part in parts) or "*" in body):
            raise DefinitionError(
                "%s: `target_review` のパス `%s` は案件ルートからの相対パスで書く"
                "（ディレクトリは末尾 `/` か `/**`、すべては `**`。それ以外のワイルドカードと `..` は使えない）" % (where, entry)
            )
        if path in paths:
            raise DefinitionError("%s: `target_review` のパス `%s` が重複している" % (where, path))
        paths.append(path)
    return tuple(paths)


def _check_references(definitions):
    """名前による参照がすべて解決できるかを、**起動前に**確かめる。"""
    for flow in definitions.flows.all():
        for step in flow.steps:
            known = definitions.actions if step.kind == "action" else definitions.flows
            if step.name not in known:
                raise DefinitionError(
                    "flow `%s`.steps: 未定義の %s `%s` を指している" % (flow.name, step.kind, step.name))
    _check_cycles(definitions)

    for gate in definitions.gates.all():
        if gate.target_action not in definitions.actions:
            raise DefinitionError(
                "gate `%s`.target_action: 未定義の action `%s` を指している"
                % (gate.name, gate.target_action)
            )

    for command in definitions.commands.all():
        for step in command.steps:
            try:
                definitions.call(step.flow)
            except DefinitionError:
                raise DefinitionError(
                    "command `%s`.steps: 未定義の呼出し先 `%s` を指している" % (command.id, step.flow)
                )


def _check_cycles(definitions):
    """flow が自分自身を（入れ子を通して間接にも）呼んでいればエラーにする。"""
    done = set()

    def visit(name, path):
        if name in path:
            raise DefinitionError("flow の循環: %s" % " → ".join(path[path.index(name):] + [name]))
        if name in done:
            return
        for step in definitions.flows.find(name).steps:
            if step.kind == "flow":
                visit(step.name, path + [name])
        done.add(name)

    for name in definitions.flows.names():
        visit(name, [])


def _skill_runs(definitions):
    for action in definitions.actions.all():
        yield action.run, "action `%s`" % action.name
    for gate in definitions.gates.all():
        yield gate.run, "gate `%s`" % gate.name


def _check_targets(definitions):
    """定義に書かれた script・Skill・agent があることを確かめる。**中身は読まない**（L0 は L3・L4 を読まない）。"""
    skills_root = os.path.dirname(definitions.root)
    for run, label in _skill_runs(definitions):
        if run.type == "script":
            script = run.target.split()[0] if run.target.split() else run.target
            if not os.path.isfile(definitions.resolve(script)):
                raise DefinitionError("%s: script `%s` が無い" % (label, script))
        if run.type != "skill":
            continue
        if not os.path.isfile(os.path.join(skills_root, run.target, "SKILL.md")):
            raise DefinitionError("%s: Skill `%s` が無い。原本を合成した配布物を使う" % (label, run.target))
        if run.is_agent:
            agent_path = os.path.join(os.path.dirname(skills_root), "agents", "check-runner.md")
            if not os.path.isfile(agent_path):
                raise DefinitionError("%s: check-runner が無い" % label)
        for name in run.calls or []:
            if not os.path.isfile(os.path.join(skills_root, name, "SKILL.md")):
                raise DefinitionError("%s: calls の Skill `%s` が無い" % (label, name))
