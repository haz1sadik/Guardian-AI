from pathlib import Path
from guardian_ai.agent.integrity import build_manifest, load_manifest, hash_check, restore_changed_files


def test_manifest_and_hash_check(tmp_path: Path):
    protected = tmp_path / "protected"
    protected.mkdir()
    f = protected / "sample.txt"
    f.write_text("hello", encoding="utf-8")

    manifest_path = tmp_path / "manifest.json"
    build_manifest(protected, manifest_path)
    m = load_manifest(manifest_path)
    assert hash_check(protected, m) == []

    f.write_text("tampered", encoding="utf-8")
    changed = hash_check(protected, m)
    assert any(c == "sample.txt" for c in changed)


def test_restore_changed_files(tmp_path: Path):
    protected = tmp_path / "protected"
    backup = tmp_path / "backup"
    protected.mkdir()
    backup.mkdir()

    rel = "a.txt"
    (protected / rel).write_text("bad", encoding="utf-8")
    (backup / rel).write_text("good", encoding="utf-8")

    restored = restore_changed_files([rel], protected, backup)
    assert restored == [rel]
    assert (protected / rel).read_text(encoding="utf-8") == "good"
