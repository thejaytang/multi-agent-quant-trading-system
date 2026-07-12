from __future__ import annotations

from system.agents.base_agent import BaseAgent


class RiskControlAgent(BaseAgent):
    def __init__(self) -> None:
        super().__init__(
            name="RiskControlAgent",
            role="Highest-priority risk, approval, audit, and kill-switch authority",
            skills=['pre_trade_risk_check', 'capital_risk_check', 'position_limit_check', 'drawdown_control', 'paper_to_live_gate', 'approval_gate_check', 'api_key_leakage_check', 'broker_mode_safety_check', 'kill_switch'],
            can_write_workspace=True,
            can_write_persistent=False,
            can_execute_live_trade=False,
        )


    def reject(self, workflow_id: str, reason: str) -> dict:
        return {
            "agent": self.name,
            "decision": "REJECT",
            "reason": reason,
            "rejection_can_be_overridden": False,
            "metadata": self.metadata(workflow_id),
        }

