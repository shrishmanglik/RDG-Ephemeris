"""Clean-room Bhinna Ashtakavarga (BAV), Sarvashtakavarga (SAV), Shodhana reductions, Pindas, and Gochara Vedha.

Mathematical formulations follow *Brihat Parashara Hora Shastra* (Chapters 66-72)
and *Phaladeepika* (Chapter 26):
- Exact BPHS benefic bindu matrices for all 7 planets (totalling 337 bindus:
  Sun 48, Moon 49, Mars 39, Mercury 54, Jupiter 56, Venus 52, Saturn 39) plus Lagna (49).
- Sarvashtakavarga (SAV) 12-sign totals.
- Trikona Shodhana (trinal reduction across Fire, Earth, Air, Water triplicities)
  and Ekadhipatya Shodhana (dual-sign ownership reduction with planetary occupancy).
- Rasi Pinda, Graha Pinda, and Shodhya Pinda with classical Gunakara multipliers.
- Gochara Transit Vedha evaluator with classical Father-Son exemptions
  (Sun-Saturn and Moon-Mercury).
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Final, Mapping

from .nakshatra import RASI_NAMES, normalize_degrees
from .shadbala import SEVEN_GRAHAS

ASHTAKAVARGA_CONTRIBUTORS: Final[tuple[str, ...]] = (
    "Sun",
    "Moon",
    "Mars",
    "Mercury",
    "Jupiter",
    "Venus",
    "Saturn",
    "Lagna",
)

# Classical BPHS Chapter 66 benefic house offsets (1-based: 1..12 from each contributor)
BAV_BENEFIC_HOUSES: Final[Mapping[str, Mapping[str, tuple[int, ...]]]] = {
    "Sun": {  # Total = 48
        "Sun": (1, 2, 4, 7, 8, 9, 10, 11),
        "Moon": (3, 6, 10, 11),
        "Mars": (1, 2, 4, 7, 8, 9, 10, 11),
        "Mercury": (3, 5, 6, 9, 10, 11, 12),
        "Jupiter": (5, 6, 9, 11),
        "Venus": (6, 7, 12),
        "Saturn": (1, 2, 4, 7, 8, 9, 10, 11),
        "Lagna": (3, 4, 6, 10, 11, 12),
    },
    "Moon": {  # Total = 49
        "Sun": (3, 6, 7, 8, 10, 11),
        "Moon": (1, 3, 6, 7, 10, 11),
        "Mars": (2, 3, 5, 6, 9, 10, 11),
        "Mercury": (1, 3, 4, 5, 7, 8, 10, 11),
        "Jupiter": (1, 4, 7, 8, 10, 11, 12),
        "Venus": (3, 4, 5, 7, 9, 10, 11),
        "Saturn": (3, 5, 6, 11),
        "Lagna": (3, 6, 10, 11),
    },
    "Mars": {  # Total = 39
        "Sun": (3, 5, 6, 10, 11),
        "Moon": (3, 6, 11),
        "Mars": (1, 2, 4, 7, 8, 10, 11),
        "Mercury": (3, 5, 6, 11),
        "Jupiter": (6, 10, 11, 12),
        "Venus": (6, 8, 11, 12),
        "Saturn": (1, 4, 7, 8, 9, 10, 11),
        "Lagna": (1, 3, 6, 10, 11),
    },
    "Mercury": {  # Total = 54
        "Sun": (5, 6, 9, 11, 12),
        "Moon": (2, 4, 6, 8, 10, 11),
        "Mars": (1, 2, 4, 7, 8, 9, 10, 11),
        "Mercury": (1, 3, 5, 6, 9, 10, 11, 12),
        "Jupiter": (6, 8, 11, 12),
        "Venus": (1, 2, 3, 4, 5, 8, 9, 11),
        "Saturn": (1, 2, 4, 7, 8, 9, 10, 11),
        "Lagna": (1, 2, 4, 6, 8, 10, 11),
    },
    "Jupiter": {  # Total = 56
        "Sun": (1, 2, 3, 4, 7, 8, 9, 10, 11),
        "Moon": (2, 5, 7, 9, 11),
        "Mars": (1, 2, 4, 7, 8, 10, 11),
        "Mercury": (1, 2, 4, 5, 6, 9, 10, 11),
        "Jupiter": (1, 2, 3, 4, 7, 8, 10, 11),
        "Venus": (2, 5, 6, 9, 10, 11),
        "Saturn": (3, 5, 6, 12),
        "Lagna": (1, 2, 4, 5, 6, 7, 9, 10, 11),
    },
    "Venus": {  # Total = 52
        "Sun": (8, 11, 12),
        "Moon": (1, 2, 3, 4, 5, 8, 9, 11, 12),
        "Mars": (3, 5, 6, 9, 11, 12),
        "Mercury": (3, 5, 6, 9, 11),
        "Jupiter": (5, 8, 9, 10, 11),
        "Venus": (1, 2, 3, 4, 5, 8, 9, 10, 11),
        "Saturn": (3, 4, 5, 8, 9, 10, 11),
        "Lagna": (1, 2, 3, 4, 5, 8, 9, 11),
    },
    "Saturn": {  # Total = 39
        "Sun": (1, 2, 4, 7, 8, 10, 11),
        "Moon": (3, 6, 11),
        "Mars": (3, 5, 6, 10, 11, 12),
        "Mercury": (6, 8, 9, 10, 11, 12),
        "Jupiter": (5, 6, 11, 12),
        "Venus": (6, 11, 12),
        "Saturn": (3, 5, 6, 11),
        "Lagna": (1, 3, 4, 6, 10, 11),
    },
    "Lagna": {  # Total = 49
        "Sun": (3, 4, 6, 10, 11, 12),
        "Moon": (3, 6, 10, 11, 12),
        "Mars": (1, 3, 6, 10, 11),
        "Mercury": (1, 2, 4, 6, 8, 10, 11),
        "Jupiter": (1, 2, 4, 5, 6, 7, 9, 10, 11),
        "Venus": (1, 2, 3, 4, 5, 8, 9, 11),
        "Saturn": (1, 3, 4, 6, 10, 11),
        "Lagna": (3, 6, 10),
    },
}

EXPECTED_BAV_TOTALS: Final[Mapping[str, int]] = {
    "Sun": 48,
    "Moon": 49,
    "Mars": 39,
    "Mercury": 54,
    "Jupiter": 56,
    "Venus": 52,
    "Saturn": 39,
    "Lagna": 49,
}
EXPECTED_SAV_TOTAL: Final[int] = 337

# Classical Rasi Gunakaras (Zodiacal Sign Multipliers for Aries=0 .. Pisces=11)
RASI_GUNAKARAS: Final[tuple[int, ...]] = (7, 10, 8, 4, 10, 5, 7, 8, 9, 5, 11, 12)

# Classical Graha Gunakaras (Planetary Multipliers)
GRAHA_GUNAKARAS: Final[Mapping[str, int]] = {
    "Sun": 5,
    "Moon": 5,
    "Mars": 8,
    "Mercury": 5,
    "Jupiter": 10,
    "Venus": 7,
    "Saturn": 5,
}

# Dual-sign ownership pairs for Ekadhipatya Shodhana: (sign_a, sign_b)
DUAL_OWNERSHIP_PAIRS: Final[tuple[tuple[int, int], ...]] = (
    (0, 7),   # Mars: Aries & Scorpio
    (1, 6),   # Venus: Taurus & Libra
    (2, 5),   # Mercury: Gemini & Virgo
    (8, 11),  # Jupiter: Sagittarius & Pisces
    (9, 10),  # Saturn: Capricorn & Aquarius
)

# Classical Gochara benefic houses from Natal Moon and their corresponding Vedha houses
GOCHARA_VEDHA_TABLE: Final[Mapping[str, Mapping[int, int]]] = {
    "Sun": {3: 9, 6: 12, 10: 4, 11: 5},
    "Moon": {1: 5, 3: 9, 6: 12, 7: 2, 10: 4, 11: 8},
    "Mars": {3: 12, 6: 9, 11: 5},
    "Mercury": {2: 5, 4: 3, 6: 9, 8: 1, 10: 8, 11: 12},
    "Jupiter": {2: 12, 5: 4, 7: 3, 9: 10, 11: 8},
    "Venus": {1: 8, 2: 7, 3: 1, 4: 10, 5: 9, 8: 5, 9: 11, 11: 6, 12: 3},
    "Saturn": {3: 12, 6: 9, 11: 5},
    "Rahu": {3: 9, 6: 12, 10: 4, 11: 5},
    "Ketu": {3: 9, 6: 12, 10: 4, 11: 5},
}

# Classical Father-Son pairs exempt from mutual Vedha obstruction (*Phaladeepika* Ch. 26)
VEDHA_EXEMPT_PAIRS: Final[frozenset[frozenset[str]]] = frozenset({
    frozenset({"Sun", "Saturn"}),
    frozenset({"Moon", "Mercury"}),
})


@dataclass(frozen=True)
class BhinnaAshtakavargaTable:
    """Bhinna Ashtakavarga (BAV) table for one planet or Lagna across 12 signs."""

    recipient: str
    sign_bindus: tuple[int, ...]
    total_bindus: int
    contributor_matrix: Mapping[str, tuple[int, ...]]
    trikona_reduced: tuple[int, ...]
    ekadhipatya_reduced: tuple[int, ...]
    rasi_pinda: int
    graha_pinda: int
    shodhya_pinda: int


@dataclass(frozen=True)
class AshtakavargaAnalysis:
    """Complete BAV, SAV (337 bindus), Shodhana reductions, and Shodhya Pindas."""

    bhinna_tables: Mapping[str, BhinnaAshtakavargaTable]
    sarvashtakavarga_7: tuple[int, ...]
    sarvashtakavarga_7_total: int
    sarvashtakavarga_with_lagna: tuple[int, ...]
    sarvashtakavarga_trikona_reduced: tuple[int, ...]
    sarvashtakavarga_ekadhipatya_reduced: tuple[int, ...]


@dataclass(frozen=True)
class GocharaPlanetTransit:
    """Transit evaluation for one planet relative to natal Moon with Vedha check."""

    planet: str
    transit_sign_index: int
    transit_sign_name: str
    house_from_moon: int
    is_naturally_benefic_house: bool
    vedha_house_from_moon: int | None
    obstructing_planets: tuple[str, ...]
    exempt_planets: tuple[str, ...]
    is_obstructed_by_vedha: bool
    net_favorable: bool
    bav_bindus_in_sign: int | None = None
    sav_bindus_in_sign: int | None = None


def trikona_shodhana(sign_bindus: tuple[int, ...]) -> tuple[int, ...]:
    """Perform Trikona Shodhana (trinal reduction) across the 4 elemental triplicities.

    For each triplicity `(s, s+4, s+8)`, subtract `min(v[s], v[s+4], v[s+8])` from all three signs.
    """
    if len(sign_bindus) != 12:
        raise ValueError("sign_bindus must have 12 sign entries")
    reduced = list(sign_bindus)
    for element_base in range(4):
        idx0, idx1, idx2 = element_base, element_base + 4, element_base + 8
        m = min(reduced[idx0], reduced[idx1], reduced[idx2])
        reduced[idx0] -= m
        reduced[idx1] -= m
        reduced[idx2] -= m
    return tuple(reduced)


def ekadhipatya_shodhana(
    trikona_reduced: tuple[int, ...],
    occupied_signs: frozenset[int],
) -> tuple[int, ...]:
    """Perform Ekadhipatya Shodhana (dual-sign ownership reduction) per BPHS Chapter 70.

    Rules for each dual-lord sign pair `(s_a, s_b)` with values `(a, b)`:
    1. If `a == 0` or `b == 0`, no change.
    2. If both `s_a` and `s_b` are occupied by planets, no change.
    3. If one sign is occupied (`v_occ`) and the other is unoccupied (`v_unocc`):
       - If `v_unocc <= v_occ`: the unoccupied sign becomes `0`.
       - If `v_unocc > v_occ`: subtract `v_occ` from `v_unocc` (`v_unocc -= v_occ`).
    4. If neither sign is occupied:
       - If `a == b`: both become `0`.
       - If `a != b`: replace the larger with `min(a, b)` and set the smaller to `0`.
    """
    if len(trikona_reduced) != 12:
        raise ValueError("trikona_reduced must have 12 sign entries")
    out = list(trikona_reduced)
    for sa, sb in DUAL_OWNERSHIP_PAIRS:
        va, vb = out[sa], out[sb]
        if va == 0 or vb == 0:
            continue
        occ_a = sa in occupied_signs
        occ_b = sb in occupied_signs
        if occ_a and occ_b:
            continue
        if occ_a and not occ_b:
            out[sb] = 0 if vb <= va else (vb - va)
        elif occ_b and not occ_a:
            out[sa] = 0 if va <= vb else (va - vb)
        else:
            if va == vb:
                out[sa] = 0
                out[sb] = 0
            elif va > vb:
                out[sa] = vb
                out[sb] = 0
            else:
                out[sb] = va
                out[sa] = 0
    return tuple(out)


def compute_pindas(
    shodhana_bindus: tuple[int, ...],
    planet_signs: Mapping[str, int],
) -> tuple[int, int, int]:
    """Compute `(rasi_pinda, graha_pinda, shodhya_pinda)` from twice-reduced bindus."""
    rasi_pinda = sum(shodhana_bindus[s] * RASI_GUNAKARAS[s] for s in range(12))
    graha_pinda = sum(
        shodhana_bindus[planet_signs[g]] * GRAHA_GUNAKARAS[g]
        for g in SEVEN_GRAHAS
        if g in planet_signs
    )
    return rasi_pinda, graha_pinda, rasi_pinda + graha_pinda


def compute_ashtakavarga(
    planet_longitudes: Mapping[str, float],
    lagna_lon_deg: float,
) -> AshtakavargaAnalysis:
    """Compute full Bhinna Ashtakavarga (BAV), Sarvashtakavarga (SAV), Shodhana reductions, and Pindas."""
    norm_lons = {k.strip().capitalize(): normalize_degrees(v) for k, v in planet_longitudes.items()}
    for g in SEVEN_GRAHAS:
        if g not in norm_lons:
            raise ValueError(f"Missing longitude for {g!r} in planet_longitudes")

    contributor_signs: dict[str, int] = {
        g: min(int(norm_lons[g] // 30.0), 11) for g in SEVEN_GRAHAS
    }
    contributor_signs["Lagna"] = min(int(normalize_degrees(lagna_lon_deg) // 30.0), 11)
    occupied_7 = frozenset(contributor_signs[g] for g in SEVEN_GRAHAS)

    bhinna_tables: dict[str, BhinnaAshtakavargaTable] = {}
    for recipient, matrix_spec in BAV_BENEFIC_HOUSES.items():
        contrib_rows: dict[str, tuple[int, ...]] = {}
        sign_totals = [0] * 12
        for contrib_name in ASHTAKAVARGA_CONTRIBUTORS:
            base_sign = contributor_signs[contrib_name]
            row = [0] * 12
            for house_offset in matrix_spec[contrib_name]:
                target_sign = (base_sign + house_offset - 1) % 12
                row[target_sign] = 1
                sign_totals[target_sign] += 1
            contrib_rows[contrib_name] = tuple(row)

        raw_tuple = tuple(sign_totals)
        trik = trikona_shodhana(raw_tuple)
        ekadh = ekadhipatya_shodhana(trik, occupied_7)
        r_pinda, g_pinda, s_pinda = compute_pindas(ekadh, contributor_signs)

        bhinna_tables[recipient] = BhinnaAshtakavargaTable(
            recipient=recipient,
            sign_bindus=raw_tuple,
            total_bindus=sum(raw_tuple),
            contributor_matrix=contrib_rows,
            trikona_reduced=trik,
            ekadhipatya_reduced=ekadh,
            rasi_pinda=r_pinda,
            graha_pinda=g_pinda,
            shodhya_pinda=s_pinda,
        )

    sav_7 = tuple(
        sum(bhinna_tables[g].sign_bindus[s] for g in SEVEN_GRAHAS)
        for s in range(12)
    )
    sav_8 = tuple(
        sav_7[s] + bhinna_tables["Lagna"].sign_bindus[s]
        for s in range(12)
    )
    sav_trik = trikona_shodhana(sav_7)
    sav_ekadh = ekadhipatya_shodhana(sav_trik, occupied_7)

    return AshtakavargaAnalysis(
        bhinna_tables=bhinna_tables,
        sarvashtakavarga_7=sav_7,
        sarvashtakavarga_7_total=sum(sav_7),
        sarvashtakavarga_with_lagna=sav_8,
        sarvashtakavarga_trikona_reduced=sav_trik,
        sarvashtakavarga_ekadhipatya_reduced=sav_ekadh,
    )


def evaluate_gochara_vedha(
    natal_moon_lon_deg: float,
    transit_longitudes: Mapping[str, float],
    *,
    ashtakavarga: AshtakavargaAnalysis | None = None,
) -> Mapping[str, GocharaPlanetTransit]:
    """Evaluate Gochara (planetary transit) benefic placement and Vedha obstruction from natal Moon.

    Enforces classical Father-Son exemptions (*Phaladeepika* Ch. 26):
    - Sun and Saturn never cause Vedha to each other.
    - Moon and Mercury never cause Vedha to each other.
    """
    moon_sign = min(int(normalize_degrees(natal_moon_lon_deg) // 30.0), 11)
    norm_transits = {k.strip().capitalize(): normalize_degrees(v) for k, v in transit_longitudes.items()}

    transit_houses: dict[str, int] = {}
    transit_signs: dict[str, int] = {}
    for p, lon in norm_transits.items():
        s_idx = min(int(lon // 30.0), 11)
        transit_signs[p] = s_idx
        transit_houses[p] = ((s_idx - moon_sign) % 12) + 1

    results: dict[str, GocharaPlanetTransit] = {}
    for p, h_from_moon in transit_houses.items():
        vedha_map = GOCHARA_VEDHA_TABLE.get(p, {})
        is_benefic_house = h_from_moon in vedha_map
        vedha_house = vedha_map.get(h_from_moon)

        obstructors: list[str] = []
        exempted: list[str] = []
        if is_benefic_house and vedha_house is not None:
            for other_p, other_h in transit_houses.items():
                if other_p == p:
                    continue
                # Classical rule: Rahu and Ketu do not obstruct physical planets in standard 7-planet Vedha
                # unless explicitly checked; Father-Son pairs are exempt.
                if other_h == vedha_house:
                    if frozenset({p, other_p}) in VEDHA_EXEMPT_PAIRS:
                        exempted.append(other_p)
                    else:
                        obstructors.append(other_p)

        is_obstructed = bool(obstructors)
        net_fav = is_benefic_house and not is_obstructed

        s_idx = transit_signs[p]
        bav_val: int | None = None
        sav_val: int | None = None
        if ashtakavarga is not None:
            sav_val = ashtakavarga.sarvashtakavarga_7[s_idx]
            if p in ashtakavarga.bhinna_tables:
                bav_val = ashtakavarga.bhinna_tables[p].sign_bindus[s_idx]

        results[p] = GocharaPlanetTransit(
            planet=p,
            transit_sign_index=s_idx,
            transit_sign_name=RASI_NAMES[s_idx],
            house_from_moon=h_from_moon,
            is_naturally_benefic_house=is_benefic_house,
            vedha_house_from_moon=vedha_house,
            obstructing_planets=tuple(sorted(obstructors)),
            exempt_planets=tuple(sorted(exempted)),
            is_obstructed_by_vedha=is_obstructed,
            net_favorable=net_fav,
            bav_bindus_in_sign=bav_val,
            sav_bindus_in_sign=sav_val,
        )
    return results
