"""The public package exposes the exact-TT entry point measured against JPL."""

from contextlib import closing
from pathlib import Path

import pytest

from ephemeris_oss import Engine
from ephemeris_oss.engine.receipt import canonical_hash


def test_explicit_tt_api_is_available_without_inventing_utc():
    assert hasattr(Engine, "positions_tt"), "the measured TT path is not packaged"


def test_measured_sun_moon_tt_result_has_a_reproducible_receipt(kernel_path):
    assert hasattr(Engine, "positions_tt"), "the measured TT path is not packaged"
    kernel = kernel_path
    with Engine.load(kernels={"DE440": kernel}, eop=None) as engine:
        first = engine.positions_tt(2451545.0, bodies=("sun", "moon"))
        second = engine.positions_tt(2451545.0, bodies=("sun", "moon"))
    assert set(first.value) == {"sun", "moon"}
    assert first.value == second.value
    assert first.receipt_sha256 == second.receipt_sha256
    assert first.receipt["time_scale"] == "TT"
    assert first.receipt["utc_inferred"] is False
    from skyfield.api import load, load_file
    from skyfield.framelib import ecliptic_frame
    with closing(load_file(str(kernel))) as reference:
        instant = load.timescale(builtin=True).tt_jd(2451545.0)
        _, longitude, _ = reference[399].at(instant).observe(reference[10]).apparent(deflectors=()).frame_latlon(ecliptic_frame)
    assert first.value["sun"]["longitude_deg"] == pytest.approx(longitude.degrees, abs=0.1 / 3600)


def test_tt_receipt_binds_normalized_bodies_targets_and_result(kernel_path):
    kernel = kernel_path
    with Engine.load(kernels={"DE440": kernel}, eop=None) as engine:
        sun = engine.positions_tt(2451545.0, bodies=("sun",))
        moon = engine.positions_tt(2451545.0, bodies=("moon",))
        normalized = engine.positions_tt(2451545.0, bodies=(" Sun ",))
        combined = engine.positions_tt(2451545.0, bodies=("sun", "mars", "jupiter", "saturn"))
    assert sun.value != moon.value and sun.receipt_sha256 != moon.receipt_sha256
    assert normalized.value == sun.value and normalized.receipt == sun.receipt
    assert normalized.receipt_sha256 == sun.receipt_sha256
    for result, bodies, targets in (
        (sun, ["sun"], {"sun": 10}),
        (moon, ["moon"], {"moon": 301}),
        (combined, ["sun", "mars", "jupiter", "saturn"],
         {"sun": 10, "mars": 4, "jupiter": 5, "saturn": 6}),
    ):
        assert result.receipt["bodies"] == bodies
        assert result.receipt["targets"] == targets
        assert result.receipt["request_sha256"] == canonical_hash(
            {"jd_tt": 2451545.0, "bodies": bodies, "targets": targets}
        )
        assert result.receipt["result_sha256"] == canonical_hash(result.value)
        assert result.receipt_sha256 == canonical_hash(result.receipt)


def test_tt_receipt_changes_when_same_request_returns_a_different_result(monkeypatch, kernel_path):
    kernel = kernel_path
    with Engine.load(kernels={"DE440": kernel}, eop=None) as engine:
        original = engine.positions_tt(2451545.0, bodies=("sun",))
        calculate = engine._provider.planet_positions_tt

        def changed_result(**kwargs):
            raw = calculate(**kwargs)
            raw["positions"]["Sun"]["longitude_deg"] += 0.25
            return raw

        monkeypatch.setattr(engine._provider, "planet_positions_tt", changed_result)
        changed = engine.positions_tt(2451545.0, bodies=("sun",))
    assert original.value != changed.value
    assert original.receipt_sha256 != changed.receipt_sha256
    assert original.receipt["request_sha256"] == changed.receipt["request_sha256"]
    assert original.receipt["result_sha256"] != changed.receipt["result_sha256"]
