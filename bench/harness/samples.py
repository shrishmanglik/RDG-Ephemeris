"""Seeded sample instants, one stratum per body x era x mode, written as JSON Lines.

Each instant is drawn as a whole number of nanodays (1e-9 day) inside its era, so the
decimal string with 9 places is exact and every engine and Horizons receive the same
instant. Each stratum has its own random stream, keyed by seed and stratum name, so
adding a body or an era never moves the instants of another stratum.
"""

from __future__ import annotations

import hashlib
import json
from decimal import Decimal
from pathlib import Path
from typing import Iterable, Sequence

import erfa
import numpy as np

BODIES: tuple[str, ...] = (
    "sun", "moon", "mercury", "venus", "mars", "jupiter", "saturn", "uranus", "neptune", "pluto",
)
MODES: tuple[str, ...] = ("geometric", "astrometric", "apparent-aberrated", "apparent")


def _jan1(year: int) -> float:
    """JD of 0h on 1 January of ``year`` (proleptic Gregorian, read as TDB)."""

    base, offset = erfa.cal2jd(year, 1, 1)
    return float(base + offset)


# Half-open [start, end): E1 is 1900-01-01 up to 2026-01-01, so the labelled year ranges
# tile without overlap. All four lie inside DE440 (JD 2287184.5 to 2688976.5).
ERAS: dict[str, tuple[float, float]] = {
    "E1": (_jan1(1900), _jan1(2026)),
    "E2": (_jan1(2026), _jan1(2041)),
    "E3": (_jan1(1550), _jan1(1900)),
    "E4": (_jan1(2041), _jan1(2650)),
}

NANODAYS = 10**9


def _stream(seed: int, body: str, era: str, mode: str) -> np.random.Generator:
    key = hashlib.sha256(f"{body}|{era}|{mode}".encode("ascii")).digest()
    words = [int.from_bytes(key[i:i + 4], "big") for i in range(0, 16, 4)]
    return np.random.default_rng(np.random.SeedSequence([int(seed), *words]))


def _check(names: Iterable[str], allowed: Iterable[str], kind: str) -> list[str]:
    names = list(names)
    unknown = sorted(set(names) - set(allowed))
    if unknown:
        raise ValueError(f"unknown {kind}: {unknown}")
    return names


def make_samples(
    seed: int, n_per_stratum: int, bodies: Sequence[str], eras: Sequence[str], modes: Sequence[str]
) -> list[dict[str, str]]:
    """Rows ``{"id", "body", "era", "mode", "jd_tdb"}`` in body, era, mode, index order."""

    bodies = _check(bodies, BODIES, "bodies")
    eras = _check(eras, ERAS, "eras")
    modes = _check(modes, MODES, "modes")
    if n_per_stratum < 1:
        raise ValueError("n_per_stratum must be at least 1")
    rows: list[dict[str, str]] = []
    for body in bodies:
        for era in eras:
            start, end = ERAS[era]
            start_ns = int(Decimal(repr(start)) * NANODAYS)
            span_ns = int(Decimal(repr(end)) * NANODAYS) - start_ns
            for mode in modes:
                offsets = _stream(seed, body, era, mode).integers(0, span_ns, size=n_per_stratum)
                for index, offset in enumerate(offsets):
                    total = start_ns + int(offset)
                    rows.append({
                        "id": f"{body}-{era}-{mode}-{index:05d}",
                        "body": body,
                        "era": era,
                        "mode": mode,
                        "jd_tdb": f"{total // NANODAYS}.{total % NANODAYS:09d}",
                    })
    return rows


def split_jd(jd_tdb: str) -> tuple[float, float]:
    """The exact decimal JD as (whole day, fraction), for two-part time arguments."""

    whole, _, fraction = jd_tdb.partition(".")
    return float(int(whole)), float(Decimal("0." + (fraction or "0")))


def write_samples(rows: Sequence[dict[str, str]], path: str | Path) -> None:
    lines = [json.dumps(row, sort_keys=True, separators=(",", ":")) + "\n" for row in rows]
    Path(path).write_bytes("".join(lines).encode("utf-8"))


def read_samples(path: str | Path) -> list[dict[str, str]]:
    text = Path(path).read_bytes().decode("utf-8")
    return [json.loads(line) for line in text.splitlines() if line.strip()]


def sample_sha256(path: str | Path) -> str:
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()
