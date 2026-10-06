"""Where the JPL kernels and IERS Earth-orientation file live, and how they are fetched.

Nothing here is bundled with the package. Files are downloaded from NASA NAIF
and the IERS into a per-user cache and accepted only when their SHA-256
matches the pinned value, so a truncated or substituted file is refused rather
than silently used.
"""

from __future__ import annotations

import hashlib
import os
import urllib.request
from dataclasses import dataclass
from pathlib import Path
from typing import Callable

from .engine.kernel_registry import (
    DE440_SHA256,
    DE440_SIZE_BYTES,
    DE441_PART_1,
    DE441_PART_1_SHA256,
    DE441_PART_2,
    DE441_PART_2_SHA256,
)

NAIF_PLANETS = "https://naif.jpl.nasa.gov/pub/naif/generic_kernels/spk/planets/"


@dataclass(frozen=True)
class KernelSpec:
    identifier: str
    filename: str
    url: str
    sha256: str
    size_bytes: int | None


KERNELS: dict[str, KernelSpec] = {
    "DE440": KernelSpec("DE440", "de440.bsp", NAIF_PLANETS + "de440.bsp", DE440_SHA256, DE440_SIZE_BYTES),
    DE441_PART_1: KernelSpec(DE441_PART_1, "de441_part-1.bsp", NAIF_PLANETS + "de441_part-1.bsp",
                             DE441_PART_1_SHA256, 1_651_119_104),
    DE441_PART_2: KernelSpec(DE441_PART_2, "de441_part-2.bsp", NAIF_PLANETS + "de441_part-2.bsp",
                             DE441_PART_2_SHA256, 1_656_830_976),
}
DEFAULT_KERNELS = ("DE440",)


def cache_dir(override: str | os.PathLike[str] | None = None) -> Path:
    """The per-user data directory: ``$EPHEMERIS_OSS_CACHE``, else the platform's user cache."""

    if override is not None:
        return Path(override)
    configured = os.getenv("EPHEMERIS_OSS_CACHE")
    if configured:
        return Path(configured)
    if os.name == "nt":
        base = Path(os.getenv("LOCALAPPDATA") or Path.home() / "AppData" / "Local")
    else:
        base = Path(os.getenv("XDG_CACHE_HOME") or Path.home() / ".cache")
    return base / "ephemeris-oss"


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def cached_path(spec: KernelSpec, directory: Path) -> Path:
    return directory / spec.filename


def fetch(
    identifiers: tuple[str, ...] = DEFAULT_KERNELS,
    *,
    directory: Path | None = None,
    opener: Callable[[str], object] = urllib.request.urlopen,
    log: Callable[[str], None] = print,
) -> dict[str, Path]:
    """Download each kernel once into the cache and verify it; a mismatch deletes the partial file."""

    target = cache_dir(directory)
    target.mkdir(parents=True, exist_ok=True)
    fetched: dict[str, Path] = {}
    for identifier in identifiers:
        spec = KERNELS[identifier]
        path = cached_path(spec, target)
        if path.exists() and sha256_file(path) == spec.sha256:
            log(f"{identifier}: cached and verified {path}")
            fetched[identifier] = path
            continue
        partial = path.with_suffix(path.suffix + ".part")
        log(f"{identifier}: downloading {spec.url}")
        with opener(spec.url) as response, partial.open("wb") as out:  # type: ignore[attr-defined]
            for block in iter(lambda: response.read(1 << 20), b""):
                out.write(block)
        actual = sha256_file(partial)
        if actual != spec.sha256:
            partial.unlink()
            raise ValueError(f"{identifier}: SHA-256 mismatch, expected {spec.sha256}, got {actual}")
        partial.replace(path)
        log(f"{identifier}: verified {spec.sha256}")
        fetched[identifier] = path
    return fetched


def verify(directory: Path | None = None) -> dict[str, str]:
    """Report each known kernel in the cache as ``verified``, ``mismatch`` or ``absent``."""

    target = cache_dir(directory)
    status: dict[str, str] = {}
    for identifier, spec in KERNELS.items():
        path = cached_path(spec, target)
        if not path.exists():
            status[identifier] = "absent"
        else:
            status[identifier] = "verified" if sha256_file(path) == spec.sha256 else "mismatch"
    return status


IERS_FINALS_URL = "https://datacenter.iers.org/data/latestVersion/finals.all.iau2000.txt"
EOP_FILENAME = "finals2000A.all"


def fetch_eop(
    *,
    directory: Path | None = None,
    opener: Callable[[str], object] = urllib.request.urlopen,
    log: Callable[[str], None] = print,
) -> tuple[Path, str]:
    """Download the IERS finals2000A file; it changes daily, so its SHA-256 is recorded, not pinned.

    Every result computed with it carries that hash in its receipt. A file that
    parses to no records is refused and the previous one is kept.
    """

    from .engine.earth_orientation import parse_finals2000a_line

    target = cache_dir(directory)
    target.mkdir(parents=True, exist_ok=True)
    path = target / EOP_FILENAME
    partial = path.with_suffix(".part")
    log(f"EOP: downloading {IERS_FINALS_URL}")
    with opener(IERS_FINALS_URL) as response, partial.open("wb") as out:  # type: ignore[attr-defined]
        for block in iter(lambda: response.read(1 << 20), b""):
            out.write(block)
    records = sum(1 for line in partial.read_text(encoding="ascii", errors="replace").splitlines()
                  if parse_finals2000a_line(line) is not None)
    if records < 2:
        partial.unlink()
        raise ValueError("EOP: downloaded file holds no finals2000A records; previous file kept")
    partial.replace(path)
    digest = sha256_file(path)
    log(f"EOP: {records} records, sha256 {digest}")
    return path, digest
