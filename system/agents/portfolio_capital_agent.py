from __future__ import annotations

from system.agents.base_agent import BaseAgent


class PortfolioCapitalAgent(BaseAgent):
    def __init__(self) -> None:
        super().__init__(
            name="PortfolioCapitalAgent",
            role="Capital aggregation, allocation, liquidity, FX, and position sizing",
            skills=['account_aggregation', 'capital_allocation', 'liquidity_reserve_check', 'fx_exposure_check', 'treasury_transfer_suggestion', 'strategy_allocation', 'position_sizing', 'cash_management'],
            can_write_workspace=True,
            can_write_persistent=False,
            can_execute_live_trade=False,
        )

