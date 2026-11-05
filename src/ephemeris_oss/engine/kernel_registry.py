"""Versioned kernel selection and fail-closed integrity checks."""

from __future__ import annotations

import hashlib
from dataclasses import dataclass
from pathlib import Path
from typing import Mapping

from .contracts import AstronomyDataUnavailable

DE440_START_YEAR = 1550
DE440_END_YEAR = 2649
DE440_START_JD = 2287184.5
DE440_END_JD = 2688976.5
DE440_SHA256 = "a4ce9bf9b3282becc9f4b2ac3cebe03a2ae7599981aabd7265fd8482fff7c4b5"
DE440_SIZE_BYTES = 119799808
COMPACT_DE440 = "COMPACT-DE440"
COMPACT_DE440_START_YEAR = 1800
COMPACT_DE440_END_YEAR = 2100
COMPACT_DE440_START_JD = 2378432.5
COMPACT_DE440_END_JD = 2488512.5
COMPACT_DE440_EARLY = "COMPACT-DE440-EARLY"
COMPACT_DE440_EARLY_START_YEAR = 1550
COMPACT_DE440_EARLY_END_YEAR = 1799
COMPACT_DE440_EARLY_START_JD = 2287184.5
COMPACT_DE440_LATE = "COMPACT-DE440-LATE"
COMPACT_DE440_LATE_START_YEAR = 2101
COMPACT_DE440_LATE_END_YEAR = 2305
COMPACT_DE440_LATE_END_JD = 2563392.5
DE441_PART_2_START_JD = 2440400.5
DE441_PART_1 = "DE441-PART1"
DE441_PART_2 = "DE441-PART2"
DE441_PART_1_SHA256 = "13757827f5db41b835a24bbd637488636ce79a8ca754062fed17844f7d5b618e"
DE441_PART_2_SHA256 = "3abb17dae2d78dd34880377544aacb54892104a0d4462b322cb9f4454d4887f6"


@dataclass(frozen=True)
class KernelArtifact:
    identifier: str
    path: Path
    sha256: str


class KernelRegistry:
    """Select DE440 for the current-era range and DE441 outside it."""

    def __init__(self, artifacts: Mapping[str, KernelArtifact]) -> None:
        self._artifacts = dict(artifacts)

    @property
    def generation(self) -> tuple[tuple[str, str], ...]:
        """Bind every configured artifact, including days spanning a boundary."""
        return tuple(sorted((key, value.sha256.lower()) for key, value in self._artifacts.items()))

    @staticmethod
    def identifier_for_year(year: int) -> str:
        return "DE440" if DE440_START_YEAR <= year <= DE440_END_YEAR else "DE441"

    def artifact_for_year(self, year: int) -> KernelArtifact:
        identifier = self.identifier_for_year(year)
        artifact = self._artifacts.get(identifier)
        if artifact is None and identifier == "DE440":
            if COMPACT_DE440_START_YEAR <= year <= COMPACT_DE440_END_YEAR:
                artifact = self._artifacts.get(COMPACT_DE440)
            elif COMPACT_DE440_EARLY_START_YEAR <= year <= COMPACT_DE440_EARLY_END_YEAR:
                artifact = self._artifacts.get(COMPACT_DE440_EARLY)
            elif COMPACT_DE440_LATE_START_YEAR <= year <= COMPACT_DE440_LATE_END_YEAR:
                artifact = self._artifacts.get(COMPACT_DE440_LATE)
        if artifact is None and identifier == "DE441":
            split_identifier = DE441_PART_1 if year < DE440_START_YEAR else DE441_PART_2
            artifact = self._artifacts.get(split_identifier)
        if artifact is None:
            raise AstronomyDataUnavailable(f"required kernel {identifier} is not configured")
        return artifact

    def artifact_for_tdb_jd(self, tdb_jd: float) -> KernelArtifact:
        """Select a configured kernel by its actual covered Julian-date span."""

        identifier = (
            "DE440" if DE440_START_JD <= tdb_jd <= DE440_END_JD else "DE441"
        )
        artifact = self._artifacts.get(identifier)
        if artifact is None and identifier == "DE440":
            if COMPACT_DE440_START_JD <= tdb_jd <= COMPACT_DE440_END_JD:
                artifact = self._artifacts.get(COMPACT_DE440)
            elif COMPACT_DE440_EARLY_START_JD <= tdb_jd < COMPACT_DE440_START_JD:
                artifact = self._artifacts.get(COMPACT_DE440_EARLY)
            elif COMPACT_DE440_END_JD < tdb_jd <= COMPACT_DE440_LATE_END_JD:
                artifact = self._artifacts.get(COMPACT_DE440_LATE)
        if artifact is None and identifier == "DE441":
            split_identifier = (
                DE441_PART_1 if tdb_jd < DE441_PART_2_START_JD else DE441_PART_2
            )
            artifact = self._artifacts.get(split_identifier)
        if artifact is None:
            raise AstronomyDataUnavailable(f"required kernel {identifier} is not configured")
        return artifact

    def verified_path_for_year(self, year: int) -> Path:
        artifact = self.artifact_for_year(year)
        return self.verified_path(artifact)

    def verified_path_for_tdb_jd(self, tdb_jd: float) -> Path:
        return self.verified_path(self.artifact_for_tdb_jd(tdb_jd))

    @staticmethod
    def verified_path(artifact: KernelArtifact) -> Path:
        if not artifact.path.is_file():
            raise AstronomyDataUnavailable(f"required kernel {artifact.identifier} is unavailable")

        digest = hashlib.sha256()
        with artifact.path.open("rb") as handle:
            for chunk in iter(lambda: handle.read(1024 * 1024), b""):
                digest.update(chunk)
        actual = digest.hexdigest()
        if actual.lower() != artifact.sha256.lower():
            raise AstronomyDataUnavailable(f"kernel checksum mismatch for {artifact.identifier}")
        return artifact.path
