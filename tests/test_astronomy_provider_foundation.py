from __future__ import annotations

import hashlib
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Mapping, Sequence

import pytest

from ephemeris_oss.engine import (
    AstronomyDataUnavailable,
    AstronomyProvider,
    CalculationReceipt,
    CalculationSettings,
    DatasetVersions,
    KernelArtifact,
    KernelRegistry,
    Observer,
    ProviderIdentity,
)


SETTINGS = CalculationSettings(
    frame="ICRF/J2000",
    zodiac_mode="sidereal",
    ayanamsa="lahiri",
    node_mode="true",
    correction_flags=("aberration", "light_time"),
)


class FakeProvider(AstronomyProvider):
    def __init__(
        self,
        name: str,
        longitude: float,
        fail: bool = False,
        delay_seconds: float = 0.0,
    ) -> None:
        self._identity = ProviderIdentity(name, "0.0.1")
        self.longitude = longitude
        self.fail = fail
        self.delay_seconds = delay_seconds

    @property
    def identity(self) -> ProviderIdentity:
        return self._identity

    def _value(self) -> float:
        if self.delay_seconds:
            time.sleep(self.delay_seconds)
        if self.fail:
            raise AstronomyDataUnavailable("candidate data unavailable")
        return self.longitude

    def planet_positions(self, **_: Any) -> Mapping[str, Any]:
        return {"Sun": {"longitude_deg": self._value()}}

    def ayanamsa(self, **_: Any) -> float:
        return self._value()

    def houses(self, **_: Any) -> Mapping[str, Any]:
        return {"ascendant_deg": self._value()}

    def julian_day(self, **_: Any) -> float:
        return self._value()

    def reverse_julian_day(self, **_: Any) -> datetime:
        self._value()
        return datetime(2000, 1, 1, tzinfo=timezone.utc)

    def rise_set(self, **_: Any) -> Mapping[str, Any]:
        return {"julian_day": self._value()}

    def solar_longitude_crossing(self, **_: Any) -> Mapping[str, Any]:
        return {"julian_day": self._value()}

    def stations(self, **_: Any) -> Sequence[Mapping[str, Any]]:
        return [{"julian_day": self._value()}]

    def ingresses(self, **_: Any) -> Sequence[Mapping[str, Any]]:
        return [{"julian_day": self._value()}]

    def solar_returns(self, **_: Any) -> Sequence[Mapping[str, Any]]:
        return [{"julian_day": self._value()}]

    def solar_eclipses(self, **_: Any) -> Sequence[Mapping[str, Any]]:
        return [{"julian_day": self._value()}]

    def lunar_eclipses(self, **_: Any) -> Sequence[Mapping[str, Any]]:
        return [{"julian_day": self._value()}]

    def coordinate_transform(self, **_: Any) -> Sequence[float]:
        return [self._value(), 0.0, 0.0]




def test_receipt_is_stable_across_mapping_and_flag_order() -> None:
    datasets = DatasetVersions(
        kernel_identifier="DE440",
        kernel_sha256="A" * 64,
        leap_seconds="iers-leap-seconds-2026a",
        earth_orientation="iers-bulletin-a-2026-07-16",
        delta_t="vas-delta-t-1",
        ayanamsa="vas-ayanamsa-1",
        earth_orientation_sha256="B" * 64,
        earth_orientation_quality="final",
        earth_orientation_lower_mjd=61_000.0,
        earth_orientation_upper_mjd=61_001.0,
    )
    observer = Observer(43.6532, -79.3832, 76.0)
    first = CalculationReceipt.from_request(
        provider=ProviderIdentity("ephemeris-oss", "0.1.0"),
        datasets=datasets,
        settings=SETTINGS,
        observer=observer,
        request={"bodies": ["Sun", "Moon"], "instant": datetime(2026, 7, 21, 12, tzinfo=timezone.utc)},
    )
    reordered = CalculationReceipt.from_request(
        provider=ProviderIdentity("ephemeris-oss", "0.1.0"),
        datasets=datasets,
        settings=CalculationSettings(
            frame="ICRF/J2000",
            zodiac_mode="sidereal",
            ayanamsa="lahiri",
            node_mode="true",
            correction_flags=("light_time", "aberration", "light_time"),
        ),
        observer=observer,
        request={"instant": datetime(2026, 7, 21, 12, tzinfo=timezone.utc), "bodies": ["Sun", "Moon"]},
    )

    assert first.bytes() == reordered.bytes()
    assert first.sha256() == reordered.sha256()
    assert first.payload()["kernel_sha256"] == "a" * 64
    assert first.payload()["earth_orientation_sha256"] == "b" * 64
    assert first.payload()["earth_orientation_quality"] == "final"
    assert first.payload()["earth_orientation_lower_mjd"] == 61_000.0
    assert first.payload()["earth_orientation_upper_mjd"] == 61_001.0


@pytest.mark.parametrize(
    ("year", "expected"),
    [(1549, "DE441"), (1550, "DE440"), (2649, "DE440"), (2650, "DE441")],
)
def test_kernel_selection_policy(year: int, expected: str) -> None:
    assert KernelRegistry.identifier_for_year(year) == expected


def test_kernel_selection_uses_exact_tdb_coverage_at_de440_end(tmp_path) -> None:
    de440 = tmp_path / "de440.bsp"
    de441 = tmp_path / "de441.bsp"
    de440.write_bytes(b"de440")
    de441.write_bytes(b"de441")
    registry = KernelRegistry(
        {
            "DE440": KernelArtifact("DE440", de440, hashlib.sha256(b"de440").hexdigest()),
            "DE441": KernelArtifact("DE441", de441, hashlib.sha256(b"de441").hexdigest()),
        }
    )

    assert registry.artifact_for_tdb_jd(2688976.5).identifier == "DE440"
    assert registry.artifact_for_tdb_jd(2688976.500001).identifier == "DE441"


def test_kernel_registry_verifies_checksum_and_fails_closed(tmp_path: Path) -> None:
    kernel = tmp_path / "de440.bsp"
    kernel.write_bytes(b"official-kernel-fixture")
    checksum = hashlib.sha256(kernel.read_bytes()).hexdigest()
    registry = KernelRegistry({"DE440": KernelArtifact("DE440", kernel, checksum)})

    assert registry.verified_path_for_year(2026) == kernel

    bad = KernelRegistry({"DE440": KernelArtifact("DE440", kernel, "0" * 64)})
    with pytest.raises(AstronomyDataUnavailable, match="checksum mismatch"):
        bad.verified_path_for_year(2026)
    with pytest.raises(AstronomyDataUnavailable, match="DE441"):
        registry.verified_path_for_year(1200)


def test_kernel_registry_selects_split_de441_artifacts(tmp_path: Path) -> None:
    first = tmp_path / "de441-part1.bsp"
    second = tmp_path / "de441-part2.bsp"
    first.write_bytes(b"part-1")
    second.write_bytes(b"part-2")
    registry = KernelRegistry(
        {
            "DE441-PART1": KernelArtifact(
                "DE441-PART1", first, hashlib.sha256(first.read_bytes()).hexdigest()
            ),
            "DE441-PART2": KernelArtifact(
                "DE441-PART2", second, hashlib.sha256(second.read_bytes()).hexdigest()
            ),
        }
    )

    assert registry.artifact_for_year(1000).identifier == "DE441-PART1"
    assert registry.artifact_for_year(3000).identifier == "DE441-PART2"












