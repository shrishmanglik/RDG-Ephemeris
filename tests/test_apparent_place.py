from __future__ import annotations

import math

import erfa
import numpy as np
import pytest

from ephemeris_oss.engine.apparent import (
    AU_KM,
    C_KM_PER_DAY,
    SECONDS_PER_DAY,
    SOLAR_DEFLECTION_LIMIT,
    ApparentPlaceConvergenceError,
    ApparentPlaceError,
    ApparentPlaceProvenance,
    BarycentricState,
    EarthOrientation,
    GeodeticObserver,
    apparent_place,
    apply_solar_gravitational_deflection,
    apply_special_relativistic_aberration,
    bennett_saemundsson_refraction_deg,
    iterate_light_time,
    terrestrial_observer_barycentric_state,
    topocentric_apparent_place,
    celestial_to_intermediate_matrix,
)


def state(
    position: tuple[float, float, float],
    velocity: tuple[float, float, float] = (0.0, 0.0, 0.0),
    source: str = "synthetic",
) -> BarycentricState:
    return BarycentricState(position, velocity, source)


def fixed_state(value: BarycentricState):
    return lambda _tdb_jd: value


def eop() -> EarthOrientation:
    utc = tuple(float(value) for value in erfa.dtf2d("UTC", 2026, 7, 22, 12, 0, 0.0))
    tai = erfa.utctai(*utc)
    tt = tuple(float(value) for value in erfa.taitt(*tai))
    return EarthOrientation(
        utc=utc,
        tt=tt,
        dut1_seconds=0.123456,
        xp_arcsec=0.071,
        yp_arcsec=0.312,
        source="IERS-test-fixture",
        version="fixture-2026-07-22",
        dx_mas=-0.066,
        dy_mas=0.031,
    )


def provenance(*, with_eop: bool = False) -> ApparentPlaceProvenance:
    return ApparentPlaceProvenance(
        ephemeris_source="synthetic-JPL-state",
        ephemeris_version="test-1",
        eop_source="IERS-test-fixture" if with_eop else None,
        eop_version="fixture-2026-07-22" if with_eop else None,
    )


def test_stationary_one_au_light_time_is_exact() -> None:
    observer = state((0.0, 0.0, 0.0))
    emission_jd, target, vector, light_time_days, iterations = iterate_light_time(
        target_state_at_tdb=fixed_state(state((AU_KM, 0.0, 0.0))),
        observer_barycentric_state=observer,
        reception_tdb_jd=2_460_000.5,
    )

    expected_days = AU_KM / C_KM_PER_DAY
    assert emission_jd == pytest.approx(2_460_000.5 - expected_days, abs=1e-14)
    assert target.position_km == (AU_KM, 0.0, 0.0)
    assert vector == pytest.approx((AU_KM, 0.0, 0.0), abs=0.0)
    assert light_time_days * SECONDS_PER_DAY == pytest.approx(
        AU_KM / 299_792.458, abs=1e-12
    )
    assert iterations == 2


def test_moving_target_light_time_matches_analytic_solution() -> None:
    reception_jd = 2_460_000.5
    reception_distance_km = 80_000_000.0
    radial_velocity_km_per_day = 750_000.0

    def moving_target(tdb_jd: float) -> BarycentricState:
        elapsed = tdb_jd - reception_jd
        return state(
            (reception_distance_km + radial_velocity_km_per_day * elapsed, 0.0, 0.0),
            (radial_velocity_km_per_day, 0.0, 0.0),
        )

    emission_jd, _target, _vector, light_time_days, _iterations = iterate_light_time(
        target_state_at_tdb=moving_target,
        observer_barycentric_state=state((0.0, 0.0, 0.0)),
        reception_tdb_jd=reception_jd,
    )
    expected_days = reception_distance_km / (C_KM_PER_DAY + radial_velocity_km_per_day)
    assert light_time_days == pytest.approx(expected_days, abs=2e-13)
    assert emission_jd == pytest.approx(reception_jd - expected_days, abs=1e-13)


def test_light_time_fails_closed_without_convergence() -> None:
    with pytest.raises(ApparentPlaceConvergenceError, match="did not converge"):
        iterate_light_time(
            target_state_at_tdb=fixed_state(state((AU_KM, 0.0, 0.0))),
            observer_barycentric_state=state((0.0, 0.0, 0.0)),
            reception_tdb_jd=2_460_000.5,
            max_iterations=1,
        )


def test_finite_distance_solar_deflection_matches_erfa_ld_identity() -> None:
    observer = np.asarray((AU_KM, 0.0, 0.0))
    target = np.asarray((AU_KM, 40_000_000.0, 12_000_000.0))
    sun = state((0.0, 0.0, 0.0))
    geometric = target - observer
    distance = float(np.linalg.norm(geometric))
    astrometric = geometric / distance

    actual, deflector_jd, applied = apply_solar_gravitational_deflection(
        astrometric_direction=astrometric,
        target_barycentric_position_km=target,
        observer_barycentric_position_km=observer,
        sun_state_at_tdb=fixed_state(sun),
        reception_tdb_jd=2_460_000.5,
        geometric_distance_km=distance,
    )
    expected = erfa.ld(
        1.0,
        astrometric,
        target / np.linalg.norm(target),
        observer / np.linalg.norm(observer),
        1.0,
        SOLAR_DEFLECTION_LIMIT,
    )
    expected /= np.linalg.norm(expected)
    np.testing.assert_allclose(actual, expected, atol=2e-16, rtol=0.0)
    assert applied is True
    assert deflector_jd is not None


def test_special_relativistic_aberration_matches_erfa_ab_identity() -> None:
    direction = np.asarray((0.3, -0.4, 0.8660254037844386))
    direction /= np.linalg.norm(direction)
    velocity = np.asarray((2_200_000.0, 1_350_000.0, -75_000.0))
    beta = velocity / C_KM_PER_DAY
    expected = erfa.ab(direction, beta, 1.012, math.sqrt(1.0 - np.dot(beta, beta)))
    expected /= np.linalg.norm(expected)

    actual = apply_special_relativistic_aberration(
        natural_direction=direction,
        observer_barycentric_velocity_km_per_day=velocity,
        sun_observer_distance_km=1.012 * AU_KM,
    )
    np.testing.assert_allclose(actual, expected, atol=2e-16, rtol=0.0)
    assert np.linalg.norm(actual) == pytest.approx(1.0, abs=2e-16)


def test_wgs84_observer_state_matches_erfa_orientation_chain() -> None:
    orientation = eop()
    site = GeodeticObserver(
        longitude_degrees_east=77.209,
        latitude_degrees=28.6139,
        height_m=216.0,
    )
    earth = state(
        (12_000_000.0, -100_000_000.0, -43_000_000.0),
        (2_400_000.0, 210_000.0, 91_000.0),
        "synthetic Earth",
    )
    actual = terrestrial_observer_barycentric_state(
        earth_barycentric_state=earth,
        observer=site,
        earth_orientation=orientation,
    )

    ut1 = erfa.utcut1(*orientation.utc, orientation.dut1_seconds)
    station_cirs = erfa.pvtob(
        math.radians(site.longitude_degrees_east),
        math.radians(site.latitude_degrees),
        site.height_m,
        orientation.xp_arcsec * erfa.DAS2R,
        orientation.yp_arcsec * erfa.DAS2R,
        erfa.sp00(*orientation.tt),
        erfa.era00(*ut1),
    )
    x, y, _s = erfa.xys06a(*orientation.tt)
    x += orientation.dx_mas * erfa.DMAS2R
    y += orientation.dy_mas * erfa.DMAS2R
    cirs_to_gcrs = erfa.c2ixys(x, y, erfa.s06(*orientation.tt, x, y)).T
    expected_position = (
        np.asarray(earth.position_km) + cirs_to_gcrs @ station_cirs["p"] / 1_000.0
    )
    expected_velocity = (
        np.asarray(earth.velocity_km_per_day)
        + cirs_to_gcrs @ station_cirs["v"] * SECONDS_PER_DAY / 1_000.0
    )
    np.testing.assert_allclose(actual.position_km, expected_position, atol=2e-9, rtol=0.0)
    np.testing.assert_allclose(actual.velocity_km_per_day, expected_velocity, atol=2e-9, rtol=0.0)
    station_offset = np.asarray(actual.position_km) - np.asarray(earth.position_km)
    station_speed = np.linalg.norm(
        np.asarray(actual.velocity_km_per_day) - np.asarray(earth.velocity_km_per_day)
    )
    assert 6_350.0 < np.linalg.norm(station_offset) < 6_390.0
    assert 20_000.0 < station_speed < 41_000.0


def test_observed_cip_offsets_are_applied_to_intermediate_matrix() -> None:
    orientation = eop()
    corrected = celestial_to_intermediate_matrix(orientation)
    modeled = np.asarray(erfa.c2i06a(*orientation.tt), dtype=np.float64)

    assert not np.array_equal(corrected, modeled)
    assert np.max(np.abs(corrected - modeled)) > 1e-11
    np.testing.assert_allclose(corrected @ corrected.T, np.identity(3), atol=5e-16)


def test_apparent_place_preserves_range_and_reports_each_stage() -> None:
    observer = state(
        (AU_KM, 0.0, 0.0),
        (0.0, 2_570_000.0, 0.0),
        "synthetic observer",
    )
    result = apparent_place(
        target_state_at_tdb=fixed_state(state((AU_KM + 384_400.0, 12_000.0, 5_000.0))),
        sun_state_at_tdb=fixed_state(state((0.0, 0.0, 0.0), source="synthetic Sun")),
        observer_barycentric_state=observer,
        reception_tdb_jd=2_460_000.5,
        provenance=provenance(),
    )

    assert result.light_time_seconds > 1.0
    assert result.light_time_iterations == 2
    assert result.solar_deflection_applied is True
    assert np.linalg.norm(result.astrometric_direction) == pytest.approx(1.0, abs=2e-16)
    assert np.linalg.norm(result.deflected_direction) == pytest.approx(1.0, abs=2e-16)
    assert np.linalg.norm(result.apparent_direction) == pytest.approx(1.0, abs=2e-16)
    assert np.linalg.norm(result.apparent_vector_km) == pytest.approx(
        result.geometric_distance_km, abs=1e-9
    )
    assert result.astrometric_direction != result.apparent_direction


def test_topocentric_apparent_place_uses_site_position_and_rotation() -> None:
    orientation = eop()
    earth = state(
        (AU_KM, 0.0, 0.0),
        (0.0, 2_570_000.0, 0.0),
        "synthetic Earth",
    )
    site = GeodeticObserver(-79.3832, 43.6532, 76.0)
    target = fixed_state(state((AU_KM + 384_400.0, 50_000.0, 25_000.0)))
    sun = fixed_state(state((0.0, 0.0, 0.0), source="synthetic Sun"))
    observer_state = terrestrial_observer_barycentric_state(
        earth_barycentric_state=earth,
        observer=site,
        earth_orientation=orientation,
    )
    expected = apparent_place(
        target_state_at_tdb=target,
        sun_state_at_tdb=sun,
        observer_barycentric_state=observer_state,
        reception_tdb_jd=2_460_000.5,
        provenance=provenance(with_eop=True),
        apply_solar_deflection=False,
    )
    actual = topocentric_apparent_place(
        target_state_at_tdb=target,
        sun_state_at_tdb=sun,
        earth_barycentric_state=earth,
        observer=site,
        earth_orientation=orientation,
        reception_tdb_jd=2_460_000.5,
        provenance=provenance(with_eop=True),
        apply_solar_deflection=False,
    )
    assert actual == expected

    geocentric = apparent_place(
        target_state_at_tdb=target,
        sun_state_at_tdb=sun,
        observer_barycentric_state=earth,
        reception_tdb_jd=2_460_000.5,
        provenance=provenance(),
        apply_solar_deflection=False,
    )
    angular_difference = math.acos(
        float(np.dot(actual.apparent_direction, geocentric.apparent_direction))
    )
    assert angular_difference > math.radians(0.5)


def test_topocentric_calculation_fails_closed_on_eop_provenance_mismatch() -> None:
    bad_provenance = ApparentPlaceProvenance(
        ephemeris_source="synthetic",
        ephemeris_version="1",
        eop_source="wrong",
        eop_version="wrong",
    )
    with pytest.raises(ApparentPlaceError, match="provenance EOP source"):
        topocentric_apparent_place(
            target_state_at_tdb=fixed_state(state((AU_KM + 1_000_000.0, 0.0, 0.0))),
            sun_state_at_tdb=fixed_state(state((0.0, 0.0, 0.0))),
            earth_barycentric_state=state((AU_KM, 0.0, 0.0)),
            observer=GeodeticObserver(0.0, 0.0, 0.0),
            earth_orientation=eop(),
            reception_tdb_jd=2_460_000.5,
            provenance=bad_provenance,
        )


@pytest.mark.parametrize(
    "observer",
    [
        GeodeticObserver(0.0, 90.0, 0.0),
        GeodeticObserver(180.0, -90.0, -400.0),
        GeodeticObserver(-180.0, 0.0, 8_848.86),
    ],
)
def test_wgs84_observer_boundaries_remain_finite(observer: GeodeticObserver) -> None:
    result = terrestrial_observer_barycentric_state(
        earth_barycentric_state=state((AU_KM, 0.0, 0.0)),
        observer=observer,
        earth_orientation=eop(),
    )
    assert np.all(np.isfinite(result.position_km))
    assert np.all(np.isfinite(result.velocity_km_per_day))


def test_solar_photosphere_occultation_guard_flags_occulted_by_sun() -> None:
    observer = state((AU_KM, 0.0, 0.0), (0.0, 2_570_000.0, 0.0), "synthetic Earth")
    sun = fixed_state(state((0.0, 0.0, 0.0), source="synthetic Sun"))

    # Case 1: Target behind the Sun within solar photosphere radius (impact parameter 200,000 km < 695,700 km)
    occulted_target = fixed_state(state((-AU_KM, 200_000.0, 0.0), source="behind Sun"))
    res_occulted = apparent_place(
        target_state_at_tdb=occulted_target,
        sun_state_at_tdb=sun,
        observer_barycentric_state=observer,
        reception_tdb_jd=2_460_000.5,
        provenance=provenance(),
    )
    assert res_occulted.occulted_by_sun is True
    assert res_occulted.solar_deflection_applied is False
    np.testing.assert_allclose(
        res_occulted.deflected_direction, res_occulted.astrometric_direction, atol=1e-15
    )

    # Case 2: Exact antiparallel superior conjunction (1 + e.Q == 0 < 1e-9)
    antiparallel_target = fixed_state(state((-AU_KM, 0.0, 0.0), source="antiparallel"))
    res_anti = apparent_place(
        target_state_at_tdb=antiparallel_target,
        sun_state_at_tdb=sun,
        observer_barycentric_state=observer,
        reception_tdb_jd=2_460_000.5,
        provenance=provenance(),
    )
    assert res_anti.occulted_by_sun is True
    assert res_anti.solar_deflection_applied is False

    # Case 3: Inferior conjunction (target in front of the Sun) is NOT occulted
    inferior_target = fixed_state(state((0.5 * AU_KM, 100_000.0, 0.0), source="in front of Sun"))
    res_inferior = apparent_place(
        target_state_at_tdb=inferior_target,
        sun_state_at_tdb=sun,
        observer_barycentric_state=observer,
        reception_tdb_jd=2_460_000.5,
        provenance=provenance(),
    )
    assert res_inferior.occulted_by_sun is False
    assert res_inferior.solar_deflection_applied is True


def test_bennett_saemundsson_refraction_deg() -> None:
    # Horizon (a0 = 0.0 deg) at standard P = 1010 hPa, T = 10 C -> 28.98 arcmin (~0.483 deg)
    ref_horizon = bennett_saemundsson_refraction_deg(0.0, 1010.0, 10.0)
    expected_arcmin = 1.02 / math.tan(math.radians(0.0 + 10.3 / 5.11))
    assert ref_horizon == pytest.approx(expected_arcmin / 60.0, rel=1e-12)
    assert 0.45 < ref_horizon < 0.60

    # At 45 deg altitude, refraction is ~1 arcmin (~0.0169 deg)
    ref_45 = bennett_saemundsson_refraction_deg(45.0, 1010.0, 10.0)
    assert 0.015 < ref_45 < 0.020

    # Below -1.0 deg or non-positive pressure returns 0.0
    assert bennett_saemundsson_refraction_deg(-2.0, 1010.0, 10.0) == 0.0
    assert bennett_saemundsson_refraction_deg(10.0, 0.0, 10.0) == 0.0

