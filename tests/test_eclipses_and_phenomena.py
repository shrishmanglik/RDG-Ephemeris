"""Tests for clean-room Solar & Lunar Eclipse solver and Planetary Phenomena engine."""

from __future__ import annotations

import math
import erfa
import pytest

from ephemeris_oss import Engine
from ephemeris_oss.engine.eclipses import (
    CENTRAL_ECLIPSE_GAMMA_LIMIT,
    DANJON_ATMOSPHERIC_ENLARGEMENT,
    besselian_elements_at,
    find_lunar_eclipses,
    find_solar_eclipses,
    lunar_eclipse_at,
    lunar_eclipse_local_visibility,
    solar_eclipse_at,
    solar_eclipse_local_circumstances,
)
from ephemeris_oss.engine.phenomena import (
    CAZIMI_ORB_DEG,
    SURYA_SIDDHANTA_COMBUSTION_ORBS_DEG,
    check_combustion,
    combustion_orb_degrees,
    evaluate_graha_yuddha,
    find_combustion_windows,
    find_retrograde_stations,
    find_sign_ingresses,
)
from ephemeris_oss.engine.receipt import canonical_hash


def _tt_jd(year: int, month: int, day: int, hour: int = 0, minute: int = 0, second: float = 0.0) -> float:
    jd1, jd2 = erfa.dtf2d("TT", year, month, day, hour, minute, second)
    return float(jd1 + jd2)


@pytest.fixture(scope="module")
def de440_engine(kernel_path):
    with Engine.load(kernels={"DE440": kernel_path}, eop=None) as eng:
        yield eng


# ---------------------------------------------------------------------------
# 1. Solar Eclipse Tests (Besselian Elements, Global & Topocentric Local)
# ---------------------------------------------------------------------------

def test_2017_aug_21_total_solar_eclipse_global(de440_engine):
    approx_jd = _tt_jd(2017, 8, 21, 18, 26, 0)
    eclipse = solar_eclipse_at(approx_jd, de440_engine)
    assert eclipse is not None
    assert eclipse.classification == "total"
    assert eclipse.eclipse_type == "total"
    # Greatest eclipse 2017-08-21 ~18:26:40 TT (18:25:32 UT)
    assert abs(eclipse.greatest_jd_tt - _tt_jd(2017, 8, 21, 18, 26, 40)) * 1440.0 < 1.5
    assert eclipse.gamma == pytest.approx(0.4367, abs=0.002)
    assert eclipse.magnitude == pytest.approx(1.0306, abs=0.003)
    assert abs(eclipse.gamma) < CENTRAL_ECLIPSE_GAMMA_LIMIT
    assert eclipse.central_latitude_deg == pytest.approx(36.97, abs=0.15)
    assert eclipse.central_longitude_deg == pytest.approx(-87.67, abs=0.15)
    assert eclipse.receipt_sha256 == canonical_hash(eclipse.receipt)


def test_2017_aug_21_besselian_elements_properties(de440_engine):
    approx_jd = _tt_jd(2017, 8, 21, 18, 26, 40)
    el = besselian_elements_at(approx_jd, de440_engine)
    assert math.hypot(el.x, el.y) == pytest.approx(0.4367, abs=0.003)
    assert el.sin_d * el.sin_d + el.cos_d * el.cos_d == pytest.approx(1.0, abs=1e-12)
    assert 0.0 <= el.mu_deg < 360.0
    assert el.l1 > 0.50
    # Total solar eclipse has negative l2 on or near fundamental plane
    assert el.l2 < 0.01
    assert el.tan_f1 > el.tan_f2 > 0.004


def test_2017_aug_21_local_totality_hopkinsville_ky(de440_engine):
    approx_jd = _tt_jd(2017, 8, 21, 18, 26, 0)
    eclipse = solar_eclipse_at(approx_jd, de440_engine)
    assert eclipse is not None
    # Hopkinsville, Kentucky (near point of greatest eclipse)
    local = solar_eclipse_local_circumstances(eclipse, 36.8664, -87.4886, 160.0, de440_engine)
    assert local.classification == "total"
    assert local.visible is True
    assert local.c1_jd_tt is not None
    assert local.c2_jd_tt is not None
    assert local.max_jd_tt is not None
    assert local.c3_jd_tt is not None
    assert local.c4_jd_tt is not None
    assert local.c1_jd_tt < local.c2_jd_tt < local.max_jd_tt < local.c3_jd_tt < local.c4_jd_tt
    assert local.magnitude > 1.0
    assert local.obscuration == pytest.approx(1.0, abs=1e-9)
    assert 150.0 <= local.duration_seconds <= 170.0
    assert local.solar_altitude_deg > 60.0
    assert local.receipt_sha256 == canonical_hash(local.receipt)


def test_2017_aug_21_local_partial_and_non_visible(de440_engine):
    approx_jd = _tt_jd(2017, 8, 21, 18, 26, 0)
    eclipse = solar_eclipse_at(approx_jd, de440_engine)
    assert eclipse is not None
    # New York City saw a partial solar eclipse (~0.71 magnitude)
    nyc = solar_eclipse_local_circumstances(eclipse, 40.7128, -74.0060, 10.0, de440_engine)
    assert nyc.classification == "partial"
    assert nyc.visible is True
    assert nyc.c1_jd_tt is not None and nyc.c4_jd_tt is not None
    assert nyc.c2_jd_tt is None and nyc.c3_jd_tt is None
    assert 0.65 <= nyc.magnitude <= 0.78
    assert 0.55 <= nyc.obscuration <= 0.75

    # Sydney, Australia was on the night side -> no local eclipse
    sydney = solar_eclipse_local_circumstances(eclipse, -33.8688, 151.2093, 20.0, de440_engine)
    assert sydney.classification == "none"
    assert sydney.visible is False
    assert sydney.magnitude == 0.0
    assert sydney.obscuration == 0.0


def test_2024_apr_08_total_solar_eclipse_and_local_dallas(de440_engine):
    approx_jd = _tt_jd(2024, 4, 8, 18, 18, 0)
    eclipse = solar_eclipse_at(approx_jd, de440_engine)
    assert eclipse is not None
    assert eclipse.classification == "total"
    assert eclipse.gamma == pytest.approx(0.3431, abs=0.003)
    assert eclipse.magnitude == pytest.approx(1.0566, abs=0.004)
    assert eclipse.central_latitude_deg == pytest.approx(25.29, abs=0.2)
    assert eclipse.central_longitude_deg == pytest.approx(-104.12, abs=0.2)

    # Dallas, Texas was inside the path of totality
    dallas = solar_eclipse_local_circumstances(eclipse, 32.7767, -96.7970, 130.0, de440_engine)
    assert dallas.classification == "total"
    assert dallas.visible is True
    assert dallas.obscuration == pytest.approx(1.0, abs=1e-9)
    assert dallas.c2_jd_tt is not None and dallas.c3_jd_tt is not None
    assert 200.0 <= dallas.duration_seconds <= 260.0


def test_2023_oct_14_annular_solar_eclipse_and_albuquerque(de440_engine):
    approx_jd = _tt_jd(2023, 10, 14, 18, 0, 0)
    eclipse = solar_eclipse_at(approx_jd, de440_engine)
    assert eclipse is not None
    assert eclipse.classification == "annular"
    assert eclipse.gamma == pytest.approx(0.3753, abs=0.003)
    assert eclipse.magnitude == pytest.approx(0.9520, abs=0.004)
    assert eclipse.besselian_elements.l2 > 0.0

    # Albuquerque, NM was on the annularity path
    abq = solar_eclipse_local_circumstances(eclipse, 35.0844, -106.6504, 1619.0, de440_engine)
    assert abq.classification == "annular"
    assert abq.visible is True
    assert abq.c1_jd_tt < abq.c2_jd_tt < abq.max_jd_tt < abq.c3_jd_tt < abq.c4_jd_tt
    assert 0.94 <= abq.magnitude <= 0.97
    assert 0.88 <= abq.obscuration <= 0.95
    assert abq.duration_seconds > 240.0


def test_2022_apr_30_partial_solar_eclipse_non_central(de440_engine):
    approx_jd = _tt_jd(2022, 4, 30, 20, 42, 0)
    eclipse = solar_eclipse_at(approx_jd, de440_engine)
    assert eclipse is not None
    assert eclipse.classification == "partial"
    assert eclipse.gamma == pytest.approx(-1.1901, abs=0.004)
    assert abs(eclipse.gamma) > CENTRAL_ECLIPSE_GAMMA_LIMIT
    assert eclipse.central_latitude_deg is None
    assert eclipse.central_longitude_deg is None
    assert 0.55 <= eclipse.magnitude <= 0.70


def test_find_solar_eclipses_in_2024_and_builtin_fallback(de440_engine):
    start_jd = _tt_jd(2024, 1, 1)
    end_jd = _tt_jd(2024, 12, 31)
    eclipses_de440 = find_solar_eclipses(start_jd, end_jd, de440_engine)
    # 2024 had two solar eclipses: 2024-04-08 (total) and 2024-10-02 (annular)
    assert len(eclipses_de440) == 2
    assert [e.classification for e in eclipses_de440] == ["total", "annular"]

    # Built-in Meeus/ELP/VSOP fallback without engine also finds the exact same eclipses
    eclipses_builtin = find_solar_eclipses(start_jd, end_jd, None)
    assert len(eclipses_builtin) == 2
    assert [e.classification for e in eclipses_builtin] == ["total", "annular"]
    for a, b in zip(eclipses_de440, eclipses_builtin):
        assert abs(a.greatest_jd_tt - b.greatest_jd_tt) * 1440.0 < 2.0


# ---------------------------------------------------------------------------
# 2. Lunar Eclipse Tests (Shadow Cone, Contacts P1..P4, Local Visibility)
# ---------------------------------------------------------------------------

def test_2022_nov_08_total_lunar_eclipse(de440_engine):
    approx_jd = _tt_jd(2022, 11, 8, 11, 0, 0)
    eclipse = lunar_eclipse_at(approx_jd, de440_engine)
    assert eclipse is not None
    assert eclipse.classification == "total"
    assert eclipse.danjon_enlargement_factor == DANJON_ATMOSPHERIC_ENLARGEMENT == 1.02
    assert eclipse.gamma == pytest.approx(0.2570, abs=0.003)
    assert eclipse.umbral_magnitude == pytest.approx(1.3589, abs=0.01)
    assert eclipse.penumbral_magnitude == pytest.approx(2.4406, abs=0.03)
    assert eclipse.p1_jd_tt < eclipse.u1_jd_tt < eclipse.u2_jd_tt < eclipse.greatest_jd_tt
    assert eclipse.greatest_jd_tt < eclipse.u3_jd_tt < eclipse.u4_jd_tt < eclipse.p4_jd_tt
    assert eclipse.total_semi_duration_min == pytest.approx(42.5, abs=1.5)
    assert eclipse.umbral_semi_duration_min == pytest.approx(109.9, abs=2.0)
    assert eclipse.penumbral_semi_duration_min == pytest.approx(176.9, abs=3.0)
    assert eclipse.parallax_moon_arcsec > 3300.0
    assert eclipse.semidiameter_moon_arcsec > 880.0
    assert eclipse.receipt_sha256 == canonical_hash(eclipse.receipt)


def test_2022_nov_08_lunar_eclipse_local_visibility(de440_engine):
    approx_jd = _tt_jd(2022, 11, 8, 11, 0, 0)
    eclipse = lunar_eclipse_at(approx_jd, de440_engine)
    assert eclipse is not None

    # Honolulu, Hawaii saw the entire lunar eclipse high in the sky
    honolulu = lunar_eclipse_local_visibility(eclipse, 21.3069, -157.8583, 10.0, de440_engine)
    assert honolulu.visible is True
    assert honolulu.visibility_summary == "entirely_visible"
    for stage in ("P1", "U1", "U2", "GREATEST", "U3", "U4", "P4"):
        assert honolulu.contacts[stage].visible is True
        assert honolulu.contacts[stage].moon_altitude_deg > 15.0

    # London, UK was in daytime at 11:00 UT -> not visible
    london = lunar_eclipse_local_visibility(eclipse, 51.5074, -0.1278, 25.0, de440_engine)
    assert london.contacts["GREATEST"].visible is False
    assert london.contacts["GREATEST"].moon_altitude_deg < 0.0
    assert london.receipt_sha256 == canonical_hash(london.receipt)


def test_2025_mar_14_total_lunar_eclipse(de440_engine):
    approx_jd = _tt_jd(2025, 3, 14, 7, 0, 0)
    eclipse = lunar_eclipse_at(approx_jd, de440_engine)
    assert eclipse is not None
    assert eclipse.classification == "total"
    assert eclipse.gamma == pytest.approx(0.3485, abs=0.003)
    assert eclipse.umbral_magnitude == pytest.approx(1.178, abs=0.015)
    assert eclipse.total_semi_duration_min == pytest.approx(32.7, abs=2.0)

    # Toronto, Canada (43.65 N, -79.38 E) saw totality in the night sky
    toronto = lunar_eclipse_local_visibility(eclipse, 43.6532, -79.3832, 76.0, de440_engine)
    assert toronto.visible is True
    assert toronto.u2.visible is True
    assert toronto.greatest.visible is True
    assert toronto.u3.visible is True


def test_2023_oct_28_partial_and_2024_mar_25_penumbral_lunar_eclipses(de440_engine):
    # 2023-10-28 Partial Lunar Eclipse
    partial = lunar_eclipse_at(_tt_jd(2023, 10, 28, 20, 15, 0), de440_engine)
    assert partial is not None
    assert partial.classification == "partial"
    assert 0.10 <= partial.umbral_magnitude <= 0.16
    assert partial.u1_jd_tt is not None and partial.u4_jd_tt is not None
    assert partial.u2_jd_tt is None and partial.u3_jd_tt is None

    # 2024-03-25 Penumbral Lunar Eclipse
    penumbral = lunar_eclipse_at(_tt_jd(2024, 3, 25, 7, 13, 0), de440_engine)
    assert penumbral is not None
    assert penumbral.classification == "penumbral"
    assert penumbral.penumbral_magnitude > 0.90
    assert penumbral.umbral_magnitude < 0.0
    assert penumbral.p1_jd_tt is not None and penumbral.p4_jd_tt is not None
    assert penumbral.u1_jd_tt is None and penumbral.u4_jd_tt is None


def test_non_eclipse_full_moon_returns_none_and_range_search(de440_engine):
    # Full Moon of 2024-01-25 had no lunar eclipse
    no_ec = lunar_eclipse_at(_tt_jd(2024, 1, 25, 17, 54, 0), de440_engine)
    assert no_ec is None

    # 2022 had two total lunar eclipses (May 16 and Nov 8)
    eclipses_2022 = find_lunar_eclipses(_tt_jd(2022, 1, 1), _tt_jd(2022, 12, 31), de440_engine)
    assert len(eclipses_2022) == 2
    assert [e.classification for e in eclipses_2022] == ["total", "total"]


# ---------------------------------------------------------------------------
# 3. Retrograde Station & Shadow Period Tests
# ---------------------------------------------------------------------------

def test_mercury_retrograde_stations_and_shadow_periods_2024(de440_engine):
    # April 2024 Mercury retrograde loop (SR ~2024-04-01, SD ~2024-04-25)
    stations = find_retrograde_stations(
        "mercury", _tt_jd(2024, 3, 25), _tt_jd(2024, 5, 5), de440_engine
    )
    assert len(stations) == 2
    sr, sd = stations[0], stations[1]
    assert sr.kind == "station_retrograde"
    assert sr.is_retrograde_station is True
    assert sr.acceleration_deg_per_day2 < 0.0
    assert abs(sr.speed_deg_per_day) < 1e-4

    assert sd.kind == "station_direct"
    assert sd.is_retrograde_station is False
    assert sd.acceleration_deg_per_day2 > 0.0
    assert abs(sd.speed_deg_per_day) < 1e-4

    # Shadow period boundaries must bracket the retrograde loop
    assert sr.shadow_entry_jd_tt is not None
    assert sr.shadow_exit_jd_tt is not None
    assert sr.shadow_entry_jd_tt < sr.jd_tt < sd.jd_tt < sr.shadow_exit_jd_tt
    assert sr.companion_station_jd_tt == pytest.approx(sd.jd_tt, abs=1e-4)
    assert sr.receipt_sha256 == canonical_hash(sr.receipt)


def test_mars_jupiter_saturn_retrograde_stations(de440_engine):
    # Mars station retrograde in Dec 2024 (~2024-12-06/07) and station direct in Feb 2025 (~2025-02-24)
    mars_stations = find_retrograde_stations(
        "mars", _tt_jd(2024, 11, 20), _tt_jd(2025, 3, 10), de440_engine, compute_shadow_periods=False
    )
    assert len(mars_stations) == 2
    assert mars_stations[0].kind == "station_retrograde"
    assert mars_stations[1].kind == "station_direct"
    assert abs(mars_stations[0].jd_tt - _tt_jd(2024, 12, 6, 23, 0)) < 1.0
    assert abs(mars_stations[1].jd_tt - _tt_jd(2025, 2, 24, 2, 0)) < 1.0

    # Jupiter 2024 stations (SR ~2024-10-09, SD ~2025-02-04)
    jup_stations = find_retrograde_stations(
        "jupiter", _tt_jd(2024, 10, 1), _tt_jd(2024, 10, 20), de440_engine, compute_shadow_periods=False
    )
    assert len(jup_stations) == 1
    assert jup_stations[0].kind == "station_retrograde"

    # Saturn 2024 stations (SR ~2024-06-29, SD ~2024-11-15)
    sat_stations = find_retrograde_stations(
        "saturn", _tt_jd(2024, 6, 20), _tt_jd(2024, 11, 25), de440_engine, compute_shadow_periods=False
    )
    assert len(sat_stations) == 2
    assert [s.kind for s in sat_stations] == ["station_retrograde", "station_direct"]


def test_luminaries_have_no_retrograde_stations(de440_engine):
    assert find_retrograde_stations("sun", _tt_jd(2024, 1, 1), _tt_jd(2024, 6, 1), de440_engine) == ()
    assert find_retrograde_stations("moon", _tt_jd(2024, 1, 1), _tt_jd(2024, 2, 1), de440_engine) == ()


# ---------------------------------------------------------------------------
# 4. Surya Siddhanta Combustion (Moudhya / Astangata) & Cazimi Tests
# ---------------------------------------------------------------------------

@pytest.mark.parametrize(
    "body,is_retro,expected_orb",
    [
        ("moon", False, 12.0),
        ("mars", False, 17.0),
        ("mercury", False, 14.0),
        ("mercury", True, 12.0),
        ("jupiter", False, 11.0),
        ("venus", False, 10.0),
        ("venus", True, 8.0),
        ("saturn", False, 15.0),
    ],
)
def test_surya_siddhanta_combustion_orb_thresholds(body: str, is_retro: bool, expected_orb: float):
    assert combustion_orb_degrees(body, is_retrograde=is_retro) == expected_orb
    # Inside orb -> combust
    inside = check_combustion(100.0, body, 100.0 + expected_orb - 0.5, is_retrograde=is_retro)
    assert inside.is_combust is True
    assert inside.orb_threshold_deg == expected_orb
    assert inside.state == "combust"
    assert inside.receipt_sha256 == canonical_hash(inside.receipt)

    # Outside orb -> visible
    outside = check_combustion(100.0, body, 100.0 + expected_orb + 0.5, is_retrograde=is_retro)
    assert outside.is_combust is False
    assert outside.state == "visible"


def test_mercury_and_venus_direct_vs_retrograde_combustion_difference():
    # Mercury at 13 deg from Sun is combust when direct (14 deg orb) but visible when retrograde (12 deg orb)
    merc_direct = check_combustion(200.0, "mercury", 213.0, is_retrograde=False)
    merc_retro = check_combustion(200.0, "mercury", 213.0, is_retrograde=True)
    assert merc_direct.is_combust is True
    assert merc_retro.is_combust is False

    # Venus at 9 deg from Sun is combust when direct (10 deg orb) but visible when retrograde (8 deg orb)
    ven_direct = check_combustion(355.0, "venus", 4.0, is_retrograde=False)
    ven_retro = check_combustion(355.0, "venus", 4.0, is_retrograde=True)
    assert ven_direct.angular_separation_deg == pytest.approx(9.0)
    assert ven_direct.is_combust is True
    assert ven_retro.is_combust is False


def test_cazimi_detection_within_17_arcminutes():
    assert CAZIMI_ORB_DEG == pytest.approx(17.0 / 60.0)
    caz = check_combustion(120.0, "jupiter", 120.20, is_retrograde=False)
    assert caz.is_cazimi is True
    assert caz.is_combust is True
    assert caz.state == "cazimi"

    not_caz = check_combustion(120.0, "jupiter", 120.35, is_retrograde=False)
    assert not_caz.is_cazimi is False
    assert not_caz.is_combust is True
    assert not_caz.state == "combust"


def test_find_combustion_windows_jupiter_2024(de440_engine):
    # Jupiter solar conjunction occurred on 2024-05-18
    windows = find_combustion_windows("jupiter", _tt_jd(2024, 4, 15), _tt_jd(2024, 6, 20), de440_engine)
    assert len(windows) == 1
    w = windows[0]
    assert w.body == "jupiter"
    assert w.start_jd_tt < w.min_separation_jd_tt < w.end_jd_tt
    assert abs(w.min_separation_jd_tt - _tt_jd(2024, 5, 18, 18, 45)) < 0.5
    assert w.duration_days > 20.0
    assert w.receipt_sha256 == canonical_hash(w.receipt)


# ---------------------------------------------------------------------------
# 5. Graha Yuddha (Planetary War) Tests
# ---------------------------------------------------------------------------

def test_graha_yuddha_northern_latitude_victor():
    positions = {
        "mars": {"longitude_deg": 145.20, "latitude_deg": 1.25},
        "saturn": {"longitude_deg": 145.80, "latitude_deg": -0.40},
        "sun": {"longitude_deg": 145.50, "latitude_deg": 0.0},  # Sun must be ignored
    }
    wars = evaluate_graha_yuddha(positions)
    assert len(wars) == 1
    war = wars[0]
    assert war.jayin == "mars"
    assert war.parajita == "saturn"
    assert war.northern_body == "mars"
    assert war.victory_criterion == "northern_latitude"
    assert war.longitude_separation_deg == pytest.approx(0.60)
    assert war.receipt_sha256 == canonical_hash(war.receipt)


def test_graha_yuddha_venus_exemption_and_brightness_tiebreaker():
    # Venus south of Jupiter within 1 deg -> Venus wins with exemption, Jupiter wins without exemption
    positions = {
        "jupiter": {"longitude_deg": 32.10, "latitude_deg": 0.80},
        "venus": {"longitude_deg": 32.55, "latitude_deg": -1.10},
    }
    with_exemption = evaluate_graha_yuddha(positions, apply_venus_exemption=True)
    assert len(with_exemption) == 1
    assert with_exemption[0].jayin == "venus"
    assert with_exemption[0].parajita == "jupiter"
    assert with_exemption[0].venus_exemption_applied is True
    assert with_exemption[0].victory_criterion == "venus_exemption"

    without_exemption = evaluate_graha_yuddha(positions, apply_venus_exemption=False)
    assert len(without_exemption) == 1
    assert without_exemption[0].jayin == "jupiter"
    assert without_exemption[0].parajita == "venus"
    assert without_exemption[0].victory_criterion == "northern_latitude"

    # Tie in latitude -> brighter planet (Jupiter > Mercury) wins
    tied_lat = {
        "mercury": {"longitude_deg": 210.0, "latitude_deg": 0.50},
        "jupiter": {"longitude_deg": 210.4, "latitude_deg": 0.50},
    }
    tie_res = evaluate_graha_yuddha(tied_lat)
    assert len(tie_res) == 1
    assert tie_res[0].jayin == "jupiter"
    assert tie_res[0].parajita == "mercury"
    assert tie_res[0].victory_criterion == "apparent_brightness_disc"


def test_graha_yuddha_no_war_when_beyond_one_degree():
    positions = {
        "mars": {"longitude_deg": 10.0, "latitude_deg": 0.5},
        "jupiter": {"longitude_deg": 11.2, "latitude_deg": 0.1},
    }
    assert evaluate_graha_yuddha(positions) == ()


# ---------------------------------------------------------------------------
# 6. Sign Ingresses & Solar Sankranti Tests
# ---------------------------------------------------------------------------

def test_solar_makar_and_mesha_sankranti_2024(de440_engine):
    # Makar Sankranti 2024 (~2024-01-14/15 when Sun enters Makara / 270 deg Lahiri sidereal)
    jan_ingresses = find_sign_ingresses("sun", _tt_jd(2024, 1, 10), _tt_jd(2024, 1, 20), "lahiri", de440_engine)
    assert len(jan_ingresses) == 1
    makar = jan_ingresses[0]
    assert makar.from_rasi == "Dhanu"
    assert makar.to_rasi == "Makara"
    assert makar.sankranti_name == "Makar Sankranti"
    assert makar.boundary_longitude_deg == pytest.approx(270.0)
    assert makar.direction == "direct"
    assert makar.residual_arcsec < 0.01
    assert makar.receipt_sha256 == canonical_hash(makar.receipt)

    # Mesha Sankranti 2024 (~2024-04-13 when Sun enters Mesha / 0 deg Lahiri sidereal)
    apr_ingresses = find_sign_ingresses("sun", _tt_jd(2024, 4, 10), _tt_jd(2024, 4, 18), "lahiri", de440_engine)
    assert len(apr_ingresses) == 1
    mesha = apr_ingresses[0]
    assert mesha.from_rasi == "Meena"
    assert mesha.to_rasi == "Mesha"
    assert mesha.sankranti_name == "Mesha Sankranti"
    assert mesha.boundary_longitude_deg == pytest.approx(0.0)
    assert mesha.residual_arcsec < 0.01


def test_full_year_solar_sankrantis_and_jupiter_transit_2024(de440_engine):
    # All 12 Solar Sankrantis in 2024
    sankrantis = find_sign_ingresses("sun", _tt_jd(2024, 1, 1), _tt_jd(2024, 12, 31), "lahiri", de440_engine)
    assert len(sankrantis) == 12
    assert [s.to_rasi_index for s in sankrantis] == [9, 10, 11, 0, 1, 2, 3, 4, 5, 6, 7, 8]

    # Jupiter transit from Mesha (Aries) to Vrishabha (Taurus) on 2024-05-01 (Lahiri sidereal)
    jup_ingresses = find_sign_ingresses("jupiter", _tt_jd(2024, 4, 20), _tt_jd(2024, 5, 10), "lahiri", de440_engine)
    assert len(jup_ingresses) == 1
    jup = jup_ingresses[0]
    assert jup.from_rasi == "Mesha"
    assert jup.to_rasi == "Vrishabha"
    assert jup.boundary_longitude_deg == pytest.approx(30.0)
    assert abs(jup.jd_tt - _tt_jd(2024, 5, 1, 7, 30)) < 1.0


def test_custom_callable_position_provider_for_eclipses_and_phenomena(de440_engine):
    def custom_provider(jd_tt: float, bodies):
        return de440_engine.positions_tt(jd_tt, bodies).value

    se = solar_eclipse_at(_tt_jd(2017, 8, 21, 18, 26), position_provider=custom_provider)
    assert se is not None
    assert se.classification == "total"

    ing = find_sign_ingresses(
        "sun", _tt_jd(2024, 1, 12), _tt_jd(2024, 1, 17), "lahiri", position_provider=custom_provider
    )
    assert len(ing) == 1
    assert ing[0].sankranti_name == "Makar Sankranti"


def test_builtin_phenomena_without_kernel_fallback():
    # Built-in evaluator (engine=None) solves stations, combustion windows, and Sankrantis
    stations = find_retrograde_stations(
        "mercury", _tt_jd(2024, 3, 25), _tt_jd(2024, 5, 5), None, compute_shadow_periods=False
    )
    assert len(stations) == 2
    assert [s.kind for s in stations] == ["station_retrograde", "station_direct"]

    ingresses = find_sign_ingresses("sun", _tt_jd(2024, 1, 12), _tt_jd(2024, 1, 17), "lahiri", None)
    assert len(ingresses) == 1
    assert ingresses[0].sankranti_name == "Makar Sankranti"


def test_graha_yuddha_accepts_engine_result_directly(de440_engine):
    # Passing an Engine.positions_tt Result object directly works seamlessly
    res = de440_engine.positions_tt(
        _tt_jd(2024, 4, 10, 12, 0), bodies=("mars", "saturn", "mercury", "venus", "jupiter")
    )
    wars = evaluate_graha_yuddha(res)
    # Mars and Saturn were in close conjunction (< 1 deg) on 2024-04-10!
    assert len(wars) == 1
    assert {wars[0].body_a, wars[0].body_b} == {"mars", "saturn"}
    assert wars[0].jayin == "mars"
    assert wars[0].parajita == "saturn"


def test_receipt_determinism_and_parameter_sensitivity():
    c1 = check_combustion(50.0, "mercury", 60.0, is_retrograde=False)
    c1_repeat = check_combustion(50.0, "mercury", 60.0, is_retrograde=False)
    c2 = check_combustion(50.0, "mercury", 60.0, is_retrograde=True)
    assert c1.receipt_sha256 == c1_repeat.receipt_sha256
    assert c1.receipt_sha256 != c2.receipt_sha256

