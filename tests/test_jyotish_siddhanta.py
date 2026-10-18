"""Unit and mathematical invariant tests for jyotish_siddhanta (Surya Siddhanta and Vedanga Jyotisha)."""

from __future__ import annotations

import math
import pytest

from ephemeris_oss.jyotish_siddhanta import (
    KALI_YUGA_EPOCH_JD,
    KALI_YUGA_SOLAR_YEARS,
    KALPA_MAHAYUGAS,
    KALPA_MANDOCCA_REVOLUTIONS,
    KALPA_SOLAR_YEARS,
    MAHAYUGA_BHAGANA,
    MAHAYUGA_SAVANA_DAYS,
    MAHAYUGA_SOLAR_YEARS,
    MANDOCCA_KALI_EPOCH_DEG,
    MANDA_PARIDHI_EVEN_ODD_DEG,
    SIGHRA_PARIDHI_EVEN_ODD_DEG,
    SPASHTA_GRAHA_ORDER,
    TARAGRAHA_BODIES,
    VEDANGA_AYANA_NAMES,
    VEDANGA_BHAMSHA_PER_NAKSHATRA,
    VEDANGA_EPOCH_NAKSHATRA_INDEX,
    VEDANGA_KSHAYA_TITHIS_PER_YUGA,
    VEDANGA_NAKSHATRA_ORDER,
    VEDANGA_RITU_NAMES,
    VEDANGA_SAMVATSARA_NAMES,
    VEDANGA_SAVANA_DAYS_PER_AYANA,
    VEDANGA_SAVANA_DAYS_PER_RITU,
    VEDANGA_SAVANA_DAYS_PER_YEAR,
    VEDANGA_YUGA_ADHIKA_MASAS,
    VEDANGA_YUGA_LUNAR_NAKSHATRAS,
    VEDANGA_YUGA_PARVANS,
    VEDANGA_YUGA_SAURA_DAYS,
    VEDANGA_YUGA_SAVANA_DAYS,
    VEDANGA_YUGA_SIDEREAL_LUNAR_MONTHS,
    VEDANGA_YUGA_SOLAR_NAKSHATRAS,
    VEDANGA_YUGA_SYNODIC_MONTHS,
    VEDANGA_YUGA_TITHIS,
    VEDANGA_YUGA_YEARS,
    compare_siddhanta_with_modern,
    compute_ahargana,
    compute_manda_paridhi,
    compute_manda_samskara,
    compute_mandocca_longitude,
    compute_sighra_paridhi,
    compute_sighra_samskara,
    compute_vedanga_yuga_state,
    surya_siddhanta_mean_longitudes,
    surya_siddhanta_true_positions,
)


# ---------------------------------------------------------------------------
# 1. Kali Yuga Epoch, Ahargana & Mahayuga Bhagana Constants
# ---------------------------------------------------------------------------


def test_kali_yuga_epoch_constants_and_mahayuga_bhagana():
    assert KALI_YUGA_EPOCH_JD == 588465.5
    assert MAHAYUGA_SOLAR_YEARS == 4_320_000
    assert KALI_YUGA_SOLAR_YEARS == 432_000
    assert MAHAYUGA_SAVANA_DAYS == 1_577_917_828
    assert KALPA_SOLAR_YEARS == 4_320_000_000
    assert KALPA_MAHAYUGAS == 1_000

    assert MAHAYUGA_BHAGANA["sun"] == 4_320_000
    assert MAHAYUGA_BHAGANA["moon"] == 57_753_336
    assert MAHAYUGA_BHAGANA["moon_apogee"] == 488_203
    assert MAHAYUGA_BHAGANA["moon_node"] == -232_238
    assert MAHAYUGA_BHAGANA["mars"] == 2_296_832
    assert MAHAYUGA_BHAGANA["mercury_sighrocca"] == 17_937_060
    assert MAHAYUGA_BHAGANA["jupiter"] == 364_220
    assert MAHAYUGA_BHAGANA["venus_sighrocca"] == 7_022_376
    assert MAHAYUGA_BHAGANA["saturn"] == 146_568


def test_compute_ahargana_at_kali_yuga_epoch_is_zero():
    ahargana = compute_ahargana(588465.5)
    assert ahargana == 0.0
    assert math.isclose(compute_ahargana(588465.5 + 365.258756), 365.258756, abs_tol=1e-12)
    assert math.isclose(compute_ahargana(588465.5 - 100.0), -100.0, abs_tol=1e-12)


def test_compute_ahargana_rejects_non_finite():
    with pytest.raises(ValueError, match="finite"):
        compute_ahargana(float("nan"))
    with pytest.raises(ValueError, match="finite"):
        compute_ahargana(float("inf"))


def test_mean_longitudes_at_kali_yuga_epoch_all_zero():
    mean = surya_siddhanta_mean_longitudes(588465.5)
    assert mean.jd_ut == 588465.5
    assert mean.ahargana == 0.0
    assert len(mean) == 9
    for body, lon in mean.items():
        assert lon == 0.0, f"Expected 0.0 deg at Kali Yuga epoch for {body}, got {lon}"
    assert mean.sun == 0.0
    assert mean.moon == 0.0
    assert mean.moon_apogee == 0.0
    assert mean.moon_node == 0.0
    assert mean.mars == 0.0
    assert mean.mercury_sighrocca == 0.0
    assert mean.jupiter == 0.0
    assert mean.venus_sighrocca == 0.0
    assert mean.saturn == 0.0
    assert mean.mercury == 0.0
    assert mean.venus == 0.0
    assert mean.rahu == 0.0
    assert mean.ketu == 180.0
    assert len(mean.receipt_sha256) == 64


def test_mean_longitudes_after_one_sidereal_solar_year():
    # One Surya Siddhanta sidereal solar year = 1,577,917,828 / 4,320,000 = 365.2587564814815 Savana days
    solar_year_days = MAHAYUGA_SAVANA_DAYS / float(MAHAYUGA_SOLAR_YEARS)
    mean = surya_siddhanta_mean_longitudes(KALI_YUGA_EPOCH_JD + solar_year_days)
    assert math.isclose(mean.ahargana, solar_year_days, abs_tol=1e-9)
    # Sun completes exactly 1 revolution -> 0.0 deg (or 360.0 wrapped)
    assert math.isclose(mean["sun"] % 360.0, 0.0, abs_tol=1e-9) or math.isclose(mean["sun"], 360.0, abs_tol=1e-9)
    # Mars moves 2,296,832 / 4,320,000 * 360 = 191.40266666666668 deg
    expected_mars = (2_296_832 / 4_320_000) * 360.0
    assert math.isclose(mean["mars"], expected_mars, abs_tol=1e-9)


def test_mean_longitudes_retrograde_moon_node_motion():
    # After 1000 Savana days, Rahu (moon_node) moves retrograde (decreasing longitude from 360)
    mean = surya_siddhanta_mean_longitudes(KALI_YUGA_EPOCH_JD + 1000.0)
    expected_node = ((-232_238.0 * 1000.0 / MAHAYUGA_SAVANA_DAYS) * 360.0) % 360.0
    assert math.isclose(mean["moon_node"], expected_node, abs_tol=1e-12)
    assert 300.0 < mean["moon_node"] < 360.0
    assert math.isclose(mean["rahu"], expected_node, abs_tol=1e-12)
    assert math.isclose(mean["ketu"], (expected_node + 180.0) % 360.0, abs_tol=1e-12)


def test_mean_longitudes_mapping_access_and_unknown_key():
    mean = surya_siddhanta_mean_longitudes(KALI_YUGA_EPOCH_JD + 500.0)
    assert mean["SUN"] == mean.sun
    assert mean["mercury"] == mean.sun
    assert mean["venus"] == mean.sun
    assert set(mean.keys()) == set(MAHAYUGA_BHAGANA.keys())
    assert len(list(mean.values())) == 9
    with pytest.raises(KeyError):
        _ = mean["pluto"]


# ---------------------------------------------------------------------------
# 2. Variable Manda Paridhi & Manda Samskara (Equation of Center)
# ---------------------------------------------------------------------------


def test_variable_manda_paridhi_even_and_odd_quadrants():
    for body, (p_even, p_odd) in MANDA_PARIDHI_EVEN_ODD_DEG.items():
        # Even quadrant boundaries: 0 deg and 180 deg
        assert math.isclose(compute_manda_paridhi(body, 0.0), p_even, abs_tol=1e-12)
        assert math.isclose(compute_manda_paridhi(body, 180.0), p_even, abs_tol=1e-12)
        # Odd quadrant peaks: 90 deg and 270 deg
        assert math.isclose(compute_manda_paridhi(body, 90.0), p_odd, abs_tol=1e-12)
        assert math.isclose(compute_manda_paridhi(body, 270.0), p_odd, abs_tol=1e-12)
        # Midpoint angle 30 deg -> sin(30) = 0.5 -> arithmetic mean of p_even and p_odd
        assert math.isclose(compute_manda_paridhi(body, 30.0), 0.5 * (p_even + p_odd), abs_tol=1e-12)


def test_manda_samskara_zero_at_apogee_and_perigee():
    # When mean_lon == mandocca (kendra = 0) or mean_lon == mandocca + 180 (kendra = 180), Manda Phala is 0
    apogee = MANDOCCA_KALI_EPOCH_DEG["sun"]
    res_apogee = compute_manda_samskara(apogee, apogee, "sun")
    assert math.isclose(res_apogee.kendra_deg, 0.0, abs_tol=1e-12)
    assert math.isclose(res_apogee.manda_phala_deg, 0.0, abs_tol=1e-12)
    assert math.isclose(res_apogee.corrected_longitude_deg, apogee, abs_tol=1e-12)

    perigee = (apogee + 180.0) % 360.0
    res_perigee = compute_manda_samskara(perigee, apogee, "sun")
    assert math.isclose(res_perigee.kendra_deg, 180.0, abs_tol=1e-12)
    assert math.isclose(res_perigee.manda_phala_deg, 0.0, abs_tol=1e-12)
    assert math.isclose(res_perigee.corrected_longitude_deg, perigee, abs_tol=1e-12)


def test_manda_samskara_maximum_equation_of_center_for_sun_and_moon():
    # At kendra = 90 deg (mean_lon = mandocca - 90), sin(kendra) = 1.0, effective paridhi = P_odd
    # For Sun: P_odd = 13 + 40/60 = 13.6666667 deg -> arcsin(13.6666667 / 360) = 2.175657 deg (~2 deg 10.5')
    res_sun = compute_manda_samskara(0.0, 90.0, "sun")
    expected_sun_phala = math.degrees(math.asin((13.0 + 40.0 / 60.0) / 360.0))
    assert math.isclose(res_sun.effective_paridhi_deg, 13.0 + 40.0 / 60.0, abs_tol=1e-12)
    assert math.isclose(res_sun.manda_phala_deg, expected_sun_phala, abs_tol=1e-12)
    assert math.isclose(res_sun.manda_phala_deg, 2.17564035, abs_tol=1e-6)

    # For Moon: P_odd = 31 + 40/60 = 31.6666667 deg -> arcsin(31.6666667 / 360) = 5.046611 deg (~5 deg 02.8')
    res_moon = compute_manda_samskara(0.0, 90.0, "moon")
    expected_moon_phala = math.degrees(math.asin((31.0 + 40.0 / 60.0) / 360.0))
    assert math.isclose(res_moon.manda_phala_deg, expected_moon_phala, abs_tol=1e-12)
    assert math.isclose(res_moon.manda_phala_deg, 5.04642863, abs_tol=1e-6)


def test_manda_samskara_antisymmetry_around_apogee():
    # Equal angular distance before vs after apogee yields equal magnitude, opposite sign Manda Phala
    r_plus = compute_manda_samskara(50.0, 100.0, "mars")   # kendra = +50 deg
    r_minus = compute_manda_samskara(150.0, 100.0, "mars") # kendra = 310 deg (-50 deg)
    assert math.isclose(r_plus.effective_paridhi_deg, r_minus.effective_paridhi_deg, abs_tol=1e-12)
    assert math.isclose(r_plus.manda_phala_deg, -r_minus.manda_phala_deg, abs_tol=1e-12)
    assert r_plus.manda_phala_deg > 0.0
    assert r_minus.manda_phala_deg < 0.0


def test_mandocca_longitude_evolution_and_errors():
    # At Ahargana = 0, Sun Mandocca equals its Kali Yuga epoch constant
    assert math.isclose(
        compute_mandocca_longitude("sun", 0.0),
        MANDOCCA_KALI_EPOCH_DEG["sun"],
        abs_tol=1e-12,
    )
    # Moon Mandocca uses moon_apogee
    assert math.isclose(compute_mandocca_longitude("moon", 0.0, moon_apogee_deg=123.45), 123.45, abs_tol=1e-12)
    with pytest.raises(ValueError, match="Unknown body"):
        compute_mandocca_longitude("uranus", 0.0)
    with pytest.raises(ValueError, match="Unknown body"):
        compute_manda_paridhi("uranus", 45.0)
    with pytest.raises(ValueError, match="Unsupported body"):
        compute_manda_samskara(0.0, 90.0, "uranus")


# ---------------------------------------------------------------------------
# 3. Variable Sighra Paridhi & Sighra Samskara (Parallax Reduction)
# ---------------------------------------------------------------------------


def test_variable_sighra_paridhi_even_and_odd_quadrants():
    for body, (s_even, s_odd) in SIGHRA_PARIDHI_EVEN_ODD_DEG.items():
        assert math.isclose(compute_sighra_paridhi(body, 0.0), s_even, abs_tol=1e-12)
        assert math.isclose(compute_sighra_paridhi(body, 180.0), s_even, abs_tol=1e-12)
        assert math.isclose(compute_sighra_paridhi(body, 90.0), s_odd, abs_tol=1e-12)
        assert math.isclose(compute_sighra_paridhi(body, 270.0), s_odd, abs_tol=1e-12)


def test_sighra_samskara_zero_at_conjunction_and_opposition():
    for body in TARAGRAHA_BODIES:
        # Kendra = 0 deg (planet aligned with Sighrocca): Sighra Phala = 0, Karna = 1 + r
        r_conj = compute_sighra_samskara(120.0, 120.0, body)
        s_even, _ = SIGHRA_PARIDHI_EVEN_ODD_DEG[body]
        assert math.isclose(r_conj.sighra_phala_deg, 0.0, abs_tol=1e-12)
        assert math.isclose(r_conj.sighra_karna, 1.0 + s_even / 360.0, abs_tol=1e-12)

        # Kendra = 180 deg (planet opposite Sighrocca): Sighra Phala = 0, Karna = 1 - r
        r_opp = compute_sighra_samskara(120.0, 300.0, body)
        assert math.isclose(r_opp.sighra_phala_deg, 0.0, abs_tol=1e-12)
        assert math.isclose(r_opp.sighra_karna, 1.0 - s_even / 360.0, abs_tol=1e-12)


def test_sighra_samskara_quadrature_and_antisymmetry():
    # At Kendra = 90 deg for Mars: S_odd = 232 -> r = 232 / 360 -> atan2(r, 1.0) = 32.80 deg
    r90 = compute_sighra_samskara(0.0, 90.0, "mars")
    r_expected = 232.0 / 360.0
    assert math.isclose(r90.effective_paridhi_deg, 232.0, abs_tol=1e-12)
    assert math.isclose(r90.sighra_karna, math.hypot(1.0, r_expected), abs_tol=1e-12)
    assert math.isclose(r90.sighra_phala_deg, math.degrees(math.atan2(r_expected, 1.0)), abs_tol=1e-12)

    # Antisymmetry at Kendra = 270 deg (-90 deg)
    r270 = compute_sighra_samskara(90.0, 0.0, "mars")
    assert math.isclose(r270.sighra_phala_deg, -r90.sighra_phala_deg, abs_tol=1e-12)


def test_sighra_samskara_rejects_non_taragraha():
    with pytest.raises(ValueError, match="Unknown Taragraha"):
        compute_sighra_paridhi("sun", 45.0)
    with pytest.raises(ValueError, match="Unsupported Taragraha"):
        compute_sighra_samskara(10.0, 50.0, "moon")


# ---------------------------------------------------------------------------
# 4. Full Spashta Graha Engine & Modern Comparison
# ---------------------------------------------------------------------------


def test_surya_siddhanta_true_positions_all_nine_grahas():
    # Test at J2000.0 (JD 2451545.0 -> Ahargana = 1,863,079.5 days)
    spashta = surya_siddhanta_true_positions(2451545.0)
    assert spashta.jd_ut == 2451545.0
    assert math.isclose(spashta.ahargana, 2451545.0 - 588465.5, abs_tol=1e-9)
    assert tuple(spashta.keys()) == SPASHTA_GRAHA_ORDER
    assert len(spashta) == 9
    assert len(spashta.receipt_sha256) == 64

    for body in SPASHTA_GRAHA_ORDER:
        p = spashta.planets[body]
        assert 0.0 <= p.true_longitude_deg < 360.0
        assert p.longitude_deg == p.true_longitude_deg
        assert 0 <= p.rasi_index <= 11
        assert 0.0 <= p.degree_in_rasi < 30.0
        assert 0 <= p.nakshatra_index <= 26
        assert 1 <= p.pada <= 4
        assert spashta[body] == p.true_longitude_deg

    # Rahu and Ketu must be exactly 180 deg apart
    assert math.isclose((spashta.rahu + 180.0) % 360.0, spashta.ketu, abs_tol=1e-12)

    # Luminaries have Sighra fields set to None; Taragrahas have populated Sighra fields
    assert spashta.planets["sun"].sighra_phala_deg is None
    assert spashta.planets["moon"].sighra_phala_deg is None
    for tara in TARAGRAHA_BODIES:
        tp = spashta.planets[tara]
        assert tp.sighrocca_deg is not None
        assert tp.sighra_karna is not None and tp.sighra_karna > 0.0
        assert tp.sighra_phala_deg is not None


def test_surya_siddhanta_true_positions_at_kali_yuga_epoch():
    # At Kali Yuga epoch (JD 588465.5), all mean longitudes and Sighroccas are 0.0 deg.
    # Because Sun, Mars, Mercury, Jupiter, Venus, Saturn have non-zero Mandocca,
    # their Manda Samskara shifts their true longitudes away from 0.0 deg, whereas
    # the Moon has both mean_lon=0 and moon_apogee=0, so Moon true_lon == 0.0 deg!
    spashta = surya_siddhanta_true_positions(KALI_YUGA_EPOCH_JD)
    assert math.isclose(spashta.moon, 0.0, abs_tol=1e-12)
    assert math.isclose(spashta.rahu, 0.0, abs_tol=1e-12)
    assert math.isclose(spashta.ketu, 180.0, abs_tol=1e-12)
    # Sun has Mandocca at 77d17' (> 0), so kendra = 77d17', Manda Phala > 0 -> true Sun ~ 2.13 deg
    assert 2.0 < spashta.sun < 2.25


def test_surya_siddhanta_true_positions_deterministic_receipt():
    r1 = surya_siddhanta_true_positions(2460000.5)
    r2 = surya_siddhanta_true_positions(2460000.5)
    r3 = surya_siddhanta_true_positions(2460001.5)
    assert r1.receipt_sha256 == r2.receipt_sha256
    assert r1.receipt_sha256 != r3.receipt_sha256


def test_compare_siddhanta_with_modern_deltas_and_receipt():
    jd = 2451545.0
    spashta = surya_siddhanta_true_positions(jd)
    # Create synthetic modern reference longitudes offset by known amounts
    modern = {
        "sun": (spashta.sun - 1.5) % 360.0,       # Siddhanta is +1.5 deg ahead
        "moon": (spashta.moon + 2.25) % 360.0,    # Siddhanta is -2.25 deg behind
        "mars": spashta.mars,                     # Exact 0.0 deg match
        "jupiter": (spashta.jupiter - 0.5) % 360.0,
    }
    cmp_res = compare_siddhanta_with_modern(jd, modern)
    assert cmp_res.jd_ut == jd
    assert math.isclose(cmp_res.angular_deltas_deg["sun"], 1.5, abs_tol=1e-9)
    assert math.isclose(cmp_res.angular_deltas_deg["moon"], -2.25, abs_tol=1e-9)
    assert math.isclose(cmp_res.angular_deltas_deg["mars"], 0.0, abs_tol=1e-9)
    assert math.isclose(cmp_res.angular_deltas_deg["jupiter"], 0.5, abs_tol=1e-9)
    assert math.isclose(cmp_res.comparisons["sun"].delta_arcminutes, 90.0, abs_tol=1e-9)
    assert math.isclose(cmp_res.max_abs_delta_deg, 2.25, abs_tol=1e-9)
    assert math.isclose(cmp_res.mean_abs_delta_deg, (1.5 + 2.25 + 0.0 + 0.5) / 4.0, abs_tol=1e-9)
    assert len(cmp_res.receipt_sha256) == 64


def test_compare_siddhanta_with_modern_zero_aries_wraparound():
    # Verify shortest signed arc across 0 deg / 360 deg boundary
    jd = KALI_YUGA_EPOCH_JD
    # At Kali Yuga epoch, Moon is at 0.0 deg; if modern is at 359.0 deg, signed delta is +1.0 deg
    cmp_res = compare_siddhanta_with_modern(jd, {"moon": 359.0})
    assert math.isclose(cmp_res.angular_deltas_deg["moon"], 1.0, abs_tol=1e-9)
    assert math.isclose(cmp_res.abs_deltas_deg["moon"], 1.0, abs_tol=1e-9)


def test_compare_siddhanta_with_modern_validation():
    with pytest.raises(ValueError, match="at least one planet"):
        compare_siddhanta_with_modern(2451545.0, {})
    with pytest.raises(ValueError, match="Unsupported planet key"):
        compare_siddhanta_with_modern(2451545.0, {"chiron": 15.0})


# ---------------------------------------------------------------------------
# 5. Lagadha Vedanga Jyotisha 5-Year Yuga Invariants
# ---------------------------------------------------------------------------


def test_vedanga_jyotisha_fundamental_yuga_constants():
    assert VEDANGA_YUGA_YEARS == 5
    assert VEDANGA_YUGA_SAVANA_DAYS == 1_830
    assert VEDANGA_YUGA_SAURA_DAYS == 1_800
    assert VEDANGA_YUGA_SYNODIC_MONTHS == 62
    assert VEDANGA_YUGA_TITHIS == 1_860
    assert VEDANGA_YUGA_SIDEREAL_LUNAR_MONTHS == 67
    assert VEDANGA_YUGA_LUNAR_NAKSHATRAS == 1_809
    assert VEDANGA_YUGA_SOLAR_NAKSHATRAS == 135
    assert VEDANGA_YUGA_ADHIKA_MASAS == 2
    assert VEDANGA_YUGA_PARVANS == 124
    assert VEDANGA_BHAMSHA_PER_NAKSHATRA == 124
    assert VEDANGA_KSHAYA_TITHIS_PER_YUGA == 30
    assert VEDANGA_SAVANA_DAYS_PER_YEAR == 366
    assert VEDANGA_SAVANA_DAYS_PER_AYANA == 183
    assert VEDANGA_SAVANA_DAYS_PER_RITU == 61
    assert VEDANGA_SAMVATSARA_NAMES == (
        "Samvatsara",
        "Parivatsara",
        "Idavatsara",
        "Anuvatsara",
        "Idvatsara",
    )
    assert VEDANGA_NAKSHATRA_ORDER[0] == "Dhanishta"
    assert len(VEDANGA_NAKSHATRA_ORDER) == 27


def test_vedanga_yuga_epoch_day_zero_state():
    # At days_into_yuga = 0.0: Year 1 (Samvatsara), Uttarayana, Shishira Ritu,
    # Month 1, Tithi 1 (Shukla Pratipada), Sun and Moon conjoined at start of Dhanishta, Bhamsha 0.0
    state = compute_vedanga_yuga_state(0.0)
    assert state.days_into_yuga == 0.0
    assert state.yuga_cycle == 0
    assert state.year_index == 0
    assert state.year == 1
    assert state.samvatsara_name == "Samvatsara"
    assert state.ayana == "Uttarayana"
    assert state.ayana_number_in_yuga == 1
    assert state.ritu_name == "Shishira"
    assert state.synodic_month_number == 1
    assert state.is_adhika_masa is False
    assert state.adhika_masas_elapsed == 0
    assert state.tithi == 1
    assert state.paksha == "Shukla"
    assert state.solar_nakshatra == "Dhanishta"
    assert state.solar_nakshatra_index == VEDANGA_EPOCH_NAKSHATRA_INDEX
    assert state.vedanga_solar_nakshatra_index == 0
    assert state.lunar_nakshatra == "Dhanishta"
    assert state.lunar_nakshatra_index == VEDANGA_EPOCH_NAKSHATRA_INDEX
    assert state.vedanga_lunar_nakshatra_index == 0
    assert math.isclose(state.bhamsha, 0.0, abs_tol=1e-12)
    assert state.bhamsha_index == 0
    assert state.bhamsha_number == 1
    assert state.kshaya_tithis_elapsed == 0
    assert len(state.receipt_sha256) == 64


@pytest.mark.parametrize(
    ("year_idx", "expected_name"),
    [
        (0, "Samvatsara"),
        (1, "Parivatsara"),
        (2, "Idavatsara"),
        (3, "Anuvatsara"),
        (4, "Idvatsara"),
    ],
)
def test_vedanga_five_samvatsara_years_and_ayana_transitions(year_idx: int, expected_name: str):
    start_day = year_idx * 366.0
    # Start of solar year -> Uttarayana
    s_uttara = compute_vedanga_yuga_state(start_day + 10.0)
    assert s_uttara.year_index == year_idx
    assert s_uttara.year == year_idx + 1
    assert s_uttara.samvatsara_name == expected_name
    assert s_uttara.ayana == "Uttarayana"
    assert s_uttara.ayana_number_in_yuga == year_idx * 2 + 1

    # Second half of solar year (day 183..365) -> Dakshinayana
    s_dakshina = compute_vedanga_yuga_state(start_day + 183.0)
    assert s_dakshina.year == year_idx + 1
    assert s_dakshina.samvatsara_name == expected_name
    assert s_dakshina.ayana == "Dakshinayana"
    assert s_dakshina.ayana_number_in_yuga == year_idx * 2 + 2
    # At summer solstice (183 Savana days = 13.5 solar Nakshatras from Dhanishta),
    # the Sun is at the midpoint of Ashlesha (Dhanishta + 13 = index 8 = Ashlesha)!
    assert s_dakshina.solar_nakshatra == "Ashlesha"
    assert math.isclose(s_dakshina.solar_bhamsha, 62.0, abs_tol=1e-9)


def test_vedanga_two_intercalary_adhika_masas():
    # Synodic month 31 ends at 915 Savana days (mid-Yuga); synodic month 62 ends at 1830 Savana days
    s_mid = compute_vedanga_yuga_state(910.0)
    assert s_mid.synodic_month_number == 31
    assert s_mid.is_adhika_masa is True
    assert s_mid.adhika_masas_elapsed == 1

    s_end = compute_vedanga_yuga_state(1825.0)
    assert s_end.synodic_month_number == 62
    assert s_end.is_adhika_masa is True
    assert s_end.adhika_masas_elapsed == 2


def test_vedanga_parvan_bhamsha_progression_and_kshaya_tithis():
    # One Parvan (15 Tithis = 1/124 of a Yuga) is 1830 / 124 = 915 / 62 Savana days.
    # In exactly 1 Parvan:
    # - Sun moves 135 / 124 = 1 + 11/124 Nakshatras -> solar_bhamsha == 11.0
    # - Moon moves 1809 / 124 = 14 + 73/124 Nakshatras -> lunar bhamsha == 73.0
    one_parvan_days = 1830.0 / 124.0
    s_parvan = compute_vedanga_yuga_state(one_parvan_days)
    assert s_parvan.parvan_index == 1
    assert s_parvan.tithi == 16
    assert s_parvan.paksha == "Krishna"
    assert s_parvan.vedanga_solar_nakshatra_index == 1
    assert math.isclose(s_parvan.solar_bhamsha, 11.0, abs_tol=1e-9)
    assert s_parvan.vedanga_lunar_nakshatra_index == 14
    assert math.isclose(s_parvan.bhamsha, 73.0, abs_tol=1e-9)
    assert s_parvan.bhamsha_index == 73

    # Every 61 Savana days corresponds to 62 Tithis (1 Kshaya Tithi per 61 Savana days)
    s_61 = compute_vedanga_yuga_state(61.0)
    assert s_61.kshaya_tithis_elapsed == 1
    assert math.isclose(s_61.tithi_in_yuga, 62.0, abs_tol=1e-9)


def test_vedanga_yuga_wraparound_and_validation():
    s0 = compute_vedanga_yuga_state(250.0)
    s1 = compute_vedanga_yuga_state(250.0 + 1830.0)
    assert s0.days_into_yuga == s1.days_into_yuga
    assert s0.yuga_cycle == 0
    assert s1.yuga_cycle == 1
    assert s0.samvatsara_name == s1.samvatsara_name
    assert s0.solar_nakshatra == s1.solar_nakshatra
    assert s0.lunar_nakshatra == s1.lunar_nakshatra
    assert s0.tithi == s1.tithi
    assert math.isclose(s0.bhamsha, s1.bhamsha, abs_tol=1e-12)

    with pytest.raises(ValueError, match="finite"):
        compute_vedanga_yuga_state(float("nan"))


@pytest.mark.parametrize(
    ("body", "expected_bhagana"),
    [
        ("sun", 4_320_000),
        ("moon", 57_753_336),
        ("moon_apogee", 488_203),
        ("moon_node", -232_238),
        ("mars", 2_296_832),
        ("mercury_sighrocca", 17_937_060),
        ("jupiter", 364_220),
        ("venus_sighrocca", 7_022_376),
        ("saturn", 146_568),
    ],
)
def test_mahayuga_bhagana_full_cycle_returns_to_zero(body: str, expected_bhagana: int):
    assert MAHAYUGA_BHAGANA[body] == expected_bhagana
    # At exactly 1 Mahayuga (1,577,917,828 Savana days), every body completes an integer number of revolutions
    mean = surya_siddhanta_mean_longitudes(KALI_YUGA_EPOCH_JD + float(MAHAYUGA_SAVANA_DAYS))
    assert math.isclose(mean[body] % 360.0, 0.0, abs_tol=1e-9) or math.isclose(mean[body], 360.0, abs_tol=1e-9)


@pytest.mark.parametrize(
    ("ritu_idx", "expected_ritu"),
    [
        (0, "Shishira"),
        (1, "Vasanta"),
        (2, "Grishma"),
        (3, "Varsha"),
        (4, "Sharad"),
        (5, "Hemanta"),
    ],
)
def test_vedanga_six_ritus_across_solar_year(ritu_idx: int, expected_ritu: str):
    day = ritu_idx * 61.0 + 15.0
    state = compute_vedanga_yuga_state(day)
    assert state.ritu_index_in_year == ritu_idx
    assert state.ritu_name == expected_ritu


def test_vedanga_receipt_determinism_and_negative_days():
    s_neg = compute_vedanga_yuga_state(-366.0)
    s_pos = compute_vedanga_yuga_state(1830.0 - 366.0)
    assert s_neg.yuga_cycle == -1
    assert s_neg.year == 5
    assert s_neg.samvatsara_name == "Idvatsara"
    assert math.isclose(s_neg.days_into_yuga, s_pos.days_into_yuga, abs_tol=1e-12)
    assert s_neg.receipt_sha256 != s_pos.receipt_sha256  # yuga_cycle differs (-1 vs 0)
    assert compute_vedanga_yuga_state(42.5).receipt_sha256 == compute_vedanga_yuga_state(42.5).receipt_sha256
