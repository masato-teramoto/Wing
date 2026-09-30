"""main_flow policy adapter. The generic runner never imports this module.

Phase/output metadata belongs to contracts/main_flow.json. L3 and L4 receive
resolved inputs from the host, not this module or the mutable project state.
"""
import json
import os
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "lib"))
import aidd_lock

import artifacts as artifact_io
import feature_manifest
import project_state

CONTRACT_PATH = Path(__file__).resolve().parents[1] / "contracts/main_flow.json"
CONTRACT = json.loads(CONTRACT_PATH.read_text(encoding="utf-8"))
if CONTRACT.get("schema") != 1:
    raise ValueError("unsupported main_flow contract")
RULES = CONTRACT["phases"]
STEERING = tuple(Path(p).stem for p in CONTRACT["steering"])
DOCS = tuple(CONTRACT["docs"])
PHASES = {name: (rule["number"], ".aidd/gates/phase-%s-%s.md" % (rule["number"], name)) for name, rule in RULES.items()}
PROCESS_OF = {event: name for name, rule in RULES.items() for event in (rule["generate"], rule["repair"])}
PROCESS_OF.update({"requirements-plan": "requirements", "design-plan": "design", "tasks-plan": "tasks",
                   "requirements-cross-gate": "requirements", "design-cross-gate": "design", "tasks-gate-run": "tasks",
                   "implement-gate-run": "implement"})


class Context:
    draft_manifest = False

    def __init__(self, root=None, state_path=None, event=None, item=None):
        self.root = os.path.abspath(root or os.environ.get("AIDD_ROOT") or os.getcwd())
        self.state_path = state_path or os.environ.get("AIDD_STATE") or self.path(".aidd/phase-progress.json")
        self.flow = os.environ.get("AIDD_FLOW") or ""
        self.event = event if event is not None else os.environ.get("AIDD_EVENT", "")
        self.process = PROCESS_OF.get(self.event, "")
        # An explicitly selected event starts a new context. Do not leak the
        # current gate's feature into a cross-phase/cross-feature lookup.
        self.item = item if item is not None else (os.environ.get("AIDD_ITEM", "") if event is None else "")
        self.gate = os.environ.get("AIDD_GATE", "")
        self.hook_point = os.environ.get("AIDD_HOOK_POINT", "")
        self.unit = os.environ.get("AIDD_UNIT", "")
        self.event_unit = os.environ.get("AIDD_EVENT_UNIT", "")

    def locked(self):
        return aidd_lock.hold(self.state_path)

    def path(self, relative):
        return str(artifact_io.resolve(self.root, relative))

    @property
    def phase(self):
        return PHASES.get(self.process, (None, None))[0]

    @property
    def gate_record(self):
        record = PHASES.get(self.process, (None, None))[1]
        return self.path(record) if record else None

    @property
    def is_cross(self):
        return self.event.endswith("-cross-gate")

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

    def artifacts(self):
        if self.process == 'implement':
            import implementation_requests
            import implementation_evidence
            feature = implementation_requests.feature_of(self)
            if self.event in implementation_requests.TASK_EVENTS:
                import implementation_store
                return implementation_store.read_execution(self)['allowed_paths']
            return [implementation_evidence.review_path(feature)]
        if self.process not in RULES:
            raise ValueError("unknown main_flow event: %s" % self.event)
        rule = RULES[self.process]
        if not rule["per_feature"]:
            if self.item:
                raise ValueError("event does not take a feature: %s" % self.event)
            return list(rule["outputs"])
        if self.item:
            self.feature()
            return [p.format(feature=self.item) for p in rule["outputs"]]
        return self._all_specs(self.process)

    def _all_specs(self, document):
        return ["specs/%s/%s.md" % (entry["name"], document) for entry in self.features()]

    def _dependency_designs(self):
        entries = self.features()
        by_name = {entry["name"]: entry for entry in entries}
        found = set()
        pending = list(self.feature()["depends_on"])
        while pending:
            name = pending.pop()
            if name not in found:
                found.add(name)
                pending.extend(by_name[name]["depends_on"])
        return ["specs/%s/design.md" % entry["name"] for entry in entries if entry["name"] in found]

    def authoring_inputs(self):
        if self.process == "intake":
            root = Path(self.path(".aidd/rfp"))
            return sorted(p.relative_to(self.root).as_posix() for p in root.rglob('*')
                          if p.is_file() and not any(s.startswith('.') for s in p.relative_to(root).parts))
        return [path for path in self.upstream() if self.process != "tasks" or path not in DOCS]

    def upstream(self):
        """Combine fixed contract inputs with scope-specific specs and dependencies.

        The JSON upstream array intentionally contains only the fixed paths.
        prerequisites.check applies its approved check to this resolved list.
        """
        if self.process == 'implement':
            import implementation_requests
            return implementation_requests.upstream(self, implementation_requests.feature_of(self))
        if self.process not in RULES:
            raise ValueError("unknown main_flow event: %s" % self.event)
        inputs = list(RULES[self.process]["upstream"])
        if self.process == "design":
            inputs += (["specs/%s/requirements.md" % self.item] + self._dependency_designs()) if self.item else self._all_specs("requirements")
        if self.process == "docs":
            inputs += self._all_specs("requirements") + self._all_specs("design")
        if self.process == "tasks":
            inputs += (["specs/%s/%s.md" % (self.item, doc) for doc in ("requirements", "design")] if self.item else self._all_specs("requirements") + self._all_specs("design"))
        if self.is_cross:
            inputs += self.artifacts()
        return list(dict.fromkeys(inputs))


front_matter = artifact_io.fields


def inspection_digest(context, target):
    if context.process == 'implement':
        import implementation_evidence
        return implementation_evidence.review_digest(context, target)
    return artifact_io.protected_digest(context.path(target))


def status_of(path):
    fields = front_matter(path)
    return fields.get("status") if fields else None


EXIT_OK, EXIT_FAIL, EXIT_WAIT = 0, 1, 10


def log_keys(**pairs):
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
