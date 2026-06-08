"""
Analytics engine: loads CSV data (or falls back to live API) and computes
the KPIs that O&M fleet managers actually care about.

Metric definitions used throughout:
  specific_yield   -- kWh produced per day (proxy; true SY needs kWp capacity)
  performance_idx  -- actual_kwh / expected_kwh  (0-1+, >1 = above expectation)
  availability     -- estimated from zero/near-zero production days as % of active days
  yoy_delta_pct    -- year-over-year change in monthly energy, in percent
"""
from __future__ import annotations

import csv
import logging
from collections import defaultdict
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)

# ג”€ג”€ CSV loaders ג”€ג”€ג”€ג”€ג”€ג”€ג”€ג”€ג”€ג”€ג”€ג”€ג”€ג”€ג”€ג”€ג”€ג”€ג”€ג”€ג”€ג”€ג”€ג”€ג”€ג”€ג”€ג”€ג”€ג”€ג”€ג”€ג”€ג”€ג”€ג”€ג”€ג”€ג”€ג”€ג”€ג”€ג”€ג”€ג”€ג”€ג”€ג”€ג”€ג”€ג”€ג”€ג”€ג”€ג”€ג”€ג”€ג”€ג”€ג”€ג”€ג”€

def _data_dir(data_dir: str) -> Path:
    """Return the data directory Path. `data_dir` is config.data_dir (already resolved)."""
    return Path(data_dir)


def _load_csv(path: Path) -> list[dict]:
    if not path.exists():
        return []
    try:
        with open(path, encoding="utf-8") as f:
            return list(csv.DictReader(f))
    except Exception as exc:
        logger.warning("Could not read %s: %s", path, exc)
        return []


def load_daily(data_dir: str, site_id: int | None = None) -> list[dict]:
    rows = _load_csv(_data_dir(data_dir) / "energy_daily.csv")
    if site_id is not None:
        rows = [r for r in rows if int(r["site_id"]) == site_id]
    # deduplicate: keep latest row per (date, site_id)
    seen: dict[tuple, dict] = {}
    for r in rows:
        key = (r["date"], r["site_id"])
        seen[key] = r
    result = sorted(seen.values(), key=lambda r: r["date"])
    # cast numeric fields
    for r in result:
        r["energy_kwh"]   = _f(r.get("energy_kwh"))
        r["expected_kwh"] = _f(r.get("expected_kwh"))
    return result


def load_monthly(data_dir: str, site_id: int | None = None) -> list[dict]:
    rows = _load_csv(_data_dir(data_dir) / "energy_monthly.csv")
    if site_id is not None:
        rows = [r for r in rows if int(r["site_id"]) == site_id]
    seen: dict[tuple, dict] = {}
    for r in rows:
        key = (r["year_month"], r["site_id"])
        seen[key] = r
    result = sorted(seen.values(), key=lambda r: r["year_month"])
    for r in result:
        r["energy_kwh"] = _f(r.get("energy_kwh"))
    return result


def load_snapshots(data_dir: str, site_id: int | None = None) -> list[dict]:
    rows = _load_csv(_data_dir(data_dir) / "snapshots.csv")
    if site_id is not None:
        rows = [r for r in rows if int(r["site_id"]) == site_id]
    for r in rows:
        for k in ("current_power_kw","day_energy_kwh","month_energy_kwh",
                  "year_energy_kwh","lifetime_energy_kwh"):
            r[k] = _f(r.get(k))
    return rows


def load_alerts_log(data_dir: str) -> list[dict]:
    return _load_csv(_data_dir(data_dir) / "alerts_log.csv")


def load_weather(data_dir: str, site_id: int | None = None) -> list[dict]:
    """Load weather_daily.csv rows, optionally filtered by site."""
    rows = _load_csv(_data_dir(data_dir) / "weather_daily.csv")
    if site_id is not None:
        rows = [r for r in rows if int(r.get("site_id", 0)) == site_id]
    # deduplicate by date (keep last)
    seen: dict[str, dict] = {}
    for r in rows:
        seen[r["date"]] = r
    result = sorted(seen.values(), key=lambda r: r["date"])
    for r in result:
        r["ghi_kwh_m2"]       = _f(r.get("ghi_kwh_m2"))
        r["cloud_cover_pct"]  = _f(r.get("cloud_cover_pct"))
        r["precipitation_mm"] = _f(r.get("precipitation_mm"))
        r["temp_max_c"]       = _f(r.get("temp_max_c"))
        r["sunshine_h"]       = _f(r.get("sunshine_h"))
    return result


def data_files_info(data_dir: str) -> list[dict]:
    d = _data_dir(data_dir)
    files = []
    for name in ("snapshots.csv","energy_daily.csv","energy_monthly.csv","alerts_log.csv","weather_daily.csv"):
        p = d / name
        files.append({
            "name":    name,
            "exists":  p.exists(),
            "size_kb": round(p.stat().st_size / 1024, 1) if p.exists() else 0,
            "rows":    _count_rows(p),
            "path":    str(p),
        })
    return files


def _count_rows(path: Path) -> int:
    if not path.exists():
        return 0
    try:
        with open(path, encoding="utf-8") as f:
            return sum(1 for _ in f) - 1  # subtract header
    except Exception:
        return 0


def _f(v) -> float | None:
    try:
        return float(v) if v not in (None, "", "None") else None
    except (ValueError, TypeError):
        return None


# ג”€ג”€ fleet-level analytics ג”€ג”€ג”€ג”€ג”€ג”€ג”€ג”€ג”€ג”€ג”€ג”€ג”€ג”€ג”€ג”€ג”€ג”€ג”€ג”€ג”€ג”€ג”€ג”€ג”€ג”€ג”€ג”€ג”€ג”€ג”€ג”€ג”€ג”€ג”€ג”€ג”€ג”€ג”€ג”€ג”€ג”€ג”€ג”€ג”€ג”€ג”€ג”€ג”€ג”€ג”€ג”€

def fleet_summary(data_dir: str, sites: list) -> dict:
    """Top-level KPIs for the entire fleet."""
    daily   = load_daily(data_dir)
    snaps   = load_snapshots(data_dir)
    site_ids = [s.id for s in sites]

    # Latest snapshot per site
    latest_snap: dict[int, dict] = {}
    for r in snaps:
        sid = int(r["site_id"])
        latest_snap[sid] = r  # last row wins (CSV is chronological)

    total_power_kw   = sum(s.get("current_power_kw") or 0 for s in latest_snap.values())
    total_day_kwh    = sum(s.get("day_energy_kwh")   or 0 for s in latest_snap.values())
    total_month_kwh  = sum(s.get("month_energy_kwh") or 0 for s in latest_snap.values())
    total_year_kwh   = sum(s.get("year_energy_kwh")  or 0 for s in latest_snap.values())
    total_life_kwh   = sum(s.get("lifetime_energy_kwh") or 0 for s in latest_snap.values())

    # Last 30 days fleet production (daily sum across all sites)
    cutoff = (datetime.now(timezone.utc) - timedelta(days=30)).strftime("%Y-%m-%d")
    recent = [r for r in daily if r["date"] >= cutoff]
    by_date: dict[str, float] = defaultdict(float)
    for r in recent:
        if r["energy_kwh"] is not None:
            by_date[r["date"]] += r["energy_kwh"]
    timeline = [{"date": k, "energy_kwh": round(v, 2)} for k, v in sorted(by_date.items())]

    # Site ranking by last-30d production
    site_totals: dict[int, dict] = defaultdict(lambda: {"energy_kwh": 0, "site_name": ""})
    for r in recent:
        if r["energy_kwh"] is not None:
            sid = int(r["site_id"])
            site_totals[sid]["energy_kwh"] += r["energy_kwh"]
            site_totals[sid]["site_name"]   = r["site_name"]

    ranking = sorted(
        [{"site_id": k, **v, "energy_kwh": round(v["energy_kwh"], 1)} for k, v in site_totals.items()],
        key=lambda x: x["energy_kwh"], reverse=True
    )
    for i, r in enumerate(ranking):
        r["rank"] = i + 1

    return {
        "total_power_kw":   round(total_power_kw, 2),
        "total_day_kwh":    round(total_day_kwh, 2),
        "total_month_kwh":  round(total_month_kwh, 1),
        "total_year_kwh":   round(total_year_kwh, 0),
        "total_life_kwh":   round(total_life_kwh, 0),
        "site_count":       len(sites),
        "sites_with_data":  len(latest_snap),
        "timeline_30d":     timeline,
        "site_ranking":     ranking,
        "has_data":         bool(daily),
    }


# ג”€ג”€ site-level analytics ג”€ג”€ג”€ג”€ג”€ג”€ג”€ג”€ג”€ג”€ג”€ג”€ג”€ג”€ג”€ג”€ג”€ג”€ג”€ג”€ג”€ג”€ג”€ג”€ג”€ג”€ג”€ג”€ג”€ג”€ג”€ג”€ג”€ג”€ג”€ג”€ג”€ג”€ג”€ג”€ג”€ג”€ג”€ג”€ג”€ג”€ג”€ג”€ג”€ג”€ג”€ג”€ג”€

def site_analysis(data_dir: str, site_id: int, site_name: str,
                  expected_daily_kwh: float | None = None) -> dict:
    “””Full analytics for one site -- all chart data + KPIs.”””
    daily   = load_daily(data_dir, site_id)
    monthly = load_monthly(data_dir, site_id)
    snaps   = load_snapshots(data_dir, site_id)

    if not daily:
        return {"has_data": False, "site_id": site_id, "site_name": site_name}

    # ג”€ג”€ KPIs ג”€ג”€
    last_snap = snaps[-1] if snaps else {}
    recent_30d = [r for r in daily
                  if r["date"] >= (datetime.now(timezone.utc) - timedelta(days=30)).strftime("%Y-%m-%d")]
    recent_365d = [r for r in daily
                   if r["date"] >= (datetime.now(timezone.utc) - timedelta(days=365)).strftime("%Y-%m-%d")]

    total_30d  = sum(r["energy_kwh"] for r in recent_30d  if r["energy_kwh"] is not None)
    total_365d = sum(r["energy_kwh"] for r in recent_365d if r["energy_kwh"] is not None)

    # Performance Index (actual vs expected)
    perf_days = [r for r in recent_30d if r["energy_kwh"] is not None and r["expected_kwh"]]
    perf_index = None
    if perf_days:
        actual   = sum(r["energy_kwh"]   for r in perf_days)
        expected = sum(r["expected_kwh"] for r in perf_days)
        perf_index = round(actual / expected * 100, 1) if expected else None

    # Availability (days with >5% of expected, or >10kWh if no expected set)
    avail_days = [r for r in recent_30d if r["energy_kwh"] is not None]
    threshold = (expected_daily_kwh * 0.05) if expected_daily_kwh else 10.0
    available = sum(1 for r in avail_days if (r["energy_kwh"] or 0) > threshold)
    availability_pct = round(available / len(avail_days) * 100, 1) if avail_days else None

    # ג”€ג”€ Daily chart ג”€ג”€
    daily_chart = [{"date": r["date"], "energy_kwh": r["energy_kwh"],
                    "expected_kwh": r["expected_kwh"]} for r in daily[-365:]]

    # ג”€ג”€ Monthly chart: this year vs last year ג”€ג”€
    this_year = str(datetime.now(timezone.utc).year)
    last_year = str(datetime.now(timezone.utc).year - 1)
    monthly_by_ym: dict[str, float] = {}
    for r in monthly:
        if r["energy_kwh"] is not None:
            monthly_by_ym[r["year_month"]] = r["energy_kwh"]

    month_labels = [f"{m:02d}" for m in range(1, 13)]
    monthly_chart = {
        "months": month_labels,
        "this_year": [monthly_by_ym.get(f"{this_year}-{m}", None) for m in month_labels],
        "last_year": [monthly_by_ym.get(f"{last_year}-{m}", None) for m in month_labels],
        "this_year_label": this_year,
        "last_year_label": last_year,
    }

    # ג”€ג”€ YoY delta ג”€ג”€
    cur_month = datetime.now(timezone.utc).strftime("%Y-%m")
    prev_year_month = f"{last_year}-{datetime.now(timezone.utc).strftime('%m')}"
    yoy_delta = None
    if cur_month in monthly_by_ym and prev_year_month in monthly_by_ym:
        prev = monthly_by_ym[prev_year_month]
        curr = monthly_by_ym[cur_month]
        yoy_delta = round((curr - prev) / prev * 100, 1) if prev else None

    # ג”€ג”€ Performance Index trend (monthly, last 12 months) ג”€ג”€
    pi_trend = []
    for r in monthly[-12:]:
        if r["energy_kwh"] is not None and expected_daily_kwh:
            days_in_month = 30  # approximation
            exp = expected_daily_kwh * days_in_month
            pi_trend.append({
                "year_month": r["year_month"],
                "pi": round(r["energy_kwh"] / exp * 100, 1) if exp else None
            })

    # ג”€ג”€ Raw records (last 30 days for drill-down table) ג”€ג”€
    records = sorted(daily[-30:], key=lambda r: r["date"], reverse=True)

    # ג”€ג”€ Weather correlation (last 365 days) ג”€ג”€
    weather = load_weather(data_dir, site_id)
    weather_by_date: dict[str, dict] = {r["date"]: r for r in weather}
    # Annotate daily_chart rows with weather data
    for row in daily_chart:
        w = weather_by_date.get(row["date"])
        row["ghi_kwh_m2"]       = w["ghi_kwh_m2"]       if w else None
        row["cloud_cover_pct"]  = w["cloud_cover_pct"]  if w else None
        row["precipitation_mm"] = w["precipitation_mm"] if w else None
        row["weather_ok"]       = (w.get("weather_ok", "True") == "True" or w.get("weather_ok") is True) if w else None

    # Weather KPIs (last 30d)
    recent_weather = [weather_by_date[r["date"]] for r in recent_30d if r["date"] in weather_by_date]
    avg_ghi_30d = None
    avg_cloud_30d = None
    weather_suppressed_days = 0
    if recent_weather:
        ghis   = [r["ghi_kwh_m2"]      for r in recent_weather if r["ghi_kwh_m2"] is not None]
        clouds = [r["cloud_cover_pct"]  for r in recent_weather if r["cloud_cover_pct"] is not None]
        if ghis:   avg_ghi_30d   = round(sum(ghis) / len(ghis), 1)
        if clouds: avg_cloud_30d = round(sum(clouds) / len(clouds), 1)
        weather_suppressed_days = sum(
            1 for r in recent_weather
            if (r.get("ghi_kwh_m2") or 99) < 1.5 or (r.get("cloud_cover_pct") or 0) > 80
        )

    return {
        "has_data":         True,
        "site_id":          site_id,
        "site_name":        site_name,
        "expected_daily":   expected_daily_kwh,
        # KPIs
        "current_power_kw": last_snap.get("current_power_kw"),
        "day_energy_kwh":   last_snap.get("day_energy_kwh"),
        "month_energy_kwh": last_snap.get("month_energy_kwh"),
        "year_energy_kwh":  last_snap.get("year_energy_kwh"),
        "total_30d_kwh":    round(total_30d, 1),
        "total_365d_kwh":   round(total_365d, 0),
        "performance_index":perf_index,
        "availability_pct": availability_pct,
        "yoy_delta_pct":    yoy_delta,
        # Weather
        "has_weather":      bool(weather),
        "avg_ghi_30d":      avg_ghi_30d,
        "avg_cloud_30d":    avg_cloud_30d,
        "weather_suppressed_days": weather_suppressed_days,
        # Chart data
        "daily_chart":      daily_chart,
        "monthly_chart":    monthly_chart,
        "pi_trend":         pi_trend,
        "records":          records,
        "total_records":    len(daily),
    }


# ג”€ג”€ comparison analytics ג”€ג”€ג”€ג”€ג”€ג”€ג”€ג”€ג”€ג”€ג”€ג”€ג”€ג”€ג”€ג”€ג”€ג”€ג”€ג”€ג”€ג”€ג”€ג”€ג”€ג”€ג”€ג”€ג”€ג”€ג”€ג”€ג”€ג”€ג”€ג”€ג”€ג”€ג”€ג”€ג”€ג”€ג”€ג”€ג”€ג”€ג”€ג”€ג”€ג”€ג”€ג”€ג”€

def compare_sites(data_dir: str, site_ids: list[int], period_days: int = 30) -> dict:
    """Side-by-side comparison of selected sites."""
    daily = load_daily(data_dir)
    cutoff = (datetime.now(timezone.utc) - timedelta(days=period_days)).strftime("%Y-%m-%d")

    # Aggregate per site for the period
    by_site: dict[int, dict] = {}
    for r in daily:
        sid = int(r["site_id"])
        if sid not in site_ids:
            continue
        if r["date"] < cutoff:
            continue
        if sid not in by_site:
            by_site[sid] = {"site_name": r["site_name"], "energy_kwh": 0,
                             "expected_kwh": 0, "days": 0, "dates": [], "values": []}
        if r["energy_kwh"] is not None:
            by_site[sid]["energy_kwh"]   += r["energy_kwh"]
            by_site[sid]["days"]         += 1
            by_site[sid]["dates"].append(r["date"])
            by_site[sid]["values"].append(r["energy_kwh"])
        if r["expected_kwh"]:
            by_site[sid]["expected_kwh"] += r["expected_kwh"]

    # Compute metrics
    for sid, s in by_site.items():
        s["energy_kwh"]    = round(s["energy_kwh"], 1)
        s["avg_daily_kwh"] = round(s["energy_kwh"] / s["days"], 1) if s["days"] else 0
        s["perf_index"]    = round(s["energy_kwh"] / s["expected_kwh"] * 100, 1) \
                             if s["expected_kwh"] else None

    # Daily timeline per site for line chart
    timeline_by_site: dict[int, dict[str, float]] = defaultdict(dict)
    for r in daily:
        sid = int(r["site_id"])
        if sid in site_ids and r["date"] >= cutoff and r["energy_kwh"] is not None:
            timeline_by_site[sid][r["date"]] = r["energy_kwh"]

    # All dates in range
    all_dates = sorted({r["date"] for r in daily
                        if int(r["site_id"]) in site_ids and r["date"] >= cutoff})

    return {
        "sites":       by_site,
        "all_dates":   all_dates,
        "timeline":    {sid: [timeline_by_site[sid].get(d) for d in all_dates]
                        for sid in site_ids},
        "period_days": period_days,
        "has_data":    bool(by_site),
    }

