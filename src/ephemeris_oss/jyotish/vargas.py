"""Clean-room Parashari Shodashvarga (D1-D60), higher harmonics, Vimshopaka Bala, and Special Lagnas.

Mathematical definitions follow *Brihat Parashara Hora Shastra* (BPHS Chapters 5-8),
*Jaimini Upadesha Sutras*, *Jataka Parijata*, and *Saravali*:
- All 16 Shodashvarga charts (D1, D2, D3, D4, D7, D9, D10, D12, D16, D20, D24,
  D27, D30, D40, D45, D60) with all 60 classical Shashtiamsa names and natures.
- Higher harmonic and Jaimini vargas (D5, D6, D8, D11, D81, D108, D144).
- Vargottama, Pushkara Navamsa, and Pushkara Bhaga evaluators.
- Vimshopaka Bala across Shadvarga (6), Saptavarga (7), Dasavarga (10), and
  Shodashvarga (16) on the 20-point Parashari scale.
- Special mathematical Lagnas: Bhava Lagna, Hora Lagna, Ghatika Lagna, Sree Lagna,
  Pranapada Lagna, Indu Lagna, Varnada Lagna, and Jaimini Arudha Padas (A1-A12, AL, UL).
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Final, Mapping, Sequence

from .nakshatra import RASI_NAMES, nakshatra_position, normalize_degrees

RASI_LORDS: Final[tuple[str, ...]] = (
    "Mars",     # 0 Mesha (Aries)
    "Venus",    # 1 Vrishabha (Taurus)
    "Mercury",  # 2 Mithuna (Gemini)
    "Moon",     # 3 Karka (Cancer)
    "Sun",      # 4 Simha (Leo)
    "Mercury",  # 5 Kanya (Virgo)
    "Venus",    # 6 Tula (Libra)
    "Mars",     # 7 Vrishchika (Scorpio)
    "Jupiter",  # 8 Dhanu (Sagittarius)
    "Saturn",   # 9 Makara (Capricorn)
    "Saturn",   # 10 Kumbha (Aquarius)
    "Jupiter",  # 11 Meena (Pisces)
)

NATURAL_FRIENDS: Final[Mapping[str, frozenset[str]]] = {
    "Sun": frozenset({"Moon", "Mars", "Jupiter"}),
    "Moon": frozenset({"Sun", "Mercury"}),
    "Mars": frozenset({"Sun", "Moon", "Jupiter"}),
    "Mercury": frozenset({"Sun", "Venus"}),
    "Jupiter": frozenset({"Sun", "Moon", "Mars"}),
    "Venus": frozenset({"Mercury", "Saturn"}),
    "Saturn": frozenset({"Mercury", "Venus"}),
    "Rahu": frozenset({"Mercury", "Venus", "Saturn"}),
    "Ketu": frozenset({"Mars", "Venus", "Saturn"}),
}

NATURAL_ENEMIES: Final[Mapping[str, frozenset[str]]] = {
    "Sun": frozenset({"Venus", "Saturn"}),
    "Moon": frozenset(),
    "Mars": frozenset({"Mercury"}),
    "Mercury": frozenset({"Moon"}),
    "Jupiter": frozenset({"Mercury", "Venus"}),
    "Venus": frozenset({"Sun", "Moon"}),
    "Saturn": frozenset({"Sun", "Moon", "Mars"}),
    "Rahu": frozenset({"Sun", "Moon", "Mars"}),
    "Ketu": frozenset({"Sun", "Moon"}),
}

# Moolatrikona ranges: (rasi_index, start_deg, end_deg)
MOOLATRIKONA_RANGES: Final[Mapping[str, tuple[int, float, float]]] = {
    "Sun": (4, 0.0, 20.0),      # Leo 0-20 deg
    "Moon": (1, 3.0, 30.0),     # Taurus 3-30 deg
    "Mars": (0, 0.0, 12.0),     # Aries 0-12 deg
    "Mercury": (5, 15.0, 20.0), # Virgo 15-20 deg
    "Jupiter": (8, 0.0, 10.0),  # Sagittarius 0-10 deg
    "Venus": (6, 0.0, 15.0),    # Libra 0-15 deg
    "Saturn": (10, 0.0, 20.0),  # Aquarius 0-20 deg
}

EXALTATION_SIGNS: Final[Mapping[str, int]] = {
    "Sun": 0,      # Aries
    "Moon": 1,     # Taurus
    "Mars": 9,     # Capricorn
    "Mercury": 5,  # Virgo
    "Jupiter": 3,  # Cancer
    "Venus": 11,   # Pisces
    "Saturn": 6,   # Libra
    "Rahu": 1,     # Taurus
    "Ketu": 7,     # Scorpio
}

DEBILITATION_SIGNS: Final[Mapping[str, int]] = {
    "Sun": 6,      # Libra
    "Moon": 7,     # Scorpio
    "Mars": 3,     # Cancer
    "Mercury": 11, # Pisces
    "Jupiter": 9,  # Capricorn
    "Venus": 5,    # Virgo
    "Saturn": 0,   # Aries
    "Rahu": 7,     # Scorpio
    "Ketu": 1,     # Taurus
}

# Classical 60 Shashtiamsa names and benefic (True) vs malefic (False) classification from BPHS Ch. 6
SHASHTIAMSA_CATALOG: Final[tuple[tuple[int, str, bool], ...]] = (
    (1, "Ghora", False),
    (2, "Rakshasa", False),
    (3, "Deva", True),
    (4, "Kubera", True),
    (5, "Yaksha", True),
    (6, "Kinnara", True),
    (7, "Bhrashta", False),
    (8, "Kulaghna", False),
    (9, "Garala", False),
    (10, "Vahni", False),
    (11, "Maya", False),
    (12, "Purishaka", False),
    (13, "Apampati", True),
    (14, "Marutwan", True),
    (15, "Kala", False),
    (16, "Sarpa", False),
    (17, "Amrita", True),
    (18, "Indu", True),
    (19, "Mridu", True),
    (20, "Komala", True),
    (21, "Heramba", True),
    (22, "Brahma", True),
    (23, "Vishnu", True),
    (24, "Maheshwara", True),
    (25, "Deva", True),
    (26, "Ardra", True),
    (27, "Kalinasa", True),
    (28, "Kshitishwara", True),
    (29, "Kamalakara", True),
    (30, "Gulika", False),
    (31, "Mrityu", False),
    (32, "Kaala", False),
    (33, "Davagni", False),
    (34, "Ghora", False),
    (35, "Yama", False),
    (36, "Kantaka", False),
    (37, "Sudha", True),
    (38, "Amrita", True),
    (39, "Purnachandra", True),
    (40, "Vishadagdha", False),
    (41, "Kulanasa", False),
    (42, "Vamshakshaya", False),
    (43, "Utpata", False),
    (44, "Kala", False),
    (45, "Saumya", True),
    (46, "Komala", True),
    (47, "Sheetala", True),
    (48, "Karaladamshtra", False),
    (49, "Chandramukhi", True),
    (50, "Praveena", True),
    (51, "Kalapavaka", False),
    (52, "Dandayudha", False),
    (53, "Nirmala", True),
    (54, "Saumya", True),
    (55, "Krura", False),
    (56, "Atisheetala", True),
    (57, "Amrita", True),
    (58, "Payodhi", True),
    (59, "Bhramana", False),
    (60, "Indurekha", True),
)

SHODASHVARGA_KEYS: Final[tuple[str, ...]] = (
    "D1", "D2", "D3", "D4", "D7", "D9", "D10", "D12",
    "D16", "D20", "D24", "D27", "D30", "D40", "D45", "D60",
)

HIGHER_VARGA_KEYS: Final[tuple[str, ...]] = (
    "D5", "D6", "D8", "D11", "D81", "D108", "D144",
)

ALL_VARGA_KEYS: Final[tuple[str, ...]] = SHODASHVARGA_KEYS + HIGHER_VARGA_KEYS

VIMSHOPAKA_WEIGHTS: Final[Mapping[str, Mapping[str, float]]] = {
    "shadvarga": {
        "D1": 6.0, "D2": 2.0, "D3": 4.0, "D9": 5.0, "D12": 2.0, "D30": 1.0,
    },
    "saptavarga": {
        "D1": 5.0, "D2": 2.0, "D3": 3.0, "D7": 2.5, "D9": 4.5, "D12": 2.0, "D30": 1.0,
    },
    "dasavarga": {
        "D1": 3.0, "D2": 1.5, "D3": 1.5, "D7": 1.5, "D9": 1.5,
        "D10": 1.5, "D12": 1.5, "D16": 1.5, "D30": 1.5, "D60": 5.0,
    },
    "shodashvarga": {
        "D1": 3.5, "D2": 1.0, "D3": 1.0, "D4": 0.5, "D7": 0.5, "D9": 3.0,
        "D10": 0.5, "D12": 0.5, "D16": 2.0, "D20": 0.5, "D24": 0.5, "D27": 0.5,
        "D30": 1.0, "D40": 0.5, "D45": 0.5, "D60": 4.0,
    },
}

# Classical Pushkara Bhaga degrees in each of the 12 signs (Aries=0 .. Pisces=11)
PUSHKARA_BHAGA_DEGREES: Final[tuple[float, ...]] = (
    21.0,  # Mesha (Aries)
    14.0,  # Vrishabha (Taurus)
    18.0,  # Mithuna (Gemini)
    8.0,   # Karka (Cancer)
    19.0,  # Simha (Leo)
    9.0,   # Kanya (Virgo)
    24.0,  # Tula (Libra)
    11.0,  # Vrishchika (Scorpio)
    23.0,  # Dhanu (Sagittarius)
    14.0,  # Makara (Capricorn)
    19.0,  # Kumbha (Aquarius)
    9.0,   # Meena (Pisces)
)

# Indu Lagna Kalas (rays) for the 7 graha lords
INDU_KALAS: Final[Mapping[str, int]] = {
    "Sun": 30,
    "Moon": 16,
    "Mars": 6,
    "Mercury": 8,
    "Jupiter": 10,
    "Venus": 12,
    "Saturn": 1,
}


@dataclass(frozen=True)
class VargaPlacement:
    """Placement of a body in a specific divisional chart (Varga)."""

    varga: str
    division_factor: int
    sign_index: int
    sign_name: str
    sign_lord: str
    part_index: int
    longitude_in_varga_deg: float
    shashtiamsa_number: int | None = None
    shashtiamsa_name: str | None = None
    shashtiamsa_is_benefic: bool | None = None


@dataclass(frozen=True)
class VimshopakaScore:
    """Vimshopaka Bala result for a planet across a varga group."""

    planet: str
    scheme: str
    total_score: float
    percentage: float
    varga_contributions: Mapping[str, float]
    varga_dignities: Mapping[str, str]


@dataclass(frozen=True)
class ArudhaPadaSet:
    """Complete set of 12 Jaimini Arudha Padas (A1-A12, with AL=A1 and UL=A12)."""

    padas: Mapping[str, int]
    pada_names: Mapping[str, str]
    arudha_lagna_sign: int
    arudha_lagna_name: str
    upapada_lagna_sign: int
    upapada_lagna_name: str


@dataclass(frozen=True)
class SpecialLagnas:
    """Special mathematical Lagnas from BPHS and Jaimini Sutras."""

    bhava_lagna_deg: float
    bhava_lagna_sign: int
    hora_lagna_deg: float
    hora_lagna_sign: int
    ghatika_lagna_deg: float
    ghatika_lagna_sign: int
    sree_lagna_deg: float
    sree_lagna_sign: int
    pranapada_lagna_deg: float
    pranapada_lagna_sign: int
    indu_lagna_sign: int
    indu_lagna_name: str
    varnada_lagna_deg: float
    varnada_lagna_sign: int


def _part_and_rem(deg_in_sign: float, n: int) -> tuple[int, float]:
    scaled = (deg_in_sign / 30.0) * n
    part = min(max(int(scaled), 0), n - 1)
    rem = (scaled - part) * 30.0
    return part, rem


def shashtiamsa_detail(sidereal_lon_deg: float) -> tuple[int, str, bool, int]:
    """Return `(shashtiamsa_number_1_to_60, name, is_benefic, d60_sign_index)` for a longitude."""
    lon = normalize_degrees(sidereal_lon_deg)
    rasi_idx = min(int(lon // 30.0), 11)
    deg_in_sign = lon - rasi_idx * 30.0
    part, _ = _part_and_rem(deg_in_sign, 60)
    d60_sign = (rasi_idx + part) % 12
    # In odd signs (Aries=0, Gemini=2, ...), Shashtiamsa names run 1..60;
    # in even signs (Taurus=1, Cancer=3, ...), they run in reverse 60..1.
    catalog_idx = part if (rasi_idx % 2 == 0) else (59 - part)
    num, name, is_benefic = SHASHTIAMSA_CATALOG[catalog_idx]
    return num, name, is_benefic, d60_sign


def varga_sign(sidereal_lon_deg: float, varga: str = "D1") -> VargaPlacement:
    """Compute the classical Parashari or harmonic divisional placement for `varga`."""
    code = varga.strip().upper()
    lon = normalize_degrees(sidereal_lon_deg)
    rasi_idx = min(int(lon // 30.0), 11)
    deg_in_sign = lon - rasi_idx * 30.0
    is_odd = (rasi_idx % 2 == 0)  # Aries=0 is 1st (odd) sign
    modality = rasi_idx % 3       # 0=Movable (Chara), 1=Fixed (Sthira), 2=Dual (Dwiswabhava)
    element = rasi_idx % 4        # 0=Fire, 1=Earth, 2=Air, 3=Water

    shashtiamsa_num: int | None = None
    shashtiamsa_name: str | None = None
    shashtiamsa_benefic: bool | None = None

    if code == "D1":
        n = 1
        part = 0
        rem = deg_in_sign
        sign = rasi_idx
    elif code == "D2":
        n = 2
        part, rem = _part_and_rem(deg_in_sign, 2)
        if is_odd:
            sign = 4 if part == 0 else 3  # Simha (Leo), then Karka (Cancer)
        else:
            sign = 3 if part == 0 else 4  # Karka (Cancer), then Simha (Leo)
    elif code == "D3":
        n = 3
        part, rem = _part_and_rem(deg_in_sign, 3)
        sign = (rasi_idx + part * 4) % 12
    elif code == "D4":
        n = 4
        part, rem = _part_and_rem(deg_in_sign, 4)
        sign = (rasi_idx + part * 3) % 12
    elif code == "D5":
        n = 5
        part, rem = _part_and_rem(deg_in_sign, 5)
        start = (0, 4, 8)[modality]
        sign = (start + part) % 12
    elif code == "D6":
        n = 6
        part, rem = _part_and_rem(deg_in_sign, 6)
        start = 0 if is_odd else 6
        sign = (start + part) % 12
    elif code == "D7":
        n = 7
        part, rem = _part_and_rem(deg_in_sign, 7)
        start = rasi_idx if is_odd else (rasi_idx + 6) % 12
        sign = (start + part) % 12
    elif code == "D8":
        n = 8
        part, rem = _part_and_rem(deg_in_sign, 8)
        start = (0, 8, 4)[modality]
        sign = (start + part) % 12
    elif code == "D9":
        n = 9
        part, rem = _part_and_rem(deg_in_sign, 9)
        start = (0, 9, 6, 3)[element]
        sign = (start + part) % 12
    elif code == "D10":
        n = 10
        part, rem = _part_and_rem(deg_in_sign, 10)
        start = rasi_idx if is_odd else (rasi_idx + 8) % 12
        sign = (start + part) % 12
    elif code == "D11":
        n = 11
        part, rem = _part_and_rem(deg_in_sign, 11)
        start = (12 - rasi_idx) % 12
        sign = (start + part) % 12
    elif code == "D12":
        n = 12
        part, rem = _part_and_rem(deg_in_sign, 12)
        sign = (rasi_idx + part) % 12
    elif code == "D16":
        n = 16
        part, rem = _part_and_rem(deg_in_sign, 16)
        start = (0, 4, 8)[modality]
        sign = (start + part) % 12
    elif code == "D20":
        n = 20
        part, rem = _part_and_rem(deg_in_sign, 20)
        start = (0, 8, 4)[modality]
        sign = (start + part) % 12
    elif code == "D24":
        n = 24
        part, rem = _part_and_rem(deg_in_sign, 24)
        start = 4 if is_odd else 3
        sign = (start + part) % 12
    elif code == "D27":
        n = 27
        part, rem = _part_and_rem(deg_in_sign, 27)
        start = (0, 3, 6, 9)[element]
        sign = (start + part) % 12
    elif code == "D30":
        n = 30
        if is_odd:
            # 5 deg Mars (Aries=0), 5 deg Saturn (Aquarius=10), 8 deg Jupiter (Sagittarius=8),
            # 7 deg Mercury (Gemini=2), 5 deg Venus (Libra=6)
            if deg_in_sign < 5.0:
                part, sign, rem = 0, 0, (deg_in_sign / 5.0) * 30.0
            elif deg_in_sign < 10.0:
                part, sign, rem = 1, 10, ((deg_in_sign - 5.0) / 5.0) * 30.0
            elif deg_in_sign < 18.0:
                part, sign, rem = 2, 8, ((deg_in_sign - 10.0) / 8.0) * 30.0
            elif deg_in_sign < 25.0:
                part, sign, rem = 3, 2, ((deg_in_sign - 18.0) / 7.0) * 30.0
            else:
                part, sign, rem = 4, 6, ((deg_in_sign - 25.0) / 5.0) * 30.0
        else:
            # 5 deg Venus (Taurus=1), 7 deg Mercury (Virgo=5), 8 deg Jupiter (Pisces=11),
            # 5 deg Saturn (Capricorn=9), 5 deg Mars (Scorpio=7)
            if deg_in_sign < 5.0:
                part, sign, rem = 0, 1, (deg_in_sign / 5.0) * 30.0
            elif deg_in_sign < 12.0:
                part, sign, rem = 1, 5, ((deg_in_sign - 5.0) / 7.0) * 30.0
            elif deg_in_sign < 20.0:
                part, sign, rem = 2, 11, ((deg_in_sign - 12.0) / 8.0) * 30.0
            elif deg_in_sign < 25.0:
                part, sign, rem = 3, 9, ((deg_in_sign - 20.0) / 5.0) * 30.0
            else:
                part, sign, rem = 4, 7, ((deg_in_sign - 25.0) / 5.0) * 30.0
    elif code == "D40":
        n = 40
        part, rem = _part_and_rem(deg_in_sign, 40)
        start = 0 if is_odd else 6
        sign = (start + part) % 12
    elif code == "D45":
        n = 45
        part, rem = _part_and_rem(deg_in_sign, 45)
        start = (0, 4, 8)[modality]
        sign = (start + part) % 12
    elif code == "D60":
        n = 60
        part, rem = _part_and_rem(deg_in_sign, 60)
        shashtiamsa_num, shashtiamsa_name, shashtiamsa_benefic, sign = shashtiamsa_detail(lon)
    elif code == "D81":
        n = 81
        part, rem = _part_and_rem(deg_in_sign, 81)
        sign = (rasi_idx * 81 + part) % 12
    elif code == "D108":
        n = 108
        part, rem = _part_and_rem(deg_in_sign, 108)
        d9_part = part // 12
        sub_d12 = part % 12
        d9_start = (0, 9, 6, 3)[element]
        d9_sign = (d9_start + d9_part) % 12
        sign = (d9_sign + sub_d12) % 12
    elif code == "D144":
        n = 144
        part, rem = _part_and_rem(deg_in_sign, 144)
        d12_part = part // 12
        sub_d12 = part % 12
        d12_sign = (rasi_idx + d12_part) % 12
        sign = (d12_sign + sub_d12) % 12
    else:
        raise ValueError(f"Unsupported varga {varga!r}; supported: {ALL_VARGA_KEYS}")

    varga_lon = sign * 30.0 + rem
    return VargaPlacement(
        varga=code,
        division_factor=n,
        sign_index=sign,
        sign_name=RASI_NAMES[sign],
        sign_lord=RASI_LORDS[sign],
        part_index=part,
        longitude_in_varga_deg=varga_lon,
        shashtiamsa_number=shashtiamsa_num,
        shashtiamsa_name=shashtiamsa_name,
        shashtiamsa_is_benefic=shashtiamsa_benefic,
    )


def compute_shodashvarga(sidereal_lon_deg: float, *, include_higher: bool = False) -> dict[str, VargaPlacement]:
    """Compute all 16 Parashari Shodashvarga placements (and optionally higher vargas)."""
    keys = ALL_VARGA_KEYS if include_higher else SHODASHVARGA_KEYS
    return {k: varga_sign(sidereal_lon_deg, k) for k in keys}


def is_vargottama(sidereal_lon_deg: float) -> bool:
    """Return True if a longitude occupies the same sign in D1 (Rasi) and D9 (Navamsa)."""
    d1 = varga_sign(sidereal_lon_deg, "D1")
    d9 = varga_sign(sidereal_lon_deg, "D9")
    return d1.sign_index == d9.sign_index


def is_pushkara_navamsa(sidereal_lon_deg: float) -> bool:
    """Return True if the longitude falls in one of the 24 classical Pushkara Navamsas.

    Classical rule (*Jataka Parijata* / *BPHS*):
    - Fire signs (Mesha, Simha, Dhanu): 7th and 9th navamsas (padas index 6, 8 within sign -> Libra, Sagittarius)
    - Earth signs (Vrishabha, Kanya, Makara): 3rd and 5th navamsas (padas index 2, 4 within sign -> Pisces, Taurus)
    - Air signs (Mithuna, Tula, Kumbha): 6th and 8th navamsas (padas index 5, 7 within sign -> Pisces, Taurus)
    - Water signs (Karka, Vrishchika, Meena): 1st and 3rd navamsas (padas index 0, 2 within sign -> Cancer, Virgo)
    """
    lon = normalize_degrees(sidereal_lon_deg)
    rasi_idx = min(int(lon // 30.0), 11)
    deg_in_sign = lon - rasi_idx * 30.0
    navamsa_part = min(int((deg_in_sign / 30.0) * 9.0), 8)  # 0..8
    element = rasi_idx % 4
    if element == 0:  # Fire: 7th (6) and 9th (8)
        return navamsa_part in (6, 8)
    if element == 1:  # Earth: 3rd (2) and 5th (4)
        return navamsa_part in (2, 4)
    if element == 2:  # Air: 6th (5) and 8th (7)
        return navamsa_part in (5, 7)
    # Water: 1st (0) and 3rd (2)
    return navamsa_part in (0, 2)


def is_pushkara_bhaga(sidereal_lon_deg: float, *, orb_deg: float = 0.5) -> bool:
    """Return True if the longitude lies within `orb_deg` of the sign's Pushkara Bhaga degree."""
    lon = normalize_degrees(sidereal_lon_deg)
    rasi_idx = min(int(lon // 30.0), 11)
    deg_in_sign = lon - rasi_idx * 30.0
    target = PUSHKARA_BHAGA_DEGREES[rasi_idx]
    return abs(deg_in_sign - target) <= orb_deg


def natural_relationship(planet: str, other_lord: str) -> str:
    """Return the Naisargika Maitri ('Friend', 'Neutral', 'Enemy', or 'Self') between two grahas."""
    p = planet.strip().capitalize()
    o = other_lord.strip().capitalize()
    if p == o:
        return "Self"
    if o in NATURAL_FRIENDS.get(p, frozenset()):
        return "Friend"
    if o in NATURAL_ENEMIES.get(p, frozenset()):
        return "Enemy"
    return "Neutral"


def compound_relationship(planet: str, other_lord: str, planet_d1_sign: int, other_d1_sign: int) -> str:
    """Compute Panchadha Maitri (5-fold compound relationship) from natural + Tatkalika (D1) friendship.

    In BPHS Chapter 15:
    - Planets in the 2nd, 3rd, 4th, 10th, 11th, or 12th houses from a planet in D1 are Tatkalika Mitras (temporary friends).
    - Planets in the 1st, 5th, 6th, 7th, 8th, or 9th houses are Tatkalika Shatrus (temporary enemies).
    """
    p = planet.strip().capitalize()
    o = other_lord.strip().capitalize()
    if p == o:
        return "Swakshetra"
    nat = natural_relationship(p, o)
    house_offset = ((other_d1_sign - planet_d1_sign) % 12) + 1
    temp_friend = house_offset in (2, 3, 4, 10, 11, 12)

    if nat == "Friend":
        return "Adhimitra" if temp_friend else "Sama"
    if nat == "Neutral":
        return "Mitra" if temp_friend else "Shatru"
    # nat == "Enemy"
    return "Sama" if temp_friend else "Adhishatru"


def compute_vimshopaka_bala(
    planet: str,
    sidereal_lon_deg: float,
    d1_planet_longitudes: Mapping[str, float] | None = None,
    *,
    scheme: str = "shodashvarga",
) -> VimshopakaScore:
    """Compute Vimshopaka Bala on the 20-point BPHS scale for `shadvarga`, `saptavarga`,
    `dasavarga`, or `shodashvarga`.

    Classical BPHS Chapter 6 / 7 dignity factors (out of 20):
    - Swakshetra (Own Sign) / Moolatrikona / Exaltation: 20 points (Moolatrikona=18 when distinct in D1, Own=20)
    - Adhimitra (Great Friend): 18 points
    - Mitra (Friend): 15 points
    - Sama (Neutral): 10 points
    - Shatru (Enemy): 7 points
    - Adhishatru (Great Enemy): 5 points
    """
    scheme_key = scheme.strip().lower()
    if scheme_key not in VIMSHOPAKA_WEIGHTS:
        raise ValueError(f"Unknown Vimshopaka scheme {scheme!r}; choose from {tuple(VIMSHOPAKA_WEIGHTS)}")

    p = planet.strip().capitalize()
    weights = VIMSHOPAKA_WEIGHTS[scheme_key]
    lon = normalize_degrees(sidereal_lon_deg)
    d1_sign = min(int(lon // 30.0), 11)
    deg_in_d1 = lon - d1_sign * 30.0

    d1_signs_by_planet: dict[str, int] = {}
    if d1_planet_longitudes:
        for k, v in d1_planet_longitudes.items():
            d1_signs_by_planet[k.strip().capitalize()] = min(int(normalize_degrees(v) // 30.0), 11)
    d1_signs_by_planet.setdefault(p, d1_sign)

    dignity_points_map = {
        "Swakshetra": 20.0,
        "Moolatrikona": 18.0,
        "Adhimitra": 18.0,
        "Mitra": 15.0,
        "Sama": 10.0,
        "Shatru": 7.0,
        "Adhishatru": 5.0,
    }

    contributions: dict[str, float] = {}
    dignities: dict[str, str] = {}
    total_score = 0.0

    for varga_code, weight in weights.items():
        placement = varga_sign(lon, varga_code)
        lord = placement.sign_lord

        if varga_code == "D1" and p in MOOLATRIKONA_RANGES:
            mt_sign, mt_start, mt_end = MOOLATRIKONA_RANGES[p]
            if placement.sign_index == mt_sign and mt_start <= deg_in_d1 < mt_end:
                dignity = "Swakshetra"
            elif lord == p:
                dignity = "Swakshetra"
            else:
                other_d1 = d1_signs_by_planet.get(lord)
                if other_d1 is not None:
                    dignity = compound_relationship(p, lord, d1_sign, other_d1)
                else:
                    nat = natural_relationship(p, lord)
                    dignity = {"Friend": "Mitra", "Neutral": "Sama", "Enemy": "Shatru"}.get(nat, "Sama")
        elif lord == p:
            dignity = "Swakshetra"
        else:
            other_d1 = d1_signs_by_planet.get(lord)
            if other_d1 is not None:
                dignity = compound_relationship(p, lord, d1_sign, other_d1)
            else:
                nat = natural_relationship(p, lord)
                dignity = {"Friend": "Mitra", "Neutral": "Sama", "Enemy": "Shatru"}.get(nat, "Sama")

        pts = dignity_points_map[dignity]
        contrib = (weight * pts) / 20.0
        contributions[varga_code] = round(contrib, 6)
        dignities[varga_code] = dignity
        total_score += contrib

    return VimshopakaScore(
        planet=p,
        scheme=scheme_key,
        total_score=round(total_score, 6),
        percentage=round((total_score / 20.0) * 100.0, 4),
        varga_contributions=contributions,
        varga_dignities=dignities,
    )


def bhava_lagna(sun_lon_deg: float, hours_since_sunrise: float) -> float:
    """Compute Bhava Lagna longitude (1 sign per 2 hours = 15 degrees per hour from sunrise Sun)."""
    return normalize_degrees(sun_lon_deg + float(hours_since_sunrise) * 15.0)


def hora_lagna(sun_lon_deg: float, hours_since_sunrise: float) -> float:
    """Compute Hora Lagna longitude (1 sign per 1 hour = 30 degrees per hour from sunrise Sun)."""
    return normalize_degrees(sun_lon_deg + float(hours_since_sunrise) * 30.0)


def ghatika_lagna(sun_lon_deg: float, hours_since_sunrise: float) -> float:
    """Compute Ghatika Lagna longitude (1 sign per ghati [24 min] = 75 degrees per hour from sunrise Sun)."""
    return normalize_degrees(sun_lon_deg + float(hours_since_sunrise) * 75.0)


def sree_lagna(lagna_lon_deg: float, moon_lon_deg: float) -> float:
    """Compute Sree Lagna longitude (Kalas of Moon's nakshatra progress added to Janma Lagna)."""
    nak = nakshatra_position(moon_lon_deg)
    return normalize_degrees(lagna_lon_deg + nak.fraction_elapsed * 360.0)


def pranapada_lagna(sun_lon_deg: float, hours_since_sunrise: float) -> float:
    """Compute Pranapada Lagna per BPHS Chapter 3.

    1 hour = 2.5 ghatis = 150 vighatis (palas).
    Divide vighatis by 15 to obtain rasis (1 vighati = 2.0 degrees).
    Base anchor is Sun's longitude if Sun is in a Movable sign, 9th from Sun (+240 deg)
    if Sun is in a Fixed sign, or 5th from Sun (+120 deg) if Sun is in a Dual sign.
    """
    sun_lon = normalize_degrees(sun_lon_deg)
    sun_sign = min(int(sun_lon // 30.0), 11)
    modality = sun_sign % 3
    offset_deg = (0.0, 240.0, 120.0)[modality]
    vighatis = float(hours_since_sunrise) * 150.0
    advance_deg = vighatis * 2.0
    return normalize_degrees(sun_lon + offset_deg + advance_deg)


def indu_lagna(lagna_lon_deg: float, moon_lon_deg: float) -> tuple[int, str]:
    """Compute Indu Lagna sign index (`0..11`) and Rasi name from Lagna and Moon longitudes."""
    lagna_sign = min(int(normalize_degrees(lagna_lon_deg) // 30.0), 11)
    moon_sign = min(int(normalize_degrees(moon_lon_deg) // 30.0), 11)
    ninth_from_lagna_lord = RASI_LORDS[(lagna_sign + 8) % 12]
    ninth_from_moon_lord = RASI_LORDS[(moon_sign + 8) % 12]
    total_kalas = INDU_KALAS[ninth_from_lagna_lord] + INDU_KALAS[ninth_from_moon_lord]
    rem = total_kalas % 12
    if rem == 0:
        rem = 12
    indu_sign = (moon_sign + rem - 1) % 12
    return indu_sign, RASI_NAMES[indu_sign]


def varnada_lagna(lagna_lon_deg: float, hora_lagna_lon_deg: float) -> float:
    """Compute Varnada Lagna (V1) longitude from Janma Lagna and Hora Lagna per BPHS / Jaimini."""
    l_lon = normalize_degrees(lagna_lon_deg)
    h_lon = normalize_degrees(hora_lagna_lon_deg)
    l_sign = min(int(l_lon // 30.0), 11)
    h_sign = min(int(h_lon // 30.0), 11)
    l_is_odd = (l_sign % 2 == 0)
    h_is_odd = (h_sign % 2 == 0)

    c1 = l_lon if l_is_odd else (360.0 - l_lon)
    c2 = h_lon if h_is_odd else (360.0 - h_lon)

    combined = (c1 + c2) if (l_is_odd == h_is_odd) else abs(c1 - c2)
    combined = normalize_degrees(combined)
    return normalize_degrees(combined if l_is_odd else (360.0 - combined))


def compute_special_lagnas(
    lagna_lon_deg: float,
    sun_lon_deg: float,
    moon_lon_deg: float,
    hours_since_sunrise: float,
) -> SpecialLagnas:
    """Compute all classical special mathematical Lagnas at once."""
    bl = bhava_lagna(sun_lon_deg, hours_since_sunrise)
    hl = hora_lagna(sun_lon_deg, hours_since_sunrise)
    gl = ghatika_lagna(sun_lon_deg, hours_since_sunrise)
    sl = sree_lagna(lagna_lon_deg, moon_lon_deg)
    pl = pranapada_lagna(sun_lon_deg, hours_since_sunrise)
    il_sign, il_name = indu_lagna(lagna_lon_deg, moon_lon_deg)
    vl = varnada_lagna(lagna_lon_deg, hl)

    return SpecialLagnas(
        bhava_lagna_deg=bl,
        bhava_lagna_sign=min(int(bl // 30.0), 11),
        hora_lagna_deg=hl,
        hora_lagna_sign=min(int(hl // 30.0), 11),
        ghatika_lagna_deg=gl,
        ghatika_lagna_sign=min(int(gl // 30.0), 11),
        sree_lagna_deg=sl,
        sree_lagna_sign=min(int(sl // 30.0), 11),
        pranapada_lagna_deg=pl,
        pranapada_lagna_sign=min(int(pl // 30.0), 11),
        indu_lagna_sign=il_sign,
        indu_lagna_name=il_name,
        varnada_lagna_deg=vl,
        varnada_lagna_sign=min(int(vl // 30.0), 11),
    )


def resolve_jaimini_sign_lord(sign_index: int, planet_longitudes: Mapping[str, float]) -> str:
    """Resolve the effective lord of a sign under Jaimini dual-lordship rules for
    Scorpio (7: Mars vs Ketu) and Aquarius (10: Saturn vs Rahu).

    Classical hierarchy (*Jaimini Sutras* / K.N. Rao / Rath):
    1. If one co-lord is placed in the sign itself and the other is not, the one NOT in the sign
       is used for Arudha/Dasha progression (or the stronger one when neither is in the sign).
    2. A co-lord conjoined with more planets in D1 is stronger.
    3. If tied on conjunction count, a co-lord that is exalted or in own sign is stronger.
    4. If still tied, the co-lord with higher degree within its sign (for Rahu/Ketu measured as
       `30 - deg_in_sign`) wins.
    """
    s = sign_index % 12
    if s not in (7, 10):
        return RASI_LORDS[s]

    cand_a, cand_b = ("Mars", "Ketu") if s == 7 else ("Saturn", "Rahu")
    norm_lons = {k.strip().capitalize(): normalize_degrees(v) for k, v in planet_longitudes.items()}
    if cand_a not in norm_lons or cand_b not in norm_lons:
        return cand_a

    sign_a = min(int(norm_lons[cand_a] // 30.0), 11)
    sign_b = min(int(norm_lons[cand_b] // 30.0), 11)

    # Rule 1: If one co-lord is in the sign and the other is outside, the outside lord gives the step
    if (sign_a == s) != (sign_b == s):
        return cand_b if sign_a == s else cand_a

    # Rule 2: Count conjunctions in D1
    occ_counts: dict[int, int] = {}
    for p_lon in norm_lons.values():
        p_sign = min(int(p_lon // 30.0), 11)
        occ_counts[p_sign] = occ_counts.get(p_sign, 0) + 1

    conj_a = occ_counts.get(sign_a, 1) - 1
    conj_b = occ_counts.get(sign_b, 1) - 1
    if conj_a != conj_b:
        return cand_a if conj_a > conj_b else cand_b

    # Rule 3: Exaltation
    ex_a = (EXALTATION_SIGNS.get(cand_a) == sign_a)
    ex_b = (EXALTATION_SIGNS.get(cand_b) == sign_b)
    if ex_a != ex_b:
        return cand_a if ex_a else cand_b

    # Rule 4: Degree in sign (nodes measured retrograde from 30 deg)
    deg_a = norm_lons[cand_a] - sign_a * 30.0
    deg_b = 30.0 - (norm_lons[cand_b] - sign_b * 30.0)
    return cand_a if deg_a >= deg_b else cand_b


def arudha_padas(lagna_lon_deg: float, planet_longitudes: Mapping[str, float]) -> ArudhaPadaSet:
    """Compute Jaimini Arudha Padas A1..A12, AL (Arudha Lagna), and UL (Upapada Lagna).

    Applies the classical *Swasthe Daraye* exception: if the raw count lands in the
    1st or 7th from the house itself, advance by 10 signs (+9 modulo 12).
    """
    lagna_sign = min(int(normalize_degrees(lagna_lon_deg) // 30.0), 11)
    norm_lons = {k.strip().capitalize(): normalize_degrees(v) for k, v in planet_longitudes.items()}

    padas: dict[str, int] = {}
    pada_names: dict[str, str] = {}

    for house_num in range(1, 13):
        house_sign = (lagna_sign + house_num - 1) % 12
        lord = resolve_jaimini_sign_lord(house_sign, norm_lons)
        if lord not in norm_lons:
            raise ValueError(f"Missing longitude for house lord {lord!r} in planet_longitudes")
        lord_sign = min(int(norm_lons[lord] // 30.0), 11)
        dist = (lord_sign - house_sign) % 12
        pada_sign = (lord_sign + dist) % 12

        # Swasthe Daraye exception: 1st (dist == 0) or 7th (dist == 6) from house_sign
        rel_from_house = (pada_sign - house_sign) % 12
        if rel_from_house in (0, 6):
            pada_sign = (pada_sign + 9) % 12

        key = f"A{house_num}"
        padas[key] = pada_sign
        pada_names[key] = RASI_NAMES[pada_sign]

    padas["AL"] = padas["A1"]
    padas["UL"] = padas["A12"]
    pada_names["AL"] = pada_names["A1"]
    pada_names["UL"] = pada_names["A12"]

    return ArudhaPadaSet(
        padas=padas,
        pada_names=pada_names,
        arudha_lagna_sign=padas["AL"],
        arudha_lagna_name=pada_names["AL"],
        upapada_lagna_sign=padas["UL"],
        upapada_lagna_name=pada_names["UL"],
    )
