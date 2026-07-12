from __future__ import annotations

import json
from pathlib import Path
from typing import Any
from uuid import uuid4

from system.schemas._validation import default_metadata


def root_path(root: str | Path | None = None) -> Path:
    return Path(root or Path.cwd()).resolve()


def new_workflow_id(prefix: str) -> str:
    return f"{prefix}_{uuid4().hex[:8]}"


def write_json(path: Path, payload: Any) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    return path


def write_text(path: Path, payload: str) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(payload, encoding="utf-8")
    return path


def metadata(workflow_id: str, source: str, created_by: str) -> dict[str, Any]:
    return default_metadata(workflow_id, source, created_by)


def leader_packet(workflow_id: str, task: str, entrypoint: str) -> dict[str, Any]:
    from system.agents import LeaderAgent

    return LeaderAgent().run({
        "workflow_id": workflow_id,
        "task": task,
        "entrypoint": entrypoint,
    })


def write_leader_packet(root_dir: Path, run_dir: Path, packet: dict[str, Any]) -> Path:
    path = write_json(run_dir / "leader_packet.json", packet)
    write_json(root_dir / "workspace" / "handoff" / "leader_packet.json", packet)
    return path
