"""Benchmark row: Delta-T (TT - UT1) for past dates against measured Earth rotation.

    python -m bench.rows.delta_t --eop finals2000A.all --out bench/data/rows/delta_t.json

Measured truth, 1973-2025. The IERS finals2000A file (fetched once with
``ephemeris_oss.kernels.fetch_eop``; it changes daily, so its SHA-256 is recorded in the
output) is read by this module's own fixed-width parser, not the engine's. For each daily
record from 1973-01-01 to 2025-12-31:

    TT - UT1 = 32.184 s + (TAI - UTC from ERFA ``dat`` at that date) - (UT1 - UTC)

where UT1 - UTC is the Bulletin B (final) value when the record carries one and the
Bulletin A value otherwise. The largest A minus B difference is reported as the spread
inside the truth itself.

What the engine gives for those dates is measured two ways:

* the EOP path, which is what a user gets with ``Engine.load(eop="auto")`` and the file in
  the cache: TT - UTC from the engine's own UTC time scales minus the engine's resolved
  UT1 - UTC. This is a consistency check of the engine's reader and interpolation, gated
  at 0.05 s;
* the fallback model ``ephemeris_oss.time.delta_t(decimal_year)`` (Espenak-Meeus
  polynomials), evaluated at the record's 0h UTC as year + (day of year - 1) / days in year.
  It is reported, not gated: it is what the engine falls back to, and the honest number
  matters more than a verdict.

Published table, 1900-1972. The model is compared with the USNO table of historic Delta-T
(half-yearly, with its stated error), retrieved on the date recorded below and committed
beside this row with its SHA-256. The Espenak-Meeus polynomials were fitted to tabulated
values of this kind, so this half checks the polynomials as implemented, not an
independent theory. From 1960 the engine itself uses UTC with the leap-second table rather
than this model. The USNO and IERS-derived series overlap in 1973.0-1984.5, and that
overlap is reported as a check on the truth derivation.

Control: +0.1 s added to the gated EOP-path values must turn the 1973-2025 target FAIL. The
offset goes on the gated path and not on the model because the model already fails 0.05 s
over this span, so offsetting it could not show the gate firing.
Exit codes: 0 PASS, 1 FAIL, 2 VOID (EOP file missing or not named finals2000A.all).
"""

from __future__ import annotations

import argparse
import hashlib
import sys
from datetime import date, datetime, timezone
from pathlib import Path
from typing import Any, Sequence

import erfa
import numpy as np

from bench.harness import stats as T
from bench.harness.scorecard import render

SCHEMA = "bench-row-delta-t-v0"
SEED = 20261006
TT_MINUS_TAI = 32.184
GATE_SECONDS = 0.05
CONTROL_OFFSET_SECONDS = 0.1
FIRST_DAY = date(1973, 1, 1)
LAST_DAY = date(2025, 12, 31)
IERS_URL = "https://datacenter.iers.org/data/latestVersion/finals.all.iau2000.txt"
USNO_URL = "https://maia.usno.navy.mil/ser7/historic_deltat.data"
USNO_RETRIEVED = "2026-10-06"
USNO_FILE = Path(__file__).resolve().parents[1] / "data" / "rows" / "usno-historic-deltat.data"
EXIT_PASS, EXIT_FAIL, EXIT_VOID = 0, 1, 2
MODEL_SEGMENTS = ((1973.0, 1986.0), (1986.0, 2005.0), (2005.0, 2026.0))


def _column(line: str, start: int, end: int) -> str:
    """One-based inclusive columns, as the finals2000A format document numbers them."""

    return line[start - 1:end].strip()


def read_finals(path: Path) -> dict[int, dict[str, float | None]]:
    """MJD -> {"a": Bulletin A UT1-UTC, "b": Bulletin B UT1-UTC or None}, observed rows only."""

    records: dict[int, dict[str, float | None]] = {}
    for line in path.read_text(encoding="ascii").splitlines():
        if len(line) < 68:
            continue
        mjd_text, flag, a_text = _column(line, 8, 15), _column(line, 58, 58), _column(line, 59, 68)
        if not mjd_text or not a_text or flag.upper() == "P":
            continue
        b_text = _column(line, 155, 165) if len(line) >= 165 else ""
        records[int(round(float(mjd_text)))] = {"a": float(a_text), "b": float(b_text) if b_text else None}
    return records


def _date_of(mjd: int) -> date:
    year, month, day, _ = erfa.jd2cal(2400000.5, float(mjd))
    return date(int(year), int(month), int(day))


def _mjd_of(day: date) -> int:
    return int(round(sum(erfa.cal2jd(day.year, day.month, day.day)) - 2400000.5))


def measured_series(records: dict[int, dict[str, float | None]]) -> tuple[np.ndarray, np.ndarray, float]:
    """Daily MJDs in the span, measured TT - UT1 there, and the largest |A - B|."""

    mjds, values, spread = [], [], 0.0
    for mjd in range(_mjd_of(FIRST_DAY), _mjd_of(LAST_DAY) + 1):
        record = records.get(mjd)
        if record is None:
            continue
        day = _date_of(mjd)
        tai_minus_utc = float(erfa.dat(day.year, day.month, day.day, 0.0))
        ut1_minus_utc = record["b"] if record["b"] is not None else record["a"]
        if record["b"] is not None:
            spread = max(spread, abs(float(record["a"]) - float(record["b"])))
        mjds.append(mjd)
        values.append(TT_MINUS_TAI + tai_minus_utc - float(ut1_minus_utc))
    return np.array(mjds), np.array(values), spread


def engine_eop_path(eop: Path, mjds: np.ndarray) -> np.ndarray:
    from ephemeris_oss import Engine

    from ephemeris_oss.engine.earth_orientation import IersFinals2000A
    digest = hashlib.sha256(eop.read_bytes()).hexdigest()
    snapshot = IersFinals2000A.from_file(eop, expected_sha256=digest, version=f"iers-finals-{digest}")
    engine = Engine.load(kernels={}, eop=snapshot)
    try:
        provider = engine._provider
        out = np.empty(len(mjds))
        for i, mjd in enumerate(mjds):
            day = _date_of(int(mjd))
            instant = datetime(day.year, day.month, day.day, tzinfo=timezone.utc)
            times = provider.utc_time_scales(instant)
            tt_minus_utc = ((times.tt[0] - times.utc[0]) + (times.tt[1] - times.utc[1])) * 86400.0
            out[i] = tt_minus_utc - provider._resolve_eop(instant).dut1_seconds
        return out
    finally:
        engine.close()


def decimal_year(day: date) -> float:
    days = 366 if (day.year % 4 == 0 and (day.year % 100 != 0 or day.year % 400 == 0)) else 365
    return day.year + (day.timetuple().tm_yday - 1) / days


def model(year: float) -> float:
    from ephemeris_oss.time import delta_t

    return float(delta_t(year).seconds)


def gated_target(errors: np.ndarray, seed: int = SEED) -> dict[str, Any]:
    absolute = np.abs(np.asarray(errors, dtype=np.float64))
    return {"abs_error_s": T.summary(absolute, seed), "gate_max_s": GATE_SECONDS,
            "verdict": "PASS" if float(absolute.max()) <= GATE_SECONDS else "FAIL"}


def read_usno(path: Path = USNO_FILE) -> list[tuple[float, float, float]]:
    rows = []
    for line in path.read_text(encoding="ascii").splitlines():
        parts = line.split()
        try:
            rows.append((float(parts[0]), float(parts[1]), float(parts[2])))
        except (IndexError, ValueError):
            continue
    return rows


def _mjd_of_decimal_year(year: float) -> float:
    return 51544.5 + (year - 2000.0) * 365.25


def build(eop: Path, seed: int = SEED, control_offset_seconds: float = 0.0) -> dict[str, Any]:
    records = read_finals(eop)
    mjds, measured, spread = measured_series(records)
    days = [_date_of(int(m)) for m in mjds]

    eop_path = engine_eop_path(eop, mjds) + control_offset_seconds
    eop_target = gated_target(eop_path - measured, seed)

    years = np.array([decimal_year(d) for d in days])
    model_values = np.array([model(y) for y in years])
    model_error = model_values - measured
    segments = []
    for low, high in MODEL_SEGMENTS:
        mask = (years >= low) & (years < high)
        segments.append({"span": [low, high], "n": int(mask.sum()),
                         "max_abs_error_s": float(np.abs(model_error[mask]).max()),
                         "signed_error_at_end_s": float(model_error[mask][-1])})
    model_target = {
        "abs_error_s": T.summary(np.abs(model_error), seed),
        "signed_error_s_median": float(np.median(model_error)),
        "segments": segments,
        "gate_max_s": GATE_SECONDS,
        "verdict": "PASS" if float(np.abs(model_error).max()) <= GATE_SECONDS else "FAIL",
        "gated": False,
    }

    usno = read_usno()
    early = [(y, v, e) for y, v, e in usno if 1900.0 <= y <= 1972.5]
    early_error = np.array([model(y) - v for y, v, _ in early])
    # Some epochs print a stated error of zero at the table's precision; they get no ratio.
    early_sigma = np.array([abs(model(y) - v) / e for y, v, e in early if e > 0])
    overlap = [(y, v) for y, v, _ in usno if 1973.0 <= y <= 1984.5]
    overlap_diff = [v - float(np.interp(_mjd_of_decimal_year(y), mjds, measured)) for y, v in overlap]

    return {
        "schema": SCHEMA,
        "seed": seed,
        "control_offset_seconds": control_offset_seconds,
        "truth_1973_2025": {
            "source": IERS_URL,
            "file_sha256": hashlib.sha256(eop.read_bytes()).hexdigest(),
            "n_days": int(mjds.size),
            "first_day": days[0].isoformat(),
            "last_day": days[-1].isoformat(),
            "formula": "32.184 + ERFA dat - UT1_UTC (Bulletin B when present, else Bulletin A)",
            "max_abs_bulletin_a_minus_b_s": spread,
        },
        "targets": {
            "eop_path_1973_2025": eop_target,
            "model_1973_2025": model_target,
            "model_1900_1972_vs_usno": {
                "source": USNO_URL,
                "retrieved": USNO_RETRIEVED,
                "file_sha256": hashlib.sha256(USNO_FILE.read_bytes()).hexdigest(),
                "n_epochs": len(early),
                "abs_error_s": T.summary(np.abs(early_error), seed),
                "signed_error_s_median": float(np.median(early_error)),
                "max_error_over_stated_sigma": float(early_sigma.max()),
                "n_epochs_with_zero_stated_error": len(early) - int(early_sigma.size),
                "gated": False,
            },
        },
        "truth_cross_check_usno_minus_iers_1973_1984": {
            "n_epochs": len(overlap),
            "max_abs_s": float(np.max(np.abs(overlap_diff))),
        },
    }


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--eop", required=True, type=Path)
    parser.add_argument("--out", required=True, type=Path)
    parser.add_argument("--control-offset-seconds", type=float, default=0.0)
    args = parser.parse_args(argv)
    if not args.eop.is_file() or args.eop.name != "finals2000A.all":
        print("VOID: EOP file missing or not named finals2000A.all", file=sys.stderr)
        return EXIT_VOID
    card = build(args.eop, control_offset_seconds=args.control_offset_seconds)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_bytes(render(card))
    verdict = card["targets"]["eop_path_1973_2025"]["verdict"]
    print(f"eop_path_1973_2025={verdict} model_1973_2025={card['targets']['model_1973_2025']['verdict']} (not gated)")
    return EXIT_PASS if verdict == "PASS" else EXIT_FAIL


if __name__ == "__main__":
    raise SystemExit(main())
