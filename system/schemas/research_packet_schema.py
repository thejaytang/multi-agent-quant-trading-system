from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from ._validation import ValidationError, allowed_dataclass_fields, dataclass_to_dict, reject_unknown_fields, require_non_empty


@dataclass
class ResearchPacketSchema:
    market_lens: dict[str, Any]
    thesis_impacts: list[dict[str, Any]]
    catalysts: list[dict[str, Any]]
    risks: list[dict[str, Any]]
    confidence: float
    workflow_id: str
    source: str
    created_at: str
    created_by: str
    metadata: dict[str, Any] = field(default_factory=dict)

    def validate(self) -> "ResearchPacketSchema":
        for name in ("market_lens", "workflow_id", "source", "created_at", "created_by"):
            require_non_empty(getattr(self, name), name)
        for lens_name in ("news", "fundamentals", "technicals"):
            if lens_name not in self.market_lens:
                raise ValidationError(f"market_lens.{lens_name} is required")
        if not 0 <= self.confidence <= 1:
            raise ValidationError("confidence must be between 0 and 1")
        return self

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "ResearchPacketSchema":
        reject_unknown_fields(data, allowed_dataclass_fields(cls))
        return cls(**data).validate()

    def to_dict(self) -> dict[str, Any]:
        return dataclass_to_dict(self)
