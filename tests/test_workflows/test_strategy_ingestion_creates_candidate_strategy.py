from pathlib import Path

from system.workflows.strategy_ingestion_workflow import run


def test_strategy_ingestion_creates_candidate_strategy(tmp_path: Path):
    result = run(root=tmp_path, workflow_id="strategy_test")
    candidate = Path(result["candidate_dir"])
    assert (candidate / "spec.yaml").exists()
    assert (candidate / "risk.yaml").exists()
    assert (candidate / "metadata.json").exists()
