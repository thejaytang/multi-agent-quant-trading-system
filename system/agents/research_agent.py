from __future__ import annotations

from system.agents.base_agent import BaseAgent


class ResearchAgent(BaseAgent):
    def __init__(self) -> None:
        super().__init__(
            name="ResearchAgent",
            role="Financial research and structured signal generation",
            skills=['news_analysis', 'sentiment_scoring', 'technical_analysis', 'fundamental_analysis', 'macro_regime_analysis', 'bull_case_generation', 'bear_case_generation', 'red_team_challenge'],
            can_write_workspace=True,
            can_write_persistent=False,
            can_execute_live_trade=False,
        )

