"""Public distributions must not carry bulk ephemerides or private local state."""

import importlib.util
from pathlib import Path
import zipfile

import pytest

spec = importlib.util.spec_from_file_location("wheel_gate", Path(__file__).parents[1] / "tools/check_wheel.py")
wheel_gate = importlib.util.module_from_spec(spec)
spec.loader.exec_module(wheel_gate)


@pytest.mark.parametrize("path", ["ephemeris_oss/data/de440.bsp", "ephemeris_oss/state/clients.sqlite", "ephemeris_oss/.env"])
def test_wheel_rejects_bulk_kernel_and_private_state(tmp_path, path):
    wheel = tmp_path / "planted.whl"
    with zipfile.ZipFile(wheel, "w") as archive:
        archive.writestr("ephemeris_oss/__init__.py", "VALUE = 1\n")
        archive.writestr(path, b"TEST_ONLY")
    assert wheel_gate.scan(wheel), f"distribution accepted {path}"


def test_wheel_accepts_clean_module_and_refuses_banned_names(tmp_path):
    clean_wheel = tmp_path / "clean.whl"
    with zipfile.ZipFile(clean_wheel, "w") as archive:
        archive.writestr("ephemeris_oss/engine.py", "VALUE = 1\n")
        archive.writestr("ephemeris_oss-0.0.dist-info/RECORD",
                         "ephemeris_oss/engine.py,sha256-test,10\n")
    assert wheel_gate.scan(clean_wheel) == []


@pytest.mark.parametrize("name,content", [
    ("ephemeris_oss/swisseph_compat.py", "VALUE = 1\n"),
    ("ephemeris_oss/other_swisseph.py", "VALUE = 1\n"),
    ("ephemeris_oss-0.0.dist-info/RECORD", "swisseph.py,sha256-test,10\n"),
])
def test_compatibility_path_does_not_exempt_code_or_other_metadata(tmp_path, name, content):
    wheel = tmp_path / "planted.whl"
    with zipfile.ZipFile(wheel, "w") as archive:
        archive.writestr(name, content)
    assert wheel_gate.scan(wheel)
