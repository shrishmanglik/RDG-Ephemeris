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
        aberration = T.separation_arcsec(out["astrometric"], out["apparent-aberrated"])
        deflection = T.separation_arcsec(out["apparent-aberrated"], out["apparent"])
        assert 1.0 < light_time < 120.0
        assert 5.0 < aberration < 25.0
        # Solar deflection of Mars on 2000-01-01: milliarcseconds, never zero.
        assert 1e-4 < deflection < 0.05


def test_ours_agrees_with_skyfield_apparent_aberrated(small_rows, both):
    # No deflection on either side, so the Sun-only versus Sun+Jupiter+Saturn choice cannot enter.
    ours, t2 = both
    rows = [r for r in small_rows if r["mode"] == "apparent-aberrated"]
    seps = {r["id"]: float(T.separations_arcsec(np.array([ours[r["id"]]]), np.array([t2[r["id"]]]))[0])
            for r in rows}
    assert max(v for i, v in seps.items() if not i.startswith("moon-")) < 1e-4
    # Open finding, not a tolerance: the Moon's light-time direction differs from Skyfield's by up
    # to about 0.4 mas in every light-time mode, cause not yet found (first seen 2026-10-06). This
    # bound pins today's size so a regression shows; it is never quoted as an accuracy figure.
    assert max(v for i, v in seps.items() if i.startswith("moon-")) < 5e-4


def test_erfa_aberration_matches_engine_aberration(small_rows, both, kernel_path):
    # The adapter used for runners without an aberrated-only mode must equal the native path.
    ours, _ = both
    rows = [r for r in small_rows if r["mode"] == "apparent-aberrated"]
    # Each mode draws its own instants, so the natural direction is computed at the same instant.
    natural = E.ours([dict(r, mode="astrometric") for r in rows], kernel_path)
    added = E.erfa_aberrate(rows, natural, kernel_path)
    seps = T.separations_arcsec(np.array([ours[r["id"]] for r in rows]),
                                np.array([added[r["id"]] for r in rows]))
    assert float(seps.max()) < 1e-4
