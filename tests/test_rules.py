from datetime import datetime

from solaredge_ops.config import ActiveHours, RuleConfig, SiteConfig
from solaredge_ops.models import Severity
from solaredge_ops.rules import (
    SiteSnapshot,
    rule_alert_count_jump,
    rule_equipment_offline,
    rule_low_production,
    rule_performance_drop,
    rule_zero_production_daylight,
)

def _t(value):
    h, m = (int(p) for p in value.split(":"))
    from datetime import time
    return time(hour=h, minute=m)


def active_hours(start="06:00", end="18:00"):
    return ActiveHours(start=_t(start), end=_t(end))


def make_snapshot(site_id=1, name="Site A", now=None, last_update=None, power=3000.0, today_wh=10_000.0, peak_kw=10.0, alert_quantity=0):
    now = now or datetime(2026, 6, 8, 12, 0)
    last_update = last_update if last_update is not None else now
    return SiteSnapshot(
        site_id=site_id,
        site_name=name,
        fetched_at=now,
        overview={
            "lastUpdateTime": last_update.strftime("%Y-%m-%d %H:%M:%S"),
            "currentPower": {"power": power},
            "lastDayData": {"energy": today_wh},
        },
        details={"peakPower": peak_kw, "alertQuantity": alert_quantity},
    )


def site_cfg(site_id=1, name="Site A", expected_daily_kwh=None):
    return SiteConfig(id=site_id, name=name, expected_daily_kwh=expected_daily_kwh)


def enabled_rule(**options):
    return RuleConfig(enabled=True, options=options)


def disabled_rule():
    return RuleConfig(enabled=False)


# ---------------------------------------------------------------------------
# equipment_offline
# ---------------------------------------------------------------------------

def test_equipment_offline_fires_after_grace_period():
    now = datetime(2026, 6, 8, 12, 0)
    last_update = datetime(2026, 6, 8, 10, 30)  # 90 minutes of silence
    snap = make_snapshot(now=now, last_update=last_update)

    alerts = rule_equipment_offline(snap, site_cfg(), enabled_rule(grace_minutes=60), now)

    assert len(alerts) == 1
    assert alerts[0].rule == "equipment_offline"
    assert alerts[0].severity == Severity.CRITICAL
    assert alerts[0].dedup_key == "equipment_offline:1"


def test_equipment_offline_does_not_fire_within_grace_period():
    now = datetime(2026, 6, 8, 12, 0)
    last_update = datetime(2026, 6, 8, 11, 45)  # 15 minutes of silence
    snap = make_snapshot(now=now, last_update=last_update)

    alerts = rule_equipment_offline(snap, site_cfg(), enabled_rule(grace_minutes=60), now)

    assert alerts == []


def test_equipment_offline_respects_disabled_flag():
    now = datetime(2026, 6, 8, 12, 0)
    last_update = datetime(2026, 6, 8, 9, 0)
    snap = make_snapshot(now=now, last_update=last_update)

    assert rule_equipment_offline(snap, site_cfg(), disabled_rule(), now) == []


# ---------------------------------------------------------------------------
# zero_production_daylight
# ---------------------------------------------------------------------------

def test_zero_production_fires_during_core_daylight():
    now = datetime(2026, 6, 8, 12, 0)
    snap = make_snapshot(now=now, last_update=now, power=0.0)

    alerts = rule_zero_production_daylight(snap, site_cfg(), enabled_rule(grace_minutes=45), active_hours(), now)

    assert len(alerts) == 1
    assert alerts[0].rule == "zero_production_daylight"
    assert alerts[0].severity == Severity.CRITICAL


def test_zero_production_does_not_fire_with_normal_output():
    now = datetime(2026, 6, 8, 12, 0)
    snap = make_snapshot(now=now, last_update=now, power=4000.0)

    alerts = rule_zero_production_daylight(snap, site_cfg(), enabled_rule(grace_minutes=45), active_hours(), now)

    assert alerts == []


def test_zero_production_does_not_fire_near_edges_of_daylight_window():
    now = datetime(2026, 6, 8, 6, 5)  # 5 minutes after sunrise window opens
    snap = make_snapshot(now=now, last_update=now, power=0.0)

    alerts = rule_zero_production_daylight(snap, site_cfg(), enabled_rule(grace_minutes=45), active_hours("06:00", "18:00"), now)

    assert alerts == []  # too close to sunrise to judge "should be producing"


def test_zero_production_does_not_fire_when_site_is_offline():
    """Offline sites are handled by `equipment_offline` - avoid double alerting."""
    now = datetime(2026, 6, 8, 12, 0)
    stale_update = datetime(2026, 6, 8, 9, 0)
    snap = make_snapshot(now=now, last_update=stale_update, power=0.0)

    alerts = rule_zero_production_daylight(snap, site_cfg(), enabled_rule(grace_minutes=45), active_hours(), now)

    assert alerts == []


# ---------------------------------------------------------------------------
# low_production
# ---------------------------------------------------------------------------

def test_low_production_fires_when_below_threshold():
    now = datetime(2026, 6, 8, 14, 0)  # daylight window 06:00-18:00 -> ~67% elapsed
    # Expected so far ~ 400 kWh * 0.667 = ~266.7 kWh = 266_700 Wh; 70% threshold -> ~186_690 Wh
    snap = make_snapshot(now=now, last_update=now, today_wh=100_000.0)

    alerts = rule_low_production(
        snap, site_cfg(expected_daily_kwh=400), enabled_rule(threshold_pct=70, min_hour_of_day=12), active_hours(), now
    )

    assert len(alerts) == 1
    assert alerts[0].rule == "low_production"
    assert alerts[0].severity == Severity.WARNING


def test_low_production_does_not_fire_when_on_track():
    now = datetime(2026, 6, 8, 14, 0)
    snap = make_snapshot(now=now, last_update=now, today_wh=300_000.0)  # well above 70% of ~266.7 kWh

    alerts = rule_low_production(
        snap, site_cfg(expected_daily_kwh=400), enabled_rule(threshold_pct=70, min_hour_of_day=12), active_hours(), now
    )

    assert alerts == []


def test_low_production_skipped_before_min_hour():
    now = datetime(2026, 6, 8, 9, 0)
    snap = make_snapshot(now=now, last_update=now, today_wh=1.0)

    alerts = rule_low_production(
        snap, site_cfg(expected_daily_kwh=400), enabled_rule(threshold_pct=70, min_hour_of_day=12), active_hours(), now
    )

    assert alerts == []


def test_low_production_skipped_without_baseline():
    now = datetime(2026, 6, 8, 14, 0)
    snap = make_snapshot(now=now, last_update=now, today_wh=1.0)

    alerts = rule_low_production(
        snap, site_cfg(expected_daily_kwh=None), enabled_rule(threshold_pct=70, min_hour_of_day=12), active_hours(), now
    )

    assert alerts == []


# ---------------------------------------------------------------------------
# performance_drop (cross-site)
# ---------------------------------------------------------------------------

def test_performance_drop_flags_underperforming_site_relative_to_fleet():
    now = datetime(2026, 6, 8, 12, 0)
    snapshots = [
        make_snapshot(site_id=1, name="Strong A", now=now, power=9000.0, peak_kw=10.0),
        make_snapshot(site_id=2, name="Strong B", now=now, power=8800.0, peak_kw=10.0),
        make_snapshot(site_id=3, name="Weak C", now=now, power=5000.0, peak_kw=10.0),
    ]
    site_cfgs = {1: site_cfg(1, "Strong A"), 2: site_cfg(2, "Strong B"), 3: site_cfg(3, "Weak C")}

    alerts = rule_performance_drop(snapshots, site_cfgs, enabled_rule(threshold_pct=20), active_hours(), now)

    assert len(alerts) == 1
    assert alerts[0].site_id == 3
    assert alerts[0].rule == "performance_drop"


def test_performance_drop_requires_at_least_three_sites():
    now = datetime(2026, 6, 8, 12, 0)
    snapshots = [
        make_snapshot(site_id=1, name="A", now=now, power=9000.0, peak_kw=10.0),
        make_snapshot(site_id=2, name="B", now=now, power=2000.0, peak_kw=10.0),
    ]
    site_cfgs = {1: site_cfg(1, "A"), 2: site_cfg(2, "B")}

    alerts = rule_performance_drop(snapshots, site_cfgs, enabled_rule(threshold_pct=20), active_hours(), now)

    assert alerts == []


def test_performance_drop_does_not_flag_uniform_fleet():
    now = datetime(2026, 6, 8, 12, 0)
    snapshots = [make_snapshot(site_id=i, name=f"S{i}", now=now, power=9000.0, peak_kw=10.0) for i in range(1, 5)]
    site_cfgs = {s.site_id: site_cfg(s.site_id, s.site_name) for s in snapshots}

    alerts = rule_performance_drop(snapshots, site_cfgs, enabled_rule(threshold_pct=20), active_hours(), now)

    assert alerts == []


# ---------------------------------------------------------------------------
# alert_count_jump
# ---------------------------------------------------------------------------

def test_alert_count_jump_fires_on_increase():
    now = datetime(2026, 6, 8, 12, 0)
    snap = make_snapshot(now=now, alert_quantity=3)

    alerts = rule_alert_count_jump(snap, site_cfg(), enabled_rule(), previous_count=1, now=now)

    assert len(alerts) == 1
    assert "1" in alerts[0].message and "3" in alerts[0].message


def test_alert_count_jump_silent_when_unchanged_or_lower():
    now = datetime(2026, 6, 8, 12, 0)
    snap = make_snapshot(now=now, alert_quantity=2)

    assert rule_alert_count_jump(snap, site_cfg(), enabled_rule(), previous_count=2, now=now) == []
    assert rule_alert_count_jump(snap, site_cfg(), enabled_rule(), previous_count=5, now=now) == []


def test_alert_count_jump_silent_without_baseline():
    now = datetime(2026, 6, 8, 12, 0)
    snap = make_snapshot(now=now, alert_quantity=2)

    assert rule_alert_count_jump(snap, site_cfg(), enabled_rule(), previous_count=None, now=now) == []
