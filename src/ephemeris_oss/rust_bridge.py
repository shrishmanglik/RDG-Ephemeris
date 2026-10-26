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
from typing import Any, Sequence

import numpy as np

J2000_JD = 2451545.0
JULIAN_CENTURY_DAYS = 36525.0

EXPECTED_WASM_EXPORTS: tuple[str, ...] = (
    "ephemeris_normalize_deg",
    "eoss_eval_chebyshev_1d",
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
    "ephemeris_kp_sub_index",
    "wasm_arena_request_ptr",
    "wasm_arena_output_ptr",
    "wasm_compute_full_kundali",
)


def read_spk_state(
    kernel_path: str | Path,
    target: int,
    center: int,
    tdb_seconds: float,
    *,
    library_path: str | Path,
) -> tuple[float, float, float, float, float, float]:
    """Read a geometric J2000 state from SPK Type 2/3 using the native Rust reader.

    Units are km, km/s and TDB seconds since J2000, not UTC or TT. This is
    opt-in and never replaces Engine's apparent-place reduction. The caller
    verifies the kernel's provenance with the existing asset registry.
    """
    for body in (target, center):
        if type(body) is not int or not -(2**31) <= body < 2**31:
            raise ValueError("NAIF target and center must be signed 32-bit integers")
    epoch = float(tdb_seconds)
    if not math.isfinite(epoch):
        raise ValueError("TDB epoch must be finite")
    path_bytes = str(Path(kernel_path).resolve(strict=True)).encode("utf-8")
    library = ctypes.CDLL(str(Path(library_path).resolve(strict=True)))
    function = library.ephemeris_spk_file_state
    function.argtypes = [ctypes.c_char_p, ctypes.c_size_t, ctypes.c_int32, ctypes.c_int32,
                         ctypes.c_double, ctypes.POINTER(ctypes.c_double)]
    function.restype = ctypes.c_int32
    output = (ctypes.c_double * 6)()
    result = function(path_bytes, len(path_bytes), target, center, epoch, output)
    if result:
        reasons = {1: "invalid SPK data or epoch", 2: "unsupported SPK format, type or frame",
                   3: "no connected SPK coverage at epoch", 4: "SPK input could not be read"}
        raise ValueError(reasons.get(result, "unknown native SPK failure"))
    return tuple(float(value) for value in output)


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


def evaluate_chebyshev_clenshaw_1d(
    coeffs_rev: Sequence[float], tau: float, span_days: float
) -> tuple[float, float]:
    """Evaluate a reverse-ordered 1D Chebyshev series `coeffs_rev` (highest degree down to c_0)
    at normalized coordinate `tau` in `[-1, 1]` over `span_days`, returning `(position, velocity_per_day)`.
    """
    n = len(coeffs_rev)
    if n == 0:
        return 0.0, 0.0
    if n == 1:
        return float(coeffs_rev[0]), 0.0
    tau_f = float(tau)
    s2 = 2.0 * tau_f
    w0 = 0.0
    w1 = 0.0
    dw0 = 0.0
    dw1 = 0.0
    for i in range(n - 1):
        w2 = w1
        w1 = w0
        w0 = float(coeffs_rev[i]) + (s2 * w1 - w2)

        dw2 = dw1
        dw1 = dw0
        dw0 = 2.0 * w1 + dw1 * s2 - dw2

    position = float(coeffs_rev[n - 1]) + (tau_f * w0 - w1)
    scale = (2.0 / float(span_days)) if span_days != 0.0 else 0.0
    velocity = (w0 + tau_f * dw0 - dw1) * scale
    return position, velocity


def evaluate_chebyshev_clenshaw_3d(
    coeffs_rev_3d: Any,
    jd_tdb: float,
    start_jd: float,
    intlen_days: float,
) -> tuple[np.ndarray, np.ndarray]:
    """Evaluate 3D Chebyshev position (km) and velocity (km/day) via backward Clenshaw recurrence,
    matching `CompactChebyshevSegment.compute_and_differentiate` to machine precision (< 1e-9 km).
    Accepts `coeffs_rev_3d` with shape `(degree, 3, n_intervals)`, `(degree, 3)`, or `(3, degree)`.
    """
    intlen = float(intlen_days)
    if intlen <= 0.0:
        raise ValueError("intlen_days must be positive")
    arr = np.asarray(coeffs_rev_3d, dtype=np.float64)
    t_rel = float(jd_tdb) - float(start_jd)
    if arr.ndim == 3:
        n_intervals = int(arr.shape[2])
        idx_f, offset = divmod(t_rel, intlen)
        idx = int(idx_f)
        if idx == n_intervals and abs(offset) <= 1e-12:
            idx -= 1
            offset += intlen
        if idx < 0 or idx >= n_intervals:
            raise ValueError(f"jd_tdb {jd_tdb} outside segment interval range")
        tau = 2.0 * offset / intlen - 1.0
        axes_coeffs = (arr[:, 0, idx], arr[:, 1, idx], arr[:, 2, idx])
    elif arr.ndim == 2:
        if isinstance(coeffs_rev_3d, (tuple, list)) and len(coeffs_rev_3d) == 3 and arr.shape[0] == 3:
            axes_coeffs = (arr[0, :], arr[1, :], arr[2, :])
        elif arr.shape[1] == 3 and arr.shape[0] != 3:
            axes_coeffs = (arr[:, 0], arr[:, 1], arr[:, 2])
        elif arr.shape[0] == 3:
            axes_coeffs = (arr[0, :], arr[1, :], arr[2, :])
        else:
            raise ValueError(f"unsupported 2D coeffs_rev_3d shape: {arr.shape}")
        if -1e-9 <= t_rel <= intlen + 1e-9:
            offset = t_rel
        else:
            _, offset = divmod(t_rel, intlen)
        tau = 2.0 * offset / intlen - 1.0
    else:
        raise ValueError(f"coeffs_rev_3d must be 2D or 3D, got shape {arr.shape}")

    pos = np.empty(3, dtype=np.float64)
    vel = np.empty(3, dtype=np.float64)
    for axis in range(3):
        p, v = evaluate_chebyshev_clenshaw_1d(axes_coeffs[axis], tau, intlen)
        pos[axis] = p
        vel[axis] = v
    return pos, vel


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


class BatchNatalRequest(ctypes.Structure):
    """Zero-copy 64-byte C-ABI request struct matching Rust `BatchNatalRequest`."""

    _fields_ = [
        ("jd_utc", ctypes.c_double),
        ("jd_tt", ctypes.c_double),
        ("delta_t_sec", ctypes.c_double),
        ("lat_deg", ctypes.c_double),
        ("lon_deg", ctypes.c_double),
        ("alt_m", ctypes.c_double),
        ("ayanamsa_id", ctypes.c_uint32),
        ("house_system_id", ctypes.c_uint32),
        ("node_mode", ctypes.c_uint32),
        ("_pad", ctypes.c_uint32),
    ]


class FullKundaliOutput(ctypes.Structure):
    """Zero-copy 1416-byte C-ABI output struct matching Rust `FullKundaliOutput`."""

    _fields_ = [
        ("planet_lon_sidereal", ctypes.c_double * 12),
        ("planet_lat_ecliptic", ctypes.c_double * 12),
        ("planet_speed_lon", ctypes.c_double * 12),
        ("house_cusps_sidereal", ctypes.c_double * 12),
        ("varga_rashi_matrix", (ctypes.c_uint8 * 12) * 16),
        ("ashtakavarga_bav", (ctypes.c_uint8 * 12) * 8),
        ("ashtakavarga_sav", ctypes.c_uint8 * 12),
        ("sav_alignment_pad", ctypes.c_uint8 * 4),
        ("dasha_mahadasha_start_jd", ctypes.c_double * 9),
        ("dasha_antardasha_start_jd", (ctypes.c_double * 9) * 9),
        ("polar_status_flag", ctypes.c_uint32),
        ("_padding", ctypes.c_uint32),
    ]


def nakshatra_index(sidereal_lon_deg: float) -> int:
    """Compute 0-based Nakshatra index (`0..26`) matching Rust `ephemeris_nakshatra_index`."""
    lon = normalize_deg(sidereal_lon_deg)
    idx = int(math.floor(lon / (360.0 / 27.0)))
    return min(idx, 26)


def nakshatra_pada(sidereal_lon_deg: float) -> int:
    """Compute 1-based Nakshatra Pada (`1..4`) matching Rust `ephemeris_nakshatra_pada`."""
    lon = normalize_deg(sidereal_lon_deg)
    span = 360.0 / 27.0
    in_nak = lon - math.floor(lon / span) * span
    pada = int(math.floor(in_nak / (span / 4.0))) + 1
    return min(pada, 4)


def kp_sub_index(sidereal_lon_deg: float) -> int:
    """Compute 1-based KP Horary Sub-Table index (`1..249`) matching Rust `ephemeris_kp_sub_index`."""
    from ephemeris_oss.jyotish_advanced.kp import kp_coordinate_lords

    return int(kp_coordinate_lords(sidereal_lon_deg).horary_number_249)


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

    lib.eoss_eval_chebyshev_1d.argtypes = [
        ctypes.POINTER(ctypes.c_double),
        ctypes.c_size_t,
        ctypes.c_double,
        ctypes.c_double,
        ctypes.POINTER(ctypes.c_double),
    ]
    lib.eoss_eval_chebyshev_1d.restype = ctypes.c_double

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

    lib.ephemeris_kp_sub_index.argtypes = [ctypes.c_double]
    lib.ephemeris_kp_sub_index.restype = ctypes.c_uint32

    lib.wasm_arena_request_ptr.argtypes = []
    lib.wasm_arena_request_ptr.restype = ctypes.POINTER(BatchNatalRequest)

    lib.wasm_arena_output_ptr.argtypes = []
    lib.wasm_arena_output_ptr.restype = ctypes.POINTER(FullKundaliOutput)

    lib.wasm_compute_full_kundali.argtypes = [
        ctypes.POINTER(BatchNatalRequest),
        ctypes.POINTER(FullKundaliOutput),
    ]
    lib.wasm_compute_full_kundali.restype = ctypes.c_int32
    return lib
