from __future__ import annotations

import math

import numpy as np
import pytest

from bench.harness import engines as E
from bench.harness import samples as S
from bench.harness import stats as T


def test_body_map_matches_spec():
    assert E.NAIF == {
        "sun": 10, "moon": 301, "mercury": 199, "venus": 299, "mars": 4,
        "jupiter": 5, "saturn": 6, "uranus": 7, "neptune": 8, "pluto": 9,
    }


def test_harness_never_imports_copyleft_modules():
    import pathlib

    harness = pathlib.Path(E.__file__).parent
    for source in harness.glob("*.py"):
        text = source.read_text(encoding="utf-8")
        for name in ("swisseph", "libephemeris"):
            assert f"import {name}" not in text and f"from {name}" not in text, source.name


@pytest.fixture(scope="module")
def small_rows():
    return S.make_samples(20, 1, list(S.BODIES), ["E1", "E3"], list(S.MODES))


@pytest.fixture(scope="module")
def both(small_rows, kernel_path):
    return E.ours(small_rows, kernel_path), E.t2_skyfield(small_rows, kernel_path)


def test_every_id_is_answered_with_a_unit_vector(small_rows, both):
    for result in both:
        assert set(result) == {r["id"] for r in small_rows}
        for vector in result.values():
            assert len(vector) == 3
            assert math.isclose(math.fsum(c * c for c in vector), 1.0, rel_tol=1e-12)


def test_ours_agrees_with_skyfield_geometric(small_rows, both):
    ours, t2 = both
    ids = [r["id"] for r in small_rows if r["mode"] == "geometric"]
    seps = T.separations_arcsec(np.array([ours[i] for i in ids]), np.array([t2[i] for i in ids]))
    # Both read the same Chebyshev segments; only arithmetic order differs.
    assert float(seps.max()) < 1e-4


def test_mode_effects_have_physical_size(kernel_path):
    row = {"body": "mars", "era": "E1", "jd_tdb": "2451545.000000000"}
    rows = [dict(row, id=m, mode=m) for m in S.MODES]
    for engine in (E.ours, E.t2_skyfield):
        out = engine(rows, kernel_path)
        light_time = T.separation_arcsec(out["geometric"], out["astrometric"])
        aberration = T.separation_arcsec(out["astrometric"], out["apparent"])
        assert 1.0 < light_time < 120.0
        assert 5.0 < aberration < 25.0
