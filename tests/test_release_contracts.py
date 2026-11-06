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


def _disk_area_fraction(r: float, R: float, d: float) -> float:
    if d >= r + R:
        return 0.0
    if d <= abs(r - R):
        return min(r, R) ** 2 / r ** 2
    overlap = (
        r * r * math.acos((d * d + r * r - R * R) / (2 * d * r))
        + R * R * math.acos((d * d + R * R - r * r) / (2 * d * R))
        - 0.5 * math.sqrt((-d + r + R) * (d + r - R) * (d - r + R) * (d + r + R))
    )
    return overlap / (math.pi * r * r)


def _geometry(jd: float, lat: float, lon: float) -> tuple[float, float]:
    top = compute_topocentric_relativistic_astrometry(jd, lat, lon)
    sun, moon = top.bodies["sun"], top.bodies["moon"]
    ra, dec, mra, mdec = map(
        math.radians,
        [
            sun.topocentric_ra_deg,
            sun.topocentric_dec_deg,
            moon.topocentric_ra_deg,
            moon.topocentric_dec_deg,
        ],
    )
    separation = math.acos(
        max(
            -1.0,
            min(
                1.0,
                math.sin(dec) * math.sin(mdec)
                + math.cos(dec) * math.cos(mdec) * math.cos(ra - mra),
            ),
        )
    )
    r = math.asin(695700 / sun.distance_km)
    R = math.asin(1737.4 / moon.distance_km)
    return _disk_area_fraction(r, R, separation), sun.apparent_altitude_deg


@pytest.mark.parametrize(
    "r,R,d,expected",
    [
        (1.0, 1.0, 3.0, 0.0),
        (2.0, 1.0, 0.0, 0.25),
        (1.0, 2.0, 0.0, 1.0),
        (1.0, 1.0, 1.0, 2 / 3 - math.sqrt(3) / (2 * math.pi)),
    ],
)
def test_independent_area_formula_has_known_clean_controls(
    r: float, R: float, d: float, expected: float
) -> None:
    assert _disk_area_fraction(r, R, d) == pytest.approx(expected, abs=1e-12)


@pytest.mark.parametrize("latitude,longitude", [(64.15, -21.94), (43.36, -5.85)])
def test_obscuration_reports_area_instead_of_diameter(
    latitude: float, longitude: float
) -> None:
    event = evaluate_lifetime_eclipse_natal_sensitivity(
        2461262.5, 2461266.5, latitude_deg=latitude, longitude_deg=longitude
    ).eclipses[0]
    area, altitude = _geometry(event.maximum_jd_ut, latitude, longitude)
    assert altitude > 0 and event.local_visible
    assert event.local_obscuration_fraction == pytest.approx(area, abs=0.001)


def test_observer_visibility_accounts_for_local_eclipse_time() -> None:
    latitude, longitude = 40.4168, -3.7038
    event = evaluate_lifetime_eclipse_natal_sensitivity(
        2461262.5, 2461266.5, latitude_deg=latitude, longitude_deg=longitude
    ).eclipses[0]
    samples = [
        _geometry(event.maximum_jd_ut + minutes / 1440, latitude, longitude)
        for minutes in [30, 45, 60, 75, 90]
    ]
    assert any(area > 0.01 and altitude > 0 for area, altitude in samples), samples
    assert event.local_visible, (event, samples)


LOCATIONS = [(64.15, -21.94), (43.36, -5.85), (40.4168, -3.7038)]


@pytest.fixture(scope="module", params=LOCATIONS)
def observer_case(request: pytest.FixtureRequest) -> tuple[float, float, object]:
    lat, lon = request.param
    report = evaluate_lifetime_eclipse_natal_sensitivity(
        2461262.5, 2461266.5, latitude_deg=lat, longitude_deg=lon
    )
    event = report.eclipses[0]
    return lat, lon, event


def test_broad_range_clean_control_contains_returned_local_maximum(
    observer_case: tuple[float, float, object]
) -> None:
    _, _, event = observer_case
    assert event.local_visible and 2461262.5 <= event.maximum_jd_ut <= 2461266.5


def test_narrow_range_around_returned_local_maximum_retains_event(
    observer_case: tuple[float, float, object]
) -> None:
    lat, lon, event = observer_case
    report = evaluate_lifetime_eclipse_natal_sensitivity(
        event.maximum_jd_ut - 5 / 1440,
        event.maximum_jd_ut + 5 / 1440,
        latitude_deg=lat,
        longitude_deg=lon,
    )
    assert any(abs(x.maximum_jd_ut - event.maximum_jd_ut) < 1 / 1440 for x in report.eclipses)


def test_no_returned_local_maximum_is_outside_requested_range() -> None:
    start, end = 2461265.233848572 - 5 / 1440, 2461265.233848572 + 5 / 1440
    report = evaluate_lifetime_eclipse_natal_sensitivity(
        start, end, latitude_deg=40.4168, longitude_deg=-3.7038
    )
    assert all(start <= x.maximum_jd_ut <= end for x in report.eclipses), report.eclipses


