from pathlib import Path

from integrations.sec_edgar.client import SecEdgarClient


def test_sec_edgar_reports_missing_user_agent(tmp_path: Path):
    result = SecEdgarClient(root=tmp_path).healthcheck()
    assert result["status"] == "missing_credentials"
    assert result["missing_credentials"] == ["SEC_EDGAR_USER_AGENT"]


def test_sec_edgar_uses_configured_user_agent(tmp_path: Path):
    (tmp_path / ".env").write_text("SEC_EDGAR_USER_AGENT=trading-os contact@example.com\n", encoding="utf-8")
    request = SecEdgarClient(root=tmp_path).build_company_facts_request("320193")
    assert request.headers["User-Agent"] == "trading-os contact@example.com"
