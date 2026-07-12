from __future__ import annotations

from system.agents.base_agent import BaseAgent


class BrokerExecutionAgent(BaseAgent):
    def __init__(self) -> None:
        super().__init__(
            name="BrokerExecutionAgent",
            role="IBKR read-only and approved structured order execution stubs",
            skills=['ibkr_account_snapshot', 'position_reading', 'cash_reading', 'order_status_reading', 'paper_order_execution', 'approved_live_order_execution', 'fill_monitoring', 'execution_report_generation'],
            can_write_workspace=True,
            can_write_persistent=False,
            can_execute_live_trade=False,
        )


    def submit_order(self, payload: dict) -> dict:
        from system.schemas.order_schema import OrderSchema
        order = OrderSchema.from_dict(payload)
        return {
            "agent": self.name,
            "status": "accepted_stub",
            "mode": order.mode,
            "metadata": self.metadata(order.workflow_id),
        }

