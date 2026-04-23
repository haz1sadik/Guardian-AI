from __future__ import annotations

import subprocess
import psutil
from pathlib import Path


def top_io_processes(limit: int = 3) -> list[psutil.Process]:
    scored: list[tuple[int, psutil.Process]] = []
    for p in psutil.process_iter(["pid", "name"]):
        try:
            io = p.io_counters()
            scored.append((io.write_bytes, p))
        except Exception:
            continue
    scored.sort(key=lambda x: x[0], reverse=True)
    return [p for _, p in scored[:limit]]


def terminate_processes(processes: list[psutil.Process]) -> list[int]:
    killed: list[int] = []
    for p in processes:
        try:
            p.terminate()
            killed.append(p.pid)
        except Exception:
            continue
    return killed


def block_program_network(exe_path: Path) -> None:
    cmd = [
        "netsh",
        "advfirewall",
        "firewall",
        "add",
        "rule",
        f"name=GuardianAI_Block_{exe_path.name}",
        "dir=out",
        "action=block",
        f"program={str(exe_path)}",
        "enable=yes",
    ]
    try:
        subprocess.run(cmd, check=False, capture_output=True, text=True)
    except Exception:
        pass


def apply_read_only_folder_policy(folder: Path) -> None:
    cmd = [
        "icacls",
        str(folder),
        "/inheritance:r",
        "/grant:r",
        "Administrators:(OI)(CI)F",
        "/grant:r",
        "Users:(OI)(CI)R",
        "/T",
        "/C",
    ]
    try:
        subprocess.run(cmd, check=False, capture_output=True, text=True)
    except Exception:
        pass
