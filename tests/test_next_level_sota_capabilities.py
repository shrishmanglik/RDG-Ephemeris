"""Tests for Next-Level SOTA Capabilities in RDG-Ephemeris (`ephemeris-oss`).

Covers:
1. BPHS Kalachakra Dasha ("The Wheel of Time": Savya/Apasavya 27x4 Padas, Paramayus 83/85/86/100, Deha/Jeeva, Gati jumps).
2. 30-Star Gaia/Hipparcos ICRS Yogatara Catalog, Stellar Bheda, Rohini Shakata Bheda, and Kalansha visibility.
3. Outer Planets (Uranus/Aruna, Neptune/Varuna, Pluto/Yama) and Physical Disk-Centre (NAIF 499/599/699) recoil offsets.
4. Exact Krantisamya (Vyatipata & Vaidhriti Mahapata) solar-lunar declination equality root solver.
5. Inverse Sky-to-Date "Astronomical Time-Machine" solver across multi-year spans.
6. Triple-Lock Life-Event Peak Window Convergence solver (Multi-Dasha + Guru-Shani Double Transit + 8-Kakshya & Bhrigu Bindu).
7. MCP JSON-RPC and OpenAPI 3.1 REST endpoints for the new solvers.
"""

from __future__ import annotations

import math
import pytest

from ephemeris_oss import (
    EphemerisAdapter,
    YOGATARA_30_CATALOG,
    build_openapi_spec,
    classify_kalachakra_gati,
    compute_kalachakra_dasha,
    compute_triple_lock_life_event_convergence,
    dispatch_api_request,
    evaluate_yogatara_stellar_bheda_and_visibility,
    execute_mcp_tool,
    propagate_yogatara_apparent,
    solve_chart_date_from_planetary_constraints,
    solve_krantisamya_mahapata_windows,
)
from ephemeris_oss.jyotish.dasha import (
    KALACHAKRA_APASAVYA_SEQUENCES,
    KALACHAKRA_SAVYA_NAKSHATRAS,
    KALACHAKRA_SAVYA_SEQUENCES,
    KALACHAKRA_SIGN_YEARS,
)


def test_kalachakra_dasha_all_27_nakshatras_and_4_padas() -> None:
    """Verify BPHS Kalachakra Dasha across all 27 Nakshatras x 4 Padas (108 Padas total)."""
    valid_paramayus = {83.0, 85.0, 86.0, 100.0}

    for (grp, pada), seq in KALACHAKRA_SAVYA_SEQUENCES.items():
        assert len(seq) == 9
        total_yrs = sum(KALACHAKRA_SIGN_YEARS[s] for s in seq)
        assert total_yrs in valid_paramayus, f"Savya group {grp} pada {pada}"

    for (grp, pada), seq in KALACHAKRA_APASAVYA_SEQUENCES.items():
        assert len(seq) == 9
        total_yrs = sum(KALACHAKRA_SIGN_YEARS[s] for s in seq)
        assert total_yrs in valid_paramayus, f"Apasavya group {grp} pada {pada}"

    # Verify Savya vs Apasavya alternation across all 27 Nakshatras (9 triplets of 3)
    assert len(KALACHAKRA_SAVYA_NAKSHATRAS) == 15  # 5 triplets of 3 = 15 Savya, 4 triplets of 3 = 12 Apasavya

    # Test Savya Nakshatra (Ashwini Pada 1 -> Moon at 1.0 deg Mesha)
    kc_savya = compute_kalachakra_dasha(1.0, 2451545.0)
    assert kc_savya.chakra_group == "Savya"
    assert kc_savya.nakshatra_name == "Ashwini"
    assert kc_savya.pada == 1
    assert kc_savya.paramayus_years == 100.0
    assert kc_savya.deha_sign_name == "Mesha"
    assert kc_savya.jeeva_sign_name == "Dhanu"
    assert len(kc_savya.mahadashas) == 9
    assert len(kc_savya.mahadashas[1].sub_periods) == 9

    # Test Apasavya Nakshatra (Rohini Pada 1 -> Moon at 41.0 deg Vrishabha)
    kc_apasavya = compute_kalachakra_dasha(41.0, 2451545.0)
    assert kc_apasavya.chakra_group == "Apasavya"
    assert kc_apasavya.nakshatra_name == "Rohini"
    assert kc_apasavya.pada == 1
    assert kc_apasavya.paramayus_years == 100.0
    # For Apasavya, Jeeva is the first sign and Deha is the last sign
    assert kc_apasavya.jeeva_sign_name == "Vrishchika"
    assert kc_apasavya.deha_sign_name == "Meena"

    # Verify Gati classifications (Simhavalokana, Mandooka, Markata)
    assert classify_kalachakra_gati(3, 4)[0] == "Markata Gati"  # Karka <-> Simha
    assert classify_kalachakra_gati(5, 3)[0] == "Mandooka Gati"  # Kanya -> Karka (-2)
    assert classify_kalachakra_gati(4, 2)[0] == "Mandooka Gati"  # Simha -> Mithuna (+10)
    assert classify_kalachakra_gati(11, 3)[0] == "Simhavalokana Gati"  # Meena -> Karka (+4)

    with pytest.raises(ValueError, match="must be finite"):
        compute_kalachakra_dasha(float("nan"), 2451545.0)


def test_30_star_yogatara_catalog_and_stellar_bheda_solver() -> None:
    """Verify all 30 Yogataras propagate cleanly and evaluate Tara Bheda & Kalansha visibility."""
    assert len(YOGATARA_30_CATALOG) == 30
    keys = {s.key for s in YOGATARA_30_CATALOG}
    assert "chitra" in keys
    assert "rohini" in keys
    assert "abhijit" in keys
    assert "agastya" in keys
    assert "lubdhaka" in keys

    chitra = next(s for s in YOGATARA_30_CATALOG if s.key == "chitra")
    pos = propagate_yogatara_apparent(chitra, tt=(2451545.0, 0.0), ayanamsa_deg=23.85, sun_tropical_lon_deg=280.0)
    assert 203.0 <= pos.tropical_longitude_deg <= 204.5
    assert -2.5 <= pos.ecliptic_latitude_shara_deg <= -1.5

    report = evaluate_yogatara_stellar_bheda_and_visibility(2461350.0, orb_deg=3.0)
    assert report.yogatara_count == 30
    assert report.visible_star_count + report.combust_star_count == 30
    assert len(report.yogatara_states) == 30
    assert len(report.receipt_sha256) == 64


def test_outer_planets_and_physical_center_recoil_offsets() -> None:
    """Verify Uranus/Neptune/Pluto and NAIF 499/599/699 physical disk-centre recoil offsets."""
    adapter = EphemerisAdapter()
    jd = 2461350.0

    # Outer planets inside 1550-2306 CE
    uranus = adapter.calc_ut(jd, "uranus", sidereal=True)
    neptune = adapter.calc_ut(jd, "neptune", sidereal=True)
    pluto = adapter.calc_ut(jd, "pluto", sidereal=True)
    aruna = adapter.calc_ut(jd, "aruna", sidereal=True)
    assert 0.0 <= uranus.longitude_deg < 360.0
    assert 0.0 <= neptune.longitude_deg < 360.0
    assert 0.0 <= pluto.longitude_deg < 360.0
    assert uranus.longitude_deg == aruna.longitude_deg

    # Jupiter system barycentre (NAIF 5) vs Jupiter physical disk centre (NAIF 599)
    jup_bary = adapter.calc_ut(jd, "jupiter", sidereal=True, physical_center=False)
    jup_phys = adapter.calc_ut(jd, "jupiter", sidereal=True, physical_center=True)
    jup_599 = adapter.calc_ut(jd, "599", sidereal=True)
    assert jup_phys.longitude_deg == jup_599.longitude_deg
    assert jup_phys.receipt_sha256 == jup_599.receipt_sha256
    assert jup_bary.receipt_sha256 != jup_phys.receipt_sha256
    diff_arcsec = abs(jup_phys.longitude_deg - jup_bary.longitude_deg) * 3600.0
    assert 0.0001 < diff_arcsec < 0.60  # Galilean moons recoil bounded to < 0.6 arcsec

    # Saturn system barycentre (NAIF 6) vs Saturn physical disk centre (NAIF 699)
    sat_bary = adapter.calc_ut(jd, "saturn", sidereal=True, physical_center=False)
    sat_phys = adapter.calc_ut(jd, "saturn_center", sidereal=True)
    sat_diff_arcsec = abs(sat_phys.longitude_deg - sat_bary.longitude_deg) * 3600.0
    assert 0.0001 < sat_diff_arcsec < 0.25


def test_krantisamya_mahapata_declination_equality_solver() -> None:
    """Verify exact Vyatipata and Vaidhriti Mahapata root finding."""
    # Over a 30-day lunar month, the Moon crosses both +dec_Sun (Vyatipata) and -dec_Sun (Vaidhriti)
    report = solve_krantisamya_mahapata_windows(2461300.0, 2461335.0, step_hours=6.0)
    assert report.event_count >= 2
    types = {e.mahapata_type for e in report.events}
    assert "Vyatipata" in types
    assert "Vaidhriti" in types
    for ev in report.events:
        if ev.mahapata_type == "Vyatipata":
            assert abs(ev.sun_declination_deg - ev.moon_declination_deg) < 1.0e-3
        else:
            assert abs(ev.sun_declination_deg + ev.moon_declination_deg) < 1.0e-3
        assert ev.duration_minutes > 10.0
    assert len(report.receipt_sha256) == 64

    with pytest.raises(ValueError, match="end_jd_ut must be greater"):
        solve_krantisamya_mahapata_windows(2461300.0, 2461290.0)


def test_inverse_sky_to_date_astronomical_time_machine_solver() -> None:
    """Verify the Inverse Sky-to-Date solver recovers a known epoch from planetary sign constraints."""
    adapter = EphemerisAdapter()
    target_jd = 2451545.0  # 2000-01-01 12:00 UTC
    constraints: dict[str, str] = {}
    for body in ("saturn", "jupiter", "mars", "sun", "moon"):
        pos = adapter.calc_ut(target_jd, body, sidereal=True, ayanamsa="lahiri")
        sign_idx = int(pos.longitude_deg // 30.0)
        from ephemeris_oss.jyotish.nakshatra import RASI_NAMES
        constraints[body] = RASI_NAMES[sign_idx]

    report = solve_chart_date_from_planetary_constraints(
        1999,
        2001,
        constraints,
        ayanamsa="lahiri",
    )
    assert report.match_count >= 1
    matched_any = any(
        m.window_start_jd_ut - 1.0 <= target_jd <= m.window_end_jd_ut + 1.0
        for m in report.matches
    )
    assert matched_any, f"Expected JD {target_jd} in matches {report.matches}"
    assert len(report.receipt_sha256) == 64

    with pytest.raises(ValueError, match="At least one planetary sign"):
        solve_chart_date_from_planetary_constraints(2000, 2001, {})


def test_triple_lock_life_event_convergence_solver() -> None:
    """Verify Triple-Lock Life-Event Convergence integrates Dasha + Double Transit + Ashtakavarga."""
    birth_jd = 2448000.0
    start_jd = 2461300.0
    end_jd = 2461360.0
    report = compute_triple_lock_life_event_convergence(
        birth_jd,
        28.6139,
        77.2090,
        start_jd,
        end_jd,
        domain="career",
        step_days=10.0,
    )
    assert report.domain == "career"
    assert report.primary_house == 10
    assert 0.0 <= report.bhrigu_bindu_longitude_deg < 360.0
    assert len(report.sampled_timeline) >= 6
    assert 0.0 <= report.peak_window.total_convergence_score_0_to_100 <= 100.0
    assert len(report.receipt_sha256) == 64

    with pytest.raises(ValueError, match="Unsupported domain"):
        compute_triple_lock_life_event_convergence(
            birth_jd, 28.6139, 77.2090, start_jd, end_jd, domain="unknown_domain"
        )


def test_mcp_and_rest_api_endpoints_for_next_level_solvers() -> None:
    """Verify MCP tools and OpenAPI 3.1 REST routes expose all 4 new SOTA solvers."""
    spec = build_openapi_spec()
    paths = spec["paths"]
    assert "/v1/yogatara" in paths
    assert "/v1/mahapata" in paths
    assert "/v1/inverse-date" in paths
    assert "/v1/triple-lock" in paths

    st1, p1 = dispatch_api_request("POST", "/v1/yogatara", {"jd_ut": 2461350.0, "orb_deg": 2.0})
    assert st1 == 200
    assert p1["yogatara_count"] == 30

    st2, p2 = dispatch_api_request(
        "POST",
        "/v1/mahapata",
        {"start_jd_ut": 2461300.0, "end_jd_ut": 2461335.0, "step_hours": 12.0},
    )
    assert st2 == 200
    assert p2["event_count"] >= 2

    st3, p3 = dispatch_api_request(
        "POST",
        "/v1/inverse-date",
        {
            "start_year": 2000,
            "end_year": 2000,
            "sign_constraints": {"saturn": "Aries", "jupiter": "Aries", "sun": "Sagittarius"},
        },
    )
    assert st3 == 200
    assert p3["match_count"] >= 1

    st4, p4 = dispatch_api_request(
        "POST",
        "/v1/triple-lock",
        {
            "birth_jd_ut": 2448000.0,
            "start_jd_ut": 2461300.0,
            "end_jd_ut": 2461330.0,
            "domain": "wealth",
            "step_days": 15.0,
        },
    )
    assert st4 == 200
    assert p4["domain"] == "wealth"
    assert "peak_window" in p4

    mcp_res = execute_mcp_tool("evaluate_yogatara_stellar_bheda", {"jd_ut": 2461350.0})
    assert mcp_res["yogatara_count"] == 30
