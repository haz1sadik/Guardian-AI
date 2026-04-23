from __future__ import annotations

from pathlib import Path
from pydantic import BaseModel, Field
import json


DEFAULT_CONFIG_PATH = Path(r"C:\ProgramData\GuardianAI\config.json")


class AgentConfig(BaseModel):
    dashboard_url: str = Field(default="http://127.0.0.1:8000")
    protected_dir: str = Field(default=r"C:\GuardianAI_Demo\protected")
    backup_dir: str = Field(default=r"C:\GuardianAI_Demo\backups\latest")
    model_path: str = Field(default=r"C:\ProgramData\GuardianAI\model\isolation_forest.joblib")
    manifest_path: str = Field(default=r"C:\ProgramData\GuardianAI\manifest\baseline_hashes.json")
    backup_interval_seconds: int = 300
    detection_window_seconds: int = 5
    anomaly_threshold: float = -0.15
    max_kill_candidates: int = 3


def load_config(path: Path = DEFAULT_CONFIG_PATH) -> AgentConfig:
    if not path.exists():
        path.parent.mkdir(parents=True, exist_ok=True)
        cfg = AgentConfig()
        path.write_text(cfg.model_dump_json(indent=2), encoding="utf-8")
        return cfg
    data = json.loads(path.read_text(encoding="utf-8"))
    return AgentConfig(**data)
