"""Clean-room 27-Nakshatra, 108-Pada, Tara Bala, and 28-Nakshatra (Abhijit) engine.

Mathematical basis follows classical Sanskrit jyotisha treatises (*Brihat Parashara
Hora Shastra*, *Surya Siddhanta*, *Muhurta Chintamani*):
- The sidereal ecliptic of 360 degrees is divided into 27 equal lunar mansions
  (nakshatras) of 13 deg 20 min (800 arcminutes = 40/3 degrees) each.
- Each nakshatra is subdivided into 4 equal padas (quarters) of 3 deg 20 min
  (200 arcminutes = 10/3 degrees), yielding 108 padas across the zodiac that map
  cyclically onto the 12 Navamsa signs (0..11).
- In the 28-nakshatra scheme used in *Muhurta* and *Ashtottari*, Abhijit spans from
  the last quarter of Uttara Ashadha (276 deg 40 min = 276 + 2/3 deg) to the first
  fifteenth of Shravana (280 deg 53 min 20 sec = 280 + 8/9 deg), a span of
  4 deg 13 min 20 sec (38/9 degrees).
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Final

NAKSHATRA_SPAN_DEG: Final[float] = 360.0 / 27.0  # 13.333333333333334 deg (800 arcmin)
PADA_SPAN_DEG: Final[float] = 360.0 / 108.0  # 3.3333333333333335 deg (200 arcmin)

ABHIJIT_START_DEG: Final[float] = 276.0 + 40.0 / 60.0  # 276 deg 40 min
ABHIJIT_END_DEG: Final[float] = 280.0 + 53.0 / 60.0 + 20.0 / 3600.0  # 280 deg 53 min 20 sec
ABHIJIT_SPAN_DEG: Final[float] = ABHIJIT_END_DEG - ABHIJIT_START_DEG  # 38/9 deg

RASI_NAMES: Final[tuple[str, ...]] = (
    "Mesha",
    "Vrishabha",
    "Mithuna",
    "Karka",
    "Simha",
    "Kanya",
    "Tula",
    "Vrishchika",
    "Dhanu",
    "Makara",
    "Kumbha",
    "Meena",
)

VIMSHOTTARI_RULERS: Final[tuple[str, ...]] = (
    "Ketu",
    "Venus",
    "Sun",
    "Moon",
    "Mars",
    "Rahu",
    "Jupiter",
    "Saturn",
    "Mercury",
)


@dataclass(frozen=True)
class NakshatraMetadata:
    """Static classical attributes of one of the 27 nakshatras."""

    index: int
    number: int
    name: str
    vimshottari_ruler: str
    deity: str
    gana: str
    nadi: str
    yoni_animal: str
    yoni_gender: str
    varna: str
    vashya: str


NAKSHATRA_CATALOG: Final[tuple[NakshatraMetadata, ...]] = (
    NakshatraMetadata(0, 1, "Ashwini", "Ketu", "Ashwini Kumaras", "Deva", "Adi", "Horse", "Male", "Vaishya", "Chatushpada"),
    NakshatraMetadata(1, 2, "Bharani", "Venus", "Yama", "Manushya", "Madhya", "Elephant", "Male", "Mleccha", "Chatushpada"),
    NakshatraMetadata(2, 3, "Krittika", "Sun", "Agni", "Rakshasa", "Antya", "Sheep", "Female", "Brahmana", "Chatushpada"),
    NakshatraMetadata(3, 4, "Rohini", "Moon", "Brahma", "Manushya", "Antya", "Serpent", "Male", "Shudra", "Chatushpada"),
    NakshatraMetadata(4, 5, "Mrigashirsha", "Mars", "Soma", "Deva", "Madhya", "Serpent", "Female", "Servant", "Chatushpada"),
    NakshatraMetadata(5, 6, "Ardra", "Rahu", "Rudra", "Manushya", "Adi", "Dog", "Female", "Butcher", "Manava"),
    NakshatraMetadata(6, 7, "Punarvasu", "Jupiter", "Aditi", "Deva", "Adi", "Cat", "Female", "Vaishya", "Manava"),
    NakshatraMetadata(7, 8, "Pushya", "Saturn", "Brihaspati", "Deva", "Madhya", "Sheep", "Male", "Kshatriya", "Chatushpada"),
    NakshatraMetadata(8, 9, "Ashlesha", "Mercury", "Sarpas", "Rakshasa", "Antya", "Cat", "Male", "Mleccha", "Keeta"),
    NakshatraMetadata(9, 10, "Magha", "Ketu", "Pitris", "Rakshasa", "Antya", "Rat", "Male", "Shudra", "Chatushpada"),
    NakshatraMetadata(10, 11, "Purva Phalguni", "Venus", "Bhaga", "Manushya", "Madhya", "Rat", "Female", "Brahmana", "Chatushpada"),
    NakshatraMetadata(11, 12, "Uttara Phalguni", "Sun", "Aryaman", "Manushya", "Adi", "Cow", "Male", "Kshatriya", "Chatushpada"),
    NakshatraMetadata(12, 13, "Hasta", "Moon", "Savitar", "Deva", "Adi", "Buffalo", "Female", "Vaishya", "Manava"),
    NakshatraMetadata(13, 14, "Chitra", "Mars", "Twashtar", "Rakshasa", "Madhya", "Tiger", "Female", "Servant", "Vanachara"),
    NakshatraMetadata(14, 15, "Swati", "Rahu", "Vayu", "Deva", "Antya", "Buffalo", "Male", "Butcher", "Manava"),
    NakshatraMetadata(15, 16, "Vishakha", "Jupiter", "Indragni", "Rakshasa", "Antya", "Tiger", "Male", "Mleccha", "Manava"),
    NakshatraMetadata(16, 17, "Anuradha", "Saturn", "Mitra", "Deva", "Madhya", "Deer", "Female", "Shudra", "Keeta"),
    NakshatraMetadata(17, 18, "Jyeshtha", "Mercury", "Indra", "Rakshasa", "Adi", "Deer", "Male", "Servant", "Keeta"),
    NakshatraMetadata(18, 19, "Mula", "Ketu", "Nirriti", "Rakshasa", "Adi", "Dog", "Male", "Butcher", "Chatushpada"),
    NakshatraMetadata(19, 20, "Purva Ashadha", "Venus", "Apah", "Manushya", "Madhya", "Monkey", "Male", "Brahmana", "Manava"),
    NakshatraMetadata(20, 21, "Uttara Ashadha", "Sun", "Vishvadevas", "Manushya", "Antya", "Mongoose", "Male", "Kshatriya", "Manava"),
    NakshatraMetadata(21, 22, "Shravana", "Moon", "Vishnu", "Deva", "Antya", "Monkey", "Female", "Mleccha", "Chatushpada"),
    NakshatraMetadata(22, 23, "Dhanishta", "Mars", "Ashta Vasus", "Rakshasa", "Madhya", "Lion", "Female", "Servant", "Vanachara"),
    NakshatraMetadata(23, 24, "Shatabhisha", "Rahu", "Varuna", "Rakshasa", "Adi", "Horse", "Female", "Butcher", "Jalachara"),
    NakshatraMetadata(24, 25, "Purva Bhadrapada", "Jupiter", "Aja Ekapada", "Manushya", "Adi", "Lion", "Male", "Brahmana", "Manava"),
    NakshatraMetadata(25, 26, "Uttara Bhadrapada", "Saturn", "Ahir Budhnya", "Manushya", "Madhya", "Cow", "Female", "Kshatriya", "Chatushpada"),
    NakshatraMetadata(26, 27, "Revati", "Mercury", "Pushan", "Deva", "Antya", "Elephant", "Female", "Shudra", "Jalachara"),
)

NAKSHATRA_NAMES: Final[tuple[str, ...]] = tuple(item.name for item in NAKSHATRA_CATALOG)

TARA_NAMES: Final[tuple[str, ...]] = (
    "Janma",
    "Sampat",
    "Vipat",
    "Kshema",
    "Pratyak",
    "Sadhana",
    "Naidhana",
    "Mitra",
    "Parama-Mitra",
)

TARA_BENEFIC: Final[tuple[bool, ...]] = (
    False,  # 1 Janma (mixed/caution to body)
    True,   # 2 Sampat (wealth/prosperity)
    False,  # 3 Vipat (danger/obstacles)
    True,   # 4 Kshema (well-being)
    False,  # 5 Pratyak (impediments)
    True,   # 6 Sadhana (accomplishment)
    False,  # 7 Naidhana (destruction/peril)
    True,   # 8 Mitra (friendly)
    True,   # 9 Parama-Mitra (supreme friend)
)


@dataclass(frozen=True)
class NakshatraPosition:
    """Computed 27-nakshatra and 108-pada position for a sidereal longitude."""

    longitude_deg: float
    index: int
    number: int
    name: str
    pada: int
    global_pada: int
    vimshottari_ruler: str
    deity: str
    gana: str
    nadi: str
    yoni_animal: str
    yoni_gender: str
    varna: str
    vashya: str
    navamsa_sign: int
    navamsa_sign_name: str
    degree_in_nakshatra: float
    degree_in_pada: float
    fraction_elapsed: float
    fraction_remaining: float


@dataclass(frozen=True)
class TaraBalaResult:
    """Nine-fold Tara Bala relationship from the natal Moon nakshatra."""

    natal_nakshatra_index: int
    natal_nakshatra_name: str
    target_nakshatra_index: int
    target_nakshatra_name: str
    count_from_natal: int
    tara_number: int
    tara_name: str
    paryaya_cycle: int
    is_benefic: bool


@dataclass(frozen=True)
class AbhijitPosition:
    """Position within the 28-nakshatra system including Abhijit in Makara."""

    longitude_deg: float
    in_abhijit: bool
    nakshatra_28_index: int
    nakshatra_28_name: str
    start_deg: float
    end_deg: float
    span_deg: float
    degree_in_nakshatra: float
    fraction_elapsed: float
    fraction_remaining: float


def normalize_degrees(lon_deg: float) -> float:
    """Normalize an angle in degrees into the half-open interval [0.0, 360.0)."""
    val = float(lon_deg) % 360.0
    if val < 0.0 or val >= 360.0:
        val = 0.0
    return val


def nakshatra_position(sidereal_lon_deg: float) -> NakshatraPosition:
    """Compute the 27-nakshatra and 108-pada state for a sidereal longitude."""
    lon = normalize_degrees(sidereal_lon_deg)
    scaled_nak = lon / NAKSHATRA_SPAN_DEG
    nak_index = min(int(scaled_nak), 26)
    deg_in_nak = lon - nak_index * NAKSHATRA_SPAN_DEG
    if deg_in_nak < 0.0:
        deg_in_nak = 0.0
    elif deg_in_nak > NAKSHATRA_SPAN_DEG:
        deg_in_nak = NAKSHATRA_SPAN_DEG

    fraction_elapsed = min(max(deg_in_nak / NAKSHATRA_SPAN_DEG, 0.0), 1.0)
    fraction_remaining = 1.0 - fraction_elapsed

    pada_zero = min(int(deg_in_nak / PADA_SPAN_DEG), 3)
    pada = pada_zero + 1
    deg_in_pada = deg_in_nak - pada_zero * PADA_SPAN_DEG
    global_pada = nak_index * 4 + pada
    navamsa_sign = (global_pada - 1) % 12

    meta = NAKSHATRA_CATALOG[nak_index]
    return NakshatraPosition(
        longitude_deg=lon,
        index=nak_index,
        number=meta.number,
        name=meta.name,
        pada=pada,
        global_pada=global_pada,
        vimshottari_ruler=meta.vimshottari_ruler,
        deity=meta.deity,
        gana=meta.gana,
        nadi=meta.nadi,
        yoni_animal=meta.yoni_animal,
        yoni_gender=meta.yoni_gender,
        varna=meta.varna,
        vashya=meta.vashya,
        navamsa_sign=navamsa_sign,
        navamsa_sign_name=RASI_NAMES[navamsa_sign],
        degree_in_nakshatra=deg_in_nak,
        degree_in_pada=deg_in_pada,
        fraction_elapsed=fraction_elapsed,
        fraction_remaining=fraction_remaining,
    )


def compute_tara_bala(
    natal_moon_lon_deg: float | None = None,
    target_lon_deg: float | None = None,
    *,
    natal_nakshatra_index: int | None = None,
    target_nakshatra_index: int | None = None,
) -> TaraBalaResult:
    """Compute the 9-fold Tara Bala relationship between natal Moon and target nakshatra.

    Accepts either sidereal longitudes (`natal_moon_lon_deg`, `target_lon_deg`)
    or explicit 0-based nakshatra indices (`0..26`).
    """
    if natal_nakshatra_index is None:
        if natal_moon_lon_deg is None:
            raise ValueError("Specify either natal_moon_lon_deg or natal_nakshatra_index")
        natal_idx = nakshatra_position(natal_moon_lon_deg).index
    else:
        if not 0 <= natal_nakshatra_index <= 26:
            raise ValueError("natal_nakshatra_index must be in 0..26")
        natal_idx = int(natal_nakshatra_index)

    if target_nakshatra_index is None:
        if target_lon_deg is None:
            raise ValueError("Specify either target_lon_deg or target_nakshatra_index")
        target_idx = nakshatra_position(target_lon_deg).index
    else:
        if not 0 <= target_nakshatra_index <= 26:
            raise ValueError("target_nakshatra_index must be in 0..26")
        target_idx = int(target_nakshatra_index)

    count_from_natal = ((target_idx - natal_idx) % 27) + 1
    tara_zero = (count_from_natal - 1) % 9
    tara_number = tara_zero + 1
    paryaya_cycle = ((count_from_natal - 1) // 9) + 1

    return TaraBalaResult(
        natal_nakshatra_index=natal_idx,
        natal_nakshatra_name=NAKSHATRA_CATALOG[natal_idx].name,
        target_nakshatra_index=target_idx,
        target_nakshatra_name=NAKSHATRA_CATALOG[target_idx].name,
        count_from_natal=count_from_natal,
        tara_number=tara_number,
        tara_name=TARA_NAMES[tara_zero],
        paryaya_cycle=paryaya_cycle,
        is_benefic=TARA_BENEFIC[tara_zero],
    )


def abhijit_position(sidereal_lon_deg: float) -> AbhijitPosition:
    """Compute position in the 28-nakshatra scheme where Abhijit sits between
    Uttara Ashadha and Shravana (276 deg 40 min to 280 deg 53 min 20 sec).

    In the 28-nakshatra partition:
    - Indices 0..19 are identical to the 27-nakshatra system (13 deg 20 min each).
    - Index 20 (Uttara Ashadha) covers 266 deg 40 min to 276 deg 40 min (10 deg = 3 padas).
    - Index 21 (Abhijit) covers 276 deg 40 min to 280 deg 53 min 20 sec (38/9 deg).
    - Index 22 (Shravana) covers 280 deg 53 min 20 sec to 293 deg 20 min (112/9 deg = 14/15 of 800').
    - Indices 23..27 correspond to Dhanishta through Revati (13 deg 20 min each).
    """
    lon = normalize_degrees(sidereal_lon_deg)
    ua_start = 20 * NAKSHATRA_SPAN_DEG  # 266.6666666666667
    shravana_end = 22 * NAKSHATRA_SPAN_DEG  # 293.3333333333333

    if lon < ua_start:
        idx = min(int(lon / NAKSHATRA_SPAN_DEG), 19)
        start = idx * NAKSHATRA_SPAN_DEG
        end = (idx + 1) * NAKSHATRA_SPAN_DEG
        name = NAKSHATRA_CATALOG[idx].name
        in_abhijit = False
    elif lon < ABHIJIT_START_DEG:
        idx = 20
        start = ua_start
        end = ABHIJIT_START_DEG
        name = "Uttara Ashadha"
        in_abhijit = False
    elif lon < ABHIJIT_END_DEG:
        idx = 21
        start = ABHIJIT_START_DEG
        end = ABHIJIT_END_DEG
        name = "Abhijit"
        in_abhijit = True
    elif lon < shravana_end:
        idx = 22
        start = ABHIJIT_END_DEG
        end = shravana_end
        name = "Shravana"
        in_abhijit = False
    else:
        std_idx = min(max(int(lon / NAKSHATRA_SPAN_DEG), 22), 26)
        idx = std_idx + 1
        start = std_idx * NAKSHATRA_SPAN_DEG
        end = (std_idx + 1) * NAKSHATRA_SPAN_DEG
        name = NAKSHATRA_CATALOG[std_idx].name
        in_abhijit = False

    span = end - start
    deg_in = max(0.0, min(lon - start, span))
    frac_elapsed = deg_in / span if span > 0 else 0.0
    return AbhijitPosition(
        longitude_deg=lon,
        in_abhijit=in_abhijit,
        nakshatra_28_index=idx,
        nakshatra_28_name=name,
        start_deg=start,
        end_deg=end,
        span_deg=span,
        degree_in_nakshatra=deg_in,
        fraction_elapsed=frac_elapsed,
        fraction_remaining=1.0 - frac_elapsed,
    )
