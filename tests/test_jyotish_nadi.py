"""Comprehensive unit and mathematical invariant tests for jyotish_nadi."""

from __future__ import annotations

import math
import pytest

from ephemeris_oss.jyotish_nadi import (
    CHAKRAPATA_MALEFIC_FRACTIONS,
    DREKKANA_SWARUPA_CATALOG,
    DREKKANA_SWARUPA_CATEGORIES,
    MRITYU_BHAGA_DEGREE_TABLE,
    NADI_DIRECTIONS_ORDER,
    NADI_DIRECTION_SIGNS,
    NISARGAYU_MAX_YEARS,
    PINDAYU_MAX_YEARS,
    amsayu_bharana_multiplier,
    astangata_reduction_fraction,
    chakrapata_reduction_fraction,
    compute_amsayu,
    compute_ayurdaya,
    compute_bhrigu_bindu,
    compute_bhrigu_progression,
    compute_khara_points,
    compute_nadi_directional_links,
    compute_nisargayu,
    compute_pindayu,
    evaluate_ayurdaya,
    evaluate_mrityu_bhaga,
    shatru_kshetra_reduction_fraction,
)


# ---------------------------------------------------------------------------
# 1. Bhrigu Bindu & Transit Aspect Tests
# ---------------------------------------------------------------------------


def test_bhrigu_bindu_forward_arc_and_midpoint_standard():
    # Rahu at 30 deg (0 deg Taurus), Moon at 150 deg (0 deg Virgo)
    # Forward arc = 120 deg -> Bindu = 30 + 60 = 90 deg (0 deg Cancer, Punarvasu Pada 4)
    report = compute_bhrigu_bindu(moon_lon_deg=150.0, rahu_lon_deg=30.0)
    assert math.isclose(report.arc_deg, 120.0, abs_tol=1e-12)
    assert math.isclose(report.bindu_lon_deg, 90.0, abs_tol=1e-12)
    assert report.sign_index == 3
    assert report.sign_name == "Karka"
    assert report.sign_lord == "moon"
    assert math.isclose(report.degree_in_sign, 0.0, abs_tol=1e-12)
    assert report.nakshatra_index == 6
    assert report.nakshatra_name == "Punarvasu"
    assert report.pada == 4
    assert report.navamsa_sign_index == 3
    assert report.navamsa_sign_name == "Karka"
    assert len(report.receipt_sha256) == 64


def test_bhrigu_bindu_wraparound_across_zero_aries():
    # Rahu at 300 deg (0 deg Aquarius), Moon at 60 deg (0 deg Gemini)
    # Forward zodiacal arc from Rahu to Moon = (60 - 300) % 360 = 120 deg
    # Bindu = (300 + 60) % 360 = 0 deg (0 deg Mesha, Ashwini Pada 1)
    report = compute_bhrigu_bindu(moon_lon_deg=60.0, rahu_lon_deg=300.0)
    assert math.isclose(report.rahu_to_moon_arc_deg, 120.0, abs_tol=1e-12)
    assert math.isclose(report.longitude_deg, 0.0, abs_tol=1e-12)
    assert report.sign_index == 0
    assert report.sign == "Mesha"
    assert report.nakshatra == "Ashwini"
    assert report.pada == 1
    assert report.navamsa_sign == "Mesha"


def test_bhrigu_bindu_active_transit_aspects_and_exact_orbs():
    # Bindu at 90.0 deg (0 deg Karka):
    # Conjunction = 90.0, 5th trine = 210.0, 7th opposition = 270.0, 9th trine = 330.0
    transits = {
        "jupiter": 91.25,     # conjunction with orb 1.25 deg
        "saturn": 268.5,      # 7th opposition with orb 1.50 deg
        "rahu": 212.0,        # 5th/9th trines (5th house) with orb 2.00 deg
        "venus": 329.2,       # 5th/9th trines (9th house) with orb 0.80 deg
        "mars": 140.0,        # 50 deg away -> outside orb
    }
    report = compute_bhrigu_bindu(
        moon_lon_deg=150.0,
        rahu_lon_deg=30.0,
        transit_longitudes=transits,
        orb_deg=5.0,
    )
    assert len(report.active_transit_aspects) == 4
    by_planet = {item.planet: item for item in report.active_transit_aspects}
    assert by_planet["jupiter"].aspect_type == "conjunction"
    assert math.isclose(by_planet["jupiter"].orb_deg, 1.25, abs_tol=1e-9)
    assert by_planet["jupiter"].house_from_bindu == 1

    assert by_planet["saturn"].aspect_type == "7th opposition"
    assert math.isclose(by_planet["saturn"].orb_deg, 1.5, abs_tol=1e-9)
    assert by_planet["saturn"].house_from_bindu == 7

    assert by_planet["rahu"].aspect_type == "5th/9th trines"
    assert math.isclose(by_planet["rahu"].orb_deg, 2.0, abs_tol=1e-9)
    assert by_planet["rahu"].house_from_bindu == 5

    assert by_planet["venus"].aspect_type == "5th/9th trines"
    assert math.isclose(by_planet["venus"].orb_deg, 0.8, abs_tol=1e-9)
    assert by_planet["venus"].house_from_bindu == 9


def test_bhrigu_bindu_validation_errors():
    with pytest.raises(ValueError, match="longitude"):
        compute_bhrigu_bindu(float("nan"), 10.0)
    with pytest.raises(ValueError, match="orb_deg"):
        compute_bhrigu_bindu(10.0, 20.0, orb_deg=-1.0)


# ---------------------------------------------------------------------------
# 2. Bhrigu Nandi Nadi Directional Trines & Connection Vector Tests
# ---------------------------------------------------------------------------


def test_nadi_directional_trines_partition_and_degree_sorting():
    planets = {
        "sun": 14.0,       # Aries (0, East) at 14 deg
        "jupiter": 125.0,  # Leo (4, East) at 5 deg
        "mars": 262.0,     # Sagittarius (8, East) at 22 deg
        "venus": 42.0,     # Taurus (1, South) at 12 deg
        "mercury": 153.0,  # Virgo (5, South) at 3 deg
        "saturn": 310.0,   # Aquarius (10, West) at 10 deg
        "moon": 108.0,     # Cancer (3, North) at 18 deg
        "rahu": 217.0,     # Scorpio (7, North) at 7 deg
        "ketu": 37.0,      # Taurus (1, South) at 7 deg
    }
    report = compute_nadi_directional_links(planets)

    assert set(report.directional_trines.keys()) == set(NADI_DIRECTIONS_ORDER)
    # East (0, 4, 8): jupiter (5 deg), sun (14 deg), mars (22 deg)
    assert report.directional_trines["East"] == ("jupiter", "sun", "mars")
    # South (1, 5, 9): mercury (3 deg), ketu (7 deg), venus (12 deg)
    assert report.directional_trines["South"] == ("mercury", "ketu", "venus")
    # West (2, 6, 10): saturn (10 deg)
    assert report.directional_trines["West"] == ("saturn",)
    # North (3, 7, 11): rahu (7 deg), moon (18 deg)
    assert report.directional_trines["North"] == ("rahu", "moon")

    sun_link = report.planet_links["sun"]
    assert sun_link.direction == "East"
    assert sun_link.element == "Fire"
    assert sun_link.purushartha == "Dharma"
    assert sun_link["trinal_1_5_9"] == ("jupiter", "mars")
    assert sun_link.preceding_in_trine == ("jupiter",)
    assert sun_link.succeeding_in_trine == ("mars",)
    # 2nd from Aries (0) is Taurus (1): ketu (7 deg), venus (12 deg)
    assert sun_link["2nd_front"] == ("ketu", "venus")


def test_nadi_planet_kartari_shubha_papa_and_mixed():
    # Case 1: Sun in Taurus (1) hemmed between Jupiter in Aries (0) and Venus in Gemini (2) -> Shubha Kartari
    # Also Mars in Leo (4) hemmed between Saturn in Cancer (3) and Rahu in Virgo (5) -> Papa Kartari
    # And Moon in Scorpio (7) with Mercury in Libra (6) and Ketu in Sagittarius (8) -> Mixed Kartari
    planets = {
        "jupiter": 10.0,   # Aries (0) - benefic
        "sun": 45.0,       # Taurus (1)
        "venus": 70.0,     # Gemini (2) - benefic
        "saturn": 100.0,   # Cancer (3) - malefic
        "mars": 135.0,     # Leo (4)
        "rahu": 160.0,     # Virgo (5) - malefic
        "mercury": 190.0,  # Libra (6) - benefic
        "moon": 225.0,     # Scorpio (7)
        "ketu": 250.0,     # Sagittarius (8) - malefic
    }
    report = compute_nadi_directional_links(planets)
    assert report.planet_links["sun"].planet_kartari == "Shubha Kartari"
    assert report.planet_links["mars"].planet_kartari == "Papa Kartari"
    assert report.planet_links["moon"].planet_kartari == "Mixed Kartari"
    assert report.planet_links["jupiter"].planet_kartari == "None"

    # Verify 12th_behind and 7th_opposite for Sun in Taurus (1):
    # 12th behind Taurus is Aries (0) -> jupiter
    # 7th opposite Taurus is Scorpio (7) -> moon
    assert report.planet_links["sun"]["12th_behind"] == ("jupiter",)
    assert report.planet_links["sun"]["7th_opposite"] == ("moon",)


def test_nadi_directional_links_empty_raises():
    with pytest.raises(ValueError, match="must not be empty"):
        compute_nadi_directional_links({})


# ---------------------------------------------------------------------------
# 3. Bhrigu Chakra Planetary Age Progression Tests
# ---------------------------------------------------------------------------


def test_bhrigu_progression_cycles_at_key_ages():
    # Lagna in Aries (10 deg), Jupiter in Cancer (95 deg, sign 3), Saturn in Libra (200 deg, sign 6)
    r0 = compute_bhrigu_progression(10.0, 95.0, 200.0, age_years=0)
    assert r0.progressed_lagna_sign == 0
    assert r0.progressed_jupiter_sign == 3
    assert r0.progressed_saturn_sign == 6
    assert r0.jupiter_cycle_number == 1
    assert r0.saturn_cycle_number == 1

    # At age 12: Jupiter and Lagna return to natal signs (2nd cycle start)
    r12 = compute_bhrigu_progression(10.0, 95.0, 200.0, age_years=12)
    assert r12.progressed_lagna_sign == 0
    assert r12.progressed_jupiter_sign == 3
    assert r12.jupiter_cycle_number == 2
    # int(12 / 2.5) = 4 signs advanced from Libra (6) -> (6 + 4) % 12 = 10 (Aquarius)
    assert r12.progressed_saturn_sign == 10

    # At age 30: Saturn completes its 30-year cycle (int(30 / 2.5) = 12 -> back to Libra 6)
    r30 = compute_bhrigu_progression(10.0, 95.0, 200.0, age_years=30)
    assert r30.progressed_saturn_sign == 6
    assert r30.saturn_cycle_number == 2
    assert r30.progressed_lagna_sign == (0 + 30) % 12  # 6 (Libra, 7th house)
    assert r30.progressed_lagna_house == 7


def test_bhrigu_progression_triggers_and_bounds():
    natal = {"sun": 15.0, "venus": 135.0, "mars": 255.0}
    rep = compute_bhrigu_progression(15.0, 15.0, 15.0, age_years=4, natal_planet_longitudes=natal)
    # At age 4, progressed Jupiter is in sign (0 + 4) = 4 (Leo), which trines Aries (0) and Sagittarius (8)
    assert rep.progressed_jupiter_sign == 4
    assert "sun" in rep.jupiter_triggered_planets
    assert "venus" in rep.jupiter_triggered_planets
    assert "mars" in rep.jupiter_triggered_planets
    assert len(rep.receipt_sha256) == 64

    with pytest.raises(ValueError, match="age_years"):
        compute_bhrigu_progression(10.0, 20.0, 30.0, age_years=-1.0)
    with pytest.raises(ValueError, match="age_years"):
        compute_bhrigu_progression(10.0, 20.0, 30.0, age_years=121.0)


# ---------------------------------------------------------------------------
# 4. 22nd Drekkana, 64th Navamsa, 85th Dwadashamsa (Khara) Tests
# ---------------------------------------------------------------------------


def test_drekkana_swarupa_catalog_completeness_and_categories():
    assert len(DREKKANA_SWARUPA_CATALOG) == 36
    observed_categories = {entry.swarupa for entry in DREKKANA_SWARUPA_CATALOG}
    assert observed_categories == DREKKANA_SWARUPA_CATEGORIES
    for idx, entry in enumerate(DREKKANA_SWARUPA_CATALOG):
        assert entry.drekkana_index == idx
        assert entry.sign_index == idx // 3
        assert entry.decanate_number == (idx % 3) + 1
        assert entry.swarupa in DREKKANA_SWARUPA_CATEGORIES


@pytest.mark.parametrize("deg", [float(i * 3.3333333 + 0.5) for i in range(36)])
def test_khara_invariants_across_entire_zodiac(deg: float):
    rep = compute_khara_points(deg, label="lagna")
    ref_sign = int((deg % 360.0) // 30.0) % 12

    # Invariant 1: 22nd Drekkana index is (ref_drekkana + 21) % 36 and always in the 8th sign from reference
    assert rep.drekkana_22nd.khara_drekkana_index == (rep.drekkana_22nd.reference_drekkana_index + 21) % 36
    assert rep.drekkana_22nd.sign_index == (ref_sign + 7) % 12
    assert rep.drekkana_22nd.swarupa in DREKKANA_SWARUPA_CATEGORIES

    # Invariant 2: 64th Navamsa index is (ref_navamsa + 63) % 108 and always in the 4th sign from reference D9 sign
    assert rep.navamsa_64th.khara_navamsa_index == (rep.navamsa_64th.reference_navamsa_index + 63) % 108
    assert rep.navamsa_64th.d9_sign_index == (rep.navamsa_64th.reference_d9_sign_index + 3) % 12
    assert rep.navamsa_64th.d1_sign_index == (ref_sign + 7) % 12

    # Invariant 3: 85th Dwadashamsa index is (ref_d12 + 84) % 144 and always in the 8th D1 sign
    assert rep.dwadashamsa_85th.khara_d12_index == (rep.dwadashamsa_85th.reference_d12_index + 84) % 144
    assert rep.dwadashamsa_85th.d1_sign_index == (ref_sign + 7) % 12


def test_khara_points_specific_calculation():
    # Reference at 5.0 deg Aries (1st Drekkana = 0, 2nd Navamsa = 1 -> Taurus D9)
    rep = compute_khara_points(5.0, label="moon")
    assert rep.label == "moon"
    # 22nd Drekkana = index 21 -> 1st Drekkana of Scorpio (sign 7, 0..10 deg), ruled by Mars, Swarupa = Sarpa
    assert rep.drekkana_22nd.khara_drekkana_index == 21
    assert rep.drekkana_22nd.sign_index == 7
    assert rep.drekkana_22nd.degree_span == (0.0, 10.0)
    assert rep.drekkana_22nd.ruling_planet == "mars"
    assert rep.drekkana_22nd.swarupa == "Sarpa"

    # 64th Navamsa = (1 + 63) = 64 -> 64 % 12 = 4 (Leo, 4th from Taurus D9), ruled by Sun
    assert rep.navamsa_64th.reference_navamsa_index == 1
    assert rep.navamsa_64th.khara_navamsa_index == 64
    assert rep.navamsa_64th.d9_sign_index == 4
    assert rep.navamsa_64th.khara_lord == "sun"
    assert math.isclose(rep.navamsa_64th.degree_span[0], 10.0 / 3.0, abs_tol=1e-9)
    assert math.isclose(rep.navamsa_64th.degree_span[1], 20.0 / 3.0, abs_tol=1e-9)


# ---------------------------------------------------------------------------
# 5. Mrityu Bhaga Vulnerability Detector Tests
# ---------------------------------------------------------------------------


def test_mrityu_bhaga_table_structure_and_exact_degrees():
    expected_keys = {"sun", "moon", "mars", "mercury", "jupiter", "venus", "saturn", "rahu", "ketu", "lagna"}
    assert set(MRITYU_BHAGA_DEGREE_TABLE.keys()) == expected_keys
    assert MRITYU_BHAGA_DEGREE_TABLE["sun"] == (20.0, 9.0, 12.0, 6.0, 8.0, 24.0, 16.0, 17.0, 22.0, 2.0, 3.0, 23.0)
    assert MRITYU_BHAGA_DEGREE_TABLE["moon"] == (26.0, 12.0, 13.0, 25.0, 24.0, 11.0, 26.0, 14.0, 13.0, 25.0, 5.0, 12.0)
    for point, degs in MRITYU_BHAGA_DEGREE_TABLE.items():
        assert len(degs) == 12, f"{point} must have 12 sign degrees"
        assert all(0.0 < d < 30.0 for d in degs)


def test_evaluate_mrityu_bhaga_detection_within_and_outside_orb():
    # Sun in Aries at 20.4 deg (Mrityu Bhaga = 20.0, dist = 0.4 <= 1.0 -> True)
    # Moon in Taurus at 42.95 deg = 12.95 deg Taurus (Mrityu Bhaga = 12.0, dist = 0.95 <= 1.0 -> True)
    # Mars in Gemini at 70.0 deg = 10.0 deg Gemini (Mrityu Bhaga = 25.0, dist = 15.0 -> False)
    # Lagna in Leo at 144.2 deg = 24.2 deg Leo (Mrityu Bhaga = 25.0, dist = 0.8 <= 1.0 -> True)
    planets = {
        "sun": 20.4,
        "moon": 42.95,
        "mars": 70.0,
        "mercury": 100.0,
        "jupiter": 130.0,
        "venus": 160.0,
        "saturn": 190.0,
        "rahu": 220.0,
        "ketu": 40.0,
    }
    report = evaluate_mrityu_bhaga(planets, lagna_lon_deg=144.2, orb_deg=1.0)
    assert report["sun"].is_in_mrityu_bhaga is True
    assert math.isclose(report["sun"].distance_deg, 0.4, abs_tol=1e-9)
    assert report["moon"].is_in_mrityu_bhaga is True
    assert math.isclose(report["moon"].distance_deg, 0.95, abs_tol=1e-9)
    assert report["mars"].is_in_mrityu_bhaga is False
    assert report["lagna"].is_in_mrityu_bhaga is True
    assert set(report.afflicted_points) == {"sun", "moon", "lagna"}


def test_evaluate_mrityu_bhaga_validation():
    with pytest.raises(ValueError, match="unsupported"):
        evaluate_mrityu_bhaga({"pluto": 10.0})
    with pytest.raises(ValueError, match="at least one"):
        evaluate_mrityu_bhaga({})


# ---------------------------------------------------------------------------
# 6. Classical Mathematical Ayurdaya (Pindayu, Nisargayu, Amsayu) Tests
# ---------------------------------------------------------------------------


def test_pindayu_deep_exaltation_and_deep_debilitation_raw_years():
    # Deep exaltation longitudes:
    exalt_lons = {
        "sun": 10.0,
        "moon": 33.0,
        "mars": 298.0,
        "mercury": 165.0,
        "jupiter": 95.0,
        "venus": 357.0,
        "saturn": 200.0,
    }
    res_exalt = compute_pindayu(exalt_lons, lagna_lon_deg=0.0)
    for p, max_y in PINDAYU_MAX_YEARS.items():
        assert math.isclose(res_exalt.planet_breakdowns[p].raw_years, max_y, abs_tol=1e-9)
    assert math.isclose(
        sum(b.raw_years for b in res_exalt.planet_breakdowns.values()),
        127.0,
        abs_tol=1e-9,
    )

    # Deep debilitation longitudes (exalt + 180 deg) must give exact half of maximum years!
    deb_lons = {p: (lon + 180.0) % 360.0 for p, lon in exalt_lons.items()}
    res_deb = compute_pindayu(deb_lons, lagna_lon_deg=0.0)
    for p, max_y in PINDAYU_MAX_YEARS.items():
        assert math.isclose(res_deb.planet_breakdowns[p].raw_years, 0.5 * max_y, abs_tol=1e-9)
    assert math.isclose(
        sum(b.raw_years for b in res_deb.planet_breakdowns.values()),
        63.5,
        abs_tol=1e-9,
    )


def test_nisargayu_deep_exaltation_and_debilitation_raw_years():
    exalt_lons = {
        "sun": 10.0,
        "moon": 33.0,
        "mars": 298.0,
        "mercury": 165.0,
        "jupiter": 95.0,
        "venus": 357.0,
        "saturn": 200.0,
    }
    res_exalt = compute_nisargayu(exalt_lons, lagna_lon_deg=0.0)
    for p, max_y in NISARGAYU_MAX_YEARS.items():
        assert math.isclose(res_exalt.planet_breakdowns[p].raw_years, max_y, abs_tol=1e-9)
    assert math.isclose(
        sum(b.raw_years for b in res_exalt.planet_breakdowns.values()),
        120.0,
        abs_tol=1e-9,
    )

    deb_lons = {p: (lon + 180.0) % 360.0 for p, lon in exalt_lons.items()}
    res_deb = compute_nisargayu(deb_lons, lagna_lon_deg=0.0)
    assert math.isclose(
        sum(b.raw_years for b in res_deb.planet_breakdowns.values()),
        60.0,
        abs_tol=1e-9,
    )


@pytest.mark.parametrize(
    ("house", "malefic_expected", "benefic_expected"),
    [
        (1, 0.0, 0.0),
        (6, 0.0, 0.0),
        (7, 1.0 / 6.0, 1.0 / 12.0),
        (8, 1.0 / 5.0, 1.0 / 10.0),
        (9, 1.0 / 4.0, 1.0 / 8.0),
        (10, 1.0 / 3.0, 1.0 / 6.0),
        (11, 1.0 / 2.0, 1.0 / 4.0),
        (12, 1.0, 0.5),
    ],
)
def test_chakrapata_reduction_fractions(house: int, malefic_expected: float, benefic_expected: float):
    assert math.isclose(chakrapata_reduction_fraction(house, is_malefic=True), malefic_expected, abs_tol=1e-12)
    assert math.isclose(chakrapata_reduction_fraction(house, is_malefic=False), benefic_expected, abs_tol=1e-12)


def test_astangata_combustion_halving_and_venus_saturn_exemption():
    # Sun at 100.0 deg
    # Mars at 110.0 deg (10 deg from Sun <= 17 deg orb) -> combust and halved (0.5)
    assert astangata_reduction_fraction("mars", 110.0, 100.0) == (True, 0.5)
    # Jupiter at 105.0 deg (5 deg from Sun <= 11 deg orb) -> combust and halved (0.5)
    assert astangata_reduction_fraction("jupiter", 105.0, 100.0) == (True, 0.5)
    # Venus at 104.0 deg (4 deg from Sun <= 10 deg orb) -> combust but EXEMPT (0.0 reduction)
    assert astangata_reduction_fraction("venus", 104.0, 100.0) == (True, 0.0)
    # Saturn at 108.0 deg (8 deg from Sun <= 15 deg orb) -> combust but EXEMPT (0.0 reduction)
    assert astangata_reduction_fraction("saturn", 108.0, 100.0) == (True, 0.0)
    # Mercury at 125.0 deg (25 deg from Sun > 14 deg orb) -> not combust
    assert astangata_reduction_fraction("mercury", 125.0, 100.0) == (False, 0.0)


def test_amsayu_bharana_multipliers_and_bahugunane_pradhanyam():
    # Sun in Aries (exalted, 5 deg) -> x3
    mult_exalt, reasons_exalt = amsayu_bharana_multiplier("sun", 5.0, is_retrograde=False)
    assert mult_exalt == 3.0
    assert "exalted_rasi_x3" in reasons_exalt

    # Mars in Aries at 1.0 deg (Own Rasi, Own Navamsa, Own Drekkana, Vargottama) -> x2 (not 2^4)
    mult_own, reasons_own = amsayu_bharana_multiplier("mars", 1.0, is_retrograde=False)
    assert mult_own == 2.0
    assert "own_rasi_x2" in reasons_own
    assert "vargottama_x2" in reasons_own

    # Retrograde Mars in Aries at 1.0 deg -> highest single multiplier is x3
    mult_retro, reasons_retro = amsayu_bharana_multiplier("mars", 1.0, is_retrograde=True)
    assert mult_retro == 3.0
    assert "retrograde_x3" in reasons_retro


def test_krurodaya_malefic_in_lagna_and_benefic_mitigation():
    base_planets = {
        "sun": 15.0,       # In Aries (same sign as Lagna at 15 deg Aries) -> malefic in Lagna
        "moon": 75.0,
        "mars": 105.0,
        "mercury": 135.0,
        "jupiter": 165.0,
        "venus": 75.0,
        "saturn": 105.0,
    }
    res_unmitigated = compute_pindayu(base_planets, lagna_lon_deg=15.0)
    assert res_unmitigated.krurodaya.krurodaya_active is True
    # At 15 deg in sign, fraction = 15/30 = 0.5
    assert math.isclose(res_unmitigated.krurodaya.krurodaya_reduction_fraction, 0.5, abs_tol=1e-9)

    # Now place Jupiter in Aries (10.0 deg) to protect Lagna -> Krurodaya reduction is halved to 0.25!
    mitigated_planets = dict(base_planets, jupiter=10.0)
    res_mitigated = compute_pindayu(mitigated_planets, lagna_lon_deg=15.0)
    assert res_mitigated.krurodaya.krurodaya_active is True
    assert math.isclose(res_mitigated.krurodaya.krurodaya_reduction_fraction, 0.25, abs_tol=1e-9)
    assert res_mitigated.lagna_net_years > res_unmitigated.lagna_net_years


def test_unified_compute_ayurdaya_system_selection_and_receipt():
    planets = {
        "sun": 10.0,       # Deep exaltation in Aries
        "moon": 65.0,      # Gemini
        "mars": 125.0,     # Leo
        "mercury": 45.0,   # Taurus
        "jupiter": 100.0,  # Cancer
        "venus": 350.0,    # Pisces
        "saturn": 295.0,   # Capricorn
    }
    # Override strengths to test all 3 primary system selections deterministically
    rep_sun = compute_ayurdaya(
        planets,
        lagna_lon_deg=10.0,
        anchor_strength_overrides={"sun": 95.0, "moon": 70.0, "lagna": 60.0},
    )
    assert rep_sun.strongest_anchor == "sun"
    assert rep_sun.recommended_system == "Pindayu"
    assert math.isclose(rep_sun.recommended_years, rep_sun.pindayu_years, abs_tol=1e-12)

    rep_moon = compute_ayurdaya(
        planets,
        lagna_lon_deg=10.0,
        anchor_strength_overrides={"sun": 60.0, "moon": 98.0, "lagna": 70.0},
    )
    assert rep_moon.strongest_anchor == "moon"
    assert rep_moon.recommended_system == "Nisargayu"
    assert math.isclose(rep_moon.recommended_years, rep_moon.nisargayu_years, abs_tol=1e-12)

    rep_lagna = compute_ayurdaya(
        planets,
        lagna_lon_deg=10.0,
        anchor_strength_overrides={"sun": 60.0, "moon": 70.0, "lagna": 99.0},
    )
    assert rep_lagna.strongest_anchor == "lagna"
    assert rep_lagna.recommended_system == "Amsayu"
    assert math.isclose(rep_lagna.recommended_years, rep_lagna.amsayu_years, abs_tol=1e-12)

    # Also test automatic anchor strength calculation and receipt determinism
    rep_auto_1 = evaluate_ayurdaya(planets, lagna_lon_deg=10.0, retrograde_planets=("saturn",))
    rep_auto_2 = compute_ayurdaya(planets, lagna_lon_deg=10.0, retrograde_planets=["saturn"])
    assert rep_auto_1.receipt_sha256 == rep_auto_2.receipt_sha256
    assert rep_auto_1.pindayu_years > 0.0
    assert rep_auto_1.nisargayu_years > 0.0
    assert rep_auto_1.amsayu_years > 0.0
    assert rep_auto_1.longevity_tier in {"Alpayu", "Madhyayu", "Purnayu", "Dirghayu"}
