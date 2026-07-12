from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from ._validation import ValidationError, allowed_dataclass_fields, dataclass_to_dict, reject_unknown_fields, require_non_empty


VALID_COCKPIT_STATUSES = {"ready", "partial", "blocked"}


@dataclass
class CockpitSnapshotSchema:
    snapshot_id: str
    status: str
    top_metrics: dict[str, Any]
    market_lens: dict[str, Any]
    strategy_center: dict[str, Any]
    portfolio_risk: dict[str, Any]
    execution_desk: dict[str, Any]
    performance_journal: dict[str, Any]
    agent_trace: dict[str, Any]
    workflow_id: str
    source: str
    created_at: str
    created_by: str
    metadata: dict[str, Any] = field(default_factory=dict)

    def validate(self) -> "CockpitSnapshotSchema":
        for name in (
            "snapshot_id",
            "status",
            "top_metrics",
            "market_lens",
            "strategy_center",
            "portfolio_risk",
            "execution_desk",
            "performance_journal",
            "agent_trace",
            "workflow_id",
            "source",
            "created_at",
            "created_by",
        ):
            require_non_empty(getattr(self, name), name)
        if self.status not in VALID_COCKPIT_STATUSES:
            raise ValidationError("cockpit snapshot status must be ready, partial, or blocked")
        if "risk_mode" not in self.top_metrics:
            raise ValidationError("top_metrics.risk_mode is required")
        return self

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "CockpitSnapshotSchema":
        reject_unknown_fields(data, allowed_dataclass_fields(cls))
        return cls(**data).validate()

    def to_dict(self) -> dict[str, Any]:
        return dataclass_to_dict(self)
