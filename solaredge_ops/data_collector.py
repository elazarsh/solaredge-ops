"""
Fetches data from the SolarEdge API and saves to local CSV files for analytics.

CSV layout (all in <config_dir>/data/):
  snapshots.csv        – one row per (site, collection run): current power + energy totals
  energy_daily.csv     – one row per (site, date): daily production in kWh
  energy_monthly.csv   – one row per (site, year-month): monthly production in kWh
  alerts_log.csv       – one row per alert event (new / still-open / resolved)

Files are append-only; the analytics layer deduplicates on read.
Running collect repeatedly is safe and idempotent for daily/monthly energy
(the same date rows just get duplicated, analytics takes the last value).
"""
from __future__ import annotations

import csv
import logging
from contextlib import contextmanager
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

from .config import Config, SiteConfig
from .api_client import SolarEdgeClient

logger = logging.getLogger(__name__)

# ── helpers ──────────────────────────────────────────────────────────────────

def _data_dir(config: Config) -> Path:
    d = Path(config.state_db_path).parent / "data"
    d.mkdir(parents=True, exist_ok=True)
    return d


@contextmanager
def _csv_appender(path: Path, fieldnames: list[str]):
    is_new = not path.exists()
    with open(path, "a", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames)
        if is_new:
            w.writeheader()
        yield w


def _wh_to_kwh(value: float | None) -> float | None:
    """SolarEdge energy endpoint returns Wh → convert to kWh."""
    return round(value / 1000, 3) if value is not None else None


def _now_iso() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")


# ── collectors ───────────────────────────────────────────────────────────────

def _collect_snapshot(data_dir: Path, client: SolarEdgeClient,
                       site: SiteConfig, collected_at: str) -> dict | None:
    """Fetch current overview and append a snapshot row."""
    try:
        ov = client.site_overview(site.id)
        row = {
            "collected_at":       collected_at,
            "site_id":            site.id,
            "site_name":          site.name,
            "current_power_kw":   round(ov.get("currentPower", {}).get("power", 0) / 1000, 3),
            "day_energy_kwh":     _wh_to_kwh(ov.get("lastDayData",   {}).get("energy")),
            "month_energy_kwh":   _wh_to_kwh(ov.get("lastMonthData", {}).get("energy")),
            "year_energy_kwh":    _wh_to_kwh(ov.get("lastYearData",  {}).get("energy")),
            "lifetime_energy_kwh":_wh_to_kwh(ov.get("lifeTimeData",  {}).get("energy")),
            "last_update":        ov.get("lastUpdateTime", ""),
        }
        with _csv_appender(data_dir / "snapshots.csv", list(row.keys())) as w:
            w.writerow(row)
        return row
    except Exception as exc:
        logger.warning("snapshot %s: %s", site.name, exc)
        return None


def _collect_daily_energy(data_dir: Path, client: SolarEdgeClient,
                           site: SiteConfig, today: datetime, days: int = 90) -> int:
    """Fetch daily energy for the last `days` days; appends to energy_daily.csv."""
    FIELDS = ["date", "site_id", "site_name", "energy_kwh", "expected_kwh"]
    start = today - timedelta(days=days)
    written = 0
    try:
        values = client.site_energy(site.id, start, today, time_unit="DAY")
        with _csv_appender(data_dir / "energy_daily.csv", FIELDS) as w:
            for v in values:
                if v.get("value") is None:
                    continue
                w.writerow({
                    "date":         v["date"][:10],
                    "site_id":      site.id,
                    "site_name":    site.name,
                    "energy_kwh":   _wh_to_kwh(v["value"]),
                    "expected_kwh": site.expected_daily_kwh or "",
                })
                written += 1
    except Exception as exc:
        logger.warning("daily energy %s: %s", site.name, exc)
    return written


def _collect_monthly_energy(data_dir: Path, client: SolarEdgeClient,
                             site: SiteConfig, today: datetime, months: int = 24) -> int:
    """Fetch monthly energy for the last `months` months."""
    FIELDS = ["year_month", "site_id", "site_name", "energy_kwh"]
    start = today.replace(day=1) - timedelta(days=months * 30)
    written = 0
    try:
        values = client.site_energy(site.id, start, today, time_unit="MONTH")
        with _csv_appender(data_dir / "energy_monthly.csv", FIELDS) as w:
            for v in values:
                if v.get("value") is None:
                    continue
                w.writerow({
                    "year_month": v["date"][:7],
                    "site_id":   site.id,
                    "site_name": site.name,
                    "energy_kwh":_wh_to_kwh(v["value"]),
                })
                written += 1
    except Exception as exc:
        logger.warning("monthly energy %s: %s", site.name, exc)
    return written


def _collect_alerts(data_dir: Path, config: Config, collected_at: str) -> int:
    """Log current open alerts from the state SQLite to alerts_log.csv."""
    import sqlite3
    from contextlib import closing
    FIELDS = ["logged_at", "event_type", "site_id", "site_name",
              "rule", "severity", "title", "message", "dedup_key"]
    db = Path(config.state_db_path)
    if not db.exists():
        return 0
    site_map = {s.id: s.name for s in config.sites}
    written = 0
    try:
        with closing(sqlite3.connect(str(db))) as conn:
            conn.row_factory = sqlite3.Row
            rows = conn.execute("SELECT * FROM open_alerts").fetchall()
        with _csv_appender(data_dir / "alerts_log.csv", FIELDS) as w:
            for r in rows:
                w.writerow({
                    "logged_at":  collected_at,
                    "event_type": "open",
                    "site_id":    r["site_id"],
                    "site_name":  site_map.get(r["site_id"], ""),
                    "rule":       r["rule"],
                    "severity":   r["severity"],
                    "title":      r["title"],
                    "message":    r["message"],
                    "dedup_key":  r["dedup_key"],
                })
                written += 1
    except Exception as exc:
        logger.warning("alerts log: %s", exc)
    return written


# ── demo data ─────────────────────────────────────────────────────────────────

def generate_demo_data(config: Config) -> None:
    """Write synthetic CSV data so the analytics dashboard is usable without a live API."""
    import random, math
    data_dir = _data_dir(config)
    today = datetime.now(timezone.utc)
    rng = random.Random(42)  # deterministic

    sites = config.sites
    if not sites:
        return

    # energy_daily.csv — 2 years of daily data
    DAILY_FIELDS = ["date", "site_id", "site_name", "energy_kwh", "expected_kwh"]
    with open(data_dir / "energy_daily.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, DAILY_FIELDS)
        w.writeheader()
        for site in sites:
            base = site.expected_daily_kwh or 300.0
            for d in range(730, -1, -1):
                dt = today - timedelta(days=d)
                if dt.weekday() >= 6:   # Sundays a touch lower
                    factor = 0.85
                else:
                    factor = 1.0
                # seasonal curve (Northern Hemisphere)
                day_of_year = dt.timetuple().tm_yday
                seasonal = 0.6 + 0.4 * math.sin(math.pi * (day_of_year - 80) / 180)
                noise = rng.gauss(1.0, 0.08)
                # occasional outage (2% of days)
                if rng.random() < 0.02:
                    energy = rng.uniform(0, base * 0.1)
                else:
                    energy = max(0, base * seasonal * factor * noise)
                w.writerow({
                    "date":         dt.strftime("%Y-%m-%d"),
                    "site_id":      site.id,
                    "site_name":    site.name,
                    "energy_kwh":   round(energy, 2),
                    "expected_kwh": base * seasonal,
                })

    # energy_monthly.csv — 3 years of monthly data
    MONTHLY_FIELDS = ["year_month", "site_id", "site_name", "energy_kwh"]
    with open(data_dir / "energy_monthly.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, MONTHLY_FIELDS)
        w.writeheader()
        for site in sites:
            base = (site.expected_daily_kwh or 300.0)
            for m in range(36, -1, -1):
                ref = (today.replace(day=1) - timedelta(days=m * 30))
                month_days = 30
                seasonal = 0.6 + 0.4 * math.sin(math.pi * (ref.month - 2) / 6)
                energy = base * month_days * seasonal * rng.gauss(0.97, 0.05)
                w.writerow({
                    "year_month": ref.strftime("%Y-%m"),
                    "site_id":    site.id,
                    "site_name":  site.name,
                    "energy_kwh": round(max(0, energy), 1),
                })

    # snapshots.csv — one row per day per site for the last 90 days
    SNAP_FIELDS = ["collected_at","site_id","site_name","current_power_kw",
                   "day_energy_kwh","month_energy_kwh","year_energy_kwh",
                   "lifetime_energy_kwh","last_update"]
    with open(data_dir / "snapshots.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, SNAP_FIELDS)
        w.writeheader()
        for site in sites:
            base = site.expected_daily_kwh or 300.0
            lifetime = base * 365 * 3
            for d in range(90, -1, -1):
                dt = today - timedelta(days=d)
                day_kwh = base * rng.gauss(0.9, 0.1)
                w.writerow({
                    "collected_at":        dt.strftime("%Y-%m-%d 08:00:00"),
                    "site_id":             site.id,
                    "site_name":           site.name,
                    "current_power_kw":    round(base / 8 * rng.gauss(1, 0.15), 2),
                    "day_energy_kwh":      round(max(0, day_kwh), 2),
                    "month_energy_kwh":    round(base * 20, 1),
                    "year_energy_kwh":     round(base * 200, 0),
                    "lifetime_energy_kwh": round(lifetime, 0),
                    "last_update":         dt.strftime("%Y-%m-%d 08:00:00"),
                })

    # weather_daily.csv — synthetic weather for the same 2-year window
    # (correlated with energy: low-energy days get low GHI / high cloud cover)
    import math as _math
    WEATHER_FIELDS = ["date","site_id","site_name","location","lat","lon",
                      "ghi_kwh_m2","cloud_cover_pct","precipitation_mm",
                      "temp_max_c","sunshine_h","weather_ok","weather_note"]
    # Use first site's location or fallback coords for Israel
    demo_lat, demo_lon = 32.08, 34.78  # Tel Aviv default
    with open(data_dir / "weather_daily.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, WEATHER_FIELDS)
        w.writeheader()
        # One row per day (same for all sites — weather doesn't depend on site)
        written_dates: set[str] = set()
        for site in sites[:1]:  # write once shared weather
            base = site.expected_daily_kwh or 300.0
            for d in range(730, -1, -1):
                dt = today - timedelta(days=d)
                ds = dt.strftime("%Y-%m-%d")
                if ds in written_dates:
                    continue
                written_dates.add(ds)
                day_of_year = dt.timetuple().tm_yday
                seasonal = 0.6 + 0.4 * _math.sin(_math.pi * (day_of_year - 80) / 180)
                # Base GHI proportional to seasonal curve (Israel peaks ~6-7 kWh/m² in summer)
                base_ghi = 2.0 + 4.5 * seasonal
                # 10% chance of cloudy day
                if rng.random() < 0.10:
                    ghi = rng.uniform(0.3, 1.8)
                    cloud = rng.uniform(70, 100)
                    rain = rng.uniform(0, 15) if rng.random() < 0.4 else 0.0
                else:
                    ghi = base_ghi * rng.gauss(0.95, 0.08)
                    cloud = max(0, rng.gauss(25, 20))
                    rain = 0.0
                sunshine = max(0, (1 - cloud / 100) * 14 * seasonal * rng.gauss(1, 0.05))
                temp = 15 + 15 * seasonal + rng.gauss(0, 3)
                w.writerow({
                    "date":            ds,
                    "site_id":         site.id,
                    "site_name":       site.name,
                    "location":        site.location or "Tel Aviv",
                    "lat":             demo_lat,
                    "lon":             demo_lon,
                    "ghi_kwh_m2":      round(max(0, ghi), 2),
                    "cloud_cover_pct": round(min(100, max(0, cloud)), 1),
                    "precipitation_mm":round(max(0, rain), 1),
                    "temp_max_c":      round(temp, 1),
                    "sunshine_h":      round(sunshine, 1),
                    "weather_ok":      ghi >= 1.5 and cloud <= 80,
                    "weather_note":    "" if ghi >= 1.5 and cloud <= 80 else
                                       (f"קרינה נמוכה ({ghi:.1f} kWh/m²)" if ghi < 1.5 else f"עננות ({cloud:.0f}%)"),
                })
        # Duplicate rows for all other sites
        for site in sites[1:]:
            with open(data_dir / "weather_daily.csv", "a", newline="", encoding="utf-8") as fa:
                wa = csv.DictWriter(fa, WEATHER_FIELDS)
                for ds in sorted(written_dates):
                    pass  # skip — analytics will use first site rows for weather overlay

    logger.info("Demo data written to %s", data_dir)


def _collect_weather(data_dir: Path, site: SiteConfig, days: int = 365) -> int:
    """Fetch and append historical weather data for a site. Returns rows written."""
    from .weather import geocode, fetch_range, assess_weather
    from datetime import date
    if not site.location:
        return 0
    coords = geocode(site.location)
    if coords is None:
        return 0
    lat, lon = coords
    today = date.today()
    start = today - timedelta(days=days)

    FIELDS = ["date","site_id","site_name","location","lat","lon",
              "ghi_kwh_m2","cloud_cover_pct","precipitation_mm",
              "temp_max_c","sunshine_h","weather_ok","weather_note"]

    rows = fetch_range(lat, lon, start, today)
    written = 0
    with _csv_appender(data_dir / "weather_daily.csv", FIELDS) as w:
        for row in rows:
            if not row.get("ghi_kwh_m2") and not row.get("cloud_cover_pct"):
                continue  # skip days with no data
            suppress, note = assess_weather(row)
            w.writerow({
                "date":            row["date"],
                "site_id":         site.id,
                "site_name":       site.name,
                "location":        site.location,
                "lat":             lat,
                "lon":             lon,
                "ghi_kwh_m2":      row.get("ghi_kwh_m2", ""),
                "cloud_cover_pct": row.get("cloud_cover_pct", ""),
                "precipitation_mm":row.get("precipitation_mm", ""),
                "temp_max_c":      row.get("temp_max_c", ""),
                "sunshine_h":      row.get("sunshine_h", ""),
                "weather_ok":      not suppress,
                "weather_note":    note,
            })
            written += 1
    logger.info("Weather collected for %s: %d rows", site.name, written)
    return written


# ── main entry point ──────────────────────────────────────────────────────────

def collect_all(config: Config, client: SolarEdgeClient) -> dict[str, int]:
    """Collect all data for all sites. Returns counts of rows written per file."""
    data_dir = _data_dir(config)
    collected_at = _now_iso()
    today = datetime.now(timezone.utc)
    counts: dict[str, int] = {"snapshots": 0, "daily": 0, "monthly": 0, "alerts": 0, "weather": 0}

    for site in config.sites:
        logger.info("Collecting %s (id=%s)...", site.name, site.id)

        snap = _collect_snapshot(data_dir, client, site, collected_at)
        if snap:
            counts["snapshots"] += 1

        counts["daily"]   += _collect_daily_energy(data_dir, client, site, today)
        counts["monthly"] += _collect_monthly_energy(data_dir, client, site, today)

        if site.location:
            counts["weather"] += _collect_weather(data_dir, site)

    counts["alerts"] += _collect_alerts(data_dir, config, collected_at)
    return counts
