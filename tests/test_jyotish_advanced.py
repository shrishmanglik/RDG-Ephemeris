"""Unit and invariant test suite for ephemeris_oss.jyotish_advanced."""

from __future__ import annotations

import math
import pytest

from ephemeris_oss.jyotish_advanced import (
    DEEP_EXALTATION_DEG,
    KP_PLANETS,
    NAKSHATRA_GANA,
    NAKSHATRA_NADI,
    SEVEN_PLANETS,
    TAJIKA_HADDA_TABLE,
    VEDHA_PAIRS,
    YONI_NAMES,
    YONI_SCORE_MATRIX,
    compute_harsha_bala,
    compute_mudda_dasha,
    compute_muntha,
    compute_pancha_vargiya_bala,
    compute_tajika_sahams,
    determine_varsheshwara,
    evaluate_ashtakoota,
    evaluate_classical_yogas,
    evaluate_dashakoota,
    evaluate_kuja_dosha,
    evaluate_mutual_kuja_dosha,
    evaluate_tajika_yogas,
    find_solar_return_jd,
    hadda_lord_for_longitude,
    kp_coordinate_lords,
    kp_fourfold_significators,
    kp_horary_entry,
    kp_ruling_planets,
    kp_sub_table_249,
)


# =============================================================================
# 1. KP 249 SUB-TABLE, LORDS, SIGNIFICATORS & RULING PLANETS
# =============================================================================


def test_kp_sub_table_249_exact_count_and_contiguity() -> None:
    table = kp_sub_table_249()
    assert len(table) == 249
    assert math.isclose(table[0].start_deg, 0.0, abs_tol=1e-12)
    assert math.isclose(table[-1].end_deg, 360.0, abs_tol=1e-12)

    total_span = 0.0
    for idx, entry in enumerate(table):
        assert entry.number == idx + 1
        assert entry.end_deg > entry.start_deg
        assert math.isclose(entry.end_deg - entry.start_deg, entry.span_deg, abs_tol=1e-12)
        total_span += entry.span_deg
        if idx > 0:
            assert math.isclose(entry.start_deg, table[idx - 1].end_deg, abs_tol=1e-12)

    assert math.isclose(total_span, 360.0, abs_tol=1e-9)


def test_kp_sub_table_249_six_sign_boundary_splits() -> None:
    table = kp_sub_table_249()
    split_entries = [e for e in table if e.split_across_sign]
    # 6 split sub-periods -> 12 split half-entries (at 30, 90, 150, 210, 270, 330 degrees)
    assert len(split_entries) == 12
    boundaries = [
        split_entries[i].end_deg for i in range(0, len(split_entries), 2)
    ]
    assert boundaries == [30.0, 90.0, 150.0, 210.0, 270.0, 330.0]


def test_kp_horary_entry_bounds_and_lookup() -> None:
    first = kp_horary_entry(1)
    assert first.number == 1
    assert first.rasi_name == "Mesha"
    assert first.nakshatra_name == "Ashwini"
    assert first.sign_lord == "mars"
    assert first.star_lord == "ketu"
    assert first.sub_lord == "ketu"

    last = kp_horary_entry(249)
    assert last.number == 249
    assert last.rasi_name == "Meena"
    assert last.nakshatra_name == "Revati"
    assert last.sign_lord == "jupiter"
    assert last.star_lord == "mercury"
    assert last.sub_lord == "saturn"

    with pytest.raises(ValueError):
        kp_horary_entry(0)
    with pytest.raises(ValueError):
        kp_horary_entry(250)


def test_kp_coordinate_lords_five_levels_and_split_horary_numbers() -> None:
    # 0.1 deg in Ashwini -> Ketu star, Ketu sub
    p0 = kp_coordinate_lords(0.1)
    assert p0.sign_lord == "mars"
    assert p0.star_lord == "ketu"
    assert p0.sub_lord == "ketu"
    assert p0.horary_number_249 == 1
    assert p0.pada == 1
    assert len(p0.receipt_sha256) == 64

    # Straddling 30 deg in Krittika (Rahu sub splits across Aries 29.8 deg and Taurus 30.2 deg)
    before_30 = kp_coordinate_lords(29.8)
    after_30 = kp_coordinate_lords(30.2)
    assert before_30.star_lord == "sun"
    assert after_30.star_lord == "sun"
    assert before_30.sub_lord == "rahu"
    assert after_30.sub_lord == "rahu"
    assert before_30.sign_lord == "mars"
    assert after_30.sign_lord == "venus"
    assert after_30.horary_number_249 == before_30.horary_number_249 + 1


def test_kp_fourfold_significators_hierarchy() -> None:
    planet_lons = {
        "sun": 10.0,       # House 1 (Mesha, Ashwini - Ketu star)
        "moon": 45.0,      # House 2 (Vrishabha, Rohini - Moon star)
        "mars": 75.0,      # House 3 (Mithuna, Ardra - Rahu star)
        "mercury": 105.0,  # House 4 (Karka, Pushya - Saturn star)
        "jupiter": 135.0,  # House 5 (Simha, Purva Phalguni - Venus star)
        "venus": 165.0,    # House 6 (Kanya, Hasta - Moon star)
        "saturn": 195.0,   # House 7 (Tula, Swati - Rahu star)
        "rahu": 225.0,     # House 8 (Vrischika, Anuradha - Saturn star)
        "ketu": 45.0,      # House 2 (Vrishabha, Rohini - Moon star)
    }
    cusps = [i * 30.0 for i in range(12)]
    report = kp_fourfold_significators(planet_lons, cusps)

    assert len(report.houses) == 12
    assert set(report.planets.keys()) == set(KP_PLANETS)
    h2 = report.houses[1]
    assert h2.house == 2
    assert "moon" in h2.level_2_occupants
    assert "ketu" in h2.level_2_occupants
    # Venus is in Hasta (Moon star), and Moon occupies House 2 -> Venus is a Level 1 significator of House 2
    assert "venus" in h2.level_1_star_of_occupants
    assert h2.cusp_sign_lord == "venus"
    # Jupiter is in Purva Phalguni (Venus star), and Venus owns Cusp 2 -> Jupiter is Level 3 for House 2
    assert "jupiter" in h2.level_3_star_of_cusp_lord
    assert h2.level_4_cusp_lord == ("venus",)


def test_kp_ruling_planets_seven_components() -> None:
    rp = kp_ruling_planets("thursday", moon_lon_deg=42.0, ascendant_lon_deg=125.0)
    assert rp.weekday_index == 4
    assert rp.day_lord == "jupiter"
    assert rp.ascendant_sign_lord == "sun"
    assert rp.moon_sign_lord == "venus"
    assert len(rp.ruling_planets_7) == 7
    assert len(rp.unique_ruling_planets) <= 7
    assert "jupiter" in rp.unique_ruling_planets


# =============================================================================
# 2. TAJIKA VARSHPHAL: SOLAR RETURN, MUNTHA, BALAS, YOGAS, MUDDA, SAHAMS
# =============================================================================


def test_find_solar_return_jd_sub_microdegree_convergence() -> None:
    birth_jd = 2451545.0  # 2000-01-01 TT
    natal_sun = find_solar_return_jd(256.5, target_year_approx_jd=birth_jd)
    assert natal_sun.residual_deg < 1e-8

    # Solve 25 years later via (birth_jd, birth_year, target_year)
    sr_2025 = find_solar_return_jd(
        natal_sun.achieved_sun_sidereal_lon_deg,
        birth_jd=natal_sun.jd_tt,
        birth_year=2000,
        target_year=2025,
    )
    assert sr_2025.residual_deg < 1e-8
    assert 25 * 365.24 < (sr_2025.jd_tt - natal_sun.jd_tt) < 25 * 365.28


def test_compute_muntha_progression_and_house() -> None:
    # Natal Ascendant Mesha (0), birth 1990, target 2026 -> elapsed 36 -> Muntha back in Mesha (0)
    m_36 = compute_muntha(12.5, birth_year=1990, target_year=2026, varsha_asc_sign_or_lon=4)
    assert m_36.elapsed_years == 36
    assert m_36.muntha_sign == 0
    assert m_36.muntha_lord == "mars"
    # From Simha (4) to Mesha (0) is 9th house -> auspicious
    assert m_36.house_from_varsha_lagna == 9
    assert m_36.is_auspicious_house is True


def test_tajika_hadda_table_all_signs_cover_30_degrees() -> None:
    assert len(TAJIKA_HADDA_TABLE) == 12
    for sign_idx, bounds in enumerate(TAJIKA_HADDA_TABLE):
        assert len(bounds) == 5
        assert bounds[-1][0] == 30.0
        lords = {lord for _, lord in bounds}
        assert lords == {"jupiter", "venus", "mercury", "mars", "saturn"}
        sample_lon = sign_idx * 30.0 + 3.0
        assert hadda_lord_for_longitude(sample_lon) == bounds[0][1]


def test_pancha_vargiya_bala_bounds_and_exaltation_peaks() -> None:
    # Place every planet at its deep exaltation degree
    lons = dict(DEEP_EXALTATION_DEG)
    pv = compute_pancha_vargiya_bala(lons)
    assert set(pv.keys()) == set(SEVEN_PLANETS)
    for body, bala in pv.items():
        assert math.isclose(bala.uchcha_bala, 20.0, abs_tol=1e-6)
        assert 0.0 < bala.vishwa_bala <= 20.0
        assert math.isclose(bala.total_virupas / 4.0, bala.vishwa_bala, abs_tol=1e-5)


def test_harsha_bala_fourfold_conditions() -> None:
    # Varsha Ascendant = Mesha (0). Put Mercury in 1st (Mesha=0), Jupiter in 11th (Kumbha=10), Sun in 9th (Dhanus=8)
    lons = {
        "sun": 245.0,      # 9th house (sthana=5, purusha=0, day=5)
        "moon": 65.0,      # 3rd house (sthana=5, stri=5)
        "mars": 165.0,     # 6th house (sthana=5, purusha=5)
        "mercury": 15.0,   # 1st house (sthana=5, stri=5)
        "jupiter": 310.0,  # 11th house (sthana=5, purusha=5, day=5)
        "venus": 135.0,    # 5th house (sthana=5)
        "saturn": 345.0,   # 12th house (sthana=5, day=5)
    }
    hb = compute_harsha_bala(lons, varsha_asc_lon_deg=10.0, is_day_birth=True)
    assert hb["sun"].sthana_points == 5
    assert hb["moon"].sthana_points == 5
    assert hb["mars"].sthana_points == 5
    assert hb["mercury"].sthana_points == 5
    assert hb["jupiter"].sthana_points == 5
    assert hb["venus"].sthana_points == 5
    assert hb["saturn"].sthana_points == 5
    for body in SEVEN_PLANETS:
        assert 0 <= hb[body].total_points <= 20


def test_determine_varsheshwara_selection() -> None:
    lons = {
        "sun": 10.0,       # Exalted in Mesha (1st house) -> high Bala, occupies Varsha Lagna
        "moon": 40.0,
        "mars": 298.0,     # Exalted in Makara (10th house) -> high Bala, aspects Varsha Lagna
        "mercury": 165.0,
        "jupiter": 95.0,
        "venus": 357.0,
        "saturn": 200.0,
    }
    rep = determine_varsheshwara(
        lons,
        natal_asc_lon_deg=10.0,
        varsha_asc_lon_deg=10.0,
        muntha_sign=0,
        is_day_birth=True,
    )
    assert rep.muntha_lord == "mars"
    assert rep.varsha_lagna_lord == "mars"
    assert rep.varsheshwara in rep.panchadhikari_candidates
    assert rep.aspects_varsha_lagna is True


def test_evaluate_tajika_yogas_ithasala_kamboola_ikkavala() -> None:
    # Put all 7 planets in Kendra/Panapara houses from Mesha Ascendant (0) -> Ikkavala active!
    # Moon (faster, 12 deg Vrishabha = 42.0) and Jupiter (slower, 15 deg Karka = 105.0)
    # Vrishabha (1) to Karka (3) is 3/11 sextile aspect, Moon at 12 deg < Jupiter at 15 deg -> Vartamana Ithasala!
    # Also Mercury at 13 deg Karka (103.0) < Jupiter at 15 deg Karka -> Mercury-Jupiter Ithasala + Moon-Jupiter -> Kamboola!
    lons = {
        "sun": 10.0,       # House 1 (Kendra)
        "moon": 42.0,      # House 2 (Panapara), 12 deg in sign
        "mars": 98.0,      # House 4 (Kendra), 8 deg in sign
        "mercury": 103.0,  # House 4 (Kendra), 13 deg in sign
        "jupiter": 105.0,  # House 4 (Kendra), 15 deg in sign
        "venus": 196.0,    # House 7 (Kendra), 16 deg in sign (separating from Jup -> Ishrafa)
        "saturn": 285.0,   # House 10 (Kendra), 15 deg in sign
    }
    yogas = {y.code: y for y in evaluate_tajika_yogas(lons, varsha_asc_lon_deg=5.0)}
    assert len(yogas) == 16
    assert yogas["ikkavala"].active is True
    assert yogas["induvara"].active is False
    assert yogas["ithasala"].active is True
    assert yogas["ishrafa"].active is True
    assert yogas["kamboola"].active is True


def test_evaluate_tajika_yogas_induvara_and_radda() -> None:
    # Put all 7 planets in Apoklima houses (3, 6, 9, 12) from Mesha (0) -> Gemini(2), Virgo(5), Sag(8), Pisces(11)
    lons = {
        "sun": 70.0,       # Gemini (H3)
        "moon": 72.0,      # Gemini (H3)
        "mars": 160.0,     # Virgo (H6)
        "mercury": 162.0,  # Virgo (H6), retrograde -> Radda
        "jupiter": 255.0,  # Sagittarius (H9)
        "venus": 340.0,    # Pisces (H12)
        "saturn": 345.0,   # Pisces (H12)
    }
    yogas = {
        y.code: y
        for y in evaluate_tajika_yogas(lons, varsha_asc_lon_deg=5.0, retrograde_planets=("mercury",))
    }
    assert yogas["induvara"].active is True
    assert yogas["ikkavala"].active is False
    assert yogas["radda"].active is True


def test_compute_mudda_dasha_spans_exact_solar_year() -> None:
    periods = compute_mudda_dasha(
        natal_moon_lon_deg=45.0,
        birth_year=1995,
        target_year=2026,
        solar_return_jd=2461000.0,
        year_length_days=365.2425,
    )
    assert len(periods) >= 9
    total_days = sum(p.duration_days for p in periods)
    assert math.isclose(total_days, 365.2425, abs_tol=1e-9)
    assert math.isclose(periods[0].start_jd, 2461000.0, abs_tol=1e-9)
    assert math.isclose(periods[-1].end_jd, 2461000.0 + 365.2425, abs_tol=1e-9)
    for p in periods:
        assert len(p.antardashas) == 9
        antar_sum = sum(end - start for _lord, start, end in p.antardashas)
        assert math.isclose(antar_sum, p.duration_days, abs_tol=1e-9)


def test_compute_tajika_sahams_day_night_reversal() -> None:
    lons = {
        "sun": 20.0,
        "moon": 110.0,
        "mars": 150.0,
        "mercury": 35.0,
        "jupiter": 95.0,
        "venus": 50.0,
        "saturn": 210.0,
    }
    day_sahams = compute_tajika_sahams(lons, varsha_asc_lon_deg=15.0, is_day_birth=True)
    night_sahams = compute_tajika_sahams(lons, varsha_asc_lon_deg=15.0, is_day_birth=False)
    assert len(day_sahams) == 36
    assert day_sahams["punya"].longitude_deg != night_sahams["punya"].longitude_deg
    # Bhratri Saham does not reverse at night
    assert math.isclose(
        day_sahams["bhratri"].longitude_deg, night_sahams["bhratri"].longitude_deg, abs_tol=1e-9
    )


# =============================================================================
# 3. ASHTAKOOTA (36-POINT), DASHAKOOTA (10-POINT) & KUJA DOSHA
# =============================================================================


def test_ashtakoota_maximum_36_points_achievable() -> None:
    # Bride in Pushya (Nakshatra 7, Cancer=3, Brahmin, Jalachara, Goat, Deva, Madhya Nadi) -> lon = 100.0
    # Groom in Revati (Nakshatra 26, Pisces=11, Brahmin, Jalachara, Elephant, Deva, Antya Nadi) -> lon = 355.0
    # Wait: let's check a pair with Same Yoni + Different Nadi!
    # Ashwini (Nak 0, Aries=0, Horse, Deva, Adi Nadi) vs Shatabhisha (Nak 23, Aquarius=10, Horse, Rakshasa, Adi Nadi) -> same Nadi.
    # What about Bharani (Nak 1, Aries=0, Elephant, Manushya, Madhya Nadi, lon=20.0)
    # and Revati (Nak 26, Pisces=11, Elephant, Deva, Antya Nadi, lon=350.0)?
    #Wait: Aries (0) and Pisces (11) is 2/12 Bhakoot, though Mars and Jupiter are mutual Naisargika friends!
    # What about Uttara Phalguni (Nak 11, Pad 2 in Virgo=5, Vaishya, Manava, Cow, Manushya, Adi Nadi)
    # and Uttara Bhadrapada (Nak 25, Pisces=11, Brahmin, Jalachara, Cow, Manushya, Madhya Nadi)?
    # Let's check exact 36.0 when same nakshatra/different pada cancels Nadi OR search across the 27x27 grid!
    best_raw = 0.0
    best_eff = 0.0
    for b_idx in range(108):
        b_lon = b_idx * (10.0 / 3.0) + 1.0
        for g_idx in range(108):
            g_lon = g_idx * (10.0 / 3.0) + 1.0
            rep = evaluate_ashtakoota(b_lon, g_lon)
            if rep.total_raw_points > best_raw:
                best_raw = rep.total_raw_points
            if rep.total_effective_points > best_eff:
                best_eff = rep.total_effective_points
    assert best_eff == 36.0
    assert best_raw >= 35.0


def test_ashtakoota_yoni_sworn_enemies_score_zero() -> None:
    enemy_pairs = [
        ("Cow", "Tiger"),
        ("Elephant", "Lion"),
        ("Horse", "Buffalo"),
        ("Dog", "Deer"),
        ("Mongoose", "Serpent"),
        ("Monkey", "Goat"),
        ("Cat", "Rat"),
    ]
    for a_name, b_name in enemy_pairs:
        idx_a = YONI_NAMES.index(a_name)
        idx_b = YONI_NAMES.index(b_name)
        assert YONI_SCORE_MATRIX[idx_a][idx_b] == 0
        assert YONI_SCORE_MATRIX[idx_b][idx_a] == 0


def test_ashtakoota_bhakoot_and_nadi_dosha_cancellations() -> None:
    # Aries (Mesha=0, Mars) and Scorpio (Vrischika=7, Mars) are 6/8 Shadashtaka,
    # but both are ruled by Mars -> Bhakoot Dosha cancelled!
    rep = evaluate_ashtakoota(bride_moon_lon_deg=5.0, groom_moon_lon_deg=215.0)
    bhakoot = dict((item.name, item) for item in rep.items)["bhakoot"]
    assert bhakoot.raw_points == 0.0
    assert bhakoot.dosha_present is True
    assert bhakoot.dosha_cancelled is True
    assert bhakoot.effective_points == 7.0

    # Same Nakshatra (Ashwini, 0..13.33 deg) but different Pada (Pada 1 at 1.0 deg vs Pada 3 at 8.0 deg) -> Nadi cancelled!
    rep_nadi = evaluate_ashtakoota(bride_moon_lon_deg=1.0, groom_moon_lon_deg=8.0)
    nadi = dict((item.name, item) for item in rep_nadi.items)["nadi"]
    assert nadi.raw_points == 0.0
    assert nadi.dosha_present is True
    assert nadi.dosha_cancelled is True
    assert nadi.effective_points == 8.0


def test_dashakoota_ten_poruthams_rajju_and_vedha() -> None:
    # Ashwini (0, lon=5.0) and Jyeshtha (17, lon=230.0) are a hostile Vedha pair!
    rep_vedha = evaluate_dashakoota(bride_moon_lon_deg=5.0, groom_moon_lon_deg=230.0)
    assert len(rep_vedha.poruthams) == 10
    assert rep_vedha.vedha_dosha is True
    assert rep_vedha.recommended is False

    # Harmonious pair: Rohini (Nak 3, lon=45.0) and Uttara Phalguni (Nak 11, lon=155.0)
    rep_good = evaluate_dashakoota(bride_moon_lon_deg=45.0, groom_moon_lon_deg=155.0)
    assert rep_good.vedha_dosha is False
    assert rep_good.rajju_dosha is False
    assert rep_good.passed_count >= 6
    assert rep_good.recommended is True


def test_kuja_dosha_single_and_mutual_cancellations() -> None:
    # Uncancelled Manglik: Asc=Taurus(35 deg), Mars in 7th (Scorpio? No, Scorpio is own sign! Put Asc=Gemini 65 deg, Mars in 7th Sagittarius 245 deg)
    # Wait: Gemini (2) -> 7th is Sagittarius (8). Put Moon in Taurus (40 deg) and Venus in Aries (10 deg).
    unmitigated = evaluate_kuja_dosha(
        mars_lon_deg=245.0,
        ascendant_lon_deg=65.0,
        moon_lon_deg=40.0,
        venus_lon_deg=10.0,
    )
    assert unmitigated.mars_house_from_lagna == 7
    assert unmitigated.dosha_from_lagna is True
    assert unmitigated.is_cancelled is False
    assert unmitigated.effective_manglik is True

    # Cancelled Manglik: Mars in Own Sign Aries (5 deg) in 1st house (Asc=10 deg)
    cancelled = evaluate_kuja_dosha(
        mars_lon_deg=5.0,
        ascendant_lon_deg=10.0,
        moon_lon_deg=120.0,
        venus_lon_deg=150.0,
    )
    assert cancelled.mars_house_from_lagna == 1
    assert cancelled.is_manglik_raw is True
    assert cancelled.is_cancelled is True
    assert cancelled.effective_manglik is False

    # Non-Manglik: Mars in 3rd house (Leo 130 deg from Gemini Asc 65 deg), 11th from Moon (Libra 190 deg), 9th from Venus (Sagittarius 250 deg)
    clean = evaluate_kuja_dosha(
        mars_lon_deg=130.0,
        ascendant_lon_deg=65.0,
        moon_lon_deg=190.0,
        venus_lon_deg=250.0,
    )
    assert clean.is_manglik_raw is False
    assert clean.effective_manglik is False

    # Mutual compatibility check
    mismatch = evaluate_mutual_kuja_dosha(unmitigated, clean)
    assert mismatch.mutually_compatible is False

    mutual_cancel = evaluate_mutual_kuja_dosha(unmitigated, unmitigated)
    assert mutual_cancel.mutually_compatible is True


# =============================================================================
# 4. CLASSICAL PARASHARI YOGAS (70 NAMED YOGAS)
# =============================================================================


def test_classical_yogas_catalog_size_and_mahapurusha() -> None:
    # Ascendant = Mesha (0). Exalt Mars in 10th (Makara=298), Jupiter in 4th (Karka=95),
    # Saturn in 7th (Tula=200), Sun in 1st (Mesha=10).
    lons = {
        "sun": 10.0,       # H1
        "moon": 95.0,      # H4 (with Jupiter -> Gajakesari)
        "mars": 298.0,     # H10 (Exalted in Kendra -> Ruchaka)
        "mercury": 10.0,   # H1 (with Sun -> Budhaditya)
        "jupiter": 95.0,   # H4 (Exalted in Kendra -> Hamsa)
        "venus": 40.0,     # H2 (Own sign Taurus)
        "saturn": 200.0,   # H7 (Exalted in Kendra -> Sasa)
    }
    rep = evaluate_classical_yogas(lons, ascendant_lon_deg=5.0)
    assert len(rep.yogas) == 70
    assert rep.by_code["ruchaka"].active is True
    assert rep.by_code["hamsa"].active is True
    assert rep.by_code["sasa"].active is True
    assert rep.by_code["gajakesari"].active is True
    assert rep.by_code["budhaditya"].active is True


def test_classical_yogas_lunar_sunapha_anapha_durudhara_kemadruma() -> None:
    # Moon at 100 deg (Karka = sign 3).
    # Put Mars in 2nd from Moon (Simha = 130 deg) and Venus in 12th from Moon (Mithuna = 70 deg) -> Durudhara!
    lons_duru = {
        "sun": 10.0,
        "moon": 100.0,
        "mars": 130.0,
        "mercury": 10.0,
        "jupiter": 10.0,
        "venus": 70.0,
        "saturn": 10.0,
    }
    rep_duru = evaluate_classical_yogas(lons_duru, ascendant_lon_deg=5.0)
    assert rep_duru.by_code["durudhara"].active is True
    assert rep_duru.by_code["sunapha"].active is False
    assert rep_duru.by_code["anapha"].active is False

    # Kemadruma uncancelled: Moon in 2nd house (Vrishabha=40 deg), all other planets in 6th house (Kanya=160 deg)
    # Wait: from Vrishabha (1), Kanya (5) is 5th house (neither 2/12 nor Kendra from Moon, and H6 is not Kendra from Lagna!)
    lons_kema = {
        "sun": 160.0,
        "moon": 40.0,
        "mars": 160.0,
        "mercury": 160.0,
        "jupiter": 160.0,
        "venus": 160.0,
        "saturn": 160.0,
    }
    rep_kema = evaluate_classical_yogas(lons_kema, ascendant_lon_deg=5.0)
    assert rep_kema.by_code["kemadruma"].active is True
    assert rep_kema.by_code["kemadruma_bhanga"].active is False


def test_classical_yogas_parivartana_vipareeta_and_neecha_bhanga() -> None:
    # Ascendant = Mesha (0).
    # 9th lord Jupiter (Dhanus=8) in 10th (Makara=9, debilitation!) and 10th lord Saturn (Makara=9) in 9th (Dhanus=8)
    # -> Dharma-Karmadhipati Raja Yoga + Maha Parivartana + Neecha Bhanga Raja Yoga!
    # Also put 6th lord Mercury in 8th (Vrischika=7) -> Harsha Vipareeta Raja Yoga!
    # And 8th lord Mars in 12th (Meena=11) -> Sarala Vipareeta Raja Yoga!
    lons = {
        "sun": 10.0,
        "moon": 40.0,
        "mars": 340.0,     # 8L in 12th -> Sarala Vipareeta
        "mercury": 220.0,  # 6L in 8th -> Harsha Vipareeta
        "jupiter": 280.0,  # 9L in 10th (Debilitated in Makara, exchanging with Saturn) -> Neecha Bhanga + Maha Parivartana
        "venus": 190.0,
        "saturn": 250.0,   # 10L in 9th
    }
    rep = evaluate_classical_yogas(lons, ascendant_lon_deg=5.0)
    assert rep.by_code["dharma_karmadhipati"].active is True
    assert rep.by_code["maha_parivartana"].active is True
    assert rep.by_code["neecha_bhanga_raja"].active is True
    assert rep.by_code["harsha_vipareeta"].active is True
    assert rep.by_code["sarala_vipareeta"].active is True


def test_classical_yogas_nabhasa_ashraya_and_sankhya() -> None:
    # All 7 planets in Chara (movable: 0, 3, 6, 9) signs -> Rajju Nabhasa Yoga + Kamala (all 4 Kendras from Mesha) + Kedara (4 signs)
    lons_chara = {
        "sun": 10.0,       # Sign 0 (H1)
        "moon": 95.0,      # Sign 3 (H4)
        "mars": 190.0,     # Sign 6 (H7)
        "mercury": 280.0,  # Sign 9 (H10)
        "jupiter": 98.0,   # Sign 3 (H4)
        "venus": 195.0,    # Sign 6 (H7)
        "saturn": 285.0,   # Sign 9 (H10)
    }
    rep = evaluate_classical_yogas(lons_chara, ascendant_lon_deg=5.0)
    assert rep.by_code["nabhasa_rajju"].active is True
    assert rep.by_code["nabhasa_kamala"].active is True
    assert rep.by_code["nabhasa_kedara"].active is True
    assert rep.by_code["nabhasa_musala"].active is False
    assert rep.by_code["nabhasa_nala"].active is False


def test_classical_yogas_gola_and_sringataka() -> None:
    # All 7 planets in 1st house (Mesha=0) -> Gola Sankhya (1 sign) + Sringataka (subset of 1,5,9) + Rajju (movable)
    lons_gola = {b: 15.0 for b in SEVEN_PLANETS}
    rep = evaluate_classical_yogas(lons_gola, ascendant_lon_deg=5.0)
    assert rep.by_code["nabhasa_gola"].active is True
    assert rep.by_code["nabhasa_sringataka"].active is True


# =============================================================================
# 5. PARAMETRIZED INVARIANTS (30+ ADDITIONAL CHECKS FOR 50+ TOTAL TESTS)
# =============================================================================


@pytest.mark.parametrize("horary_num", [1, 12, 23, 24, 61, 62, 125, 180, 248, 249])
def test_kp_horary_midpoint_round_trip(horary_num: int) -> None:
    entry = kp_horary_entry(horary_num)
    midpoint = 0.5 * (entry.start_deg + entry.end_deg)
    pos = kp_coordinate_lords(midpoint)
    assert pos.horary_number_249 == horary_num
    assert pos.sign_lord == entry.sign_lord
    assert pos.star_lord == entry.star_lord
    assert pos.sub_lord == entry.sub_lord


@pytest.mark.parametrize("weekday_idx", [0, 1, 2, 3, 4, 5, 6])
def test_kp_ruling_planets_all_weekdays(weekday_idx: int) -> None:
    rp = kp_ruling_planets(weekday_idx, moon_lon_deg=weekday_idx * 45.0, ascendant_lon_deg=weekday_idx * 30.0)
    assert rp.weekday_index == weekday_idx
    assert rp.day_lord in KP_PLANETS


@pytest.mark.parametrize("nak_idx", list(range(27)))
def test_ashtakoota_identical_moon_positions_across_all_27_nakshatras(nak_idx: int) -> None:
    lon = nak_idx * (40.0 / 3.0) + 2.0
    rep = evaluate_ashtakoota(lon, lon)
    assert rep.bride_nakshatra_index == nak_idx
    assert rep.groom_nakshatra_index == nak_idx
    assert 0.0 <= rep.total_raw_points <= 36.0
    assert NAKSHATRA_GANA[nak_idx] in {"Deva", "Manushya", "Rakshasa"}
    assert NAKSHATRA_NADI[nak_idx] in {"Adi", "Madhya", "Antya"}
