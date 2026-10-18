"""Topocentric Lunar Crescent Visibility (Yallop & Odeh Criteria) and Heliacal Rising/Setting.

Mathematical formulations follow published astronomical and jyotisha references:
- Yallop, B. D. (1997), *A Method for Predicting the First Sighting of the New Crescent Moon*,
  NAO Technical Note No. 69, HM Nautical Almanac Office.
- Odeh, M. S. (2004), *New Criterion for Lunar Crescent Visibility*, Experimental Astronomy,
  Vol. 18, pp. 39-64.
- Danjon, A. (1932), *Jeunes et vieilles lunes*, Bulletin de la Societe Astronomique de France,
  establishing the 7-degree lunar elongation limit for crescent formation.
- Schoch, C. (1928), *Planeten-Tafeln fur jedermann*, and Schaefer, B. E. (1987), *Heliacal
  Rise Phenomena*, Publications of the Astronomical Society of the Pacific, Vol. 99, for
  Arcus Visionis thresholds adjusted by azimuth difference and atmospheric extinction.
- *Surya Siddhanta* (Chapters 9-10, *Udayasta Adhikara*) for classical planetary and stellar
  heliacal rising (*Tara Udaya*) and setting/combustion (*Tara Asta*) Kalangsa degrees.
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Any, Final, Mapping

from .._version import __version__
from ..engine.receipt import canonical_hash

# Ratio of lunar radius to Earth equatorial radius (Yallop 1997 NAO Technical Note 69)
LUNAR_SD_TO_PARALLAX_RATIO: Final[float] = 0.27245
DANJON_LIMIT_DEG: Final[float] = 7.0
REFERENCE_EXTINCTION_K: Final[float] = 0.25


@dataclass(frozen=True)
class HeliacalBodySpec:
    """Canonical photometric and Arcus Visionis baseline for a planet or Vedic yogatara."""

    key: str
    sanskrit_name: str
    designation: str
    category: str
    visual_magnitude: float
    base_arcus_visionis_deg: float
    surya_siddhanta_kalangsa_deg: float


HELIACAL_BODY_CATALOG: Final[Mapping[str, HeliacalBodySpec]] = {
    "venus": HeliacalBodySpec(
        key="venus",
        sanskrit_name="Shukra",
        designation="Venus",
        category="planet",
        visual_magnitude=-4.0,
        base_arcus_visionis_deg=5.2,
        surya_siddhanta_kalangsa_deg=9.0,
    ),
    "jupiter": HeliacalBodySpec(
        key="jupiter",
        sanskrit_name="Brihaspati",
        designation="Jupiter",
        category="planet",
        visual_magnitude=-2.0,
        base_arcus_visionis_deg=7.5,
        surya_siddhanta_kalangsa_deg=11.0,
    ),
    "mercury": HeliacalBodySpec(
        key="mercury",
        sanskrit_name="Budha",
        designation="Mercury",
        category="planet",
        visual_magnitude=0.0,
        base_arcus_visionis_deg=10.0,
        surya_siddhanta_kalangsa_deg=13.0,
    ),
    "saturn": HeliacalBodySpec(
        key="saturn",
        sanskrit_name="Shani",
        designation="Saturn",
        category="planet",
        visual_magnitude=0.70,
        base_arcus_visionis_deg=11.0,
        surya_siddhanta_kalangsa_deg=15.0,
    ),
    "mars": HeliacalBodySpec(
        key="mars",
        sanskrit_name="Mangala",
        designation="Mars",
        category="planet",
        visual_magnitude=0.80,
        base_arcus_visionis_deg=11.5,
        surya_siddhanta_kalangsa_deg=17.0,
    ),
    "lubdhaka": HeliacalBodySpec(
        key="lubdhaka",
        sanskrit_name="Lubdhaka",
        designation="Sirius / alpha Canis Majoris",
        category="yogatara",
        visual_magnitude=-1.46,
        base_arcus_visionis_deg=8.0,
        surya_siddhanta_kalangsa_deg=12.0,
    ),
    "agastya": HeliacalBodySpec(
        key="agastya",
        sanskrit_name="Agastya",
        designation="Canopus / alpha Carinae",
        category="yogatara",
        visual_magnitude=-0.74,
        base_arcus_visionis_deg=9.0,
        surya_siddhanta_kalangsa_deg=13.0,
    ),
    "swati": HeliacalBodySpec(
        key="swati",
        sanskrit_name="Swati",
        designation="Arcturus / alpha Bootis",
        category="yogatara",
        visual_magnitude=-0.05,
        base_arcus_visionis_deg=9.8,
        surya_siddhanta_kalangsa_deg=13.0,
    ),
    "abhijit": HeliacalBodySpec(
        key="abhijit",
        sanskrit_name="Abhijit",
        designation="Vega / alpha Lyrae",
        category="yogatara",
        visual_magnitude=0.03,
        base_arcus_visionis_deg=10.0,
        surya_siddhanta_kalangsa_deg=13.0,
    ),
    "shravana": HeliacalBodySpec(
        key="shravana",
        sanskrit_name="Shravana",
        designation="Altair / alpha Aquilae",
        category="yogatara",
        visual_magnitude=0.76,
        base_arcus_visionis_deg=11.3,
        surya_siddhanta_kalangsa_deg=14.0,
    ),
    "rohini": HeliacalBodySpec(
        key="rohini",
        sanskrit_name="Rohini",
        designation="Aldebaran / alpha Tauri",
        category="yogatara",
        visual_magnitude=0.86,
        base_arcus_visionis_deg=11.6,
        surya_siddhanta_kalangsa_deg=14.0,
    ),
    "chitra": HeliacalBodySpec(
        key="chitra",
        sanskrit_name="Chitra",
        designation="Spica / alpha Virginis",
        category="yogatara",
        visual_magnitude=0.97,
        base_arcus_visionis_deg=11.8,
        surya_siddhanta_kalangsa_deg=14.0,
    ),
    "jyeshtha": HeliacalBodySpec(
        key="jyeshtha",
        sanskrit_name="Jyeshtha",
        designation="Antares / alpha Scorpii",
        category="yogatara",
        visual_magnitude=1.06,
        base_arcus_visionis_deg=12.0,
        surya_siddhanta_kalangsa_deg=14.0,
    ),
    "magha": HeliacalBodySpec(
        key="magha",
        sanskrit_name="Magha",
        designation="Regulus / alpha Leonis",
        category="yogatara",
        visual_magnitude=1.36,
        base_arcus_visionis_deg=12.5,
        surya_siddhanta_kalangsa_deg=15.0,
    ),
    "krittika": HeliacalBodySpec(
        key="krittika",
        sanskrit_name="Krittika",
        designation="Alcyone / eta Tauri",
        category="yogatara",
        visual_magnitude=2.87,
        base_arcus_visionis_deg=14.8,
        surya_siddhanta_kalangsa_deg=17.0,
    ),
}

HELIACAL_BODY_ALIASES: Final[Mapping[str, str]] = {
    "shukra": "venus",
    "brihaspati": "jupiter",
    "guru": "jupiter",
    "budha": "mercury",
    "shani": "saturn",
    "mangala": "mars",
    "kuja": "mars",
    "sirius": "lubdhaka",
    "canopus": "agastya",
    "aldebaran": "rohini",
    "spica": "chitra",
    "citra": "chitra",
    "arcturus": "swati",
    "vega": "abhijit",
    "altair": "shravana",
    "antares": "jyeshtha",
    "regulus": "magha",
    "alcyone": "krittika",
}


@dataclass(frozen=True)
class CrescentVisibilityReport:
    """Topocentric lunar crescent visibility report under Yallop (1997) and Odeh (2004)."""

    arcl_deg: float
    arcv_deg: float
    daz_deg: float
    moon_parallax_deg: float
    semidiameter_arcmin: float
    crescent_width_arcmin: float
    yallop_arcv_crit_deg: float
    yallop_q: float
    yallop_zone: str
    yallop_description: str
    odeh_arcv_crit_deg: float
    odeh_v: float
    odeh_zone: str
    odeh_description: str
    below_danjon_limit: bool
    is_naked_eye_visible: bool
    is_optically_visible: bool
    receipt: Mapping[str, Any]
    receipt_sha256: str

    @property
    def sd_arcmin(self) -> float:
        return self.semidiameter_arcmin

    @property
    def w_arcmin(self) -> float:
        return self.crescent_width_arcmin

    @property
    def arcv_crit_deg(self) -> float:
        return self.yallop_arcv_crit_deg

    @property
    def q(self) -> float:
        return self.yallop_q

    @property
    def v(self) -> float:
        return self.odeh_v


@dataclass(frozen=True)
class HeliacalVisibilityReport:
    """Planetary or stellar heliacal rising/setting (*Tara Udaya/Asta*) evaluation report."""

    body: str
    sanskrit_name: str
    designation: str
    category: str
    visual_magnitude: float
    surya_siddhanta_kalangsa_deg: float
    sun_alt_deg: float
    body_alt_deg: float
    daz_deg: float
    atmospheric_extinction_k: float
    arcus_visionis_deg: float
    critical_arcus_visionis_deg: float
    margin_deg: float
    is_visible: bool
    tara_state: str
    receipt: Mapping[str, Any]
    receipt_sha256: str


def evaluate_crescent_visibility(
    arcl_deg: float,
    arcv_deg: float,
    daz_deg: float,
    moon_parallax_deg: float = 0.95,
) -> CrescentVisibilityReport:
    """Evaluate topocentric lunar crescent visibility using Yallop (1997) and Odeh (2004).

    Parameters
    ----------
    arcl_deg:
        Arc of Light (topocentric elongation between Sun and Moon) in degrees.
    arcv_deg:
        Arc of Vision (topocentric altitude difference `moon_alt - sun_alt`) in degrees.
    daz_deg:
        Relative azimuth difference `|sun_az - moon_az|` in degrees.
    moon_parallax_deg:
        Lunar equatorial horizontal parallax in degrees (default `0.95` deg = `57.0` arcmin).
    """
    arcl = float(arcl_deg)
    arcv = float(arcv_deg)
    daz = float(daz_deg)
    pi_deg = float(moon_parallax_deg)

    if not all(math.isfinite(val) for val in (arcl, arcv, daz, pi_deg)):
        raise ValueError("All crescent visibility inputs must be finite numbers")
    if pi_deg <= 0.0:
        raise ValueError("moon_parallax_deg must be positive")

    # Convert horizontal parallax from degrees to arcminutes for Yallop/Odeh formulas
    pi_arcmin = pi_deg * 60.0
    sd_arcmin = LUNAR_SD_TO_PARALLAX_RATIO * pi_arcmin
    w_arcmin = sd_arcmin * (1.0 - math.cos(math.radians(arcl)))

    w_poly = -6.3226 * w_arcmin + 0.7319 * (w_arcmin ** 2) - 0.1018 * (w_arcmin ** 3)

    # Yallop (1997) NAO Technical Note 69
    yallop_arcv_crit = 11.8371 + w_poly
    yallop_q = (arcv - yallop_arcv_crit) / 10.0

    # Odeh (2004) Experimental Astronomy
    odeh_arcv_crit = 7.1651 + w_poly
    odeh_v = arcv - odeh_arcv_crit

    below_danjon = abs(arcl) < DANJON_LIMIT_DEG

    if below_danjon or yallop_q <= -0.293:
        yallop_zone = "F"
        yallop_desc = "Not visible; below Danjon limit or horizon threshold"
    elif yallop_q > 0.216:
        yallop_zone = "A"
        yallop_desc = "Easily visible by naked eye"
    elif yallop_q > -0.014:
        yallop_zone = "B"
        yallop_desc = "Visible under perfect atmospheric conditions"
    elif yallop_q > -0.160:
        yallop_zone = "C"
        yallop_desc = "May need optical aid to find the crescent first"
    elif yallop_q > -0.232:
        yallop_zone = "D"
        yallop_desc = "Visible only with optical aid"
    else:
        yallop_zone = "E"
        yallop_desc = "Not visible with telescope"

    if below_danjon or odeh_v < -0.96:
        odeh_zone = "D"
        odeh_desc = "Not visible"
    elif odeh_v >= 5.65:
        odeh_zone = "A"
        odeh_desc = "Visible by naked eye"
    elif odeh_v >= 2.0:
        odeh_zone = "B"
        odeh_desc = "Visible by optical aid; naked eye under good sky"
    else:
        odeh_zone = "C"
        odeh_desc = "Visible by optical aid only"

    naked_eye = (not below_danjon) and (yallop_zone in ("A", "B") or odeh_v >= 2.0)
    optical = (not below_danjon) and (yallop_zone in ("A", "B", "C", "D") or odeh_v >= -0.96)

    receipt_payload: dict[str, Any] = {
        "module": "ephemeris_oss.almanac.visibility",
        "function": "evaluate_crescent_visibility",
        "version": __version__,
        "arcl_deg": round(arcl, 8),
        "arcv_deg": round(arcv, 8),
        "daz_deg": round(daz, 8),
        "moon_parallax_deg": round(pi_deg, 8),
        "semidiameter_arcmin": round(sd_arcmin, 8),
        "crescent_width_arcmin": round(w_arcmin, 8),
        "yallop_arcv_crit_deg": round(yallop_arcv_crit, 8),
        "yallop_q": round(yallop_q, 8),
        "yallop_zone": yallop_zone,
        "odeh_arcv_crit_deg": round(odeh_arcv_crit, 8),
        "odeh_v": round(odeh_v, 8),
        "odeh_zone": odeh_zone,
        "below_danjon_limit": below_danjon,
    }
    r_sha = canonical_hash(receipt_payload)

    return CrescentVisibilityReport(
        arcl_deg=arcl,
        arcv_deg=arcv,
        daz_deg=daz,
        moon_parallax_deg=pi_deg,
        semidiameter_arcmin=round(sd_arcmin, 8),
        crescent_width_arcmin=round(w_arcmin, 8),
        yallop_arcv_crit_deg=round(yallop_arcv_crit, 8),
        yallop_q=round(yallop_q, 8),
        yallop_zone=yallop_zone,
        yallop_description=yallop_desc,
        odeh_arcv_crit_deg=round(odeh_arcv_crit, 8),
        odeh_v=round(odeh_v, 8),
        odeh_zone=odeh_zone,
        odeh_description=odeh_desc,
        below_danjon_limit=below_danjon,
        is_naked_eye_visible=naked_eye,
        is_optically_visible=optical,
        receipt=receipt_payload,
        receipt_sha256=r_sha,
    )


def resolve_heliacal_body(body: str) -> HeliacalBodySpec:
    """Resolve a canonical planet or Vedic yogatara identifier."""
    norm = str(body or "").strip().lower().replace("-", "_").replace(" ", "_")
    canonical = HELIACAL_BODY_ALIASES.get(norm, norm)
    if canonical not in HELIACAL_BODY_CATALOG:
        supported = ", ".join(sorted(HELIACAL_BODY_CATALOG))
        raise ValueError(f"Unsupported heliacal body {body!r}; supported keys: {supported}")
    return HELIACAL_BODY_CATALOG[canonical]


def evaluate_heliacal_visibility(
    body: str,
    sun_alt_deg: float,
    body_alt_deg: float,
    daz_deg: float,
    *,
    atmospheric_extinction_k: float = REFERENCE_EXTINCTION_K,
) -> HeliacalVisibilityReport:
    """Evaluate planetary or stellar heliacal rising/setting (*Tara Udaya/Asta*).

    Uses Schoch (1928) and Schaefer (1987) critical Arcus Visionis thresholds
    adjusted for azimuth difference `daz_deg` and atmospheric extinction `k`.
    """
    spec = resolve_heliacal_body(body)
    s_alt = float(sun_alt_deg)
    b_alt = float(body_alt_deg)
    daz = float(daz_deg)
    ext_k = float(atmospheric_extinction_k)

    if not all(math.isfinite(val) for val in (s_alt, b_alt, daz, ext_k)):
        raise ValueError("All heliacal visibility numerical inputs must be finite")
    if ext_k <= 0.0 or ext_k > 2.0:
        raise ValueError("atmospheric_extinction_k must be within (0.0, 2.0]")

    # Observed Arcus Visionis: AV = body_alt_deg - sun_alt_deg
    arcus_visionis = b_alt - s_alt

    # Schoch (1928) parabolic azimuth reduction: wider azimuth separation from the
    # solar twilight glow lowers the required vertical Arcus Visionis.
    abs_daz = min(abs(daz), 90.0)
    daz_reduction = min(0.001 * (abs_daz ** 2), 2.5)

    # Schaefer (1987) extinction sensitivity near the horizon (~8 deg per unit k from k0=0.25)
    extinction_delta = 8.0 * (ext_k - REFERENCE_EXTINCTION_K)

    critical_av = max(spec.base_arcus_visionis_deg - daz_reduction + extinction_delta, 2.0)
    margin = arcus_visionis - critical_av

    # Heliacally visible (Udaya) when AV meets critical threshold, Sun is at/below horizon,
    # and the body is above the refracted horizon band (>= -1.0 deg).
    is_visible = bool(margin >= 0.0 and s_alt <= 0.0 and b_alt >= -1.0)
    tara_state = "Udaya" if is_visible else "Asta"

    receipt_payload: dict[str, Any] = {
        "module": "ephemeris_oss.almanac.visibility",
        "function": "evaluate_heliacal_visibility",
        "version": __version__,
        "body": spec.key,
        "sanskrit_name": spec.sanskrit_name,
        "visual_magnitude": spec.visual_magnitude,
        "sun_alt_deg": round(s_alt, 8),
        "body_alt_deg": round(b_alt, 8),
        "daz_deg": round(daz, 8),
        "atmospheric_extinction_k": round(ext_k, 8),
        "arcus_visionis_deg": round(arcus_visionis, 8),
        "critical_arcus_visionis_deg": round(critical_av, 8),
        "margin_deg": round(margin, 8),
        "is_visible": is_visible,
        "tara_state": tara_state,
    }
    r_sha = canonical_hash(receipt_payload)

    return HeliacalVisibilityReport(
        body=spec.key,
        sanskrit_name=spec.sanskrit_name,
        designation=spec.designation,
        category=spec.category,
        visual_magnitude=spec.visual_magnitude,
        surya_siddhanta_kalangsa_deg=spec.surya_siddhanta_kalangsa_deg,
        sun_alt_deg=s_alt,
        body_alt_deg=b_alt,
        daz_deg=daz,
        atmospheric_extinction_k=ext_k,
        arcus_visionis_deg=round(arcus_visionis, 8),
        critical_arcus_visionis_deg=round(critical_av, 8),
        margin_deg=round(margin, 8),
        is_visible=is_visible,
        tara_state=tara_state,
        receipt=receipt_payload,
        receipt_sha256=r_sha,
    )


__all__ = [
    "CrescentVisibilityReport",
    "DANJON_LIMIT_DEG",
    "HELIACAL_BODY_ALIASES",
    "HELIACAL_BODY_CATALOG",
    "HeliacalBodySpec",
    "HeliacalVisibilityReport",
    "LUNAR_SD_TO_PARALLAX_RATIO",
    "REFERENCE_EXTINCTION_K",
    "evaluate_crescent_visibility",
    "evaluate_heliacal_visibility",
    "resolve_heliacal_body",
]
