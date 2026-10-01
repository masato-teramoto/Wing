"""phase_rules — main_flow の工程の規則と、L3 の ExecutionContext（L0 の ExecutionContext を継ぐ）。

L0 の `execution_context.py` は実行器の間で引き継ぐ文脈（今の Flow / Action / item / ゲート）を持ち、
この module はそれに工程・feature・入出力の展開・上流を足す。L3・L4 の規則 script はこの module を使う。

各アクションは入出力を action.yaml に書く。工程は flow.yaml の flow のうち、生成の Skill
（手順の宣言 `役割: 生成（generate）`）のアクションを持つものであり、flow 名が工程名、並び順が工程番号になる。
feature ごとか（per_feature）は、その工程の生成 Skill の手順の宣言 `繰り返し: feature ごと（per-feature）` が持つ。
L3 は定義を L0 の `execution_context.definitions()` から読む（L3 は L0 を import してよい。逆はしない）。
L3 と L4 は host が解決した入力を受け取り、このモジュールや可変の案件状態から直接引かない。
"""
import l0  # noqa: F401  L0 の枠組みを import できるようにする
import json
import os
from pathlib import Path
import re
import sys

import execution_context as framework  # L0 の枠組み

import artifacts as artifact_io
import feature_manifest
import project_state

COMMON = Path(__file__).resolve().parents[1]
# Phase names are the identifiers of the L3 rules below and in the other scripts.
PHASE_NAMES = ("intake", "steering", "feature", "requirements", "design", "docs", "tasks", "implement")
# Phase 8 task actions write no fixed outputs, so its final review cannot join by outputs.
IMPLEMENT_REVIEW = "implement-gate-run"
ROLES = ("generate", "repair")
# Skill の手順の冒頭の宣言（D18）。L0 は読まない。
_STEPS = re.compile(r"^## 手順[ \t]*\n(.*?)(?=^## |\Z)", re.M | re.S)
_ROLE = re.compile(r"^役割:\s*\S*?（(generate|repair)）\s*$", re.M)
_ROLE_LINE = re.compile(r"^役割:", re.M)
_PER_FEATURE = re.compile(r"^繰り返し:\s*feature ごと（per-feature）\s*$", re.M)
_REPEAT_LINE = re.compile(r"^繰り返し:", re.M)


def skill_declarations(target):
    """`.claude/skills/<target>/SKILL.md` の `## 手順` の宣言（役割・繰り返し）。無ければ {}。"""
    path = COMMON.parent / target / "SKILL.md"
    if not path.is_file():
        return {}
    match = _STEPS.search(path.read_text(encoding="utf-8"))
    if not match:
        return {}
    steps, values = match.group(1), {}
    roles = _ROLE.findall(steps)
    if len(_ROLE_LINE.findall(steps)) != len(roles) or len(roles) > 1:
        raise ValueError("`役割:` must be one of 生成（generate） / 修正（repair）, once, in %s" % path)
    if roles:
        values["role"] = roles[0]
    repeats = _REPEAT_LINE.findall(steps)
    if repeats:
        if len(repeats) != 1 or not _PER_FEATURE.search(steps):
            raise ValueError("`繰り返し:` must be `feature ごと（per-feature）`, once, in %s" % path)
        values["per_feature"] = True
    return values


def skill_role(target):
    """Skill の手順が宣言する役割（generate / repair）。無ければ None。"""
    return skill_declarations(target).get("role")


def skill_per_feature(target):
    """Skill の手順が `繰り返し: feature ごと（per-feature）` を宣言しているか。"""
    return bool(skill_declarations(target).get("per_feature"))


def _normalized(paths):
    return sorted(p.replace("{features}", "{feature}") for p in paths)


def build(data, role_of=skill_role, per_feature_of=skill_per_feature):
    """Phase rules from `validate --json`. Violations name the flow/action/Skill.

    The JSON keys of validate (`events`, `target_event`) are a wire format and stay; they hold actions.
    A phase is a flow whose steps hold its generate/repair actions; `call` is the flow that holds the
    phase flow as a step (Phase 1-3: requirements-init), else the phase flow itself.
    """
    actions = {row["name"]: row for row in data["events"]}
    flows = [row for row in data["flows"] if row["kind"] == "flow"]

    def direct(flow):
        return [step["action"] for step in flow["steps"] if "action" in step]

    def skill(action):
        run = actions[action]["run"]
        return run["target"] if run["type"] == "skill" else None

    roles = {name: role_of(skill(name)) if skill(name) else None for name in actions}
    rules, process_of = {}, {}
    for flow in flows:
        found = {role: [a for a in direct(flow) if roles[a] == role] for role in ROLES}
        if not any(found.values()):
            continue
        name = flow["name"]
        if name not in PHASE_NAMES:
            raise ValueError("flow `%s` holds generate/repair Skills but is not a main_flow phase (%s)"
                             % (name, ", ".join(PHASE_NAMES)))
        for role, names in found.items():
            if len(names) != 1:
                raise ValueError("flow `%s` needs exactly one %s action (aidd-role), found: %s"
                                 % (name, role, ", ".join(names) or "none"))
        generate, repair = found["generate"][0], found["repair"][0]
        if actions[generate]["outputs"] != actions[repair]["outputs"]:
            raise ValueError("flow `%s`: `%s` and `%s` must declare the same outputs" % (name, generate, repair))
        owners = [parent["name"] for parent in flows if {"flow": name} in parent["steps"]]
        if len(owners) > 1:
            raise ValueError("flow `%s` is a step of more than one flow: %s" % (name, ", ".join(owners)))
        outputs = list(actions[generate]["outputs"])
        if name == "implement":
            outputs = list(actions[IMPLEMENT_REVIEW]["outputs"])
        rules[name] = {"number": len(rules) + 1, "generate": generate, "repair": repair,
                       "call": owners[0] if owners else name, "inputs": list(actions[generate]["inputs"]),
                       "outputs": outputs}
        for action in direct(flow):
            if action in process_of:
                raise ValueError("action `%s` belongs to flows `%s` and `%s`" % (action, process_of[action], name))
            process_of[action] = name
    missing = [name for name in PHASE_NAMES if name not in rules]
    if missing:
        raise ValueError("main_flow phases missing from flow.yaml: " + ", ".join(missing))
    if IMPLEMENT_REVIEW not in actions:
        raise ValueError("action `%s` is required for Phase 8" % IMPLEMENT_REVIEW)
    review = [flow["name"] for flow in flows if IMPLEMENT_REVIEW in direct(flow)]
    if len(review) != 1:
        raise ValueError("action `%s` must be in exactly one flow" % IMPLEMENT_REVIEW)
    rules["implement"]["flows"] = {"generate": rules["implement"]["call"], "repair": rules["implement"]["call"],
                                   "review": review[0]}
    for name, rule in rules.items():
        # per_feature comes from the Skill (metadata.aidd-per-feature): the phase's generate Skill; Phase 8
        # the final review's Skill (its outputs are the phase outputs; the task item is a task, not a feature).
        decider = IMPLEMENT_REVIEW if name == "implement" else rule["generate"]
        rule["per_feature"] = bool(skill(decider) and per_feature_of(skill(decider)))
    process_of[IMPLEMENT_REVIEW] = "implement"
    # Actions outside the phase flows (plans, cross gates) join the phase with the same outputs.
    for name, row in actions.items():
        if name in process_of or not row["outputs"]:
            continue
        owners = [phase for phase, rule in rules.items()
                  if rule["outputs"] and _normalized(row["outputs"]) == _normalized(rule["outputs"])]
        if len(owners) == 1:
            process_of[name] = owners[0]
    return {"actions": actions, "rules": rules, "process_of": process_of, "flows": {f["name"]: f for f in flows}}


_LOADED = None


def config():
    global _LOADED
    if _LOADED is None:
        _LOADED = build(framework.definitions(COMMON))
    return _LOADED


def action_row(name):
    try:
        return config()["actions"][name]
    except KeyError:
        raise ValueError("unknown main_flow action: %s" % name) from None


def __getattr__(name):
    # Loaded on first use: importing this module must not start L0.
    if name == "RULES":
        return config()["rules"]
    if name == "PROCESS_OF":
        return config()["process_of"]
    if name == "PHASES":
        return {phase: (rule["number"], ".aidd/gates/phase-%s-%s.md" % (rule["number"], phase))
                for phase, rule in config()["rules"].items()}
    if name == "STEERING":
        return tuple(Path(p).stem for p in config()["rules"]["steering"]["outputs"])
    if name == "DOCS":
        return tuple(config()["rules"]["docs"]["outputs"])
    raise AttributeError(name)


class ExecutionContext(framework.ExecutionContext):
    """L0 の ExecutionContext に工程（process）と、工程の規則による入出力の展開を足す。"""

    # The rollback reopening of the finder reads the draft feature list (repair_requests._discovering).
    draft_manifest = False

    def __init__(self, root=None, state_path=None, action=None, item=None):
        super().__init__(root, state_path, action, item)
        self.process = config()["process_of"].get(self.action, "")

    def path(self, relative):
        return str(artifact_io.resolve(self.root, relative))

    @property
    def phase(self):
        rule = config()["rules"].get(self.process)
        return rule["number"] if rule else None

    @property
    def gate_record(self):
        rule = config()["rules"].get(self.process)
        return self.path(".aidd/gates/phase-%s-%s.md" % (rule["number"], self.process)) if rule else None

    @property
    def is_cross(self):
        return self.action.endswith("-cross-gate")

    @property
    def scope(self):
        if self.process == 'implement':
            import implementation_requests
            return 'feature:' + implementation_requests.feature_of(self)
        return "cross" if self.is_cross else ("feature:" + self.item if self.item else "phase")

    def state(self):
        return project_state.read(self.state_path)

    def features(self):
        return feature_manifest.load(self.root, self.state_path, approved=not self.draft_manifest)

    def blockers(self):
        value = self.state().get("blockers", [])
        if not isinstance(value, list):
            raise ValueError("blockers must be an array")
        return value

    def feature(self):
        result = next((entry for entry in self.features() if entry["name"] == self.item), None)
        if result is None:
            raise ValueError("feature not in approved manifest: %s" % self.item)
        return result

    def _declared(self, key):
        if self.process not in config()["rules"]:
            raise ValueError("unknown main_flow action: %s" % self.action)
        return list(action_row(self.action)[key])

    def gate_targets(self):
        """This gate's inspection targets: its `target_review`, or every output of the action."""
        declared = self.target_review
        if declared is None:
            return self.artifacts()
        return self._selected(declared, "gate `%s`" % self.gate)

    def review_targets(self):
        """What the event's inspection gate reviews and a human approves.

        The inspection gate is the agent skill gate at the action end. Outputs left
        out of its `target_review` are neither inspected nor approved (D6).
        Every phase, Phase 8 included, follows this one rule. Where the action body
        inspects (cross, tasks-gate-run, implement-gate-run) or no inspection gate is
        attached (Phase 8 tasks), nothing narrows it: every output.
        """
        rules = config()["rules"]
        if self.process not in rules or self.is_cross:
            return self.artifacts()
        rule = rules[self.process]
        if self.action not in (rule["generate"], rule["repair"]):
            return self.artifacts()
        patterns = inspection_review(self, self.action)
        other = rule["repair"] if self.action == rule["generate"] else rule["generate"]
        if patterns != inspection_review(self, other):
            raise ValueError("target_review of the inspection gate differs between %s and %s"
                             % (rule["generate"], rule["repair"]))
        if patterns is None:
            return self.artifacts()
        return self._selected([p.replace("{item}", self.item) for p in patterns], "inspection gate")

    def _selected(self, patterns, label):
        """Select outputs by the L0 rule (file, `<dir>/`, `<dir>/**`, `**`); the order is the output order."""
        return framework.select(patterns, self.artifacts(), label, self.action)

    def _dependencies(self):
        entries = self.features()
        by_name = {entry["name"]: entry for entry in entries}
        found = set()
        pending = list(self.feature()["depends_on"])
        while pending:
            name = pending.pop()
            if name not in found:
                found.add(name)
                pending.extend(by_name[name]["depends_on"])
        return [entry["name"] for entry in entries if entry["name"] in found]

    def expand(self, paths, feature):
        """Resolve {feature} (the given feature), {features} and {depends_on} of declared paths."""
        result = []
        for path in paths:
            if "{features}" in path:
                result += [path.replace("{features}", entry["name"]) for entry in self.features()]
            elif "{depends_on}" in path:
                if not self.item:
                    raise ValueError("action needs a feature (--item): %s" % self.action)
                result += [path.replace("{depends_on}", name) for name in self._dependencies()]
            elif "{feature}" in path:
                if not feature:
                    raise ValueError("action needs a feature (--item): %s" % self.action)
                result.append(path.replace("{feature}", feature))
            else:
                result.append(path)
        return list(dict.fromkeys(result))

    def _item_feature(self):
        """The item as {feature}. An item on an action without {feature} is a wrong --item."""
        row = action_row(self.action)
        if not any("{feature}" in p or "{depends_on}" in p for p in row["inputs"] + row["outputs"]):
            if self.item:
                raise ValueError("action does not take a feature: %s" % self.action)
            return ""
        if self.item:
            self.feature()
        return self.item

    def artifacts(self):
        if self.process == 'implement':
            import implementation_requests
            import implementation_evidence
            feature = implementation_requests.feature_of(self)
            if self.action in implementation_requests.TASK_ACTIONS:
                import implementation_store
                return implementation_store.read_execution(self)['allowed_paths']
            return [implementation_evidence.review_path(feature)]
        outputs = self._declared("outputs")
        return self.expand(outputs, self._item_feature())

    def _inputs(self):
        inputs = self._declared("inputs")
        if self.process == 'implement':
            import implementation_requests
            return self.expand(inputs, implementation_requests.feature_of(self))
        return self.expand(inputs, self._item_feature())

    def authoring_inputs(self):
        """Files under declared directories (not approved) followed by the approved inputs."""
        files = []
        for directory in (p for p in self._inputs() if p.endswith("/")):
            base = Path(self.path(directory.rstrip("/")))
            files += sorted(p.relative_to(self.root).as_posix() for p in base.rglob('*')
                            if p.is_file() and not any(s.startswith('.') for s in p.relative_to(base).parts))
        # docs gate Phase 7 but are not an authoring input of tasks (paths.md §6).
        docs = config()["rules"]["docs"]["outputs"] if self.process == "tasks" else ()
        return files + [path for path in self.upstream() if path not in docs]

    def upstream(self):
        """The event's declared inputs, resolved. Directories are not approved inputs.

        prerequisites.check applies its approved check to this resolved list.
        """
        if self.process == 'implement':
            import implementation_requests
            return implementation_requests.upstream(self, implementation_requests.feature_of(self))
        return [p for p in self._inputs() if not p.endswith("/")]


front_matter = artifact_io.fields

_DECLARATIONS = {}


def target_declarations(context):
    """Gate `target_review` declarations from L0 (environment in a unit, else validate)."""
    raw = os.environ.get("AIDD_GATE_TARGETS")
    if raw:
        return json.loads(raw)
    key = (context.root, context.state_path)
    if key not in _DECLARATIONS:
        import engine_client
        _DECLARATIONS[key] = [
            {"gate": g["name"], "event": g["target_event"], "hookPoint": g["hookPoint"], "type": g["run"]["type"],
             "isAgent": g["run"]["isAgent"], "target_review": g["target_review"]}
            for g in engine_client.validate(context)["gates"] if g.get("target_review") is not None]
    return _DECLARATIONS[key]


def check_gate_targets(context):
    """A rule gate's written target_review must equal its event's review targets.

    Rule gates do not narrow on their own: every gate of an action except the
    machine-check scripts declares the value of the event's inspection gate, so
    an edit that would change nothing fails instead. Omitted means no check.
    """
    raw = os.environ.get("AIDD_TARGET_REVIEW")
    if not raw or not context.gate:
        return
    declared = json.loads(raw)
    inspected = None
    rule = config()["rules"].get(context.process)
    if rule and context.action in (rule["generate"], rule["repair"]):
        inspected = inspection_review(context, context.action)
        if inspected is not None and [p.replace("{item}", context.item) for p in inspected] == declared:
            return
    if declared == ["**"] and inspected in (None, ["**"]):
        return
    expected, actual = context.review_targets(), context.gate_targets()
    if actual != expected:
        raise ValueError(
            "gate `%s`: target_review %s は、このイベント（%s）の検査対象 %s と同じ値にする。"
            "検査対象を変えるときは、このイベントに差さった全ゲート（機械検査 script を除く）の target_review を同じ値にする"
            % (context.gate, json.dumps(declared, ensure_ascii=False), context.action,
               json.dumps(expected, ensure_ascii=False)))


def gate_context():
    """The Context of a rule gate, after check_gate_targets (fails the gate on a mismatch)."""
    context = ExecutionContext()
    try:
        check_gate_targets(context)
    except (ValueError, OSError, KeyError) as error:
        fail(str(error))
    return context


def inspection_review(context, action):
    """The inspection gate's raw `target_review` for an action, or None when omitted."""
    rows = [d for d in target_declarations(context) if d["event"] == action and d["hookPoint"] == "end"
            and d["type"] == "skill" and d["isAgent"]]
    values = {tuple(d["target_review"]) for d in rows}
    if len(values) > 1:
        raise ValueError("inspection gates of %s declare different target_review" % action)
    return list(values.pop()) if values else None


def inspection_digest(context, target):
    if context.process == 'implement':
        import implementation_evidence
        return implementation_evidence.review_digest(context, target)
    return artifact_io.protected_digest(context.path(target))


def status_of(path):
    fields = front_matter(path)
    return fields.get("status") if fields else None


# The script protocol (exit codes 0 / 1 / 10, `AIDD-LOG:` lines) belongs to L0.
EXIT_OK, EXIT_FAIL, EXIT_WAIT = framework.EXIT_OK, framework.EXIT_FAIL, framework.EXIT_WAIT
log_keys, ok, fail = framework.log_keys, framework.ok, framework.fail
