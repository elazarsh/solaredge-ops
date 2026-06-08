"""Custom anomaly-detection rules evaluated on top of raw SolarEdge API data.

Why these rules exist instead of relying on SolarEdge's built-in alerts: the public
Monitoring API does not expose alert *content* (see api_client module docstring) -
only a coarse counter. These rules reconstruct the signal that matters for fast,
team-routable dispatch directly from production/status data, with thresholds the
fleet owner controls (unlike SolarEdge's fixed alert-profile rules).

Each rule is a small, pure function: given the current data it returns the set of
problems that look "currently active". Persistence/deduplication (so a problem that
is still ongoing doesn't re-notify every cycle, and a `grace_minutes` window doesn't
fire on a single noisy sample) is handled by `StateStore` in the poller - rules
themselves stay simple and easy to unit test.
"""
from __future__ import annotations

import statistics
from dataclasses import dataclass
from datetime import datetime, time, timedelta

from .config import ActiveHours, RuleConfig, SiteConfig
from .models import Alert, Severity

DATETIME_FMT = "%Y-%m-%d %H:%M:%S"

# Below this we treat reported power as "effectively zero" (filters sensor noise).
ZERO_POWER_THRESHOLD_W = 50.0
# Don't try to judge "is it producing enough" right after sunrise / before sunset.
EDGE_OF_DAY_MARGIN_MINUTES = 30


@dataclass
class SiteSnapshot:
    """Everything fetched for one site in a single poll cycle."""

    site_id: int
    site_name: str
    fetched_at: datetime
    overview: dict
    details: dict

    # -- convenience accessors over the raw API payloads ---------------------

    @property
    def last_update_time(self) -> datetime | None:
        return _parse_dt(self.overview.get("lastUpdateTime"))

    @property
    def current_power_w(self) -> float:
        return float(((self.overview.get("currentPower") or {}).get("power")) or 0.0)

    @property
    def today_energy_wh(self) -> float:
        return float(((self.overview.get("lastDayData") or {}).get("energy")) or 0.0)

    @property
    def peak_power_w(self) -> float:
        # `details.peakPower` is published in kW.
        peak_kw = self.details.get("peakPower")
        return float(peak_kw) * 1000.0 if peak_kw else 0.0

    @property
    def alert_quantity(self) -> int:
        return int(self.details.get("alertQuantity") or 0)

    @property
    def normalized_output(self) -> float | None:
        """Current power as a fraction of the site's nameplate peak power, or None if unknown."""
        if self.peak_power_w <= 0:
            return None
        return self.current_power_w / self.peak_power_w

    @property
    def is_reporting_fresh(self) -> bool:
        """True if SolarEdge received data from this site recently (last 30 min)."""
        return self.last_update_time is not None and (
            self.fetched_at - self.last_update_time
        ) < timedelta(minutes=30)


def _parse_dt(raw: str | None) -> datetime | None:
    if not raw:
        return None
    try:
        return datetime.strptime(raw, DATETIME_FMT)
    except ValueError:
        return None


def _shift(t: time, minutes: int) -> time:
    return (datetime(2000, 1, 1, t.hour, t.minute) + timedelta(minutes=minutes)).time()


def _is_core_daylight(now: time, active_hours: ActiveHours | None) -> bool:
    """True when `now` is solidly inside the configured daylight window (with edge margin)."""
    if active_hours is None:
        return True
    core_start = _shift(active_hours.start, EDGE_OF_DAY_MARGIN_MINUTES)
    core_end = _shift(active_hours.end, -EDGE_OF_DAY_MARGIN_MINUTES)
    return core_start <= now <= core_end


def _daylight_progress(now: time, active_hours: ActiveHours | None) -> float:
    """Fraction (0..1) of the configured daylight window elapsed at `now`. 1.0 if unconfigured/past end."""
    if active_hours is None:
        return 1.0
    start_min = active_hours.start.hour * 60 + active_hours.start.minute
    end_min = active_hours.end.hour * 60 + active_hours.end.minute
    now_min = now.hour * 60 + now.minute
    span = max(1, end_min - start_min)
    return max(0.0, min(1.0, (now_min - start_min) / span))


# ---------------------------------------------------------------------------
# Rules
# ---------------------------------------------------------------------------

def rule_equipment_offline(
    snapshot: SiteSnapshot, site_cfg: SiteConfig, rule_cfg: RuleConfig, now: datetime
) -> list[Alert]:
    """Site has stopped reporting data to SolarEdge for longer than the grace period.

    This is the cloud-side proxy for "communication loss": cheap to evaluate (one
    field already present in `overview`) and a strong, fast-dispatch-worthy signal -
    a site that vanishes from the monitoring feed almost always means a
    gateway/network problem that needs a truck roll, independent of sunlight.
    """
    if not rule_cfg.enabled or snapshot.last_update_time is None:
        return []

    grace = timedelta(minutes=rule_cfg.get("grace_minutes", 60))
    silence = now - snapshot.last_update_time
    if silence < grace:
        return []

    return [
        Alert(
            rule="equipment_offline",
            severity=Severity.CRITICAL,
            site_id=snapshot.site_id,
            site_name=snapshot.site_name,
            title="האתר הפסיק לדווח נתונים",
            message=(
                f"לא התקבל עדכון מהאתר מאז {snapshot.last_update_time:%Y-%m-%d %H:%M} "
                f"(כ-{silence.seconds // 60} דקות) — ייתכן ניתוק תקשורת בגייטוויי/אינטרנט."
            ),
            dedup_key=f"equipment_offline:{snapshot.site_id}",
            detected_at=now,
        )
    ]


def rule_zero_production_daylight(
    snapshot: SiteSnapshot,
    site_cfg: SiteConfig,
    rule_cfg: RuleConfig,
    active_hours: ActiveHours | None,
    now: datetime,
) -> list[Alert]:
    """Site is communicating fine but reports ~0W in the middle of its daylight window.

    Distinct from `equipment_offline`: the site IS reporting (so it's not a network
    problem) yet produces nothing - the classic symptom of a tripped breaker, blown
    fuse, or inverter fault that needs a technician dispatched, not a network engineer.
    """
    if not rule_cfg.enabled or not snapshot.is_reporting_fresh:
        return []
    if not _is_core_daylight(now.time(), active_hours):
        return []
    if snapshot.current_power_w > ZERO_POWER_THRESHOLD_W:
        return []

    return [
        Alert(
            rule="zero_production_daylight",
            severity=Severity.CRITICAL,
            site_id=snapshot.site_id,
            site_name=snapshot.site_name,
            title="ייצור אפס בשעות שיא שמש",
            message=(
                f"האתר מדווח הספק נוכחי של כ-0W בשעה {now:%H:%M}, "
                f"בזמן שהוא אמור לייצר באופן מלא. כדאי לבדוק ממסר ראשי / נתיכים / תקלת אינוורטר."
            ),
            dedup_key=f"zero_production_daylight:{snapshot.site_id}:{now:%Y-%m-%d}",
            detected_at=now,
        )
    ]


def rule_low_production(
    snapshot: SiteSnapshot,
    site_cfg: SiteConfig,
    rule_cfg: RuleConfig,
    active_hours: ActiveHours | None,
    now: datetime,
) -> list[Alert]:
    """Today's cumulative energy is trailing the site's expected baseline.

    Compares today's energy-so-far against `expected_daily_kwh` scaled by how much
    of the daylight window has elapsed - so a site isn't unfairly flagged at 9am for
    "only" having produced a third of its daily total. Needs `expected_daily_kwh`
    configured per site (a rough seasonal estimate is enough; this is a smoke
    detector, not a precision instrument).
    """
    if not rule_cfg.enabled or site_cfg.expected_daily_kwh is None:
        return []

    min_hour = rule_cfg.get("min_hour_of_day", 12)
    if now.hour < min_hour:
        return []
    if not snapshot.is_reporting_fresh:
        return []  # offline/comms rules already cover this case

    progress = _daylight_progress(now.time(), active_hours)
    if progress <= 0:
        return []

    expected_so_far_wh = site_cfg.expected_daily_kwh * 1000.0 * progress
    if expected_so_far_wh <= 0:
        return []

    threshold_pct = rule_cfg.get("threshold_pct", 70)
    actual_pct = (snapshot.today_energy_wh / expected_so_far_wh) * 100.0
    if actual_pct >= threshold_pct:
        return []

    return [
        Alert(
            rule="low_production",
            severity=Severity.WARNING,
            site_id=snapshot.site_id,
            site_name=snapshot.site_name,
            title="ייצור נמוך מהצפוי",
            message=(
                f"עד השעה {now:%H:%M} יוצרו {snapshot.today_energy_wh / 1000:.1f} קוט\"ש, "
                f"לעומת כ-{expected_so_far_wh / 1000:.1f} קוט\"ש שצפויים בשלב זה של היום "
                f"({actual_pct:.0f}% מהצפי, סף התרעה: {threshold_pct}%)."
            ),
            dedup_key=f"low_production:{snapshot.site_id}:{now:%Y-%m-%d}",
            detected_at=now,
        )
    ]


def rule_performance_drop(
    snapshots: list[SiteSnapshot],
    site_cfgs: dict[int, SiteConfig],
    rule_cfg: RuleConfig,
    active_hours: ActiveHours | None,
    now: datetime,
) -> list[Alert]:
    """Flags sites whose normalized output (current power / nameplate peak) lags the
    fleet's median by more than `threshold_pct`.

    This catches *relative* underperformance - shading, soiling, a failed string -
    that a fixed absolute threshold would miss, by comparing sites against their
    peers under the same sky at the same moment. Requires at least 3 reporting
    sites with known peak power to form a meaningful baseline.
    """
    if not rule_cfg.enabled or not _is_core_daylight(now.time(), active_hours):
        return []

    candidates = [
        s for s in snapshots if s.is_reporting_fresh and s.normalized_output is not None
    ]
    if len(candidates) < 3:
        return []

    ratios = [s.normalized_output for s in candidates]  # type: ignore[misc]
    median_ratio = statistics.median(ratios)
    if median_ratio <= 0:
        return []

    threshold_pct = rule_cfg.get("threshold_pct", 20)
    alerts: list[Alert] = []
    for snap in candidates:
        relative_drop_pct = (1 - (snap.normalized_output / median_ratio)) * 100.0  # type: ignore[operator]
        if relative_drop_pct < threshold_pct:
            continue
        site_cfg = site_cfgs.get(snap.site_id)
        site_name = site_cfg.name if site_cfg else snap.site_name
        alerts.append(
            Alert(
                rule="performance_drop",
                severity=Severity.WARNING,
                site_id=snap.site_id,
                site_name=site_name,
                title="ביצועים נמוכים יחסית לשאר הצי",
                message=(
                    f"האתר מייצר כ-{snap.normalized_output * 100:.0f}% מהספק השיא שלו, "
                    f"בעוד שחציון הצי עומד על כ-{median_ratio * 100:.0f}% "
                    f"(פער של כ-{relative_drop_pct:.0f}%, סף התרעה: {threshold_pct}%). "
                    f"ייתכן צל, לכלוך על הפאנלים, או תקלת מחרוזת מקומית."
                ),
                dedup_key=f"performance_drop:{snap.site_id}:{now:%Y-%m-%d}",
                detected_at=now,
            )
        )
    return alerts


def rule_alert_count_jump(
    snapshot: SiteSnapshot,
    site_cfg: SiteConfig,
    rule_cfg: RuleConfig,
    previous_count: int | None,
    now: datetime,
) -> list[Alert]:
    """SolarEdge's own open-alert counter for this site increased since the last check.

    The API won't tell us *what* the new alert is (see api_client docstring), but a
    jump is still a cheap, useful early-warning signal - it tells the fleet owner
    "go look at the portal for this specific site right now" faster than the daily
    digest email would.
    """
    if not rule_cfg.enabled or previous_count is None:
        return []
    if snapshot.alert_quantity <= previous_count:
        return []

    return [
        Alert(
            rule="alert_count_jump",
            severity=Severity.WARNING,
            site_id=snapshot.site_id,
            site_name=snapshot.site_name,
            title="עלייה במספר ההתראות הפתוחות באתר",
            message=(
                f"מספר ההתראות הפתוחות של סולראדג' עבור האתר עלה מ-{previous_count} ל-"
                f"{snapshot.alert_quantity}. כדאי להיכנס לפורטל הניטור ולבדוק את הפירוט."
            ),
            dedup_key=f"alert_count_jump:{snapshot.site_id}:{snapshot.alert_quantity}",
            detected_at=now,
        )
    ]
