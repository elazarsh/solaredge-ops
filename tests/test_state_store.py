from datetime import datetime

from solaredge_ops.models import Alert, Severity
from solaredge_ops.state_store import StateStore


def make_alert(dedup_key="rule:1", site_id=1, rule="equipment_offline", title="t", message="m"):
    return Alert(
        rule=rule,
        severity=Severity.CRITICAL,
        site_id=site_id,
        site_name="Site A",
        title=title,
        message=message,
        dedup_key=dedup_key,
        detected_at=datetime(2026, 6, 8, 12, 0),
    )


def test_mark_open_returns_true_only_for_first_occurrence(tmp_path):
    store = StateStore(tmp_path / "state.db")
    alert = make_alert()

    assert store.mark_open(alert) is True   # first time -> new, should notify
    assert store.mark_open(alert) is False  # still open -> stay quiet
    assert store.mark_open(alert) is False
    assert store.is_open(alert.dedup_key) is True


def test_close_stale_removes_and_returns_resolved_alerts(tmp_path):
    store = StateStore(tmp_path / "state.db")
    a1 = make_alert(dedup_key="equipment_offline:1", site_id=1)
    a2 = make_alert(dedup_key="equipment_offline:1:device-x", site_id=1)
    store.mark_open(a1)
    store.mark_open(a2)

    # Only a1 reappears this cycle -> a2 should be reported as resolved and removed.
    closed = store.close_stale({a1.dedup_key}, rule="equipment_offline", site_id=1)

    assert [c["dedup_key"] for c in closed] == [a2.dedup_key]
    assert store.is_open(a1.dedup_key) is True
    assert store.is_open(a2.dedup_key) is False


def test_close_stale_only_touches_matching_rule_and_site(tmp_path):
    store = StateStore(tmp_path / "state.db")
    other_rule = make_alert(dedup_key="low_production:1:2026-06-08", site_id=1, rule="low_production")
    other_site = make_alert(dedup_key="equipment_offline:2", site_id=2, rule="equipment_offline")
    store.mark_open(other_rule)
    store.mark_open(other_site)

    closed = store.close_stale(set(), rule="equipment_offline", site_id=1)

    assert closed == []
    assert store.is_open(other_rule.dedup_key) is True
    assert store.is_open(other_site.dedup_key) is True


def test_kv_state_roundtrip(tmp_path):
    store = StateStore(tmp_path / "state.db")

    assert store.get_value("alert_quantity:1") is None

    store.set_value("alert_quantity:1", "3")
    assert store.get_value("alert_quantity:1") == "3"

    store.set_value("alert_quantity:1", "5")  # overwrite
    assert store.get_value("alert_quantity:1") == "5"
