"""Shared fixtures for the benchmark harness tests.

Tests that need the real DE440 kernel read its path from ``EPHEMERIS_BENCH_KERNEL``.
When the variable is unset they skip with that reason; when it is set to a path
that does not exist they fail, so a wrong path can never pass as a skip.
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


@pytest.fixture(scope="session")
def kernel_path() -> Path:
    configured = os.getenv("EPHEMERIS_BENCH_KERNEL")
    if not configured:
        pytest.skip("EPHEMERIS_BENCH_KERNEL is not set; real-kernel tests need DE440")
    path = Path(configured)
    assert path.is_file(), f"EPHEMERIS_BENCH_KERNEL points at a missing file: {path}"
    return path
