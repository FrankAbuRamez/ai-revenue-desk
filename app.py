"""Zero-dependency local web demo for the AI Revenue Desk."""

from __future__ import annotations

import argparse
import json
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any

from revenue_desk import IntakeError, RevenueDesk

ROOT = Path(__file__).resolve().parent
WEB_ROOT = ROOT / "web"
DESK = RevenueDesk("Northstar Home Services")


def handle_api(method: str, path: str, body: bytes, desk: RevenueDesk) -> tuple[int, dict[str, Any]]:
    if method == "GET" and path == "/api/state":
        return HTTPStatus.OK, {"summary": desk.summary(), "leads": desk.leads()}

    if method == "POST" and path == "/api/intake":
        try:
            payload = json.loads(body.decode("utf-8"))
            if not isinstance(payload, dict):
                raise ValueError("Request must be an object")
            lead = desk.intake(payload)
        except (UnicodeDecodeError, json.JSONDecodeError, ValueError, IntakeError) as exc:
            return HTTPStatus.BAD_REQUEST, {"error": str(exc)}
        return HTTPStatus.CREATED, {"lead": lead, "summary": desk.summary()}

    return HTTPStatus.NOT_FOUND, {"error": "Not found"}


class RevenueDeskHandler(BaseHTTPRequestHandler):
    server_version = "RevenueDeskDemo/0.1"

    def _json(self, status: int, payload: dict[str, Any]) -> None:
        encoded = json.dumps(payload).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(encoded)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(encoded)

    def do_GET(self) -> None:
        if self.path.startswith("/api/"):
            status, payload = handle_api("GET", self.path, b"", DESK)
            self._json(status, payload)
            return

        file_path = WEB_ROOT / ("index.html" if self.path in ("/", "/index.html") else self.path.lstrip("/"))
        try:
            resolved = file_path.resolve(strict=True)
            resolved.relative_to(WEB_ROOT.resolve())
        except (FileNotFoundError, ValueError):
            self.send_error(HTTPStatus.NOT_FOUND)
            return
        if not resolved.is_file():
            self.send_error(HTTPStatus.NOT_FOUND)
            return
        content = resolved.read_bytes()
        content_type = "text/html; charset=utf-8" if resolved.suffix == ".html" else "text/plain; charset=utf-8"
        self.send_response(HTTPStatus.OK)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(content)))
        self.end_headers()
        self.wfile.write(content)

    def do_POST(self) -> None:
        length = min(int(self.headers.get("Content-Length", "0")), 64_000)
        body = self.rfile.read(length)
        status, payload = handle_api("POST", self.path, body, DESK)
        self._json(status, payload)

    def log_message(self, fmt: str, *args: object) -> None:
        print(f"[revenue-desk] {self.address_string()} {fmt % args}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Run the local AI Revenue Desk demo")
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8787)
    args = parser.parse_args()
    server = ThreadingHTTPServer((args.host, args.port), RevenueDeskHandler)
    print(f"AI Revenue Desk demo: http://{args.host}:{args.port}")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()


if __name__ == "__main__":
    main()
