from __future__ import annotations

import importlib
from typing import Any


class WorkflowEngine:
    def run(self, workflow_module: str, **kwargs: Any) -> dict[str, Any]:
        module = importlib.import_module(workflow_module)
        if not hasattr(module, "run"):
            raise AttributeError(f"{workflow_module} has no run function")
        return module.run(**kwargs)
