from system.schemas.experiment_schema import ExperimentSchema


def test_experiment_schema_validates_versions_and_results():
    schema = ExperimentSchema.from_dict({
        "experiment_id": "e1",
        "strategy_id": "s1",
        "data_version": "dv",
        "code_version": "cv",
        "params": {"x": 1},
        "cost_model": {"commission": 0},
        "slippage_model": {"bps": 0},
        "results": {"sharpe": 0},
        "workflow_id": "wf",
        "source": "test",
        "created_at": "2026-06-03T00:00:00+00:00",
        "created_by": "QuantConnectAgent",
        "metadata": {},
    })
    assert schema.strategy_id == "s1"
