"""状態ストアの読み書き。

状態を持つのは Workflow Engine だけであり、その置き場がこのモジュールである。
ファイルの中身（`phases` / `steering` / `features` / `blockers` …）は**案件側の語彙**であって
ランナーは解釈しない。実行に必要な次の欄は、初回実行時に作成する。

| 欄 | 用途 |
|---|---|
| `release` | 使っているリリース識別子 |
| `current.call` | 実行中 / 直近の呼び出し名（flow または action の名前） |
| `current.return_to_call` | 差戻し先の呼び出し名（無ければ null） |
| `events[]` | 実行済み unit の記録。**再開点はここから導く** |
| `current.pending` | 実際に発行した emit/wait の識別情報 |
| `engine_reports` | 発行 ID ごとの受領済み報告。再送時に同じ結果を返す |
| `trace` / `engine_schema` | 実行ログの関連付けと状態書式 |

**繰り返しのコレクション（`features[]` など）はこのモジュールが読むことはない。**
どの item をどの順で扱うか・何回繰り返すかはランナーが決めない。Skill の手順（L3 の入口 Skill）が
繰り返しの 1 回ごとに `--item` を付けて呼ぶ。`features[]` を読むのは `scripts/`（実行計画の提示・上流の確認）
の側である。
"""

import datetime
import copy
import json
import os
import uuid

RESULTS = ("ok", "fail", "wait")


class StateError(ValueError):
    pass


def invalidate_runner(data, note="explicit schema migration"):
    """状態書式の移行で、ランナー所有欄を戻す（新しい状態ファイル用。元のファイルは変えない）。

    実行記録は消さずに、各 unit の最新の記録に無効化を追記する。`current` と `trace` を空にし、
    状態書式を今の版にする。案件の欄（ランナー所有でない欄）には触れない。
    """
    events = data.setdefault("events", [])
    latest = {e["unit"]: e for e in events if isinstance(e, dict) and isinstance(e.get("unit"), str)}
    for entry in latest.values():
        events.append({**entry, "result": "invalidated", "at": now(), "note": note})
    data.update(engine_schema=2, current={})
    data.pop("trace", None)
    data.pop("loops", None)
    return data


def now():
    return datetime.datetime.now().astimezone().replace(microsecond=0).isoformat()


class State:
    def __init__(self, path, data):
        self.path = path
        self.data = data
        self._loaded_owned = self._owned(data)

    @staticmethod
    def _owned(data):
        current = data.get("current") or {}
        if not isinstance(current, dict):
            raise StateError("current はオブジェクトでなければならない")
        return copy.deepcopy({
            "events": data.get("events", []),
            "trace": data.get("trace"),
            "engine_schema": data.get("engine_schema"),
            "engine_reports": data.get("engine_reports", {}),
            "current": {key: current.get(key) for key in ("call", "return_to_call", "pending")},
        })

    # --- 読み込み・保存 -------------------------------------------------

    @classmethod
    def load(cls, path):
        if not os.path.exists(path):
            return cls(path, {})
        with open(path, encoding="utf-8") as handle:
            text = handle.read().strip()
        if not text:
            return cls(path, {})
        try:
            data = json.loads(text)
        except ValueError as error:
            raise StateError("%s を JSON として読めない: %s" % (path, error))
        if not isinstance(data, dict):
            raise StateError("%s のルートはオブジェクトでなければならない" % path)
        return cls(path, data)

    def save(self):
        directory = os.path.dirname(os.path.abspath(self.path))
        if directory:
            os.makedirs(directory, exist_ok=True)
        # Child scripts own project fields. Reload them before writing runner
        # fields, so a start gate's update survives emit/wait/fail/done saves.
        disk = self.load(self.path).data
        if self._owned(disk) != self._loaded_owned:
            raise StateError("ランナー所有欄が外部で変更された。並列実行せず再読み込みする")
        merged = copy.deepcopy(disk)
        owned = self._owned(self.data)
        merged["events"] = owned["events"]
        merged["engine_schema"] = owned["engine_schema"]
        merged["engine_reports"] = owned["engine_reports"]
        merged.pop("loops", None)  # 第 2 版の繰り返しの欄。第 3 版では使わない
        if owned["trace"] is None:
            merged.pop("trace", None)
        else:
            merged["trace"] = owned["trace"]
        current = merged.setdefault("current", {})
        for key, value in owned["current"].items():
            if value is None:
                current.pop(key, None)
            else:
                current[key] = value
        merged["updated_at"] = now()
        self.data = merged
        temporary = self.path + ".tmp"
        with open(temporary, "w", encoding="utf-8") as handle:
            json.dump(self.data, handle, ensure_ascii=False, indent=2)
            handle.write("\n")
        os.replace(temporary, self.path)
        self._loaded_owned = self._owned(self.data)

    # --- ランナーの実行欄 -----------------------------------------------

    @property
    def release(self):
        return self.data.get("release")

    @property
    def call(self):
        return (self.data.get("current") or {}).get("call")

    @property
    def return_to_call(self):
        return (self.data.get("current") or {}).get("return_to_call")

    def set_call(self, name):
        current = self.data.setdefault("current", {})
        current["call"] = name

    def set_return_to_call(self, name):
        current = self.data.setdefault("current", {})
        current["return_to_call"] = name

    def issue(self, call, unit, status, config_hash, detail=None):
        value = {"call": call, "unit": unit.key, "event": unit.action, "item": unit.item,
                 "status": status, "config_sha256": config_hash, "detail": detail}
        previous = self.data.get("current", {}).get("pending") or {}
        if previous.get('id') and all(previous.get(k) == v for k, v in value.items()):
            return previous
        value["id"] = uuid.uuid4().hex
        self.data.setdefault("current", {})["pending"] = value
        return value

    def forget_dispatch(self):
        self.data.setdefault("current", {}).pop("pending", None)

    @property
    def records(self):
        """実行済み unit の記録（保存形式のためキーは `events`）。"""
        records = self.data.get("events")
        return records if isinstance(records, list) else []

    def record(self, unit, result, note=None):
        if result not in RESULTS:
            raise StateError("result は %s のいずれか（実際: %r）" % (" / ".join(RESULTS), result))
        entry = {
            "at": now(),
            "unit": unit.key,
            "flow": unit.flow,
            "event": unit.action,  # 保存形式のためキーは `event`（中身はアクション名）
            "item": unit.item,
            "gate": unit.gate,
            "hookPoint": unit.hook_point,
            "type": unit.run.type,
            "result": result,
        }
        if note:
            entry["note"] = note
        self.data.setdefault("events", []).append(entry)
        return entry

    def mark(self, key, result, fields=None, note=None):
        """unit を持たない印（アクションの通過など）を記録する。"""
        if result not in RESULTS:
            raise StateError("result は %s のいずれか（実際: %r）" % (" / ".join(RESULTS), result))
        entry = {"at": now(), "unit": key, "result": result}
        entry.update(fields or {})
        if note:
            entry["note"] = note
        self.data.setdefault("events", []).append(entry)
        return entry

    def result_of(self, unit_key):
        """同じ unit の**最後の**結果を返す。再ゲートは新しい記録として積まれる。"""
        for entry in reversed(self.records):
            if entry.get("unit") == unit_key:
                return entry.get("result")
        return None

    def migrate_flow(self, old, new, action_names):
        """Copy each unit of `old/<action>[...]` to `new/<action>[...]`. Append-only.

        The last record of every unit is appended again under the new flow name;
        the old records stay as history. Invalidated units are not carried over.
        Returns the list of (old key, new key) pairs that were appended.
        """
        latest = {}
        for entry in self.records:
            key = entry.get("unit")
            if isinstance(key, str):
                latest[key] = entry
        moved = []
        for key, entry in latest.items():
            action = next((name for name in action_names if key.startswith("%s/%s[" % (old, name))), None)
            if action is None or entry.get("result") == "invalidated":
                continue
            target = new + key[len(old):]
            existing = latest.get(target)
            if existing is not None and existing.get("result") != "invalidated":
                if existing.get("result") != entry.get("result"):
                    raise StateError("移行先 `%s` に別の結果（%s）がある。移行元 `%s` は %s"
                                     % (target, existing.get("result"), key, entry.get("result")))
                continue
            copied = {k: v for k, v in entry.items() if k not in ("at", "note")}
            copied.update(at=now(), unit=target, note="migrated from %s" % key)
            if "flow" in copied:
                copied["flow"] = new
            self.data.setdefault("events", []).append(copied)
            moved.append((key, target))
        return moved

    def clear(self, unit_keys):
        """Append invalidations; retain previous execution evidence."""
        count = 0
        for key in dict.fromkeys(unit_keys):
            previous = next((e for e in reversed(self.records) if e.get("unit") == key), None)
            if previous is None or previous.get("result") == "invalidated":
                continue
            entry = {k: previous[k] for k in ("unit", "flow", "event", "item", "gate", "hookPoint", "type") if k in previous}
            entry.update(at=now(), result="invalidated", note="redo requested")
            self.data.setdefault("events", []).append(entry)
            count += 1
        return count
