from pathlib import Path

from system.workflows.backtest_workflow import run


def test_backtest_creates_experiment_candidate(tmp_path: Path):
    result = run(root=tmp_path, workflow_id="backtest_test")
    candidate = Path(result["candidate_dir"])
    for file_name in ["data_version.json", "code_version.txt", "params.json", "cost_model.json", "slippage_model.json", "results.json"]:
        assert (candidate / file_name).exists()


def test_backtest_uses_local_price_csv_when_available(tmp_path: Path):
    strategy_dir = tmp_path / "persistent" / "strategies" / "example_ma_cross_v1"
    strategy_dir.mkdir(parents=True)
    (strategy_dir / "params.yaml").write_text("fast_window: 2\nslow_window: 3\n", encoding="utf-8")

    price_dir = tmp_path / "data" / "normalized" / "prices"
    price_dir.mkdir(parents=True)
    (price_dir / "SPY.csv").write_text(
        "date,close\n"
        "2026-01-01,100\n"
        "2026-01-02,101\n"
        "2026-01-03,102\n"
        "2026-01-04,103\n"
        "2026-01-05,104\n",
        encoding="utf-8",
    )

    result = run(root=tmp_path, workflow_id="backtest_price_csv")

    assert result["status"] == "completed_local"
