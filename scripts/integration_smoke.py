from __future__ import annotations

import argparse
import json
import re
import sys
import threading
import time
from datetime import UTC, date, datetime, timedelta
from pathlib import Path
from typing import Any
from urllib.error import HTTPError, URLError

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from integrations.fred.client import FredClient
from integrations.ibkr.client import IbkrClient
from integrations.massive.client import MassiveClient
from integrations.quantconnect.client import QuantconnectClient
from integrations.sec_edgar.client import SecEdgarClient
from system.schemas._validation import default_metadata

IBKR_WARNING_CODES = {2103, 2104, 2105, 2106, 2107, 2108, 2158}


def _market_window() -> tuple[str, str]:
    end = date.today() - timedelta(days=3)
    start = end - timedelta(days=10)
    return start.isoformat(), end.isoformat()


def _redact_identifier(value: str | None) -> str | None:
    if not value:
        return None
    if len(value) <= 6:
        return "***"
    return f"{value[:3]}...{value[-3:]}"


def _ibkr_errors(errors: list[tuple[int, int, str]]) -> list[dict[str, Any]]:
    summaries = []
    for req_id, code, message in errors:
        safe_message = re.sub(r"\b[UF]\d{4,}\b", lambda match: _redact_identifier(match.group(0)) or "***", message)
        summaries.append(
            {
                "req_id": req_id,
                "code": code,
                "message": safe_message[:180],
            }
        )
    return summaries


def _result(name: str, ok: bool, details: dict[str, Any]) -> dict[str, Any]:
    return {"name": name, "ok": ok, "details": details}


def _ok(name: str, details: dict[str, Any]) -> dict[str, Any]:
    return _result(name, True, details)


def _fail(name: str, exc: BaseException) -> dict[str, Any]:
    message = str(exc)
    if isinstance(exc, HTTPError):
        message = f"HTTP {exc.code}: {exc.reason}"
    if isinstance(exc, URLError):
        message = f"URL error: {exc.reason}"
    return {"name": name, "ok": False, "error_type": type(exc).__name__, "error": message[:500]}


def check_massive(root: Path) -> dict[str, Any]:
    client = MassiveClient(root=root, config={"enable_external_requests": True})
    start, end = _market_window()
    response = client.fetch_daily_ohlcv("AAPL", start, end)
    news = client.fetch_news("AAPL", limit=3)
    details = {
        "ohlcv_status": response.get("status"),
        "ohlcv_http_status": response.get("_http_status"),
        "ohlcv_results_count": response.get("resultsCount", len(response.get("results", []))),
        "news_status": news.get("status"),
        "news_http_status": news.get("_http_status"),
        "news_count": news.get("count", len(news.get("results", []))),
    }
    ok = (
        details["ohlcv_http_status"] == 200
        and details["news_http_status"] == 200
        and str(details["ohlcv_status"]).upper() == "OK"
        and str(details["news_status"]).upper() == "OK"
    )
    return _result(
        "massive",
        ok,
        details,
    )


def check_fred(root: Path) -> dict[str, Any]:
    client = FredClient(root=root, config={"enable_external_requests": True})
    response = client.fetch_series_observations("DGS10")
    observations = response.get("observations", [])
    details = {
        "http_status": response.get("_http_status"),
        "series_id": "DGS10",
        "observation_count": len(observations),
        "latest_date_present": bool(observations[-1].get("date")) if observations else False,
    }
    return _result(
        "fred",
        details["http_status"] == 200 and details["observation_count"] > 0 and details["latest_date_present"],
        details,
    )


def check_sec_edgar(root: Path) -> dict[str, Any]:
    client = SecEdgarClient(root=root, config={"enable_external_requests": True})
    response = client.fetch_company_facts("0000320193")
    details = {
        "http_status": response.get("_http_status"),
        "cik": response.get("cik"),
        "entity_name_present": bool(response.get("entityName")),
        "facts_present": bool(response.get("facts")),
    }
    return _result(
        "sec_edgar",
        details["http_status"] == 200 and details["entity_name_present"] and details["facts_present"],
        details,
    )


def check_quantconnect(root: Path) -> dict[str, Any]:
    client = QuantconnectClient(root=root, config={"enable_external_requests": True})
    response = client.authenticate()
    details = {
        "http_status": response.get("_http_status"),
        "success": response.get("success"),
    }
    return _result(
        "quantconnect",
        details["http_status"] == 200 and details["success"] is True,
        details,
    )


def check_ibkr(root: Path, include_account_summary: bool) -> dict[str, Any]:
    client = IbkrClient(root=root, config={"enable_external_requests": True})
    profile = client.connection_profile()
    if not include_account_summary:
        return _check_ibkr_time(profile)
    return _check_ibkr_account_read(profile)


def _check_ibkr_time(profile: dict[str, Any]) -> dict[str, Any]:
    from ibapi.client import EClient
    from ibapi.wrapper import EWrapper

    class TimeApp(EWrapper, EClient):
        def __init__(self) -> None:
            EClient.__init__(self, self)
            self.ready = threading.Event()
            self.done = threading.Event()
            self.server_time: int | None = None
            self.warnings: list[int] = []
            self.errors: list[tuple[int, int, str]] = []

        def nextValidId(self, orderId: int) -> None:
            self.ready.set()
            self.reqCurrentTime()

        def currentTime(self, time_: int) -> None:
            self.server_time = time_
            self.done.set()
            self.disconnect()

        def error(self, reqId, errorCode, errorString, advancedOrderRejectJson="") -> None:
            if errorCode in IBKR_WARNING_CODES:
                self.warnings.append(errorCode)
                return
            self.errors.append((reqId, errorCode, errorString))
            self.done.set()

    app = TimeApp()
    app.connect(profile["host"], profile["port"], clientId=profile["client_id"] + 10)
    thread = threading.Thread(target=app.run, daemon=True)
    thread.start()
    ready = app.ready.wait(10)
    done = app.done.wait(10)
    app.disconnect()
    details = {
        "connected": bool(ready and done and app.server_time),
        "server_time_received": bool(app.server_time),
        "account": profile.get("account_id"),
        "port": profile["port"],
        "read_only": profile["read_only"],
        "warning_codes": app.warnings,
        "error_count": len(app.errors),
        "errors": _ibkr_errors(app.errors),
    }
    return _result(
        "ibkr",
        details["connected"] and details["server_time_received"] and details["read_only"] and details["error_count"] == 0,
        details,
    )


def _check_ibkr_account_read(profile: dict[str, Any]) -> dict[str, Any]:
    from ibapi.client import EClient
    from ibapi.wrapper import EWrapper

    class AccountApp(EWrapper, EClient):
        def __init__(self) -> None:
            EClient.__init__(self, self)
            self.ready = threading.Event()
            self.done = threading.Event()
            self.server_time: int | None = None
            self.raw_accounts: list[str] = []
            self.rows: list[tuple[str, str, str]] = []
            self.warnings: list[int] = []
            self.errors: list[tuple[int, int, str]] = []

        def nextValidId(self, orderId: int) -> None:
            self.ready.set()
            self.reqCurrentTime()
            self.reqManagedAccts()

        def currentTime(self, time_: int) -> None:
            self.server_time = time_

        def managedAccounts(self, accountsList: str) -> None:
            self.raw_accounts = [account for account in accountsList.split(",") if account]
            if not self.raw_accounts:
                self.done.set()
                return
            self.reqAccountUpdates(True, self.raw_accounts[0])

        def updateAccountValue(self, key: str, val: str, currency: str, accountName: str) -> None:
            self.rows.append((accountName, key, currency))

        def accountDownloadEnd(self, accountName: str) -> None:
            self.done.set()
            self.reqAccountUpdates(False, accountName)
            self.disconnect()

        def error(self, reqId, errorCode, errorString, advancedOrderRejectJson="") -> None:
            if errorCode in IBKR_WARNING_CODES:
                self.warnings.append(errorCode)
                return
            self.errors.append((reqId, errorCode, errorString))
            if errorCode >= 500:
                self.done.set()

    app = AccountApp()
    app.connect(profile["host"], profile["port"], clientId=profile["client_id"] + 11)
    thread = threading.Thread(target=app.run, daemon=True)
    thread.start()
    ready = app.ready.wait(10)
    done = app.done.wait(20)
    app.disconnect()
    tags = sorted({tag for _, tag, _ in app.rows})
    currencies = sorted({currency for _, _, currency in app.rows if currency})
    accounts = sorted({_redact_identifier(account) for account in app.raw_accounts if account})
    details = {
        "connected": bool(ready and done),
        "server_time_received": bool(app.server_time),
        "managed_accounts_count": len(app.raw_accounts),
        "managed_accounts": accounts,
        "account_update_rows": len(app.rows),
        "account_value_tags": tags,
        "currencies_returned": currencies,
        "configured_account": profile.get("account_id"),
        "port": profile["port"],
        "read_only": profile["read_only"],
        "warning_codes": app.warnings,
        "error_count": len(app.errors),
        "errors": _ibkr_errors(app.errors),
    }
    return _result(
        "ibkr",
        details["connected"]
        and details["server_time_received"]
        and details["managed_accounts_count"] > 0
        and details["account_update_rows"] > 0
        and details["read_only"]
        and details["error_count"] == 0,
        details,
    )


def run(root: Path, include_ibkr_account_summary: bool = True) -> dict[str, Any]:
    checks = [
        ("massive", lambda: check_massive(root)),
        ("fred", lambda: check_fred(root)),
        ("sec_edgar", lambda: check_sec_edgar(root)),
        ("quantconnect", lambda: check_quantconnect(root)),
        ("ibkr", lambda: check_ibkr(root, include_ibkr_account_summary)),
    ]
    results = []
    for name, check in checks:
        try:
            results.append(check())
        except BaseException as exc:
            results.append(_fail(name, exc))
    return {
        "metadata": default_metadata("integration_smoke", "scripts.integration_smoke", "LeaderAgent"),
        "created_at": datetime.now(UTC).isoformat(),
        "live_trading_enabled": False,
        "checks": results,
        "all_ok": all(item.get("ok") for item in results),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", default="workspace/active_runs/integration_smoke/latest.json")
    parser.add_argument("--skip-ibkr-account-summary", action="store_true")
    args = parser.parse_args()
    root = PROJECT_ROOT
    report = run(root, include_ibkr_account_summary=not args.skip_ibkr_account_summary)
    output_path = root / args.output
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
