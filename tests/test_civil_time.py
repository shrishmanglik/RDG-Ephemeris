from __future__ import annotations

from datetime import date, datetime

import pytest

from ephemeris_oss.engine.civil_time import (
    CalendarSystem,
    UtcTimeScalePolicy,
    calendar_jd,
    resolve_local_civil_time,
    resolve_local_mean_time_as_ut1,
    validate_utc_instant,
)
from ephemeris_oss.engine.contracts import AstronomyDataUnavailable
from ephemeris_oss.engine.earth_orientation import UtcCalendarInstant


def test_historical_1582_transition_is_continuous_and_omitted_dates_fail() -> None:
    last_julian = calendar_jd(1582, 10, 4)
    first_gregorian = calendar_jd(1582, 10, 15)
    assert first_gregorian - last_julian == pytest.approx(1.0, abs=0.0)
    with pytest.raises(AstronomyDataUnavailable, match="omitted"):
        calendar_jd(1582, 10, 10)


def test_explicit_proleptic_calendars_remain_available() -> None:
    gregorian = calendar_jd(
        1500, 3, 1, calendar=CalendarSystem.PROLEPTIC_GREGORIAN
    )
    julian = calendar_jd(1500, 3, 1, calendar=CalendarSystem.JULIAN)
    assert julian - gregorian == pytest.approx(10.0, abs=0.0)


def test_toronto_dst_gap_and_fold_require_explicit_resolution() -> None:
    with pytest.raises(AstronomyDataUnavailable, match="nonexistent"):
        resolve_local_civil_time(datetime(2026, 3, 8, 2, 30), "America/Toronto")
    ambiguous = datetime(2026, 11, 1, 1, 30)
    with pytest.raises(AstronomyDataUnavailable, match="ambiguous"):
        resolve_local_civil_time(ambiguous, "America/Toronto")
    first = resolve_local_civil_time(ambiguous, "America/Toronto", fold=0)
    second = resolve_local_civil_time(ambiguous, "America/Toronto", fold=1)
    assert (second.instant_utc - first.instant_utc).total_seconds() == 3_600.0
    assert first.utc_offset_seconds == -4 * 3_600
    assert second.utc_offset_seconds == -5 * 3_600


def test_local_mean_time_uses_longitude_and_exposes_delta_t_uncertainty() -> None:
    local = datetime(1900, 1, 1, 12)
    at_greenwich = resolve_local_mean_time_as_ut1(
        local, 0.0, input_uncertainty_seconds=60.0
    )
    at_fifteen_east = resolve_local_mean_time_as_ut1(
        local, 15.0, input_uncertainty_seconds=60.0
    )
    assert (at_greenwich.ut1_jd - at_fifteen_east.ut1_jd) * 24.0 == pytest.approx(
        1.0, abs=1e-7
    )
    assert (
        at_greenwich.tt_jd - at_greenwich.ut1_jd
    ) * 86_400.0 == pytest.approx(at_greenwich.delta_t.seconds, abs=2e-5)
    assert at_greenwich.delta_t.uncertainty_seconds is not None


def test_utc_policy_fails_closed_before_and_after_versioned_window() -> None:
    policy = UtcTimeScalePolicy(
        date(1960, 1, 1), date(2026, 12, 31), "erfa-leap-table-test"
    )
    assert validate_utc_instant(
        datetime.fromisoformat("1961-01-01T00:00:00+00:00"), policy
    ).year == 1961
    for value in (
        datetime.fromisoformat("1959-12-31T23:59:59+00:00"),
        datetime.fromisoformat("2027-01-01T00:00:00+00:00"),
    ):
        with pytest.raises(AstronomyDataUnavailable, match="validity window"):
            validate_utc_instant(value, policy)


def test_utc_policy_accepts_explicit_leap_second_inside_versioned_window() -> None:
    policy = UtcTimeScalePolicy(
        date(1960, 1, 1), date(2026, 12, 31), "erfa-leap-table-test"
    )
    leap_second = UtcCalendarInstant(2016, 12, 31, 23, 59, 60.0)
    assert validate_utc_instant(leap_second, policy) is leap_second
