from __future__ import annotations

from typing import Any

from integrations.base import IntegrationClient, RequestSpec


class FredClient(IntegrationClient):
    integration_name = "fred"
    required_env = ("FRED_API_KEY",)
    base_url = "https://api.stlouisfed.org/fred"

    def build_series_observations_request(self, series_id: str) -> RequestSpec:
        return RequestSpec(
            method="GET",
            url=f"{self.base_url}/series/observations",
            params={
                "series_id": series_id,
                "api_key": self.credential("FRED_API_KEY"),
                "file_type": "json",
            },
            headers={},
        )

    def fetch_series_observations(self, series_id: str) -> dict[str, Any]:
        return self.request_json(self.build_series_observations_request(series_id))
