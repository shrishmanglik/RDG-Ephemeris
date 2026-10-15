"""Unit and mathematical invariant tests for `ephemeris_oss.jyotish_rectification`."""

from __future__ import annotations

import math
import pytest

from ephemeris_oss.engine.receipt import canonical_hash
from ephemeris_oss.jyotish_rectification import (
    ASHTAMANGALA_DIRECTIONS,
    ASHTAMANGALA_GRAHA_BY_DIGIT,
    ASHTAMANGALA_GRAHA_CATALOG,
    ASHTAMANGALA_GRAHA_NAMES,
    BENEFIC_PRANAPADA_NAVAMSA_LORDS,
    KUNDA_DEG_PER_SECOND,
    KUNDA_HARMONIC_FACTOR,
    LAGNA_DEG_PER_SECOND,
    LifeEventSpec,
    PANCHA_TATTWA_CATALOG,
    PRANAPADA_DEG_PER_SECOND,
    SIDEREAL_DAY_SECONDS,
    TATTWA_CYCLE_MINUTES,
    TOTAL_ASHTAMANGALA_SHELLS,
    WEEKDAY_NATURAL_TATTWA,
    compute_ashtamangala_prashna,
    divide_108_cowries,
    evaluate_kunda_shuddhi,
    evaluate_pancha_tattwa,
    evaluate_pranapada_shuddhi,
    normalize_cowrie_heap,
    rectify_birth_time,
)


# ---------------------------------------------------------------------------
# 1. Kunda Shuddhi (81x Harmonic of Ascendant) Tests
# ---------------------------------------------------------------------------


def test_kunda_longitude_81x_harmonic_formula() -> None:
    """Kunda longitude equals `(lagna_lon_deg * 81.0) % 360.0` across the zodiac."""
    for lagna_deg in (0.0, 1.0, 4.444444444444445, 15.25, 123.456, 275.8, 359.9):
        res = evaluate_kunda_shuddhi(lagna_deg, moon_lon_deg=40.0)
        expected = (lagna_deg * 81.0) % 360.0
        assert math.isclose(res.kunda_lon_deg, expected, abs_tol=1e-9)
        assert res.kunda_sign_index == int(expected // 30.0)


def test_kunda_rasi_trine_or_7th_condition() -> None:
    """Kunda Rasi Shuddhi holds iff Kunda sign is 1st, 5th, 7th, or 9th from Moon sign."""
    # Moon at 10 deg Mesha (sign 0): valid Kunda signs are 0 (1st), 4 (5th), 6 (7th), 8 (9th)
    moon_lon = 10.0
    for target_kunda_sign in range(12):
        target_kunda_lon = target_kunda_sign * 30.0 + 15.0
        lagna_lon = target_kunda_lon / 81.0
        ev = evaluate_kunda_shuddhi(lagna_lon, moon_lon)
        assert ev.kunda_sign_index == target_kunda_sign
        expected_rasi_ok = target_kunda_sign in (0, 4, 6, 8)
        assert ev.rasi_trine_or_7th is expected_rasi_ok
        if expected_rasi_ok:
            assert ev.is_shuddha is True
            assert ev.seconds_to_nearest_rasi_valid == 0.0
            assert ev.seconds_to_nearest_valid == 0.0


def test_kunda_nakshatra_alignment_moon_and_lagna() -> None:
    """Kunda Nakshatra Shuddhi holds when Kunda Nakshatra ruler matches Moon or Lagna Nakshatra ruler."""
    # Moon at 1.0 deg (Ashwini, ruled by Ketu) and Lagna near 0.2 deg (Ashwini, ruled by Ketu)
    # Kunda = 0.2 * 81 = 16.2 deg -> Bharani (13.333..26.666 deg, ruled by Venus)
    ev_non_ketu = evaluate_kunda_shuddhi(0.2, 1.0)
    assert ev_non_ketu.kunda_nakshatra_name == "Bharani"
    assert ev_non_ketu.kunda_nakshatra_ruler == "Venus"
    assert ev_non_ketu.moon_nakshatra_ruler == "Ketu"
    assert ev_non_ketu.lagna_nakshatra_ruler == "Ketu"
    assert ev_non_ketu.nakshatra_alignment is False

    # Lagna = 1.5 deg (Ashwini, Ketu) -> Kunda = 1.5 * 81 = 121.5 deg (Magha, 120..133.333, ruled by Ketu)
    ev_magha = evaluate_kunda_shuddhi(1.5, 45.0)  # Moon at 45 deg = Rohini (Moon)
    assert ev_magha.kunda_nakshatra_name == "Magha"
    assert ev_magha.kunda_nakshatra_ruler == "Ketu"
    assert ev_magha.matches_lagna_nakshatra_ruler is True
    assert ev_magha.nakshatra_alignment is True
    assert ev_magha.is_shuddha is True
    assert ev_magha.seconds_to_nearest_nakshatra_valid == 0.0


def test_kunda_nearest_valid_seconds_convergence() -> None:
    """Shifting Lagna by `signed_seconds_to_nearest_valid` reaches a Kunda-valid boundary."""
    # Choose a point where neither Rasi nor Nakshatra Kunda Shuddhi holds:
    # Lagna = 0.5 deg (Ashwini, Ketu) -> Kunda = 40.5 deg (Vrishabha sign 1, Rohini ruled by Moon)
    # Place Moon at 5.0 deg (Mesha sign 0, Ashwini ruled by Ketu)
    # Then Kunda sign 1 is 2nd from Moon (not 1/5/7/9), and Kunda ruler Moon != Ketu.
    ev = evaluate_kunda_shuddhi(0.5, 5.0)
    assert ev.is_shuddha is False
    assert ev.seconds_to_nearest_valid > 0.0

    # Step slightly past the signed_seconds_to_nearest_valid boundary
    step_dir = 1.0 if ev.signed_seconds_to_nearest_valid >= 0.0 else -1.0
    adjusted_sec = ev.signed_seconds_to_nearest_valid + step_dir * 0.05
    shifted_lagna = 0.5 + adjusted_sec * LAGNA_DEG_PER_SECOND
    ev_shifted = evaluate_kunda_shuddhi(shifted_lagna, 5.0)
    assert ev_shifted.is_shuddha is True
    assert ev_shifted.seconds_to_nearest_valid == 0.0


def test_kunda_wraparound_invariance() -> None:
    """Adding multiples of 360 deg to Lagna or Moon leaves Kunda evaluation invariant."""
    ev1 = evaluate_kunda_shuddhi(87.654, 214.321)
    ev2 = evaluate_kunda_shuddhi(87.654 + 720.0, 214.321 - 360.0)
    assert math.isclose(ev1.kunda_lon_deg, ev2.kunda_lon_deg, abs_tol=1e-9)
    assert ev1.is_shuddha == ev2.is_shuddha
    assert math.isclose(ev1.seconds_to_nearest_valid, ev2.seconds_to_nearest_valid, abs_tol=1e-6)


# ---------------------------------------------------------------------------
# 2. Pranapada Shuddhi Tests
# ---------------------------------------------------------------------------


def test_pranapada_modality_offsets_and_rate() -> None:
    """Pranapada starts at Sun (Movable), Sun+240 (Fixed), or Sun+120 (Dual) at sunrise and advances 300 deg/hr."""
    # At sunrise (hours_since_sunrise = 0):
    ev_movable = evaluate_pranapada_shuddhi(0.0, 10.0, 10.0, 0.0)  # Mesha (Movable)
    assert math.isclose(ev_movable.pranapada_lon_deg, 10.0, abs_tol=1e-9)

    ev_fixed = evaluate_pranapada_shuddhi(0.0, 40.0, 10.0, 0.0)  # Vrishabha (Fixed): +240 -> 280
    assert math.isclose(ev_fixed.pranapada_lon_deg, 280.0, abs_tol=1e-9)

    ev_dual = evaluate_pranapada_shuddhi(0.0, 70.0, 10.0, 0.0)  # Mithuna (Dual): +120 -> 190
    assert math.isclose(ev_dual.pranapada_lon_deg, 190.0, abs_tol=1e-9)

    # 0.5 hours = 75 vighatis -> +150 deg
    ev_half_hr = evaluate_pranapada_shuddhi(0.0, 10.0, 10.0, 0.5)
    assert math.isclose(ev_half_hr.vighatis_since_sunrise, 75.0, abs_tol=1e-9)
    assert math.isclose(ev_half_hr.pranapada_lon_deg, 160.0, abs_tol=1e-9)


def test_pranapada_rasi_and_benefic_navamsa_rules() -> None:
    """Pranapada Shuddhi distinguishes Rasi alignment (1/5/7/9 from Moon or Lagna) and benefic D9 lord."""
    # Sun at 0.0 (Mesha), hours_since_sunrise = 0.0 -> Pranapada at 1.0 deg when hrs = 12/3600
    # At 1.0 deg Mesha: D1 sign = 0 (Mesha), D9 sign = 0 (Mesha, ruled by Mars -> malefic).
    # Put Lagna in Vrishabha (45 deg, sign 1) and Moon in Mithuna (75 deg, sign 2).
    # From Moon (2), Mesha (0) is 11th house; from Lagna (1), Mesha (0) is 12th house.
    ev_invalid = evaluate_pranapada_shuddhi(
        lagna_lon_deg=45.0,
        sun_lon_deg=0.0,
        moon_lon_deg=75.0,
        hours_since_sunrise=12.0 / 3600.0,  # 1.0 deg Pranapada
    )
    assert math.isclose(ev_invalid.pranapada_lon_deg, 1.0, abs_tol=1e-7)
    assert ev_invalid.rasi_trine_or_7th is False
    assert ev_invalid.pranapada_navamsa_lord == "Mars"
    assert ev_invalid.benefic_navamsa is False
    assert ev_invalid.is_shuddha is False
    assert ev_invalid.seconds_to_nearest_valid > 0.0

    # Advance Pranapada to 5.0 deg Mesha (2nd pada = Vrishabha D9, ruled by Venus -> benefic!)
    ev_benefic_d9 = evaluate_pranapada_shuddhi(
        lagna_lon_deg=45.0,
        sun_lon_deg=0.0,
        moon_lon_deg=75.0,
        hours_since_sunrise=60.0 / 3600.0,  # 5.0 deg Pranapada
    )
    assert ev_benefic_d9.pranapada_navamsa_lord == "Venus"
    assert ev_benefic_d9.benefic_navamsa is True
    assert ev_benefic_d9.is_shuddha is True
    assert ev_benefic_d9.seconds_to_nearest_valid == 0.0


def test_pranapada_strict_shuddhi_when_both_conditions_hold() -> None:
    """`is_strict_shuddha` is True only when both Rasi trine/7th and benefic D9 lord hold."""
    # Pranapada at 5.0 deg Mesha (sign 0, D9 Vrishabha ruled by Venus), Moon in Simha (sign 4 -> Mesha is 9th)
    ev = evaluate_pranapada_shuddhi(
        lagna_lon_deg=125.0,
        sun_lon_deg=0.0,
        moon_lon_deg=130.0,
        hours_since_sunrise=60.0 / 3600.0,
    )
    assert ev.trine_or_7th_from_moon is True
    assert ev.trine_or_7th_from_lagna is True
    assert ev.benefic_navamsa is True
    assert ev.is_strict_shuddha is True
    assert ev.seconds_to_nearest_strict_valid == 0.0


# ---------------------------------------------------------------------------
# 3. Pancha Tattwa & Antara Tattwa Cycle Tests
# ---------------------------------------------------------------------------


def test_pancha_tattwa_aroha_sequence_durations() -> None:
    """First 90 minutes from sunrise follow Aroha order: Prithvi(6), Jala(12), Tejas(18), Vayu(24), Akasha(30)."""
    expected_aroha = [
        (3.0, "Prithvi", "Earth", "Male", "Mercury", 0.0, 6.0),
        (10.0, "Jala", "Water", "Female", "Moon", 6.0, 18.0),
        (25.0, "Tejas", "Fire", "Male", "Sun", 18.0, 36.0),
        (45.0, "Vayu", "Air", "Female", "Saturn", 36.0, 60.0),
        (75.0, "Akasha", "Ether", "Neutral", "Jupiter", 60.0, 90.0),
    ]
    for min_offset, name, elem, gender, ruler, start_m, end_m in expected_aroha:
        st = evaluate_pancha_tattwa(min_offset / 60.0, weekday_index=3)
        assert st.cycle_index == 0
        assert st.cycle_direction == "Aroha"
        assert st.tattwa_name == name
        assert st.element == elem
        assert st.gender == gender
        assert st.primary_ruler == ruler
        assert math.isclose(st.maha_start_minute_in_cycle, start_m, abs_tol=1e-7)
        assert math.isclose(st.maha_end_minute_in_cycle, end_m, abs_tol=1e-7)


def test_pancha_tattwa_avaroha_reverse_sequence() -> None:
    """Second 90-minute cycle (90..180 min) reverses to Avaroha: Akasha(30), Vayu(24), Tejas(18), Jala(12), Prithvi(6)."""
    expected_avaroha = [
        (90.0 + 15.0, "Akasha", 0.0, 30.0),
        (90.0 + 40.0, "Vayu", 30.0, 54.0),
        (90.0 + 60.0, "Tejas", 54.0, 72.0),
        (90.0 + 78.0, "Jala", 72.0, 84.0),
        (90.0 + 87.0, "Prithvi", 84.0, 90.0),
    ]
    for total_min, name, start_m, end_m in expected_avaroha:
        st = evaluate_pancha_tattwa(total_min / 60.0, weekday_index=4)
        assert st.cycle_index == 1
        assert st.cycle_direction == "Avaroha"
        assert st.tattwa_name == name
        assert math.isclose(st.maha_start_minute_in_cycle, start_m, abs_tol=1e-7)
        assert math.isclose(st.maha_end_minute_in_cycle, end_m, abs_tol=1e-7)


def test_antara_tattwa_proportional_sub_periods() -> None:
    """Antara Tattwa sub-periods sum to the Maha Tattwa duration and start with the Maha Tattwa itself."""
    for hrs in (0.02, 0.2, 0.4, 0.8, 1.2, 1.7, 2.9):
        st = evaluate_pancha_tattwa(hrs, weekday_index=1)
        assert len(st.antara_sub_periods) == 5
        assert st.antara_sub_periods[0].name == st.tattwa_name
        total_sub_dur = sum(p.duration_minutes for p in st.antara_sub_periods)
        assert math.isclose(total_sub_dur, st.maha_duration_minutes, abs_tol=1e-6)
        assert (
            st.antara_tattwa.start_minute_in_cycle
            <= st.minute_in_cycle
            <= st.antara_tattwa.end_minute_in_cycle
        )


def test_pancha_tattwa_weekday_validation_and_compatibility() -> None:
    """Weekday natural Tattwa compatibility holds when active Tattwa matches the weekday's element."""
    # Wednesday (3) -> Prithvi (0..6 min from sunrise)
    st_wed = evaluate_pancha_tattwa(2.0 / 60.0, weekday_index=3)
    assert st_wed.weekday_name == "Wednesday"
    assert st_wed.weekday_natural_tattwa == "Prithvi"
    assert st_wed.weekday_compatible is True

    with pytest.raises(ValueError, match="weekday_index"):
        evaluate_pancha_tattwa(1.0, weekday_index=7)
    with pytest.raises(ValueError, match="weekday_index"):
        evaluate_pancha_tattwa(1.0, weekday_index=-1)
    with pytest.raises(ValueError, match="weekday_index"):
        evaluate_pancha_tattwa(1.0, weekday_index=True)  # type: ignore[arg-type]


# ---------------------------------------------------------------------------
# 4. Birth-Time Rectification (`rectify_birth_time`) Tests
# ---------------------------------------------------------------------------


def test_rectify_birth_time_candidate_grid_and_score_bounds() -> None:
    """`rectify_birth_time` scans the window at `step_seconds` increments with valid score bounds."""
    report = rectify_birth_time(
        nominal_jd_ut=2451545.0,
        sunrise_jd_ut=2451544.75,
        nominal_lagna_lon_deg=119.8,
        sun_lon_deg=256.0,
        moon_lon_deg=42.0,
        window_minutes=5.0,
        step_seconds=30.0,
    )
    # 5 minutes = 300 seconds -> -300..+300 at 30s steps = 21 candidates
    assert len(report.all_candidates) == 21
    assert report.nominal_candidate.offset_seconds == 0.0
    assert math.isclose(report.nominal_candidate.proximity_score, 10.0, abs_tol=1e-9)
    assert report.best_candidate.rank == 1
    assert report.best_candidate == report.top_candidates[0]
    assert math.isclose(
        report.rectified_jd_ut,
        report.nominal_jd_ut + report.offset_seconds / 86400.0,
        abs_tol=1e-9,
    )

    for cand in report.all_candidates:
        assert 0.0 <= cand.kunda_score <= 35.0
        assert 0.0 <= cand.pranapada_score <= 30.0
        assert 0.0 <= cand.tattwa_score <= 15.0
        assert 0.0 <= cand.proximity_score <= 10.0
        assert 0.0 <= cand.life_event_score <= 10.0
        assert 0.0 <= cand.total_score <= 100.0


def test_rectify_birth_time_detects_d1_d9_d10_d60_cusp_transitions() -> None:
    """When nominal Lagna sits near a 30-degree Rasi boundary, D1, D9, D10, and D60 transitions are detected."""
    # Nominal Lagna at 29.95 deg Mesha; within +/- 5 minutes (+/- 1.25 deg), Lagna crosses 30.0 deg into Vrishabha!
    report = rectify_birth_time(
        nominal_jd_ut=2451545.0,
        sunrise_jd_ut=2451544.75,
        nominal_lagna_lon_deg=29.95,
        sun_lon_deg=10.0,
        moon_lon_deg=125.0,
        window_minutes=5.0,
        step_seconds=15.0,
    )
    vargas_found = {t.varga for t in report.varga_transitions}
    assert "D1" in vargas_found
    assert "D9" in vargas_found
    assert "D10" in vargas_found
    assert "D60" in vargas_found

    d1_trans = [t for t in report.varga_transitions if t.varga == "D1"]
    assert len(d1_trans) == 1
    assert d1_trans[0].from_sign_name == "Mesha"
    assert d1_trans[0].to_sign_name == "Vrishabha"
    assert math.isclose(d1_trans[0].cusp_longitude_deg, 30.0, abs_tol=1e-7)
    expected_sec = (30.0 - 29.95) / LAGNA_DEG_PER_SECOND
    assert math.isclose(d1_trans[0].offset_seconds_from_nominal, expected_sec, abs_tol=1e-4)


def test_rectify_birth_time_life_events_correlation() -> None:
    """Passing `life_events` rewards candidates whose Varga Lagna and Dasha match the specified events."""
    events = [
        LifeEventSpec(
            name="Career Promotion",
            event_jd_ut=2451545.0 + 3652.5,
            category="career",
            varga="D10",
            house=10,
            signifying_planet="Venus",
            expected_varga_lagna_sign=5,
        ),
        {
            "name": "Marriage",
            "category": "marriage",
            "varga": "D9",
            "house": 7,
            "signifying_planet": "Jupiter",
        },
    ]
    planets = {
        "Sun": 250.0,
        "Moon": 40.0,
        "Mars": 15.0,
        "Mercury": 245.0,
        "Jupiter": 95.0,
        "Venus": 185.0,
        "Saturn": 305.0,
    }
    report = rectify_birth_time(
        nominal_jd_ut=2451545.0,
        sunrise_jd_ut=2451544.75,
        nominal_lagna_lon_deg=16.6,
        sun_lon_deg=250.0,
        moon_lon_deg=40.0,
        window_minutes=10.0,
        step_seconds=20.0,
        planet_longitudes=planets,
        life_events=events,
    )
    scores = {cand.life_event_score for cand in report.all_candidates}
    # Different D9/D10 cusps across the 20-minute span produce distinct life_event_scores
    assert len(scores) >= 2
    assert report.receipt_sha256 == canonical_hash(report.receipt)


def test_rectify_birth_time_validation_errors() -> None:
    """Invalid window_minutes or step_seconds raise ValueError."""
    with pytest.raises(ValueError, match="window_minutes"):
        rectify_birth_time(2451545.0, 2451544.75, 10.0, 20.0, 30.0, window_minutes=0.0)
    with pytest.raises(ValueError, match="step_seconds"):
        rectify_birth_time(2451545.0, 2451544.75, 10.0, 20.0, 30.0, step_seconds=-5.0)


# ---------------------------------------------------------------------------
# 5. Kerala Ashtamangala Prashna Engine Tests
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    ("digit", "expected_graha", "expected_direction", "expected_oja", "expected_benefic"),
    [
        (1, "Sun", "East", True, False),
        (2, "Mars", "South-East", False, False),
        (3, "Jupiter", "South", True, True),
        (4, "Mercury", "South-West", False, True),
        (5, "Venus", "West", True, True),
        (6, "Saturn", "North-West", False, False),
        (7, "Moon", "North", True, True),
        (8, "Rahu", "North-East", False, False),
    ],
)
def test_ashtamangala_directional_graha_catalog(
    digit: int,
    expected_graha: str,
    expected_direction: str,
    expected_oja: bool,
    expected_benefic: bool,
) -> None:
    """Each Ashtamangala digit 1..8 maps to its classical Prashna Marga Ch. 5 Graha and direction."""
    res = compute_ashtamangala_prashna(digit, digit, digit)
    assert res.chinta_graha == expected_graha
    assert res.chinta_direction == expected_direction
    assert res.present_pile.is_oja is expected_oja
    assert res.chinta_is_benefic is expected_benefic
    assert ASHTAMANGALA_GRAHA_NAMES[digit] == expected_graha
    assert ASHTAMANGALA_DIRECTIONS[digit] == expected_direction


def test_ashtamangala_number_sum_nikshepa_and_arudha() -> None:
    """Verify `ashtamangala_number`, `total_sum`, `nikshepa_rasi`, and `ashtamangala_arudha_sign`."""
    # Piles: left=3 (Jupiter), center=5 (Venus), right=7 (Moon)
    res = compute_ashtamangala_prashna(
        3,
        5,
        7,
        lagna_lon_deg=35.0,
        sun_lon_deg=120.0,
        moon_lon_deg=65.0,
        gulika_lon_deg=95.0,
    )
    assert res.ashtamangala_number == 357
    assert res.total_sum == 15
    assert res.is_odd_sum is True
    assert res.parity_classification == "Oja"
    assert res.oja_pile_count == 3
    assert res.yugma_pile_count == 0
    assert res.bhuta_graha == "Jupiter"
    assert res.chinta_graha == "Venus"
    assert res.bhavishya_graha == "Moon"

    # nikshepa_rasi = (3 + 5 + 7 - 1) % 12 = 14 % 12 = 2 (Mithuna)
    assert res.nikshepa_rasi == 2
    assert res.nikshepa_rasi_name == "Mithuna"

    # ashtamangala_arudha_sign = (3 * 10 + 5) % 12 = 35 % 12 = 11 (Meena)
    assert res.ashtamangala_arudha_sign == 11
    assert res.ashtamangala_arudha_sign_name == "Meena"


def test_ashtamangala_trisphuta_and_mrityu_sphuta_integration() -> None:
    """Verify Trisphuta = `(lagna + moon + gulika) % 360` and Mrityu Sphuta = `(7 * gulika + sun) % 360`."""
    res = compute_ashtamangala_prashna(
        2,
        4,
        6,
        lagna_lon_deg=45.5,
        sun_lon_deg=110.25,
        moon_lon_deg=210.75,
        gulika_lon_deg=15.0,
    )
    assert res.ashtamangala_number == 246
    assert res.total_sum == 12
    assert res.is_odd_sum is False
    assert res.parity_classification == "Yugma"

    expected_tri = (45.5 + 210.75 + 15.0) % 360.0  # 271.25 deg
    expected_mrityu = (7.0 * 15.0 + 110.25) % 360.0  # 215.25 deg
    assert math.isclose(res.trisphuta_lon_deg, expected_tri, abs_tol=1e-9)
    assert math.isclose(res.mrityu_sphuta_lon_deg, expected_mrityu, abs_tol=1e-9)
    assert res.trisphuta_sign_index == int(expected_tri // 30.0)
    assert res.mrityu_sphuta_sign_index == int(expected_mrityu // 30.0)
    assert res.receipt_sha256 == canonical_hash(res.receipt)


def test_ashtamangala_mrityu_affliction_detection() -> None:
    """When Mrityu Sphuta lands in the same sign as Trisphuta, `mrityu_afflicts_trisphuta` is True."""
    # Choose gulika = 0.0, sun = 10.0 -> Mrityu Sphuta = 10.0 (Mesha, Ashwini)
    # Choose lagna = 4.0, moon = 6.0 -> Trisphuta = 10.0 (Mesha, Ashwini)
    res = compute_ashtamangala_prashna(
        1,
        3,
        5,
        lagna_lon_deg=4.0,
        sun_lon_deg=10.0,
        moon_lon_deg=6.0,
        gulika_lon_deg=0.0,
    )
    assert res.mrityu_afflicts_trisphuta is True
    assert "Krichhra" in res.nimitta_verdict


def test_cowrie_heap_normalization_and_108_partition() -> None:
    """`normalize_cowrie_heap` maps multiples of 8 to 8, and `divide_108_cowries` enforces sum == 108."""
    assert [normalize_cowrie_heap(n) for n in range(1, 17)] == [
        1, 2, 3, 4, 5, 6, 7, 8,
        1, 2, 3, 4, 5, 6, 7, 8,
    ]
    piles = divide_108_cowries(32, 40, 36)
    assert piles == (8, 8, 4)
    assert TOTAL_ASHTAMANGALA_SHELLS == 108

    with pytest.raises(ValueError, match="108"):
        divide_108_cowries(30, 30, 30)
    with pytest.raises(ValueError, match="positive integer"):
        normalize_cowrie_heap(0)


@pytest.mark.parametrize(
    ("a", "b", "c"),
    [
        (0, 4, 4),
        (4, 9, 4),
        (4, 4, -1),
        (True, 4, 4),  # type: ignore[list-item]
    ],
)
def test_ashtamangala_invalid_piles_raise_value_error(a: int, b: int, c: int) -> None:
    """Pile values outside 1..8 or booleans raise ValueError."""
    with pytest.raises(ValueError, match="1..8"):
        compute_ashtamangala_prashna(a, b, c)


@pytest.mark.parametrize("weekday", [0, 1, 2, 3, 4, 5, 6])
def test_all_seven_weekdays_pancha_tattwa_cycle(weekday: int) -> None:
    """Every weekday 0..6 produces valid Pancha Tattwa state and matches its natural Tattwa window."""
    natural_name = WEEKDAY_NATURAL_TATTWA[weekday]
    # Find the Aroha midpoint for that natural Tattwa in Cycle 0
    cursor = 0.0
    target_mid_min = 0.0
    for item in PANCHA_TATTWA_CATALOG:
        if item.name == natural_name:
            target_mid_min = cursor + 0.5 * item.duration_minutes
            break
        cursor += item.duration_minutes

    st = evaluate_pancha_tattwa(target_mid_min / 60.0, weekday_index=weekday)
    assert st.tattwa_name == natural_name
    assert st.weekday_compatible is True
    assert 0.0 <= st.maha_fraction_elapsed <= 1.0


def test_pranapada_nearest_valid_seconds_convergence() -> None:
    """Advancing hours_since_sunrise by `signed_seconds_to_nearest_valid / 3600` reaches a valid Pranapada."""
    ev = evaluate_pranapada_shuddhi(
        lagna_lon_deg=45.0,
        sun_lon_deg=0.0,
        moon_lon_deg=75.0,
        hours_since_sunrise=12.0 / 3600.0,
    )
    assert ev.is_shuddha is False
    assert ev.seconds_to_nearest_valid > 0.0

    step_dir = 1.0 if ev.signed_seconds_to_nearest_valid >= 0.0 else -1.0
    shifted_hrs = (12.0 + ev.signed_seconds_to_nearest_valid + step_dir * 0.05) / 3600.0
    ev2 = evaluate_pranapada_shuddhi(
        lagna_lon_deg=45.0,
        sun_lon_deg=0.0,
        moon_lon_deg=75.0,
        hours_since_sunrise=shifted_hrs,
    )
    assert ev2.is_shuddha is True
    assert ev2.seconds_to_nearest_valid == 0.0

