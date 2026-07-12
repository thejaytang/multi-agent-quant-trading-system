from integrations.fred.client import FredClient
from integrations.ibkr.client import IbkrClient
from integrations.massive.client import MassiveClient
from integrations.quantconnect.client import QuantconnectClient
from integrations.sec_edgar.client import SecEdgarClient


def test_integration_clients_do_not_connect_by_default():
    for cls in [MassiveClient, SecEdgarClient, FredClient, IbkrClient, QuantconnectClient]:
        result = cls().healthcheck()
        assert result["external_connection"] is False
        assert result["external_requests_enabled"] is False
