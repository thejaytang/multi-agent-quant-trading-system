import json
from pathlib import Path

from system.runtime.agent_router import AgentRouter


def test_agent_router_routes_risk_question_to_risk_agent(tmp_path: Path):
    _write_snapshot(tmp_path, {
        "workflow_id": "wf",
        "status": "partial",
        "portfolio_risk": {
            "risk_decision": "PASS",
            "reason": "paper-safe",
        },
    })

    response = AgentRouter(tmp_path).route("我的止损和风险怎么样")

    assert response["agent"] == "RiskControlAgent"
    assert response["workflow_id"] == "wf"
    assert "PASS" in response["message"]


def test_agent_router_handles_missing_snapshot(tmp_path: Path):
    response = AgentRouter(tmp_path).route("系统状态")

    assert response["agent"] == "LeaderAgent"
    assert response["workflow_id"] == "unknown"
    assert response["limitations"] == ["No cockpit snapshot is available."]


def _write_snapshot(root: Path, payload: dict) -> None:
    path = root / "outputs" / "compounding" / "latest.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload), encoding="utf-8")
