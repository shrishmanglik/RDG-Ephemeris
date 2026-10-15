"""Clean-room Lagadha Vedanga Jyotisha (c. 1350-1200 BCE) 5-year Yuga luni-solar engine.

Implements the earliest systematic Sanskrit astronomical treatise (*Rigveda* and
*Yajurveda* recensions of *Lagadha's Vedanga Jyotisha*):
1. **Five-Year Yuga Fundamental Invariants**:
   - Solar years per Yuga: `5` (`Samvatsara`, `Parivatsara`, `Idavatsara`,
     `Anuvatsara`, `Idvatsara`).
   - Civil (*Savana*) days per Yuga: `1,830` (`366` Savana days per solar year;
     `183` Savana days per *Ayana*; `61` Savana days per *Ritu*).
   - Solar (*Saura*) days per Yuga: `1,800` (`360` Saura days per solar year).
   - Synodic lunar (*Chandra*) months per Yuga: `62` (`60` regular solar-aligned
     months + `2` intercalary *Adhika Masa* months inserted at month 31 and month 62).
   - Lunar *Tithis* per Yuga: `1,860` (`62 * 30` Tithis; `30` *Avama* / *Kshaya*
     omitted Tithis across `1,830` Savana days, or 1 omitted Tithi every `61`
     Savana days = `62` Tithis).
   - Sidereal lunar (*Nakshatra*) months per Yuga: `67` (`67 * 27 = 1,809`
     lunar Nakshatra transits per Yuga).
   - Solar Nakshatra transits per Yuga: `135` (`5 * 27 = 135`).
   - *Parvans* (half-months / syzygies) per Yuga: `124` (`62 * 2`).
   - *Bhamsha* (*Amsha*) subdivisions per Nakshatra: `124` (`1/124`th part of a
     Nakshatra; in one Parvan of `15` Tithis, the Sun traverses `135 / 124 = 1 + 11/124`
     Nakshatras and the Moon traverses `1809 / 124 = 14 + 73/124` Nakshatras).
2. **Yuga Epoch**:
   - The 5-year Yuga begins at winter solstice (*Uttarayana* start) on *Magha
     Shukla Pratipada* (`days_into_yuga = 0`) with both the Sun and the Moon at
     the beginning of *Shravishtha* (*Dhanishta*, index 22 in the classical
     Ashwini-first 27-Nakshatra catalog).
"""

from __future__ import annotations

from dataclasses import dataclass
import math
from typing import Final

from ..engine.receipt import canonical_hash
from ..jyotish.nakshatra import NAKSHATRA_NAMES

VEDANGA_YUGA_YEARS: Final[int] = 5
VEDANGA_YUGA_SAVANA_DAYS: Final[int] = 1_830
VEDANGA_YUGA_SAURA_DAYS: Final[int] = 1_800
VEDANGA_YUGA_SYNODIC_MONTHS: Final[int] = 62
VEDANGA_YUGA_TITHIS: Final[int] = 1_860
VEDANGA_YUGA_SIDEREAL_LUNAR_MONTHS: Final[int] = 67
VEDANGA_YUGA_LUNAR_NAKSHATRAS: Final[int] = 1_809
VEDANGA_YUGA_SOLAR_NAKSHATRAS: Final[int] = 135
VEDANGA_YUGA_ADHIKA_MASAS: Final[int] = 2
VEDANGA_YUGA_PARVANS: Final[int] = 124
VEDANGA_BHAMSHA_PER_NAKSHATRA: Final[int] = 124
VEDANGA_KSHAYA_TITHIS_PER_YUGA: Final[int] = 30
VEDANGA_SAVANA_DAYS_PER_YEAR: Final[int] = 366
VEDANGA_SAVANA_DAYS_PER_AYANA: Final[int] = 183
VEDANGA_SAVANA_DAYS_PER_RITU: Final[int] = 61

VEDANGA_SAMVATSARA_NAMES: Final[tuple[str, ...]] = (
    "Samvatsara",
    "Parivatsara",
    "Idavatsara",
    "Anuvatsara",
    "Idvatsara",
)

VEDANGA_AYANA_NAMES: Final[tuple[str, str]] = (
    "Uttarayana",
    "Dakshinayana",
)

VEDANGA_RITU_NAMES: Final[tuple[str, ...]] = (
    "Shishira",
    "Vasanta",
    "Grishma",
    "Varsha",
    "Sharad",
    "Hemanta",
)

# In Lagadha's Vedanga Jyotisha, the Yuga begins with Sun and Moon conjoined at the
# start of Shravishtha (Dhanishta, canonical index 22 in the Ashwini-led 27 list).
VEDANGA_EPOCH_NAKSHATRA_INDEX: Final[int] = 22
VEDANGA_NAKSHATRA_ORDER: Final[tuple[str, ...]] = tuple(
    NAKSHATRA_NAMES[(VEDANGA_EPOCH_NAKSHATRA_INDEX + i) % 27] for i in range(27)
)


@dataclass(frozen=True)
class VedangaYugaState:
    """Complete luni-solar state at a given point in the 5-year Vedanga Jyotisha Yuga."""

    days_into_yuga_input: float
    days_into_yuga: float
    yuga_cycle: int
    year_index: int
    year: int
    samvatsara_name: str
    day_of_year: float
    ayana_index_in_year: int
    ayana_number_in_yuga: int
    ayana: str
    ritu_index_in_year: int
    ritu_name: str
    synodic_month_index: int
    synodic_month_number: int
    is_adhika_masa: bool
    adhika_masas_elapsed: int
    parvan_index: int
    tithi_in_yuga: float
    tithi_index_in_yuga: int
    tithi_index: int
    tithi: int
    tithi_continuous: float
    paksha: str
    kshaya_tithis_elapsed: int
    solar_nakshatras_elapsed: float
    vedanga_solar_nakshatra_index: int
    solar_nakshatra_index: int
    solar_nakshatra: str
    solar_bhamsha: float
    solar_bhamsha_index: int
    lunar_nakshatras_elapsed: float
    vedanga_lunar_nakshatra_index: int
    lunar_nakshatra_index: int
    lunar_nakshatra: str
    bhamsha: float
    bhamsha_index: int
    bhamsha_number: int
    receipt_sha256: str


def compute_vedanga_yuga_state(days_into_yuga: float) -> VedangaYugaState:
    """Compute the exact Lagadha Vedanga Jyotisha 5-year Yuga state for ``days_into_yuga``.

    Parameters
    ----------
    days_into_yuga:
        Civil (*Savana*) days elapsed from the start of the 5-year Yuga (`Magha
        Shukla Pratipada` at winter solstice in *Dhanishta*). Values outside
        ``[0.0, 1830.0)`` wrap modulo ``1830.0`` while recording ``yuga_cycle``.

    Returns
    -------
    VedangaYugaState
        Year, Samvatsara name, Ayana (`Uttarayana` / `Dakshinayana`), Ritu,
        solar Nakshatra, lunar Nakshatra, Tithi, Bhamsha (`1/124`th of a
        Nakshatra), Adhika Masa status, and deterministic SHA-256 receipt.
    """
    raw_days = float(days_into_yuga)
    if not math.isfinite(raw_days):
        raise ValueError(f"days_into_yuga must be finite, got {days_into_yuga!r}")

    yuga_cycle = int(math.floor(raw_days / float(VEDANGA_YUGA_SAVANA_DAYS)))
    d = raw_days % float(VEDANGA_YUGA_SAVANA_DAYS)
    if d < 0.0 or d >= float(VEDANGA_YUGA_SAVANA_DAYS):
        d = 0.0

    # 1. Solar Year (Samvatsara) and Day of Year (366 Savana days per solar year)
    year_idx = min(int(d // float(VEDANGA_SAVANA_DAYS_PER_YEAR)), VEDANGA_YUGA_YEARS - 1)
    year_num = year_idx + 1
    samvatsara = VEDANGA_SAMVATSARA_NAMES[year_idx]
    day_of_year = d - float(year_idx * VEDANGA_SAVANA_DAYS_PER_YEAR)

    # 2. Ayana (183 Savana days per Ayana: Uttarayana then Dakshinayana)
    ayana_in_year = 0 if day_of_year < float(VEDANGA_SAVANA_DAYS_PER_AYANA) else 1
    ayana_name = VEDANGA_AYANA_NAMES[ayana_in_year]
    ayana_in_yuga = min(int(d // float(VEDANGA_SAVANA_DAYS_PER_AYANA)) + 1, 10)

    # 3. Ritu (61 Savana days per Ritu, 6 Ritus per 366-day solar year)
    ritu_in_year = min(int(day_of_year // float(VEDANGA_SAVANA_DAYS_PER_RITU)), 5)
    ritu_name = VEDANGA_RITU_NAMES[ritu_in_year]

    # 4. Tithis (1860 Tithis in 1830 Savana days -> 62/61 Tithis per Savana day)
    tithi_in_yuga = (d * float(VEDANGA_YUGA_TITHIS)) / float(VEDANGA_YUGA_SAVANA_DAYS)
    tithi_idx_yuga = min(int(math.floor(tithi_in_yuga + 1e-12)), VEDANGA_YUGA_TITHIS - 1)
    synodic_month_idx = min(tithi_idx_yuga // 30, VEDANGA_YUGA_SYNODIC_MONTHS - 1)
    synodic_month_num = synodic_month_idx + 1

    # In the 62-month Yuga, the 2 intercalary Adhika Masas occur at month 31 (mid-Yuga)
    # and month 62 (end of Yuga).
    is_adhika = synodic_month_num in (31, 62)
    if synodic_month_num < 31:
        adhika_elapsed = 0
    elif synodic_month_num < 62:
        adhika_elapsed = 1
    else:
        adhika_elapsed = 2

    parvan_idx = min(tithi_idx_yuga // 15, VEDANGA_YUGA_PARVANS - 1)
    tithi_idx = tithi_idx_yuga % 30
    tithi_num = tithi_idx + 1
    tithi_cont = (tithi_in_yuga % 30.0) + 1.0
    if tithi_cont >= 31.0:
        tithi_cont = 1.0
    paksha = "Shukla" if tithi_num <= 15 else "Krishna"
    kshaya_elapsed = int(d // 61.0)

    # 5. Solar Nakshatra (135 solar Nakshatra transits in 1830 Savana days)
    solar_naks_elapsed = (d * float(VEDANGA_YUGA_SOLAR_NAKSHATRAS)) / float(VEDANGA_YUGA_SAVANA_DAYS)
    solar_nak_int = int(math.floor(solar_naks_elapsed + 1e-12))
    vedanga_solar_idx = solar_nak_int % 27
    solar_nak_idx = (VEDANGA_EPOCH_NAKSHATRA_INDEX + vedanga_solar_idx) % 27
    solar_nak_name = NAKSHATRA_NAMES[solar_nak_idx]
    solar_frac = max(0.0, min(solar_naks_elapsed - math.floor(solar_naks_elapsed + 1e-12), 1.0 - 1e-15))
    solar_bhamsha = solar_frac * float(VEDANGA_BHAMSHA_PER_NAKSHATRA)
    solar_bhamsha_idx = min(int(math.floor(solar_bhamsha + 1e-12)), VEDANGA_BHAMSHA_PER_NAKSHATRA - 1)

    # 6. Lunar Nakshatra and Bhamsha (1809 lunar Nakshatras in 1830 Savana days)
    lunar_naks_elapsed = (d * float(VEDANGA_YUGA_LUNAR_NAKSHATRAS)) / float(VEDANGA_YUGA_SAVANA_DAYS)
    lunar_nak_int = int(math.floor(lunar_naks_elapsed + 1e-12))
    vedanga_lunar_idx = lunar_nak_int % 27
    lunar_nak_idx = (VEDANGA_EPOCH_NAKSHATRA_INDEX + vedanga_lunar_idx) % 27
    lunar_nak_name = NAKSHATRA_NAMES[lunar_nak_idx]
    lunar_frac = max(0.0, min(lunar_naks_elapsed - math.floor(lunar_naks_elapsed + 1e-12), 1.0 - 1e-15))
    bhamsha_val = lunar_frac * float(VEDANGA_BHAMSHA_PER_NAKSHATRA)
    bhamsha_idx = min(int(math.floor(bhamsha_val + 1e-12)), VEDANGA_BHAMSHA_PER_NAKSHATRA - 1)
    bhamsha_num = bhamsha_idx + 1

    receipt = canonical_hash(
        {
            "engine": "vedanga_jyotisha_yuga_v1",
            "days_into_yuga": round(d, 12),
            "yuga_cycle": yuga_cycle,
            "year": year_num,
            "samvatsara_name": samvatsara,
            "ayana": ayana_name,
            "synodic_month_number": synodic_month_num,
            "tithi": tithi_num,
            "solar_nakshatra": solar_nak_name,
            "lunar_nakshatra": lunar_nak_name,
            "bhamsha": round(bhamsha_val, 12),
        }
    )

    return VedangaYugaState(
        days_into_yuga_input=raw_days,
        days_into_yuga=d,
        yuga_cycle=yuga_cycle,
        year_index=year_idx,
        year=year_num,
        samvatsara_name=samvatsara,
        day_of_year=day_of_year,
        ayana_index_in_year=ayana_in_year,
        ayana_number_in_yuga=ayana_in_yuga,
        ayana=ayana_name,
        ritu_index_in_year=ritu_in_year,
        ritu_name=ritu_name,
        synodic_month_index=synodic_month_idx,
        synodic_month_number=synodic_month_num,
        is_adhika_masa=is_adhika,
        adhika_masas_elapsed=adhika_elapsed,
        parvan_index=parvan_idx,
        tithi_in_yuga=tithi_in_yuga,
        tithi_index_in_yuga=tithi_idx_yuga,
        tithi_index=tithi_idx,
        tithi=tithi_num,
        tithi_continuous=tithi_cont,
        paksha=paksha,
        kshaya_tithis_elapsed=kshaya_elapsed,
        solar_nakshatras_elapsed=solar_naks_elapsed,
        vedanga_solar_nakshatra_index=vedanga_solar_idx,
        solar_nakshatra_index=solar_nak_idx,
        solar_nakshatra=solar_nak_name,
        solar_bhamsha=solar_bhamsha,
        solar_bhamsha_index=solar_bhamsha_idx,
        lunar_nakshatras_elapsed=lunar_naks_elapsed,
        vedanga_lunar_nakshatra_index=vedanga_lunar_idx,
        lunar_nakshatra_index=lunar_nak_idx,
        lunar_nakshatra=lunar_nak_name,
        bhamsha=bhamsha_val,
        bhamsha_index=bhamsha_idx,
        bhamsha_number=bhamsha_num,
        receipt_sha256=receipt,
    )


__all__ = [
    "VEDANGA_AYANA_NAMES",
    "VEDANGA_BHAMSHA_PER_NAKSHATRA",
    "VEDANGA_EPOCH_NAKSHATRA_INDEX",
    "VEDANGA_KSHAYA_TITHIS_PER_YUGA",
    "VEDANGA_NAKSHATRA_ORDER",
    "VEDANGA_RITU_NAMES",
    "VEDANGA_SAMVATSARA_NAMES",
    "VEDANGA_SAVANA_DAYS_PER_AYANA",
    "VEDANGA_SAVANA_DAYS_PER_RITU",
    "VEDANGA_SAVANA_DAYS_PER_YEAR",
    "VEDANGA_YUGA_ADHIKA_MASAS",
    "VEDANGA_YUGA_LUNAR_NAKSHATRAS",
    "VEDANGA_YUGA_PARVANS",
    "VEDANGA_YUGA_SAURA_DAYS",
    "VEDANGA_YUGA_SAVANA_DAYS",
    "VEDANGA_YUGA_SIDEREAL_LUNAR_MONTHS",
    "VEDANGA_YUGA_SOLAR_NAKSHATRAS",
    "VEDANGA_YUGA_SYNODIC_MONTHS",
    "VEDANGA_YUGA_TITHIS",
    "VEDANGA_YUGA_YEARS",
    "VedangaYugaState",
    "compute_vedanga_yuga_state",
]
