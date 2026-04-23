from pathlib import Path
from guardian_ai.agent.integrity import build_manifest, load_manifest, hash_check


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
    assert "sample.txt" in changed
