"""Verification suite for the 100-Chart Canonical Golden Reference Corpus (1900-2050).

Validates ``tests/golden_corpus/canonical_100_charts.json`` across:
- Canonical historical & observatory reference epochs (1900-2023)
- IERS leap-second boundaries & century/leap-day transitions (1972-2048)
- Planetary retrograde & direct station instants (Mercury, Venus, Mars, Jupiter, Saturn)
- Equatorial & International Date Line boundary observers
- High-latitude & polar circumpolar observers (Whole Sign vs Placidus graceful handling)
- Total/Annular Solar & Lunar Eclipse syzygies (1955-2034)
- Regional Indian Almanac festival, Sankranti, and Adhika Masa benchmarks (2026-2050)
- Complete 12-Lagna diurnal rotation sweep in Ujjain
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from ephemeris_oss.adapter import (
    AnalyticalEphemerisProvider,
    EphemerisAdapter,
    EphemerisError,
    FLG_SIDEREAL,
)
from ephemeris_oss.almanac.regional_panchang import compute_regional_panchang

CORPUS_PATH = Path(__file__).resolve().parent / "golden_corpus" / "canonical_100_charts.json"


@pytest.fixture(scope="module")
def golden_corpus() -> dict:
    assert CORPUS_PATH.is_file(), f"Missing golden corpus file: {CORPUS_PATH}"
    return json.loads(CORPUS_PATH.read_text(encoding="utf-8"))


def test_golden_corpus_structure_and_coverage(golden_corpus: dict) -> None:
    assert golden_corpus["schema"] == "ephemeris-oss.golden-corpus-100.v1"
    assert golden_corpus["count"] == 100
    charts = golden_corpus["charts"]
    assert len(charts) == 100

    chart_ids = [c["chart_id"] for c in charts]
    assert chart_ids == [f"GC-{i:03d}" for i in range(1, 101)]

    years = [c["year"] for c in charts]
    assert min(years) == 1900
    assert max(years) == 2050

    categories = {c["category"] for c in charts}
    expected_categories = {
        "canonical_historical",
        "leap_second_boundary",
        "retrograde_station",
        "equatorial_idl",
        "high_latitude_polar",
        "eclipse_syzygy",
        "regional_almanac",
        "lagna_rotation_sweep",
    }
    assert categories == expected_categories

    # All 12 Lagna signs (0..11) must be represented
    lagna_signs = {c["ascendant_rashi_index"] for c in charts}
    assert lagna_signs == set(range(12))

    # High-latitude polar charts must include circumpolar Placidus cases
    polar_charts = [c for c in charts if c["category"] == "high_latitude_polar"]
    assert len(polar_charts) == 12
    assert any(not c["placidus_supported"] for c in polar_charts)


def test_all_100_golden_charts_replay_and_invariants(golden_corpus: dict) -> None:
    charts = golden_corpus["charts"]
    with EphemerisAdapter(kernels="compact") as adapter:
        for entry in charts:
            cid = entry["chart_id"]
            jd = adapter.julday(
                entry["year"],
                entry["month"],
                entry["day"],
                entry["hour_utc"],
            )
            assert abs(jd - entry["jd_ut"]) < 1e-7, f"{cid}: JD mismatch"

            lat = entry["latitude_deg"]
            lon = entry["longitude_deg"]

            # Verify Placidus support matches recorded flag
            if entry["placidus_supported"]:
                p_houses = adapter.houses_ut(jd, lat, lon, system="placidus", ayanamsa="lahiri")
                assert len(p_houses.cusps_deg) == 12
            else:
                with pytest.raises(EphemerisError):
                    adapter.houses_ut(jd, lat, lon, system="placidus", ayanamsa="lahiri")

            bundle = adapter.compute_complete_kundali_bundle(jd, lat, lon, include_svg=False)
            assert bundle.receipt_sha256 == entry["bundle_receipt_sha256"], f"{cid}: bundle SHA-256 mismatch"
            assert abs(bundle.ayanamsa_deg - entry["ayanamsa_deg"]) < 1e-5, f"{cid}: ayanamsa mismatch"
            assert abs(bundle.houses.ascendant_deg - entry["ascendant_sidereal_deg"]) < 1e-5, f"{cid}: ascendant mismatch"

            va = bundle.vedic_analysis
            assert va.ashtakavarga.sarvashtakavarga_7_total == 337
            assert entry["sav_total_bindus"] == 337

            # Check Rahu-Ketu 180 degree opposition invariant
            rahu_lon = bundle.positions["rahu"].longitude_deg
            ketu_lon = bundle.positions["ketu"].longitude_deg
            diff_rk = abs((rahu_lon - ketu_lon) % 360.0 - 180.0)
            assert diff_rk < 1e-7, f"{cid}: Rahu-Ketu opposition violated"

            # Check all 9 grahas against golden corpus
            for g_key, g_cap in (
                ("sun", "Sun"),
                ("moon", "Moon"),
                ("mars", "Mars"),
                ("mercury", "Mercury"),
                ("jupiter", "Jupiter"),
                ("venus", "Venus"),
                ("saturn", "Saturn"),
                ("rahu", "Rahu"),
                ("ketu", "Ketu"),
            ):
                p_gold = entry["planets"][g_cap]
                pos = bundle.positions[g_key]
                v_map = va.planet_vargas[g_cap]
                nak = va.planet_nakshatras[g_cap]

                assert abs(pos.longitude_deg - p_gold["longitude_deg"]) < 1e-5, f"{cid} {g_cap}: lon mismatch"
                assert bool(pos.is_retrograde) == p_gold["is_retrograde"], f"{cid} {g_cap}: retro mismatch"
                assert int(v_map["D1"].sign_index) == p_gold["d1_rashi"], f"{cid} {g_cap}: D1 mismatch"
                assert int(v_map["D9"].sign_index) == p_gold["d9_navamsha"], f"{cid} {g_cap}: D9 mismatch"
                assert int(v_map["D10"].sign_index) == p_gold["d10_dashamsha"], f"{cid} {g_cap}: D10 mismatch"
                assert int(v_map["D60"].sign_index) == p_gold["d60_shashtiamsha"], f"{cid} {g_cap}: D60 mismatch"
                assert int(nak.number - 1) == p_gold["nakshatra_index"], f"{cid} {g_cap}: nakshatra mismatch"
                assert 1 <= int(nak.pada) <= 4
                assert int(nak.pada) == p_gold["pada"], f"{cid} {g_cap}: pada mismatch"


def test_golden_corpus_regional_panchang_and_analytical_cross_check(golden_corpus: dict) -> None:
    charts = golden_corpus["charts"]
    analytical = AnalyticalEphemerisProvider()
    # Cross-check a stratified sample across all categories (every 5th chart = 20 charts)
    with EphemerisAdapter(kernels="compact") as adapter:
        for entry in charts[::5]:
            cid = entry["chart_id"]
            jd = adapter.julday(
                entry["year"],
                entry["month"],
                entry["day"],
                entry["hour_utc"],
            )
            reg = compute_regional_panchang(
                jd,
                entry["latitude_deg"],
                entry["longitude_deg"],
                adapter=adapter,
                eclipse_window_days=5.0,
            )
            assert reg.receipt_sha256 == entry["regional_panchang_receipt_sha256"], f"{cid}: regional receipt mismatch"
            assert reg.amanta_masa if hasattr(reg, "amanta_masa") else reg.lunar_month.amanta_name == entry["amanta_masa"]
            assert reg.lunar_month.purnimanta_name == entry["purnimanta_masa"]
            assert reg.samvatsara_name == entry["samvatsara_name"]

            # Cross-verify compact DE440 Sun & Moon against analytical provider within expected analytical tolerance
            sun_ana, _ = analytical.calc_ut(jd, "Sun", flags=FLG_SIDEREAL)
            moon_ana, _ = analytical.calc_ut(jd, "Moon", flags=FLG_SIDEREAL)
            sun_diff = abs(((sun_ana[0] - entry["planets"]["Sun"]["longitude_deg"] + 180.0) % 360.0) - 180.0)
            moon_diff = abs(((moon_ana[0] - entry["planets"]["Moon"]["longitude_deg"] + 180.0) % 360.0) - 180.0)
            assert sun_diff < 0.05, f"{cid}: Sun compact vs analytical divergence {sun_diff}"
            assert moon_diff < 0.25, f"{cid}: Moon compact vs analytical divergence {moon_diff}"
