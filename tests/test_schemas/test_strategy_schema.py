from system.schemas.strategy_schema import StrategySchema


def test_strategy_schema_validates_required_fields():
    schema = StrategySchema.from_dict({
        "strategy_id": "s1",
        "name": "Example",
        "version": "v1",
        "source_type": "manual",
        "status": "backtest_ready",
        "asset_class": "equity",
        "market": "US",
        "timeframe": "daily",
        "data_requirements": ["Massive daily OHLCV"],
        "risk_level": "low",
        "quantconnect_compatible": True,
        "implementation_path": "signal_generator.py",
        "live_enabled": False,
        "changelog": ["created"],
        "workflow_id": "wf",
        "source": "test",
        "created_at": "2026-06-03T00:00:00+00:00",
        "created_by": "StrategyAgent",
        "metadata": {},
    })
    assert schema.strategy_id == "s1"
