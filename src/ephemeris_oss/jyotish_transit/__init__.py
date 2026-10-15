"""Clean-room Vedic Electional Muhurta, Kerala Prashna Marga, and Sarvatobhadra / Kota / Kakshya Transit Suite.

Provides deterministic mathematical engines with SHA-256 calculation receipts:
- Electional Muhurta Evaluator and Window Scanner (`muhurta_search`):
  Panchaka Rahita, Siddha / Amrita Siddhi / Sarvartha Siddhi / Pushkara Yogas,
  Dagdha Rasi, Chandrabala, Gandanta junctions, instant scoring, and window scanning.
- Kerala Prashna Marga Sphutas, 11 Classical Upagrahas, and Horary Arudha (`prashna`):
  5 Solar Upagrahas (Dhuma, Vyatipata, Parivesha, Indrachapa, Upaketu),
  6 Kalavela Upagrahas (Gulika/Mandi, Kala, Mrityu, Ardhaprahara, Yamaghantaka, ochcha),
  Trisphuta, Chatusphuta, Panchasphuta, Prana/Deha/Mrityu Sphutas, Tithi/Kshetra/Beeja
  Sphutas, Shirshodaya/Prishtodaya/Ubhayodaya, and Dhatu/Moola/Jeeva classifications.
- Ashtakavarga Kakshya, Sarvatobhadra 9x9 Chakra, and Kota Chakra (`chakras`):
  8-fold Kakshya transit timing (3.75 deg segments), Prastara Ashtakavarga,
  81-cell Sarvatobhadra Chakra with 3-way Vedha rays, and 28-nakshatra Kota Chakra
  fortress protection and vulnerability grid.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Mapping

from .._version import __version__
from ..engine.receipt import canonical_hash
from ..jyotish.nakshatra import normalize_degrees
from ..jyotish.shadbala import SEVEN_GRAHAS
from .chakras import (
    KAKSHYA_LORDS,
    KAKSHYA_SPAN_DEG,
    KOTA_BAHYA_OFFSETS,
    KOTA_MADHYA_OFFSETS,
    KOTA_NIRGAMANA_OFFSETS,
    KOTA_PRAKAARA_OFFSETS,
    KOTA_PRAVESHA_OFFSETS,
    KOTA_STAMBHA_OFFSETS,
    NATURAL_BENEFICS,
    NATURAL_MALEFICS,
    SARVATOBHADRA_12_RASIS,
    SARVATOBHADRA_16_VOWELS,
    SARVATOBHADRA_20_CONSONANTS,
    SARVATOBHADRA_28_NAKSHATRAS,
    SARVATOBHADRA_5_TITHIS,
    KakshyaTransitEvaluation,
    KotaChakraAnalysis,
    KotaNakshatraSlot,
    KotaPlanetPlacement,
    PrastaraAshtakavargaSet,
    PrastaraTable,
    SarvatobhadraCell,
    SarvatobhadraChakraAnalysis,
    SarvatobhadraPlanetTransit,
    SarvatobhadraVedhaRays,
    build_sarvatobhadra_grid,
    compute_sarvatobhadra_vedha,
    evaluate_kakshya,
    evaluate_kota_chakra,
    evaluate_sarvatobhadra_transits,
    prastara_ashtakavarga,
)
from .muhurta_search import (
    AMRITA_SIDDHI_EXCLUDED_PAKSHA_TITHI,
    AMRITA_SIDDHI_NAKSHATRA,
    BHADRA_PAKSHA_TITHIS,
    CHANDRABALA_BAD_HOUSES,
    CHANDRABALA_GOOD_HOUSES,
    CHANDRABALA_NEUTRAL_HOUSES,
    DAGDHA_RASI_BY_PAKSHA_TITHI,
    DEFAULT_GANDANTA_ORB_DEG,
    DWIPUSHKARA_NAKSHATRA_INDICES,
    GANDANTA_JUNCTIONS_DEG,
    PANCHAKA_CATALOG,
    PUSHKARA_VARA_INDICES,
    SARVARTHA_SIDDHI_NAKSHATRAS,
    TRIPUSHKARA_NAKSHATRA_INDICES,
    ChandrabalaResult,
    MuhurtaInstantEvaluation,
    MuhurtaScanReport,
    MuhurtaWindowInterval,
    PanchakaResult,
    SiddhaYogaEvaluation,
    evaluate_chandrabala,
    evaluate_panchaka,
    evaluate_siddha_yogas,
    is_gandanta_degree,
    scan_muhurta_windows,
    score_muhurta_instant,
)
from .prashna import (
    DHATU_SIGNS,
    JEEVA_SIGNS,
    KALAVELA_RULER_VARA_INDEX,
    KALAVELA_UPAGRAHA_NAMES,
    MOOLA_SIGNS,
    PRISHTODAYA_SIGNS,
    SHIRSHODAYA_SIGNS,
    SIDEREAL_ROTATION_DEG_PER_DAY,
    SOLAR_UPAGRAHA_NAMES,
    UBHAYODAYA_SIGNS,
    UPAGRAHA_11_NAMES,
    KalavelaUpagrahaPoint,
    PrashnaAnalysis,
    PrashnaArudhaResult,
    PrashnaSignClassification,
    PrashnaSphutaSet,
    SolarUpagrahaPoint,
    SphutaPoint,
    UpagrahaSet,
    classify_prashna_sign,
    compute_11_upagrahas,
    compute_kalavela_upagrahas,
    compute_prashna_analysis,
    compute_prashna_arudha,
    compute_prashna_sphutas,
    compute_solar_upagrahas,
)


@dataclass(frozen=True)
class JyotishTransitSuiteResult:
    """Unified Muhurta, Prashna, Kakshya, Sarvatobhadra, and Kota Chakra synthesis."""

    muhurta_instant: MuhurtaInstantEvaluation
    prashna: PrashnaAnalysis
    prastara: PrastaraAshtakavargaSet
    kakshya_transits: Mapping[str, KakshyaTransitEvaluation]
    sarvatobhadra: SarvatobhadraChakraAnalysis
    kota_chakra: KotaChakraAnalysis
    receipt: Mapping[str, Any]
    receipt_sha256: str


def compute_jyotish_transit_suite(
    natal_longitudes: Mapping[str, float],
    natal_lagna_lon_deg: float,
    *,
    transit_longitudes: Mapping[str, float] | None = None,
    transit_lagna_lon_deg: float | None = None,
    planet_speeds_deg_per_day: Mapping[str, float] | None = None,
    jd_ut: float = 2451545.0,
    sunrise_jd: float = 2451544.75,
    sunset_jd: float = 2451545.25,
    next_sunrise_jd: float | None = None,
    seed_number: int = 1,
    janma_tithi_group: str | None = None,
    nama_akshara: str | None = None,
) -> JyotishTransitSuiteResult:
    """Compute a unified Muhurta, Prashna, Prastara Kakshya, Sarvatobhadra, and Kota Chakra
    analysis with a deterministic SHA-256 receipt.
    """
    n_lons = {k.strip().capitalize(): normalize_degrees(v) for k, v in natal_longitudes.items()}
    for g in SEVEN_GRAHAS:
        if g not in n_lons:
            raise ValueError(f"Missing required natal planet {g!r}")
    t_lons = (
        {k.strip().capitalize(): normalize_degrees(v) for k, v in transit_longitudes.items()}
        if transit_longitudes is not None
        else dict(n_lons)
    )
    t_lagna = normalize_degrees(transit_lagna_lon_deg if transit_lagna_lon_deg is not None else natal_lagna_lon_deg)

    muhurta_ev = score_muhurta_instant(
        jd_ut=jd_ut,
        sun_lon_deg=t_lons["Sun"],
        moon_lon_deg=t_lons["Moon"],
        lagna_lon_deg=t_lagna,
        natal_moon_lon_deg=n_lons["Moon"],
        sunrise_jd_ut=sunrise_jd,
        sunset_jd_ut=sunset_jd,
        next_sunrise_jd_ut=next_sunrise_jd,
    )
    prashna_res = compute_prashna_analysis(
        t_lons,
        t_lagna,
        jd_ut=jd_ut,
        sunrise_jd=sunrise_jd,
        sunset_jd=sunset_jd,
        next_sunrise_jd=next_sunrise_jd,
        seed_number=seed_number,
    )
    prastara_set = prastara_ashtakavarga(n_lons, natal_lagna_lon_deg)
    kakshya_map = {
        g: evaluate_kakshya(t_lons[g], recipient=g, prastara=prastara_set)
        for g in SEVEN_GRAHAS
        if g in t_lons
    }
    sbc = evaluate_sarvatobhadra_transits(
        n_lons["Moon"],
        t_lons,
        planet_speeds_deg_per_day=planet_speeds_deg_per_day,
        janma_tithi_group=janma_tithi_group,
        nama_akshara=nama_akshara,
    )
    kota = evaluate_kota_chakra(n_lons["Moon"], t_lons)

    receipt = {
        "package": "ephemeris-oss",
        "version": __version__,
        "module": "ephemeris_oss.jyotish_transit",
        "muhurta_sha256": muhurta_ev.receipt_sha256,
        "prashna_sha256": prashna_res.receipt_sha256,
        "prastara_sha256": prastara_set.receipt_sha256,
        "sarvatobhadra_sha256": sbc.receipt_sha256,
        "kota_sha256": kota.receipt_sha256,
    }
    return JyotishTransitSuiteResult(
        muhurta_instant=muhurta_ev,
        prashna=prashna_res,
        prastara=prastara_set,
        kakshya_transits=kakshya_map,
        sarvatobhadra=sbc,
        kota_chakra=kota,
        receipt=receipt,
        receipt_sha256=canonical_hash(receipt),
    )


__all__ = [
    "AMRITA_SIDDHI_EXCLUDED_PAKSHA_TITHI",
    "AMRITA_SIDDHI_NAKSHATRA",
    "BHADRA_PAKSHA_TITHIS",
    "CHANDRABALA_BAD_HOUSES",
    "CHANDRABALA_GOOD_HOUSES",
    "CHANDRABALA_NEUTRAL_HOUSES",
    "DAGDHA_RASI_BY_PAKSHA_TITHI",
    "DEFAULT_GANDANTA_ORB_DEG",
    "DHATU_SIGNS",
    "DWIPUSHKARA_NAKSHATRA_INDICES",
    "GANDANTA_JUNCTIONS_DEG",
    "JEEVA_SIGNS",
    "JyotishTransitSuiteResult",
    "KAKSHYA_LORDS",
    "KAKSHYA_SPAN_DEG",
    "KALAVELA_RULER_VARA_INDEX",
    "KALAVELA_UPAGRAHA_NAMES",
    "KOTA_BAHYA_OFFSETS",
    "KOTA_MADHYA_OFFSETS",
    "KOTA_NIRGAMANA_OFFSETS",
    "KOTA_PRAKAARA_OFFSETS",
    "KOTA_PRAVESHA_OFFSETS",
    "KOTA_STAMBHA_OFFSETS",
    "KakshyaTransitEvaluation",
    "KalavelaUpagrahaPoint",
    "KotaChakraAnalysis",
    "KotaNakshatraSlot",
    "KotaPlanetPlacement",
    "MOOLA_SIGNS",
    "MuhurtaInstantEvaluation",
    "MuhurtaScanReport",
    "MuhurtaWindowInterval",
    "NATURAL_BENEFICS",
    "NATURAL_MALEFICS",
    "PANCHAKA_CATALOG",
    "PRISHTODAYA_SIGNS",
    "PUSHKARA_VARA_INDICES",
    "PanchakaResult",
    "PrashnaAnalysis",
    "PrashnaArudhaResult",
    "PrashnaSignClassification",
    "PrashnaSphutaSet",
    "PrastaraAshtakavargaSet",
    "PrastaraTable",
    "SARVARTHA_SIDDHI_NAKSHATRAS",
    "SARVATOBHADRA_12_RASIS",
    "SARVATOBHADRA_16_VOWELS",
    "SARVATOBHADRA_20_CONSONANTS",
    "SARVATOBHADRA_28_NAKSHATRAS",
    "SARVATOBHADRA_5_TITHIS",
    "SHIRSHODAYA_SIGNS",
    "SIDEREAL_ROTATION_DEG_PER_DAY",
    "SOLAR_UPAGRAHA_NAMES",
    "SarvatobhadraCell",
    "SarvatobhadraChakraAnalysis",
    "SarvatobhadraPlanetTransit",
    "SarvatobhadraVedhaRays",
    "SiddhaYogaEvaluation",
    "SolarUpagrahaPoint",
    "SphutaPoint",
    "TRIPUSHKARA_NAKSHATRA_INDICES",
    "UBHAYODAYA_SIGNS",
    "UPAGRAHA_11_NAMES",
    "UpagrahaSet",
    "ChandrabalaResult",
    "build_sarvatobhadra_grid",
    "classify_prashna_sign",
    "compute_11_upagrahas",
    "compute_jyotish_transit_suite",
    "compute_kalavela_upagrahas",
    "compute_prashna_analysis",
    "compute_prashna_arudha",
    "compute_prashna_sphutas",
    "compute_sarvatobhadra_vedha",
    "compute_solar_upagrahas",
    "evaluate_chandrabala",
    "evaluate_kakshya",
    "evaluate_kota_chakra",
    "evaluate_panchaka",
    "evaluate_sarvatobhadra_transits",
    "evaluate_siddha_yogas",
    "is_gandanta_degree",
    "prastara_ashtakavarga",
    "scan_muhurta_windows",
    "score_muhurta_instant",
]
