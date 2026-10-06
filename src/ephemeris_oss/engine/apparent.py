"""Finite-distance apparent-place and terrestrial-observer calculations.

This module is an isolated, dark astronomy surface.  It does not select an
ephemeris, obtain Earth-orientation parameters, or register a production
provider.  Callers must supply barycentric ICRF states and versioned EOP data.

Algorithm references:

* IAU SOFA/ERFA ``eraLd`` and ``eraAb`` implement the relativistic light-
  deflection and aberration models described by Klioner (2003),
  https://doi.org/10.1086/367593.
* IERS Conventions (2010), Chapter 5, defines the ITRS/CIRS/GCRS rotation
  sequence used by ``eraPvtob`` and ``eraC2i06a``:
  https://iers-conventions.obspm.fr/content/chapter5/icc5.pdf.
* IAU SOFA is the normative source of the ERFA routines used here:
  https://www.iausofa.org/current-software.

Distances are kilometres, velocities are kilometres per TDB day for
barycentric states, terrestrial velocity is converted from metres per UT1
second to kilometres per day, and angles exposed to callers are degrees or
arcseconds as named.  All internal vectors use ICRF/GCRS-compatible axes.
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Callable

import erfa
import numpy as np

AU_KM = 149_597_870.7
C_KM_PER_SECOND = 299_792.458
C_KM_PER_DAY = C_KM_PER_SECOND * 86_400.0
SECONDS_PER_DAY = 86_400.0
# SOFA/ERFA eraLdsun uses a 1e-6 limiter (about five arcminutes at Earth),
# inside the solar limb. The former 6e-6 softened finite-distance rays already
# at C2-1475's 0.129-degree separation and moved Jupiter by 1.259 arcseconds.
SOLAR_DEFLECTION_LIMIT = 1.0e-6

Vector3 = tuple[float, float, float]


class ApparentPlaceError(RuntimeError):
    """Base error for invalid or unavailable apparent-place calculations."""


class ApparentPlaceConvergenceError(ApparentPlaceError):
    """Raised when iterative light-time does not meet its declared tolerance."""


@dataclass(frozen=True)
class BarycentricState:
    """Barycentric ICRF position and velocity at one TDB epoch."""

    position_km: Vector3
    velocity_km_per_day: Vector3
    source: str

    def __post_init__(self) -> None:
        _finite_vector(self.position_km, "position_km")
        velocity = _finite_vector(self.velocity_km_per_day, "velocity_km_per_day")
        if np.linalg.norm(velocity) >= C_KM_PER_DAY:
            raise ValueError("barycentric velocity must be slower than light")
        if not self.source.strip():
            raise ValueError("state source must be non-empty")


@dataclass(frozen=True)
class GeodeticObserver:
    """A WGS84 terrestrial site."""

    longitude_degrees_east: float
    latitude_degrees: float
    height_m: float

    def __post_init__(self) -> None:
        values = (
            self.longitude_degrees_east,
            self.latitude_degrees,
            self.height_m,
        )
        if not all(math.isfinite(value) for value in values):
            raise ValueError("observer coordinates must be finite")
        if not -180.0 <= self.longitude_degrees_east <= 180.0:
            raise ValueError("longitude must be in [-180, 180] degrees")
        if not -90.0 <= self.latitude_degrees <= 90.0:
            raise ValueError("latitude must be in [-90, 90] degrees")


@dataclass(frozen=True)
class EarthOrientation:
    """Versioned Earth orientation and two-part UTC/TT epochs."""

    utc: tuple[float, float]
    tt: tuple[float, float]
    dut1_seconds: float
    xp_arcsec: float
    yp_arcsec: float
    source: str
    version: str
    dx_mas: float = 0.0
    dy_mas: float = 0.0

    def __post_init__(self) -> None:
        values = (
            *self.utc,
            *self.tt,
            self.dut1_seconds,
            self.xp_arcsec,
            self.yp_arcsec,
            self.dx_mas,
            self.dy_mas,
        )
        if not all(math.isfinite(value) for value in values):
            raise ValueError("Earth-orientation values must be finite")
        if abs(self.dut1_seconds) >= 1.0:
            raise ValueError("DUT1 must be strictly within one second")
        if not self.source.strip() or not self.version.strip():
            raise ValueError("Earth-orientation source and version must be non-empty")


def celestial_to_intermediate_matrix(earth_orientation: EarthOrientation) -> np.ndarray:
    """Return the IAU 2006/2000A GCRS-to-CIRS matrix with observed CIP offsets.

    IERS ``dX`` and ``dY`` correct the modeled celestial intermediate pole.
    Applying them before recomputing the CIO locator prevents EOP data from
    being merely receipted without affecting the terrestrial observer state.
    """

    x, y, _modeled_s = erfa.xys06a(*earth_orientation.tt)
    x += earth_orientation.dx_mas * erfa.DMAS2R
    y += earth_orientation.dy_mas * erfa.DMAS2R
    corrected_s = erfa.s06(*earth_orientation.tt, x, y)
    return np.asarray(erfa.c2ixys(x, y, corrected_s), dtype=np.float64)


@dataclass(frozen=True)
class ApparentPlaceProvenance:
    """Reproducibility data for an apparent-place result."""

    ephemeris_source: str
    ephemeris_version: str
    light_time_model: str = "iterative-retarded-target/reception-observer"
    deflection_model: str = "ERFA-eraLd-solar-finite-distance"
    aberration_model: str = "ERFA-eraAb-special-relativistic"
    observer_model: str = "WGS84+IAU-2006/2000A"
    eop_source: str | None = None
    eop_version: str | None = None

    def __post_init__(self) -> None:
        if not self.ephemeris_source.strip() or not self.ephemeris_version.strip():
            raise ValueError("ephemeris source and version must be non-empty")
        if (self.eop_source is None) != (self.eop_version is None):
            raise ValueError("EOP source and version must be supplied together")


@dataclass(frozen=True)
class ApparentPlace:
    """Auditable apparent direction and finite-distance vector."""

    reception_tdb_jd: float
    emission_tdb_jd: float
    light_time_seconds: float
    light_time_iterations: int
    geometric_vector_km: Vector3
    geometric_distance_km: float
    astrometric_direction: Vector3
    deflected_direction: Vector3
    apparent_direction: Vector3
    apparent_vector_km: Vector3
    solar_deflection_applied: bool
    solar_deflector_tdb_jd: float | None
    provenance: ApparentPlaceProvenance


StateAtTdb = Callable[[float], BarycentricState]


def _finite_vector(value: Vector3 | np.ndarray, name: str) -> np.ndarray:
    vector = np.asarray(value, dtype=np.float64)
    if vector.shape != (3,) or not np.all(np.isfinite(vector)):
        raise ValueError(f"{name} must be a finite three-vector")
    return vector


def _unit(value: Vector3 | np.ndarray, name: str) -> tuple[float, np.ndarray]:
    vector = _finite_vector(value, name)
    magnitude = float(np.linalg.norm(vector))
    if magnitude == 0.0:
        raise ApparentPlaceError(f"{name} must be non-zero")
    return magnitude, vector / magnitude


def _as_tuple(value: np.ndarray) -> Vector3:
    return tuple(float(component) for component in value)  # type: ignore[return-value]


def terrestrial_observer_barycentric_state(
    *,
    earth_barycentric_state: BarycentricState,
    observer: GeodeticObserver,
    earth_orientation: EarthOrientation,
) -> BarycentricState:
    """Add a WGS84 site's GCRS position and rotational velocity to Earth.

    ``eraPvtob`` supplies the WGS84 station PV in CIRS.  The transpose of
    the corrected IAU ``X,Y,s`` matrix rotates both components into GCRS axes
    before they are added to the geocentre's barycentric ICRF state. No EOP
    values are synthesized.
    """

    ut1 = erfa.utcut1(*earth_orientation.utc, earth_orientation.dut1_seconds)
    theta = float(erfa.era00(*ut1))
    sp = float(erfa.sp00(*earth_orientation.tt))
    station_cirs_record = erfa.pvtob(
        math.radians(observer.longitude_degrees_east),
        math.radians(observer.latitude_degrees),
        observer.height_m,
        earth_orientation.xp_arcsec * erfa.DAS2R,
        earth_orientation.yp_arcsec * erfa.DAS2R,
        sp,
        theta,
    )
    station_cirs_position = np.asarray(station_cirs_record["p"], dtype=np.float64)
    station_cirs_velocity = np.asarray(station_cirs_record["v"], dtype=np.float64)
    cirs_to_gcrs = celestial_to_intermediate_matrix(earth_orientation).T
    station_position_km = cirs_to_gcrs @ station_cirs_position / 1_000.0
    station_velocity_km_per_day = (
        cirs_to_gcrs @ station_cirs_velocity * SECONDS_PER_DAY / 1_000.0
    )

    earth_position = _finite_vector(earth_barycentric_state.position_km, "Earth position")
    earth_velocity = _finite_vector(
        earth_barycentric_state.velocity_km_per_day, "Earth velocity"
    )
    return BarycentricState(
        position_km=_as_tuple(earth_position + station_position_km),
        velocity_km_per_day=_as_tuple(earth_velocity + station_velocity_km_per_day),
        source=(
            f"{earth_barycentric_state.source}; WGS84 site; "
            f"EOP {earth_orientation.source}@{earth_orientation.version}"
        ),
    )


def iterate_light_time(
    *,
    target_state_at_tdb: StateAtTdb,
    observer_barycentric_state: BarycentricState,
    reception_tdb_jd: float,
    tolerance_seconds: float = 1.0e-9,
    max_iterations: int = 12,
) -> tuple[float, BarycentricState, np.ndarray, float, int]:
    """Solve reception-to-emission light time for a finite-distance target."""

    if not math.isfinite(reception_tdb_jd):
        raise ValueError("reception_tdb_jd must be finite")
    if not math.isfinite(tolerance_seconds) or tolerance_seconds <= 0.0:
        raise ValueError("tolerance_seconds must be positive and finite")
    if max_iterations < 1:
        raise ValueError("max_iterations must be positive")

    observer_position = _finite_vector(
        observer_barycentric_state.position_km, "observer position"
    )
    emission_tdb_jd = reception_tdb_jd
    previous_light_time_days: float | None = None
    for iteration in range(1, max_iterations + 1):
        target_state = target_state_at_tdb(emission_tdb_jd)
        geometric_vector = _finite_vector(target_state.position_km, "target position") - observer_position
        distance_km, _direction = _unit(geometric_vector, "observer-to-target vector")
        light_time_days = distance_km / C_KM_PER_DAY
        next_emission_tdb_jd = reception_tdb_jd - light_time_days
        if previous_light_time_days is not None:
            delta_seconds = abs(light_time_days - previous_light_time_days) * SECONDS_PER_DAY
            if delta_seconds <= tolerance_seconds:
                final_state = target_state_at_tdb(next_emission_tdb_jd)
                final_vector = (
                    _finite_vector(final_state.position_km, "target position") - observer_position
                )
                final_distance, _ = _unit(final_vector, "observer-to-target vector")
                return (
                    next_emission_tdb_jd,
                    final_state,
                    final_vector,
                    final_distance / C_KM_PER_DAY,
                    iteration,
                )
        previous_light_time_days = light_time_days
        emission_tdb_jd = next_emission_tdb_jd

    raise ApparentPlaceConvergenceError(
        f"light-time iteration did not converge within {max_iterations} iterations"
    )


def apply_solar_gravitational_deflection(
    *,
    astrometric_direction: Vector3 | np.ndarray,
    target_barycentric_position_km: Vector3 | np.ndarray,
    observer_barycentric_position_km: Vector3 | np.ndarray,
    sun_state_at_tdb: StateAtTdb,
    reception_tdb_jd: float,
    geometric_distance_km: float,
) -> tuple[np.ndarray, float | None, bool]:
    """Apply ERFA's finite-distance solar monopole deflection.

    The Sun state is evaluated at an estimated closest-approach epoch along
    the finite observer-to-target ray, as recommended by ``eraLd``.  Solar
    self-deflection is inapplicable and returns the unmodified direction.
    """

    _, direction = _unit(astrometric_direction, "astrometric_direction")
    observer_position = _finite_vector(observer_barycentric_position_km, "observer position")
    target_position = _finite_vector(target_barycentric_position_km, "target position")
    sun_at_reception = sun_state_at_tdb(reception_tdb_jd)
    sun_reception_position = _finite_vector(sun_at_reception.position_km, "Sun position")

    projection_km = float(np.dot(sun_reception_position - observer_position, direction))
    ray_distance_km = min(max(projection_km, 0.0), geometric_distance_km)
    deflector_tdb_jd = reception_tdb_jd - ray_distance_km / C_KM_PER_DAY
    sun_position = _finite_vector(
        sun_state_at_tdb(deflector_tdb_jd).position_km, "Sun position"
    )
    sun_to_target = target_position - sun_position
    sun_to_observer = observer_position - sun_position
    target_separation = float(np.linalg.norm(sun_to_target))
    observer_distance_km = float(np.linalg.norm(sun_to_observer))
    if target_separation <= 1.0e-9:
        return direction, None, False
    if observer_distance_km == 0.0:
        raise ApparentPlaceError("observer cannot coincide with the solar deflector")

    _, body_to_target = _unit(sun_to_target, "Sun-to-target vector")
    _, body_to_observer = _unit(sun_to_observer, "Sun-to-observer vector")
    deflected = np.asarray(
        erfa.ld(
            1.0,
            direction,
            body_to_target,
            body_to_observer,
            observer_distance_km / AU_KM,
            SOLAR_DEFLECTION_LIMIT,
        ),
        dtype=np.float64,
    )
    _, normalized = _unit(deflected, "deflected direction")
    return normalized, deflector_tdb_jd, True


def apply_special_relativistic_aberration(
    *,
    natural_direction: Vector3 | np.ndarray,
    observer_barycentric_velocity_km_per_day: Vector3 | np.ndarray,
    sun_observer_distance_km: float,
) -> np.ndarray:
    """Apply rigorous ERFA aberration using observer barycentric velocity."""

    _, direction = _unit(natural_direction, "natural_direction")
    velocity = _finite_vector(
        observer_barycentric_velocity_km_per_day, "observer barycentric velocity"
    )
    beta = velocity / C_KM_PER_DAY
    beta_squared = float(np.dot(beta, beta))
    if beta_squared >= 1.0:
        raise ApparentPlaceError("observer barycentric velocity must be slower than light")
    if not math.isfinite(sun_observer_distance_km) or sun_observer_distance_km <= 0.0:
        raise ValueError("sun_observer_distance_km must be positive and finite")
    aberrated = np.asarray(
        erfa.ab(
            direction,
            beta,
            sun_observer_distance_km / AU_KM,
            math.sqrt(1.0 - beta_squared),
        ),
        dtype=np.float64,
    )
    _, normalized = _unit(aberrated, "aberrated direction")
    return normalized


def apparent_place(
    *,
    target_state_at_tdb: StateAtTdb,
    sun_state_at_tdb: StateAtTdb,
    observer_barycentric_state: BarycentricState,
    reception_tdb_jd: float,
    provenance: ApparentPlaceProvenance,
    apply_solar_deflection: bool = True,
    apply_aberration: bool = True,
    tolerance_seconds: float = 1.0e-9,
    max_iterations: int = 12,
) -> ApparentPlace:
    """Compute finite-distance astrometric, deflected, and apparent vectors."""

    emission_jd, target_state, geometric_vector, light_time_days, iterations = (
        iterate_light_time(
            target_state_at_tdb=target_state_at_tdb,
            observer_barycentric_state=observer_barycentric_state,
            reception_tdb_jd=reception_tdb_jd,
            tolerance_seconds=tolerance_seconds,
            max_iterations=max_iterations,
        )
    )
    geometric_distance, astrometric_direction = _unit(
        geometric_vector, "observer-to-target vector"
    )
    observer_position = _finite_vector(
        observer_barycentric_state.position_km, "observer position"
    )
    if apply_solar_deflection:
        deflected_direction, deflector_jd, deflection_applied = (
            apply_solar_gravitational_deflection(
                astrometric_direction=astrometric_direction,
                target_barycentric_position_km=target_state.position_km,
                observer_barycentric_position_km=observer_position,
                sun_state_at_tdb=sun_state_at_tdb,
                reception_tdb_jd=reception_tdb_jd,
                geometric_distance_km=geometric_distance,
            )
        )
    else:
        deflected_direction = astrometric_direction
        deflector_jd = None
        deflection_applied = False

    if apply_aberration:
        sun_position = _finite_vector(
            sun_state_at_tdb(reception_tdb_jd).position_km, "Sun position"
        )
        sun_observer_distance = float(np.linalg.norm(observer_position - sun_position))
        apparent_direction = apply_special_relativistic_aberration(
            natural_direction=deflected_direction,
            observer_barycentric_velocity_km_per_day=(
                observer_barycentric_state.velocity_km_per_day
            ),
            sun_observer_distance_km=sun_observer_distance,
        )
    else:
        apparent_direction = deflected_direction
    apparent_vector = apparent_direction * geometric_distance
    return ApparentPlace(
        reception_tdb_jd=float(reception_tdb_jd),
        emission_tdb_jd=float(emission_jd),
        light_time_seconds=float(light_time_days * SECONDS_PER_DAY),
        light_time_iterations=iterations,
        geometric_vector_km=_as_tuple(geometric_vector),
        geometric_distance_km=geometric_distance,
        astrometric_direction=_as_tuple(astrometric_direction),
        deflected_direction=_as_tuple(deflected_direction),
        apparent_direction=_as_tuple(apparent_direction),
        apparent_vector_km=_as_tuple(apparent_vector),
        solar_deflection_applied=deflection_applied,
        solar_deflector_tdb_jd=deflector_jd,
        provenance=provenance,
    )


def topocentric_apparent_place(
    *,
    target_state_at_tdb: StateAtTdb,
    sun_state_at_tdb: StateAtTdb,
    earth_barycentric_state: BarycentricState,
    observer: GeodeticObserver,
    earth_orientation: EarthOrientation,
    reception_tdb_jd: float,
    provenance: ApparentPlaceProvenance,
    apply_solar_deflection: bool = True,
    apply_aberration: bool = True,
    tolerance_seconds: float = 1.0e-9,
    max_iterations: int = 12,
) -> ApparentPlace:
    """Compute apparent place for a WGS84 terrestrial observer."""

    if provenance.eop_source != earth_orientation.source:
        raise ApparentPlaceError("provenance EOP source does not match Earth-orientation input")
    if provenance.eop_version != earth_orientation.version:
        raise ApparentPlaceError("provenance EOP version does not match Earth-orientation input")
    observer_state = terrestrial_observer_barycentric_state(
        earth_barycentric_state=earth_barycentric_state,
        observer=observer,
        earth_orientation=earth_orientation,
    )
    return apparent_place(
        target_state_at_tdb=target_state_at_tdb,
        sun_state_at_tdb=sun_state_at_tdb,
        observer_barycentric_state=observer_state,
        reception_tdb_jd=reception_tdb_jd,
        provenance=provenance,
        apply_solar_deflection=apply_solar_deflection,
        apply_aberration=apply_aberration,
        tolerance_seconds=tolerance_seconds,
        max_iterations=max_iterations,
    )
