"""Independent Jyotish convention mathematics for the dark astronomy provider.

This module contains no runtime wiring and no calls into the legacy ephemeris.
It deliberately separates astronomical quantities (TT, UT1, stellar
longitudes, and Moon state vectors) from Jyotish convention choices.

References
----------
* Capitaine, Wallace & Chapront (2003), A&A 412, 567-586, and Hilton et al.
  (2006), Celestial Mechanics 94, 351-367: IAU 2006 precession and sidereal
  time, exposed by ERFA ``p06e``, ``era00``, ``gmst06``, and ``gst06a``.
* Meeus, Astronomical Algorithms, 2nd ed., chapter 47: mean lunar-node
  polynomial in Julian centuries from J2000.0.
* Report of the Calendar Reform Committee (CSIR, New Delhi, 1955): Chitra
  Paksha convention, ayanamsa 23° 15' relating to 21 March 1956. The
  refinement to 23° 15' 00.658" true at 1956-03-21.0 TT is the Indian Astronomical
  Ephemeris (IAE 1989, p. 556) standard realization. IAU 1980 nutation is removed and the IAU 1976 equinox is
  converted to the Vondrak et al. (2011) frame. Mean and true outputs are kept
  explicit; no parameter is fitted to another library's output.
* Raman, Krishnamurti, Sri Yukteswar and Fagan-Bradley anchors are the widely
  used realisations of those authors' definitions, labelled per entry below
  with what each author's own text states. They are explicit, versioned
  software anchors, not claims that all published variants agree.
* Tropical / Sayana convention: The dark engine's ECLIPTIC_OF_DATE frame
  represents the mean ecliptic and equinox of date (via IAU 2006 precession
  erfa.ecm06). It does not include nutation in longitude (delta_psi approx
  -14.7" on 1990-08-15). Against non-nutated astronomical reference ephemerides, positions
  agree to sub-arcsecond. Full true-equinox Sayana support with nutation is
  deferred; in nirayana (sidereal) mode with Lahiri ayanamsa, the mean frame is
  consistent and nutation cancels out.
* P.V.R. Narasimha Rao, "Introducing Pushya-paksha Ayanamsa": Delta Cancri is
  fixed at 106 degrees sidereal. True Citra analogously fixes Spica at
  180 degrees sidereal.
* Porphyry, Introduction to the Tetrabiblos: trisect the four ecliptic arcs
  between Ascendant, IC, Descendant, and MC. Sripati uses those twelve points
  as bhava centres and places boundaries halfway between adjacent centres.

Mean convention operations cover the declared DE441 Julian-date interval using
Vondrak long-term precession. True-frame nutation retains its modern bound.
Star-anchored conventions require a separately computed, provenance-bearing
stellar longitude for the requested instant and never fall back to a mean
offset.
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from types import MappingProxyType
from typing import Mapping, Sequence

import erfa

from .contracts import AstronomyDataUnavailable
from .civil_time import CalendarSystem, calendar_jd
from .earth_orientation import estimate_delta_t

J2000_TT_JD = 2451545.0
JULIAN_CENTURY_DAYS = 36525.0
AYANAMSA_VALID_CENTURIES = 4.0
AYANAMSA_CATALOG_VERSION = "ephemeris-oss-ayanamsa-anchors-1.4.0"
AYANAMSA_MIN_TT_JD = -3100015.5
AYANAMSA_MAX_TT_JD = 8000016.5
TT_TDB_MAX_ABS_DAYS = 1.0 / 86400.0
HOUSE_CONVENTIONS_VERSION = "ephemeris-oss-houses-1.1.0-iau2006"
LUNAR_NODE_CONVENTIONS_VERSION = "ephemeris-oss-lunar-nodes-1.1.0-meeus47.7"


@dataclass(frozen=True)
class AyanamsaDefinition:
    """One explicit named sidereal-zero policy.

    Fixed entries transport the date equinox to a declared reference ecliptic
    using long-term precession. Stellar and polar entries consume a separately
    supplied longitude at the same TT instant; they do not invent astrometry.
    """

    key: str
    label: str
    model: str
    reference_jd_tt: float | None
    reference_offset_deg: float | None
    sidereal_anchor_deg: float | None
    source_reference: str
    aliases: tuple[str, ...] = ()
    reference_equinox_displacement_arcsec: float = 0.0
    precession_model: str = "IAU2006"
    reference_frame: str = "mean ecliptic/equinox of reference epoch"
    original_author_ambiguity: str = ""
    galactic_pole_icrs_deg: tuple[float, float] | None = None


def _dms(degrees: float, minutes: float, seconds: float) -> float:
    return degrees + minutes / 60.0 + seconds / 3600.0


# Lahiri: 23° 15' at 21 March 1956 per the Calendar Reform Committee report
# (CSIR, 1955); the 00.658" true value at 0h TT is the Indian Astronomical Ephemeris
# (IAE 1989 p. 556) refinement. ERFA provides the Lieske
# 1976, Wahr 1980 and Vondrak/Capitaine/Wallace 2011 reductions.
LAHIRI_REFERENCE_TT_JD = 2435553.5
LAHIRI_REFERENCE_TRUE_DEG = _dms(23, 15, .658)
_LAHIRI_TT = (J2000_TT_JD, LAHIRI_REFERENCE_TT_JD - J2000_TT_JD)
_LAHIRI_EPOCH = float(erfa.epj(*_LAHIRI_TT))
_LAHIRI_PRECESSION = erfa.ltp(_LAHIRI_EPOCH)
_LAHIRI_OBLIQUITY = math.acos(sum(float(a) * float(b) for a, b in zip(
    erfa.ltpequ(_LAHIRI_EPOCH), erfa.ltpecl(_LAHIRI_EPOCH))))
_LAHIRI_REFERENCE_MEAN_DEG = LAHIRI_REFERENCE_TRUE_DEG - math.degrees(float(erfa.nut80(*_LAHIRI_TT)[0]))


def _lahiri_reference_longitude(vector: Sequence[float]) -> float:
    """Longitude of a vector on the reference epoch's mean ecliptic."""
    return math.degrees(math.atan2(
        vector[1] * math.cos(_LAHIRI_OBLIQUITY) + vector[2] * math.sin(_LAHIRI_OBLIQUITY), vector[0]))


_LAHIRI_EQUINOX_CORRECTION_DEG = _lahiri_reference_longitude(
    erfa.pmat76(*_LAHIRI_TT) @ _LAHIRI_PRECESSION.T @ (1.0, 0.0, 0.0))


def _lahiri_mean_degrees(jd_tt: float) -> float:
    """Transport the equinox to the declared reference ecliptic, preserving its realisation."""
    epoch = float(erfa.epj(J2000_TT_JD, jd_tt - J2000_TT_JD))
    equinox = _LAHIRI_PRECESSION @ erfa.ltp(epoch).T @ (1.0, 0.0, 0.0)
    return (_LAHIRI_REFERENCE_MEAN_DEG - _lahiri_reference_longitude(equinox)
            - _LAHIRI_EQUINOX_CORRECTION_DEG) % 360.0


_CATALOG = {
    "lahiri": AyanamsaDefinition(
        key="lahiri",
        label="Lahiri / Chitra Paksha (mean)",
        model="published_lahiri_anchor",
        reference_jd_tt=LAHIRI_REFERENCE_TT_JD,
        reference_offset_deg=_LAHIRI_REFERENCE_MEAN_DEG,
        sidereal_anchor_deg=None,
        source_reference=(
            "Calendar Reform Committee report (CSIR, 1955): 23°15' at 1956-03-21; astronomical realisation "
            "of the Indian Astronomical Ephemeris 1989 p. 556 refinement, 23°15'00.658\" true at 1956-03-21 TT; "
            "IAU 1980 nutation, IAU 1976 reference equinox and Vondrak et al. 2011 precession"
        ),
        aliases=("chitra_paksha", "chitrapaksha", "lahiri_chitra_paksha"),
        reference_equinox_displacement_arcsec=_LAHIRI_EQUINOX_CORRECTION_DEG*3600.,
        precession_model="Vondrak2011; IAE1989 reference with IAU1976/Wahr1980 reduction",
        reference_frame=("IAE1956 reference ecliptic transported in the Vondrak2011 long-term mean frame; "
                         "true-mode IAU2006/2000A nutation is limited to +/-4 centuries"),
    ),
    "raman": AyanamsaDefinition(
        key="raman",
        label='Raman (Hand/NOVA modern realization)',
        model="modern_reference_ecliptic",
        reference_jd_tt=2415020.0,
        reference_offset_deg=21.01444,
        sidereal_anchor_deg=None,
        source_reference=(
            "Standard software realisation: 21.01444 deg at JD 2415020.0 and the 0.828\" Newcomb-to-modern "
            "reference-equinox offset are the widely used realisation, not derived here. Raman, Hindu Predictive "
            "Astrology, App. A (zero year 397, 50 1/3\"/yr) gives 21.01417 deg for 1900, 1\" away. "
            "The recorded reference ray is transported with Vondrak et al. (2011); this convention does not "
            "claim uniform physical accuracy across the full long-term interval."
        ),
        aliases=("bv_raman",),
        reference_equinox_displacement_arcsec=0.828,
        precession_model="Vondrak2011 long-term reference-ray transport",
        reference_frame=("Newcomb reference anchor transported in the Vondrak2011 long-term mean frame; "
                         "true-mode IAU2006/2000A nutation is limited to +/-4 centuries"),
        original_author_ambiguity='Raman states zero year389 without exact date; published original tables are not precisely reproduced by a single documented precession theory.',
    ),
    "kp": AyanamsaDefinition(
        key="kp",
        label='KP (Hand/NOVA modern realization)',
        model="modern_reference_ecliptic",
        reference_jd_tt=2415020.0,
        reference_offset_deg=22.363889,
        sidereal_anchor_deg=None,
        source_reference=(
            "Standard software realisation: 22.363889 deg (22 21 50) at JD 2415020.0 and the 0.828\" offset are "
            "the widely used realisation, not derived here. Agrees to its 1' precision with the 1900 entry "
            "(22 22) of Krishnamurti, Krishnamurti Padhdhati Vol. I. The recorded reference ray is transported "
            "with Vondrak et al. (2011), without a claim of uniform physical accuracy over the full interval."
        ),
        aliases=("krishnamurti", "kp_krishnamurti"),
        reference_equinox_displacement_arcsec=0.828,
        precession_model="Vondrak2011 long-term reference-ray transport",
        reference_frame=("Newcomb reference anchor transported in the Vondrak2011 long-term mean frame; "
                         "true-mode IAU2006/2000A nutation is limited to +/-4 centuries"),
        original_author_ambiguity='Zero year291 has no exact date; ReaderI table dates are ambiguous and values repeat in1918-1921. This realization does not assert original-table fidelity.',
    ),
    "yukteshwar": AyanamsaDefinition(
        key="yukteshwar",
        label='Yukteshwar (Cochrane/Dawson modern realization)',
        model="modern_reference_ecliptic",
        reference_jd_tt=2415020.0,
        reference_offset_deg=21.082222,
        sidereal_anchor_deg=None,
        source_reference=(
            "Standard software realisation: 21.082222 deg at JD 2415020.0 follows the widely used Dawson "
            "definition, not derived here. Sri Yukteswar, The Holy Science (1894) states 20 54 36 at the "
            "1894 spring equinox, a different anchor. The recorded reference ray is transported with Vondrak "
            "et al. (2011), without a claim of uniform physical accuracy over the full interval."
        ),
        aliases=("yukteswar", "sri_yukteswar", "sri_yukteshwar"),
        reference_equinox_displacement_arcsec=0.0,
        precession_model="Vondrak2011 long-term reference-ray transport",
        reference_frame=("modern reference anchor transported in the Vondrak2011 long-term mean frame; "
                         "true-mode IAU2006/2000A nutation is limited to +/-4 centuries"),
        original_author_ambiguity='Author states54 arcsec/year and20deg54min36sec at the spring equinox; editions differ between1893 and1894. This is not that author-stated rate model.',
    ),
    "fagan_bradley": AyanamsaDefinition(
        key="fagan_bradley",
        label='Fagan-Bradley (published1950 anchor)',
        model="modern_reference_ecliptic",
        reference_jd_tt=2433282.42346,
        reference_offset_deg=24.042044444444446,
        sidereal_anchor_deg=None,
        source_reference=(
            "Standard software realisation: SVP 335 57 28.64 (ayanamsa 24 02 31.36) at Besselian 1950.0 "
            "(ERFA epb2jd: JD 2433282.42346), as defined by Fagan and Allen; the 0.41256\" Newcomb-to-modern "
            "offset is the widely used realisation, not derived here. The recorded reference ray is transported "
            "with Vondrak et al. (2011), without a claim of uniform physical accuracy over the full interval."
        ),
        aliases=("fagan", "bradley", "fagan-bradley"),
        reference_equinox_displacement_arcsec=0.41256,
        precession_model="Vondrak2011 long-term reference-ray transport",
        reference_frame=("Newcomb reference anchor transported in the Vondrak2011 long-term mean frame; "
                         "true-mode IAU2006/2000A nutation is limited to +/-4 centuries"),
        original_author_ambiguity='Published calendar date is represented by the explicit published B1950 epoch; fully pinned here.',
    ),
    "true_citra": AyanamsaDefinition(
        key="true_citra",
        label="True Citra (Spica)",
        model="star_anchor",
        reference_jd_tt=None,
        reference_offset_deg=None,
        sidereal_anchor_deg=180.0,
        source_reference="Spica (alpha Virginis / HIP 65474) fixed at 180 degrees sidereal",
        aliases=("true_chitra", "true_chitrapaksha", "true_chitra_paksha"),
    ),
    "pushya": AyanamsaDefinition(
        key="pushya",
        label="Pushya Paksha (Delta Cancri)",
        model="star_anchor",
        reference_jd_tt=None,
        reference_offset_deg=None,
        sidereal_anchor_deg=106.0,
        source_reference=(
            "P.V.R. Narasimha Rao, Introducing Pushya-paksha Ayanamsa; "
            "Delta Cancri fixed at 106 degrees sidereal"
        ),
        aliases=("pushya_paksha", "true_pushya", "true_pushya_paksha"),
    ),
}


def _fixed_definition(key, label, jd, offset, source, *, correction=0., ambiguity=""):
    return AyanamsaDefinition(
        key, label, "modern_reference_ecliptic", jd, offset, None, source,
        reference_equinox_displacement_arcsec=correction,
        precession_model="Vondrak2011 long-term reference-ray transport",
        reference_frame=("declared reference anchor transported in the Vondrak2011 long-term mean frame; "
                         "true-mode IAU2006/2000A nutation is limited to +/-4 centuries"),
        original_author_ambiguity=ambiguity,
    )


def _historical_definition(key, label, year, seconds, offset):
    ut1 = calendar_jd(year, 3, 21, seconds / 86400., calendar=CalendarSystem.JULIAN)
    first = calendar_jd(year, 1, 1, calendar=CalendarSystem.JULIAN)
    last = calendar_jd(year+1, 1, 1, calendar=CalendarSystem.JULIAN)
    delta_t = estimate_delta_t(year+(ut1-first)/(last-first))
    return _fixed_definition(
        key, label, ut1+delta_t.seconds/86400., offset,
        "Surya-Siddhanta / Aryabhatiya: published "
        f"modern UT1 realization, Julian {year}-03-21 + {seconds} seconds; "
        f"Espenak/Meeus Delta-T policy {delta_t.model}; Ujjain/Lanka realization",
        ambiguity=("Historical operation with a documentation-derived modern realization; "
                   "the ancient author did not specify TT, Delta-T or these modern offsets. "
                   "The 522 day/time is a software realization of a year tradition."),
    )


_CATALOG.update({
    "lahiri_icrc": _fixed_definition(
        "lahiri_icrc", "Lahiri ICRC (1956 realization)", LAHIRI_REFERENCE_TT_JD,
        23.25-math.degrees(float(erfa.nut80(*_LAHIRI_TT)[0])),
        "Calendar Reform Committee (1955), 23 degrees 15 minutes true at 1956-03-21; "
        "explicit IAU1976/Wahr1980 modern reference reduction",
        correction=_LAHIRI_EQUINOX_CORRECTION_DEG*3600.),
    "lahiri_1940": _fixed_definition(
        "lahiri_1940", "Lahiri 1940 realization", 2415020., _dms(22,26,45.50),
        "Standard software realization: Lahiri's published 1940 mean reference, "
        "22 degrees 26 minutes 45.50 seconds at JD2415020.0 TT"),
    "kp_senthilathiban": _fixed_definition(
        "kp_senthilathiban", "KP Senthilathiban realization", 1827424.7572800927, 0.,
        "Standard software realization: Senthilathiban, zero at JD1827424.7572800927 TT"),
    "sassanian": _fixed_definition(
        "sassanian", "Sassanian (Mercier modern realization)", 1927135.8747793, 0.,
        "Mercier, Studies in the Medieval Conception of Precession (1976/1977); "
        "published ET JD1927135.8747793 represented as TT",
        ambiguity="A modern reference realization, not an observationally exact ancient TT instant."),
})

for _key, _label, _longitude, _model in (
    ("true_revati", "True Revati (zeta Piscium A)", 359+50/60, "star_anchor"),
    ("true_mula", "True Mula (lambda Scorpii)", 240., "star_anchor"),
    ("aldebaran", "Aldebaran at 15 Taurus", 45., "star_anchor"),
    ("galactic_center_sagittarius", "Galactic center at 0 Sagittarius", 240., "star_anchor"),
    ("galactic_center_capricorn", "Galactic center at 0 Capricorn", 270., "star_anchor"),
    ("dhruva_middle_mula", "Dhruva Middle Mula (polar longitude)", 246+40/60, "polar_anchor"),
):
    _CATALOG[_key] = AyanamsaDefinition(
        _key, _label, _model, None, None, _longitude,
        f"Published {_label} geometric definition; separately supplied date-specific "
        f"{'polar' if _model == 'polar_anchor' else 'ordinary ecliptic'} longitude required",
        precession_model="Vondrak2011 frame; supplied date-specific anchor",
        original_author_ambiguity="The convention does not certify the supplied stellar astrometry.",
    )

for _key, _label, _pole, _longitude in (
    ("galactic_equator_iau1958", "IAU1958 transformed galactic plane",
     (192.85948125, 27.12825111111111), 240.),
    ("galactic_equator_modern", "Liu/Zhu/Zhang proposed ICRS galactic plane",
     (192.902979992083, 27.103109214444), 240.),
    ("ardra_galactic_plane", "Ardra / middle Mula galactic intersection",
     (192.902979992083, 27.103109214444), 246+40/60),
):
    _CATALOG[_key] = AyanamsaDefinition(
        _key, _label, "galactic_plane", None, None, _longitude,
        "Liu, Zhu & Hu 2011 A&A536 A102; Liu, Zhu & Zhang 2011 A&A526 A16: "
        "ascending intersection of the frozen ICRS galactic plane with mean ecliptic of date",
        precession_model="Vondrak2011 long-term mean ecliptic",
        galactic_pole_icrs_deg=_pole,
        original_author_ambiguity="The proposed ICRS plane is a convention, not IAU-adopted physical truth.",
    )

for _key, _label, _year, _seconds, _offset in (
    ("suryasiddhanta_equinox", "Surya-Siddhanta equinox", 499, 27031.57, 0.),
    ("suryasiddhanta_mean_sun", "Surya-Siddhanta mean Sun", 499, 27031.57, -.21463395),
    ("aryabhata_equinox", "Aryabhata equinox", 499, 25015.57, 0.),
    ("aryabhata_mean_sun", "Aryabhata mean Sun", 499, 25015.57, -.23763238),
    ("aryabhata_522", "Aryabhata / Govindasvamin 522", 522, 20804., 0.),
    ("suryasiddhanta_revati", "Surya-Siddhanta Revati polar realization", 499, 27031.57, -.79167046),
    ("suryasiddhanta_citra", "Surya-Siddhanta Citra polar realization", 499, 27031.57, 2.11070444),
):
    _CATALOG[_key] = _historical_definition(_key, _label, _year, _seconds, _offset)

AYANAMSA_CATALOG: Mapping[str, AyanamsaDefinition] = MappingProxyType(_CATALOG)
_AYANAMSA_ALIASES = MappingProxyType(
    {
        alias: definition.key
        for definition in _CATALOG.values()
        for alias in (definition.key, *definition.aliases)
    }
)


@dataclass(frozen=True)
class HouseAngles:
    """IAU sidereal angles and the resulting tropical Ascendant and MC."""

    earth_rotation_angle_deg: float
    gmst_deg: float
    gast_deg: float
    local_apparent_sidereal_deg: float
    true_obliquity_deg: float
    ascendant_deg: float
    midheaven_deg: float


@dataclass(frozen=True)
class HouseLayout:
    """Twelve ordered house starts, centres, and boundaries in degrees."""

    system: str
    cusps_deg: tuple[float, ...]
    centers_deg: tuple[float, ...]
    boundaries_deg: tuple[float, ...]
    ascendant_deg: float
    midheaven_deg: float
    version: str = HOUSE_CONVENTIONS_VERSION


def normalize_degrees(value: float) -> float:
    """Normalize a finite angle to the half-open interval [0, 360)."""

    if not math.isfinite(value):
        raise AstronomyDataUnavailable("angle must be finite")
    normalized = value % 360.0
    return 0.0 if normalized == 360.0 else normalized


def _canonical_ayanamsa(convention: str) -> AyanamsaDefinition:
    key = str(convention or "").strip().lower().replace(" ", "_")
    canonical = _AYANAMSA_ALIASES.get(key)
    if canonical is None:
        raise AstronomyDataUnavailable(f"unsupported ayanamsa convention: {convention!r}")
    return AYANAMSA_CATALOG[canonical]


def _validate_tt_jd(jd_tt: float) -> None:
    if not math.isfinite(jd_tt):
        raise AstronomyDataUnavailable("TT Julian date must be finite")
    centuries = abs((jd_tt - J2000_TT_JD) / JULIAN_CENTURY_DAYS)
    if centuries > AYANAMSA_VALID_CENTURIES:
        raise AstronomyDataUnavailable(
            "ayanamsa policy is versioned only for TT dates from 1600 through 2400"
        )


def _split_j2000(jd: float) -> tuple[float, float]:
    return J2000_TT_JD, jd - J2000_TT_JD


def validate_tt_tdb(jd_tt: float, jd_tdb: float) -> None:
    """Reject unrelated TT/TDB epochs with a deliberately loose guard.

    The one-second ceiling is deliberately above the physical millisecond-scale
    separation described in JPL's Horizons time-scale documentation. It catches
    wrong-date/scale inputs, not subsecond timing errors, and is not an accuracy
    certificate: https://ssd.jpl.nasa.gov/horizons/manual.html#time
    """

    if not math.isfinite(jd_tt) or not math.isfinite(jd_tdb):
        raise AstronomyDataUnavailable("TT and TDB Julian dates must be finite")
    if abs(jd_tdb - jd_tt) > TT_TDB_MAX_ABS_DAYS:
        raise AstronomyDataUnavailable(
            "TT and TDB Julian dates must identify the same epoch within one second"
        )


def _validate_long_term_tt(jd_tt: float) -> None:
    if not math.isfinite(jd_tt):
        raise AstronomyDataUnavailable("TT Julian date must be finite")
    if not AYANAMSA_MIN_TT_JD <= jd_tt <= AYANAMSA_MAX_TT_JD:
        raise AstronomyDataUnavailable("TT Julian date is outside the declared DE441 convention interval")


def mean_ecliptic_matrix(jd_tt: float):
    """ICRS to mean ecliptic of date, retaining the established modern frame."""
    _validate_long_term_tt(jd_tt)
    if abs((jd_tt-J2000_TT_JD)/JULIAN_CENTURY_DAYS) <= AYANAMSA_VALID_CENTURIES:
        return erfa.ecm06(*_split_j2000(jd_tt))
    return erfa.ltecm(2000.+(jd_tt-J2000_TT_JD)/365.25)


def general_precession_longitude_degrees(jd_tt: float) -> float:
    """Return IAU 2006 general precession in longitude ``p_A`` from J2000."""

    _validate_tt_jd(jd_tt)
    return math.degrees(float(erfa.p06e(*_split_j2000(jd_tt))[12]))


def _modern_reference_ecliptic_ayanamsa(jd_tt, definition):
    if jd_tt == definition.reference_jd_tt:
        return normalize_degrees(definition.reference_offset_deg
                                 - definition.reference_equinox_displacement_arcsec/3600)
    ref_epoch = 2000.+(definition.reference_jd_tt-J2000_TT_JD)/365.25
    date_epoch = 2000.+(jd_tt-J2000_TT_JD)/365.25
    vector = erfa.ltp(ref_epoch) @ erfa.ltp(date_epoch)[0]
    eps = math.acos(float(erfa.pdp(erfa.ltpequ(ref_epoch), erfa.ltpecl(ref_epoch))))
    longitude = math.degrees(math.atan2(vector[1]*math.cos(eps)+vector[2]*math.sin(eps),vector[0]))
    return normalize_degrees(definition.reference_offset_deg
        - definition.reference_equinox_displacement_arcsec/3600 - longitude)


def ayanamsa_degrees(
    jd_tt: float,
    convention: str,
    *,
    anchor_tropical_longitude_deg: float | None = None,
    true: bool = False,
) -> float:
    """Evaluate one versioned ayanamsa policy at a TT Julian date.

    A date-specific tropical stellar longitude is mandatory for ``true_citra``
    and ``pushya``. It must come from a separately versioned stellar apparent-
    place calculation at the same instant; this function will not invent one.
    """

    _validate_long_term_tt(jd_tt)
    if true:
        _validate_tt_jd(jd_tt)
    definition = _canonical_ayanamsa(convention)
    if definition.model in {"star_anchor", "polar_anchor"}:
        if anchor_tropical_longitude_deg is None:
            raise AstronomyDataUnavailable(
                f"{definition.key} requires a tropical anchor-star longitude"
                + (" measured as polar longitude" if definition.model == "polar_anchor" else "")
            )
        assert definition.sidereal_anchor_deg is not None
        return normalize_degrees(
            normalize_degrees(anchor_tropical_longitude_deg) - definition.sidereal_anchor_deg
            + (math.degrees(float(erfa.nut06a(*_split_j2000(jd_tt))[0])) if true else 0.0)
        )

    if definition.model == "galactic_plane":
        assert definition.galactic_pole_icrs_deg is not None
        ra, dec = map(math.radians, definition.galactic_pole_icrs_deg)
        pole = (math.cos(ra)*math.cos(dec), math.sin(ra)*math.cos(dec), math.sin(dec))
        matrix = erfa.ltecm(2000.+(jd_tt-J2000_TT_JD)/365.25)
        intersection = erfa.pxp(pole, matrix[2])
        if float(erfa.pm(intersection)) <= 1e-15:
            raise AstronomyDataUnavailable("galactic and ecliptic planes have no unique intersection")
        vector = matrix @ intersection
        mean = math.degrees(math.atan2(float(vector[1]), float(vector[0])))
        return normalize_degrees(mean-definition.sidereal_anchor_deg
                                 + (math.degrees(float(erfa.nut06a(*_split_j2000(jd_tt))[0])) if true else 0.))

    if definition.model == "modern_reference_ecliptic":
        mean = _modern_reference_ecliptic_ayanamsa(jd_tt, definition)
        return normalize_degrees(mean + (math.degrees(float(erfa.nut06a(*_split_j2000(jd_tt))[0])) if true else 0.0))
    if definition.model == "published_lahiri_anchor":
        mean = _lahiri_mean_degrees(jd_tt)
        return normalize_degrees(mean + (math.degrees(float(erfa.nut06a(*_split_j2000(jd_tt))[0])) if true else 0.0))
    if definition.model != "mean_precession_anchor":
        raise AstronomyDataUnavailable(f"unsupported ayanamsa model: {definition.model}")
    assert definition.reference_jd_tt is not None
    assert definition.reference_offset_deg is not None
    precession_delta = general_precession_longitude_degrees(
        jd_tt
    ) - general_precession_longitude_degrees(definition.reference_jd_tt)
    return normalize_degrees(definition.reference_offset_deg + precession_delta
                             + (math.degrees(float(erfa.nut06a(*_split_j2000(jd_tt))[0])) if true else 0.0))


def tropical_to_sidereal(
    tropical_longitude_deg: float,
    jd_tt: float,
    convention: str,
    *,
    anchor_tropical_longitude_deg: float | None = None,
) -> float:
    """Convert a tropical ecliptic longitude using an explicit ayanamsa."""

    return normalize_degrees(
        normalize_degrees(tropical_longitude_deg)
        - ayanamsa_degrees(
            jd_tt,
            convention,
            anchor_tropical_longitude_deg=anchor_tropical_longitude_deg,
        )
    )


def mean_lunar_node_longitude_degrees(jd_tt: float) -> float:
    """Mean ascending lunar-node longitude in the mean ecliptic of date.

    Meeus, Astronomical Algorithms, second edition, eq. 47.7 in TT.
    This mean node is not the osculating node.
    The same bounded 1600-2400 policy is applied because no extrapolated node
    is accepted silently by the dark provider.
    """

    _validate_tt_jd(jd_tt)
    t = (jd_tt - J2000_TT_JD) / JULIAN_CENTURY_DAYS
    longitude = (
        125.0445479 - 1934.1362891 * t + 0.0020754 * t**2 + t**3 / 467441.0 - t**4 / 60616000.0
    )
    return normalize_degrees(longitude)


def osculating_lunar_node_longitude_degrees(
    moon_position: Sequence[float],
    moon_velocity: Sequence[float],
) -> float:
    """Return the ascending osculating node from a Moon state vector.

    Both vectors must use the same geocentric ecliptic frame and time unit.
    The node vector is ``k x (r x v)``. Equatorial or mixed-frame inputs are a
    caller error and cannot be detected from three numbers alone.
    """

    if len(moon_position) != 3 or len(moon_velocity) != 3:
        raise AstronomyDataUnavailable("Moon position and velocity must each contain 3 values")
    values = tuple(float(value) for value in (*moon_position, *moon_velocity))
    if not all(math.isfinite(value) for value in values):
        raise AstronomyDataUnavailable("Moon state vector must be finite")
    rx, ry, rz, vx, vy, vz = values
    hx = ry * vz - rz * vy
    hy = rz * vx - rx * vz
    hz = rx * vy - ry * vx
    angular_momentum = math.sqrt(hx * hx + hy * hy + hz * hz)
    node_norm = math.hypot(hx, hy)
    scale = math.sqrt(rx * rx + ry * ry + rz * rz) * math.sqrt(vx * vx + vy * vy + vz * vz)
    if scale == 0.0 or angular_momentum <= scale * 1e-15 or node_norm <= scale * 1e-15:
        raise AstronomyDataUnavailable("osculating lunar node is singular or undefined")
    return normalize_degrees(math.degrees(math.atan2(hx, -hy)))


def ascendant_midheaven_from_sidereal(
    local_apparent_sidereal_deg: float,
    latitude_deg: float,
    true_obliquity_deg: float,
) -> tuple[float, float]:
    """Derive tropical Ascendant and MC from local apparent sidereal time.

    The Ascendant is selected as the eastern of the two intersections between
    the ecliptic and horizon. The MC is the ecliptic point on the upper local
    meridian. Geographic poles are rejected because local east is undefined.
    """

    theta = math.radians(normalize_degrees(local_apparent_sidereal_deg))
    if not math.isfinite(latitude_deg) or not -90.0 < latitude_deg < 90.0:
        raise AstronomyDataUnavailable("house angles are undefined at the geographic poles")
    if not math.isfinite(true_obliquity_deg) or not 0.0 < true_obliquity_deg < 90.0:
        raise AstronomyDataUnavailable("true obliquity must be between 0 and 90 degrees")
    phi = math.radians(latitude_deg)
    epsilon = math.radians(true_obliquity_deg)

    horizon_a = math.cos(phi) * math.cos(theta)
    horizon_b = math.cos(phi) * math.cos(epsilon) * math.sin(theta) + math.sin(phi) * math.sin(
        epsilon
    )
    if math.hypot(horizon_a, horizon_b) <= 1e-15:
        raise AstronomyDataUnavailable("ecliptic-horizon intersection is singular")
    ascendant = math.atan2(-horizon_a, horizon_b)
    east_projection = -math.cos(ascendant) * math.sin(theta) + math.sin(ascendant) * math.cos(
        epsilon
    ) * math.cos(theta)
    if abs(east_projection) <= 1e-15:
        raise AstronomyDataUnavailable("rising ecliptic intersection is indeterminate")
    if east_projection < 0.0:
        ascendant += math.pi

    midheaven = math.atan2(math.sin(theta), math.cos(theta) * math.cos(epsilon))
    return normalize_degrees(math.degrees(ascendant)), normalize_degrees(math.degrees(midheaven))


def house_angles(
    *,
    tt_jd: float,
    ut1_jd: float,
    longitude_deg: float,
    latitude_deg: float,
) -> HouseAngles:
    """Compute IAU 2006 sidereal quantities and tropical Ascendant/MC.

    Longitude is positive east. The caller must supply provenance-bearing TT
    and UT1 values; UTC or guessed DUT1 values are not accepted by this API.
    """

    if not math.isfinite(tt_jd) or not math.isfinite(ut1_jd):
        raise AstronomyDataUnavailable("TT and UT1 Julian dates must be finite")
    if not math.isfinite(longitude_deg) or not -180.0 <= longitude_deg <= 180.0:
        raise AstronomyDataUnavailable("longitude must be within [-180, 180] degrees")
    tt = _split_j2000(tt_jd)
    ut1 = _split_j2000(ut1_jd)
    era = float(erfa.era00(*ut1))
    gmst = float(erfa.gmst06(*ut1, *tt))
    gast = float(erfa.gst06a(*ut1, *tt))
    _dpsi, deps = erfa.nut06a(*tt)
    true_obliquity = float(erfa.obl06(*tt) + deps)
    local_apparent = gast + math.radians(longitude_deg)
    ascendant, midheaven = ascendant_midheaven_from_sidereal(
        math.degrees(local_apparent), latitude_deg, math.degrees(true_obliquity)
    )
    return HouseAngles(
        earth_rotation_angle_deg=normalize_degrees(math.degrees(era)),
        gmst_deg=normalize_degrees(math.degrees(gmst)),
        gast_deg=normalize_degrees(math.degrees(gast)),
        local_apparent_sidereal_deg=normalize_degrees(math.degrees(local_apparent)),
        true_obliquity_deg=math.degrees(true_obliquity),
        ascendant_deg=ascendant,
        midheaven_deg=midheaven,
    )


def _forward_arc(start_deg: float, end_deg: float) -> float:
    return normalize_degrees(end_deg - start_deg)


def _midpoint_forward(start_deg: float, end_deg: float) -> float:
    return normalize_degrees(start_deg + _forward_arc(start_deg, end_deg) / 2.0)


def _porphyry_division_points(ascendant_deg: float, midheaven_deg: float) -> tuple[float, ...]:
    asc = normalize_degrees(ascendant_deg)
    mc = normalize_degrees(midheaven_deg)
    angles = (asc, normalize_degrees(mc + 180.0), normalize_degrees(asc + 180.0), mc)
    points: list[float] = []
    for start, end in zip(angles, (*angles[1:], angles[0]), strict=True):
        arc = _forward_arc(start, end)
        if arc <= 1e-12 or arc >= 180.0 - 1e-12:
            raise AstronomyDataUnavailable("Porphyry quadrant is singular or non-physical")
        points.extend(normalize_degrees(start + arc * fraction / 3.0) for fraction in range(3))
    return tuple(points)


def _ecliptic_longitude_from_right_ascension(
    right_ascension: float, obliquity: float
) -> float:
    return math.atan2(math.sin(right_ascension) / math.cos(obliquity), math.cos(right_ascension))


def _placidus_cusp(
    *,
    local_sidereal: float,
    latitude: float,
    obliquity: float,
    phase: str,
    fraction: float,
    initial_longitude: float,
) -> float:
    """Solve one Placidus intermediate cusp by semiarc iteration."""

    longitude = initial_longitude
    for _iteration in range(100):
        declination = math.asin(math.sin(obliquity) * math.sin(longitude))
        circumpolar = -math.tan(latitude) * math.tan(declination)
        if not -1.0 < circumpolar < 1.0:
            raise AstronomyDataUnavailable(
                "Placidus cusp is undefined for this circumpolar geometry"
            )
        semidiurnal = math.acos(circumpolar)
        seminocturnal = math.pi - semidiurnal
        if phase == "upper":
            hour_angle = -fraction * semidiurnal
        elif phase == "lower":
            hour_angle = -semidiurnal - fraction * seminocturnal
        else:  # pragma: no cover - internal contract
            raise AssertionError(phase)
        target_ra = local_sidereal - hour_angle
        candidate = _ecliptic_longitude_from_right_ascension(target_ra, obliquity)
        candidate += 2.0 * math.pi * round((longitude - candidate) / (2.0 * math.pi))
        if abs(candidate - longitude) <= 5e-14:
            return normalize_degrees(math.degrees(candidate))
        longitude = candidate
    raise AstronomyDataUnavailable("Placidus semiarc iteration did not converge")


def _placidus_cusps(
    *,
    ascendant_deg: float,
    midheaven_deg: float,
    local_apparent_sidereal_deg: float,
    latitude_deg: float,
    true_obliquity_deg: float,
) -> tuple[float, ...]:
    if not -90.0 < latitude_deg < 90.0:
        raise AstronomyDataUnavailable("Placidus houses are undefined at the poles")
    local_sidereal = math.radians(local_apparent_sidereal_deg)
    latitude = math.radians(latitude_deg)
    obliquity = math.radians(true_obliquity_deg)
    seeds = _porphyry_division_points(ascendant_deg, midheaven_deg)
    cusp_11 = _placidus_cusp(
        local_sidereal=local_sidereal,
        latitude=latitude,
        obliquity=obliquity,
        phase="upper",
        fraction=1.0 / 3.0,
        initial_longitude=math.radians(seeds[10]),
    )
    cusp_12 = _placidus_cusp(
        local_sidereal=local_sidereal,
        latitude=latitude,
        obliquity=obliquity,
        phase="upper",
        fraction=2.0 / 3.0,
        initial_longitude=math.radians(seeds[11]),
    )
    cusp_2 = _placidus_cusp(
        local_sidereal=local_sidereal,
        latitude=latitude,
        obliquity=obliquity,
        phase="lower",
        fraction=1.0 / 3.0,
        initial_longitude=math.radians(seeds[1]),
    )
    cusp_3 = _placidus_cusp(
        local_sidereal=local_sidereal,
        latitude=latitude,
        obliquity=obliquity,
        phase="lower",
        fraction=2.0 / 3.0,
        initial_longitude=math.radians(seeds[2]),
    )
    asc = normalize_degrees(ascendant_deg)
    mc = normalize_degrees(midheaven_deg)
    return (
        asc,
        cusp_2,
        cusp_3,
        normalize_degrees(mc + 180.0),
        normalize_degrees(cusp_11 + 180.0),
        normalize_degrees(cusp_12 + 180.0),
        normalize_degrees(asc + 180.0),
        normalize_degrees(cusp_2 + 180.0),
        normalize_degrees(cusp_3 + 180.0),
        mc,
        cusp_11,
        cusp_12,
    )


def _great_circle_house_cusps(system, armc_deg, latitude_deg, obliquity_deg):
    """Intersect ecliptic with N/S-horizon great circles.

    Definitions after Houlding, The Houses: Temples of the Sky (2006), ch. 8;
    further reading Holden, The Elements of House Division (1977).

    Regiomontanus divides the equator; Campanus divides the prime vertical.
    The construction is independent vector geometry, not vendor source code.
    """
    theta, phi, eps = map(math.radians, (armc_deg, latitude_deg, obliquity_deg))
    north = (-math.sin(phi)*math.cos(theta), -math.sin(phi)*math.sin(theta), math.cos(phi))
    up = (math.cos(phi)*math.cos(theta), math.cos(phi)*math.sin(theta), math.sin(phi))
    east = (-math.sin(theta), math.cos(theta), 0.)
    cusps = []
    for house in range(1, 13):
        arc = math.radians((house-10)*30)
        if system == "regiomontanus":
            point = (math.cos(theta+arc), math.sin(theta+arc), 0.)
        else:
            point = tuple(up[i]*math.cos(arc)+east[i]*math.sin(arc) for i in range(3))
        normal = (north[1]*point[2]-north[2]*point[1],
                  north[2]*point[0]-north[0]*point[2],
                  north[0]*point[1]-north[1]*point[0])
        lam = math.atan2(-normal[0], normal[1]*math.cos(eps)+normal[2]*math.sin(eps))
        ecliptic = (math.cos(lam), math.sin(lam)*math.cos(eps), math.sin(lam)*math.sin(eps))
        if sum(ecliptic[i]*point[i] for i in range(3)) < 0:
            lam += math.pi
        cusps.append(normalize_degrees(math.degrees(lam)))
    return tuple(cusps)


def _koch_cusps(asc, mc, armc, latitude, obliquity):
    """Horizon at thirds of the MC degree's semi-arc (Koch birthplace system).

    Definition after Houlding, The Houses: Temples of the Sky (2006), ch. 8, and
    Koch & Knappich, Horoskop und Himmelshauser (1959).
    """
    declination = math.asin(math.sin(math.radians(obliquity))*math.sin(math.radians(mc)))
    argument = -math.tan(math.radians(latitude))*math.tan(declination)
    if abs(argument) >= 1:
        raise AstronomyDataUnavailable("Koch undefined for a circumpolar MC")
    semi_arc = math.degrees(math.acos(argument))
    horizon = lambda rotation: ascendant_midheaven_from_sidereal(rotation, latitude, obliquity)[0]
    c2, c3 = horizon(armc+semi_arc/3), horizon(armc+2*semi_arc/3)
    c11, c12 = horizon(armc-2*semi_arc/3), horizon(armc-semi_arc/3)
    return tuple(map(normalize_degrees, (asc, c2, c3, mc+180, c11+180, c12+180,
                                        asc+180, c2+180, c3+180, mc, c11, c12)))


def house_layout(
    system: str,
    *,
    ascendant_deg: float,
    midheaven_deg: float,
    local_apparent_sidereal_deg: float | None = None,
    latitude_deg: float | None = None,
    true_obliquity_deg: float | None = None,
) -> HouseLayout:
    """Build supported house geometry under one explicit convention version.

    For Porphyry, ``cusps_deg`` and ``boundaries_deg`` are the trisected
    quadrant starts. For Sripati, those points are ``centers_deg`` and the
    house boundaries are halfway between adjacent centres.
    """

    normalized_system = str(system or "").strip().lower().replace("-", "_")
    asc = normalize_degrees(ascendant_deg)
    mc = normalize_degrees(midheaven_deg)
    if normalized_system in {"whole_sign", "whole", "w"}:
        first = math.floor(asc / 30.0) * 30.0
        cusps = tuple(normalize_degrees(first + 30.0 * index) for index in range(12))
        centers = tuple(normalize_degrees(cusp + 15.0) for cusp in cusps)
        return HouseLayout("whole_sign", cusps, centers, cusps, asc, mc)
    if normalized_system in {"equal", "equal_house", "e"}:
        cusps = tuple(normalize_degrees(asc + 30.0 * index) for index in range(12))
        centers = tuple(normalize_degrees(cusp + 15.0) for cusp in cusps)
        return HouseLayout("equal", cusps, centers, cusps, asc, mc)
    if normalized_system in {"koch", "campanus", "regiomontanus"}:
        if local_apparent_sidereal_deg is None or latitude_deg is None or true_obliquity_deg is None:
            raise AstronomyDataUnavailable("House geometry requires ARMC, latitude and true obliquity")
        if not -90 < latitude_deg < 90 or not 0 < true_obliquity_deg < 90:
            raise AstronomyDataUnavailable("House geometry inputs outside supported range")
        if normalized_system == "koch":
            cusps = _koch_cusps(asc, mc, local_apparent_sidereal_deg, latitude_deg, true_obliquity_deg)
        else:
            cusps = _great_circle_house_cusps(normalized_system, local_apparent_sidereal_deg, latitude_deg, true_obliquity_deg)
        centers = tuple(_midpoint_forward(cusp, cusps[(index+1)%12]) for index,cusp in enumerate(cusps))
        return HouseLayout(normalized_system, cusps, centers, cusps, asc, mc)
    if normalized_system in {"placidus", "p"}:
        if (
            local_apparent_sidereal_deg is None
            or latitude_deg is None
            or true_obliquity_deg is None
        ):
            raise AstronomyDataUnavailable(
                "Placidus requires local sidereal time, latitude, and true obliquity"
            )
        cusps = _placidus_cusps(
            ascendant_deg=asc,
            midheaven_deg=mc,
            local_apparent_sidereal_deg=local_apparent_sidereal_deg,
            latitude_deg=latitude_deg,
            true_obliquity_deg=true_obliquity_deg,
        )
        centers = tuple(
            _midpoint_forward(cusp, cusps[(index + 1) % 12])
            for index, cusp in enumerate(cusps)
        )
        return HouseLayout("placidus", cusps, centers, cusps, asc, mc)
    if normalized_system not in {"porphyry", "sripati"}:
        raise AstronomyDataUnavailable(f"unsupported house system: {system!r}")

    division_points = _porphyry_division_points(asc, mc)
    if normalized_system == "porphyry":
        centers = tuple(
            _midpoint_forward(cusp, division_points[(index + 1) % 12])
            for index, cusp in enumerate(division_points)
        )
        return HouseLayout("porphyry", division_points, centers, division_points, asc, mc)

    boundaries = tuple(
        _midpoint_forward(division_points[(index - 1) % 12], center)
        for index, center in enumerate(division_points)
    )
    return HouseLayout("sripati", boundaries, division_points, boundaries, asc, mc)
