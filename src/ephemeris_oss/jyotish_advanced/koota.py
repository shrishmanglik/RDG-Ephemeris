"""Ashtakoota (36-Point Guna Milan), Dashakoota (10 Porutham), and Kuja Dosha engine.

Implements classical North-Indian 36-point Ashtakoota matching, South-Indian 10-point
Dashakoota (Dasa Porutham) matching with Rajju and Vedha checks, and multi-reference
Kuja Dosha (Manglik) evaluation from Lagna, Moon, and Venus with classical cancellation
rules, derived from *Muhurta Chintamani*, *Brihat Parashara Hora Shastra*, and
*Kalaprakasika*.
"""

from __future__ import annotations

from dataclasses import dataclass
import math
from typing import Mapping, Sequence

from ..engine.receipt import canonical_hash
from .kp import NAKSHATRA_NAMES, RASI_LORDS, RASI_NAMES
from .varshphal import NAISARGIKA_ENEMIES, NAISARGIKA_FRIENDS

# Varna ranks by Rasi index 0..11: Brahmin=4, Kshatriya=3, Vaishya=2, Shudra=1.
RASI_VARNA_NAME: tuple[str, ...] = (
    "Kshatriya",  # 0 Mesha
    "Vaishya",    # 1 Vrishabha
    "Shudra",     # 2 Mithuna
    "Brahmin",    # 3 Karka
    "Kshatriya",  # 4 Simha
    "Vaishya",    # 5 Kanya
    "Shudra",     # 6 Tula
    "Brahmin",    # 7 Vrischika
    "Kshatriya",  # 8 Dhanus
    "Vaishya",    # 9 Makara
    "Shudra",     # 10 Kumbha
    "Brahmin",    # 11 Meena
)

VARNA_RANK: Mapping[str, int] = {
    "Shudra": 1,
    "Vaishya": 2,
    "Kshatriya": 3,
    "Brahmin": 4,
}

# 5 Vashya categories and 5x5 compatibility score matrix (max 2.0 points).
# Order: (bride_vashya, groom_vashya) -> score
VASHYA_MATRIX: Mapping[tuple[str, str], float] = {
    ("Chatushpada", "Chatushpada"): 2.0,
    ("Chatushpada", "Manava"): 1.0,
    ("Chatushpada", "Jalachara"): 1.0,
    ("Chatushpada", "Vanachara"): 0.0,
    ("Chatushpada", "Keeta"): 1.0,
    ("Manava", "Chatushpada"): 1.0,
    ("Manava", "Manava"): 2.0,
    ("Manava", "Jalachara"): 0.5,
    ("Manava", "Vanachara"): 0.0,
    ("Manava", "Keeta"): 1.0,
    ("Jalachara", "Chatushpada"): 1.0,
    ("Jalachara", "Manava"): 0.5,
    ("Jalachara", "Jalachara"): 2.0,
    ("Jalachara", "Vanachara"): 1.0,
    ("Jalachara", "Keeta"): 1.0,
    ("Vanachara", "Chatushpada"): 0.0,
    ("Vanachara", "Manava"): 0.0,
    ("Vanachara", "Jalachara"): 1.0,
    ("Vanachara", "Vanachara"): 2.0,
    ("Vanachara", "Keeta"): 0.0,
    ("Keeta", "Chatushpada"): 1.0,
    ("Keeta", "Manava"): 1.0,
    ("Keeta", "Jalachara"): 1.0,
    ("Keeta", "Vanachara"): 0.0,
    ("Keeta", "Keeta"): 2.0,
}

# 14 Yoni animals in canonical order 0..13:
YONI_NAMES: tuple[str, ...] = (
    "Horse",     # 0 Ashwa
    "Elephant",  # 1 Gaja
    "Goat",      # 2 Mesha/Chhaga
    "Serpent",   # 3 Sarpa
    "Dog",       # 4 Shwana
    "Cat",       # 5 Marjara
    "Rat",       # 6 Mushaka
    "Cow",       # 7 Gau
    "Buffalo",   # 8 Mahisha
    "Tiger",     # 9 Vyaghra
    "Deer",      # 10 Mriga
    "Monkey",    # 11 Vanara
    "Mongoose",  # 12 Nakula
    "Lion",      # 13 Simha
)

# Mapping of 27 Nakshatras (0..26) to Yoni index (0..13).
NAKSHATRA_YONI_INDEX: tuple[int, ...] = (
    0,   # 0 Ashwini -> Horse
    1,   # 1 Bharani -> Elephant
    2,   # 2 Krittika -> Goat
    3,   # 3 Rohini -> Serpent
    3,   # 4 Mrigashira -> Serpent
    4,   # 5 Ardra -> Dog
    5,   # 6 Punarvasu -> Cat
    2,   # 7 Pushya -> Goat
    5,   # 8 Ashlesha -> Cat
    6,   # 9 Magha -> Rat
    6,   # 10 Purva Phalguni -> Rat
    7,   # 11 Uttara Phalguni -> Cow
    8,   # 12 Hasta -> Buffalo
    9,   # 13 Chitra -> Tiger
    8,   # 14 Swati -> Buffalo
    9,   # 15 Vishakha -> Tiger
    10,  # 16 Anuradha -> Deer
    10,  # 17 Jyeshtha -> Deer
    4,   # 18 Mula -> Dog
    11,  # 19 Purva Ashadha -> Monkey
    12,  # 20 Uttara Ashadha -> Mongoose
    11,  # 21 Shravana -> Monkey
    13,  # 22 Dhanishta -> Lion
    0,   # 23 Shatabhisha -> Horse
    13,  # 24 Purva Bhadrapada -> Lion
    7,   # 25 Uttara Bhadrapada -> Cow
    1,   # 26 Revati -> Elephant
)

# Canonical 14x14 Yoni compatibility matrix (0..4 points) per Muhurta Chintamani.
# Sworn enemies (0 pts): (Horse, Buffalo), (Elephant, Lion), (Goat, Monkey),
# (Serpent, Mongoose), (Dog, Deer), (Cat, Rat), (Cow, Tiger).
YONI_SCORE_MATRIX: tuple[tuple[int, ...], ...] = (
    # H  El Go Se Do Ca Ra Co Bu Ti De Mo Mg Li
    (4, 2, 2, 3, 2, 2, 2, 1, 0, 1, 3, 3, 2, 1),  # 0 Horse
    (2, 4, 3, 3, 2, 2, 2, 2, 3, 1, 2, 3, 2, 0),  # 1 Elephant
    (2, 3, 4, 2, 1, 2, 1, 3, 3, 1, 2, 0, 3, 1),  # 2 Goat
    (3, 3, 2, 4, 2, 1, 1, 1, 1, 2, 2, 2, 0, 2),  # 3 Serpent
    (2, 2, 1, 2, 4, 2, 1, 2, 2, 1, 0, 2, 1, 1),  # 4 Dog
    (2, 2, 2, 1, 2, 4, 0, 2, 2, 1, 3, 3, 2, 1),  # 5 Cat
    (2, 2, 1, 1, 1, 0, 4, 2, 2, 2, 2, 2, 1, 2),  # 6 Rat
    (1, 2, 3, 1, 2, 2, 2, 4, 3, 0, 3, 2, 2, 1),  # 7 Cow
    (0, 3, 3, 1, 2, 2, 2, 3, 4, 1, 2, 2, 2, 1),  # 8 Buffalo
    (1, 1, 1, 2, 1, 1, 2, 0, 1, 4, 1, 1, 2, 1),  # 9 Tiger
    (3, 2, 2, 2, 0, 3, 2, 3, 2, 1, 4, 2, 2, 1),  # 10 Deer
    (3, 3, 0, 2, 2, 3, 2, 2, 2, 1, 2, 4, 3, 2),  # 11 Monkey
    (2, 2, 3, 0, 1, 2, 1, 2, 2, 2, 2, 3, 4, 2),  # 12 Mongoose
    (1, 0, 1, 2, 1, 1, 2, 1, 1, 1, 1, 2, 2, 4),  # 13 Lion
)

# Gana for each of the 27 Nakshatras: Deva, Manushya, Rakshasa.
NAKSHATRA_GANA: tuple[str, ...] = (
    "Deva",      # 0 Ashwini
    "Manushya",  # 1 Bharani
    "Rakshasa",  # 2 Krittika
    "Manushya",  # 3 Rohini
    "Deva",      # 4 Mrigashira
    "Manushya",  # 5 Ardra
    "Deva",      # 6 Punarvasu
    "Deva",      # 7 Pushya
    "Rakshasa",  # 8 Ashlesha
    "Rakshasa",  # 9 Magha
    "Manushya",  # 10 Purva Phalguni
    "Manushya",  # 11 Uttara Phalguni
    "Deva",      # 12 Hasta
    "Rakshasa",  # 13 Chitra
    "Deva",      # 14 Swati
    "Rakshasa",  # 15 Vishakha
    "Deva",      # 16 Anuradha
    "Rakshasa",  # 17 Jyeshtha
    "Rakshasa",  # 18 Mula
    "Manushya",  # 19 Purva Ashadha
    "Manushya",  # 20 Uttara Ashadha
    "Deva",      # 21 Shravana
    "Rakshasa",  # 22 Dhanishta
    "Rakshasa",  # 23 Shatabhisha
    "Manushya",  # 24 Purva Bhadrapada
    "Manushya",  # 25 Uttara Bhadrapada
    "Deva",      # 26 Revati
)

# Nadi for each of the 27 Nakshatras: Adi, Madhya, Antya (snake-wave pattern).
NAKSHATRA_NADI: tuple[str, ...] = (
    "Adi",     # 0 Ashwini
    "Madhya",  # 1 Bharani
    "Antya",   # 2 Krittika
    "Antya",   # 3 Rohini
    "Madhya",  # 4 Mrigashira
    "Adi",     # 5 Ardra
    "Adi",     # 6 Punarvasu
    "Madhya",  # 7 Pushya
    "Antya",   # 8 Ashlesha
    "Antya",   # 9 Magha
    "Madhya",  # 10 Purva Phalguni
    "Adi",     # 11 Uttara Phalguni
    "Adi",     # 12 Hasta
    "Madhya",  # 13 Chitra
    "Antya",   # 14 Swati
    "Antya",   # 15 Vishakha
    "Madhya",  # 16 Anuradha
    "Adi",     # 17 Jyeshtha
    "Adi",     # 18 Mula
    "Madhya",  # 19 Purva Ashadha
    "Antya",   # 20 Uttara Ashadha
    "Antya",   # 21 Shravana
    "Madhya",  # 22 Dhanishta
    "Adi",     # 23 Shatabhisha
    "Adi",     # 24 Purva Bhadrapada
    "Madhya",  # 25 Uttara Bhadrapada
    "Antya",   # 26 Revati
)

# Rajju (body segment + Arohana/Avarohana direction) for each of the 27 Nakshatras.
# Cycle of 9 repeats 3 times:
# 0: Pada (Arohana), 1: Kati (Arohana), 2: Udara (Arohana), 3: Kantha (Arohana),
# 4: Siro (Apex), 5: Kantha (Avarohana), 6: Udara (Avarohana), 7: Kati (Avarohana), 8: Pada (Avarohana).
_RAJJU_CYCLE_9: tuple[tuple[str, str], ...] = (
    ("Pada", "Arohana"),
    ("Kati", "Arohana"),
    ("Udara", "Arohana"),
    ("Kantha", "Arohana"),
    ("Siro", "Apex"),
    ("Kantha", "Avarohana"),
    ("Udara", "Avarohana"),
    ("Kati", "Avarohana"),
    ("Pada", "Avarohana"),
)

# Hostile Vedha pairs of Nakshatra indices (0..26).
VEDHA_PAIRS: frozenset[frozenset[int]] = frozenset(
    {
        frozenset({0, 17}),   # Ashwini - Jyeshtha
        frozenset({1, 16}),   # Bharani - Anuradha
        frozenset({2, 15}),   # Krittika - Vishakha
        frozenset({3, 14}),   # Rohini - Swati
        frozenset({5, 21}),   # Ardra - Shravana
        frozenset({6, 20}),   # Punarvasu - Uttara Ashadha
        frozenset({7, 19}),   # Pushya - Purva Ashadha
        frozenset({8, 18}),   # Ashlesha - Mula
        frozenset({9, 26}),   # Magha - Revati
        frozenset({10, 25}),  # Purva Phalguni - Uttara Bhadrapada
        frozenset({11, 24}),  # Uttara Phalguni - Purva Bhadrapada
        frozenset({12, 23}),  # Hasta - Shatabhisha
        # Tri-Vedha group: Mrigashira (4), Chitra (13), Dhanishta (22)
        frozenset({4, 13}),
        frozenset({4, 22}),
        frozenset({13, 22}),
    }
)


@dataclass(frozen=True)
class KootaScoreItem:
    """One Koota criterion result in Ashtakoota matching."""

    name: str
    max_points: float
    raw_points: float
    effective_points: float
    bride_attribute: str
    groom_attribute: str
    dosha_present: bool
    dosha_cancelled: bool
    cancellation_reason: str | None


@dataclass(frozen=True)
class AshtakootaReport:
    """Complete 36-point Ashtakoota Guna Milan compatibility report."""

    bride_moon_lon_deg: float
    groom_moon_lon_deg: float
    bride_rasi_index: int
    groom_rasi_index: int
    bride_nakshatra_index: int
    groom_nakshatra_index: int
    bride_pada: int
    groom_pada: int
    items: tuple[KootaScoreItem, ...]
    total_raw_points: float
    total_effective_points: float
    max_points: float
    verdict_tier: str
    receipt_sha256: str


@dataclass(frozen=True)
class PoruthamItem:
    """One Porutham result in South-Indian 10-point Dashakoota matching."""

    name: str
    passed: bool
    score: float
    detail: str


@dataclass(frozen=True)
class DashakootaReport:
    """Complete 10-point South-Indian Dashakoota (Dasa Porutham) report."""

    poruthams: tuple[PoruthamItem, ...]
    passed_count: int
    total_score: float
    max_score: float
    rajju_dosha: bool
    vedha_dosha: bool
    recommended: bool
    receipt_sha256: str


@dataclass(frozen=True)
class KujaDoshaReport:
    """Single-chart Kuja Dosha (Manglik) evaluation from Lagna, Moon, and Venus."""

    mars_house_from_lagna: int
    mars_house_from_moon: int
    mars_house_from_venus: int
    dosha_from_lagna: bool
    dosha_from_moon: bool
    dosha_from_venus: bool
    raw_severity_score: float
    is_manglik_raw: bool
    is_cancelled: bool
    cancellation_reasons: tuple[str, ...]
    effective_manglik: bool
    receipt_sha256: str


@dataclass(frozen=True)
class MutualKujaCompatibility:
    """Synastry Kuja Dosha comparison and mutual cancellation evaluation."""

    bride_report: KujaDoshaReport
    groom_report: KujaDoshaReport
    mutually_compatible: bool
    reason: str
    receipt_sha256: str


def _norm360(lon_deg: float) -> float:
    val = float(lon_deg)
    if not math.isfinite(val):
        raise ValueError("longitude must be finite")
    return val % 360.0


def _vashya_category(lon_deg: float) -> str:
    lon = _norm360(lon_deg)
    rasi = int(lon // 30.0)
    deg = lon - rasi * 30.0
    if rasi in {0, 1}:
        return "Chatushpada"
    if rasi in {2, 5, 6, 10}:
        return "Manava"
    if rasi in {3, 11}:
        return "Jalachara"
    if rasi == 4:
        return "Vanachara"
    if rasi == 7:
        return "Keeta"
    if rasi == 8:
        return "Manava" if deg < 15.0 else "Chatushpada"
    # rasi == 9 (Capricorn): first half quadruped, second half water
    return "Chatushpada" if deg < 15.0 else "Jalachara"


def _graha_maitri_points(bride_lord: str, groom_lord: str) -> tuple[float, bool]:
    """Return (points_out_of_5, are_friendly_or_same) for two Rasi lords."""

    if bride_lord == groom_lord:
        return 5.0, True

    def rel(a: str, b: str) -> int:
        if b in NAISARGIKA_FRIENDS[a]:
            return 1
        if b in NAISARGIKA_ENEMIES[a]:
            return -1
        return 0

    r_bg = rel(bride_lord, groom_lord)
    r_gb = rel(groom_lord, bride_lord)
    pair = tuple(sorted((r_bg, r_gb)))

    if pair == (1, 1):
        return 5.0, True
    if pair == (0, 1):
        return 4.0, True
    if pair == (0, 0):
        return 3.0, False
    if pair == (-1, 1):
        return 1.0, False
    if pair == (-1, 0):
        return 0.5, False
    return 0.0, False


def evaluate_ashtakoota(
    bride_moon_lon_deg: float,
    groom_moon_lon_deg: float,
) -> AshtakootaReport:
    """Evaluate the classical 36-point Ashtakoota Guna Milan compatibility."""

    b_lon = _norm360(bride_moon_lon_deg)
    g_lon = _norm360(groom_moon_lon_deg)

    b_rasi = int(b_lon // 30.0)
    g_rasi = int(g_lon // 30.0)

    nak_span = 40.0 / 3.0
    b_nak = min(int(b_lon // nak_span), 26)
    g_nak = min(int(g_lon // nak_span), 26)

    b_pada = min(int((b_lon - b_nak * nak_span) // (10.0 / 3.0)) + 1, 4)
    g_pada = min(int((g_lon - g_nak * nak_span) // (10.0 / 3.0)) + 1, 4)

    items: list[KootaScoreItem] = []

    # 1. Varna (1 point)
    b_varna = RASI_VARNA_NAME[b_rasi]
    g_varna = RASI_VARNA_NAME[g_rasi]
    varna_pts = 1.0 if VARNA_RANK[g_varna] >= VARNA_RANK[b_varna] else 0.0
    items.append(
        KootaScoreItem(
            name="varna",
            max_points=1.0,
            raw_points=varna_pts,
            effective_points=varna_pts,
            bride_attribute=b_varna,
            groom_attribute=g_varna,
            dosha_present=varna_pts == 0.0,
            dosha_cancelled=False,
            cancellation_reason=None,
        )
    )

    # 2. Vashya (2 points)
    b_vashya = _vashya_category(b_lon)
    g_vashya = _vashya_category(g_lon)
    vashya_pts = VASHYA_MATRIX[(b_vashya, g_vashya)]
    items.append(
        KootaScoreItem(
            name="vashya",
            max_points=2.0,
            raw_points=vashya_pts,
            effective_points=vashya_pts,
            bride_attribute=b_vashya,
            groom_attribute=g_vashya,
            dosha_present=vashya_pts == 0.0,
            dosha_cancelled=False,
            cancellation_reason=None,
        )
    )

    # 3. Tara (3 points)
    count_bg = ((g_nak - b_nak) % 27) + 1
    count_gb = ((b_nak - g_nak) % 27) + 1
    rem_bg = count_bg % 9
    rem_gb = count_gb % 9
    ausp_bg = rem_bg not in {3, 5, 7}
    ausp_gb = rem_gb not in {3, 5, 7}
    tara_pts = (1.5 if ausp_bg else 0.0) + (1.5 if ausp_gb else 0.0)
    items.append(
        KootaScoreItem(
            name="tara",
            max_points=3.0,
            raw_points=tara_pts,
            effective_points=tara_pts,
            bride_attribute=f"Tara-{rem_bg or 9}",
            groom_attribute=f"Tara-{rem_gb or 9}",
            dosha_present=tara_pts < 1.5,
            dosha_cancelled=False,
            cancellation_reason=None,
        )
    )

    # 4. Yoni (4 points)
    b_yoni_idx = NAKSHATRA_YONI_INDEX[b_nak]
    g_yoni_idx = NAKSHATRA_YONI_INDEX[g_nak]
    yoni_pts = float(YONI_SCORE_MATRIX[b_yoni_idx][g_yoni_idx])
    items.append(
        KootaScoreItem(
            name="yoni",
            max_points=4.0,
            raw_points=yoni_pts,
            effective_points=yoni_pts,
            bride_attribute=YONI_NAMES[b_yoni_idx],
            groom_attribute=YONI_NAMES[g_yoni_idx],
            dosha_present=yoni_pts == 0.0,
            dosha_cancelled=False,
            cancellation_reason=None,
        )
    )

    # 5. Graha Maitri (5 points)
    b_lord = RASI_LORDS[b_rasi]
    g_lord = RASI_LORDS[g_rasi]
    maitri_pts, lords_harmonious = _graha_maitri_points(b_lord, g_lord)
    items.append(
        KootaScoreItem(
            name="graha_maitri",
            max_points=5.0,
            raw_points=maitri_pts,
            effective_points=maitri_pts,
            bride_attribute=b_lord,
            groom_attribute=g_lord,
            dosha_present=maitri_pts < 1.0,
            dosha_cancelled=False,
            cancellation_reason=None,
        )
    )

    # 6. Gana (6 points)
    b_gana = NAKSHATRA_GANA[b_nak]
    g_gana = NAKSHATRA_GANA[g_nak]
    if b_gana == g_gana:
        gana_pts = 6.0
    elif b_gana == "Manushya" and g_gana == "Deva":
        gana_pts = 6.0
    elif b_gana == "Deva" and g_gana == "Manushya":
        gana_pts = 5.0
    elif b_gana == "Deva" and g_gana == "Rakshasa":
        gana_pts = 1.0
    else:
        gana_pts = 0.0

    items.append(
        KootaScoreItem(
            name="gana",
            max_points=6.0,
            raw_points=gana_pts,
            effective_points=gana_pts,
            bride_attribute=b_gana,
            groom_attribute=g_gana,
            dosha_present=gana_pts == 0.0,
            dosha_cancelled=False,
            cancellation_reason=None,
        )
    )

    # 7. Bhakoot (7 points)
    rasi_dist = ((g_rasi - b_rasi) % 12) + 1
    if rasi_dist in {1, 3, 4, 7, 10, 11}:
        bhakoot_raw = 7.0
        bhakoot_dosha = False
        bhakoot_cancelled = False
        bhakoot_reason = None
    else:
        bhakoot_raw = 0.0
        bhakoot_dosha = True
        if b_lord == g_lord:
            bhakoot_cancelled = True
            bhakoot_reason = f"Both Moon signs share the same planetary lord ({b_lord})."
        elif lords_harmonious:
            bhakoot_cancelled = True
            bhakoot_reason = f"Moon sign lords ({b_lord}, {g_lord}) are in Naisargika friendship."
        else:
            bhakoot_cancelled = False
            bhakoot_reason = None

    bhakoot_eff = 7.0 if (bhakoot_raw == 7.0 or bhakoot_cancelled) else 0.0
    items.append(
        KootaScoreItem(
            name="bhakoot",
            max_points=7.0,
            raw_points=bhakoot_raw,
            effective_points=bhakoot_eff,
            bride_attribute=RASI_NAMES[b_rasi],
            groom_attribute=RASI_NAMES[g_rasi],
            dosha_present=bhakoot_dosha,
            dosha_cancelled=bhakoot_cancelled,
            cancellation_reason=bhakoot_reason,
        )
    )

    # 8. Nadi (8 points)
    b_nadi = NAKSHATRA_NADI[b_nak]
    g_nadi = NAKSHATRA_NADI[g_nak]
    if b_nadi != g_nadi:
        nadi_raw = 8.0
        nadi_dosha = False
        nadi_cancelled = False
        nadi_reason = None
    else:
        nadi_raw = 0.0
        nadi_dosha = True
        if b_rasi == g_rasi and b_nak != g_nak:
            nadi_cancelled = True
            nadi_reason = "Same Rasi but different Nakshatra cancels Nadi Dosha."
        elif b_nak == g_nak and b_rasi != g_rasi:
            nadi_cancelled = True
            nadi_reason = "Same Nakshatra spanning two different Rasis cancels Nadi Dosha."
        elif b_nak == g_nak and b_pada != g_pada:
            nadi_cancelled = True
            nadi_reason = "Same Nakshatra but different Pada (quarter) mitigates Nadi Dosha."
        else:
            nadi_cancelled = False
            nadi_reason = None

    nadi_eff = 8.0 if (nadi_raw == 8.0 or nadi_cancelled) else 0.0
    items.append(
        KootaScoreItem(
            name="nadi",
            max_points=8.0,
            raw_points=nadi_raw,
            effective_points=nadi_eff,
            bride_attribute=b_nadi,
            groom_attribute=g_nadi,
            dosha_present=nadi_dosha,
            dosha_cancelled=nadi_cancelled,
            cancellation_reason=nadi_reason,
        )
    )

    total_raw = sum(item.raw_points for item in items)
    total_eff = sum(item.effective_points for item in items)

    if total_eff >= 25.0:
        tier = "uttama"
    elif total_eff >= 18.0:
        tier = "madhyama"
    else:
        tier = "adhama"

    payload = {
        "bride_moon_lon_deg": round(b_lon, 8),
        "groom_moon_lon_deg": round(g_lon, 8),
        "total_raw_points": total_raw,
        "total_effective_points": total_eff,
    }
    return AshtakootaReport(
        bride_moon_lon_deg=b_lon,
        groom_moon_lon_deg=g_lon,
        bride_rasi_index=b_rasi,
        groom_rasi_index=g_rasi,
        bride_nakshatra_index=b_nak,
        groom_nakshatra_index=g_nak,
        bride_pada=b_pada,
        groom_pada=g_pada,
        items=tuple(items),
        total_raw_points=total_raw,
        total_effective_points=total_eff,
        max_points=36.0,
        verdict_tier=tier,
        receipt_sha256=canonical_hash(payload),
    )


def evaluate_dashakoota(
    bride_moon_lon_deg: float,
    groom_moon_lon_deg: float,
) -> DashakootaReport:
    """Evaluate the 10 South-Indian Poruthams (Dasa Porutham) per *Kalaprakasika*."""

    b_lon = _norm360(bride_moon_lon_deg)
    g_lon = _norm360(groom_moon_lon_deg)
    b_rasi = int(b_lon // 30.0)
    g_rasi = int(g_lon // 30.0)
    nak_span = 40.0 / 3.0
    b_nak = min(int(b_lon // nak_span), 26)
    g_nak = min(int(g_lon // nak_span), 26)

    nak_count = ((g_nak - b_nak) % 27) + 1
    rasi_count = ((g_rasi - b_rasi) % 12) + 1

    poruthams: list[PoruthamItem] = []

    # 1. Dina Porutham: count from Bride to Groom Nakshatra in {2, 4, 6, 8, 9, 11, 13, 15, 18, 20, 24, 26} or 27 (same rasi).
    dina_ok = (nak_count % 9) in {2, 4, 6, 8, 0} or (nak_count == 27 and b_rasi == g_rasi)
    poruthams.append(
        PoruthamItem("dina", dina_ok, 1.0 if dina_ok else 0.0, f"Nakshatra count={nak_count}")
    )

    # 2. Gana Porutham
    b_gana = NAKSHATRA_GANA[b_nak]
    g_gana = NAKSHATRA_GANA[g_nak]
    gana_ok = (b_gana == g_gana and b_gana != "Rakshasa") or (
        {b_gana, g_gana} == {"Deva", "Manushya"}
    )
    poruthams.append(
        PoruthamItem("gana", gana_ok, 1.0 if gana_ok else 0.0, f"{b_gana} vs {g_gana}")
    )

    # 3. Mahendra Porutham: count from Bride to Groom Nakshatra in {4, 7, 10, 13, 16, 19, 22, 25}
    mahendra_ok = nak_count in {4, 7, 10, 13, 16, 19, 22, 25}
    poruthams.append(
        PoruthamItem("mahendra", mahendra_ok, 1.0 if mahendra_ok else 0.0, f"count={nak_count}")
    )

    # 4. Stree Deergha Porutham: Groom Nakshatra > 13 constellations away from Bride (>= 14)
    stree_ok = nak_count >= 14
    poruthams.append(
        PoruthamItem("stree_deergha", stree_ok, 1.0 if stree_ok else 0.0, f"distance={nak_count}")
    )

    # 5. Yoni Porutham
    yoni_pts = YONI_SCORE_MATRIX[NAKSHATRA_YONI_INDEX[b_nak]][NAKSHATRA_YONI_INDEX[g_nak]]
    yoni_ok = yoni_pts >= 2
    poruthams.append(
        PoruthamItem("yoni", yoni_ok, 1.0 if yoni_ok else 0.0, f"yoni_score={yoni_pts}/4")
    )

    # 6. Rasi Porutham: count from Bride Rasi to Groom Rasi >= 7 (or 1, 3, 4, 7, 10, 11)
    rasi_ok = rasi_count in {1, 7, 9, 10, 11, 12} or rasi_count >= 7
    poruthams.append(
        PoruthamItem("rasi", rasi_ok, 1.0 if rasi_ok else 0.0, f"rasi_count={rasi_count}")
    )

    # 7. Rasiyathipathi Porutham: Moon sign lords friendly
    m_pts, m_ok = _graha_maitri_points(RASI_LORDS[b_rasi], RASI_LORDS[g_rasi])
    rasi_lord_ok = m_pts >= 3.0 or m_ok
    poruthams.append(
        PoruthamItem(
            "rasiyathipathi",
            rasi_lord_ok,
            1.0 if rasi_lord_ok else 0.0,
            f"{RASI_LORDS[b_rasi]} & {RASI_LORDS[g_rasi]}",
        )
    )

    # 8. Vasya Porutham
    v_pts = VASHYA_MATRIX[(_vashya_category(b_lon), _vashya_category(g_lon))]
    vasya_ok = v_pts >= 1.0
    poruthams.append(
        PoruthamItem("vasya", vasya_ok, 1.0 if vasya_ok else 0.0, f"vashya_pts={v_pts}")
    )

    # 9. Rajju Porutham (5 body parts: Pada, Kati, Udara, Kantha, Siro + Arohana/Avarohana)
    b_part, b_dir = _RAJJU_CYCLE_9[b_nak % 9]
    g_part, g_dir = _RAJJU_CYCLE_9[g_nak % 9]
    if b_part != g_part:
        rajju_ok = True
        rajju_dosha = False
    elif b_part != "Siro" and b_dir != g_dir:
        # Opposite direction (one Arohana, one Avarohana) outside Siro mitigates Rajju
        rajju_ok = True
        rajju_dosha = False
    else:
        rajju_ok = False
        rajju_dosha = True
    poruthams.append(
        PoruthamItem(
            "rajju",
            rajju_ok,
            1.0 if rajju_ok else 0.0,
            f"Bride={b_part}({b_dir}), Groom={g_part}({g_dir})",
        )
    )

    # 10. Vedha Porutham
    vedha_dosha = frozenset({b_nak, g_nak}) in VEDHA_PAIRS
    vedha_ok = not vedha_dosha
    poruthams.append(
        PoruthamItem(
            "vedha",
            vedha_ok,
            1.0 if vedha_ok else 0.0,
            "No Vedha affliction" if vedha_ok else f"Hostile Vedha pair ({NAKSHATRA_NAMES[b_nak]}, {NAKSHATRA_NAMES[g_nak]})",
        )
    )

    passed_count = sum(1 for p in poruthams if p.passed)
    total_score = sum(p.score for p in poruthams)
    recommended = passed_count >= 6 and dina_ok and gana_ok and rajju_ok and vedha_ok

    payload = {
        "bride_nak": b_nak,
        "groom_nak": g_nak,
        "passed_count": passed_count,
        "rajju_dosha": rajju_dosha,
        "vedha_dosha": vedha_dosha,
    }
    return DashakootaReport(
        poruthams=tuple(poruthams),
        passed_count=passed_count,
        total_score=total_score,
        max_score=10.0,
        rajju_dosha=rajju_dosha,
        vedha_dosha=vedha_dosha,
        recommended=recommended,
        receipt_sha256=canonical_hash(payload),
    )


MANGLIK_HOUSES: frozenset[int] = frozenset({1, 2, 4, 7, 8, 12})


def evaluate_kuja_dosha(
    mars_lon_deg: float,
    ascendant_lon_deg: float,
    moon_lon_deg: float,
    venus_lon_deg: float,
    *,
    jupiter_lon_deg: float | None = None,
    saturn_lon_deg: float | None = None,
) -> KujaDoshaReport:
    """Evaluate Kuja Dosha (Manglik) from Lagna, Moon, and Venus with classical cancellations."""

    m_sign = int(_norm360(mars_lon_deg) // 30.0)
    asc_sign = int(_norm360(ascendant_lon_deg) // 30.0)
    moon_sign = int(_norm360(moon_lon_deg) // 30.0)
    ven_sign = int(_norm360(venus_lon_deg) // 30.0)

    h_lagna = ((m_sign - asc_sign) % 12) + 1
    h_moon = ((m_sign - moon_sign) % 12) + 1
    h_venus = ((m_sign - ven_sign) % 12) + 1

    d_lagna = h_lagna in MANGLIK_HOUSES
    d_moon = h_moon in MANGLIK_HOUSES
    d_venus = h_venus in MANGLIK_HOUSES

    raw_score = (1.0 if d_lagna else 0.0) + (0.5 if d_moon else 0.0) + (0.25 if d_venus else 0.0)
    is_raw = d_lagna or d_moon or d_venus

    reasons: list[str] = []
    if is_raw:
        # 1. Mars in Own Sign (Aries=0, Scorpio=7) or Exaltation (Capricorn=9) or Debilitation (Cancer=3) per BPHS/Muhurta Chintamani
        if m_sign in {0, 7}:
            reasons.append("Mars occupies its own Rasi (Mesha or Vrischika).")
        if m_sign == 9:
            reasons.append("Mars is exalted in Makara (Capricorn).")
        if m_sign in {4, 10}:
            reasons.append("Mars occupies Simha (Leo) or Kumbha (Aquarius).")

        # 2. Specific house-sign exceptions from Muhurta Chintamani:
        if h_lagna == 2 and m_sign in {2, 5}:
            reasons.append("Mars in 2nd house in Mithuna or Kanya is exempt from Kuja Dosha.")
        if h_lagna == 12 and m_sign in {1, 6}:
            reasons.append("Mars in 12th house in Vrishabha or Tula is exempt from Kuja Dosha.")
        if h_lagna == 4 and m_sign in {0, 7}:
            reasons.append("Mars in 4th house in Mesha or Vrischika is exempt from Kuja Dosha.")
        if h_lagna == 7 and m_sign in {3, 9}:
            reasons.append("Mars in 7th house in Karka or Makara is exempt from Kuja Dosha.")
        if h_lagna == 8 and m_sign in {8, 11}:
            reasons.append("Mars in 8th house in Dhanus or Meena is exempt from Kuja Dosha.")

        # 3. Benefic aspect or conjunction from Jupiter or Moon
        if m_sign == moon_sign:
            reasons.append("Mars is conjoined with the Moon (Chandra-Mangala cancellation).")
        if jupiter_lon_deg is not None:
            j_sign = int(_norm360(jupiter_lon_deg) // 30.0)
            j_dist = ((m_sign - j_sign) % 12) + 1
            if j_dist in {1, 5, 7, 9}:
                reasons.append("Mars is conjoined with or aspected by Jupiter.")
        if saturn_lon_deg is not None:
            s_sign = int(_norm360(saturn_lon_deg) // 30.0)
            if s_sign == m_sign:
                reasons.append("Mars is conjoined with Saturn, counterbalancing Kuja Dosha.")

    cancelled = is_raw and len(reasons) > 0
    effective = is_raw and not cancelled

    payload = {
        "h_lagna": h_lagna,
        "h_moon": h_moon,
        "h_venus": h_venus,
        "raw_score": raw_score,
        "cancelled": cancelled,
        "effective": effective,
    }
    return KujaDoshaReport(
        mars_house_from_lagna=h_lagna,
        mars_house_from_moon=h_moon,
        mars_house_from_venus=h_venus,
        dosha_from_lagna=d_lagna,
        dosha_from_moon=d_moon,
        dosha_from_venus=d_venus,
        raw_severity_score=raw_score,
        is_manglik_raw=is_raw,
        is_cancelled=cancelled,
        cancellation_reasons=tuple(reasons),
        effective_manglik=effective,
        receipt_sha256=canonical_hash(payload),
    )


def evaluate_mutual_kuja_dosha(
    bride_report: KujaDoshaReport,
    groom_report: KujaDoshaReport,
) -> MutualKujaCompatibility:
    """Evaluate mutual Kuja Dosha compatibility between two charts."""

    if not bride_report.effective_manglik and not groom_report.effective_manglik:
        compatible = True
        reason = "Neither chart carries uncancelled Kuja Dosha."
    elif bride_report.effective_manglik and groom_report.effective_manglik:
        compatible = True
        reason = "Mutual Kuja Dosha present in both charts cancels out."
    elif bride_report.is_manglik_raw and groom_report.is_manglik_raw:
        compatible = True
        reason = "Both charts share raw Manglik placements with individual mitigations."
    else:
        compatible = False
        reason = "Asymmetric uncancelled Kuja Dosha between the two charts."

    payload = {
        "bride_receipt": bride_report.receipt_sha256,
        "groom_receipt": groom_report.receipt_sha256,
        "compatible": compatible,
    }
    return MutualKujaCompatibility(
        bride_report=bride_report,
        groom_report=groom_report,
        mutually_compatible=compatible,
        reason=reason,
        receipt_sha256=canonical_hash(payload),
    )
