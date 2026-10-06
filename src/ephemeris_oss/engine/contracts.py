"""Provider-neutral contracts for deterministic astronomical calculations."""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import date, datetime
from typing import TYPE_CHECKING, Any, Mapping, Sequence

if TYPE_CHECKING:
    from .earth_orientation import UtcCalendarInstant


class AstronomyDataUnavailable(RuntimeError):
    """Required kernel or convention data is unavailable or unverifiable."""


@dataclass(frozen=True)
class Observer:
    latitude_deg: float
    longitude_deg: float
    altitude_m: float = 0.0

    def __post_init__(self) -> None:
        if not -90.0 <= self.latitude_deg <= 90.0:
            raise ValueError("latitude_deg must be within [-90, 90]")
        if not -180.0 <= self.longitude_deg <= 180.0:
            raise ValueError("longitude_deg must be within [-180, 180]")


@dataclass(frozen=True)
class ProviderIdentity:
    engine: str
    semantic_version: str


@dataclass(frozen=True)
class DatasetVersions:
    kernel_identifier: str
    kernel_sha256: str
    leap_seconds: str
    earth_orientation: str
    delta_t: str
    ayanamsa: str
    time_scale: str = "unspecified"
    tdb_minus_tt: str = "unspecified"
    earth_orientation_sha256: str | None = None
    earth_orientation_quality: str | None = None
    earth_orientation_lower_mjd: float | None = None
    earth_orientation_upper_mjd: float | None = None


@dataclass(frozen=True)
class CalculationSettings:
    frame: str
    zodiac_mode: str
    ayanamsa: str | None
    node_mode: str
    correction_flags: tuple[str, ...] = ()


class AstronomyProvider(ABC):
    """Complete dependency boundary required by the Jyotish calculation layer."""

    @property
    @abstractmethod
    def identity(self) -> ProviderIdentity:
        raise NotImplementedError

    @abstractmethod
    def planet_positions(
        self,
        *,
        instant_utc: datetime | UtcCalendarInstant,
        bodies: Sequence[str],
        observer: Observer | None,
        settings: CalculationSettings,
    ) -> Mapping[str, Any]:
        raise NotImplementedError

    @abstractmethod
    def ayanamsa(
        self, *, instant_utc: datetime | UtcCalendarInstant, convention: str
    ) -> float:
        raise NotImplementedError

    @abstractmethod
    def houses(
        self,
        *,
        instant_utc: datetime | UtcCalendarInstant,
        observer: Observer,
        system: str,
        settings: CalculationSettings,
    ) -> Mapping[str, Any]:
        raise NotImplementedError

    @abstractmethod
    def julian_day(self, *, instant_utc: datetime | UtcCalendarInstant) -> float:
        raise NotImplementedError

    @abstractmethod
    def reverse_julian_day(
        self, *, julian_day: float | tuple[float, float]
    ) -> datetime | UtcCalendarInstant:
        raise NotImplementedError

    @abstractmethod
    def rise_set(
        self,
        *,
        civil_date: date,
        observer: Observer,
        body: str,
        event: str,
        settings: CalculationSettings,
    ) -> Mapping[str, Any]:
        raise NotImplementedError

    @abstractmethod
    def solar_longitude_crossing(
        self,
        *,
        target_longitude_deg: float,
        start_utc: datetime,
        end_utc: datetime,
        settings: CalculationSettings,
    ) -> Mapping[str, Any]:
        raise NotImplementedError

    @abstractmethod
    def stations(
        self,
        *,
        body: str,
        start_utc: datetime,
        end_utc: datetime,
        settings: CalculationSettings,
    ) -> Sequence[Mapping[str, Any]]:
        raise NotImplementedError

    @abstractmethod
    def ingresses(
        self,
        *,
        body: str,
        start_utc: datetime,
        end_utc: datetime,
        settings: CalculationSettings,
    ) -> Sequence[Mapping[str, Any]]:
        raise NotImplementedError

    @abstractmethod
    def solar_returns(
        self,
        *,
        natal_longitude_deg: float,
        start_utc: datetime,
        end_utc: datetime,
        settings: CalculationSettings,
    ) -> Sequence[Mapping[str, Any]]:
        raise NotImplementedError

    @abstractmethod
    def solar_eclipses(
        self,
        *,
        start_utc: datetime,
        end_utc: datetime,
        settings: CalculationSettings,
    ) -> Sequence[Mapping[str, Any]]:
        raise NotImplementedError

    @abstractmethod
    def lunar_eclipses(
        self,
        *,
        start_utc: datetime,
        end_utc: datetime,
        settings: CalculationSettings,
    ) -> Sequence[Mapping[str, Any]]:
        raise NotImplementedError

    @abstractmethod
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
        raise NotImplementedError
