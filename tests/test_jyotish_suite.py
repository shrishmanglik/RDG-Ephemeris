"""Comprehensive unit and mathematical invariant test suite for `ephemeris_oss.jyotish`."""

from __future__ import annotations

import math
import pytest

from ephemeris_oss import VedicChartAnalysis, compute_vedic_chart_analysis, jyotish
from ephemeris_oss.jyotish import (
    ABHIJIT_END_DEG,
    ABHIJIT_START_DEG,
    ALL_VARGA_KEYS,
    BAV_BENEFIC_HOUSES,
    DEEP_EXALTATION_DEG,
    EXPECTED_BAV_TOTALS,
    EXPECTED_SAV_TOTAL,
    HIGHER_VARGA_KEYS,
    KARAKA_7_ROLES,
    KARAKA_8_ROLES,
    NAKSHATRA_CATALOG,
    NAKSHATRA_SPAN_DEG,
    NAISARGIKA_BALA_VIRUPAS,
    PADA_SPAN_DEG,
    PUSHKARA_BHAGA_DEGREES,
    RASI_NAMES,
    REQUIRED_SHADBALA_RUPAS,
    SAMVATSARA_NAMES,
    SAVANA_YEAR_DAYS,
    SEVEN_GRAHAS,
    SHASHTIAMSA_CATALOG,
    SHODASHVARGA_KEYS,
    SOLAR_YEAR_DAYS,
    VIMSHOPAKA_WEIGHTS,
    VIMSHOTTARI_RULERS,
    VIMSHOTTARI_TOTAL_YEARS,
    VIMSHOTTARI_YEARS,
    YOGA_CATALOG,
    YOGINI_TOTAL_YEARS,
    YOGINI_YEARS,
    abhijit_position,
    arudha_padas,
    bhava_lagna,
    compound_relationship,
    compute_ashtakavarga,
    compute_ashtottari_dasha,
    compute_ayana_and_ritu,
    compute_ayana_bala,
    compute_chara_dasha,
    compute_chara_karakas,
    compute_cheshta_bala,
    compute_dig_bala,
    compute_drekkana_bala,
    compute_drik_bala,
    compute_hora_table,
    compute_karana,
    compute_kendradi_bala,
    compute_muhurta_windows,
    compute_ojhayugmarasyamsa_bala,
    compute_panchanga,
    compute_samvatsara,
    compute_saptavargaja_bala,
    compute_shadbala,
    compute_shodashvarga,
    compute_special_lagnas,
    compute_sthana_bala,
    compute_tara_bala,
    compute_tithi,
    compute_uchcha_bala,
    compute_vara,
    compute_vimshopaka_bala,
    compute_vimshottari_dasha,
    compute_yoga,
    compute_yogini_dasha,
    ekadhipatya_shodhana,
    evaluate_gochara_vedha,
    ghatika_lagna,
    hora_lagna,
    indu_lagna,
    is_pushkara_bhaga,
    is_pushkara_navamsa,
    is_vargottama,
    jd_to_iso_utc,
    nakshatra_position,
    natural_relationship,
    normalize_degrees,
    parashari_aspect_virupas,
    pranapada_lagna,
    resolve_dasha_5_levels,
    resolve_jaimini_sign_lord,
    shashtiamsa_detail,
    sree_lagna,
    trikona_shodhana,
    varga_sign,
    varnada_lagna,
)


SAMPLE_CHART_LONS: dict[str, float] = {
    "Sun": 10.0,       # Aries 10 deg (deep exaltation)
    "Moon": 33.0,      # Taurus 3 deg (Krittika pada 2, deep exaltation)
    "Mars": 298.0,     # Capricorn 28 deg (deep exaltation)
    "Mercury": 165.0,  # Virgo 15 deg (deep exaltation)
    "Jupiter": 95.0,   # Cancer 5 deg (Pushya pada 1, deep exaltation)
    "Venus": 357.0,    # Pisces 27 deg (Revati pada 4, deep exaltation)
    "Saturn": 200.0,   # Libra 20 deg (Swati pada 4, deep exaltation)
    "Rahu": 45.0,      # Taurus 15 deg
    "Ketu": 225.0,     # Scorpio 15 deg
}
SAMPLE_LAGNA_LON: float = 15.0  # Aries 15 deg


# ============================================================================
# 1. NAKSHATRA, PADA, TARA BALA, AND ABHIJIT TESTS
# ============================================================================


def test_nakshatra_catalog_completeness() -> None:
    assert len(NAKSHATRA_CATALOG) == 27
    assert NAKSHATRA_CATALOG[0].name == "Ashwini"
    assert NAKSHATRA_CATALOG[26].name == "Revati"
    for i, item in enumerate(NAKSHATRA_CATALOG):
        assert item.index == i
        assert item.number == i + 1
        assert item.vimshottari_ruler == VIMSHOTTARI_RULERS[i % 9]
        assert item.gana in ("Deva", "Manushya", "Rakshasa")
        assert item.nadi in ("Adi", "Madhya", "Antya")


@pytest.mark.parametrize("global_pada", list(range(1, 109)))
def test_all_108_padas_bijection_and_navamsa_cycle(global_pada: int) -> None:
    lon = (global_pada - 0.5) * PADA_SPAN_DEG
    pos = nakshatra_position(lon)
    expected_nak_idx = (global_pada - 1) // 4
    expected_pada = ((global_pada - 1) % 4) + 1
    assert pos.global_pada == global_pada
    assert pos.index == expected_nak_idx
    assert pos.pada == expected_pada
    assert pos.navamsa_sign == (global_pada - 1) % 12
    assert pos.navamsa_sign_name == RASI_NAMES[(global_pada - 1) % 12]
    assert 0.0 <= pos.fraction_elapsed <= 1.0
    assert math.isclose(pos.fraction_elapsed + pos.fraction_remaining, 1.0, abs_tol=1e-12)


def test_nakshatra_boundary_conditions() -> None:
    pos_zero = nakshatra_position(0.0)
    assert pos_zero.name == "Ashwini"
    assert pos_zero.pada == 1
    assert pos_zero.global_pada == 1
    assert pos_zero.navamsa_sign == 0
    assert math.isclose(pos_zero.fraction_elapsed, 0.0, abs_tol=1e-12)
    assert math.isclose(pos_zero.fraction_remaining, 1.0, abs_tol=1e-12)

    pos_360 = nakshatra_position(360.0)
    assert pos_360.name == "Ashwini"
    assert pos_360.global_pada == 1

    pos_revati_end = nakshatra_position(359.9999)
    assert pos_revati_end.name == "Revati"
    assert pos_revati_end.pada == 4
    assert pos_revati_end.global_pada == 108
    assert pos_revati_end.navamsa_sign == 11  # Meena


def test_tara_bala_nine_fold_cycle() -> None:
    expected = [
        (1, "Janma", False),
        (2, "Sampat", True),
        (3, "Vipat", False),
        (4, "Kshema", True),
        (5, "Pratyak", False),
        (6, "Sadhana", True),
        (7, "Naidhana", False),
        (8, "Mitra", True),
        (9, "Parama-Mitra", True),
    ]
    for offset in range(27):
        res = compute_tara_bala(natal_nakshatra_index=0, target_nakshatra_index=offset)
        t_num, t_name, t_ben = expected[offset % 9]
        assert res.count_from_natal == offset + 1
        assert res.tara_number == t_num
        assert res.tara_name == t_name
        assert res.is_benefic is t_ben
        assert res.paryaya_cycle == (offset // 9) + 1


def test_abhijit_28_nakshatra_partition() -> None:
    # Midpoint of Abhijit (between 276 deg 40 min and 280 deg 53 min 20 sec)
    mid_abhijit = 0.5 * (ABHIJIT_START_DEG + ABHIJIT_END_DEG)
    ab = abhijit_position(mid_abhijit)
    assert ab.in_abhijit is True
    assert ab.nakshatra_28_name == "Abhijit"
    assert ab.nakshatra_28_index == 21
    assert math.isclose(ab.fraction_elapsed, 0.5, abs_tol=1e-9)

    # Just before Abhijit -> Uttara Ashadha (index 20, 10 deg span)
    before = abhijit_position(270.0)
    assert before.in_abhijit is False
    assert before.nakshatra_28_name == "Uttara Ashadha"
    assert before.nakshatra_28_index == 20
    assert math.isclose(before.span_deg, 10.0, abs_tol=1e-9)

    # Just after Abhijit -> Shravana (index 22)
    after = abhijit_position(285.0)
    assert after.in_abhijit is False
    assert after.nakshatra_28_name == "Shravana"
    assert after.nakshatra_28_index == 22

    # Revati in 28-nakshatra scheme has index 27
    rev = abhijit_position(355.0)
    assert rev.nakshatra_28_index == 27
    assert rev.nakshatra_28_name == "Revati"


# ============================================================================
# 2. VARGAS (D1-D60, HIGHER HARMONICS, VIMSHOPAKA, SPECIAL LAGNAS, ARUDHAS)
# ============================================================================


def test_d1_rasi_and_d2_parashari_hora() -> None:
    # Aries 5 deg -> odd sign, 1st half -> Leo (4)
    assert varga_sign(5.0, "D2").sign_index == 4
    # Aries 20 deg -> odd sign, 2nd half -> Cancer (3)
    assert varga_sign(20.0, "D2").sign_index == 3
    # Taurus 5 deg (lon=35) -> even sign, 1st half -> Cancer (3)
    assert varga_sign(35.0, "D2").sign_index == 3
    # Taurus 20 deg (lon=50) -> even sign, 2nd half -> Leo (4)
    assert varga_sign(50.0, "D2").sign_index == 4


def test_d3_drekkana_and_d4_chaturthamsa() -> None:
    # Aries 1-5-9 Drekkana: 0..10 -> Aries (0), 10..20 -> Leo (4), 20..30 -> Sagittarius (8)
    assert varga_sign(2.0, "D3").sign_index == 0
    assert varga_sign(12.0, "D3").sign_index == 4
    assert varga_sign(22.0, "D3").sign_index == 8

    # Aries 1-4-7-10 Chaturthamsa: 0..7.5 -> 0, 7.5..15 -> 3, 15..22.5 -> 6, 22.5..30 -> 9
    assert varga_sign(3.0, "D4").sign_index == 0
    assert varga_sign(10.0, "D4").sign_index == 3
    assert varga_sign(18.0, "D4").sign_index == 6
    assert varga_sign(27.0, "D4").sign_index == 9


def test_d7_d9_d10_d12_parashari_formulas() -> None:
    # D7: Odd sign starts from itself; Even sign starts from 7th
    assert varga_sign(1.0, "D7").sign_index == 0       # Aries 1st saptamsa -> Aries (0)
    assert varga_sign(31.0, "D7").sign_index == 7      # Taurus 1st saptamsa -> Scorpio (7)

    # D9 matches nakshatra pada navamsa_sign everywhere across the zodiac
    for deg in range(0, 360, 5):
        lon = float(deg) + 0.25
        assert varga_sign(lon, "D9").sign_index == nakshatra_position(lon).navamsa_sign

    # D10: Odd starts from sign itself; Even starts from 9th
    assert varga_sign(1.0, "D10").sign_index == 0      # Aries 1st dasamsa -> Aries (0)
    assert varga_sign(31.0, "D10").sign_index == 9     # Taurus 1st dasamsa -> Capricorn (9)

    # D12: Starts from sign itself, 2.5 deg per part
    assert varga_sign(1.0, "D12").sign_index == 0
    assert varga_sign(29.0, "D12").sign_index == 11


def test_d16_d20_d24_d27_d30_d40_d45_d60() -> None:
    # D16: Movable->Aries(0), Fixed->Leo(4), Dual->Sagittarius(8)
    assert varga_sign(0.5, "D16").sign_index == 0
    assert varga_sign(30.5, "D16").sign_index == 4
    assert varga_sign(60.5, "D16").sign_index == 8

    # D20: Movable->Aries(0), Fixed->Sagittarius(8), Dual->Leo(4)
    assert varga_sign(0.5, "D20").sign_index == 0
    assert varga_sign(30.5, "D20").sign_index == 8
    assert varga_sign(60.5, "D20").sign_index == 4

    # D24: Odd->Leo(4), Even->Cancer(3)
    assert varga_sign(0.5, "D24").sign_index == 4
    assert varga_sign(30.5, "D24").sign_index == 3

    # D27: Fire->0, Earth->3, Air->6, Water->9
    assert varga_sign(0.5, "D27").sign_index == 0
    assert varga_sign(30.5, "D27").sign_index == 3
    assert varga_sign(60.5, "D27").sign_index == 6
    assert varga_sign(90.5, "D27").sign_index == 9

    # D30 Odd (Aries): 0-5->0, 5-10->10, 10-18->8, 18-25->2, 25-30->6
    assert [varga_sign(d, "D30").sign_index for d in (2.0, 7.0, 14.0, 21.0, 27.0)] == [0, 10, 8, 2, 6]
    # D30 Even (Taurus): 0-5->1, 5-12->5, 12-20->11, 20-25->9, 25-30->7
    assert [varga_sign(30.0 + d, "D30").sign_index for d in (2.0, 7.0, 14.0, 22.0, 27.0)] == [1, 5, 11, 9, 7]

    # D40: Odd->Aries(0), Even->Libra(6)
    assert varga_sign(0.2, "D40").sign_index == 0
    assert varga_sign(30.2, "D40").sign_index == 6

    # D45: Movable->Aries(0), Fixed->Leo(4), Dual->Sagittarius(8)
    assert varga_sign(0.2, "D45").sign_index == 0
    assert varga_sign(30.2, "D45").sign_index == 4
    assert varga_sign(60.2, "D45").sign_index == 8

    # D60 Shashtiamsa catalog & reversal in even signs
    assert len(SHASHTIAMSA_CATALOG) == 60
    d60_odd_first = varga_sign(0.1, "D60")
    assert d60_odd_first.shashtiamsa_number == 1
    assert d60_odd_first.shashtiamsa_name == "Ghora"
    assert d60_odd_first.shashtiamsa_is_benefic is False

    d60_odd_last = varga_sign(29.8, "D60")
    assert d60_odd_last.shashtiamsa_number == 60
    assert d60_odd_last.shashtiamsa_name == "Indurekha"
    assert d60_odd_last.shashtiamsa_is_benefic is True

    d60_even_first = varga_sign(30.1, "D60")
    assert d60_even_first.shashtiamsa_number == 60
    assert d60_even_first.shashtiamsa_name == "Indurekha"


def test_higher_harmonic_vargas_d5_to_d144() -> None:
    all_placements = compute_shodashvarga(123.456, include_higher=True)
    assert set(all_placements.keys()) == set(ALL_VARGA_KEYS)
    for key in HIGHER_VARGA_KEYS:
        vp = all_placements[key]
        assert 0 <= vp.sign_index <= 11
        assert 0.0 <= vp.longitude_in_varga_deg < 360.0


def test_vargottama_pushkara_navamsa_and_pushkara_bhaga() -> None:
    # Aries 1.0 deg -> D1=Aries(0), D9=Aries(0) -> Vargottama
    assert is_vargottama(1.0) is True
    # Aries 5.0 deg -> D1=Aries(0), D9=Taurus(1) -> Not Vargottama
    assert is_vargottama(5.0) is False

    # Count Pushkara Navamsas across all 108 padas: exactly 2 per sign = 24 total
    pushkara_count = sum(
        1 for gp in range(1, 109) if is_pushkara_navamsa((gp - 0.5) * PADA_SPAN_DEG)
    )
    assert pushkara_count == 24

    # Pushkara Bhaga exact degrees
    for rasi_idx, deg in enumerate(PUSHKARA_BHAGA_DEGREES):
        lon = rasi_idx * 30.0 + deg
        assert is_pushkara_bhaga(lon) is True
        assert is_pushkara_bhaga(lon + 3.0) is False


@pytest.mark.parametrize("scheme", ["shadvarga", "saptavarga", "dasavarga", "shodashvarga"])
def test_vimshopaka_bala_weights_sum_to_20(scheme: str) -> None:
    assert math.isclose(sum(VIMSHOPAKA_WEIGHTS[scheme].values()), 20.0, abs_tol=1e-9)
    score = compute_vimshopaka_bala("Jupiter", 95.0, SAMPLE_CHART_LONS, scheme=scheme)
    assert 5.0 <= score.total_score <= 20.0
    assert math.isclose(score.percentage, score.total_score * 5.0, abs_tol=1e-3)


def test_special_lagnas_and_arudha_padas() -> None:
    assert math.isclose(bhava_lagna(0.0, 2.0), 30.0, abs_tol=1e-9)
    assert math.isclose(hora_lagna(0.0, 1.0), 30.0, abs_tol=1e-9)
    assert math.isclose(ghatika_lagna(0.0, 0.4), 30.0, abs_tol=1e-9)
    assert math.isclose(sree_lagna(10.0, 0.5 * NAKSHATRA_SPAN_DEG), 190.0, abs_tol=1e-9)

    spec = compute_special_lagnas(15.0, 10.0, 33.0, 3.5)
    assert 0 <= spec.indu_lagna_sign <= 11
    assert 0 <= spec.pranapada_lagna_sign <= 11
    assert 0 <= spec.varnada_lagna_sign <= 11

    arudhas = arudha_padas(SAMPLE_LAGNA_LON, SAMPLE_CHART_LONS)
    assert len(arudhas.padas) == 14  # A1..A12 + AL + UL
    assert arudhas.arudha_lagna_sign == arudhas.padas["A1"]
    assert arudhas.upapada_lagna_sign == arudhas.padas["A12"]
    # Verify Swasthe Daraye: Mars is at 298 (Capricorn=9, 10th from Aries=0),
    # so 10th from 10th is 7th from Aries (Libra=6), which triggers the +9 (10th from Libra = Cancer=3) rule!
    assert arudhas.arudha_lagna_sign == 3


# ============================================================================
# 3. PANCHANGA, SAMVATSARA, RITU, HORA, AND MUHURTA TESTS
# ============================================================================


def test_tithi_yoga_karana_invariants() -> None:
    # Shukla Pratipada (elongation = 6 deg)
    t1 = compute_tithi(10.0, 16.0)
    assert t1.number == 1
    assert t1.paksha == "Shukla"
    assert t1.name == "Pratipada"
    assert t1.group == "Nanda"
    assert math.isclose(t1.fraction_elapsed, 0.5, abs_tol=1e-9)

    # Purnima (elongation = 175 deg -> 15th tithi)
    t15 = compute_tithi(0.0, 175.0)
    assert t15.number == 15
    assert t15.paksha == "Shukla"
    assert t15.name == "Purnima"
    assert t15.group == "Purna"

    # Amavasya (elongation = 355 deg -> 30th tithi)
    t30 = compute_tithi(0.0, 355.0)
    assert t30.number == 30
    assert t30.paksha == "Krishna"
    assert t30.name == "Amavasya"
    assert t30.group == "Purna"

    # All 60 Karanas map cleanly with 4 fixed and 56 movable (8 Vishti/Bhadra)
    vishti_count = 0
    fixed_names: list[str] = []
    for k_idx in range(60):
        k = compute_karana(0.0, k_idx * 6.0 + 1.0)
        assert k.number == k_idx + 1
        if k.kind == "Fixed":
            fixed_names.append(k.name)
        if k.is_vishti_bhadra:
            vishti_count += 1
    assert fixed_names == ["Kimstughna", "Shakuni", "Chatushpada", "Naga"]
    assert vishti_count == 8

    # All 27 Yogas
    assert len(YOGA_CATALOG) == 27
    y1 = compute_yoga(2.0, 3.0)
    assert y1.number == 1
    assert y1.name == "Vishkumbha"
    assert y1.is_benefic is False


def test_samvatsara_ayana_ritu_hora_and_muhurta() -> None:
    assert len(SAMVATSARA_NAMES) == 60
    s_1987 = compute_samvatsara(1987, calendar="ce")
    assert s_1987.number == 1
    assert s_1987.name == "Prabhava"

    s_2026 = compute_samvatsara(2026, calendar="ce")
    assert s_2026.number == 40
    assert s_2026.name == "Parabhava"

    ayana_u, ritu_u, _ = compute_ayana_and_ritu(280.0)
    assert ayana_u == "Uttarayana"
    assert ritu_u == "Shishira"

    ayana_d, ritu_d, _ = compute_ayana_and_ritu(100.0)
    assert ayana_d == "Dakshinayana"
    assert ritu_d == "Varsha"

    # Hora table: 24 planetary hours, 1st hour ruled by weekday lord
    sr = 2451545.75
    ss = 2451546.25
    horas = compute_hora_table(sr, ss, vara_index=0)  # Sunday -> starts with Sun
    assert len(horas) == 24
    assert horas[0].ruler == "Sun"
    assert horas[0].is_daytime is True
    assert horas[12].is_daytime is False

    # Muhurta windows on Sunday (vara_index=0) -> Rahu Kalam is 8th octant (last 1.5h of 12h day)
    mw = compute_muhurta_windows(sr, ss, vara_index=0)
    assert math.isclose(mw.rahu_kalam.end_jd, ss, abs_tol=1e-9)
    assert math.isclose(mw.rahu_kalam.duration_minutes, 90.0, abs_tol=1e-9)
    assert math.isclose(mw.abhijit_muhurta.duration_minutes, 48.0, abs_tol=1e-9)
    assert mw.brahma_muhurta.end_jd < sr


# ============================================================================
# 4. MULTI-DASHA (5 LEVELS) AND CHARA KARAKA TESTS
# ============================================================================


def test_vimshottari_dasha_120_year_cycle_and_5_levels() -> None:
    assert math.isclose(sum(VIMSHOTTARI_YEARS.values()), VIMSHOTTARI_TOTAL_YEARS, abs_tol=1e-9)
    birth_jd = 2451545.0
    # At 0.0 deg (start of Ashwini), full 7 years of Ketu remain
    tl = compute_vimshottari_dasha(0.0, birth_jd, year_days=SAVANA_YEAR_DAYS, max_level=3)
    assert tl.opening_lord == "Ketu"
    assert math.isclose(tl.birth_balance_years, 7.0, abs_tol=1e-9)
    total_years = sum(m.duration_years for m in tl.mahadashas)
    assert math.isclose(total_years, 120.0, abs_tol=1e-9)

    # Resolve all 5 levels at birth_jd + 500 days
    lvl5 = resolve_dasha_5_levels(tl, birth_jd + 500.0)
    assert len(lvl5) == 5
    assert [p.level_name for p in lvl5] == [
        "Mahadasha", "Antardasha", "Pratyantardasha", "Sookshma", "Prana",
    ]
    for idx in range(4):
        assert lvl5[idx].start_jd <= lvl5[idx + 1].start_jd
        assert lvl5[idx].end_jd >= lvl5[idx + 1].end_jd
        assert len(lvl5[idx + 1].lords_chain) == idx + 2


def test_ashtottari_yogini_and_chara_dashas() -> None:
    birth_jd = 2451545.0
    ash = compute_ashtottari_dasha(75.0, birth_jd, max_level=2)
    assert len(ash.mahadashas) == 8
    ash_5 = resolve_dasha_5_levels(ash, birth_jd + 100.0)
    assert len(ash_5) == 5

    assert math.isclose(sum(YOGINI_YEARS.values()), YOGINI_TOTAL_YEARS, abs_tol=1e-9)
    yog = compute_yogini_dasha(0.0, birth_jd, max_level=2, cycles=1)
    assert yog.opening_lord == "Bhramari"  # Ashwini=1 -> (1+3)=4 -> Bhramari
    yog_5 = resolve_dasha_5_levels(yog, birth_jd + 100.0)
    assert len(yog_5) == 5

    cha = compute_chara_dasha(SAMPLE_LAGNA_LON, SAMPLE_CHART_LONS, birth_jd, max_level=2)
    assert len(cha.mahadashas) == 12
    assert cha.opening_lord == "Mesha"
    cha_5 = resolve_dasha_5_levels(cha, birth_jd + 200.0)
    assert len(cha_5) == 5


def test_chara_karakas_7_and_8_schemes() -> None:
    ck7 = compute_chara_karakas(SAMPLE_CHART_LONS, scheme="7")
    assert len(ck7) == 7
    assert [c.code for c in ck7] == [r[0] for r in KARAKA_7_ROLES]
    # Mars is at 298 deg (28 deg in Capricorn), highest among the 7 planets -> Atmakaraka
    assert ck7[0].planet == "Mars"
    # Moon is at 33 deg (3 deg in Taurus), lowest among the 7 planets -> Darakaraka
    assert ck7[-1].planet == "Moon"

    ck8 = compute_chara_karakas(SAMPLE_CHART_LONS, scheme="8")
    assert len(ck8) == 8
    assert [c.code for c in ck8] == [r[0] for r in KARAKA_8_ROLES]


# ============================================================================
# 5. SHADBALA, ISHTA/KASHTA PHALA, AND BHAVA BALA TESTS
# ============================================================================


def test_uchcha_bala_at_deep_exaltation_and_debilitation() -> None:
    for planet, exalt_lon in DEEP_EXALTATION_DEG.items():
        assert math.isclose(compute_uchcha_bala(planet, exalt_lon), 60.0, abs_tol=1e-9)
        debil_lon = normalize_degrees(exalt_lon + 180.0)
        assert math.isclose(compute_uchcha_bala(planet, debil_lon), 0.0, abs_tol=1e-9)


def test_dig_bala_directional_peaks_and_zeros() -> None:
    lagna = 0.0  # Aries 0 deg -> 1st=0, 4th=90, 7th=180, 10th=270
    # Jupiter & Mercury peak at 1st (0 deg -> 60 virupas), zero at 7th (180 deg)
    assert math.isclose(compute_dig_bala("Jupiter", 0.0, lagna), 60.0, abs_tol=1e-9)
    assert math.isclose(compute_dig_bala("Mercury", 180.0, lagna), 0.0, abs_tol=1e-9)
    # Sun & Mars peak at 10th (270 deg -> 60 virupas), zero at 4th (90 deg)
    assert math.isclose(compute_dig_bala("Sun", 270.0, lagna), 60.0, abs_tol=1e-9)
    assert math.isclose(compute_dig_bala("Mars", 90.0, lagna), 0.0, abs_tol=1e-9)
    # Saturn peaks at 7th (180 deg -> 60 virupas), zero at 1st (0 deg)
    assert math.isclose(compute_dig_bala("Saturn", 180.0, lagna), 60.0, abs_tol=1e-9)
    assert math.isclose(compute_dig_bala("Saturn", 0.0, lagna), 0.0, abs_tol=1e-9)
    # Moon & Venus peak at 4th (90 deg -> 60 virupas), zero at 10th (270 deg)
    assert math.isclose(compute_dig_bala("Moon", 90.0, lagna), 60.0, abs_tol=1e-9)
    assert math.isclose(compute_dig_bala("Venus", 270.0, lagna), 0.0, abs_tol=1e-9)


def test_parashari_special_aspects_vishesha_drishti() -> None:
    # All planets have full 60-virupa aspect at 180 deg (7th house opposition)
    for g in SEVEN_GRAHAS:
        assert math.isclose(parashari_aspect_virupas(g, 0.0, 180.0), 60.0, abs_tol=1e-9)
    # Mars has full 60-virupa aspect at 90 deg (4th) and 210 deg (8th)
    assert math.isclose(parashari_aspect_virupas("Mars", 0.0, 90.0), 60.0, abs_tol=1e-9)
    assert math.isclose(parashari_aspect_virupas("Mars", 0.0, 210.0), 60.0, abs_tol=1e-9)
    # Jupiter has full 60-virupa aspect at 120 deg (5th) and 240 deg (9th)
    assert math.isclose(parashari_aspect_virupas("Jupiter", 0.0, 120.0), 60.0, abs_tol=1e-9)
    assert math.isclose(parashari_aspect_virupas("Jupiter", 0.0, 240.0), 60.0, abs_tol=1e-9)
    # Saturn has full 60-virupa aspect at 60 deg (3rd) and 270 deg (10th)
    assert math.isclose(parashari_aspect_virupas("Saturn", 0.0, 60.0), 60.0, abs_tol=1e-9)
    assert math.isclose(parashari_aspect_virupas("Saturn", 0.0, 270.0), 60.0, abs_tol=1e-9)


def test_complete_shadbala_and_bhava_bala_summary() -> None:
    summary = compute_shadbala(SAMPLE_CHART_LONS, SAMPLE_LAGNA_LON)
    assert len(summary.planets) == 7
    assert len(summary.bhavas) == 12
    for g in SEVEN_GRAHAS:
        ps = summary.planets[g]
        assert ps.total_virupas > 0.0
        assert math.isclose(ps.total_rupas, ps.total_virupas / 60.0, abs_tol=1e-9)
        assert math.isclose(ps.ishta_phala ** 2, ps.sthana_bala.uchcha_bala * ps.cheshta_bala, abs_tol=1e-6)


# ============================================================================
# 6. ASHTAKAVARGA (337 SAV INVARIANT), SHODHANA, PINDAS, AND GOCHARA VEDHA
# ============================================================================


def test_classical_bav_and_337_sav_bindu_totals() -> None:
    for recipient, expected_sum in EXPECTED_BAV_TOTALS.items():
        actual_sum = sum(len(houses) for houses in BAV_BENEFIC_HOUSES[recipient].values())
        assert actual_sum == expected_sum

    analysis = compute_ashtakavarga(SAMPLE_CHART_LONS, SAMPLE_LAGNA_LON)
    assert analysis.sarvashtakavarga_7_total == EXPECTED_SAV_TOTAL == 337
    assert sum(analysis.sarvashtakavarga_with_lagna) == 337 + 49
    for g in SEVEN_GRAHAS:
        tbl = analysis.bhinna_tables[g]
        assert tbl.total_bindus == EXPECTED_BAV_TOTALS[g]
        assert sum(tbl.trikona_reduced) <= tbl.total_bindus
        assert sum(tbl.ekadhipatya_reduced) <= sum(tbl.trikona_reduced)
        assert tbl.shodhya_pinda == tbl.rasi_pinda + tbl.graha_pinda


def test_gochara_vedha_and_father_son_exemptions() -> None:
    # Natal Moon in Aries (0.0 deg)
    # Suppose Sun is in Gemini (3rd from Moon, benefic, Vedha house = 9th = Sagittarius)
    # Case A: Mars is in Sagittarius (9th) -> obstructs Sun!
    transits_obstructed = {"Sun": 70.0, "Mars": 250.0}
    res_obs = evaluate_gochara_vedha(0.0, transits_obstructed)
    assert res_obs["Sun"].house_from_moon == 3
    assert res_obs["Sun"].is_naturally_benefic_house is True
    assert res_obs["Sun"].is_obstructed_by_vedha is True
    assert res_obs["Sun"].net_favorable is False
    assert "Mars" in res_obs["Sun"].obstructing_planets

    # Case B: Saturn is in Sagittarius (9th) -> Father-Son exemption between Sun and Saturn!
    transits_exempt = {"Sun": 70.0, "Saturn": 250.0}
    res_ex = evaluate_gochara_vedha(0.0, transits_exempt)
    assert res_ex["Sun"].is_naturally_benefic_house is True
    assert res_ex["Sun"].is_obstructed_by_vedha is False
    assert res_ex["Sun"].net_favorable is True
    assert "Saturn" in res_ex["Sun"].exempt_planets

    # Case C: Mercury in Taurus (2nd from Moon, Vedha house = 5th = Leo) with Moon in Leo -> exempt!
    transits_moon_merc = {"Mercury": 40.0, "Moon": 130.0}
    res_mm = evaluate_gochara_vedha(0.0, transits_moon_merc)
    assert res_mm["Mercury"].is_naturally_benefic_house is True
    assert res_mm["Mercury"].is_obstructed_by_vedha is False
    assert "Moon" in res_mm["Mercury"].exempt_planets


# ============================================================================
# 7. UNIFIED CHART ANALYSIS AND DETERMINISTIC SHA-256 RECEIPT
# ============================================================================


def test_unified_compute_vedic_chart_analysis_and_receipt_determinism() -> None:
    chart1 = compute_vedic_chart_analysis(
        SAMPLE_CHART_LONS,
        SAMPLE_LAGNA_LON,
        jd_ut=2451545.0,
        ce_year=2000,
    )
    chart2 = compute_vedic_chart_analysis(
        SAMPLE_CHART_LONS,
        SAMPLE_LAGNA_LON,
        jd_ut=2451545.0,
        ce_year=2000,
    )
    assert isinstance(chart1, VedicChartAnalysis)
    assert len(chart1.receipt_sha256) == 64
    assert chart1.receipt_sha256 == chart2.receipt_sha256
    assert chart1.ashtakavarga.sarvashtakavarga_7_total == 337
    assert chart1.panchanga.samvatsara is not None
    assert len(chart1.vimshottari_active_5_levels) == 5


def test_yuddha_bala_planetary_war_transfer() -> None:
    # Place Mars and Mercury within 0.4 degrees of each other to trigger Graha Yuddha
    war_lons = dict(SAMPLE_CHART_LONS)
    war_lons["Mars"] = 120.1
    war_lons["Mercury"] = 120.5
    summary = compute_shadbala(war_lons, SAMPLE_LAGNA_LON)
    mars_yuddha = summary.planets["Mars"].kala_bala.yuddha_bala
    merc_yuddha = summary.planets["Mercury"].kala_bala.yuddha_bala
    assert mars_yuddha > 0.0
    assert math.isclose(mars_yuddha + merc_yuddha, 0.0, abs_tol=1e-9)


def test_jaimini_scorpio_and_aquarius_dual_lordship_rules() -> None:
    # Rule 1: If Mars is in Scorpio (215 deg) and Ketu is outside (35 deg), Ketu is the effective lord
    lons_rule1 = dict(SAMPLE_CHART_LONS)
    lons_rule1["Mars"] = 215.0
    lons_rule1["Ketu"] = 35.0
    assert resolve_jaimini_sign_lord(7, lons_rule1) == "Ketu"

    # Rule 2: Neither in Scorpio; Mars conjoined with Sun & Venus in Aries, Ketu alone in Gemini -> Mars wins
    lons_rule2 = {
        "Sun": 10.0,
        "Venus": 12.0,
        "Mars": 15.0,
        "Ketu": 70.0,
        "Moon": 100.0,
        "Mercury": 140.0,
        "Jupiter": 170.0,
        "Saturn": 280.0,
        "Rahu": 250.0,
    }
    assert resolve_jaimini_sign_lord(7, lons_rule2) == "Mars"


def test_trikona_and_ekadhipatya_shodhana_edge_cases() -> None:
    # Trikona reduction: Fire signs (0, 4, 8) have (5, 3, 6) -> min is 3 -> reduced to (2, 0, 3)
    raw = (5, 4, 2, 0, 3, 4, 2, 6, 6, 4, 2, 3)
    trik = trikona_shodhana(raw)
    assert (trik[0], trik[4], trik[8]) == (2, 0, 3)
    assert (trik[1], trik[5], trik[9]) == (0, 0, 0)
    assert (trik[2], trik[6], trik[10]) == (0, 0, 0)
    assert (trik[3], trik[7], trik[11]) == (0, 6, 3)

    # Ekadhipatya reduction: Mars owns (0, 7) with values (2, 6).
    # If neither 0 nor 7 is occupied, larger (6 in sign 7) becomes smaller (2) and smaller (sign 0) becomes 0
    ek_unocc = ekadhipatya_shodhana(trik, frozenset())
    assert ek_unocc[0] == 0
    assert ek_unocc[7] == 2

    # If both 0 and 7 are occupied, neither changes
    ek_both_occ = ekadhipatya_shodhana(trik, frozenset({0, 7}))
    assert ek_both_occ[0] == 2
    assert ek_both_occ[7] == 6


def test_engine_de440_to_jyotish_integration() -> None:
    import os
    from datetime import datetime, timezone
    from pathlib import Path
    from ephemeris_oss import EarthOrientation, Engine

    de440 = os.getenv("EPHEMERIS_OSS_DE440_KERNEL")
    if not de440 or not Path(de440).is_file():
        pytest.skip("DE440 kernel path not configured")

    eop = EarthOrientation(dut1_seconds=0.0, xp_arcsec=0.0, yp_arcsec=0.0, version="test-zero")
    instant = datetime(2026, 10, 15, 12, 0, 0, tzinfo=timezone.utc)
    with Engine.load(kernels={"DE440": Path(de440)}, eop=eop) as eng:
        pos = eng.positions(
            instant,
            bodies=("sun", "moon", "mars", "mercury", "jupiter", "venus", "saturn"),
            ayanamsa="lahiri",
        )
        rahu = eng.nodes(instant, kind="mean", ayanamsa="lahiri")
        houses = eng.houses(instant, lat=28.6139, lon=77.2090, system="placidus", ayanamsa="lahiri")
        ayan = eng.ayanamsa(instant, system="lahiri")

    planet_lons = {k.capitalize(): float(v["longitude_deg"]) for k, v in pos.value.items()}
    planet_lons["Rahu"] = float(rahu.value)
    planet_lons["Ketu"] = normalize_degrees(float(rahu.value) + 180.0)
    assert not isinstance(houses.value, jyotish.VedicChartAnalysis)
    asc_deg = float(houses.value.ascendant_deg)  # type: ignore[union-attr]

    chart = compute_vedic_chart_analysis(
        planet_lons,
        asc_deg,
        jd_ut=2461329.0,
        ayanamsa_deg=float(ayan.value),
        ayanamsa_system="lahiri",
        ce_year=2026,
    )
    assert chart.ashtakavarga.sarvashtakavarga_7_total == 337
    assert chart.panchanga.samvatsara is not None
    assert chart.panchanga.samvatsara.name == "Parabhava"
    assert len(chart.receipt_sha256) == 64

