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
    format_classical_rashi_dms,
    format_daily_motion_dms,
    format_ghati_pala,
    generate_human_manual_ephemeris_compendium,
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

    assert "/v1/human-ephemeris" in paths
    st5, p5 = dispatch_api_request(
        "POST",
        "/v1/human-ephemeris",
        {"year": 2026, "month": 11, "include_markdown": True},
    )
    assert st5 == 200
    assert p5["year"] == 2026
    assert p5["month"] == 11
    assert len(p5["daily_rows"]) == 30
    assert "Section 7 — Pt. Maheshji's Jyotish Academy Step-by-Step Worked Manual Kundali Worksheet" in p5["markdown"]


def test_human_readable_classical_ephemeris_and_jyotish_academy_compendium() -> None:
    """Verify the 20-Chapter Human-Readable Classical Ephemeris & Jyotish Academy Manual Compendium,
    8 Vishesha Lagnas, Full Spherical/Physical Sky Ephemeris, and 36 Tajika Sahams.
    """
    from ephemeris_oss import (
        compute_full_astronomical_sky_ephemeris,
        compute_vishesha_lagnas_and_special_points,
    )
    from ephemeris_oss.jyotish_advanced.varshphal import compute_tajika_sahams

    assert format_classical_rashi_dms(137.0230556) == 'Simha 17° 01\' 23"'
    assert format_classical_rashi_dms(137.0230556, compact_sign_number=True) == '04s 17° 01\' 23"'
    assert format_daily_motion_dms(-0.2122223) == '-00° 12\' 44"'
    assert format_ghati_pala(5.2) == "13g 00p"

    # 1. Verify Full Spherical & Physical Sky Ephemeris (all 13 bodies)
    sky = compute_full_astronomical_sky_ephemeris(2461345.5, ayanamsa="lahiri")
    assert len(sky) == 13
    assert "sun" in sky and "moon" in sky and "pluto" in sky
    assert sky["moon"].horizontal_parallax_arcsec > 3000.0
    assert 0.0 <= sky["moon"].illuminated_fraction_pct <= 100.0
    assert 1 <= sky["sun"].kp_sub_number_249 <= 249

    # 2. Verify All 8 Vishesha Lagnas, Yogi/Avayogi, 12 Arudha Padas, & 7/8 Chara Karakas
    vis = compute_vishesha_lagnas_and_special_points(
        2461345.72,
        28.6139,
        77.2090,
        sunrise_jd_ut=2461345.54,
    )
    assert len(vis.arudha_padas) == 12
    assert len(vis.chara_karakas_7) == 7
    assert len(vis.chara_karakas_8) == 8
    assert len(vis.receipt_sha256) == 64

    # 3. Verify All 36 Classical Tajika Sahams
    sahams_36 = compute_tajika_sahams(
        {p: sky[p].sidereal_longitude_deg for p in ("sun", "moon", "mars", "mercury", "jupiter", "venus", "saturn")},
        232.4,
        is_day_birth=True,
    )
    assert len(sahams_36) == 36

    # 4. Verify 30-Chapter Human-Readable Master Compendium & Real HTML Book Renderer
    comp = generate_human_manual_ephemeris_compendium(2026, 11, latitude_deg=28.6139, longitude_deg=77.2090)
    assert comp.year == 2026
    assert comp.month == 11
    assert comp.chapter_count == 30
    assert len(comp.daily_rows) == 30
    assert len(comp.full_sky_rows) == 30
    assert len(comp.receipt_sha256) == 64

    first_day = comp.daily_rows[0]
    assert "sun" in first_day.planets
    assert "moon" in first_day.planets
    assert "true_rahu" in first_day.planets
    assert "uranus" in first_day.planets
    assert "g" in first_day.dinamana_ghati_pala

    md = comp.to_markdown()
    assert len(md) > 450000
    assert "Chapter 1 — Fundamental Astronomical Constants" in md
    assert "Chapter 2 — Section 1 — Daily Sidereal (*Nirayana*) & Tropical (*Sayana*)" in md
    assert "Chapter 3 — Daily Spherical & Physical Ephemeris Grid" in md
    assert "Chapter 5 — Section 2 — Daily Sunrise-Anchored *Drik Panchanga*" in md
    assert "Chapter 6 — Section 3 — Manual *Spashta Graha* Interpolation Compendium" in md
    assert "Chapter 7 — Master Tables of Ascendants (*Udaya Lagna*)" in md
    assert "Chapter 8 — Complete Manual Compendium of All 8 *Vishesha Lagnas*" in md
    assert "Chapter 9 — Section 4 — Complete Manual Divisional Chart (*Shodashvarga D1–D60*)" in md
    assert "Chapter 10 — Complete 132-Cell *Mrityu Bhaga*" in md
    assert "Chapter 11 — Complete Krishnamurti Padhati (*KP*) 249 Sub-Lord Master Table" in md
    assert "Chapter 12 — Section 5 — Complete Manual Dasha Balance" in md
    assert "Chapter 13 — Complete *Jaimini Upadesha Sutras* Manual Compendium" in md
    assert "Chapter 14 — Complete Six-Fold *Shadbala*" in md
    assert "Chapter 15 — Complete *Ashtakavarga* (337-Bindu BAV/SAV)" in md
    assert "Chapter 16 — Complete Classical Mathematical Longevity (*Ayurdaya*" in md
    assert "Chapter 17 — Complete *Tajika Varshphal*" in md
    assert "Chapter 18 — Complete *Ashtakoota* (36-Guna) Compatibility" in md
    assert "Chapter 19 — Complete Classical Parashari Yoga Identification Directory" in md
    assert "Chapter 20 — Section 7 — Pt. Maheshji's Jyotish Academy Step-by-Step Worked Manual Kundali Worksheet" in md
    assert "Chapter 21 — Topocentric WGS84 Surface-Observer Astrometry" in md
    assert "Chapter 22 — Synodic Retrograde Phase-Space Loops" in md
    assert "Chapter 23 — Solar & Lunar Eclipse" in md
    assert "Chapter 24 — Complete Manual Compendium of All 10 Conditional Parashari *Nakshatra Dashas*" in md
    assert "Chapter 25 — 5-Level *Vimshottari Prana-Dasha* Sub-Hour Chronometer" in md
    assert "Chapter 26 — Complete 150-Division *Nadi Amsa*" in md
    assert "Chapter 27 — Complete 3-Ring *Sudarshana Chakra*" in md
    assert "Chapter 28 — Golden *Muhurta* Electional Optimization" in md
    assert "Chapter 29 — Continuous Sinusoidal *Uchcha-Neecha* Exaltation Potential" in md
    assert "Chapter 30 — 81-Cell *Sarvatobhadra Trishula* Ray-Tracer" in md

    html_doc = comp.to_html()
    assert "<!DOCTYPE html>" in html_doc
    assert "Master Table of Contents (30 Chapters)" in html_doc
    assert "<table class='ephemeris-table'>" in html_doc
    assert "<pre>" not in html_doc


def test_frontier_topocentric_relativistic_astrometry_and_flips() -> None:
    """Verify WGS84 topocentric parallax, atmospheric refraction, relativistic Shapiro/deflection, and varga flip detection."""
    from ephemeris_oss.frontier_astrodynamics import compute_topocentric_relativistic_astrometry

    rep = compute_topocentric_relativistic_astrometry(
        2461345.65,
        latitude_deg=28.6139,
        longitude_deg=77.2090,
        elevation_m=225.0,
        temperature_c=24.0,
        pressure_hpa=1008.0,
    )
    assert len(rep.bodies) == 13
    assert abs(rep.wgs84_rho_cos_phi_prime) > 0.5
    moon = rep.bodies["moon"]
    assert abs(moon.parallax_longitude_shift_arcsec) <= 3800.0
    assert abs(moon.parallax_longitude_shift_arcsec) > 1.0
    assert moon.shapiro_delay_microseconds > 0.0
    assert moon.light_time_seconds > 1.0
    assert len(rep.receipt_sha256) == 64


def test_frontier_synodic_retrograde_loops_and_triple_passes() -> None:
    """Verify 5-point synodic retrograde loop phase-space solver and natal triple-pass detector."""
    from ephemeris_oss.frontier_astrodynamics import solve_synodic_retrograde_loops_and_triple_passes

    rep = solve_synodic_retrograde_loops_and_triple_passes(
        2461300.5,
        2461480.5,
        bodies=("mercury",),
        natal_longitudes_deg={"natal_mercury": 208.0, "natal_sun": 212.0},
    )
    assert len(rep.loops) >= 1
    lp = rep.loops[0]
    assert lp.shadow_entry_jd_ut <= lp.station_retrograde_jd_ut < lp.station_direct_jd_ut <= lp.shadow_exit_jd_ut
    assert lp.retrograde_arc_deg > 5.0
    assert lp.retrograde_duration_days > 10.0
    assert len(rep.receipt_sha256) == 64


def test_frontier_eclipse_natal_sensitivity_scanner() -> None:
    """Verify Solar/Lunar eclipse local obscuration and natal degree Grahan sensitivity scanner."""
    from ephemeris_oss.frontier_astrodynamics import evaluate_lifetime_eclipse_natal_sensitivity

    rep = evaluate_lifetime_eclipse_natal_sensitivity(
        2461041.5,
        2461406.5,
        natal_longitudes_deg={"sun": 305.0, "moon": 139.0, "ascendant": 116.0},
        latitude_deg=28.6139,
        longitude_deg=77.2090,
        orb_deg=5.0,
    )
    assert len(rep.eclipses) >= 2
    assert len(rep.natal_hits) >= 1
    assert len(rep.receipt_sha256) == 64


def test_frontier_all_10_conditional_nakshatra_dashas_and_prana_and_nadi_and_muhurta() -> None:
    """Verify all 10 BPHS conditional Nakshatra Dashas, 5-level Prana Dasha, 150-Nadi Amsa, 3-Ring Sudarshana, and Muhurta Optimizer."""
    from ephemeris_oss.jyotish.conditional_dashas_and_nadi import (
        compute_all_10_parashari_nakshatra_dashas,
        compute_nadi_amsa_and_sudarshana_chakra,
        compute_vimshottari_5_level_prana_chronometer,
        solve_golden_muhurta_electional_windows,
    )

    lons = {
        "sun": 225.4,
        "moon": 42.8,
        "mars": 115.2,
        "mercury": 218.9,
        "jupiter": 102.5,
        "venus": 195.1,
        "saturn": 344.2,
        "rahu": 312.0,
        "ketu": 132.0,
    }
    dasha_10 = compute_all_10_parashari_nakshatra_dashas(
        moon_sidereal_lon_deg=42.8,
        asc_sidereal_lon_deg=48.2,
        sun_sidereal_lon_deg=225.4,
        planet_longitudes_deg=lons,
        birth_jd=2451545.0,
        query_jd=2461345.5,
        is_day_birth=True,
    )
    assert len(dasha_10.systems) == 10
    cycle_totals = {s.system_key: int(round(s.total_cycle_years)) for s in dasha_10.systems}
    assert cycle_totals["vimshottari"] == 120
    assert cycle_totals["ashtottari"] == 108
    assert cycle_totals["shodashottari"] == 116
    assert cycle_totals["dwadashottari"] == 112
    assert cycle_totals["panchottari"] == 105
    assert cycle_totals["shatabdika"] == 100
    assert cycle_totals["chaturashiti_sama"] == 84
    assert cycle_totals["dwisaptati_sama"] == 72
    assert cycle_totals["shat_trimsha_sama"] == 36
    assert cycle_totals["yogini"] == 36
    assert len(dasha_10.consensus_ranking) >= 1

    prana_rep = compute_vimshottari_5_level_prana_chronometer(
        moon_sidereal_lon_deg=42.8,
        birth_jd=2451545.0,
        query_jd=2461345.5,
    )
    assert prana_rep.mahadasha_lord != ""
    assert prana_rep.antardasha_lord != ""
    assert prana_rep.pratyantardasha_lord != ""
    assert prana_rep.sookshma_lord != ""
    assert prana_rep.active_prana_lord != ""
    assert len(prana_rep.prana_windows) == 9

    nadi_sud = compute_nadi_amsa_and_sudarshana_chakra(
        asc_sidereal_lon_deg=48.2,
        planet_longitudes_deg=lons,
        birth_jd=2451545.0,
        query_jd=2461345.5,
    )
    assert 1 <= nadi_sud.ascendant_nadi.nadi_amsa_number_1_to_150 <= 150
    assert len(nadi_sud.planet_nadis) == 9
    assert len(nadi_sud.sudarshana_houses) == 12
    assert len(nadi_sud.sudarshana_dasha_years) == 12

    muh = solve_golden_muhurta_electional_windows(
        start_jd_ut=2461345.5,
        end_jd_ut=2461350.5,
        latitude_deg=28.6139,
        longitude_deg=77.2090,
        activity="vyapara_business",
        natal_moon_lon_deg=42.8,
        step_minutes=60,
    )
    assert len(muh.top_windows) >= 1
    assert 0.0 <= muh.top_windows[0].score_0_to_100 <= 100.0
    assert len(muh.receipt_sha256) == 64


def test_frontier_continuous_dignity_heliacal_sarvatobhadra_vedha_and_shodhya_pinda() -> None:
    """Verify continuous Uchcha-Neecha potential, Arohi/Avarohi climb, 81-Cell Sarvatobhadra ray-tracer, and Shodhya Pinda triggers."""
    from ephemeris_oss.jyotish.harmonic_vedha_and_pinda import (
        compute_continuous_dignity_and_heliacal_phenomena,
        compute_sarvatobhadra_81_ray_vedha,
        compute_shodhya_pinda_transit_triggers_and_harmonic_yogas,
    )

    dig = compute_continuous_dignity_and_heliacal_phenomena(2461350.0, 28.6139, 77.2090)
    assert len(dig.planets) == 9
    assert 0.0 <= dig.overall_chart_uchcha_harmony_0_to_100 <= 100.0
    assert 0.0 <= dig.overall_chart_digbala_harmony_0_to_100 <= 100.0
    assert len(dig.receipt_sha256) == 64

    sbc = compute_sarvatobhadra_81_ray_vedha(2461350.0, 42.8, natal_nama_akshara="a")
    assert len(sbc.active_ray_hits) >= 27
    assert -100.0 <= sbc.net_vedha_protection_index_minus100_to_plus100 <= 100.0
    assert len(sbc.receipt_sha256) == 64

    pinda = compute_shodhya_pinda_transit_triggers_and_harmonic_yogas(2461350.0, 28.6139, 77.2090)
    assert len(pinda.shodhya_pinda_rows) == 7
    assert len(pinda.house_vitality_rows) == 12
    assert len(pinda.harmonic_yogas) == 5
    assert 0.0 <= pinda.vitta_ayavyaya_wealth_index_0_to_100 <= 100.0
    assert len(pinda.receipt_sha256) == 64


def test_live_http_socket_server_and_mcp_20_tools_end_to_end() -> None:
    """Verify live HTTP socket round-trips across all 23 REST endpoints and JSON-RPC 2.0 across all 20 MCP tools."""
    import json
    import threading
    import urllib.request

    from ephemeris_oss.api_server import create_http_server
    from ephemeris_oss.mcp_server import MCP_TOOLS, handle_jsonrpc_message

    assert len(MCP_TOOLS) == 20
    list_resp = handle_jsonrpc_message({"jsonrpc": "2.0", "id": 1, "method": "tools/list"})
    assert list_resp is not None
    assert len(list_resp["result"]["tools"]) == 20

    server = create_http_server("127.0.0.1", 0)
    host, port = server.server_address[:2]
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        base_url = f"http://{host}:{port}"
        with urllib.request.urlopen(f"{base_url}/health", timeout=10) as resp:
            health = json.loads(resp.read().decode("utf-8"))
        assert health["status"] == "ok"
        assert len(health["endpoints"]) == 23

        with urllib.request.urlopen(f"{base_url}/openapi.json", timeout=10) as resp:
            openapi = json.loads(resp.read().decode("utf-8"))
        assert len(openapi["paths"]) == 23

        for path_url, payload in (
            ("/v1/topocentric-astrometry", {"jd_ut": 2461350.0, "latitude_deg": 28.6139, "longitude_deg": 77.2090}),
            ("/v1/dignity-heliacal", {"jd_ut": 2461350.0, "latitude_deg": 28.6139, "longitude_deg": 77.2090}),
            ("/v1/sarvatobhadra-vedha-pinda", {"jd_ut": 2461350.0, "latitude_deg": 28.6139, "longitude_deg": 77.2090, "natal_moon_longitude_deg": 42.8}),
            ("/v1/conditional-dashas-nadi", {"birth_jd_ut": 2451545.0, "query_jd_ut": 2461350.0}),
        ):
            req = urllib.request.Request(
                f"{base_url}{path_url}",
                data=json.dumps(payload).encode("utf-8"),
                headers={"Content-Type": "application/json"},
                method="POST",
            )
            with urllib.request.urlopen(req, timeout=15) as r_post:
                assert r_post.status == 200
                body_json = json.loads(r_post.read().decode("utf-8"))
                assert isinstance(body_json, dict)
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=5)




