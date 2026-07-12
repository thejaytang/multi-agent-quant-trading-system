import pytest

from system.schemas._validation import ValidationError
from system.schemas.order_schema import OrderSchema


def test_order_schema_validates_required_fields():
    with pytest.raises(ValidationError):
        OrderSchema.from_dict({
            "strategy_id": "",
            "mode": "paper",
            "orders": [{"symbol": "SPY", "action": "BUY", "quantity": 1, "order_type": "market"}],
            "risk_approved": False,
            "human_approved": False,
            "workflow_id": "wf",
            "source": "test",
            "created_at": "2026-06-03T00:00:00+00:00",
            "created_by": "BrokerExecutionAgent",
            "metadata": {},
        })
