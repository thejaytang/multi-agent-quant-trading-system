from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from ._validation import ValidationError, allowed_dataclass_fields, dataclass_to_dict, reject_unknown_fields, require_non_empty


VALID_STRATEGY_STATUSES = {
    "idea",
    "ingested",
    "standardized",
    "adapted",
    "backtest_ready",
    "backtested",
    "paper_trading",
    "paper_validated",
    "live_candidate",
    "live_enabled",
    "retired",
}


@dataclass
class StrategySchema:
    strategy_id: str
    name: str
    version: str
    source_type: str
    status: str
    asset_class: str
    market: str
    timeframe: str
    data_requirements: list[str]
    risk_level: str
    quantconnect_compatible: bool
    implementation_path: str
    live_enabled: bool
    changelog: list[str]
    workflow_id: str
    source: str
    created_at: str
    created_by: str
    metadata: dict[str, Any] = field(default_factory=dict)

    def validate(self) -> "StrategySchema":
        for name in (
            "strategy_id",
            "name",
            "version",
            "source_type",
            "status",
            "asset_class",
            "market",
            "timeframe",
            "data_requirements",
            "risk_level",
            "implementation_path",
            "workflow_id",
            "source",
            "created_at",
            "created_by",
        ):
            require_non_empty(getattr(self, name), name)
        if self.status not in VALID_STRATEGY_STATUSES:
            raise ValidationError(f"invalid strategy status: {self.status}")
        if self.live_enabled and self.status != "live_enabled":
            raise ValidationError("live_enabled requires status live_enabled")
        return self

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "StrategySchema":
        reject_unknown_fields(data, allowed_dataclass_fields(cls))
        return cls(**data).validate()

    def to_dict(self) -> dict[str, Any]:
        return dataclass_to_dict(self)
