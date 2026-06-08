"""Loading and validating the YAML configuration file."""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import time
from pathlib import Path
from typing import Any

import yaml

from .models import Severity, severity_at_least


def _parse_time(value: str) -> time:
    hour, minute = (int(part) for part in value.split(":"))
    return time(hour=hour, minute=minute)


@dataclass
class SiteConfig:
    id: int
    name: str
    expected_daily_kwh: float | None = None
    location: str | None = None   # city name ("Tel Aviv") or "lat,lon" for weather lookups


@dataclass
class WeatherConfig:
    """Controls weather-based alert suppression."""
    enabled: bool = True
    suppress_alerts: bool = True          # suppress low/zero-production alerts when weather explains it
    suppress_ghi_kwh: float = 1.5         # GHI threshold below which alerts are suppressed
    suppress_cloud_pct: float = 80.0      # cloud-cover threshold above which alerts are suppressed


@dataclass
class ActiveHours:
    start: time
    end: time

    def contains(self, moment: time) -> bool:
        return self.start <= moment <= self.end


@dataclass
class PollingConfig:
    interval_minutes: int = 30
    active_hours: ActiveHours | None = None


@dataclass
class RuleConfig:
    enabled: bool = True
    options: dict[str, Any] = field(default_factory=dict)

    def get(self, key: str, default: Any = None) -> Any:
        return self.options.get(key, default)


@dataclass
class TelegramConfig:
    enabled: bool = False
    bot_token: str = ""


@dataclass
class EmailConfig:
    enabled: bool = False
    smtp_host: str = ""
    smtp_port: int = 587
    username: str = ""
    password: str = ""
    from_addr: str = ""


@dataclass
class MonthlyReportConfig:
    enabled: bool = True
    day_of_month: int = 1


@dataclass
class Recipient:
    """One person in the alert/report directory: who they are, how to reach them,
    and what they actually want to hear about.

    `categories` matches against `Alert.rule` (e.g. "equipment_offline"), the
    wildcard "all", and/or the special pseudo-category "monthly_report" (which
    only the monthly production report uses - it requires explicit opt-in so
    nobody is surprised by an email they didn't ask for).
    """

    name: str
    role: str = ""
    phone: str | None = None
    telegram_chat_id: str | None = None
    email: str | None = None
    categories: list[str] = field(default_factory=lambda: ["all"])
    min_severity: Severity = Severity.INFO

    def wants_alert(self, rule: str, severity: Severity) -> bool:
        matches_category = "all" in self.categories or rule in self.categories
        return matches_category and severity_at_least(severity, self.min_severity)

    def wants_report(self) -> bool:
        return "monthly_report" in self.categories


@dataclass
class Config:
    api_key: str
    max_requests_per_day: int
    sites: list[SiteConfig]
    polling: PollingConfig
    alert_rules: dict[str, RuleConfig]
    telegram: TelegramConfig
    email: EmailConfig
    monthly_report: MonthlyReportConfig
    recipients: list[Recipient]
    state_db_path: str
    weather: WeatherConfig = field(default_factory=WeatherConfig)

    def site_by_id(self, site_id: int) -> SiteConfig | None:
        return next((s for s in self.sites if s.id == site_id), None)


def _build_active_hours(raw: dict[str, Any] | None) -> ActiveHours | None:
    if not raw:
        return None
    return ActiveHours(start=_parse_time(raw["start"]), end=_parse_time(raw["end"]))


def _build_rules(raw: dict[str, Any] | None) -> dict[str, RuleConfig]:
    rules: dict[str, RuleConfig] = {}
    for name, body in (raw or {}).items():
        body = dict(body or {})
        enabled = bool(body.pop("enabled", True))
        rules[name] = RuleConfig(enabled=enabled, options=body)
    return rules


_VALID_SEVERITIES = {s.value for s in Severity}


def _build_recipients(raw: list[dict[str, Any]] | None) -> list[Recipient]:
    recipients: list[Recipient] = []
    for entry in raw or []:
        name = entry.get("name")
        if not name:
            raise ValueError("each entry under `recipients` must have a `name`")

        telegram_chat_id = entry.get("telegram_chat_id")
        email = entry.get("email")
        if not telegram_chat_id and not email:
            raise ValueError(
                f"recipient '{name}' has neither telegram_chat_id nor email - "
                "they would never actually receive anything"
            )

        min_severity_raw = str(entry.get("min_severity", Severity.INFO.value)).lower()
        if min_severity_raw not in _VALID_SEVERITIES:
            raise ValueError(
                f"recipient '{name}' has invalid min_severity '{min_severity_raw}' "
                f"(expected one of {sorted(_VALID_SEVERITIES)})"
            )

        recipients.append(
            Recipient(
                name=name,
                role=entry.get("role", ""),
                phone=(str(entry["phone"]) if entry.get("phone") is not None else None),
                telegram_chat_id=(str(telegram_chat_id) if telegram_chat_id else None),
                email=email,
                categories=list(entry.get("categories") or ["all"]),
                min_severity=Severity(min_severity_raw),
            )
        )
    return recipients


def load_config(path: str | Path) -> Config:
    """Read and validate the YAML config file at `path`."""
    raw = yaml.safe_load(Path(path).read_text(encoding="utf-8")) or {}

    se = raw.get("solaredge") or {}
    api_key = se.get("api_key", "")
    if not api_key or api_key.startswith("YOUR_"):
        raise ValueError(
            "solaredge.api_key is missing or still set to the placeholder value. "
            "Get a real API key from the SolarEdge monitoring portal (Site Admin > API access)."
        )

    sites_raw = raw.get("sites") or []
    if not sites_raw:
        raise ValueError("config must declare at least one site under `sites`")
    sites = [
        SiteConfig(
            id=int(s["id"]),
            name=s.get("name", str(s["id"])),
            expected_daily_kwh=(
                float(s["expected_daily_kwh"]) if s.get("expected_daily_kwh") is not None else None
            ),
            location=s.get("location") or None,
        )
        for s in sites_raw
    ]

    polling_raw = raw.get("polling") or {}
    polling = PollingConfig(
        interval_minutes=int(polling_raw.get("interval_minutes", 30)),
        active_hours=_build_active_hours(polling_raw.get("active_hours")),
    )

    notifications = raw.get("notifications") or {}
    telegram_raw = notifications.get("telegram") or {}
    telegram = TelegramConfig(
        enabled=bool(telegram_raw.get("enabled", False)),
        bot_token=telegram_raw.get("bot_token", ""),
    )

    email_raw = notifications.get("email") or {}
    email = EmailConfig(
        enabled=bool(email_raw.get("enabled", False)),
        smtp_host=email_raw.get("smtp_host", ""),
        smtp_port=int(email_raw.get("smtp_port", 587)),
        username=email_raw.get("username", ""),
        password=email_raw.get("password", ""),
        from_addr=email_raw.get("from_addr", ""),
    )

    report_raw = ((raw.get("reporting") or {}).get("monthly")) or {}
    monthly_report = MonthlyReportConfig(
        enabled=bool(report_raw.get("enabled", True)),
        day_of_month=int(report_raw.get("day_of_month", 1)),
    )

    recipients = _build_recipients(raw.get("recipients"))

    storage_raw = raw.get("storage") or {}
    weather_raw = raw.get("weather") or {}
    weather = WeatherConfig(
        enabled=bool(weather_raw.get("enabled", True)),
        suppress_alerts=bool(weather_raw.get("suppress_alerts", True)),
        suppress_ghi_kwh=float(weather_raw.get("suppress_ghi_kwh", 1.5)),
        suppress_cloud_pct=float(weather_raw.get("suppress_cloud_pct", 80.0)),
    )

    return Config(
        api_key=api_key,
        max_requests_per_day=int(se.get("max_requests_per_day", 300)),
        sites=sites,
        polling=polling,
        alert_rules=_build_rules(raw.get("alert_rules")),
        telegram=telegram,
        email=email,
        monthly_report=monthly_report,
        recipients=recipients,
        state_db_path=storage_raw.get("state_db_path", "state.db"),
        weather=weather,
    )
