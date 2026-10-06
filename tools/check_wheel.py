#!/usr/bin/env python3
"""Fail if a built wheel carries Swiss data files, benchmark or comparator code, or a swisseph string.

``--self-test`` builds two small wheels in a temporary directory, one clean and
one with a planted ``.se1`` file, a ``bench/`` file, a ``comparators/`` file and
a ``swisseph`` string, and exits 0 only if the clean one passes and each
planted item is reported.
"""

from __future__ import annotations

import argparse
import re
import sys
import tempfile
import zipfile
from pathlib import Path

BANNED_NAMES = (re.compile(r"\.se1$", re.I), re.compile(r"(^|/)bench/"), re.compile(r"(^|/)comparators/"))
BANNED_TEXT = re.compile(rb"swisseph|sweph", re.I)


def scan(wheel: Path) -> list[str]:
    problems: list[str] = []
    with zipfile.ZipFile(wheel) as archive:
        for name in archive.namelist():
            for pattern in BANNED_NAMES:
                if pattern.search(name):
                    problems.append(f"{name}: banned path ({pattern.pattern})")
            if BANNED_TEXT.search(name.encode()) or BANNED_TEXT.search(archive.read(name)):
                problems.append(f"{name}: contains a swisseph/sweph string")
    return problems


def self_test() -> int:
    with tempfile.TemporaryDirectory() as tmp:
        clean = Path(tmp) / "clean.whl"
        dirty = Path(tmp) / "dirty.whl"
        with zipfile.ZipFile(clean, "w") as archive:
            archive.writestr("pkg/__init__.py", "PLANET = 'planet'\n")
        with zipfile.ZipFile(dirty, "w") as archive:
            archive.writestr("pkg/__init__.py", "x = 1\n")
            archive.writestr("pkg/ephe/sepl_18.se1", "x")
            archive.writestr("bench/run.py", "x = 1\n")
            archive.writestr("pkg/comparators/c.py", "x = 1\n")
            archive.writestr("pkg/leak.py", "import swisseph\n")
        clean_problems, dirty_problems = scan(clean), scan(dirty)
    expected = ("sepl_18.se1", "bench/run.py", "comparators/c.py", "leak.py")
    missed = [item for item in expected if not any(item in problem for problem in dirty_problems)]
    for problem in clean_problems:
        print(f"SELF-TEST FALSE POSITIVE {problem}")
    for item in missed:
        print(f"SELF-TEST MISSED {item}")
    ok = not clean_problems and not missed
    print(f"check_wheel self-test: {'PASS' if ok else 'FAIL'}")
    return 0 if ok else 1


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("wheels", nargs="*", type=Path)
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args(argv)
    if args.self_test:
        return self_test()
    if not args.wheels:
        parser.error("give a wheel, or --self-test")
    problems = [f"{wheel.name}: {problem}" for wheel in args.wheels for problem in scan(wheel)]
    for problem in problems:
        print(problem)
    print(f"check_wheel: {len(problems)} problem(s) in {len(args.wheels)} wheel(s)")
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
