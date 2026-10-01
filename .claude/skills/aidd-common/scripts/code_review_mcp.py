"""ACE transport and strict normalization. No workflow progression or approval.

Each file uses an isolated MCP session in a bounded child process. The parent
can stop a stalled HTTP/SSE call at the shared deadline, retaining received RPC
responses. Only filename/content cross the network boundary.
"""
from concurrent.futures import ThreadPoolExecutor, as_completed
import hashlib
import json
import math
import os
from pathlib import Path
import subprocess
import sys
import time
import urllib.error
import urllib.request
import urllib.parse

PROTOCOL = '2025-06-18'
GROUPS = ('ace-review', 'metrics')
METRICS = ('loc', 'ccn', 'cognitiveComplexity', 'maintainabilityIndex')
MAX_BYTES = 512000
MAX_RESPONSE = 8 * 1024 * 1024


def digest(data):
    return hashlib.sha256(data).hexdigest()


class ReviewError(Exception):
    def __init__(self, kind, message):
        super().__init__(message)
        self.kind = kind


def settings(path=None):
    path = path or os.environ.get('AIDD_CODE_REVIEW_SETTINGS') or Path(__file__).with_name('code_review.json')
    raw = Path(path).read_bytes()
    value = json.loads(raw)
    required = {'schema', 'endpoint', 'tool', 'timeout_seconds', 'budget_seconds', 'workers',
                'extensions', 'classifications', 'blocking_metrics'}
    if (not isinstance(value, dict) or set(value) - (required | {'bearer_token_env'}) or required - set(value)
            or type(value['schema']) is not int or value['schema'] != 2
            or not isinstance(value['endpoint'], str) or not value['endpoint'].startswith(('https://', 'http://'))
            or value['tool'] != 'ace_review_code'):
        raise ValueError('code review settings require schema 2 and the ACE tool/endpoint')
    endpoint = urllib.parse.urlsplit(value['endpoint'])
    if not endpoint.hostname or endpoint.username or endpoint.password or endpoint.fragment:
        raise ValueError('MCP endpoint must have a host and no embedded credentials/fragment')
    for key, upper in (('timeout_seconds', 300), ('budget_seconds', 480), ('workers', 8)):
        if type(value.get(key)) is not int or not 1 <= value[key] <= upper:
            raise ValueError('code review %s must be an integer in 1..%d' % (key, upper))
    extensions = value['extensions']
    if (not isinstance(extensions, list) or not extensions or len(extensions) != len(set(extensions))
            or any(not isinstance(e, str) or not e.startswith('.') for e in extensions)):
        raise ValueError('code review extensions must be a nonempty unique list')
    classes = value['classifications']
    if (not isinstance(classes, dict) or not classes or
            any(not isinstance(k, str) or not k.strip() or v not in ('critical', 'major', 'minor', 'info') for k, v in classes.items())
            or classes.get('Bug Prevention') not in ('critical', 'major') or classes.get('Security') not in ('critical', 'major')
            or not isinstance(value['blocking_metrics'], list) or set(value['blocking_metrics']) - set(METRICS)):
        raise ValueError('explicit classification severities and known blocking metrics required')
    if 'bearer_token_env' in value and (not isinstance(value['bearer_token_env'], str) or not value['bearer_token_env'].isidentifier()):
        raise ValueError('bearer_token_env must name an environment variable, never a credential')
    return value, digest(raw)


class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        raise ReviewError('http', 'MCP redirects are not allowed')


class Session:
    def __init__(self, config, record=None):
        self.config, self.record = config, record or (lambda event: None)
        self.session_id, self.counter, self.server = None, 0, None
        self.schema_sha256 = None

    def _post(self, message, timeout):
        headers = {'Content-Type': 'application/json', 'Accept': 'application/json, text/event-stream',
                   'MCP-Protocol-Version': PROTOCOL}
        if self.session_id:
            headers['Mcp-Session-Id'] = self.session_id
        variable = self.config.get('bearer_token_env')
        if variable:
            token = os.environ.get(variable)
            if not token:
                raise ReviewError('auth', 'configured MCP credential is unavailable')
            headers['Authorization'] = 'Bearer ' + token
        request = urllib.request.Request(self.config['endpoint'], data=json.dumps(message).encode('utf-8'),
                                         headers=headers, method='POST')
        try:
            with urllib.request.build_opener(NoRedirect).open(request, timeout=timeout) as response:
                self.session_id = response.headers.get('Mcp-Session-Id') or self.session_id
                if 'id' not in message:
                    return None
                body = bytearray()
                kind = response.headers.get('Content-Type', '')
                while True:
                    chunk = response.read1(65536)
                    body.extend(chunk)
                    if len(body) > MAX_RESPONSE:
                        raise ReviewError('protocol', 'MCP response exceeds the response size limit')
                    if 'text/event-stream' in kind:
                        try:
                            reply = _response(body.decode('utf-8'), kind, message['id'])
                            break
                        except (ReviewError, UnicodeDecodeError):
                            pass
                    if not chunk:
                        reply = _response(body.decode('utf-8'), kind, message['id'])
                        break
        except urllib.error.HTTPError as error:
            raise ReviewError('auth' if error.code in (401, 403) else 'http', 'MCP HTTP %d' % error.code) from error
        except (TimeoutError, OSError) as error:
            reason = getattr(error, 'reason', error)
            kind = 'timeout' if isinstance(reason, TimeoutError) or 'timed out' in str(reason) else 'connection'
            # Do not echo request headers, credentials or proxy configuration.
            raise ReviewError(kind, 'MCP ' + kind) from error
        self.record({'method': message['method'], 'reply': reply})
        return reply

    def _rpc(self, method, params, timeout):
        self.counter += 1
        reply = self._post({'jsonrpc': '2.0', 'id': self.counter, 'method': method, 'params': params}, timeout)
        if 'error' in reply or not isinstance(reply.get('result'), dict):
            raise ReviewError('protocol', 'MCP %s did not return a result object' % method)
        return reply['result']

    def open(self):
        result = self._rpc('initialize', {'protocolVersion': PROTOCOL, 'capabilities': {},
                           'clientInfo': {'name': 'aidd-task-review', 'version': '2'}}, self.config['timeout_seconds'])
        if result.get('protocolVersion') != PROTOCOL:
            raise ReviewError('protocol', 'unsupported negotiated MCP protocol')
        self.server = result.get('serverInfo')
        if (not isinstance(self.server, dict) or
                any(not isinstance(self.server.get(k), str) or not self.server[k].strip() for k in ('name', 'version'))):
            raise ReviewError('protocol', 'MCP server identity/version is missing')
        self._post({'jsonrpc': '2.0', 'method': 'notifications/initialized'}, self.config['timeout_seconds'])
        listing = self._rpc('tools/list', {}, self.config['timeout_seconds'])
        candidates = [t for t in listing.get('tools', []) if isinstance(t, dict) and t.get('name') == self.config['tool']]
        if len(candidates) != 1 or set(candidates[0].get('inputSchema', {}).get('required', [])) != {'filename', 'content'}:
            raise ReviewError('schema', 'ACE tool/input schema unavailable')
        self.schema_sha256 = digest(json.dumps(candidates[0], sort_keys=True, ensure_ascii=False).encode('utf-8'))
        return self

    def review(self, filename, content):
        result = self._rpc('tools/call', {'name': self.config['tool'], 'arguments': {'filename': filename, 'content': content}},
                           self.config['timeout_seconds'])
        return tool_data(result, filename)


def tool_data(result, filename):
    if result.get('isError'):
        raise ReviewError('tool', 'ACE tool returned isError')
    data = result.get('structuredContent')
    if data is None:
        texts = [c.get('text') for c in result.get('content', []) if isinstance(c, dict) and c.get('type') == 'text']
        try:
            data = json.loads(texts[0]) if len(texts) == 1 else None
        except (ValueError, TypeError):
            data = None
    if (not isinstance(data, dict) or set(data) != {'filename', 'issueGroups'}
            or data['filename'] != filename or not isinstance(data['issueGroups'], dict)):
        raise ReviewError('schema', 'ACE result lacks the exact filename/issueGroups contract')
    return data


def _response(body, kind, expected_id):
    candidates = [body]
    if 'text/event-stream' in kind:
        candidates = []
        # SSE events may have multiple data lines; ignore comments/notifications.
        for event in body.replace('\r\n', '\n').split('\n\n')[:-1]:
            candidates.append('\n'.join(line[5:].lstrip() for line in event.splitlines() if line.startswith('data:')))
    for item in candidates:
        try:
            value = json.loads(item)
        except ValueError:
            continue
        if (isinstance(value, dict) and value.get('jsonrpc') == '2.0'
                and type(value.get('id')) is int and value['id'] == expected_id
                and ('result' in value) != ('error' in value)):
            return value
    raise ReviewError('protocol', 'matching JSON-RPC response is missing')


def number(value):
    return type(value) in (int, float) and math.isfinite(value)


def normalize(path, data, config):
    findings, incomplete = [], []
    groups = data['issueGroups']
    if set(groups) != set(GROUPS):
        incomplete.append({'path': path, 'reason': 'unknown or missing issue group'})
    for group in GROUPS:
        value = groups.get(group)
        if (not isinstance(value, dict) or value.get('status') != 'fulfilled'
                or set(value) - {'status', 'issues', 'truncatedMessage'} or not isinstance(value.get('issues'), list)):
            incomplete.append({'path': path, 'group': group, 'reason': 'rejected or malformed issue group'})
            continue
        if value.get('truncatedMessage') or ('truncatedMessage' in value and not isinstance(value['truncatedMessage'], str)):
            incomplete.append({'path': path, 'group': group, 'reason': 'truncated issue group'})
        for issue in value['issues']:
            expected = {'startLine', 'endLine', 'id', 'message', 'classification'} if group == 'ace-review' else {'startLine', 'endLine', 'functionName', *METRICS}
            if (not isinstance(issue, dict) or set(issue) != expected
                    or any(not number(issue[k]) or int(issue[k]) != issue[k] for k in ('startLine', 'endLine'))
                    or not 1 <= issue['startLine'] <= issue['endLine']):
                incomplete.append({'path': path, 'group': group, 'reason': 'malformed issue fields/lines'})
                continue
            rows = []
            if group == 'ace-review':
                if (any(not isinstance(issue[k], str) or not issue[k].strip() for k in ('id', 'message', 'classification'))
                        or issue['classification'] not in config['classifications']):
                    incomplete.append({'path': path, 'group': group, 'reason': 'unknown classification or missing issue text'})
                    continue
                rows = [(issue['id'], issue['classification'], issue['message'], config['classifications'][issue['classification']])]
            else:
                if not isinstance(issue['functionName'], str) or not issue['functionName'].strip():
                    incomplete.append({'path': path, 'group': group, 'reason': 'missing functionName'})
                    continue
                for metric in METRICS:
                    entry = issue[metric]
                    if (not isinstance(entry, dict) or set(entry) != {'value', 'threshold', 'violated'}
                            or not number(entry['value']) or not number(entry['threshold']) or type(entry['violated']) is not bool):
                        incomplete.append({'path': path, 'group': group, 'reason': 'malformed metric: ' + metric})
                    elif entry['violated']:
                        rows.append((metric, 'Metrics', '%s: %s=%s (threshold %s)' % (issue['functionName'], metric, entry['value'], entry['threshold']),
                                     'major' if metric in config['blocking_metrics'] else 'minor'))
            for rule, classification, message, severity in rows:
                identity = [path, group, rule, issue['startLine'], issue['endLine'], message]
                identifier = 'ACE-' + digest(json.dumps(identity, ensure_ascii=False).encode('utf-8'))[:24]
                findings.append({'id': identifier, 'aspect': 'mcp-static', 'severity': severity,
                    'location': '%s:%d-%d' % (path, issue['startLine'], issue['endLine']), 'summary': message,
                    'evidence': '%s / %s / %s' % (group, rule, classification),
                    'suggestion': '修正後にACEとタスクレビューを再実行する。',
                    'source': {'provider': 'ace', 'path': path, 'rule': rule, 'group': group, 'classification': classification}})
    # Identical service rows are one finding with a deterministic identity.
    return list({f['id']: f for f in findings}.values()), incomplete


def _isolated(entry, config, deadline):
    path, content, sha = entry
    record = {'path': path, 'sha256': sha, 'trace': [], 'error': None, 'engine': None}
    remaining = deadline - time.monotonic()
    if remaining <= 0:
        record['error'] = {'kind': 'timeout', 'message': 'MCP review budget exhausted before dispatch'}
        return record
    process = subprocess.Popen([sys.executable, '-X', 'utf8', '-B', str(Path(__file__).resolve()), '--worker'],
        stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
        creationflags=getattr(subprocess, 'CREATE_NO_WINDOW', 0))
    payload = json.dumps({'config': config, 'filename': Path(path).name, 'content': content}, ensure_ascii=False).encode('utf-8')
    try:
        output, _ = process.communicate(payload, timeout=max(0.001, deadline - time.monotonic()))
    except subprocess.TimeoutExpired:
        process.kill()
        output, _ = process.communicate()
        record['error'] = {'kind': 'timeout', 'message': 'MCP review exceeded its total budget'}
    final = None
    for line in output.splitlines():
        try:
            event = json.loads(line)
        except ValueError:
            continue
        if 'method' in event:
            record['trace'].append(event)
        elif 'done' in event:
            final = event
    if final is not None:
        record['engine'] = final['engine']
        if record['error'] is None:
            record['error'] = final['error']
    elif record['error'] is None:
        record['error'] = {'kind': 'connection', 'message': 'MCP worker ended before a complete response'}
    return record


def review_entries(entries, config, saved=None, save=None):
    """Bounded calls over already frozen contents; persist each received file independently."""
    saved = dict(saved or {})
    deadline = time.monotonic() + config['budget_seconds']
    pending = [entry for entry in entries if entry[0] not in saved]
    with ThreadPoolExecutor(max_workers=config['workers']) as pool:
        futures = [pool.submit(_isolated, entry, config, deadline) for entry in pending]
        for future in as_completed(futures):
            record = future.result()
            if save:
                save(record)
            saved[record['path']] = record
    return {path: saved[path] for path, _, _ in entries}


def _worker():
    payload = json.load(sys.stdin)
    def emit(value):
        print(json.dumps(value, ensure_ascii=False, allow_nan=False), flush=True)
    session = Session(payload['config'], emit)
    error = None
    try:
        session.open().review(payload['filename'], payload['content'])
    except ReviewError as exc:
        error = {'kind': exc.kind, 'message': str(exc)}
    except Exception:
        error = {'kind': 'protocol', 'message': 'MCP response could not be decoded'}
    emit({'done': True, 'engine': {'provider': 'ace', 'tool': payload['config']['tool'],
          'server': session.server, 'protocol': PROTOCOL, 'tool_schema_sha256': session.schema_sha256}, 'error': error})


if __name__ == '__main__' and sys.argv[1:] == ['--worker']:
    _worker()
