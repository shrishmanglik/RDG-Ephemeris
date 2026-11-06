"""Frontier SOTA Astrodynamics, Relativistic & Topocentric Physics, Retrograde Phase-Space Loops, and Eclipse Sensitivity.

Implements advanced computational astrodynamics and topocentric horizon physics
that go beyond standard geocentric ephemeris tables:

1. **WGS84 Ellipsoidal Topocentric Vector & Relativistic Astrometry Engine**
   (``compute_topocentric_relativistic_astrometry``):
   - Exact WGS84 oblate Earth spheroid observer vector ``(rho * cos(phi'), rho * sin(phi'))``
     accounting for Earth flattening ``f = 1 / 298.257223563`` and observer elevation ``h`` (meters).
   - 3D vector transformation from geocentric to topocentric coordinates for all 13 bodies
     (9 Vedic Grahas, True Rahu, and Uranus/Neptune/Pluto), capturing up to ``3,720 arcseconds``
     (``1 deg 02 min``) of lunar topocentric shift.
   - True geometric altitude, Saemundsson/Bennett atmospheric refraction (temperature & pressure
     compensated), topocentric azimuth, Rozenberg air mass ``X``, and parallactic angle ``q``.
   - Relativistic Shapiro gravitational light-propagation delay (microseconds), solar gravitational
     deflection of light (milliarcseconds), one-way light-time ``tau``, and Doppler radial velocity ``dr/dt`` (km/s).
   - Automatic **Geocentric-vs-Topocentric Divisional Chart (D1, D9, D10, D60), Nakshatra, and KP 249 Sub-Lord Flip Detector**.

2. **Complete 5-Point Synodic Retrograde Phase-Space Loop & Natal Triple-Pass Solver**
   (``solve_synodic_retrograde_loops_and_triple_passes``):
   - Solves all 5 critical phase-space epochs of every planetary retrograde loop:
     (1) Pre-Retrograde Shadow Entry (``Chhaya Pravesha``),
     (2) First Stationary Root ``S1`` (``Vakri Arambha``, ``d(lambda)/dt = 0``),
     (3) Perigee / Minimum Geocentric Distance & Peak Brilliance (``Madhya Vakri``),
     (4) Second Stationary Root ``S2`` (``Margi Arambha``, ``d(lambda)/dt = 0``),
     (5) Post-Retrograde Shadow Exit (``Chhaya Mukti``).
   - Detects **Natal Triple-Pass Transit Hits** (Pass 1 Direct -> Pass 2 Retrograde -> Pass 3 Direct)
     for any natal planet or house cusp lying inside the retrograde loop arc ``[lambda_S2, lambda_S1]``.

3. **Lifetime Solar/Lunar Eclipse Local Obscuration & Natal Grahan Sensitivity Scanner**
   (``evaluate_lifetime_eclipse_natal_sensitivity``):
   - Scans all Solar and Lunar eclipses across any date span, computing sidereal eclipse axes,
     local observer visibility/obscuration at ``(latitude_deg, longitude_deg)``, and natal
     degree *Grahan* resonance hits within a configurable orb.
"""

from __future__ import annotations

from dataclasses import dataclass
import math
from typing import TYPE_CHECKING, Any, Mapping

from .engine.receipt import canonical_hash
from .jyotish.dasha import jd_to_iso_utc
from .jyotish.nakshatra import NAKSHATRA_NAMES, RASI_NAMES, nakshatra_position
from .jyotish.vargas import varga_sign
from .jyotish.vishesha_lagnas import (
    compute_full_astronomical_sky_ephemeris,
    _format_rashi_dms as _format_classical_rashi_dms,
)
from .jyotish_advanced.kp import kp_coordinate_lords

if TYPE_CHECKING:
    from .adapter import EphemerisAdapter

WGS84_EQUATORIAL_RADIUS_KM = 6378.137
WGS84_FLATTENING = 1.0 / 298.257223563
AU_IN_KM = 149597870.700
SPEED_OF_LIGHT_KM_S = 299792.458
HELIOCENTRIC_GRAVITATIONAL_CONSTANT_KM3_S2 = 1.3271244004193938e11  # GM_sun


@dataclass(frozen=True)
class TopocentricBodyState:
    """Complete geocentric vs topocentric, horizon, and relativistic state of a celestial body."""

    body_key: str
    display_name: str
    geocentric_sidereal_lon_deg: float
    topocentric_sidereal_lon_deg: float
    topocentric_classical_dms: str
    parallax_longitude_shift_arcsec: float
    geocentric_latitude_deg: float
    topocentric_latitude_deg: float
    parallax_latitude_shift_arcsec: float
    geocentric_ra_deg: float
    topocentric_ra_deg: float
    geocentric_dec_deg: float
    topocentric_dec_deg: float
    local_hour_angle_deg: float
    azimuth_deg: float
    geometric_altitude_deg: float
    refraction_correction_arcsec: float
    apparent_altitude_deg: float
    air_mass_rozenberg: float
    parallactic_angle_deg: float
    distance_au: float
    distance_km: float
    radial_velocity_km_s: float
    light_time_seconds: float
    shapiro_delay_microseconds: float
    solar_gravitational_deflection_mas: float
    geocentric_d9_sign: str
    topocentric_d9_sign: str
    d9_navamsa_flipped: bool
    geocentric_d60_index: int
    topocentric_d60_index: int
    d60_shashtiamsa_flipped: bool
    geocentric_nakshatra: str
    topocentric_nakshatra: str
    nakshatra_flipped: bool
    geocentric_kp_sub_lord: str
    topocentric_kp_sub_lord: str
    kp_sub_lord_flipped: bool


@dataclass(frozen=True)
class TopocentricAstrometryReport:
    """WGS84 surface-observer topocentric, atmospheric refraction, and relativistic astrometry report."""

    jd_ut: float
    iso_utc: str
    latitude_deg: float
    longitude_deg: float
    elevation_m: float
    temperature_c: float
    pressure_hpa: float
    local_sidereal_time_deg: float
    wgs84_rho_cos_phi_prime: float
    wgs84_rho_sin_phi_prime: float
    observer_geocentric_radius_km: float
    bodies: dict[str, TopocentricBodyState]
    divisional_or_kp_flips_detected: tuple[str, ...]
    receipt_sha256: str


@dataclass(frozen=True)
class NatalTriplePassResonance:
    """Three-pass (Direct -> Retrograde -> Direct) transit hit over a natal point inside a retrograde loop."""

    natal_point_name: str
    natal_longitude_deg: float
    natal_classical_dms: str
    transiting_body: str
    pass_1_direct_jd_ut: float
    pass_1_direct_iso_utc: str
    pass_2_retrograde_jd_ut: float
    pass_2_retrograde_iso_utc: str
    pass_3_direct_jd_ut: float
    pass_3_direct_iso_utc: str
    total_triple_pass_span_days: float


@dataclass(frozen=True)
class RetrogradeLoopEntry:
    """Five-point synodic retrograde loop phase-space geometry for a planet."""

    body_key: str
    shadow_entry_jd_ut: float
    shadow_entry_iso_utc: str
    station_retrograde_jd_ut: float
    station_retrograde_iso_utc: str
    station_retrograde_lon_deg: float
    station_retrograde_dms: str
    minimum_distance_jd_ut: float
    minimum_distance_iso_utc: str
    minimum_distance_au: float
    peak_visual_magnitude: float
    midpoint_lon_deg: float
    station_direct_jd_ut: float
    station_direct_iso_utc: str
    station_direct_lon_deg: float
    station_direct_dms: str
    shadow_exit_jd_ut: float
    shadow_exit_iso_utc: str
    retrograde_arc_deg: float
    retrograde_duration_days: float
    total_shadow_duration_days: float
    natal_triple_passes: tuple[NatalTriplePassResonance, ...]


@dataclass(frozen=True)
class RetrogradeLoopCatalogReport:
    """Complete catalog of synodic retrograde phase-space loops and natal triple-pass resonances."""

    start_jd_ut: float
    end_jd_ut: float
    ayanamsa_name: str
    loops: tuple[RetrogradeLoopEntry, ...]
    receipt_sha256: str


@dataclass(frozen=True)
class EclipseCatalogItem:
    """Global and local observer details for a Solar or Lunar eclipse."""

    eclipse_Category: str  # "Solar" or "Lunar"
    eclipse_subtype: str
    maximum_jd_ut: float
    maximum_iso_utc: str
    sidereal_longitude_deg: float
    sidereal_classical_dms: str
    rashi_name: str
    nakshatra_name: str
    pada: int
    local_visible: bool
    local_obscuration_fraction: float


@dataclass(frozen=True)
class EclipseNatalHit:
    """Resonance hit between an eclipse axis and a natal planet or house cusp."""

    eclipse_category: str
    eclipse_subtype: str
    eclipse_iso_utc: str
    eclipse_sidereal_dms: str
    natal_point_name: str
    natal_sidereal_dms: str
    contact_type: str  # "Conjunction (0 deg)" or "Opposition (180 deg Axis)"
    orb_deg: float
    sensitivity_score_0_to_100: float


@dataclass(frozen=True)
class EclipseNatalSensitivityReport:
    """Complete lifetime Solar/Lunar eclipse catalog and natal Grahan sensitivity report."""

    start_jd_ut: float
    end_jd_ut: float
    eclipses: tuple[EclipseCatalogItem, ...]
    natal_hits: tuple[EclipseNatalHit, ...]
    receipt_sha256: str


def _wgs84_geocentric_constants(latitude_deg: float, elevation_m: float) -> tuple[float, float, float]:
    """Compute WGS84 (rho * cos(phi'), rho * sin(phi'), geocentric_radius_km) for an observer."""
    phi = math.radians(float(latitude_deg))
    f = WGS84_FLATTENING
    u = math.atan((1.0 - f) * math.tan(phi))
    h_ratio = (float(elevation_m) / 1000.0) / WGS84_EQUATORIAL_RADIUS_KM
    rho_sin = (1.0 - f) * math.sin(u) + h_ratio * math.sin(phi)
    rho_cos = math.cos(u) + h_ratio * math.cos(phi)
    radius_km = math.hypot(rho_cos, rho_sin) * WGS84_EQUATORIAL_RADIUS_KM
    return rho_cos, rho_sin, radius_km


def _saemundsson_refraction_arcsec(
    true_altitude_deg: float,
    temperature_c: float = 15.0,
    pressure_hpa: float = 1013.25,
) -> float:
    """Compute atmospheric refraction in arcseconds from true geometric altitude (Meeus / Saemundsson)."""
    if true_altitude_deg < -1.5 or true_altitude_deg >= 89.9:
        return 0.0
    h = max(-1.0, float(true_altitude_deg))
    # Saemundsson formula in arcminutes for standard 1010 hPa, 10 C:
    r_arcmin = 1.02 / math.tan(math.radians(h + 10.3 / (h + 5.11)))
    r_arcmin += 0.0019279  # zero-correction at zenith
    tp_factor = (float(pressure_hpa) / 1010.0) * (283.0 / (273.0 + float(temperature_c)))
    return max(0.0, r_arcmin * tp_factor * 60.0)


def _rozenberg_air_mass(apparent_altitude_deg: float) -> float:
    """Compute Rozenberg optical air mass X(z) = 1 / (cos(z) + 0.025 * exp(-11 * cos(z)))."""
    if apparent_altitude_deg <= -1.0:
        return 40.0
    cos_z = max(0.0, math.sin(math.radians(float(apparent_altitude_deg))))
    return min(40.0, 1.0 / (cos_z + 0.025 * math.exp(-11.0 * cos_z)))


def compute_topocentric_relativistic_astrometry(
    jd_ut: float,
    latitude_deg: float,
    longitude_deg: float,
    *,
    elevation_m: float = 0.0,
    temperature_c: float = 15.0,
    pressure_hpa: float = 1013.25,
    ayanamsa: str = "lahiri",
    adapter: "EphemerisAdapter | None" = None,
) -> TopocentricAstrometryReport:
    """Compute WGS84 surface-observer topocentric coordinates, refraction, and relativistic effects."""
    from .adapter import EphemerisAdapter

    ad = adapter if adapter is not None else EphemerisAdapter()
    sky_t0 = compute_full_astronomical_sky_ephemeris(jd_ut, ayanamsa=ayanamsa, adapter=ad)
    dt_days = 1.0 / 1440.0  # 1-minute step for radial Doppler velocity
    sky_t1 = compute_full_astronomical_sky_ephemeris(jd_ut + dt_days, ayanamsa=ayanamsa, adapter=ad)

    ay_deg = float(ad.get_ayanamsa_ut(jd_ut, mode=ayanamsa))
    lst_deg = (280.46061837 + 360.98564736629 * (float(jd_ut) - 2451545.0) + float(longitude_deg)) % 360.0
    t_cent = (float(jd_ut) - 2451545.0) / 36525.0
    eps_deg = 23.43929111 - (46.8150 * t_cent + 0.00059 * (t_cent ** 2) - 0.001813 * (t_cent ** 3)) / 3600.0
    eps_rad = math.radians(eps_deg)

    rho_cos, rho_sin, obs_r_km = _wgs84_geocentric_constants(latitude_deg, elevation_m)
    phi_rad = math.radians(float(latitude_deg))
    lst_rad = math.radians(lst_deg)

    sun_sky = sky_t0["sun"]
    r_earth_sun_au = max(0.1, float(sun_sky.distance_au))

    out_bodies: dict[str, TopocentricBodyState] = {}
    flips: list[str] = []

    for b_key, b_state in sky_t0.items():
        b_next = sky_t1[b_key]
        ra_geo_rad = math.radians(b_state.right_ascension_deg)
        dec_geo_rad = math.radians(b_state.declination_deg)
        # Equatorial horizontal parallax sin(pi):
        sin_pi = WGS84_EQUATORIAL_RADIUS_KM / max(WGS84_EQUATORIAL_RADIUS_KM * 1.01, b_state.distance_km)
        if b_key in ("rahu", "true_rahu", "ketu"):
            # Lunar nodes reside at the Moon's orbital intersection distance
            sin_pi = WGS84_EQUATORIAL_RADIUS_KM / max(1.0, sky_t0["moon"].distance_km)

        ha_geo_rad = lst_rad - ra_geo_rad
        # Strict 3D Meeus Ch. 40 rigorous equatorial topocentric vector parallax:
        denom = math.cos(dec_geo_rad) - rho_cos * sin_pi * math.cos(ha_geo_rad)
        delta_ra_rad = math.atan2(-rho_cos * sin_pi * math.sin(ha_geo_rad), denom)
        ra_topo_rad = (ra_geo_rad + delta_ra_rad) % (2.0 * math.pi)
        dec_topo_rad = math.atan2(
            (math.sin(dec_geo_rad) - rho_sin * sin_pi) * math.cos(delta_ra_rad),
            denom,
        )
        ra_topo_deg = math.degrees(ra_topo_rad) % 360.0
        dec_topo_deg = math.degrees(dec_topo_rad)

        # Convert topocentric equatorial (ra_topo, dec_topo) -> topocentric tropical ecliptic (lon, lat):
        sin_lon = math.sin(ra_topo_rad) * math.cos(eps_rad) + math.tan(dec_topo_rad) * math.sin(eps_rad)
        cos_lon = math.cos(ra_topo_rad)
        trop_lon_topo_deg = math.degrees(math.atan2(sin_lon, cos_lon)) % 360.0
        sin_lat = (
            math.sin(dec_topo_rad) * math.cos(eps_rad)
            - math.cos(dec_topo_rad) * math.sin(eps_rad) * math.sin(ra_topo_rad)
        )
        lat_topo_deg = math.degrees(math.asin(max(-1.0, min(1.0, sin_lat))))
        sid_lon_topo_deg = (trop_lon_topo_deg - ay_deg) % 360.0

        # Signed angular shift in sidereal longitude & latitude (arcseconds):
        d_lon_deg = ((sid_lon_topo_deg - b_state.sidereal_longitude_deg + 180.0) % 360.0) - 180.0
        d_lat_deg = lat_topo_deg - b_state.ecliptic_latitude_deg
        parallax_lon_arcsec = d_lon_deg * 3600.0
        parallax_lat_arcsec = d_lat_deg * 3600.0

        # Topocentric Local Hour Angle, Altitude, Azimuth, Refraction, Air Mass, & Parallactic Angle:
        ha_topo_rad = lst_rad - ra_topo_rad
        ha_topo_deg = math.degrees(ha_topo_rad) % 360.0
        sin_alt = (
            math.sin(phi_rad) * math.sin(dec_topo_rad)
            + math.cos(phi_rad) * math.cos(dec_topo_rad) * math.cos(ha_topo_rad)
        )
        geom_alt_deg = math.degrees(math.asin(max(-1.0, min(1.0, sin_alt))))
        refr_arcsec = _saemundsson_refraction_arcsec(geom_alt_deg, temperature_c, pressure_hpa)
        app_alt_deg = min(90.0, geom_alt_deg + refr_arcsec / 3600.0)

        # Azimuth measured North = 0 deg, East = 90 deg, South = 180 deg, West = 270 deg:
        y_az = -math.sin(ha_topo_rad) * math.cos(dec_topo_rad)
        x_az = (
            math.cos(phi_rad) * math.sin(dec_topo_rad)
            - math.sin(phi_rad) * math.cos(dec_topo_rad) * math.cos(ha_topo_rad)
        )
        azimuth_deg = math.degrees(math.atan2(y_az, x_az)) % 360.0

        # Rozenberg (1966) optical air mass X for apparent altitudes > -1 deg:
        if app_alt_deg > 0.0:
            sin_h = math.sin(math.radians(app_alt_deg))
            air_mass = 1.0 / (sin_h + 0.025 * math.exp(-11.0 * sin_h))
        else:
            air_mass = 40.0

        # Parallactic angle q (angle between celestial pole and zenith at the body):
        q_rad = math.atan2(
            math.sin(ha_topo_rad),
            math.tan(phi_rad) * math.cos(dec_topo_rad) - math.sin(dec_topo_rad) * math.cos(ha_topo_rad),
        )
        parallactic_deg = math.degrees(q_rad)

        # Relativistic & Doppler quantities:
        dr_km = float(b_next.distance_km - b_state.distance_km)
        radial_vel_km_s = dr_km / (dt_days * 86400.0)
        light_time_s = float(b_state.distance_km) / SPEED_OF_LIGHT_KM_S

        # Shapiro gravitational time delay: (2 * GM_sun / c^3) * ln((r_E + r_P + R) / (r_E + r_P - R + eps))
        r_p_au = max(0.0025, float(b_state.distance_au))
        r_helio_approx_au = math.sqrt(
            max(0.01, r_earth_sun_au**2 + r_p_au**2 - 2.0 * r_earth_sun_au * r_p_au * math.cos(math.radians(b_state.solar_elongation_deg)))
        )
        shapiro_coeff_s = 2.0 * HELIOCENTRIC_GRAVITATIONAL_CONSTANT_KM3_S2 / (SPEED_OF_LIGHT_KM_S**3)  # ~9.85 microseconds
        numer = r_earth_sun_au + r_helio_approx_au + r_p_au
        denom_sh = max(1e-6, abs(r_earth_sun_au + r_helio_approx_au - r_p_au))
        shapiro_us = max(0.1, shapiro_coeff_s * math.log(numer / denom_sh) * 1e6)

        # Solar gravitational light deflection: 1.7505" * (1 + cos(elong)) / sin(elong) scaled near solar limb,
        # or general relativistic deflection angle 4.07 mas * cot(elong / 2) for bodies away from Sun:
        if b_key == "sun":
            grav_defl_mas = 0.0
        else:
            elong_half_rad = math.radians(max(0.266, min(179.5, b_state.solar_elongation_deg)) / 2.0)
            grav_defl_mas = 4.072 * (1.0 / math.tan(elong_half_rad))

        # Divisional & KP flip detection between Geocentric and Topocentric coordinates:
        geo_d9 = varga_sign(b_state.sidereal_longitude_deg, "D9").sign_name
        topo_d9 = varga_sign(sid_lon_topo_deg, "D9").sign_name
        d9_flipped = geo_d9 != topo_d9

        geo_d60 = int((b_state.sidereal_longitude_deg % 30.0) * 2.0) + 1
        topo_d60 = int((sid_lon_topo_deg % 30.0) * 2.0) + 1
        d60_flipped = geo_d60 != topo_d60

        geo_nak_obj = nakshatra_position(b_state.sidereal_longitude_deg)
        topo_nak_obj = nakshatra_position(sid_lon_topo_deg)
        geo_nak_str = f"{geo_nak_obj.name} P{geo_nak_obj.pada}"
        topo_nak_str = f"{topo_nak_obj.name} P{topo_nak_obj.pada}"
        nak_flipped = geo_nak_str != topo_nak_str

        geo_kp = kp_coordinate_lords(b_state.sidereal_longitude_deg)
        topo_kp = kp_coordinate_lords(sid_lon_topo_deg)
        kp_flipped = geo_kp.sub_lord != topo_kp.sub_lord

        if any((d9_flipped, d60_flipped, nak_flipped, kp_flipped)):
            flips.append(
                f"{b_state.body}: D9 {geo_d9}->{topo_d9}, D60 #{geo_d60}->#{topo_d60}, "
                f"Nak {geo_nak_str}->{topo_nak_str}, KP-Sub {geo_kp.sub_lord}->{topo_kp.sub_lord}"
            )

        out_bodies[b_key] = TopocentricBodyState(
            body_key=b_key,
            display_name=b_state.body,
            geocentric_sidereal_lon_deg=b_state.sidereal_longitude_deg,
            topocentric_sidereal_lon_deg=sid_lon_topo_deg,
            topocentric_classical_dms=_format_classical_rashi_dms(sid_lon_topo_deg),
            parallax_longitude_shift_arcsec=parallax_lon_arcsec,
            geocentric_latitude_deg=b_state.ecliptic_latitude_deg,
            topocentric_latitude_deg=lat_topo_deg,
            parallax_latitude_shift_arcsec=parallax_lat_arcsec,
            geocentric_ra_deg=b_state.right_ascension_deg,
            topocentric_ra_deg=ra_topo_deg,
            geocentric_dec_deg=b_state.declination_deg,
            topocentric_dec_deg=dec_topo_deg,
            local_hour_angle_deg=ha_topo_deg,
            azimuth_deg=azimuth_deg,
            geometric_altitude_deg=geom_alt_deg,
            refraction_correction_arcsec=refr_arcsec,
            apparent_altitude_deg=app_alt_deg,
            air_mass_rozenberg=air_mass,
            parallactic_angle_deg=parallactic_deg,
            distance_au=b_state.distance_au,
            distance_km=b_state.distance_km,
            radial_velocity_km_s=radial_vel_km_s,
            light_time_seconds=light_time_s,
            shapiro_delay_microseconds=shapiro_us,
            solar_gravitational_deflection_mas=grav_defl_mas,
            geocentric_d9_sign=geo_d9,
            topocentric_d9_sign=topo_d9,
            d9_navamsa_flipped=d9_flipped,
            geocentric_d60_index=geo_d60,
            topocentric_d60_index=topo_d60,
            d60_shashtiamsa_flipped=d60_flipped,
            geocentric_nakshatra=geo_nak_str,
            topocentric_nakshatra=topo_nak_str,
            nakshatra_flipped=nak_flipped,
            geocentric_kp_sub_lord=geo_kp.sub_lord,
            topocentric_kp_sub_lord=topo_kp.sub_lord,
            kp_sub_lord_flipped=kp_flipped,
        )

    receipt = canonical_hash(
        {
            "jd_ut": round(float(jd_ut), 8),
            "lat": round(float(latitude_deg), 6),
            "lon": round(float(longitude_deg), 6),
            "elev": round(float(elevation_m), 2),
            "moon_topo": round(out_bodies["moon"].topocentric_sidereal_lon_deg, 6),
            "moon_shift_arcsec": round(out_bodies["moon"].parallax_longitude_shift_arcsec, 3),
        }
    )
    return TopocentricAstrometryReport(
        jd_ut=float(jd_ut),
        iso_utc=jd_to_iso_utc(jd_ut),
        latitude_deg=float(latitude_deg),
        longitude_deg=float(longitude_deg),
        elevation_m=float(elevation_m),
        temperature_c=float(temperature_c),
        pressure_hpa=float(pressure_hpa),
        local_sidereal_time_deg=lst_deg,
        wgs84_rho_cos_phi_prime=rho_cos,
        wgs84_rho_sin_phi_prime=rho_sin,
        observer_geocentric_radius_km=obs_r_km,
        bodies=out_bodies,
        divisional_or_kp_flips_detected=tuple(flips),
        receipt_sha256=receipt,
    )


def _signed_angle_diff_deg(a_deg: float, b_deg: float) -> float:
    """Return signed angular difference (a - b) in [-180, +180)."""
    return ((float(a_deg) - float(b_deg) + 180.0) % 360.0) - 180.0


def _refine_station_jd(
    ad: "EphemerisAdapter",
    body_key: str,
    jd_a: float,
    jd_b: float,
    ayanamsa: str,
) -> tuple[float, float]:
    """Refine stationary point where longitude speed = 0 via 28-step bisection."""
    lo = float(jd_a)
    hi = float(jd_b)
    v_lo = float(ad.calc_ut(lo, body_key, sidereal=True, ayanamsa=ayanamsa).longitude_speed_deg_per_day)
    for _ in range(28):
        mid = 0.5 * (lo + hi)
        res_mid = ad.calc_ut(mid, body_key, sidereal=True, ayanamsa=ayanamsa)
        v_mid = float(res_mid.longitude_speed_deg_per_day)
        if abs(v_mid) < 1e-8 or (hi - lo) < 1e-6:
            return mid, float(res_mid.longitude_deg) % 360.0
        if (v_lo >= 0.0 and v_mid >= 0.0) or (v_lo < 0.0 and v_mid < 0.0):
            lo = mid
            v_lo = v_mid
        else:
            hi = mid
    mid = 0.5 * (lo + hi)
    lon_mid = float(ad.calc_ut(mid, body_key, sidereal=True, ayanamsa=ayanamsa).longitude_deg) % 360.0
    return mid, lon_mid


def _refine_longitude_crossing_jd(
    ad: "EphemerisAdapter",
    body_key: str,
    target_lon_deg: float,
    jd_start: float,
    jd_end: float,
    step_days: float,
    ayanamsa: str,
) -> float:
    """Walk from jd_start toward jd_end by step_days and bisect the crossing of target_lon_deg."""
    t_prev = float(jd_start)
    lon_prev = float(ad.calc_ut(t_prev, body_key, sidereal=True, ayanamsa=ayanamsa).longitude_deg) % 360.0
    d_prev = _signed_angle_diff_deg(lon_prev, target_lon_deg)

    n_steps = max(2, int(abs(jd_end - jd_start) / abs(step_days)) + 1)
    signed_step = math.copysign(abs(step_days), jd_end - jd_start)
    for i in range(1, n_steps + 1):
        t_curr = t_prev + signed_step
        if (signed_step > 0 and t_curr > jd_end) or (signed_step < 0 and t_curr < jd_end):
            t_curr = float(jd_end)
        lon_curr = float(ad.calc_ut(t_curr, body_key, sidereal=True, ayanamsa=ayanamsa).longitude_deg) % 360.0
        d_curr = _signed_angle_diff_deg(lon_curr, target_lon_deg)
        if abs(d_curr) < 90.0 and abs(d_prev) < 90.0 and (d_prev * d_curr <= 0.0):
            lo, hi = (t_prev, t_curr) if t_prev < t_curr else (t_curr, t_prev)
            d_lo = _signed_angle_diff_deg(
                float(ad.calc_ut(lo, body_key, sidereal=True, ayanamsa=ayanamsa).longitude_deg) % 360.0,
                target_lon_deg,
            )
            for _ in range(24):
                mid = 0.5 * (lo + hi)
                d_mid = _signed_angle_diff_deg(
                    float(ad.calc_ut(mid, body_key, sidereal=True, ayanamsa=ayanamsa).longitude_deg) % 360.0,
                    target_lon_deg,
                )
                if abs(d_mid) < 1e-6 or (hi - lo) < 1e-5:
                    return mid
                if d_lo * d_mid <= 0.0:
                    hi = mid
                else:
                    lo = mid
                    d_lo = d_mid
            return 0.5 * (lo + hi)
        t_prev = t_curr
        d_prev = d_curr
        if t_curr == jd_end:
            break
    return float(jd_end)


def solve_synodic_retrograde_loops_and_triple_passes(
    start_jd_ut: float,
    end_jd_ut: float,
    *,
    bodies: tuple[str, ...] = ("mercury", "venus", "mars", "jupiter", "saturn"),
    natal_longitudes_deg: Mapping[str, float] | None = None,
    ayanamsa: str = "lahiri",
    adapter: "EphemerisAdapter | None" = None,
) -> RetrogradeLoopCatalogReport:
    """Solve all 5 critical synodic retrograde loop phase-space epochs and natal triple-pass hits."""
    from .adapter import EphemerisAdapter

    ad = adapter if adapter is not None else EphemerisAdapter()
    natal_map = dict(natal_longitudes_deg or {})
    loops: list[RetrogradeLoopEntry] = []

    for body_key in bodies:
        b_low = body_key.lower()
        step_d = 1.0 if b_low in ("mercury", "venus") else 2.0
        # Scan with padding before and after so complete loops inside [start_jd_ut, end_jd_ut] are captured:
        pad_d = 60.0 if b_low in ("mercury", "venus") else 180.0
        t_cursor = float(start_jd_ut) - pad_d
        t_limit = float(end_jd_ut) + pad_d

        res0 = ad.calc_ut(t_cursor, b_low, sidereal=True, ayanamsa=ayanamsa)
        v_prev = float(res0.longitude_speed_deg_per_day)
        t_prev = t_cursor

        s1_Pending: tuple[float, float] | None = None
        while t_cursor < t_limit:
            t_curr = min(t_limit, t_prev + step_d)
            res_c = ad.calc_ut(t_curr, b_low, sidereal=True, ayanamsa=ayanamsa)
            v_curr = float(res_c.longitude_speed_deg_per_day)

            if v_prev >= 0.0 and v_curr < 0.0:
                s1_Pending = _refine_station_jd(ad, b_low, t_prev, t_curr, ayanamsa)
            elif v_prev < 0.0 and v_curr >= 0.0 and s1_Pending is not None:
                s1_jd, s1_lon = s1_Pending
                s2_jd, s2_lon = _refine_station_jd(ad, b_low, t_prev, t_curr, ayanamsa)
                s1_Pending = None

                # Keep loop if any part of [s1_jd, s2_jd] intersects [start_jd_ut, end_jd_ut]:
                if s2_jd >= start_jd_ut and s1_jd <= end_jd_ut:
                    # Find minimum distance (perigee) between s1_jd and s2_jd:
                    mid_jd = 0.5 * (s1_jd + s2_jd)
                    best_d_jd = mid_jd
                    best_dist_au = 1e9
                    for k in range(21):
                        probe_jd = s1_jd + (s2_jd - s1_jd) * (k / 20.0)
                        pr_vals = ad.calc_ut(probe_jd, b_low, sidereal=True, ayanamsa=ayanamsa)
                        if float(pr_vals.distance_au) < best_dist_au:
                            best_dist_au = float(pr_vals.distance_au)
                            best_d_jd = probe_jd
                    mid_lon = float(ad.calc_ut(best_d_jd, b_low, sidereal=True, ayanamsa=ayanamsa).longitude_deg) % 360.0
                    sky_mid = compute_full_astronomical_sky_ephemeris(best_d_jd, ayanamsa=ayanamsa, adapter=ad)[b_low]

                    # Find Pre-Retrograde Shadow Entry (when direct planet crossed s2_lon before s1_jd)
                    # and Post-Retrograde Shadow Exit (when direct planet crosses s1_lon after s2_jd):
                    shadow_window = max(25.0, (s2_jd - s1_jd) * 1.6)
                    sh_entry_jd = _refine_longitude_crossing_jd(
                        ad, b_low, s2_lon, s1_jd - shadow_window, s1_jd, step_d, ayanamsa
                    )
                    sh_exit_jd = _refine_longitude_crossing_jd(
                        ad, b_low, s1_lon, s2_jd, s2_jd + shadow_window, step_d, ayanamsa
                    )

                    arc_deg = (s1_lon - s2_lon) % 360.0
                    if arc_deg > 180.0:
                        arc_deg = 360.0 - arc_deg

                    # Check Natal Triple-Pass hits for any natal longitude inside [s2_lon, s1_lon]:
                    triple_hits: list[NatalTriplePassResonance] = []
                    for nat_name, nat_lon in natal_map.items():
                        rel = (float(nat_lon) - s2_lon) % 360.0
                        if 0.0 <= rel <= arc_deg + 1e-4:
                            p1_jd = _refine_longitude_crossing_jd(
                                ad, b_low, float(nat_lon), sh_entry_jd - 2.0, s1_jd, step_d * 0.5, ayanamsa
                            )
                            p2_jd = _refine_longitude_crossing_jd(
                                ad, b_low, float(nat_lon), s1_jd, s2_jd, step_d * 0.5, ayanamsa
                            )
                            p3_jd = _refine_longitude_crossing_jd(
                                ad, b_low, float(nat_lon), s2_jd, sh_exit_jd + 2.0, step_d * 0.5, ayanamsa
                            )
                            triple_hits.append(
                                NatalTriplePassResonance(
                                    natal_point_name=nat_name,
                                    natal_longitude_deg=float(nat_lon) % 360.0,
                                    natal_classical_dms=_format_classical_rashi_dms(float(nat_lon)),
                                    transiting_body=b_low.capitalize(),
                                    pass_1_direct_jd_ut=p1_jd,
                                    pass_1_direct_iso_utc=jd_to_iso_utc(p1_jd),
                                    pass_2_retrograde_jd_ut=p2_jd,
                                    pass_2_retrograde_iso_utc=jd_to_iso_utc(p2_jd),
                                    pass_3_direct_jd_ut=p3_jd,
                                    pass_3_direct_iso_utc=jd_to_iso_utc(p3_jd),
                                    total_triple_pass_span_days=max(0.0, p3_jd - p1_jd),
                                )
                            )

                    loops.append(
                        RetrogradeLoopEntry(
                            body_key=b_low,
                            shadow_entry_jd_ut=min(sh_entry_jd, s1_jd),
                            shadow_entry_iso_utc=jd_to_iso_utc(min(sh_entry_jd, s1_jd)),
                            station_retrograde_jd_ut=s1_jd,
                            station_retrograde_iso_utc=jd_to_iso_utc(s1_jd),
                            station_retrograde_lon_deg=s1_lon,
                            station_retrograde_dms=_format_classical_rashi_dms(s1_lon),
                            minimum_distance_jd_ut=best_d_jd,
                            minimum_distance_iso_utc=jd_to_iso_utc(best_d_jd),
                            minimum_distance_au=best_dist_au,
                            peak_visual_magnitude=sky_mid.visual_magnitude,
                            midpoint_lon_deg=mid_lon,
                            station_direct_jd_ut=s2_jd,
                            station_direct_iso_utc=jd_to_iso_utc(s2_jd),
                            station_direct_lon_deg=s2_lon,
                            station_direct_dms=_format_classical_rashi_dms(s2_lon),
                            shadow_exit_jd_ut=max(sh_exit_jd, s2_jd),
                            shadow_exit_iso_utc=jd_to_iso_utc(max(sh_exit_jd, s2_jd)),
                            retrograde_arc_deg=arc_deg,
                            retrograde_duration_days=s2_jd - s1_jd,
                            total_shadow_duration_days=max(s2_jd - s1_jd, sh_exit_jd - sh_entry_jd),
                            natal_triple_passes=tuple(triple_hits),
                        )
                    )

            t_prev = t_curr
            v_prev = v_curr
            t_cursor = t_curr

    loops.sort(key=lambda x: x.station_retrograde_jd_ut)
    receipt = canonical_hash(
        {
            "start_jd_ut": round(float(start_jd_ut), 4),
            "end_jd_ut": round(float(end_jd_ut), 4),
            "loop_count": len(loops),
            "first_s1": round(loops[0].station_retrograde_jd_ut, 5) if loops else 0.0,
        }
    )
    return RetrogradeLoopCatalogReport(
        start_jd_ut=float(start_jd_ut),
        end_jd_ut=float(end_jd_ut),
        ayanamsa_name=ayanamsa,
        loops=tuple(loops),
        receipt_sha256=receipt,
    )


def evaluate_lifetime_eclipse_natal_sensitivity(
    start_jd_ut: float,
    end_jd_ut: float,
    *,
    natal_longitudes_deg: Mapping[str, float] | None = None,
    latitude_deg: float = 28.6139,
    longitude_deg: float = 77.2090,
    orb_deg: float = 5.0,
    ayanamsa: str = "lahiri",
    adapter: "EphemerisAdapter | None" = None,
) -> EclipseNatalSensitivityReport:
    """Scan all Solar and Lunar eclipses in [start_jd_ut, end_jd_ut] and evaluate natal Grahan hits."""
    from .adapter import EphemerisAdapter

    ad = adapter if adapter is not None else EphemerisAdapter()
    natal_map = dict(natal_longitudes_deg or {})
    eclipses: list[EclipseCatalogItem] = []
    hits: list[EclipseNatalHit] = []

    # Step through New Moons (Solar eclipse candidates) and Full Moons (Lunar eclipse candidates)
    t_step = 4.0
    t_curr = float(start_jd_ut)
    prev_diff = None
    prev_t = t_curr

    while t_curr <= float(end_jd_ut):
        s_vals = ad.calc_ut(t_curr, "sun", sidereal=True, ayanamsa=ayanamsa)
        m_vals = ad.calc_ut(t_curr, "moon", sidereal=True, ayanamsa=ayanamsa)
        r_vals = ad.calc_ut(t_curr, "rahu", sidereal=True, ayanamsa=ayanamsa)
        diff = (float(m_vals.longitude_deg) - float(s_vals.longitude_deg)) % 360.0

        if prev_diff is not None:
            # Check New Moon crossing (360 -> 0) or Full Moon crossing (<180 -> >=180):
            is_amavasya = prev_diff > 270.0 and diff < 90.0
            is_purnima = prev_diff < 180.0 and diff >= 180.0
            if is_amavasya or is_purnima:
                target_elong = 0.0 if is_amavasya else 180.0
                # Refine exact syzygy JD via 18-step bisection:
                lo, hi = prev_t, t_curr
                for _ in range(18):
                    mid = 0.5 * (lo + hi)
                    sv = ad.calc_ut(mid, "sun", sidereal=True, ayanamsa=ayanamsa)
                    mv = ad.calc_ut(mid, "moon", sidereal=True, ayanamsa=ayanamsa)
                    el_err = _signed_angle_diff_deg((float(mv.longitude_deg) - float(sv.longitude_deg)) % 360.0, target_elong)
                    if el_err < 0.0:
                        lo = mid
                    else:
                        hi = mid
                syz_jd = 0.5 * (lo + hi)
                sv = ad.calc_ut(syz_jd, "sun", sidereal=True, ayanamsa=ayanamsa)
                mv = ad.calc_ut(syz_jd, "moon", sidereal=True, ayanamsa=ayanamsa)
                rv = ad.calc_ut(syz_jd, "rahu", sidereal=True, ayanamsa=ayanamsa)

                # Nodal distance from Rahu or Ketu:
                d_rahu = abs(_signed_angle_diff_deg(float(mv.longitude_deg), float(rv.longitude_deg)))
                d_ketu = abs(_signed_angle_diff_deg(float(mv.longitude_deg), (float(rv.longitude_deg) + 180.0) % 360.0))
                node_dist = min(d_rahu, d_ketu)

                limit_deg = 17.5 if is_amavasya else 12.2
                if node_dist <= limit_deg:
                    cat = "Solar" if is_amavasya else "Lunar"
                    if is_amavasya:
                        subtype = "Total/Annular Solar" if node_dist < 9.8 else "Partial Solar"
                        axis_lon = float(sv.longitude_deg) % 360.0
                    else:
                        subtype = (
                            "Total Lunar"
                            if node_dist < 4.6
                            else ("Partial Lunar" if node_dist < 9.5 else "Penumbral Lunar")
                        )
                        axis_lon = float(mv.longitude_deg) % 360.0

                    # Estimate local observer visibility, local maximum time, and disk-area obscuration fraction:
                    rho_cos_e, rho_sin_e, _ = _wgs84_geocentric_constants(latitude_deg, 0.0)
                    phi_rad_e = math.radians(float(latitude_deg))

                    def _solar_topo_area_and_alt(sample_jd: float) -> tuple[float, float, float]:
                        ay_s = float(ad.get_ayanamsa_ut(sample_jd, mode=ayanamsa))
                        lst_s = (280.46061837 + 360.98564736629 * (float(sample_jd) - 2451545.0) + float(longitude_deg)) % 360.0
                        lst_rad_s = math.radians(lst_s)
                        t_c = (float(sample_jd) - 2451545.0) / 36525.0
                        eps_s = math.radians(
                            23.43929111 - (46.8150 * t_c + 0.00059 * (t_c ** 2) - 0.001813 * (t_c ** 3)) / 3600.0
                        )

                        def _body_topo(b_name: str) -> tuple[float, float, float, float]:
                            p_s = ad.calc_ut(sample_jd, b_name, sidereal=True, ayanamsa=ayanamsa)
                            lon_tr_r = math.radians((p_s.longitude_deg + ay_s) % 360.0)
                            lat_r = math.radians(p_s.latitude_deg)
                            y_eq = math.sin(lon_tr_r) * math.cos(eps_s) - math.tan(lat_r) * math.sin(eps_s)
                            x_eq = math.cos(lon_tr_r)
                            ra_g_r = math.atan2(y_eq, x_eq) % (2.0 * math.pi)
                            sin_d = math.sin(lat_r) * math.cos(eps_s) + math.cos(lat_r) * math.sin(eps_s) * math.sin(lon_tr_r)
                            dec_g_r = math.asin(max(-1.0, min(1.0, sin_d)))
                            d_km = max(1e-6, p_s.distance_au) * AU_IN_KM
                            sin_pi_b = WGS84_EQUATORIAL_RADIUS_KM / max(WGS84_EQUATORIAL_RADIUS_KM * 1.01, d_km)
                            ha_g_r = lst_rad_s - ra_g_r
                            den = math.cos(dec_g_r) - rho_cos_e * sin_pi_b * math.cos(ha_g_r)
                            d_ra_r = math.atan2(-rho_cos_e * sin_pi_b * math.sin(ha_g_r), den)
                            ra_t_r = (ra_g_r + d_ra_r) % (2.0 * math.pi)
                            dec_t_r = math.atan2((math.sin(dec_g_r) - rho_sin_e * sin_pi_b) * math.cos(d_ra_r), den)
                            ha_t_r = lst_rad_s - ra_t_r
                            sin_alt_b = (
                                math.sin(phi_rad_e) * math.sin(dec_t_r)
                                + math.cos(phi_rad_e) * math.cos(dec_t_r) * math.cos(ha_t_r)
                            )
                            geom_alt_b = math.degrees(math.asin(max(-1.0, min(1.0, sin_alt_b))))
                            app_alt_b = min(90.0, geom_alt_b + _saemundsson_refraction_arcsec(geom_alt_b) / 3600.0)
                            return ra_t_r, dec_t_r, d_km, app_alt_b

                        sr_r, sd_r, s_km, s_alt = _body_topo("sun")
                        mr_r, md_r, m_km, _ = _body_topo("moon")
                        cos_sep = max(
                            -1.0,
                            min(
                                1.0,
                                math.sin(sd_r) * math.sin(md_r)
                                + math.cos(sd_r) * math.cos(md_r) * math.cos(sr_r - mr_r),
                            ),
                        )
                        sep_rad = math.acos(cos_sep)
                        r_sun_rad = math.asin(min(1.0, 695700.0 / max(1.0, s_km)))
                        r_moon_rad = math.asin(min(1.0, 1737.4 / max(1.0, m_km)))
                        if sep_rad >= r_sun_rad + r_moon_rad or r_sun_rad <= 0.0:
                            area_frac = 0.0
                        elif sep_rad <= abs(r_sun_rad - r_moon_rad):
                            area_frac = (min(r_sun_rad, r_moon_rad) ** 2) / (r_sun_rad ** 2)
                        else:
                            c_sun = max(
                                -1.0,
                                min(
                                    1.0,
                                    (sep_rad * sep_rad + r_sun_rad * r_sun_rad - r_moon_rad * r_moon_rad)
                                    / (2.0 * sep_rad * r_sun_rad),
                                ),
                            )
                            c_moon = max(
                                -1.0,
                                min(
                                    1.0,
                                    (sep_rad * sep_rad + r_moon_rad * r_moon_rad - r_sun_rad * r_sun_rad)
                                    / (2.0 * sep_rad * r_moon_rad),
                                ),
                            )
                            heron = max(
                                0.0,
                                (-sep_rad + r_sun_rad + r_moon_rad)
                                * (sep_rad + r_sun_rad - r_moon_rad)
                                * (sep_rad - r_sun_rad + r_moon_rad)
                                * (sep_rad + r_sun_rad + r_moon_rad),
                            )
                            overlap_area = (
                                (r_sun_rad * r_sun_rad) * math.acos(c_sun)
                                + (r_moon_rad * r_moon_rad) * math.acos(c_moon)
                                - 0.5 * math.sqrt(heron)
                            )
                            area_frac = overlap_area / (math.pi * r_sun_rad * r_sun_rad)
                        return area_frac, s_alt, sep_rad

                    event_max_jd = syz_jd
                    if is_amavasya:
                        # Coarse search across [-180, +180] minutes around geocentric syzygy for observer-local daylight contact
                        best_jd = syz_jd
                        best_area, best_alt, _ = _solar_topo_area_and_alt(syz_jd)
                        if best_alt <= 0.0:
                            best_area = 0.0
                        for offset_min in range(-180, 181, 10):
                            cand_jd = syz_jd + offset_min / 1440.0
                            c_area, c_alt, _ = _solar_topo_area_and_alt(cand_jd)
                            if c_alt > 0.0 and c_area > best_area:
                                best_area = c_area
                                best_alt = c_alt
                                best_jd = cand_jd
                        if best_area > 0.0:
                            # Fine 1-minute refinement around local peak daylight overlap
                            center_jd = best_jd
                            for fine_min in range(-9, 10, 1):
                                cand_jd = center_jd + fine_min / 1440.0
                                c_area, c_alt, _ = _solar_topo_area_and_alt(cand_jd)
                                if c_alt > 0.0 and c_area > best_area:
                                    best_area = c_area
                                    best_alt = c_alt
                                    best_jd = cand_jd
                            loc_vis = True
                            obsc_frac = max(0.0, min(1.0, best_area))
                            event_max_jd = best_jd
                        else:
                            loc_vis = False
                            obsc_frac = 0.0
                    else:
                        topo_rep = compute_topocentric_relativistic_astrometry(
                            syz_jd, latitude_deg, longitude_deg, ayanamsa=ayanamsa, adapter=ad
                        )
                        alt_deg = topo_rep.bodies["moon"].apparent_altitude_deg
                        loc_vis = alt_deg > 0.0
                        obsc_frac = max(0.0, min(1.0, (1.0 - node_dist / limit_deg))) if loc_vis else 0.0

                    nak_obj = nakshatra_position(axis_lon)
                    r_idx = int(axis_lon // 30.0) % 12
                    item = EclipseCatalogItem(
                        eclipse_Category=cat,
                        eclipse_subtype=subtype,
                        maximum_jd_ut=event_max_jd,
                        maximum_iso_utc=jd_to_iso_utc(event_max_jd),
                        sidereal_longitude_deg=axis_lon,
                        sidereal_classical_dms=_format_classical_rashi_dms(axis_lon),
                        rashi_name=RASI_NAMES[r_idx],
                        nakshatra_name=nak_obj.name,
                        pada=nak_obj.pada,
                        local_visible=loc_vis,
                        local_obscuration_fraction=round(obsc_frac, 4),
                    )
                    eclipses.append(item)

                    for nat_name, nat_lon in natal_map.items():
                        orb_conj = abs(_signed_angle_diff_deg(axis_lon, float(nat_lon)))
                        orb_opp = abs(_signed_angle_diff_deg((axis_lon + 180.0) % 360.0, float(nat_lon)))
                        best_orb = min(orb_conj, orb_opp)
                        if best_orb <= float(orb_deg):
                            contact = "Conjunction (0 deg)" if orb_conj <= orb_opp else "Opposition (180 deg Axis)"
                            score = round(100.0 * (1.0 - best_orb / max(0.1, float(orb_deg))), 2)
                            hits.append(
                                EclipseNatalHit(
                                    eclipse_category=cat,
                                    eclipse_subtype=subtype,
                                    eclipse_iso_utc=item.maximum_iso_utc,
                                    eclipse_sidereal_dms=item.sidereal_classical_dms,
                                    natal_point_name=nat_name,
                                    natal_sidereal_dms=_format_classical_rashi_dms(float(nat_lon)),
                                    contact_type=contact,
                                    orb_deg=round(best_orb, 4),
                                    sensitivity_score_0_to_100=score,
                                )
                            )

        prev_diff = diff
        prev_t = t_curr
        if t_curr >= float(end_jd_ut):
            break
        t_curr = min(float(end_jd_ut), t_curr + t_step)

    receipt = canonical_hash(
        {
            "start_jd_ut": round(float(start_jd_ut), 3),
            "end_jd_ut": round(float(end_jd_ut), 3),
            "eclipse_count": len(eclipses),
            "hit_count": len(hits),
        }
    )
    return EclipseNatalSensitivityReport(
        start_jd_ut=float(start_jd_ut),
        end_jd_ut=float(end_jd_ut),
        eclipses=tuple(eclipses),
        natal_hits=tuple(hits),
        receipt_sha256=receipt,
    )
