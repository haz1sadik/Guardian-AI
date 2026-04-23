from __future__ import annotations

from pathlib import Path
import shutil
import subprocess
import time


def mirror_backup(protected_dir: Path, backup_dir: Path) -> None:
    backup_dir.mkdir(parents=True, exist_ok=True)
    if backup_dir.exists():
        for p in list(backup_dir.rglob("*")):
            if p.is_file():
                p.unlink()
    for src in protected_dir.rglob("*"):
        if src.is_file():
            rel = src.relative_to(protected_dir)
            dst = backup_dir / rel
            dst.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(src, dst)


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
        time.sleep(max(30, interval_seconds))
