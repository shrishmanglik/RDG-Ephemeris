"""Clean-room Electional Muhurta Evaluator and Window Scanner.

Mathematical and classical rules follow *Muhurta Chintamani*, *Brihat Samhita*,
*Kalamrita*, and *Brihat Parashara Hora Shastra*:
- Panchaka Rahita (Five-fold limb sum modulo 9 classifying Mrityu, Agni, Raja,
  Chora, Roga, and Shuddha windows).
- Siddha, Amrita Siddhi, Sarvartha Siddhi, Ravi Pushya, Guru Pushya, Dwipushkara,
  Tripushkara, and Dagdha Rasi (burnt sign) yoga detectors.
- Chandrabala (12-fold transit Moon strength from natal Moon sign) and Tarabala
  (9-fold transit Moon star strength from natal Moon nakshatra).
- Gandanta junction detector (within 48 arcminutes of the three Water-Fire
  rasi/nakshatra boundaries at 0, 120, and 240 degrees).
- Deterministic 0..100 Muhurta instant scorer and window scanner with auditable
  SHA-256 calculation receipts.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Final, Mapping, Sequence

from .._version import __version__
from ..engine.receipt import canonical_hash
from ..jyotish.dasha import jd_to_iso_utc
from ..jyotish.nakshatra import (
    NAKSHATRA_NAMES,
    RASI_NAMES,
    TaraBalaResult,
    compute_tara_bala,
    nakshatra_position,
    normalize_degrees,
)
from ..jyotish.panchanga import (
    MuhurtaWindows,
    PanchangaSummary,
    compute_muhurta_windows,
    compute_panchanga,
)

# Panchaka modulo-9 classifications (*Muhurta Chintamani*)
PANCHAKA_CATALOG: Final[Mapping[int, tuple[str, bool, str]]] = {
    0: ("Shuddha", True, "Pure and free of Panchaka affliction"),
    1: ("Mrityu Panchaka", False, "Danger to life and vitality"),
    2: ("Agni Panchaka", False, "Risk of fire, heat, and conflict"),
    3: ("Shuddha", True, "Pure and free of Panchaka affliction"),
    4: ("Raja Panchaka", False, "Obstacle from authority or governance"),
    5: ("Shuddha", True, "Pure and free of Panchaka affliction"),
    6: ("Chora Panchaka", False, "Risk of theft, loss, or travel hazard"),
    7: ("Shuddha", True, "Pure and free of Panchaka affliction"),
    8: ("Roga Panchaka", False, "Risk of illness, delay, and infirmity"),
}

# Sarvartha Siddhi Yoga: 0-based weekday (0=Sun..6=Sat) -> frozenset of 0-based nakshatra indices (0..26)
SARVARTHA_SIDDHI_NAKSHATRAS: Final[Mapping[int, frozenset[int]]] = {
    0: frozenset({0, 7, 11, 12, 18, 20, 25}),  # Sun: Ashwini, Pushya, U.Phalguni, Hasta, Mula, U.Ashadha, U.Bhadrapada
    1: frozenset({3, 4, 7, 16, 21}),           # Mon: Rohini, Mrigashirsha, Pushya, Anuradha, Shravana
    2: frozenset({0, 2, 8, 25}),               # Tue: Ashwini, Krittika, Ashlesha, U.Bhadrapada
    3: frozenset({2, 3, 4, 12, 16}),           # Wed: Krittika, Rohini, Mrigashirsha, Hasta, Anuradha
    4: frozenset({0, 6, 7, 16, 26}),           # Thu: Ashwini, Punarvasu, Pushya, Anuradha, Revati
    5: frozenset({0, 6, 16, 21, 26}),          # Fri: Ashwini, Punarvasu, Anuradha, Shravana, Revati
    6: frozenset({3, 14, 21}),                 # Sat: Rohini, Swati, Shravana
}

# Amrita Siddhi Yoga: 0-based weekday (0=Sun..6=Sat) -> 0-based nakshatra index
AMRITA_SIDDHI_NAKSHATRA: Final[Mapping[int, int]] = {
    0: 12,  # Sunday + Hasta
    1: 4,   # Monday + Mrigashirsha
    2: 0,   # Tuesday + Ashwini
    3: 16,  # Wednesday + Anuradha
    4: 7,   # Thursday + Pushya
    5: 26,  # Friday + Revati
    6: 3,   # Saturday + Rohini
}

# Inauspicious Tithi exception for Amrita Siddhi Yoga (*Muhurta Chintamani*)
AMRITA_SIDDHI_EXCLUDED_PAKSHA_TITHI: Final[Mapping[int, int]] = {
    0: 5,   # Sunday + Hasta on Panchami
    1: 6,   # Monday + Mrigashirsha on Shashthi
    2: 7,   # Tuesday + Ashwini on Saptami
    3: 8,   # Wednesday + Anuradha on Ashtami
    4: 9,   # Thursday + Pushya on Navami
    5: 10,  # Friday + Revati on Dashami
    6: 11,  # Saturday + Rohini on Ekadashi
}

# Dwipushkara & Tripushkara components (*Muhurta Chintamani*)
PUSHKARA_VARA_INDICES: Final[frozenset[int]] = frozenset({0, 2, 6})  # Sunday, Tuesday, Saturday
BHADRA_PAKSHA_TITHIS: Final[frozenset[int]] = frozenset({2, 7, 12})  # Dwitiya, Saptami, Dwadashi
DWIPUSHKARA_NAKSHATRA_INDICES: Final[frozenset[int]] = frozenset({4, 13, 22})  # Mrigashirsha, Chitra, Dhanishta
TRIPUSHKARA_NAKSHATRA_INDICES: Final[frozenset[int]] = frozenset({
    2, 6, 11, 15, 20, 24,  # Krittika, Punarvasu, U.Phalguni, Vishakha, U.Ashadha, P.Bhadrapada
})

# Dagdha Rasi (burnt signs, 0-based 0..11) by Paksha Tithi (1..15) per *Kalamrita* / *Muhurta Chintamani*
DAGDHA_RASI_BY_PAKSHA_TITHI: Final[Mapping[int, tuple[int, ...]]] = {
    1: (6, 9),          # Pratipada: Tula, Makara
    2: (8, 11),         # Dwitiya: Dhanu, Meena
    3: (4, 9),          # Tritiya: Simha, Makara
    4: (1, 10),         # Chaturthi: Vrishabha, Kumbha
    5: (2, 5),          # Panchami: Mithuna, Kanya
    6: (0, 4),          # Shashthi: Mesha, Simha
    7: (3, 8),          # Saptami: Karka, Dhanu
    8: (2, 5),          # Ashtami: Mithuna, Kanya
    9: (4, 7),          # Navami: Simha, Vrishchika
    10: (4, 7),         # Dashami: Simha, Vrishchika
    11: (8, 11),        # Ekadashi: Dhanu, Meena
    12: (6, 9),         # Dwadashi: Tula, Makara
    13: (1, 4),         # Trayodashi: Vrishabha, Simha
    14: (2, 5, 8, 11),  # Chaturdashi: Mithuna, Kanya, Dhanu, Meena
    15: (),             # Purnima / Amavasya: no Dagdha Rasi
}

# Auspicious and inauspicious Chandrabala houses from natal Moon (1..12)
CHANDRABALA_GOOD_HOUSES: Final[frozenset[int]] = frozenset({1, 3, 6, 7, 10, 11})
CHANDRABALA_BAD_HOUSES: Final[frozenset[int]] = frozenset({4, 8, 12})
CHANDRABALA_NEUTRAL_HOUSES: Final[frozenset[int]] = frozenset({2, 5, 9})

# Water-Fire Gandanta junction longitudes (0, 120, 240 deg) and default orb (48 arcminutes = 0.8 deg)
GANDANTA_JUNCTIONS_DEG: Final[tuple[float, ...]] = (0.0, 120.0, 240.0)
DEFAULT_GANDANTA_ORB_DEG: Final[float] = 48.0 / 60.0  # 0.8 degrees


@dataclass(frozen=True)
class PanchakaResult:
    """Result of the classical Panchaka Rahita (mod 9) electional test."""

    tithi_num: int
    vara_num: int
    nakshatra_num: int
    lagna_sign: int
    total: int
    remainder: int
    name: str
    is_auspicious: bool
    meaning: str


@dataclass(frozen=True)
class SiddhaYogaEvaluation:
    """Active electional Siddha Yogas and Dagdha Rasi state for an instant."""

    vara_index: int
    nakshatra_index: int
    tithi_num: int
    paksha_tithi: int
    sarvartha_siddhi: bool
    amrita_siddhi: bool
    amrita_siddhi_tithi_afflicted: bool
    ravi_pushya: bool
    guru_pushya: bool
    dwipushkara: bool
    tripushkara: bool
    active_yogas: tuple[str, ...]
    dagdha_rasis: tuple[int, ...]
    dagdha_rasi_names: tuple[str, ...]
    moon_in_dagdha_rasi: bool


@dataclass(frozen=True)
class ChandrabalaResult:
    """Chandrabala (lunar transit strength relative to natal Moon sign)."""

    natal_moon_sign: int
    transit_moon_sign: int
    house_from_natal_moon: int
    status: str
    is_auspicious: bool
    is_inauspicious: bool
    score_weight: float


@dataclass(frozen=True)
class MuhurtaInstantEvaluation:
    """Comprehensive deterministic evaluation of one candidate Muhurta timestamp."""

    jd_ut: float
    iso_utc: str
    score: float
    grade: str
    is_recommended: bool
    panchanga: PanchangaSummary
    panchaka: PanchakaResult
    siddha_yogas: SiddhaYogaEvaluation
    tara_bala: TaraBalaResult | None
    chandra_bala: ChandrabalaResult | None
    lagna_sign_index: int
    lagna_sign_name: str
    moon_gandanta: bool
    lagna_gandanta: bool
    in_rahu_kalam: bool
    in_yamagandam: bool
    in_gulika_kalam: bool
    in_abhijit_muhurta: bool
    in_durmuhurta: bool
    dosha_flags: tuple[str, ...]
    benefic_factors: tuple[str, ...]
    receipt: Mapping[str, Any]
    receipt_sha256: str


@dataclass(frozen=True)
class MuhurtaWindowInterval:
    """Contiguous recommended electional window aggregated from scanned instants."""

    start_jd: float
    end_jd: float
    start_iso_utc: str
    end_iso_utc: str
    duration_minutes: float
    peak_jd: float
    peak_score: float
    mean_score: float
    sample_count: int
    active_yogas: tuple[str, ...]


@dataclass(frozen=True)
class MuhurtaScanReport:
    """Complete Muhurta window scan report with ranked instants, intervals, and SHA-256 receipt."""

    sample_count: int
    threshold_score: float
    best_instant: MuhurtaInstantEvaluation
    instants: tuple[MuhurtaInstantEvaluation, ...]
    recommended_windows: tuple[MuhurtaWindowInterval, ...]
    receipt: Mapping[str, Any]
    receipt_sha256: str


def evaluate_panchaka(
    tithi_num: int,
    vara_num: int,
    nakshatra_num: int,
    lagna_sign: int,
) -> PanchakaResult:
    """Evaluate Panchaka Rahita from 1-based Panchanga numbers.

    Parameters
    ----------
    tithi_num : int
        Lunar day number in ``1..30`` (or Paksha Tithi ``1..15``).
    vara_num : int
        Vedic weekday number in ``1..7`` (1=Sunday .. 7=Saturday).
    nakshatra_num : int
        Lunar mansion number in ``1..27`` (1=Ashwini .. 27=Revati).
    lagna_sign : int
        Ascendant sign number in ``1..12`` (1=Mesha .. 12=Meena).
    """
    if not 1 <= int(tithi_num) <= 30:
        raise ValueError("tithi_num must be in 1..30")
    if not 1 <= int(vara_num) <= 7:
        raise ValueError("vara_num must be in 1..7")
    if not 1 <= int(nakshatra_num) <= 27:
        raise ValueError("nakshatra_num must be in 1..27")
    if not 1 <= int(lagna_sign) <= 12:
        raise ValueError("lagna_sign must be in 1..12")

    t_num = int(tithi_num)
    v_num = int(vara_num)
    n_num = int(nakshatra_num)
    l_num = int(lagna_sign)

    total = t_num + v_num + n_num + l_num
    rem = total % 9
    name, is_auspicious, meaning = PANCHAKA_CATALOG[rem]

    return PanchakaResult(
        tithi_num=t_num,
        vara_num=v_num,
        nakshatra_num=n_num,
        lagna_sign=l_num,
        total=total,
        remainder=rem,
        name=name,
        is_auspicious=is_auspicious,
        meaning=meaning,
    )


def evaluate_siddha_yogas(
    vara_index: int,
    nakshatra_index: int,
    tithi_num: int = 1,
    *,
    moon_sign_index: int | None = None,
) -> SiddhaYogaEvaluation:
    """Evaluate classical electional Siddha Yogas and Dagdha Rasi for a weekday, nakshatra, and tithi.

    Parameters
    ----------
    vara_index : int
        0-based weekday index (`0=Sunday .. 6=Saturday`).
    nakshatra_index : int
        0-based nakshatra index (`0=Ashwini .. 26=Revati`).
    tithi_num : int
        1-based Tithi number (`1..30`). Defaults to 1.
    moon_sign_index : int | None
        Optional 0-based Rasi index (`0..11`) of the Moon or Lagna to test for Dagdha Rasi.
    """
    if not 0 <= int(vara_index) <= 6:
        raise ValueError("vara_index must be in 0..6")
    if not 0 <= int(nakshatra_index) <= 26:
        raise ValueError("nakshatra_index must be in 0..26")
    if not 1 <= int(tithi_num) <= 30:
        raise ValueError("tithi_num must be in 1..30")

    v_idx = int(vara_index)
    n_idx = int(nakshatra_index)
    t_num = int(tithi_num)
    paksha_tithi = t_num if t_num <= 15 else (t_num - 15)

    sarvartha = n_idx in SARVARTHA_SIDDHI_NAKSHATRAS[v_idx]
    amrita_raw = AMRITA_SIDDHI_NAKSHATRA[v_idx] == n_idx
    amrita_afflicted = amrita_raw and (AMRITA_SIDDHI_EXCLUDED_PAKSHA_TITHI[v_idx] == paksha_tithi)
    amrita = amrita_raw and not amrita_afflicted

    ravi_pushya = (v_idx == 0) and (n_idx == 7)
    guru_pushya = (v_idx == 4) and (n_idx == 7)

    is_pushkara_day_tithi = (v_idx in PUSHKARA_VARA_INDICES) and (paksha_tithi in BHADRA_PAKSHA_TITHIS)
    dwipushkara = is_pushkara_day_tithi and (n_idx in DWIPUSHKARA_NAKSHATRA_INDICES)
    tripushkara = is_pushkara_day_tithi and (n_idx in TRIPUSHKARA_NAKSHATRA_INDICES)

    active: list[str] = []
    if sarvartha:
        active.append("Sarvartha Siddhi Yoga")
    if amrita:
        active.append("Amrita Siddhi Yoga")
    if ravi_pushya:
        active.append("Ravi Pushya Yoga")
    if guru_pushya:
        active.append("Guru Pushya Yoga")
    if dwipushkara:
        active.append("Dwipushkara Yoga")
    if tripushkara:
        active.append("Tripushkara Yoga")

    dagdha = DAGDHA_RASI_BY_PAKSHA_TITHI.get(paksha_tithi, ())
    dagdha_names = tuple(RASI_NAMES[r] for r in dagdha)
    if moon_sign_index is not None:
        m_sign = int(moon_sign_index) % 12
        in_dagdha = m_sign in dagdha
    else:
        in_dagdha = False

    return SiddhaYogaEvaluation(
        vara_index=v_idx,
        nakshatra_index=n_idx,
        tithi_num=t_num,
        paksha_tithi=paksha_tithi,
        sarvartha_siddhi=sarvartha,
        amrita_siddhi=amrita,
        amrita_siddhi_tithi_afflicted=amrita_afflicted,
        ravi_pushya=ravi_pushya,
        guru_pushya=guru_pushya,
        dwipushkara=dwipushkara,
        tripushkara=tripushkara,
        active_yogas=tuple(active),
        dagdha_rasis=dagdha,
        dagdha_rasi_names=dagdha_names,
        moon_in_dagdha_rasi=in_dagdha,
    )


def evaluate_chandrabala(
    natal_moon_sign: int,
    transit_moon_sign: int,
) -> ChandrabalaResult:
    """Evaluate Chandrabala (transit Moon house from natal Moon sign).

    Accepts either 1-based sign numbers (`1..12`) or 0-based sign indices (`0..11`)
    consistently for both arguments. Houses `1, 3, 6, 7, 10, 11` from natal Moon
    are auspicious; houses `4, 8, 12` are inauspicious (Ashtama Chandra at 8th is
    severely afflicted); houses `2, 5, 9` are neutral/moderate.
    """
    if not 0 <= int(natal_moon_sign) <= 12 or not 0 <= int(transit_moon_sign) <= 12:
        raise ValueError("Moon sign arguments must be in 0..12")
    n_sign = int(natal_moon_sign)
    t_sign = int(transit_moon_sign)
    house = ((t_sign - n_sign) % 12) + 1

    if house in CHANDRABALA_GOOD_HOUSES:
        status = "Auspicious"
        is_good = True
        is_bad = False
        weight = 1.0
    elif house in CHANDRABALA_BAD_HOUSES:
        status = "Ashtama Chandra (Severe Dosha)" if house == 8 else "Inauspicious"
        is_good = False
        is_bad = True
        weight = 0.0
    else:
        status = "Moderate"
        is_good = False
        is_bad = False
        weight = 0.6

    return ChandrabalaResult(
        natal_moon_sign=n_sign,
        transit_moon_sign=t_sign,
        house_from_natal_moon=house,
        status=status,
        is_auspicious=is_good,
        is_inauspicious=is_bad,
        score_weight=weight,
    )


def is_gandanta_degree(
    lon_deg: float,
    *,
    orb_deg: float = DEFAULT_GANDANTA_ORB_DEG,
) -> bool:
    """Return True if a sidereal longitude lies within `orb_deg` (default 48 arcmin = 0.8 deg)
    of any of the three Water-Fire junctions (0 deg, 120 deg, 240 deg).
    """
    if orb_deg <= 0.0:
        raise ValueError("orb_deg must be positive")
    lon = normalize_degrees(lon_deg)
    for j_deg in GANDANTA_JUNCTIONS_DEG:
        diff = abs((lon - j_deg + 180.0) % 360.0 - 180.0)
        if diff <= orb_deg + 1e-12:
            return True
    return False


def _in_window(jd_ut: float, start_jd: float, end_jd: float) -> bool:
    return start_jd <= jd_ut < end_jd


def score_muhurta_instant(
    jd_ut: float,
    sun_lon_deg: float,
    moon_lon_deg: float,
    lagna_lon_deg: float,
    *,
    natal_moon_lon_deg: float | None = None,
    sunrise_jd_ut: float | None = None,
    sunset_jd_ut: float | None = None,
    next_sunrise_jd_ut: float | None = None,
    vara_index: int | None = None,
    gandanta_orb_deg: float = DEFAULT_GANDANTA_ORB_DEG,
) -> MuhurtaInstantEvaluation:
    """Evaluate and score a single candidate Muhurta timestamp on a deterministic 0..100 scale."""
    sr_jd = float(sunrise_jd_ut) if sunrise_jd_ut is not None else (float(int(jd_ut - 0.5)) + 0.75)
    ss_jd = float(sunset_jd_ut) if sunset_jd_ut is not None else (sr_jd + 0.5)
    next_sr = float(next_sunrise_jd_ut) if next_sunrise_jd_ut is not None else (sr_jd + 1.0)

    s_lon = normalize_degrees(sun_lon_deg)
    m_lon = normalize_degrees(moon_lon_deg)
    l_lon = normalize_degrees(lagna_lon_deg)

    panchanga = compute_panchanga(
        s_lon,
        m_lon,
        jd_ut=jd_ut,
        sunrise_jd_ut=sr_jd,
        vara_index=vara_index,
    )
    windows: MuhurtaWindows = compute_muhurta_windows(
        sr_jd,
        ss_jd,
        next_sunrise_jd=next_sr,
        vara_index=panchanga.vara.index,
    )

    lagna_sign_idx = min(int(l_lon // 30.0), 11)
    moon_sign_idx = min(int(m_lon // 30.0), 11)

    panchaka = evaluate_panchaka(
        tithi_num=panchanga.tithi.number,
        vara_num=panchanga.vara.index + 1,
        nakshatra_num=panchanga.nakshatra.number,
        lagna_sign=lagna_sign_idx + 1,
    )
    siddha = evaluate_siddha_yogas(
        vara_index=panchanga.vara.index,
        nakshatra_index=panchanga.nakshatra.index,
        tithi_num=panchanga.tithi.number,
        moon_sign_index=moon_sign_idx,
    )

    tara_res: TaraBalaResult | None = None
    chandra_res: ChandrabalaResult | None = None
    if natal_moon_lon_deg is not None:
        n_m_lon = normalize_degrees(natal_moon_lon_deg)
        tara_res = compute_tara_bala(n_m_lon, m_lon)
        natal_sign_1based = min(int(n_m_lon // 30.0), 11) + 1
        transit_sign_1based = moon_sign_idx + 1
        chandra_res = evaluate_chandrabala(natal_sign_1based, transit_sign_1based)

    moon_gandanta = is_gandanta_degree(m_lon, orb_deg=gandanta_orb_deg)
    lagna_gandanta = is_gandanta_degree(l_lon, orb_deg=gandanta_orb_deg)

    in_rahu = _in_window(jd_ut, windows.rahu_kalam.start_jd, windows.rahu_kalam.end_jd)
    in_yama = _in_window(jd_ut, windows.yamagandam.start_jd, windows.yamagandam.end_jd)
    in_gulika = _in_window(jd_ut, windows.gulika_kalam.start_jd, windows.gulika_kalam.end_jd)
    in_abhijit = _in_window(jd_ut, windows.abhijit_muhurta.start_jd, windows.abhijit_muhurta.end_jd)
    in_durmuhurta = any(_in_window(jd_ut, d.start_jd, d.end_jd) for d in windows.durmuhurtas)

    # Deterministic scoring (base 60.0, clamped to 0.0..100.0)
    score = 60.0
    doshas: list[str] = []
    benefics: list[str] = []

    # 1. Tithi quality
    if panchanga.tithi.group == "Rikta":
        score -= 15.0
        doshas.append(f"Rikta Tithi ({panchanga.tithi.name})")
    elif panchanga.tithi.number == 30:
        score -= 15.0
        doshas.append("Amavasya Tithi")
    elif panchanga.tithi.group in ("Purna", "Bhadra", "Jaya", "Nanda"):
        score += 6.0
        benefics.append(f"{panchanga.tithi.group} Tithi ({panchanga.tithi.name})")

    # 2. Yoga quality
    if panchanga.yoga.is_benefic:
        score += 6.0
        benefics.append(f"Benefic Yoga ({panchanga.yoga.name})")
    else:
        score -= 10.0
        if panchanga.yoga.name in ("Vyatipata", "Vaidhriti"):
            score -= 8.0
        doshas.append(f"Malefic Yoga ({panchanga.yoga.name})")

    # 3. Karana quality
    if panchanga.karana.is_vishti_bhadra:
        score -= 16.0
        doshas.append("Vishti (Bhadra) Karana")
    elif panchanga.karana.kind == "Fixed" and panchanga.karana.name != "Kimstughna":
        score -= 10.0
        doshas.append(f"Fixed Inauspicious Karana ({panchanga.karana.name})")
    else:
        score += 4.0
        benefics.append(f"Auspicious Karana ({panchanga.karana.name})")

    # 4. Panchaka Rahita
    if panchaka.is_auspicious:
        score += 8.0
        benefics.append("Panchaka Shuddha")
    else:
        score -= 12.0
        doshas.append(panchaka.name)

    # 5. Siddha Yogas & Dagdha Rasi
    if siddha.amrita_siddhi:
        score += 12.0
        benefics.append("Amrita Siddhi Yoga")
    if siddha.sarvartha_siddhi:
        score += 10.0
        benefics.append("Sarvartha Siddhi Yoga")
    if siddha.guru_pushya:
        score += 10.0
        benefics.append("Guru Pushya Yoga")
    if siddha.ravi_pushya:
        score += 8.0
        benefics.append("Ravi Pushya Yoga")
    if siddha.dwipushkara:
        score += 4.0
        benefics.append("Dwipushkara Yoga")
    if siddha.tripushkara:
        score += 5.0
        benefics.append("Tripushkara Yoga")
    if siddha.moon_in_dagdha_rasi:
        score -= 12.0
        doshas.append(f"Moon in Dagdha Rasi ({RASI_NAMES[moon_sign_idx]})")

    # 6. Gandanta junctions
    if moon_gandanta:
        score -= 18.0
        doshas.append("Moon in Gandanta junction")
    if lagna_gandanta:
        score -= 14.0
        doshas.append("Lagna in Gandanta junction")

    # 7. Kalam & Muhurta windows
    if in_abhijit:
        score += 10.0
        benefics.append("Abhijit Muhurta")
    if in_rahu:
        score -= 18.0
        doshas.append("Rahu Kalam")
    if in_yama:
        score -= 12.0
        doshas.append("Yamagandam")
    if in_gulika:
        score += 2.0
        benefics.append("Gulika Kalam")
    if in_durmuhurta:
        score -= 10.0
        doshas.append("Durmuhurta")

    # 8. Personal Tarabala & Chandrabala (if natal Moon supplied)
    if tara_res is not None:
        if tara_res.is_benefic:
            score += 8.0
            benefics.append(f"Benefic Tara Bala ({tara_res.tara_name})")
        else:
            score -= 12.0
            doshas.append(f"Inauspicious Tara Bala ({tara_res.tara_name})")

    if chandra_res is not None:
        if chandra_res.is_auspicious:
            score += 8.0
            benefics.append(f"Auspicious Chandrabala ({chandra_res.house_from_natal_moon}th from Moon)")
        elif chandra_res.is_inauspicious:
            penalty = 18.0 if chandra_res.house_from_natal_moon == 8 else 12.0
            score -= penalty
            doshas.append(f"Inauspicious Chandrabala ({chandra_res.house_from_natal_moon}th from Moon)")

    clamped_score = round(min(max(score, 0.0), 100.0), 4)
    if clamped_score >= 80.0:
        grade = "Uttama (Excellent)"
    elif clamped_score >= 65.0:
        grade = "Madhyama (Good)"
    elif clamped_score >= 50.0:
        grade = "Samanya (Neutral)"
    else:
        grade = "Varjya (Avoid)"

    is_recommended = (
        clamped_score >= 65.0
        and not moon_gandanta
        and not lagna_gandanta
        and not in_rahu
        and not panchanga.karana.is_vishti_bhadra
    )

    receipt_payload = {
        "module": "ephemeris_oss.jyotish_transit.muhurta_search",
        "version": __version__,
        "jd_ut": float(jd_ut),
        "sun_lon_deg": round(s_lon, 8),
        "moon_lon_deg": round(m_lon, 8),
        "lagna_lon_deg": round(l_lon, 8),
        "score": clamped_score,
        "grade": grade,
        "panchaka": panchaka.name,
        "active_yogas": list(siddha.active_yogas),
        "dosha_flags": doshas,
    }
    r_sha = canonical_hash(receipt_payload)

    return MuhurtaInstantEvaluation(
        jd_ut=float(jd_ut),
        iso_utc=jd_to_iso_utc(jd_ut),
        score=clamped_score,
        grade=grade,
        is_recommended=is_recommended,
        panchanga=panchanga,
        panchaka=panchaka,
        siddha_yogas=siddha,
        tara_bala=tara_res,
        chandra_bala=chandra_res,
        lagna_sign_index=lagna_sign_idx,
        lagna_sign_name=RASI_NAMES[lagna_sign_idx],
        moon_gandanta=moon_gandanta,
        lagna_gandanta=lagna_gandanta,
        in_rahu_kalam=in_rahu,
        in_yamagandam=in_yama,
        in_gulika_kalam=in_gulika,
        in_abhijit_muhurta=in_abhijit,
        in_durmuhurta=in_durmuhurta,
        dosha_flags=tuple(doshas),
        benefic_factors=tuple(benefics),
        receipt=receipt_payload,
        receipt_sha256=r_sha,
    )


def scan_muhurta_windows(
    samples: Sequence[Mapping[str, Any]],
    *,
    natal_moon_lon_deg: float | None = None,
    threshold_score: float = 65.0,
) -> MuhurtaScanReport:
    """Scan a sequence of candidate timestamps and aggregate contiguous auspicious Muhurta windows.

    Each entry in `samples` must provide:
    - `jd_ut`: Julian Day UT
    - `sun_lon_deg`: sidereal solar longitude (degrees)
    - `moon_lon_deg`: sidereal lunar longitude (degrees)
    - `lagna_lon_deg`: sidereal ascendant longitude (degrees)
    And optionally `sunrise_jd_ut`, `sunset_jd_ut`, `next_sunrise_jd_ut`, `vara_index`.
    """
    if not samples:
        raise ValueError("samples must contain at least one candidate instant")

    ordered_samples = sorted(samples, key=lambda item: float(item["jd_ut"]))
    evaluations: list[MuhurtaInstantEvaluation] = []
    for item in ordered_samples:
        ev = score_muhurta_instant(
            jd_ut=float(item["jd_ut"]),
            sun_lon_deg=float(item["sun_lon_deg"]),
            moon_lon_deg=float(item["moon_lon_deg"]),
            lagna_lon_deg=float(item["lagna_lon_deg"]),
            natal_moon_lon_deg=natal_moon_lon_deg,
            sunrise_jd_ut=float(item["sunrise_jd_ut"]) if "sunrise_jd_ut" in item and item["sunrise_jd_ut"] is not None else None,
            sunset_jd_ut=float(item["sunset_jd_ut"]) if "sunset_jd_ut" in item and item["sunset_jd_ut"] is not None else None,
            next_sunrise_jd_ut=float(item["next_sunrise_jd_ut"]) if "next_sunrise_jd_ut" in item and item["next_sunrise_jd_ut"] is not None else None,
            vara_index=int(item["vara_index"]) if "vara_index" in item and item["vara_index"] is not None else None,
        )
        evaluations.append(ev)

    # Estimate step duration for single-point intervals
    if len(evaluations) >= 2:
        default_step_jd = max(evaluations[1].jd_ut - evaluations[0].jd_ut, 1.0 / 1440.0)
    else:
        default_step_jd = 15.0 / 1440.0

    intervals: list[MuhurtaWindowInterval] = []
    current_run: list[MuhurtaInstantEvaluation] = []

    def _flush_run(run: list[MuhurtaInstantEvaluation]) -> None:
        if not run:
            return
        start_jd = run[0].jd_ut
        end_jd = run[-1].jd_ut + default_step_jd if len(run) == 1 else run[-1].jd_ut
        peak_ev = max(run, key=lambda r: r.score)
        mean_sc = round(sum(r.score for r in run) / len(run), 4)
        yogas_seen: list[str] = []
        for r in run:
            for y in r.siddha_yogas.active_yogas:
                if y not in yogas_seen:
                    yogas_seen.append(y)
        intervals.append(
            MuhurtaWindowInterval(
                start_jd=start_jd,
                end_jd=end_jd,
                start_iso_utc=jd_to_iso_utc(start_jd),
                end_iso_utc=jd_to_iso_utc(end_jd),
                duration_minutes=round((end_jd - start_jd) * 1440.0, 4),
                peak_jd=peak_ev.jd_ut,
                peak_score=peak_ev.score,
                mean_score=mean_sc,
                sample_count=len(run),
                active_yogas=tuple(yogas_seen),
            )
        )

    for ev in evaluations:
        qualifies = ev.score >= threshold_score and not ev.moon_gandanta and not ev.lagna_gandanta and not ev.in_rahu_kalam
        if qualifies:
            current_run.append(ev)
        else:
            _flush_run(current_run)
            current_run = []
    _flush_run(current_run)

    best_ev = max(evaluations, key=lambda r: r.score)
    receipt = {
        "module": "ephemeris_oss.jyotish_transit.muhurta_search",
        "version": __version__,
        "sample_count": len(evaluations),
        "threshold_score": float(threshold_score),
        "best_jd_ut": best_ev.jd_ut,
        "best_score": best_ev.score,
        "recommended_window_count": len(intervals),
        "instant_hashes": [e.receipt_sha256 for e in evaluations],
    }
    receipt_sha256 = canonical_hash(receipt)

    return MuhurtaScanReport(
        sample_count=len(evaluations),
        threshold_score=float(threshold_score),
        best_instant=best_ev,
        instants=tuple(evaluations),
        recommended_windows=tuple(intervals),
        receipt=receipt,
        receipt_sha256=receipt_sha256,
    )


__all__ = [
    "AMRITA_SIDDHI_EXCLUDED_PAKSHA_TITHI",
    "AMRITA_SIDDHI_NAKSHATRA",
    "BHADRA_PAKSHA_TITHIS",
    "CHANDRABALA_BAD_HOUSES",
    "CHANDRABALA_GOOD_HOUSES",
    "CHANDRABALA_NEUTRAL_HOUSES",
    "DAGDHA_RASI_BY_PAKSHA_TITHI",
    "DEFAULT_GANDANTA_ORB_DEG",
    "DWIPUSHKARA_NAKSHATRA_INDICES",
    "GANDANTA_JUNCTIONS_DEG",
    "MuhurtaInstantEvaluation",
    "MuhurtaScanReport",
    "MuhurtaWindowInterval",
    "PANCHAKA_CATALOG",
    "PUSHKARA_VARA_INDICES",
    "PanchakaResult",
    "SARVARTHA_SIDDHI_NAKSHATRAS",
    "SiddhaYogaEvaluation",
    "TRIPUSHKARA_NAKSHATRA_INDICES",
    "ChandrabalaResult",
    "evaluate_chandrabala",
    "evaluate_panchaka",
    "evaluate_siddha_yogas",
    "is_gandanta_degree",
    "scan_muhurta_windows",
    "score_muhurta_instant",
]
