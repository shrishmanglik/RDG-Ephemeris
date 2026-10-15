"""Self-contained compact Chebyshev polynomial ephemeris kernel derived from JPL DE440.

This module provides ``CompactChebyshevKernel`` and ``CompactChebyshevSegment``,
implementing the exact segment interface expected by ``_SpkGraph`` in
``ephemeris_oss.engine.numerical_provider`` without requiring an external
114 MB ``de440.bsp`` download at runtime.
"""

from __future__ import annotations

import hashlib
import json
import struct
import threading
import zlib
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import numpy as np

from .engine.contracts import AstronomyDataUnavailable
from .engine.kernel_registry import DE440_SHA256

COMPACT_KERNEL_ID = "COMPACT-DE440"
COMPACT_KERNEL_MODE = "compact-chebyshev-de440"
COMPACT_KERNEL_PATH = Path(__file__).resolve().parent / "data" / "de440_compact.bin.zlib"
COMPACT_START_JD = 2378432.5  # 1799-10-28 00:00 TDB
COMPACT_SPAN_DAYS = 110080.0  # 860 * 128 days
COMPACT_END_JD = COMPACT_START_JD + COMPACT_SPAN_DAYS  # 2101-03-20 00:00 TDB

# Earth-Moon mass ratio in DE440: r_{3->399} = -r_{3->301} / DE440_EMRAT to < 1e-12 km.
DE440_EMRAT = 81.30056822149722

MAGIC_HEADER = b"EOSS_COMPACT_DE440_V1\x00"

REQUIRED_SEGMENT_PAIRS: tuple[tuple[int, int], ...] = (
    (0, 3),
    (3, 399),
    (3, 301),
    (0, 10),
    (0, 1),
    (1, 199),
    (0, 2),
    (2, 299),
    (0, 4),
    (0, 5),
    (0, 6),
    (0, 7),
    (0, 8),
    (0, 9),
)

# (center, target, interval_days, chebyshev_degree, quantization_step_km)
PRIMARY_SEGMENT_SPECS: tuple[tuple[int, int, float, int, float], ...] = (
    (3, 301, 8.0, 12, 2.0**-6),   # Moon wrt EMB
    (0, 1, 16.0, 11, 2.0**-2),    # Mercury Barycenter wrt SSB
    (0, 2, 32.0, 10, 2.0**-2),    # Venus Barycenter wrt SSB
    (0, 3, 32.0, 11, 2.0**-2),    # Earth-Moon Barycenter wrt SSB
    (0, 10, 32.0, 8, 2.0**-3),    # Sun wrt SSB
    (0, 4, 64.0, 10, 2.0**-2),    # Mars Barycenter wrt SSB
    (0, 5, 128.0, 8, 2.0**-1),    # Jupiter Barycenter wrt SSB
    (0, 6, 128.0, 7, 1.0),        # Saturn Barycenter wrt SSB
    (0, 7, 128.0, 6, 1.0),        # Uranus Barycenter wrt SSB
    (0, 8, 128.0, 6, 1.0),        # Neptune Barycenter wrt SSB
    (0, 9, 128.0, 6, 1.0),        # Pluto Barycenter wrt SSB
)

# Pinned SHA-256 of src/ephemeris_oss/data/de440_compact.bin.zlib
COMPACT_KERNEL_SHA256 = "ed25b159561a0471f6dbc79e54de9df938a1932175100c35a5a880344d9b9169"


@dataclass(frozen=True)
class CompactChebyshevSegment:
    """Chebyshev polynomial segment compatible with jplephem.spk.Segment."""

    center: int
    target: int
    start_jd: float
    end_jd: float
    intlen_days: float
    # Shape: (degree, 3, n_intervals), ordered from highest degree (m = degree - 1)
    # down to constant term (m = 0), matching jplephem Clenshaw layout.
    coefficients_rev: np.ndarray

    def compute(self, tdb: float | np.ndarray, tdb2: float | np.ndarray = 0.0) -> np.ndarray:
        pos, _vel = self.compute_and_differentiate(tdb, tdb2)
        return pos

    def compute_and_differentiate(
        self, tdb: float | np.ndarray, tdb2: float | np.ndarray = 0.0
    ) -> tuple[np.ndarray, np.ndarray]:
        scalar = not getattr(tdb, "shape", 0) and not getattr(tdb2, "shape", 0)
        t1 = np.asarray((tdb,) if scalar else tdb, dtype=np.float64)
        t2 = np.asarray(tdb2, dtype=np.float64)

        intlen = self.intlen_days
        n_intervals = self.coefficients_rev.shape[2]

        index1, offset1 = np.divmod(t1 - self.start_jd, intlen)
        index2, offset2 = np.divmod(t2, intlen)
        index3, offset = np.divmod(offset1 + offset2, intlen)
        index = (index1 + index2 + index3).astype(np.intp)

        if np.any(index < 0) or np.any(index > n_intervals):
            raise AstronomyDataUnavailable(
                f"compact kernel segment ({self.center}, {self.target}) only covers "
                f"JD {self.start_jd} through {self.end_jd}"
            )

        omegas = index == n_intervals
        if np.any(omegas):
            index = index.copy()
            offset = offset.copy()
            index[omegas] -= 1
            offset[omegas] += intlen

        coeffs = self.coefficients_rev[:, :, index]  # (degree, 3, batch)

        s = 2.0 * offset / intlen - 1.0
        s2 = 2.0 * s

        w0: float | np.ndarray = 0.0
        w1: float | np.ndarray = 0.0
        wlist: list[float | np.ndarray] = []

        for coefficient in coeffs[:-1]:
            w2 = w1
            w1 = w0
            w0 = coefficient + (s2 * w1 - w2)
            wlist.append(w1)

        position = coeffs[-1] + (s * w0 - w1)

        dw0: float | np.ndarray = 0.0
        dw1: float | np.ndarray = 0.0
        for w1_val in wlist:
            dw2 = dw1
            dw1 = dw0
            dw0 = 2.0 * w1_val + dw1 * s2 - dw2

        velocity = (w0 + s * dw0 - dw1) * (2.0 / intlen)

        if scalar:
            return position[:, 0], velocity[:, 0]
        return position, velocity


@dataclass(frozen=True)
class ZeroOffsetSegment:
    """Zero-offset segment for body centers identical to their system barycenter in DE440."""

    center: int
    target: int
    start_jd: float
    end_jd: float

    def compute(self, tdb: float | np.ndarray, tdb2: float | np.ndarray = 0.0) -> np.ndarray:
        pos, _vel = self.compute_and_differentiate(tdb, tdb2)
        return pos

    def compute_and_differentiate(
        self, tdb: float | np.ndarray, tdb2: float | np.ndarray = 0.0
    ) -> tuple[np.ndarray, np.ndarray]:
        scalar = not getattr(tdb, "shape", 0) and not getattr(tdb2, "shape", 0)
        jd = np.asarray(tdb, dtype=np.float64) + np.asarray(tdb2, dtype=np.float64)
        if np.any(jd < self.start_jd) or np.any(jd > self.end_jd):
            raise AstronomyDataUnavailable(
                f"compact kernel segment ({self.center}, {self.target}) only covers "
                f"JD {self.start_jd} through {self.end_jd}"
            )
        if scalar:
            return np.zeros(3, dtype=np.float64), np.zeros(3, dtype=np.float64)
        count = int(jd.shape[0])
        return np.zeros((3, count), dtype=np.float64), np.zeros((3, count), dtype=np.float64)


_CACHE_LOCK = threading.RLock()
_DECODED_SEGMENTS_CACHE: dict[tuple[str, str], tuple[Any, ...]] = {}


class CompactChebyshevKernel:
    """Self-contained compact Chebyshev DE440 kernel for offline ephemeris evaluation."""

    def __init__(self, segments: tuple[Any, ...], sha256: str) -> None:
        self.segments = segments
        self.sha256 = sha256

    @classmethod
    def open(cls, path: str | Path | None = None) -> "CompactChebyshevKernel":
        target_path = Path(path) if path is not None else COMPACT_KERNEL_PATH
        if not target_path.is_file():
            raise AstronomyDataUnavailable(f"compact kernel data file missing: {target_path}")
        raw_bytes = target_path.read_bytes()
        actual_sha256 = hashlib.sha256(raw_bytes).hexdigest()
        if target_path.resolve() == COMPACT_KERNEL_PATH.resolve():
            if COMPACT_KERNEL_SHA256 != "0" * 64 and actual_sha256.lower() != COMPACT_KERNEL_SHA256.lower():
                raise AstronomyDataUnavailable(
                    f"compact kernel SHA-256 mismatch: expected {COMPACT_KERNEL_SHA256}, got {actual_sha256}"
                )
        cache_key = (str(target_path.resolve()), actual_sha256)
        with _CACHE_LOCK:
            cached = _DECODED_SEGMENTS_CACHE.get(cache_key)
            if cached is not None:
                return cls(cached, actual_sha256)
            segments = _decode_compact_bytes(raw_bytes)
            _DECODED_SEGMENTS_CACHE[cache_key] = segments
            return cls(segments, actual_sha256)

    def close(self) -> None:
        """No file descriptor is kept open after decoding."""

    def __enter__(self) -> "CompactChebyshevKernel":
        return self

    def __exit__(self, *_exc: object) -> None:
        self.close()


def _decode_compact_bytes(raw_bytes: bytes) -> tuple[Any, ...]:
    if not raw_bytes.startswith(MAGIC_HEADER):
        raise AstronomyDataUnavailable("invalid compact kernel magic header")
    offset = len(MAGIC_HEADER)
    if len(raw_bytes) < offset + 4:
        raise AstronomyDataUnavailable("truncated compact kernel header")
    (meta_len,) = struct.unpack("<I", raw_bytes[offset : offset + 4])
    offset += 4
    meta = json.loads(raw_bytes[offset : offset + meta_len].decode("ascii"))
    offset += meta_len
    decompressed = zlib.decompress(raw_bytes[offset:])

    start_jd = float(meta["start_jd"])
    end_jd = float(meta["end_jd"])
    emrat = float(meta["emrat"])

    segments: list[Any] = []
    moon_coeffs_rev: np.ndarray | None = None
    moon_intlen: float = 8.0
    cursor = 0

    for entry in meta["segments"]:
        center = int(entry["center"])
        target = int(entry["target"])
        intlen = float(entry["intlen_days"])
        deg = int(entry["degree"])
        n_intervals = int(entry["n_intervals"])
        n_floats = deg * 3 * n_intervals
        n_bytes = n_floats * 8
        chunk = decompressed[cursor : cursor + n_bytes]
        cursor += n_bytes

        # Unshuffle bytes: stored as (8, n_floats) uint8 -> transpose back to (n_floats, 8)
        unshuffled = (
            np.frombuffer(chunk, dtype=np.uint8)
            .reshape(8, n_floats)
            .T.copy()
            .view(np.float64)
            .reshape(deg, 3, n_intervals)
        )
        # Reverse degree axis so index 0 is highest degree and index -1 is constant term c_0
        coeffs_rev = np.ascontiguousarray(unshuffled[::-1], dtype=np.float64)
        segments.append(
            CompactChebyshevSegment(
                center=center,
                target=target,
                start_jd=start_jd,
                end_jd=end_jd,
                intlen_days=intlen,
                coefficients_rev=coeffs_rev,
            )
        )
        if (center, target) == (3, 301):
            moon_coeffs_rev = coeffs_rev
            moon_intlen = intlen

    if moon_coeffs_rev is None:
        raise AstronomyDataUnavailable("compact kernel is missing (3, 301) lunar segment")

    # Derive (3, 399) Earth wrt EMB from (3, 301) Moon wrt EMB via DE440 Earth-Moon mass ratio
    earth_coeffs_rev = np.ascontiguousarray(-moon_coeffs_rev / emrat, dtype=np.float64)
    segments.append(
        CompactChebyshevSegment(
            center=3,
            target=399,
            start_jd=start_jd,
            end_jd=end_jd,
            intlen_days=moon_intlen,
            coefficients_rev=earth_coeffs_rev,
        )
    )

    # Add zero-offset planetary center segments for Mercury (1, 199) and Venus (2, 299)
    segments.append(ZeroOffsetSegment(center=1, target=199, start_jd=start_jd, end_jd=end_jd))
    segments.append(ZeroOffsetSegment(center=2, target=299, start_jd=start_jd, end_jd=end_jd))

    return tuple(segments)


def _fit_chebyshev_segment(
    spk_segment: Any, jd_start: float, intlen_days: float, n_intervals: int, deg_fit: int, deg_keep: int
) -> np.ndarray:
    j = np.arange(deg_fit, dtype=np.float64)
    nodes = np.cos(np.pi * (j + 0.5) / deg_fit)
    starts = jd_start + np.arange(n_intervals, dtype=np.float64) * intlen_days
    mids = starts + 0.5 * intlen_days
    t_grid = mids[:, None] + 0.5 * intlen_days * nodes[None, :]
    pos = spk_segment.compute(2451545.0, t_grid.ravel() - 2451545.0).reshape(3, n_intervals, deg_fit)
    m = np.arange(deg_keep, dtype=np.float64)[:, None]
    basis = np.cos(m * np.pi * (j[None, :] + 0.5) / deg_fit) * (2.0 / deg_fit)
    basis[0, :] *= 0.5
    return np.einsum("mj,caj->mca", basis, pos)


def build_compact_kernel_file(
    de440_bsp_path: str | Path, output_path: str | Path | None = None
) -> tuple[Path, str]:
    """Fit and write the compact Chebyshev kernel file from a verified DE440 SPK file."""
    from jplephem.spk import SPK

    bsp_path = Path(de440_bsp_path)
    actual_bsp_sha = hashlib.sha256(bsp_path.read_bytes()).hexdigest()
    if actual_bsp_sha.lower() != DE440_SHA256.lower():
        raise ValueError(f"DE440 SHA-256 mismatch: expected {DE440_SHA256}, got {actual_bsp_sha}")

    target_out = Path(output_path) if output_path is not None else COMPACT_KERNEL_PATH
    target_out.parent.mkdir(parents=True, exist_ok=True)

    chunks: list[bytes] = []
    meta_segments: list[dict[str, Any]] = []

    with SPK.open(str(bsp_path)) as spk:
        spk_map = {(int(s.center), int(s.target)): s for s in spk.segments}
        for center, target, intlen_days, degree, quant_km in PRIMARY_SEGMENT_SPECS:
            n_intervals = int(COMPACT_SPAN_DAYS // intlen_days)
            coeffs = _fit_chebyshev_segment(
                spk_map[(center, target)],
                COMPACT_START_JD,
                intlen_days,
                n_intervals,
                deg_fit=16,
                deg_keep=degree,
            )
            quantized = np.ascontiguousarray(
                np.round(coeffs / quant_km) * quant_km, dtype=np.float64
            )
            shuffled = quantized.view(np.uint8).reshape(-1, 8).T.tobytes()
            chunks.append(shuffled)
            meta_segments.append(
                {
                    "center": center,
                    "target": target,
                    "intlen_days": intlen_days,
                    "degree": degree,
                    "n_intervals": n_intervals,
                    "quant_km": quant_km,
                }
            )

    meta = {
        "format": "eoss-compact-chebyshev-v1",
        "source_kernel": "DE440",
        "source_sha256": DE440_SHA256,
        "start_jd": COMPACT_START_JD,
        "end_jd": COMPACT_END_JD,
        "emrat": DE440_EMRAT,
        "segments": meta_segments,
    }
    meta_bytes = json.dumps(meta, separators=(",", ":"), sort_keys=True).encode("ascii")
    compressed = zlib.compress(b"".join(chunks), level=9)
    payload = MAGIC_HEADER + struct.pack("<I", len(meta_bytes)) + meta_bytes + compressed

    target_out.write_bytes(payload)
    digest = hashlib.sha256(payload).hexdigest()
    return target_out, digest
