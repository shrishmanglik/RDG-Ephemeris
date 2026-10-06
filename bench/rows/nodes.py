"""Benchmark row: the Moon's ascending node, true (osculating) and mean.

    python -m bench.rows.nodes --kernel DE440.bsp --out bench/data/rows/nodes.json

True node. The engine's value comes from its provider path ``_osculating_lunar_node``, the
code ``Engine.nodes(t, kind="true")`` runs, called directly so the sample can span 1900-2100
(the public API accepts UTC only inside its leap-second window). That path takes the
geometric geocentric Moon state from DE440 in ICRF and rotates position and velocity with
ERFA ``ecm06`` at the instant's TT: the MEAN ecliptic and equinox of date (IAU 2006), with no
nutation. The reference here must use the same frame, or the row would measure nutation in
longitude (up to about 17 arcsec) instead of the engine: it reads the Moon and Earth from the
same kernel through Skyfield (an independent reader), rotates both vectors by ``ecm06``, takes
h = r x v and the node longitude atan2(hx, -hy). None of the engine's node code is called for
the reference. Frame velocity terms are left out on both sides, as the engine documents,
because the node of the inertial orbit plane is what is wanted.

Instants: TT drawn uniformly over 1900-01-01 to 2100-12-31 with a seeded generator; TDB is
TT plus ERFA ``dtdb`` at the geocentre, and both sides read the kernel at that TDB.

Mean node. The engine says it evaluates the Meeus chapter 47 polynomial. Its coefficients
are not those of Meeus (2nd edition, 1998) eq. 47.7, so the row reports the engine against
the cited Meeus polynomial (the target), against its own coefficient set re-evaluated here
(an implementation check), and the difference curve between the two polynomials.

Control: +0.2 arcsec added to the engine's true node must turn the true-node target FAIL.
Exit codes: 0 every target PASS, 1 a target FAIL, 2 VOID (kernel missing or not the pinned
DE440).
"""

from __future__ import annotations

import argparse
import math
import sys
from pathlib import Path
from typing import Any, Sequence

import erfa
import numpy as np

from bench.harness import stats as T
from bench.harness.scorecard import render

SCHEMA = "bench-row-nodes-v0"
SEED = 20261006
COUNT = 2000
JD_TT_START = 2415020.5  # 1900-01-01 00:00 TT
JD_TT_END = 2488069.5  # 2100-12-31 00:00 TT
J2000 = 2451545.0
CENTURY = 36525.0
TRUE_NODE_THRESHOLD_ARCSEC = 0.1
MEAN_NODE_TOLERANCE_ARCSEC = 0.001
CONTROL_OFFSET_ARCSEC = 0.2
EXIT_PASS, EXIT_FAIL, EXIT_VOID = 0, 1, 2

# (c0, c1, c2, 1/c3 divisor, 1/c4 divisor) for
# c0 + c1 T + c2 T^2 + T^3 / d3 - T^4 / d4, degrees, T in Julian centuries of TT from J2000.
MEEUS_2ED_47_7 = (125.0445479, -1934.1362891, 0.0020754, 467441.0, 60616000.0)
ENGINE_COEFFICIENTS = (125.04455501, -1934.1361849, 0.0020762, 467410.0, 60616000.0)


def polynomial(coefficients: Sequence[float], jd_tt: np.ndarray | float) -> np.ndarray:
    c0, c1, c2, d3, d4 = coefficients
    t = (np.asarray(jd_tt, dtype=np.float64) - J2000) / CENTURY
    return np.mod(c0 + c1 * t + c2 * t**2 + t**3 / d3 - t**4 / d4, 360.0)


def wrapped_diff_arcsec(a_deg: np.ndarray, b_deg: np.ndarray) -> np.ndarray:
    """Signed a - b in arcseconds, wrapped into [-648000, 648000)."""

    d = np.asarray(a_deg, dtype=np.float64) - np.asarray(b_deg, dtype=np.float64)
    return (np.mod(d + 180.0, 360.0) - 180.0) * 3600.0


def sample_tt(count: int = COUNT, seed: int = SEED) -> np.ndarray:
    rng = np.random.default_rng(seed)
    return np.sort(rng.uniform(JD_TT_START, JD_TT_END, size=count))


def tdb_from_tt(jd_tt: float) -> float:
    return jd_tt + float(erfa.dtdb(J2000, jd_tt - J2000, 0.0, 0.0, 0.0, 0.0)) / 86400.0


def reference_true_node(kernel: Path, jd_tt: np.ndarray) -> np.ndarray:
    """Independent osculating node: Skyfield state, ``ecm06`` rotation, h = r x v."""

    from skyfield.api import load, load_file

    ephemeris = load_file(str(kernel))
    try:
        ts = load.timescale(builtin=True)
        tdb = np.array([tdb_from_tt(float(j)) for j in jd_tt])
        whole = np.floor(tdb)
        t = ts.tdb_jd(whole, tdb - whole)
        state = (ephemeris["moon"] - ephemeris["earth"]).at(t)
        r = np.asarray(state.position.km, dtype=np.float64).T
        v = np.asarray(state.velocity.km_per_s, dtype=np.float64).T
    finally:
        ephemeris.close()
    out = np.empty(len(jd_tt))
    for i, jd in enumerate(jd_tt):
        m = np.asarray(erfa.ecm06(J2000, float(jd) - J2000), dtype=np.float64)
        h = np.cross(m @ r[i], m @ v[i])
        out[i] = math.degrees(math.atan2(h[0], -h[1])) % 360.0
    return out


def _engine(kernel: Path):
    from ephemeris_oss import Engine

    return Engine.load(kernels={"DE440": str(kernel)}, eop=None)


def engine_true_node(kernel: Path, jd_tt: np.ndarray) -> np.ndarray:
    from ephemeris_oss.engine.numerical_provider import TimeScaleState

    engine = _engine(kernel)
    try:
        provider = engine._provider
        out = np.empty(len(jd_tt))
        for i, jd in enumerate(jd_tt):
            tt = (J2000, float(jd) - J2000)
            tdb = (J2000, tdb_from_tt(float(jd)) - J2000)
            times = TimeScaleState(utc=tt, tt=tt, tdb=tdb)
            year = int(erfa.jd2cal(*tt)[0])
            out[i] = provider._osculating_lunar_node(times, year)
        return out
    finally:
        engine.close()


def public_api_spot_check(kernel: Path) -> dict[str, Any]:
    """``Engine.nodes(kind="true")`` must equal the provider path the row samples."""

    from datetime import datetime, timezone

    from ephemeris_oss.engine.numerical_provider import TimeScaleState

    engine = _engine(kernel)
    try:
        provider = engine._provider
        worst = 0.0
        instants = [datetime(year, 6, 15, 12, tzinfo=timezone.utc) for year in (1962, 1985, 2000, 2013, 2026)]
        for instant in instants:
            public = engine.nodes(instant, kind="true").value
            times = provider.utc_time_scales(instant)
            direct = provider._osculating_lunar_node(TimeScaleState(utc=times.utc, tt=times.tt, tdb=times.tdb),
                                                     instant.year)
            worst = max(worst, abs(float(wrapped_diff_arcsec(np.array([public]), np.array([direct]))[0])))
        return {"instants": len(instants), "max_abs_arcsec": worst}
    finally:
        engine.close()


def engine_mean_node(jd_tt: float) -> float:
    from ephemeris_oss.engine.conventions import mean_lunar_node_longitude_degrees

    return float(mean_lunar_node_longitude_degrees(jd_tt))


def true_node_target(diffs_arcsec: np.ndarray, seed: int = SEED) -> dict[str, Any]:
    absolute = np.abs(np.asarray(diffs_arcsec, dtype=np.float64))
    worst = float(absolute.max())
    return {
        "abs_diff_arcsec": T.summary(absolute, seed),
        "signed_diff_arcsec_median": float(np.median(diffs_arcsec)),
        "threshold_max_arcsec": TRUE_NODE_THRESHOLD_ARCSEC,
        "verdict": "PASS" if worst <= TRUE_NODE_THRESHOLD_ARCSEC else "FAIL",
    }


def polynomial_difference_curve() -> dict[str, Any]:
    """Meeus 2nd ed. eq. 47.7 minus the engine's coefficient set, in arcseconds."""

    jd = np.linspace(JD_TT_START, JD_TT_END, 2001)
    curve = wrapped_diff_arcsec(polynomial(MEEUS_2ED_47_7, jd), polynomial(ENGINE_COEFFICIENTS, jd))

    def at(jd_tt: float) -> float:
        return float(wrapped_diff_arcsec(polynomial(MEEUS_2ED_47_7, jd_tt), polynomial(ENGINE_COEFFICIENTS, jd_tt)))

    return {
        "at_1900_arcsec": at(JD_TT_START),
        "at_2000_arcsec": at(J2000),
        "at_2100_arcsec": at(2488069.5),
        "max_abs_arcsec_1900_2100": float(np.max(np.abs(curve))),
        "grid_points": int(jd.size),
    }


def build(kernel: Path, count: int = COUNT, seed: int = SEED, control_offset_arcsec: float = 0.0) -> dict[str, Any]:
    jd_tt = sample_tt(count, seed)
    ours = engine_true_node(kernel, jd_tt)
    if control_offset_arcsec:
        ours = np.mod(ours + control_offset_arcsec / 3600.0, 360.0)
    reference = reference_true_node(kernel, jd_tt)
    true_target = true_node_target(wrapped_diff_arcsec(ours, reference), seed)

    ours_mean = np.array([engine_mean_node(float(j)) for j in jd_tt])
    vs_meeus = np.abs(wrapped_diff_arcsec(ours_mean, polynomial(MEEUS_2ED_47_7, jd_tt)))
    vs_own = np.abs(wrapped_diff_arcsec(ours_mean, polynomial(ENGINE_COEFFICIENTS, jd_tt)))
    mean_target = {
        "cited": "Meeus, Astronomical Algorithms, 2nd ed. (1998), eq. 47.7",
        "abs_diff_vs_cited_arcsec": T.summary(vs_meeus, seed),
        "abs_diff_vs_own_coefficients_arcsec": T.summary(vs_own, seed),
        "tolerance_arcsec": MEAN_NODE_TOLERANCE_ARCSEC,
        "verdict": "PASS" if float(vs_meeus.max()) <= MEAN_NODE_TOLERANCE_ARCSEC else "FAIL",
        "own_coefficients_verdict": "PASS" if float(vs_own.max()) <= MEAN_NODE_TOLERANCE_ARCSEC else "FAIL",
        "coefficients": {"engine": list(ENGINE_COEFFICIENTS), "meeus_2ed_47_7": list(MEEUS_2ED_47_7),
                         "form": "c0 + c1*T + c2*T^2 + T^3/d3 - T^4/d4 degrees, T Julian centuries TT from J2000"},
        "difference_curve_meeus_minus_engine": polynomial_difference_curve(),
    }
    from ephemeris_oss.engine.kernel_registry import DE440_SHA256

    return {
        "schema": SCHEMA,
        "seed": seed,
        "count": int(count),
        "span_tt": ["1900-01-01", "2100-12-31"],
        "kernel_sha256": DE440_SHA256.lower(),
        "frame": "mean ecliptic and equinox of date, ERFA ecm06 (IAU 2006), geometric geocentric, no nutation",
        "control_offset_arcsec": control_offset_arcsec,
        "public_api_spot_check": public_api_spot_check(kernel),
        "targets": {"true_node": true_target, "mean_node": mean_target},
    }


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--kernel", required=True, type=Path)
    parser.add_argument("--out", required=True, type=Path)
    parser.add_argument("--count", type=int, default=COUNT)
    parser.add_argument("--control-offset-arcsec", type=float, default=0.0)
    args = parser.parse_args(argv)

    from bench.harness.scorecard import file_sha256
    from ephemeris_oss.engine.kernel_registry import DE440_SHA256

    if not args.kernel.is_file() or file_sha256(args.kernel) != DE440_SHA256.lower():
        print("VOID: kernel missing or not the pinned DE440", file=sys.stderr)
        return EXIT_VOID
    card = build(args.kernel, args.count, control_offset_arcsec=args.control_offset_arcsec)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_bytes(render(card))
    verdicts = {name: target["verdict"] for name, target in card["targets"].items()}
    print(" ".join(f"{name}={verdict}" for name, verdict in sorted(verdicts.items())))
    return EXIT_PASS if all(v == "PASS" for v in verdicts.values()) else EXIT_FAIL


if __name__ == "__main__":
    raise SystemExit(main())
