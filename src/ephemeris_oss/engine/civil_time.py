"""Explicit civil-time and historical-calendar policy for astronomy inputs."""

from __future__ import annotations

import math
from dataclasses import dataclass
from datetime import date, datetime, timezone
from enum import Enum
from importlib.metadata import PackageNotFoundError, version
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

import erfa

from .contracts import AstronomyDataUnavailable
from .earth_orientation import DeltaTEstimate, UtcCalendarInstant, estimate_delta_t

SECONDS_PER_DAY = 86_400.0


class CalendarSystem(str, Enum):
    PROLEPTIC_GREGORIAN = "proleptic_gregorian"
    JULIAN = "julian"
    HISTORICAL_1582 = "historical_1582"


@dataclass(frozen=True)
class LocalCivilResolution:
    instant_utc: datetime
    zone_name: str
    utc_offset_seconds: int
    fold: int
    tzdb_version: str


@dataclass(frozen=True)
class HistoricalTimeResolution:
    ut1_jd: float
    tt_jd: float
    delta_t: DeltaTEstimate
    calendar: CalendarSystem
    local_mean_time_longitude_deg: float
    input_uncertainty_seconds: float


@dataclass(frozen=True)
class UtcTimeScalePolicy:
    valid_from: date
    valid_through: date
    leap_second_version: str

    def __post_init__(self) -> None:
        if self.valid_from < date(1550, 1, 1):
            raise ValueError("UTC policy cannot begin before 1550")
        if self.valid_through < self.valid_from:
            raise ValueError("UTC policy validity window is inverted")
        if not self.leap_second_version.strip():
            raise ValueError("leap_second_version must be non-empty")


def _tzdb_version() -> str:
    try:
        return f"tzdata-{version('tzdata')}"
    except PackageNotFoundError:
        return "system-zoneinfo-unversioned"


def resolve_local_civil_time(
    local_time: datetime,
    zone_name: str,
    *,
    fold: int | None = None,
) -> LocalCivilResolution:
    """Resolve an IANA local time, rejecting gaps and unresolved folds."""

    if local_time.tzinfo is not None:
        raise ValueError("local_time must be naive; zone_name supplies its timezone")
    if fold not in {None, 0, 1}:
        raise ValueError("fold must be 0, 1, or None")
    try:
        zone = ZoneInfo(zone_name)
    except ZoneInfoNotFoundError as error:
        raise AstronomyDataUnavailable(f"unknown IANA timezone: {zone_name!r}") from error

    candidates: dict[datetime, tuple[datetime, int, int]] = {}
    for candidate_fold in (0, 1):
        aware = local_time.replace(tzinfo=zone, fold=candidate_fold)
        instant = aware.astimezone(timezone.utc)
        round_trip = instant.astimezone(zone)
        if round_trip.replace(tzinfo=None) != local_time:
            continue
        offset = aware.utcoffset()
        if offset is None:
            continue
        candidates[instant] = (instant, int(offset.total_seconds()), candidate_fold)

    if not candidates:
        raise AstronomyDataUnavailable(
            f"nonexistent local civil time in {zone_name}: {local_time.isoformat()}"
        )
    ordered = sorted(candidates.values(), key=lambda item: item[0])
    if len(ordered) > 1 and fold is None:
        raise AstronomyDataUnavailable(
            f"ambiguous local civil time in {zone_name}; explicit fold is required"
        )
    if fold is None:
        chosen = ordered[0]
    else:
        matches = [candidate for candidate in ordered if candidate[2] == fold]
        if not matches:
            raise AstronomyDataUnavailable(
                f"fold={fold} is not valid for {local_time.isoformat()} in {zone_name}"
            )
        chosen = matches[0]
    return LocalCivilResolution(
        instant_utc=chosen[0],
        zone_name=zone_name,
        utc_offset_seconds=chosen[1],
        fold=chosen[2],
        tzdb_version=_tzdb_version(),
    )


def calendar_jd(
    year: int,
    month: int,
    day: int,
    day_fraction: float = 0.0,
    *,
    calendar: CalendarSystem = CalendarSystem.HISTORICAL_1582,
) -> float:
    """Convert a declared civil calendar date to Julian Date.

    The historical policy rejects the ten dates omitted during the 1582 Roman
    transition. Jurisdictions that adopted later must use an explicit
    proleptic Gregorian or Julian policy instead of silently assuming Rome.
    """

    if not math.isfinite(day_fraction) or not 0.0 <= day_fraction < 1.0:
        raise ValueError("day_fraction must be finite and within [0, 1)")
    civil = date(year, month, day)
    effective = calendar
    if calendar is CalendarSystem.HISTORICAL_1582:
        if date(1582, 10, 5) <= civil <= date(1582, 10, 14):
            raise AstronomyDataUnavailable("date was omitted by the 1582 calendar transition")
        effective = (
            CalendarSystem.JULIAN
            if civil <= date(1582, 10, 4)
            else CalendarSystem.PROLEPTIC_GREGORIAN
        )
    if effective is CalendarSystem.PROLEPTIC_GREGORIAN:
        first, second = erfa.cal2jd(year, month, day)
        return float(first + second + day_fraction)

    adjusted_year = year - 1 if month <= 2 else year
    adjusted_month = month + 12 if month <= 2 else month
    return float(
        math.floor(365.25 * (adjusted_year + 4716))
        + math.floor(30.6001 * (adjusted_month + 1))
        + day
        - 1524.5
        + day_fraction
    )


def resolve_local_mean_time_as_ut1(
    local_time: datetime,
    longitude_deg_east: float,
    *,
    calendar: CalendarSystem = CalendarSystem.HISTORICAL_1582,
    input_uncertainty_seconds: float,
) -> HistoricalTimeResolution:
    """Resolve pre-standard local mean time to UT1 and uncertainty-bearing TT."""

    if local_time.tzinfo is not None:
        raise ValueError("historical local mean time must be naive")
    if not math.isfinite(longitude_deg_east) or not -180.0 <= longitude_deg_east <= 180.0:
        raise ValueError("longitude_deg_east must be within [-180, 180]")
    if not math.isfinite(input_uncertainty_seconds) or input_uncertainty_seconds < 0.0:
        raise ValueError("input_uncertainty_seconds must be finite and non-negative")
    seconds = (
        local_time.hour * 3_600.0
        + local_time.minute * 60.0
        + local_time.second
        + local_time.microsecond / 1_000_000.0
    )
    local_jd = calendar_jd(
        local_time.year,
        local_time.month,
        local_time.day,
        seconds / SECONDS_PER_DAY,
        calendar=calendar,
    )
    ut1_jd = local_jd - longitude_deg_east / 360.0
    year_start = calendar_jd(local_time.year, 1, 1, calendar=calendar)
    next_year = calendar_jd(local_time.year + 1, 1, 1, calendar=calendar)
    decimal_year = local_time.year + (ut1_jd - year_start) / (next_year - year_start)
    delta_t = estimate_delta_t(decimal_year)
    return HistoricalTimeResolution(
        ut1_jd=ut1_jd,
        tt_jd=ut1_jd + delta_t.seconds / SECONDS_PER_DAY,
        delta_t=delta_t,
        calendar=calendar,
        local_mean_time_longitude_deg=longitude_deg_east,
        input_uncertainty_seconds=input_uncertainty_seconds,
    )


def validate_utc_instant(
    instant: datetime | UtcCalendarInstant, policy: UtcTimeScalePolicy
) -> datetime | UtcCalendarInstant:
    """Validate that UTC is defined by the versioned provider time policy."""

    if isinstance(instant, UtcCalendarInstant):
        civil_date = date(instant.year, instant.month, instant.day)
        utc: datetime | UtcCalendarInstant = instant
    else:
        if instant.tzinfo is None or instant.utcoffset() is None:
            raise ValueError("UTC instant must be timezone-aware")
        utc = instant.astimezone(timezone.utc)
        civil_date = utc.date()
    if not policy.valid_from <= civil_date <= policy.valid_through:
        raise AstronomyDataUnavailable(
            "UTC instant is outside the versioned leap-second validity window "
            f"[{policy.valid_from.isoformat()}, {policy.valid_through.isoformat()}]"
        )
    return utc
