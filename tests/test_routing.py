"""Tests for the recipient directory (`Recipient`) and alert fan-out (`AlertRouter`).

This is the layer that turns "an alert happened" into "the right people heard
about it on the right channel" - e.g. the maintenance crew gets real-time
Telegram pushes for field issues, while finance only gets the monthly report.
"""
from datetime import datetime

from solaredge_ops.config import Recipient
from solaredge_ops.models import Alert, Severity
from solaredge_ops.notifiers.router import AlertRouter


def make_alert(rule="equipment_offline", severity=Severity.WARNING, site_name="Site A"):
    return Alert(
        rule=rule,
        severity=severity,
        site_id=1,
        site_name=site_name,
        title="t",
        message="m",
        dedup_key=f"{rule}:1",
        detected_at=datetime(2026, 6, 8, 12, 0),
    )


# ---------------------------------------------------------------------------
# Recipient.wants_alert / wants_report
# ---------------------------------------------------------------------------

def test_wants_alert_matches_category_and_severity_floor():
    r = Recipient(name="Danny", telegram_chat_id="1", categories=["equipment_offline"], min_severity=Severity.WARNING)

    assert r.wants_alert("equipment_offline", Severity.WARNING) is True
    assert r.wants_alert("equipment_offline", Severity.CRITICAL) is True
    assert r.wants_alert("equipment_offline", Severity.INFO) is False   # below the severity floor
    assert r.wants_alert("low_production", Severity.CRITICAL) is False  # not subscribed to this category


def test_wants_alert_all_category_matches_any_rule():
    r = Recipient(name="Yossi", telegram_chat_id="1", categories=["all"], min_severity=Severity.CRITICAL)

    assert r.wants_alert("equipment_offline", Severity.CRITICAL) is True
    assert r.wants_alert("performance_drop", Severity.CRITICAL) is True
    assert r.wants_alert("performance_drop", Severity.WARNING) is False  # still filtered by severity


def test_wants_report_requires_explicit_opt_in():
    everything = Recipient(name="Yossi", telegram_chat_id="1", categories=["all"])
    subscribed = Recipient(name="Ronit", email="r@example.com", categories=["monthly_report"])

    assert everything.wants_report() is False   # "all" does not imply the report - opt-in only
    assert subscribed.wants_report() is True


# ---------------------------------------------------------------------------
# AlertRouter fan-out
# ---------------------------------------------------------------------------

class FakeTelegram:
    def __init__(self):
        self.sent = []  # [(chat_id, text), ...]

    def send(self, chat_id, text):
        self.sent.append((chat_id, text))


class FakeEmail:
    def __init__(self):
        self.sent = []  # [(to_addrs, subject, html, text), ...]

    def send(self, to_addrs, subject, html_body, text_body):
        self.sent.append((to_addrs, subject, html_body, text_body))


class PartiallyFailingTelegram:
    """Raises for one specific chat_id, to test that the router isolates failures."""

    def __init__(self, failing_chat_id):
        self.failing_chat_id = failing_chat_id
        self.sent = []

    def send(self, chat_id, text):
        if chat_id == self.failing_chat_id:
            raise RuntimeError("network is down")
        self.sent.append((chat_id, text))


def test_send_alert_only_reaches_subscribed_recipients_on_their_channels():
    maintenance = Recipient(name="Danny", telegram_chat_id="111", categories=["equipment_offline"], min_severity=Severity.WARNING)
    finance = Recipient(name="Ronit", email="ronit@example.com", categories=["monthly_report"])
    ceo = Recipient(name="Yossi", telegram_chat_id="222", email="yossi@example.com", categories=["all"], min_severity=Severity.CRITICAL)

    telegram, email = FakeTelegram(), FakeEmail()
    router = AlertRouter([maintenance, finance, ceo], telegram=telegram, email=email)

    router.send_alert(make_alert(rule="equipment_offline", severity=Severity.CRITICAL))

    # Danny: subscribed to equipment_offline at >= warning -> Telegram only
    # Ronit: only subscribed to the monthly report -> nothing
    # Yossi: subscribed to "all" at >= critical -> both Telegram and email
    assert [chat_id for chat_id, _ in telegram.sent] == ["111", "222"]
    assert [addrs for addrs, *_ in email.sent] == [["yossi@example.com"]]


def test_send_alert_respects_severity_floor():
    danny = Recipient(name="Danny", telegram_chat_id="111", categories=["equipment_offline"], min_severity=Severity.CRITICAL)
    telegram = FakeTelegram()
    router = AlertRouter([danny], telegram=telegram)

    router.send_alert(make_alert(rule="equipment_offline", severity=Severity.WARNING))
    assert telegram.sent == []

    router.send_alert(make_alert(rule="equipment_offline", severity=Severity.CRITICAL))
    assert len(telegram.sent) == 1


def test_send_resolved_routes_by_rule_and_severity():
    danny = Recipient(name="Danny", telegram_chat_id="111", categories=["equipment_offline"], min_severity=Severity.WARNING)
    telegram = FakeTelegram()
    router = AlertRouter([danny], telegram=telegram)

    router.send_resolved("Site A", "Inverter back online", "warning", "equipment_offline")
    assert len(telegram.sent) == 1
    assert "הבעיה חלפה" in telegram.sent[0][1]

    telegram.sent.clear()
    router.send_resolved("Site A", "Low production cleared", "warning", "low_production")
    assert telegram.sent == []  # Danny isn't subscribed to this category


def test_router_isolates_delivery_failures_between_recipients():
    broken = Recipient(name="Broken", telegram_chat_id="111", categories=["all"])
    healthy = Recipient(name="Healthy", telegram_chat_id="222", categories=["all"])

    telegram = PartiallyFailingTelegram(failing_chat_id="111")
    router = AlertRouter([broken, healthy], telegram=telegram)

    router.send_alert(make_alert())  # must not raise despite Broken's failure

    assert [chat_id for chat_id, _ in telegram.sent] == ["222"]


def test_router_tries_every_channel_even_if_another_one_fails():
    both = Recipient(name="Yossi", telegram_chat_id="111", email="yossi@example.com", categories=["all"])

    email = FakeEmail()
    router = AlertRouter([both], telegram=PartiallyFailingTelegram(failing_chat_id="111"), email=email)

    router.send_alert(make_alert())  # Telegram fails, email must still be attempted

    assert len(email.sent) == 1
