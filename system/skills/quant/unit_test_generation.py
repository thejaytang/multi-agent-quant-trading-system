from __future__ import annotations

from system.schemas._validation import default_metadata


def run(input_data: dict | None = None, workflow_id: str = "manual") -> dict:
    return {
        "skill": "unit_test_generation",
        "status": "stub",
        "input": input_data or {},
        "output": {},
        "metadata": default_metadata(workflow_id, "unit_test_generation", "unit_test_generation"),
    }
