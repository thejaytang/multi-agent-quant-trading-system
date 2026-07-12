from __future__ import annotations

import json
import sys
from pathlib import Path

from system.agents import LeaderAgent
from system.workflows._helpers import new_workflow_id, root_path, write_json, write_text


DEFAULT_TASK = "manual Codex or Claude Code session bootstrap"


def run(task: str = DEFAULT_TASK, root: str | Path | None = None, workflow_id: str | None = None) -> dict:
    root_dir = root_path(root)
    workflow_id = workflow_id or new_workflow_id("leader")
    run_dir = root_dir / "workspace" / "active_runs" / workflow_id
    run_dir.mkdir(parents=True, exist_ok=True)

    leader_packet = LeaderAgent().run({
        "workflow_id": workflow_id,
        "task": task,
        "entrypoint": "leader_orchestrated_workflow",
    })

    write_json(run_dir / "leader_packet.json", leader_packet)
    write_json(run_dir / "delegation_plan.json", leader_packet["delegation_plan"])
    write_json(run_dir / "agent_trace.json", leader_packet["subagent_outputs"])
    write_json(root_dir / "workspace" / "handoff" / "leader_packet.json", leader_packet)
    write_text(root_dir / "workspace" / "shared_context" / "current_task.md", f"# Current Task\n\n{task}\n")

    return {
        "workflow_id": workflow_id,
        "run_dir": str(run_dir),
        "leader_packet": str(run_dir / "leader_packet.json"),
        "delegation_plan": str(run_dir / "delegation_plan.json"),
        "agent_trace": str(run_dir / "agent_trace.json"),
        "status": "leader_orchestrated_stub",
    }


if __name__ == "__main__":
    cli_task = " ".join(sys.argv[1:]).strip() or DEFAULT_TASK
    print(json.dumps(run(task=cli_task), indent=2))
