from __future__ import annotations

from pathlib import Path

from system.workflows._helpers import leader_packet, new_workflow_id, root_path, write_leader_packet


def run(
    human_approved: bool = False,
    risk_approved: bool = False,
    live_enabled: bool = False,
    workflow_id: str | None = None,
    root: str | Path | None = None,
) -> dict:
    root_dir = root_path(root)
    workflow_id = workflow_id or new_workflow_id("live")
    run_dir = root_dir / "workspace" / "active_runs" / workflow_id
    run_dir.mkdir(parents=True, exist_ok=True)
    leader = leader_packet(workflow_id, "live trading workflow precheck", "live_trading_workflow")
    leader_packet_path = write_leader_packet(root_dir, run_dir, leader)

    if not live_enabled:
        return {
            "workflow_id": workflow_id,
            "status": "rejected",
            "reason": "broker_mode live_enabled=false",
            "leader_packet": str(leader_packet_path),
        }
    if not risk_approved:
        return {
            "workflow_id": workflow_id,
            "status": "rejected",
            "reason": "risk approval required",
            "leader_packet": str(leader_packet_path),
        }
    if not human_approved:
        return {
            "workflow_id": workflow_id,
            "status": "rejected",
            "reason": "human approval required",
            "leader_packet": str(leader_packet_path),
        }
    return {
        "workflow_id": workflow_id,
        "status": "prepared_stub_only",
        "live_execution": False,
        "leader_packet": str(leader_packet_path),
    }
