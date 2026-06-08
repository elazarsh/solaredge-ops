from datetime import datetime

import pytest
import requests

from solaredge_ops.api_client import RateLimiter, SolarEdgeApiError, SolarEdgeClient


class FakeResponse:
    def __init__(self, status_code=200, json_body=None, text=""):
        self.status_code = status_code
        self._json_body = json_body if json_body is not None else {}
        self.text = text or str(json_body)

    def json(self):
        return self._json_body


class FakeSession:
    def __init__(self, responses):
        self._responses = list(responses)
        self.requests = []

    def get(self, url, params=None, timeout=None):
        self.requests.append((url, params))
        return self._responses.pop(0)


# ---------------------------------------------------------------------------
# RateLimiter
# ---------------------------------------------------------------------------

def test_rate_limiter_allows_up_to_max_then_blocks():
    limiter = RateLimiter(max_per_window=3)
    now = 1_000_000.0

    assert limiter.remaining("site-1", now) == 3
    limiter.acquire("site-1")
    limiter.acquire("site-1")
    limiter.acquire("site-1")
    assert limiter.remaining("site-1", now) == 0

    with pytest.raises(RuntimeError, match="quota exhausted"):
        limiter.acquire("site-1")


def test_rate_limiter_buckets_are_independent():
    limiter = RateLimiter(max_per_window=1)
    limiter.acquire("site-1")

    # site-2's bucket is untouched
    limiter.acquire("site-2")
    assert limiter.remaining("site-2") == 0
    assert limiter.remaining("site-1") == 0


def test_rate_limiter_window_expires_old_calls():
    from collections import deque

    limiter = RateLimiter(max_per_window=1)
    base = 1_000_000.0
    limiter._calls["site-1"] = deque([base])

    # Just inside the 24h window -> still counted
    assert limiter.remaining("site-1", base + RateLimiter.WINDOW_SECONDS - 1) == 0
    # Just outside the window -> expired, budget refreshed
    assert limiter.remaining("site-1", base + RateLimiter.WINDOW_SECONDS + 1) == 1


# ---------------------------------------------------------------------------
# SolarEdgeClient
# ---------------------------------------------------------------------------

def test_site_overview_parses_payload_and_includes_api_key():
    payload = {"overview": {"currentPower": {"power": 1234.5}, "lastUpdateTime": "2026-06-08 12:00:00"}}
    session = FakeSession([FakeResponse(200, payload)])
    client = SolarEdgeClient("the-key", session=session)

    overview = client.site_overview(42)

    assert overview["currentPower"]["power"] == 1234.5
    url, params = session.requests[0]
    assert url == "https://monitoringapi.solaredge.com/site/42/overview"
    assert params["api_key"] == "the-key"


def test_non_200_response_raises_api_error():
    session = FakeSession([FakeResponse(403, text="Forbidden")])
    client = SolarEdgeClient("the-key", session=session)

    with pytest.raises(SolarEdgeApiError, match="HTTP 403"):
        client.site_overview(42)


def test_list_sites_unwraps_nested_payload():
    payload = {"sites": {"count": 2, "site": [{"id": 1}, {"id": 2}]}}
    session = FakeSession([FakeResponse(200, payload)])
    client = SolarEdgeClient("the-key", session=session)

    sites = client.list_sites()

    assert [s["id"] for s in sites] == [1, 2]


def test_site_power_passes_formatted_time_range():
    session = FakeSession([FakeResponse(200, {"power": {"values": [{"date": "x", "value": 1}]}})])
    client = SolarEdgeClient("the-key", session=session)

    values = client.site_power(7, datetime(2026, 6, 1, 0, 0), datetime(2026, 6, 2, 0, 0))

    assert values == [{"date": "x", "value": 1}]
    _, params = session.requests[0]
    assert params["startTime"] == "2026-06-01 00:00:00"
    assert params["endTime"] == "2026-06-02 00:00:00"


def test_rate_limit_exhaustion_prevents_http_call():
    session = FakeSession([FakeResponse(200, {"overview": {}})])
    client = SolarEdgeClient("the-key", session=session, max_requests_per_day=1)

    client.site_overview(99)
    with pytest.raises(RuntimeError, match="quota exhausted"):
        client.site_overview(99)

    assert len(session.requests) == 1  # second call never reached the network
