"""Deterministic event solvers for the dark astronomy provider.

The routines in this module are callback-driven on purpose.  They provide the
numerical event-finding and atmospheric surface without registering a provider
or depending on any legacy ephemeris implementation.  Callers must supply
apparent coordinates in one documented frame and time scale.
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Callable, Literal, Sequence

import erfa


ScalarCallback = Callable[[float], float]
VectorCallback = Callable[[float], Sequence[float]]

EVENTS_VERSION = "0.2.0-dark"
SECONDS_PER_DAY = 86_400.0
SUN_RADIUS_KM = 695_700.0
MOON_RADIUS_KM = 1_737.4
EARTH_EQUATORIAL_RADIUS_KM = 6_378.1366


class EventSolverError(ValueError):
    """Raised when a requested numerical event cannot be solved safely."""


@dataclass(frozen=True)
class SolverPolicy:
    """Bounded numerical policy shared by all event searches."""

    sample_count: int = 97
    max_iterations: int = 80
    time_tolerance_days: float = 1e-9
    value_tolerance: float = 1e-12
    subdivision_depth: int = 3

    def __post_init__(self) -> None:
        if self.sample_count < 2:
            raise EventSolverError("sample_count must be at least 2")
        if not 1 <= self.max_iterations <= 256:
            raise EventSolverError("max_iterations must be between 1 and 256")
        if not math.isfinite(self.time_tolerance_days) or self.time_tolerance_days <= 0.0:
            raise EventSolverError("time_tolerance_days must be positive and finite")
        if not math.isfinite(self.value_tolerance) or self.value_tolerance < 0.0:
            raise EventSolverError("value_tolerance must be finite and non-negative")
        if not 0 <= self.subdivision_depth <= 12:
            raise EventSolverError("subdivision_depth must be between 0 and 12")


@dataclass(frozen=True)
class EventProvenance:
    """Stable, serializable description of how an event result was obtained."""

    method: str
    policy: SolverPolicy
    inputs: tuple[tuple[str, str], ...] = ()
    component: str = "ephemeris-oss.events"
    version: str = EVENTS_VERSION

    @classmethod
    def create(
        cls,
        method: str,
        policy: SolverPolicy,
        **inputs: object,
    ) -> EventProvenance:
        normalized = tuple(sorted((key, str(value)) for key, value in inputs.items()))
        return cls(method=method, policy=policy, inputs=normalized)

    def as_dict(self) -> dict[str, object]:
        return {
            "component": self.component,
            "version": self.version,
            "method": self.method,
            "sample_count": self.policy.sample_count,
            "max_iterations": self.policy.max_iterations,
            "time_tolerance_days": self.policy.time_tolerance_days,
            "value_tolerance": self.policy.value_tolerance,
            "subdivision_depth": self.policy.subdivision_depth,
            "inputs": dict(self.inputs),
        }


@dataclass(frozen=True)
class ScalarBracket:
    start_jd: float
    end_jd: float
    start_value: float
    end_value: float


@dataclass(frozen=True)
class ScalarRoot:
    jd: float
    residual: float
    iterations: int
    bracket: tuple[float, float]


@dataclass(frozen=True)
class AngularBracket:
    start_jd: float
    end_jd: float
    start_unwrapped_deg: float
    end_unwrapped_deg: float
    target_unwrapped_deg: float
    direction: Literal["direct", "retrograde"]


@dataclass(frozen=True)
class LongitudeCrossing:
    jd: float
    target_longitude_deg: float
    direction: Literal["direct", "retrograde"]
    residual_arcsec: float
    iterations: int
    bracket: tuple[float, float]
    provenance: EventProvenance


@dataclass(frozen=True)
class IngressEvent:
    jd: float
    boundary_longitude_deg: float
    direction: Literal["direct", "retrograde"]
    from_sector: int
    to_sector: int
    residual_arcsec: float
    provenance: EventProvenance


@dataclass(frozen=True)
class StationEvent:
    jd: float
    kind: Literal["direct", "retrograde"]
    speed_before_deg_per_day: float
    speed_after_deg_per_day: float
    residual_deg_per_day: float
    provenance: EventProvenance


@dataclass(frozen=True)
class OpticalAtmosphere:
    """Observed optical conditions accepted by ERFA's refraction model."""

    pressure_hpa: float
    temperature_c: float
    relative_humidity: float
    wavelength_micrometers: float

    def __post_init__(self) -> None:
        values = (
            self.pressure_hpa,
            self.temperature_c,
            self.relative_humidity,
            self.wavelength_micrometers,
        )
        if not all(math.isfinite(value) for value in values):
            raise EventSolverError("atmospheric inputs must be finite")
        if not 0.0 <= self.pressure_hpa <= 1_200.0:
            raise EventSolverError("pressure_hpa must be between 0 and 1200")
        if not -100.0 <= self.temperature_c <= 100.0:
            raise EventSolverError("temperature_c must be between -100 and 100")
        if not 0.0 <= self.relative_humidity <= 1.0:
            raise EventSolverError("relative_humidity must be between 0 and 1")
        if not 0.1 <= self.wavelength_micrometers <= 100.0:
            raise EventSolverError(
                "wavelength_micrometers must select ERFA's optical/IR range (0.1 to 100)"
            )


@dataclass(frozen=True)
class RefractionModel:
    coefficient_a_radians: float
    coefficient_b_radians: float
    atmosphere: OpticalAtmosphere
    provenance: EventProvenance


@dataclass(frozen=True)
class HorizonEvent:
    kind: Literal["rise", "set", "grazing"]
    jd: float
    apparent_altitude_deg: float


@dataclass(frozen=True)
class RiseSetTransitResult:
    outcome: Literal[
        "events",
        "rise_only",
        "set_only",
        "always_above",
        "always_below",
        "no_event",
    ]
    horizon_events: tuple[HorizonEvent, ...]
    transit_jd: float
    transit_altitude_deg: float
    provenance: EventProvenance


@dataclass(frozen=True)
class EclipseContact:
    label: str
    jd: float


@dataclass(frozen=True)
class EclipseResult:
    status: Literal["found", "no_event"]
    eclipse_type: Literal[
        "solar_partial",
        "solar_annular",
        "solar_total",
        "lunar_penumbral",
        "lunar_partial",
        "lunar_total",
        "none",
    ]
    maximum_jd: float
    separation_deg: float
    magnitude: float
    contacts: tuple[EclipseContact, ...]
    provenance: EventProvenance


def _finite(value: float, label: str) -> float:
    result = float(value)
    if not math.isfinite(result):
        raise EventSolverError(f"{label} callback returned a non-finite value")
    return result


def _validate_interval(start_jd: float, end_jd: float) -> tuple[float, float]:
    start = _finite(start_jd, "start_jd")
    end = _finite(end_jd, "end_jd")
    if end <= start:
        raise EventSolverError("end_jd must be greater than start_jd")
    return start, end


def _sample_grid(start_jd: float, end_jd: float, count: int) -> tuple[float, ...]:
    step = (end_jd - start_jd) / (count - 1)
    return tuple(start_jd + index * step for index in range(count))


def _effective_sample_count(policy: SolverPolicy) -> int:
    """Apply deterministic bounded subdivision between declared coarse samples."""

    return (policy.sample_count - 1) * (2**policy.subdivision_depth) + 1


def bracket_scalar_roots(
    function: ScalarCallback,
    start_jd: float,
    end_jd: float,
    *,
    policy: SolverPolicy = SolverPolicy(),
) -> tuple[ScalarBracket, ...]:
    """Return bounded sign-change brackets, including exact sampled roots."""

    start, end = _validate_interval(start_jd, end_jd)
    times = _sample_grid(start, end, _effective_sample_count(policy))
    values = tuple(_finite(function(jd), "scalar") for jd in times)
    brackets: list[ScalarBracket] = []
    for index, (left_jd, right_jd) in enumerate(zip(times, times[1:])):
        left_value = values[index]
        right_value = values[index + 1]
        left_zero = abs(left_value) <= policy.value_tolerance
        right_zero = abs(right_value) <= policy.value_tolerance
        if left_zero:
            brackets.append(ScalarBracket(left_jd, left_jd, left_value, left_value))
        if left_value * right_value < 0.0:
            brackets.append(ScalarBracket(left_jd, right_jd, left_value, right_value))
        if index == len(times) - 2 and right_zero:
            brackets.append(ScalarBracket(right_jd, right_jd, right_value, right_value))
    return _deduplicate_scalar_brackets(brackets, policy.time_tolerance_days)


def _deduplicate_scalar_brackets(
    brackets: Sequence[ScalarBracket], tolerance_days: float
) -> tuple[ScalarBracket, ...]:
    ordered = sorted(brackets, key=lambda item: (item.start_jd, item.end_jd))
    result: list[ScalarBracket] = []
    for bracket in ordered:
        center = (bracket.start_jd + bracket.end_jd) / 2.0
        if result:
            previous = result[-1]
            previous_center = (previous.start_jd + previous.end_jd) / 2.0
            if abs(center - previous_center) <= tolerance_days:
                if bracket.end_jd - bracket.start_jd < previous.end_jd - previous.start_jd:
                    result[-1] = bracket
                continue
        result.append(bracket)
    return tuple(result)


def refine_scalar_root(
    function: ScalarCallback,
    bracket: ScalarBracket,
    *,
    policy: SolverPolicy = SolverPolicy(),
) -> ScalarRoot:
    """Refine one validated scalar bracket by deterministic bisection."""

    left = bracket.start_jd
    right = bracket.end_jd
    f_left = _finite(function(left), "scalar")
    f_right = _finite(function(right), "scalar")
    if abs(f_left) <= policy.value_tolerance:
        return ScalarRoot(left, f_left, 0, (left, right))
    if abs(f_right) <= policy.value_tolerance:
        return ScalarRoot(right, f_right, 0, (left, right))
    if f_left * f_right > 0.0:
        raise EventSolverError("scalar bracket does not contain a sign change")

    for iteration in range(1, policy.max_iterations + 1):
        midpoint = (left + right) / 2.0
        f_midpoint = _finite(function(midpoint), "scalar")
        if (
            abs(f_midpoint) <= policy.value_tolerance
            or right - left <= policy.time_tolerance_days
        ):
            candidates = ((left, f_left), (midpoint, f_midpoint), (right, f_right))
            best_jd, best_residual = min(candidates, key=lambda item: abs(item[1]))
            return ScalarRoot(
                best_jd,
                best_residual,
                iteration,
                (bracket.start_jd, bracket.end_jd),
            )
        if f_left * f_midpoint <= 0.0:
            right = midpoint
            f_right = f_midpoint
        else:
            left = midpoint
            f_left = f_midpoint
    raise EventSolverError("scalar root refinement exceeded max_iterations")


def find_scalar_roots(
    function: ScalarCallback,
    start_jd: float,
    end_jd: float,
    *,
    policy: SolverPolicy = SolverPolicy(),
) -> tuple[ScalarRoot, ...]:
    brackets = bracket_scalar_roots(function, start_jd, end_jd, policy=policy)
    roots = tuple(refine_scalar_root(function, bracket, policy=policy) for bracket in brackets)
    return _deduplicate_roots(roots, policy.time_tolerance_days)


def _deduplicate_roots(
    roots: Sequence[ScalarRoot], tolerance_days: float
) -> tuple[ScalarRoot, ...]:
    result: list[ScalarRoot] = []
    for root in sorted(roots, key=lambda item: item.jd):
        if result and abs(root.jd - result[-1].jd) <= tolerance_days:
            if abs(root.residual) < abs(result[-1].residual):
                result[-1] = root
            continue
        result.append(root)
    return tuple(result)


def signed_angular_difference_degrees(angle_deg: float, reference_deg: float) -> float:
    """Shortest signed angular difference in the half-open range [-180, 180)."""

    angle = _finite(angle_deg, "angle")
    reference = _finite(reference_deg, "reference")
    return (angle - reference + 180.0) % 360.0 - 180.0


def _unwrap_near(angle_deg: float, reference_unwrapped_deg: float) -> float:
    angle = _finite(angle_deg, "longitude") % 360.0
    return angle + 360.0 * round((reference_unwrapped_deg - angle) / 360.0)


def _sample_unwrapped_angles(
    longitude_at_jd: ScalarCallback,
    start_jd: float,
    end_jd: float,
    policy: SolverPolicy,
) -> tuple[tuple[float, ...], tuple[float, ...]]:
    times = _sample_grid(start_jd, end_jd, _effective_sample_count(policy))
    raw = tuple(_finite(longitude_at_jd(jd), "longitude") % 360.0 for jd in times)
    unwrapped = [raw[0]]
    for previous_raw, current_raw in zip(raw, raw[1:]):
        delta = signed_angular_difference_degrees(current_raw, previous_raw)
        if abs(delta) >= 180.0 - 1e-12:
            raise EventSolverError(
                "angular samples are ambiguous by 180 degrees; increase sample_count"
            )
        unwrapped.append(unwrapped[-1] + delta)
    return times, tuple(unwrapped)


def bracket_angular_crossings(
    longitude_at_jd: ScalarCallback,
    start_jd: float,
    end_jd: float,
    target_longitude_deg: float,
    *,
    policy: SolverPolicy = SolverPolicy(),
) -> tuple[AngularBracket, ...]:
    """Bracket all crossings of one longitude without false roots at wrap."""

    start, end = _validate_interval(start_jd, end_jd)
    target = _finite(target_longitude_deg, "target_longitude") % 360.0
    times, unwrapped = _sample_unwrapped_angles(longitude_at_jd, start, end, policy)
    brackets: list[AngularBracket] = []
    seen: set[tuple[int, int]] = set()
    for index, (left, right) in enumerate(zip(unwrapped, unwrapped[1:])):
        if abs(right - left) <= policy.value_tolerance:
            continue
        low, high = sorted((left, right))
        first = math.ceil((low - target) / 360.0 - 1e-14)
        last = math.floor((high - target) / 360.0 + 1e-14)
        for revolution in range(first, last + 1):
            level = target + 360.0 * revolution
            if level < low - policy.value_tolerance or level > high + policy.value_tolerance:
                continue
            fraction = (level - left) / (right - left)
            estimated_jd = times[index] + fraction * (times[index + 1] - times[index])
            key = (round(estimated_jd / policy.time_tolerance_days), round(level * 1e9))
            if key in seen:
                continue
            seen.add(key)
            brackets.append(
                AngularBracket(
                    start_jd=times[index],
                    end_jd=times[index + 1],
                    start_unwrapped_deg=left,
                    end_unwrapped_deg=right,
                    target_unwrapped_deg=level,
                    direction="direct" if right > left else "retrograde",
                )
            )
    return tuple(brackets)


def _refine_angular_crossing(
    longitude_at_jd: ScalarCallback,
    bracket: AngularBracket,
    policy: SolverPolicy,
) -> ScalarRoot:
    left = bracket.start_jd
    right = bracket.end_jd
    target = bracket.target_unwrapped_deg
    f_left = bracket.start_unwrapped_deg - target
    f_right = bracket.end_unwrapped_deg - target
    if abs(f_left) <= policy.value_tolerance:
        return ScalarRoot(left, f_left, 0, (left, right))
    if abs(f_right) <= policy.value_tolerance:
        return ScalarRoot(right, f_right, 0, (left, right))
    if f_left * f_right > 0.0:
        raise EventSolverError("angular bracket does not contain the requested crossing")

    for iteration in range(1, policy.max_iterations + 1):
        midpoint = (left + right) / 2.0
        raw_midpoint = _finite(longitude_at_jd(midpoint), "longitude")
        f_midpoint = _unwrap_near(raw_midpoint, target) - target
        if (
            abs(f_midpoint) <= policy.value_tolerance
            or right - left <= policy.time_tolerance_days
        ):
            return ScalarRoot(midpoint, f_midpoint, iteration, (bracket.start_jd, bracket.end_jd))
        if f_left * f_midpoint <= 0.0:
            right = midpoint
            f_right = f_midpoint
        else:
            left = midpoint
            f_left = f_midpoint
    raise EventSolverError("angular crossing refinement exceeded max_iterations")


def solve_longitude_crossings(
    longitude_at_jd: ScalarCallback,
    start_jd: float,
    end_jd: float,
    target_longitude_deg: float,
    *,
    policy: SolverPolicy = SolverPolicy(),
    event_kind: str = "longitude_crossing",
) -> tuple[LongitudeCrossing, ...]:
    brackets = bracket_angular_crossings(
        longitude_at_jd,
        start_jd,
        end_jd,
        target_longitude_deg,
        policy=policy,
    )
    provenance = EventProvenance.create(
        "wrap-aware-angular-bisection",
        policy,
        event_kind=event_kind,
        target_longitude_deg=target_longitude_deg % 360.0,
    )
    results: list[LongitudeCrossing] = []
    for bracket in brackets:
        root = _refine_angular_crossing(longitude_at_jd, bracket, policy)
        results.append(
            LongitudeCrossing(
                jd=root.jd,
                target_longitude_deg=target_longitude_deg % 360.0,
                direction=bracket.direction,
                residual_arcsec=abs(root.residual) * 3_600.0,
                iterations=root.iterations,
                bracket=root.bracket,
                provenance=provenance,
            )
        )
    return tuple(results)


def solve_ingresses(
    longitude_at_jd: ScalarCallback,
    start_jd: float,
    end_jd: float,
    *,
    sector_size_deg: float = 30.0,
    policy: SolverPolicy = SolverPolicy(),
) -> tuple[IngressEvent, ...]:
    if not math.isfinite(sector_size_deg) or sector_size_deg <= 0.0:
        raise EventSolverError("sector_size_deg must be positive and finite")
    sector_count_float = 360.0 / sector_size_deg
    sector_count = round(sector_count_float)
    if not math.isclose(sector_count_float, sector_count, abs_tol=1e-12):
        raise EventSolverError("sector_size_deg must divide 360 exactly")

    all_crossings: list[LongitudeCrossing] = []
    for sector in range(sector_count):
        all_crossings.extend(
            solve_longitude_crossings(
                longitude_at_jd,
                start_jd,
                end_jd,
                sector * sector_size_deg,
                policy=policy,
                event_kind="ingress",
            )
        )
    provenance = EventProvenance.create(
        "wrap-aware-sector-boundary-bisection",
        policy,
        sector_size_deg=sector_size_deg,
    )
    events: list[IngressEvent] = []
    for crossing in sorted(all_crossings, key=lambda item: item.jd):
        boundary = round(crossing.target_longitude_deg / sector_size_deg) % sector_count
        if crossing.direction == "direct":
            from_sector = (boundary - 1) % sector_count
            to_sector = boundary
        else:
            from_sector = boundary
            to_sector = (boundary - 1) % sector_count
        events.append(
            IngressEvent(
                jd=crossing.jd,
                boundary_longitude_deg=crossing.target_longitude_deg,
                direction=crossing.direction,
                from_sector=from_sector,
                to_sector=to_sector,
                residual_arcsec=crossing.residual_arcsec,
                provenance=provenance,
            )
        )
    return tuple(events)


def solve_solar_returns(
    solar_longitude_at_jd: ScalarCallback,
    start_jd: float,
    end_jd: float,
    natal_longitude_deg: float,
    *,
    policy: SolverPolicy = SolverPolicy(),
) -> tuple[LongitudeCrossing, ...]:
    return tuple(
        crossing
        for crossing in solve_longitude_crossings(
            solar_longitude_at_jd,
            start_jd,
            end_jd,
            natal_longitude_deg,
            policy=policy,
            event_kind="solar_return",
        )
        if crossing.direction == "direct"
    )


def solve_stations(
    longitude_at_jd: ScalarCallback,
    start_jd: float,
    end_jd: float,
    *,
    angular_speed_at_jd: ScalarCallback | None = None,
    derivative_step_days: float = 1e-3,
    policy: SolverPolicy = SolverPolicy(),
) -> tuple[StationEvent, ...]:
    start, end = _validate_interval(start_jd, end_jd)
    if not math.isfinite(derivative_step_days) or derivative_step_days <= 0.0:
        raise EventSolverError("derivative_step_days must be positive and finite")

    if angular_speed_at_jd is None:
        def speed(jd: float) -> float:
            before = longitude_at_jd(jd - derivative_step_days)
            after = longitude_at_jd(jd + derivative_step_days)
            delta = signed_angular_difference_degrees(after, before)
            return delta / (2.0 * derivative_step_days)

        search_start = start + derivative_step_days
        search_end = end - derivative_step_days
        if search_end <= search_start:
            raise EventSolverError("station interval is too short for the derivative step")
        method = "central-difference-speed-bisection"
    else:
        speed = angular_speed_at_jd
        search_start = start
        search_end = end
        method = "provided-speed-bisection"

    roots = find_scalar_roots(speed, search_start, search_end, policy=policy)
    provenance = EventProvenance.create(
        method,
        policy,
        derivative_step_days=derivative_step_days,
    )
    events: list[StationEvent] = []
    probe = max(policy.time_tolerance_days * 8.0, derivative_step_days)
    for root in roots:
        before_jd = max(search_start, root.jd - probe)
        after_jd = min(search_end, root.jd + probe)
        before = _finite(speed(before_jd), "angular_speed")
        after = _finite(speed(after_jd), "angular_speed")
        if before == after:
            continue
        kind: Literal["direct", "retrograde"] = "retrograde" if before > after else "direct"
        events.append(
            StationEvent(
                jd=root.jd,
                kind=kind,
                speed_before_deg_per_day=before,
                speed_after_deg_per_day=after,
                residual_deg_per_day=abs(root.residual),
                provenance=provenance,
            )
        )
    return tuple(events)


def erfa_optical_refraction_model(atmosphere: OpticalAtmosphere) -> RefractionModel:
    coefficient_a, coefficient_b = erfa.refco(
        atmosphere.pressure_hpa,
        atmosphere.temperature_c,
        atmosphere.relative_humidity,
        atmosphere.wavelength_micrometers,
    )
    policy = SolverPolicy(sample_count=2, max_iterations=1)
    provenance = EventProvenance.create(
        "ERFA-eraRefco-A-tanZ-plus-B-tan3Z",
        policy,
        pressure_hpa=atmosphere.pressure_hpa,
        temperature_c=atmosphere.temperature_c,
        relative_humidity=atmosphere.relative_humidity,
        wavelength_micrometers=atmosphere.wavelength_micrometers,
        low_altitude_sine_floor=0.05,
    )
    return RefractionModel(float(coefficient_a), float(coefficient_b), atmosphere, provenance)


def refracted_altitude_degrees(geometric_altitude_deg: float, model: RefractionModel) -> float:
    """Apply atmospheric refraction correction to geometric altitude.

    For high elevations (altitude >= 15 deg), ERFA's two-coefficient expansion
    (A tan Z + B tan^3 Z) is used. For low and near-horizon elevations down
    through sunrise/sunset (altitude < 15 deg), the altitude dependence of
    Saemundsson (Sky and Telescope 72, 70, 1986) is scaled to a horizon
    refraction of 0.55988864426 deg (33.593') at 1013.25 hPa and 15 deg C.
    That horizon value is an empirical almanac convention:
    no publication derives it; it sits 0.41' below the USNO 34' convention
    (aa.usno.navy.mil/faq/RST_defs) and is kept because it reproduces widely
    used rise and set times.
    """

    altitude = _finite(geometric_altitude_deg, "geometric_altitude")
    if not -90.0 <= altitude <= 90.0:
        raise EventSolverError("geometric_altitude_deg must be between -90 and 90")
    if model.atmosphere.pressure_hpa <= 0.0:
        return altitude

    p = model.atmosphere.pressure_hpa
    t = model.atmosphere.temperature_c

    # Saemundsson (1986) altitude dependence, scaled to the horizon convention above:
    if altitude < 15.0:
        clamped_alt = max(altitude, -4.5)
        arg = clamped_alt + 10.3 / (clamped_alt + 5.11)
        r_arcmin = 1.02 / math.tan(math.radians(arg))
        r0_target = 0.55988864426 * (p / 1013.25) * (288.15 / (273.15 + t))
        arg0 = -0.55988864426 + 10.3 / (-0.55988864426 + 5.11)
        r_at_0 = (1.02 / math.tan(math.radians(arg0))) / 60.0
        scale = r0_target / r_at_0 if r_at_0 > 0 else 0.0
        correction = (r_arcmin / 60.0) * scale
        if altitude > 10.0:
            z = math.radians(90.0 - altitude)
            tan_z = math.tan(z)
            erfa_corr = math.degrees(
                (model.coefficient_a_radians + model.coefficient_b_radians * tan_z * tan_z) * tan_z
            )
            weight = (altitude - 10.0) / 5.0
            correction = (1.0 - weight) * correction + weight * erfa_corr
        return altitude + correction

    sine_elevation = math.sin(math.radians(altitude))
    cosine_elevation = math.cos(math.radians(altitude))
    tangent_zenith = cosine_elevation / sine_elevation
    correction = (
        model.coefficient_a_radians
        + model.coefficient_b_radians * tangent_zenith * tangent_zenith
    ) * tangent_zenith
    return altitude + math.degrees(correction)



def _golden_extremum(
    function: ScalarCallback,
    start_jd: float,
    end_jd: float,
    policy: SolverPolicy,
    *,
    maximize: bool,
) -> tuple[float, float]:
    left, right = _validate_interval(start_jd, end_jd)
    ratio = (math.sqrt(5.0) - 1.0) / 2.0
    x1 = right - ratio * (right - left)
    x2 = left + ratio * (right - left)
    f1 = _finite(function(x1), "extremum")
    f2 = _finite(function(x2), "extremum")
    if not maximize:
        f1 = -f1
        f2 = -f2
    for _ in range(policy.max_iterations):
        if right - left <= policy.time_tolerance_days:
            break
        if f1 < f2:
            left = x1
            x1 = x2
            f1 = f2
            x2 = left + ratio * (right - left)
            f2 = _finite(function(x2), "extremum")
            if not maximize:
                f2 = -f2
        else:
            right = x2
            x2 = x1
            f2 = f1
            x1 = right - ratio * (right - left)
            f1 = _finite(function(x1), "extremum")
            if not maximize:
                f1 = -f1
    jd = (left + right) / 2.0
    return jd, _finite(function(jd), "extremum")


def _sampled_extremum(
    function: ScalarCallback,
    start_jd: float,
    end_jd: float,
    policy: SolverPolicy,
    *,
    maximize: bool,
) -> tuple[float, float]:
    times = _sample_grid(start_jd, end_jd, _effective_sample_count(policy))
    values = tuple(_finite(function(jd), "extremum") for jd in times)
    best_index = (
        max(range(len(values)), key=values.__getitem__)
        if maximize
        else min(range(len(values)), key=values.__getitem__)
    )
    if best_index == 0 or best_index == len(times) - 1:
        return times[best_index], values[best_index]
    refined_jd, refined_value = _golden_extremum(
        function,
        times[best_index - 1],
        times[best_index + 1],
        policy,
        maximize=maximize,
    )
    sampled_value = values[best_index]
    if (maximize and sampled_value >= refined_value) or (
        not maximize and sampled_value <= refined_value
    ):
        return times[best_index], sampled_value
    return refined_jd, refined_value


def _refine_horizon_root(
    function: ScalarCallback, bracket: ScalarBracket, policy: SolverPolicy,
) -> ScalarRoot:
    """Illinois refinement keeps the horizon bracket without repeated bisection."""
    left, right = bracket.start_jd, bracket.end_jd
    f_left, f_right = bracket.start_value, bracket.end_value
    if f_left * f_right >= 0:
        raise EventSolverError("horizon bracket does not contain a sign change")
    weight_left, weight_right = f_left, f_right
    retained = ""
    for iteration in range(1, policy.max_iterations + 1):
        candidate = left + (right - left) * (-weight_left) / (weight_right - weight_left)
        if not left < candidate < right:
            candidate = (left + right) / 2
        value = _finite(function(candidate), "horizon")
        if abs(value) <= policy.value_tolerance or right - left <= policy.time_tolerance_days:
            jd, residual = min(((left, f_left), (candidate, value), (right, f_right)),
                               key=lambda item: abs(item[1]))
            return ScalarRoot(jd, residual, iteration, (bracket.start_jd, bracket.end_jd))
        if f_left * value < 0:
            right, f_right, weight_right = candidate, value, value
            weight_left = weight_left / 2 if retained == "left" else f_left
            retained = "left"
        else:
            left, f_left, weight_left = candidate, value, value
            weight_right = weight_right / 2 if retained == "right" else f_right
            retained = "right"
    raise EventSolverError("horizon root refinement exceeded max_iterations")


def solve_rise_set_transit(
    apparent_altitude_at_jd: ScalarCallback,
    start_jd: float,
    end_jd: float,
    *,
    horizon_altitude_deg: float = 0.0,
    policy: SolverPolicy = SolverPolicy(sample_count=145),
    refine_transit: bool = True,
) -> RiseSetTransitResult:
    """Solve apparent horizon crossings and the highest transit in an interval."""

    start, end = _validate_interval(start_jd, end_jd)
    horizon = _finite(horizon_altitude_deg, "horizon_altitude")

    def horizon_function(jd: float) -> float:
        return _finite(apparent_altitude_at_jd(jd), "apparent_altitude") - horizon

    sample_count = _effective_sample_count(policy)
    times = _sample_grid(start, end, sample_count)
    altitudes = tuple(_finite(apparent_altitude_at_jd(jd), "apparent_altitude") for jd in times)
    sampled = tuple(alt - horizon for alt in altitudes)

    # 1. Detect zero-crossing brackets directly from the single sampled grid
    brackets: list[ScalarBracket] = []
    roots: list[ScalarRoot] = []
    seen_times: set[int] = set()

    for i in range(len(times) - 1):
        t1, t2 = times[i], times[i + 1]
        f1, f2 = sampled[i], sampled[i + 1]
        if abs(f1) <= policy.value_tolerance:
            key = round(t1 / policy.time_tolerance_days)
            if key not in seen_times:
                seen_times.add(key)
                roots.append(ScalarRoot(t1, f1, 0, (t1, t2)))
        elif f1 * f2 < 0.0:
            brackets.append(ScalarBracket(t1, t2, f1, f2))
        elif abs(f2) <= policy.value_tolerance and i + 1 == len(times) - 1:
            key = round(t2 / policy.time_tolerance_days)
            if key not in seen_times:
                seen_times.add(key)
                roots.append(ScalarRoot(t2, f2, 0, (t1, t2)))

    # A short polar day/night or brief horizon dip/passage can fit between coarse samples
    # even when another interval already contains a crossing. Inspect sampled local extrema
    # whose adjacent intervals do not already have a sign change.
    n_samples = len(sampled)
    for k in range(n_samples):
        val_k = sampled[k]
        if abs(val_k) <= policy.value_tolerance:
            continue
        is_local_min = (k == 0 or val_k <= sampled[k - 1]) and (k == n_samples - 1 or val_k <= sampled[k + 1])
        is_local_max = (k == 0 or val_k >= sampled[k - 1]) and (k == n_samples - 1 or val_k >= sampled[k + 1])
        check_modes: list[bool] = []
        if val_k > 0.0 and is_local_min:
            check_modes.append(False)
        if val_k < 0.0 and is_local_max:
            check_modes.append(True)
        for maximize in check_modes:
            left = max(0, k - 1)
            right = min(n_samples - 1, k + 1)
            if left == right:
                continue
            extreme_jd, extreme_value = _golden_extremum(
                horizon_function, times[left], times[right], policy, maximize=maximize,
            )
            for edge in (left, right):
                if sampled[edge] * extreme_value < 0.0 and abs(extreme_value) > policy.value_tolerance:
                    pairs = sorted(((times[edge], sampled[edge]), (extreme_jd, extreme_value)))
                    brackets.append(ScalarBracket(pairs[0][0], pairs[1][0], pairs[0][1], pairs[1][1]))

    # Refine any brackets found
    for bracket in brackets:
        root = _refine_horizon_root(horizon_function, bracket, policy)
        key = round(root.jd / policy.time_tolerance_days)
        if key not in seen_times:
            seen_times.add(key)
            roots.append(root)

    # If no roots found and subdivision_depth > 0, check coarse intervals for hidden extrema
    if not roots and policy.subdivision_depth > 0:
        full_roots = find_scalar_roots(horizon_function, start, end, policy=policy)
        roots.extend(full_roots)

    deduped_roots = _deduplicate_roots(roots, policy.time_tolerance_days)

    probe = max(policy.time_tolerance_days * 8.0, (end - start) / sample_count / 100.0)
    events: list[HorizonEvent] = []
    for root in deduped_roots:
        before = horizon_function(max(start, root.jd - probe))
        after = horizon_function(min(end, root.jd + probe))
        if before < after:
            kind: Literal["rise", "set", "grazing"] = "rise"
        elif before > after:
            kind = "set"
        else:
            kind = "grazing"
        events.append(
            HorizonEvent(kind, root.jd, _finite(apparent_altitude_at_jd(root.jd), "altitude"))
        )

    # Grazing event check if no regular roots
    if not deduped_roots:
        min_idx = min(range(len(sampled)), key=lambda idx: abs(sampled[idx]))
        if min_idx == 0 or min_idx == len(times) - 1:
            grazing_jd = times[min_idx]
            grazing_residual = abs(sampled[min_idx])
        else:
            grazing_jd, grazing_val = _golden_extremum(
                lambda jd: abs(horizon_function(jd)),
                times[min_idx - 1],
                times[min_idx + 1],
                policy,
                maximize=False,
            )
            grazing_residual = abs(grazing_val)

        # Also fallback to full extremum search if coarse search missed it
        if grazing_residual > policy.value_tolerance and policy.subdivision_depth > 0:
            grazing_jd, grazing_residual = _sampled_extremum(
                lambda jd: abs(horizon_function(jd)),
                start,
                end,
                policy,
                maximize=False,
            )

        if grazing_residual <= policy.value_tolerance:
            events.append(
                HorizonEvent(
                    "grazing",
                    grazing_jd,
                    _finite(apparent_altitude_at_jd(grazing_jd), "altitude"),
                )
            )

    # 2. Upper transit localized from the sampled altitudes
    best_index = max(range(len(altitudes)), key=altitudes.__getitem__)
    if not refine_transit or best_index == 0 or best_index == len(times) - 1:
        transit_jd = times[best_index]
        transit_altitude = altitudes[best_index]
    else:
        refined_jd, refined_alt = _golden_extremum(
            apparent_altitude_at_jd,
            times[best_index - 1],
            times[best_index + 1],
            policy,
            maximize=True,
        )
        if altitudes[best_index] >= refined_alt:
            transit_jd = times[best_index]
            transit_altitude = altitudes[best_index]
        else:
            transit_jd = refined_jd
            transit_altitude = refined_alt

    has_rise = any(event.kind == "rise" for event in events)
    has_set = any(event.kind == "set" for event in events)
    if has_rise and has_set:
        outcome = "events"
    elif has_rise:
        outcome = "rise_only"
    elif has_set:
        outcome = "set_only"
    elif all(value > policy.value_tolerance for value in sampled):
        outcome = "always_above"
    elif all(value < -policy.value_tolerance for value in sampled):
        outcome = "always_below"
    else:
        outcome = "no_event"

    provenance = EventProvenance.create(
        "sample-bracket-illinois-plus-golden-transit" if refine_transit else "sample-bracket-illinois-horizon",
        policy,
        altitude_kind="topocentric_apparent",
        horizon_altitude_deg=horizon,
    )
    return RiseSetTransitResult(
        outcome=outcome,
        horizon_events=tuple(events),
        transit_jd=transit_jd,
        transit_altitude_deg=transit_altitude,
        provenance=provenance,
    )


def _vector(vector: Sequence[float], label: str) -> tuple[float, float, float]:
    if len(vector) != 3:
        raise EventSolverError(f"{label} callback must return exactly three components")
    result = tuple(_finite(component, label) for component in vector)
    norm = math.sqrt(sum(component * component for component in result))
    if norm <= 0.0:
        raise EventSolverError(f"{label} callback returned a zero-length vector")
    return result  # type: ignore[return-value]


def _norm(vector: Sequence[float]) -> float:
    return math.sqrt(sum(component * component for component in vector))


def _angular_separation_radians(first: Sequence[float], second: Sequence[float]) -> float:
    first_norm = _norm(first)
    second_norm = _norm(second)
    dot = sum(a * b for a, b in zip(first, second))
    cross = (
        first[1] * second[2] - first[2] * second[1],
        first[2] * second[0] - first[0] * second[2],
        first[0] * second[1] - first[1] * second[0],
    )
    return math.atan2(_norm(cross), dot) if first_norm * second_norm > 0.0 else math.nan


def _angular_radius_radians(radius_km: float, distance_km: float) -> float:
    if radius_km <= 0.0 or radius_km >= distance_km:
        raise EventSolverError("physical radius must be positive and smaller than distance")
    return math.asin(radius_km / distance_km)


def _contact_roots(
    margin: ScalarCallback,
    start_jd: float,
    maximum_jd: float,
    end_jd: float,
    policy: SolverPolicy,
    before_label: str,
    after_label: str,
) -> tuple[EclipseContact, ...]:
    contacts: list[EclipseContact] = []
    if maximum_jd > start_jd + policy.time_tolerance_days:
        before = find_scalar_roots(margin, start_jd, maximum_jd, policy=policy)
        if before:
            contacts.append(EclipseContact(before_label, before[-1].jd))
    if maximum_jd < end_jd - policy.time_tolerance_days:
        after = find_scalar_roots(margin, maximum_jd, end_jd, policy=policy)
        if after:
            contacts.append(EclipseContact(after_label, after[0].jd))
    return tuple(contacts)


def solve_solar_eclipse_candidate(
    sun_vector_at_jd: VectorCallback,
    moon_vector_at_jd: VectorCallback,
    start_jd: float,
    end_jd: float,
    *,
    sun_radius_km: float = SUN_RADIUS_KM,
    moon_radius_km: float = MOON_RADIUS_KM,
    apparent_vector_frame: str,
    policy: SolverPolicy = SolverPolicy(sample_count=193),
) -> EclipseResult:
    """Classify and solve geometric contacts for an apparent solar eclipse."""

    start, end = _validate_interval(start_jd, end_jd)
    if not apparent_vector_frame.strip():
        raise EventSolverError("apparent_vector_frame is required")

    def geometry(jd: float) -> tuple[float, float, float]:
        sun = _vector(sun_vector_at_jd(jd), "sun_vector")
        moon = _vector(moon_vector_at_jd(jd), "moon_vector")
        separation = _angular_separation_radians(sun, moon)
        sun_radius = _angular_radius_radians(sun_radius_km, _norm(sun))
        moon_radius = _angular_radius_radians(moon_radius_km, _norm(moon))
        return separation, sun_radius, moon_radius

    def outer_margin(jd: float) -> float:
        separation, sun_radius, moon_radius = geometry(jd)
        return sun_radius + moon_radius - separation

    maximum_jd, maximum_margin = _sampled_extremum(
        outer_margin, start, end, policy, maximize=True
    )
    separation, sun_radius, moon_radius = geometry(maximum_jd)
    provenance = EventProvenance.create(
        "apparent-disc-separation-and-contact-roots",
        policy,
        apparent_vector_frame=apparent_vector_frame,
        geometry="spherical-discs-no-local-terrain",
        moon_radius_km=moon_radius_km,
        sun_radius_km=sun_radius_km,
    )
    if maximum_margin < -policy.value_tolerance:
        return EclipseResult(
            "no_event", "none", maximum_jd, math.degrees(separation), 0.0, (), provenance
        )

    inner_margin = abs(moon_radius - sun_radius) - separation
    if inner_margin >= -policy.value_tolerance:
        eclipse_type: Literal["solar_annular", "solar_total"] = (
            "solar_total" if moon_radius >= sun_radius else "solar_annular"
        )
    else:
        eclipse_type = "solar_partial"  # type: ignore[assignment]

    contacts = list(
        _contact_roots(outer_margin, start, maximum_jd, end, policy, "C1", "C4")
    )
    if eclipse_type in ("solar_total", "solar_annular"):
        def internal_margin(jd: float) -> float:
            current_separation, current_sun_radius, current_moon_radius = geometry(jd)
            return abs(current_moon_radius - current_sun_radius) - current_separation

        contacts.extend(
            _contact_roots(internal_margin, start, maximum_jd, end, policy, "C2", "C3")
        )
    contacts.sort(key=lambda item: item.jd)
    magnitude = max(0.0, (moon_radius + sun_radius - separation) / (2.0 * sun_radius))
    return EclipseResult(
        "found",
        eclipse_type,
        maximum_jd,
        math.degrees(separation),
        magnitude,
        tuple(contacts),
        provenance,
    )


@dataclass(frozen=True)
class _LunarGeometry:
    separation_km: float
    penumbra_radius_km: float
    umbra_radius_km: float
    axial_distance_km: float


def _lunar_shadow_geometry(
    sun_vector: Sequence[float],
    moon_vector: Sequence[float],
    sun_radius_km: float,
    earth_radius_km: float,
) -> _LunarGeometry:
    sun_distance = _norm(sun_vector)
    anti_solar = tuple(-component / sun_distance for component in sun_vector)
    axial = sum(component * axis for component, axis in zip(moon_vector, anti_solar))
    transverse = tuple(
        component - axial * axis for component, axis in zip(moon_vector, anti_solar)
    )
    separation = _norm(transverse)
    if axial <= 0.0:
        return _LunarGeometry(separation, 0.0, 0.0, axial)
    umbra = earth_radius_km - axial * (sun_radius_km - earth_radius_km) / sun_distance
    penumbra = earth_radius_km + axial * (sun_radius_km + earth_radius_km) / sun_distance
    return _LunarGeometry(separation, penumbra, umbra, axial)


def solve_lunar_eclipse_candidate(
    sun_vector_at_jd: VectorCallback,
    moon_vector_at_jd: VectorCallback,
    start_jd: float,
    end_jd: float,
    *,
    sun_radius_km: float = SUN_RADIUS_KM,
    moon_radius_km: float = MOON_RADIUS_KM,
    earth_radius_km: float = EARTH_EQUATORIAL_RADIUS_KM,
    apparent_vector_frame: str,
    policy: SolverPolicy = SolverPolicy(sample_count=193),
) -> EclipseResult:
    """Classify geometric lunar shadow contacts from apparent geocentric vectors."""

    start, end = _validate_interval(start_jd, end_jd)
    if not apparent_vector_frame.strip():
        raise EventSolverError("apparent_vector_frame is required")

    def geometry(jd: float) -> _LunarGeometry:
        sun = _vector(sun_vector_at_jd(jd), "sun_vector")
        moon = _vector(moon_vector_at_jd(jd), "moon_vector")
        return _lunar_shadow_geometry(sun, moon, sun_radius_km, earth_radius_km)

    def penumbral_margin(jd: float) -> float:
        state = geometry(jd)
        if state.axial_distance_km <= 0.0:
            return -1e30
        return state.penumbra_radius_km + moon_radius_km - state.separation_km

    maximum_jd, maximum_margin = _sampled_extremum(
        penumbral_margin, start, end, policy, maximize=True
    )
    state = geometry(maximum_jd)
    provenance = EventProvenance.create(
        "conical-earth-shadow-and-contact-roots",
        policy,
        apparent_vector_frame=apparent_vector_frame,
        atmosphere_enlargement="not_applied",
        earth_radius_km=earth_radius_km,
        moon_radius_km=moon_radius_km,
        sun_radius_km=sun_radius_km,
    )
    separation_deg = math.degrees(math.atan2(state.separation_km, state.axial_distance_km))
    if maximum_margin < -policy.value_tolerance or state.axial_distance_km <= 0.0:
        return EclipseResult("no_event", "none", maximum_jd, separation_deg, 0.0, (), provenance)

    umbral_margin = state.umbra_radius_km + moon_radius_km - state.separation_km
    total_margin = state.umbra_radius_km - moon_radius_km - state.separation_km
    if total_margin >= -policy.value_tolerance:
        eclipse_type: Literal["lunar_penumbral", "lunar_partial", "lunar_total"] = (
            "lunar_total"
        )
    elif umbral_margin >= -policy.value_tolerance:
        eclipse_type = "lunar_partial"
    else:
        eclipse_type = "lunar_penumbral"

    contacts = list(
        _contact_roots(penumbral_margin, start, maximum_jd, end, policy, "P1", "P4")
    )
    if eclipse_type in ("lunar_partial", "lunar_total"):
        def umbral_contact_margin(jd: float) -> float:
            current = geometry(jd)
            return current.umbra_radius_km + moon_radius_km - current.separation_km

        contacts.extend(
            _contact_roots(umbral_contact_margin, start, maximum_jd, end, policy, "U1", "U4")
        )
    if eclipse_type == "lunar_total":
        def total_contact_margin(jd: float) -> float:
            current = geometry(jd)
            return current.umbra_radius_km - moon_radius_km - current.separation_km

        contacts.extend(
            _contact_roots(total_contact_margin, start, maximum_jd, end, policy, "U2", "U3")
        )
    contacts.sort(key=lambda item: item.jd)
    magnitude = max(
        0.0,
        (state.umbra_radius_km + moon_radius_km - state.separation_km)
        / (2.0 * moon_radius_km),
    )
    return EclipseResult(
        "found",
        eclipse_type,
        maximum_jd,
        separation_deg,
        magnitude,
        tuple(contacts),
        provenance,
    )
