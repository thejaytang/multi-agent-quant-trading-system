from pathlib import Path


def test_sensitive_outputs_ignored():
    text = Path(".gitignore").read_text(encoding="utf-8")
    for item in ["outputs/live_trading/", "outputs/approved_orders/", "data/raw/ibkr/", "persistent/capital/broker_accounts/", "persistent/ledgers/", "logs/broker_events/"]:
        assert item in text
