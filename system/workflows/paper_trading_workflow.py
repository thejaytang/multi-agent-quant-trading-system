from __future__ import annotations

from pathlib import Path

from system.workflows._helpers import (
    leader_packet,
    metadata,
    new_workflow_id,
    root_path,
    write_json,
    write_leader_packet,
)


def run(user_confirmed: bool = False, root: str | Path | None = None, workflow_id: str | None = None) -> dict:
    root_dir = root_path(root)
    workflow_id = workflow_id or new_workflow_id("paper")
    run_dir = root_dir / "workspace" / "active_runs" / workflow_id
    run_dir.mkdir(parents=True, exist_ok=True)
    leader = leader_packet(workflow_id, "paper trading workflow", "paper_trading_workflow")
    leader_packet_path = write_leader_packet(root_dir, run_dir, leader)
    if not user_confirmed:
        return {
            "workflow_id": workflow_id,
            "status": "blocked_for_user_confirmation",
            "mode": "paper",
            "leader_packet": str(leader_packet_path),
        }
    payload = {
        "workflow_id": workflow_id,
        "mode": "paper",
        "status": "started_stub",
        "metadata": metadata(workflow_id, "paper_trading_workflow", "QuantConnectAgent"),
    }
    write_json(root_dir / "outputs" / "paper_trading" / f"{workflow_id}.json", payload)
    return {**payload, "leader_packet": str(leader_packet_path)}
