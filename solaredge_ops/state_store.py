"""Tiny SQLite-backed store that remembers which alerts are already "open".

This is what turns a raw rule evaluation ("production is low right now") into a
sane notification policy: notify once when a problem starts, stay silent while it
continues (no flapping/spam), and optionally notify again when it clears.
"""
from __future__ import annotations

import sqlite3
from contextlib import closing
from datetime import datetime, timezone
from pathlib import Path

from .models import Alert

_SCHEMA = """
CREATE TABLE IF NOT EXISTS open_alerts (
    dedup_key   TEXT PRIMARY KEY,
    rule        TEXT NOT NULL,
    site_id     INTEGER NOT NULL,
    title       TEXT NOT NULL,
    message     TEXT NOT NULL,
    severity    TEXT NOT NULL,
    first_seen  TEXT NOT NULL,
    last_seen   TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS kv_state (
    key   TEXT PRIMARY KEY,
    value TEXT NOT NULL
);
"""


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


class StateStore:
    """Persists "currently open" alerts so repeated checks don't re-notify."""

    def __init__(self, db_path: str | Path):
        self.db_path = str(db_path)
        with closing(self._connect()) as conn:
            conn.executescript(_SCHEMA)
            conn.commit()

    def _connect(self) -> sqlite3.Connection:
        return sqlite3.connect(self.db_path)

    def is_open(self, dedup_key: str) -> bool:
        with closing(self._connect()) as conn:
            row = conn.execute(
                "SELECT 1 FROM open_alerts WHERE dedup_key = ?", (dedup_key,)
            ).fetchone()
            return row is not None

    def mark_open(self, alert: Alert) -> bool:
        """Record `alert` as open. Returns True if it is newly opened (i.e. should notify)."""
        now = _now()
        with closing(self._connect()) as conn:
            existing = conn.execute(
                "SELECT 1 FROM open_alerts WHERE dedup_key = ?", (alert.dedup_key,)
            ).fetchone()
            if existing:
                conn.execute(
                    "UPDATE open_alerts SET last_seen = ?, message = ? WHERE dedup_key = ?",
                    (now, alert.message, alert.dedup_key),
                )
                conn.commit()
                return False

            conn.execute(
                "INSERT INTO open_alerts "
                "(dedup_key, rule, site_id, title, message, severity, first_seen, last_seen) "
                "VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                (
                    alert.dedup_key,
                    alert.rule,
                    alert.site_id,
                    alert.title,
                    alert.message,
                    alert.severity.value,
                    now,
                    now,
                ),
            )
            conn.commit()
            return True

    def get_value(self, key: str) -> str | None:
        with closing(self._connect()) as conn:
            row = conn.execute("SELECT value FROM kv_state WHERE key = ?", (key,)).fetchone()
            return row[0] if row else None

    def set_value(self, key: str, value: str) -> None:
        with closing(self._connect()) as conn:
            conn.execute(
                "INSERT INTO kv_state (key, value) VALUES (?, ?) "
                "ON CONFLICT(key) DO UPDATE SET value = excluded.value",
                (key, value),
            )
            conn.commit()

    def close_stale(self, still_open_keys: set[str], rule: str, site_id: int) -> list[dict]:
        """Close any previously-open alerts for `(rule, site_id)` not present in `still_open_keys`.

        Returns the rows that were closed (so the caller can send "resolved" notifications).
        """
        with closing(self._connect()) as conn:
            rows = conn.execute(
                "SELECT dedup_key, title, message, severity FROM open_alerts "
                "WHERE rule = ? AND site_id = ?",
                (rule, site_id),
            ).fetchall()
            closed = [dict(zip(("dedup_key", "title", "message", "severity"), row)) for row in rows]
            closed = [row for row in closed if row["dedup_key"] not in still_open_keys]
            for row in closed:
                conn.execute("DELETE FROM open_alerts WHERE dedup_key = ?", (row["dedup_key"],))
            conn.commit()
            return closed
