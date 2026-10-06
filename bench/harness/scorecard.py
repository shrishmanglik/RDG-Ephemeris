"""Scorecard CLI: every engine against T2, per stratum and per mode, as byte-stable JSON.

    python -m bench.harness.scorecard --samples S --kernel K --out scorecard.json [--engines ours,t2]

The output has sorted keys, floats rounded to 1e-12 arcsec and written as Python's repr,
and nothing that varies between runs: no timestamps, no host, no paths, no timings
(those belong in ``speed-*.json``). Exit codes: 0 PASS, 1 FAIL (a fidelity threshold was
exceeded), 2 VOID (the kernel is missing or its SHA-256 is not the pinned DE440 hash).
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import sys
from collections import defaultdict
from importlib import metadata
from pathlib import Path
from typing import Any, Mapping, Sequence

import numpy as np

from ephemeris_oss._version import __version__ as PACKAGE_VERSION
from ephemeris_oss.engine.kernel_registry import DE440_SHA256

from . import engines as E
from . import samples as S
from . import stats as T
from .controls import offset_body

EXIT_PASS, EXIT_FAIL, EXIT_VOID = 0, 1, 2
SCHEMA = "bench-scorecard-v0"
TRUTH = "t2"
STATISTIC_NAMES = ("separation_arcsec", "ecliptic_max_component_arcsec")
_DIGITS = 12


def _clean(value: Any) -> Any:
    if isinstance(value, bool) or value is None or isinstance(value, (int, str)):
        return value
    if isinstance(value, float):
        if not math.isfinite(value):
            raise ValueError("scorecard values must be finite")
        rounded = round(value, _DIGITS)
        return 0.0 if rounded == 0 else rounded
    if isinstance(value, Mapping):
        return {str(k): _clean(v) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return [_clean(v) for v in value]
    raise TypeError(f"cannot render {type(value).__name__}")


def render(card: Mapping[str, Any]) -> bytes:
    text = json.dumps(_clean(card), sort_keys=True, separators=(",", ":"), allow_nan=False)
    return (text + "\n").encode("utf-8")


def file_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def _stream_seed(seed: int, key: str) -> int:
    return int.from_bytes(hashlib.sha256(f"{seed}|{key}".encode("ascii")).digest()[:8], "big")


def _formatted(summary: Mapping[str, Any], floor: float | None) -> dict:
    out = {"n": summary["n"]}
    for name in T.STATISTICS:
        out[name] = T.tie(summary[name], floor)
        out.setdefault("ci95", {})[name] = [T.tie(v, floor) for v in summary["ci95"][name]]
    return out


def score_engine(rows: Sequence[Mapping[str, str]], result: Mapping[str, Sequence[float]],
                 truth: Mapping[str, Sequence[float]], seed: int,
                 floors: Mapping[str, float] | None) -> tuple[dict, dict]:
    """Per-stratum and per-mode summaries plus the raw per-stratum maxima for the verdict."""

    groups: dict[str, list[Mapping[str, str]]] = defaultdict(list)
    for row in rows:
        groups[f"{row['body']}|{row['era']}|{row['mode']}"].append(row)
        groups[f"mode:{row['mode']}"].append(row)
    strata, by_mode, raw_max = {}, {}, {}
    for key in sorted(groups):
        members = groups[key]
        ids = [row["id"] for row in members]
        a = np.array([truth[i] for i in ids])
        b = np.array([result[i] for i in ids])
        values = {
            "separation_arcsec": T.separations_arcsec(a, b),
            "ecliptic_max_component_arcsec": T.ecliptic_component_diffs_arcsec(
                a, b, [float(row["jd_tdb"]) for row in members]),
        }
        floor = None if floors is None else floors.get(members[0]["mode"])
        entry = {name: _formatted(T.summary(v, _stream_seed(seed, f"{key}|{name}")), floor)
                 for name, v in values.items()}
        if key.startswith("mode:"):
            by_mode[key[5:]] = entry
        else:
            strata[key] = entry
            raw_max[key] = float(values["separation_arcsec"].max())
    return {"strata": strata, "by_mode": by_mode}, raw_max


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="python -m bench.harness.scorecard", description=__doc__.splitlines()[0])
    parser.add_argument("--samples", required=True, type=Path)
    parser.add_argument("--kernel", required=True, type=Path)
    parser.add_argument("--out", required=True, type=Path)
    parser.add_argument("--engines", default="ours,t2", help="comma list; t2 is the truth and always runs")
    parser.add_argument("--seed", type=int, default=0, help="bootstrap seed, recorded in the card")
    parser.add_argument("--truth-floor", type=Path, help="JSON {mode: arcsec}; values below are ties")
    parser.add_argument("--fail-above-arcsec", type=float,
                        help="fidelity threshold: any stratum max separation above it makes the run FAIL")
    parser.add_argument("--control-moon-offset-arcsec", type=float, default=0.0,
                        help="control only: rotate our Moon by this angle before scoring")
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    parser = _parser()
    args = parser.parse_args(argv)
    names = [n.strip() for n in args.engines.split(",") if n.strip()]
    unknown = sorted(set(names) - set(E.ENGINES))
    if unknown:
        parser.error(f"unknown engines: {unknown}; known: {sorted(E.ENGINES)}")
    scored = [n for n in names if n != TRUTH]

    card: dict[str, Any] = {
        "schema": SCHEMA, "truth": TRUTH, "seed": args.seed, "package_version": PACKAGE_VERSION,
        "skyfield_version": metadata.version("skyfield"), "kernel_id": "DE440",
        "sample_sha256": S.sample_sha256(args.samples),
        "fidelity_threshold_arcsec": args.fail_above_arcsec,
    }
    if not args.kernel.is_file():
        return _finish(args.out, card, "VOID", f"kernel file {args.kernel.name} does not exist")
    kernel_sha = file_sha256(args.kernel)
    card["kernel_sha256"] = kernel_sha
    if kernel_sha != DE440_SHA256:
        return _finish(args.out, card, "VOID", f"kernel sha256 {kernel_sha} is not the pinned DE440 {DE440_SHA256}")

    rows = S.read_samples(args.samples)
    card["n_samples"] = len(rows)
    floors = None
    if args.truth_floor is not None:
        floors = {str(k): float(v) for k, v in json.loads(args.truth_floor.read_text(encoding="utf-8")).items()}
    card["truth_floor_arcsec"] = floors
    if args.control_moon_offset_arcsec:
        card["control_moon_offset_arcsec"] = args.control_moon_offset_arcsec

    truth = E.t2_skyfield(rows, args.kernel)
    card["engines"], failures = {}, []
    for name in scored:
        result = E.ENGINES[name](rows, args.kernel)
        if name == "ours" and args.control_moon_offset_arcsec:
            result = offset_body(result, rows, "moon", args.control_moon_offset_arcsec)
        card["engines"][name], raw_max = score_engine(rows, result, truth, args.seed, floors)
        if args.fail_above_arcsec is not None:
            failures += [f"{name}|{key}" for key, value in raw_max.items() if value > args.fail_above_arcsec]
    card["failures"] = sorted(failures)
    return _finish(args.out, card, "FAIL" if failures else "PASS")


def _finish(out: Path, card: dict, verdict: str, reason: str | None = None) -> int:
    card["verdict"] = verdict
    if reason is not None:
        card["void_reason"] = reason
    out.write_bytes(render(card))
    print(f"scorecard {verdict}" + (f": {reason}" if reason else ""), file=sys.stderr)
    return {"PASS": EXIT_PASS, "FAIL": EXIT_FAIL, "VOID": EXIT_VOID}[verdict]


if __name__ == "__main__":
    raise SystemExit(main())
