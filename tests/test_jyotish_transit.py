"""Comprehensive unit and mathematical invariant tests for `ephemeris_oss.jyotish_transit`.

Tests cover:
- Electional Muhurta Evaluator and Window Scanner (`muhurta_search.py`):
  Panchaka Rahita (all 9 remainders), Siddha / Amrita Siddhi / Sarvartha Siddhi /
  Ravi Pushya / Guru Pushya / Dwipushkara / Tripushkara Yogas, Dagdha Rasi,
  Chandrabala (all 12 houses), Gandanta junctions, instant scoring, and window scanning.
- Kerala Prashna Marga Sphutas, 11 Classical Upagrahas, and Horary Arudha (`prashna.py`):
  5 Solar Upagrahas (Dhuma, Vyatipata, Parivesha, Indrachapa, Upaketu mathematical
  identities), 6 Kalavela Upagrahas (Gulika/Mandi, Kala, Mrityu, Ardhaprahara,
  Yamaghantaka, ochcha across day and night octants), 9 Prashna Sphutas,
  Shirshodaya/Prishtodaya/Ubhayodaya and Dhatu/Moola/Jeeva sign classifications,
  and 108-seed Horary Arudha & Chatra Rasi.
- Ashtakavarga Kakshya, Sarvatobhadra 9x9 Chakra, and Kota Chakra (`chakras.py`):
  8-fold Kakshya lords (Saturn..Lagna) and 3.75-degree boundaries, Prastara Ashtakavarga
  337-bindu conservation, 81-cell Sarvatobhadra Chakra partition (28+16+20+12+5=81)
  and 3-way Vedha ray symmetry (Front, Left, Right), and 28-nakshatra Kota Chakra
  concentric zones (Stambha 4, Madhya 8, Prakaara 8, Bahya 8) and Pravesha/Nirgamana paths.
"""

from __future__ import annotations

import math
import pytest

from ephemeris_oss.jyotish_transit import (
    AMRITA_SIDDHI_EXCLUDED_PAKSHA_TITHI,
    AMRITA_SIDDHI_NAKSHATRA,
    DAGDHA_RASI_BY_PAKSHA_TITHI,
    DHATU_SIGNS,
    JEEVA_SIGNS,
    KAKSHYA_LORDS,
    KAKSHYA_SPAN_DEG,
    KALAVELA_UPAGRAHA_NAMES,
    KOTA_BAHYA_OFFSETS,
    KOTA_MADHYA_OFFSETS,
    KOTA_NIRGAMANA_OFFSETS,
    KOTA_PRAKAARA_OFFSETS,
    KOTA_PRAVESHA_OFFSETS,
    KOTA_STAMBHA_OFFSETS,
    MOOLA_SIGNS,
    PRISHTODAYA_SIGNS,
    SARVARTHA_SIDDHI_NAKSHATRAS,
    SARVATOBHADRA_28_NAKSHATRAS,
    SHIRSHODAYA_SIGNS,
    SOLAR_UPAGRAHA_NAMES,
    UBHAYODAYA_SIGNS,
    UPAGRAHA_11_NAMES,
    build_sarvatobhadra_grid,
    classify_prashna_sign,
    compute_11_upagrahas,
    compute_jyotish_transit_suite,
    compute_kalavela_upagrahas,
    compute_prashna_analysis,
    compute_prashna_arudha,
    compute_prashna_sphutas,
    compute_sarvatobhadra_vedha,
    compute_solar_upagrahas,
    evaluate_chandrabala,
    evaluate_kakshya,
    evaluate_kota_chakra,
    evaluate_panchaka,
    evaluate_sarvatobhadra_transits,
    evaluate_siddha_yogas,
    is_gandanta_degree,
    prastara_ashtakavarga,
    scan_muhurta_windows,
    score_muhurta_instant,
)

SAMPLE_NATAL_LONGITUDES: dict[str, float] = {
    "Sun": 45.0,
    "Moon": 100.0,
    "Mars": 15.0,
    "Mercury": 60.0,
    "Jupiter": 95.0,
    "Venus": 35.0,
    "Saturn": 285.0,
    "Rahu": 190.0,
    "Ketu": 10.0,
}


# ============================================================================
# 1. Electional Muhurta Search Engine Tests (`muhurta_search.py`)
# ============================================================================


def test_panchaka_mrityu_remainder_1() -> None:
    """Remainder 1 produces Mrityu Panchaka (inauspicious)."""
    res = evaluate_panchaka(tithi_num=7, vara_num=1, nakshatra_num=1, lagna_sign=1)  # total=10, 10%9=1
    assert res.remainder == 1
    assert res.name == "Mrityu Panchaka"
    assert res.is_auspicious is False


def test_panchaka_agni_remainder_2() -> None:
    """Remainder 2 produces Agni Panchaka (inauspicious)."""
    res = evaluate_panchaka(tithi_num=8, vara_num=1, nakshatra_num=1, lagna_sign=1)  # total=11, 11%9=2
    assert res.remainder == 2
    assert res.name == "Agni Panchaka"
    assert res.is_auspicious is False


def test_panchaka_raja_remainder_4() -> None:
    """Remainder 4 produces Raja Panchaka (inauspicious)."""
    res = evaluate_panchaka(tithi_num=1, vara_num=1, nakshatra_num=1, lagna_sign=1)  # total=4, 4%9=4
    assert res.remainder == 4
    assert res.name == "Raja Panchaka"
    assert res.is_auspicious is False


def test_panchaka_chora_remainder_6() -> None:
    """Remainder 6 produces Chora Panchaka (inauspicious)."""
    res = evaluate_panchaka(tithi_num=3, vara_num=1, nakshatra_num=1, lagna_sign=1)  # total=6, 6%9=6
    assert res.remainder == 6
    assert res.name == "Chora Panchaka"
    assert res.is_auspicious is False


def test_panchaka_roga_remainder_8() -> None:
    """Remainder 8 produces Roga Panchaka (inauspicious)."""
    res = evaluate_panchaka(tithi_num=5, vara_num=1, nakshatra_num=1, lagna_sign=1)  # total=8, 8%9=8
    assert res.remainder == 8
    assert res.name == "Roga Panchaka"
    assert res.is_auspicious is False


def test_panchaka_shuddha_remainders_0_3_5_7() -> None:
    """Remainders 0, 3, 5, 7 produce Shuddha (auspicious)."""
    for tithi, exp_rem in ((6, 0), (9, 3), (2, 5), (4, 7)):
        res = evaluate_panchaka(tithi_num=tithi, vara_num=1, nakshatra_num=1, lagna_sign=1)
        assert res.remainder == exp_rem
        assert res.name == "Shuddha"
        assert res.is_auspicious is True


def test_panchaka_input_validation() -> None:
    """Out-of-range Panchaka inputs raise ValueError."""
    with pytest.raises(ValueError):
        evaluate_panchaka(0, 1, 1, 1)
    with pytest.raises(ValueError):
        evaluate_panchaka(31, 1, 1, 1)
    with pytest.raises(ValueError):
        evaluate_panchaka(1, 8, 1, 1)
    with pytest.raises(ValueError):
        evaluate_panchaka(1, 1, 28, 1)
    with pytest.raises(ValueError):
        evaluate_panchaka(1, 1, 1, 13)


def test_sarvartha_siddhi_all_weekdays() -> None:
    """Verify Sarvartha Siddhi Yoga matches the catalog for every weekday 0..6."""
    for v_idx, nak_set in SARVARTHA_SIDDHI_NAKSHATRAS.items():
        for n_idx in range(27):
            ev = evaluate_siddha_yogas(v_idx, n_idx, tithi_num=3)
            assert ev.sarvartha_siddhi is (n_idx in nak_set)


def test_amrita_siddhi_all_weekdays_and_tithi_exceptions() -> None:
    """Verify Amrita Siddhi Yoga across all 7 weekdays and its Tithi exceptions."""
    for v_idx, target_nak in AMRITA_SIDDHI_NAKSHATRA.items():
        bad_tithi = AMRITA_SIDDHI_EXCLUDED_PAKSHA_TITHI[v_idx]
        good_tithi = 1 if bad_tithi != 1 else 2
        ev_good = evaluate_siddha_yogas(v_idx, target_nak, tithi_num=good_tithi)
        assert ev_good.amrita_siddhi is True
        assert ev_good.amrita_siddhi_tithi_afflicted is False

        ev_bad = evaluate_siddha_yogas(v_idx, target_nak, tithi_num=bad_tithi)
        assert ev_bad.amrita_siddhi is False
        assert ev_bad.amrita_siddhi_tithi_afflicted is True


def test_siddha_yogas_guru_and_ravi_pushya() -> None:
    """Verify Guru Pushya (Thursday + Pushya) and Ravi Pushya (Sunday + Pushya)."""
    guru = evaluate_siddha_yogas(vara_index=4, nakshatra_index=7, tithi_num=3)
    assert guru.guru_pushya is True
    assert guru.ravi_pushya is False
    assert "Guru Pushya Yoga" in guru.active_yogas

    ravi = evaluate_siddha_yogas(vara_index=0, nakshatra_index=7, tithi_num=3)
    assert ravi.ravi_pushya is True
    assert ravi.guru_pushya is False
    assert "Ravi Pushya Yoga" in ravi.active_yogas


def test_dwipushkara_and_tripushkara_yogas() -> None:
    """Verify Dwipushkara and Tripushkara Yogas on Bhadra tithi (2, 7, 12) + Sun/Tue/Sat."""
    dwi = evaluate_siddha_yogas(vara_index=0, nakshatra_index=4, tithi_num=2)
    assert dwi.dwipushkara is True
    assert dwi.tripushkara is False
    assert "Dwipushkara Yoga" in dwi.active_yogas

    tri = evaluate_siddha_yogas(vara_index=2, nakshatra_index=2, tithi_num=22)
    assert tri.tripushkara is True
    assert tri.dwipushkara is False
    assert "Tripushkara Yoga" in tri.active_yogas


def test_siddha_yogas_input_validation() -> None:
    """Invalid weekday, nakshatra, or tithi in `evaluate_siddha_yogas` raises ValueError."""
    with pytest.raises(ValueError):
        evaluate_siddha_yogas(-1, 0, 1)
    with pytest.raises(ValueError):
        evaluate_siddha_yogas(0, 27, 1)
    with pytest.raises(ValueError):
        evaluate_siddha_yogas(0, 0, 31)


def test_dagdha_rasi_all_paksha_tithis() -> None:
    """Verify burnt signs (Dagdha Rasi) for all 15 Paksha Tithis."""
    for pt in range(1, 15):
        expected_signs = DAGDHA_RASI_BY_PAKSHA_TITHI[pt]
        assert len(expected_signs) >= 2
        ev = evaluate_siddha_yogas(1, 3, tithi_num=pt, moon_sign_index=expected_signs[0])
        assert ev.moon_in_dagdha_rasi is True
    ev_15 = evaluate_siddha_yogas(1, 3, tithi_num=15, moon_sign_index=0)
    assert ev_15.dagdha_rasis == ()
    assert ev_15.moon_in_dagdha_rasi is False


def test_chandrabala_auspicious_houses() -> None:
    """Houses 1, 3, 6, 7, 10, 11 from natal Moon are auspicious with weight 1.0."""
    for h in (1, 3, 6, 7, 10, 11):
        res = evaluate_chandrabala(1, h)
        assert res.house_from_natal_moon == h
        assert res.is_auspicious is True
        assert res.is_inauspicious is False
        assert res.score_weight == 1.0


def test_chandrabala_inauspicious_and_ashtama_houses() -> None:
    """Houses 4, 8, 12 from natal Moon are inauspicious with weight 0.0; 8th is Ashtama Chandra."""
    for h in (4, 8, 12):
        res = evaluate_chandrabala(1, h)
        assert res.house_from_natal_moon == h
        assert res.is_auspicious is False
        assert res.is_inauspicious is True
        assert res.score_weight == 0.0
    assert "Ashtama" in evaluate_chandrabala(1, 8).status


def test_chandrabala_moderate_houses_and_validation() -> None:
    """Houses 2, 5, 9 from natal Moon are moderate with weight 0.6; invalid signs raise ValueError."""
    for h in (2, 5, 9):
        res = evaluate_chandrabala(1, h)
        assert res.house_from_natal_moon == h
        assert res.status == "Moderate"
        assert res.score_weight == 0.6
    with pytest.raises(ValueError):
        evaluate_chandrabala(-1, 1)
    with pytest.raises(ValueError):
        evaluate_chandrabala(1, 13)


def test_gandanta_junction_all_three_water_fire_boundaries() -> None:
    """Verify 48-arcminute (0.8 deg) Gandanta junction detection at 0, 120, and 240 degrees."""
    for junction in (0.0, 120.0, 240.0, 360.0):
        assert is_gandanta_degree(junction - 0.5) is True
        assert is_gandanta_degree(junction + 0.5) is True
        assert is_gandanta_degree(junction + 0.79) is True
        assert is_gandanta_degree(junction + 0.85) is False
    with pytest.raises(ValueError):
        is_gandanta_degree(10.0, orb_deg=0.0)


def test_score_muhurta_instant_auspicious_vs_afflicted() -> None:
    """Auspicious Guru Pushya Abhijit instant scores significantly higher than Gandanta/Vishti/Rahu Kalam."""
    sr_jd = 2451548.75
    ss_jd = 2451549.25
    good_ev = score_muhurta_instant(
        jd_ut=2451549.0,
        sun_lon_deg=60.0,
        moon_lon_deg=96.0,
        lagna_lon_deg=45.0,
        natal_moon_lon_deg=96.0,
        sunrise_jd_ut=sr_jd,
        sunset_jd_ut=ss_jd,
        vara_index=4,
    )
    assert good_ev.score >= 80.0
    assert good_ev.grade == "Uttama (Excellent)"
    assert good_ev.is_recommended is True
    assert good_ev.in_abhijit_muhurta is True
    assert good_ev.siddha_yogas.guru_pushya is True
    assert len(good_ev.receipt_sha256) == 64

    bad_ev = score_muhurta_instant(
        jd_ut=2451545.20,
        sun_lon_deg=77.9,
        moon_lon_deg=119.9,
        lagna_lon_deg=240.1,
        natal_moon_lon_deg=245.0,
        sunrise_jd_ut=2451544.75,
        sunset_jd_ut=2451545.25,
        vara_index=0,
    )
    assert bad_ev.moon_gandanta is True
    assert bad_ev.lagna_gandanta is True
    assert bad_ev.in_rahu_kalam is True
    assert bad_ev.is_recommended is False
    assert bad_ev.grade == "Varjya (Avoid)"
    assert good_ev.score > bad_ev.score + 50.0


def test_scan_muhurta_windows_aggregation_and_empty_error() -> None:
    """Verify `scan_muhurta_windows` aggregates recommended intervals and rejects empty samples."""
    with pytest.raises(ValueError):
        scan_muhurta_windows([])

    sr = 2451548.75
    ss = 2451549.25
    samples = [
        {
            "jd_ut": sr + i * (0.5 / 10.0),
            "sun_lon_deg": 60.0 + i * 0.05,
            "moon_lon_deg": 95.0 + i * 0.6,
            "lagna_lon_deg": 35.0 + i * 15.0,
            "sunrise_jd_ut": sr,
            "sunset_jd_ut": ss,
            "vara_index": 4,
        }
        for i in range(10)
    ]
    report = scan_muhurta_windows(samples, natal_moon_lon_deg=95.0, threshold_score=65.0)
    assert report.sample_count == 10
    assert len(report.instants) == 10
    assert len(report.recommended_windows) >= 1
    assert report.best_instant.score >= 80.0
    assert len(report.receipt_sha256) == 64


# ============================================================================
# 2. Kerala Prashna Marga Sphutas & 11 Upagrahas Tests (`prashna.py`)
# ============================================================================


def test_solar_upagraha_dhuma() -> None:
    """Dhuma = (Sun + 133 deg 20 min) % 360."""
    solar = compute_solar_upagrahas(30.0)
    assert math.isclose(solar["Dhuma"].longitude_deg, 163.33333333333334, abs_tol=1e-9)
    assert solar["Dhuma"].sign_name == "Kanya"


def test_solar_upagraha_vyatipata() -> None:
    """Vyatipata = (360 - Dhuma) % 360."""
    solar = compute_solar_upagrahas(30.0)
    assert math.isclose((solar["Dhuma"].longitude_deg + solar["Vyatipata"].longitude_deg) % 360.0, 0.0, abs_tol=1e-9)


def test_solar_upagraha_parivesha() -> None:
    """Parivesha = (Vyatipata + 180) % 360."""
    solar = compute_solar_upagrahas(30.0)
    assert math.isclose((solar["Parivesha"].longitude_deg - solar["Vyatipata"].longitude_deg) % 360.0, 180.0, abs_tol=1e-9)


def test_solar_upagraha_indrachapa_kodanda() -> None:
    """Indrachapa (Kodanda) = (360 - Parivesha) % 360."""
    solar = compute_solar_upagrahas(30.0)
    assert solar["Indrachapa"].alias == "Kodanda"
    assert math.isclose((solar["Indrachapa"].longitude_deg + solar["Parivesha"].longitude_deg) % 360.0, 0.0, abs_tol=1e-9)


def test_solar_upagraha_upaketu_sikhi() -> None:
    """Upaketu (Sikhi) = (Indrachapa + 16 deg 40 min) % 360 == (Sun - 30) % 360."""
    for sun_lon in (0.0, 30.0, 145.5, 290.0):
        solar = compute_solar_upagrahas(sun_lon)
        assert solar["Upaketu"].alias == "Sikhi"
        assert math.isclose(solar["Upaketu"].longitude_deg, (sun_lon - 30.0) % 360.0, abs_tol=1e-9)


def test_kalavela_upagrahas_daytime_gulika_segments() -> None:
    """Daytime Gulika octants on Sun(0)..Sat(6) are (7, 6, 5, 4, 3, 2, 1)."""
    expected_day_gulika = (7, 6, 5, 4, 3, 2, 1)
    for w in range(7):
        day_kv = compute_kalavela_upagrahas(2451544.75, 2451545.25, is_daytime=True, vara_index=w)
        assert day_kv["Gulika"].octant_number == expected_day_gulika[w]


def test_kalavela_upagrahas_nighttime_gulika_segments() -> None:
    """Nighttime Gulika octants (5th lord starts) on Sun(0)..Sat(6) are (3, 2, 1, 7, 6, 5, 4)."""
    expected_night_gulika = (3, 2, 1, 7, 6, 5, 4)
    for w in range(7):
        night_kv = compute_kalavela_upagrahas(2451544.75, 2451545.25, is_daytime=False, vara_index=w)
        assert night_kv["Gulika"].octant_number == expected_night_gulika[w]


def test_kalavela_custom_ascendant_callback_and_validation() -> None:
    """Verify `compute_kalavela_upagrahas` supports a custom `ascendant_fn` and validates JD order."""
    with pytest.raises(ValueError):
        compute_kalavela_upagrahas(2451545.25, 2451544.75)
    with pytest.raises(ValueError):
        compute_kalavela_upagrahas(2451544.75, 2451545.25, next_sunrise_jd=2451545.0)

    kv = compute_kalavela_upagrahas(
        2451544.75,
        2451545.25,
        vara_index=6,  # Saturday -> Gulika is octant 1 (start_jd = 2451544.75)
        ascendant_fn=lambda jd: 123.45,
    )
    assert math.isclose(kv["Gulika"].longitude_deg, 123.45, abs_tol=1e-9)


def test_compute_11_upagrahas_completeness() -> None:
    """Verify `compute_11_upagrahas` returns all 11 canonical Upagrahas plus Mandi."""
    upa = compute_11_upagrahas(
        sun_lon_deg=50.0,
        sunrise_jd=2451544.75,
        sunset_jd=2451545.25,
        jd_ut=2451545.0,
        lagna_lon_deg=120.0,
    )
    assert len(upa.all_11_longitudes) == 11
    assert tuple(upa.all_11_longitudes.keys()) == UPAGRAHA_11_NAMES
    assert 0.0 <= upa.ochcha.longitude_deg < 360.0
    assert 0.0 <= upa.mandi.longitude_deg < 360.0


def test_prashna_trisphuta_chatusphuta_panchasphuta() -> None:
    """Verify Trisphuta, Chatusphuta, and Panchasphuta formulas."""
    sph = compute_prashna_sphutas(lagna_deg=35.0, sun_deg=50.0, moon_deg=110.0, gulika_deg=200.0, rahu_deg=80.0)
    assert math.isclose(sph.trisphuta.longitude_deg, 345.0)
    assert math.isclose(sph.chatusphuta.longitude_deg, 35.0)
    assert math.isclose(sph.panchasphuta.longitude_deg, 115.0)


def test_prashna_prana_deha_mrityu_sphutas() -> None:
    """Verify Prana (5*Lagna + Gulika), Deha (8*Moon + Gulika), and Mrityu (7*Gulika + Sun) Sphutas."""
    sph = compute_prashna_sphutas(lagna_deg=20.0, sun_deg=40.0, moon_deg=30.0, gulika_deg=10.0)
    assert math.isclose(sph.prana_sphuta.longitude_deg, 110.0)
    assert math.isclose(sph.deha_sphuta.longitude_deg, 250.0)
    assert math.isclose(sph.mrityu_sphuta.longitude_deg, 110.0)
    assert sph.vitality_conjunction_warning is True  # Prana and Mrityu both at 110 deg (Ashlesha)


def test_prashna_tithi_kshetra_beeja_sphutas() -> None:
    """Verify Tithi Sphuta, Kshetra Sphuta (female fertility), and Beeja Sphuta (male virility)."""
    sph = compute_prashna_sphutas(
        lagna_deg=30.0,
        sun_deg=40.0,
        moon_deg=100.0,
        gulika_deg=10.0,
        mars_deg=25.0,
        jupiter_deg=85.0,
        venus_deg=55.0,
    )
    assert math.isclose(sph.tithi_sphuta.longitude_deg, 90.0)
    assert math.isclose(sph.kshetra_sphuta.longitude_deg, 210.0)
    assert math.isclose(sph.beeja_sphuta.longitude_deg, 180.0)


def test_prashna_sign_udaya_classifications() -> None:
    """Verify Shirshodaya (2,4,5,6,7,10), Prishtodaya (0,1,3,8,9), and Ubhayodaya (11)."""
    for idx in SHIRSHODAYA_SIGNS:
        assert classify_prashna_sign(idx).udaya_type == "Shirshodaya"
    for idx in PRISHTODAYA_SIGNS:
        assert classify_prashna_sign(idx).udaya_type == "Prishtodaya"
    assert classify_prashna_sign(11).udaya_type == "Ubhayodaya"
    with pytest.raises(ValueError):
        classify_prashna_sign(12)


def test_prashna_sign_dhatu_moola_jeeva_classifications() -> None:
    """Verify Dhatu (Movable), Moola (Fixed), and Jeeva (Dual) across all 12 signs."""
    for idx in DHATU_SIGNS:
        assert classify_prashna_sign(idx).substance_type == "Dhatu"
    for idx in MOOLA_SIGNS:
        assert classify_prashna_sign(idx).substance_type == "Moola"
    for idx in JEEVA_SIGNS:
        assert classify_prashna_sign(idx).substance_type == "Jeeva"


def test_prashna_arudha_108_seeds_and_validation() -> None:
    """Verify 108-seed Horary Arudha and Veethya/Chatra Rasi across all 3 solar streets."""
    with pytest.raises(ValueError):
        compute_prashna_arudha(0, 0.0, 0.0)
    with pytest.raises(ValueError):
        compute_prashna_arudha(109, 0.0, 0.0)

    ar1 = compute_prashna_arudha(seed_number=15, lagna_lon_deg=45.0, sun_lon_deg=50.0)
    assert ar1.arudha_sign_name == "Mithuna"
    assert ar1.veethya_sign_index == 0

    ar2 = compute_prashna_arudha(seed_number=24, lagna_lon_deg=10.0, sun_lon_deg=180.0)
    assert ar2.arudha_sign_name == "Meena"
    assert ar2.veethya_sign_index == 2

    ar3 = compute_prashna_arudha(seed_number=1, lagna_lon_deg=10.0, sun_lon_deg=300.0)
    assert ar3.arudha_sign_name == "Mesha"
    assert ar3.veethya_sign_index == 1


def test_compute_prashna_analysis_receipt_and_missing_planet_error() -> None:
    """Verify `compute_prashna_analysis` produces a 64-hex SHA-256 receipt and validates inputs."""
    with pytest.raises(ValueError):
        compute_prashna_analysis({"Sun": 10.0}, 45.0)
    analysis = compute_prashna_analysis(SAMPLE_NATAL_LONGITUDES, 45.0, seed_number=15)
    assert len(analysis.receipt_sha256) == 64


# ============================================================================
# 3. Ashtakavarga Kakshya, Sarvatobhadra 9x9 Chakra & Kota Chakra (`chakras.py`)
# ============================================================================


def test_prastara_ashtakavarga_bindu_conservation() -> None:
    """Verify Prastara Ashtakavarga tables preserve the 337-bindu BPHS invariant and Kakshya order."""
    prastara = prastara_ashtakavarga(SAMPLE_NATAL_LONGITUDES, 15.0)
    assert prastara.sarvashtakavarga_7_total == 337
    for tbl in prastara.tables.values():
        assert tbl.kakshya_lords == KAKSHYA_LORDS
        for s_idx in range(12):
            col_sum = sum(tbl.kakshya_grid[k_idx][s_idx] for k_idx in range(8))
            assert col_sum == tbl.sign_totals[s_idx]


def test_evaluate_kakshya_eight_segments_per_sign() -> None:
    """Verify each of the 8 Kakshyas of 3.75 deg maps to Saturn..Lagna in order."""
    prastara = prastara_ashtakavarga(SAMPLE_NATAL_LONGITUDES, 15.0)
    for k_idx, expected_lord in enumerate(KAKSHYA_LORDS):
        lon = 60.0 + k_idx * KAKSHYA_SPAN_DEG + 1.875
        ev = evaluate_kakshya("Jupiter", lon, prastara=prastara)
        assert ev.sign_index == 2
        assert ev.kakshya_index == k_idx
        assert ev.kakshya_number == k_idx + 1
        assert ev.kakshya_lord == expected_lord
        assert math.isclose(ev.fraction_elapsed, 0.5, abs_tol=1e-9)
        assert isinstance(ev.has_bindu, bool)


def test_evaluate_kakshya_calling_conventions() -> None:
    """Verify `evaluate_kakshya` works with direct `PrastaraTable` or `planet_longitudes`."""
    prastara = prastara_ashtakavarga(SAMPLE_NATAL_LONGITUDES, 15.0)
    ev1 = evaluate_kakshya(10.0, prastara=prastara.tables["Saturn"])
    ev2 = evaluate_kakshya(10.0, recipient="Saturn", planet_longitudes=SAMPLE_NATAL_LONGITUDES, lagna_lon_deg=15.0)
    assert ev1.has_bindu == ev2.has_bindu
    assert ev1.kakshya_lord == "Mars"  # 10.0 deg is in 7.5..11.25 (index 2 = Mars)
    with pytest.raises(ValueError):
        evaluate_kakshya("Saturn")
    with pytest.raises(ValueError):
        evaluate_kakshya(10.0, recipient="Pluto", prastara=prastara)


def test_sarvatobhadra_grid_81_cell_partition() -> None:
    """Verify the 9x9 Sarvatobhadra Chakra has 81 cells: 28 Nakshatras, 16 Vowels, 20 Consonants, 12 Rasis, 5 Tithis."""
    grid = build_sarvatobhadra_grid()
    counts: dict[str, int] = {"Nakshatra": 0, "Vowel": 0, "Consonant": 0, "Rasi": 0, "Tithi": 0}
    for r in range(9):
        for c in range(9):
            counts[grid[r][c].cell_type] += 1
    assert counts == {"Nakshatra": 28, "Vowel": 16, "Consonant": 20, "Rasi": 12, "Tithi": 5}
    assert sum(counts.values()) == 81


def test_sarvatobhadra_3way_vedha_geometric_symmetry() -> None:
    """Verify Front Vedha involution and Left/Right Vedha reciprocity across all 28 Nakshatras."""
    grid = build_sarvatobhadra_grid()
    for idx, n_name in enumerate(SARVATOBHADRA_28_NAKSHATRAS):
        rays = compute_sarvatobhadra_vedha(idx, grid=grid)
        assert rays.source_nakshatra == n_name
        opposite_rays = compute_sarvatobhadra_vedha(rays.front_vedha_nakshatra, grid=grid)
        assert opposite_rays.front_vedha_nakshatra == n_name

        left_target_rays = compute_sarvatobhadra_vedha(rays.left_vedha_nakshatra, grid=grid)
        assert left_target_rays.right_vedha_nakshatra == n_name
    with pytest.raises(ValueError):
        compute_sarvatobhadra_vedha(28)
    with pytest.raises(ValueError):
        compute_sarvatobhadra_vedha("InvalidStar")


def test_sarvatobhadra_transit_directional_motion_rules() -> None:
    """Verify direct vs retrograde vs luminary Vedha activation in `evaluate_sarvatobhadra_transits`."""
    sbc = evaluate_sarvatobhadra_transits(
        natal_moon_lon_deg=40.0,
        transit_longitudes={"Sun": 40.0, "Saturn": 220.0, "Jupiter": 100.0},
        planet_speeds_deg_per_day={"Sun": 1.0, "Saturn": -0.05, "Jupiter": 0.12},
        janma_tithi_group="Nanda",
        nama_akshara="r",
    )
    assert sbc.planet_transits["Sun"].motion == "luminary"
    assert len(sbc.planet_transits["Sun"].active_vedha_nakshatras) == 3
    assert sbc.planet_transits["Saturn"].motion == "retrograde"
    assert len(sbc.planet_transits["Saturn"].active_vedha_nakshatras) == 2
    assert sbc.planet_transits["Jupiter"].motion == "direct"
    assert len(sbc.planet_transits["Jupiter"].active_vedha_nakshatras) == 2


def test_kota_chakra_zone_and_path_partition() -> None:
    """Verify Kota Chakra partitions the 28 Nakshatras into Stambha(4), Madhya(8), Prakaara(8), Bahya(8)."""
    assert len(KOTA_STAMBHA_OFFSETS) == 4
    assert len(KOTA_MADHYA_OFFSETS) == 8
    assert len(KOTA_PRAKAARA_OFFSETS) == 8
    assert len(KOTA_BAHYA_OFFSETS) == 8
    assert len(KOTA_PRAVESHA_OFFSETS) == 12
    assert len(KOTA_NIRGAMANA_OFFSETS) == 16

    kota_siege = evaluate_kota_chakra(
        natal_moon_lon_deg=100.0,
        transit_longitudes={"Saturn": 100.0, "Mars": 200.0},
    )
    assert kota_siege.kota_swami == "Moon"
    assert kota_siege.kota_paala == "Saturn"
    assert kota_siege.stambha_malefics == ("Saturn",)
    assert kota_siege.is_fortress_besieged is True


def test_kota_chakra_contested_and_protected_states() -> None:
    """Verify Contested, Guarded Alert, and Protected states in `evaluate_kota_chakra`."""
    kota_contested = evaluate_kota_chakra(100.0, {"Saturn": 100.0, "Jupiter": 100.0})
    assert kota_contested.is_fortress_besieged is False
    assert "Contested" in kota_contested.vulnerability_status

    kota_alert = evaluate_kota_chakra(100.0, {"Saturn": 113.0})  # Ashlesha = offset 2 (Madhya, Pravesha)
    assert kota_alert.is_fortress_besieged is False
    assert "Guarded Alert" in kota_alert.vulnerability_status

    kota_safe = evaluate_kota_chakra(100.0, {"Jupiter": 100.0})
    assert kota_safe.is_fortress_besieged is False
    assert "Protected" in kota_safe.vulnerability_status


def test_unified_jyotish_transit_suite_determinism() -> None:
    """Verify `compute_jyotish_transit_suite` produces identical SHA-256 receipts across repeated runs."""
    with pytest.raises(ValueError):
        compute_jyotish_transit_suite({"Sun": 10.0}, 45.0)
    r1 = compute_jyotish_transit_suite(SAMPLE_NATAL_LONGITUDES, 45.0, seed_number=27)
    r2 = compute_jyotish_transit_suite(SAMPLE_NATAL_LONGITUDES, 45.0, seed_number=27)
    assert r1.receipt_sha256 == r2.receipt_sha256
    assert len(r1.kakshya_transits) == 7
    assert r1.prastara.sarvashtakavarga_7_total == 337
