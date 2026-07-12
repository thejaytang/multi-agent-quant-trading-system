import pytest

from system.schemas._validation import ValidationError
from system.schemas.order_schema import OrderSchema


def test_live_order_requires_risk_and_human_approval():
    with pytest.raises(ValidationError):
        OrderSchema.from_dict({
            "strategy_id": "s1",
            "mode": "live",
            "orders": [{"symbol": "SPY", "action": "BUY", "quantity": 1, "order_type": "market"}],
            "risk_approved": False,
            "human_approved": True,
            "workflow_id": "wf",
            "source": "test",
            "created_at": "2026-06-03T00:00:00+00:00",
            "created_by": "BrokerExecutionAgent",
            "metadata": {},
        })
