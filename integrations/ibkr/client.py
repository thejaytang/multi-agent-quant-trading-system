from __future__ import annotations

from typing import Any

from integrations.base import ExternalRequestDisabled, IntegrationClient


class IbkrClient(IntegrationClient):
    integration_name = "ibkr"
    required_env = ("IBKR_ACCOUNT_ID",)

    def connection_profile(self) -> dict[str, Any]:
        mode = self.config.get("broker_mode") or self.env.get("BROKER_MODE") or "paper"
        host = self.config.get("host") or self.env.get("IBKR_HOST") or "127.0.0.1"
        port = self.config.get("port") or self.env.get("IBKR_PORT") or ("7497" if mode == "paper" else "7496")
        client_id = self.config.get("client_id") or self.env.get("IBKR_CLIENT_ID") or "1"
        read_only = self.config.get("read_only")
        if read_only is None:
            read_only = self.env.get("IBKR_READ_ONLY", "true").lower() == "true"
        return {
            "account_id": self.configured_credentials().get("IBKR_ACCOUNT_ID"),
            "broker_mode": mode,
            "host": host,
            "port": int(port),
            "client_id": int(client_id),
            "read_only": bool(read_only),
            "auth_mode": self.config.get("auth_mode") or self.env.get("IBKR_AUTH_MODE") or "tws_gateway_socket",
        }

    def healthcheck(self) -> dict[str, Any]:
        result = super().healthcheck()
        result["connection_profile"] = self.connection_profile()
        return result

    def account_snapshot(self) -> dict[str, Any]:
        return {
            "status": "stub",
            "external_connection": False,
            "connection_profile": self.connection_profile(),
            "cash": [],
            "positions": [],
            "open_orders": [],
            "pnl": {},
            "margin": {},
        }

    def submit_order(self, order_payload: dict[str, Any]) -> dict[str, Any]:
        from system.schemas.order_schema import OrderSchema

        order = OrderSchema.from_dict(order_payload)
        if order.mode == "live":
            if not self.live_trading_enabled:
                raise ExternalRequestDisabled("IBKR live trading is disabled")
            self.require_external_requests_enabled()
        return {
            "status": "accepted_stub",
            "external_connection": False,
            "mode": order.mode,
            "orders": [item.__dict__ for item in order.orders],
        }
