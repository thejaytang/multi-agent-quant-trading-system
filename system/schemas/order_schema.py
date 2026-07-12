from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from ._validation import ValidationError, allowed_dataclass_fields, dataclass_to_dict, reject_unknown_fields, require_non_empty


VALID_ACTIONS = {"BUY", "SELL", "HOLD"}
VALID_MODES = {"paper", "live"}


@dataclass
class OrderItem:
    symbol: str
    action: str
    quantity: float
    order_type: str

    def validate(self) -> "OrderItem":
        for name in ("symbol", "action", "order_type"):
            require_non_empty(getattr(self, name), name)
        if self.action not in VALID_ACTIONS:
            raise ValidationError(f"invalid order action: {self.action}")
        if self.quantity < 0:
            raise ValidationError("quantity cannot be negative")
        return self

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "OrderItem":
        if "natural_language_instruction" in data:
            raise ValidationError("natural language orders are not accepted")
        reject_unknown_fields(data, allowed_dataclass_fields(cls))
        return cls(**data).validate()


@dataclass
class OrderSchema:
    strategy_id: str
    mode: str
    orders: list[OrderItem]
    risk_approved: bool
    human_approved: bool
    workflow_id: str
    source: str
    created_at: str
    created_by: str
    metadata: dict[str, Any] = field(default_factory=dict)

    def validate(self) -> "OrderSchema":
        for name in ("strategy_id", "mode", "orders", "workflow_id", "source", "created_at", "created_by"):
            require_non_empty(getattr(self, name), name)
        if self.mode not in VALID_MODES:
            raise ValidationError("mode must be paper or live")
        if self.mode == "live" and not self.risk_approved:
            raise ValidationError("live order requires risk_approved=true")
        if self.mode == "live" and not self.human_approved:
            raise ValidationError("live order requires human_approved=true")
        self.orders = [order if isinstance(order, OrderItem) else OrderItem.from_dict(order) for order in self.orders]
        for order in self.orders:
            order.validate()
        return self

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "OrderSchema":
        if "natural_language_instruction" in data:
            raise ValidationError("natural language orders are not accepted")
        reject_unknown_fields(data, allowed_dataclass_fields(cls))
        converted = dict(data)
        converted["orders"] = [OrderItem.from_dict(item) if isinstance(item, dict) else item for item in converted.get("orders", [])]
        return cls(**converted).validate()

    def to_dict(self) -> dict[str, Any]:
        return dataclass_to_dict(self)
