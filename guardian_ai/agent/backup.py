from __future__ import annotations

from pathlib import Path
import shutil
import subprocess
import time

MIN_BACKUP_INTERVAL_SECONDS = 30


def mirror_backup(protected_dir: Path, backup_dir: Path) -> None:
    stage_dir = backup_dir.parent / f"{backup_dir.name}.stage"
    old_dir = backup_dir.parent / f"{backup_dir.name}.old"

    if stage_dir.exists():
        shutil.rmtree(stage_dir, ignore_errors=True)
    stage_dir.mkdir(parents=True, exist_ok=True)

    for src in protected_dir.rglob("*"):
        if src.is_file():
            rel = src.relative_to(protected_dir)
            dst = stage_dir / rel
            dst.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(src, dst)

    if old_dir.exists():
        shutil.rmtree(old_dir, ignore_errors=True)
    if backup_dir.exists():
        backup_dir.rename(old_dir)
    stage_dir.rename(backup_dir)
    if old_dir.exists():
        shutil.rmtree(old_dir, ignore_errors=True)


def try_create_vss_snapshot(volume: str = "C:") -> str:
    cmd = [
        "powershell",
        "-NoProfile",
        "-Command",
        f"vssadmin create shadow /for={volume}",
    ]
    try:
        out = subprocess.check_output(cmd, stderr=subprocess.STDOUT, text=True, timeout=45)
        return out
    except Exception as exc:
        return f"VSS snapshot attempt failed: {exc}"


def backup_loop(protected_dir: Path, backup_dir: Path, interval_seconds: int, stop_flag: dict[str, bool]) -> None:
    while not stop_flag.get("stop", False):
        mirror_backup(protected_dir, backup_dir)
        try_create_vss_snapshot("C:")
        # Enforce a floor to avoid aggressive copy/snapshot churn on low intervals.
        sleep_left = max(MIN_BACKUP_INTERVAL_SECONDS, interval_seconds)
        while sleep_left > 0 and not stop_flag.get("stop", False):
            chunk = min(1.0, sleep_left)
            time.sleep(chunk)
            sleep_left -= chunk
