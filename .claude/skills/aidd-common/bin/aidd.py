#!/usr/bin/env python3
"""汎用ランナーの CLI 入口。**`event_handler` の実体である。**

    python3 .claude/skills/aidd-common/bin/aidd.py <サブコマンド> [オプション]

| サブコマンド | すること |
|---|---|
| `validate` | events / flows / gates をスキーマに照らして検査し、一覧する |
| `status` | 再開点（次に実行する unit）を示す。**何も実行しない** |
| `call <名前>` | その flow（または flows・event）を再開点から実行する。`type: skill` に当たったら「次にやること」を出して止まる |
| `report` | `call` が出した unit の結果（`ok` / `fail` / `wait`）を書き戻す |
| `redo` | 記録を落として、その範囲をやり直せるようにする（差戻し・再ゲート） |

コマンドの SKILL.md に書く `event_handler.call(<名前>)` は、この `call` サブコマンドである。

### `--item`

feature ごとに何度も呼ぶイベント（例: `requirements-authoring`）は、**`--item <feature 名>`
を付けて feature の数だけ呼ぶ**。ループの位置と回数は呼び出し側（コマンドの SKILL.md）が
決める。`status` / `report` / `redo` にも同じ `--item` を渡す（無いと別の記録を指してしまう）。
`--item` を付けずに呼べば、これまでどおり 1 回だけ走る。

終了コード

| 値 | 意味 |
|---|---|
| 0 | flow を最後まで通した / 記録した |
| 10 | 人間待ちで止まった（`wait`） |
| 20 | ホストのエージェントが実行する unit を出した（`emit`） |
| 1 | 失敗・設定の誤り |

このファイルを含め `bin/` の中に、フェーズ・feature・承認という語彙は現れない。
それらは設定ファイル（events / flows / gates）と `scripts/` の側にある。

ログは統一エンベロープの JSONL を追記する。出力先と閾値は **`.aidd/logging.yaml`** が持つ。
書式と ID の持ち回りは `log.py` を見る。
"""

import argparse
import json
import os
import sys

# 出力・エラー出力を UTF-8 に固定する（Windows の既定ロケール cp932 等でも、
# 日本語を含む出力で `UnicodeEncodeError` を起こさないため）。Python 3.7+ の
# `reconfigure` が無い環境ではそのまま既定のストリームを使う。
for _stream in (sys.stdout, sys.stderr):
    if hasattr(_stream, "reconfigure"):
        _stream.reconfigure(encoding="utf-8", errors="replace")

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'lib'))
import aidd_lock

import config as config_module  # noqa: E402
import flow as flow_module  # noqa: E402
import log as log_module  # noqa: E402
import state as state_module  # noqa: E402
from orchestrator import Orchestrator, ReportRejected  # noqa: E402

EXIT_OK = 0
EXIT_ERROR = 1
EXIT_WAIT = 10
EXIT_EMIT = 20

DEFAULT_CONFIG = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DEFAULT_STATE = ".aidd/phase-progress.json"


def main(argv=None):
    parser = argparse.ArgumentParser(
        prog="aidd", description="events / flows / gates を実行する汎用ランナー"
    )
    parser.add_argument(
        "--config", default=DEFAULT_CONFIG, help="設定ファイル（events.yaml / flows.yaml / gates.yaml）の置き場"
    )
    parser.add_argument("--state", default=DEFAULT_STATE, help="状態ストアのパス")
    parser.add_argument("--root", default=".", help="出力ルート（相対パスの基準）")
    sub = parser.add_subparsers(dest="subcommand", required=True)

    def add(name, help_text):
        # 実行のたびに付けるオプションはサブコマンド側に置く。グローバルに置くと
        # `call --json` の指定がサブパーサの既定値で打ち消される。
        child = sub.add_parser(name, help=help_text)
        child.add_argument("--json", action="store_true", help="結果を JSON で出す")
        child.add_argument(
            "--log-config", default=None, help="ログ設定（既定 .aidd/logging.yaml）"
        )
        child.add_argument(
            "--log-level",
            default=None,
            choices=sorted(log_module.ORDER),
            help="`output.level` を上書きする（debug は既定では出さない）",
        )
        child.add_argument("--log-echo", action="store_true", help="ログを stderr にも流す")
        return child

    add("validate", "設定ファイルを検査する")

    child = add("status", "再開点を見る")
    child.add_argument("--call", help="呼び出し名（省略時は current.call）")
    child.add_argument("--item", default=None, help="feature 名など。ループの中の呼び出しを見るとき")

    child = add("call", "flow / flows / event を再開点から実行する")
    child.add_argument("name", nargs="?", help="flow・flows・event の名前")
    child.add_argument("--item", default=None, help="feature 名など。ループの中を呼ぶとき")

    child = add("report", "unit の結果を書き戻す")
    child.add_argument("--call")
    child.add_argument("--item", default=None)
    child.add_argument("--result", required=True, choices=state_module.RESULTS)
    child.add_argument("--note", default=None)
    child.add_argument("--dispatch-id", help="Identity returned by the actual emit/wait")
    child.add_argument(
        "--detail",
        default=None,
        help="`終了` 行に載せる キー=値（例: \"出力=specs/login/requirements.md\" / "
             "\"指摘=3 回数=1\" / \"判断=修正 判断者=山田 修正主体=AI\"）",
    )

    child = add("redo", "記録を落としてやり直せるようにする")
    child.add_argument("--call")
    child.add_argument("--flow", default=None)
    child.add_argument("--event", default=None)
    child.add_argument("--item", default=None, help="この feature だけ落とす（省略時は全 item）")

    args = parser.parse_args(argv)
    try:
        return _dispatch(args)
    except (
        config_module.ConfigError,
        state_module.StateError,
        log_module.LogError,
        ReportRejected,
        ValueError,
    ) as error:
        _fail(args, str(error))
        return EXIT_ERROR


def _dispatch(args):
    state_path = args.state if os.path.isabs(args.state) else os.path.join(os.path.abspath(args.root), args.state)
    with aidd_lock.hold(state_path):
        return _dispatch_locked(args)


def _dispatch_locked(args):
    config = config_module.load(args.config)
    root = os.path.abspath(args.root)
    state_path = args.state if os.path.isabs(args.state) else os.path.join(root, args.state)
    state = state_module.State.load(state_path)
    state.path = state_path

    if args.subcommand == "validate":
        # The log settings are part of the configuration a run depends on (doctor uses validate).
        log_module.Settings.load(root, getattr(args, "log_config", None) or os.environ.get("AIDD_LOG_CONFIG"))
        return _validate(args, config)

    if state.events and state.data.get("engine_schema") != 2 and args.subcommand != "status":
        raise state_module.StateError(
            "旧実行記録の移行が必要。references/migration.md を参照する。"
            "過去の成功印を新しいゲート構成へ流用せず、状態・証跡を保持する。"
        )
    if args.subcommand != "status":
        state.data["engine_schema"] = 2

    # `status` / `redo` は実行しないため、ログを汚さない。
    logger = None
    if args.subcommand in ("call", "report"):
        settings = log_module.Settings.load(
            root, getattr(args, "log_config", None) or os.environ.get("AIDD_LOG_CONFIG")
        )
        logger = log_module.Logger(
            settings,
            root,
            getattr(args, "log_level", None) or os.environ.get("AIDD_LOG_LEVEL"),
            echo=getattr(args, "log_echo", False),
        )

    orchestrator = Orchestrator(config, state, root, logger)
    requested = getattr(args, "name", None) or getattr(args, "call", None)
    call = orchestrator.select(requested)
    item = getattr(args, "item", None)

    if args.subcommand == "status":
        return _status(args, orchestrator, call, item)
    if args.subcommand == "call":
        return _call(args, orchestrator, call, item)
    if args.subcommand == "report":
        return _report(args, orchestrator, call, item)
    if args.subcommand == "redo":
        return _redo(args, orchestrator, call, item)
    raise config_module.ConfigError("不明なサブコマンド: %s" % args.subcommand)


# --- サブコマンド ---------------------------------------------------------


def _run_payload(run):
    return {
        "type": run.type,
        "target": run.target,
        "isAgent": run.is_agent,
        "requiresHuman": run.requires_human,
        "calls": list(run.calls) if run.calls else None,
    }


def _run_label(run):
    flags = "".join(
        f" {label}" for label, on in (("isAgent", run.is_agent), ("requiresHuman", run.requires_human)) if on
    )
    calls = " calls=%d" % len(run.calls) if run.calls else ""
    return "%s: %s%s%s" % (run.type, run.target, flags, calls)


def _validate(args, config):
    flows = []
    for name, entry in config.flows.items():
        if entry.kind == "flow":
            flows.append({"name": name, "kind": "flow", "order": list(entry.event_order)})
        else:
            flows.append({"name": name, "kind": "flows", "order": list(entry.flow_order)})
    gates = [
        {
            "name": gate.name,
            "target_event": gate.target_event,
            "hookPoint": gate.hook_point,
            "run": _run_payload(gate.run),
        }
        for gate in config.gates
    ]
    payload = {
        "config": config.path,
        "events": [
            {"name": name, "run": _run_payload(event.run)}
            for name, event in config.events.items()
        ],
        "flows": flows,
        "gates": gates,
    }
    if args.json:
        _emit_json(payload)
        return EXIT_OK
    print("設定ファイル: %s — 検査に通った（calls整合を含む）" % config.path)
    print("events: %d 件" % len(payload["events"]))
    for name, event in config.events.items():
        print("  %s（%s）" % (name, _run_label(event.run)))
        for hook_point in ("start", "end"):
            for gate in config.gates_for(name, hook_point):
                print("    %-5s %s（%s）" % (hook_point, gate.name, _run_label(gate.run)))
    print("flows: %d 件" % len(flows))
    for entry in flows:
        print("  %s（%s）: %s" % (entry["name"], entry["kind"], " → ".join(entry["order"])))
    print("gates: %d 件" % len(gates))
    return EXIT_OK


def _status(args, orchestrator, call, item):
    event_unit, outcome = orchestrator.pending(call, item)
    total = len(flow_module.plan(orchestrator.config, call, item))
    remaining = len(flow_module.pending(orchestrator.config, call, orchestrator.state, item))
    payload = {
        "call": call,
        "item": item,
        "release": orchestrator.state.release,
        "return_to_call": orchestrator.state.return_to_call,
        "events_total": total,
        "events_remaining": remaining,
        "pending": outcome.unit.describe() if event_unit is not None else None,
        "dispatch": orchestrator.dispatch_for(call, item),
    }
    if args.json:
        _emit_json(payload)
        return EXIT_OK
    print("call: %s（イベント %d / %d 残り）" % (call, remaining, total))
    if event_unit is None:
        print("この呼び出しに残りは無い。")
        return EXIT_OK
    print("再開点: %s" % event_unit.label())
    print("  unit  : %s" % outcome.unit.key)
    print(
        "  実行  : %s（type: %s / target: %s）"
        % (outcome.unit.name, outcome.unit.run.type, outcome.unit.target())
    )
    if outcome.unit.gate:
        print("  ゲート: %s（hookPoint: %s）" % (outcome.unit.gate, outcome.unit.hook_point))
    return EXIT_OK


def _call(args, orchestrator, call, item):
    result = orchestrator.run(call, item)

    if result.status == "done":
        payload = {"status": "done", "call": call, "item": item}
        _report_out(args, payload, "call(%s) を最後まで通した。" % call)
        return EXIT_OK

    unit = result.outcome.unit
    payload = dict(unit.describe())
    payload["status"] = result.status
    payload["call"] = call
    payload["dispatch"] = orchestrator.dispatch_for(call, item)
    payload["label"] = result.event_unit.label()
    if result.outcome.detail:
        payload["detail"] = result.outcome.detail

    if result.status == "emit":
        _report_out(args, payload, _emit_text(payload))
        return EXIT_EMIT
    if result.status == "wait":
        _report_out(args, payload, _wait_text(payload))
        return EXIT_WAIT
    _report_out(args, payload, _fail_text(payload))
    return EXIT_ERROR


def _report(args, orchestrator, call, item):
    unit = orchestrator.report(call, args.result, args.note, args.detail, item, args.dispatch_id)
    if unit is None:
        _report_out(args, {"status": "done", "call": call, "item": item}, "書き戻す unit が無い。")
        return EXIT_OK
    payload = dict(unit)
    payload["status"] = "recorded"
    payload["result"] = args.result
    _report_out(args, payload, "記録した: %s ← %s" % (unit['unit'], args.result))
    return EXIT_OK


def _redo(args, orchestrator, call, item):
    removed = orchestrator.redo(call, args.flow, args.event, item)
    payload = {
        "status": "redo",
        "call": call,
        "flow": args.flow,
        "event": args.event,
        "item": item,
        "removed": removed,
    }
    _report_out(args, payload, "%d unit の成功印を無効化した。履歴は保持した（call %s）。" % (removed, call))
    return EXIT_OK


# --- 出力 ----------------------------------------------------------------


def _emit_text(payload):
    lines = [
        "次にやること — %s" % payload["label"],
        "  type  : %s" % payload["type"],
        "  target: %s" % payload["target"],
        "  unit  : %s" % payload["unit"],
    ]
    if payload.get("item"):
        lines.append("  item  : %s" % payload["item"])
    if payload.get("gate"):
        lines.append("  ゲート: %s（hookPoint: %s）" % (payload["gate"], payload["hookPoint"]))
    if payload.get("isAgent"):
        lines.append("  起動: check-runner を別コンテキストで起動し、target の合成 Skill を渡す")
    elif payload.get("type") == "skill":
        lines.append("  起動: target の SKILL.md を読み、手順を実行する")
    if payload.get("calls"):
        lines.append("  calls : %s" % ", ".join(payload["calls"]))
    lines.append("")
    lines.append("実行したら結果を書き戻す:")
    item_flag = " --item %s" % payload["item"] if payload.get("item") else ""
    lines.append("  aidd.py report --call %s%s --result ok" % (payload["call"], item_flag))
    return "\n".join(lines)


def _wait_text(payload):
    lines = ["人間待ちで止まった — %s" % payload["label"]]
    if payload.get("gate"):
        lines.append("  ゲート: %s（hookPoint: %s）" % (payload["gate"], payload["hookPoint"]))
    if payload.get("detail"):
        lines.append("")
        lines.append(payload["detail"])
    lines.append("")
    lines.append("人間の回答を受けてから書き戻す:")
    item_flag = " --item %s" % payload["item"] if payload.get("item") else ""
    lines.append("  aidd.py report --call %s%s --result ok" % (payload["call"], item_flag))
    return "\n".join(lines)


def _fail_text(payload):
    lines = ["失敗したため flow を終える — %s" % payload["label"]]
    if payload.get("gate"):
        lines.append("  ゲート: %s（hookPoint: %s）" % (payload["gate"], payload["hookPoint"]))
    if payload.get("detail"):
        lines.append("")
        lines.append(payload["detail"])
    return "\n".join(lines)


def _report_out(args, payload, text):
    if args.json:
        _emit_json(payload)
    else:
        print(text)


def _emit_json(payload):
    print(json.dumps(payload, ensure_ascii=False, indent=2))


def _fail(args, message):
    if args.json:
        _emit_json({"status": "error", "message": message})
    else:
        print("エラー: %s" % message, file=sys.stderr)


if __name__ == "__main__":
    sys.exit(main())
