"""Contract tests for the bounded Swiss-shaped public facade."""

from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor
import json
import math
import os
from pathlib import Path
import threading

import erfa
import pytest

from ephemeris_oss import EphemerisAdapter, EphemerisError
from ephemeris_oss import swisseph_compat as swe
from ephemeris_oss.engine.contracts import AstronomyDataUnavailable


def _signed_angle_delta(later: float, earlier: float) -> float:
    return (later - earlier + 180.0) % 360.0 - 180.0


def test_calc_ut_receipt_preserves_adapter_result_and_declares_utc_contract() -> None:
    jd = swe.julday(2000, 1, 1, 12.0)
    flags = swe.FLG_SWIEPH | swe.FLG_SPEED | swe.FLG_SIDEREAL
    result = swe.calc_ut_with_receipt(jd, swe.MARS, flags)

    with EphemerisAdapter(kernels="compact") as adapter:
        direct = adapter.calc_tt(
            result.jd_tt, swe.MARS, jd_tdb=result.jd_tdb,
            sidereal=True, ayanamsa="lahiri",
        )

    assert result.values[:4] == pytest.approx(
        (direct.longitude_deg, direct.latitude_deg, direct.distance_au,
         direct.longitude_speed_deg_per_day), abs=1e-12
    )
    assert result.receipt_sha256 != direct.receipt_sha256
    assert len(result.receipt_sha256) == 64
    assert result.api == "ephemeris_oss.compat.v2"
    assert result.input_time_scale == "UT1"
    assert result.flags == (flags & ~swe.FLG_SWIEPH) | swe.FLG_JPLEPH
    assert math.isclose(jd, 2451545.0, abs_tol=1e-9)


def test_independent_j2000_sun_almanac_anchor_and_units() -> None:
    # Frozen NASA/JPL Horizons geometric ICRF state is independent of the
    # adapter. Rotate it to mean J2000 ecliptic coordinates, then use a broad
    # tolerance for the facade's documented apparent/ecliptic-of-date output.
    fixture = json.loads(
        (Path(__file__).parent / "fixtures" / "swisseph_compat_j2000_oracle.json")
        .read_text(encoding="utf-8")
    )
    x, y, z = fixture["position_km"]
    obliquity = math.radians(fixture["mean_obliquity_deg"])
    ecliptic_y = y * math.cos(obliquity) + z * math.sin(obliquity)
    oracle_lon = math.degrees(math.atan2(ecliptic_y, x)) % 360.0
    oracle_distance_au = math.sqrt(x * x + y * y + z * z) / fixture["au_km"]
    result = swe.calc_ut_with_receipt(2451545.0, swe.SUN, swe.FLG_SWIEPH | swe.FLG_SPEED)
    lon, lat, distance_au, speed_deg_per_day, _, _ = result.values
    assert lon == pytest.approx(oracle_lon, abs=0.08)
    assert lat == pytest.approx(0.0, abs=0.01)
    assert distance_au == pytest.approx(oracle_distance_au, abs=0.001)
    assert speed_deg_per_day == pytest.approx(1.019, abs=0.02)


def test_no_speed_flag_returns_zero_speed_slots() -> None:
    values, flags = swe.calc_ut(2451545.0, swe.MARS, swe.FLG_SWIEPH)
    assert values[3:] == (0.0, 0.0, 0.0)
    assert flags & swe.FLG_SPEED == 0


def test_utc_uses_versioned_tai_tt_and_rejects_inconsistent_delta_t() -> None:
    jd_utc = swe.julday(2024, 4, 8, 18.0)
    dut1 = 0.2
    derived = swe.calc_ut_with_receipt(
        jd_utc, swe.MARS, 0, input_time_scale="UTC", dut1_seconds=dut1,
    )
    explicit = swe.calc_ut_with_receipt(
        jd_utc, swe.MARS, 0, input_time_scale="UTC", dut1_seconds=dut1,
        delta_t_seconds=69.184 - dut1,
    )

    assert (derived.jd_tt - jd_utc) * 86400.0 == pytest.approx(69.184, abs=5e-5)
    assert explicit == derived
    with pytest.raises(EphemerisError, match="contradicts"):
        swe.calc_ut_with_receipt(
            jd_utc, swe.MARS, 0, input_time_scale="UTC", dut1_seconds=dut1,
            delta_t_seconds=69.184,
        )
    with pytest.raises(EphemerisError, match="outside.*1960.*2026"):
        swe.calc_ut_with_receipt(
            swe.julday(1959, 12, 31), swe.MARS, 0,
            input_time_scale="UTC", dut1_seconds=0.0,
        )


def test_true_sidereal_ayanamsa_cancels_tropical_nutation() -> None:
    jd_tt = swe.julday(2024, 4, 8, 18.0)
    mean_tropical = swe.calc(jd_tt, swe.MARS, swe.FLG_NONUT)[0][0]
    true_tropical = swe.calc(jd_tt, swe.MARS, 0)[0][0]
    mean_sidereal = swe.calc(
        jd_tt, swe.MARS, swe.FLG_SIDEREAL | swe.FLG_NONUT,
    )[0][0]
    true_sidereal = swe.calc(jd_tt, swe.MARS, swe.FLG_SIDEREAL)[0][0]
    dpsi_deg = math.degrees(float(erfa.nut06a(2451545.0, jd_tt - 2451545.0)[0]))

    assert _signed_angle_delta(true_tropical, mean_tropical) == pytest.approx(
        dpsi_deg, abs=1e-12,
    )
    assert _signed_angle_delta(true_sidereal, mean_sidereal) == pytest.approx(
        0.0, abs=1e-12,
    )


def test_returned_source_flag_reports_jpl_and_receipt_keeps_request() -> None:
    jd_tt = swe.julday(2024, 4, 8, 18.0)
    implicit = swe.calc_with_receipt(jd_tt, swe.MARS, 0)
    compatibility_request = swe.calc_with_receipt(jd_tt, swe.MARS, swe.FLG_SWIEPH)

    assert implicit.values == compatibility_request.values
    assert implicit.flags == compatibility_request.flags == swe.FLG_JPLEPH
    assert implicit.flags & swe.FLG_SWIEPH == 0
    assert implicit.receipt_sha256 != compatibility_request.receipt_sha256


@pytest.mark.parametrize("mismatch_seconds", [10.0, 86400.0])
def test_explicit_tdb_must_identify_the_same_tt_epoch_at_every_boundary(mismatch_seconds) -> None:
    jd_tt = swe.julday(2024, 4, 8, 18.0)
    mismatched_tdb = jd_tt + mismatch_seconds / 86400.0
    with EphemerisAdapter(kernels="compact") as adapter, swe.adapter_context(adapter):
        with pytest.raises(EphemerisError, match="same epoch"):
            adapter.calc_tt(
                jd_tt, swe.MARS, jd_tdb=mismatched_tdb,
                include_derivatives=False,
            )
        with pytest.raises(AstronomyDataUnavailable, match="same epoch"):
            adapter.engine._provider.planet_positions_tt(
                jd_tt=jd_tt, bodies=("mars",), jd_tdb=mismatched_tdb,
            )
        with pytest.raises(EphemerisError, match="same epoch"):
            swe.calc(jd_tt, swe.MARS, 0, jd_tdb=mismatched_tdb)

        supplied_tdb = jd_tt + 0.001 / 86400.0
        adapter_result = adapter.calc_tt(
            jd_tt, swe.MARS, jd_tdb=supplied_tdb,
            include_derivatives=False,
        )
        provider_result = adapter.engine._provider.planet_positions_tt(
            jd_tt=jd_tt, bodies=("mars",), jd_tdb=supplied_tdb,
        )
        facade_values, _ = swe.calc(jd_tt, swe.MARS, 0, jd_tdb=supplied_tdb)

    assert math.isfinite(adapter_result.longitude_deg)
    assert math.isfinite(provider_result["positions"]["Mars"]["longitude_deg"])
    assert all(math.isfinite(value) for value in facade_values)


def test_sidereal_receipt_labels_mean_ecliptic_reduction_for_both_flags() -> None:
    jd_tt = swe.julday(2024, 4, 8, 18.0)
    true_requested = swe.calc_with_receipt(
        jd_tt, swe.MARS, swe.FLG_SIDEREAL,
    )
    mean_requested = swe.calc_with_receipt(
        jd_tt, swe.MARS, swe.FLG_SIDEREAL | swe.FLG_NONUT,
    )

    assert true_requested.coordinate_convention == "mean ecliptic/sidereal reduction"
    assert mean_requested.coordinate_convention == "mean ecliptic/sidereal reduction"


def test_engine_far_tt_fails_closed_without_explicit_mean_policy() -> None:
    with EphemerisAdapter(kernels="compact") as adapter:
        with pytest.raises(EphemerisError, match="jd_tdb"):
            adapter.engine.positions_tt(
                -1_000_000.0, ("sun",), mean_equinox=True,
            )
        with pytest.raises(EphemerisError, match="mean_equinox"):
            adapter.engine.positions_tt(
                -1_000_000.0, ("sun",), jd_tdb=-1_000_000.0,
            )


@pytest.mark.parametrize(
    ("variable", "identifier", "jd_tt"),
    [
        ("EPHEMERIS_OSS_DE441_PART1_KERNEL", "DE441-PART1", -1_000_000.0),
        ("EPHEMERIS_OSS_DE441_PART2_KERNEL", "DE441-PART2", 7_500_000.0),
    ],
)
def test_real_de441_far_date_explicit_tt_mean_position(
    variable: str, identifier: str, jd_tt: float,
) -> None:
    configured = os.getenv(variable)
    if configured is None:
        pytest.skip(f"real {identifier} kernel not supplied")
    kernel = Path(configured)
    with EphemerisAdapter(
        kernels={identifier: kernel}, eop=None,
    ) as adapter, swe.adapter_context(adapter):
        engine_result = adapter.engine.positions_tt(
            jd_tt, ("sun",), jd_tdb=jd_tt, mean_equinox=True,
        )
        result = swe.calc_with_receipt(
            jd_tt, swe.SUN, swe.FLG_NONUT, jd_tdb=jd_tt,
        )

    assert engine_result.receipt["tdb_policy"] == "caller-supplied"
    assert engine_result.receipt["mean_equinox"] is True
    assert engine_result.receipt["frame"] == "apparent-geocentric-mean-ecliptic-of-date"
    assert all(math.isfinite(value) for value in engine_result.value["sun"].values())
    assert result.flags == swe.FLG_JPLEPH | swe.FLG_NONUT
    assert result.coordinate_convention == "mean ecliptic/equinox"
    assert result.jd_tt == result.jd_tdb == jd_tt
    assert all(math.isfinite(value) for value in result.values)
    assert 0.9 < result.values[2] < 1.1


def test_sidereal_mode_is_isolated_between_concurrent_callers() -> None:
    jd = swe.julday(2024, 4, 8, 18.0)
    lahiri_ready = threading.Event()
    raman_ready = threading.Event()

    def lahiri_call() -> float:
        swe.set_sid_mode(swe.SIDM_LAHIRI)
        lahiri_ready.set()
        assert raman_ready.wait(5)
        return swe.calc_ut(jd, swe.MOON, swe.FLG_SWIEPH | swe.FLG_SIDEREAL)[0][0]

    def raman_call() -> float:
        assert lahiri_ready.wait(5)
        swe.set_sid_mode(swe.SIDM_RAMAN)
        raman_ready.set()
        return swe.calc_ut(jd, swe.MOON, swe.FLG_SWIEPH | swe.FLG_SIDEREAL)[0][0]

    with ThreadPoolExecutor(max_workers=2) as pool:
        lahiri_value = pool.submit(lahiri_call)
        raman_value = pool.submit(raman_call)
        lahiri_lon, raman_lon = lahiri_value.result(), raman_value.result()

    explicit_lahiri = swe.calc_ut_with_receipt(
        jd, swe.MOON, swe.FLG_SWIEPH | swe.FLG_SIDEREAL,
        sidereal_mode=swe.SIDM_LAHIRI,
    ).values[0]
    explicit_raman = swe.calc_ut_with_receipt(
        jd, swe.MOON, swe.FLG_SWIEPH | swe.FLG_SIDEREAL,
        sidereal_mode=swe.SIDM_RAMAN,
    ).values[0]
    assert lahiri_lon == pytest.approx(explicit_lahiri, abs=1e-12)
    assert raman_lon == pytest.approx(explicit_raman, abs=1e-12)
    assert abs(lahiri_lon - raman_lon) > 0.1


def test_sidereal_house_contract_keeps_lahiri_scope() -> None:
    jd = swe.julday(2024, 4, 8, 18.0)
    swe.set_sid_mode(swe.SIDM_LAHIRI)
    cusps, angles = swe.houses_ex(jd, 23.0225, 72.5714, b"W", swe.FLG_SIDEREAL)
    assert len(cusps) == 12
    assert len(angles) == 10


@pytest.mark.parametrize(
    ("call", "match"),
    [
        (lambda: swe.calc_ut(2451545.0, 999999), "body"),
        (lambda: swe.calc_ut(2451545.0, swe.SUN, swe.FLG_EQUATORIAL), "flag"),
        (lambda: swe.calc_ut_with_receipt(2451545.0, swe.SUN, input_time_scale="TAI"), "UT1"),
        (lambda: swe.calc_ut_with_receipt(2451545.0, swe.SUN, input_time_scale="UTC"), "dut1"),
        (lambda: swe.calc_ut_with_receipt(2451545.0, swe.SUN, delta_t_seconds=math.inf), "finite"),
        (lambda: swe.set_sid_mode(999999), "sidereal mode"),
        (lambda: swe.houses_ex(2451545.0, 91.0, 0.0), "[Ll]atitude"),
    ],
)
def test_unsupported_compatibility_requests_fail_closed(call, match: str) -> None:
    with pytest.raises((EphemerisError, ValueError), match=match):
        call()
