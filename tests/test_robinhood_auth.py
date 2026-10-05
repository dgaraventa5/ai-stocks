"""The executor's own self-renewing Robinhood login (robinhood_auth.py).

Offline: a dict stands in for the Keychain and a function for the HTTP
layer. Tokens here are fictional strings.
"""
import pytest

import robinhood_auth as ra

TOKEN_URL = 'https://example.invalid/token'


class FakeStore:
    def __init__(self, blob=None):
        self.blob, self.saves = blob, 0

    def load(self):
        return self.blob

    def save(self, blob):
        self.blob, self.saves = blob, self.saves + 1


def blob(expires_at, refresh='refresh-1'):
    return {'access_token': 'access-1', 'refresh_token': refresh,
            'expires_at': expires_at, 'client_id': 'client-1',
            'token_endpoint': TOKEN_URL}


def no_http(*a, **k):
    raise AssertionError('network must not be touched')


def test_valid_token_is_returned_without_touching_the_network():
    store = FakeStore(blob(expires_at=10_000))
    assert ra.access_token(store, http=no_http, now=lambda: 1_000) == 'access-1'
    assert store.saves == 0


def test_near_expiry_token_is_renewed_and_saved():
    store = FakeStore(blob(expires_at=1_100))       # 100s left < margin
    calls = []

    def http(url, form=None, body=None):
        calls.append((url, form))
        return {'access_token': 'access-2', 'expires_in': 3600}

    assert ra.access_token(store, http=http, now=lambda: 1_000) == 'access-2'
    assert calls == [(TOKEN_URL, {'grant_type': 'refresh_token',
                                  'refresh_token': 'refresh-1',
                                  'client_id': 'client-1'})]
    assert store.blob['access_token'] == 'access-2'
    assert store.blob['expires_at'] == 4_600
    assert store.blob['refresh_token'] == 'refresh-1'   # kept: none re-issued
    assert store.blob['client_id'] == 'client-1'


def test_rotated_refresh_token_replaces_the_old_one():
    store = FakeStore(blob(expires_at=0))

    def http(url, form=None, body=None):
        return {'access_token': 'access-2', 'refresh_token': 'refresh-2',
                'expires_in': 60}

    ra.access_token(store, http=http, now=lambda: 1_000)
    assert store.blob['refresh_token'] == 'refresh-2'


def test_refused_renewal_asks_for_login_and_keeps_the_stored_blob():
    store = FakeStore(blob(expires_at=0))
    with pytest.raises(ra.LoginRequired) as e:
        ra.access_token(store, http=lambda *a, **k: {'error': 'invalid_grant'},
                        now=lambda: 1_000)
    assert 'robinhood_auth.py login' in str(e.value)
    assert store.saves == 0


def test_nothing_stored_asks_for_login():
    with pytest.raises(ra.LoginRequired):
        ra.access_token(FakeStore(None), http=no_http, now=lambda: 1_000)


def test_expired_without_refresh_token_asks_for_login():
    with pytest.raises(ra.LoginRequired):
        ra.access_token(FakeStore(blob(expires_at=0, refresh=None)),
                        http=no_http, now=lambda: 1_000)


def test_network_failure_during_renewal_propagates_and_keeps_login():
    store = FakeStore(blob(expires_at=0))

    def http(*a, **k):
        raise OSError('offline')

    with pytest.raises(OSError):
        ra.access_token(store, http=http, now=lambda: 1_000)
    assert store.blob['refresh_token'] == 'refresh-1' and store.saves == 0


def test_status_never_contains_a_token():
    out = ra.status(FakeStore(blob(expires_at=4_600)), now=lambda: 1_000)
    assert 'access-1' not in out and 'refresh-1' not in out
    assert '60 more minutes' in out and 'renewable' in out


def test_discover_requires_https_endpoints_and_refresh_support():
    good = {'authorization_endpoint': 'https://a.invalid/auth',
            'token_endpoint': 'https://a.invalid/token',
            'grant_types_supported': ['authorization_code', 'refresh_token']}
    assert ra.discover(lambda url: good) == good
    with pytest.raises(RuntimeError):
        ra.discover(lambda url: {**good, 'token_endpoint': 'http://a.invalid/t'})
    with pytest.raises(RuntimeError):
        ra.discover(lambda url: {**good,
                                 'grant_types_supported': ['authorization_code']})


def test_keychain_secret_goes_to_stdin_not_argv():
    seen = {}

    class Out:
        returncode, stdout = 0, ''

    def run(argv, **kw):
        seen['argv'], seen['input'] = argv, kw.get('input', '')
        return Out()

    ra.Keychain(run=run).save({'access_token': 'access-1'})
    assert seen['argv'] == ['security', '-i']
    assert 'access-1' not in seen['input']            # hex-encoded on the wire
    assert 'access-1'.encode().hex() in seen['input']


def test_pkce_challenge_is_s256_of_the_verifier():
    import base64, hashlib
    verifier, challenge = ra._pkce()
    want = base64.urlsafe_b64encode(
        hashlib.sha256(verifier.encode()).digest()).rstrip(b'=').decode()
    assert challenge == want and len(verifier) >= 43
