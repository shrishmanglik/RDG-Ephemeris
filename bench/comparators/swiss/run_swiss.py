"""Swiss Ephemeris comparator, run as its own process in its own virtual environment.

This directory is licensed under the GNU Affero General Public License v3 (see
LICENSE in this directory) because it links the pyswisseph binding. Nothing in
the package imports it; the harness reads only the results file it writes.

Reads a sample file (JSON Lines: id, body, mode, jd_tdb) and writes one JSON
line per sample: id, x, y, z (geocentric ICRS unit direction), retflags.
Modes: geometric = true position (no light time, aberration or deflection);
astrometric = light time only; apparent = light time, aberration, deflection.

``--ephemeris swieph`` uses the Swiss data files in ``--ephe-path`` and makes
the run VOID (exit 2) if any call falls back to the built-in Moshier model;
``--ephemeris jpl`` reads a JPL kernel through Swiss; ``--ephemeris moshier``
uses the analytical model deliberately.
"""

from __future__ import annotations

import argparse
import json
import math
import sys

import erfa
import swisseph as swe

BODIES = {"sun": 0, "moon": 1, "mercury": 2, "venus": 3, "mars": 4, "jupiter": 5, "saturn": 6,
          "uranus": 7, "neptune": 8, "pluto": 9}
MODES = {
    "geometric": swe.FLG_TRUEPOS | swe.FLG_NOABERR | swe.FLG_NOGDEFL,
    "astrometric": swe.FLG_NOABERR | swe.FLG_NOGDEFL,
    "apparent": 0,
}
BASE = swe.FLG_J2000 | swe.FLG_ICRS | swe.FLG_EQUATORIAL | swe.FLG_XYZ


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--samples", required=True)
    parser.add_argument("--out", required=True)
    parser.add_argument("--ephemeris", choices=("swieph", "jpl", "moshier"), default="swieph")
    parser.add_argument("--ephe-path", default="")
    parser.add_argument("--jpl-file", default="")
    args = parser.parse_args(argv)
    source = {"swieph": swe.FLG_SWIEPH, "jpl": swe.FLG_JPLEPH, "moshier": swe.FLG_MOSEPH}[args.ephemeris]
    if args.ephe_path:
        swe.set_ephe_path(args.ephe_path)
    if args.ephemeris == "jpl":
        swe.set_jpl_file(args.jpl_file)
    rows = []
    with open(args.samples, encoding="utf-8") as handle:
        for line in handle:
            sample = json.loads(line)
            jd = float(sample["jd_tdb"])
            # Swiss takes TT; convert from TDB with ERFA's TDB-TT model at the geocentre.
            whole = math.floor(jd)
            dtr = float(erfa.dtdb(whole, jd - whole, 0.0, 0.0, 0.0, 0.0))
            tt1, tt2 = erfa.tdbtt(whole, jd - whole, dtr)
            flags = BASE | source | MODES[sample["mode"]]
            xx, retflags = swe.calc(float(tt1) + float(tt2), BODIES[sample["body"]], flags)
            if source != swe.FLG_MOSEPH and not retflags & source:
                print(f"VOID: {sample['id']} fell back from the requested ephemeris (retflags {retflags})",
                      file=sys.stderr)
                return 2
            norm = math.sqrt(xx[0] ** 2 + xx[1] ** 2 + xx[2] ** 2)
            rows.append({"id": sample["id"], "x": xx[0] / norm, "y": xx[1] / norm, "z": xx[2] / norm,
                         "distance_au": norm, "retflags": retflags})
    with open(args.out, "w", encoding="utf-8", newline="\n") as out:
        for row in rows:
            out.write(json.dumps(row, sort_keys=True) + "\n")
    print(f"swiss {swe.version} {args.ephemeris}: {len(rows)} rows")
    return 0


if __name__ == "__main__":
    sys.exit(main())
