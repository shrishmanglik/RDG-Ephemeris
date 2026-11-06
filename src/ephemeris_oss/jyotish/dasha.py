"""Clean-room Multi-Dasha Solver (5 levels: Mahadasha to Prana) and Jaimini Chara Karakas.

Mathematical formulations follow *Brihat Parashara Hora Shastra* (Chapters 28, 32, 46-48)
and *Jaimini Upadesha Sutras*:
- Vimshottari Dasha (120-year cycle across 9 grahas)
- Ashtottari Dasha (108-year cycle across 8 grahas)
- Yogini Dasha (36-year cycle across 8 Yoginis)
- Jaimini Chara Dasha (12-sign Savya/Apasavya progression with Scorpio/Aquarius co-lords)
- Jaimini Chara Karakas (7-karaka and 8-karaka schemes from Atmakaraka to Darakaraka)
- 5-level recursive temporal subdivision (`Mahadasha`, `Antardasha`, `Pratyantardasha`,
  `Sookshma`, `Prana`) with exact Julian Day (`start_jd`, `end_jd`) and ISO-8601 UTC timestamps.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
import math
from typing import Final, Mapping, Sequence

import erfa

from .nakshatra import (
    NAKSHATRA_SPAN_DEG,
    RASI_NAMES,
    VIMSHOTTARI_RULERS,
    abhijit_position,
    nakshatra_position,
    normalize_degrees,
)
from .vargas import EXALTATION_SIGNS, DEBILITATION_SIGNS, resolve_jaimini_sign_lord

SOLAR_YEAR_DAYS: Final[float] = 365.2425
SAVANA_YEAR_DAYS: Final[float] = 360.0

LEVEL_NAMES: Final[tuple[str, ...]] = (
    "Mahadasha",
    "Antardasha",
    "Pratyantardasha",
    "Sookshma",
    "Prana",
)

VIMSHOTTARI_YEARS: Final[Mapping[str, float]] = {
    "Ketu": 7.0,
    "Venus": 20.0,
    "Sun": 6.0,
    "Moon": 10.0,
    "Mars": 7.0,
    "Rahu": 18.0,
    "Jupiter": 16.0,
    "Saturn": 19.0,
    "Mercury": 17.0,
}
VIMSHOTTARI_TOTAL_YEARS: Final[float] = 120.0

ASHTOTTARI_RULERS: Final[tuple[str, ...]] = (
    "Sun",
    "Moon",
    "Mars",
    "Mercury",
    "Saturn",
    "Jupiter",
    "Rahu",
    "Venus",
)

ASHTOTTARI_YEARS: Final[Mapping[str, float]] = {
    "Sun": 6.0,
    "Moon": 15.0,
    "Mars": 8.0,
    "Mercury": 17.0,
    "Saturn": 10.0,
    "Jupiter": 19.0,
    "Rahu": 12.0,
    "Venus": 21.0,
}
ASHTOTTARI_TOTAL_YEARS: Final[float] = 108.0

# 28-nakshatra groups for Ashtottari Dasha (indices in 0..27 where 21 is Abhijit)
ASHTOTTARI_28_GROUPS: Final[tuple[tuple[str, tuple[int, ...]], ...]] = (
    ("Sun", (5, 6, 7, 8)),          # Ardra, Punarvasu, Pushya, Ashlesha
    ("Moon", (9, 10, 11)),          # Magha, Purva Phalguni, Uttara Phalguni
    ("Mars", (12, 13, 14, 15)),     # Hasta, Chitra, Swati, Vishakha
    ("Mercury", (16, 17, 18)),      # Anuradha, Jyeshtha, Mula
    ("Saturn", (19, 20, 21, 22)),   # Purva Ashadha, Uttara Ashadha, Abhijit, Shravana
    ("Jupiter", (23, 24, 25)),      # Dhanishta, Shatabhisha, Purva Bhadrapada
    ("Rahu", (26, 27, 0, 1)),       # Uttara Bhadrapada, Revati, Ashwini, Bharani
    ("Venus", (2, 3, 4)),           # Krittika, Rohini, Mrigashirsha
)

YOGINI_CATALOG: Final[tuple[tuple[str, str, float], ...]] = (
    ("Mangala", "Moon", 1.0),
    ("Pingala", "Sun", 2.0),
    ("Dhanya", "Jupiter", 3.0),
    ("Bhramari", "Mars", 4.0),
    ("Bhadrika", "Mercury", 5.0),
    ("Ulka", "Saturn", 6.0),
    ("Siddha", "Venus", 7.0),
    ("Sankata", "Rahu", 8.0),
)
YOGINI_NAMES: Final[tuple[str, ...]] = tuple(item[0] for item in YOGINI_CATALOG)
YOGINI_YEARS: Final[Mapping[str, float]] = {item[0]: item[2] for item in YOGINI_CATALOG}
YOGINI_LORDS: Final[Mapping[str, str]] = {item[0]: item[1] for item in YOGINI_CATALOG}
YOGINI_TOTAL_YEARS: Final[float] = 36.0

# Savya (odd-footed / Vishama Pada) signs: Aries, Taurus, Gemini, Libra, Scorpio, Sagittarius
SAVYA_SIGNS: Final[frozenset[int]] = frozenset({0, 1, 2, 6, 7, 8})

KARAKA_7_ROLES: Final[tuple[tuple[str, str], ...]] = (
    ("AK", "Atmakaraka"),
    ("AmK", "Amatyakaraka"),
    ("BK", "Bhratrikaraka"),
    ("MK", "Matrikaraka"),
    ("PK", "Putrakaraka"),
    ("GK", "Gnatikaraka"),
    ("DK", "Darakaraka"),
)

KARAKA_8_ROLES: Final[tuple[tuple[str, str], ...]] = (
    ("AK", "Atmakaraka"),
    ("AmK", "Amatyakaraka"),
    ("BK", "Bhratrikaraka"),
    ("MK", "Matrikaraka"),
    ("PiK", "Pitrikaraka"),
    ("PK", "Putrakaraka"),
    ("GK", "Gnatikaraka"),
    ("DK", "Darakaraka"),
)


@dataclass(frozen=True)
class DashaPeriod:
    """A single Dasha period at level 1..5 (`Mahadasha` through `Prana`)."""

    system: str
    level: int
    level_name: str
    lord: str
    lords_chain: tuple[str, ...]
    start_jd: float
    end_jd: float
    start_iso_utc: str
    end_iso_utc: str
    duration_days: float
    duration_years: float
    associated_planet: str | None = None
    sub_periods: tuple["DashaPeriod", ...] = ()


@dataclass(frozen=True)
class DashaTimeline:
    """Top-level Dasha calculation result with birth balance and Mahadasha tree."""

    system: str
    birth_jd: float
    birth_iso_utc: str
    year_days: float
    opening_lord: str
    birth_balance_years: float
    birth_balance_days: float
    mahadashas: tuple[DashaPeriod, ...]


@dataclass(frozen=True)
class CharaKarakaEntry:
    """A single Jaimini Chara Karaka assignment."""

    code: str
    role_name: str
    planet: str
    sidereal_lon_deg: float
    sign_index: int
    sign_name: str
    degree_in_sign: float
    effective_karaka_degree: float


def jd_to_iso_utc(jd_ut: float) -> str:
    """Convert a Julian Day number to an ISO-8601 UTC timestamp string (`YYYY-MM-DDTHH:MM:SSZ`)."""
    y, m, d, fd = erfa.jd2cal(float(jd_ut), 0.0)
    yi, mi, di = int(y), int(m), int(d)
    if 1 <= yi <= 9998:
        base = datetime(yi, mi, di, tzinfo=timezone.utc)
        dt = base + timedelta(days=float(fd))
        return dt.isoformat(timespec="seconds").replace("+00:00", "Z")
    total_sec = int(round(max(0.0, min(86399.0, float(fd) * 86400.0))))
    hh, rem = divmod(total_sec, 3600)
    mm, ss = divmod(rem, 60)
    sign = "-" if yi < 0 else ""
    return f"{sign}{abs(yi):04d}-{mi:02d}-{di:02d}T{hh:02d}:{mm:02d}:{ss:02d}Z"


def _subdivide_proportional(
    *,
    system: str,
    parent_chain: tuple[str, ...],
    parent_start_jd: float,
    parent_end_jd: float,
    start_lord: str,
    cycle_order: Sequence[str],
    cycle_weights: Mapping[str, float],
    total_weight: float,
    year_days: float,
    current_level: int,
    max_level: int,
    associated_planets: Mapping[str, str] | None = None,
    clip_start_jd: float | None = None,
) -> tuple[DashaPeriod, ...]:
    """Recursively subdivide a parent Dasha interval into proportional sub-periods."""
    span_days = parent_end_jd - parent_start_jd
    start_idx = cycle_order.index(start_lord)
    n = len(cycle_order)
    cursor_jd = parent_start_jd
    results: list[DashaPeriod] = []

    for i in range(n):
        lord = cycle_order[(start_idx + i) % n]
        weight = cycle_weights[lord]
        sub_days = span_days * (weight / total_weight) if i < n - 1 else (parent_end_jd - cursor_jd)
        s_jd = cursor_jd
        e_jd = cursor_jd + sub_days
        cursor_jd = e_jd

        if clip_start_jd is not None and e_jd <= clip_start_jd:
            continue

        chain = parent_chain + (lord,)
        children: tuple[DashaPeriod, ...] = ()
        if current_level < max_level:
            children = _subdivide_proportional(
                system=system,
                parent_chain=chain,
                parent_start_jd=s_jd,
                parent_end_jd=e_jd,
                start_lord=lord,
                cycle_order=cycle_order,
                cycle_weights=cycle_weights,
                total_weight=total_weight,
                year_days=year_days,
                current_level=current_level + 1,
                max_level=max_level,
                associated_planets=associated_planets,
                clip_start_jd=clip_start_jd,
            )

        eff_s_jd = max(s_jd, clip_start_jd) if clip_start_jd is not None else s_jd
        eff_days = e_jd - eff_s_jd
        results.append(
            DashaPeriod(
                system=system,
                level=current_level,
                level_name=LEVEL_NAMES[current_level - 1],
                lord=lord,
                lords_chain=chain,
                start_jd=eff_s_jd,
                end_jd=e_jd,
                start_iso_utc=jd_to_iso_utc(eff_s_jd),
                end_iso_utc=jd_to_iso_utc(e_jd),
                duration_days=eff_days,
                duration_years=eff_days / year_days,
                associated_planet=associated_planets.get(lord) if associated_planets else lord,
                sub_periods=children,
            )
        )
    return tuple(results)


def compute_vimshottari_dasha(
    moon_sidereal_lon_deg: float,
    birth_jd: float,
    *,
    year_days: float = SOLAR_YEAR_DAYS,
    max_level: int = 2,
    cycles: int = 1,
) -> DashaTimeline:
    """Compute the 120-year Vimshottari Dasha tree from natal Moon sidereal longitude.

    `max_level` may be 1..5 (`Mahadasha`, `Antardasha`, `Pratyantardasha`, `Sookshma`, `Prana`).
    For instant 5-level lookup at any target date without materializing all 9^5 nodes,
    see :func:`resolve_dasha_5_levels`.
    """
    if not 1 <= max_level <= 5:
        raise ValueError("max_level must be between 1 and 5")
    if year_days <= 0:
        raise ValueError("year_days must be positive")

    nak = nakshatra_position(moon_sidereal_lon_deg)
    opening_lord = nak.vimshottari_ruler
    start_idx = VIMSHOTTARI_RULERS.index(opening_lord)

    full_first_years = VIMSHOTTARI_YEARS[opening_lord]
    balance_years = full_first_years * nak.fraction_remaining
    balance_days = balance_years * year_days
    elapsed_days = (full_first_years - balance_years) * year_days

    virtual_start_jd = float(birth_jd) - elapsed_days
    cursor_jd = virtual_start_jd
    total_lords = 9 * max(1, int(cycles))
    mahadashas: list[DashaPeriod] = []

    for i in range(total_lords):
        lord = VIMSHOTTARI_RULERS[(start_idx + i) % 9]
        yrs = VIMSHOTTARI_YEARS[lord]
        span_days = yrs * year_days
        s_jd = cursor_jd
        e_jd = cursor_jd + span_days
        cursor_jd = e_jd

        children: tuple[DashaPeriod, ...] = ()
        if max_level > 1:
            children = _subdivide_proportional(
                system="Vimshottari",
                parent_chain=(lord,),
                parent_start_jd=s_jd,
                parent_end_jd=e_jd,
                start_lord=lord,
                cycle_order=VIMSHOTTARI_RULERS,
                cycle_weights=VIMSHOTTARI_YEARS,
                total_weight=VIMSHOTTARI_TOTAL_YEARS,
                year_days=year_days,
                current_level=2,
                max_level=max_level,
                clip_start_jd=float(birth_jd) if i == 0 else None,
            )

        eff_s_jd = float(birth_jd) if i == 0 else s_jd
        eff_days = e_jd - eff_s_jd
        mahadashas.append(
            DashaPeriod(
                system="Vimshottari",
                level=1,
                level_name="Mahadasha",
                lord=lord,
                lords_chain=(lord,),
                start_jd=eff_s_jd,
                end_jd=e_jd,
                start_iso_utc=jd_to_iso_utc(eff_s_jd),
                end_iso_utc=jd_to_iso_utc(e_jd),
                duration_days=eff_days,
                duration_years=eff_days / year_days,
                associated_planet=lord,
                sub_periods=children,
            )
        )

    return DashaTimeline(
        system="Vimshottari",
        birth_jd=float(birth_jd),
        birth_iso_utc=jd_to_iso_utc(birth_jd),
        year_days=year_days,
        opening_lord=opening_lord,
        birth_balance_years=balance_years,
        birth_balance_days=balance_days,
        mahadashas=tuple(mahadashas),
    )


def compute_ashtottari_dasha(
    moon_sidereal_lon_deg: float,
    birth_jd: float,
    *,
    year_days: float = SOLAR_YEAR_DAYS,
    max_level: int = 2,
) -> DashaTimeline:
    """Compute the 108-year Ashtottari Dasha tree using the classical 28-nakshatra mapping."""
    if not 1 <= max_level <= 5:
        raise ValueError("max_level must be between 1 and 5")

    ab = abhijit_position(moon_sidereal_lon_deg)
    idx_28 = ab.nakshatra_28_index

    opening_lord = "Sun"
    group_indices: tuple[int, ...] = (5, 6, 7, 8)
    for ruler, indices in ASHTOTTARI_28_GROUPS:
        if idx_28 in indices:
            opening_lord = ruler
            group_indices = indices
            break

    pos_in_group = group_indices.index(idx_28)
    # In Ashtottari, each nakshatra within the ruler's group carries equal share of the ruler's dasha,
    # or the balance within the current nakshatra is used. In Jagannatha Hora / BPHS standard,
    # the fraction elapsed within the current nakshatra (or across the group) determines the balance;
    # using the current nakshatra's fraction remaining matches standard JH per-nakshatra Ashtottari balance.
    _ = pos_in_group
    frac_rem = ab.fraction_remaining
    frac_el = ab.fraction_elapsed

    full_first_years = ASHTOTTARI_YEARS[opening_lord]
    balance_years = full_first_years * frac_rem
    balance_days = balance_years * year_days
    elapsed_days = full_first_years * frac_el * year_days

    start_idx = ASHTOTTARI_RULERS.index(opening_lord)
    virtual_start_jd = float(birth_jd) - elapsed_days
    cursor_jd = virtual_start_jd
    mahadashas: list[DashaPeriod] = []

    for i in range(8):
        lord = ASHTOTTARI_RULERS[(start_idx + i) % 8]
        yrs = ASHTOTTARI_YEARS[lord]
        span_days = yrs * year_days
        s_jd = cursor_jd
        e_jd = cursor_jd + span_days
        cursor_jd = e_jd

        children: tuple[DashaPeriod, ...] = ()
        if max_level > 1:
            children = _subdivide_proportional(
                system="Ashtottari",
                parent_chain=(lord,),
                parent_start_jd=s_jd,
                parent_end_jd=e_jd,
                start_lord=lord,
                cycle_order=ASHTOTTARI_RULERS,
                cycle_weights=ASHTOTTARI_YEARS,
                total_weight=ASHTOTTARI_TOTAL_YEARS,
                year_days=year_days,
                current_level=2,
                max_level=max_level,
                clip_start_jd=float(birth_jd) if i == 0 else None,
            )

        eff_s_jd = float(birth_jd) if i == 0 else s_jd
        eff_days = e_jd - eff_s_jd
        mahadashas.append(
            DashaPeriod(
                system="Ashtottari",
                level=1,
                level_name="Mahadasha",
                lord=lord,
                lords_chain=(lord,),
                start_jd=eff_s_jd,
                end_jd=e_jd,
                start_iso_utc=jd_to_iso_utc(eff_s_jd),
                end_iso_utc=jd_to_iso_utc(e_jd),
                duration_days=eff_days,
                duration_years=eff_days / year_days,
                associated_planet=lord,
                sub_periods=children,
            )
        )

    return DashaTimeline(
        system="Ashtottari",
        birth_jd=float(birth_jd),
        birth_iso_utc=jd_to_iso_utc(birth_jd),
        year_days=year_days,
        opening_lord=opening_lord,
        birth_balance_years=balance_years,
        birth_balance_days=balance_days,
        mahadashas=tuple(mahadashas),
    )


def compute_yogini_dasha(
    moon_sidereal_lon_deg: float,
    birth_jd: float,
    *,
    year_days: float = SOLAR_YEAR_DAYS,
    max_level: int = 2,
    cycles: int = 3,
) -> DashaTimeline:
    """Compute the 36-year Yogini Dasha tree across the 8 Yoginis (Mangala through Sankata)."""
    if not 1 <= max_level <= 5:
        raise ValueError("max_level must be between 1 and 5")

    nak = nakshatra_position(moon_sidereal_lon_deg)
    # Classical BPHS formula: (Nakshatra number + 3) mod 8 (1=Mangala .. 8/0=Sankata)
    yogini_idx = (nak.number + 3 - 1) % 8
    opening_yogini = YOGINI_NAMES[yogini_idx]

    full_first_years = YOGINI_YEARS[opening_yogini]
    balance_years = full_first_years * nak.fraction_remaining
    balance_days = balance_years * year_days
    elapsed_days = full_first_years * nak.fraction_elapsed * year_days

    virtual_start_jd = float(birth_jd) - elapsed_days
    cursor_jd = virtual_start_jd
    total_periods = 8 * max(1, int(cycles))
    mahadashas: list[DashaPeriod] = []

    for i in range(total_periods):
        yogini = YOGINI_NAMES[(yogini_idx + i) % 8]
        yrs = YOGINI_YEARS[yogini]
        span_days = yrs * year_days
        s_jd = cursor_jd
        e_jd = cursor_jd + span_days
        cursor_jd = e_jd

        children: tuple[DashaPeriod, ...] = ()
        if max_level > 1:
            children = _subdivide_proportional(
                system="Yogini",
                parent_chain=(yogini,),
                parent_start_jd=s_jd,
                parent_end_jd=e_jd,
                start_lord=yogini,
                cycle_order=YOGINI_NAMES,
                cycle_weights=YOGINI_YEARS,
                total_weight=YOGINI_TOTAL_YEARS,
                year_days=year_days,
                current_level=2,
                max_level=max_level,
                associated_planets=YOGINI_LORDS,
                clip_start_jd=float(birth_jd) if i == 0 else None,
            )

        eff_s_jd = float(birth_jd) if i == 0 else s_jd
        eff_days = e_jd - eff_s_jd
        mahadashas.append(
            DashaPeriod(
                system="Yogini",
                level=1,
                level_name="Mahadasha",
                lord=yogini,
                lords_chain=(yogini,),
                start_jd=eff_s_jd,
                end_jd=e_jd,
                start_iso_utc=jd_to_iso_utc(eff_s_jd),
                end_iso_utc=jd_to_iso_utc(e_jd),
                duration_days=eff_days,
                duration_years=eff_days / year_days,
                associated_planet=YOGINI_LORDS[yogini],
                sub_periods=children,
            )
        )

    return DashaTimeline(
        system="Yogini",
        birth_jd=float(birth_jd),
        birth_iso_utc=jd_to_iso_utc(birth_jd),
        year_days=year_days,
        opening_lord=opening_yogini,
        birth_balance_years=balance_years,
        birth_balance_days=balance_days,
        mahadashas=tuple(mahadashas),
    )


def _chara_sub_signs(sign_idx: int) -> tuple[str, ...]:
    """Return the 12 sub-period sign names for a Jaimini Chara Dasha sign."""
    is_savya = sign_idx in SAVYA_SIGNS
    step = 1 if is_savya else -1
    # In classical Jaimini / K.N. Rao Chara Antardasha, sub-periods start from the sign
    # next to (or preceding) the Mahadasha sign and end with the Mahadasha sign itself.
    return tuple(RASI_NAMES[(sign_idx + step * (k + 1)) % 12] for k in range(12))


def _subdivide_chara(
    *,
    parent_chain: tuple[str, ...],
    parent_sign_idx: int,
    parent_start_jd: float,
    parent_end_jd: float,
    year_days: float,
    current_level: int,
    max_level: int,
) -> tuple[DashaPeriod, ...]:
    span_days = parent_end_jd - parent_start_jd
    sub_days = span_days / 12.0
    sub_names = _chara_sub_signs(parent_sign_idx)
    out: list[DashaPeriod] = []

    for i, s_name in enumerate(sub_names):
        s_idx = RASI_NAMES.index(s_name)
        s_jd = parent_start_jd + i * sub_days
        e_jd = parent_end_jd if i == 11 else (parent_start_jd + (i + 1) * sub_days)
        chain = parent_chain + (s_name,)
        children: tuple[DashaPeriod, ...] = ()
        if current_level < max_level:
            children = _subdivide_chara(
                parent_chain=chain,
                parent_sign_idx=s_idx,
                parent_start_jd=s_jd,
                parent_end_jd=e_jd,
                year_days=year_days,
                current_level=current_level + 1,
                max_level=max_level,
            )
        dur_days = e_jd - s_jd
        out.append(
            DashaPeriod(
                system="Chara",
                level=current_level,
                level_name=LEVEL_NAMES[current_level - 1],
                lord=s_name,
                lords_chain=chain,
                start_jd=s_jd,
                end_jd=e_jd,
                start_iso_utc=jd_to_iso_utc(s_jd),
                end_iso_utc=jd_to_iso_utc(e_jd),
                duration_days=dur_days,
                duration_years=dur_days / year_days,
                associated_planet=None,
                sub_periods=children,
            )
        )
    return tuple(out)


def compute_chara_dasha(
    lagna_lon_deg: float,
    planet_longitudes: Mapping[str, float],
    birth_jd: float,
    *,
    year_days: float = SOLAR_YEAR_DAYS,
    max_level: int = 2,
    apply_dignity_adjustment: bool = False,
) -> DashaTimeline:
    """Compute Jaimini Chara Dasha across all 12 signs with Savya/Apasavya progression.

    - Progression direction from Lagna is governed by the 9th house from Lagna:
      direct (`+1`) if the 9th sign is in `SAVYA_SIGNS` (`{0, 1, 2, 6, 7, 8}`),
      reverse (`-1`) if the 9th sign is in `APASAVYA_SIGNS` (`{3, 4, 5, 9, 10, 11}`).
    - Each sign's duration in years is counted from the sign to its lord (zodiacally
      for Savya signs, anti-zodiacally for Apasavya signs), with own-sign placement
      giving 12 years.
    """
    if not 1 <= max_level <= 5:
        raise ValueError("max_level must be between 1 and 5")

    lagna_sign = min(int(normalize_degrees(lagna_lon_deg) // 30.0), 11)
    norm_lons = {k.strip().capitalize(): normalize_degrees(v) for k, v in planet_longitudes.items()}

    ninth_sign = (lagna_sign + 8) % 12
    step = 1 if ninth_sign in SAVYA_SIGNS else -1

    cursor_jd = float(birth_jd)
    mahadashas: list[DashaPeriod] = []
    first_years = 0.0

    for i in range(12):
        sign_idx = (lagna_sign + step * i) % 12
        sign_name = RASI_NAMES[sign_idx]
        lord = resolve_jaimini_sign_lord(sign_idx, norm_lons)
        if lord not in norm_lons:
            raise ValueError(f"Missing longitude for sign lord {lord!r} in planet_longitudes")
        lord_sign = min(int(norm_lons[lord] // 30.0), 11)

        if lord_sign == sign_idx:
            yrs = 12.0
        elif sign_idx in SAVYA_SIGNS:
            yrs = float((lord_sign - sign_idx) % 12)
        else:
            yrs = float((sign_idx - lord_sign) % 12)

        if apply_dignity_adjustment:
            if EXALTATION_SIGNS.get(lord) == lord_sign:
                yrs = min(12.0, yrs + 1.0)
            elif DEBILITATION_SIGNS.get(lord) == lord_sign:
                yrs = max(1.0, yrs - 1.0)

        if i == 0:
            first_years = yrs

        span_days = yrs * year_days
        s_jd = cursor_jd
        e_jd = cursor_jd + span_days
        cursor_jd = e_jd

        children: tuple[DashaPeriod, ...] = ()
        if max_level > 1:
            children = _subdivide_chara(
                parent_chain=(sign_name,),
                parent_sign_idx=sign_idx,
                parent_start_jd=s_jd,
                parent_end_jd=e_jd,
                year_days=year_days,
                current_level=2,
                max_level=max_level,
            )

        mahadashas.append(
            DashaPeriod(
                system="Chara",
                level=1,
                level_name="Mahadasha",
                lord=sign_name,
                lords_chain=(sign_name,),
                start_jd=s_jd,
                end_jd=e_jd,
                start_iso_utc=jd_to_iso_utc(s_jd),
                end_iso_utc=jd_to_iso_utc(e_jd),
                duration_days=span_days,
                duration_years=yrs,
                associated_planet=lord,
                sub_periods=children,
            )
        )

    return DashaTimeline(
        system="Chara",
        birth_jd=float(birth_jd),
        birth_iso_utc=jd_to_iso_utc(birth_jd),
        year_days=year_days,
        opening_lord=RASI_NAMES[lagna_sign],
        birth_balance_years=first_years,
        birth_balance_days=first_years * year_days,
        mahadashas=tuple(mahadashas),
    )


def resolve_dasha_5_levels(
    timeline_or_moon_lon: DashaTimeline | float,
    query_jd: float,
    *,
    birth_jd: float | None = None,
    system: str = "vimshottari",
    year_days: float = SOLAR_YEAR_DAYS,
) -> tuple[DashaPeriod, DashaPeriod, DashaPeriod, DashaPeriod, DashaPeriod]:
    """Resolve the exact 5 active Dasha levels (`Mahadasha`, `Antardasha`, `Pratyantardasha`,
    `Sookshma`, `Prana`) at `query_jd` with O(1) branch expansion.
    """
    sys_key = system.strip().lower()
    if isinstance(timeline_or_moon_lon, DashaTimeline):
        timeline = timeline_or_moon_lon
        sys_key = timeline.system.lower()
        year_days = timeline.year_days
    else:
        if birth_jd is None:
            raise ValueError("birth_jd is required when passing moon_sidereal_lon_deg directly")
        if sys_key == "vimshottari":
            timeline = compute_vimshottari_dasha(timeline_or_moon_lon, birth_jd, year_days=year_days, max_level=1, cycles=2)
        elif sys_key == "ashtottari":
            timeline = compute_ashtottari_dasha(timeline_or_moon_lon, birth_jd, year_days=year_days, max_level=1)
        elif sys_key == "yogini":
            timeline = compute_yogini_dasha(timeline_or_moon_lon, birth_jd, year_days=year_days, max_level=1, cycles=4)
        else:
            raise ValueError(f"Unsupported direct system {system!r}")

    q_jd = float(query_jd)
    maha: DashaPeriod | None = None
    for idx, candidate in enumerate(timeline.mahadashas):
        if candidate.start_jd <= q_jd < candidate.end_jd or (idx == len(timeline.mahadashas) - 1 and q_jd == candidate.end_jd):
            maha = candidate
            break
    if maha is None:
        raise ValueError(f"query_jd={q_jd} lies outside the computed Mahadasha timeline [{timeline.mahadashas[0].start_jd}, {timeline.mahadashas[-1].end_jd}]")

    if sys_key == "vimshottari":
        order: Sequence[str] = VIMSHOTTARI_RULERS
        weights: Mapping[str, float] = VIMSHOTTARI_YEARS
        total_w = VIMSHOTTARI_TOTAL_YEARS
        assoc: Mapping[str, str] | None = None
    elif sys_key == "ashtottari":
        order = ASHTOTTARI_RULERS
        weights = ASHTOTTARI_YEARS
        total_w = ASHTOTTARI_TOTAL_YEARS
        assoc = None
    elif sys_key == "yogini":
        order = YOGINI_NAMES
        weights = YOGINI_YEARS
        total_w = YOGINI_TOTAL_YEARS
        assoc = YOGINI_LORDS
    elif sys_key == "chara":
        # Chara Dasha subdivides each level into 12 equal sign parts
        levels: list[DashaPeriod] = [maha]
        cur = maha
        for lvl in range(2, 6):
            s_idx = RASI_NAMES.index(cur.lord)
            subs = _subdivide_chara(
                parent_chain=cur.lords_chain,
                parent_sign_idx=s_idx,
                parent_start_jd=cur.start_jd,
                parent_end_jd=cur.end_jd,
                year_days=year_days,
                current_level=lvl,
                max_level=lvl,
            )
            picked = subs[-1]
            for sub in subs:
                if sub.start_jd <= q_jd < sub.end_jd:
                    picked = sub
                    break
            levels.append(picked)
            cur = picked
        return (levels[0], levels[1], levels[2], levels[3], levels[4])
    else:
        raise ValueError(f"Unknown Dasha system {timeline.system!r}")

    # Reconstruct full unclipped start of opening Mahadasha if maha is the first Mahadasha
    full_maha_days = weights[maha.lord] * year_days
    unclipped_start_jd = maha.end_jd - full_maha_days

    levels = [maha]
    cur_start = unclipped_start_jd
    cur_end = maha.end_jd
    cur_lord = maha.lord
    cur_chain = maha.lords_chain

    for lvl in range(2, 6):
        subs = _subdivide_proportional(
            system=timeline.system,
            parent_chain=cur_chain,
            parent_start_jd=cur_start,
            parent_end_jd=cur_end,
            start_lord=cur_lord,
            cycle_order=order,
            cycle_weights=weights,
            total_weight=total_w,
            year_days=year_days,
            current_level=lvl,
            max_level=lvl,
            associated_planets=assoc,
        )
        picked = subs[-1]
        for sub in subs:
            if sub.start_jd <= q_jd < sub.end_jd:
                picked = sub
                break
        levels.append(picked)
        cur_start = picked.start_jd
        cur_end = picked.end_jd
        cur_lord = picked.lord
        cur_chain = picked.lords_chain

    return (levels[0], levels[1], levels[2], levels[3], levels[4])


def compute_chara_karakas(
    planet_longitudes: Mapping[str, float],
    *,
    scheme: str = "7",
) -> tuple[CharaKarakaEntry, ...]:
    """Compute Jaimini Chara Karakas in either the 7-karaka (`scheme="7"`) or 8-karaka (`scheme="8"`) system.

    In the 7-karaka system, Sun, Moon, Mars, Mercury, Jupiter, Venus, and Saturn are ranked
    by their degree within their sign (`lon % 30`).
    In the 8-karaka system, Rahu is included with its effective degree measured from the end
    of the sign (`30 - (lon % 30)`).
    """
    scheme_str = str(scheme).strip()
    if scheme_str not in ("7", "8"):
        raise ValueError("scheme must be '7' or '8'")

    norm_lons = {k.strip().capitalize(): normalize_degrees(v) for k, v in planet_longitudes.items()}
    required = ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn"]
    if scheme_str == "8":
        required.append("Rahu")

    candidates: list[tuple[float, str, float, int, float]] = []
    for p in required:
        if p not in norm_lons:
            raise ValueError(f"Missing longitude for {p!r} in planet_longitudes")
        lon = norm_lons[p]
        sign_idx = min(int(lon // 30.0), 11)
        deg_in_sign = lon - sign_idx * 30.0
        eff_deg = (30.0 - deg_in_sign) if p == "Rahu" else deg_in_sign
        candidates.append((eff_deg, p, lon, sign_idx, deg_in_sign))

    # Sort descending by effective degree in sign
    candidates.sort(key=lambda item: item[0], reverse=True)
    roles = KARAKA_7_ROLES if scheme_str == "7" else KARAKA_8_ROLES

    out: list[CharaKarakaEntry] = []
    for (code, role_name), (eff_deg, p, lon, sign_idx, deg_in_sign) in zip(roles, candidates):
        out.append(
            CharaKarakaEntry(
                code=code,
                role_name=role_name,
                planet=p,
                sidereal_lon_deg=lon,
                sign_index=sign_idx,
                sign_name=RASI_NAMES[sign_idx],
                degree_in_sign=deg_in_sign,
                effective_karaka_degree=eff_deg,
            )
        )
    return tuple(out)


# ============================================================================
# BPHS Kalachakra Dasha ("The Wheel of Time", Brihat Parashara Hora Shastra Ch. 46)
# ============================================================================

KALACHAKRA_SIGN_YEARS: Final[Mapping[int, float]] = {
    0: 7.0,   # Mesha (Mars)
    1: 16.0,  # Vrishabha (Venus)
    2: 9.0,   # Mithuna (Mercury)
    3: 21.0,  # Karka (Moon)
    4: 5.0,   # Simha (Sun)
    5: 9.0,   # Kanya (Mercury)
    6: 16.0,  # Tula (Venus)
    7: 7.0,   # Vrishchika (Mars)
    8: 10.0,  # Dhanu (Jupiter)
    9: 4.0,   # Makara (Saturn)
    10: 4.0,  # Kumbha (Saturn)
    11: 10.0, # Meena (Jupiter)
}

# Savya (clockwise) Nakshatra indices (0..26):
# Triads 0 (Ashwini..Krittika), 2 (Punarvasu..Ashlesha), 4 (Hasta..Swati),
# 6 (Mula..Uttara Ashadha), 8 (Purva Bhadrapada..Revati)
KALACHAKRA_SAVYA_NAKSHATRAS: Final[frozenset[int]] = frozenset(
    {0, 1, 2, 6, 7, 8, 12, 13, 14, 18, 19, 20, 24, 25, 26}
)

# Canonical 12 Savya Pada 9-sign sequences (indexed by (pos_in_triad 0..2, pada 1..4))
# per Brihat Parashara Hora Shastra Chapter 46:
# Paramayus totals: 100, 85, 83, 86 years.
KALACHAKRA_SAVYA_SEQUENCES: Final[Mapping[tuple[int, int], tuple[int, ...]]] = {
    # Savya Star 1 in triad (Ashwini, Punarvasu, Hasta, Mula, Purva Bhadrapada)
    (0, 1): (0, 1, 2, 3, 4, 5, 6, 7, 8),       # Mesha Amsa (100y): Aries..Sagittarius
    (0, 2): (9, 10, 11, 7, 6, 5, 3, 4, 2),     # Vrishabha Amsa (85y): Capricorn..Gemini
    (0, 3): (1, 0, 11, 10, 9, 8, 0, 1, 2),     # Mithuna Amsa (83y): Taurus..Gemini
    (0, 4): (3, 4, 5, 6, 7, 8, 9, 10, 11),     # Karka Amsa (86y): Cancer..Pisces
    # Savya Star 2 in triad (Bharani, Pushya, Chitra, Purva Ashadha, Uttara Bhadrapada)
    (1, 1): (7, 6, 5, 3, 4, 2, 1, 0, 11),      # Simha Amsa (100y): Scorpio..Pisces
    (1, 2): (10, 9, 8, 0, 1, 2, 3, 4, 5),      # Kanya Amsa (85y): Aquarius..Virgo
    (1, 3): (6, 7, 8, 9, 10, 11, 7, 6, 5),     # Tula Amsa (83y): Libra..Virgo
    (1, 4): (3, 4, 2, 1, 0, 11, 10, 9, 8),     # Vrishchika Amsa (86y): Cancer..Sagittarius
    # Savya Star 3 in triad (Krittika, Ashlesha, Swati, Uttara Ashadha, Revati)
    (2, 1): (8, 9, 10, 11, 0, 1, 2, 4, 3),     # Dhanu Amsa (86y): Sagittarius..Cancer
    (2, 2): (5, 6, 7, 8, 9, 10, 11, 7, 6),     # Makara Amsa (83y): Virgo..Libra
    (2, 3): (5, 4, 3, 2, 1, 0, 8, 9, 10),      # Kumbha Amsa (85y): Virgo..Aquarius
    (2, 4): (11, 0, 1, 2, 4, 3, 5, 6, 7),      # Meena Amsa (100y): Pisces..Scorpio
}

# Canonical 12 Apasavya Pada 9-sign sequences (mirror reversal of Savya triads)
# In Apasavya triads (Rohini..Ardra, Magha..U.Phalguni, Vishakha..Jyeshtha, Shravana..Shatabhisha):
# Star 1 (Rohini/Magha/Vishakha/Shravana) reverses Savya Star 3 (Padas 4, 3, 2, 1)
# Star 2 (Mrigashirsha/P.Phalguni/Anuradha/Dhanishta) reverses Savya Star 2 (Padas 4, 3, 2, 1)
# Star 3 (Ardra/U.Phalguni/Jyeshtha/Shatabhisha) reverses Savya Star 1 (Padas 4, 3, 2, 1)
KALACHAKRA_APASAVYA_SEQUENCES: Final[Mapping[tuple[int, int], tuple[int, ...]]] = {
    (0, 1): tuple(reversed(KALACHAKRA_SAVYA_SEQUENCES[(2, 4)])),  # Dhanu Amsa (100y)
    (0, 2): tuple(reversed(KALACHAKRA_SAVYA_SEQUENCES[(2, 3)])),  # Makara Amsa (85y)
    (0, 3): tuple(reversed(KALACHAKRA_SAVYA_SEQUENCES[(2, 2)])),  # Kumbha Amsa (83y)
    (0, 4): tuple(reversed(KALACHAKRA_SAVYA_SEQUENCES[(2, 1)])),  # Meena Amsa (86y)
    (1, 1): tuple(reversed(KALACHAKRA_SAVYA_SEQUENCES[(1, 4)])),  # Vrishchika Amsa (86y)
    (1, 2): tuple(reversed(KALACHAKRA_SAVYA_SEQUENCES[(1, 3)])),  # Tula Amsa (83y)
    (1, 3): tuple(reversed(KALACHAKRA_SAVYA_SEQUENCES[(1, 2)])),  # Kanya Amsa (85y)
    (1, 4): tuple(reversed(KALACHAKRA_SAVYA_SEQUENCES[(1, 1)])),  # Simha Amsa (100y)
    (2, 1): tuple(reversed(KALACHAKRA_SAVYA_SEQUENCES[(0, 4)])),  # Karka Amsa (86y)
    (2, 2): tuple(reversed(KALACHAKRA_SAVYA_SEQUENCES[(0, 3)])),  # Mithuna Amsa (83y)
    (2, 3): tuple(reversed(KALACHAKRA_SAVYA_SEQUENCES[(0, 2)])),  # Vrishabha Amsa (85y)
    (2, 4): tuple(reversed(KALACHAKRA_SAVYA_SEQUENCES[(0, 1)])),  # Mesha Amsa (100y)
}


@dataclass(frozen=True)
class KalachakraDashaPeriod:
    """A single BPHS Kalachakra Dasha or Antardasha sign period with Gati and Deha/Jeeva flags."""

    level: int
    level_name: str
    sign_index: int
    sign_name: str
    sign_lord: str
    start_jd: float
    end_jd: float
    start_iso_utc: str
    end_iso_utc: str
    duration_days: float
    duration_years: float
    gati: str
    gati_description: str
    is_deha_sign: bool
    is_jeeva_sign: bool
    sub_periods: tuple["KalachakraDashaPeriod", ...] = ()


@dataclass(frozen=True)
class KalachakraDashaTimeline:
    """Complete BPHS Kalachakra Dasha calculation with Savya/Apasavya chakra, Deha/Jeeva, and Gati jumps."""

    system: str
    birth_jd: float
    birth_iso_utc: str
    year_days: float
    moon_sidereal_lon_deg: float
    nakshatra_index: int
    nakshatra_name: str
    pada: int
    chakra_group: str
    paramayus_years: float
    deha_sign_index: int
    deha_sign_name: str
    jeeva_sign_index: int
    jeeva_sign_name: str
    nine_sign_sequence: tuple[int, ...]
    nine_sign_names: tuple[str, ...]
    opening_sign_index: int
    opening_sign_name: str
    birth_balance_years: float
    birth_balance_days: float
    gati_jumps_detected: tuple[str, ...]
    mahadashas: tuple[KalachakraDashaPeriod, ...]


def classify_kalachakra_gati(prev_sign_idx: int | None, curr_sign_idx: int) -> tuple[str, str]:
    """Classify the classical BPHS Kalachakra Gati (planetary motion jump) between consecutive signs.

    Classical Gatis (*Brihat Parashara Hora Shastra* Ch. 46):
    - ``Simhavalokana Gati`` (Lion's Gaze): Trinal jump of 4 or 8 signs (e.g., Meena -> Vrishchika or Dhanu -> Mesha).
    - ``Mandooka Gati`` (Frog Jump): Skipping one intermediate sign (`Virgo -> Cancer` or `Leo -> Gemini`, delta 2 or 10).
    - ``Markata Gati`` (Monkey Jump): Stepping backward by 1 sign after a frog jump (`Cancer -> Leo` or `Leo -> Cancer`).
    - ``Krama Gati`` (Regular Step): Normal sequential progression to an adjacent sign.
    """
    if prev_sign_idx is None:
        return ("Prarambha", "Opening birth Dasha sign of the Kalachakra sequence")
    p = int(prev_sign_idx) % 12
    c = int(curr_sign_idx) % 12
    forward_diff = (c - p) % 12
    if forward_diff in (4, 8):
        return (
            "Simhavalokana Gati",
            f"Lion's gaze trinal jump from {RASI_NAMES[p]} to {RASI_NAMES[c]} (major life direction shift)",
        )
    if forward_diff in (2, 10):
        return (
            "Mandooka Gati",
            f"Frog jump skipping one sign from {RASI_NAMES[p]} to {RASI_NAMES[c]} (sudden leap or transition)",
        )
    if (p == 3 and c == 4) or (p == 4 and c == 3):
        return (
            "Markata Gati",
            f"Monkey reversal step between {RASI_NAMES[p]} and {RASI_NAMES[c]} (restless reversal of fortune)",
        )
    return ("Krama Gati", f"Sequential zodiacal step from {RASI_NAMES[p]} to {RASI_NAMES[c]}")


def compute_kalachakra_dasha(
    moon_sidereal_lon_deg: float,
    birth_jd: float,
    *,
    year_days: float = SOLAR_YEAR_DAYS,
    include_antardashas: bool = True,
) -> KalachakraDashaTimeline:
    """Compute the classical BPHS Kalachakra Dasha ('Wheel of Time') from Moon's sidereal longitude.

    Implements the full 27-Nakshatra x 4-Pada Savya and Apasavya 9-sign progressions,
    exact Paramayus (83, 85, 86, or 100 years), Deha (Body) and Jeeva (Soul) Rashi
    identification, proportional birth-pada balance across the 9 signs, Antardasha
    sub-periods, and Mandooka / Markata / Simhavalokana Gati jump classification.
    """
    from .vargas import RASI_LORDS

    if not math.isfinite(float(moon_sidereal_lon_deg)) or not math.isfinite(float(birth_jd)):
        raise ValueError("moon_sidereal_lon_deg and birth_jd must be finite numbers")

    nak = nakshatra_position(moon_sidereal_lon_deg)
    nak_idx = int(nak.index)
    pada = int(nak.pada)
    pos_in_triad = nak_idx % 3
    is_savya = nak_idx in KALACHAKRA_SAVYA_NAKSHATRAS
    chakra_group = "Savya" if is_savya else "Apasavya"

    seq = (
        KALACHAKRA_SAVYA_SEQUENCES[(pos_in_triad, pada)]
        if is_savya
        else KALACHAKRA_APASAVYA_SEQUENCES[(pos_in_triad, pada)]
    )
    paramayus = float(sum(KALACHAKRA_SIGN_YEARS[s] for s in seq))

    # In Savya, first sign is Deha and last (9th) sign is Jeeva.
    # In Apasavya, first sign is Jeeva and last (9th) sign is Deha (BPHS Ch. 46).
    if is_savya:
        deha_sign = seq[0]
        jeeva_sign = seq[-1]
    else:
        jeeva_sign = seq[0]
        deha_sign = seq[-1]

    # Fraction elapsed within the active Pada (each Pada spans 3 deg 20 min = 10/3 deg)
    pada_span = NAKSHATRA_SPAN_DEG / 4.0
    offset_in_pada = max(0.0, min(pada_span, float(nak.degree_in_pada)))
    fraction_elapsed_in_pada = offset_in_pada / pada_span
    years_elapsed_in_cycle = fraction_elapsed_in_pada * paramayus
    years_remaining_in_cycle = max(0.0, paramayus - years_elapsed_in_cycle)

    # Locate which of the 9 signs in `seq` is active at birth_jd, and build 2 full cycles
    # (18 sign periods) so the timeline comfortably covers >100 years from birth.
    unclipped_start_jd = float(birth_jd) - (years_elapsed_in_cycle * float(year_days))
    cursor_jd = unclipped_start_jd

    extended_seq = seq + seq
    mahadashas: list[KalachakraDashaPeriod] = []
    gati_jumps: list[str] = []
    opening_sign_idx: int | None = None
    birth_balance_years: float = 0.0

    for idx_in_ext, s_idx in enumerate(extended_seq):
        full_sign_years = float(KALACHAKRA_SIGN_YEARS[s_idx])
        full_sign_days = full_sign_years * float(year_days)
        s_start_jd = cursor_jd
        s_end_jd = cursor_jd + full_sign_days
        cursor_jd = s_end_jd

        prev_s = extended_seq[idx_in_ext - 1] if idx_in_ext > 0 else None
        gati_name, gati_desc = classify_kalachakra_gati(prev_s, s_idx)
        if idx_in_ext < len(seq) and gati_name not in ("Prarambha", "Krama Gati"):
            gati_jumps.append(f"{RASI_NAMES[prev_s]}->{RASI_NAMES[s_idx]} ({gati_name})")

        if s_end_jd <= float(birth_jd) + 1e-9:
            continue

        eff_start_jd = max(float(birth_jd), s_start_jd)
        eff_days = s_end_jd - eff_start_jd
        eff_years = eff_days / float(year_days)

        if opening_sign_idx is None:
            opening_sign_idx = s_idx
            birth_balance_years = eff_years

        # Build proportional Antardashas across the 9 signs starting from the active sign position in `seq`
        sub_periods: list[KalachakraDashaPeriod] = []
        if include_antardashas:
            seq_pos = idx_in_ext % len(seq)
            ordered_sub_seq = seq[seq_pos:] + seq[:seq_pos]
            sub_cursor = s_start_jd
            for sub_i, sub_s_idx in enumerate(ordered_sub_seq):
                sub_w = float(KALACHAKRA_SIGN_YEARS[sub_s_idx])
                sub_full_days = (
                    full_sign_days * (sub_w / paramayus)
                    if sub_i < len(ordered_sub_seq) - 1
                    else (s_end_jd - sub_cursor)
                )
                sub_s = sub_cursor
                sub_e = sub_cursor + sub_full_days
                sub_cursor = sub_e
                if sub_e <= float(birth_jd) + 1e-9:
                    continue
                eff_sub_s = max(float(birth_jd), sub_s)
                eff_sub_days = sub_e - eff_sub_s
                prev_sub_s = ordered_sub_seq[sub_i - 1] if sub_i > 0 else None
                sub_gati, sub_gati_desc = classify_kalachakra_gati(prev_sub_s, sub_s_idx)
                sub_periods.append(
                    KalachakraDashaPeriod(
                        level=2,
                        level_name="Antardasha",
                        sign_index=sub_s_idx,
                        sign_name=RASI_NAMES[sub_s_idx],
                        sign_lord=RASI_LORDS[sub_s_idx],
                        start_jd=eff_sub_s,
                        end_jd=sub_e,
                        start_iso_utc=jd_to_iso_utc(eff_sub_s),
                        end_iso_utc=jd_to_iso_utc(sub_e),
                        duration_days=eff_sub_days,
                        duration_years=eff_sub_days / float(year_days),
                        gati=sub_gati,
                        gati_description=sub_gati_desc,
                        is_deha_sign=(sub_s_idx == deha_sign),
                        is_jeeva_sign=(sub_s_idx == jeeva_sign),
                    )
                )

        mahadashas.append(
            KalachakraDashaPeriod(
                level=1,
                level_name="Mahadasha",
                sign_index=s_idx,
                sign_name=RASI_NAMES[s_idx],
                sign_lord=RASI_LORDS[s_idx],
                start_jd=eff_start_jd,
                end_jd=s_end_jd,
                start_iso_utc=jd_to_iso_utc(eff_start_jd),
                end_iso_utc=jd_to_iso_utc(s_end_jd),
                duration_days=eff_days,
                duration_years=eff_years,
                gati=gati_name,
                gati_description=gati_desc,
                is_deha_sign=(s_idx == deha_sign),
                is_jeeva_sign=(s_idx == jeeva_sign),
                sub_periods=tuple(sub_periods),
            )
        )
        if len(mahadashas) >= 9:
            break

    if opening_sign_idx is None:
        opening_sign_idx = seq[0]

    return KalachakraDashaTimeline(
        system="Kalachakra",
        birth_jd=float(birth_jd),
        birth_iso_utc=jd_to_iso_utc(birth_jd),
        year_days=float(year_days),
        moon_sidereal_lon_deg=normalize_degrees(moon_sidereal_lon_deg),
        nakshatra_index=nak_idx,
        nakshatra_name=nak.name,
        pada=pada,
        chakra_group=chakra_group,
        paramayus_years=paramayus,
        deha_sign_index=deha_sign,
        deha_sign_name=RASI_NAMES[deha_sign],
        jeeva_sign_index=jeeva_sign,
        jeeva_sign_name=RASI_NAMES[jeeva_sign],
        nine_sign_sequence=seq,
        nine_sign_names=tuple(RASI_NAMES[s] for s in seq),
        opening_sign_index=opening_sign_idx,
        opening_sign_name=RASI_NAMES[opening_sign_idx],
        birth_balance_years=birth_balance_years,
        birth_balance_days=birth_balance_years * float(year_days),
        gati_jumps_detected=tuple(gati_jumps),
        mahadashas=tuple(mahadashas),
    )

