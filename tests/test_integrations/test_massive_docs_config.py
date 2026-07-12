from pathlib import Path


def test_massive_docs_links_are_recorded():
    text = Path("integrations/massive/README.md").read_text(encoding="utf-8")
    assert "https://massive.com/docs/rest/llms.txt" in text
    assert "https://massive.com/docs/websocket/llms.txt" in text
    assert "https://github.com/massive-com/mcp_massive" in text


def test_massive_config_uses_current_provider_name():
    text = Path("config/data_sources.yaml").read_text(encoding="utf-8")
    assert "Massive" in text
    assert "Polygon" not in text
