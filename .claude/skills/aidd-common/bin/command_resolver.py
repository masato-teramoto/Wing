#!/usr/bin/env python3
"""CommandResolver — 入力されたコマンドから CommandDefinition と呼出し先を解決する（仕様書の不変条件 1）。

    python3 .claude/skills/aidd-common/bin/command_resolver.py <コマンド> [オプション] <操作> [オプション]
    python3 .claude/skills/aidd-common/bin/command_resolver.py validate | doctor [--runtime-only]

コマンドは `command.yaml` の CommandDefinition（id または `/aidd-...` の入力文字列）で指定する。
host agent の入口は規則の層（L3）の入口であり、それがこの CommandResolver でコマンドと呼出し先を解決してから、
L0 の host に規則を渡して advance / submit / respond を実行する。L0 は L3・L4 を import せず、定義ファイルに hook は無い。

この CLI が受けるのは、規則の要らない操作だけである。

| 操作 | 行き先 |
|---|---|
| `status` / `report` / `redo` / `migrate-flow` | Workflow Engine の CLI（`aidd.py`） |
| `validate` / `doctor` | 定義の検査、読むだけの確認（`doctor` は L0 の確認だけ。案件側の確認は規則の層の入口が加える） |
| それ以外（`advance` / `submit` / `respond`、L3・L4 の操作） | 拒む（規則の層の入口から呼ぶ） |

**呼出し先はコマンドのもの**でなければならない。`--call` / `--action` は、そのコマンドの steps の呼出し先、
またはその flow が（入れ子を含めて）たどるアクションに限る。別のコマンドの呼出し先なら、持つコマンドを示して拒む。

案件ルート・状態ストア・定義ファイルの置き場は、このファイルの場所から決まる
（`<案件>/.claude/skills/aidd-common/bin/command_resolver.py`）。`--root` / `--state` / `--config` では変えられない
（別の案件を操作させない。試験で別の置き場を使うときは内部の `aidd.py` / `host.Host` を直接使う）。

**この層は解決だけを行う。** フローの実行・状態の保存は Workflow Engine、繰り返し（feature ごと・修正の回）は
入口 Skill の手順が持つ。
"""

import argparse
import json
import os
import shutil
import subprocess
import sys

_BIN = os.path.dirname(os.path.abspath(__file__))
COMMON = os.path.dirname(_BIN)
for _path in (_BIN, os.path.join(COMMON, "lib")):
    if _path not in sys.path:
        sys.path.insert(0, _path)

from definitions import DefinitionError  # noqa: E402

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(COMMON)))  # <案件>/.claude/skills/aidd-common
ENGINE_OPERATIONS = ("status", "report", "redo", "migrate-flow")
GLOBAL_OPERATIONS = ("validate", "doctor")


class CommandResolver:
    def __init__(self, definitions):
        self.definitions = definitions

    def resolve(self, command):
        """`id`（`aidd-requirements`）または入力文字列（`/aidd-requirements`）で引く。"""
        for definition in self.definitions.commands.all():
            if command in (definition.id, definition.command):
                return definition
        raise DefinitionError(
            "コマンド `%s` は command.yaml に無い（登録済み: %s）"
            % (command, ", ".join(d.command for d in self.definitions.commands.all()) or "なし")
        )

    def root_flows(self, command):
        """コマンドが順に呼ぶ呼出し先の名前。"""
        return [step.flow for step in self.resolve(command).steps]

    def step_for(self, call):
        """呼出し先 `call` を持つ step（コマンドの step に無ければ None）。"""
        for definition in self.definitions.commands.all():
            for step in definition.steps:
                if step.flow == call:
                    return step
        return None

    def reachable(self, command):
        """コマンドから呼べる名前：steps の呼出し先、その入れ子の flow、たどるアクション。"""
        names = set()
        for step in self.resolve(command).steps:
            names.add(step.flow)
            pending = [step.flow]
            while pending:
                name = pending.pop()
                flow = self.definitions.flows.find(name)
                if flow is None:
                    continue
                for inner in flow.steps:
                    if inner.name not in names:
                        names.add(inner.name)
                        if inner.kind == "flow":
                            pending.append(inner.name)
        return names

    def owners(self, name):
        """名前を呼べるコマンド（入力文字列）の並び。"""
        return [d.command for d in self.definitions.commands.all() if name in self.reachable(d.id)]

    def check(self, command, name):
        """`name`（呼出し先・アクション）がコマンドのものであること。コマンドの定義を返す。"""
        definition = self.resolve(command)
        if name and name not in self.reachable(definition.id):
            owners = self.owners(name)
            raise DefinitionError(
                "`%s` は %s の呼出し先ではない（%s）"
                % (name, definition.command,
                   "呼べるコマンド: " + ", ".join(owners) if owners else "どのコマンドの呼出し先でもない"))
        return definition


# --- CLI（host agent の入口）-------------------------------------------------

VALUE_OPTIONS = ("--root", "--state", "--config", "--call", "--action", "--item", "--payload", "--actor", "--result",
                 "--note", "--detail", "--dispatch-id", "--flow", "--from", "--to", "--log-config", "--log-level")
FLAG_OPTIONS = ("--json", "--runtime-only", "--log-echo")


class _Options:
    def __init__(self):
        self.root = self.state = self.config = self.call = self.action = None
        self.operation = None
        self.rest = []  # その他のオプション（行き先へそのまま渡す）


def _options(argv):
    """オプションと操作（最初の位置引数）を取り出す。操作はコマンドの後のどこに書いてもよい。"""
    known = _Options()
    tokens = list(argv)
    while tokens:
        token = tokens.pop(0)
        if token.startswith("--"):
            name, _, inline = token.partition("=")
            if name in VALUE_OPTIONS:
                if not inline:
                    if not tokens:
                        raise DefinitionError("`%s` に値が要る" % name)
                    inline = tokens.pop(0)
                field = name[2:].replace("-", "_")
                if field in ("root", "state", "config"):
                    raise DefinitionError("root, state and config are fixed to this project")
                if field in ("call", "action"):
                    setattr(known, field, inline)
                else:
                    known.rest += [name, inline]
            elif name in FLAG_OPTIONS:
                known.rest.append(name)
            else:
                raise DefinitionError("不明なオプション `%s`" % name)
        elif known.operation is None:
            known.operation = token
        else:
            raise DefinitionError("操作は 1 つだけ書く（`%s` と `%s`）" % (known.operation, token))
    return known


def _paths(known):
    root = os.path.abspath(known.root or PROJECT_ROOT)
    state = os.path.abspath(known.state) if known.state else os.path.join(root, ".aidd/phase-progress.json")
    config = os.path.abspath(known.config or COMMON)
    return root, state, config


def _passthrough(known):
    value = []
    if known.call:
        value += ["--call", known.call]
    if known.action:
        value += ["--action", known.action]
    return value


def run(argv):
    if not argv or argv[0] in ("-h", "--help"):
        print(__doc__)
        return 0 if argv else 1
    if argv[0] in GLOBAL_OPERATIONS:
        known = _options(argv[1:])
        root, state, config = _paths(known)
        if argv[0] == "doctor":
            return doctor(root, state, config, "--runtime-only" in known.rest)
        import aidd
        return aidd.main(["--root", root, "--state", state, "--config", config, "validate"] + known.rest)
    command = argv[0]
    known = _options(argv[1:])
    operation, rest = known.operation, known.rest
    if not operation:
        raise DefinitionError("操作が要る（例: /aidd-requirements advance --call requirements-plan）")
    root, state, config = _paths(known)
    import repositories
    definitions = repositories.load(config)
    resolver = CommandResolver(definitions)
    resolver.check(command, known.call)
    resolver.check(command, known.action)
    if operation not in ENGINE_OPERATIONS:
        raise DefinitionError("`%s` は規則の要る操作であり、この CLI では受けない。規則の層（L3）の入口から呼ぶ" % operation)
    import aidd
    common = ["--root", root, "--state", state, "--config", config]
    return aidd.main(common + [operation] + _passthrough(known) + rest)


def main(argv=None):
    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, "reconfigure"):
            stream.reconfigure(encoding="utf-8", errors="replace")
    if sys.version_info < (3, 9):
        print("Python 3.9 or later is required.", file=sys.stderr)
        return 1
    try:
        return run(list(sys.argv[1:] if argv is None else argv))
    except DefinitionError as error:
        print(json.dumps({"status": "fail", "error": str(error)}, ensure_ascii=False))
        return 1


# --- doctor（読むだけの確認。状態・ログ・承認を作らない）------------------------

def doctor(root, state, config, runtime_only=False, extra=None):
    """`extra` は規則の層が加える案件側の確認（配布物の資材・入力など）の並び。"""
    checks = []

    def check(name, passed, detail):
        checks.append({"name": name, "ok": bool(passed), "detail": detail})

    check("python", sys.version_info >= (3, 9), sys.version.split()[0])
    try:
        for base, _, files in os.walk(config):
            for name in files:
                if name.endswith(".py"):
                    path = os.path.join(base, name)
                    with open(path, "rb") as handle:
                        compile(handle.read(), path, "exec")
        check("python_sources", True, "syntax checked without bytecode")
    except (OSError, SyntaxError) as error:
        check("python_sources", False, str(error))
    try:
        import repositories
        definitions = repositories.load(config)
        check("engine_config", True, "valid")
        skills = os.path.dirname(config)
        missing = [d.id for d in definitions.commands.all()
                   if not os.path.isfile(os.path.join(skills, d.id, "SKILL.md"))]
        check("commands", definitions.commands.all() and not missing,
              missing or "%d commands" % len(definitions.commands.all()))
        for row in extra or []:
            check(row.get("name"), row.get("ok"), row.get("detail"))
    except (DefinitionError, ValueError, OSError) as error:
        check("engine_config", False, str(error))
    if not runtime_only:
        claude = shutil.which("claude")
        try:
            if not claude:
                raise OSError("Claude Code CLI is not on PATH. See README.md.")
            version = subprocess.run([claude, "--version"], capture_output=True, encoding="utf-8", timeout=15)
            check("claude_code", version.returncode == 0, version.stdout.strip() or version.stderr.strip())
        except (OSError, subprocess.TimeoutExpired) as error:
            check("claude_code", False, str(error))
    ok = all(item["ok"] for item in checks)
    print(json.dumps({"status": "ready" if ok else "not_ready", "root": root, "python": sys.executable,
                      "runtime_only": runtime_only, "checks": checks,
                      "note": "Login, project trust and LLM generation are checked in the Claude Code session."},
                     ensure_ascii=False, indent=2))
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
