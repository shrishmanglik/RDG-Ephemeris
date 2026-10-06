"""Fetching refuses bad bytes and keeps nothing it cannot verify. No network: the opener is a fake."""

from __future__ import annotations

import io
from pathlib import Path

import pytest

from ephemeris_oss import kernels


class FakeResponse(io.BytesIO):
    def __enter__(self) -> "FakeResponse":
        return self

    def __exit__(self, *_exc: object) -> None:
        self.close()


def test_kernel_fetch_with_wrong_bytes_raises_and_leaves_nothing(tmp_path: Path) -> None:
    with pytest.raises(ValueError, match="SHA-256 mismatch"):
        kernels.fetch(("DE440",), directory=tmp_path, opener=lambda _url: FakeResponse(b"garbage"), log=lambda _m: None)
    assert list(tmp_path.iterdir()) == []
    assert kernels.verify(tmp_path)["DE440"] == "absent"


def test_eop_fetch_refuses_a_file_with_no_records(tmp_path: Path) -> None:
    with pytest.raises(ValueError, match="no finals2000A records"):
        kernels.fetch_eop(directory=tmp_path, opener=lambda _url: FakeResponse(b"<html>maintenance</html>"),
                          log=lambda _m: None)
    assert not (tmp_path / kernels.EOP_FILENAME).exists()


def test_kernel_urls_point_only_at_naif() -> None:
    assert all(spec.url.startswith("https://naif.jpl.nasa.gov/") for spec in kernels.KERNELS.values())
    assert kernels.IERS_FINALS_URL.startswith("https://datacenter.iers.org/")
