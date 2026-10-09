"""ExecutionContext — 実行器の間で引き継ぐ文脈（仕様書 §6）。L3・L4 が import する枠組みの API。

L0 は unit を実行するとき、今の Flow / Action / item / ゲート / HookPoint / 検査対象を環境変数で渡す
（`run_dispatcher.py` の `_env`）。この module はそれを読み、L3・L4 の規則 script が使う形にする。

| 部品 | すること |
|---|---|
| `ExecutionContext` | 案件ルート・状態ストア・今の unit（環境変数）。状態ストアの排他 `locked()` |
| `definitions()` | 定義ファイル 4 つを読んだ結果（`validate --json` と同じ形）。L3・L4 は子プロセスを起こさずに読める |
| `select()` | `target_review` の並びで、アクションの出力から検査対象を選ぶ（ファイル / `<dir>/` / `<dir>/**` / `**`） |
| `ok()` / `fail()` / `log_keys()` | script とランナーの約束（終了コード 0 / 1 / 10、`AIDD-LOG:` 行） |

**この module は L3・L4 を import しない。** 工程・feature・承認といった語彙は持たず、L3 の
`phase_rules.py` がこの `ExecutionContext` を継いで持つ。
"""

import json
import os
import sys

_BIN = os.path.dirname(os.path.abspath(__file__))
COMMON = os.path.dirname(_BIN)
for _path in (_BIN, os.path.join(COMMON, "lib")):
    if _path not in sys.path:
        sys.path.insert(0, _path)

import aidd_lock  # noqa: E402

EXIT_OK, EXIT_FAIL, EXIT_WAIT = 0, 1, 10

_DEFINITIONS = {}


def definitions(config=None):
    """定義ファイルを読んだ結果（`validate --json` と同じ形）。置き場と内容ごとに 1 回だけ読む。"""
    import aidd
    import repositories
    root = os.path.abspath(config or os.environ.get("AIDD_CONFIG") or COMMON)
    key = (root, repositories.config_hash(root))  # 設定が変われば読み直す
    if key not in _DEFINITIONS:
        _DEFINITIONS[key] = aidd.describe(repositories.load(root))
    return _DEFINITIONS[key]


class ExecutionContext:
    """今の unit の文脈。引数を渡さなければ、L0 が unit に渡した環境変数から読む。"""

    def __init__(self, root=None, state_path=None, action=None, item=None):
        self.root = os.path.realpath(root or os.environ.get("AIDD_ROOT") or os.getcwd())
        self.state_path = os.path.realpath(state_path or os.environ.get("AIDD_STATE") or self.path(".aidd/phase-progress.json"))
        self.config = os.environ.get("AIDD_CONFIG") or COMMON
        self.flow = os.environ.get("AIDD_FLOW") or ""
        self.action = action if action is not None else os.environ.get("AIDD_ACTION", "")
        # An explicitly selected action starts a new context. Do not leak the
        # current gate's item into a lookup of another action.
        self.item = item if item is not None else (os.environ.get("AIDD_ITEM", "") if action is None else "")
        self.gate = os.environ.get("AIDD_GATE", "")
        self.hook_point = os.environ.get("AIDD_HOOK_POINT", "")
        self.unit = os.environ.get("AIDD_UNIT", "")
        self.action_unit = os.environ.get("AIDD_ACTION_UNIT", "")

    def locked(self):
        return aidd_lock.hold(self.state_path)

    def path(self, relative):
        """案件ルートからの相対パスを絶対パスにする。ルートの外は拒む。"""
        root = os.path.realpath(self.root)
        candidate = os.path.realpath(os.path.join(root, relative))
        if candidate != root and not candidate.startswith(root + os.sep):
            raise ValueError("path is outside the project root: %s" % relative)
        return candidate

    @property
    def target_review(self):
        """このゲートの `target_review`（`{item}` を差し替えた並び）。省略なら None。"""
        raw = os.environ.get("AIDD_TARGET_REVIEW")
        if not raw or not self.gate:
            return None
        return json.loads(raw)


def select(patterns, outputs, label, action):
    """`target_review` の並びで出力を選ぶ。ファイル、`<dir>/`（直下）、`<dir>/**`（配下すべて）、`**`（すべて）。

    どの並びも、そのアクションの出力のどれかに当たらなければエラーにする。順序は出力の順。
    """
    if patterns == ["**"]:
        return list(outputs)
    chosen = set()
    for pattern in patterns:
        if pattern.endswith("/**"):
            matched = [o for o in outputs if o.startswith(pattern[:-2])]
        elif pattern.endswith("/"):
            matched = [o for o in outputs if o.startswith(pattern) and "/" not in o[len(pattern):]]
        else:
            matched = [pattern] if pattern in outputs else []
        if not matched:
            raise ValueError("%s: target_review `%s` names no output of %s (outputs: %s)"
                             % (label, pattern, action, ", ".join(outputs)))
        chosen.update(matched)
    return [o for o in outputs if o in chosen]


def log_keys(**pairs):
    """`終了` 行に載せる キー=値 を `AIDD-LOG:` 行で渡す。"""
    items = ["%s=%s" % (k, " ".join(str(v).split())) for k, v in pairs.items() if v not in (None, "")]
    if items:
        print("AIDD-LOG: " + " ".join(items))


def ok(message=None, **pairs):
    log_keys(**pairs)
    if message:
        print(message)
    raise SystemExit(EXIT_OK)


def fail(title, lines=()):
    print(title, file=sys.stderr)
    for line in lines:
        print("  - %s" % line, file=sys.stderr)
    raise SystemExit(EXIT_FAIL)
