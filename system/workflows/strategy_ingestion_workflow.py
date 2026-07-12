from __future__ import annotations

from pathlib import Path

from system.workflows._helpers import (
    leader_packet,
    metadata,
    new_workflow_id,
    root_path,
    write_json,
    write_leader_packet,
    write_text,
)

DEFAULT_STRATEGY_TEXT = "Moving average cross strategy using SPY with paper-only stub execution."


def run(strategy_text: str = DEFAULT_STRATEGY_TEXT, root: str | Path | None = None, workflow_id: str | None = None) -> dict:
    root_dir = root_path(root)
    workflow_id = workflow_id or new_workflow_id("strategy_ingestion")
    run_dir = root_dir / "workspace" / "active_runs" / workflow_id
    run_dir.mkdir(parents=True, exist_ok=True)
    leader = leader_packet(workflow_id, "strategy ingestion workflow", "strategy_ingestion_workflow")
    leader_packet_path = write_leader_packet(root_dir, run_dir, leader)
    strategy_id = "candidate_ma_cross_v1"
    candidate_dir = root_dir / "workspace" / "promotion_queue" / "candidate_strategies" / strategy_id
    candidate_dir.mkdir(parents=True, exist_ok=True)

    write_text(candidate_dir / "source.md", strategy_text + "\n")
    write_text(candidate_dir / "spec.yaml", """
strategy_id: candidate_ma_cross_v1
name: Candidate Moving Average Cross
version: v1
source_type: manual_text
status: backtest_ready
asset_class: equity
market: US
timeframe: daily
data_requirements:
  - Massive daily OHLCV
risk_level: low
quantconnect_compatible: true
implementation_path: signal_generator.py
live_enabled: false
""")
    write_text(candidate_dir / "params.yaml", "fast_window: 20\nslow_window: 50\n")
    write_text(candidate_dir / "risk.yaml", "max_single_position: 0.05\nallow_leverage: false\nallow_short_selling: false\n")
    write_text(candidate_dir / "signal_generator.py", """
from __future__ import annotations


def generate_signal(fast_ma: float, slow_ma: float) -> str:
    if fast_ma > slow_ma:
        return "BUY"
    if fast_ma < slow_ma:
        return "SELL"
    return "HOLD"
""")
    write_text(candidate_dir / "quantconnect_main.py", """
from __future__ import annotations


class CandidateMovingAverageCrossAlgorithm:
    broker_mode = "paper"

    def initialize(self) -> None:
        self.symbol = "SPY"
""")
    write_json(candidate_dir / "metadata.json", metadata(workflow_id, "strategy_ingestion_workflow", "StrategyAgent"))
    write_text(candidate_dir / "changelog.md", "# Changelog\n\n- v1: Created candidate strategy package.\n")
    return {
        "workflow_id": workflow_id,
        "strategy_id": strategy_id,
        "candidate_dir": str(candidate_dir),
        "leader_packet": str(leader_packet_path),
        "status": "completed_stub",
    }


if __name__ == "__main__":
    import json
    print(json.dumps(run(), indent=2))
