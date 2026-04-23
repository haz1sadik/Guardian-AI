from __future__ import annotations

from pathlib import Path
import hashlib
import json
import shutil


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def build_manifest(protected_dir: Path, manifest_path: Path) -> dict[str, str]:
    manifest: dict[str, str] = {}
    for p in protected_dir.rglob("*"):
        if p.is_file():
            rel = str(p.relative_to(protected_dir))
            manifest[rel] = sha256_file(p)
    manifest_path.parent.mkdir(parents=True, exist_ok=True)
    manifest_path.write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    return manifest


def load_manifest(manifest_path: Path) -> dict[str, str]:
    if not manifest_path.exists():
        return {}
    return json.loads(manifest_path.read_text(encoding="utf-8"))


def hash_check(protected_dir: Path, manifest: dict[str, str]) -> list[str]:
    changed: list[str] = []
    for rel, old_hash in manifest.items():
        p = protected_dir / rel
        if not p.exists() or not p.is_file():
            changed.append(rel)
            continue
        if sha256_file(p) != old_hash:
            changed.append(rel)
    return changed


def restore_changed_files(changed_files: list[str], protected_dir: Path, backup_dir: Path) -> list[str]:
    restored: list[str] = []
    for rel in changed_files:
        src = backup_dir / rel
        dst = protected_dir / rel
        if src.exists() and src.is_file():
            dst.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(src, dst)
            restored.append(rel)
    return restored
