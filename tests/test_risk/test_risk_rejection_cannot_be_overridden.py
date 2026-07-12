import pytest

from system.schemas._validation import ValidationError
from system.schemas.risk_schema import RiskDecisionSchema


def test_risk_rejection_cannot_be_overridden():
    with pytest.raises(ValidationError):
        RiskDecisionSchema.from_dict({
            "decision_id": "r1",
            "decision": "REJECT",
            "reason": "limit breach",
            "workflow_id": "wf",
            "source": "test",
            "created_at": "2026-06-03T00:00:00+00:00",
            "created_by": "RiskControlAgent",
            "rejection_can_be_overridden": True,
            "checks": {},
            "metadata": {},
        })
