from pathlib import Path

import pytest

from system.runtime.promotion_manager import PromotionManager
from system.schemas._validation import default_metadata


def test_leader_only_promotion(tmp_path: Path):
    source = tmp_path / "workspace" / "promotion_queue" / "candidate_reports" / "r1"
    source.mkdir(parents=True)
    (source / "report.md").write_text("report", encoding="utf-8")
    manager = PromotionManager(tmp_path)
    candidate = manager.create_promotion_candidate(
        "report",
        "workspace/promotion_queue/candidate_reports/r1",
        "persistent/reports/daily/r1",
        "ReportingAgent",
        "wf",
        default_metadata("wf", "test", "ReportingAgent"),
    )
    with pytest.raises(PermissionError):
        manager.request_leader_review(candidate, reviewer_agent="DataAgent")
    manager.request_leader_review(candidate, reviewer_agent="LeaderAgent")
    target = manager.promote_to_persistent(candidate)
    assert target.exists()
