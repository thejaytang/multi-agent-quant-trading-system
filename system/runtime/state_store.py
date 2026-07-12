from __future__ import annotations

import json
from pathlib import Path
from typing import Any


class StateStore:
    def __init__(self, root: str | Path | None = None) -> None:
        self.root = Path(root or Path.cwd())

    def read_json(self, relative_path: str | Path, default: Any = None) -> Any:
        path = self.root / relative_path
        if not path.exists():
            return default
        return json.loads(path.read_text(encoding="utf-8"))

    def write_json(self, relative_path: str | Path, payload: Any) -> Path:
        path = self.root / relative_path
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
        return path
