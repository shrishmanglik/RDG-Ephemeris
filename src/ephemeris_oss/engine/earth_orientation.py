"""Versioned IERS Earth-orientation and civil-time policy.

The operational EOP source is the IERS ``finals.all (IAU2000)`` product:
https://datacenter.iers.org/data/latestVersion/finals.all.iau2000.txt

The fixed-width layout is published by the IERS Rapid Service/USNO.  Bulletin
B fields are preferred when present; Bulletin A observed/predicted fields are
used otherwise.  Data are never extrapolated.  This module deliberately keeps
historical Delta-T estimates separate from UTC: before atomic UTC, or beyond a
versioned leap-second table, callers must explicitly identify the input as
proleptic UT1 rather than silently treating civil time as UTC.
"""

from __future__ import annotations

import hashlib
import json
import math
import re
import warnings
from bisect import bisect_left
from dataclasses import dataclass
from datetime import datetime, timezone
from enum import Enum
from pathlib import Path
from typing import Iterable

import erfa

from .contracts import AstronomyDataUnavailable


class EopQuality(str, Enum):
    FINAL = "final"
    OBSERVED = "observed"
    PREDICTED = "predicted"


@dataclass(frozen=True)
class EopRecord:
    mjd_utc: float
    dut1_seconds: float
    xp_arcsec: float
    yp_arcsec: float
    dx_mas: float | None
    dy_mas: float | None
    quality: EopQuality


@dataclass(frozen=True)
class ResolvedEarthOrientation:
    dut1_seconds: float
    xp_arcsec: float
    yp_arcsec: float
    dx_mas: float | None
    dy_mas: float | None
    quality: EopQuality
    version: str
    source_sha256: str
    lower_mjd: float
    upper_mjd: float


@dataclass(frozen=True)
class UtcCalendarInstant:
    """UTC calendar instant, including a standards-valid ``23:59:60``.

    Python's :class:`datetime` cannot represent a leap second.  This type
    validates the calendar fields through ERFA/SOFA and preserves the UTC
    quasi-Julian-date representation required around an insertion boundary.
    """

    year: int
    month: int
    day: int
    hour: int
    minute: int
    second: float

    def __post_init__(self) -> None:
        if not math.isfinite(self.second):
            raise ValueError("UTC second must be finite")
        try:
            with warnings.catch_warnings():
                warnings.simplefilter("error", erfa.ErfaWarning)
                erfa.dtf2d(
                    "UTC",
                    self.year,
                    self.month,
                    self.day,
                    self.hour,
                    self.minute,
                    self.second,
                )
        except (ValueError, erfa.ErfaError, erfa.ErfaWarning) as error:
            raise ValueError("invalid UTC calendar instant") from error

    @classmethod
    def from_datetime(cls, instant: datetime) -> "UtcCalendarInstant":
        if instant.tzinfo is None or instant.utcoffset() is None:
            raise ValueError("instant must be timezone-aware")
        value = instant.astimezone(timezone.utc)
        return cls(
            value.year,
            value.month,
            value.day,
            value.hour,
            value.minute,
            value.second + value.microsecond / 1_000_000.0,
        )

    def utc_jd(self) -> tuple[float, float]:
        first, second = erfa.dtf2d(
            "UTC",
            self.year,
            self.month,
            self.day,
            self.hour,
            self.minute,
            self.second,
        )
        return float(first), float(second)

    def tai_minus_utc_seconds(self) -> float:
        return float(erfa.dat(self.year, self.month, self.day, 0.0))

    def isoformat(self) -> str:
        """Return an ISO-like UTC representation that can preserve ``:60``."""

        whole_seconds = int(self.second)
        fraction = self.second - whole_seconds
        suffix = ""
        if fraction:
            suffix = f"{fraction:.9f}"[1:].rstrip("0")
        return (
            f"{self.year:04d}-{self.month:02d}-{self.day:02d}T"
            f"{self.hour:02d}:{self.minute:02d}:{whole_seconds:02d}{suffix}Z"
        )


def _field(line: str, start: int, end: int) -> str:
    return line[start - 1 : end].strip()


def _optional_float(line: str, start: int, end: int) -> float | None:
    value = _field(line, start, end)
    return float(value) if value else None


def parse_finals2000a_line(line: str) -> EopRecord | None:
    """Parse one IERS finals2000A fixed-width record.

    Column numbers follow the official finals2000A format (one-based).  Empty
    trailing prediction rows are ignored rather than converted to zero.
    """

    if len(line) < 68:
        return None
    try:
        mjd = float(_field(line, 8, 15))
    except ValueError:
        return None

    # Bulletin B combined/final values occupy columns 135 onward.  They are
    # absent for recent observed and predicted Bulletin A rows.
    b_x = _optional_float(line, 135, 144)
    b_y = _optional_float(line, 145, 154)
    b_ut1 = _optional_float(line, 155, 165)
    if b_x is not None and b_y is not None and b_ut1 is not None:
        return EopRecord(
            mjd_utc=mjd,
            dut1_seconds=b_ut1,
            xp_arcsec=b_x,
            yp_arcsec=b_y,
            dx_mas=_optional_float(line, 166, 175),
            dy_mas=_optional_float(line, 176, 185),
            quality=EopQuality.FINAL,
        )

    x = _optional_float(line, 19, 27)
    y = _optional_float(line, 38, 46)
    dut1 = _optional_float(line, 59, 68)
    if x is None or y is None or dut1 is None:
        return None
    flag = _field(line, 58, 58).upper()
    quality = EopQuality.PREDICTED if flag == "P" else EopQuality.OBSERVED
    return EopRecord(
        mjd_utc=mjd,
        dut1_seconds=dut1,
        xp_arcsec=x,
        yp_arcsec=y,
        dx_mas=_optional_float(line, 98, 106),
        dy_mas=_optional_float(line, 117, 125),
        quality=quality,
    )


class IersFinals2000A:
    """Checksum-gated, interpolating EOP snapshot.

    Linear interpolation is appropriate for daily polar-motion/CIP samples.
    DUT1 is first converted to continuous UT1-TAI, interpolated there, and
    converted back with the leap-second table at the requested instant.
    Interpolation across a gap larger than ``max_gap_days`` and every form of
    extrapolation fail closed.
    """

    def __init__(
        self,
        records: Iterable[EopRecord],
        *,
        version: str,
        source_sha256: str,
        allow_predictions: bool = False,
        max_gap_days: float = 1.5,
    ) -> None:
        ordered = tuple(sorted(records, key=lambda record: record.mjd_utc))
        if len(ordered) < 2:
            raise AstronomyDataUnavailable("IERS EOP snapshot has fewer than two records")
        if any(b.mjd_utc <= a.mjd_utc for a, b in zip(ordered, ordered[1:])):
            raise AstronomyDataUnavailable("IERS EOP snapshot contains duplicate MJD records")
        self._records = ordered
        self._mjds = tuple(record.mjd_utc for record in ordered)
        self.version = version
        self.source_sha256 = source_sha256.lower()
        self.allow_predictions = allow_predictions
        self.max_gap_days = max_gap_days

    @classmethod
    def from_file(
        cls,
        path: str | Path,
        *,
        expected_sha256: str,
        version: str,
        allow_predictions: bool = False,
        max_gap_days: float = 1.5,
    ) -> "IersFinals2000A":
        source = Path(path)
        digest = hashlib.sha256(source.read_bytes()).hexdigest()
        if digest.lower() != expected_sha256.lower():
            raise AstronomyDataUnavailable(
                f"IERS EOP checksum mismatch for {source.name}: expected "
                f"{expected_sha256.lower()}, got {digest.lower()}"
            )
        records = [
            record
            for line in source.read_text(encoding="ascii").splitlines()
            if (record := parse_finals2000a_line(line)) is not None
        ]
        return cls(
            records,
            version=version,
            source_sha256=digest,
            allow_predictions=allow_predictions,
            max_gap_days=max_gap_days,
        )

    @classmethod
    def from_release_root(
        cls,
        release_root: str | Path,
        *,
        allow_predictions: bool = False,
        max_gap_days: float = 1.5,
    ) -> "IersFinals2000A":
        """Load only the checksum-bound generation selected by ``active.json``."""

        root = Path(release_root).resolve()
        pointer_path = root / "active.json"
        try:
            pointer = json.loads(pointer_path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as error:
            raise AstronomyDataUnavailable("IERS EOP active pointer is unavailable") from error
        if pointer.get("schema_version") != "iers-eop-active-pointer-v1":
            raise AstronomyDataUnavailable("IERS EOP active pointer schema is unsupported")
        digest = str(pointer.get("generation_sha256", "")).lower()
        if re.fullmatch(r"[0-9a-f]{64}", digest) is None:
            raise AstronomyDataUnavailable("IERS EOP active generation checksum is invalid")
        expected_payload = f"releases/{digest}/finals2000A.all"
        expected_manifest = f"releases/{digest}/manifest.json"
        if pointer.get("payload") != expected_payload or pointer.get("manifest") != expected_manifest:
            raise AstronomyDataUnavailable("IERS EOP active pointer paths are not canonical")

        manifest_path = root / expected_manifest
        try:
            manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as error:
            raise AstronomyDataUnavailable("IERS EOP release manifest is unavailable") from error
        if manifest.get("schema_version") != "iers-eop-manifest-v2":
            raise AstronomyDataUnavailable("IERS EOP release manifest schema is unsupported")
        if manifest.get("sha256") != digest:
            raise AstronomyDataUnavailable("IERS EOP release manifest checksum does not match")
        version = f"iers-finals2000a@{manifest.get('retrieved_at_utc', digest[:16])}"
        snapshot = cls.from_file(
            root / expected_payload,
            expected_sha256=digest,
            version=version,
            allow_predictions=allow_predictions,
            max_gap_days=max_gap_days,
        )
        payload_path = root / expected_payload
        if manifest.get("byte_count") != payload_path.stat().st_size:
            raise AstronomyDataUnavailable("IERS EOP release manifest byte count does not match")
        records = snapshot._records
        quality_counts = {
            quality.value: sum(record.quality is quality for record in records)
            for quality in EopQuality
            if any(record.quality is quality for record in records)
        }
        latest_non_predicted = max(
            record.mjd_utc
            for record in records
            if record.quality is not EopQuality.PREDICTED
        )
        semantic_fields = {
            "record_count": len(records),
            "first_mjd_utc": records[0].mjd_utc,
            "last_mjd_utc": records[-1].mjd_utc,
            "latest_non_predicted_mjd_utc": latest_non_predicted,
            "quality_counts": quality_counts,
        }
        for field, expected in semantic_fields.items():
            if manifest.get(field) != expected:
                raise AstronomyDataUnavailable(
                    f"IERS EOP release manifest {field} does not match payload"
                )
        return snapshot

    @staticmethod
    def _mjd(instant_utc: datetime | UtcCalendarInstant) -> float:
        value = (
            instant_utc
            if isinstance(instant_utc, UtcCalendarInstant)
            else UtcCalendarInstant.from_datetime(instant_utc)
        )
        jd1, jd2 = value.utc_jd()
        return float(jd1 + jd2 - 2_400_000.5)

    @staticmethod
    def _tai_minus_utc_at_mjd(mjd_utc: float) -> float:
        year, month, day, fraction = erfa.jd2cal(2_400_000.5, mjd_utc)
        return float(erfa.dat(int(year), int(month), int(day), float(fraction)))

    def resolve(
        self, instant_utc: datetime | UtcCalendarInstant
    ) -> ResolvedEarthOrientation:
        requested = (
            instant_utc
            if isinstance(instant_utc, UtcCalendarInstant)
            else UtcCalendarInstant.from_datetime(instant_utc)
        )
        mjd = self._mjd(instant_utc)
        index = bisect_left(self._mjds, mjd)
        if index < len(self._records) and math.isclose(
            self._records[index].mjd_utc, mjd, abs_tol=1e-12
        ):
            lower = upper = self._records[index]
        elif index == 0 or index == len(self._records):
            raise AstronomyDataUnavailable(
                f"UTC MJD {mjd:.9f} is outside IERS EOP snapshot "
                f"[{self._mjds[0]:.1f}, {self._mjds[-1]:.1f}]"
            )
        else:
            lower, upper = self._records[index - 1], self._records[index]

        if upper.mjd_utc - lower.mjd_utc > self.max_gap_days:
            raise AstronomyDataUnavailable(
                f"IERS EOP interpolation gap is {upper.mjd_utc - lower.mjd_utc:.3f} days"
            )
        if not self.allow_predictions and (
            lower.quality is EopQuality.PREDICTED or upper.quality is EopQuality.PREDICTED
        ):
            raise AstronomyDataUnavailable("IERS predicted EOP values are disabled by policy")

        fraction = (
            0.0
            if upper.mjd_utc == lower.mjd_utc
            else (mjd - lower.mjd_utc) / (upper.mjd_utc - lower.mjd_utc)
        )

        def interpolate(name: str) -> float | None:
            a = getattr(lower, name)
            b = getattr(upper, name)
            if a is None or b is None:
                return None
            return float(a + fraction * (b - a))

        lower_ut1_tai = lower.dut1_seconds - self._tai_minus_utc_at_mjd(lower.mjd_utc)
        upper_ut1_tai = upper.dut1_seconds - self._tai_minus_utc_at_mjd(upper.mjd_utc)
        ut1_tai = lower_ut1_tai + fraction * (upper_ut1_tai - lower_ut1_tai)
        dut1 = ut1_tai + requested.tai_minus_utc_seconds()

        quality = max((lower.quality, upper.quality), key=_quality_rank)
        return ResolvedEarthOrientation(
            dut1_seconds=float(dut1),
            xp_arcsec=float(interpolate("xp_arcsec")),
            yp_arcsec=float(interpolate("yp_arcsec")),
            dx_mas=interpolate("dx_mas"),
            dy_mas=interpolate("dy_mas"),
            quality=quality,
            version=self.version,
            source_sha256=self.source_sha256,
            lower_mjd=lower.mjd_utc,
            upper_mjd=upper.mjd_utc,
        )

    __call__ = resolve


def _quality_rank(quality: EopQuality) -> int:
    return {
        EopQuality.FINAL: 0,
        EopQuality.OBSERVED: 1,
        EopQuality.PREDICTED: 2,
    }[quality]


class CivilTimeBasis(str, Enum):
    UTC = "utc"
    PROLEPTIC_UT1 = "proleptic_ut1"


@dataclass(frozen=True)
class DeltaTEstimate:
    seconds: float
    model: str
    valid_year_min: float
    valid_year_max: float
    is_prediction: bool
    uncertainty_seconds: float | None


def estimate_delta_t(decimal_year: float) -> DeltaTEstimate:
    """Espenak/Meeus historical extrapolation policy for years -1999..3000.

    These piecewise polynomials are a civil-time fallback, not an observational
    EOP replacement.  Their uncertainty grows rapidly outside the telescopic
    era, so production receipts must expose the model and uncertainty.
    """

    y = float(decimal_year)
    if not -1999.0 <= y <= 3000.0:
        raise AstronomyDataUnavailable("Delta-T model is valid only for years -1999..3000")
    if y < -500:
        u = (y - 1820) / 100
        seconds = -20 + 32 * u**2
        uncertainty = 1200.0
    elif y < 500:
        u = y / 100
        seconds = (
            10583.6
            - 1014.41 * u
            + 33.78311 * u**2
            - 5.952053 * u**3
            - 0.1798452 * u**4
            + 0.022174192 * u**5
            + 0.0090316521 * u**6
        )
        uncertainty = 600.0
    elif y < 1600:
        u = (y - 1000) / 100
        seconds = (
            1574.2
            - 556.01 * u
            + 71.23472 * u**2
            + 0.319781 * u**3
            - 0.8503463 * u**4
            - 0.005050998 * u**5
            + 0.0083572073 * u**6
        )
        uncertainty = 180.0
    elif y < 1700:
        t = y - 1600
        seconds = 120 - 0.9808 * t - 0.01532 * t**2 + t**3 / 7129
        uncertainty = 30.0
    elif y < 1800:
        t = y - 1700
        seconds = 8.83 + 0.1603 * t - 0.0059285 * t**2 + 0.00013336 * t**3 - t**4 / 1174000
        uncertainty = 10.0
    elif y < 1860:
        t = y - 1800
        seconds = (
            13.72
            - 0.332447 * t
            + 0.0068612 * t**2
            + 0.0041116 * t**3
            - 0.00037436 * t**4
            + 0.0000121272 * t**5
            - 0.0000001699 * t**6
            + 0.000000000875 * t**7
        )
        uncertainty = 5.0
    elif y < 1900:
        t = y - 1860
        seconds = 7.62 + 0.5737 * t - 0.251754 * t**2 + 0.01680668 * t**3 - 0.0004473624 * t**4 + t**5 / 233174
        uncertainty = 2.0
    elif y < 1920:
        t = y - 1900
        seconds = -2.79 + 1.494119 * t - 0.0598939 * t**2 + 0.0061966 * t**3 - 0.000197 * t**4
        uncertainty = 1.0
    elif y < 1941:
        t = y - 1920
        seconds = 21.20 + 0.84493 * t - 0.076100 * t**2 + 0.0020936 * t**3
        uncertainty = 0.8
    elif y < 1961:
        t = y - 1950
        seconds = 29.07 + 0.407 * t - t**2 / 233 + t**3 / 2547
        uncertainty = 0.5
    elif y < 1986:
        t = y - 1975
        seconds = 45.45 + 1.067 * t - t**2 / 260 - t**3 / 718
        uncertainty = 0.25
    elif y < 2005:
        t = y - 2000
        seconds = 63.86 + 0.3345 * t - 0.060374 * t**2 + 0.0017275 * t**3 + 0.000651814 * t**4 + 0.00002373599 * t**5
        uncertainty = 0.2
    elif y < 2050:
        t = y - 2000
        seconds = 62.92 + 0.32217 * t + 0.005589 * t**2
        uncertainty = max(0.5, (y - 2005) * 0.12)
    elif y < 2150:
        seconds = -20 + 32 * ((y - 1820) / 100) ** 2 - 0.5628 * (2150 - y)
        uncertainty = 60.0
    else:
        u = (y - 1820) / 100
        seconds = -20 + 32 * u**2
        uncertainty = 300.0
    return DeltaTEstimate(
        seconds=float(seconds),
        model="espenak-meeus-piecewise-v1",
        valid_year_min=-1999.0,
        valid_year_max=3000.0,
        is_prediction=y >= 2005.0,
        uncertainty_seconds=uncertainty,
    )
