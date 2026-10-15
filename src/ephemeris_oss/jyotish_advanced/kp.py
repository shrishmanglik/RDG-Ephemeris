"""Krishnamurti Paddhati (KP) 249 Sub-Lord, Significator, and Ruling Planets engine.

Implements the canonical 249-division KP horary table, five-tier longitudinal lordships
(Sign, Star, Sub, Sub-Sub, Sookshma), fourfold house and planet significators, and the
seven Ruling Planets at the moment of judgment, derived directly from *Krishnamurti
Padhdhati Reader I-VI* (Prof. K.S. Krishnamurti) and *Brihat Parashara Hora Shastra*
Vimshottari proportions.
"""

from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction
import math
from typing import Mapping, Sequence

from ..engine.receipt import canonical_hash

RASI_NAMES: tuple[str, ...] = (
    "Mesha",
    "Vrishabha",
    "Mithuna",
    "Karka",
    "Simha",
    "Kanya",
    "Tula",
    "Vrischika",
    "Dhanus",
    "Makara",
    "Kumbha",
    "Meena",
)

RASI_LORDS: tuple[str, ...] = (
    "mars",
    "venus",
    "mercury",
    "moon",
    "sun",
    "mercury",
    "venus",
    "mars",
    "jupiter",
    "saturn",
    "saturn",
    "jupiter",
)

NAKSHATRA_NAMES: tuple[str, ...] = (
    "Ashwini",
    "Bharani",
    "Krittika",
    "Rohini",
    "Mrigashira",
    "Ardra",
    "Punarvasu",
    "Pushya",
    "Ashlesha",
    "Magha",
    "Purva Phalguni",
    "Uttara Phalguni",
    "Hasta",
    "Chitra",
    "Swati",
    "Vishakha",
    "Anuradha",
    "Jyeshtha",
    "Mula",
    "Purva Ashadha",
    "Uttara Ashadha",
    "Shravana",
    "Dhanishta",
    "Shatabhisha",
    "Purva Bhadrapada",
    "Uttara Bhadrapada",
    "Revati",
)

VIMSHOTTARI_LORDS: tuple[str, ...] = (
    "ketu",
    "venus",
    "sun",
    "moon",
    "mars",
    "rahu",
    "jupiter",
    "saturn",
    "mercury",
)

VIMSHOTTARI_YEARS: Mapping[str, int] = {
    "ketu": 7,
    "venus": 20,
    "sun": 6,
    "moon": 10,
    "mars": 7,
    "rahu": 18,
    "jupiter": 16,
    "saturn": 19,
    "mercury": 17,
}

WEEKDAY_LORDS: tuple[str, ...] = (
    "sun",      # 0 = Sunday (Ravivara)
    "moon",     # 1 = Monday (Somavara)
    "mars",     # 2 = Tuesday (Mangalavara)
    "mercury",  # 3 = Wednesday (Budhavara)
    "jupiter",  # 4 = Thursday (Guruvara)
    "venus",    # 5 = Friday (Shukravara)
    "saturn",   # 6 = Saturday (Shanivara)
)

WEEKDAY_NAME_TO_INDEX: Mapping[str, int] = {
    "sunday": 0,
    "sun": 0,
    "ravivara": 0,
    "monday": 1,
    "moon": 1,
    "mon": 1,
    "somavara": 1,
    "tuesday": 2,
    "tue": 2,
    "mangalavara": 2,
    "wednesday": 3,
    "wed": 3,
    "budhavara": 3,
    "thursday": 4,
    "thu": 4,
    "guruvara": 4,
    "friday": 5,
    "fri": 5,
    "shukravara": 5,
    "saturday": 6,
    "sat": 6,
    "shanivara": 6,
}

KP_PLANETS: tuple[str, ...] = (
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


@dataclass(frozen=True)
class KpHoraryEntry:
    """One entry in the canonical 249-division KP Horary Sub-Table."""

    number: int
    start_deg: float
    end_deg: float
    span_deg: float
    rasi_index: int
    rasi_name: str
    nakshatra_index: int
    nakshatra_name: str
    sign_lord: str
    star_lord: str
    sub_lord: str
    split_across_sign: bool


@dataclass(frozen=True)
class KpPositionLords:
    """Five-level KP hierarchy and 249 horary number for a sidereal longitude."""

    longitude_deg: float
    rasi_index: int
    rasi_name: str
    degree_in_rasi: float
    nakshatra_index: int
    nakshatra_name: str
    pada: int
    sign_lord: str
    star_lord: str
    sub_lord: str
    sub_sub_lord: str
    sookshma_sub_lord: str
    horary_number_249: int
    receipt_sha256: str


@dataclass(frozen=True)
class KpHouseSignification:
    """Fourfold KP significators and cusp hierarchy for one Bhava (house)."""

    house: int
    cusp_longitude_deg: float
    cusp_sign_lord: str
    cusp_star_lord: str
    cusp_sub_lord: str
    level_1_star_of_occupants: tuple[str, ...]
    level_2_occupants: tuple[str, ...]
    level_3_star_of_cusp_lord: tuple[str, ...]
    level_4_cusp_lord: tuple[str, ...]
    combined_significators: tuple[str, ...]


@dataclass(frozen=True)
class KpPlanetSignification:
    """Fourfold KP house significations for a single planet."""

    planet: str
    longitude_deg: float
    occupied_house: int
    owned_houses: tuple[int, ...]
    star_lord: str
    sub_lord: str
    level_1_via_star_lord_occupancy: tuple[int, ...]
    level_2_own_occupancy: tuple[int, ...]
    level_3_via_star_lord_ownership: tuple[int, ...]
    level_4_own_ownership: tuple[int, ...]
    all_signified_houses: tuple[int, ...]
    sub_lord_signified_houses: tuple[int, ...]


@dataclass(frozen=True)
class KpSignificatorReport:
    """Complete KP house and planetary fourfold significator table."""

    houses: tuple[KpHouseSignification, ...]
    planets: Mapping[str, KpPlanetSignification]
    receipt_sha256: str


@dataclass(frozen=True)
class KpRulingPlanets:
    """Seven KP Ruling Planets at the moment of judgment."""

    weekday_index: int
    day_lord: str
    ascendant_lon_deg: float
    ascendant_sign_lord: str
    ascendant_star_lord: str
    ascendant_sub_lord: str
    moon_lon_deg: float
    moon_sign_lord: str
    moon_star_lord: str
    moon_sub_lord: str
    ruling_planets_7: tuple[str, ...]
    unique_ruling_planets: tuple[str, ...]
    receipt_sha256: str


def _normalize_lon(lon_deg: float) -> float:
    val = float(lon_deg)
    if not math.isfinite(val):
        raise ValueError("sidereal longitude must be finite")
    return val % 360.0


def _vimshottari_cycle_from(start_lord: str) -> tuple[str, ...]:
    idx = VIMSHOTTARI_LORDS.index(start_lord)
    return VIMSHOTTARI_LORDS[idx:] + VIMSHOTTARI_LORDS[:idx]


def _build_kp_sub_table_249() -> tuple[KpHoraryEntry, ...]:
    """Construct the exact 249-entry KP sub-table using exact rational arithmetic."""

    entries: list[KpHoraryEntry] = []
    cursor = Fraction(0, 1)
    number = 1

    for nak_idx in range(27):
        star_lord = VIMSHOTTARI_LORDS[nak_idx % 9]
        nak_name = NAKSHATRA_NAMES[nak_idx]
        sub_sequence = _vimshottari_cycle_from(star_lord)

        for sub_lord in sub_sequence:
            # Each Nakshatra is 40/3 deg; sub span is (40/3) * (years / 120) = years / 9 deg.
            sub_span = Fraction(VIMSHOTTARI_YEARS[sub_lord], 9)
            sub_start = cursor
            sub_end = cursor + sub_span
            cursor = sub_end

            start_rasi = int(sub_start // 30)
            # If sub_end lands exactly on a multiple of 30, it belongs to the sign ending there.
            end_rasi = int((sub_end - Fraction(1, 10**9)) // 30)

            if start_rasi == end_rasi:
                entries.append(
                    KpHoraryEntry(
                        number=number,
                        start_deg=float(sub_start),
                        end_deg=float(sub_end),
                        span_deg=float(sub_span),
                        rasi_index=start_rasi,
                        rasi_name=RASI_NAMES[start_rasi],
                        nakshatra_index=nak_idx,
                        nakshatra_name=nak_name,
                        sign_lord=RASI_LORDS[start_rasi],
                        star_lord=star_lord,
                        sub_lord=sub_lord,
                        split_across_sign=False,
                    )
                )
                number += 1
            else:
                boundary = Fraction((start_rasi + 1) * 30, 1)
                span_first = boundary - sub_start
                span_second = sub_end - boundary
                entries.append(
                    KpHoraryEntry(
                        number=number,
                        start_deg=float(sub_start),
                        end_deg=float(boundary),
                        span_deg=float(span_first),
                        rasi_index=start_rasi,
                        rasi_name=RASI_NAMES[start_rasi],
                        nakshatra_index=nak_idx,
                        nakshatra_name=nak_name,
                        sign_lord=RASI_LORDS[start_rasi],
                        star_lord=star_lord,
                        sub_lord=sub_lord,
                        split_across_sign=True,
                    )
                )
                number += 1
                entries.append(
                    KpHoraryEntry(
                        number=number,
                        start_deg=float(boundary),
                        end_deg=float(sub_end),
                        span_deg=float(span_second),
                        rasi_index=end_rasi,
                        rasi_name=RASI_NAMES[end_rasi],
                        nakshatra_index=nak_idx,
                        nakshatra_name=nak_name,
                        sign_lord=RASI_LORDS[end_rasi],
                        star_lord=star_lord,
                        sub_lord=sub_lord,
                        split_across_sign=True,
                    )
                )
                number += 1

    return tuple(entries)


_KP_TABLE_249: tuple[KpHoraryEntry, ...] = _build_kp_sub_table_249()


def kp_sub_table_249() -> tuple[KpHoraryEntry, ...]:
    """Return the immutable 249-entry KP Horary Sub-Table."""

    return _KP_TABLE_249


def kp_horary_entry(number: int) -> KpHoraryEntry:
    """Return the KP Horary Sub-Table entry for horary number ``1 <= number <= 249``."""

    if not isinstance(number, int) or isinstance(number, bool) or not 1 <= number <= 249:
        raise ValueError(f"KP horary number must be an integer in 1..249, got {number!r}")
    return _KP_TABLE_249[number - 1]


def _subdivide_vimshottari(offset: float, total_span: float, start_lord: str) -> tuple[str, float, float]:
    """Locate the Vimshottari sub-division lord and return (lord, inner_offset, inner_span)."""

    clamped = min(max(offset, 0.0), max(total_span - 1e-15, 0.0))
    acc = 0.0
    sequence = _vimshottari_cycle_from(start_lord)
    for idx, lord in enumerate(sequence):
        part_span = total_span * (VIMSHOTTARI_YEARS[lord] / 120.0)
        next_acc = acc + part_span
        if clamped < next_acc or idx == len(sequence) - 1:
            return lord, max(0.0, clamped - acc), part_span
        acc = next_acc
    return sequence[-1], 0.0, total_span * (VIMSHOTTARI_YEARS[sequence[-1]] / 120.0)


def kp_coordinate_lords(sidereal_lon_deg: float) -> KpPositionLords:
    """Compute Sign, Star, Sub, Sub-Sub, Sookshma lords and 1..249 horary number."""

    lon = _normalize_lon(sidereal_lon_deg)
    rasi_idx = min(int(lon // 30.0), 11)
    degree_in_rasi = lon - rasi_idx * 30.0

    nak_span = 40.0 / 3.0
    nak_idx = min(int(lon // nak_span), 26)
    offset_in_nak = lon - nak_idx * nak_span
    pada = min(int(offset_in_nak // (10.0 / 3.0)) + 1, 4)

    sign_lord = RASI_LORDS[rasi_idx]
    star_lord = VIMSHOTTARI_LORDS[nak_idx % 9]

    sub_lord, offset_in_sub, sub_span = _subdivide_vimshottari(offset_in_nak, nak_span, star_lord)
    sub_sub_lord, offset_in_ss, ss_span = _subdivide_vimshottari(offset_in_sub, sub_span, sub_lord)
    sookshma_lord, _, _ = _subdivide_vimshottari(offset_in_ss, ss_span, sub_sub_lord)

    horary_num = 249
    for entry in _KP_TABLE_249:
        if entry.start_deg <= lon < entry.end_deg or (entry.number == 249 and math.isclose(lon, 360.0)):
            horary_num = entry.number
            break

    payload = {
        "longitude_deg": round(lon, 10),
        "rasi_index": rasi_idx,
        "nakshatra_index": nak_idx,
        "pada": pada,
        "sign_lord": sign_lord,
        "star_lord": star_lord,
        "sub_lord": sub_lord,
        "sub_sub_lord": sub_sub_lord,
        "sookshma_sub_lord": sookshma_lord,
        "horary_number_249": horary_num,
    }
    return KpPositionLords(
        longitude_deg=lon,
        rasi_index=rasi_idx,
        rasi_name=RASI_NAMES[rasi_idx],
        degree_in_rasi=degree_in_rasi,
        nakshatra_index=nak_idx,
        nakshatra_name=NAKSHATRA_NAMES[nak_idx],
        pada=pada,
        sign_lord=sign_lord,
        star_lord=star_lord,
        sub_lord=sub_lord,
        sub_sub_lord=sub_sub_lord,
        sookshma_sub_lord=sookshma_lord,
        horary_number_249=horary_num,
        receipt_sha256=canonical_hash(payload),
    )


def _house_of_longitude(lon_deg: float, cusps: Sequence[float]) -> int:
    """Return 1-based house index [1..12] occupied by ``lon_deg`` given 12 house cusps."""

    lon = _normalize_lon(lon_deg)
    for idx in range(12):
        start = _normalize_lon(cusps[idx])
        end = _normalize_lon(cusps[(idx + 1) % 12])
        if start <= end:
            if start <= lon < end:
                return idx + 1
        else:
            if lon >= start or lon < end:
                return idx + 1
    return 1


def kp_fourfold_significators(
    planet_lons: Mapping[str, float],
    house_cusp_lons: Sequence[float],
) -> KpSignificatorReport:
    """Compute the fourfold KP house and planet significator tables.

    Hierarchy of signification (strongest to weakest):
    - Level 1: Planets posited in the constellation (Nakshatra) of the occupants of that house.
    - Level 2: Planets posited (occupying) in that house.
    - Level 3: Planets posited in the constellation (Nakshatra) of the house cusp sign lord.
    - Level 4: The house cusp sign lord itself.
    """

    if len(house_cusp_lons) != 12:
        raise ValueError(f"house_cusp_lons must contain 12 cusps, got {len(house_cusp_lons)}")

    normalized_planets: dict[str, float] = {}
    for body in KP_PLANETS:
        if body not in planet_lons:
            raise ValueError(f"missing required KP planet {body!r} in planet_lons")
        normalized_planets[body] = _normalize_lon(planet_lons[body])

    cusps = tuple(_normalize_lon(c) for c in house_cusp_lons)
    planet_lords = {body: kp_coordinate_lords(lon) for body, lon in normalized_planets.items()}
    cusp_lords = tuple(kp_coordinate_lords(c) for c in cusps)

    planet_house = {body: _house_of_longitude(lon, cusps) for body, lon in normalized_planets.items()}

    house_occupants: dict[int, list[str]] = {h: [] for h in range(1, 13)}
    for body in KP_PLANETS:
        house_occupants[planet_house[body]].append(body)

    owned_houses_by_planet: dict[str, list[int]] = {body: [] for body in KP_PLANETS}
    for h_idx, c_lord in enumerate(cusp_lords, start=1):
        owned_houses_by_planet[c_lord.sign_lord].append(h_idx)

    # Nodes (Rahu/Ketu) also act as agents of their sign dispositor and occupants/owners as standard.
    houses_out: list[KpHouseSignification] = []
    for h_idx in range(1, 13):
        c_info = cusp_lords[h_idx - 1]
        occupants = tuple(house_occupants[h_idx])
        occupant_set = set(occupants)

        level_1 = tuple(
            body for body in KP_PLANETS if planet_lords[body].star_lord in occupant_set
        )
        level_2 = occupants
        level_3 = tuple(
            body for body in KP_PLANETS if planet_lords[body].star_lord == c_info.sign_lord
        )
        level_4 = (c_info.sign_lord,)

        combined: list[str] = []
        for group in (level_1, level_2, level_3, level_4):
            for body in group:
                if body not in combined:
                    combined.append(body)

        houses_out.append(
            KpHouseSignification(
                house=h_idx,
                cusp_longitude_deg=cusps[h_idx - 1],
                cusp_sign_lord=c_info.sign_lord,
                cusp_star_lord=c_info.star_lord,
                cusp_sub_lord=c_info.sub_lord,
                level_1_star_of_occupants=level_1,
                level_2_occupants=level_2,
                level_3_star_of_cusp_lord=level_3,
                level_4_cusp_lord=level_4,
                combined_significators=tuple(combined),
            )
        )

    planets_temp: dict[str, KpPlanetSignification] = {}
    for body in KP_PLANETS:
        p_info = planet_lords[body]
        star_lord = p_info.star_lord
        l1_houses = (planet_house[star_lord],)
        l2_houses = (planet_house[body],)
        l3_houses = tuple(owned_houses_by_planet[star_lord])
        l4_houses = tuple(owned_houses_by_planet[body])

        # For Rahu and Ketu, include their sign dispositor's owned houses in Level 4 if empty.
        if body in {"rahu", "ketu"} and not l4_houses:
            l4_houses = tuple(owned_houses_by_planet[p_info.sign_lord])

        all_houses: list[int] = []
        for h_group in (l1_houses, l2_houses, l3_houses, l4_houses):
            for h_num in h_group:
                if h_num not in all_houses:
                    all_houses.append(h_num)

        planets_temp[body] = KpPlanetSignification(
            planet=body,
            longitude_deg=normalized_planets[body],
            occupied_house=planet_house[body],
            owned_houses=l4_houses,
            star_lord=star_lord,
            sub_lord=p_info.sub_lord,
            level_1_via_star_lord_occupancy=l1_houses,
            level_2_own_occupancy=l2_houses,
            level_3_via_star_lord_ownership=l3_houses,
            level_4_own_ownership=l4_houses,
            all_signified_houses=tuple(all_houses),
            sub_lord_signified_houses=(),
        )

    planets_final: dict[str, KpPlanetSignification] = {}
    for body, sig in planets_temp.items():
        sub_houses = planets_temp[sig.sub_lord].all_signified_houses
        planets_final[body] = KpPlanetSignification(
            planet=sig.planet,
            longitude_deg=sig.longitude_deg,
            occupied_house=sig.occupied_house,
            owned_houses=sig.owned_houses,
            star_lord=sig.star_lord,
            sub_lord=sig.sub_lord,
            level_1_via_star_lord_occupancy=sig.level_1_via_star_lord_occupancy,
            level_2_own_occupancy=sig.level_2_own_occupancy,
            level_3_via_star_lord_ownership=sig.level_3_via_star_lord_ownership,
            level_4_own_ownership=sig.level_4_own_ownership,
            all_signified_houses=sig.all_signified_houses,
            sub_lord_signified_houses=sub_houses,
        )

    receipt_payload = {
        "houses": [
            {
                "house": h.house,
                "cusp_sub_lord": h.cusp_sub_lord,
                "combined": list(h.combined_significators),
            }
            for h in houses_out
        ],
        "planets": {
            b: list(p.all_signified_houses) for b, p in sorted(planets_final.items())
        },
    }
    return KpSignificatorReport(
        houses=tuple(houses_out),
        planets=planets_final,
        receipt_sha256=canonical_hash(receipt_payload),
    )


def kp_ruling_planets(
    weekday_index: int | str,
    moon_lon_deg: float,
    ascendant_lon_deg: float,
) -> KpRulingPlanets:
    """Compute the 7 KP Ruling Planets (Ascendant Sign/Star/Sub, Moon Sign/Star/Sub, Day Lord).

    ``weekday_index`` uses standard Vedic/KP indexing ``0 = Sunday .. 6 = Saturday``
    or accepts English/Sanskrit weekday names (e.g. ``"sunday"``, ``"thursday"``).
    """

    if isinstance(weekday_index, str):
        key = weekday_index.strip().lower()
        if key not in WEEKDAY_NAME_TO_INDEX:
            raise ValueError(f"unknown weekday name {weekday_index!r}")
        w_idx = WEEKDAY_NAME_TO_INDEX[key]
    elif isinstance(weekday_index, int) and not isinstance(weekday_index, bool) and 0 <= weekday_index <= 6:
        w_idx = weekday_index
    else:
        raise ValueError(f"weekday_index must be 0..6 (0=Sunday) or a weekday name, got {weekday_index!r}")

    day_lord = WEEKDAY_LORDS[w_idx]
    asc_info = kp_coordinate_lords(ascendant_lon_deg)
    moon_info = kp_coordinate_lords(moon_lon_deg)

    rp_7 = (
        asc_info.sign_lord,
        asc_info.star_lord,
        asc_info.sub_lord,
        moon_info.sign_lord,
        moon_info.star_lord,
        moon_info.sub_lord,
        day_lord,
    )
    unique_rp: list[str] = []
    for lord in rp_7:
        if lord not in unique_rp:
            unique_rp.append(lord)

    payload = {
        "weekday_index": w_idx,
        "day_lord": day_lord,
        "ascendant_lon_deg": round(asc_info.longitude_deg, 10),
        "moon_lon_deg": round(moon_info.longitude_deg, 10),
        "ruling_planets_7": list(rp_7),
    }
    return KpRulingPlanets(
        weekday_index=w_idx,
        day_lord=day_lord,
        ascendant_lon_deg=asc_info.longitude_deg,
        ascendant_sign_lord=asc_info.sign_lord,
        ascendant_star_lord=asc_info.star_lord,
        ascendant_sub_lord=asc_info.sub_lord,
        moon_lon_deg=moon_info.longitude_deg,
        moon_sign_lord=moon_info.sign_lord,
        moon_star_lord=moon_info.star_lord,
        moon_sub_lord=moon_info.sub_lord,
        ruling_planets_7=rp_7,
        unique_ruling_planets=tuple(unique_rp),
        receipt_sha256=canonical_hash(payload),
    )
