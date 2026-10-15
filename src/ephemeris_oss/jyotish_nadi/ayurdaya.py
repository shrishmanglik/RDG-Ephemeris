"""Classical Mathematical Longevity (Ayurdaya): Pindayu, Nisargayu, and Amsayu Engine.

Implements the three canonical mathematical longevity (*Ayurdaya*) systems of
*Brihat Parashara Hora Shastra* (Chapter 43), Varahamihira's *Brihat Jataka*
(Chapter 7, *Ayurdaya Adhyaya*), and Satyacharya's *Amsayu* doctrine:
1. **Pindayu**:
   - Maximum planetary years at deep exaltation:
     ``Sun 19, Moon 25, Mars 15, Mercury 12, Jupiter 15, Venus 21, Saturn 20`` (sum = 127).
   - Reduced linearly by angular distance from deep exaltation on ``[0, 180]`` so that
     deep exaltation yields 100% of maximum years and deep debilitation yields 50% (half)
     of maximum years.
   - Applies classical *Shatru Kshetra* (enemy sign 1/3 reduction), *Astangata*
     (combustion halving, with Venus and Saturn exempt), *Chakrapata* (visible hemisphere
     7th to 12th house reductions: ``12th: 100%, 11th: 1/2, 10th: 1/3, 9th: 1/4,
     8th: 1/5, 7th: 1/6`` for malefics and half those fractions for benefics), and
     *Krurodaya* (Lagna reduction when a malefic rises in the 1st house).
2. **Nisargayu**:
   - Uses the Naisargika maximum planetary years:
     ``Sun 20, Moon 1, Mars 2, Mercury 9, Jupiter 18, Venus 20, Saturn 50`` (sum = 120)
     under the identical algorithmic pipeline.
3. **Amsayu (Navamsa Longevity)**:
   - Converts each body's sidereal longitude to arcminutes (``total_arcmin = lon_deg * 60.0``),
     divides by ``200.0`` (one Navamsa = 3 deg 20 min = 200 arcminutes), takes the
     remainder modulo ``12.0`` as raw years, and applies classical *Bharana* multipliers
     (trebling for exaltation/retrograde, doubling for own Rasi/Navamsa/Drekkana or
     Vargottama per the single-highest multiplier rule *Bahugunane pradhanyam*) and
     classical reductions.
4. **Primary System Recommendation**:
   - Selects the primary longevity system based on the strongest of Sun (``Pindayu``),
     Moon (``Nisargayu``), or Lagna (``Amsayu``).
"""

from __future__ import annotations

from dataclasses import dataclass
import math
from typing import Final, Mapping, Sequence

from ..engine.receipt import canonical_hash
from ..jyotish.nakshatra import RASI_NAMES
from ..jyotish.vargas import RASI_LORDS
from ..jyotish_advanced.varshphal import (
    DEBILITATION_SIGN,
    DEEP_EXALTATION_DEG,
    EXALTATION_SIGN,
    NAISARGIKA_ENEMIES,
    NAISARGIKA_FRIENDS,
    OWN_SIGNS,
    SEVEN_PLANETS,
)

PINDAYU_MAX_YEARS: Final[Mapping[str, float]] = {
    "sun": 19.0,
    "moon": 25.0,
    "mars": 15.0,
    "mercury": 12.0,
    "jupiter": 15.0,
    "venus": 21.0,
    "saturn": 20.0,
}

NISARGAYU_MAX_YEARS: Final[Mapping[str, float]] = {
    "sun": 20.0,
    "moon": 1.0,
    "mars": 2.0,
    "mercury": 9.0,
    "jupiter": 18.0,
    "venus": 20.0,
    "saturn": 50.0,
}

# Classical combustion orbs (in degrees from Sun) per Surya Siddhanta / BPHS.
COMBUSTION_ORBS_DEG: Final[Mapping[str, float]] = {
    "moon": 12.0,
    "mars": 17.0,
    "mercury": 14.0,
    "jupiter": 11.0,
    "venus": 10.0,
    "saturn": 15.0,
}

# Base Chakrapata reduction fractions for malefics in houses 7..12.
CHAKRAPATA_MALEFIC_FRACTIONS: Final[Mapping[int, float]] = {
    12: 1.0,
    11: 1.0 / 2.0,
    10: 1.0 / 3.0,
    9: 1.0 / 4.0,
    8: 1.0 / 5.0,
    7: 1.0 / 6.0,
}

AYURDAYA_BENEFICS: Final[frozenset[str]] = frozenset({"moon", "mercury", "jupiter", "venus"})
AYURDAYA_MALEFICS: Final[frozenset[str]] = frozenset({"sun", "mars", "saturn", "rahu", "ketu"})


def _norm360(lon_deg: float) -> float:
    val = float(lon_deg)
    if not math.isfinite(val):
        raise ValueError("longitude must be a finite float")
    return val % 360.0


def _angular_separation_deg(a_deg: float, b_deg: float) -> float:
    diff = (float(a_deg) - float(b_deg)) % 360.0
    return diff if diff <= 180.0 else 360.0 - diff


def chakrapata_reduction_fraction(house_from_lagna: int, is_malefic: bool) -> float:
    """Return the classical Chakrapata reduction fraction for a planet in ``house_from_lagna`` (1..12).

    Houses 1..6 (invisible hemisphere) suffer zero reduction (``0.0``).
    Houses 7..12 (visible hemisphere) suffer:
    - Malefics: ``12th: 1.0, 11th: 1/2, 10th: 1/3, 9th: 1/4, 8th: 1/5, 7th: 1/6``
    - Benefics: half of the malefic reduction (``1/2, 1/4, 1/6, 1/8, 1/10, 1/12``).
    """
    if house_from_lagna < 1 or house_from_lagna > 12:
        raise ValueError(f"house_from_lagna must be in 1..12, got {house_from_lagna}")
    base = CHAKRAPATA_MALEFIC_FRACTIONS.get(house_from_lagna, 0.0)
    if base == 0.0:
        return 0.0
    return base if is_malefic else 0.5 * base


def astangata_reduction_fraction(planet: str, planet_lon_deg: float, sun_lon_deg: float) -> tuple[bool, float]:
    """Return ``(is_combust, reduction_fraction)`` for Astangata Harana.

    Venus and Saturn are exempt from Astangata halving per *Brihat Jataka* 7.2 and *BPHS*.
    """
    p_name = str(planet).strip().lower()
    if p_name == "sun" or p_name not in COMBUSTION_ORBS_DEG:
        return (False, 0.0)
    sep = _angular_separation_deg(planet_lon_deg, sun_lon_deg)
    combust = sep <= COMBUSTION_ORBS_DEG[p_name]
    if not combust:
        return (False, 0.0)
    if p_name in {"venus", "saturn"}:
        return (True, 0.0)
    return (True, 0.5)


def shatru_kshetra_reduction_fraction(
    planet: str,
    sign_index: int,
    is_retrograde: bool = False,
) -> float:
    """Return the classical 1/3 enemy-sign reduction fraction (0.0 if exempt or not in enemy sign)."""
    p_name = str(planet).strip().lower()
    if p_name not in SEVEN_PLANETS:
        return 0.0
    if is_retrograde or sign_index == EXALTATION_SIGN[p_name] or sign_index in OWN_SIGNS[p_name]:
        return 0.0
    sign_lord = RASI_LORDS[sign_index].lower()
    if sign_lord in NAISARGIKA_ENEMIES[p_name]:
        return 1.0 / 3.0
    return 0.0


def amsayu_bharana_multiplier(
    planet: str,
    lon_deg: float,
    is_retrograde: bool = False,
) -> tuple[float, tuple[str, ...]]:
    """Compute Satyacharya's Amsayu Bharana multiplier (1.0, 2.0, or 3.0) and reasons.

    Following *Brihat Jataka* 7.9-11 (*Bahugunane pradhanyam*):
    - Trebled (``3.0``) if exalted in Rasi or retrograde.
    - Doubled (``2.0``) if in Own Rasi, Own Navamsa, Own Drekkana, or Vargottama.
    - When multiple multipliers apply, only the highest single multiplier is applied.
    """
    p_name = str(planet).strip().lower()
    lon = _norm360(lon_deg)
    sign_idx = int(lon // 30.0) % 12
    d9_sign = int(lon / (10.0 / 3.0)) % 12
    dec_idx = int((lon % 30.0) // 10.0) % 3
    d3_sign = (sign_idx + dec_idx * 4) % 12

    reasons: list[str] = []
    multiplier = 1.0

    if p_name in EXALTATION_SIGN and sign_idx == EXALTATION_SIGN[p_name]:
        reasons.append("exalted_rasi_x3")
        multiplier = max(multiplier, 3.0)
    if is_retrograde and p_name not in {"sun", "moon"}:
        reasons.append("retrograde_x3")
        multiplier = max(multiplier, 3.0)
    if p_name in OWN_SIGNS and sign_idx in OWN_SIGNS[p_name]:
        reasons.append("own_rasi_x2")
        multiplier = max(multiplier, 2.0)
    if p_name in OWN_SIGNS and d9_sign in OWN_SIGNS[p_name]:
        reasons.append("own_navamsa_x2")
        multiplier = max(multiplier, 2.0)
    if p_name in OWN_SIGNS and d3_sign in OWN_SIGNS[p_name]:
        reasons.append("own_drekkana_x2")
        multiplier = max(multiplier, 2.0)
    if sign_idx == d9_sign:
        reasons.append("vargottama_x2")
        multiplier = max(multiplier, 2.0)

    return (multiplier, tuple(reasons))


@dataclass(frozen=True)
class PlanetAyurdayaBreakdown:
    """Per-planet calculation breakdown for Pindayu, Nisargayu, or Amsayu."""

    planet: str
    longitude_deg: float
    sign_index: int
    sign_name: str
    house_from_lagna: int
    max_years: float
    distance_from_exaltation_deg: float
    raw_years: float
    bharana_multiplier: float
    bharana_reasons: tuple[str, ...]
    multiplied_years: float
    shatru_reduction_fraction: float
    is_combust: bool
    astangata_reduction_fraction: float
    chakrapata_reduction_fraction: float
    net_years: float


@dataclass(frozen=True)
class KrurodayaReport:
    """Lagna Ayus and Krurodaya (malefic rising) reduction breakdown."""

    lagna_lon_deg: float
    lagna_sign_index: int
    lagna_sign_name: str
    lagna_degree_in_sign: float
    lagna_raw_years: float
    malefics_in_lagna: tuple[str, ...]
    benefics_protecting_lagna: tuple[str, ...]
    krurodaya_active: bool
    krurodaya_reduction_fraction: float
    krurodaya_reduction_years: float
    lagna_net_years: float


@dataclass(frozen=True)
class AyurdayaSystemResult:
    """Result for a single Ayurdaya system (Pindayu, Nisargayu, or Amsayu)."""

    system_name: str
    planet_breakdowns: Mapping[str, PlanetAyurdayaBreakdown]
    krurodaya: KrurodayaReport
    total_raw_years: float
    total_planet_net_years: float
    lagna_net_years: float
    total_net_years: float


@dataclass(frozen=True)
class AyurdayaReport:
    """Unified classical Ayurdaya report across Pindayu, Nisargayu, and Amsayu."""

    pindayu_years: float
    nisargayu_years: float
    amsayu_years: float
    pindayu: AyurdayaSystemResult
    nisargayu: AyurdayaSystemResult
    amsayu: AyurdayaSystemResult
    anchor_strengths: Mapping[str, float]
    strongest_anchor: str
    recommended_system: str
    recommended_years: float
    longevity_tier: str
    receipt_sha256: str


def _validate_seven_planets(planet_longitudes: Mapping[str, float]) -> dict[str, float]:
    normalized: dict[str, float] = {}
    for raw_k, raw_v in planet_longitudes.items():
        k = str(raw_k).strip().lower()
        normalized[k] = _norm360(raw_v)
    missing = [p for p in SEVEN_PLANETS if p not in normalized]
    if missing:
        raise ValueError(f"planet_longitudes missing required planets: {', '.join(missing)}")
    return normalized


def _evaluate_krurodaya(
    lagna_lon: float,
    normalized_planets: Mapping[str, float],
    apply_reduction: bool = True,
) -> KrurodayaReport:
    lagna_sign = int(lagna_lon // 30.0) % 12
    deg_in_sign = lagna_lon % 30.0
    # Raw Lagna years in Pindayu/Nisargayu = Navamsas elapsed in the rising sign (0..9 years).
    lagna_raw_years = (deg_in_sign * 60.0) / 200.0

    malefics_in_lagna: list[str] = []
    benefics_protecting: list[str] = []

    for p_name, p_lon in sorted(normalized_planets.items()):
        p_sign = int(p_lon // 30.0) % 12
        if p_sign == lagna_sign:
            if p_name in AYURDAYA_MALEFICS:
                malefics_in_lagna.append(p_name)
            elif p_name in AYURDAYA_BENEFICS:
                benefics_protecting.append(p_name)
        elif p_name in AYURDAYA_BENEFICS:
            dist = ((lagna_sign - p_sign) % 12) + 1
            if dist == 7 or (p_name == "jupiter" and dist in {5, 9}):
                benefics_protecting.append(p_name)

    krurodaya_active = bool(malefics_in_lagna) and apply_reduction
    if krurodaya_active:
        base_frac = deg_in_sign / 30.0
        red_frac = 0.5 * base_frac if benefics_protecting else base_frac
    else:
        red_frac = 0.0

    red_years = lagna_raw_years * red_frac
    net_years = lagna_raw_years - red_years

    return KrurodayaReport(
        lagna_lon_deg=lagna_lon,
        lagna_sign_index=lagna_sign,
        lagna_sign_name=RASI_NAMES[lagna_sign],
        lagna_degree_in_sign=deg_in_sign,
        lagna_raw_years=lagna_raw_years,
        malefics_in_lagna=tuple(malefics_in_lagna),
        benefics_protecting_lagna=tuple(benefics_protecting),
        krurodaya_active=krurodaya_active,
        krurodaya_reduction_fraction=red_frac,
        krurodaya_reduction_years=red_years,
        lagna_net_years=net_years,
    )


def _compute_arc_based_system(
    system_name: str,
    max_years_table: Mapping[str, float],
    planet_longitudes: Mapping[str, float],
    lagna_lon_deg: float,
    retrograde_planets: Sequence[str] = (),
) -> AyurdayaSystemResult:
    normalized = _validate_seven_planets(planet_longitudes)
    lagna_lon = _norm360(lagna_lon_deg)
    lagna_sign = int(lagna_lon // 30.0) % 12
    retro_set = {str(p).strip().lower() for p in retrograde_planets}
    sun_lon = normalized["sun"]

    breakdowns: dict[str, PlanetAyurdayaBreakdown] = {}
    total_raw = 0.0
    total_planet_net = 0.0

    for p_name in SEVEN_PLANETS:
        p_lon = normalized[p_name]
        p_sign = int(p_lon // 30.0) % 12
        house = ((p_sign - lagna_sign) % 12) + 1
        max_y = max_years_table[p_name]

        exalt_deg = DEEP_EXALTATION_DEG[p_name]
        dist_exalt = _angular_separation_deg(p_lon, exalt_deg)
        # Linear interpolation: 100% of max_years at deep exaltation (dist=0),
        # 50% (half) of max_years at deep debilitation (dist=180).
        arc_factor = 1.0 - 0.5 * (dist_exalt / 180.0)
        raw_y = max_y * arc_factor

        is_retro = p_name in retro_set
        shatru_frac = shatru_kshetra_reduction_fraction(p_name, p_sign, is_retrograde=is_retro)
        is_combust, astangata_frac = astangata_reduction_fraction(p_name, p_lon, sun_lon)
        chakrapata_frac = chakrapata_reduction_fraction(house, is_malefic=(p_name in AYURDAYA_MALEFICS))

        net_y = raw_y * (1.0 - shatru_frac) * (1.0 - astangata_frac) * (1.0 - chakrapata_frac)

        total_raw += raw_y
        total_planet_net += net_y

        breakdowns[p_name] = PlanetAyurdayaBreakdown(
            planet=p_name,
            longitude_deg=p_lon,
            sign_index=p_sign,
            sign_name=RASI_NAMES[p_sign],
            house_from_lagna=house,
            max_years=max_y,
            distance_from_exaltation_deg=dist_exalt,
            raw_years=raw_y,
            bharana_multiplier=1.0,
            bharana_reasons=(),
            multiplied_years=raw_y,
            shatru_reduction_fraction=shatru_frac,
            is_combust=is_combust,
            astangata_reduction_fraction=astangata_frac,
            chakrapata_reduction_fraction=chakrapata_frac,
            net_years=net_y,
        )

    krurodaya = _evaluate_krurodaya(lagna_lon, normalized, apply_reduction=True)
    total_raw_with_lagna = total_raw + krurodaya.lagna_raw_years
    total_net = total_planet_net + krurodaya.lagna_net_years

    return AyurdayaSystemResult(
        system_name=system_name,
        planet_breakdowns=breakdowns,
        krurodaya=krurodaya,
        total_raw_years=total_raw_with_lagna,
        total_planet_net_years=total_planet_net,
        lagna_net_years=krurodaya.lagna_net_years,
        total_net_years=total_net,
    )


def compute_pindayu(
    planet_longitudes: Mapping[str, float],
    lagna_lon_deg: float,
    retrograde_planets: Sequence[str] = (),
) -> AyurdayaSystemResult:
    """Compute classical Pindayu longevity from the 7 grahas and Lagna."""
    return _compute_arc_based_system(
        system_name="Pindayu",
        max_years_table=PINDAYU_MAX_YEARS,
        planet_longitudes=planet_longitudes,
        lagna_lon_deg=lagna_lon_deg,
        retrograde_planets=retrograde_planets,
    )


def compute_nisargayu(
    planet_longitudes: Mapping[str, float],
    lagna_lon_deg: float,
    retrograde_planets: Sequence[str] = (),
) -> AyurdayaSystemResult:
    """Compute classical Nisargayu longevity from the 7 grahas and Lagna."""
    return _compute_arc_based_system(
        system_name="Nisargayu",
        max_years_table=NISARGAYU_MAX_YEARS,
        planet_longitudes=planet_longitudes,
        lagna_lon_deg=lagna_lon_deg,
        retrograde_planets=retrograde_planets,
    )


def compute_amsayu(
    planet_longitudes: Mapping[str, float],
    lagna_lon_deg: float,
    retrograde_planets: Sequence[str] = (),
) -> AyurdayaSystemResult:
    """Compute Satyacharya's Amsayu (Navamsa) longevity with Bharana multipliers and reductions."""
    normalized = _validate_seven_planets(planet_longitudes)
    lagna_lon = _norm360(lagna_lon_deg)
    lagna_sign = int(lagna_lon // 30.0) % 12
    retro_set = {str(p).strip().lower() for p in retrograde_planets}
    sun_lon = normalized["sun"]

    breakdowns: dict[str, PlanetAyurdayaBreakdown] = {}
    total_raw = 0.0
    total_planet_net = 0.0

    for p_name in SEVEN_PLANETS:
        p_lon = normalized[p_name]
        p_sign = int(p_lon // 30.0) % 12
        house = ((p_sign - lagna_sign) % 12) + 1

        total_arcmin = p_lon * 60.0
        raw_y = (total_arcmin / 200.0) % 12.0
        # If exact non-zero multiple of 12 Navamsas (40 deg), ensure minimum 1/12 year floor only if 0.
        is_retro = p_name in retro_set
        bharana_mult, bharana_reasons = amsayu_bharana_multiplier(p_name, p_lon, is_retrograde=is_retro)
        multiplied_y = raw_y * bharana_mult

        shatru_frac = shatru_kshetra_reduction_fraction(p_name, p_sign, is_retrograde=is_retro)
        is_combust, astangata_frac = astangata_reduction_fraction(p_name, p_lon, sun_lon)
        chakrapata_frac = chakrapata_reduction_fraction(house, is_malefic=(p_name in AYURDAYA_MALEFICS))

        net_y = multiplied_y * (1.0 - shatru_frac) * (1.0 - astangata_frac) * (1.0 - chakrapata_frac)

        exalt_deg = DEEP_EXALTATION_DEG[p_name]
        dist_exalt = _angular_separation_deg(p_lon, exalt_deg)

        total_raw += raw_y
        total_planet_net += net_y

        breakdowns[p_name] = PlanetAyurdayaBreakdown(
            planet=p_name,
            longitude_deg=p_lon,
            sign_index=p_sign,
            sign_name=RASI_NAMES[p_sign],
            house_from_lagna=house,
            max_years=12.0,
            distance_from_exaltation_deg=dist_exalt,
            raw_years=raw_y,
            bharana_multiplier=bharana_mult,
            bharana_reasons=bharana_reasons,
            multiplied_years=multiplied_y,
            shatru_reduction_fraction=shatru_frac,
            is_combust=is_combust,
            astangata_reduction_fraction=astangata_frac,
            chakrapata_reduction_fraction=chakrapata_frac,
            net_years=net_y,
        )

    # Lagna Amsayu contribution: (lagna_lon * 60 / 200) % 12, without Krurodaya reduction per Brihat Jataka 7.12.
    lagna_arcmin = lagna_lon * 60.0
    lagna_raw_amsa = (lagna_arcmin / 200.0) % 12.0
    lagna_d9_sign = int(lagna_lon / (10.0 / 3.0)) % 12
    lagna_mult = 2.0 if lagna_d9_sign == lagna_sign else 1.0
    lagna_net_amsa = lagna_raw_amsa * lagna_mult

    krurodaya_info = KrurodayaReport(
        lagna_lon_deg=lagna_lon,
        lagna_sign_index=lagna_sign,
        lagna_sign_name=RASI_NAMES[lagna_sign],
        lagna_degree_in_sign=lagna_lon % 30.0,
        lagna_raw_years=lagna_raw_amsa,
        malefics_in_lagna=(),
        benefics_protecting_lagna=(),
        krurodaya_active=False,
        krurodaya_reduction_fraction=0.0,
        krurodaya_reduction_years=0.0,
        lagna_net_years=lagna_net_amsa,
    )

    return AyurdayaSystemResult(
        system_name="Amsayu",
        planet_breakdowns=breakdowns,
        krurodaya=krurodaya_info,
        total_raw_years=total_raw + lagna_raw_amsa,
        total_planet_net_years=total_planet_net,
        lagna_net_years=lagna_net_amsa,
        total_net_years=total_planet_net + lagna_net_amsa,
    )


def _compute_anchor_strengths(
    normalized_planets: Mapping[str, float],
    lagna_lon: float,
) -> dict[str, float]:
    """Compute deterministic classical dignity + positional strength for Sun, Moon, and Lagna."""
    lagna_sign = int(lagna_lon // 30.0) % 12

    def _planet_score(p_name: str) -> float:
        p_lon = normalized_planets[p_name]
        p_sign = int(p_lon // 30.0) % 12
        d9_sign = int(p_lon / (10.0 / 3.0)) % 12
        house = ((p_sign - lagna_sign) % 12) + 1
        dist_exalt = _angular_separation_deg(p_lon, DEEP_EXALTATION_DEG[p_name])
        # Uchcha Bala component in [0, 60]
        uchcha_score = 60.0 * (1.0 - dist_exalt / 180.0)
        # Rasi dignity component
        if p_sign == EXALTATION_SIGN[p_name]:
            rasi_score = 30.0
        elif p_sign in OWN_SIGNS[p_name]:
            rasi_score = 25.0
        elif RASI_LORDS[p_sign].lower() in NAISARGIKA_FRIENDS[p_name]:
            rasi_score = 18.0
        elif p_sign == DEBILITATION_SIGN[p_name]:
            rasi_score = 2.0
        elif RASI_LORDS[p_sign].lower() in NAISARGIKA_ENEMIES[p_name]:
            rasi_score = 6.0
        else:
            rasi_score = 12.0
        # Navamsa & Vargottama bonus
        nav_score = 15.0 if (d9_sign == EXALTATION_SIGN[p_name] or d9_sign in OWN_SIGNS[p_name]) else 5.0
        if p_sign == d9_sign:
            nav_score += 10.0
        # House placement (Kendra / Trikona bonus)
        if house in {1, 4, 7, 10}:
            house_score = 15.0
        elif house in {5, 9}:
            house_score = 12.0
        elif house in {6, 8, 12}:
            house_score = 3.0
        else:
            house_score = 8.0
        return uchcha_score + rasi_score + nav_score + house_score

    sun_score = _planet_score("sun")
    moon_score = _planet_score("moon")

    lagna_lord = RASI_LORDS[lagna_sign].lower()
    lagna_lord_score = _planet_score(lagna_lord)
    lagna_d9_sign = int(lagna_lon / (10.0 / 3.0)) % 12
    vargottama_bonus = 15.0 if lagna_d9_sign == lagna_sign else 0.0
    benefic_in_lagna_bonus = sum(
        8.0 for b in AYURDAYA_BENEFICS if int(normalized_planets[b] // 30.0) % 12 == lagna_sign
    )
    lagna_score = lagna_lord_score + vargottama_bonus + benefic_in_lagna_bonus

    return {
        "sun": round(sun_score, 6),
        "moon": round(moon_score, 6),
        "lagna": round(lagna_score, 6),
    }


def _classify_longevity_tier(years: float) -> str:
    if years < 32.0:
        return "Alpayu"
    if years < 70.0:
        return "Madhyayu"
    if years <= 100.0:
        return "Purnayu"
    return "Dirghayu"


def compute_ayurdaya(
    planet_longitudes: Mapping[str, float],
    lagna_lon_deg: float,
    retrograde_planets: Sequence[str] = (),
    anchor_strength_overrides: Mapping[str, float] | None = None,
) -> AyurdayaReport:
    """Compute Pindayu, Nisargayu, and Amsayu longevity and select the primary system.

    Parameters
    ----------
    planet_longitudes:
        Mapping of at least the 7 classical grahas (``sun``, ``moon``, ``mars``,
        ``mercury``, ``jupiter``, ``venus``, ``saturn``) to sidereal longitudes in degrees.
    lagna_lon_deg:
        Sidereal longitude of Lagna in degrees ``[0, 360)``.
    retrograde_planets:
        Optional sequence of retrograde planet names.
    anchor_strength_overrides:
        Optional explicit strength scores for ``{"sun": ..., "moon": ..., "lagna": ...}``
        to determine whether Sun (``Pindayu``), Moon (``Nisargayu``), or Lagna (``Amsayu``)
        is strongest.
    """
    normalized = _validate_seven_planets(planet_longitudes)
    lagna_lon = _norm360(lagna_lon_deg)

    pindayu_res = compute_pindayu(normalized, lagna_lon, retrograde_planets=retrograde_planets)
    nisargayu_res = compute_nisargayu(normalized, lagna_lon, retrograde_planets=retrograde_planets)
    amsayu_res = compute_amsayu(normalized, lagna_lon, retrograde_planets=retrograde_planets)

    if anchor_strength_overrides is not None:
        strengths = {
            "sun": float(anchor_strength_overrides.get("sun", 0.0)),
            "moon": float(anchor_strength_overrides.get("moon", 0.0)),
            "lagna": float(anchor_strength_overrides.get("lagna", 0.0)),
        }
    else:
        strengths = _compute_anchor_strengths(normalized, lagna_lon)

    # Deterministic tie-breaking priority: lagna, sun, moon if exact tie, otherwise strictly max.
    anchor_priority = ("sun", "moon", "lagna")
    strongest_anchor = max(anchor_priority, key=lambda k: (strengths[k], -anchor_priority.index(k)))

    system_map = {
        "sun": ("Pindayu", pindayu_res.total_net_years),
        "moon": ("Nisargayu", nisargayu_res.total_net_years),
        "lagna": ("Amsayu", amsayu_res.total_net_years),
    }
    rec_system, rec_years = system_map[strongest_anchor]
    tier = _classify_longevity_tier(rec_years)

    receipt = canonical_hash(
        {
            "engine": "ayurdaya",
            "lagna_lon_deg": round(lagna_lon, 9),
            "planets": {k: round(normalized[k], 9) for k in SEVEN_PLANETS},
            "retrograde": sorted(str(p).strip().lower() for p in retrograde_planets),
            "pindayu_years": round(pindayu_res.total_net_years, 9),
            "nisargayu_years": round(nisargayu_res.total_net_years, 9),
            "amsayu_years": round(amsayu_res.total_net_years, 9),
            "strongest_anchor": strongest_anchor,
            "recommended_system": rec_system,
        }
    )

    return AyurdayaReport(
        pindayu_years=pindayu_res.total_net_years,
        nisargayu_years=nisargayu_res.total_net_years,
        amsayu_years=amsayu_res.total_net_years,
        pindayu=pindayu_res,
        nisargayu=nisargayu_res,
        amsayu=amsayu_res,
        anchor_strengths=strengths,
        strongest_anchor=strongest_anchor,
        recommended_system=rec_system,
        recommended_years=rec_years,
        longevity_tier=tier,
        receipt_sha256=receipt,
    )


evaluate_ayurdaya = compute_ayurdaya


__all__ = [
    "AYURDAYA_BENEFICS",
    "AYURDAYA_MALEFICS",
    "AyurdayaReport",
    "AyurdayaSystemResult",
    "CHAKRAPATA_MALEFIC_FRACTIONS",
    "COMBUSTION_ORBS_DEG",
    "KrurodayaReport",
    "NISARGAYU_MAX_YEARS",
    "PINDAYU_MAX_YEARS",
    "PlanetAyurdayaBreakdown",
    "amsayu_bharana_multiplier",
    "astangata_reduction_fraction",
    "chakrapata_reduction_fraction",
    "compute_amsayu",
    "compute_ayurdaya",
    "compute_nisargayu",
    "compute_pindayu",
    "evaluate_ayurdaya",
    "shatru_kshetra_reduction_fraction",
]
