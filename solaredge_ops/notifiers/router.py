"""Routes alerts and resolutions to the people who actually want them.

The `recipients` directory in the config replaces a single fixed chat/inbox
with a real contact list: each person declares their channel(s) (Telegram chat,
email, or both) and what they're subscribed to (`categories` - alert rule names,
"all", or the special "monthly_report" pseudo-category - plus a `min_severity`
floor). `AlertRouter` is the single `Notifier` that `run_once` and the CLI talk
to; it fans each alert/resolution out to the matching recipients over their
configured channels, so e.g. the maintenance crew gets real-time field alerts
on Telegram while finance only gets the monthly report by email.
"""
from __future__ import annotations

import logging

from ..config import Recipient
from ..models import Alert, Severity
from .base import Notifier
from .email import EmailNotifier
from .telegram import TelegramNotifier

logger = logging.getLogger(__name__)


def _alert_email_parts(alert: Alert) -> tuple[str, str, str]:
    subject = f"[SolarEdge] {alert.severity.value.upper()} - {alert.site_name}"
    text = f"{alert.title}\n\n{alert.message}"
    html = f"<h3>{alert.title}</h3><p>{alert.message}</p><p><b>אתר:</b> {alert.site_name}</p>"
    return subject, html, text


def _resolved_parts(site_name: str, title: str) -> tuple[str, str, str, str]:
    chat_text = f"✅ *{site_name}*\nהבעיה חלפה: {title}"
    subject = f"[SolarEdge] Resolved - {site_name}"
    text = f"הבעיה נפתרה: {title}\nאתר: {site_name}"
    html = f"<p>✅ הבעיה נפתרה: <b>{title}</b></p><p>אתר: {site_name}</p>"
    return chat_text, subject, html, text


class AlertRouter(Notifier):
    """The single `Notifier` the poller talks to; fans out per-recipient subscriptions."""

    name = "router"

    def __init__(
        self,
        recipients: list[Recipient],
        telegram: TelegramNotifier | None = None,
        email: EmailNotifier | None = None,
    ):
        self.recipients = recipients
        self.telegram = telegram
        self.email = email

    def send_alert(self, alert: Alert) -> None:
        subject, html, text = _alert_email_parts(alert)
        for recipient in self.recipients:
            if recipient.wants_alert(alert.rule, alert.severity):
                self._deliver(recipient, alert.format_for_chat(), subject, html, text)

    def send_resolved(self, site_name: str, title: str, severity: str, rule: str) -> None:
        chat_text, subject, html, text = _resolved_parts(site_name, title)
        for recipient in self.recipients:
            if recipient.wants_alert(rule, Severity(severity)):
                self._deliver(recipient, chat_text, subject, html, text)

    def _deliver(self, recipient: Recipient, chat_text: str, subject: str, html: str, text: str) -> None:
        if recipient.telegram_chat_id and self.telegram:
            try:
                self.telegram.send(recipient.telegram_chat_id, chat_text)
            except Exception:
                logger.exception("Failed to deliver Telegram message to %s", recipient.name)
        if recipient.email and self.email:
            try:
                self.email.send([recipient.email], subject, html, text)
            except Exception:
                logger.exception("Failed to deliver email to %s", recipient.name)
