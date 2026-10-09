"""The public package exposes the exact-TT entry point measured against JPL."""

from pathlib import Path
from contextlib import closing

import pytest

from ephemeris_oss import Engine


def test_explicit_tt_api_is_available_without_inventing_utc():
    assert hasattr(Engine, "positions_tt"), "the measured TT path is not packaged"


def test_measured_sun_moon_tt_result_has_a_reproducible_receipt():
    assert hasattr(Engine, "positions_tt"), "the measured TT path is not packaged"
    kernel = Path.home() / ".agi/assets/jpl/de440-a4ce9bf9b328.bsp"
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
