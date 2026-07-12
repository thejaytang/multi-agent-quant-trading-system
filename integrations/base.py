from __future__ import annotations

import os
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any
from urllib.parse import urlencode
from urllib.request import Request, urlopen


class ExternalRequestDisabled(RuntimeError):
    """Raised when a caller tries to use a real external request before enabling it."""


def _parse_env_file(path: Path) -> dict[str, str]:
    if not path.exists():
        return {}
    values: dict[str, str] = {}
    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        key = key.strip()
        value = value.strip().strip('"').strip("'")
        if key:
            values[key] = value
    return values


def load_local_env(root: str | Path | None = None) -> dict[str, str]:
    """Load local env files without mutating process env.

    Precedence is process env, then `.env.local`, then `.env`.
    `.env.example` is intentionally not loaded because it has no secrets.
    """

    root_path = Path(root or Path.cwd())
    file_values: dict[str, str] = {}
    for name in (".env", ".env.local"):
        file_values.update(_parse_env_file(root_path / name))
    merged = dict(file_values)
    merged.update({key: value for key, value in os.environ.items() if value})
    return merged


def redacted(value: str | None) -> str | None:
    if not value:
        return None
    if len(value) <= 8:
        return "***"
    return f"{value[:4]}...{value[-4:]}"


def as_bool(value: Any, default: bool = False) -> bool:
    if value is None:
        return default
    if isinstance(value, bool):
        return value
    return str(value).strip().lower() in {"1", "true", "yes", "on"}


@dataclass(frozen=True)
class RequestSpec:
    method: str
    url: str
    params: dict[str, Any]
    headers: dict[str, str]

    def sanitized(self) -> dict[str, Any]:
        return {
            "method": self.method,
            "url": self.url,
            "params": {
                key: ("***" if "key" in key.lower() or "token" in key.lower() else value)
                for key, value in self.params.items()
            },
            "headers": {
                key: ("***" if key.lower() in {"authorization", "token"} else value)
                for key, value in self.headers.items()
            },
        }


class IntegrationClient:
    integration_name = "integration"
    status = "configured_stub"
    required_env: tuple[str, ...] = ()

    def __init__(self, config: dict[str, Any] | None = None, root: str | Path | None = None) -> None:
        self.config = config or {}
        self.root = Path(root or Path.cwd())
        self.env = load_local_env(self.root)

    @property
    def external_requests_enabled(self) -> bool:
        configured = self.config.get("enable_external_requests")
        env_value = self.env.get("EXTERNAL_API_REQUESTS_ENABLED")
        return as_bool(configured if configured is not None else env_value, default=False)

    @property
    def live_trading_enabled(self) -> bool:
        configured = self.config.get("live_trading_enabled")
        env_value = self.env.get("LIVE_TRADING_ENABLED")
        return as_bool(configured if configured is not None else env_value, default=False)

    def credential(self, env_name: str) -> str | None:
        value = self.config.get(env_name) or self.env.get(env_name)
        return str(value) if value else None

    def missing_credentials(self) -> list[str]:
        return [name for name in self.required_env if not self.credential(name)]

    def configured_credentials(self) -> dict[str, str | None]:
        return {name: redacted(self.credential(name)) for name in self.required_env}

    def healthcheck(self) -> dict[str, Any]:
        missing = self.missing_credentials()
        return {
            "integration": self.integration_name,
            "status": "configured" if not missing else "missing_credentials",
            "external_connection": False,
            "external_requests_enabled": self.external_requests_enabled,
            "live_trading_enabled": self.live_trading_enabled,
            "missing_credentials": missing,
            "configured_credentials": self.configured_credentials(),
        }

    def require_external_requests_enabled(self) -> None:
        if not self.external_requests_enabled:
            raise ExternalRequestDisabled(
                f"{self.integration_name} external requests are disabled by default"
            )

    def request_json(self, spec: RequestSpec, body: dict[str, Any] | None = None, timeout: int = 20) -> dict[str, Any]:
        self.require_external_requests_enabled()
        url = spec.url
        if spec.params:
            url = f"{url}?{urlencode({key: value for key, value in spec.params.items() if value is not None})}"
        data = None
        headers = dict(spec.headers)
        if body is not None:
            data = json.dumps(body).encode("utf-8")
            headers.setdefault("Content-Type", "application/json")
        request = Request(url, data=data, headers=headers, method=spec.method)
        with urlopen(request, timeout=timeout) as response:
            payload = response.read().decode("utf-8")
            parsed = json.loads(payload) if payload else {}
            if isinstance(parsed, dict):
                parsed["_http_status"] = response.status
            return parsed
