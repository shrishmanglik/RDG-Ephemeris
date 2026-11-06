"""High-precision deterministic solvers for computational problems in classical and modern astrology.

Legacy ephemeris libraries provide point-in-time planetary coordinates at a single timestamp,
leaving multi-variable inverse problems, sub-second divisional cusp boundaries, multi-century
phenomena sweeps, and classical-to-modern epicyclic drift analysis to manual guesswork.

This module provides four deterministic, receipt-sealed solvers:
1. ``solve_subsecond_shodashvarga_cusp_transitions``:
   Computes exact seconds-to-previous and seconds-to-next divisional chart sign transitions
   across all 16 Parashari Shodashvarga charts (``D1`` through ``D60``) for the Ascendant
   (Lagna) and all nine Grahas, identifying the tightest birth-time sensitivity threshold.
2. ``rectify_birth_time_bayesian``:
   Combines topocentric sunrise, Ascendant kinematics, Kunda 81x harmonic Shuddhi,
   Pranapada Shuddhi, Pancha Tattwa 90-minute elemental cycles, and life-event Dasha
   correlation into a single call from Julian Date and observer coordinates.
3. ``scan_multi_century_rare_phenomena``:
   Scans across multi-century windows (``3102 BCE`` to ``3000 CE``) for exact-second
   Graha Yuddha (planetary wars within 1 degree with apparent disc diameter and northern
   ecliptic latitude victory adjudication), retrograde stations (Vakri / Margi), and
   solar combustion windows (Astangata / Cazimi).
4. ``analyze_siddhanta_vs_jpl_de440_drift``:
   Quantifies the exact angular divergence between classical *Surya Siddhanta* (epicyclic
   *Manda* and *Sighra Samskara* from the ``3102 BCE`` Kali Yuga epoch) and modern
   numerical / analytical *Drig-Ganita* ephemerides at any historical or modern date.
"""

from __future__ import annotations

from bisect import bisect_right
from dataclasses import asdict, dataclass
from datetime import datetime, timedelta, timezone
import math
from typing import Any, Callable, Mapping, Sequence
import warnings

import erfa

from ._api import Engine
from ._version import __version__
from .adapter import CALC_RISE, EphemerisAdapter, VEDIC_NINE_GRAHAS
from .compact_kernel import COMPACT_EARLY_START_JD, COMPACT_LATE_END_JD
from .engine.civil_time import CalendarSystem, calendar_date
from .engine.earth_orientation import estimate_delta_t
from .engine.phenomena import (
    TARAGRAHAS,
    _builtin_planet_apparent,
    evaluate_graha_yuddha,
    find_combustion_windows,
    find_retrograde_stations,
)

_ORIG_BUILTIN_PLANET_APPARENT = _builtin_planet_apparent
_CACHED_COMPACT_PROVIDER: Any = None


def _get_cached_compact_provider() -> Any:
    global _CACHED_COMPACT_PROVIDER
    if _CACHED_COMPACT_PROVIDER is None:
        _CACHED_COMPACT_PROVIDER = Engine.load(kernels="compact-extended")._provider
    return _CACHED_COMPACT_PROVIDER
from .engine.receipt import canonical_hash
from .engine.stellar_anchors import YOGATARA_30_CATALOG, propagate_yogatara_apparent
from .jyotish.ashtakavarga import compute_ashtakavarga, evaluate_gochara_vedha
from .jyotish.dasha import (
    compute_chara_dasha,
    compute_chara_karakas,
    compute_kalachakra_dasha,
    compute_vimshottari_dasha,
    jd_to_iso_utc,
)
from .jyotish.nakshatra import NAKSHATRA_NAMES, RASI_NAMES, nakshatra_position, normalize_degrees
from .jyotish.vargas import (
    RASI_LORDS,
    SHODASHVARGA_KEYS,
    compute_shodashvarga,
    compute_vimshopaka_bala,
    is_pushkara_bhaga,
    is_pushkara_navamsa,
    is_vargottama,
    varga_sign,
)
from .jyotish_rectification.rectify import (
    BirthTimeRectificationReport,
    LAGNA_DEG_PER_SECOND,
    LifeEventSpec,
    rectify_birth_time,
)
from .jyotish_siddhanta.surya_siddhanta import (
    SiddhantaModernComparison,
    compare_siddhanta_with_modern,
    surya_siddhanta_true_positions,
)


def _jd_tt_to_iso_utc(jd_tt: float) -> str:
    """Convert a Terrestrial Time (TT) Julian Date to an ISO-8601 UTC timestamp string."""
    jd_val = float(jd_tt)
    y_tt, m_tt, d_tt, _fd_tt = erfa.jd2cal(2451545.0, jd_val - 2451545.0)
    if 1960 <= int(y_tt) <= 2100:
        try:
            with warnings.catch_warnings():
                warnings.simplefilter("ignore")
                tai1, tai2 = erfa.tttai(2451545.0, jd_val - 2451545.0)
                utc1, utc2 = erfa.taiutc(tai1, tai2)
            jd_utc = float(utc1 + utc2)
        except Exception:
            dec_year = float(y_tt) + (float(m_tt) - 0.5) / 12.0 + (float(d_tt) - 1.0) / 365.2425
            dt_sec = float(estimate_delta_t(min(max(dec_year, -1999.0), 3000.0)).seconds)
            jd_utc = jd_val - dt_sec / 86400.0
    else:
        dec_year = float(y_tt) + (float(m_tt) - 0.5) / 12.0 + (float(d_tt) - 1.0) / 365.2425
        if -1999.0 <= dec_year <= 3000.0:
            dt_sec = float(estimate_delta_t(dec_year).seconds)
        else:
            u_cent = (dec_year - 1820.0) / 100.0
            dt_sec = float(-20.0 + 32.0 * u_cent * u_cent)
        jd_utc = jd_val - dt_sec / 86400.0

    y, m, d, fd = erfa.jd2cal(2451545.0, jd_utc - 2451545.0)
    yi, mi, di = int(y), int(m), int(d)
    if 1 <= yi <= 9998:
        base = datetime(yi, mi, di, tzinfo=timezone.utc)
        dt = base + timedelta(days=float(fd))
        return dt.isoformat(timespec="microseconds").replace("+00:00", "Z")
    return jd_to_iso_utc(jd_utc)

# Mean angular velocities in degrees per second for fast analytical bracket estimation
_MEAN_DEG_PER_SECOND: Mapping[str, float] = {
    "Ascendant": LAGNA_DEG_PER_SECOND,
    "Sun": 0.98564736 / 86400.0,
    "Moon": 13.17635815 / 86400.0,
    "Mercury": 1.3833 / 86400.0,
    "Venus": 1.2000 / 86400.0,
    "Mars": 0.5240 / 86400.0,
    "Jupiter": 0.0831 / 86400.0,
    "Saturn": 0.0335 / 86400.0,
    "Rahu": -0.0529539 / 86400.0,
    "Ketu": -0.0529539 / 86400.0,
}

_DIVISION_FACTORS: Mapping[str, int] = {
    "D1": 1,
    "D2": 2,
    "D3": 3,
    "D4": 4,
    "D7": 7,
    "D9": 9,
    "D10": 10,
    "D12": 12,
    "D16": 16,
    "D20": 20,
    "D24": 24,
    "D27": 27,
    "D30": 30,
    "D40": 40,
    "D45": 45,
    "D60": 60,
}


@dataclass(frozen=True)
class VargaBoundaryMargin:
    """Exact angular and temporal margin to the previous and next divisional cusp."""

    body: str
    varga: str
    division_factor: int
    sign_index: int
    sign_name: str
    sign_lord: str
    longitude_deg: float
    sector_span_deg: float
    degrees_from_lower_cusp: float
    degrees_to_upper_cusp: float
    seconds_to_previous_cusp: float
    seconds_to_next_cusp: float
    shashtiamsa_name: str | None = None
    shashtiamsa_is_benefic: bool | None = None


@dataclass(frozen=True)
class SubsecondShodashvargaCuspReport:
    """Complete 16-varga sub-second cusp sensitivity analysis for Ascendant and 9 Grahas."""

    jd_ut: float
    iso_utc: str
    latitude_deg: float
    longitude_deg: float
    ayanamsa: str
    ayanamsa_deg: float
    ascendant_longitude_deg: float
    most_sensitive_varga: str
    minimum_ascendant_cusp_margin_seconds: float
    ascendant_margins: Mapping[str, VargaBoundaryMargin]
    planet_margins: Mapping[str, Mapping[str, VargaBoundaryMargin]]
    receipt: Mapping[str, Any]
    receipt_sha256: str
    true_node: bool = False


@dataclass(frozen=True)
class MultiCenturyPhenomenaReport:
    """Multi-century exact-second scan of planetary wars, retrograde stations, and combustion."""

    start_jd_tt: float
    end_jd_tt: float
    start_iso_utc: str
    end_iso_utc: str
    ayanamsa: str
    bodies: tuple[str, ...]
    graha_yuddha_count: int
    retrograde_station_count: int
    combustion_window_count: int
    graha_yuddha_events: tuple[Mapping[str, Any], ...]
    retrograde_stations: tuple[Mapping[str, Any], ...]
    combustion_windows: tuple[Mapping[str, Any], ...]
    receipt: Mapping[str, Any]
    receipt_sha256: str
    ephemeris_source: str = "compact-de440-numerical"


@dataclass(frozen=True)
class SiddhantaDriftAnalysisReport:
    """Differential report comparing classical Surya Siddhanta vs modern JPL DE440 / Drig-Ganita."""

    jd_ut: float
    iso_utc: str
    ahargana_days: float
    ayanamsa: str
    ephemeris_source: str
    mean_abs_delta_deg: float
    max_abs_delta_deg: float
    min_abs_delta_body: str
    max_abs_delta_body: str
    planet_comparisons: Mapping[str, Mapping[str, Any]]
    receipt: Mapping[str, Any]
    receipt_sha256: str


def _build_varga_sign_cusps() -> dict[str, tuple[float, ...]]:
    """Precompute the exact sorted list of true 360-degree sign-transition cusps for each Varga.

    Handles unequal Parashari D30 (Trimsamsa) sector widths ([0, 5, 10, 18, 25, 30] in odd signs
    and [0, 5, 12, 20, 25, 30] in even signs) as well as cross-sign same-lord/same-sign
    continuations (such as D2 Hora, D10 Dasamsa, and D24 Chaturvimsamsa) so that every cusp
    in the table is an actual ``varga_sign(...).sign_index`` transition boundary.
    """
    table: dict[str, tuple[float, ...]] = {}
    eps = 1.0e-7
    for varga_key in SHODASHVARGA_KEYS:
        candidates: list[float] = []
        if varga_key == "D30":
            for rasi_idx in range(12):
                base = rasi_idx * 30.0
                offsets = (0.0, 5.0, 10.0, 18.0, 25.0) if (rasi_idx % 2 == 0) else (0.0, 5.0, 12.0, 20.0, 25.0)
                for off in offsets:
                    candidates.append(base + off)
        else:
            div_factor = _DIVISION_FACTORS[varga_key]
            total_parts = 12 * div_factor
            for k in range(total_parts):
                candidates.append((k * 360.0) / float(total_parts))

        true_cusps: list[float] = []
        for c in sorted(candidates):
            sign_before = varga_sign((c - eps) % 360.0, varga_key).sign_index
            sign_after = varga_sign((c + eps) % 360.0, varga_key).sign_index
            if sign_before != sign_after:
                true_cusps.append(float(c))
        table[varga_key] = tuple(true_cusps)
    return table


_VARGA_SIGN_CUSPS: Mapping[str, tuple[float, ...]] = _build_varga_sign_cusps()


def _varga_sign_sector_bounds(
    lon_deg: float,
    varga_key: str,
    current_sign: int,
) -> tuple[float, float, float, float, float]:
    """Return ``(c_low, c_high, deg_from_lower, deg_to_upper, sector_span)`` for ``lon_deg``."""
    lon = normalize_degrees(lon_deg)
    cusps = _VARGA_SIGN_CUSPS[varga_key]
    n_cusps = len(cusps)
    idx = bisect_right(cusps, lon) - 1
    if idx < 0:
        idx = n_cusps - 1

    # Guard against floating-point boundary rounding when lon is within machine epsilon of a cusp
    for offset in (0, -1, 1):
        cand_idx = (idx + offset) % n_cusps
        c_low = cusps[cand_idx]
        c_high = cusps[(cand_idx + 1) % n_cusps]
        span = (c_high - c_low) % 360.0
        if span <= 0.0:
            span = 360.0
        mid = (c_low + 0.5 * span) % 360.0
        if varga_sign(mid, varga_key).sign_index == current_sign:
            deg_from_lower = (lon - c_low) % 360.0
            if deg_from_lower > span and deg_from_lower > 360.0 - 1.0e-7:
                deg_from_lower = 0.0
            deg_from_lower = min(max(0.0, deg_from_lower), span)
            deg_to_upper = max(0.0, span - deg_from_lower)
            return c_low, c_high, deg_from_lower, deg_to_upper, span

    c_low = cusps[idx]
    c_high = cusps[(idx + 1) % n_cusps]
    span = (c_high - c_low) % 360.0 or 360.0
    deg_from_lower = min(max(0.0, (lon - c_low) % 360.0), span)
    deg_to_upper = max(0.0, span - deg_from_lower)
    return c_low, c_high, deg_from_lower, deg_to_upper, span


def _solve_varga_transition_seconds(
    body: str,
    lon0: float,
    current_sign: int,
    varga_key: str,
    deg_from_lower: float,
    deg_to_upper: float,
    sector_span: float,
    speed_deg_per_sec: float,
    dir_sign: float,
    position_at_offset_sec: Callable[[float], float],
) -> float:
    """Bracket and refine the exact transition time ``t > 0`` along ``dt = dir_sign * t``
    where ``varga_sign(position_at_offset_sec(dir_sign * t), varga_key).sign_index != current_sign``.
    """
    v_mean = abs(_MEAN_DEG_PER_SECOND.get(body, 1.0e-5))
    v_dir = dir_sign * float(speed_deg_per_sec)

    if deg_from_lower <= 1.0e-12 and v_dir < 0.0:
        return 0.0
    if deg_to_upper <= 1.0e-12 and v_dir > 0.0:
        return 0.0

    def eval_at(t_sec: float) -> tuple[bool, float, float]:
        lon_t = normalize_degrees(position_at_offset_sec(dir_sign * t_sec))
        d_t = (lon_t - lon0 + 180.0) % 360.0 - 180.0
        margin_t = min(d_t + deg_from_lower, deg_to_upper - d_t)
        sign_t = varga_sign(lon_t, varga_key).sign_index
        still_in = (sign_t == current_sign) and (-deg_from_lower <= d_t < deg_to_upper)
        return still_in, margin_t, d_t

    t_lo = 0.0
    lon_lo = lon0
    margin_lo = min(deg_from_lower, deg_to_upper)
    t_hi: float | None = None
    margin_hi = 0.0

    # Unified first-crossing-preserving adaptive bracketing from t_lo = 0.0
    target_deg = deg_to_upper if v_dir >= 0.0 else deg_from_lower
    if abs(v_dir) > 1.0e-9:
        t_est = target_deg / abs(v_dir)
        step = min(1.0, max(1.0e-4, 0.05 * min(target_deg, sector_span) / abs(v_dir)))
        max_step = max(10.0, min(0.125 * max(t_est, 1.0), 0.20 * sector_span / max(abs(v_dir), v_mean, 1.0e-7)))
    else:
        step = 0.25
        max_step = max(60.0, 0.20 * sector_span / max(v_mean, 1.0e-7))
    max_angle_step = max(0.05, min(0.20 * sector_span, 4.0))

    for _ in range(480):
        t_probe = t_lo + step
        lon_p = normalize_degrees(position_at_offset_sec(dir_sign * t_probe))
        signed_step_delta = (lon_p - lon_lo + 180.0) % 360.0 - 180.0
        step_delta = abs(signed_step_delta)
        if step_delta > max_angle_step and step > 1.0e-5:
            step *= 0.5
            continue
        in_p, margin_p, d_p = eval_at(t_probe)
        if not in_p:
            t_hi = t_probe
            margin_hi = margin_p
            break
        v_inst = step_delta / max(step, 1.0e-9)
        if signed_step_delta > 1.0e-12:
            rem_deg = max(0.0, deg_to_upper - d_p)
        elif signed_step_delta < -1.0e-12:
            rem_deg = max(0.0, deg_from_lower + d_p)
        else:
            rem_deg = max(0.0, margin_p)
        t_rem_est = rem_deg / max(v_inst, 1.0e-12)
        dyn_max_step = max(
            10.0,
            min(
                0.20 * max(t_rem_est, 1.0),
                0.20 * sector_span / max(v_inst, v_mean, 1.0e-7),
            ),
        )
        max_step = max(max_step, dyn_max_step)
        t_lo = t_probe
        lon_lo = lon_p
        margin_lo = margin_p
        if step_delta < 0.05 * max_angle_step:
            step = min(max_step, step * 1.5)
        else:
            step = min(max_step, step * 1.2)

    if t_hi is None:
        raise RuntimeError(f"Failed to bracket {varga_key} transition for {body} at lon={lon0}")

    # Safeguarded Illinois secant + bisection refinement to sub-10-microsecond precision
    f_lo = float(margin_lo)
    f_hi = float(margin_hi)
    last_side = 0
    for it in range(56):
        span = t_hi - t_lo
        if span <= 1.0e-5:
            break
        denom = f_lo - f_hi
        if (it % 6 != 5) and abs(denom) > 1.0e-15 and f_lo > 0.0 >= f_hi:
            frac = f_lo / denom
            pad = min(0.25 * 1.0e-5 / span, 0.05)
            frac = min(max(frac, pad), 1.0 - pad)
            t_mid = t_lo + frac * span
        else:
            t_mid = 0.5 * (t_lo + t_hi)

        in_mid, margin_mid, _ = eval_at(t_mid)
        if in_mid:
            t_lo = t_mid
            f_lo = float(margin_mid)
            if last_side == -1:
                f_hi *= 0.5
            last_side = -1
        else:
            t_hi = t_mid
            f_hi = float(margin_mid)
            if last_side == 1:
                f_lo *= 0.5
            last_side = 1

    return 0.5 * (t_lo + t_hi)


def _compute_body_varga_margins(
    body: str,
    longitude_deg: float,
    speed_deg_per_sec: float,
    *,
    position_at_offset_sec: Callable[[float], float] | None = None,
) -> dict[str, VargaBoundaryMargin]:
    """Compute exact angular and temporal distance to each of the 16 Shodashvarga boundaries."""
    lon = normalize_degrees(longitude_deg)
    spd = float(speed_deg_per_sec)
    if position_at_offset_sec is None and spd == 0.0:
        raise ValueError("speed_deg_per_sec must be non-zero when position_at_offset_sec is not provided")

    pos_fn: Callable[[float], float] | None = None
    solved_bounds_cache: dict[tuple[float, float, float], float] = {}
    if position_at_offset_sec is not None:
        pos_cache: dict[float, float] = {0.0: lon}

        def _cached_pos(dt_sec: float) -> float:
            key = round(float(dt_sec), 7)
            val = pos_cache.get(key)
            if val is None:
                val = normalize_degrees(position_at_offset_sec(float(dt_sec)))
                pos_cache[key] = val
            return val

        pos_fn = _cached_pos

    placements = compute_shodashvarga(lon)
    margins: dict[str, VargaBoundaryMargin] = {}

    for varga_key in SHODASHVARGA_KEYS:
        pl = placements[varga_key]
        div_factor = _DIVISION_FACTORS[varga_key]
        c_low, c_high, deg_from_lower, deg_to_upper, sector_span = _varga_sign_sector_bounds(
            lon,
            varga_key,
            pl.sign_index,
        )

        if pos_fn is None:
            abs_speed = abs(spd)
            if spd > 0.0:
                sec_prev = deg_from_lower / abs_speed
                sec_next = deg_to_upper / abs_speed
            else:
                sec_prev = deg_to_upper / abs_speed
                sec_next = deg_from_lower / abs_speed
        else:
            prev_cache_key = (round(c_low, 9), round(c_high, 9), -1.0)
            sec_prev = solved_bounds_cache.get(prev_cache_key)
            if sec_prev is None:
                sec_prev = _solve_varga_transition_seconds(
                    body,
                    lon,
                    pl.sign_index,
                    varga_key,
                    deg_from_lower,
                    deg_to_upper,
                    sector_span,
                    spd,
                    -1.0,
                    pos_fn,
                )
                solved_bounds_cache[prev_cache_key] = sec_prev

            next_cache_key = (round(c_low, 9), round(c_high, 9), 1.0)
            sec_next = solved_bounds_cache.get(next_cache_key)
            if sec_next is None:
                sec_next = _solve_varga_transition_seconds(
                    body,
                    lon,
                    pl.sign_index,
                    varga_key,
                    deg_from_lower,
                    deg_to_upper,
                    sector_span,
                    spd,
                    1.0,
                    pos_fn,
                )
                solved_bounds_cache[next_cache_key] = sec_next

        margins[varga_key] = VargaBoundaryMargin(
            body=body,
            varga=varga_key,
            division_factor=div_factor,
            sign_index=pl.sign_index,
            sign_name=pl.sign_name,
            sign_lord=pl.sign_lord,
            longitude_deg=round(lon, 8),
            sector_span_deg=round(sector_span, 8),
            degrees_from_lower_cusp=round(deg_from_lower, 8),
            degrees_to_upper_cusp=round(deg_to_upper, 8),
            seconds_to_previous_cusp=round(sec_prev, 4),
            seconds_to_next_cusp=round(sec_next, 4),
            shashtiamsa_name=pl.shashtiamsa_name,
            shashtiamsa_is_benefic=pl.shashtiamsa_is_benefic,
        )
    return margins


def solve_subsecond_shodashvarga_cusp_transitions(
    jd_ut: float,
    latitude_deg: float,
    longitude_deg: float,
    *,
    ayanamsa: str = "lahiri",
    true_node: bool = False,
    adapter: EphemerisAdapter | None = None,
) -> SubsecondShodashvargaCuspReport:
    """Solve exact seconds-to-previous and seconds-to-next sign transitions across all 16
    Parashari Shodashvarga charts (``D1`` through ``D60``) for the Ascendant and all 9 Grahas.
    """
    ad = adapter if adapter is not None else EphemerisAdapter()
    base_jd = float(jd_ut)
    lat = float(latitude_deg)
    lon = float(longitude_deg)
    use_true_node = bool(true_node)
    ayan_deg = ad.get_ayanamsa_ut(base_jd, mode=ayanamsa)
    houses_res = ad.houses_ut(
        base_jd,
        lat,
        lon,
        system="whole_sign",
        ayanamsa=ayanamsa,
    )

    # Measure instantaneous topocentric Ascendant angular speed via 1-second finite difference
    dt_days = 1.0 / 86400.0
    houses_plus = ad.houses_ut(
        base_jd + dt_days,
        lat,
        lon,
        system="whole_sign",
        ayanamsa=ayanamsa,
    )
    asc_delta = (houses_plus.ascendant_deg - houses_res.ascendant_deg + 180.0) % 360.0 - 180.0
    asc_speed_deg_per_sec = asc_delta

    def _asc_at_offset(dt_sec: float) -> float:
        return ad.houses_ut(
            base_jd + float(dt_sec) / 86400.0,
            lat,
            lon,
            system="whole_sign",
            ayanamsa=ayanamsa,
        ).ascendant_deg

    asc_margins = _compute_body_varga_margins(
        "Ascendant",
        houses_res.ascendant_deg,
        asc_speed_deg_per_sec,
        position_at_offset_sec=_asc_at_offset,
    )

    planet_margins: dict[str, Mapping[str, VargaBoundaryMargin]] = {}
    for body_key in VEDIC_NINE_GRAHAS:
        p_pos = ad.calc_ut(
            base_jd,
            body_key,
            sidereal=True,
            ayanamsa=ayanamsa,
            true_node=use_true_node,
        )
        p_name = body_key.capitalize()
        p_speed_sec = p_pos.longitude_speed_deg_per_day / 86400.0

        def _planet_at_offset(dt_sec: float, _b: str = body_key) -> float:
            return ad.calc_ut(
                base_jd + float(dt_sec) / 86400.0,
                _b,
                sidereal=True,
                ayanamsa=ayanamsa,
                true_node=use_true_node,
            ).longitude_deg

        planet_margins[p_name] = _compute_body_varga_margins(
            p_name,
            p_pos.longitude_deg,
            p_speed_sec,
            position_at_offset_sec=_planet_at_offset,
        )

    most_sensitive_varga = "D60"
    min_margin_sec = float("inf")
    for v_key, margin in asc_margins.items():
        nearest = min(margin.seconds_to_previous_cusp, margin.seconds_to_next_cusp)
        if nearest < min_margin_sec:
            min_margin_sec = nearest
            most_sensitive_varga = v_key

    receipt = {
        "module": "ephemeris_oss.impossible_astrology.shodashvarga_cusps",
        "version": __version__,
        "jd_ut": round(base_jd, 10),
        "latitude_deg": round(lat, 6),
        "longitude_deg": round(lon, 6),
        "ayanamsa": ayanamsa,
        "ayanamsa_deg": round(float(ayan_deg), 8),
        "true_node": use_true_node,
        "ascendant_longitude_deg": round(float(houses_res.ascendant_deg), 8),
        "most_sensitive_varga": most_sensitive_varga,
        "minimum_ascendant_cusp_margin_seconds": round(min_margin_sec, 4),
        "ascendant_margins": {k: asdict(v) for k, v in asc_margins.items()},
        "planet_margins": {
            p_name: {k: asdict(v) for k, v in v_map.items()}
            for p_name, v_map in planet_margins.items()
        },
    }
    return SubsecondShodashvargaCuspReport(
        jd_ut=base_jd,
        iso_utc=jd_to_iso_utc(base_jd),
        latitude_deg=lat,
        longitude_deg=lon,
        ayanamsa=ayanamsa,
        ayanamsa_deg=float(ayan_deg),
        ascendant_longitude_deg=float(houses_res.ascendant_deg),
        most_sensitive_varga=most_sensitive_varga,
        minimum_ascendant_cusp_margin_seconds=round(min_margin_sec, 4),
        ascendant_margins=asc_margins,
        planet_margins=planet_margins,
        receipt=receipt,
        receipt_sha256=canonical_hash(receipt),
        true_node=use_true_node,
    )


def rectify_birth_time_bayesian(
    nominal_jd_ut: float,
    latitude_deg: float,
    longitude_deg: float,
    *,
    window_minutes: float = 15.0,
    step_seconds: float = 10.0,
    ayanamsa: str = "lahiri",
    true_node: bool = False,
    life_events: Sequence[Mapping[str, Any] | LifeEventSpec] | None = None,
    adapter: EphemerisAdapter | None = None,
) -> BirthTimeRectificationReport:
    """High-level birth-time rectification solver directly from Julian Date and observer coordinates.

    Automatically resolves local sunrise, sidereal Lagna, Sun/Moon/planetary longitudes,
    Kunda 81x harmonic alignment, Pranapada Shuddhi, Pancha Tattwa elemental cycles,
    and life-event Dasha triggers across ``[nominal_jd_ut - window, nominal_jd_ut + window]``.
    """
    ad = adapter if adapter is not None else EphemerisAdapter()
    houses_res = ad.houses_ut(
        float(nominal_jd_ut),
        float(latitude_deg),
        float(longitude_deg),
        system="whole_sign",
        ayanamsa=ayanamsa,
    )
    try:
        _, sr_tuple = ad.rise_trans(
            float(nominal_jd_ut) - 0.5,
            "sun",
            CALC_RISE,
            geopos=(float(longitude_deg), float(latitude_deg), 0.0),
        )
        sunrise_jd = float(sr_tuple[0])
        if sunrise_jd > float(nominal_jd_ut):
            _, sr_prev = ad.rise_trans(
                float(nominal_jd_ut) - 1.25,
                "sun",
                CALC_RISE,
                geopos=(float(longitude_deg), float(latitude_deg), 0.0),
            )
            sunrise_jd = float(sr_prev[0])
    except Exception:
        sunrise_jd = float(nominal_jd_ut) - 0.25

    planet_lons: dict[str, float] = {}
    for body_key in VEDIC_NINE_GRAHAS:
        pos = ad.calc_ut(
            float(nominal_jd_ut),
            body_key,
            sidereal=True,
            ayanamsa=ayanamsa,
            true_node=bool(true_node),
        )
        planet_lons[body_key.capitalize()] = pos.longitude_deg

    return rectify_birth_time(
        nominal_jd_ut=float(nominal_jd_ut),
        sunrise_jd_ut=float(sunrise_jd),
        nominal_lagna_lon_deg=float(houses_res.ascendant_deg),
        sun_lon_deg=float(planet_lons["Sun"]),
        moon_lon_deg=float(planet_lons["Moon"]),
        window_minutes=float(window_minutes),
        step_seconds=float(step_seconds),
        planet_longitudes=planet_lons,
        life_events=life_events,
    )


def scan_multi_century_rare_phenomena(
    start_jd_tt: float,
    end_jd_tt: float,
    *,
    bodies: Sequence[str] = TARAGRAHAS,
    ayanamsa: str = "lahiri",
    max_war_separation_deg: float = 1.0,
) -> MultiCenturyPhenomenaReport:
    """Scan a multi-day, multi-year, or multi-century window (``3102 BCE`` to ``3000 CE``)
    for exact-second Graha Yuddha (planetary wars), retrograde stations, and solar combustion.
    """
    if float(end_jd_tt) <= float(start_jd_tt):
        raise ValueError("end_jd_tt must be greater than start_jd_tt")

    normalized_bodies = tuple(
        b.strip().lower() for b in bodies if b.strip().lower() in TARAGRAHAS
    )
    if not normalized_bodies:
        normalized_bodies = TARAGRAHAS

    is_monkeypatched = _builtin_planet_apparent is not _ORIG_BUILTIN_PLANET_APPARENT
    compact_provider = None
    if not is_monkeypatched:
        try:
            compact_provider = _get_cached_compact_provider()
        except Exception:
            compact_provider = None

    start_year = int(
        calendar_date(float(start_jd_tt) - 2.0, calendar=CalendarSystem.PROLEPTIC_GREGORIAN)[0]
    )
    end_year = int(
        calendar_date(float(end_jd_tt) + 2.0, calendar=CalendarSystem.PROLEPTIC_GREGORIAN)[0]
    )
    use_long_term_mean_frame = start_year < 1600 or end_year > 2400

    used_numerical = False
    used_analytical = False

    def _epoch_source(jd_val: float) -> str:
        t_val = float(jd_val)
        if (
            compact_provider is not None
            and COMPACT_EARLY_START_JD <= t_val <= COMPACT_LATE_END_JD
        ):
            return "compact-de440-numerical"
        return "analytical-keplerian-fallback"

    def _evaluate_bodies_at(req_bodies: Sequence[str], jd_val: float) -> dict[str, dict[str, float]]:
        nonlocal used_numerical, used_analytical
        t_val = float(jd_val)
        keys = tuple(dict.fromkeys(b.strip().lower() for b in req_bodies))
        if (
            compact_provider is not None
            and COMPACT_EARLY_START_JD <= t_val <= COMPACT_LATE_END_JD
        ):
            used_numerical = True
            tt_pair = (2451545.0, t_val - 2451545.0)
            epoch_year = int(
                calendar_date(t_val, calendar=CalendarSystem.PROLEPTIC_GREGORIAN)[0]
            )
            if use_long_term_mean_frame or epoch_year < 1600 or epoch_year > 2400:
                tdb_offset = float(erfa.dtdb(*tt_pair, 0.0, 0.0, 0.0, 0.0))
                jd_tdb_val = float(sum(erfa.tttdb(*tt_pair, tdb_offset)))
                positions = compact_provider.planet_positions_tt(
                    jd_tt=t_val,
                    bodies=keys,
                    jd_tdb=jd_tdb_val,
                    mean_equinox=True,
                )["positions"]
            else:
                positions = compact_provider.planet_positions_tt(
                    jd_tt=t_val,
                    bodies=keys,
                )["positions"]
            lower_map = {k.strip().lower(): v for k, v in positions.items()}
            out: dict[str, dict[str, float]] = {}
            for key in keys:
                entry = lower_map.get(key)
                if entry is not None:
                    dist_km: float | None = None
                    if "distance_km" in entry:
                        dist_km = float(entry["distance_km"])
                    else:
                        try:
                            st = compact_provider.geocentric_state_at_tdb(
                                body=key,
                                tdb=tt_pair,
                                kernel_year=2000,
                            )
                            dist_km = float(math.hypot(*st.position_km))
                        except Exception:
                            dist_km = None
                    if dist_km is None:
                        dist_km = float(_builtin_planet_apparent(key, t_val)["distance_km"])
                    out[key] = {
                        "longitude_deg": float(entry["longitude_deg"]) % 360.0,
                        "latitude_deg": float(entry.get("latitude_deg", 0.0)),
                        "distance_km": dist_km,
                    }
                else:
                    used_analytical = True
                    raw = dict(_builtin_planet_apparent(key, t_val))
                    if use_long_term_mean_frame and not is_monkeypatched:
                        dpsi_rad, _ = erfa.nut06a(2451545.0, t_val - 2451545.0)
                        raw["longitude_deg"] = (float(raw["longitude_deg"]) - math.degrees(float(dpsi_rad))) % 360.0
                    out[key] = raw
            return out

        used_analytical = True
        out_analytical: dict[str, dict[str, float]] = {}
        dpsi_deg = 0.0
        if use_long_term_mean_frame and not is_monkeypatched:
            dpsi_rad, _ = erfa.nut06a(2451545.0, t_val - 2451545.0)
            dpsi_deg = math.degrees(float(dpsi_rad))
        for key in keys:
            raw = dict(_builtin_planet_apparent(key, t_val))
            if dpsi_deg != 0.0:
                raw["longitude_deg"] = (float(raw["longitude_deg"]) - dpsi_deg) % 360.0
            out_analytical[key] = raw
        return out_analytical

    def _planet_apparent_at(body_key: str, jd_val: float) -> dict[str, float]:
        key = body_key.strip().lower()
        return _evaluate_bodies_at((key,), jd_val)[key]

    def _hybrid_position_provider(jd_val: float, req_bodies: Sequence[str]) -> dict[str, dict[str, float]]:
        return _evaluate_bodies_at(req_bodies, float(jd_val))

    # Scan across [start_jd_tt, end_jd_tt] for contiguous Graha Yuddha encounters per body pair
    span_days = float(end_jd_tt) - float(start_jd_tt)
    step_days = min(1.0, max(0.25, span_days / 365.0), span_days)
    active_encounters: dict[tuple[str, str], list[tuple[float, Any]]] = {}
    completed_encounters: list[tuple[tuple[str, str], list[tuple[float, Any]]]] = []
    t_cur = float(start_jd_tt)
    end_val = float(end_jd_tt)
    while True:
        snap_positions = _evaluate_bodies_at(normalized_bodies, t_cur)
        instant_wars = evaluate_graha_yuddha(
            snap_positions,
            max_longitude_separation_deg=float(max_war_separation_deg),
        )
        present_pairs: set[tuple[str, str]] = set()
        for w in instant_wars:
            pair = (w.body_a, w.body_b)
            present_pairs.add(pair)
            active_encounters.setdefault(pair, []).append((t_cur, w))
        for pair in list(active_encounters.keys()):
            if pair not in present_pairs:
                completed_encounters.append((pair, active_encounters.pop(pair)))
        if t_cur >= end_val:
            break
        t_cur = min(end_val, t_cur + step_days)

    for pair, samples in list(active_encounters.items()):
        completed_encounters.append((pair, samples))

    def _refine_war_encounter_minimum(
        pair: tuple[str, str],
        samples: list[tuple[float, Any]],
    ) -> tuple[float, Any]:
        best_t, best_w = min(samples, key=lambda item: item[1].longitude_separation_deg)
        body_a_key = pair[0].strip().lower()
        body_b_key = pair[1].strip().lower()
        first_t = min(t for t, _ in samples)
        last_t = max(t for t, _ in samples)
        left = max(float(start_jd_tt), min(best_t - step_days, first_t - step_days))
        right = min(float(end_jd_tt), max(best_t + step_days, last_t + step_days))
        if right <= left + 1.0e-9:
            return best_t, best_w

        def _signed_diff_at(jd: float) -> float:
            pa = _planet_apparent_at(body_a_key, jd)
            pb = _planet_apparent_at(body_b_key, jd)
            return (float(pa["longitude_deg"]) - float(pb["longitude_deg"]) + 180.0) % 360.0 - 180.0

        def _sep_at(jd: float) -> float:
            return abs(_signed_diff_at(jd))

        candidates: list[tuple[float, float]] = [(best_t, _sep_at(best_t))]

        # 1. Exact conjunction root via bisection if signed longitude difference changes sign
        grid_pts = sorted({left, right, best_t, *(t for t, _ in samples)})
        grid_vals = [(g, _signed_diff_at(g)) for g in grid_pts]
        for idx in range(len(grid_vals) - 1):
            g0, v0 = grid_vals[idx]
            g1, v1 = grid_vals[idx + 1]
            if v0 == 0.0:
                candidates.append((g0, 0.0))
            elif v1 == 0.0:
                candidates.append((g1, 0.0))
            elif (v0 < 0.0 < v1 or v1 < 0.0 < v0) and abs(v1 - v0) < 90.0:
                lo_b, hi_b = g0, g1
                lo_v = v0
                for _ in range(48):
                    mid_b = 0.5 * (lo_b + hi_b)
                    if hi_b - lo_b <= 1.0e-11:
                        break
                    mid_v = _signed_diff_at(mid_b)
                    if lo_v * mid_v <= 0.0:
                        hi_b = mid_b
                    else:
                        lo_b, lo_v = mid_b, mid_v
                root_jd = 0.5 * (lo_b + hi_b)
                candidates.append((root_jd, _sep_at(root_jd)))

        # 2. Golden Section Search on [max(left, best_t - step_days), min(right, best_t + step_days)]
        inv_phi = (math.sqrt(5.0) - 1.0) / 2.0
        a = max(float(start_jd_tt), best_t - step_days)
        b = min(float(end_jd_tt), best_t + step_days)
        c = b - inv_phi * (b - a)
        d = a + inv_phi * (b - a)
        fc = _sep_at(c)
        fd = _sep_at(d)
        for _ in range(52):
            if b - a <= 1.0e-8:
                break
            if fc <= fd:
                b, d, fd = d, c, fc
                c = b - inv_phi * (b - a)
                fc = _sep_at(c)
            else:
                a, c, fc = c, d, fd
                d = a + inv_phi * (b - a)
                fd = _sep_at(d)
        cand_jd = 0.5 * (a + b)
        candidates.append((cand_jd, _sep_at(cand_jd)))

        refined_jd, min_sep = min(candidates, key=lambda item: item[1])
        refined_snap = {
            body_a_key: _planet_apparent_at(body_a_key, refined_jd),
            body_b_key: _planet_apparent_at(body_b_key, refined_jd),
        }
        refined_wars = evaluate_graha_yuddha(
            refined_snap,
            max_longitude_separation_deg=max(float(max_war_separation_deg), min_sep + 1.0e-3),
        )
        for rw in refined_wars:
            if (rw.body_a, rw.body_b) == pair:
                return refined_jd, rw
        return refined_jd, best_w

    refined_encounters = [
        _refine_war_encounter_minimum(pair, samples)
        for pair, samples in completed_encounters
    ]

    war_list: list[Mapping[str, Any]] = []
    for war_jd, w in sorted(refined_encounters, key=lambda item: item[0]):
        war_list.append(
            {
                "body_a": w.body_a,
                "body_b": w.body_b,
                "jd_tt": round(war_jd, 8),
                "iso_utc": _jd_tt_to_iso_utc(war_jd),
                "winner": w.winner,
                "loser": w.loser,
                "victory_criterion": w.victory_criterion,
                "separation_deg": round(w.longitude_separation_deg, 6),
                "latitude_separation_deg": round(w.latitude_separation_deg, 6),
                "northern_body": w.northern_body,
                "brighter_body": w.brighter_body,
                "ephemeris_source": _epoch_source(war_jd),
                "receipt_sha256": w.receipt_sha256,
            }
        )
    war_dicts = tuple(war_list)

    stations_list: list[Mapping[str, Any]] = []
    combustion_list: list[Mapping[str, Any]] = []
    provider_arg = None if is_monkeypatched else _hybrid_position_provider
    for body in normalized_bodies:
        st_events = find_retrograde_stations(
            body,
            float(start_jd_tt),
            float(end_jd_tt),
            position_provider=provider_arg,
            ayanamsa=ayanamsa,
            compute_shadow_periods=False,
        )
        for st in st_events:
            stations_list.append(
                {
                    "body": st.body,
                    "jd_tt": round(st.jd_tt, 8),
                    "iso_utc": _jd_tt_to_iso_utc(st.jd_tt),
                    "station_type": st.kind,
                    "longitude_deg": round(st.longitude_deg, 6),
                    "sidereal_longitude_deg": round(st.sidereal_longitude_deg, 6),
                    "rasi": varga_sign(st.sidereal_longitude_deg, "D1").sign_name,
                    "ephemeris_source": _epoch_source(st.jd_tt),
                    "receipt_sha256": st.receipt_sha256,
                }
            )
        cb_windows = find_combustion_windows(
            body,
            float(start_jd_tt),
            float(end_jd_tt),
            position_provider=provider_arg,
        )
        for cb in cb_windows:
            combustion_list.append(
                {
                    "body": cb.body,
                    "ingress_jd_tt": round(cb.start_jd_tt, 8),
                    "ingress_iso_utc": _jd_tt_to_iso_utc(cb.start_jd_tt),
                    "min_elongation_jd_tt": round(cb.min_separation_jd_tt, 8),
                    "egress_jd_tt": round(cb.end_jd_tt, 8),
                    "egress_iso_utc": _jd_tt_to_iso_utc(cb.end_jd_tt),
                    "min_elongation_deg": round(cb.min_separation_deg, 6),
                    "has_cazimi": cb.cazimi_occurred,
                    "duration_days": round(cb.duration_days, 4),
                    "ephemeris_source": _epoch_source(cb.min_separation_jd_tt),
                    "receipt_sha256": cb.receipt_sha256,
                }
            )
    stations_list.sort(key=lambda item: float(item["jd_tt"]))
    combustion_list.sort(key=lambda item: float(item["ingress_jd_tt"]))

    if used_numerical and used_analytical:
        ephemeris_source = "hybrid-compact-de440-and-analytical-fallback"
    elif used_numerical:
        ephemeris_source = "compact-de440-numerical"
    else:
        ephemeris_source = "analytical-keplerian-fallback"

    receipt = {
        "module": "ephemeris_oss.impossible_astrology.rare_phenomena",
        "version": __version__,
        "start_jd_tt": round(float(start_jd_tt), 8),
        "end_jd_tt": round(float(end_jd_tt), 8),
        "ayanamsa": ayanamsa,
        "ephemeris_source": ephemeris_source,
        "max_war_separation_deg": round(float(max_war_separation_deg), 6),
        "bodies": normalized_bodies,
        "graha_yuddha_count": len(war_dicts),
        "retrograde_station_count": len(stations_list),
        "combustion_window_count": len(combustion_list),
        "graha_yuddha_events": list(war_dicts),
        "retrograde_stations": list(stations_list),
        "combustion_windows": list(combustion_list),
    }
    return MultiCenturyPhenomenaReport(
        start_jd_tt=float(start_jd_tt),
        end_jd_tt=float(end_jd_tt),
        start_iso_utc=_jd_tt_to_iso_utc(float(start_jd_tt)),
        end_iso_utc=_jd_tt_to_iso_utc(float(end_jd_tt)),
        ayanamsa=ayanamsa,
        bodies=normalized_bodies,
        graha_yuddha_count=len(war_dicts),
        retrograde_station_count=len(stations_list),
        combustion_window_count=len(combustion_list),
        graha_yuddha_events=war_dicts,
        retrograde_stations=tuple(stations_list),
        combustion_windows=tuple(combustion_list),
        receipt=receipt,
        receipt_sha256=canonical_hash(receipt),
        ephemeris_source=ephemeris_source,
    )


def analyze_siddhanta_vs_jpl_de440_drift(
    jd_ut: float,
    *,
    ayanamsa: str = "lahiri",
    adapter: EphemerisAdapter | None = None,
) -> SiddhantaDriftAnalysisReport:
    """Compare classical *Surya Siddhanta* (epicyclic *Manda* + *Sighra Samskara* from
    the ``3102 BCE`` Kali Yuga epoch) against modern *Drig-Ganita* (embedded NASA JPL DE440
    Chebyshev in ``1550..2306 CE`` or historical Vondrak-2011 + analytical outside).
    """
    ad = adapter if adapter is not None else EphemerisAdapter()
    modern_lons: dict[str, float] = {}
    for body_key in VEDIC_NINE_GRAHAS:
        pos = ad.calc_ut(float(jd_ut), body_key, sidereal=True, ayanamsa=ayanamsa)
        modern_lons[body_key] = pos.longitude_deg
    ephem_source = "de440-chebyshev" if 2287184.5 <= float(jd_ut) <= 2563392.5 else "vondrak2011-analytical"

    comparison: SiddhantaModernComparison = compare_siddhanta_with_modern(
        float(jd_ut),
        modern_lons,
    )
    spashta = surya_siddhanta_true_positions(float(jd_ut))

    planet_rows: dict[str, Mapping[str, Any]] = {}
    min_body = "sun"
    max_body = "sun"
    min_val = float("inf")
    max_val = -1.0

    for body, comp in comparison.comparisons.items():
        sp_pos = spashta.planets[body]
        if comp.abs_delta_deg < min_val:
            min_val = comp.abs_delta_deg
            min_body = body
        if comp.abs_delta_deg > max_val:
            max_val = comp.abs_delta_deg
            max_body = body
        planet_rows[body] = {
            "body": body,
            "siddhanta_true_longitude_deg": round(comp.siddhanta_longitude_deg, 6),
            "modern_drig_ganita_longitude_deg": round(comp.modern_longitude_deg, 6),
            "signed_delta_deg": round(comp.signed_delta_deg, 6),
            "abs_delta_deg": round(comp.abs_delta_deg, 6),
            "delta_arcminutes": round(comp.delta_arcminutes, 4),
            "siddhanta_mean_longitude_deg": round(comp.mean_longitude_deg, 6),
            "manda_phala_deg": round(comp.manda_phala_deg, 6),
            "sighra_phala_deg": round(comp.sighra_phala_deg, 6),
            "siddhanta_rasi": sp_pos.rasi_name,
            "modern_rasi": varga_sign(comp.modern_longitude_deg, "D1").sign_name,
            "rasi_agrees": sp_pos.rasi_name == varga_sign(comp.modern_longitude_deg, "D1").sign_name,
        }

    receipt = {
        "module": "ephemeris_oss.impossible_astrology.siddhanta_drift",
        "version": __version__,
        "jd_ut": round(float(jd_ut), 10),
        "ahargana_days": round(float(comparison.ahargana), 6),
        "ayanamsa": ayanamsa,
        "ephemeris_source": ephem_source,
        "mean_abs_delta_deg": round(float(comparison.mean_abs_delta_deg), 6),
        "max_abs_delta_deg": round(float(comparison.max_abs_delta_deg), 6),
        "min_abs_delta_body": min_body,
        "max_abs_delta_body": max_body,
        "planet_comparisons": planet_rows,
        "comparison_receipt_sha256": comparison.receipt_sha256,
    }
    return SiddhantaDriftAnalysisReport(
        jd_ut=float(jd_ut),
        iso_utc=jd_to_iso_utc(float(jd_ut)),
        ahargana_days=float(comparison.ahargana),
        ayanamsa=ayanamsa,
        ephemeris_source=ephem_source,
        mean_abs_delta_deg=round(float(comparison.mean_abs_delta_deg), 6),
        max_abs_delta_deg=round(float(comparison.max_abs_delta_deg), 6),
        min_abs_delta_body=min_body,
        max_abs_delta_body=max_body,
        planet_comparisons=planet_rows,
        receipt=receipt,
        receipt_sha256=canonical_hash(receipt),
    )


_KAKSHA_LORDS_8: tuple[str, ...] = (
    "Saturn",
    "Jupiter",
    "Mars",
    "Sun",
    "Venus",
    "Mercury",
    "Moon",
    "Lagna",
)

_VARGA_LIFE_DOMAINS: Mapping[str, str] = {
    "D1": "identity_and_physical_vitality",
    "D2": "wealth_and_sustenance",
    "D3": "courage_and_siblings",
    "D4": "property_home_and_fortune",
    "D7": "progeny_and_creative_legacy",
    "D9": "dharma_marriage_and_inner_fruit",
    "D10": "career_vocation_and_public_impact",
    "D12": "ancestry_and_parents",
    "D16": "conveyances_and_inner_contentment",
    "D20": "spiritual_sadhanas_and_devotion",
    "D24": "higher_learning_and_vidya",
    "D27": "intrinsic_strengths_and_stamina",
    "D30": "resilience_and_crisis_thresholds",
    "D40": "matrilineal_auspiciousness",
    "D45": "patrilineal_ethics_and_character",
    "D60": "past_life_karmic_root_shashtiamsa",
}


@dataclass(frozen=True)
class PersonalizedAstroFingerprintReport:
    """Multi-dimensional, birth-clock-calibrated, topocentric personal astrological fingerprint."""

    jd_ut: float
    iso_utc: str
    query_jd_ut: float
    query_iso_utc: str
    latitude_deg: float
    longitude_deg: float
    ayanamsa: str
    ayanamsa_deg: float
    true_node: bool
    birth_time_uncertainty_seconds: float
    ephemeris_source: str
    fingerprint_id_sha256: str
    atmakaraka_planet: str
    amatyakaraka_planet: str
    dominant_vimshopaka_planet: str
    dominant_digbala_planet: str
    overall_clock_confidence_score: float
    overall_personal_transit_resonance_score: float
    harmonic_phase_matrix: Mapping[str, Mapping[str, Any]]
    domain_clock_confidence: Mapping[str, Mapping[str, Any]]
    topocentric_digbala_vector: Mapping[str, Mapping[str, Any]]
    personal_transit_resonance: Mapping[str, Mapping[str, Any]]
    receipt: Mapping[str, Any]
    receipt_sha256: str

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def compute_personalized_astro_fingerprint(
    jd_ut: float,
    latitude_deg: float = 28.6139,
    longitude_deg: float = 77.2090,
    *,
    query_jd_ut: float | None = None,
    birth_time_uncertainty_seconds: float = 60.0,
    ayanamsa: str = "lahiri",
    true_node: bool = False,
    adapter: EphemerisAdapter | None = None,
) -> PersonalizedAstroFingerprintReport:
    """Compute a personalized, non-generic astrological fingerprint combining:
    1. Continuous 16-Varga Harmonic Phase Vector & 20-point Shodashvarga Vimshopaka alignment.
    2. 16-Domain Birth-Clock Sensitivity & Prediction Confidence Decay ``exp(-sigma_t / tau_min)``.
    3. Continuous Topocentric Horizon-Meridian Digbala Vector (0..60 Virupas).
    4. Personal Natal-to-Transit 8-Kaksha (3 deg 45 arcmin) & 337-Bindu Ashtakavarga Resonance.
    """
    sigma_t = float(birth_time_uncertainty_seconds)
    if not math.isfinite(sigma_t) or sigma_t < 0.0:
        raise ValueError("birth_time_uncertainty_seconds must be a finite non-negative number")

    ad = adapter if adapter is not None else EphemerisAdapter()
    base_jd = float(jd_ut)
    q_jd = float(query_jd_ut) if query_jd_ut is not None else base_jd
    lat = float(latitude_deg)
    lon = float(longitude_deg)

    cusp_report = solve_subsecond_shodashvarga_cusp_transitions(
        base_jd,
        lat,
        lon,
        ayanamsa=ayanamsa,
        true_node=bool(true_node),
        adapter=ad,
    )
    houses_res = ad.houses_ut(base_jd, lat, lon, system="whole_sign", ayanamsa=ayanamsa)
    asc_deg = float(houses_res.ascendant_deg)
    mc_deg = float(houses_res.mc_deg)
    desc_deg = normalize_degrees(asc_deg + 180.0)
    ic_deg = normalize_degrees(mc_deg + 180.0)

    natal_lons_cap: dict[str, float] = {}
    ephemeris_source_str = (
        "de440-chebyshev"
        if COMPACT_EARLY_START_JD <= base_jd <= COMPACT_LATE_END_JD
        else "vondrak2011-analytical"
    )
    for body_key in VEDIC_NINE_GRAHAS:
        pos = ad.calc_ut(base_jd, body_key, sidereal=True, ayanamsa=ayanamsa, true_node=true_node)
        natal_lons_cap[body_key.capitalize()] = float(pos.longitude_deg)

    # 1. Continuous 16-Varga Harmonic Phase Matrix & Vimshopaka Bala
    harmonic_phase_matrix: dict[str, Mapping[str, Any]] = {}
    best_vim_planet = "Sun"
    best_vim_score = -1.0

    all_bodies_for_phase = ("Ascendant",) + tuple(b.capitalize() for b in VEDIC_NINE_GRAHAS)
    for b_name in all_bodies_for_phase:
        b_lon = asc_deg if b_name == "Ascendant" else natal_lons_cap[b_name]
        b_margins = (
            cusp_report.ascendant_margins
            if b_name == "Ascendant"
            else cusp_report.planet_margins[b_name]
        )
        varga_phases: dict[str, Mapping[str, Any]] = {}
        phase_stability_sum = 0.0
        for v_key in SHODASHVARGA_KEYS:
            m = b_margins[v_key]
            span = max(float(m.sector_span_deg), 1.0e-9)
            phase = min(max(float(m.degrees_from_lower_cusp) / span, 0.0), 1.0)
            center_stability = math.sin(math.pi * phase)
            phase_stability_sum += center_stability
            varga_phases[v_key] = {
                "sign_name": m.sign_name,
                "sign_lord": m.sign_lord,
                "phase_in_sector": round(phase, 6),
                "center_stability_index": round(center_stability, 6),
                "seconds_to_nearest_cusp": round(
                    min(float(m.seconds_to_previous_cusp), float(m.seconds_to_next_cusp)),
                    4,
                ),
            }

        vim_score_val: float | None = None
        vim_pct_val: float | None = None
        if b_name in ("Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn"):
            vim = compute_vimshopaka_bala(b_name, b_lon, natal_lons_cap, scheme="shodashvarga")
            vim_score_val = round(float(vim.total_score), 6)
            vim_pct_val = round(float(vim.percentage), 4)
            if vim_score_val > best_vim_score:
                best_vim_score = vim_score_val
                best_vim_planet = b_name

        harmonic_phase_matrix[b_name] = {
            "sidereal_longitude_deg": round(b_lon, 8),
            "d1_rasi": varga_sign(b_lon, "D1").sign_name,
            "d9_navamsa": varga_sign(b_lon, "D9").sign_name,
            "d60_shashtiamsa_name": b_margins["D60"].shashtiamsa_name,
            "d60_shashtiamsa_is_benefic": b_margins["D60"].shashtiamsa_is_benefic,
            "is_vargottama": is_vargottama(b_lon),
            "is_pushkara_navamsa": is_pushkara_navamsa(b_lon),
            "is_pushkara_bhaga": is_pushkara_bhaga(b_lon),
            "mean_16varga_center_stability": round(phase_stability_sum / 16.0, 6),
            "shodashvarga_vimshopaka_score_20": vim_score_val,
            "shodashvarga_vimshopaka_pct": vim_pct_val,
            "varga_phases": varga_phases,
        }

    # 2. 16-Domain Clock-Sensitivity & Prediction Confidence Decay
    domain_clock_confidence: dict[str, Mapping[str, Any]] = {}
    conf_sum = 0.0
    for v_key in SHODASHVARGA_KEYS:
        asc_m = cusp_report.ascendant_margins[v_key]
        moon_m = cusp_report.planet_margins["Moon"][v_key]
        asc_tau = min(float(asc_m.seconds_to_previous_cusp), float(asc_m.seconds_to_next_cusp))
        moon_tau = min(float(moon_m.seconds_to_previous_cusp), float(moon_m.seconds_to_next_cusp))
        tau_min = min(asc_tau, moon_tau)
        conf = 1.0 if sigma_t == 0.0 else math.exp(-sigma_t / max(tau_min, 1.0e-3))
        conf_sum += conf
        if tau_min >= 3.0 * sigma_t:
            status = "LOCKED_INVARIANT"
        elif tau_min >= sigma_t:
            status = "MODERATELY_SENSITIVE"
        else:
            status = "RECTIFICATION_REQUIRED"
        domain_clock_confidence[v_key] = {
            "varga": v_key,
            "life_domain": _VARGA_LIFE_DOMAINS[v_key],
            "ascendant_sign": asc_m.sign_name,
            "ascendant_cusp_margin_seconds": round(asc_tau, 4),
            "moon_cusp_margin_seconds": round(moon_tau, 4),
            "governing_cusp_margin_seconds": round(tau_min, 4),
            "clock_confidence_score": round(conf, 6),
            "stability_classification": status,
        }

    overall_clock_conf = round(conf_sum / 16.0, 6)

    # 3. Continuous Topocentric Horizon-Meridian Digbala Vector (0..60 Virupas)
    # Power poles: East/Lagna (Jupiter, Mercury), South/MC (Sun, Mars), West/Desc (Saturn), North/IC (Moon, Venus)
    digbala_poles: Mapping[str, tuple[str, float]] = {
        "Sun": ("MC_South_Meridian", mc_deg),
        "Moon": ("IC_North_Nadir", ic_deg),
        "Mars": ("MC_South_Meridian", mc_deg),
        "Mercury": ("Ascendant_East_Horizon", asc_deg),
        "Jupiter": ("Ascendant_East_Horizon", asc_deg),
        "Venus": ("IC_North_Nadir", ic_deg),
        "Saturn": ("Descendant_West_Horizon", desc_deg),
    }
    topocentric_digbala_vector: dict[str, Mapping[str, Any]] = {}
    best_dig_planet = "Sun"
    best_dig_virupas = -1.0
    for p_name, (pole_label, pole_deg) in digbala_poles.items():
        p_lon = natal_lons_cap[p_name]
        raw_diff = abs(normalize_degrees(p_lon - pole_deg))
        ang_dist = 360.0 - raw_diff if raw_diff > 180.0 else raw_diff
        cosine_idx = 0.5 * (1.0 + math.cos(math.radians(ang_dist)))
        linear_virupas = (180.0 - ang_dist) / 3.0
        cosine_virupas = cosine_idx * 60.0
        if cosine_virupas > best_dig_virupas:
            best_dig_virupas = cosine_virupas
            best_dig_planet = p_name
        topocentric_digbala_vector[p_name] = {
            "power_pole": pole_label,
            "pole_longitude_deg": round(pole_deg, 6),
            "planet_longitude_deg": round(p_lon, 6),
            "angular_distance_from_pole_deg": round(ang_dist, 6),
            "continuous_cosine_index": round(cosine_idx, 6),
            "continuous_cosine_virupas": round(cosine_virupas, 4),
            "classical_linear_virupas": round(linear_virupas, 4),
        }

    # 4. Personal Natal-to-Transit 8-Kaksha (3 deg 45 arcmin) & 337-Bindu Ashtakavarga Resonance
    karakas = compute_chara_karakas(natal_lons_cap, scheme="7")
    atmakaraka_planet = karakas[0].planet
    amatyakaraka_planet = karakas[1].planet
    ak_lon = natal_lons_cap[atmakaraka_planet]
    natal_moon_lon = natal_lons_cap["Moon"]

    ashtaka = compute_ashtakavarga(natal_lons_cap, asc_deg)
    transit_lons_cap: dict[str, float] = {}
    for body_key in ("sun", "moon", "mars", "mercury", "jupiter", "venus", "saturn"):
        t_pos = ad.calc_ut(q_jd, body_key, sidereal=True, ayanamsa=ayanamsa, true_node=true_node)
        transit_lons_cap[body_key.capitalize()] = float(t_pos.longitude_deg)

    gochara_map = evaluate_gochara_vedha(natal_moon_lon, transit_lons_cap, ashtakavarga=ashtaka)
    personal_transit_resonance: dict[str, Mapping[str, Any]] = {}
    res_sum = 0.0

    for p_name in ("Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn"):
        t_lon = transit_lons_cap[p_name]
        s_idx = min(int(t_lon // 30.0), 11)
        deg_in_sign = t_lon - s_idx * 30.0
        kaksha_idx = min(int(deg_in_sign // 3.75), 7)  # 8 Kakshas of 3.75 deg (3 deg 45 arcmin) each
        kaksha_lord = _KAKSHA_LORDS_8[kaksha_idx]
        bav_table = ashtaka.bhinna_tables[p_name]
        bav_bindus = int(bav_table.sign_bindus[s_idx])
        sav_bindus = int(ashtaka.sarvashtakavarga_7[s_idx])
        kaksha_has_bindu = bool(bav_table.contributor_matrix[kaksha_lord][s_idx] == 1)
        goch = gochara_map[p_name]

        # Angular resonance to seeker's Atmakaraka, Natal Moon, and Natal Ascendant (trine/conjunction/opposition harmonics)
        def _harmonic_alignment(lon_a: float, lon_b: float) -> float:
            diff = abs(normalize_degrees(lon_a - lon_b))
            sep = 360.0 - diff if diff > 180.0 else diff
            # Proximity to 0, 60, 120, 180 deg major harmonic angles
            nearest_harm = min(abs(sep - h) for h in (0.0, 60.0, 120.0, 180.0))
            return math.exp(-nearest_harm / 15.0)

        ak_align = _harmonic_alignment(t_lon, ak_lon)
        moon_align = _harmonic_alignment(t_lon, natal_moon_lon)
        asc_align = _harmonic_alignment(t_lon, asc_deg)
        personal_point_alignment = (0.45 * ak_align) + (0.35 * moon_align) + (0.20 * asc_align)

        # Composite 0..100 score combining BAV/8, SAV/56, Kaksha bindu activation, Gochara net favorability, and personal harmonic alignment
        bav_norm = bav_bindus / 8.0
        sav_norm = min(sav_bindus / 40.0, 1.0)
        kaksha_bonus = 1.0 if kaksha_has_bindu else 0.25
        vedha_factor = 1.0 if goch.net_favorable else (0.45 if goch.is_obstructed_by_vedha else 0.70)
        planet_res_score = 100.0 * (
            0.30 * bav_norm
            + 0.25 * sav_norm
            + 0.20 * kaksha_bonus
            + 0.15 * personal_point_alignment
            + 0.10 * vedha_factor
        )
        res_sum += planet_res_score

        personal_transit_resonance[p_name] = {
            "transit_longitude_deg": round(t_lon, 6),
            "transit_rasi": goch.transit_sign_name,
            "transit_nakshatra": nakshatra_position(t_lon).name,
            "house_from_natal_moon": goch.house_from_moon,
            "kaksha_number_1_to_8": kaksha_idx + 1,
            "kaksha_lord": kaksha_lord,
            "kaksha_has_bindu": kaksha_has_bindu,
            "bhinna_ashtakavarga_bindus_0_to_8": bav_bindus,
            "sarvashtakavarga_bindus_in_sign": sav_bindus,
            "gochara_naturally_benefic": goch.is_naturally_benefic_house,
            "gochara_obstructed_by_vedha": goch.is_obstructed_by_vedha,
            "gochara_net_favorable": goch.net_favorable,
            "personal_point_harmonic_alignment": round(personal_point_alignment, 6),
            "resonance_score_0_to_100": round(planet_res_score, 4),
        }

    overall_res_score = round(res_sum / 7.0, 4)

    fingerprint_core = {
        "jd_ut": round(base_jd, 10),
        "latitude_deg": round(lat, 6),
        "longitude_deg": round(lon, 6),
        "ayanamsa": ayanamsa,
        "true_node": bool(true_node),
        "ascendant_deg": round(asc_deg, 8),
        "mc_deg": round(mc_deg, 8),
        "natal_longitudes": {k: round(v, 8) for k, v in sorted(natal_lons_cap.items())},
    }
    fingerprint_id = canonical_hash(fingerprint_core)

    receipt = {
        "module": "ephemeris_oss.impossible_astrology.personalized_fingerprint",
        "version": __version__,
        "jd_ut": round(base_jd, 10),
        "query_jd_ut": round(q_jd, 10),
        "latitude_deg": round(lat, 6),
        "longitude_deg": round(lon, 6),
        "ayanamsa": ayanamsa,
        "true_node": bool(true_node),
        "birth_time_uncertainty_seconds": round(sigma_t, 4),
        "ephemeris_source": ephemeris_source_str,
        "fingerprint_id_sha256": fingerprint_id,
        "atmakaraka_planet": atmakaraka_planet,
        "amatyakaraka_planet": amatyakaraka_planet,
        "dominant_vimshopaka_planet": best_vim_planet,
        "dominant_digbala_planet": best_dig_planet,
        "overall_clock_confidence_score": overall_clock_conf,
        "overall_personal_transit_resonance_score": overall_res_score,
        "cusp_report_receipt_sha256": cusp_report.receipt_sha256,
    }

    return PersonalizedAstroFingerprintReport(
        jd_ut=base_jd,
        iso_utc=jd_to_iso_utc(base_jd),
        query_jd_ut=q_jd,
        query_iso_utc=jd_to_iso_utc(q_jd),
        latitude_deg=lat,
        longitude_deg=lon,
        ayanamsa=ayanamsa,
        ayanamsa_deg=round(float(cusp_report.ayanamsa_deg), 8),
        true_node=bool(true_node),
        birth_time_uncertainty_seconds=sigma_t,
        ephemeris_source=ephemeris_source_str,
        fingerprint_id_sha256=fingerprint_id,
        atmakaraka_planet=atmakaraka_planet,
        amatyakaraka_planet=amatyakaraka_planet,
        dominant_vimshopaka_planet=best_vim_planet,
        dominant_digbala_planet=best_dig_planet,
        overall_clock_confidence_score=overall_clock_conf,
        overall_personal_transit_resonance_score=overall_res_score,
        harmonic_phase_matrix=harmonic_phase_matrix,
        domain_clock_confidence=domain_clock_confidence,
        topocentric_digbala_vector=topocentric_digbala_vector,
        personal_transit_resonance=personal_transit_resonance,
        receipt=receipt,
        receipt_sha256=canonical_hash(receipt),
    )


# ---------------------------------------------------------------------------
# 6. 30-Star Yogatara Stellar Piercing (Tara Bheda / Rohini Shakata Bheda)
#    & Heliacal Visibility (Kalansha Udaya/Asta) Solver
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class YogataraStellarBhedaReport:
    """30-star Gaia/Hipparcos ICRS Yogatara apparent catalog, Tara Bheda, and Rohini Shakata Bheda report."""

    jd_ut: float
    iso_utc: str
    ayanamsa: str
    ayanamsa_deg: float
    orb_deg: float
    ephemeris_source: str
    yogatara_count: int
    visible_star_count: int
    combust_star_count: int
    rohini_shakata_bheda_active: bool
    rohini_shakata_bheda_planets: tuple[str, ...]
    active_tara_bheda_events: tuple[Mapping[str, Any], ...]
    yogatara_states: tuple[Mapping[str, Any], ...]
    receipt: Mapping[str, Any]
    receipt_sha256: str

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def evaluate_yogatara_stellar_bheda_and_visibility(
    jd_ut: float,
    *,
    ayanamsa: str = "lahiri",
    orb_deg: float = 1.5,
    true_node: bool = False,
    adapter: EphemerisAdapter | None = None,
) -> YogataraStellarBhedaReport:
    """Propagate all 30 Yogataras relativistically via IAU SOFA/ERFA and detect:

    1. Apparent tropical and sidereal ecliptic coordinates of all 27 Nakshatra
       Yogataras + 28th Abhijit (Vega) + Agastya (Canopus) + Lubdhaka (Sirius).
    2. Heliacal visibility state (*Udaya* visible vs *Asta* solar combustion)
       against each star's classical *Surya Siddhanta Kalansha* arc.
    3. *Tara Bheda* (planetary-stellar longitudinal conjunction & ecliptic
       latitude piercing) and **Rohini Shakata Bheda** (*Brihat Samhita* Ch. 9:
       when Saturn, Mars, or Rahu transits Rohini near Aldebaran and pierces the
       Hyades cart asterism).
    """
    ad = adapter if adapter is not None else EphemerisAdapter()
    base_jd = float(jd_ut)
    max_orb = max(float(orb_deg), 0.05)
    jd_tt = ad._jd_ut_to_jd_tt(base_jd)
    ayan_deg = float(ad.get_ayanamsa_ut(base_jd, mode=ayanamsa))
    ephem_source = (
        "de440-chebyshev"
        if COMPACT_EARLY_START_JD <= base_jd <= COMPACT_LATE_END_JD
        else "vondrak2011-analytical"
    )

    planet_coords: dict[str, tuple[float, float, float]] = {}
    for body_key in VEDIC_NINE_GRAHAS:
        pos = ad.calc_ut(base_jd, body_key, sidereal=True, ayanamsa=ayanamsa, true_node=true_node)
        planet_coords[body_key.capitalize()] = (
            float(pos.longitude_deg),
            float(pos.latitude_deg),
            float(pos.longitude_speed_deg_per_day),
        )

    sun_sid_lon = planet_coords["Sun"][0]
    sun_trop_lon = normalize_degrees(sun_sid_lon + ayan_deg)
    tt_pair = (2451545.0, jd_tt - 2451545.0)
    yogatara_states: list[Mapping[str, Any]] = []
    bheda_events: list[Mapping[str, Any]] = []
    rohini_bheda_planets: list[str] = []
    visible_count = 0
    combust_count = 0

    for star in YOGATARA_30_CATALOG:
        star_pos = propagate_yogatara_apparent(
            star,
            tt=tt_pair,
            ayanamsa_deg=ayan_deg,
            sun_tropical_lon_deg=sun_trop_lon,
        )
        trop_lon = float(star_pos.tropical_longitude_deg)
        trop_lat = float(star_pos.ecliptic_latitude_shara_deg)
        sid_lon = float(star_pos.sidereal_longitude_deg)
        solar_elong_deg = float(star_pos.solar_elongation_deg)
        is_combust = not bool(star_pos.is_heliacally_visible)
        if is_combust:
            combust_count += 1
        else:
            visible_count += 1

        star_row = {
            "key": star.key,
            "nakshatra_number": star.nakshatra_number,
            "vedic_name": star.vedic_name,
            "western_designation": star.western_designation,
            "hip_id": star.hip_id,
            "visual_magnitude": star.visual_magnitude,
            "tropical_longitude_deg": round(trop_lon, 6),
            "sidereal_longitude_deg": round(sid_lon, 6),
            "ecliptic_latitude_deg": round(trop_lat, 6),
            "rasi_name": RASI_NAMES[min(int(sid_lon // 30.0), 11)],
            "solar_elongation_deg": round(solar_elong_deg, 4),
            "kalansha_threshold_deg": star.kalansha_visibility_arc_deg,
            "visibility_state": "Asta_Combust" if is_combust else "Udaya_Visible",
        }
        yogatara_states.append(star_row)

        for p_name, (p_lon, p_lat, p_speed) in planet_coords.items():
            if p_name == "Sun":
                continue
            dlon_raw = abs(normalize_degrees(p_lon - sid_lon))
            dlon = 360.0 - dlon_raw if dlon_raw > 180.0 else dlon_raw
            if dlon <= max_orb:
                dlat = abs(p_lat - trop_lat)
                angular_sep = math.hypot(dlon, dlat)
                is_lat_piercing = bool(dlat <= 1.0)
                is_rohini_shakata = bool(
                    star.key == "rohini"
                    and p_name in ("Saturn", "Mars", "Rahu")
                    and dlon <= max(max_orb, 2.0)
                )
                if is_rohini_shakata and p_name not in rohini_bheda_planets:
                    rohini_bheda_planets.append(p_name)
                bheda_events.append(
                    {
                        "yogatara_key": star.key,
                        "vedic_name": star.vedic_name,
                        "star_designation": star.western_designation,
                        "planet": p_name,
                        "planet_sidereal_longitude_deg": round(p_lon, 6),
                        "star_sidereal_longitude_deg": round(sid_lon, 6),
                        "longitude_separation_deg": round(dlon, 6),
                        "latitude_separation_deg": round(dlat, 6),
                        "total_angular_separation_deg": round(angular_sep, 6),
                        "is_direct_latitude_bheda": is_lat_piercing,
                        "is_rohini_shakata_bheda": is_rohini_shakata,
                        "planet_is_retrograde": bool(p_speed < 0.0),
                    }
                )

    # Also check broader Rohini Nakshatra span (40..53.333 deg Taurus) for classical Rohini Shakata Bheda
    for malefic in ("Saturn", "Mars", "Rahu"):
        m_lon, m_lat, _ = planet_coords[malefic]
        if 45.0 <= m_lon <= 52.5 and -6.5 <= m_lat <= -1.0:
            if malefic not in rohini_bheda_planets:
                rohini_bheda_planets.append(malefic)

    receipt = {
        "module": "ephemeris_oss.impossible_astrology.yogatara_stellar_bheda",
        "version": __version__,
        "jd_ut": round(base_jd, 9),
        "ayanamsa": ayanamsa,
        "ayanamsa_deg": round(ayan_deg, 8),
        "orb_deg": round(max_orb, 6),
        "ephemeris_source": ephem_source,
        "yogatara_count": len(yogatara_states),
        "visible_star_count": visible_count,
        "combust_star_count": combust_count,
        "rohini_shakata_bheda_active": bool(rohini_bheda_planets),
        "active_bheda_count": len(bheda_events),
    }
    return YogataraStellarBhedaReport(
        jd_ut=base_jd,
        iso_utc=jd_to_iso_utc(base_jd),
        ayanamsa=ayanamsa,
        ayanamsa_deg=round(ayan_deg, 8),
        orb_deg=max_orb,
        ephemeris_source=ephem_source,
        yogatara_count=len(yogatara_states),
        visible_star_count=visible_count,
        combust_star_count=combust_count,
        rohini_shakata_bheda_active=bool(rohini_bheda_planets),
        rohini_shakata_bheda_planets=tuple(rohini_bheda_planets),
        active_tara_bheda_events=tuple(bheda_events),
        yogatara_states=tuple(yogatara_states),
        receipt=receipt,
        receipt_sha256=canonical_hash(receipt),
    )


# ---------------------------------------------------------------------------
# 7. Exact Krantisamya (Vyatipata & Vaidhriti Mahapata) Declination-Equality Solver
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class KrantisamyaMahapataEvent:
    """Single exact solar-lunar declination equality (*Krantisamya Mahapata*) event."""

    mahapata_type: str  # "Vyatipata" (same declination, opposite solstice) or "Vaidhriti" (opposite declination)
    exact_jd_ut: float
    exact_iso_utc: str
    window_start_jd_ut: float
    window_end_jd_ut: float
    duration_minutes: float
    sun_declination_deg: float
    moon_declination_deg: float
    sun_sidereal_longitude_deg: float
    moon_sidereal_longitude_deg: float
    tropical_longitude_sum_deg: float


@dataclass(frozen=True)
class KrantisamyaMahapataReport:
    """Report of all exact Vyatipata and Vaidhriti Mahapata windows in a time span."""

    start_jd_ut: float
    end_jd_ut: float
    start_iso_utc: str
    end_iso_utc: str
    event_count: int
    events: tuple[KrantisamyaMahapataEvent, ...]
    receipt: Mapping[str, Any]
    receipt_sha256: str

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def solve_krantisamya_mahapata_windows(
    start_jd_ut: float,
    end_jd_ut: float,
    *,
    step_hours: float = 6.0,
    ayanamsa: str = "lahiri",
    adapter: EphemerisAdapter | None = None,
) -> KrantisamyaMahapataReport:
    """Solve exact *Surya Siddhanta* (Ch. 11, *Pata Adhikara*) *Krantisamya Mahapata* events:

    - **Vyatipata Mahapata:** Sun and Moon have equal apparent equatorial declination
      in the **same hemisphere** (``dec_Sun == +dec_Moon``) while moving in opposite
      solstitial directions (``trop_lon_Sun + trop_lon_Moon ~= 180 deg``).
    - **Vaidhriti Mahapata:** Sun and Moon have equal apparent equatorial declination
      magnitude in **opposite hemispheres** (``dec_Sun == -dec_Moon``) while
      ``trop_lon_Sun + trop_lon_Moon ~= 360 deg``.
    """
    t0 = float(start_jd_ut)
    t1 = float(end_jd_ut)
    if t1 <= t0:
        raise ValueError("end_jd_ut must be greater than start_jd_ut")
    ad = adapter if adapter is not None else EphemerisAdapter()
    dt_days = max(float(step_hours) / 24.0, 0.02)

    def _equatorial_declinations_and_sum(j_ut: float) -> tuple[float, float, float, float, float]:
        sun_tr = ad.calc_ut(j_ut, "sun", sidereal=False)
        moon_tr = ad.calc_ut(j_ut, "moon", sidereal=False)
        j_tt = ad._jd_ut_to_jd_tt(j_ut)
        eps_rad = float(erfa.obl06(2451545.0, j_tt - 2451545.0))

        def _ecl_to_dec_deg(lon_deg: float, lat_deg: float) -> float:
            l_rad = math.radians(lon_deg)
            b_rad = math.radians(lat_deg)
            sin_dec = math.sin(b_rad) * math.cos(eps_rad) + math.cos(b_rad) * math.sin(eps_rad) * math.sin(l_rad)
            return math.degrees(math.asin(max(-1.0, min(1.0, sin_dec))))

        dec_sun = _ecl_to_dec_deg(float(sun_tr.longitude_deg), float(sun_tr.latitude_deg))
        dec_moon = _ecl_to_dec_deg(float(moon_tr.longitude_deg), float(moon_tr.latitude_deg))
        trop_sum = normalize_degrees(float(sun_tr.longitude_deg) + float(moon_tr.longitude_deg))
        return dec_sun, dec_moon, trop_sum, float(sun_tr.longitude_deg), float(moon_tr.longitude_deg)

    def _find_root(f_func: Callable[[float], float], a: float, b: float) -> float:
        fa = f_func(a)
        fb = f_func(b)
        left, right = a, b
        for _ in range(36):
            mid = 0.5 * (left + right)
            if (right - left) * 86400.0 <= 0.05:
                return mid
            fm = f_func(mid)
            if fa * fm <= 0.0:
                right = mid
                fb = fm
            else:
                left = mid
                fa = fm
        return 0.5 * (left + right)

    events: list[KrantisamyaMahapataEvent] = []
    curr = t0
    prev_dec_s, prev_dec_m, _, _, _ = _equatorial_declinations_and_sum(curr)
    prev_f_vyatipata = prev_dec_s - prev_dec_m
    prev_f_vaidhriti = prev_dec_s + prev_dec_m

    while curr < t1:
        nxt = min(curr + dt_days, t1)
        dec_s, dec_m, _, _, _ = _equatorial_declinations_and_sum(nxt)
        f_vyatipata = dec_s - dec_m
        f_vaidhriti = dec_s + dec_m

        # Check Vyatipata (dec_Sun - dec_Moon == 0 near trop_sum ~ 180 deg)
        if prev_f_vyatipata * f_vyatipata <= 0.0:
            root_jd = _find_root(
                lambda x: _equatorial_declinations_and_sum(x)[0] - _equatorial_declinations_and_sum(x)[1],
                curr,
                nxt,
            )
            ds, dm, t_sum, s_tr_lon, m_tr_lon = _equatorial_declinations_and_sum(root_jd)
            # Distinguish Vyatipata (trop_sum near 180 deg) from simple conjunction (trop_sum near 0/360)
            if 115.0 <= t_sum <= 245.0:
                ayan_val = ad.get_ayanamsa_ut(root_jd, mode=ayanamsa)
                # Rate of declination separation (~0.22 deg/hour typical) -> half-window for solar+lunar semi-diameter (~0.53 deg)
                dt_probe = 1.0 / 24.0
                ds2, dm2, _, _, _ = _equatorial_declinations_and_sum(root_jd + dt_probe)
                rate_deg_per_day = max(abs((ds2 - dm2) - (ds - dm)) / dt_probe, 0.5)
                half_win_days = 0.53 / rate_deg_per_day
                events.append(
                    KrantisamyaMahapataEvent(
                        mahapata_type="Vyatipata",
                        exact_jd_ut=round(root_jd, 8),
                        exact_iso_utc=jd_to_iso_utc(root_jd),
                        window_start_jd_ut=round(root_jd - half_win_days, 8),
                        window_end_jd_ut=round(root_jd + half_win_days, 8),
                        duration_minutes=round(2.0 * half_win_days * 1440.0, 2),
                        sun_declination_deg=round(ds, 6),
                        moon_declination_deg=round(dm, 6),
                        sun_sidereal_longitude_deg=round(normalize_degrees(s_tr_lon - ayan_val), 6),
                        moon_sidereal_longitude_deg=round(normalize_degrees(m_tr_lon - ayan_val), 6),
                        tropical_longitude_sum_deg=round(t_sum, 4),
                    )
                )

        # Check Vaidhriti (dec_Sun + dec_Moon == 0 near trop_sum ~ 360/0 deg)
        if prev_f_vaidhriti * f_vaidhriti <= 0.0:
            root_jd = _find_root(
                lambda x: _equatorial_declinations_and_sum(x)[0] + _equatorial_declinations_and_sum(x)[1],
                curr,
                nxt,
            )
            ds, dm, t_sum, s_tr_lon, m_tr_lon = _equatorial_declinations_and_sum(root_jd)
            if t_sum >= 295.0 or t_sum <= 65.0:
                ayan_val = ad.get_ayanamsa_ut(root_jd, mode=ayanamsa)
                dt_probe = 1.0 / 24.0
                ds2, dm2, _, _, _ = _equatorial_declinations_and_sum(root_jd + dt_probe)
                rate_deg_per_day = max(abs((ds2 + dm2) - (ds + dm)) / dt_probe, 0.5)
                half_win_days = 0.53 / rate_deg_per_day
                events.append(
                    KrantisamyaMahapataEvent(
                        mahapata_type="Vaidhriti",
                        exact_jd_ut=round(root_jd, 8),
                        exact_iso_utc=jd_to_iso_utc(root_jd),
                        window_start_jd_ut=round(root_jd - half_win_days, 8),
                        window_end_jd_ut=round(root_jd + half_win_days, 8),
                        duration_minutes=round(2.0 * half_win_days * 1440.0, 2),
                        sun_declination_deg=round(ds, 6),
                        moon_declination_deg=round(dm, 6),
                        sun_sidereal_longitude_deg=round(normalize_degrees(s_tr_lon - ayan_val), 6),
                        moon_sidereal_longitude_deg=round(normalize_degrees(m_tr_lon - ayan_val), 6),
                        tropical_longitude_sum_deg=round(t_sum, 4),
                    )
                )

        curr = nxt
        prev_f_vyatipata = f_vyatipata
        prev_f_vaidhriti = f_vaidhriti

    events.sort(key=lambda e: e.exact_jd_ut)
    receipt = {
        "module": "ephemeris_oss.impossible_astrology.krantisamya_mahapata",
        "version": __version__,
        "start_jd_ut": round(t0, 8),
        "end_jd_ut": round(t1, 8),
        "event_count": len(events),
        "events": [asdict(e) for e in events],
    }
    return KrantisamyaMahapataReport(
        start_jd_ut=t0,
        end_jd_ut=t1,
        start_iso_utc=jd_to_iso_utc(t0),
        end_iso_utc=jd_to_iso_utc(t1),
        event_count=len(events),
        events=tuple(events),
        receipt=receipt,
        receipt_sha256=canonical_hash(receipt),
    )


# ---------------------------------------------------------------------------
# 8. Inverse Sky-to-Date "Astronomical Time-Machine" Solver
# ---------------------------------------------------------------------------


_SIGN_LOOKUP: Mapping[str, int] = {
    name.lower(): idx for idx, name in enumerate(RASI_NAMES)
}
_SIGN_SANSKRIT_ALIASES: Mapping[str, int] = {
    "aries": 0,
    "taurus": 1,
    "gemini": 2,
    "cancer": 3,
    "leo": 4,
    "virgo": 5,
    "libra": 6,
    "scorpio": 7,
    "sagittarius": 8,
    "capricorn": 9,
    "aquarius": 10,
    "pisces": 11,
    "mesha": 0,
    "vrishabha": 1,
    "mithuna": 2,
    "karka": 3,
    "karkata": 3,
    "simha": 4,
    "kanya": 5,
    "tula": 6,
    "vrishchika": 7,
    "dhanu": 8,
    "dhanus": 8,
    "makara": 9,
    "kumbha": 10,
    "meena": 11,
}


def _parse_sign_index(val: str | int) -> int:
    if isinstance(val, int) and not isinstance(val, bool):
        if 0 <= val <= 11:
            return val
        if 1 <= val <= 12:
            return val - 1
        raise ValueError(f"Sign integer must be 0..11 (or 1..12), got {val}")
    s = str(val).strip().lower()
    if s in _SIGN_LOOKUP:
        return _SIGN_LOOKUP[s]
    if s in _SIGN_SANSKRIT_ALIASES:
        return _SIGN_SANSKRIT_ALIASES[s]
    for idx, r_name in enumerate(RASI_NAMES):
        if s in r_name.lower():
            return idx
    raise ValueError(f"Unrecognized zodiac sign constraint: {val!r}")


@dataclass(frozen=True)
class InverseChartMatchWindow:
    """Matched historical or future epoch satisfying all planetary sign/nakshatra constraints."""

    matched_jd_ut: float
    matched_iso_utc: str
    window_start_jd_ut: float
    window_end_jd_ut: float
    window_duration_hours: float
    planetary_longitudes_deg: Mapping[str, float]
    planetary_signs: Mapping[str, str]
    planetary_nakshatras: Mapping[str, str]


@dataclass(frozen=True)
class InverseChartDateSearchReport:
    """Result of the Inverse Sky-to-Date 'Astronomical Time-Machine' search."""

    start_year: int
    end_year: int
    start_jd_ut: float
    end_jd_ut: float
    ayanamsa: str
    sign_constraints: Mapping[str, str]
    nakshatra_constraints: Mapping[str, str]
    match_count: int
    matches: tuple[InverseChartMatchWindow, ...]
    receipt: Mapping[str, Any]
    receipt_sha256: str

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def solve_chart_date_from_planetary_constraints(
    start_year: int,
    end_year: int,
    sign_constraints: Mapping[str, str | int],
    *,
    nakshatra_constraints: Mapping[str, str | int] | None = None,
    ayanamsa: str = "lahiri",
    true_node: bool = False,
    max_results: int = 20,
    adapter: EphemerisAdapter | None = None,
) -> InverseChartDateSearchReport:
    """Inverse Sky-to-Date 'Astronomical Time-Machine' Solver (`3102 BCE` to `3000 CE`).

    Given any combination of planetary Rashi (sign) constraints (e.g.,
    ``{"Saturn": "Libra", "Jupiter": "Cancer", "Sun": "Aries", "Moon": "Taurus"}``)
    and optional 27-Nakshatra constraints, searches across years, decades, or
    centuries using a hierarchical orbital-period sieve:
      - Stage 1 (12-day coarse sieve): Filters slow planets (`Saturn`, `Jupiter`, `Rahu`, `Ketu`).
      - Stage 2 (1-day medium sieve): Filters intermediate planets (`Mars`, `Sun`, `Venus`, `Mercury`).
      - Stage 3 (3-hour fine sieve): Resolves fast `Moon` Rashi and Nakshatra windows.
    """
    if not sign_constraints and not nakshatra_constraints:
        raise ValueError("At least one planetary sign or nakshatra constraint must be provided.")
    y0 = int(start_year)
    y1 = int(end_year)
    if y1 < y0:
        raise ValueError("end_year must be >= start_year")

    ad = adapter if adapter is not None else EphemerisAdapter()
    jd_start = max(float(erfa.cal2jd(y0, 1, 1)[0] + erfa.cal2jd(y0, 1, 1)[1]), 588465.5)
    jd_end = min(float(erfa.cal2jd(y1, 12, 31)[0] + erfa.cal2jd(y1, 12, 31)[1] + 0.999), 2817152.5)

    body_alias_map: dict[str, str] = {
        "sun": "sun",
        "surya": "sun",
        "ravi": "sun",
        "moon": "moon",
        "chandra": "moon",
        "soma": "moon",
        "mars": "mars",
        "mangala": "mars",
        "kuja": "mars",
        "mercury": "mercury",
        "budha": "mercury",
        "jupiter": "jupiter",
        "guru": "jupiter",
        "brihaspati": "jupiter",
        "venus": "venus",
        "shukra": "venus",
        "saturn": "saturn",
        "shani": "saturn",
        "rahu": "rahu",
        "mean_node": "rahu",
        "true_node": "rahu",
        "true_rahu": "rahu",
        "ketu": "ketu",
        "true_ketu": "ketu",
        "uranus": "uranus",
        "neptune": "neptune",
        "pluto": "pluto",
    }

    parsed_signs: dict[str, int] = {}
    normalized_sign_names: dict[str, str] = {}
    for body_raw, s_val in (sign_constraints or {}).items():
        b_raw = str(body_raw).strip().lower()
        if b_raw not in body_alias_map:
            raise ValueError(f"Unsupported planetary constraint body: {body_raw!r}")
        b_key = body_alias_map[b_raw]
        s_idx = _parse_sign_index(s_val)
        parsed_signs[b_key] = s_idx
        normalized_sign_names[b_key] = RASI_NAMES[s_idx]

    parsed_naks: dict[str, int] = {}
    normalized_nak_names: dict[str, str] = {}
    for body_raw, n_val in (nakshatra_constraints or {}).items():
        b_raw = str(body_raw).strip().lower()
        if b_raw not in body_alias_map:
            raise ValueError(f"Unsupported planetary constraint body: {body_raw!r}")
        b_key = body_alias_map[b_raw]
        if isinstance(n_val, int) and not isinstance(n_val, bool):
            n_idx = n_val if 0 <= n_val <= 26 else n_val - 1
        else:
            n_str = str(n_val).strip().lower()
            matched_n = None
            for idx, nk_name in enumerate(NAKSHATRA_NAMES):
                if n_str == nk_name.lower() or n_str in nk_name.lower():
                    matched_n = idx
                    break
            if matched_n is None:
                raise ValueError(f"Unrecognized Nakshatra constraint: {n_val!r}")
            n_idx = matched_n
        parsed_naks[b_key] = n_idx
        normalized_nak_names[b_key] = NAKSHATRA_NAMES[n_idx]

    slow_bodies = [
        b
        for b in ("pluto", "neptune", "uranus", "saturn", "jupiter", "rahu", "ketu")
        if b in parsed_signs or b in parsed_naks
    ]
    med_bodies = [b for b in ("mars", "sun", "venus", "mercury") if b in parsed_signs or b in parsed_naks]
    fast_bodies = [b for b in ("moon",) if b in parsed_signs or b in parsed_naks]

    def _body_matches(j_ut: float, b_key: str) -> bool:
        pos = ad.calc_ut(j_ut, b_key, sidereal=True, ayanamsa=ayanamsa, true_node=true_node)
        lon = float(pos.longitude_deg)
        if b_key in parsed_signs and min(int(lon // 30.0), 11) != parsed_signs[b_key]:
            return False
        if b_key in parsed_naks and min(int(lon // (360.0 / 27.0)), 26) != parsed_naks[b_key]:
            return False
        return True

    # Stage 1: Build conservative padded intervals per slow body and intersect so short overlaps (<10d) are preserved
    step1 = 10.0
    if not slow_bodies:
        stage1_intervals: list[tuple[float, float]] = [(jd_start, jd_end)]
    else:
        stage1_intervals = [(jd_start, jd_end)]
        for s_body in slow_bodies:
            b_intervals: list[tuple[float, float]] = []
            t = jd_start
            in_match = False
            win_s = jd_start
            while True:
                ok = _body_matches(t, s_body)
                if ok and not in_match:
                    in_match = True
                    win_s = max(jd_start, t - step1)
                elif not ok and in_match:
                    in_match = False
                    b_intervals.append((win_s, min(jd_end, t + step1)))
                if t >= jd_end:
                    break
                t = min(jd_end, t + step1)
            if in_match:
                b_intervals.append((win_s, jd_end))
            # Intersect stage1_intervals with b_intervals:
            next_intervals: list[tuple[float, float]] = []
            for a0, a1 in stage1_intervals:
                for b0, b1 in b_intervals:
                    lo = max(a0, b0)
                    hi = min(a1, b1)
                    if lo <= hi:
                        if next_intervals and lo <= next_intervals[-1][1]:
                            next_intervals[-1] = (next_intervals[-1][0], max(next_intervals[-1][1], hi))
                        else:
                            next_intervals.append((lo, hi))
            stage1_intervals = next_intervals
            if not stage1_intervals:
                break

    # Stage 2: 1-day intervals inside Stage 1 where medium + slow bodies match
    stage2_intervals: list[tuple[float, float]] = []
    step2 = 1.0
    for s1_start, s1_end in stage1_intervals:
        t = s1_start
        in_m2 = False
        w2_s = s1_start
        while t <= s1_end:
            ok = all(_body_matches(t, b) for b in slow_bodies + med_bodies)
            if ok and not in_m2:
                in_m2 = True
                w2_s = max(s1_start, t - step2)
            elif not ok and in_m2:
                in_m2 = False
                stage2_intervals.append((w2_s, min(s1_end, t + step2)))
            t += step2
        if in_m2:
            stage2_intervals.append((w2_s, s1_end))

    # Stage 3: 0.125-day (3-hour) refinement for fast bodies (Moon) and exact window bounds
    matches: list[InverseChartMatchWindow] = []
    step3 = 0.125 if fast_bodies else 0.5
    all_constrained = slow_bodies + med_bodies + fast_bodies

    for s2_start, s2_end in stage2_intervals:
        if len(matches) >= max_results:
            break
        t = s2_start
        in_m3 = False
        w3_s = s2_start
        last_good = s2_start
        while t <= s2_end:
            ok = all(_body_matches(t, b) for b in all_constrained)
            if ok:
                if not in_m3:
                    in_m3 = True
                    w3_s = t
                last_good = t
            elif in_m3:
                in_m3 = False
                mid_jd = 0.5 * (w3_s + last_good)
                matches.append(_build_inverse_match_window(ad, mid_jd, w3_s, last_good, ayanamsa, true_node))
                if len(matches) >= max_results:
                    break
            t += step3
        if in_m3 and len(matches) < max_results:
            mid_jd = 0.5 * (w3_s + last_good)
            matches.append(_build_inverse_match_window(ad, mid_jd, w3_s, last_good, ayanamsa, true_node))

    receipt = {
        "module": "ephemeris_oss.impossible_astrology.inverse_chart_date_solver",
        "version": __version__,
        "start_year": y0,
        "end_year": y1,
        "ayanamsa": ayanamsa,
        "sign_constraints": normalized_sign_names,
        "nakshatra_constraints": normalized_nak_names,
        "match_count": len(matches),
        "first_match_jd_ut": matches[0].matched_jd_ut if matches else None,
    }
    return InverseChartDateSearchReport(
        start_year=y0,
        end_year=y1,
        start_jd_ut=round(jd_start, 6),
        end_jd_ut=round(jd_end, 6),
        ayanamsa=ayanamsa,
        sign_constraints=normalized_sign_names,
        nakshatra_constraints=normalized_nak_names,
        match_count=len(matches),
        matches=tuple(matches),
        receipt=receipt,
        receipt_sha256=canonical_hash(receipt),
    )


def _build_inverse_match_window(
    ad: EphemerisAdapter,
    mid_jd: float,
    w_start: float,
    w_end: float,
    ayanamsa: str,
    true_node: bool,
) -> InverseChartMatchWindow:
    lons: dict[str, float] = {}
    signs: dict[str, str] = {}
    naks: dict[str, str] = {}
    for b_key in VEDIC_NINE_GRAHAS + ("uranus", "neptune", "pluto"):
        pos = ad.calc_ut(mid_jd, b_key, sidereal=True, ayanamsa=ayanamsa, true_node=true_node)
        lon = float(pos.longitude_deg)
        cap = b_key.capitalize()
        lons[cap] = round(lon, 6)
        signs[cap] = RASI_NAMES[min(int(lon // 30.0), 11)]
        naks[cap] = nakshatra_position(lon).name
    return InverseChartMatchWindow(
        matched_jd_ut=round(mid_jd, 6),
        matched_iso_utc=jd_to_iso_utc(mid_jd),
        window_start_jd_ut=round(w_start, 6),
        window_end_jd_ut=round(w_end, 6),
        window_duration_hours=round(max((w_end - w_start) * 24.0, 3.0), 2),
        planetary_longitudes_deg=lons,
        planetary_signs=signs,
        planetary_nakshatras=naks,
    )


# ---------------------------------------------------------------------------
# 9. Triple-Lock Life-Event Peak Window Convergence Solver
# ---------------------------------------------------------------------------


_LIFE_DOMAIN_CONFIG: Mapping[str, Mapping[str, Any]] = {
    "career": {
        "primary_house": 10,
        "supporting_houses": (10, 1, 6, 11, 9),
        "karaka": "Saturn",
        "secondary_karaka": "Sun",
    },
    "marriage": {
        "primary_house": 7,
        "supporting_houses": (7, 2, 11, 1, 5),
        "karaka": "Venus",
        "secondary_karaka": "Jupiter",
    },
    "wealth": {
        "primary_house": 2,
        "supporting_houses": (2, 11, 5, 9, 1),
        "karaka": "Jupiter",
        "secondary_karaka": "Venus",
    },
    "health_vitality": {
        "primary_house": 1,
        "supporting_houses": (1, 5, 9, 11),
        "karaka": "Sun",
        "secondary_karaka": "Mars",
    },
    "spiritual_awakening": {
        "primary_house": 9,
        "supporting_houses": (9, 12, 5, 8, 4),
        "karaka": "Jupiter",
        "secondary_karaka": "Ketu",
    },
}


@dataclass(frozen=True)
class TripleLockWindowEntry:
    """Single evaluated date in the Triple-Lock Life-Event Convergence scan."""

    jd_ut: float
    iso_utc: str
    lock1_natal_dasha_score_0_to_100: float
    lock2_double_transit_score_0_to_100: float
    lock3_ashtakavarga_kaksha_score_0_to_100: float
    total_convergence_score_0_to_100: float
    is_triple_lock_gold_window: bool
    vimshottari_mahadasha: str
    vimshottari_antardasha: str
    kalachakra_sign: str
    kalachakra_gati: str
    kalachakra_touches_deha_or_jeeva: bool
    chara_dasha_sign: str
    jupiter_aspects_primary_house_or_lord: bool
    saturn_aspects_primary_house_or_lord: bool
    double_transit_locked: bool
    karaka_kaksha_lord: str
    karaka_kaksha_has_bindu: bool
    primary_house_sav_bindus: int
    bhrigu_bindu_triggered: bool


@dataclass(frozen=True)
class TripleLockConvergenceReport:
    """Multi-system Triple-Lock Life-Event Convergence report."""

    birth_jd_ut: float
    birth_iso_utc: str
    start_jd_ut: float
    end_jd_ut: float
    domain: str
    primary_house: int
    primary_house_sign: str
    primary_house_lord: str
    bhrigu_bindu_longitude_deg: float
    kalachakra_deha_sign: str
    kalachakra_jeeva_sign: str
    peak_window: TripleLockWindowEntry
    gold_windows: tuple[TripleLockWindowEntry, ...]
    sampled_timeline: tuple[TripleLockWindowEntry, ...]
    receipt: Mapping[str, Any]
    receipt_sha256: str

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def compute_triple_lock_life_event_convergence(
    birth_jd_ut: float,
    latitude_deg: float,
    longitude_deg: float,
    start_jd_ut: float,
    end_jd_ut: float,
    *,
    domain: str = "career",
    step_days: float = 5.0,
    ayanamsa: str = "lahiri",
    true_node: bool = False,
    adapter: EphemerisAdapter | None = None,
) -> TripleLockConvergenceReport:
    """Synthesize three orthogonal Jyotish timing locks across ``[start_jd_ut, end_jd_ut]``:

    - **Lock 1 (Multi-Dasha Natal Promise):** Combines active *Vimshottari*
      Mahadasha/Antardasha house placement/lordship, BPHS *Kalachakra Dasha*
      (*Deha/Jeeva* activation & *Gati*), and *Jaimini Chara Dasha*.
    - **Lock 2 (Guru-Shani Double Transit Gochara Lock):** Evaluates whether
      transiting **Jupiter** (1st/5th/7th/9th houses) and **Saturn**
      (1st/3rd/7th/10th houses) simultaneously aspect or occupy the target
      domain house or its natal lord's sign.
    - **Lock 3 (Ashtakavarga 8-Kakshya Bindu & Bhrigu Bindu Trigger):** Evaluates
      Sarvashtakavarga bindus in the transited domain sign, 8-Kakshya (`3 deg 45'`)
      bindu activation of the domain Karaka, and transit contact with the
      seeker's **Bhrigu Bindu** (Rahu-Moon midpoint).
    """
    dom_key = str(domain).strip().lower()
    if dom_key not in _LIFE_DOMAIN_CONFIG:
        raise ValueError(f"Unsupported domain {domain!r}; choose from {sorted(_LIFE_DOMAIN_CONFIG)}")
    cfg = _LIFE_DOMAIN_CONFIG[dom_key]
    t0 = float(start_jd_ut)
    t1 = float(end_jd_ut)
    if t1 < t0:
        raise ValueError("end_jd_ut must be >= start_jd_ut")

    ad = adapter if adapter is not None else EphemerisAdapter()
    b_jd = float(birth_jd_ut)
    lat = float(latitude_deg)
    lon = float(longitude_deg)
    dt = max(float(step_days), 1.0)

    houses = ad.houses_ut(b_jd, lat, lon, system="whole_sign", ayanamsa=ayanamsa)
    asc_deg = float(houses.ascendant_deg)
    lagna_sign = min(int(asc_deg // 30.0), 11)

    natal_lons: dict[str, float] = {}
    for b_key in VEDIC_NINE_GRAHAS:
        pos = ad.calc_ut(b_jd, b_key, sidereal=True, ayanamsa=ayanamsa, true_node=true_node)
        natal_lons[b_key.capitalize()] = float(pos.longitude_deg)

    natal_signs = {p: min(int(l_deg // 30.0), 11) for p, l_deg in natal_lons.items()}
    natal_houses = {p: ((s - lagna_sign) % 12) + 1 for p, s in natal_signs.items()}

    primary_house: int = int(cfg["primary_house"])
    supporting_houses: tuple[int, ...] = tuple(cfg["supporting_houses"])
    primary_sign = (lagna_sign + primary_house - 1) % 12
    primary_lord = RASI_LORDS[primary_sign]
    primary_lord_natal_sign = natal_signs[primary_lord]
    karaka_planet = str(cfg["karaka"])

    # Bhrigu Bindu = Rahu -> Moon arc midpoint
    moon_lon = natal_lons["Moon"]
    rahu_lon = natal_lons["Rahu"]
    bhrigu_bindu_lon = normalize_degrees(rahu_lon + 0.5 * normalize_degrees(moon_lon - rahu_lon))

    # Precompute Dasha timelines and Ashtakavarga (extend cycles so any query horizon is covered)
    req_years = max(120.0, (t1 - b_jd) / 365.2425 + 24.0)
    vim_cycles = max(1, int(math.ceil(req_years / 120.0)) + 1)
    vim_dasha = compute_vimshottari_dasha(moon_lon, b_jd, max_level=2, cycles=vim_cycles)
    kc_dasha = compute_kalachakra_dasha(moon_lon, b_jd)
    kc_span = (kc_dasha.mahadashas[-1].end_jd - b_jd) if kc_dasha.mahadashas else 0.0
    chara_timeline = compute_chara_dasha(asc_deg, natal_lons, b_jd, max_level=1)
    chara_periods = chara_timeline.mahadashas
    chara_span = (chara_periods[-1].end_jd - b_jd) if chara_periods else 0.0
    ashtaka = compute_ashtakavarga(natal_lons, asc_deg)

    # Which planets are connected to the target domain houses (by occupancy or lordship)?
    domain_connected_planets: set[str] = {primary_lord, karaka_planet, str(cfg["secondary_karaka"])}
    for p_name, h_num in natal_houses.items():
        if h_num in supporting_houses:
            domain_connected_planets.add(p_name)
    for s_idx in range(12):
        h_num = ((s_idx - lagna_sign) % 12) + 1
        if h_num in supporting_houses:
            domain_connected_planets.add(RASI_LORDS[s_idx])

    sampled_entries: list[TripleLockWindowEntry] = []
    curr = t0
    while curr <= t1 + 1.0e-9:
        # 1. Lock 1: Multi-Dasha Natal Promise
        vim_maha = "Ket"
        vim_antar = "Ket"
        for m_p in vim_dasha.mahadashas:
            if m_p.start_jd <= curr < m_p.end_jd:
                vim_maha = m_p.lord
                for a_p in m_p.sub_periods:
                    if a_p.start_jd <= curr < a_p.end_jd:
                        vim_antar = a_p.lord
                        break
                break
        maha_full = {
            "Sun": "Sun",
            "Moon": "Moon",
            "Mars": "Mars",
            "Mercury": "Mercury",
            "Jupiter": "Jupiter",
            "Venus": "Venus",
            "Saturn": "Saturn",
            "Rahu": "Rahu",
            "Ketu": "Ketu",
        }.get(vim_maha, vim_maha)
        antar_full = {
            "Sun": "Sun",
            "Moon": "Moon",
            "Mars": "Mars",
            "Mercury": "Mercury",
            "Jupiter": "Jupiter",
            "Venus": "Venus",
            "Saturn": "Saturn",
            "Rahu": "Rahu",
            "Ketu": "Ketu",
        }.get(vim_antar, vim_antar)

        kc_sign_name = kc_dasha.deha_sign_name
        kc_gati = "Mandooka_Regular"
        kc_touches_vital = False
        kc_sign_idx = kc_dasha.deha_sign_index
        curr_kc = b_jd + ((curr - b_jd) % kc_span) if (kc_span > 0.0 and curr >= kc_dasha.mahadashas[-1].end_jd) else curr
        for kp in kc_dasha.mahadashas:
            if kp.start_jd <= curr_kc < kp.end_jd:
                kc_sign_name = kp.sign_name
                kc_gati = kp.gati
                kc_touches_vital = bool(kp.is_deha_sign or kp.is_jeeva_sign)
                kc_sign_idx = kp.sign_index
                break

        chara_sign_name = RASI_NAMES[lagna_sign]
        chara_sign_idx = lagna_sign
        curr_chara = b_jd + ((curr - b_jd) % chara_span) if (chara_span > 0.0 and curr >= chara_periods[-1].end_jd) else curr
        for cp in chara_periods:
            if cp.start_jd <= curr_chara < cp.end_jd:
                chara_sign_name = cp.lord
                chara_sign_idx = RASI_NAMES.index(cp.lord) if cp.lord in RASI_NAMES else lagna_sign
                break

        lock1_score = 25.0
        if maha_full in domain_connected_planets:
            lock1_score += 25.0
        if antar_full in domain_connected_planets:
            lock1_score += 25.0
        kc_house = ((kc_sign_idx - lagna_sign) % 12) + 1
        if kc_house in supporting_houses or kc_touches_vital:
            lock1_score += 15.0
        chara_house = ((chara_sign_idx - lagna_sign) % 12) + 1
        if chara_house in supporting_houses:
            lock1_score += 10.0
        lock1_score = min(lock1_score, 100.0)

        # 2. Lock 2: Guru-Shani Double Transit Gochara Lock
        jup_pos = ad.calc_ut(curr, "jupiter", sidereal=True, ayanamsa=ayanamsa, true_node=true_node)
        sat_pos = ad.calc_ut(curr, "saturn", sidereal=True, ayanamsa=ayanamsa, true_node=true_node)
        kar_pos = (
            jup_pos
            if karaka_planet == "Jupiter"
            else (
                sat_pos
                if karaka_planet == "Saturn"
                else ad.calc_ut(curr, karaka_planet.lower(), sidereal=True, ayanamsa=ayanamsa, true_node=true_node)
            )
        )
        jup_sign = min(int(float(jup_pos.longitude_deg) // 30.0), 11)
        sat_sign = min(int(float(sat_pos.longitude_deg) // 30.0), 11)

        # Jupiter aspects 1st (occupancy), 5th, 7th, 9th signs from itself
        jup_aspected_signs = {
            jup_sign,
            (jup_sign + 4) % 12,
            (jup_sign + 6) % 12,
            (jup_sign + 8) % 12,
        }
        # Saturn aspects 1st (occupancy), 3rd, 7th, 10th signs from itself
        sat_aspected_signs = {
            sat_sign,
            (sat_sign + 2) % 12,
            (sat_sign + 6) % 12,
            (sat_sign + 9) % 12,
        }
        target_signs = {primary_sign, primary_lord_natal_sign}
        jup_hit = bool(jup_aspected_signs & target_signs)
        sat_hit = bool(sat_aspected_signs & target_signs)
        double_transit_locked = bool(jup_hit and sat_hit)
        if double_transit_locked:
            lock2_score = 100.0
        elif jup_hit or sat_hit:
            lock2_score = 60.0
        else:
            lock2_score = 20.0

        # 3. Lock 3: Ashtakavarga 8-Kakshya Bindu & Bhrigu Bindu Trigger
        kar_lon = float(kar_pos.longitude_deg)
        kar_sign = min(int(kar_lon // 30.0), 11)
        kar_deg_in_sign = kar_lon - kar_sign * 30.0
        kaksha_idx = min(int(kar_deg_in_sign // 3.75), 7)
        kaksha_lord = _KAKSHA_LORDS_8[kaksha_idx]
        bav_Lookup_planet = karaka_planet if karaka_planet in ashtaka.bhinna_tables else "Jupiter"
        bav_table = ashtaka.bhinna_tables[bav_Lookup_planet]
        kaksha_has_bindu = bool(bav_table.contributor_matrix[kaksha_lord][kar_sign] == 1)
        sav_primary = int(ashtaka.sarvashtakavarga_7[primary_sign])
        sav_jup = int(ashtaka.sarvashtakavarga_7[jup_sign])

        # Check Bhrigu Bindu activation by Jupiter, Saturn, or Karaka within 5 deg (conjunction/trine/opposition)
        bb_triggered = False
        for t_lon in (float(jup_pos.longitude_deg), float(sat_pos.longitude_deg), kar_lon):
            diff_bb = abs(normalize_degrees(t_lon - bhrigu_bindu_lon))
            sep_bb = 360.0 - diff_bb if diff_bb > 180.0 else diff_bb
            if min(abs(sep_bb - 0.0), abs(sep_bb - 120.0), abs(sep_bb - 180.0)) <= 5.0:
                bb_triggered = True
                break

        lock3_score = (
            (40.0 if kaksha_has_bindu else 10.0)
            + min(sav_jup / 35.0, 1.0) * 35.0
            + (25.0 if bb_triggered else 5.0)
        )
        lock3_score = min(round(lock3_score, 4), 100.0)

        total_score = round(0.40 * lock1_score + 0.35 * lock2_score + 0.25 * lock3_score, 4)
        is_gold = bool(double_transit_locked and lock1_score >= 65.0 and kaksha_has_bindu)

        sampled_entries.append(
            TripleLockWindowEntry(
                jd_ut=round(curr, 6),
                iso_utc=jd_to_iso_utc(curr),
                lock1_natal_dasha_score_0_to_100=round(lock1_score, 4),
                lock2_double_transit_score_0_to_100=round(lock2_score, 4),
                lock3_ashtakavarga_kaksha_score_0_to_100=round(lock3_score, 4),
                total_convergence_score_0_to_100=total_score,
                is_triple_lock_gold_window=is_gold,
                vimshottari_mahadasha=maha_full,
                vimshottari_antardasha=antar_full,
                kalachakra_sign=kc_sign_name,
                kalachakra_gati=kc_gati,
                kalachakra_touches_deha_or_jeeva=kc_touches_vital,
                chara_dasha_sign=chara_sign_name,
                jupiter_aspects_primary_house_or_lord=jup_hit,
                saturn_aspects_primary_house_or_lord=sat_hit,
                double_transit_locked=double_transit_locked,
                karaka_kaksha_lord=kaksha_lord,
                karaka_kaksha_has_bindu=kaksha_has_bindu,
                primary_house_sav_bindus=sav_primary,
                bhrigu_bindu_triggered=bb_triggered,
            )
        )
        if curr >= t1:
            break
        curr = min(curr + dt, t1) if curr + dt > t1 and curr < t1 else curr + dt

    peak_entry = max(sampled_entries, key=lambda e: e.total_convergence_score_0_to_100)
    gold_list = tuple(e for e in sampled_entries if e.is_triple_lock_gold_window)

    receipt = {
        "module": "ephemeris_oss.impossible_astrology.triple_lock_convergence",
        "version": __version__,
        "birth_jd_ut": round(b_jd, 8),
        "start_jd_ut": round(t0, 8),
        "end_jd_ut": round(t1, 8),
        "domain": dom_key,
        "primary_house": primary_house,
        "primary_house_sign": RASI_NAMES[primary_sign],
        "primary_house_lord": primary_lord,
        "bhrigu_bindu_longitude_deg": round(bhrigu_bindu_lon, 6),
        "peak_jd_ut": peak_entry.jd_ut,
        "peak_score": peak_entry.total_convergence_score_0_to_100,
        "gold_window_count": len(gold_list),
    }
    return TripleLockConvergenceReport(
        birth_jd_ut=b_jd,
        birth_iso_utc=jd_to_iso_utc(b_jd),
        start_jd_ut=t0,
        end_jd_ut=t1,
        domain=dom_key,
        primary_house=primary_house,
        primary_house_sign=RASI_NAMES[primary_sign],
        primary_house_lord=primary_lord,
        bhrigu_bindu_longitude_deg=round(bhrigu_bindu_lon, 6),
        kalachakra_deha_sign=kc_dasha.deha_sign_name,
        kalachakra_jeeva_sign=kc_dasha.jeeva_sign_name,
        peak_window=peak_entry,
        gold_windows=gold_list,
        sampled_timeline=tuple(sampled_entries),
        receipt=receipt,
        receipt_sha256=canonical_hash(receipt),
    )


__all__ = [
    "InverseChartDateSearchReport",
    "InverseChartMatchWindow",
    "KrantisamyaMahapataEvent",
    "KrantisamyaMahapataReport",
    "MultiCenturyPhenomenaReport",
    "PersonalizedAstroFingerprintReport",
    "SiddhantaDriftAnalysisReport",
    "SubsecondShodashvargaCuspReport",
    "TripleLockConvergenceReport",
    "TripleLockWindowEntry",
    "VargaBoundaryMargin",
    "YogataraStellarBhedaReport",
    "analyze_siddhanta_vs_jpl_de440_drift",
    "compute_personalized_astro_fingerprint",
    "compute_triple_lock_life_event_convergence",
    "evaluate_yogatara_stellar_bheda_and_visibility",
    "rectify_birth_time_bayesian",
    "scan_multi_century_rare_phenomena",
    "solve_chart_date_from_planetary_constraints",
    "solve_krantisamya_mahapata_windows",
    "solve_subsecond_shodashvarga_cusp_transitions",
]
