from __future__ import annotations

import base64
import hashlib
import time
from typing import Any

from integrations.base import IntegrationClient, RequestSpec


class QuantconnectClient(IntegrationClient):
    integration_name = "quantconnect"
    required_env = ("QUANTCONNECT_USER_ID", "QUANTCONNECT_API_TOKEN")
    base_url = "https://www.quantconnect.com/api/v2"

    def authentication_headers(self) -> dict[str, str]:
        timestamp = str(int(time.time()))
        api_token = self.credential("QUANTCONNECT_API_TOKEN") or ""
        user_id = self.credential("QUANTCONNECT_USER_ID") or ""
        hashed_token = hashlib.sha256(f"{api_token}:{timestamp}".encode("utf-8")).hexdigest()
        authentication = base64.b64encode(f"{user_id}:{hashed_token}".encode("utf-8")).decode("ascii")
        return {"Authorization": f"Basic {authentication}", "Timestamp": timestamp}

    def build_authenticate_request(self) -> RequestSpec:
        return RequestSpec(
            method="POST",
            url=f"{self.base_url}/authenticate",
            params={},
            headers=self.authentication_headers(),
        )

    def authenticate(self) -> dict[str, Any]:
        return self.request_json(self.build_authenticate_request(), body={})


QuantConnectClient = QuantconnectClient
