from __future__ import annotations

from pydantic import BaseModel


class Alert(BaseModel):
    host: str
    timestamp_utc: str
    severity: str
    reason: str
    anomaly_score: float
    suspicious_pids: list[int]
    changed_files: list[str]
    mtcr_seconds: float | None = None
    details: dict[str, str] = {}
