"""Versioned ICRS catalog data and geocentric apparent star places.

SOFA/ERFA atci13 applies proper motion, annual parallax, solar deflection and
aberration in IAU2006/2000A. The returned longitude is on the mean ecliptic;
ayanamsa_degrees supplies the paired true-frame nutation. Explicit apparent=False
retains the former propagated barycentric astrometric calculation.
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from types import MappingProxyType
from typing import Mapping

import erfa
import numpy as np

from .contracts import AstronomyDataUnavailable

J2000_JD = 2451545.0
STELLAR_ANCHOR_CATALOG_VERSION = "simbad-icrs-2026-10-06-erfa-apparent-2"


@dataclass(frozen=True)
class StellarAnchor:
    key: str
    designation: str
    ra_icrs_deg_j2000: float
    dec_icrs_deg_j2000: float
    pm_ra_cos_dec_mas_per_year: float
    pm_dec_mas_per_year: float
    parallax_mas: float
    radial_velocity_km_per_s: float
    source_reference: str


STELLAR_ANCHORS: Mapping[str, StellarAnchor] = MappingProxyType(
    {
        "true_citra": StellarAnchor(
            key="true_citra",
            designation="Spica / alpha Virginis / HIP 65474",
            ra_icrs_deg_j2000=201.298247375,
            dec_icrs_deg_j2000=-11.161319472222223,
            pm_ra_cos_dec_mas_per_year=-42.35,
            pm_dec_mas_per_year=-30.67,
            parallax_mas=13.06,
            radial_velocity_km_per_s=-3.310,
            source_reference=(
                "SIMBAD alpha Virginis snapshot retrieved 2026-10-06; "
                "ICRS J2000 astrometry and cited catalog values"
            ),
        ),
        "pushya": StellarAnchor(
            key="pushya",
            designation="Asellus Australis / delta Cancri / HIP 42911",
            ra_icrs_deg_j2000=131.17124658768915,
            dec_icrs_deg_j2000=18.154308069054164,
            pm_ra_cos_dec_mas_per_year=-18.435,
            pm_dec_mas_per_year=-227.813,
            parallax_mas=23.8271,
            radial_velocity_km_per_s=17.14,
            source_reference=(
                "SIMBAD delta Cancri snapshot retrieved 2026-10-06; "
                "Gaia EDR3 ICRS J2000 astrometry and cited radial velocity"
            ),
        ),
    }
)

_AYANAMSA_TO_ANCHOR = MappingProxyType(
    {
        "true_citra": "true_citra",
        "true_chitra": "true_citra",
        "true_chitrapaksha": "true_citra",
        "true_chitra_paksha": "true_citra",
        "pushya": "pushya",
        "pushya_paksha": "pushya",
        "true_pushya": "pushya",
        "true_pushya_paksha": "pushya",
    }
)


def stellar_anchor_for_ayanamsa(convention: str) -> StellarAnchor | None:
    key = str(convention or "").strip().lower().replace(" ", "_")
    anchor_key = _AYANAMSA_TO_ANCHOR.get(key)
    return None if anchor_key is None else STELLAR_ANCHORS[anchor_key]


def tropical_longitude_degrees(
    anchor: StellarAnchor,
    *,
    tt: tuple[float, float],
    apparent: bool = True,
) -> float:
    """Mean-frame geocentric apparent longitude; explicit false keeps astrometric mode."""

    if len(tt) != 2 or not all(math.isfinite(value) for value in tt):
        raise AstronomyDataUnavailable("TT must contain two finite Julian-date parts")
    ra = math.radians(anchor.ra_icrs_deg_j2000)
    dec = math.radians(anchor.dec_icrs_deg_j2000)
    cos_dec = math.cos(dec)
    if abs(cos_dec) < 1e-15:
        raise AstronomyDataUnavailable("stellar anchor is singular at the celestial pole")
    pm_ra = (
        anchor.pm_ra_cos_dec_mas_per_year / 1000.0 * erfa.DAS2R / cos_dec
    )
    pm_dec = anchor.pm_dec_mas_per_year / 1000.0 * erfa.DAS2R
    if apparent:
        # Point-source stellar definitions retain the unregularized solar term.
        # atci13 hard-codes a solar-disc limiter and changes conjunctions.
        astrom, eo = erfa.apci13(*tt)
        natural = erfa.pmpx(ra, dec, pm_ra, pm_dec, anchor.parallax_mas/1000,
                            anchor.radial_velocity_km_per_s, astrom["pmt"], astrom["eb"])
        deflected = erfa.ld(1., natural, natural, astrom["eh"], astrom["em"], 0.0)
        aberrated = erfa.ab(deflected, astrom["v"], astrom["em"], astrom["bm1"])
        ri, di = erfa.c2s(astrom["bpn"] @ aberrated)
        equinox_ra = float(ri-eo)
        dpsi, deps = erfa.nut06a(*tt)
        obliquity = float(erfa.obl06(*tt)+deps)
        x = math.cos(equinox_ra)*math.cos(float(di))
        y = math.sin(equinox_ra)*math.cos(float(di))*math.cos(obliquity)+math.sin(float(di))*math.sin(obliquity)
        return (math.degrees(math.atan2(y,x))-math.degrees(float(dpsi)))%360
    try:
        propagated_ra, propagated_dec, *_ = erfa.pmsafe(
            ra,
            dec,
            pm_ra,
            pm_dec,
            anchor.parallax_mas / 1000.0,
            anchor.radial_velocity_km_per_s,
            J2000_JD,
            0.0,
            *tt,
        )
    except (ValueError, erfa.ErfaError) as error:
        raise AstronomyDataUnavailable("stellar-anchor propagation failed") from error
    icrs_direction = np.asarray(erfa.s2c(propagated_ra, propagated_dec), dtype=np.float64)
    ecliptic_direction = np.asarray(erfa.ecm06(*tt), dtype=np.float64) @ icrs_direction
    return math.degrees(
        math.atan2(float(ecliptic_direction[1]), float(ecliptic_direction[0]))
    ) % 360.0


# ============================================================================
# Complete 30-Star Gaia/Hipparcos ICRS Yogatara Catalog & Stellar Bheda Engine
# ============================================================================


@dataclass(frozen=True)
class YogataraStarEntry:
    """ICRS J2000 6-parameter astrometric entry for a Vedic Nakshatra Yogatara or sacred star."""

    key: str
    vedic_name: str
    western_designation: str
    hip_id: int
    nakshatra_number: int | None
    ra_icrs_deg_j2000: float
    dec_icrs_deg_j2000: float
    pm_ra_cos_dec_mas_per_year: float
    pm_dec_mas_per_year: float
    parallax_mas: float
    radial_velocity_km_per_s: float
    visual_magnitude: float
    kalansha_visibility_arc_deg: float


# All 27 classical Nakshatra Yogataras + 28th Abhijit (Vega) + Agastya (Canopus) + Lubdhaka (Sirius)
YOGATARA_30_CATALOG: tuple[YogataraStarEntry, ...] = (
    YogataraStarEntry("ashwini", "Ashwini", "Sheratan / beta Arietis", 8903, 1, 28.660046, 20.808030, 97.26, -108.84, 54.74, -1.9, 2.64, 13.0),
    YogataraStarEntry("bharani", "Bharani", "41 Arietis / c Arietis", 13209, 2, 42.496012, 27.260506, 65.87, -116.58, 19.65, 4.0, 3.61, 14.0),
    YogataraStarEntry("krittika", "Krittika", "Alcyone / eta Tauri", 17702, 3, 56.871154, 24.105136, 19.34, -43.67, 8.09, 10.1, 2.87, 13.0),
    YogataraStarEntry("rohini", "Rohini", "Aldebaran / alpha Tauri", 21421, 4, 68.980163, 16.509302, 63.45, -188.94, 48.94, 54.26, 0.86, 12.0),
    YogataraStarEntry("mrigashirsha", "Mrigashirsha", "Meissa / lambda Orionis", 26207, 5, 83.784490, 9.934156, -0.21, -2.69, 2.97, 30.1, 3.39, 14.0),
    YogataraStarEntry("ardra", "Ardra", "Betelgeuse / alpha Orionis", 27989, 6, 88.792939, 7.407064, 27.54, 11.30, 6.55, 21.91, 0.50, 12.0),
    YogataraStarEntry("punarvasu", "Punarvasu", "Pollux / beta Geminorum", 37826, 7, 116.328958, 28.026199, -626.55, -45.80, 96.54, 3.23, 1.14, 12.0),
    YogataraStarEntry("pushya", "Pushya", "Asellus Australis / delta Cancri", 42911, 8, 131.171247, 18.154308, -18.435, -227.813, 23.8271, 17.14, 3.94, 14.0),
    YogataraStarEntry("ashlesha", "Ashlesha", "Minchir / zeta Hydrae", 43813, 9, 133.848444, 5.945571, -99.13, 12.56, 19.51, 22.86, 3.11, 13.5),
    YogataraStarEntry("magha", "Magha", "Regulus / alpha Leonis", 49669, 10, 152.092962, 11.967209, -248.73, 5.59, 41.13, 5.9, 1.36, 12.0),
    YogataraStarEntry("purva_phalguni", "Purva Phalguni", "Zosma / delta Leonis", 54872, 11, 168.527089, 20.523718, 143.42, -129.88, 55.82, -20.2, 2.56, 13.0),
    YogataraStarEntry("uttara_phalguni", "Uttara Phalguni", "Denebola / beta Leonis", 57632, 12, 177.264910, 14.572058, -497.68, -114.67, 90.91, -0.2, 2.14, 12.5),
    YogataraStarEntry("hasta", "Hasta", "Algorab / delta Corvi", 60965, 13, 187.466071, -16.515427, -210.22, -138.64, 37.55, 8.7, 2.95, 13.5),
    YogataraStarEntry("chitra", "Chitra", "Spica / alpha Virginis", 65474, 14, 201.298247, -11.161319, -42.35, -30.67, 13.06, -3.31, 0.97, 12.0),
    YogataraStarEntry("swati", "Swati", "Arcturus / alpha Bootis", 69673, 15, 213.915300, 19.182409, -1093.39, -2000.06, 88.83, -5.19, -0.05, 11.0),
    YogataraStarEntry("vishakha", "Vishakha", "Zubenelgenubi / alpha2 Librae", 72622, 16, 222.719638, -16.041777, -105.68, -68.40, 43.03, -23.3, 2.75, 13.0),
    YogataraStarEntry("anuradha", "Anuradha", "Dschubba / delta Scorpii", 78401, 17, 240.083359, -22.621710, -10.21, -35.41, 6.64, -7.0, 2.31, 13.0),
    YogataraStarEntry("jyeshtha", "Jyeshtha", "Antares / alpha Scorpii", 80763, 18, 247.351915, -26.432003, -12.11, -23.30, 5.89, -3.4, 0.96, 12.0),
    YogataraStarEntry("mula", "Mula", "Shaula / lambda Scorpii", 85927, 19, 263.402167, -37.103824, -0.89, -30.80, 5.71, -3.0, 1.62, 12.5),
    YogataraStarEntry("purva_ashadha", "Purva Ashadha", "Kaus Media / delta Sagittarii", 89931, 20, 275.248511, -29.828102, 35.81, -27.95, 9.39, -20.0, 2.70, 13.0),
    YogataraStarEntry("uttara_ashadha", "Uttara Ashadha", "Nunki / sigma Sagittarii", 92855, 21, 283.816360, -26.296724, 15.14, -53.43, 14.32, -11.2, 2.05, 12.5),
    YogataraStarEntry("shravana", "Shravana", "Altair / alpha Aquilae", 97649, 22, 297.695827, 8.868321, 536.23, 385.29, 194.95, -26.1, 0.76, 12.0),
    YogataraStarEntry("dhanishta", "Dhanishta", "Rotanev / beta Delphini", 101769, 23, 309.387258, 14.595086, 111.78, -32.78, 32.39, -23.6, 3.63, 14.0),
    YogataraStarEntry("shatabhisha", "Shatabhisha", "Hydor / lambda Aquarii", 112961, 24, 343.153629, -7.579605, 8.89, 36.66, 8.48, -8.7, 3.73, 14.0),
    YogataraStarEntry("purva_bhadrapada", "Purva Bhadrapada", "Markab / alpha Pegasi", 113963, 25, 346.190223, 15.205267, 60.40, -41.30, 24.46, -3.5, 2.48, 13.0),
    YogataraStarEntry("uttara_bhadrapada", "Uttara Bhadrapada", "Alpheratz / alpha Andromedae", 677, 26, 2.096916, 29.090431, 135.68, -162.95, 33.62, -11.7, 2.06, 12.5),
    YogataraStarEntry("revati", "Revati", "Revati / zeta Piscium A", 5737, 27, 18.423225, 7.576670, 146.79, -49.11, 21.64, 10.6, 5.21, 15.0),
    # 28th intercalary Nakshatra & two supreme Vedic seasonal stars:
    YogataraStarEntry("abhijit", "Abhijit", "Vega / alpha Lyrae", 91262, 28, 279.234735, 38.783689, 200.94, 286.23, 130.23, -20.6, 0.03, 11.0),
    YogataraStarEntry("agastya", "Agastya", "Canopus / alpha Carinae", 30438, None, 95.987958, -52.695661, 19.93, 23.24, 10.55, 20.3, -0.74, 13.0),
    YogataraStarEntry("lubdhaka", "Lubdhaka", "Sirius / alpha Canis Majoris", 32349, None, 101.287155, -16.716116, -546.01, -1223.07, 379.21, -5.50, -1.46, 13.0),
)


@dataclass(frozen=True)
class YogataraStarPosition:
    """Propagated apparent geocentric coordinates and heliacal visibility of a Yogatara star."""

    key: str
    vedic_name: str
    western_designation: str
    hip_id: int
    nakshatra_number: int | None
    tropical_longitude_deg: float
    sidereal_longitude_deg: float
    ecliptic_latitude_shara_deg: float
    ra_deg: float
    dec_deg: float
    proper_motion_shift_arcsec_since_j2000: float
    solar_elongation_deg: float
    is_heliacally_visible: bool
    visibility_status: str


def propagate_yogatara_apparent(
    star: YogataraStarEntry,
    *,
    tt: tuple[float, float],
    ayanamsa_deg: float,
    sun_tropical_lon_deg: float = 0.0,
) -> YogataraStarPosition:
    """Propagate a Yogatara star from J2000 ICRS to apparent geocentric ecliptic and equatorial coordinates."""
    ra = math.radians(star.ra_icrs_deg_j2000)
    dec = math.radians(star.dec_icrs_deg_j2000)
    cos_dec = max(1e-12, abs(math.cos(dec)))
    pm_ra = star.pm_ra_cos_dec_mas_per_year / 1000.0 * erfa.DAS2R / cos_dec
    pm_dec = star.pm_dec_mas_per_year / 1000.0 * erfa.DAS2R

    jd_tt = float(tt[0] + tt[1])
    years_from_j2000 = (jd_tt - J2000_JD) / 365.25
    pm_total_mas_yr = math.hypot(star.pm_ra_cos_dec_mas_per_year, star.pm_dec_mas_per_year)
    pm_shift_arcsec = abs(years_from_j2000) * (pm_total_mas_yr / 1000.0)

    if 1600.0 <= 2000.0 + years_from_j2000 <= 2400.0:
        astrom, eo = erfa.apci13(*tt)
        natural = erfa.pmpx(
            ra,
            dec,
            pm_ra,
            pm_dec,
            star.parallax_mas / 1000.0,
            star.radial_velocity_km_per_s,
            astrom["pmt"],
            astrom["eb"],
        )
        deflected = erfa.ld(1.0, natural, natural, astrom["eh"], astrom["em"], 0.0)
        aberrated = erfa.ab(deflected, astrom["v"], astrom["em"], astrom["bm1"])
        ri, di = erfa.c2s(astrom["bpn"] @ aberrated)
        equinox_ra = float(ri - eo)
        dpsi, deps = erfa.nut06a(*tt)
        obliquity = float(erfa.obl06(*tt) + deps)
        x = math.cos(equinox_ra) * math.cos(float(di))
        y = math.sin(equinox_ra) * math.cos(float(di)) * math.cos(obliquity) + math.sin(float(di)) * math.sin(obliquity)
        z = -math.sin(equinox_ra) * math.cos(float(di)) * math.sin(obliquity) + math.sin(float(di)) * math.cos(obliquity)
        trop_lon = (math.degrees(math.atan2(y, x)) - math.degrees(float(dpsi))) % 360.0
        ecl_lat = math.degrees(math.asin(max(-1.0, min(1.0, z))))
        ra_deg = math.degrees(equinox_ra) % 360.0
        dec_deg = math.degrees(float(di))
    else:
        propagated_ra, propagated_dec, *_ = erfa.pmsafe(
            ra,
            dec,
            pm_ra,
            pm_dec,
            star.parallax_mas / 1000.0,
            star.radial_velocity_km_per_s,
            J2000_JD,
            0.0,
            *tt,
        )
        icrs_dir = np.asarray(erfa.s2c(propagated_ra, propagated_dec), dtype=np.float64)
        epj = erfa.epj(*tt)
        ecl_mat = np.asarray(erfa.ltecm(epj), dtype=np.float64)
        ecl_dir = ecl_mat @ icrs_dir
        trop_lon = math.degrees(math.atan2(float(ecl_dir[1]), float(ecl_dir[0]))) % 360.0
        ecl_lat = math.degrees(math.asin(max(-1.0, min(1.0, float(ecl_dir[2])))))
        eq_mat = np.asarray(erfa.ltp(epj), dtype=np.float64)
        eq_dir = eq_mat @ icrs_dir
        eq_ra, eq_dec = erfa.c2s(eq_dir)
        ra_deg = math.degrees(float(eq_ra)) % 360.0
        dec_deg = math.degrees(float(eq_dec))

    sid_lon = (trop_lon - float(ayanamsa_deg)) % 360.0
    raw_diff = abs((trop_lon - float(sun_tropical_lon_deg)) % 360.0)
    lon_sep = 360.0 - raw_diff if raw_diff > 180.0 else raw_diff
    elong_deg = math.degrees(
        math.acos(
            max(
                -1.0,
                min(
                    1.0,
                    math.cos(math.radians(ecl_lat)) * math.cos(math.radians(lon_sep)),
                ),
            )
        )
    )
    visible = elong_deg >= star.kalansha_visibility_arc_deg
    vis_status = "Udaya (Visible)" if visible else "Asta (Heliacally Combust)"

    return YogataraStarPosition(
        key=star.key,
        vedic_name=star.vedic_name,
        western_designation=star.western_designation,
        hip_id=star.hip_id,
        nakshatra_number=star.nakshatra_number,
        tropical_longitude_deg=round(trop_lon, 8),
        sidereal_longitude_deg=round(sid_lon, 8),
        ecliptic_latitude_shara_deg=round(ecl_lat, 8),
        ra_deg=round(ra_deg, 8),
        dec_deg=round(dec_deg, 8),
        proper_motion_shift_arcsec_since_j2000=round(pm_shift_arcsec, 4),
        solar_elongation_deg=round(elong_deg, 6),
        is_heliacally_visible=visible,
        visibility_status=vis_status,
    )

