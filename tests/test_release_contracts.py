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


from pathlib import Path
from types import SimpleNamespace
from dataclasses import replace
import erfa
from ephemeris_oss.impossible_astrology import (
    solve_chart_date_from_planetary_constraints,
    compute_triple_lock_life_event_convergence,
)
from ephemeris_oss.jyotish.dasha import compute_kalachakra_dasha
from ephemeris_oss.jyotish.conditional_dashas_and_nadi import (
    solve_golden_muhurta_electional_windows,
    SOLAR_YEAR_DAYS,
)
from ephemeris_oss.jyotish.panchanga import compute_muhurta_windows
from ephemeris_oss.engine.stellar_anchors import YOGATARA_30_CATALOG, propagate_yogatara_apparent
from ephemeris_oss.jyotish.vargas import SHASHTIAMSA_CATALOG


class _BirthMoonAdapter:
    def __init__(self) -> None:
        self.actual = EphemerisAdapter()

    def __getattr__(self, name: str):
        return getattr(self.actual, name)

    def calc_ut(self, jd: float, body: str, **kwargs):
        value = self.actual.calc_ut(jd, body, **kwargs)
        return replace(value, longitude_deg=1.0) if body == "moon" and jd == 2451545.0 else value


@pytest.mark.parametrize("age", [0, 100])
def test_kalachakra_repeats_the_full_paramayus_at_natal_phase(age: int) -> None:
    birth = 2451545.0
    natal = compute_kalachakra_dasha(1.0, birth)
    jd = birth + age * natal.year_days
    report = compute_triple_lock_life_event_convergence(
        birth, 28.6139, 77.209, jd, jd, adapter=_BirthMoonAdapter()
    )
    assert natal.paramayus_years == 100
    assert report.sampled_timeline[0].kalachakra_sign == natal.mahadashas[0].sign_name


def _circular_difference(a: float, b: float) -> float:
    return (a - b + 180.0) % 360.0 - 180.0


@pytest.mark.parametrize("jd", [2451545.0, 2086302.5])
def test_physical_center_velocity_includes_its_position_correction_derivative(jd: float) -> None:
    ad = EphemerisAdapter()

    def correction(t: float) -> float:
        p = ad.calc_ut(t, "jupiter", physical_center=True)
        b = ad.calc_ut(t, "jupiter", physical_center=False)
        return _circular_difference(p.longitude_deg, b.longitude_deg)

    h = 0.05
    expected = (correction(jd + h) - correction(jd - h)) / (2 * h) * 3600
    p = ad.calc_ut(jd, "jupiter", physical_center=True)
    b = ad.calc_ut(jd, "jupiter", physical_center=False)
    actual = (p.longitude_speed_deg_per_day - b.longitude_speed_deg_per_day) * 3600
    assert abs(expected) > 0.0001
    assert actual == pytest.approx(expected, abs=0.0001)


class _LinearAdapter:
    def __init__(self, mercury_entry: float) -> None:
        self.mercury_entry = mercury_entry

    def calc_ut(self, jd: float, body: str, **kwargs):
        day = jd - sum(erfa.cal2jd(2026, 1, 1))
        lon = 29.4 + day if body == "sun" else (30 - self.mercury_entry + day if body == "mercury" else 0)
        return SimpleNamespace(longitude_deg=lon % 360)


@pytest.mark.parametrize("mercury_entry", [-0.2, 0.2])
def test_inverse_solver_retains_joint_subday_sign_window(mercury_entry: float) -> None:
    report = solve_chart_date_from_planetary_constraints(
        2026, 2026, {"sun": "Aries", "mercury": "Taurus"}, adapter=_LinearAdapter(mercury_entry)
    )
    assert report.match_count > 0


@pytest.mark.parametrize("seconds", [-1, 0, 1])
def test_prana_mahadasha_boundary_selects_incoming_hierarchy(seconds: int) -> None:
    jd = 2451545.0 + 7 * SOLAR_YEAR_DAYS + seconds / 86400
    report = compute_vimshottari_5_level_prana_chronometer(0.0, 2451545.0, jd)
    expected = "Ketu" if seconds < 0 else "Venus"
    assert report.mahadasha_lord == expected


def test_prana_antardasha_boundary_selects_incoming_period() -> None:
    jd = 2451545.0 + (7 * SOLAR_YEAR_DAYS) * (7 / 120)
    report = compute_vimshottari_5_level_prana_chronometer(0.0, 2451545.0, jd)
    assert report.mahadasha_lord == "Ketu" and report.antardasha_lord == "Venus"


@pytest.mark.parametrize("epoch", [1600.0, 2000.0, 2400.0])
def test_stellar_equatorial_coordinates_are_continuous_across_date_branches(epoch: float) -> None:
    star = YOGATARA_30_CATALOG[0]

    def position(e: float):
        return propagate_yogatara_apparent(star, tt=(2451545.0, (e - 2000) * 365.25), ayanamsa_deg=0.0)

    left, right = position(epoch - 1e-6), position(epoch + 1e-6)
    dra = abs(_circular_difference(right.ra_deg, left.ra_deg))
    ddec = abs(right.dec_deg - left.dec_deg)
    assert dra < 0.01 and ddec < 0.01


@pytest.mark.parametrize("hour", [5.5, 8.0])
def test_muhurta_uses_current_sunrise_for_early_day_exclusions(hour: float) -> None:
    ad = EphemerisAdapter()
    day = sum(erfa.cal2jd(2026, 6, 18))
    candidate = day + hour / 24
    _, (sunrise,) = ad.rise_trans(day, "sun", 1, (0.0, 45.0, 0.0))
    _, (sunset,) = ad.rise_trans(sunrise, "sun", 2, (0.0, 45.0, 0.0))
    _, (next_sunrise,) = ad.rise_trans(sunset, "sun", 1, (0.0, 45.0, 0.0))
    windows = compute_muhurta_windows(sunrise, sunset, next_sunrise_jd=next_sunrise, vara_index=4)
    expected = bool(windows.yamagandam.start_jd <= candidate < windows.yamagandam.end_jd)
    report = solve_golden_muhurta_electional_windows(
        candidate, candidate, latitude_deg=45.0, longitude_deg=0.0, adapter=ad
    )
    row = report.top_windows[0]
    actual = any("Yamagandam" in x for x in row.warnings)
    assert expected == (hour == 5.5)
    assert actual == expected


@pytest.mark.parametrize("benefic", [False, True])
def test_printed_d60_nature_matches_the_boolean_catalog(benefic: bool) -> None:
    _, name, flag = next(x for x in SHASHTIAMSA_CATALOG if x[2] is benefic)
    doc_path = Path(__file__).resolve().parents[1] / "docs" / "HUMAN-READABLE-EPHEMERIS-AND-JYOTISH-ACADEMY-MANUAL.md"
    text = doc_path.read_text(encoding="utf-8")
    label = "Shubha (Benefic)" if flag else "Krura (Malefic)"
    actual = [line for line in text.splitlines() if f"**{name}** | " in line and "°" in line]
    assert actual and any(f"**{name}** | {label}" in line for line in actual)


class _RecordingNodeAdapter:
    def __init__(self) -> None:
        self.flags: list[bool] = []

    def calc_ut(self, jd_ut: float, body: str, **kwargs):
        flag = bool(kwargs.get("true_node", False))
        self.flags.append(flag)
        return SimpleNamespace(longitude_deg=30.0 if flag else 0.0)


@pytest.mark.parametrize(
    "alias,true_node_flag,use_nak",
    [
        ("true_rahu", False, False),
        ("true_node", False, False),
        ("true_ketu", False, False),
        ("true_rahu", False, True),
        ("rahu", True, False),
    ],
)
def test_explicit_node_alias_preserves_model_in_signs_and_nakshatras(
    alias: str, true_node_flag: bool, use_nak: bool
) -> None:
    ad = _RecordingNodeAdapter()
    rep = solve_chart_date_from_planetary_constraints(
        2026,
        2026,
        {} if use_nak else {alias: "Aries"},
        nakshatra_constraints={alias: "Ashwini"} if use_nak else None,
        true_node=true_node_flag,
        adapter=ad,
        max_results=1,
    )
    assert ad.flags and all(ad.flags)
    assert rep.match_count == 0


class _ConfiguredAnalyticalAdapter:
    def __init__(self, ayanamsa: str) -> None:
        from ephemeris_oss.adapter import AnalyticalEphemerisProvider

        self.provider = AnalyticalEphemerisProvider()
        self.provider.set_ayanamsa(ayanamsa)

    def calc_ut(self, jd_ut: float, body: str, sidereal: bool = True, ayanamsa: str = "lahiri"):
        from ephemeris_oss.adapter import FLG_SIDEREAL

        vals, _ = self.provider.calc_ut(jd_ut, body.capitalize(), flags=FLG_SIDEREAL if sidereal else 0)
        return SimpleNamespace(longitude_deg=float(vals[0]), longitude_speed_deg_per_day=float(vals[3]))

    def rise_trans(self, jd_ut: float, body: str, rsmi: int, geopos):
        return self.provider.rise_trans(jd_ut, body.capitalize(), rsmi, geopos)


@pytest.mark.parametrize("mode", ["lahiri", "raman"])
def test_default_monthly_provider_obeys_the_requested_convention(mode: str) -> None:
    from ephemeris_oss.almanac.panchang_calendar import generate_monthly_panchang

    default_sheet = generate_monthly_panchang(2026, 11, 28.6139, 77.209, ayanamsa=mode)
    configured = generate_monthly_panchang(
        2026, 11, 28.6139, 77.209, ayanamsa=mode, adapter=_ConfiguredAnalyticalAdapter(mode)
    )
    assert default_sheet.days[0].sun_sidereal_lon_deg == pytest.approx(configured.days[0].sun_sidereal_lon_deg)
    assert default_sheet.days[0].moon_sidereal_lon_deg == pytest.approx(configured.days[0].moon_sidereal_lon_deg)


class _RayAdapter:
    def __init__(self, target_body: str, speed: float) -> None:
        self.target_body = target_body.lower()
        self.speed = speed

    def calc_ut(self, jd_ut: float, body: str, sidereal: bool = True, ayanamsa: str = "lahiri"):
        is_target = body.lower() == self.target_body
        lon = 30.0 if is_target else 120.0
        spd = self.speed if is_target else 1.0
        return SimpleNamespace(longitude_deg=lon, longitude_speed_deg_per_day=spd)


@pytest.mark.parametrize("body,speed,expect_hit", [("mars", 1.0, False), ("mars", -1.0, True), ("sun", 1.0, True)])
def test_only_motion_active_rays_can_hit_the_natal_moon(body: str, speed: float, expect_hit: bool) -> None:
    rep = compute_sarvatobhadra_81_ray_vedha(2451545.0, 14.0, adapter=_RayAdapter(body, speed))
    cap = body.capitalize()
    assert (cap in rep.janma_nakshatra_vedha_planets) is expect_hit
    assert any(h.transiting_body == cap and h.hits_natal_janma_nakshatra for h in rep.active_ray_hits) is expect_hit


class _LinearSunMoon:
    def __init__(self, entry: float) -> None:
        self.entry = entry

    def calc_ut(self, jd: float, body: str, **kwargs):
        day = jd - sum(erfa.cal2jd(2026, 1, 1))
        lon = 29.9 + day if body == "sun" else (30.0 - self.entry + day if body == "moon" else 0.0)
        return SimpleNamespace(longitude_deg=lon % 360.0)


@pytest.mark.parametrize("entry", [0.0, 0.02])
def test_final_stage_preserves_a_short_joint_constraint_window(entry: float) -> None:
    report = solve_chart_date_from_planetary_constraints(
        2026, 2026, {"sun": "Aries", "moon": "Taurus"}, max_results=1, adapter=_LinearSunMoon(entry)
    )
    assert report.match_count > 0
    jd_jan1 = sum(erfa.cal2jd(2026, 1, 1))
    assert report.matches[0].window_start_jd_ut == pytest.approx(jd_jan1 + entry, abs=1e-4)
    assert report.matches[0].window_end_jd_ut == pytest.approx(jd_jan1 + 0.10, abs=1e-4)
    assert report.matches[0].window_duration_hours == pytest.approx(round((0.10 - entry) * 24.0, 2), abs=0.02)


class _GeneratedWindowAdapter:
    def __init__(self, entry_day: float, exit_day: float, use_nakshatra: bool) -> None:
        self.entry_day = entry_day
        self.exit_day = exit_day
        self.use_nakshatra = use_nakshatra
        self.jd_0 = sum(erfa.cal2jd(2026, 1, 1))

    def calc_ut(self, jd: float, body: str, **kwargs):
        day = jd - self.jd_0
        b = body.lower()
        if not self.use_nakshatra:
            # Target: sun in Aries [0, 30) exits at exit_day; moon enters Taurus [30, 60) at entry_day
            if b == "sun":
                lon = 30.0 - self.exit_day + day
            elif b == "moon":
                lon = 30.0 - self.entry_day + day
            else:
                lon = 15.0
        else:
            # Target: sun in Ashwini [0, 13.3333) exits at exit_day; moon enters Bharani [13.3333, 26.6667) at entry_day
            span = 360.0 / 27.0
            if b == "sun":
                lon = span - self.exit_day + day
            elif b == "moon":
                lon = span - self.entry_day + day
            else:
                lon = 5.0
        return SimpleNamespace(longitude_deg=lon % 360.0)


def test_generated_inverse_interval_and_ayanamsa_matrix(monkeypatch) -> None:
    """Generated class-wide test over 36 synthetic short-overlap intervals and 6 ayanamsa conventions."""
    from ephemeris_oss.almanac import human_ephemeris as human
    from ephemeris_oss.almanac.ephemeris_tables import generate_ephemeris_table, scan_ingresses_and_aspects

    jd_jan1 = sum(erfa.cal2jd(2026, 1, 1))
    entries = (0.0, 0.01, 0.02, 0.04, 0.07, 0.11)
    exits = (0.05, 0.10, 0.18, 0.45)
    case_count = 0
    for use_nak in (False, True):
        for entry_d in entries:
            for exit_d in exits:
                if exit_d <= entry_d + 0.015:
                    continue
                case_count += 1
                ad = _GeneratedWindowAdapter(entry_d, exit_d, use_nak)
                if not use_nak:
                    rep = solve_chart_date_from_planetary_constraints(
                        2026, 2026, {"sun": "Aries", "moon": "Taurus"}, max_results=1, adapter=ad
                    )
                else:
                    rep = solve_chart_date_from_planetary_constraints(
                        2026,
                        2026,
                        {},
                        nakshatra_constraints={"sun": "Ashwini", "moon": "Bharani"},
                        max_results=1,
                        adapter=ad,
                    )
                assert rep.match_count == 1, f"Failed for entry={entry_d}, exit={exit_d}, nak={use_nak}"
                w = rep.matches[0]
                expected_hours = round((exit_d - entry_d) * 24.0, 2)
                assert w.window_start_jd_ut == pytest.approx(jd_jan1 + entry_d, abs=1e-4)
                assert w.window_end_jd_ut == pytest.approx(jd_jan1 + exit_d, abs=1e-4)
                assert w.window_duration_hours == pytest.approx(expected_hours, abs=0.02)
    assert case_count >= 36

    for mode in ("lahiri", "raman", "krishnamurti", "fagan_bradley", "yukteshwar", "true_chitrapaksha"):
        ad_track = _TrackingAdapter()
        ad_track.scanning = True
        tbl = generate_ephemeris_table(2461345.5, 2461347.5, step_days=1.0, ayanamsa=mode, adapter=ad_track)
        assert ad_track.scan_modes == {mode}
        expected_ay = ad_track.actual.get_ayanamsa_ut(2461345.5, mode=mode)
        assert tbl.rows[0].ayanamsa_deg == pytest.approx(expected_ay, abs=1e-6)

        ad_scan = _TrackingAdapter()
        ad_scan.scanning = True
        timeline = scan_ingresses_and_aspects(
            2461345.5, 2461375.5, bodies=("Sun",), aspect_angles=(0.0,), ayanamsa=mode, adapter=ad_scan
        )
        assert ad_scan.scan_modes == {mode}
        sun_ing = next(e for e in timeline.rashi_ingresses if e.body.lower() == "sun")
        sel_lon = ad_scan.actual.calc_ut(sun_ing.jd_ut, "sun", sidereal=True, ayanamsa=mode).longitude_deg
        res_deg = abs((sel_lon - sun_ing.boundary_longitude_deg + 180.0) % 360.0 - 180.0)
        assert res_deg < 0.001


class _TrackingAdapter:
    def __init__(self) -> None:
        self.actual = EphemerisAdapter()
        self.scanning = False
        self.scan_modes: set[str] = set()

    def __getattr__(self, name: str):
        return getattr(self.actual, name)

    def calc_ut(self, jd: float, body: str, *, sidereal: bool = False, ayanamsa: str = "lahiri", **kwargs):
        if self.scanning and sidereal:
            self.scan_modes.add(ayanamsa)
        return self.actual.calc_ut(jd, body, sidereal=sidereal, ayanamsa=ayanamsa, **kwargs)


@pytest.mark.parametrize("mode", ["lahiri", "raman"])
def test_compendium_phenomena_respect_the_selected_convention(mode: str, monkeypatch) -> None:
    from ephemeris_oss.almanac import human_ephemeris as human

    ad = _TrackingAdapter()
    original = human.scan_ingresses_and_aspects

    def observed_scan(*args, **kwargs):
        ad.scanning = True
        try:
            return original(*args, **kwargs)
        finally:
            ad.scanning = False

    monkeypatch.setattr(human, "scan_ingresses_and_aspects", observed_scan)
    comp = human.generate_human_manual_ephemeris_compendium(2026, 11, ayanamsa=mode, adapter=ad)
    event = next(e for e in comp.phenomena_summary["rashi_ingresses"] if e.body.lower() == "sun")
    selected_lon = ad.actual.calc_ut(event.jd_ut, "sun", sidereal=True, ayanamsa=mode).longitude_deg
    residual = abs((selected_lon - event.boundary_longitude_deg + 180.0) % 360.0 - 180.0)
    assert ad.scan_modes == {mode}
    assert residual < 0.001


class _CurveOracleAdapter:
    def __init__(self, curves: dict[str, object], jd_0: float) -> None:
        self.curves = curves
        self.jd_0 = jd_0

    def longitude(self, day: float, body: str) -> float:
        fn = self.curves.get(body.lower(), lambda _t: 15.0)
        return float(fn(day)) % 360.0

    def calc_ut(self, jd: float, body: str, **kwargs):
        return SimpleNamespace(longitude_deg=self.longitude(jd - self.jd_0, body))


def test_generated_stationary_excursion_and_planet_key_matrix() -> None:
    """Generated Round-8 matrix covering non-monotonic stationary excursions against a dense reference oracle and planet-key casing/alias normalization."""
    from ephemeris_oss.jyotish.conditional_dashas_and_nadi import (
        compute_all_10_parashari_nakshatra_dashas,
        compute_nadi_amsa_and_sudarshana_chakra,
    )

    jd_0 = sum(erfa.cal2jd(2026, 1, 1))
    station_specs = []
    # 12 symmetric + 6 asymmetric stationary excursions + 2 live Saturn station controls = 20 curve cases
    for body, center, accel, radius, end_day in (
        ("mercury", 0.5, 0.001, 0.1, 1.0),
        ("saturn", 5.0, 0.0001, 1.0, 10.0),
    ):
        for sign_idx in (0, 1, 11):
            for is_peak in (True, False):
                station_specs.append((body, center, accel, radius, end_day, sign_idx, is_peak))
    for center_asym in (0.23, 0.77, 3.15):
        end_d = 1.0 if center_asym < 1.0 else 10.0
        rad_d = 0.08 if center_asym < 1.0 else 0.9
        acc_d = 0.001 if center_asym < 1.0 else 0.0001
        b_name = "mercury" if center_asym < 1.0 else "saturn"
        for is_peak in (True, False):
            station_specs.append((b_name, center_asym, acc_d, rad_d, end_d, 1, is_peak))

    station_count = 0
    for body, center, accel, radius, end_day, sign_idx, is_peak in station_specs:
        station_count += 1
        boundary = sign_idx * 30.0 if is_peak else (sign_idx + 1) * 30.0
        direction = 1.0 if is_peak else -1.0

        def _curve(t: float, c=center, a=accel, r=radius, e=end_day, b=boundary, d=direction) -> float:
            t_clamped = min(max(t, 0.0), e)
            return b + d * a * (r * r - (t_clamped - c) ** 2)

        ad = _CurveOracleAdapter({body: _curve}, jd_0)
        step = end_day / 20000.0
        dense_in = [i * step for i in range(20001) if int(ad.longitude(i * step, body) // 30.0) == sign_idx]
        assert dense_in, f"Invalid oracle fixture for {body} sign={sign_idx}"
        want_start, want_end = min(dense_in), max(dense_in)

        rep = solve_chart_date_from_planetary_constraints(2026, 2026, {body: sign_idx}, max_results=5, adapter=ad)
        assert rep.match_count == 1, f"Missed stationary excursion for {body} center={center} sign={sign_idx} peak={is_peak}"
        got_start = rep.matches[0].window_start_jd_ut - jd_0
        got_end = rep.matches[0].window_end_jd_ut - jd_0
        assert abs(got_start - want_start) <= step + 2e-4
        assert abs(got_end - want_end) <= step + 2e-4
        mid_lon = ad.longitude(0.5 * (got_start + got_end), body)
        assert int(mid_lon // 30.0) == sign_idx
    assert station_count == 18

    # Live Saturn turning vs linear control (2 cases -> 20 total trajectory cases):
    for turning in (False, True):
        def _sat_curve(t: float, turn=turning) -> float:
            tc = min(t, 10.0)
            return 29.99 + 0.0008 * tc * (10.0 - tc) if turn else 29.99 + 0.008 * tc

        ad_sat = _CurveOracleAdapter({"saturn": _sat_curve}, jd_0)
        rep_sat = solve_chart_date_from_planetary_constraints(2026, 2026, {"saturn": "Taurus"}, max_results=1, adapter=ad_sat)
        assert rep_sat.match_count == 1
        mid_jd = 0.5 * (rep_sat.matches[0].window_start_jd_ut + rep_sat.matches[0].window_end_jd_ut)
        assert 30.0 <= ad_sat.calc_ut(mid_jd, "saturn").longitude_deg < 60.0

    # 12 planet-key-variant equivalence cases (2 Rahu longitudes x 6 key variants) + missing-key guard:
    for rahu_lon in (150.0, 270.0):
        base_map = {
            "sun": 10.0,
            "moon": 70.0,
            "mars": 60.0,
            "mercury": 90.0,
            "jupiter": 120.0,
            "venus": 180.0,
            "saturn": 210.0,
            "rahu": rahu_lon,
            "ketu": (rahu_lon + 180.0) % 360.0,
        }
        expected_dasha = compute_all_10_parashari_nakshatra_dashas(
            70.0, 5.0, 10.0, base_map, 2451545.0, query_jd=2461350.0, is_day_birth=True
        )
        expected_nadi = compute_nadi_amsa_and_sudarshana_chakra(5.0, base_map, 2451545.0, query_jd=2461350.0)

        variants = [
            base_map,
            {k.title(): v for k, v in base_map.items()},
            {k.upper(): v for k, v in base_map.items()},
            {("Rahu" if k == "rahu" else k): v for k, v in base_map.items()},
            {(k.title() if k != "rahu" else "rahu"): v for k, v in base_map.items()},
            {
                "Surya": 10.0,
                "Chandra": 70.0,
                "Mangala": 60.0,
                "Budha": 90.0,
                "Guru": 120.0,
                "Shukra": 180.0,
                "Shani": 210.0,
                "True_Rahu": rahu_lon,
                "True_Ketu": (rahu_lon + 180.0) % 360.0,
            },
        ]
        for var_map in variants:
            actual_dasha = compute_all_10_parashari_nakshatra_dashas(
                70.0, 5.0, 10.0, var_map, 2451545.0, query_jd=2461350.0, is_day_birth=True
            )
            assert [(s.system_key, s.is_conditionally_eligible, s.eligibility_reason) for s in actual_dasha.systems] == [
                (s.system_key, s.is_conditionally_eligible, s.eligibility_reason) for s in expected_dasha.systems
            ]
            assert actual_dasha.consensus_ranking == expected_dasha.consensus_ranking
            actual_nadi = compute_nadi_amsa_and_sudarshana_chakra(5.0, var_map, 2451545.0, query_jd=2461350.0)
            assert actual_nadi.receipt_sha256 == expected_nadi.receipt_sha256

    with pytest.raises(ValueError, match="Missing required planet longitude"):
        compute_all_10_parashari_nakshatra_dashas(
            70.0, 5.0, 10.0, {"sun": 10.0, "moon": 70.0}, 2451545.0, query_jd=2461350.0, is_day_birth=True
        )

