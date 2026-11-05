from __future__ import annotations

import math

import erfa
import pytest

from ephemeris_oss.engine.events import (
    EventSolverError,
    OpticalAtmosphere,
    SolverPolicy,
    bracket_angular_crossings,
    bracket_scalar_roots,
    erfa_optical_refraction_model,
    find_scalar_roots,
    refracted_altitude_degrees,
    refine_scalar_root,
    signed_angular_difference_degrees,
    solve_ingresses,
    solve_longitude_crossings,
    solve_lunar_eclipse_candidate,
    solve_rise_set_transit,
    solve_solar_eclipse_candidate,
    solve_solar_returns,
    solve_stations,
)


FAST_POLICY = SolverPolicy(
    sample_count=65,
    max_iterations=80,
    time_tolerance_days=1e-10,
    value_tolerance=1e-11,
)


def test_scalar_bracket_and_refine_find_all_roots() -> None:
    def function(jd: float) -> float:
        return (jd - 1.0) * (jd - 2.0)

    brackets = bracket_scalar_roots(function, 0.0, 3.0, policy=FAST_POLICY)
    roots = tuple(refine_scalar_root(function, item, policy=FAST_POLICY) for item in brackets)

    assert [root.jd for root in roots] == pytest.approx([1.0, 2.0], abs=1e-9)
    assert max(abs(root.residual) for root in roots) <= 2.0 * FAST_POLICY.value_tolerance
    assert find_scalar_roots(lambda jd: jd * jd + 1.0, -1.0, 1.0, policy=FAST_POLICY) == ()


def test_bounded_subdivision_finds_two_roots_inside_one_coarse_cell() -> None:
    policy = SolverPolicy(
        sample_count=3,
        subdivision_depth=5,
        max_iterations=80,
        time_tolerance_days=1e-10,
        value_tolerance=1e-11,
    )
    roots = find_scalar_roots(
        lambda jd: (jd - 0.45) * (jd - 0.55),
        0.0,
        1.0,
        policy=policy,
    )

    assert [root.jd for root in roots] == pytest.approx([0.45, 0.55], abs=2e-9)


def test_scalar_solver_rejects_unbounded_or_invalid_requests() -> None:
    with pytest.raises(EventSolverError, match="end_jd"):
        bracket_scalar_roots(lambda jd: jd, 1.0, 1.0)
    with pytest.raises(EventSolverError, match="non-finite"):
        bracket_scalar_roots(lambda _jd: math.nan, 0.0, 1.0)


def test_angular_wrap_crossing_is_found_without_opposition_false_positive() -> None:
    def direct(jd: float) -> float:
        return (359.0 + 2.0 * jd) % 360.0

    crossing = solve_longitude_crossings(direct, 0.0, 1.0, 0.0, policy=FAST_POLICY)

    assert len(crossing) == 1
    assert crossing[0].jd == pytest.approx(0.5, abs=1e-9)
    assert crossing[0].direction == "direct"
    assert crossing[0].residual_arcsec < 1e-5

    def opposition(jd: float) -> float:
        return 179.0 + 2.0 * jd

    assert bracket_angular_crossings(opposition, 0.0, 1.0, 0.0, policy=FAST_POLICY) == ()
    assert signed_angular_difference_degrees(1.0, 359.0) == pytest.approx(2.0)


def test_retrograde_wrap_and_ingress_sector_direction() -> None:
    def retrograde(jd: float) -> float:
        return (1.0 - 2.0 * jd) % 360.0

    crossing = solve_longitude_crossings(retrograde, 0.0, 1.0, 0.0, policy=FAST_POLICY)
    ingresses = solve_ingresses(retrograde, 0.0, 1.0, policy=FAST_POLICY)

    assert len(crossing) == 1
    assert crossing[0].jd == pytest.approx(0.5, abs=1e-9)
    assert crossing[0].direction == "retrograde"
    assert len(ingresses) == 1
    assert ingresses[0].from_sector == 0
    assert ingresses[0].to_sector == 11


def test_solar_return_filters_to_direct_target_crossing() -> None:
    def longitude(jd: float) -> float:
        return (95.0 + 10.0 * jd) % 360.0

    returns = solve_solar_returns(longitude, 0.0, 2.0, 100.0, policy=FAST_POLICY)

    assert len(returns) == 1
    assert returns[0].jd == pytest.approx(0.5, abs=1e-9)
    assert returns[0].provenance.as_dict()["inputs"]["event_kind"] == "solar_return"


@pytest.mark.parametrize(
    ("longitude", "expected_kind"),
    [
        (lambda jd: 100.0 + (jd - 1.0) ** 2, "direct"),
        (lambda jd: 100.0 - (jd - 1.0) ** 2, "retrograde"),
    ],
)
def test_station_solver_classifies_motion_reversal(longitude, expected_kind: str) -> None:
    stations = solve_stations(
        longitude,
        0.0,
        2.0,
        derivative_step_days=1e-4,
        policy=FAST_POLICY,
    )

    assert len(stations) == 1
    assert stations[0].jd == pytest.approx(1.0, abs=2e-7)
    assert stations[0].kind == expected_kind
    assert stations[0].speed_before_deg_per_day * stations[0].speed_after_deg_per_day < 0.0


def test_erfa_optical_refraction_uses_explicit_conditions_and_stable_provenance() -> None:
    atmosphere = OpticalAtmosphere(1013.25, 15.0, 0.5, 0.55)
    model = erfa_optical_refraction_model(atmosphere)
    expected_a, expected_b = erfa.refco(1013.25, 15.0, 0.5, 0.55)

    assert model.coefficient_a_radians == pytest.approx(expected_a, abs=0.0)
    assert model.coefficient_b_radians == pytest.approx(expected_b, abs=0.0)
    assert refracted_altitude_degrees(10.0, model) > 10.0
    assert model.provenance.as_dict() == erfa_optical_refraction_model(
        atmosphere
    ).provenance.as_dict()

    vacuum = erfa_optical_refraction_model(OpticalAtmosphere(0.0, 15.0, 0.5, 0.55))
    assert refracted_altitude_degrees(0.0, vacuum) == pytest.approx(0.0, abs=1e-15)


def test_refraction_rejects_non_optical_or_invalid_inputs() -> None:
    with pytest.raises(EventSolverError, match="humidity"):
        OpticalAtmosphere(1013.25, 15.0, 1.1, 0.55)
    with pytest.raises(EventSolverError, match="optical"):
        OpticalAtmosphere(1013.25, 15.0, 0.5, 1_000.0)


def test_rise_set_and_transit_solver_finds_crossings_and_upper_transit() -> None:
    def altitude(jd: float) -> float:
        return 30.0 * math.sin(2.0 * math.pi * (jd - 0.25))

    result = solve_rise_set_transit(altitude, 0.0, 1.0, policy=FAST_POLICY)

    assert result.outcome == "events"
    assert [event.kind for event in result.horizon_events] == ["rise", "set"]
    assert [event.jd for event in result.horizon_events] == pytest.approx(
        [0.25, 0.75], abs=2e-8
    )
    assert result.transit_jd == pytest.approx(0.5, abs=2e-8)
    assert result.transit_altitude_deg == pytest.approx(30.0, abs=1e-8)
    assert result.provenance.as_dict()["inputs"]["altitude_kind"] == "topocentric_apparent"


def test_rise_set_solver_reports_polar_and_no_crossing_outcomes() -> None:
    above = solve_rise_set_transit(lambda _jd: 20.0, 0.0, 1.0, policy=FAST_POLICY)
    below = solve_rise_set_transit(lambda _jd: -20.0, 0.0, 1.0, policy=FAST_POLICY)
    grazing = solve_rise_set_transit(
        lambda jd: (jd - 0.5) ** 2,
        0.0,
        1.0,
        policy=FAST_POLICY,
    )

    assert above.outcome == "always_above"
    assert below.outcome == "always_below"
    assert grazing.outcome == "no_event"
    assert [event.kind for event in grazing.horizon_events] == ["grazing"]


def test_rise_set_finds_grazing_contact_between_coarse_samples() -> None:
    contact = 0.4375
    policy = SolverPolicy(
        sample_count=4,
        subdivision_depth=2,
        max_iterations=100,
        time_tolerance_days=1e-11,
        value_tolerance=1e-12,
    )
    result = solve_rise_set_transit(
        lambda jd: (jd - contact) ** 2,
        0.0,
        1.0,
        policy=policy,
    )

    assert [event.kind for event in result.horizon_events] == ["grazing"]
    assert result.horizon_events[0].jd == pytest.approx(contact, abs=2e-7)


AU_KM = 149_597_870.7


def _solar_vectors(moon_distance_km: float):
    def sun(_jd: float) -> tuple[float, float, float]:
        return (AU_KM, 0.0, 0.0)

    def moon(jd: float) -> tuple[float, float, float]:
        angle = 0.04 * (jd - 0.5)
        return (
            moon_distance_km * math.cos(angle),
            moon_distance_km * math.sin(angle),
            0.0,
        )

    return sun, moon


@pytest.mark.parametrize(
    ("moon_distance_km", "expected_type"),
    [(360_000.0, "solar_total"), (410_000.0, "solar_annular")],
)
def test_solar_eclipse_geometry_classifies_central_events_and_contacts(
    moon_distance_km: float,
    expected_type: str,
) -> None:
    sun, moon = _solar_vectors(moon_distance_km)
    result = solve_solar_eclipse_candidate(
        sun,
        moon,
        0.0,
        1.0,
        apparent_vector_frame="GCRS apparent geocentric",
        policy=FAST_POLICY,
    )

    assert result.status == "found"
    assert result.eclipse_type == expected_type
    assert result.maximum_jd == pytest.approx(0.5, abs=2e-7)
    assert result.separation_deg < 1e-7
    assert [contact.label for contact in result.contacts] == ["C1", "C2", "C3", "C4"]
    assert list(result.contacts) == sorted(result.contacts, key=lambda item: item.jd)
    assert result.contacts[1].jd < result.maximum_jd < result.contacts[2].jd


def test_solar_eclipse_geometry_returns_explicit_no_event() -> None:
    result = solve_solar_eclipse_candidate(
        lambda _jd: (AU_KM, 0.0, 0.0),
        lambda _jd: (0.0, 384_400.0, 0.0),
        0.0,
        1.0,
        apparent_vector_frame="GCRS apparent geocentric",
        policy=FAST_POLICY,
    )

    assert result.status == "no_event"
    assert result.eclipse_type == "none"
    assert result.contacts == ()


def _lunar_vectors():
    def sun(_jd: float) -> tuple[float, float, float]:
        return (AU_KM, 0.0, 0.0)

    def moon(jd: float) -> tuple[float, float, float]:
        return (-384_400.0, 20_000.0 * (jd - 0.5), 0.0)

    return sun, moon


def test_lunar_eclipse_geometry_classifies_total_shadow_and_contacts() -> None:
    sun, moon = _lunar_vectors()
    result = solve_lunar_eclipse_candidate(
        sun,
        moon,
        0.0,
        1.0,
        apparent_vector_frame="GCRS apparent geocentric",
        policy=FAST_POLICY,
    )

    assert result.status == "found"
    assert result.eclipse_type == "lunar_total"
    assert result.maximum_jd == pytest.approx(0.5, abs=2e-7)
    assert [contact.label for contact in result.contacts] == [
        "P1",
        "U1",
        "U2",
        "U3",
        "U4",
        "P4",
    ]
    assert result.contacts[2].jd < result.maximum_jd < result.contacts[3].jd
    assert result.provenance.as_dict()["inputs"]["atmosphere_enlargement"] == "not_applied"


def test_lunar_eclipse_geometry_requires_moon_behind_earth() -> None:
    result = solve_lunar_eclipse_candidate(
        lambda _jd: (AU_KM, 0.0, 0.0),
        lambda _jd: (384_400.0, 0.0, 0.0),
        0.0,
        1.0,
        apparent_vector_frame="GCRS apparent geocentric",
        policy=FAST_POLICY,
    )

    assert result.status == "no_event"
    assert result.eclipse_type == "none"


def test_eclipse_solver_requires_explicit_apparent_frame() -> None:
    sun, moon = _solar_vectors(360_000.0)
    with pytest.raises(EventSolverError, match="frame"):
        solve_solar_eclipse_candidate(
            sun,
            moon,
            0.0,
            1.0,
            apparent_vector_frame="",
            policy=FAST_POLICY,
        )
