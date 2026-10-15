"""Clean-room Solar and Lunar Eclipse Solver using Besselian elements and shadow cone geometry.

References
----------
* Chauvenet, W. (1891), A Manual of Spherical and Practical Astronomy, 5th ed.,
  Vol. I, Chapter X (Eclipses), Dover reprint.
* Meeus, J. (1989), Elements of Solar Eclipses 1951-2200, Willmann-Bell.
* Meeus, J. (1998), Astronomical Algorithms, 2nd ed., Chapters 25, 47, 49, 54,
  Willmann-Bell.
* Espenak, F. & Meeus, J. (2006), Five Millennium Canon of Solar Eclipses:
  -1999 to +3000, NASA/TP-2006-214141.
* Espenak, F. & Meeus, J. (2009), Five Millennium Canon of Lunar Eclipses:
  -1999 to +3000, NASA/TP-2009-214172.
* Danjon, A. (1951), L'Astronomie, 65, 51-53: atmospheric enlargement of Earth's
  umbral and penumbral shadow cones (traditional Chauvenet 1/50 = 1.02 factor).
* IAU SOFA / ERFA library for IAU 2006 precession, nutation, obliquity, and
  Greenwich apparent sidereal time reductions.
"""

from __future__ import annotations

import math
from dataclasses import asdict, dataclass
from typing import Any, Callable, Literal, Mapping, Sequence

import erfa

from .._version import __version__
from .earth_orientation import estimate_delta_t
from .receipt import canonical_hash

J2000_TT_JD = 2451545.0
JULIAN_CENTURY_DAYS = 36525.0
SECONDS_PER_DAY = 86400.0
MINUTES_PER_DAY = 1440.0

# Fundamental physical and geometric constants (IAU / WGS84 / Chauvenet)
AU_KM = 149_597_870.7
EARTH_EQUATORIAL_RADIUS_KM = 6378.1366
WGS84_FLATTENING = 1.0 / 298.257223563
WGS84_E2 = 2.0 * WGS84_FLATTENING - WGS84_FLATTENING * WGS84_FLATTENING
EARTH_OBLATENESS_SHADOW_FACTOR = 0.998340
SUN_RADIUS_KM = 695_700.0
MOON_RADIUS_KM = 1737.4
# Solar radius in units of Earth equatorial radius
K_SUN = SUN_RADIUS_KM / EARTH_EQUATORIAL_RADIUS_KM
# Lunar radius in units of Earth equatorial radius (mean eclipse limb value)
K_MOON = MOON_RADIUS_KM / EARTH_EQUATORIAL_RADIUS_KM
# Traditional Chauvenet / Danjon 1/50 atmospheric shadow enlargement factor
DANJON_ATMOSPHERIC_ENLARGEMENT = 1.02
# Central solar eclipse gamma threshold on the oblate Earth spheroid
CENTRAL_ECLIPSE_GAMMA_LIMIT = 0.9972

LunarEclipseClassification = Literal["total", "partial", "penumbral"]
SolarEclipseClassification = Literal["total", "annular", "hybrid", "partial"]
LocalSolarEclipseClassification = Literal["total", "annular", "partial", "none"]


# ---------------------------------------------------------------------------
# Built-in Meeus Ch. 25 & Ch. 47 (ELP-2000/82 truncated) Solar-Lunar Evaluator
# ---------------------------------------------------------------------------

# 60 periodic terms for Moon's longitude (Meeus Table 47.A): (D, M, M', F, sigma_l, sigma_r)
_MOON_LON_DIST_TERMS: tuple[tuple[int, int, int, int, int, int], ...] = (
    (0, 0, 1, 0, 6288774, -20905355),
    (2, 0, -1, 0, 1274027, -3699111),
    (2, 0, 0, 0, 658314, -2955968),
    (0, 0, 2, 0, 213618, -569925),
    (0, 1, 0, 0, -185116, 48888),
    (0, 0, 0, 2, -114332, -3149),
    (2, 0, -2, 0, 58793, 246158),
    (2, -1, -1, 0, 57066, -152138),
    (2, 0, 1, 0, 53322, -170733),
    (2, -1, 0, 0, 45758, -204586),
    (0, 1, -1, 0, -40923, -129620),
    (1, 0, 0, 0, -34720, 108743),
    (0, 1, 1, 0, -30383, 104755),
    (2, 0, 0, -2, 15327, 10321),
    (0, 0, 1, 2, -12528, 0),
    (0, 0, 1, -2, 10980, 79661),
    (4, 0, -1, 0, 10675, -34782),
    (0, 0, 3, 0, 10034, -23210),
    (4, 0, -2, 0, 8548, -21636),
    (2, 1, -1, 0, -7888, 24208),
    (2, 1, 0, 0, -6766, 30824),
    (1, 0, -1, 0, -5163, -8379),
    (1, 1, 0, 0, 4987, -16675),
    (2, -1, 1, 0, 4036, -12831),
    (2, 0, 2, 0, 3994, -10445),
    (4, 0, 0, 0, 3861, -11650),
    (2, 0, -3, 0, 3665, 14403),
    (0, 1, -2, 0, -2689, -7003),
    (2, 0, -1, 2, -2602, 0),
    (2, -1, -2, 0, 2390, 10056),
    (1, 0, 1, 0, -2348, 6322),
    (2, -2, 0, 0, 2236, -9884),
    (0, 1, 2, 0, -2120, 5751),
    (0, 2, 0, 0, -2069, 0),
    (2, -2, -1, 0, 2048, -4950),
    (2, 0, 1, -2, -1773, 4130),
    (2, 0, 0, 2, -1595, 0),
    (4, -1, -1, 0, 1215, -3958),
    (0, 0, 2, 2, -1110, 0),
    (3, 0, -1, 0, -892, 3258),
    (2, 1, 1, 0, -810, 2616),
    (4, -1, -2, 0, 759, -1897),
    (0, 2, -1, 0, -713, -2117),
    (2, 2, -1, 0, -700, 2354),
    (2, 1, -2, 0, 691, 0),
    (2, -1, 0, -2, 596, 0),
    (4, 0, 1, 0, 549, -1423),
    (0, 0, 4, 0, 537, -1117),
    (4, -1, 0, 0, 520, -1571),
    (1, 0, -2, 0, -487, -1739),
    (2, 1, 0, -2, -399, 0),
    (0, 0, 2, -2, -381, -4421),
    (1, 1, 1, 0, 351, 0),
    (3, 0, -2, 0, -340, 0),
    (4, 0, -3, 0, 330, 0),
    (2, -1, 2, 0, 327, 0),
    (0, 2, 1, 0, -323, 1165),
    (1, 1, -1, 0, 299, 0),
    (2, 0, 3, 0, 294, 0),
    (2, 0, -1, -2, 0, 8752),
)

# 60 periodic terms for Moon's latitude (Meeus Table 47.B): (D, M, M', F, sigma_b)
_MOON_LAT_TERMS: tuple[tuple[int, int, int, int, int], ...] = (
    (0, 0, 0, 1, 5128122),
    (0, 0, 1, 1, 280602),
    (0, 0, 1, -1, 277693),
    (2, 0, 0, -1, 173237),
    (2, 0, -1, 1, 55413),
    (2, 0, -1, -1, 46271),
    (2, 0, 0, 1, 32573),
    (0, 0, 2, 1, 17198),
    (2, 0, 1, -1, 9266),
    (0, 0, 2, -1, 8822),
    (2, -1, 0, -1, 8216),
    (2, 0, -2, -1, 4324),
    (2, 0, 1, 1, 4200),
    (2, 1, 0, -1, -3359),
    (2, -1, -1, 1, 2463),
    (2, -1, 0, 1, 2211),
    (2, -1, -1, -1, 2065),
    (0, 1, -1, -1, -1870),
    (4, 0, -1, -1, 1828),
    (0, 1, 0, 1, -1794),
    (0, 0, 0, 3, -1749),
    (0, 1, -1, 1, -1565),
    (1, 0, 0, 1, -1491),
    (0, 1, 1, 1, -1475),
    (0, 1, 1, -1, -1410),
    (0, 1, 0, -1, -1344),
    (1, 0, 0, -1, -1335),
    (0, 0, 3, 1, 1107),
    (4, 0, 0, -1, 1021),
    (4, 0, -1, 1, 833),
    (0, 0, 1, -3, 777),
    (4, 0, -2, 1, 671),
    (2, 0, 0, -3, 607),
    (2, 0, 2, -1, 596),
    (2, -1, 1, -1, 491),
    (2, 0, -2, 1, -451),
    (0, 0, 3, -1, 439),
    (2, 0, 2, 1, 422),
    (2, 0, -3, -1, 421),
    (2, 1, -1, 1, -366),
    (2, 1, 0, 1, -351),
    (4, 0, 0, 1, 331),
    (2, -1, 1, 1, 315),
    (2, -2, 0, -1, 302),
    (0, 0, 1, 3, -283),
    (2, 1, 1, -1, -229),
    (1, 1, 0, -1, 223),
    (1, 1, 0, 1, 223),
    (0, 1, -2, -1, -220),
    (2, 1, -1, -1, -220),
    (1, 0, 1, 1, -185),
    (2, -1, -2, -1, 181),
    (0, 1, 2, 1, -177),
    (4, 0, -2, -1, 176),
    (4, -1, -1, -1, 166),
    (1, 0, 1, -1, -164),
    (4, 0, 1, -1, 132),
    (1, 0, -1, -1, -119),
    (4, -1, 0, -1, 115),
    (2, -2, 0, 1, 107),
)


def _meeus_sun_apparent(jd_tt: float) -> dict[str, float]:
    """Compute apparent geocentric ecliptic position and distance of the Sun (Meeus Ch. 25)."""
    t = (jd_tt - J2000_TT_JD) / JULIAN_CENTURY_DAYS
    t2 = t * t
    t3 = t2 * t

    # Geometric mean longitude of the Sun (deg)
    l0 = (280.46646 + 36000.76983 * t + 0.0003032 * t2) % 360.0
    # Mean anomaly of the Sun (deg)
    m = (357.5291092 + 35999.0502909 * t - 0.0001536 * t2 + t3 / 24490000.0) % 360.0
    m_rad = math.radians(m)
    # Eccentricity of Earth's orbit
    e = 0.016708634 - 0.000042037 * t - 0.0000001267 * t2

    # Sun's equation of the center (deg)
    c = (
        (1.914602 - 0.004817 * t - 0.000014 * t2) * math.sin(m_rad)
        + (0.019993 - 0.000101 * t) * math.sin(2.0 * m_rad)
        + 0.000289 * math.sin(3.0 * m_rad)
    )
    true_lon = (l0 + c) % 360.0
    true_anom = m + c
    r_au = (1.000001018 * (1.0 - e * e)) / (1.0 + e * math.cos(math.radians(true_anom)))
    distance_km = r_au * AU_KM

    # Nutation in longitude (from ERFA IAU 2006/2000A) and aberration
    dpsi_rad, _deps_rad = erfa.nut06a(J2000_TT_JD, jd_tt - J2000_TT_JD)
    aberration_deg = -20.4898 / (3600.0 * r_au)
    apparent_lon = (true_lon + math.degrees(float(dpsi_rad)) + aberration_deg) % 360.0

    return {
        "longitude_deg": apparent_lon,
        "latitude_deg": 0.0,
        "distance_km": distance_km,
    }


def _meeus_moon_apparent(jd_tt: float) -> dict[str, float]:
    """Compute apparent geocentric ecliptic position and distance of the Moon (Meeus Ch. 47)."""
    t = (jd_tt - J2000_TT_JD) / JULIAN_CENTURY_DAYS
    t2 = t * t
    t3 = t2 * t
    t4 = t3 * t

    # Moon's mean longitude L'
    lp = (218.3164477 + 481267.88123421 * t - 0.0015786 * t2 + t3 / 538841.0 - t4 / 65194000.0) % 360.0
    # Mean elongation of the Moon D
    d = (297.8501921 + 445267.1114034 * t - 0.0018819 * t2 + t3 / 545868.0 - t4 / 113065000.0) % 360.0
    # Sun's mean anomaly M
    m = (357.5291092 + 35999.0502909 * t - 0.0001536 * t2 + t3 / 24490000.0) % 360.0
    # Moon's mean anomaly M'
    mp = (134.9633964 + 477198.8675055 * t + 0.0087414 * t2 + t3 / 69699.0 - t4 / 14712000.0) % 360.0
    # Moon's argument of latitude F
    f = (93.2720950 + 483202.0175233 * t - 0.0036539 * t2 - t3 / 3526000.0 + t4 / 863310000.0) % 360.0

    # Planetary and flattening arguments A1, A2, A3
    a1 = math.radians((119.75 + 131.849 * t) % 360.0)
    a2 = math.radians((53.09 + 479264.290 * t) % 360.0)
    a3 = math.radians((313.45 + 481266.484 * t) % 360.0)

    e_factor = 1.0 - 0.002516 * t - 0.0000074 * t2
    e_factor2 = e_factor * e_factor

    d_rad = math.radians(d)
    m_rad = math.radians(m)
    mp_rad = math.radians(mp)
    f_rad = math.radians(f)
    lp_rad = math.radians(lp)

    sum_l = 0.0
    sum_r = 0.0
    for cd, cm, cmp, cf, sl, sr in _MOON_LON_DIST_TERMS:
        arg = cd * d_rad + cm * m_rad + cmp * mp_rad + cf * f_rad
        abs_cm = abs(cm)
        scale = e_factor if abs_cm == 1 else (e_factor2 if abs_cm == 2 else 1.0)
        if sl:
            sum_l += sl * scale * math.sin(arg)
        if sr:
            sum_r += sr * scale * math.cos(arg)

    sum_l += 3958.0 * math.sin(a1) + 1962.0 * math.sin(lp_rad - f_rad) + 318.0 * math.sin(a2)

    sum_b = 0.0
    for cd, cm, cmp, cf, sb in _MOON_LAT_TERMS:
        arg = cd * d_rad + cm * m_rad + cmp * mp_rad + cf * f_rad
        abs_cm = abs(cm)
        scale = e_factor if abs_cm == 1 else (e_factor2 if abs_cm == 2 else 1.0)
        sum_b += sb * scale * math.sin(arg)

    sum_b += (
        -2235.0 * math.sin(lp_rad)
        + 382.0 * math.sin(a3)
        + 175.0 * math.sin(a1 - f_rad)
        + 175.0 * math.sin(a1 + f_rad)
        + 127.0 * math.sin(lp_rad - mp_rad)
        - 115.0 * math.sin(lp_rad + mp_rad)
    )

    dpsi_rad, _ = erfa.nut06a(J2000_TT_JD, jd_tt - J2000_TT_JD)
    lon_deg = (lp + sum_l * 1.0e-6 + math.degrees(float(dpsi_rad))) % 360.0
    lat_deg = sum_b * 1.0e-6
    distance_km = 385000.56 + sum_r * 1.0e-3

    return {
        "longitude_deg": lon_deg,
        "latitude_deg": lat_deg,
        "distance_km": distance_km,
    }


def _evaluate_sun_moon(
    jd_tt: float,
    engine: Any = None,
    position_provider: Any = None,
) -> tuple[dict[str, float], dict[str, float], str]:
    """Return apparent geocentric ecliptic (longitude_deg, latitude_deg, distance_km) for Sun and Moon."""
    source = position_provider if position_provider is not None else engine
    meeus_sun = _meeus_sun_apparent(jd_tt)
    meeus_moon = _meeus_moon_apparent(jd_tt)

    if source is None:
        return meeus_sun, meeus_moon, "meeus-elp2000-vsop87"

    # Resolve Engine instance vs callable provider
    provider_label = "custom-position-provider"
    raw_positions: Mapping[str, Any]
    engine_obj: Any = None

    if hasattr(source, "positions_tt") and callable(source.positions_tt):
        engine_obj = source
        res = source.positions_tt(jd_tt, ("sun", "moon"))
        raw_positions = res.value if hasattr(res, "value") else res
        provider_label = "engine.positions_tt"
    elif callable(source):
        engine_obj = getattr(source, "__self__", None)
        res = source(jd_tt, ("sun", "moon"))
        raw_positions = res.value if hasattr(res, "value") else res
        if engine_obj is not None and hasattr(engine_obj, "positions_tt"):
            provider_label = "engine.positions_tt"
    else:
        raise ValueError("engine or position_provider must be an Engine instance, a callable, or None")

    def _extract(body_key: str, fallback: dict[str, float]) -> dict[str, float]:
        entry: Mapping[str, Any] | None = None
        for k, v in raw_positions.items():
            if k.strip().lower() == body_key:
                entry = v
                break
        if entry is None:
            return fallback
        lon = float(entry.get("longitude_deg", fallback["longitude_deg"])) % 360.0
        lat = float(entry.get("latitude_deg", fallback["latitude_deg"]))
        dist = entry.get("distance_km")
        if dist is not None:
            dist_km = float(dist)
        elif engine_obj is not None and hasattr(engine_obj, "_provider"):
            try:
                prov = engine_obj._provider
                tt = (J2000_TT_JD, jd_tt - J2000_TT_JD)
                year = int(erfa.jd2cal(*tt)[0])
                offset = float(erfa.dtdb(*tt, 0.0, 0.0, 0.0, 0.0))
                tdb = tuple(float(v) for v in erfa.tttdb(*tt, offset))
                state = prov.geocentric_state_at_tdb(body=body_key, tdb=tdb, kernel_year=year)
                px, py, pz = state.position_km
                dist_km = math.sqrt(px * px + py * py + pz * pz)
            except Exception:
                dist_km = fallback["distance_km"]
        else:
            dist_km = fallback["distance_km"]
        return {"longitude_deg": lon, "latitude_deg": lat, "distance_km": dist_km}

    return _extract("sun", meeus_sun), _extract("moon", meeus_moon), provider_label


def _signed_angle_diff_deg(a_deg: float, b_deg: float) -> float:
    """Return shortest signed angular difference (a - b) in [-180, 180)."""
    return (a_deg - b_deg + 180.0) % 360.0 - 180.0


def _decimal_year_from_jd(jd_tt: float) -> float:
    year, month, day, frac = erfa.jd2cal(J2000_TT_JD, jd_tt - J2000_TT_JD)
    return float(year) + (float(month) - 1.0) / 12.0 + (float(day) - 1.0 + float(frac)) / 365.2425


def _true_obliquity_rad(jd_tt: float) -> float:
    tt = (J2000_TT_JD, jd_tt - J2000_TT_JD)
    _dpsi, deps = erfa.nut06a(*tt)
    return float(erfa.obl06(*tt) + deps)


def _gast_rad(jd_tt: float) -> float:
    """Greenwich Apparent Sidereal Time in radians at TT Julian Date."""
    dec_year = _decimal_year_from_jd(jd_tt)
    clamped_year = min(max(dec_year, -1999.0), 3000.0)
    dt_sec = estimate_delta_t(clamped_year).seconds
    jd_ut1 = jd_tt - dt_sec / SECONDS_PER_DAY
    tt = (J2000_TT_JD, jd_tt - J2000_TT_JD)
    ut1 = (J2000_TT_JD, jd_ut1 - J2000_TT_JD)
    return float(erfa.gst06a(*ut1, *tt))


def _ecliptic_to_equatorial_cartesian(
    lon_deg: float, lat_deg: float, radius_units: float, eps_rad: float
) -> tuple[float, float, float]:
    """Convert spherical ecliptic coordinates to true-of-date equatorial Cartesian (x, y, z)."""
    lam = math.radians(lon_deg)
    bet = math.radians(lat_deg)
    cos_b = math.cos(bet)
    x_ecl = radius_units * cos_b * math.cos(lam)
    y_ecl = radius_units * cos_b * math.sin(lam)
    z_ecl = radius_units * math.sin(bet)

    cos_e = math.cos(eps_rad)
    sin_e = math.sin(eps_rad)
    x_eq = x_ecl
    y_eq = y_ecl * cos_e - z_ecl * sin_e
    z_eq = y_ecl * sin_e + z_ecl * cos_e
    return x_eq, y_eq, z_eq


def _minimize_scalar(
    func: Callable[[float], float],
    left_jd: float,
    right_jd: float,
    tol_days: float = 1.0e-8,
    max_iter: int = 80,
) -> tuple[float, float]:
    """Golden-section minimization on [left_jd, right_jd]."""
    inv_phi = (math.sqrt(5.0) - 1.0) / 2.0
    a = left_jd
    b = right_jd
    x1 = b - inv_phi * (b - a)
    x2 = a + inv_phi * (b - a)
    f1 = func(x1)
    f2 = func(x2)
    for _ in range(max_iter):
        if b - a <= tol_days:
            break
        if f1 < f2:
            b = x2
            x2 = x1
            f2 = f1
            x1 = b - inv_phi * (b - a)
            f1 = func(x1)
        else:
            a = x1
            x1 = x2
            f1 = f2
            x2 = a + inv_phi * (b - a)
            f2 = func(x2)
    mid = 0.5 * (a + b)
    return mid, func(mid)


def _bisect_root(
    func: Callable[[float], float],
    left_jd: float,
    right_jd: float,
    tol_days: float = 1.0e-8,
    max_iter: int = 80,
) -> float | None:
    """Find root of func(t) == 0 in [left_jd, right_jd] by bisection, or None if no sign change."""
    a = left_jd
    b = right_jd
    fa = func(a)
    fb = func(b)
    if abs(fa) <= 1.0e-13:
        return a
    if abs(fb) <= 1.0e-13:
        return b
    if fa * fb > 0.0:
        # Sub-sample once in case the sign change is near the extremum
        samples = 16
        step = (b - a) / samples
        prev_t = a
        prev_f = fa
        found = False
        for i in range(1, samples + 1):
            cur_t = a + i * step
            cur_f = func(cur_t)
            if prev_f * cur_f <= 0.0:
                a, b = prev_t, cur_t
                fa, fb = prev_f, cur_f
                found = True
                break
            prev_t, prev_f = cur_t, cur_f
        if not found:
            return None

    for _ in range(max_iter):
        mid = 0.5 * (a + b)
        fm = func(mid)
        if abs(fm) <= 1.0e-13 or (b - a) <= tol_days:
            return mid
        if fa * fm <= 0.0:
            b = mid
            fb = fm
        else:
            a = mid
            fa = fm
    return 0.5 * (a + b)


def _find_syzygy_roots(
    start_jd_tt: float,
    end_jd_tt: float,
    target_elongation_deg: float,
    engine: Any = None,
    position_provider: Any = None,
) -> list[float]:
    """Locate all syzygy instants (0 deg for New Moon, 180 deg for Full Moon) in [start_jd_tt, end_jd_tt]."""
    if end_jd_tt <= start_jd_tt:
        raise ValueError("end_jd_tt must be greater than start_jd_tt")

    def elongation_residual(jd: float) -> float:
        sun, moon, _ = _evaluate_sun_moon(jd, engine, position_provider)
        elong = (moon["longitude_deg"] - sun["longitude_deg"]) % 360.0
        return _signed_angle_diff_deg(elong, target_elongation_deg)

    # Synodic month is ~29.53 days; a 4-day step advances by ~48.7 deg (< 180 deg)
    step = min(4.0, max(0.25, (end_jd_tt - start_jd_tt) / 8.0))
    roots: list[float] = []
    t_prev = start_jd_tt
    f_prev = elongation_residual(t_prev)
    while t_prev < end_jd_tt:
        t_next = min(end_jd_tt, t_prev + step)
        f_next = elongation_residual(t_next)
        # Direct crossing has f_prev < 0 <= f_next and |f_next - f_prev| < 180
        if f_prev <= 0.0 <= f_next and (f_next - f_prev) < 180.0:
            root = _bisect_root(elongation_residual, t_prev, t_next, tol_days=1.0e-8)
            if root is not None and (not roots or abs(root - roots[-1]) > 5.0):
                roots.append(root)
        t_prev = t_next
        f_prev = f_next
    return roots


def _topocentric_alt_az_deg(
    jd_tt: float,
    lon_ecl_deg: float,
    lat_ecl_deg: float,
    distance_km: float,
    latitude_deg: float,
    longitude_deg: float,
    altitude_m: float = 0.0,
) -> tuple[float, float]:
    """Compute topocentric apparent altitude and azimuth (degrees) of a body."""
    eps_rad = _true_obliquity_rad(jd_tt)
    r_units = distance_km / EARTH_EQUATORIAL_RADIUS_KM
    x_eq, y_eq, z_eq = _ecliptic_to_equatorial_cartesian(lon_ecl_deg, lat_ecl_deg, r_units, eps_rad)

    phi = math.radians(latitude_deg)
    u = math.atan((1.0 - WGS84_FLATTENING) * math.tan(phi))
    rho_sin_phi = (1.0 - WGS84_FLATTENING) * math.sin(u) + (altitude_m / (EARTH_EQUATORIAL_RADIUS_KM * 1000.0)) * math.sin(phi)
    rho_cos_phi = math.cos(u) + (altitude_m / (EARTH_EQUATORIAL_RADIUS_KM * 1000.0)) * math.cos(phi)

    theta_local = _gast_rad(jd_tt) + math.radians(longitude_deg)
    obs_x = rho_cos_phi * math.cos(theta_local)
    obs_y = rho_cos_phi * math.sin(theta_local)
    obs_z = rho_sin_phi

    dx = x_eq - obs_x
    dy = y_eq - obs_y
    dz = z_eq - obs_z

    # Rotate topocentric equatorial vector (dx, dy, dz) to local East-North-Up
    sin_t = math.sin(theta_local)
    cos_t = math.cos(theta_local)
    sin_p = math.sin(phi)
    cos_p = math.cos(phi)

    east = -sin_t * dx + cos_t * dy
    north = -sin_p * cos_t * dx - sin_p * sin_t * dy + cos_p * dz
    up = cos_p * cos_t * dx + cos_p * sin_t * dy + sin_p * dz

    horiz = math.hypot(east, north)
    alt_deg = math.degrees(math.atan2(up, horiz))
    az_deg = math.degrees(math.atan2(east, north)) % 360.0
    return alt_deg, az_deg


# ---------------------------------------------------------------------------
# Lunar Eclipse Data Structures and Solvers
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class LunarEclipse:
    """Complete shadow-cone solution and contact instants for a lunar eclipse."""

    classification: LunarEclipseClassification
    syzygy_jd_tt: float
    greatest_jd_tt: float
    gamma: float
    penumbral_magnitude: float
    umbral_magnitude: float
    parallax_moon_deg: float
    parallax_sun_deg: float
    semidiameter_moon_deg: float
    semidiameter_sun_deg: float
    umbra_radius_deg: float
    penumbra_radius_deg: float
    danjon_enlargement_factor: float
    p1_jd_tt: float | None
    u1_jd_tt: float | None
    u2_jd_tt: float | None
    u3_jd_tt: float | None
    u4_jd_tt: float | None
    p4_jd_tt: float | None
    penumbral_semi_duration_min: float
    umbral_semi_duration_min: float
    total_semi_duration_min: float
    receipt: Mapping[str, Any]
    receipt_sha256: str

    @property
    def eclipse_type(self) -> LunarEclipseClassification:
        return self.classification

    @property
    def magnitude(self) -> float:
        return self.umbral_magnitude if self.classification in ("total", "partial") else self.penumbral_magnitude

    @property
    def partial_semi_duration_min(self) -> float:
        return self.umbral_semi_duration_min

    @property
    def totality_semi_duration_min(self) -> float:
        return self.total_semi_duration_min

    @property
    def parallax_moon_arcsec(self) -> float:
        return self.parallax_moon_deg * 3600.0

    @property
    def parallax_sun_arcsec(self) -> float:
        return self.parallax_sun_deg * 3600.0

    @property
    def semidiameter_moon_arcsec(self) -> float:
        return self.semidiameter_moon_deg * 3600.0

    @property
    def semidiameter_sun_arcsec(self) -> float:
        return self.semidiameter_sun_deg * 3600.0

    def __getitem__(self, key: str) -> Any:
        return getattr(self, key)


@dataclass(frozen=True)
class LunarContactVisibility:
    """Observer horizon state at a single lunar eclipse contact."""

    contact: str
    jd_tt: float | None
    moon_altitude_deg: float | None
    moon_azimuth_deg: float | None
    visible: bool

    @property
    def altitude_deg(self) -> float | None:
        return self.moon_altitude_deg

    @property
    def azimuth_deg(self) -> float | None:
        return self.moon_azimuth_deg

    def __getitem__(self, key: str) -> Any:
        return getattr(self, key)


@dataclass(frozen=True)
class LunarEclipseLocalVisibility:
    """Topocentric observer visibility across all stages of a lunar eclipse."""

    classification: LunarEclipseClassification
    latitude_deg: float
    longitude_deg: float
    altitude_m: float
    visible: bool
    visibility_summary: Literal["entirely_visible", "partially_visible", "not_visible"]
    p1: LunarContactVisibility
    u1: LunarContactVisibility
    u2: LunarContactVisibility
    greatest: LunarContactVisibility
    u3: LunarContactVisibility
    u4: LunarContactVisibility
    p4: LunarContactVisibility
    contacts: Mapping[str, LunarContactVisibility]
    receipt: Mapping[str, Any]
    receipt_sha256: str

    @property
    def any_stage_visible(self) -> bool:
        return self.visible

    def __getitem__(self, key: str) -> Any:
        if key in self.contacts:
            return self.contacts[key]
        return getattr(self, key)


def _lunar_shadow_state(
    jd_tt: float,
    engine: Any = None,
    position_provider: Any = None,
) -> dict[str, float]:
    """Evaluate fundamental shadow-cone parameters at Earth's lunar distance at jd_tt."""
    sun, moon, _ = _evaluate_sun_moon(jd_tt, engine, position_provider)

    pi_moon_deg = math.degrees(math.asin(EARTH_EQUATORIAL_RADIUS_KM / moon["distance_km"]))
    pi_sun_deg = math.degrees(math.asin(EARTH_EQUATORIAL_RADIUS_KM / sun["distance_km"]))
    s_moon_deg = math.degrees(math.asin(MOON_RADIUS_KM / moon["distance_km"]))
    s_sun_deg = math.degrees(math.asin(SUN_RADIUS_KM / sun["distance_km"]))

    # Chauvenet / Danjon 1/50 (1.02) atmospheric shadow enlargement with Earth oblateness factor
    pi_moon_eff = EARTH_OBLATENESS_SHADOW_FACTOR * pi_moon_deg
    umbra_radius_deg = DANJON_ATMOSPHERIC_ENLARGEMENT * (pi_moon_eff + pi_sun_deg - s_sun_deg)
    penumbra_radius_deg = DANJON_ATMOSPHERIC_ENLARGEMENT * (pi_moon_eff + pi_sun_deg + s_sun_deg)

    # Anti-solar shadow axis center
    shadow_lon = (sun["longitude_deg"] + 180.0) % 360.0
    shadow_lat = -sun["latitude_deg"]

    dx_deg = _signed_angle_diff_deg(moon["longitude_deg"], shadow_lon) * math.cos(math.radians(moon["latitude_deg"]))
    dy_deg = moon["latitude_deg"] - shadow_lat
    sigma_deg = math.hypot(dx_deg, dy_deg)

    # Normalized distance from shadow axis in units of Earth's equatorial radius
    gamma_unsigned = sigma_deg / pi_moon_deg
    gamma_sign = 1.0 if dy_deg >= 0.0 else -1.0

    return {
        "pi_moon_deg": pi_moon_deg,
        "pi_sun_deg": pi_sun_deg,
        "s_moon_deg": s_moon_deg,
        "s_sun_deg": s_sun_deg,
        "umbra_radius_deg": umbra_radius_deg,
        "penumbra_radius_deg": penumbra_radius_deg,
        "dx_deg": dx_deg,
        "dy_deg": dy_deg,
        "sigma_deg": sigma_deg,
        "gamma": gamma_sign * gamma_unsigned,
    }


def lunar_eclipse_at(
    approx_jd_tt: float,
    engine: Any = None,
    *,
    position_provider: Any = None,
) -> LunarEclipse | None:
    """Evaluate a Lunar Eclipse near an approximate Full Moon TT Julian Date.

    Returns :class:`LunarEclipse` if the Moon enters Earth's penumbra within
    ``approx_jd_tt +/- 5 days``, or ``None`` if no lunar eclipse occurs at that syzygy.
    """
    if not math.isfinite(approx_jd_tt):
        raise ValueError("approx_jd_tt must be finite")

    roots = _find_syzygy_roots(approx_jd_tt - 5.0, approx_jd_tt + 5.0, 180.0, engine, position_provider)
    if not roots:
        return None
    syzygy_jd = min(roots, key=lambda r: abs(r - approx_jd_tt))

    _, _, provider_label = _evaluate_sun_moon(syzygy_jd, engine, position_provider)

    # Minimize angular separation sigma_deg in [syzygy_jd - 0.5, syzygy_jd + 0.5]
    greatest_jd, _ = _minimize_scalar(
        lambda t: _lunar_shadow_state(t, engine, position_provider)["sigma_deg"],
        syzygy_jd - 0.5,
        syzygy_jd + 0.5,
        tol_days=1.0e-8,
    )
    peak = _lunar_shadow_state(greatest_jd, engine, position_provider)

    sigma = peak["sigma_deg"]
    r_p = peak["penumbra_radius_deg"]
    r_u = peak["umbra_radius_deg"]
    s_m = peak["s_moon_deg"]

    l1_deg = r_p + s_m  # Outer penumbral contact distance
    l2_deg = r_u + s_m  # Outer umbral contact distance
    l3_deg = r_u - s_m  # Inner umbral (total) contact distance

    if sigma > l1_deg:
        return None

    penumbral_mag = (l1_deg - sigma) / (2.0 * s_m)
    umbral_mag = (l2_deg - sigma) / (2.0 * s_m)

    if sigma <= l3_deg:
        classification: LunarEclipseClassification = "total"
    elif sigma <= l2_deg:
        classification = "partial"
    else:
        classification = "penumbral"

    # Contact root finding over +/- 0.35 days (8.4 hours) from greatest eclipse
    window = 0.35

    def penumbral_margin(t: float) -> float:
        st = _lunar_shadow_state(t, engine, position_provider)
        return (st["penumbra_radius_deg"] + st["s_moon_deg"]) - st["sigma_deg"]

    p1_jd = _bisect_root(penumbral_margin, greatest_jd - window, greatest_jd)
    p4_jd = _bisect_root(penumbral_margin, greatest_jd, greatest_jd + window)

    u1_jd: float | None = None
    u4_jd: float | None = None
    if classification in ("partial", "total"):
        def umbral_margin(t: float) -> float:
            st = _lunar_shadow_state(t, engine, position_provider)
            return (st["umbra_radius_deg"] + st["s_moon_deg"]) - st["sigma_deg"]

        u1_jd = _bisect_root(umbral_margin, greatest_jd - window, greatest_jd)
        u4_jd = _bisect_root(umbral_margin, greatest_jd, greatest_jd + window)

    u2_jd: float | None = None
    u3_jd: float | None = None
    if classification == "total":
        def total_margin(t: float) -> float:
            st = _lunar_shadow_state(t, engine, position_provider)
            return (st["umbra_radius_deg"] - st["s_moon_deg"]) - st["sigma_deg"]

        u2_jd = _bisect_root(total_margin, greatest_jd - window, greatest_jd)
        u3_jd = _bisect_root(total_margin, greatest_jd, greatest_jd + window)

    penumbral_semi_min = ((p4_jd - p1_jd) * 0.5 * MINUTES_PER_DAY) if (p1_jd is not None and p4_jd is not None) else 0.0
    umbral_semi_min = ((u4_jd - u1_jd) * 0.5 * MINUTES_PER_DAY) if (u1_jd is not None and u4_jd is not None) else 0.0
    total_semi_min = ((u3_jd - u2_jd) * 0.5 * MINUTES_PER_DAY) if (u2_jd is not None and u3_jd is not None) else 0.0

    receipt_payload = {
        "component": "ephemeris_oss.engine.eclipses.lunar_eclipse",
        "package_version": __version__,
        "model": "chauvenet-danjon-shadow-cone-1.02",
        "position_provider": provider_label,
        "syzygy_jd_tt": syzygy_jd,
        "greatest_jd_tt": greatest_jd,
        "classification": classification,
        "gamma": peak["gamma"],
        "penumbral_magnitude": penumbral_mag,
        "umbral_magnitude": umbral_mag,
        "contacts": {
            "p1_jd_tt": p1_jd,
            "u1_jd_tt": u1_jd,
            "u2_jd_tt": u2_jd,
            "u3_jd_tt": u3_jd,
            "u4_jd_tt": u4_jd,
            "p4_jd_tt": p4_jd,
        },
    }
    digest = canonical_hash(receipt_payload)

    return LunarEclipse(
        classification=classification,
        syzygy_jd_tt=syzygy_jd,
        greatest_jd_tt=greatest_jd,
        gamma=peak["gamma"],
        penumbral_magnitude=penumbral_mag,
        umbral_magnitude=umbral_mag,
        parallax_moon_deg=peak["pi_moon_deg"],
        parallax_sun_deg=peak["pi_sun_deg"],
        semidiameter_moon_deg=peak["s_moon_deg"],
        semidiameter_sun_deg=peak["s_sun_deg"],
        umbra_radius_deg=peak["umbra_radius_deg"],
        penumbra_radius_deg=peak["penumbra_radius_deg"],
        danjon_enlargement_factor=DANJON_ATMOSPHERIC_ENLARGEMENT,
        p1_jd_tt=p1_jd,
        u1_jd_tt=u1_jd,
        u2_jd_tt=u2_jd,
        u3_jd_tt=u3_jd,
        u4_jd_tt=u4_jd,
        p4_jd_tt=p4_jd,
        penumbral_semi_duration_min=penumbral_semi_min,
        umbral_semi_duration_min=umbral_semi_min,
        total_semi_duration_min=total_semi_min,
        receipt=receipt_payload,
        receipt_sha256=digest,
    )


def find_lunar_eclipses(
    start_jd_tt: float,
    end_jd_tt: float,
    engine: Any = None,
    *,
    position_provider: Any = None,
) -> tuple[LunarEclipse, ...]:
    """Find all lunar eclipses occurring in the TT interval [start_jd_tt, end_jd_tt]."""
    syzygies = _find_syzygy_roots(start_jd_tt, end_jd_tt, 180.0, engine, position_provider)
    results: list[LunarEclipse] = []
    for syz_jd in syzygies:
        _, moon, _ = _evaluate_sun_moon(syz_jd, engine, position_provider)
        if abs(moon["latitude_deg"]) > 2.0:
            continue
        eclipse = lunar_eclipse_at(syz_jd, engine, position_provider=position_provider)
        if eclipse is not None and start_jd_tt <= eclipse.greatest_jd_tt <= end_jd_tt:
            results.append(eclipse)
    return tuple(results)


def lunar_eclipse_local_visibility(
    eclipse: LunarEclipse | float,
    latitude_deg: float,
    longitude_deg: float,
    altitude_m: float = 0.0,
    engine: Any = None,
    *,
    position_provider: Any = None,
) -> LunarEclipseLocalVisibility:
    """Compute Moon altitude, azimuth, and horizon visibility at each contact P1..P4."""
    if not (-90.0 <= latitude_deg <= 90.0):
        raise ValueError("latitude_deg must be in [-90, 90]")
    if not (-180.0 <= longitude_deg <= 180.0):
        raise ValueError("longitude_deg must be in [-180, 180]")

    if isinstance(eclipse, (int, float)):
        resolved = lunar_eclipse_at(float(eclipse), engine, position_provider=position_provider)
        if resolved is None:
            raise ValueError(f"no lunar eclipse near JD TT {eclipse}")
        eclipse_obj = resolved
    else:
        eclipse_obj = eclipse

    def _eval_contact(label: str, contact_jd: float | None) -> LunarContactVisibility:
        if contact_jd is None:
            return LunarContactVisibility(label, None, None, None, False)
        _, moon, _ = _evaluate_sun_moon(contact_jd, engine, position_provider)
        alt_deg, az_deg = _topocentric_alt_az_deg(
            contact_jd,
            moon["longitude_deg"],
            moon["latitude_deg"],
            moon["distance_km"],
            latitude_deg,
            longitude_deg,
            altitude_m,
        )
        # Include standard horizon refraction + lunar semidiameter (~0.83 deg) or center > 0.0
        is_vis = alt_deg > 0.0
        return LunarContactVisibility(label, contact_jd, alt_deg, az_deg, is_vis)

    p1 = _eval_contact("P1", eclipse_obj.p1_jd_tt)
    u1 = _eval_contact("U1", eclipse_obj.u1_jd_tt)
    u2 = _eval_contact("U2", eclipse_obj.u2_jd_tt)
    greatest = _eval_contact("GREATEST", eclipse_obj.greatest_jd_tt)
    u3 = _eval_contact("U3", eclipse_obj.u3_jd_tt)
    u4 = _eval_contact("U4", eclipse_obj.u4_jd_tt)
    p4 = _eval_contact("P4", eclipse_obj.p4_jd_tt)

    defined_contacts = [c for c in (p1, u1, u2, greatest, u3, u4, p4) if c.jd_tt is not None]
    any_visible = any(c.visible for c in defined_contacts)
    all_visible = bool(defined_contacts) and all(c.visible for c in defined_contacts)
    summary: Literal["entirely_visible", "partially_visible", "not_visible"] = (
        "entirely_visible" if all_visible else ("partially_visible" if any_visible else "not_visible")
    )

    contacts_map = {
        "P1": p1,
        "U1": u1,
        "U2": u2,
        "GREATEST": greatest,
        "U3": u3,
        "U4": u4,
        "P4": p4,
        "p1": p1,
        "u1": u1,
        "u2": u2,
        "greatest": greatest,
        "u3": u3,
        "u4": u4,
        "p4": p4,
    }

    receipt_payload = {
        "component": "ephemeris_oss.engine.eclipses.lunar_eclipse_local_visibility",
        "package_version": __version__,
        "eclipse_receipt_sha256": eclipse_obj.receipt_sha256,
        "observer": {
            "latitude_deg": latitude_deg,
            "longitude_deg": longitude_deg,
            "altitude_m": altitude_m,
        },
        "visible": any_visible,
        "visibility_summary": summary,
        "contacts": {
            c.contact: {
                "jd_tt": c.jd_tt,
                "moon_altitude_deg": c.moon_altitude_deg,
                "moon_azimuth_deg": c.moon_azimuth_deg,
                "visible": c.visible,
            }
            for c in (p1, u1, u2, greatest, u3, u4, p4)
        },
    }
    digest = canonical_hash(receipt_payload)

    return LunarEclipseLocalVisibility(
        classification=eclipse_obj.classification,
        latitude_deg=latitude_deg,
        longitude_deg=longitude_deg,
        altitude_m=altitude_m,
        visible=any_visible,
        visibility_summary=summary,
        p1=p1,
        u1=u1,
        u2=u2,
        greatest=greatest,
        u3=u3,
        u4=u4,
        p4=p4,
        contacts=contacts_map,
        receipt=receipt_payload,
        receipt_sha256=digest,
    )


# ---------------------------------------------------------------------------
# Solar Eclipse Besselian Elements and Solvers
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class BesselianElements:
    """Fundamental plane Besselian elements at a TT instant (Chauvenet / Meeus)."""

    jd_tt: float
    x: float
    y: float
    sin_d: float
    cos_d: float
    d_deg: float
    mu_deg: float
    l1: float
    l2: float
    tan_f1: float
    tan_f2: float

    @property
    def mu(self) -> float:
        return self.mu_deg

    @property
    def d(self) -> float:
        return self.d_deg

    def __getitem__(self, key: str) -> Any:
        return getattr(self, key)


@dataclass(frozen=True)
class SolarEclipse:
    """Global Besselian solution for a solar eclipse."""

    classification: SolarEclipseClassification
    syzygy_jd_tt: float
    greatest_jd_tt: float
    gamma: float
    magnitude: float
    besselian_elements: BesselianElements
    central_latitude_deg: float | None
    central_longitude_deg: float | None
    receipt: Mapping[str, Any]
    receipt_sha256: str

    @property
    def eclipse_type(self) -> SolarEclipseClassification:
        return self.classification

    @property
    def max_magnitude(self) -> float:
        return self.magnitude

    @property
    def maximum_magnitude(self) -> float:
        return self.magnitude

    def __getitem__(self, key: str) -> Any:
        return getattr(self, key)


@dataclass(frozen=True)
class LocalSolarEclipse:
    """Topocentric local solar eclipse circumstances for a terrestrial observer."""

    classification: LocalSolarEclipseClassification
    latitude_deg: float
    longitude_deg: float
    altitude_m: float
    visible: bool
    c1_jd_tt: float | None
    c2_jd_tt: float | None
    max_jd_tt: float | None
    c3_jd_tt: float | None
    c4_jd_tt: float | None
    magnitude: float
    obscuration: float
    solar_altitude_deg: float
    solar_azimuth_deg: float
    duration_seconds: float
    receipt: Mapping[str, Any]
    receipt_sha256: str

    @property
    def eclipse_type(self) -> LocalSolarEclipseClassification:
        return self.classification

    @property
    def local_magnitude(self) -> float:
        return self.magnitude

    @property
    def altitude_deg(self) -> float:
        return self.solar_altitude_deg

    @property
    def azimuth_deg(self) -> float:
        return self.solar_azimuth_deg

    def __getitem__(self, key: str) -> Any:
        return getattr(self, key)


def besselian_elements_at(
    jd_tt: float,
    engine: Any = None,
    *,
    position_provider: Any = None,
) -> BesselianElements:
    """Compute instantaneous fundamental-plane Besselian elements at ``jd_tt``."""
    sun, moon, _ = _evaluate_sun_moon(jd_tt, engine, position_provider)
    eps_rad = _true_obliquity_rad(jd_tt)

    # Geocentric equatorial positions in units of Earth's equatorial radius
    r_sun = sun["distance_km"] / EARTH_EQUATORIAL_RADIUS_KM
    r_moon = moon["distance_km"] / EARTH_EQUATORIAL_RADIUS_KM

    xs, ys, zs = _ecliptic_to_equatorial_cartesian(sun["longitude_deg"], sun["latitude_deg"], r_sun, eps_rad)
    xm, ym, zm = _ecliptic_to_equatorial_cartesian(moon["longitude_deg"], moon["latitude_deg"], r_moon, eps_rad)

    # Vector G from Moon to Sun
    gx = xs - xm
    gy = ys - ym
    gz = zs - zm
    g_norm = math.sqrt(gx * gx + gy * gy + gz * gz)

    # Shadow axis right ascension a and declination d
    a_rad = math.atan2(gy, gx) % (2.0 * math.pi)
    sin_d = gz / g_norm
    cos_d = math.hypot(gx, gy) / g_norm
    d_rad = math.asin(max(-1.0, min(1.0, sin_d)))

    sin_a = math.sin(a_rad)
    cos_a = math.cos(a_rad)

    # Fundamental plane coordinates (x, y, z) of the Moon's center in Earth equatorial radii
    x = -xm * sin_a + ym * cos_a
    y = -xm * sin_d * cos_a - ym * sin_d * sin_a + zm * cos_d
    z = xm * cos_d * cos_a + ym * cos_d * sin_a + zm * sin_d

    # Ephemeris/Greenwich hour angle mu of the shadow axis
    gast = _gast_rad(jd_tt)
    mu_deg = math.degrees(gast - a_rad) % 360.0

    # Penumbral (f1) and umbral (f2) shadow cone angles
    sin_f1 = (K_SUN + K_MOON) / g_norm
    sin_f2 = (K_SUN - K_MOON) / g_norm
    tan_f1 = sin_f1 / math.sqrt(1.0 - sin_f1 * sin_f1)
    tan_f2 = sin_f2 / math.sqrt(1.0 - sin_f2 * sin_f2)

    # Cone vertex distances and radii on the fundamental plane (z = 0)
    c1 = z + K_MOON / sin_f1
    c2 = z - K_MOON / sin_f2
    l1 = c1 * tan_f1
    l2 = c2 * tan_f2

    return BesselianElements(
        jd_tt=jd_tt,
        x=x,
        y=y,
        sin_d=sin_d,
        cos_d=cos_d,
        d_deg=math.degrees(d_rad),
        mu_deg=mu_deg,
        l1=l1,
        l2=l2,
        tan_f1=tan_f1,
        tan_f2=tan_f2,
    )


def _central_line_lat_lon(elements: BesselianElements) -> tuple[float, float] | tuple[None, None]:
    """Compute geodetic (latitude_deg, longitude_deg) of the shadow axis on the WGS84 ellipsoid."""
    rho1 = math.sqrt(1.0 - WGS84_E2 * elements.cos_d * elements.cos_d)
    y1 = elements.y / rho1
    rad_sq = elements.x * elements.x + y1 * y1
    if rad_sq >= 1.0:
        return None, None

    zeta1 = math.sqrt(max(0.0, 1.0 - rad_sq))
    sin_d1 = elements.sin_d / rho1
    cos_d1 = math.sqrt(1.0 - WGS84_E2) * elements.cos_d / rho1

    sin_phi1 = y1 * cos_d1 + zeta1 * sin_d1
    cos_phi1_sin_h = elements.x
    cos_phi1_cos_h = -y1 * sin_d1 + zeta1 * cos_d1

    cos_phi1 = math.hypot(cos_phi1_sin_h, cos_phi1_cos_h)
    tan_phi = (sin_phi1 / cos_phi1) / math.sqrt(1.0 - WGS84_E2) if cos_phi1 > 1.0e-12 else math.copysign(1.0e12, sin_phi1)
    lat_deg = math.degrees(math.atan(tan_phi))

    h_deg = math.degrees(math.atan2(cos_phi1_sin_h, cos_phi1_cos_h))
    lon_deg = _signed_angle_diff_deg(h_deg, elements.mu_deg)
    return lat_deg, lon_deg


def solar_eclipse_at(
    approx_jd_tt: float,
    engine: Any = None,
    *,
    position_provider: Any = None,
) -> SolarEclipse | None:
    """Evaluate a Solar Eclipse near an approximate New Moon TT Julian Date.

    Returns :class:`SolarEclipse` if Earth intersects the lunar penumbra within
    ``approx_jd_tt +/- 5 days``, or ``None`` if no solar eclipse occurs at that syzygy.
    """
    if not math.isfinite(approx_jd_tt):
        raise ValueError("approx_jd_tt must be finite")

    roots = _find_syzygy_roots(approx_jd_tt - 5.0, approx_jd_tt + 5.0, 0.0, engine, position_provider)
    if not roots:
        return None
    syzygy_jd = min(roots, key=lambda r: abs(r - approx_jd_tt))

    _, _, provider_label = _evaluate_sun_moon(syzygy_jd, engine, position_provider)

    # Minimize shadow axis distance m(t) = hypot(x(t), y(t)) on the fundamental plane
    def axis_distance(t: float) -> float:
        el = besselian_elements_at(t, engine, position_provider=position_provider)
        return math.hypot(el.x, el.y)

    greatest_jd, min_dist = _minimize_scalar(
        axis_distance,
        syzygy_jd - 0.5,
        syzygy_jd + 0.5,
        tol_days=1.0e-8,
    )
    peak_el = besselian_elements_at(greatest_jd, engine, position_provider=position_provider)
    gamma_sign = 1.0 if peak_el.y >= 0.0 else -1.0
    gamma = gamma_sign * min_dist

    # Spheroidal limb radius along shadow axis direction
    rho1 = math.sqrt(1.0 - WGS84_E2 * peak_el.cos_d * peak_el.cos_d)
    abs_gamma = abs(gamma)

    if abs_gamma >= rho1 + peak_el.l1:
        return None

    if abs_gamma < CENTRAL_ECLIPSE_GAMMA_LIMIT:
        central_lat, central_lon = _central_line_lat_lon(peak_el)
        y1 = peak_el.y / rho1
        zeta = math.sqrt(max(0.0, 1.0 - peak_el.x * peak_el.x - y1 * y1))
        big_l1 = peak_el.l1 - zeta * peak_el.tan_f1
        big_l2 = peak_el.l2 - zeta * peak_el.tan_f2
        magnitude = (big_l1 - big_l2) / (big_l1 + big_l2)
        if big_l2 < 0.0 and peak_el.l2 > 0.0:
            classification: SolarEclipseClassification = "hybrid"
        elif big_l2 < 0.0:
            classification = "total"
        else:
            classification = "annular"
    else:
        central_lat, central_lon = None, None
        classification = "partial"
        u_limb = abs_gamma - CENTRAL_ECLIPSE_GAMMA_LIMIT
        magnitude = max(0.0, (peak_el.l1 - u_limb) / (2.0 * peak_el.l1 - 0.5465))

    receipt_payload = {
        "component": "ephemeris_oss.engine.eclipses.solar_eclipse",
        "package_version": __version__,
        "model": "chauvenet-meeus-besselian-fundamental-plane",
        "position_provider": provider_label,
        "syzygy_jd_tt": syzygy_jd,
        "greatest_jd_tt": greatest_jd,
        "classification": classification,
        "gamma": gamma,
        "magnitude": magnitude,
        "central_latitude_deg": central_lat,
        "central_longitude_deg": central_lon,
        "besselian_elements": asdict(peak_el),
    }
    digest = canonical_hash(receipt_payload)

    return SolarEclipse(
        classification=classification,
        syzygy_jd_tt=syzygy_jd,
        greatest_jd_tt=greatest_jd,
        gamma=gamma,
        magnitude=magnitude,
        besselian_elements=peak_el,
        central_latitude_deg=central_lat,
        central_longitude_deg=central_lon,
        receipt=receipt_payload,
        receipt_sha256=digest,
    )


def find_solar_eclipses(
    start_jd_tt: float,
    end_jd_tt: float,
    engine: Any = None,
    *,
    position_provider: Any = None,
) -> tuple[SolarEclipse, ...]:
    """Find all solar eclipses occurring in the TT interval [start_jd_tt, end_jd_tt]."""
    syzygies = _find_syzygy_roots(start_jd_tt, end_jd_tt, 0.0, engine, position_provider)
    results: list[SolarEclipse] = []
    for syz_jd in syzygies:
        _, moon, _ = _evaluate_sun_moon(syz_jd, engine, position_provider)
        if abs(moon["latitude_deg"]) > 2.0:
            continue
        eclipse = solar_eclipse_at(syz_jd, engine, position_provider=position_provider)
        if eclipse is not None and start_jd_tt <= eclipse.greatest_jd_tt <= end_jd_tt:
            results.append(eclipse)
    return tuple(results)


def _observer_fundamental_plane(
    jd_tt: float,
    latitude_deg: float,
    longitude_deg: float,
    altitude_m: float,
    engine: Any = None,
    position_provider: Any = None,
) -> dict[str, float]:
    """Compute observer Besselian coordinates (xi, eta, zeta) and local shadow cone radii (L1, L2, delta)."""
    el = besselian_elements_at(jd_tt, engine, position_provider=position_provider)

    phi = math.radians(latitude_deg)
    u_lat = math.atan((1.0 - WGS84_FLATTENING) * math.tan(phi))
    h_er = altitude_m / (EARTH_EQUATORIAL_RADIUS_KM * 1000.0)
    rho_sin_phi = (1.0 - WGS84_FLATTENING) * math.sin(u_lat) + h_er * math.sin(phi)
    rho_cos_phi = math.cos(u_lat) + h_er * math.cos(phi)

    h_rad = math.radians(el.mu_deg + longitude_deg)
    sin_h = math.sin(h_rad)
    cos_h = math.cos(h_rad)

    xi = rho_cos_phi * sin_h
    eta = rho_sin_phi * el.cos_d - rho_cos_phi * el.sin_d * cos_h
    zeta = rho_sin_phi * el.sin_d + rho_cos_phi * el.cos_d * cos_h

    u = el.x - xi
    v = el.y - eta
    delta = math.hypot(u, v)

    big_l1 = el.l1 - zeta * el.tan_f1
    big_l2 = el.l2 - zeta * el.tan_f2

    return {
        "xi": xi,
        "eta": eta,
        "zeta": zeta,
        "u": u,
        "v": v,
        "delta": delta,
        "L1": big_l1,
        "L2": big_l2,
    }


def _solar_disk_obscuration(magnitude: float, k_ratio: float, is_central: bool, l2_val: float) -> float:
    """Compute fraction of solar disk area obscured by the lunar disk (Meeus / Espenak)."""
    if magnitude <= 0.0:
        return 0.0
    if is_central:
        return 1.0 if l2_val <= 0.0 else min(1.0, k_ratio * k_ratio)

    # Normalized center-to-center distance in units of solar apparent radius = 1
    d = 1.0 + k_ratio - 2.0 * magnitude
    if d >= 1.0 + k_ratio:
        return 0.0
    if d <= abs(1.0 - k_ratio):
        return 1.0 if k_ratio >= 1.0 else k_ratio * k_ratio

    cos_a1 = max(-1.0, min(1.0, (1.0 + d * d - k_ratio * k_ratio) / (2.0 * d)))
    cos_a2 = max(-1.0, min(1.0, (k_ratio * k_ratio + d * d - 1.0) / (2.0 * k_ratio * d)))
    a1 = math.acos(cos_a1)
    a2 = math.acos(cos_a2)
    radicand = max(0.0, (-d + 1.0 + k_ratio) * (d + 1.0 - k_ratio) * (d - 1.0 + k_ratio) * (d + 1.0 + k_ratio))
    overlap_area = a1 + k_ratio * k_ratio * a2 - 0.5 * math.sqrt(radicand)
    return max(0.0, min(1.0, overlap_area / math.pi))


def solar_eclipse_local_circumstances(
    eclipse: SolarEclipse | float,
    latitude_deg: float,
    longitude_deg: float,
    altitude_m: float = 0.0,
    engine: Any = None,
    *,
    position_provider: Any = None,
) -> LocalSolarEclipse:
    """Compute topocentric local solar eclipse circumstances (C1, C2, Max, C3, C4, magnitude, obscuration)."""
    if not (-90.0 <= latitude_deg <= 90.0):
        raise ValueError("latitude_deg must be in [-90, 90]")
    if not (-180.0 <= longitude_deg <= 180.0):
        raise ValueError("longitude_deg must be in [-180, 180]")

    if isinstance(eclipse, (int, float)):
        resolved = solar_eclipse_at(float(eclipse), engine, position_provider=position_provider)
        if resolved is None:
            raise ValueError(f"no solar eclipse near JD TT {eclipse}")
        eclipse_obj = resolved
    else:
        eclipse_obj = eclipse

    center_jd = eclipse_obj.greatest_jd_tt
    window = 0.30  # +/- 7.2 hours around global greatest eclipse

    def local_normalized_sep(t: float) -> float:
        st = _observer_fundamental_plane(t, latitude_deg, longitude_deg, altitude_m, engine, position_provider)
        # Penalize night-side geometry so we find the daytime local minimum
        if st["zeta"] < -0.05:
            return 10.0 + st["delta"]
        return st["delta"]

    max_jd, _ = _minimize_scalar(
        local_normalized_sep,
        center_jd - window,
        center_jd + window,
        tol_days=1.0e-8,
    )
    peak = _observer_fundamental_plane(max_jd, latitude_deg, longitude_deg, altitude_m, engine, position_provider)
    sun_at_max, _, provider_label = _evaluate_sun_moon(max_jd, engine, position_provider)
    alt_deg, az_deg = _topocentric_alt_az_deg(
        max_jd,
        sun_at_max["longitude_deg"],
        sun_at_max["latitude_deg"],
        sun_at_max["distance_km"],
        latitude_deg,
        longitude_deg,
        altitude_m,
    )

    delta = peak["delta"]
    big_l1 = peak["L1"]
    big_l2 = peak["L2"]

    if delta >= big_l1 or peak["zeta"] < -0.02:
        receipt_payload = {
            "component": "ephemeris_oss.engine.eclipses.solar_eclipse_local_circumstances",
            "package_version": __version__,
            "position_provider": provider_label,
            "eclipse_receipt_sha256": eclipse_obj.receipt_sha256,
            "observer": {"latitude_deg": latitude_deg, "longitude_deg": longitude_deg, "altitude_m": altitude_m},
            "classification": "none",
            "visible": False,
            "magnitude": 0.0,
            "obscuration": 0.0,
        }
        return LocalSolarEclipse(
            classification="none",
            latitude_deg=latitude_deg,
            longitude_deg=longitude_deg,
            altitude_m=altitude_m,
            visible=False,
            c1_jd_tt=None,
            c2_jd_tt=None,
            max_jd_tt=None,
            c3_jd_tt=None,
            c4_jd_tt=None,
            magnitude=0.0,
            obscuration=0.0,
            solar_altitude_deg=alt_deg,
            solar_azimuth_deg=az_deg,
            duration_seconds=0.0,
            receipt=receipt_payload,
            receipt_sha256=canonical_hash(receipt_payload),
        )

    k_ratio = (big_l1 - big_l2) / (big_l1 + big_l2)
    is_central = delta <= abs(big_l2)
    if is_central:
        local_class: LocalSolarEclipseClassification = "total" if big_l2 <= 0.0 else "annular"
        # Standard Besselian central magnitude is the Moon/Sun apparent radius ratio k
        magnitude = k_ratio
    else:
        local_class = "partial"
        magnitude = (big_l1 - delta) / (big_l1 + big_l2)

    obscuration = _solar_disk_obscuration(magnitude, k_ratio, is_central, big_l2)

    def outer_margin(t: float) -> float:
        st = _observer_fundamental_plane(t, latitude_deg, longitude_deg, altitude_m, engine, position_provider)
        return st["L1"] - st["delta"]

    c1_jd = _bisect_root(outer_margin, max_jd - 0.20, max_jd, tol_days=1.0e-8)
    c4_jd = _bisect_root(outer_margin, max_jd, max_jd + 0.20, tol_days=1.0e-8)

    c2_jd: float | None = None
    c3_jd: float | None = None
    duration_sec = 0.0
    if is_central:
        def inner_margin(t: float) -> float:
            st = _observer_fundamental_plane(t, latitude_deg, longitude_deg, altitude_m, engine, position_provider)
            return abs(st["L2"]) - st["delta"]

        c2_jd = _bisect_root(inner_margin, max_jd - 0.02, max_jd, tol_days=1.0e-8)
        c3_jd = _bisect_root(inner_margin, max_jd, max_jd + 0.02, tol_days=1.0e-8)
        if c2_jd is not None and c3_jd is not None:
            duration_sec = (c3_jd - c2_jd) * SECONDS_PER_DAY

    visible = alt_deg > -0.833  # Visible above horizon (with refraction + solar upper limb)

    receipt_payload = {
        "component": "ephemeris_oss.engine.eclipses.solar_eclipse_local_circumstances",
        "package_version": __version__,
        "position_provider": provider_label,
        "eclipse_receipt_sha256": eclipse_obj.receipt_sha256,
        "observer": {
            "latitude_deg": latitude_deg,
            "longitude_deg": longitude_deg,
            "altitude_m": altitude_m,
        },
        "classification": local_class,
        "visible": visible,
        "c1_jd_tt": c1_jd,
        "c2_jd_tt": c2_jd,
        "max_jd_tt": max_jd,
        "c3_jd_tt": c3_jd,
        "c4_jd_tt": c4_jd,
        "magnitude": magnitude,
        "obscuration": obscuration,
        "solar_altitude_deg": alt_deg,
        "solar_azimuth_deg": az_deg,
        "duration_seconds": duration_sec,
    }
    digest = canonical_hash(receipt_payload)

    return LocalSolarEclipse(
        classification=local_class,
        latitude_deg=latitude_deg,
        longitude_deg=longitude_deg,
        altitude_m=altitude_m,
        visible=visible,
        c1_jd_tt=c1_jd,
        c2_jd_tt=c2_jd,
        max_jd_tt=max_jd,
        c3_jd_tt=c3_jd,
        c4_jd_tt=c4_jd,
        magnitude=magnitude,
        obscuration=obscuration,
        solar_altitude_deg=alt_deg,
        solar_azimuth_deg=az_deg,
        duration_seconds=duration_sec,
        receipt=receipt_payload,
        receipt_sha256=digest,
    )


__all__ = [
    "BesselianElements",
    "CENTRAL_ECLIPSE_GAMMA_LIMIT",
    "DANJON_ATMOSPHERIC_ENLARGEMENT",
    "LocalSolarEclipse",
    "LunarContactVisibility",
    "LunarEclipse",
    "LunarEclipseLocalVisibility",
    "SolarEclipse",
    "besselian_elements_at",
    "find_lunar_eclipses",
    "find_solar_eclipses",
    "lunar_eclipse_at",
    "lunar_eclipse_local_visibility",
    "solar_eclipse_at",
    "solar_eclipse_local_circumstances",
]
