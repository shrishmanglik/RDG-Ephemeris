from __future__ import annotations

import json

import numpy as np
import pytest

from bench.harness import controls as K
from bench.harness import samples as S
from bench.harness import scorecard as C
from bench.harness import stats as T


def test_offset_moves_moon_by_exactly_the_requested_angle():
    rows = [{"id": "m", "body": "moon"}, {"id": "s", "body": "sun"}]
    vectors = {"m": (0.6, 0.0, 0.8), "s": (1.0, 0.0, 0.0)}
    out = K.offset_body(vectors, rows, "moon", 1.0)
    assert T.separation_arcsec(vectors["m"], out["m"]) == pytest.approx(1.0, rel=1e-9)
    assert out["s"] == vectors["s"]
    assert np.isclose(np.linalg.norm(out["m"]), 1.0)


def test_offset_works_at_the_pole():
    rows = [{"id": "m", "body": "moon"}]
    out = K.offset_body({"m": (0.0, 0.0, 1.0)}, rows, "moon", 1.0)
    assert T.separation_arcsec((0.0, 0.0, 1.0), out["m"]) == pytest.approx(1.0, rel=1e-9)


@pytest.fixture(scope="module")
def moon_samples(tmp_path_factory):
    path = tmp_path_factory.mktemp("ctl") / "s.jsonl"
    S.write_samples(S.make_samples(41, 3, ["moon", "mars"], ["E1"], ["geometric", "apparent"]), path)
    return path


def run(samples, kernel, out, *extra):
    return C.main(["--samples", str(samples), "--kernel", str(kernel), "--out", str(out), *extra])


def test_plus_one_arcsec_on_moon_fails_fidelity(moon_samples, kernel_path, tmp_path):
    clean = run(moon_samples, kernel_path, tmp_path / "clean.json", "--fail-above-arcsec", "0.1")
    assert clean == C.EXIT_PASS
    dirty = run(moon_samples, kernel_path, tmp_path / "dirty.json", "--fail-above-arcsec", "0.1",
                "--control-moon-offset-arcsec", "1.0")
    assert dirty == C.EXIT_FAIL
    card = json.loads((tmp_path / "dirty.json").read_text())
    assert card["verdict"] == "FAIL"
    assert any("moon" in key for key in card["failures"])
    assert not any("mars" in key for key in card["failures"])


def test_self_comparison_is_exactly_zero(moon_samples, kernel_path):
    result = K.self_comparison(S.read_samples(moon_samples), kernel_path)
    assert result["n"] == 12
    assert result["max_separation_arcsec"] == 0.0
    assert result["max_ecliptic_component_arcsec"] == 0.0


def test_missing_kernel_control(moon_samples, tmp_path):
    assert K.missing_kernel_is_void(moon_samples, tmp_path) is True


def test_run_all_controls(moon_samples, kernel_path, tmp_path):
    report = K.run_all(moon_samples, kernel_path, tmp_path)
    assert report == {"missing_kernel_void": True, "moon_offset_fails": True, "self_zero": True}
