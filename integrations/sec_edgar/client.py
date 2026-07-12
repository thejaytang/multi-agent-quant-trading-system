from __future__ import annotations


from integrations.base import IntegrationClient, RequestSpec


class SecEdgarClient(IntegrationClient):
    integration_name = "sec_edgar"
    required_env = ("SEC_EDGAR_USER_AGENT",)
    base_url = "https://data.sec.gov"

    def build_company_facts_request(self, cik: str) -> RequestSpec:
        normalized = cik.zfill(10)
        return RequestSpec(
            method="GET",
            url=f"{self.base_url}/api/xbrl/companyfacts/CIK{normalized}.json",
            params={},
            headers={"User-Agent": self.credential("SEC_EDGAR_USER_AGENT") or "trading-os contact-required"},
        )

    def fetch_company_facts(self, cik: str) -> dict:
        return self.request_json(self.build_company_facts_request(cik))
