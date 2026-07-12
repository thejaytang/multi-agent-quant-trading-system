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


def run(root: str | Path | None = None, workflow_id: str | None = None) -> dict:
    root_dir = root_path(root)
    workflow_id = workflow_id or new_workflow_id("capital")
    run_dir = root_dir / "workspace" / "active_runs" / workflow_id
    run_dir.mkdir(parents=True, exist_ok=True)
    leader = leader_packet(workflow_id, "capital review workflow", "capital_review_workflow")
    leader_packet_path = write_leader_packet(root_dir, run_dir, leader)
    snapshot = {
        "snapshot_id": workflow_id,
        "total_net_worth": 0,
        "base_currency": "NOK",
        "buckets": {},
        "accounts": [],
        "metadata": metadata(workflow_id, "capital_review_workflow", "PortfolioCapitalAgent"),
    }
    path = root_dir / "workspace" / "promotion_queue" / "candidate_capital_updates" / f"{workflow_id}.json"
    write_json(path, snapshot)
    return {
        "workflow_id": workflow_id,
        "capital_candidate": str(path),
        "leader_packet": str(leader_packet_path),
        "status": "completed_stub",
    }
