from pathlib import Path

import pytest

from system.runtime.promotion_manager import PromotionManager
from system.schemas._validation import ValidationError, default_metadata


def test_strategy_promotion_requires_risk_file(tmp_path: Path):
    source = tmp_path / "workspace" / "promotion_queue" / "candidate_strategies" / "s1"
    source.mkdir(parents=True)
    (source / "spec.yaml").write_text("strategy_id: s1", encoding="utf-8")
    manager = PromotionManager(tmp_path)
    candidate = manager.create_promotion_candidate(
        "strategy",
        "workspace/promotion_queue/candidate_strategies/s1",
        "persistent/strategies/s1",
        "StrategyAgent",
        "wf",
        default_metadata("wf", "test", "StrategyAgent"),
    )
    with pytest.raises(ValidationError):
        manager.validate_candidate(candidate)
