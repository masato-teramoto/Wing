"""host — advance / submit / respond の実行。Workflow Engine の手前に立つ。

規則の層（L3）の入口が `Host(root, state, config, stage_runner=<規則の段>)` として使う。この module に CLI は無い
（規則の無い host を外から呼ばせない）。

| 操作 | すること |
|---|---|
| `advance` | 呼出し先を再開点から実行し（`aidd.py call`）、返却（emit / wait / done / fail）を提示する |
| `submit` | emit した Skill の結果を受け取り、検査・保存してから L0 に報告し、続きを advance する |
| `respond` | wait に対する人間の回答を受け取り、記録してから、報告・advance・提示のいずれかを行う |

**この層は L3・L4 を import しない。** 規則が要る段（呼出しの前後・結果の検査と保存・回答の記録・提示）は、
L3 が渡す関数（`stage_runner`）で実行する。定義ファイルに hook は無い（L3 が L0 を import して自分の関数を渡す）。
L4 の規則は、Workflow Engine の GateExecutor が gate.yaml から実行するゲートの中だけで動く。

この層が持つのは次だけである。

- 状態ストアの排他（`aidd_lock`）
- 操作の記録（`host_operations` 欄。操作 ID ごとの進み具合。再送すれば同じ結果を返し、途中からやり直す）
- dispatch の照合（報告しようとしている emit / wait が今のものか）
- L0 への報告と、続きの advance

**繰り返しは持たない。** 1 回の呼出しの前後を扱うだけで、feature ごと・修正の繰り返しは入口 Skill の手順が持つ。
"""

import os
import re
import sys

_BIN = os.path.dirname(os.path.abspath(__file__))
COMMON = os.path.dirname(_BIN)
for _path in (_BIN, os.path.join(COMMON, "lib")):
    if _path not in sys.path:
        sys.path.insert(0, _path)

import aidd_lock  # noqa: E402
import engine_cli  # noqa: E402
import project_state  # noqa: E402
import location_identity  # noqa: E402

OPERATIONS = ("advance", "submit", "respond")
JOURNAL = "host_operations"
_OPERATION_ID = re.compile(r"[A-Za-z0-9][A-Za-z0-9_.:-]{0,127}")
CALL_TIMEOUT = 900  # 呼出しの上限。unit の上限（10 分）とゲートの実行を含む


class HostError(ValueError):
    """hook の段が拒んだ・失敗した。`data` に hook の出力（error / error_code など）を持つ。"""

    def __init__(self, message, data=None):
        self.data = data or {}
        super().__init__(message)


def ensure_idle(state, operation_id=None):
    """終わっていない他の操作が無いこと。`<id>.<n>` は操作 `<id>` の子として扱う。"""
    entries = state.get(JOURNAL, {})

    def own(key):
        return operation_id is not None and (key == operation_id or operation_id.startswith(key + "."))

    if any(not own(key) and entry.get("status") != "finished" for key, entry in entries.items()):
        raise ValueError("a host operation is incomplete; retry its original operation ID and payload")


class Host:
    def __init__(self, root, state_path=None, config=None, stage_runner=None):
        self.root = os.path.realpath(root)
        self.state_path = os.path.realpath(state_path or os.path.join(self.root, ".aidd/phase-progress.json"))
        self.config = os.path.abspath(config or COMMON)
        self.stage_runner = stage_runner

    # --- 段（L3・L4 の規則）------------------------------------------------

    def stage(self, name, gate=None, **data):
        """規則の段を、規則の層が渡した `stage_runner` で実行する。`gate` は段の材料の unit のゲート。"""
        if self.stage_runner is None:
            raise HostError("no rule layer is attached; use the host through the rule layer's entry (stage_runner)")
        data.update(stage=name, root=self.root, state=self.state_path, gate=gate)
        output = self.stage_runner(name, data) or {}
        if not isinstance(output, dict):
            raise HostError("stage `%s` must return a JSON object" % name)
        return output

    # --- L0 の実行 ---------------------------------------------------------

    def engine(self, command, call=None, item=None, **options):
        timeout = CALL_TIMEOUT if command == "call" else 60
        return engine_cli.invoke(self.root, self.state_path, command, call, item or None, config=self.config,
                                 timeout=timeout, **options)

    def matching(self, action, item, receipt):
        """報告しようとしている dispatch が、今の emit / wait であること。今の unit を返す。"""
        if not isinstance(receipt, dict) or not receipt.get("id"):
            raise ValueError("the actual L0 dispatch is required")
        status = self.engine("status", receipt.get("call"), item)
        if status.get("dispatch") != receipt:
            raise ValueError("stale or unissued dispatch")
        unit = status["pending"]
        if (unit.get("event") or "") != (action or "") or (unit.get("item") or "") != (item or ""):
            raise ValueError("dispatch belongs to another action/item")
        return unit

    # --- 操作の記録 --------------------------------------------------------

    def _journal(self):
        return dict(project_state.read(self.state_path).get(JOURNAL, {}))

    def _save(self, operation_id, entry):
        entries = self._journal()
        entries[operation_id] = entry
        project_state._write(self.state_path, {JOURNAL: entries})

    def _begin(self, kind, action, item, payload, actor):
        """操作 ID を検査し、記録を返す。同じ内容の再送なら記録を、違う内容なら拒む。"""
        operation_id = payload.get("operation_id")
        if not isinstance(operation_id, str) or not _OPERATION_ID.fullmatch(operation_id):
            raise ValueError("a stable operation_id is required")
        request = {"kind": kind, "payload": payload, "actor": actor, "event": action, "item": item,
                   "root": self.root, "state": self.state_path}
        entry = self._journal().get(operation_id)
        if entry and not location_identity.same_request(entry["request"], request):
            raise ValueError("operation ID already used with different content")
        if not (entry and entry["status"] == "finished"):
            ensure_idle(project_state.read(self.state_path), operation_id)
        self.stage("guard", operation=kind, action=action, item=item, operation_id=operation_id)
        return operation_id, request, entry

    # --- advance ----------------------------------------------------------

    def advance(self, call=None, action="", item=""):
        with aidd_lock.hold(self.state_path):
            ensure_idle(project_state.read(self.state_path))
            self.stage("guard", operation="advance", action=action, item=item)
            resolved = self.stage("resolve", operation="advance", call=call, action=action, item=item)
            call = resolved.get("call") or call or action
            action = resolved.get("action", action)
            return self._advance(call, action, item)

    def _advance(self, call, action, item):
        for _ in range(100):
            status = self.engine("status", call, item)
            pending = status.get("pending")
            before = self.stage("advance-before", (pending or {}).get("gate"), call=call, action=action, item=item,
                                pending=pending)
            if before.get("stop"):
                return before["stop"]
            failed = False
            try:
                outcome = self.engine("call", call, (pending or {}).get("item") or item)
            except engine_cli.RuntimeFailure as error:
                outcome, failed = error.data, True
            after = self.stage("advance-after", outcome.get("gate"), call=call, action=action, item=item,
                               pending=pending, outcome=outcome, failed=failed)
            if after.get("complete") == "ok":
                receipt = outcome.get("dispatch")
                gate = outcome.get("gate")
                note = after.get("note")
                if (failed or outcome.get("status") not in ("emit", "wait") or not receipt or not gate
                        or not isinstance(note, str) or not note.strip()):
                    raise ValueError("only a live gate unit may be completed, and only with a reason")
                unit = self.matching(outcome.get("event"), outcome.get("item") or item, receipt)
                if unit.get("gate") != gate:
                    raise ValueError("hook completion belongs to another gate")
                self.engine("report", receipt["call"], outcome.get("item") or item, result="ok",
                            dispatch_id=receipt["id"], note=note)
                continue
            return after.get("output") or dict(outcome, allowed_actions=[] if failed else outcome.get("allowed_actions", []))
        raise ValueError("too many gate units were completed without the host agent")

    # --- submit -----------------------------------------------------------

    def submit(self, action, item, payload, actor=""):
        with aidd_lock.hold(self.state_path):
            operation_id, request, entry = self._begin("submit", action, item, payload, actor)
            if entry and entry["status"] == "finished":
                return dict(entry["output"], replayed=True)
            if not entry:
                receipt = payload.get("dispatch")
                unit = self.matching(action, item, receipt)
                if receipt["status"] != "emit" or unit["type"] != "skill":
                    raise ValueError("submit requires an emitted Skill")
                prepared = self.stage("submit-prepare", unit.get("gate"), action=action, item=item, unit=unit,
                                      receipt=receipt, result=payload["result"], operation_id=operation_id)
                # The prepare stage may schedule a redo after an upstream edit. Do not
                # prepare an operation against a receipt that it invalidated.
                self.matching(action, item, receipt)
                entry = {"status": "prepared", "request": request, "dispatch": receipt, "unit": unit,
                         "result": prepared["result"]}
                self._save(operation_id, entry)
            receipt = entry["dispatch"]
            if entry["status"] == "prepared":
                self.matching(action, item, receipt)
                applied = self.stage("submit-apply", entry["unit"].get("gate"), action=action, item=item,
                                     unit=entry["unit"], receipt=receipt, result=payload["result"],
                                     report=entry["result"], operation_id=operation_id)
                entry.update(status="saved", pending_output=applied.get("output"))
                self._save(operation_id, entry)
            if entry["status"] == "saved":
                # L0 deduplicates this exact dispatch/result even if its reply was lost.
                self.engine("report", receipt["call"], item, result=entry["result"], dispatch_id=receipt["id"])
                entry["status"] = "reported"
                self._save(operation_id, entry)
            if entry["result"] == "ok":
                output = self._advance(receipt["call"], action, item)
            else:
                output = dict(entry.get("pending_output") or {"status": entry["result"], "allowed_actions": []})
            return self._finish(operation_id, entry, output)

    # --- respond ----------------------------------------------------------

    def respond(self, action, item, payload, actor=""):
        with aidd_lock.hold(self.state_path):
            operation_id, request, entry = self._begin("respond", action, item, payload, actor)
            if entry:
                payload = entry['request']['payload']  # Preserve the original answer bytes on relocation replay.
            if entry and entry["status"] == "finished":
                return dict(entry["output"], replayed=True)
            if not entry:
                gate = self._waiting_gate(payload, item)
                prepared = self.stage("respond-prepare", gate, action=action, item=item, payload=payload, actor=actor,
                                      operation_id=operation_id)
                entry = {"status": "prepared", "request": request, "dispatch": prepared["receipt"],
                         "result": prepared.get("result", "ok"), "decisions": prepared.get("decisions"),
                         "report_first": bool(prepared.get("report_first")), "gate": gate}
                self._save(operation_id, entry)
            receipt = entry["dispatch"]
            gate = entry.get("gate")
            common = dict(action=action, item=item, payload=payload, actor=actor, receipt=receipt,
                          decisions=entry.get("decisions"), report_first=entry.get("report_first"),
                          operation_id=operation_id)
            if entry["status"] == "prepared" and entry.get("report_first"):
                self.engine("report", receipt["call"], item, result="ok", dispatch_id=receipt["id"])
                entry["status"] = "answered"
                self._save(operation_id, entry)
            if entry["status"] in ("prepared", "answered"):
                applied = self.stage("respond-apply", gate, **common)
                entry.update(status="saved" if entry["status"] == "prepared" else "reported",
                             then=applied.get("then", "report"))
                self._save(operation_id, entry)
            then = entry.get("then", "report")
            if then == "output":
                output = self.stage("respond-output", gate, **common)["output"]
            elif then == "advance":
                output = self._advance(receipt["call"], action, item)
            else:
                if entry["status"] == "saved":
                    self.engine("report", receipt["call"], item, result=entry["result"], dispatch_id=receipt["id"])
                    entry["status"] = "reported"
                    self._save(operation_id, entry)
                if then == "report-then" and not entry.get("reported_stage"):
                    # A rule step that must follow the report (e.g. restarting a task after its review).
                    self.stage("respond-reported", gate, **common)
                    entry["reported_stage"] = True
                    self._save(operation_id, entry)
                output = self._advance(receipt["call"], action, item)
            return self._finish(operation_id, entry, output)

    def _waiting_gate(self, payload, item):
        """回答が答える wait のゲート（段の宛先を選ぶため）。呼出し先は payload の expected / dispatch から。"""
        call = (payload.get("expected") or {}).get("call") or (payload.get("dispatch") or {}).get("call")
        if not call:
            return None
        try:
            return (self.engine("status", call, item).get("pending") or {}).get("gate")
        except (ValueError, OSError):
            return None

    def _finish(self, operation_id, entry, output):
        output = dict(output, operation_id=operation_id, operation_applied=True)
        entry.update(status="finished", output=output)
        self._save(operation_id, entry)
        return output
