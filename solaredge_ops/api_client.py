"""Thin wrapper around the SolarEdge Monitoring API (monitoringapi.solaredge.com).

Notes on the real API that shape this client:
  * Auth is a single `api_key` query parameter (account-level or site-level key).
  * Responses are JSON only.
  * Daily quota is ~300 requests per API key *and* per site id from the same source -
    `RateLimiter` below tracks calls so callers can budget a polling interval that
    won't blow through it across an entire fleet.
  * The official API has NO endpoint that returns alert/fault *events* - only a
    coarse `alertQuantity` counter on `/site/{id}/details`. Anything more granular
    (offline equipment, low production, etc.) has to be derived from raw
    power/energy/equipment data, which is exactly what the `rules` module does.
"""
from __future__ import annotations

import logging
import time
from collections import deque
from datetime import datetime
from typing import Any

import requests

logger = logging.getLogger(__name__)

BASE_URL = "https://monitoringapi.solaredge.com"
DATETIME_FMT = "%Y-%m-%d %H:%M:%S"
DATE_FMT = "%Y-%m-%d"


class SolarEdgeApiError(RuntimeError):
    """Raised when the SolarEdge API returns an error status."""


class RateLimiter:
    """Tracks recent calls and blocks once a rolling 24h budget is exhausted.

    SolarEdge enforces ~300 requests/day per api_key (and per site id). Rather than
    guess at reset times, we keep a rolling 24h window per bucket and refuse calls
    that would exceed the budget - callers should catch `RuntimeError` and skip
    that cycle rather than crash the whole poll loop.
    """

    WINDOW_SECONDS = 24 * 60 * 60

    def __init__(self, max_per_window: int):
        self.max_per_window = max_per_window
        self._calls: dict[str, deque[float]] = {}

    def _bucket(self, key: str) -> deque[float]:
        return self._calls.setdefault(key, deque())

    def remaining(self, key: str, now: float | None = None) -> int:
        now = now if now is not None else time.time()
        bucket = self._bucket(key)
        while bucket and now - bucket[0] > self.WINDOW_SECONDS:
            bucket.popleft()
        return max(0, self.max_per_window - len(bucket))

    def acquire(self, key: str) -> None:
        now = time.time()
        if self.remaining(key, now) <= 0:
            raise RuntimeError(
                f"SolarEdge API daily quota exhausted for '{key}' "
                f"({self.max_per_window} requests/24h) - skipping call"
            )
        self._bucket(key).append(now)


class SolarEdgeClient:
    """Calls the public SolarEdge Monitoring REST API with built-in rate limiting."""

    def __init__(
        self,
        api_key: str,
        max_requests_per_day: int = 300,
        session: requests.Session | None = None,
        base_url: str = BASE_URL,
        timeout: float = 30.0,
    ):
        self.api_key = api_key
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self.session = session or requests.Session()
        self.rate_limiter = RateLimiter(max_requests_per_day)

    # -- low level -------------------------------------------------------

    def _get(self, path: str, *, rate_limit_key: str, params: dict[str, Any] | None = None) -> dict:
        self.rate_limiter.acquire(rate_limit_key)
        query = dict(params or {})
        query["api_key"] = self.api_key
        url = f"{self.base_url}{path}"
        response = self.session.get(url, params=query, timeout=self.timeout)
        if response.status_code != 200:
            raise SolarEdgeApiError(
                f"SolarEdge API GET {path} failed: HTTP {response.status_code} - {response.text[:300]}"
            )
        try:
            return response.json()
        except ValueError as exc:
            raise SolarEdgeApiError(f"SolarEdge API GET {path} returned non-JSON body") from exc

    # -- account / fleet --------------------------------------------------

    def list_sites(self) -> list[dict]:
        data = self._get("/sites/list", rate_limit_key="account")
        return (data.get("sites") or {}).get("site", [])

    # -- per-site ----------------------------------------------------------

    def site_details(self, site_id: int) -> dict:
        data = self._get(f"/site/{site_id}/details", rate_limit_key=str(site_id))
        return data.get("details", {})

    def site_overview(self, site_id: int) -> dict:
        data = self._get(f"/site/{site_id}/overview", rate_limit_key=str(site_id))
        return data.get("overview", {})

    def site_power(self, site_id: int, start: datetime, end: datetime) -> list[dict]:
        """15-minute resolution power samples. SolarEdge limits this to <= 1 month per call."""
        data = self._get(
            f"/site/{site_id}/power",
            rate_limit_key=str(site_id),
            params={"startTime": start.strftime(DATETIME_FMT), "endTime": end.strftime(DATETIME_FMT)},
        )
        return ((data.get("power") or {}).get("values")) or []

    def site_energy(self, site_id: int, start_date: datetime, end_date: datetime, time_unit: str = "DAY") -> list[dict]:
        data = self._get(
            f"/site/{site_id}/energy",
            rate_limit_key=str(site_id),
            params={
                "startDate": start_date.strftime(DATE_FMT),
                "endDate": end_date.strftime(DATE_FMT),
                "timeUnit": time_unit,
            },
        )
        return ((data.get("energy") or {}).get("values")) or []

    def env_benefits(self, site_id: int) -> dict:
        data = self._get(f"/site/{site_id}/envBenefits", rate_limit_key=str(site_id))
        return data.get("envBenefits", {})

    # -- equipment ----------------------------------------------------------

    def equipment_list(self, site_id: int) -> list[dict]:
        data = self._get(f"/equipment/{site_id}/list", rate_limit_key=str(site_id))
        return (data.get("reporters") or {}).get("list", [])

    def equipment_data(self, site_id: int, serial_number: str, start: datetime, end: datetime) -> list[dict]:
        """Per-device telemetry. SolarEdge limits the range to <= 1 week per call."""
        data = self._get(
            f"/equipment/{site_id}/{serial_number}/data",
            rate_limit_key=str(site_id),
            params={"startTime": start.strftime(DATETIME_FMT), "endTime": end.strftime(DATETIME_FMT)},
        )
        return (data.get("data") or {}).get("telemetries", [])
