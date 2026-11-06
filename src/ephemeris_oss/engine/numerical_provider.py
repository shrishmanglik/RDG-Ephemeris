"""Direct JPL SPK evaluation with ERFA IAU 2006 frame transformations.

This provider is deliberately dark. It computes geometric and apparent states
without importing or calling the legacy runtime and fails closed for every
correction or Jyotish convention that has not yet been independently built.
"""

from __future__ import annotations

import math
import threading
from collections import OrderedDict, deque
from copy import deepcopy
from dataclasses import asdict, dataclass
from datetime import date, datetime, timedelta, timezone
from functools import lru_cache
from typing import Any, Callable, Mapping, Sequence

import erfa
import numpy as np
from jplephem.spk import SPK

from .._version import __version__

from .contracts import (
    AstronomyDataUnavailable,
    AstronomyProvider,
    CalculationSettings,
    DatasetVersions,
    Observer,
    ProviderIdentity,
)
from .apparent import (
    ApparentPlaceProvenance,
    BarycentricState,
    EarthOrientation,
    GeodeticObserver,
    apparent_place,
    terrestrial_observer_barycentric_state,
)
from .conventions import (
    AYANAMSA_CATALOG_VERSION,
    HOUSE_CONVENTIONS_VERSION,
    ayanamsa_degrees,
    house_angles,
    house_layout,
    mean_ecliptic_matrix,
    mean_lunar_node_longitude_degrees,
    osculating_lunar_node_longitude_degrees,
    validate_tt_tdb,
)
from .civil_time import CalendarSystem, calendar_date
from .events import (
    MOON_RADIUS_KM,
    SUN_RADIUS_KM,
    EventProvenance,
    OpticalAtmosphere,
    SolverPolicy,
    _golden_extremum,
    erfa_optical_refraction_model,
    refracted_altitude_degrees,
    solve_ingresses,
    solve_lunar_eclipse_candidate,
    solve_longitude_crossings,
    solve_rise_set_transit,
    solve_solar_eclipse_candidate,
    solve_solar_returns,
    solve_stations,
)
from .kernel_registry import KernelArtifact, KernelRegistry
from .earth_orientation import UtcCalendarInstant, estimate_delta_t
from .receipt import CalculationReceipt
from .stellar_anchors import (
    STELLAR_ANCHOR_CATALOG_VERSION,
    stellar_anchor_for_ayanamsa,
    tropical_longitude_degrees as stellar_tropical_longitude_degrees,
)

J2000_JD = 2451545.0
SECONDS_PER_DAY = 86400.0


@dataclass(frozen=True)
class TimeScaleState:
    utc: tuple[float, float]
    tt: tuple[float, float]
    tdb: tuple[float, float]

    @property
    def utc_jd(self) -> float:
        return self.utc[0] + self.utc[1]

    @property
    def tt_jd(self) -> float:
        return self.tt[0] + self.tt[1]

    @property
    def tdb_jd(self) -> float:
        return self.tdb[0] + self.tdb[1]


@dataclass(frozen=True)
class EarthOrientationParameters:
    dut1_seconds: float
    xp_arcsec: float
    yp_arcsec: float
    dx_mas: float | None = None
    dy_mas: float | None = None
    source: str = "unspecified"
    version: str = "unspecified"
    source_sha256: str | None = None
    quality: str = "unspecified"
    lower_mjd: float | None = None
    upper_mjd: float | None = None


@dataclass(frozen=True)
class GeometricState:
    position_km: tuple[float, float, float]
    velocity_km_per_day: tuple[float, float, float]
    target_naif_id: int
    target_kind: str
    kernel_identifier: str
    kernel_sha256: str


BODY_TARGETS: Mapping[str, tuple[int, str, str]] = {
    "sun": (10, "Sun", "center"),
    "moon": (301, "Moon", "center"),
    "mercury": (199, "Mercury", "center"),
    "venus": (299, "Venus", "center"),
    "earth": (399, "Earth", "center"),
    # Outer planets use planetary system barycenters (NAIF 4, 5, 6, 7, 8, 9),
    # matching the standard compact DE440 target convention.
    "mars": (4, "Mars", "barycenter"),
    "jupiter": (5, "Jupiter", "barycenter"),
    "saturn": (6, "Saturn", "barycenter"),
    "uranus": (7, "Uranus", "barycenter"),
    "neptune": (8, "Neptune", "barycenter"),
    "pluto": (9, "Pluto", "barycenter"),
    "mars_barycenter": (4, "Mars Barycenter", "barycenter"),
    "jupiter_barycenter": (5, "Jupiter Barycenter", "barycenter"),
    "saturn_barycenter": (6, "Saturn Barycenter", "barycenter"),
    "uranus_barycenter": (7, "Uranus Barycenter", "barycenter"),
    "neptune_barycenter": (8, "Neptune Barycenter", "barycenter"),
    "pluto_barycenter": (9, "Pluto Barycenter", "barycenter"),
}

FRAME_ALIASES: Mapping[str, str] = {
    "ICRF": "ICRF",
    "MEAN_EQUATOR_EQUINOX_J2000": "MEAN_EQUATOR_EQUINOX_J2000",
    "EQUATORIAL_MEAN_J2000": "MEAN_EQUATOR_EQUINOX_J2000",
    "MEAN_EQUATOR_EQUINOX_OF_DATE": "MEAN_EQUATOR_EQUINOX_OF_DATE",
    "EQUATORIAL_MEAN_OF_DATE": "MEAN_EQUATOR_EQUINOX_OF_DATE",
    "TRUE_EQUATOR_EQUINOX_OF_DATE": "TRUE_EQUATOR_EQUINOX_OF_DATE",
    "EQUATORIAL_TRUE_OF_DATE": "TRUE_EQUATOR_EQUINOX_OF_DATE",
    "ECLIPTIC_J2000": "ECLIPTIC_J2000",
    "ECLIPTIC_OF_DATE": "ECLIPTIC_OF_DATE",
    "ITRS": "ITRS",
}


class _SpkGraph:
    """Date-aware traversal of an SPK segment graph.

    Later segments take precedence for an overlapping center/target pair, as
    required by SPK kernel priority rules.
    """

    def __init__(self, kernel: SPK) -> None:
        self._segments = tuple(kernel.segments)
        self._path_cache: dict[tuple[int, tuple[tuple[int, int], ...]], list[tuple[Any, float]]] = {}

    def _path(self, target: int, jd: float) -> list[tuple[Any, float]]:
        active: dict[tuple[int, int], Any] = {}
        for segment in self._segments:
            if segment.start_jd <= jd <= segment.end_jd:
                active[(int(segment.center), int(segment.target))] = segment

        cache_key = (target, tuple(sorted((k, id(seg)) for k, seg in active.items())))
        cached = self._path_cache.get(cache_key)
        if cached is not None:
            return cached

        adjacency: dict[int, list[tuple[int, Any, float]]] = {}
        for (center, segment_target), segment in active.items():
            adjacency.setdefault(center, []).append((segment_target, segment, 1.0))
            adjacency.setdefault(segment_target, []).append((center, segment, -1.0))

        queue: deque[tuple[int, list[tuple[Any, float]]]] = deque([(0, [])])
        visited = {0}
        path: list[tuple[Any, float]] | None = None
        while queue:
            node, edges = queue.popleft()
            if node == target:
                path = edges
                break
            for next_node, segment, sign in adjacency.get(node, ()):
                if next_node not in visited:
                    visited.add(next_node)
                    queue.append((next_node, [*edges, (segment, sign)]))

        if path is None:
            raise AstronomyDataUnavailable(
                f"kernel has no active SSB path to NAIF target {target} at TDB JD {jd:.9f}"
            )

        self._path_cache[cache_key] = path
        return path

    def state(self, target: int, tdb: tuple[float, float]) -> tuple[np.ndarray, np.ndarray]:
        path = self._path(target, tdb[0] + tdb[1])
        if len(path) == 1:
            segment, sign = path[0]
            pos, vel = segment.compute_and_differentiate(*tdb)
            if sign == 1.0:
                return np.asarray(pos, dtype=np.float64), np.asarray(vel, dtype=np.float64)
            return -np.asarray(pos, dtype=np.float64), -np.asarray(vel, dtype=np.float64)
        position = np.zeros(3, dtype=np.float64)
        velocity = np.zeros(3, dtype=np.float64)
        for segment, sign in path:
            segment_position, segment_velocity = segment.compute_and_differentiate(*tdb)
            position += sign * np.asarray(segment_position, dtype=np.float64)
            velocity += sign * np.asarray(segment_velocity, dtype=np.float64)
        return position, velocity

    def state_many(self, target: int, tdb_jds: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
        values = np.asarray(tdb_jds, dtype=np.float64)
        if values.ndim != 1 or not len(values) or not np.all(np.isfinite(values)):
            raise ValueError("tdb_jds must be a non-empty finite one-dimensional array")
        minimum = float(np.min(values))
        maximum = float(np.max(values))
        path = self._path(target, float(values[0]))
        # Any segment boundary can change graph connectivity or kernel-priority
        # selection, including a later overlapping segment absent from the
        # first epoch's path. Cross-boundary batches therefore use scalar path
        # resolution for correctness.
        crosses_segment_boundary = any(
            minimum < float(segment.start_jd) <= maximum
            or minimum <= float(segment.end_jd) < maximum
            for segment in self._segments
        )
        if crosses_segment_boundary or any(
            segment.start_jd > minimum or segment.end_jd < maximum
            for segment, _ in path
        ):
            states = [self.state(target, (J2000_JD, float(jd - J2000_JD))) for jd in values]
            return (
                np.stack([state[0] for state in states], axis=1),
                np.stack([state[1] for state in states], axis=1),
            )

        position = np.zeros((3, len(values)), dtype=np.float64)
        velocity = np.zeros((3, len(values)), dtype=np.float64)
        offsets = values - J2000_JD
        for segment, sign in path:
            segment_position, segment_velocity = segment.compute_and_differentiate(
                J2000_JD, offsets
            )
            position += sign * np.asarray(segment_position, dtype=np.float64)
            velocity += sign * np.asarray(segment_velocity, dtype=np.float64)
        return position, velocity


class JplErfaAstronomyProvider(AstronomyProvider):
    """Geometric JPL state vectors and IAU 2006/2000A transformations."""

    _identity = ProviderIdentity("ephemeris-oss", __version__)

    def __init__(
        self,
        *,
        kernel_registry: KernelRegistry,
        leap_seconds_version: str,
        earth_orientation_version: str,
        time_scale_version: str,
        tdb_minus_tt_version: str,
        time_scale_valid_from_utc: date,
        time_scale_valid_through_utc: date,
        ayanamsa_data_version: str,
        earth_orientation_resolver: Callable[
            [datetime | UtcCalendarInstant], EarthOrientationParameters
        ]
        | None = None,
    ) -> None:
        self._kernel_registry = kernel_registry
        self._leap_seconds_version = leap_seconds_version
        self._earth_orientation_version = earth_orientation_version
        self._time_scale_version = time_scale_version
        self._tdb_minus_tt_version = tdb_minus_tt_version
        self._time_scale_valid_from_utc = time_scale_valid_from_utc
        self._time_scale_valid_through_utc = time_scale_valid_through_utc
        self._ayanamsa_data_version = ayanamsa_data_version
        self._earth_orientation_resolver = earth_orientation_resolver
        self._lock = threading.RLock()
        self._open_kernels: dict[str, tuple[SPK, _SpkGraph]] = {}
        self._rise_set_cache: OrderedDict[tuple[Any, ...], dict[str, Any]] = OrderedDict()
        if time_scale_valid_from_utc < date(1550, 1, 1):
            raise ValueError("time-scale policy cannot claim UTC coverage before 1550")
        if time_scale_valid_through_utc < time_scale_valid_from_utc:
            raise ValueError("time-scale validity window is inverted")

    @property
    def identity(self) -> ProviderIdentity:
        return self._identity

    def close(self) -> None:
        with self._lock:
            for kernel, _graph in self._open_kernels.values():
                kernel.close()
            self._open_kernels.clear()
            self._rise_set_cache.clear()

    def planet_positions_tt(
        self,
        *,
        jd_tt: float,
        bodies: Sequence[str],
        jd_tdb: float | None = None,
        mean_equinox: bool = False,
    ) -> dict[str, Any]:
        """Apparent geocentric ecliptic positions at explicit dynamical times."""
        if not math.isfinite(jd_tt) or not bodies:
            raise AstronomyDataUnavailable("TT instant must be finite and bodies nonempty")
        if jd_tdb is not None and not math.isfinite(jd_tdb):
            raise AstronomyDataUnavailable("TDB instant must be finite")
        if jd_tdb is not None:
            validate_tt_tdb(jd_tt, jd_tdb)
        keys = tuple(body.strip().lower() for body in bodies)
        if any(key not in {"sun", "moon", "mercury", "venus", "mars", "jupiter", "saturn"} for key in keys):
            raise AstronomyDataUnavailable("TT apparent output supports the seven classical bodies")
        tt = (J2000_JD, jd_tt - J2000_JD)
        year = int(calendar_date(
            jd_tt, calendar=CalendarSystem.PROLEPTIC_GREGORIAN
        )[0])
        modern = 1600 <= year <= 2400
        if not modern and jd_tdb is None:
            raise AstronomyDataUnavailable(
                "jd_tdb is required outside TT years 1600..2400"
            )
        if not modern and not mean_equinox:
            raise AstronomyDataUnavailable(
                "mean_equinox=True is required outside TT years 1600..2400"
            )
        if jd_tdb is None:
            offset = float(erfa.dtdb(*tt, 0.0, 0.0, 0.0, 0.0))
            tdb = tuple(float(v) for v in erfa.tttdb(*tt, offset))
            tdb_policy = "erfa-dtdb-from-tt"
        else:
            tdb = (J2000_JD, float(jd_tdb) - J2000_JD)
            tdb_policy = "caller-supplied"
        # UTC is unknown and unused in this geocentric Tier A operation.
        times = TimeScaleState(utc=(math.nan, math.nan), tt=tt, tdb=tdb)
        artifact = self._kernel_registry.artifact_for_tdb_jd(times.tdb_jd)
        if mean_equinox:
            frame = np.asarray(mean_ecliptic_matrix(jd_tt), dtype=np.float64)
            nutation = 0.0
            frame_name = "apparent-geocentric-mean-ecliptic-of-date"
        else:
            frame = np.asarray(erfa.ecm06(*tt), dtype=np.float64)
            nutation = math.degrees(float(erfa.nut06a(*tt)[0]))
            frame_name = "apparent-geocentric-true-ecliptic-of-date"
        earth = self.barycentric_state_at_tdb(body="earth", tdb=tdb, kernel_year=year)
        sun_cache: dict[float, BarycentricState] = {}
        def sun_at(jd: float) -> BarycentricState:
            if jd not in sun_cache:
                sun_cache[jd] = self.barycentric_state_at_tdb(
                    body="sun", tdb=(J2000_JD, jd - J2000_JD), kernel_year=year)
            return sun_cache[jd]
        positions = {}
        for key in keys:
            apparent, _ = self._apparent_state(
                body=key, instant_utc=None, kernel_year=year, observer=None, times=times,
                apply_deflection=True, apply_aberration=True,
                precomputed_earth_state=earth, precomputed_sun_func=sun_at)
            lon, lat, _ = self._spherical(frame @ np.asarray(apparent.apparent_vector_km))
            positions[self._body(key)[1]] = {"longitude_deg": (lon + nutation) % 360,
                                            "latitude_deg": lat}
        result_payload: dict[str, Any] = {
            "jd_tt": jd_tt,
            "jd_tdb": times.tdb_jd,
            "positions": positions,
            "frame": frame_name,
            "kernel_sha256": artifact.sha256.lower(),
        }
        if jd_tdb is not None or mean_equinox:
            result_payload.update({
                "tdb_policy": tdb_policy,
                "mean_equinox": bool(mean_equinox),
            })
        if artifact.identifier.startswith("COMPACT-DE440"):
            result_payload["kernel_mode"] = "compact-chebyshev-de440"
        return result_payload

    def __enter__(self) -> "JplErfaAstronomyProvider":
        return self

    def __exit__(self, *_: Any) -> None:
        self.close()

    @staticmethod
    def _calendar_year(instant_utc: datetime | UtcCalendarInstant) -> int:
        return instant_utc.year

    def utc_time_scales(
        self, instant_utc: datetime | UtcCalendarInstant
    ) -> TimeScaleState:
        if isinstance(instant_utc, UtcCalendarInstant):
            instant = instant_utc
            civil_date = date(instant.year, instant.month, instant.day)
            utc = instant.utc_jd()
            seconds = instant.second
        else:
            if instant_utc.tzinfo is None or instant_utc.utcoffset() is None:
                raise ValueError("instant_utc must be timezone-aware")
            instant = instant_utc.astimezone(timezone.utc)
            civil_date = instant.date()
            seconds = instant.second + instant.microsecond / 1_000_000.0
            utc = tuple(
                float(value)
                for value in erfa.dtf2d(
                    "UTC",
                    instant.year,
                    instant.month,
                    instant.day,
                    instant.hour,
                    instant.minute,
                    seconds,
                )
            )
        if not (
            self._time_scale_valid_from_utc
            <= civil_date
            <= self._time_scale_valid_through_utc
        ):
            raise AstronomyDataUnavailable(
                "UTC instant is outside the provider's versioned time-scale validity window "
                f"[{self._time_scale_valid_from_utc.isoformat()}, "
                f"{self._time_scale_valid_through_utc.isoformat()}]"
            )
        if civil_date < date(1960, 1, 1):
            jd_ut = utc[0] + utc[1]
            cal_year = instant.year if hasattr(instant, "year") else civil_date.year
            cal_month = instant.month if hasattr(instant, "month") else civil_date.month
            cal_day = instant.day if hasattr(instant, "day") else civil_date.day
            decimal_year = cal_year + (cal_month - 1) / 12.0 + cal_day / 365.25
            delta_t_sec = estimate_delta_t(decimal_year).seconds
            tt_jd = jd_ut + delta_t_sec / SECONDS_PER_DAY
            tt = (J2000_JD, float(tt_jd - J2000_JD))
        else:
            tai = tuple(float(value) for value in erfa.utctai(*utc))
            tt = tuple(float(value) for value in erfa.taitt(*tai))
        ut_fraction = (
            instant.hour * 3600.0 + instant.minute * 60.0 + seconds
        ) / SECONDS_PER_DAY
        tdb_minus_tt = float(erfa.dtdb(*tt, ut_fraction, 0.0, 0.0, 0.0))
        tdb = tuple(float(value) for value in erfa.tttdb(*tt, tdb_minus_tt))
        return TimeScaleState(utc=utc, tt=tt, tdb=tdb)

    def _kernel(self, tdb_jd: float) -> tuple[KernelArtifact, _SpkGraph]:
        artifact = self._kernel_registry.artifact_for_tdb_jd(tdb_jd)
        with self._lock:
            cached = self._open_kernels.get(artifact.identifier)
            if cached is not None:
                return artifact, cached[1]
            path = self._kernel_registry.verified_path_for_tdb_jd(tdb_jd)
            if artifact.identifier.startswith("COMPACT-DE440"):
                from ..compact_kernel import CompactChebyshevKernel

                kernel: Any = CompactChebyshevKernel.open(path)
            else:
                kernel = SPK.open(str(path))
            graph = _SpkGraph(kernel)
            self._open_kernels[artifact.identifier] = (kernel, graph)
            return artifact, graph

    @staticmethod
    def _body(body: str) -> tuple[int, str, str]:
        try:
            return BODY_TARGETS[body.strip().lower()]
        except KeyError as error:
            raise AstronomyDataUnavailable(f"unsupported body: {body}") from error

    def geocentric_state_at_tdb_jd(
        self, *, body: str, tdb_jd: float, kernel_year: int
    ) -> GeometricState:
        if not math.isfinite(tdb_jd):
            raise ValueError("tdb_jd must be finite")
        return self.geocentric_state_at_tdb(
            body=body,
            tdb=(J2000_JD, float(tdb_jd - J2000_JD)),
            kernel_year=kernel_year,
        )

    def barycentric_state_at_tdb(
        self, *, body: str, tdb: tuple[float, float], kernel_year: int
    ) -> BarycentricState:
        """Return one physical-center or explicit-barycenter ICRF state."""

        if len(tdb) != 2 or not all(math.isfinite(value) for value in tdb):
            raise ValueError("tdb must contain two finite Julian-date components")
        target, display_name, target_kind = self._body(body)
        artifact, graph = self._kernel(tdb[0] + tdb[1])
        barycenter_fallback = {499: 4, 599: 5, 699: 6, 799: 7, 899: 8, 999: 9}
        try:
            position, velocity = graph.state(target, tdb)
        except AstronomyDataUnavailable as error:
            if target in barycenter_fallback:
                fallback_target = barycenter_fallback[target]
                position, velocity = graph.state(fallback_target, tdb)
                target = fallback_target
                target_kind = "barycenter"
            else:
                raise AstronomyDataUnavailable(
                    f"{display_name} {target_kind} (NAIF {target}) is unavailable in "
                    f"kernel {artifact.identifier}; supply a checksum-gated supplemental "
                    "planet-center SPK or request the explicit *_barycenter target"
                ) from error
        return BarycentricState(
            position_km=tuple(float(value) for value in position),
            velocity_km_per_day=tuple(float(value) for value in velocity),
            source=f"{artifact.identifier}:{artifact.sha256.lower()}:{target}",
        )

    def _target_state_func(
        self,
        *,
        body: str,
        times: TimeScaleState,
        kernel_year: int,
        base_target_func: Callable[[float], BarycentricState] | None = None,
        sun_func: Callable[[float], BarycentricState] | None = None,
    ) -> Callable[[float], BarycentricState]:
        if base_target_func is not None and getattr(
            base_target_func, "_lunar_straddle_wrapped", False
        ):
            return base_target_func

        @lru_cache(maxsize=16)
        def default_target_at(jd: float) -> BarycentricState:
            return self.barycentric_state_at_tdb(
                body=body,
                tdb=(J2000_JD, jd - J2000_JD),
                kernel_year=kernel_year,
            )

        raw_target_func = base_target_func or (
            sun_func
            if (sun_func is not None and body.strip().lower() == "sun")
            else default_target_at
        )
        artifact = self._kernel_registry.artifact_for_tdb_jd(times.tdb_jd)
        if body.strip().lower() != "moon" or not artifact.identifier.startswith("COMPACT-DE440"):
            return raw_target_func

        _rec_artifact, rec_graph = self._kernel(times.tdb_jd)
        emb_pos_rec, emb_vel_rec = rec_graph.state(3, times.tdb)
        rec_tdb_jd = times.tdb_jd
        rec_block_16 = int(math.floor((rec_tdb_jd - 2287184.5) / 16.0))

        @lru_cache(maxsize=16)
        def _moon_state_at(jd: float) -> BarycentricState:
            raw_state = raw_target_func(jd)
            if int(math.floor((float(jd) - 2287184.5) / 16.0)) == rec_block_16:
                return raw_state
            dt_days = float(jd - rec_tdb_jd)
            em_tdb = (J2000_JD, float(jd - J2000_JD))
            _em_artifact, em_graph = self._kernel(jd)
            emb_em_pos, emb_em_vel = em_graph.state(3, em_tdb)
            moon_ssb_pos = np.asarray(raw_state.position_km, dtype=np.float64)
            moon_ssb_vel = np.asarray(raw_state.velocity_km_per_day, dtype=np.float64)
            rel_moon_pos = moon_ssb_pos - emb_em_pos
            rel_moon_vel = moon_ssb_vel - emb_em_vel
            pos = emb_pos_rec + emb_vel_rec * dt_days + rel_moon_pos
            vel = emb_vel_rec + rel_moon_vel
            return BarycentricState(
                position_km=tuple(float(v) for v in pos),
                velocity_km_per_day=tuple(float(v) for v in vel),
                source=raw_state.source,
            )

        setattr(_moon_state_at, "_lunar_straddle_wrapped", True)
        return _moon_state_at

    def _apparent_state(
        self,
        *,
        body: str,
        instant_utc: datetime | UtcCalendarInstant | None,
        observer: Observer | None,
        times: TimeScaleState,
        apply_deflection: bool,
        apply_aberration: bool,
        precomputed_earth_state: BarycentricState | None = None,
        precomputed_observer_state: BarycentricState | None = None,
        precomputed_eop: EarthOrientationParameters | None = None,
        precomputed_sun_func: Callable[[float], BarycentricState] | None = None,
        precomputed_target_func: Callable[[float], BarycentricState] | None = None,
        kernel_year: int | None = None,
    ) -> tuple[Any, EarthOrientationParameters | None]:
        if kernel_year is None:
            if instant_utc is None:
                raise AstronomyDataUnavailable("kernel calendar year or UTC instant is required")
            kernel_year = self._calendar_year(instant_utc)
        if observer is not None and instant_utc is None:
            raise AstronomyDataUnavailable("topocentric output requires UTC and Earth orientation")

        def state_at(requested_body: str) -> Callable[[float], BarycentricState]:
            @lru_cache(maxsize=16)
            def at(jd: float) -> BarycentricState:
                return self.barycentric_state_at_tdb(
                    body=requested_body,
                    tdb=(J2000_JD, jd - J2000_JD),
                    kernel_year=kernel_year,
                )
            # The cache dies with this solve. It only avoids an identical
            # converged state being read again; no chart output is cached.
            return at

        earth_state = (
            precomputed_earth_state
            if precomputed_earth_state is not None
            else self.barycentric_state_at_tdb(
                body="earth", tdb=times.tdb, kernel_year=kernel_year
            )
        )
        eop: EarthOrientationParameters | None = precomputed_eop
        observer_state = earth_state
        if observer is not None:
            if precomputed_observer_state is not None:
                observer_state = precomputed_observer_state
            else:
                eop = self._resolve_eop(instant_utc)
                observer_state = terrestrial_observer_barycentric_state(
                    earth_barycentric_state=earth_state,
                    observer=GeodeticObserver(
                        observer.longitude_deg,
                        observer.latitude_deg,
                        observer.altitude_m,
                    ),
                    earth_orientation=EarthOrientation(
                        utc=times.utc,
                        tt=times.tt,
                        dut1_seconds=eop.dut1_seconds,
                        xp_arcsec=eop.xp_arcsec,
                        yp_arcsec=eop.yp_arcsec,
                        source=eop.source,
                        version=eop.version,
                        dx_mas=eop.dx_mas or 0.0,
                        dy_mas=eop.dy_mas or 0.0,
                    ),
                )
        artifact = self._kernel_registry.artifact_for_tdb_jd(times.tdb_jd)
        sun_func = precomputed_sun_func or state_at("sun")
        target_func = self._target_state_func(
            body=body,
            times=times,
            kernel_year=kernel_year,
            base_target_func=precomputed_target_func,
            sun_func=sun_func,
        )
        result = apparent_place(
            target_state_at_tdb=target_func,
            sun_state_at_tdb=sun_func,
            observer_barycentric_state=observer_state,
            reception_tdb_jd=times.tdb_jd,
            provenance=ApparentPlaceProvenance(
                ephemeris_source="JPL-SPK",
                ephemeris_version=f"{artifact.identifier}:{artifact.sha256.lower()}",
                eop_source=(eop.source if eop else None),
                eop_version=(eop.version if eop else None),
            ),
            # A target cannot gravitationally deflect its own light.
            apply_solar_deflection=apply_deflection and body.strip().lower() != "sun",
            apply_aberration=apply_aberration,
            tolerance_seconds=1.0e-4,
        )
        return result, eop

    @staticmethod
    def _spherical(vector: Sequence[float]) -> tuple[float, float, float]:
        value = np.asarray(vector, dtype=np.float64)
        radius = float(np.linalg.norm(value))
        if not radius:
            raise AstronomyDataUnavailable("zero-length state has undefined coordinates")
        return (
            math.degrees(math.atan2(value[1], value[0])) % 360.0,
            math.degrees(math.asin(float(value[2]) / radius)),
            radius,
        )

    def _osculating_lunar_node(self, times: TimeScaleState, kernel_year: int) -> float:
        """Return the inertial osculating orbit plane expressed on the ecliptic of date."""

        state = self.geocentric_state_at_tdb(
            body="moon", tdb=times.tdb, kernel_year=kernel_year
        )
        position = np.asarray(state.position_km, dtype=np.float64)
        velocity = np.asarray(state.velocity_km_per_day, dtype=np.float64)
        rotation = np.asarray(erfa.ecm06(*times.tt), dtype=np.float64)
        ecliptic_position = rotation @ position
        # R-dot*r is the velocity of the coordinate axes, not part of the
        # Moon's inertial angular momentum. Adding it tilts the orbit plane.
        ecliptic_velocity = rotation @ velocity
        return osculating_lunar_node_longitude_degrees(
            ecliptic_position,
            ecliptic_velocity,
        )

    def _ayanamsa_offset(self, times: TimeScaleState, convention: str) -> float:
        anchor = stellar_anchor_for_ayanamsa(convention)
        anchor_longitude = (
            None
            if anchor is None
            else stellar_tropical_longitude_degrees(anchor, tt=times.tt)
        )
        return ayanamsa_degrees(
            times.tt_jd,
            convention,
            anchor_tropical_longitude_deg=anchor_longitude,
        )

    def geocentric_state_at_tdb(
        self, *, body: str, tdb: tuple[float, float], kernel_year: int
    ) -> GeometricState:
        if len(tdb) != 2 or not all(math.isfinite(value) for value in tdb):
            raise ValueError("tdb must contain two finite Julian-date components")
        target, _name, target_kind = self._body(body)
        artifact, graph = self._kernel(tdb[0] + tdb[1])
        earth_position, earth_velocity = graph.state(399, tdb)
        if target == 399:
            position = np.zeros(3, dtype=np.float64)
            velocity = np.zeros(3, dtype=np.float64)
        else:
            target_position, target_velocity = graph.state(target, tdb)
            position = target_position - earth_position
            velocity = target_velocity - earth_velocity
        return GeometricState(
            position_km=tuple(float(value) for value in position),
            velocity_km_per_day=tuple(float(value) for value in velocity),
            target_naif_id=target,
            target_kind=target_kind,
            kernel_identifier=artifact.identifier,
            kernel_sha256=artifact.sha256.lower(),
        )

    def geocentric_states_at_tdb_jds(
        self, *, body: str, tdb_jds: Sequence[float], kernel_year: int
    ) -> tuple[np.ndarray, np.ndarray, Mapping[str, Any]]:
        del kernel_year
        values = np.asarray(tdb_jds, dtype=np.float64)
        if values.ndim != 1 or not len(values) or not np.all(np.isfinite(values)):
            raise ValueError("tdb_jds must be a non-empty finite one-dimensional array")
        identifiers = {
            self._kernel_registry.artifact_for_tdb_jd(float(jd)).identifier
            for jd in values
        }
        if len(identifiers) != 1:
            raise AstronomyDataUnavailable(
                "vectorized request spans multiple kernels; split it at the kernel boundary"
            )
        target, _name, target_kind = self._body(body)
        artifact, graph = self._kernel(float(values[0]))
        earth_position, earth_velocity = graph.state_many(399, values)
        if target == 399:
            position = np.zeros_like(earth_position)
            velocity = np.zeros_like(earth_velocity)
        else:
            target_position, target_velocity = graph.state_many(target, values)
            position = target_position - earth_position
            velocity = target_velocity - earth_velocity
        return position, velocity, {
            "target_naif_id": target,
            "target_kind": target_kind,
            "kernel_identifier": artifact.identifier,
            "kernel_sha256": artifact.sha256.lower(),
        }

    def geocentric_states_for_bodies_at_tdb_jds(
        self, *, bodies: Sequence[str], tdb_jds: Sequence[float], kernel_year: int
    ) -> Mapping[str, tuple[np.ndarray, np.ndarray, Mapping[str, Any]]]:
        del kernel_year
        values = np.asarray(tdb_jds, dtype=np.float64)
        if values.ndim != 1 or not len(values) or not np.all(np.isfinite(values)):
            raise ValueError("tdb_jds must be a non-empty finite one-dimensional array")
        identifiers = {
            self._kernel_registry.artifact_for_tdb_jd(float(jd)).identifier
            for jd in values
        }
        if len(identifiers) != 1:
            raise AstronomyDataUnavailable(
                "vectorized request spans multiple kernels; split it at the kernel boundary"
            )
        artifact, graph = self._kernel(float(values[0]))
        earth_position, earth_velocity = graph.state_many(399, values)
        output: dict[str, tuple[np.ndarray, np.ndarray, Mapping[str, Any]]] = {}
        for body in bodies:
            target, display_name, target_kind = self._body(body)
            if target == 399:
                position = np.zeros_like(earth_position)
                velocity = np.zeros_like(earth_velocity)
            else:
                target_position, target_velocity = graph.state_many(target, values)
                position = target_position - earth_position
                velocity = target_velocity - earth_velocity
            output[display_name] = (
                position,
                velocity,
                {
                    "target_naif_id": target,
                    "target_kind": target_kind,
                    "kernel_identifier": artifact.identifier,
                    "kernel_sha256": artifact.sha256.lower(),
                },
            )
        return output

    @staticmethod
    def _normalize_frame(frame: str) -> str:
        key = frame.strip().upper().replace("-", "_").replace(" ", "_")
        try:
            return FRAME_ALIASES[key]
        except KeyError as error:
            raise AstronomyDataUnavailable(f"unsupported coordinate frame: {frame}") from error

    @staticmethod
    def _celestial_matrix(frame: str, tt: tuple[float, float]) -> np.ndarray:
        if frame == "ICRF":
            return np.identity(3, dtype=np.float64)
        if frame == "MEAN_EQUATOR_EQUINOX_J2000":
            return np.asarray(erfa.pmat06(J2000_JD, 0.0), dtype=np.float64)
        if frame == "MEAN_EQUATOR_EQUINOX_OF_DATE":
            return np.asarray(erfa.pmat06(*tt), dtype=np.float64)
        if frame == "TRUE_EQUATOR_EQUINOX_OF_DATE":
            return np.asarray(erfa.pnm06a(*tt), dtype=np.float64)
        if frame == "ECLIPTIC_J2000":
            return np.asarray(erfa.ecm06(J2000_JD, 0.0), dtype=np.float64)
        if frame == "ECLIPTIC_OF_DATE":
            return np.asarray(erfa.ecm06(*tt), dtype=np.float64)
        raise AstronomyDataUnavailable(f"unsupported celestial frame: {frame}")

    @staticmethod
    def _itrs_matrix(
        tt: tuple[float, float], ut1: tuple[float, float], eop: EarthOrientationParameters
    ) -> np.ndarray:
        x, y, _s = (float(value) for value in erfa.xys06a(*tt))
        if (eop.dx_mas is None) != (eop.dy_mas is None):
            raise AstronomyDataUnavailable("EOP dX and dY must be supplied together")
        if eop.dx_mas is not None and eop.dy_mas is not None:
            x += eop.dx_mas * erfa.DMAS2R
            y += eop.dy_mas * erfa.DMAS2R
        s = float(erfa.s06(*tt, x, y))
        celestial_to_intermediate = np.asarray(erfa.c2ixys(x, y, s), dtype=np.float64)
        era = float(erfa.era00(*ut1))
        polar_motion = np.asarray(
            erfa.pom00(
                eop.xp_arcsec * erfa.DAS2R,
                eop.yp_arcsec * erfa.DAS2R,
                erfa.sp00(*tt),
            ),
            dtype=np.float64,
        )
        return np.asarray(
            erfa.c2tcio(celestial_to_intermediate, era, polar_motion),
            dtype=np.float64,
        )

    def _resolve_eop(
        self, instant_utc: datetime | UtcCalendarInstant
    ) -> EarthOrientationParameters:
        if self._earth_orientation_resolver is None:
            raise AstronomyDataUnavailable("operation requires versioned Earth-orientation data")
        resolved = self._earth_orientation_resolver(instant_utc)
        return EarthOrientationParameters(
            dut1_seconds=float(resolved.dut1_seconds),
            xp_arcsec=float(resolved.xp_arcsec),
            yp_arcsec=float(resolved.yp_arcsec),
            dx_mas=(None if getattr(resolved, "dx_mas", None) is None else float(resolved.dx_mas)),
            dy_mas=(None if getattr(resolved, "dy_mas", None) is None else float(resolved.dy_mas)),
            source=str(getattr(resolved, "source", "IERS-finals2000A")),
            version=str(getattr(resolved, "version", self._earth_orientation_version)),
            source_sha256=getattr(resolved, "source_sha256", None),
            quality=str(getattr(getattr(resolved, "quality", None), "value", getattr(resolved, "quality", "unspecified"))),
            lower_mjd=(
                None
                if getattr(resolved, "lower_mjd", None) is None
                else float(resolved.lower_mjd)
            ),
            upper_mjd=(
                None
                if getattr(resolved, "upper_mjd", None) is None
                else float(resolved.upper_mjd)
            ),
        )

    def _icrf_to_frame_matrix(
        self,
        frame: str,
        instant_utc: datetime | UtcCalendarInstant,
        time_scales: TimeScaleState,
    ) -> np.ndarray:
        normalized = self._normalize_frame(frame)
        if normalized == "ITRS":
            eop = self._resolve_eop(instant_utc)
            ut1 = erfa.utcut1(*time_scales.utc, eop.dut1_seconds)
            return self._itrs_matrix(time_scales.tt, ut1, eop)
        return self._celestial_matrix(normalized, time_scales.tt)

    def coordinate_transform(
        self,
        *,
        vector: Sequence[float],
        source_frame: str,
        target_frame: str,
        instant_utc: datetime | UtcCalendarInstant,
        observer: Observer | None,
        settings: CalculationSettings,
    ) -> Sequence[float]:
        del observer, settings
        value = np.asarray(vector, dtype=np.float64)
        if value.shape != (3,) or not np.all(np.isfinite(value)):
            raise ValueError("vector must contain three finite components")
        times = self.utc_time_scales(instant_utc)
        source_matrix = self._icrf_to_frame_matrix(source_frame, instant_utc, times)
        target_matrix = self._icrf_to_frame_matrix(target_frame, instant_utc, times)
        icrf = source_matrix.T @ value
        transformed = target_matrix @ icrf
        return tuple(float(component) for component in transformed)

    def planet_positions(
        self,
        *,
        instant_utc: datetime | UtcCalendarInstant,
        bodies: Sequence[str],
        observer: Observer | None,
        settings: CalculationSettings,
    ) -> Mapping[str, Any]:
        flags = {flag.strip().lower() for flag in settings.correction_flags}
        supported = {"geometric", "light_time", "aberration", "solar_deflection", "apparent"}
        unsupported_corrections = flags - supported
        if unsupported_corrections:
            names = ", ".join(sorted(unsupported_corrections))
            raise AstronomyDataUnavailable(f"unsupported correction flags: {names}")
        use_apparent = bool(flags & {"light_time", "aberration", "solar_deflection", "apparent"})
        if observer is not None and not use_apparent:
            raise AstronomyDataUnavailable(
                "topocentric output requires light_time/apparent corrections"
            )
        zodiac_mode = settings.zodiac_mode.strip().lower()
        if zodiac_mode not in {"tropical", "sidereal"}:
            raise AstronomyDataUnavailable(f"unsupported zodiac mode: {settings.zodiac_mode!r}")
        frame = self._normalize_frame(settings.frame)
        if zodiac_mode == "sidereal" and not frame.startswith("ECLIPTIC"):
            raise AstronomyDataUnavailable("sidereal longitude requires an ecliptic frame")
        if zodiac_mode == "sidereal" and not settings.ayanamsa:
            raise AstronomyDataUnavailable("sidereal output requires an ayanamsa convention")

        times = self.utc_time_scales(instant_utc)
        frame_matrix = self._icrf_to_frame_matrix(frame, instant_utc, times)
        sidereal_offset = (
            self._ayanamsa_offset(times, settings.ayanamsa or "")
            if zodiac_mode == "sidereal"
            else 0.0
        )
        positions: dict[str, Any] = {}
        selected_artifact: KernelArtifact | None = None
        used_eop: EarthOrientationParameters | None = None

        pre_earth_state: BarycentricState | None = None
        pre_observer_state: BarycentricState | None = None
        pre_eop: EarthOrientationParameters | None = None
        pre_sun_func: Callable[[float], BarycentricState] | None = None

        has_apparent_bodies = any(
            b.strip().lower().replace(" ", "_") not in {"rahu", "ketu", "mean_node", "mean_lunar_node"}
            for b in bodies
        )
        if use_apparent and has_apparent_bodies:
            k_year = self._calendar_year(instant_utc)
            pre_earth_state = self.barycentric_state_at_tdb(
                body="earth", tdb=times.tdb, kernel_year=k_year
            )
            pre_sun_cache: dict[float, BarycentricState] = {}

            def pre_sun_func(jd: float) -> BarycentricState:
                cached_sun = pre_sun_cache.get(jd)
                if cached_sun is None:
                    cached_sun = self.barycentric_state_at_tdb(
                        body="sun", tdb=(J2000_JD, jd - J2000_JD), kernel_year=k_year
                    )
                    pre_sun_cache[jd] = cached_sun
                return cached_sun
            if observer is not None:
                pre_eop = self._resolve_eop(instant_utc)
                pre_observer_state = terrestrial_observer_barycentric_state(
                    earth_barycentric_state=pre_earth_state,
                    observer=GeodeticObserver(
                        observer.longitude_deg,
                        observer.latitude_deg,
                        observer.altitude_m,
                    ),
                    earth_orientation=EarthOrientation(
                        utc=times.utc,
                        tt=times.tt,
                        dut1_seconds=pre_eop.dut1_seconds,
                        xp_arcsec=pre_eop.xp_arcsec,
                        yp_arcsec=pre_eop.yp_arcsec,
                        source=pre_eop.source,
                        version=pre_eop.version,
                        dx_mas=pre_eop.dx_mas or 0.0,
                        dy_mas=pre_eop.dy_mas or 0.0,
                    ),
                )
                used_eop = pre_eop

        for requested_body in bodies:
            requested_key = requested_body.strip().lower().replace(" ", "_")
            if requested_key in {"rahu", "ketu", "mean_node", "mean_lunar_node"}:
                node_mode = settings.node_mode.strip().lower()
                if node_mode == "mean":
                    tropical_node = mean_lunar_node_longitude_degrees(times.tt_jd)
                    position_type = "mean_lunar_node_axis"
                    node_speed = -0.05295376
                    node_retro = True
                elif node_mode in {"true", "osculating"}:
                    k_yr = self._calendar_year(instant_utc)
                    tropical_node = self._osculating_lunar_node(times, k_yr)
                    position_type = "osculating_lunar_node_axis"
                    step = timedelta(seconds=43.2)
                    times_p = self.utc_time_scales(instant_utc + step)
                    times_m = self.utc_time_scales(instant_utc - step)
                    n_p = self._osculating_lunar_node(times_p, k_yr)
                    n_m = self._osculating_lunar_node(times_m, k_yr)
                    node_speed = ((n_p - n_m + 180.0) % 360.0 - 180.0) / 0.001
                    node_retro = (node_speed < 0.0)
                else:
                    raise AstronomyDataUnavailable(
                        f"unsupported lunar node mode: {settings.node_mode!r}"
                    )
                if requested_key == "ketu":
                    tropical_node = (tropical_node + 180.0) % 360.0
                longitude = tropical_node
                if zodiac_mode == "sidereal":
                    longitude = (tropical_node - sidereal_offset) % 360.0
                label = "Ketu" if requested_key == "ketu" else "Rahu"
                positions[label] = {
                    "longitude_deg": longitude,
                    "tropical_longitude_deg": tropical_node,
                    "latitude_deg": 0.0,
                    "speed_deg_per_day": node_speed,
                    "retrograde": node_retro,
                    "position_type": position_type,
                    "node_mode": node_mode,
                }
                continue
            _target, display_name, _kind = self._body(requested_body)
            selected_artifact = self._kernel_registry.artifact_for_tdb_jd(times.tdb_jd)
            if use_apparent:
                target_state = self._target_state_func(
                    body=requested_body,
                    times=times,
                    kernel_year=k_year,
                    sun_func=pre_sun_func,
                )

                apparent, eop = self._apparent_state(
                    body=requested_body,
                    instant_utc=instant_utc,
                    observer=observer,
                    times=times,
                    apply_deflection=("apparent" in flags or "solar_deflection" in flags),
                    apply_aberration=("apparent" in flags or "aberration" in flags),
                    precomputed_earth_state=pre_earth_state,
                    precomputed_observer_state=pre_observer_state,
                    precomputed_eop=pre_eop,
                    precomputed_sun_func=pre_sun_func,
                    precomputed_target_func=target_state,
                )
                used_eop = eop or used_eop
                icrf = np.asarray(apparent.apparent_vector_km, dtype=np.float64)
                tau = apparent.light_time_seconds / 86400.0
                st = target_state(times.tdb_jd - tau)
                obs_vel = (
                    pre_observer_state.velocity_km_per_day
                    if pre_observer_state
                    else pre_earth_state.velocity_km_per_day  # type: ignore[union-attr]
                )
                v_icrf = np.asarray(st.velocity_km_per_day, dtype=np.float64) - np.asarray(obs_vel, dtype=np.float64)
                velocity_icrf = [float(v) for v in v_icrf]
                target, _display, target_kind = self._body(requested_body)
                position_type = (
                    "apparent_topocentric" if observer is not None else "apparent_geocentric"
                )
                correction_data: dict[str, Any] = {
                    "light_time_seconds": apparent.light_time_seconds,
                    "light_time_iterations": apparent.light_time_iterations,
                    "solar_deflection_applied": apparent.solar_deflection_applied,
                }
            else:
                state = self.geocentric_state_at_tdb(
                    body=requested_body,
                    tdb=times.tdb,
                    kernel_year=self._calendar_year(instant_utc),
                )
                icrf = np.asarray(state.position_km, dtype=np.float64)
                velocity_icrf = list(state.velocity_km_per_day)
                v_icrf = np.asarray(state.velocity_km_per_day, dtype=np.float64)
                target = state.target_naif_id
                target_kind = state.target_kind
                position_type = "geometric_geocentric"
                correction_data = {}
            transformed = frame_matrix @ icrf
            v_transformed = frame_matrix @ v_icrf
            longitude, latitude, radius = self._spherical(transformed)
            denom = transformed[0] * transformed[0] + transformed[1] * transformed[1]
            speed_deg_per_day = (
                math.degrees((transformed[0] * v_transformed[1] - transformed[1] * v_transformed[0]) / denom)
                if denom > 1e-12
                else 0.0
            )
            retrograde = (speed_deg_per_day < 0.0) if display_name not in ("Sun", "Moon") else False
            tropical_longitude = longitude
            if zodiac_mode == "sidereal":
                longitude = (tropical_longitude - sidereal_offset) % 360.0
            ra, dec, icrf_radius = self._spherical(icrf)
            positions[display_name] = {
                "position_icrf_km": [float(value) for value in icrf],
                "velocity_icrf_km_per_day": velocity_icrf,
                "position_frame_km": [float(value) for value in transformed],
                "distance_km": radius,
                "longitude_deg": longitude,
                "tropical_longitude_deg": tropical_longitude,
                "latitude_deg": latitude,
                "speed_deg_per_day": speed_deg_per_day,
                "retrograde": retrograde,
                "right_ascension_deg": ra,
                "declination_deg": dec,
                "target_naif_id": target,
                "target_kind": target_kind,
                "position_type": position_type,
                **correction_data,
            }

        if selected_artifact is None:
            selected_artifact = self._kernel_registry.artifact_for_tdb_jd(times.tdb_jd)
        datasets = DatasetVersions(
            kernel_identifier=selected_artifact.identifier,
            kernel_sha256=selected_artifact.sha256,
            leap_seconds=self._leap_seconds_version,
            earth_orientation=(used_eop.version if used_eop else self._earth_orientation_version),
            delta_t="not-used-for-utc-tai-tt",
            ayanamsa=(
                f"{self._ayanamsa_data_version};stellar={STELLAR_ANCHOR_CATALOG_VERSION}"
            ),
            time_scale=self._time_scale_version,
            tdb_minus_tt=self._tdb_minus_tt_version,
            earth_orientation_sha256=(used_eop.source_sha256 if used_eop else None),
            earth_orientation_quality=(used_eop.quality if used_eop else None),
            earth_orientation_lower_mjd=(used_eop.lower_mjd if used_eop else None),
            earth_orientation_upper_mjd=(used_eop.upper_mjd if used_eop else None),
            kernel_mode=(
                "compact-chebyshev-de440"
                if selected_artifact.identifier.startswith("COMPACT-DE440")
                else None
            ),
        )
        request = {
            "instant_utc": instant_utc,
            "bodies": list(bodies),
            "observer": observer,
            "settings": settings,
            "position_type": "apparent" if use_apparent else "geometric_geocentric",
        }
        receipt = CalculationReceipt.from_request(
            provider=self.identity,
            datasets=datasets,
            settings=settings,
            observer=observer,
            request=request,
        )
        return {
            "positions": positions,
            "time_scales_jd": {
                "utc": times.utc_jd,
                "tt": times.tt_jd,
                "tdb": times.tdb_jd,
            },
            "earth_orientation": (
                None
                if used_eop is None
                else {
                    "source": used_eop.source,
                    "version": used_eop.version,
                    "source_sha256": used_eop.source_sha256,
                    "quality": used_eop.quality,
                    "dut1_seconds": used_eop.dut1_seconds,
                    "xp_arcsec": used_eop.xp_arcsec,
                    "yp_arcsec": used_eop.yp_arcsec,
                    "dx_mas": used_eop.dx_mas,
                    "dy_mas": used_eop.dy_mas,
                    "lower_mjd": used_eop.lower_mjd,
                    "upper_mjd": used_eop.upper_mjd,
                }
            ),
            "calculation_receipt": receipt.payload(),
            "calculation_receipt_sha256": receipt.sha256(),
        }

    def julian_day(self, *, instant_utc: datetime | UtcCalendarInstant) -> float:
        return self.utc_time_scales(instant_utc).utc_jd

    def reverse_julian_day(
        self, *, julian_day: float | tuple[float, float]
    ) -> datetime | UtcCalendarInstant:
        if isinstance(julian_day, tuple):
            if len(julian_day) != 2 or not all(math.isfinite(value) for value in julian_day):
                raise ValueError("two-part julian_day must contain two finite values")
            first, second = julian_day
        else:
            if not math.isfinite(julian_day):
                raise ValueError("julian_day must be finite")
            first, second = J2000_JD, julian_day - J2000_JD
        year, month, day, hmsf = erfa.d2dtf("UTC", 6, first, second)
        if int(hmsf["s"]) == 60:
            instant: datetime | UtcCalendarInstant = UtcCalendarInstant(
                int(year),
                int(month),
                int(day),
                int(hmsf["h"]),
                int(hmsf["m"]),
                60.0 + int(hmsf["f"]) / 1_000_000.0,
            )
        else:
            base = datetime(int(year), int(month), int(day), tzinfo=timezone.utc)
            instant = base + timedelta(
                hours=int(hmsf["h"]),
                minutes=int(hmsf["m"]),
                seconds=int(hmsf["s"]),
                microseconds=int(hmsf["f"]),
            )
        instant_date = date(instant.year, instant.month, instant.day)
        if not (
            self._time_scale_valid_from_utc
            <= instant_date
            <= self._time_scale_valid_through_utc
        ):
            raise AstronomyDataUnavailable(
                "UTC instant is outside the provider's versioned time-scale validity window "
                f"[{self._time_scale_valid_from_utc.isoformat()}, "
                f"{self._time_scale_valid_through_utc.isoformat()}]"
            )
        return instant

    @staticmethod
    def _not_implemented(capability: str) -> AstronomyDataUnavailable:
        return AstronomyDataUnavailable(f"{capability} is not implemented in the numerical slice")

    def ayanamsa(
        self, *, instant_utc: datetime | UtcCalendarInstant, convention: str
    ) -> float:
        return self._ayanamsa_offset(self.utc_time_scales(instant_utc), convention)

    def houses(
        self,
        *,
        instant_utc: datetime | UtcCalendarInstant,
        observer: Observer,
        system: str,
        settings: CalculationSettings,
    ) -> Mapping[str, Any]:
        times = self.utc_time_scales(instant_utc)
        eop = self._resolve_eop(instant_utc)
        ut1 = erfa.utcut1(*times.utc, eop.dut1_seconds)
        angles = house_angles(
            tt_jd=times.tt_jd,
            ut1_jd=float(ut1[0] + ut1[1]),
            longitude_deg=observer.longitude_deg,
            latitude_deg=observer.latitude_deg,
        )
        layout = house_layout(
            system,
            ascendant_deg=angles.ascendant_deg,
            midheaven_deg=angles.midheaven_deg,
            local_apparent_sidereal_deg=angles.local_apparent_sidereal_deg,
            latitude_deg=observer.latitude_deg,
            true_obliquity_deg=angles.true_obliquity_deg,
        )
        zodiac_mode = settings.zodiac_mode.strip().lower()
        if zodiac_mode == "sidereal":
            if not settings.ayanamsa:
                raise AstronomyDataUnavailable("sidereal houses require an ayanamsa")
            offset = self._ayanamsa_offset(times, settings.ayanamsa)
            dpsi, _ = erfa.nut06a(*times.tt)
            offset = offset + math.degrees(dpsi)
        elif zodiac_mode == "tropical":
            offset = 0.0
        else:
            raise AstronomyDataUnavailable(f"unsupported zodiac mode: {settings.zodiac_mode!r}")

        def shifted(values: Sequence[float]) -> list[float]:
            return [float((value - offset) % 360.0) for value in values]

        artifact = self._kernel_registry.artifact_for_tdb_jd(times.tdb_jd)
        datasets = DatasetVersions(
            kernel_identifier=artifact.identifier,
            kernel_sha256=artifact.sha256,
            leap_seconds=self._leap_seconds_version,
            earth_orientation=eop.version,
            delta_t="not-used-for-modern-utc",
            ayanamsa=(
                f"{AYANAMSA_CATALOG_VERSION};stellar={STELLAR_ANCHOR_CATALOG_VERSION}"
            ),
            time_scale=self._time_scale_version,
            tdb_minus_tt=self._tdb_minus_tt_version,
            earth_orientation_sha256=eop.source_sha256,
            earth_orientation_quality=eop.quality,
            earth_orientation_lower_mjd=eop.lower_mjd,
            earth_orientation_upper_mjd=eop.upper_mjd,
            kernel_mode=(
                "compact-chebyshev-de440"
                if artifact.identifier.startswith("COMPACT-DE440")
                else None
            ),
        )
        receipt = CalculationReceipt.from_request(
            provider=self.identity,
            datasets=datasets,
            settings=settings,
            observer=observer,
            request={
                "instant_utc": instant_utc,
                "system": system,
                "house_conventions_version": HOUSE_CONVENTIONS_VERSION,
            },
        )
        asc_deg = float((angles.ascendant_deg - offset) % 360.0)
        mc_deg = float((angles.midheaven_deg - offset) % 360.0)
        if system.strip().lower() in {"whole_sign", "whole", "w"} and zodiac_mode == "sidereal":
            first_cusp = math.floor(asc_deg / 30.0) * 30.0
            cusps_deg = [float((first_cusp + 30.0 * i) % 360.0) for i in range(12)]
            centers_deg = [float((c + 15.0) % 360.0) for c in cusps_deg]
            boundaries_deg = list(cusps_deg)
        else:
            cusps_deg = shifted(layout.cusps_deg)
            centers_deg = shifted(layout.centers_deg)
            boundaries_deg = shifted(layout.boundaries_deg)

        return {
            "system": layout.system,
            "zodiac_mode": zodiac_mode,
            "ayanamsa_deg": offset,
            "ascendant_deg": asc_deg,
            "midheaven_deg": mc_deg,
            "cusps_deg": cusps_deg,
            "centers_deg": centers_deg,
            "boundaries_deg": boundaries_deg,
            "sidereal_angles": asdict(angles),
            "earth_orientation": asdict(eop),
            "calculation_receipt": receipt.payload(),
            "calculation_receipt_sha256": receipt.sha256(),
        }

    @staticmethod
    def _event_settings(settings: CalculationSettings) -> CalculationSettings:
        flags = {
            flag
            for flag in settings.correction_flags
            if flag.strip().lower() != "refraction_standard"
        }
        flags.add("apparent")
        return CalculationSettings(
            frame="ICRF",
            zodiac_mode="tropical",
            ayanamsa=None,
            node_mode=settings.node_mode,
            correction_flags=tuple(sorted(flags)),
        )

    def _utc_at_jd(self, jd_utc: float) -> datetime | UtcCalendarInstant:
        return self.reverse_julian_day(julian_day=jd_utc)

    def _apparent_altitude(
        self,
        *,
        jd_utc: float,
        observer: Observer,
        body: str,
        settings: CalculationSettings,
        atmosphere: OpticalAtmosphere | None,
        upper_limb_radius_km: float | None = None,
    ) -> float:
        instant = self._utc_at_jd(jd_utc)
        times = self.utc_time_scales(instant)
        event_settings = self._event_settings(settings)
        flags = {flag.strip().lower() for flag in event_settings.correction_flags}
        apply_deflection = "apparent" in flags or "solar_deflection" in flags
        apply_aberration = "apparent" in flags or "aberration" in flags
        apparent, eop = self._apparent_state(
            body=body,
            instant_utc=instant,
            observer=observer,
            times=times,
            apply_deflection=apply_deflection,
            apply_aberration=apply_aberration,
        )
        vector = apparent.apparent_vector_km
        # The topocentric solve already resolved these exact Earth-orientation
        # values; a second lookup must not repeat the same dataset work.
        ut1 = erfa.utcut1(*times.utc, eop.dut1_seconds)
        itrs = self._itrs_matrix(times.tt, ut1, eop) @ np.asarray(vector, dtype=np.float64)
        longitude = math.radians(observer.longitude_deg)
        latitude = math.radians(observer.latitude_deg)
        x, y, z = (float(value) for value in itrs)
        east = -math.sin(longitude) * x + math.cos(longitude) * y
        north = (
            -math.sin(latitude) * math.cos(longitude) * x
            - math.sin(latitude) * math.sin(longitude) * y
            + math.cos(latitude) * z
        )
        up = (
            math.cos(latitude) * math.cos(longitude) * x
            + math.cos(latitude) * math.sin(longitude) * y
            + math.sin(latitude) * z
        )
        altitude = math.degrees(math.atan2(up, math.hypot(east, north)))
        if atmosphere is not None:
            # Horizon atmospheric refraction: empirical standard convention:
            # 33.59 arcminutes (0.5598886 deg) at 1013.25 hPa, 15 C scaled by pressure and temperature
            p = atmosphere.pressure_hpa
            t = atmosphere.temperature_c
            r0 = 0.55988864426 * (p / 1013.25) * (288.15 / (273.15 + t)) if p > 0.0 else 0.0
            altitude += r0
        if upper_limb_radius_km is not None:
            distance_km = float(np.linalg.norm(vector))
            if not 0.0 < upper_limb_radius_km < distance_km:
                raise AstronomyDataUnavailable("invalid angular semidiameter geometry")
            altitude += math.degrees(math.asin(upper_limb_radius_km / distance_km))
        return altitude

    def rise_set(
        self,
        *,
        civil_date: date,
        observer: Observer,
        body: str,
        event: str,
        settings: CalculationSettings,
        atmosphere: OpticalAtmosphere | None = None,
        policy: SolverPolicy | None = None,
        start_jd_utc: float | None = None,
    ) -> Mapping[str, Any]:
        if event.strip().lower() not in {"rise", "set", "transit", "all"}:
            raise AstronomyDataUnavailable(f"unsupported rise/set event: {event!r}")
        start = datetime.combine(civil_date, datetime.min.time(), tzinfo=timezone.utc)
        start_jd = self.julian_day(instant_utc=start)
        if start_jd_utc is not None:
            if not math.isfinite(start_jd_utc):
                raise ValueError("start_jd_utc must be finite")
            start_jd = float(start_jd_utc)
            start = self._utc_at_jd(start_jd)
            if not isinstance(start, datetime) or start.date() != civil_date:
                raise ValueError("start_jd_utc must fall on the same UTC civil date")
        end_jd = start_jd + 1.0
        end = self._utc_at_jd(end_jd)
        use_standard_refraction = "refraction_standard" in {
            flag.strip().lower() for flag in settings.correction_flags
        }
        if use_standard_refraction and atmosphere is None:
            atmosphere = OpticalAtmosphere(1013.25, 15.0, 0.5, 0.55)
        solver_policy = policy or SolverPolicy(
            sample_count=19,
            subdivision_depth=0,
            time_tolerance_days=1e-7,
            max_iterations=40,
        )
        body_key = body.strip().lower().replace(" ", "_")
        refine_transit = event.strip().lower() in {"all", "transit"}
        times = self.utc_time_scales(start)
        artifact = self._kernel_registry.artifact_for_tdb_jd(times.tdb_jd)
        eop_receipts = None if self._earth_orientation_resolver is None else tuple(
            self._resolve_eop(instant) for instant in (start, self._utc_at_jd(start_jd + 0.5), end)
        )
        cache_key = (
            civil_date,
            start_jd,
            end_jd,
            observer,
            body_key,
            settings,
            atmosphere,
            solver_policy,
            refine_transit,
            self.identity,
            artifact.identifier,
            artifact.sha256,
            self._kernel_registry.generation,
            eop_receipts,
            self._earth_orientation_version,
            self._leap_seconds_version,
            self._time_scale_version,
            self._tdb_minus_tt_version,
            self._ayanamsa_data_version,
            id(self._earth_orientation_resolver),
            getattr(self._earth_orientation_resolver, "source_sha256", None),
        )
        with self._lock:
            cached = self._rise_set_cache.get(cache_key)
            if cached is not None:
                self._rise_set_cache.move_to_end(cache_key)
                return self._select_horizon_events(cached, event)
        upper_limb_radius_km = {
            "sun": SUN_RADIUS_KM,
            "moon": MOON_RADIUS_KM,
        }.get(body_key)
        horizon_definition = (
            "apparent_upper_limb_altitude_zero"
            if upper_limb_radius_km is not None
            else "apparent_center_altitude_zero"
        )

        _alt_cache: dict[float, float] = {}

        def altitude(jd: float) -> float:
            cached_alt = _alt_cache.get(jd)
            if cached_alt is not None:
                return cached_alt
            val = self._apparent_altitude(
                jd_utc=jd,
                observer=observer,
                body=body,
                settings=settings,
                atmosphere=atmosphere,
                upper_limb_radius_km=upper_limb_radius_km,
            )
            _alt_cache[jd] = val
            return val

        result = solve_rise_set_transit(
            altitude,
            start_jd,
            end_jd,
            policy=solver_policy,
            refine_transit=refine_transit,
        )
        horizon_events = [
            {
                **asdict(item),
                "instant_utc": self._utc_at_jd(item.jd).isoformat(),
            }
            for item in result.horizon_events
        ]
        payload = {
            "outcome": result.outcome,
            "events": horizon_events,
            "transit": {
                "jd": result.transit_jd,
                "instant_utc": self._utc_at_jd(result.transit_jd).isoformat(),
                "altitude_deg": result.transit_altitude_deg,
            },
            "civil_date_basis": "UTC",
            "search_interval_jd_utc": [start_jd, end_jd],
            "horizon_definition": horizon_definition,
            "semidiameter_model": (
                None
                if upper_limb_radius_km is None
                else {
                    "body_radius_km": upper_limb_radius_km,
                    "angular_radius": "dynamic_asin(radius/distance)",
                }
            ),
            "atmosphere": None if atmosphere is None else asdict(atmosphere),
            "provenance": result.provenance.as_dict(),
        }
        with self._lock:
            self._rise_set_cache[cache_key] = payload
            self._rise_set_cache.move_to_end(cache_key)
            while len(self._rise_set_cache) > 512:
                self._rise_set_cache.popitem(last=False)
        return self._select_horizon_events(payload, event)

    @staticmethod
    def _select_horizon_events(payload: Mapping[str, Any], event: str) -> dict[str, Any]:
        selected = event.strip().lower()
        result = deepcopy(payload)
        result["events"] = [item for item in result["events"] if selected in {"all", item["kind"]}]
        if selected not in {"all", "transit"}:
            result["transit"] = None
        return result

    def _longitude_at_utc_jd(
        self,
        *,
        body: str,
        jd_utc: float,
        settings: CalculationSettings,
    ) -> float:
        event_settings = CalculationSettings(
            frame="ECLIPTIC_OF_DATE",
            zodiac_mode=settings.zodiac_mode,
            ayanamsa=settings.ayanamsa,
            node_mode=settings.node_mode,
            correction_flags=tuple(
                flag
                for flag in settings.correction_flags
                if flag.strip().lower() != "refraction_standard"
            ),
        )
        result = self.planet_positions(
            instant_utc=self._utc_at_jd(jd_utc),
            bodies=(body,),
            observer=None,
            settings=event_settings,
        )
        return float(result["positions"][self._body(body)[1]]["longitude_deg"])

    def solar_longitude_crossing(
        self,
        *,
        target_longitude_deg: float,
        start_utc: datetime,
        end_utc: datetime,
        settings: CalculationSettings,
    ) -> Mapping[str, Any]:
        start_jd = self.julian_day(instant_utc=start_utc)
        end_jd = self.julian_day(instant_utc=end_utc)
        crossings = solve_longitude_crossings(
            lambda jd: self._longitude_at_utc_jd(body="sun", jd_utc=jd, settings=settings),
            start_jd,
            end_jd,
            target_longitude_deg,
        )
        return {
            "crossings": [
                {**asdict(item), "instant_utc": self._utc_at_jd(item.jd).isoformat()}
                for item in crossings
            ]
        }

    def stations(
        self,
        *,
        body: str,
        start_utc: datetime,
        end_utc: datetime,
        settings: CalculationSettings,
    ) -> Sequence[Mapping[str, Any]]:
        start_jd = self.julian_day(instant_utc=start_utc)
        end_jd = self.julian_day(instant_utc=end_utc)
        events = solve_stations(
            lambda jd: self._longitude_at_utc_jd(body=body, jd_utc=jd, settings=settings),
            start_jd,
            end_jd,
        )
        return tuple(
            {**asdict(item), "instant_utc": self._utc_at_jd(item.jd).isoformat()}
            for item in events
        )

    def ingresses(
        self,
        *,
        body: str,
        start_utc: datetime,
        end_utc: datetime,
        settings: CalculationSettings,
    ) -> Sequence[Mapping[str, Any]]:
        start_jd = self.julian_day(instant_utc=start_utc)
        end_jd = self.julian_day(instant_utc=end_utc)
        events = solve_ingresses(
            lambda jd: self._longitude_at_utc_jd(body=body, jd_utc=jd, settings=settings),
            start_jd,
            end_jd,
        )
        return tuple(
            {**asdict(item), "instant_utc": self._utc_at_jd(item.jd).isoformat()}
            for item in events
        )

    def solar_returns(
        self,
        *,
        natal_longitude_deg: float,
        start_utc: datetime,
        end_utc: datetime,
        settings: CalculationSettings,
    ) -> Sequence[Mapping[str, Any]]:
        start_jd = self.julian_day(instant_utc=start_utc)
        end_jd = self.julian_day(instant_utc=end_utc)
        events = solve_solar_returns(
            lambda jd: self._longitude_at_utc_jd(body="sun", jd_utc=jd, settings=settings),
            start_jd,
            end_jd,
            natal_longitude_deg,
        )
        return tuple(
            {**asdict(item), "instant_utc": self._utc_at_jd(item.jd).isoformat()}
            for item in events
        )

    def _geocentric_vector_at_utc_jd(self, body: str, jd_utc: float) -> Sequence[float]:
        instant = self._utc_at_jd(jd_utc)
        times = self.utc_time_scales(instant)
        state = self.geocentric_state_at_tdb(
            body=body,
            tdb=times.tdb,
            kernel_year=instant.year,
        )
        return state.position_km

    def _syzygies(
        self,
        *,
        start_jd: float,
        end_jd: float,
        target_deg: float,
    ) -> Sequence[float]:
        def elongation(jd: float) -> float:
            sun = self._geocentric_vector_at_utc_jd("sun", jd)
            moon = self._geocentric_vector_at_utc_jd("moon", jd)
            frame = self._celestial_matrix(
                "ECLIPTIC_OF_DATE", self.utc_time_scales(self._utc_at_jd(jd)).tt
            )
            sun_lon = self._spherical(frame @ np.asarray(sun))[0]
            moon_lon = self._spherical(frame @ np.asarray(moon))[0]
            return (moon_lon - sun_lon) % 360.0

        policy = SolverPolicy(sample_count=max(97, int((end_jd - start_jd) * 8) + 1))
        return tuple(
            item.jd
            for item in solve_longitude_crossings(
                elongation,
                start_jd,
                end_jd,
                target_deg,
                policy=policy,
                event_kind="syzygy",
            )
        )

    def solar_eclipses(
        self,
        *,
        start_utc: datetime,
        end_utc: datetime,
        settings: CalculationSettings,
    ) -> Sequence[Mapping[str, Any]]:
        del settings
        start_jd = self.julian_day(instant_utc=start_utc)
        end_jd = self.julian_day(instant_utc=end_utc)
        results = []
        for conjunction in self._syzygies(start_jd=start_jd, end_jd=end_jd, target_deg=0.0):
            left = max(start_jd, conjunction - 1.0)
            right = min(end_jd, conjunction + 1.0)
            result = solve_solar_eclipse_candidate(
                lambda jd: self._geocentric_vector_at_utc_jd("sun", jd),
                lambda jd: self._geocentric_vector_at_utc_jd("moon", jd),
                left,
                right,
                apparent_vector_frame="geocentric-ICRF geometric-disc candidate",
            )
            if result.status == "found":
                results.append(
                    {
                        **asdict(result),
                        "maximum_utc": self._utc_at_jd(result.maximum_jd).isoformat(),
                    }
                )
        return tuple(results)

    def lunar_eclipses(
        self,
        *,
        start_utc: datetime,
        end_utc: datetime,
        settings: CalculationSettings,
    ) -> Sequence[Mapping[str, Any]]:
        del settings
        start_jd = self.julian_day(instant_utc=start_utc)
        end_jd = self.julian_day(instant_utc=end_utc)
        results = []
        for opposition in self._syzygies(start_jd=start_jd, end_jd=end_jd, target_deg=180.0):
            left = max(start_jd, opposition - 1.0)
            right = min(end_jd, opposition + 1.0)
            result = solve_lunar_eclipse_candidate(
                lambda jd: self._geocentric_vector_at_utc_jd("sun", jd),
                lambda jd: self._geocentric_vector_at_utc_jd("moon", jd),
                left,
                right,
                apparent_vector_frame="geocentric-ICRF physical-shadow candidate",
            )
            if result.status == "found":
                results.append(
                    {
                        **asdict(result),
                        "maximum_utc": self._utc_at_jd(result.maximum_jd).isoformat(),
                    }
                )
        return tuple(results)
