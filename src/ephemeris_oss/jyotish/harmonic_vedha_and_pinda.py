"""Proprietary Continuous Dignity Fields, Heliacal Rising/Setting, 81-Cell Sarvatobhadra Ray Vedha, & Shodhya Pinda Triggers.

Implements three breakthrough mathematical and classical Jyotish solvers that go
beyond binary lookup tables:
1. Continuous Sinusoidal Exaltation Potential (Uchcha-Neecha Field), Arohi/Avarohi
   Orbital Climb Gradient, Continuous 3D Digbala Vector Field, & Surya Siddhanta
   Kalansha Heliacal Rising/Setting (Udaya/Asta) Root Solver.
2. 9x9 (81-Cell) Sarvatobhadra Chakra Coordinate Ray-Tracer casting 3-way
   Trishula Vedha (Front Sammukha, Left Diagonal Vama, Right Diagonal Dakshina)
   onto all 28 Nakshatras (with Abhijit), 12 Rashis, 16 Vowels (Swaras),
   20 Consonants (Aksharas), and 5 Tithi/Vara cells.
3. Complete 7-Planet Ashtakavarga Trikona & Ekadhipatya Shodhana, Rashi/Graha/Shodhya
   Pinda, 27-Nakshatra Sodya-Pinda Transit Trigger Stars, 12-House Vitta-Ayavyaya
   Wealth/Expenditure Ratios, and Continuous Harmonic Phase-Coherence Yoga Potency.
"""

from __future__ import annotations

from dataclasses import dataclass
import hashlib
import json
import math
from typing import TYPE_CHECKING, Dict, List, Optional, Tuple

from .ashtakavarga import compute_ashtakavarga
from .dasha import jd_to_iso_utc
from .nakshatra import (
    NAKSHATRA_NAMES,
    RASI_NAMES,
    abhijit_position,
    nakshatra_position,
)

if TYPE_CHECKING:
    from ..adapter import EphemerisAdapter

EXALTATION_DEGREE: Dict[str, float] = {
    "Sun": 10.0,         # Aries 10°
    "Moon": 33.0,        # Taurus 3°
    "Mars": 298.0,       # Capricorn 28°
    "Mercury": 165.0,    # Virgo 15°
    "Jupiter": 95.0,     # Cancer 5°
    "Venus": 357.0,      # Pisces 27°
    "Saturn": 200.0,     # Libra 20°
    "Rahu": 50.0,        # Taurus 20°
    "Ketu": 230.0,       # Scorpio 20°
}

KALANSHA_LIMIT_DEG: Dict[str, Tuple[float, float]] = {
    # (Direct limit deg, Retrograde limit deg) per Surya Siddhanta Ch. 9
    "Mars": (17.0, 17.0),
    "Mercury": (14.0, 12.0),
    "Jupiter": (11.0, 11.0),
    "Venus": (10.0, 8.0),
    "Saturn": (15.0, 15.0),
}

# Ideal Digbala cusp index: 1 = Lagna (East), 10 = MC (South), 7 = Descendant (West), 4 = IC (North)
DIGBALA_PEAK_HOUSE: Dict[str, int] = {
    "Sun": 10,
    "Mars": 10,
    "Mercury": 1,
    "Jupiter": 1,
    "Moon": 4,
    "Venus": 4,
    "Saturn": 7,
}


def _wrap360(deg: float) -> float:
    return deg % 360.0


def _signed_diff_deg(a: float, b: float) -> float:
    return (a - b + 180.0) % 360.0 - 180.0


@dataclass(frozen=True)
class ContinuousPlanetDignityVector:
    body: str
    sidereal_longitude_deg: float
    speed_deg_per_day: float
    exaltation_point_deg: float
    debilitation_point_deg: float
    angular_distance_from_exaltation_deg: float
    uchcha_potential_0_to_100: float
    uchcha_vira_virupas_0_to_60: float
    arohi_avarohi_state: str  # "AROHI_ASCENDING_TO_EXALTATION" | "AVAROHI_DESCENDING_TO_DEBILITATION" | "STATIONARY_PEAK"
    dignity_velocity_per_day: float
    digbala_peak_house: int
    digbala_continuous_virupas_0_to_60: float
    solar_elongation_deg: float
    kalansha_threshold_deg: float
    is_combust_astangata: bool
    heliacal_visibility_state: str  # "VISIBLE_UDAYA" | "COMBUST_ASTANGATA" | "DAWN_DUSK_TRANSITION_BORDER"
    nearest_heliacal_event_type: Optional[str]
    nearest_heliacal_event_jd_ut: Optional[float]
    nearest_heliacal_event_utc: Optional[str]


@dataclass(frozen=True)
class ContinuousDignityAndHeliacalReport:
    jd_ut: float
    timestamp_utc: str
    ayanamsa_name: str
    ascendant_deg: float
    mc_deg: float
    planets: List[ContinuousPlanetDignityVector]
    overall_chart_uchcha_harmony_0_to_100: float
    overall_chart_digbala_harmony_0_to_100: float
    arohi_planet_count: int
    combust_planet_count: int
    receipt_sha256: str


@dataclass(frozen=True)
class SarvatobhadraRayHit:
    transiting_body: str
    transiting_nakshatra_28: str
    transiting_grid_row: int
    transiting_grid_col: int
    ray_direction: str  # "FRONT_SAMMUKHA" | "LEFT_DIAGONAL_VAMA" | "RIGHT_DIAGONAL_DAKSHINA"
    target_row: int
    target_col: int
    target_cell_type: str
    target_label: str
    vedha_nature: str  # "SUBHA_BENEFIC_VEDHA" | "KRURA_MALEFIC_VEDHA" | "ATI_VEDHA_RETROGRADE"
    hits_natal_janma_nakshatra: bool
    hits_natal_janma_rashi: bool
    hits_natal_nama_akshara: bool


@dataclass(frozen=True)
class Sarvatobhadra81RayVedhaReport:
    jd_ut: float
    timestamp_utc: str
    natal_moon_longitude_deg: float
    natal_janma_nakshatra_28: str
    natal_janma_rashi: str
    natal_nama_akshara: str
    active_ray_hits: List[SarvatobhadraRayHit]
    janma_nakshatra_vedha_planets: List[str]
    janma_rashi_vedha_planets: List[str]
    nama_akshara_vedha_planets: List[str]
    net_vedha_protection_index_minus100_to_plus100: float
    verdict_summary: str
    receipt_sha256: str


@dataclass(frozen=True)
class ShodhyaPindaPlanetRow:
    body: str
    raw_bav_total_bindus: int
    trikona_reduced_total: int
    ekadhipatya_reduced_total: int
    rashi_pinda: int
    graha_pinda: int
    shodhya_pinda: int
    sodya_nakshatra_index_1_to_27: int
    sodya_trigger_nakshatra: str
    kendra_kona_trigger_nakshatra: str
    current_transit_nakshatra: str
    is_transit_on_sodya_trigger_now: bool


@dataclass(frozen=True)
class HouseVitalityRatioRow:
    house_number: int
    rashi_name: str
    sav_bindus: int
    bandhu_7th_bindus: int
    sevaka_6th_bindus: int
    poshaka_11th_bindus: int
    ghataka_12th_bindus: int
    artha_net_surplus: int  # Poshaka (11th from house) - Ghataka (12th from house)
    prosperity_tier: str


@dataclass(frozen=True)
class HarmonicYogaResonanceRow:
    yoga_name: str
    category: str
    participating_bodies: List[str]
    exact_angular_separation_deg: float
    ideal_harmonic_angle_deg: float
    orb_error_deg: float
    phase_coherence_score_0_to_100: float
    dignity_weighted_potency_0_to_100: float
    plain_english_effect: str


@dataclass(frozen=True)
class ShodhyaPindaAndHarmonicYogaReport:
    jd_ut: float
    timestamp_utc: str
    ascendant_deg: float
    shodhya_pinda_rows: List[ShodhyaPindaPlanetRow]
    house_vitality_rows: List[HouseVitalityRatioRow]
    vitta_ayavyaya_wealth_index_0_to_100: float
    harmonic_yogas: List[HarmonicYogaResonanceRow]
    peak_harmonic_yoga_potency_0_to_100: float
    receipt_sha256: str


def _find_nearest_heliacal_crossing(
    adapter: EphemerisAdapter,
    jd_ut: float,
    planet_key: str,
    planet_name: str,
    ayanamsa: str,
    search_window_days: float = 60.0,
) -> Tuple[Optional[str], Optional[float]]:
    if planet_name not in KALANSHA_LIMIT_DEG:
        return None, None

    def _elongation_margin(t_jd: float) -> float:
        sun_p = adapter.calc_ut(t_jd, "sun", sidereal=True, ayanamsa=ayanamsa)
        pl_p = adapter.calc_ut(t_jd, planet_key, sidereal=True, ayanamsa=ayanamsa)
        elong = abs(_signed_diff_deg(pl_p.longitude_deg, sun_p.longitude_deg))
        lim_dir, lim_ret = KALANSHA_LIMIT_DEG[planet_name]
        lim = lim_ret if pl_p.longitude_speed_deg_per_day < 0.0 else lim_dir
        return elong - lim

    m0 = _elongation_margin(jd_ut)
    step_days = 2.0
    max_steps = int(search_window_days / step_days)
    for k in range(1, max_steps + 1):
        shell_candidates: List[Tuple[float, str, float]] = []
        for sign_dir in (1.0, -1.0):
            t_prev = jd_ut + sign_dir * (k - 1) * step_days
            t_curr = jd_ut + sign_dir * k * step_days
            m_prev = m0 if k == 1 else _elongation_margin(t_prev)
            m_curr = _elongation_margin(t_curr)
            if m_prev * m_curr <= 0.0:
                lo, hi = (t_prev, t_curr) if t_prev < t_curr else (t_curr, t_prev)
                m_lo = _elongation_margin(lo)
                for _ in range(20):
                    mid = 0.5 * (lo + hi)
                    m_mid = _elongation_margin(mid)
                    if m_lo * m_mid <= 0.0:
                        hi = mid
                    else:
                        lo = mid
                        m_lo = m_mid
                root_jd = 0.5 * (lo + hi)
                m_before = _elongation_margin(root_jd - 0.1)
                m_after = _elongation_margin(root_jd + 0.1)
                evt_type = (
                    "HELIACAL_RISING_UDAYA"
                    if m_before < 0.0 and m_after >= 0.0
                    else "HELIACAL_SETTING_ASTA"
                )
                shell_candidates.append((abs(root_jd - jd_ut), evt_type, round(root_jd, 6)))
        if shell_candidates:
            shell_candidates.sort(key=lambda item: item[0])
            _, evt_type, best_root_jd = shell_candidates[0]
            return evt_type, best_root_jd
    return None, None


def compute_continuous_dignity_and_heliacal_phenomena(
    jd_ut: float,
    latitude_deg: float,
    longitude_deg: float,
    ayanamsa: str = "lahiri",
    adapter: Optional[EphemerisAdapter] = None,
) -> ContinuousDignityAndHeliacalReport:
    """Compute continuous sinusoidal Uchcha-Neecha potential, Arohi/Avarohi climb, 3D Digbala, and Heliacal Udaya/Asta."""
    if adapter is None:
        from ..adapter import EphemerisAdapter as _EphemerisAdapter

        ad = _EphemerisAdapter()
    else:
        ad = adapter
    ay_key = ayanamsa.strip().lower()

    houses = ad.houses_ut(jd_ut, latitude_deg, longitude_deg, system="placidus", ayanamsa=ay_key)
    asc_deg = float(houses.ascendant_deg)
    mc_deg = float(houses.mc_deg)
    desc_deg = _wrap360(asc_deg + 180.0)
    ic_deg = _wrap360(mc_deg + 180.0)

    cusp_target_by_house = {
        1: asc_deg,
        10: mc_deg,
        7: desc_deg,
        4: ic_deg,
    }

    sun_pos = ad.calc_ut(jd_ut, "sun", sidereal=True, ayanamsa=ay_key)
    sun_lon = float(sun_pos.longitude_deg)

    planet_sequence = [
        ("Sun", "sun"),
        ("Moon", "moon"),
        ("Mars", "mars"),
        ("Mercury", "mercury"),
        ("Jupiter", "jupiter"),
        ("Venus", "venus"),
        ("Saturn", "saturn"),
        ("Rahu", "rahu"),
        ("Ketu", "ketu"),
    ]

    rows: List[ContinuousPlanetDignityVector] = []
    for name, p_key in planet_sequence:
        pos = ad.calc_ut(jd_ut, p_key, sidereal=True, ayanamsa=ay_key)
        lon = float(pos.longitude_deg)
        spd = float(pos.longitude_speed_deg_per_day)

        ex_deg = EXALTATION_DEGREE[name]
        deb_deg = _wrap360(ex_deg + 180.0)
        delta_from_ex = _signed_diff_deg(lon, ex_deg)
        abs_dist_ex = abs(delta_from_ex)

        # Continuous sinusoidal Uchcha potential: 100 at exact exaltation, 0 at exact debilitation
        rad_delta = math.radians(delta_from_ex)
        uchcha_pot = 50.0 * (1.0 + math.cos(rad_delta))
        uchcha_virupas = (180.0 - abs_dist_ex) / 3.0  # Classical 0..60 Virupas

        # Time derivative of Uchcha potential: d/dt [50*(1 + cos(lon - ex))] = -50*sin(lon - ex)*(d_lon/dt in rad/day)
        d_uchcha_dt = -50.0 * math.sin(rad_delta) * math.radians(spd)
        if abs(d_uchcha_dt) < 1e-4:
            arohi_state = "STATIONARY_PEAK"
        elif d_uchcha_dt > 0.0:
            arohi_state = "AROHI_ASCENDING_TO_EXALTATION"
        else:
            arohi_state = "AVAROHI_DESCENDING_TO_DEBILITATION"

        # Continuous Digbala from exact cardinal cusp
        peak_h = DIGBALA_PEAK_HOUSE.get(name, 1)
        powerless_cusp = _wrap360(cusp_target_by_house[peak_h] + 180.0)
        arc_from_powerless = abs(_signed_diff_deg(lon, powerless_cusp))
        digbala_virupas = arc_from_powerless / 3.0

        # Solar elongation and Kalansha heliacal visibility
        if name in ("Sun", "Rahu", "Ketu"):
            elong = 0.0 if name == "Sun" else abs(_signed_diff_deg(lon, sun_lon))
            kal_lim = 0.0
            is_combust = False
            vis_state = "SOLAR_SOURCE" if name == "Sun" else "SHADOW_NODE_EXEMPT"
            evt_type, evt_jd = None, None
        elif name == "Moon":
            elong = abs(_signed_diff_deg(lon, sun_lon))
            kal_lim = 12.0
            is_combust = elong < kal_lim
            vis_state = (
                "COMBUST_ASTANGATA"
                if elong < 10.0
                else ("DAWN_DUSK_TRANSITION_BORDER" if elong < 14.0 else "VISIBLE_UDAYA")
            )
            evt_type, evt_jd = None, None
        else:
            elong = abs(_signed_diff_deg(lon, sun_lon))
            lim_dir, lim_ret = KALANSHA_LIMIT_DEG[name]
            kal_lim = lim_ret if spd < 0.0 else lim_dir
            is_combust = elong < kal_lim
            if abs(elong - kal_lim) <= 1.5:
                vis_state = "DAWN_DUSK_TRANSITION_BORDER"
            elif is_combust:
                vis_state = "COMBUST_ASTANGATA"
            else:
                vis_state = "VISIBLE_UDAYA"
            evt_type, evt_jd = _find_nearest_heliacal_crossing(
                ad, jd_ut, p_key, name, ay_key, search_window_days=45.0
            )

        rows.append(
            ContinuousPlanetDignityVector(
                body=name,
                sidereal_longitude_deg=round(lon, 6),
                speed_deg_per_day=round(spd, 6),
                exaltation_point_deg=ex_deg,
                debilitation_point_deg=deb_deg,
                angular_distance_from_exaltation_deg=round(abs_dist_ex, 4),
                uchcha_potential_0_to_100=round(uchcha_pot, 2),
                uchcha_vira_virupas_0_to_60=round(uchcha_virupas, 2),
                arohi_avarohi_state=arohi_state,
                dignity_velocity_per_day=round(d_uchcha_dt, 4),
                digbala_peak_house=peak_h,
                digbala_continuous_virupas_0_to_60=round(digbala_virupas, 2),
                solar_elongation_deg=round(elong, 4),
                kalansha_threshold_deg=kal_lim,
                is_combust_astangata=is_combust,
                heliacal_visibility_state=vis_state,
                nearest_heliacal_event_type=evt_type,
                nearest_heliacal_event_jd_ut=evt_jd,
                nearest_heliacal_event_utc=jd_to_iso_utc(evt_jd) if evt_jd is not None else None,
            )
        )

    uchcha_avg = sum(r.uchcha_potential_0_to_100 for r in rows) / len(rows)
    digbala_avg = sum((r.digbala_continuous_virupas_0_to_60 / 60.0) * 100.0 for r in rows[:7]) / 7.0
    arohi_cnt = sum(1 for r in rows if r.arohi_avarohi_state == "AROHI_ASCENDING_TO_EXALTATION")
    combust_cnt = sum(1 for r in rows if r.is_combust_astangata)

    receipt_payload = {
        "solver": "compute_continuous_dignity_and_heliacal_phenomena",
        "jd_ut": round(jd_ut, 8),
        "uchcha_avg": round(uchcha_avg, 2),
        "digbala_avg": round(digbala_avg, 2),
        "arohi_cnt": arohi_cnt,
        "combust_cnt": combust_cnt,
    }
    receipt = hashlib.sha256(json.dumps(receipt_payload, sort_keys=True).encode("utf-8")).hexdigest()

    return ContinuousDignityAndHeliacalReport(
        jd_ut=jd_ut,
        timestamp_utc=jd_to_iso_utc(jd_ut),
        ayanamsa_name=ay_key.upper(),
        ascendant_deg=round(asc_deg, 6),
        mc_deg=round(mc_deg, 6),
        planets=rows,
        overall_chart_uchcha_harmony_0_to_100=round(uchcha_avg, 2),
        overall_chart_digbala_harmony_0_to_100=round(digbala_avg, 2),
        arohi_planet_count=arohi_cnt,
        combust_planet_count=combust_cnt,
        receipt_sha256=receipt,
    )


def _norm_sbc_name(name: str) -> str:
    return "".join(ch for ch in name.strip().lower() if ch.isalnum())


def _build_sbc_nakshatra_coord_map() -> Dict[str, Tuple[int, int]]:
    from ..jyotish_transit.chakras import build_sarvatobhadra_grid

    grid = build_sarvatobhadra_grid()
    mapping: Dict[str, Tuple[int, int]] = {}
    for row in grid:
        for cell in row:
            if cell.cell_type.lower() == "nakshatra":
                mapping[cell.label.lower()] = (cell.row, cell.col)
                mapping[_norm_sbc_name(cell.label)] = (cell.row, cell.col)
    return mapping


def _build_sbc_grid_lookup() -> Dict[Tuple[int, int], Tuple[str, str]]:
    from ..jyotish_transit.chakras import build_sarvatobhadra_grid

    grid = build_sarvatobhadra_grid()
    return {
        (cell.row, cell.col): (cell.cell_type.lower(), cell.label)
        for row in grid
        for cell in row
    }


def compute_sarvatobhadra_81_ray_vedha(
    jd_ut: float,
    natal_moon_longitude_deg: float,
    natal_nama_akshara: str = "a",
    ayanamsa: str = "lahiri",
    adapter: Optional[EphemerisAdapter] = None,
) -> Sarvatobhadra81RayVedhaReport:
    """Trace all 3-way Trishula Vedha rays across the 9x9 Sarvatobhadra Chakra grid."""
    if adapter is None:
        from ..adapter import EphemerisAdapter as _EphemerisAdapter

        ad = _EphemerisAdapter()
    else:
        ad = adapter
    ay_key = ayanamsa.strip().lower()

    nak_coords = _build_sbc_nakshatra_coord_map()
    grid_lookup = _build_sbc_grid_lookup()

    natal_ab = abhijit_position(_wrap360(natal_moon_longitude_deg))
    natal_nak_28_name = natal_ab.nakshatra_28_name
    natal_rashi_name = RASI_NAMES[int(_wrap360(natal_moon_longitude_deg) // 30.0) % 12]
    target_akshara = natal_nama_akshara.strip().lower()

    benefics = {"Jupiter", "Venus", "Mercury", "Moon"}
    planet_sequence = [
        ("Sun", "sun"),
        ("Moon", "moon"),
        ("Mars", "mars"),
        ("Mercury", "mercury"),
        ("Jupiter", "jupiter"),
        ("Venus", "venus"),
        ("Saturn", "saturn"),
        ("Rahu", "rahu"),
        ("Ketu", "ketu"),
    ]

    all_hits: List[SarvatobhadraRayHit] = []
    janma_nak_hit_planets: List[str] = []
    janma_rashi_hit_planets: List[str] = []
    nama_akshara_hit_planets: List[str] = []

    for body_name, p_key in planet_sequence:
        pos = ad.calc_ut(jd_ut, p_key, sidereal=True, ayanamsa=ay_key)
        lon = float(pos.longitude_deg)
        spd = float(pos.longitude_speed_deg_per_day)
        ab_pos = abhijit_position(lon)
        nak28_name = ab_pos.nakshatra_28_name

        # Match exact nakshatra cell on 9x9 border
        coord = nak_coords.get(nak28_name.lower()) or nak_coords.get(_norm_sbc_name(nak28_name))
        if coord is None:
            coord = (0, 1)

        r0, c0 = coord
        # Determine inward normal and diagonal directions from border cell (r0, c0)
        if r0 == 0:  # East edge -> cast South (+r)
            rays = [
                ("FRONT_SAMMUKHA", 1, 0),
                ("LEFT_DIAGONAL_VAMA", 1, 1),
                ("RIGHT_DIAGONAL_DAKSHINA", 1, -1),
            ]
        elif r0 == 8:  # West edge -> cast North (-r)
            rays = [
                ("FRONT_SAMMUKHA", -1, 0),
                ("LEFT_DIAGONAL_VAMA", -1, -1),
                ("RIGHT_DIAGONAL_DAKSHINA", -1, 1),
            ]
        elif c0 == 8:  # South edge -> cast West (-c)
            rays = [
                ("FRONT_SAMMUKHA", 0, -1),
                ("LEFT_DIAGONAL_VAMA", 1, -1),
                ("RIGHT_DIAGONAL_DAKSHINA", -1, -1),
            ]
        else:  # North edge (c0 == 0) -> cast East (+c)
            rays = [
                ("FRONT_SAMMUKHA", 0, 1),
                ("LEFT_DIAGONAL_VAMA", -1, 1),
                ("RIGHT_DIAGONAL_DAKSHINA", 1, 1),
            ]

        if spd < 0.0 and body_name not in ("Rahu", "Ketu"):
            nature = "ATI_VEDHA_RETROGRADE"
        elif body_name in benefics:
            nature = "SUBHA_BENEFIC_VEDHA"
        else:
            nature = "KRURA_MALEFIC_VEDHA"

        for ray_name, dr, dc in rays:
            rr, cc = r0 + dr, c0 + dc
            while 0 <= rr <= 8 and 0 <= cc <= 8:
                ctype, clabel = grid_lookup.get((rr, cc), ("unknown", ""))
                hits_nak = (
                    ctype == "nakshatra"
                    and _norm_sbc_name(clabel) == _norm_sbc_name(natal_nak_28_name)
                )
                hits_rashi = (
                    ctype in ("rasi", "rashi")
                    and _norm_sbc_name(clabel) == _norm_sbc_name(natal_rashi_name)
                )
                hits_akshara = (
                    ctype in ("consonant", "vowel", "akshara", "swara")
                    and clabel.lower() == target_akshara
                )

                if hits_nak or hits_rashi or hits_akshara or ctype == "nakshatra":
                    all_hits.append(
                        SarvatobhadraRayHit(
                            transiting_body=body_name,
                            transiting_nakshatra_28=nak28_name,
                            transiting_grid_row=r0,
                            transiting_grid_col=c0,
                            ray_direction=ray_name,
                            target_row=rr,
                            target_col=cc,
                            target_cell_type=ctype,
                            target_label=clabel,
                            vedha_nature=nature,
                            hits_natal_janma_nakshatra=hits_nak,
                            hits_natal_janma_rashi=hits_rashi,
                            hits_natal_nama_akshara=hits_akshara,
                        )
                    )
                if hits_nak and body_name not in janma_nak_hit_planets:
                    janma_nak_hit_planets.append(body_name)
                if hits_rashi and body_name not in janma_rashi_hit_planets:
                    janma_rashi_hit_planets.append(body_name)
                if hits_akshara and body_name not in nama_akshara_hit_planets:
                    nama_akshara_hit_planets.append(body_name)

                rr += dr
                cc += dc

    # Compute net Vedha protection score (-100 to +100)
    score = 0.0
    for hit in all_hits:
        if hit.hits_natal_janma_nakshatra or hit.hits_natal_janma_rashi or hit.hits_natal_nama_akshara:
            weight = 25.0 if hit.hits_natal_janma_nakshatra else 15.0
            if hit.vedha_nature == "SUBHA_BENEFIC_VEDHA":
                score += weight
            else:
                score -= weight
    score = max(-100.0, min(100.0, score))

    if score >= 20.0:
        verdict = "Strong Benefic Subha-Vedha protection across Janma Nakshatra / Rashi / Akshara."
    elif score <= -20.0:
        verdict = "Active Malefic Krura-Vedha obstruction on sensitive natal SBC cells; remedial caution advised."
    else:
        verdict = "Balanced / neutral Sarvatobhadra Chakra ray geometry across natal sensitivity cells."

    receipt_payload = {
        "solver": "compute_sarvatobhadra_81_ray_vedha",
        "jd_ut": round(jd_ut, 8),
        "natal_nak_28": natal_nak_28_name,
        "janma_nak_hits": janma_nak_hit_planets,
        "janma_rashi_hits": janma_rashi_hit_planets,
        "score": round(score, 2),
    }
    receipt = hashlib.sha256(json.dumps(receipt_payload, sort_keys=True).encode("utf-8")).hexdigest()

    return Sarvatobhadra81RayVedhaReport(
        jd_ut=jd_ut,
        timestamp_utc=jd_to_iso_utc(jd_ut),
        natal_moon_longitude_deg=round(natal_moon_longitude_deg, 6),
        natal_janma_nakshatra_28=natal_nak_28_name,
        natal_janma_rashi=natal_rashi_name,
        natal_nama_akshara=natal_nama_akshara,
        active_ray_hits=all_hits,
        janma_nakshatra_vedha_planets=janma_nak_hit_planets,
        janma_rashi_vedha_planets=janma_rashi_hit_planets,
        nama_akshara_vedha_planets=nama_akshara_hit_planets,
        net_vedha_protection_index_minus100_to_plus100=round(score, 2),
        verdict_summary=verdict,
        receipt_sha256=receipt,
    )


def compute_shodhya_pinda_transit_triggers_and_harmonic_yogas(
    jd_ut: float,
    latitude_deg: float,
    longitude_deg: float,
    ayanamsa: str = "lahiri",
    adapter: Optional[EphemerisAdapter] = None,
) -> ShodhyaPindaAndHarmonicYogaReport:
    """Compute 7-planet Shodhya Pinda Nakshatra triggers, 12-house Vitta-Ayavyaya ratios, and Continuous Harmonic Yogas."""
    if adapter is None:
        from ..adapter import EphemerisAdapter as _EphemerisAdapter

        ad = _EphemerisAdapter()
    else:
        ad = adapter
    ay_key = ayanamsa.strip().lower()

    houses = ad.houses_ut(jd_ut, latitude_deg, longitude_deg, system="placidus", ayanamsa=ay_key)
    asc_deg = float(houses.ascendant_deg)
    asc_sign = int(_wrap360(asc_deg) // 30.0) % 12

    planet_sequence = [
        ("Sun", "sun"),
        ("Moon", "moon"),
        ("Mars", "mars"),
        ("Mercury", "mercury"),
        ("Jupiter", "jupiter"),
        ("Venus", "venus"),
        ("Saturn", "saturn"),
    ]
    lons: Dict[str, float] = {}
    for name, p_key in planet_sequence:
        pos = ad.calc_ut(jd_ut, p_key, sidereal=True, ayanamsa=ay_key)
        lons[name] = float(pos.longitude_deg)

    av_analysis = compute_ashtakavarga(lons, asc_deg)

    pinda_rows: List[ShodhyaPindaPlanetRow] = []
    for name, _ in planet_sequence:
        bav_tbl = av_analysis.bhinna_tables[name]
        raw_tot = int(bav_tbl.total_bindus)
        trik_tot = int(sum(bav_tbl.trikona_reduced))
        ekad_tot = int(sum(bav_tbl.ekadhipatya_reduced))
        sp = int(bav_tbl.shodhya_pinda)

        # Classical Sodya Pinda Nakshatra trigger: (Shodhya_Pinda * 7) % 27
        sodya_idx_0 = ((sp * 7) % 27)
        sodya_nak_name = NAKSHATRA_NAMES[sodya_idx_0]

        # Kendra/Kona Bhava-weighted trigger star
        lagna_bindu = max(1, int(bav_tbl.sign_bindus[asc_sign]))
        kk_idx_0 = ((sp * lagna_bindu) % 27)
        kk_nak_name = NAKSHATRA_NAMES[kk_idx_0]

        curr_nak = nakshatra_position(lons[name]).name
        pinda_rows.append(
            ShodhyaPindaPlanetRow(
                body=name,
                raw_bav_total_bindus=raw_tot,
                trikona_reduced_total=trik_tot,
                ekadhipatya_reduced_total=ekad_tot,
                rashi_pinda=int(bav_tbl.rasi_pinda),
                graha_pinda=int(bav_tbl.graha_pinda),
                shodhya_pinda=sp,
                sodya_nakshatra_index_1_to_27=sodya_idx_0 + 1,
                sodya_trigger_nakshatra=sodya_nak_name,
                kendra_kona_trigger_nakshatra=kk_nak_name,
                current_transit_nakshatra=curr_nak,
                is_transit_on_sodya_trigger_now=(curr_nak in (sodya_nak_name, kk_nak_name)),
            )
        )

    # 12-House Bandhu / Sevaka / Poshaka / Ghataka Vitality Matrix
    sav = av_analysis.sarvashtakavarga_7
    vitality_rows: List[HouseVitalityRatioRow] = []
    surplus_count = 0
    for h_num in range(1, 13):
        s_idx = (asc_sign + h_num - 1) % 12
        b_sav = int(sav[s_idx])
        b_bandhu = int(sav[(s_idx + 6) % 12])   # 7th from house
        b_sevaka = int(sav[(s_idx + 5) % 12])   # 6th from house
        b_poshaka = int(sav[(s_idx + 10) % 12]) # 11th from house (gains)
        b_ghataka = int(sav[(s_idx + 11) % 12]) # 12th from house (expenditure)
        net_surplus = b_poshaka - b_ghataka
        if net_surplus > 0:
            surplus_count += 1
        if b_sav >= 30 and net_surplus >= 2:
            tier = "UTTAMA_HIGH_ACCUMULATION"
        elif b_sav >= 28 or net_surplus >= 0:
            tier = "MADHYAMA_BALANCED_SUSTENANCE"
        else:
            tier = "KSHINA_HIGH_EXPENDITURE"

        vitality_rows.append(
            HouseVitalityRatioRow(
                house_number=h_num,
                rashi_name=RASI_NAMES[s_idx],
                sav_bindus=b_sav,
                bandhu_7th_bindus=b_bandhu,
                sevaka_6th_bindus=b_sevaka,
                poshaka_11th_bindus=b_poshaka,
                ghataka_12th_bindus=b_ghataka,
                artha_net_surplus=net_surplus,
                prosperity_tier=tier,
            )
        )

    # Vitta-Ayavyaya Wealth Index (combining 1st, 2nd, 9th, 10th, 11th vs 12th SAV bindus)
    b1 = vitality_rows[0].sav_bindus
    b2 = vitality_rows[1].sav_bindus
    b9 = vitality_rows[8].sav_bindus
    b10 = vitality_rows[9].sav_bindus
    b11 = vitality_rows[10].sav_bindus
    b12 = vitality_rows[11].sav_bindus
    wealth_ratio = ((b1 + b2 + b9 + b10 + b11) / max(1.0, 5.0 * b12)) * 50.0 + (surplus_count / 12.0) * 30.0
    vitta_index = max(0.0, min(100.0, wealth_ratio))

    # Continuous Harmonic Phase-Coherence Yoga Potency Tensor
    harmonic_pairs = [
        (
            "Gaja-Kesari Harmonic Resonance",
            "CHANDRA_GURU_KENDRA",
            ["Moon", "Jupiter"],
            (0.0, 90.0, 180.0, 270.0),
            "Continuous 4th-harmonic (Kendra) phase lock between Moon and Jupiter amplifying wisdom and lasting reputation.",
        ),
        (
            "Budha-Aditya Solar-Mental Coherence",
            "SURYA_BUDHA_YUTI",
            ["Sun", "Mercury"],
            (0.0,),
            "1st-harmonic conjunction coherence (peaking outside deep combustion) sharpening analytical intelligence.",
        ),
        (
            "Dharma-Karmadhipati / Guru-Shani Structural Resonance",
            "GURU_SHANI_HARMONIC",
            ["Jupiter", "Saturn"],
            (0.0, 60.0, 120.0, 180.0),
            "Expansion-structure harmonic alignment governing institutional leadership and long-term career architecture.",
        ),
        (
            "Lakshmi-Narayana / Shukra-Budha Creative Resonance",
            "SHUKRA_BUDHA_HARMONIC",
            ["Venus", "Mercury"],
            (0.0, 60.0),
            "Aesthetic and commercial phase coherence uniting design taste with articulate communication.",
        ),
        (
            "Chandra-Mangala Wealth Impulse Resonance",
            "CHANDRA_MANGALA_HARMONIC",
            ["Moon", "Mars"],
            (0.0, 120.0, 180.0),
            "Emotional courage and enterprise execution harmonic driving decisive financial action.",
        ),
    ]

    harmonic_rows: List[HarmonicYogaResonanceRow] = []
    for y_name, cat, bodies, ideal_angles, desc in harmonic_pairs:
        l1 = lons[bodies[0]]
        l2 = lons[bodies[1]]
        sep = abs(_signed_diff_deg(l1, l2))
        best_ideal = min(ideal_angles, key=lambda ia: abs(sep - ia))
        orb_err = abs(sep - best_ideal)
        # Gaussian / cosine harmonic phase coherence within a 15° window
        coherence = max(0.0, 100.0 * math.exp(-((orb_err / 10.0) ** 2)))
        # Weight by dignity potential of the two bodies
        u1 = 50.0 * (1.0 + math.cos(math.radians(_signed_diff_deg(l1, EXALTATION_DEGREE[bodies[0]]))))
        u2 = 50.0 * (1.0 + math.cos(math.radians(_signed_diff_deg(l2, EXALTATION_DEGREE[bodies[1]]))))
        potency = 0.65 * coherence + 0.35 * (0.5 * (u1 + u2))
        harmonic_rows.append(
            HarmonicYogaResonanceRow(
                yoga_name=y_name,
                category=cat,
                participating_bodies=bodies,
                exact_angular_separation_deg=round(sep, 4),
                ideal_harmonic_angle_deg=best_ideal,
                orb_error_deg=round(orb_err, 4),
                phase_coherence_score_0_to_100=round(coherence, 2),
                dignity_weighted_potency_0_to_100=round(potency, 2),
                plain_english_effect=desc,
            )
        )

    harmonic_rows.sort(key=lambda r: -r.dignity_weighted_potency_0_to_100)
    peak_potency = harmonic_rows[0].dignity_weighted_potency_0_to_100 if harmonic_rows else 0.0

    receipt_payload = {
        "solver": "compute_shodhya_pinda_transit_triggers_and_harmonic_yogas",
        "jd_ut": round(jd_ut, 8),
        "shodhya_pindas": [r.shodhya_pinda for r in pinda_rows],
        "vitta_index": round(vitta_index, 2),
        "peak_potency": round(peak_potency, 2),
    }
    receipt = hashlib.sha256(json.dumps(receipt_payload, sort_keys=True).encode("utf-8")).hexdigest()

    return ShodhyaPindaAndHarmonicYogaReport(
        jd_ut=jd_ut,
        timestamp_utc=jd_to_iso_utc(jd_ut),
        ascendant_deg=round(asc_deg, 6),
        shodhya_pinda_rows=pinda_rows,
        house_vitality_rows=vitality_rows,
        vitta_ayavyaya_wealth_index_0_to_100=round(vitta_index, 2),
        harmonic_yogas=harmonic_rows,
        peak_harmonic_yoga_potency_0_to_100=round(peak_potency, 2),
        receipt_sha256=receipt,
    )


__all__ = [
    "ContinuousDignityAndHeliacalReport",
    "ContinuousPlanetDignityVector",
    "HarmonicYogaResonanceRow",
    "HouseVitalityRatioRow",
    "Sarvatobhadra81RayVedhaReport",
    "SarvatobhadraRayHit",
    "ShodhyaPindaAndHarmonicYogaReport",
    "ShodhyaPindaPlanetRow",
    "compute_continuous_dignity_and_heliacal_phenomena",
    "compute_sarvatobhadra_81_ray_vedha",
    "compute_shodhya_pinda_transit_triggers_and_harmonic_yogas",
]
