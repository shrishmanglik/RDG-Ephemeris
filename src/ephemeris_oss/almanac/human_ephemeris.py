"""Human-Readable Classical Ephemeris & Pt. Maheshji's Jyotish Academy Master Calculation Compendium.

Generates a complete, encyclopedic, 30-Chapter classical *Nirayana* (Sidereal) and *Sayana* (Tropical)
Astronomical Ephemeris and Manual Kundali Calculation Compendium designed for human astrologers,
classical researchers, and students of **Pt. Maheshji's Jyotish Academy (Jyotish Gurukul)**.

Every calculation that the ``ephemeris-oss`` software engine performs computationally can be
performed manually on paper using the tables in this 30-chapter master volume:

1. **Chapter 1:** Fundamental Astronomical Constants, Time Scales (UTC/UT1/TT/TDB/Delta-T), Julian Day Conversion Tables (1900-2050), & 25-Ayanamsha Master Reference Table
2. **Chapter 2:** Complete Daily Sidereal (*Nirayana*) & Tropical (*Sayana*) Planetary Longitude Grid (`05:30 IST / 00:00 UTC`) Across All 13 Bodies + Second-Order Tabular Differences
3. **Chapter 3:** Complete Daily Spherical & Physical Ephemeris Grid — Right Ascension, Declination (*Kranti*), Ecliptic Latitude (*Shara*), True Distance (AU/km), Horizontal Parallax, Angular Diameter, Phase, & Visual Magnitude
4. **Chapter 4:** Complete Monthly Astronomical & Astrological Phenomena Almanac (Sign Ingresses / *Sankrantis*, Nakshatra Ingresses, Synodic Aspects, *Krantisamya Mahapata* Windows, & 30-Star *Yogatara* Conjunctions)
5. **Chapter 5:** Daily Sunrise-Anchored *Drik Panchanga*, *Ghati-Pala* Almanac, *Muhurta* Windows, & Daily Sunrise *Gulika/Mandi* Longitude Table
6. **Chapter 6:** Manual *Spashta Graha* Interpolation Compendium — 96-Row 15-Minute *Trairashika* Ready Reckoner & Bessel Second-Difference Lunar Correction Table
7. **Chapter 7:** Master Tables of Ascendants (*Udaya Lagna*), 10th House Midheaven (*Madhya Lagna*), & *Sripathi Bhava Chalit* Across 9 Canonical World Latitudes (`00h 00m` to `23h 52m` Local Sidereal Time)
8. **Chapter 8:** Complete Manual Compendium of All 8 *Vishesha Lagnas* (*Udaya, Hora, Ghati, Bhava, Sree, Indu, Pranapada, Varnada*), 11 *Upagrahas*, *Yogi/Avayogi*, & 9 *Prashna Sphutas*
9. **Chapter 9:** Complete *Shodashvarga* (D1-D60) Divisional Chart Master Lookup Tables, 36 *Drekkana Swarupas*, 60 *Shashtiamsa* Deities, *Pushkara*, & *Vimsopaka Bala* Matrices
10. **Chapter 10:** Complete 132-Cell *Mrityu Bhaga* (Fatal Degrees), 22nd *Khara Drekkana*, & 64th *Khara Navamsa* Master Vulnerability Tables
11. **Chapter 11:** Complete Krishnamurti Padhati (KP) 249 Sub-Lord Master Table (`#001` to `#249`) & 4-Fold Significator Worksheet
12. **Chapter 12:** Complete Multi-System *Dasha* Manual Compendium (80-Row *Vimshottari Bhogyamsha* Balance Table, 81-Row *Mahadasha x Antardasha* Matrix, 36y *Yogini*, 108y *Ashtottari*, & 108-Pada *Kalachakra* Master Wheel)
13. **Chapter 13:** Complete *Jaimini Upadesha Sutras* Manual Compendium (7/8 *Chara Karakas*, *Karakamsa* Deities, 144-Cell 12x12 *Arudha Pada* *Swastha* Jump Matrix, *Rashi Drishti*, *Argala*, & *Jaimini Ayurdaya*)
14. **Chapter 14:** Complete Six-Fold *Shadbala*, 36-Row Continuous Parashari *Sphuta Drishti* Aspectual Strength Table (`0°..360°`), *Ishta/Kashta Phala*, & 12-House *Bhava Bala*
15. **Chapter 15:** Complete *Ashtakavarga* (337-Bindu BAV/SAV), *Trikona & Ekadhipatya Shodhana*, *Rashi/Graha/Shodhya Pinda*, & 8-Lord *Kakshya* (`3°45'`) Transit Timing Compendium
16. **Chapter 16:** Complete Classical Longevity (*Ayurdaya* — *Pindayu, Nisargayu, & Amsayu*) Manual Calculation Compendium
17. **Chapter 17:** Complete *Tajika Varshphal* (Annual Solar Return) Manual Compendium — 100-Year *Dhruvanka* Table, *Muntha*, 12-Sign *Tajika Hadda* Bounds, 16 *Tajika Yogas*, & All 36 *Tajika Sahams*
18. **Chapter 18:** Complete *Ashtakoota* (36-Guna) & *Dashakoota* (10-Porutham) Marriage Compatibility, 14x14 *Yoni* Matrix, 81-Cell *Sarvatobhadra Chakra*, *Kota Chakra*, & *Muhurta* Electional Compendium
19. **Chapter 19:** Complete Classical Parashari Yoga Encyclopedia, 30-Star *Yogatara* Astrometric Catalog, & *Surya Siddhanta* Epicyclic Reference
20. **Chapter 20 (Section 7):** Pt. Maheshji's Jyotish Academy Complete 15-Step Worked Manual Master Kundali & Predictive Synthesis Case Study
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date, timedelta
import html as html_mod
import math
import re
from typing import Any, Mapping

from .._version import __version__
from ..adapter import EphemerisAdapter, FLG_SIDEREAL
from ..engine.conventions import AYANAMSA_CATALOG
from ..engine.earth_orientation import estimate_delta_t
from ..engine.receipt import canonical_hash
from ..engine.stellar_anchors import YOGATARA_30_CATALOG
from ..frontier_astrodynamics import (
    _rozenberg_air_mass,
    _saemundsson_refraction_arcsec,
    compute_topocentric_relativistic_astrometry,
    evaluate_lifetime_eclipse_natal_sensitivity,
    solve_synodic_retrograde_loops_and_triple_passes,
)
from ..impossible_astrology import (
    evaluate_yogatara_stellar_bheda_and_visibility,
    solve_krantisamya_mahapata_windows,
)
from ..jyotish import compute_vedic_chart_analysis
from ..jyotish.ashtakavarga import BAV_BENEFIC_HOUSES
from ..jyotish.conditional_dashas_and_nadi import (
    BPHS_10_NAKSHATRA_DASHAS,
    NADI_AMSA_BASE_NAMES_15,
    NADI_AMSA_DECADE_QUALITIES_10,
    compute_all_10_parashari_nakshatra_dashas,
    compute_nadi_amsa_and_sudarshana_chakra,
    compute_vimshottari_5_level_prana_chronometer,
    solve_golden_muhurta_electional_windows,
)
from ..jyotish.harmonic_vedha_and_pinda import (
    EXALTATION_DEGREE,
    KALANSHA_LIMIT_DEG,
    compute_continuous_dignity_and_heliacal_phenomena,
    compute_sarvatobhadra_81_ray_vedha,
    compute_shodhya_pinda_transit_triggers_and_harmonic_yogas,
)
from ..jyotish.dasha import (
    ASHTOTTARI_RULERS as ASHTOTTARI_LORDS,
    ASHTOTTARI_YEARS,
    KALACHAKRA_APASAVYA_SEQUENCES,
    KALACHAKRA_SAVYA_SEQUENCES,
    KALACHAKRA_SIGN_YEARS,
    VIMSHOTTARI_TOTAL_YEARS,
    VIMSHOTTARI_YEARS,
    YOGINI_LORDS as YOGINI_RULERS,
    YOGINI_NAMES,
    YOGINI_YEARS,
    compute_kalachakra_dasha,
)
from ..jyotish.nakshatra import (
    NAKSHATRA_NAMES,
    RASI_NAMES as RASHI_NAMES,
    VIMSHOTTARI_RULERS as VIMSHOTTARI_LORDS,
    nakshatra_position,
)
from ..jyotish.vargas import RASI_LORDS, SHASHTIAMSA_CATALOG, varga_sign
from ..jyotish.vishesha_lagnas import (
    ARUDHA_HOUSE_NAMES,
    FullAstronomicalBodyEphemeris,
    INDU_LAGNA_KALA_VALUES,
    PUSHKARA_BHAGA_DEGREES,
    PUSHKARA_NAVAMSA_RASHI_INDICES,
    compute_full_astronomical_sky_ephemeris,
    compute_vishesha_lagnas_and_special_points,
)
from ..jyotish_advanced.koota import (
    NAKSHATRA_GANA,
    NAKSHATRA_NADI,
    NAKSHATRA_YONI_INDEX,
    RASI_VARNA_NAME,
    YONI_NAMES,
    YONI_SCORE_MATRIX,
)
from ..jyotish_advanced.kp import kp_coordinate_lords, kp_sub_table_249
from ..jyotish_advanced.varshphal import TAJIKA_HADDA_TABLE, TAJIKA_PLANET_ORBS_DEG, compute_tajika_sahams
from ..jyotish_jaimini.sutras import JAIMINI_DEITY_MAP, RASHI_DRISHTI_TABLE
from ..jyotish_nadi.ayurdaya import NISARGAYU_MAX_YEARS, PINDAYU_MAX_YEARS
from ..jyotish_nadi.khara_mrityu import DREKKANA_SWARUPA_CATALOG, MRITYU_BHAGA_DEGREE_TABLE
from ..jyotish_siddhanta.surya_siddhanta import (
    MAHAYUGA_BHAGANA,
    MANDOCCA_KALI_EPOCH_DEG,
    MANDA_PARIDHI_EVEN_ODD_DEG,
    SIGHRA_PARIDHI_EVEN_ODD_DEG,
)
from ..jyotish_transit.chakras import KAKSHYA_LORDS, build_sarvatobhadra_grid
from ..jyotish_transit.muhurta_search import (
    AMRITA_SIDDHI_NAKSHATRA,
    DAGDHA_RASI_BY_PAKSHA_TITHI,
    SARVARTHA_SIDDHI_NAKSHATRAS,
)
from ..jyotish_transit.prashna import compute_11_upagrahas, compute_prashna_sphutas
from .ephemeris_tables import scan_ingresses_and_aspects
from .panchang_calendar import generate_monthly_panchang

# Classical combustion orbs (degrees from Sun) per Surya Siddhanta / BPHS
CLASSICAL_COMBUSTION_ORBS_DEG: Mapping[str, tuple[float, float]] = {
    "moon": (12.0, 12.0),
    "mars": (17.0, 17.0),
    "mercury": (14.0, 12.0),  # (direct, retrograde)
    "jupiter": (11.0, 11.0),
    "venus": (10.0, 8.0),     # (direct, retrograde)
    "saturn": (15.0, 15.0),
}

# Classical Lankodaya (equatorial rising durations of the 12 signs in Vinadis / Palas; 3600 Vinadis = 60 Ghatis = 24 Hours)
LANKODAYA_VINADIS: tuple[int, ...] = (
    278,  # Mesha (Aries)
    299,  # Vrishabha (Taurus)
    323,  # Mithuna (Gemini)
    323,  # Karka (Cancer)
    299,  # Simha (Leo)
    278,  # Kanya (Virgo)
    278,  # Tula (Libra)
    299,  # Vrishchika (Scorpio)
    323,  # Dhanu (Sagittarius)
    323,  # Makara (Capricorn)
    299,  # Kumbha (Aquarius)
    278,  # Meena (Pisces)
)

# Daytime Rahu Kala octant (1..8 of Dinamana) for Sun=0, Mon=1, Tue=2, Wed=3, Thu=4, Fri=5, Sat=6
RAHU_KALA_OCTANT: Mapping[int, int] = {0: 8, 1: 2, 2: 7, 3: 5, 4: 6, 5: 4, 6: 3}
YAMAGANDA_OCTANT: Mapping[int, int] = {0: 5, 1: 4, 2: 3, 3: 2, 4: 1, 5: 7, 6: 6}
GULIKA_KALA_OCTANT: Mapping[int, int] = {0: 7, 1: 6, 2: 5, 3: 4, 4: 3, 5: 2, 6: 1}


def format_classical_rashi_dms(lon_deg: float, *, compact_sign_number: bool = False) -> str:
    """Format an ecliptic longitude in ``[0, 360)`` as classical Jyotish ``Rashi DD° MM' SS"``
    or ``SSs DD° MM' SS"`` (where ``SS`` is 00..11 completed signs).
    """
    lon = float(lon_deg) % 360.0
    rashi_idx = int(lon // 30.0) % 12
    deg_in_sign = lon - rashi_idx * 30.0
    total_arcsec = int(round(deg_in_sign * 3600.0))
    if total_arcsec >= 30 * 3600:
        total_arcsec = 0
        rashi_idx = (rashi_idx + 1) % 12
    deg = total_arcsec // 3600
    rem = total_arcsec % 3600
    arcmin = rem // 60
    arcsec = rem % 60
    if compact_sign_number:
        return f"{rashi_idx:02d}s {deg:02d}° {arcmin:02d}' {arcsec:02d}\""
    return f"{RASHI_NAMES[rashi_idx]} {deg:02d}° {arcmin:02d}' {arcsec:02d}\""


def format_daily_motion_dms(speed_deg_per_day: float) -> str:
    """Format daily angular speed as ``+DD° MM' SS"`` or ``-DD° MM' SS"``."""
    sign = "-" if speed_deg_per_day < 0.0 else "+"
    val = abs(float(speed_deg_per_day))
    total_arcsec = int(round(val * 3600.0))
    deg = total_arcsec // 3600
    rem = total_arcsec % 3600
    arcmin = rem // 60
    arcsec = rem % 60
    return f"{sign}{deg:02d}° {arcmin:02d}' {arcsec:02d}\""


def format_ghati_pala(hours: float) -> str:
    """Convert decimal hours into classical Vedic ``GG Ghatis PP Palas`` (1 day = 24h = 60 Ghatis)."""
    total_palas = int(round(max(0.0, float(hours)) * 2.5 * 60.0))
    ghatis = total_palas // 60
    palas = total_palas % 60
    return f"{ghatis:02d}g {palas:02d}p"


def _jd_to_local_hhmm(jd_ut: float, tz_offset_hours: float) -> str:
    year, month, day, hour_ut = EphemerisAdapter.revjul(jd_ut + tz_offset_hours / 24.0)
    total_min = int(round(hour_ut * 60.0)) % 1440
    hh = total_min // 60
    mm = total_min % 60
    return f"{hh:02d}:{mm:02d}"


def _jd_to_local_hhmmss(jd_ut: float, tz_offset_hours: float) -> str:
    year, month, day, hour_ut = EphemerisAdapter.revjul(jd_ut + tz_offset_hours / 24.0)
    total_sec = int(round(hour_ut * 3600.0)) % 86400
    hh = total_sec // 3600
    rem = total_sec % 3600
    mm = rem // 60
    ss = rem % 60
    return f"{hh:02d}:{mm:02d}:{ss:02d}"


@dataclass(frozen=True)
class HumanDailyPlanetCell:
    """One planet's daily human-readable classical ephemeris entry."""

    body: str
    longitude_deg: float
    rashi_index: int
    rashi_name: str
    classical_dms: str
    sign_num_dms: str
    nakshatra_name: str
    nakshatra_lord: str
    pada: int
    speed_deg_per_day: float
    daily_motion_dms: str
    is_retrograde: bool
    is_combust: bool
    status_flags: str
    d9_navamsa_sign: str


@dataclass(frozen=True)
class HumanDailyEphemerisRow:
    """One day's complete human-readable ephemeris and Panchanga row."""

    civil_date: str
    vara_name: str
    jd_reference_ut: float
    ahargana_kali_days: float
    ayanamsa_dms: str
    local_sidereal_time_hms: str
    sunrise_local_hms: str
    sunset_local_hms: str
    dinamana_hours: float
    dinamana_ghati_pala: str
    tithi_name: str
    tithi_end_local_hm: str
    tithi_end_ghati_pala: str
    nakshatra_at_sunrise: str
    yoga_at_sunrise: str
    karana_at_sunrise: str
    rahu_kala_window: str
    abhijit_muhurta_window: str
    vratas: tuple[str, ...]
    planets: Mapping[str, HumanDailyPlanetCell]


@dataclass(frozen=True)
class HumanManualEphemerisCompendium:
    """Complete human-readable ephemeris and Jyotish Academy manual calculation compendium."""

    year: int
    month: int
    reference_epoch_label: str
    observer_latitude_deg: float
    observer_longitude_deg: float
    tz_offset_hours: float
    ayanamsa_mode: str
    daily_rows: tuple[HumanDailyEphemerisRow, ...]
    worked_example: Mapping[str, Any]
    receipt: Mapping[str, Any]
    receipt_sha256: str
    full_sky_rows: tuple[Mapping[str, FullAstronomicalBodyEphemeris], ...] = ()
    phenomena_summary: Mapping[str, Any] | None = None
    chapter_count: int = 30

    def to_dict(self) -> dict[str, Any]:
        return {
            "year": self.year,
            "month": self.month,
            "chapter_count": self.chapter_count,
            "reference_epoch_label": self.reference_epoch_label,
            "observer_latitude_deg": self.observer_latitude_deg,
            "observer_longitude_deg": self.observer_longitude_deg,
            "tz_offset_hours": self.tz_offset_hours,
            "ayanamsa_mode": self.ayanamsa_mode,
            "daily_rows": [
                {
                    "civil_date": r.civil_date,
                    "vara_name": r.vara_name,
                    "jd_reference_ut": r.jd_reference_ut,
                    "ahargana_kali_days": r.ahargana_kali_days,
                    "ayanamsa_dms": r.ayanamsa_dms,
                    "local_sidereal_time_hms": r.local_sidereal_time_hms,
                    "sunrise_local_hms": r.sunrise_local_hms,
                    "sunset_local_hms": r.sunset_local_hms,
                    "dinamana_hours": round(r.dinamana_hours, 4),
                    "dinamana_ghati_pala": r.dinamana_ghati_pala,
                    "tithi_name": r.tithi_name,
                    "tithi_end_local_hm": r.tithi_end_local_hm,
                    "tithi_end_ghati_pala": r.tithi_end_ghati_pala,
                    "nakshatra_at_sunrise": r.nakshatra_at_sunrise,
                    "yoga_at_sunrise": r.yoga_at_sunrise,
                    "karana_at_sunrise": r.karana_at_sunrise,
                    "rahu_kala_window": r.rahu_kala_window,
                    "abhijit_muhurta_window": r.abhijit_muhurta_window,
                    "vratas": list(r.vratas),
                    "planets": {
                        k: {
                            "body": v.body,
                            "longitude_deg": round(v.longitude_deg, 6),
                            "rashi_index": v.rashi_index,
                            "rashi_name": v.rashi_name,
                            "classical_dms": v.classical_dms,
                            "sign_num_dms": v.sign_num_dms,
                            "nakshatra_name": v.nakshatra_name,
                            "nakshatra_lord": v.nakshatra_lord,
                            "pada": v.pada,
                            "speed_deg_per_day": round(v.speed_deg_per_day, 6),
                            "daily_motion_dms": v.daily_motion_dms,
                            "is_retrograde": v.is_retrograde,
                            "is_combust": v.is_combust,
                            "status_flags": v.status_flags,
                            "d9_navamsa_sign": v.d9_navamsa_sign,
                        }
                        for k, v in r.planets.items()
                    },
                }
                for r in self.daily_rows
            ],
            "worked_example": {
                k: v
                for k, v in self.worked_example.items()
                if k
                not in (
                    "vishesha_report",
                    "upagrahas_report",
                    "sphutas_report",
                    "kundali_bundle",
                    "sahams_report",
                    "kalachakra_report",
                    "frontier_topo_report",
                    "frontier_retro_report",
                    "frontier_eclipse_report",
                    "frontier_dashas_report",
                    "frontier_prana_report",
                    "frontier_nadi_report",
                    "frontier_muhurta_report",
                    "frontier_dignity_report",
                    "frontier_sbc_report",
                    "frontier_pinda_report",
                )
            },
            "receipt": dict(self.receipt),
            "receipt_sha256": self.receipt_sha256,
        }

    def to_markdown(self) -> str:
        """Render the complete 30-Chapter Human-Readable Classical Ephemeris & Jyotish Academy Manual."""
        return _render_compendium_markdown(self)

    def to_html(self) -> str:
        """Render a standalone, print-ready, richly formatted HTML book edition."""
        return _render_compendium_html(self)


def generate_human_manual_ephemeris_compendium(
    year: int = 2026,
    month: int = 11,
    *,
    latitude_deg: float = 23.1765,   # Default: Ujjain Mahakaleshwar Prime Meridian of Classical Jyotish
    longitude_deg: float = 75.7885,
    tz_offset_hours: float = 5.5,
    ayanamsa: str = "lahiri",
    reference_hour_ut: float = 0.0,  # 00:00 UTC = 05:30 IST (standard Indian Ephemeris daily epoch)
    adapter: EphemerisAdapter | None = None,
) -> HumanManualEphemerisCompendium:
    """Generate the complete 30-Chapter Human-Readable Classical Ephemeris & Jyotish Academy Compendium."""
    if not (1 <= int(month) <= 12):
        raise ValueError(f"month must be in 1..12; got {month}")
    yr = int(year)
    mo = int(month)
    lat = float(latitude_deg)
    lon = float(longitude_deg)
    tz_off = float(tz_offset_hours)
    ref_h_ut = float(reference_hour_ut)

    ad = adapter if adapter is not None else EphemerisAdapter()
    panchang_cal = generate_monthly_panchang(
        yr,
        mo,
        lat,
        lon,
        tz_offset_hours=tz_off,
        ayanamsa=ayanamsa,
        adapter=ad,
    )

    bodies_order = (
        "sun",
        "moon",
        "mars",
        "mercury",
        "jupiter",
        "venus",
        "saturn",
        "rahu",
        "true_rahu",
        "ketu",
        "uranus",
        "neptune",
        "pluto",
    )

    daily_rows: list[HumanDailyEphemerisRow] = []
    full_sky_rows: list[Mapping[str, FullAstronomicalBodyEphemeris]] = []
    kali_epoch_jd = 588465.5  # 3102 BCE Feb 18 00:00 UT

    for p_day in panchang_cal.days:
        parts = [int(x) for x in p_day.civil_date.split("-")]
        jd_ref_ut = ad.julday(parts[0], parts[1], parts[2], ref_h_ut)
        ahargana = round(jd_ref_ut - kali_epoch_jd, 4)
        ay_deg = ad.get_ayanamsa_ut(jd_ref_ut, mode=ayanamsa)
        ay_sec = int(round(ay_deg * 3600.0))
        ay_d = ay_sec // 3600
        ay_m = (ay_sec % 3600) // 60
        ay_s = (ay_sec % 3600) % 60
        ay_dms = f"{ay_d:02d}° {ay_m:02d}' {ay_s:02d}\""

        houses_ref = ad.houses_ex(jd_ref_ut, lat, lon, b"P", FLG_SIDEREAL)
        armc_deg = float(houses_ref[1][2]) % 360.0
        lst_hours = armc_deg / 15.0
        lst_sec_total = int(round(lst_hours * 3600.0)) % 86400
        lst_hms = f"{lst_sec_total // 3600:02d}h {(lst_sec_total % 3600) // 60:02d}m {lst_sec_total % 60:02d}s"

        sky_map = compute_full_astronomical_sky_ephemeris(jd_ref_ut, ayanamsa=ayanamsa, adapter=ad)
        full_sky_rows.append(sky_map)

        planet_cells: dict[str, HumanDailyPlanetCell] = {}
        for body in bodies_order:
            fb = sky_map[body]
            planet_cells[body] = HumanDailyPlanetCell(
                body=body,
                longitude_deg=fb.sidereal_longitude_deg,
                rashi_index=fb.rashi_index,
                rashi_name=fb.rashi_name,
                classical_dms=fb.sidereal_dms,
                sign_num_dms=format_classical_rashi_dms(fb.sidereal_longitude_deg, compact_sign_number=True),
                nakshatra_name=fb.nakshatra_name,
                nakshatra_lord=fb.nakshatra_lord,
                pada=fb.pada,
                speed_deg_per_day=fb.longitude_speed_deg_per_day,
                daily_motion_dms=fb.daily_motion_dms,
                is_retrograde=fb.is_retrograde,
                is_combust=fb.is_combust,
                status_flags=fb.status_flags,
                d9_navamsa_sign=fb.d9_navamsa_sign,
            )

        sr_jd = p_day.sunrise_jd_ut
        ss_jd = p_day.sunset_jd_ut
        dinamana_hours = max(0.0, (ss_jd - sr_jd) * 24.0)
        dinamana_gp = format_ghati_pala(dinamana_hours)
        tithi_end_hours_from_sr = max(0.0, (p_day.tithi_end_jd_ut - sr_jd) * 24.0)
        tithi_end_gp = format_ghati_pala(tithi_end_hours_from_sr)

        octant_days = (ss_jd - sr_jd) / 8.0
        rk_oct = RAHU_KALA_OCTANT[p_day.vara_index % 7]
        rk_start = sr_jd + (rk_oct - 1) * octant_days
        rk_end = sr_jd + rk_oct * octant_days
        rahu_kala_str = f"{_jd_to_local_hhmm(rk_start, tz_off)}-{_jd_to_local_hhmm(rk_end, tz_off)}"

        muhurta_days = (ss_jd - sr_jd) / 15.0
        ab_start = sr_jd + 7.0 * muhurta_days
        ab_end = sr_jd + 8.0 * muhurta_days
        abhijit_str = f"{_jd_to_local_hhmm(ab_start, tz_off)}-{_jd_to_local_hhmm(ab_end, tz_off)}"

        daily_rows.append(
            HumanDailyEphemerisRow(
                civil_date=p_day.civil_date,
                vara_name=p_day.vara_name,
                jd_reference_ut=jd_ref_ut,
                ahargana_kali_days=ahargana,
                ayanamsa_dms=ay_dms,
                local_sidereal_time_hms=lst_hms,
                sunrise_local_hms=_jd_to_local_hhmmss(sr_jd, tz_off),
                sunset_local_hms=_jd_to_local_hhmmss(ss_jd, tz_off),
                dinamana_hours=dinamana_hours,
                dinamana_ghati_pala=dinamana_gp,
                tithi_name=p_day.tithi_name,
                tithi_end_local_hm=_jd_to_local_hhmm(p_day.tithi_end_jd_ut, tz_off),
                tithi_end_ghati_pala=tithi_end_gp,
                nakshatra_at_sunrise=p_day.nakshatra_name,
                yoga_at_sunrise=p_day.yoga_name,
                karana_at_sunrise=p_day.karana_name,
                rahu_kala_window=rahu_kala_str,
                abhijit_muhurta_window=abhijit_str,
                vratas=p_day.vratas,
                planets=planet_cells,
            )
        )

    # Scan monthly phenomena (Rashi Ingresses, Nakshatra Ingresses, Synodic Aspects, Krantisamya Mahapata, Yogatara Bheda)
    start_jd_month = daily_rows[0].jd_reference_ut
    end_jd_month = daily_rows[-1].jd_reference_ut + 1.0
    transit_timeline = scan_ingresses_and_aspects(
        start_jd_month,
        end_jd_month,
        bodies=("Sun", "Mars", "Mercury", "Jupiter", "Venus", "Saturn", "Rahu"),
        aspect_angles=(0.0, 60.0, 90.0, 120.0, 180.0),
        include_nakshatra_ingresses=True,
        ayanamsa=ayanamsa,
        adapter=ad,
    )
    rashi_ingresses = transit_timeline.rashi_ingresses
    nak_ingresses = transit_timeline.nakshatra_ingresses
    major_aspects = transit_timeline.aspects
    mahapata_rep = solve_krantisamya_mahapata_windows(start_jd_month, end_jd_month, step_hours=12.0, adapter=ad)
    yogatara_rep = evaluate_yogatara_stellar_bheda_and_visibility(
        daily_rows[min(14, len(daily_rows) - 1)].jd_reference_ut,
        ayanamsa=ayanamsa,
        orb_deg=2.5,
        adapter=ad,
    )
    phenomena_summary = {
        "rashi_ingresses": rashi_ingresses,
        "nakshatra_ingresses": nak_ingresses,
        "major_aspects": major_aspects,
        "mahapata_report": mahapata_rep,
        "yogatara_report": yogatara_rep,
    }

    # Construct the 15-Step Worked Example for the 15th day of the month at 10:42:00 Local Time (= +5h 12m after 05:30 IST)
    sample_idx = min(14, len(daily_rows) - 1)
    row_d0 = daily_rows[sample_idx]
    sky_d0 = full_sky_rows[sample_idx]
    interp_hours = 5.2
    interp_fraction = interp_hours / 24.0
    jd_worked_ut = row_d0.jd_reference_ut + (interp_hours / 24.0)

    worked_planets: dict[str, Any] = {}
    for b in ("sun", "moon", "mars", "mercury", "jupiter", "venus", "saturn", "rahu", "ketu"):
        c0 = row_d0.planets[b]
        s0 = sky_d0[b]
        # 1st-order Trairashika linear interpolation: L_1(t) = L_0 + f * v_0
        manual_lon_1st = (c0.longitude_deg + interp_fraction * c0.speed_deg_per_day) % 360.0
        # 2nd-order Taylor/Bessel correction using instantaneous velocity v_0 and centered second difference Delta^2:
        # L_2(t) = L_1(t) + 0.5 * f^2 * Delta^2
        bessel_corr_deg = 0.5 * (interp_fraction ** 2) * (s0.second_difference_arcsec_per_day2 / 3600.0)
        manual_lon_2nd = (manual_lon_1st + bessel_corr_deg) % 360.0

        exact_pos = ad.calc_ut(jd_worked_ut, b, sidereal=True, ayanamsa=ayanamsa)
        exact_lon = exact_pos.longitude_deg % 360.0
        diff_arcsec = abs(((manual_lon_1st - exact_lon + 180.0) % 360.0) - 180.0) * 3600.0
        diff_2nd_arcsec = abs(((manual_lon_2nd - exact_lon + 180.0) % 360.0) - 180.0) * 3600.0
        nak_w = nakshatra_position(exact_lon)
        kp_w = kp_coordinate_lords(exact_lon)
        worked_planets[b] = {
            "tabulated_0530_dms": c0.classical_dms,
            "daily_motion_dms": c0.daily_motion_dms,
            "motion_increment_dms": format_daily_motion_dms(interp_fraction * c0.speed_deg_per_day),
            "manual_trairashika_dms": format_classical_rashi_dms(manual_lon_1st),
            "manual_bessel_2nd_order_dms": format_classical_rashi_dms(manual_lon_2nd),
            "software_exact_dms": format_classical_rashi_dms(exact_lon),
            "manual_vs_software_diff_arcsec": round(diff_arcsec, 2),
            "bessel_vs_software_diff_arcsec": round(diff_2nd_arcsec, 2),
            "nakshatra_pada": f"{nak_w.name} Pada {nak_w.pada}",
            "kp_lords": f"{kp_w.sign_lord} / {kp_w.star_lord} / {kp_w.sub_lord} / {kp_w.sub_sub_lord}",
            "d1_sign": varga_sign(exact_lon, "D1").sign_name,
            "d9_navamsa_sign": varga_sign(exact_lon, "D9").sign_name,
            "d10_dasamsa_sign": varga_sign(exact_lon, "D10").sign_name,
            "d60_shashtiamsa_sign": varga_sign(exact_lon, "D60").sign_name,
        }

    worked_houses = ad.houses_ut(jd_worked_ut, lat, lon, system="placidus", ayanamsa=ayanamsa)
    moon_exact_lon = ad.calc_ut(jd_worked_ut, "moon", sidereal=True, ayanamsa=ayanamsa).longitude_deg % 360.0
    moon_nak = nakshatra_position(moon_exact_lon)
    rem_deg_in_nak = (360.0 / 27.0) - moon_nak.degree_in_nakshatra
    rem_arcmin_in_nak = rem_deg_in_nak * 60.0
    maha_lord = moon_nak.vimshottari_ruler
    maha_total_years = float(VIMSHOTTARI_YEARS[maha_lord])
    balance_years = (rem_arcmin_in_nak / 800.0) * maha_total_years
    bal_y = int(balance_years)
    bal_m_rem = (balance_years - bal_y) * 12.0
    bal_m = int(bal_m_rem)
    bal_d = int(round((bal_m_rem - bal_m) * 30.0))

    p_day_worked = panchang_cal.days[sample_idx]
    vishesha_worked = compute_vishesha_lagnas_and_special_points(
        jd_worked_ut,
        lat,
        lon,
        sunrise_jd_ut=p_day_worked.sunrise_jd_ut,
        ayanamsa=ayanamsa,
        adapter=ad,
    )
    sun_w_lon = ad.calc_ut(jd_worked_ut, "sun", sidereal=True, ayanamsa=ayanamsa).longitude_deg % 360.0
    upagrahas_worked = compute_11_upagrahas(
        sun_w_lon,
        p_day_worked.sunrise_jd_ut,
        p_day_worked.sunset_jd_ut,
        jd_ut=jd_worked_ut,
        next_sunrise_jd=p_day_worked.sunrise_jd_ut + 1.0,
        vara_index=p_day_worked.vara_index,
        lagna_lon_deg=worked_houses.ascendant_deg,
        ascendant_fn=lambda j: ad.houses_ut(j, lat, lon, system="placidus", ayanamsa=ayanamsa).ascendant_deg,
    )
    sphutas_worked = compute_prashna_sphutas(
        worked_houses.ascendant_deg,
        sun_w_lon,
        moon_exact_lon,
        upagrahas_worked.gulika.longitude_deg,
        jupiter_deg=ad.calc_ut(jd_worked_ut, "jupiter", sidereal=True, ayanamsa=ayanamsa).longitude_deg % 360.0,
        venus_deg=ad.calc_ut(jd_worked_ut, "venus", sidereal=True, ayanamsa=ayanamsa).longitude_deg % 360.0,
        mars_deg=ad.calc_ut(jd_worked_ut, "mars", sidereal=True, ayanamsa=ayanamsa).longitude_deg % 360.0,
        rahu_deg=ad.calc_ut(jd_worked_ut, "rahu", sidereal=True, ayanamsa=ayanamsa).longitude_deg % 360.0,
    )
    kundali_worked = compute_vedic_chart_analysis(
        {
            p.capitalize(): ad.calc_ut(jd_worked_ut, p, sidereal=True, ayanamsa=ayanamsa).longitude_deg % 360.0
            for p in ("sun", "moon", "mars", "mercury", "jupiter", "venus", "saturn", "rahu", "ketu")
        },
        worked_houses.ascendant_deg,
        jd_ut=jd_worked_ut,
        sunrise_jd_ut=p_day_worked.sunrise_jd_ut,
        sunset_jd_ut=p_day_worked.sunset_jd_ut,
        ayanamsa_deg=ad.get_ayanamsa_ut(jd_worked_ut, mode=ayanamsa),
        ayanamsa_system=ayanamsa,
    )
    kalachakra_worked = compute_kalachakra_dasha(moon_exact_lon, jd_worked_ut)
    sahams_worked = compute_tajika_sahams(
        {
            p: ad.calc_ut(jd_worked_ut, p, sidereal=True, ayanamsa=ayanamsa).longitude_deg % 360.0
            for p in ("sun", "moon", "mars", "mercury", "jupiter", "venus", "saturn")
        },
        worked_houses.ascendant_deg,
        is_day_birth=True,
    )
    natal_lons_worked = {
        p: ad.calc_ut(jd_worked_ut, p, sidereal=True, ayanamsa=ayanamsa).longitude_deg % 360.0
        for p in ("sun", "moon", "mars", "mercury", "jupiter", "venus", "saturn", "rahu", "ketu")
    }
    frontier_topo_worked = compute_topocentric_relativistic_astrometry(
        jd_worked_ut,
        lat,
        lon,
        elevation_m=491.0,
        temperature_c=24.0,
        pressure_hpa=1008.0,
        ayanamsa=ayanamsa,
        adapter=ad,
    )
    frontier_retro_worked = solve_synodic_retrograde_loops_and_triple_passes(
        daily_rows[0].jd_reference_ut - 180.0,
        daily_rows[-1].jd_reference_ut + 180.0,
        natal_longitudes_deg={**natal_lons_worked, "ascendant": worked_houses.ascendant_deg},
        ayanamsa=ayanamsa,
        adapter=ad,
    )
    frontier_eclipse_worked = evaluate_lifetime_eclipse_natal_sensitivity(
        daily_rows[0].jd_reference_ut - 300.0,
        daily_rows[-1].jd_reference_ut + 120.0,
        natal_longitudes_deg={**natal_lons_worked, "ascendant": worked_houses.ascendant_deg},
        latitude_deg=lat,
        longitude_deg=lon,
        orb_deg=6.0,
        ayanamsa=ayanamsa,
        adapter=ad,
    )
    frontier_dashas_worked = compute_all_10_parashari_nakshatra_dashas(
        moon_exact_lon,
        worked_houses.ascendant_deg,
        sun_w_lon,
        natal_lons_worked,
        jd_worked_ut,
        is_day_birth=True,
        query_jd=jd_worked_ut + 365.2425 * 24.0,
    )
    frontier_prana_worked = compute_vimshottari_5_level_prana_chronometer(
        moon_exact_lon,
        jd_worked_ut,
        jd_worked_ut + 365.2425 * 24.0,
    )
    frontier_nadi_worked = compute_nadi_amsa_and_sudarshana_chakra(
        worked_houses.ascendant_deg,
        natal_lons_worked,
        jd_worked_ut,
        query_jd=jd_worked_ut + 365.2425 * 24.0,
    )
    frontier_muhurta_worked = solve_golden_muhurta_electional_windows(
        daily_rows[0].jd_reference_ut,
        daily_rows[min(6, len(daily_rows) - 1)].jd_reference_ut,
        latitude_deg=lat,
        longitude_deg=lon,
        natal_moon_lon_deg=moon_exact_lon,
        step_minutes=120,
        top_k=15,
        ayanamsa=ayanamsa,
        adapter=ad,
    )
    frontier_dignity_worked = compute_continuous_dignity_and_heliacal_phenomena(
        jd_worked_ut,
        lat,
        lon,
        ayanamsa=ayanamsa,
        adapter=ad,
    )
    frontier_sbc_worked = compute_sarvatobhadra_81_ray_vedha(
        jd_worked_ut,
        moon_exact_lon,
        natal_nama_akshara="a",
        ayanamsa=ayanamsa,
        adapter=ad,
    )
    frontier_pinda_worked = compute_shodhya_pinda_transit_triggers_and_harmonic_yogas(
        jd_worked_ut,
        lat,
        lon,
        ayanamsa=ayanamsa,
        adapter=ad,
    )

    worked_example = {
        "civil_date": row_d0.civil_date,
        "birth_time_local": "10:42:00 IST (UTC+05:30)",
        "elapsed_after_0530_ist": "5 hours 12 minutes (13 Ghatis 00 Palas)",
        "trairashika_fraction": round(interp_fraction, 6),
        "observer_location": f"Lat {lat:.4f} deg, Lon {lon:.4f} deg",
        "ascendant_dms": format_classical_rashi_dms(worked_houses.ascendant_deg),
        "mc_10th_cusp_dms": format_classical_rashi_dms(worked_houses.mc_deg),
        "house_cusps_dms": [format_classical_rashi_dms(c) for c in worked_houses.cusps_deg],
        "moon_nakshatra": f"{moon_nak.name} Pada {moon_nak.pada} (Lord: {maha_lord})",
        "remaining_arcminutes_bhogyamsha": round(rem_arcmin_in_nak, 2),
        "vimshottari_dasha_balance_at_birth": f"{maha_lord} Mahadasha: {bal_y} Years, {bal_m} Months, {bal_d} Days remaining",
        "planets": worked_planets,
        "vishesha_report": vishesha_worked,
        "upagrahas_report": upagrahas_worked,
        "sphutas_report": sphutas_worked,
        "kundali_bundle": kundali_worked,
        "sahams_report": sahams_worked,
        "kalachakra_report": kalachakra_worked,
        "frontier_topo_report": frontier_topo_worked,
        "frontier_retro_report": frontier_retro_worked,
        "frontier_eclipse_report": frontier_eclipse_worked,
        "frontier_dashas_report": frontier_dashas_worked,
        "frontier_prana_report": frontier_prana_worked,
        "frontier_nadi_report": frontier_nadi_worked,
        "frontier_muhurta_report": frontier_muhurta_worked,
        "frontier_dignity_report": frontier_dignity_worked,
        "frontier_sbc_report": frontier_sbc_worked,
        "frontier_pinda_report": frontier_pinda_worked,
    }

    receipt_payload = {
        "engine": "ephemeris_oss.almanac.human_ephemeris",
        "version": __version__,
        "year": yr,
        "month": mo,
        "chapter_count": 30,
        "latitude_deg": round(lat, 6),
        "longitude_deg": round(lon, 6),
        "ayanamsa": ayanamsa,
        "days_count": len(daily_rows),
        "first_day_sun_dms": daily_rows[0].planets["sun"].classical_dms,
        "last_day_moon_dms": daily_rows[-1].planets["moon"].classical_dms,
        "worked_ascendant_dms": worked_example["ascendant_dms"],
    }
    receipt_sha256 = canonical_hash(receipt_payload)

    return HumanManualEphemerisCompendium(
        year=yr,
        month=mo,
        reference_epoch_label="05:30:00 IST (00:00:00 UTC)",
        observer_latitude_deg=lat,
        observer_longitude_deg=lon,
        tz_offset_hours=tz_off,
        ayanamsa_mode=ayanamsa,
        daily_rows=tuple(daily_rows),
        worked_example=worked_example,
        receipt=receipt_payload,
        receipt_sha256=receipt_sha256,
        full_sky_rows=tuple(full_sky_rows),
        phenomena_summary=phenomena_summary,
        chapter_count=30,
    )


def _render_compendium_markdown(comp: HumanManualEphemerisCompendium) -> str:
    """Render the complete 30-Chapter Human-Readable Classical Ephemeris & Jyotish Academy Master Compendium."""
    lines: list[str] = []
    ad = EphemerisAdapter()
    jd_epoch = comp.daily_rows[0].jd_reference_ut

    lines.append(
        f"# RDG Ephemeris — Human-Readable Classical *Nirayana* & *Sayana* Ephemeris & Pt. Maheshji's Jyotish Academy Manual Calculation Compendium ({comp.year}-{comp.month:02d})"
    )
    lines.append("")
    lines.append(
        "> **For Practising Jyotishis, Positional Astronomers, Classical Researchers, and Students of Pt. Maheshji's Jyotish Academy:**\n"
        "> Before computers existed, every master astrologer cast a *Kundali* (natal chart), *Shodashvarga* (16 divisional charts), "
        "*Panchanga* (5-limb daily almanac), *Vishesha Lagnas* (8 special ascendants), *Upagrahas* (11 shadow planets), "
        "*KP 249 Sub-Lords*, *Jaimini Arudha Padas & Chara Karakas*, *Vimshottari/Yogini/Ashtottari/Kalachakra Dashas*, "
        "*Shadbala* (6-fold planetary strength), *Ashtakavarga* (337-bindu transit grid), *Ayurdaya* (longevity), and "
        "*Tajika Varshphal* (annual solar return with 36 Sahams) **entirely by hand** using printed ephemeris tables. "
        "This 30-chapter master volume restores that unbroken lineage with sub-arcsecond NASA JPL DE440/DE441 astronomical precision."
    )
    lines.append("")
    lines.append("### Master Document Metadata & Cryptographic Provenance Receipt")
    lines.append(f"- **Ephemeris Month & Year:** `{comp.year}-{comp.month:02d}` (`30 Complete Chapters`)")
    lines.append(f"- **Daily Tabular Reference Epoch:** `{comp.reference_epoch_label}`")
    lines.append(
        f"- **Reference Meridian / Location:** Latitude `{comp.observer_latitude_deg:.4f}°`, "
        f"Longitude `{comp.observer_longitude_deg:.4f}°` (UTC`+{comp.tz_offset_hours:.2f}h` — Ujjain Mahakaleshwar Prime Meridian)"
    )
    lines.append(f"- **Primary Sidereal Ayanamsha:** `{comp.ayanamsa_mode}` (Chitrapaksha / IAE 1989 Lahiri Standard + 25-Ayanamsha Conversion Table in Chapter 1)")
    lines.append(f"- **Astronomical Kernel Backbone:** NASA JPL DE440 / DE441 + IAU 2006/2000A Precession-Nutation (`ephemeris-oss v{__version__}`)")
    lines.append(f"- **Cryptographic SHA-256 Receipt:** `sha256:{comp.receipt_sha256}`")
    lines.append("")

    # =========================================================================
    # CHAPTER 1: Fundamental Astronomical Constants, Julian Days & 25 Ayanamshas
    # =========================================================================
    lines.append("## Chapter 1 — Fundamental Astronomical Constants, Julian Day Tables (`1900–2050`), ΔT, & 25-Ayanamsha Master Conversion Table")
    lines.append("")
    lines.append("### Table 1A — Fundamental Astronomical & Vedic Siddhantic Constants")
    lines.append("")
    lines.append("| Constant / Parameter | Exact Numerical Value | Classical / IAU Standard Reference |")
    lines.append("|---|---|---|")
    lines.append("| **J2000.0 Fundamental Epoch** | `JD 2451545.0 TT` (`2000-01-01 12:00:00 TT`) | IAU 2006 / 2000A Standard Epoch |")
    lines.append("| **Kali Yuga Fundamental Epoch** | `JD 588465.5 UT` (`3102 BCE Feb 18 00:00 Ujjain`) | *Surya Siddhanta* & *Aryabhatiya* |")
    lines.append("| **Astronomical Unit (`1 AU`)** | `149,597,870.700 km` (exact) | IAU 2012 Resolution B2 |")
    lines.append("| **Speed of Light (`c`)** | `299,792.458 km/s` (`173.144632674 AU/day`) | IAU / SI Exact Constant |")
    lines.append("| **Mean Obliquity at J2000.0 (`ε₀`)** | `23° 26' 21.406\"` (`84381.406\"`) | Capitaine et al. (2003) / IAU 2006 |")
    lines.append("| **General Precession Rate (`p_A` at J2000)** | `50.28796195\" / Julian year` (`1° in 71.5877 years`) | IAU 2006 Precession Model |")
    lines.append("| **Mean Tropical Year (`Y_trop`)** | `365.24218967 days` (`365d 05h 48m 45.2s`) | Simon et al. (1994) |")
    lines.append("| **Mean Sidereal Year (`Y_sid`)** | `365.256363004 days` (`365d 06h 09m 09.8s`) | IAU Standard Sidereal Year |")
    lines.append("| **Surya Siddhanta Sidereal Year** | `365.25875648 days` (`365d 15g 31p 31.4v`) | `1,577,917,828 / 4,320,000` Savana days |")
    lines.append("| **Mean Synodic Lunar Month** | `29.530588853 days` (`29d 12h 44m 02.9s`) | Mean New Moon to New Moon |")
    lines.append("| **Mean Sidereal Lunar Month** | `27.321661547 days` (`27d 07h 43m 11.6s`) | `1 Nakshatra ≈ 24h 18m` |")
    lines.append("| **Vedic Time Units (*Ghati / Pala / Vipala*)** | `1 Day = 60 Ghatis = 3,600 Palas = 216,000 Vipalas` | `1 Ghati = 24 min`, `1 Pala = 24 sec`, `1 Vipala = 0.4 sec` |")
    lines.append("")

    lines.append("### Table 1B — Master 25-Ayanamsha Reference & Conversion Table (Evaluated at Epoch `2026-11-01 00:00 UTC`)")
    lines.append("")
    lines.append(
        "**How to Convert Any Position in This Compendium to Another Ayanamsha:** Every sidereal table in this book "
        "is printed in **Chitrapaksha / Lahiri (`IAE 1989`)**. To convert any longitude to another Ayanamsha, simply "
        "**subtract `Δ = (Target Ayanamsha − Lahiri Ayanamsha)`** listed in the column below:"
    )
    lines.append("")
    lines.append("| # | Ayanamsha Key | Canonical Name & Lineage | Value on `2026-11-01` (`DD° MM' SS\"`) | Decimal (`deg`) | Offset vs Lahiri (`Δ = A − A_Lahiri`) | Precession / Anchor Model |")
    lines.append("|---|---|---|---|---|---|---|")
    lahiri_base = ad.get_ayanamsa_ut(jd_epoch, mode="lahiri")
    ay_idx = 0
    for ay_key, ay_def in AYANAMSA_CATALOG.items():
        try:
            val_deg = ad.get_ayanamsa_ut(jd_epoch, mode=ay_key)
        except Exception:
            continue
        ay_idx += 1
        tot_s = int(round(val_deg * 3600.0))
        ad_d = tot_s // 3600
        ad_m = (tot_s % 3600) // 60
        ad_s = (tot_s % 3600) % 60
        delta_deg = val_deg - lahiri_base
        delta_sign = "+" if delta_deg >= 0 else "-"
        d_abs_s = int(round(abs(delta_deg) * 3600.0))
        dd_d = d_abs_s // 3600
        dd_m = (d_abs_s % 3600) // 60
        dd_s = (d_abs_s % 3600) % 60
        lines.append(
            f"| **{ay_idx:02d}** | `{ay_key}` | **{ay_def.label}** | `{ad_d:02d}° {ad_m:02d}' {ad_s:02d}\"` | "
            f"`{val_deg:.6f}°` | `{delta_sign}{dd_d:02d}° {dd_m:02d}' {dd_s:02d}\"` | {ay_def.model} |"
        )
    lines.append("")

    lines.append("### Table 1C — Manual Julian Day Number (`JDN`) Lookup Table for Years `1900` to `2050` (`Jan 0.0 UTC`)")
    lines.append("")
    lines.append(
        "**How to Compute Any Julian Date (`JD`) by Hand:**\n"
        "`JD = JD_Jan0.0(Year) + Month Offset (Table 1D) + Day of Month + (UTC Hours / 24)`"
    )
    lines.append("")
    lines.append("| Year | `JD (Jan 0.0)` | Year | `JD (Jan 0.0)` | Year | `JD (Jan 0.0)` | Year | `JD (Jan 0.0)` | Year | `JD (Jan 0.0)` |")
    lines.append("|---|---|---|---|---|---|---|---|---|---|")
    for base_y in range(1900, 1930):
        row_cells = []
        for col_offset in (0, 30, 60, 90, 120):
            y_val = base_y + col_offset
            if y_val <= 2050:
                jd_jan0 = ad.julday(y_val, 1, 1, 0.0) - 1.0
                leap_mark = "*" if (y_val % 4 == 0 and (y_val % 100 != 0 or y_val % 400 == 0)) else ""
                row_cells.append(f"**{y_val}{leap_mark}** | `{jd_jan0:.1f}`")
            else:
                row_cells.append("— | —")
        lines.append("| " + " | ".join(row_cells) + " |")
    lines.append("")

    lines.append("### Table 1D — Cumulative Month Day-Offsets & Historical `ΔT = TT − UT1` Table")
    lines.append("")
    lines.append("| Month | Regular Year Offset | Leap Year (`*`) Offset | Historical Epoch | `ΔT = TT − UT1` (Seconds) | `ΔT` (Minutes) |")
    lines.append("|---|---|---|---|---|---|")
    month_names = ("January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December")
    reg_offsets = (0, 31, 59, 90, 120, 151, 181, 212, 243, 273, 304, 334)
    leap_offsets = (0, 31, 60, 91, 121, 152, 182, 213, 244, 274, 305, 335)
    dt_epochs = (-500, 0, 500, 1000, 1500, 1700, 1800, 1900, 1950, 2000, 2026, 2100)
    for m_i in range(12):
        ep_y = dt_epochs[m_i]
        dt_sec = estimate_delta_t(float(ep_y)).seconds
        ep_label = f"{abs(ep_y)} BCE" if ep_y < 0 else (f"{ep_y} CE" if ep_y > 0 else "1 BCE / 0")
        lines.append(
            f"| **{month_names[m_i]}** | `+{reg_offsets[m_i]} days` | `+{leap_offsets[m_i]} days` | "
            f"**{ep_label}** | `{dt_sec:+.1f} s` | `{dt_sec / 60.0:+.2f} min` |"
        )
    lines.append("")

    # =========================================================================
    # CHAPTER 2 (Section 1): Complete Daily Sidereal & Tropical Longitude Grid
    # =========================================================================
    lines.append("## Chapter 2 — Section 1 — Daily Sidereal (*Nirayana*) & Tropical (*Sayana*) Planetary Ephemeris Grid (`05:30 IST / 00:00 UTC`)")
    lines.append("")
    lines.append(
        "**How to Read This Grid:** Each cell gives (1) the exact sidereal longitude in `Rashi DD° MM' SS\"`, "
        "(2) the 27-Nakshatra and Pada (`P1..P4`) plus KP Sub-Lord, and (3) the signed 24-hour daily motion "
        "(`±DD° MM' SS\"/d`) with status flags (`D` = Direct, `R` = Retrograde/*Vakri*, `S` = Stationary, "
        "`C` = Combust/*Asta*, `V` = *Vargottama*, `PN` = *Pushkara Navamsa*, `MB` = *Mrityu Bhaga*)."
    )
    lines.append("")
    lines.append("### Table 2A — Daily *Navagraha* Sidereal Longitudes, Nakshatra-Padas, & Daily Angular Velocities")
    lines.append("")
    lines.append(
        "| Date | Vara | Lahiri Ayanamsha | LST | Surya (Sun) | Chandra (Moon) | Mangala (Mars) | Budha (Mercury) | Guru (Jupiter) | Shukra (Venus) | Shani (Saturn) | Mean Rahu | True Rahu | Ketu |"
    )
    lines.append("|---|---|---|---|---|---|---|---|---|---|---|---|---|---|")
    for r in comp.daily_rows:
        cells: list[str] = [
            f"`{r.civil_date}`",
            r.vara_name.split(" ")[0],
            f"`{r.ayanamsa_dms}`",
            f"`{r.local_sidereal_time_hms}`",
        ]
        for b in ("sun", "moon", "mars", "mercury", "jupiter", "venus", "saturn", "rahu", "true_rahu", "ketu"):
            c = r.planets[b]
            cells.append(
                f"**{c.classical_dms}**<br/>{c.nakshatra_name} P{c.pada} ({c.status_flags})<br/>`{c.daily_motion_dms}/d`"
            )
        lines.append("| " + " | ".join(cells) + " |")
    lines.append("")

    lines.append("### Table 2B — Daily Outer Planets (*Aruna / Uranus, Varuna / Neptune, Yama / Pluto*), Tropical (*Sayana*) Luminaries, & Second-Order Tabular Differences (`Δ²λ`)")
    lines.append("")
    lines.append(
        "| Date | Kali *Ahargana* | Tropical Sun (`λ_trop`) | Tropical Moon (`λ_trop`) | Uranus (*Aruna*) Sidereal | Neptune (*Varuna*) Sidereal | Pluto (*Yama*) Sidereal | Moon `Δ²λ` (`\"/d²`) | Mercury `Δ²λ` (`\"/d²`) | Venus `Δ²λ` (`\"/d²`) | Mars `Δ²λ` (`\"/d²`) |"
    )
    lines.append("|---|---|---|---|---|---|---|---|---|---|---|")
    for idx_r, r in enumerate(comp.daily_rows):
        sky = comp.full_sky_rows[idx_r]
        lines.append(
            f"| `{r.civil_date}` | `{r.ahargana_kali_days:.1f}` | `{sky['sun'].tropical_dms}` | `{sky['moon'].tropical_dms}` | "
            f"**{sky['uranus'].sidereal_dms}** (`{sky['uranus'].daily_motion_dms}/d`) | "
            f"**{sky['neptune'].sidereal_dms}** (`{sky['neptune'].daily_motion_dms}/d`) | "
            f"**{sky['pluto'].sidereal_dms}** (`{sky['pluto'].daily_motion_dms}/d`) | "
            f"`{sky['moon'].second_difference_arcsec_per_day2:+.1f}\"` | "
            f"`{sky['mercury'].second_difference_arcsec_per_day2:+.1f}\"` | "
            f"`{sky['venus'].second_difference_arcsec_per_day2:+.1f}\"` | "
            f"`{sky['mars'].second_difference_arcsec_per_day2:+.1f}\"` |"
        )
    lines.append("")

    # =========================================================================
    # CHAPTER 3: Complete Daily Spherical & Physical Ephemeris Grid
    # =========================================================================
    lines.append("## Chapter 3 — Daily Spherical & Physical Ephemeris Grid (Declination `δ`, Right Ascension `α`, Ecliptic Latitude `β`, Distance `R`, Parallax, Diameter, Phase & Magnitude)")
    lines.append("")
    lines.append(
        "**Why Spherical & Physical Coordinates Are Essential for Manual Jyotish:**\n"
        "- **Declination (`δ` / *Kranti*):** Required to compute *Ayana Bala* in *Shadbala*, Parallel/Contra-Parallel Declination aspects (*Kranti Yoga*), and *Vyatipata / Vaidhriti Mahapata*.\n"
        "- **Ecliptic Latitude (`β` / *Shara / Vikshepa*):** Required to adjudicate the winner of a *Graha Yuddha* (Planetary War — the planet with the more northern latitude wins) and *Nakshatra Tara Bheda*.\n"
        "- **True Distance (`R` in AU), Horizontal Parallax (`HP`), Apparent Diameter (`\"`), & Visual Magnitude (`V_mag`):** Required for topocentric Moon correction, eclipse contact sizing, and *Cheshta / Brihat Samhita* brightness diagnostics."
    )
    lines.append("")
    lines.append("### Table 3A — Daily Declination (`δ` / *Kranti*) & Right Ascension (`α`) Across the *Navagrahas* (`05:30 IST`)")
    lines.append("")
    lines.append("| Date | Sun `δ / α` | Moon `δ / α` | Mars `δ / α` | Mercury `δ / α` | Jupiter `δ / α` | Venus `δ / α` | Saturn `δ / α` | Rahu `δ` |")
    lines.append("|---|---|---|---|---|---|---|---|---|")
    for idx_r, r in enumerate(comp.daily_rows):
        sky = comp.full_sky_rows[idx_r]
        lines.append(
            f"| `{r.civil_date}` | `{sky['sun'].declination_dms}`<br/>`{sky['sun'].right_ascension_hms}` | "
            f"`{sky['moon'].declination_dms}`<br/>`{sky['moon'].right_ascension_hms}` | "
            f"`{sky['mars'].declination_dms}`<br/>`{sky['mars'].right_ascension_hms}` | "
            f"`{sky['mercury'].declination_dms}`<br/>`{sky['mercury'].right_ascension_hms}` | "
            f"`{sky['jupiter'].declination_dms}`<br/>`{sky['jupiter'].right_ascension_hms}` | "
            f"`{sky['venus'].declination_dms}`<br/>`{sky['venus'].right_ascension_hms}` | "
            f"`{sky['saturn'].declination_dms}`<br/>`{sky['saturn'].right_ascension_hms}` | "
            f"`{sky['rahu'].declination_dms}` |"
        )
    lines.append("")

    lines.append("### Table 3B — Daily Ecliptic Latitude (`β` / *Shara*), Geocentric Distance (`R` in AU), Lunar Parallax (`HP`), Disk Illumination (`%`), & Visual Magnitude (`V_mag`)")
    lines.append("")
    lines.append("| Date | Moon `β` (`DMS`) | Moon `HP` / Diam | Moon Illum `%` | Mars `β` / Dist (`AU`) / `V_mag` | Mercury `β` / Dist (`AU`) / `V_mag` | Jupiter `β` / Dist (`AU`) / `V_mag` | Venus `β` / Dist (`AU`) / `V_mag` | Saturn `β` / Dist (`AU`) / `V_mag` |")
    lines.append("|---|---|---|---|---|---|---|---|---|")
    for idx_r, r in enumerate(comp.daily_rows):
        sky = comp.full_sky_rows[idx_r]
        lines.append(
            f"| `{r.civil_date}` | `{sky['moon'].ecliptic_latitude_dms}` | "
            f"`{sky['moon'].horizontal_parallax_arcsec:.1f}\"` / `{sky['moon'].apparent_diameter_arcsec:.1f}\"` | "
            f"**`{sky['moon'].illuminated_fraction_pct:.1f}%`** | "
            f"`{sky['mars'].ecliptic_latitude_dms}`<br/>`{sky['mars'].distance_au:.4f} AU` (`{sky['mars'].visual_magnitude:+.2f}m`) | "
            f"`{sky['mercury'].ecliptic_latitude_dms}`<br/>`{sky['mercury'].distance_au:.4f} AU` (`{sky['mercury'].visual_magnitude:+.2f}m`) | "
            f"`{sky['jupiter'].ecliptic_latitude_dms}`<br/>`{sky['jupiter'].distance_au:.4f} AU` (`{sky['jupiter'].visual_magnitude:+.2f}m`) | "
            f"`{sky['venus'].ecliptic_latitude_dms}`<br/>`{sky['venus'].distance_au:.4f} AU` (`{sky['venus'].visual_magnitude:+.2f}m`) | "
            f"`{sky['saturn'].ecliptic_latitude_dms}`<br/>`{sky['saturn'].distance_au:.4f} AU` (`{sky['saturn'].visual_magnitude:+.2f}m`) |"
        )
    lines.append("")

    # =========================================================================
    # CHAPTER 4: Monthly Astronomical & Astrological Phenomena Almanac
    # =========================================================================
    lines.append("## Chapter 4 — Monthly Astronomical & Astrological Phenomena Almanac (Exact Sign Ingresses, Nakshatra Ingresses, Synodic Aspects, & *Krantisamya Mahapata* Windows)")
    lines.append("")
    phen = comp.phenomena_summary or {}
    lines.append("### Table 4A — Exact Planetary Sign Ingresses (*Rashi Sankranti*) During the Month")
    lines.append("")
    lines.append("| Planet | From Rashi | To Rashi | Exact Ingress Longitude | Exact UTC Timestamp | Exact Julian Date (`JD UT`) | Direction |")
    lines.append("|---|---|---|---|---|---|---|")
    r_ing = phen.get("rashi_ingresses", ())
    if r_ing:
        for ev in r_ing:
            lines.append(
                f"| **{ev.body}** | {ev.from_name} | **{ev.to_name}** | `{ev.longitude_deg:.4f}°` | "
                f"`{ev.iso_utc}` | `{ev.jd_ut:.6f}` | {'Retrograde Ingress' if ev.is_retrograde else 'Direct Ingress'} |"
            )
    else:
        lines.append("| *None* | — | — | — | — | — | — |")
    lines.append("")

    lines.append("### Table 4B — Exact Planetary *Nakshatra* Ingresses During the Month")
    lines.append("")
    lines.append("| Planet | From Nakshatra | To Nakshatra | Exact UTC Timestamp | Exact Julian Date (`JD UT`) | Motion |")
    lines.append("|---|---|---|---|---|---|")
    n_ing = phen.get("nakshatra_ingresses", ())
    if n_ing:
        for ev in n_ing[:40]:
            lines.append(
                f"| **{ev.body}** | {ev.from_name} | **{ev.to_name}** | `{ev.iso_utc}` | "
                f"`{ev.jd_ut:.6f}` | {'Retrograde' if ev.is_retrograde else 'Direct'} |"
            )
    else:
        lines.append("| *None* | — | — | — | — | — |")
    lines.append("")

    lines.append("### Table 4C — Exact Synodic Planetary Aspects (`0°, 60°, 90°, 120°, 180°`) During the Month")
    lines.append("")
    lines.append("| Body 1 | Body 2 | Aspect Type | Exact Angle | Body 1 Longitude | Body 2 Longitude | Exact UTC Timestamp |")
    lines.append("|---|---|---|---|---|---|---|")
    asp_list = phen.get("major_aspects", ())
    if asp_list:
        for ev in asp_list[:45]:
            lines.append(
                f"| **{ev.body_a}** | **{ev.body_b}** | **{ev.aspect_name}** | `{ev.aspect_angle_deg:.0f}°` | "
                f"`{format_classical_rashi_dms(ev.longitude_a_deg)}` | `{format_classical_rashi_dms(ev.longitude_b_deg)}` | `{ev.iso_utc}` |"
            )
    else:
        lines.append("| *None* | — | — | — | — | — | — |")
    lines.append("")

    lines.append("### Table 4D — Exact *Surya Siddhanta Krantisamya* (*Vyatipata* & *Vaidhriti Mahapata*) Declination-Equality Windows")
    lines.append("")
    lines.append("| Mahapata Type | Classical Condition | Peak Exact JD (`UT`) | Window Start (`JD UT`) | Window End (`JD UT`) | Sun Declination (`δ_Sun`) | Moon Declination (`δ_Moon`) |")
    lines.append("|---|---|---|---|---|---|---|")
    mp_rep = phen.get("mahapata_report")
    if mp_rep and mp_rep.events:
        for mp in mp_rep.events:
            cond = "`δ_Sun = +δ_Moon` (Same Hemisphere)" if mp.mahapata_type == "Vyatipata" else "`δ_Sun = -δ_Moon` (Opposite Hemisphere)"
            lines.append(
                f"| **{mp.mahapata_type} Mahapata** | {cond} | `{mp.exact_jd_ut:.5f}` | "
                f"`{mp.window_start_jd_ut:.5f}` | `{mp.window_end_jd_ut:.5f}` | "
                f"`{mp.sun_declination_deg:+.4f}°` | `{mp.moon_declination_deg:+.4f}°` |"
            )
    else:
        lines.append("| *None in interval* | — | — | — | — | — | — |")
    lines.append("")

    # =========================================================================
    # CHAPTER 5 (Section 2): Daily Sunrise-Anchored Drik Panchanga & Muhurta
    # =========================================================================
    lines.append("## Chapter 5 — Section 2 — Daily Sunrise-Anchored *Drik Panchanga*, *Ghati-Pala* Almanac, & *Muhurta* Table")
    lines.append("")
    lines.append(
        "**Vedic Timekeeping Conversion:** `1 Solar Day = 24 Hours = 60 Ghatis (Nadis)`; "
        "`1 Hour = 2.5 Ghatis`; `1 Ghati = 24 Minutes = 60 Palas (Vinadis)`; "
        "`1 Pala = 24 Seconds`."
    )
    lines.append("")
    lines.append(
        "| Date | Vara | Sunrise | Sunset | *Dinamana* (`Hours / Ghatis`) | Sunrise Tithi | Tithi Ends (`Clock / Ghati-Pala`) | Sunrise Nakshatra | Sunrise Yoga | Sunrise Karana | *Rahu Kala* | *Abhijit Muhurta* | Observances (*Vratas*) |"
    )
    lines.append("|---|---|---|---|---|---|---|---|---|---|---|---|---|")
    for r in comp.daily_rows:
        vrata_str = ", ".join(r.vratas) if r.vratas else "—"
        lines.append(
            f"| `{r.civil_date}` | {r.vara_name} | `{r.sunrise_local_hms}` | `{r.sunset_local_hms}` | "
            f"`{r.dinamana_hours:.2f}h` (`{r.dinamana_ghati_pala}`) | **{r.tithi_name}** | "
            f"`{r.tithi_end_local_hm}` (`{r.tithi_end_ghati_pala}`) | {r.nakshatra_at_sunrise} | "
            f"{r.yoga_at_sunrise} | {r.karana_at_sunrise} | `{r.rahu_kala_window}` | "
            f"`{r.abhijit_muhurta_window}` | {vrata_str} |"
        )
    lines.append("")

    # =========================================================================
    # CHAPTER 6 (Section 3): Manual Spashta Graha Interpolation (1st & 2nd Order)
    # =========================================================================
    lines.append("## Chapter 6 — Section 3 — Manual *Spashta Graha* Interpolation Compendium (1st-Order *Trairashika* & 2nd-Order Bessel Lunar Tables)")
    lines.append("")
    lines.append(
        "### 6.1 First-Order *Trairashika* (Rule of Three) & Second-Order Bessel Formula\n"
        "- **First-Order Formula (Sufficient for Sun, Mars, Mercury, Jupiter, Venus, Saturn, Rahu, Ketu to `< 0.5\"`):**\n"
        "  `λ₁(t) = λ(05:30 IST) + f × v_day`, where `f = Δt_hours / 24 = ΔG_ghatis / 60`\n"
        "- **Second-Order Quadratic Formula (For Sub-Arcsecond Manual Interpolation of the Fast-Moving Moon using Instantaneous Velocity `v_day`):**\n"
        "  `λ₂(t) = λ₁(t) + (f² / 2) × Δ²λ`\n"
        "  where `Δ²λ` is printed in **Table 2B** and the quadratic multiplier `B₂(f) = f² / 2` is printed in **Table 6A** below."
    )
    lines.append("")
    lines.append("### Table 6A — Complete 96-Row 15-Minute (`00:00` to `24:00`) *Trairashika* Fraction (`f`), *Ghati-Pala*, & 2nd-Difference Coefficient (`B₂(f)`) Table")
    lines.append("")
    lines.append("| Elapsed Time (`HH:MM`) | Elapsed *Ghati-Pala* | Fraction `f = Δt / 24` | Quadratic `B₂(f) = f² / 2` | Sun Incr (`+59'08\"/d`) | Mean Moon Incr (`+13°10'35\"/d`) | Elapsed Time (`HH:MM`) | Elapsed *Ghati-Pala* | Fraction `f = Δt / 24` | Quadratic `B₂(f) = f² / 2` | Sun Incr (`+59'08\"/d`) | Mean Moon Incr (`+13°10'35\"/d`) |")
    lines.append("|---|---|---|---|---|---|---|---|---|---|---|---|")
    for q_idx in range(1, 49):
        # Left column: 00:15 to 12:00; Right column: 12:15 to 24:00
        row_pair = []
        for k_q in (q_idx, q_idx + 48):
            hrs = k_q * 0.25
            hh = int(hrs)
            mm = int(round((hrs - hh) * 60))
            f_val = hrs / 24.0
            b2_val = 0.5 * (f_val ** 2)
            gp_s = format_ghati_pala(hrs)
            sun_i = format_daily_motion_dms(f_val * (59.1333 / 60.0))
            moon_i = format_daily_motion_dms(f_val * 13.17639)
            row_pair.append(f"`{hh:02d}:{mm:02d}` | `{gp_s}` | **`{f_val:.5f}`** | `{b2_val:+.5f}` | `{sun_i}` | `{moon_i}`")
        lines.append("| " + " | ".join(row_pair) + " |")
    lines.append("")

    # =========================================================================
    # CHAPTER 7: Master Tables of Ascendants (Lagna) & 10th House Across Latitudes
    # =========================================================================
    lines.append("## Chapter 7 — Master Tables of Ascendants (*Udaya Lagna*), 10th House Midheaven (*Madhya Lagna*), & *Sripathi Bhava Chalit* Across World Latitudes")
    lines.append("")
    lines.append(
        "**How to Find the Exact Sidereal Ascendant (*Udaya Lagna*) and 10th Cusp (*Madhya Lagna*) from Table 7A:**\n"
        "1. Take the **Local Sidereal Time (LST)** at `05:30 IST` from **Table 2A** (already computed for the compendium reference meridian `"
        f"{comp.observer_longitude_deg:.4f}°`).\n"
        f"2. Add the time elapsed from `05:30 IST` to Birth Time, plus `10 seconds per hour` of elapsed solar time (`+3m 56.56s` per 24h), and adjust by `(Observer Longitude - {comp.observer_longitude_deg:.4f}°) × 4 minutes/degree` to get **Birth Local Sidereal Time (RAMC)**.\n"
        "3. Look up the Birth LST row in **Table 7A** under your city's latitude column and subtract `(Current Lahiri Ayanamsha - 24° 13' 55\")` if casting for another century."
    )
    lines.append("")
    lines.append("### Table 7A — Master Sidereal Ascendant (*Udaya Lagna*) & 10th Cusp (*MC*) Lookup Grid (`00h 00m` to `23h 52m` LST across 9 World Latitudes, Lahiri `2026` Epoch)")
    lines.append("")
    lines.append(
        "| LST (`HH:MM`) | RAMC (`°`) | Sidereal 10th Cusp (*MC*) | `0°00'` Equator (*Lanka*) | `13°05'N` Chennai / Bengaluru | `19°05'N` Mumbai | `23°11'N` Ujjain / Kolkata | `28°37'N` New Delhi | `34°03'N` Los Angeles | `40°43'N` New York | `43°39'N` Toronto | `51°30'N` London |"
    )
    lines.append("|---|---|---|---|---|---|---|---|---|---|---|---|")
    eps_rad = math.radians(23.4392911)
    ay_ref = lahiri_base
    world_lats = (0.0, 13.0827, 19.0760, 23.1765, 28.6139, 34.0522, 40.7128, 43.6532, 51.5074)
    for step_ramc in range(0, 360, 4):  # Every 4 degrees = 16 minutes of Sidereal Time (90 rows covering 24h)
        ramc_deg = float(step_ramc)
        lst_tot_min = step_ramc * 4
        lst_hh = lst_tot_min // 60
        lst_mm = lst_tot_min % 60
        ramc_rad = math.radians(ramc_deg)
        # Tropical MC: tan(MC) = tan(RAMC) / cos(eps)
        mc_trop = math.degrees(math.atan2(math.sin(ramc_rad), math.cos(ramc_rad) * math.cos(eps_rad))) % 360.0
        mc_sid = (mc_trop - ay_ref) % 360.0
        lat_cells = []
        for w_lat in world_lats:
            phi_rad = math.radians(w_lat)
            # Standard spherical astronomy Ascendant formula:
            # tan(lambda_asc) = cos(RAMC) / (-sin(RAMC)*cos(eps) - tan(phi)*sin(eps))
            y_asc = math.cos(ramc_rad)
            x_asc = -math.sin(ramc_rad) * math.cos(eps_rad) - math.tan(phi_rad) * math.sin(eps_rad)
            asc_trop = math.degrees(math.atan2(y_asc, x_asc)) % 360.0
            asc_sid = (asc_trop - ay_ref) % 360.0
            lat_cells.append(f"`{format_classical_rashi_dms(asc_sid, compact_sign_number=True)}`")
        lines.append(
            f"| **`{lst_hh:02d}h {lst_mm:02d}m`** | `{ramc_deg:03.0f}°` | `{format_classical_rashi_dms(mc_sid, compact_sign_number=True)}` | "
            + " | ".join(lat_cells) + " |"
        )
    lines.append("")

    lines.append("### Table 7B — Classical *Lankodaya* (Equatorial Rising Durations) & *Charakhanda* Latitude Adjustments")
    lines.append("")
    lines.append("| Rashi # | Sanskrit Rashi | Western Sign | *Lankodaya* (*Vinadis*) | *Lankodaya* (*Ghatis & Palas*) | *Lankodaya* (Clock Minutes) | *odaya* Type (*Shirshodaya / Prishtodaya*) |")
    lines.append("|---|---|---|---|---|---|---|")
    odaya_types = (
        "Prishtodaya (Rises by Hind Part)",
        "Prishtodaya (Rises by Hind Part)",
        "Ubhayodaya (Rises Both Ways)",
        "Prishtodaya (Rises by Hind Part)",
        "Shirshodaya (Rises by Head)",
        "Shirshodaya (Rises by Head)",
        "Shirshodaya (Rises by Head)",
        "Shirshodaya (Rises by Head)",
        "Prishtodaya (Rises by Hind Part)",
        "Prishtodaya (Rises by Hind Part)",
        "Shirshodaya (Rises by Head)",
        "Ubhayodaya (Rises Both Ways)",
    )
    western_names = ("Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo", "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces")
    for idx_s, r_name in enumerate(RASHI_NAMES):
        vin = LANKODAYA_VINADIS[idx_s]
        gh = vin // 60
        pl = vin % 60
        mins = vin * 0.4
        lines.append(
            f"| `{idx_s + 1:02d}` | **{r_name}** | {western_names[idx_s]} | `{vin} v` | "
            f"`{gh}g {pl:02d}p` | `{mins:.1f} min` | {odaya_types[idx_s]} |"
        )
    lines.append("")

    # =========================================================================
    # CHAPTER 8: Special Lagnas (Vishesha Lagnas), 11 Upagrahas, Yogi, & Sphutas
    # =========================================================================
    lines.append("## Chapter 8 — Complete Manual Compendium of All 8 *Vishesha Lagnas*, 11 *Upagrahas*, *Yogi/Avayogi*, & 9 *Prashna Sphutas*")
    lines.append("")
    lines.append("### Table 8A — Complete Manual Formulas for the 8 *Vishesha Lagnas* (Special Ascendants)")
    lines.append("")
    lines.append("| # | Special Lagna (*Vishesha Lagna*) | Rate of Motion | Exact Classical Manual Formula (*Brihat Parashara Hora Shastra* & *Uttara Kalamrita*) | Primary Predictive Domain |")
    lines.append("|---|---|---|---|---|")
    lines.append("| **1** | **Udaya Lagna (Birth Ascendant)** | `~1° per 4 min` (`12 signs / 24h`) | Eastern horizon intersection with the sidereal ecliptic at birth (Table 7A) | Physical body, vitality, self, overall life trajectory |")
    lines.append("| **2** | **Hora Lagna (HL)** | `0.5° per min` (`1 sign per Hora`) | `HL = λ_Sun(Sunrise) + (Elapsed Minutes since Sunrise / 2.0)` | Personal wealth, sustenance, liquid resources, financial inflow |")
    lines.append("| **3** | **Ghati Lagna (GL)** | `1.25° per min` (`1 sign per Ghati`) | `GL = λ_Sun(Sunrise) + (Elapsed Ghatis since Sunrise × 30°)` | Power, royal authority, political/executive rank, fame |")
    lines.append("| **4** | **Bhava Lagna (BL)** | `0.25° per min` (`1 sign per 5 Ghatis`) | `BL = λ_Sun(Sunrise) + (Elapsed Ghatis since Sunrise × 6°)` | Inner psychological disposition and bodily constitution |")
    lines.append("| **5** | **Sree Lagna (SL)** | Linked to Moon's Pada | `SL = λ_Udaya_Lagna + ((λ_Moon mod 13°20') / 13°20') × 360°` | Goddess Lakshmi's grace, prosperity, marriage fortune |")
    lines.append("| **6** | **Indu Lagna (IL)** | Planetary *Kala* Sum | Sum *Kalas* (`Sun 30, Moon 16, Mars 6, Mercury 8, Jupiter 10, Venus 12, Saturn 1`) of 9th Lord from Lagna + 9th Lord from Moon; take `Sum mod 12` (`0 -> 12`) and count that many signs from Natal Moon | Millionaire/billionaire *Dhana Yogas* and windfall wealth Dasha triggers |")
    lines.append("| **7** | **Pranapada Lagna (PL)** | `2° per Pala` (`1 sign per 15 Palas`) | `PL = λ_Sun + ((Elapsed Palas since Sunrise / 15) × 30°) + Offset` (`0°` Movable, `240°` Fixed, `120°` Dual Solar Sign) | Birth-time rectification (must fall in trine/10th to Moon or Lagna) |")
    lines.append("| **8** | **Varnada Lagna (VL)** | Sign-Parity Vector | Count Udaya Lagna & Hora Lagna from Mesha (if Odd) or Meena backwards (if Even); add if same parity, subtract if opposite parity | Social class, vocational calling, and public duty |")
    lines.append("")

    lines.append("### Table 8B — Complete Manual Formulas for the 5 Solar *Upagrahas* & 6 *Kalavela* Time-of-Day *Upagrahas* (*Gulika/Mandi*)")
    lines.append("")
    lines.append("| Category | Upagraha Name | Ruling Planet | Exact Manual Calculation Formula | Daytime Octant (`Sun..Sat`, out of 8) | Nighttime Octant (`Sun..Sat`, out of 8) |")
    lines.append("|---|---|---|---|---|---|")
    lines.append("| **Solar Upagraha 1** | **Dhuma** | Mars (Fiery Smoke) | `λ_Dhuma = (λ_Sun + 133° 20') mod 360°` | Instantaneous from `λ_Sun` | Instantaneous from `λ_Sun` |")
    lines.append("| **Solar Upagraha 2** | **Vyatipata** | Rahu (Calamity) | `λ_Vyatipata = (360° - λ_Dhuma) mod 360°` | Instantaneous from `λ_Sun` | Instantaneous from `λ_Sun` |")
    lines.append("| **Solar Upagraha 3** | **Parivesha** | Moon (Halo) | `λ_Parivesha = (λ_Vyatipata + 180°) mod 360°` | Instantaneous from `λ_Sun` | Instantaneous from `λ_Sun` |")
    lines.append("| **Solar Upagraha 4** | **Indrachapa (Kodanda)** | Venus (Rainbow Bow) | `λ_Indrachapa = (360° - λ_Parivesha) mod 360°` | Instantaneous from `λ_Sun` | Instantaneous from `λ_Sun` |")
    lines.append("| **Solar Upagraha 5** | **Upaketu (Sikhi)** | Ketu (Comet Crest) | `λ_Upaketu = (λ_Indrachapa + 16° 40') mod 360° = (λ_Sun - 30°)` | Instantaneous from `λ_Sun` | Instantaneous from `λ_Sun` |")
    lines.append("| **Kalavela 1** | **Gulika (Mandi)** | Saturn's Son | Ascendant rising at start of Saturn's 1/8th portion of *Dinamana* / *Ratrimana* | `Sun:7, Mon:6, Tue:5, Wed:4, Thu:3, Fri:2, Sat:1` | `Sun:3, Mon:2, Tue:1, Wed:7, Thu:6, Fri:5, Sat:4` |")
    lines.append("| **Kalavela 2** | **Kala** | Sun's Portion | Ascendant rising at start of Sun's 1/8th portion | `Sun:1, Mon:7, Tue:6, Wed:5, Thu:4, Fri:3, Sat:2` | `Sun:4, Mon:3, Tue:2, Wed:1, Thu:7, Fri:6, Sat:5` |")
    lines.append("| **Kalavela 3** | **Mrityu** | Mars's Portion | Ascendant rising at start of Mars's 1/8th portion | `Sun:3, Mon:2, Tue:1, Wed:7, Thu:6, Fri:5, Sat:4` | `Sun:6, Mon:5, Tue:4, Wed:3, Thu:2, Fri:1, Sat:7` |")
    lines.append("| **Kalavela 4** | **Ardhaprahara** | Mercury's Portion | Ascendant rising at start of Mercury's 1/8th portion | `Sun:4, Mon:3, Tue:2, Wed:1, Thu:7, Fri:6, Sat:5` | `Sun:7, Mon:6, Tue:5, Wed:4, Thu:3, Fri:2, Sat:1` |")
    lines.append("| **Kalavela 5** | **Yamaghantaka** | Jupiter's Portion | Ascendant rising at start of Jupiter's 1/8th portion | `Sun:5, Mon:4, Tue:3, Wed:2, Thu:1, Fri:7, Sat:6` | `Sun:1, Mon:7, Tue:6, Wed:5, Thu:4, Fri:3, Sat:2` |")
    lines.append("")

    lines.append("### Table 8C — Complete Manual Formulas for *Yogi / Sahayogi / Avayogi* & the 9 Kerala *Prashna Marga Sphutas*")
    lines.append("")
    lines.append("| Sensitive Point (*Sphuta*) | Exact Mathematical Formula (`Mod 360°`) | Classical Interpretation Rule (*Prashna Marga* & *BPHS*) |")
    lines.append("|---|---|---|")
    lines.append("| **Yogi Point & Yogi Planet** | `λ_Yogi = (λ_Sun + λ_Moon + 93° 20') mod 360°` | Nakshatra Lord of `λ_Yogi` is **Yogi Planet** (supreme prosperity significator); Sign Lord is **Sahayogi** |")
    lines.append("| **Avayogi Point & Planet** | `λ_Avayogi = (λ_Yogi + 186° 40') mod 360°` | Nakshatra Lord of `λ_Avayogi` is **Avayogi Planet** (obstruction/drain significator) |")
    lines.append("| **1. Trisphuta** | `(λ_Lagna + λ_Moon + λ_Gulika) mod 360°` | Core vitality, health, and immediate horary crisis indicator |")
    lines.append("| **2. Chatusphuta** | `(λ_Trisphuta + λ_Sun) mod 360°` | Soul-level endurance and royal/spiritual support |")
    lines.append("| **3. Panchasphuta** | `(λ_Chatusphuta + λ_Rahu) mod 360°` | Karmic destiny and hidden snakes/curses in Prashna |")
    lines.append("| **4. Prana Sphuta** | `(5 × λ_Lagna + λ_Gulika) mod 360°` | Vital breath (*Prana*) — conjunction with Mrityu Sphuta indicates acute danger |")
    lines.append("| **5. Deha Sphuta** | `(8 × λ_Moon + λ_Gulika) mod 360°` | Physical body resilience and recovery capacity |")
    lines.append("| **6. Mrityu Sphuta** | `(7 × λ_Gulika + λ_Sun) mod 360°` | Mortality / critical vulnerability point |")
    lines.append("| **7. Tithi Sphuta** | `(λ_Lagna + (λ_Moon - λ_Sun)) mod 360°` | Lunar-phase harmony in relationships and undertakings |")
    lines.append("| **8. Beeja Sphuta (Male)** | `(λ_Sun + λ_Venus + λ_Jupiter) mod 360°` | Male virility and progeny seed strength (must occupy odd signs/navamsas with benefic aspect) |")
    lines.append("| **9. Kshetra Sphuta (Female)** | `(λ_Moon + λ_Mars + λ_Jupiter) mod 360°` | Female fertility and womb strength (must occupy even signs/navamsas with benefic aspect) |")
    lines.append("")

    # =========================================================================
    # CHAPTER 9 (Section 4): Complete Shodashvarga D1-D60 Master Lookup Tables
    # =========================================================================
    lines.append("## Chapter 9 — Section 4 — Complete Manual Divisional Chart (*Shodashvarga D1–D60*) Master Lookup Tables, 36 *Drekkana Swarupas*, & *Vimsopaka Bala*")
    lines.append("")
    lines.append("### Table 9A — All 16 Parashari *Shodashvarga* Divisional Rules & *Vimsopaka Bala* Weights (`20-Point Scale`)")
    lines.append("")
    lines.append("| Varga | Sanskrit Name | Slice Size | Classical Manual Counting Rule | Primary Life Domain | *Shadvarga* Wt | *Saptavarga* Wt | *Dashavarga* Wt | *Shodashvarga* Wt |")
    lines.append("|---|---|---|---|---|---|---|---|---|")
    from ..jyotish.vargas import VIMSHOPAKA_WEIGHTS

    varga_specs = (
        ("D1", "Rashi", "30° 00'", "1st sign itself (`0°–30°`)", "Physical body, general fortune & identity"),
        ("D2", "Hora", "15° 00'", "Odd signs: `0°–15°` Simha (Sun), `15°–30°` Karka (Moon); Even signs: reversed", "Wealth, family sustenance & speech"),
        ("D3", "Drekkana", "10° 00'", "`0°–10°` 1st sign; `10°–20°` 5th sign; `20°–30°` 9th sign", "Siblings, courage, enterprise & co-born"),
        ("D4", "Chaturthamsa", "07° 30'", "4 slices of `7°30'`: 1st, 4th, 7th, and 10th (Kendra) signs from the Rashi", "Real estate, homes, fixed assets & happiness"),
        ("D7", "Saptamsa", "04° 17' 08.6\"", "7 slices: Odd signs count from same sign; Even signs count from 7th sign", "Children, grandchildren & creative legacy"),
        ("D9", "Navamsa", "03° 20'", "9 slices: Fire from Mesha, Earth from Makara, Air from Tula, Water from Karka", "Marriage, spouse, Dharma & inner fruit of planets"),
        ("D10", "Dasamsa", "03° 00'", "10 slices of `3°`: Odd signs count from same sign; Even signs count from 9th sign", "Career, profession, authority, fame & karma"),
        ("D12", "Dwadasamsa", "02° 30'", "12 slices of `2°30'`: Always count consecutively starting from the same sign", "Parents, ancestral lineage & hereditary karma"),
        ("D16", "Shodasamsa", "01° 52' 30\"", "16 slices: Movable from Mesha, Fixed from Simha, Dual from Dhanu", "Vehicles, luxury, conveyances & inner contentment"),
        ("D20", "Vimsamsa", "01° 30'", "20 slices: Movable from Mesha, Fixed from Dhanu, Dual from Simha", "Spiritual sadhana, Upasana, mantra & devotion"),
        ("D24", "Chaturvimsamsa", "01° 15'", "24 slices: Odd signs count from Simha (`04`); Even signs count from Karka (`03`)", "Higher learning, scholarship, Vidya & wisdom"),
        ("D27", "Saptavimsamsa", "01° 06' 40\"", "27 slices: Fire from Mesha, Earth from Karka, Air from Tula, Water from Makara", "Physical stamina, bodily strength & vitality"),
        ("D30", "Trimsamsa", "Unequal (5/5/8/7/5°)", "Odd: Mars 5°, Sat 5°, Jup 8°, Mer 7°, Ven 5°; Even: Ven 5°, Mer 7°, Jup 8°, Sat 5°, Mars 5°", "Arishta, misfortune, character & crisis resilience"),
        ("D40", "Khavedamsa", "00° 45'", "40 slices: Odd signs count from Mesha (`00`); Even signs count from Tula (`06`)", "Matrilineal karma & auspicious/inauspicious habits"),
        ("D45", "Akshavedamsa", "00° 40'", "45 slices: Movable from Mesha, Fixed from Simha, Dual from Dhanu", "Patrilineal karma, ethical conduct & royal character"),
        ("D60", "Shashtiamsa", "00° 30'", "60 slices of `30'`: Count `⌊deg × 2⌋` from the same sign; 60 named Sanskrit deities", "Past-life Sanchita Karma & twin birth differentiation"),
    )

    def _fmt_vw(scheme_key: str, v_code: str) -> str:
        val = VIMSHOPAKA_WEIGHTS[scheme_key].get(v_code)
        if val is None:
            return "—"
        return f"{int(val)}" if float(val).is_integer() else f"{val:g}"

    scheme_keys = tuple(VIMSHOPAKA_WEIGHTS.keys())
    for vc, vn, vs, vr, vd in varga_specs:
        w6 = _fmt_vw(scheme_keys[0], vc)
        w7 = _fmt_vw(scheme_keys[1], vc)
        w10 = _fmt_vw(scheme_keys[2], vc)
        w16 = _fmt_vw(scheme_keys[3], vc)
        lines.append(f"| **{vc}** | *{vn}* | `{vs}` | {vr} | {vd} | `{w6}` | `{w7}` | `{w10}` | **`{w16}`** |")
    lines.append("")

    lines.append("### Table 9B — Complete 108-Pada *Navamsa* (`D9`), *Pushkara Navamsa* (`*PN*`), & *Vargottama* (`*V*`) Master Lookup Grid")
    lines.append("")
    lines.append(
        "| Slice # | Degree Range in Sign | Arcminutes | Fire Signs (`Mesha, Simha, Dhanu`) | Earth Signs (`Vrishabha, Kanya, Makara`) | Air Signs (`Mithuna, Tula, Kumbha`) | Water Signs (`Karka, Vrishchika, Meena`) |"
    )
    lines.append("|---|---|---|---|---|---|---|")
    for p_idx in range(9):
        start_min = p_idx * 200
        end_min = (p_idx + 1) * 200
        sd, sm = start_min // 60, start_min % 60
        ed, em = end_min // 60, end_min % 60
        f_s = RASHI_NAMES[(0 + p_idx) % 12]
        e_s = RASHI_NAMES[(9 + p_idx) % 12]
        a_s = RASHI_NAMES[(6 + p_idx) % 12]
        w_s = RASHI_NAMES[(3 + p_idx) % 12]
        pn_f = " *PN*" if ((0 + p_idx) % 12) in (6, 8) else ""
        pn_e = " *PN*" if ((9 + p_idx) % 12) in (11, 1) else ""
        pn_a = " *PN*" if ((6 + p_idx) % 12) in (11, 1) else ""
        pn_w = " *PN*" if ((3 + p_idx) % 12) in (3, 5) else ""
        lines.append(
            f"| **Navamsa {p_idx + 1}** | `{sd:02d}° {sm:02d}' – {ed:02d}° {em:02d}'` | `{start_min}'–{end_min}'` | "
            f"**{f_s}**{pn_f} | **{e_s}**{pn_e} | **{a_s}**{pn_a} | **{w_s}**{pn_w} |"
        )
    lines.append("")

    lines.append("### Table 9C — Complete *Dasamsa* (`D10` — `3° 00'` per Slice) & *Dwadasamsa* (`D12` — `2° 30'` per Slice) Lookup Grid")
    lines.append("")
    lines.append("| Slice # | D10 Degree Span | D10 Odd Signs (`1,3,5,7,9,11`) | D10 Even Signs (`2,4,6,8,10,12`) | D12 Degree Span | D12 Any Sign (Offset from Sign) |")
    lines.append("|---|---|---|---|---|---|")
    for s_i in range(12):
        d12_s = s_i * 150
        d12_e = (s_i + 1) * 150
        d12_span = f"`{d12_s // 60:02d}° {d12_s % 60:02d}' – {d12_e // 60:02d}° {d12_e % 60:02d}'`"
        d12_rule = f"**+{s_i} signs** ({s_i + 1}th sign from Rashi)"
        if s_i < 10:
            d10_s = s_i * 3
            d10_e = (s_i + 1) * 3
            d10_span = f"`{d10_s:02d}° 00' – {d10_e:02d}° 00'`"
            d10_odd = f"**+{s_i} signs** ({s_i + 1}th from Rashi)"
            d10_even = f"**+{(8 + s_i) % 12} signs** ({(8 + s_i) % 12 + 1}th from Rashi)"
        else:
            d10_span, d10_odd, d10_even = "—", "—", "—"
        lines.append(f"| **{s_i + 1:02d}** | {d10_span} | {d10_odd} | {d10_even} | {d12_span} | {d12_rule} |")
    lines.append("")

    lines.append("### Table 9D — Complete 36 *Drekkana Swarupas* (`D3` Decanates — *Brihat Jataka* & *Phaladeepika* Classification)")
    lines.append("")
    lines.append("| # | Rashi | Decanate (`D3` Span) | Resulting D3 Sign & Lord | Classical *Drekkana Swarupa* Name | Nature (*Sarpa / Pakshi / Ayudha / Chatushpada / Pasa*) |")
    lines.append("|---|---|---|---|---|---|")
    for d3_entry in DREKKANA_SWARUPA_CATALOG:
        r_name = d3_entry.sign_name
        dec_idx = d3_entry.decanate_number
        span_str = f"`{(dec_idx - 1) * 10:02d}°–{dec_idx * 10:02d}°`"
        d3_sign_name = d3_entry.d3_sign_name
        d3_lord = d3_entry.ruling_planet.capitalize()
        cats = ", ".join(d3_entry.secondary_tags) if d3_entry.secondary_tags else d3_entry.swarupa
        lines.append(
            f"| **{(d3_entry.drekkana_index + 1):02d}** | **{r_name}** | Decanate {dec_idx} ({span_str}) | "
            f"**{d3_sign_name}** ({d3_lord}) | *{d3_entry.description}* | `{d3_entry.swarupa} ({cats})` |"
        )
    lines.append("")

    lines.append("### Table 9E — Complete 60 *Shashtiamsa* (`D60` — `00° 30'` Each) Deities & *Shubha / Krura* Classification")
    lines.append("")
    lines.append("| # | Odd Sign Span | Even Sign Span (Reversed) | Sanskrit *Shashtiamsa* Deity | Nature | # | Odd Sign Span | Even Sign Span (Reversed) | Sanskrit *Shashtiamsa* Deity | Nature |")
    lines.append("|---|---|---|---|---|---|---|---|---|---|")
    for idx_60 in range(30):
        # Print 2 columns of 30 rows = all 60 Shashtiamsas
        pair_60 = []
        for k_60 in (idx_60, idx_60 + 30):
            _, s_name, s_nature = SHASHTIAMSA_CATALOG[k_60]
            odd_s_m = k_60 * 30
            odd_e_m = (k_60 + 1) * 30
            ev_s_m = (59 - k_60) * 30
            ev_e_m = (60 - k_60) * 30
            odd_sp = f"`{odd_s_m // 60:02d}°{odd_s_m % 60:02d}'–{odd_e_m // 60:02d}°{odd_e_m % 60:02d}'`"
            ev_sp = f"`{ev_s_m // 60:02d}°{ev_s_m % 60:02d}'–{ev_e_m // 60:02d}°{ev_e_m % 60:02d}'`"
            nat_lbl = "Shubha (Benefic)" if (s_nature is True or str(s_nature).lower() == "benefic") else "Krura (Malefic)"
            pair_60.append(f"**{k_60 + 1:02d}** | {odd_sp} | {ev_sp} | **{s_name}** | {nat_lbl}")
        lines.append("| " + " | ".join(pair_60) + " |")
    lines.append("")

    # =========================================================================
    # CHAPTER 10: Complete Mrityu Bhaga (132 Fatal Degrees), 22nd Drekkana & 64th Navamsa
    # =========================================================================
    lines.append("## Chapter 10 — Complete 132-Cell *Mrityu Bhaga* (Fatal Degrees), 22nd *Khara Drekkana*, & 64th *Khara Navamsa* Master Vulnerability Tables")
    lines.append("")
    lines.append("### Table 10A — Complete 132-Cell *Mrityu Bhaga* (Fatal Degree) Master Table Across All 12 Signs (`Phaladeepika` & `Jataka Parijata`)")
    lines.append("")
    lines.append("| Rashi (Sign) | *Pushkara Bhaga* (Auspicious) | Lagna | Surya (Sun) | Chandra (Moon) | Mangala (Mars) | Budha (Mercury) | Guru (Jupiter) | Shukra (Venus) | Shani (Saturn) | Rahu | Ketu | Mandi (Gulika) |")
    lines.append("|---|---|---|---|---|---|---|---|---|---|---|---|---|")
    mb_keys = ("lagna", "sun", "moon", "mars", "mercury", "jupiter", "venus", "saturn", "rahu", "ketu")
    mandi_mb = (23, 24, 16, 12, 19, 28, 14, 13, 4, 20, 15, 9)
    for r_i, r_name in enumerate(RASHI_NAMES):
        pb_deg = PUSHKARA_BHAGA_DEGREES[r_i]
        mb_cells = [f"`{int(MRITYU_BHAGA_DEGREE_TABLE[mk][r_i]):02d}°`" for mk in mb_keys]
        mb_cells.append(f"`{mandi_mb[r_i]:02d}°`")
        lines.append(f"| **{r_name}** | **`{pb_deg:02.0f}°`** | " + " | ".join(mb_cells) + " |")
    lines.append("")

    lines.append("### Table 10B — Complete 22nd *Khara Drekkana* & 64th *Khara Navamsa* Lookup Table for Every Ascendant / Moon Position")
    lines.append("")
    lines.append("| Natal Sign (`D1`) | Decanate 1 (`0°–10°`) 22nd Drekkana Sign & Lord | Decanate 2 (`10°–20°`) 22nd Drekkana Sign & Lord | Decanate 3 (`20°–30°`) 22nd Drekkana Sign & Lord | 64th *Khara Navamsa* Rule (From Any Natal `D9` Sign) |")
    lines.append("|---|---|---|---|---|")
    for r_i, r_name in enumerate(RASHI_NAMES):
        # 22nd Drekkana is the Drekkana of the 8th house from the Natal Drekkana sign
        d_cells = []
        for dec_k in (0, 1, 2):
            natal_d3 = (r_i + dec_k * 4) % 12
            khara_d3 = (natal_d3 + 7) % 12
            d_cells.append(f"**{RASHI_NAMES[khara_d3]}** ({RASI_LORDS[khara_d3]})")
        khara_d9 = (r_i + 3) % 12  # 64th Navamsa = 7 signs + 1 navamsa = 4th sign from Natal D9 sign!
        lines.append(
            f"| **{r_name}** | {d_cells[0]} | {d_cells[1]} | {d_cells[2]} | "
            f"If Natal `D9` is **{r_name}**, 64th *Khara D9* is **{RASHI_NAMES[khara_d9]}** ({RASI_LORDS[khara_d9]}) |"
        )
    lines.append("")

    # =========================================================================
    # CHAPTER 11: Complete KP 249 Sub-Lord Master Table & 4-Fold Significators
    # =========================================================================
    lines.append("## Chapter 11 — Complete Krishnamurti Padhati (*KP*) 249 Sub-Lord Master Table (`#001` to `#249`) & 4-Fold Significator Rules")
    lines.append("")
    lines.append("### Table 11A — Complete 249-Division *KP* Sign-Star-Sub Master Reference Table (`000° 00' 00\"` to `360° 00' 00\"`)")
    lines.append("")
    lines.append("| Sub # | Zodiac Sign (`Rashi`) | Sign Lord | Nakshatra (`Star`) | Star Lord | Sub Lord | Start (`DMS` in Sign) | End (`DMS` in Sign) | Span (`MM' SS\"`) |")
    lines.append("|---|---|---|---|---|---|---|---|---|")
    for kp_entry in kp_sub_table_249():
        s_in_sign = kp_entry.start_deg - kp_entry.rasi_index * 30.0
        e_in_sign = kp_entry.end_deg - kp_entry.rasi_index * 30.0
        if e_in_sign <= 0.0001 and kp_entry.end_deg > kp_entry.start_deg:
            e_in_sign = 30.0
        sd_s = int(round(s_in_sign * 3600.0))
        ed_s = int(round(e_in_sign * 3600.0))
        sp_s = max(0, ed_s - sd_s)
        s_str = f"`{sd_s // 3600:02d}° {(sd_s % 3600) // 60:02d}' {sd_s % 60:02d}\"`"
        e_str = f"`{ed_s // 3600:02d}° {(ed_s % 3600) // 60:02d}' {ed_s % 60:02d}\"`"
        sp_str = f"`{sp_s // 60:02d}' {sp_s % 60:02d}\"`"
        lines.append(
            f"| **`#{kp_entry.number:03d}`** | **{kp_entry.rasi_name}** | {kp_entry.sign_lord.capitalize()} | "
            f"{kp_entry.nakshatra_name} | **{kp_entry.star_lord.capitalize()}** | **`{kp_entry.sub_lord.capitalize()}`** | {s_str} | {e_str} | {sp_str} |"
        )
    lines.append("")

    lines.append("### Table 11B — *KP* 4-Fold Hierarchy of Planetary Significators (Manual Worksheet Rule)")
    lines.append("")
    lines.append("| Significator Level | Priority | Classical *KP* Definition | Predictive Rule |")
    lines.append("|---|---|---|---|")
    lines.append("| **Level A (1st Order)** | Highest (`4x`) | Planet(s) occupying the **Nakshatra (Star)** of the Occupants of House `H` | Strongest driver of the event when its Dasha/Bhukti/Antara runs |")
    lines.append("| **Level B (2nd Order)** | High (`3x`) | Planet(s) directly **occupying** House `H` in the *Placidus Bhava Chalit* chart | Delivers the house result directly unless vacated by Star tenants |")
    lines.append("| **Level C (3rd Order)** | Moderate (`2x`) | Planet(s) occupying the **Nakshatra (Star)** of the Cusp Sign Lord of House `H` | Activates the house promise through stellar rulership over the cusp lord |")
    lines.append("| **Level D (4th Order)** | Baseline (`1x`) | The **Sign Lord** of the Cusp of House `H` itself | Background significator; strong when untenanted in both house and star |")
    lines.append("| **Cuspal Sub-Lord Gate** | **Decider** | The **Sub-Lord (`#001–#249`)** of Cusp `H` | **The Star Lord shows the nature of the involvement; the Sub-Lord decides YES or NO** |")
    lines.append("")

    # =========================================================================
    # CHAPTER 12 (Section 5): Multi-System Dasha Manual Compendium
    # =========================================================================
    lines.append("## Chapter 12 — Section 5 — Complete Manual Dasha Balance & Multi-System *Dasha* Compendium (*Vimshottari, Yogini, Ashtottari, & Kalachakra*)")
    lines.append("")
    lines.append(
        "**Classical Formula for Balance of Dasha at Birth (*Bhogyamsha*):**\n"
        "- Each Nakshatra spans `13° 20' = 800 arcminutes` (`4 Padas × 200' = 800'`).\n"
        "- If the Natal Moon is at `λ_Moon`, find its elapsed arcminutes inside the current Nakshatra (`G_elapsed`) "
        "and the remaining arcminutes to complete the Nakshatra (`B_rem = 800' - G_elapsed`).\n"
        "- `Balance of Mahadasha at Birth (Years) = Y_Mahadasha × (800' - G_elapsed) / 800'`"
    )
    lines.append("")
    lines.append("### Table 12A — 80-Row *Vimshottari Dasha* Balance Ready Reckoner (For Every `10'` of Remaining Lunar Arc `800'` down to `10'`)")
    lines.append("")
    lines.append("| Rem. Arc (`B'`) | Deg:Min Left | Pada | Ketu (`7y`) | Venus (`20y`) | Sun (`6y`) | Moon (`10y`) | Mars (`7y`) | Rahu (`18y`) | Jupiter (`16y`) | Saturn (`19y`) | Mercury (`17y`) |")
    lines.append("|---|---|---|---|---|---|---|---|---|---|---|---|")
    for rem_min in range(800, 0, -10):
        deg_l = rem_min // 60
        min_l = rem_min % 60
        elapsed_m = 800 - rem_min
        pada_n = min(4, (elapsed_m // 200) + 1)
        cells = []
        for lord in VIMSHOTTARI_LORDS:
            y_tot = VIMSHOTTARI_YEARS[lord]
            y_bal = y_tot * (rem_min / 800.0)
            yi = int(y_bal)
            mr = (y_bal - yi) * 12.0
            mi = int(mr)
            di = int(round((mr - mi) * 30.0))
            if di == 30:
                di = 0
                mi += 1
            if mi == 12:
                mi = 0
                yi += 1
            cells.append(f"`{yi:02d}y {mi:02d}m {di:02d}d`")
        lines.append(f"| **`{rem_min:03d}'`** | `{deg_l:02d}° {min_l:02d}'` | P{pada_n} | " + " | ".join(cells) + " |")
    lines.append("")

    lines.append("### Table 12B — Complete 81-Cell *Vimshottari Mahadasha × Antardasha (Bhukti)* Exact Duration Matrix (`Years-Months-Days`)")
    lines.append("")
    lines.append(
        "**Manual Antardasha (Bhukti) Formula:** Multiply the Mahadasha years by the Antardasha years and divide by 10 to obtain total months "
        "(`Total Months = (Y_MD × Y_AD) / 10`); divide integer months by 12 for years and remaining months, and multiply any fractional month by **30** "
        "(`Days = Fractional Month × 30`) to obtain days."
    )
    lines.append("")
    lines.append("| Mahadasha \\ Antardasha | Ketu (`7y`) | Venus (`20y`) | Sun (`6y`) | Moon (`10y`) | Mars (`7y`) | Rahu (`18y`) | Jupiter (`16y`) | Saturn (`19y`) | Mercury (`17y`) |")
    lines.append("|---|---|---|---|---|---|---|---|---|---|")
    for m_lord in VIMSHOTTARI_LORDS:
        m_yrs = VIMSHOTTARI_YEARS[m_lord]
        row_cells = []
        for a_lord in VIMSHOTTARI_LORDS:
            a_yrs = VIMSHOTTARI_YEARS[a_lord]
            total_months = (m_yrs * a_yrs) / 10.0
            y_part = int(total_months // 12)
            m_part = int(total_months % 12)
            d_part = int(round((total_months - int(total_months)) * 30.0))
            if d_part == 30:
                d_part = 0
                m_part += 1
            if m_part == 12:
                m_part = 0
                y_part += 1
            row_cells.append(f"`{y_part}y {m_part:02d}m {d_part:02d}d`")
        lines.append(f"| **{m_lord} ({int(m_yrs)}y)** | " + " | ".join(row_cells) + " |")
    lines.append("")

    lines.append("### Table 12C — Complete 36-Year *Yogini Dasha* (`8 Yoginis`) & 108-Year *Ashtottari Dasha* (`8 Grahas`) Reference Tables")
    lines.append("")
    lines.append("| Yogini # | Yogini Name | Planetary Ruler | Duration (`Years`) | Starting Nakshatra Rule `(N + 3) mod 8` | Ashtottari # | Ashtottari Lord | Duration (`Years`) | Assigned 28-Nakshatra Group |")
    lines.append("|---|---|---|---|---|---|---|---|---|")
    ashto_groups = (
        "Ardra, Punarvasu, Pushya, Ashlesha (4)",
        "Magha, P.Phalguni, U.Phalguni (3)",
        "Hasta, Chitra, Swati, Vishakha (4)",
        "Anuradha, Jyeshtha, Mula (3)",
        "P.Ashadha, U.Ashadha, Abhijit, Shravana (4)",
        "Dhanishta, Shatabhisha, P.Bhadrapada (3)",
        "U.Bhadrapada, Revati, Ashwini, Bharani (4)",
        "Krittika, Rohini, Mrigashirsha (3)",
    )
    for idx_d in range(8):
        y_name = YOGINI_NAMES[idx_d]
        y_lord = YOGINI_RULERS[y_name]
        y_yrs = int(YOGINI_YEARS[y_name])
        a_lord = ASHTOTTARI_LORDS[idx_d]
        a_yrs = int(ASHTOTTARI_YEARS[a_lord])
        lines.append(
            f"| **{idx_d + 1}** | **{y_name}** | {y_lord} | `{y_yrs} Years` | Remainder `{(idx_d + 1) % 8}` | "
            f"**{idx_d + 1}** | **{a_lord}** | `{a_yrs} Years` | {ashto_groups[idx_d]} |"
        )
    lines.append("")

    lines.append("### Table 12D — Complete 108-Pada *Kalachakra Dasha* (*Savya* & *Apasavya*) Master Sequence & *Dehamsha / Jeevamsha* Table")
    lines.append("")
    lines.append(
        "**Sign Durations in *Kalachakra Dasha*:** Mesha/Vrishchika (`7y`), Vrishabha/Tula (`16y`), Mithuna/Kanya (`9y`), "
        "Karka (`21y`), Simha (`5y`), Dhanu/Meena (`10y`), Makara/Kumbha (`4y`)."
    )
    lines.append("")
    lines.append("| Cycle Group | Nakshatra Triad | Pada | *Dehamsha* (Body Sign) | *Jeevamsha* (Soul Sign) | Total Cycle (`Paramayus`) | 9-Sign *Kalachakra* Progression Sequence |")
    lines.append("|---|---|---|---|---|---|---|")
    for g_idx in range(3):
        triad_lbl = ("Ashwini, Punarvasu, Hasta, Mula, P.Bhadra (I)", "Bharani, Pushya, Chitra, P.Ashadha, U.Bhadra (II)", "Krittika, Ashlesha, Swati, U.Ashadha, Revati (III)")[g_idx]
        for p_no in range(1, 5):
            seq_tuple = KALACHAKRA_SAVYA_SEQUENCES[(g_idx, p_no)]
            seq_names = [RASHI_NAMES[s] for s in seq_tuple]
            tot_y = sum(int(KALACHAKRA_SIGN_YEARS[s]) for s in seq_tuple)
            lines.append(
                f"| **Savya {g_idx + 1}** | {triad_lbl} | **Pada {p_no}** | **{seq_names[0]}** | **{seq_names[-1]}** | "
                f"`{tot_y} Years` | " + " → ".join(seq_names) + " |"
            )
    for g_idx in range(3):
        triad_lbl = ("Rohini, Magha, Vishakha, Shravana (I)", "Mrigashirsha, P.Phalguni, Anuradha, Dhanishta (II)", "Ardra, U.Phalguni, Jyeshtha, Shatabhisha (III)")[g_idx]
        for p_no in range(1, 5):
            seq_tuple = KALACHAKRA_APASAVYA_SEQUENCES[(g_idx, p_no)]
            seq_names = [RASHI_NAMES[s] for s in seq_tuple]
            tot_y = sum(int(KALACHAKRA_SIGN_YEARS[s]) for s in seq_tuple)
            lines.append(
                f"| **Apasavya {g_idx + 1}** | {triad_lbl} | **Pada {p_no}** | **{seq_names[-1]}** | **{seq_names[0]}** | "
                f"`{tot_y} Years` | " + " → ".join(seq_names) + " |"
            )
    lines.append("")

    # =========================================================================
    # CHAPTER 13: Complete Jaimini Upadesha Sutras Manual Compendium
    # =========================================================================
    lines.append("## Chapter 13 — Complete *Jaimini Upadesha Sutras* Manual Compendium (*Chara Karakas*, *Arudha Padas*, *Rashi Drishti*, *Argala*, & *Jaimini Ayurdaya*)")
    lines.append("")
    lines.append("### Table 13A — Complete 144-Cell `12 × 12` *Jaimini Arudha Pada* (*Swastha* 1st/7th Exception Included) Master Lookup Matrix")
    lines.append("")
    lines.append(
        "**How to Read This Table:** Find the **Sign of the House (`H`)** in the left column, and the **Sign Occupied by Its Lord (`L`)** "
        "across the top row. The cell gives the **exact Arudha Pada Sign** (automatically applying the Jaimini *Swastha* rule: when the projected Arudha lands in the 1st or 7th from the house, the Arudha jumps 10 signs from the raw position)."
    )
    lines.append("")
    lines.append("| House Sign \\ Lord Sign | " + " | ".join(f"**{r[:5]}**" for r in RASHI_NAMES) + " |")
    lines.append("|---|" + "|".join(["---"] * 12) + "|")
    for h_s in range(12):
        row_arudha = []
        for l_s in range(12):
            dist = (l_s - h_s) % 12
            raw_a = (l_s + dist) % 12
            if ((raw_a - h_s) % 12) in (0, 6):
                final_a = (raw_a + 9) % 12
                row_arudha.append(f"**{RASHI_NAMES[final_a][:5]}***")
            else:
                row_arudha.append(f"{RASHI_NAMES[raw_a][:5]}")
        lines.append(f"| **{h_s + 1:02d} {RASHI_NAMES[h_s]}** | " + " | ".join(row_arudha) + " |")
    lines.append("")

    lines.append("### Table 13B — Complete `12 × 12` *Jaimini Rashi Drishti* (Sign Aspect) Matrix & *Argala / Virodhargala* Rules")
    lines.append("")
    lines.append("| Sign (`Rashi`) | Modality | Signs Aspected by *Jaimini Rashi Drishti* (`Abhimukha` Rule) | Primary *Argala* Houses (`2nd, 4th, 11th`) | *Virodhargala* Obstruction Houses (`12th, 10th, 3rd`) | *Shoola Dasha* (`9y/sign`) | *Sthira Dasha* (`7/8/9y`) |")
    lines.append("|---|---|---|---|---|---|---|")
    for r_i, r_name in enumerate(RASHI_NAMES):
        mod_str = ("Chara (Movable)", "Sthira (Fixed)", "Dwiswabhava (Dual)")[r_i % 3]
        asp_names = ", ".join(f"**{RASHI_NAMES[a]}**" for a in RASHI_DRISHTI_TABLE[r_i])
        arg_names = f"`2nd:` {RASHI_NAMES[(r_i + 1) % 12]}, `4th:` {RASHI_NAMES[(r_i + 3) % 12]}, `11th:` {RASHI_NAMES[(r_i + 10) % 12]}"
        vir_names = f"`12th:` {RASHI_NAMES[(r_i + 11) % 12]}, `10th:` {RASHI_NAMES[(r_i + 9) % 12]}, `3rd:` {RASHI_NAMES[(r_i + 2) % 12]}"
        sthira_y = (7, 8, 9)[r_i % 3]
        lines.append(f"| **{r_name}** | {mod_str} | {asp_names} | {arg_names} | {vir_names} | `9 Years` | `{sthira_y} Years` |")
    lines.append("")

    lines.append("### Table 13C — *Jaimini Chara Karakas*, *Karakamsa* Deities (`Ishta / Palana / Dharma Devata`), & *Three-Pair Ayurdaya* Matrix")
    lines.append("")
    lines.append("| Graha | *Jaimini Devata* (`Ishta / Dharma`) | Modality Pair 1 (`Lagna + Moon`) | Modality Pair 2 (`Lagna + Hora Lagna`) | Modality Pair 3 (`Lagna + 8th`) | Resulting *Ayurdaya* Tier (`Years`) |")
    lines.append("|---|---|---|---|---|---|")
    ayur_rows = (
        ("Sun", JAIMINI_DEITY_MAP["Sun"], "Movable + Movable", "Fixed + Dual", "Movable + Movable", "**Purnayu** (`66–100 Years`)"),
        ("Moon", JAIMINI_DEITY_MAP["Moon"], "Movable + Fixed", "Movable + Dual", "Fixed + Fixed", "**Madhyayu** (`33–66 Years`)"),
        ("Mars", JAIMINI_DEITY_MAP["Mars"], "Fixed + Fixed", "Movable + Movable", "Dual + Dual", "**Alpayu** (`0–33 Years`)"),
        ("Mercury", JAIMINI_DEITY_MAP["Mercury"], "Dual + Dual", "Movable + Fixed", "Movable + Dual", "**Madhyayu** (`33–66 Years`)"),
        ("Jupiter", JAIMINI_DEITY_MAP["Jupiter"], "Movable + Dual", "Fixed + Fixed", "Movable + Fixed", "**Purnayu** (with Jupiter in Lagna/7th: *Kakshya Vriddhi* +1 tier)"),
        ("Venus", JAIMINI_DEITY_MAP["Venus"], "Fixed + Dual", "Dual + Dual", "Fixed + Dual", "**Purnayu** (`66–100 Years`)"),
        ("Saturn", JAIMINI_DEITY_MAP["Saturn"], "Malefic in 8th/Lagna", "Afflicted Rudra", "Saturn un-elevated", "**Kakshya Hrasa** (-1 tier reduction when unassisted)"),
        ("Rahu / Ketu", f"{JAIMINI_DEITY_MAP['Rahu']} / {JAIMINI_DEITY_MAP['Ketu']}", "8-Karaka Scheme (`Rahu` at `30° - d`)", "*Moksha Karaka* (`Ketu` in 12th from *Karakamsa*)", "—", "Ketu in 4th/8th/12th from *Karakamsa* grants final liberation"),
    )
    for g_n, dev_n, mp1, mp2, mp3, ay_res in ayur_rows:
        lines.append(f"| **{g_n}** | **{dev_n}** | {mp1} | {mp2} | {mp3} | {ay_res} |")
    lines.append("")

    # =========================================================================
    # CHAPTER 14: Complete Six-Fold Shadbala, 36-Row Drishti Table & Bhava Bala
    # =========================================================================
    lines.append("## Chapter 14 — Complete Six-Fold *Shadbala*, 36-Row Continuous Parashari *Sphuta Drishti* Table, *Ishta/Kashta Phala*, & *Bhava Bala*")
    lines.append("")
    lines.append("### Table 14A — Complete Six-Fold *Shadbala* Formulas, Deep Exaltation Points, *Naisargika Bala*, & Minimum Required *Rupas*")
    lines.append("")
    lines.append("| Graha | Deep Exaltation (`Uchcha` = `60v`) | Deep Debilitation (`Neecha` = `0v`) | Zero *Dig Bala* House | Max *Dig Bala* House (`60v`) | *Naisargika Bala* (`Virupas`) | *Kala Bala* Day/Night Ruler | Min Required *Shadbala* (`Virupas` / `Rupas`) |")
    lines.append("|---|---|---|---|---|---|---|---|")
    shadbala_ref = (
        ("Sun", "`10° Mesha (010°)`", "`10° Tula (190°)`", "4th Cusp (`IC`)", "10th Cusp (`MC`)", "`60.00v`", "Day (`Diwa`) +60v", "**`390v` (`6.50 Rupas`)**"),
        ("Moon", "`03° Vrishabha (033°)`", "`03° Vrishchika (213°)`", "10th Cusp (`MC`)", "4th Cusp (`IC`)", "`51.43v`", "Night (`Ratri`) +60v", "**`360v` (`6.00 Rupas`)**"),
        ("Mars", "`28° Makara (298°)`", "`28° Karka (118°)`", "4th Cusp (`IC`)", "10th Cusp (`MC`)", "`17.14v`", "Night (`Ratri`) +60v", "**`300v` (`5.00 Rupas`)**"),
        ("Mercury", "`15° Kanya (165°)`", "`15° Meena (345°)`", "7th Cusp (`Desc`)", "1st Cusp (`Lagna`)", "`25.71v`", "Always (`Sarvada`) +60v", "**`420v` (`7.00 Rupas`)**"),
        ("Jupiter", "`05° Karka (095°)`", "`05° Makara (275°)`", "7th Cusp (`Desc`)", "1st Cusp (`Lagna`)", "`34.29v`", "Day (`Diwa`) +60v", "**`390v` (`6.50 Rupas`)**"),
        ("Venus", "`27° Meena (357°)`", "`27° Kanya (177°)`", "10th Cusp (`MC`)", "4th Cusp (`IC`)", "`42.86v`", "Day (`Diwa`) +60v", "**`330v` (`5.50 Rupas`)**"),
        ("Saturn", "`20° Tula (200°)`", "`20° Mesha (020°)`", "1st Cusp (`Lagna`)", "7th Cusp (`Desc`)", "`08.57v`", "Night (`Ratri`) +60v", "**`300v` (`5.00 Rupas`)**"),
    )
    for gn, ux, nx, z_d, m_d, nb_v, kb_r, req_r in shadbala_ref:
        lines.append(f"| **{gn}** | {ux} | {nx} | {z_d} | {m_d} | {nb_v} | {kb_r} | {req_r} |")
    lines.append("")

    lines.append("### Table 14B — Complete 36-Row Continuous Parashari *Sphuta Drishti* (Aspectual Strength in *Virupas* `0v–60v`) Lookup Table")
    lines.append("")
    lines.append(
        "**Classical Piecewise Formula (*Brihat Parashara Hora Shastra*):** Let `Δ = (λ_Target - λ_Aspecting) mod 360°`. "
        "Base *Drishti* is `0v` for `0°..30°` and `300°..360°`; rises from `30°..60°` (`(Δ-30)/2`); "
        "rises from `60°..90°` (`(Δ-60)+15`); drops from `90°..120°` (`45-(Δ-90)/2`); drops from `120°..150°` (`30-(Δ-120)`); "
        "rises sharply from `150°..180°` (`2*(Δ-150)` peaking at `60v` at `180°`); and decreases linearly from `180°..300°` (`(300-Δ)/2`). "
        "**Special Vishesha Drishti:** Mars gets `60v` across `90°..120°` & `210°..240°`; Jupiter gets `60v` across `120°..150°` & `240°..270°`; Saturn gets `60v` across `60°..90°` & `270°..300°`."
    )
    lines.append("")
    lines.append("| Separation `Δ` | House Span | Standard (*Sun, Moon, Mer, Ven*) | Mars (*4th & 8th Vishesha*) | Jupiter (*5th & 9th Vishesha*) | Saturn (*3rd & 10th Vishesha*) |")
    lines.append("|---|---|---|---|---|---|")
    for deg_step in range(0, 360, 10):
        d = float(deg_step)
        if d < 30.0 or d >= 300.0:
            base_v = 0.0
        elif d < 60.0:
            base_v = (d - 30.0) / 2.0
        elif d < 90.0:
            base_v = 15.0 + (d - 60.0)
        elif d < 120.0:
            base_v = 45.0 - (d - 90.0) / 2.0
        elif d < 150.0:
            base_v = 30.0 - (d - 120.0)
        elif d < 180.0:
            base_v = 2.0 * (d - 150.0)
        else:
            base_v = (300.0 - d) / 2.0
        mars_v = 60.0 if (90.0 <= d < 120.0 or 210.0 <= d < 240.0) else min(60.0, base_v + 15.0 if base_v > 0 else 0.0)
        jup_v = 60.0 if (120.0 <= d < 150.0 or 240.0 <= d < 270.0) else min(60.0, base_v + 30.0 if base_v > 0 else 0.0)
        sat_v = 60.0 if (60.0 <= d < 90.0 or 270.0 <= d < 300.0) else min(60.0, base_v + 45.0 if base_v > 0 else 0.0)
        h_no = (deg_step // 30) + 1
        lines.append(
            f"| **`{deg_step:03d}°`** | House {h_no:02d} | `{base_v:05.2f}v` | **`{mars_v:05.2f}v`** | **`{jup_v:05.2f}v`** | **`{sat_v:05.2f}v`** |"
        )
    lines.append("")

    # =========================================================================
    # CHAPTER 15: Complete Ashtakavarga, Shodhana, Pindas, & 8-Lord Kakshya
    # =========================================================================
    lines.append("## Chapter 15 — Complete *Ashtakavarga* (337-Bindu BAV/SAV), *Shodhana* Reductions, *Pinda* Multipliers, & 8-Lord *Kakshya* (`3°45'`) Transit Table")
    lines.append("")
    lines.append("### Table 15A — Complete 337-Bindu *Bhinna Ashtakavarga* (`BAV`) Benefic House Contribution Matrix (*Brihat Parashara Hora Shastra*)")
    lines.append("")
    lines.append("| BAV Planet | Total Bindus | From Sun | From Moon | From Mars | From Mercury | From Jupiter | From Venus | From Saturn | From Lagna |")
    lines.append("|---|---|---|---|---|---|---|---|---|---|")
    bav_totals = {"Sun": 48, "Moon": 49, "Mars": 39, "Mercury": 54, "Jupiter": 56, "Venus": 52, "Saturn": 39}
    for p_bav in ("Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn"):
        contrib_map = BAV_BENEFIC_HOUSES[p_bav]
        cells_b = []
        for src_k in ("Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn", "Lagna"):
            houses_str = ",".join(str(h) for h in contrib_map[src_k])
            cells_b.append(f"`{houses_str}` ({len(contrib_map[src_k])})")
        lines.append(f"| **{p_bav}** | **`{bav_totals[p_bav]}`** | " + " | ".join(cells_b) + " |")
    lines.append("")

    lines.append("### Table 15B — *Rashi Gunakara*, *Graha Gunakara* (*Shodhya Pinda* Multipliers), & 8-Lord *Kakshya* (`3° 45'`) Sub-Sign Transit Grid")
    lines.append("")
    lines.append("| Kakshya # | Degree Span in Sign | Arcminutes | Ruling *Kakshya* Lord | Speed Order | *Rashi Gunakara* (Signs 1–12) | *Graha Gunakara* (Planets) |")
    lines.append("|---|---|---|---|---|---|---|")
    rasi_mult_strs = (
        "Mesha `7`, Vrishabha `10`",
        "Mithuna `8`, Karka `4`",
        "Simha `10`, Kanya `5`",
        "Tula `7`, Vrishchika `8`",
        "Dhanu `9`, Makara `5`",
        "Kumbha `11`, Meena `12`",
        "Trikona Reduction: Subtract minimum of `(1,5,9), (2,6,10), (3,7,11), (4,8,12)`",
        "Ekadhipatya Reduction: Reduce dual-lord signs (`Mesha/Vrishchika`, `Vrishabha/Tula`, etc.)",
    )
    graha_mult_strs = (
        "Sun `5`",
        "Moon `5`",
        "Mars `8`",
        "Mercury `5`",
        "Jupiter `10`",
        "Venus `7`",
        "Saturn `5`",
        "Shodhya Pinda = Rashi Pinda + Graha Pinda",
    )
    for k_i, k_lord in enumerate(KAKSHYA_LORDS):
        s_m = int(round(k_i * 225.0))
        e_m = int(round((k_i + 1) * 225.0))
        sp_lbl = f"`{s_m // 60:02d}° {s_m % 60:02d}' – {e_m // 60:02d}° {e_m % 60:02d}'`"
        lines.append(
            f"| **Kakshya {k_i + 1}** | {sp_lbl} | `{s_m}'–{e_m}'` | **{k_lord}** | Orbit #{k_i + 1} | "
            f"{rasi_mult_strs[k_i]} | {graha_mult_strs[k_i]} |"
        )
    lines.append("")

    # =========================================================================
    # CHAPTER 16: Complete Classical Longevity (Ayurdaya) Manual Compendium
    # =========================================================================
    lines.append("## Chapter 16 — Complete Classical Mathematical Longevity (*Ayurdaya* — *Pindayu, Nisargayu, & Amsayu*) Manual Calculation Compendium")
    lines.append("")
    lines.append("### Table 16A — Maximum *Pindayu* & *Nisargayu* Planetary Years & The Four Classical Reductions (*Harana*)")
    lines.append("")
    lines.append("| Graha | Deep Exaltation | *Pindayu* Max Years | *Nisargayu* Max Years | *Astangata Harana* (Combustion Reduction) | *Shatru Kshetra Harana* (Enemy Sign Reduction) | *Chakrapata Harana* (Visible Hemisphere `H12..H7` Reduction) |")
    lines.append("|---|---|---|---|---|---|---|")
    chakrapata_notes = (
        "`H12:` Lose `100%` (Malefic) / `50%` (Benefic)",
        "`H11:` Lose `50%` (Malefic) / `25%` (Benefic)",
        "`H10:` Lose `1/3` (Malefic) / `1/6` (Benefic)",
        "`H9:` Lose `1/4` (Malefic) / `1/8` (Benefic)",
        "`H8:` Lose `1/5` (Malefic) / `1/10` (Benefic)",
        "`H7:` Lose `1/6` (Malefic) / `1/12` (Benefic)",
        "**Amsayu Rule:** Total Elapsed Arcminutes `÷ 200' mod 12 =` Base Years (multiplied by `2×` or `3×` in Own/Exalted Rashi or D9)",
    )
    for idx_ay, p_ay in enumerate(("Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn")):
        p_max = PINDAYU_MAX_YEARS.get(p_ay, PINDAYU_MAX_YEARS.get(p_ay.lower(), 0.0))
        n_max = NISARGAYU_MAX_YEARS.get(p_ay, NISARGAYU_MAX_YEARS.get(p_ay.lower(), 0.0))
        ast_note = "**Exempt** (Saturn & Venus never lose years by combustion)" if p_ay in ("Saturn", "Venus") else ("N/A (Luminary)" if p_ay == "Sun" else "Lose **`1/2` (`50%`)** when combust")
        shatru_note = "**Exempt** when Retrograde (*Vakri*)" if p_ay not in ("Sun", "Moon") else "Lose **`1/3` (`33.3%`)** in Enemy Sign"
        if p_ay not in ("Sun", "Moon"):
            shatru_note = "Lose **`1/3` (`33.3%`)** in Enemy Sign (Exempt if Retrograde)"
        lines.append(
            f"| **{p_ay}** | `{shadbala_ref[idx_ay][1]}` | **`{p_max:.0f} Years`** | **`{n_max:.0f} Years`** | "
            f"{ast_note} | {shatru_note} | {chakrapata_notes[idx_ay]} |"
        )
    lines.append("")

    # =========================================================================
    # CHAPTER 17: Complete Tajika Varshphal Manual Compendium & 36 Sahams
    # =========================================================================
    lines.append("## Chapter 17 — Complete *Tajika Varshphal* (Annual Solar Return) Manual Compendium, 100-Year *Dhruvanka* Table, *Hadda* Bounds, & All 36 *Tajika Sahams*")
    lines.append("")
    lines.append("### Table 17A — 100-Year *Tajika Varsha Pravesha Dhruvanka* (Constant Sidereal Solar Return Time Advance Table `Ages 1 to 100`)")
    lines.append("")
    lines.append(
        "**How to Find Any Annual Solar Return (*Varsha Pravesha*) Epoch by Hand:** 1 Sidereal Solar Year = `365d 06h 09m 09.8s` "
        "(`1d 06h 09m 09.8s` mod 7 weekdays). Add the **Cumulative Weekday + Hours:Minutes:Seconds Advance (*Dhruvanka*)** "
        "for the native's completed age to the Natal Birth Weekday and Time (then refine by final solar arcminutes using daily solar motion):"
    )
    lines.append("")
    lines.append("| Completed Age | Weekday & Time Advance (`d hh:mm:ss`) | Completed Age | Weekday & Time Advance (`d hh:mm:ss`) | Completed Age | Weekday & Time Advance (`d hh:mm:ss`) | Completed Age | Weekday & Time Advance (`d hh:mm:ss`) |")
    lines.append("|---|---|---|---|---|---|---|---|")
    sid_excess_sec = (365.256363004 - 364.0) * 86400.0  # 1d 06h 09m 09.76s in seconds
    for age_row in range(1, 26):
        age_cells = []
        for col_offset in (0, 25, 50, 75):
            age_val = age_row + col_offset
            tot_sec = (age_val * sid_excess_sec) % (7.0 * 86400.0)
            w_days = int(tot_sec // 86400.0)
            rem_s = int(round(tot_sec % 86400.0))
            hh = rem_s // 3600
            mm = (rem_s % 3600) // 60
            ss = rem_s % 60
            age_cells.append(f"**Age {age_val:03d}** | `+{w_days}d {hh:02d}:{mm:02d}:{ss:02d}`")
        lines.append("| " + " | ".join(age_cells) + " |")
    lines.append("")

    lines.append("### Table 17B — Complete 12-Sign *Tajika Hadda* (Egyptian Terms) & *Tri-Rashi Pati* Table (*Tajika Neelakanthi*)")
    lines.append("")
    lines.append("| Rashi (Sign) | Hadda 1 | Hadda 2 | Hadda 3 | Hadda 4 | Hadda 5 | *Tri-Rashi Pati* (Day / Night) |")
    lines.append("|---|---|---|---|---|---|---|")
    tri_rashi_names = (
        "Sun / Jupiter", "Venus / Moon", "Saturn / Mercury", "Venus / Mars",
        "Jupiter / Sun", "Moon / Venus", "Mercury / Saturn", "Mars / Venus",
        "Saturn / Saturn", "Mars / Mars", "Jupiter / Jupiter", "Moon / Moon",
    )
    for r_i, r_name in enumerate(RASHI_NAMES):
        h_row = TAJIKA_HADDA_TABLE[r_i]
        h_strs = []
        prev_d = 0
        for end_d, h_lord in h_row:
            h_strs.append(f"`{prev_d:02d}°–{int(end_d):02d}°` **{h_lord.capitalize()}**")
            prev_d = int(end_d)
        lines.append(f"| **{r_name}** | " + " | ".join(h_strs) + f" | **{tri_rashi_names[r_i]}** |")
    lines.append("")

    lines.append("### Table 17C — Complete Catalog of All 36 Classical *Tajika Sahams* (Arabic Lots — Day & Night Manual Formulas)")
    lines.append("")
    lines.append(
        "**Universal Saham Rule (*Tajika Neelakanthi*):** Compute `λ_Saham = (A - B + C) mod 360°`. "
        "Whenever the Ascendant (`C`) is **not** geometrically situated on the zodiacal arc moving forward from `B` to `A`, "
        "**add `+30°` (`1 Sign`)** to the result."
    )
    lines.append("")
    lines.append("| # | Classical *Saham* Name | Life Domain / Signification | Day Birth Formula (`A - B + C`) | Night Birth Formula (`A - B + C`) |")
    lines.append("|---|---|---|---|---|")
    saham_catalog_36 = (
        ("01", "Punya Saham (Fortune)", "Overall fortune, dharma, prosperity & grace", "Moon - Sun + Lagna", "Sun - Moon + Lagna"),
        ("02", "Vidya Saham (Learning)", "Education, scholarship, wisdom & intellect", "Sun - Moon + Lagna", "Moon - Sun + Lagna"),
        ("03", "Yashas Saham (Fame)", "Fame, public honour, reputation & prestige", "Jupiter - Punya + Lagna", "Punya - Jupiter + Lagna"),
        ("04", "Mitra Saham (Friends)", "Alliances, patrons, benefactors & friendships", "Jupiter - Punya + Venus", "Punya - Jupiter + Venus"),
        ("05", "Mahatmya Saham (Greatness)", "Eminence, nobility, high rank & grandeur", "Punya - Mars + Lagna", "Mars - Punya + Lagna"),
        ("06", "Asha Saham (Desires)", "Fulfilment of hopes, wishes & long-term ambitions", "Saturn - Venus + Lagna", "Venus - Saturn + Lagna"),
        ("07", "Samarthya Saham (Enterprise)", "Capability, courage, stamina & executive power", "Mars - Lagna_Lord + Lagna", "Lagna_Lord - Mars + Lagna"),
        ("08", "Bhratri Saham (Brothers)", "Siblings, co-born, valour & teamwork", "Jupiter - Saturn + Lagna", "Jupiter - Saturn + Lagna (Same)"),
        ("09", "Gaurava Saham (Respect)", "Social standing, dignity & respect from elders", "Jupiter - Moon + Sun", "Moon - Jupiter + Sun"),
        ("10", "Pitri Saham (Father)", "Father's health, fortune, authority & blessings", "Saturn - Sun + Lagna", "Sun - Saturn + Lagna"),
        ("11", "Matri Saham (Mother)", "Mother's health, domestic peace & nourishment", "Moon - Venus + Lagna", "Venus - Moon + Lagna"),
        ("12", "Putra Saham (Children)", "Progeny, childbirth, creativity & disciples", "Jupiter - Moon + Lagna", "Moon - Jupiter + Lagna"),
        ("13", "Jeeva Saham (Vitality)", "Life force, longevity, recovery & bodily vigour", "Saturn - Jupiter + Lagna", "Jupiter - Saturn + Lagna"),
        ("14", "Karma Saham (Action/Deeds)", "Profession, career execution & righteous action", "Mars - Mercury + Lagna", "Mercury - Mars + Lagna"),
        ("15", "Roga Saham (Disease)", "Illness, vulnerability, diagnosis & convalescence", "Lagna - Moon + Lagna", "Lagna - Moon + Lagna (Same)"),
        ("16", "Kali Saham (Strife/Great Effort)", "Sudden upheaval, crisis or heroic breakthrough", "Jupiter - Mars + Lagna", "Mars - Jupiter + Lagna"),
        ("17", "Sastra Saham (Scriptures)", "Mastery of sacred texts, sciences & philosophy", "Jupiter - Saturn + Mercury", "Saturn - Jupiter + Mercury"),
        ("18", "Bandhu Saham (Relatives)", "Kinsmen, extended family & community support", "Mercury - Moon + Lagna", "Moon - Mercury + Lagna"),
        ("19", "Mrityu Saham (Death/Danger)", "Mortal danger, severe crisis & transformation", "8th Cusp - Moon + Lagna", "8th Cusp - Moon + Lagna (Same)"),
        ("20", "Paradesa Saham (Foreign Travel)", "Foreign residence, long journeys & pilgrimage", "9th Cusp - 9th Lord + Lagna", "9th Cusp - 9th Lord + Lagna (Same)"),
        ("21", "Artha / Dhana Saham (Wealth)", "Liquid wealth, treasury, income & financial gain", "2nd Cusp - 2nd Lord + Lagna", "2nd Cusp - 2nd Lord + Lagna (Same)"),
        ("22", "Paradara Saham (Illicit Liaison)", "Romantic entanglement & boundary testing", "Venus - Sun + Lagna", "Venus - Sun + Lagna (Same)"),
        ("23", "Vanik Saham (Commerce/Trade)", "Business, merchandising, trading & negotiation", "Moon - Mercury + Lagna", "Mercury - Moon + Lagna"),
        ("24", "Karyasiddhi Saham (Success)", "Completion of undertakings & victory in projects", "Saturn - Sun + Sun_Sign_Lord", "Saturn - Moon + Moon_Sign_Lord"),
        ("25", "Vivaha Saham (Marriage)", "Marriage, partnership, wedding & spousal bond", "Venus - Saturn + Lagna", "Venus - Saturn + Lagna (Same)"),
        ("26", "Santapa Saham (Grief/Sorrow)", "Mental anguish, bereavement & emotional trials", "Saturn - Moon + 6th Cusp", "Saturn - Moon + 6th Cusp (Same)"),
        ("27", "Shraddha Saham (Faith/Devotion)", "Religious devotion, trust, integrity & piety", "Venus - Mars + Lagna", "Mars - Venus + Lagna"),
        ("28", "Preeti Saham (Love/Affection)", "Deep affection, harmony & cordiality", "Vidya - Punya + Lagna", "Punya - Vidya + Lagna"),
        ("29", "Bala Saham (Strength)", "Physical and moral authority & command", "Punya - Vidya + Lagna", "Vidya - Punya + Lagna"),
        ("30", "Manmatha Saham (Passion)", "Romantic passion, artistic charm & attraction", "Moon - Lagna_Lord + Lagna", "Lagna_Lord - Moon + Lagna"),
        ("31", "Vyapara Saham (Business Venture)", "Commercial expansion, contracts & deals", "Mars - Saturn + Lagna", "Mars - Saturn + Lagna (Same)"),
        ("32", "Paniyapatana Saham (Water)", "Maritime travel, liquids, rainfall & water hazards", "Saturn - Moon + Lagna", "Moon - Saturn + Lagna"),
        ("33", "Shatru Saham (Enemies)", "Litigation, rivals, competitors & opposition", "Mars - Saturn + Lagna", "Saturn - Mars + Lagna"),
        ("34", "Bandhana Saham (Confinement)", "Restraint, hospitalization, debt or captivity", "Punya - Saturn + Lagna", "Saturn - Punya + Lagna"),
        ("35", "Apamrityu Saham (Accidents)", "Sudden accidents, surgical risk & acute hazards", "8th Cusp - Mars + Lagna", "Mars - 8th Cusp + Lagna"),
        ("36", "Labha Saham (Gains/Profits)", "Net profits, windfalls, dividends & awards", "11th Cusp - 11th Lord + Lagna", "11th Cusp - 11th Lord + Lagna (Same)"),
    )
    for s_no, s_nm, s_dom, s_day, s_night in saham_catalog_36:
        lines.append(f"| **`#{s_no}`** | **{s_nm}** | {s_dom} | `{s_day}` | `{s_night}` |")
    lines.append("")

    # =========================================================================
    # CHAPTER 18: Ashtakoota, Yoni Matrix, Sarvatobhadra Chakra & Muhurta
    # =========================================================================
    lines.append("## Chapter 18 — Complete *Ashtakoota* (36-Guna) Compatibility, `14 × 14` *Yoni* Matrix, 81-Cell *Sarvatobhadra Chakra*, & *Muhurta* Compendium")
    lines.append("")
    lines.append("### Table 18A — Complete 27-Nakshatra *Ashtakoota* & *Dashakoota* Classification Directory (`Gana, Nadi, Yoni, Rajju, & Tara`)")
    lines.append("")
    lines.append("| # | Nakshatra | Span (`Rashi` & Degrees) | Ruler | *Gana* (`6 pts`) | *Nadi* (`8 pts`) | *Yoni* Animal (`4 pts`) | *Rajju* Group (`Dashakoota`) |")
    lines.append("|---|---|---|---|---|---|---|---|")
    rajju_cycle = ("Pada (Foot)", "Kati (Waist)", "Nabhi (Navel)", "Kantha (Neck)", "Shiro (Head)", "Kantha (Neck)", "Nabhi (Navel)", "Kati (Waist)", "Pada (Foot)")
    for n_i, n_name in enumerate(NAKSHATRA_NAMES):
        s_deg = n_i * (360.0 / 27.0)
        e_deg = (n_i + 1) * (360.0 / 27.0)
        gana_s = str(NAKSHATRA_GANA[n_i])
        nadi_s = str(NAKSHATRA_NADI[n_i])
        yoni_s = YONI_NAMES[NAKSHATRA_YONI_INDEX[n_i]]
        rajju_s = rajju_cycle[n_i % 9]
        lines.append(
            f"| **{n_i + 1:02d}** | **{n_name}** | `{format_classical_rashi_dms(s_deg)}` – `{format_classical_rashi_dms(e_deg)}` | "
            f"{VIMSHOTTARI_LORDS[n_i % 9]} | {gana_s} | **{nadi_s}** | {yoni_s} | {rajju_s} |"
        )
    lines.append("")

    lines.append("### Table 18B — Complete `14 × 14` *Yoni Koota* (`0 to 4 Points`) Classical Compatibility Matrix")
    lines.append("")
    lines.append("| Yoni \\ Yoni | " + " | ".join(f"**{y[:5]}**" for y in YONI_NAMES) + " |")
    lines.append("|---|" + "|".join(["---"] * 14) + "|")
    for y_r in range(14):
        y_cells = [f"`{YONI_SCORE_MATRIX[y_r][y_c]}`" for y_c in range(14)]
        lines.append(f"| **{y_r + 1:02d} {YONI_NAMES[y_r]}** | " + " | ".join(y_cells) + " |")
    lines.append("")

    lines.append("### Table 18C — Complete `9 × 9` (81-Cell) *Sarvatobhadra Chakra* Master Transit & *Vedha* Grid")
    lines.append("")
    lines.append("| Row \\ Col | Col 0 (West) | Col 1 | Col 2 | Col 3 | Col 4 (Center) | Col 5 | Col 6 | Col 7 | Col 8 (East) |")
    lines.append("|---|---|---|---|---|---|---|---|---|---|")
    sbc_grid = build_sarvatobhadra_grid()
    for r_idx, sbc_row in enumerate(sbc_grid):
        c_strs = [f"**{c.label}** *({c.cell_type[:3]})*" for c in sbc_row]
        lines.append(f"| **Row {r_idx}** | " + " | ".join(c_strs) + " |")
    lines.append("")

    lines.append("### Table 18D — *Muhurta* Electional Compendium: *Amrita Siddhi*, *Sarvartha Siddhi*, & *Dagdha Rashi* (Burnt Signs by Tithi)")
    lines.append("")
    lines.append("| Weekday (*Vara*) | *Amrita Siddhi* Nakshatra (Avoid Tithi) | *Sarvartha Siddhi* Nakshatras | Paksha Tithis | *Dagdha Rashi* (Burnt Signs to Avoid in Lagna) |")
    lines.append("|---|---|---|---|---|")
    vara_full = ("Sunday (Ravivara)", "Monday (Somavara)", "Tuesday (Mangalavara)", "Wednesday (Budhavara)", "Thursday (Guruvara)", "Friday (Shukravara)", "Saturday (Shanivara)")
    excl_tithis = ("Panchami (5)", "Shashthi (6)", "Saptami (7)", "Ashtami (8)", "Navami (9)", "Dashami (10)", "Ekadashi (11)")
    for w_i in range(7):
        am_nak = NAKSHATRA_NAMES[AMRITA_SIDDHI_NAKSHATRA[w_i]]
        ss_naks = ", ".join(NAKSHATRA_NAMES[n] for n in sorted(SARVARTHA_SIDDHI_NAKSHATRAS[w_i]))
        t_pair_1 = w_i * 2 + 1
        t_pair_2 = w_i * 2 + 2
        d_s1 = ", ".join(RASHI_NAMES[r] for r in DAGDHA_RASI_BY_PAKSHA_TITHI.get(t_pair_1, ()))
        d_s2 = ", ".join(RASHI_NAMES[r] for r in DAGDHA_RASI_BY_PAKSHA_TITHI.get(t_pair_2, ())) if t_pair_2 <= 15 else "Amavasya: None"
        t15_extra = f"; Tithi 15: {', '.join(RASHI_NAMES[r] for r in DAGDHA_RASI_BY_PAKSHA_TITHI.get(15, ()))}" if w_i == 6 else ""
        lines.append(
            f"| **{vara_full[w_i]}** | **{am_nak}** *(excl. {excl_tithis[w_i]})* | {ss_naks} | "
            f"Tithi {t_pair_1} & {t_pair_2} | `T{t_pair_1}:` **{d_s1}**; `T{t_pair_2}:` **{d_s2}**{t15_extra} |"
        )
    lines.append("")

    # =========================================================================
    # CHAPTER 19: Classical Parashari Yogas, 30-Star Yogatara & Surya Siddhanta
    # =========================================================================
    lines.append("## Chapter 19 — Complete Classical Parashari Yoga Identification Directory, 30-Star *Yogatara* Catalog, & *Surya Siddhanta* Reference")
    lines.append("")
    lines.append("### Table 19A — Complete 30-Star *Yogatara* (Junction Star) Astrometric Reference Catalog (*Surya Siddhanta* Chapter 8)")
    lines.append("")
    lines.append("| # | Nakshatra / Star | Sanskrit *Yogatara* Name | Modern IAU Star | J2000 RA (`deg`) | J2000 Dec (`deg`) | Visual Mag (`V`) | *Kalansha* Heliacal Arc |")
    lines.append("|---|---|---|---|---|---|---|---|")
    for st_i, st in enumerate(YOGATARA_30_CATALOG, start=1):
        nak_lbl = f"Nakshatra #{st.nakshatra_number}" if st.nakshatra_number else "Seasonal Star"
        lines.append(
            f"| **{st_i:02d}** | **{st.vedic_name}** *({nak_lbl})* | `{st.key}` (`HIP {st.hip_id}`) | `{st.western_designation}` | "
            f"`{st.ra_icrs_deg_j2000:07.3f}°` | `{st.dec_icrs_deg_j2000:+07.3f}°` | `{st.visual_magnitude:+05.2f}` | `{st.kalansha_visibility_arc_deg:.1f}°` |"
        )
    lines.append("")

    lines.append("### Table 19B — Classical *Surya Siddhanta* *Mahayuga Bhagana*, *Mandocca* (Apogees), & Epicycle (*Paridhi*) Constants")
    lines.append("")
    lines.append("| Graha | *Mahayuga Bhagana* (`4,320,000` Solar Years) | *Mandocca* at Kali Epoch (`deg`) | *Manda Paridhi* (`Even / Odd` Quadrants) | *Sighra Paridhi* (`Even / Odd` Quadrants) |")
    lines.append("|---|---|---|---|---|")
    for p_ss in ("Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn"):
        p_ss_low = p_ss.lower()
        bhag = MAHAYUGA_BHAGANA.get(p_ss_low, MAHAYUGA_BHAGANA.get(f"{p_ss_low}_sighrocca", 0))
        mand = MANDOCCA_KALI_EPOCH_DEG.get(p_ss_low, 0.0)
        mp_e, mp_o = MANDA_PARIDHI_EVEN_ODD_DEG.get(p_ss_low, (0.0, 0.0))
        sp_e, sp_o = SIGHRA_PARIDHI_EVEN_ODD_DEG.get(p_ss_low, (0.0, 0.0))
        sp_str = f"`{sp_e:.1f}° / {sp_o:.1f}°`" if sp_e > 0 else "— (No Sighra Samskara)"
        lines.append(
            f"| **{p_ss}** | `{bhag:,}` revolutions | `{mand:.4f}°` | `{mp_e:.1f}° / {mp_o:.1f}°` | {sp_str} |"
        )
    lines.append("")

    # =========================================================================
    # CHAPTER 20 (Section 7): Pt. Maheshji's Complete 15-Step Worked Manual Kundali
    # =========================================================================
    lines.append("## Chapter 20 — Section 7 — Pt. Maheshji's Jyotish Academy Step-by-Step Worked Manual Kundali Worksheet (Complete 15-Step Master Case Study)")
    lines.append("")
    we = comp.worked_example
    vis_rep = we["vishesha_report"]
    upa_rep = we["upagrahas_report"]
    sph_rep = we["sphutas_report"]
    kun_rep = we["kundali_bundle"]
    sah_rep = we["sahams_report"]
    kc_rep = we["kalachakra_report"]

    lines.append(f"- **Case Study Date & Time:** `{we['civil_date']}` at `{we['birth_time_local']}`")
    lines.append(f"- **Observer Location:** `{we['observer_location']}` (Ujjain Prime Meridian Reference)")
    lines.append(f"- **Elapsed Time After `05:30 IST` Tabular Epoch:** `{we['elapsed_after_0530_ist']}` (Interpolation Fraction `f = {we['trairashika_fraction']:.6f}`)")
    lines.append(f"- **Manual Ascendant (*Udaya Lagna*):** `{we['ascendant_dms']}` | **10th Cusp (*Madhya Lagna*):** `{we['mc_10th_cusp_dms']}`")
    lines.append(f"- **Natal Moon Nakshatra & Pada:** `{we['moon_nakshatra']}` (`{we['remaining_arcminutes_bhogyamsha']:.2f}'` *Bhogyamsha* remaining)")
    lines.append(f"- **Natal *Vimshottari Dasha* Balance at Birth:** **`{we['vimshottari_dasha_balance_at_birth']}`**")
    lines.append("")

    lines.append("### Step 1 & Step 2 — Complete 1st-Order (*Trairashika*) & 2nd-Order (*Bessel*) Manual *Spashta Graha* Worksheet")
    lines.append("")
    lines.append("| Body | `05:30 IST` Day `D` | `05:30 IST` Day `D+1` | Daily Motion `v₁` | 1st-Order *Trairashika* | 2nd-Order *Bessel* Exact | `D9` Navamsa | `D10` Dasamsa | `D60` Shashtiamsa | *KP* Star / Sub / Sub-Sub |")
    lines.append("|---|---|---|---|---|---|---|---|---|---|")
    for b_key, b_label in (
        ("sun", "Surya (Sun)"),
        ("moon", "Chandra (Moon)"),
        ("mars", "Mangala (Mars)"),
        ("mercury", "Budha (Mercury)"),
        ("jupiter", "Guru (Jupiter)"),
        ("venus", "Shukra (Venus)"),
        ("saturn", "Shani (Saturn)"),
        ("rahu", "Rahu (Node)"),
        ("ketu", "Ketu (S. Node)"),
    ):
        wp = we["planets"][b_key]
        lines.append(
            f"| **{b_label}** | `{wp['tabulated_0530_dms']}` | `{wp['motion_increment_dms']}` | `{wp['daily_motion_dms']}` | "
            f"`{wp['manual_trairashika_dms']}` | **`{wp['manual_bessel_2nd_order_dms']}`** | **{wp['d9_navamsa_sign']}** | "
            f"**{wp['d10_dasamsa_sign']}** | {wp['d60_shashtiamsa_sign']} | `{wp['kp_lords']}` |"
        )
    lines.append("")

    lines.append("### Step 3 & Step 4 — All 12 *Sripathi Bhava* Cusps, 8 *Vishesha Lagnas*, *Yogi/Avayogi*, 11 *Upagrahas*, & 9 *Prashna Sphutas*")
    lines.append("")
    lines.append("| Special Point Category | Point Name | Computed Sidereal Longitude (`DMS`) | Sign (`Rashi`) | `D9` Navamsa / Nakshatra Details |")
    lines.append("|---|---|---|---|---|")
    for vl_pt in (
        vis_rep.udaya_lagna,
        vis_rep.hora_lagna,
        vis_rep.ghati_lagna,
        vis_rep.bhava_lagna,
        vis_rep.sree_lagna,
        vis_rep.indu_lagna,
        vis_rep.pranapada_lagna,
        vis_rep.varnada_lagna,
    ):
        lines.append(
            f"| **8 Vishesha Lagnas** | **{vl_pt.title}** | **`{vl_pt.classical_dms}`** | {vl_pt.rashi_name} ({vl_pt.rashi_lord}) | "
            f"`D9:` **{vl_pt.d9_navamsa_sign}**; *{vl_pt.nakshatra_name}* P{vl_pt.pada} ({vl_pt.formula_summary}) |"
        )
    lines.append(
        f"| **Yogi & Avayogi** | **Yogi Point & Yogi Planet** | **`{vis_rep.yogi_point_dms}`** | Yogi: **{vis_rep.yogi_planet}** | "
        f"Nakshatra: *{vis_rep.yogi_nakshatra_name}*; Sahayogi: **{vis_rep.sahayogi_planet}** |"
    )
    lines.append(
        f"| **Yogi & Avayogi** | **Avayogi Point & Planet** | **`{vis_rep.avayogi_point_dms}`** | Avayogi: **{vis_rep.avayogi_planet}** | "
        f"Nakshatra: *{vis_rep.avayogi_nakshatra_name}* |"
    )
    for upa_k, upa_pt in (
        ("Dhuma", upa_rep.dhuma),
        ("Vyatipata", upa_rep.vyatipata),
        ("Parivesha", upa_rep.parivesha),
        ("Indrachapa", upa_rep.indrachapa),
        ("Upaketu", upa_rep.upaketu),
        ("Gulika (Mandi)", upa_rep.gulika),
        ("Kala", upa_rep.kala),
        ("Mrityu", upa_rep.mrityu),
        ("Ardhaprahara", upa_rep.ardhaprahara),
        ("Yamaghantaka", upa_rep.yamaghantaka),
        ("Ochcha", upa_rep.ochcha),
    ):
        lines.append(
            f"| **11 Upagrahas** | **{upa_k}** | `{format_classical_rashi_dms(upa_pt.longitude_deg)}` | "
            f"{upa_pt.sign_name} | *{upa_pt.nakshatra.name}* Pada {upa_pt.nakshatra.pada} |"
        )
    for sph_pt in (
        sph_rep.trisphuta,
        sph_rep.chatusphuta,
        sph_rep.panchasphuta,
        sph_rep.prana_sphuta,
        sph_rep.deha_sphuta,
        sph_rep.mrityu_sphuta,
        sph_rep.tithi_sphuta,
        sph_rep.beeja_sphuta,
        sph_rep.kshetra_sphuta,
    ):
        lines.append(
            f"| **9 Prashna Sphutas** | **{sph_pt.name}** | `{format_classical_rashi_dms(sph_pt.longitude_deg)}` | "
            f"{sph_pt.sign_name} | *{sph_pt.nakshatra.name}* Pada {sph_pt.nakshatra.pada} |"
        )
    lines.append("")

    lines.append("### Step 5 & Step 6 — Worked Case Study: *Jaimini Chara Karakas*, 12 *Arudha Padas*, *Shadbala*, & *Sarvashtakavarga*")
    lines.append("")
    lines.append("| Graha | 7-Karaka Role | 8-Karaka Role | Total *Shadbala* (`Virupas` / `Rupas`) | Required (`Rupas`) | *Shadbala* Ratio | *Vimshopaka* (`D16` / `20`) | *Bhinna Ashtakavarga* Total |")
    lines.append("|---|---|---|---|---|---|---|---|")
    ck7_map = {c.planet: f"**{c.karaka_code}** ({c.karaka_name})" for c in vis_rep.chara_karakas_7}
    ck8_map = {c.planet: f"**{c.karaka_code}** ({c.karaka_name})" for c in vis_rep.chara_karakas_8}
    for p_name in ("Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn", "Rahu"):
        c7_s = ck7_map.get(p_name, "—")
        c8_s = ck8_map.get(p_name, "—")
        if p_name in kun_rep.shadbala.planets:
            sb_p = kun_rep.shadbala.planets[p_name]
            vm_p = kun_rep.vimshopaka_shodashvarga[p_name]
            bav_p = kun_rep.ashtakavarga.bhinna_tables[p_name].total_bindus
            lines.append(
                f"| **{p_name}** | {c7_s} | {c8_s} | **`{sb_p.total_virupas:.1f}v` (`{sb_p.total_rupas:.2f}R`)** | "
                f"`{sb_p.required_rupas:.2f}R` | `{sb_p.strength_ratio:.2f}x` | `{vm_p.total_score:.2f} / 20` | `{bav_p} Bindus` |"
            )
        else:
            lines.append(f"| **{p_name}** | {c7_s} | {c8_s} | — (Shadow Node) | — | — | — | — |")
    lines.append("")

    lines.append(
        "**Worked 12 *Sarvashtakavarga* (`SAV`) Totals by Sign (`Mesha` to `Meena`):** "
        + ", ".join(
            f"**{RASHI_NAMES[i]}:** `{kun_rep.ashtakavarga.sarvashtakavarga_7[i]}`"
            for i in range(12)
        )
        + f" (Grand Total = **`{kun_rep.ashtakavarga.sarvashtakavarga_7_total} Bindus`**)."
    )
    lines.append("")
    lines.append(
        "**Worked 12 *Jaimini Arudha Padas* (`AL` to `UL`):** "
        + ", ".join(
            f"**{ap.pada_code}:** {ap.arudha_sign_name}{' *(Swastha)*' if ap.swastha_exception_applied else ''}"
            for ap in vis_rep.arudha_padas
        )
        + "."
    )
    lines.append("")
    lines.append(
        f"**Worked *Kalachakra Dasha* at Birth:** Chakra Group = **{kc_rep.chakra_group}**, "
        f"*Dehamsha* = **{kc_rep.deha_sign_name}**, *Jeevamsha* = **{kc_rep.jeeva_sign_name}**, "
        f"Paramayus = `{kc_rep.paramayus_years:.0f} Years`, Birth Period = **{kc_rep.mahadashas[0].sign_name}** (`{kc_rep.mahadashas[0].gati}` Gati)."
    )
    lines.append("")
    lines.append(
        "**Worked Sample of 36 *Tajika Sahams*:** "
        + ", ".join(
            f"**{sh.sanskrit_name}:** `{format_classical_rashi_dms(sh.longitude_deg)}`"
            for sh in list(sah_rep.values())[:12]
        )
        + f" *(all `{len(sah_rep)}` Sahams computed deterministically)*."
    )
    lines.append("")

    # =========================================================================
    # CHAPTER 21: Topocentric Parallax, Atmospheric Refraction, & Relativistic Astrometry
    # =========================================================================
    lines.append("## Chapter 21 — Topocentric WGS84 Surface-Observer Astrometry, Lunar Parallax (`1°02'`), Atmospheric Refraction, Air Mass, Doppler Velocity, & Relativistic Shapiro Delay")
    lines.append("")
    lines.append(
        "> **Why Topocentric & Relativistic Astrometry Matters:** Classical *Surya Siddhanta* (*Lambana* & *Nati* chapters) "
        "and modern IAU observatory physics agree that an observer stands on the rotating, oblate surface of the Earth (`r ≈ 6,378.137 km`), "
        "not at Earth's center. For the Moon, surface parallax shifts apparent sidereal longitude by up to **`1° 02' 00\"` (`3,720\"`)** — "
        "enough to flip `D9 Navamsa`, `D60 Shashtiamsa`, `Nakshatra Pada`, and `KP 249 Sub-Lords`."
    )
    lines.append("")
    topo_rep = we["frontier_topo_report"]
    lines.append("### 21.1 Worked Case Study: 13-Body Geocentric vs Topocentric & Relativistic Astrometry Table")
    lines.append("")
    lines.append("| Body | Geocentric Sidereal (`DMS`) | Topocentric Sidereal (`DMS`) | Parallax Shift (`Δλ\" / Δβ\"`) | Azimuth / True Alt / Refracted Alt | Air Mass `X` | Doppler `v_r` (`km/s`) | Light-Time `τ` (`s`) | Shapiro `Δt` (`μs`) | GR Defl (`mas`) | `D9 / D60 / KP` Flip Audit |")
    lines.append("|---|---|---|---|---|---|---|---|---|---|---|")
    for b_k, tb in topo_rep.bodies.items():
        flip_tag = (
            f"D9:{'FLIP' if tb.d9_navamsa_flipped else 'OK'}({tb.geocentric_d9_sign}->{tb.topocentric_d9_sign}) "
            f"D60:{'FLIP' if tb.d60_shashtiamsa_flipped else 'OK'}({tb.geocentric_d60_index}->{tb.topocentric_d60_index}) "
            f"KP:{'FLIP' if tb.kp_sub_lord_flipped else 'OK'}({tb.geocentric_kp_sub_lord}->{tb.topocentric_kp_sub_lord})"
        )
        lines.append(
            f"| **{tb.display_name}** | `{format_classical_rashi_dms(tb.geocentric_sidereal_lon_deg)}` | **`{tb.topocentric_classical_dms}`** | "
            f"`{tb.parallax_longitude_shift_arcsec:+.2f}\" / {tb.parallax_latitude_shift_arcsec:+.2f}\"` | "
            f"`Az {tb.azimuth_deg:.1f}° / Alt {tb.geometric_altitude_deg:+.2f}° -> {tb.apparent_altitude_deg:+.2f}° (+{tb.refraction_correction_arcsec:.1f}\")` | "
            f"`{tb.air_mass_rozenberg:.2f}` | `{tb.radial_velocity_km_s:+.3f}` | `{tb.light_time_seconds:.2f}s` | "
            f"`{tb.shapiro_delay_microseconds:.2f}μs` | `{tb.solar_gravitational_deflection_mas:.2f}` | `{flip_tag}` |"
        )
    lines.append("")

    lines.append("### 21.2 Daily Geocentric vs Topocentric Moon & Sun Parallax Almanac Across the Month (`05:30 IST`)")
    lines.append("")
    lines.append("| Date | Local Sidereal Time | Geocentric Moon (`DMS`) | Topocentric Moon (`DMS`) | Lunar Parallax Shift (`Δλ\" / Δβ\"`) | Moon Alt / Azimuth / Refraction | Geocentric vs Topocentric `D9 / D60 / KP-Sub` Audit |")
    lines.append("|---|---|---|---|---|---|---|")
    for d_row in comp.daily_rows:
        t_day = compute_topocentric_relativistic_astrometry(
            d_row.jd_reference_ut,
            comp.observer_latitude_deg,
            comp.observer_longitude_deg,
            elevation_m=491.0,
            ayanamsa=comp.ayanamsa_mode,
            adapter=ad,
        )
        tm = t_day.bodies["moon"]
        audit_s = (
            f"D9: {tm.geocentric_d9_sign}->{tm.topocentric_d9_sign} | "
            f"D60: #{tm.geocentric_d60_index}->#{tm.topocentric_d60_index} | "
            f"KP: {tm.geocentric_kp_sub_lord}->{tm.topocentric_kp_sub_lord}"
        )
        lines.append(
            f"| `{d_row.civil_date}` | `{d_row.local_sidereal_time_hms}` | `{format_classical_rashi_dms(tm.geocentric_sidereal_lon_deg)}` | "
            f"**`{tm.topocentric_classical_dms}`** | **`{tm.parallax_longitude_shift_arcsec:+.1f}\" / {tm.parallax_latitude_shift_arcsec:+.1f}\"`** | "
            f"`Alt {tm.apparent_altitude_deg:+.1f}° / Az {tm.azimuth_deg:.1f}° (Refr +{tm.refraction_correction_arcsec:.1f}\")` | `{audit_s}` |"
        )
    lines.append("")

    lines.append("### 21.3 Saemundsson-Bennett Atmospheric Refraction & Rozenberg Optical Air Mass Master Table (`-1°` to `90°` Altitude)")
    lines.append("")
    lines.append("| True Altitude `h₀` | Std Refraction (`15°C, 1013 hPa`) | Hot Tropical (`35°C, 1005 hPa`) | Cold Winter (`0°C, 1020 hPa`) | High Altitude (`2200m, 780 hPa`) | Rozenberg Optical Air Mass `X(z)` | Extinction Loss (`Δmag`, `k=0.20`) |")
    lines.append("|---|---|---|---|---|---|---|")
    for h_deg in (-1.0, -0.5, 0.0, 0.5, 1.0, 1.5, 2.0, 3.0, 4.0, 5.0, 6.0, 8.0, 10.0, 12.0, 15.0, 20.0, 25.0, 30.0, 35.0, 40.0, 45.0, 50.0, 60.0, 70.0, 80.0, 90.0):
        r_std = _saemundsson_refraction_arcsec(h_deg, 15.0, 1013.25)
        r_hot = _saemundsson_refraction_arcsec(h_deg, 35.0, 1005.0)
        r_cold = _saemundsson_refraction_arcsec(h_deg, 0.0, 1020.0)
        r_high = _saemundsson_refraction_arcsec(h_deg, 10.0, 780.0)
        am_x = _rozenberg_air_mass(h_deg + r_std / 3600.0)
        ext_mag = 0.20 * am_x
        lines.append(
            f"| **`{h_deg:+5.1f}°`** | `{r_std:6.1f}\"` (`{r_std/60.0:4.2f}'`) | `{r_hot:6.1f}\"` | `{r_cold:6.1f}\"` | `{r_high:6.1f}\"` | **`{am_x:5.2f}x`** | `+{ext_mag:4.2f} mag` |"
        )
    lines.append("")

    # =========================================================================
    # CHAPTER 22: Synodic Retrograde Phase-Space Loops & Triple-Pass Transit Solver
    # =========================================================================
    lines.append("## Chapter 22 — Synodic Retrograde Phase-Space Loops (*Vakri / Vakra-Tyaga*), Perigee Brilliance, & 360° Natal Triple-Pass Transit Matrix")
    lines.append("")
    retro_rep = we["frontier_retro_report"]
    lines.append("### 22.1 Complete 5-Point Synodic Retrograde Phase-Space Loops (±180 Days Around Reference Epoch)")
    lines.append("")
    lines.append("| Body | Pre-Shadow Entry | First Station `S₁` (*Vakri*) | Minimum Distance / Opposition Peak | Second Station `S₂` (*Margi*) | Post-Shadow Exit | Retrograde Arc Width | Loop Duration (`Days`) |")
    lines.append("|---|---|---|---|---|---|---|---|")
    for lp in retro_rep.loops:
        lines.append(
            f"| **{lp.body_key.capitalize()}** | `{lp.shadow_entry_iso_utc or '—'}` | "
            f"**`{lp.station_retrograde_iso_utc}`** (`{lp.station_retrograde_dms}`) | "
            f"`{lp.minimum_distance_iso_utc}` (`{lp.minimum_distance_au:.4f} AU`, `{lp.peak_visual_magnitude:+.2f} mag`) | "
            f"**`{lp.station_direct_iso_utc}`** (`{lp.station_direct_dms}`) | "
            f"`{lp.shadow_exit_iso_utc or '—'}` | **`{lp.retrograde_arc_deg:.2f}°`** | **`{lp.retrograde_duration_days:.2f} d`** |"
        )
    lines.append("")

    lines.append("### 22.2 Complete 360-Degree Zodiacal Retrograde Triple-Pass, Divisional (`D9/D10/D60`), & `KP` Master Reference Table (`0°` to `359°`)")
    lines.append("")
    lines.append("| Zodiacal Degree (`Nirayana`) | Classical `Rashi DMS` | `Nakshatra & Pada` | `D9 Navamsa` | `D10 Dasamsa` | `D60 Shashtiamsa` | `KP Sign / Star / Sub / Sub-Sub` | Active Retrograde Shadow Zone Status (±180d Window) |")
    lines.append("|---|---|---|---|---|---|---|---|")
    for deg_step in range(0, 360):
        lon_v = float(deg_step)
        nk_v = nakshatra_position(lon_v)
        d9_v = varga_sign(lon_v, "D9").sign_name
        d10_v = varga_sign(lon_v, "D10").sign_name
        d60_v = varga_sign(lon_v, "D60").sign_name
        kp_v = kp_coordinate_lords(lon_v)
        in_loops: list[str] = []
        for lp in retro_rep.loops:
            s1_l = lp.station_retrograde_lon_deg
            s2_l = lp.station_direct_lon_deg
            arc_w = (s1_l - s2_l) % 360.0
            rel_d = (s1_l - lon_v) % 360.0
            if 0.0 < arc_w < 40.0 and rel_d <= arc_w:
                in_loops.append(f"**{lp.body_key.capitalize()} Triple-Pass Zone** (`{lp.station_direct_dms}`..`{lp.station_retrograde_dms}`)")
        zone_str = "; ".join(in_loops) if in_loops else "Single Direct Transit Pass"
        lines.append(
            f"| **`{deg_step:03d}° 00'`** | `{format_classical_rashi_dms(lon_v)}` | *{nk_v.name}* P{nk_v.pada} ({nk_v.vimshottari_ruler}) | "
            f"**{d9_v}** | {d10_v} | {d60_v} | `{kp_v.sign_lord}/{kp_v.star_lord}/{kp_v.sub_lord}/{kp_v.sub_sub_lord}` | {zone_str} |"
        )
    lines.append("")

    # =========================================================================
    # CHAPTER 23: Solar & Lunar Eclipse Local Obscuration & Natal Grahan Sensitivity
    # =========================================================================
    lines.append("## Chapter 23 — Solar & Lunar Eclipse (*Surya & Chandra Grahan*) Local Obscuration, Nodal Limits, & Natal *Grahan* Sensitivity Compendium")
    lines.append("")
    ecl_rep = we["frontier_eclipse_report"]
    lines.append("### 23.1 Solar & Lunar Eclipses Around Epoch & Local Observer Obscuration")
    lines.append("")
    lines.append("| Eclipse Category | Subtype | Maximum Eclipse (`UTC`) | Sidereal Longitude (`DMS`) | Sign (`Rashi`) | `Nakshatra & Pada` | Local Visible? | Local Obscuration Fraction |")
    lines.append("|---|---|---|---|---|---|---|---|")
    for ec in ecl_rep.eclipses:
        lines.append(
            f"| **{ec.eclipse_Category}** | **{ec.eclipse_subtype}** | `{ec.maximum_iso_utc}` | **`{ec.sidereal_classical_dms}`** | "
            f"{ec.rashi_name} | *{ec.nakshatra_name}* P{ec.pada} | `{'YES' if ec.local_visible else 'No'}` | **`{ec.local_obscuration_fraction*100.0:.1f}%`** |"
        )
    lines.append("")
    if ecl_rep.natal_hits:
        lines.append("### 23.2 Worked Case Study: Natal *Grahan* Sensitivity Hits")
        lines.append("")
        lines.append("| Natal Point | Natal Longitude | Eclipse Type & Date (`UTC`) | Eclipse Longitude (`DMS`) | Aspect Type | Orb (`deg`) | Impact Severity |")
        lines.append("|---|---|---|---|---|---|---|")
        for nh in ecl_rep.natal_hits:
            lines.append(
                f"| **{nh.natal_point_name}** | `{nh.natal_sidereal_dms}` | **{nh.eclipse_subtype}** (`{nh.eclipse_iso_utc}`) | "
                f"`{nh.eclipse_sidereal_dms}` | **{nh.contact_type}** | `{nh.orb_deg:.2f}°` | **`{nh.sensitivity_score_0_to_100:.1f} / 100`** |"
            )
        lines.append("")

    # =========================================================================
    # CHAPTER 24: All 10 Conditional Parashari Nakshatra Dashas & Multi-Dasha Synchronicity
    # =========================================================================
    lines.append("## Chapter 24 — Complete Manual Compendium of All 10 Conditional Parashari *Nakshatra Dashas* (BPHS Ch. 46) & Multi-Dasha Synchronicity")
    lines.append("")
    lines.append(
        "> **Unabridged BPHS Chapter 46 Conditional Nakshatra Dasha Suite:** Beyond universal *Vimshottari* (`120y`), "
        "Maharishi Parashara prescribes nine conditional *Nakshatra Dashas* (*Ashtottari 108y, Shodashottari 116y, "
        "Dwadashottari 112y, Panchottari 105y, Shatabdika 100y, Chaturashiti-Sama 84y, Dwisaptati-Sama 72y, "
        "Shat-Trimsha-Sama 36y, and Yogini 36y*). Below is the complete 27-Nakshatra Opening Lord & Duration Master Matrix."
    )
    lines.append("")
    lines.append("### 24.1 Master 27-Nakshatra Opening Lord & Full Duration Lookup Table Across All 10 BPHS Nakshatra Dasha Systems")
    lines.append("")
    lines.append("| `#` | Nakshatra (`0°..360°`) | Vimshottari (`120y`) | Ashtottari (`108y`) | Shodashottari (`116y`) | Dwadashottari (`112y`) | Panchottari (`105y`) | Shatabdika (`100y`) | Chaturashiti (`84y`) | Dwisaptati (`72y`) | Shat-Trimsha (`36y`) | Yogini (`36y`) |")
    lines.append("|---|---|---|---|---|---|---|---|---|---|---|---|")
    for nk_i, nk_name in enumerate(NAKSHATRA_NAMES):
        row_cells: list[str] = [f"`#{nk_i+1:02d}`", f"**{nk_name}**"]
        for spec in BPHS_10_NAKSHATRA_DASHAS:
            s_k = spec["key"]
            lords_t = spec["lords"]
            yrs_t = spec["years"]
            st_n = int(spec["start_nakshatra_index"])
            dv = int(spec["divisor"])
            if s_k == "vimshottari":
                o_i = nk_i % 9
            elif s_k == "ashtottari":
                from ..jyotish.dasha import compute_ashtottari_dasha
                ash_rep = compute_ashtottari_dasha(nk_i * (360.0 / 27.0) + 1.0, 2451545.0)
                o_i = lords_t.index(ash_rep.opening_lord)
            elif s_k == "dwadashottari":
                o_i = ((st_n - nk_i) % 27) % dv
            elif s_k == "yogini":
                o_i = (nk_i + 3) % 8
            else:
                o_i = ((nk_i - st_n) % 27) % dv
            row_cells.append(f"`{lords_t[o_i]} ({int(yrs_t[o_i])}y)`")
        lines.append("| " + " | ".join(row_cells) + " |")
    lines.append("")

    dashas_rep = we["frontier_dashas_report"]
    lines.append("### 24.2 Worked Case Study: All 10 BPHS Conditional Dasha Eligibility & Active Period Synchronicity")
    lines.append("")
    lines.append("| Dasha System | Cycle (`Years`) | BPHS Conditional Eligibility | Eligibility Reason | Opening Lord & Balance (`Years`) | Active Mahadasha (`+24y`) | Active Antardasha (`+24y`) |")
    lines.append("|---|---|---|---|---|---|---|")
    for sys_e in dashas_rep.systems:
        lines.append(
            f"| **{sys_e.title}** | `{sys_e.total_cycle_years:.0f}y` | **`{'ELIGIBLE' if sys_e.is_conditionally_eligible else 'Secondary'}`** | "
            f"{sys_e.eligibility_reason} | `{sys_e.opening_lord}` (`{sys_e.birth_balance_years:.2f}y`) | "
            f"**`{sys_e.active_mahadasha_lord}`** | **`{sys_e.active_antardasha_lord}`** |"
        )
    lines.append("")
    lines.append("### 24.3 Worked Multi-Dasha Consensus Ranking")
    lines.append("")
    lines.append("| Rank | Graha | Active Mahadasha Count | Active Antardasha Count | Eligible-System MD Count | Consensus Score (`0..100`) | Supporting Dasha Systems |")
    lines.append("|---|---|---|---|---|---|---|")
    for rk_i, c_item in enumerate(dashas_rep.consensus_ranking, start=1):
        lines.append(
            f"| `#{rk_i}` | **{c_item.planet}** | `{c_item.active_mahadasha_count}` | `{c_item.active_antardasha_count}` | "
            f"`{c_item.eligible_system_mahadasha_count}` | **`{c_item.consensus_score_0_to_100:.1f}`** | `{', '.join(c_item.supporting_systems)}` |"
        )
    lines.append("")

    # =========================================================================
    # CHAPTER 25: 5-Level Vimshottari Prana-Dasha Sub-Hour Chronometer
    # =========================================================================
    lines.append("## Chapter 25 — 5-Level *Vimshottari Prana-Dasha* Sub-Hour Chronometer (*Mahadasha -> Antardasha -> Pratyantardasha -> Sookshma -> Prana*)")
    lines.append("")
    lines.append("### 25.1 Complete 81-Row *Mahadasha × Antardasha* Proportional Sub-Period Ready Reckoner (Exact Days, Hours, & Self-Sub *Pratyantardasha / Sookshma / Prana* Durations)")
    lines.append("")
    lines.append("| Mahadasha (`MD`) | Antardasha (`AD`) | `MD × AD` Duration (`Years`) | Exact Solar Days (`365.2425d/y`) | Self-`PD` Duration (`Days`) | Self-`Sookshma` Duration (`Hours`) | Self-`Prana` Duration (`Minutes`) |")
    lines.append("|---|---|---|---|---|---|---|")
    for md_l in VIMSHOTTARI_LORDS:
        md_y = float(VIMSHOTTARI_YEARS[md_l])
        for ad_l in VIMSHOTTARI_LORDS:
            ad_y = float(VIMSHOTTARI_YEARS[ad_l])
            w_ad = ad_y / 120.0
            ad_yrs = md_y * w_ad
            ad_days = ad_yrs * 365.2425
            pd_self_days = ad_days * w_ad
            sd_self_hours = pd_self_days * w_ad * 24.0
            pr_self_mins = sd_self_hours * w_ad * 60.0
            lines.append(
                f"| **{md_l}** (`{int(md_y)}y`) | **{ad_l}** (`{int(ad_y)}y`) | `{ad_yrs:.4f}y` | **`{ad_days:.2f} d`** | "
                f"`{pd_self_days:.2f} d` | `{sd_self_hours:.2f} h` | **`{pr_self_mins:.2f} min`** |"
            )
    lines.append("")

    prana_rep = we["frontier_prana_report"]
    lines.append(
        f"### 25.2 Worked Case Study: 5-Level *Prana-Dasha* Sub-Hour Chronometer at `{prana_rep.query_iso_utc}`\n\n"
        f"- **Level 1 (*Mahadasha*):** **{prana_rep.mahadasha_lord}** (`{prana_rep.mahadasha_start_iso}` to `{prana_rep.mahadasha_end_iso}`)\n"
        f"- **Level 2 (*Antardasha*):** **{prana_rep.antardasha_lord}** (`{prana_rep.antardasha_start_iso}` to `{prana_rep.antardasha_end_iso}`)\n"
        f"- **Level 3 (*Pratyantardasha*):** **{prana_rep.pratyantardasha_lord}** (`{prana_rep.pratyantardasha_start_iso}` to `{prana_rep.pratyantardasha_end_iso}`)\n"
        f"- **Level 4 (*Sookshma Dasha*):** **{prana_rep.sookshma_lord}** (`{prana_rep.sookshma_start_iso}` to `{prana_rep.sookshma_end_iso}`, Duration = `{prana_rep.sookshma_duration_hours:.2f} hours`)\n"
        f"- **Level 5 (*Active Prana Dasha*):** **`{prana_rep.active_prana_lord}`**"
    )
    lines.append("")
    lines.append("| Prana Order | Level-5 *Prana Dasha* Lord | Start (`UTC`) | End (`UTC`) | Duration (`Minutes`) | Active at Query? |")
    lines.append("|---|---|---|---|---|---|")
    for pr_i, pw in enumerate(prana_rep.prana_windows, start=1):
        lines.append(
            f"| `#{pr_i}` | **{pw.prana_lord}** | `{pw.start_iso_utc}` | `{pw.end_iso_utc}` | **`{pw.duration_minutes:.2f} min`** | `{'ACTIVE' if pw.is_active_at_query else '—'}` |"
        )
    lines.append("")

    # =========================================================================
    # CHAPTER 26: Complete 150-Division Nadi Amsa (Deva Keralam) Master Compendium
    # =========================================================================
    lines.append("## Chapter 26 — Complete 150-Division *Nadi Amsa* (`0°12'` *Chandra Kala Nadi / Deva Keralam*) Master Reckoning Table (`#001` to `#150`) & Birth-Time Rectification")
    lines.append("")
    lines.append(
        "> **150 *Nadi Amsas* per Rashi (`1,800` Across `360°`):** Each `30°` sign is divided into `150` micro-slices of **`0° 12' 00\"`** (`720\"`). "
        "In *Chara* (Movable: Mesha, Karka, Tula, Makara) signs, numbering runs directly `1..150`; in *Sthira* (Fixed: Vrishabha, Simha, Vrishchika, Kumbha) "
        "signs, numbering reverses `150..1`; in *Dwiswabhava* (Dual: Mithuna, Kanya, Dhanu, Meena) signs, numbering begins at the midpoint `76..150` followed by `1..75`."
    )
    lines.append("")
    lines.append("### 26.1 Unabridged 150-*Nadi Amsa* (`0°00'` to `30°00'`) Master Lookup Table")
    lines.append("")
    lines.append("| Slice `#` | Degree Span in Sign (`0°..30°`) | *Chara* (Movable) Nadi `#` & Name | *Sthira* (Fixed) Nadi `#` & Name | *Dwiswabhava* (Dual) Nadi `#` & Name | Nadi Planetary Ruler | Lagna Rectification Window (`Seconds`) |")
    lines.append("|---|---|---|---|---|---|---|")
    for sl_i in range(1, 151):
        d_start = (sl_i - 1) * 0.2
        d_end = sl_i * 0.2
        d_s_deg = int(d_start)
        d_s_min = int(round((d_start - d_s_deg) * 60.0))
        d_e_deg = int(d_end)
        d_e_min = int(round((d_end - d_e_deg) * 60.0))
        span_s = f"`{d_s_deg:02d}° {d_s_min:02d}' .. {d_e_deg:02d}° {d_e_min:02d}'`"

        n_chara = sl_i
        n_sthira = 151 - sl_i
        n_dwi = (sl_i + 75) if sl_i <= 75 else (sl_i - 75)

        def _nadi_label(n_num: int) -> str:
            b_nm = NADI_AMSA_BASE_NAMES_15[(n_num - 1) % 15]
            q_nm = NADI_AMSA_DECADE_QUALITIES_10[(n_num - 1) // 15]
            return f"`#{n_num:03d}` **{b_nm}** *({q_nm})*"

        ruler_c = VIMSHOTTARI_LORDS[(n_chara - 1) % 9]
        lines.append(
            f"| **`#{sl_i:03d}`** | {span_s} | {_nadi_label(n_chara)} | {_nadi_label(n_sthira)} | {_nadi_label(n_dwi)} | **{ruler_c}** | `48.0 sec` (`0°12'` Lagna shift) |"
        )
    lines.append("")

    nadi_rep = we["frontier_nadi_report"]
    lines.append("### 26.2 Worked Case Study: Natal 150-*Nadi Amsa* Coordinates & Exact Seconds to Boundary Flip")
    lines.append("")
    lines.append("| Point | Sidereal Longitude (`DMS`) | Sign & Modality | Nadi `#` (`1..150`) | Zodiacal Nadi (`1..1800`) | Classical *Deva Keralam* Nadi Name | Nadi Ruler | Seconds to Prev / Next Nadi Flip |")
    lines.append("|---|---|---|---|---|---|---|---|")
    for nc in (nadi_rep.ascendant_nadi, *nadi_rep.planet_nadis.values()):
        lines.append(
            f"| **{nc.point_name}** | `{nc.classical_dms}` | {nc.rashi_name} *({nc.sign_modality})* | **`#{nc.nadi_amsa_number_1_to_150:03d}`** | "
            f"`#{nc.zodiacal_nadi_index_1_to_1800:04d}` | **{nc.nadi_amsa_name}** | `{nc.nadi_ruler}` | "
            f"`-{nc.seconds_of_birth_time_to_prev_nadi:.1f}s / +{nc.seconds_of_birth_time_to_next_nadi:.1f}s` |"
        )
    lines.append("")

    lines.append("### 26.3 Complete 360-Degree Zodiacal *Deva Keralam Nadi Amsa* (`1..1800`) & *Shashtiamsa* (`D60`) Deity Cross-Reference Encyclopedia (`0°` to `359°`)")
    lines.append("")
    lines.append("| Zodiacal Degree | `Rashi & Degree` | Sign Modality | Slice (`1..150`) | Modality-Adjusted Nadi `#` | Zodiacal Nadi (`1..1800`) | *Deva Keralam* Nadi Name & Quality | `D60` *Shashtiamsa* `#` & Deity |")
    lines.append("|---|---|---|---|---|---|---|---|")
    for deg_z in range(0, 360):
        r_z = deg_z // 30
        d_in_s = deg_z % 30
        sl_z = d_in_s * 5 + 1
        if (r_z % 3) == 0:
            mod_z = "Chara (Direct)"
            n_z = sl_z
        elif (r_z % 3) == 1:
            mod_z = "Sthira (Reverse)"
            n_z = 151 - sl_z
        else:
            mod_z = "Dwiswabhava (Mid)"
            n_z = (sl_z + 75) if sl_z <= 75 else (sl_z - 75)
        zn_idx = r_z * 150 + n_z
        b_nm_z = NADI_AMSA_BASE_NAMES_15[(n_z - 1) % 15]
        q_nm_z = NADI_AMSA_DECADE_QUALITIES_10[(n_z - 1) // 15]
        sh_idx = min(59, d_in_s * 2)
        sh_entry = SHASHTIAMSA_CATALOG[sh_idx]
        lines.append(
            f"| **`{deg_z:03d}° 00'`** | **{RASHI_NAMES[r_z]}** `{d_in_s:02d}° 00'` | {mod_z} | `Slice #{sl_z:03d}` | "
            f"**`Nadi #{n_z:03d}`** | `#{zn_idx:04d} / 1800` | **{b_nm_z}** *({q_nm_z})* | `D60 #{sh_idx+1:02d}` **{sh_entry[1]}** *({sh_entry[2]})* |"
        )
    lines.append("")

    # =========================================================================
    # CHAPTER 27: Complete 3-Ring Sudarshana Chakra (BPHS Ch. 67) & 100-Year Progression
    # =========================================================================
    lines.append("## Chapter 27 — Complete 3-Ring *Sudarshana Chakra* (BPHS Ch. 67: *Lagna, Chandra, & Surya* Wheels) & 100-Year Cyclic Progression Table")
    lines.append("")
    lines.append("### 27.1 Worked Case Study: 12-House 3-Ring *Sudarshana Chakra* Synthesis Matrix")
    lines.append("")
    lines.append("| Bhava (`1..12`) | Inner Ring: *Lagna* Sign & Lord | *Lagna* Occupants | Middle Ring: *Chandra* Sign & Lord | *Chandra* Occupants | Outer Ring: *Surya* Sign & Lord | *Surya* Occupants | 3-Ring Convergence Score (`0..100`) |")
    lines.append("|---|---|---|---|---|---|---|---|")
    for sh_r in nadi_rep.sudarshana_houses:
        lines.append(
            f"| **Bhava `{sh_r.house_number:02d}`** | **{sh_r.lagna_ring_sign}** ({sh_r.lagna_ring_lord}) | `{', '.join(sh_r.lagna_ring_occupants) or '—'}` | "
            f"**{sh_r.chandra_ring_sign}** ({sh_r.chandra_ring_lord}) | `{', '.join(sh_r.chandra_ring_occupants) or '—'}` | "
            f"**{sh_r.surya_ring_sign}** ({sh_r.surya_ring_lord}) | `{', '.join(sh_r.surya_ring_occupants) or '—'}` | **`{sh_r.triple_frame_convergence_score_0_to_100:.1f}`** |"
        )
    lines.append("")

    lines.append("### 27.2 Complete 100-Year *Sudarshana Chakra* Annual Progression Table (Ages `1` to `100`)")
    lines.append("")
    lines.append("| AgeYear | Progressed House (`Bhava`) | Progressed *Lagna* Sign & Lord | Progressed *Chandra* Sign & Lord | Progressed *Surya* Sign & Lord | Annual 3-Ring Convergence Score |")
    lines.append("|---|---|---|---|---|---|")
    for age_y in range(1, 101):
        h_idx = (age_y - 1) % 12
        sh_row = nadi_rep.sudarshana_houses[h_idx]
        lines.append(
            f"| **Year `{age_y:03d}`** (Age {age_y-1}..{age_y}) | **Bhava `{sh_row.house_number:02d}`** | **{sh_row.lagna_ring_sign}** ({sh_row.lagna_ring_lord}) | "
            f"**{sh_row.chandra_ring_sign}** ({sh_row.chandra_ring_lord}) | **{sh_row.surya_ring_sign}** ({sh_row.surya_ring_lord}) | **`{sh_row.triple_frame_convergence_score_0_to_100:.1f}`** |"
        )
    lines.append("")

    # =========================================================================
    # CHAPTER 28: Golden Muhurta Electional Optimizer, 27x27 Tarabala, & Panchaka Rahita
    # =========================================================================
    lines.append("## Chapter 28 — Golden *Muhurta* Electional Optimization, Complete `27 × 9` *Tarabala* & `12 × 12` *Chandrabala* Master Reckoners, & *Panchaka Rahita* Matrix")
    lines.append("")
    lines.append("### 28.1 Complete 27-Nakshatra *Navatara* (`9-Tara` Cycle) *Tarabala* Master Lookup Matrix")
    lines.append("")
    lines.append("| Birth Star (`Janma Nakshatra`) | `1: Janma` (Mixed) | `2: Sampat` (Wealth) | `3: Vipat` (Danger) | `4: Kshema` (Prosperity) | `5: Pratyak` (Obstacle) | `6: Sadhana` (Success) | `7: Naidhana` (Peril) | `8: Mitra` (Friend) | `9: Parama Mitra` (Supreme) |")
    lines.append("|---|---|---|---|---|---|---|---|---|---|")
    for b_nk_i, b_nk_name in enumerate(NAKSHATRA_NAMES):
        tara_cols: list[str] = []
        for t_rem in range(9):
            stars_in_tara = [
                NAKSHATRA_NAMES[(b_nk_i + t_rem + 9 * grp) % 27]
                for grp in range(3)
            ]
            tara_cols.append(", ".join(stars_in_tara))
        lines.append(f"| **`#{b_nk_i+1:02d}` {b_nk_name}** | " + " | ".join(tara_cols) + " |")
    lines.append("")

    lines.append("### 28.2 Complete `12 × 12` *Chandrabala* (Natal Moon Rashi vs Transit Moon Rashi) Master Matrix")
    lines.append("")
    lines.append("| Natal Moon Rashi (`Janma Rashi`) | Auspicious Transit Moon Signs (`1, 3, 6, 7, 10, 11` = *Shubha Chandrabala*) | Avoided *Ashtama / Dusthana* Signs (`4, 8, 12` = *Chandrashtama / Ari*) | Neutral Signs (`2, 5, 9`) |")
    lines.append("|---|---|---|---|")
    for m_r_i, m_r_name in enumerate(RASHI_NAMES):
        good_r = [f"**{RASHI_NAMES[(m_r_i + h - 1) % 12]}** ({h}H)" for h in (1, 3, 6, 7, 10, 11)]
        bad_r = [f"`{RASHI_NAMES[(m_r_i + h - 1) % 12]}` ({h}H)" for h in (4, 8, 12)]
        neu_r = [f"{RASHI_NAMES[(m_r_i + h - 1) % 12]} ({h}H)" for h in (2, 5, 9)]
        lines.append(f"| **{m_r_name}** | {', '.join(good_r)} | {', '.join(bad_r)} | {', '.join(neu_r)} |")
    lines.append("")

    muh_rep = we["frontier_muhurta_report"]
    lines.append("### 28.3 Worked Case Study: Top 15 Golden *Muhurta* Electional Windows (12-Constraint Multi-Objective Optimization)")
    lines.append("")
    lines.append("| Rank | Window (`UTC`) | Vara | Tithi | Nakshatra | Yoga | Ascendant (`Lagna`) | *Panchaka Rahita* | *Tarabala* | *Chandrabala* | Score (`0..100`) | Grade & Auspicious Factors |")
    lines.append("|---|---|---|---|---|---|---|---|---|---|---|---|")
    for mw_i, mw in enumerate(muh_rep.top_windows, start=1):
        panch_s = f"Shubha (r={mw.panchaka_remainder})" if mw.is_panchaka_rahita else f"Dosha (r={mw.panchaka_remainder})"
        lines.append(
            f"| `#{mw_i:02d}` | `{mw.iso_utc}` | {mw.vara_name} | {mw.paksha} #{mw.tithi_number} | *{mw.nakshatra_name}* | Yoga #{mw.yoga_number} | "
            f"**{mw.electional_lagna_sign}** | `{panch_s}` | `{mw.tarabala_name}` | {mw.chandrabala_house_1_to_12}H | "
            f"**`{mw.score_0_to_100:.1f}`** | **{mw.grade}**: {', '.join(mw.passed_checks[:3])} |"
        )
    lines.append("")

    lines.append("### 28.4 Complete `30 Tithi × 7 Vara` (`210-Row`) *Panchaka Rahita*, *Dagdha Rashi*, & *Amrita/Sarvartha Siddhi* Electional Master Table")
    lines.append("")
    lines.append("| Lunar Tithi (`1..30`) | Paksha & Tithi Group (*Nanda/Bhadra/Jaya/Rikta/Purna*) | Weekday (`Vara`) | *Dagdha Rashi* (Burnt Sign to Avoid) | *Amrita Siddhi* Star | *Sarvartha Siddhi* Stars | Safe *Panchaka Rahita* Ascendants (`Mesha..Meena` for Star #1) |")
    lines.append("|---|---|---|---|---|---|---|")
    tithi_groups_5 = ("Nanda (Joy)", "Bhadra (Good)", "Jaya (Victory)", "Rikta (Empty/Avoid)", "Purna (Fullness)")
    weekdays_7 = ("Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday")
    for t_num in range(1, 31):
        pk_name = "Shukla" if t_num <= 15 else "Krishna"
        pk_tithi = t_num if t_num <= 15 else (t_num - 15)
        t_grp = tithi_groups_5[(pk_tithi - 1) % 5]
        dag_pair = DAGDHA_RASI_BY_PAKSHA_TITHI.get(pk_tithi, ())
        dag_str = ", ".join(RASHI_NAMES[idx] for idx in dag_pair) if dag_pair else "None (Shubha)"
        for w_idx, w_name in enumerate(weekdays_7):
            am_idx = AMRITA_SIDDHI_NAKSHATRA.get(w_idx)
            am_str = NAKSHATRA_NAMES[am_idx] if am_idx is not None else "—"
            sarv_indices = SARVARTHA_SIDDHI_NAKSHATRAS.get(w_idx, ())
            sarv_str = ", ".join(NAKSHATRA_NAMES[idx] for idx in sorted(sarv_indices)[:4])
            safe_lagnas = [
                RASHI_NAMES[lg_i]
                for lg_i in range(12)
                if ((t_num + (w_idx + 1) + 1 + (lg_i + 1)) % 9) not in (1, 2, 4, 6, 8)
            ]
            lines.append(
                f"| **`Tithi #{t_num:02d}`** ({pk_name} {pk_tithi:02d}) | {t_grp} | **{w_name}** | `{dag_str}` | *{am_str}* | {sarv_str} | {', '.join(safe_lagnas[:6])} |"
            )
    lines.append("")

    # =========================================================================
    # CHAPTER 29: Continuous Sinusoidal Exaltation Potential, Arohi/Avarohi Climb, & Kalansha Heliacal Phenomena
    # =========================================================================
    dig_rep = we["frontier_dignity_report"]
    lines.append("## Chapter 29 — Continuous Sinusoidal *Uchcha-Neecha* Exaltation Potential, *Arohi/Avarohi* Orbital Climb Velocity, 3D *Digbala*, & *Surya Siddhanta Kalansha* Heliacal Phenomena")
    lines.append("")
    lines.append("> **Why Continuous Dignity Replaces Binary Lookup Tables:** Traditional software treats exaltation (*Uchcha*) as a step function by sign. RDG evaluates both the classical linear *Uchcha Bala* (`0..60 Virupas`) and the smooth harmonic potential `U(lambda) = 50 * (1 + cos(lambda - lambda_uchcha))` along with its exact time derivative `dU/dt` (*Arohi* ascending toward exaltation vs. *Avarohi* descending toward debilitation) and exact *Surya Siddhanta Kalansha* heliacal rising (*Udaya*) and setting (*Asta*) crossings.")
    lines.append("")
    lines.append(f"### 29.1 Worked Case Study: 9-Graha Continuous *Uchcha* Potential, *Arohi/Avarohi* Gradient, 3D *Digbala*, & Heliacal State (`Chart Uchcha Harmony = {dig_rep.overall_chart_uchcha_harmony_0_to_100:.2f}/100`)")
    lines.append("")
    lines.append("| Graha | Sidereal Lon (`deg`) | Speed (`deg/d`) | Deep Exaltation (`deg`) | *Uchcha* Potential (`0..100`) | *Uchcha Bala* (`0..60v`) | *Arohi / Avarohi* Climb State | `dU/dt` (`/day`) | Peak *Digbala* House | *Digbala* (`0..60v`) | Solar Elongation | *Kalansha* Limit | Heliacal Visibility & Nearest Crossing |")
    lines.append("|---|---|---|---|---|---|---|---|---|---|---|---|---|")
    for pd in dig_rep.planets:
        hel_evt = f"{pd.nearest_heliacal_event_type} @ `{pd.nearest_heliacal_event_utc}`" if pd.nearest_heliacal_event_type else "None in ±45d"
        lines.append(
            f"| **{pd.body}** | `{pd.sidereal_longitude_deg:.4f}°` | `{pd.speed_deg_per_day:+.4f}°` | `{pd.exaltation_point_deg:.1f}°` | "
            f"**`{pd.uchcha_potential_0_to_100:.2f}`** | `{pd.uchcha_vira_virupas_0_to_60:.2f}v` | `{pd.arohi_avarohi_state}` | `{pd.dignity_velocity_per_day:+.4f}` | "
            f"`{pd.digbala_peak_house}H` | `{pd.digbala_continuous_virupas_0_to_60:.2f}v` | `{pd.solar_elongation_deg:.2f}°` | `{pd.kalansha_threshold_deg:.1f}°` | **{pd.heliacal_visibility_state}** ({hel_evt}) |"
        )
    lines.append("")

    lines.append("### 29.2 Complete 36-Row (`0°` to `350°` in `10°` Steps) Manual *Uchcha-Neecha* Harmonic Potential & *Arohi/Avarohi* Lookup Reckoner")
    lines.append("")
    lines.append("| Angular Offset `Δλ = λ - λ_uchcha` | Absolute Distance `|Δλ|` | Classical *Uchcha Bala* (`(180 - |Δλ|)/3` Virupas) | Harmonic Potential `50*(1 + cos Δλ)` (`0..100`) | Orbital Climb Phase (Direct Motion `v > 0`) | Orbital Climb Phase (Retrograde Motion `v < 0`) |")
    lines.append("|---|---|---|---|---|---|")
    for step_deg in range(0, 360, 10):
        signed_d = ((step_deg + 180.0) % 360.0) - 180.0
        abs_d = abs(signed_d)
        vir_u = (180.0 - abs_d) / 3.0
        pot_u = 50.0 * (1.0 + math.cos(math.radians(signed_d)))
        phase_dir = "PEAK / NADIR" if step_deg in (0, 180) else ("AVAROHI (Descending to Neecha)" if 0 < step_deg < 180 else "AROHI (Ascending to Uchcha)")
        phase_ret = "PEAK / NADIR" if step_deg in (0, 180) else ("AROHI (Retrograde Climb)" if 0 < step_deg < 180 else "AVAROHI (Retrograde Descent)")
        lines.append(
            f"| **`{step_deg:03d}°`** (`{signed_d:+.0f}°`) | `{abs_d:.0f}°` | **`{vir_u:.2f} Virupas`** | **`{pot_u:.2f} / 100`** | {phase_dir} | {phase_ret} |"
        )
    lines.append("")

    # =========================================================================
    # CHAPTER 30: 81-Cell Sarvatobhadra Trishula Ray-Tracer, Shodhya Pinda Triggers, & Harmonic Yogas
    # =========================================================================
    sbc_rep = we["frontier_sbc_report"]
    pinda_rep = we["frontier_pinda_report"]
    lines.append("## Chapter 30 — 81-Cell *Sarvatobhadra Trishula* Ray-Tracer, 7-Planet *Shodhya Pinda* Trigger Stars, 12-House *Vitta-Ayavyaya* Wealth Matrix, & Continuous Harmonic *Yoga* Potency")
    lines.append("")
    lines.append(f"### 30.1 Worked Case Study: 9x9 *Sarvatobhadra Chakra* 3-Way *Trishula Vedha* Ray-Trace (`Net Protection Index = {sbc_rep.net_vedha_protection_index_minus100_to_plus100:+.1f}`, Verdict: {sbc_rep.verdict_summary})")
    lines.append("")
    lines.append("| Transiting Graha | Source 28-Star (`Nakshatra`) | Border Grid `(r, c)` | Ray Direction (*Sammukha / Vama / Dakshina*) | Target Cell `(r, c)` | Target Type | Target Label | *Vedha* Nature | Hits Natal *Janma Star / Rashi / Akshara* |")
    lines.append("|---|---|---|---|---|---|---|---|---|")
    for hit in sbc_rep.active_ray_hits[:36]:
        hit_flags = []
        if hit.hits_natal_janma_nakshatra:
            hit_flags.append("JANMA_NAKSHATRA")
        if hit.hits_natal_janma_rashi:
            hit_flags.append("JANMA_RASHI")
        if hit.hits_natal_nama_akshara:
            hit_flags.append("NAMA_AKSHARA")
        flag_s = ", ".join(hit_flags) if hit_flags else "Perimeter Nakshatra"
        lines.append(
            f"| **{hit.transiting_body}** | *{hit.transiting_nakshatra_28}* | `({hit.transiting_grid_row}, {hit.transiting_grid_col})` | `{hit.ray_direction}` | "
            f"`({hit.target_row}, {hit.target_col})` | `{hit.target_cell_type}` | **{hit.target_label}** | `{hit.vedha_nature}` | `{flag_s}` |"
        )
    lines.append("")

    lines.append("### 30.2 Worked Case Study: 7-Planet *Trikona & Ekadhipatya Shodhana*, *Rashi / Graha / Shodhya Pinda*, & 27-Nakshatra Transit Trigger Stars")
    lines.append("")
    lines.append("| Graha | Raw BAV Bindus | *Trikona* Reduced Sum | *Ekadhipatya* Reduced Sum | *Rashi Pinda* | *Graha Pinda* | *Shodhya Pinda* (`S`) | Classical Trigger Star (`(S × 7) mod 27`) | *Lagna-Bindu* Trigger Star | Current Transit Star | Active Trigger Hit |")
    lines.append("|---|---|---|---|---|---|---|---|---|---|---|")
    for sp_r in pinda_rep.shodhya_pinda_rows:
        lines.append(
            f"| **{sp_r.body}** | `{sp_r.raw_bav_total_bindus}` | `{sp_r.trikona_reduced_total}` | `{sp_r.ekadhipatya_reduced_total}` | "
            f"`{sp_r.rashi_pinda}` | `{sp_r.graha_pinda}` | **`{sp_r.shodhya_pinda}`** | **#{sp_r.sodya_nakshatra_index_1_to_27:02d} {sp_r.sodya_trigger_nakshatra}** | "
            f"*{sp_r.kendra_kona_trigger_nakshatra}* | {sp_r.current_transit_nakshatra} | `{'YES' if sp_r.is_transit_on_sodya_trigger_now else 'No'}` |"
        )
    lines.append("")

    lines.append(f"### 30.3 Worked Case Study: 12-House *Bandhu / Sevaka / Poshaka / Ghataka* Vitality & *Vitta-Ayavyaya* Wealth Surplus (`Wealth Index = {pinda_rep.vitta_ayavyaya_wealth_index_0_to_100:.1f}/100`)")
    lines.append("")
    lines.append("| House (`Bhava`) | Sign (`Rashi`) | SAV Bindus | *Bandhu* (`7th` from House) | *Sevaka* (`6th` from House) | *Poshaka* (`11th` Gains) | *Ghataka* (`12th` Loss) | *Artha* Net Surplus (`Poshaka - Ghataka`) | Prosperity Tier |")
    lines.append("|---|---|---|---|---|---|---|---|---|")
    for hv_r in pinda_rep.house_vitality_rows:
        lines.append(
            f"| **House `{hv_r.house_number:02d}`** | **{hv_r.rashi_name}** | **`{hv_r.sav_bindus}`** | `{hv_r.bandhu_7th_bindus}` | `{hv_r.sevaka_6th_bindus}` | "
            f"`{hv_r.poshaka_11th_bindus}` | `{hv_r.ghataka_12th_bindus}` | **`{hv_r.artha_net_surplus:+d}`** | `{hv_r.prosperity_tier}` |"
        )
    lines.append("")

    lines.append("### 30.4 Worked Case Study: Continuous Harmonic Phase-Coherence *Yoga* Potency Tensor")
    lines.append("")
    lines.append("| Classical *Yoga* Resonance | Category | Participating Grahas | Exact Separation (`deg`) | Ideal Harmonic (`deg`) | Orb Error (`deg`) | Phase Coherence (`0..100`) | Dignity-Weighted Potency (`0..100`) | Plain-English Effect |")
    lines.append("|---|---|---|---|---|---|---|---|---|")
    for hy_r in pinda_rep.harmonic_yogas:
        lines.append(
            f"| **{hy_r.yoga_name}** | `{hy_r.category}` | {', '.join(hy_r.participating_bodies)} | `{hy_r.exact_angular_separation_deg:.2f}°` | "
            f"`{hy_r.ideal_harmonic_angle_deg:.1f}°` | `{hy_r.orb_error_deg:.2f}°` | `{hy_r.phase_coherence_score_0_to_100:.1f}` | "
            f"**`{hy_r.dignity_weighted_potency_0_to_100:.1f}`** | {hy_r.plain_english_effect} |"
        )
    lines.append("")
    return "\n".join(lines)


def _format_inline_md(text: str) -> str:
    """Convert inline Markdown formatting (bold, italic, inline code, and `<br/>` line breaks) to clean HTML."""
    br_token = "___BR_TOKEN___"
    cleaned = text.replace("<br/>", br_token).replace("<br>", br_token)
    escaped = html_mod.escape(cleaned)
    escaped = re.sub(r"`([^`]+)`", r"<code>\1</code>", escaped)
    escaped = re.sub(r"\*\*([^*]+)\*\*", r"<strong>\1</strong>", escaped)
    escaped = re.sub(r"\*([^*]+)\*", r"<em>\1</em>", escaped)
    escaped = escaped.replace(br_token, "<br/>")
    return escaped


def _render_compendium_html(comp: HumanManualEphemerisCompendium) -> str:
    """Render a richly formatted, multi-chapter, print-ready HTML book edition with real HTML tables and a Table of Contents."""
    md_text = comp.to_markdown()
    md_lines = md_text.splitlines()

    toc_items: list[tuple[str, str]] = []
    body_parts: list[str] = []
    in_table = False
    in_list = False
    in_blockquote = False
    chapter_idx = 0

    def close_blocks() -> None:
        nonlocal in_table, in_list, in_blockquote
        if in_table:
            body_parts.append("</tbody></table></div>")
            in_table = False
        if in_list:
            body_parts.append("</ul>")
            in_list = False
        if in_blockquote:
            body_parts.append("</blockquote>")
            in_blockquote = False

    i = 0
    while i < len(md_lines):
        raw_line = md_lines[i]
        stripped = raw_line.strip()

        if not stripped:
            close_blocks()
            i += 1
            continue

        if stripped.startswith("# "):
            close_blocks()
            title_html = _format_inline_md(stripped[2:].strip())
            body_parts.append(f"<header class='book-header'><h1>{title_html}</h1></header>")
            i += 1
            continue

        if stripped.startswith("## "):
            close_blocks()
            chapter_idx += 1
            sec_id = f"chapter-{chapter_idx:02d}"
            sec_title = stripped[3:].strip()
            toc_items.append((sec_id, _format_inline_md(sec_title)))
            body_parts.append(f"<section class='chapter-section' id='{sec_id}'><h2>{_format_inline_md(sec_title)}</h2></section>")
            i += 1
            continue

        if stripped.startswith("### "):
            close_blocks()
            sub_title = stripped[4:].strip()
            body_parts.append(f"<h3>{_format_inline_md(sub_title)}</h3>")
            i += 1
            continue

        if stripped.startswith(">"):
            if in_table or in_list:
                close_blocks()
            if not in_blockquote:
                body_parts.append("<blockquote class='academy-callout'>")
                in_blockquote = True
            q_content = stripped.lstrip(">").strip()
            body_parts.append(f"<p>{_format_inline_md(q_content)}</p>")
            i += 1
            continue

        if stripped.startswith("- "):
            if in_table or in_blockquote:
                close_blocks()
            if not in_list:
                body_parts.append("<ul class='compendium-list'>")
                in_list = True
            body_parts.append(f"<li>{_format_inline_md(stripped[2:].strip())}</li>")
            i += 1
            continue

        if stripped.startswith("|") and stripped.endswith("|"):
            if in_list or in_blockquote:
                close_blocks()
            cells = [c.strip() for c in stripped.strip("|").split("|")]
            if not in_table:
                body_parts.append("<div class='table-scroll'><table class='ephemeris-table'><thead><tr>")
                for c in cells:
                    body_parts.append(f"<th>{_format_inline_md(c)}</th>")
                body_parts.append("</tr></thead><tbody>")
                in_table = True
                # Skip separator row if next line is |---|---|
                if i + 1 < len(md_lines) and re.match(r"^\|\s*[-:]+", md_lines[i + 1].strip()):
                    i += 2
                    continue
            else:
                if all(re.match(r"^[-:\s]+$", c) for c in cells if c):
                    i += 1
                    continue
                body_parts.append("<tr>")
                for c in cells:
                    body_parts.append(f"<td>{_format_inline_md(c)}</td>")
                body_parts.append("</tr>")
            i += 1
            continue

        close_blocks()
        body_parts.append(f"<p>{_format_inline_md(stripped)}</p>")
        i += 1

    close_blocks()

    toc_html = "<nav class='toc-box'><h2>Master Table of Contents (30 Chapters)</h2><ol>" + "".join(
        f"<li><a href='#{cid}'>{ctitle}</a></li>" for cid, ctitle in toc_items
    ) + "</ol></nav>"

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8" />
<meta name="viewport" content="width=device-width, initial-scale=1" />
<title>RDG Ephemeris — 30-Chapter Classical Ephemeris &amp; Pt. Maheshji's Jyotish Academy Compendium ({comp.year}-{comp.month:02d})</title>
<style>
  :root {{
    --bg: #fdfaf3;
    --paper: #ffffff;
    --ink: #1a1815;
    --muted: #5a5246;
    --accent: #7a2012;
    --gold: #b8860b;
    --border: #d8cebe;
    --row-alt: #f8f3e8;
    --code-bg: #f1ead8;
  }}
  * {{ box-sizing: border-box; }}
  body {{
    font-family: "Georgia", "Cambria", "Times New Roman", serif;
    background: var(--bg);
    color: var(--ink);
    margin: 0;
    padding: 20px 24px;
    line-height: 1.5;
  }}
  .page-container {{
    max-width: 1560px;
    width: 100%;
    margin: 0 auto;
    background: var(--paper);
    border: 1px solid var(--border);
    box-shadow: 0 8px 28px rgba(0,0,0,0.06);
    padding: 28px 32px;
  }}
  .book-header h1 {{
    font-size: 1.85rem;
    color: var(--accent);
    border-bottom: 3px double var(--gold);
    padding-bottom: 12px;
    margin-top: 0;
  }}
  h2 {{
    font-size: 1.35rem;
    color: var(--accent);
    border-bottom: 2px solid var(--border);
    padding-bottom: 6px;
    margin-top: 32px;
  }}
  h3 {{
    font-size: 1.08rem;
    color: #2f261d;
    margin-top: 20px;
    margin-bottom: 8px;
  }}
  .toc-box {{
    background: var(--row-alt);
    border: 1px solid var(--border);
    border-left: 5px solid var(--gold);
    padding: 16px 22px;
    margin: 18px 0 28px 0;
    border-radius: 4px;
  }}
  .toc-box h2 {{
    margin-top: 0;
    font-size: 1.15rem;
    border-bottom: none;
  }}
  .toc-box ol {{
    columns: 2;
    column-gap: 32px;
    margin: 0;
    padding-left: 20px;
  }}
  .toc-box li {{
    margin-bottom: 5px;
    font-size: 0.9rem;
  }}
  .toc-box a {{
    color: var(--accent);
    text-decoration: none;
  }}
  .toc-box a:hover {{
    text-decoration: underline;
  }}
  .academy-callout {{
    background: #fbf5e6;
    border-left: 4px solid var(--accent);
    padding: 12px 18px;
    margin: 14px 0;
    font-size: 0.95rem;
  }}
  .table-scroll {{
    width: 100%;
    max-width: 100%;
    overflow-x: hidden;
    margin: 10px 0 20px 0;
  }}
  table.ephemeris-table {{
    width: 100%;
    max-width: 100%;
    table-layout: fixed;
    border-collapse: collapse;
    font-size: 0.72rem;
    font-family: "Consolas", "Menlo", "Monaco", monospace;
    word-break: break-word;
    overflow-wrap: anywhere;
  }}
  table.ephemeris-table th {{
    background: #2b2118;
    color: #fdfaf3;
    text-align: left;
    padding: 4px 5px;
    border: 1px solid #3d3024;
    font-weight: 600;
    white-space: normal;
    word-break: break-word;
    overflow-wrap: anywhere;
  }}
  table.ephemeris-table td {{
    padding: 4px 5px;
    border: 1px solid var(--border);
    vertical-align: top;
    white-space: normal;
    word-break: break-word;
    overflow-wrap: anywhere;
  }}
  table.ephemeris-table tbody tr:nth-child(even) {{
    background: var(--row-alt);
  }}
  code {{
    background: var(--code-bg);
    padding: 1px 3px;
    border-radius: 3px;
    font-family: "Consolas", "Menlo", monospace;
    font-size: 0.85em;
    white-space: normal;
    word-break: break-word;
    overflow-wrap: anywhere;
  }}
  @media print {{
    body {{ background: #fff; padding: 0; margin: 0; }}
    .page-container {{ box-shadow: none; border: none; padding: 4px; max-width: 100%; width: 100%; }}
    .chapter-section {{ page-break-before: always; }}
    table.ephemeris-table {{ font-size: 5.2pt; table-layout: fixed; width: 100%; max-width: 100%; }}
    table.ephemeris-table th, table.ephemeris-table td {{ padding: 2px 2px; }}
  }}
</style>
</head>
<body>
<div class="page-container">
{toc_html}
{''.join(body_parts)}
</div>
</body>
</html>
"""


__all__ = [
    "CLASSICAL_COMBUSTION_ORBS_DEG",
    "HumanDailyEphemerisRow",
    "HumanDailyPlanetCell",
    "HumanManualEphemerisCompendium",
    "LANKODAYA_VINADIS",
    "format_classical_rashi_dms",
    "format_daily_motion_dms",
    "format_ghati_pala",
    "generate_human_manual_ephemeris_compendium",
]
