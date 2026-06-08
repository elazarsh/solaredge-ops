"""Runs one fleet-wide check: fetch -> evaluate rules -> de-duplicate -> notify.

This is the thing a cron job / scheduled task calls every `polling.interval_minutes`.
It is intentionally a single "do one pass and exit" function (`run_once`) rather than
its own scheduler — cron/systemd-timer/Task Scheduler are more robust and observable
than a long-lived Python loop, and that keeps this tool boring and easy to operate.
"""
from __future__ import annotations

import logging
from datetime import datetime

from .api_client import SolarEdgeApiError, SolarEdgeClient
from .config import Config
from .models import Alert, Severity
from .notifiers.base import Notifier
from .rules import (
    SiteSnapshot,
    rule_alert_count_jump,
    rule_equipment_offline,
    rule_low_production,
    rule_performance_drop,
    rule_zero_production_daylight,
)
from .state_store import StateStore

logger = logging.getLogger(__name__)


def _fetch_snapshot(client: SolarEdgeClient, site, now: datetime) -> SiteSnapshot | None:
    try:
        overview = client.site_overview(site.id)
        details = client.site_details(site.id)
    except (SolarEdgeApiError, RuntimeError) as exc:
        logger.warning("Skipping site %s (%s): %s", site.id, site.name, exc)
        return None
    return SiteSnapshot(
        site_id=site.id,
        site_name=site.name,
        fetched_at=now,
        overview=overview,
        details=details,
    )


def _per_site_alerts(snapshot: SiteSnapshot, config: Config, store: StateStore, now: datetime) -> list[Alert]:
    site_cfg = config.site_by_id(snapshot.site_id)
    rules = config.alert_rules
    alerts: list[Alert] = []

    alerts += rule_equipment_offline(
        snapshot, site_cfg, rules.get("equipment_offline", _disabled()), now
    )
    alerts += rule_zero_production_daylight(
        snapshot, site_cfg, rules.get("zero_production_daylight", _disabled()), config.polling.active_hours, now
    )
    alerts += rule_low_production(
        snapshot, site_cfg, rules.get("low_production", _disabled()), config.polling.active_hours, now
    )

    jump_rule = rules.get("alert_count_jump")
    if jump_rule and jump_rule.enabled:
        prev_key = f"alert_quantity:{snapshot.site_id}"
        previous_raw = store.get_value(prev_key)
        previous_count = int(previous_raw) if previous_raw is not None else None
        alerts += rule_alert_count_jump(snapshot, site_cfg, jump_rule, previous_count, now)
        store.set_value(prev_key, str(snapshot.alert_quantity))

    return alerts


def _disabled():
    from .config import RuleConfig
    return RuleConfig(enabled=False)


def _dispatch(alert: Alert, store: StateStore, notifiers: list[Notifier]) -> bool:
    """Notify on `alert` only if it represents a newly-opened problem. Returns whether it dispatched."""
    if not store.mark_open(alert):
        return False  # already notified for this exact problem; stay quiet to avoid spam
    logger.info("New alert: %s [%s] %s", alert.site_name, alert.severity.value, alert.title)
    for notifier in notifiers:
        try:
            notifier.send_alert(alert)
        except Exception:
            logger.exception("Notifier %s failed to deliver alert %s", notifier.name, alert.dedup_key)
    return True


def _resolve_stale(rule: str, site_id: int, still_open: set[str], store: StateStore, notifiers: list[Notifier], site_name: str) -> None:
    for closed in store.close_stale(still_open, rule=rule, site_id=site_id):
        logger.info("Resolved: %s [%s] %s", site_name, closed["severity"], closed["title"])
        for notifier in notifiers:
            send_resolved = getattr(notifier, "send_resolved", None)
            if send_resolved is None:
                continue
            try:
                send_resolved(site_name, closed["title"], closed["severity"], rule)
            except Exception:
                logger.exception("Notifier %s failed to deliver resolution %s", notifier.name, closed["dedup_key"])


def run_once(config: Config, client: SolarEdgeClient, store: StateStore, notifiers: list[Notifier], now: datetime | None = None) -> int:
    """Run a single fleet-wide check. Returns the number of new alerts dispatched."""
    now = now or datetime.now()

    if config.polling.active_hours and not config.polling.active_hours.contains(now.time()):
        logger.debug("Outside active hours (%s) - skipping this cycle", now.time())
        return 0

    snapshots: list[SiteSnapshot] = []
    for site in config.sites:
        snapshot = _fetch_snapshot(client, site, now)
        if snapshot is not None:
            snapshots.append(snapshot)

    dispatched = 0
    per_site_open_keys: dict[tuple[str, int], set[str]] = {}

    def _handle(alert: Alert) -> None:
        nonlocal dispatched
        per_site_open_keys.setdefault((alert.rule, alert.site_id), set()).add(alert.dedup_key)
        if _dispatch(alert, store, notifiers):
            dispatched += 1

    for snapshot in snapshots:
        for alert in _per_site_alerts(snapshot, config, store, now):
            _handle(alert)

    fleet_rule = config.alert_rules.get("performance_drop")
    if fleet_rule and fleet_rule.enabled:
        site_cfgs = {s.id: s for s in config.sites}
        for alert in rule_performance_drop(snapshots, site_cfgs, fleet_rule, config.polling.active_hours, now):
            _handle(alert)

    # Close out anything that didn't reappear this cycle (i.e. it has cleared).
    for snapshot in snapshots:
        for rule_name in ("equipment_offline", "zero_production_daylight", "low_production", "performance_drop"):
            still_open = per_site_open_keys.get((rule_name, snapshot.site_id), set())
            _resolve_stale(rule_name, snapshot.site_id, still_open, store, notifiers, snapshot.site_name)

    return dispatched
