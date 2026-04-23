from __future__ import annotations

from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from guardian_ai.common.models import Alert
import sqlite3
from pathlib import Path

DB_PATH = Path("data/guardian_dashboard.db")
DB_PATH.parent.mkdir(parents=True, exist_ok=True)

def _db() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH, timeout=10)
    conn.row_factory = sqlite3.Row
    return conn


def _init_db() -> None:
    with _db() as conn:
        conn.execute("PRAGMA journal_mode=WAL;")
        conn.execute("PRAGMA synchronous=NORMAL;")
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS alerts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                host TEXT NOT NULL,
                timestamp_utc TEXT NOT NULL,
                severity TEXT NOT NULL,
                reason TEXT NOT NULL,
                anomaly_score REAL NOT NULL,
                suspicious_pids TEXT NOT NULL,
                changed_files TEXT NOT NULL,
                mtcr_seconds REAL,
                details TEXT NOT NULL
            )
            """
        )


@asynccontextmanager
async def lifespan(_: FastAPI):
    _init_db()
    yield


app = FastAPI(title="Guardian-AI Dashboard", lifespan=lifespan)


@app.get("/health")
def health() -> dict:
    return {"ok": True}


@app.post("/api/alerts")
def create_alert(alert: Alert) -> dict:
    with _db() as conn:
        conn.execute(
            """
            INSERT INTO alerts (host, timestamp_utc, severity, reason, anomaly_score, suspicious_pids, changed_files, mtcr_seconds, details)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                alert.host,
                alert.timestamp_utc,
                alert.severity,
                alert.reason,
                alert.anomaly_score,
                ",".join(str(x) for x in alert.suspicious_pids),
                "\n".join(alert.changed_files),
                alert.mtcr_seconds,
                str(alert.details),
            ),
        )
    return {"stored": True}


@app.get("/api/alerts")
def list_alerts(limit: int = 100) -> list[dict]:
    with _db() as conn:
        rows = conn.execute(
            "SELECT * FROM alerts ORDER BY id DESC LIMIT ?", (max(1, min(limit, 500)),)
        ).fetchall()
    return [dict(row) for row in rows]


@app.get("/", response_class=HTMLResponse)
def index() -> str:
    return """
<!doctype html>
<html>
<head>
  <meta charset='utf-8' />
  <title>Guardian-AI Alerts</title>
  <style>
    body { font-family: Arial, sans-serif; margin: 20px; background: #f3f6fb; }
    h1 { margin-bottom: 8px; }
    .card { background: white; border-radius: 8px; padding: 12px; margin-bottom: 10px; border-left: 6px solid #d33; }
    .meta { color: #444; font-size: 12px; margin-bottom: 6px; }
    code { background: #eee; padding: 2px 4px; }
  </style>
</head>
<body>
  <h1>Guardian-AI Admin Dashboard</h1>
  <p>Live ransomware alerts from LAN agents.</p>
  <div id='alerts'></div>
<script>
async function loadAlerts() {
  const res = await fetch('/api/alerts?limit=50');
  const data = await res.json();
  const root = document.getElementById('alerts');
  root.innerHTML = data.map(a => `
    <div class='card'>
      <div class='meta'><b>${a.timestamp_utc}</b> | host: <code>${a.host}</code> | severity: <b>${a.severity}</b></div>
      <div><b>${a.reason}</b> (score=${a.anomaly_score})</div>
      <div>Suspicious PIDs: <code>${a.suspicious_pids}</code></div>
      <div>Changed files:<pre>${a.changed_files || ''}</pre></div>
      <div>MTCR: <b>${a.mtcr_seconds ?? 'n/a'}</b></div>
    </div>
  `).join('');
}
loadAlerts();
setInterval(loadAlerts, 2000);
</script>
</body>
</html>
"""
