"""The public engine: one object that owns kernels, Earth orientation and time-scale policy."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime
from pathlib import Path
from typing import Any, Callable, Generic, Mapping, Sequence, TypeVar, Union

import erfa

from . import kernels as _kernels
from ._version import __version__
from .engine.contracts import AstronomyDataUnavailable, CalculationSettings, Observer
from .engine.conventions import AYANAMSA_CATALOG, AYANAMSA_CATALOG_VERSION, ayanamsa_degrees
from .engine.earth_orientation import IersFinals2000A, UtcCalendarInstant
from .engine.kernel_registry import KernelArtifact, KernelRegistry
from .engine.numerical_provider import EarthOrientationParameters, JplErfaAstronomyProvider

T = TypeVar("T")
Instant = Union[datetime, UtcCalendarInstant]

# UTC is accepted only where the leap-second table is known. The window ends at
# the last date this release vouches for; later instants are refused, not
# extrapolated, until a release extends it.
UTC_VALID_FROM = date(1960, 1, 1)
UTC_VALID_THROUGH = date(2026, 12, 31)


class EphemerisError(ValueError):
    """Bad input, a missing or unverified data file, or a policy refusal."""


@dataclass(frozen=True)
class Undefined:
    """A quantity that has no value for this geometry, with the reason."""

    reason: str


@dataclass(frozen=True)
class Houses:
    system: str
    cusps_deg: tuple[float, ...]
    ascendant_deg: float
    midheaven_deg: float


@dataclass(frozen=True)
class Result(Generic[T]):
    """A computed value and the receipt that says exactly how it was computed."""

    value: T
    receipt: Mapping[str, Any]
    receipt_sha256: str


@dataclass(frozen=True)
class EarthOrientation:
    """Fixed Earth-orientation values, for callers who supply their own (tests, archival work)."""

    dut1_seconds: float
    xp_arcsec: float
    yp_arcsec: float
    version: str

    def __call__(self, _instant: Instant) -> EarthOrientationParameters:
        return EarthOrientationParameters(
            dut1_seconds=self.dut1_seconds, xp_arcsec=self.xp_arcsec, yp_arcsec=self.yp_arcsec,
            source="caller-supplied", version=self.version,
        )


def _error(error: Exception) -> EphemerisError:
    return error if isinstance(error, EphemerisError) else EphemerisError(str(error))


class Engine:
    """Positions, ayanamsas, houses, nodes and rise/set from JPL kernels, each with a receipt."""

    def __init__(self, provider: JplErfaAstronomyProvider) -> None:
        self._provider = provider

    @classmethod
    def load(
        cls,
        kernels: str | Mapping[str, str | Path] = "auto",
        eop: str | EarthOrientation | Callable[[Instant], Any] | None = "auto",
        cache_dir: str | Path | None = None,
    ) -> "Engine":
        """Open and verify the data files.

        ``kernels="auto"`` uses the verified files in the user cache (run
        ``ephemeris-oss kernels fetch --verify`` first); a mapping of kernel id
        to path uses those files, each checked against its pinned SHA-256.
        ``eop="auto"`` uses ``finals2000A.all`` from the cache when present;
        without it, anything that needs UT1 (houses, topocentric places,
        rise/set) raises :class:`EphemerisError` rather than assuming zero.
        """

        directory = _kernels.cache_dir(cache_dir)
        if kernels == "compact":
            from .compact_kernel import (
                COMPACT_KERNEL_ID,
                COMPACT_KERNEL_PATH,
                COMPACT_KERNEL_SHA256,
            )

            if not COMPACT_KERNEL_PATH.is_file():
                raise EphemerisError(f"{COMPACT_KERNEL_ID}: {COMPACT_KERNEL_PATH} does not exist")
            actual = _kernels.sha256_file(COMPACT_KERNEL_PATH)
            if actual != COMPACT_KERNEL_SHA256:
                raise EphemerisError(
                    f"{COMPACT_KERNEL_ID}: SHA-256 mismatch for {COMPACT_KERNEL_PATH}: "
                    f"expected {COMPACT_KERNEL_SHA256}, got {actual}"
                )
            artifacts: dict[str, KernelArtifact] = {
                COMPACT_KERNEL_ID: KernelArtifact(
                    COMPACT_KERNEL_ID, COMPACT_KERNEL_PATH, actual
                )
            }
        else:
            if kernels == "auto":
                chosen = {
                    identifier: _kernels.cached_path(spec, directory)
                    for identifier, spec in _kernels.KERNELS.items()
                    if _kernels.cached_path(spec, directory).exists()
                }
                if "DE440" not in chosen:
                    raise EphemerisError(
                        f"no DE440 kernel in {directory}; run `ephemeris-oss kernels fetch --verify`"
                    )
            elif isinstance(kernels, Mapping):
                chosen = {str(key): Path(value) for key, value in kernels.items()}
            else:
                raise EphemerisError(
                    "kernels must be 'auto', 'compact', or a mapping of kernel id to path"
                )
            artifacts = {}
            for identifier, path in chosen.items():
                spec = _kernels.KERNELS.get(identifier)
                if spec is None:
                    raise EphemerisError(
                        f"unknown kernel id {identifier!r}; known: {sorted(_kernels.KERNELS)}"
                    )
                if not path.is_file():
                    raise EphemerisError(f"{identifier}: {path} does not exist")
                actual = _kernels.sha256_file(path)
                if actual != spec.sha256:
                    raise EphemerisError(
                        f"{identifier}: SHA-256 mismatch for {path}: expected {spec.sha256}, got {actual}"
                    )
                artifacts[identifier] = KernelArtifact(identifier, path, actual)

        resolver, eop_version = cls._eop_resolver(eop, directory)
        provider = JplErfaAstronomyProvider(
            kernel_registry=KernelRegistry(artifacts),
            leap_seconds_version=f"erfa-{erfa.__version__}",
            earth_orientation_version=eop_version,
            time_scale_version=f"ephemeris-oss-{__version__}-utc-{UTC_VALID_FROM}-{UTC_VALID_THROUGH}",
            tdb_minus_tt_version=f"erfa-dtdb-{erfa.__version__}",
            time_scale_valid_from_utc=UTC_VALID_FROM,
            time_scale_valid_through_utc=UTC_VALID_THROUGH,
            ayanamsa_data_version=AYANAMSA_CATALOG_VERSION,
            earth_orientation_resolver=resolver,
        )
        return cls(provider)

    @staticmethod
    def _eop_resolver(eop: Any, directory: Path) -> tuple[Callable[[Instant], Any] | None, str]:
        if eop is None:
            return None, "none"
        if isinstance(eop, EarthOrientation):
            return eop, eop.version
        if eop == "auto":
            finals = directory / "finals2000A.all"
            if not finals.is_file():
                return None, "none"
            digest = _kernels.sha256_file(finals)
            snapshot = IersFinals2000A.from_file(finals, expected_sha256=digest, version=f"iers-finals2000a-sha256-{digest[:12]}")
            return snapshot, f"iers-finals2000a-sha256-{digest}"
        if callable(eop):
            return eop, str(getattr(eop, "version", "caller-supplied"))
        raise EphemerisError("eop must be 'auto', None, an EarthOrientation or a callable")

    def __enter__(self) -> "Engine":
        return self

    def __exit__(self, *_exc: object) -> None:
        self.close()

    def close(self) -> None:
        self._provider.close()

    @staticmethod
    def _settings(ayanamsa: str | None, frame: str = "ecliptic-of-date", node_mode: str = "mean",
                  apparent: bool = True) -> CalculationSettings:
        return CalculationSettings(
            frame=frame.upper().replace("-", "_"),
            zodiac_mode="sidereal" if ayanamsa else "tropical",
            ayanamsa=ayanamsa,
            node_mode=node_mode,
            correction_flags=("apparent",) if apparent else ("geometric",),
        )

    @staticmethod
    def _result(raw: Mapping[str, Any], value: Any) -> Result[Any]:
        return Result(value=value, receipt=raw["calculation_receipt"], receipt_sha256=raw["calculation_receipt_sha256"])

    def positions(
        self,
        t: Instant,
        bodies: Sequence[str],
        *,
        frame: str = "ecliptic-of-date",
        apparent: bool = True,
        ayanamsa: str | None = None,
        observer: tuple[float, float, float] | None = None,
    ) -> Result[dict[str, dict[str, Any]]]:
        """Geocentric (or topocentric, with ``observer=(lat, lon, height_m)``) places of each body."""

        try:
            raw = self._provider.planet_positions(
                instant_utc=t, bodies=tuple(bodies),
                observer=None if observer is None else Observer(observer[0], observer[1], observer[2]),
                settings=self._settings(ayanamsa, frame, apparent=apparent),
            )
        except (AstronomyDataUnavailable, ValueError) as error:
            raise _error(error) from error
        positions = raw["positions"]
        value = {body.strip().lower(): dict(positions[self._key(positions, body)]) for body in bodies}
        return self._result(raw, value)

    @staticmethod
    def _key(positions: Mapping[str, Any], body: str) -> str:
        for key in positions:
            if key.lower() == body.strip().lower():
                return key
        raise EphemerisError(f"engine returned no position for {body!r}")

    def positions_tt(
        self, jd_tt: float, bodies: Sequence[str]
    ) -> Result[dict[str, dict[str, Any]]]:
        """Apparent geocentric true-ecliptic positions at an explicit TT instant.

        This is the entry point measured over 1800..2100. It does not infer
        civil time, UTC, UT1 or Earth orientation. Nodes use their separately
        declared definition interface rather than this physical-body method.
        """
        normalized_bodies = tuple(body.strip().lower() for body in bodies)
        try:
            raw = self._provider.planet_positions_tt(jd_tt=jd_tt, bodies=normalized_bodies)
        except (AstronomyDataUnavailable, ValueError) as error:
            raise _error(error) from error
        positions = raw["positions"]
        value = {body: dict(positions[self._key(positions, body)]) for body in normalized_bodies}
        targets = {body: self._provider._body(body)[0] for body in normalized_bodies}
        request = {"jd_tt": raw["jd_tt"], "bodies": list(normalized_bodies), "targets": targets}
        receipt: dict[str, Any] = {
            "package": __version__, "time_scale": "TT", "jd_tt": raw["jd_tt"],
            "jd_tdb": raw["jd_tdb"], "utc_inferred": False,
            "frame": raw["frame"], "kernel_sha256": raw["kernel_sha256"],
            "apparent_model": "solar-only finite-distance; opaque solar photosphere",
            "bodies": request["bodies"], "targets": targets,
            "request_sha256": _digest(request), "result_sha256": _digest(value),
        }
        if "kernel_mode" in raw:
            receipt["kernel_mode"] = raw["kernel_mode"]
        return Result(value=value, receipt=receipt, receipt_sha256=_digest(receipt))

    def ayanamsa(self, t: Instant, system: str = "lahiri", mode: str = "mean") -> Result[float]:
        """The named ayanamsa at ``t``; ``mode="true"`` adds nutation in longitude."""

        if mode not in {"mean", "true"}:
            raise EphemerisError("mode must be 'mean' or 'true'")
        try:
            times = self._provider.utc_time_scales(t)
            definition = AYANAMSA_CATALOG.get(system)
            if definition is not None and definition.model == "star_anchor":
                # Star-anchored systems need the star's apparent place, which the provider computes.
                if mode == "true":
                    raise EphemerisError(f"{system} is star-anchored; only its provider realisation is offered")
                value = self._provider.ayanamsa(instant_utc=t, convention=system)
            else:
                value = ayanamsa_degrees(times.tt_jd, system, true=mode == "true")
        except (AstronomyDataUnavailable, ValueError) as error:
            raise _error(error) from error
        receipt = {"system": system, "mode": mode, "tt_jd": times.tt_jd, "package": __version__}
        return Result(value=float(value), receipt=receipt, receipt_sha256=_digest(receipt))

    def houses(self, t: Instant, lat: float, lon: float, system: str = "placidus",
               ayanamsa: str | None = None) -> Result[Houses | Undefined]:
        """House cusps, or :class:`Undefined` with the reason where the system has no solution."""

        try:
            raw = self._provider.houses(
                instant_utc=t, observer=Observer(lat, lon), system=system,
                settings=self._settings(ayanamsa),
            )
        except AstronomyDataUnavailable as error:
            message = str(error)
            if "undefined" in message.lower() or "singular" in message.lower() or "circumpolar" in message.lower():
                receipt = {"system": system, "lat": lat, "lon": lon, "undefined": message, "package": __version__}
                return Result(value=Undefined(message), receipt=receipt, receipt_sha256=_digest(receipt))
            raise _error(error) from error
        except ValueError as error:
            raise _error(error) from error
        value = Houses(raw["system"], tuple(raw["cusps_deg"]), raw["ascendant_deg"], raw["midheaven_deg"])
        return self._result(raw, value)

    def nodes(self, t: Instant, kind: str = "mean", ayanamsa: str | None = None) -> Result[float]:
        """Longitude of the Moon's ascending node: ``mean`` (Meeus ch. 47) or ``true`` (osculating)."""

        if kind not in {"mean", "true"}:
            raise EphemerisError("kind must be 'mean' or 'true'")
        try:
            raw = self._provider.planet_positions(
                instant_utc=t, bodies=("rahu",), observer=None,
                settings=self._settings(ayanamsa, node_mode=kind),
            )
        except (AstronomyDataUnavailable, ValueError) as error:
            raise _error(error) from error
        entry = raw["positions"][self._key(raw["positions"], "rahu")]
        return self._result(raw, float(entry["longitude_deg"]))

    def rise_set(self, day: date, lat: float, lon: float, body: str = "sun", event: str = "rise",
                 height_m: float = 0.0) -> Result[dict[str, Any]]:
        """Rise, set or transit on a UTC civil day. ``outcome`` says when an event does not occur."""

        try:
            raw = self._provider.rise_set(
                civil_date=day, observer=Observer(lat, lon, height_m), body=body, event=event,
                settings=self._settings(None),
            )
        except (AstronomyDataUnavailable, ValueError) as error:
            raise _error(error) from error
        value = dict(raw)
        provenance = value.pop("provenance", {})
        receipt = {"rise_set": provenance, "package": __version__}
        return Result(value=value, receipt=receipt, receipt_sha256=_digest(receipt))


def _digest(receipt: Mapping[str, Any]) -> str:
    from .engine.receipt import canonical_hash

    return canonical_hash(receipt)
