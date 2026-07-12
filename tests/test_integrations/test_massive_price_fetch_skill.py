from system.skills.data.massive_price_fetch import run


def test_massive_price_fetch_does_not_connect_by_default(tmp_path):
    result = run({"root": str(tmp_path), "symbols": ["SPY"]}, workflow_id="wf")

    assert result["status"] == "missing_credentials"
    assert result["output"]["missing_credentials"] == ["MASSIVE_API_KEY"]


def test_massive_price_fetch_requires_explicit_external_enablement(tmp_path):
    (tmp_path / ".env.local").write_text("MASSIVE_API_KEY=dummy\n", encoding="utf-8")

    result = run({"root": str(tmp_path), "symbols": ["SPY"]}, workflow_id="wf")

    assert result["status"] == "external_requests_disabled"
