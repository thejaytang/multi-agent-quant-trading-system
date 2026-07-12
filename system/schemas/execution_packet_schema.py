from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from ._validation import ValidationError, allowed_dataclass_fields, dataclass_to_dict, reject_unknown_fields, require_non_empty


VALID_EXECUTION_MODES = {"paper", "live", "disabled"}


@dataclass
class ExecutionPacketSchema:
    mode: str
    pending_actions: list[dict[str, Any]]
    rejected_actions: list[dict[str, Any]]
    confirmed_actions: list[dict[str, Any]]
    order_status: list[dict[str, Any]]
    human_confirmation_required: bool
    workflow_id: str
    source: str
    created_at: str
    created_by: str
    metadata: dict[str, Any] = field(default_factory=dict)

    def validate(self) -> "ExecutionPacketSchema":
        for name in ("mode", "workflow_id", "source", "created_at", "created_by"):
            require_non_empty(getattr(self, name), name)
        if self.mode not in VALID_EXECUTION_MODES:
            raise ValidationError("execution mode must be paper, live, or disabled")
        if self.mode == "live" and self.pending_actions:
            raise ValidationError("live pending actions are not allowed in this first-phase workflow")
        return self

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "ExecutionPacketSchema":
        reject_unknown_fields(data, allowed_dataclass_fields(cls))
        return cls(**data).validate()

    def to_dict(self) -> dict[str, Any]:
        return dataclass_to_dict(self)
