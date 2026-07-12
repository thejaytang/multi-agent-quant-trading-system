from __future__ import annotations

from system.schemas._validation import default_metadata


def run(input_data: dict | None = None, workflow_id: str = "manual") -> dict:
    return {
        "skill": "decision_log_summary",
        "status": "stub",
        "input": input_data or {},
        "output": {},
        "metadata": default_metadata(workflow_id, "decision_log_summary", "decision_log_summary"),
    }
