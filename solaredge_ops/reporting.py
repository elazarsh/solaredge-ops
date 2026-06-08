"""Generates and emails the monthly fleet production report.

SolarEdge's own portal can already schedule a similar "Monthly Summary" email -
this module exists for fleet owners who want the report's content, layout, and
recipient routing fully under their own control (e.g. merged with other KPIs,
sent through their own mail system, in their own language/branding).
"""
from __future__ import annotations

import calendar
import logging
from dataclasses import dataclass
from datetime import date, datetime

from .api_client import SolarEdgeApiError, SolarEdgeClient
from .config import Config, SiteConfig
from .notifiers.email import EmailNotifier

logger = logging.getLogger(__name__)


@dataclass
class SiteMonthSummary:
    site: SiteConfig
    energy_kwh: float
    previous_month_kwh: float | None
    co2_saved_kg: float | None

    @property
    def change_pct(self) -> float | None:
        if not self.previous_month_kwh:
            return None
        return ((self.energy_kwh - self.previous_month_kwh) / self.previous_month_kwh) * 100.0


def _month_bounds(year: int, month: int) -> tuple[date, date]:
    last_day = calendar.monthrange(year, month)[1]
    return date(year, month, 1), date(year, month, last_day)


def _previous_month(year: int, month: int) -> tuple[int, int]:
    return (year - 1, 12) if month == 1 else (year, month - 1)


def _site_month_energy_kwh(client: SolarEdgeClient, site_id: int, year: int, month: int) -> float:
    start, end = _month_bounds(year, month)
    values = client.site_energy(site_id, datetime.combine(start, datetime.min.time()), datetime.combine(end, datetime.min.time()), time_unit="MONTH")
    total_wh = sum(float(v.get("value") or 0) for v in values)
    return total_wh / 1000.0


def build_summaries(client: SolarEdgeClient, config: Config, year: int, month: int) -> list[SiteMonthSummary]:
    prev_year, prev_month = _previous_month(year, month)
    summaries: list[SiteMonthSummary] = []

    for site in config.sites:
        try:
            energy_kwh = _site_month_energy_kwh(client, site.id, year, month)
        except (SolarEdgeApiError, RuntimeError) as exc:
            logger.warning("Could not fetch energy for site %s: %s", site.name, exc)
            continue

        previous_kwh: float | None
        try:
            previous_kwh = _site_month_energy_kwh(client, site.id, prev_year, prev_month)
        except (SolarEdgeApiError, RuntimeError):
            previous_kwh = None

        co2_saved: float | None
        try:
            benefits = client.env_benefits(site.id)
            co2_saved = float(((benefits.get("gasEmissionSaved") or {}).get("co2")) or 0) or None
        except (SolarEdgeApiError, RuntimeError):
            co2_saved = None

        summaries.append(
            SiteMonthSummary(
                site=site,
                energy_kwh=energy_kwh,
                previous_month_kwh=previous_kwh,
                co2_saved_kg=co2_saved,
            )
        )

    return summaries


def render_report(summaries: list[SiteMonthSummary], year: int, month: int) -> tuple[str, str, str]:
    """Returns (subject, html_body, text_body)."""
    month_name = calendar.month_name[month]
    subject = f"דוח ייצור חודשי — {month_name} {year}"

    total_kwh = sum(s.energy_kwh for s in summaries)

    text_lines = [subject, "", f"סה\"כ ייצור הצי: {total_kwh:,.0f} קוט\"ש", ""]
    rows_html = []
    for s in summaries:
        change = s.change_pct
        change_text = f"{change:+.1f}%" if change is not None else "—"
        text_lines.append(
            f"- {s.site.name}: {s.energy_kwh:,.0f} קוט\"ש (שינוי מהחודש הקודם: {change_text})"
        )
        rows_html.append(
            "<tr>"
            f"<td>{s.site.name}</td>"
            f"<td style='text-align:right'>{s.energy_kwh:,.0f}</td>"
            f"<td style='text-align:right'>{change_text}</td>"
            f"<td style='text-align:right'>{(s.co2_saved_kg or 0):,.0f}</td>"
            "</tr>"
        )

    text_body = "\n".join(text_lines)
    html_body = f"""
    <div dir="rtl" style="font-family: Arial, sans-serif">
      <h2>{subject}</h2>
      <p><b>סה"כ ייצור הצי:</b> {total_kwh:,.0f} קוט"ש</p>
      <table border="1" cellpadding="6" cellspacing="0" style="border-collapse: collapse">
        <tr style="background:#f0f0f0">
          <th>אתר</th><th>ייצור (קוט"ש)</th><th>שינוי מול חודש קודם</th><th>חיסכון CO2 (ק"ג)</th>
        </tr>
        {''.join(rows_html)}
      </table>
    </div>
    """
    return subject, html_body, text_body


def send_monthly_report(client: SolarEdgeClient, config: Config, year: int, month: int) -> None:
    if not config.monthly_report.enabled:
        logger.info("Monthly report is disabled - skipping")
        return

    recipients = [r.email for r in config.recipients if r.email and r.wants_report()]
    if not recipients:
        logger.info(
            "No recipients are subscribed to the monthly report "
            "(add `monthly_report` to their `categories`) - skipping"
        )
        return

    summaries = build_summaries(client, config, year, month)
    if not summaries:
        logger.warning("No site data available for %s-%02d - report not sent", year, month)
        return

    subject, html_body, text_body = render_report(summaries, year, month)
    EmailNotifier(config.email).send(recipients, subject, html_body, text_body)
    logger.info("Monthly report for %s-%02d sent to %s", year, month, recipients)
