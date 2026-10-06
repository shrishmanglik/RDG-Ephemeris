"""Error statistics between two engines' geocentric ICRF directions.

Two statistics are always reported side by side because they are not comparable:

* the angular separation, computed as atan2(|a x b|, a . b), which keeps full relative
  precision at micro-arcsecond angles where acos of a dot product rounds to zero;
* the larger of the longitude and latitude differences on the true ecliptic of date,
  the statistic the earlier internal scorecard used. The longitude difference is the raw
  wrapped difference, not scaled by cos(latitude), so it can exceed the separation by
  about a factor of the square root of two.

The ecliptic of date is evaluated at TT taken equal to the sample's TDB. TDB - TT is under
2 ms, over which precession and nutation move the frame by about 1e-9 arcsec, far below
any difference this harness reports.
"""

from __future__ import annotations

import math
from typing import Callable, Mapping, Sequence

import erfa
import numpy as np

ARCSEC_PER_RAD = 180.0 * 3600.0 / math.pi
BOOTSTRAP_RESAMPLES = 2000
_CHUNK = 250


def separations_arcsec(a: np.ndarray, b: np.ndarray) -> np.ndarray:
    """Row-wise angle between direction vectors (any length), in arcseconds."""

    a = np.asarray(a, dtype=np.float64).reshape(-1, 3)
    b = np.asarray(b, dtype=np.float64).reshape(-1, 3)
    cross = np.linalg.norm(np.cross(a, b), axis=1)
    dot = np.einsum("ij,ij->i", a, b)
    return np.arctan2(cross, dot) * ARCSEC_PER_RAD


def separation_arcsec(a: Sequence[float], b: Sequence[float]) -> float:
    return float(separations_arcsec(np.asarray(a), np.asarray(b))[0])


def _tt(jd: float) -> tuple[float, float]:
    whole = math.floor(jd)
    return float(whole), float(jd - whole)


def ecliptic_matrix(jd_tdb: float, kind: str = "true") -> np.ndarray:
    """Rotation from ICRF to the ecliptic of date.

    ``true``: ERFA ``pnm06a`` (GCRS to true equator and equinox, IAU 2006/2000A) followed by a
    rotation about x by the true obliquity (``obl06`` plus the nutation in obliquity).
    ``mean``: ERFA ``ecm06``, the mean ecliptic and equinox of date.
    """

    tt = _tt(jd_tdb)
    if kind == "mean":
        return np.asarray(erfa.ecm06(*tt), dtype=np.float64)
    if kind != "true":
        raise ValueError("kind must be 'true' or 'mean'")
    npb = np.asarray(erfa.pnm06a(*tt), dtype=np.float64)
    epsilon = float(erfa.obl06(*tt)) + float(erfa.nut06a(*tt)[1])
    c, s = math.cos(epsilon), math.sin(epsilon)
    to_ecliptic = np.array([[1.0, 0.0, 0.0], [0.0, c, s], [0.0, -s, c]])
    return to_ecliptic @ npb


def _lon_lat(vectors: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    x, y, z = vectors[:, 0], vectors[:, 1], vectors[:, 2]
    return np.arctan2(y, x), np.arctan2(z, np.hypot(x, y))


def ecliptic_component_diffs_arcsec(a: np.ndarray, b: np.ndarray, jds_tdb: Sequence[float]) -> np.ndarray:
    """Row-wise max(|d longitude|, |d latitude|) on the true ecliptic of date, in arcseconds."""

    a = np.asarray(a, dtype=np.float64).reshape(-1, 3)
    b = np.asarray(b, dtype=np.float64).reshape(-1, 3)
    matrices = np.stack([ecliptic_matrix(float(jd)) for jd in jds_tdb])
    lon_a, lat_a = _lon_lat(np.einsum("nij,nj->ni", matrices, a))
    lon_b, lat_b = _lon_lat(np.einsum("nij,nj->ni", matrices, b))
    d_lon = np.remainder(lon_b - lon_a + math.pi, 2.0 * math.pi) - math.pi
    return np.maximum(np.abs(d_lon), np.abs(lat_b - lat_a)) * ARCSEC_PER_RAD


def ecliptic_component_diff_arcsec(a: Sequence[float], b: Sequence[float], jd_tdb: float) -> float:
    return float(ecliptic_component_diffs_arcsec(np.asarray(a), np.asarray(b), [jd_tdb])[0])


def _p95(values: np.ndarray, axis: int | None = None) -> np.ndarray:
    return np.percentile(values, 95, axis=axis, method="linear")


STATISTICS: Mapping[str, Callable[..., np.ndarray]] = {
    "median": lambda v, axis=None: np.median(v, axis=axis),
    "p95": _p95,
    "max": lambda v, axis=None: np.max(v, axis=axis),
}


def bootstrap_ci(values: Sequence[float], statistic: Callable[..., np.ndarray], seed: int,
                 resamples: int = BOOTSTRAP_RESAMPLES) -> tuple[float, float]:
    """Seeded percentile-method 95% interval. ``statistic`` must accept ``axis``.

    Resamples are drawn in chunks so memory stays bounded for large strata; the chunking
    does not change the stream, because every chunk draws from the same generator in order.
    """

    data = np.asarray(values, dtype=np.float64)
    if data.size == 0:
        raise ValueError("cannot bootstrap an empty sample")
    rng = np.random.default_rng(seed)
    estimates = np.empty(resamples, dtype=np.float64)
    for start in range(0, resamples, _CHUNK):
        count = min(_CHUNK, resamples - start)
        idx = rng.integers(0, data.size, size=(count, data.size))
        estimates[start:start + count] = statistic(data[idx], axis=1)
    low, high = np.percentile(estimates, [2.5, 97.5], method="linear")
    return float(low), float(high)


def summary(values: Sequence[float], seed: int) -> dict:
    """n, median, P95 (numpy 'linear'), max, and a bootstrap 95% interval for each."""

    data = np.asarray(values, dtype=np.float64)
    out: dict = {"n": int(data.size)}
    intervals = {}
    for name, function in STATISTICS.items():
        out[name] = float(function(data))
        intervals[name] = list(bootstrap_ci(data, function, seed))
    out["ci95"] = intervals
    return out


def truth_floor(t1: Mapping[str, Sequence[float]], t2: Mapping[str, Sequence[float]]) -> float:
    """P99 of the separation between two truths over their shared ids (which must match)."""

    if set(t1) != set(t2) or not t1:
        raise ValueError("truth floor needs two non-empty results over the same ids")
    ids = sorted(t1)
    seps = separations_arcsec(np.array([t1[i] for i in ids]), np.array([t2[i] for i in ids]))
    return float(np.percentile(seps, 99, method="linear"))


def tie(value: float, floor: float | None) -> float | dict:
    """A value below the truth floor is a tie with truth and is never reported as a number."""

    if floor is not None and value < floor:
        return {"tie_with_truth": True}
    return value
