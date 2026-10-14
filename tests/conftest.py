import os
from pathlib import Path
import pytest
from ephemeris_oss.kernels import cache_dir

@pytest.fixture(scope="session")
def kernel_path():
    configured = os.getenv("EPHEMERIS_OSS_DE440_KERNEL") or os.getenv("EPHEMERIS_BENCH_KERNEL")
    path = Path(configured) if configured else cache_dir() / "de440.bsp"
    assert path.is_file(), "Real DE440 input missing. Fetch the verified package cache or set EPHEMERIS_OSS_DE440_KERNEL."
    return path
