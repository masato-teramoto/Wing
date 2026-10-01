"""Issue the L3 completion seal after the existing L4 acceptance checks.

L4 chooses the evidence and validates its meaning. L3 subsequently checks the
saved identity and bytes without importing the task-quality implementation.
"""
from pathlib import Path

import code_review_mcp as adapter
import gate_exchange
import implementation_code_review as code_review
import implementation_completion as completion
import implementation_requests as requests
import implementation_store as store
import implementation_task_review as task_review
import task_code_review
import task_code_review_mcp as mcp
import task_quality
import task_quality_inputs as inputs
import task_quality_storage as storage


EXECUTION_BINDINGS = [
    'task_quality', 'code_review', 'review_baseline', 'feature_records',
    'quality_instructions', 'retries', 'retry_operations', 'baseline', 'protected',
    'allowed_paths', 'repair_findings', 'previous_execution',
]


class Evidence:
    """Collect the immutable dependency closure, including reused review rounds."""

    def __init__(self, context, execution):
        self.context = context
        self.root = context.root
        self.execution = execution
        self.paths = set()
        self.operations = set()
        self.visited = set()
        self.active = set()

    def add(self, execution_id, number, name):
        storage.path(self.root, execution_id, number, name)  # validate the allowed artifact name
        self.paths.add(storage.directory(execution_id, number) + '/' + name)

    def read(self, execution_id, number, name):
        self.add(execution_id, number, name)
        return storage.read(self.root, execution_id, number, name)

    def bundle(self, execution_id, number, name):
        manifest = self.read(execution_id, number, name)
        for member in manifest['files']:
            self.add(execution_id, number, member)

    def exchange(self, gate, kind, attempt=None):
        name = gate_exchange.record_path(self.context, gate, kind, attempt)
        self.paths.add(name)

    def collect(self, kind, execution_id, number, attempt=None):
        key = kind, execution_id, number
        if key in self.active:
            raise ValueError('cyclic task completion evidence reference')
        if key in self.visited:
            return
        self.active.add(key)
        if kind == 'specification':
            self.bundle(execution_id, number, 'manifest.json')
            request = self.read(execution_id, number, 'request.json')
            previous = request.get('previous')
            if previous:
                task_quality.previous_snapshot(self.root, previous, request['target']['feature'], request['scope'])
                self.collect(kind, previous['execution_id'], previous['round'])
        elif kind == 'code':
            self.bundle(execution_id, number, 'code-manifest.json')
            request = self.read(execution_id, number, 'code-request.json')
            receipt = self.read(execution_id, number, 'code-review.json')
            # A reused receipt still depends on the original submitted review,
            # not only its later copy. Attempts have separate exchange records.
            self.exchange(code_review.REVIEW, 'published', attempt)
            if not receipt.get('reused_from'):
                self.exchange(code_review.REVIEW, 'result', attempt)
                submitted = gate_exchange.result(self.context, code_review.REVIEW, attempt=attempt)
                if submitted['result'] != receipt['host_review']:
                    raise ValueError('submitted task code review differs from its sealed receipt')
                self.operations.add(gate_exchange.record_operation(self.context, code_review.REVIEW, 'result', submitted))
            reference = request['mcp']['reference']
            self.collect('mcp', reference['execution_id'], reference['round'])
            # Prior failed/repair rounds need not have a human acceptance. Their
            # immutable review and MCP evidence still support retained findings.
            for previous in ((request.get('previous') or {}).get('reference'), receipt.get('reused_from')):
                if previous:
                    task_code_review.load(self.context, self.execution, previous, current=False)
                    self.collect(kind, execution_id, previous['round'], previous['attempt'])
        elif kind == 'mcp':
            self.bundle(execution_id, number, 'mcp-manifest.json')
        else:
            raise ValueError('unknown task completion evidence kind')
        self.active.remove(key)
        self.visited.add(key)


def dependencies(context, execution, accepted=True):
    """Select only immutable history plus the current inputs actually checked by L4."""
    specification = bool(inputs.scope_of(execution))
    review = code_review.enabled(execution)
    evidence = Evidence(context, execution)
    execution_id = execution['execution_id']
    directory = store.BASE + '/runs/' + execution_id
    operations, current_artifacts, environment_files = [], [], []
    optional_checks = set()
    if specification:
        number = task_review.pointer(execution)['round']
        evidence.collect('specification', execution_id, number)
        if accepted:
            evidence.add(execution_id, number, 'acceptance.json')
        request = evidence.read(execution_id, number, 'request.json')
        evidence.exchange(task_review.GENERATE, 'published')
        evidence.exchange(task_review.GENERATE, 'result')
        submitted = gate_exchange.result(context, task_review.GENERATE)
        evidence.operations.add(gate_exchange.record_operation(context, task_review.GENERATE, 'result', submitted))
        saved, _ = task_quality.load(context, execution, task_review.pointer(execution))
        if task_quality.generate(context, request, submitted['result']) != saved:
            raise ValueError('submitted task specification differs from its sealed result')
        evidence.paths.update(directory + '/' + name for name in request['inputs']['checks'])
        optional_checks.update(('red.json', 'green.json', 'verify.json', 'result.json'))
    if review:
        number = code_review.pointer(execution)['round']
        evidence.collect('code', execution_id, number, code_review.pointer(execution)['attempt'])
        if accepted:
            evidence.add(execution_id, number, 'code-acceptance.json')
        request = evidence.read(execution_id, number, 'code-request.json')
        evidence.paths.update(request['inputs']['checks'])
        optional_checks.update(('red.json', 'green.json', 'verify.json'))
        current_artifacts = list(task_code_review.RULE_FILES) + [
            str(Path(mcp.__file__).with_name(name)) for name in mcp.RULES]
        environment_files = [{'variable': 'AIDD_CODE_REVIEW_SETTINGS',
                              'default': str(Path(adapter.__file__).with_name('code_review.json'))}]
    if accepted and (specification or review):
        number, name = task_review.response_slot(execution)
        response = evidence.read(execution_id, number, name)
        evidence.exchange(task_review.WAIT, 'published')
        evidence.exchange(task_review.WAIT, 'answer')
        answer = gate_exchange.answer(context, task_review.WAIT)
        if (any(answer.get(key) != response.get(key) for key in ('operation_id', 'action', 'actor', 'data', 'expected'))
                or answer.get('dispatch_id') != response['expected'].get('dispatch_id')):
            raise ValueError('submitted task answer differs from its recorded human response')
        operations.append(response['operation_id'])
    return {'artifacts': sorted(evidence.paths), 'current_artifacts': sorted(current_artifacts),
            'current_optional_artifacts': sorted(directory + '/' + name for name in optional_checks),
            'inventories': [False, True] if specification or review else [],
            'environment_files': environment_files, 'execution_bindings': EXECUTION_BINDINGS,
            'operations': sorted(evidence.operations | set(operations))}


def accept(context):
    """Accept or explicitly exempt, then seal; an empty revision reuses its generation seal."""
    execution = requests.preflight(context)
    if store.empty_revision(context, execution):
        return completion.require(context, execution, current=True)
    # These L4 selectors also reject malformed policy and invalid exemptions.
    if inputs.scope_of(execution) or code_review.enabled(execution):
        task_review.accept(context)
    selected = dependencies(context, execution)
    candidate = completion.capture(context, execution, **selected)
    task_review.require_accepted(context, execution, current=True)
    if dependencies(context, execution) != selected:
        raise ValueError('task completion evidence dependencies changed during validation')
    return completion.publish(context, execution, candidate)
