from __future__ import annotations

from typing import Any

from system.agents.base_agent import BaseAgent
from system.agents.broker_execution_agent import BrokerExecutionAgent
from system.agents.data_agent import DataAgent
from system.agents.portfolio_capital_agent import PortfolioCapitalAgent
from system.agents.quant_engineering_agent import QuantEngineeringAgent
from system.agents.quantconnect_agent import QuantConnectAgent
from system.agents.reporting_agent import ReportingAgent
from system.agents.research_agent import ResearchAgent
from system.agents.risk_control_agent import RiskControlAgent
from system.agents.strategy_agent import StrategyAgent


CORE_SUBAGENT_TYPES = (
    DataAgent,
    ResearchAgent,
    StrategyAgent,
    QuantEngineeringAgent,
    QuantConnectAgent,
    PortfolioCapitalAgent,
    RiskControlAgent,
    BrokerExecutionAgent,
    ReportingAgent,
)


class LeaderAgent(BaseAgent):
    def __init__(self) -> None:
        super().__init__(
            name="LeaderAgent",
            role="System orchestration and promotion authority",
            skills=['workflow_control', 'subagent_assignment', 'promotion_review'],
            can_write_workspace=True,
            can_write_persistent=True,
            can_execute_live_trade=False,
        )

    def can_promote_to_persistent(self) -> bool:
        return True

    def subagents(self) -> list[BaseAgent]:
        return [agent_type() for agent_type in CORE_SUBAGENT_TYPES]

    def delegation_plan(self, task: str) -> list[dict[str, Any]]:
        return [
            {
                "agent": agent.name,
                "role": agent.role,
                "skills": agent.skills,
                "task": task,
                "assigned_by": self.name,
            }
            for agent in self.subagents()
        ]

    def run(self, context: dict[str, Any] | None = None) -> dict[str, Any]:
        context = context or {}
        workflow_id = context.get("workflow_id", "manual")
        task = context.get("task", "manual session")
        subagent_context = {**context, "assigned_by": self.name, "leader_task": task}
        subagent_outputs = [agent.run(subagent_context) for agent in self.subagents()]

        return {
            "agent": self.name,
            "role": self.role,
            "status": "delegated_stub",
            "delegation_mode": "full_team",
            "delegation_plan": self.delegation_plan(task),
            "subagent_outputs": subagent_outputs,
            "metadata": self.metadata(workflow_id),
        }
