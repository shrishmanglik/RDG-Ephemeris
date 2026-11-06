"""Release contract regressions for RDG Ephemeris v1.3.0 (PR #26)."""
import math
import pytest
from ephemeris_oss import EphemerisAdapter
from ephemeris_oss.jyotish.dasha import compute_ashtottari_dasha
from ephemeris_oss.jyotish.conditional_dashas_and_nadi import (
    compute_all_10_parashari_nakshatra_dashas,
    compute_vimshottari_5_level_prana_chronometer,
)
from ephemeris_oss.frontier_astrodynamics import (
    evaluate_lifetime_eclipse_natal_sensitivity,
    compute_topocentric_relativistic_astrometry,
)
from ephemeris_oss.jyotish.harmonic_vedha_and_pinda import (
    compute_sarvatobhadra_81_ray_vedha,
)

LONS = {
    "sun": 225.4,
    "moon": 85.0,
    "mars": 115.2,
    "mercury": 218.9,
    "jupiter": 102.5,
    "venus": 195.1,
    "saturn": 344.2,
    "rahu": 312.0,
    "ketu": 132.0,
}


@pytest.mark.parametrize("moon", [70.0, 85.0, 100.0, 42.8])
def test_ashtottari_agrees_with_existing_28_star_mapping(moon: float) -> None:
    rep = compute_all_10_parashari_nakshatra_dashas(
        moon, 48.2, 225.4, LONS, 2451545.0, query_jd=2451545.0
    )
    new = next(x for x in rep.systems if x.system_key == "ashtottari")
    assert new.opening_lord == compute_ashtottari_dasha(moon, 2451545.0).opening_lord


@pytest.mark.parametrize("offset", [-0.0001, 0.0, 0.0001])
def test_prana_query_has_exactly_one_active_window(offset: float) -> None:
    initial = compute_vimshottari_5_level_prana_chronometer(42.8, 2451545.0, 2461345.5)
    boundary = initial.prana_windows[2].end_jd
    rep = compute_vimshottari_5_level_prana_chronometer(
        42.8, 2451545.0, boundary + offset
    )
    assert sum(w.is_active_at_query for w in rep.prana_windows) == 1


@pytest.fixture(scope="module")
def delhi_eclipse():
    return evaluate_lifetime_eclipse_natal_sensitivity(
        2461086.5, 2461092.5, latitude_deg=28.6139, longitude_deg=77.2090
    ).eclipses[0]


def test_solar_local_visibility_requires_disk_overlap(delhi_eclipse) -> None:
    e = delhi_eclipse
    topo = compute_topocentric_relativistic_astrometry(
        e.maximum_jd_ut, 28.6139, 77.2090
    )
    s, m = topo.bodies["sun"], topo.bodies["moon"]
    sr, sd, mr, md = map(
        math.radians,
        [
            s.topocentric_ra_deg,
            s.topocentric_dec_deg,
            m.topocentric_ra_deg,
            m.topocentric_dec_deg,
        ],
    )
    sep = math.degrees(
        math.acos(
            math.sin(sd) * math.sin(md)
            + math.cos(sd) * math.cos(md) * math.cos(sr - mr)
        )
    )
    radius_sum = math.degrees(
        math.asin(695700 / s.distance_km) + math.asin(1737.4 / m.distance_km)
    )
    assert sep > radius_sum
    assert e.local_visible is False and e.local_obscuration_fraction == 0.0


def test_eclipse_is_retained_when_range_narrows_around_event(delhi_eclipse) -> None:
    e = delhi_eclipse
    rep = evaluate_lifetime_eclipse_natal_sensitivity(
        e.maximum_jd_ut - 0.25, e.maximum_jd_ut + 0.25
    )
    assert any(
        abs(x.maximum_jd_ut - e.maximum_jd_ut) < 1.0 / 86400 for x in rep.eclipses
    )


@pytest.mark.parametrize("jd", [2451545.0, 2461350.0])
def test_topocentric_ecliptic_and_equatorial_coordinates_use_same_date_frame(
    jd: float,
) -> None:
    ad = EphemerisAdapter()
    rep = compute_topocentric_relativistic_astrometry(
        jd, 28.6139, 77.2090, adapter=ad
    )
    moon = rep.bodies["moon"]
    t = (jd - 2451545.0) / 36525.0
    eps = math.radians(
        23.43929111 - (46.8150 * t + 0.00059 * t * t - 0.001813 * t * t * t) / 3600.0
    )
    ra, dec = map(
        math.radians, [moon.topocentric_ra_deg, moon.topocentric_dec_deg]
    )
    tropical = (
        math.degrees(
            math.atan2(
                math.sin(ra) * math.cos(eps) + math.tan(dec) * math.sin(eps),
                math.cos(ra),
            )
        )
        % 360
    )
    expected = (tropical - ad.get_ayanamsa_ut(jd, mode="lahiri")) % 360
    error = abs((moon.topocentric_sidereal_lon_deg - expected + 180) % 360 - 180) * 3600
    assert error < 0.1, f"date-frame inconsistency {error} arcsec"


@pytest.mark.parametrize("moon", [1.0, 148.0, 285.0])
def test_sarvatobhadra_natal_star_hit_names_exact_star(moon: float) -> None:
    rep = compute_sarvatobhadra_81_ray_vedha(2461350.0, moon)
    bad = [
        (h.target_label, rep.natal_janma_nakshatra_28)
        for h in rep.active_ray_hits
        if h.hits_natal_janma_nakshatra
        and h.target_label.lower() != rep.natal_janma_nakshatra_28.lower()
    ]
    assert not bad
