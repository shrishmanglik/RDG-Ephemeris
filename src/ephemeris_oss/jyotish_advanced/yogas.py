"""Deterministic Classical Parashari Yoga Evaluator (70 Named Classical Yogas).

Evaluates 70 canonical planetary combinations from *Brihat Parashara Hora Shastra*,
*Phaladeepika* (Mantreswara), *Jataka Parijata* (Vaidyanatha Dikshita), and *Saravali*
(Kalyana Varma), covering Pancha Mahapurusha, Solar, Lunar, Raja, Dhana, Parivartana,
Vipareeta Raja, Neecha Bhanga Raja (all 5 cancellation conditions), Special Benefic,
and all 32 Nabhasa (Ashraya, Dala, Akriti, Sankhya) Yogas.
"""

from __future__ import annotations

from dataclasses import dataclass
import math
from typing import Mapping

from ..engine.receipt import canonical_hash
from .kp import RASI_LORDS, RASI_NAMES
from .varshphal import DEBILITATION_SIGN, EXALTATION_SIGN, NAISARGIKA_FRIENDS, OWN_SIGNS, SEVEN_PLANETS

# Planet that is exalted in a given Rasi (0..11), if any.
SIGN_EXALTATION_LORD: Mapping[int, str] = {
    0: "sun",
    1: "moon",
    3: "jupiter",
    5: "mercury",
    6: "saturn",
    9: "mars",
    11: "venus",
}

NATURAL_BENEFICS: frozenset[str] = frozenset({"jupiter", "venus", "mercury", "moon"})
NATURAL_MALEFICS: frozenset[str] = frozenset({"sun", "mars", "saturn"})
KENDRA_HOUSES: frozenset[int] = frozenset({1, 4, 7, 10})
TRIKONA_HOUSES: frozenset[int] = frozenset({1, 5, 9})
PANAPARA_HOUSES: frozenset[int] = frozenset({2, 5, 8, 11})
APOKLIMA_HOUSES: frozenset[int] = frozenset({3, 6, 9, 12})
DUSTHANA_HOUSES: frozenset[int] = frozenset({6, 8, 12})


@dataclass(frozen=True)
class ClassicalYogaFinding:
    """One deterministically evaluated classical Parashari Yoga."""

    code: str
    name: str
    category: str
    active: bool
    involved_planets: tuple[str, ...]
    involved_houses: tuple[int, ...]
    strength_score: float
    citation: str
    summary: str


@dataclass(frozen=True)
class ClassicalYogaReport:
    """Complete evaluation report across all 70 classical Parashari Yogas."""

    ascendant_lon_deg: float
    ascendant_rasi_index: int
    yogas: tuple[ClassicalYogaFinding, ...]
    active_yogas: tuple[ClassicalYogaFinding, ...]
    by_code: Mapping[str, ClassicalYogaFinding]
    receipt_sha256: str


def _norm360(lon_deg: float) -> float:
    val = float(lon_deg)
    if not math.isfinite(val):
        raise ValueError("longitude must be finite")
    return val % 360.0


def _parashari_aspects_sign(planet: str, from_sign: int, target_sign: int) -> bool:
    """Return True if ``planet`` at ``from_sign`` casts a full Parashari aspect on ``target_sign``."""

    dist = ((target_sign - from_sign) % 12) + 1
    if dist in {1, 7}:
        return True
    if planet == "mars" and dist in {4, 8}:
        return True
    if planet == "jupiter" and dist in {5, 9}:
        return True
    if planet == "saturn" and dist in {3, 10}:
        return True
    return False


def _planets_connected(
    p1: str,
    p2: str,
    signs: Mapping[str, int],
) -> bool:
    """Return True if two planets are conjoined, in mutual aspect, or in sign exchange."""

    if p1 == p2:
        return True
    s1 = signs[p1]
    s2 = signs[p2]
    if s1 == s2:
        return True
    if _parashari_aspects_sign(p1, s1, s2) and _parashari_aspects_sign(p2, s2, s1):
        return True
    if RASI_LORDS[s1] == p2 and RASI_LORDS[s2] == p1:
        return True
    return False


def _is_dignified(planet: str, sign_idx: int) -> bool:
    return sign_idx == EXALTATION_SIGN[planet] or sign_idx in OWN_SIGNS[planet]


def _planet_strength_score(planet: str, sign_idx: int, house: int) -> float:
    if sign_idx == EXALTATION_SIGN[planet]:
        base = 0.95
    elif sign_idx in OWN_SIGNS[planet]:
        base = 0.85
    elif RASI_LORDS[sign_idx] in NAISARGIKA_FRIENDS[planet]:
        base = 0.75
    elif sign_idx == DEBILITATION_SIGN[planet]:
        base = 0.35
    else:
        base = 0.65

    if house in KENDRA_HOUSES or house in TRIKONA_HOUSES:
        base = min(1.0, base + 0.05)
    elif house in DUSTHANA_HOUSES:
        base = max(0.2, base - 0.1)
    return round(base, 4)


def evaluate_classical_yogas(
    planet_lons: Mapping[str, float],
    ascendant_lon_deg: float,
) -> ClassicalYogaReport:
    """Evaluate 70 classical Parashari Yogas deterministically."""

    asc_lon = _norm360(ascendant_lon_deg)
    asc_sign = int(asc_lon // 30.0)

    signs: dict[str, int] = {}
    houses: dict[str, int] = {}
    for body in SEVEN_PLANETS:
        if body not in planet_lons:
            raise ValueError(f"missing required planet {body!r} in planet_lons")
        lon = _norm360(planet_lons[body])
        s_idx = int(lon // 30.0)
        signs[body] = s_idx
        houses[body] = ((s_idx - asc_sign) % 12) + 1

    moon_sign = signs["moon"]
    sun_sign = signs["sun"]

    def house_from_moon(body: str) -> int:
        return ((signs[body] - moon_sign) % 12) + 1

    def house_from_sun(body: str) -> int:
        return ((signs[body] - sun_sign) % 12) + 1

    def house_lord(house_num: int) -> str:
        return RASI_LORDS[(asc_sign + house_num - 1) % 12]

    findings: list[ClassicalYogaFinding] = []

    def add(
        code: str,
        name: str,
        category: str,
        active: bool,
        planets: tuple[str, ...],
        inv_houses: tuple[int, ...],
        strength: float,
        citation: str,
        summary: str,
    ) -> None:
        findings.append(
            ClassicalYogaFinding(
                code=code,
                name=name,
                category=category,
                active=active,
                involved_planets=planets if active else (),
                involved_houses=inv_houses if active else (),
                strength_score=round(strength, 4) if active else 0.0,
                citation=citation,
                summary=summary,
            )
        )

    # =========================================================================
    # 1. PANCHA MAHAPURUSHA YOGAS (5)
    # =========================================================================
    mahapurusha_specs = (
        ("ruchaka", "Ruchaka Mahapurusha Yoga", "mars", "Valor, command, and physical vitality from Mars in own/exalted Kendra."),
        ("bhadra", "Bhadra Mahapurusha Yoga", "mercury", "Intellect, eloquence, and analytical mastery from Mercury in own/exalted Kendra."),
        ("hamsa", "Hamsa Mahapurusha Yoga", "jupiter", "Wisdom, dharma, and spiritual authority from Jupiter in own/exalted Kendra."),
        ("malavya", "Malavya Mahapurusha Yoga", "venus", "Artistic refinement, prosperity, and grace from Venus in own/exalted Kendra."),
        ("sasa", "Sasa Mahapurusha Yoga", "saturn", "Discipline, organizational authority, and endurance from Saturn in own/exalted Kendra."),
    )
    for code, name, body, desc in mahapurusha_specs:
        is_act = houses[body] in KENDRA_HOUSES and _is_dignified(body, signs[body])
        add(
            code,
            name,
            "pancha_mahapurusha",
            is_act,
            (body,),
            (houses[body],),
            _planet_strength_score(body, signs[body], houses[body]),
            "Brihat Parashara Hora Shastra Ch. 75; Phaladeepika Ch. 6",
            desc,
        )

    # =========================================================================
    # 2. LUNAR YOGAS (10)
    # =========================================================================
    lunar_wings = ("mars", "mercury", "jupiter", "venus", "saturn")
    in_2nd_from_moon = tuple(b for b in lunar_wings if house_from_moon(b) == 2)
    in_12th_from_moon = tuple(b for b in lunar_wings if house_from_moon(b) == 12)

    sunapha_act = bool(in_2nd_from_moon) and not bool(in_12th_from_moon)
    add(
        "sunapha",
        "Sunapha Yoga",
        "lunar",
        sunapha_act,
        ("moon",) + in_2nd_from_moon,
        tuple({houses["moon"]} | {houses[b] for b in in_2nd_from_moon}),
        0.8,
        "Brihat Parashara Hora Shastra Ch. 37; Phaladeepika Ch. 6",
        "Self-acquired wealth and intelligence from planets (excluding Sun) in the 2nd house from the Moon.",
    )

    anapha_act = bool(in_12th_from_moon) and not bool(in_2nd_from_moon)
    add(
        "anapha",
        "Anapha Yoga",
        "lunar",
        anapha_act,
        ("moon",) + in_12th_from_moon,
        tuple({houses["moon"]} | {houses[b] for b in in_12th_from_moon}),
        0.8,
        "Brihat Parashara Hora Shastra Ch. 37; Phaladeepika Ch. 6",
        "Dignity, renown, and moral stature from planets (excluding Sun) in the 12th house from the Moon.",
    )

    durudhara_act = bool(in_2nd_from_moon) and bool(in_12th_from_moon)
    add(
        "durudhara",
        "Durudhara Yoga",
        "lunar",
        durudhara_act,
        ("moon",) + in_2nd_from_moon + in_12th_from_moon,
        tuple({houses["moon"]} | {houses[b] for b in in_2nd_from_moon + in_12th_from_moon}),
        0.9,
        "Brihat Parashara Hora Shastra Ch. 37; Phaladeepika Ch. 6",
        "Balanced prosperity and support from planets flanking both 2nd and 12th houses from the Moon.",
    )

    raw_kemadruma = not in_2nd_from_moon and not in_12th_from_moon
    kendra_from_lagna_planets = tuple(b for b in SEVEN_PLANETS if houses[b] in KENDRA_HOUSES)
    kendra_from_moon_planets = tuple(b for b in lunar_wings if house_from_moon(b) in KENDRA_HOUSES)
    kemadruma_cancelled = raw_kemadruma and (bool(kendra_from_lagna_planets) or bool(kendra_from_moon_planets))
    kemadruma_act = raw_kemadruma and not kemadruma_cancelled

    add(
        "kemadruma",
        "Kemadruma Yoga",
        "lunar",
        kemadruma_act,
        ("moon",),
        (houses["moon"],),
        0.4,
        "Brihat Parashara Hora Shastra Ch. 37; Jataka Parijata",
        "Unflanked Moon without Kendra support indicating solitary struggle.",
    )

    add(
        "kemadruma_bhanga",
        "Kemadruma Bhanga Yoga",
        "lunar",
        kemadruma_cancelled,
        ("moon",) + kendra_from_moon_planets,
        (houses["moon"],),
        0.78,
        "Brihat Parashara Hora Shastra Ch. 37; Phaladeepika Ch. 6",
        "Cancellation of Kemadruma through Kendra planetary support from Lagna or Moon, turning adversity into resilience.",
    )

    gajakesari_act = house_from_moon("jupiter") in KENDRA_HOUSES
    add(
        "gajakesari",
        "Gajakesari Yoga",
        "lunar",
        gajakesari_act,
        ("moon", "jupiter"),
        (houses["moon"], houses["jupiter"]),
        0.88 if _is_dignified("jupiter", signs["jupiter"]) else 0.78,
        "Brihat Parashara Hora Shastra Ch. 36; Phaladeepika Ch. 6",
        "Lasting reputation, wisdom, and protection from Jupiter in a Kendra from the Moon.",
    )

    adhi_benefics = tuple(
        b for b in ("mercury", "jupiter", "venus") if house_from_moon(b) in {6, 7, 8}
    )
    adhi_act = len(adhi_benefics) >= 2
    add(
        "adhi_yoga",
        "Chandra Adhi Yoga",
        "lunar",
        adhi_act,
        ("moon",) + adhi_benefics,
        tuple({houses["moon"]} | {houses[b] for b in adhi_benefics}),
        0.92 if len(adhi_benefics) == 3 else 0.78,
        "Brihat Parashara Hora Shastra Ch. 36; Phaladeepika Ch. 6",
        "Leadership, trustworthiness, and affluence from natural benefics occupying the 6th, 7th, and 8th from the Moon.",
    )

    cm_dist = house_from_moon("mars")
    chandra_mangala_act = cm_dist in {1, 7}
    add(
        "chandra_mangala",
        "Chandra-Mangala Yoga",
        "lunar",
        chandra_mangala_act,
        ("moon", "mars"),
        (houses["moon"], houses["mars"]),
        0.76,
        "Phaladeepika Ch. 6; Saravali",
        "Financial enterprise and decisive resourcefulness from Moon-Mars conjunction or mutual opposition.",
    )

    tenth_from_lagna_or_moon = tuple(
        b for b in SEVEN_PLANETS if houses[b] == 10 or house_from_moon(b) == 10
    )
    amala_act = bool(tenth_from_lagna_or_moon) and all(
        b in NATURAL_BENEFICS for b in tenth_from_lagna_or_moon
    )
    add(
        "amala",
        "Amala Yoga",
        "lunar",
        amala_act,
        tenth_from_lagna_or_moon,
        tuple({houses[b] for b in tenth_from_lagna_or_moon}),
        0.85,
        "Phaladeepika Ch. 6 Verse 14",
        "Spotless character, ethical renown, and lasting prosperity from exclusively benefic occupancy in the 10th from Lagna or Moon.",
    )

    upachaya_benefics = tuple(
        b for b in ("mercury", "jupiter", "venus") if houses[b] in {3, 6, 10, 11} or house_from_moon(b) in {3, 6, 10, 11}
    )
    vasumati_act = len(upachaya_benefics) == 3
    add(
        "vasumati",
        "Vasumati Yoga",
        "lunar",
        vasumati_act,
        upachaya_benefics,
        tuple({houses[b] for b in upachaya_benefics}),
        0.84,
        "Brihat Parashara Hora Shastra Ch. 36; Phaladeepika Ch. 6",
        "Abundant independent wealth from all three natural benefics (Mercury, Jupiter, Venus) occupying Upachaya (3, 6, 10, 11) houses.",
    )

    # =========================================================================
    # 3. SOLAR YOGAS (4)
    # =========================================================================
    solar_wings = ("mars", "mercury", "jupiter", "venus", "saturn")
    in_2nd_from_sun = tuple(b for b in solar_wings if house_from_sun(b) == 2)
    in_12th_from_sun = tuple(b for b in solar_wings if house_from_sun(b) == 12)

    veshi_act = bool(in_2nd_from_sun) and not bool(in_12th_from_sun)
    add(
        "veshi",
        "Veshi Yoga",
        "solar",
        veshi_act,
        ("sun",) + in_2nd_from_sun,
        tuple({houses["sun"]} | {houses[b] for b in in_2nd_from_sun}),
        0.78,
        "Brihat Parashara Hora Shastra Ch. 38; Phaladeepika Ch. 6",
        "Truthfulness, poise, and balanced judgment from planets (excluding Moon) in the 2nd house from the Sun.",
    )

    vashi_act = bool(in_12th_from_sun) and not bool(in_2nd_from_sun)
    add(
        "vashi",
        "Vashi Yoga",
        "solar",
        vashi_act,
        ("sun",) + in_12th_from_sun,
        tuple({houses["sun"]} | {houses[b] for b in in_12th_from_sun}),
        0.78,
        "Brihat Parashara Hora Shastra Ch. 38; Phaladeepika Ch. 6",
        "Organizational skill, scholarly focus, and influence from planets (excluding Moon) in the 12th house from the Sun.",
    )

    ubhayachari_act = bool(in_2nd_from_sun) and bool(in_12th_from_sun)
    add(
        "ubhayachari",
        "Ubhayachari Yoga",
        "solar",
        ubhayachari_act,
        ("sun",) + in_2nd_from_sun + in_12th_from_sun,
        tuple({houses["sun"]} | {houses[b] for b in in_2nd_from_sun + in_12th_from_sun}),
        0.9,
        "Brihat Parashara Hora Shastra Ch. 38; Phaladeepika Ch. 6",
        "Sovereign stature and broad support from planets flanking both 2nd and 12th houses from the Sun.",
    )

    budhaditya_act = signs["sun"] == signs["mercury"]
    add(
        "budhaditya",
        "Budhaditya Nipuna Yoga",
        "solar",
        budhaditya_act,
        ("sun", "mercury"),
        (houses["sun"],),
        0.82,
        "Brihat Parashara Hora Shastra Ch. 36; Phaladeepika Ch. 6",
        "Sharp intelligence, scholarly reputation, and administrative skill from Sun-Mercury conjunction.",
    )

    # =========================================================================
    # 4. RAJA, DHANA, PARIVARTANA, VIPAREETA & NEECHA BHANGA YOGAS (19)
    # =========================================================================
    l1 = house_lord(1)
    l2 = house_lord(2)
    l3 = house_lord(3)
    l4 = house_lord(4)
    l5 = house_lord(5)
    l6 = house_lord(6)
    l8 = house_lord(8)
    l9 = house_lord(9)
    l10 = house_lord(10)
    l11 = house_lord(11)
    l12 = house_lord(12)

    dk_act = _planets_connected(l9, l10, signs)
    add(
        "dharma_karmadhipati",
        "Dharma-Karmadhipati Raja Yoga",
        "raja",
        dk_act,
        tuple(dict.fromkeys((l9, l10))),
        tuple(dict.fromkeys((houses[l9], houses[l10]))),
        0.95,
        "Brihat Parashara Hora Shastra Ch. 39; Phaladeepika Ch. 7",
        "Supreme Raja Yoga linking the 9th lord of Dharma with the 10th lord of Karma.",
    )

    lp_act = _planets_connected(l1, l5, signs)
    add(
        "lagna_panchama_raja",
        "Lagna-Panchama Raja Yoga",
        "raja",
        lp_act,
        tuple(dict.fromkeys((l1, l5))),
        tuple(dict.fromkeys((houses[l1], houses[l5]))),
        0.88,
        "Brihat Parashara Hora Shastra Ch. 39",
        "Raja Yoga uniting the 1st lord of Self with the 5th lord of Intelligence and Poorvapunya.",
    )

    lb_act = _planets_connected(l1, l9, signs)
    add(
        "lagna_bhagya_raja",
        "Lagna-Bhagya Raja Yoga",
        "raja",
        lb_act,
        tuple(dict.fromkeys((l1, l9))),
        tuple(dict.fromkeys((houses[l1], houses[l9]))),
        0.9,
        "Brihat Parashara Hora Shastra Ch. 39",
        "Raja Yoga uniting the 1st lord of Self with the 9th lord of Fortune.",
    )

    cp_act = _planets_connected(l4, l5, signs)
    add(
        "chaturtha_panchama_raja",
        "Chaturtha-Panchama Raja Yoga",
        "raja",
        cp_act,
        tuple(dict.fromkeys((l4, l5))),
        tuple(dict.fromkeys((houses[l4], houses[l5]))),
        0.87,
        "Brihat Parashara Hora Shastra Ch. 39",
        "Kendra-Trikona Raja Yoga uniting the 4th lord of Sukha and the 5th lord of Vidya.",
    )

    # Parivartana (Mutual Sign Exchange) detection across houses 1..12
    good_houses = {1, 2, 4, 5, 7, 9, 10, 11}
    maha_pairs: list[tuple[str, str, int, int]] = []
    kahala_pairs: list[tuple[str, str, int, int]] = []
    dainya_pairs: list[tuple[str, str, int, int]] = []

    for h_a in range(1, 13):
        for h_b in range(h_a + 1, 13):
            lord_a = house_lord(h_a)
            lord_b = house_lord(h_b)
            if lord_a == lord_b:
                continue
            if houses[lord_a] == h_b and houses[lord_b] == h_a:
                if h_a in DUSTHANA_HOUSES or h_b in DUSTHANA_HOUSES:
                    dainya_pairs.append((lord_a, lord_b, h_a, h_b))
                elif h_a == 3 or h_b == 3:
                    kahala_pairs.append((lord_a, lord_b, h_a, h_b))
                elif h_a in good_houses and h_b in good_houses:
                    maha_pairs.append((lord_a, lord_b, h_a, h_b))

    add(
        "maha_parivartana",
        "Maha Parivartana Yoga",
        "parivartana",
        bool(maha_pairs),
        (maha_pairs[0][0], maha_pairs[0][1]) if maha_pairs else (),
        (maha_pairs[0][2], maha_pairs[0][3]) if maha_pairs else (),
        0.92,
        "Phaladeepika Ch. 6 Verse 32",
        "Mutual sign exchange between lords of Kendra, Trikona, 2nd, or 11th houses conferring high status and wealth.",
    )

    add(
        "kahala_parivartana",
        "Kahala Parivartana Yoga",
        "parivartana",
        bool(kahala_pairs),
        (kahala_pairs[0][0], kahala_pairs[0][1]) if kahala_pairs else (),
        (kahala_pairs[0][2], kahala_pairs[0][3]) if kahala_pairs else (),
        0.72,
        "Phaladeepika Ch. 6 Verse 33",
        "Mutual sign exchange involving the 3rd house lord requiring bold initiative.",
    )

    add(
        "dainya_parivartana",
        "Dainya Parivartana Yoga",
        "parivartana",
        bool(dainya_pairs),
        (dainya_pairs[0][0], dainya_pairs[0][1]) if dainya_pairs else (),
        (dainya_pairs[0][2], dainya_pairs[0][3]) if dainya_pairs else (),
        0.45,
        "Phaladeepika Ch. 6 Verse 34",
        "Mutual sign exchange involving a Dusthana (6th, 8th, or 12th) lord.",
    )

    # Vipareeta Raja Yogas: Harsha (6L in 6/8/12), Sarala (8L in 6/8/12), Vimala (12L in 6/8/12)
    harsha_act = houses[l6] in DUSTHANA_HOUSES
    add(
        "harsha_vipareeta",
        "Harsha Vipareeta Raja Yoga",
        "vipareeta_raja",
        harsha_act,
        (l6,),
        (houses[l6],),
        0.8,
        "Phaladeepika Ch. 6 Verse 63",
        "6th lord posited in the 6th, 8th, or 12th house, granting victory over obstacles and strong constitution.",
    )

    sarala_act = houses[l8] in DUSTHANA_HOUSES
    add(
        "sarala_vipareeta",
        "Sarala Vipareeta Raja Yoga",
        "vipareeta_raja",
        sarala_act,
        (l8,),
        (houses[l8],),
        0.82,
        "Phaladeepika Ch. 6 Verse 65",
        "8th lord posited in the 6th, 8th, or 12th house, granting fearlessness, longevity, and scholarly depth.",
    )

    vimala_act = houses[l12] in DUSTHANA_HOUSES
    add(
        "vimala_vipareeta",
        "Vimala Vipareeta Raja Yoga",
        "vipareeta_raja",
        vimala_act,
        (l12,),
        (houses[l12],),
        0.8,
        "Phaladeepika Ch. 6 Verse 67",
        "12th lord posited in the 6th, 8th, or 12th house, granting ethical independence and financial prudence.",
    )

    # Neecha Bhanga Raja Yoga (all 5 classical cancellation conditions)
    neecha_bhanga_planets: list[str] = []
    for body in SEVEN_PLANETS:
        if signs[body] == DEBILITATION_SIGN[body]:
            deb_sign = signs[body]
            dispositor = RASI_LORDS[deb_sign]
            exalt_lord = SIGN_EXALTATION_LORD.get(deb_sign)

            cond1 = houses[dispositor] in KENDRA_HOUSES or house_from_moon(dispositor) in KENDRA_HOUSES
            cond2 = exalt_lord is not None and (
                houses[exalt_lord] in KENDRA_HOUSES or house_from_moon(exalt_lord) in KENDRA_HOUSES
            )
            cond3 = _parashari_aspects_sign(dispositor, signs[dispositor], deb_sign)
            cond4 = RASI_LORDS[signs[dispositor]] == body
            cond5 = houses[body] in KENDRA_HOUSES or house_from_moon(body) in KENDRA_HOUSES

            if cond1 or cond2 or cond3 or cond4 or cond5:
                neecha_bhanga_planets.append(body)

    add(
        "neecha_bhanga_raja",
        "Neecha Bhanga Raja Yoga",
        "neecha_bhanga",
        bool(neecha_bhanga_planets),
        tuple(neecha_bhanga_planets),
        tuple({houses[b] for b in neecha_bhanga_planets}),
        0.9,
        "Phaladeepika Ch. 7 Verses 26-30; Jataka Parijata",
        "Debilitated planet rescued by classical cancellation conditions, converting initial hardship into high elevation.",
    )

    # Dhana Yoga (2nd and 11th lords connected with each other or with 5th/9th lords)
    dhana_act = (
        _planets_connected(l2, l11, signs)
        or _planets_connected(l2, l5, signs)
        or _planets_connected(l2, l9, signs)
        or _planets_connected(l11, l5, signs)
        or _planets_connected(l11, l9, signs)
    )
    add(
        "dhana_yoga",
        "Parashari Dhana Yoga",
        "dhana",
        dhana_act,
        tuple(dict.fromkeys((l2, l11, l5, l9))),
        tuple(dict.fromkeys((houses[l2], houses[l11]))),
        0.86,
        "Brihat Parashara Hora Shastra Ch. 41",
        "Wealth combination linking the 2nd and 11th treasury lords with Trikona lords.",
    )

    # Lakshmi Yoga: 9th lord in own/exalted sign in Kendra/Trikona while Lagna lord is strong
    lakshmi_act = (
        (houses[l9] in KENDRA_HOUSES or houses[l9] in TRIKONA_HOUSES)
        and _is_dignified(l9, signs[l9])
        and houses[l1] not in DUSTHANA_HOUSES
    )
    add(
        "lakshmi",
        "Lakshmi Yoga",
        "special_benefic",
        lakshmi_act,
        tuple(dict.fromkeys((l9, l1))),
        tuple(dict.fromkeys((houses[l9], houses[l1]))),
        0.93,
        "Brihat Parashara Hora Shastra Ch. 36; Phaladeepika Ch. 6",
        "Abundant fortune, noble character, and wealth from a dignified 9th lord in Kendra/Trikona with strong Lagna lord.",
    )

    # Saraswati Yoga: Jupiter, Venus, and Mercury in Kendra, Trikona, or 2nd house, with Jupiter strong
    saraswati_houses = KENDRA_HOUSES | TRIKONA_HOUSES | {2}
    saraswati_act = (
        houses["jupiter"] in saraswati_houses
        and houses["venus"] in saraswati_houses
        and houses["mercury"] in saraswati_houses
        and signs["jupiter"] != DEBILITATION_SIGN["jupiter"]
    )
    add(
        "saraswati",
        "Saraswati Yoga",
        "special_benefic",
        saraswati_act,
        ("jupiter", "venus", "mercury"),
        tuple(dict.fromkeys((houses["jupiter"], houses["venus"], houses["mercury"]))),
        0.92,
        "Phaladeepika Ch. 6 Verse 24; Saravali",
        "Mastery of learning, arts, and sciences from Jupiter, Venus, and Mercury in Kendra, Trikona, or 2nd house.",
    )

    # Parijata Yoga: Dispositor of Lagna lord (or dispositor of that dispositor) in own/exalted sign in Kendra/Trikona
    disp_1 = RASI_LORDS[signs[l1]]
    disp_2 = RASI_LORDS[signs[disp_1]]
    parijata_act = (
        (houses[disp_1] in (KENDRA_HOUSES | TRIKONA_HOUSES) and _is_dignified(disp_1, signs[disp_1]))
        or (houses[disp_2] in (KENDRA_HOUSES | TRIKONA_HOUSES) and _is_dignified(disp_2, signs[disp_2]))
    )
    add(
        "parijata",
        "Parijata Yoga",
        "special_benefic",
        parijata_act,
        tuple(dict.fromkeys((l1, disp_1, disp_2))),
        tuple(dict.fromkeys((houses[l1], houses[disp_1]))),
        0.85,
        "Brihat Parashara Hora Shastra Ch. 36; Jataka Parijata",
        "Rising stature in middle and later life through a dignified dispositor chain of the Lagna lord.",
    )

    # Kahala Yoga: Lords of 4th and 9th in mutual Kendras and Lagna lord strong
    kahala_dist = ((signs[l9] - signs[l4]) % 12) + 1
    kahala_act = kahala_dist in KENDRA_HOUSES and (_is_dignified(l1, signs[l1]) or houses[l1] in KENDRA_HOUSES)
    add(
        "kahala",
        "Kahala Yoga",
        "special_benefic",
        kahala_act,
        tuple(dict.fromkeys((l4, l9, l1))),
        tuple(dict.fromkeys((houses[l4], houses[l9]))),
        0.82,
        "Brihat Parashara Hora Shastra Ch. 36; Phaladeepika Ch. 6",
        "Executive daring, command, and enterprising spirit from 4th and 9th lords in mutual Kendras.",
    )

    # Chamara Yoga: Lagna lord exalted in Kendra and aspected by Jupiter, or two benefics in 1, 7, 9, 10
    benefics_in_chamara = [b for b in NATURAL_BENEFICS if houses[b] in {1, 7, 9, 10}]
    chamara_act = (
        houses[l1] in KENDRA_HOUSES
        and signs[l1] == EXALTATION_SIGN[l1]
        and _parashari_aspects_sign("jupiter", signs["jupiter"], signs[l1])
    ) or len(benefics_in_chamara) >= 2
    add(
        "chamara",
        "Chamara Yoga",
        "special_benefic",
        chamara_act,
        tuple(dict.fromkeys([l1] + benefics_in_chamara[:2])),
        tuple(dict.fromkeys([houses[l1]] + [houses[b] for b in benefics_in_chamara[:2]])),
        0.83,
        "Brihat Parashara Hora Shastra Ch. 36; Phaladeepika Ch. 6",
        "Eloquence, longevity, and scholarly distinction from exalted Lagna lord or benefics in 1, 7, 9, 10.",
    )

    # Sankha Yoga: Lords of 5th and 6th in mutual Kendras and Lagna lord strong
    sankha_dist = ((signs[l6] - signs[l5]) % 12) + 1
    sankha_act = sankha_dist in KENDRA_HOUSES and houses[l1] not in DUSTHANA_HOUSES
    add(
        "sankha",
        "Sankha Yoga",
        "special_benefic",
        sankha_act,
        tuple(dict.fromkeys((l5, l6, l1))),
        tuple(dict.fromkeys((houses[l5], houses[l6]))),
        0.81,
        "Brihat Parashara Hora Shastra Ch. 36; Phaladeepika Ch. 6",
        "Humanitarian spirit, learning, and longevity from 5th and 6th lords in mutual Kendras.",
    )

    # Bheri Yoga: Planets in 1, 2, 7, 12 or Venus, Jupiter, and Lagna lord in Kendra with strong 9th lord
    bheri_act = (
        houses["venus"] in KENDRA_HOUSES
        and houses["jupiter"] in KENDRA_HOUSES
        and houses[l1] in KENDRA_HOUSES
        and houses[l9] not in DUSTHANA_HOUSES
    )
    add(
        "bheri",
        "Bheri Yoga",
        "special_benefic",
        bheri_act,
        tuple(dict.fromkeys(("venus", "jupiter", l1, l9))),
        tuple(dict.fromkeys((houses["venus"], houses["jupiter"], houses[l1]))),
        0.88,
        "Brihat Parashara Hora Shastra Ch. 36; Phaladeepika Ch. 6",
        "Multi-source prosperity, vitality, and family harmony from Venus, Jupiter, and Lagna lord in Kendras.",
    )

    # =========================================================================
    # 5. NABHASA YOGAS (32: 3 Ashraya + 2 Dala + 20 Akriti + 7 Sankhya)
    # =========================================================================
    occupied_signs = {signs[b] for b in SEVEN_PLANETS}
    occupied_houses = {houses[b] for b in SEVEN_PLANETS}
    all_houses_tuple = tuple(sorted(occupied_houses))

    # --- 5A. Ashraya Nabhasa Yogas (3) ---
    add(
        "nabhasa_rajju",
        "Rajju Nabhasa Yoga",
        "nabhasa_ashraya",
        occupied_signs.issubset({0, 3, 6, 9}),
        SEVEN_PLANETS,
        all_houses_tuple,
        0.78,
        "Brihat Parashara Hora Shastra Ch. 35 Verse 7",
        "All seven planets occupy Chara (movable) signs, indicating dynamism, travel, and adaptability.",
    )
    add(
        "nabhasa_musala",
        "Musala Nabhasa Yoga",
        "nabhasa_ashraya",
        occupied_signs.issubset({1, 4, 7, 10}),
        SEVEN_PLANETS,
        all_houses_tuple,
        0.78,
        "Brihat Parashara Hora Shastra Ch. 35 Verse 7",
        "All seven planets occupy Sthira (fixed) signs, indicating stability, persistence, and enduring assets.",
    )
    add(
        "nabhasa_nala",
        "Nala Nabhasa Yoga",
        "nabhasa_ashraya",
        occupied_signs.issubset({2, 5, 8, 11}),
        SEVEN_PLANETS,
        all_houses_tuple,
        0.78,
        "Brihat Parashara Hora Shastra Ch. 35 Verse 7",
        "All seven planets occupy Dwiswabhava (dual) signs, indicating versatility and intellectual breadth.",
    )

    # --- 5B. Dala Nabhasa Yogas (2) ---
    kendra_occupants = [b for b in SEVEN_PLANETS if houses[b] in KENDRA_HOUSES]
    mala_act = len(kendra_occupants) >= 3 and all(b in NATURAL_BENEFICS for b in kendra_occupants)
    sarpa_act = len(kendra_occupants) >= 3 and all(b in NATURAL_MALEFICS for b in kendra_occupants)
    add(
        "nabhasa_mala",
        "Mala (Srik) Dala Nabhasa Yoga",
        "nabhasa_dala",
        mala_act,
        tuple(kendra_occupants),
        tuple(sorted({houses[b] for b in kendra_occupants})),
        0.85,
        "Brihat Parashara Hora Shastra Ch. 35 Verse 8",
        "Kendra houses occupied exclusively by natural benefics, conferring comfort and contentment.",
    )
    add(
        "nabhasa_sarpa",
        "Sarpa (Bhujanga) Dala Nabhasa Yoga",
        "nabhasa_dala",
        sarpa_act,
        tuple(kendra_occupants),
        tuple(sorted({houses[b] for b in kendra_occupants})),
        0.4,
        "Brihat Parashara Hora Shastra Ch. 35 Verse 8",
        "Kendra houses occupied exclusively by natural malefics, requiring resilience through pressure.",
    )

    # --- 5C. Akriti Nabhasa Yogas (20) ---
    gada_act = occupied_houses in ({1, 4}, {4, 7}, {7, 10}, {10, 1})
    add(
        "nabhasa_gada",
        "Gada Akriti Nabhasa Yoga",
        "nabhasa_akriti",
        gada_act,
        SEVEN_PLANETS,
        all_houses_tuple,
        0.76,
        "Brihat Parashara Hora Shastra Ch. 35 Verse 9",
        "All seven planets concentrated in two adjacent Kendra houses.",
    )

    sakata_act = occupied_houses == {1, 7}
    add(
        "nabhasa_sakata",
        "Sakata Akriti Nabhasa Yoga",
        "nabhasa_akriti",
        sakata_act,
        SEVEN_PLANETS,
        all_houses_tuple,
        0.65,
        "Brihat Parashara Hora Shastra Ch. 35 Verse 9",
        "All seven planets posited exclusively in the 1st and 7th houses.",
    )

    vihaga_act = occupied_houses == {4, 10}
    add(
        "nabhasa_vihaga",
        "Vihaga Akriti Nabhasa Yoga",
        "nabhasa_akriti",
        vihaga_act,
        SEVEN_PLANETS,
        all_houses_tuple,
        0.7,
        "Brihat Parashara Hora Shastra Ch. 35 Verse 9",
        "All seven planets posited exclusively in the 4th and 10th houses.",
    )

    sringataka_act = occupied_houses.issubset({1, 5, 9})
    add(
        "nabhasa_sringataka",
        "Sringataka Akriti Nabhasa Yoga",
        "nabhasa_akriti",
        sringataka_act,
        SEVEN_PLANETS,
        all_houses_tuple,
        0.84,
        "Brihat Parashara Hora Shastra Ch. 35 Verse 10",
        "All seven planets posited exclusively in the Trikona (1st, 5th, 9th) houses.",
    )

    hala_act = (
        occupied_houses.issubset({2, 6, 10})
        or occupied_houses.issubset({3, 7, 11})
        or occupied_houses.issubset({4, 8, 12})
    )
    add(
        "nabhasa_hala",
        "Hala Akriti Nabhasa Yoga",
        "nabhasa_akriti",
        hala_act,
        SEVEN_PLANETS,
        all_houses_tuple,
        0.75,
        "Brihat Parashara Hora Shastra Ch. 35 Verse 10",
        "All seven planets posited in a mutual trine triangle outside the 1-5-9 axis (2-6-10, 3-7-11, or 4-8-12).",
    )

    vajra_act = all(houses[b] in {1, 7} for b in NATURAL_BENEFICS) and all(
        houses[m] in {4, 10} for m in NATURAL_MALEFICS
    )
    add(
        "nabhasa_vajra",
        "Vajra Akriti Nabhasa Yoga",
        "nabhasa_akriti",
        vajra_act,
        SEVEN_PLANETS,
        all_houses_tuple,
        0.82,
        "Brihat Parashara Hora Shastra Ch. 35 Verse 11",
        "All benefics in the 1st and 7th houses and all malefics in the 4th and 10th houses.",
    )

    yava_act = all(houses[m] in {1, 7} for m in NATURAL_MALEFICS) and all(
        houses[b] in {4, 10} for b in NATURAL_BENEFICS
    )
    add(
        "nabhasa_yava",
        "Yava Akriti Nabhasa Yoga",
        "nabhasa_akriti",
        yava_act,
        SEVEN_PLANETS,
        all_houses_tuple,
        0.74,
        "Brihat Parashara Hora Shastra Ch. 35 Verse 11",
        "All malefics in the 1st and 7th houses and all benefics in the 4th and 10th houses.",
    )

    kamala_act = occupied_houses == {1, 4, 7, 10}
    add(
        "nabhasa_kamala",
        "Kamala Akriti Nabhasa Yoga",
        "nabhasa_akriti",
        kamala_act,
        SEVEN_PLANETS,
        all_houses_tuple,
        0.9,
        "Brihat Parashara Hora Shastra Ch. 35 Verse 12",
        "All seven planets distributed across all four Kendra houses (1, 4, 7, 10).",
    )

    vapi_act = occupied_houses.issubset(PANAPARA_HOUSES) or occupied_houses.issubset(APOKLIMA_HOUSES)
    add(
        "nabhasa_vapi",
        "Vapi Akriti Nabhasa Yoga",
        "nabhasa_akriti",
        vapi_act,
        SEVEN_PLANETS,
        all_houses_tuple,
        0.77,
        "Brihat Parashara Hora Shastra Ch. 35 Verse 12",
        "All seven planets posited exclusively in Panapara (2, 5, 8, 11) or Apoklima (3, 6, 9, 12) houses.",
    )

    yupa_act = occupied_houses.issubset({1, 2, 3, 4})
    add(
        "nabhasa_yupa",
        "Yupa Akriti Nabhasa Yoga",
        "nabhasa_akriti",
        yupa_act,
        SEVEN_PLANETS,
        all_houses_tuple,
        0.76,
        "Brihat Parashara Hora Shastra Ch. 35 Verse 13",
        "All seven planets in the four contiguous houses starting from the Ascendant (1, 2, 3, 4).",
    )

    sara_act = occupied_houses.issubset({4, 5, 6, 7})
    add(
        "nabhasa_sara",
        "Sara (Ishu) Akriti Nabhasa Yoga",
        "nabhasa_akriti",
        sara_act,
        SEVEN_PLANETS,
        all_houses_tuple,
        0.72,
        "Brihat Parashara Hora Shastra Ch. 35 Verse 13",
        "All seven planets in the four contiguous houses starting from the 4th house (4, 5, 6, 7).",
    )

    sakti_act = occupied_houses.issubset({7, 8, 9, 10})
    add(
        "nabhasa_sakti",
        "Sakti Akriti Nabhasa Yoga",
        "nabhasa_akriti",
        sakti_act,
        SEVEN_PLANETS,
        all_houses_tuple,
        0.72,
        "Brihat Parashara Hora Shastra Ch. 35 Verse 13",
        "All seven planets in the four contiguous houses starting from the 7th house (7, 8, 9, 10).",
    )

    danda_act = occupied_houses.issubset({10, 11, 12, 1})
    add(
        "nabhasa_danda",
        "Danda Akriti Nabhasa Yoga",
        "nabhasa_akriti",
        danda_act,
        SEVEN_PLANETS,
        all_houses_tuple,
        0.7,
        "Brihat Parashara Hora Shastra Ch. 35 Verse 13",
        "All seven planets in the four contiguous houses starting from the 10th house (10, 11, 12, 1).",
    )

    nauka_act = occupied_houses.issubset({1, 2, 3, 4, 5, 6, 7}) and 1 in occupied_houses and 7 in occupied_houses
    add(
        "nabhasa_nauka",
        "Nauka Akriti Nabhasa Yoga",
        "nabhasa_akriti",
        nauka_act,
        SEVEN_PLANETS,
        all_houses_tuple,
        0.8,
        "Brihat Parashara Hora Shastra Ch. 35 Verse 14",
        "All seven planets occupying the seven contiguous houses from the 1st through the 7th.",
    )

    kuta_act = occupied_houses.issubset({4, 5, 6, 7, 8, 9, 10}) and 4 in occupied_houses and 10 in occupied_houses
    add(
        "nabhasa_kuta",
        "Kuta Akriti Nabhasa Yoga",
        "nabhasa_akriti",
        kuta_act,
        SEVEN_PLANETS,
        all_houses_tuple,
        0.72,
        "Brihat Parashara Hora Shastra Ch. 35 Verse 14",
        "All seven planets occupying the seven contiguous houses from the 4th through the 10th.",
    )

    chatra_act = occupied_houses.issubset({7, 8, 9, 10, 11, 12, 1}) and 7 in occupied_houses and 1 in occupied_houses
    add(
        "nabhasa_chatra",
        "Chatra Akriti Nabhasa Yoga",
        "nabhasa_akriti",
        chatra_act,
        SEVEN_PLANETS,
        all_houses_tuple,
        0.78,
        "Brihat Parashara Hora Shastra Ch. 35 Verse 14",
        "All seven planets occupying the seven contiguous houses from the 7th through the 1st.",
    )

    chapa_act = occupied_houses.issubset({10, 11, 12, 1, 2, 3, 4}) and 10 in occupied_houses and 4 in occupied_houses
    add(
        "nabhasa_chapa",
        "Chapa (Karmuka) Akriti Nabhasa Yoga",
        "nabhasa_akriti",
        chapa_act,
        SEVEN_PLANETS,
        all_houses_tuple,
        0.78,
        "Brihat Parashara Hora Shastra Ch. 35 Verse 14",
        "All seven planets occupying the seven contiguous houses from the 10th through the 4th.",
    )

    chandra_act = False
    for start_h in (2, 3, 5, 6, 8, 9, 11, 12):
        arc_7 = {((start_h - 1 + offset) % 12) + 1 for offset in range(7)}
        end_h = ((start_h - 1 + 6) % 12) + 1
        if occupied_houses.issubset(arc_7) and start_h in occupied_houses and end_h in occupied_houses:
            chandra_act = True
            break
    add(
        "nabhasa_chandra",
        "Ardha-Chandra Akriti Nabhasa Yoga",
        "nabhasa_akriti",
        chandra_act,
        SEVEN_PLANETS,
        all_houses_tuple,
        0.82,
        "Brihat Parashara Hora Shastra Ch. 35 Verse 15",
        "All seven planets occupying seven contiguous houses starting from a Panapara or Apoklima house.",
    )

    chakra_act = occupied_houses.issubset({1, 3, 5, 7, 9, 11})
    add(
        "nabhasa_chakra",
        "Chakra Akriti Nabhasa Yoga",
        "nabhasa_akriti",
        chakra_act,
        SEVEN_PLANETS,
        all_houses_tuple,
        0.88,
        "Brihat Parashara Hora Shastra Ch. 35 Verse 15",
        "All seven planets occupying the six odd houses (1, 3, 5, 7, 9, 11).",
    )

    samudra_act = occupied_houses.issubset({2, 4, 6, 8, 10, 12})
    add(
        "nabhasa_samudra",
        "Samudra Akriti Nabhasa Yoga",
        "nabhasa_akriti",
        samudra_act,
        SEVEN_PLANETS,
        all_houses_tuple,
        0.86,
        "Brihat Parashara Hora Shastra Ch. 35 Verse 15",
        "All seven planets occupying the six even houses (2, 4, 6, 8, 10, 12).",
    )

    # --- 5D. Sankhya Nabhasa Yogas (7) ---
    sign_count = len(occupied_signs)
    sankhya_specs = (
        (7, "nabhasa_vallaki", "Vallaki (Veena) Sankhya Yoga", 0.84, "All seven planets occupy seven distinct signs."),
        (6, "nabhasa_dama", "Dama (Damini) Sankhya Yoga", 0.82, "All seven planets occupy six distinct signs."),
        (5, "nabhasa_pasa", "Pasa Sankhya Yoga", 0.76, "All seven planets occupy five distinct signs."),
        (4, "nabhasa_kedara", "Kedara Sankhya Yoga", 0.78, "All seven planets occupy four distinct signs."),
        (3, "nabhasa_sula", "Sula Sankhya Yoga", 0.68, "All seven planets occupy three distinct signs."),
        (2, "nabhasa_yuga", "Yuga Sankhya Yoga", 0.62, "All seven planets occupy two distinct signs."),
        (1, "nabhasa_gola", "Gola Sankhya Yoga", 0.55, "All seven planets cluster into a single sign."),
    )
    for target_cnt, code, name, score, desc in sankhya_specs:
        add(
            code,
            name,
            "nabhasa_sankhya",
            sign_count == target_cnt,
            SEVEN_PLANETS,
            all_houses_tuple,
            score,
            "Brihat Parashara Hora Shastra Ch. 35 Verses 16-17",
            desc,
        )

    active_tuple = tuple(f for f in findings if f.active)
    by_code = {f.code: f for f in findings}
    payload = {
        "asc_rasi": asc_sign,
        "planet_signs": {b: signs[b] for b in SEVEN_PLANETS},
        "active_codes": [f.code for f in active_tuple],
    }
    return ClassicalYogaReport(
        ascendant_lon_deg=asc_lon,
        ascendant_rasi_index=asc_sign,
        yogas=tuple(findings),
        active_yogas=active_tuple,
        by_code=by_code,
        receipt_sha256=canonical_hash(payload),
    )
