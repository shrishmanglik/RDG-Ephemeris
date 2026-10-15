"""Canonical calculation receipts for reproducible astronomy requests."""

from __future__ import annotations

import hashlib
import json
import math
from dataclasses import asdict, dataclass, is_dataclass
from datetime import date, datetime, timezone
from enum import Enum
from pathlib import Path
from typing import Any, Mapping

from .contracts import CalculationSettings, DatasetVersions, Observer, ProviderIdentity


def _canonical_value(value: Any) -> Any:
    if is_dataclass(value):
        return _canonical_value(asdict(value))
    if isinstance(value, Enum):
        return _canonical_value(value.value)
    if isinstance(value, datetime):
        if value.tzinfo is None or value.utcoffset() is None:
            raise ValueError("receipt datetimes must be timezone-aware")
        return value.astimezone(timezone.utc).isoformat(timespec="microseconds").replace("+00:00", "Z")
    if isinstance(value, date):
        return value.isoformat()
    if isinstance(value, Path):
        return value.as_posix()
    if isinstance(value, Mapping):
        return {str(key): _canonical_value(value[key]) for key in sorted(value, key=lambda item: str(item))}
    if isinstance(value, (list, tuple)):
        return [_canonical_value(item) for item in value]
    if isinstance(value, (set, frozenset)):
        return sorted((_canonical_value(item) for item in value), key=lambda item: json.dumps(item, sort_keys=True))
    if isinstance(value, float):
        if not math.isfinite(value):
            raise ValueError("receipt values must not contain NaN or infinity")
        return value
    if value is None or isinstance(value, (str, int, bool)):
        return value
    raise TypeError(f"unsupported receipt value: {type(value).__name__}")


def canonical_json_bytes(value: Any) -> bytes:
    return json.dumps(
        _canonical_value(value),
        ensure_ascii=True,
        allow_nan=False,
        separators=(",", ":"),
        sort_keys=True,
    ).encode("ascii")


def canonical_hash(value: Any) -> str:
    return hashlib.sha256(canonical_json_bytes(value)).hexdigest()


@dataclass(frozen=True)
class CalculationReceipt:
    engine: str
    semantic_version: str
    kernel_identifier: str
    kernel_sha256: str
    leap_seconds_version: str
    earth_orientation_version: str
    delta_t_version: str
    ayanamsa_data_version: str
    time_scale_version: str
    tdb_minus_tt_version: str
    frame: str
    observer: Observer | None
    zodiac_mode: str
    ayanamsa: str | None
    node_mode: str
    correction_flags: tuple[str, ...]
    request_sha256: str
    earth_orientation_sha256: str | None = None
    earth_orientation_quality: str | None = None
    earth_orientation_lower_mjd: float | None = None
    earth_orientation_upper_mjd: float | None = None
    kernel_mode: str | None = None

    @classmethod
    def from_request(
        cls,
        *,
        provider: ProviderIdentity,
        datasets: DatasetVersions,
        settings: CalculationSettings,
        observer: Observer | None,
        request: Mapping[str, Any],
    ) -> "CalculationReceipt":
        return cls(
            engine=provider.engine,
            semantic_version=provider.semantic_version,
            kernel_identifier=datasets.kernel_identifier,
            kernel_sha256=datasets.kernel_sha256.lower(),
            leap_seconds_version=datasets.leap_seconds,
            earth_orientation_version=datasets.earth_orientation,
            delta_t_version=datasets.delta_t,
            ayanamsa_data_version=datasets.ayanamsa,
            time_scale_version=datasets.time_scale,
            tdb_minus_tt_version=datasets.tdb_minus_tt,
            frame=settings.frame,
            observer=observer,
            zodiac_mode=settings.zodiac_mode,
            ayanamsa=settings.ayanamsa,
            node_mode=settings.node_mode,
            correction_flags=tuple(sorted(set(settings.correction_flags))),
            request_sha256=canonical_hash(request),
            earth_orientation_sha256=(
                datasets.earth_orientation_sha256.lower()
                if datasets.earth_orientation_sha256
                else None
            ),
            earth_orientation_quality=datasets.earth_orientation_quality,
            earth_orientation_lower_mjd=datasets.earth_orientation_lower_mjd,
            earth_orientation_upper_mjd=datasets.earth_orientation_upper_mjd,
            kernel_mode=datasets.kernel_mode,
        )

    def payload(self) -> dict[str, Any]:
        return _canonical_value(self)

    def bytes(self) -> bytes:
        return canonical_json_bytes(self)

    def sha256(self) -> str:
        return hashlib.sha256(self.bytes()).hexdigest()
