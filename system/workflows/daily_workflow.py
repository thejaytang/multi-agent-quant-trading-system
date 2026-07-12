from __future__ import annotations

from pathlib import Path

from system.workflows._helpers import (
    leader_packet,
    metadata,
    new_workflow_id,
    root_path,
    write_json,
    write_leader_packet,
    write_text,
)


def run(root: str | Path | None = None, workflow_id: str | None = None) -> dict:
    root_dir = root_path(root)
    workflow_id = workflow_id or new_workflow_id("daily")
    run_dir = root_dir / "workspace" / "active_runs" / workflow_id
    run_dir.mkdir(parents=True, exist_ok=True)
    leader = leader_packet(workflow_id, "daily workflow", "daily_workflow")
    leader_packet_path = write_leader_packet(root_dir, run_dir, leader)

    data_packet = {
        "symbols": ["SPY", "QQQ"],
        "quality_status": "stub_pass",
        "metadata": metadata(workflow_id, "daily_workflow.data_packet", "DataAgent"),
    }
    research_packet = {
        "facts": [],
        "interpretations": [],
        "signals": [{"symbol": "SPY", "signal": "HOLD", "timeframe": "1d"}],
        "risk_flags": [],
        "confidence": 0.5,
        "metadata": metadata(workflow_id, "daily_workflow.research_packet", "ResearchAgent"),
    }
    risk_packet = {
        "decision": "PASS",
        "reason": "stub daily workflow only produces paper-safe signals",
        "metadata": metadata(workflow_id, "daily_workflow.risk_packet", "RiskControlAgent"),
    }
    daily_signals = {
        "workflow_id": workflow_id,
        "signals": research_packet["signals"],
        "broker_mode": "paper",
        "metadata": metadata(workflow_id, "outputs.daily_signals", "QuantConnectAgent"),
    }
    report_body = "Daily report draft. External data and broker connectivity are stubs."

    write_json(run_dir / "data_packet.json", data_packet)
    write_json(run_dir / "research_packet.json", research_packet)
    write_json(run_dir / "risk_packet.json", risk_packet)
    write_json(root_dir / "workspace" / "handoff" / "data_packet.json", data_packet)
    write_json(root_dir / "workspace" / "handoff" / "research_packet.json", research_packet)
    write_json(root_dir / "workspace" / "handoff" / "risk_packet.json", risk_packet)
    write_json(root_dir / "outputs" / "daily_signals" / "latest.json", daily_signals)

    candidate_dir = root_dir / "workspace" / "promotion_queue" / "candidate_reports" / f"daily_report_{workflow_id}"
    write_text(candidate_dir / "report.md", report_body)
    write_json(candidate_dir / "metadata.json", metadata(workflow_id, "daily_workflow.report", "ReportingAgent"))

    return {
        "workflow_id": workflow_id,
        "run_dir": str(run_dir),
        "leader_packet": str(leader_packet_path),
        "daily_signals": str(root_dir / "outputs" / "daily_signals" / "latest.json"),
        "report_candidate": str(candidate_dir),
        "status": "completed_stub",
    }


if __name__ == "__main__":
    import json
    print(json.dumps(run(), indent=2))
