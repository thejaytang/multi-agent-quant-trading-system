from __future__ import annotations

from system.agents.base_agent import BaseAgent


class ReportingAgent(BaseAgent):
    def __init__(self) -> None:
        super().__init__(
            name="ReportingAgent",
            role="Report, review, ledger, and decision summary drafting",
            skills=['daily_report_generation', 'weekly_report_generation', 'strategy_report_generation', 'trade_review', 'pnl_attribution', 'tax_ledger_export', 'dividend_record', 'fx_record', 'decision_log_summary'],
            can_write_workspace=True,
            can_write_persistent=False,
            can_execute_live_trade=False,
        )

