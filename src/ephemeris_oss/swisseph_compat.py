"""Bounded Swiss-shaped facade over the compact DE440 engine.

This module intentionally implements only ``julday``, ``revjul``, named
sidereal modes, ``get_ayanamsa_ut``, ``calc_ut`` and ``houses_ex``.  Its
numeric Julian-date input is **UTC**, not UT1.  Callers that require Swiss
Ephemeris UT1 semantics must convert upstream or use another provider.
Unsupported flags, time scales and conventions fail explicitly.
"""

from __future__ import annotations

from contextvars import ContextVar
from dataclasses import dataclass
from functools import lru_cache
import re

from ._api import EphemerisError
from .adapter import (
    FLG_EQUATORIAL,
    FLG_SIDEREAL,
    FLG_SPEED,
    FLG_SWIEPH,
    FLG_TOPOCTR,
    JUPITER,
    MARS,
    MEAN_NODE,
    MERCURY,
    MOON,
    NEPTUNE,
    PLUTO,
    SATURN,
    SUN,
    TRUE_NODE,
    URANUS,
    VENUS,
    EphemerisAdapter,
)

SIDM_FAGAN_BRADLEY: int = 0
SIDM_LAHIRI: int = 1
SIDM_RAMAN: int = 3
SIDM_KRISHNAMURTI: int = 5

COMPATIBILITY_API_VERSION = "ephemeris_oss.swisseph_compat.v1"
INPUT_TIME_SCALE = "UTC"
COORDINATE_CONVENTION = "apparent geocentric ecliptic-of-date; degrees and AU"

_SIDEREAL_MODES = {
    SIDM_FAGAN_BRADLEY: "fagan_bradley",
    SIDM_LAHIRI: "lahiri",
    SIDM_RAMAN: "raman",
    SIDM_KRISHNAMURTI: "kp",
}
_CALC_FLAGS = FLG_SWIEPH | FLG_SPEED | FLG_SIDEREAL
_HOUSE_FLAGS = FLG_SWIEPH | FLG_SIDEREAL
_ayanamsa_context: ContextVar[str] = ContextVar(
    "swisseph_compat_ayanamsa", default="lahiri"
)
_SHA256 = re.compile(r"^[0-9a-f]{64}$")


@dataclass(frozen=True)
class CompatibilityCalculation:
    """Receipt-bearing result for the bounded compatibility contract."""

    values: tuple[float, float, float, float, float, float]
    flags: int
    receipt_sha256: str
    api: str
    input_time_scale: str
    ayanamsa: str
    coordinate_convention: str


@lru_cache(maxsize=1)
def _adapter() -> EphemerisAdapter:
    return EphemerisAdapter(kernels="compact")


def _reject_flag_bits(flags: int, supported: int, operation: str) -> int:
    value = int(flags)
    unsupported = value & ~supported
    if unsupported:
        raise EphemerisError(
            f"unsupported {operation} flag bits 0x{unsupported:x}; "
            "equatorial and topocentric compatibility are not implemented"
        )
    return value


def _require_utc(input_time_scale: str) -> None:
    if str(input_time_scale).strip().upper() != INPUT_TIME_SCALE:
        raise EphemerisError(
            "swisseph_compat numeric Julian dates are UTC; UT/UT1 input is not "
            "implemented because no DUT1 value is available"
        )


def set_sid_mode(mode: int, t0: float = 0.0, ayan_t0: float = 0.0) -> None:
    """Select a named sidereal mode for the current thread/task context."""

    if float(t0) != 0.0 or float(ayan_t0) != 0.0:
        raise EphemerisError("custom sidereal epochs are not implemented")
    try:
        selected = _SIDEREAL_MODES[int(mode)]
    except (KeyError, TypeError, ValueError) as exc:
        raise EphemerisError(f"unsupported sidereal mode {mode!r}") from exc
    _ayanamsa_context.set(selected)


def julday(year: int, month: int, day: int, hour: float = 0.0, cal: int = 1) -> float:
    """Convert a proleptic-Gregorian UTC calendar instant to Julian Date UTC."""

    if int(cal) != 1:
        raise EphemerisError("Julian-calendar conversion is not implemented")
    return _adapter().julday(year, month, day, hour)


def revjul(jd: float, cal: int = 1) -> tuple[int, int, int, float]:
    """Convert a Julian Date UTC to a proleptic-Gregorian calendar tuple."""

    if int(cal) != 1:
        raise EphemerisError("Julian-calendar conversion is not implemented")
    return _adapter().revjul(jd)


def get_ayanamsa_ut(jd: float) -> float:
    """Return ayanamsa for a Julian Date UTC (name retained for call shape)."""

    return _adapter().get_ayanamsa_ut(jd, mode=_ayanamsa_context.get())


def calc_ut_with_receipt(
    tjdutc: float,
    planet: int | str,
    flags: int = FLG_SWIEPH | FLG_SPEED,
    *,
    input_time_scale: str = INPUT_TIME_SCALE,
    sidereal_mode: int | None = None,
) -> CompatibilityCalculation:
    """Calculate one body and retain the compact-engine provenance receipt.

    ``tjdutc`` is Julian Date UTC.  ``sidereal_mode`` makes a calculation
    atomic and independent of context; when omitted the caller-local mode set
    by :func:`set_sid_mode` is used.
    """

    _require_utc(input_time_scale)
    requested = _reject_flag_bits(flags, _CALC_FLAGS, "calc_ut")
    if sidereal_mode is None:
        ayanamsa = _ayanamsa_context.get()
    else:
        try:
            ayanamsa = _SIDEREAL_MODES[int(sidereal_mode)]
        except (KeyError, TypeError, ValueError) as exc:
            raise EphemerisError(f"unsupported sidereal mode {sidereal_mode!r}") from exc
    result = _adapter().calc_ut(
        tjdutc,
        planet,
        sidereal=bool(requested & FLG_SIDEREAL),
        ayanamsa=ayanamsa,
    )
    speed = float(result.longitude_speed_deg_per_day) if requested & FLG_SPEED else 0.0
    values = (
        float(result.longitude_deg),
        float(result.latitude_deg),
        float(result.distance_au),
        speed,
        0.0,
        0.0,
    )
    receipt = str(result.receipt_sha256).lower()
    if not _SHA256.fullmatch(receipt):
        raise EphemerisError("compact adapter returned an invalid provenance receipt")
    return CompatibilityCalculation(
        values=values,
        flags=int(requested | FLG_SWIEPH),
        receipt_sha256=receipt,
        api=COMPATIBILITY_API_VERSION,
        input_time_scale=INPUT_TIME_SCALE,
        ayanamsa=ayanamsa,
        coordinate_convention=COORDINATE_CONVENTION,
    )


def calc_ut(
    tjdutc: float,
    planet: int | str,
    flags: int = FLG_SWIEPH | FLG_SPEED,
) -> tuple[tuple[float, float, float, float, float, float], int]:
    """Return Swiss-shaped coordinates for a Julian Date **UTC**.

    This preserves the familiar two-tuple call shape while deliberately
    narrowing the time-scale contract.  Use :func:`calc_ut_with_receipt` when
    provenance or an explicit time-scale assertion is required.
    """

    result = calc_ut_with_receipt(tjdutc, planet, flags)
    return result.values, result.flags


def houses_ex(
    tjdutc: float,
    lat: float,
    lon: float,
    hsys: str | bytes = b"P",
    flags: int = 0,
) -> tuple[tuple[float, ...], tuple[float, ...]]:
    """Return 12 cusps and 10 angles for a Julian Date UTC."""

    requested = _reject_flag_bits(flags, _HOUSE_FLAGS, "houses_ex")
    ayanamsa = _ayanamsa_context.get()
    if requested & FLG_SIDEREAL and ayanamsa != "lahiri":
        raise EphemerisError(
            "houses_ex sidereal compatibility currently supports Lahiri only"
        )
    return _adapter().houses_ex(tjdutc, lat, lon, hsys, flags=requested)


__all__ = [
    "COMPATIBILITY_API_VERSION", "COORDINATE_CONVENTION", "INPUT_TIME_SCALE",
    "CompatibilityCalculation", "FLG_EQUATORIAL", "FLG_SIDEREAL",
    "FLG_SPEED", "FLG_SWIEPH", "FLG_TOPOCTR", "JUPITER", "MARS",
    "MEAN_NODE", "MERCURY", "MOON", "NEPTUNE", "PLUTO", "SATURN",
    "SIDM_FAGAN_BRADLEY", "SIDM_KRISHNAMURTI", "SIDM_LAHIRI",
    "SIDM_RAMAN", "SUN", "TRUE_NODE", "URANUS", "VENUS", "calc_ut",
    "calc_ut_with_receipt", "get_ayanamsa_ut", "houses_ex", "julday",
    "revjul", "set_sid_mode",
]
