import pytest

from system.schemas._validation import ValidationError
from system.schemas.order_schema import OrderSchema


def test_no_natural_language_orders():
    with pytest.raises(ValidationError):
        OrderSchema.from_dict({
            "strategy_id": "s1",
            "mode": "paper",
            "natural_language_instruction": "buy SPY now",
            "orders": [],
            "risk_approved": False,
            "human_approved": False,
            "workflow_id": "wf",
            "source": "test",
            "created_at": "2026-06-03T00:00:00+00:00",
            "created_by": "BrokerExecutionAgent",
            "metadata": {},
        })
