"""Tests for multi-millennium date span (3102 BCE to 2300 CE / 3000 CE),
impossible astrology solvers, MCP JSON-RPC 2.0 server, and HTTP REST API.
"""

from __future__ import annotations

from dataclasses import replace
import io
import json
from pathlib import Path
import pytest

from ephemeris_oss import (
    Engine,
    EphemerisAdapter,
    PersonalizedAstroFingerprintReport,
    analyze_siddhanta_vs_jpl_de440_drift,
    cli,
    compute_personalized_astro_fingerprint,
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
from ephemeris_oss.impossible_astrology import _compute_body_varga_margins
from ephemeris_oss.jyotish.vargas import SHODASHVARGA_KEYS, varga_sign
from ephemeris_oss.mcp_server import MCP_TOOLS, execute_mcp_tool, handle_jsonrpc_message, serve_stdio


def test_embedded_early_and_late_de440_chebyshev_wings_verify() -> None:
    with CompactChebyshevKernel.open(COMPACT_EARLY_WING_PATH) as early:
        assert early.sha256 == COMPACT_EARLY_WING_SHA256
        assert len(early.segments) == 14
    with CompactChebyshevKernel.open(COMPACT_LATE_WING_PATH) as late:
        assert late.sha256 == COMPACT_LATE_WING_SHA256
        assert len(late.segments) == 14


def test_multi_millennium_date_range_3102_bce_to_2300_ce_and_3000_ce(tmp_path: Path) -> None:
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

    # Verify zero-config embedded offline loading works with an empty explicit cache directory
    empty_cache = tmp_path / "empty_kernel_cache"
    empty_cache.mkdir(parents=True, exist_ok=True)
    with Engine.load(kernels="extended", cache_dir=empty_cache, eop=None) as eng:
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

    fp = compute_personalized_astro_fingerprint(
        jd_ut,
        28.6139,
        77.2090,
        query_jd_ut=jd_ut + 15.0,
        birth_time_uncertainty_seconds=60.0,
    )
    assert isinstance(fp, PersonalizedAstroFingerprintReport)
    assert len(fp.fingerprint_id_sha256) == 64
    assert len(fp.receipt_sha256) == 64
    assert 0.0 < fp.overall_clock_confidence_score <= 1.0
    assert 0.0 <= fp.overall_personal_transit_resonance_score <= 100.0
    assert len(fp.harmonic_phase_matrix) == 10
    assert len(fp.domain_clock_confidence) == 16
    assert len(fp.topocentric_digbala_vector) == 7
    assert len(fp.personal_transit_resonance) == 7
    with pytest.raises(ValueError, match="birth_time_uncertainty_seconds"):
        compute_personalized_astro_fingerprint(jd_ut, 28.6139, 77.2090, birth_time_uncertainty_seconds=-5.0)


def test_mcp_jsonrpc_server_and_all_tools() -> None:
    assert len(MCP_TOOLS) == 20
    init_resp = handle_jsonrpc_message(
        {"jsonrpc": "2.0", "id": 1, "method": "initialize", "params": {"protocolVersion": "2024-11-05"}}
    )
    assert init_resp is not None
    assert init_resp["result"]["serverInfo"]["name"] == "rdg-ephemeris-mcp"

    list_resp = handle_jsonrpc_message({"jsonrpc": "2.0", "id": 2, "method": "tools/list", "params": {}})
    assert list_resp is not None
    assert len(list_resp["result"]["tools"]) == 20

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

    fp_call = handle_jsonrpc_message(
        {
            "jsonrpc": "2.0",
            "id": 4,
            "method": "tools/call",
            "params": {
                "name": "compute_personalized_astro_fingerprint",
                "arguments": {
                    "iso_utc": "2026-10-06T12:00:00Z",
                    "latitude_deg": 28.6139,
                    "longitude_deg": 77.2090,
                    "birth_time_uncertainty_seconds": 45.0,
                },
            },
        }
    )
    assert fp_call is not None
    assert fp_call["result"]["isError"] is False
    fp_struct = fp_call["result"]["structuredContent"]
    assert len(fp_struct["fingerprint_id_sha256"]) == 64
    assert len(fp_struct["receipt_sha256"]) == 64

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
    assert "/v1/fingerprint" in build_openapi_spec()["paths"]

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

    status_fp, fp_payload = dispatch_api_request(
        "POST",
        "/v1/fingerprint",
        {"jd_ut": 2461139.0, "latitude_deg": 28.6139, "longitude_deg": 77.2090, "birth_time_uncertainty_seconds": 30.0},
    )
    assert status_fp == 200
    assert len(fp_payload["fingerprint_id_sha256"]) == 64

    assert cli.main(["mcp", "--dump-tools"]) == 0
    assert cli.main(["serve", "--dump-openapi"]) == 0
    assert cli.main(["impossible", "--at", "2026-10-06T12:00:00Z", "--step-seconds", "60"]) == 0
    assert cli.main(["fingerprint", "--at", "2026-10-06T12:00:00Z", "--json"]) == 0
    assert cli.main(["fingerprint", "--at", "2026-10-06T12:00:00Z"]) == 0


def test_d30_unequal_boundaries_and_subsecond_varga_transitions_and_receipt_binding() -> None:
    # 1. Unequal Parashari D30 boundaries (Aquarius runs from 5 to 10 deg in odd signs)
    margin_d30 = _compute_body_varga_margins("control", 5.1, 0.1)["D30"]
    assert varga_sign(5.1, "D30").sign_index == varga_sign(6.0, "D30").sign_index
    assert abs(margin_d30.seconds_to_next_cusp - 49.0) < 0.001

    # 2. Zero speed without position evaluator raises ValueError instead of substituting mean speed
    with pytest.raises(ValueError, match="speed_deg_per_sec must be non-zero"):
        _compute_body_varga_margins("stationary", 12.0, 0.0)

    # 3. Stationary/reversing body with position_at_offset_sec solves exact reversal cusp crossing
    # Starts at 12.0 deg (D1 Aries 0..30) with 0 instantaneous speed and accelerates backward (-0.5 * 0.01 * t^2)
    stationary_d1 = _compute_body_varga_margins(
        "Mars",
        12.0,
        0.0,
        position_at_offset_sec=lambda dt: 12.0 - 0.005 * (dt ** 2),
    )["D1"]
    # Crosses 0.0 deg when 0.005 * t^2 = 12.0 => t = sqrt(2400) = 48.98979485566356 s
    assert abs(stationary_d1.seconds_to_next_cusp - 48.9898) < 0.001
    assert abs(stationary_d1.seconds_to_previous_cusp - 48.9898) < 0.001

    # 4. Sub-second accuracy across all 16 Shodashvarga charts (both previous and next transitions)
    jd_ut = 2461139.0
    lat, lon = 28.6139, 77.209
    adapter = EphemerisAdapter()
    cusp_report = solve_subsecond_shodashvarga_cusp_transitions(jd_ut, lat, lon, adapter=adapter)

    def _asc_sign(offset_sec: float, v_key: str) -> int:
        asc = adapter.houses_ut(
            jd_ut + offset_sec / 86400.0,
            lat,
            lon,
            system="whole_sign",
            ayanamsa="lahiri",
        ).ascendant_deg
        return varga_sign(asc, v_key).sign_index

    for v_key in SHODASHVARGA_KEYS:
        m = cusp_report.ascendant_margins[v_key]
        assert _asc_sign(m.seconds_to_next_cusp - 0.5, v_key) == m.sign_index, (v_key, "next_in")
        assert _asc_sign(m.seconds_to_next_cusp + 0.5, v_key) != m.sign_index, (v_key, "next_out")
        assert _asc_sign(-m.seconds_to_previous_cusp + 0.5, v_key) == m.sign_index, (v_key, "prev_in")
        assert _asc_sign(-m.seconds_to_previous_cusp - 0.5, v_key) != m.sign_index, (v_key, "prev_out")

    # 5. Receipt changes whenever any planetary result changes
    class ChangedPlanetAdapter(EphemerisAdapter):
        def calc_ut(self, *args, **kwargs):  # type: ignore[no-untyped-def]
            result = super().calc_ut(*args, **kwargs)
            return replace(result, longitude_deg=(result.longitude_deg + 1.0) % 360.0)

    changed_report = solve_subsecond_shodashvarga_cusp_transitions(
        jd_ut,
        lat,
        lon,
        adapter=ChangedPlanetAdapter(),
    )
    assert (
        cusp_report.planet_margins["Sun"]["D1"].longitude_deg
        != changed_report.planet_margins["Sun"]["D1"].longitude_deg
    )
    assert cusp_report.receipt_sha256 != changed_report.receipt_sha256


def test_benchmark_horizons_iae_positive_and_negative_controls() -> None:
    """Verify live Horizons/IAE benchmark passes clean engine and rejects 1-degree planetary or anchor perturbations."""
    import contextlib
    import importlib.util
    import io

    bench_path = Path(__file__).resolve().parent.parent / "tools" / "benchmark_horizons_iae.py"

    def _load_bench():  # type: ignore[no-untyped-def]
        spec = importlib.util.spec_from_file_location("benchmark_horizons_iae_probe", bench_path)
        assert spec is not None and spec.loader is not None
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        return mod

    def _run_quietly(mod):  # type: ignore[no-untyped-def]
        with contextlib.redirect_stdout(io.StringIO()):
            return mod.run_benchmark()

    # 1. Clean positive control
    clean_mod = _load_bench()
    clean_report = _run_quietly(clean_mod)
    assert clean_report["status"] == "PASS"
    assert clean_report["nasa_jpl_horizons"]["total_samples"] == 2100
    assert clean_report["nasa_jpl_horizons"]["overall_max_separation_arcsec"] < 0.05
    assert clean_report["nasa_jpl_horizons"]["status"] == "PASS_TIED_WITH_HORIZONS"
    assert clean_report["iae_lahiri_anchor"]["status"] == "CONVENTION_REGRESSION_ONLY"
    assert clean_report["iae_lahiri_anchor"]["check_classification"] == "CONVENTION_REGRESSION_ONLY"
    assert clean_report["iae_lahiri_anchor"]["independent_external_verification"] is False
    assert (
        clean_report["iae_lahiri_anchor"]["unverified_1989_01_01_tabular_candidate"]["status"]
        == "HELD_UNVERIFIED_PRIMARY_BOOK_PAGE"
    )

    # 2. Negative control: +1 deg anchor perturbation cannot pass
    bad_anchor_mod = _load_bench()
    real_ayanamsa = bad_anchor_mod.ayanamsa_degrees
    bad_anchor_mod.ayanamsa_degrees = lambda *args, **kwargs: real_ayanamsa(*args, **kwargs) + 1.0
    bad_anchor_report = _run_quietly(bad_anchor_mod)
    assert bad_anchor_report["status"] == "FAIL"
    assert bad_anchor_report["iae_lahiri_anchor"]["status"].startswith("FAIL")
    assert not bad_anchor_report["iae_lahiri_anchor"]["status"].startswith("PASS")

    # 3. Negative control: +1 deg planetary longitude perturbation cannot pass
    bad_planet_mod = _load_bench()
    real_engine = bad_planet_mod.Engine

    class IncorrectEngine:
        @classmethod
        def load(cls, **kwargs):  # type: ignore[no-untyped-def]
            return cls(real_engine.load(**kwargs))

        def __init__(self, eng):  # type: ignore[no-untyped-def]
            self.engine = eng

        def __enter__(self):  # type: ignore[no-untyped-def]
            return self

        def __exit__(self, *args):  # type: ignore[no-untyped-def]
            self.engine.close()

        def positions_tt(self, *args, **kwargs):  # type: ignore[no-untyped-def]
            res = self.engine.positions_tt(*args, **kwargs)
            changed = {
                body: {**pos, "longitude_deg": (pos["longitude_deg"] + 1.0) % 360.0}
                for body, pos in res.value.items()
            }
            return replace(res, value=changed)

    bad_planet_mod.Engine = IncorrectEngine
    bad_planet_report = _run_quietly(bad_planet_mod)
    assert bad_planet_report["status"] == "FAIL"
    assert not bad_planet_report["nasa_jpl_horizons"]["status"].startswith("PASS")


def test_varga_transition_solver_preserves_first_crossing_and_linear_control() -> None:
    """Verify _solve_varga_transition_seconds preserves the first crossing on a leave-and-return arc and matches linear control."""
    import math
    from ephemeris_oss.impossible_astrology import _solve_varga_transition_seconds

    day_sec = 86400.0

    def _solve(callback):  # type: ignore[no-untyped-def]
        return (
            _solve_varga_transition_seconds(
                "Sun",
                12.0,
                0,
                "D1",
                12.0,
                18.0,
                30.0,
                1.0 / day_sec,
                1.0,
                callback,
            )
            / day_sec
        )

    # 1. Linear clean control
    assert abs(_solve(lambda seconds: 12.0 + seconds / day_sec) - 18.0) < 1.0e-5

    # 2. Leave-and-return excursion before 0.85 * t_est preserves the first crossing (~4.09858 days)
    def _excursion_longitude(seconds: float) -> float:
        t = seconds / day_sec
        return 12.0 + t + 25.0 * (math.sin(math.pi * t / 15.3) ** 2)

    low, high = 4.0, 5.0
    assert _excursion_longitude(low * day_sec) < 30.0 < _excursion_longitude(high * day_sec)
    for _ in range(48):
        mid = 0.5 * (low + high)
        if _excursion_longitude(mid * day_sec) < 30.0:
            low = mid
        else:
            high = mid
    actual_first_days = 0.5 * (low + high)
    predicted_days = _solve(_excursion_longitude)
    assert abs(predicted_days - actual_first_days) * day_sec < 0.5


def test_mcp_stdio_keeps_connection_alive_on_malformed_and_non_object_json() -> None:
    """Verify serve_stdio recovers cleanly from malformed JSON (-32700) and non-object JSON [] / null (-32600)."""
    import io
    from ephemeris_oss import mcp_server

    ping_line = '{"jsonrpc":"2.0","id":7,"method":"ping"}\n'

    # 1. Malformed JSON clean control
    out_malformed = io.StringIO()
    assert mcp_server.serve_stdio(io.StringIO("{bad\n" + ping_line), out_malformed) == 0
    replies_malformed = [json.loads(line) for line in out_malformed.getvalue().splitlines()]
    assert replies_malformed[0]["error"]["code"] == -32700
    assert replies_malformed[1]["id"] == 7

    # 2. Syntactically valid non-object JSON ([] and null)
    for invalid_msg in ("[]", "null"):
        out_non_obj = io.StringIO()
        assert mcp_server.serve_stdio(io.StringIO(invalid_msg + "\n" + ping_line), out_non_obj) == 0
        replies = [json.loads(line) for line in out_non_obj.getvalue().splitlines()]
        assert replies[0]["error"]["code"] == -32600
        assert replies[1]["id"] == 7


def test_mcp_daily_panchanga_anchors_to_local_sunrise_and_separates_instantaneous(monkeypatch) -> None:  # type: ignore[no-untyped-def]
    """Verify MCP compute_panchanga resolves observer local sunrise, handles before-sunrise and daytime transitions, and keeps instantaneous separate."""
    from ephemeris_oss import mcp_server
    from ephemeris_oss.almanac import regional_panchang

    # 1. Direct instrumentation verifying sunrise_jd_ut is passed to regional_panchang.compute_panchanga
    captured: dict[str, object] = {}

    class _CapturedCall(Exception):
        pass

    def _capture_call(**kwargs: object) -> None:
        captured.update(kwargs)
        raise _CapturedCall

    with monkeypatch.context() as m:
        m.setattr(regional_panchang, "compute_panchanga", _capture_call)
        try:
            mcp_server.execute_mcp_tool(
                "compute_panchanga",
                {"jd_ut": 2461139.0, "latitude_deg": 28.6139, "longitude_deg": 77.2090},
            )
        except _CapturedCall:
            pass
    assert captured.get("sunrise_jd_ut") is not None

    # 2. End-to-end daytime transition and before-sunrise anchoring for Delhi (28.6139 N, 77.2090 E)
    # Scan a day where Tithi transitions during daytime after local sunrise:
    base_jd = 2461135.0
    transition_day_sr: float | None = None
    for day_idx in range(15):
        probe_jd = base_jd + float(day_idx)
        rep_morning = mcp_server.execute_mcp_tool(
            "compute_panchanga",
            {"jd_ut": probe_jd - 0.10, "latitude_deg": 28.6139, "longitude_deg": 77.2090},
        )
        sr_jd = float(rep_morning["sunrise_jd_ut"])
        rep_after_sr = mcp_server.execute_mcp_tool(
            "compute_panchanga",
            {"jd_ut": sr_jd + 0.05, "latitude_deg": 28.6139, "longitude_deg": 77.2090},
        )
        rep_evening = mcp_server.execute_mcp_tool(
            "compute_panchanga",
            {"jd_ut": sr_jd + 0.45, "latitude_deg": 28.6139, "longitude_deg": 77.2090},
        )
        # In sunrise-anchored mode, two instants after sunrise on the same civil day share the same daily Tithi and Vara
        assert rep_after_sr["anchoring_mode"] == "sunrise"
        assert rep_evening["anchoring_mode"] == "sunrise"
        assert rep_after_sr["active_sunrise_jd_ut"] == rep_evening["active_sunrise_jd_ut"] == sr_jd
        assert rep_after_sr["tithi_number"] == rep_evening["tithi_number"]
        assert rep_after_sr["vara_name"] == rep_evening["vara_name"]

        # Before-sunrise instant (sr_jd - 0.05) anchors to the preceding Vedic day's sunrise and preceding weekday
        rep_before_sr = mcp_server.execute_mcp_tool(
            "compute_panchanga",
            {"jd_ut": sr_jd - 0.05, "latitude_deg": 28.6139, "longitude_deg": 77.2090},
        )
        assert rep_before_sr["active_sunrise_jd_ut"] < sr_jd
        assert rep_before_sr["vara_name"] != rep_after_sr["vara_name"]

        if rep_after_sr["instantaneous_panchanga"]["tithi_number"] != rep_evening["instantaneous_panchanga"]["tithi_number"]:
            transition_day_sr = sr_jd
            # Even though the instantaneous Tithi transitioned during the day, the daily sunrise-anchored Tithi stayed invariant,
            # while explicit mode="instantaneous" reports the new Tithi at sr_jd + 0.45
            rep_inst_evening = mcp_server.execute_mcp_tool(
                "compute_panchanga",
                {
                    "jd_ut": sr_jd + 0.45,
                    "latitude_deg": 28.6139,
                    "longitude_deg": 77.2090,
                    "mode": "instantaneous",
                },
            )
            assert rep_inst_evening["anchoring_mode"] == "instantaneous"
            assert rep_inst_evening["tithi_number"] == rep_evening["instantaneous_panchanga"]["tithi_number"]
            assert rep_inst_evening["tithi_number"] != rep_evening["tithi_number"]
            break

    assert transition_day_sr is not None

    # 3. Eastern observer (Tokyo, longitude +139.69 deg) whose local sunrise falls on the preceding UTC calendar date
    from datetime import date

    observer_cases = [
        ("Delhi after sunrise", 28.6139, 77.2090, 2461046.625, date(2026, 1, 6).strftime("%A")),
        ("Tokyo after sunrise", 35.68, 139.69, 2461046.625, date(2026, 1, 6).strftime("%A")),
        ("Tokyo before sunrise", 35.68, 139.69, 2461046.3333333335, date(2026, 1, 5).strftime("%A")),
    ]
    for city, lat, lon, jd_req, expected_weekday in observer_cases:
        obs_report = mcp_server.execute_mcp_tool(
            "compute_panchanga",
            {"jd_ut": jd_req, "latitude_deg": lat, "longitude_deg": lon},
        )
        assert obs_report["anchoring_mode"] == "sunrise", city
        assert obs_report["active_sunrise_jd_ut"] <= jd_req, city
        assert obs_report["vara_name"] == expected_weekday, (city, obs_report["vara_name"], expected_weekday)


def test_round5_release_reconciliation_contracts(monkeypatch) -> None:  # type: ignore[no-untyped-def]
    """Verify all Round 5 release contracts: console --dump-tools, complete Kundali vargas/dashas,
    Panchanga ayanamsa forwarding, provider eclipse distances, short horizon passage recovery,
    contiguous war deduplication, TT-to-UTC conversion, war minimum refinement, and direction-reversal step ceiling.
    """
    import math
    import subprocess
    import sys
    from datetime import datetime
    import erfa
    from ephemeris_oss import Engine, impossible_astrology, mcp_server
    from ephemeris_oss.engine.eclipses import _evaluate_sun_moon
    from ephemeris_oss.engine.events import SolverPolicy, solve_rise_set_transit

    # 1. Console entry point --dump-tools
    console = subprocess.run(
        [sys.executable, "-c", "from ephemeris_oss.mcp_server import main; raise SystemExit(main())", "--dump-tools"],
        input="",
        text=True,
        capture_output=True,
        check=True,
    )
    assert len(json.loads(console.stdout)["tools"]) == 20

    # 2. Complete Kundali exposes divisional charts and Dasha timelines
    kundali = mcp_server.execute_mcp_tool("compute_complete_kundali", {"jd_ut": 2461139.0})
    assert {
        "planet_vargas",
        "lagna_vargas",
        "vimshottari_dasha",
        "ashtottari_dasha",
        "yogini_dasha",
        "chara_dasha",
    } <= set(kundali.keys())

    # 3. Panchanga honors advertised ayanamsa
    p_lahiri = mcp_server.execute_mcp_tool("compute_panchanga", {"jd_ut": 2461139.0, "mode": "instantaneous", "ayanamsa": "lahiri"})
    p_raman = mcp_server.execute_mcp_tool("compute_panchanga", {"jd_ut": 2461139.0, "mode": "instantaneous", "ayanamsa": "raman"})
    assert abs(p_lahiri["sun_sidereal_lon_deg"] - p_raman["sun_sidereal_lon_deg"]) > 1.0
    assert p_lahiri["receipt_sha256"] != p_raman["receipt_sha256"]

    # 4. Provider eclipse adapter retains numerical distances
    with Engine.load(kernels="compact") as engine:
        numerical = _evaluate_sun_moon(2461139.0, engine=engine)
        provider = engine._provider
        callback = lambda epoch, bodies: provider.planet_positions_tt(jd_tt=epoch, bodies=bodies)["positions"]
        adapted = _evaluate_sun_moon(2461139.0, position_provider=callback)
    for idx in (0, 1):
        assert abs(adapted[idx]["distance_km"] - numerical[idx]["distance_km"]) < 0.001

    # 5. Reduced horizon policy keeps short passage after existing crossing
    lat_r = math.radians(70.0)
    dec_r = math.radians(19.999)

    def _alt(t: float) -> float:
        ha = math.pi + 2.0 * math.pi * (t - 0.0003) / 0.99726957
        return math.degrees(math.asin(math.sin(lat_r) * math.sin(dec_r) + math.cos(lat_r) * math.cos(dec_r) * math.cos(ha)))

    ctrl_h = solve_rise_set_transit(_alt, 0.0, 1.0)
    cand_h = solve_rise_set_transit(
        _alt,
        0.0,
        1.0,
        policy=SolverPolicy(sample_count=19, subdivision_depth=0, time_tolerance_days=1e-7, max_iterations=40),
    )
    assert len(ctrl_h.horizon_events) == 3
    assert len(cand_h.horizon_events) == 3

    # 6. Contiguous war deduplication, numerical DE440 provider binding (1550-2306 wings), OpenAPI requestBody schemas, and TT-to-UTC conversion
    from ephemeris_oss.api_server import _ROUTE_TO_TOOL, build_openapi_spec

    openapi_spec = build_openapi_spec()
    tool_schemas = {t["name"]: t["inputSchema"] for t in mcp_server.MCP_TOOLS}
    for route_path, tool_name in _ROUTE_TO_TOOL.items():
        rb = openapi_spec["paths"][route_path]["post"]["requestBody"]
        assert rb["content"]["application/json"]["schema"] == tool_schemas[tool_name]

    for wing_yr in (1550, 1599, 1700, 2200):
        jd_wing = float(sum(erfa.cal2jd(wing_yr, 6, 1)))
        rep_wing = impossible_astrology.scan_multi_century_rare_phenomena(jd_wing, jd_wing + 0.25, bodies=("mercury", "venus"))
        assert rep_wing.ephemeris_source == "compact-de440-numerical"

    war_rep = impossible_astrology.scan_multi_century_rare_phenomena(2461041.5, 2461081.5, bodies=("mercury", "venus"))
    assert war_rep.ephemeris_source == "compact-de440-numerical"
    jan_events = [ev for ev in war_rep.graha_yuddha_events if 2461068.0 <= ev["jd_tt"] <= 2461072.0]
    assert len(jan_events) == 1
    assert jan_events[0]["ephemeris_source"] == "compact-de440-numerical"
    tai = erfa.tttai(2451545.0, war_rep.start_jd_tt - 2451545.0)
    expected_utc = sum(erfa.taiutc(*tai))
    parsed_dt = datetime.fromisoformat(war_rep.start_iso_utc.replace("Z", "+00:00"))
    actual_utc = EphemerisAdapter.julday(
        parsed_dt.year,
        parsed_dt.month,
        parsed_dt.day,
        parsed_dt.hour + parsed_dt.minute / 60.0 + (parsed_dt.second + parsed_dt.microsecond / 1e6) / 3600.0,
    )
    assert abs(actual_utc - expected_utc) * 86400.0 < 0.01

    # 7. Direction-reversal near cusp updates step ceiling and converges
    def _rev_lon(offset_sec: float) -> float:
        t_days = offset_sec / 86400.0
        return (29.9999 + 0.001 * t_days - 0.01 * t_days * t_days) % 360.0

    t_exit = impossible_astrology._solve_varga_transition_seconds(
        body="Jupiter",
        varga_key="D1",
        lon0=29.9999,
        current_sign=0,
        deg_from_lower=29.9999,
        deg_to_upper=0.0001,
        sector_span=30.0,
        speed_deg_per_sec=0.001 / 86400.0,
        dir_sign=1.0,
        position_at_offset_sec=_rev_lon,
    )
    expected_days = (0.001 + math.sqrt(0.001 * 0.001 + 4.0 * 0.01 * 29.9999)) / (2.0 * 0.01)
    assert abs(t_exit - expected_days * 86400.0) < 0.05

    # 8. War minimum refinement between sample epochs
    start_w = 2451545.0
    center_w = start_w + 1.37

    def _mock_pos(body: str, jd: float) -> dict[str, float]:
        return {
            "longitude_deg": 30.0 + ((jd - center_w) ** 2 if body == "venus" else 0.0),
            "latitude_deg": 0.1 if body == "venus" else 0.0,
        }

    monkeypatch.setattr(impossible_astrology, "_builtin_planet_apparent", _mock_pos)
    monkeypatch.setattr(impossible_astrology, "find_retrograde_stations", lambda *a, **kw: ())
    monkeypatch.setattr(impossible_astrology, "find_combustion_windows", lambda *a, **kw: ())
    rep_w = impossible_astrology.scan_multi_century_rare_phenomena(start_w, start_w + 3.0, bodies=("mercury", "venus"))
    assert len(rep_w.graha_yuddha_events) == 1
    assert abs(rep_w.graha_yuddha_events[0]["jd_tt"] - center_w) * 86400.0 < 0.5

    # 9. Short 0.1-day interval samples the clamped endpoint when separation enters war threshold near end
    def _mock_endpoint_pos(body: str, jd: float) -> dict[str, float]:
        frac = (jd - start_w) / 0.1
        sep = 1.05 - 0.10 * frac
        return {
            "longitude_deg": 30.0 + (sep if body == "venus" else 0.0),
            "latitude_deg": 0.1 if body == "venus" else 0.0,
        }

    monkeypatch.setattr(impossible_astrology, "_builtin_planet_apparent", _mock_endpoint_pos)
    rep_short = impossible_astrology.scan_multi_century_rare_phenomena(start_w, start_w + 0.1, bodies=("mercury", "venus"))
    assert len(rep_short.graha_yuddha_events) == 1
    assert abs(rep_short.graha_yuddha_events[0]["jd_tt"] - (start_w + 0.1)) < 1.0e-5


def test_true_node_in_calc_ut_kundali_mcp_openapi_and_legal_docs() -> None:
    """Verify True (osculating) vs Mean Rahu/Ketu in calc_ut (including 1550/2306 TDB endpoints), kundali bundle, MCP tools, OpenAPI responses, and legal/limitations docs."""
    import erfa
    import math
    from pathlib import Path
    from ephemeris_oss import EphemerisAdapter, build_openapi_spec, execute_mcp_tool

    adapter = EphemerisAdapter()
    for jd_probe in (2461139.0, 588465.5):
        mean_rahu = adapter.calc_ut(jd_probe, "rahu", sidereal=True)
        true_rahu_flag = adapter.calc_ut(jd_probe, "rahu", sidereal=True, true_node=True)
        true_rahu_alias = adapter.calc_ut(jd_probe, "true_node", sidereal=True)
        true_ketu = adapter.calc_ut(jd_probe, "true_ketu", sidereal=True)

        assert abs(true_rahu_flag.longitude_deg - true_rahu_alias.longitude_deg) < 1.0e-9
        assert abs(true_rahu_flag.longitude_deg - mean_rahu.longitude_deg) > 1.0e-3
        assert abs(((true_rahu_flag.longitude_deg + 180.0) % 360.0) - true_ketu.longitude_deg) < 1.0e-9

    # Verify true_node within 0.0005 days of both embedded TDB endpoints (2287184.5005 and 2563392.4995)
    def _tdb_for_ut(jd_ut_val: float) -> float:
        tt_val = adapter._jd_ut_to_jd_tt(jd_ut_val)
        pair = (2451545.0, tt_val - 2451545.0)
        off = float(erfa.dtdb(*pair, 0.0, 0.0, 0.0, 0.0))
        return float(sum(erfa.tttdb(*pair, off)))

    for target_tdb in (2287184.5005, 2563392.4995):
        lo, hi = target_tdb - 1.0, target_tdb + 1.0
        for _ in range(38):
            mid = 0.5 * (lo + hi)
            if _tdb_for_ut(mid) < target_tdb:
                lo = mid
            else:
                hi = mid
        jd_ut_edge = 0.5 * (lo + hi)
        adapter._engine._provider._kernel_registry.artifact_for_tdb_jd(_tdb_for_ut(jd_ut_edge))
        edge_true = adapter.calc_ut(jd_ut_edge, "rahu", sidereal=True, true_node=True)
        edge_ketu = adapter.calc_ut(jd_ut_edge, "true_ketu", sidereal=True)
        assert math.isfinite(edge_true.longitude_deg)
        assert math.isfinite(edge_true.longitude_speed_deg_per_day)
        assert abs(((edge_true.longitude_deg + 180.0) % 360.0) - edge_ketu.longitude_deg) < 1.0e-9

    bundle_mean = adapter.compute_complete_kundali_bundle(2461139.0, 28.6139, 77.2090, include_svg=False)
    bundle_true = adapter.compute_complete_kundali_bundle(
        2461139.0, 28.6139, 77.2090, true_node=True, include_svg=False
    )
    assert bundle_mean.positions["rahu"].longitude_deg != bundle_true.positions["rahu"].longitude_deg
    assert bundle_mean.bundle_receipt_sha256 != bundle_true.bundle_receipt_sha256

    mcp_pos_true = execute_mcp_tool(
        "compute_planetary_positions",
        {"jd_ut": 2461139.0, "true_node": True},
    )
    assert mcp_pos_true["node_mode"] == "true"
    assert abs(
        mcp_pos_true["planets"]["rahu"]["longitude_deg"] - bundle_true.positions["rahu"].longitude_deg
    ) < 1.0e-9

    spec = build_openapi_spec()
    for path_key, path_item in spec["paths"].items():
        for method_key, op in path_item.items():
            assert "responses" in op, f"{method_key.upper()} {path_key} missing responses"
            assert "200" in op["responses"]
            if method_key == "post":
                assert "400" in op["responses"]
                assert "413" in op["responses"]

    repo_root = Path(__file__).resolve().parents[1]
    for rel_doc in (
        "NOTICE",
        "docs/TRADEMARK-AND-COMMERCIAL-BOUNDARY.md",
        "docs/JYOTISH-CAPABILITIES-AND-CONVENTIONS.md",
        "docs/ROADMAP-AND-LIMITATIONS.md",
        "docs/EXPERT-TESTER-COHORT-REPORT.md",
    ):
        assert (repo_root / rel_doc).is_file(), f"Missing {rel_doc}"

    roadmap_txt = (repo_root / "docs/ROADMAP-AND-LIMITATIONS.md").read_text(encoding="utf-8")
    assert "<= 0.018191 arcsec" in roadmap_txt
    assert "UNVERIFIED against a primary ancient numerical ephemeris" in roadmap_txt

    cohort_txt = (repo_root / "docs/EXPERT-TESTER-COHORT-REPORT.md").read_text(encoding="utf-8")
    assert "Internal AI Role Analysis, Not an External Human Expert Cohort" in cohort_txt
    assert "4dc841fe-b60e-4d5c-9c09-fda77e6deb80" in cohort_txt


def test_personalized_astro_fingerprint_across_sdk_cli_mcp_and_rest_api() -> None:
    """Verify compute_personalized_astro_fingerprint across Python SDK, CLI, MCP, and REST API."""
    from ephemeris_oss.cli import main as cli_main

    # 1. Python SDK
    fp = compute_personalized_astro_fingerprint(
        2461320.0,
        latitude_deg=28.6139,
        longitude_deg=77.2090,
        query_jd_ut=2461350.0,
        birth_time_uncertainty_seconds=60.0,
        ayanamsa="lahiri",
    )
    assert len(fp.fingerprint_id_sha256) == 64
    assert len(fp.receipt_sha256) == 64
    assert 0.0 <= fp.overall_clock_confidence_score <= 1.0
    assert 0.0 <= fp.overall_personal_transit_resonance_score <= 100.0
    assert len(fp.domain_clock_confidence) == 16
    assert len(fp.harmonic_phase_matrix) == 10
    assert len(fp.topocentric_digbala_vector) == 7
    assert len(fp.personal_transit_resonance) == 7

    # 2. MCP tool execution
    mcp_res = execute_mcp_tool(
        "compute_personalized_astro_fingerprint",
        {
            "jd_ut": 2461320.0,
            "query_jd_ut": 2461350.0,
            "latitude_deg": 28.6139,
            "longitude_deg": 77.2090,
            "birth_time_uncertainty_seconds": 60.0,
            "ayanamsa": "lahiri",
        },
    )
    assert mcp_res["fingerprint_id_sha256"] == fp.fingerprint_id_sha256
    assert mcp_res["receipt_sha256"] == fp.receipt_sha256

    # 3. CLI subcommand `ephemeris-oss fingerprint`
    rc = cli_main(
        [
            "fingerprint",
            "--jd",
            "2461320.0",
            "--query-jd",
            "2461350.0",
            "--lat",
            "28.6139",
            "--lon",
            "77.2090",
            "--uncertainty-sec",
            "60",
            "--compact",
        ]
    )
    assert rc == 0

    # 4. REST API `POST /v1/fingerprint`
    status, api_payload = dispatch_api_request(
        "POST",
        "/v1/fingerprint",
        {
            "jd_ut": 2461320.0,
            "query_jd_ut": 2461350.0,
            "latitude_deg": 28.6139,
            "longitude_deg": 77.2090,
            "birth_time_uncertainty_seconds": 60.0,
        },
    )
    assert status == 200
    assert api_payload["fingerprint_id_sha256"] == fp.fingerprint_id_sha256
    assert api_payload["receipt_sha256"] == fp.receipt_sha256

    # 5. Verify full-span 9,074-month benchmark & white paper artifacts exist and are valid
    repo_root = Path(__file__).resolve().parents[1]
    monthly_bench = json.loads(
        (repo_root / "evidence/monthly-full-span-de440-benchmark.json").read_text(encoding="utf-8")
    )
    assert monthly_bench["monthly_embedded_de440_vs_full_de440_bsp"]["months_evaluated"] == 9074
    assert monthly_bench["monthly_embedded_de440_vs_full_de440_bsp"]["samples_evaluated"] == 63518
    assert monthly_bench["monthly_embedded_de440_vs_full_de440_bsp"]["failures"] == 0
    assert (repo_root / "docs/RDG-EPHEMERIS-WHITEPAPER-AND-BENCHMARKS.md").is_file()
    assert (repo_root / "docs/AI-MCP-AND-PLUGIN-INTEGRATION-GUIDE.md").is_file()


@pytest.mark.parametrize("true_node", [False, True], ids=["mean-node", "true-node"])
def test_personalized_astro_fingerprint_selected_node_divisional_consistency(true_node: bool) -> None:
    """Ensure Rahu and Ketu varga_phases, D9, and D60 metadata match the selected node mode."""
    report = compute_personalized_astro_fingerprint(2461139.0, true_node=true_node)
    assert report.true_node is true_node
    for body in ("Rahu", "Ketu"):
        matrix = report.harmonic_phase_matrix[body]
        lon = float(matrix["sidereal_longitude_deg"])
        for v_key, phase in matrix["varga_phases"].items():
            expected = varga_sign(lon, v_key)
            assert phase["sign_name"] == expected.sign_name, (true_node, body, v_key)
            assert phase["sign_lord"] == expected.sign_lord, (true_node, body, v_key)
        d60_expected = varga_sign(lon, "D60")
        assert matrix["d60_shashtiamsa_name"] == d60_expected.shashtiamsa_name
        assert matrix["d60_shashtiamsa_is_benefic"] == d60_expected.shashtiamsa_is_benefic


def test_public_utc_and_supplied_callback_lunar_interval_straddle() -> None:
    """Verify public UTC positions() and supplied-callback _apparent_state share the lunar 16-day straddle fix."""
    from datetime import datetime, timedelta, timezone
    import math
    from ephemeris_oss import Engine
    from ephemeris_oss.engine.numerical_provider import TimeScaleState

    target_tdb = 2460032.5 + (0.4 / 86400.0)
    with Engine.load(kernels="compact", eop=None) as compact:
        instant = datetime(2000, 1, 1, 12, tzinfo=timezone.utc) + timedelta(days=target_tdb - 2451545.0)
        for _ in range(3):
            instant += timedelta(days=target_tdb - compact._provider.utc_time_scales(instant).tdb_jd)
        times = compact._provider.utc_time_scales(instant)
        assert abs(times.tdb_jd - target_tdb) < 1.0e-8

        tt_pos = compact.positions_tt(times.tt_jd, ("moon",), jd_tdb=times.tdb_jd, mean_equinox=True).value["moon"]
        utc_pos = compact.positions(instant, ("moon",)).value["moon"]
        diff_deg = abs((tt_pos["longitude_deg"] - utc_pos["longitude_deg"] + 180.0) % 360.0 - 180.0)
        assert diff_deg * 3600.0 < 0.001

        ts = TimeScaleState((math.nan, math.nan), (2451545.0, target_tdb - 2451545.0), (2451545.0, target_tdb - 2451545.0))
        res_default, _ = compact._provider._apparent_state(
            body="moon",
            instant_utc=None,
            kernel_year=2023,
            observer=None,
            times=ts,
            apply_deflection=True,
            apply_aberration=True,
            precomputed_target_func=None,
        )
        res_cb, _ = compact._provider._apparent_state(
            body="moon",
            instant_utc=None,
            kernel_year=2023,
            observer=None,
            times=ts,
            apply_deflection=True,
            apply_aberration=True,
            precomputed_target_func=lambda at: compact._provider.barycentric_state_at_tdb(
                body="moon",
                tdb=(2451545.0, at - 2451545.0),
                kernel_year=2023,
            ),
        )
        assert res_default.apparent_vector_km == res_cb.apparent_vector_km


@pytest.mark.parametrize("sigma", [0.0, 0.1, 2.0], ids=["exact-clock", "subsecond-clock", "two-second-control"])
def test_actual_uncertainty_sets_near_cusp_status(sigma: float) -> None:
    """Verify subsecond and zero birth_time_uncertainty_seconds govern stability_classification without a 1s floor."""
    from ephemeris_oss import compute_personalized_astro_fingerprint, solve_subsecond_shodashvarga_cusp_transitions

    base = 2461139.0
    margins = solve_subsecond_shodashvarga_cusp_transitions(base, 28.6139, 77.2090)
    near_cusp_jd = base + (margins.ascendant_margins["D60"].seconds_to_next_cusp - 0.5) / 86400.0
    report = compute_personalized_astro_fingerprint(near_cusp_jd, birth_time_uncertainty_seconds=sigma)
    domain = report.domain_clock_confidence["D60"]
    tau = domain["governing_cusp_margin_seconds"]
    assert 0.45 < tau < 0.55
    expected = (
        "LOCKED_INVARIANT"
        if tau >= 3.0 * sigma
        else "MODERATELY_SENSITIVE"
        if tau >= sigma
        else "RECTIFICATION_REQUIRED"
    )
    assert domain["stability_classification"] == expected




