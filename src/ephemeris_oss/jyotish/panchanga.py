"""Clean-room Five-Limb Vedic Almanac (Panchanga), Samvatsara, Ritu, Hora, and Muhurta engine.

Mathematical formulations follow *Surya Siddhanta*, *Brihat Parashara Hora Shastra*,
and *Muhurta Chintamani*:
- Tithi (1..30 lunar days of 12 deg synodic elongation each, Shukla/Krishna Paksha,
  Tithi lord, Nanda/Bhadra/Jaya/Rikta/Purna classification).
- Vara (7 Vedic weekdays anchored to local sunrise and their planetary lords).
- Nakshatra (27 lunar mansions and 108 padas of the Moon).
- Yoga (1..27 luni-solar sums of 13 deg 20 min each, Vishkumbha to Vaidhriti,
  benefic/malefic nature).
- Karana (1..60 half-tithis of 6 deg each, mapped to the 7 Chara and 4 Sthira karanas).
- Samvatsara (60-year Jovian cycle from Prabhava to Akshaya), Ritu (6 seasons),
  Ayana (Uttarayana / Dakshinayana).
- Daily 24-Hora table and classical Muhurta windows (Abhijit Muhurta, Brahma Muhurta,
  Rahu Kalam, Yamagandam, Gulika Kalam, Durmuhurta).
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Final

from .nakshatra import NAKSHATRA_SPAN_DEG, NakshatraPosition, nakshatra_position, normalize_degrees

TITHI_SPAN_DEG: Final[float] = 12.0
KARANA_SPAN_DEG: Final[float] = 6.0
YOGA_SPAN_DEG: Final[float] = NAKSHATRA_SPAN_DEG  # 13 deg 20 min

PAKSHA_TITHI_NAMES: Final[tuple[str, ...]] = (
    "Pratipada",
    "Dwitiya",
    "Tritiya",
    "Chaturthi",
    "Panchami",
    "Shashthi",
    "Saptami",
    "Ashtami",
    "Navami",
    "Dashami",
    "Ekadashi",
    "Dwadashi",
    "Trayodashi",
    "Chaturdashi",
)

TITHI_GROUPS: Final[tuple[str, ...]] = (
    "Nanda",   # 1, 6, 11
    "Bhadra",  # 2, 7, 12
    "Jaya",    # 3, 8, 13
    "Rikta",   # 4, 9, 14
    "Purna",   # 5, 10, 15
)

TITHI_EIGHT_LORDS: Final[tuple[str, ...]] = (
    "Sun",
    "Moon",
    "Mars",
    "Mercury",
    "Jupiter",
    "Venus",
    "Saturn",
    "Rahu",
)

VARA_CATALOG: Final[tuple[tuple[int, str, str, str], ...]] = (
    (0, "Ravivara", "Sunday", "Sun"),
    (1, "Somavara", "Monday", "Moon"),
    (2, "Mangalavara", "Tuesday", "Mars"),
    (3, "Budhavara", "Wednesday", "Mercury"),
    (4, "Guruvara", "Thursday", "Jupiter"),
    (5, "Shukravara", "Friday", "Venus"),
    (6, "Shanivara", "Saturday", "Saturn"),
)

# Standard Hora ruler progression (descending orbital period: Sat, Jup, Mars, Sun, Ven, Merc, Moon)
HORA_CHALDEAN_ORDER: Final[tuple[str, ...]] = (
    "Sun",
    "Venus",
    "Mercury",
    "Moon",
    "Saturn",
    "Jupiter",
    "Mars",
)

YOGA_CATALOG: Final[tuple[tuple[int, str, bool], ...]] = (
    (1, "Vishkumbha", False),
    (2, "Priti", True),
    (3, "Ayushman", True),
    (4, "Saubhagya", True),
    (5, "Shobhana", True),
    (6, "Atiganda", False),
    (7, "Sukarma", True),
    (8, "Dhriti", True),
    (9, "Shula", False),
    (10, "Ganda", False),
    (11, "Vriddhi", True),
    (12, "Dhruva", True),
    (13, "Vyaghata", False),
    (14, "Harshana", True),
    (15, "Vajra", False),
    (16, "Siddhi", True),
    (17, "Vyatipata", False),
    (18, "Variyan", True),
    (19, "Parigha", False),
    (20, "Shiva", True),
    (21, "Siddha", True),
    (22, "Sadhya", True),
    (23, "Shubha", True),
    (24, "Shukla", True),
    (25, "Brahma", True),
    (26, "Indra", True),
    (27, "Vaidhriti", False),
)

MOVABLE_KARANAS: Final[tuple[str, ...]] = (
    "Bava",
    "Balava",
    "Kaulava",
    "Taitila",
    "Gara",
    "Vanija",
    "Vishti",
)

FIXED_KARANAS: Final[tuple[str, ...]] = (
    "Kimstughna",
    "Shakuni",
    "Chatushpada",
    "Naga",
)

SAMVATSARA_NAMES: Final[tuple[str, ...]] = (
    "Prabhava", "Vibhava", "Shukla", "Pramoduta", "Prajothpatti",
    "Angirasa", "Shrimukha", "Bhava", "Yuva", "Dhatri",
    "Ishvara", "Bahudhanya", "Pramathi", "Vikrama", "Vrisha",
    "Chitrabhanu", "Svabhanu", "Tarana", "Parthiva", "Vyaya",
    "Sarvajit", "Sarvadharin", "Virodhin", "Vikrita", "Khara",
    "Nandana", "Vijaya", "Jaya", "Manmatha", "Durmukhi",
    "Hevilambi", "Vilambi", "Vikari", "Sharvari", "Plava",
    "Shubhakrit", "Shobhakrit", "Krodhin", "Vishvavasu", "Parabhava",
    "Plavanga", "Kilaka", "Saumya", "Sadharana", "Virodhikrit",
    "Paridhavi", "Pramadicha", "Ananda", "Rakshasa", "Nala",
    "Pingala", "Kalayukti", "Siddharthi", "Raudri", "Durmati",
    "Dundubhi", "Rudhirodgari", "Raktakshi", "Krodhana", "Akshaya",
)

RITU_CATALOG: Final[tuple[tuple[str, str], ...]] = (
    ("Shishira", "Late Winter"),
    ("Vasanta", "Spring"),
    ("Grishma", "Summer"),
    ("Varsha", "Monsoon"),
    ("Sharad", "Autumn"),
    ("Hemanta", "Pre-Winter"),
)

# 1-based octant (1..8) of daytime for Rahu Kalam, Yamagandam, Gulika Kalam by weekday (0=Sun..6=Sat)
RAHU_KALAM_SEGMENT: Final[tuple[int, ...]] = (8, 2, 7, 5, 6, 4, 3)
YAMAGANDAM_SEGMENT: Final[tuple[int, ...]] = (5, 4, 3, 2, 1, 7, 6)
GULIKA_KALAM_SEGMENT: Final[tuple[int, ...]] = (7, 6, 5, 4, 3, 2, 1)

# Classical daytime Durmuhurta 1-based indices (out of 15 daytime Muhurtas) per weekday (0=Sun..6=Sat)
DURMUHURTA_DAY_INDICES: Final[tuple[tuple[int, ...], ...]] = (
    (14,),      # Sunday: 14th muhurta
    (9, 12),    # Monday: 9th and 12th muhurtas
    (4,),       # Tuesday: 4th muhurta (plus 7th of night)
    (8,),       # Wednesday: 8th muhurta
    (6, 12),    # Thursday: 6th and 12th muhurtas
    (4, 9),     # Friday: 4th and 9th muhurtas
    (1, 2),     # Saturday: 1st and 2nd muhurtas
)


@dataclass(frozen=True)
class TithiInfo:
    """Computed Tithi (lunar day) state."""

    number: int
    paksha: str
    paksha_tithi: int
    name: str
    lord: str
    group: str
    elongation_deg: float
    degree_in_tithi: float
    fraction_elapsed: float
    fraction_remaining: float


@dataclass(frozen=True)
class VaraInfo:
    """Computed Vedic weekday (Vara) anchored to local sunrise."""

    index: int
    sanskrit_name: str
    english_name: str
    ruler: str


@dataclass(frozen=True)
class YogaInfo:
    """Computed Luni-Solar Yoga (1..27)."""

    index: int
    number: int
    name: str
    is_benefic: bool
    sum_longitude_deg: float
    degree_in_yoga: float
    fraction_elapsed: float
    fraction_remaining: float


@dataclass(frozen=True)
class KaranaInfo:
    """Computed Karana (half-tithi 1..60)."""

    number: int
    name: str
    kind: str
    is_vishti_bhadra: bool
    degree_in_karana: float
    fraction_elapsed: float
    fraction_remaining: float


@dataclass(frozen=True)
class SamvatsaraInfo:
    """60-year Jovian Samvatsara cycle entry."""

    number: int
    name: str


@dataclass(frozen=True)
class HoraWindow:
    """One planetary hour (Hora) window."""

    hora_number: int
    is_daytime: bool
    ruler: str
    start_jd: float
    end_jd: float


@dataclass(frozen=True)
class TimeWindow:
    """A start-to-end Julian Day window for a Muhurta or Kalam."""

    name: str
    start_jd: float
    end_jd: float
    duration_minutes: float
    is_auspicious: bool


@dataclass(frozen=True)
class MuhurtaWindows:
    """Daily Muhurta and Kalam windows derived from sunrise and sunset."""

    sunrise_jd: float
    sunset_jd: float
    next_sunrise_jd: float
    vara: VaraInfo
    abhijit_muhurta: TimeWindow
    brahma_muhurta: TimeWindow
    rahu_kalam: TimeWindow
    yamagandam: TimeWindow
    gulika_kalam: TimeWindow
    durmuhurtas: tuple[TimeWindow, ...]


@dataclass(frozen=True)
class PanchangaSummary:
    """Complete Five-Limb Panchanga plus seasonal and calendar metadata."""

    tithi: TithiInfo
    vara: VaraInfo
    nakshatra: NakshatraPosition
    yoga: YogaInfo
    karana: KaranaInfo
    ayana: str
    ritu_sanskrit: str
    ritu_english: str
    samvatsara: SamvatsaraInfo | None = None


def compute_tithi(sun_lon_deg: float, moon_lon_deg: float) -> TithiInfo:
    """Compute Tithi (1..30) from sidereal or tropical Sun and Moon longitudes.

    Note: Because `(lon_moon - lon_sun)` cancels any additive ayanamsa offset,
    Tithi is invariant between tropical and sidereal coordinates.
    """
    elong = normalize_degrees(moon_lon_deg - sun_lon_deg)
    idx = min(int(elong / TITHI_SPAN_DEG), 29)
    number = idx + 1
    deg_in = elong - idx * TITHI_SPAN_DEG
    frac_elapsed = min(max(deg_in / TITHI_SPAN_DEG, 0.0), 1.0)

    if number <= 15:
        paksha = "Shukla"
        paksha_tithi = number
        name = "Purnima" if number == 15 else PAKSHA_TITHI_NAMES[number - 1]
    else:
        paksha = "Krishna"
        paksha_tithi = number - 15
        name = "Amavasya" if number == 30 else PAKSHA_TITHI_NAMES[paksha_tithi - 1]

    group = TITHI_GROUPS[(paksha_tithi - 1) % 5]
    lord = TITHI_EIGHT_LORDS[(paksha_tithi - 1) % 8]

    return TithiInfo(
        number=number,
        paksha=paksha,
        paksha_tithi=paksha_tithi,
        name=name,
        lord=lord,
        group=group,
        elongation_deg=elong,
        degree_in_tithi=deg_in,
        fraction_elapsed=frac_elapsed,
        fraction_remaining=1.0 - frac_elapsed,
    )


def compute_vara(
    jd_ut: float | None = None,
    *,
    sunrise_jd_ut: float | None = None,
    vara_index: int | None = None,
) -> VaraInfo:
    """Compute the Vedic weekday (Vara, 0=Sunday..6=Saturday).

    If `sunrise_jd_ut` is provided and `jd_ut < sunrise_jd_ut`, the instant falls
    before local sunrise and belongs to the preceding Vedic weekday.
    """
    if vara_index is not None:
        idx = int(vara_index) % 7
    elif jd_ut is not None:
        effective_jd = float(sunrise_jd_ut) if (sunrise_jd_ut is not None and jd_ut >= sunrise_jd_ut) else float(jd_ut)
        if sunrise_jd_ut is not None and jd_ut < sunrise_jd_ut:
            effective_jd = float(sunrise_jd_ut) - 1.0
        # JD 0.0 was Monday noon (12:00 UT); floor(JD + 0.5) + 1 mod 7 -> 0=Sun, 1=Mon, ..., 6=Sat
        idx = (int(effective_jd + 0.5) + 1) % 7
    else:
        raise ValueError("Provide either jd_ut or vara_index")

    v_idx, sanskrit, english, ruler = VARA_CATALOG[idx]
    return VaraInfo(index=v_idx, sanskrit_name=sanskrit, english_name=english, ruler=ruler)


def compute_yoga(sun_lon_deg: float, moon_lon_deg: float) -> YogaInfo:
    """Compute the Luni-Solar Yoga (1..27) from sidereal Sun and Moon longitudes."""
    sum_lon = normalize_degrees(sun_lon_deg + moon_lon_deg)
    idx = min(int(sum_lon / YOGA_SPAN_DEG), 26)
    deg_in = sum_lon - idx * YOGA_SPAN_DEG
    frac_elapsed = min(max(deg_in / YOGA_SPAN_DEG, 0.0), 1.0)
    num, name, is_benefic = YOGA_CATALOG[idx]

    return YogaInfo(
        index=idx,
        number=num,
        name=name,
        is_benefic=is_benefic,
        sum_longitude_deg=sum_lon,
        degree_in_yoga=deg_in,
        fraction_elapsed=frac_elapsed,
        fraction_remaining=1.0 - frac_elapsed,
    )


def compute_karana(sun_lon_deg: float, moon_lon_deg: float) -> KaranaInfo:
    """Compute the Karana (1..60 half-tithis of 6 deg each) from Sun and Moon longitudes."""
    elong = normalize_degrees(moon_lon_deg - sun_lon_deg)
    idx = min(int(elong / KARANA_SPAN_DEG), 59)  # 0..59
    number = idx + 1                              # 1..60
    deg_in = elong - idx * KARANA_SPAN_DEG
    frac_elapsed = min(max(deg_in / KARANA_SPAN_DEG, 0.0), 1.0)

    if number == 1:
        name = "Kimstughna"
        kind = "Fixed"
    elif number == 58:
        name = "Shakuni"
        kind = "Fixed"
    elif number == 59:
        name = "Chatushpada"
        kind = "Fixed"
    elif number == 60:
        name = "Naga"
        kind = "Fixed"
    else:
        name = MOVABLE_KARANAS[(number - 2) % 7]
        kind = "Movable"

    return KaranaInfo(
        number=number,
        name=name,
        kind=kind,
        is_vishti_bhadra=(name == "Vishti"),
        degree_in_karana=deg_in,
        fraction_elapsed=frac_elapsed,
        fraction_remaining=1.0 - frac_elapsed,
    )


def compute_samvatsara(year: int, *, calendar: str = "ce") -> SamvatsaraInfo:
    """Compute the 60-year Jovian Samvatsara name for a Common Era (`ce`), `shaka`, or `kali` year.

    In the traditional Panchanga cycle:
    - Shaka year `S` has `(S + 11) % 60` as the 0-based index from Prabhava (1987 CE = Shaka 1909 = Prabhava #1).
    - CE year `Y` corresponds to Shaka `Y - 78`, so `(Y - 1987) % 60` gives 0-based index (e.g. 2026 CE -> #40 Parabhava).
    """
    cal = calendar.strip().lower()
    if cal == "ce":
        idx = (int(year) - 1987) % 60
    elif cal == "shaka":
        idx = (int(year) + 11) % 60
    elif cal == "kali":
        idx = (int(year) - 5088) % 60
    else:
        raise ValueError("calendar must be 'ce', 'shaka', or 'kali'")
    return SamvatsaraInfo(number=idx + 1, name=SAMVATSARA_NAMES[idx])


def compute_ayana_and_ritu(sun_lon_deg: float) -> tuple[str, str, str]:
    """Compute `(ayana, ritu_sanskrit, ritu_english)` from solar longitude.

    - Uttarayana: 270 deg (Makara) through 90 deg (end of Mithuna).
    - Dakshinayana: 90 deg (Karka) through 270 deg (end of Dhanu).
    - 6 Ritus of 60 deg each starting from Makara (270 deg):
      Shishira (270-330), Vasanta (330-30), Grishma (30-90),
      Varsha (90-150), Sharad (150-210), Hemanta (210-270).
    """
    lon = normalize_degrees(sun_lon_deg)
    ayana = "Dakshinayana" if 90.0 <= lon < 270.0 else "Uttarayana"
    shifted = normalize_degrees(lon - 270.0)
    ritu_idx = min(int(shifted // 60.0), 5)
    ritu_sanskrit, ritu_english = RITU_CATALOG[ritu_idx]
    return ayana, ritu_sanskrit, ritu_english


def compute_hora_table(
    sunrise_jd: float,
    sunset_jd: float,
    *,
    next_sunrise_jd: float | None = None,
    vara_index: int | None = None,
) -> tuple[HoraWindow, ...]:
    """Compute the 24 planetary Horas from local sunrise to next sunrise.

    12 daytime Horas divide `(sunset_jd - sunrise_jd)` into 12 equal parts;
    12 nighttime Horas divide `(next_sunrise_jd - sunset_jd)` into 12 equal parts.
    """
    if sunset_jd <= sunrise_jd:
        raise ValueError("sunset_jd must be greater than sunrise_jd")
    next_sr = float(next_sunrise_jd) if next_sunrise_jd is not None else (float(sunrise_jd) + 1.0)
    if next_sr <= sunset_jd:
        raise ValueError("next_sunrise_jd must be greater than sunset_jd")

    vara = compute_vara(sunrise_jd, sunrise_jd_ut=sunrise_jd, vara_index=vara_index)
    start_pos = HORA_CHALDEAN_ORDER.index(vara.ruler)

    day_step = (sunset_jd - sunrise_jd) / 12.0
    night_step = (next_sr - sunset_jd) / 12.0

    windows: list[HoraWindow] = []
    for i in range(24):
        ruler = HORA_CHALDEAN_ORDER[(start_pos + i) % 7]
        if i < 12:
            s_jd = sunrise_jd + i * day_step
            e_jd = sunrise_jd + (i + 1) * day_step
            is_day = True
        else:
            j = i - 12
            s_jd = sunset_jd + j * night_step
            e_jd = sunset_jd + (j + 1) * night_step
            is_day = False
        windows.append(
            HoraWindow(
                hora_number=i + 1,
                is_daytime=is_day,
                ruler=ruler,
                start_jd=s_jd,
                end_jd=e_jd,
            )
        )
    return tuple(windows)


def compute_muhurta_windows(
    sunrise_jd: float,
    sunset_jd: float,
    *,
    next_sunrise_jd: float | None = None,
    vara_index: int | None = None,
) -> MuhurtaWindows:
    """Compute Abhijit Muhurta, Brahma Muhurta, Rahu Kalam, Yamagandam, Gulika Kalam, and Durmuhurtas."""
    if sunset_jd <= sunrise_jd:
        raise ValueError("sunset_jd must be greater than sunrise_jd")
    next_sr = float(next_sunrise_jd) if next_sunrise_jd is not None else (float(sunrise_jd) + 1.0)
    if next_sr <= sunset_jd:
        raise ValueError("next_sunrise_jd must be greater than sunset_jd")

    vara = compute_vara(sunrise_jd, sunrise_jd_ut=sunrise_jd, vara_index=vara_index)
    day_span = sunset_jd - sunrise_jd
    night_span = next_sr - sunset_jd

    day_muhurta = day_span / 15.0
    night_muhurta = night_span / 15.0
    octant = day_span / 8.0

    # Abhijit Muhurta is the 8th daytime Muhurta (0-based index 7)
    ab_start = sunrise_jd + 7.0 * day_muhurta
    ab_end = sunrise_jd + 8.0 * day_muhurta
    abhijit = TimeWindow(
        name="Abhijit Muhurta",
        start_jd=ab_start,
        end_jd=ab_end,
        duration_minutes=day_muhurta * 1440.0,
        is_auspicious=True,
    )

    # Brahma Muhurta is the 14th nighttime Muhurta (2 muhurtas before sunrise to 1 muhurta before sunrise)
    br_start = sunrise_jd - 2.0 * night_muhurta
    br_end = sunrise_jd - 1.0 * night_muhurta
    brahma = TimeWindow(
        name="Brahma Muhurta",
        start_jd=br_start,
        end_jd=br_end,
        duration_minutes=night_muhurta * 1440.0,
        is_auspicious=True,
    )

    def _octant_window(label: str, seg_1based: int) -> TimeWindow:
        s = sunrise_jd + (seg_1based - 1) * octant
        e = sunrise_jd + seg_1based * octant
        return TimeWindow(
            name=label,
            start_jd=s,
            end_jd=e,
            duration_minutes=octant * 1440.0,
            is_auspicious=False,
        )

    rahu = _octant_window("Rahu Kalam", RAHU_KALAM_SEGMENT[vara.index])
    yama = _octant_window("Yamagandam", YAMAGANDAM_SEGMENT[vara.index])
    gulika = _octant_window("Gulika Kalam", GULIKA_KALAM_SEGMENT[vara.index])

    dur_list: list[TimeWindow] = []
    for idx_1based in DURMUHURTA_DAY_INDICES[vara.index]:
        s = sunrise_jd + (idx_1based - 1) * day_muhurta
        e = sunrise_jd + idx_1based * day_muhurta
        dur_list.append(
            TimeWindow(
                name=f"Durmuhurta (Day #{idx_1based})",
                start_jd=s,
                end_jd=e,
                duration_minutes=day_muhurta * 1440.0,
                is_auspicious=False,
            )
        )

    return MuhurtaWindows(
        sunrise_jd=sunrise_jd,
        sunset_jd=sunset_jd,
        next_sunrise_jd=next_sr,
        vara=vara,
        abhijit_muhurta=abhijit,
        brahma_muhurta=brahma,
        rahu_kalam=rahu,
        yamagandam=yama,
        gulika_kalam=gulika,
        durmuhurtas=tuple(dur_list),
    )


def compute_panchanga(
    sun_lon_deg: float,
    moon_lon_deg: float,
    *,
    jd_ut: float | None = None,
    sunrise_jd_ut: float | None = None,
    vara_index: int | None = None,
    ce_year: int | None = None,
) -> PanchangaSummary:
    """Compute the complete Five-Limb Vedic Almanac (Panchanga) at an instant."""
    tithi = compute_tithi(sun_lon_deg, moon_lon_deg)
    vara = compute_vara(jd_ut, sunrise_jd_ut=sunrise_jd_ut, vara_index=vara_index)
    nak = nakshatra_position(moon_lon_deg)
    yoga = compute_yoga(sun_lon_deg, moon_lon_deg)
    karana = compute_karana(sun_lon_deg, moon_lon_deg)
    ayana, ritu_sa, ritu_en = compute_ayana_and_ritu(sun_lon_deg)
    samvatsara = compute_samvatsara(ce_year, calendar="ce") if ce_year is not None else None

    return PanchangaSummary(
        tithi=tithi,
        vara=vara,
        nakshatra=nak,
        yoga=yoga,
        karana=karana,
        ayana=ayana,
        ritu_sanskrit=ritu_sa,
        ritu_english=ritu_en,
        samvatsara=samvatsara,
    )
