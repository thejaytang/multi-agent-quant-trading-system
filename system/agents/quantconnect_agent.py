from __future__ import annotations

from system.agents.base_agent import BaseAgent


class QuantConnectAgent(BaseAgent):
    def __init__(self) -> None:
        super().__init__(
            name="QuantConnectAgent",
            role="QuantConnect project, backtest, paper trading, and live deploy preparation stubs",
            skills=['quantconnect_project_management', 'code_sync', 'backtest_execution', 'backtest_result_parsing', 'object_store_upload', 'paper_trading_monitoring', 'live_deploy_precheck', 'quantconnect_log_analysis'],
            can_write_workspace=True,
            can_write_persistent=False,
            can_execute_live_trade=False,
        )

