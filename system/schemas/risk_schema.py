from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from ._validation import ValidationError, allowed_dataclass_fields, dataclass_to_dict, reject_unknown_fields, require_non_empty


VALID_RISK_DECISIONS = {"PASS", "REJECT", "HALT"}


@dataclass
class RiskDecisionSchema:
    decision_id: str
    decision: str
    reason: str
    workflow_id: str
    source: str
    created_at: str
    created_by: str
    rejection_can_be_overridden: bool = False
    checks: dict[str, Any] = field(default_factory=dict)
    metadata: dict[str, Any] = field(default_factory=dict)

    def validate(self) -> "RiskDecisionSchema":
        for name in ("decision_id", "decision", "reason", "workflow_id", "source", "created_at", "created_by"):
            require_non_empty(getattr(self, name), name)
        if self.decision not in VALID_RISK_DECISIONS:
            raise ValidationError("invalid risk decision")
        if self.decision in {"REJECT", "HALT"} and self.rejection_can_be_overridden:
            raise ValidationError("RiskControlAgent rejection cannot be overridden")
        return self

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "RiskDecisionSchema":
        reject_unknown_fields(data, allowed_dataclass_fields(cls))
        return cls(**data).validate()

    def to_dict(self) -> dict[str, Any]:
        return dataclass_to_dict(self)
