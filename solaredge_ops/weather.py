"""
Weather data from Open-Meteo (https://open-meteo.com) — free, no API key.

Two APIs used:
  - archive-api.open-meteo.com  → historical data going back to 1940 (ERA5 reanalysis)
  - api.open-meteo.com          → forecast (today + up to 16 days)
  - geocoding-api.open-meteo.com → city name → lat/lon

Variables collected (daily aggregates):
  shortwave_radiation_sum  MJ/m²  → converted to kWh/m²  (Global Horizontal Irradiance proxy)
  cloud_cover_mean         %      (0 = clear, 100 = fully overcast)
  precipitation_sum        mm     (daily rain/snow)
  temperature_2m_max       °C     (affects panel efficiency at −0.4%/°C above 25°C STC)
  sunshine_duration        s      → hours

Solar suppression thresholds (tuned for Israel/Mediterranean conditions):
  GHI < 1.5 kWh/m²               → full suppress: nearly no sun, alerts are meaningless
  cloud_cover > 80%               → full suppress: heavily overcast
  1.5 ≤ GHI < 3.0  OR  60–80% cloud → partial: add weather note to alert message
"""
from __future__ import annotations

import logging
from dataclasses import dataclass
from datetime import date, timedelta
from typing import Any

logger = logging.getLogger(__name__)

_GEOCODE_URL  = "https://geocoding-api.open-meteo.com/v1/search"
_ARCHIVE_URL  = "https://archive-api.open-meteo.com/v1/archive"
_FORECAST_URL = "https://api.open-meteo.com/v1/forecast"
_DAILY_VARS   = "shortwave_radiation_sum,cloud_cover_mean,precipitation_sum,temperature_2m_max,sunshine_duration"

# MJ/m² → kWh/m²
_MJ_TO_KWH = 1.0 / 3.6

# Thresholds
_FULL_SUPPRESS_GHI_KWH   = 1.5    # below → full suppression
_FULL_SUPPRESS_CLOUD_PCT = 80.0   # above → full suppression
_PARTIAL_GHI_KWH         = 3.0    # below → partial (add note)
_PARTIAL_CLOUD_PCT        = 60.0  # above → partial (add note)
_RAIN_NOTE_MM             = 5.0   # above → mention rain in note

# In-process geocode cache (key: location string, value: (lat, lon) or None)
_geocode_cache: dict[str, tuple[float, float] | None] = {}


@dataclass
class WeatherData:
    """Daily weather summary for one site on one date."""
    date: str                       # "YYYY-MM-DD"
    site_id: int
    site_name: str
    location: str                   # city name or "lat,lon"
    lat: float
    lon: float
    ghi_kwh_m2: float | None = None
    cloud_cover_pct: float | None = None
    precipitation_mm: float | None = None
    temp_max_c: float | None = None
    sunshine_h: float | None = None

    @property
    def weather_available(self) -> bool:
        return self.ghi_kwh_m2 is not None or self.cloud_cover_pct is not None

    def as_csv_row(self) -> dict:
        suppressed, note = assess_weather(self)
        return {
            "date":             self.date,
            "site_id":          self.site_id,
            "site_name":        self.site_name,
            "location":         self.location,
            "lat":              self.lat,
            "lon":              self.lon,
            "ghi_kwh_m2":       _fmt(self.ghi_kwh_m2),
            "cloud_cover_pct":  _fmt(self.cloud_cover_pct),
            "precipitation_mm": _fmt(self.precipitation_mm),
            "temp_max_c":       _fmt(self.temp_max_c),
            "sunshine_h":       _fmt(self.sunshine_h),
            "weather_ok":       not suppressed,
            "weather_note":     note,
        }


def _fmt(v) -> str:
    return str(round(v, 2)) if v is not None else ""


# ── HTTP helper ───────────────────────────────────────────────────────────────

def _get(url: str, params: dict, timeout: int = 12) -> dict | None:
    try:
        import requests
        r = requests.get(url, params=params, timeout=timeout)
        r.raise_for_status()
        return r.json()
    except Exception as exc:
        logger.warning("Weather API (%s): %s", url.split("/")[2], exc)
        return None


# ── Geocoding ─────────────────────────────────────────────────────────────────

def geocode(location: str) -> tuple[float, float] | None:
    """
    Resolve a location string to (lat, lon).
    Accepts:
      "32.0853,34.7818"  → parsed as (lat, lon)
      "Tel Aviv"         → geocoded via Open-Meteo
      "חיפה"             → Hebrew city names work too
    Returns None (with a warning) if geocoding fails.
    """
    key = location.strip()
    if key in _geocode_cache:
        return _geocode_cache[key]

    # Try explicit "lat,lon" format
    parts = key.split(",")
    if len(parts) == 2:
        try:
            coords = (float(parts[0].strip()), float(parts[1].strip()))
            _geocode_cache[key] = coords
            return coords
        except ValueError:
            pass

    # Geocode via Open-Meteo
    data = _get(_GEOCODE_URL, {"name": key, "count": 1, "language": "he", "format": "json"})
    if data and data.get("results"):
        r = data["results"][0]
        coords = (float(r["latitude"]), float(r["longitude"]))
        logger.info("Geocoded %r → %.4f, %.4f (%s)", key, *coords, r.get("name", ""))
        _geocode_cache[key] = coords
        return coords

    logger.warning("Could not geocode %r — weather data unavailable for this site", key)
    _geocode_cache[key] = None
    return None


# ── Daily weather fetch ───────────────────────────────────────────────────────

def _parse_response(data: dict | None, target_date: str) -> dict | None:
    """Extract one day's values from an Open-Meteo daily response."""
    if not data or not data.get("daily"):
        return None
    d = data["daily"]
    dates = d.get("time", [])
    try:
        idx = dates.index(target_date)
    except ValueError:
        idx = 0 if dates else None
    if idx is None:
        return None

    def _v(key: str) -> float | None:
        arr = d.get(key)
        if arr and idx < len(arr) and arr[idx] is not None:
            return float(arr[idx])
        return None

    ghi_mj  = _v("shortwave_radiation_sum")
    sun_s   = _v("sunshine_duration")
    return {
        "ghi_kwh_m2":       round(ghi_mj * _MJ_TO_KWH, 2) if ghi_mj is not None else None,
        "cloud_cover_pct":  _v("cloud_cover_mean"),
        "precipitation_mm": _v("precipitation_sum"),
        "temp_max_c":       _v("temperature_2m_max"),
        "sunshine_h":       round(sun_s / 3600.0, 1) if sun_s is not None else None,
    }


def _parse_range_response(data: dict | None, out: dict[str, dict]) -> None:
    """Parse a multi-day Open-Meteo response into `out[date_str] = values_dict`."""
    if not data or not data.get("daily"):
        return
    d = data["daily"]
    for i, ds in enumerate(d.get("time", [])):
        def _v(key: str, _i: int = i) -> float | None:
            arr = d.get(key)
            if arr and _i < len(arr) and arr[_i] is not None:
                return float(arr[_i])
            return None
        ghi_mj = _v("shortwave_radiation_sum")
        sun_s  = _v("sunshine_duration")
        out[ds] = {
            "ghi_kwh_m2":       round(ghi_mj * _MJ_TO_KWH, 2) if ghi_mj is not None else None,
            "cloud_cover_pct":  _v("cloud_cover_mean"),
            "precipitation_mm": _v("precipitation_sum"),
            "temp_max_c":       _v("temperature_2m_max"),
            "sunshine_h":       round(sun_s / 3600.0, 1) if sun_s is not None else None,
        }


def fetch_day(lat: float, lon: float, for_date: date) -> dict | None:
    """
    Fetch daily weather for a single date (lat/lon).
    Returns dict with ghi_kwh_m2, cloud_cover_pct, ... or None on failure.
    Automatically uses archive API for past dates, forecast for today/future.
    """
    today = date.today()
    ds = for_date.isoformat()
    params_base = {"latitude": lat, "longitude": lon, "daily": _DAILY_VARS, "timezone": "auto"}

    if for_date < today:
        data = _get(_ARCHIVE_URL, {**params_base, "start_date": ds, "end_date": ds})
    else:
        days_ahead = max(1, (for_date - today).days + 1)
        data = _get(_FORECAST_URL, {**params_base, "forecast_days": days_ahead})

    return _parse_response(data, ds)


def fetch_range(lat: float, lon: float, start: date, end: date) -> list[dict]:
    """
    Fetch daily weather for a range of dates.
    Returns one dict per day (missing days have only {"date": "..."}).
    Splits into archive (past) and forecast (today+) as needed.
    """
    today = date.today()
    raw: dict[str, dict] = {}
    params_base = {"latitude": lat, "longitude": lon, "daily": _DAILY_VARS, "timezone": "auto"}

    # Archive: everything before today
    if start < today:
        arc_end = min(end, today - timedelta(days=1))
        data = _get(_ARCHIVE_URL, {**params_base,
                                    "start_date": start.isoformat(),
                                    "end_date":   arc_end.isoformat()})
        _parse_range_response(data, raw)

    # Forecast: today onwards
    if end >= today:
        fwd_start = max(start, today)
        days_ahead = min(16, (end - today).days + 2)
        data = _get(_FORECAST_URL, {**params_base,
                                     "start_date":    fwd_start.isoformat(),
                                     "end_date":      end.isoformat(),
                                     "forecast_days": days_ahead})
        _parse_range_response(data, raw)

    result = []
    current = start
    while current <= end:
        ds = current.isoformat()
        result.append({"date": ds, **raw[ds]} if ds in raw else {"date": ds})
        current += timedelta(days=1)
    return result


# ── Alert suppression logic ───────────────────────────────────────────────────

def assess_weather(w) -> tuple[bool, str]:
    """
    Assess whether weather explains low/zero solar production.

    Accepts either a WeatherData instance or a plain dict with the same keys.

    Returns:
        (suppress: bool, note: str)
        suppress=True  → weather fully explains the shortfall; suppress the alert
        note != ""     → mention weather conditions in the alert message
    """
    ghi   = w.ghi_kwh_m2      if isinstance(w, WeatherData) else w.get("ghi_kwh_m2")
    cloud = w.cloud_cover_pct if isinstance(w, WeatherData) else w.get("cloud_cover_pct")
    rain  = w.precipitation_mm if isinstance(w, WeatherData) else w.get("precipitation_mm")

    parts: list[str] = []

    # Full suppression conditions
    if ghi is not None and ghi < _FULL_SUPPRESS_GHI_KWH:
        return True, f"מזג אוויר מסביר: קרינה נמוכה מאוד ({ghi:.1f} kWh/m²)"
    if cloud is not None and cloud > _FULL_SUPPRESS_CLOUD_PCT:
        return True, f"מזג אוויר מסביר: עננות כבדה ({cloud:.0f}%)"

    # Partial / note-only conditions
    if ghi is not None and ghi < _PARTIAL_GHI_KWH:
        parts.append(f"קרינה חלקית ({ghi:.1f} kWh/m²)")
    elif cloud is not None and cloud > _PARTIAL_CLOUD_PCT:
        parts.append(f"עננות חלקית ({cloud:.0f}%)")

    if rain is not None and rain > _RAIN_NOTE_MM:
        parts.append(f"גשם ({rain:.0f} mm)")

    note = ("הערת מזג אוויר: " + ", ".join(parts)) if parts else ""
    return False, note
