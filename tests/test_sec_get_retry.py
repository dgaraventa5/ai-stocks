"""tests/test_sec_get_retry.py — sec_get retries, no network, stubbed requests.

requests is faked through sys.modules because the deploy CI runs without it.
"""
import sys
import types

import pytest

import common


class _ConnectionError(Exception):
    pass


class _Timeout(Exception):
    pass


class _ChunkedEncodingError(Exception):
    pass


class _HTTPError(Exception):
    pass


class _Response:
    def __init__(self, status):
        self.status_code = status

    def raise_for_status(self):
        if self.status_code >= 400:
            raise _HTTPError(str(self.status_code))


@pytest.fixture
def stub(monkeypatch):
    """Script the outcomes of requests.get; returns the shared call record."""
    record = types.SimpleNamespace(calls=0, waits=0, sleeps=[], outcomes=[])

    def fake_get(url, headers, timeout, **kwargs):
        record.calls += 1
        outcome = record.outcomes.pop(0)
        if isinstance(outcome, Exception):
            raise outcome
        return _Response(outcome)

    fake = types.ModuleType("requests")
    fake.get = fake_get
    fake.ConnectionError = _ConnectionError
    fake.Timeout = _Timeout
    fake.exceptions = types.SimpleNamespace(
        ChunkedEncodingError=_ChunkedEncodingError)
    monkeypatch.setitem(sys.modules, "requests", fake)
    monkeypatch.setattr(common.sec_limiter, "wait",
                        lambda: setattr(record, "waits", record.waits + 1))
    monkeypatch.setattr(common.time, "sleep", record.sleeps.append)
    return record


def test_two_failures_then_success_returns_the_response(stub):
    stub.outcomes = [_ConnectionError("dns"), _Timeout("slow"), 200]
    assert common.sec_get("https://www.sec.gov/x").status_code == 200
    assert stub.calls == 3


def test_body_cut_off_partway_is_retried(stub):
    stub.outcomes = [_ChunkedEncodingError("dropped mid-body"), 200]
    assert common.sec_get("https://www.sec.gov/x").status_code == 200
    assert stub.calls == 2


def test_404_makes_exactly_one_call(stub):
    stub.outcomes = [404]
    with pytest.raises(_HTTPError):
        common.sec_get("https://www.sec.gov/x")
    assert stub.calls == 1


def test_three_network_failures_raise(stub):
    stub.outcomes = [_ConnectionError("a"), _ConnectionError("b"), _ConnectionError("c")]
    with pytest.raises(_ConnectionError):
        common.sec_get("https://www.sec.gov/x")
    assert stub.calls == 3


def test_throttle_and_server_errors_retry_then_raise(stub):
    stub.outcomes = [429, 503, 500]
    with pytest.raises(_HTTPError):
        common.sec_get("https://www.sec.gov/x")
    assert stub.calls == 3


@pytest.mark.parametrize("status", [429, 500, 502, 503, 504])
def test_transient_status_then_success(stub, status):
    stub.outcomes = [status, 200]
    assert common.sec_get("https://www.sec.gov/x").status_code == 200
    assert stub.calls == 2


def test_backoff_doubles_between_attempts(stub):
    stub.outcomes = [503, 503, 200]
    common.sec_get("https://www.sec.gov/x")
    assert stub.sleeps == [common.SEC_RETRY_DELAY, common.SEC_RETRY_DELAY * 2]


def test_every_attempt_goes_through_the_rate_limiter(stub):
    stub.outcomes = [_Timeout("slow"), 503, 200]
    common.sec_get("https://www.sec.gov/x")
    assert stub.waits == stub.calls == 3


def test_success_first_try_does_not_wait_or_retry(stub):
    stub.outcomes = [200]
    common.sec_get("https://www.sec.gov/x")
    assert stub.calls == 1 and stub.sleeps == []
