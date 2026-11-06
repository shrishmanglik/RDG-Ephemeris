"""Built-in Model Context Protocol (MCP) JSON-RPC 2.0 server over stdio.

Allows any MCP-compatible AI assistant or agent runtime (Claude Desktop, Cursor,
VS Code, Windsurf, custom LLM agents) to invoke deterministic NASA JPL DE440
Chebyshev ephemeris and Jyotish calculations natively with cryptographic SHA-256
receipts and zero hallucinated astronomy.

Usage::

    rdg-ephemeris-mcp
    # or:
    ephemeris-oss mcp
    # or:
    python -m ephemeris_oss.mcp_server
"""

from __future__ import annotations

from dataclasses import asdict, is_dataclass
from datetime import datetime, timezone
import json
import sys
from typing import Any, Mapping, TextIO

from ._version import __version__
from .adapter import EphemerisAdapter, VEDIC_NINE_GRAHAS
from .almanac import compute_regional_panchang
from .fact_sheet import compile_ai_fact_sheet, verify_ai_interpretation
from .impossible_astrology import (
    analyze_siddhanta_vs_jpl_de440_drift,
    compute_personalized_astro_fingerprint,
    rectify_birth_time_bayesian,
    scan_multi_century_rare_phenomena,
    solve_subsecond_shodashvarga_cusp_transitions,
)
from .jyotish.dasha import jd_to_iso_utc

MCP_PROTOCOL_VERSION = "2024-11-05"


def _to_jsonable(obj: Any) -> Any:
    if is_dataclass(obj) and not isinstance(obj, type):
        return _to_jsonable(asdict(obj))
    if isinstance(obj, Mapping):
        return {str(k): _to_jsonable(v) for k, v in obj.items()}
    if isinstance(obj, (list, tuple, set, frozenset)):
        return [_to_jsonable(v) for v in obj]
    if isinstance(obj, datetime):
        return obj.isoformat()
    return obj


def _resolve_jd_ut(arguments: Mapping[str, Any]) -> float:
    """Resolve ``jd_ut`` from either explicit ``jd_ut`` float or ``iso_utc`` string."""
    if "jd_ut" in arguments and arguments["jd_ut"] is not None:
        return float(arguments["jd_ut"])
    iso_text = arguments.get("iso_utc") or arguments.get("at")
    if not iso_text:
        raise ValueError("Provide either 'jd_ut' (Julian Date UT) or 'iso_utc' (ISO-8601 UTC timestamp).")
    text = str(iso_text).strip()
    dt = datetime.fromisoformat(text.replace("Z", "+00:00"))
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    else:
        dt = dt.astimezone(timezone.utc)
    return dt.timestamp() / 86400.0 + 2440587.5


MCP_TOOLS: tuple[dict[str, Any], ...] = (
    {
        "name": "compute_planetary_positions",
        "description": (
            "Compute high-precision sidereal and tropical planetary positions, speeds, "
            "retrograde status, Rasi sign, and 27-Nakshatra Pada from the embedded NASA JPL "
            "DE440 Chebyshev kernel (1550-2306 CE) or historical Vondrak-2011 provider (3102 BCE-3000 CE)."
        ),
        "inputSchema": {
            "type": "object",
            "properties": {
                "jd_ut": {"type": "number", "description": "Julian Date (UT). Covers 3102 BCE (JD 588465.5) to 3000 CE."},
                "iso_utc": {"type": "string", "description": "ISO-8601 UTC timestamp (e.g. '2026-10-06T12:00:00Z')."},
                "ayanamsa": {"type": "string", "default": "lahiri", "description": "Sidereal ayanamsa mode (lahiri, raman, kp, true_chitrapaksha, yukteshwar, fagan_bradley)."},
                "true_node": {"type": "boolean", "default": False, "description": "Use True (osculating) Rahu/Ketu instead of Mean Rahu/Ketu."},
            },
        },
    },
    {
        "name": "compute_complete_kundali",
        "description": (
            "Compute a complete deterministic Vedic natal chart (Kundali): all 9 Grahas, "
            "Ascendant and 12 house cusps, all 16 Shodashvarga divisional charts (D1-D60), "
            "Ashtakavarga, Shadbala, Vimshottari/Yogini/Chara/Narayana Dashas, Panchanga, and Yogas."
        ),
        "inputSchema": {
            "type": "object",
            "properties": {
                "jd_ut": {"type": "number", "description": "Julian Date (UT)."},
                "iso_utc": {"type": "string", "description": "ISO-8601 UTC timestamp."},
                "latitude_deg": {"type": "number", "default": 28.6139, "description": "Observer geographic latitude in degrees."},
                "longitude_deg": {"type": "number", "default": 77.2090, "description": "Observer geographic longitude in degrees."},
                "ayanamsa": {"type": "string", "default": "lahiri"},
                "true_node": {"type": "boolean", "default": False, "description": "Use True (osculating) Rahu/Ketu instead of Mean Rahu/Ketu."},
            },
        },
    },
    {
        "name": "compute_panchanga",
        "description": (
            "Compute sunrise-anchored regional Drik Panchanga: Tithi, Nakshatra, Yoga, Karana, "
            "Vara, Amanta/Purnimanta lunar month, regional solar calendar, and a separate "
            "instantaneous_panchanga snapshot (or request mode='instantaneous' explicitly)."
        ),
        "inputSchema": {
            "type": "object",
            "properties": {
                "jd_ut": {"type": "number"},
                "iso_utc": {"type": "string"},
                "latitude_deg": {"type": "number", "default": 28.6139},
                "longitude_deg": {"type": "number", "default": 77.2090},
                "ayanamsa": {"type": "string", "default": "lahiri"},
                "mode": {
                    "type": "string",
                    "enum": ["sunrise", "instantaneous"],
                    "default": "sunrise",
                    "description": (
                        "Default 'sunrise' evaluates daily Udaya Panchanga limbs at the observer's "
                        "active local sunrise (and before-sunrise instants at the preceding Vedic day's "
                        "sunrise); 'instantaneous' evaluates primary limbs at the exact supplied instant."
                    ),
                },
            },
        },
    },
    {
        "name": "rectify_birth_time_and_varga_cusps",
        "description": (
            "Solve sub-second divisional chart (D1-D60) cusp transition margins and run "
            "multi-criterion classical birth-time rectification (Kunda 81x harmonic, Pranapada "
            "Shuddhi, Pancha Tattwa 90-minute elemental cycles, and life-event Dasha alignment)."
        ),
        "inputSchema": {
            "type": "object",
            "properties": {
                "jd_ut": {"type": "number"},
                "iso_utc": {"type": "string"},
                "latitude_deg": {"type": "number", "default": 28.6139},
                "longitude_deg": {"type": "number", "default": 77.2090},
                "window_minutes": {"type": "number", "default": 15.0},
                "step_seconds": {"type": "number", "default": 15.0},
                "ayanamsa": {"type": "string", "default": "lahiri"},
                "true_node": {"type": "boolean", "default": False},
            },
        },
    },
    {
        "name": "scan_planetary_wars_and_stations",
        "description": (
            "Scan a date interval for exact-second Graha Yuddha (planetary wars within 1 degree "
            "with disc-diameter and northern-latitude winner), retrograde stations (Vakri/Margi), "
            "and solar combustion (Astangata/Cazimi)."
        ),
        "inputSchema": {
            "type": "object",
            "properties": {
                "start_jd_tt": {"type": "number", "description": "Window start Julian Date (TT/UT)."},
                "end_jd_tt": {"type": "number", "description": "Window end Julian Date (TT/UT)."},
                "ayanamsa": {"type": "string", "default": "lahiri"},
                "bodies": {
                    "type": "array",
                    "items": {"type": "string"},
                    "default": ["mars", "mercury", "jupiter", "venus", "saturn"],
                },
            },
            "required": ["start_jd_tt", "end_jd_tt"],
        },
    },
    {
        "name": "compare_surya_siddhanta_vs_de440",
        "description": (
            "Compare classical Surya Siddhanta epicyclic (Manda and Sighra Samskara from 3102 BCE "
            "Kali Yuga epoch) true positions against modern NASA JPL DE440 / Drig-Ganita positions."
        ),
        "inputSchema": {
            "type": "object",
            "properties": {
                "jd_ut": {"type": "number"},
                "iso_utc": {"type": "string"},
                "ayanamsa": {"type": "string", "default": "lahiri"},
            },
        },
    },
    {
        "name": "compile_verified_ai_fact_sheet",
        "description": (
            "Compile a compact (<3 KB), token-disciplined, SHA-256-sealed JSON astrological "
            "fact sheet designed for LLM system prompts so AI models never hallucinate placements."
        ),
        "inputSchema": {
            "type": "object",
            "properties": {
                "jd_ut": {"type": "number"},
                "iso_utc": {"type": "string"},
                "latitude_deg": {"type": "number", "default": 28.6139},
                "longitude_deg": {"type": "number", "default": 77.2090},
                "ayanamsa": {"type": "string", "default": "lahiri"},
            },
        },
    },
    {
        "name": "verify_ai_astrology_text",
        "description": (
            "Audit an AI-generated astrological paragraph against a deterministic chart fact sheet "
            "to catch and flag any hallucinated sign, house, Nakshatra, or Dasha claim."
        ),
        "inputSchema": {
            "type": "object",
            "properties": {
                "text": {"type": "string", "description": "AI-generated astrological interpretation text to verify."},
                "jd_ut": {"type": "number"},
                "iso_utc": {"type": "string"},
                "latitude_deg": {"type": "number", "default": 28.6139},
                "longitude_deg": {"type": "number", "default": 77.2090},
                "ayanamsa": {"type": "string", "default": "lahiri"},
            },
            "required": ["text"],
        },
    },
    {
        "name": "compute_personalized_astro_fingerprint",
        "description": (
            "Compute a personalized, birth-clock-calibrated, topocentric astrological fingerprint: "
            "continuous 16-Varga (D1-D60) harmonic phase vector, 20-point Shodashvarga Vimshopaka "
            "alignment, 16-domain clock-uncertainty confidence decay exp(-sigma_t / tau_min), "
            "continuous horizon-meridian Digbala vector, and personal 8-Kaksha (3 deg 45 arcmin) "
            "Ashtakavarga transit resonance."
        ),
        "inputSchema": {
            "type": "object",
            "properties": {
                "jd_ut": {"type": "number", "description": "Natal Julian Date (UT)."},
                "iso_utc": {"type": "string", "description": "Natal ISO-8601 UTC timestamp."},
                "query_jd_ut": {"type": "number", "description": "Optional transit/query Julian Date (UT)."},
                "latitude_deg": {"type": "number", "default": 28.6139},
                "longitude_deg": {"type": "number", "default": 77.2090},
                "birth_time_uncertainty_seconds": {"type": "number", "default": 60.0},
                "ayanamsa": {"type": "string", "default": "lahiri"},
                "true_node": {"type": "boolean", "default": False},
            },
        },
    },
)


_DEFAULT_ADAPTER: EphemerisAdapter | None = None


def _get_default_adapter() -> EphemerisAdapter:
    global _DEFAULT_ADAPTER
    if _DEFAULT_ADAPTER is None:
        _DEFAULT_ADAPTER = EphemerisAdapter()
    return _DEFAULT_ADAPTER


def execute_mcp_tool(name: str, arguments: Mapping[str, Any] | None = None) -> dict[str, Any]:
    """Execute one named MCP tool and return a JSON-serializable dictionary payload."""
    args = dict(arguments or {})
    adapter = _get_default_adapter()

    if name == "compute_planetary_positions":
        jd_ut = _resolve_jd_ut(args)
        ayanamsa = str(args.get("ayanamsa", "lahiri"))
        use_true_node = bool(args.get("true_node", False))
        ayan_deg = adapter.get_ayanamsa_ut(jd_ut, mode=ayanamsa)
        planets = {
            body: adapter.calc_ut(
                jd_ut,
                body,
                sidereal=True,
                ayanamsa=ayanamsa,
                true_node=use_true_node,
            )
            for body in VEDIC_NINE_GRAHAS
        }
        ephem_source = "de440-chebyshev" if 2287184.5 <= jd_ut <= 2563392.5 else "vondrak2011-analytical"
        return _to_jsonable(
            {
                "jd_ut": jd_ut,
                "iso_utc": jd_to_iso_utc(jd_ut),
                "ayanamsa_mode": ayanamsa,
                "ayanamsa_deg": ayan_deg,
                "node_mode": "true" if use_true_node else "mean",
                "ephemeris_source": ephem_source,
                "planets": planets,
            }
        )

    if name == "compute_complete_kundali":
        jd_ut = _resolve_jd_ut(args)
        lat = float(args.get("latitude_deg", 28.6139))
        lon = float(args.get("longitude_deg", 77.2090))
        ayanamsa = str(args.get("ayanamsa", "lahiri"))
        use_true_node = bool(args.get("true_node", False))
        bundle = adapter.compute_complete_kundali_bundle(
            jd_ut,
            lat,
            lon,
            ayanamsa=ayanamsa,
            true_node=use_true_node,
            include_svg=False,
        )
        ephem_source = "de440-chebyshev" if 2287184.5 <= jd_ut <= 2563392.5 else "vondrak2011-analytical"
        return _to_jsonable(
            {
                "jd_ut": bundle.jd_ut,
                "iso_utc": jd_to_iso_utc(bundle.jd_ut),
                "ephemeris_source": ephem_source,
                "ayanamsa_mode": bundle.ayanamsa_system,
                "ayanamsa_deg": bundle.ayanamsa_deg,
                "node_mode": "true" if use_true_node else "mean",
                "ascendant_deg": bundle.houses.ascendant_deg,
                "mc_deg": bundle.houses.mc_deg,
                "planets": bundle.positions,
                "planet_vargas": bundle.vedic_analysis.planet_vargas,
                "lagna_vargas": bundle.vedic_analysis.lagna_vargas,
                "panchanga": bundle.vedic_analysis.panchanga,
                "vimshottari_dasha": bundle.vedic_analysis.vimshottari_dasha,
                "ashtottari_dasha": bundle.vedic_analysis.ashtottari_dasha,
                "yogini_dasha": bundle.vedic_analysis.yogini_dasha,
                "chara_dasha": bundle.vedic_analysis.chara_dasha,
                "yogas": bundle.classical_yogas,
                "shadbala": bundle.vedic_analysis.shadbala,
                "ashtakavarga_sarva": bundle.vedic_analysis.ashtakavarga.sarvashtakavarga_7,
                "ashtakavarga_sarva_total": bundle.vedic_analysis.ashtakavarga.sarvashtakavarga_7_total,
                "ai_fact_sheet": bundle.ai_fact_sheet,
                "receipt_sha256": bundle.bundle_receipt_sha256,
            }
        )

    if name == "compute_panchanga":
        jd_ut = _resolve_jd_ut(args)
        lat = float(args.get("latitude_deg", 28.6139))
        lon = float(args.get("longitude_deg", 77.2090))
        ayanamsa = str(args.get("ayanamsa", "lahiri")).strip() or "lahiri"
        mode = str(args.get("mode", "sunrise")).strip().lower()
        if mode not in {"sunrise", "instantaneous"}:
            raise ValueError("mode must be 'sunrise' or 'instantaneous'")
        report = compute_regional_panchang(
            jd_ut,
            latitude_deg=lat,
            longitude_deg=lon,
            adapter=adapter,
            ayanamsa=ayanamsa,
            anchor_to_sunrise=(mode == "sunrise"),
        )
        return _to_jsonable(report.to_dict())

    if name == "rectify_birth_time_and_varga_cusps":
        jd_ut = _resolve_jd_ut(args)
        lat = float(args.get("latitude_deg", 28.6139))
        lon = float(args.get("longitude_deg", 77.2090))
        win_min = float(args.get("window_minutes", 15.0))
        step_sec = float(args.get("step_seconds", 15.0))
        ayanamsa = str(args.get("ayanamsa", "lahiri"))
        use_true_node = bool(args.get("true_node", False))
        cusp_report = solve_subsecond_shodashvarga_cusp_transitions(
            jd_ut,
            lat,
            lon,
            ayanamsa=ayanamsa,
            true_node=use_true_node,
            adapter=adapter,
        )
        rect_report = rectify_birth_time_bayesian(
            jd_ut,
            lat,
            lon,
            window_minutes=win_min,
            step_seconds=step_sec,
            ayanamsa=ayanamsa,
            true_node=use_true_node,
            adapter=adapter,
        )
        return _to_jsonable(
            {
                "jd_ut": jd_ut,
                "iso_utc": jd_to_iso_utc(jd_ut),
                "node_mode": "true" if use_true_node else "mean",
                "most_sensitive_varga": cusp_report.most_sensitive_varga,
                "minimum_ascendant_cusp_margin_seconds": cusp_report.minimum_ascendant_cusp_margin_seconds,
                "ascendant_varga_margins": cusp_report.ascendant_margins,
                "planet_varga_margins": cusp_report.planet_margins,
                "cusp_receipt_sha256": cusp_report.receipt_sha256,
                "rectified_jd_ut": rect_report.rectified_jd_ut,
                "rectified_iso_utc": jd_to_iso_utc(rect_report.rectified_jd_ut),
                "offset_seconds": rect_report.offset_seconds,
                "best_candidate": rect_report.best_candidate,
                "top_candidates": rect_report.top_candidates[:5],
                "varga_transitions_in_window": rect_report.varga_transitions,
                "receipt_sha256": rect_report.receipt_sha256,
            }
        )

    if name == "scan_planetary_wars_and_stations":
        start_jd = float(args["start_jd_tt"])
        end_jd = float(args["end_jd_tt"])
        ayanamsa = str(args.get("ayanamsa", "lahiri"))
        bodies = tuple(args.get("bodies", ("mars", "mercury", "jupiter", "venus", "saturn")))
        report = scan_multi_century_rare_phenomena(
            start_jd,
            end_jd,
            bodies=bodies,
            ayanamsa=ayanamsa,
        )
        return _to_jsonable(report)

    if name == "compare_surya_siddhanta_vs_de440":
        jd_ut = _resolve_jd_ut(args)
        ayanamsa = str(args.get("ayanamsa", "lahiri"))
        report = analyze_siddhanta_vs_jpl_de440_drift(
            jd_ut,
            ayanamsa=ayanamsa,
            adapter=adapter,
        )
        return _to_jsonable(report)

    if name == "compile_verified_ai_fact_sheet":
        jd_ut = _resolve_jd_ut(args)
        lat = float(args.get("latitude_deg", 28.6139))
        lon = float(args.get("longitude_deg", 77.2090))
        ayanamsa = str(args.get("ayanamsa", "lahiri"))
        bundle = adapter.compute_complete_kundali_bundle(
            jd_ut,
            lat,
            lon,
            ayanamsa=ayanamsa,
            include_svg=False,
        )
        return _to_jsonable(bundle.ai_fact_sheet)

    if name == "verify_ai_astrology_text":
        jd_ut = _resolve_jd_ut(args)
        lat = float(args.get("latitude_deg", 28.6139))
        lon = float(args.get("longitude_deg", 77.2090))
        ayanamsa = str(args.get("ayanamsa", "lahiri"))
        text = str(args.get("text", ""))
        bundle = adapter.compute_complete_kundali_bundle(
            jd_ut,
            lat,
            lon,
            ayanamsa=ayanamsa,
            include_svg=False,
        )
        audit = verify_ai_interpretation(text, bundle.ai_fact_sheet)
        return _to_jsonable(audit)

    if name == "compute_personalized_astro_fingerprint":
        jd_ut = _resolve_jd_ut(args)
        lat = float(args.get("latitude_deg", 28.6139))
        lon = float(args.get("longitude_deg", 77.2090))
        query_jd = float(args["query_jd_ut"]) if args.get("query_jd_ut") is not None else None
        sigma_t = float(args.get("birth_time_uncertainty_seconds", 60.0))
        ayanamsa = str(args.get("ayanamsa", "lahiri"))
        use_true_node = bool(args.get("true_node", False))
        fp_report = compute_personalized_astro_fingerprint(
            jd_ut,
            lat,
            lon,
            query_jd_ut=query_jd,
            birth_time_uncertainty_seconds=sigma_t,
            ayanamsa=ayanamsa,
            true_node=use_true_node,
            adapter=adapter,
        )
        return _to_jsonable(fp_report.to_dict())

    raise ValueError(f"Unknown MCP tool: {name!r}")


def handle_jsonrpc_message(request: Any) -> dict[str, Any] | None:
    """Process one MCP JSON-RPC 2.0 request and return a response dict (or None for notifications)."""
    if not isinstance(request, Mapping):
        return {
            "jsonrpc": "2.0",
            "id": None,
            "error": {
                "code": -32600,
                "message": "Invalid Request: JSON-RPC message must be a JSON object.",
            },
        }

    raw_method = request.get("method")
    req_id = request.get("id")
    if not isinstance(raw_method, str) or not raw_method.strip():
        return {
            "jsonrpc": "2.0",
            "id": req_id if isinstance(req_id, (str, int, float)) or req_id is None else None,
            "error": {
                "code": -32600,
                "message": "Invalid Request: 'method' must be a non-empty string.",
            },
        }

    method = raw_method
    params = request.get("params") or {}

    if method.startswith("notifications/") or req_id is None:
        return None

    if method == "initialize":
        client_version = params.get("protocolVersion") if isinstance(params, Mapping) else None
        negotiated_version = str(client_version) if client_version else MCP_PROTOCOL_VERSION
        return {
            "jsonrpc": "2.0",
            "id": req_id,
            "result": {
                "protocolVersion": negotiated_version,
                "capabilities": {
                    "tools": {"listChanged": False},
                },
                "serverInfo": {
                    "name": "rdg-ephemeris-mcp",
                    "version": __version__,
                },
            },
        }

    if method == "ping":
        return {
            "jsonrpc": "2.0",
            "id": req_id,
            "result": {},
        }

    if method == "tools/list":
        return {
            "jsonrpc": "2.0",
            "id": req_id,
            "result": {
                "tools": list(MCP_TOOLS),
            },
        }

    if method == "tools/call":
        tool_name = str(params.get("name", "")) if isinstance(params, Mapping) else ""
        tool_args = params.get("arguments") if isinstance(params, Mapping) else {}
        try:
            payload = execute_mcp_tool(tool_name, tool_args if isinstance(tool_args, Mapping) else {})
            return {
                "jsonrpc": "2.0",
                "id": req_id,
                "result": {
                    "content": [
                        {
                            "type": "text",
                            "text": json.dumps(payload, sort_keys=True),
                        }
                    ],
                    "structuredContent": payload,
                    "isError": False,
                },
            }
        except Exception as exc:
            return {
                "jsonrpc": "2.0",
                "id": req_id,
                "result": {
                    "content": [
                        {
                            "type": "text",
                            "text": json.dumps({"error": str(exc)}, sort_keys=True),
                        }
                    ],
                    "isError": True,
                },
            }

    return {
        "jsonrpc": "2.0",
        "id": req_id,
        "error": {
            "code": -32601,
            "message": f"Method not found: {method}",
        },
    }


def serve_stdio(stdin: TextIO = sys.stdin, stdout: TextIO = sys.stdout) -> int:
    """Run the MCP JSON-RPC 2.0 server loop over newline-delimited stdio."""
    for raw_line in stdin:
        line = raw_line.strip()
        if not line:
            continue
        try:
            message = json.loads(line)
        except json.JSONDecodeError as exc:
            err_resp = {
                "jsonrpc": "2.0",
                "id": None,
                "error": {"code": -32700, "message": f"Parse error: {exc}"},
            }
            stdout.write(json.dumps(err_resp) + "\n")
            stdout.flush()
            continue

        response = handle_jsonrpc_message(message)
        if response is not None:
            stdout.write(json.dumps(response) + "\n")
            stdout.flush()
    return 0


def main(argv: list[str] | None = None) -> int:
    """CLI entry point for ``rdg-ephemeris-mcp``."""
    effective_argv = sys.argv[1:] if argv is None else list(argv)
    if "--dump-tools" in effective_argv:
        print(json.dumps({"tools": list(MCP_TOOLS)}, indent=2, sort_keys=True))
        return 0
    return serve_stdio()


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
