"""Civil time to UTC and the Delta-T estimate, with the policy each one applies."""

from __future__ import annotations

from datetime import datetime, timezone

from .engine.civil_time import resolve_local_civil_time
from .engine.earth_orientation import DeltaTEstimate, estimate_delta_t

__all__ = ["delta_t", "from_civil"]


def from_civil(year: int, month: int, day: int, hour: int = 0, minute: int = 0, second: int = 0,
               *, tz: str = "UTC", fold: int | None = None) -> datetime:
    """Resolve a wall-clock time in an IANA zone to an aware UTC datetime.

    Times that do not exist (a spring-forward gap) are rejected, and times that
    occur twice need ``fold`` (0 for the first, 1 for the second).
    """

    local = datetime(year, month, day, hour, minute, second)
    if tz.upper() == "UTC":
        return local.replace(tzinfo=timezone.utc)
    return resolve_local_civil_time(local, tz, fold=fold).instant_utc


def delta_t(decimal_year: float) -> DeltaTEstimate:
    """TT minus UT1 estimate, model named in the result (Espenak-Meeus polynomials, -1999 to 3000)."""

    return estimate_delta_t(decimal_year)
