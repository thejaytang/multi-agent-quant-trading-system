from __future__ import annotations

import argparse
import json
import mimetypes
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

from system.runtime.agent_router import AgentRouter
from system.workflows.daily_compounding_workflow import run as run_daily_compounding


ROOT = Path(__file__).resolve().parents[2]
WEB_ROOT = ROOT / "apps" / "web"


def api_get(path: str, root: str | Path | None = None) -> tuple[int, dict[str, Any]]:
    root_dir = Path(root or ROOT).resolve()
    if path == "/api/health":
        return HTTPStatus.OK, {"status": "ok", "source": "apps.api.server"}
    if path == "/api/cockpit":
        return HTTPStatus.OK, _load_cockpit(root_dir)
    snapshot = _load_cockpit(root_dir)
    if path == "/api/market-lens":
        return HTTPStatus.OK, snapshot.get("market_lens", {})
    if path == "/api/strategies":
        return HTTPStatus.OK, snapshot.get("strategy_center", {})
    if path == "/api/portfolio-risk":
        return HTTPStatus.OK, snapshot.get("portfolio_risk", {})
    if path == "/api/execution":
        return HTTPStatus.OK, snapshot.get("execution_desk", {})
    if path == "/api/performance":
        return HTTPStatus.OK, snapshot.get("performance_journal", {})
    if path == "/api/agent-trace":
        return HTTPStatus.OK, snapshot.get("agent_trace", {})
    return HTTPStatus.NOT_FOUND, {"error": "not_found", "path": path}


def api_post(path: str, body: dict[str, Any], root: str | Path | None = None) -> tuple[int, dict[str, Any]]:
    root_dir = Path(root or ROOT).resolve()
    if path == "/api/chat":
        message = str(body.get("message", "")).strip()
        if not message:
            return HTTPStatus.BAD_REQUEST, {"error": "message is required"}
        return HTTPStatus.OK, AgentRouter(root_dir).route(message)
    if path == "/api/actions/confirm":
        return HTTPStatus.ACCEPTED, {
            "status": "recorded_stub",
            "message": "Human confirmation is recorded as a local stub only. No broker execution was submitted.",
            "source": "apps.api.server",
        }
    if path == "/api/run/daily-compounding":
        result = run_daily_compounding(root=root_dir)
        return HTTPStatus.OK, result
    return HTTPStatus.NOT_FOUND, {"error": "not_found", "path": path}


def _load_cockpit(root_dir: Path) -> dict[str, Any]:
    path = root_dir / "outputs" / "compounding" / "latest.json"
    if not path.exists():
        result = run_daily_compounding(root=root_dir)
        path = Path(result["latest_snapshot"])
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {"status": "blocked", "error": "invalid cockpit snapshot json", "path": str(path)}
    return payload if isinstance(payload, dict) else {"status": "blocked", "error": "cockpit snapshot must be an object"}


class CockpitRequestHandler(BaseHTTPRequestHandler):
    def do_GET(self) -> None:
        parsed = urlparse(self.path)
        if parsed.path.startswith("/api/"):
            status, payload = api_get(parsed.path, ROOT)
            self._send_json(status, payload)
            return
        self._send_static(parsed.path)

    def do_POST(self) -> None:
        parsed = urlparse(self.path)
        if not parsed.path.startswith("/api/"):
            self._send_json(HTTPStatus.NOT_FOUND, {"error": "not_found", "path": parsed.path})
            return
        try:
            body = self.rfile.read(int(self.headers.get("Content-Length", "0") or 0))
            payload = json.loads(body.decode("utf-8") or "{}")
        except json.JSONDecodeError:
            self._send_json(HTTPStatus.BAD_REQUEST, {"error": "invalid_json"})
            return
        status, response = api_post(parsed.path, payload, ROOT)
        self._send_json(status, response)

    def log_message(self, format: str, *args: Any) -> None:
        return

    def _send_json(self, status: int, payload: dict[str, Any]) -> None:
        body = json.dumps(payload, indent=2).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Cache-Control", "no-store")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _send_static(self, request_path: str) -> None:
        relative = "index.html" if request_path in {"", "/"} else request_path.lstrip("/")
        path = (WEB_ROOT / relative).resolve()
        if not path.is_file() or not _is_under(path, WEB_ROOT):
            path = WEB_ROOT / "index.html"
        content = path.read_bytes()
        content_type = mimetypes.guess_type(path.name)[0] or "application/octet-stream"
        self.send_response(HTTPStatus.OK)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(content)))
        self.end_headers()
        self.wfile.write(content)


def _is_under(path: Path, parent: Path) -> bool:
    try:
        path.relative_to(parent.resolve())
        return True
    except ValueError:
        return False


def main() -> None:
    parser = argparse.ArgumentParser(description="Run the local compounding cockpit server.")
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", default=8765, type=int)
    args = parser.parse_args()
    server = ThreadingHTTPServer((args.host, args.port), CockpitRequestHandler)
    print(f"Compounding Cockpit running at http://{args.host}:{args.port}")
    server.serve_forever()


if __name__ == "__main__":
    main()
