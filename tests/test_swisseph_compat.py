"""Contract tests for the bounded Swiss-shaped public facade."""

from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor
import json
import math
from pathlib import Path
import threading

import pytest

from ephemeris_oss import EphemerisAdapter, EphemerisError
from ephemeris_oss import swisseph_compat as swe


def test_calc_ut_receipt_preserves_adapter_result_and_declares_utc_contract() -> None:
    jd = swe.julday(2000, 1, 1, 12.0)
    flags = swe.FLG_SWIEPH | swe.FLG_SPEED | swe.FLG_SIDEREAL
    result = swe.calc_ut_with_receipt(jd, swe.MARS, flags)

    with EphemerisAdapter(kernels="compact") as adapter:
        direct = adapter.calc_ut(jd, swe.MARS, sidereal=True, ayanamsa="lahiri")

    assert result.values[:4] == pytest.approx(
        (direct.longitude_deg, direct.latitude_deg, direct.distance_au,
         direct.longitude_speed_deg_per_day), abs=1e-12
    )
    assert result.receipt_sha256 == direct.receipt_sha256
    assert len(result.receipt_sha256) == 64
    assert result.api == "ephemeris_oss.swisseph_compat.v1"
    assert result.input_time_scale == "UTC"
    assert "geocentric" in result.coordinate_convention
    assert result.flags == flags
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
        (lambda: swe.calc_ut_with_receipt(2451545.0, swe.SUN, input_time_scale="UT1"), "UTC"),
        (lambda: swe.set_sid_mode(999999), "sidereal mode"),
        (lambda: swe.houses_ex(2451545.0, 91.0, 0.0), "[Ll]atitude"),
    ],
)
def test_unsupported_compatibility_requests_fail_closed(call, match: str) -> None:
    with pytest.raises((EphemerisError, ValueError), match=match):
        call()
