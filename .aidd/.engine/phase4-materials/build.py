"""Build requirements.md for the remaining 4 features from the template.

usage: python build.py <feature> <draft|full>
draft: grounded parts only (before answers), full: with answers.
"""
import datetime, os, re, sys, json
HERE = os.path.dirname(os.path.abspath(__file__))
feature, mode = sys.argv[1], sys.argv[2]
spec = json.load(open(os.path.join(HERE, feature + '.json'), encoding='utf-8'))
tpl = open('Templates/specs/_template/requirements.md', encoding='utf-8').read()
now = datetime.datetime.now().strftime('%Y-%m-%dT%H:%M:%S+09:00')
s = tpl.replace('{{FEATURE_NAME}}', feature).replace('{{ISO_8601_TIMESTAMP_JST}}', now)


def rep(a, b):
    global s
    assert s.count(a) == 1, a[:60]
    s = s.replace(a, b)


def bullets(items, indent='  '):
    return '\n'.join(indent + '- ' + x for x in items)


Q = spec['qprefix']
rep('> _書き方_: 確定した要件だけを書き、作成の手順やレビューの記録は残さない。\n',
    '> _書き方_: 確定した要件だけを書き、作成の手順やレビューの記録は残さない。\n\n> _出典の表記_: 「' + Q + '-xxx」は本 feature の作成中の質問への回答者（Junichi Noumi）の回答。依存先の feature への言及は、その `specs/<feature>/requirements.md`（approved）による。\n')
m = spec[mode]
rep('- **背景**: <REQ_INTRO_BACKGROUND>', '- **背景**: ' + m['background'])
rep('- **対象ユーザー**: <REQ_INTRO_TARGET_USER>', '- **対象ユーザー**: ' + m['target_user'])
rep('- **期待する変化**: <REQ_INTRO_EXPECTED_CHANGE>', '- **期待する変化**: ' + m['change'])
rep('- **対象業務**: <REQ_BIZFLOW_TARGET>', '- **対象業務**: ' + spec['biz_target'])
if mode == 'full':
    rep('  - <REQ_BIZFLOW_BEFORE_N>', bullets(m['before']))
    rep('  - <REQ_BIZFLOW_AFTER_N>', bullets(m['after']))
    rep('  - <REQ_BIZFLOW_HUMAN_STEP_N>', bullets(m['human']))
rep('  - <REQ_SCOPE_IN_N>', bullets(m['in']))
rep('  - <REQ_SCOPE_OUT_N>', bullets(m['out']))
rep('  - <REQ_SCOPE_ADJACENT_N>', bullets(m['adjacent']))
rep('- <REQ_OUTSCOPE_ITEM_N>', '\n'.join('- ' + x for x in m['outscope']))
if m.get('assumption'):
    rep('  - <REQ_ASSUMPTION_N>', bullets(m['assumption']))
rep('  - <REQ_DEPENDENCY_N>', bullets(spec['dependency']))
if m.get('open'):
    rep('  - <REQ_OPEN_ISSUE_N>', bullets(m['open']))
a = s.index('### 要件 1:'); b = s.index('## 非機能要件')
reqs = open(os.path.join(HERE, feature + '-' + mode + '.md'), encoding='utf-8').read()
s = s[:a] + reqs.rstrip('\n') + '\n\n' + s[b:]
base = [('| <REQ_NFR_PERFORMANCE> | <REQ_NFR_PERFORMANCE_VERIFY> |', '| `steering/non-functional.md` 準拠（既存 WiNG の水準に従い、本 feature 固有の目標値は設けない） | 総合テスト（工程ごとの試験仕様書。`steering/tech.md` の `### 基本方針`） |'),
        ('| <REQ_NFR_AVAILABILITY> |', '| `steering/non-functional.md` 準拠（保守運用は既存 WiNG の運用に従う） |'),
        ('| <REQ_NFR_OPERATION> |', '| `steering/non-functional.md` 準拠（ログは `### ログ方針` に従う） |'),
        ('| <REQ_NFR_SECURITY> | <REQ_NFR_SECURITY_VERIFY> |', '| `steering/security.md` 準拠' + spec.get('security_note', '') + ' | 総合テスト（工程ごとの試験仕様書） |')]
for x, y in base:
    rep(x, y)
if mode == 'full':
    src = Q + '-' + spec['nfr_q'] + '。property-basic-info と同じ'
    rep('| <REQ_NFR_AVAILABILITY_VERIFY> |', '| <REQ_NFR_AVAILABILITY_VERIFY>（不要：既存 WiNG の運用に従い、本 feature では検証しない — ' + src + '） |')
    rep('| <REQ_NFR_OPERATION_VERIFY> |', '| <REQ_NFR_OPERATION_VERIFY>（不要：既存 WiNG の運用に従い、本 feature では検証しない — ' + src + '） |')
    rep('| <REQ_NFR_ACCESSIBILITY> | <REQ_NFR_ACCESSIBILITY_VERIFY> |', '| <REQ_NFR_ACCESSIBILITY>（不要：社内と協力会社が日本語で使う既存画面に合わせる — ' + src + '） | <REQ_NFR_ACCESSIBILITY_VERIFY>（不要：社内と協力会社が日本語で使う既存画面に合わせる — ' + src + '） |')
    rep('| <REQ_NFR_I18N> | <REQ_NFR_I18N_VERIFY> |', '| <REQ_NFR_I18N>（不要：社内と協力会社が日本語で使う既存画面に合わせる — ' + src + '） | <REQ_NFR_I18N_VERIFY>（不要：社内と協力会社が日本語で使う既存画面に合わせる — ' + src + '） |')
    rep('| <REQ_NFR_PRIVACY> | <REQ_NFR_PRIVACY_VERIFY> |', '| ' + spec['privacy'] + ' | 総合テスト（工程ごとの試験仕様書） |')
    rep('| <REQ_NFR_AUDIT> | <REQ_NFR_AUDIT_VERIFY> |', spec['audit'])
os.makedirs('specs/' + feature, exist_ok=True)
open('specs/' + feature + '/requirements.md', 'w', encoding='utf-8').write(s)
left = [x for x in re.finditer(r'<[A-Z][A-Z0-9_]*>', s) if '不要：' not in s[x.end():x.end() + 6]]
print(len(left))
