from __future__ import annotations


class TradingOsAlgorithm:
    """QuantConnect-oriented stub. It avoids importing QuantConnect locally."""

    broker_mode = "paper"

    def initialize(self) -> None:
        self.active_strategies_path = "object_store/active_strategies.json"
        self.daily_signals_path = "object_store/daily_signals.json"
