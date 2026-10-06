"""Controls that must fire on every run, or the run is VOID.

* ``offset_body``: rotates one body's directions by an exact angle (the +1 arcsec Moon control).
* ``self_comparison``: an engine against itself must give exactly zero on both statistics.
  This is the in-process stand-in for "Swiss against Swiss"; the copyleft comparator runs
  the same check in its own process.
* ``missing_kernel_is_void``: the scorecard must exit VOID, never pass, with no kernel.
"""

from __future__ import annotations

import math
from pathlib import Path
from typing import Mapping, Sequence

import numpy as np

ARCSEC = math.pi / (180.0 * 3600.0)


def offset_body(vectors: Mapping[str, Sequence[float]], rows: Sequence[Mapping[str, str]],
                body: str, arcsec: float) -> dict[str, tuple[float, float, float]]:
    """Copy of ``vectors`` with every ``body`` direction rotated by ``arcsec`` (Rodrigues)."""

    targets = {row["id"] for row in rows if row["body"] == body}
    angle = arcsec * ARCSEC
    out = {}
    for key, value in vectors.items():
        v = np.asarray(value, dtype=np.float64)
        if key in targets:
            # Rotate about an axis perpendicular to v, so the whole angle shows as separation.
            helper = np.array([1.0, 0.0, 0.0]) if abs(v[0]) < 0.9 else np.array([0.0, 1.0, 0.0])
            axis = np.cross(v, helper)
            axis /= np.linalg.norm(axis)
            v = v * math.cos(angle) + np.cross(axis, v) * math.sin(angle) + axis * np.dot(axis, v) * (1 - math.cos(angle))
        out[key] = (float(v[0]), float(v[1]), float(v[2]))
    return out


def self_comparison(rows: Sequence[Mapping[str, str]], kernel_path: str | Path) -> dict:
    """Run our engine twice on the same rows; both statistics must be exactly 0."""

    from . import engines as E
    from . import stats as T

    first = E.ours(rows, kernel_path)
    second = E.ours(rows, kernel_path)
    ids = [row["id"] for row in rows]
    a = np.array([first[i] for i in ids])
    b = np.array([second[i] for i in ids])
    seps = T.separations_arcsec(a, b)
    ecl = T.ecliptic_component_diffs_arcsec(a, b, [float(row["jd_tdb"]) for row in rows])
    return {"n": len(ids), "max_separation_arcsec": float(seps.max()),
            "max_ecliptic_component_arcsec": float(ecl.max())}


def missing_kernel_is_void(samples_path: str | Path, work_dir: str | Path) -> bool:
    from . import scorecard as C

    work = Path(work_dir)
    code = C.main(["--samples", str(samples_path), "--kernel", str(work / "absent-de440.bsp"),
                   "--out", str(work / "control-missing-kernel.json")])
    return code == C.EXIT_VOID


def moon_offset_fails(samples_path: str | Path, kernel_path: str | Path, work_dir: str | Path,
                      threshold_arcsec: float = 0.1) -> bool:
    """+1 arcsec on our Moon must turn a passing fidelity threshold into FAIL."""

    from . import scorecard as C

    work = Path(work_dir)
    common = ["--samples", str(samples_path), "--kernel", str(kernel_path),
              "--fail-above-arcsec", repr(threshold_arcsec)]
    clean = C.main([*common, "--out", str(work / "control-clean.json")])
    dirty = C.main([*common, "--out", str(work / "control-moon.json"), "--control-moon-offset-arcsec", "1.0"])
    return clean == C.EXIT_PASS and dirty == C.EXIT_FAIL


def run_all(samples_path: str | Path, kernel_path: str | Path, work_dir: str | Path) -> dict[str, bool]:
    from .samples import read_samples

    result = self_comparison(read_samples(samples_path), kernel_path)
    return {
        "missing_kernel_void": missing_kernel_is_void(samples_path, work_dir),
        "moon_offset_fails": moon_offset_fails(samples_path, kernel_path, work_dir),
        "self_zero": result["max_separation_arcsec"] == 0.0 and result["max_ecliptic_component_arcsec"] == 0.0,
    }
