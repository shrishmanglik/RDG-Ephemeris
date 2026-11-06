"""Clean-room Vedic Jyotish mathematical suite with deterministic SHA-256 receipts.

Provides complete Parashari and Jaimini mathematical engines:
- 27-Nakshatra, 108-Pada, Tara Bala, and 28-Nakshatra (Abhijit) geometry (`nakshatra`)
- 16 Parashari Shodashvarga (D1-D60), higher harmonics (D5-D144), Vimshopaka Bala,
  Special Lagnas, and Jaimini Arudha Padas (`vargas`)
- Five-Limb Vedic Almanac (Panchanga), Samvatsara, Ritu, 24-Hora, and Muhurtas (`panchanga`)
- 5-Level Multi-Dasha Solver (Vimshottari, Ashtottari, Yogini, Jaimini Chara) and
  Chara Karakas (`dasha`)
- Six-Fold Planetary Strength (Shadbala), Ishta/Kashta Phala, and Bhava Bala (`shadbala`)
- Bhinna Ashtakavarga, 337-bindu Sarvashtakavarga, Trikona/Ekadhipatya Shodhana,
  Rasi/Graha/Shodhya Pindas, and Gochara Transit Vedha (`ashtakavarga`)
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Mapping

from .._version import __version__
from ..engine.receipt import canonical_hash
from .ashtakavarga import (
    ASHTAKAVARGA_CONTRIBUTORS,
    BAV_BENEFIC_HOUSES,
    DUAL_OWNERSHIP_PAIRS,
    EXPECTED_BAV_TOTALS,
    EXPECTED_SAV_TOTAL,
    GOCHARA_VEDHA_TABLE,
    GRAHA_GUNAKARAS,
    RASI_GUNAKARAS,
    VEDHA_EXEMPT_PAIRS,
    AshtakavargaAnalysis,
    BhinnaAshtakavargaTable,
    GocharaPlanetTransit,
    compute_ashtakavarga,
    compute_pindas,
    ekadhipatya_shodhana,
    evaluate_gochara_vedha,
    trikona_shodhana,
)
from .dasha import (
    ASHTOTTARI_RULERS,
    ASHTOTTARI_TOTAL_YEARS,
    ASHTOTTARI_YEARS,
    KALACHAKRA_APASAVYA_SEQUENCES,
    KALACHAKRA_SAVYA_NAKSHATRAS,
    KALACHAKRA_SAVYA_SEQUENCES,
    KALACHAKRA_SIGN_YEARS,
    KARAKA_7_ROLES,
    KARAKA_8_ROLES,
    LEVEL_NAMES,
    SAVANA_YEAR_DAYS,
    SAVYA_SIGNS,
    SOLAR_YEAR_DAYS,
    VIMSHOTTARI_TOTAL_YEARS,
    VIMSHOTTARI_YEARS,
    YOGINI_CATALOG,
    YOGINI_LORDS,
    YOGINI_NAMES,
    YOGINI_TOTAL_YEARS,
    YOGINI_YEARS,
    CharaKarakaEntry,
    DashaPeriod,
    DashaTimeline,
    KalachakraDashaPeriod,
    KalachakraDashaTimeline,
    classify_kalachakra_gati,
    compute_ashtottari_dasha,
    compute_chara_dasha,
    compute_chara_karakas,
    compute_kalachakra_dasha,
    compute_vimshottari_dasha,
    compute_yogini_dasha,
    jd_to_iso_utc,
    resolve_dasha_5_levels,
)
from .nakshatra import (
    ABHIJIT_END_DEG,
    ABHIJIT_SPAN_DEG,
    ABHIJIT_START_DEG,
    NAKSHATRA_CATALOG,
    NAKSHATRA_NAMES,
    NAKSHATRA_SPAN_DEG,
    PADA_SPAN_DEG,
    RASI_NAMES,
    TARA_BENEFIC,
    TARA_NAMES,
    VIMSHOTTARI_RULERS,
    AbhijitPosition,
    NakshatraMetadata,
    NakshatraPosition,
    TaraBalaResult,
    abhijit_position,
    compute_tara_bala,
    nakshatra_position,
    normalize_degrees,
)
from .panchanga import (
    DURMUHURTA_DAY_INDICES,
    FIXED_KARANAS,
    GULIKA_KALAM_SEGMENT,
    HORA_CHALDEAN_ORDER,
    KARANA_SPAN_DEG,
    MOVABLE_KARANAS,
    PAKSHA_TITHI_NAMES,
    RAHU_KALAM_SEGMENT,
    RITU_CATALOG,
    SAMVATSARA_NAMES,
    TITHI_EIGHT_LORDS,
    TITHI_GROUPS,
    TITHI_SPAN_DEG,
    VARA_CATALOG,
    YAMAGANDAM_SEGMENT,
    YOGA_CATALOG,
    YOGA_SPAN_DEG,
    HoraWindow,
    KaranaInfo,
    MuhurtaWindows,
    PanchangaSummary,
    SamvatsaraInfo,
    TimeWindow,
    TithiInfo,
    VaraInfo,
    YogaInfo,
    compute_ayana_and_ritu,
    compute_hora_table,
    compute_karana,
    compute_muhurta_windows,
    compute_panchanga,
    compute_samvatsara,
    compute_tithi,
    compute_vara,
    compute_yoga,
)
from .shadbala import (
    DEEP_EXALTATION_DEG,
    DISC_DIAMETER_ARCSEC,
    MEAN_DAILY_SPEED_DEG,
    NAISARGIKA_BALA_VIRUPAS,
    REQUIRED_SHADBALA_RUPAS,
    SAPTAVARGAJA_POINTS,
    SEVEN_GRAHAS,
    TARAGRAHAS,
    BhavaBalaEntry,
    KalaBalaBreakdown,
    PlanetShadbala,
    ShadbalaSummary,
    SthanaBalaBreakdown,
    compute_ayana_bala,
    compute_cheshta_bala,
    compute_dig_bala,
    compute_drekkana_bala,
    compute_drik_bala,
    compute_kendradi_bala,
    compute_ojhayugmarasyamsa_bala,
    compute_saptavargaja_bala,
    compute_shadbala,
    compute_sthana_bala,
    compute_uchcha_bala,
    parashari_aspect_virupas,
)
from .vargas import (
    ALL_VARGA_KEYS,
    DEBILITATION_SIGNS,
    EXALTATION_SIGNS,
    HIGHER_VARGA_KEYS,
    INDU_KALAS,
    MOOLATRIKONA_RANGES,
    NATURAL_ENEMIES,
    NATURAL_FRIENDS,
    PUSHKARA_BHAGA_DEGREES,
    RASI_LORDS,
    SHASHTIAMSA_CATALOG,
    SHODASHVARGA_KEYS,
    VIMSHOPAKA_WEIGHTS,
    ArudhaPadaSet,
    SpecialLagnas,
    VargaPlacement,
    VimshopakaScore,
    arudha_padas,
    bhava_lagna,
    compound_relationship,
    compute_shodashvarga,
    compute_special_lagnas,
    compute_vimshopaka_bala,
    ghatika_lagna,
    hora_lagna,
    indu_lagna,
    is_pushkara_bhaga,
    is_pushkara_navamsa,
    is_vargottama,
    natural_relationship,
    pranapada_lagna,
    resolve_jaimini_sign_lord,
    shashtiamsa_detail,
    sree_lagna,
    varga_sign,
    varnada_lagna,
)
from .vishesha_lagnas import (
    ARUDHA_HOUSE_NAMES,
    ArudhaPadaDetail,
    FullAstronomicalBodyEphemeris,
    INDU_LAGNA_KALA_VALUES,
    PUSHKARA_BHAGA_DEGREES as VISHESHA_PUSHKARA_BHAGA_DEGREES,
    PUSHKARA_NAVAMSA_RASHI_INDICES,
    VisheshaLagnaAndSpecialPointsReport,
    VisheshaLagnaPoint,
    compute_full_astronomical_sky_ephemeris,
    compute_vishesha_lagnas_and_special_points,
)


@dataclass(frozen=True)
class PlanetDignityFlags:
    """Special dignity flags for a single body."""

    planet: str
    longitude_deg: float
    vargottama: bool
    pushkara_navamsa: bool
    pushkara_bhaga: bool


@dataclass(frozen=True)
class VedicChartAnalysis:
    """Comprehensive clean-room Vedic Jyotish mathematical analysis with a SHA-256 receipt."""

    jd_ut: float
    iso_utc: str
    lagna_lon_deg: float
    lagna_nakshatra: NakshatraPosition
    planet_nakshatras: Mapping[str, NakshatraPosition]
    planet_abhijit_positions: Mapping[str, AbhijitPosition]
    tara_bala_from_moon: Mapping[str, TaraBalaResult]
    planet_vargas: Mapping[str, Mapping[str, VargaPlacement]]
    lagna_vargas: Mapping[str, VargaPlacement]
    planet_dignity_flags: Mapping[str, PlanetDignityFlags]
    vimshopaka_shodashvarga: Mapping[str, VimshopakaScore]
    special_lagnas: SpecialLagnas
    arudha_padas: ArudhaPadaSet
    panchanga: PanchangaSummary
    hora_table: tuple[HoraWindow, ...]
    muhurta_windows: MuhurtaWindows
    vimshottari_dasha: DashaTimeline
    vimshottari_active_5_levels: tuple[DashaPeriod, DashaPeriod, DashaPeriod, DashaPeriod, DashaPeriod]
    ashtottari_dasha: DashaTimeline
    yogini_dasha: DashaTimeline
    chara_dasha: DashaTimeline
    chara_karakas_7: tuple[CharaKarakaEntry, ...]
    chara_karakas_8: tuple[CharaKarakaEntry, ...]
    shadbala: ShadbalaSummary
    ashtakavarga: AshtakavargaAnalysis
    gochara_transits: Mapping[str, GocharaPlanetTransit]
    receipt: Mapping[str, Any]
    receipt_sha256: str


def compute_vedic_chart_analysis(
    planet_longitudes: Mapping[str, float],
    lagna_lon_deg: float,
    *,
    jd_ut: float = 2451545.0,
    sunrise_jd_ut: float | None = None,
    sunset_jd_ut: float | None = None,
    ayanamsa_deg: float = 24.0,
    ayanamsa_system: str = "lahiri",
    year_days: float = SOLAR_YEAR_DAYS,
    query_jd: float | None = None,
    transit_longitudes: Mapping[str, float] | None = None,
    planet_speeds_deg_per_day: Mapping[str, float] | None = None,
    ce_year: int | None = None,
) -> VedicChartAnalysis:
    """Compute a complete, deterministic Vedic Jyotish mathematical chart analysis
    with an auditable SHA-256 calculation receipt.
    """
    norm_lons: dict[str, float] = {
        k.strip().capitalize(): normalize_degrees(v) for k, v in planet_longitudes.items()
    }
    for req in SEVEN_GRAHAS:
        if req not in norm_lons:
            raise ValueError(f"Missing required planet {req!r} in planet_longitudes")
    if "Rahu" in norm_lons and "Ketu" not in norm_lons:
        norm_lons["Ketu"] = normalize_degrees(norm_lons["Rahu"] + 180.0)
    elif "Rahu" not in norm_lons:
        norm_lons["Rahu"] = 0.0
        norm_lons["Ketu"] = 180.0

    l_lon = normalize_degrees(lagna_lon_deg)
    sr_jd = float(sunrise_jd_ut) if sunrise_jd_ut is not None else (float(int(jd_ut - 0.5)) + 0.75)
    ss_jd = float(sunset_jd_ut) if sunset_jd_ut is not None else (sr_jd + 0.5)
    hours_since_sr = ((jd_ut - sr_jd) % 1.0) * 24.0
    q_jd = float(query_jd) if query_jd is not None else float(jd_ut)

    lagna_nak = nakshatra_position(l_lon)
    moon_lon = norm_lons["Moon"]
    sun_lon = norm_lons["Sun"]

    p_naks = {p: nakshatra_position(lon) for p, lon in norm_lons.items()}
    p_abhijit = {p: abhijit_position(lon) for p, lon in norm_lons.items()}
    tara_map = {p: compute_tara_bala(moon_lon, lon) for p, lon in norm_lons.items()}

    p_vargas = {p: compute_shodashvarga(lon, include_higher=True) for p, lon in norm_lons.items()}
    l_vargas = compute_shodashvarga(l_lon, include_higher=True)

    dignity_flags = {
        p: PlanetDignityFlags(
            planet=p,
            longitude_deg=lon,
            vargottama=is_vargottama(lon),
            pushkara_navamsa=is_pushkara_navamsa(lon),
            pushkara_bhaga=is_pushkara_bhaga(lon),
        )
        for p, lon in norm_lons.items()
    }

    vimshopaka_16 = {
        g: compute_vimshopaka_bala(g, norm_lons[g], norm_lons, scheme="shodashvarga")
        for g in SEVEN_GRAHAS
    }

    spec_lagnas = compute_special_lagnas(l_lon, sun_lon, moon_lon, hours_since_sr)
    arudhas = arudha_padas(l_lon, norm_lons)

    panch = compute_panchanga(
        sun_lon,
        moon_lon,
        jd_ut=jd_ut,
        sunrise_jd_ut=sr_jd,
        ce_year=ce_year,
    )
    horas = compute_hora_table(sr_jd, ss_jd)
    muhurtas = compute_muhurta_windows(sr_jd, ss_jd)

    vim_dasha = compute_vimshottari_dasha(moon_lon, jd_ut, year_days=year_days, max_level=2)
    vim_5 = resolve_dasha_5_levels(vim_dasha, q_jd)
    ash_dasha = compute_ashtottari_dasha(moon_lon, jd_ut, year_days=year_days, max_level=2)
    yog_dasha = compute_yogini_dasha(moon_lon, jd_ut, year_days=year_days, max_level=2)
    cha_dasha = compute_chara_dasha(l_lon, norm_lons, jd_ut, year_days=year_days, max_level=2)

    ck_7 = compute_chara_karakas(norm_lons, scheme="7")
    ck_8 = compute_chara_karakas(norm_lons, scheme="8")

    shad = compute_shadbala(
        norm_lons,
        l_lon,
        jd_ut=jd_ut,
        sunrise_jd_ut=sr_jd,
        sunset_jd_ut=ss_jd,
        ayanamsa_deg=ayanamsa_deg,
        planet_speeds_deg_per_day=planet_speeds_deg_per_day,
    )

    ashta = compute_ashtakavarga(norm_lons, l_lon)
    tr_lons = transit_longitudes if transit_longitudes is not None else norm_lons
    gochara = evaluate_gochara_vedha(moon_lon, tr_lons, ashtakavarga=ashta)

    request_payload = {
        "jd_ut": float(jd_ut),
        "sunrise_jd_ut": sr_jd,
        "sunset_jd_ut": ss_jd,
        "lagna_lon_deg": l_lon,
        "planet_longitudes": norm_lons,
        "ayanamsa_deg": float(ayanamsa_deg),
        "ayanamsa_system": ayanamsa_system,
        "year_days": float(year_days),
        "query_jd": q_jd,
    }
    summary_digest_payload = {
        "lagna_nakshatra": lagna_nak.name,
        "moon_nakshatra": p_naks["Moon"].name,
        "tithi": panch.tithi.number,
        "yoga": panch.yoga.number,
        "karana": panch.karana.number,
        "vimshottari_opening_lord": vim_dasha.opening_lord,
        "atmakaraka_7": ck_7[0].planet,
        "sav_7": list(ashta.sarvashtakavarga_7),
        "sav_total": ashta.sarvashtakavarga_7_total,
        "shadbala_rupas": {g: round(shad.planets[g].total_rupas, 6) for g in SEVEN_GRAHAS},
    }
    receipt: dict[str, Any] = {
        "package": "ephemeris-oss",
        "version": __version__,
        "module": "ephemeris_oss.jyotish",
        "ayanamsa_system": ayanamsa_system,
        "ayanamsa_deg": float(ayanamsa_deg),
        "request_sha256": canonical_hash(request_payload),
        "result_sha256": canonical_hash(summary_digest_payload),
    }
    receipt_sha256 = canonical_hash(receipt)

    return VedicChartAnalysis(
        jd_ut=float(jd_ut),
        iso_utc=jd_to_iso_utc(jd_ut),
        lagna_lon_deg=l_lon,
        lagna_nakshatra=lagna_nak,
        planet_nakshatras=p_naks,
        planet_abhijit_positions=p_abhijit,
        tara_bala_from_moon=tara_map,
        planet_vargas=p_vargas,
        lagna_vargas=l_vargas,
        planet_dignity_flags=dignity_flags,
        vimshopaka_shodashvarga=vimshopaka_16,
        special_lagnas=spec_lagnas,
        arudha_padas=arudhas,
        panchanga=panch,
        hora_table=horas,
        muhurta_windows=muhurtas,
        vimshottari_dasha=vim_dasha,
        vimshottari_active_5_levels=vim_5,
        ashtottari_dasha=ash_dasha,
        yogini_dasha=yog_dasha,
        chara_dasha=cha_dasha,
        chara_karakas_7=ck_7,
        chara_karakas_8=ck_8,
        shadbala=shad,
        ashtakavarga=ashta,
        gochara_transits=gochara,
        receipt=receipt,
        receipt_sha256=receipt_sha256,
    )


__all__ = [
    "ABHIJIT_END_DEG",
    "ABHIJIT_SPAN_DEG",
    "ABHIJIT_START_DEG",
    "ALL_VARGA_KEYS",
    "ASHTAKAVARGA_CONTRIBUTORS",
    "ASHTOTTARI_RULERS",
    "ASHTOTTARI_TOTAL_YEARS",
    "ASHTOTTARI_YEARS",
    "AbhijitPosition",
    "ArudhaPadaSet",
    "AshtakavargaAnalysis",
    "BAV_BENEFIC_HOUSES",
    "BhavaBalaEntry",
    "BhinnaAshtakavargaTable",
    "CharaKarakaEntry",
    "DEBILITATION_SIGNS",
    "DEEP_EXALTATION_DEG",
    "DISC_DIAMETER_ARCSEC",
    "DUAL_OWNERSHIP_PAIRS",
    "DURMUHURTA_DAY_INDICES",
    "DashaPeriod",
    "DashaTimeline",
    "EXALTATION_SIGNS",
    "EXPECTED_BAV_TOTALS",
    "EXPECTED_SAV_TOTAL",
    "FIXED_KARANAS",
    "GOCHARA_VEDHA_TABLE",
    "GRAHA_GUNAKARAS",
    "GULIKA_KALAM_SEGMENT",
    "GocharaPlanetTransit",
    "HIGHER_VARGA_KEYS",
    "HORA_CHALDEAN_ORDER",
    "HoraWindow",
    "INDU_KALAS",
    "KARAKA_7_ROLES",
    "KARAKA_8_ROLES",
    "KARANA_SPAN_DEG",
    "KalaBalaBreakdown",
    "KaranaInfo",
    "LEVEL_NAMES",
    "MEAN_DAILY_SPEED_DEG",
    "MOOLATRIKONA_RANGES",
    "MOVABLE_KARANAS",
    "MuhurtaWindows",
    " NAISARGIKA_BALA_VIRUPAS".strip(),
    "NAKSHATRA_CATALOG",
    "NAKSHATRA_NAMES",
    "NAKSHATRA_SPAN_DEG",
    "NATURAL_ENEMIES",
    "NATURAL_FRIENDS",
    "NakshatraMetadata",
    "NakshatraPosition",
    "PADA_SPAN_DEG",
    "PAKSHA_TITHI_NAMES",
    "PUSHKARA_BHAGA_DEGREES",
    "PanchangaSummary",
    "PlanetDignityFlags",
    "PlanetShadbala",
    "RAHU_KALAM_SEGMENT",
    "RASI_GUNAKARAS",
    "RASI_LORDS",
    "RASI_NAMES",
    "REQUIRED_SHADBALA_RUPAS",
    "RITU_CATALOG",
    "SAMVATSARA_NAMES",
    "SAPTAVARGAJA_POINTS",
    "SAVANA_YEAR_DAYS",
    "SAVYA_SIGNS",
    "SEVEN_GRAHAS",
    "SHASHTIAMSA_CATALOG",
    "SHODASHVARGA_KEYS",
    "SOLAR_YEAR_DAYS",
    "SamvatsaraInfo",
    "ShadbalaSummary",
    "SpecialLagnas",
    "SthanaBalaBreakdown",
    "TARAGRAHAS",
    "TARA_BENEFIC",
    "TARA_NAMES",
    "TITHI_EIGHT_LORDS",
    "TITHI_GROUPS",
    "TITHI_SPAN_DEG",
    "TaraBalaResult",
    "TimeWindow",
    "TithiInfo",
    "VARA_CATALOG",
    "VEDHA_EXEMPT_PAIRS",
    "VIMSHOPAKA_WEIGHTS",
    "VIMSHOTTARI_RULERS",
    "VIMSHOTTARI_TOTAL_YEARS",
    "VIMSHOTTARI_YEARS",
    "VaraInfo",
    "VargaPlacement",
    "VedicChartAnalysis",
    "VimshopakaScore",
    "YAMAGANDAM_SEGMENT",
    "YOGA_CATALOG",
    "YOGA_SPAN_DEG",
    "YOGINI_CATALOG",
    "YOGINI_LORDS",
    "YOGINI_NAMES",
    "YOGINI_TOTAL_YEARS",
    "YOGINI_YEARS",
    "YogaInfo",
    "abhijit_position",
    "arudha_padas",
    "bhava_lagna",
    "classify_kalachakra_gati",
    "compound_relationship",
    "compute_ashtakavarga",
    "compute_ashtottari_dasha",
    "compute_ayana_and_ritu",
    "compute_ayana_bala",
    "compute_chara_dasha",
    "compute_chara_karakas",
    "compute_cheshta_bala",
    "compute_dig_bala",
    "compute_drekkana_bala",
    "compute_drik_bala",
    "compute_hora_table",
    "compute_kalachakra_dasha",
    "compute_karana",
    "KalachakraDashaPeriod",
    "KalachakraDashaTimeline",
    "KALACHAKRA_APASAVYA_SEQUENCES",
    "KALACHAKRA_SAVYA_NAKSHATRAS",
    "KALACHAKRA_SAVYA_SEQUENCES",
    "KALACHAKRA_SIGN_YEARS",
    "compute_kendradi_bala",
    "compute_muhurta_windows",
    "compute_ojhayugmarasyamsa_bala",
    "compute_panchanga",
    "compute_pindas",
    "compute_samvatsara",
    "compute_saptavargaja_bala",
    "compute_shadbala",
    "compute_shodashvarga",
    "compute_special_lagnas",
    "compute_sthana_bala",
    "compute_tara_bala",
    "compute_tithi",
    "compute_uchcha_bala",
    "compute_vara",
    "compute_vedic_chart_analysis",
    "compute_vimshopaka_bala",
    "compute_vimshottari_dasha",
    "compute_yoga",
    "compute_yogini_dasha",
    "ekadhipatya_shodhana",
    "evaluate_gochara_vedha",
    "ghatika_lagna",
    "hora_lagna",
    "indu_lagna",
    "is_pushkara_bhaga",
    "is_pushkara_navamsa",
    "is_vargottama",
    "jd_to_iso_utc",
    "nakshatra_position",
    "natural_relationship",
    "normalize_degrees",
    "parashari_aspect_virupas",
    "pranapada_lagna",
    "resolve_dasha_5_levels",
    "resolve_jaimini_sign_lord",
    "shashtiamsa_detail",
    "sree_lagna",
    "trikona_shodhana",
    "varga_sign",
    "varnada_lagna",
]
