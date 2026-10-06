"""Contract tests for the public ``ephemeris_oss`` interface.

They touch only names exported from ``ephemeris_oss`` so the engine underneath
can change without breaking them. Tests that need the real DE440 file skip
unless ``EPHEMERIS_OSS_DE440_KERNEL`` points at it.
"""

from __future__ import annotations

import hashlib
import os
from datetime import date, datetime, timezone
from pathlib import Path

import pytest

import ephemeris_oss
from ephemeris_oss import EarthOrientation, Engine, EphemerisError, Houses, Result, Undefined

DE440 = os.getenv("EPHEMERIS_OSS_DE440_KERNEL")
needs_de440 = pytest.mark.skipif(not DE440, reason="real DE440 kernel not supplied")
T = datetime(2026, 10, 6, 12, tzinfo=timezone.utc)
ZERO_EOP = EarthOrientation(dut1_seconds=0.0, xp_arcsec=0.0, yp_arcsec=0.0, version="test-zero")


def engine() -> Engine:
    assert DE440 is not None
    return Engine.load(kernels={"DE440": Path(DE440)}, eop=ZERO_EOP)


def test_public_surface_is_small_and_has_no_eclipse_or_swiss_shaped_names() -> None:
    exported = set(ephemeris_oss.__all__)
    assert {"Engine", "Result", "Undefined", "Houses", "EphemerisError", "EarthOrientation"} <= exported
    banned = ("eclipse", "calc_ut", "houses_ex", "rise_trans", "swe")
    assert not [name for name in exported if any(word in name.lower() for word in banned)]
    public_methods = {name for name in dir(Engine) if not name.startswith("_")}
    assert not [name for name in public_methods if "eclipse" in name.lower()]


def test_kernel_with_wrong_hash_is_refused(tmp_path: Path) -> None:
    fake = tmp_path / "de440.bsp"
    fake.write_bytes(b"not a kernel")
    with pytest.raises(EphemerisError, match="SHA-256"):
        Engine.load(kernels={"DE440": fake}, eop=ZERO_EOP)


def test_auto_kernels_without_cache_says_how_to_fetch(tmp_path: Path) -> None:
    with pytest.raises(EphemerisError, match="kernels fetch"):
        Engine.load(kernels="auto", eop=ZERO_EOP, cache_dir=tmp_path)


@needs_de440
def test_positions_return_values_with_a_receipt_naming_the_kernel_hash() -> None:
    with engine() as eng:
        result = eng.positions(T, bodies=("sun", "moon"))
    assert isinstance(result, Result)
    assert set(result.value) == {"sun", "moon"}
    assert 0.0 <= result.value["sun"]["longitude_deg"] < 360.0
    digest = hashlib.sha256(Path(DE440).read_bytes()).hexdigest()
    assert digest in str(result.receipt)
    assert result.receipt_sha256 and len(result.receipt_sha256) == 64


@needs_de440
def test_sidereal_positions_need_an_ayanamsa_and_differ_by_it() -> None:
    with engine() as eng:
        tropical = eng.positions(T, bodies=("sun",)).value["sun"]["longitude_deg"]
        sidereal = eng.positions(T, bodies=("sun",), ayanamsa="lahiri").value["sun"]["longitude_deg"]
        offset = eng.ayanamsa(T, system="lahiri").value
    assert 23.0 < offset < 25.0
    assert abs(((tropical - sidereal) - offset + 180.0) % 360.0 - 180.0) < 1e-6


@needs_de440
def test_houses_are_a_value_or_undefined_with_a_reason_never_a_silent_switch() -> None:
    with engine() as eng:
        toronto = eng.houses(T, lat=43.65, lon=-79.38, system="placidus")
        polar = eng.houses(T, lat=80.0, lon=10.0, system="placidus")
    assert isinstance(toronto.value, Houses) and len(toronto.value.cusps_deg) == 12
    assert toronto.value.system == "placidus"
    assert isinstance(polar.value, Undefined)
    assert "Placidus" in polar.value.reason


@needs_de440
def test_nodes_mean_and_true_are_distinct_and_named() -> None:
    with engine() as eng:
        mean = eng.nodes(T, kind="mean").value
        true = eng.nodes(T, kind="true").value
    assert 0.0 <= mean < 360.0 and 0.0 <= true < 360.0
    assert mean != true
    with pytest.raises(EphemerisError):
        engine().nodes(T, kind="osculating-ish")


@needs_de440
def test_rise_set_returns_an_instant_for_a_normal_latitude() -> None:
    with engine() as eng:
        result = eng.rise_set(date(2026, 10, 6), lat=43.65, lon=-79.38, body="sun", event="rise")
    assert result.value["outcome"] == "events"
    assert result.value["events"]


def test_time_helpers_are_exported() -> None:
    from ephemeris_oss import time as eot

    estimate = eot.delta_t(2000.0)
    assert 60.0 < estimate.seconds < 70.0
    assert eot.from_civil(2026, 10, 6, 12, 0, 0, tz="UTC").isoformat().startswith("2026-10-06T12:00")


def test_from_civil_resolves_an_iana_zone_and_rejects_a_gap() -> None:
    from ephemeris_oss import time as eot

    assert eot.from_civil(2026, 7, 1, 12, tz="America/Toronto").hour == 16
    with pytest.raises(Exception):
        eot.from_civil(2026, 3, 8, 2, 30, tz="America/Toronto")
