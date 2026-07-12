from pathlib import Path

import pytest

from system.runtime.promotion_manager import PromotionManager
from system.schemas._validation import ValidationError, default_metadata


def test_experiment_promotion_requires_versions(tmp_path: Path):
    source = tmp_path / "workspace" / "promotion_queue" / "candidate_experiments" / "e1"
    source.mkdir(parents=True)
    (source / "results.json").write_text("{}", encoding="utf-8")
    manager = PromotionManager(tmp_path)
    candidate = manager.create_promotion_candidate(
        "experiment",
        "workspace/promotion_queue/candidate_experiments/e1",
        "persistent/experiments/2026/e1",
        "StrategyAgent",
        "wf",
        default_metadata("wf", "test", "StrategyAgent"),
    )
    with pytest.raises(ValidationError):
        manager.validate_candidate(candidate)
