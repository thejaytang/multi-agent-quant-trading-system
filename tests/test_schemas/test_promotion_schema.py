import pytest

from system.schemas._validation import ValidationError
from system.schemas.promotion_schema import PromotionCandidateSchema


def test_promotion_schema_requires_leader_review():
    with pytest.raises(ValidationError):
        PromotionCandidateSchema.from_dict({
            "candidate_id": "pc1",
            "asset_type": "report",
            "source_workspace_path": "workspace/promotion_queue/candidate_reports/r1",
            "target_persistent_path": "persistent/reports/daily/r1",
            "created_by_agent": "ReportingAgent",
            "workflow_id": "wf",
            "created_at": "2026-06-03T00:00:00+00:00",
            "metadata": {"workflow_id": "wf", "source": "test", "created_at": "2026-06-03T00:00:00+00:00", "created_by": "ReportingAgent"},
            "leader_review_required": False,
        })
