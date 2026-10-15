"""Clean-room Parashari Six-Fold Planetary Strength (Shadbala), Ishta/Kashta Phala, and Bhava Bala.

Mathematical formulations follow *Brihat Parashara Hora Shastra* (Chapter 27),
*Graha and Bhava Balas*, and *Saravali*:
- Sthana Bala = Uchcha Bala + Saptavargaja Bala + Ojhayugmarasyamsa Bala +
  Kendradi Bala + Drekkana Bala.
- Dig Bala = Directional strength from 1st/4th/7th/10th house cusps.
- Kala Bala = Nathonnatha Bala + Paksha Bala + Tribhaga Bala +
  Varsha-Masa-Dina-Hora Bala + Ayana Bala + Yuddha Bala.
- Cheshta Bala = Motional strength (Sun uses Ayana Bala, Moon uses Paksha Bala,
  5 Taragrahas use motional state / Seeghra arc).
- Naisargika Bala = Natural luminosity hierarchy (60.0 down to 8.57 virupas).
- Drik Bala = Continuous piecewise Parashari aspect strength (Drishti Pinda / 4).
- Ishta Phala & Kashta Phala, minimum required Rupas, and 12-house Bhava Bala.
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Final, Mapping

from .nakshatra import RASI_NAMES, normalize_degrees
from .panchanga import HORA_CHALDEAN_ORDER, compute_vara
from .vargas import MOOLATRIKONA_RANGES, RASI_LORDS, compound_relationship, varga_sign

SEVEN_GRAHAS: Final[tuple[str, ...]] = (
    "Sun",
    "Moon",
    "Mars",
    "Mercury",
    "Jupiter",
    "Venus",
    "Saturn",
)

TARAGRAHAS: Final[tuple[str, ...]] = (
    "Mars",
    "Mercury",
    "Jupiter",
    "Venus",
    "Saturn",
)

# Deep exaltation longitudes (Paramochcha) in sidereal degrees
DEEP_EXALTATION_DEG: Final[Mapping[str, float]] = {
    "Sun": 10.0,       # 10 deg Aries
    "Moon": 33.0,      # 3 deg Taurus
    "Mars": 298.0,     # 28 deg Capricorn
    "Mercury": 165.0,  # 15 deg Virgo
    "Jupiter": 95.0,   # 5 deg Cancer
    "Venus": 357.0,    # 27 deg Pisces
    "Saturn": 200.0,   # 20 deg Libra
}

NAISARGIKA_BALA_VIRUPAS: Final[Mapping[str, float]] = {
    "Sun": 60.0 * 7.0 / 7.0,      # 60.000000
    "Moon": 60.0 * 6.0 / 7.0,     # 51.428571
    "Venus": 60.0 * 5.0 / 7.0,    # 42.857143
    "Jupiter": 60.0 * 4.0 / 7.0,  # 34.285714
    "Mercury": 60.0 * 3.0 / 7.0,  # 25.714286
    "Mars": 60.0 * 2.0 / 7.0,     # 17.142857
    "Saturn": 60.0 * 1.0 / 7.0,   #  8.571429
}

REQUIRED_SHADBALA_RUPAS: Final[Mapping[str, float]] = {
    "Sun": 5.0,      # 300 virupas
    "Moon": 6.0,     # 360 virupas
    "Mars": 5.0,     # 300 virupas
    "Mercury": 7.0,  # 420 virupas
    "Jupiter": 6.5,  # 390 virupas
    "Venus": 5.5,    # 330 virupas
    "Saturn": 5.0,   # 300 virupas
}

SAPTAVARGAJA_POINTS: Final[Mapping[str, float]] = {
    "Moolatrikona": 45.0,
    "Swakshetra": 30.0,
    "Adhimitra": 22.5,
    "Mitra": 15.0,
    "Sama": 7.5,
    "Shatru": 3.75,
    "Adhishatru": 1.875,
}

# Mean daily motions in degrees/day for Cheshta Gati classification when speeds are supplied
MEAN_DAILY_SPEED_DEG: Final[Mapping[str, float]] = {
    "Mars": 0.5240,
    "Mercury": 1.3833,
    "Jupiter": 0.0831,
    "Venus": 1.2000,
    "Saturn": 0.0335,
}

# Classical Bimba Parimana (planetary disc diameters in arcseconds) for Yuddha Bala transfer
DISC_DIAMETER_ARCSEC: Final[Mapping[str, float]] = {
    "Mars": 9.4,
    "Mercury": 6.6,
    "Jupiter": 190.4,
    "Venus": 16.6,
    "Saturn": 158.0,
}


@dataclass(frozen=True)
class SthanaBalaBreakdown:
    """Five-component breakdown of Sthana Bala (Positional Strength) in Virupas."""

    uchcha_bala: float
    saptavargaja_bala: float
    ojhayugmarasyamsa_bala: float
    kendradi_bala: float
    drekkana_bala: float
    total_virupas: float


@dataclass(frozen=True)
class KalaBalaBreakdown:
    """Six-component breakdown of Kala Bala (Temporal Strength) in Virupas."""

    nathonnatha_bala: float
    paksha_bala: float
    tribhaga_bala: float
    varsha_masa_dina_hora_bala: float
    ayana_bala: float
    yuddha_bala: float
    total_virupas: float


@dataclass(frozen=True)
class PlanetShadbala:
    """Complete Six-Fold Strength (Shadbala) and Ishta/Kashta Phala for one graha."""

    planet: str
    sthana_bala: SthanaBalaBreakdown
    dig_bala: float
    kala_bala: KalaBalaBreakdown
    cheshta_bala: float
    naisargika_bala: float
    drik_bala: float
    total_virupas: float
    total_rupas: float
    required_rupas: float
    strength_ratio: float
    meets_minimum: bool
    ishta_phala: float
    kashta_phala: float


@dataclass(frozen=True)
class BhavaBalaEntry:
    """Three-component Bhava Bala for a single house (1..12)."""

    house_number: int
    sign_index: int
    sign_name: str
    sign_lord: str
    cusp_lon_deg: float
    bhava_adhipati_bala: float
    bhava_dig_bala: float
    bhava_drishti_bala: float
    total_virupas: float
    total_rupas: float


@dataclass(frozen=True)
class ShadbalaSummary:
    """Complete Shadbala and Bhava Bala report for all 7 grahas and 12 houses."""

    planets: Mapping[str, PlanetShadbala]
    bhavas: tuple[BhavaBalaEntry, ...]
    strongest_planet: str
    weakest_planet: str
    strongest_bhava: int


def _shortest_arc_deg(lon_a: float, lon_b: float) -> float:
    """Return shortest angular distance in [0.0, 180.0] between two longitudes."""
    diff = abs(normalize_degrees(lon_a) - normalize_degrees(lon_b)) % 360.0
    return 360.0 - diff if diff > 180.0 else diff


def compute_uchcha_bala(planet: str, sidereal_lon_deg: float) -> float:
    """Compute Uchcha Bala (0..60 virupas) from angular distance to deep debilitation."""
    p = planet.strip().capitalize()
    exalt = DEEP_EXALTATION_DEG[p]
    debil = normalize_degrees(exalt + 180.0)
    arc = _shortest_arc_deg(sidereal_lon_deg, debil)
    return arc / 3.0


def compute_saptavargaja_bala(planet: str, planet_longitudes: Mapping[str, float]) -> float:
    """Compute Saptavargaja Bala in D1, D2, D3, D7, D9, D12, and D30 using Panchadha Maitri."""
    p = planet.strip().capitalize()
    lon = normalize_degrees(planet_longitudes[p])
    d1_sign = min(int(lon // 30.0), 11)
    deg_in_d1 = lon - d1_sign * 30.0
    d1_signs = {k.strip().capitalize(): min(int(normalize_degrees(v) // 30.0), 11) for k, v in planet_longitudes.items()}

    total = 0.0
    for v_code in ("D1", "D2", "D3", "D7", "D9", "D12", "D30"):
        vp = varga_sign(lon, v_code)
        lord = vp.sign_lord
        if v_code == "D1" and p in MOOLATRIKONA_RANGES:
            mt_sign, mt_start, mt_end = MOOLATRIKONA_RANGES[p]
            if vp.sign_index == mt_sign and mt_start <= deg_in_d1 < mt_end:
                total += SAPTAVARGAJA_POINTS["Moolatrikona"]
                continue
        if lord == p:
            dignity = "Swakshetra"
        else:
            dignity = compound_relationship(p, lord, d1_sign, d1_signs[lord])
        total += SAPTAVARGAJA_POINTS[dignity]
    return total


def compute_ojhayugmarasyamsa_bala(planet: str, sidereal_lon_deg: float) -> float:
    """Compute Ojhayugmarasyamsa Bala (0, 15, or 30 virupas) from D1 and D9 sign parity."""
    p = planet.strip().capitalize()
    d1_sign = varga_sign(sidereal_lon_deg, "D1").sign_index
    d9_sign = varga_sign(sidereal_lon_deg, "D9").sign_index
    wants_even = p in ("Moon", "Venus")

    score = 0.0
    if (d1_sign % 2 == 1) == wants_even:
        score += 15.0
    if (d9_sign % 2 == 1) == wants_even:
        score += 15.0
    return score


def compute_kendradi_bala(planet_lon_deg: float, lagna_lon_deg: float) -> float:
    """Compute Kendradi Bala (60 in Kendra, 30 in Panapara, 15 in Apoklima)."""
    p_sign = min(int(normalize_degrees(planet_lon_deg) // 30.0), 11)
    l_sign = min(int(normalize_degrees(lagna_lon_deg) // 30.0), 11)
    house = ((p_sign - l_sign) % 12) + 1
    if house in (1, 4, 7, 10):
        return 60.0
    if house in (2, 5, 8, 11):
        return 30.0
    return 15.0


def compute_drekkana_bala(planet: str, sidereal_lon_deg: float) -> float:
    """Compute Drekkana Bala (15 virupas when placed in gender-matching decanate, else 0)."""
    p = planet.strip().capitalize()
    lon = normalize_degrees(sidereal_lon_deg)
    deg_in_sign = lon % 30.0
    decanate = min(int(deg_in_sign // 10.0), 2)  # 0, 1, 2
    if p in ("Sun", "Mars", "Jupiter") and decanate == 0:
        return 15.0
    if p in ("Mercury", "Saturn") and decanate == 1:
        return 15.0
    if p in ("Moon", "Venus") and decanate == 2:
        return 15.0
    return 0.0


def compute_sthana_bala(
    planet: str,
    planet_longitudes: Mapping[str, float],
    lagna_lon_deg: float,
) -> SthanaBalaBreakdown:
    """Compute full 5-part Sthana Bala breakdown for `planet`."""
    p = planet.strip().capitalize()
    lon = normalize_degrees(planet_longitudes[p])
    uchcha = compute_uchcha_bala(p, lon)
    sapta = compute_saptavargaja_bala(p, planet_longitudes)
    ojha = compute_ojhayugmarasyamsa_bala(p, lon)
    kendra = compute_kendradi_bala(lon, lagna_lon_deg)
    drek = compute_drekkana_bala(p, lon)
    total = uchcha + sapta + ojha + kendra + drek
    return SthanaBalaBreakdown(
        uchcha_bala=uchcha,
        saptavargaja_bala=sapta,
        ojhayugmarasyamsa_bala=ojha,
        kendradi_bala=kendra,
        drekkana_bala=drek,
        total_virupas=total,
    )


def compute_dig_bala(
    planet: str,
    sidereal_lon_deg: float,
    lagna_lon_deg: float,
    *,
    mc_lon_deg: float | None = None,
) -> float:
    """Compute Dig Bala (0..60 virupas) from angular distance to the powerless house cusp."""
    p = planet.strip().capitalize()
    l_lon = normalize_degrees(lagna_lon_deg)
    tenth_lon = normalize_degrees(mc_lon_deg) if mc_lon_deg is not None else normalize_degrees(l_lon + 270.0)
    fourth_lon = normalize_degrees(tenth_lon + 180.0)
    seventh_lon = normalize_degrees(l_lon + 180.0)

    if p in ("Jupiter", "Mercury"):
        powerless = seventh_lon
    elif p in ("Sun", "Mars"):
        powerless = fourth_lon
    elif p == "Saturn":
        powerless = l_lon
    elif p in ("Moon", "Venus"):
        powerless = tenth_lon
    else:
        raise ValueError(f"Unsupported planet {planet!r} for Dig Bala")

    return _shortest_arc_deg(sidereal_lon_deg, powerless) / 3.0


def compute_ayana_bala(planet: str, sidereal_lon_deg: float, *, ayanamsa_deg: float = 24.0) -> float:
    """Compute Ayana Bala (0..60 virupas) from Tropical longitude and solar obliquity (24 deg Kranti)."""
    p = planet.strip().capitalize()
    sayana_rad = math.radians(normalize_degrees(sidereal_lon_deg + ayanamsa_deg))
    kranti_deg = 24.0 * math.sin(sayana_rad)

    if p in ("Sun", "Mars", "Jupiter", "Venus"):
        val = ((24.0 + kranti_deg) / 48.0) * 60.0
    elif p in ("Moon", "Saturn"):
        val = ((24.0 - kranti_deg) / 48.0) * 60.0
    elif p == "Mercury":
        val = ((24.0 + abs(kranti_deg)) / 48.0) * 60.0
    else:
        raise ValueError(f"Unsupported planet {planet!r} for Ayana Bala")
    return max(0.0, min(60.0, val))


def compute_cheshta_bala(
    planet: str,
    planet_longitudes: Mapping[str, float],
    *,
    ayanamsa_deg: float = 24.0,
    planet_speeds_deg_per_day: Mapping[str, float] | None = None,
) -> float:
    """Compute Cheshta Bala (0..60 virupas).

    - Sun's Cheshta Bala equals its Ayana Bala.
    - Moon's Cheshta Bala equals its Paksha Bala.
    - For the 5 Taragrahas:
      If `planet_speeds_deg_per_day` is supplied, uses BPHS Gati classification combined
      with solar elongation; otherwise uses continuous Seeghra Kendra arc from the Sun.
    """
    p = planet.strip().capitalize()
    lon = normalize_degrees(planet_longitudes[p])
    sun_lon = normalize_degrees(planet_longitudes["Sun"])
    moon_lon = normalize_degrees(planet_longitudes["Moon"])

    if p == "Sun":
        return compute_ayana_bala("Sun", lon, ayanamsa_deg=ayanamsa_deg)
    if p == "Moon":
        arc = _shortest_arc_deg(moon_lon, sun_lon)
        return (arc / 3.0)

    if planet_speeds_deg_per_day and p in planet_speeds_deg_per_day:
        spd = float(planet_speeds_deg_per_day[p])
        mean_spd = MEAN_DAILY_SPEED_DEG[p]
        if spd < 0.0:
            return 60.0  # Vakra (retrograde)
        if abs(spd) < 0.05 * mean_spd:
            return 15.0  # Vikala (stationary)
        if spd < 0.5 * mean_spd:
            return 7.5   # Mandatara (very slow)
        if spd < 0.95 * mean_spd:
            return 15.0  # Manda (slow)
        if spd <= 1.15 * mean_spd:
            return 30.0  # Sama (normal speed)
        if spd <= 1.5 * mean_spd:
            return 45.0  # Chara / Sheeghra (fast)
        return 30.0      # Atichara (very fast)

    # Continuous Seeghra Kendra approximation from solar elongation (maximum 60 at opposition)
    elong_arc = _shortest_arc_deg(lon, sun_lon)
    return max(0.0, min(60.0, elong_arc / 3.0))


def parashari_aspect_virupas(aspecting_planet: str, aspecting_lon_deg: float, target_lon_deg: float) -> float:
    """Compute Parashari Drishti strength (0..60 virupas) cast by `aspecting_planet` onto `target_lon_deg`.

    Implements the continuous piecewise BPHS Chapter 26 / 27 Drishti function plus full
    special aspects (Vishesha Drishti) for Mars (4th, 8th), Jupiter (5th, 9th), and Saturn (3rd, 10th).
    """
    p = aspecting_planet.strip().capitalize()
    dk = normalize_degrees(target_lon_deg - aspecting_lon_deg)

    if dk < 30.0 or dk >= 300.0:
        return 0.0

    # Base piecewise aspect curve (Sputa Drishti)
    if 30.0 <= dk < 60.0:
        base = (dk - 30.0) / 2.0
    elif 60.0 <= dk < 90.0:
        base = (dk - 60.0) + 15.0
    elif 90.0 <= dk < 120.0:
        base = 45.0 - (dk - 90.0) / 2.0
    elif 120.0 <= dk < 150.0:
        base = 30.0 - (dk - 120.0)
    elif 150.0 <= dk < 180.0:
        base = (dk - 150.0) * 2.0
    else:  # 180.0 <= dk < 300.0
        base = (300.0 - dk) / 2.0

    # Special Vishesha Drishti additions per BPHS:
    if p == "Mars" and (90.0 <= dk < 120.0 or 210.0 <= dk < 240.0):
        base = min(60.0, base + 15.0)
    elif p == "Jupiter" and (120.0 <= dk < 150.0 or 240.0 <= dk < 270.0):
        base = min(60.0, base + 30.0)
    elif p == "Saturn" and (60.0 <= dk < 90.0 or 270.0 <= dk < 300.0):
        base = min(60.0, base + 45.0)

    return max(0.0, min(60.0, base))


def compute_drik_bala(target_planet: str, planet_longitudes: Mapping[str, float]) -> float:
    """Compute net Drik Bala (`0.25 * (benefic_drishti - malefic_drishti)`) received by `target_planet`."""
    target = target_planet.strip().capitalize()
    target_lon = normalize_degrees(planet_longitudes[target])
    sun_lon = normalize_degrees(planet_longitudes["Sun"])
    moon_lon = normalize_degrees(planet_longitudes["Moon"])
    moon_waxing = normalize_degrees(moon_lon - sun_lon) < 180.0

    net_drishti = 0.0
    for other in SEVEN_GRAHAS:
        if other == target:
            continue
        other_lon = normalize_degrees(planet_longitudes[other])
        aspect_val = parashari_aspect_virupas(other, other_lon, target_lon)
        is_benefic = other in ("Jupiter", "Venus", "Mercury") or (other == "Moon" and moon_waxing)
        if is_benefic:
            net_drishti += aspect_val
        else:
            net_drishti -= aspect_val

    return net_drishti / 4.0


def compute_shadbala(
    planet_longitudes: Mapping[str, float],
    lagna_lon_deg: float,
    *,
    jd_ut: float = 2451545.0,
    sunrise_jd_ut: float | None = None,
    sunset_jd_ut: float | None = None,
    ayanamsa_deg: float = 24.0,
    planet_speeds_deg_per_day: Mapping[str, float] | None = None,
    mc_lon_deg: float | None = None,
) -> ShadbalaSummary:
    """Compute complete Six-Fold Planetary Strength (Shadbala) and 12-house Bhava Bala."""
    norm_lons = {k.strip().capitalize(): normalize_degrees(v) for k, v in planet_longitudes.items()}
    for g in SEVEN_GRAHAS:
        if g not in norm_lons:
            raise ValueError(f"Missing longitude for {g!r} in planet_longitudes")

    sr_jd = float(sunrise_jd_ut) if sunrise_jd_ut is not None else (math.floor(jd_ut - 0.5) + 0.75)
    ss_jd = float(sunset_jd_ut) if sunset_jd_ut is not None else (sr_jd + 0.5)
    if ss_jd <= sr_jd:
        ss_jd = sr_jd + 0.5

    day_span = ss_jd - sr_jd
    night_span = 1.0 - day_span
    midday_jd = sr_jd + 0.5 * day_span
    midnight_jd = midday_jd - 0.5

    # Distance from local midnight in days (0.0 at midnight, 0.5 at noon)
    dist_from_midnight_days = abs(((jd_ut - midnight_jd + 0.5) % 1.0) - 0.5)
    unnatha_virupas = (dist_from_midnight_days / 0.5) * 60.0

    # Paksha base (0..60)
    paksha_arc = _shortest_arc_deg(norm_lons["Moon"], norm_lons["Sun"])
    paksha_base = paksha_arc / 3.0

    # Tribhaga winner
    is_day = sr_jd <= jd_ut < ss_jd
    if is_day:
        third_idx = min(int(((jd_ut - sr_jd) / day_span) * 3.0), 2)
        tribhaga_lord = ("Mercury", "Sun", "Saturn")[third_idx]
    else:
        night_elapsed = (jd_ut - ss_jd) % 1.0
        third_idx = min(int((night_elapsed / night_span) * 3.0), 2)
        tribhaga_lord = ("Moon", "Venus", "Mars")[third_idx]

    # Varsha, Masa, Dina, Hora lords
    vara = compute_vara(jd_ut, sunrise_jd_ut=sr_jd)
    dina_lord = vara.ruler
    hora_start_idx = HORA_CHALDEAN_ORDER.index(dina_lord)
    if is_day:
        hora_num = min(int(((jd_ut - sr_jd) / day_span) * 12.0), 11)
    else:
        night_elapsed = (jd_ut - ss_jd) % 1.0
        hora_num = 12 + min(int((night_elapsed / night_span) * 12.0), 11)
    hora_lord = HORA_CHALDEAN_ORDER[(hora_start_idx + hora_num) % 7]

    days_since_epoch = int(max(0.0, jd_ut - 588465.5))
    varsha_idx = ((days_since_epoch // 360) * 3 + 1) % 7
    masa_idx = ((days_since_epoch // 30) * 2 + 1) % 7
    varsha_lord = VARA_LORDS_BY_INDEX[varsha_idx]
    masa_lord = VARA_LORDS_BY_INDEX[masa_idx]

    sthana_map: dict[str, SthanaBalaBreakdown] = {}
    dig_map: dict[str, float] = {}
    pre_war_kala: dict[str, tuple[float, float, float, float, float]] = {}

    for g in SEVEN_GRAHAS:
        sthana_map[g] = compute_sthana_bala(g, norm_lons, lagna_lon_deg)
        dig_map[g] = compute_dig_bala(g, norm_lons[g], lagna_lon_deg, mc_lon_deg=mc_lon_deg)

        # 1. Nathonnatha
        if g == "Mercury":
            nath = 60.0
        elif g in ("Sun", "Jupiter", "Venus"):
            nath = unnatha_virupas
        else:
            nath = 60.0 - unnatha_virupas

        # 2. Paksha
        if g in ("Jupiter", "Venus", "Mercury", "Moon"):
            paksha = paksha_base * (2.0 if g == "Moon" else 1.0)
        else:
            paksha = 60.0 - paksha_base

        # 3. Tribhaga
        tribhaga = 60.0 if (g == "Jupiter" or g == tribhaga_lord) else 0.0

        # 4. Varsha-Masa-Dina-Hora
        vmdh = 0.0
        if g == varsha_lord:
            vmdh += 15.0
        if g == masa_lord:
            vmdh += 30.0
        if g == dina_lord:
            vmdh += 45.0
        if g == hora_lord:
            vmdh += 60.0

        # 5. Ayana
        ayana = compute_ayana_bala(g, norm_lons[g], ayanamsa_deg=ayanamsa_deg)
        pre_war_kala[g] = (nath, paksha, tribhaga, vmdh, ayana)

    # 6. Yuddha Bala (planetary war when two Taragrahas are within 1.0 deg)
    yuddha_adj: dict[str, float] = {g: 0.0 for g in SEVEN_GRAHAS}
    for i, g1 in enumerate(TARAGRAHAS):
        for g2 in TARAGRAHAS[i + 1 :]:
            arc = _shortest_arc_deg(norm_lons[g1], norm_lons[g2])
            if arc < 1.0:
                b1 = sthana_map[g1].total_virupas + dig_map[g1] + sum(pre_war_kala[g1][:4])
                b2 = sthana_map[g2].total_virupas + dig_map[g2] + sum(pre_war_kala[g2][:4])
                diff_bala = abs(b1 - b2)
                disc_diff = max(0.5, abs(DISC_DIAMETER_ARCSEC[g1] - DISC_DIAMETER_ARCSEC[g2]))
                transfer = diff_bala / disc_diff
                # The planet with smaller longitude in the conjunction (or brighter) wins
                delta = (norm_lons[g2] - norm_lons[g1]) % 360.0
                g1_wins = delta <= 180.0
                if g1_wins:
                    yuddha_adj[g1] += transfer
                    yuddha_adj[g2] -= transfer
                else:
                    yuddha_adj[g2] += transfer
                    yuddha_adj[g1] -= transfer

    planets_out: dict[str, PlanetShadbala] = {}
    for g in SEVEN_GRAHAS:
        nath, paksha, tribhaga, vmdh, ayana = pre_war_kala[g]
        yuddha = yuddha_adj[g]
        kala_total = nath + paksha + tribhaga + vmdh + ayana + yuddha
        kala_bd = KalaBalaBreakdown(
            nathonnatha_bala=nath,
            paksha_bala=paksha,
            tribhaga_bala=tribhaga,
            varsha_masa_dina_hora_bala=vmdh,
            ayana_bala=ayana,
            yuddha_bala=yuddha,
            total_virupas=kala_total,
        )

        cheshta = compute_cheshta_bala(
            g,
            norm_lons,
            ayanamsa_deg=ayanamsa_deg,
            planet_speeds_deg_per_day=planet_speeds_deg_per_day,
        )
        naisargika = NAISARGIKA_BALA_VIRUPAS[g]
        drik = compute_drik_bala(g, norm_lons)

        tot_virupas = sthana_map[g].total_virupas + dig_map[g] + kala_total + cheshta + naisargika + drik
        tot_rupas = tot_virupas / 60.0
        req_rupas = REQUIRED_SHADBALA_RUPAS[g]
        ratio = tot_rupas / req_rupas

        uchcha = sthana_map[g].uchcha_bala
        ishta = math.sqrt(max(0.0, uchcha * cheshta))
        kashta = math.sqrt(max(0.0, (60.0 - uchcha) * (60.0 - cheshta)))

        planets_out[g] = PlanetShadbala(
            planet=g,
            sthana_bala=sthana_map[g],
            dig_bala=dig_map[g],
            kala_bala=kala_bd,
            cheshta_bala=cheshta,
            naisargika_bala=naisargika,
            drik_bala=drik,
            total_virupas=tot_virupas,
            total_rupas=tot_rupas,
            required_rupas=req_rupas,
            strength_ratio=ratio,
            meets_minimum=(tot_rupas >= req_rupas),
            ishta_phala=ishta,
            kashta_phala=kashta,
        )

    # Compute Bhava Bala across all 12 houses
    l_lon = normalize_degrees(lagna_lon_deg)
    l_sign = min(int(l_lon // 30.0), 11)
    deg_in_lagna = l_lon - l_sign * 30.0
    bhavas: list[BhavaBalaEntry] = []

    for h in range(1, 13):
        h_sign = (l_sign + h - 1) % 12
        cusp_lon = normalize_degrees(h_sign * 30.0 + deg_in_lagna)
        lord = RASI_LORDS[h_sign]
        adhipati_bala = planets_out[lord].total_virupas

        # Bhava Dig Bala per BPHS Ch. 27:
        # Nara (human) signs (Gemini=2, Virgo=5, Libra=6, first half Sagittarius=8, Aquarius=10) strongest in 1st
        # Jalachara (water) signs (Cancer=3, second half Capricorn=9, Pisces=11) strongest in 4th
        # Keeta (insect) sign (Scorpio=7) strongest in 7th
        # Chatushpada (quadruped) signs (Aries=0, Taurus=1, Leo=4, second half Sag, first half Cap) strongest in 10th
        if h_sign in (2, 5, 6, 10):
            powerless_house = 7
        elif h_sign in (3, 11):
            powerless_house = 10
        elif h_sign == 7:
            powerless_house = 1
        else:
            powerless_house = 4
        house_dist = abs(h - powerless_house)
        if house_dist > 6:
            house_dist = 12 - house_dist
        bhava_dig = (house_dist / 6.0) * 60.0

        # Bhava Drishti Bala
        bhava_drishti = 0.0
        moon_waxing = normalize_degrees(norm_lons["Moon"] - norm_lons["Sun"]) < 180.0
        for g in SEVEN_GRAHAS:
            asp = parashari_aspect_virupas(g, norm_lons[g], cusp_lon)
            is_ben = g in ("Jupiter", "Venus", "Mercury") or (g == "Moon" and moon_waxing)
            bhava_drishti += (asp / 4.0) if is_ben else (-asp / 4.0)

        tot_bhava_virupas = adhipati_bala + bhava_dig + bhava_drishti
        bhavas.append(
            BhavaBalaEntry(
                house_number=h,
                sign_index=h_sign,
                sign_name=RASI_NAMES[h_sign],
                sign_lord=lord,
                cusp_lon_deg=cusp_lon,
                bhava_adhipati_bala=adhipati_bala,
                bhava_dig_bala=bhava_dig,
                bhava_drishti_bala=bhava_drishti,
                total_virupas=tot_bhava_virupas,
                total_rupas=tot_bhava_virupas / 60.0,
            )
        )

    strongest_p = max(SEVEN_GRAHAS, key=lambda k: planets_out[k].strength_ratio)
    weakest_p = min(SEVEN_GRAHAS, key=lambda k: planets_out[k].strength_ratio)
    strongest_b = max(bhavas, key=lambda b: b.total_virupas).house_number

    return ShadbalaSummary(
        planets=planets_out,
        bhavas=tuple(bhavas),
        strongest_planet=strongest_p,
        weakest_planet=weakest_p,
        strongest_bhava=strongest_b,
    )


VARA_LORDS_BY_INDEX: Final[tuple[str, ...]] = (
    "Sun",
    "Moon",
    "Mars",
    "Mercury",
    "Jupiter",
    "Venus",
    "Saturn",
)
