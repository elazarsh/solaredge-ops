"""Minimal Flask web UI for browsing system state."""
from __future__ import annotations

import json
import sqlite3
from contextlib import closing
from datetime import datetime, time, timezone
from pathlib import Path

import yaml
from flask import Flask, abort, render_template, request, redirect, send_file, url_for

from .config import Config, load_config

app = Flask(__name__)
_config: Config | None = None
_config_path: str = "config.yaml"


def _get_config() -> Config | None:
    try:
        return load_config(_config_path)
    except Exception:
        return None


def _open_alerts(config: Config) -> list[dict]:
    db = Path(config.state_db_path)
    if not db.exists():
        return []
    site_map = {s.id: s.name for s in config.sites}
    with closing(sqlite3.connect(str(db))) as conn:
        conn.row_factory = sqlite3.Row
        rows = conn.execute(
            "SELECT * FROM open_alerts ORDER BY first_seen DESC"
        ).fetchall()
    result = []
    for r in rows:
        d = dict(r)
        d["site_name"] = site_map.get(d["site_id"], "")
        result.append(d)
    return result


def _quota(config: Config) -> dict[int, int]:
    db = Path(config.state_db_path)
    if not db.exists():
        return {}
    quota = {}
    with closing(sqlite3.connect(str(db))) as conn:
        for site in config.sites:
            row = conn.execute(
                "SELECT value FROM kv_state WHERE key = ?",
                (f"quota_remaining_{site.id}",),
            ).fetchone()
            quota[site.id] = int(row[0]) if row else config.max_requests_per_day
    return quota


def _in_active_hours(config: Config) -> bool:
    if not config.polling.active_hours:
        return True
    now = datetime.now(timezone.utc).astimezone().time().replace(tzinfo=None)
    return config.polling.active_hours.contains(now)


def _mask(value: str, show: int = 4) -> str:
    if not value or len(value) <= show:
        return "••••••••"
    return value[:show] + "••••••••" + value[-2:]


def _nav_context(config: Config | None) -> dict:
    open_count = len(_open_alerts(config)) if config else 0
    return {"open_count": open_count}


def _default_config() -> Config:
    """Return a Config pre-filled with sensible defaults for the first-time setup form."""
    from datetime import time as _time
    from .config import (
        PollingConfig, ActiveHours, RuleConfig,
        TelegramConfig, EmailConfig, MonthlyReportConfig, WeatherConfig,
    )
    return Config(
        api_key="",
        max_requests_per_day=300,
        sites=[],
        polling=PollingConfig(
            interval_minutes=30,
            active_hours=ActiveHours(start=_time(6, 0), end=_time(19, 0)),
        ),
        alert_rules={
            "equipment_offline":       RuleConfig(enabled=True,  options={"grace_minutes": 60}),
            "zero_production_daylight":RuleConfig(enabled=True,  options={"grace_minutes": 45}),
            "low_production":          RuleConfig(enabled=True,  options={"threshold_pct": 70}),
            "performance_drop":        RuleConfig(enabled=True,  options={"threshold_pct": 20}),
            "alert_count_jump":        RuleConfig(enabled=True,  options={}),
        },
        telegram=TelegramConfig(enabled=False, bot_token=""),
        email=EmailConfig(
            enabled=False,
            smtp_host="smtp.gmail.com",
            smtp_port=587,
            username="",
            password="",
            from_addr="",
        ),
        monthly_report=MonthlyReportConfig(enabled=True, day_of_month=1),
        recipients=[],
        state_db_path="state.db",
        data_dir="",
        weather=WeatherConfig(),
    )


@app.route("/")
def dashboard():
    config = _get_config()
    if not config:
        return render_template(
            "no_config.html", active="dashboard", open_count=0, config_path=_config_path
        )
    alerts = _open_alerts(config)
    quota = _quota(config)
    ah = config.polling.active_hours
    return render_template(
        "dashboard.html",
        active="dashboard",
        open_count=len(alerts),
        sites=config.sites,
        open_alerts=alerts,
        recipients=config.recipients,
        quota=quota,
        max_quota=config.max_requests_per_day,
        active_hours=ah,
        in_active_hours=_in_active_hours(config),
        polling_interval=config.polling.interval_minutes,
    )


@app.route("/alerts")
def alerts():
    config = _get_config()
    if not config:
        return render_template(
            "no_config.html", active="alerts", open_count=0, config_path=_config_path
        )
    site_map = {s.id: s.name for s in config.sites}
    data = _open_alerts(config)
    return render_template(
        "alerts.html",
        active="alerts",
        open_count=len(data),
        alerts=data,
        site_names=site_map,
    )


@app.route("/contacts")
def contacts():
    config = _get_config()
    if not config:
        return render_template(
            "no_config.html", active="contacts", open_count=0, config_path=_config_path
        )
    return render_template(
        "contacts.html",
        active="contacts",
        open_count=len(_open_alerts(config)),
        recipients=config.recipients,
    )


@app.route("/config")
def config_view():
    config = _get_config()
    if not config:
        return render_template(
            "no_config.html", active="config", open_count=0, config_path=_config_path
        )
    ah = config.polling.active_hours
    ah_str = f"{ah.start.strftime('%H:%M')} — {ah.end.strftime('%H:%M')}" if ah else None
    return render_template(
        "config.html",
        active="config",
        open_count=len(_open_alerts(config)),
        api_key_masked=_mask(config.api_key),
        max_requests_per_day=config.max_requests_per_day,
        polling_interval=config.polling.interval_minutes,
        active_hours=ah_str,
        sites=config.sites,
        telegram_enabled=config.telegram.enabled,
        telegram_token_masked=_mask(config.telegram.bot_token),
        email_enabled=config.email.enabled,
        smtp_host=config.email.smtp_host,
        smtp_port=config.email.smtp_port,
        smtp_user=config.email.username,
        rules=config.alert_rules,
        state_db_path=config.state_db_path,
    )


def _form_to_yaml(f) -> str:
    """Build a YAML dict from the structured config form and return it as a string."""
    # sites — parallel lists
    site_ids       = f.getlist("site_id")
    site_names     = f.getlist("site_name")
    site_kwhs      = f.getlist("site_kwh")
    site_locations = f.getlist("site_location")
    sites = []
    for i, (sid, sname, skwh) in enumerate(zip(site_ids, site_names, site_kwhs)):
        entry: dict = {"id": int(sid), "name": sname}
        if skwh.strip():
            entry["expected_daily_kwh"] = float(skwh)
        loc = site_locations[i].strip() if i < len(site_locations) else ""
        if loc:
            entry["location"] = loc
        sites.append(entry)

    # polling active hours
    ah_start = f.get("active_start", "").strip()
    ah_end   = f.get("active_end",   "").strip()
    polling: dict = {"interval_minutes": int(f.get("interval_minutes", 30))}
    if ah_start and ah_end:
        polling["active_hours"] = {"start": ah_start, "end": ah_end}

    # alert rules
    rule_keys = ["equipment_offline", "zero_production_daylight", "low_production",
                 "performance_drop", "alert_count_jump"]
    opt_keys  = {"equipment_offline": "grace_minutes",
                 "zero_production_daylight": "grace_minutes",
                 "low_production": "threshold_pct",
                 "performance_drop": "threshold_pct"}
    alert_rules = {}
    for rk in rule_keys:
        enabled = f"rule_{rk}" in f
        entry: dict = {"enabled": enabled}
        ok = opt_keys.get(rk)
        if ok:
            val = f.get(f"rule_opt_{rk}", "").strip()
            if val:
                entry[ok] = int(val)
        alert_rules[rk] = entry

    # recipients — parallel lists (one value per recipient per field)
    r_names     = f.getlist("r_name")
    r_roles     = f.getlist("r_role")
    r_phones    = f.getlist("r_phone")
    r_severities= f.getlist("r_severity")
    r_telegrams = f.getlist("r_telegram")
    r_emails    = f.getlist("r_email")
    r_cats_list = f.getlist("r_categories")  # comma-joined string per recipient

    recipients = []
    for i, name in enumerate(r_names):
        if not name.strip():
            continue
        cats_str = r_cats_list[i] if i < len(r_cats_list) else "all"
        cats = [c.strip() for c in cats_str.split(",") if c.strip()] or ["all"]
        rec: dict = {
            "name": name,
            "role": r_roles[i] if i < len(r_roles) else "",
            "categories": cats,
            "min_severity": r_severities[i] if i < len(r_severities) else "info",
        }
        phone = r_phones[i].strip() if i < len(r_phones) else ""
        tg    = r_telegrams[i].strip() if i < len(r_telegrams) else ""
        email = r_emails[i].strip() if i < len(r_emails) else ""
        if phone: rec["phone"] = phone
        if tg:    rec["telegram_chat_id"] = tg
        if email: rec["email"] = email
        recipients.append(rec)

    doc = {
        "solaredge": {
            "api_key": f.get("api_key", ""),
            "max_requests_per_day": int(f.get("max_requests_per_day", 300)),
        },
        "sites": sites,
        "polling": polling,
        "alert_rules": alert_rules,
        "notifications": {
            "telegram": {
                "enabled": "telegram_enabled" in f,
                "bot_token": f.get("telegram_token", ""),
            },
            "email": {
                "enabled": "email_enabled" in f,
                "smtp_host": f.get("smtp_host", ""),
                "smtp_port": int(f.get("smtp_port", 587) or 587),
                "username":  f.get("smtp_user", ""),
                "password":  f.get("smtp_pass", ""),
                "from_addr": f.get("from_addr", ""),
            },
        },
        "recipients": recipients,
        "reporting": {"monthly": {"enabled": True, "day_of_month": 1}},
        "storage": {
            "state_db_path": "state.db",
            "data_path": f.get("data_path", "").strip(),
        },
    }
    return yaml.dump(doc, allow_unicode=True, sort_keys=False, default_flow_style=False)


def _config_edit_ctx(config, config_path: Path, error=None, saved=False):
    ah = config.polling.active_hours if config else None
    return dict(
        active="config",
        open_count=0,
        config_path=str(config_path),
        cfg=config,
        active_start=ah.start.strftime("%H:%M") if ah else "",
        active_end=ah.end.strftime("%H:%M") if ah else "",
        error=error,
        saved=saved,
    )


@app.route("/config/edit", methods=["GET", "POST"])
def config_edit():
    config_path = Path(_config_path)
    error = None
    saved = False

    if request.method == "POST":
        try:
            yaml_text = _form_to_yaml(request.form)
            yaml.safe_load(yaml_text)   # syntax check only
            config_path.write_text(yaml_text, encoding="utf-8")
            saved = True
        except Exception as exc:
            error = str(exc)

    config = _get_config()
    # First-time setup: no config.yaml yet — show form with sensible defaults
    if config is None and not saved:
        config = _default_config()

    if config is None:
        return render_template("no_config.html", active="config", open_count=0, config_path=str(config_path))

    is_new = not config_path.exists()
    return render_template("config_edit.html",
                           is_new=is_new,
                           **_config_edit_ctx(config, config_path, error, saved))


# ── Analytics routes ──────────────────────────────────────────────────────────

@app.route("/analytics/")
@app.route("/analytics")
def analytics_fleet():
    from .analytics import fleet_summary
    config = _get_config()
    if not config:
        return render_template("no_config.html", active="analytics", open_count=0, config_path=_config_path)

    source = request.args.get("source", "csv")
    summary = fleet_summary(config.data_dir, config.sites)

    # full timeline (for client-side period filtering)
    from .analytics import load_daily
    all_daily = load_daily(config.data_dir)
    from collections import defaultdict
    by_date: dict[str, float] = defaultdict(float)
    for r in all_daily:
        if r["energy_kwh"] is not None:
            by_date[r["date"]] += r["energy_kwh"]
    full_timeline = [{"date": k, "energy_kwh": round(v, 2)} for k, v in sorted(by_date.items())]

    return render_template(
        "analytics/fleet.html",
        active="analytics",
        open_count=len(_open_alerts(config)),
        summary=summary,
        has_data=summary.get("has_data", False),
        source=source,
        timeline_json=json.dumps(full_timeline),
        ranking_json=json.dumps(summary.get("site_ranking", [])),
    )


@app.route("/analytics/site/<int:site_id>")
def analytics_site(site_id: int):
    from .analytics import site_analysis, load_daily
    config = _get_config()
    if not config:
        return render_template("no_config.html", active="analytics", open_count=0, config_path=_config_path)

    site_cfg  = next((s for s in config.sites if s.id == site_id), None)
    site_name = site_cfg.name if site_cfg else f"Site {site_id}"
    expected  = getattr(site_cfg, "expected_daily_kwh", None) if site_cfg else None
    source    = request.args.get("source", "csv")
    period    = int(request.args.get("period", 365))

    analysis  = site_analysis(config.data_dir, site_id, site_name, expected)

    # Drill-down table: all daily records for the selected period
    all_recs = load_daily(config.data_dir, site_id)
    records  = sorted(all_recs[-period:], key=lambda r: r["date"], reverse=True)

    # Daily chart data for selected period
    daily_chart = analysis.get("daily_chart", [])[-period:]

    return render_template(
        "analytics/site.html",
        active="analytics",
        open_count=len(_open_alerts(config)),
        analysis=analysis,
        has_data=analysis.get("has_data", False),
        site_id=site_id,
        site_name=site_name,
        source=source,
        period=period,
        sites=config.sites,
        records=records,
        daily_json=json.dumps(daily_chart),
        monthly_json=json.dumps(analysis.get("monthly_chart", {})),
        pi_json=json.dumps(analysis.get("pi_trend", [])),
    )


@app.route("/analytics/compare")
def analytics_compare():
    from .analytics import compare_sites
    config = _get_config()
    if not config:
        return render_template("no_config.html", active="analytics", open_count=0, config_path=_config_path)

    selected_raw = request.args.get("sites", "")
    period       = int(request.args.get("period", 30))

    if selected_raw:
        selected_ids = [int(x) for x in selected_raw.split(",") if x.strip().isdigit()]
    else:
        selected_ids = [s.id for s in config.sites]

    comparison = compare_sites(config.data_dir, selected_ids, period)

    COLORS = ["#3fb950", "#58a6ff", "#e3b341", "#f85149", "#a371f7", "#39d353"]
    traces = []
    for i, sid in enumerate(selected_ids):
        site_data = comparison["sites"].get(sid, {})
        traces.append({
            "site_id":   sid,
            "site_name": site_data.get("site_name", f"Site {sid}"),
            "values":    comparison["timeline"].get(sid, []),
            "color":     COLORS[i % len(COLORS)],
        })

    return render_template(
        "analytics/compare.html",
        active="analytics",
        open_count=len(_open_alerts(config)),
        comparison=comparison,
        sites=config.sites,
        selected_ids=selected_ids,
        period=period,
        has_data=comparison.get("has_data", False),
        dates_json=json.dumps(comparison.get("all_dates", [])),
        traces_json=json.dumps(traces),
    )


@app.route("/analytics/export")
def analytics_export():
    from .analytics import data_files_info
    config = _get_config()
    if not config:
        return render_template("no_config.html", active="analytics", open_count=0, config_path=_config_path)

    files = data_files_info(config.data_dir)
    return render_template(
        "analytics/export.html",
        active="analytics",
        open_count=len(_open_alerts(config)),
        files=files,
    )


@app.route("/analytics/download/<filename>")
def analytics_download(filename: str):
    _allowed = {"snapshots.csv", "energy_daily.csv", "energy_monthly.csv", "alerts_log.csv", "weather_daily.csv"}
    if filename not in _allowed:
        abort(404)
    config = _get_config()
    if not config:
        abort(404)
    p = Path(config.data_dir) / filename
    if not p.exists():
        abort(404)
    return send_file(str(p.resolve()), as_attachment=True, download_name=filename)


def run(config_path: str = "config.yaml", host: str = "127.0.0.1", port: int = 5000, debug: bool = False):
    global _config_path
    _config_path = config_path
    app.run(host=host, port=port, debug=debug)
