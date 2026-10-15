"""Clean-room Classical Birth-Time Rectification (Kala Shodhana) Engine.

Mathematical formulations follow *Brihat Parashara Hora Shastra* (BPHS Chapters 3, 4, 6),
*Prashna Marga* (Chapter 5), *Nashta Jataka*, *Saravali*, and *Surya Siddhanta*:
- Kunda Shuddhi (81x harmonic of the Ascendant: `kunda_lon = (lagna_lon * 81) % 360`):
  - Rasi alignment: Kunda sign falls in trine (1st, 5th, 9th) or 7th from natal Moon sign.
  - Nakshatra alignment: Kunda Nakshatra (`0..26`) is ruled by the same Vimshottari lord
    as either the natal Moon Nakshatra or the natal Lagna Nakshatra (`Janma`, `Anujanma`,
    `Trijanma`).
  - Exact angular and temporal distance in seconds to the nearest Kunda-valid interval.
- Pranapada Shuddhi (*Brihat Parashara Hora Shastra* Chapter 3):
  - Pranapada Lagna from solar longitude and elapsed vighatis since local sunrise.
  - Human-birth rectification rule: Pranapada sign in trine (1, 5, 9) or 7th from Moon sign
    or Lagna sign, or Pranapada Navamsa (`D9`) ruled by Jupiter, Mercury, Venus, or Moon.
- Pancha Tattwa & Antara Tattwa Engine:
  - 90-minute (1.5-hour) elemental cycle (`Prithvi 6 min, Jala 12 min, Tejas 18 min,
    Vayu 24 min, Akasha 30 min`) alternating `Aroha` (forward) and `Avaroha` (reverse)
    from local sunrise, with proportional Antara Tattwa sub-periods and weekday harmony.
- Multi-Criterion Birth-Time Rectification (`rectify_birth_time`):
  - Scans `[nominal_jd_ut - window, nominal_jd_ut + window]` at `step_seconds` increments,
    scoring candidates (`0..100`) across Kunda Shuddhi (`35 pts`), Pranapada Shuddhi (`30 pts`),
    Pancha Tattwa compatibility (`15 pts`), proximity to recorded time (`10 pts`), and
    life-event Dasha/Varga correlation (`10 pts`), while detecting every `D1, D9, D10, D60`
    cusp transition within the uncertainty window.
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Any, Final, Mapping, Sequence

from .._version import __version__
from ..engine.receipt import canonical_hash
from ..jyotish.dasha import compute_vimshottari_dasha
from ..jyotish.nakshatra import (
    NAKSHATRA_CATALOG,
    NAKSHATRA_SPAN_DEG,
    PADA_SPAN_DEG,
    RASI_NAMES,
    NakshatraPosition,
    nakshatra_position,
    normalize_degrees,
)
from ..jyotish.panchanga import VARA_CATALOG, compute_vara
from ..jyotish.vargas import RASI_LORDS, pranapada_lagna, varga_sign

SIDEREAL_DAY_SECONDS: Final[float] = 86164.0905
LAGNA_DEG_PER_SECOND: Final[float] = 360.0 / SIDEREAL_DAY_SECONDS
LAGNA_DEG_PER_DAY: Final[float] = 86400.0 * LAGNA_DEG_PER_SECOND
MOON_DEG_PER_DAY: Final[float] = 13.176358
MOON_DEG_PER_SECOND: Final[float] = MOON_DEG_PER_DAY / 86400.0

KUNDA_HARMONIC_FACTOR: Final[float] = 81.0
KUNDA_DEG_PER_SECOND: Final[float] = KUNDA_HARMONIC_FACTOR * LAGNA_DEG_PER_SECOND

PRANAPADA_DEG_PER_HOUR: Final[float] = 300.0
PRANAPADA_DEG_PER_SECOND: Final[float] = PRANAPADA_DEG_PER_HOUR / 3600.0

SHUDDHI_HOUSE_OFFSETS: Final[frozenset[int]] = frozenset({0, 4, 6, 8})  # 1st, 5th, 7th, 9th
BENEFIC_PRANAPADA_NAVAMSA_LORDS: Final[frozenset[str]] = frozenset(
    {"Jupiter", "Mercury", "Venus", "Moon"}
)

RECTIFICATION_VARGA_KEYS: Final[tuple[str, ...]] = ("D1", "D9", "D10", "D60")
VARGA_DIVISION_FACTORS: Final[Mapping[str, int]] = {
    "D1": 1,
    "D9": 9,
    "D10": 10,
    "D60": 60,
}


@dataclass(frozen=True)
class TattwaDefinition:
    """Static attributes of one of the five classical Pancha Tattwas."""

    index: int
    name: str
    sanskrit_name: str
    element: str
    duration_minutes: float
    polarity: str
    gender: str
    nature: str
    primary_ruler: str
    ruling_planets: tuple[str, ...]


PANCHA_TATTWA_CATALOG: Final[tuple[TattwaDefinition, ...]] = (
    TattwaDefinition(
        index=0,
        name="Prithvi",
        sanskrit_name="Prithvi",
        element="Earth",
        duration_minutes=6.0,
        polarity="Positive",
        gender="Male",
        nature="Saumya",
        primary_ruler="Mercury",
        ruling_planets=("Mercury",),
    ),
    TattwaDefinition(
        index=1,
        name="Jala",
        sanskrit_name="Jala",
        element="Water",
        duration_minutes=12.0,
        polarity="Negative",
        gender="Female",
        nature="Saumya",
        primary_ruler="Moon",
        ruling_planets=("Moon", "Venus"),
    ),
    TattwaDefinition(
        index=2,
        name="Tejas",
        sanskrit_name="Tejas",
        element="Fire",
        duration_minutes=18.0,
        polarity="Positive",
        gender="Male",
        nature="Krura",
        primary_ruler="Sun",
        ruling_planets=("Sun", "Mars"),
    ),
    TattwaDefinition(
        index=3,
        name="Vayu",
        sanskrit_name="Vayu",
        element="Air",
        duration_minutes=24.0,
        polarity="Negative",
        gender="Female",
        nature="Krura",
        primary_ruler="Saturn",
        ruling_planets=("Saturn",),
    ),
    TattwaDefinition(
        index=4,
        name="Akasha",
        sanskrit_name="Akasha",
        element="Ether",
        duration_minutes=30.0,
        polarity="Neutral",
        gender="Neutral",
        nature="Saumya",
        primary_ruler="Jupiter",
        ruling_planets=("Jupiter",),
    ),
)

TATTWA_CYCLE_MINUTES: Final[float] = 90.0

# Natural Tattwa affinity for each weekday index (0=Sunday .. 6=Saturday)
WEEKDAY_NATURAL_TATTWA: Final[tuple[str, ...]] = (
    "Tejas",    # 0 Sunday (Sun)
    "Jala",     # 1 Monday (Moon)
    "Tejas",    # 2 Tuesday (Mars)
    "Prithvi",  # 3 Wednesday (Mercury)
    "Akasha",   # 4 Thursday (Jupiter)
    "Jala",     # 5 Friday (Venus)
    "Vayu",     # 6 Saturday (Saturn)
)

# Element mapping for the 12 Rasis (Fire, Earth, Air, Water repeating)
RASI_ELEMENTS: Final[tuple[str, ...]] = (
    "Fire",   # 0 Mesha
    "Earth",  # 1 Vrishabha
    "Air",    # 2 Mithuna
    "Water",  # 3 Karka
    "Fire",   # 4 Simha
    "Earth",  # 5 Kanya
    "Air",    # 6 Tula
    "Water",  # 7 Vrishchika
    "Fire",   # 8 Dhanu
    "Earth",  # 9 Makara
    "Air",    # 10 Kumbha
    "Water",  # 11 Meena
)

EVENT_CATEGORY_DEFAULTS: Final[Mapping[str, tuple[str, int]]] = {
    "marriage": ("D9", 7),
    "partnership": ("D9", 7),
    "career": ("D10", 10),
    "profession": ("D10", 10),
    "promotion": ("D10", 10),
    "childbirth": ("D9", 5),
    "children": ("D9", 5),
    "education": ("D9", 4),
    "property": ("D1", 4),
    "health": ("D60", 6),
    "longevity": ("D60", 8),
    "spirituality": ("D60", 9),
    "general": ("D1", 1),
}


@dataclass(frozen=True)
class KundaEvaluation:
    """Classical Kunda (81x Ascendant harmonic) rectification assessment."""

    lagna_lon_deg: float
    moon_lon_deg: float
    kunda_lon_deg: float
    kunda_sign_index: int
    kunda_sign_name: str
    moon_sign_index: int
    moon_sign_name: str
    lagna_sign_index: int
    lagna_sign_name: str
    house_from_moon: int
    rasi_trine_or_7th: bool
    kunda_nakshatra_index: int
    kunda_nakshatra_name: str
    kunda_nakshatra_ruler: str
    moon_nakshatra_index: int
    moon_nakshatra_name: str
    moon_nakshatra_ruler: str
    lagna_nakshatra_index: int
    lagna_nakshatra_name: str
    lagna_nakshatra_ruler: str
    matches_moon_nakshatra_ruler: bool
    matches_lagna_nakshatra_ruler: bool
    nakshatra_alignment: bool
    is_shuddha: bool
    is_strict_shuddha: bool
    kunda_deg_to_nearest_valid: float
    lagna_deg_to_nearest_valid: float
    seconds_to_nearest_valid: float
    signed_seconds_to_nearest_valid: float
    seconds_to_nearest_rasi_valid: float
    seconds_to_nearest_nakshatra_valid: float
    seconds_to_nearest_strict_valid: float


@dataclass(frozen=True)
class PranapadaEvaluation:
    """Classical Pranapada Lagna Shuddhi assessment per *Brihat Parashara Hora Shastra*."""

    lagna_lon_deg: float
    sun_lon_deg: float
    moon_lon_deg: float
    hours_since_sunrise: float
    vighatis_since_sunrise: float
    pranapada_lon_deg: float
    pranapada_sign_index: int
    pranapada_sign_name: str
    pranapada_sign_lord: str
    pranapada_navamsa_sign_index: int
    pranapada_navamsa_sign_name: str
    pranapada_navamsa_lord: str
    house_from_moon: int
    house_from_lagna: int
    trine_or_7th_from_moon: bool
    trine_or_7th_from_lagna: bool
    rasi_trine_or_7th: bool
    benefic_navamsa: bool
    is_shuddha: bool
    is_strict_shuddha: bool
    seconds_to_nearest_valid: float
    signed_seconds_to_nearest_valid: float
    seconds_to_nearest_rasi_valid: float
    seconds_to_nearest_navamsa_valid: float
    seconds_to_nearest_strict_valid: float


@dataclass(frozen=True)
class AntaraTattwaPeriod:
    """Sub-period (Antara Tattwa) within a 90-minute Maha Tattwa cycle."""

    name: str
    element: str
    polarity: str
    gender: str
    primary_ruler: str
    ruling_planets: tuple[str, ...]
    start_minute_in_cycle: float
    end_minute_in_cycle: float
    duration_minutes: float


@dataclass(frozen=True)
class PanchaTattwaState:
    """Active Pancha Tattwa and Antara Tattwa state at a given offset from sunrise."""

    hours_since_sunrise: float
    minutes_since_sunrise: float
    weekday_index: int
    weekday_name: str
    weekday_lord: str
    weekday_natural_tattwa: str
    cycle_index: int
    cycle_number: int
    cycle_direction: str
    minute_in_cycle: float
    tattwa_index: int
    tattwa_name: str
    element: str
    polarity: str
    gender: str
    nature: str
    primary_ruler: str
    ruling_planets: tuple[str, ...]
    maha_start_minute_in_cycle: float
    maha_end_minute_in_cycle: float
    maha_duration_minutes: float
    maha_fraction_elapsed: float
    antara_tattwa: AntaraTattwaPeriod
    antara_sub_periods: tuple[AntaraTattwaPeriod, ...]
    weekday_compatible: bool


@dataclass(frozen=True)
class VargaCuspTransition:
    """A divisional chart (Varga) Ascendant sign or Shashtiamsa transition within the rectification window."""

    varga: str
    division_factor: int
    transition_jd_ut: float
    offset_seconds_from_nominal: float
    cusp_longitude_deg: float
    from_sign_index: int
    from_sign_name: str
    to_sign_index: int
    to_sign_name: str
    from_shashtiamsa_name: str | None = None
    to_shashtiamsa_name: str | None = None


@dataclass(frozen=True)
class LifeEventSpec:
    """Specification of a dated life event for birth-time rectification correlation."""

    name: str
    event_jd_ut: float | None = None
    category: str = "general"
    varga: str | None = None
    house: int | None = None
    signifying_planet: str | None = None
    expected_varga_lagna_sign: int | None = None


@dataclass(frozen=True)
class RectificationCandidate:
    """Single evaluated timestamp candidate inside the birth-time uncertainty window."""

    rank: int
    candidate_jd_ut: float
    offset_seconds: float
    offset_minutes: float
    lagna_lon_deg: float
    moon_lon_deg: float
    d1_lagna_sign_index: int
    d1_lagna_sign_name: str
    d9_lagna_sign_index: int
    d9_lagna_sign_name: str
    d10_lagna_sign_index: int
    d10_lagna_sign_name: str
    d60_lagna_sign_index: int
    d60_lagna_sign_name: str
    d60_shashtiamsa_name: str
    d60_shashtiamsa_is_benefic: bool
    total_score: float
    kunda_score: float
    pranapada_score: float
    tattwa_score: float
    proximity_score: float
    life_event_score: float
    kunda: KundaEvaluation
    pranapada: PranapadaEvaluation
    tattwa: PanchaTattwaState


@dataclass(frozen=True)
class BirthTimeRectificationReport:
    """Complete mathematical birth-time rectification report with SHA-256 receipt."""

    nominal_jd_ut: float
    sunrise_jd_ut: float
    rectified_jd_ut: float
    offset_seconds: float
    offset_minutes: float
    window_minutes: float
    step_seconds: float
    nominal_candidate: RectificationCandidate
    best_candidate: RectificationCandidate
    top_candidates: tuple[RectificationCandidate, ...]
    all_candidates: tuple[RectificationCandidate, ...]
    varga_transitions: tuple[VargaCuspTransition, ...]
    receipt: Mapping[str, Any]
    receipt_sha256: str


def _distance_to_pada_mask_deg(
    lon_deg: float,
    valid_padas: Sequence[bool],
) -> tuple[float, float]:
    """Return `(unsigned_distance_deg, signed_distance_deg)` from `lon_deg` in `[0, 360)`
    to the nearest valid pada interval `[p * 10/3, (p + 1) * 10/3)` where `valid_padas[p]` is True.
    """
    angle = normalize_degrees(lon_deg)
    current_pada = min(int(angle / PADA_SPAN_DEG), 107)
    if valid_padas[current_pada]:
        return 0.0, 0.0

    best_unsigned = 360.0
    best_signed = 0.0
    for p, is_valid in enumerate(valid_padas):
        if not is_valid:
            continue
        start_deg = p * PADA_SPAN_DEG
        end_deg = (p + 1) * PADA_SPAN_DEG
        forward_deg = (start_deg - angle) % 360.0
        backward_deg = (angle - end_deg) % 360.0
        if forward_deg < best_unsigned:
            best_unsigned = forward_deg
            best_signed = forward_deg
        if backward_deg < best_unsigned:
            best_unsigned = backward_deg
            best_signed = -backward_deg

    return best_unsigned, best_signed


def evaluate_kunda_shuddhi(
    lagna_lon_deg: float,
    moon_lon_deg: float,
) -> KundaEvaluation:
    """Evaluate classical *Prashna Marga* / *Brihat Parashara Hora Shastra* Kunda Shuddhi.

    - Kunda longitude = `(lagna_lon_deg * 81.0) % 360.0` (81x harmonic of the Ascendant).
    - `rasi_trine_or_7th`: Kunda sign (`0..11`) is in the 1st, 5th, 7th, or 9th house
      from the natal Moon sign (`0..11`).
    - `nakshatra_alignment`: Kunda Nakshatra (`0..26`) shares the same Vimshottari ruler
      as either the natal Moon Nakshatra or the natal Lagna Nakshatra (`Janma`, `Anujanma`,
      `Trijanma`).
    """
    l_lon = normalize_degrees(lagna_lon_deg)
    m_lon = normalize_degrees(moon_lon_deg)
    kunda_lon = normalize_degrees(l_lon * KUNDA_HARMONIC_FACTOR)

    kunda_sign = min(int(kunda_lon // 30.0), 11)
    moon_sign = min(int(m_lon // 30.0), 11)
    lagna_sign = min(int(l_lon // 30.0), 11)

    house_offset = (kunda_sign - moon_sign) % 12
    house_from_moon = house_offset + 1
    rasi_ok = house_offset in SHUDDHI_HOUSE_OFFSETS

    kunda_nak: NakshatraPosition = nakshatra_position(kunda_lon)
    moon_nak: NakshatraPosition = nakshatra_position(m_lon)
    lagna_nak: NakshatraPosition = nakshatra_position(l_lon)

    matches_moon_ruler = kunda_nak.vimshottari_ruler == moon_nak.vimshottari_ruler
    matches_lagna_ruler = kunda_nak.vimshottari_ruler == lagna_nak.vimshottari_ruler
    nak_ok = matches_moon_ruler or matches_lagna_ruler

    is_shuddha = rasi_ok or nak_ok
    is_strict = rasi_ok and nak_ok

    valid_rasi_set = {(moon_sign + off) % 12 for off in SHUDDHI_HOUSE_OFFSETS}
    valid_rulers = {moon_nak.vimshottari_ruler, lagna_nak.vimshottari_ruler}

    rasi_mask = [(p // 9) in valid_rasi_set for p in range(108)]
    nak_mask = [NAKSHATRA_CATALOG[p // 4].vimshottari_ruler in valid_rulers for p in range(108)]
    union_mask = [r or n for r, n in zip(rasi_mask, nak_mask)]
    strict_mask = [r and n for r, n in zip(rasi_mask, nak_mask)]

    kunda_deg_any, kunda_signed_deg_any = _distance_to_pada_mask_deg(kunda_lon, union_mask)
    kunda_deg_rasi, _ = _distance_to_pada_mask_deg(kunda_lon, rasi_mask)
    kunda_deg_nak, _ = _distance_to_pada_mask_deg(kunda_lon, nak_mask)
    kunda_deg_strict, _ = _distance_to_pada_mask_deg(kunda_lon, strict_mask)

    lagna_deg_any = kunda_deg_any / KUNDA_HARMONIC_FACTOR
    sec_any = kunda_deg_any / KUNDA_DEG_PER_SECOND
    signed_sec_any = kunda_signed_deg_any / KUNDA_DEG_PER_SECOND
    sec_rasi = kunda_deg_rasi / KUNDA_DEG_PER_SECOND
    sec_nak = kunda_deg_nak / KUNDA_DEG_PER_SECOND
    sec_strict = kunda_deg_strict / KUNDA_DEG_PER_SECOND

    return KundaEvaluation(
        lagna_lon_deg=l_lon,
        moon_lon_deg=m_lon,
        kunda_lon_deg=kunda_lon,
        kunda_sign_index=kunda_sign,
        kunda_sign_name=RASI_NAMES[kunda_sign],
        moon_sign_index=moon_sign,
        moon_sign_name=RASI_NAMES[moon_sign],
        lagna_sign_index=lagna_sign,
        lagna_sign_name=RASI_NAMES[lagna_sign],
        house_from_moon=house_from_moon,
        rasi_trine_or_7th=rasi_ok,
        kunda_nakshatra_index=kunda_nak.index,
        kunda_nakshatra_name=kunda_nak.name,
        kunda_nakshatra_ruler=kunda_nak.vimshottari_ruler,
        moon_nakshatra_index=moon_nak.index,
        moon_nakshatra_name=moon_nak.name,
        moon_nakshatra_ruler=moon_nak.vimshottari_ruler,
        lagna_nakshatra_index=lagna_nak.index,
        lagna_nakshatra_name=lagna_nak.name,
        lagna_nakshatra_ruler=lagna_nak.vimshottari_ruler,
        matches_moon_nakshatra_ruler=matches_moon_ruler,
        matches_lagna_nakshatra_ruler=matches_lagna_ruler,
        nakshatra_alignment=nak_ok,
        is_shuddha=is_shuddha,
        is_strict_shuddha=is_strict,
        kunda_deg_to_nearest_valid=round(kunda_deg_any, 8),
        lagna_deg_to_nearest_valid=round(lagna_deg_any, 8),
        seconds_to_nearest_valid=round(sec_any, 6),
        signed_seconds_to_nearest_valid=round(signed_sec_any, 6),
        seconds_to_nearest_rasi_valid=round(sec_rasi, 6),
        seconds_to_nearest_nakshatra_valid=round(sec_nak, 6),
        seconds_to_nearest_strict_valid=round(sec_strict, 6),
    )


def evaluate_pranapada_shuddhi(
    lagna_lon_deg: float,
    sun_lon_deg: float,
    moon_lon_deg: float,
    hours_since_sunrise: float,
) -> PranapadaEvaluation:
    """Evaluate *Brihat Parashara Hora Shastra* Pranapada Shuddhi for human-birth rectification.

    - Computes Pranapada Lagna from `sun_lon_deg` and `hours_since_sunrise`
      (`vighatis_since_sunrise = hours_since_sunrise * 150.0`, advancing 2.0 degrees per vighati
      from Sun if Movable, 9th from Sun if Fixed, or 5th from Sun if Dual).
    - Checks whether Pranapada sign lies in trine (`1, 5, 9`) or `7th` from the natal Moon
      sign or Lagna sign, or whether Pranapada Navamsa (`D9`) is ruled by Jupiter, Mercury,
      Venus, or Moon.
    """
    l_lon = normalize_degrees(lagna_lon_deg)
    s_lon = normalize_degrees(sun_lon_deg)
    m_lon = normalize_degrees(moon_lon_deg)
    hrs = float(hours_since_sunrise)
    vighatis = hrs * 150.0

    pp_lon = pranapada_lagna(s_lon, hrs)
    pp_sign = min(int(pp_lon // 30.0), 11)
    pp_d9 = varga_sign(pp_lon, "D9")

    lagna_sign = min(int(l_lon // 30.0), 11)
    moon_sign = min(int(m_lon // 30.0), 11)

    off_moon = (pp_sign - moon_sign) % 12
    off_lagna = (pp_sign - lagna_sign) % 12
    trine_7_moon = off_moon in SHUDDHI_HOUSE_OFFSETS
    trine_7_lagna = off_lagna in SHUDDHI_HOUSE_OFFSETS
    rasi_ok = trine_7_moon or trine_7_lagna
    navamsa_ok = pp_d9.sign_lord in BENEFIC_PRANAPADA_NAVAMSA_LORDS

    is_shuddha = rasi_ok or navamsa_ok
    is_strict = rasi_ok and navamsa_ok

    valid_rasi_set = {
        (moon_sign + off) % 12 for off in SHUDDHI_HOUSE_OFFSETS
    } | {
        (lagna_sign + off) % 12 for off in SHUDDHI_HOUSE_OFFSETS
    }
    rasi_mask = [(p // 9) in valid_rasi_set for p in range(108)]
    nav_mask = [RASI_LORDS[p % 12] in BENEFIC_PRANAPADA_NAVAMSA_LORDS for p in range(108)]
    union_mask = [r or n for r, n in zip(rasi_mask, nav_mask)]
    strict_mask = [r and n for r, n in zip(rasi_mask, nav_mask)]

    pp_deg_any, pp_signed_deg_any = _distance_to_pada_mask_deg(pp_lon, union_mask)
    pp_deg_rasi, _ = _distance_to_pada_mask_deg(pp_lon, rasi_mask)
    pp_deg_nav, _ = _distance_to_pada_mask_deg(pp_lon, nav_mask)
    pp_deg_strict, _ = _distance_to_pada_mask_deg(pp_lon, strict_mask)

    sec_any = pp_deg_any / PRANAPADA_DEG_PER_SECOND
    signed_sec_any = pp_signed_deg_any / PRANAPADA_DEG_PER_SECOND
    sec_rasi = pp_deg_rasi / PRANAPADA_DEG_PER_SECOND
    sec_nav = pp_deg_nav / PRANAPADA_DEG_PER_SECOND
    sec_strict = pp_deg_strict / PRANAPADA_DEG_PER_SECOND

    return PranapadaEvaluation(
        lagna_lon_deg=l_lon,
        sun_lon_deg=s_lon,
        moon_lon_deg=m_lon,
        hours_since_sunrise=hrs,
        vighatis_since_sunrise=vighatis,
        pranapada_lon_deg=pp_lon,
        pranapada_sign_index=pp_sign,
        pranapada_sign_name=RASI_NAMES[pp_sign],
        pranapada_sign_lord=RASI_LORDS[pp_sign],
        pranapada_navamsa_sign_index=pp_d9.sign_index,
        pranapada_navamsa_sign_name=pp_d9.sign_name,
        pranapada_navamsa_lord=pp_d9.sign_lord,
        house_from_moon=off_moon + 1,
        house_from_lagna=off_lagna + 1,
        trine_or_7th_from_moon=trine_7_moon,
        trine_or_7th_from_lagna=trine_7_lagna,
        rasi_trine_or_7th=rasi_ok,
        benefic_navamsa=navamsa_ok,
        is_shuddha=is_shuddha,
        is_strict_shuddha=is_strict,
        seconds_to_nearest_valid=round(sec_any, 6),
        signed_seconds_to_nearest_valid=round(signed_sec_any, 6),
        seconds_to_nearest_rasi_valid=round(sec_rasi, 6),
        seconds_to_nearest_navamsa_valid=round(sec_nav, 6),
        seconds_to_nearest_strict_valid=round(sec_strict, 6),
    )


def evaluate_pancha_tattwa(
    hours_since_sunrise: float,
    weekday_index: int,
) -> PanchaTattwaState:
    """Evaluate the classical 90-minute (`1.5-hour`) Pancha Tattwa and Antara Tattwa cycle.

    - Starting at local sunrise, each 90-minute cycle comprises:
      `Prithvi (6 min) -> Jala (12 min) -> Tejas (18 min) -> Vayu (24 min) -> Akasha (30 min)`
      in even cycles (`Aroha`, 0-indexed `0, 2, 4, ...`), and reverses to
      `Akasha (30 min) -> Vayu (24 min) -> Tejas (18 min) -> Jala (12 min) -> Prithvi (6 min)`
      in odd cycles (`Avaroha`, 0-indexed `1, 3, 5, ...`).
    - Within each Maha Tattwa, the 5 Antara Tattwas divide the Maha Tattwa duration
      proportionally (`6:12:18:24:30` out of `90`), starting from the active Maha Tattwa
      and following the current cycle direction.
    """
    if isinstance(weekday_index, bool) or not 0 <= int(weekday_index) <= 6:
        raise ValueError("weekday_index must be an integer in 0..6 (0=Sunday .. 6=Saturday)")
    w_idx = int(weekday_index)
    hrs = float(hours_since_sunrise)
    total_minutes = hrs * 60.0

    cycle_idx = int(math.floor(total_minutes / TATTWA_CYCLE_MINUTES))
    min_in_cycle = total_minutes - cycle_idx * TATTWA_CYCLE_MINUTES
    if min_in_cycle < 0.0 or min_in_cycle >= TATTWA_CYCLE_MINUTES:
        min_in_cycle = min_in_cycle % TATTWA_CYCLE_MINUTES

    is_aroha = (cycle_idx % 2) == 0
    direction = "Aroha" if is_aroha else "Avaroha"
    ordered_tattwas = PANCHA_TATTWA_CATALOG if is_aroha else tuple(reversed(PANCHA_TATTWA_CATALOG))

    cursor = 0.0
    active_maha = ordered_tattwas[-1]
    active_pos_in_seq = len(ordered_tattwas) - 1
    maha_start = 0.0
    maha_end = TATTWA_CYCLE_MINUTES

    for seq_idx, t_def in enumerate(ordered_tattwas):
        next_cursor = cursor + t_def.duration_minutes
        if min_in_cycle < next_cursor or seq_idx == len(ordered_tattwas) - 1:
            active_maha = t_def
            active_pos_in_seq = seq_idx
            maha_start = cursor
            maha_end = next_cursor
            break
        cursor = next_cursor

    maha_dur = active_maha.duration_minutes
    elapsed_in_maha = min(max(min_in_cycle - maha_start, 0.0), maha_dur)
    maha_frac = elapsed_in_maha / maha_dur if maha_dur > 0.0 else 0.0

    # Build the 5 proportional Antara Tattwa sub-periods starting with the active Maha Tattwa
    sub_cursor = maha_start
    sub_periods: list[AntaraTattwaPeriod] = []
    active_antara: AntaraTattwaPeriod | None = None

    for offset in range(5):
        sub_def = ordered_tattwas[(active_pos_in_seq + offset) % 5]
        sub_dur = maha_dur * (sub_def.duration_minutes / TATTWA_CYCLE_MINUTES)
        s_min = sub_cursor
        e_min = (maha_end if offset == 4 else sub_cursor + sub_dur)
        sub_cursor = e_min
        period = AntaraTattwaPeriod(
            name=sub_def.name,
            element=sub_def.element,
            polarity=sub_def.polarity,
            gender=sub_def.gender,
            primary_ruler=sub_def.primary_ruler,
            ruling_planets=sub_def.ruling_planets,
            start_minute_in_cycle=round(s_min, 8),
            end_minute_in_cycle=round(e_min, 8),
            duration_minutes=round(e_min - s_min, 8),
        )
        sub_periods.append(period)
        if active_antara is None and (min_in_cycle < e_min or offset == 4):
            active_antara = period

    assert active_antara is not None

    weekday_tattwa = WEEKDAY_NATURAL_TATTWA[w_idx]
    _, _, weekday_name, weekday_lord = VARA_CATALOG[w_idx]
    weekday_compatible = (
        active_maha.name == weekday_tattwa
        or active_antara.name == weekday_tattwa
        or weekday_lord in active_maha.ruling_planets
    )

    return PanchaTattwaState(
        hours_since_sunrise=hrs,
        minutes_since_sunrise=total_minutes,
        weekday_index=w_idx,
        weekday_name=weekday_name,
        weekday_lord=weekday_lord,
        weekday_natural_tattwa=weekday_tattwa,
        cycle_index=cycle_idx,
        cycle_number=cycle_idx + 1,
        cycle_direction=direction,
        minute_in_cycle=round(min_in_cycle, 8),
        tattwa_index=active_maha.index,
        tattwa_name=active_maha.name,
        element=active_maha.element,
        polarity=active_maha.polarity,
        gender=active_maha.gender,
        nature=active_maha.nature,
        primary_ruler=active_maha.primary_ruler,
        ruling_planets=active_maha.ruling_planets,
        maha_start_minute_in_cycle=round(maha_start, 8),
        maha_end_minute_in_cycle=round(maha_end, 8),
        maha_duration_minutes=maha_dur,
        maha_fraction_elapsed=round(maha_frac, 8),
        antara_tattwa=active_antara,
        antara_sub_periods=tuple(sub_periods),
        weekday_compatible=weekday_compatible,
    )


def _detect_varga_transitions(
    nominal_jd_ut: float,
    nominal_lagna_lon_deg: float,
    window_minutes: float,
) -> tuple[VargaCuspTransition, ...]:
    """Analytically locate every D1, D9, D10, and D60 Ascendant cusp transition inside
    `[nominal_jd_ut - window_minutes/1440, nominal_jd_ut + window_minutes/1440]`.
    """
    window_sec = float(window_minutes) * 60.0
    delta_deg = window_sec * LAGNA_DEG_PER_SECOND
    start_unwrapped = float(nominal_lagna_lon_deg) - delta_deg
    end_unwrapped = float(nominal_lagna_lon_deg) + delta_deg

    transitions: list[VargaCuspTransition] = []
    eps = 1e-7

    for varga_code in RECTIFICATION_VARGA_KEYS:
        n_div = VARGA_DIVISION_FACTORS[varga_code]
        step_deg = 30.0 / float(n_div)
        k_min = int(math.floor(start_unwrapped / step_deg)) + 1
        k_max = int(math.floor(end_unwrapped / step_deg))

        for k in range(k_min, k_max + 1):
            cusp_unwrapped = k * step_deg
            if not (start_unwrapped <= cusp_unwrapped <= end_unwrapped):
                continue
            offset_sec = (cusp_unwrapped - float(nominal_lagna_lon_deg)) / LAGNA_DEG_PER_SECOND
            trans_jd = float(nominal_jd_ut) + offset_sec / 86400.0
            before_pl = varga_sign(cusp_unwrapped - eps, varga_code)
            after_pl = varga_sign(cusp_unwrapped + eps, varga_code)
            if (
                before_pl.sign_index == after_pl.sign_index
                and before_pl.part_index == after_pl.part_index
                and before_pl.shashtiamsa_name == after_pl.shashtiamsa_name
            ):
                continue
            transitions.append(
                VargaCuspTransition(
                    varga=varga_code,
                    division_factor=n_div,
                    transition_jd_ut=round(trans_jd, 10),
                    offset_seconds_from_nominal=round(offset_sec, 6),
                    cusp_longitude_deg=round(normalize_degrees(cusp_unwrapped), 8),
                    from_sign_index=before_pl.sign_index,
                    from_sign_name=before_pl.sign_name,
                    to_sign_index=after_pl.sign_index,
                    to_sign_name=after_pl.sign_name,
                    from_shashtiamsa_name=before_pl.shashtiamsa_name,
                    to_shashtiamsa_name=after_pl.shashtiamsa_name,
                )
            )

    transitions.sort(key=lambda item: (item.offset_seconds_from_nominal, item.division_factor))
    return tuple(transitions)


def _normalize_life_event(item: Mapping[str, Any] | LifeEventSpec) -> LifeEventSpec:
    if isinstance(item, LifeEventSpec):
        return item
    if not isinstance(item, Mapping):
        raise TypeError(f"Each life_event must be a Mapping or LifeEventSpec, got {type(item).__name__}")
    cat = str(item.get("category", item.get("event_type", "general"))).strip().lower()
    default_varga, default_house = EVENT_CATEGORY_DEFAULTS.get(cat, ("D1", 1))
    varga = str(item["varga"]).strip().upper() if item.get("varga") is not None else default_varga
    house = int(item["house"]) if item.get("house") is not None else default_house
    sig_planet = (
        str(item["signifying_planet"]).strip().capitalize()
        if item.get("signifying_planet") is not None
        else None
    )
    exp_sign = (
        int(item["expected_varga_lagna_sign"]) % 12
        if item.get("expected_varga_lagna_sign") is not None
        else None
    )
    ev_jd = float(item["event_jd_ut"]) if item.get("event_jd_ut") is not None else None
    return LifeEventSpec(
        name=str(item.get("name", cat)),
        event_jd_ut=ev_jd,
        category=cat,
        varga=varga,
        house=house,
        signifying_planet=sig_planet,
        expected_varga_lagna_sign=exp_sign,
    )


def _score_life_events(
    cand_jd_ut: float,
    cand_lagna_lon: float,
    cand_moon_lon: float,
    d1_pl: Any,
    d9_pl: Any,
    d10_pl: Any,
    d60_pl: Any,
    planet_longitudes: Mapping[str, float] | None,
    events: Sequence[LifeEventSpec],
) -> float:
    """Compute the 10-point life-event / Varga fortification score for a candidate timestamp."""
    if not events:
        score = 5.0
        if d60_pl.shashtiamsa_is_benefic:
            score += 2.5
        if d9_pl.sign_lord in BENEFIC_PRANAPADA_NAVAMSA_LORDS:
            score += 1.5
        if d1_pl.sign_index == d9_pl.sign_index:
            score += 1.0
        return round(min(10.0, score), 6)

    varga_map = {
        "D1": d1_pl,
        "D9": d9_pl,
        "D10": d10_pl,
        "D60": d60_pl,
    }
    norm_planets: dict[str, float] = {}
    if planet_longitudes:
        norm_planets = {k.strip().capitalize(): normalize_degrees(v) for k, v in planet_longitudes.items()}

    per_event_max = 10.0 / float(len(events))
    total = 0.0

    for ev in events:
        v_code = (ev.varga or "D9").upper()
        v_pl = varga_map.get(v_code) or varga_sign(cand_lagna_lon, v_code)
        house_num = ((ev.house or 1) - 1) % 12
        target_sign = (v_pl.sign_index + house_num) % 12
        target_lord = RASI_LORDS[target_sign]

        pts = 0.0
        matched_criteria = 0
        checks_run = 0

        if ev.expected_varga_lagna_sign is not None:
            checks_run += 1
            if v_pl.sign_index == (ev.expected_varga_lagna_sign % 12):
                matched_criteria += 1

        if ev.signifying_planet is not None:
            checks_run += 1
            sig_p = ev.signifying_planet.strip().capitalize()
            if target_lord == sig_p or v_pl.sign_lord == sig_p:
                matched_criteria += 1
            elif sig_p in norm_planets:
                p_varga = varga_sign(norm_planets[sig_p], v_code)
                rel_house = ((p_varga.sign_index - v_pl.sign_index) % 12) + 1
                if p_varga.sign_index == target_sign or rel_house in (1, 4, 5, 7, 9, 10, 11):
                    matched_criteria += 1

        if ev.event_jd_ut is not None and ev.event_jd_ut > cand_jd_ut:
            checks_run += 1
            timeline = compute_vimshottari_dasha(cand_moon_lon, cand_jd_ut, max_level=2)
            active_lords: set[str] = set()
            for maha in timeline.mahadashas:
                if maha.start_jd <= ev.event_jd_ut <= maha.end_jd:
                    active_lords.add(maha.lord)
                    for antar in maha.sub_periods:
                        if antar.start_jd <= ev.event_jd_ut <= antar.end_jd:
                            active_lords.add(antar.lord)
                    break
            if (
                target_lord in active_lords
                or v_pl.sign_lord in active_lords
                or (ev.signifying_planet and ev.signifying_planet.capitalize() in active_lords)
            ):
                matched_criteria += 1

        if checks_run > 0:
            pts = per_event_max * (matched_criteria / float(checks_run))
        else:
            # Default structural check on the target house lord / varga benefic status
            if target_lord in BENEFIC_PRANAPADA_NAVAMSA_LORDS or d60_pl.shashtiamsa_is_benefic:
                pts = per_event_max * 0.8
            else:
                pts = per_event_max * 0.4
        total += pts

    return round(min(10.0, total), 6)


def _score_candidate(
    offset_sec: float,
    window_sec: float,
    cand_jd_ut: float,
    cand_lagna_lon: float,
    cand_moon_lon: float,
    kunda: KundaEvaluation,
    pranapada: PranapadaEvaluation,
    tattwa: PanchaTattwaState,
    planet_longitudes: Mapping[str, float] | None,
    events: Sequence[LifeEventSpec],
) -> tuple[float, float, float, float, float, Any, Any, Any, Any]:
    """Compute `(kunda_score, pranapada_score, tattwa_score, proximity_score, life_event_score, d1, d9, d10, d60)`."""
    # 1. Kunda Shuddhi (up to 35 points: 20 Rasi + 15 Nakshatra)
    if kunda.rasi_trine_or_7th:
        k_rasi = 20.0
    else:
        k_rasi = max(0.0, 12.0 * (1.0 - kunda.seconds_to_nearest_rasi_valid / 45.0))

    if kunda.nakshatra_alignment:
        k_nak = 15.0 if (kunda.matches_moon_nakshatra_ruler and kunda.matches_lagna_nakshatra_ruler) else 14.0
    else:
        k_nak = max(0.0, 8.0 * (1.0 - kunda.seconds_to_nearest_nakshatra_valid / 25.0))
    kunda_score = round(min(35.0, k_rasi + k_nak), 6)

    # 2. Pranapada Shuddhi (up to 30 points: 18 Rasi + 12 Benefic Navamsa)
    if pranapada.trine_or_7th_from_moon and pranapada.trine_or_7th_from_lagna:
        p_rasi = 18.0
    elif pranapada.rasi_trine_or_7th:
        p_rasi = 16.5
    else:
        p_rasi = max(0.0, 9.0 * (1.0 - pranapada.seconds_to_nearest_rasi_valid / 180.0))

    if pranapada.benefic_navamsa:
        p_nav = 12.0
    else:
        p_nav = max(0.0, 5.0 * (1.0 - pranapada.seconds_to_nearest_navamsa_valid / 40.0))
    pranapada_score = round(min(30.0, p_rasi + p_nav), 6)

    # 3. Pancha Tattwa compatibility (up to 15 points)
    d1_pl = varga_sign(cand_lagna_lon, "D1")
    d9_pl = varga_sign(cand_lagna_lon, "D9")
    d10_pl = varga_sign(cand_lagna_lon, "D10")
    d60_pl = varga_sign(cand_lagna_lon, "D60")

    lagna_is_odd = (d1_pl.sign_index % 2) == 0
    lagna_gender = "Male" if lagna_is_odd else "Female"
    lagna_element = RASI_ELEMENTS[d1_pl.sign_index]
    moon_element = RASI_ELEMENTS[min(int(cand_moon_lon // 30.0), 11)]

    t_score = 5.0 if tattwa.nature == "Saumya" else 3.5
    if tattwa.weekday_compatible:
        t_score += 4.0
    if tattwa.gender in (lagna_gender, "Neutral"):
        t_score += 2.5
    if tattwa.element in (lagna_element, moon_element, "Ether"):
        t_score += 2.0
    if tattwa.antara_tattwa.primary_ruler in BENEFIC_PRANAPADA_NAVAMSA_LORDS or (
        d1_pl.sign_lord in tattwa.antara_tattwa.ruling_planets
    ):
        t_score += 1.5
    tattwa_score = round(min(15.0, t_score), 6)

    # 4. Proximity to nominal recorded birth time (up to 10 points)
    if window_sec > 0.0:
        proximity_score = round(10.0 * max(0.0, 1.0 - (abs(offset_sec) / window_sec)), 6)
    else:
        proximity_score = 10.0

    # 5. Life-event Dasha/Varga alignment or structural Varga fortification (up to 10 points)
    life_event_score = _score_life_events(
        cand_jd_ut=cand_jd_ut,
        cand_lagna_lon=cand_lagna_lon,
        cand_moon_lon=cand_moon_lon,
        d1_pl=d1_pl,
        d9_pl=d9_pl,
        d10_pl=d10_pl,
        d60_pl=d60_pl,
        planet_longitudes=planet_longitudes,
        events=events,
    )

    return (
        kunda_score,
        pranapada_score,
        tattwa_score,
        proximity_score,
        life_event_score,
        d1_pl,
        d9_pl,
        d10_pl,
        d60_pl,
    )


def rectify_birth_time(
    nominal_jd_ut: float,
    sunrise_jd_ut: float,
    nominal_lagna_lon_deg: float,
    sun_lon_deg: float,
    moon_lon_deg: float,
    *,
    window_minutes: float = 15.0,
    step_seconds: float = 10.0,
    planet_longitudes: Mapping[str, float] | None = None,
    life_events: Sequence[Mapping[str, Any] | LifeEventSpec] | None = None,
) -> BirthTimeRectificationReport:
    """Scan `[nominal_jd_ut - window_minutes/1440, nominal_jd_ut + window_minutes/1440]`
    at `step_seconds` increments and rank candidate birth timestamps (`0..100`) across:
    - Kunda Shuddhi (`35 pts`)
    - Pranapada Shuddhi (`30 pts`)
    - Pancha Tattwa compatibility (`15 pts`)
    - Proximity to nominal recorded time (`10 pts`)
    - Life-event Dasha/Varga alignment (`10 pts`)

    Also analytically detects every `D1, D9, D10, D60` Varga cusp transition inside
    the uncertainty window and emits a deterministic SHA-256 calculation receipt.
    """
    if float(window_minutes) <= 0.0:
        raise ValueError("window_minutes must be positive")
    if float(step_seconds) <= 0.0:
        raise ValueError("step_seconds must be positive")

    win_min = float(window_minutes)
    step_sec = float(step_seconds)
    win_sec = win_min * 60.0

    half_steps = int(round(win_sec / step_sec))
    offsets_sec: list[float] = []
    if half_steps == 0:
        offsets_sec = [-win_sec, 0.0, win_sec]
    else:
        for idx in range(-half_steps, half_steps + 1):
            off = round(idx * step_sec, 6)
            if -win_sec - 1e-6 <= off <= win_sec + 1e-6:
                offsets_sec.append(off)
        if 0.0 not in offsets_sec:
            offsets_sec.append(0.0)
            offsets_sec.sort()

    parsed_events: tuple[LifeEventSpec, ...] = (
        tuple(_normalize_life_event(ev) for ev in life_events) if life_events else ()
    )

    raw_candidates: list[RectificationCandidate] = []
    for off_sec in offsets_sec:
        cand_jd = float(nominal_jd_ut) + (off_sec / 86400.0)
        cand_lagna = normalize_degrees(float(nominal_lagna_lon_deg) + off_sec * LAGNA_DEG_PER_SECOND)
        cand_moon = normalize_degrees(float(moon_lon_deg) + (off_sec / 86400.0) * MOON_DEG_PER_DAY)
        cand_hrs = (cand_jd - float(sunrise_jd_ut)) * 24.0
        vara = compute_vara(cand_jd, sunrise_jd_ut=float(sunrise_jd_ut))

        kunda_eval = evaluate_kunda_shuddhi(cand_lagna, cand_moon)
        pranapada_eval = evaluate_pranapada_shuddhi(
            cand_lagna,
            float(sun_lon_deg),
            cand_moon,
            cand_hrs,
        )
        tattwa_state = evaluate_pancha_tattwa(cand_hrs, vara.index)

        (
            k_score,
            p_score,
            t_score,
            prox_score,
            ev_score,
            d1_pl,
            d9_pl,
            d10_pl,
            d60_pl,
        ) = _score_candidate(
            offset_sec=off_sec,
            window_sec=win_sec,
            cand_jd_ut=cand_jd,
            cand_lagna_lon=cand_lagna,
            cand_moon_lon=cand_moon,
            kunda=kunda_eval,
            pranapada=pranapada_eval,
            tattwa=tattwa_state,
            planet_longitudes=planet_longitudes,
            events=parsed_events,
        )

        total = round(k_score + p_score + t_score + prox_score + ev_score, 6)
        raw_candidates.append(
            RectificationCandidate(
                rank=0,
                candidate_jd_ut=round(cand_jd, 10),
                offset_seconds=off_sec,
                offset_minutes=round(off_sec / 60.0, 6),
                lagna_lon_deg=round(cand_lagna, 8),
                moon_lon_deg=round(cand_moon, 8),
                d1_lagna_sign_index=d1_pl.sign_index,
                d1_lagna_sign_name=d1_pl.sign_name,
                d9_lagna_sign_index=d9_pl.sign_index,
                d9_lagna_sign_name=d9_pl.sign_name,
                d10_lagna_sign_index=d10_pl.sign_index,
                d10_lagna_sign_name=d10_pl.sign_name,
                d60_lagna_sign_index=d60_pl.sign_index,
                d60_lagna_sign_name=d60_pl.sign_name,
                d60_shashtiamsa_name=d60_pl.shashtiamsa_name or "",
                d60_shashtiamsa_is_benefic=bool(d60_pl.shashtiamsa_is_benefic),
                total_score=total,
                kunda_score=k_score,
                pranapada_score=p_score,
                tattwa_score=t_score,
                proximity_score=prox_score,
                life_event_score=ev_score,
                kunda=kunda_eval,
                pranapada=pranapada_eval,
                tattwa=tattwa_state,
            )
        )

    # Sort by descending total_score, breaking ties by smaller absolute offset_seconds, then earlier offset
    sorted_by_score = sorted(
        raw_candidates,
        key=lambda c: (-c.total_score, abs(c.offset_seconds), c.offset_seconds),
    )

    ranked_map: dict[float, int] = {
        c.offset_seconds: rank_idx for rank_idx, c in enumerate(sorted_by_score, start=1)
    }

    ranked_chronological = tuple(
        RectificationCandidate(
            rank=ranked_map[c.offset_seconds],
            candidate_jd_ut=c.candidate_jd_ut,
            offset_seconds=c.offset_seconds,
            offset_minutes=c.offset_minutes,
            lagna_lon_deg=c.lagna_lon_deg,
            moon_lon_deg=c.moon_lon_deg,
            d1_lagna_sign_index=c.d1_lagna_sign_index,
            d1_lagna_sign_name=c.d1_lagna_sign_name,
            d9_lagna_sign_index=c.d9_lagna_sign_index,
            d9_lagna_sign_name=c.d9_lagna_sign_name,
            d10_lagna_sign_index=c.d10_lagna_sign_index,
            d10_lagna_sign_name=c.d10_lagna_sign_name,
            d60_lagna_sign_index=c.d60_lagna_sign_index,
            d60_lagna_sign_name=c.d60_lagna_sign_name,
            d60_shashtiamsa_name=c.d60_shashtiamsa_name,
            d60_shashtiamsa_is_benefic=c.d60_shashtiamsa_is_benefic,
            total_score=c.total_score,
            kunda_score=c.kunda_score,
            pranapada_score=c.pranapada_score,
            tattwa_score=c.tattwa_score,
            proximity_score=c.proximity_score,
            life_event_score=c.life_event_score,
            kunda=c.kunda,
            pranapada=c.pranapada,
            tattwa=c.tattwa,
        )
        for c in raw_candidates
    )

    by_offset = {c.offset_seconds: c for c in ranked_chronological}
    top_ranked = tuple(by_offset[c.offset_seconds] for c in sorted_by_score[:10])
    best_cand = top_ranked[0]
    nominal_cand = by_offset[0.0]

    transitions = _detect_varga_transitions(
        nominal_jd_ut=float(nominal_jd_ut),
        nominal_lagna_lon_deg=float(nominal_lagna_lon_deg),
        window_minutes=win_min,
    )

    receipt = {
        "module": "ephemeris_oss.jyotish_rectification.rectify",
        "version": __version__,
        "nominal_jd_ut": round(float(nominal_jd_ut), 10),
        "sunrise_jd_ut": round(float(sunrise_jd_ut), 10),
        "nominal_lagna_lon_deg": round(normalize_degrees(nominal_lagna_lon_deg), 8),
        "sun_lon_deg": round(normalize_degrees(sun_lon_deg), 8),
        "moon_lon_deg": round(normalize_degrees(moon_lon_deg), 8),
        "window_minutes": win_min,
        "step_seconds": step_sec,
        "candidate_count": len(ranked_chronological),
        "rectified_jd_ut": best_cand.candidate_jd_ut,
        "offset_seconds": best_cand.offset_seconds,
        "best_total_score": best_cand.total_score,
        "best_kunda_lon_deg": round(best_cand.kunda.kunda_lon_deg, 8),
        "best_pranapada_lon_deg": round(best_cand.pranapada.pranapada_lon_deg, 8),
        "best_tattwa": best_cand.tattwa.tattwa_name,
        "varga_transition_count": len(transitions),
    }
    receipt_sha256 = canonical_hash(receipt)

    return BirthTimeRectificationReport(
        nominal_jd_ut=round(float(nominal_jd_ut), 10),
        sunrise_jd_ut=round(float(sunrise_jd_ut), 10),
        rectified_jd_ut=best_cand.candidate_jd_ut,
        offset_seconds=best_cand.offset_seconds,
        offset_minutes=best_cand.offset_minutes,
        window_minutes=win_min,
        step_seconds=step_sec,
        nominal_candidate=nominal_cand,
        best_candidate=best_cand,
        top_candidates=top_ranked,
        all_candidates=ranked_chronological,
        varga_transitions=transitions,
        receipt=receipt,
        receipt_sha256=receipt_sha256,
    )


__all__ = [
    "AntaraTattwaPeriod",
    "BENEFIC_PRANAPADA_NAVAMSA_LORDS",
    "BirthTimeRectificationReport",
    "KUNDA_DEG_PER_SECOND",
    "KUNDA_HARMONIC_FACTOR",
    "KundaEvaluation",
    "LAGNA_DEG_PER_DAY",
    "LAGNA_DEG_PER_SECOND",
    "LifeEventSpec",
    "MOON_DEG_PER_DAY",
    "MOON_DEG_PER_SECOND",
    "PANCHA_TATTWA_CATALOG",
    "PRANAPADA_DEG_PER_HOUR",
    "PRANAPADA_DEG_PER_SECOND",
    "PanchaTattwaState",
    "PranapadaEvaluation",
    "RECTIFICATION_VARGA_KEYS",
    "RectificationCandidate",
    "SHUDDHI_HOUSE_OFFSETS",
    "SIDEREAL_DAY_SECONDS",
    "TATTWA_CYCLE_MINUTES",
    "TattwaDefinition",
    "VargaCuspTransition",
    "WEEKDAY_NATURAL_TATTWA",
    "evaluate_kunda_shuddhi",
    "evaluate_pancha_tattwa",
    "evaluate_pranapada_shuddhi",
    "rectify_birth_time",
]
