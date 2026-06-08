"""Shared data structures passed between the rule engine and notifiers."""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from enum import Enum


class Severity(str, Enum):
    INFO = "info"
    WARNING = "warning"
    CRITICAL = "critical"


_SEVERITY_ORDER = (Severity.INFO, Severity.WARNING, Severity.CRITICAL)


def severity_at_least(value: Severity, threshold: Severity) -> bool:
    """True if `value` is at least as severe as `threshold` (e.g. CRITICAL >= WARNING)."""
    return _SEVERITY_ORDER.index(value) >= _SEVERITY_ORDER.index(threshold)


@dataclass(frozen=True)
class Alert:
    """A single anomaly detected by a rule for one site (optionally one device).

    `dedup_key` identifies "the same problem" across poll cycles - the state store
    uses it to decide whether this is a brand new issue (-> notify), an ongoing one
    (-> stay quiet), or one that has just cleared (-> optionally notify "resolved").
    """

    rule: str
    severity: Severity
    site_id: int
    site_name: str
    title: str
    message: str
    dedup_key: str
    device_serial: str | None = None
    detected_at: datetime | None = None

    def format_for_chat(self) -> str:
        icon = {Severity.CRITICAL: "🔴", Severity.WARNING: "🟠", Severity.INFO: "ℹ️"}[self.severity]
        return f"{icon} *{self.site_name}*\n{self.title}\n{self.message}"
