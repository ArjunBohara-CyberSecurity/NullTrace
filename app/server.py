from __future__ import annotations

import argparse
import json
import os
import sys
import time
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any
from urllib.parse import parse_qs, urlparse

from app.api.analyze.route import analyze_payload, stream_events
from app.ui import build_index
from lib.incident_engine.engine import analyze_incident
from lib.integrations.connectors import get_connector_registry
from lib.openrouter.client import OpenRouterClient
from lib.realtime.telemetry import get_realtime_feed
from styles.theme import build_css


ROOT = Path(__file__).resolve().parent.parent
ENV_PATH = ROOT / ".env.local"
SERVER_STATE_PATH = ROOT / ".nulltrace-server.json"


def load_env_file(path: Path = ENV_PATH) -> None:
    if not path.exists():
        return

    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        key = key.strip()
        value = value.strip().strip('"').strip("'")
        if key:
            os.environ[key] = value


def json_bytes(payload: Any) -> bytes:
    return json.dumps(payload, separators=(",", ":"), ensure_ascii=False).encode("utf-8")


class NullTraceHandler(BaseHTTPRequestHandler):
    server_version = "NULLTRACE/1.0"

    def log_message(self, format: str, *args: Any) -> None:
        sys.stdout.write("[%s] %s\n" % (self.log_date_time_string(), format % args))
        sys.stdout.flush()

    def do_GET(self) -> None:
        parsed = urlparse(self.path)
        path = parsed.path.rstrip("/") or "/"

        if path == "/":
            context = get_realtime_feed().snapshot()
            analysis = analyze_incident(context)
            self.respond_html(build_index(context, analysis))
            return

        if path == "/styles/nulltrace.css":
            self.respond(build_css().encode("utf-8"), "text/css; charset=utf-8")
            return

        if path == "/api/context":
            self.respond_json(get_realtime_feed().advance())
            return

        if path == "/api/integrations":
            context = get_realtime_feed().advance()
            self.respond_json(
                {
                    "connectors": context.get("connectors", []),
                    "signalLedger": context.get("signalLedger", []),
                    "agentPipeline": context.get("agentPipeline", []),
                    "analysis": analyze_incident(context),
                }
            )
            return

        if path == "/api/connectors":
            self.respond_json({"connectors": get_connector_registry().statuses()})
            return

        if path == "/api/openrouter/status":
            self.respond_json(OpenRouterClient().status())
            return

        if path == "/api/telemetry/stream":
            self.respond_telemetry_sse()
            return

        if path == "/api/analyze/stream":
            query = parse_qs(parsed.query)
            model = query.get("model", [None])[0]
            self.respond_sse(model=model)
            return

        self.respond_json({"error": "not_found", "path": path}, status=HTTPStatus.NOT_FOUND)

    def do_POST(self) -> None:
        parsed = urlparse(self.path)
        path = parsed.path.rstrip("/") or "/"

        if path == "/api/connectors/connect":
            payload = self.read_json_body()
            provider = str(payload.get("provider", ""))
            credentials = payload.get("credentials") if isinstance(payload.get("credentials"), dict) else {}
            try:
                state = get_connector_registry().connect(provider, credentials)
            except ValueError as exc:
                self.respond_json({"error": str(exc)}, status=HTTPStatus.BAD_REQUEST)
                return
            context = get_realtime_feed().refresh_connectors()
            self.respond_json({"state": state, "context": context, "analysis": analyze_incident(context)})
            return

        if path == "/api/connectors/disconnect":
            payload = self.read_json_body()
            provider = str(payload.get("provider", ""))
            try:
                state = get_connector_registry().disconnect(provider)
            except ValueError as exc:
                self.respond_json({"error": str(exc)}, status=HTTPStatus.BAD_REQUEST)
                return
            context = get_realtime_feed().refresh_connectors()
            self.respond_json({"state": state, "context": context, "analysis": analyze_incident(context)})
            return

        if path == "/api/connectors/sync":
            payload = self.read_json_body()
            provider = str(payload.get("provider", ""))
            try:
                result = get_realtime_feed().sync_provider(provider)
            except ValueError as exc:
                self.respond_json({"error": str(exc)}, status=HTTPStatus.BAD_REQUEST)
                return
            context = result["context"]
            self.respond_json(
                {
                    "state": result.get("state"),
                    "signals": result.get("signals", []),
                    "context": context,
                    "analysis": analyze_incident(context),
                }
            )
            return

        if path != "/api/analyze":
            self.respond_json({"error": "not_found", "path": path}, status=HTTPStatus.NOT_FOUND)
            return

        payload = self.read_json_body()
        self.respond_json(analyze_payload(payload))

    def read_json_body(self) -> dict[str, Any]:
        length = int(self.headers.get("Content-Length", "0") or "0")
        raw_body = self.rfile.read(length) if length else b"{}"
        try:
            payload = json.loads(raw_body.decode("utf-8"))
        except json.JSONDecodeError:
            self.respond_json({"error": "invalid_json"}, status=HTTPStatus.BAD_REQUEST)
            return {}
        return payload if isinstance(payload, dict) else {}

    def respond_telemetry_sse(self) -> None:
        feed = get_realtime_feed()
        self.send_response(HTTPStatus.OK)
        self.send_header("Content-Type", "text/event-stream; charset=utf-8")
        self.send_header("Cache-Control", "no-cache")
        self.send_header("Connection", "keep-alive")
        self.end_headers()

        def send(event: dict[str, Any]) -> None:
            message = "data: " + json.dumps(event, ensure_ascii=False) + "\n\n"
            self.wfile.write(message.encode("utf-8"))
            self.wfile.flush()

        try:
            send({"type": "connected", "source": "local connector status"})
            while True:
                context = feed.advance()
                send({"type": "snapshot", "context": context, "analysis": analyze_incident(context)})
                time.sleep(5.0)
        except (BrokenPipeError, ConnectionResetError):
            self.close_connection = True

    def respond_sse(self, model: str | None = None) -> None:
        self.close_connection = True
        self.send_response(HTTPStatus.OK)
        self.send_header("Content-Type", "text/event-stream; charset=utf-8")
        self.send_header("Cache-Control", "no-cache")
        self.send_header("Connection", "close")
        self.end_headers()

        def send(event: dict[str, Any]) -> None:
            message = "data: " + json.dumps(event, ensure_ascii=False) + "\n\n"
            self.wfile.write(message.encode("utf-8"))
            self.wfile.flush()

        try:
            for event in stream_events(model=model):
                send(event)
        except (BrokenPipeError, ConnectionResetError):
            self.close_connection = True
        self.close_connection = True

    def respond_html(self, html: str) -> None:
        self.respond(html.encode("utf-8"), "text/html; charset=utf-8")

    def respond_json(self, payload: Any, status: HTTPStatus = HTTPStatus.OK) -> None:
        self.respond(json_bytes(payload), "application/json; charset=utf-8", status=status)

    def respond(
        self,
        body: bytes,
        content_type: str,
        status: HTTPStatus = HTTPStatus.OK,
    ) -> None:
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(body)


def create_server(host: str, port: int, attempts: int = 20) -> ThreadingHTTPServer:
    for candidate in range(port, port + attempts):
        try:
            return ThreadingHTTPServer((host, candidate), NullTraceHandler)
        except OSError:
            continue
    raise RuntimeError(f"Unable to bind NULLTRACE on ports {port}-{port + attempts - 1}")


def run(host: str, port: int) -> None:
    load_env_file()
    get_realtime_feed().advance()
    server = create_server(host, port)
    actual_host, actual_port = server.server_address
    url = f"http://{actual_host}:{actual_port}"
    SERVER_STATE_PATH.write_text(
        json.dumps({"url": url, "host": actual_host, "port": actual_port, "pid": os.getpid()}, indent=2),
        encoding="utf-8",
    )
    openrouter_status = OpenRouterClient().status()
    print(f"NULLTRACE operational at {url}", flush=True)
    print(
        f"OpenRouter configured={openrouter_status['configured']} model={openrouter_status['model']}",
        flush=True,
    )

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nNULLTRACE shutdown acknowledged.", flush=True)
    finally:
        server.server_close()


def main() -> None:
    parser = argparse.ArgumentParser(description="Run the NULLTRACE Python incident intelligence platform.")
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", default=8765, type=int)
    args = parser.parse_args()
    run(args.host, args.port)
