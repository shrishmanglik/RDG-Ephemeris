"""Zero-dependency HTTP REST JSON API server with OpenAPI 3.1 specification.

Exposes the RDG-Ephemeris calculation engine over HTTP so any backend microservice,
web frontend, mobile app, or external webhook can query planetary positions,
complete Kundali charts, sunrise-anchored Panchanga, birth-time rectification,
multi-century planetary phenomena, and AI fact sheets via standard JSON requests.

Usage::

    rdg-ephemeris-api --host 127.0.0.1 --port 8765
    # or:
    ephemeris-oss serve --host 127.0.0.1 --port 8765
"""

from __future__ import annotations

import argparse
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json
import sys
from typing import Any, Mapping
from urllib.parse import urlparse

from ._version import __version__
from .mcp_server import MCP_TOOLS, execute_mcp_tool


def build_openapi_spec(server_url: str = "http://127.0.0.1:8765") -> dict[str, Any]:
    """Generate the OpenAPI 3.1.0 specification for the RDG-Ephemeris REST API."""
    return {
        "openapi": "3.1.0",
        "info": {
            "title": "RDG-Ephemeris Sovereign Astronomical & Jyotish REST API",
            "version": __version__,
            "description": (
                "Apache-2.0 deterministic planetary ephemeris and Vedic Jyotish calculation API "
                "backed by embedded NASA JPL DE440 Chebyshev polynomials (1550-2306 CE) and "
                "Vondrak-2011 long-term precession (3102 BCE-3000 CE)."
            ),
            "license": {
                "name": "Apache-2.0",
                "identifier": "Apache-2.0",
            },
        },
        "servers": [{"url": server_url}],
        "paths": {
            "/health": {
                "get": {
                    "summary": "Health and coverage status check",
                    "operationId": "getHealth",
                }
            },
            "/openapi.json": {
                "get": {
                    "summary": "OpenAPI 3.1 specification",
                    "operationId": "getOpenApiSpec",
                }
            },
            "/v1/tools": {
                "get": {
                    "summary": "List all available calculation tools and JSON schemas",
                    "operationId": "listTools",
                }
            },
            "/v1/positions": {
                "post": {
                    "summary": "Compute planetary positions (3102 BCE to 3000 CE)",
                    "operationId": "computePlanetaryPositions",
                }
            },
            "/v1/kundali": {
                "post": {
                    "summary": "Compute complete Vedic Kundali (D1-D60, Dashas, Shadbala, Ashtakavarga, Yogas)",
                    "operationId": "computeCompleteKundali",
                }
            },
            "/v1/panchanga": {
                "post": {
                    "summary": "Compute regional sunrise-anchored Drik Panchanga",
                    "operationId": "computePanchanga",
                }
            },
            "/v1/rectify": {
                "post": {
                    "summary": "Solve sub-second D1-D60 varga cusp margins and Kunda/Pranapada/Tattwa birth-time rectification",
                    "operationId": "rectifyBirthTime",
                }
            },
            "/v1/phenomena": {
                "post": {
                    "summary": "Scan multi-century Graha Yuddha (planetary wars), retrograde stations, and combustion",
                    "operationId": "scanPhenomena",
                }
            },
            "/v1/siddhanta-diff": {
                "post": {
                    "summary": "Compare classical Surya Siddhanta epicyclic positions against modern NASA JPL DE440",
                    "operationId": "compareSiddhanta",
                }
            },
            "/v1/fact-sheet": {
                "post": {
                    "summary": "Compile compact (<3 KB) SHA-256-sealed AI astrological fact sheet",
                    "operationId": "compileFactSheet",
                }
            },
            "/v1/verify-text": {
                "post": {
                    "summary": "Audit AI-generated astrological text for hallucinated placements",
                    "operationId": "verifyText",
                }
            },
        },
    }


_ROUTE_TO_TOOL: Mapping[str, str] = {
    "/v1/positions": "compute_planetary_positions",
    "/v1/kundali": "compute_complete_kundali",
    "/v1/panchanga": "compute_panchanga",
    "/v1/rectify": "rectify_birth_time_and_varga_cusps",
    "/v1/phenomena": "scan_planetary_wars_and_stations",
    "/v1/siddhanta-diff": "compare_surya_siddhanta_vs_de440",
    "/v1/fact-sheet": "compile_verified_ai_fact_sheet",
    "/v1/verify-text": "verify_ai_astrology_text",
}


def dispatch_api_request(
    method: str,
    path: str,
    body: Mapping[str, Any] | None = None,
) -> tuple[int, dict[str, Any]]:
    """Pure function dispatching an HTTP method + path + JSON body to `(status_code, payload)`."""
    clean_path = urlparse(path).path.rstrip("/") or "/"
    upper_method = method.upper()

    if upper_method == "GET":
        if clean_path in ("/", "/health"):
            return 200, {
                "status": "ok",
                "engine": "ephemeris-oss",
                "version": __version__,
                "license": "Apache-2.0",
                "embedded_de440_chebyshev_span_ce": "1550-2306",
                "historical_extended_span": "3102 BCE - 3000 CE",
                "endpoints": sorted(["/health", "/openapi.json", "/v1/tools", *_ROUTE_TO_TOOL.keys()]),
            }
        if clean_path == "/openapi.json":
            return 200, build_openapi_spec()
        if clean_path == "/v1/tools":
            return 200, {"tools": list(MCP_TOOLS)}
        return 404, {"error": f"Unknown GET endpoint: {clean_path}"}

    if upper_method == "POST":
        if clean_path in _ROUTE_TO_TOOL:
            tool_name = _ROUTE_TO_TOOL[clean_path]
            try:
                result = execute_mcp_tool(tool_name, body or {})
                return 200, result
            except Exception as exc:
                return 400, {"error": str(exc), "endpoint": clean_path}
        return 404, {"error": f"Unknown POST endpoint: {clean_path}"}

    return 405, {"error": f"Method not allowed: {upper_method}"}


class EphemerisAPIHandler(BaseHTTPRequestHandler):
    """Thread-safe HTTP handler serving the RDG-Ephemeris REST API with CORS headers."""

    def _send_json(self, status_code: int, payload: Mapping[str, Any]) -> None:
        encoded = json.dumps(payload, sort_keys=True).encode("utf-8")
        self.send_response(status_code)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(encoded)))
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type, Authorization")
        self.end_headers()
        self.wfile.write(encoded)

    def do_OPTIONS(self) -> None:  # noqa: N802
        self._send_json(200, {"status": "ok"})

    def do_GET(self) -> None:  # noqa: N802
        status, payload = dispatch_api_request("GET", self.path)
        self._send_json(status, payload)

    def do_POST(self) -> None:  # noqa: N802
        length = int(self.headers.get("Content-Length", "0") or "0")
        raw_body = self.rfile.read(length) if length > 0 else b"{}"
        try:
            parsed = json.loads(raw_body.decode("utf-8")) if raw_body else {}
        except json.JSONDecodeError as exc:
            self._send_json(400, {"error": f"Invalid JSON body: {exc}"})
            return
        status, payload = dispatch_api_request(
            "POST",
            self.path,
            parsed if isinstance(parsed, Mapping) else {},
        )
        self._send_json(status, payload)

    def log_message(self, format: str, *args: Any) -> None:  # noqa: A002
        return


def create_http_server(host: str = "127.0.0.1", port: int = 8765) -> ThreadingHTTPServer:
    """Create a bound ``ThreadingHTTPServer`` instance (useful for tests or embedding)."""
    return ThreadingHTTPServer((host, int(port)), EphemerisAPIHandler)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="rdg-ephemeris-api",
        description="Run the RDG-Ephemeris HTTP REST JSON API server.",
    )
    parser.add_argument("--host", default="127.0.0.1", help="Bind address (default: 127.0.0.1)")
    parser.add_argument("--port", type=int, default=8765, help="Bind port (default: 8765)")
    parser.add_argument("--dump-openapi", action="store_true", help="Print OpenAPI 3.1 JSON and exit")
    args = parser.parse_args(argv)

    if args.dump_openapi:
        print(json.dumps(build_openapi_spec(f"http://{args.host}:{args.port}"), indent=2, sort_keys=True))
        return 0

    server = create_http_server(args.host, args.port)
    actual_host, actual_port = server.server_address[:2]
    print(f"RDG-Ephemeris REST API listening on http://{actual_host}:{actual_port}")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
