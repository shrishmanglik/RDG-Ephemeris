"""Unit and invariant test suite for Jaimini Upadesha Sutras (`jyotish_jaimini`)
and Scientific Uncertainty & Boundary Sensitivity Envelope (`uncertainty_envelope`).
"""

from __future__ import annotations

import math
import pytest

from ephemeris_oss.engine.uncertainty_envelope import (
    COMPACT_RESIDUAL_CEILINGS_ARCSEC,
    compute_boundary_sensitivity,
    compute_position_uncertainty,
)
from ephemeris_oss.jyotish_jaimini import (
    ADJACENT_MOVABLE_FIXED_PAIRS,
    DUAL_SIGNS,
    FIXED_SIGNS,
    MANDOOKA_JUMP_OFFSETS,
    MOVABLE_SIGNS,
    classify_modality_pair_longevity,
    compute_argala_matrix,
    compute_jaimini_ayurdaya,
    compute_karakamsa_analysis,
    compute_mandooka_dasha,
    compute_shoola_dasha,
    compute_sthira_dasha,
    j_rashi_drishti,
    sign_modality,
    stronger_sign_jaimini,
)


SAMPLE_CHART_LONS: dict[str, float] = {
    "Sun": 18.5,       # 0 Mesha (Aries), 18.5 deg
    "Moon": 52.0,      # 1 Vrishabha (Taurus), 22.0 deg
    "Mars": 104.2,     # 3 Karka (Cancer), 14.2 deg
    "Mercury": 27.8,   # 0 Mesha (Aries), 27.8 deg -> Atmakaraka (AK) in 7-karaka scheme
    "Jupiter": 95.0,   # 3 Karka (Cancer), 5.0 deg
    "Venus": 351.0,    # 11 Meena (Pisces), 21.0 deg
    "Saturn": 199.4,   # 6 Tula (Libra), 19.4 deg
    "Rahu": 72.0,      # 2 Mithuna (Gemini), 12.0 deg (eff = 18.0 deg)
    "Ketu": 252.0,     # 8 Dhanu (Sagittarius), 12.0 deg (eff = 18.0 deg)
}


# ============================================================================
# 1. Rashi Drishti Invariants & Unit Tests
# ============================================================================


def test_rashi_drishti_full_table_length_and_degree() -> None:
    all_entries = j_rashi_drishti()
    assert len(all_entries) == 12
    for idx, entry in enumerate(all_entries):
        assert entry.sign_index == idx
        assert len(entry.aspected_signs) == 3
        assert len(set(entry.aspected_signs)) == 3
        assert idx not in entry.aspected_signs


def test_rashi_drishti_symmetry_invariant() -> None:
    """In Jaimini Rashi Drishti, Sign A aspects Sign B if and only if Sign B aspects Sign A."""
    for a in range(12):
        for b in range(12):
            assert j_rashi_drishti(a, b) == j_rashi_drishti(b, a), f"Asymmetry between {a} and {b}"


def test_rashi_drishti_zero_adjacent_movable_fixed_aspects() -> None:
    """Movable and immediately adjacent Fixed signs (0<->1, 3<->4, 6<->7, 9<->10) never aspect."""
    expected_pairs = {(0, 1), (3, 4), (6, 7), (9, 10)}
    for a, b in expected_pairs:
        assert frozenset({a, b}) in ADJACENT_MOVABLE_FIXED_PAIRS
        assert j_rashi_drishti(a, b) is False
        assert j_rashi_drishti(b, a) is False
        assert b not in j_rashi_drishti(a)
        assert a not in j_rashi_drishti(b)


def test_rashi_drishti_movable_aspects_non_adjacent_fixed() -> None:
    for m in MOVABLE_SIGNS:
        entry = j_rashi_drishti(m)
        assert entry.modality == "Movable"
        for f in FIXED_SIGNS:
            if frozenset({m, f}) in ADJACENT_MOVABLE_FIXED_PAIRS:
                assert f not in entry
            else:
                assert f in entry
                assert entry.aspects(f) is True


def test_rashi_drishti_fixed_aspects_non_adjacent_movable() -> None:
    for f in FIXED_SIGNS:
        entry = j_rashi_drishti(f)
        assert entry.modality == "Fixed"
        for m in MOVABLE_SIGNS:
            if frozenset({m, f}) in ADJACENT_MOVABLE_FIXED_PAIRS:
                assert m not in entry
            else:
                assert m in entry


def test_rashi_drishti_dual_signs_mutual_aspects() -> None:
    for d in DUAL_SIGNS:
        entry = j_rashi_drishti(d)
        assert entry.modality == "Dual"
        assert set(entry.aspected_signs) == (DUAL_SIGNS - {d})


def test_rashi_drishti_with_planet_longitudes() -> None:
    # Mesha (0) is aspected by Simha (4), Vrishchika (7), Kumbha (10)
    lons = {"Sun": 130.0, "Mars": 220.0, "Saturn": 310.0, "Jupiter": 15.0}
    entry_aries = j_rashi_drishti(0, planet_longitudes=lons)
    assert entry_aries.occupants == ("Jupiter",)
    assert set(entry_aries.aspected_by_planets) == {"Sun", "Mars", "Saturn"}
    assert "Simha" in entry_aries


# ============================================================================
# 2. Argala & Virodhargala Matrix Tests
# ============================================================================


def test_argala_unobstructed_primary_and_secondary() -> None:
    # Reference sign: Mesha (0). Place planets in 2nd (1), 4th (3), 11th (10), 5th (4)
    # Leave 12th (11), 10th (9), 3rd (2), 9th (8) empty.
    lons = {
        "Venus": 45.0,    # 1 Vrishabha (2nd from Mesha)
        "Moon": 100.0,    # 3 Karka (4th from Mesha)
        "Saturn": 310.0,  # 10 Kumbha (11th from Mesha)
        "Sun": 135.0,     # 4 Simha (5th from Mesha)
    }
    matrix = compute_argala_matrix(lons)
    aries = matrix[0]
    assert aries.dhana_2nd_vs_12th.status == "Unobstructed"
    assert aries.dhana_2nd_vs_12th.net_active is True
    assert aries.sukha_4th_vs_10th.status == "Unobstructed"
    assert aries.sukha_4th_vs_10th.net_active is True
    assert aries.labha_11th_vs_3rd.status == "Unobstructed"
    assert aries.labha_11th_vs_3rd.net_active is True
    assert aries.putra_5th_vs_9th.status == "Unobstructed"
    assert aries.putra_5th_vs_9th.net_active is True
    assert set(aries.active_argala_houses) == {"2nd", "4th", "11th", "5th"}


def test_argala_obstructed_by_greater_planet_count() -> None:
    # For Mesha (0): 1 planet in 2nd (Vrishabha=1), 2 planets in 12th (Meena=11)
    lons = {
        "Venus": 40.0,     # 1 Vrishabha (2nd)
        "Jupiter": 340.0,  # 11 Meena (12th)
        "Mercury": 350.0,  # 11 Meena (12th)
    }
    matrix = compute_argala_matrix(lons)
    aries = matrix[0]
    assert aries.dhana_2nd_vs_12th.status == "Obstructed"
    assert aries.dhana_2nd_vs_12th.net_active is False


def test_argala_equal_count_resolved_by_degree() -> None:
    # For Mesha (0): 1 planet in 4th (Karka=3 at 24 deg) vs 1 planet in 10th (Makara=9 at 10 deg)
    lons = {
        "Jupiter": 114.0,  # 3 Karka, 24.0 deg
        "Saturn": 280.0,   # 9 Makara, 10.0 deg
    }
    matrix = compute_argala_matrix(lons)
    aries = matrix[0]
    assert aries.sukha_4th_vs_10th.status == "Predominant_By_Degree"
    assert aries.sukha_4th_vs_10th.net_active is True

    # Flip degrees so 10th house planet has higher degree
    lons_flipped = {
        "Jupiter": 95.0,   # 3 Karka, 5.0 deg
        "Saturn": 295.0,   # 9 Makara, 25.0 deg
    }
    aries_flipped = compute_argala_matrix(lons_flipped)[0]
    assert aries_flipped.sukha_4th_vs_10th.status == "Obstructed_By_Degree"
    assert aries_flipped.sukha_4th_vs_10th.net_active is False


def test_argala_vipareeta_3rd_house_malefics() -> None:
    # 3 natural malefics in 3rd from Mesha (Mithuna=2)
    lons = {
        "Sun": 65.0,
        "Mars": 72.0,
        "Saturn": 80.0,
    }
    matrix = compute_argala_matrix(lons)
    aries = matrix[0]
    assert aries.third_house_sign == 2
    assert len(aries.third_house_malefics) == 3
    assert aries.has_vipareeta_argala_3rd is True
    assert "3rd_Vipareeta" in aries.active_argala_houses


def test_argala_ketu_dominated_reverse_counting() -> None:
    # Place Ketu alone in Dhanu (8). With reverse_for_ketu=True:
    # 2nd from Dhanu in reverse is Vrishchika (7), 12th in reverse is Makara (9).
    lons = {
        "Ketu": 250.0,   # 8 Dhanu
        "Mars": 225.0,   # 7 Vrishchika (reverse 2nd from Dhanu)
    }
    matrix = compute_argala_matrix(lons, reverse_for_ketu=True)
    sag = matrix[8]
    assert sag.is_ketu_reversed is True
    assert sag.direction_step == -1
    assert sag.dhana_2nd_vs_12th.argala_sign == 7
    assert sag.dhana_2nd_vs_12th.virodha_sign == 9
    assert sag.dhana_2nd_vs_12th.net_active is True

    matrix_direct = compute_argala_matrix(lons, reverse_for_ketu=False)
    sag_direct = matrix_direct[8]
    assert sag_direct.is_ketu_reversed is False
    assert sag_direct.direction_step == 1
    assert sag_direct.dhana_2nd_vs_12th.argala_sign == 9


# ============================================================================
# 3. Karakamsa, Swamsa & Jaimini Devatas Tests
# ============================================================================


def test_karakamsa_and_devatas_7_karaka_scheme() -> None:
    # In SAMPLE_CHART_LONS:
    # Mercury is at 27.8 deg in Mesha (0) -> highest degree -> AK = Mercury.
    # Mesha 27.8 deg is in 9th Navamsa (26.666.. to 30.0 deg) -> Dhanu (8) -> Karakamsa = 8 (Dhanu).
    # Moon is at 52.0 deg in Vrishabha (1), 22.0 deg -> 2nd highest -> AmK = Moon.
    # Vrishabha 22.0 deg -> part = int(22 / 3.3333) = 6 -> Earth starts at Makara (9) -> (9 + 6) % 12 = 3 (Karka).
    # Lagna at 12.0 deg Mesha -> part = 3 -> (0 + 3) % 12 = 3 (Karka) -> Swamsa = 3 (Karka).
    analysis = compute_karakamsa_analysis(12.0, SAMPLE_CHART_LONS, scheme="7")
    assert analysis.atmakaraka_planet == "Mercury"
    assert analysis.amatyakaraka_planet == "Moon"
    assert analysis.darakaraka_planet == "Jupiter"  # 5.0 deg in Karka is lowest
    assert analysis.karakamsa_sign == 8
    assert analysis.karakamsa_sign_name == "Dhanu"
    assert analysis.swamsa_sign == 3
    assert analysis.swamsa_sign_name == "Karka"

    # Ishta Devata = 12th from Karakamsa (8) -> (8 + 11) % 12 = 7 (Vrishchika)
    assert analysis.ishta_devata.sign_index == 7
    assert analysis.ishta_devata.sign_name == "Vrishchika"

    # Palana Devata = 6th from AmK in D9 (3 Karka) -> (3 + 5) % 12 = 8 (Dhanu)
    assert analysis.palana_devata.sign_index == 8
    assert analysis.palana_devata.sign_name == "Dhanu"

    # Dharma Devata = 9th from Karakamsa (8) -> (8 + 8) % 12 = 4 (Simha)
    assert analysis.dharma_devata.sign_index == 4
    assert analysis.dharma_devata.sign_name == "Simha"


def test_karakamsa_8_karaka_scheme_includes_pitrikaraka() -> None:
    analysis = compute_karakamsa_analysis(12.0, SAMPLE_CHART_LONS, scheme="8")
    assert len(analysis.chara_karakas) == 8
    assert "PiK" in analysis.karakas_by_code
    assert analysis.karakas_by_code["AK"].planet == "Mercury"


# ============================================================================
# 4. Three-Pairs Jaimini Longevity (Ayurdaya) Tests
# ============================================================================


@pytest.mark.parametrize(
    ("sign_a", "sign_b", "expected"),
    [
        (0, 3, "Purnayu"),   # Movable + Movable -> Purnayu (66-100y)
        (1, 2, "Purnayu"),   # Fixed + Dual -> Purnayu
        (8, 4, "Purnayu"),   # Dual + Fixed -> Purnayu
        (1, 7, "Alpayu"),    # Fixed + Fixed -> Alpayu (0-33y)
        (0, 2, "Alpayu"),    # Movable + Dual -> Alpayu
        (11, 6, "Alpayu"),   # Dual + Movable -> Alpayu
        (2, 5, "Madhyayu"),  # Dual + Dual -> Madhyayu (33-66y)
        (0, 1, "Madhyayu"),  # Movable + Fixed -> Madhyayu
        (10, 9, "Madhyayu"), # Fixed + Movable -> Madhyayu
    ],
)
def test_classify_modality_pair_longevity_table(sign_a: int, sign_b: int, expected: str) -> None:
    assert classify_modality_pair_longevity(sign_a, sign_b) == expected


def test_ayurdaya_unanimous_purnayu() -> None:
    # Lagna=0 (Movable), Moon=3 (Movable -> Purnayu), Hora Lagna=6 (Movable -> Purnayu), Saturn=9 (Movable -> Purnayu)
    res = compute_jaimini_ayurdaya(
        lagna_sign=0,
        moon_sign=3,
        hora_lagna_sign=6,
        eighth_or_saturn_sign=9,
        apply_kakshya_adjustment=False,
    )
    assert res.pair_1_lagna_moon.category == "Purnayu"
    assert res.pair_2_lagna_hora_lagna.category == "Purnayu"
    assert res.pair_3_lagna_eighth_or_saturn.category == "Purnayu"
    assert res.base_category == "Purnayu"
    assert res.final_category == "Purnayu"
    assert res.estimated_Range_years == (66.0, 100.0)
    assert res.tie_breaker_used is False


def test_ayurdaya_majority_alpayu_and_kakshya_vriddhi() -> None:
    # Lagna=1 (Fixed, Vrishabha), Moon=4 (Fixed -> Alpayu), Hora Lagna=7 (Fixed -> Alpayu), Saturn=2 (Dual -> Purnayu)
    # Majority is Alpayu (2 out of 3).
    # Place Jupiter in Vrishabha (1) on Lagna -> Kakshya Vriddhi elevates Alpayu -> Madhyayu!
    lons = dict(SAMPLE_CHART_LONS)
    lons["Jupiter"] = 45.0  # Vrishabha (1), on Lagna
    lons["Moon"] = 135.0    # Simha (4)
    lons["Saturn"] = 75.0   # Mithuna (2)
    res = compute_jaimini_ayurdaya(
        lagna_lon_deg=40.0,
        planet_longitudes=lons,
        hora_lagna_sign=7,
        apply_kakshya_adjustment=True,
    )
    assert res.base_category == "Alpayu"
    assert res.kakshya_type == "Kakshya Vriddhi"
    assert res.kakshya_shift == 1
    assert res.final_category == "Madhyayu"
    assert res.estimated_Range_years == (33.0, 66.0)


def test_ayurdaya_three_way_tie_resolved_by_hora_lagna_pair() -> None:
    # Lagna=0 (Movable):
    # Pair 1: Moon=2 (Dual) -> Movable + Dual = Alpayu
    # Pair 2: Hora Lagna=1 (Fixed) -> Movable + Fixed = Madhyayu
    # Pair 3: Saturn=3 (Movable) -> Movable + Movable = Purnayu
    res = compute_jaimini_ayurdaya(
        lagna_sign=0,
        moon_sign=2,
        hora_lagna_sign=1,
        eighth_or_saturn_sign=3,
        apply_kakshya_adjustment=False,
    )
    assert {p.category for p in res.pairs} == {"Alpayu", "Madhyayu", "Purnayu"}
    assert res.tie_breaker_used is True
    assert res.base_category == "Madhyayu"
    assert res.final_category == "Madhyayu"


def test_ayurdaya_kakshya_hrasa_and_graha_identifiers() -> None:
    # Base Madhyayu reduced to Alpayu when multiple malefics afflict Lagna/AK without Jupiter/Venus
    lons = {
        "Sun": 10.0,
        "Moon": 70.0,
        "Mars": 15.0,     # in Mesha (0) on Lagna
        "Mercury": 140.0,
        "Jupiter": 200.0,
        "Venus": 250.0,
        "Saturn": 22.0,   # in Mesha (0) on Lagna
        "Rahu": 5.0,      # in Mesha (0) on Lagna (eff = 25.0)
        "Ketu": 185.0,
    }
    res = compute_jaimini_ayurdaya(
        lagna_lon_deg=12.0,
        planet_longitudes=lons,
        hora_lagna_sign=1,
        eighth_or_saturn_sign=1,
        apply_kakshya_adjustment=True,
    )
    assert res.base_category == "Madhyayu"
    assert res.kakshya_type == "Kakshya Hrasa"
    assert res.kakshya_shift == -1
    assert res.final_category == "Alpayu"
    assert res.brahma_graha in lons
    assert res.rudra_graha in lons
    assert res.maheshwara_graha in lons


# ============================================================================
# 5. Additional Jaimini Rasi Dashas (Sthira, Shoola, Mandooka)
# ============================================================================


def test_sthira_dasha_96_year_total_and_modality_durations() -> None:
    timeline = compute_sthira_dasha(15.0, SAMPLE_CHART_LONS, birth_jd=2451545.0, max_level=2)
    assert timeline.system == "Sthira"
    assert len(timeline.mahadashas) == 12
    total_years = sum(m.duration_years for m in timeline.mahadashas)
    assert math.isclose(total_years, 96.0, abs_tol=1e-9)
    # Verify 4 signs of 7y, 4 signs of 8y, 4 signs of 9y
    durations = sorted(m.duration_years for m in timeline.mahadashas)
    assert durations == [7.0] * 4 + [8.0] * 4 + [9.0] * 4
    # Verify Antardasha subdivision continuity
    for m in timeline.mahadashas:
        assert len(m.sub_periods) == 12
        assert math.isclose(m.sub_periods[0].start_jd, m.start_jd, abs_tol=1e-9)
        assert math.isclose(m.sub_periods[-1].end_jd, m.end_jd, abs_tol=1e-9)


def test_shoola_dasha_108_year_total_and_equal_9_year_periods() -> None:
    timeline = compute_shoola_dasha(15.0, SAMPLE_CHART_LONS, birth_jd=2451545.0, max_level=2)
    assert timeline.system == "Shoola"
    assert len(timeline.mahadashas) == 12
    total_years = sum(m.duration_years for m in timeline.mahadashas)
    assert math.isclose(total_years, 108.0, abs_tol=1e-9)
    for m in timeline.mahadashas:
        assert math.isclose(m.duration_years, 9.0, abs_tol=1e-9)
        assert len(m.sub_periods) == 12
        for sub in m.sub_periods:
            assert math.isclose(sub.duration_years, 0.75, abs_tol=1e-9)


def test_mandooka_dasha_frog_jump_sequence_and_96_year_total() -> None:
    timeline = compute_mandooka_dasha(
        15.0, SAMPLE_CHART_LONS, birth_jd=2451545.0, start_sign=0, max_level=2
    )
    assert timeline.system == "Mandooka"
    assert len(timeline.mahadashas) == 12
    total_years = sum(m.duration_years for m in timeline.mahadashas)
    assert math.isclose(total_years, 96.0, abs_tol=1e-9)

    # Starting from Mesha (0, odd -> step +1), sequence must follow frog-jump offsets:
    # 0 (Mesha), 2 (Mithuna), 4 (Simha), 6 (Tula), 8 (Dhanu), 10 (Kumbha),
    # 1 (Vrishabha), 3 (Karka), 5 (Kanya), 7 (Vrishchika), 9 (Makara), 11 (Meena)
    expected_lords = [
        "Mesha", "Mithuna", "Simha", "Tula", "Dhanu", "Kumbha",
        "Vrishabha", "Karka", "Kanya", "Vrishchika", "Makara", "Meena",
    ]
    actual_lords = [m.lord for m in timeline.mahadashas]
    assert actual_lords == expected_lords
    assert len(set(actual_lords)) == 12
    assert len(MANDOOKA_JUMP_OFFSETS) == 12


def test_stronger_sign_jaimini_occupant_and_modality_rules() -> None:
    # Mesha (0) has Sun + Mercury (2 planets); Tula (6) has Saturn (1 planet) -> Mesha wins
    assert stronger_sign_jaimini(0, 6, SAMPLE_CHART_LONS) == 0
    # Empty signs: Dual (2) beats Fixed (1) beats Movable (0) when lords are unselected
    assert stronger_sign_jaimini(2, 0, {}) == 2
    assert stronger_sign_jaimini(1, 0, {}) == 1


# ============================================================================
# 6. Scientific Position Uncertainty & Boundary Sensitivity Envelope Tests
# ============================================================================


def test_position_uncertainty_de440_j2000_sun_and_moon() -> None:
    sun_env = compute_position_uncertainty(2451545.0, "Sun", kernel_mode="de440", utc_year=2000.0)
    assert math.isclose(sun_env.ephemeris_model_spread_arcsec, 0.0005, abs_tol=1e-12)
    assert sun_env.compact_fit_residual_arcsec == 0.0
    assert sun_env.delta_t_propagated_arcsec == 0.0
    assert sun_env.iers_observed_window is True
    assert math.isclose(sun_env.total_uncertainty_arcsec, 0.0005, abs_tol=1e-12)
    assert len(sun_env.receipt_sha256) == 64

    moon_env = compute_position_uncertainty(2451545.0, "Moon", kernel_mode="de440", utc_year=2000.0)
    assert math.isclose(moon_env.ephemeris_model_spread_arcsec, 0.015, abs_tol=1e-12)
    assert moon_env.compact_fit_residual_arcsec == 0.0
    assert moon_env.delta_t_propagated_arcsec == 0.0
    assert math.isclose(moon_env.total_uncertainty_arcsec, 0.015, abs_tol=1e-12)


@pytest.mark.parametrize(
    ("body", "expected_ceiling"),
    [
        ("Sun", 0.00060),
        ("Moon", 0.01418),
        ("Mercury", 0.00182),
        ("Venus", 0.00182),
        ("Mars", 0.00182),
        ("Jupiter", 0.00026),
        ("Saturn", 0.00026),
        ("Uranus", 0.00026),
        ("Neptune", 0.00026),
        ("Pluto", 0.00026),
    ],
)
def test_position_uncertainty_compact_fit_residual_ceilings(body: str, expected_ceiling: float) -> None:
    env = compute_position_uncertainty(2451545.0, body, kernel_mode="compact", utc_year=2000.0)
    assert math.isclose(env.compact_fit_residual_arcsec, expected_ceiling, abs_tol=1e-12)
    assert math.isclose(
        env.total_uncertainty_arcsec,
        env.ephemeris_model_spread_arcsec + expected_ceiling,
        abs_tol=1e-12,
    )
    assert COMPACT_RESIDUAL_CEILINGS_ARCSEC[body.lower()] == expected_ceiling


def test_position_uncertainty_secular_quadratic_growth_and_historical_delta_t() -> None:
    # 2 Julian centuries before J2000 (T = -2.0 -> year ~1800, outside IERS [1962, 2026])
    jd_1800 = 2451545.0 - 2.0 * 36525.0
    env = compute_position_uncertainty(jd_1800, "Moon", kernel_mode="de440", utc_year=1799.0)
    # Ephemeris spread = 0.015 + 0.002 * (-2)^2 = 0.023 arcsec
    assert math.isclose(env.ephemeris_model_spread_arcsec, 0.023, abs_tol=1e-12)
    assert env.iers_observed_window is False
    assert env.delta_t_uncertainty_seconds == 10.0  # 1700..1800 Espenak-Meeus uncertainty = 10s
    expected_dt_prop = (13.17639648 * 3600.0 * 10.0) / 86400.0
    assert math.isclose(env.delta_t_propagated_arcsec, expected_dt_prop, rel_tol=1e-9)
    assert env.total_uncertainty_arcsec > env.ephemeris_model_spread_arcsec


def test_boundary_sensitivity_ascendant_cuspal_borderline_d60_and_d9() -> None:
    # Ascendant moves at 360 deg/day = 15 arcsec/sec.
    # Place Ascendant at 3.30 deg (0.033333... deg = 120 arcsec below the 3.333333... deg D9/Pada boundary).
    # At 15 arcsec/sec, 120 arcsec takes 8.0 seconds (< 60s) -> cuspal borderline!
    env = compute_boundary_sensitivity(3.30, is_ascendant=True)
    assert env.daily_speed_deg_per_day == 360.0
    assert env.is_cuspal_borderline is True
    assert env.d9.is_cuspal_borderline is True
    assert env.pada.is_cuspal_borderline is True
    assert math.isclose(env.d9.margin_arcsec, 120.0, abs_tol=1e-6)
    assert math.isclose(env.d9.birth_time_margin_seconds, 8.0, abs_tol=1e-6)
    assert "D9" in env.borderline_divisions
    assert "Pada" in env.borderline_divisions
    assert len(env.receipt_sha256) == 64


def test_boundary_sensitivity_safe_interior_planet_not_borderline() -> None:
    # Sun moving at 1.0 deg/day = 3600 arcsec/day = 1/24 arcsec/sec.
    # Place at 1.25 deg:
    # - D1 (30 deg): 1.25 deg from lower
    # - Nakshatra (13.333 deg): 1.25 deg from lower
    # - Pada / D9 (3.333 deg): 1.25 deg from lower
    # - D10 (3.0 deg): 1.25 deg from lower
    # - D60 (0.5 deg): midpoint of [1.0, 1.5] -> 0.25 deg = 900 arcsec from boundary!
    # At 1/24 arcsec/sec, 900 arcsec takes 21,600 seconds (6 hours) >> 60 seconds!
    env = compute_boundary_sensitivity(1.25, daily_speed_deg_per_day=1.0, is_ascendant=False)
    assert env.is_cuspal_borderline is False
    assert env.borderline_divisions == ()
    assert env.nearest_boundary_name == "D60"
    assert math.isclose(env.d60.margin_arcsec, 900.0, abs_tol=1e-9)
    assert math.isclose(env.d60.birth_time_margin_seconds, 21600.0, abs_tol=1e-6)
    assert set(env.boundaries.keys()) == {"D1", "Nakshatra", "Pada", "D9", "D10", "D60"}


def test_boundary_sensitivity_receipt_determinism_and_sign_modality() -> None:
    env1 = compute_boundary_sensitivity(44.95, is_ascendant=True)
    env2 = compute_boundary_sensitivity(44.95, is_ascendant=True)
    assert env1.receipt_sha256 == env2.receipt_sha256
    assert sign_modality(0) == "Movable"
    assert sign_modality(1) == "Fixed"
    assert sign_modality(2) == "Dual"
