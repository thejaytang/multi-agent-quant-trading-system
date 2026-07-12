from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from ._validation import ValidationError, allowed_dataclass_fields, dataclass_to_dict, reject_unknown_fields, require_non_empty


@dataclass
class CapitalSnapshotSchema:
    snapshot_id: str
    total_net_worth: float
    base_currency: str
    buckets: dict[str, float]
    accounts: list[dict[str, Any]]
    workflow_id: str
    source: str
    created_at: str
    created_by: str
    metadata: dict[str, Any] = field(default_factory=dict)

    def validate(self) -> "CapitalSnapshotSchema":
        for name in ("snapshot_id", "base_currency", "buckets", "workflow_id", "source", "created_at", "created_by"):
            require_non_empty(getattr(self, name), name)
        if self.total_net_worth < 0:
            raise ValidationError("total_net_worth cannot be negative")
        return self

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "CapitalSnapshotSchema":
        reject_unknown_fields(data, allowed_dataclass_fields(cls))
        return cls(**data).validate()

    def to_dict(self) -> dict[str, Any]:
        return dataclass_to_dict(self)
