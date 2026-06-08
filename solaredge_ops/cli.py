"""Command-line entry point.

Designed to be invoked by cron / systemd timers / Task Scheduler — each subcommand
runs once and exits, which is far easier to operate and debug than a long-lived
daemon:

    */30 6-19 * * *  solaredge-ops check  --config /etc/solaredge-ops/config.yaml
    0 6 1 * *        solaredge-ops report --config /etc/solaredge-ops/config.yaml
"""
from __future__ import annotations

import argparse
import calendar
import logging
import sys
from datetime import datetime

from .api_client import SolarEdgeClient
from .config import load_config
from .notifiers.base import Notifier
from .notifiers.email import EmailNotifier
from .notifiers.router import AlertRouter
from .notifiers.telegram import TelegramNotifier
from .poller import run_once
from .reporting import send_monthly_report
from .state_store import StateStore


def _build_notifiers(config) -> list[Notifier]:
    logger = logging.getLogger(__name__)

    if not config.recipients:
        logger.warning("No recipients configured - alerts will only be logged")
        return []

    telegram = TelegramNotifier(config.telegram) if config.telegram.enabled else None
    email = EmailNotifier(config.email) if config.email.enabled else None
    if telegram is None and email is None:
        logger.warning("No notification channel is enabled in config - alerts will only be logged")
        return []

    return [AlertRouter(config.recipients, telegram=telegram, email=email)]


def cmd_contacts(args: argparse.Namespace) -> int:
    config = load_config(args.config)
    if not config.recipients:
        print("No recipients configured under `recipients` in the config.")
        return 0

    for recipient in config.recipients:
        channels = []
        if recipient.telegram_chat_id:
            channels.append(f"Telegram (chat {recipient.telegram_chat_id})")
        if recipient.email:
            channels.append(f"Email ({recipient.email})")
        role = f" [{recipient.role}]" if recipient.role else ""
        phone = f" | phone: {recipient.phone}" if recipient.phone else ""
        categories = "all" if "all" in recipient.categories else ", ".join(recipient.categories)

        print(f"{recipient.name}{role}{phone}")
        print(f"    channels: {' + '.join(channels) if channels else 'NONE (will receive nothing!)'}")
        print(f"    subscribed to: {categories} (minimum severity: {recipient.min_severity.value})")
    return 0


def cmd_check(args: argparse.Namespace) -> int:
    config = load_config(args.config)
    client = SolarEdgeClient(config.api_key, config.max_requests_per_day)
    store = StateStore(config.state_db_path)
    notifiers = _build_notifiers(config)

    dispatched = run_once(config, client, store, notifiers)
    print(f"Check complete: {dispatched} new alert(s) dispatched.")
    return 0


def cmd_report(args: argparse.Namespace) -> int:
    config = load_config(args.config)
    client = SolarEdgeClient(config.api_key, config.max_requests_per_day)

    now = datetime.now()
    if args.month:
        year, month = (int(part) for part in args.month.split("-", 1))
    else:
        # Default: report on the *previous* calendar month (the month that just completed).
        year, month = now.year, now.month
        month -= 1
        if month == 0:
            year, month = year - 1, 12

    send_monthly_report(client, config, year, month)
    print(f"Monthly report for {calendar.month_name[month]} {year} sent.")
    return 0


def cmd_check_quota(args: argparse.Namespace) -> int:
    config = load_config(args.config)
    client = SolarEdgeClient(config.api_key, config.max_requests_per_day)
    for site in config.sites:
        remaining = client.rate_limiter.remaining(str(site.id))
        print(f"{site.name} (id={site.id}): {remaining}/{config.max_requests_per_day} requests remaining today (local estimate)")
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="solaredge-ops", description="Custom SolarEdge fleet monitoring, alerting and reporting")
    parser.add_argument("--config", default="config.yaml", help="Path to config.yaml (default: ./config.yaml)")
    parser.add_argument("-v", "--verbose", action="store_true", help="Enable debug logging")
    sub = parser.add_subparsers(dest="command", required=True)

    check = sub.add_parser("check", help="Run one fleet-wide alert check and exit")
    check.set_defaults(func=cmd_check)

    report = sub.add_parser("report", help="Generate and email the monthly report")
    report.add_argument("--month", help="Month to report on, format YYYY-MM (default: previous month)")
    report.set_defaults(func=cmd_report)

    quota = sub.add_parser("quota", help="Show the local estimate of remaining daily API quota per site")
    quota.set_defaults(func=cmd_check_quota)

    contacts = sub.add_parser("contacts", help="List configured recipients and what they're subscribed to")
    contacts.set_defaults(func=cmd_contacts)

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    logging.basicConfig(
        level=logging.DEBUG if args.verbose else logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    )
    try:
        return args.func(args)
    except Exception as exc:  # top-level guard so cron sees a clean non-zero exit + message
        logging.getLogger(__name__).exception("solaredge-ops %s failed", args.command)
        print(f"Error: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
