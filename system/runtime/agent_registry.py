from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class AgentRegistration:
    name: str
    role: str
    can_write_workspace: bool
    can_write_persistent: bool


class AgentRegistry:
    def __init__(self) -> None:
        self._agents: dict[str, AgentRegistration] = {}

    def register(self, registration: AgentRegistration) -> None:
        self._agents[registration.name] = registration

    def get(self, name: str) -> AgentRegistration:
        return self._agents[name]

    def names(self) -> list[str]:
        return sorted(self._agents)


def default_registry() -> AgentRegistry:
    registry = AgentRegistry()
    registry.register(AgentRegistration("LeaderAgent", "orchestration", True, True))
    for name, role in {
        "DataAgent": "data",
        "ResearchAgent": "research",
        "StrategyAgent": "strategy",
        "QuantEngineeringAgent": "quant engineering",
        "QuantConnectAgent": "quantconnect",
        "PortfolioCapitalAgent": "portfolio capital",
        "RiskControlAgent": "risk control",
        "BrokerExecutionAgent": "broker execution",
        "ReportingAgent": "reporting",
    }.items():
        registry.register(AgentRegistration(name, role, True, False))
    return registry
