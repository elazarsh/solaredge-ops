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

    from .notifiers.whatsapp import WhatsAppNotifier
    telegram = TelegramNotifier(config.telegram) if config.telegram.enabled else None
    whatsapp = WhatsAppNotifier(config.whatsapp) if config.whatsapp.enabled else None
    email    = EmailNotifier(config.email)    if config.email.enabled    else None
    if telegram is None and whatsapp is None and email is None:
        logger.warning("No notification channel is enabled in config - alerts will only be logged")
        return []

    return [AlertRouter(config.recipients, telegram=telegram, whatsapp=whatsapp, email=email)]


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


def cmd_collect(args: argparse.Namespace) -> int:
    from datetime import date as _date
    from .data_collector import collect_all, generate_demo_data
    config = load_config(args.config)
    if args.demo:
        print("=" * 60)
        print("WARNING: --demo writes SYNTHETIC FICTITIOUS data.")
        print("Use only for UI/dev testing, NEVER in production.")
        print("All demo rows are clearly marked site_name='DEMO-...'")
        print("=" * 60)
        generate_demo_data(config)
        print("Done. Demo data written. Do NOT use this for real analysis.")
        return 0

    # Resolve --backfill / --since overrides
    backfill_days: int | None = None
    since_date: _date | None = None
    if getattr(args, "since", None):
        try:
            since_date = _date.fromisoformat(args.since)
        except ValueError:
            print(f"Error: --since value '{args.since}' is not a valid YYYY-MM-DD date.", file=sys.stderr)
            return 1
    elif getattr(args, "backfill", None) is not None:
        if args.backfill <= 0:
            print("Error: --backfill must be a positive number of days.", file=sys.stderr)
            return 1
        backfill_days = args.backfill

    if since_date:
        print(f"Collecting data for {len(config.sites)} site(s) — backfill from {since_date}...")
    elif backfill_days:
        print(f"Collecting data for {len(config.sites)} site(s) — backfill {backfill_days} days...")
    else:
        print(f"Collecting data for {len(config.sites)} site(s)...")

    client = SolarEdgeClient(config.api_key, config.max_requests_per_day)
    counts = collect_all(config, client, backfill_days=backfill_days, since_date=since_date)
    print(f"  snapshots:      {counts['snapshots']} row(s)")
    print(f"  daily energy:   {counts['daily']} row(s)")
    print(f"  monthly energy: {counts['monthly']} row(s)")
    print(f"  alert events:   {counts['alerts']} row(s)")
    weather = counts.get("weather", 0)
    if weather:
        print(f"  weather:        {weather} row(s)")
    else:
        no_loc = [s.name for s in config.sites if not s.location]
        if no_loc:
            print(f"  weather:        skipped (add `location:` to sites: {', '.join(no_loc)})")
    print("Saved to data/ folder. Open the Analytics dashboard to explore.")
    return 0


def cmd_web(args: argparse.Namespace) -> int:
    from .web import run as web_run
    print(f"Starting web UI at http://{args.host}:{args.port}")
    web_run(config_path=args.config, host=args.host, port=args.port)
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

    collect = sub.add_parser("collect", help="Fetch data from API and save to CSV for analytics")
    collect.add_argument("--demo", action="store_true", help="Generate synthetic demo data (no API needed)")
    collect_bf = collect.add_mutually_exclusive_group()
    collect_bf.add_argument(
        "--backfill", type=int, metavar="DAYS",
        help="Fetch this many days back regardless of tracker (e.g. --backfill 730 for 2 years)"
    )
    collect_bf.add_argument(
        "--since", metavar="DATE",
        help="Fetch from a specific date to today, format YYYY-MM-DD (e.g. --since 2024-01-01)"
    )
    collect.set_defaults(func=cmd_collect)

    web = sub.add_parser("web", help="Start the web UI dashboard")
    web.add_argument("--port", type=int, default=5000, help="Port to listen on (default: 5000)")
    web.add_argument("--host", default="127.0.0.1", help="Host to bind (default: 127.0.0.1)")
    web.set_defaults(func=cmd_web)

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
