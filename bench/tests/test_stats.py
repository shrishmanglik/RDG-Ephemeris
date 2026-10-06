from __future__ import annotations

import math

import numpy as np
import pytest

from bench.harness import stats as T

ARCSEC = math.pi / (180 * 3600)


def rotate_z(v, arcsec):
    a = arcsec * ARCSEC
    c, s = math.cos(a), math.sin(a)
    return (c * v[0] - s * v[1], s * v[0] + c * v[1], v[2])


def test_separation_exact_zero_for_identical():
    v = (0.3, -0.5, 0.81)
    assert T.separation_arcsec(v, v) == 0.0


def test_separation_small_angle_is_stable():
    # acos loses everything below about 0.01 arcsec; the atan2 form does not.
    v = (1.0, 0.0, 0.0)
    for arcsec in (1e-6, 1e-3, 1.0, 3600.0):
        assert T.separation_arcsec(v, rotate_z(v, arcsec)) == pytest.approx(arcsec, rel=1e-9)


def test_separation_ignores_length_and_handles_antipodes():
    assert T.separation_arcsec((2.0, 0, 0), (5.0, 0, 0)) == 0.0
    assert T.separation_arcsec((1.0, 0, 0), (-1.0, 0, 0)) == pytest.approx(180 * 3600)


def test_separations_vectorised_matches_scalar():
    a = np.array([[1.0, 0, 0], [0, 1.0, 0]])
    b = np.array([rotate_z((1.0, 0, 0), 2.0), (0, 1.0, 0)])
    out = T.separations_arcsec(a, b)
    assert out[0] == pytest.approx(2.0, rel=1e-9) and out[1] == 0.0


def test_ecliptic_component_difference_longitude_only():
    # A pure rotation about the ecliptic pole changes longitude only.
    jd = 2451545.0
    m = T.ecliptic_matrix(jd)
    base = m.T @ np.array([math.cos(0.4), math.sin(0.4), 0.0])
    shifted = m.T @ np.array([math.cos(0.4 + 1.5 * ARCSEC), math.sin(0.4 + 1.5 * ARCSEC), 0.0])
    assert T.ecliptic_component_diff_arcsec(base, shifted, jd) == pytest.approx(1.5, rel=1e-6)


def test_ecliptic_longitude_wraps_at_zero():
    jd = 2451545.0
    m = T.ecliptic_matrix(jd)
    a = m.T @ np.array([math.cos(-0.5 * ARCSEC), math.sin(-0.5 * ARCSEC), 0.0])
    b = m.T @ np.array([math.cos(0.5 * ARCSEC), math.sin(0.5 * ARCSEC), 0.0])
    assert T.ecliptic_component_diff_arcsec(a, b, jd) == pytest.approx(1.0, rel=1e-6)


def test_ecliptic_latitude_difference():
    jd = 2460000.5
    m = T.ecliptic_matrix(jd)
    a = m.T @ np.array([1.0, 0.0, 0.0])
    b = m.T @ np.array([math.cos(2 * ARCSEC), 0.0, math.sin(2 * ARCSEC)])
    assert T.ecliptic_component_diff_arcsec(a, b, jd) == pytest.approx(2.0, rel=1e-6)


def test_ecliptic_matrix_is_true_ecliptic_from_pnm06a():
    # The true ecliptic of date differs from ERFA's mean ecliptic (ecm06) by
    # nutation: about 17 arcsec in longitude, under 10 arcsec of obliquity.
    jd = 2451545.0
    true = T.ecliptic_matrix(jd)
    mean = T.ecliptic_matrix(jd, kind="mean")
    assert np.allclose(true @ true.T, np.eye(3), atol=1e-15)
    angle = math.acos(min(1.0, (np.trace(true @ mean.T) - 1) / 2)) / ARCSEC
    assert 1.0 < angle < 30.0


def test_summary_quantiles():
    values = np.arange(1, 101, dtype=float)
    s = T.summary(values, seed=1)
    assert s["n"] == 100
    assert s["median"] == 50.5
    assert s["p95"] == pytest.approx(np.percentile(values, 95, method="linear"))
    assert s["max"] == 100.0
    lo, hi = s["ci95"]["median"]
    assert lo <= 50.5 <= hi


def test_bootstrap_seeded_and_bracketing():
    values = np.random.default_rng(0).normal(size=200)
    a = T.bootstrap_ci(values, np.median, seed=3)
    b = T.bootstrap_ci(values, np.median, seed=3)
    c = T.bootstrap_ci(values, np.median, seed=4)
    assert a == b
    assert a != c
    assert a[0] < np.median(values) < a[1]


def test_bootstrap_uses_2000_resamples():
    assert T.BOOTSTRAP_RESAMPLES == 2000


def test_truth_floor_is_p99():
    t1 = {str(i): (1.0, 0.0, 0.0) for i in range(100)}
    t2 = {str(i): rotate_z((1.0, 0.0, 0.0), i / 1000) for i in range(100)}
    floor = T.truth_floor(t1, t2)
    seps = [i / 1000 for i in range(100)]
    assert floor == pytest.approx(np.percentile(seps, 99, method="linear"), rel=1e-6)


def test_truth_floor_requires_same_ids():
    with pytest.raises(ValueError):
        T.truth_floor({"a": (1, 0, 0)}, {"b": (1, 0, 0)})


def test_tie_rule_never_emits_a_number_below_floor():
    assert T.tie(0.001, 0.01) == {"tie_with_truth": True}
    assert T.tie(0.02, 0.01) == 0.02
    assert T.tie(0.02, None) == 0.02
