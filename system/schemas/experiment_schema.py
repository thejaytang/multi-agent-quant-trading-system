from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from ._validation import ValidationError, allowed_dataclass_fields, dataclass_to_dict, reject_unknown_fields, require_non_empty


@dataclass
class ExperimentSchema:
    experiment_id: str
    strategy_id: str
    data_version: str
    code_version: str
    params: dict[str, Any]
    cost_model: dict[str, Any]
    slippage_model: dict[str, Any]
    results: dict[str, Any]
    workflow_id: str
    source: str
    created_at: str
    created_by: str
    metadata: dict[str, Any] = field(default_factory=dict)

    def validate(self) -> "ExperimentSchema":
        for name in (
            "experiment_id",
            "strategy_id",
            "data_version",
            "code_version",
            "params",
            "cost_model",
            "slippage_model",
            "results",
            "workflow_id",
            "source",
            "created_at",
            "created_by",
        ):
            require_non_empty(getattr(self, name), name)
        if not isinstance(self.results, dict):
            raise ValidationError("results must be a dictionary")
        return self

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "ExperimentSchema":
        reject_unknown_fields(data, allowed_dataclass_fields(cls))
        return cls(**data).validate()

    def to_dict(self) -> dict[str, Any]:
        return dataclass_to_dict(self)
