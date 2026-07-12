from __future__ import annotations

from system.schemas._validation import default_metadata
from system.workflows.backtest_workflow import run as run_backtest


def run(input_data: dict | None = None, workflow_id: str = "manual") -> dict:
    input_data = input_data or {}
    strategy_id = input_data.get("strategy_id", "example_ma_cross_v1")
    backtest_result = run_backtest(strategy_id=strategy_id, workflow_id=workflow_id)
    return {
        "skill": "local_quick_backtest",
        "status": backtest_result["status"],
        "input": input_data,
        "output": backtest_result,
        "metadata": default_metadata(workflow_id, "local_quick_backtest", "local_quick_backtest"),
    }
