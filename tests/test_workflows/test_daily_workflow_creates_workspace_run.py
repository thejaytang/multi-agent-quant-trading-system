from pathlib import Path

from system.workflows.daily_workflow import run


def test_daily_workflow_creates_workspace_run(tmp_path: Path):
    result = run(root=tmp_path, workflow_id="daily_test")
    assert Path(result["run_dir"]).exists()
    assert Path(result["leader_packet"]).exists()
    assert (tmp_path / "outputs" / "daily_signals" / "latest.json").exists()
    assert Path(result["report_candidate"]).exists()
