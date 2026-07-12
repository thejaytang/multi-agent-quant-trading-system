import re
from pathlib import Path

SECRET_PATTERN = re.compile(r"(?i)(api[_-]?key|secret|token)[ \t]*[:=][ \t]*['\"]?[A-Za-z0-9_\-]{16,}")


def test_api_keys_not_committed():
    for path in Path(".").rglob("*"):
        if not path.is_file():
            continue
        if path.name in {".env", ".env.local"}:
            continue
        if any(part in {".git", "__pycache__", ".pytest_cache"} for part in path.parts):
            continue
        if path.suffix in {".rtf", ".pyc", ".png", ".jpg", ".jpeg"}:
            continue
        text = path.read_text(encoding="utf-8", errors="ignore")
        assert not SECRET_PATTERN.search(text), str(path)
