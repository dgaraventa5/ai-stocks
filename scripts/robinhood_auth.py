"""The executor's OWN Robinhood login — self-renewing (2026-10-05, Dom).

Why this exists. The scheduled executor used to borrow the OAuth token that
Claude Code keeps in the macOS Keychain. That token is renewed only when a
Claude session touches the Robinhood connector, so an unattended run found it
expired: every run from 2026-09-15 to 09-22 died on HTTP 401. This module
gives the executor a login of its own that it renews itself, in a Keychain
item Claude Code never reads or writes. Renewing the borrowed token instead
was rejected: OAuth servers may rotate the refresh token on use, which would
silently break Claude Code's own stored login.

What it is NOT. It places no orders and names no order tool (rule 29: one
order writer, scripts/execute_ticket.py). It only obtains and renews the
bearer token that file's transport sends.

Use:
  python3 scripts/robinhood_auth.py login    # Dom, once: browser approval
  python3 scripts/robinhood_auth.py status   # expiry only — never the token
  python3 scripts/robinhood_auth.py logout   # delete the stored login

Stdlib only. Endpoints are discovered from the server's published OAuth
metadata, never hard-coded. Tokens are never printed or logged.
"""
from __future__ import annotations

import base64
import hashlib
import json
import secrets
import subprocess
import sys
import time
import urllib.error
import urllib.parse
import urllib.request

MCP_URL = 'https://agent.robinhood.com/mcp/trading'
METADATA_URL = ('https://agent.robinhood.com/.well-known/'
                'oauth-authorization-server')
KEYCHAIN_SERVICE = 'aistocks-executor-robinhood'
KEYCHAIN_ACCOUNT = 'oauth'
REFRESH_MARGIN_S = 300          # renew when under 5 minutes of life remain
CALLBACK_TIMEOUT_S = 300
LOGIN_HINT = ('run `python3 scripts/robinhood_auth.py login` in a terminal '
              'and approve in the browser')


class LoginRequired(Exception):
    """No stored login, or the server refused to renew it."""


# ------------------------------------------------------------------ keychain

class Keychain:
    """One JSON blob in a generic-password item. The secret is fed to
    `security -i` on stdin so it never appears in a process argument list."""

    def __init__(self, service: str = KEYCHAIN_SERVICE,
                 account: str = KEYCHAIN_ACCOUNT, run=subprocess.run):
        self.service, self.account, self._run = service, account, run

    def load(self) -> dict | None:
        out = self._run(['security', 'find-generic-password', '-s',
                         self.service, '-a', self.account, '-w'],
                        capture_output=True, text=True, timeout=10)
        if out.returncode != 0 or not out.stdout.strip():
            return None
        try:
            return json.loads(_unhex(out.stdout.strip()))
        except ValueError:
            return None

    def save(self, blob: dict) -> None:
        # Hex-encode: `security -i` parses its command line shell-style, and
        # a token may contain quotes or spaces.
        secret = json.dumps(blob, separators=(',', ':')).encode().hex()
        cmd = (f'add-generic-password -U -s {self.service} '
               f'-a {self.account} -w {secret}\n')
        out = self._run(['security', '-i'], input=cmd, capture_output=True,
                        text=True, timeout=10)
        if out.returncode != 0:
            raise RuntimeError('could not write the login to the Keychain')

    def delete(self) -> None:
        self._run(['security', 'delete-generic-password', '-s', self.service,
                   '-a', self.account], capture_output=True, text=True,
                  timeout=10)


def _unhex(s: str) -> str:
    try:
        return bytes.fromhex(s).decode()
    except ValueError:
        return s


# ---------------------------------------------------------------------- http

def _http_json(url: str, *, form: dict | None = None,
               body: dict | None = None) -> dict:
    """GET, or POST a form / JSON body. Returns the parsed JSON response; an
    OAuth error response is returned (not raised) so callers can read
    `error`. Raises OSError on transport failure."""
    data, headers = None, {'Accept': 'application/json'}
    if form is not None:
        data = urllib.parse.urlencode(form).encode()
        headers['Content-Type'] = 'application/x-www-form-urlencoded'
    elif body is not None:
        data = json.dumps(body).encode()
        headers['Content-Type'] = 'application/json'
    req = urllib.request.Request(url, data=data, headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            return json.loads(resp.read().decode() or '{}')
    except urllib.error.HTTPError as e:
        try:
            payload = json.loads(e.read().decode() or '{}')
        except ValueError:
            payload = {}
        payload.setdefault('error', f'http_{e.code}')
        return payload


def discover(http=_http_json) -> dict:
    meta = http(METADATA_URL)
    for key in ('authorization_endpoint', 'token_endpoint'):
        if not str(meta.get(key, '')).startswith('https://'):
            raise RuntimeError(f'OAuth metadata has no https {key}')
    if 'refresh_token' not in meta.get('grant_types_supported', []):
        raise RuntimeError('server does not advertise refresh_token — a '
                           'self-renewing login is not possible')
    return meta


# -------------------------------------------------------------------- tokens

def _stamp(tok: dict, now: float) -> dict:
    """Keep only what is needed; convert expires_in to an absolute time."""
    if not tok.get('access_token'):
        raise RuntimeError(f"token endpoint refused: {tok.get('error', 'no access_token')}")
    return {'access_token': tok['access_token'],
            'refresh_token': tok.get('refresh_token'),
            'expires_at': now + float(tok.get('expires_in') or 0)}


def access_token(store: Keychain | None = None, http=_http_json,
                 now=time.time) -> str:
    """A currently valid bearer token, renewing it when close to expiry.
    Raises LoginRequired when there is nothing stored or renewal is refused;
    raises OSError when the network is down (the stored login is kept)."""
    store = store or Keychain()
    blob = store.load()
    if not blob or not blob.get('access_token'):
        raise LoginRequired(f'no executor login stored — {LOGIN_HINT}')
    if blob.get('expires_at', 0) - now() > REFRESH_MARGIN_S:
        return blob['access_token']
    if not blob.get('refresh_token') or not blob.get('client_id'):
        raise LoginRequired(f'executor login expired and cannot renew — '
                            f'{LOGIN_HINT}')
    tok = http(blob['token_endpoint'],
               form={'grant_type': 'refresh_token',
                     'refresh_token': blob['refresh_token'],
                     'client_id': blob['client_id']})
    if not tok.get('access_token'):
        raise LoginRequired(f"Robinhood refused to renew the executor login "
                            f"({tok.get('error', 'unknown')}) — {LOGIN_HINT}")
    fresh = _stamp(tok, now())
    # Servers may rotate the refresh token; keep the old one if none is sent.
    fresh['refresh_token'] = fresh['refresh_token'] or blob['refresh_token']
    # Persist BEFORE returning: if the old refresh token was just consumed,
    # losing the new one would strand the login.
    store.save({**blob, **fresh})
    return fresh['access_token']


# --------------------------------------------------------------------- login

def _pkce() -> tuple[str, str]:
    verifier = secrets.token_urlsafe(64)
    digest = hashlib.sha256(verifier.encode()).digest()
    return verifier, base64.urlsafe_b64encode(digest).rstrip(b'=').decode()


def _wait_for_callback(server, state: str) -> str:
    """Serve exactly the redirect on 127.0.0.1 and return the auth code."""
    from http.server import BaseHTTPRequestHandler
    got: dict = {}

    class Handler(BaseHTTPRequestHandler):
        def do_GET(self):               # noqa: N802 (stdlib name)
            q = urllib.parse.parse_qs(urllib.parse.urlparse(self.path).query)
            got.update({k: v[0] for k, v in q.items()})
            self.send_response(200)
            self.send_header('Content-Type', 'text/plain; charset=utf-8')
            self.end_headers()
            self.wfile.write(b'Login received. You can close this tab.')

        def log_message(self, *a):      # the query string carries the code
            pass

    server.RequestHandlerClass = Handler
    deadline = time.time() + CALLBACK_TIMEOUT_S
    # Ignore stray requests (favicon, preconnect) until the redirect lands.
    while 'state' not in got and 'error' not in got:
        left = deadline - time.time()
        if left <= 0:
            raise RuntimeError('timed out waiting for the browser approval')
        server.timeout = left
        server.handle_request()
    if got.get('state') != state:
        raise RuntimeError('login callback state mismatch — aborted')
    if 'code' not in got:
        raise RuntimeError(f"login was not approved ({got.get('error', 'no code')})")
    return got['code']


def login(store: Keychain | None = None, http=_http_json, opener=None,
          now=time.time) -> None:
    """Interactive, attended: register a public client, approve in the
    browser (PKCE), store the tokens. Run by Dom, never by a Claude session."""
    from http.server import HTTPServer
    import webbrowser
    store = store or Keychain()
    meta = discover(http)
    server = HTTPServer(('127.0.0.1', 0), None)
    try:
        redirect = f'http://127.0.0.1:{server.server_address[1]}/callback'
        reg = http(meta['registration_endpoint'], body={
            'client_name': 'ai-stocks executor (local, Dom)',
            'redirect_uris': [redirect],
            'grant_types': ['authorization_code', 'refresh_token'],
            'response_types': ['code'],
            'token_endpoint_auth_method': 'none'})
        client_id = reg.get('client_id')
        if not client_id:
            raise RuntimeError(f"client registration refused: "
                               f"{reg.get('error', 'no client_id')} "
                               f"{reg.get('error_description', '')}".strip())
        verifier, challenge = _pkce()
        state = secrets.token_urlsafe(24)
        params = {'response_type': 'code', 'client_id': client_id,
                  'redirect_uri': redirect, 'state': state,
                  'code_challenge': challenge, 'code_challenge_method': 'S256',
                  'resource': MCP_URL}
        scopes = meta.get('scopes_supported') or []
        if scopes:
            params['scope'] = ' '.join(scopes)
        url = meta['authorization_endpoint'] + '?' + urllib.parse.urlencode(params)
        print('Opening the Robinhood approval page in your browser…')
        (opener or webbrowser.open)(url)
        code = _wait_for_callback(server, state)
    finally:
        server.server_close()
    tok = http(meta['token_endpoint'],
               form={'grant_type': 'authorization_code', 'code': code,
                     'redirect_uri': redirect, 'client_id': client_id,
                     'code_verifier': verifier, 'resource': MCP_URL})
    blob = {**_stamp(tok, now()), 'client_id': client_id,
            'token_endpoint': meta['token_endpoint']}
    store.save(blob)
    print('Executor login stored in the Keychain. '
          + ('It will renew itself.' if blob['refresh_token'] else
             'WARNING: no refresh token was issued — it will NOT renew.'))


def status(store: Keychain | None = None, now=time.time) -> str:
    blob = (store or Keychain()).load()
    if not blob:
        return 'no executor login stored'
    left = blob.get('expires_at', 0) - now()
    return ('executor login stored; access token '
            + (f'valid for {int(left // 60)} more minutes'
               if left > 0 else 'expired')
            + ('; renewable' if blob.get('refresh_token') else
               '; NOT renewable'))


if __name__ == '__main__':
    cmd = sys.argv[1] if len(sys.argv) > 1 else ''
    if cmd == 'login':
        login()
    elif cmd == 'status':
        print(status())
    elif cmd == 'logout':
        Keychain().delete()
        print('executor login deleted')
    else:
        sys.exit(__doc__)
