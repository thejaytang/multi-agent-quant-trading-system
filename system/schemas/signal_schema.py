from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from ._validation import ValidationError, allowed_dataclass_fields, dataclass_to_dict, reject_unknown_fields, require_non_empty


@dataclass
class SignalSchema:
    strategy_id: str
    signals: list[dict[str, Any]]
    risk_flags: list[str]
    confidence: float
    workflow_id: str
    source: str
    created_at: str
    created_by: str
    metadata: dict[str, Any] = field(default_factory=dict)

    def validate(self) -> "SignalSchema":
        for name in ("strategy_id", "signals", "workflow_id", "source", "created_at", "created_by"):
            require_non_empty(getattr(self, name), name)
        if not 0 <= self.confidence <= 1:
            raise ValidationError("confidence must be between 0 and 1")
        for item in self.signals:
            for required in ("symbol", "signal", "timeframe"):
                require_non_empty(item.get(required), f"signals.{required}")
        return self

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "SignalSchema":
        reject_unknown_fields(data, allowed_dataclass_fields(cls))
        return cls(**data).validate()

    def to_dict(self) -> dict[str, Any]:
        return dataclass_to_dict(self)
