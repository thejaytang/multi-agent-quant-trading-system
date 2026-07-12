from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from ._validation import allowed_dataclass_fields, dataclass_to_dict, reject_unknown_fields, require_non_empty


@dataclass
class StrategyPacketSchema:
    active_strategies: list[str]
    signals: list[dict[str, Any]]
    strategy_library_summary: dict[str, Any]
    backtest_refs: list[str]
    workflow_id: str
    source: str
    created_at: str
    created_by: str
    metadata: dict[str, Any] = field(default_factory=dict)

    def validate(self) -> "StrategyPacketSchema":
        for name in ("strategy_library_summary", "workflow_id", "source", "created_at", "created_by"):
            require_non_empty(getattr(self, name), name)
        return self

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "StrategyPacketSchema":
        reject_unknown_fields(data, allowed_dataclass_fields(cls))
        return cls(**data).validate()

    def to_dict(self) -> dict[str, Any]:
        return dataclass_to_dict(self)
