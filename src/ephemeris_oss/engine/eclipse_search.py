"""Clean-room global solar and lunar eclipse search over RDG numerical states."""

from __future__ import annotations

import math
from typing import Any, Literal, Mapping

from .contracts import AstronomyDataUnavailable
from .eclipses import find_lunar_eclipses, find_solar_eclipses

MAX_SEARCH_DAYS = 3660.0
COARSE_WINDOW_DAYS = 90.0
SOLAR_TYPE_CODES = {"total": 4, "annular": 8, "partial": 16, "hybrid": 32}
LUNAR_TYPE_CODES = {"total": 4, "partial": 16, "penumbral": 64}


def global_eclipse(
    engine_or_provider: Any,
    jd_start: float,
    *,
    kind: Literal["solar", "lunar"],
    backward: bool = False,
) -> Mapping[str, Any]:
    """Find the next global solar or lunar eclipse from jd_start."""
    if not math.isfinite(jd_start):
        raise ValueError("jd_start must be finite")
    if backward:
        raise AstronomyDataUnavailable("backward eclipse search is not enabled")
    if kind not in ("solar", "lunar"):
        raise AstronomyDataUnavailable("global eclipse kind must be solar or lunar")

    engine = engine_or_provider if hasattr(engine_or_provider, "positions_tt") else None

    def _adapted_provider_positions(jd: float, bodies: Any) -> dict[str, dict[str, float]]:
        raw = engine_or_provider.planet_positions_tt(jd_tt=jd, bodies=bodies)["positions"]
        enriched: dict[str, dict[str, float]] = {}
        for k, v in raw.items():
            entry = dict(v)
            if "distance_km" not in entry and hasattr(engine_or_provider, "geocentric_state_at_tdb"):
                try:
                    import erfa as _erfa
                    body_key = str(k).strip().lower()
                    tt = (2451545.0, float(jd) - 2451545.0)
                    year = int(_erfa.jd2cal(*tt)[0])
                    offset = float(_erfa.dtdb(*tt, 0.0, 0.0, 0.0, 0.0))
                    tdb = tuple(float(val) for val in _erfa.tttdb(*tt, offset))
                    state = engine_or_provider.geocentric_state_at_tdb(
                        body=body_key,
                        tdb=tdb,
                        kernel_year=year,
                    )
                    px, py, pz = state.position_km
                    entry["distance_km"] = math.sqrt(px * px + py * py + pz * pz)
                except Exception:
                    pass
            enriched[k] = entry
        return enriched

    position_provider = (
        _adapted_provider_positions
        if engine is None and hasattr(engine_or_provider, "planet_positions_tt")
        else None
    )

    cursor = float(jd_start)
    limit = cursor + MAX_SEARCH_DAYS
    while cursor < limit:
        window_end = min(limit, cursor + COARSE_WINDOW_DAYS)
        if kind == "solar":
            events = find_solar_eclipses(
                cursor - 2.0,
                window_end,
                engine=engine,
                position_provider=position_provider,
            )
            for item in events:
                if item.greatest_jd_tt >= jd_start - 1e-6:
                    code = SOLAR_TYPE_CODES.get(item.classification, 16)
                    tret = (
                        item.greatest_jd_tt,
                        0.0,
                        0.0,
                        0.0,
                        0.0,
                        0.0,
                        0.0,
                        0.0,
                        item.magnitude,
                        item.gamma,
                    )
                    return {
                        "retflag": code,
                        "classification": item.classification,
                        "tret": tret,
                        "receipt_sha256": item.receipt_sha256,
                    }
        else:
            events_lunar = find_lunar_eclipses(
                cursor - 2.0,
                window_end,
                engine=engine,
                position_provider=position_provider,
            )
            for item in events_lunar:
                if item.greatest_jd_tt >= jd_start - 1e-6:
                    code = LUNAR_TYPE_CODES.get(item.classification, 64)
                    tret = (
                        item.greatest_jd_tt,
                        0.0,
                        item.u1_jd_tt or 0.0,
                        item.u4_jd_tt or 0.0,
                        item.u2_jd_tt or 0.0,
                        item.u3_jd_tt or 0.0,
                        item.p1_jd_tt or 0.0,
                        item.p4_jd_tt or 0.0,
                        item.umbral_magnitude,
                        item.penumbral_magnitude,
                    )
                    return {
                        "retflag": code,
                        "classification": item.classification,
                        "tret": tret,
                        "receipt_sha256": item.receipt_sha256,
                    }
        cursor = window_end
    raise AstronomyDataUnavailable(f"no {kind} eclipse found within {int(MAX_SEARCH_DAYS)} days")
