import json
from pathlib import Path

from system.workflows.daily_compounding_workflow import run


def test_daily_compounding_workflow_creates_cockpit_snapshot(tmp_path: Path):
    _write_json(tmp_path / "persistent" / "project_state" / "active_strategies.json", {
        "active_strategies": ["example_ma_cross_v1"],
    })
    _write_json(tmp_path / "persistent" / "project_state" / "current_broker_mode.json", {
        "mode": "paper",
        "live_enabled": False,
    })
    _write_json(tmp_path / "persistent" / "project_state" / "current_risk_mode.json", {
        "risk_mode": "normal",
    })
    _write_json(tmp_path / "persistent" / "portfolios" / "current_portfolio.json", {
        "total_equity": 100000,
        "positions": [{"symbol": "SPY", "quantity": 10, "stop_loss": 480, "take_profit": 540}],
    })
    _write_json(tmp_path / "persistent" / "ledgers" / "pnl" / "pnl_summary.json", {
        "today_pnl": 125.5,
        "cagr": 0.12,
        "max_drawdown": -0.08,
        "compound_curve": [{"date": "2026-06-07", "equity": 100000}],
    })
    _write_json(tmp_path / "outputs" / "daily_signals" / "latest.json", {
        "signals": [{"symbol": "SPY", "signal": "BUY", "timeframe": "1d"}],
        "broker_mode": "paper",
    })

    result = run(root=tmp_path, workflow_id="compounding_test")

    snapshot_path = Path(result["cockpit_snapshot"])
    latest_path = Path(result["latest_snapshot"])
    assert snapshot_path.exists()
    assert latest_path.exists()
    assert result["risk_decision"] == "PASS"

    snapshot = json.loads(snapshot_path.read_text(encoding="utf-8"))
    assert snapshot["metadata"]["workflow_id"] == "compounding_test"
    assert snapshot["top_metrics"]["total_equity"] == 100000
    assert snapshot["top_metrics"]["risk_mode"] == "normal"
    assert snapshot["market_lens"]["technicals"]["signals"][0]["symbol"] == "SPY"
    assert snapshot["execution_desk"]["human_confirmation_required"] is True
    assert snapshot["execution_desk"]["pending_actions"][0]["action"] == "BUY"

    for packet_name in [
        "research_packet",
        "strategy_packet",
        "risk_packet",
        "execution_packet",
        "performance_packet",
        "cockpit_snapshot",
    ]:
        assert (tmp_path / "workspace" / "active_runs" / "compounding_test" / f"{packet_name}.json").exists()
        assert (tmp_path / "workspace" / "handoff" / f"{packet_name}.json").exists()


def test_daily_compounding_workflow_rejects_live_execution_context(tmp_path: Path):
    _write_json(tmp_path / "persistent" / "project_state" / "current_broker_mode.json", {
        "mode": "live",
        "live_enabled": True,
    })
    _write_json(tmp_path / "outputs" / "daily_signals" / "latest.json", {
        "signals": [{"symbol": "SPY", "signal": "BUY", "timeframe": "1d"}],
    })

    result = run(root=tmp_path, workflow_id="compounding_live")

    risk_packet = json.loads(
        (tmp_path / "workspace" / "active_runs" / "compounding_live" / "risk_packet.json").read_text(encoding="utf-8")
    )
    snapshot = json.loads(Path(result["cockpit_snapshot"]).read_text(encoding="utf-8"))

    assert result["risk_decision"] == "REJECT"
    assert result["status"] == "blocked"
    assert risk_packet["risk_gate_passed"] is False
    assert risk_packet["rejection_can_be_overridden"] is False
    assert snapshot["execution_desk"]["pending_actions"] == []
    assert snapshot["execution_desk"]["rejected_actions"][0]["reason"] == risk_packet["reason"]


def test_daily_compounding_workflow_connects_capital_snapshot_and_strategy_registry(tmp_path: Path):
    _write_json(tmp_path / "persistent" / "capital" / "capital_snapshot_latest.json", {
        "base_currency": "NOK",
        "known_nok_assets_total": 261726,
        "accounts": [
            {
                "account_id": "ibkr_read_only",
                "provider": "IBKR",
                "source": "ibkr_api",
                "positions": [
                    {"symbol": "MSFT", "quantity": 10, "avg_cost": 409.9},
                    {"symbol": "NVDA", "quantity": 10, "avg_cost": 233.38},
                ],
            }
        ],
    })
    registry = tmp_path / "persistent" / "strategies" / "registry.yaml"
    registry.parent.mkdir(parents=True, exist_ok=True)
    registry.write_text("strategies:\n  - s1\n  - s2\n", encoding="utf-8")
    _write_json(tmp_path / "persistent" / "experiments" / "experiment_index.json", {
        "experiments": [{"experiment_id": "exp1", "strategy_id": "s1"}],
    })

    result = run(root=tmp_path, workflow_id="compounding_connected")
    snapshot = json.loads(Path(result["cockpit_snapshot"]).read_text(encoding="utf-8"))

    assert snapshot["top_metrics"]["total_equity"] == 261726
    assert snapshot["top_metrics"]["base_currency"] == "NOK"
    assert {item["symbol"] for item in snapshot["portfolio_risk"]["positions"]} == {"MSFT", "NVDA"}
    assert snapshot["portfolio_risk"]["checks"]["accounts_count"] == 1
    assert snapshot["strategy_center"]["strategy_library_summary"]["total_count"] == 2
    assert snapshot["strategy_center"]["strategy_library_summary"]["experiments_count"] == 1
    assert snapshot["performance_journal"]["compound_curve"][0]["equity"] == 261726


def test_daily_compounding_workflow_tracks_plugin_connector_status_separately(tmp_path: Path):
    _write_json(tmp_path / "workspace" / "handoff" / "plugin_connector_status.json", {
        "verified_at": "2026-06-07T20:52:45+02:00",
        "plugins": {
            "public_equity_investing": {
                "plugin": "Public Equity Investing",
                "status": "available",
                "connectors": [{"name": "Gmail", "status": "connected"}],
            },
            "investment_banking": {
                "plugin": "Investment Banking",
                "status": "available",
                "connectors": [{"name": "Gmail", "status": "connected"}],
            },
        },
    })

    result = run(root=tmp_path, workflow_id="compounding_plugins")
    snapshot = json.loads(Path(result["cockpit_snapshot"]).read_text(encoding="utf-8"))
    external_sources = snapshot["market_lens"]["external_sources"]

    assert external_sources["connected"]["public_equity_investing"] is True
    assert external_sources["connected"]["investment_banking"] is True
    assert external_sources["research_packets_loaded"]["public_equity_investing"] is False
    assert external_sources["research_packets_loaded"]["investment_banking"] is False
    assert external_sources["connector_status"]["plugins"]["public_equity_investing"]["research_packet_status"] == "missing"
    assert external_sources["connector_status"]["plugins"]["investment_banking"]["research_packet_status"] == "missing"


def _write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload), encoding="utf-8")
