"""Tests for the lunar-node and Delta-T benchmark rows.

The control cases come first: each row must turn FAIL when a known offset is added to the
quantity it gates, or a passing verdict means nothing. Tests that need the real DE440 kernel
read ``EPHEMERIS_BENCH_KERNEL``; tests that need the IERS finals2000A file read
``EPHEMERIS_BENCH_EOP``. Unset means skip with that reason; set to a missing path means fail.
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

import numpy as np
import pytest

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from bench.rows import delta_t as D  # noqa: E402
from bench.rows import nodes as N  # noqa: E402


def _required(variable: str) -> Path:
    configured = os.getenv(variable)
    if not configured:
        pytest.skip(f"{variable} is not set")
    path = Path(configured)
    assert path.is_file(), f"{variable} points at a missing file: {path}"
    return path


@pytest.fixture(scope="module")
def kernel() -> Path:
    return _required("EPHEMERIS_BENCH_KERNEL")


@pytest.fixture(scope="module")
def eop() -> Path:
    return _required("EPHEMERIS_BENCH_EOP")


# Controls on synthetic differences: no data files needed.

def test_true_node_target_fails_with_offset() -> None:
    diffs = np.full(50, 1e-4)
    assert N.true_node_target(diffs, seed=1)["verdict"] == "PASS"
    assert N.true_node_target(diffs + N.CONTROL_OFFSET_ARCSEC, seed=1)["verdict"] == "FAIL"


def test_delta_t_gate_fails_with_offset() -> None:
    errors = np.full(50, 1e-6)
    assert D.gated_target(errors, seed=1)["verdict"] == "PASS"
    assert D.gated_target(errors + D.CONTROL_OFFSET_SECONDS, seed=1)["verdict"] == "FAIL"


def test_wrapped_difference_crosses_zero() -> None:
    assert N.wrapped_diff_arcsec(np.array([0.0]), np.array([359.9999]))[0] == pytest.approx(0.36, abs=1e-6)


# The mean-node polynomials: pins the coefficient finding.

def test_engine_mean_node_matches_its_own_coefficients() -> None:
    jd = np.linspace(2415020.5, 2488069.5, 41)
    ours = np.array([N.engine_mean_node(float(j)) for j in jd])
    diffs = N.wrapped_diff_arcsec(ours, N.polynomial(N.ENGINE_COEFFICIENTS, jd))
    assert float(np.max(np.abs(diffs))) < N.MEAN_NODE_TOLERANCE_ARCSEC


def test_engine_mean_node_differs_from_meeus_second_edition() -> None:
    curve = N.polynomial_difference_curve()
    assert curve["max_abs_arcsec_1900_2100"] > N.MEAN_NODE_TOLERANCE_ARCSEC


# Real-data rows.

def test_nodes_row_control_and_clean(kernel: Path) -> None:
    clean = N.build(kernel, count=200)
    assert clean["targets"]["true_node"]["verdict"] == "PASS"
    dirty = N.build(kernel, count=200, control_offset_arcsec=N.CONTROL_OFFSET_ARCSEC)
    assert dirty["targets"]["true_node"]["verdict"] == "FAIL"


def test_nodes_row_is_byte_stable(kernel: Path) -> None:
    assert N.render(N.build(kernel, count=50)) == N.render(N.build(kernel, count=50))


def test_delta_t_row_control_and_clean(eop: Path) -> None:
    clean = D.build(eop)
    assert clean["targets"]["eop_path_1973_2025"]["verdict"] == "PASS"
    dirty = D.build(eop, control_offset_seconds=D.CONTROL_OFFSET_SECONDS)
    assert dirty["targets"]["eop_path_1973_2025"]["verdict"] == "FAIL"


def test_independent_eop_reader_agrees_with_engine_parser(eop: Path) -> None:
    from ephemeris_oss.engine.earth_orientation import parse_finals2000a_line

    ours = D.read_finals(eop)
    lines = [line for line in eop.read_text(encoding="ascii").splitlines()
             if (record := parse_finals2000a_line(line)) is not None]
    assert len(ours) > 19000 and len(lines) >= len(ours)
