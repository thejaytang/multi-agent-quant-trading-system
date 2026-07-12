from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from system.schemas._validation import default_metadata


@dataclass
class BaseAgent:
    name: str
    role: str
    skills: list[str]
    can_write_workspace: bool = True
    can_write_persistent: bool = False
    can_execute_live_trade: bool = False
    permissions: dict[str, Any] = field(default_factory=dict)

    def metadata(self, workflow_id: str, source: str | None = None) -> dict[str, Any]:
        return default_metadata(workflow_id, source or self.name, self.name)

    def run(self, context: dict[str, Any] | None = None) -> dict[str, Any]:
        context = context or {}
        workflow_id = context.get("workflow_id", "manual")
        return {
            "agent": self.name,
            "role": self.role,
            "status": "stub",
            "output": {},
            "metadata": self.metadata(workflow_id),
        }
