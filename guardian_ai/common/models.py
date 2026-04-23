from __future__ import annotations

from pydantic import BaseModel
from typing import Dict, List


class Alert(BaseModel):
    host: str
    timestamp_utc: str
    severity: str
    reason: str
    anomaly_score: float
    suspicious_pids: List[int]
    changed_files: List[str]
    mtcr_seconds: float | None = None
    details: Dict[str, str] = {}
