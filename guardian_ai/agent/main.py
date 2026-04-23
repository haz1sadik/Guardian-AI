from __future__ import annotations

from pathlib import Path
from datetime import datetime, timezone
import socket
import threading
import time

from guardian_ai.common.config import load_config
from guardian_ai.common.models import Alert
from guardian_ai.agent.detection import Detector, FeatureWindow
from guardian_ai.agent.monitor import FolderMonitor
from guardian_ai.agent.backup import backup_loop, mirror_backup
from guardian_ai.agent.containment import top_io_processes, terminate_processes, apply_read_only_folder_policy
from guardian_ai.agent.integrity import build_manifest, load_manifest, hash_check, restore_changed_files
from guardian_ai.agent.alerting import send_alert

MIN_DETECTION_WINDOW_SECONDS = 2


def ensure_dirs(*paths: Path) -> None:
    for p in paths:
        p.mkdir(parents=True, exist_ok=True)


def run() -> None:
    cfg = load_config()
    protected_dir = Path(cfg.protected_dir)
    backup_dir = Path(cfg.backup_dir)
    manifest_path = Path(cfg.manifest_path)
    model_path = Path(cfg.model_path)

    ensure_dirs(protected_dir, backup_dir, manifest_path.parent, model_path.parent)

    if not manifest_path.exists():
        mirror_backup(protected_dir, backup_dir)
        build_manifest(protected_dir, manifest_path)

    detector = Detector(model_path=model_path, threshold=cfg.anomaly_threshold)
    window = FeatureWindow()
    monitor = FolderMonitor(protected_dir, window)

    stop_flag = {"stop": False}
    backup_thread = threading.Thread(
        target=backup_loop,
        args=(protected_dir, backup_dir, cfg.backup_interval_seconds, stop_flag),
        daemon=True,
    )

    backup_thread.start()
    monitor.start()

    try:
        while True:
            touched = monitor.drain()
            elapsed = time.time() - window.start
            if elapsed >= max(MIN_DETECTION_WINDOW_SECONDS, cfg.detection_window_seconds):
                x = window.vector()
                is_anomaly, score = detector.is_anomaly(x)
                if is_anomaly and touched:
                    detect_started = time.perf_counter()
                    suspects = top_io_processes(limit=cfg.max_kill_candidates)
                    killed = terminate_processes(suspects)
                    apply_read_only_folder_policy(protected_dir)

                    baseline = load_manifest(manifest_path)
                    changed = hash_check(protected_dir, baseline)
                    restored = restore_changed_files(changed, protected_dir, backup_dir)
                    mtcr = time.perf_counter() - detect_started

                    alert = Alert(
                        host=socket.gethostname(),
                        timestamp_utc=datetime.now(timezone.utc).isoformat(),
                        severity="critical",
                        reason="Anomalous file-behavior burst detected; containment + restore executed",
                        anomaly_score=score,
                        suspicious_pids=killed,
                        changed_files=restored if restored else changed,
                        mtcr_seconds=round(mtcr, 3),
                        details={
                            "protected_dir": str(protected_dir),
                            "restored_count": str(len(restored)),
                            "changed_count": str(len(changed)),
                        },
                    )
                    send_alert(cfg.dashboard_url, alert)
                    build_manifest(protected_dir, manifest_path)
                window.reset()
            time.sleep(0.5)
    finally:
        stop_flag["stop"] = True
        monitor.stop()


if __name__ == "__main__":
    run()
