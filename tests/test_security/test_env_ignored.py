from pathlib import Path


def test_env_ignored():
    text = Path(".gitignore").read_text(encoding="utf-8")
    assert ".env" in text
    assert ".env.*" in text
