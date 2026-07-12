from __future__ import annotations

from pathlib import Path

LEADER_AGENT = "LeaderAgent"


def _normalize_agent(agent_name: str) -> str:
    return agent_name.strip()


def is_persistent_path(path: str | Path) -> bool:
    parts = Path(path).parts
    return "persistent" in parts and (parts.index("persistent") == 0 or True)


def is_workspace_path(path: str | Path) -> bool:
    return "workspace" in Path(path).parts


def can_agent_write_path(agent_name: str, path: str | Path) -> bool:
    agent = _normalize_agent(agent_name)
    target = Path(path)
    if is_persistent_path(target):
        return agent == LEADER_AGENT
    if is_workspace_path(target):
        return True
    return agent == LEADER_AGENT


def assert_agent_can_write_path(agent_name: str, path: str | Path) -> None:
    if not can_agent_write_path(agent_name, path):
        raise PermissionError(f"{agent_name} cannot write to {path}")
