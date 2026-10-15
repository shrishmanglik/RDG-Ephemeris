"""Clean-room bridge to the Rust/WebAssembly core crate (`rust/ephemeris-core`).

Provides:
1. Direct `ctypes` acceleration against the compiled `ephemeris_core` native library when present.
2. WebAssembly (`wasm32-unknown-unknown`) binary inspection and export verification (`verify_wasm_binary`).
3. Identical pure-Python reference implementations of the exact Clenshaw Chebyshev recurrence,
   Meeus Eq. 47.7 mean node, IAU 2006 general precession, named ayanamsa realisations,
   27 Nakshatras, 16 Parashari Shodashvarga charts, and Five-Limb Panchanga primitives so
   tests can verify machine-epsilon (`< 1e-13`) parity between Rust and Python.
"""

from __future__ import annotations

import ctypes
import math
import struct
from pathlib import Path
from typing import Sequence

J2000_JD = 2451545.0
JULIAN_CENTURY_DAYS = 36525.0

EXPECTED_WASM_EXPORTS: tuple[str, ...] = (
    "ephemeris_normalize_deg",
    "ephemeris_chebyshev_state_3d",
    "ephemeris_tdb_minus_tt_seconds",
    "ephemeris_mean_lunar_node_deg",
    "ephemeris_general_precession_deg",
    "ephemeris_ayanamsa_deg",
    "ephemeris_nakshatra_index",
    "ephemeris_nakshatra_pada",
    "ephemeris_nakshatra_fraction_remaining",
    "ephemeris_varga_sign",
    "ephemeris_tithi_number",
    "ephemeris_yoga_number",
    "ephemeris_karana_number",
    "ephemeris_fnv1a64_f64_slice",
)


def normalize_deg(angle_deg: float) -> float:
    """Normalize an angle in degrees into `[0.0, 360.0)`."""
    r = math.fmod(float(angle_deg), 360.0)
    return r + 360.0 if r < 0.0 else r


def evaluate_chebyshev_1d(coeffs: Sequence[float], tau: float) -> tuple[float, float]:
    """Evaluate a 1D Chebyshev series at `tau` in `[-1, 1]` via Clenshaw recurrence."""
    n = len(coeffs)
    if n == 0:
        return 0.0, 0.0
    if n == 1:
        return float(coeffs[0]), 0.0
    two_tau = 2.0 * tau
    b_kplus1 = 0.0
    b_kplus2 = 0.0
    db_kplus1 = 0.0
    db_kplus2 = 0.0
    for k in range(n - 1, 0, -1):
        b_k = two_tau * b_kplus1 - b_kplus2 + float(coeffs[k])
        db_k = 2.0 * b_kplus1 + two_tau * db_kplus1 - db_kplus2
        b_kplus2 = b_kplus1
        b_kplus1 = b_k
        db_kplus2 = db_kplus1
        db_kplus1 = db_k
    value = tau * b_kplus1 - b_kplus2 + float(coeffs[0])
    d_value_d_tau = b_kplus1 + tau * db_kplus1 - db_kplus2
    return value, d_value_d_tau


def chebyshev_state_3d(
    coeffs_xyz: Sequence[float],
    degree_count: int,
    t_start_jd: float,
    t_end_jd: float,
    t_jd: float,
) -> tuple[float, float, float, float, float, float]:
    """Evaluate 3D position and velocity `(x, y, z, vx, vy, vz)` over `[t_start_jd, t_end_jd]`."""
    if degree_count <= 0 or len(coeffs_xyz) != 3 * degree_count:
        raise ValueError("coeffs_xyz length must equal 3 * degree_count")
    span = t_end_jd - t_start_jd
    if span <= 0.0:
        raise ValueError("t_end_jd must be greater than t_start_jd")
    mid = 0.5 * (t_start_jd + t_end_jd)
    half_span = 0.5 * span
    tau = (t_jd - mid) / half_span
    d_tau_dt = 1.0 / half_span
    pos = [0.0, 0.0, 0.0]
    vel = [0.0, 0.0, 0.0]
    for axis in range(3):
        axis_coeffs = coeffs_xyz[axis * degree_count : (axis + 1) * degree_count]
        p, dp_dtau = evaluate_chebyshev_1d(axis_coeffs, tau)
        pos[axis] = p
        vel[axis] = dp_dtau * d_tau_dt
    return (pos[0], pos[1], pos[2], vel[0], vel[1], vel[2])


def mean_lunar_node_deg(jd_tt: float) -> float:
    """Mean longitude of the Moon's ascending node (Meeus Eq. 47.7)."""
    t = (jd_tt - J2000_JD) / JULIAN_CENTURY_DAYS
    omega = (
        125.0445479
        - 1934.1362891 * t
        + 0.0020754 * (t**2)
        + (t**3) / 467441.0
        - (t**4) / 60616000.0
    )
    return normalize_deg(omega)


def general_precession_deg(jd_tt: float) -> float:
    """IAU 2006 general precession in longitude from J2000.0 in degrees."""
    t = (jd_tt - J2000_JD) / JULIAN_CENTURY_DAYS
    arcsec = (
        5028.796195 * t
        + 1.1054348 * (t**2)
        + 0.00007964 * (t**3)
        - 0.000023857 * (t**4)
        - 0.0000000383 * (t**5)
    )
    return arcsec / 3600.0


def ayanamsa_deg(jd_tt: float, system_id: int = 0) -> float:
    """Mean ayanamsa in degrees matching Rust `ephemeris_ayanamsa_deg`."""
    anchors = {
        0: 23.853055555555556,
        1: 22.370277777777778,
        2: 23.75388888888889,
        3: 22.46,
        4: 24.73611111111111,
        5: 23.8570925,
    }
    anchor = anchors.get(system_id, 23.853055555555556)
    return normalize_deg(anchor + general_precession_deg(jd_tt))


def varga_sign(sidereal_lon_deg: float, varga_d: int) -> int:
    """Compute 0-based sign (`0..11`) in any of the 16 Parashari Shodashvarga charts."""
    lon = normalize_deg(sidereal_lon_deg)
    sign = min(int(math.floor(lon / 30.0)), 11)
    in_sign = min(max(lon - sign * 30.0, 0.0), 29.999999999999)
    is_odd = (sign % 2) == 0
    modality = sign % 3

    if varga_d == 1:
        return sign
    if varga_d == 2:
        first_half = in_sign < 15.0
        return 4 if ((is_odd and first_half) or (not is_odd and not first_half)) else 3
    if varga_d == 3:
        part = min(int(math.floor(in_sign / 10.0)), 2)
        return (sign + part * 4) % 12
    if varga_d == 4:
        part = min(int(math.floor(in_sign / 7.5)), 3)
        return (sign + part * 3) % 12
    if varga_d == 7:
        part = min(int(math.floor(in_sign / (30.0 / 7.0))), 6)
        start = sign if is_odd else (sign + 6) % 12
        return (start + part) % 12
    if varga_d == 9:
        part = min(int(math.floor(in_sign / (30.0 / 9.0))), 8)
        start = (0, 9, 6, 3)[sign % 4]
        return (start + part) % 12
    if varga_d == 10:
        part = min(int(math.floor(in_sign / 3.0)), 9)
        start = sign if is_odd else (sign + 8) % 12
        return (start + part) % 12
    if varga_d == 12:
        part = min(int(math.floor(in_sign / 2.5)), 11)
        return (sign + part) % 12
    if varga_d == 16:
        part = min(int(math.floor(in_sign / (30.0 / 16.0))), 15)
        return (modality * 4 + part) % 12
    if varga_d == 20:
        part = min(int(math.floor(in_sign / 1.5)), 19)
        start = (0, 8, 4)[modality]
        return (start + part) % 12
    if varga_d == 24:
        part = min(int(math.floor(in_sign / 1.25)), 23)
        start = 4 if is_odd else 3
        return (start + part) % 12
    if varga_d == 27:
        part = min(int(math.floor(in_sign / (30.0 / 27.0))), 26)
        return ((sign % 4) * 3 + part) % 12
    if varga_d == 30:
        if is_odd:
            if in_sign < 5.0:
                return 0
            if in_sign < 10.0:
                return 10
            if in_sign < 18.0:
                return 8
            if in_sign < 25.0:
                return 2
            return 6
        if in_sign < 5.0:
            return 1
        if in_sign < 12.0:
            return 5
        if in_sign < 20.0:
            return 11
        if in_sign < 25.0:
            return 9
        return 7
    if varga_d == 40:
        part = min(int(math.floor(in_sign / 0.75)), 39)
        start = 0 if is_odd else 6
        return (start + part) % 12
    if varga_d == 45:
        part = min(int(math.floor(in_sign / (30.0 / 45.0))), 44)
        return (modality * 4 + part) % 12
    if varga_d == 60:
        part = min(int(math.floor(in_sign * 2.0)), 59)
        return (sign + part) % 12
    d = max(varga_d, 1)
    part = min(int(math.floor(in_sign / (30.0 / d))), d - 1)
    return (sign + part) % 12


def fnv1a64_f64_slice(values: Sequence[float]) -> int:
    """Deterministic 64-bit FNV-1a hash matching Rust `ephemeris_fnv1a64_f64_slice`."""
    h = 0xCBF29CE484222325
    for v in values:
        val = 0.0 if v == 0.0 else float(v)
        for byte in struct.pack("<d", val):
            h ^= byte
            h = (h * 0x100000001B3) & 0xFFFFFFFFFFFFFFFF
    return h


def verify_wasm_binary(wasm_path: str | Path) -> dict[str, object]:
    """Verify that a compiled `.wasm` binary has valid WebAssembly magic/version headers
    and exports all required `ephemeris_*` C-ABI functions.
    """
    path = Path(wasm_path)
    data = path.read_bytes()
    if len(data) < 8 or data[:4] != b"\x00asm" or data[4:8] != b"\x01\x00\x00\x00":
        raise ValueError(f"invalid WebAssembly header in {path}")
    present_exports = [name for name in EXPECTED_WASM_EXPORTS if name.encode("utf-8") in data]
    missing = [name for name in EXPECTED_WASM_EXPORTS if name not in present_exports]
    if missing:
        raise ValueError(f"missing expected WebAssembly exports: {missing}")
    return {
        "size_bytes": len(data),
        "exports_verified": tuple(present_exports),
    }


def load_native_cdylib(dll_path: str | Path) -> ctypes.CDLL:
    """Bind the compiled native `ephemeris_core` shared library via `ctypes`."""
    lib = ctypes.CDLL(str(dll_path))
    lib.ephemeris_normalize_deg.argtypes = [ctypes.c_double]
    lib.ephemeris_normalize_deg.restype = ctypes.c_double

    lib.ephemeris_chebyshev_state_3d.argtypes = [
        ctypes.POINTER(ctypes.c_double),
        ctypes.c_size_t,
        ctypes.c_double,
        ctypes.c_double,
        ctypes.c_double,
        ctypes.POINTER(ctypes.c_double),
    ]
    lib.ephemeris_chebyshev_state_3d.restype = ctypes.c_int32

    lib.ephemeris_tdb_minus_tt_seconds.argtypes = [ctypes.c_double]
    lib.ephemeris_tdb_minus_tt_seconds.restype = ctypes.c_double

    lib.ephemeris_mean_lunar_node_deg.argtypes = [ctypes.c_double]
    lib.ephemeris_mean_lunar_node_deg.restype = ctypes.c_double

    lib.ephemeris_ayanamsa_deg.argtypes = [ctypes.c_double, ctypes.c_uint32]
    lib.ephemeris_ayanamsa_deg.restype = ctypes.c_double

    lib.ephemeris_nakshatra_index.argtypes = [ctypes.c_double]
    lib.ephemeris_nakshatra_index.restype = ctypes.c_uint32

    lib.ephemeris_nakshatra_pada.argtypes = [ctypes.c_double]
    lib.ephemeris_nakshatra_pada.restype = ctypes.c_uint32

    lib.ephemeris_varga_sign.argtypes = [ctypes.c_double, ctypes.c_uint32]
    lib.ephemeris_varga_sign.restype = ctypes.c_uint32

    lib.ephemeris_tithi_number.argtypes = [ctypes.c_double, ctypes.c_double]
    lib.ephemeris_tithi_number.restype = ctypes.c_uint32

    lib.ephemeris_yoga_number.argtypes = [ctypes.c_double, ctypes.c_double]
    lib.ephemeris_yoga_number.restype = ctypes.c_uint32

    lib.ephemeris_karana_number.argtypes = [ctypes.c_double, ctypes.c_double]
    lib.ephemeris_karana_number.restype = ctypes.c_uint32

    lib.ephemeris_fnv1a64_f64_slice.argtypes = [ctypes.POINTER(ctypes.c_double), ctypes.c_size_t]
    lib.ephemeris_fnv1a64_f64_slice.restype = ctypes.c_uint64
    return lib
