import json
from pathlib import Path

from apps.api.server import api_get, api_post


def test_api_get_cockpit_loads_latest_snapshot(tmp_path: Path):
    _write_snapshot(tmp_path, {
        "workflow_id": "wf",
        "status": "partial",
        "market_lens": {"news": {"summary": "news"}},
    })

    status, payload = api_get("/api/cockpit", tmp_path)

    assert status == 200
    assert payload["workflow_id"] == "wf"


def test_api_get_market_lens_returns_cockpit_section(tmp_path: Path):
    _write_snapshot(tmp_path, {
        "workflow_id": "wf",
        "status": "partial",
        "market_lens": {"technicals": {"signals": []}},
    })

    status, payload = api_get("/api/market-lens", tmp_path)

    assert status == 200
    assert payload["technicals"]["signals"] == []


def test_api_chat_routes_to_project_agent(tmp_path: Path):
    _write_snapshot(tmp_path, {
        "workflow_id": "wf",
        "status": "partial",
        "strategy_center": {"active_strategies": ["s1"], "signals": []},
    })

    status, payload = api_post("/api/chat", {"message": "策略现在怎么样"}, tmp_path)

    assert status == 200
    assert payload["agent"] == "StrategyLabAgent"
    assert payload["workflow_id"] == "wf"


def test_api_confirm_action_is_stub_only(tmp_path: Path):
    status, payload = api_post("/api/actions/confirm", {"action_id": "a1"}, tmp_path)

    assert status == 202
    assert payload["status"] == "recorded_stub"
    assert "No broker execution" in payload["message"]


def _write_snapshot(root: Path, payload: dict) -> None:
    path = root / "outputs" / "compounding" / "latest.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload), encoding="utf-8")
