from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from ._validation import ValidationError, allowed_dataclass_fields, dataclass_to_dict, reject_unknown_fields, require_non_empty


@dataclass
class ReportSchema:
    report_id: str
    report_type: str
    title: str
    body: str
    supporting_data: list[str]
    workflow_id: str
    source: str
    created_at: str
    created_by: str
    metadata: dict[str, Any] = field(default_factory=dict)

    def validate(self) -> "ReportSchema":
        for name in ("report_id", "report_type", "title", "body", "workflow_id", "source", "created_at", "created_by"):
            require_non_empty(getattr(self, name), name)
        return self

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "ReportSchema":
        reject_unknown_fields(data, allowed_dataclass_fields(cls))
        return cls(**data).validate()

    def to_dict(self) -> dict[str, Any]:
        return dataclass_to_dict(self)
