"""Clean-room Special Lagnas (Vishesha Lagnas), Yogi/Avayogi, Jaimini Arudha Padas, Chara Karakas,
and Full 6-Coordinate Spherical & Physical Ephemeris Engine.

Mathematical formulations follow:
- *Brihat Parashara Hora Shastra* (Chapters 5, 29, 32: Special Lagnas, Arudha Padas, Chara Karakas, Pranapada)
- *Jaimini Upadesha Sutras* (Adhyaya 1 Pada 1-4: Arudha Padas, Swastha exception, 7/8 Chara Karakas)
- *Uttara Kalamrita* by Kalidasa (Khanda 4: Indu Lagna and Kala ray values)
- *Surya Siddhanta* & IAU 2006/2000A spherical coordinate conversions (Ecliptic to Equatorial RA/Dec,
  Horizontal Parallax, Apparent Semidiameter, Phase Angle, Illuminated Fraction, Visual Magnitude,
  and Second-Order Bessel Tabular Differences).
"""

from __future__ import annotations

from dataclasses import dataclass
import math
from typing import TYPE_CHECKING, Any, Mapping

from .._version import __version__
from ..engine.receipt import canonical_hash

if TYPE_CHECKING:
    from ..adapter import EphemerisAdapter
from ..jyotish_advanced.kp import kp_coordinate_lords
from ..jyotish_nadi.khara_mrityu import MRITYU_BHAGA_DEGREE_TABLE
from .nakshatra import (
    NAKSHATRA_NAMES,
    RASI_NAMES as RASHI_NAMES,
    VIMSHOTTARI_RULERS,
    nakshatra_position,
    normalize_degrees,
)
from .vargas import RASI_LORDS, varga_sign

AU_IN_KM: float = 149_597_870.700
EARTH_EQUATORIAL_RADIUS_KM: float = 6378.137

# Mean equatorial radii of Sun, Moon, and planets in km (IAU) for apparent angular diameter
BODY_EQUATORIAL_RADIUS_KM: Mapping[str, float] = {
    "sun": 695_700.0,
    "moon": 1_737.4,
    "mercury": 2_439.7,
    "venus": 6_051.8,
    "mars": 3_396.2,
    "jupiter": 71_492.0,
    "saturn": 60_268.0,
    "uranus": 25_559.0,
    "neptune": 24_764.0,
    "pluto": 1_188.3,
}

# Classical Kalidasa Uttara Kalamrita Kala (ray) values for Indu Lagna calculation
INDU_LAGNA_KALA_VALUES: Mapping[str, int] = {
    "Sun": 30,
    "Moon": 16,
    "Mars": 6,
    "Mercury": 8,
    "Jupiter": 10,
    "Venus": 12,
    "Saturn": 1,
}

# Classical Pushkara Bhaga exact degrees in each of the 12 signs (0=Mesha .. 11=Meena)
PUSHKARA_BHAGA_DEGREES: Mapping[int, float] = {
    0: 21.0,   # Mesha 21°
    1: 14.0,   # Vrishabha 14°
    2: 18.0,   # Mithuna 18°
    3: 8.0,    # Karka 8°
    4: 19.0,   # Simha 19°
    5: 9.0,    # Kanya 9°
    6: 24.0,   # Tula 24°
    7: 11.0,   # Vrishchika 11°
    8: 23.0,   # Dhanu 23°
    9: 14.0,   # Makara 14°
    10: 19.0,  # Kumbha 19°
    11: 9.0,   # Meena 9°
}

# Pushkara Navamsa sign pairs for Fire, Earth, Air, Water signs
PUSHKARA_NAVAMSA_RASHI_INDICES: Mapping[int, tuple[int, int]] = {
    0: (6, 8),   # Mesha -> Tula, Dhanu
    4: (6, 8),   # Simha -> Tula, Dhanu
    8: (6, 8),   # Dhanu -> Tula, Dhanu
    1: (11, 1),  # Vrishabha -> Meena, Vrishabha
    5: (11, 1),  # Kanya -> Meena, Vrishabha
    9: (11, 1),  # Makara -> Meena, Vrishabha
    2: (11, 1),  # Mithuna -> Meena, Vrishabha
    6: (11, 1),  # Tula -> Meena, Vrishabha
    10: (11, 1), # Kumbha -> Meena, Vrishabha
    3: (3, 5),   # Karka -> Karka, Kanya
    7: (3, 5),   # Vrishchika -> Karka, Kanya
    11: (3, 5),  # Meena -> Karka, Kanya
}

ARUDHA_HOUSE_NAMES: tuple[tuple[str, str], ...] = (
    ("AL", "Arudha Lagna (Pada 1 — Public Image & Maya)"),
    ("A2", "Dhana Pada (Pada 2 — Wealth & Speech)"),
    ("A3", "Vikrama Pada (Pada 3 — Enterprise & Siblings)"),
    ("A4", "Matri / Sukha Pada (Pada 4 — Property, Vehicles & Happiness)"),
    ("A5", "Mantra Pada (Pada 5 — Intelligence, Progeny & Authority)"),
    ("A6", "Roga / Shatru Pada (Pada 6 — Conflict, Debt & Litigation)"),
    ("A7", "Dara Pada (Pada 7 — Business Partnerships & Relationships)"),
    ("A8", "Mrityu Pada (Pada 8 — Transformation, Inheritance & Longevity)"),
    ("A9", "Bhagya / Dharma Pada (Pada 9 — Fortune, Guru & Higher Law)"),
    ("A10", "Rajya / Karma Pada (Pada 10 — Career, Throne & Command)"),
    ("A11", "Labha Pada (Pada 11 — Gains, Fulfillment & Networks)"),
    ("UL", "Upapada Lagna (Pada 12 — Marriage, Spouse & Commitment)"),
)

CHARA_KARAKA_7_TITLES: tuple[tuple[str, str], ...] = (
    ("AK", "Atmakaraka (Soul Significator — Highest Degree)"),
    ("AmK", "Amatyakaraka (Career & Minister Significator — 2nd Highest)"),
    ("BK", "Bhratrukaraka (Siblings, Guru & Courage — 3rd Highest)"),
    ("MK", "Matrukaraka (Mother, Homeland & Emotional Peace — 4th Highest)"),
    ("PK", "Putrakaraka (Children, Intelligence & Followers — 5th Highest)"),
    ("GK", "Gnathikaraka (Rivals, Kinsmen & Obstacles — 6th Highest)"),
    ("DK", "Darakaraka (Spouse & Business Partner — Lowest Degree)"),
)

CHARA_KARAKA_8_TITLES: tuple[tuple[str, str], ...] = (
    ("AK", "Atmakaraka (Soul Significator — Highest Degree)"),
    ("AmK", "Amatyakaraka (Career & Minister Significator — 2nd Highest)"),
    ("BK", "Bhratrukaraka (Siblings & Courage — 3rd Highest)"),
    ("MK", "Matrukaraka (Mother & Emotional Peace — 4th Highest)"),
    ("PiK", "Pitrukaraka (Father, Ancestors & Authority — 5th Highest)"),
    ("PK", "Putrakaraka (Children, Intelligence & Merit — 6th Highest)"),
    ("GK", "Gnathikaraka (Rivals, Kinsmen & Disease — 7th Highest)"),
    ("DK", "Darakaraka (Spouse & Partner — Lowest Degree)"),
)


def _format_rashi_dms(lon_deg: float) -> str:
    lon = lon_deg % 360.0
    rashi_idx = int(lon // 30.0) % 12
    deg_in_sign = lon - rashi_idx * 30.0
    total_arcsec = int(round(deg_in_sign * 3600.0))
    if total_arcsec >= 30 * 3600:
        total_arcsec = 0
        rashi_idx = (rashi_idx + 1) % 12
    d = total_arcsec // 3600
    rem = total_arcsec % 3600
    m = rem // 60
    s = rem % 60
    return f"{RASHI_NAMES[rashi_idx]} {d:02d}° {m:02d}' {s:02d}\""


def _format_signed_dms(angle_deg: float) -> str:
    sign = "-" if angle_deg < 0.0 else "+"
    val = abs(angle_deg)
    total_arcsec = int(round(val * 3600.0))
    d = total_arcsec // 3600
    rem = total_arcsec % 3600
    m = rem // 60
    s = rem % 60
    return f"{sign}{d:02d}° {m:02d}' {s:02d}\""


def _format_ra_hms(ra_deg: float) -> str:
    ra_hours = (ra_deg % 360.0) / 15.0
    total_sec = int(round(ra_hours * 3600.0)) % 86400
    hh = total_sec // 3600
    rem = total_sec % 3600
    mm = rem // 60
    ss = rem % 60
    return f"{hh:02d}h {mm:02d}m {ss:02d}s"


@dataclass(frozen=True)
class SpecialLagnaEntry:
    """One computed classical Vishesha Lagna (Special Ascendant)."""

    key: str
    sanskrit_name: str
    longitude_deg: float
    classical_dms: str
    rashi_index: int
    rashi_name: str
    rashi_lord: str
    nakshatra_name: str
    pada: int
    d9_navamsa_sign: str
    formula_summary: str

    @property
    def title(self) -> str:
        return self.sanskrit_name


VisheshaLagnaPoint = SpecialLagnaEntry


@dataclass(frozen=True)
class YogiAvayogiReport:
    """Classical Yogi, Sahayogi (Duplicate Yogi), and Avayogi calculation."""

    yogi_point_deg: float
    yogi_point_dms: str
    yogi_rashi_name: str
    yogi_nakshatra_name: str
    yogi_pada: int
    yogi_planet: str
    sahayogi_planet: str
    avayogi_point_deg: float
    avayogi_point_dms: str
    avayogi_rashi_name: str
    avayogi_nakshatra_name: str
    avayogi_pada: int
    avayogi_planet: str


@dataclass(frozen=True)
class ArudhaPadaEntry:
    """One Jaimini / Parashari Arudha Pada (A1..A12) with Swastha exception status."""

    house_number: int
    code: str
    title: str
    base_sign_index: int
    base_sign_name: str
    lord_planet: str
    lord_sign_index: int
    lord_sign_name: str
    raw_distance_signs: int
    swastha_exception_applied: bool
    arudha_sign_index: int
    arudha_sign_name: str
    arudha_sign_lord: str

    @property
    def pada_code(self) -> str:
        return self.code


ArudhaPadaDetail = ArudhaPadaEntry


@dataclass(frozen=True)
class CharaKarakaEntry:
    """One Jaimini Chara Karaka significator entry."""

    code: str
    title: str
    planet: str
    longitude_deg: float
    degree_in_sign: float
    effective_karaka_degree: float
    classical_dms: str
    rashi_name: str
    karakamsa_d9_sign: str

    @property
    def karaka_code(self) -> str:
        return self.code

    @property
    def karaka_name(self) -> str:
        return self.title


@dataclass(frozen=True)
class VisheshaLagnaAndSpecialPointsReport:
    """Unified report of all 8 Lagnas, Yogi/Avayogi, 12 Arudha Padas, and 7/8 Chara Karakas."""

    jd_ut: float
    sunrise_jd_ut: float
    elapsed_hours_since_sunrise: float
    elapsed_ghatis_since_sunrise: float
    special_lagnas: tuple[SpecialLagnaEntry, ...]
    yogi_avayogi: YogiAvayogiReport
    arudha_padas: tuple[ArudhaPadaEntry, ...]
    chara_karakas_7: tuple[CharaKarakaEntry, ...]
    chara_karakas_8: tuple[CharaKarakaEntry, ...]
    receipt: Mapping[str, Any]
    receipt_sha256: str

    @property
    def udaya_lagna(self) -> SpecialLagnaEntry:
        return self.special_lagnas[0]

    @property
    def hora_lagna(self) -> SpecialLagnaEntry:
        return self.special_lagnas[1]

    @property
    def ghati_lagna(self) -> SpecialLagnaEntry:
        return self.special_lagnas[2]

    @property
    def bhava_lagna(self) -> SpecialLagnaEntry:
        return self.special_lagnas[3]

    @property
    def sree_lagna(self) -> SpecialLagnaEntry:
        return self.special_lagnas[4]

    @property
    def indu_lagna(self) -> SpecialLagnaEntry:
        return self.special_lagnas[5]

    @property
    def pranapada_lagna(self) -> SpecialLagnaEntry:
        return self.special_lagnas[6]

    @property
    def varnada_lagna(self) -> SpecialLagnaEntry:
        return self.special_lagnas[7]

    @property
    def yogi_point_deg(self) -> float:
        return self.yogi_avayogi.yogi_point_deg

    @property
    def yogi_point_dms(self) -> str:
        return self.yogi_avayogi.yogi_point_dms

    @property
    def yogi_nakshatra_name(self) -> str:
        return self.yogi_avayogi.yogi_nakshatra_name

    @property
    def yogi_planet(self) -> str:
        return self.yogi_avayogi.yogi_planet

    @property
    def sahayogi_planet(self) -> str:
        return self.yogi_avayogi.sahayogi_planet

    @property
    def avayogi_point_deg(self) -> float:
        return self.yogi_avayogi.avayogi_point_deg

    @property
    def avayogi_point_dms(self) -> str:
        return self.yogi_avayogi.avayogi_point_dms

    @property
    def avayogi_nakshatra_name(self) -> str:
        return self.yogi_avayogi.avayogi_nakshatra_name

    @property
    def avayogi_planet(self) -> str:
        return self.yogi_avayogi.avayogi_planet


@dataclass(frozen=True)
class FullAstronomicalBodyEphemeris:
    """Complete 6-coordinate spherical, equatorial, ecliptic, physical, and Jyotish ephemeris row for a body."""

    body: str
    sidereal_longitude_deg: float
    tropical_longitude_deg: float
    sidereal_dms: str
    tropical_dms: str
    rashi_index: int
    rashi_name: str
    rashi_lord: str
    ecliptic_latitude_deg: float
    ecliptic_latitude_dms: str
    right_ascension_deg: float
    right_ascension_hms: str
    declination_deg: float
    declination_dms: str
    distance_au: float
    distance_km: float
    longitude_speed_deg_per_day: float
    daily_motion_dms: str
    second_difference_arcsec_per_day2: float
    latitude_speed_deg_per_day: float
    declination_speed_deg_per_day: float
    radial_velocity_au_per_day: float
    horizontal_parallax_arcsec: float
    apparent_semidiameter_arcsec: float
    apparent_diameter_arcsec: float
    solar_elongation_deg: float
    phase_angle_deg: float
    illuminated_fraction_pct: float
    visual_magnitude: float
    nakshatra_name: str
    nakshatra_lord: str
    pada: int
    kp_sign_lord: str
    kp_star_lord: str
    kp_sub_lord: str
    kp_sub_sub_lord: str
    kp_sub_number_249: int
    d9_navamsa_sign: str
    d10_dasamsa_sign: str
    d60_shashtiamsa_sign: str
    is_retrograde: bool
    is_stationary: bool
    is_combust: bool
    is_vargottama: bool
    is_pushkara_navamsa: bool
    is_pushkara_bhaga: bool
    is_mrityu_bhaga: bool
    status_flags: str


def _make_special_lagna_entry(key: str, name: str, lon_deg: float, formula: str) -> SpecialLagnaEntry:
    lon = normalize_degrees(lon_deg)
    rashi_idx = int(lon // 30.0) % 12
    rashi_name = RASHI_NAMES[rashi_idx]
    nak = nakshatra_position(lon)
    d9_sign = varga_sign(lon, "D9").sign_name
    return SpecialLagnaEntry(
        key=key,
        sanskrit_name=name,
        longitude_deg=lon,
        classical_dms=_format_rashi_dms(lon),
        rashi_index=rashi_idx,
        rashi_name=rashi_name,
        rashi_lord=RASI_LORDS[rashi_idx],
        nakshatra_name=nak.name,
        pada=nak.pada,
        d9_navamsa_sign=d9_sign,
        formula_summary=formula,
    )


def compute_vishesha_lagnas_and_special_points(
    jd_ut: float,
    latitude_deg: float,
    longitude_deg: float,
    *,
    sunrise_jd_ut: float | None = None,
    ayanamsa: str = "lahiri",
    adapter: EphemerisAdapter | None = None,
) -> VisheshaLagnaAndSpecialPointsReport:
    """Compute all 8 Special Lagnas (Udaya, Hora, Ghati, Bhava, Sree, Indu, Pranapada, Varnada),
    Yogi/Sahayogi/Avayogi points, 12 Jaimini Arudha Padas (AL..UL), and 7/8 Chara Karakas.
    """
    if adapter is None:
        from ..adapter import EphemerisAdapter as _EphemerisAdapter
        ad = _EphemerisAdapter()
    else:
        ad = adapter
    houses = ad.houses_ut(jd_ut, latitude_deg, longitude_deg, system="placidus", ayanamsa=ayanamsa)
    udaya_lagna_deg = normalize_degrees(houses.ascendant_deg)

    if sunrise_jd_ut is None:
        # Approximate local sunrise on the active solar day
        local_solar_jd = jd_ut + (longitude_deg / 360.0)
        sr_approx = math.floor(local_solar_jd - 0.5) + 0.5 + (6.0 / 24.0) - (longitude_deg / 360.0)
        if sr_approx > jd_ut:
            sr_approx -= 1.0
        sunrise_jd_ut = sr_approx

    sun_birth = ad.calc_ut(jd_ut, "sun", sidereal=True, ayanamsa=ayanamsa).longitude_deg % 360.0
    moon_birth = ad.calc_ut(jd_ut, "moon", sidereal=True, ayanamsa=ayanamsa).longitude_deg % 360.0
    sun_sunrise = ad.calc_ut(sunrise_jd_ut, "sun", sidereal=True, ayanamsa=ayanamsa).longitude_deg % 360.0

    elapsed_days = max(0.0, jd_ut - sunrise_jd_ut)
    elapsed_hours = elapsed_days * 24.0
    elapsed_minutes = elapsed_hours * 60.0
    elapsed_ghatis = elapsed_days * 60.0  # 1 day = 60 Ghatis
    elapsed_palas = elapsed_ghatis * 60.0  # 1 Ghati = 60 Palas (Vinadis)

    # 1. Udaya Lagna (Ascendant)
    ul_entry = _make_special_lagna_entry(
        "udaya_lagna",
        "Udaya Lagna (Birth Ascendant)",
        udaya_lagna_deg,
        "Eastern horizon intersection with the sidereal ecliptic at birth",
    )

    # 2. Hora Lagna (HL): Sun at sunrise + (elapsed_minutes / 2.0) degrees (= 1 sign per Hora / hour = 2.5 Ghatis)
    hora_lagna_deg = normalize_degrees(sun_sunrise + (elapsed_minutes / 2.0))
    hl_entry = _make_special_lagna_entry(
        "hora_lagna",
        "Hora Lagna (HL — Sustenance & Wealth)",
        hora_lagna_deg,
        "Sun at Sunrise + (Elapsed Minutes since Sunrise / 2.0)",
    )

    # 3. Ghati Lagna (GL): Sun at sunrise + (elapsed_ghatis * 30 deg) (= 1 sign per Ghati = 1.25 deg/min)
    ghati_lagna_deg = normalize_degrees(sun_sunrise + (elapsed_ghatis * 30.0))
    gl_entry = _make_special_lagna_entry(
        "ghati_lagna",
        "Ghati Lagna (GL — Power, Rank & Authority)",
        ghati_lagna_deg,
        "Sun at Sunrise + (Elapsed Ghatis since Sunrise × 30°)",
    )

    # 4. Bhava Lagna (BL): Sun at sunrise + (elapsed_ghatis * 6 deg) (= 1 sign per 5 Ghatis / 2 hours)
    bhava_lagna_deg = normalize_degrees(sun_sunrise + (elapsed_ghatis * 6.0))
    bl_entry = _make_special_lagna_entry(
        "bhava_lagna",
        "Bhava Lagna (BL — Disposition & Vitality)",
        bhava_lagna_deg,
        "Sun at Sunrise + (Elapsed Ghatis since Sunrise × 6°)",
    )

    # 5. Sree Lagna (SL): Natal Udaya Lagna + (Moon's traversed fraction in its Nakshatra × 360°)
    moon_nak = nakshatra_position(moon_birth)
    moon_nak_frac = moon_nak.degree_in_nakshatra / (360.0 / 27.0)
    sree_lagna_deg = normalize_degrees(udaya_lagna_deg + moon_nak_frac * 360.0)
    sl_entry = _make_special_lagna_entry(
        "sree_lagna",
        "Sree Lagna (SL — Lakshmi Prosperity & Grace)",
        sree_lagna_deg,
        "Udaya Lagna + (Moon's Traversed Nakshatra Fraction × 360°)",
    )

    # 6. Indu Lagna (IL): 9th lord from Lagna + 9th lord from Moon -> sum Kalas % 12 counted from Moon
    lagna_sign_idx = int(udaya_lagna_deg // 30.0) % 12
    moon_sign_idx = int(moon_birth // 30.0) % 12
    ninth_from_lagna_lord = RASI_LORDS[(lagna_sign_idx + 8) % 12]
    ninth_from_moon_lord = RASI_LORDS[(moon_sign_idx + 8) % 12]
    kala_sum = INDU_LAGNA_KALA_VALUES[ninth_from_lagna_lord] + INDU_LAGNA_KALA_VALUES[ninth_from_moon_lord]
    indu_offset_signs = kala_sum % 12
    if indu_offset_signs == 0:
        indu_offset_signs = 12
    indu_sign_idx = (moon_sign_idx + indu_offset_signs - 1) % 12
    indu_lagna_deg = indu_sign_idx * 30.0 + (moon_birth % 30.0)
    il_entry = _make_special_lagna_entry(
        "indu_lagna",
        "Indu Lagna (IL — Kalidasa Wealth & Dhana Yoga Point)",
        indu_lagna_deg,
        f"9th Lord from Lagna ({ninth_from_lagna_lord}={INDU_LAGNA_KALA_VALUES[ninth_from_lagna_lord]}) + "
        f"9th Lord from Moon ({ninth_from_moon_lord}={INDU_LAGNA_KALA_VALUES[ninth_from_moon_lord]}) = "
        f"{kala_sum} Kalas -> {indu_offset_signs}th sign from Moon",
    )

    # 7. Pranapada Lagna (PL): BPHS Ch. 5 — Palas since sunrise / 15 = signs (* 30° = 2° per Pala) added to Sun (Movable: +0°, Fixed: +240°, Dual: +120°)
    sun_sign_idx = int(sun_birth // 30.0) % 12
    sun_modality = sun_sign_idx % 3  # 0=Movable (Chara), 1=Fixed (Sthira), 2=Dual (Dwiswabhava)
    modality_offset_deg = 0.0 if sun_modality == 0 else (240.0 if sun_modality == 1 else 120.0)
    pranapada_deg = normalize_degrees(sun_birth + modality_offset_deg + (elapsed_palas * 2.0))
    pl_entry = _make_special_lagna_entry(
        "pranapada_lagna",
        "Pranapada Lagna (PL — Vital Breath & Rectification Anchor)",
        pranapada_deg,
        "Sun at Birth + Modality Offset (Movable +0°, Fixed +240°, Dual +120°) + ((Elapsed Palas / 15) × 30°)",
    )

    # 8. Varnada Lagna (VL): BPHS Ch. 5 — Odd/Even counting of Udaya Lagna and Hora Lagna
    hl_sign_idx = int(hora_lagna_deg // 30.0) % 12
    lagna_is_odd = (lagna_sign_idx % 2) == 0  # 0=Mesha (1st sign, odd)
    hl_is_odd = (hl_sign_idx % 2) == 0
    count_lagna = (lagna_sign_idx + 1) if lagna_is_odd else (12 - lagna_sign_idx)
    count_hl = (hl_sign_idx + 1) if hl_is_odd else (12 - hl_sign_idx)
    if lagna_is_odd == hl_is_odd:
        vl_count = count_lagna + count_hl
    else:
        vl_count = abs(count_lagna - count_hl)
    if vl_count == 0:
        vl_count = 12
    vl_sign_idx = ((vl_count - 1) % 12) if lagna_is_odd else ((12 - vl_count) % 12)
    varnada_deg = vl_sign_idx * 30.0 + (udaya_lagna_deg % 30.0)
    vl_entry = _make_special_lagna_entry(
        "varnada_lagna",
        "Varnada Lagna (VL — Social Standing & Vocational Destiny)",
        varnada_deg,
        "Parashari Odd-Direct / Even-Reverse synthesis of Udaya Lagna and Hora Lagna",
    )

    # Yogi, Sahayogi, and Avayogi calculation
    yogi_deg = normalize_degrees(sun_birth + moon_birth + (93.0 + 20.0 / 60.0))
    yogi_nak = nakshatra_position(yogi_deg)
    yogi_rashi_idx = int(yogi_deg // 30.0) % 12
    sahayogi_planet = RASI_LORDS[yogi_rashi_idx]
    avayogi_deg = normalize_degrees(yogi_deg + (186.0 + 40.0 / 60.0))
    avayogi_nak = nakshatra_position(avayogi_deg)
    avayogi_rashi_idx = int(avayogi_deg // 30.0) % 12

    yogi_report = YogiAvayogiReport(
        yogi_point_deg=yogi_deg,
        yogi_point_dms=_format_rashi_dms(yogi_deg),
        yogi_rashi_name=RASHI_NAMES[yogi_rashi_idx],
        yogi_nakshatra_name=yogi_nak.name,
        yogi_pada=yogi_nak.pada,
        yogi_planet=yogi_nak.vimshottari_ruler,
        sahayogi_planet=sahayogi_planet,
        avayogi_point_deg=avayogi_deg,
        avayogi_point_dms=_format_rashi_dms(avayogi_deg),
        avayogi_rashi_name=RASHI_NAMES[avayogi_rashi_idx],
        avayogi_nakshatra_name=avayogi_nak.name,
        avayogi_pada=avayogi_nak.pada,
        avayogi_planet=avayogi_nak.vimshottari_ruler,
    )

    # Planetary longitudes for Arudha Padas & Chara Karakas
    planet_lons: dict[str, float] = {
        "Sun": sun_birth,
        "Moon": moon_birth,
    }
    for p_key, p_cap in (
        ("mars", "Mars"),
        ("mercury", "Mercury"),
        ("jupiter", "Jupiter"),
        ("venus", "Venus"),
        ("saturn", "Saturn"),
        ("rahu", "Rahu"),
    ):
        planet_lons[p_cap] = ad.calc_ut(jd_ut, p_key, sidereal=True, ayanamsa=ayanamsa).longitude_deg % 360.0

    # 12 Arudha Padas (A1..A12) with Jaimini Swastha Dasha 1st/7th house exception
    arudha_list: list[ArudhaPadaEntry] = []
    for h_idx in range(12):
        code, title = ARUDHA_HOUSE_NAMES[h_idx]
        base_sign = (lagna_sign_idx + h_idx) % 12
        lord = RASI_LORDS[base_sign]
        lord_lon = planet_lons[lord]
        lord_sign = int(lord_lon // 30.0) % 12
        dist = (lord_sign - base_sign) % 12  # 0 means 1st from house, 6 means 7th from house
        raw_arudha = (lord_sign + dist) % 12
        swastha = ((raw_arudha - base_sign) % 12) in (0, 6)
        final_arudha = (raw_arudha + 9) % 12 if swastha else raw_arudha
        arudha_list.append(
            ArudhaPadaEntry(
                house_number=h_idx + 1,
                code=code,
                title=title,
                base_sign_index=base_sign,
                base_sign_name=RASHI_NAMES[base_sign],
                lord_planet=lord,
                lord_sign_index=lord_sign,
                lord_sign_name=RASHI_NAMES[lord_sign],
                raw_distance_signs=dist + 1,
                swastha_exception_applied=swastha,
                arudha_sign_index=final_arudha,
                arudha_sign_name=RASHI_NAMES[final_arudha],
                arudha_sign_lord=RASI_LORDS[final_arudha],
            )
        )

    # 7-Planet Chara Karakas (Sun..Saturn)
    seven_candidates = []
    for p_name in ("Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn"):
        p_lon = planet_lons[p_name]
        deg_in_s = p_lon % 30.0
        seven_candidates.append((deg_in_s, p_name, p_lon, deg_in_s))
    seven_candidates.sort(key=lambda x: x[0], reverse=True)

    ck_7: list[CharaKarakaEntry] = []
    for idx, (eff_deg, p_name, p_lon, deg_in_s) in enumerate(seven_candidates):
        code, title = CHARA_KARAKA_7_TITLES[idx]
        ck_7.append(
            CharaKarakaEntry(
                code=code,
                title=title,
                planet=p_name,
                longitude_deg=p_lon,
                degree_in_sign=deg_in_s,
                effective_karaka_degree=eff_deg,
                classical_dms=_format_rashi_dms(p_lon),
                rashi_name=RASHI_NAMES[int(p_lon // 30.0) % 12],
                karakamsa_d9_sign=varga_sign(p_lon, "D9").sign_name,
            )
        )

    # 8-Planet Chara Karakas (Sun..Saturn + Rahu measured from 30° - deg_in_sign)
    eight_candidates = list(seven_candidates)
    rahu_lon = planet_lons["Rahu"]
    rahu_deg_in_s = rahu_lon % 30.0
    rahu_eff = 30.0 - rahu_deg_in_s
    eight_candidates.append((rahu_eff, "Rahu", rahu_lon, rahu_deg_in_s))
    eight_candidates.sort(key=lambda x: x[0], reverse=True)

    ck_8: list[CharaKarakaEntry] = []
    for idx, (eff_deg, p_name, p_lon, deg_in_s) in enumerate(eight_candidates):
        code, title = CHARA_KARAKA_8_TITLES[idx]
        ck_8.append(
            CharaKarakaEntry(
                code=code,
                title=title,
                planet=p_name,
                longitude_deg=p_lon,
                degree_in_sign=deg_in_s,
                effective_karaka_degree=eff_deg,
                classical_dms=_format_rashi_dms(p_lon),
                rashi_name=RASHI_NAMES[int(p_lon // 30.0) % 12],
                karakamsa_d9_sign=varga_sign(p_lon, "D9").sign_name,
            )
        )

    special_lagnas = (ul_entry, hl_entry, gl_entry, bl_entry, sl_entry, il_entry, pl_entry, vl_entry)
    receipt_payload = {
        "engine": "ephemeris_oss.jyotish.vishesha_lagnas",
        "version": __version__,
        "jd_ut": round(jd_ut, 8),
        "udaya_lagna_deg": round(udaya_lagna_deg, 6),
        "hora_lagna_deg": round(hora_lagna_deg, 6),
        "ghati_lagna_deg": round(ghati_lagna_deg, 6),
        "sree_lagna_deg": round(sree_lagna_deg, 6),
        "indu_lagna_deg": round(indu_lagna_deg, 6),
        "pranapada_lagna_deg": round(pranapada_deg, 6),
        "yogi_planet": yogi_report.yogi_planet,
        "atmakaraka": ck_7[0].planet,
    }
    receipt_sha256 = canonical_hash(receipt_payload)

    return VisheshaLagnaAndSpecialPointsReport(
        jd_ut=jd_ut,
        sunrise_jd_ut=sunrise_jd_ut,
        elapsed_hours_since_sunrise=elapsed_hours,
        elapsed_ghatis_since_sunrise=elapsed_ghatis,
        special_lagnas=special_lagnas,
        yogi_avayogi=yogi_report,
        arudha_padas=tuple(arudha_list),
        chara_karakas_7=tuple(ck_7),
        chara_karakas_8=tuple(ck_8),
        receipt=receipt_payload,
        receipt_sha256=receipt_sha256,
    )


def _ecliptic_to_equatorial(lon_trop_deg: float, lat_deg: float, eps_deg: float = 23.4392911) -> tuple[float, float]:
    """Convert tropical ecliptic (longitude, latitude) to equatorial (RA, Dec) in degrees."""
    lam = math.radians(lon_trop_deg)
    beta = math.radians(lat_deg)
    eps = math.radians(eps_deg)
    sin_dec = math.sin(beta) * math.cos(eps) + math.cos(beta) * math.sin(eps) * math.sin(lam)
    dec_rad = math.asin(max(-1.0, min(1.0, sin_dec)))
    y = math.sin(lam) * math.cos(eps) - math.tan(beta) * math.sin(eps)
    x = math.cos(lam)
    ra_rad = math.atan2(y, x)
    return (math.degrees(ra_rad) % 360.0), math.degrees(dec_rad)


def _estimate_visual_magnitude(body: str, dist_au: float, helio_r_au: float, phase_angle_deg: float) -> float:
    """Compute physical visual magnitude V_mag using Mallama & Hilton (2018) / Astronomical Almanac formulas."""
    b = body.lower()
    if b == "sun":
        return -26.74
    if b == "moon":
        return -12.73 + 0.026 * abs(phase_angle_deg) + 4.0e-9 * (abs(phase_angle_deg) ** 4)
    if b in ("rahu", "true_rahu", "ketu", "true_ketu", "mean_node", "true_node"):
        return 99.0
    r_d = max(1e-6, dist_au * helio_r_au)
    five_log = 5.0 * math.log10(r_d)
    ph = abs(phase_angle_deg)
    if b == "mercury":
        return -0.613 + five_log + 0.06328 * ph - 0.0016336 * (ph ** 2) + 0.000033644 * (ph ** 3)
    if b == "venus":
        return -4.384 + five_log + 0.001044 * ph + 0.0003687 * (ph ** 2)
    if b == "mars":
        return -1.601 + five_log + 0.02267 * ph
    if b == "jupiter":
        return -9.395 + five_log + 0.005 * ph
    if b == "saturn":
        return -8.914 + five_log + 0.026 * ph
    if b == "uranus":
        return -7.110 + five_log
    if b == "neptune":
        return -7.000 + five_log
    if b == "pluto":
        return -1.01 + five_log
    return 0.0


def compute_full_astronomical_sky_ephemeris(
    jd_ut: float,
    *,
    ayanamsa: str = "lahiri",
    physical_center: bool = False,
    adapter: EphemerisAdapter | None = None,
) -> Mapping[str, FullAstronomicalBodyEphemeris]:
    """Compute the full 6-coordinate spherical, equatorial, ecliptic, physical, and Jyotish
    ephemeris for all 13 bodies at ``jd_ut``.
    """
    if adapter is None:
        from ..adapter import EphemerisAdapter as _EphemerisAdapter
        ad = _EphemerisAdapter()
    else:
        ad = adapter
    ay_deg = ad.get_ayanamsa_ut(jd_ut, mode=ayanamsa)

    # Mean obliquity of the ecliptic at date (Meeus Ch. 22)
    t_cent = (jd_ut - 2451545.0) / 36525.0
    eps_deg = 23.43929111 - (46.8150 * t_cent + 0.00059 * (t_cent ** 2) - 0.001813 * (t_cent ** 3)) / 3600.0

    sun_sid = ad.calc_ut(jd_ut, "sun", sidereal=True, ayanamsa=ayanamsa)
    sun_lon_sid = sun_sid.longitude_deg % 360.0
    sun_dist_au = max(0.001, sun_sid.distance_au)

    bodies = (
        ("sun", "Sun"),
        ("moon", "Moon"),
        ("mars", "Mars"),
        ("mercury", "Mercury"),
        ("jupiter", "Jupiter"),
        ("venus", "Venus"),
        ("saturn", "Saturn"),
        ("rahu", "Rahu"),
        ("true_rahu", "True_Rahu"),
        ("ketu", "Ketu"),
        ("uranus", "Uranus"),
        ("neptune", "Neptune"),
        ("pluto", "Pluto"),
    )

    results: dict[str, FullAstronomicalBodyEphemeris] = {}
    for b_query, b_label in bodies:
        pos_sid = ad.calc_ut(
            jd_ut,
            b_query,
            sidereal=True,
            ayanamsa=ayanamsa,
            physical_center=(physical_center and b_query in ("mars", "jupiter", "saturn")),
        )
        lon_sid = pos_sid.longitude_deg % 360.0
        lon_trop = (lon_sid + ay_deg) % 360.0
        lat_deg = pos_sid.latitude_deg
        dist_au = max(1e-6, pos_sid.distance_au)
        spd_lon = pos_sid.longitude_speed_deg_per_day
        spd_lat = pos_sid.latitude_speed_deg_per_day
        spd_dist = pos_sid.distance_speed_au_per_day

        # Equatorial RA and Dec + Declination/Latitude/Radial daily speeds via +/- 1.0 day probe
        ra_deg, dec_deg = _ecliptic_to_equatorial(lon_trop, lat_deg, eps_deg)
        use_phys = physical_center and b_query in ("mars", "jupiter", "saturn")
        try:
            pos_m1 = ad.calc_ut(jd_ut - 1.0, b_query, sidereal=True, ayanamsa=ayanamsa, physical_center=use_phys)
            pos_p1 = ad.calc_ut(jd_ut + 1.0, b_query, sidereal=True, ayanamsa=ayanamsa, physical_center=use_phys)
            _, dec_m1 = _ecliptic_to_equatorial((pos_m1.longitude_deg + ay_deg) % 360.0, pos_m1.latitude_deg, eps_deg)
            _, dec_p1 = _ecliptic_to_equatorial((pos_p1.longitude_deg + ay_deg) % 360.0, pos_p1.latitude_deg, eps_deg)
            dec_speed = 0.5 * (dec_p1 - dec_m1)
            if spd_lat == 0.0:
                spd_lat = 0.5 * (pos_p1.latitude_deg - pos_m1.latitude_deg)
            if spd_dist == 0.0:
                spd_dist = 0.5 * (pos_p1.distance_au - pos_m1.distance_au)
            # Second-order tabular difference Delta^2 = L(+1) - 2*L(0) + L(-1) in arcseconds
            d_plus = ((pos_p1.longitude_deg - lon_sid + 180.0) % 360.0) - 180.0
            d_minus = ((lon_sid - pos_m1.longitude_deg + 180.0) % 360.0) - 180.0
            second_diff_arcsec = (d_plus - d_minus) * 3600.0
        except Exception:
            dec_speed = 0.0
            second_diff_arcsec = 0.0

        dist_km = dist_au * AU_IN_KM
        if b_query in ("rahu", "true_rahu", "ketu"):
            hp_arcsec = 0.0
            sd_arcsec = 0.0
            elong_deg = abs(((lon_sid - sun_lon_sid + 180.0) % 360.0) - 180.0)
            phase_ang = 0.0
            illum_pct = 0.0
            v_mag = 99.0
        else:
            sin_hp = min(1.0, EARTH_EQUATORIAL_RADIUS_KM / max(EARTH_EQUATORIAL_RADIUS_KM + 1.0, dist_km))
            hp_arcsec = math.degrees(math.asin(sin_hp)) * 3600.0
            r_body_km = BODY_EQUATORIAL_RADIUS_KM.get(b_query, 1000.0)
            sd_arcsec = math.degrees(math.asin(min(1.0, r_body_km / max(r_body_km + 1.0, dist_km)))) * 3600.0
            elong_deg = abs(((lon_sid - sun_lon_sid + 180.0) % 360.0) - 180.0)
            if b_query == "sun":
                phase_ang = 0.0
                illum_pct = 100.0
                helio_r = 1.0
            elif b_query == "moon":
                phase_ang = 180.0 - elong_deg
                illum_pct = 50.0 * (1.0 + math.cos(math.radians(phase_ang)))
                helio_r = sun_dist_au
            else:
                # Law of cosines for heliocentric distance r
                cos_e = math.cos(math.radians(elong_deg))
                helio_r = math.sqrt(max(0.01, dist_au ** 2 + sun_dist_au ** 2 - 2.0 * dist_au * sun_dist_au * cos_e))
                cos_i = (helio_r ** 2 + dist_au ** 2 - sun_dist_au ** 2) / max(1e-6, 2.0 * helio_r * dist_au)
                phase_ang = math.degrees(math.acos(max(-1.0, min(1.0, cos_i))))
                illum_pct = 50.0 * (1.0 + math.cos(math.radians(phase_ang)))
            v_mag = _estimate_visual_magnitude(b_query, dist_au, helio_r, phase_ang)

        rashi_idx = int(lon_sid // 30.0) % 12
        rashi_name = RASHI_NAMES[rashi_idx]
        nak = nakshatra_position(lon_sid)
        kp_lords = kp_coordinate_lords(lon_sid)
        d9_place = varga_sign(lon_sid, "D9")
        d10_place = varga_sign(lon_sid, "D10")
        d60_place = varga_sign(lon_sid, "D60")

        is_retro = spd_lon < 0.0
        is_stat = abs(spd_lon) < 0.005 and b_query not in ("sun", "moon")
        is_combust = False
        comb_orbs = {"moon": (12.0, 12.0), "mars": (17.0, 17.0), "mercury": (14.0, 12.0), "jupiter": (11.0, 11.0), "venus": (10.0, 8.0), "saturn": (15.0, 15.0)}
        if b_query in comb_orbs:
            orb = comb_orbs[b_query][1] if is_retro else comb_orbs[b_query][0]
            is_combust = elong_deg <= orb

        is_vargottama = (d9_place.sign_index == rashi_idx)
        is_pushkara_nav = d9_place.sign_index in PUSHKARA_NAVAMSA_RASHI_INDICES.get(rashi_idx, ())
        deg_in_sign = lon_sid % 30.0
        is_pushkara_bhaga = abs(deg_in_sign - PUSHKARA_BHAGA_DEGREES[rashi_idx]) <= 0.5

        mb_key = "rahu" if b_query == "true_rahu" else b_query.lower()
        is_mrityu = False
        if mb_key in MRITYU_BHAGA_DEGREE_TABLE:
            mb_deg = float(MRITYU_BHAGA_DEGREE_TABLE[mb_key][rashi_idx])
            is_mrityu = abs(deg_in_sign - mb_deg) <= 0.5

        flags: list[str] = []
        if is_stat:
            flags.append("S")
        elif is_retro:
            flags.append("R")
        else:
            flags.append("D")
        if is_combust:
            flags.append("C")
        if is_vargottama:
            flags.append("V")
        if is_pushkara_nav:
            flags.append("PN")
        if is_mrityu:
            flags.append("MB")

        results[b_query] = FullAstronomicalBodyEphemeris(
            body=b_query,
            sidereal_longitude_deg=lon_sid,
            tropical_longitude_deg=lon_trop,
            sidereal_dms=_format_rashi_dms(lon_sid),
            tropical_dms=_format_rashi_dms(lon_trop),
            rashi_index=rashi_idx,
            rashi_name=rashi_name,
            rashi_lord=RASI_LORDS[rashi_idx],
            ecliptic_latitude_deg=lat_deg,
            ecliptic_latitude_dms=_format_signed_dms(lat_deg),
            right_ascension_deg=ra_deg,
            right_ascension_hms=_format_ra_hms(ra_deg),
            declination_deg=dec_deg,
            declination_dms=_format_signed_dms(dec_deg),
            distance_au=round(dist_au, 7),
            distance_km=round(dist_km, 1),
            longitude_speed_deg_per_day=spd_lon,
            daily_motion_dms=_format_signed_dms(spd_lon),
            second_difference_arcsec_per_day2=round(second_diff_arcsec, 2),
            latitude_speed_deg_per_day=spd_lat,
            declination_speed_deg_per_day=dec_speed,
            radial_velocity_au_per_day=spd_dist,
            horizontal_parallax_arcsec=round(hp_arcsec, 2),
            apparent_semidiameter_arcsec=round(sd_arcsec, 2),
            apparent_diameter_arcsec=round(2.0 * sd_arcsec, 2),
            solar_elongation_deg=round(elong_deg, 4),
            phase_angle_deg=round(phase_ang, 2),
            illuminated_fraction_pct=round(illum_pct, 2),
            visual_magnitude=round(v_mag, 2),
            nakshatra_name=nak.name,
            nakshatra_lord=nak.vimshottari_ruler,
            pada=nak.pada,
            kp_sign_lord=kp_lords.sign_lord,
            kp_star_lord=kp_lords.star_lord,
            kp_sub_lord=kp_lords.sub_lord,
            kp_sub_sub_lord=kp_lords.sub_sub_lord,
            kp_sub_number_249=kp_lords.horary_number_249,
            d9_navamsa_sign=d9_place.sign_name,
            d10_dasamsa_sign=d10_place.sign_name,
            d60_shashtiamsa_sign=d60_place.sign_name,
            is_retrograde=is_retro,
            is_stationary=is_stat,
            is_combust=is_combust,
            is_vargottama=is_vargottama,
            is_pushkara_navamsa=is_pushkara_nav,
            is_pushkara_bhaga=is_pushkara_bhaga,
            is_mrityu_bhaga=is_mrityu,
            status_flags="/".join(flags),
        )

    return results


__all__ = [
    "ARUDHA_HOUSE_NAMES",
    "ArudhaPadaEntry",
    "BODY_EQUATORIAL_RADIUS_KM",
    "CHARA_KARAKA_7_TITLES",
    "CHARA_KARAKA_8_TITLES",
    "CharaKarakaEntry",
    "FullAstronomicalBodyEphemeris",
    "INDU_LAGNA_KALA_VALUES",
    "PUSHKARA_BHAGA_DEGREES",
    "PUSHKARA_NAVAMSA_RASHI_INDICES",
    "SpecialLagnaEntry",
    "VisheshaLagnaAndSpecialPointsReport",
    "YogiAvayogiReport",
    "compute_full_astronomical_sky_ephemeris",
    "compute_vishesha_lagnas_and_special_points",
]
