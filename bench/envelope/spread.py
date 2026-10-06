"""Uncertainty envelope feasibility: how far independent planetary ephemerides disagree, per body, per instant.

Run:
    python -m bench.envelope.spread --kernel de440=<de440.bsp> --kernel de442=<de442.bsp> \
        --kernel inpop21a=<inpop21a_TDB_m100_p100_spice.bsp> --out bench/data/envelope/spread.json

Every kernel is read through jplephem only. The geocentre is built per kernel from that kernel's own segments by
walking each target's centre chain down to the solar system barycentre (0), because the files do not share one layout:
the DE files store Earth and Moon relative to the Earth-Moon barycentre (3), while INPOP21a stores Earth relative to 0
and the Moon relative to Earth (399). Mixing one kernel's Earth with another's barycentre would measure the mix, not
the ephemeris.

Directions are geometric (no light time, no aberration), ICRF, geocentric. Mars, Jupiter and Saturn are system
barycentres (NAIF 4, 5, 6), the only ids all three files carry, which matches the bench's documented choice.

Every kernel passed must be in TDB. The INPOP SPICE file carries no comment area, so its scale is taken from its
published file name and README (the TCB variant ships under a different name); a TCB file mixed in here would show
up in the sanity block's geocentric Sun offset as hundreds of km or more.
"""

from __future__ import annotations

import argparse
import itertools
import json
import math
from pathlib import Path

import numpy as np
from jplephem.spk import SPK

SEED = 20261006
N_INSTANTS = 200
# 1950-01-01 00:00 TDB and 2050-01-01 00:00 TDB.
JD_START = 2433282.5
JD_END = 2469807.5
BODIES = {"sun": 10, "moon": 301, "mars": 4, "jupiter": 5, "saturn": 6}
EARTH = 399
ARCSEC_PER_RAD = 180.0 / math.pi * 3600.0


def sample_instants() -> list[str]:
    rng = np.random.default_rng(SEED)
    jds = np.sort(rng.uniform(JD_START, JD_END, N_INSTANTS))
    # Decimal strings with 9 decimals, the bench's instant contract, so a rerun feeds identical floats.
    return [f"{jd:.9f}" for jd in jds]


class Kernel:
    def __init__(self, name: str, path: Path):
        self.name = name
        self.spk = SPK.open(str(path))
        self.by_target: dict[int, object] = {}
        for seg in self.spk.segments:
            if seg.target in self.by_target:
                raise ValueError(f"{name}: target {seg.target} appears in more than one segment")
            self.by_target[seg.target] = seg

    def chain(self, target: int) -> list[tuple[int, int]]:
        links = []
        while target != 0:
            seg = self.by_target.get(target)
            if seg is None:
                raise KeyError(f"{self.name}: no segment reaches target {target}")
            links.append((seg.center, seg.target))
            target = seg.center
        return links

    def ssb(self, target: int, jd: float) -> np.ndarray:
        pos = np.zeros(3)
        t = target
        while t != 0:
            seg = self.by_target[t]
            pos = pos + seg.compute(jd)
            t = seg.center
        return pos

    def geocentric(self, body: int, jd: float) -> np.ndarray:
        return self.ssb(body, jd) - self.ssb(EARTH, jd)


def separation_arcsec(a: np.ndarray, b: np.ndarray) -> float:
    # atan2 of cross and dot stays accurate at milliarcsecond separations where acos does not.
    return math.atan2(np.linalg.norm(np.cross(a, b)), float(np.dot(a, b))) * ARCSEC_PER_RAD


def percentile(values: list[float], q: float) -> float:
    return float(np.percentile(np.asarray(values), q))


def r(x: float, nd: int = 6) -> float:
    return float(round(x, nd))


def run(kernels: list[Kernel]) -> dict:
    instants = sample_instants()
    names = [k.name for k in kernels]
    pairs = list(itertools.combinations(names, 2))
    pair_key = {p: f"{p[0]}|{p[1]}" for p in pairs}
    out_bodies = {}
    for body, naif in BODIES.items():
        max_spread = []
        pair_values = {pair_key[p]: [] for p in pairs}
        dominant = {pair_key[p]: 0 for p in pairs}
        for jd_s in instants:
            jd = float(jd_s)
            vecs = {k.name: k.geocentric(naif, jd) for k in kernels}
            seps = {pair_key[p]: separation_arcsec(vecs[p[0]], vecs[p[1]]) for p in pairs}
            for key, v in seps.items():
                pair_values[key].append(v)
            top = max(seps, key=lambda key: (seps[key], key))
            dominant[top] += 1
            max_spread.append(seps[top])
        out_bodies[body] = {
            "naif_id": naif,
            "max_pairwise_spread_arcsec": {
                "median": r(percentile(max_spread, 50)),
                "p95": r(percentile(max_spread, 95)),
                "max": r(max(max_spread)),
            },
            "pairwise_median_arcsec": {k: r(percentile(v, 50)) for k, v in pair_values.items()},
            "pairwise_max_arcsec": {k: r(max(v)) for k, v in pair_values.items()},
            "dominant_pair_counts": dominant,
            "dominant_pair": max(dominant, key=lambda key: (dominant[key], key)),
        }
    # Sanity, in km. The geocentric Sun vector does not depend on where each file puts the barycentre, so a unit or
    # time-scale mismatch (km vs au, TDB vs TCB) would show there as hundreds to thousands of km. Earth's offset from
    # the barycentre is reported beside it because files with different asteroid and TNO mass models place the
    # barycentre differently; that offset cancels in every geocentric direction above.
    sanity = {}
    for a, b in pairs:
        ka, kb = kernels[names.index(a)], kernels[names.index(b)]
        d_ssb = [float(np.linalg.norm(ka.ssb(EARTH, float(j)) - kb.ssb(EARTH, float(j)))) for j in instants]
        d_sun = [float(np.linalg.norm(ka.geocentric(10, float(j)) - kb.geocentric(10, float(j)))) for j in instants]
        sanity[pair_key[(a, b)]] = {
            "earth_ssb_offset_km_median": r(percentile(d_ssb, 50)),
            "earth_ssb_offset_km_max": r(max(d_ssb)),
            "geocentric_sun_offset_km_median": r(percentile(d_sun, 50)),
            "geocentric_sun_offset_km_max": r(max(d_sun)),
        }
    return {
        "method": {
            "seed": SEED,
            "n_instants": N_INSTANTS,
            "jd_tdb_range": [JD_START, JD_END],
            "time_scale": "TDB",
            "mode": "geometric geocentric direction, ICRF",
            "geocentre": "per kernel, each target's centre chain walked to the solar system barycentre",
            "spread": "per instant, the largest pairwise angular separation across all kernels",
            "planets": "mars, jupiter, saturn as system barycentres (NAIF 4, 5, 6)",
        },
        "kernels": {k.name: {"chains": {b: k.chain(n) for b, n in [*BODIES.items(), ("earth", EARTH)]}} for k in kernels},
        "instants_first_last": [instants[0], instants[-1]],
        "bodies": out_bodies,
        "sanity": sanity,
    }


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--kernel", action="append", required=True, help="name=path, at least two")
    ap.add_argument("--out", required=True)
    args = ap.parse_args(argv)
    kernels = []
    for spec in args.kernel:
        name, _, path = spec.partition("=")
        kernels.append(Kernel(name, Path(path)))
    if len(kernels) < 2:
        ap.error("need at least two kernels")
    result = run(kernels)
    Path(args.out).parent.mkdir(parents=True, exist_ok=True)
    with open(args.out, "w", encoding="utf-8", newline="\n") as fh:
        json.dump(result, fh, sort_keys=True, indent=2)
        fh.write("\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
