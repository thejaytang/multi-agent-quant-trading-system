import pytest

from system.schemas._validation import ValidationError
from system.schemas.signal_schema import SignalSchema


def test_signal_schema_requires_confidence_range():
    with pytest.raises(ValidationError):
        SignalSchema.from_dict({
            "strategy_id": "s1",
            "signals": [{"symbol": "SPY", "signal": "HOLD", "timeframe": "1d"}],
            "risk_flags": [],
            "confidence": 2,
            "workflow_id": "wf",
            "source": "test",
            "created_at": "2026-06-03T00:00:00+00:00",
            "created_by": "ResearchAgent",
            "metadata": {},
        })
