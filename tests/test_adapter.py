"""Comprehensive tests for EphemerisAdapter, QA-SEC probes, and Almanac modules."""

from __future__ import annotations

from datetime import datetime, timezone
import math
import pytest

from ephemeris_oss import (
    AnalyticalEphemerisProvider,
    CompleteKundaliBundle,
    EphemerisAdapter,
    EphemerisError,
    HouseSystemResult,
    PlanetCoordinateResult,
    normalize_ephemeris_source,
)
from ephemeris_oss.adapter import (
    CALC_RISE,
    CALC_SET,
    ECL_ANNULAR,
    ECL_PARTIAL,
    ECL_PENUMBRAL,
    ECL_TOTAL,
    FLG_SIDEREAL,
    SUN,
    VEDIC_NINE_GRAHAS,
)
from ephemeris_oss.almanac import (
    HELIACAL_BODY_CATALOG,
    evaluate_crescent_visibility,
    evaluate_heliacal_visibility,
    generate_monthly_panchang,
    resolve_heliacal_body,
)


# ---------------------------------------------------------------------------
# 1. QA-SEC Probe Suite (Direct Regression Tests for Astro-AI-Studio#442)
# ---------------------------------------------------------------------------


def test_qa_sec_default_source_remains_configured_primary() -> None:
    assert normalize_ephemeris_source(env={}) == "primary"
    assert normalize_ephemeris_source("PRIMARY", env={}) == "primary"
    assert normalize_ephemeris_source("alternative", env={}) == "alternative"


def test_qa_sec_invalid_supplied_manifest_fails_closed(tmp_path) -> None:
    bad_manifest = tmp_path / "missing-manifest.json"
    bad_kernel = tmp_path / "missing-de440.bsp"
    with pytest.raises(ValueError):
        normalize_ephemeris_source(
            env={
                "EPHEMERIS_RELEASE_MANIFEST": str(bad_manifest),
                "EPHEMERIS_DE440_KERNEL": str(bad_kernel),
            }
        )
    with pytest.raises(ValueError):
        normalize_ephemeris_source(
            env={
                "EPHEMERIS_SOURCE": "JPL",
                "EPHEMERIS_RELEASE_MANIFEST": str(bad_manifest),
            }
        )


def test_qa_sec_sunrise_depends_on_latitude() -> None:
    alt = AnalyticalEphemerisProvider()
    jd = 2461041.0  # 2026-01-01 12:00 UT
    _, (equator_rise,) = alt.rise_trans(jd, SUN, CALC_RISE, (0.0, 0.0, 0.0))
    _, (north45_rise,) = alt.rise_trans(jd, SUN, CALC_RISE, (0.0, 45.0, 0.0))
    assert abs(equator_rise - north45_rise) > 0.03
    # Match USNO spherical horizon reference values (~2461041.7499 and ~2461041.8183) within 3 minutes
    assert abs(equator_rise - 2461041.7499) < 0.003
    assert abs(north45_rise - 2461041.8183) < 0.003


def test_qa_sec_circumpolar_sunrise_raises() -> None:
    alt = AnalyticalEphemerisProvider()
    jd = 2461041.0  # Northern winter solstice season
    with pytest.raises(ValueError):
        alt.rise_trans(jd, SUN, CALC_RISE, (0.0, 80.0, 0.0))


def test_qa_sec_eclipses_not_fabricated_offset_and_fail_closed_by_default() -> None:
    alt = AnalyticalEphemerisProvider()
    jd = 2461041.0
    with pytest.raises((ValueError, NotImplementedError)):
        alt.sol_eclipse_when_glob(jd)
    with pytest.raises((ValueError, NotImplementedError)):
        alt.lun_eclipse_when(jd)

    # When Besselian eclipses are enabled, returns real syzygy solutions, never jd + 177.0
    alt_bessel = AnalyticalEphemerisProvider(enable_besselian_eclipses=True)
    sol_flag, sol_contacts = alt_bessel.sol_eclipse_when_glob(jd)
    lun_flag, lun_contacts = alt_bessel.lun_eclipse_when(jd)
    assert sol_flag in (ECL_TOTAL, ECL_ANNULAR, ECL_PARTIAL)
    assert lun_flag in (ECL_TOTAL, ECL_PARTIAL, ECL_PENUMBRAL)
    assert not math.isclose(sol_contacts[0] - jd, 177.0, abs_tol=1.0)
    assert not math.isclose(lun_contacts[0] - jd, 177.0, abs_tol=1.0)


def test_qa_sec_placidus_houses_differ_from_equal_and_unsupported_raises() -> None:
    alt = AnalyticalEphemerisProvider()
    jd = 2461041.0
    placidus_cusps, _ = alt.houses_ex(jd, 45.0, 0.0, b"P")
    equal_cusps, _ = alt.houses_ex(jd, 45.0, 0.0, b"E")
    assert placidus_cusps != equal_cusps
    for unsupported_hsys in (b"K", b"S", b"C", b"R", "X"):
        with pytest.raises(ValueError):
            alt.houses_ex(jd, 45.0, 0.0, unsupported_hsys)


def test_qa_sec_unknown_body_ids_raise_value_error() -> None:
    alt = AnalyticalEphemerisProvider()
    jd = 2461041.0
    with pytest.raises(ValueError):
        alt.calc_ut(jd, 999999)
    with pytest.raises(ValueError):
        alt.calc_ut(jd, "QA_SEC_UNKNOWN_BODY")
    with pytest.raises(ValueError):
        alt.calc_ut(jd, 15)  # Chiron unsupported on analytical fallback


# ---------------------------------------------------------------------------
# 2. EphemerisAdapter & CompleteKundaliBundle Tests
# ---------------------------------------------------------------------------


def test_ephemeris_adapter_julday_revjul_and_calc_ut() -> None:
    with EphemerisAdapter(kernels="compact") as adapter:
        jd = adapter.julday(2000, 1, 1, 12.0)
        assert math.isclose(jd, 2451545.0, abs_tol=1e-9)
        assert adapter.revjul(jd) == (2000, 1, 1, 12.0)

        ayan = adapter.get_ayanamsa_ut(jd, mode="lahiri")
        assert 23.8 < ayan < 23.9

        for code in range(12):
            pos = adapter.calc_ut(jd, code, sidereal=True)
            assert isinstance(pos, PlanetCoordinateResult)
            lon, lat, dist, spd, retro, sha = pos
            assert 0.0 <= lon < 360.0
            assert -90.0 <= lat <= 90.0
            assert dist > 0.0
            assert isinstance(retro, bool)
            assert len(sha) == 64

        rahu = adapter.calc_ut(jd, "rahu", sidereal=True)
        ketu = adapter.calc_ut(jd, "ketu", sidereal=True)
        assert math.isclose((rahu.longitude_deg + 180.0) % 360.0, ketu.longitude_deg, abs_tol=1e-9)

        with pytest.raises(ValueError):
            adapter.calc_ut(jd, 999999)
        with pytest.raises(ValueError):
            adapter.calc_ut(jd, "QA_SEC_UNKNOWN_BODY")


def test_ephemeris_adapter_houses_rise_trans_and_eclipses() -> None:
    with EphemerisAdapter(kernels="compact") as adapter:
        jd = 2461041.0
        p_cusps, p_ascmc = adapter.houses_ex(jd, 45.0, 0.0, b"P", flags=FLG_SIDEREAL)
        e_cusps, e_ascmc = adapter.houses_ex(jd, 45.0, 0.0, b"E", flags=FLG_SIDEREAL)
        assert p_cusps != e_cusps
        assert len(p_cusps) == 12
        assert len(p_ascmc) == 10
        with pytest.raises(ValueError):
            adapter.houses_ex(jd, 45.0, 0.0, b"K")

        _, (eq_rise,) = adapter.rise_trans(jd, "sun", CALC_RISE, (0.0, 0.0, 0.0))
        _, (n45_rise,) = adapter.rise_trans(jd, "sun", CALC_RISE, (0.0, 45.0, 0.0))
        assert abs(eq_rise - n45_rise) > 0.03

        sol_flag, sol_contacts = adapter.sol_eclipse_when_glob(jd)
        lun_flag, lun_contacts = adapter.lun_eclipse_when(jd)
        assert sol_contacts[0] > jd
        assert lun_contacts[0] > jd
        assert not math.isclose(sol_contacts[0] - jd, 177.0, abs_tol=1.0)


def test_complete_kundali_bundle_end_to_end() -> None:
    with EphemerisAdapter(kernels="compact") as adapter:
        dt = datetime(1990, 5, 15, 6, 30, tzinfo=timezone.utc)
        bundle = adapter.compute_complete_kundali_bundle(
            dt,
            latitude_deg=28.6139,
            longitude_deg=77.2090,
            ayanamsa="lahiri",
            include_svg=True,
        )
        assert isinstance(bundle, CompleteKundaliBundle)
        assert set(bundle.positions.keys()) == set(VEDIC_NINE_GRAHAS)
        assert isinstance(bundle.houses, HouseSystemResult)
        assert bundle.ai_fact_sheet.byte_length <= 3000
        assert bundle.north_indian_svg is not None
        assert bundle.south_indian_svg is not None
        assert "<svg" in bundle.north_indian_svg.svg
        assert len(bundle.bundle_receipt_sha256) == 64


# ---------------------------------------------------------------------------
# 3. Almanac Visibility & Monthly Drik Panchang Calendar Tests
# ---------------------------------------------------------------------------


def test_crescent_and_heliacal_visibility() -> None:
    crescent = evaluate_crescent_visibility(arcl_deg=15.0, arcv_deg=12.5, daz_deg=8.0)
    assert crescent.yallop_zone in ("A", "B")
    assert crescent.is_naked_eye_visible is True
    assert len(crescent.receipt_sha256) == 64

    danjon = evaluate_crescent_visibility(arcl_deg=5.0, arcv_deg=4.0, daz_deg=2.0)
    assert danjon.below_danjon_limit is True
    assert danjon.yallop_zone == "F"
    assert danjon.is_naked_eye_visible is False

    for key in HELIACAL_BODY_CATALOG:
        spec = resolve_heliacal_body(key)
        rep = evaluate_heliacal_visibility(key, sun_alt_deg=-10.0, body_alt_deg=6.0, daz_deg=10.0)
        assert rep.body == spec.key
        assert rep.is_visible is True
        assert rep.tara_state == "Udaya"
        assert len(rep.receipt_sha256) == 64


def test_monthly_panchang_calendar_generation() -> None:
    sheet = generate_monthly_panchang(
        2026,
        1,
        latitude_deg=28.6139,
        longitude_deg=77.2090,
        tz_offset_hours=5.5,
    )
    assert sheet.year == 2026
    assert sheet.month == 1
    assert len(sheet.days) == 31
    assert len(sheet.receipt_sha256) == 64
    assert any(d.is_ekadashi for d in sheet.days)
    assert any(d.is_purnima or d.is_amavasya for d in sheet.days)
    assert any(d.sankranti_rashi_name is not None for d in sheet.days)
