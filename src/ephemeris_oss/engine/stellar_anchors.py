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
