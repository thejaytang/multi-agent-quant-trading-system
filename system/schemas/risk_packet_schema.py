from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from ._validation import ValidationError, allowed_dataclass_fields, dataclass_to_dict, reject_unknown_fields, require_non_empty


VALID_RISK_PACKET_DECISIONS = {"PASS", "REJECT", "HALT"}


@dataclass
class RiskPacketSchema:
    risk_mode: str
    decision: str
    reason: str
    risk_gate_passed: bool
    rejection_can_be_overridden: bool
    checks: dict[str, Any]
    alerts: list[dict[str, Any]]
    stop_loss_take_profit: list[dict[str, Any]]
    workflow_id: str
    source: str
    created_at: str
    created_by: str
    metadata: dict[str, Any] = field(default_factory=dict)

    def validate(self) -> "RiskPacketSchema":
        for name in ("risk_mode", "decision", "reason", "workflow_id", "source", "created_at", "created_by"):
            require_non_empty(getattr(self, name), name)
        if self.decision not in VALID_RISK_PACKET_DECISIONS:
            raise ValidationError("invalid risk packet decision")
        if self.decision in {"REJECT", "HALT"} and self.rejection_can_be_overridden:
            raise ValidationError("RiskControlAgent rejection cannot be overridden")
        if self.decision in {"REJECT", "HALT"} and self.risk_gate_passed:
            raise ValidationError("risk_gate_passed must be false for REJECT or HALT")
        return self

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "RiskPacketSchema":
        reject_unknown_fields(data, allowed_dataclass_fields(cls))
        return cls(**data).validate()

    def to_dict(self) -> dict[str, Any]:
        return dataclass_to_dict(self)
