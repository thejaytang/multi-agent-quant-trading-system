from __future__ import annotations

import importlib
from types import ModuleType


class SkillLoader:
    def load(self, dotted_path: str) -> ModuleType:
        return importlib.import_module(dotted_path)

    def run(self, dotted_path: str, input_data: dict | None = None) -> dict:
        module = self.load(dotted_path)
        if not hasattr(module, "run"):
            raise AttributeError(f"{dotted_path} has no run function")
        return module.run(input_data or {})
