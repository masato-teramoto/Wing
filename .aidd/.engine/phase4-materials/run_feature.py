"""Draft -> waiting(questions) -> answer -> full -> completed for one feature.

usage: python run_feature.py <feature> <short>   (cwd = project root)
"""
import json, os, re, subprocess, sys, uuid
HERE = os.path.dirname(os.path.abspath(__file__))
feature, short = sys.argv[1], sys.argv[2]
T = os.environ['TEMP']
P = 'specs/%s/requirements.md' % feature
PY = sys.executable
ENTRY = '.claude/skills/aidd-common/scripts/aidd_entry.py'
spec = json.load(open(os.path.join(HERE, feature + '.json'), encoding='utf-8'))
Q = spec['qprefix']


def call(args):
    out = subprocess.run([PY, '-X', 'utf8', '-B', ENTRY, '/aidd-requirements'] + args, capture_output=True, text=True, encoding='utf-8')
    d = json.loads(out.stdout)
    if d.get('status') != 'ok':
        raise SystemExit('FAIL %s: %s' % (args[:3], json.dumps(d, ensure_ascii=False)[:600]))
    return d


def build(mode):
    out = subprocess.run([PY, '-X', 'utf8', os.path.join(HERE, 'build.py'), feature, mode], capture_output=True, text=True, encoding='utf-8')
    if out.returncode:
        raise SystemExit(out.stderr)
    return int(out.stdout.strip())


# questions from the handoff file
qtext = open('_handoff/questions-phase4-remaining.md', encoding='utf-8').read()
qs = []
for m in re.finditer(r'^(' + re.escape(Q) + r'-\d{3})（([^）]*)）\n((?:(?!Q-RQ-|\n|-{5}).*\n)+)', qtext, re.M):
    qs.append({'id': m.group(1), 'target': P, 'location': m.group(2), 'question': m.group(3).strip().replace('\n', ''),
               'reason_unanswered': '承認済み入力に具体的な値が無く、推測で書けないため'})
assert qs, 'no questions'
# answers from the saved answer file
atext = open('.aidd/.engine/answer-20261002-1347.txt', encoding='utf-8').read()
blk = re.search(r'^(' + re.escape(Q) + r'-001：[\s\S]*?)(?=^-{10}|\Z)', atext, re.M).group(1).strip()
assert blk.count(Q + '-') >= len(qs), (blk.count(Q + '-'), len(qs))

d = json.load(open(os.path.join(T, 'claude_%s1.json' % short), encoding='utf-8'))['result']
n = build('draft')
pay = {'operation_id': uuid.uuid4().hex, 'dispatch': d['dispatch'], 'result': {
    'status': 'waiting', 'targets': [P], 'questions': qs, 'open_placeholders': n, 'changed_findings': [], 'return_candidates': [],
    'summary': '要求文と feature 一覧から書ける範囲で下書きを作成した。未確定は質問 %d 件（_handoff/questions-phase4-remaining.md と同じ）。' % len(qs)}}
fn = '.aidd/.engine/rq-%s-generate-submit-1.json' % short
json.dump(pay, open(fn, 'w', encoding='utf-8'), ensure_ascii=False, indent=2)
r = call(['submit', '--action', 'requirements-authoring-generate', '--item', feature, '--payload', fn])
print('waiting', r['result'].get('status'))
fn = '.aidd/.engine/rq-%s-answer-1.json' % short
json.dump({'operation_id': uuid.uuid4().hex, 'answers': [blk]}, open(fn, 'w', encoding='utf-8'), ensure_ascii=False, indent=2)
call(['answer', '--action', 'requirements-authoring-generate', '--item', feature, '--payload', fn, '--actor', 'Junichi Noumi'])
r = call(['advance', '--call', 'requirements-authoring-generate', '--item', feature])['result']
print('after answer', r.get('status'), r.get('unit'))
n = build('full')
pay = {'operation_id': uuid.uuid4().hex, 'dispatch': r['dispatch'], 'result': {
    'status': 'completed', 'targets': [P], 'questions': [], 'open_placeholders': n, 'changed_findings': [], 'return_candidates': [],
    'summary': spec['summary']}}
fn = '.aidd/.engine/rq-%s-generate-submit-2.json' % short
json.dump(pay, open(fn, 'w', encoding='utf-8'), ensure_ascii=False, indent=2)
r = call(['submit', '--action', 'requirements-authoring-generate', '--item', feature, '--payload', fn])
json.dump(r, open(os.path.join(T, 'claude_%s3.json' % short), 'w', encoding='utf-8'), ensure_ascii=False)
res = r['result']; c = res.get('context') or {}; s = c.get('snapshot') or {}
print('completed ->', res.get('status'), res.get('isAgent'), n)
print(json.dumps({'snapshot_path': c.get('snapshot_path'), 'findings_path': c.get('findings_path'), 'inspection_path': c.get('inspection_path'),
                  'event': s.get('event'), 'run': s.get('run'), 'at': s.get('at'), 'calls': res.get('calls')}, ensure_ascii=False))
