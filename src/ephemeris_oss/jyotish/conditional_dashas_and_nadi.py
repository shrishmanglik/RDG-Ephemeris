"""All 10 Classical BPHS Conditional Nakshatra Dashas, 5-Level Prana Chronometer, 150-Nadi Amsa, 3-Ring Sudarshana Chakra, & Golden Muhurta Optimizer.

Implements frontier computational Jyotish subsystems from *Brihat Parashara Hora Shastra* (BPHS),
*Deva Keralam (Chandra Kala Nadi)*, and *Muhurta Chintamani*:

1. **All 10 Classical BPHS Nakshatra Dashas & Conditional Eligibility Classifier**
   (``compute_all_10_parashari_nakshatra_dashas``):
   - Evaluates the exact BPHS Chapter 46 mathematical eligibility criteria and computes full
     Mahadasha and Antardasha timelines for:
     (1) *Vimshottari Dasha* (120 Years, 9 Lords, Janma Nakshatra),
     (2) *Ashtottari Dasha* (108 Years, 8 Lords, Ardra-anchored 28-Nakshatra cycle),
     (3) *Shodashottari Dasha* (116 Years, 8 Lords: ``11..18y``, Pushya-anchored),
     (4) *Dwadashottari Dasha* (112 Years, 8 Lords: ``7..21y``, Revati-anchored),
     (5) *Panchottari Dasha* (105 Years, 7 Lords: ``12..18y``, Anuradha-anchored),
     (6) *Shatabdika Dasha* (100 Years, 7 Lords: ``5, 5, 10, 10, 20, 20, 30y``, Revati-anchored),
     (7) *Chaturashiti-Sama Dasha* (84 Years, 7 Lords x ``12y``, Swati-anchored),
     (8) *Dwisaptati-Sama Dasha* (72 Years, 8 Lords x ``9y``, Mula-anchored),
     (9) *Shat-Trimsha-Sama Dasha* (36 Years, 8 Lords: ``1..8y``, Shravana-anchored),
     (10) *Yogini Dasha* (36 Years, 8 Yoginis: ``1..8y``).
   - Computes the **Multi-Dasha Synchronicity & Cross-System Consensus Ranking** at any target date.

2. **Five-Level Vimshottari Prana-Dasha Sub-Hour Chronometer**
   (``compute_vimshottari_5_level_prana_chronometer``):
   - Drills down all 5 proportional levels (*Mahadasha -> Antardasha -> Pratyantardasha ->
     Sookshma Dasha -> Prana Dasha*) to resolve exact sub-hour/minute planetary activation windows.

3. **150-Division Nadi Amsa (0 deg 12 min Chandra Kala Nadi) & 3-Ring Sudarshana Chakra Engine**
   (``compute_nadi_amsa_and_sudarshana_chakra``):
   - Computes the exact 150-division *Nadi Amsa* (``1..150`` per sign, ``1,800`` across the zodiac,
     with classical *Chara* ``1..150``, *Sthira* ``150..1``, and *Dwiswabhava* ``76..150, 1..75`` ordering)
     and exact seconds of birth-time shift to the previous/next Nadi Amsa boundary.
   - Computes the 3-Ring *Sudarshana Chakra* (BPHS Ch. 67) superposing the Lagna, Chandra, and
     Surya charts across all 12 houses plus the 12-year cyclic *Sudarshana Dasha*.

4. **Golden Muhurta Electional Optimization Solver**
   (``solve_golden_muhurta_electional_windows``):
   - Evaluates 12 classical *Muhurta Chintamani* constraints (*Vara, Tithi, Nakshatra, Yoga, Karana,
     Rahu/Yamaganda/Gulika Kala, Dagdha Rashi, Panchaka Rahita, Tarabala, Chandrabala,
     Amrita/Sarvartha Siddhi, and Abhijit Muhurta*) across a date range to find the top-ranked
     electional windows for any human endeavor.
"""

from __future__ import annotations

from dataclasses import dataclass
import math
from typing import TYPE_CHECKING, Any, Mapping

from ..engine.receipt import canonical_hash
from .dasha import (
    ASHTOTTARI_RULERS,
    ASHTOTTARI_YEARS,
    SOLAR_YEAR_DAYS,
    VIMSHOTTARI_TOTAL_YEARS,
    VIMSHOTTARI_YEARS,
    YOGINI_LORDS,
    YOGINI_NAMES,
    YOGINI_YEARS,
    jd_to_iso_utc,
)
from .nakshatra import (
    NAKSHATRA_NAMES,
    NAKSHATRA_SPAN_DEG,
    RASI_NAMES,
    VIMSHOTTARI_RULERS,
    nakshatra_position,
)
from .vargas import RASI_LORDS, varga_sign
from .vishesha_lagnas import _format_rashi_dms as _format_classical_rashi_dms
from ..jyotish_transit.muhurta_search import (
    AMRITA_SIDDHI_NAKSHATRA,
    DAGDHA_RASI_BY_PAKSHA_TITHI,
    SARVARTHA_SIDDHI_NAKSHATRAS,
)

if TYPE_CHECKING:
    from ..adapter import EphemerisAdapter

# =============================================================================
# 1. ALL 10 CLASSICAL BPHS CONDITIONAL NAKSHATRA DASHAS
# =============================================================================

BPHS_10_NAKSHATRA_DASHAS: tuple[dict[str, Any], ...] = (
    {
        "key": "vimshottari",
        "title": "Vimshottari Dasha (120-Year Universal Mahadasha)",
        "total_years": 120.0,
        "start_nakshatra_index": 0,  # Ashwini (or Janma cycle)
        "divisor": 9,
        "lords": VIMSHOTTARI_RULERS,
        "years": tuple(float(VIMSHOTTARI_YEARS[r]) for r in VIMSHOTTARI_RULERS),
        "bphs_condition": "Universal primary Dasha applicable to all horoscopes in Kali Yuga (BPHS Ch. 46).",
    },
    {
        "key": "ashtottari",
        "title": "Ashtottari Dasha (108-Year Conditional Mahadasha)",
        "total_years": 108.0,
        "start_nakshatra_index": 5,  # Ardra
        "divisor": 8,
        "lords": ASHTOTTARI_RULERS,
        "years": tuple(float(ASHTOTTARI_YEARS[r]) for r in ASHTOTTARI_RULERS),
        "bphs_condition": "Rahu (not in Lagna) in Kendra (1,4,7,10) or Trikona (5,9) from Lagna Lord, or Day birth in Krishna Paksha / Night birth in Shukla Paksha.",
    },
    {
        "key": "shodashottari",
        "title": "Shodashottari Dasha (116-Year Conditional Mahadasha)",
        "total_years": 116.0,
        "start_nakshatra_index": 7,  # Pushya
        "divisor": 8,
        "lords": ("Sun", "Mars", "Jupiter", "Saturn", "Ketu", "Moon", "Mercury", "Venus"),
        "years": (11.0, 12.0, 13.0, 14.0, 15.0, 16.0, 17.0, 18.0),
        "bphs_condition": "Lagna in Moon's Hora in Krishna Paksha, or Lagna in Sun's Hora in Shukla Paksha (BPHS Ch. 46).",
    },
    {
        "key": "dwadashottari",
        "title": "Dwadashottari Dasha (112-Year Conditional Mahadasha)",
        "total_years": 112.0,
        "start_nakshatra_index": 26,  # Revati reverse/count
        "divisor": 8,
        "lords": ("Sun", "Jupiter", "Ketu", "Mercury", "Rahu", "Mars", "Saturn", "Moon"),
        "years": (7.0, 9.0, 11.0, 13.0, 15.0, 17.0, 19.0, 21.0),
        "bphs_condition": "Ascendant placed in a Navamsa ruled by Venus (Vrishabha or Tula D9).",
    },
    {
        "key": "panchottari",
        "title": "Panchottari Dasha (105-Year Conditional Mahadasha)",
        "total_years": 105.0,
        "start_nakshatra_index": 16,  # Anuradha
        "divisor": 7,
        "lords": ("Sun", "Mercury", "Saturn", "Mars", "Venus", "Moon", "Jupiter"),
        "years": (12.0, 13.0, 14.0, 15.0, 16.0, 17.0, 18.0),
        "bphs_condition": "Ascendant in Cancer (Karka) Rashi and Cancer Dwadasamsa (D12).",
    },
    {
        "key": "shatabdika",
        "title": "Shatabdika Dasha (100-Year Vargottama Mahadasha)",
        "total_years": 100.0,
        "start_nakshatra_index": 26,  # Revati
        "divisor": 7,
        "lords": ("Venus", "Sun", "Moon", "Mercury", "Jupiter", "Mars", "Saturn"),
        "years": (5.0, 5.0, 10.0, 10.0, 20.0, 20.0, 30.0),
        "bphs_condition": "Ascendant is Vargottama (occupying the same Rashi in D1 and D9 Navamsa).",
    },
    {
        "key": "chaturashiti_sama",
        "title": "Chaturashiti-Sama Dasha (84-Year 10th-Lord Mahadasha)",
        "total_years": 84.0,
        "start_nakshatra_index": 14,  # Swati
        "divisor": 7,
        "lords": ("Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn"),
        "years": (12.0, 12.0, 12.0, 12.0, 12.0, 12.0, 12.0),
        "bphs_condition": "10th House Lord (Karma-Pati) is placed in the 10th House.",
    },
    {
        "key": "dwisaptati_sama",
        "title": "Dwisaptati-Sama Dasha (72-Year Lagna/7th-Lord Mahadasha)",
        "total_years": 72.0,
        "start_nakshatra_index": 18,  # Mula
        "divisor": 8,
        "lords": ("Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn", "Rahu"),
        "years": (9.0, 9.0, 9.0, 9.0, 9.0, 9.0, 9.0, 9.0),
        "bphs_condition": "Lagna Lord is in the 1st or 7th House, or 7th House Lord is in the 1st House.",
    },
    {
        "key": "shat_trimsha_sama",
        "title": "Shat-Trimsha-Sama Dasha (36-Year Hora-Aligned Mahadasha)",
        "total_years": 36.0,
        "start_nakshatra_index": 21,  # Shravana
        "divisor": 8,
        "lords": ("Moon", "Sun", "Jupiter", "Mars", "Mercury", "Saturn", "Venus", "Rahu"),
        "years": (1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 8.0),
        "bphs_condition": "Daytime birth in Lagna Hora of Sun, or Nighttime birth in Lagna Hora of Moon.",
    },
    {
        "key": "yogini",
        "title": "Yogini Dasha (36-Year Tantric/Parashari Mahadasha)",
        "total_years": 36.0,
        "start_nakshatra_index": 0,  # (Nak + 3) mod 8
        "divisor": 8,
        "lords": tuple(f"{y} ({YOGINI_LORDS[y]})" for y in YOGINI_NAMES),
        "years": tuple(float(YOGINI_YEARS[y]) for y in YOGINI_NAMES),
        "bphs_condition": "Universal companion 36-year Sankata/Siddha Yogini cycle (BPHS Ch. 46).",
    },
)


@dataclass(frozen=True)
class ConditionalDashaPeriodSummary:
    """Single Mahadasha period in one of the 10 BPHS Nakshatra Dasha systems."""

    lord: str
    full_duration_years: float
    effective_duration_years: float
    start_jd: float
    end_jd: float
    start_iso_utc: str
    end_iso_utc: str


@dataclass(frozen=True)
class ConditionalNakshatraDashaSystemEntry:
    """Evaluation of one of the 10 BPHS Nakshatra Dasha systems for a birth chart."""

    system_key: str
    title: str
    total_cycle_years: float
    is_conditionally_eligible: bool
    eligibility_reason: str
    bphs_rule_summary: str
    opening_lord: str
    birth_balance_years: float
    active_mahadasha_lord: str
    active_antardasha_lord: str
    mahadashas: tuple[ConditionalDashaPeriodSummary, ...]


@dataclass(frozen=True)
class MultiDashaConsensusItem:
    """Planetary consensus score across all 10 Nakshatra Dashas at query_jd."""

    planet: str
    active_mahadasha_count: int
    active_antardasha_count: int
    eligible_system_mahadasha_count: int
    consensus_score_0_to_100: float
    supporting_systems: tuple[str, ...]


@dataclass(frozen=True)
class MultiDashaSynchronicityReport:
    """Complete 10-System BPHS Conditional Nakshatra Dasha & Multi-Dasha Synchronicity Report."""

    birth_jd: float
    query_jd: float
    moon_sidereal_lon_deg: float
    moon_nakshatra_name: str
    systems: tuple[ConditionalNakshatraDashaSystemEntry, ...]
    eligible_system_keys: tuple[str, ...]
    consensus_ranking: tuple[MultiDashaConsensusItem, ...]
    receipt_sha256: str


@dataclass(frozen=True)
class PranaSubPeriodWindow:
    """Level-5 Prana Dasha sub-period window (hours/minutes)."""

    prana_lord: str
    start_jd: float
    end_jd: float
    start_iso_utc: str
    end_iso_utc: str
    duration_minutes: float
    is_active_at_query: bool


@dataclass(frozen=True)
class PranaDashaChronometerReport:
    """Complete 5-Level Vimshottari (Mahadasha -> Antardasha -> Pratyantardasha -> Sookshma -> Prana) Chronometer."""

    birth_jd: float
    query_jd: float
    query_iso_utc: str
    mahadasha_lord: str
    mahadasha_start_iso: str
    mahadasha_end_iso: str
    antardasha_lord: str
    antardasha_start_iso: str
    antardasha_end_iso: str
    pratyantardasha_lord: str
    pratyantardasha_start_iso: str
    pratyantardasha_end_iso: str
    sookshma_lord: str
    sookshma_start_iso: str
    sookshma_end_iso: str
    sookshma_duration_hours: float
    active_prana_lord: str
    prana_windows: tuple[PranaSubPeriodWindow, ...]
    receipt_sha256: str


# =============================================================================
# 2. 150-NADI AMSA (DEVA KERALAM) & 3-RING SUDARSHANA CHAKRA
# =============================================================================

NADI_AMSA_BASE_NAMES_15: tuple[str, ...] = (
    "Vasudha",
    "Vaishnavi",
    "Brahmi",
    "Kalakoota",
    "Shankari",
    "Sudhakara",
    "Sama",
    "Saumya",
    "Sura",
    "Maya",
    "Manohara",
    "Madhavi",
    "Manjuswana",
    "Ghora",
    "Kumbhini",
)

NADI_AMSA_DECADE_QUALITIES_10: tuple[str, ...] = (
    "Prathama-Kala",
    "Dvitiya-Kala",
    "Tritiya-Kala",
    "Chaturtha-Kala",
    "Panchama-Kala",
    "Shashtha-Kala",
    "Saptama-Kala",
    "Ashtama-Kala",
    "Navama-Kala",
    "Dashama-Kala",
)


@dataclass(frozen=True)
class NadiAmsaCoordinate:
    """150-division Nadi Amsa (0 deg 12 min = 12 arcminutes) coordinate in Deva Keralam / Chandra Kala Nadi."""

    point_name: str
    sidereal_longitude_deg: float
    classical_dms: str
    rashi_name: str
    sign_modality: str  # "Chara (Movable)", "Sthira (Fixed)", "Dwiswabhava (Dual)"
    raw_slice_index_1_to_150: int
    nadi_amsa_number_1_to_150: int
    zodiacal_nadi_index_1_to_1800: int
    nadi_amsa_name: str
    nadi_ruler: str
    arcminutes_elapsed_in_nadi: float
    arcminutes_remaining_in_nadi: float
    seconds_of_birth_time_to_prev_nadi: float
    seconds_of_birth_time_to_next_nadi: float


@dataclass(frozen=True)
class SudarshanaHouseRow:
    """Simultaneous 3-ring (Lagna, Chandra, Surya) house analysis in BPHS Ch. 67 Sudarshana Chakra."""

    house_number: int
    lagna_ring_sign: str
    lagna_ring_lord: str
    lagna_ring_occupants: tuple[str, ...]
    chandra_ring_sign: str
    chandra_ring_lord: str
    chandra_ring_occupants: tuple[str, ...]
    surya_ring_sign: str
    surya_ring_lord: str
    surya_ring_occupants: tuple[str, ...]
    triple_frame_benefic_count: int
    triple_frame_convergence_score_0_to_100: float


@dataclass(frozen=True)
class SudarshanaDashaYearEntry:
    """Annual cyclic Sudarshana Dasha progression (1 year per house from birth)."""

    year_number_1_to_12: int
    active_lagna_house: int
    active_sign_name: str
    active_sign_lord: str
    start_iso_utc: str
    end_iso_utc: str


@dataclass(frozen=True)
class NadiAndSudarshanaReport:
    """Complete 150-Nadi Amsa (0 deg 12 min) & 3-Ring Sudarshana Chakra Synthesis Report."""

    ascendant_nadi: NadiAmsaCoordinate
    planet_nadis: dict[str, NadiAmsaCoordinate]
    sudarshana_houses: tuple[SudarshanaHouseRow, ...]
    sudarshana_dasha_years: tuple[SudarshanaDashaYearEntry, ...]
    active_sudarshana_house_at_query: int
    receipt_sha256: str


@dataclass(frozen=True)
class GoldenMuhurtaWindow:
    """Evaluated electional Muhurta candidate window with 12-constraint breakdown."""

    jd_ut: float
    iso_utc: str
    ist_timestamp: str
    vara_name: str
    tithi_number: int
    paksha: str
    nakshatra_name: str
    yoga_number: int
    karana_name: str
    electional_lagna_sign: str
    electional_lagna_dms: str
    tarabala_number_1_to_9: int
    tarabala_name: str
    chandrabala_house_1_to_12: int
    panchaka_remainder: int
    is_panchaka_rahita: bool
    is_amrita_or_sarvartha_siddhi: bool
    is_dagdha_rashi_free: bool
    score_0_to_100: float
    grade: str
    passed_checks: tuple[str, ...]
    warnings: tuple[str, ...]


@dataclass(frozen=True)
class GoldenMuhurtaOptimizationReport:
    """Multi-constraint Electional Muhurta Optimization Report."""

    activity: str
    start_jd_ut: float
    end_jd_ut: float
    evaluated_window_count: int
    top_windows: tuple[GoldenMuhurtaWindow, ...]
    receipt_sha256: str


_CANONICAL_PLANET_ALIASES: dict[str, str] = {
    "sun": "sun",
    "surya": "sun",
    "moon": "moon",
    "chandra": "moon",
    "mars": "mars",
    "mangala": "mars",
    "kuja": "mars",
    "mercury": "mercury",
    "budha": "mercury",
    "jupiter": "jupiter",
    "guru": "jupiter",
    "brihaspati": "jupiter",
    "venus": "venus",
    "shukra": "venus",
    "saturn": "saturn",
    "shani": "saturn",
    "rahu": "rahu",
    "true_rahu": "rahu",
    "mean_rahu": "rahu",
    "true_node": "rahu",
    "mean_node": "rahu",
    "north_node": "rahu",
    "ketu": "ketu",
    "true_ketu": "ketu",
    "mean_ketu": "ketu",
    "south_node": "ketu",
}


def _canonical_planet_key(name: str) -> str:
    raw = str(name).strip().lower().replace("-", "_").replace(" ", "_")
    return _CANONICAL_PLANET_ALIASES.get(raw, raw)


def _normalize_planet_longitudes(
    planet_longitudes_deg: Mapping[str, float],
    *,
    fallback_sun: float | None = None,
    fallback_moon: float | None = None,
) -> dict[str, float]:
    norm: dict[str, float] = {}
    for k, v in planet_longitudes_deg.items():
        if v is None:
            continue
        norm[_canonical_planet_key(k)] = float(v) % 360.0
    if "sun" not in norm and fallback_sun is not None:
        norm["sun"] = float(fallback_sun) % 360.0
    if "moon" not in norm and fallback_moon is not None:
        norm["moon"] = float(fallback_moon) % 360.0
    if "rahu" in norm and "ketu" not in norm:
        norm["ketu"] = (norm["rahu"] + 180.0) % 360.0
    elif "ketu" in norm and "rahu" not in norm:
        norm["rahu"] = (norm["ketu"] + 180.0) % 360.0
    return norm


def compute_all_10_parashari_nakshatra_dashas(
    moon_sidereal_lon_deg: float,
    asc_sidereal_lon_deg: float,
    sun_sidereal_lon_deg: float,
    planet_longitudes_deg: Mapping[str, float],
    birth_jd: float,
    *,
    query_jd: float | None = None,
    is_day_birth: bool = True,
    year_days: float = SOLAR_YEAR_DAYS,
) -> MultiDashaSynchronicityReport:
    """Evaluate all 10 BPHS conditional Nakshatra Dashas and compute Multi-Dasha Synchronicity."""
    q_jd = float(query_jd if query_jd is not None else birth_jd + 30.0 * year_days)
    nak = nakshatra_position(moon_sidereal_lon_deg)
    nak_idx = int(nak.index)
    frac_rem = float(nak.fraction_remaining)
    frac_el = float(nak.fraction_elapsed)

    asc_rashi = int((float(asc_sidereal_lon_deg) % 360.0) // 30.0) % 12
    asc_d9 = varga_sign(float(asc_sidereal_lon_deg), "D9").sign_index
    asc_d12 = varga_sign(float(asc_sidereal_lon_deg), "D12").sign_index
    asc_d2_deg = float(asc_sidereal_lon_deg) % 30.0
    is_odd_asc = (asc_rashi % 2) == 0
    in_sun_hora = (is_odd_asc and asc_d2_deg < 15.0) or ((not is_odd_asc) and asc_d2_deg >= 15.0)

    elong = (float(moon_sidereal_lon_deg) - float(sun_sidereal_lon_deg)) % 360.0
    is_shukla = elong < 180.0

    norm_planet_longitudes = _normalize_planet_longitudes(
        planet_longitudes_deg,
        fallback_sun=sun_sidereal_lon_deg,
        fallback_moon=moon_sidereal_lon_deg,
    )

    # House positions of lords relative to Ascendant:
    def _planet_rashi(p_name: str) -> int:
        c_key = _canonical_planet_key(p_name)
        if c_key not in norm_planet_longitudes:
            raise ValueError(f"Missing required planet longitude for {p_name!r}")
        val = norm_planet_longitudes[c_key]
        return int((float(val) % 360.0) // 30.0) % 12

    lagna_lord = RASI_LORDS[asc_rashi]
    lagna_lord_rashi = _planet_rashi(lagna_lord)
    rahu_rashi = _planet_rashi("rahu")
    rahu_from_ll = ((rahu_rashi - lagna_lord_rashi) % 12) + 1
    seventh_lord = RASI_LORDS[(asc_rashi + 6) % 12]
    seventh_lord_rashi = _planet_rashi(seventh_lord)
    tenth_rashi = (asc_rashi + 9) % 12
    tenth_lord = RASI_LORDS[tenth_rashi]
    tenth_lord_rashi = _planet_rashi(tenth_lord)

    systems_out: list[ConditionalNakshatraDashaSystemEntry] = []
    eligible_keys: list[str] = []
    maha_hits: dict[str, list[str]] = {}
    antar_hits: dict[str, list[str]] = {}
    elig_maha_hits: dict[str, int] = {}

    for spec in BPHS_10_NAKSHATRA_DASHAS:
        s_key = spec["key"]
        lords: tuple[str, ...] = spec["lords"]
        yrs: tuple[float, ...] = spec["years"]
        tot_y = float(spec["total_years"])
        div = int(spec["divisor"])
        start_nak = int(spec["start_nakshatra_index"])

        # Evaluate BPHS conditional eligibility:
        if s_key == "vimshottari":
            is_elig = True
            elig_reason = "Universal Kali Yuga primary Nakshatra Dasha (always applicable)."
            open_idx = nak_idx % 9
        elif s_key == "ashtottari":
            cond_rahu = (rahu_rashi != asc_rashi) and (rahu_from_ll in (1, 4, 5, 7, 9, 10))
            cond_paksha = (is_day_birth and not is_shukla) or ((not is_day_birth) and is_shukla)
            is_elig = bool(cond_rahu or cond_paksha)
            elig_reason = (
                f"Eligible: Rahu is in House {rahu_from_ll} from Lagna Lord ({lagna_lord}) / Paksha-Day condition met."
                if is_elig
                else f"Secondary: Rahu in House {rahu_from_ll} from {lagna_lord} and Day={is_day_birth}/Shukla={is_shukla}."
            )
            open_idx = ((nak_idx - start_nak) % 27) % div
        elif s_key == "shodashottari":
            is_elig = bool(((not in_sun_hora) and (not is_shukla)) or (in_sun_hora and is_shukla))
            elig_reason = (
                "Eligible: Hora Lagna and Shukla/Krishna Paksha polarity match BPHS Shodashottari rule."
                if is_elig
                else "Secondary: Hora Lagna and Paksha polarity do not trigger primary Shodashottari condition."
            )
            open_idx = ((nak_idx - start_nak) % 27) % div
        elif s_key == "dwadashottari":
            is_elig = asc_d9 in (1, 6)  # Taurus or Libra Navamsa
            elig_reason = (
                f"Eligible: Ascendant D9 Navamsa is {RASI_NAMES[asc_d9]} (ruled by Venus)."
                if is_elig
                else f"Secondary: Ascendant D9 Navamsa is {RASI_NAMES[asc_d9]} (not Taurus/Libra)."
            )
            open_idx = ((start_nak - nak_idx) % 27) % div
        elif s_key == "panchottari":
            is_elig = (asc_rashi == 3) and (asc_d12 == 3)
            elig_reason = (
                "Eligible: Ascendant is in Cancer Rashi and Cancer D12 Dwadasamsa."
                if is_elig
                else f"Secondary: Ascendant is {RASI_NAMES[asc_rashi]} (D12 {RASI_NAMES[asc_d12]})."
            )
            open_idx = ((nak_idx - start_nak) % 27) % div
        elif s_key == "shatabdika":
            is_elig = asc_rashi == asc_d9
            elig_reason = (
                f"Eligible: Ascendant is Vargottama in {RASI_NAMES[asc_rashi]}."
                if is_elig
                else f"Secondary: Ascendant D1 ({RASI_NAMES[asc_rashi]}) != D9 ({RASI_NAMES[asc_d9]})."
            )
            open_idx = ((nak_idx - start_nak) % 27) % div
        elif s_key == "chaturashiti_sama":
            is_elig = tenth_lord_rashi == tenth_rashi
            elig_reason = (
                f"Eligible: 10th Lord ({tenth_lord}) occupies the 10th House ({RASI_NAMES[tenth_rashi]})."
                if is_elig
                else f"Secondary: 10th Lord ({tenth_lord}) is in {RASI_NAMES[tenth_lord_rashi]}."
            )
            open_idx = ((nak_idx - start_nak) % 27) % div
        elif s_key == "dwisaptati_sama":
            is_elig = (lagna_lord_rashi in (asc_rashi, (asc_rashi + 6) % 12)) or (seventh_lord_rashi == asc_rashi)
            elig_reason = (
                f"Eligible: Lagna Lord ({lagna_lord}) or 7th Lord ({seventh_lord}) occupies the 1st/7th axis."
                if is_elig
                else f"Secondary: Lagna Lord ({lagna_lord}) in {RASI_NAMES[lagna_lord_rashi]}."
            )
            open_idx = ((nak_idx - start_nak) % 27) % div
        elif s_key == "shat_trimsha_sama":
            is_elig = (is_day_birth and in_sun_hora) or ((not is_day_birth) and (not in_sun_hora))
            elig_reason = (
                "Eligible: Day/Night birth matches Sun/Moon Hora Lagna."
                if is_elig
                else "Secondary: Day/Night birth does not match Sun/Moon Hora Lagna."
            )
            open_idx = ((nak_idx - start_nak) % 27) % div
        else:  # yogini
            is_elig = True
            elig_reason = "Universal companion 36-year Yogini Dasha cycle."
            open_idx = (nak_idx + 3) % 8

        if is_elig:
            eligible_keys.append(s_key)

        if s_key == "ashtottari":
            from .dasha import compute_ashtottari_dasha

            ash_tl = compute_ashtottari_dasha(moon_sidereal_lon_deg, birth_jd, year_days=year_days)
            open_lord = ash_tl.opening_lord
            open_idx = lords.index(open_lord)
            open_full_yrs = float(yrs[open_idx])
            bal_yrs = float(ash_tl.birth_balance_years)
            el_days = (open_full_yrs - bal_yrs) * float(year_days)
        else:
            open_lord = lords[open_idx]
            open_full_yrs = float(yrs[open_idx])
            bal_yrs = open_full_yrs * frac_rem
            el_days = open_full_yrs * frac_el * float(year_days)

        cursor_jd = float(birth_jd) - el_days
        mahas: list[ConditionalDashaPeriodSummary] = []
        active_maha = open_lord
        active_antar = open_lord

        # Generate enough full cycles so query_jd is always covered across any horizon:
        num_cycles = max(2, int(math.ceil(max(0.0, q_jd - float(birth_jd)) / max(1.0, tot_y * float(year_days)))) + 2)
        for cycle_step in range(len(lords) * num_cycles):
            l_i = (open_idx + cycle_step) % len(lords)
            l_name = lords[l_i]
            f_y = float(yrs[l_i])
            s_jd = cursor_jd
            e_jd = cursor_jd + f_y * float(year_days)
            cursor_jd = e_jd
            if e_jd <= float(birth_jd) + 1e-9:
                continue
            eff_s = max(float(birth_jd), s_jd)
            eff_y = (e_jd - eff_s) / float(year_days)
            if len(mahas) < len(lords):
                mahas.append(
                    ConditionalDashaPeriodSummary(
                        lord=l_name,
                        full_duration_years=f_y,
                        effective_duration_years=eff_y,
                        start_jd=eff_s,
                        end_jd=e_jd,
                        start_iso_utc=jd_to_iso_utc(eff_s),
                        end_iso_utc=jd_to_iso_utc(e_jd),
                    )
                )
            if s_jd <= q_jd < e_jd:
                active_maha = l_name
                # Locate active Antardasha proportionally inside [s_jd, e_jd]:
                sub_c = s_jd
                for sub_step in range(len(lords)):
                    sub_i = (l_i + sub_step) % len(lords)
                    sub_y = f_y * (float(yrs[sub_i]) / tot_y)
                    sub_e = sub_c + sub_y * float(year_days)
                    if (sub_c <= q_jd < sub_e) if sub_step < len(lords) - 1 else (sub_c <= q_jd <= sub_e):
                        active_antar = lords[sub_i]
                        break
                    sub_c = sub_e

        # Normalize planet key for consensus scoring (strip Yogini prefix if present):
        norm_maha = active_maha.split("(")[-1].rstrip(")") if "(" in active_maha else active_maha
        norm_antar = active_antar.split("(")[-1].rstrip(")") if "(" in active_antar else active_antar
        maha_hits.setdefault(norm_maha, []).append(f"{s_key}:MD")
        antar_hits.setdefault(norm_antar, []).append(f"{s_key}:AD")
        if is_elig:
            elig_maha_hits[norm_maha] = elig_maha_hits.get(norm_maha, 0) + 1

        systems_out.append(
            ConditionalNakshatraDashaSystemEntry(
                system_key=s_key,
                title=spec["title"],
                total_cycle_years=tot_y,
                is_conditionally_eligible=is_elig,
                eligibility_reason=elig_reason,
                bphs_rule_summary=spec["bphs_condition"],
                opening_lord=open_lord,
                birth_balance_years=bal_yrs,
                active_mahadasha_lord=active_maha,
                active_antardasha_lord=active_antar,
                mahadashas=tuple(mahas),
            )
        )

    all_planets = ("Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn", "Rahu", "Ketu")
    consensus: list[MultiDashaConsensusItem] = []
    for p_name in all_planets:
        m_list = maha_hits.get(p_name, [])
        a_list = antar_hits.get(p_name, [])
        el_cnt = elig_maha_hits.get(p_name, 0)
        if m_list or a_list:
            raw_score = min(100.0, len(m_list) * 14.0 + len(a_list) * 8.0 + el_cnt * 10.0)
            consensus.append(
                MultiDashaConsensusItem(
                    planet=p_name,
                    active_mahadasha_count=len(m_list),
                    active_antardasha_count=len(a_list),
                    eligible_system_mahadasha_count=el_cnt,
                    consensus_score_0_to_100=round(raw_score, 2),
                    supporting_systems=tuple(m_list + a_list),
                )
            )
    consensus.sort(key=lambda x: (-x.consensus_score_0_to_100, x.planet))

    receipt = canonical_hash(
        {
            "birth_jd": round(float(birth_jd), 6),
            "query_jd": round(q_jd, 6),
            "moon_lon": round(float(moon_sidereal_lon_deg), 6),
            "eligible": eligible_keys,
        }
    )
    return MultiDashaSynchronicityReport(
        birth_jd=float(birth_jd),
        query_jd=q_jd,
        moon_sidereal_lon_deg=float(moon_sidereal_lon_deg) % 360.0,
        moon_nakshatra_name=nak.name,
        systems=tuple(systems_out),
        eligible_system_keys=tuple(eligible_keys),
        consensus_ranking=tuple(consensus),
        receipt_sha256=receipt,
    )


def compute_vimshottari_5_level_prana_chronometer(
    moon_sidereal_lon_deg: float,
    birth_jd: float,
    query_jd: float,
    *,
    year_days: float = SOLAR_YEAR_DAYS,
) -> PranaDashaChronometerReport:
    """Compute exact 5-level Vimshottari (Mahadasha -> Antardasha -> Pratyantardasha -> Sookshma -> Prana) windows."""
    nak = nakshatra_position(moon_sidereal_lon_deg)
    open_idx = int(nak.index) % 9
    open_lord = VIMSHOTTARI_RULERS[open_idx]
    open_yrs = float(VIMSHOTTARI_YEARS[open_lord])
    unclipped_start = float(birth_jd) - open_yrs * float(nak.fraction_elapsed) * float(year_days)

    def _find_sub(start_jd: float, span_days: float, start_lord_idx: int, target_jd: float) -> tuple[int, float, float]:
        c = start_jd
        for k in range(9):
            idx = (start_lord_idx + k) % 9
            w = float(VIMSHOTTARI_YEARS[VIMSHOTTARI_RULERS[idx]]) / VIMSHOTTARI_TOTAL_YEARS
            sub_d = span_days * w if k < 8 else (start_jd + span_days - c)
            if (c <= target_jd < c + sub_d - 1e-12) or k == 8:
                return idx, c, c + sub_d
            c += sub_d
        return start_lord_idx, start_jd, start_jd + span_days

    # Walk 120-year cycles to bracket query_jd at Level 1 (Mahadasha):
    c_jd = unclipped_start
    md_idx = open_idx
    md_s = c_jd
    md_e = c_jd
    for step in range(27):
        idx = (open_idx + step) % 9
        span_d = float(VIMSHOTTARI_YEARS[VIMSHOTTARI_RULERS[idx]]) * float(year_days)
        if (c_jd <= float(query_jd) < c_jd + span_d - 1e-12) or step == 26:
            md_idx = idx
            md_s = c_jd
            md_e = c_jd + span_d
            break
        c_jd += span_d

    ad_idx, ad_s, ad_e = _find_sub(md_s, md_e - md_s, md_idx, float(query_jd))
    pd_idx, pd_s, pd_e = _find_sub(ad_s, ad_e - ad_s, ad_idx, float(query_jd))
    sd_idx, sd_s, sd_e = _find_sub(pd_s, pd_e - pd_s, pd_idx, float(query_jd))

    # Build all 9 Level-5 Prana Dasha windows inside the active Level-4 Sookshma period:
    prana_list: list[PranaSubPeriodWindow] = []
    p_cursor = sd_s
    sd_span = sd_e - sd_s
    active_prana = VIMSHOTTARI_RULERS[sd_idx]
    for k in range(9):
        p_idx = (sd_idx + k) % 9
        p_lord = VIMSHOTTARI_RULERS[p_idx]
        w = float(VIMSHOTTARI_YEARS[p_lord]) / VIMSHOTTARI_TOTAL_YEARS
        p_span = sd_span * w if k < 8 else (sd_e - p_cursor)
        p_s = p_cursor
        p_e = p_cursor + p_span
        p_cursor = p_e
        is_act = (p_s <= float(query_jd) < p_e) if k < 8 else (p_s <= float(query_jd) <= p_e + 1e-9)
        if is_act:
            active_prana = p_lord
        prana_list.append(
            PranaSubPeriodWindow(
                prana_lord=p_lord,
                start_jd=p_s,
                end_jd=p_e,
                start_iso_utc=jd_to_iso_utc(p_s),
                end_iso_utc=jd_to_iso_utc(p_e),
                duration_minutes=round(p_span * 1440.0, 2),
                is_active_at_query=is_act,
            )
        )

    receipt = canonical_hash(
        {
            "birth_jd": round(float(birth_jd), 6),
            "query_jd": round(float(query_jd), 6),
            "md": VIMSHOTTARI_RULERS[md_idx],
            "ad": VIMSHOTTARI_RULERS[ad_idx],
            "pd": VIMSHOTTARI_RULERS[pd_idx],
            "sd": VIMSHOTTARI_RULERS[sd_idx],
            "prana": active_prana,
        }
    )
    return PranaDashaChronometerReport(
        birth_jd=float(birth_jd),
        query_jd=float(query_jd),
        query_iso_utc=jd_to_iso_utc(query_jd),
        mahadasha_lord=VIMSHOTTARI_RULERS[md_idx],
        mahadasha_start_iso=jd_to_iso_utc(max(birth_jd, md_s)),
        mahadasha_end_iso=jd_to_iso_utc(md_e),
        antardasha_lord=VIMSHOTTARI_RULERS[ad_idx],
        antardasha_start_iso=jd_to_iso_utc(ad_s),
        antardasha_end_iso=jd_to_iso_utc(ad_e),
        pratyantardasha_lord=VIMSHOTTARI_RULERS[pd_idx],
        pratyantardasha_start_iso=jd_to_iso_utc(pd_s),
        pratyantardasha_end_iso=jd_to_iso_utc(pd_e),
        sookshma_lord=VIMSHOTTARI_RULERS[sd_idx],
        sookshma_start_iso=jd_to_iso_utc(sd_s),
        sookshma_end_iso=jd_to_iso_utc(sd_e),
        sookshma_duration_hours=round(sd_span * 24.0, 2),
        active_prana_lord=active_prana,
        prana_windows=tuple(prana_list),
        receipt_sha256=receipt,
    )


def _compute_single_nadi_amsa(
    point_name: str,
    lon_deg: float,
    angular_speed_deg_per_sec: float,
) -> NadiAmsaCoordinate:
    """Compute the 150-division Nadi Amsa (0 deg 12 min = 0.2 deg) coordinate."""
    norm = float(lon_deg) % 360.0
    r_idx = int(norm // 30.0) % 12
    deg_in_sign = norm % 30.0
    # Each Nadi Amsa spans 30 / 150 = 0.2 deg = 12 arcminutes:
    raw_idx_0 = min(149, int(deg_in_sign / 0.2))
    raw_slice_1_to_150 = raw_idx_0 + 1

    # Classical Deva Keralam / Chandra Kala Nadi modality ordering:
    # Movable (Chara: 0, 3, 6, 9) -> Direct 1..150
    # Fixed (Sthira: 1, 4, 7, 10) -> Reverse 150..1
    # Dual (Dwiswabhava: 2, 5, 8, 11) -> 76..150 then 1..75
    mod_rem = r_idx % 3
    if mod_rem == 0:
        modality = "Chara (Movable: Direct 1..150)"
        nadi_no = raw_slice_1_to_150
    elif mod_rem == 1:
        modality = "Sthira (Fixed: Reverse 150..1)"
        nadi_no = 151 - raw_slice_1_to_150
    else:
        modality = "Dwiswabhava (Dual: 76..150, 1..75)"
        nadi_no = (raw_slice_1_to_150 + 75) if raw_slice_1_to_150 <= 75 else (raw_slice_1_to_150 - 75)

    zodiac_nadi = r_idx * 150 + nadi_no
    base_name = NADI_AMSA_BASE_NAMES_15[(nadi_no - 1) % 15]
    decade_name = NADI_AMSA_DECADE_QUALITIES_10[(nadi_no - 1) // 15]
    full_nadi_name = f"{base_name} ({decade_name})"
    nadi_ruler = VIMSHOTTARI_RULERS[(nadi_no - 1) % 9]

    offset_deg = deg_in_sign - raw_idx_0 * 0.2
    arcmin_el = offset_deg * 60.0
    arcmin_rem = max(0.0, 12.0 - arcmin_el)

    speed = max(1e-8, abs(float(angular_speed_deg_per_sec)))
    sec_prev = offset_deg / speed
    sec_next = max(0.0, (0.2 - offset_deg) / speed)

    return NadiAmsaCoordinate(
        point_name=point_name,
        sidereal_longitude_deg=norm,
        classical_dms=_format_classical_rashi_dms(norm),
        rashi_name=RASI_NAMES[r_idx],
        sign_modality=modality,
        raw_slice_index_1_to_150=raw_slice_1_to_150,
        nadi_amsa_number_1_to_150=nadi_no,
        zodiacal_nadi_index_1_to_1800=zodiac_nadi,
        nadi_amsa_name=full_nadi_name,
        nadi_ruler=nadi_ruler,
        arcminutes_elapsed_in_nadi=round(arcmin_el, 4),
        arcminutes_remaining_in_nadi=round(arcmin_rem, 4),
        seconds_of_birth_time_to_prev_nadi=round(sec_prev, 2),
        seconds_of_birth_time_to_next_nadi=round(sec_next, 2),
    )


def compute_nadi_amsa_and_sudarshana_chakra(
    asc_sidereal_lon_deg: float,
    planet_longitudes_deg: Mapping[str, float],
    birth_jd: float,
    *,
    query_jd: float | None = None,
    year_days: float = SOLAR_YEAR_DAYS,
) -> NadiAndSudarshanaReport:
    """Compute the 150-Nadi Amsa coordinates and the 3-Ring Sudarshana Chakra (BPHS Ch. 67)."""
    q_jd = float(query_jd if query_jd is not None else birth_jd)
    # Ascendant moves ~360 deg per sidereal day = 15 arcsec/sec = 1/240 deg/sec:
    asc_nadi = _compute_single_nadi_amsa("Ascendant (Lagna)", asc_sidereal_lon_deg, 1.0 / 240.0)

    mean_speeds_deg_day = {
        "sun": 0.9856,
        "moon": 13.1764,
        "mars": 0.5240,
        "mercury": 1.2000,
        "jupiter": 0.0831,
        "venus": 1.1500,
        "saturn": 0.0335,
        "rahu": 0.0529,
        "ketu": 0.0529,
    }
    planet_nadis: dict[str, NadiAmsaCoordinate] = {}
    rashi_occupants: dict[int, list[str]] = {i: [] for i in range(12)}
    norm_planet_longitudes = _normalize_planet_longitudes(planet_longitudes_deg)

    for p_key in ("sun", "moon", "mars", "mercury", "jupiter", "venus", "saturn", "rahu", "ketu"):
        if p_key not in norm_planet_longitudes:
            raise ValueError(f"Missing required planet longitude for {p_key!r}")
        lon = float(norm_planet_longitudes[p_key]) % 360.0
        sp_sec = mean_speeds_deg_day[p_key] / 86400.0
        planet_nadis[p_key] = _compute_single_nadi_amsa(p_key.capitalize(), lon, sp_sec)
        rashi_occupants[int(lon // 30.0) % 12].append(p_key.capitalize())

    asc_rashi = int((float(asc_sidereal_lon_deg) % 360.0) // 30.0) % 12
    moon_rashi = int((planet_nadis["moon"].sidereal_longitude_deg) // 30.0) % 12
    sun_rashi = int((planet_nadis["sun"].sidereal_longitude_deg) // 30.0) % 12

    benefics = {"Jupiter", "Venus", "Mercury", "Moon"}
    houses_out: list[SudarshanaHouseRow] = []
    for h_no in range(1, 13):
        offset = h_no - 1
        l_s = (asc_rashi + offset) % 12
        c_s = (moon_rashi + offset) % 12
        s_s = (sun_rashi + offset) % 12

        l_occ = tuple(rashi_occupants[l_s])
        c_occ = tuple(rashi_occupants[c_s])
        s_occ = tuple(rashi_occupants[s_s])

        all_occ = l_occ + c_occ + s_occ
        ben_cnt = sum(1 for p in all_occ if p in benefics)
        mal_cnt = len(all_occ) - ben_cnt
        base_sc = 50.0 + ben_cnt * 12.0 - mal_cnt * 6.0
        if h_no in (1, 4, 5, 7, 9, 10, 11):
            base_sc += 8.0
        conv_score = max(10.0, min(100.0, round(base_sc, 1)))

        houses_out.append(
            SudarshanaHouseRow(
                house_number=h_no,
                lagna_ring_sign=RASI_NAMES[l_s],
                lagna_ring_lord=RASI_LORDS[l_s],
                lagna_ring_occupants=l_occ,
                chandra_ring_sign=RASI_NAMES[c_s],
                chandra_ring_lord=RASI_LORDS[c_s],
                chandra_ring_occupants=c_occ,
                surya_ring_sign=RASI_NAMES[s_s],
                surya_ring_lord=RASI_LORDS[s_s],
                surya_ring_occupants=s_occ,
                triple_frame_benefic_count=ben_cnt,
                triple_frame_convergence_score_0_to_100=conv_score,
            )
        )

    # 12-Year Cyclic Sudarshana Dasha (1 house per solar year):
    age_years = max(0.0, (q_jd - float(birth_jd)) / float(year_days))
    cycle_base_year = int(age_years // 12) * 12
    active_house = (int(age_years) % 12) + 1
    dasha_years: list[SudarshanaDashaYearEntry] = []
    for yr_i in range(12):
        h_idx = yr_i + 1
        s_rashi = (asc_rashi + yr_i) % 12
        y_start = float(birth_jd) + (cycle_base_year + yr_i) * float(year_days)
        y_end = y_start + float(year_days)
        dasha_years.append(
            SudarshanaDashaYearEntry(
                year_number_1_to_12=cycle_base_year + yr_i + 1,
                active_lagna_house=h_idx,
                active_sign_name=RASI_NAMES[s_rashi],
                active_sign_lord=RASI_LORDS[s_rashi],
                start_iso_utc=jd_to_iso_utc(y_start),
                end_iso_utc=jd_to_iso_utc(y_end),
            )
        )

    receipt = canonical_hash(
        {
            "asc_nadi": asc_nadi.zodiacal_nadi_index_1_to_1800,
            "moon_nadi": planet_nadis["moon"].zodiacal_nadi_index_1_to_1800,
            "active_house": active_house,
        }
    )
    return NadiAndSudarshanaReport(
        ascendant_nadi=asc_nadi,
        planet_nadis=planet_nadis,
        sudarshana_houses=tuple(houses_out),
        sudarshana_dasha_years=tuple(dasha_years),
        active_sudarshana_house_at_query=active_house,
        receipt_sha256=receipt,
    )


TARABALA_NAMES_9: tuple[str, ...] = (
    "Janma (Body/Danger)",
    "Sampat (Wealth/Prosperity)",
    "Vipat (Danger/Obstacles)",
    "Kshema (Well-Being/Safety)",
    "Pratyak (Obstacles)",
    "Sadhana (Realization/Success)",
    "Naidhana (Peril/Destruction)",
    "Mitra (Friendly/Auspicious)",
    "Parama Mitra (Supreme Friend)",
)

ACTIVITY_FAVORED_NAKSHATRAS: dict[str, set[int]] = {
    "vivaha_marriage": {3, 4, 6, 9, 11, 12, 14, 16, 18, 20, 21, 25, 26},
    "vyapara_business": {0, 3, 6, 7, 11, 12, 13, 14, 16, 20, 21, 22, 25, 26},
    "griha_pravesha_property": {3, 4, 11, 13, 16, 20, 21, 22, 23, 25, 26},
    "vidyarambha_education": {0, 4, 6, 7, 12, 13, 14, 21, 26},
    "yatra_travel": {0, 4, 6, 7, 12, 14, 16, 21, 22, 26},
    "general_auspicious": {0, 3, 4, 6, 7, 11, 12, 13, 14, 16, 20, 21, 22, 23, 25, 26},
}

MALEFIC_YOGAS_1_INDEXED = {1, 6, 9, 10, 13, 15, 17, 19, 27}
VARA_NAMES_7 = ("Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday")
KARANA_MOVABLE_7 = ("Bava", "Balava", "Kaulava", "Taitila", "Gara", "Vanija", "Vishti (Bhadra)")


def solve_golden_muhurta_electional_windows(
    start_jd_ut: float,
    end_jd_ut: float,
    *,
    latitude_deg: float = 28.6139,
    longitude_deg: float = 77.2090,
    activity: str = "vyapara_business",
    natal_moon_lon_deg: float = 42.8,
    step_minutes: int = 60,
    top_k: int = 12,
    ayanamsa: str = "lahiri",
    adapter: "EphemerisAdapter | None" = None,
) -> GoldenMuhurtaOptimizationReport:
    """Scan [start_jd_ut, end_jd_ut] across 12 classical Muhurta constraints to find top Golden Muhurtas."""
    from ..adapter import EphemerisAdapter

    ad = adapter if adapter is not None else EphemerisAdapter()
    act_key = activity if activity in ACTIVITY_FAVORED_NAKSHATRAS else "general_auspicious"
    fav_naks = ACTIVITY_FAVORED_NAKSHATRAS[act_key]

    nat_nak_idx = int(nakshatra_position(natal_moon_lon_deg).index)
    nat_rashi_idx = int((float(natal_moon_lon_deg) % 360.0) // 30.0) % 12

    step_d = max(5, int(step_minutes)) / 1440.0
    t_curr = float(start_jd_ut)
    candidates: list[GoldenMuhurtaWindow] = []
    n_eval = 0

    while t_curr <= float(end_jd_ut) + 1e-9:
        n_eval += 1
        s_lon = float(ad.calc_ut(t_curr, "sun", sidereal=True, ayanamsa=ayanamsa).longitude_deg) % 360.0
        m_lon = float(ad.calc_ut(t_curr, "moon", sidereal=True, ayanamsa=ayanamsa).longitude_deg) % 360.0
        houses = ad.houses_ut(t_curr, latitude_deg, longitude_deg, system="placidus", ayanamsa=ayanamsa)
        asc_lon = float(houses.ascendant_deg) % 360.0
        asc_rashi = int(asc_lon // 30.0) % 12

        # Resolve actual sunrise for the active solar day and derive its Vedic weekday (Vara):
        from .panchanga import compute_muhurta_windows

        jd_local = t_curr + float(longitude_deg) / 360.0
        local_midnight_ut = math.floor(jd_local - 0.5) + 0.5 - (float(longitude_deg) / 360.0)
        try:
            _, (cand_sr_jd,) = ad.rise_trans(local_midnight_ut, "sun", 1, (float(longitude_deg), float(latitude_deg), 0.0))
            if cand_sr_jd > t_curr:
                _, (sr_jd,) = ad.rise_trans(local_midnight_ut - 1.0, "sun", 1, (float(longitude_deg), float(latitude_deg), 0.0))
            else:
                sr_jd = cand_sr_jd
            _, (ss_jd,) = ad.rise_trans(sr_jd, "sun", 2, (float(longitude_deg), float(latitude_deg), 0.0))
            _, (next_sr_jd,) = ad.rise_trans(ss_jd, "sun", 1, (float(longitude_deg), float(latitude_deg), 0.0))
        except Exception:
            sr_approx = local_midnight_ut + (6.0 / 24.0)
            if sr_approx > t_curr:
                sr_approx -= 1.0
            sr_jd = sr_approx
            ss_jd = sr_approx + 0.5
            next_sr_jd = sr_approx + 1.0

        sr_local = sr_jd + float(longitude_deg) / 360.0
        vara_sun0 = int(math.floor(sr_local + 1.5)) % 7
        vara_names_sun0 = ("Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday")
        vara_name = vara_names_sun0[vara_sun0]

        elong = (m_lon - s_lon) % 360.0
        tithi_1_to_30 = int(elong // 12.0) + 1
        paksha = "Shukla" if tithi_1_to_30 <= 15 else "Krishna"
        paksha_tithi = tithi_1_to_30 if tithi_1_to_30 <= 15 else tithi_1_to_30 - 15

        m_nak = nakshatra_position(m_lon)
        nak_idx = int(m_nak.index)
        yoga_1_to_27 = int(((s_lon + m_lon) % 360.0) // (360.0 / 27.0)) + 1

        karana_idx_0_59 = int(elong // 6.0)
        if karana_idx_0_59 == 0:
            karana_name = "Kimstughna"
        elif karana_idx_0_59 >= 57:
            karana_name = ("Shakuni", "Chatushpada", "Naga")[karana_idx_0_59 - 57]
        else:
            karana_name = KARANA_MOVABLE_7[(karana_idx_0_59 - 1) % 7]

        # Tarabala (1..9 from Natal Moon Nakshatra):
        tara_num = ((nak_idx - nat_nak_idx) % 27) % 9 + 1
        tara_name = TARABALA_NAMES_9[tara_num - 1]
        m_rashi = int(m_lon // 30.0) % 12
        chandra_house = ((m_rashi - nat_rashi_idx) % 12) + 1

        # Panchaka Rahita check: (Tithi_paksha + Vara_1_7 + Nak_1_27 + Lagna_1_12) mod 9
        panchaka_rem = (paksha_tithi + (vara_sun0 + 1) + (nak_idx + 1) + (asc_rashi + 1)) % 9
        is_panchaka_clean = panchaka_rem not in (1, 2, 4, 6, 8)

        # Dagdha Rashi (burnt sign) check:
        dagdha_set = set(DAGDHA_RASI_BY_PAKSHA_TITHI.get(paksha_tithi, ()))
        is_dagdha_free = asc_rashi not in dagdha_set

        # Amrita Siddhi & Sarvartha Siddhi check:
        is_siddhi = (AMRITA_SIDDHI_NAKSHATRA.get(vara_sun0) == nak_idx) or (
            nak_idx in SARVARTHA_SIDDHI_NAKSHATRAS.get(vara_sun0, ())
        )

        # Daily sunrise/sunset time-window checks (Rahu Kalam, Yamagandam, Gulika Kalam, Abhijit Muhurta):
        m_wins = compute_muhurta_windows(sr_jd, ss_jd, next_sunrise_jd=next_sr_jd, vara_index=vara_sun0)
        in_rahu = m_wins.rahu_kalam.start_jd <= t_curr < m_wins.rahu_kalam.end_jd
        in_yama = m_wins.yamagandam.start_jd <= t_curr < m_wins.yamagandam.end_jd
        in_gulika = m_wins.gulika_kalam.start_jd <= t_curr < m_wins.gulika_kalam.end_jd
        in_abhijit = m_wins.abhijit_muhurta.start_jd <= t_curr < m_wins.abhijit_muhurta.end_jd

        # Scoring across the 12 Muhurta constraints:
        score = 50.0
        passed: list[str] = []
        warns: list[str] = []

        if in_rahu:
            score -= 25.0
            warns.append("Rahu Kalam (Inauspicious Daily Window)")
        else:
            passed.append("Free of Rahu Kalam")
        if in_yama:
            score -= 18.0
            warns.append("Yamagandam (Inauspicious Daily Window)")
        else:
            passed.append("Free of Yamagandam")
        if in_gulika:
            score -= 10.0
            warns.append("Gulika Kalam")
        if in_abhijit:
            score += 10.0
            passed.append("Abhijit Muhurta (Midday Victory Window)")

        if vara_sun0 in (1, 3, 4, 5):  # Mon, Wed, Thu, Fri
            score += 8.0
            passed.append(f"Shubha Vara ({vara_name})")
        if paksha_tithi not in (4, 9, 14) and tithi_1_to_30 != 30:
            score += 8.0
            passed.append(f"Non-Rikta Tithi ({paksha} {paksha_tithi})")
        else:
            score -= 15.0
            warns.append(f"Rikta/Amavasya Tithi ({tithi_1_to_30})")

        if nak_idx in fav_naks:
            score += 12.0
            passed.append(f"Activity-Favored Nakshatra ({m_nak.name})")
        if yoga_1_to_27 not in MALEFIC_YOGAS_1_INDEXED:
            score += 6.0
            passed.append(f"Auspicious Yoga (#{yoga_1_to_27})")
        else:
            score -= 10.0
            warns.append(f"Malefic Nitya Yoga (#{yoga_1_to_27})")

        if "Vishti" not in karana_name and karana_idx_0_59 < 57:
            score += 5.0
            passed.append(f"Shubha Karana ({karana_name})")
        else:
            score -= 14.0
            warns.append(f"Bhadra/Fixed Karana ({karana_name})")

        if tara_num in (2, 4, 6, 8, 9):
            score += 10.0
            passed.append(f"Shubha Tarabala ({tara_name})")
        else:
            score -= 10.0
            warns.append(f"Adverse Tarabala ({tara_name})")

        if chandra_house in (1, 3, 6, 7, 10, 11):
            score += 8.0
            passed.append(f"Shubha Chandrabala ({chandra_house}th from Janma Rashi)")
        else:
            score -= 12.0
            warns.append(f"Weak Chandrabala ({chandra_house}th from Janma Rashi)")

        if is_panchaka_clean:
            score += 6.0
            passed.append("Panchaka Rahita (Free of 5 Blemishes)")
        if is_dagdha_free:
            score += 5.0
            passed.append(f"Lagna Free of Tithi Dagdha ({RASI_NAMES[asc_rashi]})")
        else:
            score -= 15.0
            warns.append(f"Dagdha Rashi Lagna ({RASI_NAMES[asc_rashi]})")

        if is_siddhi:
            score += 8.0
            passed.append("Amrita / Sarvartha Siddhi Yoga Active")

        final_score = max(0.0, min(100.0, round(score, 1)))
        if in_rahu or in_yama:
            grade = "Adhama (Avoid)" if final_score < 70.0 else "Madhyama (Auspicious)"
        else:
            grade = (
                "Uttama (Supreme Golden Muhurta)"
                if final_score >= 85.0
                else ("Madhyama (Auspicious)" if final_score >= 70.0 else "Adhama (Avoid)")
            )

        ist_iso = jd_to_iso_utc(t_curr + 5.5 / 24.0).replace("Z", " IST")
        candidates.append(
            GoldenMuhurtaWindow(
                jd_ut=t_curr,
                iso_utc=jd_to_iso_utc(t_curr),
                ist_timestamp=ist_iso,
                vara_name=vara_name,
                tithi_number=tithi_1_to_30,
                paksha=paksha,
                nakshatra_name=m_nak.name,
                yoga_number=yoga_1_to_27,
                karana_name=karana_name,
                electional_lagna_sign=RASI_NAMES[asc_rashi],
                electional_lagna_dms=_format_classical_rashi_dms(asc_lon),
                tarabala_number_1_to_9=tara_num,
                tarabala_name=tara_name,
                chandrabala_house_1_to_12=chandra_house,
                panchaka_remainder=panchaka_rem,
                is_panchaka_rahita=is_panchaka_clean,
                is_amrita_or_sarvartha_siddhi=is_siddhi,
                is_dagdha_rashi_free=is_dagdha_free,
                score_0_to_100=final_score,
                grade=grade,
                passed_checks=tuple(passed),
                warnings=tuple(warns),
            )
        )
        t_curr += step_d

    candidates.sort(key=lambda w: (-w.score_0_to_100, w.jd_ut))
    top_wins = tuple(candidates[: max(1, int(top_k))])
    receipt = canonical_hash(
        {
            "activity": act_key,
            "start_jd_ut": round(float(start_jd_ut), 4),
            "end_jd_ut": round(float(end_jd_ut), 4),
            "top_score": top_wins[0].score_0_to_100 if top_wins else 0.0,
        }
    )
    return GoldenMuhurtaOptimizationReport(
        activity=act_key,
        start_jd_ut=float(start_jd_ut),
        end_jd_ut=float(end_jd_ut),
        evaluated_window_count=n_eval,
        top_windows=top_wins,
        receipt_sha256=receipt,
    )
