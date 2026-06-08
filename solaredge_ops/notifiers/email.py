"""SMTP email transport.

Used for the monthly report and (optionally) as a secondary alert channel for
stakeholders who don't want Telegram.

This class is a thin transport: it knows how to deliver a prepared message to
an explicit list of addresses, nothing more. Deciding *who* gets *which*
message is the job of `notifiers.router.AlertRouter`, driven by the
`recipients` directory in the config.
"""
from __future__ import annotations

import logging
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from ..config import EmailConfig

logger = logging.getLogger(__name__)


class EmailNotifier:
    name = "email"

    def __init__(self, config: EmailConfig):
        self.config = config

    def send(self, to_addrs: list[str], subject: str, html_body: str, text_body: str) -> None:
        cfg = self.config
        if not cfg.enabled or not to_addrs:
            logger.warning("Email not enabled/configured - dropping message '%s'", subject)
            return

        message = MIMEMultipart("alternative")
        message["Subject"] = subject
        message["From"] = cfg.from_addr
        message["To"] = ", ".join(to_addrs)
        message.attach(MIMEText(text_body, "plain", "utf-8"))
        message.attach(MIMEText(html_body, "html", "utf-8"))

        with smtplib.SMTP(cfg.smtp_host, cfg.smtp_port) as server:
            server.starttls()
            if cfg.username:
                server.login(cfg.username, cfg.password)
            server.sendmail(cfg.from_addr, to_addrs, message.as_string())
