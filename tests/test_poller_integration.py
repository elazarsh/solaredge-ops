"""End-to-end smoke test: fake API responses -> rule evaluation -> dedup -> notification.

Exercises the full `run_once` pipeline the way `solaredge-ops check` would, without
hitting the real SolarEdge API or a real Telegram/email endpoint.
"""
from datetime import datetime

from solaredge_ops.api_client import SolarEdgeClient
from solaredge_ops.config import ActiveHours, Config, MonthlyReportConfig, PollingConfig, RuleConfig, SiteConfig, TelegramConfig, EmailConfig
from solaredge_ops.models import Alert
from solaredge_ops.notifiers.base import Notifier
from solaredge_ops.poller import run_once
from solaredge_ops.state_store import StateStore


class RecordingNotifier(Notifier):
    name = "recording"

    def __init__(self):
        self.sent: list[Alert] = []
        self.resolved: list[tuple[str, str]] = []

    def send_alert(self, alert):
        self.sent.append(alert)

    def send_resolved(self, site_name, title, severity, rule):
        self.resolved.append((site_name, title))


class ScriptedSession:
    """Replays a fixed sequence of (overview, details) pairs per `.get` call, by URL suffix."""

    def __init__(self, site_payloads: dict[int, list[tuple[dict, dict]]]):
        # site_payloads[site_id] is a list consumed one pair per `run_once` call
        self._payloads = site_payloads
        self._cursor = {site_id: 0 for site_id in site_payloads}

    def get(self, url, params=None, timeout=None):
        site_id = int(url.split("/site/")[1].split("/")[0])
        idx = self._cursor[site_id]
        overview, details = self._payloads[site_id][min(idx, len(self._payloads[site_id]) - 1)]
        if "/overview" in url:
            body = {"overview": overview}
        elif "/details" in url:
            body = {"details": details}
            self._cursor[site_id] = idx + 1  # advance once per (overview, details) pair, on the 2nd call
        else:
            body = {}
        return _FakeResponse(body)


class _FakeResponse:
    def __init__(self, body):
        self.status_code = 200
        self._body = body
        self.text = str(body)

    def json(self):
        return self._body


def _config(tmp_path, sites, rules):
    return Config(
        api_key="test-key",
        max_requests_per_day=300,
        sites=sites,
        polling=PollingConfig(interval_minutes=30, active_hours=ActiveHours(start=_time("06:00"), end=_time("18:00"))),
        alert_rules=rules,
        telegram=TelegramConfig(enabled=False),
        email=EmailConfig(enabled=False),
        monthly_report=MonthlyReportConfig(enabled=False),
        recipients=[],
        state_db_path=str(tmp_path / "state.db"),
    )


def _time(value):
    from datetime import time
    h, m = (int(p) for p in value.split(":"))
    return time(hour=h, minute=m)


def _overview(power, energy_wh, last_update):
    return {
        "currentPower": {"power": power},
        "lastDayData": {"energy": energy_wh},
        "lastUpdateTime": last_update,
    }


def test_run_once_detects_new_problem_then_stays_quiet_then_resolves(tmp_path):
    site = SiteConfig(id=1, name="Site A", expected_daily_kwh=None)
    rules = {"zero_production_daylight": RuleConfig(enabled=True, options={"grace_minutes": 0})}

    now = datetime(2026, 6, 8, 12, 0)
    broken = (_overview(power=0.0, energy_wh=1000.0, last_update="2026-06-08 12:00:00"), {"alertQuantity": 0})
    fixed = (_overview(power=4000.0, energy_wh=5000.0, last_update="2026-06-08 12:30:00"), {"alertQuantity": 0})

    session = ScriptedSession({1: [broken, broken, fixed]})
    client = SolarEdgeClient("test-key", session=session)
    store = StateStore(tmp_path / "state.db")
    notifier = RecordingNotifier()
    config = _config(tmp_path, [site], rules)

    # Cycle 1: problem appears -> one new alert dispatched
    dispatched_1 = run_once(config, client, store, [notifier], now=now)
    assert dispatched_1 == 1
    assert len(notifier.sent) == 1
    assert notifier.sent[0].rule == "zero_production_daylight"

    # Cycle 2: problem persists -> no duplicate notification
    dispatched_2 = run_once(config, client, store, [notifier], now=now)
    assert dispatched_2 == 0
    assert len(notifier.sent) == 1

    # Cycle 3: production resumes -> alert closes and a "resolved" message goes out
    dispatched_3 = run_once(config, client, store, [notifier], now=now)
    assert dispatched_3 == 0
    assert len(notifier.resolved) == 1
    assert notifier.resolved[0][0] == "Site A"


def test_run_once_skips_outside_active_hours(tmp_path):
    site = SiteConfig(id=1, name="Site A", expected_daily_kwh=None)
    rules = {"zero_production_daylight": RuleConfig(enabled=True, options={"grace_minutes": 0})}
    night = datetime(2026, 6, 8, 23, 0)

    broken = (_overview(power=0.0, energy_wh=0.0, last_update="2026-06-08 23:00:00"), {"alertQuantity": 0})
    session = ScriptedSession({1: [broken]})
    client = SolarEdgeClient("test-key", session=session)
    store = StateStore(tmp_path / "state.db")
    notifier = RecordingNotifier()
    config = _config(tmp_path, [site], rules)

    dispatched = run_once(config, client, store, [notifier], now=night)

    assert dispatched == 0
    assert notifier.sent == []
