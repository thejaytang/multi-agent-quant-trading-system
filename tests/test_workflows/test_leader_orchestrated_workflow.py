import json
from pathlib import Path

from system.workflows.leader_orchestrated_workflow import run


def test_leader_orchestrated_workflow_writes_full_team_trace(tmp_path: Path):
    result = run(task="daily multi-agent review", root=tmp_path, workflow_id="leader_test")

    leader_packet_path = Path(result["leader_packet"])
    delegation_plan_path = Path(result["delegation_plan"])
    agent_trace_path = Path(result["agent_trace"])

    assert leader_packet_path.exists()
    assert delegation_plan_path.exists()
    assert agent_trace_path.exists()
    assert (tmp_path / "workspace" / "handoff" / "leader_packet.json").exists()
    assert (tmp_path / "workspace" / "shared_context" / "current_task.md").exists()

    leader_packet = json.loads(leader_packet_path.read_text(encoding="utf-8"))
    agent_trace = json.loads(agent_trace_path.read_text(encoding="utf-8"))

    assert leader_packet["agent"] == "LeaderAgent"
    assert leader_packet["delegation_mode"] == "full_team"
    assert len(agent_trace) == 9
