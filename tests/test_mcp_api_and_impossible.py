"""Tests for multi-millennium date span (3102 BCE to 2300 CE / 3000 CE),
impossible astrology solvers, MCP JSON-RPC 2.0 server, and HTTP REST API.
"""

from __future__ import annotations

import io
import json

from ephemeris_oss import (
    Engine,
    EphemerisAdapter,
    analyze_siddhanta_vs_jpl_de440_drift,
    cli,
    rectify_birth_time_bayesian,
    scan_multi_century_rare_phenomena,
    solve_subsecond_shodashvarga_cusp_transitions,
)
from ephemeris_oss.api_server import build_openapi_spec, dispatch_api_request
from ephemeris_oss.compact_kernel import (
    COMPACT_EARLY_WING_PATH,
    COMPACT_EARLY_WING_SHA256,
    COMPACT_LATE_WING_PATH,
    COMPACT_LATE_WING_SHA256,
    CompactChebyshevKernel,
)
from ephemeris_oss.mcp_server import MCP_TOOLS, execute_mcp_tool, handle_jsonrpc_message, serve_stdio


def test_embedded_early_and_late_de440_chebyshev_wings_verify() -> None:
    with CompactChebyshevKernel.open(COMPACT_EARLY_WING_PATH) as early:
        assert early.sha256 == COMPACT_EARLY_WING_SHA256
        assert len(early.segments) == 14
    with CompactChebyshevKernel.open(COMPACT_LATE_WING_PATH) as late:
        assert late.sha256 == COMPACT_LATE_WING_SHA256
        assert len(late.segments) == 14


def test_multi_millennium_date_range_3102_bce_to_2300_ce_and_3000_ce() -> None:
    adapter = EphemerisAdapter()
    epochs = (
        ("3102_bce_kali_yuga", 588465.5),
        ("1600_ce_early_wing", 2305447.5),
        ("2026_ce_modern_core", 2461139.0),
        ("2300_ce_future_wing", 2561117.5),
        ("3000_ce_far_future", 2816787.5),
    )
    for label, jd_ut in epochs:
        bundle = adapter.compute_complete_kundali_bundle(
            jd_ut,
            28.6139,
            77.2090,
            ayanamsa="lahiri",
            include_svg=False,
        )
        assert len(bundle.bundle_receipt_sha256) == 64, label
        assert 0.0 <= bundle.positions["sun"].longitude_deg < 360.0, label
        assert 0.0 <= bundle.positions["moon"].longitude_deg < 360.0, label
        assert 0.0 <= bundle.houses.ascendant_deg < 360.0, label

    with Engine.load(kernels="auto", eop=None) as eng:
        r_1600 = eng.positions_tt(2305447.5, bodies=("sun", "moon", "jupiter", "saturn"))
        r_2300 = eng.positions_tt(2561117.5, bodies=("sun", "moon", "jupiter", "saturn"))
        assert len(r_1600.receipt_sha256) == 64
        assert len(r_2300.receipt_sha256) == 64
        assert 0.0 <= r_1600.value["moon"]["longitude_deg"] < 360.0
        assert 0.0 <= r_2300.value["saturn"]["longitude_deg"] < 360.0


def test_impossible_astrology_solvers_end_to_end() -> None:
    jd_ut = 2461139.0
    cusps = solve_subsecond_shodashvarga_cusp_transitions(jd_ut, 28.6139, 77.2090)
    assert len(cusps.receipt_sha256) == 64
    assert len(cusps.ascendant_margins) == 16
    assert cusps.most_sensitive_varga in cusps.ascendant_margins
    assert cusps.minimum_ascendant_cusp_margin_seconds >= 0.0

    rect = rectify_birth_time_bayesian(
        jd_ut,
        28.6139,
        77.2090,
        window_minutes=10.0,
        step_seconds=60.0,
    )
    assert len(rect.receipt_sha256) == 64
    assert len(rect.all_candidates) == 21
    assert 0.0 <= rect.best_candidate.total_score <= 100.0

    phen = scan_multi_century_rare_phenomena(
        2461041.5,
        2461131.5,
        bodies=("mars", "mercury", "jupiter", "venus", "saturn"),
    )
    assert len(phen.receipt_sha256) == 64
    assert phen.graha_yuddha_count >= 0
    assert phen.retrograde_station_count >= 0
    assert phen.combustion_window_count >= 0

    drift = analyze_siddhanta_vs_jpl_de440_drift(jd_ut)
    assert len(drift.receipt_sha256) == 64
    assert drift.ahargana_days > 1_800_000.0
    assert "sun" in drift.planet_comparisons
    assert "moon" in drift.planet_comparisons


def test_mcp_jsonrpc_server_and_all_tools() -> None:
    assert len(MCP_TOOLS) == 8
    init_resp = handle_jsonrpc_message(
        {"jsonrpc": "2.0", "id": 1, "method": "initialize", "params": {"protocolVersion": "2024-11-05"}}
    )
    assert init_resp is not None
    assert init_resp["result"]["serverInfo"]["name"] == "rdg-ephemeris-mcp"

    list_resp = handle_jsonrpc_message({"jsonrpc": "2.0", "id": 2, "method": "tools/list", "params": {}})
    assert list_resp is not None
    assert len(list_resp["result"]["tools"]) == 8

    call_resp = handle_jsonrpc_message(
        {
            "jsonrpc": "2.0",
            "id": 3,
            "method": "tools/call",
            "params": {
                "name": "compute_planetary_positions",
                "arguments": {"iso_utc": "2026-10-06T12:00:00Z", "ayanamsa": "lahiri"},
            },
        }
    )
    assert call_resp is not None
    assert call_resp["result"]["isError"] is False
    structured = call_resp["result"]["structuredContent"]
    assert structured["ephemeris_source"] == "de440-chebyshev"
    assert "sun" in structured["planets"]

    # Test stdio loop
    stdin_buf = io.StringIO(
        json.dumps({"jsonrpc": "2.0", "id": 10, "method": "ping"}) + "\n"
    )
    stdout_buf = io.StringIO()
    assert serve_stdio(stdin=stdin_buf, stdout=stdout_buf) == 0
    out_msg = json.loads(stdout_buf.getvalue().strip())
    assert out_msg["id"] == 10
    assert out_msg["result"] == {}


def test_rest_api_dispatcher_and_cli_subcommands() -> None:
    status, health = dispatch_api_request("GET", "/health")
    assert status == 200
    assert health["status"] == "ok"
    assert health["embedded_de440_chebyshev_span_ce"] == "1550-2306"

    status_oa, oa = dispatch_api_request("GET", "/openapi.json")
    assert status_oa == 200
    assert oa["openapi"] == "3.1.0"
    assert "/v1/positions" in build_openapi_spec()["paths"]

    status_pos, pos = dispatch_api_request(
        "POST",
        "/v1/positions",
        {"jd_ut": 2561117.5, "ayanamsa": "lahiri"},
    )
    assert status_pos == 200
    assert pos["ephemeris_source"] == "de440-chebyshev"

    status_rect, rect = dispatch_api_request(
        "POST",
        "/v1/rectify",
        {"jd_ut": 2461139.0, "latitude_deg": 28.6139, "longitude_deg": 77.2090, "window_minutes": 5.0, "step_seconds": 60.0},
    )
    assert status_rect == 200
    assert "rectified_jd_ut" in rect

    status_fs, fs = dispatch_api_request(
        "POST",
        "/v1/fact-sheet",
        {"jd_ut": 2461139.0, "latitude_deg": 28.6139, "longitude_deg": 77.2090},
    )
    assert status_fs == 200
    assert "receipt_sha256" in fs

    assert cli.main(["mcp", "--dump-tools"]) == 0
    assert cli.main(["serve", "--dump-openapi"]) == 0
    assert cli.main(["impossible", "--at", "2026-10-06T12:00:00Z", "--step-seconds", "60"]) == 0
