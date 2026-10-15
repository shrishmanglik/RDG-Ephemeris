"""Tajika Varshphal (Annual Solar Return Horoscopy) engine.

Implements high-precision Solar Return (Varsha Pravesha) epoch determination via
secant-Newton root finding, annual Muntha progression, Pancha-Vargiya Bala (fivefold
strength in Virupas and Vishwas), Harsha Bala (fourfold joy strength), Panchadhikari
and Varsheshwara (Lord of the Year) selection, the 16 classical Tajika Yogas (Ithasala,
Ishrafa, Nakta, Yamaya, Kamboola, Radda, etc.), annual Mudda Dasha, and 24+ Tajika
Sahams (Arabic/Tajika lots), following *Tajika Neelakanthi* (Acharya Neelakantha) and
*Varshaphala* classical canons.
"""

from __future__ import annotations

from dataclasses import dataclass
import math
from typing import Callable, Mapping, Sequence

import erfa

from ..engine.conventions import ayanamsa_degrees
from ..engine.receipt import canonical_hash
from .kp import NAKSHATRA_NAMES, RASI_LORDS, RASI_NAMES, VIMSHOTTARI_LORDS, VIMSHOTTARI_YEARS

SEVEN_PLANETS: tuple[str, ...] = (
    "sun",
    "moon",
    "mars",
    "mercury",
    "jupiter",
    "venus",
    "saturn",
)

# Classical Tajika Deeptamsa (orb of light in degrees) per Tajika Neelakanthi.
TAJIKA_PLANET_ORBS_DEG: Mapping[str, float] = {
    "sun": 15.0,
    "moon": 12.0,
    "mars": 8.0,
    "mercury": 7.0,
    "jupiter": 9.0,
    "venus": 7.0,
    "saturn": 9.0,
}

# Mean daily motion order from fastest to slowest (for Ithasala/Ishrafa/Nakta).
TAJIKA_SPEED_RANK: Mapping[str, int] = {
    "moon": 1,
    "mercury": 2,
    "venus": 3,
    "sun": 4,
    "mars": 5,
    "jupiter": 6,
    "saturn": 7,
}

# Deep exaltation longitudes (sidereal degrees 0..360) per BPHS / Tajika Neelakanthi.
DEEP_EXALTATION_DEG: Mapping[str, float] = {
    "sun": 10.0,       # 10 deg Mesha
    "moon": 33.0,      # 3 deg Vrishabha
    "mars": 298.0,     # 28 deg Makara
    "mercury": 165.0,  # 15 deg Kanya
    "jupiter": 95.0,   # 5 deg Karka
    "venus": 357.0,    # 27 deg Meena
    "saturn": 200.0,   # 20 deg Tula
}

EXALTATION_SIGN: Mapping[str, int] = {
    "sun": 0,
    "moon": 1,
    "mars": 9,
    "mercury": 5,
    "jupiter": 3,
    "venus": 11,
    "saturn": 6,
}

DEBILITATION_SIGN: Mapping[str, int] = {
    "sun": 6,
    "moon": 7,
    "mars": 3,
    "mercury": 11,
    "jupiter": 9,
    "venus": 5,
    "saturn": 0,
}

OWN_SIGNS: Mapping[str, tuple[int, ...]] = {
    "sun": (4,),
    "moon": (3,),
    "mars": (0, 7),
    "mercury": (2, 5),
    "jupiter": (8, 11),
    "venus": (1, 6),
    "saturn": (9, 10),
}

# Naisargika (natural) relationships in Tajika Neelakanthi.
NAISARGIKA_FRIENDS: Mapping[str, frozenset[str]] = {
    "sun": frozenset({"moon", "mars", "jupiter"}),
    "moon": frozenset({"sun", "mercury"}),
    "mars": frozenset({"sun", "moon", "jupiter"}),
    "mercury": frozenset({"sun", "venus"}),
    "jupiter": frozenset({"sun", "moon", "mars"}),
    "venus": frozenset({"mercury", "saturn"}),
    "saturn": frozenset({"mercury", "venus"}),
}

NAISARGIKA_ENEMIES: Mapping[str, frozenset[str]] = {
    "sun": frozenset({"venus", "saturn"}),
    "moon": frozenset(),
    "mars": frozenset({"mercury"}),
    "mercury": frozenset({"moon"}),
    "jupiter": frozenset({"mercury", "venus"}),
    "venus": frozenset({"sun", "moon"}),
    "saturn": frozenset({"sun", "moon", "mars"}),
}

# Classical Tajika Hadda (Egyptian unequal bounds) per sign: tuple of (end_deg_in_sign, lord).
TAJIKA_HADDA_TABLE: tuple[tuple[tuple[float, str], ...], ...] = (
    # 0 Mesha (Aries): Jup 6, Ven 6, Mer 8, Mar 5, Sat 5
    ((6.0, "jupiter"), (12.0, "venus"), (20.0, "mercury"), (25.0, "mars"), (30.0, "saturn")),
    # 1 Vrishabha (Taurus): Ven 8, Mer 6, Jup 8, Sat 5, Mar 3
    ((8.0, "venus"), (14.0, "mercury"), (22.0, "jupiter"), (27.0, "saturn"), (30.0, "mars")),
    # 2 Mithuna (Gemini): Mer 6, Jup 6, Ven 5, Mar 7, Sat 6
    ((6.0, "mercury"), (12.0, "jupiter"), (17.0, "venus"), (24.0, "mars"), (30.0, "saturn")),
    # 3 Karka (Cancer): Mar 7, Ven 6, Mer 6, Jup 7, Sat 4
    ((7.0, "mars"), (13.0, "venus"), (19.0, "mercury"), (26.0, "jupiter"), (30.0, "saturn")),
    # 4 Simha (Leo): Jup 6, Ven 5, Sat 7, Mer 6, Mar 6
    ((6.0, "jupiter"), (11.0, "venus"), (18.0, "saturn"), (24.0, "mercury"), (30.0, "mars")),
    # 5 Kanya (Virgo): Mer 7, Ven 10, Jup 4, Mar 7, Sat 2
    ((7.0, "mercury"), (17.0, "venus"), (21.0, "jupiter"), (28.0, "mars"), (30.0, "saturn")),
    # 6 Tula (Libra): Sat 6, Mer 8, Jup 7, Ven 7, Mar 2
    ((6.0, "saturn"), (14.0, "mercury"), (21.0, "jupiter"), (28.0, "venus"), (30.0, "mars")),
    # 7 Vrischika (Scorpio): Mar 7, Ven 4, Mer 8, Jup 5, Sat 6
    ((7.0, "mars"), (11.0, "venus"), (19.0, "mercury"), (24.0, "jupiter"), (30.0, "saturn")),
    # 8 Dhanus (Sagittarius): Jup 12, Ven 5, Mer 4, Sat 5, Mar 4
    ((12.0, "jupiter"), (17.0, "venus"), (21.0, "mercury"), (26.0, "saturn"), (30.0, "mars")),
    # 9 Makara (Capricorn): Mer 7, Jup 7, Ven 8, Sat 4, Mar 4
    ((7.0, "mercury"), (14.0, "jupiter"), (22.0, "venus"), (26.0, "saturn"), (30.0, "mars")),
    # 10 Kumbha (Aquarius): Mer 7, Ven 6, Jup 7, Mar 5, Sat 5
    ((7.0, "mercury"), (13.0, "venus"), (20.0, "jupiter"), (25.0, "mars"), (30.0, "saturn")),
    # 11 Meena (Pisces): Ven 12, Jup 4, Mer 3, Mar 9, Sat 2
    ((12.0, "venus"), (16.0, "jupiter"), (19.0, "mercury"), (28.0, "mars"), (30.0, "saturn")),
)

# Tri-Rashi Pati (Day, Night) per Varsha Lagna sign index 0..11 in Tajika Neelakanthi.
TRI_RASHI_PATI_TABLE: tuple[tuple[str, str], ...] = (
    ("sun", "jupiter"),     # 0 Mesha
    ("venus", "moon"),      # 1 Vrishabha
    ("saturn", "mercury"),  # 2 Mithuna
    ("venus", "mars"),      # 3 Karka
    ("jupiter", "sun"),     # 4 Simha
    ("moon", "venus"),      # 5 Kanya
    ("mercury", "saturn"),  # 6 Tula
    ("mars", "venus"),      # 7 Vrischika
    ("saturn", "saturn"),   # 8 Dhanus
    ("mars", "mars"),       # 9 Makara
    ("jupiter", "jupiter"), # 10 Kumbha
    ("moon", "moon"),       # 11 Meena
)

# Harsha Sthana (special house of joy for each planet, 1..12).
HARSHA_STHANA_HOUSE: Mapping[str, int] = {
    "sun": 9,
    "moon": 3,
    "mars": 6,
    "mercury": 1,
    "jupiter": 11,
    "venus": 5,
    "saturn": 12,
}

SIDEREAL_YEAR_DAYS = 365.256363004
TROPICAL_SOLAR_YEAR_DAYS = 365.2425


@dataclass(frozen=True)
class SolarReturnEpoch:
    """Solved Varsha Pravesha (Solar Return) epoch and convergence metrics."""

    jd_tt: float
    natal_sun_sidereal_lon_deg: float
    achieved_sun_sidereal_lon_deg: float
    residual_deg: float
    iterations: int
    receipt_sha256: str


@dataclass(frozen=True)
class MunthaReport:
    """Annual progressed Muntha sign, house placement, and lordship."""

    natal_asc_sign: int
    birth_year: int
    target_year: int
    elapsed_years: int
    muntha_sign: int
    muntha_rasi_name: str
    muntha_longitude_deg: float
    muntha_lord: str
    varsha_asc_sign: int
    house_from_varsha_lagna: int
    is_auspicious_house: bool
    receipt_sha256: str


@dataclass(frozen=True)
class PanchaVargiyaPlanetBala:
    """Fivefold Tajika strength (Virupas and Vishwas) for one planet."""

    planet: str
    longitude_deg: float
    kshetra_bala: float
    uchcha_bala: float
    hadda_bala: float
    drekkana_bala: float
    navamsa_bala: float
    total_virupas: float
    vishwa_bala: float
    strength_tier: str
    hadda_lord: str
    drekkana_lord: str
    navamsa_lord: str


@dataclass(frozen=True)
class HarshaPlanetBala:
    """Fourfold Harsha Bala (0..20 points) for one planet."""

    planet: str
    house_from_lagna: int
    sthana_points: int
    uchcha_swakshetra_points: int
    stri_purusha_points: int
    dina_ratri_points: int
    total_points: int


@dataclass(frozen=True)
class VarsheshwaraReport:
    """Fivefold office holders (Panchadhikari) and selected Lord of the Year."""

    muntha_lord: str
    janma_lagna_lord: str
    varsha_lagna_lord: str
    tri_rashi_pati: str
    din_ratri_pati: str
    panchadhikari_candidates: tuple[str, ...]
    varsheshwara: str
    varsheshwara_vishwa_bala: float
    aspects_varsha_lagna: bool
    receipt_sha256: str


@dataclass(frozen=True)
class TajikaYogaFinding:
    """One evaluated classical Tajika Yoga in the annual solar return chart."""

    code: str
    name: str
    active: bool
    subtype: str | None
    involved_planets: tuple[str, ...]
    orb_limit_deg: float | None
    actual_separation_deg: float | None
    summary: str


@dataclass(frozen=True)
class MuddaDashaPeriod:
    """One Mahadasha or Antardasha period in the 1-year compressed Mudda Dasha."""

    lord: str
    start_jd: float
    end_jd: float
    duration_days: float
    antardashas: tuple[ tuple[str, float, float], ... ] = ()


@dataclass(frozen=True)
class TajikaSahamEntry:
    """One computed Tajika Saham (Arabic/Tajika sensitive point)."""

    name: str
    sanskrit_name: str
    signification: str
    longitude_deg: float
    rasi_index: int
    rasi_name: str
    degree_in_rasi: float
    lord: str
    formula_used: str


def _norm360(angle_deg: float) -> float:
    val = float(angle_deg)
    if not math.isfinite(val):
        raise ValueError("angle_deg must be finite")
    return val % 360.0


def _signed_diff_deg(angle_a: float, angle_b: float) -> float:
    """Return shortest signed angular difference ``(angle_a - angle_b)`` in ``[-180, 180)``."""

    return ((float(angle_a) - float(angle_b) + 180.0) % 360.0) - 180.0


def _default_sidereal_sun_lon(jd_tt: float) -> float:
    """Analytical geocentric sidereal solar longitude (Lahiri) via ERFA ``epv00``."""

    pvh, _pvb = erfa.epv00(2400000.5, float(jd_tt) - 2400000.5)
    # Sun geocentric vector is -Earth heliocentric vector.
    sx, sy, sz = -float(pvh[0][0]), -float(pvh[0][1]), -float(pvh[0][2])
    eps = float(erfa.obl06(2400000.5, float(jd_tt) - 2400000.5))
    cos_e = math.cos(eps)
    sin_e = math.sin(eps)
    ecl_x = sx
    ecl_y = sy * cos_e + sz * sin_e
    tropical_lon = math.degrees(math.atan2(ecl_y, ecl_x)) % 360.0
    aya = ayanamsa_degrees(float(jd_tt), "lahiri", true=False)
    return (tropical_lon - aya) % 360.0


def find_solar_return_jd(
    natal_sun_sidereal_lon_deg: float,
    target_year_approx_jd: float | None = None,
    *,
    birth_jd: float | None = None,
    birth_year: int | None = None,
    target_year: int | None = None,
    sun_sidereal_lon_fn: Callable[[float], float] | None = None,
    tolerance_deg: float = 1e-10,
    max_iterations: int = 64,
) -> SolarReturnEpoch:
    """Find the exact Julian Date (TT) of the sidereal Solar Return (Varsha Pravesha).

    Uses damped Newton-secant steps with angular unwrapping to converge to
    ``abs(residual_deg) < tolerance_deg`` (well inside ``1e-8`` degrees).
    """

    target_lon = _norm360(natal_sun_sidereal_lon_deg)
    if target_year_approx_jd is not None:
        jd_guess = float(target_year_approx_jd)
    elif birth_jd is not None and birth_year is not None and target_year is not None:
        jd_guess = float(birth_jd) + (int(target_year) - int(birth_year)) * SIDEREAL_YEAR_DAYS
    else:
        raise ValueError(
            "provide either target_year_approx_jd or (birth_jd, birth_year, target_year)"
        )

    lon_fn = _default_sidereal_sun_lon if sun_sidereal_lon_fn is None else sun_sidereal_lon_fn

    def f_err(jd: float) -> float:
        return _signed_diff_deg(lon_fn(jd), target_lon)

    # First coarse step using mean solar sidereal motion (~0.985609 deg/day)
    mean_rate = 360.0 / SIDEREAL_YEAR_DAYS
    x0 = jd_guess
    f0 = f_err(x0)
    if abs(f0) <= tolerance_deg:
        achieved = _norm360(lon_fn(x0))
        payload = {"jd_tt": round(x0, 10), "target_lon": round(target_lon, 10)}
        return SolarReturnEpoch(
            jd_tt=x0,
            natal_sun_sidereal_lon_deg=target_lon,
            achieved_sun_sidereal_lon_deg=achieved,
            residual_deg=abs(f0),
            iterations=0,
            receipt_sha256=canonical_hash(payload),
        )

    x1 = x0 - f0 / mean_rate
    f1 = f_err(x1)
    iterations = 1

    for step in range(2, max_iterations + 1):
        iterations = step
        if abs(f1) <= tolerance_deg:
            break
        df = f1 - f0
        if abs(df) < 1e-15:
            slope = mean_rate
        else:
            slope = df / (x1 - x0)
            if slope <= 0.1 or slope >= 2.5:
                slope = mean_rate
        delta = f1 / slope
        # Clamp single step to at most 10 days to avoid wild jumps
        delta = max(-10.0, min(10.0, delta))
        x_next = x1 - delta
        f_next = f_err(x_next)
        x0, f0 = x1, f1
        x1, f1 = x_next, f_next
        if abs(f1) <= tolerance_deg or abs(x1 - x0) <= 1e-12:
            break

    achieved = _norm360(lon_fn(x1))
    residual = abs(_signed_diff_deg(achieved, target_lon))
    payload = {
        "jd_tt": round(x1, 10),
        "natal_sun_sidereal_lon_deg": round(target_lon, 10),
        "achieved_sun_sidereal_lon_deg": round(achieved, 10),
        "iterations": iterations,
    }
    return SolarReturnEpoch(
        jd_tt=x1,
        natal_sun_sidereal_lon_deg=target_lon,
        achieved_sun_sidereal_lon_deg=achieved,
        residual_deg=residual,
        iterations=iterations,
        receipt_sha256=canonical_hash(payload),
    )


def compute_muntha(
    natal_asc_sign_or_lon: int | float,
    birth_year: int,
    target_year: int,
    varsha_asc_sign_or_lon: int | float,
) -> MunthaReport:
    """Compute the progressed Muntha sign, longitude, lord, and Varsha house placement."""

    elapsed = int(target_year) - int(birth_year)
    if elapsed < 0:
        raise ValueError(f"target_year ({target_year}) must be >= birth_year ({birth_year})")

    if isinstance(natal_asc_sign_or_lon, int) and not isinstance(natal_asc_sign_or_lon, bool) and 0 <= natal_asc_sign_or_lon <= 11:
        natal_sign = natal_asc_sign_or_lon
        deg_in_sign = 0.0
    else:
        lon_val = _norm360(float(natal_asc_sign_or_lon))
        natal_sign = int(lon_val // 30.0)
        deg_in_sign = lon_val - natal_sign * 30.0

    if isinstance(varsha_asc_sign_or_lon, int) and not isinstance(varsha_asc_sign_or_lon, bool) and 0 <= varsha_asc_sign_or_lon <= 11:
        varsha_sign = varsha_asc_sign_or_lon
    else:
        varsha_sign = int(_norm360(float(varsha_asc_sign_or_lon)) // 30.0)

    muntha_sign = (natal_sign + elapsed) % 12
    muntha_lon = muntha_sign * 30.0 + deg_in_sign
    muntha_lord = RASI_LORDS[muntha_sign]
    house = ((muntha_sign - varsha_sign) % 12) + 1
    # Per Tajika Neelakanthi: Muntha in 9, 10, 11, 1, 2, 3, 5 is auspicious; 4, 6, 7, 8, 12 is inauspicious.
    auspicious = house in {1, 2, 3, 5, 9, 10, 11}

    payload = {
        "natal_asc_sign": natal_sign,
        "birth_year": int(birth_year),
        "target_year": int(target_year),
        "muntha_sign": muntha_sign,
        "varsha_asc_sign": varsha_sign,
        "house": house,
    }
    return MunthaReport(
        natal_asc_sign=natal_sign,
        birth_year=int(birth_year),
        target_year=int(target_year),
        elapsed_years=elapsed,
        muntha_sign=muntha_sign,
        muntha_rasi_name=RASI_NAMES[muntha_sign],
        muntha_longitude_deg=muntha_lon,
        muntha_lord=muntha_lord,
        varsha_asc_sign=varsha_sign,
        house_from_varsha_lagna=house,
        is_auspicious_house=auspicious,
        receipt_sha256=canonical_hash(payload),
    )


def _panchadha_relationship(planet: str, other_lord: str, planet_signs: Mapping[str, int]) -> str:
    """Compute compound (Panchadha) relationship between ``planet`` and ``other_lord``."""

    if planet == other_lord:
        return "own"

    if other_lord in NAISARGIKA_FRIENDS[planet]:
        nat_score = 1
    elif other_lord in NAISARGIKA_ENEMIES[planet]:
        nat_score = -1
    else:
        nat_score = 0

    p_sign = planet_signs[planet]
    o_sign = planet_signs[other_lord]
    dist = ((o_sign - p_sign) % 12) + 1
    # Tatkalika (temporal) friendship in houses 2, 3, 4, 10, 11, 12 from the planet.
    tat_score = 1 if dist in {2, 3, 4, 10, 11, 12} else -1

    total = nat_score + tat_score
    if total >= 2:
        return "adhi_mitra"
    if total == 1:
        return "mitra"
    if total == 0:
        return "sama"
    if total == -1:
        return "shatru"
    return "adhi_shatru"


_REL_MULTIPLIER: Mapping[str, float] = {
    "own": 1.0,
    "adhi_mitra": 0.75,
    "mitra": 0.5,
    "sama": 0.25,
    "shatru": 0.125,
    "adhi_shatru": 0.0625,
}


def hadda_lord_for_longitude(sidereal_lon_deg: float) -> str:
    """Return the classical Tajika Hadda (bound) lord for a sidereal longitude."""

    lon = _norm360(sidereal_lon_deg)
    sign_idx = min(int(lon // 30.0), 11)
    deg_in_sign = lon - sign_idx * 30.0
    for bound_end, lord in TAJIKA_HADDA_TABLE[sign_idx]:
        if deg_in_sign < bound_end or math.isclose(deg_in_sign, 30.0):
            return lord
    return TAJIKA_HADDA_TABLE[sign_idx][-1][1]


def _drekkana_lord_for_longitude(sidereal_lon_deg: float) -> str:
    """Return Drekkana (10-degree decanate) lord (1st, 5th, 9th sign lord from sign)."""

    lon = _norm360(sidereal_lon_deg)
    sign_idx = min(int(lon // 30.0), 11)
    part = min(int((lon - sign_idx * 30.0) // 10.0), 2)
    target_sign = (sign_idx + part * 4) % 12
    return RASI_LORDS[target_sign]


def _navamsa_lord_for_longitude(sidereal_lon_deg: float) -> str:
    """Return Navamsa (3 deg 20 min division) sign lord."""

    lon = _norm360(sidereal_lon_deg)
    nav_index = min(int(lon // (10.0 / 3.0)), 107)
    nav_sign = nav_index % 12
    return RASI_LORDS[nav_sign]


def compute_pancha_vargiya_bala(
    planet_lons: Mapping[str, float],
) -> Mapping[str, PanchaVargiyaPlanetBala]:
    """Compute Pancha-Vargiya Bala (Kshetra 30, Uchcha 20, Hadda 15, Drekkana 10, Navamsa 5).

    Total Virupas (max 80) are divided by 4 to yield Vishwa Bala in ``(0, 20.0]``.
    """

    signs: dict[str, int] = {}
    norm_lons: dict[str, float] = {}
    for body in SEVEN_PLANETS:
        if body not in planet_lons:
            raise ValueError(f"missing planet {body!r} in planet_lons")
        lon = _norm360(planet_lons[body])
        norm_lons[body] = lon
        signs[body] = min(int(lon // 30.0), 11)

    result: dict[str, PanchaVargiyaPlanetBala] = {}
    for body in SEVEN_PLANETS:
        lon = norm_lons[body]
        sign_idx = signs[body]

        # 1. Kshetra Bala (max 30 Virupas)
        rasi_lord = RASI_LORDS[sign_idx]
        rel_kshetra = _panchadha_relationship(body, rasi_lord, signs)
        kshetra_bala = 30.0 * _REL_MULTIPLIER[rel_kshetra]

        # 2. Uchcha Bala (max 20 Virupas)
        exalt_lon = DEEP_EXALTATION_DEG[body]
        debil_lon = (exalt_lon + 180.0) % 360.0
        dist_from_debil = abs(_signed_diff_deg(lon, debil_lon))
        uchcha_bala = 20.0 * (dist_from_debil / 180.0)

        # 3. Hadda Bala (max 15 Virupas)
        h_lord = hadda_lord_for_longitude(lon)
        rel_hadda = _panchadha_relationship(body, h_lord, signs)
        hadda_bala = 15.0 * _REL_MULTIPLIER[rel_hadda]

        # 4. Drekkana Bala (max 10 Virupas)
        d_lord = _drekkana_lord_for_longitude(lon)
        rel_drekkana = _panchadha_relationship(body, d_lord, signs)
        drekkana_bala = 10.0 * _REL_MULTIPLIER[rel_drekkana]

        # 5. Navamsa Bala (max 5 Virupas)
        n_lord = _navamsa_lord_for_longitude(lon)
        rel_navamsa = _panchadha_relationship(body, n_lord, signs)
        navamsa_bala = 5.0 * _REL_MULTIPLIER[rel_navamsa]

        total_virupas = kshetra_bala + uchcha_bala + hadda_bala + drekkana_bala + navamsa_bala
        vishwa_bala = total_virupas / 4.0

        if vishwa_bala >= 10.0:
            tier = "purnabali"
        elif vishwa_bala >= 5.0:
            tier = "madhyabali"
        else:
            tier = "alpabali"

        result[body] = PanchaVargiyaPlanetBala(
            planet=body,
            longitude_deg=lon,
            kshetra_bala=round(kshetra_bala, 6),
            uchcha_bala=round(uchcha_bala, 6),
            hadda_bala=round(hadda_bala, 6),
            drekkana_bala=round(drekkana_bala, 6),
            navamsa_bala=round(navamsa_bala, 6),
            total_virupas=round(total_virupas, 6),
            vishwa_bala=round(vishwa_bala, 6),
            strength_tier=tier,
            hadda_lord=h_lord,
            drekkana_lord=d_lord,
            navamsa_lord=n_lord,
        )
    return result


def compute_harsha_bala(
    planet_lons: Mapping[str, float],
    varsha_asc_lon_deg: float,
    *,
    is_day_birth: bool = True,
) -> Mapping[str, HarshaPlanetBala]:
    """Compute the fourfold Harsha Bala (0, 5, 10, 15, or 20 points) for each of the 7 planets."""

    asc_sign = int(_norm360(varsha_asc_lon_deg) // 30.0)
    feminine_planets = {"moon", "venus", "mercury", "saturn"}
    masculine_planets = {"sun", "mars", "jupiter"}
    stri_houses = {1, 2, 3, 7, 8, 9}
    purusha_houses = {4, 5, 6, 10, 11, 12}
    day_planets = {"sun", "jupiter", "saturn"}
    night_planets = {"moon", "mars", "venus", "mercury"}

    out: dict[str, HarshaPlanetBala] = {}
    for body in SEVEN_PLANETS:
        lon = _norm360(planet_lons[body])
        p_sign = int(lon // 30.0)
        house = ((p_sign - asc_sign) % 12) + 1

        sthana_pts = 5 if house == HARSHA_STHANA_HOUSE[body] else 0
        uchcha_pts = 5 if (p_sign == EXALTATION_SIGN[body] or p_sign in OWN_SIGNS[body]) else 0

        if (body in feminine_planets and house in stri_houses) or (
            body in masculine_planets and house in purusha_houses
        ):
            gender_pts = 5
        else:
            gender_pts = 0

        if (is_day_birth and body in day_planets) or (not is_day_birth and body in night_planets):
            diurnal_pts = 5
        else:
            diurnal_pts = 0

        total = sthana_pts + uchcha_pts + gender_pts + diurnal_pts
        out[body] = HarshaPlanetBala(
            planet=body,
            house_from_lagna=house,
            sthana_points=sthana_pts,
            uchcha_swakshetra_points=uchcha_pts,
            stri_purusha_points=gender_pts,
            dina_ratri_points=diurnal_pts,
            total_points=total,
        )
    return out


def _has_tajika_aspect(sign_a: int, sign_b: int) -> bool:
    """In Tajika, aspects occur across 1/1, 3/11, 4/10, 5/9, and 7/7 sign distances."""

    dist = ((sign_b - sign_a) % 12) + 1
    return dist in {1, 3, 4, 5, 7, 9, 10, 11}


def determine_varsheshwara(
    planet_lons: Mapping[str, float],
    natal_asc_lon_deg: float,
    varsha_asc_lon_deg: float,
    muntha_sign: int,
    *,
    is_day_birth: bool = True,
    pancha_vargiya: Mapping[str, PanchaVargiyaPlanetBala] | None = None,
) -> VarsheshwaraReport:
    """Determine the 5 Panchadhikari office holders and select the Varsheshwara (Year Lord)."""

    pv = compute_pancha_vargiya_bala(planet_lons) if pancha_vargiya is None else pancha_vargiya

    natal_sign = int(_norm360(natal_asc_lon_deg) // 30.0)
    varsha_sign = int(_norm360(varsha_asc_lon_deg) // 30.0)
    sun_sign = int(_norm360(planet_lons["sun"]) // 30.0)
    moon_sign = int(_norm360(planet_lons["moon"]) // 30.0)

    muntha_lord = RASI_LORDS[muntha_sign % 12]
    janma_lagna_lord = RASI_LORDS[natal_sign]
    varsha_lagna_lord = RASI_LORDS[varsha_sign]
    tri_rashi_pati = TRI_RASHI_PATI_TABLE[varsha_sign][0 if is_day_birth else 1]
    din_ratri_pati = RASI_LORDS[sun_sign] if is_day_birth else RASI_LORDS[moon_sign]

    raw_offices = (
        muntha_lord,
        janma_lagna_lord,
        varsha_lagna_lord,
        tri_rashi_pati,
        din_ratri_pati,
    )
    candidates: list[str] = []
    for lord in raw_offices:
        if lord not in candidates:
            candidates.append(lord)

    # Check which candidates aspect or occupy Varsha Lagna
    aspecting_candidates: list[str] = []
    for cand in candidates:
        cand_sign = int(_norm360(planet_lons[cand]) // 30.0)
        if _has_tajika_aspect(cand_sign, varsha_sign):
            aspecting_candidates.append(cand)

    # Per Tajika Neelakanthi, Moon normally requires higher scrutiny unless it is the sole
    # aspecting candidate or strongest in Night charts; we rank aspecting candidates by Vishwa Bala.
    pool = aspecting_candidates if aspecting_candidates else candidates
    non_moon_pool = [c for c in pool if c != "moon"]
    effective_pool = non_moon_pool if (non_moon_pool and pv["moon"].vishwa_bala < 10.0) else pool

    winner = max(effective_pool, key=lambda c: pv[c].vishwa_bala)
    winner_sign = int(_norm360(planet_lons[winner]) // 30.0)
    aspects_lagna = _has_tajika_aspect(winner_sign, varsha_sign)

    payload = {
        "panchadhikari": list(raw_offices),
        "varsheshwara": winner,
        "vishwa_bala": round(pv[winner].vishwa_bala, 6),
        "aspects_varsha_lagna": aspects_lagna,
    }
    return VarsheshwaraReport(
        muntha_lord=muntha_lord,
        janma_lagna_lord=janma_lagna_lord,
        varsha_lagna_lord=varsha_lagna_lord,
        tri_rashi_pati=tri_rashi_pati,
        din_ratri_pati=din_ratri_pati,
        panchadhikari_candidates=tuple(candidates),
        varsheshwara=winner,
        varsheshwara_vishwa_bala=pv[winner].vishwa_bala,
        aspects_varsha_lagna=aspects_lagna,
        receipt_sha256=canonical_hash(payload),
    )


def evaluate_tajika_yogas(
    planet_lons: Mapping[str, float],
    varsha_asc_lon_deg: float,
    *,
    retrograde_planets: Sequence[str] = (),
    pancha_vargiya: Mapping[str, PanchaVargiyaPlanetBala] | None = None,
) -> tuple[TajikaYogaFinding, ...]:
    """Evaluate all 16 classical Tajika Yogas in the annual Varsha chart."""

    pv = compute_pancha_vargiya_bala(planet_lons) if pancha_vargiya is None else pancha_vargiya
    asc_sign = int(_norm360(varsha_asc_lon_deg) // 30.0)
    retro_set = {p.lower() for p in retrograde_planets}

    signs: dict[str, int] = {}
    deg_in_sign: dict[str, float] = {}
    houses: dict[str, int] = {}
    for body in SEVEN_PLANETS:
        lon = _norm360(planet_lons[body])
        s_idx = int(lon // 30.0)
        signs[body] = s_idx
        deg_in_sign[body] = lon - s_idx * 30.0
        houses[body] = ((s_idx - asc_sign) % 12) + 1

    findings: list[TajikaYogaFinding] = []

    # 1. Ikkavala Yoga: All 7 planets in Kendra (1,4,7,10) or Panapara (2,5,8,11), none in Apoklima (3,6,9,12).
    apoklima_planets = [b for b in SEVEN_PLANETS if houses[b] in {3, 6, 9, 12}]
    ikkavala_active = len(apoklima_planets) == 0
    findings.append(
        TajikaYogaFinding(
            code="ikkavala",
            name="Ikkavala Yoga",
            active=ikkavala_active,
            subtype=None,
            involved_planets=SEVEN_PLANETS if ikkavala_active else (),
            orb_limit_deg=None,
            actual_separation_deg=None,
            summary="All seven planets occupy Kendra and Panapara houses with none in Apoklima.",
        )
    )

    # 2. Induvara Yoga: All 7 planets in Apoklima houses (3, 6, 9, 12).
    induvara_active = len(apoklima_planets) == len(SEVEN_PLANETS)
    findings.append(
        TajikaYogaFinding(
            code="induvara",
            name="Induvara Yoga",
            active=induvara_active,
            subtype=None,
            involved_planets=SEVEN_PLANETS if induvara_active else (),
            orb_limit_deg=None,
            actual_separation_deg=None,
            summary="All seven planets occupy Apoklima (cadent 3, 6, 9, 12) houses.",
        )
    )

    # Pairwise Ithasala & Ishrafa detection
    ithasala_pairs: list[tuple[str, str, str, float, float]] = []
    ishrafa_pairs: list[tuple[str, str, float, float]] = []

    for idx_a, body_a in enumerate(SEVEN_PLANETS):
        for body_b in SEVEN_PLANETS[idx_a + 1 :]:
            if TAJIKA_SPEED_RANK[body_a] < TAJIKA_SPEED_RANK[body_b]:
                faster, slower = body_a, body_b
            else:
                faster, slower = body_b, body_a

            mean_orb = 0.5 * (TAJIKA_PLANET_ORBS_DEG[faster] + TAJIKA_PLANET_ORBS_DEG[slower])
            aspect_ok = _has_tajika_aspect(signs[faster], signs[slower])
            deg_f = deg_in_sign[faster]
            deg_s = deg_in_sign[slower]
            diff = abs(deg_s - deg_f)

            if aspect_ok and deg_f <= deg_s and diff <= mean_orb:
                subtype = "Purna" if diff <= 1.0 else "Vartamana"
                ithasala_pairs.append((faster, slower, subtype, mean_orb, diff))
            elif deg_f >= 29.0 and _has_tajika_aspect((signs[faster] + 1) % 12, signs[slower]):
                # Bhavishyat Ithasala: faster planet at end of sign (>29 deg) about to enter aspect
                next_diff = (30.0 - deg_f) + deg_s
                if next_diff <= mean_orb:
                    ithasala_pairs.append((faster, slower, "Bhavishyat", mean_orb, next_diff))
            elif aspect_ok and deg_f > deg_s and (deg_f - deg_s) <= mean_orb:
                ishrafa_pairs.append((faster, slower, mean_orb, deg_f - deg_s))

    # 3. Ithasala Yoga
    if ithasala_pairs:
        f_p, s_p, sub, orb_lim, sep = ithasala_pairs[0]
        involved = tuple(dict.fromkeys(p for pair in ithasala_pairs for p in pair[:2]))
        findings.append(
            TajikaYogaFinding(
                code="ithasala",
                name="Ithasala Yoga",
                active=True,
                subtype=sub,
                involved_planets=involved,
                orb_limit_deg=orb_lim,
                actual_separation_deg=round(sep, 6),
                summary=f"Faster planet ({f_p}) applies to slower planet ({s_p}) within Tajika Deeptamsa ({sub}).",
            )
        )
    else:
        findings.append(
            TajikaYogaFinding(
                code="ithasala",
                name="Ithasala Yoga",
                active=False,
                subtype=None,
                involved_planets=(),
                orb_limit_deg=None,
                actual_separation_deg=None,
                summary="No applying Ithasala aspect within Deeptamsa.",
            )
        )

    # 4. Ishrafa (Musarpha) Yoga
    if ishrafa_pairs:
        f_p, s_p, orb_lim, sep = ishrafa_pairs[0]
        involved = tuple(dict.fromkeys(p for pair in ishrafa_pairs for p in pair[:2]))
        findings.append(
            TajikaYogaFinding(
                code="ishrafa",
                name="Ishrafa Yoga",
                active=True,
                subtype=None,
                involved_planets=involved,
                orb_limit_deg=orb_lim,
                actual_separation_deg=round(sep, 6),
                summary=f"Faster planet ({f_p}) has separated past slower planet ({s_p}) within orb.",
            )
        )
    else:
        findings.append(
            TajikaYogaFinding(
                code="ishrafa",
                name="Ishrafa Yoga",
                active=False,
                subtype=None,
                involved_planets=(),
                orb_limit_deg=None,
                actual_separation_deg=None,
                summary="No separating Ishrafa aspect within orb.",
            )
        )

    # 5. Nakta Yoga: A faster planet links two slower planets that do not aspect each other.
    nakta_trio: tuple[str, str, str] | None = None
    for idx_a, slow_a in enumerate(SEVEN_PLANETS):
        for slow_b in SEVEN_PLANETS[idx_a + 1 :]:
            if _has_tajika_aspect(signs[slow_a], signs[slow_b]):
                continue
            for med in SEVEN_PLANETS:
                if med in {slow_a, slow_b}:
                    continue
                if TAJIKA_SPEED_RANK[med] < min(TAJIKA_SPEED_RANK[slow_a], TAJIKA_SPEED_RANK[slow_b]):
                    if _has_tajika_aspect(signs[med], signs[slow_a]) and _has_tajika_aspect(signs[med], signs[slow_b]):
                        orb_a = 0.5 * (TAJIKA_PLANET_ORBS_DEG[med] + TAJIKA_PLANET_ORBS_DEG[slow_a])
                        orb_b = 0.5 * (TAJIKA_PLANET_ORBS_DEG[med] + TAJIKA_PLANET_ORBS_DEG[slow_b])
                        if abs(deg_in_sign[med] - deg_in_sign[slow_a]) <= orb_a and abs(
                            deg_in_sign[med] - deg_in_sign[slow_b]
                        ) <= orb_b:
                            nakta_trio = (med, slow_a, slow_b)
                            break
            if nakta_trio:
                break
        if nakta_trio:
            break

    findings.append(
        TajikaYogaFinding(
            code="nakta",
            name="Nakta Yoga",
            active=nakta_trio is not None,
            subtype=None,
            involved_planets=nakta_trio if nakta_trio else (),
            orb_limit_deg=None,
            actual_separation_deg=None,
            summary="A faster intermediary planet transfers light between two non-aspecting slower planets.",
        )
    )

    # 6. Yamaya Yoga: A slower planet receives light from two non-aspecting faster planets.
    yamaya_trio: tuple[str, str, str] | None = None
    for slow in SEVEN_PLANETS:
        connected_faster = [
            pair[0] for pair in ithasala_pairs if pair[1] == slow
        ]
        if len(connected_faster) >= 2:
            yamaya_trio = (slow, connected_faster[0], connected_faster[1])
            break

    findings.append(
        TajikaYogaFinding(
            code="yamaya",
            name="Yamaya Yoga",
            active=yamaya_trio is not None,
            subtype=None,
            involved_planets=yamaya_trio if yamaya_trio else (),
            orb_limit_deg=None,
            actual_separation_deg=None,
            summary="Two faster planets collect light into a slower receiver planet.",
        )
    )

    # 7. Manau Yoga: Ithasala obstructed by hostile aspect (1, 4, 7, 10) from Mars or Saturn.
    manau_planets: tuple[str, ...] = ()
    for f_p, s_p, _sub, _orb, _sep in ithasala_pairs:
        for malefic in ("mars", "saturn"):
            if malefic in {f_p, s_p}:
                continue
            dist_f = ((signs[f_p] - signs[malefic]) % 12) + 1
            if dist_f in {1, 4, 7, 10}:
                manau_planets = (f_p, s_p, malefic)
                break
        if manau_planets:
            break

    findings.append(
        TajikaYogaFinding(
            code="manau",
            name="Manau Yoga",
            active=bool(manau_planets),
            subtype=None,
            involved_planets=manau_planets,
            orb_limit_deg=None,
            actual_separation_deg=None,
            summary="An active Ithasala is obstructed by a square, opposition, or conjunction from Mars or Saturn.",
        )
    )

    # 8. Kamboola Yoga: Ithasala between two planets while the Moon also forms Ithasala with one of them.
    moon_ithasalas = {pair[1] for pair in ithasala_pairs if pair[0] == "moon"}
    kamboola_trio: tuple[str, ...] = ()
    for f_p, s_p, _sub, _orb, _sep in ithasala_pairs:
        if "moon" not in {f_p, s_p} and (f_p in moon_ithasalas or s_p in moon_ithasalas):
            kamboola_trio = ("moon", f_p, s_p)
            break

    findings.append(
        TajikaYogaFinding(
            code="kamboola",
            name="Kamboola Yoga",
            active=bool(kamboola_trio),
            subtype=None,
            involved_planets=kamboola_trio,
            orb_limit_deg=None,
            actual_separation_deg=None,
            summary="Moon joins in Ithasala with planets already connected by Ithasala.",
        )
    )

    # 9. Gairi-Kamboola Yoga: Moon at sign end (deg >= 27) lacking dignity, moving to form Ithasala.
    moon_end = deg_in_sign["moon"] >= 27.0 and signs["moon"] not in {1, 3}
    gairi_active = bool(kamboola_trio and moon_end)
    findings.append(
        TajikaYogaFinding(
            code="gairi_kamboola",
            name="Gairi-Kamboola Yoga",
            active=gairi_active,
            subtype=None,
            involved_planets=kamboola_trio if gairi_active else (),
            orb_limit_deg=None,
            actual_separation_deg=None,
            summary="Kamboola formed by an undignified Moon at the closing degrees of a sign.",
        )
    )

    # 10. Khallasara Yoga: Ithasala present, but Moon forms neither Ithasala nor Ishrafa with the pair.
    moon_connected = any("moon" in pair[:2] for pair in ithasala_pairs) or any(
        "moon" in pair[:2] for pair in ishrafa_pairs
    )
    khallasara_active = bool(ithasala_pairs and not moon_connected)
    findings.append(
        TajikaYogaFinding(
            code="khallasara",
            name="Khallasara Yoga",
            active=khallasara_active,
            subtype=None,
            involved_planets=("moon", ithasala_pairs[0][0], ithasala_pairs[0][1]) if khallasara_active else (),
            orb_limit_deg=None,
            actual_separation_deg=None,
            summary="Moon moves void of connection with the Ithasala planets.",
        )
    )

    # 11. Radda Yoga: Ithasala spoiled because a participant is retrograde, combust, debilitated, or in 6/8/12.
    radda_pair: tuple[str, str] = ()
    for f_p, s_p, _sub, _orb, _sep in ithasala_pairs:
        bad_f = (
            f_p in retro_set
            or houses[f_p] in {6, 8, 12}
            or signs[f_p] == DEBILITATION_SIGN[f_p]
        )
        bad_s = (
            s_p in retro_set
            or houses[s_p] in {6, 8, 12}
            or signs[s_p] == DEBILITATION_SIGN[s_p]
        )
        if bad_f or bad_s:
            radda_pair = (f_p, s_p)
            break

    findings.append(
        TajikaYogaFinding(
            code="radda",
            name="Radda Yoga",
            active=bool(radda_pair),
            subtype=None,
            involved_planets=radda_pair,
            orb_limit_deg=None,
            actual_separation_deg=None,
            summary="Ithasala nullified or weakened by retrogression, debilitation, or Dusthana (6/8/12) placement.",
        )
    )

    # 12. Duphal-Kuttha Yoga: Faster planet in Ithasala has low Bala (< 10 Vishwas) while slower has high Bala (>= 10).
    duphal_pair: tuple[str, str] = ()
    for f_p, s_p, _sub, _orb, _sep in ithasala_pairs:
        if pv[f_p].vishwa_bala < 10.0 and pv[s_p].vishwa_bala >= 10.0:
            duphal_pair = (f_p, s_p)
            break

    findings.append(
        TajikaYogaFinding(
            code="duphal_kuttha",
            name="Duphal-Kuttha Yoga",
            active=bool(duphal_pair),
            subtype=None,
            involved_planets=duphal_pair,
            orb_limit_deg=None,
            actual_separation_deg=None,
            summary="Weak faster planet applies to a strong slower planet in Ithasala.",
        )
    )

    # 13. Dutthottha-Davira Yoga: Both Ithasala planets are weak (< 10 Vishwas), but one connects to a strong third planet.
    dutthottha_trio: tuple[str, ...] = ()
    for f_p, s_p, _sub, _orb, _sep in ithasala_pairs:
        if pv[f_p].vishwa_bala < 10.0 and pv[s_p].vishwa_bala < 10.0:
            for other in SEVEN_PLANETS:
                if other not in {f_p, s_p} and pv[other].vishwa_bala >= 10.0:
                    if _has_tajika_aspect(signs[other], signs[f_p]) or _has_tajika_aspect(signs[other], signs[s_p]):
                        dutthottha_trio = (f_p, s_p, other)
                        break
        if dutthottha_trio:
            break

    findings.append(
        TajikaYogaFinding(
            code="dutthottha_davira",
            name="Dutthottha-Davira Yoga",
            active=bool(dutthottha_trio),
            subtype=None,
            involved_planets=dutthottha_trio,
            orb_limit_deg=None,
            actual_separation_deg=None,
            summary="Two weak Ithasala planets derive success through aspect from a third strong planet.",
        )
    )

    # 14. Tambira Yoga: Planet at closing degrees (>= 28 deg) about to enter next sign where it joins a strong planet.
    tambira_planets: tuple[str, ...] = ()
    for body in SEVEN_PLANETS:
        if deg_in_sign[body] >= 28.0:
            next_sign = (signs[body] + 1) % 12
            for target in SEVEN_PLANETS:
                if target != body and _has_tajika_aspect(next_sign, signs[target]) and pv[target].vishwa_bala >= 10.0:
                    tambira_planets = (body, target)
                    break
        if tambira_planets:
            break

    findings.append(
        TajikaYogaFinding(
            code="tambira",
            name="Tambira Yoga",
            active=bool(tambira_planets),
            subtype=None,
            involved_planets=tambira_planets,
            orb_limit_deg=None,
            actual_separation_deg=None,
            summary="Planet at the end of a sign enters the next sign to connect with a strong planet.",
        )
    )

    # 15. Kuttha Yoga: Lagna lord and strong planets posited in Kendra or Panapara houses with high Bala.
    lagna_lord = RASI_LORDS[asc_sign]
    kuttha_active = houses[lagna_lord] in {1, 4, 7, 10, 2, 5, 8, 11} and pv[lagna_lord].vishwa_bala >= 10.0
    findings.append(
        TajikaYogaFinding(
            code="kuttha",
            name="Kuttha Yoga",
            active=kuttha_active,
            subtype=None,
            involved_planets=(lagna_lord,) if kuttha_active else (),
            orb_limit_deg=None,
            actual_separation_deg=None,
            summary="Varsha Lagna lord occupies a Kendra or Panapara house with Purnabali strength.",
        )
    )

    # 16. Durupha Yoga: Lagna lord or Ithasala planets in 6/8/12 with low Pancha-Vargiya Bala (< 5 Vishwas).
    durupha_bodies = tuple(
        b for b in SEVEN_PLANETS if houses[b] in {6, 8, 12} and pv[b].vishwa_bala < 6.0
    )
    findings.append(
        TajikaYogaFinding(
            code="durupha",
            name="Durupha Yoga",
            active=bool(durupha_bodies),
            subtype=None,
            involved_planets=durupha_bodies,
            orb_limit_deg=None,
            actual_separation_deg=None,
            summary="Planets posited in Dusthana (6, 8, 12) houses with weak Pancha-Vargiya Bala.",
        )
    )

    return tuple(findings)


def compute_mudda_dasha(
    natal_moon_lon_deg: float,
    birth_year: int,
    target_year: int,
    solar_return_jd: float,
    *,
    year_length_days: float = TROPICAL_SOLAR_YEAR_DAYS,
) -> tuple[MuddaDashaPeriod, ...]:
    """Compute the 1-year compressed Vimshottari Mudda Dasha starting at ``solar_return_jd``.

    Per *Tajika Neelakanthi*, the starting dasha index is ``(natal_nakshatra_index + elapsed_years - 1) % 9``
    (where 1-based counting from natal Nakshatra plus completed years modulo 9 gives the opening lord),
    with the balance of the first dasha proportional to the remaining fraction of the natal Nakshatra,
    followed by full dashas and closing with the remainder of the opening lord so the total equals
    ``year_length_days`` exactly.
    """

    elapsed = int(target_year) - int(birth_year)
    if elapsed < 0:
        raise ValueError("target_year must be >= birth_year")

    lon = _norm360(natal_moon_lon_deg)
    nak_span = 40.0 / 3.0
    nak_idx = min(int(lon // nak_span), 26)
    fraction_remaining = max(0.0, min(1.0, (nak_span - (lon - nak_idx * nak_span)) / nak_span))

    start_lord_idx = (nak_idx + elapsed) % 9
    ordered_indices = [(start_lord_idx + k) % 9 for k in range(9)]

    periods: list[MuddaDashaPeriod] = []
    cursor_jd = float(solar_return_jd)

    for pos, idx in enumerate(ordered_indices):
        lord = VIMSHOTTARI_LORDS[idx]
        full_days = year_length_days * (VIMSHOTTARI_YEARS[lord] / 120.0)
        duration = full_days * fraction_remaining if pos == 0 else full_days
        end_jd = cursor_jd + duration

        # Compute 9 sub-periods (Antardashas) inside this Mudda Mahadasha
        antar_list: list[tuple[str, float, float]] = []
        a_cursor = cursor_jd
        for k in range(9):
            a_lord = VIMSHOTTARI_LORDS[(idx + k) % 9]
            a_dur = duration * (VIMSHOTTARI_YEARS[a_lord] / 120.0)
            a_end = a_cursor + a_dur
            antar_list.append((a_lord, a_cursor, a_end))
            a_cursor = a_end

        periods.append(
            MuddaDashaPeriod(
                lord=lord,
                start_jd=cursor_jd,
                end_jd=end_jd,
                duration_days=duration,
                antardashas=tuple(antar_list),
            )
        )
        cursor_jd = end_jd

    # If fraction_remaining < 1.0, append the tail of the opening lord so total == year_length_days.
    if fraction_remaining < 1.0 - 1e-12:
        first_lord = VIMSHOTTARI_LORDS[start_lord_idx]
        full_days = year_length_days * (VIMSHOTTARI_YEARS[first_lord] / 120.0)
        tail_duration = full_days * (1.0 - fraction_remaining)
        end_jd = cursor_jd + tail_duration
        antar_list = []
        a_cursor = cursor_jd
        for k in range(9):
            a_lord = VIMSHOTTARI_LORDS[(start_lord_idx + k) % 9]
            a_dur = tail_duration * (VIMSHOTTARI_YEARS[a_lord] / 120.0)
            a_end = a_cursor + a_dur
            antar_list.append((a_lord, a_cursor, a_end))
            a_cursor = a_end
        periods.append(
            MuddaDashaPeriod(
                lord=first_lord,
                start_jd=cursor_jd,
                end_jd=end_jd,
                duration_days=tail_duration,
                antardashas=tuple(antar_list),
            )
        )

    return tuple(periods)


def _is_on_zodiacal_arc(start_deg: float, end_deg: float, test_deg: float) -> bool:
    """Return True if ``test_deg`` lies on the forward zodiacal arc from ``start_deg`` to ``end_deg``."""

    arc = (end_deg - start_deg) % 360.0
    pos = (test_deg - start_deg) % 360.0
    return pos <= arc + 1e-9


def _eval_saham_formula(
    a_deg: float,
    b_deg: float,
    c_deg: float,
    *,
    reverse_at_night: bool,
    is_day_birth: bool,
) -> tuple[float, str]:
    """Evaluate ``A - B + C`` (or ``B - A + C`` at night) with the Tajika +30 deg rule."""

    if reverse_at_night and not is_day_birth:
        first, second = b_deg, a_deg
        label = "B - A + C (Night)"
    else:
        first, second = a_deg, b_deg
        label = "A - B + C (Day)"

    raw = (first - second + c_deg) % 360.0
    # Per Tajika Neelakanthi: if C is not between B (second) and A (first) along zodiacal order, add 30 degrees.
    if not _is_on_zodiacal_arc(second, first, c_deg):
        raw = (raw + 30.0) % 360.0
        label += " + 30 deg"
    return raw, label


def compute_tajika_sahams(
    planet_lons: Mapping[str, float],
    varsha_asc_lon_deg: float,
    *,
    is_day_birth: bool = True,
) -> Mapping[str, TajikaSahamEntry]:
    """Compute 25 classical Tajika Sahams (sensitive points) from *Tajika Neelakanthi*."""

    asc = _norm360(varsha_asc_lon_deg)
    asc_sign = int(asc // 30.0)

    lons = {b: _norm360(planet_lons[b]) for b in SEVEN_PLANETS}

    def house_cusp(house_num: int) -> float:
        return ((asc_sign + house_num - 1) % 12) * 30.0 + (asc % 30.0)

    def house_lord_lon(house_num: int) -> float:
        sign_idx = (asc_sign + house_num - 1) % 12
        return lons[RASI_LORDS[sign_idx]]

    punya_lon, punya_label = _eval_saham_formula(
        lons["moon"], lons["sun"], asc, reverse_at_night=True, is_day_birth=is_day_birth
    )
    vidya_lon, vidya_label = _eval_saham_formula(
        lons["sun"], lons["moon"], asc, reverse_at_night=True, is_day_birth=is_day_birth
    )

    # 25 canonical Tajika Sahams: (key, Sanskrit Name, Signification, A, B, C, reverse_at_night)
    specs: tuple[tuple[str, str, str, float, float, float, bool], ...] = (
        ("punya", "Punya Saham", "Fortune and merit", lons["moon"], lons["sun"], asc, True),
        ("vidya", "Vidya Saham", "Knowledge and learning", lons["sun"], lons["moon"], asc, True),
        ("yasas", "Yasas Saham", "Fame and reputation", lons["jupiter"], punya_lon, asc, True),
        ("mitra", "Mitra Saham", "Friends and alliances", lons["jupiter"], punya_lon, lons["venus"], True),
        ("mahatmya", "Mahatmya Saham", "Greatness and eminence", punya_lon, lons["mars"], asc, True),
        ("asha", "Asha Saham", "Desires and expectations", lons["saturn"], lons["venus"], asc, True),
        ("samarthya", "Samarthya Saham", "Enterprise and capability", lons["mars"], house_lord_lon(1), asc, True),
        ("bhratri", "Bhratri Saham", "Brothers and siblings", lons["jupiter"], lons["saturn"], asc, False),
        ("gaurava", "Gaurava Saham", "Respect and honor", lons["sun"], lons["moon"], lons["jupiter"], True),
        ("pitri", "Pitri Saham", "Father and ancestry", lons["saturn"], lons["sun"], asc, True),
        ("matri", "Matri Saham", "Mother and nourishment", lons["moon"], lons["venus"], asc, True),
        ("putra", "Putra Saham", "Children and progeny", lons["jupiter"], lons["moon"], asc, True),
        ("jeeva", "Jeeva Saham", "Vitality and longevity", lons["saturn"], lons["jupiter"], asc, True),
        ("karma", "Karma Saham", "Action and vocation", lons["mars"], lons["mercury"], asc, True),
        ("roga", "Roga Saham", "Illness and vulnerability", asc, lons["moon"], asc, False),
        ("kali", "Kali Saham", "Strife and adversity", lons["jupiter"], lons["mars"], asc, True),
        ("sastra", "Sastra Saham", "Scriptures and sciences", lons["jupiter"], lons["saturn"], lons["mercury"], True),
        ("bandhu", "Bandhu Saham", "Relatives and kin", lons["mercury"], lons["moon"], asc, False),
        ("mrityu", "Mrityu Saham", "Danger and mortality", house_cusp(8), lons["moon"], asc, False),
        ("paradesa", "Paradesa Saham", "Foreign travel and residence", house_cusp(9), house_lord_lon(9), asc, False),
        ("artha", "Artha Saham", "Wealth and treasury", house_cusp(2), house_lord_lon(2), asc, False),
        ("paradara", "Paradara Saham", "Romantic attachment", lons["venus"], lons["sun"], asc, False),
        ("vanijya", "Vanijya Saham", "Trade and commerce", lons["moon"], lons["mercury"], asc, False),
        ("vivaha", "Vivaha Saham", "Marriage and partnership", lons["venus"], lons["saturn"], asc, False),
        ("raja", "Raja Saham", "Authority and sovereignty", lons["saturn"], lons["sun"], asc, True),
    )

    out: dict[str, TajikaSahamEntry] = {}
    for key, s_name, desc, a_val, b_val, c_val, rev in specs:
        if key == "punya":
            s_lon, f_label = punya_lon, punya_label
        elif key == "vidya":
            s_lon, f_label = vidya_lon, vidya_label
        else:
            s_lon, f_label = _eval_saham_formula(
                a_val, b_val, c_val, reverse_at_night=rev, is_day_birth=is_day_birth
            )
        r_idx = int(s_lon // 30.0)
        out[key] = TajikaSahamEntry(
            name=key,
            sanskrit_name=s_name,
            signification=desc,
            longitude_deg=round(s_lon, 8),
            rasi_index=r_idx,
            rasi_name=RASI_NAMES[r_idx],
            degree_in_rasi=round(s_lon - r_idx * 30.0, 8),
            lord=RASI_LORDS[r_idx],
            formula_used=f_label,
        )
    return out
