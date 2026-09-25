"""設定ファイル（events.yaml / flows.yaml / gates.yaml）の読み込みとスキーマ検査。

このモジュールが知っているのは **event / flow / gate / Run** だけである。
フェーズ・feature・承認といった AIDD 固有の語彙は持たない。それらは設定ファイルの
値として現れるだけで、ランナーは値の意味を解釈しない。

    events ― 何をするか   : name と Run だけを持つ
    flows  ― どの順で呼ぶか: event の並び（flow）／ flow の並び（flows）
    gates  ― どこに差すか  : target_event と hookPoint で、イベントの前後に差し込む

**つながりはすべて名前による参照である。** 名前は 3 ファイルを横断して一意であり、
未定義の名前は**読み込んだ時点でエラーにする**（実行時に見つからないと、検査が黙って
スキップされる）。**gate だけが逆向きに指すため、ゲートを足しても event と flow は変わらない。**

**`call(名前)` は event を直接指してもよい。** flows.yaml に 1 イベントだけの flow を
量産しないための救済であり、その場でイベント 1 本の flow を組み立てて返すだけで、
名前の登録（3 ファイル横断の一意性）は増やさない。feature ごとに呼び分ける
（`--item` を付けて何度も呼ぶ）ものはこちらを使う。
"""

import os
import re

try:  # PyYAML があれば使う。無ければ同梱のサブセットパーサで読む。
    import yaml as _yaml

    def parse_yaml(text):
        """設定ファイルと .aidd/logging.yaml の両方がこれで読む。"""
        return _yaml.safe_load(text)

except ImportError:  # pragma: no cover - 環境依存

    import yamlmini as _yamlmini

    def parse_yaml(text):
        """設定ファイルと .aidd/logging.yaml の両方がこれで読む。"""
        return _yamlmini.load(text)


RUN_TYPES = ("command", "script", "skill")
HOOK_POINTS = ("start", "end")


# retry / timeout は設定ファイルに持たせない（スキーマは name / run / 並びだけである）。
# engine の既定値としてここに置き、**requiresHuman: true の run には適用しない**。
DEFAULT_TIMEOUT = "10m"
DEFAULT_RETRY = 0

FILES = ("events.yaml", "flows.yaml", "gates.yaml")


class ConfigError(ValueError):
    """設定ファイルがスキーマに合っていない。読み込んだ時点で止める。"""


class Run:
    """events と gates で共通の「実行のされ方」。

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

    def __init__(
        self,
        type_,
        target,
        is_agent=False,
        requires_human=False,
        calls=None,
        retry=DEFAULT_RETRY,
        timeout=DEFAULT_TIMEOUT,
    ):
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
        return "Run(%s, %s%s)" % (self.type, self.target, flags)


class Event:
    __slots__ = ("name", "run")

    def __init__(self, name, run):
        self.name = name
        self.run = run

    def __repr__(self):
        return "Event(%s)" % self.name


class Flow:
    """`flow` ― イベントの並び。"""

    __slots__ = ("name", "event_order")

    def __init__(self, name, event_order):
        self.name = name
        self.event_order = event_order

    @property
    def kind(self):
        return "flow"


class FlowGroup:
    """`flows` ― flow の並び。**入れ子は 1 段まで**（flow_order に flows を書けない）。"""

    __slots__ = ("name", "flow_order")

    def __init__(self, name, flow_order):
        self.name = name
        self.flow_order = flow_order

    @property
    def kind(self):
        return "flows"


class Gate:
    __slots__ = ("name", "target_event", "hook_point", "run", "when")

    def __init__(self, name, target_event, hook_point, run, when=None):
        self.name = name
        self.target_event = target_event
        self.hook_point = hook_point
        self.run = run
        # 差し口ごとの適用条件（script のパス）。終了コード 0 で適用、SKIP_EXIT_CODE で省略。
        # 省略の判断は呼出し側の規則 script が持ち、L0 は名前の意味を解釈しない。
        self.when = when

    def __repr__(self):
        return "Gate(%s, %s, %s)" % (self.name, self.target_event, self.hook_point)


class Config:
    def __init__(self, root, events, flows, gates):
        # `scripts/...` などの相対パスは設定ファイルの置き場を基準にする。
        self.root = os.path.abspath(root)
        self.events = events          # {name: Event}（記述順）
        self.flows = flows            # {name: Flow | FlowGroup}（記述順）
        self.gates = gates            # [Gate]（記述順。同じ差し口はこの順で直列に走る）

    # --- 名前で引く ------------------------------------------------------

    @property
    def path(self):
        """設定ファイルの置き場（ログと環境変数に載せる）。"""
        return self.root

    def paths(self):
        return [os.path.join(self.root, name) for name in FILES]

    def event(self, name):
        try:
            return self.events[name]
        except KeyError:
            raise ConfigError("event `%s` は events.yaml に無い" % name)

    def call(self, name):
        """`event_handler.call(<名前>)` が指すもの。flow / flows / event のいずれでもよい。

        flows.yaml に登録が無くても、event の名前と一致すれば **その場でイベント 1 本の
        flow を組み立てて返す**（登録はしない。`--item` を付けて何度も呼ぶ、feature ごとの
        呼び出しはこの経路を使う。plan 1 回・横断ゲート 1 回のような「1 回だけ」の呼び出しも
        同じ経路でよい）。
        """
        found = self.flows.get(name)
        if found is not None:
            return found
        if name in self.events:
            return Flow(name, [name])
        raise ConfigError(
            "`%s` は event にも flows.yaml にも無い（登録済み flow/flows: %s）"
            % (name, ", ".join(self.flows) or "なし")
        )

    def gates_for(self, event_name, hook_point):
        """その差し口に差さったゲートを**記述順**で返す。並列にしない。"""
        return [
            gate
            for gate in self.gates
            if gate.target_event == event_name and gate.hook_point == hook_point
        ]

    def flow_order(self, name):
        """`call` の名前を flow の並びにする（flows なら展開し、flow なら 1 本）。"""
        entry = self.call(name)
        if entry.kind == "flow":
            return [entry]
        return [self.call(child) for child in entry.flow_order]

    def resolve(self, path):
        """設定ファイルの置き場からの相対パスを絶対パスにする。"""
        if os.path.isabs(path):
            return path
        return os.path.normpath(os.path.join(self.root, path))


# --- 読み込み -------------------------------------------------------------


def load(root):
    """`root` に置かれた 3 ファイルを読む。1 つでも欠けていたらエラーにする。"""
    root = os.path.abspath(root)
    raw = {}
    for name in FILES:
        path = os.path.join(root, name)
        if not os.path.exists(path):
            raise ConfigError("設定ファイル `%s` が無い（置き場: %s）" % (name, root))
        with open(path, encoding="utf-8") as handle:
            raw[name] = _entries(parse_yaml(handle.read()), name)

    names = {}  # 3 ファイル横断の一意性はここで見る
    events = _load_events(raw["events.yaml"], names)
    flows = _load_flows(raw["flows.yaml"], names)
    gates = _load_gates(raw["gates.yaml"], names)

    config = Config(root, events, flows, gates)
    _check_references(config)
    _check_calls_consistency(config)
    return config


def _entries(data, where):
    if data is None:
        return []
    if not isinstance(data, list):
        raise ConfigError("%s のルートは `- <種別>:` の並び（シーケンス）でなければならない" % where)
    return data


def _claim(names, name, where):
    """名前を 3 ファイル横断で一意に保つ。"""
    if not isinstance(name, str) or not name.strip():
        raise ConfigError("%s: `name` は空でない文字列でなければならない" % where)
    name = name.strip()
    if name in names:
        raise ConfigError(
            "%s: 名前 `%s` が重複している（%s と衝突）。名前は 3 ファイル横断で一意である"
            % (where, name, names[name])
        )
    names[name] = where
    return name


def _body(entry, kinds, where):
    """`- event:` / `- flow:` / `- gate:` の 1 ブロックを開く。"""
    if not isinstance(entry, dict):
        raise ConfigError("%s: `- <種別>:` のマッピングでなければならない" % where)
    if len(entry) != 1:
        raise ConfigError(
            "%s: 1 エントリに書けるのは `%s` のいずれか 1 つだけ（実際: %s）"
            % (where, " / ".join(kinds), ", ".join(sorted(entry)))
        )
    kind, body = next(iter(entry.items()))
    if kind not in kinds:
        raise ConfigError(
            "%s: 先頭のキーは `%s` のいずれか（実際: `%s`）" % (where, " / ".join(kinds), kind)
        )
    if not isinstance(body, dict):
        raise ConfigError("%s: `%s` の中身はマッピングでなければならない" % (where, kind))
    return kind, body


def _keys(body, required, optional, where):
    unknown = set(body) - set(required) - set(optional)
    if unknown:
        raise ConfigError("%s: 不明なキーがある: %s" % (where, ", ".join(sorted(unknown))))
    for key in required:
        if body.get(key) is None:
            raise ConfigError("%s: `%s` が無い" % (where, key))


def _run(raw, where):
    if not isinstance(raw, dict):
        raise ConfigError("%s: `run` は `{ type: ..., target: ... }` の形で書く" % where)
    _keys(raw, ("type",), ("target", "isAgent", "requiresHuman", "calls"), where + ".run")

    type_ = raw.get("type")
    if type_ in ("agent", "approval"):
        raise ConfigError(
            "%s.run: 旧 type `%s` は移行が必要。agent は skill + isAgent、"
            "approval は script + requiresHuman へ変更し、呼出先と再開点を確認する。"
            "references/migration.md を参照（状態・証跡を削除しない）。" % (where, type_)
        )
    if type_ not in RUN_TYPES:
        raise ConfigError(
            "%s.run: `type` は %s のいずれか（実際: %r）"
            % (where, " / ".join(RUN_TYPES), type_)
        )

    is_agent = raw.get("isAgent", False)
    if not isinstance(is_agent, bool):
        raise ConfigError("%s.run: `isAgent` は真偽値で書く" % where)
    if is_agent and type_ != "skill":
        raise ConfigError("%s.run: `isAgent` は `type: skill` のときのみ意味を持つ" % where)

    requires_human = raw.get("requiresHuman", False)
    if not isinstance(requires_human, bool):
        raise ConfigError("%s.run: `requiresHuman` は真偽値で書く" % where)
    if requires_human and type_ != "script":
        raise ConfigError("%s.run: `requiresHuman` は `type: script` のときのみ意味を持つ" % where)

    calls = raw.get("calls")
    if calls is not None:
        if type_ != "skill":
            raise ConfigError("%s.run: `calls` は `type: skill` のときのみ意味を持つ" % where)
        if not isinstance(calls, list) or not calls:
            raise ConfigError("%s.run: `calls` は空でない名前の配列で書く" % where)
        resolved_calls = []
        for item in calls:
            if not isinstance(item, str) or not item.strip():
                raise ConfigError("%s.run.calls: 要素は名前の文字列で書く（実際: %r）" % (where, item))
            resolved_calls.append(item.strip())
        calls = resolved_calls

    target = raw.get("target")
    if not target:
        raise ConfigError("%s.run: `type: %s` には `target` が要る" % (where, type_))
    if not isinstance(target, str) or not target.strip():
        raise ConfigError("%s.run: target は空でない文字列で書く" % where)
    if type_ == "skill" and not re.fullmatch(r"[a-z0-9][a-z0-9_.-]*", target):
        raise ConfigError("%s.run: Skill target はディレクトリ名で指定する" % where)
    if calls and any(not re.fullmatch(r"[a-z0-9][a-z0-9_.-]*", name) for name in calls):
        raise ConfigError("%s.run: calls は Skill ディレクトリ名の列で指定する" % where)
    return Run(type_, target, is_agent, requires_human, calls)


def _load_events(entries, names):
    events = {}
    for index, entry in enumerate(entries):
        where = "events.yaml[%d]" % index
        _, body = _body(entry, ("event",), where)
        _keys(body, ("name", "run"), (), where)
        name = _claim(names, body["name"], where)
        events[name] = Event(name, _run(body["run"], "event `%s`" % name))
    if not events:
        raise ConfigError("events.yaml に event が 1 つも無い")
    return events


def _load_flows(entries, names):
    flows = {}
    for index, entry in enumerate(entries):
        where = "flows.yaml[%d]" % index
        kind, body = _body(entry, ("flow", "flows"), where)
        if kind == "flow":
            _keys(body, ("name", "event_order"), (), where)
            name = _claim(names, body["name"], where)
            flows[name] = Flow(name, _order(body["event_order"], "flow `%s`.event_order" % name))
        else:
            _keys(body, ("name", "flow_order"), (), where)
            name = _claim(names, body["name"], where)
            flows[name] = FlowGroup(
                name, _order(body["flow_order"], "flows `%s`.flow_order" % name)
            )
    return flows


def _order(value, where):
    if not isinstance(value, list) or not value:
        raise ConfigError("%s: 名前の配列（空でない）で書く" % where)
    order = []
    for item in value:
        if not isinstance(item, str) or not item.strip():
            raise ConfigError("%s: 要素は名前の文字列で書く（実際: %r）" % (where, item))
        order.append(item.strip())
    return order


def _load_gates(entries, names):
    gates = []
    for index, entry in enumerate(entries):
        where = "gates.yaml[%d]" % index
        _, body = _body(entry, ("gate",), where)
        # `hookPoint` は `target_event` が文字列のときだけ必須（配列のときは各要素が持つ）。
        _keys(body, ("name", "target_event", "run"), ("hookPoint",), where)
        name = _claim(names, body["name"], where)
        run = _run(body["run"], "gate `%s`" % name)
        for target_event, hook_point, when in _target_events(body, name, where):
            gates.append(Gate(name, target_event, hook_point, run, when))
    return gates


def _target_events(body, name, where):
    """`target_event` を `(event, hookPoint)` の列にする。

    文字列（従来どおり。トップレベルの `hookPoint` が必須）か、
    `{event, hookPoint}` の配列（同一ロジックの汎用ゲートを複数イベントへまとめて差す形）の
    どちらかを受け付ける。配列のときはトップレベルの `hookPoint` を持てない
    （各要素の `hookPoint` を使うため、両方あると衝突する）。
    """
    raw = body["target_event"]
    if isinstance(raw, str):
        if not raw.strip():
            raise ConfigError("gate `%s`: `target_event` は event の名前で書く" % name)
        hook_point = body.get("hookPoint")
        if hook_point not in HOOK_POINTS:
            raise ConfigError(
                "gate `%s`: `hookPoint` は %s のいずれか（実際: %r）"
                % (name, " / ".join(HOOK_POINTS), hook_point)
            )
        return [(raw.strip(), hook_point, None)]

    if isinstance(raw, list) and raw:
        if body.get("hookPoint") is not None:
            raise ConfigError(
                "gate `%s`: `target_event` が配列のときは、トップレベルの `hookPoint` を持てない"
                "（各要素の `hookPoint` を使う）" % name
            )
        pairs = []
        for item_index, item in enumerate(raw):
            item_where = "%s.target_event[%d]" % (where, item_index)
            if not isinstance(item, dict):
                raise ConfigError("%s: `{ event, hookPoint }` の形で書く" % item_where)
            unknown = set(item) - {"event", "hookPoint", "when"}
            if unknown:
                raise ConfigError("%s: 不明なキーがある: %s" % (item_where, ", ".join(sorted(unknown))))
            event_name = item.get("event")
            hook_point = item.get("hookPoint")
            if not isinstance(event_name, str) or not event_name.strip():
                raise ConfigError("%s: `event` は event の名前で書く" % item_where)
            if hook_point not in HOOK_POINTS:
                raise ConfigError(
                    "%s: `hookPoint` は %s のいずれか（実際: %r）"
                    % (item_where, " / ".join(HOOK_POINTS), hook_point)
                )
            when = item.get("when")
            if when is not None and (not isinstance(when, str) or not when.strip()):
                raise ConfigError("%s: `when` は条件 script のパスで書く" % item_where)
            pairs.append((event_name.strip(), hook_point, when.strip() if when else None))
        return pairs

    raise ConfigError(
        "gate `%s`: `target_event` は event 名の文字列、または `{event,hookPoint}` の配列で書く" % name
    )


def _check_references(config):
    """名前による参照がすべて解決できるかを、**起動前に**確かめる。"""
    for flow in config.flows.values():
        if flow.kind == "flow":
            for event_name in flow.event_order:
                if event_name not in config.events:
                    raise ConfigError(
                        "flow `%s`.event_order: 未定義の event `%s` を指している"
                        % (flow.name, event_name)
                    )
            continue
        for child in flow.flow_order:
            target = config.flows.get(child)
            if target is None:
                raise ConfigError(
                    "flows `%s`.flow_order: 未定義の flow `%s` を指している" % (flow.name, child)
                )
            if target.kind != "flow":
                # 入れ子は 1 段まで。深くしても読みにくくなるだけである。
                raise ConfigError(
                    "flows `%s`.flow_order: `%s` は flows である（入れ子は 1 段まで）"
                    % (flow.name, child)
                )

    for gate in config.gates:
        if gate.target_event not in config.events:
            raise ConfigError(
                "gate `%s`.target_event: 未定義の event `%s` を指している"
                % (gate.name, gate.target_event)
            )
        if gate.when and not os.path.isfile(config.resolve(gate.when)):
            raise ConfigError(
                "gate `%s`（%s）: when の script `%s` が無い" % (gate.name, gate.target_event, gate.when)
            )


# 合成 Skill の本文が Read する観点 Skill への参照（`.claude/skills/<name>/SKILL.md`）。
_SKILL_REF = re.compile(r"\.claude/skills/([A-Za-z0-9_.-]+)/SKILL\.md")


def _referenced_skills(text):
    """合成 Skill の手順内の参照だけを、重複と順序を保って返す。"""
    sections = re.findall(r"^## 手順\s*\n(.*?)(?=^## |\Z)", text, re.M | re.S)
    if len(sections) != 1:
        raise ConfigError("合成 Skill は `## 手順` を一つ持つ必要がある")
    return [match.group(1) for match in _SKILL_REF.finditer(sections[0])]


def _skill_runs(config):
    for name, event in config.events.items():
        yield event.run, "event `%s`" % name
    for gate in config.gates:
        yield gate.run, "gate `%s`" % gate.name


def _check_calls_consistency(config):
    """合成済みパッケージの実体・手順と calls を検査する。欠落は省略しない。"""
    skills_root = os.path.dirname(config.root)
    checked = set()
    for run, label in _skill_runs(config):
        if run.type == "script":
            if not os.path.isfile(config.resolve(run.target)):
                raise ConfigError("%s: script `%s` が無い" % (label, run.target))
        if run.type != "skill":
            continue
        key = (run.target, tuple(run.calls or []))
        if key in checked:
            continue
        checked.add(key)
        skill_path = os.path.join(skills_root, run.target, "SKILL.md")
        if not os.path.isfile(skill_path):
            raise ConfigError("%s: Skill `%s` が無い。原本を合成した配布物を使う" % (label, run.target))
        if run.is_agent:
            agent_path = os.path.join(os.path.dirname(skills_root), "agents", "check-runner.md")
            if not os.path.isfile(agent_path):
                raise ConfigError("%s: check-runner が無い" % label)
        if not run.calls:
            continue
        for name in run.calls:
            if not os.path.isfile(os.path.join(skills_root, name, "SKILL.md")):
                raise ConfigError("%s: calls の Skill `%s` が無い" % (label, name))
        with open(skill_path, encoding="utf-8") as handle:
            body_calls = _referenced_skills(handle.read())
        if body_calls != list(run.calls):
            raise ConfigError(
                "%s: `run.calls` %s と、合成 Skill `%s` の手順内 Read 対象 %s が一致しない"
                % (label, list(run.calls), run.target, body_calls)
            )


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
            raise ConfigError("timeout `%s` を秒に直せない" % timeout)
    try:
        return int(text)
    except ValueError:
        raise ConfigError("timeout `%s` を秒に直せない" % timeout)
