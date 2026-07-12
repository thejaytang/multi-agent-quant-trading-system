from __future__ import annotations

from typing import Any

from integrations.base import IntegrationClient, RequestSpec


class MassiveClient(IntegrationClient):
    integration_name = "massive"
    required_env = ("MASSIVE_API_KEY",)
    base_url = "https://api.massive.com"

    def build_daily_ohlcv_request(self, symbol: str, start: str, end: str) -> RequestSpec:
        api_key = self.credential("MASSIVE_API_KEY")
        return RequestSpec(
            method="GET",
            url=f"{self.base_url}/v2/aggs/ticker/{symbol}/range/1/day/{start}/{end}",
            params={"adjusted": "true", "sort": "asc", "apiKey": api_key},
            headers={},
        )

    def fetch_daily_ohlcv(self, symbol: str, start: str, end: str) -> dict[str, Any]:
        return self.request_json(self.build_daily_ohlcv_request(symbol, start, end))

    def build_news_request(self, symbol: str, limit: int = 10) -> RequestSpec:
        api_key = self.credential("MASSIVE_API_KEY")
        return RequestSpec(
            method="GET",
            url=f"{self.base_url}/v2/reference/news",
            params={"ticker": symbol, "limit": limit, "apiKey": api_key},
            headers={},
        )

    def fetch_news(self, symbol: str, limit: int = 5) -> dict[str, Any]:
        return self.request_json(self.build_news_request(symbol, limit))
