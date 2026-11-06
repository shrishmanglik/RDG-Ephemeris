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
import copy
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json
import sys
from typing import Any, Mapping
from urllib.parse import urlparse

from ._version import __version__
from .mcp_server import MCP_TOOLS, execute_mcp_tool


def build_openapi_spec(server_url: str = "http://127.0.0.1:8765") -> dict[str, Any]:
    """Generate the OpenAPI 3.1.0 specification for the RDG-Ephemeris REST API."""
    tool_schemas: dict[str, Mapping[str, Any]] = {
        str(t["name"]): t.get("inputSchema", {"type": "object"})
        for t in MCP_TOOLS
    }

    def _request_body(tool_name: str) -> dict[str, Any]:
        return {
            "required": True,
            "content": {
                "application/json": {
                    "schema": copy.deepcopy(dict(tool_schemas.get(tool_name, {"type": "object"}))),
                }
            },
        }

    def _get_responses() -> dict[str, Any]:
        return {
            "200": {
                "description": "JSON response payload",
                "content": {"application/json": {"schema": {"type": "object"}}},
            }
        }

    def _post_responses() -> dict[str, Any]:
        return {
            "200": {
                "description": "Deterministic calculation result with SHA-256 receipt",
                "content": {"application/json": {"schema": {"type": "object"}}},
            },
            "400": {
                "description": "Invalid input parameters or malformed JSON request",
                "content": {"application/json": {"schema": {"type": "object"}}},
            },
            "413": {
                "description": "Request body exceeds maximum allowed size (1 MB)",
                "content": {"application/json": {"schema": {"type": "object"}}},
            },
        }

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
                    "responses": _get_responses(),
                }
            },
            "/openapi.json": {
                "get": {
                    "summary": "OpenAPI 3.1 specification",
                    "operationId": "getOpenApiSpec",
                    "responses": _get_responses(),
                }
            },
            "/v1/tools": {
                "get": {
                    "summary": "List all available calculation tools and JSON schemas",
                    "operationId": "listTools",
                    "responses": _get_responses(),
                }
            },
            "/v1/positions": {
                "post": {
                    "summary": "Compute planetary positions (3102 BCE to 3000 CE)",
                    "operationId": "computePlanetaryPositions",
                    "requestBody": _request_body("compute_planetary_positions"),
                    "responses": _post_responses(),
                }
            },
            "/v1/kundali": {
                "post": {
                    "summary": "Compute complete Vedic Kundali (D1-D60, Dashas, Shadbala, Ashtakavarga, Yogas)",
                    "operationId": "computeCompleteKundali",
                    "requestBody": _request_body("compute_complete_kundali"),
                    "responses": _post_responses(),
                }
            },
            "/v1/panchanga": {
                "post": {
                    "summary": "Compute regional sunrise-anchored Drik Panchanga",
                    "operationId": "computePanchanga",
                    "requestBody": _request_body("compute_panchanga"),
                    "responses": _post_responses(),
                }
            },
            "/v1/rectify": {
                "post": {
                    "summary": "Solve sub-second D1-D60 varga cusp margins and Kunda/Pranapada/Tattwa birth-time rectification",
                    "operationId": "rectifyBirthTime",
                    "requestBody": _request_body("rectify_birth_time_and_varga_cusps"),
                    "responses": _post_responses(),
                }
            },
            "/v1/phenomena": {
                "post": {
                    "summary": "Scan multi-century Graha Yuddha (planetary wars), retrograde stations, and combustion",
                    "operationId": "scanPhenomena",
                    "requestBody": _request_body("scan_planetary_wars_and_stations"),
                    "responses": _post_responses(),
                }
            },
            "/v1/siddhanta-diff": {
                "post": {
                    "summary": "Compare classical Surya Siddhanta epicyclic positions against modern NASA JPL DE440",
                    "operationId": "compareSiddhanta",
                    "requestBody": _request_body("compare_surya_siddhanta_vs_de440"),
                    "responses": _post_responses(),
                }
            },
            "/v1/fact-sheet": {
                "post": {
                    "summary": "Compile compact (<3 KB) SHA-256-sealed AI astrological fact sheet",
                    "operationId": "compileFactSheet",
                    "requestBody": _request_body("compile_verified_ai_fact_sheet"),
                    "responses": _post_responses(),
                }
            },
            "/v1/verify-text": {
                "post": {
                    "summary": "Audit AI-generated astrological text for hallucinated placements",
                    "operationId": "verifyText",
                    "requestBody": _request_body("verify_ai_astrology_text"),
                    "responses": _post_responses(),
                }
            },
            "/v1/fingerprint": {
                "post": {
                    "summary": (
                        "Compute personalized 16-Varga harmonic phase vector, domain clock-confidence "
                        "decay, topocentric Digbala vector, and 8-Kaksha Ashtakavarga transit resonance"
                    ),
                    "operationId": "computePersonalizedFingerprint",
                    "requestBody": _request_body("compute_personalized_astro_fingerprint"),
                    "responses": _post_responses(),
                }
            },
            "/v1/yogatara": {
                "post": {
                    "summary": (
                        "Propagate 30 Gaia/Hipparcos Yogataras and detect Tara Bheda, "
                        "Rohini Shakata Bheda, and Kalansha heliacal visibility"
                    ),
                    "operationId": "evaluateYogataraStellarBheda",
                    "requestBody": _request_body("evaluate_yogatara_stellar_bheda"),
                    "responses": _post_responses(),
                }
            },
            "/v1/mahapata": {
                "post": {
                    "summary": (
                        "Solve exact Surya Siddhanta Vyatipata and Vaidhriti Mahapata "
                        "solar-lunar declination equality windows"
                    ),
                    "operationId": "solveKrantisamyaMahapata",
                    "requestBody": _request_body("solve_krantisamya_mahapata"),
                    "responses": _post_responses(),
                }
            },
            "/v1/inverse-date": {
                "post": {
                    "summary": (
                        "Inverse Sky-to-Date 'Astronomical Time-Machine' solver across 3102 BCE to 3000 CE"
                    ),
                    "operationId": "solveInverseChartDate",
                    "requestBody": _request_body("solve_inverse_chart_date"),
                    "responses": _post_responses(),
                }
            },
            "/v1/triple-lock": {
                "post": {
                    "summary": (
                        "Compute Triple-Lock Life-Event Convergence (Multi-Dasha + Guru-Shani Double Transit "
                        "+ Ashtakavarga 8-Kakshya & Bhrigu Bindu)"
                    ),
                    "operationId": "computeTripleLockConvergence",
                    "requestBody": _request_body("compute_triple_lock_convergence"),
                    "responses": _post_responses(),
                }
            },
            "/v1/human-ephemeris": {
                "post": {
                    "summary": (
                        "Generate Human-Readable Classical Ephemeris & Jyotish Academy Manual Calculation Compendium"
                    ),
                    "operationId": "generateHumanManualEphemeris",
                    "requestBody": _request_body("generate_human_manual_ephemeris"),
                    "responses": _post_responses(),
                }
            },
            "/v1/topocentric-astrometry": {
                "post": {
                    "summary": (
                        "Compute WGS84 topocentric parallax, Saemundsson-Bennett refraction, Doppler velocity, "
                        "Shapiro delay, and Geocentric-vs-Topocentric D9/D60/KP Sub-Lord flips"
                    ),
                    "operationId": "computeTopocentricAstrometry",
                    "requestBody": _request_body("compute_topocentric_astrometry"),
                    "responses": _post_responses(),
                }
            },
            "/v1/retrograde-loops": {
                "post": {
                    "summary": (
                        "Solve 5-point synodic retrograde phase-space loops and Natal Triple-Pass Transit hits"
                    ),
                    "operationId": "solveRetrogradeLoops",
                    "requestBody": _request_body("solve_retrograde_loops"),
                    "responses": _post_responses(),
                }
            },
            "/v1/eclipse-sensitivity": {
                "post": {
                    "summary": (
                        "Evaluate Solar/Lunar eclipses, local obscuration, and natal degree Grahan sensitivity"
                    ),
                    "operationId": "evaluateEclipseSensitivity",
                    "requestBody": _request_body("evaluate_eclipse_sensitivity"),
                    "responses": _post_responses(),
                }
            },
            "/v1/conditional-dashas-nadi": {
                "post": {
                    "summary": (
                        "Compute all 10 BPHS Conditional Nakshatra Dashas, 5-level Prana Chronometer, "
                        "150-Division Nadi Amsa, and 3-Ring Sudarshana Chakra"
                    ),
                    "operationId": "computeConditionalDashasAndNadi",
                    "requestBody": _request_body("compute_conditional_dashas_and_nadi"),
                    "responses": _post_responses(),
                }
            },
            "/v1/dignity-heliacal": {
                "post": {
                    "summary": (
                        "Compute continuous sinusoidal Uchcha-Neecha potential, Arohi/Avarohi climb velocity, "
                        "3D Digbala, and Surya Siddhanta Kalansha heliacal rising/setting (Udaya/Asta)"
                    ),
                    "operationId": "computeDignityAndHeliacal",
                    "requestBody": _request_body("compute_dignity_and_heliacal_phenomena"),
                    "responses": _post_responses(),
                }
            },
            "/v1/sarvatobhadra-vedha-pinda": {
                "post": {
                    "summary": (
                        "Trace 81-Cell Sarvatobhadra 3-way Trishula Vedha rays, 7-planet Shodhya Pinda "
                        "Nakshatra triggers, 12-house Vitta-Ayavyaya ratios, and Continuous Harmonic Yogas"
                    ),
                    "operationId": "computeSarvatobhadraVedhaAndPinda",
                    "requestBody": _request_body("compute_sarvatobhadra_vedha_and_shodhya_pinda"),
                    "responses": _post_responses(),
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
    "/v1/fingerprint": "compute_personalized_astro_fingerprint",
    "/v1/yogatara": "evaluate_yogatara_stellar_bheda",
    "/v1/mahapata": "solve_krantisamya_mahapata",
    "/v1/inverse-date": "solve_inverse_chart_date",
    "/v1/triple-lock": "compute_triple_lock_convergence",
    "/v1/human-ephemeris": "generate_human_manual_ephemeris",
    "/v1/topocentric-astrometry": "compute_topocentric_astrometry",
    "/v1/retrograde-loops": "solve_retrograde_loops",
    "/v1/eclipse-sensitivity": "evaluate_eclipse_sensitivity",
    "/v1/conditional-dashas-nadi": "compute_conditional_dashas_and_nadi",
    "/v1/dignity-heliacal": "compute_dignity_and_heliacal_phenomena",
    "/v1/sarvatobhadra-vedha-pinda": "compute_sarvatobhadra_vedha_and_shodhya_pinda",
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


MAX_REQUEST_BODY_BYTES = 1_048_576


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
        try:
            length = int(self.headers.get("Content-Length", "0") or "0")
        except ValueError:
            self._send_json(400, {"error": "Invalid Content-Length header"})
            return
        if length < 0:
            self._send_json(400, {"error": "Negative Content-Length header"})
            return
        if length > MAX_REQUEST_BODY_BYTES:
            self._send_json(
                413,
                {"error": f"Request body exceeds {MAX_REQUEST_BODY_BYTES} byte limit"},
            )
            return
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
