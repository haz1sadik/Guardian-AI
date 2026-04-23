from __future__ import annotations

from guardian_ai.common.models import Alert
import requests


def send_alert(dashboard_url: str, alert: Alert) -> None:
    try:
        requests.post(f"{dashboard_url.rstrip('/')}/api/alerts", json=alert.model_dump(), timeout=4)
    except Exception:
        pass
