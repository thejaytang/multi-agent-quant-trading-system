from system.workflows.live_trading_workflow import run


def test_paper_to_live_gate_blocks_when_live_disabled():
    result = run(human_approved=True, risk_approved=True, live_enabled=False)
    assert result["status"] == "rejected"
    assert "live_enabled=false" in result["reason"]
