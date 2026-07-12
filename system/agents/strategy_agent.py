from __future__ import annotations

from system.agents.base_agent import BaseAgent


class StrategyAgent(BaseAgent):
    def __init__(self) -> None:
        super().__init__(
            name="StrategyAgent",
            role="Strategy ingestion, registry, lifecycle, and experiment coordination",
            skills=['external_strategy_ingestion', 'strategy_parsing', 'strategy_normalization', 'strategy_registry_management', 'strategy_lifecycle_management', 'strategy_comparison', 'strategy_selection', 'experiment_registry_management'],
            can_write_workspace=True,
            can_write_persistent=False,
            can_execute_live_trade=False,
        )

