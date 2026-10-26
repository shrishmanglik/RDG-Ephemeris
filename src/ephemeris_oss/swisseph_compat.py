"""Bounded signature-compatible v2 facade over the deterministic JPL engine.

``calc_ut`` and ``houses_ex`` accept UT1 by default, matching their names.
UTC is accepted only with caller-supplied DUT1. Wide epochs use explicit
TT/TDB through :func:`calc`; time scales are never silently interchanged.
"""
from __future__ import annotations

from contextlib import contextmanager
from contextvars import ContextVar
from dataclasses import dataclass
from functools import lru_cache
import math
from pathlib import Path
import re
from typing import Any, Iterator, Mapping

import erfa

from ._api import (
    UTC_VALID_FROM, UTC_VALID_THROUGH, EarthOrientation, EphemerisError,
)
from .adapter import (
    FLG_EQUATORIAL, FLG_SIDEREAL, FLG_SPEED, FLG_SWIEPH, FLG_TOPOCTR,
    JUPITER, MARS, MERCURY, MOON, NEPTUNE, PLUTO, SATURN, SUN, URANUS,
    VENUS, EphemerisAdapter,
)
from .engine.civil_time import CalendarSystem, calendar_date, calendar_jd
from .engine.conventions import AYANAMSA_CATALOG, validate_tt_tdb
from .engine.earth_orientation import estimate_delta_t
from .engine.receipt import canonical_hash

SIDM_FAGAN_BRADLEY = 0
SIDM_LAHIRI = 1
SIDM_RAMAN = 3
SIDM_KRISHNAMURTI = 5
MEAN_NODE = 10
TRUE_NODE = 11
SOUTH_NODE = "south_node"
GREG_CAL = 1
JUL_CAL = 0
FLG_NONUT = 64
FLG_JPLEPH = 1
COMPATIBILITY_API_VERSION = "ephemeris_oss.compat.v2"
INPUT_TIME_SCALE = "UT1"
DERIVATIVE_STEP_DAYS = 0.001
_SECONDS_PER_DAY = 86_400.0
_SIDEREAL_MODES = {
    SIDM_FAGAN_BRADLEY: "fagan_bradley", SIDM_LAHIRI: "lahiri",
    SIDM_RAMAN: "raman", SIDM_KRISHNAMURTI: "kp",
}
_CALC_FLAGS = FLG_JPLEPH | FLG_SWIEPH | FLG_SPEED | FLG_SIDEREAL | FLG_NONUT
_HOUSE_FLAGS = FLG_SWIEPH | FLG_SIDEREAL
_ayanamsa_context: ContextVar[str] = ContextVar("ephemeris_compat_ayanamsa", default="lahiri")
_adapter_context: ContextVar[EphemerisAdapter | None] = ContextVar(
    "ephemeris_compat_adapter", default=None
)
_SHA256 = re.compile(r"^[0-9a-f]{64}$")


@dataclass(frozen=True)
class CompatibilityCalculation:
    values: tuple[float, float, float, float, float, float]
    flags: int
    receipt_sha256: str
    api: str
    input_time_scale: str
    ayanamsa: str | None
    coordinate_convention: str
    jd_ut1: float | None
    jd_tt: float
    jd_tdb: float


@lru_cache(maxsize=1)
def _default_adapter() -> EphemerisAdapter:
    return EphemerisAdapter(kernels="compact")


def _adapter() -> EphemerisAdapter:
    return _adapter_context.get() or _default_adapter()


@contextmanager
def adapter_context(adapter: EphemerisAdapter) -> Iterator[EphemerisAdapter]:
    """Use a caller-owned verified adapter in this task/thread context."""
    if not isinstance(adapter, EphemerisAdapter):
        raise TypeError("adapter must be an EphemerisAdapter")
    token = _adapter_context.set(adapter)
    try:
        yield adapter
    finally:
        _adapter_context.reset(token)


def configure(
    kernels: str | Path | Mapping[str, str | Path] = "compact",
    *, eop: str | EarthOrientation | Any | None = "auto",
    cache_dir: str | Path | None = None,
) -> EphemerisAdapter:
    """Create and select a verified compact, auto, DE440, or DE441 adapter."""
    adapter = EphemerisAdapter(kernels=kernels, eop=eop, cache_dir=cache_dir)
    _adapter_context.set(adapter)
    return adapter


def _reject_flag_bits(flags: int, supported: int, operation: str) -> int:
    if isinstance(flags, bool):
        raise EphemerisError(f"{operation} flags must be an integer bit mask")
    value = int(flags)
    unsupported = value & ~supported
    if unsupported:
        raise EphemerisError(f"unsupported {operation} flag bits 0x{unsupported:x}")
    return value


def _finite(value: float | None, name: str, *, required: bool = True) -> float | None:
    if value is None and not required:
        return None
    if value is None:
        raise EphemerisError(f"{name} is required")
    number = float(value)
    if not math.isfinite(number):
        raise EphemerisError(f"{name} must be finite")
    return number


def _calendar(cal: int) -> CalendarSystem:
    if int(cal) == GREG_CAL:
        return CalendarSystem.PROLEPTIC_GREGORIAN
    if int(cal) == JUL_CAL:
        return CalendarSystem.JULIAN
    raise EphemerisError("calendar must be GREG_CAL (1) or JUL_CAL (0)")


def julday(year: int, month: int, day: int, hour: float = 0.0, cal: int = GREG_CAL) -> float:
    hour_value = float(_finite(hour, "hour"))
    if not 0.0 <= hour_value < 24.0:
        raise EphemerisError("hour must be within [0, 24)")
    try:
        return float(calendar_jd(
            int(year), int(month), int(day), hour_value / 24.0, calendar=_calendar(cal)
        ))
    except Exception as error:
        raise EphemerisError(str(error)) from error


def revjul(jd: float, cal: int = GREG_CAL) -> tuple[int, int, int, float]:
    value = float(_finite(jd, "jd"))
    try:
        year, month, day, fraction = calendar_date(value, calendar=_calendar(cal))
    except Exception as error:
        raise EphemerisError(str(error)) from error
    return int(year), int(month), int(day), float(fraction) * 24.0


def _decimal_year(jd: float) -> float:
    year = calendar_date(jd, calendar=CalendarSystem.PROLEPTIC_GREGORIAN)[0]
    start = calendar_jd(year, 1, 1, calendar=CalendarSystem.PROLEPTIC_GREGORIAN)
    end = calendar_jd(year + 1, 1, 1, calendar=CalendarSystem.PROLEPTIC_GREGORIAN)
    return float(year) + (jd - start) / (end - start)


def _resolve_ut1_tt(
    jd: float, *, input_time_scale: str, dut1_seconds: float | None,
    delta_t_seconds: float | None,
) -> tuple[float, float, float, str]:
    value = float(_finite(jd, "Julian date"))
    scale = str(input_time_scale).strip().upper()
    if scale == "UTC":
        dut1 = float(_finite(dut1_seconds, "dut1_seconds"))
        ut1 = value + dut1 / _SECONDS_PER_DAY
        year, month, day, fraction = calendar_date(
            value, calendar=CalendarSystem.PROLEPTIC_GREGORIAN
        )
        utc_start = calendar_jd(
            UTC_VALID_FROM.year, UTC_VALID_FROM.month, UTC_VALID_FROM.day,
            calendar=CalendarSystem.PROLEPTIC_GREGORIAN,
        )
        utc_stop = calendar_jd(
            UTC_VALID_THROUGH.year + 1, 1, 1,
            calendar=CalendarSystem.PROLEPTIC_GREGORIAN,
        )
        if utc_start <= value < utc_stop:
            try:
                tai_minus_utc = float(erfa.dat(year, month, day, fraction))
            except Exception as error:
                raise EphemerisError("UTC instant is outside the versioned ERFA table") from error
            standards_delta_t = tai_minus_utc + 32.184 - dut1
            if delta_t_seconds is not None:
                supplied = float(_finite(delta_t_seconds, "delta_t_seconds"))
                if not math.isclose(supplied, standards_delta_t, abs_tol=1e-6):
                    raise EphemerisError(
                        "delta_t_seconds contradicts versioned UTC, TAI, TT, and DUT1 clocks"
                    )
            policy = (
                f"utc_erfa-{erfa.__version__}_{UTC_VALID_FROM.isoformat()}_"
                f"{UTC_VALID_THROUGH.isoformat()}"
            )
            return ut1, value + (tai_minus_utc + 32.184) / _SECONDS_PER_DAY, standards_delta_t, policy
        if delta_t_seconds is None:
            raise EphemerisError(
                "delta_t_seconds is required for UTC outside the versioned 1960..2026 window"
            )
    elif scale == "UT1":
        if dut1_seconds is not None:
            raise EphemerisError("dut1_seconds is only valid when input_time_scale='UTC'")
        ut1 = value
    else:
        raise EphemerisError("input_time_scale must be 'UT1' or explicit 'UTC'")
    if delta_t_seconds is None:
        try:
            delta_t = float(estimate_delta_t(_decimal_year(ut1)).seconds)
        except Exception as error:
            raise EphemerisError(
                "delta_t_seconds is required outside the bounded Delta-T model"
            ) from error
        policy = "bounded_espenak_meeus"
    else:
        delta_t = float(_finite(delta_t_seconds, "delta_t_seconds"))
        policy = "caller_supplied"
    return ut1, ut1 + delta_t / _SECONDS_PER_DAY, delta_t, policy


def _tdb_from_tt(jd_tt: float, jd_tdb: float | None) -> float:
    if jd_tdb is not None:
        supplied = float(_finite(jd_tdb, "jd_tdb"))
        try:
            validate_tt_tdb(jd_tt, supplied)
        except Exception as error:
            raise EphemerisError(str(error)) from error
        return supplied
    year = calendar_date(jd_tt, calendar=CalendarSystem.PROLEPTIC_GREGORIAN)[0]
    if not 1600 <= year <= 2400:
        raise EphemerisError("jd_tdb is required outside TT years 1600..2400")
    tt = (2451545.0, jd_tt - 2451545.0)
    return float(sum(erfa.tttdb(*tt, float(erfa.dtdb(*tt, 0.0, 0.0, 0.0, 0.0)))))


def _ayanamsa(mode: int | str | None) -> str:
    if mode is None:
        return _ayanamsa_context.get()
    if isinstance(mode, int) and not isinstance(mode, bool):
        try:
            return _SIDEREAL_MODES[mode]
        except KeyError as error:
            raise EphemerisError(f"unsupported sidereal mode {mode!r}") from error
    key = str(mode).strip().lower().replace("-", "_").replace(" ", "_")
    if key not in AYANAMSA_CATALOG:
        raise EphemerisError(f"unsupported sidereal mode {mode!r}")
    return key


def set_sid_mode(mode: int | str, t0: float = 0.0, ayan_t0: float = 0.0) -> None:
    if float(t0) != 0.0 or float(ayan_t0) != 0.0:
        raise EphemerisError("custom sidereal epochs are not implemented")
    _ayanamsa_context.set(_ayanamsa(mode))


def _calculation(
    jd_tt: float, planet: int | str, flags: int, *, jd_tdb: float | None,
    jd_ut1: float | None, input_time_scale: str, time_policy: str,
    sidereal_mode: int | str | None,
    anchor_tropical_longitude_deg: float | None,
    anchor_tropical_speed_deg_per_day: float | None,
    dut1_seconds: float | None,
    delta_t_seconds: float | None,
) -> CompatibilityCalculation:
    requested = _reject_flag_bits(flags, _CALC_FLAGS, "calculation")
    tt_value = float(_finite(jd_tt, "jd_tt"))
    tdb_value = _tdb_from_tt(tt_value, jd_tdb)
    ayanamsa = _ayanamsa(sidereal_mode) if requested & FLG_SIDEREAL else None
    result = _adapter().calc_tt(
        tt_value, planet, jd_tdb=tdb_value, sidereal=ayanamsa is not None,
        ayanamsa=ayanamsa or "lahiri", nonut=bool(requested & FLG_NONUT),
        derivative_step_days=DERIVATIVE_STEP_DAYS,
        anchor_tropical_longitude_deg=anchor_tropical_longitude_deg,
        anchor_tropical_speed_deg_per_day=anchor_tropical_speed_deg_per_day,
        include_derivatives=bool(requested & FLG_SPEED),
    )
    values = (
        float(result.longitude_deg), float(result.latitude_deg), float(result.distance_au),
        float(result.longitude_speed_deg_per_day) if requested & FLG_SPEED else 0.0,
        float(result.latitude_speed_deg_per_day) if requested & FLG_SPEED else 0.0,
        float(result.distance_speed_au_per_day) if requested & FLG_SPEED else 0.0,
    )
    returned_flags = int((requested & ~(FLG_SWIEPH | FLG_JPLEPH)) | FLG_JPLEPH)
    artifact = _adapter().engine._provider._kernel_registry.artifact_for_tdb_jd(tdb_value)
    if ayanamsa is not None:
        convention = "mean ecliptic/sidereal reduction"
    else:
        convention = "mean ecliptic/equinox" if requested & FLG_NONUT else "true ecliptic/equinox"
    payload = {
        "schema": "ephemeris-oss.compat.v2", "api": COMPATIBILITY_API_VERSION,
        "values": values, "requested_flags": requested, "flags": returned_flags,
        "input_time_scale": input_time_scale,
        "time_policy": time_policy, "jd_ut1": jd_ut1, "jd_tt": tt_value,
        "dut1_seconds": dut1_seconds, "delta_t_seconds": delta_t_seconds,
        "jd_tdb": tdb_value, "ayanamsa": ayanamsa,
        "anchor_tropical_longitude_deg": anchor_tropical_longitude_deg,
        "anchor_tropical_speed_deg_per_day": anchor_tropical_speed_deg_per_day,
        "coordinate_convention": convention,
        "derivative_step_days": DERIVATIVE_STEP_DAYS if requested & FLG_SPEED else None,
        "kernel_identifier": artifact.identifier, "kernel_sha256": artifact.sha256.lower(),
        "kernel_provenance": (
            "JPL-derived compact" if artifact.identifier.startswith("COMPACT-") else "JPL SPK"
        ),
        "underlying_receipts": [result.receipt_sha256],
    }
    receipt = canonical_hash(payload)
    if not _SHA256.fullmatch(receipt):
        raise EphemerisError("compatibility calculation produced an invalid receipt")
    return CompatibilityCalculation(
        values, returned_flags, receipt, COMPATIBILITY_API_VERSION,
        input_time_scale, ayanamsa, convention, jd_ut1, tt_value, tdb_value,
    )


def calc_with_receipt(
    jd_tt: float, planet: int | str, flags: int = FLG_SWIEPH | FLG_SPEED,
    *, jd_tdb: float | None = None, sidereal_mode: int | str | None = None,
    anchor_tropical_longitude_deg: float | None = None,
    anchor_tropical_speed_deg_per_day: float | None = None,
) -> CompatibilityCalculation:
    return _calculation(
        jd_tt, planet, flags, jd_tdb=jd_tdb, jd_ut1=None,
        input_time_scale="TT", time_policy="explicit_tt", sidereal_mode=sidereal_mode,
        anchor_tropical_longitude_deg=anchor_tropical_longitude_deg,
        anchor_tropical_speed_deg_per_day=anchor_tropical_speed_deg_per_day,
        dut1_seconds=None, delta_t_seconds=None,
    )


def calc(
    jd_tt: float, planet: int | str, flags: int = FLG_SWIEPH | FLG_SPEED,
    *, jd_tdb: float | None = None, sidereal_mode: int | str | None = None,
    anchor_tropical_longitude_deg: float | None = None,
    anchor_tropical_speed_deg_per_day: float | None = None,
) -> tuple[tuple[float, float, float, float, float, float], int]:
    result = calc_with_receipt(
        jd_tt, planet, flags, jd_tdb=jd_tdb, sidereal_mode=sidereal_mode,
        anchor_tropical_longitude_deg=anchor_tropical_longitude_deg,
        anchor_tropical_speed_deg_per_day=anchor_tropical_speed_deg_per_day,
    )
    return result.values, result.flags


def calc_ut_with_receipt(
    tjdut: float, planet: int | str, flags: int = FLG_SWIEPH | FLG_SPEED, *,
    input_time_scale: str = INPUT_TIME_SCALE, dut1_seconds: float | None = None,
    delta_t_seconds: float | None = None, jd_tdb: float | None = None,
    sidereal_mode: int | str | None = None,
    anchor_tropical_longitude_deg: float | None = None,
    anchor_tropical_speed_deg_per_day: float | None = None,
) -> CompatibilityCalculation:
    ut1, tt, resolved_delta_t, policy = _resolve_ut1_tt(
        tjdut, input_time_scale=input_time_scale, dut1_seconds=dut1_seconds,
        delta_t_seconds=delta_t_seconds,
    )
    return _calculation(
        tt, planet, flags, jd_tdb=jd_tdb, jd_ut1=ut1,
        input_time_scale=str(input_time_scale).strip().upper(),
        time_policy=policy, sidereal_mode=sidereal_mode,
        anchor_tropical_longitude_deg=anchor_tropical_longitude_deg,
        anchor_tropical_speed_deg_per_day=anchor_tropical_speed_deg_per_day,
        dut1_seconds=dut1_seconds if str(input_time_scale).strip().upper() == "UTC" else None,
        delta_t_seconds=resolved_delta_t,
    )


def calc_ut(
    tjdut: float, planet: int | str, flags: int = FLG_SWIEPH | FLG_SPEED, **kwargs: Any,
) -> tuple[tuple[float, float, float, float, float, float], int]:
    result = calc_ut_with_receipt(tjdut, planet, flags, **kwargs)
    return result.values, result.flags


def get_ayanamsa_ut(
    tjdut: float, *, input_time_scale: str = INPUT_TIME_SCALE,
    dut1_seconds: float | None = None, delta_t_seconds: float | None = None,
    anchor_tropical_longitude_deg: float | None = None,
) -> float:
    _ut1, tt, _delta_t, _policy = _resolve_ut1_tt(
        tjdut, input_time_scale=input_time_scale, dut1_seconds=dut1_seconds,
        delta_t_seconds=delta_t_seconds,
    )
    return _adapter().get_ayanamsa_tt(
        tt,
        _ayanamsa_context.get(),
        anchor_tropical_longitude_deg=anchor_tropical_longitude_deg,
        true=False,
    )


def houses_ex(
    tjdut: float, lat: float, lon: float, hsys: str | bytes = b"P", flags: int = 0, *,
    input_time_scale: str = INPUT_TIME_SCALE, dut1_seconds: float | None = None,
    delta_t_seconds: float | None = None,
) -> tuple[tuple[float, ...], tuple[float, ...]]:
    requested = _reject_flag_bits(flags, _HOUSE_FLAGS, "houses_ex")
    ut1, tt, _delta_t, _policy = _resolve_ut1_tt(
        tjdut, input_time_scale=input_time_scale, dut1_seconds=dut1_seconds,
        delta_t_seconds=delta_t_seconds,
    )
    ayanamsa = _ayanamsa_context.get()
    if requested & FLG_SIDEREAL and ayanamsa != "lahiri":
        raise EphemerisError("houses_ex sidereal compatibility currently supports Lahiri only")
    year = calendar_date(tt, calendar=CalendarSystem.PROLEPTIC_GREGORIAN)[0]
    if not 1600 <= year <= 2400:
        raise EphemerisError("house calculations are supported only for TT years 1600..2400")
    # ascmc slots 0..3 are Ascendant, MC, ARMC, and Vertex. Remaining
    # unsupported angles are NaN, never fabricated measured zeros.
    return _adapter().houses_ex(ut1, lat, lon, hsys, requested, tt_jd=tt)


__all__ = [
    "COMPATIBILITY_API_VERSION", "DERIVATIVE_STEP_DAYS", "FLG_EQUATORIAL",
    "FLG_JPLEPH", "FLG_NONUT", "FLG_SIDEREAL", "FLG_SPEED", "FLG_SWIEPH", "FLG_TOPOCTR",
    "GREG_CAL", "INPUT_TIME_SCALE", "JUL_CAL", "JUPITER", "MARS", "MEAN_NODE",
    "MERCURY", "MOON", "NEPTUNE", "PLUTO", "SATURN", "SIDM_FAGAN_BRADLEY",
    "SIDM_KRISHNAMURTI", "SIDM_LAHIRI", "SIDM_RAMAN", "SOUTH_NODE", "SUN",
    "TRUE_NODE", "URANUS", "VENUS", "CompatibilityCalculation", "adapter_context",
    "calc", "calc_ut", "calc_ut_with_receipt", "calc_with_receipt", "configure",
    "get_ayanamsa_ut", "houses_ex", "julday", "revjul", "set_sid_mode",
]
