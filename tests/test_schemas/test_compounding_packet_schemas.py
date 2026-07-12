import pytest

from system.schemas import CockpitSnapshotSchema, ResearchPacketSchema, RiskPacketSchema
from system.schemas._validation import ValidationError


BASE = {
    "workflow_id": "wf",
    "source": "test",
    "created_at": "2026-06-07T00:00:00+00:00",
    "created_by": "LeaderAgent",
    "metadata": {},
}


def test_research_packet_requires_three_market_lenses():
    with pytest.raises(ValidationError):
        ResearchPacketSchema.from_dict({
            "market_lens": {"news": [], "fundamentals": []},
            "thesis_impacts": [],
            "catalysts": [],
            "risks": [],
            "confidence": 0.5,
            **BASE,
        })


def test_risk_packet_rejection_cannot_be_overridden():
    with pytest.raises(ValidationError):
        RiskPacketSchema.from_dict({
            "risk_mode": "normal",
            "decision": "REJECT",
            "reason": "blocked",
            "risk_gate_passed": False,
            "rejection_can_be_overridden": True,
            "checks": {},
            "alerts": [],
            "stop_loss_take_profit": [],
            **BASE,
        })


def test_cockpit_snapshot_requires_risk_mode_metric():
    with pytest.raises(ValidationError):
        CockpitSnapshotSchema.from_dict({
            "snapshot_id": "cockpit_wf",
            "status": "partial",
            "top_metrics": {"today_pnl": 0},
            "market_lens": {"news": [], "fundamentals": [], "technicals": []},
            "strategy_center": {"active_strategies": []},
            "portfolio_risk": {"positions": []},
            "execution_desk": {"pending_actions": []},
            "performance_journal": {"pnl": {}},
            "agent_trace": {"workflow_id": "wf"},
            **BASE,
        })
