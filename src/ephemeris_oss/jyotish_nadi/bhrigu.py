"""Bhrigu Bindu, Bhrigu Nandi Nadi Directional Trines, and Planetary Age Progressions.

Implements classical Nadi Jyotisha mathematical techniques from *Bhrigu Nandi Nadi*,
*Chandra Kala Nadi*, and *Bhrigu Samhita*:
1. **Bhrigu Bindu (Muntha-Rahu-Chandra Midpoint)**:
   Computes the zodiacal forward arc from Rahu to the Moon
   ``arc = (moon_lon_deg - rahu_lon_deg) % 360.0`` and the sensitive karmic midpoint
   ``bindu = (rahu_lon_deg + arc / 2.0) % 360.0``, along with its Rasi, degree in sign,
   Nakshatra, Pada, Navamsa (D9) sign, and active transit aspects (conjunction,
   7th opposition, and 5th/9th trines) with exact angular orb.
2. **Bhrigu Nandi Nadi Directional Trines & Connection Vectors**:
   Groups natal planets into the four classical directional trines:
   - ``East`` (Fire / Dharma): Mesha (0), Simha (4), Dhanu (8)
   - ``South`` (Earth / Artha): Vrishabha (1), Kanya (5), Makara (9)
   - ``West`` (Air / Kama): Mithuna (2), Tula (6), Kumbha (10)
   - ``North`` (Water / Moksha): Karka (3), Vrishchika (7), Meena (11)
   Evaluates each planet's Nadi connection vector: trinal ``1-5-9`` links sorted by
   degree in sign (so earlier degrees pass influence to later degrees), ``2nd_front``
   obstructing/receiving planets, ``12th_behind`` backing planets, ``7th_opposite``
   confronting planets, and ``planet_kartari`` hemming status (``Shubha Kartari`` vs
   ``Papa Kartari``).
3. **Bhrigu Chakra Planetary Age Progression**:
   Evaluates age progressions for any native age in ``0..120`` years:
   - Lagna progresses at 1 sign per year.
   - Jupiter (Jeeva) progresses at 1 sign per year (12-year cycle).
   - Saturn (Karma) progresses at 1 sign per 2.5 years (30-year cycle).
"""

from __future__ import annotations

from dataclasses import dataclass
import math
from typing import Any, Final, Mapping

from ..engine.receipt import canonical_hash
from ..jyotish.nakshatra import NAKSHATRA_NAMES, RASI_NAMES, VIMSHOTTARI_RULERS
from ..jyotish.vargas import RASI_LORDS

CANONICAL_GRAHAS: Final[tuple[str, ...]] = (
    "sun",
    "moon",
    "mars",
    "mercury",
    "jupiter",
    "venus",
    "saturn",
    "rahu",
    "ketu",
)

NATURAL_BENEFICS: Final[frozenset[str]] = frozenset({"moon", "mercury", "jupiter", "venus"})
NATURAL_MALEFICS: Final[frozenset[str]] = frozenset({"sun", "mars", "saturn", "rahu", "ketu"})

NADI_DIRECTIONS_ORDER: Final[tuple[str, ...]] = ("East", "South", "West", "North")

NADI_DIRECTION_SIGNS: Final[Mapping[str, tuple[int, int, int]]] = {
    "East": (0, 4, 8),
    "South": (1, 5, 9),
    "West": (2, 6, 10),
    "North": (3, 7, 11),
}

NADI_DIRECTION_ELEMENT: Final[Mapping[str, str]] = {
    "East": "Fire",
    "South": "Earth",
    "West": "Air",
    "North": "Water",
}

NADI_DIRECTION_PURUSHARTHA: Final[Mapping[str, str]] = {
    "East": "Dharma",
    "South": "Artha",
    "West": "Kama",
    "North": "Moksha",
}


def _norm360(lon_deg: float) -> float:
    val = float(lon_deg)
    if not math.isfinite(val):
        raise ValueError("longitude must be a finite float")
    return val % 360.0


def _angular_separation_deg(a_deg: float, b_deg: float) -> float:
    """Return shortest angular distance in [0, 180] between two ecliptic longitudes."""
    diff = (float(a_deg) - float(b_deg)) % 360.0
    return diff if diff <= 180.0 else 360.0 - diff


def _canonical_planet_name(name: str) -> str:
    return str(name).strip().lower()


@dataclass(frozen=True)
class BhriguBinduTransitAspect:
    """Active transit aspect from a transiting planet to the natal Bhrigu Bindu."""

    planet: str
    transit_lon_deg: float
    transit_sign_index: int
    transit_sign_name: str
    aspect_type: str
    house_from_bindu: int
    target_lon_deg: float
    orb_deg: float
    is_same_or_trinal_sign: bool


@dataclass(frozen=True)
class BhriguBinduReport:
    """Complete Bhrigu Bindu calculation and transit activation report."""

    moon_lon_deg: float
    rahu_lon_deg: float
    arc_deg: float
    bindu_lon_deg: float
    sign_index: int
    sign_name: str
    sign_lord: str
    degree_in_sign: float
    nakshatra_index: int
    nakshatra_name: str
    nakshatra_lord: str
    pada: int
    navamsa_sign_index: int
    navamsa_sign_name: str
    navamsa_lord: str
    exact_aspect_longitudes: Mapping[str, float]
    active_transit_aspects: tuple[BhriguBinduTransitAspect, ...]
    receipt_sha256: str

    @property
    def longitude_deg(self) -> float:
        return self.bindu_lon_deg

    @property
    def rahu_to_moon_arc_deg(self) -> float:
        return self.arc_deg

    @property
    def sign(self) -> str:
        return self.sign_name

    @property
    def nakshatra(self) -> str:
        return self.nakshatra_name

    @property
    def navamsa_sign(self) -> str:
        return self.navamsa_sign_name

    @property
    def transit_aspects(self) -> tuple[BhriguBinduTransitAspect, ...]:
        return self.active_transit_aspects


@dataclass(frozen=True)
class NadiTrineGroup:
    """One of the four classical Bhrigu Nandi Nadi directional trine groups."""

    direction: str
    element: str
    purushartha: str
    sign_indices: tuple[int, int, int]
    sign_names: tuple[str, str, str]
    planets_by_degree: tuple[str, ...]


@dataclass(frozen=True)
class NadiPlanetLink:
    """Directional Nadi connection vector for a single natal planet."""

    planet: str
    longitude_deg: float
    sign_index: int
    sign_name: str
    degree_in_sign: float
    direction: str
    element: str
    purushartha: str
    trinal_1_5_9: tuple[str, ...]
    trine_sequence: tuple[str, ...]
    preceding_in_trine: tuple[str, ...]
    succeeding_in_trine: tuple[str, ...]
    front_2nd: tuple[str, ...]
    behind_12th: tuple[str, ...]
    opposite_7th: tuple[str, ...]
    planet_kartari: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "planet": self.planet,
            "longitude_deg": self.longitude_deg,
            "sign_index": self.sign_index,
            "sign_name": self.sign_name,
            "degree_in_sign": self.degree_in_sign,
            "direction": self.direction,
            "element": self.element,
            "purushartha": self.purushartha,
            "trinal_1_5_9": self.trinal_1_5_9,
            "trine_sequence": self.trine_sequence,
            "preceding_in_trine": self.preceding_in_trine,
            "succeeding_in_trine": self.succeeding_in_trine,
            "2nd_front": self.front_2nd,
            "12th_behind": self.behind_12th,
            "7th_opposite": self.opposite_7th,
            "front_2nd": self.front_2nd,
            "behind_12th": self.behind_12th,
            "opposite_7th": self.opposite_7th,
            "planet_kartari": self.planet_kartari,
        }

    def __getitem__(self, key: str) -> Any:
        mapping = self.to_dict()
        if key in mapping:
            return mapping[key]
        raise KeyError(key)


@dataclass(frozen=True)
class NadiDirectionalReport:
    """Complete Bhrigu Nandi Nadi directional trine and planetary link report."""

    directional_trines: Mapping[str, tuple[str, ...]]
    trine_groups: Mapping[str, NadiTrineGroup]
    planet_links: Mapping[str, NadiPlanetLink]
    receipt_sha256: str

    def __getitem__(self, key: str) -> Any:
        if key in self. directional_trines:
            return self.directional_trines[key]
        norm_key = _canonical_planet_name(key)
        if norm_key in self.planet_links:
            return self.planet_links[norm_key]
        raise KeyError(key)


@dataclass(frozen=True)
class BhriguProgressionReport:
    """Bhrigu Chakra age progression report for Lagna, Jupiter, and Saturn."""

    age_years: float
    natal_lagna_sign_index: int
    natal_lagna_sign_name: str
    natal_jupiter_sign_index: int
    natal_jupiter_sign_name: str
    natal_saturn_sign_index: int
    natal_saturn_sign_name: str
    progressed_lagna_sign_index: int
    progressed_lagna_sign_name: str
    progressed_lagna_lon_deg: float
    progressed_lagna_house: int
    progressed_jupiter_sign_index: int
    progressed_jupiter_sign_name: str
    progressed_jupiter_lon_deg: float
    progressed_jupiter_house: int
    jupiter_cycle_number: int
    progressed_saturn_sign_index: int
    progressed_saturn_sign_name: str
    progressed_saturn_lon_deg: float
    progressed_saturn_house: int
    saturn_cycle_number: int
    activated_houses: tuple[int, ...]
    double_transit_houses: tuple[int, ...]
    jupiter_triggered_planets: tuple[str, ...]
    saturn_triggered_planets: tuple[str, ...]
    receipt_sha256: str

    @property
    def progressed_lagna_sign(self) -> int:
        return self.progressed_lagna_sign_index

    @property
    def progressed_jupiter_sign(self) -> int:
        return self.progressed_jupiter_sign_index

    @property
    def progressed_saturn_sign(self) -> int:
        return self.progressed_saturn_sign_index


def compute_bhrigu_bindu(
    moon_lon_deg: float,
    rahu_lon_deg: float,
    transit_longitudes: Mapping[str, float] | None = None,
    orb_deg: float = 15.0,
) -> BhriguBinduReport:
    """Compute the Bhrigu Bindu (Rahu-to-Moon zodiacal midpoint) and active transit aspects.

    Parameters
    ----------
    moon_lon_deg:
        Sidereal longitude of natal Moon in degrees ``[0, 360)``.
    rahu_lon_deg:
        Sidereal longitude of natal Rahu in degrees ``[0, 360)``.
    transit_longitudes:
        Optional mapping of transiting planet names to sidereal longitudes in degrees.
    orb_deg:
        Maximum angular orb in degrees around exact ``conjunction`` (0 deg),
        ``7th opposition`` (180 deg), or ``5th/9th trines`` (120 / 240 deg).
        Defaults to ``15.0`` degrees.
    """
    moon_lon = _norm360(moon_lon_deg)
    rahu_lon = _norm360(rahu_lon_deg)
    max_orb = float(orb_deg)
    if not math.isfinite(max_orb) or max_orb < 0.0:
        raise ValueError("orb_deg must be a non-negative finite float")

    arc_deg = (moon_lon - rahu_lon) % 360.0
    bindu_lon_deg = (rahu_lon + arc_deg / 2.0) % 360.0

    sign_index = int(bindu_lon_deg // 30.0) % 12
    sign_name = RASI_NAMES[sign_index]
    sign_lord = RASI_LORDS[sign_index].lower()
    degree_in_sign = bindu_lon_deg % 30.0

    nakshatra_index = int((bindu_lon_deg * 27.0 + 1e-12) / 360.0) % 27
    nakshatra_name = NAKSHATRA_NAMES[nakshatra_index]
    nakshatra_lord = VIMSHOTTARI_RULERS[nakshatra_index % 9].lower()
    pada_index_108 = int((bindu_lon_deg * 108.0 + 1e-12) / 360.0) % 108
    pada = (pada_index_108 % 4) + 1
    navamsa_sign_index = pada_index_108 % 12
    navamsa_sign_name = RASI_NAMES[navamsa_sign_index]
    navamsa_lord = RASI_LORDS[navamsa_sign_index].lower()

    exact_aspect_longitudes: dict[str, float] = {
        "conjunction": bindu_lon_deg,
        "5th_trine": (bindu_lon_deg + 120.0) % 360.0,
        "7th_opposition": (bindu_lon_deg + 180.0) % 360.0,
        "9th_trine": (bindu_lon_deg + 240.0) % 360.0,
    }

    aspect_targets: tuple[tuple[str, int, float], ...] = (
        ("conjunction", 1, exact_aspect_longitudes["conjunction"]),
        ("5th/9th trines", 5, exact_aspect_longitudes["5th_trine"]),
        ("7th opposition", 7, exact_aspect_longitudes["7th_opposition"]),
        ("5th/9th trines", 9, exact_aspect_longitudes["9th_trine"]),
    )

    active_aspects: list[BhriguBinduTransitAspect] = []
    if transit_longitudes:
        for raw_planet, raw_lon in sorted(transit_longitudes.items(), key=lambda kv: str(kv[0]).lower()):
            p_name = _canonical_planet_name(raw_planet)
            t_lon = _norm360(raw_lon)
            t_sign = int(t_lon // 30.0) % 12
            house_from_bindu = ((t_sign - sign_index) % 12) + 1

            best_match: BhriguBinduTransitAspect | None = None
            for aspect_label, target_house, target_lon in aspect_targets:
                current_orb = _angular_separation_deg(t_lon, target_lon)
                if current_orb <= max_orb:
                    candidate = BhriguBinduTransitAspect(
                        planet=p_name,
                        transit_lon_deg=t_lon,
                        transit_sign_index=t_sign,
                        transit_sign_name=RASI_NAMES[t_sign],
                        aspect_type=aspect_label,
                        house_from_bindu=target_house,
                        target_lon_deg=target_lon,
                        orb_deg=current_orb,
                        is_same_or_trinal_sign=(house_from_bindu == target_house),
                    )
                    if best_match is None or candidate.orb_deg < best_match.orb_deg:
                        best_match = candidate
            if best_match is not None:
                active_aspects.append(best_match)

    active_aspects.sort(key=lambda item: (item.orb_deg, item.planet))

    receipt = canonical_hash(
        {
            "engine": "bhrigu_bindu",
            "moon_lon_deg": round(moon_lon, 9),
            "rahu_lon_deg": round(rahu_lon, 9),
            "arc_deg": round(arc_deg, 9),
            "bindu_lon_deg": round(bindu_lon_deg, 9),
            "sign_index": sign_index,
            "nakshatra_index": nakshatra_index,
            "pada": pada,
            "navamsa_sign_index": navamsa_sign_index,
            "active_aspects": [
                {
                    "planet": a.planet,
                    "aspect_type": a.aspect_type,
                    "orb_deg": round(a.orb_deg, 9),
                }
                for a in active_aspects
            ],
        }
    )

    return BhriguBinduReport(
        moon_lon_deg=moon_lon,
        rahu_lon_deg=rahu_lon,
        arc_deg=arc_deg,
        bindu_lon_deg=bindu_lon_deg,
        sign_index=sign_index,
        sign_name=sign_name,
        sign_lord=sign_lord,
        degree_in_sign=degree_in_sign,
        nakshatra_index=nakshatra_index,
        nakshatra_name=nakshatra_name,
        nakshatra_lord=nakshatra_lord,
        pada=pada,
        navamsa_sign_index=navamsa_sign_index,
        navamsa_sign_name=navamsa_sign_name,
        navamsa_lord=navamsa_lord,
        exact_aspect_longitudes=exact_aspect_longitudes,
        active_transit_aspects=tuple(active_aspects),
        receipt_sha256=receipt,
    )


def _classify_kartari(behind_planets: tuple[str, ...], front_planets: tuple[str, ...]) -> str:
    """Classify Shubha or Papa Kartari when both adjacent signs are occupied."""
    if not behind_planets or not front_planets:
        return "None"
    combined = set(behind_planets) | set(front_planets)
    all_benefic = all(p in NATURAL_BENEFICS for p in combined)
    all_malefic = all(p in NATURAL_MALEFICS for p in combined)
    if all_benefic:
        return "Shubha Kartari"
    if all_malefic:
        return "Papa Kartari"
    return "Mixed Kartari"


def compute_nadi_directional_links(
    planet_longitudes: Mapping[str, float],
) -> NadiDirectionalReport:
    """Group natal planets into the 4 Bhrigu Nandi Nadi directional trines and compute connection vectors.

    Parameters
    ----------
    planet_longitudes:
        Mapping of planet identifiers (e.g. ``sun``, ``moon``, ``mars``, ``mercury``,
        ``jupiter``, ``venus``, ``saturn``, ``rahu``, ``ketu``) to sidereal longitudes
        in degrees ``[0, 360)``.
    """
    if not planet_longitudes:
        raise ValueError("planet_longitudes must not be empty")

    normalized: dict[str, float] = {}
    sign_of: dict[str, int] = {}
    deg_in_sign_of: dict[str, float] = {}

    for raw_name, raw_lon in planet_longitudes.items():
        p_name = _canonical_planet_name(raw_name)
        lon = _norm360(raw_lon)
        normalized[p_name] = lon
        sign_of[p_name] = int(lon // 30.0) % 12
        deg_in_sign_of[p_name] = lon % 30.0

    def _degree_sort_key(p: str) -> tuple[float, str]:
        return (deg_in_sign_of[p], p)

    directional_trines: dict[str, tuple[str, ...]] = {}
    trine_groups: dict[str, NadiTrineGroup] = {}

    for direction in NADI_DIRECTIONS_ORDER:
        signs = NADI_DIRECTION_SIGNS[direction]
        members = sorted(
            (p for p, s in sign_of.items() if s in signs),
            key=_degree_sort_key,
        )
        members_tuple = tuple(members)
        directional_trines[direction] = members_tuple
        trine_groups[direction] = NadiTrineGroup(
            direction=direction,
            element=NADI_DIRECTION_ELEMENT[direction],
            purushartha=NADI_DIRECTION_PURUSHARTHA[direction],
            sign_indices=signs,
            sign_names=(RASI_NAMES[signs[0]], RASI_NAMES[signs[1]], RASI_NAMES[signs[2]]),
            planets_by_degree=members_tuple,
        )

    planet_links: dict[str, NadiPlanetLink] = {}
    for p_name in sorted(normalized):
        p_lon = normalized[p_name]
        p_sign = sign_of[p_name]
        p_deg = deg_in_sign_of[p_name]
        direction = NADI_DIRECTIONS_ORDER[p_sign % 4]
        trine_seq = directional_trines[direction]

        trinal_others = tuple(other for other in trine_seq if other != p_name)
        p_idx_in_trine = trine_seq.index(p_name)
        preceding_in_trine = trine_seq[:p_idx_in_trine]
        succeeding_in_trine = trine_seq[p_idx_in_trine + 1 :]

        front_sign = (p_sign + 1) % 12
        behind_sign = (p_sign - 1) % 12
        opp_sign = (p_sign + 6) % 12

        front_2nd = tuple(
            sorted((other for other, s in sign_of.items() if s == front_sign), key=_degree_sort_key)
        )
        behind_12th = tuple(
            sorted((other for other, s in sign_of.items() if s == behind_sign), key=_degree_sort_key)
        )
        opposite_7th = tuple(
            sorted((other for other, s in sign_of.items() if s == opp_sign), key=_degree_sort_key)
        )

        kartari = _classify_kartari(behind_12th, front_2nd)

        planet_links[p_name] = NadiPlanetLink(
            planet=p_name,
            longitude_deg=p_lon,
            sign_index=p_sign,
            sign_name=RASI_NAMES[p_sign],
            degree_in_sign=p_deg,
            direction=direction,
            element=NADI_DIRECTION_ELEMENT[direction],
            purushartha=NADI_DIRECTION_PURUSHARTHA[direction],
            trinal_1_5_9=trinal_others,
            trine_sequence=trine_seq,
            preceding_in_trine=preceding_in_trine,
            succeeding_in_trine=succeeding_in_trine,
            front_2nd=front_2nd,
            behind_12th=behind_12th,
            opposite_7th=opposite_7th,
            planet_kartari=kartari,
        )

    receipt = canonical_hash(
        {
            "engine": "nadi_directional_links",
            "planets": {k: round(v, 9) for k, v in sorted(normalized.items())},
            "directional_trines": directional_trines,
            "kartari": {k: v.planet_kartari for k, v in sorted(planet_links.items())},
        }
    )

    return NadiDirectionalReport(
        directional_trines=directional_trines,
        trine_groups=trine_groups,
        planet_links=planet_links,
        receipt_sha256=receipt,
    )


def compute_bhrigu_progression(
    lagna_lon_deg: float,
    jupiter_lon_deg: float,
    saturn_lon_deg: float,
    age_years: float,
    natal_planet_longitudes: Mapping[str, float] | None = None,
) -> BhriguProgressionReport:
    """Evaluate Bhrigu Chakra progression for Lagna, Jupiter, and Saturn at ``age_years`` (0..120).

    Progression rates per *Bhrigu Nandi Nadi*:
    - Lagna progresses at 1 sign per year: ``(natal_lagna_sign + int(age_years)) % 12``
    - Jupiter progresses at 1 sign per year (12-year cycle):
      ``(natal_jupiter_sign + int(age_years)) % 12``
    - Saturn progresses at 1 sign per 2.5 years (30-year cycle):
      ``(natal_saturn_sign + int(age_years / 2.5)) % 12``
    """
    age = float(age_years)
    if not math.isfinite(age) or age < 0.0 or age > 120.0:
        raise ValueError("age_years must be between 0.0 and 120.0 inclusive")

    lagna_lon = _norm360(lagna_lon_deg)
    jupiter_lon = _norm360(jupiter_lon_deg)
    saturn_lon = _norm360(saturn_lon_deg)

    natal_lagna_sign = int(lagna_lon // 30.0) % 12
    natal_jupiter_sign = int(jupiter_lon // 30.0) % 12
    natal_saturn_sign = int(saturn_lon // 30.0) % 12

    age_int = int(age)
    saturn_steps = int(age / 2.5)

    prog_lagna_sign = (natal_lagna_sign + age_int) % 12
    prog_jupiter_sign = (natal_jupiter_sign + age_int) % 12
    prog_saturn_sign = (natal_saturn_sign + saturn_steps) % 12

    prog_lagna_lon = (lagna_lon + age * 30.0) % 360.0
    prog_jupiter_lon = (jupiter_lon + age * 30.0) % 360.0
    prog_saturn_lon = (saturn_lon + (age / 2.5) * 30.0) % 360.0

    prog_lagna_house = ((prog_lagna_sign - natal_lagna_sign) % 12) + 1
    prog_jupiter_house = ((prog_jupiter_sign - natal_lagna_sign) % 12) + 1
    prog_saturn_house = ((prog_saturn_sign - natal_lagna_sign) % 12) + 1

    jupiter_cycle_number = (age_int // 12) + 1
    saturn_cycle_number = int(age / 30.0) + 1

    # Jupiter aspects/activates 1st, 5th, 7th, and 9th signs from its progressed sign.
    jupiter_active_signs = {
        prog_jupiter_sign,
        (prog_jupiter_sign + 4) % 12,
        (prog_jupiter_sign + 6) % 12,
        (prog_jupiter_sign + 8) % 12,
    }
    # Saturn activates 1st, 5th, 7th, 9th (Nadi trines + opposition) plus 3rd and 10th Parashari aspects.
    saturn_active_signs = {
        prog_saturn_sign,
        (prog_saturn_sign + 2) % 12,
        (prog_saturn_sign + 4) % 12,
        (prog_saturn_sign + 6) % 12,
        (prog_saturn_sign + 8) % 12,
        (prog_saturn_sign + 9) % 12,
    }

    jupiter_houses = {((s - natal_lagna_sign) % 12) + 1 for s in jupiter_active_signs}
    saturn_houses = {((s - natal_lagna_sign) % 12) + 1 for s in saturn_active_signs}

    activated_houses = tuple(sorted({prog_lagna_house, prog_jupiter_house, prog_saturn_house} | jupiter_houses | saturn_houses))
    double_transit_houses = tuple(sorted(jupiter_houses & saturn_houses))

    # Build natal sign registry including lagna, jupiter, saturn and any extra natal planets.
    natal_signs: dict[str, int] = {
        "lagna": natal_lagna_sign,
        "jupiter": natal_jupiter_sign,
        "saturn": natal_saturn_sign,
    }
    if natal_planet_longitudes:
        for raw_name, raw_lon in natal_planet_longitudes.items():
            p_name = _canonical_planet_name(raw_name)
            natal_signs[p_name] = int(_norm360(raw_lon) // 30.0) % 12

    jupiter_triggered = tuple(
        sorted(p for p, s in natal_signs.items() if s in jupiter_active_signs)
    )
    saturn_triggered = tuple(
        sorted(p for p, s in natal_signs.items() if s in saturn_active_signs)
    )

    receipt = canonical_hash(
        {
            "engine": "bhrigu_progression",
            "age_years": round(age, 9),
            "natal_lagna_sign": natal_lagna_sign,
            "natal_jupiter_sign": natal_jupiter_sign,
            "natal_saturn_sign": natal_saturn_sign,
            "progressed_lagna_sign": prog_lagna_sign,
            "progressed_jupiter_sign": prog_jupiter_sign,
            "progressed_saturn_sign": prog_saturn_sign,
            "activated_houses": activated_houses,
            "double_transit_houses": double_transit_houses,
            "jupiter_triggered": jupiter_triggered,
            "saturn_triggered": saturn_triggered,
        }
    )

    return BhriguProgressionReport(
        age_years=age,
        natal_lagna_sign_index=natal_lagna_sign,
        natal_lagna_sign_name=RASI_NAMES[natal_lagna_sign],
        natal_jupiter_sign_index=natal_jupiter_sign,
        natal_jupiter_sign_name=RASI_NAMES[natal_jupiter_sign],
        natal_saturn_sign_index=natal_saturn_sign,
        natal_saturn_sign_name=RASI_NAMES[natal_saturn_sign],
        progressed_lagna_sign_index=prog_lagna_sign,
        progressed_lagna_sign_name=RASI_NAMES[prog_lagna_sign],
        progressed_lagna_lon_deg=prog_lagna_lon,
        progressed_lagna_house=prog_lagna_house,
        progressed_jupiter_sign_index=prog_jupiter_sign,
        progressed_jupiter_sign_name=RASI_NAMES[prog_jupiter_sign],
        progressed_jupiter_lon_deg=prog_jupiter_lon,
        progressed_jupiter_house=prog_jupiter_house,
        jupiter_cycle_number=jupiter_cycle_number,
        progressed_saturn_sign_index=prog_saturn_sign,
        progressed_saturn_sign_name=RASI_NAMES[prog_saturn_sign],
        progressed_saturn_lon_deg=prog_saturn_lon,
        progressed_saturn_house=prog_saturn_house,
        saturn_cycle_number=saturn_cycle_number,
        activated_houses=activated_houses,
        double_transit_houses=double_transit_houses,
        jupiter_triggered_planets=jupiter_triggered,
        saturn_triggered_planets=saturn_triggered,
        receipt_sha256=receipt,
    )


__all__ = [
    "BhriguBinduReport",
    "BhriguBinduTransitAspect",
    "BhriguProgressionReport",
    "CANONICAL_GRAHAS",
    "NADI_DIRECTIONS_ORDER",
    "NADI_DIRECTION_ELEMENT",
    "NADI_DIRECTION_PURUSHARTHA",
    "NADI_DIRECTION_SIGNS",
    "NATURAL_BENEFICS",
    "NATURAL_MALEFICS",
    "NadiDirectionalReport",
    "NadiPlanetLink",
    "NadiTrineGroup",
    "compute_bhrigu_bindu",
    "compute_bhrigu_progression",
    "compute_nadi_directional_links",
]
