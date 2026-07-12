from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from ._validation import ValidationError, allowed_dataclass_fields, dataclass_to_dict, reject_unknown_fields, require_non_empty


ALLOWED_ASSET_TYPES = {
    "strategy",
    "experiment",
    "report",
    "decision",
    "capital_update",
    "portfolio_update",
    "ledger_update",
    "knowledge_note",
    "archive",
}


@dataclass
class PromotionCandidateSchema:
    candidate_id: str
    asset_type: str
    source_workspace_path: str
    target_persistent_path: str
    created_by_agent: str
    workflow_id: str
    created_at: str
    metadata: dict[str, Any]
    leader_review_required: bool = True
    risk_review_required: bool = False
    status: str = "created"
    review_notes: list[str] = field(default_factory=list)

    def validate(self) -> "PromotionCandidateSchema":
        for name in (
            "candidate_id",
            "asset_type",
            "source_workspace_path",
            "target_persistent_path",
            "created_by_agent",
            "workflow_id",
            "created_at",
            "metadata",
        ):
            require_non_empty(getattr(self, name), name)
        if self.asset_type not in ALLOWED_ASSET_TYPES:
            raise ValidationError(f"invalid asset_type: {self.asset_type}")
        if not self.leader_review_required:
            raise ValidationError("leader_review_required must be true")
        return self

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "PromotionCandidateSchema":
        reject_unknown_fields(data, allowed_dataclass_fields(cls))
        return cls(**data).validate()

    def to_dict(self) -> dict[str, Any]:
        return dataclass_to_dict(self)
