from system.schemas.order_schema import OrderSchema


def test_order_schema_accepts_paper_order():
    order = OrderSchema.from_dict({
        "strategy_id": "s1",
        "mode": "paper",
        "orders": [{"symbol": "SPY", "action": "HOLD", "quantity": 0, "order_type": "market"}],
        "risk_approved": False,
        "human_approved": False,
        "workflow_id": "wf",
        "source": "test",
        "created_at": "2026-06-03T00:00:00+00:00",
        "created_by": "BrokerExecutionAgent",
        "metadata": {},
    })
    assert order.mode == "paper"
