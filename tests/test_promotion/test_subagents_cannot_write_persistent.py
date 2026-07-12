from system.runtime.permissions import can_agent_write_path


def test_subagents_cannot_write_persistent():
    assert not can_agent_write_path("DataAgent", "persistent/reports/daily/report.md")
    assert can_agent_write_path("DataAgent", "workspace/promotion_queue/candidate_reports/report.md")
