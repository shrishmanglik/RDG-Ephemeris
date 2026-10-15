"""Clean-room Planetary Phenomena, Retrograde Station, Vedic Combustion (Moudhya/Astangata),
Graha Yuddha (Planetary War), and Sankranti / Sign Ingress Solver.

References
----------
* Meeus, J. (1998), Astronomical Algorithms, 2nd ed., Chapters 25, 31, 33, 36, 47,
  Willmann-Bell.
* Standish, E. M. & Williams, J. G. (1992), Orbital Ephemerides of the Sun, Moon,
  and Planets, in Explanatory Supplement to the Astronomical Almanac.
* Surya Siddhanta, Chapter 2 (Spashtadhikara: True Places and Retrograde Motion),
  Chapter 7 (Graha Yuddha Adhikara: Planetary Conjunction and War),
  Chapter 9 (Udayastadhikara: Heliacal Rising, Setting, and Combustion Orbs),
  trans. E. Burgess (1860), Journal of the American Oriental Society, 6, 141-498.
* Varahamihira, Brihat Samhita, Chapter 17 (Graha Yuddha Adhyaya): planetary war
  classification and Venus (Shukra) victory rules.
* IAU SOFA / ERFA library for precession, nutation, and sidereal reduction.
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Any, Callable, Literal, Mapping, Sequence

import erfa

from .._version import __version__
from .conventions import ayanamsa_degrees, normalize_degrees
from .eclipses import (
    AU_KM,
    J2000_TT_JD,
    JULIAN_CENTURY_DAYS,
    _bisect_root,
    _meeus_moon_apparent,
    _meeus_sun_apparent,
    _minimize_scalar,
    _signed_angle_diff_deg,
)
from .receipt import canonical_hash

# Classical Surya Siddhanta (Ch. 9, vv. 6-9) angular combustion (Astangata / Moudhya) orbs in degrees
SURYA_SIDDHANTA_COMBUSTION_ORBS_DEG: Mapping[str, dict[str, float]] = {
    "moon": {"direct": 12.0, "retrograde": 12.0},
    "mars": {"direct": 17.0, "retrograde": 17.0},
    "mercury": {"direct": 14.0, "retrograde": 12.0},
    "jupiter": {"direct": 11.0, "retrograde": 11.0},
    "venus": {"direct": 10.0, "retrograde": 8.0},
    "saturn": {"direct": 15.0, "retrograde": 15.0},
}

# Classical Cazimi threshold: 17 arcminutes (17/60 deg) from solar center
CAZIMI_ORB_DEG = 17.0 / 60.0

# Five Taragrahas (star-planets eligible for Graha Yuddha / planetary war)
TARAGRAHAS: tuple[str, ...] = ("mars", "mercury", "jupiter", "venus", "saturn")

# Intrinsic apparent brightness / disc dominance order in classical Jyotish (higher wins ties)
TARAGRAHA_BRIGHTNESS_RANK: Mapping[str, int] = {
    "venus": 5,
    "jupiter": 4,
    "mars": 3,
    "mercury": 2,
    "saturn": 1,
}

# Mean planetary equatorial radii in km (IAU) for apparent disc diameter calculations
PLANET_EQUATORIAL_RADIUS_KM: Mapping[str, float] = {
    "mercury": 2439.7,
    "venus": 6051.8,
    "mars": 3396.2,
    "jupiter": 71492.0,
    "saturn": 60268.0,
}

RASI_NAMES: tuple[str, ...] = (
    "Mesha",
    "Vrishabha",
    "Mithuna",
    "Karka",
    "Simha",
    "Kanya",
    "Tula",
    "Vrischika",
    "Dhanu",
    "Makara",
    "Kumbha",
    "Meena",
)

WESTERN_SIGN_NAMES: tuple[str, ...] = (
    "Aries",
    "Taurus",
    "Gemini",
    "Cancer",
    "Leo",
    "Virgo",
    "Libra",
    "Scorpio",
    "Sagittarius",
    "Capricorn",
    "Aquarius",
    "Pisces",
)

SANKRANTI_NAMES: tuple[str, ...] = (
    "Mesha Sankranti",
    "Vrishabha Sankranti",
    "Mithuna Sankranti",
    "Karka Sankranti",
    "Simha Sankranti",
    "Kanya Sankranti",
    "Tula Sankranti",
    "Vrischika Sankranti",
    "Dhanu Sankranti",
    "Makar Sankranti",
    "Kumbha Sankranti",
    "Meena Sankranti",
)


# ---------------------------------------------------------------------------
# Built-in Clean-Room Analytical Planetary Evaluator (Meeus Ch. 31 / Standish)
# ---------------------------------------------------------------------------

# Mean orbital elements of the planets on the ecliptic of date (Meeus Table 31.A):
# (a_AU, L0, L1, e0, e1, i0, i1, omega0, omega1, pi0, pi1)
# where T is in Julian centuries from J2000.0
_ORBITAL_ELEMENTS: Mapping[str, tuple[float, ...]] = {
    "mercury": (
        0.387098310,
        252.250906, 149474.0722491,
        0.20563175, 0.000020407,
        7.004986, 0.0018215,
        48.330893, 1.1861883,
        77.456119, 1.5564776,
    ),
    "venus": (
        0.723329820,
        181.979801, 58519.2130302,
        0.00677192, -0.000047765,
        3.394662, 0.0010037,
        76.679920, 0.9011206,
        131.563703, 1.4022288,
    ),
    "earth": (
        1.000001018,
        100.466457, 36000.7698278,
        0.01670863, -0.000042037,
        0.0, 0.0,
        0.0, 0.0,
        102.937348, 1.7195366,
    ),
    "mars": (
        1.523679342,
        355.433000, 19141.6964471,
        0.09340065, 0.000090484,
        1.849726, -0.0006011,
        49.558093, 0.7720959,
        336.060234, 1.8410449,
    ),
    "jupiter": (
        5.202603209,
        34.351519, 3036.3027748,
        0.04849793, 0.000163225,
        1.303267, -0.0054965,
        100.464407, 1.0209774,
        14.331207, 1.6126352,
    ),
    "saturn": (
        9.554909192,
        50.077444, 1223.5110686,
        0.05554814, -0.000346641,
        2.488879, -0.0037362,
        113.665503, 0.8770880,
        93.057237, 1.9637613,
    ),
}


def _heliocentric_ecliptic_xyz_au(body: str, jd_tt: float) -> tuple[float, float, float]:
    """Compute heliocentric ecliptic-of-date Cartesian coordinates (AU) via Kepler's equation."""
    t = (jd_tt - J2000_TT_JD) / JULIAN_CENTURY_DAYS
    a, l0, l1, e0, e1, i0, i1, om0, om1, pi0, pi1 = _ORBITAL_ELEMENTS[body]

    mean_lon = (l0 + l1 * t) % 360.0
    e = e0 + e1 * t
    inc = math.radians(i0 + i1 * t)
    omega = math.radians((om0 + om1 * t) % 360.0)
    varpi = (pi0 + pi1 * t) % 360.0
    m_deg = (mean_lon - varpi) % 360.0

    # Great Jupiter-Saturn inequality perturbations (Meeus Ch. 31 / Simon et al.)
    if body in ("jupiter", "saturn"):
        m_jup = math.radians((20.0202 + 3034.69202 * t) % 360.0)
        m_sat = math.radians((317.0207 + 1221.55147 * t) % 360.0)
        arg_js = 5.0 * m_sat - 2.0 * m_jup + math.radians(67.652 - 2.13 * t)
        if body == "jupiter":
            m_deg = (m_deg + 0.3314 * math.sin(arg_js)) % 360.0
        else:
            m_deg = (m_deg - 0.8142 * math.sin(arg_js)) % 360.0

    m_rad = math.radians(m_deg)
    ecc_anom = m_rad + e * math.sin(m_rad)
    for _ in range(12):
        delta = (ecc_anom - e * math.sin(ecc_anom) - m_rad) / (1.0 - e * math.cos(ecc_anom))
        ecc_anom -= delta
        if abs(delta) <= 1.0e-14:
            break

    true_anom = 2.0 * math.atan2(
        math.sqrt(1.0 + e) * math.sin(0.5 * ecc_anom),
        math.sqrt(1.0 - e) * math.cos(0.5 * ecc_anom),
    )
    r_au = a * (1.0 - e * math.cos(ecc_anom))
    u_arg = true_anom + math.radians((varpi - (om0 + om1 * t)) % 360.0)

    cos_u = math.cos(u_arg)
    sin_u = math.sin(u_arg)
    cos_o = math.cos(omega)
    sin_o = math.sin(omega)
    cos_i = math.cos(inc)
    sin_i = math.sin(inc)

    x = r_au * (cos_o * cos_u - sin_o * sin_u * cos_i)
    y = r_au * (sin_o * cos_u + cos_o * sin_u * cos_i)
    z = r_au * (sin_u * sin_i)
    return x, y, z


def _builtin_planet_apparent(body: str, jd_tt: float) -> dict[str, float]:
    """Built-in clean-room apparent geocentric ecliptic position of any classical body."""
    key = body.strip().lower()
    if key == "sun":
        return _meeus_sun_apparent(jd_tt)
    if key == "moon":
        return _meeus_moon_apparent(jd_tt)
    if key not in _ORBITAL_ELEMENTS or key == "earth":
        raise ValueError(f"unsupported body for phenomena evaluation: {body!r}")

    xe, ye, ze = _heliocentric_ecliptic_xyz_au("earth", jd_tt)
    # 1-step light-time retardation
    xp, yp, zp = _heliocentric_ecliptic_xyz_au(key, jd_tt)
    dist_au = math.sqrt((xp - xe) ** 2 + (yp - ye) ** 2 + (zp - ze) ** 2)
    tau_days = dist_au * 0.00577551833  # light-time per AU in days
    xp, yp, zp = _heliocentric_ecliptic_xyz_au(key, jd_tt - tau_days)

    dx = xp - xe
    dy = yp - ye
    dz = zp - ze
    dist_au = math.sqrt(dx * dx + dy * dy + dz * dz)

    lon_geom = math.degrees(math.atan2(dy, dx)) % 360.0
    lat_geom = math.degrees(math.asin(max(-1.0, min(1.0, dz / dist_au))))

    # Nutation in longitude and annual aberration
    dpsi_rad, _ = erfa.nut06a(J2000_TT_JD, jd_tt - J2000_TT_JD)
    sun_lon_rad = math.radians(_meeus_sun_apparent(jd_tt)["longitude_deg"])
    aberr_lon_deg = -20.4898 / 3600.0 * math.cos(sun_lon_rad - math.radians(lon_geom)) / max(0.1, math.cos(math.radians(lat_geom)))
    lon_app = (lon_geom + math.degrees(float(dpsi_rad)) + aberr_lon_deg) % 360.0

    return {
        "longitude_deg": lon_app,
        "latitude_deg": lat_geom,
        "distance_km": dist_au * AU_KM,
    }


def _evaluate_body_position(
    body: str,
    jd_tt: float,
    engine: Any = None,
    position_provider: Any = None,
) -> tuple[dict[str, float], str]:
    """Evaluate apparent geocentric ecliptic (longitude_deg, latitude_deg) of a body at jd_tt."""
    key = body.strip().lower()
    source = position_provider if position_provider is not None else engine
    if source is None:
        return _builtin_planet_apparent(key, jd_tt), "builtin-keplerian-meeus"

    provider_label = "custom-position-provider"
    raw_positions: Mapping[str, Any]
    if hasattr(source, "positions_tt") and callable(source.positions_tt):
        res = source.positions_tt(jd_tt, (key,))
        raw_positions = res.value if hasattr(res, "value") else res
        provider_label = "engine.positions_tt"
    elif callable(source):
        res = source(jd_tt, (key,))
        raw_positions = res.value if hasattr(res, "value") else res
        engine_obj = getattr(source, "__self__", None)
        if engine_obj is not None and hasattr(engine_obj, "positions_tt"):
            provider_label = "engine.positions_tt"
    else:
        raise ValueError("engine or position_provider must be an Engine instance, a callable, or None")

    entry: Mapping[str, Any] | None = None
    for k, v in raw_positions.items():
        if k.strip().lower() == key:
            entry = v
            break
    if entry is None:
        raise ValueError(f"position provider returned no entry for {body!r}")

    lon = float(entry["longitude_deg"]) % 360.0
    lat = float(entry.get("latitude_deg", 0.0))
    dist_km = float(entry["distance_km"]) if "distance_km" in entry else _builtin_planet_apparent(key, jd_tt)["distance_km"]
    return {"longitude_deg": lon, "latitude_deg": lat, "distance_km": dist_km}, provider_label


def _longitude_speed_deg_per_day(
    body: str,
    jd_tt: float,
    engine: Any = None,
    position_provider: Any = None,
    step_days: float = 1.0e-3,
) -> float:
    """Compute instantaneous apparent ecliptic longitudinal velocity d(lambda)/dt in deg/day."""
    pos_before, _ = _evaluate_body_position(body, jd_tt - step_days, engine, position_provider)
    pos_after, _ = _evaluate_body_position(body, jd_tt + step_days, engine, position_provider)
    delta_deg = _signed_angle_diff_deg(pos_after["longitude_deg"], pos_before["longitude_deg"])
    return delta_deg / (2.0 * step_days)


def _longitude_acceleration_deg_per_day2(
    body: str,
    jd_tt: float,
    engine: Any = None,
    position_provider: Any = None,
    step_days: float = 0.05,
) -> float:
    """Compute second derivative d^2(lambda)/dt^2 in deg/day^2."""
    v_before = _longitude_speed_deg_per_day(body, jd_tt - step_days, engine, position_provider)
    v_after = _longitude_speed_deg_per_day(body, jd_tt + step_days, engine, position_provider)
    return (v_after - v_before) / (2.0 * step_days)


# ---------------------------------------------------------------------------
# 1. Retrograde Station & Shadow Period Solver
# ---------------------------------------------------------------------------

StationKind = Literal["station_retrograde", "station_direct"]


@dataclass(frozen=True)
class RetrogradeStationEvent:
    """Exact planetary retrograde or direct station with shadow-period boundaries."""

    body: str
    kind: StationKind
    jd_tt: float
    longitude_deg: float
    sidereal_longitude_deg: float
    latitude_deg: float
    speed_deg_per_day: float
    acceleration_deg_per_day2: float
    shadow_entry_jd_tt: float | None
    shadow_exit_jd_tt: float | None
    companion_station_jd_tt: float | None
    companion_station_longitude_deg: float | None
    receipt: Mapping[str, Any]
    receipt_sha256: str

    @property
    def station_type(self) -> StationKind:
        return self.kind

    @property
    def is_retrograde_station(self) -> bool:
        return self.kind == "station_retrograde"

    @property
    def pre_shadow_jd_tt(self) -> float | None:
        return self.shadow_entry_jd_tt

    @property
    def post_shadow_jd_tt(self) -> float | None:
        return self.shadow_exit_jd_tt

    def __getitem__(self, key: str) -> Any:
        return getattr(self, key)


def _solve_longitude_crossing_near(
    body: str,
    target_lon_deg: float,
    start_jd_tt: float,
    end_jd_tt: float,
    engine: Any = None,
    position_provider: Any = None,
    step_days: float = 3.0,
) -> float | None:
    """Find a direct crossing of target_lon_deg in [start_jd_tt, end_jd_tt]."""
    if end_jd_tt <= start_jd_tt:
        return None

    def residual(t: float) -> float:
        pos, _ = _evaluate_body_position(body, t, engine, position_provider)
        return _signed_angle_diff_deg(pos["longitude_deg"], target_lon_deg)

    t_prev = start_jd_tt
    f_prev = residual(t_prev)
    step = min(step_days, max(0.5, (end_jd_tt - start_jd_tt) / 10.0))
    while t_prev < end_jd_tt:
        t_next = min(end_jd_tt, t_prev + step)
        f_next = residual(t_next)
        if f_prev * f_next <= 0.0 and abs(f_next - f_prev) < 90.0:
            root = _bisect_root(residual, t_prev, t_next, tol_days=1.0e-7)
            if root is not None:
                return root
        t_prev = t_next
        f_prev = f_next
    return None


def find_retrograde_stations(
    body: str,
    start_jd_tt: float,
    end_jd_tt: float,
    engine: Any = None,
    *,
    position_provider: Any = None,
    ayanamsa: str = "lahiri",
    compute_shadow_periods: bool = True,
) -> tuple[RetrogradeStationEvent, ...]:
    """Find all retrograde and direct stations of ``body`` in ``[start_jd_tt, end_jd_tt]``.

    Solves ``d(lambda)/dt = 0`` to sub-second accuracy, classifies ``station_retrograde``
    (``d^2(lambda)/dt^2 < 0``) vs ``station_direct`` (``d^2(lambda)/dt^2 > 0``), and
    computes the pre-retrograde shadow entry and post-retrograde shadow exit boundaries.
    """
    if end_jd_tt <= start_jd_tt:
        raise ValueError("end_jd_tt must be greater than start_jd_tt")
    key = body.strip().lower()
    if key in ("sun", "moon"):
        return ()
    if key not in TARAGRAHAS:
        raise ValueError(f"retrograde stations apply to the five planets {TARAGRAHAS}, got {body!r}")

    _, provider_label = _evaluate_body_position(key, start_jd_tt, engine, position_provider)

    # Coarse step size smaller than half of the shortest retrograde duration (Mercury ~21 days)
    coarse_step = 4.0 if key == "mercury" else 6.0
    step = min(coarse_step, max(0.5, (end_jd_tt - start_jd_tt) / 12.0))

    # Sample longitudes on coarse grid and detect sign changes in secant velocity
    times: list[float] = []
    t_cur = start_jd_tt
    while t_cur < end_jd_tt:
        times.append(t_cur)
        t_cur = min(end_jd_tt, t_cur + step)
    if not times or times[-1] < end_jd_tt:
        times.append(end_jd_tt)

    lons = [_evaluate_body_position(key, t, engine, position_provider)[0]["longitude_deg"] for t in times]
    secant_speeds = [
        _signed_angle_diff_deg(lons[i + 1], lons[i]) / (times[i + 1] - times[i])
        for i in range(len(times) - 1)
    ]

    def speed_fn(t: float) -> float:
        return _longitude_speed_deg_per_day(key, t, engine, position_provider, step_days=1.0e-3)

    candidate_brackets: list[tuple[float, float]] = []
    for i in range(len(secant_speeds) - 1):
        if secant_speeds[i] * secant_speeds[i + 1] <= 0.0:
            candidate_brackets.append((times[i], times[i + 2]))
    # Also check first and last intervals in case a station sits near the boundary
    if secant_speeds:
        v_start = speed_fn(start_jd_tt)
        if v_start * secant_speeds[0] <= 0.0:
            candidate_brackets.insert(0, (times[0], times[min(2, len(times) - 1)]))
        v_end = speed_fn(end_jd_tt)
        if v_end * secant_speeds[-1] <= 0.0:
            candidate_brackets.append((times[max(0, len(times) - 3)], times[-1]))

    raw_roots: list[float] = []
    for left_jd, right_jd in candidate_brackets:
        root = _bisect_root(speed_fn, left_jd, right_jd, tol_days=1.0e-7)
        if root is not None and start_jd_tt <= root <= end_jd_tt:
            if not raw_roots or abs(root - raw_roots[-1]) > 1.0:
                raw_roots.append(root)

    # Half-loop lookahead/lookbehind window by planet to pair SR/SD stations and shadow boundaries
    loop_window = {
        "mercury": 35.0,
        "venus": 60.0,
        "mars": 100.0,
        "jupiter": 150.0,
        "saturn": 170.0,
    }[key]

    def _find_companion_station(station_jd: float, station_kind: StationKind) -> tuple[float, float] | tuple[None, None]:
        if station_kind == "station_retrograde":
            s_left, s_right = station_jd + 5.0, station_jd + loop_window
        else:
            s_left, s_right = station_jd - loop_window, station_jd - 5.0
        # Coarse scan with 5-day step for companion
        c_step = 4.0 if key == "mercury" else 6.0
        t_p = s_left
        lon_p = _evaluate_body_position(key, t_p, engine, position_provider)[0]["longitude_deg"]
        prev_v: float | None = None
        prev_t = t_p
        while t_p < s_right:
            t_n = min(s_right, t_p + c_step)
            lon_n = _evaluate_body_position(key, t_n, engine, position_provider)[0]["longitude_deg"]
            cur_v = _signed_angle_diff_deg(lon_n, lon_p) / (t_n - t_p)
            if prev_v is not None and prev_v * cur_v <= 0.0:
                c_root = _bisect_root(speed_fn, prev_t, t_n, tol_days=1.0e-7)
                if c_root is not None:
                    c_lon = _evaluate_body_position(key, c_root, engine, position_provider)[0]["longitude_deg"]
                    return c_root, c_lon
            prev_t = t_p
            prev_v = cur_v
            t_p = t_n
            lon_p = lon_n
        return None, None

    events: list[RetrogradeStationEvent] = []
    for root_jd in raw_roots:
        pos, _ = _evaluate_body_position(key, root_jd, engine, position_provider)
        lon_deg = pos["longitude_deg"]
        lat_deg = pos["latitude_deg"]
        v_res = speed_fn(root_jd)
        accel = _longitude_acceleration_deg_per_day2(key, root_jd, engine, position_provider)
        kind: StationKind = "station_retrograde" if accel < 0.0 else "station_direct"

        try:
            ay_deg = ayanamsa_degrees(root_jd, ayanamsa) if ayanamsa else 0.0
        except Exception:
            ay_deg = 0.0
        sidereal_lon = normalize_degrees(lon_deg - ay_deg)

        comp_jd: float | None = None
        comp_lon: float | None = None
        shadow_entry: float | None = None
        shadow_exit: float | None = None

        if compute_shadow_periods:
            comp_jd, comp_lon = _find_companion_station(root_jd, kind)
            if comp_jd is not None and comp_lon is not None:
                if kind == "station_retrograde":
                    sr_jd, sr_lon = root_jd, lon_deg
                    sd_jd, sd_lon = comp_jd, comp_lon
                else:
                    sd_jd, sd_lon = root_jd, lon_deg
                    sr_jd, sr_lon = comp_jd, comp_lon
                shadow_entry = _solve_longitude_crossing_near(
                    key, sd_lon, sr_jd - loop_window, sr_jd - 2.0, engine, position_provider
                )
                shadow_exit = _solve_longitude_crossing_near(
                    key, sr_lon, sd_jd + 2.0, sd_jd + loop_window, engine, position_provider
                )

        receipt_payload = {
            "component": "ephemeris_oss.engine.phenomena.retrograde_station",
            "package_version": __version__,
            "position_provider": provider_label,
            "body": key,
            "kind": kind,
            "jd_tt": root_jd,
            "longitude_deg": lon_deg,
            "sidereal_longitude_deg": sidereal_lon,
            "acceleration_deg_per_day2": accel,
            "shadow_entry_jd_tt": shadow_entry,
            "shadow_exit_jd_tt": shadow_exit,
            "companion_station_jd_tt": comp_jd,
        }
        digest = canonical_hash(receipt_payload)

        events.append(
            RetrogradeStationEvent(
                body=key,
                kind=kind,
                jd_tt=root_jd,
                longitude_deg=lon_deg,
                sidereal_longitude_deg=sidereal_lon,
                latitude_deg=lat_deg,
                speed_deg_per_day=v_res,
                acceleration_deg_per_day2=accel,
                shadow_entry_jd_tt=shadow_entry,
                shadow_exit_jd_tt=shadow_exit,
                companion_station_jd_tt=comp_jd,
                companion_station_longitude_deg=comp_lon,
                receipt=receipt_payload,
                receipt_sha256=digest,
            )
        )

    return tuple(events)


# ---------------------------------------------------------------------------
# 2. Vedic Combustion (Moudhya / Astangata) & Cazimi Solver
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class CombustionStatus:
    """Instantaneous Surya Siddhanta combustion (Astangata/Moudhya) and Cazimi state."""

    body: str
    sun_longitude_deg: float
    body_longitude_deg: float
    is_retrograde: bool
    angular_separation_deg: float
    signed_elongation_deg: float
    orb_threshold_deg: float
    is_combust: bool
    is_cazimi: bool
    state: Literal["cazimi", "combust", "visible"]
    receipt: Mapping[str, Any]
    receipt_sha256: str

    @property
    def combust(self) -> bool:
        return self.is_combust

    @property
    def astangata(self) -> bool:
        return self.is_combust

    @property
    def moudhya(self) -> bool:
        return self.is_combust

    @property
    def cazimi(self) -> bool:
        return self.is_cazimi

    @property
    def separation_deg(self) -> float:
        return self.angular_separation_deg

    @property
    def threshold_deg(self) -> float:
        return self.orb_threshold_deg

    def __getitem__(self, key: str) -> Any:
        return getattr(self, key)


@dataclass(frozen=True)
class CombustionWindow:
    """A continuous interval during which a planet is combust (Astangata)."""

    body: str
    start_jd_tt: float
    end_jd_tt: float
    min_separation_jd_tt: float
    min_separation_deg: float
    cazimi_occurred: bool
    is_retrograde_at_conjunction: bool
    orb_entry_deg: float
    orb_exit_deg: float
    duration_days: float
    receipt: Mapping[str, Any]
    receipt_sha256: str

    @property
    def entry_jd_tt(self) -> float:
        return self.start_jd_tt

    @property
    def exit_jd_tt(self) -> float:
        return self.end_jd_tt

    @property
    def conjunction_jd_tt(self) -> float:
        return self.min_separation_jd_tt

    def __getitem__(self, key: str) -> Any:
        return getattr(self, key)


def combustion_orb_degrees(body: str, is_retrograde: bool = False) -> float:
    """Return the classical Surya Siddhanta combustion orb threshold (degrees) for ``body``."""
    key = body.strip().lower()
    if key not in SURYA_SIDDHANTA_COMBUSTION_ORBS_DEG:
        raise ValueError(
            f"combustion orb is defined for {tuple(SURYA_SIDDHANTA_COMBUSTION_ORBS_DEG)}, got {body!r}"
        )
    entry = SURYA_SIDDHANTA_COMBUSTION_ORBS_DEG[key]
    return entry["retrograde"] if is_retrograde else entry["direct"]


def check_combustion(
    sun_lon_deg: float,
    body: str,
    body_lon_deg: float,
    is_retrograde: bool = False,
) -> CombustionStatus:
    """Evaluate Surya Siddhanta combustion (Moudhya / Astangata) and Cazimi at an instant."""
    if not (math.isfinite(sun_lon_deg) and math.isfinite(body_lon_deg)):
        raise ValueError("sun_lon_deg and body_lon_deg must be finite")
    key = body.strip().lower()
    orb_deg = combustion_orb_degrees(key, is_retrograde=bool(is_retrograde))

    sun_norm = sun_lon_deg % 360.0
    body_norm = body_lon_deg % 360.0
    signed_elong = _signed_angle_diff_deg(body_norm, sun_norm)
    sep_deg = abs(signed_elong)

    is_combust = sep_deg <= orb_deg
    is_cazimi = sep_deg < CAZIMI_ORB_DEG
    state: Literal["cazimi", "combust", "visible"] = (
        "cazimi" if is_cazimi else ("combust" if is_combust else "visible")
    )

    receipt_payload = {
        "component": "ephemeris_oss.engine.phenomena.check_combustion",
        "package_version": __version__,
        "authority": "Surya Siddhanta Ch. 9 (Udayastadhikara)",
        "body": key,
        "sun_longitude_deg": sun_norm,
        "body_longitude_deg": body_norm,
        "is_retrograde": bool(is_retrograde),
        "angular_separation_deg": sep_deg,
        "orb_threshold_deg": orb_deg,
        "is_combust": is_combust,
        "is_cazimi": is_cazimi,
        "state": state,
    }
    digest = canonical_hash(receipt_payload)

    return CombustionStatus(
        body=key,
        sun_longitude_deg=sun_norm,
        body_longitude_deg=body_norm,
        is_retrograde=bool(is_retrograde),
        angular_separation_deg=sep_deg,
        signed_elongation_deg=signed_elong,
        orb_threshold_deg=orb_deg,
        is_combust=is_combust,
        is_cazimi=is_cazimi,
        state=state,
        receipt=receipt_payload,
        receipt_sha256=digest,
    )


def find_combustion_windows(
    body: str,
    start_jd_tt: float,
    end_jd_tt: float,
    engine: Any = None,
    *,
    position_provider: Any = None,
) -> tuple[CombustionWindow, ...]:
    """Find all combustion (Astangata/Moudhya) intervals for ``body`` in ``[start_jd_tt, end_jd_tt]``."""
    if end_jd_tt <= start_jd_tt:
        raise ValueError("end_jd_tt must be greater than start_jd_tt")
    key = body.strip().lower()
    if key not in SURYA_SIDDHANTA_COMBUSTION_ORBS_DEG:
        raise ValueError(f"unsupported body for combustion search: {body!r}")

    _, provider_label = _evaluate_body_position(key, start_jd_tt, engine, position_provider)

    def _state_at(jd: float) -> tuple[float, float, bool]:
        sun_pos, _ = _evaluate_body_position("sun", jd, engine, position_provider)
        body_pos, _ = _evaluate_body_position(key, jd, engine, position_provider)
        sep = abs(_signed_angle_diff_deg(body_pos["longitude_deg"], sun_pos["longitude_deg"]))
        if key in ("mercury", "venus"):
            speed = _longitude_speed_deg_per_day(key, jd, engine, position_provider, step_days=5.0e-3)
            retro = speed < 0.0
        else:
            retro = False
        orb = combustion_orb_degrees(key, is_retrograde=retro)
        return sep, orb, retro

    def margin_fn(jd: float) -> float:
        sep, orb, _ = _state_at(jd)
        return orb - sep

    step = 1.0 if key == "moon" else (3.0 if key in ("mercury", "venus") else 6.0)
    step = min(step, max(0.25, (end_jd_tt - start_jd_tt) / 12.0))

    times: list[float] = []
    t_cur = start_jd_tt
    while t_cur < end_jd_tt:
        times.append(t_cur)
        t_cur = min(end_jd_tt, t_cur + step)
    if not times or times[-1] < end_jd_tt:
        times.append(end_jd_tt)

    margins = [margin_fn(t) for t in times]

    windows: list[CombustionWindow] = []
    in_window = margins[0] >= 0.0
    entry_jd = start_jd_tt if in_window else None

    for i in range(len(times) - 1):
        t1, t2 = times[i], times[i + 1]
        m1, m2 = margins[i], margins[i + 1]
        if not in_window and m2 >= 0.0:
            root = _bisect_root(margin_fn, t1, t2, tol_days=1.0e-6)
            entry_jd = root if root is not None else t2
            in_window = True
        elif in_window and m2 < 0.0:
            root = _bisect_root(margin_fn, t1, t2, tol_days=1.0e-6)
            exit_jd = root if root is not None else t1
            assert entry_jd is not None
            windows.append(
                _build_combustion_window(key, entry_jd, exit_jd, provider_label, engine, position_provider)
            )
            in_window = False
            entry_jd = None

    if in_window and entry_jd is not None and entry_jd < end_jd_tt:
        windows.append(
            _build_combustion_window(key, entry_jd, end_jd_tt, provider_label, engine, position_provider)
        )

    return tuple(windows)


def _build_combustion_window(
    body: str,
    entry_jd: float,
    exit_jd: float,
    provider_label: str,
    engine: Any,
    position_provider: Any,
) -> CombustionWindow:
    def sep_fn(t: float) -> float:
        sun_p, _ = _evaluate_body_position("sun", t, engine, position_provider)
        body_p, _ = _evaluate_body_position(body, t, engine, position_provider)
        return abs(_signed_angle_diff_deg(body_p["longitude_deg"], sun_p["longitude_deg"]))

    min_jd, min_sep = _minimize_scalar(sep_fn, entry_jd, exit_jd, tol_days=1.0e-6)
    retro_at_conj = (
        _longitude_speed_deg_per_day(body, min_jd, engine, position_provider, step_days=5.0e-3) < 0.0
        if body in TARAGRAHAS
        else False
    )
    retro_entry = (
        _longitude_speed_deg_per_day(body, entry_jd, engine, position_provider, step_days=5.0e-3) < 0.0
        if body in ("mercury", "venus")
        else False
    )
    retro_exit = (
        _longitude_speed_deg_per_day(body, exit_jd, engine, position_provider, step_days=5.0e-3) < 0.0
        if body in ("mercury", "venus")
        else False
    )
    orb_entry = combustion_orb_degrees(body, retro_entry)
    orb_exit = combustion_orb_degrees(body, retro_exit)
    cazimi = min_sep < CAZIMI_ORB_DEG
    duration = exit_jd - entry_jd

    receipt_payload = {
        "component": "ephemeris_oss.engine.phenomena.combustion_window",
        "package_version": __version__,
        "position_provider": provider_label,
        "body": body,
        "start_jd_tt": entry_jd,
        "end_jd_tt": exit_jd,
        "min_separation_jd_tt": min_jd,
        "min_separation_deg": min_sep,
        "cazimi_occurred": cazimi,
        "is_retrograde_at_conjunction": retro_at_conj,
    }
    return CombustionWindow(
        body=body,
        start_jd_tt=entry_jd,
        end_jd_tt=exit_jd,
        min_separation_jd_tt=min_jd,
        min_separation_deg=min_sep,
        cazimi_occurred=cazimi,
        is_retrograde_at_conjunction=retro_at_conj,
        orb_entry_deg=orb_entry,
        orb_exit_deg=orb_exit,
        duration_days=duration,
        receipt=receipt_payload,
        receipt_sha256=canonical_hash(receipt_payload),
    )


# ---------------------------------------------------------------------------
# 3. Graha Yuddha (Planetary War) Solver
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class GrahaYuddhaEvent:
    """Resolution of a Graha Yuddha (Planetary War) between two Taragrahas within 1 deg longitude."""

    body_a: str
    body_b: str
    longitude_separation_deg: float
    latitude_separation_deg: float
    jayin: str
    parajita: str
    northern_body: str
    brighter_body: str
    victory_criterion: Literal["venus_exemption", "northern_latitude", "apparent_brightness_disc"]
    venus_exemption_applied: bool
    receipt: Mapping[str, Any]
    receipt_sha256: str

    @property
    def victor(self) -> str:
        return self.jayin

    @property
    def winner(self) -> str:
        return self.jayin

    @property
    def vanquished(self) -> str:
        return self.parajita

    @property
    def loser(self) -> str:
        return self.parajita

    @property
    def separation_deg(self) -> float:
        return self.longitude_separation_deg

    def __getitem__(self, key: str) -> Any:
        return getattr(self, key)


def _apparent_disc_score(body: str, entry: Mapping[str, Any]) -> float:
    """Return apparent disc diameter (arcsec) or intrinsic brightness score for tie-breaking."""
    if "apparent_disc_arcsec" in entry:
        return float(entry["apparent_disc_arcsec"])
    if "brightness" in entry:
        return float(entry["brightness"])
    # Intrinsic Vedic brilliance hierarchy (Venus > Jupiter > Mars > Mercury > Saturn)
    return float(TARAGRAHA_BRIGHTNESS_RANK[body]) * 100.0


def evaluate_graha_yuddha(
    positions: Any,
    *,
    max_longitude_separation_deg: float = 1.0,
    apply_venus_exemption: bool = True,
) -> tuple[GrahaYuddhaEvent, ...]:
    """Evaluate Planetary War (Graha Yuddha) among the five Taragrahas (Mars, Mercury, Jupiter, Venus, Saturn).

    Rules (Surya Siddhanta Ch. 7 & Brihat Samhita Ch. 17):
    1. Only the five Taragrahas participate (Sun, Moon, Rahu, Ketu are excluded).
    2. A war occurs when two Taragrahas are within ``max_longitude_separation_deg`` (default 1.0 deg).
    3. If ``apply_venus_exemption`` is True and Venus is one of the combatants, Venus is the
       victor (``jayin``) whether North or South.
    4. Otherwise, the planet with the more northern ecliptic latitude (``latitude_deg``) is
       the victor (``jayin``) and the southern planet is vanquished (``parajita``).
    5. If ecliptic latitudes are equal, the planet with larger apparent disc / brightness wins.
    """
    raw_map: Mapping[str, Any] = positions.value if hasattr(positions, "value") else positions
    if not isinstance(raw_map, Mapping):
        raise ValueError("positions must be a mapping of body names to coordinate dicts (or an Engine Result)")

    taragraha_states: dict[str, Mapping[str, Any]] = {}
    for k, v in raw_map.items():
        norm_key = str(k).strip().lower()
        if norm_key in TARAGRAHAS and isinstance(v, Mapping) and "longitude_deg" in v:
            taragraha_states[norm_key] = v

    ordered_bodies = [b for b in TARAGRAHAS if b in taragraha_states]
    events: list[GrahaYuddhaEvent] = []

    for idx_a in range(len(ordered_bodies)):
        for idx_b in range(idx_a + 1, len(ordered_bodies)):
            body_a = ordered_bodies[idx_a]
            body_b = ordered_bodies[idx_b]
            state_a = taragraha_states[body_a]
            state_b = taragraha_states[body_b]

            lon_a = float(state_a["longitude_deg"]) % 360.0
            lon_b = float(state_b["longitude_deg"]) % 360.0
            lon_sep = abs(_signed_angle_diff_deg(lon_a, lon_b))
            if lon_sep > max_longitude_separation_deg:
                continue

            lat_a = float(state_a.get("latitude_deg", 0.0))
            lat_b = float(state_b.get("latitude_deg", 0.0))
            lat_sep = abs(lat_a - lat_b)

            score_a = _apparent_disc_score(body_a, state_a)
            score_b = _apparent_disc_score(body_b, state_b)
            brighter = body_a if score_a >= score_b else body_b

            if abs(lat_a - lat_b) > 1.0e-9:
                northern = body_a if lat_a > lat_b else body_b
            else:
                northern = brighter

            venus_involved = "venus" in (body_a, body_b)
            if apply_venus_exemption and venus_involved:
                jayin = "venus"
                parajita = body_b if body_a == "venus" else body_a
                venus_exemption_used = True
                criterion: Literal["venus_exemption", "northern_latitude", "apparent_brightness_disc"] = (
                    "venus_exemption" if northern != "venus" else "northern_latitude"
                )
            elif abs(lat_a - lat_b) > 1.0e-9:
                jayin = northern
                parajita = body_b if northern == body_a else body_a
                venus_exemption_used = False
                criterion = "northern_latitude"
            else:
                jayin = brighter
                parajita = body_b if brighter == body_a else body_a
                venus_exemption_used = False
                criterion = "apparent_brightness_disc"

            receipt_payload = {
                "component": "ephemeris_oss.engine.phenomena.graha_yuddha",
                "package_version": __version__,
                "authority": "Surya Siddhanta Ch. 7 / Brihat Samhita Ch. 17",
                "body_a": body_a,
                "body_b": body_b,
                "longitude_separation_deg": lon_sep,
                "latitude_separation_deg": lat_sep,
                "jayin": jayin,
                "parajita": parajita,
                "northern_body": northern,
                "brighter_body": brighter,
                "victory_criterion": criterion,
                "venus_exemption_applied": venus_exemption_used,
            }
            events.append(
                GrahaYuddhaEvent(
                    body_a=body_a,
                    body_b=body_b,
                    longitude_separation_deg=lon_sep,
                    latitude_separation_deg=lat_sep,
                    jayin=jayin,
                    parajita=parajita,
                    northern_body=northern,
                    brighter_body=brighter,
                    victory_criterion=criterion,
                    venus_exemption_applied=venus_exemption_used,
                    receipt=receipt_payload,
                    receipt_sha256=canonical_hash(receipt_payload),
                )
            )

    return tuple(events)


# ---------------------------------------------------------------------------
# 4. Sign Ingress & Solar Sankranti Solver
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class SignIngressEvent:
    """Exact sub-second Rasi / Zodiac sign boundary crossing (Sankranti for the Sun)."""

    body: str
    jd_tt: float
    boundary_longitude_deg: float
    direction: Literal["direct", "retrograde"]
    from_rasi_index: int
    to_rasi_index: int
    from_rasi: str
    to_rasi: str
    from_sign: str
    to_sign: str
    sankranti_name: str | None
    ayanamsa: str | None
    ayanamsa_deg: float
    residual_arcsec: float
    receipt: Mapping[str, Any]
    receipt_sha256: str

    @property
    def from_sign_index(self) -> int:
        return self.from_rasi_index

    @property
    def to_sign_index(self) -> int:
        return self.to_rasi_index

    @property
    def rasi(self) -> str:
        return self.to_rasi

    @property
    def sign(self) -> str:
        return self.to_sign

    def __getitem__(self, key: str) -> Any:
        return getattr(self, key)


def find_sign_ingresses(
    body: str,
    start_jd_tt: float,
    end_jd_tt: float,
    ayanamsa: str | None = "lahiri",
    engine: Any = None,
    *,
    position_provider: Any = None,
) -> tuple[SignIngressEvent, ...]:
    """Find all 30-degree Rasi / sign ingresses (and Solar Sankrantis) in ``[start_jd_tt, end_jd_tt]``."""
    if end_jd_tt <= start_jd_tt:
        raise ValueError("end_jd_tt must be greater than start_jd_tt")
    key = body.strip().lower()
    use_tropical = ayanamsa is None or str(ayanamsa).strip().lower() in ("", "none", "tropical")
    ayanamsa_name = None if use_tropical else str(ayanamsa).strip().lower()

    _, provider_label = _evaluate_body_position(key, start_jd_tt, engine, position_provider)

    def zodiac_lon(jd: float) -> float:
        pos, _ = _evaluate_body_position(key, jd, engine, position_provider)
        trop = pos["longitude_deg"]
        if use_tropical:
            return trop % 360.0
        assert ayanamsa_name is not None
        ay = ayanamsa_degrees(jd, ayanamsa_name)
        return normalize_degrees(trop - ay)

    # Choose step size based on body's maximum daily motion so 30-deg sectors are never skipped
    base_step = 0.5 if key == "moon" else (3.0 if key in ("sun", "mercury", "venus", "mars") else 8.0)
    step = min(base_step, max(0.1, (end_jd_tt - start_jd_tt) / 16.0))

    times: list[float] = []
    t_cur = start_jd_tt
    while t_cur < end_jd_tt:
        times.append(t_cur)
        t_cur = min(end_jd_tt, t_cur + step)
    if not times or times[-1] < end_jd_tt:
        times.append(end_jd_tt)

    raw_lons = [zodiac_lon(t) for t in times]
    unwrapped = [raw_lons[0]]
    for prev_l, cur_l in zip(raw_lons, raw_lons[1:]):
        unwrapped.append(unwrapped[-1] + _signed_angle_diff_deg(cur_l, prev_l))

    events: list[SignIngressEvent] = []
    seen_roots: list[tuple[float, int]] = []

    for i in range(len(times) - 1):
        t1, t2 = times[i], times[i + 1]
        u1, u2 = unwrapped[i], unwrapped[i + 1]
        if abs(u2 - u1) <= 1.0e-12:
            continue
        low, high = (u1, u2) if u1 <= u2 else (u2, u1)
        k_min = math.ceil(low / 30.0 - 1.0e-12)
        k_max = math.floor(high / 30.0 + 1.0e-12)
        direction: Literal["direct", "retrograde"] = "direct" if u2 > u1 else "retrograde"

        for k_idx in range(k_min, k_max + 1):
            level = k_idx * 30.0
            if level < low - 1.0e-9 or level > high + 1.0e-9:
                continue
            target_deg = level % 360.0
            boundary_sector = int(round(target_deg / 30.0)) % 12

            def crossing_residual(t: float, target: float = target_deg) -> float:
                return _signed_angle_diff_deg(zodiac_lon(t), target)

            root_jd = _bisect_root(crossing_residual, t1, t2, tol_days=1.0e-8)
            if root_jd is None or not (start_jd_tt <= root_jd <= end_jd_tt):
                continue
            if any(abs(root_jd - prev_jd) <= 1.0e-4 and prev_sec == boundary_sector for prev_jd, prev_sec in seen_roots):
                continue
            seen_roots.append((root_jd, boundary_sector))

            res_arcsec = abs(crossing_residual(root_jd)) * 3600.0
            if direction == "direct":
                from_idx = (boundary_sector - 1) % 12
                to_idx = boundary_sector
            else:
                from_idx = boundary_sector
                to_idx = (boundary_sector - 1) % 12

            ay_val = 0.0 if use_tropical else ayanamsa_degrees(root_jd, ayanamsa_name or "lahiri")
            sankranti = SANKRANTI_NAMES[to_idx] if key == "sun" else None

            receipt_payload = {
                "component": "ephemeris_oss.engine.phenomena.sign_ingress",
                "package_version": __version__,
                "position_provider": provider_label,
                "body": key,
                "jd_tt": root_jd,
                "boundary_longitude_deg": target_deg,
                "direction": direction,
                "from_rasi_index": from_idx,
                "to_rasi_index": to_idx,
                "from_rasi": RASI_NAMES[from_idx],
                "to_rasi": RASI_NAMES[to_idx],
                "sankranti_name": sankranti,
                "ayanamsa": ayanamsa_name,
                "ayanamsa_deg": ay_val,
                "residual_arcsec": res_arcsec,
            }
            events.append(
                SignIngressEvent(
                    body=key,
                    jd_tt=root_jd,
                    boundary_longitude_deg=target_deg,
                    direction=direction,
                    from_rasi_index=from_idx,
                    to_rasi_index=to_idx,
                    from_rasi=RASI_NAMES[from_idx],
                    to_rasi=RASI_NAMES[to_idx],
                    from_sign=WESTERN_SIGN_NAMES[from_idx],
                    to_sign=WESTERN_SIGN_NAMES[to_idx],
                    sankranti_name=sankranti,
                    ayanamsa=ayanamsa_name,
                    ayanamsa_deg=ay_val,
                    residual_arcsec=res_arcsec,
                    receipt=receipt_payload,
                    receipt_sha256=canonical_hash(receipt_payload),
                )
            )

    events.sort(key=lambda ev: ev.jd_tt)
    return tuple(events)


__all__ = [
    "CAZIMI_ORB_DEG",
    "CombustionStatus",
    "CombustionWindow",
    "GrahaYuddhaEvent",
    "RASI_NAMES",
    "RetrogradeStationEvent",
    "SANKRANTI_NAMES",
    "SURYA_SIDDHANTA_COMBUSTION_ORBS_DEG",
    "SignIngressEvent",
    "TARAGRAHAS",
    "WESTERN_SIGN_NAMES",
    "check_combustion",
    "combustion_orb_degrees",
    "evaluate_graha_yuddha",
    "find_combustion_windows",
    "find_retrograde_stations",
    "find_sign_ingresses",
]
