"""Behavioral regressions for the bounded Swiss-shaped v2 facade."""

from __future__ import annotations

import math

import pytest
from ephemeris_oss import EphemerisError
from ephemeris_oss import swisseph_compat as swe

def _signed_angle_delta(later: float, earlier: float) -> float:
    return (later - earlier + 180.0) % 360.0 - 180.0


@pytest.mark.parametrize("calendar", [0, 1])
@pytest.mark.parametrize("date", [(-13200, 1, 1, 0.0), (0, 2, 29, 12.5),
                                  (1582, 10, 10, 18.0), (17191, 12, 31, 23.75)])
def test_calendar_arithmetic_round_trips_astronomical_years_without_datetime(date, calendar):
    jd = swe.julday(*date, cal=calendar)
    year, month, day, hour = swe.revjul(jd, cal=calendar)
    assert (year, month, day) == date[:3]
    assert hour == pytest.approx(date[3], abs=1e-7)


def test_calendar_definitions_have_independent_known_anchors():
    assert swe.julday(2000, 1, 1, 12., cal=1) == 2451545.
    assert swe.julday(1582, 10, 4, 0., cal=0) + 1 == swe.julday(1582, 10, 15, 0., cal=1)
    assert swe.julday(-4712, 1, 1, 12., cal=0) == 0.
    with pytest.raises((EphemerisError, ValueError)):
        swe.julday(1900, 2, 29, cal=1)
    assert math.isfinite(swe.julday(1900, 2, 29, cal=0))

def test_true_node_standard_id_is_distinct_from_mean_and_mean_south_node() -> None:
    jd = swe.julday(2024, 4, 8, 18.0)
    flags = swe.FLG_SWIEPH | swe.FLG_SPEED

    assert swe.MEAN_NODE == 10
    assert swe.TRUE_NODE == 11
    mean = swe.calc_ut(jd, swe.MEAN_NODE, flags)[0]
    true = swe.calc_ut(jd, swe.TRUE_NODE, flags)[0]
    south = swe.calc_ut(jd, "south_node", flags)[0]

    assert all(math.isfinite(value) for value in (*mean, *true, *south))
    assert abs(_signed_angle_delta(true[0], mean[0])) > 1e-5
    assert abs(abs(_signed_angle_delta(south[0], mean[0])) - 180.0) < 1e-9
    assert true != south

def test_facade_receipt_binds_flag_dependent_values_and_is_repeatable() -> None:
    jd = swe.julday(2024, 4, 8, 18.0)
    base_flags = swe.FLG_SWIEPH
    position_only = swe.calc_ut_with_receipt(jd, swe.MARS, base_flags)
    with_speed = swe.calc_ut_with_receipt(jd, swe.MARS, base_flags | swe.FLG_SPEED)
    repeated = swe.calc_ut_with_receipt(jd, swe.MARS, base_flags | swe.FLG_SPEED)

    assert position_only.values != with_speed.values
    assert position_only.flags != with_speed.flags
    assert position_only.receipt_sha256 != with_speed.receipt_sha256
    assert repeated == with_speed
    assert len(with_speed.receipt_sha256) == 64

def test_speed_flag_returns_all_centered_coordinate_derivatives() -> None:
    jd = swe.julday(2024, 4, 8, 18.0)
    half_span_days = 1e-3
    no_speed = swe.FLG_SWIEPH
    values, returned_flags = swe.calc_ut(jd, swe.MOON, no_speed | swe.FLG_SPEED)
    before = swe.calc_ut(jd - half_span_days, swe.MOON, no_speed)[0]
    after = swe.calc_ut(jd + half_span_days, swe.MOON, no_speed)[0]

    expected = (
        _signed_angle_delta(after[0], before[0]) / (2.0 * half_span_days),
        (after[1] - before[1]) / (2.0 * half_span_days),
        (after[2] - before[2]) / (2.0 * half_span_days),
    )
    assert returned_flags & swe.FLG_SPEED
    assert all(math.isfinite(value) for value in values)
    assert abs(expected[1]) > 1e-4
    assert abs(expected[2]) > 1e-8
    assert values[3] == pytest.approx(expected[0], abs=1e-4)
    assert values[4] == pytest.approx(expected[1], abs=1e-4)
    assert values[5] == pytest.approx(expected[2], abs=1e-7)

def test_houses_require_finite_dut1_and_use_it_to_derive_ut1() -> None:
    jd_utc = swe.julday(2024, 4, 8, 18.0)
    location = (23.0225, 72.5714)

    default_cusps, _ = swe.houses_ex(jd_utc, *location, b"P")
    assert len(default_cusps) == 12
    with pytest.raises(EphemerisError, match="dut1_seconds"):
        swe.houses_ex(jd_utc, *location, b"P", input_time_scale="UTC")
    for invalid in (math.nan, math.inf, -math.inf):
        with pytest.raises(EphemerisError, match="finite"):
            swe.houses_ex(
                jd_utc, *location, b"P", input_time_scale="UTC",
                dut1_seconds=invalid,
            )

    zero_cusps, zero_angles = swe.houses_ex(
        jd_utc, *location, b"P", input_time_scale="UTC", dut1_seconds=0.0
    )
    shifted_cusps, shifted_angles = swe.houses_ex(
        jd_utc, *location, b"P", input_time_scale="UTC", dut1_seconds=0.8
    )
    assert len(zero_cusps) == len(shifted_cusps) == 12
    assert len(zero_angles) == len(shifted_angles) == 10
    assert all(math.isfinite(value) for value in (*zero_cusps, *zero_angles[:4]))
    assert all(math.isnan(value) for value in zero_angles[4:])
    changes = [
        abs(_signed_angle_delta(later, earlier))
        for earlier, later in zip(
            (*zero_cusps, *zero_angles[:4]),
            (*shifted_cusps, *shifted_angles[:4]),
            strict=True,
        )
    ]
    assert max(changes) > 1e-6

def test_wide_tt_policy_requires_tdb_and_mean_equinox() -> None:
    ancient_tt = swe.julday(1500, 1, 1, 0.0)
    with pytest.raises(EphemerisError, match="jd_tdb"):
        swe.calc(ancient_tt, swe.MARS, swe.FLG_SWIEPH | swe.FLG_NONUT)
    with pytest.raises(EphemerisError, match="true-equinox"):
        swe.calc(ancient_tt, swe.MARS, swe.FLG_SWIEPH, jd_tdb=ancient_tt)

def test_stellar_ayanamsa_requires_explicit_anchor_input() -> None:
    jd_tt = swe.julday(2024, 4, 8, 18.0)
    flags = swe.FLG_SWIEPH | swe.FLG_SIDEREAL
    with pytest.raises(EphemerisError, match="anchor"):
        swe.calc(jd_tt, swe.MARS, flags, sidereal_mode="true_citra")
    values, _ = swe.calc(
        jd_tt, swe.MARS, flags, sidereal_mode="true_citra",
        anchor_tropical_longitude_deg=180.0,
    )
    assert all(math.isfinite(value) for value in values)

def test_stellar_anchor_speed_is_required_and_changes_sidereal_speed() -> None:
    jd_tt = swe.julday(2024, 4, 8, 18.0)
    flags = swe.FLG_SWIEPH | swe.FLG_SIDEREAL | swe.FLG_SPEED
    kwargs = {"sidereal_mode": "true_citra", "anchor_tropical_longitude_deg": 180.0}
    with pytest.raises(EphemerisError, match="anchor_tropical_speed"):
        swe.calc(jd_tt, swe.MARS, flags, **kwargs)
    with pytest.raises(EphemerisError, match="finite"):
        swe.calc(jd_tt, swe.MARS, flags, **kwargs, anchor_tropical_speed_deg_per_day=math.nan)
    frozen = swe.calc(
        jd_tt, swe.MARS, flags, **kwargs, anchor_tropical_speed_deg_per_day=0.0
    )[0]
    moving = swe.calc(
        jd_tt, swe.MARS, flags, **kwargs, anchor_tropical_speed_deg_per_day=1.0
    )[0]
    assert moving[3] == pytest.approx(frozen[3] - 1.0, abs=1e-7)
