from pathlib import Path


def test_broker_mode_default_is_paper():
    text = Path("config/broker_mode.yaml").read_text(encoding="utf-8")
    assert "default_mode: paper" in text
    assert "live_enabled: false" in text
