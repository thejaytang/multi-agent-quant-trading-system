from __future__ import annotations

from system.agents.base_agent import BaseAgent


class DataAgent(BaseAgent):
    def __init__(self) -> None:
        super().__init__(
            name="DataAgent",
            role="Unified data access, processing, and quality control",
            skills=['massive_price_fetch', 'massive_news_fetch', 'sec_edgar_fetch', 'fred_macro_fetch', 'ohlcv_processing', 'data_quality_check', 'timestamp_guard', 'data_versioning'],
            can_write_workspace=True,
            can_write_persistent=False,
            can_execute_live_trade=False,
        )

