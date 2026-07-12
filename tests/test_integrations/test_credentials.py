from pathlib import Path

import pytest

from integrations.base import ExternalRequestDisabled, load_local_env, redacted
from integrations.fred.client import FredClient
from integrations.ibkr.client import IbkrClient
from integrations.massive.client import MassiveClient


def test_load_local_env_reads_dot_env_without_mutating_process_env(tmp_path: Path):
    (tmp_path / ".env").write_text("MASSIVE_API_KEY=dummy\n", encoding="utf-8")
    env = load_local_env(tmp_path)
    assert env["MASSIVE_API_KEY"] == "dummy"


def test_redacted_keeps_secret_out_of_healthcheck():
    assert redacted("abcd1234efgh5678") == "abcd...5678"


def test_massive_reports_missing_credentials_without_connection(tmp_path: Path):
    result = MassiveClient(root=tmp_path).healthcheck()
    assert result["status"] == "missing_credentials"
    assert result["missing_credentials"] == ["MASSIVE_API_KEY"]
    assert result["external_connection"] is False


def test_request_builders_sanitize_credentials(tmp_path: Path):
    (tmp_path / ".env").write_text("FRED_API_KEY=dummy\n", encoding="utf-8")
    client = FredClient(root=tmp_path)
    request = client.build_series_observations_request("DGS10").sanitized()
    assert request["params"]["api_key"] == "***"


def test_external_fetch_requires_explicit_enablement(tmp_path: Path):
    (tmp_path / ".env").write_text("MASSIVE_API_KEY=dummy\n", encoding="utf-8")
    with pytest.raises(ExternalRequestDisabled):
        MassiveClient(root=tmp_path).fetch_daily_ohlcv("SPY", "2026-01-01", "2026-01-31")


def test_ibkr_live_order_requires_live_trading_enabled(tmp_path: Path):
    payload = {
        "strategy_id": "s1",
        "mode": "live",
        "orders": [{"symbol": "SPY", "action": "BUY", "quantity": 1, "order_type": "market"}],
        "risk_approved": True,
        "human_approved": True,
        "workflow_id": "wf",
        "source": "test",
        "created_at": "2026-06-03T00:00:00+00:00",
        "created_by": "BrokerExecutionAgent",
        "metadata": {},
    }
    with pytest.raises(ExternalRequestDisabled):
        IbkrClient(root=tmp_path, config={"enable_external_requests": True}).submit_order(payload)


def test_ibkr_connection_profile_defaults_to_paper_read_only(tmp_path: Path):
    result = IbkrClient(root=tmp_path).healthcheck()
    profile = result["connection_profile"]
    assert profile["broker_mode"] == "paper"
    assert profile["host"] == "127.0.0.1"
    assert profile["port"] == 7497
    assert profile["client_id"] == 1
    assert profile["read_only"] is True
