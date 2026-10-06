"""Engine adapters. Each maps sample rows to geocentric ICRF unit directions, keyed by id.

Modes, for every engine:

* ``geometric``: the target minus the geocentre at the same TDB instant, no light time;
* ``astrometric``: light-time corrected direction, no deflection, no aberration;
* ``apparent``: light time, gravitational deflection and annual aberration.

Only permissively licensed code is imported here. Copyleft comparators run as separate
processes from ``bench/comparators/`` and write their own results files.
"""

from __future__ import annotations

import math
from collections import defaultdict
from pathlib import Path
from typing import Mapping, Sequence

import erfa
import numpy as np

from .samples import split_jd

Vector = tuple[float, float, float]

# NAIF ids per the benchmark method: outer planets are system barycentres.
NAIF: dict[str, int] = {
    "sun": 10, "moon": 301, "mercury": 199, "venus": 299, "mars": 4,
    "jupiter": 5, "saturn": 6, "uranus": 7, "neptune": 8, "pluto": 9,
}


def _unit(vector: Sequence[float]) -> Vector:
    v = np.asarray(vector, dtype=np.float64)
    v = v / np.linalg.norm(v)
    return float(v[0]), float(v[1]), float(v[2])


def ours(samples: Sequence[Mapping[str, str]], kernel_path: str | Path) -> dict[str, Vector]:
    """Our engine, through the provider's TDB entry points (no UTC, no Earth orientation)."""

    from ephemeris_oss._api import Engine
    from ephemeris_oss.engine.numerical_provider import TimeScaleState

    out: dict[str, Vector] = {}
    with Engine.load(kernels={"DE440": Path(kernel_path)}, eop=None) as engine:
        provider = engine._provider
        for row in samples:
            tdb = split_jd(row["jd_tdb"])
            year = int(erfa.jd2cal(*tdb)[0])
            body, mode = row["body"], row["mode"]
            if mode == "geometric":
                state = provider.geocentric_state_at_tdb(body=body, tdb=tdb, kernel_year=year)
                out[row["id"]] = _unit(state.position_km)
                continue
            if mode not in ("astrometric", "apparent"):
                raise ValueError(f"unknown mode {mode!r}")
            tt = tuple(float(v) for v in erfa.tdbtt(*tdb, float(erfa.dtdb(*tdb, 0.0, 0.0, 0.0, 0.0))))
            times = TimeScaleState(utc=(math.nan, math.nan), tt=tt, tdb=tdb)
            apparent = mode == "apparent"
            place, _ = provider._apparent_state(
                body=body, instant_utc=None, observer=None, times=times, kernel_year=year,
                apply_deflection=apparent, apply_aberration=apparent,
            )
            out[row["id"]] = _unit(place.apparent_direction if apparent else place.astrometric_direction)
    return out


def t2_skyfield(samples: Sequence[Mapping[str, str]], kernel_path: str | Path) -> dict[str, Vector]:
    """T2 truth: Skyfield (MIT) reading the same kernel through jplephem.

    ``apparent`` uses Skyfield's default deflectors (Sun, Jupiter, Saturn); our engine
    deflects by the Sun only, so that difference is part of what the benchmark measures.
    """

    from skyfield.api import load, load_file

    ts = load.timescale(builtin=True)
    kernel = load_file(str(kernel_path))
    try:
        earth = kernel[399]
        groups: dict[tuple[str, str], list[Mapping[str, str]]] = defaultdict(list)
        for row in samples:
            groups[(row["body"], row["mode"])].append(row)
        out: dict[str, Vector] = {}
        for (body, mode), rows in sorted(groups.items()):
            target = kernel[NAIF[body]]
            parts = np.array([split_jd(row["jd_tdb"]) for row in rows])
            t = ts.tdb_jd(parts[:, 0], parts[:, 1])
            if mode == "geometric":
                xyz = (target - earth).at(t).position.au
            elif mode == "astrometric":
                xyz = earth.at(t).observe(target).position.au
            elif mode == "apparent":
                xyz = earth.at(t).observe(target).apparent().position.au
            else:
                raise ValueError(f"unknown mode {mode!r}")
            xyz = np.asarray(xyz).reshape(3, -1)
            for column, row in enumerate(rows):
                out[row["id"]] = _unit(xyz[:, column])
        return out
    finally:
        kernel.close()


ENGINES = {"ours": ours, "t2": t2_skyfield}
